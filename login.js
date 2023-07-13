
$(document).ready(function() {
    const apiUrl = "http://127.0.0.1:8080"; // URL de la API
    // Manejar el evento de envío del formulario de inicio de sesión
    $(apiUrl).submit(function(event) {
        event.preventDefault(); // Evitar el envío del formulario

        var username = $('#username').val().trim();

        if (username !== '') {
            // Enviar la solicitud de inicio de sesión al servidor
            $.ajax({
                url: '/login',
                type: 'POST',
                data: { username: username },
                success: function(data) {
                    window.location.href = '/web.html'; // Redirigir al usuario al chat
                },
                error: function(error) {
                    console.log('Error:', error);
                }
            });
        }
    });
});
