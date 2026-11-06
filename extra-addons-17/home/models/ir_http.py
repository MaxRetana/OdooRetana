from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        """Usar el Home como pantalla de inicio de los usuarios internos.

        Solo aplica a quienes no tienen una "Acción de inicio" propia en sus preferencias
        (res.users.action_id), y se puede desactivar poniendo en False el parámetro
        del sistema 'home.use_as_landing'. No modifica ningún dato de usuario.
        """
        info = super().session_info()
        if info.get('is_internal_user') and not info.get('home_action_id'):
            use_as_landing = self.env['ir.config_parameter'].sudo().get_param('home.use_as_landing')
            if use_as_landing == 'True':
                action = self.env.ref('home.action_home_home_dashboard', raise_if_not_found=False)
                if action:
                    info['home_action_id'] = action.id
        return info
