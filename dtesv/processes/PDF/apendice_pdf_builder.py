"""
2026-09-01: Bloque 'apendice' del diccionario que consume generar_pdf_con_reportlab.
"""


def construir_apendice(documentos):
    if not documentos.orden_compra:
        return None

    return {
        'campo': 'OrdenCompra',
        'etiqueta': 'Número de Orden de Compra',
        'valor': documentos.orden_compra,
    }