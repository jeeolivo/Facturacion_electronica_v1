from decimal import Decimal
from dtesv.models import Pagos, DocumentosDetalle
from dtesv.processes.builders.documentoRelacionado_builder import (
    obtener_documento_relacionado_obj
)
from dtesv.processes.rules.tributo_rules import (
    obtener_total_iva_resumen,
    TributoRuleError,
)
import logging
import json

logger = logging.getLogger(__name__)

# tipoDte donde totalIva depende de validar el documento relacionado (NCE y NDE). Único lugar donde se resuelve esta consulta.
TIPOS_DTE_CON_VALIDACION_RELACIONADO = ("05", "06")

def construir_resumen(documentos):
    pagos = Pagos.objects.filter(codigogeneracion_doc=documentos.codigoGeneracion).first()
    tipo_dte = documentos.tipodocumento.codigo
    detalles = DocumentosDetalle.objects.filter(codigoGeneracion_id=documentos.codigoGeneracion)

    # Solo se resuelve el documento relacionado cuando el tipo de documento realmente lo requiere (NCE/NDE). 
    # Este es el ÚNICO punto del pipeline donde se hace esta consulta y esta validación; 
    # los adapters (NotaCreditoAdapter, NotaDebitoAdapter, etc.) NO deben volver a llamar a obtener_total_iva_resumen ni a resolver tipo_doc_relacionado por su cuenta — deben conservar el totalIva que ya viene calculado aquí.
    tipo_doc_relacionado = None
    if tipo_dte in TIPOS_DTE_CON_VALIDACION_RELACIONADO:
        relacionado = obtener_documento_relacionado_obj(documentos)
        tipo_doc_relacionado = (relacionado.tipodocumento.codigo if relacionado else None)

    total_iva = obtener_total_iva_resumen(documentos, detalles, tipo_dte, tipo_doc_relacionado)

    resumen = {
        # 123
        "totalNoSuj": Decimal(str(documentos.totalNoSuj)) if documentos.totalNoSuj is not None else Decimal("0"),
        # 124
        "totalExenta": Decimal(str(documentos.totalExenta)) if documentos.totalExenta is not None else Decimal("0"),
        # 125
        "totalGravada": Decimal(str(documentos.totalGravada)) if documentos.totalGravada is not None else Decimal("0"),
        # 126 "exportacion": Agregado en adapter, Aplica a CLE
        # 127 "totalCompra": Agregado en adapter, Aplica a FSEE
        # 128 "valorTotal": Agregado en adapter, Aplica a CDE 
        # 129
        "subTotalVentas": Decimal(str(documentos.subTotalVentas)) if documentos.subTotalVentas is not None else Decimal("0"),
        # 130
        "descuNoSuj": Decimal(str(documentos.descuNoSuj)) if documentos.descuNoSuj is not None else Decimal("0"),
        # 131
        "descuExenta": Decimal(str(documentos.descuExenta)) if documentos.descuExenta is not None else Decimal("0"),
        # 132
        "descuGravada": Decimal(str(documentos.descuGravada)) if documentos.descuGravada is not None else Decimal("0"),
        # 133 "descu": Agregado en adapter, Aplica a FSEE
        # 134
        "porcentajeDescuento": Decimal(str(documentos.porcentajeDescuento)) if documentos.porcentajeDescuento is not None else Decimal("0"),
        # 135
        "totalDescu": Decimal(str(documentos.totalDescu)) if documentos.totalDescu is not None else Decimal("0"),
        "tributos": None,
        # 136 "tibutos.codigo": Mostrar los codigos de la seccion 3 CAT-015 para uso informativo
        # 137 "tributos.descripcion": Mostrar la descripcion de la seccion 3 CAT-015 para uso informativo
        # 138 "tributos.valor" Mostrar el calculo consolidado de los tributos aplicados en Codigo del Tributo, aplicando la seccion 3 CAT-015 para uso informativo
        # 139 
        "subTotal": Decimal(str(documentos.subTotalVentas - (documentos.descuGravada + documentos.descuExenta + documentos.descuNoSuj))) if documentos.subTotalVentas is not None else Decimal("0"),
        # 140 
        "totalSujetoRetencion": Decimal(str(documentos.totalSujetoRetenido)) if documentos.totalSujetoRetenido is not None else Decimal("0"), # Agregado en adapter, Aplica a CRE
        # 141 - 143 "ivaPerci": Agregado en adapter, Aplica a CCFE y CLE  -- NCE y NDE
    #    # 142 - 145
        "ivaRete": Decimal(str(documentos.ivaRete1)) if documentos.ivaRete1 is not None else Decimal("0"), # Agregar a adapter, Aplica a FE y CCFE -- NCE y NDE
        # 144 "codigoRetencionMH": Cuando se ajuste 07-CRE ingresar CAT-006, si es CCFE colocar NULL, APlica a NCE y NDE
    #    # 146 - 157 
        "totalIva": total_iva, # Aplica NCE y NDE -- FE y CRE
    #    # 147 : Agregar en adapter, Aplica a FSEE
        "reteRenta": Decimal(str(documentos.reteRenta)) if documentos.reteRenta is not None else Decimal("0"),
        # 148 "seguro": Agregado en adapter, Aplica a FEXE
        # 149 "flete": Agregado en adapter, Aplica a FEXE
        # 150 : Aplicado a FE, CCFE, NCE, NDE y FEXE
        "montoTotalOperacion": Decimal(str(documentos.montoTotalOperacion)) if documentos.montoTotalOperacion is not None else Decimal("0"),
        # 151 : Aplicado a FE, CCFE, NCE, NDE y FEXE
        "totalNoGravado": Decimal(str(documentos.totalNoGravado)) if documentos.totalNoGravado is not None else Decimal("0"),
        # 152 "totalNoOnerosa": Aplica a FEXE
        # 153 : Aplicado a FE, CCFE, NCE, NDE y FEXE
        "totalPagar": Decimal(str(documentos.totalPagar)) if documentos.totalPagar is not None else Decimal("0"),
        # 154 "total": MontoTotalOperacion + IvaPercibidoLiquidado, Aplica a CLE
        # 155 
        "totalIvaRetenido": Decimal(str(documentos.totalIVAretenido)) if documentos.totalIVAretenido is not None else Decimal("0"), # Es el IvaRetenido, Aplica a CRE
        # 156 : Aplicado a FE, CCFE, NRE, NCE, NDE, CRE, CLE, FEXE, FSEE y CDE
        "totalLetras": documentos.totalLetras,
        # 158 : Aplicado a FE, CCFE y FEXE
        "saldoFavor": Decimal(str(documentos.saldoFavor)) if documentos.saldoFavor is not None else Decimal("0"),
        # 159 : Aplicado a FE, CCFE, NCE, NDE, CLE, FEXE y FSEE
        #"condicionOperacion": documentos.condicionOperacion.codigo,
        "condicionOperacion": 2 if tipo_dte == "11" else documentos.condicionOperacion.codigo,
        "pagos": [
            {   # 160
                "codigo": pagos.codigo_forma_pago,
                # 161
                "montoPago": Decimal(str(pagos.monto)) if pagos.monto is not None else Decimal("0"),
                # 162
                "referencia": None,
                # 163
                "plazo": Decimal(str(pagos.plazo)) if pagos.plazo is not None else Decimal("0"),
                # 164
                "periodo": int(pagos.periodo),
            }
        ]
        if pagos else None,
            # 165
            "numPagoElectronico": None,
        # 166 "codIcoterms": Codigo Segun CAT-031.Aplica a FEXE
        # 167 "desIcoterms": Descripcion Segun CAT-031.Aplica a FEXE
        # 168 Enviar null si no se hace uso
        "observaciones": None
    }

    # Este logger permite visualizar una previa del resumen a enviar a certificacion.
    # logger.error(json.dumps(resumen,indent=4,default=str,ensure_ascii=False))

    return resumen