from django.views import View
from django.http import JsonResponse

from dtesv.processes import procesorLote 

class ProcessLoteDocument(View):
    def get(self, request, *args, **kwargs):
        print(request)
        data_processor = procesorLote.updateDocumentosLote(request,kwargs['loteId'])
        #response = data_processor.process_data_document(request,kwargs['codigoGeneracion'])
         
        return JsonResponse({'message': str(data_processor)})
    
    