from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase, tagged
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
