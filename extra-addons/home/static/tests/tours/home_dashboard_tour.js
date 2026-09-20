/** @odoo-module **/

import { registry } from "@web/core/registry";

function assertCardCount(expected) {
    return () => {
        const count = document.querySelectorAll(".o_home_dashboard .o_home_app_card").length;
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
            trigger: ".o_home_dashboard .o_home_app_card:contains('Configuración Test')",
            run: () => {
                assertCardCount(2)();
                const links = document.querySelectorAll(".o_home_dashboard a.o_home_app_card[href^='/web#menu_id=']");
                if (links.length !== 2) {
                    throw new Error("Las tarjetas deben ser enlaces con el menu de destino");
                }
                const icon = document.querySelector(".o_home_app_card .o_home_app_icon");
                if (getComputedStyle(icon).backgroundColor !== "rgb(255, 0, 0)") {
                    throw new Error("El icono debe usar el color configurado");
                }
            },
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
            content: "La busqueda ignora acentos y mayusculas",
            trigger: ".o_home_dashboard input",
            run: "text CONFIGURACION",
        },
        {
            content: "Solo queda la tarjeta con acento",
            trigger: ".o_home_dashboard .o_home_app_card:contains('Configuración Test')",
            run: assertCardCount(1),
        },
        {
            content: "Sin coincidencias se muestra un mensaje",
            trigger: ".o_home_dashboard input",
            run: "text zzzz",
        },
        {
            content: "Mensaje de sin resultados",
            trigger: ".o_home_dashboard .o_home_no_results:contains('zzzz')",
            run: assertCardCount(0),
        },
        {
            content: "Escape limpia la busqueda",
            trigger: ".o_home_dashboard input",
            run: () => {
                document
                    .querySelector(".o_home_dashboard input")
                    .dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
            },
        },
        {
            content: "Vuelven a verse todas las tarjetas",
            trigger: ".o_home_dashboard .o_home_app_card:contains('Aplicaciones Test')",
            run: assertCardCount(2),
        },
        {
            content: "Buscar resalta el primer resultado",
            trigger: ".o_home_dashboard input",
            run: "text aplic",
        },
        {
            content: "El resultado resaltado es la unica tarjeta",
            trigger: ".o_home_dashboard .o_home_app_card.o_home_app_active:contains('Aplicaciones Test')",
            run: assertCardCount(1),
        },
        {
            content: "Enter abre la aplicacion resaltada",
            trigger: ".o_home_dashboard input",
            run: () => {
                document
                    .querySelector(".o_home_dashboard input")
                    .dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
            },
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
            trigger: ".o_home_dashboard .o_home_app_card:contains('Grupo Restringido Test')",
            run: assertCardCount(4),
        },
    ],
});

registry.category("web_tour.tours").add("home_dashboard_empty_tour", {
    test: true,
    steps: () => [
        {
            content: "Sin accesos se muestra el estado vacio con boton para el administrador",
            trigger: ".o_home_dashboard .o_home_empty button:contains('Configurar accesos')",
            run: "click",
        },
        {
            content: "Se abre la configuracion",
            trigger: ".o_action_manager:not(:has(.o_home_dashboard)) .o_control_panel",
            run: () => {},
        },
    ],
});

registry.category("web_tour.tours").add("home_dashboard_link_tour", {
    test: true,
    steps: () => [
        {
            content: "El enlace de una tarjeta abre directamente la aplicacion",
            trigger: ".o_action_manager:not(:has(.o_home_dashboard)) .o_control_panel",
            run: () => {},
        },
    ],
});
