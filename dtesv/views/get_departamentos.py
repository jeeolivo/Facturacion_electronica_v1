### 2024-09-19: Este funcion se agrega para mejorar busqueda de acuerdo modificacion de catalogos de MH, para Sistema de Facturación v1.1

from venv import logger
from django.http import JsonResponse
from dtesv.models import C012Departamento  # Asegúrate de que esta importación sea correcta

def get_departamentos(request):
    
    try:
        # Asegúrate de que 'departamentos' es un QuerySet
        departamentos = C012Departamento.objects.all()
        data = list(departamentos.values('codigo', 'nombre'))  # Ajusta los campos según tu modelo
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"Error al obtener departamentos: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)