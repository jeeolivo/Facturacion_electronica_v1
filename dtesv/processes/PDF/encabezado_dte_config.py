"""
Configuración del "Recuadro identificación DTE" (código de generación, sello, número de control, modelo, versión, etc.) dentro del encabezado.

Para agregar un campo nuevo: agrega una tupla a la fila que corresponda (o una fila nueva) en FILAS_RECUADRO_DTE. Para quitar uno: elimina su
tupla. No hace falta tocar dibujar_encabezado ni calcular coordenadas a mano — los offsets de columna ya están centralizados en `columnas()`.
"""

from dtesv.processes.PDF.pdf_layout_helpers import dibujar_fila_campos, resolver_filas


def columnas(box_x):
    """Posiciones x reutilizadas por todas las filas del recuadro."""
    return {
        "linea_completa": (box_x + 5, box_x + 75),
        "col1": (box_x + 5, box_x + 75),
        "col2": (box_x + 205, box_x + 270),
    }


def construir_filas(box_x, ctx):
    """
    ctx: dict con, al menos, las claves usadas en los resolvers de abajo (ver `contexto_recuadro_dte` en dibujar_encabezado).
    """
    col = columnas(box_x)
    lc = col["linea_completa"]
    c1 = col["col1"]
    c2 = col["col2"]

    return [
        # Filas de una sola columna (label:valor a lo ancho del recuadro)
        [(lc[0], lc[1], "Código Generación:", lambda c: c["codigoGeneracion"])],
        [(lc[0], lc[1], "Sello de Recepción:", lambda c: c["selloRecibido"])],
        [(lc[0], lc[1], "Número de Control:", lambda c: c["numeroControl"])],

        # Filas de dos columnas
        [
            (c1[0], c1[1], "Modelo facturación:", lambda c: c["modelo"]),
            (c2[0], c2[1], "Versión del JSON:", lambda c: c["version"]),
        ],
        [
            (c1[0], c1[1], "Tipo Transmisión:", lambda c: c["tipo_transmision"]),
            (c2[0], c2[1], "Fecha emisión:", lambda c: c["fecEmi"]),
        ],
        [
            (c1[0], c1[1], "Documento Interno:", lambda c: c["documento_interno"]),
            (c2[0], c2[1], "Hora de Emisión:", lambda c: c["horEmi"]),
        ],
    ]


def dibujar(p, box_x, y_inicio, ctx, alto_fila=10):
    """
    Dibuja todas las filas configuradas y retorna la posición y donde quedó el cursor (por si el llamador necesita seguir dibujando debajo,
    p. ej. el texto pequeño "RG.J01").
    """
    filas = resolver_filas(construir_filas(box_x, ctx), ctx)
    y = y_inicio
    for fila in filas:
        dibujar_fila_campos(p, y, fila, tam_fuente=7)
        y -= alto_fila
    return y