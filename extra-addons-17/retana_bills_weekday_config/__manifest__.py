{
    "name": "Retana Bills Weekday Config",
    "summary": "Permite configurar el dia por defecto de anticipos desde Ajustes",
    "description": """
        Modulo para configurar desde Ajustes el dia por defecto
        que usa el wizard de anticipos de Retana Bills.
    """,
    "author": ["MaxRetana"],
    "category": "Accounting",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "depends": ["base", "retana_bills"],
    "data": [
        "views/res_config_settings_views.xml"
    ],
}
