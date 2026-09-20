/** @odoo-module **/

import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

const HOME_MENU_XMLID = "home.menu_home_home_root";

patch(NavBar.prototype, {
    setup() {
        super.setup(...arguments);
        this.homeAppsState = useState(useService("home.apps").state);
    },

    /**
     * Aplicaciones del selector del navbar: las configuradas en el Home, con su nombre y
     * orden, y siempre el propio Home primero para poder volver. Si no hay accesos
     * configurados (o no cargaron) se conserva la lista nativa de Odoo.
     */
    get homeApps() {
        const nativeApps = this.menuService.getApps();
        const shortcuts = this.homeAppsState.apps;
        if (!shortcuts || !shortcuts.length) {
            return nativeApps;
        }
        const homeMenu = nativeApps.find((menu) => menu.xmlid === HOME_MENU_XMLID);
        const apps = homeMenu ? [homeMenu] : [];
        for (const shortcut of shortcuts) {
            const menu = this.menuService.getMenu(shortcut.menu_id);
            if (menu && (!homeMenu || menu.id !== homeMenu.id)) {
                apps.push({ ...menu, name: shortcut.name });
            }
        }
        return apps;
    },

    isCurrentApp(app) {
        const currentApp = this.menuService.getCurrentApp();
        return Boolean(currentApp) && currentApp.id === app.id;
    },
});
