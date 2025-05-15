from odoo import models, fields, api, _

class RestPartner(models.Model):
    _inherit = 'res.partner'

    # Adding a new field to the res.partner model
    is_teacher = fields.Boolean(string='Is Teacher', default=False)
    is_student = fields.Boolean(string='Is Student', default=False)