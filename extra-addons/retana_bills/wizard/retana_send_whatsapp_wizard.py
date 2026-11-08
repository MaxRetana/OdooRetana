from odoo import models, fields, api
from odoo.exceptions import UserError
import urllib.parse

class RetanaSendWhatsappWizard(models.TransientModel):
    _name = 'retana.send.whatsapp.wizard'
    _description = 'Enviar Reporte por WhatsApp'
    
    phone = fields.Char(string='Número de WhatsApp', required=True)
    report_type = fields.Selection([
        ('budget', 'Presupuesto'),
        ('downpayment', 'Anticipo'),
        ('downpayment_list', 'Lista de Anticipos'),
    ], string='Tipo de Reporte', required=True, default='budget')
    message = fields.Text(string='Mensaje', default='Hola, te envío el reporte solicitado.')
    
    # Campos específicos para cada tipo de reporte
    budget_id = fields.Many2one('retana.budget', string='Presupuesto')
    downpayment_id = fields.Many2one('retana.downpayment', string='Anticipo')
    building_id = fields.Many2one('retana.buildings', string='Obra (para lista de anticipos)')
    
    @api.onchange('report_type')
    def _onchange_report_type(self):
        """Limpiar campos al cambiar tipo de reporte"""
        self.budget_id = False
        self.downpayment_id = False
        self.building_id = False
    
    def _get_report_url(self, action_xmlid, record_ids):
        """Arma la URL de descarga a partir del report_name real de la acción."""
        report = self.env.ref(action_xmlid)
        ids_str = ','.join(str(record_id) for record_id in record_ids)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/report/pdf/{report.report_name}/{ids_str}"

    def action_send_whatsapp(self):
        """Descarga el PDF y abre WhatsApp"""
        self.ensure_one()
        
        # Limpiar el número de teléfono
        phone = ''.join(filter(str.isdigit, self.phone))
        
        # Generar URL del reporte según el tipo
        report_url = ''
        report_name = ''
        
        if self.report_type == 'budget' and self.budget_id:
            # Reporte de presupuesto específico
            report_url = self._get_report_url('retana_bills.action_report_retana_budget', self.budget_id.ids)
            report_name = f"Presupuesto_{self.budget_id.name.replace('/', '-')}.pdf"
        elif self.report_type == 'downpayment' and self.downpayment_id:
            # Reporte de anticipo específico
            report_url = self._get_report_url('retana_bills.action_report_retana_downpayment', self.downpayment_id.ids)
            report_name = f"Anticipo_{self.downpayment_id.name.replace('/', '-')}.pdf"
        elif self.report_type == 'downpayment_list' and self.building_id:
            # Buscar anticipos de la obra para generar el reporte
            downpayments = self.env['retana.downpayment'].search([('building_id', '=', self.building_id.id)])
            if downpayments:
                # Generar reporte con los IDs de los anticipos de la obra
                report_url = self._get_report_url('retana_bills.action_report_retana_downpayment_list', downpayments.ids)
                report_name = f"RelacionPagos_{self.building_id.name.replace('/', '-')}.pdf"
        
        if not report_url:
            raise UserError('No hay un reporte que enviar: la obra seleccionada no tiene anticipos.')

        # Construir el mensaje
        full_message = self.message
        
        # Codificar el mensaje para URL
        encoded_message = urllib.parse.quote(full_message)
        
        # Construir URL de WhatsApp Web
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
        
        # Crear acción múltiple: primero descarga el PDF, luego abre WhatsApp
        return {
            'type': 'ir.actions.client',
            'tag': 'download_and_open_whatsapp',
            'params': {
                'download_url': report_url,
                'download_name': report_name,
                'whatsapp_url': whatsapp_url,
            }
        }
