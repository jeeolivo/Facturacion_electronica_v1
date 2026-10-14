"""
2026-09-01: Bloque 'detalle' (líneas) del diccionario que consume generar_pdf_con_reportlab.
"""

from dtesv.models import DocumentosDetalle


def construir_detalle(codigoGeneracion, tipo_doc_use):
    """
    tipo_doc_use: documentos.tipodocumento_id del documento padre.
    Se recibe como parámetro (en vez de volver a consultar Documentos) porque quien llama ya lo tiene disponible.
    """
    lineas = []

    detalles = DocumentosDetalle.objects.filter(codigoGeneracion_id=codigoGeneracion)

    for doc in detalles:
        # Sujeto Excluido (14) no trae ventaGravada calculada en el detalle; se calcula aquí como cantidad * precioUni.
        if tipo_doc_use == '14':
            venta_gravada = doc.cantidad * doc.precioUni
        else:
            venta_gravada = doc.ventaGravada

        lineas.append({
            'numItem': doc.numItem,
            'tipoItem': int(doc.tipoItem),
            'numeroDocumento': None,
            'cantidad': doc.cantidad,
            'codigo': doc.codigo,
            'codTributo': None,
            'uniMedida': doc.uniMedida,
            'descripcion': doc.descripcion,
            'precioUni': doc.precioUni,
            'montoDescu': doc.montoDescu,
            'ventaNoSuj': doc.ventaNoSuj,
            'ventaExenta': doc.ventaExenta,
            'ventaGravada': venta_gravada,
            'tributos': None,
            'psv': doc.psv,
            'noGravado': doc.noGravado,
            'ivaItem': doc.ivaItem,
        })

    return lineas