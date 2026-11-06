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
            
            console.log('Loaded apps:', apps);
            this.state.apps = apps;
            this.state.loading = false;
            
        } catch (error) {
            console.error('Error loading apps:', error);
            this.state.error = true;
            this.state.loading = false;
        }
    }

    async openApp(app) {
        console.log('=== Opening app ===');
        console.log('App data:', app);
        console.log('Menu ID:', app.menu_id);
        console.log('Action type:', app.action_type);
        
        try {
            // Special handling for Apps menu
            if (app.action_type === 'apps_store') {
                console.log('Opening apps store...');
                await this.actionService.doAction('base.open_module_tree');
                return;
            }
            
            if (app.menu_id) {
                console.log('Attempting to open menu with ID:', app.menu_id);
                
                // Get the action associated with this menu
                const menuAction = await this.orm.call(
                    'ir.ui.menu',
                    'read',
                    [[app.menu_id], ['action']]
                );
                
                console.log('Menu action:', menuAction);
                
                if (menuAction && menuAction[0] && menuAction[0].action) {
                    const actionString = menuAction[0].action;
                    const actionId = parseInt(actionString.split(',')[1]);
                    console.log('Executing action ID:', actionId);
                    await this.actionService.doAction(actionId);
                } else {
                    // Try direct URL navigation
                    console.log('No action found, using URL navigation');
                    window.location.href = `/web#menu_id=${app.menu_id}`;
                }
            } else {
                // Fallback: Search for the app's main action
                console.warn('No menu found for app:', app.name);
                await this.openAppBySearch(app);
            }
        } catch (error) {
            console.error('Error opening app:', error);
            console.error('Error details:', error.message, error.stack);
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