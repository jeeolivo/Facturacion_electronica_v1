# En tu vista Django
from django.views import View
from django.http import JsonResponse
from dtesv.processes.procesor_runner import run_processor,MainProcessor
from dtesv.models import Documentos,DocumentosDetalle,C002TipoDocumento,C016CondicionOperacion,C025BienesRemitidosTitulos, C015Tributos,Parametros,Company
from dtesv.tasks import send_emails_for_pending_documents,sell_hellos,procesar_documentos
from django.forms.models import model_to_dict
from dtesv.tools.consecutivo_local import ConsecutivosSF
import uuid
import requests
from datetime import datetime,timedelta,date
from dtesv.Apis import consecutivos
import logging
import traceback

logger = logging.getLogger('celery')

class GenerateNotaCredito(View):
    def post(self, request, *args, **kwargs):
        try:
            # Llama a la función que ejecuta el procesador
            logger.info("Ingresando a la vista GenerateNotaCredito")
            company_id = Company.objects.filter(users=request.user).first()
            parametro = company_id.parametros_company_id.first()
            codigoGeneracion =  kwargs['codigoGeneracion']

            #documentos = Documentos.objects.filter(codigoGeneracion=codigoGeneracion,en_contingencia=False).first()
            # 2024-09-05: Filtrar documentos, pero permitir la posibilidad de procesar contingencias si es necesario
            documentos = Documentos.objects.filter(codigoGeneracion=codigoGeneracion).exclude(estado='ANULADO').first()
            
            if documentos and documentos.en_contingencia:
                logger.warning(f"El documento {codigoGeneracion} está en contingencia.")
                # Aquí podrías decidir si lo procesas o no, por ejemplo, devolver un mensaje
                return JsonResponse({'success': False, 'message': 'El documento está en contingencia y no puede procesarse una Nota de Crédito.'})

            # Nota_credito = Documentos.objects.filter(numeroDocumento_rel_guid=codigoGeneracion).first()
            # if documentos and not Nota_credito:

            Nota_credito = Documentos.objects.filter(numeroDocumento_rel_guid=codigoGeneracion).first()

            # Si existe una NC vinculada, verificar su estado
            if Nota_credito:
                logger.info(f"Se encontró NC vinculada al documento {codigoGeneracion}: NC={Nota_credito.codigoGeneracion}, estado={Nota_credito.estado}")

                # Si la NC existente está anulada, se permite continuar
                if Nota_credito.estado == 'INVALIDADO':
                    logger.info(
                        f"La NC {Nota_credito.codigoGeneracion} está INVALIDADO. "
                        f"Se permite generar/procesar una nueva NC."
                    )
                else:
                    result = 'Documento ya cuenta con Nota de Crédito para Anulación'
                    logger.warning(result)
                    return JsonResponse({
                        'success': False,
                        'message': result
                    })

            if documentos:
                
                fecha_actuals = datetime.now().date()
                diferencia = fecha_actuals - documentos.fecEmi
                if diferencia < timedelta(days=90):
                    guid = str(uuid.uuid4()).upper()           
                    documento_dict = model_to_dict(documentos)
                    documento_dict['codigoGeneracion'] = guid
                    
                    # # 5. Verificar si ya existe una Nota de Débito para este CCF
                    # nota_credito_existente = Documentos.objects.filter(numeroDocumento_rel_guid=Nota_credito, tipodocumento__codigo='05').first()
                    # logger.info(f"Nota de Crédito existente: {nota_credito_existente}")
                    # if nota_credito_existente:
                    #     return JsonResponse({'success': False, 'message': 'Documento ya cuenta con una Nota de Crédito.'})


                    detalles_lista = [model_to_dict(detalle) for detalle in documentos.documento_detalle_codigoGeneracion_id.all()]
                    DTE_cosecutivo = ''

                    ESTABLECIMIENTO_POR_SUCURSAL = {
                        '0': 'M001',
                        '1': 'S001',
                        '2': 'S002',
                    }

                    try:
                        #with transaction.atomic():
                        # Manejar transacciones en el bloque de código donde se crean y actualizan los documentos. 
                        # Esto asegura que todas las operaciones de base de datos dentro del bloque se consideren una sola transacción. 
                        # Si alguna operación falla, la transacción se revierte para evitar inconsistencias en la base de datos
                            cod_sucursal = documentos.cod_sucursal
                            establecimiento = ESTABLECIMIENTO_POR_SUCURSAL.get(str(cod_sucursal), "M001")
                            logger.info(f"Valor de Sucursal obtenido: {cod_sucursal}, codigo: {establecimiento}, codigoGeneracion = {codigoGeneracion}")

                            fecha_actual = datetime.now().strftime('%Y-%m-%d')
                            tipo_doc = '05'
                            consecutivo_sf = ConsecutivosSF(tipo_doc, parametro, sucursal = cod_sucursal)
                            Nconsecutivos = consecutivo_sf.get()
                            logger.info(f"Valor de Nconsecutivos obtenido: {Nconsecutivos}")

                            if 'datos' in Nconsecutivos:
                                nuevo_consecutivo = '{:015}'.format(int(Nconsecutivos['datos']))
                                logger.info(f"Nuevo consecutivo formateado: {nuevo_consecutivo}")

                                documento_dict['numeroDocumento_rel_guid'] = documentos.codigoGeneracion
                                documento_dict['numeroDocumento_rel_corr'] = guid
                                DTE_cosecutivo = f'DTE-05-{establecimiento}P001-' + Nconsecutivos['datos']
                                documento_dict['selloRecibido'] = None
                                documento_dict['tipodocumento'] = C002TipoDocumento.objects.get(codigo='05')
                                documento_dict['clase_documento'] = 'D'
                                documento_dict['fecEmi'] = fecha_actual
                                documento_dict['num_documento'] = Nconsecutivos['datos']
                                documento_dict['estado'] = 'Nuevo'
                                documento_dict['numeroControl'] = DTE_cosecutivo
                                documento_dict['codigoGeneracion'] = guid
                                documento_dict['observaciones_mh'] = None
                                documento_dict['montoTotalOperacion'] = documentos.totalPagar
                                documento_dict['observacion_proceso'] = f'Nota de Credito que Anula al Documento: {documentos.codigoGeneracion}, Con numero ERP: {documentos.num_documento}, Esta NC no existe en Softland, Create: {request.user}'
                                documento_dict['condicionOperacion'] = documentos.condicionOperacion
                                documento_dict['codigo_iva'] = documentos.codigo_iva
                                documento_dict['bienTitulo'] = C025BienesRemitidosTitulos.objects.get(codigo='01')
                                documento_dict['receptor_id'] = documentos.receptor_id
                                documento_dict['emisor_id'] = documentos.emisor_id
                                documento_dict['receptor_origen'] = documentos.receptor_origen
                                documento_dict['tipoModelo'] = documentos.tipoModelo
                                documento_dict['tipoOperacion'] = documentos.tipoOperacion
                                documento_dict['estado_anulado'] = None
                                documento_dict['fecha_anula_mh'] = None
                                documento_dict['codigoGenInvalida'] = None
                                documento_dict['anuladoErp'] = 0

                                nuevo_documento = Documentos(**documento_dict)
                                nuevo_documento.save()
                                logger.info(f"Documento creado: {nuevo_documento}")

                                for detalle_dict in detalles_lista:
                                    detalle_dict['codigoGeneracion_id'] = nuevo_documento
                                    detalle_dict['numeroDocumento'] = documentos.codigoGeneracion
                                    detalle_dict['codTributo'] = C015Tributos.objects.get(codigo='20')
                                    nuevo_detalle = DocumentosDetalle(**detalle_dict)
                                    nuevo_detalle.save()
                                    logger.info(f"Detalle del documento creado: {nuevo_detalle}")

                                documentos.estado = 'ANULADONC'
                                documentos.anuladoErp = False
                                documentos.observacion_proceso = f'Anulado con NC Local No.: {nuevo_documento.codigoGeneracion}, Nota: Este Documento No Existira en Softland, Create: {request.user}'
                                documentos.save()
                                logger.info(f"Documento original actualizado: {documentos}")

                                actualizado = consecutivo_sf.set(nuevo_consecutivo)
                                logger.info(f"Resultado de la actualización del consecutivo: {actualizado}")

                                if actualizado.get('status') != 'OK':
                                    raise Exception(actualizado.get('error', 'Error al actualizar el consecutivo'))
                                
                                result = 'OK'
                            else:
                                result = Nconsecutivos.get('error')
                    except Exception as er:
                        result = str(er)
                        logger.error(f"Error al procesar la nota de crédito: {result}")
                else:
                    result = 'No se puede Realizar Nota de Crédito a Documento con mas de 90 Días de Generado'
                    logger.error(result)

                #lineas =  documentos.documento_detalle_codigoGeneracion_id.all()                    
            else:
                result = 'Documento ya cuenta con Nota de Crédito para Anulación'
                logger.error(result)


            #result = run_processor(codigoGeneracion)
            
            #result = MainProcessor( codigoGeneracion).run()
           # result = procesar_documentos.delay(codigoGeneracion)
           # if 'estado' in  result:
           #     if result['estado'] == 'PROCESADO':
           #         result_mail = send_emails_for_pending_documents.delay(codigoGeneracion)
                    
               
            #result = send_emails_for_pending_documents.delay('dos','trs','params')
            #result = sell_hellos.delay('hola hey!!')
            logger.info("Registro existoso de la NC")
            return JsonResponse({'success': True, 'message': str(result)})    
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})