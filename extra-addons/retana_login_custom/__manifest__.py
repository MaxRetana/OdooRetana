{
    "name": "Retana Custom Login",
    "summary": "Este modulo permitira la personalizacion de la pantalla de inicio de sesion",
    "description": 
        """
        Este modulo permitira la personalizacion de la pantalla de inicio de sesion.
        """,
    "author": ["MaxRetana"],
    "category": "base",
    "version": "18.1.0",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["base", "website", "web"],
    "data": [
        "views/retana_login_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "retana_login_custom/static/src/scss/login.scss",
        ],
    },
}
