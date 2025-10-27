$(document).ready(function() {
    $('#submitBtn').on('click', function(event) {
        console.log("Botón de envío clickeado.");
        // Evita que el formulario se envíe de la manera tradicional
        event.preventDefault(); 
        
        const $form = $('#targetForm'); // El formulario actual
        const url = $form.attr('action') || window.location.href;
        
        // 2. Obtiene el CSRF Token de un campo oculto del formulario
        const csrftoken = $form.find('input[name="csrfmiddlewaretoken"]').val();
        

        // 3. Envía la solicitud POST usando jQuery.ajax()
        $.ajax({
            type: 'POST',
            url: url,
            data: $form.serialize(), // Serializa todos los datos del formulario (como un objeto Form Data simple)
            headers: {
                // Incluye el CSRF token en los encabezados
                'X-CSRFToken': csrftoken,
            },
            dataType: 'json', // Esperamos que la vista de Django devuelva JSON
            
            success: function(response) {
                if (response.result) {
                    swal("Registrado", response.message, "success");
                    window.location.href = response.to || window.location.href;
                } else {
                       window.alert("Error");
                    // Manejo de errores específicos devueltos por el servidor
                    swal("Error", response.message || 'Error desconocido del servidor.', "error");
                }
            },
            
            error: function(xhr, status, error) {
                // 5. Manejo de Errores
                console.error("Error al enviar el formulario:", status, error);
                
                // Intenta parsear el error JSON si está disponible
                try {
                    const errorData = JSON.parse(xhr.responseText);
                    console.error("Detalles del error de Django:", errorData);
                    alert(`Error: ${errorData.mensaje || 'Error desconocido del servidor.'}`);
                } catch (e) {
                    alert("Ocurrió un error al procesar la solicitud.");
                }
            }
        });
    });
});