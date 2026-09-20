from odoo.tests import TransactionCase, tagged
from odoo.tests.common import new_test_user


@tagged('post_install', '-at_install')
class TestHomeData(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = cls.env['res.groups'].create({'name': 'Grupo Home Test'})
        cls.user = new_test_user(cls.env, login='home_data_user', groups='base.group_user')
        cls.member = new_test_user(cls.env, login='home_data_member', groups='base.group_user')
        cls.member.groups_id = [(4, cls.group.id)]
        action = cls.env.ref('base.action_partner_form')
        cls.open_menu = cls.env['ir.ui.menu'].create({'name': 'Menu abierto', 'action': f'ir.actions.act_window,{action.id}'})
        cls.hidden_menu = cls.env['ir.ui.menu'].create({
            'name': 'Menu oculto', 'action': f'ir.actions.act_window,{action.id}',
            'groups_id': [(6, 0, cls.group.ids)],
        })
        Home = cls.env['home.home']
        cls.open_shortcut = Home.create({'name': 'Abierto', 'menu_id': cls.open_menu.id, 'sequence': 1})
        cls.hidden_shortcut = Home.create({'name': 'Menu restringido', 'menu_id': cls.hidden_menu.id, 'sequence': 2})

    def _names(self, user):
        data = self.env['home.home'].with_user(user).get_home_data()
        return [app['name'] for app in data['apps']]

    def test_menu_not_accessible_is_filtered_out(self):
        self.assertEqual(self._names(self.user), ['Abierto'])
        self.assertEqual(self._names(self.member), ['Abierto', 'Menu restringido'])

    def test_groups_restriction_is_applied(self):
        self.open_shortcut.groups_ids = [(6, 0, self.group.ids)]
        self.assertEqual(self._names(self.user), [])
        self.assertEqual(self._names(self.member), ['Abierto', 'Menu restringido'])

    def test_archived_and_menuless_shortcuts_are_skipped(self):
        self.open_shortcut.active = False
        self.env['home.home'].create({'name': 'Sin menu'})
        self.assertEqual(self._names(self.member), ['Menu restringido'])

    def test_custom_icon_is_a_versioned_url_not_base64(self):
        menu = self.env.ref('base.menu_administration')
        self.open_shortcut.write({
            'icon_type': 'custom', 'custom_icon': menu.web_icon_data,
        })
        app = self.env['home.home'].with_user(self.user).get_home_data()['apps'][0]
        self.assertNotIn('custom_icon', app)
        self.assertRegex(app['icon_url'], rf'^/web/image/home\.home/{self.open_shortcut.id}/custom_icon\?unique=\d+$')

    def test_color_is_returned(self):
        self.open_shortcut.color = '#FF0000'
        apps = self.env['home.home'].with_user(self.user).get_home_data()['apps']
        self.assertEqual(apps[0]['color'], '#FF0000')

    def test_can_configure_flag(self):
        self.assertFalse(self.env['home.home'].with_user(self.user).get_home_data()['can_configure'])
        admin = new_test_user(self.env, login='home_data_admin', groups='home.group_home_home_admin')
        self.assertTrue(self.env['home.home'].with_user(admin).get_home_data()['can_configure'])
