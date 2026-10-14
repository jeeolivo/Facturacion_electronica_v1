from venv import logger
from django.views import View
from django.http import JsonResponse

from dtesv.processes.contingenciaProcess import Contingencia

class ContingenciaView(View):
## Está clase está diseñada para procesar solicitudes POST relacionadas con contingencias. Recibe datos de solicitud, los procesa utilizando la clase Contingencia, y devuelve una respuesta JSON 
    def post(self, request, *args, **kwargs):
        #print(request)

        ##logger.error(f"valor del request {request}",exc_info=True)
        try:
            response = Contingencia.process_data_document(
                request,kwargs['tipo_contingencia'],
                kwargs['motivo'],kwargs['fecha_inicio'],
                kwargs['fecha_fin'],
                kwargs['hora_ini'],kwargs['hora_fin']
            )
            logger.error(f"Proceso de contingencia completado: {response}", exc_info=True)
        except Exception as e:
            logger.error(f"Error en el proceso de contingencia: {str(e)}", exc_info=True)
            response = 'Error en el proceso de contingencia'
        
        ##return JsonResponse({'message': str(response[0])})
        return JsonResponse({'message': str(response)})    
    # def post(self, request, *args, **kwargs):
    #     print(request)
        
    #     response = Contingencia.process_data_document(request,kwargs['tipo_contingencia'],kwargs['motivo'],kwargs['fecha_inicio'],kwargs['fecha_fin'],
    #                                                   kwargs['hora_ini'],kwargs['hora_fin'])
         
    #     return JsonResponse({'message': str(response[0])})