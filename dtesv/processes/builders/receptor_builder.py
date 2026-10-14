import logging

logger = logging.getLogger(__name__)


def clean_text(value):
    return value.strip() if isinstance(value, str) else value   

def construir_receptor(documentos):
    if documentos.receptor_id and documentos.tipodocumento.codigo not in  ["14","07"]:
        receptor_data = obtener_receptor(documentos)
    else:
        receptor_data = obtener_proveedor(documentos)

    # receptor = DiccionarioUtil.agregar_si(receptor, 'codPais', str(documentos.receptor_id.codpais.codigo))
    # 51 codPais: de acuerdo al CAT-020: Pais Destino para FEXE, Nacionalidad del Donante para CDE
    # receptor = DiccionarioUtil.agregar_si(receptor, 'nombrePais', documentos.receptor_id.codpais.descripcion)
    # 52 nombrePais: nombre del Pais Destino para FEXE
    # 53 codDomicilio: Ingresar codificacion de acuerdo al CAT-032: Domicilio Fiscal, aplica a: CDE y CLE
    # 54 bienTitulo: Segun CAT-025: Aplica a NRE
    # receptor = DiccionarioUtil.agregar_si(receptor, 'tipoPersona', int(documentos.receptor_id.tipopersona.codigo))
    # 55  tipoPersona: Segun CAT-029, clasifica al receptor en Persona Juridica o Persona Natural, aplica a: FEXE
    
    return receptor_data


def obtener_receptor(documentos):

    logger.error(f"Obteniendo datos del receptor para el documento {documentos.tipodocumento.codigo} - {documentos.receptor_id.numdocumento} - {documentos.receptor_id.tipodocumento.codigo}")

    return {
        # 38
        "tipoDocumento": documentos.receptor_id.tipodocumento.codigo,
        # 39
        "numDocumento": # documentos.receptor_id.numdocumento.replace("-", "")
        #             if documentos.receptor_id.tipodocumento.codigo == "36"
        #                 and documentos.tipodocumento.codigo in ("03", "14", "05", "06", "07")
        #             else 
                    documentos.receptor_id.numdocumento,
        # 40 "nit": Se agrega directamente en los adapter correspondiente CCFE, DCLE
        # 41
        "nrc": documentos.receptor_id.nrc
                    if documentos.receptor_id.nrc and (documentos.tipodocumento.codigo == "03" or 
                                                       documentos.tipodocumento.codigo == "05" or 
                                                       documentos.tipodocumento.codigo == "06" or 
                                                       documentos.tipodocumento.codigo == "07")
                    else None,
        # 42
        "nombre": clean_text(documentos.receptor_id.nombre),
        # 45
        "nombreComercial": clean_text(documentos.receptor_id.nombrecomercial),
        # 43 
        "codActividad": documentos.receptor_id.codactividad.codigo,
        # 44
        "descActividad": documentos.receptor_id.codactividad.nombre,
        # 46 "tipoEstablecimiento": Se agrega en el adapter correspondiente DLCE
        "direccion": {  # En el caso de las FE es opcional segun la normativa
                    # 47
                    "departamento": documentos.receptor_id.departamento.codigo,
                    # 48
                    "municipio": documentos.receptor_id.municipio.codigo, # documentos.receptor_id.munidistrito.codigo,
                    # 49
                    # "distrito": documentos.receptor_id.municipio.codigo,
                    # 50
                    "complemento": clean_text(documentos.receptor_id.complemento),
            },
        # 56
        "telefono": clean_text(documentos.receptor_id.telefono),
        # 57
        "correo": clean_text(documentos.receptor_id.correo)
    }


def obtener_proveedor(documentos):
    if not documentos.proveedor_id:
        raise ValueError(
            f"El documento {documentos.codigoGeneracion} (tipo {documentos.tipodocumento.codigo}) "
            f"no tiene proveedor_id asignado."
        )
        
    return {
            "tipoDocumento": documentos.proveedor_id.tipodocumento.codigo,
            "numDocumento": documentos.proveedor_id.numdocumento.replace("-", "") 
                if "-" in documentos.proveedor_id.numdocumento and documentos.proveedor_id.tipodocumento.codigo != "13"
                else documentos.proveedor_id.numdocumento,
            "nrc": documentos.proveedor_id.nrc
                if documentos.proveedor_id.nrc
                else None,
            "nombre": clean_text(documentos.proveedor_id.nombre),
            "nombreComercial": clean_text(documentos.proveedor_id.nombrecomercial),
            "codActividad": documentos.proveedor_id.codactividad.codigo,
            "descActividad": documentos.proveedor_id.codactividad.nombre,
            "direccion": {
                "departamento": documentos.proveedor_id.departamento.codigo,
                "municipio": documentos.proveedor_id.munidistrito.codigo, # documentos.proveedor_id.municipio.codigo, #
                "distrito": documentos.proveedor_id.municipio.codigo,
                "complemento": clean_text(documentos.proveedor_id.complemento),
                },
            "telefono": clean_text(documentos.proveedor_id.telefono),
            "correo": clean_text(documentos.proveedor_id.correo),
        }      