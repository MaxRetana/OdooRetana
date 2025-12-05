from odoo import models, fields

class RetanaBuildings(models.Model):
    _name = 'retana.buildings'
    _description = 'Obras Retana'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name        =fields.Char(string='Nombre del Edificio')
    client_id   =fields.Many2one('res.partner', string='Cliente', domain="[('is_retana_customer', '=', True)]")
    active      =fields.Boolean(string='Activo', default=True)