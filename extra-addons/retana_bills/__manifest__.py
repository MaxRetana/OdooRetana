{
    "name": "Electricos Retana",
    "summary": "Este modulo gestiona Presupuestos, Facturas y Clientes de Electricos Retana",
    "description": 
        """
            Este modulo gestiona Presupuestos, Facturas y Clientes de Electricos Retana.
        """,
    "author": ["MaxRetana"],
    "category": "base",
    "version": "15.0.0",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["base", "mail", "field_tracking_mixin", "account", "product"],
    "data": [
        "security/ir.model.access.csv",
        "views/retana_bills_menus.xml",
        "views/res_partner_views.xml",
        "views/retana_budget_type_views.xml",
        "views/retana_budget_line_views.xml",
        "views/retana_buildings_views.xml",
        "views/retana_budget_views.xml",
        "report/retana_budget_report.xml",
    ],
}
