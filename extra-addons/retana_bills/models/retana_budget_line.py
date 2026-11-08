from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class RetanaBudgetLine(models.Model):
    _name = 'retana.budget.line'
    _description = 'Líneas de Presupuesto Retana'
    _order = 'sequence, id'
    
    sequence    =fields.Integer(string='Secuencia', default=10)
    budget_id   =fields.Many2one('retana.budget', string='Presupuesto', ondelete='cascade')
    display_type =fields.Selection([
        ('line_section', 'Sección'),
        ('line_note', 'Nota')
    ], string='Tipo de línea', default=False)
    product_id  =fields.Many2one('product.product', string='Concepto')
    description =fields.Char(string='Descripción')
    quantity    =fields.Float(string='Cantidad', default=1.0)
    currency_id =fields.Many2one(related='budget_id.currency_id', string='Moneda', store=True)
    unit_price  =fields.Monetary(string='Precio Unitario', currency_field='currency_id')
    uom_id      =fields.Many2one('uom.uom', string='Unidad de Medida')
    taxes_ids   =fields.Many2many('account.tax', string='Impuestos')
    subtotal    =fields.Monetary(string='Subtotal', compute='_compute_subtotal', currency_field='currency_id')
    
    def _check_budget_required(self, vals_list):
        # Se valida aqui y no con required=True porque hay lineas antiguas sin presupuesto
        # (el CSV de retana_data_import las recarga; install_mode no pasa por la validacion)
        if not self.env.context.get('install_mode') and any(not vals.get('budget_id') for vals in vals_list):
            raise ValidationError('La línea debe pertenecer a un presupuesto.')

    @api.constrains('quantity', 'unit_price', 'display_type')
    def _check_not_negative(self):
        for line in self.filtered(lambda line: not line.display_type):
            if line.quantity < 0:
                raise ValidationError('La cantidad no puede ser negativa.')
            if line.unit_price < 0:
                raise ValidationError('El precio unitario no puede ser negativo.')

    @api.constrains('quantity', 'unit_price', 'taxes_ids')
    def _check_budget_total(self):
        self.budget_id._check_total_not_negative()

    def _compute_taxes(self):
        """Impuestos de la linea calculados por Odoo (respeta redondeo y tipo de impuesto)."""
        self.ensure_one()
        return self.taxes_ids.compute_all(
            self.unit_price, currency=self.currency_id, quantity=self.quantity, product=self.product_id,
        )

    @api.depends('quantity', 'unit_price', 'display_type', 'taxes_ids', 'currency_id')
    def _compute_subtotal(self):
        for line in self:
            if line.display_type:
                line.subtotal = 0.0
            else:
                line.subtotal = line._compute_taxes()['total_excluded']

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.unit_price = self.product_id.standard_price
            self.uom_id = self.product_id.uom_id

    def _check_budget_not_approved(self, budgets):
        # La carga de datos de modulos (install_mode) no pasa por el bloqueo
        if not self.env.context.get('install_mode') and budgets.filtered(lambda budget: budget.state == 'approved'):
            raise UserError('El presupuesto está aprobado y sus líneas no se pueden modificar. '
                            'Un administrador puede reabrirlo.')

    @api.model_create_multi
    def create(self, vals_list):
        self._check_budget_required(vals_list)
        budgets = self.env['retana.budget'].browse([vals['budget_id'] for vals in vals_list if vals.get('budget_id')])
        self._check_budget_not_approved(budgets)
        return super().create(vals_list)

    def write(self, vals):
        if 'budget_id' in vals:
            self._check_budget_required([vals])
        self._check_budget_not_approved(self.budget_id)
        return super().write(vals)

    def unlink(self):
        self._check_budget_not_approved(self.budget_id)
        return super().unlink()
