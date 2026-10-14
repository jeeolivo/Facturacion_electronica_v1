from .factura_adapter import FacturaAdapter
from .creditoFiscal_adapter import CreditoFiscalAdapter
from .notaCredito_adapter import NotaCreditoAdapter
from .notaDebito_adapter import NotaDebitoAdapter
from .exportacion_adapter import ExportacionAdapter
from .retencion_adapter import RetencionAdapter
from .sujetoExcluido_adapter import SujetoExcluidoAdapter
from .evento_retorno_adapter import EventoRetornoAdapter
import logging

logger = logging.getLogger(__name__)

def aplicar(documentos, diccionario):

    adapters = {
        "01": FacturaAdapter,
        "03": CreditoFiscalAdapter,
        "05": NotaCreditoAdapter,
        "06": NotaDebitoAdapter,
        "07": RetencionAdapter,
        "11": ExportacionAdapter,
        "14": SujetoExcluidoAdapter,
        "18": EventoRetornoAdapter,
    }

    adapter = adapters.get(documentos.tipodocumento.codigo)
    logger.error (f"Codigo del documento seleccionado: {documentos.tipodocumento.codigo} - Adapter seleccionado: {adapter.__name__ if adapter else 'Ninguno'}")

    if adapter:

        return adapter.aplicar(
            documentos,
            diccionario
        )

    return diccionario