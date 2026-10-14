"""
Configuración del bloque "Datos del Cliente" dentro del encabezado.

La mayoría de campos son pares etiqueta:valor de una línea y viven en FILAS_CLIENTE (agregar/quitar uno = editar esa lista). Hay 4 casos que
NO son campos simples y se manejan aparte, con su propia función, porque tienen lógica propia:
  - Dirección: se parte en dos líneas si es muy larga.
  - Incoterms: solo aplica para "Factura de exportación".
  - Documento Relacionado: solo aplica para Nota de Crédito/Débito (05, 06).
  - Orden de Compra: solo aplica si el documento tiene una.
Si mañana alguno de esos 4 deja de ser "especial" (por ejemplo, Incoterms pasa a mostrarse siempre), se puede mover a FILAS_CLIENTE sin problema.
"""
from reportlab.lib.utils import simpleSplit
from dtesv.processes.PDF.pdf_layout_helpers import dibujar_fila_campos, dibujar_campo, resolver_filas


def construir_filas(col1_x, col2_x, col3_x):
    v = col1_x + 80                      # x del valor en la columna izquierda
    return [
        # 0-2: identidad y datos fiscales
        [
            (col1_x, v, "Cliente:", lambda c: f"{c['receptor']['codigo']} - {c['receptor']['nombre']}"),
            (col3_x, col3_x + 38, "NIT:", lambda c: c["receptor"].get("numDocumento")),
        ],
        [
            (col1_x, v, "Nombre Comercial:", lambda c: c["receptor"].get("nombreComercial")),
            (col3_x, col3_x + 38, "NRC:", lambda c: c["receptor"].get("nrc")),
        ],
        [
            (col1_x, v, "Act. Económica:", lambda c: c["receptor"].get("actividad_economica")),
            (col3_x, col3_x + 38, "F. Pago:", lambda c: c["condicion"]),
        ],
        # (aquí va la Dirección, caso especial)
        # 3: ubicación
        [
            (col1_x, v, "Departamento:", lambda c: c["receptor"].get("departamento")),
            (col1_x + 170, col1_x + 215, "Municipio:", lambda c: c["receptor"].get("municipio")),
            (col1_x + 315, col1_x + 350, "Distrito:", lambda c: c["receptor"].get("distrito")),
            (col3_x, col3_x + 38, "Moneda:", lambda c: c["identificacion"].get("tipoMoneda")),
        ],
        # 4: contacto
        [
            (col1_x, v, "Correo:", lambda c: c["receptor"].get("correo")),
            (col3_x, col3_x + 38, "Teléfono:", lambda c: c["receptor"].get("telefono")),
        ],
        # 5: logística
        [
            (col1_x + 80, col1_x + 125, "Vendedor:", lambda c: c["receptor"].get("vendedor")),
            (col1_x + 170, col1_x + 210, "Entrega:", lambda c: c["receptor"].get("rutaEntrega")),
        ],
    ]    


def _dibujar_direccion(p, col1_x, y, direccion, ancho=365):
    dibujar_campo(p, col1_x, col1_x + 80, y, "Dirección:", None, tam_fuente=8)
    p.setFont("Helvetica", 8)
    lineas = simpleSplit(direccion or "", "Helvetica", 8, ancho)[:2] or [""]   # corta por palabra, máx. 2 líneas
    for linea in lineas:
        p.drawString(col1_x + 80, y, linea)
        y -= 10
    return y


def _es_exportacion(ctx):
    return ctx["identificacion"].get("tipoDte") == "11"


def _datos_doc_rel(ctx):
    """(codigoGeneracion, numeroControl, fecha), con '' donde no haya dato."""
    doc = ctx.get("documentoRelacionado") or {}
    return (
        doc.get("codigoGeneracion") or "",
        doc.get("numeroControl") or "",
        ctx.get("docRelFecha_emision") or "",
    )


def _incoterms(ctx):
    return (ctx["receptor"].get("incoterms") or "") if _es_exportacion(ctx) else ""


def hay_referencias(ctx):
    """True solo si existe al menos una referencia con valor."""
    return any(_datos_doc_rel(ctx)) or bool(ctx.get("oCompra")) or bool(_incoterms(ctx))


def dibujar_referencias(p, col1_x, col2_x, col3_x, y_inicio, ctx, alto_fila=10):
    """Dibuja solo las referencias que existen.
    Devuelve la y del borde inferior del recuadro (y_inicio es la línea base de la primera fila)."""
    y = y_inicio

    cod_gen, num_control, fecha = _datos_doc_rel(ctx)
    fila_doc = [
        (col1_x, col1_x + 90, "Documento Relacionado:", cod_gen),
        (col2_x + 56, col2_x + 120, "Número Control:", num_control),
        (col3_x, col3_x + 65, "Fecha Documento:", fecha),
    ]
    fila_doc = [campo for campo in fila_doc if campo[3]]          # quita los vacíos
    if fila_doc:
        dibujar_fila_campos(p, y, fila_doc, tam_fuente=7)
        y -= alto_fila

    fila_extra = []
    if ctx.get("oCompra"):
        fila_extra.append((col1_x, col1_x + 80, "Orden de Compra:", ctx["oCompra"]))
    if _incoterms(ctx):
        fila_extra.append((col2_x + 56, col2_x + 120, "Incoterms:", _incoterms(ctx)))
    if fila_extra:
        dibujar_fila_campos(p, y, fila_extra, tam_fuente=7)
        y -= alto_fila

    return y + alto_fila - 5

def dibujar(p, col1_x, col2_x, col3_x, y_inicio, ctx, alto_fila=10):
    filas = resolver_filas(construir_filas(col1_x, col2_x, col3_x), ctx)
    y = y_inicio

    for fila in filas[:3]:                       # identidad / fiscal
        dibujar_fila_campos(p, y, fila, tam_fuente=8)
        y -= alto_fila

    y = _dibujar_direccion(p, col1_x, y, ctx["receptor"].get("complemento", ""))

    for fila in filas[3:5]:                      # ubicación / contacto
        dibujar_fila_campos(p, y, fila, tam_fuente=8)
        y -= alto_fila

    dibujar_fila_campos(p, y, filas[5], tam_fuente=8)   # vendedor / entrega
    y -= alto_fila

    return y - 6