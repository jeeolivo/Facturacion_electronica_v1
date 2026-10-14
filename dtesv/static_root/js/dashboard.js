function generateColorByStatus(status) {
  switch (status) {
    case "RECHAZADO":
      return "#FF0000"; // Rojo
    case "PROCESADO":
      return "#00b300"; // Verde
    case "Nuevo":
      return "#FFFF00"; // Amarillo
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
        var borderColor = "#000000"; // Color de borde predeterminado (negro)

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
       console.log(data)
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








