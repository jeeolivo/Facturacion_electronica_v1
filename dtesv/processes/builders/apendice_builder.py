# from dtesv.models import Documentos
import logging

logger = logging.getLogger(__name__)


def construir_apendice(documentos):
    apendice = documentos.orden_compra
    if not apendice:
        return None
    
    return [{
        # 172
        'campo':'OrdenCompra',
        # 173
        'etiqueta':'Número de Orden de Compra',
        # 174
        'valor': documentos.orden_compra
    }]
        