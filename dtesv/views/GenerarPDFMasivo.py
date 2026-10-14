import os

from django.http import HttpResponse , JsonResponse
from dtesv.models import Company
from PyPDF2 import PdfMerger
from datetime import datetime
import json
from io import BytesIO

def GenerarPDFS(request):
    data = json.loads(request.body)
    codigos_generacion = data.get('codigosGeneracion', [])
    empresa = data.get('company', str)
    paths_pdf = []
    company_id = Company.objects.get(id=int(empresa))
    parametro = company_id.parametros_company_id.first()

    merger = PdfMerger()
    for codigo_generacion in codigos_generacion:
        path_pdf = parametro.attachment_files_path + codigo_generacion + '.pdf'
        if os.path.exists(path_pdf):
            merger.append(path_pdf)

    # Verificar si el merger está vacío
    if len(merger.pages) == 0:
       return JsonResponse({'result': "No existen Documentos Generados "}, status=404)

    now = datetime.now()
    fecha = now.strftime('%d_%m_%Y_%H_%M_%S')
    nombre_pdf = f"{request.user.username}_{fecha}.pdf"

    # Crear el buffer en memoria para almacenar el contenido del PDF
    pdf_buffer = BytesIO()
    merger.write(pdf_buffer)
    pdf_buffer.seek(0)

    # Configurar la respuesta HTTP con el contenido del PDF
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={nombre_pdf}'

    # Devolver el nombre del archivo en la respuesta JSON
    return response
