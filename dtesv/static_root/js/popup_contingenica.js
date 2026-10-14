// popup.js

document.addEventListener('DOMContentLoaded', function() {
    var popupContainer = document.getElementById('popup-container');
    var popup = document.getElementById('popup');
    var openButton = document.getElementById('contingencia-button'); // Botón de la barra lateral
    var closeButton = document.getElementById('close-button');
    var tipoContingenciaSelect = document.getElementById('tipo-contingencia'); // Select de tipos de contingencia
    var errorMessage = document.getElementById('error-message');
    // Ocultar el popup al cargar la página
    popupContainer.style.display = 'none';
  
    // Mostrar el popup al hacer clic en el botón de la barra lateral
    openButton.addEventListener('click', function() {
      // Antes de mostrar el popup, cargar los tipos de contingencia
      loadTiposContingencia();
      popupContainer.style.display = 'block';
    });
  
    // Ocultar el popup al hacer clic en el botón "Cerrar"
    closeButton.addEventListener('click', function() {
      popupContainer.style.display = 'none';
    });
  
    // Función para cargar los tipos de contingencia desde la vista Django
    function loadTiposContingencia() {
      // Realizar una solicitud AJAX a la vista tipo_contingencia
      $.ajax({
        url: '/dtesv/home/tipo_contingencia',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
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
        error: function(error) {
          console.error('Error al cargar tipos de contingencia: ', error);
        }
      });
    }
    errorMessage.textContent = '';
    // Evento para guardar la contingencia
    document.getElementById('guardar-button').addEventListener('click', function() {
      // Obtener los valores del formulario
      var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
      var tipoContingencia = tipoContingenciaSelect.value;
      var motivoContingencia = document.getElementById('motivo-contingencia').value;
      var fecha_inicio = document.getElementById('fecha-inicio').value;
      var fecha_fin = document.getElementById('fecha-fin').value;
      var hora_ini = document.getElementById('hora-inicio').value;
      var hora_fin = document.getElementById('hora-fin').value;
      
      // Verificar que los campos requeridos estén llenos
      if (!tipoContingencia || !motivoContingencia || !fecha_inicio || !fecha_fin|| !hora_ini|| !hora_fin) {
        errorMessage.textContent = 'Todos los campos son obligatorios.';
        return; // Evitar enviar la solicitud si falta algún campo
      }
      
      // Realizar una solicitud fetch para enviar los datos al servidor
      console.log(fecha_inicio)
      console.log(fecha_fin)
      fetch('/dtesv/contingencia/' + tipoContingencia + '/' + motivoContingencia+ '/' +fecha_inicio+ '/' +fecha_fin+'/' +hora_ini+ '/' +hora_fin, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken, // Obtener el token CSRF
        },
        body: JSON.stringify({}), // Agregar aquí los datos que deseas enviar
      })
        .then(function(response) {
          if (!response.ok) {
            throw new Error('Error al guardar la contingencia');
          }
          return response.json();
        })
        .then(function(data) {
          // Aquí puedes manejar la respuesta del servidor, como mostrar un mensaje de éxito
          console.log('Contingencia guardada con éxito:', data);
          // Cerrar el popup después de guardar
          popupContainer.style.display = 'none';
        })
        .catch(function(error) {
          errorMessage.textContent = 'Error al guardar la contingencia: '+ error;
          
          // Puedes mostrar un mensaje de error o realizar otras acciones aquí
        });
    });
    // ... (otros eventos y funciones) ...
  });
  