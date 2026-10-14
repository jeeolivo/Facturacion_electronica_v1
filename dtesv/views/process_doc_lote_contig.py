from django.views import View
from django.http import JsonResponse

from dtesv.processes import procesorDocMhLote
from dtesv.models.contingencia import contingencias 

class ProcessLoteDocumentConting(View):
    def get(self, request, *args, **kwargs):
        print(request)
        codigoGeneracionContin = kwargs['codigoGeneracion']
        documentos = contingencias.objects.filter(codigoGeneracion =  codigoGeneracionContin )

        data_processor = procesorDocMhLote.procesorLote.get_documentos_lote(None,request,documentos.detalleDTE.all())
        
        #response = data_processor.process_data_document(request,kwargs['codigoGeneracion'])
         
        return JsonResponse({'message': str(data_processor)})
    
    