from odoo import models, fields, api
from odoo.exceptions import UserError

class ExpenseTrackingCategory(models.Model):
    _name = 'expense.tracking.category'
    _description = 'Categoria de Gastos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', tracking=True)
    description = fields.Text('Descripción', tracking=True)
    color = fields.Integer('Color', tracking=True)
    active = fields.Boolean('Activo', default=True, tracking=True)