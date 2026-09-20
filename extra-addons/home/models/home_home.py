import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HomeHome(models.Model):
    _name = 'home.home'
    _description = 'Accesos Rápidos del Home'
    _order = 'sequence, id'

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
    
    color = fields.Char(
        string="Color de fondo",
        help="Color (hexadecimal) del recuadro del icono. Vacío para usar el estilo por defecto.",
    )

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
                
    @api.model
    def _get_icon_values_from_menu(self, menu):
        """Devuelve los valores de icono equivalentes al icono original del menú.

        - Si el web_icon del menú es una clase FontAwesome ('fa-xxx,color,fondo'), se usa tal cual.
        - Si el menú tiene una imagen (web_icon_data), se copia como imagen personalizada.
        - En otro caso no se sugiere nada y se conserva el icono actual.
        """
        icon_parts = (menu.web_icon or '').split(',')
        if icon_parts[0].startswith('fa-'):
            return {'icon_type': 'fontawesome', 'fa_icon': icon_parts[0]}
        if menu.web_icon_data:
            return {'icon_type': 'custom', 'custom_icon': menu.web_icon_data}
        return {}

    @api.onchange('menu_id')
    def _onchange_menu_id(self):
        if not self.menu_id:
            return
        # No pisar una etiqueta que el usuario ya personalizó
        if not self.name or self.name == self._origin.menu_id.name:
            self.name = self.menu_id.name
        self.update(self._get_icon_values_from_menu(self.menu_id))

    @api.onchange('fa_icon')
    def _onchange_fa_icon(self):
        if self.fa_icon and not self.fa_icon.startswith('fa-'):
            self.fa_icon = 'fa-' + self.fa_icon

    def action_sync_apps(self):
        """Crea un acceso por cada aplicación (menú raíz) que todavía no tenga uno.

        Se ignoran los menús que ya tienen acceso, incluso archivado (para no resucitar
        los que el administrador quitó a propósito) y el propio menú del Home. La
        visibilidad real se comprueba al mostrar el dashboard (get_home_data).
        """
        self.check_access_rights('create')
        Menu = self.env['ir.ui.menu'].with_context(**{'ir.ui.menu.full_list': True})
        existing_menus = self.with_context(active_test=False).search([]).menu_id
        home_menu = self.env.ref('home.menu_home_home_root', raise_if_not_found=False)
        root_menus = Menu.search([('parent_id', '=', False)], order='sequence, id')
        vals_list = []
        for menu in root_menus - existing_menus - home_menu:
            vals = {'name': menu.name, 'menu_id': menu.id, 'sequence': menu.sequence}
            vals.update(self._get_icon_values_from_menu(menu))
            vals_list.append(vals)
        self.create(vals_list)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Aplicaciones sincronizadas"),
                'message': _("Se crearon %s accesos nuevos.", len(vals_list)),
                'type': 'success',
                'next': {'type': 'ir.actions.client', 'tag': 'reload'},
            },
        }

    @api.constrains('color')
    def _check_color(self):
        for record in self:
            if record.color and not re.fullmatch(r'#[0-9a-fA-F]{6}', record.color):
                raise ValidationError(_(
                    "El color '%s' no es válido. Usa el formato hexadecimal, por ejemplo: #714B67.",
                    record.color,
                ))

    @api.constrains('fa_icon')
    def _check_fa_icon(self):
        for record in self:
            if record.fa_icon and not re.fullmatch(r'fa-[a-z0-9-]+', record.fa_icon):
                raise ValidationError(_(
                    "El icono '%s' no es válido. Usa el formato de FontAwesome, por ejemplo: fa-rocket.",
                    record.fa_icon,
                ))

    @api.model
    def get_home_data(self):
        """Datos que necesita el dashboard para el usuario actual.

        Solo se devuelven los accesos activos cuyo menú es realmente accesible para el
        usuario y que no estén restringidos a grupos a los que no pertenece. La imagen
        personalizada no se envía en base64: se entrega una URL con un parámetro que
        cambia cuando se modifica el registro, para invalidar la caché del navegador.
        """
        shortcuts = self.search([('menu_id', '!=', False)])
        # ir.ui.menu.search solo devuelve los menús visibles para el usuario actual
        accessible_menus = self.env['ir.ui.menu'].search([('id', 'in', shortcuts.menu_id.ids)])
        user_groups = self.env.user.groups_id
        apps = []
        for shortcut in shortcuts:
            if shortcut.menu_id not in accessible_menus:
                continue
            if shortcut.groups_ids and not (shortcut.groups_ids & user_groups):
                continue
            icon_url = False
            if shortcut.icon_type == 'custom' and shortcut.custom_icon:
                version = int(shortcut.write_date.timestamp()) if shortcut.write_date else 0
                icon_url = f'/web/image/home.home/{shortcut.id}/custom_icon?unique={version}'
            apps.append({
                'id': shortcut.id,
                'name': shortcut.name,
                'menu_id': shortcut.menu_id.id,
                'icon_type': shortcut.icon_type,
                'fa_icon': shortcut.fa_icon,
                'icon_url': icon_url,
                'color': shortcut.color or False,
            })
        return {
            'apps': apps,
            'can_configure': self.env.user.has_group('home.group_home_home_admin'),
        }
