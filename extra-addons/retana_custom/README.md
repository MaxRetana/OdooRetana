# Retana Custom Odoo

Theming (tema oscuro) para el backend de Odoo de Electricos Retana.

## Qué hace

- Agrega una hoja de estilos (`static/src/css/retana_dark_theme.css`) al bundle
  `web.assets_backend`, que aplica un tema oscuro a la navbar, dropdowns y controles
  de formulario del backend.
- Agrega una clase `retana-dark-theme` al `<body>` al cargar la página
  (`static/src/js/retana_theme.js`), como gancho para estilos condicionales.

## Compatibilidad

- **Odoo:** 19.0
- **Depende de:** `base`, `web`

## Notas de la migración 17 → 19

- Se normalizó la versión del manifest al formato estándar de Odoo
  (`19.0.1.0.0`) — antes era `17.0.0.1`, que no sigue la convención de 5
  segmentos `serie.mayor.menor.parche`.
- Se removieron imports de `@odoo/owl` (`Component`, `onMounted`) que no se usaban:
  el archivo no define un componente OWL, solo JS plano que se ejecuta en
  `DOMContentLoaded`.
- Se eliminó `static/src/css/retana_dark_theme copy.css`, un archivo de respaldo
  desactualizado que no estaba referenciado en ningún lado y quedó versionado por error.
- No requirió cambios de sintaxis de vistas ni de seguridad (no define ninguna).

## Instalación

Este módulo no tiene modelos ni vistas propias; solo se activa desde
**Ajustes → Apps** como cualquier módulo instalable de Odoo.
