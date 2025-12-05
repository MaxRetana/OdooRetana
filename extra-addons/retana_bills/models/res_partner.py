from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
RED = '\033[91m'
ENDC = '\033[0m'

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_retana_customer = fields.Boolean(string='Cliente Retana', default=False)
    
    
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        _logger.info(RED + "Contexto en res.partner create: %s" % self.env.context + ENDC)
        if self.env.context.get('default_is_retana_customer') == True:
            res.is_retana_customer = True
        return res