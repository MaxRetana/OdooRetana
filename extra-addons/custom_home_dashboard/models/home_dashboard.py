from odoo import models, fields, api
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)

class HomeDashboard(models.Model):
    _name = 'home.dashboard'
    _description = 'Home Dashboard'
    
    name = fields.Char(string='Name', default='Home Dashboard')
    
    @api.model
    def get_installed_apps(self):
        """Get all installed applications, including Settings and Apps"""
        try:
            # Get all installed modules that are applications
            apps = self.env['ir.module.module'].search([
                ('state', '=', 'installed'),
                ('application', '=', True)
            ])
            
            app_list = []
            for app in apps:
                if app.name == 'custom_home_dashboard':
                    # Skip the custom home dashboard module itself
                    continue
                # Get the menu associated with this app
                menu = self.env['ir.ui.menu'].search([
                    ('name', '=', app.shortdesc or app.name),
                    ('parent_id', '=', False)
                ], limit=1)
                
                if not menu:
                    # Try to find menu by technical name
                    menu = self.env['ir.ui.menu'].search([
                        ('name', 'ilike', app.name),
                        ('parent_id', '=', False)
                    ], limit=1)
                
                app_data = {
                    'id': app.id,
                    'name': app.shortdesc or app.name,
                    'technical_name': app.name,
                    'summary': app.summary or '',
                    'description': app.description or '',
                    'author': app.author or '',
                    'website': app.website or '',
                    'icon': self._get_app_icon(app.name),
                    'menu_id': menu.id if menu else False,
                    'web_icon': False,
                }
                app_list.append(app_data)
            
            # Add Settings manually
            app_list.append({
                'id': 'settings',
                'name': 'Settings',
                'technical_name': 'settings',
                'summary': 'System configuration and settings',
                'description': 'Access system settings and configurations',
                'author': 'Odoo',
                'website': '',
                'icon': 'fa-cogs',
                'menu_id': self.env.ref('base.menu_administration').id,
                'web_icon': False,
            })
            
            # CORRECCIÓN: Usar el menú correcto para Apps
            # Opción 1: Buscar por el external ID correcto
            try:
                apps_menu_id = self.env.ref('base.menu_management').id
            except:
                # Opción 2: Si no existe, buscar por varios nombres posibles
                apps_menu = self.env['ir.ui.menu'].search([
                    '|', '|', '|',
                    ('name', '=', 'Apps'),
                    ('name', '=', 'Applications'),
                    ('name', '=', 'Aplicaciones'),
                    ('name', 'ilike', 'app'),
                    ('parent_id', '=', False)
                ], limit=1)
                apps_menu_id = apps_menu.id if apps_menu else False
            
            app_list.append({
                'id': 'apps',
                'name': 'Apps',
                'technical_name': 'apps',
                'summary': 'Manage and install applications',
                'description': 'Access the app store to install and manage applications',
                'author': 'Odoo',
                'website': '',
                'icon': 'fa-th-large',
                'menu_id': apps_menu_id,
                'web_icon': False,
                # IMPORTANTE: Añadir acción específica para Apps
                'action_type': 'apps_store'
            })
            
            return app_list
            
        except AccessError:
            _logger.warning("Access denied when trying to get installed apps")
            return []
        except Exception as e:
            _logger.error("Error getting installed apps: %s", str(e))
            return []
    
    def _get_app_icon(self, module_name):
        """Get icon for the application"""
        # Common icons mapping
        icon_mapping = {
            'sale': 'fa-shopping-cart',
            'purchase': 'fa-shopping-bag',
            'account': 'fa-book',
            'stock': 'fa-truck',
            'hr': 'fa-users',
            'project': 'fa-tasks',
            'crm': 'fa-handshake-o',
            'website': 'fa-globe',
            'calendar': 'fa-calendar',
            'contacts': 'fa-address-book',
            'mail': 'fa-envelope',
            'documents': 'fa-folder',
            'manufacturing': 'fa-cogs',
            'quality': 'fa-check-circle',
            'maintenance': 'fa-wrench',
            'fleet': 'fa-car',
            'point_of_sale': 'fa-credit-card',
            'pos': 'fa-credit-card',
            'survey': 'fa-clipboard',
            'event': 'fa-ticket',
            'lunch': 'fa-cutlery',
            'expense': 'fa-money',
            'timesheet': 'fa-clock-o',
            'planning': 'fa-calendar-check-o',
            'social': 'fa-share-alt',
            'website_sale': 'fa-shopping-cart',
            'inventory': 'fa-cubes',
            'invoicing': 'fa-file-text',
            'marketing': 'fa-bullhorn',
            'helpdesk': 'fa-life-ring',
            'barcode': 'fa-barcode',
            'payment': 'fa-credit-card-alt',
        }
        
        # Try to find icon by module name
        for key, icon in icon_mapping.items():
            if key in module_name.lower():
                return icon
        
        # Default icon
        return 'fa-cube'
    
    @api.model
    def open_app(self, menu_id, action_type=None):
        """Open application by menu ID or special action"""
        
        # CORRECCIÓN: Manejar caso especial para Apps
        if action_type == 'apps_store':
            # Opción 1: Redirigir directamente a la acción de Apps
            return {
                'type': 'ir.actions.client',
                'tag': 'apps',
                'target': 'current',
            }
        
        # ALTERNATIVA: Si la opción anterior no funciona, usar esta
        # if action_type == 'apps_store':
        #     return {
        #         'type': 'ir.actions.act_window',
        #         'name': 'Apps',
        #         'res_model': 'ir.module.module',
        #         'view_mode': 'kanban,tree,form',
        #         'domain': [('application', '=', True)],
        #         'context': {'search_default_name': 1},
        #         'target': 'current',
        #     }
        
        if not menu_id:
            return False
            
        return {
            'type': 'ir.actions.client',
            'tag': 'menu',
            'params': {'menu_id': menu_id}
        }