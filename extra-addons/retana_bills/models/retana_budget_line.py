from odoo import models, fields, api

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
            self.unit_price = self.product_id.standard_priceuom_id