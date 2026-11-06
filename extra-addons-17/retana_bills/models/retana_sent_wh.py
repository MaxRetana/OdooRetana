from odoo import models, fields, api
import urllib.parse

class RetanaSentWh(models.Model):
    _name = 'retana.sent.wh'
    _description = 'Enviar Reportes por WhatsApp'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'field.tracking.mixin']
    
    name = fields.Char(string='Nombre', required=True, tracking=True)
    phone_number = fields.Char(string='Número de Teléfono', required=True, tracking=True)
    report_type = fields.Selection([
        ('budget', 'Presupuesto'),
        ('downpayment', 'Anticipo'),
        ('downpayment_list', 'Lista de Anticipos'),
    ], string='Tipo de Reporte', default='budget', tracking=True)
    message = fields.Text(string='Mensaje Predeterminado', default='Hola, te envío el reporte solicitado.', tracking=True)
    last_sent_date = fields.Datetime(string='Última Fecha de Envío', readonly=True, tracking=True)
    sent_count = fields.Integer(string='Cantidad de Envíos', default=0, readonly=True, tracking=True)
    
    def action_send_whatsapp(self):
        """Abre WhatsApp con el mensaje y enlace al reporte"""
        self.ensure_one()
        
        # Limpiar el número de teléfono (quitar espacios, guiones, etc.)
        phone = ''.join(filter(str.isdigit, self.phone_number))
        
        # Construir el mensaje completo
        full_message = self.message or 'Hola, te envío el reporte solicitado.'
        
        # Codificar el mensaje para URL
        encoded_message = urllib.parse.quote(full_message)
        
        # Construir URL de WhatsApp Web
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
        
        # Actualizar estadísticas de envío
        self.write({
            'last_sent_date': fields.Datetime.now(),
            'sent_count': self.sent_count + 1,
        })
        
        # Retornar acción para abrir WhatsApp
        return {
            'type': 'ir.actions.act_url',
            'url': whatsapp_url,
            'target': 'new',
        }
    
    def action_open_wizard(self):
        """Abre el wizard de envío con los datos precargados"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enviar por WhatsApp',
            'res_model': 'retana.send.whatsapp.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_phone': self.phone_number,
                'default_message': self.message,
                'default_report_type': self.report_type,
            }
        }
