{
    "name": "Tareas Personales",
    "summary": "Este modulo permite gestionar tareas personales.",
    "description": 
        """
        Este modulo permite gestionar tareas personales.
        """,
    "author": ["MaxRetana"],
    "category": "Custom",
    "version": "15.0.0",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        
        "views/personal_task_views.xml",
        
        "data/email_template_deadline_reminder.xml",
        "data/cron.xml",
    ],
}
