import json
import requests
from datetime import datetime
from django.db.models import Q
from dtesv.tasks import send_emails_for_pending_documents,procesar_documentos
from dtesv.models import Documentos ,Emisor,Receptor,DocumentosDetalle,ExtencionEntrega,DocumentosAsociados,Pagos,Parametros
import dtesv.processes.procesorDocMhold as  procesoMH

 
class buscar_documentos():
     def no_procesados(self,cod_receptor):
        result = 'No se encontraron documentos a reprocesar'
        documentos = Documentos.objects.filter(
                             receptor_id=cod_receptor
                                ).filter(
                                    Q(estado='RECHAZADO') | Q(estado='ERROR')
                                )
                               
        if(documentos): 
            for doc in documentos:
                result = procesar_documentos.delay(doc.codigoGeneracion).id
               # result =   procesoMH.DataProcessor.process_data_document(self,doc.codigoGeneracion)

        return result  