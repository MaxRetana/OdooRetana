from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class RetanaDownpayment(models.Model):
    _name = 'retana.downpayment'
    _description = 'Anticipos de Presupuestos Retana'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'field.tracking.mixin']
    
    def _get_default_saturday(self):
        """Retorna el jueves de la semana en curso"""
        today = datetime.today()
        # weekday() retorna 0=Lunes, 3=Jueves
        days_until_thursday = (3 - today.weekday()) % 7
        thursday = today + timedelta(days=days_until_thursday)
        return thursday.date()
    
    name            =fields.Char(string='Nombre del Anticipo', default='Nuevo', tracking=True)
    concept_id     =fields.Many2one('retana.downpayment.type.concept', string='Concepto de Anticipo', tracking=True)
    building_id     =fields.Many2one('retana.buildings', string='Obra', domain="[('active', '=', True)]", tracking=True)
    client_id       =fields.Many2one('res.partner', string='Cliente', domain="[('is_retana_customer', '=', True)]", tracking=True)
    date            =fields.Date(string='Fecha del Anticipo', default=_get_default_saturday, tracking=True)
    amount          =fields.Monetary(string='Importe del Anticipo', currency_field='currency_id', tracking=True)
    currency_id     =fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id, tracking=True)
    
    
    @api.constrains('amount')
    def _check_amount_positive(self):
        for record in self:
            if record.amount <= 0:
                raise UserError("El importe del anticipo debe ser un valor positivo.")
    
    
    @api.onchange('building_id')
    def _onchange_building_id(self):
        if self.building_id:
            self.client_id = self.building_id.client_id
        else:
            self.client_id = False
            
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'Nuevo':
                # Buscar si existe la secuencia, si no existe la crea
                sequence = self.env['ir.sequence'].search([('code', '=', 'retana.downpayment')], limit=1)
                if not sequence:
                    sequence = self.env['ir.sequence'].create({
                        'name': 'Retana Downpayment Sequence',
                        'code': 'retana.downpayment',
                        'prefix': 'RD',
                        'padding': 4,
                        'number_next': 1,
                        'number_increment': 1,
                    })
                # Generar el siguiente número
                next_number = self.env['ir.sequence'].next_by_code('retana.downpayment') or '0001'
                vals['name'] = f"{next_number}"
        return super().create(vals_list)