/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("home_dashboard_tour", {
    test: true,
    steps: () => [
        {
            content: "El dashboard muestra las tarjetas configuradas",
            trigger: ".o_home_dashboard .app-card:contains('Ajustes Test')",
            run: () => {},
        },
        {
            content: "Buscar filtra las aplicaciones",
            trigger: ".o_home_dashboard input",
            run: "text Aplicaciones",
        },
        {
            content: "Solo queda la aplicacion buscada",
            trigger: ".o_home_dashboard .app-card:contains('Aplicaciones Test')",
            run: () => {
                if (document.querySelectorAll(".o_home_dashboard .app-card").length !== 1) {
                    throw new Error("Se esperaba una sola tarjeta tras filtrar");
                }
            },
        },
        {
            content: "Abrir la aplicacion navega fuera del dashboard",
            trigger: ".o_home_dashboard .app-card:contains('Aplicaciones Test')",
            run: "click",
        },
        {
            content: "El dashboard desaparece al abrir la app",
            trigger: "body:not(:has(.o_home_dashboard))",
            run: () => {},
        },
    ],
});
