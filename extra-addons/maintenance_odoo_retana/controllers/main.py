# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class MaintenanceMode(http.Controller):

    @http.route('/web/maintenance', type='http', auth='public', csrf=False, website=True)
    def maintenance_page(self, **kw):
        """Página de mantenimiento - accesible para cualquier usuario"""
        _logger.info("=== ACCEDIENDO A PÁGINA DE MANTENIMIENTO ===")
        
        # Mensaje por defecto
        message = 'El sistema está en mantenimiento. Por favor, intente más tarde.'
        # Vista de mantenimiento
        template = 'maintenance_odoo_retana.maintenance_page'
        
        # Retornar vista
        return request.render(template, {
            'message': message,
        })