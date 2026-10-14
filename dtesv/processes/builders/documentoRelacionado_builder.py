from dtesv.models import Documentos
import logging

logger = logging.getLogger(__name__)


def construir_documentoRelacionado(documentos):
    if documentos.receptor_id and documentos.tipodocumento.codigo == "18":
        documentoRelacionado = asociadoRetorno(documentos)
    else:
        documentoRelacionado = asociadoOtros(documentos)

    return documentoRelacionado


def obtener_documento_relacionado_obj(documentos):
    """
    Devuelve el registro `Documentos` relacionado (o None), reutilizando el mismo criterio de búsqueda que asociadoRetorno/asociadoOtros.
    Permite a otras capas (p. ej. tributo_rules.obtener_total_iva_resumen) leer el código MH del documento relacionado sin repetir la query ni depender de la PK interna.
    """
    return Documentos.objects.filter(codigoGeneracion=documentos.numeroDocumento_rel_guid).first()

def asociadoRetorno(documentos):
    relacionado = Documentos.objects.filter(codigoGeneracion=documentos.numeroDocumento_rel_guid).first()
    if not relacionado:
        return None

    return [{
        # 14 Segun CAT-002: Relaciona doc. fisicos y electronicos, NCE y NDE Requerido, FE, CCFE, NRE y FEXE: cuando no exista debe enviarse NULL.
        "tipoDocumento": relacionado.tipodocumento_id,
        # 16 Ingresar Electronico: codigoGeneracion/Fisico:  Serie + N° Correlativo, si no existe enviar NULL, NCE y NDE Requerido, FE, CCFE, NRE y FEXE: cuando no exista debe enviarse NULL.
        "codigoGeneracion": relacionado.codigoGeneracion,
        # 17 NCE y NDE Requerido, FE, CCFE, NRE y FEXE: cuando no exista debe enviarse NULL.
        "fechaEmision": relacionado.fecEmi.strftime("%Y-%m-%d")
    }] 

def asociadoOtros(documentos):
    relacionado = Documentos.objects.filter(codigoGeneracion=documentos.numeroDocumento_rel_guid).first()
    if not relacionado:
        return None

    return [{
        # 14 Segun CAT-002: Relaciona doc. fisicos y electronicos, NCE y NDE Requerido, FE, CCFE, NRE y FEXE: cuando no exista debe enviarse NULL.
        "tipoDocumento": relacionado.tipodocumento_id,
        # 15 Segun CAT-007: NCE y NDE Requerido, FE, CCFE, NRE y FEXE: cuando no exista debe enviarse NULL.
        "tipoGeneracion": 2,
        # 16 Ingresar Electronico: codigoGeneracion/Fisico:  Serie + N° Correlativo, si no existe enviar NULL, NCE y NDE Requerido, FE, CCFE, NRE y FEXE: cuando no exista debe enviarse NULL.
        "numeroDocumento": relacionado.codigoGeneracion,
        # 17 NCE y NDE Requerido, FE, CCFE, NRE y FEXE: cuando no exista debe enviarse NULL.
        "fechaEmision": relacionado.fecEmi.strftime("%Y-%m-%d")
        }] 