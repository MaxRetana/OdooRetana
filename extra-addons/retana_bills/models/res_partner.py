from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_retana_customer = fields.Boolean(string='Cliente Retana', default=False, tracking=True)
    retana_type_res_partner_id = fields.Many2one('retana.type.res.partner', string='Tipo de Cliente Retana', domain="[('active', '=', True)]", tracking=True)
