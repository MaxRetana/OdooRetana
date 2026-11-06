/** @odoo-module **/

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { session } from "@web/session";

// Servicio que verifica el modo mantenimiento
const maintenanceCheckService = {
    dependencies: ["rpc"],
    
    async start(env, { rpc }) {
        console.log("🔧 Servicio de mantenimiento iniciado");
        
        // Verificar el modo mantenimiento
        const checkMaintenance = async () => {
            try {
                // Verificar si el usuario tiene permisos de sistema
                const hasSystemGroup = session.user_companies && 
                                      session.is_system === true;
                
                // Si el usuario YA es administrador, no hacer nada
                if (hasSystemGroup) {
                    console.log("👤 Usuario administrador - no verificar mantenimiento");
                    return;
                }
                
                console.log("🔍 Verificando modo mantenimiento...");
                
                // Obtener el parámetro de configuración
                const maintenanceEnabled = await rpc("/web/dataset/call_kw", {
                    model: "ir.config_parameter",
                    method: "get_param",
                    args: ["maintenance_odoo_retana.maintenance_mode_enabled"],
                    kwargs: {},
                });
                
                console.log("📊 Modo mantenimiento:", maintenanceEnabled);
                
                // Si el modo está activo, redirigir
                if (maintenanceEnabled === 'True') {
                    console.log("⚠️ Modo mantenimiento ACTIVO - redirigiendo...");
                    browser.location.href = "/web/maintenance";
                }
            } catch (error) {
                console.error("❌ Error verificando mantenimiento:", error);
            }
        };
        
        // Verificar INMEDIATAMENTE al cargar
        checkMaintenance();
        
        // Verificar cada 5 segundos
        setInterval(checkMaintenance, 5000);
    },
};

registry.category("services").add("maintenance_check", maintenanceCheckService);
