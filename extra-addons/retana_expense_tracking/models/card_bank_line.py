from odoo import models, fields, api

class CardBankLine(models.Model):
    _name = 'card.bank.line'
    _description = 'Movimientos de Tarjeta Bancaria'

    name = fields.Char(string='Referencia', default='Nuevo')
    description = fields.Text(string='Detalles del Movimiento')
    date = fields.Date(string='Fecha del Movimiento')
    amount = fields.Float(string='Monto del Movimiento')
    place = fields.Char(string='Establecimiento')
    card_bank_id = fields.Many2one('card.bank', string='Tarjeta Bancaria')
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'Nuevo':
                # Buscar si existe la secuencia, si no existe la crea
                sequence = self.env['ir.sequence'].search([('code', '=', 'card.bank.line')], limit=1)
                if not sequence:
                    sequence = self.env['ir.sequence'].create({
                        'name': 'Card Bank Line Sequence',
                        'code': 'card.bank.line',
                        'prefix': 'CBL',
                        'padding': 4,
                        'number_next': 1,
                        'number_increment': 1,
                    })
                
                # Generar el siguiente número
                next_number = self.env['ir.sequence'].next_by_code('card.bank.line') or '0001'
                vals['name'] = f"{next_number}"
        return super().create(vals_list)