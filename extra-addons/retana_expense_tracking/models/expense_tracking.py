from odoo import models, fields, api

class ExpenseTracking(models.Model):
    _name = 'expense.tracking'
    _description = 'Control de Gastos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre del Control de Gastos', default="Nuevo", tracking=True)
    user_id = fields.Many2one('res.users', string='Usuario', tracking=True)
    month = fields.Selection([
        ('1', 'Enero'),
        ('2', 'Febrero'),
        ('3', 'Marzo'),
        ('4', 'Abril'),
        ('5', 'Mayo'),
        ('6', 'Junio'),
        ('7', 'Julio'),
        ('8', 'Agosto'),
        ('9', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre')
    ], string='Mes', tracking=True)
    year = fields.Integer(string='Año', tracking=True)
    line_ids = fields.One2many('expense.tracking.lines', 'expense_tracking_id', string='Líneas de Gastos')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'Nuevo':
                # Buscar si existe la secuencia, si no existe la crea
                sequence = self.env['ir.sequence'].search([('code', '=', 'expense.tracking')], limit=1)
                if not sequence:
                    sequence = self.env['ir.sequence'].create({
                        'name': 'Expense Tracking Sequence',
                        'code': 'expense.tracking',
                        'prefix': 'ET',
                        'padding': 4,
                        'number_next': 1,
                        'number_increment': 1,
                    })
                
                # Generar el siguiente número
                next_number = self.env['ir.sequence'].next_by_code('expense.tracking') or '0001'
                vals['name'] = f"{next_number}"
        return super().create(vals_list)