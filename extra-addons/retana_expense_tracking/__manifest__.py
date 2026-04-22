{
    "name": "Control de Gastos Retana",
    "summary": "Modulo para el control de gastos",
    "description": 
        """
        Este módulo permite a los usuarios registrar y gestionar sus gastos de manera eficiente.
        Con esta herramienta, los usuarios pueden ingresar detalles de cada gasto, como la categoría, el monto, la fecha y una descripción. Además, el módulo ofrece funcionalidades para visualizar y analizar los gastos a través de informes y gráficos, lo que facilita la toma de decisiones financieras. Es una solución ideal para individuos y pequeñas empresas que buscan mantener un control efectivo sobre sus finanzas personales o comerciales.
        """,
    "author": ["MaxRetana"],
    "category": "base",
    "version": "15.0.0",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["base", "mail"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/card_bank_line_views.xml",
        "views/card_bank_views.xml",
        "views/expense_tracking_category_views.xml",
        "views/expense_tracking_lines_views.xml",
        "views/expense_tracking_type_views.xml",
        "views/expense_tracking_views.xml",
        "views/menu_views.xml"
    ],
}
