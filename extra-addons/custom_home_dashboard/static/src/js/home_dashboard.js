/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class HomeDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.state = useState({
            apps: [],
            loading: true,
            error: false
        });
        
        onMounted(() => {
            this.loadApps();
        });
    }

    async loadApps() {
        try {
            this.state.loading = true;
            this.state.error = false;
            
            const apps = await this.orm.call(
                'home.dashboard',
                'get_installed_apps',
                []
            );
            
            this.state.apps = apps;
            this.state.loading = false;
            
        } catch (error) {
            console.error('Error loading apps:', error);
            this.state.error = true;
            this.state.loading = false;
        }
    }

    async openApp(app) {
        try {
            if (app.menu_id) {
                // Method 1: Try using the menu service
                const menuService = this.env.services.menu;
                if (menuService) {
                    await menuService.selectMenu(app.menu_id);
                    return;
                }
                
                // Method 2: Use action service with menu action
                await this.actionService.doAction({
                    type: 'ir.actions.client',
                    tag: 'menu',
                    params: {
                        menu_id: app.menu_id
                    }
                });
            } else {
                // Fallback: Search for the app's main action
                console.warn('No menu found for app:', app.name);
                await this.openAppBySearch(app);
            }
        } catch (error) {
            console.error('Error opening app:', error);
            // Last resort: try to navigate using window location
            this.openAppByUrl(app);
        }
    }

    async openAppBySearch(app) {
        try {
            // Try to find and execute the app's main action
            const actions = await this.orm.searchRead(
                'ir.actions.act_window',
                [['name', 'ilike', app.name]],
                ['id', 'name', 'res_model', 'view_mode'],
                { limit: 1 }
            );
            
            if (actions.length > 0) {
                await this.actionService.doAction(actions[0].id);
            }
        } catch (error) {
            console.error('Error in openAppBySearch:', error);
        }
    }

    openAppByUrl(app) {
        // Last resort: navigate using URL
        if (app.menu_id) {
            window.location.href = `/web#menu_id=${app.menu_id}`;
        }
    }

    getAppIcon(app) {
        // If the app has a web_icon, use it
        if (app.web_icon) {
            return app.web_icon;
        }
        
        // Otherwise use the FontAwesome icon
        return `fa ${app.icon}`;
    }
}

HomeDashboard.template = "custom_home_dashboard.HomeDashboard";

registry.category("actions").add("home_dashboard", HomeDashboard);