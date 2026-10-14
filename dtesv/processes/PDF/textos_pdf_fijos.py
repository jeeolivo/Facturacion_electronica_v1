"""
Configuración de elementos "fijos" del PDF que no dependen del tipo de documento: pie de página y sello de anulado.

Cambiar el texto, tamaño o color de cualquiera de los dos se hace aquí, sin tocar create_pdf.py.
"""

from reportlab.lib import colors

PIE_PAGINA = {
    "fuente": "Helvetica",
    "tam_fuente": 6,
    "texto": "Página {num_pagina} de {total_paginas}",
}

SELLO_ANULADO = {
    "texto": "INVALIDADO",
    "fuente": "Helvetica-Bold",
    "tam_fuente": 80,
    "color": colors.red,
    "alpha_relleno": 0.3,
    "angulo": 45,
}