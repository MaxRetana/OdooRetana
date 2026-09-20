/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class HomeDashboard extends Component {
    static template = "home.HomeDashboardMain";

    setup() {
        this.menu = useService("menu");
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.searchInputRef = useRef("searchInput"); // Referencia para el input
        this.boundWindowKeydown = this.onWindowKeydown.bind(this);
        
        this.state = useState({ 
            apps: [],
            canConfigure: false,
            loadError: false,
            searchTerm: "",
        });

        onWillStart(() => this.loadApps());

        // Detectar teclado globalmente
        onMounted(() => {
            window.addEventListener("keydown", this.boundWindowKeydown);
        });

        onWillUnmount(() => {
            window.removeEventListener("keydown", this.boundWindowKeydown);
        });
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
        const inputEl = this.searchInputRef && this.searchInputRef.el;
        if (!inputEl) {
            return;
        }

        // Si el usuario presiona una tecla alfanumérica y no está ya en el input
        if (ev.key.length === 1 && document.activeElement !== inputEl) {
            inputEl.focus();
        }
    }

    get filteredApps() {
        const term = this.state.searchTerm.toLowerCase().trim();
        if (!term) return this.state.apps;
        return this.state.apps.filter(app => app.name.toLowerCase().includes(term));
    }

    onSearchInput(ev) {
        this.state.searchTerm = ev.target.value;
    }

    async openApp(app) {
        if (app.menu_id) {
            await this.menu.selectMenu(app.menu_id);
        }
    }
}

registry.category("actions").add("home_home_dashboard", HomeDashboard);