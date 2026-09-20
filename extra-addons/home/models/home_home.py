import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HomeHome(models.Model):
    _name = 'home.home'
    _description = 'Accesos Rápidos del Home'
    _order = 'sequence'

    _sql_constraints = [
        ('menu_id_unique', 'unique(menu_id)',
         'Ya existe un acceso rápido para ese menú.'),
    ]

    active = fields.Boolean(default=True)
    name = fields.Char(string="Etiqueta de la App", required=True, translate=True)
    sequence = fields.Integer(default=10)
    
    icon_type = fields.Selection([
        ('fontawesome', 'FontAwesome'),
        ('custom', 'Imagen Personalizada')
    ], string="Tipo de Icono", default='fontawesome')

    fa_icon = fields.Char(string="Icono (FontAwesome)", default="fa-th-large")
    
    custom_icon = fields.Image(string="Imagen Personalizada", max_width=128, max_height=128)
    
    # Seleccionamos el menú raíz (el que aparece en el tablero de Odoo)
    # Seleccionamos el menú que representa a la aplicación
    menu_id = fields.Many2one(
        'ir.ui.menu', 
        string="Menú Principal de la App",
        # Quitamos la restricción de action si es necesario, 
        # pero filtramos por los que tienen icono web (las apps del dashboard)
        domain=[('parent_id', '=', False)],
        help="Selecciona el ícono del menú principal que quieres mostrar"
    )

    groups_ids = fields.Many2many('res.groups', string="Grupos permitidos")
                
    @api.onchange('menu_id')
    def _onchange_menu_id(self):
        if self.menu_id:
            # Sugerimos el nombre y el icono original del menú de Odoo
            self.name = self.menu_id.name
            if self.menu_id.web_icon:
                # El formato de web_icon suele ser 'icono,color,fondo' o una clase fa
                icon_parts = self.menu_id.web_icon.split(',')
                if len(icon_parts) > 0 and 'fa-' in icon_parts[0]:
                    self.fa_icon = icon_parts[0]
    
    @api.onchange('fa_icon')
    def _onchange_fa_icon(self):
        if self.fa_icon and not self.fa_icon.startswith('fa-'):
            self.fa_icon = 'fa-' + self.fa_icon

    @api.constrains('fa_icon')
    def _check_fa_icon(self):
        for record in self:
            if record.fa_icon and not re.fullmatch(r'fa-[a-z0-9-]+', record.fa_icon):
                raise ValidationError(_(
                    "El icono '%s' no es válido. Usa el formato de FontAwesome, por ejemplo: fa-rocket.",
                    record.fa_icon,
                ))
