/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Botón de la barra superior para volver al Home desde cualquier aplicación.
 */
export class HomeSystrayButton extends Component {
    static template = "home.HomeSystrayButton";

    setup() {
        this.action = useService("action");
    }

    openHome() {
        return this.action.doAction("home.action_home_home_dashboard", { clearBreadcrumbs: true });
    }
}

registry.category("systray").add("home.HomeSystrayButton", { Component: HomeSystrayButton }, { sequence: 100 });
