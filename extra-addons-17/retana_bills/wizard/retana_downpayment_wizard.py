from odoo import models, fields, api
from datetime import datetime, timedelta

class RetanaDownpaymentWizard(models.TransientModel):
    _name = 'retana.downpayment.wizard'
    _description = 'Anticipos de Presupuestos Retana'
    
    def _get_default_saturday(self):
        """Retorna el jueves de la semana en curso"""
        today = datetime.today()
        # weekday() retorna 0=Lunes, 3=Jueves
        days_until_thursday = (3 - today.weekday()) % 7
        thursday = today + timedelta(days=days_until_thursday)
        return thursday.date()
    
    name            =fields.Char(string='Nombre del Anticipo', default='Nuevo', tracking=True)
    concept_id     =fields.Many2one('retana.downpayment.type.concept', string='Concepto de Anticipo', tracking=True)
    building_id     =fields.Many2one('retana.buildings', string='Obra', domain="[('active', '=', True)]", tracking=True)
    client_id       =fields.Many2one('res.partner', string='Cliente', domain="[('is_retana_customer', '=', True)]", tracking=True)
    date            =fields.Date(string='Fecha del Anticipo', default=_get_default_saturday, tracking=True)
    amount          =fields.Monetary(string='Importe del Anticipo', currency_field='currency_id', tracking=True)
    currency_id     =fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id, tracking=True)
    
    def action_create_downpayment(self):
        """Crea el registro de anticipo y cierra el wizard"""
        self.ensure_one()
        
        # Crear el anticipo
        downpayment = self.env['retana.downpayment'].create({
            'name': self.name,
            'concept_id': self.concept_id.id,
            'building_id': self.building_id.id,
            'client_id': self.client_id.id,
            'date': self.date,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
        })
        
        # Retornar acción para abrir el registro creado
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'retana.downpayment',
            'res_id': downpayment.id,
            'view_mode': 'form',
            'target': 'current',
        }
    