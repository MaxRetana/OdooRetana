from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDownpaymentTypeConceptSearch(TransactionCase):

    def test_search_view_has_name_field(self):
        view = self.env.ref('retana_bills.view_retana_downpayment_type_concept_search')
        arch = self.env['retana.downpayment.type.concept'].get_view(view.id, 'search')['arch']
        self.assertIn('<field name="name"', arch)
