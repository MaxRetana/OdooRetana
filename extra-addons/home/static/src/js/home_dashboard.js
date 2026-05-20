/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class HomeDashboard extends Component {
    static template = "home.HomeDashboardMain";

    setup() {
        this.action = useService("action");
        this.menu = useService("menu");
        this.orm = useService("orm");
        this.searchInputRef = useRef("searchInput"); // Referencia para el input
        this.boundWindowKeydown = this.onWindowKeydown.bind(this);
        
        this.state = useState({ 
            apps: [],
            searchTerm: "",
        });

        onWillStart(async () => {
            try {
                this.state.apps = await this.orm.searchRead(
                    "home.home", 
                    [], 
                    ["id", "name", "fa_icon", "custom_icon", "icon_type", "menu_id", "action_id"]
                );
            } catch (error) {
                console.error("Error al cargar aplicaciones:", error);
            }
        });

        // Detectar teclado globalmente
        onMounted(() => {
            window.addEventListener("keydown", this.boundWindowKeydown);
        });

        onWillUnmount(() => {
            window.removeEventListener("keydown", this.boundWindowKeydown);
        });
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
        const menuId = Array.isArray(app.menu_id) ? app.menu_id[0] : app.menu_id;
        if (menuId) {
            await this.menu.selectMenu(menuId);
        }
    }
}

registry.category("actions").add("home_home_dashboard", HomeDashboard);