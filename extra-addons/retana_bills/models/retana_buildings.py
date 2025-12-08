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