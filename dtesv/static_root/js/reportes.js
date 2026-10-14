document.addEventListener('DOMContentLoaded', function () {
    const empresasSelect = document.getElementById('empresas');
    if (empresasSelect) {
        empresasSelect.addEventListener('change', cambiarEmpresa);
        cambiarEmpresa(); // Guarda en cookie o backend si deseas
    }

    cargarSeccionPorHash();
    window.addEventListener('hashchange', cargarSeccionPorHash);

    const formReporte = document.querySelector('form[action$="resumen_clientes/"]');
    if (formReporte) {
        formReporte.addEventListener('submit', function (e) {
            const desde = formReporte.querySelector('input[name="desde"]').value;
            const hasta = formReporte.querySelector('input[name="hasta"]').value;
            if (desde && hasta && desde > hasta) {
                e.preventDefault();
                alert('La fecha "Desde" no puede ser mayor que la fecha "Hasta".');
            }
        });
    }

    document.addEventListener('click', function (e) {
        const botonExportarClientes = e.target.closest('#btn-exportar-excel');
        const botonExportarDocumentos = e.target.closest('#btn-exportar-documentos');

        if (botonExportarClientes) {
            e.preventDefault();
            exportarResumenClientesExcel(botonExportarClientes);
        }

        if (botonExportarDocumentos) {
            e.preventDefault();
            exportarDocumentosExcel(botonExportarDocumentos);
        }
    });
});

function cambiarEmpresa() {
    const select = document.getElementById("empresas");
    const empresaId = select.value;
    document.cookie = "empresaSeleccionada=" + empresaId;
    // O bien: enviar al backend vía fetch POST si manejas sesión
}

function exportarResumenClientesExcel(boton) {
    const empresasSelect = document.getElementById('empresas');
    const nombreEmpresa = empresasSelect
        ? empresasSelect.options[empresasSelect.selectedIndex].text
        : 'Empresa no seleccionada';

    const baseUrl = boton.dataset.exportUrl || '/dtesv/reportes/exportar_excel/';
    const params = new URLSearchParams(window.location.search);
    const desde = params.get('desde') || '';
    const hasta = params.get('hasta') || '';
    const tipo = params.get('tipo') || '';

    const queryString = `?desde=${desde}&hasta=${hasta}&tipo=${tipo}&empresa=${encodeURIComponent(nombreEmpresa)}`;
    const excelUrl = `${baseUrl}${queryString}`;

    console.log("Exportando resumen clientes:", excelUrl);

    fetch(excelUrl)
        .then(async response => {
            if (!response.ok) {
                const text = await response.text();
                console.error("Error del servidor:", response.status, text);
                throw new Error('Error al generar Excel');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Resumen_Clientes.xlsx';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            alert("Error al exportar Excel: " + error.message);
        });
}

function exportarDocumentosExcel(boton) {
    const baseUrl = boton.dataset.exportUrl;
    const params = new URLSearchParams(window.location.search);
    const desde = params.get('desde') || '';
    const hasta = params.get('hasta') || '';

    const queryString = `?desde=${desde}&hasta=${hasta}`;
    const excelUrl = `${baseUrl}${queryString}`;

    console.log("Exportando documentos:", excelUrl);

    fetch(excelUrl)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Reporte_Documentos.xlsx';
            document.body.appendChild(a);
            a.click();
            a.remove();
        })
        .catch(error => {
            alert("Error al exportar documentos");
            console.error(error);
        });
}

function cargarSeccionPorHash() {
    const hash = window.location.hash;

    if (hash === '#reportes') {
        mostrarReportes();
    } else if (hash === '#documentos') {
        mostrarDocumentos();
    } else if (hash === '#contingencias') {
        mostrarContingencias();
    } else {
        mostrarDashboard();
    }
}

function mostrarReportes() {
    ocultarTodasSecciones();
    const contenedor = document.getElementById("reportes-container");
    contenedor.style.display = "block";

    const params = new URLSearchParams(window.location.search);
    const desde = params.get('desde') || '';
    const hasta = params.get('hasta') || '';
    const tipo = params.get('tipo') || '';

    const queryString = `?desde=${desde}&hasta=${hasta}&tipo=${tipo}`;

    fetch('/dtesv/reportes/' + queryString)
        .then(response => {
            if (!response.ok) throw new Error('Error al cargar reportes');
            return response.text();
        })
        .then(html => {
            contenedor.innerHTML = html;
        })
        .catch(err => {
            contenedor.innerHTML = `<p class="text-danger">Error al cargar los reportes: ${err.message}</p>`;
        });
}

function mostrarDocumentos() {
    ocultarTodasSecciones();
    document.getElementById("documentos-container").style.display = "block";
}

function mostrarContingencias() {
    ocultarTodasSecciones();
    document.getElementById("contingencia-container").style.display = "block";
}

function mostrarDashboard() {
    ocultarTodasSecciones();
    document.getElementById("dashboard-container").style.display = "block";
}

function ocultarTodasSecciones() {
    document.getElementById("dashboard-container").style.display = "none";
    document.getElementById("documentos-container").style.display = "none";
    document.getElementById("contingencia-container").style.display = "none";
    document.getElementById("reportes-container").style.display = "none";
}


document.addEventListener('DOMContentLoaded', function () {
    const btnExcel = document.getElementById("btn-exportar-excel");
    if (btnExcel) {
        btnExcel.addEventListener('click', function () {
            mostrarCargando("Generando archivo Excel...");
            // Permitimos que continúe el flujo normal de descarga
            setTimeout(() => {
                ocultarCargando();
            }, 3000); // Oculta después de 3s como fallback
        });
    }
});

function mostrarCargando(mensaje = "Cargando...") {
    let overlay = document.createElement("div");
    overlay.id = "cargando-overlay";
    overlay.innerHTML = `
        <div class="spinner-overlay">
            <div class="spinner-border text-primary" role="status"></div>
            <span class="ml-2">${mensaje}</span>
        </div>`;
    document.body.appendChild(overlay);
}

function ocultarCargando() {
    const overlay = document.getElementById("cargando-overlay");
    if (overlay) overlay.remove();
}