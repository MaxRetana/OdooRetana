from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

# Campos que no se pueden modificar cuando el presupuesto esta aprobado
APPROVED_LOCKED_FIELDS = {
    'title', 'description', 'client_id', 'building_id', 'date', 'currency_id',
    'budget_type_id', 'discount', 'line_ids', 'downpayment_amount', 'taxes_ids', 'show_sign',
}


class RetanaBudget(models.Model):
    _name = 'retana.budget'
    _description = 'Presupuestos Retana'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'field.tracking.mixin']
    _order = 'date desc, id desc'

    # Nota (migracion 19.0): las claves usaban 'linea_ids'/'producto_id', que no
    # existen en el modelo (los campos reales son 'line_ids'/'product_id', ver
    # mas abajo). Por ese typo, field.tracking.mixin nunca encontraba
    # coincidencia entre _tracked_fields y los vals de write(), asi que el
    # tracking de lineas de presupuesto en el chatter nunca se disparaba. Se
    # corrige para que coincida con los nombres reales de los campos.
    _tracked_fields = {
        'line_ids': {
            'type': 'one2many',
            'display_name': 'Líneas de Presupuesto',
            'fields_to_track': ['product_id', 'quantity', 'unit_price', 'taxes_ids', 'subtotal', 'display_type'],
            'display_fields': {
                'product_id': lambda val: val.name if val else 'Sin producto',
                'quantity': lambda val: str(val),
                'unit_price': lambda val: f"${val:,.2f}",
                'subtotal': lambda val: f"${val:,.2f}",
                'display_type': lambda val: 'Sección' if val == 'line_section' else ('Nota' if val == 'line_note' else 'Línea normal'),
            }
        }
    }
    name                =fields.Char(string='Referencia', copy=False, default='Nuevo', tracking=True)
    title               =fields.Char(string='Título', tracking=True)
    description         =fields.Text(string='Descripción', tracking=True)
    client_id           =fields.Many2one('res.partner', string='Cliente', domain="[('is_retana_customer', '=', True)]", tracking=True, index=True)
    building_id         =fields.Many2one('retana.buildings', string='Obra', domain="[('client_id', '=', client_id)]", tracking=True)
    date                =fields.Date(string='Fecha', default=fields.Date.context_today, tracking=True, index=True)
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
    show_sign           =fields.Boolean(string='Mostrar firma', default=True, tracking=True)
    state               =fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviado'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ], string='Estado', default='draft', required=True, copy=False, tracking=True, index=True)

    def _check_has_lines(self):
        for budget in self:
            if not budget.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(f'El presupuesto {budget.name} no tiene conceptos. Agrega al menos uno antes de continuar.')

    @api.constrains('discount')
    def _check_discount_range(self):
        for budget in self:
            if not 0.0 <= budget.discount <= 1.0:
                raise ValidationError('El descuento debe estar entre 0 % y 100 %.')

    @api.constrains('downpayment_amount')
    def _check_downpayment_not_negative(self):
        for budget in self:
            if budget.downpayment_amount < 0:
                raise ValidationError('El anticipo no puede ser negativo.')

    @api.constrains('line_ids', 'downpayment_amount', 'discount', 'taxes_ids')
    def _check_total_not_negative(self):
        # En la carga de datos de modulos los presupuestos llegan antes que sus lineas
        if self.env.context.get('install_mode'):
            return
        for budget in self:
            if budget.currency_id and budget.currency_id.compare_amounts(budget.total_amount, 0.0) < 0:
                raise ValidationError(
                    f'El total del presupuesto {budget.name} no puede ser negativo: '
                    'el anticipo y el descuento superan el importe de los conceptos.'
                )

    @api.constrains('client_id', 'building_id')
    def _check_building_belongs_to_client(self):
        for budget in self:
            building_client = budget.building_id.client_id
            if building_client and budget.client_id and building_client != budget.client_id:
                raise ValidationError(
                    f'La obra "{budget.building_id.name}" pertenece a {building_client.name}, '
                    f'no a {budget.client_id.name}.'
                )

    def action_send(self):
        self._check_has_lines()
        self.filtered(lambda budget: budget.state == 'draft').write({'state': 'sent'})

    def action_approve(self):
        self._check_has_lines()
        self.filtered(lambda budget: budget.state in ('draft', 'sent')).write({'state': 'approved'})

    def action_reject(self):
        self.filtered(lambda budget: budget.state in ('draft', 'sent')).write({'state': 'rejected'})

    def action_draft(self):
        """Rechazado vuelve a borrador; reabrir un aprobado es solo del administrador."""
        if self.filtered(lambda budget: budget.state == 'approved') and \
                not self.env.user.has_group('retana_bills.group_retana_admin'):
            raise UserError('Solo un administrador puede reabrir un presupuesto aprobado.')
        self.filtered(lambda budget: budget.state in ('approved', 'rejected')).write({'state': 'draft'})

    def write(self, vals):
        if APPROVED_LOCKED_FIELDS & vals.keys() and 'state' not in vals \
                and not self.env.context.get('install_mode') \
                and self.filtered(lambda budget: budget.state == 'approved'):
            raise UserError('El presupuesto está aprobado y no se puede modificar. '
                            'Un administrador puede reabrirlo.')
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get('install_mode') and self.filtered(lambda budget: budget.state == 'approved'):
            raise UserError('No se puede borrar un presupuesto aprobado. Reábralo primero.')
        return super().unlink()
    
    @api.onchange('budget_type_id', 'client_id', 'building_id')
    def _onchange_budget_type_id(self):
        for budget in self:
            # Construir el título completo desde cero cada vez
            title_parts = []
            
            # Parte 1: Tipo de presupuesto (siempre primero)
            if budget.budget_type_id:
                title_parts.append(budget.budget_type_id.name)
            
            # Parte 2: Cliente (siempre segundo)
            if budget.client_id:
                client_part = f"PARA EL {budget.client_id.retana_type_res_partner_id.code} {budget.client_id.name}"
                title_parts.append(client_part)
            
            # Parte 3: Edificio (siempre tercero)
            if budget.building_id:
                building_part = f"EN LA OBRA {budget.building_id.name}"
                title_parts.append(building_part)
            
            # Unir todas las partes con espacio
            budget.title = " ".join(title_parts).upper()

    @api.depends('line_ids.subtotal', 'line_ids.taxes_ids', 'line_ids.quantity', 'line_ids.unit_price',
                 'line_ids.display_type', 'currency_id', 'discount', 'downpayment_amount')
    def _compute_amounts(self):
        for budget in self:
            subtotal = 0.0
            tax_total = 0.0
            for line in budget.line_ids.filtered(lambda l: not l.display_type):
                taxes = line._compute_taxes()
                subtotal += taxes['total_excluded']
                tax_total += sum(tax['amount'] for tax in taxes['taxes'])
            budget.subtotal_amount = subtotal
            budget.tax_amount = tax_total
            # El widget percentage guarda el valor como decimal (0.1 = 10%)
            budget.discount_amount = budget.currency_id.round(subtotal * budget.discount) if budget.currency_id else subtotal * budget.discount
            budget.total_amount = subtotal + tax_total - budget.discount_amount - budget.downpayment_amount

    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = 'Nuevo'
        line_vals = []
        for line in self.line_ids:
            vals = line.copy_data()[0]
            vals.pop('budget_id', None)
            line_vals.append((0, 0, vals))
        # Las lineas viajan en el create para que las validaciones vean el presupuesto completo
        default['line_ids'] = line_vals
        return super().copy(default=default)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('retana.budget') or '0001'
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