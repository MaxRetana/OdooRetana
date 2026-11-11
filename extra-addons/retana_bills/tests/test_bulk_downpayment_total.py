from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBulkDownpaymentTotal(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        client = cls.env['res.partner'].create({'name': 'Cliente', 'is_retana_customer': True})
        cls.env['retana.buildings'].create({'name': 'Zanya', 'client_id': client.id})
        cls.env['retana.buildings'].create({'name': 'Kahlal', 'client_id': client.id})

    def test_total_only_counts_lines_with_building_found(self):
        wizard = self.env['retana.bulk.downpayment.wizard']
        analysis = wizard.analyze_bulk_message('$3000 zanya\n$5000 kahlal, materiales\n$999 inexistente')
        self.assertEqual(analysis['found_total'], 8000.0)

    def test_onchange_fills_total_text(self):
        wizard = self.env['retana.bulk.downpayment.wizard'].new({'message_text': '$3000 zanya\n$2500.50 kahlal'})
        wizard._onchange_message_text_split_buildings()
        self.assertEqual(wizard.total_text, '$5,500.50')
        wizard.message_text = False
        wizard._onchange_message_text_split_buildings()
        self.assertFalse(wizard.total_text)
