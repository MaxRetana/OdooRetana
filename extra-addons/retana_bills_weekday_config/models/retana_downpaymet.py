from odoo import fields, models


class RetanaDownpayment(models.Model):
    _inherit = ['retana.downpayment', 'retana.weekday.default.mixin']

    date = fields.Date(
        string='Fecha del Anticipo',
        default='_get_default_saturday',
    )
