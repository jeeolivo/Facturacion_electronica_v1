
function generateColorByStatus(status) {
  switch (status) {
    case "RECHAZADO":
      return 'rgba(255, 99, 132, 0.2)'; // Rojo Rosado semi transparente   Los valores originales son: "#FF0000"; // Rojo
    case "PROCESADO":
      return 'rgba(75, 192, 192, 0.2)'; // Verde Aguamarina    Los valores originales son: "#00b300"; // Verde
    case "Nuevo":
      return 'rgba(255, 206, 86, 0.2)'; // Amarillo suave semitransparente Los valores originales son: "#FFFF00"; // Amarillo
    case "INVALIDADO":
      return 'rgba(255, 159, 64, 0.2)'; // Naranja semi transparente
    default:
      return "#000000"; // Negro (color predeterminado)
  }
}

function generateBorderByStatus(status) {
  switch (status) {
    case "RECHAZADO":
      return 'rgba(255, 99, 132)'; // Rojo
    case "PROCESADO":
      return 'rgba(75, 192, 192)'; // Verde
    case "Nuevo":
      return 'rgba(255, 206, 86)'; // Amarillo
    case "INVALIDADO":
      return 'rgba(255, 159, 64)'; // Naranja
    default:
      return "#000000"; // Negro (color predeterminado)
  }
}

function createChart(filtro) {
  fetch("/dtesv/dashboard/" + filtro)
    .then(response => response.json())
    .then(data => {
      const labels = data.map(d => d.estado);
      const counts = data.map(d => d.cantidad);     
      
      var backgroundColors = [];
      var borderColors = [];

      for (var i = 0; i < labels.length; i++) {
        var status = labels[i];
        var backgroundColor = generateColorByStatus(status);
        var borderColor = generateBorderByStatus(status); //"#000000"; // Color de borde predeterminado (negro)

        backgroundColors.push(backgroundColor);
        borderColors.push(borderColor);
      }

      var ctx = document.getElementById('chartContainer').getContext('2d');
      var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Cantidad de Documentos',
            data: counts,
            backgroundColor: backgroundColors,
            borderColor: borderColors,
            borderWidth: 1
          }]
        },
        options: {
          scales: {
            yAxes: [{
              ticks: {
                beginAtZero: true
              }
            }]
          },
          legend: {
            labels: {
              fontColor: '#000000' // Color de las etiquetas del legend (rojo)
            },
            fillStyle: '#000000' // Color del recuadro del legend (verde)
          }
        }
      });

      return myChart;
    });
}
function urls_status(filtro) {
  // Llamada a la función para llenar la tabla con nombres y círculos rojos
fillTableWithNames(filtro);

// Llamada a la función para actualizar los estados de las URL
//updateStatusForURLs();
}

function fillTableWithNames(filtro) {
  const urlStatusTable = document.getElementById('url-status-table');

  // Llamada a la vista con el filtro proporcionado
  fetch('/dtesv/urls_status/'+ filtro)
    .then(response => response.json())
    .then(data => {
      //console.log(data)
      // Elimina todas las filas de la tabla, excepto la primera fila de encabezado
      while (urlStatusTable.rows.length > 1) {
        urlStatusTable.deleteRow(1);
      }

      // Itera a través de los nombres de URL y agrega filas a la tabla con círculos rojos por defecto
      data.forEach(name => {
        const row = urlStatusTable.insertRow(-1); // Agrega una nueva fila al final
        const cell1 = row.insertCell(0); // Celda para la descripción
        const cell2 = row.insertCell(1); // Celda para el estado

        cell1.textContent = name; // Nombre de la URL
        cell2.innerHTML = '<i class="fas fa-circle red-icon"></i>'; // Círculo rojo por defecto
      });
    })
    .catch(error => {
      console.error('Error al obtener los nombres de las URL:', error);
    });
}

function updateStatusForURLs() {
  // Aquí llamamos a la vista que valida las URL y actualiza los estados
  const urlStatusTable = document.getElementById('url-status-table');

  // Llamada a la vista con el filtro "state"
  fetch('/dtesv/urls_status/?filter=state')
    .then(response => response.json())
    .then(data => {
      data.forEach(item => {
        const row = urlStatusTable.rows.namedItem('url-' + item.name.toLowerCase());
        if (row) {
          const cell2 = row.cells[1];
          if (item.state) {
            // Círculo verde si el estado es verdadero
            cell2.innerHTML = '<i class="fas fa-circle green-icon"></i>';
          } else {
            // Círculo rojo si el estado es falso
            cell2.innerHTML = '<i class="fas fa-circle red-icon"></i>';
          }
        }
      });
    })
    .catch(error => {
      console.error('Error al obtener los estados de las URL:', error);
    });
}


function setDefaultDates() {
  // Obtener la fecha actual
  const today = new Date();
  console.log("Fecha Actual: ", today)
  // Establecer la fecha actual en el input "Hasta"
  const endDateInput = document.getElementById("end-date");
  if (endDateInput) {  // Verifica que el elemento existe
    endDateInput.value = today.toISOString().split("T")[0]; // Formato YYYY-MM-DD
  } else {
    console.error("El input 'end-date' no se encontró.");
  }

  // Establecer el primer día del mes en el input "Desde"
  const startDateInput = document.getElementById("start-date");
  if (startDateInput) {  // Verifica que el elemento existe
    const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    startDateInput.value = firstDayOfMonth.toISOString().split("T")[0]; // Formato YYYY-MM-DD
  } else {
    console.error("El input 'start-date' no se encontró.");
  }
}


// 2024-10-10: Esta grafica es para el conteo de documentos por mes
function cargarGrafico(meses, datosPorEstado) {
  // Verifica que meses y datosPorEstado estén definidos
  console.log("Version:", Chart.version);
  //console.log("Datos por estado:", datosPorEstado);
  // Verificar si el canvas existe antes de intentar acceder a su contexto
  var canvasElement = document.getElementById('documentosEstadoChart');
  canvasElement.style.paddingTop = '18px'
  canvasElement.style.paddingBottom = '18px'

  if (!canvasElement) {
    console.error("El elemento 'documentosEstadoChart' no se encontró.");
    return; // Detener la ejecución si el canvas no existe
  }

  var ctx = canvasElement.getContext('2d');

  // Definición de colores para cada estado
  var borderColoresEstado = {
    'PROCESADO': 'rgba(75, 192, 192, 1)', // color para PROCESADO
    'INVALIDADO': 'rgba(255, 99, 132, 1)', // color para INVALIDADO
    'RECHAZADO': 'rgba(255, 206, 86, 1)',  // color para RECHAZADO
    'ERROR': 'rgba(54, 162, 235, 1)',      // color para ERROR
    'ERR_INVALI': 'rgba(153, 102, 255, 1)' // color para ERR_INVALI
  };

  // Definición de colores para cada estado
  var groundColoresEstado = {
    'PROCESADO': 'rgba(75, 192, 192, 0.2)', // color para PROCESADO
    'INVALIDADO': 'rgba(255, 99, 132, 0.2)', // color para INVALIDADO
    'RECHAZADO': 'rgba(255, 206, 86, 0.2)',  // color para RECHAZADO
    'ERROR': 'rgba(54, 162, 235, 0.2)',      // color para ERROR
    'ERR_INVALI': 'rgba(153, 102, 255, 0.2)' // color para ERR_INVALI
  };

  var chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: meses,
      datasets: Object.keys(datosPorEstado).map(function (estado) {
        return {
          label: estado,
          data: datosPorEstado[estado],
          backgroundColor: groundColoresEstado[estado] || 'rgba(0, 0, 0, 0.1)', // color de fondo por defecto
          borderColor: borderColoresEstado[estado] || 'rgba(0, 0, 0, 1)', // color de borde por defecto
          borderWidth: 1
        };
      })
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });

  chart.options.plugins.legend.labels.padding = 50;

  return chart;
}


function correosNoEnviados(data) {
  //console.log("Datos recibidos en correosNoEnviados: ", data); // Verifica los datos en la consola
  const tbody = $("#tablaDocumentosNoEnviados tbody");
  tbody.empty(); // Limpia el tbody antes de llenarlo

  if (data.length === 0) {
    tbody.append("<tr><td colspan='4'>No hay documentos pendientes de enviar</td></tr>");
  } else {
    data.forEach(function (doc) {
      tbody.append(`
        <tr>
          <td>${doc.num_documento}</td>
          <td>${doc.Receptor_id}</td> <!-- Asegúrate de que 'Receptor_id' es el nombre correcto -->
          <td>${doc.Nombre}</td> <!-- Asegúrate de que 'Nombre' es el nombre correcto -->
          <td>${doc.fecEmi}</td>
        </tr>
      `);
    });
  }
}





