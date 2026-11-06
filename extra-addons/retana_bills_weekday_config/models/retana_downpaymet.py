from odoo import fields, models


class RetanaDownpayment(models.Model):
    _inherit = ['retana.downpayment', 'retana.weekday.default.mixin']

    def _get_default_saturday(self):
        # El modelo base define un metodo con el mismo nombre (siempre el jueves) y, por el orden
        # de herencia, ganaria sobre el del mixin: se delega explicitamente al mixin.
        return self.env['retana.weekday.default.mixin']._get_default_saturday()

    date = fields.Date(
        string='Fecha del Anticipo',
        default=lambda self: self._get_default_saturday(),
    )
