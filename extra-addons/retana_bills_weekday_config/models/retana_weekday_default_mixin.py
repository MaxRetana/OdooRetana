from datetime import datetime, timedelta

from odoo import models


class RetanaWeekdayDefaultMixin(models.AbstractModel):
    """Mixin que centraliza el cálculo de la fecha por defecto de anticipos,
    según el día de la semana configurado en Ajustes > Anticipos Retana.

    Antes de la migración a 19.0, la misma lógica (``_get_configured_weekday``
    y ``_get_default_saturday``) estaba copiada y pegada en tres archivos
    distintos (``retana_downpayment_wizard.py``, ``retana_bulk_downpayment_wizard.py``
    y ``retana_downpaymet.py``). Se extrae aquí a un mixin para que los tres
    modelos la reutilicen, sin cambiar el comportamiento.
    """

    _name = 'retana.weekday.default.mixin'
    _description = 'Mixin: fecha por defecto de anticipos según día configurado'

    def _get_configured_weekday(self):
        weekday_value = self.env["ir.config_parameter"].sudo().get_param(
            "retana_bills_weekday_config.downpayment_weekday", "2"
        )
        try:
            weekday = int(weekday_value)
        except (TypeError, ValueError):
            weekday = 2

        if weekday < 0 or weekday > 6:
            return 2
        return weekday

    def _get_default_saturday(self):
        today = datetime.today()
        configured_weekday = self._get_configured_weekday()
        days_until_target = (configured_weekday - today.weekday()) % 7
        target_day = today + timedelta(days=days_until_target)
        return target_day.date()
