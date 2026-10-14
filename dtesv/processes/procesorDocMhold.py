import json
import requests
from datetime import datetime
from dtesv.views.edicion_receptor import edit_receptor
from django.urls import reverse


from dtesv.models import (
    Documentos,
    Emisor,
    Receptor,
    DocumentosDetalle,
    ExtencionEntrega,
    DocumentosAsociados,
    Pagos,
    Parametros,
    C015Tributos,
)

import dtesv.processes.create_pdf as gen_pdf
import dtesv.processes.create_json as gen_json
import dtesv.processes.constructor_dicionario as get_dic_documento


import dtesv.Apis.firmador as firmador
import dtesv.Apis.autentificador as autenticador
import dtesv.Apis.recepcion_dte as mh_recepciondte
import dtesv.views.sent_email as enviar_email
import os

import base64


class DataProcessor:
    def process_data_document(self, request, codigoGen):
        company = request.user.companies_company.first().id
        tipo_peticion=''
        if 'api' in request.path.startswith.__self__:
            tipo_peticion = 'api'
        else:
            tipo_peticion = 'web'    
        parametros = Parametros.objects.filter(company_id=company).first()
       

        documentos = Documentos.objects.filter(codigoGeneracion=codigoGen)

        list_result = get_dic_documento.DocumentoDiccionarioStruc.procesar_documento_mh(
            documentos, company,False
        )
        result = DataProcessor.save_result_documents(self, list_result,parametros)

        for res in result:
            estado = True if 'estado' in res and res['estado'] == 'PROCESADO' else False
            if  estado:
                codigoGen =res['dic_dte']['identificacion']['codigoGeneracion']
                ruta_pdf_file = gen_pdf.gen_pdf.generarPdf(self,codigoGen)
                if os.path.isfile(ruta_pdf_file['pdf_file']):                                
                   ruta_json_file = DataProcessor.create_jsonFile(self,res['dic_dte'],parametros)
                if os.path.isfile(ruta_json_file): 
                        result_mail = enviar_email.sent_email(parametros,codigoGen)
                        estadoml = json.loads(result_mail.content)['result']
                        if 'Enviado!' in json.loads(result_mail.content)['result'] :
                            res['Estado_email'] =estadoml
                            
                        else :
                            res['Estado_email'] ="NO Enviado"
            
            del res['dic_dte']

        return result
    def save_result_documents(self, documentoslist,parametros):
        for index, resultado in enumerate(documentoslist):
            documentos = Documentos.objects.filter(
                codigoGeneracion=resultado["codigoGeneracion"]
            ).first()

            if "tipo" in resultado:
                if resultado["tipo"] == "schema":
                    data_update = {
                        "tipo": "validacion_schema",
                        "estado": "ERROR",
                        "cadena": resultado['cadena'],
                    }

                elif resultado["tipo"] == "firmador":
                    data_update = {
                        "tipo": "firmador",
                        "estado": "ERROR",
                        "cadena":  resultado['cadena'],
                    }

            else:
                data_update = {
                    "tipo": "mh_log",
                    "estado": resultado["estado"],
                    "cadena": resultado,
                }

            if data_update:
                results = [
                    DataProcessor.update_documento(self, documentos, data_update)
                ]
                results[index]['dic_dte'] = resultado['dic_dte'] if 'dic_dte' in resultado else None
           
        return results

    def update_documento(self, document, result):
        historico = document.observacion_proceso
        historico_mh = document.observaciones_mh
        fecha_actual = datetime.now()
        fecha_actual_str = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")
        document.estado = result["estado"]
        edit_cliente = None
        is_receptor_error  = (("receptor" in result["cadena"]) if isinstance(result.get("cadena"), str) else  any("receptor" in elemento for elemento in result["cadena"]["observaciones"]) if isinstance(result.get("cadena"), dict) and "observaciones" in result["cadena"] else  False)
        if is_receptor_error:
            #url = reverse('home')
            edit_cliente = (
                            "<a> Puede Editar el cliente en el siguiente link: "
                            + f"<a href='/dtesv/editar-receptor/{document.receptor_id_id}/'>Editar Cliente</a>"
                        )
        if result["tipo"] == "mh_log":
            selloRecibido = result["cadena"]["selloRecibido"] if result["cadena"]["selloRecibido"] else None
            if selloRecibido:
                document.selloRecibido = selloRecibido
            observacion = result["cadena"]["observaciones"] if  result["cadena"]["observaciones"] and len(result["cadena"]["observaciones"]) > 0 else None
            document.observaciones_mh = (
                fecha_actual_str
                + ":"
                + (result["cadena"]["descripcionMsg"])+"/"
                + (",".join(observacion) if isinstance(observacion, list) and len(observacion) > 1 else observacion[0] if observacion else '.'
                )
                + ", "
                + (historico_mh)
            )
            document.fecha_proceso_mh = datetime.now()
            estado = result['cadena']['estado']
            retorno = {'estado':document.estado}
            if selloRecibido:
               retorno['selloRecibido']  = selloRecibido  
            retorno['descripcionMsg'] = result["cadena"]["descripcionMsg"] if result["cadena"]["descripcionMsg"] else 'Sin mensaje extra'
            retorno['observaciones'] = result["cadena"]["observaciones"] if result["cadena"]["observaciones"] else 'Sin Observaciones'
            retorno['options'] = edit_cliente if edit_cliente else None
        else:
            document.observacion_proceso = (
                fecha_actual_str + ": "+result["tipo"]+":" + (', '.join(result["cadena"]))if isinstance(result["cadena"],list) else result["cadena"] + ", " + (historico)
            )
            retorno = {'codigoGeneracion':document.codigoGeneracion,'result':document.observacion_proceso }
            retorno['options'] = edit_cliente if edit_cliente else None
        
        document.save()
        return retorno

    def create_jsonFile(self, documento, parametros):
        json_path = gen_json.gen_json.create_fileJson(self, documento, parametros)
        return json_path

