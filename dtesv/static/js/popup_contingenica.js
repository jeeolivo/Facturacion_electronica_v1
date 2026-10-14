// popup.js

// Primero es necesario definir las variables globales
var tipoContingenciaSelect;
var guardarButton;
var errorMessage;
var popupContainer;

/* DEFINIENDO LAS FUNCIONES GLOBALES */
// Función para cargar los tipos de contingencia desde la vista Django
function loadTiposContingencia() {
  // Realizar una solicitud AJAX a la vista tipo_contingencia
  $.ajax({
    url: '/dtesv/home/tipo_contingencia',
    type: 'GET',
    dataType: 'json',
    success: function (data) {
      console.log('Tipos de contingencia cargados exitosamente');

      // Definir la variable tipoContingenciaSelect aquí
      tipoContingenciaSelect = document.getElementById('tipo-contingencia');
      // Limpiar el select actual
      tipoContingenciaSelect.innerHTML = '';

      // Iterar a través de los datos recibidos y agregar opciones al select
      for (var i = 0; i < data.tipos_contingencia.length; i++) {
        var option = document.createElement('option');
        option.value = data.tipos_contingencia[i].codigo;
        option.textContent = data.tipos_contingencia[i].valor;
        tipoContingenciaSelect.appendChild(option);
      }
    },
    error: function (error) {
      console.error('Error al cargar tipos de contingencia: ', error);
    }
  });
}


// Función para manejar el evento del botón btn-contingencia.
function manejarContingencia() {
  var popupContainer = document.getElementById('popup-container');
  // Aquí va tu lógica para manejar la contingencia
  console.log('Función manejarContingencia llamada');

  if (popupContainer) {
    // Mostrar el popup
    popupContainer.style.display = 'block';

    // Aquí puedes agregar cualquier otra lógica que necesites
    // por ejemplo, cargar datos específicos en el popup
    loadTiposContingencia();

    // Limpiar mensajes de error si existen
    var errorMessage = document.getElementById('error-message');
    if (errorMessage) {
      errorMessage.textContent = '';
    }
  } else {
    console.error('No se pudo encontrar el contenedor del popup');
  }
}

// Evento para guardar la contingencia
function addGuardarEventListener() {
  console.log('Función Guardar llamada');
  if (guardarButton) {
    guardarButton.addEventListener('click', function (event) {
      event.preventDefault();  // Previene la recarga de la página
      console.log('Event.preventDefault llamado. La recarga de la página debería estar prevenida.');

      // Obtener los valores de los campos del formulario
      var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
      var tipoContingencia = tipoContingenciaSelect.value;
      var motivoContingencia = document.getElementById('motivo-contingencia').value;
      var fecha_inicio = document.getElementById('fecha-inicio').value;
      var fecha_fin = document.getElementById('fecha-fin').value;
      var hora_ini = document.getElementById('hora-inicio').value;
      var hora_fin = document.getElementById('hora-fin').value;
      
      console.log('Valores capturados:', {
        tipoContingencia,
        motivoContingencia,
        fecha_inicio,
        fecha_fin,
        hora_ini,
        hora_fin
      });

      // Valida que los campos esten llenos
      if (!tipoContingencia || !motivoContingencia || !fecha_inicio || !fecha_fin || !hora_ini || !hora_fin) {
        errorMessage.textContent = 'Todos los campos son obligatorios.';
        return;
      }

      // Realiza la solicitud POST
      fetch('/dtesv/contingencia/' + tipoContingencia + '/' + motivoContingencia + '/' + fecha_inicio + '/' + fecha_fin + '/' + hora_ini + '/' + hora_fin, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
          tipoContingencia,
          motivoContingencia,
          fecha_inicio,
          fecha_fin,
          hora_ini,
          hora_fin
        }),
      })
        /// Manejo de la respuesta a la solicitud POST hecha por el fetch
        .then(function (response) {
          console.log('Respuesta Recibida:', response);
          if (!response.ok) {
            throw new Error('Error al guardar la contingencia');
          }
          return response.json();
        })
        .then(function (data) {
          //console.log('Datos recibidos', data)
          alert('contingencia guardada')
          console.log('Contingencia guardada con éxito:', data);
          // Ocultar el popup después de guardar
          if (popupContainer) {
            popupContainer.style.display = 'none';
          } else {
            console.error('No se pudo encontrar el contenedor del popup');
          }
        })
        .catch(function (error) {
          errorMessage.textContent = 'Error al guardar la contingencia: ' + error;
        });
    });
  } else {
    //alert('Error no existe btnGuardar en el DOM')
    console.error("El elemento con id 'btn-guardar' no existe en el DOM.");
  }
}

// Evento DOMContentLoaded para asegurar que el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
  console.log('DOMContentLoaded: El DOM está completamente cargado');

  popupContainer = document.getElementById('popup-container');
  //console.log(popupContainer ? 'popupContainer encontrado' : 'popupContainer no encontrado');

  var closeButton = document.getElementById('btn-cerrar');
  //console.log(closeButton ? 'btn-cerrar encontrado' : 'btn-cerrar no encontrado');

  guardarButton = document.getElementById('btn-guardar');
  //console.log(guardarButton ? 'btn-guardar encontrado' : 'btn-guardar no encontrado');

  var openButton = document.getElementById('contingencia-button');
  //console.log(openButton ? 'contingencia-button encontrado' : 'contingencia-button no encontrado');
  
  // Llamar a la función cuando se haga clic en btn-contingencia
  var crearContingencia = document.getElementById('btn-contingencia');
  if (crearContingencia) {
    crearContingencia.addEventListener('click', manejarContingencia);
  } else {
    //console.error('btn-contingencia no encontrado');
  }

  // Ocultar el popup al cargar la página
  if (popupContainer) {
    popupContainer.style.display = 'none';
  } else {
    //console.error('popupContainer no encontrado');
  }

  // Verificar si el botón existe antes de añadir el evento
  if (openButton) {
    //console.log('contigencia-button encontrado');
    // Mostrar el popup al hacer clic en el botón de la barra lateral
    openButton.addEventListener('click', function () {
      // Antes de mostrar el popup, cargar los tipos de contingencia
      loadTiposContingencia();
      popupContainer.style.display = 'block';
    });
  }

  // Verificar si el botón de cerrar existe antes de añadir el evento
  if (closeButton) {
    //console.log('btn-cerrar encontrado');
    // Ocultar el popup al hacer clic en el botón "Cerrar"
    closeButton.addEventListener('click', function () {
      popupContainer.style.display = 'none';
    });
  }

  addGuardarEventListener();
  // ... (otros eventos y funciones) ...
});
