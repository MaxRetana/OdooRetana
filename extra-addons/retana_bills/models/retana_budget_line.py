from odoo import models, fields, api

class RetanaBudgetLine(models.Model):
    _name = 'retana.budget.line'
    _description = 'Líneas de Presupuesto Retana'
    
    budget_id   =fields.Many2one('retana.budget', string='Presupuesto', tracking=True)
    product_id  =fields.Many2one('product.product', string='Concepto', tracking=True)
    description =fields.Char(string='Descripción', tracking=True)
    quantity    =fields.Float(string='Cantidad', default=1.0, tracking=True)
    unit_price  =fields.Float(string='Precio Unitario', tracking=True)
    taxes_ids   =fields.Many2many('account.tax', string='Impuestos', tracking=True)
    subtotal    =fields.Float(string='Subtotal', compute='_compute_subtotal')
    
    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
            
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.unit_price = self.product_id.lst_price
            self.taxes_ids = self.product_id.taxes_id