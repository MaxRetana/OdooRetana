/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";

// Funcionalidades adicionales para el tema oscuro Retana
class RetanaDarkTheme {
    constructor() {
        this.initTheme();
    }

    initTheme() {
        // Aplicar clases adicionales al body cuando se carga el tema
        document.body.classList.add('retana-dark-theme');
        
        // Detectar preferencia del sistema (opcional)
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            console.log('Sistema en modo oscuro detectado - Tema Retana aplicado');
        }
    }

    // Método para alternar entre tema claro y oscuro (funcionalidad futura)
    toggleTheme() {
        document.body.classList.toggle('retana-dark-theme');
    }
}

// Inicializar el tema cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    new RetanaDarkTheme();
});

// Exportar para uso en otros módulos si es necesario
export { RetanaDarkTheme };
