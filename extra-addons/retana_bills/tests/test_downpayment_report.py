from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDownpaymentReport(TransactionCase):

    def test_report_tables_have_no_borders(self):
        partner_type = self.env['retana.type.res.partner'].create({'name': 'Arquitecto', 'code': 'ARQ'})
        partner = self.env['res.partner'].create({
            'name': 'Cliente', 'is_retana_customer': True, 'retana_type_res_partner_id': partner_type.id,
        })
        downpayment = self.env['retana.downpayment'].create({'client_id': partner.id, 'amount': 4000.0})
        report = self.env.ref('retana_bills.action_report_retana_downpayment')
        html = report._render_qweb_html(report.report_name, downpayment.ids)[0].decode()
        self.assertIn('retana_downpayment_page', html)
        self.assertRegex(html, r'\.retana_downpayment_page table[^{]*\{[^}]*border: none !important')
