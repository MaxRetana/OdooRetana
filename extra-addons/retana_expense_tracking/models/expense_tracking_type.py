from odoo import models, fields, api
from odoo.exceptions import UserError


class ExpenseTrackingType(models.Model):
    _name = 'expense.tracking.type'
    _description = 'Tipo de Gastos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', tracking=True)
    description = fields.Text('Descripción', tracking=True)
    active = fields.Boolean('Activo', default=True, tracking=True)
