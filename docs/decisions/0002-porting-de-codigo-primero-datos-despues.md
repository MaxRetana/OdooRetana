# ADR 0002: Priorizar el porting de código a 19.0; posponer la migración de datos reales

- **Estado:** Aceptada
- **Fecha:** 2026-09-22
- **Contexto:** Migración Odoo 17 → 19 (ver [`docs/MIGRACION_ODOO_17_A_19.md`](../MIGRACION_ODOO_17_A_19.md), secciones 4 y 11)
- **Decidido por:** Maximiliano Retana

## Contexto

El plan de migración plantea dos rutas posibles para migrar los **datos** de la base real
`retana` de 17.0 a 19.0 (sección 4.1):

- **Opción A:** upgrade oficial de Odoo (servicio de Odoo.com), que requiere gestionar una
  solicitud desde la cuenta/suscripción del negocio y no puede iniciarse desde este entorno
  de desarrollo.
- **Opción B:** OpenUpgrade (OCA) autogestionado, que exige levantar y validar scripts de
  migración de esquema contra una copia de la base real — trabajo de infraestructura
  considerable y con impacto potencial sobre datos productivos si no se ejecuta con cuidado.

Ambas opciones son independientes del porting del **código** custom (sección 4.2), que puede
adelantarse contra bases de datos Odoo 19.0 vacías/desechables sin ningún riesgo para los
datos reales de Retana.

## Decisión

Se **pospone** la decisión y ejecución de la migración de datos de la base `retana` real.
El trabajo de esta fase se concentra primero en:

1. Portar el código de los 7 módulos en alcance a la sintaxis/API de Odoo 19.0.
2. Validar cada módulo instalando contra bases de datos Odoo 19.0 **vacías**, creadas y
   descartadas localmente con `odev` (`odev create <db> -V 19.0`), nunca contra una copia
   de `retana` con datos reales.

La migración de datos (Opción A u Opción B) se retomará como una fase aparte, una vez que:

- El código de los 7 módulos ya instale y pase pruebas en Odoo 19.0 vacío.
- El negocio decida qué ruta de datos usar (implica costo y/o acceso a servicios externos
  que este entorno de desarrollo no gestiona por sí solo).

## Consecuencias

- Esta fase de trabajo **no toca en ningún momento la base de datos `retana` real** ni su
  filestore — cero riesgo de pérdida de datos productivos mientras dure el porting de código.
- El checklist técnico de la sección 6 del plan se ejecuta módulo por módulo contra
  bases Odoo 19.0 desechables gestionadas por `odev`.
- Antes de programar la fase de migración de datos real, se debe volver a esta decisión y
  reemplazarla (o complementarla) por un ADR que registre la ruta elegida (A o B) y el
  cronograma acordado con el negocio.
