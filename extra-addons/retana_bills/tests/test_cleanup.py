from datetime import date

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDownpaymentDate(TransactionCase):

    def _date(self):
        return self.env['retana.downpayment.date.mixin']._get_default_downpayment_date()

    def test_uses_configured_weekday(self):
        params = self.env['ir.config_parameter'].sudo()
        for weekday in range(7):
            params.set_param('retana_bills_weekday_config.downpayment_weekday', str(weekday))
            result = self._date()
            self.assertEqual(result.weekday(), weekday)
            self.assertGreaterEqual(result, date.today())
            self.assertLess((result - date.today()).days, 7)

    def test_defaults_to_thursday(self):
        params = self.env['ir.config_parameter'].sudo()
        for value in (False, 'no-es-numero', '9'):
            params.set_param('retana_bills_weekday_config.downpayment_weekday', value)
            self.assertEqual(self._date().weekday(), 3)

    def test_models_share_the_same_default(self):
        self.env['ir.config_parameter'].sudo().set_param('retana_bills_weekday_config.downpayment_weekday', '4')
        expected = self._date()
        self.assertEqual(self.env['retana.downpayment'].default_get(['date'])['date'], expected)
        self.assertEqual(self.env['retana.downpayment.wizard'].default_get(['date'])['date'], expected)
        self.assertEqual(self.env['retana.bulk.downpayment.wizard'].default_get(['date'])['date'], expected)


@tagged('post_install', '-at_install')
class TestSequences(TransactionCase):

    def test_single_sequence_per_code_with_xmlid(self):
        for code, xmlid in (('retana.budget', 'retana_bills.seq_retana_budget'), ('retana.downpayment', 'retana_bills.seq_retana_downpayment')):
            self.assertEqual(self.env['ir.sequence'].search_count([('code', '=', code)]), 1, code)
            self.assertEqual(self.env.ref(xmlid).code, code)

    def test_names_come_from_sequences(self):
        partner = self.env['res.partner'].create({'name': 'Cliente', 'is_retana_customer': True})
        budget = self.env['retana.budget'].create({'client_id': partner.id})
        downpayment = self.env['retana.downpayment'].create({'client_id': partner.id, 'amount': 10.0})
        self.assertTrue(budget.name.startswith('RB'))
        self.assertTrue(downpayment.name.startswith('RD'))


@tagged('post_install', '-at_install')
class TestBulkMessageParsing(TransactionCase):

    def setUp(self):
        super().setUp()
        self.mixin = self.env['retana.bulk.downpayment.mixin']

    def test_amount_and_building(self):
        self.assertEqual(self.mixin._parse_line('$4000 Monte Olimpo'),
                         {'amount': 4000.0, 'building_name': 'Monte Olimpo', 'concept_name': None})

    def test_amount_with_decimals_and_concept(self):
        self.assertEqual(self.mixin._parse_line('$1500.50 Torre 120, Material'),
                         {'amount': 1500.5, 'building_name': 'Torre 120', 'concept_name': 'Material'})

    def test_without_dollar_sign(self):
        self.assertEqual(self.mixin._parse_line('3000 Nory')['amount'], 3000.0)

    def test_lines_without_amount_are_ignored(self):
        self.assertIsNone(self.mixin._parse_line('Anticipos de la semana'))
        self.assertIsNone(self.mixin._parse_line('   '))

    def test_create_bulk_downpayments(self):
        client = self.env['res.partner'].create({'name': 'Cliente masivo', 'is_retana_customer': True})
        self.env['retana.buildings'].create({'name': 'Obra Masiva Uno', 'client_id': client.id})
        if not self.env['retana.downpayment.type.concept'].search([('default_concept', '=', True)]):
            self.env['retana.downpayment.type.concept'].create({'name': 'Anticipo', 'default_concept': True})
        created, errors = self.mixin.create_bulk_downpayments('$2500 Obra Masiva Uno\n$100 Obra Que No Existe', date.today())
        self.assertEqual(len(created), 1)
        self.assertEqual(created.amount, 2500.0)
        self.assertEqual(created.client_id, client)
        self.assertEqual(len(errors), 1)
