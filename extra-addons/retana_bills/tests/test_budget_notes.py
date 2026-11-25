from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBudgetNotes(TransactionCase):

    def test_notes_saved_and_rendered_in_report(self):
        partner = self.env['res.partner'].create({'name': 'Cliente', 'is_retana_customer': True})
        budget = self.env['retana.budget'].create({
            'client_id': partner.id,
            'notes': 'Vigencia de 15 días',
            'line_ids': [(0, 0, {'description': 'A', 'quantity': 1.0, 'unit_price': 10.0})],
        })
        self.assertEqual(budget.notes, 'Vigencia de 15 días')
        html = self.env['ir.actions.report']._render_qweb_html(
            'retana_bills.report_retana_budget_document', budget.ids)[0].decode()
        self.assertIn('NOTA:', html)
        self.assertIn('Vigencia de 15 días', html)
