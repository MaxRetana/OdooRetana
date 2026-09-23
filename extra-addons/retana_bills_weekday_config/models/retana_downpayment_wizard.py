from odoo import fields, models


class RetanaDownpaymentWizard(models.TransientModel):
    _inherit = ['retana.downpayment.wizard', 'retana.weekday.default.mixin']

    date = fields.Date(
        string='Fecha del Anticipo',
        required=True,
        default='_get_default_saturday',
    )
