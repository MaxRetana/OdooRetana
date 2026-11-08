from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBudgetAmounts(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Cliente', 'is_retana_customer': True})
        cls.iva16 = cls.env['account.tax'].create({'name': 'IVA 16 prueba', 'amount': 16.0, 'amount_type': 'percent', 'type_tax_use': 'sale'})
        cls.iva8 = cls.env['account.tax'].create({'name': 'IVA 8 prueba', 'amount': 8.0, 'amount_type': 'percent', 'type_tax_use': 'sale'})
        cls.iva16_included = cls.env['account.tax'].create({
            'name': 'IVA 16 incluido prueba', 'amount': 16.0, 'amount_type': 'percent',
            'type_tax_use': 'sale', 'price_include_override': 'tax_included',
        })

    def _budget(self, lines, **vals):
        return self.env['retana.budget'].create({
            'client_id': self.partner.id,
            'line_ids': [(0, 0, line) for line in lines],
            **vals,
        })

    def test_line_uses_budget_currency(self):
        budget = self._budget([{'description': 'A', 'quantity': 1.0, 'unit_price': 10.0}])
        self.assertEqual(budget.line_ids.currency_id, budget.currency_id)

    def test_totals_without_taxes(self):
        budget = self._budget([
            {'description': 'A', 'quantity': 2.0, 'unit_price': 100.0},
            {'description': 'B', 'quantity': 1.0, 'unit_price': 50.5},
        ])
        self.assertEqual(budget.subtotal_amount, 250.5)
        self.assertEqual(budget.tax_amount, 0.0)
        self.assertEqual(budget.total_amount, 250.5)

    def test_mixed_taxes(self):
        budget = self._budget([
            {'description': 'A', 'quantity': 1.0, 'unit_price': 100.0, 'taxes_ids': [(6, 0, self.iva16.ids)]},
            {'description': 'B', 'quantity': 1.0, 'unit_price': 100.0, 'taxes_ids': [(6, 0, self.iva8.ids)]},
            {'description': 'C', 'quantity': 1.0, 'unit_price': 100.0},
        ])
        self.assertEqual(budget.subtotal_amount, 300.0)
        self.assertEqual(budget.tax_amount, 24.0)
        self.assertEqual(budget.total_amount, 324.0)

    def test_discount_and_downpayment(self):
        budget = self._budget(
            [{'description': 'A', 'quantity': 1.0, 'unit_price': 1000.0, 'taxes_ids': [(6, 0, self.iva16.ids)]}],
            discount=0.1, downpayment_amount=100.0,
        )
        # 1000 + 160 de IVA - 100 de descuento - 100 de anticipo
        self.assertEqual(budget.discount_amount, 100.0)
        self.assertEqual(budget.total_amount, 960.0)

    def test_rounding_to_currency(self):
        budget = self._budget([{'description': 'A', 'quantity': 3.0, 'unit_price': 0.335, 'taxes_ids': [(6, 0, self.iva16.ids)]}])
        self.assertEqual(budget.subtotal_amount, budget.currency_id.round(3 * 0.335))
        self.assertEqual(budget.tax_amount, budget.currency_id.round(budget.subtotal_amount * 0.16))

    def test_tax_included_in_price(self):
        budget = self._budget([{'description': 'A', 'quantity': 1.0, 'unit_price': 116.0, 'taxes_ids': [(6, 0, self.iva16_included.ids)]}])
        self.assertEqual(budget.subtotal_amount, 100.0)
        self.assertEqual(budget.tax_amount, 16.0)

    def test_sections_and_notes_do_not_add(self):
        budget = self._budget([
            {'description': 'Seccion', 'display_type': 'line_section'},
            {'description': 'A', 'quantity': 1.0, 'unit_price': 10.0},
            {'description': 'Nota', 'display_type': 'line_note'},
        ])
        self.assertEqual(budget.total_amount, 10.0)
