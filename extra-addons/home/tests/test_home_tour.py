from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestHomeDashboardTour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings = cls.env.ref('base.menu_administration')
        apps = cls.env.ref('base.menu_management')
        cls.env['home.home'].create([
            {'name': 'Ajustes Test', 'menu_id': settings.id, 'sequence': 1},
            {'name': 'Aplicaciones Test', 'menu_id': apps.id, 'sequence': 2},
        ])

    def test_dashboard_tour(self):
        self.start_tour('/web#action=home.action_home_home_dashboard', 'home_dashboard_tour', login='admin')
