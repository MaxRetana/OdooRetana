from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import re


class RetanaBulkDownpaymentWizard(models.TransientModel):
    _name = 'retana.bulk.downpayment.wizard'
    _description = 'Wizard para crear múltiples anticipos desde mensaje de texto'

    def _get_default_saturday(self):
        """Retorna el sábado de la semana en curso"""
        today = datetime.today()
        # weekday() retorna 0=Lunes, 5=Sábado
        days_until_saturday = (5 - today.weekday()) % 7
        saturday = today + timedelta(days=days_until_saturday)
        return saturday.date()

    message_text = fields.Text(
        string='Mensaje',
        required=True,
        help='Pega el mensaje con los anticipos. Formato: $monto nombre_obra o $monto nombre_obra, concepto'
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
        Busca una obra por nombre exacto (solo case insensitive).
        Si no existe, retorna False y NO la crea automáticamente.
        """
        Building = self.env['retana.buildings']
        
        # Buscar la obra con nombre exacto (solo ignorando mayúsculas/minúsculas)
        building = Building.search([
            ('name', '=ilike', building_name)
        ], limit=1)
        
        return building if building else False

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
