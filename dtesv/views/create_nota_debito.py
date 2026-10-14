# En tu archivo create_nota_debito.py
from django.views import View
from django.http import JsonResponse
from dtesv.models import (
    Documentos,
    DocumentosDetalle,
    C002TipoDocumento,
    C015Tributos,
    Parametros,
    Company,
    C016CondicionOperacion,
    C025BienesRemitidosTitulos
)
from dtesv.tools.consecutivo_local import ConsecutivosSF
from django.forms.models import model_to_dict
from django.db import transaction
import uuid
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('celery')

class GenerateNotaDebito(View):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("Ingresando a la vista GenerateNotaDebito")

            # 1. Obtener la compañía y sus parámetros
            company = Company.objects.filter(users=request.user).first()
            if not company:
                logger.error("No se encontró la compañía para el usuario.")
                return JsonResponse({'success': False, 'message': 'No se encontró la compañía asociada al usuario.'})
            
            parametro = company.parametros_company_id.first()
            if not parametro:
                logger.error("No se encontraron parámetros para la compañía.")
                return JsonResponse({'success': False, 'message': 'No se encontraron parámetros de configuración.'})

            codigoGeneracion = kwargs.get('codigoGeneracion')
            if not codigoGeneracion:
                return JsonResponse({'success': False, 'message': 'Código de generación no proporcionado.'})

            logger.info(f"Evaluando codigo: {codigoGeneracion}")
            
            # 2. Identificar y validar el documento de origen
            documento_origen = Documentos.objects.filter(codigoGeneracion=codigoGeneracion).first()
            logger.info(f"Documento Origen: {documento_origen}")

            if not documento_origen:
                return JsonResponse({'success': False, 'message': 'Documento no encontrado.'})

            # 3. Determinar el documento padre (CCF) y los detalles a copiar
            if documento_origen.tipodocumento.codigo == '03':
                documento_padre = documento_origen
                detalles_a_copiar = documento_padre.documento_detalle_codigoGeneracion_id.all()
                logger.info("Documento de entrada es un CCF, se usará como documento padre.")
            elif documento_origen.tipodocumento.codigo == '05':
                documento_padre = Documentos.objects.filter(codigoGeneracion=documento_origen.numeroDocumento_rel_guid).first()
                if not documento_padre:
                    return JsonResponse({'success': False, 'message': 'CCF padre no encontrado para esta Nota de Crédito.'})
                detalles_a_copiar = documento_origen.documento_detalle_codigoGeneracion_id.all()
                logger.info(f"Documento de entrada es una NC. Se creará una ND para el CCF padre: {documento_padre.codigoGeneracion}")
            else:
                return JsonResponse({'success': False, 'message': 'El tipo de documento no es válido para crear una Nota de Débito.'})

            # 4. Validar que el documento padre no tenga más de 90 días
            fecha_actual_date = datetime.now().date()
            diferencia = fecha_actual_date - documento_padre.fecEmi
            logger.info(f"Diferencia detectada: {diferencia.days} días. Valor máximo: 90 días.")
            if diferencia.days > 90:
                return JsonResponse({'success': False, 'message': 'No se puede realizar Nota de Débito a un documento con más de 90 días de generado.'})

            # 5. Verificar si ya existe una Nota de Débito para este CCF
            nota_debito_existente = Documentos.objects.filter(numeroDocumento_rel_guid=documento_padre.codigoGeneracion, tipodocumento__codigo='06').first()
            logger.info(f"Nota de Débito existente: {nota_debito_existente}")
            if nota_debito_existente:
                return JsonResponse({'success': False, 'message': 'Documento ya cuenta con una Nota de Débito.'})

            ## Obtener el consecutivo
            cod_sucursal = documento_origen.cod_sucursal
            logger.info(f"Valor de Sucursal obtenido: {cod_sucursal}, codigoGeneracion = {codigoGeneracion}")
            guid = str(uuid.uuid4()).upper()
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            hora_actual = datetime.now().time()

            ESTABLECIMIENTO_POR_SUCURSAL = {
                '0': 'M001',
                '1': 'S001',
                '2': 'S002',
            }            
            establecimiento = ESTABLECIMIENTO_POR_SUCURSAL.get(cod_sucursal, 'M001')

            tipo_doc = '06'
            consecutivo_sf = ConsecutivosSF(tipo_doc, parametro, sucursal = cod_sucursal)
            Nconsecutivos = consecutivo_sf.get()
            logger.info(f"Valor de Nconsecutivos obtenido: {Nconsecutivos}")

            if 'datos' not in Nconsecutivos:
                raise Exception(Nconsecutivos.get('error', 'Error al obtener consecutivo revisar StoreProcedure SQL'))

            nuevo_consecutivo = '{:015}'.format(int(Nconsecutivos['datos']))
            dte_consecutivo = f'DTE-06-{establecimiento}P001-' + Nconsecutivos['datos']

            # 6. Usar una transacción atómica para garantizar la consistencia de los datos
            with transaction.atomic():
               
                # Crear un diccionario para el nuevo documento con los campos correctos
                documento_dict = {}
                documento_dict['numeroDocumento_rel_guid'] = documento_padre.codigoGeneracion
                documento_dict['numeroDocumento_rel_corr'] = guid
                documento_dict['selloRecibido'] = None
                documento_dict['tipodocumento'] = C002TipoDocumento.objects.get(codigo='06')
                documento_dict['clase_documento'] = 'ND'
                documento_dict['fecEmi'] = fecha_actual
                documento_dict['num_documento'] = nuevo_consecutivo                
                documento_dict['totalNoSuj'] = documento_origen.totalNoSuj
                documento_dict['totalExenta'] = documento_origen.totalExenta
                documento_dict['totalNoGravado'] = documento_origen.totalNoGravado
                documento_dict['horEmi'] = hora_actual
                documento_dict['descuGravada'] = documento_origen.descuGravada
                documento_dict['descuExenta'] = documento_origen.descuExenta
                documento_dict['descuNoSuj'] = documento_origen.descuNoSuj
                documento_dict['porcentajeDescuento'] = documento_origen.porcentajeDescuento
                documento_dict['totalDescu'] = documento_origen.totalDescu
                documento_dict['iva'] = documento_origen.iva
                documento_dict['ivaRete1'] = documento_origen.ivaRete1
                documento_dict['ivaPerci1'] = documento_origen.ivaPerci1
                documento_dict['reteRenta'] = documento_origen.reteRenta
                documento_dict['numPagoElectronico'] = documento_origen.numPagoElectronico
                documento_dict['vendedor_id'] = documento_origen.vendedor_id
                documento_dict['estado'] = 'Nuevo'
                documento_dict['numeroControl'] = dte_consecutivo
                documento_dict['codigoGeneracion'] = guid
                documento_dict['tipoMoneda'] = documento_origen.tipoMoneda
                documento_dict['rutaEntrega'] = documento_origen.rutaEntrega
                documento_dict['observaciones_mh'] = None
                documento_dict['saldoFavor'] = documento_origen.saldoFavor
                documento_dict['totalGravada'] = documento_origen.totalGravada
                documento_dict['subTotalVentas'] = documento_origen.subTotalVentas
                documento_dict['montoTotalOperacion'] = documento_origen.montoTotalOperacion
                documento_dict['totalPagar'] = documento_origen.totalPagar
                documento_dict['totalLetras'] = documento_origen.totalLetras
                documento_dict['observacion_proceso'] = f'Nota de Débito que Anula al Documento: {documento_origen.codigoGeneracion}, Con numero ERP: {documento_origen.num_documento}, Esta ND no existe en Softland, Create: {request.user}; ' + documento_origen.observacion_proceso
                documento_dict['condicionOperacion'] = documento_origen.condicionOperacion
                documento_dict['codigo_iva'] = documento_origen.codigo_iva
                documento_dict['seguro'] = documento_origen.seguro
                documento_dict['flete'] = documento_origen.flete
                documento_dict['bienTitulo'] = C025BienesRemitidosTitulos.objects.get(codigo='01')
                documento_dict['receptor_id'] = documento_origen.receptor_id
                documento_dict['emisor_id'] = documento_origen.emisor_id
                documento_dict['receptor_origen'] = documento_origen.receptor_origen
                documento_dict['tipoModelo'] = documento_origen.tipoModelo
                documento_dict['tipoOperacion'] = documento_origen.tipoOperacion
                documento_dict['estado_anulado'] = None
                documento_dict['fecha_anula_mh'] = None
                documento_dict['codigoGenInvalida'] = None
                documento_dict['anuladoErp'] = 0

                nuevo_documento = Documentos(**documento_dict)
                nuevo_documento.save()
                logger.info(f"Documento creado: {nuevo_documento}")

                for detalle_origen in detalles_a_copiar:
                    detalle_dict = model_to_dict(detalle_origen)
                    detalle_dict.pop('id', None)
                    detalle_dict['codigoGeneracion_id'] = nuevo_documento
                    detalle_dict['numeroDocumento'] = documento_padre.codigoGeneracion
                    detalle_dict['codTributo'] = C015Tributos.objects.get(codigo='20')
                    
                    nuevo_detalle = DocumentosDetalle(**detalle_dict)
                    nuevo_detalle.save()
                    logger.info(f"Detalle del documento creado: {nuevo_detalle.id}")

                documento_origen.estado = 'ANULADOND'
                documento_origen.anuladoErp = False
                documento_origen.observacion_proceso = f'Anulado con ND Local No.: {nuevo_documento.codigoGeneracion}, Nota: Este Documento No Existira en Softland, Create: {request.user}'
                documento_origen.save()
                logger.info(f"Documento original actualizado: {documento_origen}")

                actualizado = consecutivo_sf.set(nuevo_consecutivo)
                logger.info(f"Resultado de la actualización del consecutivo: {actualizado}")

                if actualizado.get('status') != 'OK':
                    raise Exception(actualizado.get('error', 'Error al actualizar el consecutivo'))
                
                result = 'OK'
                logger.info(f"Nota de Débito y detalles creados con éxito.")
                return JsonResponse({'success': True, 'message': str(result)})
        
        except Exception as e:
            logger.error(f"Error inesperado en la vista: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'message': str(e)})