/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useEffect, useExternalListener, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";

// Normaliza para comparar sin importar mayúsculas ni acentos ("Configuración" -> "configuracion")
function normalize(text) {
    return (text || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

export class HomeDashboard extends Component {
    static template = "home.HomeDashboardMain";

    setup() {
        this.action = useService("action");
        this.menu = useService("menu");
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.searchInputRef = useRef("searchInput"); // Referencia para el input

        this.state = useState({ 
            apps: [],
            canConfigure: false,
            loadError: false,
            searchTerm: "",
            activeIndex: -1, // tarjeta resaltada con el teclado (-1: ninguna)
        });

        onWillStart(() => this.loadApps());

        // Mantener a la vista la tarjeta resaltada al navegar con el teclado
        useEffect(
            () => {
                const card = document.querySelector(".o_home_dashboard .o_home_app_active");
                card?.scrollIntoView({ block: "nearest" });
            },
            () => [this.state.activeIndex]
        );

        // Detectar teclado globalmente (owl lo desregistra solo al destruir el componente)
        useExternalListener(window, "keydown", this.onWindowKeydown);
    }

    get userFirstName() {
        return (session.name || "").split(" ")[0];
    }

    async loadApps() {
        try {
            const data = await this.orm.call("home.home", "get_home_data", []);
            this.state.apps = data.apps;
            this.state.canConfigure = data.can_configure;
            this.state.loadError = false;
        } catch (error) {
            console.error("Error al cargar aplicaciones:", error);
            this.state.loadError = true;
            this.notification.add(_t("No se pudieron cargar las aplicaciones."), {
                type: "danger",
            });
        }
    }

    iconClass(app) {
        return app.icon_type === "fontawesome" && app.fa_icon ? app.fa_icon : "fa-th-large";
    }

    onWindowKeydown(ev) {
        const inputEl = this.searchInputRef.el;
        if (!inputEl || ev.defaultPrevented) {
            return;
        }
        // Respetar atajos del navegador/sistema (Ctrl+C, Cmd+R, Alt+...) y teclas no imprimibles
        const isNavigationKey = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(ev.key);
        if (ev.ctrlKey || ev.metaKey || ev.altKey || (ev.key.length !== 1 && !isNavigationKey)) {
            return;
        }
        // No robar el foco si el usuario ya escribe en otro campo o hay un diálogo abierto
        const target = ev.target;
        if (target !== inputEl && target instanceof Element) {
            const isEditable =
                target.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName);
            if (isEditable || target.closest(".modal")) {
                return;
            }
        }
        inputEl.focus();
    }

    get filteredApps() {
        const term = normalize(this.state.searchTerm);
        if (!term) return this.state.apps;
        return this.state.apps.filter((app) => normalize(app.name).includes(term));
    }

    onSearchInput(ev) {
        this.state.searchTerm = ev.target.value;
        // Al buscar se resalta el primer resultado, para abrirlo con Enter
        this.state.activeIndex = normalize(this.state.searchTerm) ? 0 : -1;
    }

    onSearchKeydown(ev) {
        const count = this.filteredApps.length;
        switch (ev.key) {
            case "ArrowRight":
            case "ArrowDown":
                ev.preventDefault();
                if (count) {
                    this.state.activeIndex = Math.min(this.state.activeIndex + 1, count - 1);
                }
                break;
            case "ArrowLeft":
            case "ArrowUp":
                ev.preventDefault();
                if (count) {
                    this.state.activeIndex = Math.max(this.state.activeIndex - 1, 0);
                }
                break;
            case "Enter": {
                const app = this.filteredApps[this.state.activeIndex];
                if (app) {
                    ev.preventDefault();
                    this.openApp(app);
                }
                break;
            }
            case "Escape":
                this.state.searchTerm = "";
                this.state.activeIndex = -1;
                break;
        }
    }

    async syncApps() {
        await this.orm.call("home.home", "action_sync_apps", [[]]);
        await this.loadApps();
    }

    openConfiguration() {
        return this.action.doAction("home.action_home_home_config");
    }

    appUrl(app) {
        // Igual que el navbar de Odoo: sin "action", la acción de inicio del usuario
        // (que puede ser este mismo Home) tendría prioridad sobre el menú.
        const menu = this.menu.getMenu(app.menu_id);
        const parts = [`menu_id=${app.menu_id}`];
        if (menu && menu.actionID) {
            parts.push(`action=${menu.actionID}`);
        }
        return `/web#${parts.join("&")}`;
    }

    onAppClick(ev, app) {
        // Con Ctrl/Cmd/Shift se deja al navegador abrir el enlace en otra pestaña o ventana
        if (ev.ctrlKey || ev.metaKey || ev.shiftKey) {
            return;
        }
        ev.preventDefault();
        this.openApp(app);
    }

    async openApp(app) {
        if (app.menu_id) {
            await this.menu.selectMenu(app.menu_id);
        }
    }
}

registry.category("actions").add("home_home_dashboard", HomeDashboard);