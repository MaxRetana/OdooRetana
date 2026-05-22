{
    "name": "Retana Web",
    "summary": "Este modulo permitira la visualizacion de retana_bills en la web",
    "description": 
        """
        Este modulo permitira la visualizacion de retana_bills en la web, permitiendo a los usuarios acceder a sus facturas de manera sencilla y eficiente. Con esta funcionalidad, los clientes podrán consultar y descargar sus facturas en formato digital, mejorando la experiencia del usuario y facilitando la gestión de sus documentos financieros.
        """,
    "author": ["MaxRetana"],
    "category": "base",
    "version": "18.1.0",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["base", "website", "retana_bills"],
    "data": [
        "views/retana_bills_templates.xml",
        "views/retana_site_menus.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "retana_web/static/src/scss/footer.scss",
        ],
    },
}
