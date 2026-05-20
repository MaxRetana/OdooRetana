from odoo import models, fields, api

class RetanaTypeResPartner(models.Model):
    _name = 'retana.type.res.partner'
    _description = 'Tipo de Cliente Retana' 
    _inherit = ['mail.thread', 'mail.activity.mixin', 'field.tracking.mixin']
    
    name = fields.Char(string='Nombre del Tipo', tracking=True)
    code = fields.Char(string='Acrónimo', tracking=True)
    description = fields.Text(string='Descripción', tracking=True)
    active = fields.Boolean(string='Activo', default=True, tracking=True)