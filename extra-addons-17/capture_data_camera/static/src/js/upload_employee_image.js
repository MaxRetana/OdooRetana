function ensureSwalLoaded(callback) {
    if (typeof Swal !== 'undefined') {
        callback();
    } else {
        var script = document.createElement('script');
        script.src = "https://cdn.jsdelivr.net/npm/sweetalert2@11";
        script.onload = callback;
        document.head.appendChild(script);
    }
}

function uploadEmployeeImage() {
    ensureSwalLoaded(function() {
        // Crear input file para imágenes
        var input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.style.display = 'none';

        input.onchange = function(e) {
            var file = e.target.files[0];
            if (file) {
                // Leer archivo como base64
                var reader = new FileReader();
                reader.onload = function(event) {
                    var base64Data = event.target.result.split(',')[1];

                    // Llamada AJAX al backend Odoo (sin ID de empleado)
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', '/web/dataset/call_kw/hr.employee/upload_image_temp', true);
                    xhr.setRequestHeader('Content-Type', 'application/json');

                    var data = {
                        jsonrpc: "2.0",
                        method: "call",
                        params: {
                            model: 'hr.employee',
                            method: 'upload_image_temp',
                            args: [],
                            kwargs: {
                                file: base64Data
                            },
                            context: {
                                'active_model': 'hr.employee'
                            }
                        }
                    };

                    xhr.onreadystatechange = function() {
                        if (xhr.readyState === 4) {
                            if (xhr.status === 200) {
                                try {
                                    const response = JSON.parse(xhr.responseText);
                                    if (response.result) {
                                        Swal.fire({
                                            icon: "success",
                                            title: "¡Datos procesados!",
                                            text: "La imagen fue enviada y procesada correctamente.",
                                            showConfirmButton: true
                                        });
                                    } else {
                                        Swal.fire({
                                            icon: "error",
                                            title: "Error",
                                            text: "No se pudo procesar la imagen.",
                                            showConfirmButton: true
                                        });
                                    }
                                } catch (e) {
                                    Swal.fire({
                                        icon: "error",
                                        title: "Error",
                                        text: "Error parseando respuesta del servidor.",
                                        showConfirmButton: true
                                    });
                                }
                            } else {
                                Swal.fire({
                                    icon: "error",
                                    title: "Error",
                                    text: `Error de conexión: ${xhr.status}`,
                                    showConfirmButton: true
                                });
                            }
                        }
                    };

                    xhr.send(JSON.stringify(data));
                };
                reader.onerror = function() {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: "No se pudo leer el archivo.",
                        showConfirmButton: true
                    });
                };
                reader.readAsDataURL(file);
            }
        };

        document.body.appendChild(input);
        input.click();
        document.body.removeChild(input);
    });
}