# CHANGELOG

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
