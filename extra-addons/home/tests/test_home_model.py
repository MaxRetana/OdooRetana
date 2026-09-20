from psycopg2 import IntegrityError

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import Form, TransactionCase, tagged
from odoo.tests.common import new_test_user
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestHomeModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.menu = cls.env.ref('base.menu_administration')

    def test_menu_must_be_unique(self):
        self.env['home.home'].create({'name': 'A', 'menu_id': self.menu.id})
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['home.home'].create({'name': 'B', 'menu_id': self.menu.id})

    def test_fa_icon_is_validated(self):
        with self.assertRaises(ValidationError):
            self.env['home.home'].create({'name': 'A', 'fa_icon': 'rocket<script>'})
        record = self.env['home.home'].create({'name': 'B', 'fa_icon': 'fa-rocket'})
        self.assertEqual(record.fa_icon, 'fa-rocket')

    def test_color_is_validated(self):
        with self.assertRaises(ValidationError):
            self.env['home.home'].create({'name': 'A', 'color': 'red; background: url(x)'})
        record = self.env['home.home'].create({'name': 'B', 'color': '#714B67'})
        self.assertEqual(record.color, '#714B67')

    def test_archived_shortcuts_are_hidden(self):
        record = self.env['home.home'].create({'name': 'A', 'menu_id': self.menu.id})
        record.active = False
        self.assertFalse(self.env['home.home'].search([('id', '=', record.id)]))

    def test_icon_values_from_menu(self):
        Home = self.env['home.home']
        fa_menu = self.env['ir.ui.menu'].create({'name': 'FA', 'web_icon': 'fa-rocket,#FFFFFF,#000000'})
        self.assertEqual(
            Home._get_icon_values_from_menu(fa_menu),
            {'icon_type': 'fontawesome', 'fa_icon': 'fa-rocket'},
        )
        self.assertTrue(self.menu.web_icon_data, "El menú de Ajustes debería tener imagen")
        values = Home._get_icon_values_from_menu(self.menu)
        self.assertEqual(values['icon_type'], 'custom')
        self.assertTrue(values['custom_icon'])
        plain_menu = self.env['ir.ui.menu'].create({'name': 'Plain'})
        self.assertEqual(Home._get_icon_values_from_menu(plain_menu), {})

    def test_onchange_keeps_customized_name(self):
        other = self.env.ref('base.menu_management')
        # Alta nueva: el nombre se sugiere desde el menú
        with Form(self.env['home.home']) as form:
            form.menu_id = self.menu
            self.assertEqual(form.name, self.menu.name)
            record = form.save()
        # Nombre igual al del menú anterior: se actualiza con el nuevo menú
        with Form(record) as form:
            form.menu_id = other
            self.assertEqual(form.name, other.name)
        # Nombre personalizado: no se pisa al cambiar de menú
        with Form(record) as form:
            form.name = 'Personalizado'
        with Form(record) as form:
            form.menu_id = self.menu
            self.assertEqual(form.name, 'Personalizado')

    def test_sync_apps_creates_missing_shortcuts_once(self):
        Home = self.env['home.home']
        Home.search([]).unlink()
        root_menus = self.env['ir.ui.menu'].with_context(**{'ir.ui.menu.full_list': True}).search(
            [('parent_id', '=', False)])
        home_root = self.env.ref('home.menu_home_home_root')
        expected = root_menus - home_root

        result = Home.action_sync_apps()
        self.assertEqual(result['tag'], 'display_notification')
        created = Home.search([])
        self.assertEqual(created.menu_id, expected, "Un acceso por app, sin incluir el propio Home")
        self.assertNotIn(home_root, created.menu_id)
        settings = created.filtered(lambda h: h.menu_id == self.menu)
        self.assertEqual(settings.name, self.menu.name)
        self.assertEqual(settings.icon_type, 'custom')
        self.assertTrue(settings.custom_icon)

        # Idempotente, y no resucita los accesos archivados a propósito
        settings.active = False
        Home.action_sync_apps()
        self.assertEqual(Home.with_context(active_test=False).search_count([]), len(expected))
        self.assertFalse(Home.search([('id', '=', settings.id)]))

    def test_sync_apps_requires_create_rights(self):
        user = new_test_user(self.env, login='home_sync_user', groups='base.group_user')
        with self.assertRaises(AccessError):
            self.env['home.home'].with_user(user).action_sync_apps()
