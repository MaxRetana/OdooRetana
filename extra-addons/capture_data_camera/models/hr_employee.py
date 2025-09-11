import base64
import tempfile
import os
import cv2
import numpy as np

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
            # Determinar si es ruta o base64
            if isinstance(file, str) and os.path.isfile(file):
                img = cv2.imread(file)
                _logger.info(f'Imagen abierta desde ruta: {file}')
            elif isinstance(file, bytes):
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
                    temp_img.write(file)
                    temp_img.flush()
                    img = cv2.imread(temp_img.name)
                    _logger.info('Imagen abierta desde base64')
            else:
                _logger.error('Archivo no encontrado o formato no soportado')
                return False

            # --------------------
            # 🔹 Preprocesamiento
            # --------------------
            # Preprocesamiento ligero
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Umbral simple
            _, processed_img = cv2.threshold(gray, 117, 255, cv2.THRESH_BINARY)

            # --------------------
            # 🔹 OCR con Tesseract
            # --------------------
            # OCR con mejor configuración
            custom_config = r'--oem 3 --psm 4'
            texto = pytesseract.image_to_string(processed_img, lang="spa", config=custom_config)
            _logger.info(f'Texto extraído: {texto}')

            # Regex para INE
            data = {}

            # Buscar la palabra NOMBRE y tomar solo las 3 siguientes líneas válidas
            lineas = texto.split('\n')
            nombre_lines = []
            start_idx = None
            for idx, linea in enumerate(lineas):
                # Busca "NOMBRE" en la línea, aunque esté acompañada de "SEXO"
                if "NOMBRE" in linea.upper():
                    start_idx = idx
                    break
            if start_idx is not None:
                # Si la línea contiene "SEXO", saltar esa palabra y tomar las siguientes líneas
                # Ejemplo: "NOMBRE sexo H"
                siguientes = []
                # Si la línea tiene más palabras después de "NOMBRE", ignorarlas
                for l in lineas[start_idx+1:start_idx+6]:  # Tomar hasta 5 líneas siguientes por si hay saltos vacíos
                    limpio = re.sub(r'[^A-ZÑÁÉÍÓÚ ]', '', l.upper()).strip()
                    if limpio and len(limpio.split()) <= 3 and not any(x in limpio for x in ["SEXO", "DOMICILIO", "CLAVE", "CURP", "FECHA", "AÑO", "SECCIÓN", "VIGENCIA"]):
                        siguientes.append(limpio)
                    if len(siguientes) == 3:
                        break
                if len(siguientes) == 3:
                    data['apellido_paterno'] = siguientes[0]
                    data['apellido_materno'] = siguientes[1]
                    data['nombres'] = siguientes[2]
                    data['nombre'] = f"{siguientes[0]} {siguientes[1]} {siguientes[2]}"
                    _logger.info(f"Nombre extraído: {data['nombre']}")
                else:
                    _logger.info("No se pudieron extraer las 3 líneas de nombre.")
            else:
                _logger.info("No se encontró la palabra NOMBRE, no se extrae nombre.")

            # Domicilio
            match_domicilio = re.search(r'DOMICILIO\s+([A-Z0-9\s\.\,]+(?:\n[A-Z0-9\s\.\,]+)+)', texto)
            if match_domicilio:
                data['domicilio'] = match_domicilio.group(1).replace("\n", " ").strip()

            # Sexo
            match_sexo = re.search(r'SEXO\s+([HM])', texto)
            if match_sexo:
                data['sexo'] = match_sexo.group(1)

            # Clave de elector
            match_clave = re.search(r'CLAVE DE ELECTOR\s+([A-Z0-9]{18})', texto)
            if match_clave:
                data['clave_elector'] = match_clave.group(1)

            # CURP
            match_curp = re.search(r'CURP\s+([A-Z0-9]{18})', texto)
            if match_curp:
                data['curp'] = match_curp.group(1)

            # Fecha de nacimiento
            match_fecha = re.search(r'FECHA DE NACIMIENTO\s+(\d{2}/\d{2}/\d{4})', texto)
            if match_fecha:
                data['fecha_nacimiento'] = match_fecha.group(1)

            # Año de registro
            match_registro = re.search(r'AÑO DE REGISTRO\s+(\d{4})', texto)
            if match_registro:
                data['anio_registro'] = match_registro.group(1)

            # Sección
            match_seccion = re.search(r'SECCIÓN\s+(\d{4})', texto)
            if match_seccion:
                data['seccion'] = match_seccion.group(1)

            # Vigencia
            match_vigencia = re.search(r'VIGENCIA\s+(\d{4}\s*-\s*\d{4})', texto)
            if match_vigencia:
                data['vigencia'] = match_vigencia.group(1)
            _logger.info(f"Datos extraídos: {data}")
            # --------------------
            # Retornar datos estructurados
            # --------------------
            return data if data else False

        except Exception as e:
            _logger.error(f'Error procesando la imagen: {e}', exc_info=True)
            return False

    @api.model
    def get_employee_data(self):
        file = self.image or self.document_file
        if file:
            data = self._get_data_employee(file)
            _logger.info(f'Datos obtenidos: {data}')
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
            image_data = base64.b64decode(file)
            _logger.info('Imagen decodificada correctamente')

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
                temp_img.write(image_data)
                temp_img.flush()
                temp_img_path = temp_img.name

            result = self._get_data_employee(temp_img_path)

            if result:
                return result
            else:
                _logger.error('No se pudo procesar la imagen en _get_data_employee')
                return False
        except Exception as e:
            _logger.error(f'Error en upload_image_temp: {e}', exc_info=True)
            return False
