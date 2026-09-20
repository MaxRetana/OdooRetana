from odoo import models
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import re
import unicodedata


class RetanaBulkDownpaymentMixin(models.AbstractModel):
    _name = 'retana.bulk.downpayment.mixin'
    _description = 'Logica compartida para crear multiples anticipos desde un mensaje de texto'

    def get_default_downpayment_date(self):
        """Retorna el jueves de la semana en curso"""
        today = datetime.today()
        # weekday() retorna 0=Lunes, 3=Jueves
        days_until_thursday = (3 - today.weekday()) % 7
        thursday = today + timedelta(days=days_until_thursday)
        return thursday.date()

    def _parse_line(self, line):
        """
        Parsea una línea del mensaje para extraer monto, obra y concepto.
        Formato esperado: $monto nombre_obra o $monto nombre_obra, concepto

        Returns:
            dict con 'amount', 'building_name' y 'concept_name' (opcional)
        """
        line = line.strip()
        if not line:
            return None

        amount_match = re.match(r'^\$?\s*(\d+(?:[.,]\d+)?)', line)
        if not amount_match:
            return None

        amount = float(amount_match.group(1).replace(',', '.'))
        rest = line[amount_match.end():].strip()

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
            'concept_name': concept_name,
        }

    def _find_building_with_match_info(self, building_name):
        """Retorna (obra, tipo_match): exact, fuzzy o none."""
        Building = self.env['retana.buildings']

        if not building_name:
            return False, 'none'

        building = Building.search([
            ('name', '=ilike', building_name)
        ], limit=1)

        if building:
            return building, 'exact'

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

    def analyze_bulk_message(self, message_text):
        """
        Analiza el mensaje linea por linea: separa las lineas cuya obra fue
        encontrada de las que no, y anota el mensaje con marcadores de revision.

        Returns:
            dict con 'updated_message', 'found_lines_text', 'not_found_lines_text',
            'found_client_ids' (lista de ids de cliente de las obras encontradas),
            'suggested_client_id' (cuando todas las obras comparten un solo cliente)
            y 'client_conflict' (True si hay mas de un cliente entre las obras encontradas).
        """
        result = {
            'updated_message': message_text or '',
            'found_lines_text': False,
            'not_found_lines_text': False,
            'found_client_ids': [],
            'suggested_client_id': False,
            'client_conflict': False,
        }

        if not message_text:
            return result

        found_lines = []
        not_found_lines = []
        found_client_ids = set()
        updated_lines = []

        for raw_line in message_text.split('\n'):
            original_line = raw_line.rstrip()
            line = self._strip_line_marker(raw_line).strip()
            if not line:
                updated_lines.append('')
                continue

            parsed = self._parse_line(line)
            if not parsed or not parsed.get('building_name'):
                marked_line = self._mark_line_for_review(original_line)
                not_found_lines.append(marked_line)
                updated_lines.append(marked_line)
                continue

            building, match_type = self._find_building_with_match_info(parsed['building_name'])
            if building:
                if match_type == 'fuzzy':
                    marked_line = self._mark_line_as_similar(original_line)
                    found_lines.append(marked_line)
                    updated_lines.append(marked_line)
                else:
                    found_lines.append(line)
                    updated_lines.append(line)
                if building.client_id:
                    found_client_ids.add(building.client_id.id)
            else:
                marked_line = self._mark_line_for_review(original_line)
                not_found_lines.append(marked_line)
                updated_lines.append(marked_line)

        result['updated_message'] = '\n'.join(updated_lines)
        result['found_lines_text'] = '\n'.join(found_lines) if found_lines else False
        result['not_found_lines_text'] = '\n'.join(not_found_lines) if not_found_lines else False
        result['found_client_ids'] = list(found_client_ids)

        if len(found_client_ids) == 1:
            result['suggested_client_id'] = next(iter(found_client_ids))
        elif len(found_client_ids) > 1:
            result['client_conflict'] = True

        return result

    def create_bulk_downpayments(self, message_text, date, client_id=None):
        """
        Parsea el mensaje completo y crea los anticipos correspondientes.

        Returns:
            tupla (created_downpayments, errors) donde errors es una lista de
            advertencias sobre lineas omitidas o con conceptos no encontrados.
        """
        lines = (message_text or '').split('\n')
        downpayment_vals_list = []
        errors = []
        default_concept = None

        for line_num, raw_line in enumerate(lines, 1):
            line = self._strip_line_marker(raw_line).strip()
            parsed = self._parse_line(line)

            if not parsed:
                continue

            try:
                building, _match_type = self._find_building_with_match_info(parsed['building_name'])

                if not building:
                    errors.append(
                        f"Línea {line_num}: Obra '{parsed['building_name']}' no encontrada. "
                        f"Esta línea se omitirá."
                    )
                    continue

                concept = None
                if parsed['concept_name']:
                    concept = self._find_concept(parsed['concept_name'])
                    if not concept:
                        errors.append(
                            f"Línea {line_num} (Obra: {parsed['building_name']}): "
                            f"Concepto '{parsed['concept_name']}' no encontrado. "
                            f"Se usará el concepto predeterminado."
                        )

                if not concept:
                    if not default_concept:
                        default_concept = self._get_default_concept()
                    concept = default_concept

                vals = {
                    'building_id': building.id,
                    'client_id': building.client_id.id if building.client_id else (client_id or False),
                    'concept_id': concept.id,
                    'amount': parsed['amount'],
                    'date': date,
                }

                downpayment_vals_list.append(vals)

            except Exception as e:
                errors.append(f"Línea {line_num}: Error procesando '{line}': {str(e)}")

        if not downpayment_vals_list:
            raise UserError(
                'No se pudo procesar ningún anticipo del mensaje.\n'
                'Verifica que el formato sea correcto: $monto nombre_obra'
            )

        created_downpayments = self.env['retana.downpayment'].create(downpayment_vals_list)
        return created_downpayments, errors
