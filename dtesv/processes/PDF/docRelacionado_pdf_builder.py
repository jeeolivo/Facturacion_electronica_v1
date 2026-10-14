"""
2026-09-01: Bloque 'documentoRelacionado' del diccionario que consume generar_pdf_con_reportlab.
"""

from dtesv.models import Documentos


def construir_documento_relacionado(documentos):
    if not documentos.numeroDocumento_rel_guid:
        return {}

    documento_rel = Documentos.objects.filter(codigoGeneracion=documentos.numeroDocumento_rel_guid).first()

    # Nota: se agrega esta validación porque el código original asumía que `documento_rel` siempre existía si `numeroDocumento_rel_guid` estaba
    # presente; si el registro relacionado ya no existe, evita un AttributeError y simplemente no muestra el bloque.
    if not documento_rel:
        return {}

    return {
        'codigoGeneracion': documento_rel.codigoGeneracion,
        'numeroControl': documento_rel.numeroControl,
        'fecEmi': documento_rel.fecEmi,
    }