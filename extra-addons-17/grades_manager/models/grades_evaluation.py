from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GradesEvaluation(models.Model):
    _name = 'grades.evaluation'
    _description = 'Evaluation'

    name = fields.Char(string='Evaluation Name', required=True)
    date = fields.Date(string='Evaluation Date', required=True)
    observations = fields.Text(string='Observations')
    course_id = fields.Many2one('grades.course', string='Course', required=True)
    