from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRetanaSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        group_user = cls.env.ref('retana_bills.group_retana_user')
        group_admin = cls.env.ref('retana_bills.group_retana_admin')
        Users = cls.env['res.users'].with_context(no_reset_password=True)
        cls.no_group = Users.create({'name': 'Sin grupo', 'login': 'sin_grupo', 'group_ids': [(6, 0, [cls.env.ref('base.group_user').id])]})
        cls.user = Users.create({'name': 'Usuario Retana', 'login': 'usuario_retana', 'group_ids': [(6, 0, [group_user.id])]})
        cls.admin = Users.create({'name': 'Admin Retana', 'login': 'admin_retana', 'group_ids': [(6, 0, [group_admin.id])]})
        cls.partner = cls.env['res.partner'].create({'name': 'Cliente', 'is_retana_customer': True})

    def test_user_without_group_cannot_read(self):
        with self.assertRaises(AccessError):
            self.env['retana.budget'].with_user(self.no_group).search([])

    def test_user_creates_and_edits_but_does_not_delete(self):
        budget = self.env['retana.budget'].with_user(self.user).create({'client_id': self.partner.id})
        budget.write({'title': 'Editado'})
        with self.assertRaises(AccessError):
            budget.unlink()

    def test_user_cannot_change_catalogs(self):
        budget_type = self.env['retana.budget.type'].create({'name': 'Tipo'})
        self.assertTrue(budget_type.with_user(self.user).name)
        with self.assertRaises(AccessError):
            budget_type.with_user(self.user).write({'name': 'Otro'})

    def test_user_cannot_delete_downpayments(self):
        downpayment = self.env['retana.downpayment'].with_user(self.user).create({'client_id': self.partner.id, 'amount': 10.0})
        with self.assertRaises(AccessError):
            downpayment.unlink()

    def test_admin_deletes_and_changes_catalogs(self):
        budget = self.env['retana.budget'].with_user(self.admin).create({'client_id': self.partner.id})
        budget.unlink()
        budget_type = self.env['retana.budget.type'].with_user(self.admin).create({'name': 'Tipo admin'})
        budget_type.write({'name': 'Otro'})

    def test_admin_group_implies_user_group(self):
        self.assertTrue(self.admin.has_group('retana_bills.group_retana_user'))
        self.assertFalse(self.user.has_group('retana_bills.group_retana_admin'))
