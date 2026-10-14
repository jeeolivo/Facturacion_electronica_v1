# from dtesv.models import Documentos, DocumentosDetalle
import logging

logger = logging.getLogger(__name__)


def construir_identificacion(documentos):

    return {
        # 1
        "version": int(documentos.tipodocumento.version_work),
        # 2 Segun CAT-001
        "ambiente": documentos.emisor_id.ambiente_trabajo.codigo,
        # 3 Segun CAT-002
        "tipoDte": documentos.tipodocumento.codigo,
        # 4 UUID v4 l32
        "codigoGeneracion": documentos.codigoGeneracion,
        # 5 l31: DTE00-P001M001-15digitos
        "numeroControl": documentos.numeroControl,
        # 6 Segun CAT-003 y en contingencias ingresar codigo 2 para: FE, CCFE, NRE, NDR, CRE, FEXE y FSEE
        "tipoModelo": int(documentos.tipoModelo.codigo)
            if documentos.tipoModelo else None,
        # 7 Segun CAT-004  y en contingencias ingresar codigo 2 para: FE, CCFE, NRE, NDR, CRE, FEXE y FSEE
        "tipoOperacion": int(documentos.tipoOperacion.codigo)
            if documentos.tipoOperacion else None,
        # 8 Enviar NULL si hay codigo debe ser segun CAT-005
        "tipoContingencia": documentos.tipoContingencia.codigo
            if documentos.tipoContingencia else None,
        # 9 Enviar NULL mientas tipoContingencia no tenga datos
        "motivoContin": (documentos.motivoContin.strip()
            if documentos.motivoContin and documentos.motivoContin.strip()else None),
        # 10
        "fecEmi": documentos.fecEmi.strftime("%Y-%m-%d"),
        # 11
        "horEmi": documentos.horEmi.strftime("%H:%M:%S"),
        # 12, este debe ser en USD
        "tipoMoneda": documentos.tipoMoneda,
        # 13 "fusion": Este valor se agregara en el adapter correspondiente, NCE, NDE, CRE y CLE
    }