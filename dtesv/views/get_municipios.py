### 2024-09-19: Este funcion se agrega para mejorar busqueda de acuerdo modificacion de catalogos de MH, para Sistema de Facturación v1.1

from venv import logger
from django.http import JsonResponse
from dtesv.models import C013Municipio  # Asegúrate de que esta importación sea correcta

def get_municipios(request):
    try:
        departamento_id = request.GET.get('departamento_id')
        logger.error(f"El valor obtenido del departamento es: {departamento_id}",exc_info=True)
        
        municipios = C013Municipio.objects.filter(cod_departamento_id=departamento_id)
        logger.error(f"El valor obtenido del municipio es: {municipios}",exc_info=True)
        
        data = list(municipios.values('id','nombre','distr_munic'))  # Ajusta los campos según tu modelo
        #logger.error(f"El valor de la data es: {data}",exc_info=True)
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        logger.error(f"Error al obtener municipios: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
