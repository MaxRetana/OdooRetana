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

- `docker-compose.yaml` — producción (Odoo 19.0, detrás de nginx). Usa `config/prod.conf` y `nginx/nginx.conf`, y su propio volumen de PostgreSQL, `odoo_data` y filestore (`odoo-filestore-19/`).
- `docker-compose-17.yaml` — copia de la producción anterior (Odoo 17.0). Usa `config/prod-17.conf` y `nginx/nginx-17.conf`, con sus volúmenes originales.
- `docker-compose-local.yaml` / `docker-compose-test.yaml` — desarrollo/prueba local (Odoo 17.0).
- `docker-compose-19.yaml` — desarrollo local contra Odoo 19.0 (base de datos vacía, sin datos reales — ver [ADR 0002](docs/decisions/0002-porting-de-codigo-primero-datos-despues.md)).

### Cambio de producción 17 → 19

Los dos stacks de producción publican los puertos 80/443, así que no pueden
correr a la vez:

```bash
docker compose -f docker-compose-17.yaml down      # baja la producción 17 (no borra volúmenes)
docker compose up -d                               # levanta la producción 19
```

Para volver atrás: `docker compose down` y `docker compose -f docker-compose-17.yaml up -d`.
La base de datos de 19 empieza vacía en su propio volumen: restaura ahí la base
migrada y copia su filestore a `odoo-filestore-19/<nombre_de_la_base>/`.

## Documentación

Ver [`docs/`](docs/) para el plan de migración completo, el checklist
técnico por módulo y el registro de decisiones (ADRs).
