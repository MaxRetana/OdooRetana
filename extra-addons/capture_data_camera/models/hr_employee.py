import base64
import tempfile
import os

from odoo import models, api
from PIL import Image
import pytesseract
import re

import logging
_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    
    def _get_data_employee(self, file):
        try:
            # Si es una ruta, verifica que exista
            if isinstance(file, str) and os.path.isfile(file):
                img = Image.open(file)
                _logger.info(f'Imagen abierta desde ruta: {file}')
            # Si es base64, decodifica y guarda temporalmente
            elif isinstance(file, bytes):
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
                    temp_img.write(file)
                    temp_img.flush()
                    img = Image.open(temp_img.name)
                    _logger.info('Imagen abierta desde base64')
            else:
                _logger.error('Archivo no encontrado o formato no soportado')
                return False

            # Extrae texto con OCR
            texto = pytesseract.image_to_string(img, lang='spa')
            _logger.info(f'Texto extraído: {texto}')
            match = re.search(r'NOMBRE\s*[:\-]?\s*(.+)', texto)
            if match:
                nombre = match.group(1).split('\n')[0].strip()
                _logger.info(f'Nombre detectado: {nombre}')
            else:
                _logger.info('No se detectó el nombre')
            return True
        except Exception as e:
            _logger.error(f'Error procesando la imagen: {e}', exc_info=True)
            return False

    @api.model
    def get_employee_data(self):
        # Este método debe ser compatible con el botón de acción
        # Aquí podrías poner lógica para obtener el archivo desde algún campo del modelo
        # Por ejemplo, si tienes un campo 'image' o 'document_file'
        file = self.image or self.document_file
        if file:
            self._get_data_employee(file)
        # Opcionalmente, mostrar un mensaje al usuario
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Acción ejecutada',
                'message': 'La extracción de datos se ha iniciado.',
                'type': 'success',
                'sticky': False,
            }
        }
    
    @api.model
    def upload_image_temp(self, file):
        """
        Recibe una imagen en base64, la guarda temporalmente y la procesa.
        """
        try:
            # Decodificar base64
            image_data = base64.b64decode(file)
            _logger.info('Imagen decodificada correctamente')
            # Guardar imagen temporalmente
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
                temp_img.write(image_data)
                temp_img.flush()
                temp_img_path = temp_img.name

            # Procesar la imagen (puedes llamar aquí tu lógica OCR)
            result = self._get_data_employee(temp_img_path)

            if result:
                return True
            else:
                _logger.error('No se pudo procesar la imagen en _get_data_employee')
                return False
        except Exception as e:
            _logger.error(f'Error en upload_image_temp: {e}', exc_info=True)
            return False
