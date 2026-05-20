from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RetanaDownpaymentTypeConcept(models.Model):
    _name = 'retana.downpayment.type.concept'
    _description = 'Concepto de Tipo de Anticipo Retana'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name        =fields.Char(string='Concepto de Anticipo' , tracking=True)
    default_concept =fields.Boolean(string='Concepto Predeterminado', default=False, tracking=True)
    active      =fields.Boolean(string='Activo', default=True, tracking=True)
    
    @api.constrains('default_concept')
    def _check_single_default(self):
        """Asegura que solo haya un concepto marcado como predeterminado."""
        for record in self:
            if record.default_concept:
                other_defaults = self.search([
                    ('default_concept', '=', True),
                    ('id', '!=', record.id),
                    ('active', '=', True)
                ])
                if other_defaults:
                    raise ValidationError(
                        'Solo puede haber un concepto marcado como predeterminado. '
                        f'El concepto "{other_defaults[0].name}" ya está marcado como predeterminado.'
                    )
