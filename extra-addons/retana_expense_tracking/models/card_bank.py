from odoo import models, fields, api

class CardBank(models.Model):
    _name = 'card.bank'
    _description = 'Tarjeta Bancaria'

    name = fields.Char(string='Referencia', default='Nuevo')
    card_name = fields.Char(string='Nombre de la Tarjeta')
    bank_name = fields.Char(string='Nombre del Banco')
    card_number = fields.Char(string='Número de Tarjeta')
    expiration_date = fields.Date(string='Fecha de Expiración')
    limit_amount = fields.Float(string='Límite de Crédito')
    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)
    card_line_ids = fields.One2many('card.bank.line', 'card_bank_id', string='Movimientos de la Tarjeta')
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'Nuevo':
                # Buscar si existe la secuencia, si no existe la crea
                sequence = self.env['ir.sequence'].search([('code', '=', 'card.bank')], limit=1)
                if not sequence:
                    sequence = self.env['ir.sequence'].create({
                        'name': 'Card Bank Sequence',
                        'code': 'card.bank',
                        'prefix': 'CB',
                        'padding': 4,
                        'number_next': 1,
                        'number_increment': 1,
                    })
                
                # Generar el siguiente número
                next_number = self.env['ir.sequence'].next_by_code('card.bank') or '0001'
                vals['name'] = f"{next_number}"
        return super().create(vals_list)