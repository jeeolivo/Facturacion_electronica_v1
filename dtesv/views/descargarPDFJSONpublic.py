from rest_framework.views import APIView
from decimal import Decimal
from django.db.models import Model
from django.utils.encoding import smart_str
from django.http import FileResponse, JsonResponse, HttpResponse
from dtesv.processes.constructor_dicionario import DocumentoDiccionarioStruc
from dtesv.models import Documentos
from dtesv.views.generar_pdf import ger_pdf
import zipfile
import json
import io
import logging

logger = logging.getLogger(__name__)

def json_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, Model):
        # Devuelve los campos del modelo como diccionario
        return obj_to_dict(obj)
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

def obj_to_dict(obj):
    return {
        field.name: getattr(obj, field.name)
        for field in obj._meta.fields
    }

class DescargarPDFJSONPublic(APIView):
    authentication_classes = []  # acceso público
    permission_classes = []

    def get(self, request, codigoGeneracion):
        try:
            documento = Documentos.objects.filter(codigoGeneracion=codigoGeneracion).first()
            if not documento:
                return JsonResponse({'error': 'Documento no encontrado'}, status=404)

            # OBTENER RUTA CONFIGURADA PARA ARCHIVOS
            # ============================================================
            mi_compania = Company.objects.get(emisor=documento.emisor_id)
            parametros = Parametros.objects.get(company_id=mi_compania)

            ruta_base = parametros.attachment_files_path

            ruta_json = os.path.join(ruta_base, f"{codigoGeneracion}.json")
            ruta_pdf = os.path.join(ruta_base, f"{codigoGeneracion}.pdf")

            # JSON
            # ============================================================
            if os.path.isfile(ruta_json):
                logger.info(f"JSON encontrado. Se utilizara archivo existente: {ruta_json}")
                with open(ruta_json, 'rb') as archivo_json:
                    json_bytes = archivo_json.read()
            else:
                logger.info(f"JSON no encontrado: {ruta_json}. Se procedera a construir nuevamente.")
                diccionario = DocumentoDiccionarioStruc.get_diccionario([documento])
                if not diccionario:
                    return JsonResponse({'error': 'No se pudo construir el JSON'},status=500)

                dicto_json = diccionario[0]

                # AGREGAR SELLO RECIBIDO
                sello_recibido = getattr(documento, 'selloRecibido', None)
                if sello_recibido:
                    dicto_json['selloRecibido'] = sello_recibido                

                json_data = json.dumps(
                    dicto_json,
                    ensure_ascii=False,
                    indent=4,
                    default=json_default
                )
                json_bytes = json_data.encode('utf-8')

                # Guardar JSON regenerado
                with open(ruta_json, 'wb') as archivo_json:
                    archivo_json.write(json_bytes)

                logger.info(f"JSON regenerado y guardado: {ruta_json}")

            # PDF
            # ============================================================
            if os.path.isfile(ruta_pdf):
                logger.info(f"PDF encontrado. Se utilizara archivo existente: {ruta_pdf}")
                with open(ruta_pdf, 'rb') as archivo_pdf:
                    pdf_bytes = archivo_pdf.read()
            else:
                logger.info(f"PDF no encontrado: {ruta_pdf}. Se procedera a generarlo nuevamente.")
                pdf_bytes = ger_pdf.generar_pdf_byte(codigoGeneracion)
                # Guardar PDF regenerado
                with open(ruta_pdf, 'wb') as archivo_pdf:
                    archivo_pdf.write(pdf_bytes)

                logger.info(f"PDF regenerado y guardado: {ruta_pdf}")


            # Crear el archivo ZIP en memoria
            # ============================================================
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(f"{codigoGeneracion}.json", json_bytes)
                zip_file.writestr(f"{codigoGeneracion}.pdf", pdf_bytes)

            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={codigoGeneracion}.zip'
            return response

        except Exception as e:
            logger.error(f"Error al descargar JSON: {e}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
        