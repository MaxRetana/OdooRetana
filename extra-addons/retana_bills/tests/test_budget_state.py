from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBudgetState(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Cliente', 'is_retana_customer': True})
        cls.budget = cls.env['retana.budget'].create({
            'client_id': cls.partner.id,
            'line_ids': [(0, 0, {'description': 'Linea', 'quantity': 2.0, 'unit_price': 10.0})],
        })

    def test_new_budget_is_draft(self):
        self.assertEqual(self.budget.state, 'draft')

    def test_copy_resets_state(self):
        self.budget.action_approve()
        self.assertEqual(self.budget.copy().state, 'draft')

    def test_flow(self):
        self.budget.action_send()
        self.assertEqual(self.budget.state, 'sent')
        self.budget.action_reject()
        self.assertEqual(self.budget.state, 'rejected')
        self.budget.action_draft()
        self.assertEqual(self.budget.state, 'draft')
        self.budget.action_approve()
        self.assertEqual(self.budget.state, 'approved')

    def test_approved_budget_is_locked(self):
        self.budget.action_approve()
        with self.assertRaises(UserError):
            self.budget.write({'title': 'Otro'})
        with self.assertRaises(UserError):
            self.budget.line_ids.write({'quantity': 5.0})
        with self.assertRaises(UserError):
            self.budget.line_ids.unlink()
        with self.assertRaises(UserError):
            self.env['retana.budget.line'].create({'budget_id': self.budget.id, 'description': 'Nueva'})
        with self.assertRaises(UserError):
            self.budget.unlink()

    def test_unapproved_budget_is_editable(self):
        self.budget.write({'title': 'Editado', 'line_ids': [(0, 0, {'description': 'Otra', 'unit_price': 1.0})]})
        self.assertEqual(len(self.budget.line_ids), 2)

    def test_only_admin_reopens_approved(self):
        self.budget.action_approve()
        user = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Usuario', 'login': 'usuario_estado',
            'group_ids': [(6, 0, [self.env.ref('retana_bills.group_retana_user').id])],
        })
        with self.assertRaises(UserError):
            self.budget.with_user(user).action_draft()
        self.budget.action_draft()
        self.assertEqual(self.budget.state, 'draft')
        self.budget.write({'title': 'Editable otra vez'})
