from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)
RED = '\033[91m'
ENDC = '\033[0m'

class RetanaBudget(models.Model):
    _name = 'retana.budget'
    _description = 'Presupuestos Retana'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'field.tracking.mixin']
    
    _tracked_fields = {
        'linea_ids': {
            'type': 'one2many',
            'display_name': 'Líneas de Presupuesto',
            'fields_to_track': ['producto_id', 'quantity', 'unit_price', 'taxes_ids', 'subtotal'],
            'display_fields': {
                'producto_id': lambda val: val.name if val else 'Sin producto',
                'quantity': lambda val: str(val),
                'unit_price': lambda val: f"${val:,.2f}",
                'subtotal': lambda val: f"${val:,.2f}",
            }
        }
    }
    name                =fields.Char(string='Referencia', copy=False, default='Nuevo', tracking=True)
    client_id           =fields.Many2one('res.partner', string='Cliente', domain="[('is_retana_customer', '=', True)]", tracking=True)
    building_id         =fields.Many2one('retana.buildings', string='Obra', domain="[('client_id', '=', client_id)]", tracking=True)
    date                =fields.Date(string='Fecha', default=fields.Date.context_today, tracking=True)
    currency_id         =fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id, tracking=True)
    subtotal_amount     =fields.Monetary(string='Subtotal', compute='_compute_amounts', currency_field='currency_id', tracking=True)
    tax_amount          =fields.Monetary(string='IVA', compute='_compute_amounts', currency_field='currency_id', tracking=True)
    total_amount        =fields.Monetary(string='Total', compute='_compute_amounts', currency_field='currency_id', tracking=True)
    budget_type_id      =fields.Many2one('retana.budget.type', string='Tipo de Presupuesto', tracking=True)
    discount            =fields.Float(string='Descuento (%)', default=0.0, tracking=True)
    discount_amount     =fields.Monetary(string='Importe Descuento', compute='_compute_amounts', currency_field='currency_id', tracking=True)
    line_ids            =fields.One2many('retana.budget.line', 'budget_id', string='Líneas de Presupuesto', tracking=True)
    downpayment_amount  =fields.Monetary(string='Anticipo', currency_field='currency_id', tracking=True)
    taxes_ids           =fields.Many2many('account.tax', string='Impuestos', tracking=True)
    
    @api.depends('line_ids.subtotal', 'line_ids.taxes_ids', 'discount', 'downpayment_amount')
    def _compute_amounts(self):
        for budget in self:
            subtotal = 0.0
            tax_total = 0.0
            for line in budget.line_ids:
                subtotal += line.subtotal
                for tax in line.taxes_ids:
                    tax_total += line.subtotal * tax.amount / 100
            budget.subtotal_amount = subtotal
            budget.tax_amount = tax_total
            # El widget percentage guarda el valor como decimal (0.1 = 10%)
            budget.discount_amount = subtotal * budget.discount
            budget.total_amount = subtotal + tax_total - budget.discount_amount - budget.downpayment_amount
            _logger.info(f"{RED}Descuento: {budget.discount*100}%, Importe: {budget.discount_amount}{ENDC}")
            
            
            
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'Nuevo':
                # Buscar si existe la secuencia, si no existe la crea
                sequence = self.env['ir.sequence'].search([('code', '=', 'retana.budget')], limit=1)
                if not sequence:
                    sequence = self.env['ir.sequence'].create({
                        'name': 'Retana Budget Sequence',
                        'code': 'retana.budget',
                        'prefix': 'RB',
                        'padding': 4,
                        'number_next': 1,
                        'number_increment': 1,
                    })
                # Generar el siguiente número
                next_number = self.env['ir.sequence'].next_by_code('retana.budget') or '0001'
                vals['name'] = f"{next_number}"
        return super().create(vals_list)
    
    @api.onchange('discount')
    def _onchange_discount(self):
        for budget in self:
            # Con widget percentage, el valor ya viene como decimal (0.1 = 10%)
            if budget.discount < 0.0:
                budget.discount = 0.0
            elif budget.discount > 1.0:
                budget.discount = 1.0

    @api.onchange('taxes_ids')
    def _onchange_taxes_ids(self):
        for budget in self:
            for line in budget.line_ids:
                line.taxes_ids = budget.taxes_ids