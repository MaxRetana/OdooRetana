# -*- coding: utf-8 -*-
{
    'name': 'Retana Data Import',
    'summary': 'Carga los datos de Retana migrados desde Odoo 17',
    'description': """
        Al instalarse carga los datos de negocio de Retana (contactos, productos, presupuestos,
        anticipos, obras, tipos y conceptos) exportados de Odoo 17. Todos los registros llevan
        id externo `retana_data_import.*`, por lo que reinstalar no duplica datos.
        Para regenerar los CSV ver tools/export_data.py.
    """,
    'author': 'MaxRetana',
    'category': 'Base',
    'version': '19.0.1.0.0',
    'depends': ['base', 'product', 'account', 'retana_bills'],
    'data': [
        'data/retana_data_import_base.xml',
        # catalogos que usan los contactos y los presupuestos
        'data/retana.type.res.partner.csv',
        'data/retana.budget.type.csv',
        'data/retana.downpayment.type.concept.csv',
        'data/res.partner.csv',
        'data/product.template.csv',
        'data/retana_data_import_variants.xml',
        'data/retana.buildings.csv',
        'data/retana.budget.csv',
        'data/retana.budget.line.csv',
        'data/retana.downpayment.csv',
        'data/retana.sent.wh.csv',
        'data/retana.company.info.csv',
    ],
    'post_init_hook': 'post_init_hook',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
