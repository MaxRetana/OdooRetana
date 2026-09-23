# Field Tracking Mixin

Mixin abstracto reutilizable para trackear automáticamente cambios en campos
`One2many` y `Many2many` de cualquier modelo, registrando los cambios (líneas
agregadas, eliminadas o modificadas) como un mensaje HTML en el chatter.

## Cómo usarlo

1. Hereda de `field.tracking.mixin` en tu modelo (además de `mail.thread`,
   que es quien te da el chatter donde se publican los cambios).
2. Define el diccionario `_tracked_fields` con la configuración de qué
   campos trackear.

```python
class MiModelo(models.Model):
    _name = 'mi.modelo'
    _inherit = ['mail.thread', 'field.tracking.mixin']

    _tracked_fields = {
        'linea_ids': {
            'type': 'one2many',
            'display_name': 'Líneas',
            'fields_to_track': ['producto_id', 'cantidad', 'precio'],
            'display_fields': {
                'producto_id': lambda val: val.name if val else 'Sin producto',
                'cantidad': lambda val: str(val),
                'precio': lambda val: f"${val:,.2f}",
            },
        },
        'tag_ids': {
            'type': 'many2many',
            'display_name': 'Etiquetas',
            'fields_to_track': ['name'],
        },
    }
```

Al hacer `write()` sobre un registro (o varios) de `mi.modelo` cambiando
`linea_ids` o `tag_ids`, el mixin compara el estado antes/después y publica
un mensaje en el chatter listando qué se agregó, eliminó o modificó.

## Compatibilidad

- **Odoo:** 19.0
- **Depende de:** `base`, `mail`

Usado hoy por `retana_bills` en varios de sus modelos de presupuestos.

## Notas de la migración 17 → 19

- Se normalizó la versión del manifest a `19.0.1.0.0`. Antes decía `15.0.1`,
  muy desalineada respecto al resto del repo y sin relación con la fecha del
  `CHANGELOG.md` (que ya documentaba, informalmente, una versión
  `17.0.1.0.0`).
- Se corrigió un bug preexistente en `write()`: por un `return` ubicado
  dentro del `for record in self`, al escribir sobre un recordset de más de
  un registro el mixin solo trackeaba el primero — el resto se guardaba
  igual, pero sin dejar rastro en el chatter. Ver `CHANGELOG.md` para el
  detalle técnico del fix.
- No usa vistas, seguridad ni assets — es puro Python (`models.AbstractModel`),
  por lo que no se vio afectado por cambios de sintaxis de vistas/OWL en 19.0.
