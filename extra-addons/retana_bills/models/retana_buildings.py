from odoo import models, fields

class RetanaBuildings(models.Model):
    _name = 'retana.buildings'
    _description = 'Obras Retana'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name        =fields.Char(string='Nombre del Edificio', tracking=True)
    client_id   =fields.Many2one('res.partner', string='Cliente', domain="[('is_retana_customer', '=', True)]", tracking=True)
    active      =fields.Boolean(string='Activo', default=True, tracking=True)
    
    
    def action_create_downpayment(self):
        """Acción para crear un anticipo desde la obra"""
        self.ensure_one()
        return {
            'name': 'Crear Anticipo',
            'type': 'ir.actions.act_window',
            'res_model': 'retana.downpayment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_building_id': self.id,
                'default_client_id': self.client_id.id,
            },
        }
    
    def action_print_downpayments_list(self):
        """Acción para imprimir la relación de pagos de la obra"""
        self.ensure_one()
        # Buscar todos los anticipos de esta obra
        downpayments = self.env['retana.downpayment'].search([
            ('building_id', '=', self.id)
        ], order='date asc')
        
        if not downpayments:
            # Si no hay anticipos, mostrar mensaje
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Sin anticipos',
                    'message': 'Esta obra no tiene anticipos registrados.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Generar el reporte con los anticipos encontrados
        return self.env.ref('retana_bills.action_report_retana_building_downpayments').report_action(downpayments)