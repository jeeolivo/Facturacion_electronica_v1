import json
import requests
from datetime import datetime

from dtesv.models import Documentos,Parametros
from dtesv.models.documentos_lote import DocumentosLote
import dtesv.Apis.autentificador as autenticador
from dtesv.processes.constructor_dicionario import DocumentoDiccionarioStruc
from django.db import transaction
import dtesv.Apis.recepcion_dte as mh_recepciondte

import uuid
import base64




class procesorLote:
    def get_cocumento_contingencia():
        documentos = Documentos.objects.filter(en_contingencia = True) 
        
        
        print('HELLO')

    def get_documentos_lote(self,request,documentos):
        company = request.user.companies_company.first().id
        parametros = Parametros.objects.filter(company_id = company).first()
        idEnvio = uuid.uuid4()
        
        documentoLote = DocumentosLote().crear_documentos_lote(
            idEnvio= str(idEnvio).upper(),
            version=1,
            ambiente=parametros.ambiente,
            version_app=1,
            estado=None,
            codigo_lote=None,
            fh_procesamiento=datetime.now(),
            clasifica_msg=1,
            codigo_msg=None,
            descripcion_msg=None,
            documentos_relacionados=documentos 

            )
        if documentoLote:
            listaDocumentos = list(documentoLote.detalledocumentoslote.all())
            dic_documentos =  DocumentoDiccionarioStruc.procesar_documento_mh(listaDocumentos,company,True,documentoLote.idEnvio)
        
        if  any(diccionario.get('tipo') in ['schema', 'firmador'] for diccionario in dic_documentos):

            documento_lote = DocumentosLote.objects.get(id=documentoLote['idEnvio'])
            nueva_lista = [item['codigoGeneracion'] for item in dic_documentos]
            with transaction.atomic():
                # Itera sobre los IDs a eliminar y elimina los registros correspondientes de DocumentosLote
                for doc_id in nueva_lista:
                    documento_lote.documentos_relacionados.filter(id=doc_id).delete()

                    # Si deseas guardar los cambios en el objeto documento_lote
                documento_lote.save()  
            newlistaDocumentos = list(documento_lote.detalledocumentoslote.all())
            redic_documentos =  DocumentoDiccionarioStruc.procesar_documento_mh(newlistaDocumentos,company,True,documento_lote.idEnvio)
            if redic_documentos and 'descripcionMsg' in dic_documentos[0] and 'RECIBIDO' in dic_documentos[0]['descripcionMsg']:
                result =procesorLote.actualizarDatoslote(redic_documentos,documento_lote,request,newlistaDocumentos)
             
            return redic_documentos
        else:
            if dic_documentos and 'descripcionMsg' in dic_documentos[0] and 'RECIBIDO' in dic_documentos[0]['descripcionMsg']:
                result= procesorLote.actualizarDatoslote(dic_documentos,documentoLote,request,listaDocumentos)
            
            return dic_documentos
        

    def actualizarDatoslote(dic_documentos,documentoLote,request,listaDocumentos):
            
                with transaction.atomic():                          

                            Documentos.objects.filter(pk__in=[doc.pk for doc in listaDocumentos]).update(
                                codigoLotelocal=dic_documentos[0]['idEnvio'],
                                codigoLotemh=dic_documentos[0]['codigoLote'],
                                estado = 'ENVIADO',
                                observacion_proceso = str(dic_documentos)
                                    )
                documentoLote.codigoLote = dic_documentos[0]['codigoLote']
                documentoLote.estado = 'RECIBIDO'
                documentoLote.descripcionMsg = dic_documentos[0]['descripcionMsg']
                documentoLote.codigoMsg = dic_documentos[0]['codigoMsg']
                documentoLote.save()
                procesorLote.updateDocumentosLote(request,dic_documentos[0]['codigoLote']) 
                

    def updateDocumentosLote(request,loteId= None):
         
        company = request.user.companies_company.first()
        parametros = Parametros.objects.filter(company_id = company).first()
        lis_doc=[]
        if not loteId or 'null' in loteId :
            documentoslote = DocumentosLote.objects.filter(estado = 'RECIBIDO')
            
            if documentoslote:
                 lis_doc = [documento.codigoLote for documento in documentoslote]
                  
        else:
             lis_doc.append({loteId})
        nit = company.emisor.nit
        pwd = base64.b64decode(company.emisor.mh_auth).decode("utf-16")

        uth_data = ({'user':nit,'pwd':pwd})
        token = autenticador.authenticate(uth_data,parametros).get_token()
        for doc in lis_doc:
            dic_process = ({'auth':token['body']['token'],'loteId':doc})
            mh_result = mh_recepciondte.get_documentosLote(dic_process,parametros).sent_data()
            if mh_result:
                print(mh_result)
                
                procesados = mh_result.get('procesados', [])                
                rechazados = mh_result.get('rechazados', [])

                lista_total = procesados + rechazados
                for item in lista_total:
                    documento_id = item.get('codigoGeneracion')
                    nuevo_estado = item.get('estado')
                    descriciomsg = item.get('descripcionMsg')
                    observaciones = item.get('observaciones')
                    selloRecibido = item.get('selloRecibido') if 'selloRecibido' in item else None

                    # Buscar el documento por su ID
                    documento = Documentos.objects.get(codigoGeneracion=documento_id)

                    # Actualizar el campo estado con el nuevo estado
                    documento.estado = nuevo_estado
                    documento.observaciones_mh = descriciomsg + ':'+ str(observaciones)
                    documento.selloRecibido = selloRecibido
                     
                    documento.save()
                    

            return mh_result