# from dtesv.models import Documentos
import logging

logger = logging.getLogger(__name__)


def construir_ventaTercero(documentos):
    # Venta Tercero: Aplica a FE, CCFE, NRE, NCE, NDE, FEXE
    # 69 "nit": Default NULL o se debe ingresar sin guiones
    # 70 "nombre": Default NULL o debe ingresarse Nombre, Denominacion o Razón Social del Tercero
    # 71 "domiciliado": Cuando se detalle venta, usar CAT-032

    return None
