from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    downpayment_weekday = fields.Selection(
        selection=[
            ("0", "Lunes"),
            ("1", "Martes"),
            ("2", "Miercoles"),
            ("3", "Jueves"),
            ("4", "Viernes"),
            ("5", "Sabado"),
            ("6", "Domingo"),
        ],
        string="Dia por defecto para anticipos",
        config_parameter="retana_bills_weekday_config.downpayment_weekday",
        default="3",
        required=True,
        help="Dia de la semana que se usara por defecto en la fecha de los anticipos (jueves si no se configura).",
    )
