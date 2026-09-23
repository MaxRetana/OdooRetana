===========================
Retana Bills Weekday Config
===========================

.. |badge1| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

|badge1|

Agrega una página en **Ajustes → Anticipos Retana** para configurar el día
de la semana que se usará por defecto como fecha en los wizards y modelos
de anticipos de ``retana_bills``.

**Tabla de contenidos**

.. contents::
   :local:

Qué hace
========

- Agrega el campo ``downpayment_weekday`` (selección Lunes–Domingo) a
  ``res.config.settings``, guardado como ``ir.config_parameter``
  (``retana_bills_weekday_config.downpayment_weekday``).
- Extiende tres modelos de ``retana_bills`` para que su campo ``date`` tome
  por defecto el próximo día de esa semana configurada:

  - ``retana.downpayment.wizard``
  - ``retana.bulk.downpayment.wizard``
  - ``retana.downpayment``

Compatibilidad
===============

- Odoo: 19.0
- Depende de: ``base``, ``retana_bills``

Notas de la migración 17 → 19
==============================

- Se normalizó la versión del manifest a ``19.0.1.0.0``.
- Se verificó contra el código fuente de Odoo 19.0 que los tags ``<app>``,
  ``<block>`` y ``<setting>`` de ``res.config.settings`` y el ancla
  ``//app[@name='general_settings']`` siguen existiendo sin cambios.
- **Refactor de buenas prácticas:** la lógica para calcular la fecha por
  defecto (``_get_configured_weekday`` / ``_get_default_saturday``) estaba
  duplicada, copiada y pegada casi textualmente (con indentación
  inconsistente), en los tres archivos de modelo. Se extrajo a un mixin
  nuevo, ``models/retana_weekday_default_mixin.py``
  (``retana.weekday.default.mixin``), y los tres modelos ahora lo heredan
  junto con su modelo original
  (``_inherit = ['<modelo>', 'retana.weekday.default.mixin']``). El
  comportamiento es idéntico al anterior; solo cambia dónde vive el código.
- Se removieron imports sin usar (``UserError``, ``api``) que quedaban en
  los tres archivos de modelo tras el refactor.

Instalación
===========

Requiere que ``retana_bills`` esté instalado. Se activa desde
**Ajustes → Apps**; la configuración queda disponible en
**Ajustes → Anticipos Retana**.

Autor
=====

MaxRetana
