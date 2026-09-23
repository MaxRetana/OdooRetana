# OdooRetana

Instancia Odoo self-hosted (Docker Compose) de Electricos Retana, con
módulos custom propios en [`extra-addons/`](extra-addons/).

## Estado

En migración de Odoo 17.0 a 19.0 — ver el plan completo y las decisiones
tomadas en [`docs/`](docs/).

## Módulos custom en alcance (Odoo 19.0)

| Módulo | Qué hace |
|---|---|
| [`home`](extra-addons/home/README.md) | Dashboard tipo "app launcher" para el backend |
| [`field_tracking_mixin`](extra-addons/field_tracking_mixin/README.md) | Mixin para trackear cambios en campos relacionales en el chatter |
| [`retana_bills`](extra-addons/retana_bills/README.md) | Presupuestos, anticipos, obras y clientes (módulo principal de negocio) |
| [`retana_bills_weekday_config`](extra-addons/retana_bills_weekday_config/README.md) | Configura el día por defecto de los anticipos |
| [`retana_custom`](extra-addons/retana_custom/README.md) | Theming (tema oscuro) del backend |
| [`retana_login_custom`](extra-addons/retana_login_custom/README.md) | Personalización de la pantalla de login/2FA |
| [`retana_web`](extra-addons/retana_web/README.md) | Sitio web público para consultar presupuestos/anticipos/obras |

Cada módulo tiene su propio `README.md` (arriba) y `README.rst` con el
detalle técnico. Los módulos que no estaban instalados en producción se
retiraron del repo — ver
[ADR 0001](docs/decisions/0001-retiro-modulos-legacy-no-instalados.md).

## Entornos

- `docker-compose.yaml` — producción (Odoo 17.0, detrás de nginx).
- `docker-compose-local.yaml` / `docker-compose-test.yaml` — desarrollo/prueba local (Odoo 17.0).
- `docker-compose-19.yaml` — desarrollo local contra Odoo 19.0 (base de datos vacía, sin datos reales — ver [ADR 0002](docs/decisions/0002-porting-de-codigo-primero-datos-despues.md)).

## Documentación

Ver [`docs/`](docs/) para el plan de migración completo, el checklist
técnico por módulo y el registro de decisiones (ADRs).
