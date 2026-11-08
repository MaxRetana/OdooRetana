from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class RetanaDownpayment(models.Model):
    _name = 'retana.downpayment'
    _description = 'Anticipos de Presupuestos Retana'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'field.tracking.mixin', 'retana.downpayment.date.mixin']
    _order = 'date desc, id desc'

    name            =fields.Char(string='Nombre del Anticipo', default='Nuevo', tracking=True)
    concept_id     =fields.Many2one('retana.downpayment.type.concept', string='Concepto de Anticipo', tracking=True)
    building_id     =fields.Many2one('retana.buildings', string='Obra', domain="[('active', '=', True)]", tracking=True, index=True)
    client_id       =fields.Many2one('res.partner', string='Cliente', domain="[('is_retana_customer', '=', True)]", tracking=True, index=True)
    date            =fields.Date(string='Fecha del Anticipo', default=lambda self: self._get_default_downpayment_date(), tracking=True, index=True)
    amount          =fields.Monetary(string='Importe del Anticipo', currency_field='currency_id', tracking=True)
    currency_id     =fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id, tracking=True)
    
    
    @api.constrains('amount')
    def _check_amount_positive(self):
        for record in self:
            if record.amount <= 0:
                raise UserError("El importe del anticipo debe ser un valor positivo.")
    
    
    @api.constrains('building_id', 'client_id')
    def _check_building_belongs_to_client(self):
        for record in self:
            building_client = record.building_id.client_id
            if building_client and record.client_id and building_client != record.client_id:
                raise ValidationError(
                    f'La obra "{record.building_id.name}" pertenece a {building_client.name}, '
                    f'no a {record.client_id.name}.'
                )

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
                vals['name'] = self.env['ir.sequence'].next_by_code('retana.downpayment') or '0001'
        return super().create(vals_list)