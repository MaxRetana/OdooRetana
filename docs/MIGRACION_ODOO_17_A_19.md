# Plan de Ejecución: Migración Odoo 17 → 19 (OdooRetana)

**Autor:** Preparado para Maximiliano Retana
**Fecha:** 22 de septiembre de 2026
**Repositorio base:** `OdooRetana` (self-hosted, Docker Compose, 11 módulos custom en `extra-addons/`, de los cuales **7 están instalados** en la base de odev — ver sección 3)

> Nota de alcance: la ruta técnica exacta (nombres de campos/modelos renombrados, etc.) cambia entre builds de Odoo 19 y no toda la información pública al respecto es confiable (mucho contenido de blogs de terceros es genérico o generado por SEO). Este plan da la estructura de ejecución, el checklist por módulo y los puntos de verificación; los detalles finos de breaking changes deben confirmarse contra el **changelog oficial de Odoo 19** y el **reporte de la base de datos de prueba** que genera el propio upgrade de Odoo antes de programar el esfuerzo de cada módulo.

---

## 1. Resumen ejecutivo

Se requiere migrar la instancia Odoo de la versión **17.0** a la **19.0**. No existe salto directo soportado: tanto la herramienta oficial de Odoo como OpenUpgrade (OCA) procesan la migración de datos **paso a paso, 17→18→19**, aunque para código custom conviene evaluar si conviene saltar directo a 19 en el desarrollo (evitando mantener dos rondas de porting) y solo usar 18 como puente de datos.

Hallazgos del inventario del repositorio, **confirmados contra la base de datos real (`retana`) en el entorno odev** vía `ir_module_module` (no solo por inspección del código — ver sección 3):

- El repo tiene **11 módulos custom** en `extra-addons/`, pero **solo 7 están realmente instalados** en la base `retana`. Los otros 4 (`capture_data_camera`, `custom_home_dashboard`, `grades_manager`, `maintenance_odoo_retana`) están en estado `uninstalled` y **quedan fuera del alcance obligatorio** de esta migración (ver detalle y matiz en sección 3).
- **Duplicidad `home` vs `custom_home_dashboard` — resuelta**: `home` está instalado; `custom_home_dashboard` no. Solo `home` requiere porting.
- **Conflicto de `ir.http` — no está activo hoy**: de los dos módulos que lo sobrescriben, solo `home` está instalado; `maintenance_odoo_retana` no. No hay conflicto de herencia real en la base actual, pero si se decide instalar `maintenance_odoo_retana` en el futuro (en 17 o ya en 19), debe auditarse antes.
- **`field_tracking_mixin` sigue en uso** (instalado), pese a que su manifest declara `version: '15.0.1'` (Odoo lo normaliza internamente a `17.0.15.0.1` en el registro de módulos). Sí entra en el alcance obligatorio.
- `capture_data_camera` (`hr.employee`, manifest `15.0.0`) y `grades_manager` (`groups_id`/`category_id`, manifest `17.0.0.1`) **no están instalados** — no requieren porting a menos que se decida activarlos, aunque siguen siendo candidatos a limpieza de repo.

**Recomendación de ruta:** migración escalonada con doble ambiente de staging (17→18 y 18→19), usando la plataforma oficial de upgrade de Odoo para la base de datos (más confiable que ejecutar OpenUpgrade a mano) y porting manual del código custom directamente a la sintaxis de 19.0 en una rama de desarrollo paralela.

---

## 2. Objetivos y criterios de éxito

- Instancia productiva corriendo en Odoo 19.0 CE (o EE si aplica) sin pérdida de datos.
- Los 7 módulos custom instalados operando en 19.0 con paridad funcional (o funcionalidad documentada como retirada/reemplazada por core). Los 4 módulos no instalados quedan fuera de este criterio salvo que se decida reactivarlos.
- Cero incidentes críticos en las primeras 2 semanas post go-live (ventana de hypercare).
- Plan de rollback probado y disponible durante la ventana de corte.
- Documentación actualizada (manifest, README, changelog interno) al cierre.

---

## 3. Alcance: inventario de módulos custom

Estado verificado con `SELECT name, state FROM ir_module_module` sobre la base `retana` (odev), el 22 de septiembre de 2026.

### 3.1 Instalados — en alcance obligatorio (7 módulos)

| Módulo | Versión manifest | Componentes relevantes | Nivel de riesgo estimado |
|---|---|---|---|
| `home` | 17.0.1.0.0 | Dashboard OWL, navbar, systray, tours de test, `groups.xml`, override `ir_http.py` | Alto — frontend OWL + seguridad + tests |
| `field_tracking_mixin` | 15.0.1 (normalizada a 17.0.15.0.1 en el registro) | Mixin de tracking de campos | Medio-alto — versión de manifest muy atrasada respecto al resto; revisar compatibilidad de API antes de portar |
| `retana_bills` | 17.0.15.0.0 | Modelos de facturación/presupuestos, reportes QWeb, wizards, vistas extensas | Alto — módulo más grande, lógica de negocio crítica |
| `retana_bills_weekday_config` | 17.0.1.0.0 | Configuración adicional sobre `retana_bills` | Bajo-medio (dependiente de `retana_bills`) |
| `retana_custom` | 17.0.0.1 | Theming (CSS/JS, dark theme) | Bajo |
| `retana_login_custom` | 17.0.18.1.0 | Plantillas de login (SCSS) | Bajo |
| `retana_web` | 17.0.18.1.0 | Controladores (21 KB), plantilla de sitio (66 KB) | Alto — sitio web público, mayor superficie de cambio |

### 3.2 No instalados — fuera de alcance obligatorio (4 módulos)

No aparecen en `state = 'installed'` en la base `retana`. No bloquean el go-live y no hace falta portarlos salvo que se decida reactivarlos; sí conviene decidir en fase 1 si se retiran del repo o se documentan como "legacy, no instalar".

| Módulo | Versión manifest | Estado en `retana` | Nota |
|---|---|---|---|
| `custom_home_dashboard` | 16.0.1 | `uninstalled` | Duplicaba a `home` (mismo dashboard); `home` es el activo, este puede retirarse del alcance de porting |
| `capture_data_camera` | 15.0.0 | `uninstalled` | Extiende `hr.employee`; sin uso actual |
| `grades_manager` | 17.0.0.1 | `uninstalled` | Modelos/vistas sobre `res.partner`; sin uso actual |
| `maintenance_odoo_retana` | 17.0.1.0.0 | `uninstalled` | Segundo override de `ir_http.py`; al no estar instalado, no genera conflicto activo con el de `home` |

**Acción previa a migrar (ya resuelta por esta verificación):** el alcance real de porting son los 7 módulos de 3.1. Queda pendiente solo la decisión de negocio sobre si los 4 módulos de 3.2 se eliminan del repo o se mantienen sin instalar (documentarlo en fase 1, sección 7).

### 3.3 Módulos estándar/OCA instalados (contexto para QA, no requieren porting de código)

La misma base `retana` tiene **52 módulos no-custom instalados** (además de los 7 custom); estos se migran vía el proceso oficial de upgrade/OpenUpgrade, no por porting manual, pero definen el alcance real de pruebas funcionales en fase 5 (sección 5). Áreas cubiertas: `account` + `account_edi_ubl_cii` + `account_payment` (contabilidad/facturación electrónica), `stock` + `stock_account` + `stock_sms` (inventario), `website` + `website_mail` + `website_payment` + `website_sms` + `http_routing` (sitio web), `mail` + `sms` + `snailmail` + `google_gmail` (comunicaciones), `payment` (pasarelas de pago), `spreadsheet_dashboard` + `spreadsheet_dashboard_stock_account` (dashboards), `auth_totp*` + `google_recaptcha` (seguridad/login), `barcodes` + `barcodes_gs1_nomenclature`, `partner_autocomplete`, `web_unsplash`, `digest`, `onboarding`. No hay módulos de `sale`, `purchase`, `crm`, `hr` ni `manufacturing` instalados — no hace falta cubrirlos en el checklist de pruebas.

---

## 4. Estrategia de migración

### 4.1 Ruta de datos: 17 → 18 → 19 (escalonada)

Ni la plataforma oficial de Odoo ni OpenUpgrade garantizan saltos de más de una versión mayor en un solo paso para bases con módulos custom instalados. Camino recomendado:

1. **Opción A — Upgrade oficial de Odoo (preferida si hay soporte/Enterprise o si se paga el servicio para CE):**
   solicitar una base de datos de prueba vía la plataforma oficial de upgrade de Odoo, que aplica las migraciones de esquema y genera un **reporte de incompatibilidades** (módulos no estándar detectados, campos/modelos que cambiaron). Este reporte es la fuente más confiable de "qué se rompe" para los 7 módulos custom instalados — úsese para afinar el checklist de la sección 6 antes de invertir horas de desarrollo.
2. **Opción B — OpenUpgrade (OCA), autogestionado:**
   clonar los scripts de OpenUpgrade para 18.0, migrar 17→18, validar, luego clonar los scripts para 19.0 y migrar 18→19. Requiere más esfuerzo propio pero no depende de un servicio externo ni de licenciamiento Enterprise.

Ambas opciones migran **solo el esquema y los datos estándar de Odoo**; los módulos custom deben portarse aparte (sección 4.2) y probarse contra la base ya migrada.

### 4.2 Ruta de código custom: porting directo a 19.0

En lugar de portar cada módulo 17→18 y luego 18→19, se recomienda portar el código **directamente a la sintaxis/API de 19.0** en una rama de desarrollo, y solo usar la base intermedia en 18 para validar la migración de *datos* (no de código). Esto evita duplicar el esfuerzo de porting dos veces.

### 4.3 Entornos

- **Prod (17.0)** — no se toca hasta el corte final.
- **Staging-18** — base de datos resultado del paso 17→18, usada solo para validar integridad de datos.
- **Staging-19 (dev)** — base 18→19 + código custom portado a 19.0. Ambiente principal de trabajo y QA.
- **Staging-19 (UAT)** — copia fresca de Staging-19 para pruebas de usuario final antes del corte.

Dado que el repo ya tiene `docker-compose-local.yaml` y `docker-compose-test.yaml`, se recomienda crear un tercer compose (`docker-compose-19.yaml`) apuntando a la imagen `odoo:19.0` para desarrollo local sin interferir con los stacks actuales.

---

## 5. Fases y cronograma

Estimación para un equipo de 1-2 desarrolladores Odoo. Con 7 módulos en alcance (varios con frontend OWL y controladores), el proyecto cae en la banda "mediana-baja" — **7 a 11 semanas** en total (recortado desde la estimación inicial de 9-13 semanas basada en 11 módulos, al confirmarse que 4 no están instalados). Ajustar según disponibilidad real.

| Fase | Duración estimada | Objetivo |
|---|---|---|
| **0. Preparación y gobernanza** | 3-5 días | Congelar cambios no críticos en prod, definir dueños por módulo, respaldo completo (BD + filestore), crear `docker-compose-19.yaml` |
| **1. Diagnóstico (assessment)** | 1 semana | Solicitar/generar reporte de upgrade oficial, confirmar versiones de manifest reales, decidir retiro de `custom_home_dashboard`/`field_tracking_mixin`, resolver conflicto de doble `ir_http` |
| **2. Migración de datos 17→18** | 3-5 días | Correr upgrade (oficial u OpenUpgrade) sobre copia de prod, validar conteos e integridad |
| **3. Porting de código custom a 19.0** | 2-4 semanas | Adaptar los 7 módulos instalados (ver checklist sección 6), priorizando `retana_bills`, `retana_web`, `home` (alto riesgo) |
| **4. Migración de datos 18→19** | 3-5 días | Correr segundo salto de upgrade sobre Staging-18 ya validada |
| **5. QA funcional** | 2-3 semanas | Smoke test, pruebas automatizadas (`home` ya tiene tests/tours — extenderlos), pruebas de negocio módulo por módulo, pruebas de integración (WhatsApp, reportes, sitio web) |
| **6. UAT (usuario final)** | 1 semana | Usuarios de Retana validan flujos reales en Staging-19 (UAT) |
| **7. Corte a producción** | 1 ventana (fin de semana) | Congelamiento total, migración final, smoke test post-corte |
| **8. Hypercare / post-migración** | 2 semanas | Monitoreo reforzado, soporte prioritario, cierre de documentación |

---

## 6. Checklist técnico por módulo

Aplicar a cada uno de los **7 módulos instalados** (sección 3.1); marcar N/A cuando no aplique. Los 4 módulos no instalados se retiraron del repo (ver [ADR 0001](decisions/0001-retiro-modulos-legacy-no-instalados.md)) y quedan fuera de este checklist.

> **Estado (2026-09-22):** los 7 módulos ya se portaron a la sintaxis/API de 19.0 en el repo (rama `131-feature-plan-de-migracion-a-version-19`, un commit por módulo), validados con análisis estático (`py_compile`, `xmllint`, `node --check`) y verificación de cada cambio contra el código fuente real de `odoo/odoo` rama `19.0` en GitHub. **No** se corrió todavía contra una instancia Odoo 19.0 real ni contra datos reales — eso sigue pendiente (ver nota de bloqueo al final de esta sección).

- [x] `__manifest__.py`: version actualizada a `19.0.1.0.0` en los 7 módulos; `depends` revisado, sin módulos core removidos/renombrados detectados.
- [x] Vistas XML: `<tree>` → `<list>` en las 12 vistas de lista que lo usaban (`home`, `retana_bills`); `attrs="..."` → atributos directos en `retana_bills/views/retana_budget_views.xml`. Validado con `xmllint --noout`, no validado aún contra el log de arranque real de Odoo 19.0.
- [x] Seguridad: `res.groups.category_id` → `res.groups.privilege_id` y `res.groups.users`/`res.users.groups_id` → `user_ids`/`group_ids` en `home/security/groups.xml` y `home/models/home_home.py` (ver [ADR 0003](decisions/0003-migracion-a-res-groups-privilege.md)). `grades_manager` se retiró del repo, no aplica.
- [x] Controladores HTTP (`retana_web/controllers`): revisados, sin sintaxis deprecada; `_render_qweb_pdf` verificado sin cambios en 19.0. El conflicto de doble `ir.http` se resolvió al retirar `maintenance_odoo_retana` (no instalado, ver ADR 0001) — solo queda el override de `home`.
- [x] Frontend OWL (`home`, `retana_bills`, `retana_custom`): revisado — rutas de import, plantillas heredadas de `web.NavBar`/`web.NavBar.AppsMenu` y hooks de OWL verificados sin cambios en 19.0. `custom_home_dashboard` se retiró del repo, no aplica. Tours de `home` no re-ejecutados (requieren instancia real).
- [ ] Reportes QWeb (`retana_bills/report/*.xml`): revisados estáticamente (usan `web.html_container`, sin sintaxis deprecada); **falta** renderizar cada reporte y comparar el PDF de salida contra la versión 17 — requiere instancia real.
- [ ] Wizards (`retana_bills/wizard`, `retana_bills_weekday_config`): revisados y refactorizados (ver commit de `retana_bills_weekday_config`); **falta** probar el flujo completo de creación/confirmación en una instancia real.
- [x] Extensiones de modelos core: `capture_data_camera` (sobre `hr.employee`) se retiró del repo, no aplica.
- [x] Datos de carga: `data/retana_company_info_data.xml` revisado, sin cambios necesarios; se detectó que `data/retana_company_info_import.csv` no está referenciado en el manifest (archivo huérfano, documentado en el README de `retana_bills`, no se borró sin confirmar con el negocio).
- [ ] Dependencias Python (`pytesseract`, `pillow`): no confirmado contra la versión de Python del contenedor `odoo:19` — requiere levantar el stack (`docker-compose-19.yaml`) o el worktree de `odev` para probarlo.
- [x] `__pycache__`: confirmado que **no** está versionado en git (ya estaba cubierto por `.gitignore`); se corrigió además una regla `README.md` genérica en `.gitignore` que hubiera bloqueado los README por módulo.

**Bloqueo de entorno para las pruebas reales (los ítems sin marcar arriba):** no hay Docker disponible en este entorno de trabajo, y `odev` (que gestiona bases Odoo locales por versión) necesita un Personal Access Token de GitHub configurado (`odev setup github`) para clonar el código fuente de Odoo 19.0 — no estaba configurado al momento de este porting. Cualquiera de las dos rutas (`docker compose -f docker-compose-19.yaml up`, o configurar el token de `odev`) desbloquea las pruebas reales pendientes.

---

## 7. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Conflicto de herencia entre los dos overrides de `ir.http` | Baja (no activo hoy — `maintenance_odoo_retana` está `uninstalled`) | Alto si se reactivara | Confirmado por query a `ir_module_module`; solo re-auditar si `maintenance_odoo_retana` se instala en algún momento antes del corte |
| `field_tracking_mixin` (manifest 15.0.1) incompatible con APIs de 19.0 | Media | Medio-alto | Confirmado en uso (instalado) — sí entra al alcance de porting; revisar compatibilidad de API en fase 3 |
| Duplicidad `home` vs `custom_home_dashboard` genera doble esfuerzo de porting | Resuelto | — | Confirmado: solo `home` está instalado; `custom_home_dashboard` queda fuera del alcance de porting |
| Cambios en modelo de seguridad (grupos/privilegios) rompen accesos silenciosamente | Media | Alto | Pruebas de seguridad explícitas por rol de usuario en fase 5, no solo pruebas funcionales |
| Sitio web (`retana_web`, plantilla de 66 KB) con regresiones visuales | Media | Medio | Pruebas visuales/manuales dedicadas + captura de pantallas antes/después |
| Ventana de corte se extiende más de lo previsto | Baja-media | Alto | Ensayar el corte completo al menos una vez en Staging-19 (UAT) con datos de tamaño real |
| Reportes financieros (`retana_bills`) con diferencias numéricas post-migración | Baja | Muy alto | Cuadre de totales contra base de producción antes del go-live (paso obligatorio, no opcional) |

---

## 8. Entorno, respaldo y rollback

- **Respaldo antes de cada salto de versión:** `pg_dump` completo de la base + copia del filestore (`filestore/<db_name>`). No continuar sin backup verificado (restaurable).
- **Rollback:** mientras no haya transacciones nuevas en 19.0, restaurar el backup de 17.0 revierte limpiamente. Definir con el negocio la ventana máxima tras la cual el rollback deja de ser viable (recomendado: no más de 48-72 h después del corte).
- **Congelamiento de cambios:** ninguna migración de datos/hotfix estructural en producción 17.0 desde el inicio de la fase 1 hasta el corte, salvo emergencias documentadas.

---

## 9. Roles y responsabilidades

| Rol | Responsable | Notas |
|---|---|---|
| Dueño del proyecto / decisiones de negocio | Maximiliano | Prioriza módulos, aprueba ventana de corte |
| Desarrollo backend (ORM, seguridad, datos) | — | Porting de modelos, vistas, ACL |
| Desarrollo frontend (OWL, sitio web) | — | Porting de `home`, `retana_web`, `retana_custom` |
| QA / pruebas funcionales | — | Ejecuta checklist sección 6 y pruebas de UAT |
| DevOps / infraestructura | — | Contenedores, backups, ventana de corte, monitoreo post go-live |

---

## 10. Criterios de "Go / No-Go" para el corte a producción

- [ ] Reporte de upgrade oficial sin errores `FATAL` pendientes.
- [ ] Los 7 módulos instalados (o los que se agreguen si se decide reactivar alguno de los 4 no instalados) instalan sin error en Staging-19.
- [ ] Suite de tests de `home` (unit + tour) en verde.
- [ ] Cuadre de totales financieros (`retana_bills`) validado por el negocio.
- [ ] UAT firmado por al menos un usuario clave por área (facturación, RRHH/captura, sitio web).
- [ ] Plan de rollback ensayado y documentado.
- [ ] Ventana de mantenimiento comunicada a usuarios finales.

---

## 11. Próximos pasos inmediatos

1. ~~Confirmar versión real de manifests y decidir destino de `custom_home_dashboard`/`field_tracking_mixin`/conflicto `ir_http`~~ — resuelto en esta revisión (sección 3): alcance de porting = 7 módulos instalados; `custom_home_dashboard`, `capture_data_camera`, `grades_manager` y `maintenance_odoo_retana` quedan fuera al no estar instalados.
2. ~~Decidir con el negocio si los 4 módulos no instalados se eliminan del repo/`extra-addons` o se conservan sin instalar~~ — resuelto: se eliminaron del repo (ver [ADR 0001](decisions/0001-retiro-modulos-legacy-no-instalados.md)).
3. ~~Crear `docker-compose-19.yaml` para levantar un entorno local de desarrollo en 19.0~~ — hecho (`docker-compose-19.yaml`, base de datos vacía y desechable).
4. ~~Portar el código de los 7 módulos instalados a la sintaxis/API de 19.0~~ — hecho, un commit por módulo en la rama `131-feature-plan-de-migracion-a-version-19` (ver sección 6 para el detalle de cada módulo). Validado con análisis estático y verificación contra el código fuente oficial de Odoo 19.0; **no** validado todavía contra una instancia real corriendo.
5. **Pendiente y bloqueado:** correr los 7 módulos contra una instancia Odoo 19.0 real (`docker compose -f docker-compose-19.yaml up`, o configurar `odev setup github` para usar el worktree local de `odev`) y ejecutar la suite de tests de `home` (unitarios + tours). Ninguna de las dos rutas estaba disponible en el entorno donde se hizo este porting.
6. Solicitar/generar la base de datos de prueba de upgrade oficial de Odoo para obtener el reporte real de incompatibilidades sobre esta instancia específica — sigue pendiente, requiere la cuenta/suscripción de Odoo.com del negocio.
7. Decidir la ruta de migración de **datos** de la base real (Opción A vs B, sección 4.1) — pospuesta a propósito hasta que el código esté validado en runtime (ver [ADR 0002](decisions/0002-porting-de-codigo-primero-datos-despues.md)).
8. Decidir si la instancia necesita soportar más de un idioma, y en ese caso retomar el trabajo de traducciones (ver [ADR 0004](decisions/0004-estado-de-traducciones-i18n.md)).

---

## Referencias

- [Odoo 17 to 19 Migration: What Actually Breaks — Octura Solutions](https://octurasolutions.com/resources/migrating-from-odoo-17-to-19-breaking-changes-upgrade-path-and-testing-strategy)
- [Odoo Migration with OpenUpgrade: Step-by-Step (2026) — DeployMonkey](https://deploymonkey.com/blog/odoo-migration-openupgrade-guide)
- [Odoo 19 Breaking Changes: res.groups, group_ids, Removed Fields](https://ocu.winotto.com/articles/whats-new-odoo-19)
- [Odoo 17 to 19 Migration: 2026 Step-by-Step Guide — ECOSIRE](https://ecosire.com/blog/odoo-migration-17-to-19-guide)
- [Odoo 19 vs Odoo 17: When to Migrate — ECOSIRE](https://ecosire.com/blog/odoo-19-vs-odoo-17-migration-decision-matrix)
- [Odoo Upgrade & Migration Guide: v14-v18 to v19 — DeployMonkey](https://deploymonkey.com/blog/odoo-upgrade-migration-14-to-19)
- [Upgrade — Odoo 19.0 documentation (oficial)](https://www.odoo.com/documentation/19.0/administration/upgrade.html)

> Estas fuentes son en su mayoría contenido de terceros (agencias/blogs) publicado en 2026; útiles para dimensionar el esfuerzo, pero los detalles técnicos exactos (nombres de modelos/campos renombrados) deben confirmarse contra el changelog oficial y el reporte de upgrade generado para esta base de datos específica antes de ejecutarlos.
