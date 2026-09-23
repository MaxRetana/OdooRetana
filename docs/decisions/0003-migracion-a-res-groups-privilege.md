# ADR 0003: Migración de `res.groups.category_id` a `res.groups.privilege_id`

- **Estado:** Aceptada
- **Fecha:** 2026-09-22
- **Contexto:** Migración Odoo 17 → 19, porting del módulo `home`
- **Decidido por:** Maximiliano Retana / Claude (verificado contra código fuente oficial)

## Contexto

Al portar `extra-addons/home/security/groups.xml` se detectó un cambio de arquitectura
real en el modelo de seguridad de Odoo 19.0 (no solo un rename cosmético), confirmado
leyendo el código fuente de `odoo/odoo` rama `19.0` en GitHub:

- `res.groups.category_id` (Many2one a `ir.module.category`) **ya no existe** en 19.0.
- En su lugar aparece `res.groups.privilege_id` (Many2one a un modelo nuevo,
  `res.groups.privilege`), que es el que ahora agrupa visualmente los grupos en la
  pestaña de "Derechos de acceso" del formulario de Usuario.
- `res.groups.privilege` sí tiene un campo `category_id` que apunta a
  `ir.module.category` — la categoría no desaparece, se mueve un nivel: antes
  `res.groups` apuntaba directo a la categoría, ahora apunta a un "privilegio"
  intermedio, y es el privilegio el que apunta a la categoría.
- Se confirmó el patrón exacto de uso mirando cómo lo hace el propio módulo `account`
  de Odoo 19.0 (`res.groups.privilege` + `privilege_id` en cada `res.groups`).
- De forma relacionada, `res.groups.users` (Many2many a `res.users`) se renombró a
  `res.groups.user_ids`, y `res.users.groups_id` se renombró a `res.users.group_ids`
  (sin alias de compatibilidad hacia atrás — es un cambio duro, no un warning).

`res.groups.privilege_id` **no es obligatorio**: un grupo sin privilegio sigue
funcionando igual a nivel de permisos, solo pierde el agrupamiento visual en el
formulario de Usuario.

## Decisión

Se migra `home/security/groups.xml` al nuevo esquema:

1. Se mantiene el registro `ir.module.category` (`module_category_home_home`) tal cual.
2. Se agrega un nuevo registro `res.groups.privilege` (`privilege_home_home`) que
   apunta a esa categoría.
3. Los dos grupos del módulo (`group_home_home_user`, `group_home_home_admin`) pasan
   de `category_id` a `privilege_id`, apuntando al nuevo privilegio.
4. El campo `users` del grupo admin pasa a `user_ids`.
5. En código Python (`home_home.py`) y en los tests, todo uso de
   `self.env.user.groups_id` pasa a `self.env.user.group_ids`, y de
   `ir.ui.menu`'s `groups_id` a `group_ids` en los tests que crean menús de prueba.

Se optó por replicar el patrón completo (crear el `res.groups.privilege`) en vez de
simplemente omitir `privilege_id`, para conservar el mismo agrupamiento visual que
tenía el módulo en 17.0/18.0.

## Consecuencias

- Este mismo patrón debe revisarse en cualquier otro módulo del repo que defina
  `res.groups` con `category_id` o `users`, o que lea `res.users.groups_id` /
  `ir.ui.menu.groups_id` en Python. Al momento de este ADR, tras revisar los 7 módulos
  en alcance, **solo `home` los usa**; el resto no define grupos propios.
- Si en el futuro se agregan grupos de seguridad a otro módulo custom, deben crearse
  ya directamente contra `privilege_id` (no contra el `category_id`, que no existe en
  19.0).
- No se detectó ningún alias de compatibilidad hacia atrás en el código fuente de
  Odoo 19.0 para `category_id`/`users`/`groups_id` — cualquier dato o vista externa
  (por ejemplo, un reporte o una integración) que todavía referencie estos nombres de
  campo debe actualizarse antes del corte a producción.
