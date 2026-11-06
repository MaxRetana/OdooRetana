from odoo import fields, models


class RetanaBulkDownpaymentWizard(models.TransientModel):
    _inherit = ['retana.bulk.downpayment.wizard', 'retana.weekday.default.mixin']

    date = fields.Date(
        string='Fecha del Anticipo',
        required=True,
        default='_get_default_saturday',
    )
