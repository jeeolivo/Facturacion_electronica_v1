### 2024-09-19: Este funcion se agrega para mejorar busqueda de acuerdo modificacion de catalogos de MH, para Sistema de Facturación v1.1

from django.views import View
from django.http import JsonResponse

from dtesv.models import Documentos

class receptor_from_document(View):
    def post(self, request, *args, **kwargs):
        id_result = ''
        response =   Documentos.objects.filter(codigoGeneracion = kwargs['codigoGeneracion']).get()
        if response.tipodocumento.codigo in ['07','14']:
           id_result = response.proveedor_id.codigo
           tipo_receptor = response.proveedor_id.tiporeceptor 
           #tipo_receptor = 'proveedor'
        else:
            id_result = response.receptor_origen.codigo if response.receptor_origen else response.receptor_id.codigo
            tipo_receptor = response.receptor_origen.tiporeceptor if response.receptor_origen else response.receptor_id.tiporeceptor
            #tipo_receptor = 'cliente'
        
        if response: 
            return  JsonResponse({'message': id_result, 'tipo_receptor': tipo_receptor})        


        return JsonResponse({'message': 'Error', 'tipo_receptor': 'Desconocido'})    
    
