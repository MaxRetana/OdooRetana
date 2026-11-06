from odoo.tests import HttpCase, tagged
from odoo.tests.common import new_test_user


@tagged('post_install', '-at_install')
class TestHomeDashboardTour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        group = cls.env['res.groups'].create({'name': 'Grupo Tour Home'})
        action = cls.env.ref('base.action_partner_form')
        Menu = cls.env['ir.ui.menu']
        values = {'action': f'ir.actions.act_window,{action.id}'}
        menu_a = Menu.create({'name': 'Menu A', **values})
        menu_b = Menu.create({'name': 'Menu B', **values})
        menu_c = Menu.create({'name': 'Menu C', 'group_ids': [(6, 0, group.ids)], **values})
        menu_d = Menu.create({'name': 'Menu D', **values})
        cls.env['home.home'].create([
            {'name': 'Configuración Test', 'menu_id': menu_a.id, 'sequence': 1, 'color': '#FF0000'},
            {'name': 'Aplicaciones Test', 'menu_id': menu_b.id, 'sequence': 2},
            {'name': 'Menu Restringido Test', 'menu_id': menu_c.id, 'sequence': 3},
            {'name': 'Grupo Restringido Test', 'menu_id': menu_d.id, 'sequence': 4,
             'groups_ids': [(6, 0, group.ids)]},
        ])
        cls.member = new_test_user(cls.env, login='home_tour_member', groups='base.group_user')
        cls.member.group_ids = [(4, group.id)]

    def test_dashboard_tour(self):
        self.start_tour('/web#action=home.action_home_home_dashboard', 'home_dashboard_tour', login='admin')

    def test_card_link_opens_the_app_directly(self):
        menu = self.env['ir.ui.menu'].search([('name', '=', 'Menu A')])
        action = self.env.ref('base.action_partner_form')
        self.start_tour(f'/web#menu_id={menu.id}&action={action.id}', 'home_dashboard_link_tour', login='admin')

    def test_navbar_apps_menu_follows_home_config(self):
        self.start_tour('/web#action=home.action_home_home_dashboard', 'home_navbar_apps_tour', login='admin')

    def test_config_views_tour(self):
        self.start_tour('/web#action=home.action_home_home_config', 'home_config_views_tour', login='admin')

    def test_dashboard_tour_member(self):
        self.start_tour('/web#action=home.action_home_home_dashboard', 'home_dashboard_member_tour',
                        login='home_tour_member')


@tagged('post_install', '-at_install')
class TestHomeDashboardEmptyTour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['home.home'].search([]).write({'active': False})

    def test_empty_dashboard_tour(self):
        self.start_tour('/web#action=home.action_home_home_dashboard', 'home_dashboard_empty_tour', login='admin')

    def test_navbar_falls_back_to_native_menu_without_shortcuts(self):
        self.start_tour('/web#action=home.action_home_home_dashboard', 'home_navbar_fallback_tour', login='admin')

    def test_sync_from_empty_dashboard_tour(self):
        self.start_tour('/web#action=home.action_home_home_dashboard', 'home_dashboard_sync_tour', login='admin')


@tagged('post_install', '-at_install')
class TestHomeLanding(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        action = cls.env.ref('base.action_partner_form')
        # Una app que por orden sería la primera: sin el Home como inicio, Odoo abriría esta
        cls.env['ir.ui.menu'].create({
            'name': 'Primera App', 'sequence': 0, 'action': f'ir.actions.act_window,{action.id}',
        })
        cls.env['home.home'].search([]).write({'active': False})
        cls.user = new_test_user(cls.env, login='home_landing_user', groups='base.group_user')

    def test_home_is_the_landing_page(self):
        self.start_tour('/web', 'home_landing_tour', login='home_landing_user')

    def test_landing_can_be_disabled(self):
        self.env['ir.config_parameter'].set_param('home.use_as_landing', 'False')
        self.start_tour('/web', 'home_no_landing_tour', login='home_landing_user')

    def test_personal_home_action_is_respected(self):
        self.user.action_id = self.env.ref('base.action_partner_form').id
        self.start_tour('/web', 'home_no_landing_tour', login='home_landing_user')
