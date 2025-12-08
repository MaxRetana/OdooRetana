from odoo import models, fields

class RetanaBudgetType(models.Model):
    _name = 'retana.budget.type'
    _description = 'Tipo de Presupuesto Retana'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name    =fields.Char(string='Tipo de Presupuesto' , tracking=True)
    active  =fields.Boolean(string='Activo', default=True, tracking=True)