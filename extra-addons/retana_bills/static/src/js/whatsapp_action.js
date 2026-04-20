/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * Cliente de acción personalizada para descargar PDF y abrir WhatsApp
 */
registry.category("actions").add("download_and_open_whatsapp", async (env, action) => {
    const { download_url, download_name, whatsapp_url } = action.params;
    
    // Crear un enlace temporal para descargar el PDF
    const downloadLink = document.createElement('a');
    downloadLink.href = download_url;
    downloadLink.download = download_name || 'reporte.pdf';
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    
    // Iniciar la descarga
    downloadLink.click();
    
    // Esperar un momento para que la descarga inicie
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Abrir WhatsApp Web en una nueva pestaña
    window.open(whatsapp_url, '_blank');
    
    // Limpiar el enlace temporal
    document.body.removeChild(downloadLink);
    
    // Mostrar notificación al usuario
    env.services.notification.add(
        'El PDF se está descargando. Adjúntalo manualmente en WhatsApp Web.',
        {
            type: 'info',
            title: 'Descarga en proceso',
        }
    );
});
