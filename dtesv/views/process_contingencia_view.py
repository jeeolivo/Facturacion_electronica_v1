# En tu vista Django
from venv import logger
from django.views import View
from django.http import JsonResponse
from dtesv.processes.contingenciaProcess import Contingencia
#from dtesv.tasks import send_emails_for_pending_documents,sell_hellos,procesar_documentos



class ProcessDataViewContin(View):
    def post(self, request, *args, **kwargs):
        try:
            # Captura los parámetros de la URL
            codigoGeneracion = kwargs.get('codigoGeneracion')
            empresa_id = kwargs.get('empresa_id')

            # Valida que ambos argumentos están presentes
            if not codigoGeneracion or not empresa_id:
                raise ValueError("Faltan parámetros requeridos para el procesamiento.")
            
            # Llama a la función con ambos argumentos
            result = Contingencia.enviar_solicitud(self, codigoGeneracion, empresa_id)
            logger.error(f"Resultado de enviar_solicitud: {result}")
            
            # Devuelve una respuesta de éxito si el proceso se completa
            return JsonResponse({'success': True, 'message': str(result)})
        except Exception as e:
            # Registra y devuelve el error
            logger.error(f"Error en ProcessDataViewContin: {e}", exc_info=True)
            return JsonResponse({'success': False, 'message': str(e)})
    
    