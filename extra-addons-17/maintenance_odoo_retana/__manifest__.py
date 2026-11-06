{
    "name": "Ventana de Mantenimiento Odoo Retana",
    "summary": "Este modulo proporciona una ventana de mantenimiento personalizada para Odoo Retana",
    "description": 
        """
            Este modulo proporciona una ventana de mantenimiento personalizada para Odoo Retana.
            Cuando se activa el modo mantenimiento, solo los usuarios con permisos de Ajustes/Configuración
            pueden acceder al sistema. Los demás usuarios verán una página de mantenimiento personalizada.
            
            Características:
            - Activar/desactivar modo mantenimiento desde Ajustes
            - Mensaje personalizable de mantenimiento
            - Tiempo estimado de finalización configurable
            - Solo usuarios del grupo 'Ajustes' pueden acceder durante el mantenimiento
            - Página de mantenimiento con diseño atractivo y profesional
        """,
    "author": ["MaxRetana"],
    "category": "Administration",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/maintenance_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "maintenance_odoo_retana/static/src/js/maintenance_check.js",
        ],
    },
}
