from .home_view import CustomLoginView ,profile_view,home,documentos_by_fecha,obtener_datos_documento ,documentos,tipo_contingencia
from .process_view import ProcessDataView
from .re_process_view import ReProcessDataView
from .generar_pdf import ger_pdf
from .dashboard import dashboard_view, dashboard_json_view, dashboard_json_totalMeses,obtener_documentos_no_enviados #, urls_status_data #,url_status,dashboard_data_view
from .rest_api import (
    ReceptorDetail,
    DocumentosCreateAPIView,
    DocumentosRetrieveAPIView,
    DocumentosUpdateCompleteAPIView,
    InvalidacionClass,
    DocumentoClienteTelefono,
    DocumentoCliente,
    DocumentosLoteCreateAPIView,
    CustomObtainAuthToken,
    ProveedorDetail,
    DownloadFilesAPI,
    createPDFJSONSENMAIL
)
from .sent_email import sent_email, update_email_sent
from .edicion_receptor import edit_receptor

from . contingeciaview import ContingenciaView
from . get_receptor_from_dte import receptor_from_document
from . update_documentLote import ProcessLoteDocument
from . solicitud_contingencias import solicitud_contingencias_view,data_contingencias
from . process_contingencia_view import ProcessDataViewContin
from . process_doc_lote_contig import ProcessLoteDocumentConting

from . create_nota_credito import GenerateNotaCredito
from . create_nota_debito import GenerateNotaDebito
from . GenerarPDFMasivo import GenerarPDFS
#from .descargarPDFJSONpublic import DescargaPublica
from . edit_documento import edit_Documento
## Estos cambios de aplican de acuerdo al nuevo requerimiento de MH, donde se deben de reflejar los distritos
from .get_departamentos import get_departamentos
from .get_municipios import get_municipios
from .get_munidistrito import get_distritos
from .email_counts import get_email_counts

from .reportes import reportes_view, exportar_resumen_clientes_excel, exportar_documentos_excel

# siendo el archivo view  la vista principal llamo las otras vistas  y las asigno a variables que seran llamadas desde las url


CustomLoginViews = CustomLoginView
profile_views = profile_view
homes =home
documento_fecha =documentos_by_fecha
documentoss = documentos
obtener_datos_documentos = obtener_datos_documento
procesoDatos =ProcessDataView
reprocesoDatos = ReProcessDataView
Generar_pdf = ger_pdf.generarPdf
ProcessLoteDocumentContings = ProcessLoteDocumentConting.get
#Settings_list = settings_list
#Settings_create = settings_create
#Settings_edit = settings_edit
#Settings_delete = settings_delete

#!# Vistas usadas para el DashBoard 
Dashboard_view = dashboard_view
Dashboard_json_view = dashboard_json_view
Dashboard_totalMes = dashboard_json_totalMeses
Dashboard_NoEnviados = obtener_documentos_no_enviados
get_emails_counts = get_email_counts

ReceptorDetails = ReceptorDetail
ProveedorDetails = ProveedorDetail
DocumentosCreateAPIViews = DocumentosCreateAPIView
DocumentosRetrieveAPIViews = DocumentosRetrieveAPIView
DocumentosUpdateCompleteAPIViews = DocumentosUpdateCompleteAPIView
sentEmail = sent_email
updateEmail = update_email_sent
invalidarDocumento = InvalidacionClass
DocumentoClienteTelefonos =DocumentoClienteTelefono
DocumentoClientes =DocumentoCliente
receptor_from_documents = receptor_from_document
#urls_status =urls_status_data
edit_receptors =edit_receptor
DocumentosLoteCreateAPIViews =DocumentosLoteCreateAPIView
ProcessLoteDocuments = ProcessLoteDocument

##! Vistas para manipulacion de documentos
edit_Documentos = edit_Documento
DownloadFilesAPIs = DownloadFilesAPI
GenerateNotaCreditos = GenerateNotaCredito
GenerateNotaDebitos = GenerateNotaDebito
PdfJsonMail = createPDFJSONSENMAIL
GenerarPDFM = GenerarPDFS
#descargar_pdf_json = DescargaPublica

##! Vistas usadas para las contingencias.
solicitud_contingencias_views = solicitud_contingencias_view
data_contingencias_views = data_contingencias
procesar_contingencia = ProcessDataViewContin
tipo_contingecias =tipo_contingencia
contingencia = ContingenciaView

##! Vista a usar para usar dinamicamente en el formulario, Estos cambios de aplican de acuerdo al nuevo requerimiento de MH, donde se deben de reflejar los distritos
gDepartamentos = get_departamentos
gMunicipio = get_municipios
gDistritos = get_distritos


##! Vistas para la reporteria.
reporte_Clientes = reportes_view
exportar_Excel = exportar_resumen_clientes_excel
exportar_documentos_excel = exportar_documentos_excel
