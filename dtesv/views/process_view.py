# En tu vista Django
from django.views import View
from django.http import JsonResponse
from dtesv.processes.procesor_runner import run_processor,MainProcessor
from dtesv.tasks import send_emails_for_pending_documents,sell_hellos,procesar_documentos


class ProcessDataView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Llama a la función que ejecuta el procesador
            codigoGeneracion =  kwargs['codigoGeneracion']
            #result = run_processor(codigoGeneracion)
            
            #result = MainProcessor( codigoGeneracion).run()
            result = procesar_documentos.delay(codigoGeneracion)
           # if 'estado' in  result:
           #     if result['estado'] == 'PROCESADO':
           #         result_mail = send_emails_for_pending_documents.delay(codigoGeneracion)
                    

                
            #result = send_emails_for_pending_documents.delay('dos','trs','params')
            #result = sell_hellos.delay('hola hey!!')
            return JsonResponse({'success': True, 'message': str(result.id)})    
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    