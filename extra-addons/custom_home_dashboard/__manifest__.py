{
    'name': 'Custom Home Dashboard',
    'version': '16.0.1',
    'category': 'Tools',
    'summary': 'Custom Home Dashboard with App Cards',
    'description': """
        Custom Home Dashboard
        =====================
        
        This module provides a custom home dashboard that displays all installed
        applications as cards, similar to Odoo Enterprise home screen.
        
        Features:
        - View all installed apps as cards
        - Click to navigate to each app
        - Responsive design
        - Modern UI
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/home_dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_home_dashboard/static/src/css/home_dashboard.css',
            'custom_home_dashboard/static/src/js/home_dashboard.js',
            'custom_home_dashboard/static/src/xml/home_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}