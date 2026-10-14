import json
import requests
from datetime import datetime
from dtesv.views.edicion_receptor import edit_receptor
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from django.urls import reverse
import sys
from dtesv.tasks import send_emails_for_pending_documents
import logging
import traceback
import pytz

logger = logging.getLogger(__name__)
 

from dtesv.models import (
    Documentos,
    Emisor,
    Receptor,
    DocumentosDetalle,
    ExtencionEntrega,
    DocumentosAsociados,
    Pagos,
    Parametros,
    C015Tributos,Company
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

import threading
from multiprocessing import Process, Queue, Event
from concurrent.futures import ThreadPoolExecutor 
import time
import json
import os
from datetime import datetime


# Importa tus clases y funciones necesarias

class DataProcessor:
    def process_data_document(self,codigoGen):
        result = None
        try:
            company = Company.objects.get(id=1)
            #logger.error(f"Ingresando al DataProcessor - compañia: {company}", exc_info=True)
            parametros = Parametros.objects.filter(company_id=company).first()
            #logger.error(f"Ingresando al DataProcessor - parametros: {parametros}", exc_info=True)
            documentos = Documentos.objects.filter(
                 codigoGeneracion=codigoGen,
                 #en_contingencia=False,
                 #selloRecibido__in=[None, ''],
                 )
            logger.error(f"Ingresando al DataProcessor - Documentos-Detalles {documentos}", exc_info=True)

            if documentos.exists():
                 documento = documentos.first()
                 logger.error(f"Documento encontrado: {documento.codigoGeneracion}")
                 list_result = get_dic_documento.DocumentoDiccionarioStruc.procesar_documento_mh(
                    documentos, company, False)
                 result = DataProcessor.save_result_documents(list_result, parametros)
            else:
                 logger.error(f"No se encontraron documentos con el código de generación: {codigoGen}")
                 return {"error": "No existe Documento"}
            # if documentos:
            #     logger.error(f"datas: {documentos.first().codigoGeneracion}", exc_info=True)
            # else:
            #     logger.error(f"datas: No existe Documento", exc_info=True)
            
            # list_result = get_dic_documento.DocumentoDiccionarioStruc.procesar_documento_mh(documentos, company, False)
            # result = DataProcessor.save_result_documents(list_result, parametros)

            return result
        except Exception as e:
            logger.error(f"Ocurrio un problema en procesar_documento_mh: {e}", exc_info=True)
            return result

    def save_result_documents( documentoslist, parametros):
        results = []
        for index, resultado in enumerate(documentoslist):
            # documentos = Documentos.objects.filter(codigoGeneracion=resultado["codigoGeneracion"]).first()
            # 2025-07-10: Estas lineas me permiten obtener el fallback del codigo de generacion si la respues de MH es un error
            codigo_gen = (
                resultado.get("codigoGeneracion")
                or resultado.get("dic_dte", {}).get("identificacion", {}).get("codigoGeneracion")
            )

            if not codigo_gen:
                logger.error("No se pudo extraer el código de generación del resultado.")
                continue

            documentos = Documentos.objects.filter(codigoGeneracion=codigo_gen).first()

            if not documentos:
                logger.error(f"No se encontró documento con codigoGeneracion: {codigo_gen}")
                continue
            # 2025-07-10: Fin de Fallback 

            # Inicializar `resultado2` con un valor por defecto
            resultado2 = {
                "tipo": "mh_log",
                "estado": resultado["estado"],  # Estado predeterminado en caso de error
                "cadena": resultado  # Valor completo de `resultado` para referencia
            }

            if "tipo" in resultado:
                if resultado["tipo"] == "schema":
                    resultado2 = {
                        "tipo": "validacion_schema",
                        "estado": "ERROR",
                        "cadena": resultado['cadena'],
                    }

                elif resultado["tipo"] == "firmador":
                    resultado2 = {
                        "tipo": "firmador",
                        "estado": "ERROR",
                        "cadena":  resultado['cadena'],
                    }

            else:
                # logger.error("Ingresando a la asignacion de RESULTADO2 por defecto")
                # resultado2 = {
                #     "tipo": "mh_log",
                #     "estado": resultado["estado"],
                #     "cadena": resultado,
                # }
                # 2025-07-10: Manejo robusto de 'estado', determina si se encuentra a nivel superior o en el body
                estado = resultado.get("estado")
                if not estado and "body" in resultado and isinstance(resultado["body"], dict):
                    estado = resultado["body"].get("estado")
                if not estado:
                    estado = resultado.get("status", "ERROR")
                resultado2 = {
                    "tipo": "mh_log",
                    "estado": estado,
                    "cadena": resultado,
                }                
                # 2025-07-10: Fin 
            logger.error(f"Error en proceso datos: {resultado2}", exc_info=True)
            data_update = DataProcessor.process_result_data(documentos, resultado2)
            if data_update:
                results.append(data_update)
                results[index]['dic_dte'] = resultado['dic_dte'] if 'dic_dte' in resultado else None

        return results

    def process_result_data( document, result):
        updates_fields=[]
        if isinstance(document,str):
           logger.info(f" datos: {document}", exc_info=True)
           traceback.print_exc()  
           retorno = document
        else:
                    logger.error(f"datos_retorno: {result}", exc_info=True)
                    is_receptor_error = ()
               # try:
                    retorno =None
                    historico = document.observacion_proceso 
                    historico_mh = document.observaciones_mh
                    fecha_actual = datetime.now()            
                    zona_horaria = pytz.timezone('America/El_Salvador')
                    fecha_actual_sv = fecha_actual.astimezone(zona_horaria)
                    fecha_actual_str = fecha_actual_sv.strftime("%Y-%m-%d %H:%M:%S")
                    document.estado = result["estado"]
                    updates_fields.append('estado')
                    edit_cliente = None
                    
                    is_receptor_error = (
                        (
                            "receptor" in result["cadena"] or "sujetoExcluido" in result["cadena"]
                        ) if isinstance(result.get("cadena"), str) else any(
                            "receptor" in elemento or "sujetoExcluido" in elemento
                            for elemento in result["cadena"].get("observaciones", [])
                        ) if isinstance(result.get("cadena"), dict) else False
                    )
                    if is_receptor_error:
                        edit_cliente = (
                            "<a> Puede Editar el cliente en el siguiente link: "
                            + f"<a href='/dtesv/editar-receptor/{document.receptor_id_id if document.receptor_id_id else document.proveedor_id if document.proveedor_id else None}/' target='_blank'>Editar Cliente</a>"
                        )
                        retorno = edit_cliente
                    if result["tipo"] == "mh_log":
                        selloRecibido = result["cadena"]["selloRecibido"] if result["cadena"]["selloRecibido"] else None
                        if selloRecibido:
                            document.selloRecibido = selloRecibido
                            updates_fields.append('selloRecibido')

                        observacion = (
                            result["cadena"]["observaciones"]
                            if result["cadena"]["observaciones"]                            
                            and len(result["cadena"]["observaciones"]) > 0
                            else None
                        )
                        
                        document.observaciones_mh = (
                            fecha_actual_str
                            + ":"
                            +str(result["cadena"]["descripcionMsg"])
                            + "/"
                            + (
                                ",".join(observacion)
                                if isinstance(observacion, list) and len(observacion) > 1
                                else observacion[0] if observacion and len(observacion) > 0
                                else "."
                            )
                            + ", "
                            + (historico_mh if historico_mh else ".")
                        #str(result["cadena"])
                        )
                        updates_fields.append('observaciones_mh')
                        document.fecha_proceso_mh = fecha_actual_sv  
                        updates_fields.append('fecha_proceso_mh')                      
                        retorno = {"estado": document.estado}
                        if selloRecibido:
                            retorno["selloRecibido"] = selloRecibido
                        retorno["descripcionMsg"] = result["cadena"]["descripcionMsg"] if result["cadena"]["descripcionMsg"] else 'Sin mensaje extra'
                        retorno["observaciones"] = result["cadena"]["observaciones"] if result["cadena"]["observaciones"] else 'Sin Observaciones'
                        retorno["options"] = edit_cliente if edit_cliente else None
                    else:
                       
                        document.observacion_proceso = (
                        
                            fecha_actual_str
                            + ": "
                            + result["tipo"]
                            + ":"
                            + (
                                ", ".join(result["cadena"])
                                if isinstance(result["cadena"], list)
                                else result["cadena"] + edit_cliente if  edit_cliente else result["cadena"]
                                + ", "
                                + (historico if historico else '.')
                            )
                        )
                        updates_fields.append('observacion_proceso')    
                        retorno = {
                            "codigoGeneracion": document.codigoGeneracion,
                            "result": document.observacion_proceso,
                        }
                        retorno["options"] = edit_cliente if edit_cliente else None
                    
                    #logger.info(f"datos_DocumentoDjango: {datos}", exc_info=True)
                    traceback.print_exc()
                   # document.save()
                    document.save(update_fields=updates_fields)

               # except Exception as e:
                
               #     logger.error(f"Error en proceso datos: {e}", exc_info=True)
                #    traceback.print_exc()
                
            


        return retorno
    

     

    

   
class MainProcessor:
    def __init__(self,  codigoGen):
        
        self.codigoGen = codigoGen
        self.parametros = Parametros.objects.filter(
            company_id=Company.objects.get(id=1)
        ).first()

    def run(self):
        result_queue = Queue()
        process_data_queue = Queue()
        email_result_queue = Queue()
        stop_event = threading.Event() 

        with ThreadPoolExecutor(max_workers=5) as executor:
        
           # process_data_worker = Process(
           #     target=self.process_data_worker(process_data_queue, stop_event)
           # )
           # process_data_worker.start()
            process_data_worker_future = executor.submit(self.process_data_worker, process_data_queue, stop_event)

        

            user_thread = threading.Thread(target=self.handle_user_communication, args=(result_queue, process_data_queue, stop_event))
            user_thread.start()

            #process_data_worker.join()
            user_thread.join() 

            #if not process_data_worker.is_alive():
                # Solo si el proceso de procesamiento ha terminado, recogemos el resultado
            
            process_data_worker_future.result()
            result = result_queue.get()
            #if not self.should_process_result(result):
            if not self.should_process_result(result):   
                #json_thread = threading.Thread(target=self.json_worker, args=(process_data_queue, stop_event, result))
                #email_thread.start()
                executor.submit(self.json_worker, email_result_queue, stop_event, result)

            #  email_worker = Process(s
            #  target=self.email_worker(process_data_queue, stop_event,result)
            #  )
            #  email_worker.start()   
            
              
            return result[0]

    

     

    def process_data_worker(self, process_data_queue,stop_event):
        try:
            data_processor = DataProcessor()
            result_proces = data_processor.process_data_document(self.codigoGen)
            valor = self.queue_result(process_data_queue, result_proces)  
            process_data_queue.put(result_proces) 

        except Exception as e:
                print(f'Error en el proceso de correo electrónico: {str(e)}')
         
          
            
         
         
        #return result_proces
    
        #queue.put(None)  
    def should_process_result(self, result):
        if isinstance(result, list) and result:
            entry = result[0]  # Tomamos el primer elemento para evaluar
            if 'estado' in entry and entry['estado'] == 'RECHAZADO':
                return True
            if 'result' in entry and 'Error' in entry['result']:
                return True
        return False

    def handle_user_communication(self, result_queue, process_data_queue, stop_event):
        
                result_queue.put(process_data_queue.get())
                 
                        # Envía el resultado al usuario (en este caso, respondiendo con JSON)
                         
                        #return response_data

            
    def email_worker(self, queue, stop_event,values):
        
            try:
                codigoGen=self.codigoGen
                dicto_json = values[0]['dic_dte']
                dicto_json['identificacion']['selloRecibido'] = values[0]['selloRecibido']
                ruta_pdf_file = gen_pdf.gen_pdf.generarPdf(self,codigoGen)
                if os.path.isfile(ruta_pdf_file['pdf_file']):                                
                   ruta_json_file = DataProcessor.create_jsonFile(self,dicto_json,self.parametros)
                if os.path.isfile(ruta_json_file): 
                        result_mail = enviar_email.sent_email(self.parametros,codigoGen)
                        estadoml = json.loads(result_mail.content)['result']
                        if 'Enviado!' in json.loads(result_mail.content)['result'] :
                            estado = print(f'Correo enviado para {codigoGen}. Estado: {estadoml}')
                            
                        else :
                            estado = estadoml
 
               
                return estado    
            except queue.Empty:
                pass  # La cola está vacía, continúa esperando
            except Exception as e:
                print(f'Error en el proceso de correo electrónico: {str(e)}')

    def json_worker(self, queue, stop_event,values):
        
            try:
                 
                dicto_json = values[0]['dic_dte']
                dicto_json['identificacion']['selloRecibido'] = values[0]['selloRecibido']
                                            
                ruta_json_file = DataProcessor.create_jsonFile(self,dicto_json,self.parametros)
                if os.path.isfile(ruta_json_file):

                    
                    
                    return {'documento':self,'codigoGen':self.codigoGen,'parametros':self.parametros}


                
            except queue.Empty:
                pass  # La cola está vacía, continúa esperando
            except Exception as e:
                print(f'Error en el proceso de correo electrónico: {str(e)}')

   

    def queue_result(self, queue, result):
        processed_data = []
        for res in result:
            if res['dic_dte']:  
                if 'estado' in res:
                    if res['estado'] == 'RECHAZADO':
                        codigoGeneracion = res['dic_dte']['identificacion']['codigoGeneracion']
                        mensage =  'Error '+ res['descripcionMsg'] 
                        
                        # Revisar si se recibe el selloRecibido en caso de RECHAZO
                        if 'selloRecibido' in res:
                            # Almacena el sello recibido incluso si el estado es RECHAZADO
                            processed_data.append((res['selloRecibido'], 'PROCESADO', res['dic_dte']))
                            logger.warning(f"Sello recibido presente en un estado RECHAZADO: {res['selloRecibido']}")                        

                        processed_data.append((codigoGeneracion, mensage,res['observaciones']))
                        #queue.put((processed_data))
                    else:
                       processed_data.append((res['selloRecibido'],res['estado'],res['dic_dte'])) 
            else:
                processed_data.append((res['codigoGeneracion'],res['result'],res['dic_dte']))
            #queue.put(processed_data)
        return processed_data
