from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestValidations(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env['res.partner']
        cls.client_a = Partner.create({'name': 'Cliente A', 'is_retana_customer': True})
        cls.client_b = Partner.create({'name': 'Cliente B', 'is_retana_customer': True})
        cls.building_a = cls.env['retana.buildings'].create({'name': 'Obra A', 'client_id': cls.client_a.id})
        cls.budget = cls.env['retana.budget'].create({
            'client_id': cls.client_a.id,
            'building_id': cls.building_a.id,
            'line_ids': [(0, 0, {'description': 'Linea', 'quantity': 1.0, 'unit_price': 100.0})],
        })

    def test_line_requires_budget(self):
        with self.assertRaises(ValidationError):
            self.env['retana.budget.line'].with_context(install_mode=False).create({'description': 'Huerfana', 'quantity': 1.0, 'unit_price': 1.0})

    def test_line_values_not_negative(self):
        with self.assertRaises(ValidationError):
            self.budget.line_ids.write({'quantity': -1.0})
        with self.assertRaises(ValidationError):
            self.budget.line_ids.write({'unit_price': -5.0})

    def test_discount_range(self):
        with self.assertRaises(ValidationError):
            self.budget.write({'discount': 1.5})
        with self.assertRaises(ValidationError):
            self.budget.write({'discount': -0.1})
        self.budget.write({'discount': 1.0})

    def test_downpayment_cannot_exceed_total(self):
        with self.assertRaises(ValidationError):
            self.budget.write({'downpayment_amount': 100.01})
        with self.assertRaises(ValidationError):
            self.budget.write({'downpayment_amount': -1.0})
        self.budget.write({'downpayment_amount': 100.0})
        self.assertEqual(self.budget.total_amount, 0.0)

    def test_editing_line_cannot_make_total_negative(self):
        self.budget.write({'downpayment_amount': 80.0})
        with self.assertRaises(ValidationError):
            self.budget.line_ids.write({'unit_price': 50.0})

    def test_building_must_belong_to_client(self):
        with self.assertRaises(ValidationError):
            self.budget.write({'client_id': self.client_b.id})
        with self.assertRaises(ValidationError):
            self.env['retana.downpayment'].create({
                'building_id': self.building_a.id, 'client_id': self.client_b.id, 'amount': 10.0,
            })

    def test_building_without_client_is_accepted(self):
        building = self.env['retana.buildings'].create({'name': 'Sin cliente'})
        self.env['retana.downpayment'].create({'building_id': building.id, 'client_id': self.client_b.id, 'amount': 10.0})

    def test_budget_without_lines_cannot_be_sent_or_approved(self):
        empty = self.env['retana.budget'].create({'client_id': self.client_a.id})
        with self.assertRaises(UserError):
            empty.action_send()
        with self.assertRaises(UserError):
            empty.action_approve()

    def test_copy_with_downpayment(self):
        self.budget.write({'downpayment_amount': 40.0})
        copy = self.budget.copy()
        self.assertEqual(len(copy.line_ids), 1)
        self.assertEqual(copy.total_amount, 60.0)
        self.assertEqual(copy.state, 'draft')
