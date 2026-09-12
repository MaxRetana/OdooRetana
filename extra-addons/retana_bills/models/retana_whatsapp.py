import requests

from odoo import api, fields, models
from odoo.exceptions import UserError


class RetanaWhatsapp(models.Model):
    _name = 'retana.whatsapp'
    _description = 'Números de WhatsApp de Clientes Retana'
    _rec_name = 'number'

    partner_id = fields.Many2one(
        'res.partner', string='Cliente', required=True, ondelete='cascade',
        domain=[('send_whatsapp', '=', True)],
    )
    number = fields.Char(
        string='Número de WhatsApp',
        required=True,
        help="Incluye código de país sin '+' ni espacios. Ejemplo: 521XXXXXXXXXX",
    )
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('partner_number_uniq', 'unique(partner_id, number)',
         'Este cliente ya tiene registrado ese número de WhatsApp.'),
    ]

    def name_get(self):
        return [(rec.id, f"{rec.partner_id.name}\n{rec.number}") for rec in self]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = list(args or [])
        domain = args
        if name:
            domain = args + ['|', ('partner_id.name', operator, name), ('number', operator, name)]
        records = self.search(domain, limit=limit)
        return records.name_get()

    @api.model
    def _get_green_api_config(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        id_instance = get_param('retana_bills.green_api_id_instance')
        api_token = get_param('retana_bills.green_api_token')
        api_host = get_param('retana_bills.green_api_host') or 'https://api.green-api.com'
        media_host = get_param('retana_bills.green_api_media_host') or api_host
        if not id_instance or not api_token:
            raise UserError(
                'Falta configurar la cuenta de WhatsApp (Green API). '
                'Ve a Ajustes > Ajustes Generales > Retana WhatsApp y completa '
                'el ID de instancia y el token.'
            )
        return {
            'id_instance': id_instance,
            'api_token': api_token,
            'api_host': api_host.rstrip('/'),
            'media_host': media_host.rstrip('/'),
        }

    @api.model
    def _format_chat_id(self, number):
        digits = ''.join(ch for ch in (number or '') if ch.isdigit())
        if not digits:
            raise UserError('El número de WhatsApp no es válido.')
        if len(digits) == 10:
            # Número local mexicano sin código de país: se asume Retana (México, 52).
            digits = f'52{digits}'
        return f'{digits}@c.us'

    @api.model
    def get_instance_state(self):
        """Consulta el estado de la instancia de Green API (autorizada, esperando QR, etc.)."""
        config = self._get_green_api_config()
        url = f"{config['api_host']}/waInstance{config['id_instance']}/getStateInstance/{config['api_token']}"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise UserError(f'No se pudo conectar con Green API: {exc}') from exc
        return response.json()

    @api.model
    def get_qr_code(self):
        """Obtiene el código QR (base64) para vincular el WhatsApp a la instancia."""
        config = self._get_green_api_config()
        url = f"{config['api_host']}/waInstance{config['id_instance']}/qr/{config['api_token']}"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise UserError(f'No se pudo conectar con Green API: {exc}') from exc
        return response.json()

    @api.model
    def send_pdf_document(self, number, pdf_content, filename, caption=None):
        """Envía un PDF por WhatsApp usando Green API. Devuelve la respuesta JSON de la API."""
        config = self._get_green_api_config()
        chat_id = self._format_chat_id(number)
        url = f"{config['media_host']}/waInstance{config['id_instance']}/sendFileByUpload/{config['api_token']}"
        files = {'file': (filename, pdf_content, 'application/pdf')}
        data = {'chatId': chat_id}
        if caption:
            data['caption'] = caption
        try:
            response = requests.post(url, data=data, files=files, timeout=60)
        except requests.RequestException as exc:
            raise UserError(f'No se pudo enviar el WhatsApp: {exc}') from exc
        if response.status_code >= 400:
            raise UserError(f'Green API respondió con error ({response.status_code}): {response.text}')
        result = response.json()
        if not result.get('idMessage'):
            raise UserError(f'Green API no confirmó el envío: {result}')
        return result
