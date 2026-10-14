// contingencias.js

document.addEventListener('DOMContentLoaded', function() {
     
 
    var contingenciasLink = document.getElementById('contingencias-link');
    var empresaSeleccionada;
    var contingenciasContainer = document.getElementById('contingencia-container');
    var dashboardContainer = document.getElementById('dashboard-container');
    var documentosContainer = document.getElementById('documentos-container');

    var bt_busqueda;
    const dataTableOptions = {
        "order": [[7, 'desc']],
        columnDefs: [
          
          { className: 'centered', targets: [0, 1, 2] },
          { searching: true, targets: [0, 3, 9] },
         // { searchable: false, targets: [2] },
          { "type": "time-uni", "targets": 7 }
        ],
        pageLength: 25,
        destroy: true,
        responsive: true
      };
      
  // Función para obtener la empresa seleccionada
  function obtenerEmpresaSeleccionada() {
    return empresaSeleccionada;
  }

  // Función para cambiar la empresa seleccionada
  function cambiarEmpresa() {
    var empresasSelect = document.getElementById('empresas');
    empresaSeleccionada = empresasSelect.options[empresasSelect.selectedIndex].value;
    document.cookie = "empresaSeleccionada=" + empresaSeleccionada;
  }
  document.getElementById('empresas').addEventListener('change', cambiarEmpresa);

  // Llama a cambiarEmpresa al cargar la página para inicializar empresaSeleccionada
  cambiarEmpresa(); 

     function cargarContingencias(fecha_desde_p, fecha_hasta_p) {https://www.bing.com/ck/a?!&&p=f5f2f725623062baJmltdHM9MTY5MDI0MzIwMCZpZ3VpZD0zMmUwMzVjOS00MGIzLTYyODQtMDhlMy0yNmZlNDEwZDYzYjQmaW5zaWQ9NTA0MQ&ptn=3&hsh=3&fclid=32e035c9-40b3-6284-08e3-26fe410d63b4&u=a1Lz9GT1JNPVo5RkQx&ntb=1
    
                        
                //var pageNumber = myTable.page.info().page + 1; // Obtener el número de página actual
                //var pageLength = myTable.page.info().length;


                // Realizar una petición AJAX para o
                var todayDate = new Date();
                var options = { day: '2-digit', month: '2-digit', year: 'numeric' };
                var fechaActual = todayDate.toLocaleDateString('es-SV', options).split('/').reverse().join('-');

                if (!fecha_desde_p) {
                fecha_desde_p = fechaActual
                }


                if (!fecha_hasta_p) {
                fecha_hasta_p = fechaActual
                }


                var xhr = new XMLHttpRequest();
                //xhr.open('GET', '/dtesv/documentos/');
                // console.log(fecha_desde_p)
                // console.log(fecha_hasta_p)
                xhr.open('GET', '/dtesv/contingencias/' + fecha_desde_p + '/' + fecha_hasta_p +'/'+empresaSeleccionada);

                xhr.onload = function() {
                if (xhr.status === 200) {


                // Actualizar el contenido del contenedor con la respuesta del servidor
                contingenciasContainer.innerHTML = xhr.responseText;
                $('#myTable').DataTable(dataTableOptions);
                sentDocumentMh();
                fecha_desde_c.value = fecha_desde_p;
                fecha_hasta_c.value = fecha_hasta_p;
                filtro_fecha();
                sentLoteDocumentMh();
                // agregarEventosPopup();
                
                
                //fecha_desde.value = fecha_desde_p;
                //fecha_hasta.value = fecha_hasta_p;
                //filtro_fecha();


                // Inicializar los filtros de búsqueda
                $('#myTable thead th').each(function() {
                var title = $(this).text();
                $(this).html(title + '<input type="text" class="form-control form-control-sm" placeholder="Buscar ' + title + '">');
                });

                // Aplicar la búsqueda en la tabla
                $('#myTable').DataTable().columns().every(function() {
                var column = this;
                $('input', this.header()).on('keyup change', function() {
                    if (column.search() !== this.value) {
                    column.search(this.value).draw();
                    }
                });
                });

                } else {
                console.log('Error al cargar la tabla de documentos');
                }
                };
                xhr.send();
}

contingenciasLink.addEventListener('click', function(e) {
    e.preventDefault(); // Evitar la acción predeterminada del enlace
    
   
    cargarContingencias();
   // documentosContainer.style.display = 'block'; // Mostrar documentosContainer
    //dashboardContainer.style.display = 'none';
    
    documentosContainer.style.display = 'none'; // Ocultar documentosContainer
   
    dashboardContainer.style.display = 'none'; // Mostrar settingsContainer
    contingenciasContainer.style.display = 'block';
     
  });

  window.cambiarEmpresa = cambiarEmpresa


  function sentDocumentMh() {
    
    var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    $('#myTable tbody').on('click', 'button#sent_mh', function() {
      var rowData = $(this).closest('tr').find('td'); // Obtener todas las celdas de la fila
      
      var plianIcon = $(this).find('i');
      plianIcon.removeClass('fa-solid fa-paper-plane').addClass('fa fa-refresh fa-spin');
          // Obtener los encabezados de columna
      var columnHeaders = $('#myTable thead th').map(function() {
        return $(this).text();
      }).get();

      // Definir el nombre de la columna que deseas buscar
      var nombreColumna = 'Codigo Generacion';
      
      // Verificar si el nombre de la columna existe en los encabezados
      var columnIndex = columnHeaders.indexOf(nombreColumna);
      if (columnIndex !== -1) {
        var documentId = rowData.eq(columnIndex).text();
          
        // Realizar las operaciones que necesites con el valor de la celda
        // ...
      } else {
        console.log("La columna '" + nombreColumna + "' no existe en la tabla.");
      }


      //var documentId = rowData.eq(0).text();
      console.log("Se procesar el documento: " + documentId +" de la empresa " +empresaSeleccionada + company);
      
      fetch('/dtesv/process_contingencias/' + documentId + '/' +empresaSeleccionada+'/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          },
          body: JSON.stringify({ codigoGen: documentId , company : empresaSeleccionada })
        })
        .then(response => response.json())
        .then(data => {
          // Hacer algo con la respuesta de la API
         // alert(data.message);
         plianIcon.removeClass('fa fa-refresh fa-spin').addClass('fa-solid fa-paper-plane');
          mostrarDatosEnPopup(data,"process");
        })
        
        .catch(error => {
          console.log('Al procesar Contingencia se presento un error:',error);
          console.error('Error al procesar los datos:', error);
        });
    });

  }

        function filtro_fecha()
        {
            bt_busqueda = document.getElementById('busca_ids_c');
            
            var todayDate = new Date();
            var options = { day: '2-digit', month: '2-digit', year: 'numeric' };
            var fechaActual = todayDate.toLocaleDateString('es-SV', options).split('/').reverse().join('-');
            
            if (!fecha_desde_c.value) {
            fecha_desde_c.value = fechaActual;
            }
            if (!fecha_hasta_c.value) {
            fecha_hasta_c.value = fechaActual;
            }
            bt_busqueda.addEventListener('click', function() {
            // Obtener los valores de fecha_desde y fecha_hasta de los campos de fecha
            
            // console.log(fecha_desde.value)
            // console.log(fecha_hasta.value)
            // Llamar a la función cargarDocumentos con los valores de fecha
              cargarContingencias(fecha_desde_c.value, fecha_hasta_c.value);
                bt_busqueda.click();
            });

        }

        function sentLoteDocumentMh() {
          var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
          $('#myTable tbody').on('click', 'button#process_lote', function() {
            var rowData = $(this).closest('tr').find('td'); // Obtener todas las celdas de la fila
            
            var plianIcon = $(this).find('i');
            plianIcon.removeClass('fa-cubes').addClass('fa fa-refresh fa-spin');
                // Obtener los encabezados de columna
            var columnHeaders = $('#myTable thead th').map(function() {
              return $(this).text();
            }).get();
      
            // Definir el nombre de la columna que deseas buscar
            var nombreColumna = 'Codigo de Generacion';
      
            // Verificar si el nombre de la columna existe en los encabezados
            var columnIndex = columnHeaders.indexOf(nombreColumna);
            if (columnIndex !== -1) {
              var documentId = rowData.eq(columnIndex).text();
      
              // Realizar las operaciones que necesites con el valor de la celda
              // ...
            } else {
              console.log("La columna '" + nombreColumna + "' no existe en la tabla.");
            }
      
      
      
            
            var documentId = rowData.eq(3).text();
            //console.log(documentId);
            var postData = {       
              codigoGen: documentId,
              fecha_desde: fecha_desde,
              fecha_hasta: fecha_hasta
          };
            fetch('/dtesv/contingencias/procesaLote/' + documentId + '/', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ codigoGen: documentId })
              })
              .then(response => response.json())
              .then(data => {
                // Hacer algo con la respuesta de la API
               // alert(data.message);
               plianIcon.removeClass('fa fa-refresh fa-spin').addClass('fa-cubes');
                //mostrarDatosEnPopup(data,"process");
               
                
                
              })
              
              .catch(error => {
                console.log(error);
                console.error('Error al procesar los datos:', error);
              });
          });
      
        }
});

