import json
from venv import logger
import requests
from datetime import datetime

from dtesv.models import Documentos ,Emisor,Receptor,DocumentosDetalle,ExtencionEntrega,DocumentosAsociados,Pagos,Parametros,C015Tributos,Company
import dtesv.processes.validate_schema as  validateSchema
import dtesv.processes.create_pdf as  gen_pdf
import dtesv.processes.create_json as  gen_json
import dtesv.Apis.firmador as firmador
import dtesv.Apis.autentificador as autenticador
import dtesv.Apis.invalidacion as mh_invalidacion
import dtesv.views.sent_email as enviar_email
import dtesv.processes.constructor_dicionario as get_dic_documento
import os
import pytz

import base64


class InvalidProcessor:
    def invalid_document(self,invalid_doc):
        import celery
        logger.error(f"Running task ID: {celery.current_task.request.id}, Código generación: {invalid_doc['documento']['codigoGeneracion']}")        
        result = ''
        fecha_actual = datetime.now()
        fecha_actual_str = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")
    ##     company_ids = Company.objects.filter(emisor__nombre=invalid_doc['emisor']['nombre']).values_list('id', flat=True)
    ##    logger.error(f" 1. Informacion compania: {company_ids}", exc_info=True)
    ##    parametros = Parametros.objects.filter(company_id = company_ids[0]).first()
    ##    logger.error(f" 2. Informacion parametros: {parametros}", exc_info=True)
    ##    emisor_data =Emisor.objects.filter(nit = invalid_doc['emisor']['nit']).first() 
    ##    logger.error(f" 3. Informacion emisor: {emisor_data}", exc_info=True)
    ##    documentos = Documentos.objects.filter(emisor_id=emisor_data.id, codigoGeneracion=invalid_doc['documento']['codigoGeneracion']).first() 
    ##    logger.error(f" 4. Informacion documento: {documentos}", exc_info=True) 


        # Obtener company_ids
        try:
            company_ids = Company.objects.filter(emisor__nombre=invalid_doc['emisor']['nombre']).values_list('id', flat=True)
        except Exception as e:
            logger.error(f"Error fetching company_ids: {e}", exc_info=True)
            return {'error': f"Error fetching company_ids: {e}"}
        #logger.error(f"1. Informacion compania: {company_ids}", exc_info=True)

        if not company_ids:
            return {'error': 'No se encontró ningún company_id para el emisor dado.'}

        # Tomar el primer company_id encontrado
        company_id = company_ids[0]
        try:
            parametros = Parametros.objects.filter(company_id=company_id).first()
        except Exception as e:
            logger.error(f"Error fetching parametros: {e}", exc_info=True)
            return {'error': f"Error fetching parametros: {e}"}
        #logger.error(f"2. Informacion parametros: {parametros}", exc_info=True)

        if not parametros:
            return {'error': 'No se encontró ningún parámetro para el company_id dado.'}

        try:
            emisor_data = Emisor.objects.filter(nit=invalid_doc['emisor']['nit']).first()
            logger.error(f"Emisor Data Found: {emisor_data}")
        except Exception as e:
            logger.error(f"Error fetching emisor_data: {e}", exc_info=True)
            return {'error': f"Error fetching emisor_data: {e}"}

        #logger.error(f"3. Informacion emisor: {emisor_data}", exc_info=True)

        if not emisor_data:
            return {'error': 'No se encontró información del emisor con el nit dado.'}

        try:
            documentos = Documentos.objects.filter(emisor_id=emisor_data.id, codigoGeneracion=invalid_doc['documento']['codigoGeneracion']).first()
            logger.error(f"Documentos Found: {documentos}")
        except Exception as e:
            logger.error(f"Error fetching documentos: {e}", exc_info=True)
            return {'error': f"Error fetching documentos: {e}"}

        #logger.error(f"4. Informacion documento: {documentos}", exc_info=True)

        if not documentos:
            return {'error': 'No se encontró ningún documento con el código de generación dado.'}

        # 2026-10-07: Inicio data Original
        # if (documentos.estado == 'PROCESADO' or (documentos.estado == 'ERR_INVALI' and documentos.tipodocumento == '01')) and documentos.selloRecibido:
        #     validacion_schema =  validateSchema.schemaValidate({'tipo':'anulacion-schema-v2','json':invalid_doc}).validar_schema()
        #     #logger.error(f"4.1 Validacion del Schema: {validacion_schema}", exc_info=True)
        #     if  validacion_schema == True:
        #         dic_datos_dte = ({ 'nit':emisor_data.nit,'activo':emisor_data.activo,'passwordPri':base64.b64decode(emisor_data.passwordpri).decode("utf-16") , 'dteJson':invalid_doc})
        #         dic_otra_info = ({'ambiente':invalid_doc['identificacion']['ambiente'],'version':invalid_doc['identificacion']['version'],'tipoDte':invalid_doc['documento']['tipoDte'],'pwd':base64.b64decode(emisor_data.mh_auth).decode("utf-16")})    
        #         gen_json.gen_json.save_fileJSon(None,dic_datos_dte) 
        #        # nombre_archivo = invalid_doc['documento']['codigoGeneracion']+'.json'
        #        # mi_json = json.dumps(dic_datos_dte)
        #        # with open(nombre_archivo, 'w') as archivo:
        #        #     archivo.write(mi_json)

        #         result_firma = firmador.get_dte_firma(dic_datos_dte,parametros).get_firma()
        #         logger.error(f" 5. Informacion de firma: {result_firma}", exc_info=True)
        #         if result_firma['status'] != 'OK':
        #             result = result_firma
        #             logger.error(f" Resultado de firma: {result}", exc_info=True)
        #         else:
        #             uth_data = ({'user':emisor_data.nit,'pwd':dic_otra_info['pwd']})
        #             token = autenticador.authenticate(uth_data,parametros).get_token()  
        #             if token['status'] == 'OK':
        #                     dic_to_repcion_mh = ({'ambiente':dic_otra_info['ambiente'],'idEnvio': 1117,'version': int(dic_otra_info['version']),'tipoDte': dic_otra_info['tipoDte'],'documento':result_firma['body']})
        #                     dic_process = ({'auth':token['body']['token'],'documento':dic_to_repcion_mh})
        #                     respuesta_dte_mh = mh_invalidacion.post_recepciondte(dic_process,parametros).sent_data()
        #                     logger.error(f"6. Esta es la respuesta de la invalidacion: {respuesta_dte_mh}")

        #                     # Validar si 'estado' o 'status' existen en la respuesta
        #                     estado = respuesta_dte_mh.get('estado')
        #                     status = respuesta_dte_mh.get('status')

        #                     if estado == 'RECHAZADO' or estado == 'ERROR':
        #                     #if respuesta_dte_mh['estado'] == 'RECHAZADO':                                
        #                         cadena = documentos.observaciones_mh if documentos.observaciones_mh else "."
        #                         mensaje_mh = respuesta_dte_mh['descripcionMsg'] if respuesta_dte_mh['descripcionMsg'] else "."
        #                         if isinstance(respuesta_dte_mh['observaciones'], list) and len(respuesta_dte_mh['observaciones']) >0:
        #                             cadena =  fecha_actual_str +':'+mensaje_mh+"-"+(','.join(respuesta_dte_mh['observaciones']))+','+cadena
        #                         else:
        #                             cadena = fecha_actual_str + ':'+respuesta_dte_mh['descripcionMsg'] +','+cadena
        #                         result = respuesta_dte_mh
        #                         data_update ={'tipo':'mh_error','estado':respuesta_dte_mh['estado'],'cadena':cadena}
        #                         InvalidProcessor.update_documento(self,documentos,data_update)
        #                     else:
        #                         data_update ={'tipo':'mh_log','estado':'PROCESADO','cadena':respuesta_dte_mh,
        #                                       'motivoAnulacion': invalid_doc['motivo']['motivoAnulacion']} 
                                
        #                         document_up = InvalidProcessor.update_documento(self,documentos,data_update)
        #                         respuesta_dte_mh ['documento'] = document_up
        #                         result = respuesta_dte_mh
        #     else:
        #         result = {'message':validacion_schema,}      
        #         historico = documentos.observacion_proceso
        #         if historico:
                    
        #             result = {"message": fecha_actual_str+':' +'validacion_schema:'+validacion_schema +','+ historico,'codigoGeneracion':invalid_doc['documento']['codigoGeneracion']}
        #         else:
        #             result =  {"message":fecha_actual_str+':' +'validacion_schema:'+validacion_schema ,'codigoGeneracion':invalid_doc['documento']['codigoGeneracion']}
        #         data_update ={'tipo':'validacion_schema','estado':'ERROR','cadena':'validacion_schema: ' + validacion_schema}
        #         #self.update_documento(documentos,data_update)
        #         document_up = InvalidProcessor.update_documento(self,documentos,data_update)
        # 2026-10-07: Fin data Original 
        # 2026-10-07: INICIA NUEVA data 
        ESTADOS_INVALIDABLES = ('PROCESADO', 'ERR_INVALI')
        cod_gen = invalid_doc['documento']['codigoGeneracion']

        if documentos.estado in ESTADOS_INVALIDABLES and documentos.selloRecibido:
            validacion_schema = validateSchema.schemaValidate({'tipo': 'anulacion-schema-v2', 'json': invalid_doc}).validar_schema()
            if validacion_schema == True:
                dic_datos_dte = ({'nit': emisor_data.nit, 'activo': emisor_data.activo, 'passwordPri': base64.b64decode(emisor_data.passwordpri).decode("utf-16"), 'dteJson': invalid_doc})
                dic_otra_info = ({'ambiente': invalid_doc['identificacion']['ambiente'], 'version': invalid_doc['identificacion']['version'], 'tipoDte': invalid_doc['documento']['tipoDte'], 'pwd': base64.b64decode(emisor_data.mh_auth).decode("utf-16")})
                gen_json.gen_json.save_fileJSon(None, dic_datos_dte)

                result_firma = firmador.get_dte_firma(dic_datos_dte, parametros).get_firma()
                logger.error(f" 5. Informacion de firma: {result_firma}", exc_info=True)
                if result_firma['status'] != 'OK':
                    result = result_firma
                    logger.error(f" Resultado de firma: {result}", exc_info=True)
                else:
                    uth_data = ({'user': emisor_data.nit, 'pwd': dic_otra_info['pwd']})
                    token = autenticador.authenticate(uth_data, parametros).get_token()
                    if token['status'] == 'OK':
                        dic_to_repcion_mh = ({'ambiente':dic_otra_info['ambiente'],'idEnvio': 1117,'version': int(dic_otra_info['version']),'tipoDte': dic_otra_info['tipoDte'],'documento':result_firma['body']})
                        dic_process = ({'auth':token['body']['token'],'documento':dic_to_repcion_mh})
                        respuesta_dte_mh = mh_invalidacion.post_recepciondte(dic_process,parametros).sent_data()
                        logger.error(f"6. Esta es la respuesta de la invalidacion: {respuesta_dte_mh}")

                        # Validar si 'estado' o 'status' existen en la respuesta
                        estado = respuesta_dte_mh.get('estado')
                        status = respuesta_dte_mh.get('status')

                        if estado == 'RECHAZADO' or estado == 'ERROR':
                        #if respuesta_dte_mh['estado'] == 'RECHAZADO':                                
                            cadena = documentos.observaciones_mh if documentos.observaciones_mh else "."
                            mensaje_mh = respuesta_dte_mh['descripcionMsg'] if respuesta_dte_mh['descripcionMsg'] else "."
                            if isinstance(respuesta_dte_mh['observaciones'], list) and len(respuesta_dte_mh['observaciones']) >0:
                                cadena =  fecha_actual_str +':'+mensaje_mh+"-"+(','.join(respuesta_dte_mh['observaciones']))+','+cadena
                            else:
                                cadena = fecha_actual_str + ':'+respuesta_dte_mh['descripcionMsg'] +','+cadena
                            result = respuesta_dte_mh
                            data_update ={'tipo':'mh_error','estado':respuesta_dte_mh['estado'],'cadena':cadena}
                            InvalidProcessor.update_documento(self,documentos,data_update)
                        else:
                            data_update ={'tipo':'mh_log','estado':'PROCESADO','cadena':respuesta_dte_mh,
                                          'motivoAnulacion': invalid_doc['motivo']['motivoAnulacion']} 
                                
                            document_up = InvalidProcessor.update_documento(self,documentos,data_update)
                            respuesta_dte_mh ['documento'] = document_up
                            result = respuesta_dte_mh
                    else:
                        result = {'message': f"Error de autenticación con MH: {token}", 'codigoGeneracion': cod_gen}
            else:
                historico = documentos.observacion_proceso
                msg = fecha_actual_str + ':validacion_schema:' + str(validacion_schema)
                if historico:
                    msg += ',' + historico
                result = {'message': msg, 'codigoGeneracion': cod_gen}
                data_update = {'tipo': 'validacion_schema', 'estado': 'ERROR', 'cadena': 'validacion_schema: ' + str(validacion_schema)}
                InvalidProcessor.update_documento(self, documentos, data_update)
        else:
            result = {'message': f"Documento no invalidable: estado={documentos.estado}, "
                                f"selloRecibido={'sí' if documentos.selloRecibido else 'no'}",
                    'codigoGeneracion': cod_gen}

        logger.error(f"Este es el result de la invalidacion: {result}")
        return result         


    # def update_documento(self,document,result):
    #     fecha_actual = datetime.now()            
    #     zona_horaria = pytz.timezone('America/El_Salvador')
    #     fecha_actual_sv = fecha_actual.astimezone(zona_horaria)
    #     document.estado_anulado =  result['estado']   

    #     try:
    #         if result['tipo'] == 'mh_log':
    #             if result['cadena']['selloRecibido']:
    #                 document.selloInvalidacion =  result['cadena']['selloRecibido']
    #                 document.observaciones_mh =result['cadena']['descripcionMsg'] + (','.join(result['cadena']['codigoGeneracion'])) if result['cadena']['observaciones'] else "."
    #                 document.estado = 'INVALIDADO'
    #                 document.motivoInvalidacion = result['motivoAnulacion']
    #                 document.codigoGenInvalida = result['cadena']['codigoGeneracion']
    #             else:                
    #                 document.observaciones_mh ='INVALIDACION:'+result['cadena']['descripcionMsg'] + (','.join(result['cadena']['codigoGeneracion'])) if result['cadena']['observaciones'] else 'INVALIDACION:' + result['cadena']['descripcionMsg']
    #         elif  not  result['tipo'] =='validacion_schema':
    #             document.estado = 'ERR_INVALI'
    #             document.observaciones_mh =  result['cadena']
    #             #document.codigoGenInvalida = result['cadena']['codigoGeneracion']
    #         else:
    #             document.estado = 'ERR_INVALI'
    #             document.observacion_proceso = "Error en el proceso de invalidación, " + result['cadena']
    #             #document.codigoGenInvalida = result['cadena']['codigoGeneracion']
    #     except KeyError as e:
    #         # Manejo específico de errores KeyError
    #         document.estado = 'ERR_INVALI'
    #         document.observaciones_mh = f"Error al invalidar: {str(e)}"
    #     except Exception as e:
    #         # Manejo general de otros errores
    #         document.estado = 'ERR_INVALI'
    #         document.observaciones_mh = f"Error inesperado invalidar: {str(e)}"

    #     document.fecha_anula_mh = fecha_actual

    #     document.save()

    #     return document

    def update_documento(self, document, result):
        from django.utils import timezone
        fecha_actual = timezone.now()   # si USE_TZ=False, usa datetime.now() con la zona de El Salvador

        document.estado_anulado = result.get('estado')

        try:
            tipo = result.get('tipo')

            if tipo == 'mh_log':
                cadena = result['cadena']
                desc = cadena.get('descripcionMsg') or ''
                obs = cadena.get('observaciones')
                obs_txt = ','.join(map(str, obs)) if isinstance(obs, list) and obs else ''
                fh = cadena.get('fhProcesamiento') or ''          # ej. '07/10/2026 18:31:04'
                texto = ' '.join(p for p in [desc, obs_txt, f"({fh})" if fh else ''] if p) or '.'

                if cadena.get('selloRecibido'):
                    document.selloInvalidacion = cadena['selloRecibido']
                    document.observaciones_mh = texto
                    document.motivoInvalidacion = result.get('motivoAnulacion')
                    document.codigoGenInvalida = cadena.get('codigoGeneracion') or document.codigoGenInvalida                    
                    document.estado = 'INVALIDADO'
                else:
                    document.observaciones_mh = 'INVALIDACION:' + texto

            elif tipo == 'validacion_schema':
                document.estado = 'ERR_INVALI'
                document.observacion_proceso = "Error en el proceso de invalidación, " + str(result.get('cadena'))

            else:  # mh_error y cualquier otro tipo
                document.estado = 'ERR_INVALI'
                document.observaciones_mh = str(result.get('cadena'))

        except Exception as e:
            # Solo degradar el estado si no se llegó a invalidar
            if document.estado != 'INVALIDADO':
                document.estado = 'ERR_INVALI'
            document.observaciones_mh = f"Error al guardar resultado de invalidación: {e}"
            logger.error(f"update_documento falló: {e}", exc_info=True)

        document.fecha_anula_mh = fecha_actual
        document.save()
        return document
    