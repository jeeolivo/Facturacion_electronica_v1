### 2024-09-19: Este funcion se agrega para mejorar busqueda de acuerdo modificacion de catalogos de MH, para Sistema de Facturación v1.1

from venv import logger
from django.http import JsonResponse
from dtesv.models import C013Municipio, C014Distritos  # Asegúrate de que esta importación sea correcta

def get_distritos(request):
    
    distr_munic = request.GET.get('municipio_id')
     ## = request.GET.get('municipio_distr_munic')
    logger.error(f"El valor recibido de Municipio en distrito es: {distr_munic}", exc_info=True)

    try:
        #municipio = municipio_id.distr_munic
        #logger.error(f"El valor asignado a municipio es: {municipio}", exc_info=True)
        munidistritos = C014Distritos.objects.filter(id=distr_munic)
        logger.error(f"El valor obtenido del distritos es: {munidistritos}", exc_info=True)
        
        data = list(munidistritos.values('id', 'nombre'))  # Ajusta los campos según tu modelo
        logger.error(f"El valor de la data es: {data}", exc_info=True)
        
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        logger.error(f"Error al obtener distritos: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)