# En tu vista Django
from django.views import View
from django.http import JsonResponse
from dtesv.models import Documentos
from dtesv.processes.procesor_runner import run_processor,MainProcessor
from dtesv.tasks import send_emails_for_pending_documents,sell_hellos,procesar_documentos
from datetime import datetime


class ReProcessDataView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Llama a la función que ejecuta el procesador
            lista = []
            fecha_desde =  kwargs['fecha_desde']
            fecha_hasta =  kwargs['fecha_hasta']
            fecha_desde_d = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            fecha_hasta_d = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            documentos = Documentos.objects.filter(fecEmi__gte=fecha_desde_d, fecEmi__lte=fecha_hasta_d,estado__in=['RECHAZADO', 'ERROR','Nuevo'])
            if documentos:
                for doc in documentos:
                    if doc.codigoGeneracion:
                        key = procesar_documentos.delay(doc.codigoGeneracion)
                        lista.append(key)
            else:
                lista.append('NO Existen Documentos a Reprocesar')
           
            return JsonResponse({'success': True, 'message': str(lista)})    
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    