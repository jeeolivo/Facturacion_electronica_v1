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

            diccionario = DocumentoDiccionarioStruc.get_diccionario([documento])
            if not diccionario:
                return JsonResponse({'error': 'No se pudo construir el JSON'}, status=500)

            # Generar el JSON como bytes
            json_data = json.dumps(diccionario[0], ensure_ascii=False, indent=4, default=json_default)
            json_bytes = json_data.encode('utf-8')

            # Generar el PDF como bytes
            pdf_bytes = ger_pdf.generar_pdf_byte(codigoGeneracion)

            # Crear el archivo ZIP en memoria
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(f"{codigoGeneracion}.json", json_bytes)
                zip_file.writestr(f"{codigoGeneracion}.pdf", pdf_bytes)

            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={codigoGeneracion}.zip'
            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
        