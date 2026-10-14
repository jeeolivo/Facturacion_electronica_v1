# from dtesv.models import Documentos, DocumentosDetalle
import logging

logger = logging.getLogger(__name__)


def construir_emisor(documentos):
    logger.error (f"Preparando datos del emisor {documentos.emisor_id.nombre}")
    return {
        # 18, Aplica a: FE, CCRE, NRE, NCE, NDE, CRE, CLE, DCLE, FEXE, FSEE
        "nit": documentos.emisor_id.nit,
        # 19 "tipoDocumento":  Aplica en adapter CDE, unicamente se ingresa el codigo 36-NIT
        # 20 "numDocumento": Aplicar en adapter CDE, Ingresar NIT del donatorio
        # 21 El NRC debe ir sin guiones y sin ceros a la izquierda
        "nrc": documentos.emisor_id.nrc,
        # 22
        "nombre": documentos.emisor_id.nombre,
        # 23 Segun CAT-019
        "codActividad": documentos.emisor_id.codactividad.codigo,
        # 24 Segun la descripcion del CAT-019
        "descActividad": documentos.emisor_id.codactividad.nombre,
        # 25
        "nombreComercial": documentos.emisor_id.nombrecomercial,
        "direccion":{
            # 26
            "departamento": documentos.emisor_id.departamento.codigo,
            # 27
            "municipio": documentos.emisor_id.municipio.codigo, # documentos.emisor_id.munidistrito.codigo,
            # 28
            #"distrito": documentos.emisor_id.municipio.codigo,
            # 29
            "complemento": documentos.emisor_id.direccion_complemento
        },
        # 30
        "telefono": documentos.emisor_id.telefono,
        # 31
        "correo": documentos.emisor_id.correo,
        # 32
        "codEstable": documentos.emisor_id.codestable,
        # 33
        "codPuntoVenta": documentos.emisor_id.codpuntoventa,
        # 34 "tipoItemExport": Usar segun CAT-011, los datos se agregan directo en adapter, aplica a: FEXE
        # 35 "recintoFiscal": Usar segun CAT-027, los datos se agregan directo en adapter, aplica a: FEXE
        # 36 "tipoRegimen": Usar segun CAT-033, los datos se agregan directo en adapter, aplica a: FEXE
        # 37 "regimen": Usar segun CAT-028, los datos se agregan directo en adapter, aplica a: FEXE

        # Estos datos son para control interno en la base
        "tipoEstablecimiento": documentos.emisor_id.tipoestablecimiento.codigo,
        "codEstableMH": documentos.emisor_id.codestablemh,
        "codPuntoVentaMH": documentos.emisor_id.codpuntoventamh

    }  