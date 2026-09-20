from odoo import models, fields, api


class RetanaBulkDownpaymentWizard(models.TransientModel):
    _name = 'retana.bulk.downpayment.wizard'
    _inherit = ['retana.bulk.downpayment.mixin']
    _description = 'Wizard para crear múltiples anticipos desde mensaje de texto'

    message_text = fields.Text(
        string='Mensaje',
        required=True,
        help='Pega el mensaje con los anticipos. Formato: $monto nombre_obra o $monto nombre_obra, concepto'
    )
    found_lines_text = fields.Text(
        string='Lineas Con Obra Encontrada',
        readonly=True,
        help='Muestra las lineas del mensaje cuya obra fue encontrada en el sistema.'
    )
    not_found_lines_text = fields.Text(
        string='Lineas Sin Obra Encontrada',
        readonly=True,
        help='Muestra las lineas del mensaje cuya obra no fue encontrada en el sistema.'
    )
    date = fields.Date(
        string='Fecha del Anticipo',
        required=True,
        default=lambda self: self.get_default_downpayment_date()
    )
    client_id = fields.Many2one(
        'res.partner',
        string='Cliente por Defecto',
        domain="[('is_retana_customer', '=', True)]",
        help='Cliente a usar cuando la obra no tenga cliente asignado'
    )

    @api.onchange('message_text')
    def _onchange_message_text_split_buildings(self):
        """Separa lineas por obra encontrada y marca con * las que requieren correccion."""
        for wizard in self:
            if not wizard.message_text:
                wizard.found_lines_text = False
                wizard.not_found_lines_text = False
                continue

            analysis = wizard.analyze_bulk_message(wizard.message_text)

            if wizard.message_text != analysis['updated_message']:
                wizard.message_text = analysis['updated_message']

            wizard.found_lines_text = analysis['found_lines_text']
            wizard.not_found_lines_text = analysis['not_found_lines_text']

            if analysis['suggested_client_id']:
                wizard.client_id = analysis['suggested_client_id']
            elif (
                analysis['client_conflict']
                and wizard.client_id
                and wizard.client_id.id not in analysis['found_client_ids']
            ):
                return {
                    'warning': {
                        'title': 'Clientes Distintos Detectados',
                        'message': (
                            'Las obras encontradas pertenecen a diferentes clientes. '
                            'Selecciona manualmente el cliente por defecto que deseas usar '
                            'para las obras sin cliente.'
                        ),
                    }
                }

    def action_create_downpayments(self):
        """Procesa el mensaje y crea múltiples anticipos."""
        self.ensure_one()

        created_downpayments, errors = self.create_bulk_downpayments(
            self.message_text,
            self.date,
            self.client_id.id if self.client_id else None,
        )

        message = f'✅ Se crearon {len(created_downpayments)} anticipo(s) correctamente.'
        notification_type = 'success'

        if errors:
            message += '\n\n⚠️ Advertencias:\n' + '\n'.join(errors)
            notification_type = 'warning'

        self.env['bus.bus']._sendone(
            self.env.user.partner_id,
            'simple_notification',
            {
                'title': '✅ Anticipos Creados' if not errors else '⚠️ Anticipos Creados con Advertencias',
                'message': message,
                'type': notification_type,
                'sticky': True,
            }
        )

        return {
            'type': 'ir.actions.act_window',
            'name': 'Anticipos Creados',
            'res_model': 'retana.downpayment',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('retana_bills.view_retana_downpayment_tree').id, 'tree'),
                      (self.env.ref('retana_bills.view_retana_downpayment_form').id, 'form')],
            'domain': [('id', 'in', created_downpayments.ids)],
            'target': 'current',
        }
