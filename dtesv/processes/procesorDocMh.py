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
    Documentos,Parametros,Company
)

import dtesv.processes.create_pdf as gen_pdf
import dtesv.processes.create_json as gen_json
import dtesv.processes.constructor_dicionario as get_dic_documento


import dtesv.Apis.firmador as firmador
import dtesv.Apis.autentificador as autenticador
import dtesv.Apis.recepcion_dte as mh_recepciondte
import dtesv.views.sent_email as enviar_email
import os

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

        documentos = Documentos.objects.filter(codigoGeneracion=codigoGen)

        if not documentos.exists():
            logger.error(
                f"No se encontró el documento {codigoGen}"
            )
            return {"error": "No existe Documento"}
        
        documento = documentos.first()
        empresa = documento.emisor_id
        logger.info(f"Valor de empresa en documento: {empresa}")

        try:
            company = Company.objects.get(emisor=empresa)
            logger.info(f"Compañía obtenida: {company.name} ID:{company.id}")

            parametros = Parametros.objects.filter(company_id=company.id).first() # Tambien puedo hacer una consulta directa parametros = Parametros.objects.filter(company_id=documento.emisor_id).first()

            if documentos:
                logger.info(f"[SENT_MH-PROCESSOR] Documento encontrado: " f"{documento.codigoGeneracion}, Estado actual: {documento.estado}"
                )
                 
                logger.info(f"[SENT_MH-PROCESSOR] Llamando procesar_documento_mh()")
                list_result = get_dic_documento.DocumentoDiccionarioStruc.procesar_documento_mh(documentos, company, False)
                 
                logger.info(f"[SENT_MH-PROCESSOR] Resultado de procesar_documento_mh obtenido, guardando resultados...")
                result = DataProcessor.save_result_documents(list_result, parametros)
                logger.info(f"[SENT_MH-PROCESSOR] Resultados guardados exitosamente")
            else:
                logger.error(f"[SENT_MH-PROCESSOR] No se encontraron documentos con el código de generación: {codigoGen}")
                return {"error": "No existe Documento"}
            
            return result
        except Exception as e:
            logger.error(f"[SENT_MH-PROCESSOR] EXCEPCION en process_data_document para {codigoGen}: {str(e)}", exc_info=True)
            return result


    def save_result_documents( documentoslist, parametros):
        logger.info(f"[SENT_MH-PROCESSOR] save_result_documents: Procesando {len(documentoslist)} resultado(s)")
        results = []
        for index, resultado in enumerate(documentoslist):
            # Estas lineas me permiten obtener el fallback del codigo de generacion si la respues de MH es un error
            codigo_gen = (
                resultado.get("codigoGeneracion")
                or resultado.get("dic_dte", {}).get("identificacion", {}).get("codigoGeneracion")
            )

            if not codigo_gen:
                logger.error(f"[SENT_MH-PROCESSOR] No se pudo extraer el código de generación del resultado en índice {index}")
                continue

            logger.info(f"[SENT_MH-PROCESSOR] [{index}] Procesando resultado para codigoGen: {codigo_gen}")
            documento = Documentos.objects.filter(codigoGeneracion=codigo_gen).first()

            if not documento:
                logger.error(f"[SENT_MH-PROCESSOR] No se encontró documento con codigoGeneracion: {codigo_gen}")
                continue
            logger.info(f"[SENT_MH-PROCESSOR] [{index}] Documento encontrado - codigoGen: {codigo_gen}, Estado anterior: {documento.estado}")

            # Determinar el tipo de resultado y asignar el estado correspondiente
            tipo = resultado.get("tipo", "mh_log")

            if tipo == "schema":
                resultado2 = {
                    "tipo": "validacion_schema",
                    "estado": "ERROR",
                    "cadena": resultado['cadena'],
                }
                logger.warning(f"[SENT_MH-PROCESSOR] [{index}] Error de validación de esquema MH")

            elif tipo == "firmador":
                resultado2 = {
                    "tipo": "firmador",
                    "estado": "ERROR",
                    "cadena":  resultado['cadena'],
                }
                logger.warning(f"[SENT_MH-PROCESSOR] [{index}] Error en servicio firmador")

            else:
                resultado2 = {
                    "tipo": "mh_log",
                    "estado": resultado.get("estado", "ERROR"),
                    "cadena": resultado,
                }                
                logger.info(f"[SENT_MH-PROCESSOR] [{index}] Resultado tipo MH - Estado: {resultado2['estado']}")
            
            logger.info(f"[SENT_MH-PROCESSOR] [{index}] Actualizando documento con resultado2: tipo={resultado2['tipo']}, estado={resultado2['estado']}")
            
            data_update = DataProcessor.process_result_data(documento, resultado2)
            
            if data_update:
                data_update["dic_dte"] = resultado.get("dic_dte")
                results.append(data_update)
                logger.info(f"[SENT_MH-PROCESSOR] [{index}] Documento actualizado y agregado a resultados")

        logger.info(f"[SENT_MH-PROCESSOR] save_result_documents completado - {len(results)} documento(s) procesado(s)")
        return results


    def process_result_data(document, result):

        updates_fields = []

        if isinstance(document, str):
            logger.error(document)
            return document

        logger.info(f"datos_retorno: {result}")

        historico = document.observacion_proceso or ""
        historico_mh = document.observaciones_mh or ""

        fecha_actual_sv = datetime.now(pytz.timezone("America/El_Salvador"))
        fecha_actual_str = fecha_actual_sv.strftime("%Y-%m-%d %H:%M:%S")
        document.estado = result.get("estado", "ERROR")
        updates_fields.append("estado")

        cadena = result.get("cadena", {})

        # Detectar errores del receptor
        edit_cliente = None

        if isinstance(cadena, str):
            is_receptor_error = ("receptor" in cadena or "sujetoExcluido" in cadena)
        elif isinstance(cadena, dict):
            observaciones = cadena.get("observaciones") or []
            is_receptor_error = any(
                "receptor" in x or "sujetoExcluido" in x
                for x in observaciones
            )
        else:
            is_receptor_error = False

        if is_receptor_error:
            edit_cliente = (
                "<a> Puede Editar el cliente en el siguiente link: "
                f"<a href='/dtesv/editar-receptor/"
                f"{document.receptor_id_id if document.receptor_id_id else document.proveedor_id}/'"
                f" target='_blank'>Editar Cliente</a>"
            )

        # RESPUESTA MH

        if result["tipo"] == "mh_log":
            sello = cadena.get("selloRecibido")
            if sello:
                document.selloRecibido = sello
                updates_fields.append("selloRecibido")

            observaciones = cadena.get("observaciones") or []

            document.observaciones_mh = (
                f"{fecha_actual_str}:"
                f"{cadena.get('descripcionMsg','')}/"
                f"{', '.join(observaciones) if observaciones else '.'}, "
                f"{historico_mh if historico_mh else '.'}"
            )

            updates_fields.append("observaciones_mh")

            document.fecha_proceso_mh = fecha_actual_sv
            updates_fields.append("fecha_proceso_mh")

            retorno = {
                "estado": document.estado,
                "selloRecibido": sello,
                "descripcionMsg": cadena.get("descripcionMsg"),
                "observaciones": observaciones,
                "options": edit_cliente,
            }

        # ERRORES INTERNOS
        else:
            cadena_val = result.get("cadena")

            if isinstance(cadena_val, dict):
                cadena_str = (
                    cadena_val.get("descripcionMsg")
                    or cadena_val.get("message")
                    or json.dumps(cadena_val, ensure_ascii=False)
                )
            elif isinstance(cadena_val, list):
                cadena_str = ", ".join(map(str, cadena_val))
            else:
                cadena_str = str(cadena_val)
            if edit_cliente:
                cadena_str += " " + edit_cliente

            document.observacion_proceso = (
                f"{fecha_actual_str}: "
                f"{result['tipo']}: "
                f"{cadena_str}, "
                f"{historico if historico else '.'}"
            )

            updates_fields.append("observacion_proceso")

            retorno = {
                "codigoGeneracion": document.codigoGeneracion,
                "result": document.observacion_proceso,
                "options": edit_cliente,
            }

        document.save(update_fields=updates_fields)

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
