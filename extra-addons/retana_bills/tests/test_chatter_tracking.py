from markupsafe import Markup

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestChatterTracking(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Cliente', 'is_retana_customer': True})
        cls.budget = cls.env['retana.budget'].create({'client_id': cls.partner.id})

    def _last_messages(self):
        return self.budget.message_ids.filtered(lambda m: 'Cambios en' in (m.body or ''))

    def test_line_change_message_is_html_not_escaped(self):
        self.budget.write({'line_ids': [(0, 0, {'description': 'Linea', 'quantity': 1.0, 'unit_price': 200.0})]})
        messages = self._last_messages()
        self.assertEqual(len(messages), 1)
        body = messages.body
        self.assertIsInstance(body, Markup)
        self.assertNotIn('&lt;', body)
        self.assertIn('<strong>', body)

    def test_labels_instead_of_technical_names(self):
        self.budget.write({'line_ids': [(0, 0, {'description': 'Linea', 'quantity': 1.0, 'unit_price': 200.0})]})
        line = self.budget.line_ids
        self.budget.write({'line_ids': [(1, line.id, {'unit_price': 300.0})]})
        text = ' '.join(self._last_messages().mapped(lambda m: m.body))
        self.assertIn('Precio Unitario', text)
        self.assertNotIn('unit_price', text)

    def test_no_raw_record_reference_in_tracking_values(self):
        self.budget.write({'line_ids': [(0, 0, {'description': 'Linea', 'quantity': 1.0, 'unit_price': 200.0})]})
        values = self.budget.message_ids.tracking_value_ids
        self.assertFalse(values.filtered(lambda v: v.field_id.name == 'line_ids'))
