function exportToExcel() {
    // Obtener los datos de la tabla desde documentos.js
    var datosTabla = obtenerDatosTabla();
  
    // Aquí puedes enviar estos datos al servidor para que se procese y genere el archivo Excel
    // Ejemplo de cómo podrías hacer la solicitud al servidor usando Fetch API
    fetch('/ruta/al/servidor/para/generar/excel', {
      method: 'POST', // o 'GET' dependiendo de tu implementación en el servidor
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ data: datosTabla }) // Enviar los datos al servidor
    })
    .then(response => {
      // Aquí puedes manejar la respuesta del servidor, por ejemplo, descargar el archivo Excel
      // Si el servidor responde con el archivo Excel, podrías descargarlo aquí
      // Podrías hacer algo como window.location.href = '/ruta/del/archivo/excel';
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }