from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Antes de los grupos Retana todos los usuarios internos tenian acceso total.
    Para que nadie pierda acceso al actualizar: los usuarios internos pasan a
    'Usuario' y los administradores del sistema a 'Administrador'."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    user_group = env.ref('retana_bills.group_retana_user')
    admin_group = env.ref('retana_bills.group_retana_admin')
    internal = env['res.users'].search([('share', '=', False)])
    user_group.write({'user_ids': [(4, user.id) for user in internal]})
    admins = internal.filtered(lambda user: user.has_group('base.group_system'))
    admin_group.write({'user_ids': [(4, user.id) for user in admins]})
