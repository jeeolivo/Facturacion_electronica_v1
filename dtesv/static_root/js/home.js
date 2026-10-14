// Función para mostrar la fecha y hora actual
function mostrarFechaHora() {
    // Obtén el elemento donde deseas mostrar la fecha y hora
    var fechaHoraElement = document.getElementById('fecha-hora');

    // Obtén la fecha y hora actual
    var fechaHoraActual = new Date();

    // Formatea la fecha y hora como desees
    var formatoFechaHora = fechaHoraActual.toLocaleString(); // Formato por defecto

    // Actualiza el contenido del elemento con la fecha y hora actual
    fechaHoraElement.textContent = 'Fecha y Hora Actual: ' + formatoFechaHora;
}

// Llama a la función para mostrar la fecha y hora actual cuando se cargue la página
document.addEventListener('DOMContentLoaded', function() {
    //mostrarFechaHora();

    // Llama a la función para actualizar la fecha y hora cada segundo
   // setInterval(mostrarFechaHora, 1000);
});
