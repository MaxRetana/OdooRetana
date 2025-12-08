from odoo import models, fields, api

class RetanaDownpaymentTypeConcept(models.Model):
    _name = 'retana.downpayment.type.concept'
    _description = 'Concepto de Tipo de Anticipo Retana'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name        =fields.Char(string='Concepto de Anticipo' , tracking=True)
    active      =fields.Boolean(string='Activo', default=True, tracking=True)