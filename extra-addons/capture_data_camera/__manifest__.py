{
    "name": "Captura de datos con camara",
    "summary": "Este modulo permite capturar datos con la camara del dispositivo o adjuntar imagenes",
    "description": 
        """
            ste modulo permite capturar datos con la camara del dispositivo o adjuntar imagenes
        """,
    "author": "MaxRetana",
    "category": "base",
    "version": "15.0.0",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "depends": ["base", "hr"],
    "data": [
        "views/view_employee_form_inherit.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'capture_data_camera/static/src/js/upload_employee_image.js',
        ],
    },
}