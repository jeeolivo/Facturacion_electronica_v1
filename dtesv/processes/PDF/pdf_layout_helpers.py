"""
Helpers de dibujo genéricos, reutilizados por los distintos bloques del encabezado del PDF (recuadro de identificación DTE, datos del cliente, etc.)

La idea: separar QUÉ se dibuja (listas de configuración, en los módulos *_config.py) de CÓMO se dibuja (estas funciones). Así, agregar/quitar un
campo es editar una lista, no escribir código de ReportLab nuevo.
"""


def dibujar_campo(p, x_label, x_valor, y, etiqueta, valor, tam_fuente=7):
    """
    Dibuja un par etiqueta:valor. `etiqueta` en negrita en x_label, `valor` en fuente normal en x_valor, ambos a la altura y.
    `valor=None` se dibuja como cadena vacía en vez de "None".
    """
    p.setFont("Helvetica-Bold", tam_fuente)
    p.drawString(x_label, y, etiqueta)
    p.setFont("Helvetica", tam_fuente)
    p.drawString(x_valor, y, "" if valor is None else str(valor))


def dibujar_fila_campos(p, y, campos, tam_fuente=7):
    """
    campos: lista de tuplas (x_label, x_valor, etiqueta, valor). Dibuja todos los campos de una fila a la misma altura `y`.
    Una fila puede tener 1, 2, 3... campos; el número de columnas lo define la propia lista, no esta función.
    """
    for x_label, x_valor, etiqueta, valor in campos:
        dibujar_campo(p, x_label, x_valor, y, etiqueta, valor, tam_fuente)


def resolver_filas(filas_config, contexto):
    """
    filas_config: lista de filas, cada fila es una lista de (x_label, x_valor, etiqueta, resolver) donde `resolver` es
    callable(contexto) -> valor.

    Devuelve la misma estructura pero con los valores ya resueltos, lista para pasar a dibujar_fila_campos.
    """
    filas_resueltas = []
    for fila in filas_config:
        fila_resuelta = [
            (x_label, x_valor, etiqueta, resolver(contexto))
            for (x_label, x_valor, etiqueta, resolver) in fila
        ]
        filas_resueltas.append(fila_resuelta)
    return filas_resueltas