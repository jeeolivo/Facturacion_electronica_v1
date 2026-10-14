from celery import shared_task , Task
from dtesv.models import Documentos , Parametros , Company
import dtesv.processes.create_pdf as gen_pdf
import dtesv.processes.procesorDocMh as  DataProcessor
import dtesv.processes.create_json as gen_json
import dtesv.processes.invalidDocumento as invelid_doc
import os
import dtesv.views.sent_email as enviar_email
import traceback
import redis
import logging

import json

logger = logging.getLogger(__name__)

#@shared_task(queue='general_tasks')
@shared_task(queue='default')
def send_emails_for_pending_documents(codigoGeneracion):
   
      try:    
            document = Documentos.objects.get(codigoGeneracion=codigoGeneracion)
            mi_compania = Company.objects.get(id=1)  # Ajusta el ID según tus necesidades

            # Obtén los parámetros asociados a la compañía
            parametros = Parametros.objects.get(company_id=mi_compania)            
            ruta_pdf_file = gen_pdf.gen_pdf.generarPdf(document,codigoGeneracion)
            #if os.path.isfile(ruta_pdf_file['pdf_file']): 
            pdf_file = ruta_pdf_file.get('pdf_file')

            if pdf_file and os.path.isfile(pdf_file):            
            #if os.path.isfile(ruta_pdf_file):
                  result_mail = enviar_email.sent_email(parametros,codigoGeneracion)
                  estadoml = json.loads(result_mail.content)['result']
                  
                  if 'Enviado!' in estadoml:
                        
                        document.email_enviado = True
                        
                        document.save()
                        logger.info(f'Ok -- {estadoml}',exc_info=True)
                        #traceback.print_exc()
                        #estado = print(f'Correo enviado para {codigoGeneracion}. Estado: {estadoml}')
                         
                  else :
                        document.observacion_proceso = estadoml
                        logger.info(f'Not -- {estadoml}',exc_info=True)
                        #traceback.print_exc()
            else :
                estadoml = (f"No se encontró el archivo PDF para {codigoGeneracion}: {pdf_file}")
                logger.error(estadoml)                         
            return estadoml
      except Exception as e:
        logger.error(f"Error in send_emails_for_pending_documents: {e}", exc_info=True)
        #traceback.print_exc()
        return f"Error in send_emails_for_pending_documents: {e}"



#@shared_task(queue='general_tasks')
@shared_task(queue='urgent')
def procesar_documentos(codigoGen):
    logger.info(f"Ingresando al Task - procesar_documentos: {codigoGen}", exc_info=True)
    try:
        document = Documentos.objects.get(codigoGeneracion=codigoGen)
        mi_compania = Company.objects.get(emisor=document.emisor_id)

        # Obtén los parámetros asociados a la compañía
        parametros = Parametros.objects.get(company_id=mi_compania)     
        logger.info(f"[PROCESS_DOCUMENT] Company: {mi_compania.id}")

        logger.info(f"[PROCESS_DOCUMENT] attachment_files_path: " f"{parametros.attachment_files_path}")

        result_proces = DataProcessor.DataProcessor.process_data_document(None,codigoGen)
        #logger.error(f"Resultado DataProcesor: {result_proces}", exc_info=True)
        
        #if len(result_proces) > 0:
        if result_proces and len(result_proces) > 0:
            documento_procesado = result_proces[0]
            estado = documento_procesado.get('estado')
            result = documento_procesado.get('result')

            if (estado not in ['RECHAZADO','ERROR'] and estado is not None) or (result is not None and 'Error' not in result):
                logger.error(f"Resultado REVISION DataProcesor: {documento_procesado}", exc_info=True)
                dicto_json = documento_procesado['dic_dte']
                # dicto_json['identificacion']['selloRecibido'] = (documento_procesado['selloRecibido']) # Esta linea permite que el sello recibido se agregue dentro del campo de identificacion del JSON, pero no es necesario para el envio a MH, ya que el sello recibido se encuentra en la raiz del JSON. Se deja comentada por si se requiere en el futuro.
                dicto_json['selloRecibido'] = documento_procesado['selloRecibido']  # Sello de recepción al mismo nivel que identificacion
                # Documento firmado enviado a MH
                if documento_procesado.get('firmaElectronica'):
                    dicto_json['firmaElectronica'] = documento_procesado['firmaElectronica']  # Agregar la firma electrónica al JSON

                ruta_json = gen_json.gen_json.create_fileJson(None, dicto_json, parametros)

                if not ruta_json:
                    logger.error(f"No se pudo crear el JSON para {codigoGen}")
                    return "ERROR: No se pudo crear JSON"

                send_emails_for_pending_documents.delay(codigoGen)
                resultado = documento_procesado['selloRecibido']
            else:
                resultado = estado

            #logger.info(f" procesar_documentos, sello obtenido: {resultado}")    
            return resultado
    except Exception as e:
        # Agrega manejo de excepciones y registra el error
        logger.error(f"Error en procesar_documentos: {e}", exc_info=True)
        resultado = f"Error en procesar_documentos: {e}"
        return resultado



@shared_task()
def sell_hellos(parametros):
    print(parametros)
     
      
def test_redis_connection(host, port):
    try:
        print(f"Probando conexión a Redis en {host}:{port}")
        redis_connection = redis.StrictRedis(host=host, port=port, decode_responses=True)
        redis_connection.ping()  # Intenta realizar un ping a Redis
        print("Conexión a Redis exitosa")
        redis_connection.close()

    except Exception as e:
        print(f"No se pudo conectar a Redis. Error: {e}")
        traceback.print_exc()


@shared_task(queue='default')
def invalidacion_documento(invalid_doc):
    try:
        # Crear una instancia de InvalidProcessor
        invalid_processor = invelid_doc.InvalidProcessor()
        invalid_data = invalid_processor.invalid_document(invalid_doc)
        logger.error(f"Información del data: {invalid_data}", exc_info=True)
        
        # Verificar si el documento está en los datos de retorno
        # Verificar si invalid_data es un diccionario antes de usar get()
        # if isinstance(invalid_data, dict):
        #     document = invalid_data.get('documento', None)
        # else:
        #     if not invalid_data:
        #         mensaje_error = "Error: No se recibió información de invalidación. Puede que el documento esté fuera del plazo permitido por MH o los datos del receptor son diferentes al documento emitido."
        #     else:
        #         mensaje_error = f"Error: invalid_data no es un diccionario. Valor recibido: {invalid_data}"
            
        #     logger.error(mensaje_error)
        #     return mensaje_error  
        if isinstance(invalid_data, dict):
            document = invalid_data.get('documento', None)
            if not document:
                msg = invalid_data.get('message') or invalid_data.get('error') or str(invalid_data)
                logger.error(f"Invalidación no completada: {msg}")
                return f"Invalidación no completada: {msg}"            
        
        #document = invalid_data.get('documento', None)
        #logger.error(f"Información del documento: {document}", exc_info=True)

        if document and document.estado == 'INVALIDADO':
            # Si el documento está INVALIDADO, escribir el archivo JSON y enviar correos electrónicos
            gen_json.gen_json.write_fileJSon(None, document)
            send_emails_for_pending_documents.delay(document.codigoGeneracion)
            return document.selloInvalidacion if document.selloInvalidacion else 'INVALIDADO'
        else:
            # Manejar otros estados o la ausencia del documento en los datos de retorno
            return 'Documento no encontrado o no está INVALIDADO'

    except Exception as e:
        # Manejar excepciones y registrar el error
        logger.error(f"Error en invalidacion_documento: {e}", exc_info=True)
        return f"Error en invalidacion_documento: {e}"
    # try:
    #     invalid_data =  invelid_doc.InvalidProcessor.invalid_document(None,invalid_doc)
    #     document = invalid_data['documento'] if 'documento' in invalid_data else None
    #     logger.info(f": {document}", exc_info=True)

    #     if document:
    #         if document.estado == 'INVALIDADO':            
    #         #doucmento = constructor_dicionario.DocumentoDiccionarioStruc.get_diccionario(invalid_doc['documento']['codigoGeneracion'])  
    #             if document:        
    #                 gen_json.gen_json.write_fileJSon(None, document)
    #                 send_emails_for_pending_documents.delay(document.codigoGeneracion)  
    #             return document.selloInvalidacion if document.selloInvalidacion  else 'INVALIDADO'

    # except Exception as e:
    #     # Agrega manejo de excepciones y registra el error
    #     logger.error(f"Error en invalidacion_documento: {e}", exc_info=True)
    #     return f"Error en invalidacion_documento: {e}"
