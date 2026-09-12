from odoo import api, fields, models
from odoo.exceptions import UserError

REPORT_CONFIG = {
    'retana.downpayment': {
        'single_report': 'retana_bills.action_report_retana_downpayment',
        'multi_report': 'retana_bills.action_report_retana_downpayment_list',
        'filename_prefix': 'Anticipo',
        'partner_field': 'client_id',
        'label_singular': 'anticipo',
        'label_plural': 'anticipos',
    },
    'retana.budget': {
        'single_report': 'retana_bills.action_report_retana_budget',
        'multi_report': 'retana_bills.action_report_retana_budget',
        'filename_prefix': 'Presupuesto',
        'partner_field': 'client_id',
        'label_singular': 'presupuesto',
        'label_plural': 'presupuestos',
    },
}


class RetanaWhatsappSendWizard(models.TransientModel):
    _name = 'retana.whatsapp.send.wizard'
    _description = 'Enviar Reporte por WhatsApp'

    res_model = fields.Char(readonly=True)
    res_ids = fields.Char(readonly=True)
    record_count = fields.Integer(string='Registros', readonly=True)
    summary = fields.Char(string='Reporte a enviar', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    whatsapp_id = fields.Many2one('retana.whatsapp', string='Número guardado')
    number = fields.Char(
        string='Número de WhatsApp',
        required=True,
        help="Incluye código de país sin '+'. Ejemplo: 521XXXXXXXXXX",
    )
    save_number = fields.Boolean(string='Guardar número para este cliente', default=True)
    message = fields.Text(string='Mensaje', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids') or []
        config = REPORT_CONFIG.get(active_model)
        if not config or not active_ids:
            raise UserError('Selecciona al menos un registro para enviar por WhatsApp.')

        records = self.env[active_model].browse(active_ids).exists()
        if not records:
            raise UserError('Selecciona al menos un registro para enviar por WhatsApp.')

        partners = records.mapped(config['partner_field'])
        count = len(records)
        label = config['label_singular'] if count == 1 else config['label_plural']
        article = 'el' if count == 1 else 'los'
        plural_suffix = '' if count == 1 else 's'

        res.update({
            'res_model': active_model,
            'res_ids': ','.join(str(i) for i in records.ids),
            'record_count': count,
            'summary': f"{count} {label} seleccionado{plural_suffix}",
            'message': f"Hola, te comparto {article} {label} solicitado{plural_suffix}.",
        })
        if len(partners) == 1:
            res['partner_id'] = partners.id
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.whatsapp_id = False
        self.number = False
        if self.partner_id:
            whatsapp = self.env['retana.whatsapp'].search([('partner_id', '=', self.partner_id.id)], limit=1)
            if whatsapp:
                self.whatsapp_id = whatsapp
                self.number = whatsapp.number
            else:
                self.number = self.partner_id.mobile or self.partner_id.phone or False
        return {'domain': {'whatsapp_id': [('partner_id', '=', self.partner_id.id)]}}

    @api.onchange('whatsapp_id')
    def _onchange_whatsapp_id(self):
        if self.whatsapp_id:
            self.number = self.whatsapp_id.number

    def action_send(self):
        self.ensure_one()
        if not self.res_model or not self.res_ids:
            raise UserError('No hay registros para enviar.')
        config = REPORT_CONFIG[self.res_model]
        ids = [int(i) for i in self.res_ids.split(',') if i]
        records = self.env[self.res_model].browse(ids)

        report_xmlid = config['single_report'] if len(ids) == 1 else config['multi_report']
        pdf_content, _report_type = self.env['ir.actions.report']._render_qweb_pdf(report_xmlid, res_ids=ids)

        first_name = (records[:1].name or 'reporte').replace('/', '-')
        if len(ids) == 1:
            filename = f"{config['filename_prefix']}_{first_name}.pdf"
        else:
            filename = f"{config['filename_prefix']}s.pdf"

        if self.save_number and self.partner_id and self.number:
            existing = self.env['retana.whatsapp'].search([
                ('partner_id', '=', self.partner_id.id),
                ('number', '=', self.number),
            ], limit=1)
            if not existing:
                self.env['retana.whatsapp'].create({
                    'partner_id': self.partner_id.id,
                    'number': self.number,
                })

        self.env['retana.whatsapp'].send_pdf_document(self.number, pdf_content, filename, self.message)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'WhatsApp enviado',
                'message': f'Se envió {filename} al número {self.number}.',
                'sticky': False,
                'type': 'success',
            },
        }
