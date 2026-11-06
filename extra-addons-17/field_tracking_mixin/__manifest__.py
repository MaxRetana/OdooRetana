# -*- coding: utf-8 -*-
{
    'name': 'Field Tracking Mixin',
    'version': '15.0.1',
    'category': 'Tools',
    'summary': 'Mixin genérico para trackear cambios en campos One2many y Many2many',
    'description': """
        Este módulo proporciona un mixin abstracto que permite trackear automáticamente
        cambios en campos One2many y Many2many, registrando los cambios en el chatter.
        
        Características:
        - Tracking automático de líneas agregadas, eliminadas y modificadas
        - Configuración flexible de campos a trackear
        - Mensajes HTML formateados en el chatter
        - Reutilizable en cualquier modelo
    """,
    'author': '[MaxRetana]',
    'website': 'https://maxretana.github.io/MaxRetana.Dev/',
    'depends': ['base', 'mail'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
