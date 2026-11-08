from datetime import timedelta

from odoo import fields, models

DOWNPAYMENT_WEEKDAY_PARAM = 'retana_bills_weekday_config.downpayment_weekday'
DEFAULT_WEEKDAY = 3  # Jueves (0 = lunes)


class RetanaDownpaymentDateMixin(models.AbstractModel):
    """Fecha por defecto de los anticipos: el proximo dia de la semana configurado
    en Ajustes (modulo retana_bills_weekday_config) o el jueves si no hay ajuste."""
    _name = 'retana.downpayment.date.mixin'
    _description = 'Fecha por defecto de anticipos segun el dia configurado'

    def _get_configured_weekday(self):
        value = self.env['ir.config_parameter'].sudo().get_param(DOWNPAYMENT_WEEKDAY_PARAM)
        if not value:  # sin configurar: get_param devuelve False e int(False) seria lunes
            return DEFAULT_WEEKDAY
        try:
            weekday = int(value)
        except (TypeError, ValueError):
            return DEFAULT_WEEKDAY
        return weekday if 0 <= weekday <= 6 else DEFAULT_WEEKDAY

    def _get_default_downpayment_date(self):
        today = fields.Date.context_today(self)
        days_until_target = (self._get_configured_weekday() - today.weekday()) % 7
        return today + timedelta(days=days_until_target)
