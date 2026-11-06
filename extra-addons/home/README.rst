======
Home
======

.. |badge1| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

|badge1|

Dashboard tipo "app launcher" para el backend de Odoo de Electricos Retana:
muestra tarjetas con accesos directos a las aplicaciones instaladas, con
buscador, configuración de íconos/colores por acceso, y restricción por
grupo o compañía. Reemplaza la pantalla de inicio nativa de Odoo para los
usuarios internos.

**Tabla de contenidos**

.. contents::
   :local:

Qué hace
========

- **Modelo** ``home.home``: cada registro es un "acceso rápido" (nombre,
  ícono, color, menú raíz al que apunta, grupos permitidos, compañía). Trae
  una acción ``action_sync_apps`` que crea automáticamente un acceso por
  cada aplicación instalada que todavía no tenga uno.
- **Dashboard OWL** (``home.HomeDashboardMain``): tarjetas de las apps
  permitidas para el usuario actual, buscador con navegación por teclado
  (flechas, Enter, Escape), estados vacíos/de error.
- **Navbar**: parchea ``web.NavBar`` para que el selector de aplicaciones use
  los mismos accesos configurados en el Home (con su nombre personalizado),
  en vez de la lista nativa de apps.
- **Systray**: botón para volver al Home desde cualquier aplicación.
- **Override de** ``ir.http``: usa el Home como pantalla de inicio de los
  usuarios internos que no tengan una "Acción de inicio" propia en sus
  preferencias; desactivable con el parámetro de sistema
  ``home.use_as_landing``.
- Seguridad propia: grupos ``home.group_home_home_user`` (solo lectura) y
  ``home.group_home_home_admin`` (puede configurar accesos).
- Suite de tests: unitarios (``tests/test_home_data.py``,
  ``test_home_model.py``, ``test_home_security.py``) y tours de UI
  (``test_home_tour.py`` + ``static/tests/tours/home_dashboard_tour.js``).

Compatibilidad
===============

- Odoo: 19.0
- Depende de: ``base``, ``web``

Notas de la migración 17 → 19
==============================

Este fue el módulo de mayor riesgo del plan de migración (frontend OWL +
seguridad + tests). Cambios reales encontrados y corregidos, todos
verificados contra el código fuente de ``odoo/odoo`` rama ``19.0`` en
GitHub:

- **``<tree>`` → ``<list>``** (breaking change confirmado desde Odoo 18.0):
  el ``Selection`` de ``ir.ui.view.type`` ya no acepta ``'tree'``. Se
  renombró la vista de lista (``view_home_home_tree``) y el ``view_mode`` de
  la acción de configuración.
- **``res.groups.category_id`` → ``res.groups.privilege_id``**: cambio de
  arquitectura, no un simple rename. Ver `ADR 0003
  <../../docs/decisions/0003-migracion-a-res-groups-privilege.md>`_ para el
  detalle completo; en resumen, se agregó un registro
  ``res.groups.privilege`` nuevo y los dos grupos del módulo ahora apuntan a
  él en vez de a la categoría directamente.
- **``res.groups.users`` → ``res.groups.user_ids``** y **``res.users.groups_id``
  → ``res.users.group_ids``**: sin alias de compatibilidad. Se actualizó
  ``home_home.py`` (``get_home_data``) y los tests que asignan grupos a
  usuarios/menús de prueba.
- Se verificó explícitamente que **no cambiaron** (siguen igual en 19.0):

  - Las plantillas QWeb que hereda ``home_navbar.xml`` (``web.NavBar``, con
    ``<t t-set="apps">``, y ``web.NavBar.AppsMenu``, con ``<DropdownItem>``).
  - Las rutas de import de OWL/JS usadas (``@web/webclient/navbar/navbar``,
    ``@web/session``, ``@web/core/l10n/translation``, ``@odoo/owl``).
  - Los métodos ``ir.ui.menu._visible_menu_ids()`` y el campo
    ``ir.ui.menu.web_icon_data``, usados en los tests de seguridad.

- Todo el Python y XML del módulo pasó ``python3 -m py_compile`` /
  ``xmllint --noout``, y todo el JS pasó ``node --check`` (como módulo ES).
  **Esto no reemplaza correr la suite de tests real** (``odev test`` / los
  tours) contra una base Odoo 19.0: ``odev`` necesita un GitHub Personal
  Access Token configurado (``odev setup github``) para poder clonar el
  código fuente de Odoo 19.0 y levantar el worktree local — no estaba
  configurado al momento de este porting. Es el primer paso pendiente antes
  de dar este módulo por verificado en runtime.

Instalación
===========

Se activa desde **Ajustes → Apps**. Al instalarse, agrega el menú "Home"
(visible para todo usuario interno) como pantalla de inicio por defecto.

Autor
=====

MaxRetana
