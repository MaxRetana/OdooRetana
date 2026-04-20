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
        "data/retana_company_info_data.xml",
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/retana_bills_menus.xml",
        "views/retana_res_partner.xml",
        "views/retana_product_template.xml",
        "views/retana_budget_line_views.xml",
        "views/retana_budget_type_views.xml",
        "views/retana_budget_views.xml",
        "views/retana_buildings_views.xml",
        "views/retana_company_info_views.xml",
        "views/retana_downpayment_type_concept_views.xml",
        "views/retana_downpayment_views.xml",
        "views/retana_downpayment_wizard_views.xml",
        "views/retana_bulk_downpayment_wizard_views.xml",
        "views/retana_send_whatsapp_wizard_views.xml",
        "views/retana_sent_wh_views.xml",
        "views/retana_type_res_partner_views.xml",
        "report/retana_budget_report.xml",
        "report/retana_downpayment_list_report.xml",
        "report/retana_downpayment_report.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "retana_bills/static/src/js/retana_bills.js",
            "retana_bills/static/src/js/whatsapp_action.js",
            "retana_bills/static/src/xml/retana_bills.xml",
            "retana_bills/static/src/css/retana_bills.css",
        ],
    },
}
