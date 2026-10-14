"""
2026-09-01: Bloque 'receptor' (info_cliente) del diccionario que consume generar_pdf_con_reportlab.

Reglas de origen de los datos (se mantienen tal cual estaban en create_pdf.py,
solo se ordenan y comentan):

  - Datos fiscales (documento, nombre, actividad, país, tipo de persona): receptor_id > proveedor_id.
  - Datos geográficos y de contacto (nombre comercial, ubicación, teléfono, correo): receptor_origen > receptor_id > proveedor_id.
  - Caso especial: si el código de cliente es '16051', los datos no viven en las tablas de Django sino en SQL Server, y se resuelven aparte.
"""

from dtesv.tools.consecutivo_local import ConsecutivosSF


def construir_receptor(documentos):
    receptor_id = documentos.receptor_id
    proveedor_id = documentos.proveedor_id
    receptor_origen = documentos.receptor_origen

    codigo = receptor_id.codigo if receptor_id else proveedor_id.codigo if proveedor_id else None

    if codigo == '16051':
        return ConsecutivosSF.obtener_info_cliente_desde_sqlserver(
            codigo, documentos.emisor_id.id, documentos.num_documento
        )

    return {
        'codigo': codigo,

        # --- Datos fiscales: receptor_id > proveedor_id ---
        'tipoDocumento': (
            receptor_id.tipodocumento.nombre if receptor_id
            else proveedor_id.nombre if proveedor_id
            else None
        ),
        'numDocumento': (
            receptor_id.numdocumento if receptor_id
            else proveedor_id.numdocumento if proveedor_id
            else None
        ),
        'nrc': (
            receptor_id.nrc if receptor_id and receptor_id.nrc
            else proveedor_id.nrc if proveedor_id
            else None
        ),
        'nombre': (
            receptor_id.nombre if receptor_id
            else proveedor_id.nombre if proveedor_id
            else None
        ),
        'codActividad': (
            receptor_id.codactividad.codigo if receptor_id
            else proveedor_id.codactividad.codigo if proveedor_id
            else None
        ),
        'actividad_economica': (
            f"{receptor_id.codactividad.codigo} - {receptor_id.codactividad.nombre}" if receptor_id
            else f"{proveedor_id.codactividad.codigo} - {proveedor_id.codactividad.nombre}" if proveedor_id
            else None
        ),
        'codPais': (
            receptor_id.codpais.codigo if receptor_id
            else proveedor_id.codpais.codigo if proveedor_id
            else None
        ),
        'tipoPersona': (
            receptor_id.tipopersona.codigo if receptor_id
            else proveedor_id.tipopersona.codigo if proveedor_id
            else None
        ),
        'tipoReceptor': (
            receptor_id.tiporeceptor if receptor_id
            else proveedor_id.tiporeceptor if proveedor_id
            else None
        ),
        'vendedor': documentos.vendedor_id,

        # --- Datos geográficos / de contacto: receptor_origen > receptor_id > proveedor_id ---
        'nombreComercial': (
            f"{receptor_origen.codigo} - {receptor_origen.nombrecomercial}" if receptor_origen
            else receptor_id.nombrecomercial if receptor_id
            else proveedor_id.nombrecomercial if proveedor_id
            else None
        ),
        'departamento': (
            receptor_origen.departamento.nombre if receptor_origen
            else receptor_id.departamento.nombre if receptor_id
            else proveedor_id.departamento.nombre if proveedor_id
            else None
        ),
        'distrito': (
            receptor_origen.municipio.nombre if receptor_origen
            else receptor_id.municipio.nombre if receptor_id
            else proveedor_id.municipio.nombre if proveedor_id
            else None
        ),
        'municipio': (
            receptor_origen.munidistrito.nombre if receptor_origen
            else receptor_id.munidistrito.nombre if receptor_id
            else proveedor_id.munidistrito.nombre if proveedor_id
            else None
        ),
        'complemento': (
            receptor_origen.complemento if receptor_origen
            else receptor_id.complemento if receptor_id
            else proveedor_id.complemento if proveedor_id
            else None
        ),
        'telefono': (
            receptor_origen.telefono if receptor_origen
            else receptor_id.telefono if receptor_id
            else proveedor_id.telefono if proveedor_id
            else None
        ),
        'correo': (
            receptor_origen.correo if receptor_origen
            else receptor_id.correo if receptor_id
            else proveedor_id.correo if proveedor_id
            else None
        ),
        'incoterms': documentos.codIncoterms.descripcion if documentos.codIncoterms else None,
        'rutaEntrega': documentos.rutaEntrega,
    }