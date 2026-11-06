# ADR 0004: Estado de traducciones (i18n) — diagnóstico, sin cambios aplicados

- **Estado:** Propuesta (diagnóstico; requiere decisión de negocio antes de actuar)
- **Fecha:** 2026-09-22
- **Contexto:** Migración Odoo 17 → 19, pedido explícito de revisar "traducciones, buenas prácticas"
- **Decidido por:** Pendiente — Maximiliano Retana

## Contexto

Se revisaron los 7 módulos en alcance en busca de infraestructura de traducción:

- **Ninguno de los 7 módulos tiene carpeta `i18n/`** ni archivos `.pot`/`.po`. No
  hay infraestructura de traducción en el repo, en ningún módulo, no solo en los
  que se migraron ahora.
- El uso de `translate=True` en los campos `Char`/`Text` es inconsistente: por
  ejemplo `home.home.name` sí lo tiene, pero campos de nombre equivalentes en
  `retana_bills` (`retana.buildings.name`, `retana.budget_type.name`,
  `retana.downpayment.type.concept.name`, `retana.type.res.partner.name`, etc.)
  no lo tienen.
- Toda la interfaz de los 7 módulos está *hard-coded* en español (labels,
  mensajes de error, nombres de reportes). No hay evidencia de que el negocio
  necesite hoy soportar más de un idioma.

## Por qué no se aplicó un cambio ahora

Generar archivos `.pot`/`.po` reales y completos requiere ejecutar la
exportación de traducciones de Odoo (`odoo-bin --i18n-export` o el asistente de
Ajustes → Traducciones) contra una instancia corriendo — no es algo que se
pueda producir de forma confiable a mano sin ese paso, y en esta sesión no hay
un entorno Odoo 19.0 corriendo (ver bloqueo del token de GitHub de `odev` en
los commits de porting de cada módulo).

Además, agregar `translate=True` a un campo que **ya tiene datos en
producción** no es un cambio cosmético gratis: Odoo migra el valor existente a
la estructura de traducción al actualizar el módulo, lo cual es un paso de
migración de datos real. Dado que este trabajo pospuso explícitamente la
migración de datos de la base real (ver
[ADR 0002](0002-porting-de-codigo-primero-datos-despues.md)) y el pedido
explícito de no perder datos, no se tocó `translate=True` en ningún campo
existente sin antes consultarlo.

## Decisión pendiente

Antes de invertir tiempo en esto, se necesita una respuesta de negocio a:
**¿la instancia de Retana necesita soportar más de un idioma (o planea
necesitarlo) en algún momento previsible?**

- Si la respuesta es **no**: no vale la pena construir infraestructura de
  traducción; alcanza con mantener el español hard-coded como está. En ese
  caso, esta ADR se puede cerrar como "no aplica" sin más acción.
- Si la respuesta es **sí**: el trabajo pendiente es (a) decidir qué campos de
  "nombre"/catálogo conviene marcar `translate=True` siguiendo la convención
  de Odoo (campos tipo catálogo — p. ej. tipos, conceptos — sí; campos que son
  nombres propios o códigos generados por secuencia — p. ej. el `name` de un
  anticipo o de una obra — no), (b) generar los `.pot` iniciales de cada
  módulo contra una instancia real, y (c) validar que la migración de los
  datos existentes a la nueva estructura de traducción no pierda información.

## Consecuencias

Mientras esta decisión no se tome, los 7 módulos quedan igual que estaban
respecto a traducciones (sin `i18n/`, con el mismo `translate=True` parcial
que ya tenían). No es un bloqueante para el resto de la migración a 19.0.
