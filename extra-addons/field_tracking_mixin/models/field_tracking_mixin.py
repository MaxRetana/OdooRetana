# -*- coding: utf-8 -*-
from odoo import models, api


class FieldTrackingMixin(models.AbstractModel):
    """
    Mixin abstracto para trackear cambios en campos One2many y Many2many.
    
    Para usar este mixin:
    1. Hereda de 'field.tracking.mixin' en tu modelo
    2. Asegúrate de heredar también de 'mail.thread'
    3. Define el diccionario _tracked_fields con la configuración
    
    Ejemplo de uso:
    
    class MiModelo(models.Model):
        _name = 'mi.modelo'
        _inherit = ['mail.thread', 'field.tracking.mixin']
        
        # Configurar campos a trackear
        _tracked_fields = {
            'linea_ids': {
                'type': 'one2many',
                'display_name': 'Líneas',
                'fields_to_track': ['producto_id', 'cantidad', 'precio'],
                'display_fields': {
                    'producto_id': lambda val: val.name if val else 'Sin producto',
                    'cantidad': lambda val: str(val),
                    'precio': lambda val: f"${val:,.2f}",
                }
            },
            'tag_ids': {
                'type': 'many2many',
                'display_name': 'Etiquetas',
                'fields_to_track': ['name'],
            }
        }
    """
    _name = 'field.tracking.mixin'
    _description = 'Mixin para Tracking de Campos Relacionales'

    # Diccionario de configuración de campos a trackear
    # Debe ser sobrescrito en el modelo que hereda
    _tracked_fields = {}

    def write(self, vals):
        """
        Sobrescribir write para trackear cambios en campos relacionales configurados
        """
        # Verificar si algún campo trackeado está en vals
        fields_to_track = set(self._tracked_fields.keys()) & set(vals.keys())
        
        if fields_to_track:
            for record in self:
                # Guardar snapshots de todos los campos trackeados que van a cambiar
                old_snapshots = {}
                for field_name in fields_to_track:
                    field_value = record[field_name]
                    old_snapshots[field_name] = self._prepare_field_snapshot(
                        field_name, field_value
                    )
                
                # Ejecutar el write original
                result = super(FieldTrackingMixin, record).write(vals)
                
                # Comparar y registrar cambios para cada campo
                all_changes = []
                for field_name in fields_to_track:
                    new_snapshot = self._prepare_field_snapshot(
                        field_name, record[field_name]
                    )
                    field_changes = self._compare_field_snapshots(
                        field_name, old_snapshots[field_name], new_snapshot
                    )
                    if field_changes:
                        all_changes.append(field_changes)
                
                # Registrar todos los cambios en un solo mensaje
                if all_changes:
                    record.message_post(body='<br/>'.join(all_changes))
                
                return result
        
        return super(FieldTrackingMixin, self).write(vals)

    def _prepare_field_snapshot(self, field_name, field_value):
        """
        Crear un snapshot del estado actual de un campo relacional
        
        :param field_name: Nombre del campo
        :param field_value: Valor actual del campo (recordset)
        :return: Diccionario con el snapshot
        """
        if field_name not in self._tracked_fields:
            return {}
        
        config = self._tracked_fields[field_name]
        field_type = config.get('type', 'one2many')
        fields_to_track = config.get('fields_to_track', [])
        
        snapshot = {}
        
        for record in field_value:
            record_data = {}
            for tracked_field in fields_to_track:
                if hasattr(record, tracked_field):
                    value = record[tracked_field]
                    record_data[tracked_field] = self._format_field_value(
                        field_name, tracked_field, value
                    )
            snapshot[record.id] = record_data
        
        return snapshot

    def _format_field_value(self, field_name, tracked_field, value):
        """
        Formatear el valor de un campo según la configuración
        
        :param field_name: Nombre del campo principal
        :param tracked_field: Nombre del campo trackeado
        :param value: Valor del campo
        :return: Valor formateado
        """
        config = self._tracked_fields.get(field_name, {})
        display_fields = config.get('display_fields', {})
        
        # Si hay una función de formateo personalizada, usarla
        if tracked_field in display_fields:
            formatter = display_fields[tracked_field]
            return formatter(value)
        
        # Formateo por defecto según tipo
        if hasattr(value, 'name'):  # Many2one
            return value.name if value else False
        elif isinstance(value, (list, tuple)):  # Many2many o lista
            if value and hasattr(value[0], 'name'):
                return ', '.join([v.name for v in value])
            return ', '.join([str(v) for v in value])
        elif hasattr(value, 'mapped'):  # Recordset
            return ', '.join(value.mapped('name'))
        else:
            return str(value) if value not in (False, None, '') else ''

    def _compare_field_snapshots(self, field_name, old_snapshot, new_snapshot):
        """
        Comparar dos snapshots y generar HTML con los cambios
        
        :param field_name: Nombre del campo
        :param old_snapshot: Snapshot anterior
        :param new_snapshot: Snapshot nuevo
        :return: String HTML con los cambios o False
        """
        config = self._tracked_fields.get(field_name, {})
        display_name = config.get('display_name', field_name)
        fields_to_track = config.get('fields_to_track', [])
        
        changes = []
        
        # Registros eliminados
        deleted_ids = set(old_snapshot.keys()) - set(new_snapshot.keys())
        for record_id in deleted_ids:
            record_desc = self._get_record_description(
                old_snapshot[record_id], fields_to_track
            )
            changes.append(f"<li><strong>❌ Eliminado:</strong> {record_desc}</li>")
        
        # Registros nuevos
        new_ids = set(new_snapshot.keys()) - set(old_snapshot.keys())
        for record_id in new_ids:
            record_desc = self._get_record_description(
                new_snapshot[record_id], fields_to_track
            )
            changes.append(f"<li><strong>✅ Agregado:</strong> {record_desc}</li>")
        
        # Registros modificados
        common_ids = set(old_snapshot.keys()) & set(new_snapshot.keys())
        for record_id in common_ids:
            old_record = old_snapshot[record_id]
            new_record = new_snapshot[record_id]
            record_changes = []
            
            for field in fields_to_track:
                old_value = old_record.get(field, '')
                new_value = new_record.get(field, '')
                
                if old_value != new_value:
                    old_display = old_value if old_value else 'Vacío'
                    new_display = new_value if new_value else 'Vacío'
                    record_changes.append(
                        f"{field}: {old_display} → {new_display}"
                    )
            
            if record_changes:
                main_field = fields_to_track[0] if fields_to_track else 'id'
                record_identifier = new_record.get(main_field, f'ID: {record_id}')
                changes.append(
                    f"<li><strong>✏️ Modificado ({record_identifier}):</strong><br/>"
                    f"&nbsp;&nbsp;&nbsp;&nbsp;{('<br/>&nbsp;&nbsp;&nbsp;&nbsp;').join(record_changes)}</li>"
                )
        
        if changes:
            header = f"<p><strong>📝 Cambios en {display_name}:</strong></p>"
            return header + "<ul>" + "".join(changes) + "</ul>"
        
        return False

    def _get_record_description(self, record_data, fields_to_track):
        """
        Obtener una descripción legible de un registro
        
        :param record_data: Diccionario con los datos del registro
        :param fields_to_track: Lista de campos trackeados
        :return: String con la descripción
        """
        # Usar el primer campo como identificador principal
        if not fields_to_track or not record_data:
            return "Registro"
        
        main_field = fields_to_track[0]
        main_value = record_data.get(main_field, 'Sin valor')
        
        # Si hay más campos, agregarlos como detalles
        if len(fields_to_track) > 1:
            details = []
            for field in fields_to_track[1:]:
                value = record_data.get(field, '')
                if value:
                    details.append(f"{field}: {value}")
            
            if details:
                return f"{main_value} ({', '.join(details)})"
        
        return main_value
