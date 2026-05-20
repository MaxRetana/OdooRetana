from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import re
import unicodedata


class RetanaBulkDownpaymentWizard(models.TransientModel):
    _name = 'retana.bulk.downpayment.wizard'
    _description = 'Wizard para crear múltiples anticipos desde mensaje de texto'

    def _get_default_saturday(self):
        """Retorna el jueves de la semana en curso"""
        today = datetime.today()
        # weekday() retorna 0=Lunes, 3=Jueves
        days_until_thursday = (3 - today.weekday()) % 7
        thursday = today + timedelta(days=days_until_thursday)
        return thursday.date()

    message_text = fields.Text(
        string='Mensaje',
        required=True,
        help='Pega el mensaje con los anticipos. Formato: $monto nombre_obra o $monto nombre_obra, concepto'
    )
    found_lines_text = fields.Text(
        string='Lineas Con Obra Encontrada',
        readonly=True,
        help='Muestra las lineas del mensaje cuya obra fue encontrada en el sistema.'
    )
    not_found_lines_text = fields.Text(
        string='Lineas Sin Obra Encontrada',
        readonly=True,
        help='Muestra las lineas del mensaje cuya obra no fue encontrada en el sistema.'
    )
    date = fields.Date(
        string='Fecha del Anticipo',
        required=True,
        default=_get_default_saturday
    )
    client_id = fields.Many2one(
        'res.partner',
        string='Cliente por Defecto',
        domain="[('is_retana_customer', '=', True)]",
        help='Cliente a usar cuando la obra no tenga cliente asignado'
    )

    def _parse_line(self, line):
        """
        Parsea una línea del mensaje para extraer monto, obra y concepto.
        Formato esperado: $monto nombre_obra o $monto nombre_obra, concepto
        
        Returns:
            dict con 'amount', 'building_name' y 'concept_name' (opcional)
        """
        # Limpiar la línea
        line = line.strip()
        if not line:
            return None
        
        # Regex para detectar el monto al inicio: $número o número sin $
        amount_match = re.match(r'^\$?\s*(\d+(?:[.,]\d+)?)', line)
        if not amount_match:
            return None
        
        amount = float(amount_match.group(1).replace(',', '.'))
        
        # Obtener el resto después del monto
        rest = line[amount_match.end():].strip()
        
        # Verificar si hay concepto (separado por coma)
        if ',' in rest:
            parts = rest.split(',', 1)
            building_name = parts[0].strip()
            concept_name = parts[1].strip()
        else:
            building_name = rest
            concept_name = None
        
        return {
            'amount': amount,
            'building_name': building_name,
            'concept_name': concept_name
        }

    def _find_or_create_building(self, building_name, default_client_id=None):
        """
        Busca una obra por nombre, primero exacta y luego con coincidencia flexible.
        Si no existe, retorna False y NO la crea automáticamente.
        """
        building, _match_type = self._find_building_with_match_info(building_name)
        return building

    def _find_building_with_match_info(self, building_name):
        """Retorna (obra, tipo_match): exact, fuzzy o none."""
        Building = self.env['retana.buildings']

        if not building_name:
            return False, 'none'
        
        # Buscar la obra con nombre exacto (solo ignorando mayúsculas/minúsculas)
        building = Building.search([
            ('name', '=ilike', building_name)
        ], limit=1)

        if building:
            return building, 'exact'

        # Si no hubo coincidencia exacta, aplicar coincidencia flexible.
        normalized_input = self._normalize_text(building_name)
        compact_input = normalized_input.replace(' ', '')
        if not normalized_input:
            return False, 'none'

        best_building = False
        best_score = 0.0
        input_tokens = set(normalized_input.split())

        for candidate in Building.search([]):
            normalized_candidate = self._normalize_text(candidate.name)
            if not normalized_candidate:
                continue

            compact_candidate = normalized_candidate.replace(' ', '')
            score = 0.0

            if normalized_candidate == normalized_input:
                score = 100.0
            elif compact_candidate == compact_input:
                score = 95.0
            elif compact_candidate and compact_candidate in compact_input:
                score = 85.0 + min(len(compact_candidate), 100) / 100.0
            elif compact_input and compact_input in compact_candidate:
                score = 78.0 + min(len(compact_input), 100) / 100.0
            else:
                candidate_tokens = set(normalized_candidate.split())
                common_tokens = input_tokens.intersection(candidate_tokens)
                if common_tokens:
                    precision = len(common_tokens) / max(len(candidate_tokens), 1)
                    recall = len(common_tokens) / max(len(input_tokens), 1)
                    score = (precision * 55.0) + (recall * 35.0)

            if score > best_score:
                best_score = score
                best_building = candidate

        if best_building and best_score >= 80.0:
            return best_building, 'fuzzy'
        return False, 'none'

    def _normalize_text(self, text):
        """Normaliza texto: minusculas, sin tildes y sin simbolos especiales."""
        if not text:
            return ''

        normalized = unicodedata.normalize('NFKD', text)
        normalized = ''.join(ch for ch in normalized if not unicodedata.combining(ch))
        normalized = normalized.lower()
        normalized = re.sub(r'[^a-z0-9\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def _strip_line_marker(self, line):
        """Quita marcadores de revision (*, ?) al final de la linea."""
        if not line:
            return line
        return re.sub(r'\s*[\*\?]+\s*$', '', line)

    def _mark_line_for_review(self, line):
        """Agrega marcador de revision (*) al final de la linea, sin duplicarlo."""
        clean_line = self._strip_line_marker(line).rstrip()
        return f'{clean_line} *' if clean_line else clean_line

    def _mark_line_as_similar(self, line):
        """Agrega marcador de coincidencia aproximada (?) al final de la linea."""
        clean_line = self._strip_line_marker(line).rstrip()
        return f'{clean_line} ?' if clean_line else clean_line

    def _get_default_concept(self):
        """Obtiene el concepto marcado como predeterminado."""
        Concept = self.env['retana.downpayment.type.concept']
        default_concept = Concept.search([
            ('default_concept', '=', True),
            ('active', '=', True)
        ], limit=1)
        
        if not default_concept:
            raise UserError(
                'No hay un concepto predeterminado configurado. '
                'Por favor, marca un concepto como "Concepto Predeterminado" en la configuración.'
            )
        
        return default_concept

    def _find_concept(self, concept_name):
        """Busca un concepto por nombre (case insensitive)."""
        if not concept_name:
            return None
        
        Concept = self.env['retana.downpayment.type.concept']
        return Concept.search([
            ('name', '=ilike', concept_name),
            ('active', '=', True)
        ], limit=1)

    @api.onchange('message_text')
    def _onchange_message_text_split_buildings(self):
        """Separa lineas por obra encontrada y marca con * las que requieren correccion."""
        for wizard in self:
            if not wizard.message_text:
                wizard.found_lines_text = False
                wizard.not_found_lines_text = False
                continue

            found_lines = []
            not_found_lines = []
            found_client_ids = set()
            updated_lines = []

            for raw_line in wizard.message_text.split('\n'):
                original_line = raw_line.rstrip()
                line = wizard._strip_line_marker(raw_line).strip()
                if not line:
                    updated_lines.append('')
                    continue

                parsed = wizard._parse_line(line)
                if not parsed or not parsed.get('building_name'):
                    marked_line = wizard._mark_line_for_review(original_line)
                    not_found_lines.append(marked_line)
                    updated_lines.append(marked_line)
                    continue

                building, match_type = wizard._find_building_with_match_info(parsed['building_name'])
                if building:
                    if match_type == 'fuzzy':
                        marked_line = wizard._mark_line_as_similar(original_line)
                        found_lines.append(marked_line)
                        updated_lines.append(marked_line)
                    else:
                        found_lines.append(line)
                        updated_lines.append(line)
                    if building.client_id:
                        found_client_ids.add(building.client_id.id)
                else:
                    marked_line = wizard._mark_line_for_review(original_line)
                    not_found_lines.append(marked_line)
                    updated_lines.append(marked_line)

            updated_message = '\n'.join(updated_lines)
            if wizard.message_text != updated_message:
                wizard.message_text = updated_message

            wizard.found_lines_text = '\n'.join(found_lines) if found_lines else False
            wizard.not_found_lines_text = '\n'.join(not_found_lines) if not_found_lines else False

            if len(found_client_ids) == 1:
                wizard.client_id = next(iter(found_client_ids))
            elif len(found_client_ids) > 1 and wizard.client_id and wizard.client_id.id not in found_client_ids:
                return {
                    'warning': {
                        'title': 'Clientes Distintos Detectados',
                        'message': (
                            'Las obras encontradas pertenecen a diferentes clientes. '
                            'Selecciona manualmente el cliente por defecto que deseas usar '
                            'para las obras sin cliente.'
                        ),
                    }
                }

    def action_create_downpayments(self):
        """Procesa el mensaje y crea múltiples anticipos."""
        self.ensure_one()
        
        lines = self.message_text.split('\n')
        downpayment_vals_list = []
        errors = []
        default_concept = None
        
        for line_num, line in enumerate(lines, 1):
            parsed = self._parse_line(line)
            
            # Saltar líneas vacías o que no pudieron parsearse
            if not parsed:
                continue
            
            try:
                # Buscar la obra (NO crear si no existe)
                building = self._find_or_create_building(
                    parsed['building_name'],
                    self.client_id.id if self.client_id else None
                )
                
                # Si la obra no existe, saltar esta línea con advertencia
                if not building:
                    errors.append(
                        f"Línea {line_num}: Obra '{parsed['building_name']}' no encontrada. "
                        f"Esta línea se omitirá."
                    )
                    continue
                
                # Determinar el concepto
                concept = None
                if parsed['concept_name']:
                    concept = self._find_concept(parsed['concept_name'])
                    if not concept:
                        errors.append(
                            f"Línea {line_num} (Obra: {parsed['building_name']}): "
                            f"Concepto '{parsed['concept_name']}' no encontrado. "
                            f"Se usará el concepto predeterminado."
                        )
                
                # Si no se encontró concepto, usar el predeterminado
                if not concept:
                    if not default_concept:
                        default_concept = self._get_default_concept()
                    concept = default_concept
                
                # Preparar valores para crear el anticipo
                vals = {
                    'building_id': building.id,
                    'client_id': building.client_id.id if building.client_id else (self.client_id.id if self.client_id else False),
                    'concept_id': concept.id,
                    'amount': parsed['amount'],
                    'date': self.date,
                }
                
                downpayment_vals_list.append(vals)
                
            except Exception as e:
                errors.append(f"Línea {line_num}: Error procesando '{line}': {str(e)}")
        
        if not downpayment_vals_list:
            raise UserError(
                'No se pudo procesar ningún anticipo del mensaje.\n'
                'Verifica que el formato sea correcto: $monto nombre_obra'
            )
        
        # Crear todos los anticipos
        Downpayment = self.env['retana.downpayment']
        created_downpayments = Downpayment.create(downpayment_vals_list)
        
        # Preparar mensaje
        message = f'✅ Se crearon {len(created_downpayments)} anticipo(s) correctamente.'
        notification_type = 'success'
        
        if errors:
            message += '\n\n⚠️ Advertencias:\n' + '\n'.join(errors)
            notification_type = 'warning'
        
        # Mostrar notificación
        self.env['bus.bus']._sendone(
            self.env.user.partner_id,
            'simple_notification',
            {
                'title': '✅ Anticipos Creados' if not errors else '⚠️ Anticipos Creados con Advertencias',
                'message': message,
                'type': notification_type,
                'sticky': True,
            }
        )
        
        # Abrir vista de los anticipos creados
        return {
            'type': 'ir.actions.act_window',
            'name': 'Anticipos Creados',
            'res_model': 'retana.downpayment',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('retana_bills.view_retana_downpayment_tree').id, 'tree'), 
                      (self.env.ref('retana_bills.view_retana_downpayment_form').id, 'form')],
            'domain': [('id', 'in', created_downpayments.ids)],
            'target': 'current',
        }
