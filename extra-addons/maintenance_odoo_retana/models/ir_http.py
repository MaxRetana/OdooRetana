# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request
from werkzeug.exceptions import HTTPException
import logging

_logger = logging.getLogger(__name__)


class MaintenanceRedirect(HTTPException):
    """Excepción personalizada para redirección de mantenimiento"""
    code = 302
    
    def __init__(self, location):
        self.location = location
        super(MaintenanceRedirect, self).__init__()
    
    def get_response(self, environ=None):
        from werkzeug.wrappers import Response
        return Response(
            'Redirecting...',
            status=302,
            headers={'Location': self.location}
        )


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls, endpoint):
        """
        Override del método _dispatch para interceptar todas las peticiones
        y verificar si el modo mantenimiento está activo
        """
        # Verificar si la ruta actual es la página de mantenimiento o rutas permitidas
        current_route = request.httprequest.path if request.httprequest else ''
        
        # Rutas que NO deben ser bloqueadas
        allowed_routes = [
            '/web/maintenance',
            '/web/session/logout',
            '/web/session/destroy',
            '/web/static/',
            '/web/assets/',
        ]
        
        # Verificar si la ruta está permitida
        is_allowed = any(current_route.startswith(route) for route in allowed_routes)
        
        # También permitir archivos estáticos por extensión
        if not is_allowed:
            static_extensions = ['.css', '.js', '.xml', '.json', '.woff', '.woff2', '.ttf', '.eot', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.map']
            is_allowed = any(current_route.endswith(ext) for ext in static_extensions)
        
        # Si NO está permitida, verificar el modo mantenimiento
        if not is_allowed:
            if request.env:
                try:
                    # Obtener el parámetro de configuración
                    ICP = request.env['ir.config_parameter'].sudo()
                    maintenance_enabled = ICP.get_param(
                        'maintenance_odoo_retana.maintenance_mode_enabled',
                        default='False'
                    )
                    
                    _logger.info(f">>> Verificando mantenimiento para {current_route} - Modo: {maintenance_enabled}")
                    
                    # Si el modo mantenimiento está activo
                    if maintenance_enabled == 'True':
                        # Verificar si el usuario tiene acceso al grupo de Ajustes
                        user = request.env.user
                        _logger.info(f">>> Usuario actual: {user.name} (ID: {user.id})")
                        
                        if user and user.id:
                            # Si NO es el usuario público y NO tiene permisos de sistema
                            try:
                                public_user = request.env.ref('base.public_user')
                                is_public = user.id == public_user.id
                            except:
                                is_public = False
                            
                            has_system_group = user.has_group('base.group_system')
                            _logger.info(f">>> Es público: {is_public}, Tiene permisos sistema: {has_system_group}")
                            
                            if not is_public and not has_system_group:
                                _logger.info(f">>> BLOQUEANDO {current_route} - Usuario sin permisos")
                                # Devolver página de mantenimiento con meta refresh
                                return request.make_response(
                                    '''<!DOCTYPE html>
                                    <html>
                                    <head>
                                        <meta charset="utf-8">
                                        <meta http-equiv="refresh" content="0; url=/web/maintenance">
                                        <script>window.location.replace('/web/maintenance');</script>
                                    </head>
                                    <body>
                                        <p>Redirigiendo a página de mantenimiento...</p>
                                    </body>
                                    </html>''',
                                    headers={'Content-Type': 'text/html; charset=utf-8'}
                                )
                except Exception as e:
                    _logger.error(f"Error verificando modo mantenimiento: {e}", exc_info=True)
        
        # Continuar con el dispatch normal
        return super(IrHttp, cls)._dispatch(endpoint)
