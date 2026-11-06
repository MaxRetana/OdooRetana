from odoo import models, fields, api
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
    
    def action_send_whatsapp(self):
        """Descarga el PDF y abre WhatsApp"""
        self.ensure_one()
        
        # Limpiar el número de teléfono
        phone = ''.join(filter(str.isdigit, self.phone))
        
        # Generar URL del reporte según el tipo
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        report_url = ''
        report_name = ''
        
        if self.report_type == 'budget' and self.budget_id:
            # Reporte de presupuesto específico
            report_url = f"{base_url}/report/pdf/retana_bills.retana_budget_report/{self.budget_id.id}"
            report_name = f"Presupuesto_{self.budget_id.name.replace('/', '-')}.pdf"
        elif self.report_type == 'downpayment' and self.downpayment_id:
            # Reporte de anticipo específico
            report_url = f"{base_url}/report/pdf/retana_bills.retana_downpayment_report/{self.downpayment_id.id}"
            report_name = f"Anticipo_{self.downpayment_id.name.replace('/', '-')}.pdf"
        elif self.report_type == 'downpayment_list' and self.building_id:
            # Buscar anticipos de la obra para generar el reporte
            downpayments = self.env['retana.downpayment'].search([('building_id', '=', self.building_id.id)])
            if downpayments:
                # Generar reporte con los IDs de los anticipos de la obra
                ids_str = ','.join(str(dp.id) for dp in downpayments)
                report_url = f"{base_url}/report/pdf/retana_bills.action_report_retana_downpayment_list/{ids_str}"
                report_name = f"RelacionPagos_{self.building_id.name.replace('/', '-')}.pdf"
        
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
