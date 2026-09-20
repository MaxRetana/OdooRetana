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
        menu_c = Menu.create({'name': 'Menu C', 'groups_id': [(6, 0, group.ids)], **values})
        menu_d = Menu.create({'name': 'Menu D', **values})
        cls.env['home.home'].create([
            {'name': 'Configuración Test', 'menu_id': menu_a.id, 'sequence': 1, 'color': '#FF0000'},
            {'name': 'Aplicaciones Test', 'menu_id': menu_b.id, 'sequence': 2},
            {'name': 'Menu Restringido Test', 'menu_id': menu_c.id, 'sequence': 3},
            {'name': 'Grupo Restringido Test', 'menu_id': menu_d.id, 'sequence': 4,
             'groups_ids': [(6, 0, group.ids)]},
        ])
        cls.member = new_test_user(cls.env, login='home_tour_member', groups='base.group_user')
        cls.member.groups_id = [(4, group.id)]

    def test_dashboard_tour(self):
        self.start_tour('/web#action=home.action_home_home_dashboard', 'home_dashboard_tour', login='admin')

    def test_card_link_opens_the_app_directly(self):
        menu = self.env['ir.ui.menu'].search([('name', '=', 'Menu A')])
        self.start_tour(f'/web#menu_id={menu.id}', 'home_dashboard_link_tour', login='admin')

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
