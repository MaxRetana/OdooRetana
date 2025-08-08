# -*- coding: utf-8 -*-
{
    'name': 'Retana Custom Odoo',
    'summary': 'This module costomizes Odoo for Retana',
    'author': 'MaxRetana',
    'category': 'Base',
    'version': '17.0.0.1',
    'depends': ['base', 'web'],
    'data': [
        # 'static/src/xml/retana_theme.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'retana_custom/static/src/css/retana_dark_theme.css',
            'retana_custom/static/src/js/retana_theme.js',
        ],
    },
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
