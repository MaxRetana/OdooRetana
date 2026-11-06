from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class RetanaDownpayment(models.Model):
    _inherit = 'retana.downpayment'
    
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
    
    date = fields.Date(
        string='Fecha del Anticipo',
        default=_get_default_saturday,
    )