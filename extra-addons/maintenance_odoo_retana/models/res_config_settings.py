# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    maintenance_mode_enabled = fields.Boolean(
        string='Modo Mantenimiento Activo',
        config_parameter='maintenance_odoo_retana.maintenance_mode_enabled',
        help='Cuando está activo, solo los usuarios del grupo de Ajustes pueden acceder al sistema. '
             'Los demás usuarios verán una página de mantenimiento.'
    )

    maintenance_message = fields.Char(
        string='Mensaje de Mantenimiento',
        config_parameter='maintenance_odoo_retana.maintenance_message',
        default='El sistema está en mantenimiento. Por favor, intente más tarde.',
        help='Mensaje que se mostrará a los usuarios durante el mantenimiento.'
    )
