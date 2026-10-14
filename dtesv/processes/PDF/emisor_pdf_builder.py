"""
2026-09-01: Bloque 'emisor' (info_empresa) del diccionario que consume generar_pdf_con_reportlab.
"""

def construir_emisor(documentos):
    emisor = documentos.emisor_id

    return {
        'ID': emisor.id,
        'nit': emisor.nit,
        'nrc': emisor.nrc,
        'nombre': emisor.nombre,
        'codActividad': emisor.codactividad.codigo,
        'descActividad': emisor.codactividad.nombre,
        'nombreComercial': emisor.nombrecomercial,
        'tipoEstablecimiento': emisor.tipoestablecimiento.codigo,
        'departamento': emisor.departamento.codigo,
        'municipio': emisor.munidistrito.codigo,
        'distrito': emisor.municipio.codigo,
        'direccion_complemento': emisor.direccion_complemento,
        'telefono': emisor.telefono,
        'correo': emisor.correo,
        'codEstableMH': emisor.codestablemh,
        'codEstable': emisor.codestable,
        'codPuntoVentaMH': emisor.codpuntoventamh,
        'codPuntoVenta': emisor.codpuntoventa,
        'categoria': emisor.categoria,
        'whatsapp': emisor.whatsapp,
        'logo': emisor.company.logo.path,
    }