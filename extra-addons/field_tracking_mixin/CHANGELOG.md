# CHANGELOG

## Versión 19.0.1.0.0 (2026-09-22)

### Cambios

- Se normaliza la versión del manifest a `19.0.1.0.0` (antes decía `15.0.1`,
  desalineada con el resto del repo y con este mismo changelog, que ya
  documentaba una versión `17.0.1.0.0`).
- Se corrige un bug en `write()`: la versión anterior hacía `return` dentro del
  `for record in self`, por lo que al escribir sobre un recordset con más de
  un registro solo se trackeaba (y retornaba) el primero; además se llamaba a
  `super().write(vals)` una vez por registro en vez de en batch. Ahora se
  toma el snapshot "antes" por registro, se hace un único `write()` por lotes
  sobre todo el recordset, y luego se compara/publica el cambio de cada
  registro.
- Se moderniza `super(FieldTrackingMixin, self).write(vals)` a `super().write(vals)`
  (sintaxis de Python 3, ya estándar en el resto del repo).
- Se agrega `README.md` y `README.rst`; ver ahí la guía de uso (la referencia
  a un `EXAMPLES.py` en la entrada anterior de este changelog nunca llegó a
  crearse — los ejemplos ahora viven directamente en el README).

## Versión 17.0.1.0.0 (2025-11-24)

### Características Iniciales

- ✅ Mixin abstracto `field.tracking.mixin` para tracking de campos relacionales
- ✅ Soporte completo para campos `One2many`
- ✅ Soporte completo para campos `Many2many`
- ✅ Detección automática de:
  - Registros agregados
  - Registros eliminados
  - Registros modificados
- ✅ Mensajes formateados en HTML con emojis
- ✅ Configuración flexible mediante diccionario `_tracked_fields`
- ✅ Formateo personalizado de valores mediante funciones lambda
- ✅ Formateo por defecto inteligente para tipos comunes
- ✅ Documentación completa con ejemplos
- ✅ Compatible con Odoo 17.0

### Dependencias

- `base`: Módulo base de Odoo
- `mail`: Para funcionalidad de chatter y mensajería

### Uso

Ver archivo `README.md` para instrucciones completas de uso.

### Ejemplos

Ver archivo `EXAMPLES.py` para ejemplos de implementación.
