# -*- coding: utf-8 -*-
{
    'name': 'Home menu',
    'summary': 'Manage home menu',
    'description': 'This module allows to users to manage the home menu.',
    'author': 'MaxRetana',
    'category': 'Base',
    'version': '17.0.0.1',
    'depends': ['base', 'web'],
    'data': [
        "views/home_menu.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'home/static/src/xml/home_view_template.xml',
        ],
    },
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
