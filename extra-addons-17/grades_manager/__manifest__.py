# -*- coding: utf-8 -*-
{
    'name': 'Grades Manager',
    'summary': 'Manage student grades and performance',
    'description': 'This module allows teachers to manage student grades, track performance, and generate reports.',
    'author': 'MaxRetana',
    'category': 'Base',
    'version': '17.0.0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        
        'views/grades_course_views.xml',
        'views/res_partner_views.xml',
        'views/grades_evaluation_views.xml',
        'views/grades_manager_menu.xml',
    ],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
