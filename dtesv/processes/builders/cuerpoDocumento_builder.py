#from Facturacion_electronica.dtesv.processes.utils.diccionario import DiccionarioUtil
from dtesv.models import DocumentosDetalle
from dtesv.processes.rules.tributo_rules import (
    obtener_cod_tributo,
    obtener_campos_iva_detalle,
    obtener_tributos_detalle,
)
from decimal import Decimal
import logging
import json

logger = logging.getLogger(__name__)

def construir_cuerpo(documentos):

    tipo_dte = documentos.tipodocumento.codigo
    detalles = DocumentosDetalle.objects.filter(
        codigoGeneracion_id=documentos.codigoGeneracion
    )

    if documentos.receptor_id and documentos.tipodocumento.codigo == "18":
        logger.error (f"Preparando Cuerpo Documento, tipo {tipo_dte} para {documentos.codigoGeneracion} con {detalles.count()} detalles.")
        documentoRelacionado = cuerpoRetorno(detalles, tipo_dte)
    else:
        logger.error (f"Preparando Cuerpo Documento, tipo {tipo_dte} para {documentos.codigoGeneracion} con {detalles.count()} detalles.")
        documentoRelacionado = cuerpoVentas(detalles, tipo_dte)

    return documentoRelacionado


def cuerpoRetorno(detalles, tipo_dte):
    cuerpo = []

    for detalle in detalles:
        # Reorganizando la asignacion de los tributos y las asignaciones de IVA
        campos_iva = obtener_campos_iva_detalle(detalle, tipo_dte)
        cod_tributo = obtener_cod_tributo(detalle, tipo_dte)
        tributos = obtener_tributos_detalle(detalle, tipo_dte)

        cuerpo.append({
            # 74
            "numItem": detalle.numItem,
            # 75 Segun CAT-011, este se puede vincular con CAT-015 si el codigo asignado es 4
            "tipoItem": int(detalle.tipoItem),
            # 80
            "codigoGeneracion": detalle.numeroDocumento
                if detalle.numeroDocumento and detalle.numeroDocumento.strip()
                else None,
            # 82
            "cantidad": Decimal(str(detalle.cantidad)) if detalle.cantidad is not None else Decimal("0"),
            # 87
            "precioUni": Decimal(str(detalle.precioUni)) if detalle.precioUni is not None else Decimal("0"),
            # 86
            "descripcion": detalle.descripcion,
            # 83
            "codigo": detalle.codigo,
            # 85
            "uniMedida": detalle.uniMedida,
            # 89
            "montoDescu": Decimal(str(detalle.montoDescu)) if detalle.montoDescu is not None else Decimal("0"),
            # 84 Apartado especial, para uso con CAT-015 si se ingreso codigo 4 en tipoItem
            "codTributo": cod_tributo,
            # 90
            "ventaNoSuj": Decimal(str(detalle.ventaNoSuj)) if detalle.ventaNoSuj is not None else Decimal("0"),
            # 91
            "ventaExenta": Decimal(str(detalle.ventaExenta)) if detalle.ventaExenta is not None else Decimal("0"),
            # 92
            "ventaGravada": Decimal(str(detalle.ventaGravada)) if detalle.ventaGravada is not None else Decimal("0"),
            # 93 "exportaciones": en la descripcion relaciona a FEXE, pero aplica a CLE
            # 94 "valor": resultado de (valorUnitario * cantidad) - Depreciacion. Agregado a adapter, Aplica a CDE
            # 95 
            "compra": Decimal("0.00"), # resultado de (precioUnitario * cantidad) - DescuentoItem. Agregado a adapter, Aplica a FSEE
            # 96 Ingresar segun CAT-015 secciones 1 y 3
            "tributos": tributos,
            # 97
            "psv": Decimal(str(detalle.psv)) if detalle.psv is not None else Decimal("0"),
            # 98
            "noGravado": Decimal(str(detalle.noGravado)) if detalle.noGravado is not None else Decimal("0"),
            "seguro": Decimal("0.00"),
            "flete": Decimal("0.00"),
            # 101 
            "ivaRete": Decimal(str(campos_iva["ivaRete"])) if campos_iva["ivaRete"] is not None else Decimal("0"), # Requerido en NCE y NDE
            # 102
            "ivaItem": Decimal(str(campos_iva["ivaItem"])) if campos_iva["ivaItem"] is not None else Decimal("0"), # Requerido en FE y CLE            
            "reteRenta": Decimal("0.00")
        })

        # Este logger permite visualizar como esta estructurado el cuerpo antes de certificar.
        # logger.error(json.dumps(cuerpo,indent=4,default=str,ensure_ascii=False))

    return cuerpo


def cuerpoVentas(detalles, tipo_dte):
    cuerpo = []

    for detalle in detalles:
        # Reorganizando la asignacion de los tributos y las asignaciones de IVA
        campos_iva = obtener_campos_iva_detalle(detalle, tipo_dte)
        cod_tributo = obtener_cod_tributo(detalle, tipo_dte)
        tributos = obtener_tributos_detalle(detalle, tipo_dte)
        #logger.error(f"Datos del detalle: tributos {tributos} codTributo: {cod_tributo}, campoIva: {campos_iva}")

        cuerpo.append({
            # 74
            "numItem": detalle.numItem,
            # 75 Segun CAT-011, este se puede vincular con CAT-015 si el codigo asignado es 4
            "tipoItem": int(detalle.tipoItem),
            # 76 "tipoDonacion": Segun CAT-026 Aplicado en adapter CDE
            # 77 "tipoDepreciacion": Ingresar el valor de la depreciacion del bien donado, si valor es 2 segun CAT-026 Aplicado en adapter, Aplica a CDE
    #        # 78 Indicado segun CAT-002, Agregarlo al Adapter. Aplicado a CRE y CLE
            "tipoDte": detalle.tipoDte.codigo
                if detalle.tipoDte else None,
            # 79 en la version 1 para CRE se usa tipoDoc
            "tipoGeneracion": int(detalle.tipoDoc.codigo)  # Segun CAT-007, Aplicado a CRE y CLE
                if detalle.tipoDoc else None,
            # 80
            "numeroDocumento": detalle.numeroDocumento
                if detalle.numeroDocumento and detalle.numeroDocumento.strip()
                else None,
            # 81                
            "fechaEmision": detalle.fechaEmision.strftime("%Y-%m-%d")
                if detalle.fechaEmision else None,
            # 82
            "cantidad": Decimal(str(detalle.cantidad)) if detalle.cantidad is not None else Decimal("0"),
            # 83
            "codigo": detalle.codigo,
            # 84 Apartado especial, para uso con CAT-015 si se ingreso codigo 4 en tipoItem
            "codTributo": cod_tributo,
            # 85
            "uniMedida": detalle.uniMedida,
            # 86
            "descripcion": detalle.descripcion,
            # 87
            "precioUni": Decimal(str(detalle.precioUni)) if detalle.precioUni is not None else Decimal("0"),
            # 88 "valorUni": costo de servicios donados o monto total de la donacion. Agregado a adapter, Aplica a CDE
            # 89
            "montoDescu": Decimal(str(detalle.montoDescu)) if detalle.montoDescu is not None else Decimal("0"),
            # 90
            "ventaNoSuj": Decimal(str(detalle.ventaNoSuj)) if detalle.ventaNoSuj is not None else Decimal("0"),
            # 91
            "ventaExenta": Decimal(str(detalle.ventaExenta)) if detalle.ventaExenta is not None else Decimal("0"),
            # 92
            "ventaGravada": Decimal(str(detalle.ventaGravada)) if detalle.ventaGravada is not None else Decimal("0"),
            # 93 "exportaciones": en la descripcion relaciona a FEXE, pero aplica a CLE
            # 94 "valor": resultado de (valorUnitario * cantidad) - Depreciacion. Agregado a adapter, Aplica a CDE
            # 95 "compra": resultado de (precioUnitario * cantidad) - DescuentoItem. Agregado a adapter, Aplica a FSEE
            # 96 Ingresar segun CAT-015 secciones 1 y 3
            "tributos": tributos,
            # 97
            "psv": Decimal(str(detalle.psv)) if detalle.psv is not None else Decimal("0"),
            # 98
            "noGravado": Decimal(str(detalle.noGravado)) if detalle.noGravado is not None else Decimal("0"),
            # 99 
            "ivaPerci": Decimal(str(campos_iva["ivaPerci"])) if campos_iva["ivaPerci"] is not None else Decimal("0"),  # Requerido en NCE y NDE
            # 100 
            "totalIva": Decimal(str(campos_iva["totalIva"])) if campos_iva["totalIva"] is not None else Decimal("0"), # Requerido en NCE y NDE
            # 101 
            "ivaRete": Decimal(str(campos_iva["ivaRete"])) if campos_iva["ivaRete"] is not None else Decimal("0"), # Requerido en NCE y NDE
            # 102
            "ivaItem": Decimal(str(campos_iva["ivaItem"])) if campos_iva["ivaItem"] is not None else Decimal("0"), # Requerido en FE y CLE
            # 103
            "montoSujetoGrav": Decimal(str(detalle.ventaGravada)) if detalle.ventaGravada is not None else Decimal("0"), # Aplicar en adapter. Requerido en CRE
            # 104
            "codigoRetencionMH": detalle.codigoRetencionMH.codigo  # Aplicar en adapter. Requerido en CRE
                if detalle.codigoRetencionMH else None,
            # 105 "ivaRetenido"
            "ivaRetenido": Decimal(str(detalle.ivaItem)) if detalle.ivaItem is not None else Decimal("0"),  # Aplicar en adapter. Requerido en CRE
            # 106 "periodoLiquidacionFechaInicio": Aplicado en adapter. Requerido en DCLE
            # 107 "periodoLiquidacionFechaFin": Aplicado en adapter. Requerido en DCLE
            # 108 "codLiquidacion": Aplicado en adapter. Requerido en DCLE
            # 109 "cantidadDoc": Aplicado en adapter. Requerido en DCLE
            # 110 "valOperaciones": Aplicado en adapter. Requerido en DCLE
            # 111 "montoSinPercepcion": Aplicado en adapter. Requerido en DCLE
            # 112 "descripSinPercepcion": Aplicado en adapter. Requerido en DCLE
            # 113 "observaciones": Aplicado en adapter. Requerido en CLE y DCLE
            # 114 "subTotal": Aplicado en adapter. Requerido en DCLE
            # 115 "sujetoPercepcion": Aplicado en adapter. Requerido en DCLE
            # 116 "iva": Aplicado en adapter. Requerido en DCLE
            # 117 "ivaPercibido": : Aplicado en adapter. Requerido en DCLE
            # 118 "comision": Aplicado en adapter. Requerido en DCLE
            # 119 "porcentComision": Aplicado en adapter. Requerido en DCLE
            # 120 "ivaComision": Aplicado en adapter. Requerido en DCLE
            # 121 "liquidacionApagar": Aplicado en adapter. Requerido en DCLE
            # 122 "totalLetras": Aplicado en adapter. Requerido en DCLE

            # Otros campos de uso interno DM
            "tipoDoc": int(detalle.tipoDoc.codigo)
                if detalle.tipoDoc else None,
            "numDocumento": detalle.numeroDocumento # Este creo que se puede eliminar
            
        })

        # Este logger permite visualizar como esta estructurado el cuerpo antes de certificar.
        # logger.error(json.dumps(cuerpo,indent=4,default=str,ensure_ascii=False))

    return cuerpo