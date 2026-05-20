{
    "name": "Home",
    "summary": "Este modulo adaptara un home para visualizar todas las aplicaciones instaladas en el sistema",
    "description": 
        """
        Este modulo adaptara un home para visualizar todas las aplicaciones instaladas en el sistema, con el fin de facilitar la navegacion y acceso a las mismas.
        """,
    "author": ["MaxRetana"],
    "category": "base",
    "version": "18.1.0",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["base", "web"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/home_home_views.xml"
    ],
    'assets': {
        'web.assets_backend': [
            'home/static/src/css/home_dashboard.css',
            'home/static/src/js/home_dashboard.js',
            'home/static/src/xml/home_dashboard.xml',
        ],
    },
}
