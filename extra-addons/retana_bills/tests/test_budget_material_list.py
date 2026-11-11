from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBudgetMaterialList(TransactionCase):

    def test_is_material_list_follows_budget_type(self):
        budget_type = self.env['retana.budget.type'].create({'name': 'Materiales', 'is_material_list': True})
        budget = self.env['retana.budget'].new({'budget_type_id': budget_type.id})
        self.assertTrue(budget.is_material_list)
        budget_type.is_material_list = False
        self.assertFalse(budget.is_material_list)

    def test_price_columns_hidden_in_form_for_material_list(self):
        arch = self.env['retana.budget'].get_view(
            self.env.ref('retana_bills.view_retana_budget_form').id, 'form')['arch']
        for field in ('display_type', 'unit_price', 'taxes_ids', 'subtotal'):
            self.assertRegex(arch, r'<field name="%s"[^>]*parent\.is_material_list' % field)
