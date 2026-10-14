"""
2026-09-01: Bloque 'identificacion' del diccionario que consume generar_pdf_con_reportlab.
"""

def construir_identificacion(documentos):
    return {
        'version': documentos.tipodocumento.version_work,
        'ambiente': documentos.emisor_id.ambiente_trabajo,
        'tipoDte': documentos.tipodocumento.codigo,
        'numeroControl': documentos.numeroControl,
        'codigoGeneracion': documentos.codigoGeneracion,
        'tipoModelo': int(documentos.tipoModelo.codigo),
        'tipoOperacion': int(documentos.tipoOperacion.codigo),
        'tipoContingencia': documentos.tipoContingencia.codigo if documentos.tipoContingencia else None,
        'motivoContin': documentos.motivoContin if documentos.motivoContin else None,
        'fecEmi': documentos.fecEmi.strftime('%Y-%m-%d'),
        'horEmi': documentos.horEmi.strftime('%H:%M:%S'),
        'tipoMoneda': documentos.tipoMoneda,
        'selloRecibido': documentos.selloRecibido if documentos.selloRecibido else 'NO ENVIADO',
        'condicionOperacion': documentos.condicionOperacion.codigo,
        'nombreDocumento': documentos.tipodocumento.valor,
        'Documento_interno': documentos.num_documento,
        'estado': documentos.estado,
    }