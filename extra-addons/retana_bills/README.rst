============================
Electricos Retana (retana_bills)
============================

.. |badge1| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

|badge1|

Módulo principal de negocio: gestiona presupuestos, anticipos, obras y
clientes de Electricos Retana, con reportes PDF, envío por WhatsApp y
widgets propios. Es el módulo más grande y de mayor riesgo del repositorio.

**Tabla de contenidos**

.. contents::
   :local:

Qué hace
========

- **Presupuestos** (``retana.budget`` + ``retana.budget.line``): líneas con
  secciones/notas, cálculo de subtotal/IVA/descuento/total, reporte PDF.
- **Anticipos** (``retana.downpayment``): registro individual, con
  secuencia automática (``RD0001``, ``RD0002``, ...) y reporte de recibo en
  PDF.
- **Anticipos masivos** (wizard ``retana.bulk.downpayment.wizard``, con
  lógica compartida en el mixin ``retana.bulk.downpayment.mixin``): pega un
  mensaje de texto tipo ``$3000 nombre_obra, concepto`` por línea y crea
  varios anticipos a la vez, con matching difuso de nombres de obra (exacto
  → normalizado → por tokens) y marcado de líneas que necesitan revisión
  manual.
- **Obras** (``retana.buildings``) y **clientes** (extensión de
  ``res.partner`` con ``is_retana_customer`` / ``retana.type.res.partner``).
- **Envío por WhatsApp** (``retana.sent.wh`` + wizard
  ``retana.send.whatsapp.wizard``): genera el link de WhatsApp Web con el
  PDF del reporte adjunto manualmente.
- Widget OWL propio ``retana_bills.amount_selector``: grid de montos
  rápidos para el campo de importe de anticipo.
- Tracking de cambios (vía ``field_tracking_mixin``) en presupuestos,
  obras, tipos de cliente y agenda de WhatsApp.

Compatibilidad
===============

- Odoo: 19.0
- Depende de: ``base``, ``mail``, ``field_tracking_mixin``, ``account``, ``product``

Notas de la migración 17 → 19
==============================

Cambios de compatibilidad, todos verificados contra el código fuente de
``odoo/odoo`` rama ``19.0``:

- **``<tree>`` → ``<list>``** en las 11 vistas de lista del módulo
  (breaking change confirmado desde Odoo 18.0), incluyendo la subvista
  editable de líneas dentro del formulario de presupuesto. Se actualizaron
  también los ``view_mode`` de las acciones de ventana y de las ``views``
  devueltas por el wizard de anticipos masivos.
- **``attrs="..."`` → atributos directos** en
  ``views/retana_budget_views.xml`` (líneas de presupuesto): la sintaxis
  ``attrs``/``states`` ya lanza ``ValidationError`` **desde Odoo 17.0** (no
  es algo nuevo de 19.0), así que esto ya estaba roto de fondo en el
  código. Se convirtió a ``required="..."`` / ``column_invisible="..."``
  con expresiones Python directas.

Bugs preexistentes encontrados y corregidos de paso (no relacionados con el
salto de versión en sí, pero afectaban directamente la corrección del
tracking de cambios que ya se estaba revisando):

- **``retana_budgets.py``**: ``_tracked_fields`` usaba las claves
  ``'linea_ids'`` / ``'producto_id'``, que no existen en el modelo (los
  campos reales son ``line_ids`` / ``product_id``). Por ese typo, el
  tracking de líneas de presupuesto en el chatter nunca se disparó. Se
  corrigieron los nombres.

Otras observaciones (no requirieron cambios):

- ``data/retana_company_info_import.csv`` no está listado en el ``data``
  del manifest — parece un archivo de importación manual, suelto, que no
  carga el módulo. Se deja tal cual (no se borra sin confirmar con el
  negocio), pero se documenta aquí para que quede claro que no es parte del
  flujo normal del módulo.
- Los reportes QWeb (``report/*.xml``) usan ``web.html_container`` (layout
  base, sin cambios en 19.0) y no tienen sintaxis deprecada.
- El widget de campo propio (``retana_bills.amount_selector``) usa
  ``standardFieldProps`` de ``@web/views/fields/standard_field_props``,
  verificado que sigue existiendo igual en 19.0.

Todo el Python, XML y JS del módulo pasó ``python3 -m py_compile``,
``xmllint --noout`` y ``node --check`` (módulo ES) respectivamente.
**Pendiente**: correr los flujos completos (crear presupuesto, anticipo,
anticipo masivo, generar reportes PDF, enviar por WhatsApp) contra una base
Odoo 19.0 real una vez ``odev`` tenga el token de GitHub configurado.

Instalación
===========

Depende de ``field_tracking_mixin`` (debe instalarse junto o antes). Se
activa desde **Ajustes → Apps**; agrega el menú "Electricos Retana" con
Presupuestos, Anticipos y Configuración.

Autor
=====

MaxRetana
