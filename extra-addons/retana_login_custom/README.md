# Retana Custom Login

Personaliza la pantalla de inicio de sesión (login) y de verificación en dos
pasos (2FA) de Electricos Retana.

## Qué hace

- Hereda la plantilla `web.login` y le agrega la clase `retana-login-form` al
  formulario, y oculta el botón `redirect` ("Log in as superuser").
- Hereda `auth_totp.auth_totp_form` (formulario de verificación 2FA) para
  aplicarle el mismo estilo.
- Agrega una hoja de estilos (`static/src/scss/login.scss`) al bundle
  `web.assets_frontend` con un diseño oscuro para la página de login, incluyendo
  el contenedor `oe_website_login_container` que aporta el módulo `website` al
  envolver el login con el layout del sitio.

## Compatibilidad

- **Odoo:** 19.0
- **Depende de:** `base`, `website`, `web`, `auth_totp`

## Notas de la migración 17 → 19

- Se normalizó la versión del manifest a `19.0.1.0.0` (antes decía `18.1.0`,
  inconsistente con la serie de Odoo realmente instalada en producción, 17.0).
- Se verificaron contra el código fuente real de Odoo 19.0 (rama `19.0` de
  `odoo/odoo` en GitHub) los tres selectores de los que depende este módulo:
  - `web.login`: el `<form>` conserva la clase `oe_login_form` y el
    `<button name="redirect">` sigue existiendo — el xpath de
    `retana_login_templates.xml` no requiere cambios.
  - `auth_totp.auth_totp_form`: el `<div class="oe_login_form">` se mantiene
    igual — el xpath tampoco requiere cambios.
  - `website.login_layout` (que hereda `web.login_layout`) sigue envolviendo el
    login en un `<div class="oe_website_login_container">` cuando `website`
    está instalado — el selector de `login.scss` sigue siendo válido.
- No se detectaron cambios de sintaxis o de estructura que afecten a este
  módulo en la migración a 19.0.

## Instalación

Sin modelos propios. Se activa desde **Ajustes → Apps**; requiere que
`website` y `auth_totp` estén instalados para que ambas plantillas hereden
correctamente.
