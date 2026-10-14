
from dtesv.models import Documentos,  DocumentosDetalle, ExtencionEntrega,  Pagos, Parametros, C015Tributos,C002TipoDocumento
import dtesv.processes.validate_schema as validateSchema 
import dtesv.Apis.autentificador as autenticador
import dtesv.processes.create_json as gen_json
import dtesv.Apis.recepcion_dte as mh_recepciondte
import dtesv.Apis.firmador as firmador
import base64
import uuid
import traceback
import logging
import json


logger = logging.getLogger(__name__)

def clean_text(value):
    return value.strip() if isinstance(value, str) else value   

class DocumentoDiccionarioStruc:
    def get_diccionario(Documentos_obj):
        logger.info("Ingresando a la creacion del diccionario")
        try:
            document_list=[]
            for documentos in Documentos_obj:
                
                logger.info(f"Datos obtenidos de ciclo FOR: {documentos}, {Documentos_obj}", exc_info=True)
               # traceback.print_exc() 
                codigoGen = documentos.codigoGeneracion
                identificacion_dic = {
                    "version": int(documentos.tipodocumento.version_work),
                    "ambiente": documentos.emisor_id.ambiente_trabajo.codigo,
                    "tipoDte": documentos.tipodocumento.codigo,
                    "numeroControl": documentos.numeroControl,
                    "codigoGeneracion": documentos.codigoGeneracion,
                    "tipoModelo": int(documentos.tipoModelo.codigo)
                    if documentos.tipoModelo
                    else None,
                    "tipoOperacion": int(documentos.tipoOperacion.codigo),
                    "tipoContingencia": None
                    if documentos.tipoContingencia
                    else None,
                    "motivoContin": documentos.motivoContin
                    if documentos.motivoContin
                    else None,
                    "fecEmi": documentos.fecEmi.strftime("%Y-%m-%d"),
                    "horEmi": documentos.horEmi.strftime("%H:%M:%S"),
                    "tipoMoneda": documentos.tipoMoneda,
                }
                emisor_data = {
                    "nit": documentos.emisor_id.nit,
                    "nrc": documentos.emisor_id.nrc,
                    "nombre": documentos.emisor_id.nombre,
                    "codActividad": documentos.emisor_id.codactividad.codigo,
                    "descActividad": documentos.emisor_id.codactividad.nombre,
                    "nombreComercial": documentos.emisor_id.nombrecomercial,
                    "tipoEstablecimiento": documentos.emisor_id.tipoestablecimiento.codigo,
                    "direccion": {
                        "departamento": documentos.emisor_id.departamento.codigo,
                        "municipio": documentos.emisor_id.municipio.codigo,
                    ### 2024-09-12: Se hace cambio a la variable para que se puedan mostrar los nuevos municipio
                        #"municipio": documentos.emisor_id.munidistrito.codigo, 
                        "complemento": documentos.emisor_id.direccion_complemento,
                    },
                    "telefono": documentos.emisor_id.telefono,
                    "correo": documentos.emisor_id.correo,
                    "codEstableMH": documentos.emisor_id.codestablemh,
                    "codEstable": documentos.emisor_id.codestable,
                    "codPuntoVentaMH": documentos.emisor_id.codpuntoventamh,
                    "codPuntoVenta": documentos.emisor_id.codpuntoventa,
                }
                if documentos.receptor_id and documentos.tipodocumento.codigo not in  ["14","07"]:
                    receptor_data = {
                        "tipoDocumento": documentos.receptor_id.tipodocumento.codigo,
                        "numDocumento": documentos.receptor_id.numdocumento.replace("-", "")
                        if "-" in documentos.receptor_id.numdocumento
                               and (documentos.tipodocumento.codigo == "03" or
                                    documentos.tipodocumento.codigo == "14" or 
                                    documentos.tipodocumento.codigo == "05" or 
                                    documentos.tipodocumento.codigo == "06" or 
                                    documentos.tipodocumento.codigo == "07")
                        
                        else documentos.receptor_id.numdocumento,
                        "nrc": documentos.receptor_id.nrc
                        if documentos.receptor_id.nrc and (documentos.tipodocumento.codigo == "03" or 
                                                           documentos.tipodocumento.codigo == "05" or 
                                                           documentos.tipodocumento.codigo == "06" or 
                                                           documentos.tipodocumento.codigo == "07")
                        else None,
                        "nombre": clean_text(documentos.receptor_id.nombre),
                        "codActividad": documentos.receptor_id.codactividad.codigo,
                        "descActividad": documentos.receptor_id.codactividad.nombre,
                        "direccion": {
                            "departamento": documentos.receptor_id.departamento.codigo,
                            "municipio": documentos.receptor_id.municipio.codigo,
                        ### 2024-09-12: Se hace cambio a la variable para que se puedan mostrar los nuevos municipio
                            #"municipio": documentos.receptor_id.munidistrito.codigo,                             
                            "complemento": clean_text(documentos.receptor_id.complemento),
                        },
                        "telefono": clean_text(documentos.receptor_id.telefono),
                        "correo": clean_text(documentos.receptor_id.correo),
                    }
                else:
                    receptor_data = {}
                data_extra = ExtencionEntrega.objects.filter(
                    id_emisor=documentos.emisor_id.id
                ).first()

                if data_extra:
                    extension_data = {
                        "nombEntrega": data_extra.nombre if data_extra.nombre else None,
                        "docuEntrega": data_extra.docuentrega
                        if data_extra.docuentrega
                        else None,
                        "nombRecibe": None,
                        "docuRecibe": None,
                        "observaciones": None,
                        "placaVehiculo": data_extra.placa_vehiculo
                        if data_extra.placa_vehiculo
                        else None,
                    }
                else:
                    extension_data = None

                documento_asoc = Documentos.objects.filter(
                    codigoGeneracion=documentos.numeroDocumento_rel_guid
                ).first()
                documento_asociado = []
                if documento_asoc:
                    documento_asociado.append(
                        {
                            "tipoGeneracion": 2,
                            "numeroDocumento": documento_asoc.codigoGeneracion,
                            "tipoDocumento": documento_asoc.tipodocumento_id,
                            "fechaEmision": documento_asoc.fecEmi.strftime("%Y-%m-%d"),
                        }
                    )
                else:
                    documento_asociado = None

                cuerpoDocumento = []
                DocumentosDetalle_new = list(
                    DocumentosDetalle.objects.filter(codigoGeneracion_id=codigoGen)
                )
                for doc in DocumentosDetalle_new:

                    cuerpoDocumento.append(
                        {
                            "numItem": doc.numItem,
                            "tipoItem": int(doc.tipoItem),
                            "numeroDocumento": doc.numeroDocumento
                            if documentos.tipodocumento.codigo in ("05", "06", "07")
                            else None,
                            "cantidad": doc.cantidad,
                            "codigo": doc.codigo,
                            "codTributo": None,
                            "uniMedida": doc.uniMedida,
                            "descripcion": doc.descripcion,
                            "precioUni": doc.precioUni,
                            "montoDescu": doc.montoDescu,
                            "ventaNoSuj": doc.ventaNoSuj,
                            "ventaExenta": doc.ventaExenta,
                            "ventaGravada": doc.ventaGravada,
                            "tributos": None,
                            "psv": doc.psv,
                            "noGravado": doc.noGravado,
                            "ivaItem": doc.ivaItem,
                            #Estos campos son usados para Comprobante de retencion se deben quitar en los otros tipos de documentos
                            "codigoRetencionMH":doc.codigoRetencionMH.codigo if doc.codigoRetencionMH else None,
                            "tipoDte":doc.tipoDte.codigo if doc.tipoDte else None,
                            #"tipoDoc":int(doc.tipoDoc.codigo) if  doc.tipoDoc else None ,
                            "tipoGeneracion":int(doc.tipoDoc.codigo) if  doc.tipoDoc else None ,
                            "fechaEmision":doc.fechaEmision.strftime("%Y-%m-%d") if doc.fechaEmision else None,
                            "numDocumento":doc.numeroDocumento, # Este campo se deja de usar a partir del 25-08-2026 de acuerdo a requerimiento de MH
                            "montoSujetoGrav":doc.ventaGravada,
                            'ivaRetenido':doc.ivaItem

                        }
                    )

                pagos = Pagos.objects.filter(codigogeneracion_doc=codigoGen).first()

                resumen = {
                    "totalNoSuj": documentos.totalNoSuj,
                    "totalExenta": documentos.totalExenta,
                    "totalGravada": documentos.totalGravada,
                    "subTotalVentas": documentos.subTotalVentas,
                    "descuNoSuj": documentos.descuNoSuj,
                    "descuExenta": documentos.descuExenta,
                    "descuGravada": documentos.descuGravada,
                    "porcentajeDescuento": documentos.porcentajeDescuento,
                    "totalDescu": documentos.totalDescu,
                    "tributos": None,
                    "subTotal": documentos.subTotalVentas - (documentos.descuGravada + documentos.descuExenta + documentos.descuNoSuj),
                    "ivaRete1": documentos.ivaRete1,
                    "reteRenta": documentos.reteRenta,
                    "montoTotalOperacion": documentos.montoTotalOperacion,
                    "totalNoGravado": documentos.totalNoGravado,
                    "totalPagar": documentos.totalPagar,
                    "totalLetras": documentos.totalLetras,
                    "totalIva": documentos.iva,
                    "saldoFavor": documentos.saldoFavor,
                    "condicionOperacion": documentos.condicionOperacion.codigo,
                    "pagos": [
                        {
                            "codigo": pagos.codigo_forma_pago,
                            "montoPago": pagos.monto,
                            "referencia": None,
                            "plazo": pagos.plazo,
                            "periodo": int(pagos.periodo),
                        }
                    ]
                    if pagos
                    else None,
                    "numPagoElectronico": None,
                }
                apendice = [{'campo':'OrdenCompra','etiqueta':'Número de Orden de Compra','valor': documentos.orden_compra}] if documentos.orden_compra else None

        #.#.# SOLO PARA EL CASO DE NOTAS DE CREDITO DEBO HACER ESTOS CAMBIOS PARA SUPERAR LA VALIDACION DEL SCHEMA
                if documentos.tipodocumento.codigo == "05" or documentos.tipodocumento.codigo == "06" :
                    claves_a_eliminar_emisor = [
                        "codEstable",
                        "codEstableMH",
                        "codPuntoVenta",
                        "codPuntoVentaMH",
                    ]
                    claves_a_eliminar_receptor = ["numDocumento", "tipoDocumento"]
                    # Solo eliminar 'numPagoElectronico' si el documento no es del tipo 06 (Nota de Crédito)
                    if documentos.tipodocumento.codigo != "06":
                        claves_a_eliminar_resumen = [
                            "numPagoElectronico",
                            "pagos",
                            "porcentajeDescuento",
                            "saldoFavor",
                            "totalIva",
                            "totalNoGravado",
                            "totalPagar",
                        ]
                    else:
                        claves_a_eliminar_resumen = [
                            "pagos",
                            "porcentajeDescuento",
                            "saldoFavor",
                            "totalIva",
                            "totalNoGravado",
                            "totalPagar",
                        ]
                    claves_a_eliminar_cuerpo = ["ivaItem", "noGravado", "psv","codigoRetencionMH","tipoDte","tipoDoc", "tipoGeneracion", "fechaEmision","numDocumento"
                                                ,"montoSujetoGrav",'ivaRetenido']

                    emisor_data = {
                        clave: valor
                        for clave, valor in emisor_data.items()
                        if clave not in claves_a_eliminar_emisor
                    }
                    receptor_data = {
                        clave: valor
                        for clave, valor in receptor_data.items()
                        if clave not in claves_a_eliminar_receptor
                    }

                    for id, cuerpo in enumerate(cuerpoDocumento):
                        cuerpoDocumento[id] = {
                            clave: valor
                            for clave, valor in cuerpo.items()
                            if clave not in claves_a_eliminar_cuerpo
                        }
                        # cuerpoDocumento[id]['numeroDocumento']= documentos.num_documento
                        if cuerpoDocumento[id]["ventaGravada"] > 0.0:
                            cuerpoDocumento[id]["tributos"] = ["20"]

                    tributo_db = C015Tributos.objects.filter(codigo="20").first()
                    tributos = {
                        "codigo": tributo_db.codigo,
                        "descripcion": tributo_db.descripcion,
                        "valor": documentos.iva,
                    }

                    resumen = {
                        clave: valor
                        for clave, valor in resumen.items()
                        if clave not in claves_a_eliminar_resumen
                    }
                    receptor_data["nit"] = str(documentos.receptor_id.numdocumento.replace("-", ""))
                    receptor_data[
                        "nombreComercial"
                    ] = clean_text(documentos.receptor_id.nombrecomercial)
                    resumen["ivaPerci1"] = documentos.ivaPerci1
                    resumen["ivaRete1"] = documentos.ivaRete1
                    resumen["tributos"] = [tributos]

                    identificacion_dic["version"] = 3

                    dic_result = {
                        "identificacion": identificacion_dic,
                        "documentoRelacionado": documento_asociado,
                        "emisor": emisor_data,
                        "receptor": receptor_data,
                        "ventaTercero": None,
                        "cuerpoDocumento": cuerpoDocumento,
                        "resumen": resumen,
                        "extension": extension_data,
                        "apendice": apendice,
                    }

                # PARA EL CASO DE CREDITO FISCAL SE HARAN ESTOS CAMBIOS
                elif documentos.tipodocumento.codigo == "03":
                    
                    claves_a_eliminar_receptor = ["numDocumento", "tipoDocumento"]
                    claves_a_eliminar_resumen = ["totalIva"]
                    claves_a_eliminar_cuerpo = ["ivaItem","codigoRetencionMH","tipoDte","tipoDoc", "tipoGeneracion", "fechaEmision","numDocumento","montoSujetoGrav",'ivaRetenido']
                    for id, cuerpo in enumerate(cuerpoDocumento):
                        cuerpoDocumento[id] = {
                            clave: valor
                            for clave, valor in cuerpo.items()
                            if clave not in claves_a_eliminar_cuerpo
                        }
                        if cuerpoDocumento[id]["ventaGravada"] > 0.0:
                            cuerpoDocumento[id]["tributos"] = ["20"]

                    receptor_data = {
                        clave: valor
                        for clave, valor in receptor_data.items()
                        if clave not in claves_a_eliminar_receptor
                    }
                    resumen = {
                        clave: valor
                        for clave, valor in resumen.items()
                        if clave not in claves_a_eliminar_resumen
                    }
                    receptor_data["nit"] = str(documentos.receptor_id.numdocumento.replace("-", ""))
                    receptor_data[
                        "nombreComercial"
                    ] = clean_text(documentos.receptor_id.nombrecomercial)

                    resumen["ivaPerci1"] = documentos.ivaPerci1
                    resumen["ivaRete1"] = documentos.ivaRete1
                    # resumen['totalIva'] = documentos.iva
                    identificacion_dic["version"] = 3
                    tributos = []
                    if documentos.codigo_iva:
                        tributos.append(
                            {
                                "codigo": documentos.codigo_iva.codigo,
                                "descripcion": documentos.codigo_iva.descripcion,
                                "valor": documentos.iva,
                            }
                        )
                    resumen["tributos"] = tributos

                    dic_result = {
                        "identificacion": identificacion_dic,
                        "documentoRelacionado": documento_asociado,
                        "emisor": emisor_data,
                        "receptor": receptor_data,
                        "otrosDocumentos": None,
                        "ventaTercero": None,
                        "cuerpoDocumento": cuerpoDocumento,
                        "resumen": resumen,
                        "extension": extension_data,
                        "apendice": apendice,
                    }
                    

                # PARA FACTURAS DE EXPORTACION SE HARAN LOS SIGUENTES CAMBIOS
                elif documentos.tipodocumento.codigo == "11":
                    claves_a_eliminar_identificacion = ["motivoContin"]
                    claves_a_eliminar_receptor_ex = ["codActividad", "direccion", "nrc"]
                    claves_a_eliminar_resumen_ex = [
                        "descuExenta",
                        "descuGravada",
                        "descuNoSuj",
                        "ivaRete1",
                        "reteRenta",
                        "saldoFavor",
                        "subTotal",
                        "subTotalVentas",
                        "totalExenta",
                        "totalIva",
                        "totalNoSuj",
                        "tributos",
                    ]
                    claves_a_eliminar_cuerpo_ex = [
                        "codTributo",
                        "ivaItem",
                        "numeroDocumento",
                        "psv",
                        "tipoItem",
                        "ventaExenta",
                        "ventaNoSuj",
                        "numeroDocumento","codigoRetencionMH","tipoDte","tipoDoc", "tipoGeneracion", "fechaEmision","numDocumento","montoSujetoGrav",'ivaRetenido'
                    ]

                    identificacion_dic = {
                        clave: valor
                        for clave, valor in identificacion_dic.items()
                        if clave not in claves_a_eliminar_identificacion
                    }
                    receptor_data = {
                        clave: valor
                        for clave, valor in receptor_data.items()
                        if clave not in claves_a_eliminar_receptor_ex
                    }
                    resumen = {
                        clave: valor
                        for clave, valor in resumen.items()
                        if clave not in claves_a_eliminar_resumen_ex
                    }
                    for id, cuerpo in enumerate(cuerpoDocumento):
                        cuerpoDocumento[id] = {
                            clave: valor
                            for clave, valor in cuerpo.items()
                            if clave not in claves_a_eliminar_cuerpo_ex
                        }

                    identificacion_dic["motivoContigencia"] = (
                        documentos.motivoContin if documentos.motivoContin else None
                    )
                    emisor_data["tipoItemExpor"] = documentos.tipoItemExpor
                    emisor_data["recintoFiscal"] = str(documentos.recintoFiscal.codigo)
                    emisor_data["regimen"] = documentos.regimen.codigo
                    receptor_data["codPais"] = str(documentos.receptor_id.codpais.codigo)
                    receptor_data["nombrePais"] = documentos.receptor_id.codpais.descripcion
                    receptor_data["complemento"] = clean_text(documentos.receptor_id.complemento)
                    receptor_data[
                        "nombreComercial"
                    ] = clean_text(documentos.receptor_id.nombrecomercial)
                    receptor_data["tipoPersona"] = int(
                        documentos.receptor_id.tipopersona.codigo
                    )
                    receptor_data["numDocumento"] = documentos.receptor_id.numdocumento
                    resumen["descuento"] = documentos.totalDescu
                    resumen["codIncoterms"] = documentos.codIncoterms.codigo if documentos.codIncoterms else None
                    resumen["descIncoterms"] = documentos.codIncoterms.descripcion if documentos.codIncoterms else None
                    resumen["observaciones"] = None
                    resumen["flete"] = documentos.flete
                    resumen["seguro"] = documentos.seguro

                    dic_result = {
                        "identificacion": identificacion_dic,
                        "emisor": emisor_data,
                        "receptor": receptor_data,
                        "otrosDocumentos": None,
                        "ventaTercero": None,
                        "cuerpoDocumento": cuerpoDocumento,
                        "resumen": resumen,
                        "apendice": apendice,
                    }
            

                # PARA FACTURAS SE HARAN LOS SIGUENTES CAMBIOS
                elif  documentos.tipodocumento.codigo == '01':
                    claves_a_eliminar_cuerpo =["codigoRetencionMH","tipoDte","tipoDoc", "tipoGeneracion", "fechaEmision","numDocumento","montoSujetoGrav","ivaRetenido"]
                    #claves_a_eliminar_cuerpo = ['numeroDocumento']
                    for id, cuerpo in enumerate(cuerpoDocumento):
                            cuerpoDocumento[id] = {clave: valor for clave, valor in cuerpo.items() if clave not in claves_a_eliminar_cuerpo}

                    receptor_data["numDocumento"] = str(documentos.receptor_id.numdocumento.replace("-", "")) if documentos.receptor_id.tipodocumento.codigo=='36' else documentos.receptor_id.numdocumento
                    resumen["ivaRete1"] = documentos.ivaRete1
                    dic_result = {
                        "identificacion": identificacion_dic,
                        "documentoRelacionado": documento_asociado,
                        "emisor": emisor_data,
                        "receptor": receptor_data,
                        "otrosDocumentos": None,
                        "ventaTercero": None,
                        "cuerpoDocumento": cuerpoDocumento,
                        "resumen": resumen,
                        "extension": extension_data,
                        "apendice": apendice,
                    }

                elif  documentos.tipodocumento.codigo == '14':
                     #dic_result.pop('receptor',None)
                     proveedor_data = {
                        "tipoDocumento": documentos.proveedor_id.tipodocumento.codigo,
                        "numDocumento": documentos.proveedor_id.numdocumento.replace("-", ""),
                       # if "-" in documentos.proveedor_id.numdocumento and documentos.proveedor_id.tipodocumento.codigo != "13"                        
                       # else documentos.proveedor_id.numdocumento,                      
                        
                        "nombre": clean_text(documentos.proveedor_id.nombre),
                        #"nombreComercial":documentos.proveedor_id.nombrecomercial,
                        "codActividad": documentos.proveedor_id.codactividad.codigo,
                        "descActividad": documentos.proveedor_id.codactividad.nombre,
                        "direccion": {
                            "departamento": documentos.proveedor_id.departamento.codigo,
                            "municipio": documentos.proveedor_id.municipio.codigo,
                        ### 2024-09-12: Se hace cambio a la variable para que se puedan mostrar los nuevos municipio
                            #"municipio": documentos.proveedor_id.munidistrito.nombre,                            
                            "complemento": clean_text(documentos.proveedor_id.complemento),
                        },
                        "telefono": clean_text(documentos.proveedor_id.telefono),
                        "correo": clean_text(documentos.proveedor_id.correo),
                        }
                    
                     #dic_result['receptor'] = proveedor_data


                     claves_a_eliminar_cuerpo =["codTributo","codigoRetencionMH","fechaEmision", "ivaItem","ivaRetenido","montoSujetoGrav","noGravado",
                                                'numDocumento', 'numeroDocumento', 'psv', 'tipoDoc', 'tipoGeneracion', 'tipoDte', 'tributos', 'ventaExenta', 'ventaGravada',
                                                  'ventaNoSuj' ]
                     #claves_a_eliminar_cuerpo = ['numeroDocumento']
                     for id, cuerpo in enumerate(cuerpoDocumento):
                            cuerpoDocumento[id] = {clave: valor for clave, valor in cuerpo.items() if clave not in claves_a_eliminar_cuerpo}
                            cuerpoDocumento[id]['compra'] = (cuerpoDocumento[id]['precioUni'] * cuerpoDocumento[id]['cantidad'])

                            
                     resumen['totalCompra'] = documentos.totalSujetoRetenido
                     resumen['descu'] =  resumen['totalDescu']
                     resumen['observaciones'] = None
                     resumen['subTotal'] = documentos.totalSujetoRetenido
                     
                     emisor_data.pop('tipoEstablecimiento',None)
                     emisor_data.pop('nombreComercial',None)
                     #receptor_data.pop('nrc',None)                     
                     resumen.pop('descuExenta',None)
                     resumen.pop('descuGravada',None)
                     resumen.pop('descuNoSuj',None)
                     resumen.pop('montoTotalOperacion',None)
                     resumen.pop('numPagoElectronico',None)
                     resumen.pop('porcentajeDescuento',None)
                     resumen.pop('saldoFavor',None)
                     resumen.pop('subTotalVentas',None)
                     resumen.pop('totalGravada',None)
                     resumen.pop('totalIva',None)
                     resumen.pop('totalNoGravado',None)
                     resumen.pop('totalNoSuj',None)
                     resumen.pop('tributos',None)
                     resumen.pop('totalExenta',None)

                     dic_result = {
                        "identificacion": identificacion_dic,                         
                        "emisor": emisor_data,
                        "sujetoExcluido": proveedor_data,
                        "cuerpoDocumento": cuerpoDocumento,
                        "resumen": resumen,                        
                        "apendice": apendice,
                    }

                # SI NO APLICA NINGUNA DE LAS ANTERIORES ENTONCES UTILIZARA EL STANDARD QUE ES FACTURA CONSUMIDOR FINAL  01
                else:
                    dic_result = {
                        "identificacion": identificacion_dic,
                        "documentoRelacionado": documento_asociado,
                        "emisor": emisor_data,
                        "receptor": receptor_data,
                        "otrosDocumentos": None,
                        "ventaTercero": None,
                        "cuerpoDocumento": cuerpoDocumento,
                        "resumen": resumen,
                        #"extension": extension_data,
                        "apendice": apendice,
                    }
                if  documentos.tipodocumento.codigo == "07":    
                    dic_result.pop('documentoRelacionado',None)
                    dic_result.pop('otrosDocumentos',None)
                    dic_result.pop('ventaTercero',None)
                    dic_result.pop('receptor',None)

                    proveedor_data = {
                    "tipoDocumento": documentos.proveedor_id.tipodocumento.codigo,
                    "numDocumento": documentos.proveedor_id.numdocumento.replace("-", "") if "-" in documentos.proveedor_id.numdocumento and documentos.proveedor_id.tipodocumento.codigo != "13"
                    #and (documentos.tipodocumento.codigo == "03" or documentos.tipodocumento.codigo == "14" or documentos.tipodocumento.codigo == "05" or documentos.tipodocumento.codigo == "07")
                    
                    else documentos.proveedor_id.numdocumento,
                    "nrc": documentos.proveedor_id.nrc
                    if documentos.proveedor_id.nrc
                    else None,
                    "nombre": clean_text(documentos.proveedor_id.nombre),
                    "nombreComercial": clean_text(documentos.proveedor_id.nombrecomercial),
                    "codActividad": documentos.proveedor_id.codactividad.codigo,
                    "descActividad": documentos.proveedor_id.codactividad.nombre,
                    "direccion": {
                        "departamento": documentos.proveedor_id.departamento.codigo,
                        "distrito": documentos.proveedor_id.municipio.codigo,
                        ### 2024-09-12: Se hace cambio a la variable para que se puedan mostrar los nuevos municipio
                        "municipio": documentos.proveedor_id.munidistrito.codigo,                            

                        "complemento": clean_text(documentos.proveedor_id.complemento),
                    },
                    "telefono": clean_text(documentos.proveedor_id.telefono),
                    "correo": clean_text(documentos.proveedor_id.correo),
                     }
                    
                    dic_result['receptor'] = proveedor_data

                    dic_result['emisor']['codigoMH'] = dic_result['emisor']['codEstableMH']
                    dic_result['emisor']['codigo'] = dic_result['emisor']['codEstable']
                    dic_result['emisor']['puntoVentaMH'] = dic_result['emisor']['codPuntoVentaMH']
                    dic_result['emisor']['puntoVenta'] = dic_result['emisor']['codPuntoVenta']
                    dic_result['emisor']['direccion']['distrito'] = documentos.emisor_id.municipio.codigo
                    dic_result['emisor']['direccion']['municipio'] = documentos.emisor_id.munidistrito.codigo

                    claves_a_eliminar_emisor_se = ["codigo", "codEstableMH","codPuntoVentaMH","numDocumento","tipoDocumento", #"codEstable","codPuntoVenta", 
                                                    "codigoMH", "puntoVentaMH", "puntoVenta", "tipoEstablecimiento"]
                    claves_elimiar_resumen_se =['condicionOperacion', 'descuExenta', 'descuGravada', 'descuNoSuj', 'ivaRete1', 'montoTotalOperacion', 
                                                'numPagoElectronico', 'pagos', 'porcentajeDescuento', 'reteRenta', 'saldoFavor', 'subTotal', 
                                                'subTotalVentas', 'totalDescu', 'totalExenta', 'totalGravada', 'totalIva', 'totalLetras', 
                                                'totalNoGravado', 'totalNoSuj', 'totalPagar', 'tributos']
                    claves_elimiar_cuerpo_se = [
                        'cantidad', 'codTributo', 'codigo', 'ivaItem', 'montoDescu', 'noGravado', 'numDocumento',
                        #'numeroDocumento', # Este campo se usara a partir del 25-08-2026 de acuerdo a requerimiento de MH
                        'precioUni', 'psv', 'tipoItem', 
                        'tributos', 'uniMedida', 'ventaExenta', 'ventaGravada', 'ventaNoSuj'
                    ]
                    dic_result['emisor'] = {
                        clave: valor
                        for clave, valor in  dic_result['emisor'].items()
                        if clave not in claves_a_eliminar_emisor_se
                    }
                    dic_result['resumen'] = {
                        clave: valor
                        for clave, valor in  dic_result['resumen'].items()
                        if clave not in claves_elimiar_resumen_se
                    }
                    
                    #dic_result['receptor']['nombreComercial'] = documentos.receptor_id.nombrecomercial
                    dic_result['resumen']['totalIva'] = 0.000000 #documentos.totalIVAretenido
                    dic_result['resumen']['totalIvaRetenido'] = documentos.totalIVAretenido
                    dic_result['resumen']['totalSujetoRetencion'] = documentos.totalSujetoRetenido
                    dic_result['resumen']['totalLetras'] = documentos.totalLetras
                    dic_result['resumen']['observaciones'] = None

                    for id, cuerpo in enumerate(dic_result['cuerpoDocumento']):
                        dic_result['cuerpoDocumento'][id] = {
                            clave: valor
                            for clave, valor in cuerpo.items()
                            if clave not in claves_elimiar_cuerpo_se
                        }
 

                #LLENO MI LIST CON LOS DOCUMENTOS  
                document_list.append(dic_result)
                logger.error(f"mh_result: {document_list}", exc_info=True)
                #traceback.print_exc() 
                #logger.error(document_list, exc_info=True)
               # traceback.print_exc()
        # RETORNO EL LIST CON LOS DOCUMENTO
               
            return document_list
        except Exception as e:
            logger.error(f"Error Constructor Diccionario: {e}", exc_info=True)
            traceback.print_exc()

    def validar_schema(domument_list):
        try:
            list_validacion=[]
            for documento in domument_list:
                schema_name = ''
                if 'tipoDte' in  documento['identificacion']:
                    tipo_documento = C002TipoDocumento.objects.filter(codigo = documento['identificacion']['tipoDte']).first()    
                    schema_name  = tipo_documento.schema_name
                else:
                    schema_name = 'contingencia-schema-v3'

                
                #logger.info(f"Validacion del schema: documento['identificacion']['codigoGeneracion']: {documento['identificacion']['codigoGeneracion']}")
                #logger.info(f"Valores: schema_name: {schema_name}")
                validacion_schema =  validateSchema.schemaValidate({'tipo':schema_name,'json':documento}).validar_schema()
                list_validacion.append({'codigoGeneracion':documento['identificacion']['codigoGeneracion'],'result':validacion_schema})

            return list_validacion 
           
        except Exception as e:
            logger.error(f"Error Validar Schema: {e}", exc_info=True)
            traceback.print_exc()

    
    def get_documentos_firmados(dic_dtes,company_id):
        try:
            list_doc_firmados = []
            
            parametros = Parametros.objects.filter(company_id = company_id).first()
            for dic_dte in dic_dtes:
                
                dic_datos_dte = ({ 'nit':parametros.company_id.emisor.nit,'activo':parametros.company_id.emisor.activo,'passwordPri':base64.b64decode(parametros.company_id.emisor.passwordpri).decode("utf-16") , 'dteJson':dic_dte})         
                #logger.error(f"datos Firmador Documentos: {str(dic_datos_dte)}", exc_info=True)
                
               
                doc_firmado = firmador.get_dte_firma(dic_datos_dte,parametros).get_firma()
                 
                doc_firmado['ambiente'] = dic_dte['identificacion']['ambiente']
                doc_firmado['version'] = dic_dte['identificacion']['version']
                if 'tipoDte' in dic_dte['identificacion']:
                    doc_firmado['tipoDte'] = dic_dte['identificacion']['tipoDte']

                list_doc_firmados.append({'dic_dte':dic_dte,'doc_firmado':doc_firmado})
                
            
            return list_doc_firmados,parametros.company_id.emisor.nit,base64.b64decode(parametros.company_id.emisor.mh_auth).decode("utf-16"),parametros
        
        except Exception as e:
            logger.error(f"Error Firmador Documentos: {e}", exc_info=True)
            list_doc_firmados.append({'result':str(e)})
            #traceback.print_exc()
    

    def procesar_documento_mh(documentos,company_id,eslote,idlote = None):
        
        # CREO LOS DOCUMENTOS AGRUPADOS EN UN LIST DE DICCIOANARIO CON LA ESTRUCTURA SEGUN DOCUMENTO
        dic_dtes =DocumentoDiccionarioStruc.get_diccionario(documentos)
        #logger.error(f" procesar_documento_mh, toma el objeto a revision: {dic_dtes}",exc_info=True)
        # VALID EL SCHEMA
        validacion_schema = DocumentoDiccionarioStruc.validar_schema(dic_dtes)
        #logger.error(f" procesar_documento_mh, datos del schema: {validacion_schema}",exc_info=True)
        print(validacion_schema)
        items_con_result_falso = []
        items_con_status_firma_falso = []
        
        logger.error(f"Resultado de validar_schema: {validacion_schema}")
        for item in validacion_schema:
            if item['result'] != True:
                error = {'estado':'error','codigoGeneracion':item['codigoGeneracion'], 'tipo':'schema', 'cadena':item['result']}
                items_con_result_falso.append(error)

        #logger.error(f"Longitud del schema: {items_con_result_falso}", exc_info=True)
        if len(items_con_result_falso) == 0:
            documentos_firmados,nit,pwd,Parametros = DocumentoDiccionarioStruc.get_documentos_firmados(dic_dtes,company_id)
            #logger.error(f"Documentos firmados: {documentos_firmados}, nit: {nit}, pwd: {pwd}, Parametros: {Parametros}")

            for item in documentos_firmados:
                if item['doc_firmado']['status'] != 'OK':
                    error = {'estado':item['doc_firmado']['status'],'codigoGeneracion':item['dic_dte']['identificacion']['codigoGeneracion'],'tipo':'firmador', 'cadena':item['doc_firmado']}
                    items_con_status_firma_falso.append(error)

            if len(items_con_status_firma_falso) == 0:
               if eslote:
                    return DocumentoDiccionarioStruc.generacion_dic_lote(nit,pwd,Parametros,documentos_firmados,idlote)
               else:
                   #logger.error(f"Llamando a envio_mh con los siguientes datos: nit={nit}, pwd={pwd}, Parametros={Parametros}, documentos_firmados={documentos_firmados}", exc_info=True)
                   result = DocumentoDiccionarioStruc.envio_mh(nit,pwd,Parametros,documentos_firmados)
                   return result
            else:
               logger.error(f"Error en FirmaDocumentos: {items_con_status_firma_falso}", exc_info=True)
               return items_con_status_firma_falso
        else:
            logger.error(f"Error en Validar Schema: {items_con_result_falso}", exc_info=True)
            return items_con_result_falso


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
                                
                dic_to_repcion_mh = ({'ambiente':doc_fimado['doc_firmado']['ambiente'],'idEnvio': 1117,'version': int(doc_fimado['doc_firmado']['version']),'tipoDte': doc_fimado['doc_firmado']['tipoDte'],'documento':doc_fimado['doc_firmado']['body']})
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
                mh_result['tipo'] = 'mh_log'

                if 'observaciones' in mh_result and not mh_result['observaciones']:
                    mh_result['observaciones'] = ['.']

                estado = mh_result.get('estado')
                descripcion = mh_result.get('descripcionMsg', '')                    
                
                # evaluemos si el documento ya esta registrado en MH
                #if mh_result['estado'] =='RECHAZADO' and '[identificacion.codigoGeneracion] YA EXISTE UN REGISTRO CON ESE VALOR' in mh_result['descripcionMsg'] :
                if estado == 'RECHAZADO' and '[identificacion.codigoGeneracion] YA EXISTE UN REGISTRO CON ESE VALOR' in descripcion:
                     
                   dic_con={'nitEmisor':nit,'tdte':doc_fimado['doc_firmado']['tipoDte'],'codigoGeneracion':mh_result['codigoGeneracion']}
                   dic_consulta = ({'auth':token['body']['token'],'documento':dic_con})
                   #logger.error(f"Datos a enviar para consulta: {dic_consulta}")
                   new_data = mh_recepciondte.post_consultadte(dic_consulta,Parametros).sent_data()                  
                   #logger.error(f"Error en Validar Schema PRUEBA token!: {new_data}", exc_info=True)
                   if  new_data['estado'] == "PROCESADO": #new_data['estadoDoc'] == "Transmitido satisfactoriamente":                      
                       mh_result['estado'] =  'PROCESADO' 
                       mh_result['selloRecibido'] =  new_data['selloRecibido']  #new_data['selloVal'] 
                   else:
                       logger.error("El documento consultado no contiene el campo esperado 'estadoDoc' o 'selloVal'")
                       
                respuesta_dte_mh.append(mh_result)
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