from odoo import models, fields, api, _

class GradesCourse(models.Model):
    _name = 'grades.course'
    _description = 'Course'

    name = fields.Char(string='Course Name')
    student_qty = fields.Integer(string='Number of Students')
    grades_average = fields.Float(string='Average Grade')
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active')
    course_started = fields.Date(string='Course Start Date', default=fields.Date.today)
    course_end = fields.Date(string='Course End Date')
    last_evaluation_date = fields.Datetime(string='Last Evaluation Date')
    course_image = fields.Binary(string='Course Image')
    course_shift = fields.Selection([
        ('day', 'Day'),
        ('night', 'Night'),
    ], string='Course Shift')
    teacher_id = fields.Many2one('res.partner', string='Teacher', domain=[('is_teacher', '=', True)])
    evaluation_ids = fields.One2many('grades.evaluation', 'course_id', string='Evaluations')
    students_ids = fields.Many2many('res.partner', 'grades_course_studens_rel', string='Students', domain=[('is_student', '=', True)])
    state = fields.Selection([
        ('register', 'Register'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished')], string="State", default='register')
