# Retana Web

Sitio web público (portal) para que los clientes/usuarios de Electricos
Retana consulten y descarguen en PDF sus presupuestos, anticipos y obras,
sin entrar al backend de Odoo.

## Qué hace

- Controlador HTTP (`RetanaBillsWebsiteController`) con rutas `/retana/...`:
  inicio con resumen (`/`), listado paginado con búsqueda/filtro/agrupado de
  presupuestos, anticipos y obras, detalle de cada uno, descarga de su
  reporte en PDF, alta de anticipos masivos vía formulario web
  (reutilizando `retana.bulk.downpayment.mixin` de `retana_bills`), y
  descarga de un PDF combinado de varios anticipos seleccionados.
- Todas las rutas exigen sesión de usuario portal o de sistema
  (`_ensure_portal_user`); no hay rutas públicas anónimas.
- Agrega los enlaces "Presupuestos", "Anticipos" y "Obras" al menú principal
  del sitio (`website.menu`).
- Estilos propios (`footer.scss`) para el pie de página del sitio.

## Compatibilidad

- **Odoo:** 19.0
- **Depende de:** `base`, `website`, `retana_bills`

## Notas de la migración 17 → 19

- Se normalizó la versión del manifest a `19.0.1.0.0` (antes decía `18.1.0`,
  inconsistente con la serie realmente instalada en producción, 17.0).
- Se verificó contra el código fuente de Odoo 19.0 que
  `ir.actions.report._render_qweb_pdf(report_ref, res_ids=None, data=None)`
  — el método que usa `_download_report` para generar los PDF — conserva
  exactamente la misma firma.
- Las plantillas QWeb (`views/retana_bills_templates.xml`, 1161 líneas) ya
  usaban sintaxis moderna (`t-esc`, `t-att-*`, `t-call="website.layout"`) sin
  `attrs=`/`states=` ni vistas `<tree>` (son páginas de sitio, `type="qweb"`,
  no vistas de backend) — no requirieron cambios.
- No se detectaron usos de `res.users.groups_id`, `res.groups.category_id`
  ni otros campos renombrados en 19.0 (ver
  [ADR 0003](../../docs/decisions/0003-migracion-a-res-groups-privilege.md))
  en este módulo.

Todo el Python y XML del módulo pasó `python3 -m py_compile` /
`xmllint --noout`. **Pendiente**: probar en un navegador real contra Odoo
19.0 los flujos de listado/filtro/paginado/descarga de PDF, una vez `odev`
tenga el token de GitHub configurado para levantar el entorno local.

## Instalación

Requiere `website` y `retana_bills` instalados. Se activa desde
**Ajustes → Apps**.
