from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged
from odoo.tests.common import new_test_user


@tagged('post_install', '-at_install')
class TestHomeSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.internal_user = new_test_user(cls.env, login='home_internal', groups='base.group_user')
        cls.home_admin = new_test_user(cls.env, login='home_admin', groups='home.group_home_home_admin')
        cls.menu = cls.env.ref('base.menu_administration')
        cls.shortcut = cls.env['home.home'].create({'name': 'Ajustes', 'menu_id': cls.menu.id})

    def test_any_internal_user_sees_home_menu(self):
        Menu = self.env['ir.ui.menu']
        visible = Menu.with_user(self.internal_user)._visible_menu_ids()
        self.assertIn(self.env.ref('home.menu_home_home_root').id, visible)
        self.assertNotIn(self.env.ref('home.menu_home_home_settings').id, visible)
        admin_visible = Menu.with_user(self.home_admin)._visible_menu_ids()
        self.assertIn(self.env.ref('home.menu_home_home_settings').id, admin_visible)

    def test_internal_user_is_read_only(self):
        shortcut = self.shortcut.with_user(self.internal_user)
        self.assertEqual(shortcut.name, 'Ajustes')
        with self.assertRaises(AccessError):
            shortcut.write({'name': 'Otro'})
        with self.assertRaises(AccessError):
            self.env['home.home'].with_user(self.internal_user).create({'name': 'X'})

    def test_home_admin_can_configure(self):
        self.shortcut.with_user(self.home_admin).write({'name': 'Nuevo'})
        self.assertEqual(self.shortcut.name, 'Nuevo')

    def test_home_app_has_an_image_icon(self):
        menu = self.env.ref('home.menu_home_home_root')
        self.assertTrue(menu.web_icon_data, "La app Home debe tener un icono de imagen")
