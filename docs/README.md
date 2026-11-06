# Documentación de OdooRetana

Este directorio reúne la documentación técnica del proyecto que no vive junto al código de
cada módulo (para eso, ver el `README.md`/`README.rst` dentro de cada carpeta en
`extra-addons/<modulo>/`).

## Contenido

- [`MIGRACION_ODOO_17_A_19.md`](MIGRACION_ODOO_17_A_19.md) — plan de ejecución de la migración
  de la instancia de Odoo 17.0 a 19.0: alcance, fases, checklist técnico por módulo, riesgos
  y criterios de go/no-go.
- [`decisions/`](decisions/) — registro de decisiones de arquitectura y de negocio (ADR,
  *Architecture Decision Records*) tomadas durante la migración. Cada archivo documenta el
  contexto, la decisión y sus consecuencias, en el momento en que se tomó.

## Convención de ADRs

Los archivos en `decisions/` siguen el formato `NNNN-titulo-corto.md`, numerados en orden
secuencial y nunca renumerados ni borrados aunque queden obsoletos (en ese caso se marcan como
*Reemplazada* y se enlaza al ADR que la reemplaza). Úsese este formato para cualquier decisión
técnica o de negocio no trivial tomada durante el proyecto, no solo durante la migración a 19.0.
