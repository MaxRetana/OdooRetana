/** @odoo-module **/

import { registry } from "@web/core/registry";

function assertCardCount(expected) {
    return () => {
        const count = document.querySelectorAll(".o_home_dashboard .app-card").length;
        if (count !== expected) {
            throw new Error(`Se esperaban ${expected} tarjetas y hay ${count}`);
        }
    };
}

registry.category("web_tour.tours").add("home_dashboard_tour", {
    test: true,
    steps: () => [
        {
            content: "Solo se muestran los accesos permitidos para el usuario",
            trigger: ".o_home_dashboard .app-card:contains('Ajustes Test')",
            run: assertCardCount(2),
        },
        {
            content: "Ctrl+tecla no roba el foco hacia el buscador",
            trigger: ".o_home_dashboard input",
            run: () => {
                const input = document.querySelector(".o_home_dashboard input");
                input.blur();
                document.body.dispatchEvent(
                    new KeyboardEvent("keydown", { key: "c", ctrlKey: true, bubbles: true })
                );
                if (document.activeElement === input) {
                    throw new Error("Ctrl+C no debe enfocar el buscador");
                }
            },
        },
        {
            content: "Escribir una letra en cualquier parte enfoca el buscador",
            trigger: ".o_home_dashboard input",
            run: () => {
                const input = document.querySelector(".o_home_dashboard input");
                document.body.dispatchEvent(new KeyboardEvent("keydown", { key: "a", bubbles: true }));
                if (document.activeElement !== input) {
                    throw new Error("Una letra debe enfocar el buscador");
                }
            },
        },
        {
            content: "Buscar filtra las aplicaciones",
            trigger: ".o_home_dashboard input",
            run: "text Aplicaciones",
        },
        {
            content: "Solo queda la aplicacion buscada",
            trigger: ".o_home_dashboard .app-card:contains('Aplicaciones Test')",
            run: assertCardCount(1),
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

registry.category("web_tour.tours").add("home_dashboard_member_tour", {
    test: true,
    steps: () => [
        {
            content: "Un miembro del grupo ve tambien los accesos restringidos",
            trigger: ".o_home_dashboard .app-card:contains('Grupo Restringido Test')",
            run: assertCardCount(4),
        },
    ],
});
