from odoo import models, fields, api

class PersonalTask(models.Model):
    _name = 'personal.task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Tarea Personal'

    name = fields.Char(string='Nombre', required=True, tracking=True)
    description = fields.Text(string='Descripción', tracking=True)
    deadline = fields.Date(string='Fecha de Vencimiento', tracking=True)
    priority = fields.Selection([
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta')
    ], string='Prioridad', default='medium', tracking=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('todo', 'En Progreso'),
        ('done', 'Hecho'),
        ('cancel', 'Cancelado')
    ], string='Estado', default='draft', tracking=True)
    user_id = fields.Many2one('res.users', string='Responsable', tracking=True)
    important = fields.Boolean(string='Importante', default=False, tracking=True)

    def create(self, vals):
        # Lógica personalizada al crear una tarea
        vals['user_id'] = self.env.user.id
        return super(PersonalTask, self).create(vals)
    
    def todo_action(self):
        self.state = 'todo'
        
    def done_action(self):
        self.state = 'done'
        
    def cancel_action(self):
        self.state = 'cancel'
        
    def reset_to_draft(self):
        self.state = 'draft'
        
    def send_deadline_reminders(self):
        today = fields.Date.today()
        tasks = self.search([('deadline', '=', today), ('state', 'in', ['draft', 'todo'])])
        # Agrupar tareas por usuario
        tasks_by_user = {}
        for task in tasks:
            if task.user_id and task.user_id.partner_id:
                tasks_by_user.setdefault(task.user_id, []).append(task)
        # Enviar un correo por usuario con todas sus tareas
        template = self.env.ref('personal_task.email_template_deadline_reminder_grouped')
        for user, user_tasks in tasks_by_user.items():
            if template:
                # Construir la lista de tareas en HTML
                task_list_html = "<ul>"
                for t in user_tasks:
                    task_list_html += f"<li>{t.name} (Vence: {t.deadline})</li>"
                task_list_html += "</ul>"
                # Crear contexto para el template
                ctx = {
                    'task_list_html': task_list_html,
                    'user_name': user.name,
                }
                email_values = {
                    'email_to': user.email,
                    'email_from': self.env.user.email
                }
                # Corregir la llamada a send_mail
                template.with_context(ctx).send_mail(
                    user_tasks[0].id,  # res_id
                    force_send=True,
                    email_values=email_values
                )