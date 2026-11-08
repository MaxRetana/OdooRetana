from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestWhatsappWizard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = cls.env['res.partner'].create({'name': 'Cliente de prueba', 'is_retana_customer': True})
        cls.building = cls.env['retana.buildings'].create({'name': 'Obra de prueba', 'client_id': cls.client.id})
        cls.budget = cls.env['retana.budget'].create({'client_id': cls.client.id, 'building_id': cls.building.id})
        cls.downpayment = cls.env['retana.downpayment'].create({
            'building_id': cls.building.id, 'client_id': cls.client.id, 'amount': 100.0,
        })

    def _send(self, **vals):
        wizard = self.env['retana.send.whatsapp.wizard'].create({'phone': '+52 123 456 7890', **vals})
        return wizard.action_send_whatsapp()['params']

    def _assert_url_uses_real_report(self, url, action_xmlid):
        report = self.env.ref(action_xmlid)
        self.assertIn(f'/report/pdf/{report.report_name}/', url)
        self.assertTrue(self.env['ir.actions.report']._get_report_from_name(report.report_name))

    def test_budget_url(self):
        params = self._send(report_type='budget', budget_id=self.budget.id)
        self._assert_url_uses_real_report(params['download_url'], 'retana_bills.action_report_retana_budget')
        self.assertTrue(params['download_url'].endswith(f'/{self.budget.id}'))

    def test_downpayment_url(self):
        params = self._send(report_type='downpayment', downpayment_id=self.downpayment.id)
        self._assert_url_uses_real_report(params['download_url'], 'retana_bills.action_report_retana_downpayment')

    def test_downpayment_list_url(self):
        params = self._send(report_type='downpayment_list', building_id=self.building.id)
        self._assert_url_uses_real_report(params['download_url'], 'retana_bills.action_report_retana_downpayment_list')
        self.assertTrue(params['download_url'].endswith(f'/{self.downpayment.id}'))

    def test_downpayment_list_without_downpayments(self):
        other = self.env['retana.buildings'].create({'name': 'Obra vacia', 'client_id': self.client.id})
        with self.assertRaises(UserError):
            self._send(report_type='downpayment_list', building_id=other.id)
