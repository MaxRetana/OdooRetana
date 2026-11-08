from odoo import models, fields, api
from odoo.exceptions import UserError

class RetanaBudgetLine(models.Model):
    _name = 'retana.budget.line'
    _description = 'Líneas de Presupuesto Retana'
    _order = 'sequence, id'
    
    sequence    =fields.Integer(string='Secuencia', default=10)
    budget_id   =fields.Many2one('retana.budget', string='Presupuesto')
    display_type =fields.Selection([
        ('line_section', 'Sección'),
        ('line_note', 'Nota')
    ], string='Tipo de línea', default=False)
    product_id  =fields.Many2one('product.product', string='Concepto')
    description =fields.Char(string='Descripción')
    quantity    =fields.Float(string='Cantidad', default=1.0)
    unit_price  =fields.Float(string='Precio Unitario')
    uom_id      =fields.Many2one('uom.uom', string='Unidad de Medida')
    taxes_ids   =fields.Many2many('account.tax', string='Impuestos')
    subtotal    =fields.Float(string='Subtotal', compute='_compute_subtotal')
    
    @api.depends('quantity', 'unit_price', 'display_type')
    def _compute_subtotal(self):
        for line in self:
            if line.display_type:
                line.subtotal = 0.0
            else:
                line.subtotal = line.quantity * line.unit_price
            
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
        budgets = self.env['retana.budget'].browse([vals['budget_id'] for vals in vals_list if vals.get('budget_id')])
        self._check_budget_not_approved(budgets)
        return super().create(vals_list)

    def write(self, vals):
        self._check_budget_not_approved(self.budget_id)
        return super().write(vals)

    def unlink(self):
        self._check_budget_not_approved(self.budget_id)
        return super().unlink()
