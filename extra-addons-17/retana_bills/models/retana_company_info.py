from odoo import models, fields, api

class RetanaCompanyInfo(models.Model):
    _name = 'retana.company.info'
    _description = 'Información de Empresa Retana'
    _rec_name = 'company_name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'field.tracking.mixin']
    
    company_name = fields.Char(string='Nombre de la Empresa', required=True, default='JOSE NATIVIDAD RETANA RODRIGUEZ')
    business_line = fields.Char(string='Giro Comercial', required=True, default='SERVICIOS ELECTRICOS Y MANTENIMIENTO')
    rfc = fields.Char(string='R.F.C.', required=True, default='RENR-720328-FE5')
    curp = fields.Char(string='C.U.R.P.', required=True, default='RERN720328HCMTDT02')
    address = fields.Char(string='Dirección', required=True, default='PRIV. MARGARITA MAZA DE JUAREZ #476')
    phone = fields.Char(string='Teléfono', required=True, default='31 4 05 23')
    mobile = fields.Char(string='Celular', required=True, default='044 312 31 9 31 05')
    zone = fields.Char(string='Zona', required=True, default='ZONA CENTRO')
    postal_code = fields.Char(string='Código Postal', required=True, default='28000')
    city = fields.Char(string='Ciudad', required=True, default='COLIMA')
    state = fields.Char(string='Estado', required=True, default='COL.')
    active = fields.Boolean(string='Activo', default=True)
    
    @api.model
    def get_company_info(self):
        """Retorna la información de la empresa activa"""
        company_info = self.search([('active', '=', True)], limit=1)
        if not company_info:
            # Crear registro por defecto si no existe
            company_info = self.create({})
        return company_info
