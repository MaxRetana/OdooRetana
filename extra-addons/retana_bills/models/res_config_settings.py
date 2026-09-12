from odoo import fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    retana_green_api_id_instance = fields.Char(
        string='ID de Instancia',
        config_parameter='retana_bills.green_api_id_instance',
    )
    retana_green_api_token = fields.Char(
        string='Token de la Instancia',
        config_parameter='retana_bills.green_api_token',
    )
    retana_green_api_host = fields.Char(
        string='URL de la API',
        config_parameter='retana_bills.green_api_host',
    )
    retana_green_api_media_host = fields.Char(
        string='URL de Media (opcional)',
        config_parameter='retana_bills.green_api_media_host',
    )

    def action_retana_whatsapp_check_state(self):
        self.ensure_one()
        result = self.env['retana.whatsapp'].get_instance_state()
        state = result.get('stateInstance', 'desconocido')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Estado de WhatsApp (Green API)',
                'message': f'Estado de la instancia: {state}',
                'sticky': True,
                'type': 'success' if state == 'authorized' else 'warning',
            },
        }

    def action_retana_whatsapp_get_qr(self):
        self.ensure_one()
        result = self.env['retana.whatsapp'].get_qr_code()
        if result.get('type') == 'alreadyLogged':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'WhatsApp (Green API)',
                    'message': 'La instancia ya está vinculada a un WhatsApp.',
                    'sticky': False,
                    'type': 'success',
                },
            }
        qr_b64 = result.get('message')
        if not qr_b64:
            raise UserError(f'Green API no devolvió un código QR: {result}')
        qr_datas = qr_b64 if isinstance(qr_b64, str) else qr_b64.decode()
        attachment = self.env['ir.attachment'].create({
            'name': 'whatsapp_qr.png',
            'datas': qr_datas,
            'res_model': 'res.config.settings',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/image/{attachment.id}',
            'target': 'new',
        }
