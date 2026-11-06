# ADR 0001: Retiro de los módulos custom no instalados del repositorio

- **Estado:** Aceptada
- **Fecha:** 2026-09-22
- **Contexto:** Migración Odoo 17 → 19 (ver [`docs/MIGRACION_ODOO_17_A_19.md`](../MIGRACION_ODOO_17_A_19.md), sección 3.2)
- **Decidido por:** Maximiliano Retana

## Contexto

El inventario de módulos custom (sección 3 del plan de migración) confirmó contra
`ir_module_module` en la base `retana` que de los 11 módulos en `extra-addons/`
solo 7 están realmente instalados. Los otros 4 estaban en estado `uninstalled`:

| Módulo | Motivo de no uso |
|---|---|
| `custom_home_dashboard` | Duplicaba la funcionalidad de `home` (mismo dashboard); `home` es el que quedó activo. |
| `capture_data_camera` | Extendía `hr.employee`; sin caso de uso vigente (no hay módulos de RRHH instalados). |
| `grades_manager` | Extendía `res.partner` para gestión de calificaciones; sin relación con el negocio actual de Retana. |
| `maintenance_odoo_retana` | Segundo override de `ir.http` (ventana de mantenimiento); redundante y generaba riesgo de conflicto de herencia si se llegara a instalar junto con `home`. |

El plan de migración (sección 11, punto 2) dejaba esta decisión pendiente de negocio antes de
iniciar el porting de código a 19.0, para no invertir esfuerzo portando módulos sin uso real.

## Decisión

Se **eliminan del repositorio** los 4 módulos no instalados
(`custom_home_dashboard`, `capture_data_camera`, `grades_manager`, `maintenance_odoo_retana`),
en lugar de conservarlos sin portar como "legacy".

Se verificó previamente (`grep` sobre todo el repo) que ningún otro módulo, archivo de
configuración o compose depende de ellos — su retiro no afecta a los 7 módulos en alcance.

## Consecuencias

- El alcance de porting a Odoo 19.0 queda limitado a los 7 módulos realmente instalados
  (`home`, `field_tracking_mixin`, `retana_bills`, `retana_bills_weekday_config`,
  `retana_custom`, `retana_login_custom`, `retana_web`), reduciendo superficie de trabajo y
  riesgo de mantener código muerto en el repo.
- Si en el futuro se necesita alguna de estas funcionalidades (p. ej. gestión de calificaciones
  o ventana de mantenimiento), se recomienda **reescribirla desde cero** contra la API de
  Odoo 19.0 en vez de recuperar el código eliminado, dado que estaba escrito contra manifests
  de Odoo 15.0/16.0/17.0 y ya estaba desactualizado antes de esta migración.
- El historial de git conserva el código eliminado (commit de este ADR), por lo que sigue
  siendo recuperable si se decide reactivar alguno de estos módulos más adelante.
