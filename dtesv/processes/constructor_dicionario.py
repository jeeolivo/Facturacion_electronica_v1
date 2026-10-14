
from dtesv.processes.builders import (
    identificacion_builder, emisor_builder, receptor_builder, documentoRelacionado_builder, cuerpoDocumento_builder, 
    resumen_builder, extension_builder, apendice_builder, ventaTercero_builder, otrosDocumentos_builder, compraTercero_builder
    )
from dtesv.processes.adapters import adapter_factory
from dtesv.processes.utils.schema_helper import SchemaHelper
from dtesv.models import Parametros
from decimal import Decimal
import dtesv.Apis.autentificador as autenticador
import dtesv.Apis.recepcion_dte as mh_recepciondte
import dtesv.Apis.firmador as firmador
import base64
import traceback
import logging
import json


logger = logging.getLogger(__name__)

def clean_text(value):
    return value.strip() if isinstance(value, str) else value   

class DocumentoDiccionarioStruc:
    def get_diccionario(Documentos_obj):
        logger.info("Creando el diccionario de datos para el documento a procesar...")
        try:
            document_list=[]
            for documentos in Documentos_obj:
                # codigoGen = documentos.codigoGeneracion
                dic_result = {
                    "identificacion": identificacion_builder.construir_identificacion(documentos),
                    "emisor": emisor_builder.construir_emisor(documentos),
                    "receptor": receptor_builder.construir_receptor(documentos),
                    "documentoRelacionado": documentoRelacionado_builder.construir_documentoRelacionado(documentos),
                    "otrosDocumentos": otrosDocumentos_builder.construir_otrosDocumentos(documentos),
                    "ventaTercero": ventaTercero_builder.construir_ventaTercero(documentos),
                    "compraTercero": compraTercero_builder.construir_compraTercero(documentos),
                    "cuerpoDocumento": cuerpoDocumento_builder.construir_cuerpo(documentos),
                    "resumen": resumen_builder.construir_resumen(documentos),
                    "extension": extension_builder.construir_extension(documentos),
                    "apendice": apendice_builder.construir_apendice(documentos)
                }               
                
                dic_result = adapter_factory.aplicar(
                    documentos,
                    dic_result
                )

                #LLENO MI LIST CON LOS DOCUMENTOS  
                document_list.append(dic_result)
                #logger.debug(f"Documento construido: {dic_result}")
               
            return document_list
        except Exception as e:
            logger.error(f"Error Constructor Diccionario: {e}", exc_info=True)
            traceback.print_exc()
            return None

      



    def validar_schema(document_list):
        try:

            resultados = []

            # Si llega un único documento como dict
            if isinstance(document_list, dict):
                document_list = [document_list]

            for documento in document_list:

                resultado = SchemaHelper.validar(documento) # Este es su orquestador de validación de schema

                resultados.append({
                    "codigoGeneracion": documento.get(
                        "identificacion",
                        {}
                    ).get(
                        "codigoGeneracion"
                    ),
                    "result": resultado
                })

            return resultados

        except Exception as e:
            logger.exception(
                "[CONSTRUCTOR_DICT] Excepción en validar_schema: %s",
                e
            )
            return None

    
    def get_documentos_firmados(dic_dtes,company_id):
        try:

                list_doc_firmados = []

                parametros = Parametros.objects.filter(
                    company_id=company_id
                ).first()

                # Permitir recibir un solo documento o una lista
                if isinstance(dic_dtes, dict):
                    dic_dtes = [dic_dtes]

                for dic_dte in dic_dtes:

                    dic_datos_dte = {
                        "nit": parametros.company_id.emisor.nit,
                        "activo": parametros.company_id.emisor.activo,
                        "passwordPri": base64.b64decode(
                            parametros.company_id.emisor.passwordpri
                        ).decode("utf-16"),
                        "dteJson": dic_dte
                    }

                    doc_firmado = firmador.get_dte_firma(
                        dic_datos_dte,
                        parametros
                    ).get_firma()
                    # logger.error(f"firma: {doc_firmado}")
                    doc_firmado["ambiente"] = dic_dte["identificacion"]["ambiente"]
                    doc_firmado["version"] = dic_dte["identificacion"]["version"]

                    if "tipoDte" in dic_dte["identificacion"]:
                        doc_firmado["tipoDte"] = dic_dte["identificacion"]["tipoDte"]

                    list_doc_firmados.append({
                        "dic_dte": dic_dte,
                        "doc_firmado": doc_firmado
                    })
                    # logger.error(f"firmas: {list_doc_firmados}")
                return (
                    list_doc_firmados,
                    parametros.company_id.emisor.nit,
                    base64.b64decode(
                        parametros.company_id.emisor.mh_auth
                    ).decode("utf-16"),
                    parametros
                )

        except Exception as e:
            logger.exception("Error Firmador Documentos")

            return None
    

    def procesar_documento_mh(documentos,company_id,eslote,idlote = None):
        # 1. Construcción inicial del DTE
        dic_dtes = DocumentoDiccionarioStruc.get_diccionario(documentos)

        if not dic_dtes:
            error_msg = "get_diccionario retornó un documento vacío."
            logger.error("[SENT_MH-DTE] %s", error_msg)

            return [{"estado": "error", "tipo": "constructor", "cadena": error_msg}]

        # 2. VALIDAR SCHEMA
        # IMPORTANTE:
        # Aquí todavía NO eliminamos tipoDte ni numeroControl.
        # validar_schema() necesita la estructura interna original para determinar el schema.
        validacion_schema = DocumentoDiccionarioStruc.validar_schema(dic_dtes)

        #logger.error("Resultado de validar_schema: %s",validacion_schema)

        # 3. Verificar resultado
        # ============================================================
        if validacion_schema is None:

            error_msg = ("validacion_schema returned None - schema validation failed")

            logger.error("[SENT_MH-DTE] %s", error_msg)

            return [{
                "estado": "error",
                "tipo": "schema",
                "cadena": error_msg
            }]

        if not isinstance(validacion_schema, list):

            error_msg = (
                "validacion_schema is not a list: "
                f"{type(validacion_schema)} - "
                f"{str(validacion_schema)}"
            )

            logger.error("[SENT_MH-DTE] %s", error_msg)

            return [{
                "estado": "error",
                "tipo": "schema",
                "cadena": error_msg
            }]

        errores_schema = []

        for item in validacion_schema:

            if item["result"] is not True:

                errores_schema.append({
                    "estado": "error",
                    "codigoGeneracion": item["codigoGeneracion"],
                    "tipo": "schema",
                    "cadena": item["result"]
                })

        if errores_schema:

            logger.error("Errores en validación de schema: %s", errores_schema)

            return errores_schema


        # 4. Preparar los documentos para MH.
        dic_dtes_preparados = []

        for dic_dte in dic_dtes:
            if not isinstance(dic_dte, dict):
                error_msg = (f"get_diccionario retornó un elemento que no es un diccionario: {type(dic_dte)}")

                logger.error("[SENT_MH-DTE] %s", error_msg)

                return [{"estado": "error", "tipo": "constructor", "cadena": error_msg}]

            # tipo_dte = identificacion.get("tipoDte")

            # Determinar schema
            schema_name = SchemaHelper.obtener_schema(dic_dte)

            #logger.info("[SENT_MH-DTE] codigoGeneracion=%s tipoDte=%s schema=%s", identificacion.get("codigoGeneracion"), tipo_dte, schema_name)

            # Preparar documento
            dic_dte_preparado = SchemaHelper.preparar_para_schema(dic_dte, schema_name)

            dic_dtes_preparados.append(dic_dte_preparado)       

        # 5. Documento Definitivo: A partir de aquí SOLO utilizamos dic_dtes_preparados
        dic_dtes = dic_dtes_preparados


        # # Esto me permite serializar objetos Decimal a JSON, para poder obtener el archivo legible para depurar.
        # # 6. Log del JSON REAL que continuará a firma y MH - Descomentar logger para ver
        class DecimalEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Decimal):
                    return float(obj)   # o str(obj)
                return super().default(obj)
        # logger.error(json.dumps(dic_dtes, cls=DecimalEncoder, indent=4, ensure_ascii=False))     
            

        # 7. IMPORTANTE: Firma del documento y envío a MH
        # NO volver a llamar get_diccionario()
        # NO volver a construir el DTE
        # NO utilizar una estructura anterior.
        # Se firma EXACTAMENTE dic_dtes, que es el mismo documento
        # que acabamos de validar.        
        resultado_firma = DocumentoDiccionarioStruc.get_documentos_firmados(dic_dtes, company_id)
        if resultado_firma is None:
            logger.error("[SENT_MH-DTE] get_documentos_firmados retornó None")
            return [{
                "estado": "error",
                "tipo": "firmador",
                "cadena": "No fue posible firmar el documento."
            }]

        documentos_firmados, nit, pwd, parametros = resultado_firma
        # logger.error("[DEBUG_FIRMA] documentos_firmados:\n%s", json.dumps(documentos_firmados, cls=DecimalEncoder, indent=4, ensure_ascii=False))

        # 8. Validar resultado de firma
        errores_firma = []

        for item in documentos_firmados:

            if item["doc_firmado"]["status"] != "OK":

                errores_firma.append({
                    "estado": item["doc_firmado"]["status"],
                    "codigoGeneracion": item["dic_dte"]["identificacion"]["codigoGeneracion"],
                    "tipo": "firmador",
                    "cadena": item["doc_firmado"]
                })

        if errores_firma:
            logger.error("Error en FirmaDocumentos: %s",errores_firma)

            return errores_firma

        # 9. Envío a MH
        # documentos_firmados proviene directamente del dic_dtes
        # que pasó la validación.        
        if eslote:
            return DocumentoDiccionarioStruc.generacion_dic_lote(
                nit,
                pwd,
                parametros,
                documentos_firmados,
                idlote
            )
        return DocumentoDiccionarioStruc.envio_mh(
            nit,
            pwd,
            parametros,
            documentos_firmados
        )


    def envio_mh(nit,pwd,Parametros,documentosFirmaddos):
        respuesta_dte_mh=[]
        # Obtener el token de autenticación
        uth_data = ({'user':nit,'pwd':pwd})
        #logger.info(f"datos_mh_authmh: {str(uth_data)}, firma generada: {documentosFirmaddos}", exc_info=True)
        token = autenticador.authenticate(uth_data,Parametros).get_token()
        #logger.error(f"Token de autenticación: {token}")
        #logger.info(f"envio_mh, la respuesta_mh_authmh: {token}", exc_info=True)
        traceback.print_exc()
        estado =  token['status']
        if estado == 'OK':
            
            for  doc_fimado in documentosFirmaddos:   
                #dic_to_repcion_mh = ({'ambiente':doc_fimado['doc_firmado']['ambiente'],'idEnvio': 1117,'version': int(doc_fimado['doc_firmado']['version']),'tipoDte': doc_fimado['doc_firmado']['tipoDte'],'documento':doc_fimado['doc_firmado']['body']})
                
                # Obtener tipoDte para el encabezado de envío a MH
                # Para DTE normales viene directamente como tipoDte.
                # Para eventos de retorno (tipo 18), el JSON final de MH utiliza tipoEvento en lugar de tipoDte.

                identificacion_firmada = doc_fimado["doc_firmado"]

                tipo_dte = DocumentoDiccionarioStruc.obtener_tipo_dte_envio(doc_fimado)

                if not tipo_dte:

                    return [{
                        "estado": "error",
                        "tipo": "envio",
                        "codigoGeneracion": doc_fimado.get("dic_dte", {}).get("identificacion", {}).get("codigoGeneracion"),
                        "cadena": "No fue posible determinar tipoDte ni tipoEvento para el documento."
                    }]

                dic_to_repcion_mh = {
                    "ambiente": identificacion_firmada["ambiente"],
                    "idEnvio": 1117,
                    "version": int(
                        identificacion_firmada["version"]
                    ),
                    "tipoDte": tipo_dte,
                    "documento": identificacion_firmada["body"]
                }
                # logger.error(f"Datos a enviar a MH(Similar POSTMAN): {dic_to_repcion_mh}", exc_info=True)
                dic_process = ({'auth':token['body']['token'],'documento':dic_to_repcion_mh})
                mh_result = mh_recepciondte.post_recepciondte(dic_process,Parametros).sent_data()
                
                # 1. Normalizar mh_result
                if isinstance(mh_result, list):
                    mh_result = mh_result[0] if mh_result else {}

                # 2. VALIDAR ESTRUCTURA MÍNIMA
                codigo_gen = mh_result.get('codigoGeneracion')
                if not codigo_gen:
                    logger.error(f"Respuesta MH sin codigoGeneracion: {mh_result}")
                    # opcional: marcar estado para evitar crashes posteriores
                    mh_result['estado'] = mh_result.get('estado', 'ERROR')               
               
                mh_result['dic_dte'] = doc_fimado['dic_dte']
                mh_result['firmaElectronica'] = dic_process['documento']       # Aqui registro la firma electronica que se envio a MH, para poderla guardar en la base de datos y poderla consultar posteriormente.         
                mh_result['tipo'] = 'mh_log'

                if 'observaciones' in mh_result and not mh_result['observaciones']:
                    mh_result['observaciones'] = ['.']

                estado = mh_result.get('estado')
                descripcion = mh_result.get('descripcionMsg', '')                    
                
                # evaluemos si el documento ya esta registrado en MH
                #if mh_result['estado'] =='RECHAZADO' and '[identificacion.codigoGeneracion] YA EXISTE UN REGISTRO CON ESE VALOR' in mh_result['descripcionMsg'] :
                # if estado == 'RECHAZADO' and '[identificacion.codigoGeneracion] YA EXISTE UN REGISTRO CON ESE VALOR' in descripcion:
                     
                #    dic_con={'nitEmisor':nit,'tdte':doc_fimado['doc_firmado']['tipoDte'],'codigoGeneracion':mh_result['codigoGeneracion']}
                #    dic_consulta = ({'auth':token['body']['token'],'documento':dic_con})
                #    #logger.error(f"Datos a enviar para consulta: {dic_consulta}")

                codigo_gen = (mh_result.get('codigoGeneracion')
                            or doc_fimado['dic_dte']['identificacion']['codigoGeneracion'])
                ya_existe = (estado == 'RECHAZADO'
                            and 'YA EXISTE UN REGISTRO' in descripcion)
                sin_respuesta_mh = not mh_result.get('codigoGeneracion')

                if ya_existe or sin_respuesta_mh:
                    dic_consulta = {
                        'auth': token['body']['token'],
                        'documento': {'nitEmisor': nit,
                                    'tdte': doc_fimado['doc_firmado']['tipoDte'],
                                    'codigoGeneracion': codigo_gen}}
                    new_data = mh_recepciondte.post_consultadte(dic_consulta, Parametros).sent_data() or {}

                    if new_data.get('estado') == 'PROCESADO' and new_data.get('selloRecibido'):
                        mh_result['estado'] = 'PROCESADO'
                        mh_result['codigoGeneracion'] = codigo_gen
                        mh_result['selloRecibido'] = new_data['selloRecibido']
                        mh_result['descripcionMsg'] = new_data.get('descripcionMsg', 'RECIBIDO')
                        mh_result['observaciones'] = new_data.get('observaciones') or ['.']
                        mh_result['firmaElectronica'] = doc_fimado['doc_firmado']['body']
                    else:
                        logger.error("No se pudo confirmar en MH el documento %s: %s", codigo_gen, new_data)

                respuesta_dte_mh.append(mh_result)
                # if estado == 'RECHAZADO' and '[identificacion.codigoGeneracion] YA EXISTE UN REGISTRO CON ESE VALOR' in descripcion:
                #     dic_con = {
                #         'nitEmisor': nit,
                #         'tdte': doc_fimado['doc_firmado']['tipoDte'],
                #         'codigoGeneracion': mh_result['codigoGeneracion']
                #     }
                #     dic_consulta = {'auth': token['body']['token'], 'documento': dic_con}
                #     new_data = mh_recepciondte.post_consultadte(dic_consulta, Parametros).sent_data() or {}

                #     if new_data.get('estado') == "PROCESADO" and new_data.get('selloRecibido'):
                #         mh_result['estado'] = 'PROCESADO'
                #         mh_result['selloRecibido'] = new_data['selloRecibido']
                #         mh_result['firmaElectronica'] = doc_fimado['doc_firmado']['body']
                #     else:
                #         logger.error("No se pudo confirmar en MH el documento %s: %s",
                #                      mh_result.get('codigoGeneracion'), new_data)

                # respuesta_dte_mh.append(mh_result)

                #    new_data = mh_recepciondte.post_consultadte(dic_consulta,Parametros).sent_data()                  
                #    #logger.error(f"Error en Validar Schema PRUEBA token!: {new_data}", exc_info=True)
                #    if  new_data['estado'] == "PROCESADO": #new_data['estadoDoc'] == "Transmitido satisfactoriamente":                      
                #        mh_result['estado'] =  'PROCESADO' 
                #        mh_result['selloRecibido'] =  new_data['selloRecibido']  #new_data['selloVal'] 
                #        mh_result['firmaElectronica'] = doc_fimado['doc_firmado']['body']       # Aqui registro la firma electronica que se envio a MH, para poderla guardar en la base de datos y poderla consultar posteriormente.         
                #    else:
                #        logger.error("El documento consultado no contiene el campo esperado 'estadoDoc' o 'selloVal'")
                       
                # respuesta_dte_mh.append(mh_result)
        else:
            
            token['codigoGeneracion'] = documentosFirmaddos[0]['dic_dte']['identificacion']['codigoGeneracion']
            respuesta_dte_mh.append(token) 
            logger.info(f"envio_mh, los codigo tienen coincidencia: {token}", exc_info=True)

        #logger.error(f"datos_firmador: {documentosFirmaddos[0]}", exc_info=True)
        #if documentosFirmaddos[0]['dic_dte']['identificacion']['tipoDte'] == '07':
        #    gen_json.gen_json.create_fileJSonLocal(None, documentosFirmaddos[0])    
        logger.info(f" El proceso envio_mh contiene: {respuesta_dte_mh}", exc_info=True)
        traceback.print_exc()
        return respuesta_dte_mh
        
    def generacion_dic_lote(nit,pwd,Parametros,documentosFirmaddos,idlote):
        doc_firmado = [doc['doc_firmado']['body'] for doc in documentosFirmaddos]
        #uuid4 = uuid.uuid4()
        respuesta_dte_mh=[]
        uth_data = ({'user':nit,'pwd':pwd})
        token = autenticador.authenticate(uth_data,Parametros).get_token()
        dic_to_repcion_mh = ({'ambiente':Parametros.ambiente.codigo,'idEnvio': idlote,'version': 1,'nitEmisor':nit,'documentos':doc_firmado})
        dic_process = ({'auth':token['body']['token'],'documento':dic_to_repcion_mh})
        mh_result = mh_recepciondte.post_recepciondteLote(dic_process,Parametros).sent_data()
        respuesta_dte_mh.append(mh_result)

        return respuesta_dte_mh
    
    
        
    def envio_contingencia_mh(data,company_id):
        logger.error(f"Ingresando al proceso de contingencia, empresa_id {company_id}",exc_info=True)
        if len(data)>0:
            list_doc_conting=[]
            items_con_result_falso = []
            items_con_status_firma_falso = []
            list_doc_conting.append(data)
            
            validacion_schema = DocumentoDiccionarioStruc.validar_schema(list_doc_conting)
            #logger.error(f"Nueva validacion de schema, {validacion_schema}",exc_info=True)
            for item in validacion_schema:
                if item['result'] != True:
                    error = {
                        'estado':'error',
                        'codigoGeneracion':item['codigoGeneracion'],
                        'tipo':'schema',
                        'cadena':item['result']
                    }
                    items_con_result_falso.append(error)

        
            if len(items_con_result_falso) == 0:
            ## Firma de los documentos
                documentos_firmados,nit,pwd,Parametros = DocumentoDiccionarioStruc.get_documentos_firmados(list_doc_conting,company_id)

                if documentos_firmados is None or nit is None or pwd is None or Parametros is None:
                    logger.error("Error al firmar documentos: uno de los valores devueltos es None")
                    return {"error": "Error en la firma de documentos. Datos incompletos."}

                logger.error(f"Revisando el documento firmado: {documentos_firmados}")
                for item in documentos_firmados:
                    if item['doc_firmado']['status'] != 'OK':
                        error = {
                            'estado':item['doc_firmado']['status'],
                            'codigoGeneracion':item['dic_dte']['identificacion']['codigoGeneracion'],
                            'tipo':'firmador',
                            'cadena':item['doc_firmado']['body']['mensaje']
                        }
                        items_con_status_firma_falso.append(error)
                # Si no hubo errores en la firma                        
                if len(items_con_status_firma_falso) == 0:
                ## Autenticacion y envio a MH
                    uth_data = ({'user':nit,'pwd':pwd})
                    token = autenticador.authenticate(uth_data,Parametros).get_token()

                    if token is None:
                        logger.error("Token es None después de la autenticación")
                        return {"error": "Error en la autenticación. Token no obtenido."}

                    logger.info(f"Token obtenido: {token}", exc_info=True)
                    if token['status'] == 'OK':
                        respuesta_dte_mh=[]
                        for  doc_fimado in documentos_firmados:                    
                            dic_to_repcion_mh = ({'nit':nit,'documento':doc_fimado['doc_firmado']['body']})
                            dic_process = ({'auth':token['body']['token'],'documento':dic_to_repcion_mh})
                            logger.info(f"Datos del documento firmado a enviar a MH: {dic_process}", exc_info=True)                            
                            mh_result = mh_recepciondte.post_recepcioncontingencia(dic_process,Parametros).sent_data()

                            if mh_result is None:
                                logger.error("Error al enviar documento a MH: el resultado es None")
                                return {"error": "Error al enviar documento a MH. Resultado no recibido."}
                            
                            logger.info(f"Resultado de la recepción en MH: {mh_result}", exc_info=True)
                            mh_result['dic_dte'] = doc_fimado['dic_dte']
                            respuesta_dte_mh.append(mh_result)
                        return respuesta_dte_mh
                    else:
                        logger.error(f"Error de autenticación: {token}", exc_info=True)
                        return items_con_status_firma_falso
                else:
                    logger.error(f"Error de autenticación: {token}", exc_info=True)
                    return items_con_status_firma_falso

            else:
                logger.error(f"Errores en la firma de documentos: {items_con_status_firma_falso}", exc_info=True)
                return items_con_result_falso
        else:
            logger.error('La longitud de la data no cumple los requisitos',exc_info=True)
            return items_con_result_falso



    @staticmethod
    def obtener_tipo_dte_envio(doc_fimado):

        # 1. Obtener el DTE original que fue firmado
        dic_dte = doc_fimado.get("dic_dte", {})

        if not isinstance(dic_dte, dict):
            logger.error("[SENT_MH-DTE] dic_dte no es un diccionario: %s", type(dic_dte))
            return None

        identificacion = dic_dte.get("identificacion", {})

        if not isinstance(identificacion, dict):
            logger.error("[SENT_MH-DTE] identificacion no es un diccionario.")
            return None

        # ------------------------------------------------------------
        # 2. DTE normal: tipoDte puede venir directamente en doc_firmado
        # ------------------------------------------------------------
        tipo_dte = identificacion.get("tipoDte")

        if tipo_dte:
            return tipo_dte

        # ------------------------------------------------------------
        # 3. Evento: intentar obtener tipoEvento desde doc_firmado
        # ------------------------------------------------------------
        tipo_evento = identificacion.get("tipoEvento")

        if tipo_evento:
            return tipo_evento

        # ------------------------------------------------------------
        # 4. Si no se encontró tipoDte ni tipoEvento en doc_firmado, intentar obtener desde el dic_dte original
        # ------------------------------------------------------------
        logger.error(
            "[SENT_MH-DTE] No se encontró tipoDte ni tipoEvento "
            "en doc_firmado ni en body."
        )

        return None            