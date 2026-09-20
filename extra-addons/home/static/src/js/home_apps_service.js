/** @odoo-module **/

import { registry } from "@web/core/registry";
import { reactive } from "@odoo/owl";

/**
 * Guarda los accesos configurados en el Home (ya filtrados por permisos para el usuario
 * actual) para que el selector de aplicaciones del navbar muestre lo mismo que el Home.
 *
 * state.apps es null si no se pudieron cargar; el navbar usa entonces la lista nativa.
 */
export const homeAppsService = {
    dependencies: ["orm"],

    async start(env, { orm }) {
        const state = reactive({ apps: null });
        try {
            const data = await orm.call("home.home", "get_home_data", []);
            state.apps = data.apps;
        } catch (error) {
            // Un fallo aquí no debe impedir que arranque el cliente web
            console.error("Home: no se pudieron cargar los accesos para el navbar", error);
        }
        return {
            state,
            /** Lo usa el dashboard del Home para mantener el navbar al día tras cambios. */
            update(apps) {
                state.apps = apps;
            },
        };
    },
};

registry.category("services").add("home.apps", homeAppsService);
