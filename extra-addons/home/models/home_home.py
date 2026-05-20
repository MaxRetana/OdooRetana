from odoo import models, fields, api

class HomeHome(models.Model):
    _name = 'home.home'
    _description = 'Accesos Rápidos del Home'
    _order = 'sequence'

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

    # La acción se vuelve automática basada en el menú
    action_id = fields.Many2one(
        'ir.actions.actions', 
        string="Acción Automática",
        compute='_compute_action_id',
        store=True,
        readonly=True
    )

    groups_ids = fields.Many2many('res.groups', string="Grupos permitidos")
                
    @api.depends('menu_id')
    def _compute_action_id(self):
        for record in self:
            if record.menu_id:
                # Obtenemos la referencia de la acción
                action_ref = record.menu_id.action
                if action_ref:
                    # Extraemos solo el ID numérico para evitar conflictos de tipo
                    record.action_id = action_ref.id
                else:
                    # Búsqueda en submenús si el principal es solo un contenedor
                    first_child = self.env['ir.ui.menu'].search([
                        ('parent_id', '=', record.menu_id.id),
                        ('action', '!=', False)
                    ], limit=1, order='sequence')
                    # Asignamos el ID del primer hijo encontrado
                    record.action_id = first_child.action.id if first_child and first_child.action else False
            else:
                record.action_id = False

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