from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
RED = '\033[91m'
ENDC = '\033[0m'

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_retana_customer = fields.Boolean(string='Cliente Retana', default=False, tracking=True)
    retana_type_res_partner_id = fields.Many2one('retana.type.res.partner', string='Tipo de Cliente Retana', domain="[('active', '=', True)]", tracking=True)
    whatsapp_ids = fields.One2many('retana.whatsapp', 'partner_id', string='Números de WhatsApp')
    send_whatsapp = fields.Boolean(string='Enviar WhatsApp', default=False, tracking=True,
                                    help='Marca este contacto como destinatario válido para el envío de reportes por WhatsApp.')


    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        _logger.info(RED + "Contexto en res.partner create: %s" % self.env.context + ENDC)
        if self.env.context.get('default_is_retana_customer') == True:
            res.is_retana_customer = True
        if self.env.context.get('default_send_whatsapp') == True:
            res.send_whatsapp = True
        return res