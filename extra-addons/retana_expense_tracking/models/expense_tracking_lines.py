from odoo import models, fields, api

class ExpenseTrackingLines(models.Model):
    _name = 'expense.tracking.lines'
    _description = 'Lineas de Control de Gastos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    expense_tracking_id = fields.Many2one('expense.tracking', string='Control de Gastos', tracking=True)
    name = fields.Char(string='Identificador', default="Nuevo", tracking=True)
    amount = fields.Float(string='Monto', tracking=True)
    date = fields.Date(string='Fecha', tracking=True)
    category_id = fields.Many2one('expense.tracking.category', string='Categoría', tracking=True)
    type_id = fields.Many2one('expense.tracking.type', string='Tipo', tracking=True)
    description = fields.Text(string='Descripción', tracking=True)
    card_id = fields.Many2one('card.bank', string='Tarjeta Bancaria', tracking=True)
    is_recurring = fields.Boolean(string='¿Recurrente?', tracking=True)
    card_line_id = fields.Many2one('card.bank.line', string='Movimiento de Tarjeta', readonly=True, copy=False)
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'Nuevo':
                # Buscar si existe la secuencia, si no existe la crea
                sequence = self.env['ir.sequence'].search([('code', '=', 'expense.tracking.lines')], limit=1)
                if not sequence:
                    sequence = self.env['ir.sequence'].create({
                        'name': 'Expense Tracking Lines Sequence',
                        'code': 'expense.tracking.lines',
                        'prefix': 'ETL',
                        'padding': 4,
                        'number_next': 1,
                        'number_increment': 1,
                    })
                
                # Generar el siguiente número
                next_number = self.env['ir.sequence'].next_by_code('expense.tracking.lines') or '0001'
                vals['name'] = f"{next_number}"
        
        # Crear los registros
        records = super().create(vals_list)
        
        # Crear movimiento en tarjeta si se seleccionó una tarjeta
        for record in records:
            if record.card_id:
                record._create_card_movement()
        
        return records
    
    def write(self, vals):
        # Guardar tarjetas anteriores para detectar cambios
        old_cards = {rec.id: rec.card_id for rec in self}
        
        # Actualizar el registro
        result = super().write(vals)
        
        for record in self:
            old_card = old_cards.get(record.id)
            
            # Si se cambió la tarjeta
            if 'card_id' in vals and old_card != record.card_id:
                # Si existe movimiento y hay nueva tarjeta, solo cambiar el ID de la tarjeta
                if record.card_line_id and record.card_id:
                    record.card_line_id.write({'card_bank_id': record.card_id.id})
                # Si existe movimiento pero se quitó la tarjeta, eliminar el movimiento
                elif record.card_line_id and not record.card_id:
                    record.card_line_id.unlink()
                    record.card_line_id = False
                # Si no existe movimiento pero se agregó una tarjeta, crear nuevo
                elif not record.card_line_id and record.card_id:
                    record._create_card_movement()
            
            # Si se actualizaron otros campos y hay tarjeta asociada
            elif record.card_id and record.card_line_id:
                record._update_card_movement(vals)
        
        return result
    
    def unlink(self):
        # Eliminar movimientos de tarjeta asociados
        card_lines = self.mapped('card_line_id').filtered(lambda x: x)
        result = super().unlink()
        if card_lines:
            card_lines.unlink()
        return result
    
    def _create_card_movement(self):
        """Crea un movimiento en la tarjeta bancaria"""
        self.ensure_one()
        if not self.card_id:
            return
        
        card_line = self.env['card.bank.line'].create({
            'card_bank_id': self.card_id.id,
            'description': self.description or self.name,
            'date': self.date,
            'amount': self.amount,
            'place': self.category_id.name if self.category_id else '',
        })
        self.card_line_id = card_line.id
    
    def _update_card_movement(self, vals):
        """Actualiza el movimiento existente en la tarjeta bancaria"""
        self.ensure_one()
        if not self.card_line_id:
            return
        
        # Preparar valores a actualizar en el movimiento
        card_vals = {}
        if 'description' in vals:
            card_vals['description'] = vals['description'] or self.name
        if 'date' in vals:
            card_vals['date'] = vals['date']
        if 'amount' in vals:
            card_vals['amount'] = vals['amount']
        if 'category_id' in vals:
            category = self.env['expense.tracking.category'].browse(vals['category_id']) if vals['category_id'] else False
            card_vals['place'] = category.name if category else ''
        
        if card_vals:
            self.card_line_id.write(card_vals)