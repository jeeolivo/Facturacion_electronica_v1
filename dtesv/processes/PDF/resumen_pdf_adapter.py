"""
Adapters de "resumen" para la generación del PDF del DTE.

Reemplaza la lógica repartida entre `construir_diccionario` (armaba TODOS los campos y filtraba con `key_for_resumen`, genérico) y `generar_pdf_con_reportlab` 
(volvía a filtrar con `elimina_claves_por_tipo`, por tipo, y además tenía un `if tipo_doc == '07'` suelto para renombrar 'TOTAL A PAGAR (=)' -> 'IVA RETENIDO').

Mismo patrón que dtesv/processes/adapters/adapter_factory.py: un factory que resuelve el adapter según `documentos.tipodocumento.codigo` / `tipodocumento_id`,
y cada adapter concreto declara SOLO los campos que le corresponden, en el orden en que deben imprimirse. No hay "armar todo y luego borrar".
"""

import logging

logger = logging.getLogger(__name__)


class ResumenAdapterBase:
    """
    `campos` es una tupla ordenada de (etiqueta, origen), donde `origen` es:
      - el nombre de un atributo de `documentos` (str), o
      - un callable que recibe `documentos` y retorna el valor.

    El resultado tiene la misma forma que el `resumen_copia` original:
    {"etiqueta": {"valor": ...}, ...}
    """
    campos = ()

    @classmethod
    def construir(cls, documentos):
        resumen = {}
        for etiqueta, origen in cls.campos:
            valor = origen(documentos) if callable(origen) else getattr(documentos, origen, None)
            resumen[etiqueta] = {"valor": valor}
        return resumen


# ---------------------------------------------------------------------
# Campos comunes, reutilizados por los adapters concretos.
# Se definen una sola vez para no repetir el nombre del atributo del
# modelo Documentos en cada adapter.
# ---------------------------------------------------------------------

def _suma_total_operacion(documentos):
    # Para sujeto excluido (14) y retención (07) el total de la operación viene de otro campo del modelo.
    if documentos.tipodocumento_id in ("14", "07"):
        return documentos.totalSujetoRetenido
    return documentos.subTotalVentas


CAMPO_TOTAL_LETRAS = ("Total en Letras", "totalLetras")
CAMPO_SUMA_TOTAL = ("Suma Total Operación (+)", _suma_total_operacion)
CAMPO_DESCUENTO = ("Monto Total Descuento (-)", "descuGravada")
CAMPO_RETENCION_RENTA = ("Retencion Renta (-)", "reteRenta")
CAMPO_IVA = ("IVA (+)", "iva")
CAMPO_SUBTOTAL = ("Sub Total (=)", "montoTotalOperacion")
CAMPO_IVA_PERCIBIDO = ("IVA Percibido (+)", "ivaPerci1")
CAMPO_IVA_RETENIDO = ("IVA Retenido (-)", "ivaRete1")
CAMPO_MONTO_OPERACION = ("Monto Total de la Operación (=)", "totalPagar")
CAMPO_OTROS_NO_AFECTOS = ("Otros Montos no Afectos (+)", "totalNoGravado")
CAMPO_FLETE = ("Flete (+)", "flete")
CAMPO_SEGURO = ("Seguro (+)", "seguro")
CAMPO_TOTAL_PAGAR = ("TOTAL A PAGAR (=)", "totalPagar")
CAMPO_TIPO_DOCUMENTO = ("tipoDocumento", "tipodocumento_id")


class FacturaAdapter(ResumenAdapterBase):          # tipoDte 01
    campos = (
        CAMPO_TOTAL_LETRAS,
        CAMPO_SUMA_TOTAL,
        CAMPO_DESCUENTO,
        CAMPO_SUBTOTAL,
        CAMPO_IVA_PERCIBIDO,
        CAMPO_IVA_RETENIDO,
        CAMPO_MONTO_OPERACION,
        CAMPO_OTROS_NO_AFECTOS,
        CAMPO_TOTAL_PAGAR,
        CAMPO_TIPO_DOCUMENTO,
    )


class CreditoFiscalAdapter(ResumenAdapterBase):    # tipoDte 03
    campos = (
        CAMPO_TOTAL_LETRAS,
        CAMPO_SUMA_TOTAL,
        CAMPO_DESCUENTO,
        #CAMPO_RETENCION_RENTA,
        CAMPO_IVA,
        CAMPO_SUBTOTAL,
        CAMPO_IVA_PERCIBIDO,
        CAMPO_IVA_RETENIDO,
        CAMPO_MONTO_OPERACION,
        CAMPO_OTROS_NO_AFECTOS,
        #CAMPO_FLETE,
        #CAMPO_SEGURO,
        CAMPO_TOTAL_PAGAR,
        CAMPO_TIPO_DOCUMENTO,
    )


class NotaCreditoAdapter(CreditoFiscalAdapter):    # tipoDte 05 (mismo layout que CCF)
    pass


class NotaDebitoAdapter(CreditoFiscalAdapter):     # tipoDte 06 (mismo layout que CCF)
    pass


class RetencionAdapter(ResumenAdapterBase):        # tipoDte 07
    campos = (
        CAMPO_TOTAL_LETRAS,
        CAMPO_SUMA_TOTAL,
        # Antes: se copiaba 'TOTAL A PAGAR (=)' y se renombraba a mano
        # a 'IVA RETENIDO' con un `if tipo_doc == '07':` suelto.
        ("IVA RETENIDO", "totalPagar"),
        CAMPO_TIPO_DOCUMENTO,
    )


class ExportacionAdapter(ResumenAdapterBase):      # tipoDte 11
    campos = (
        CAMPO_TOTAL_LETRAS,
        CAMPO_SUMA_TOTAL,
        CAMPO_FLETE,
        CAMPO_SEGURO,
        CAMPO_TOTAL_PAGAR,
        CAMPO_TIPO_DOCUMENTO,
    )


class SujetoExcluidoAdapter(ResumenAdapterBase):   # tipoDte 14
    campos = (
        CAMPO_TOTAL_LETRAS,
        CAMPO_SUMA_TOTAL,
        CAMPO_RETENCION_RENTA,
        CAMPO_MONTO_OPERACION,
        CAMPO_TOTAL_PAGAR,
        CAMPO_TIPO_DOCUMENTO,
    )

class EventoRetornoAdapter(ResumenAdapterBase):   # tipoDte 18
    campos = (
        CAMPO_TOTAL_LETRAS,
        CAMPO_SUMA_TOTAL,
        CAMPO_DESCUENTO,
        CAMPO_SUBTOTAL,
        CAMPO_IVA_PERCIBIDO,
        CAMPO_IVA_RETENIDO,
        CAMPO_MONTO_OPERACION,
        CAMPO_OTROS_NO_AFECTOS,
        CAMPO_TOTAL_PAGAR,
        CAMPO_TIPO_DOCUMENTO,
    )


_ADAPTERS = {
    "01": FacturaAdapter,
    "03": CreditoFiscalAdapter,
    "05": NotaCreditoAdapter,
    "06": NotaDebitoAdapter,
    "07": RetencionAdapter,
    "11": ExportacionAdapter,
    "14": SujetoExcluidoAdapter,
    "18": EventoRetornoAdapter,
}


def construir_resumen(documentos):
    """
    Punto de entrada único. Reemplaza:
      - el bloque de ~95 líneas en `construir_diccionario` que armaba `resumen` completo + `key_for_resumen` + `resumen_copia`, y
      - el bloque `elimina_claves_por_tipo` + el `if tipo_doc == '07'` dentro de `generar_pdf_con_reportlab`.

    `generar_pdf_con_reportlab` recibe el resultado ya filtrado y en el orden correcto para su tipo de documento; no necesita volver a tocarlo.
    """
    adapter = _ADAPTERS.get(documentos.tipodocumento_id)

    if not adapter:
        logger.error(
            "No hay ResumenAdapter para tipoDte=%s (codigoGeneracion=%s); "
            "se usa FacturaAdapter como valor por defecto.",
            documentos.tipodocumento_id,
            documentos.codigoGeneracion,
        )
        adapter = FacturaAdapter

    return adapter.construir(documentos)