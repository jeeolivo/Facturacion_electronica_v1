import re
from decimal import Decimal
from dtesv.processes.utils.diccionario import DiccionarioUtil

# Campos permitidos por fe-fse-v1.json
CAMPOS_EMISOR = ["nit", "nrc", "nombre", "codActividad", "descActividad",
                 "direccion", "telefono", "codEstable",
                 "codPuntoVenta", "correo"]
                # "codEstableMH", "codPuntoVentaMH",  # Estas no se usan en el schema FSE, version 2.0
CAMPOS_RECEPTOR = ["tipoDocumento", "numDocumento", "nombre", "codActividad",
                   "descActividad", "direccion", "telefono", "correo"]
CAMPOS_CUERPO = ["numItem", "tipoItem", "cantidad", "codigo", "uniMedida",
                 "descripcion", "precioUni", "montoDescu", "compra"]
CAMPOS_RESUMEN = ["totalCompra", "descu", "totalDescu", "subTotal",
                  "reteRenta", "totalPagar", "totalLetras", "condicionOperacion",
                  "pagos", "observaciones"]
                # "ivaRete1",   # Estas no se usan en el schema FSE, version 2.0


class SujetoExcluidoAdapter:

    @staticmethod
    def aplicar(documentos, dic):
        # El schema FSE usa "sujetoExcluido" en lugar de "receptor"
        receptor = dic.pop("receptor", None)
        dic["emisor"] = SujetoExcluidoAdapter.adaptar_emisor(documentos, dic["emisor"]) # DiccionarioUtil.conservar(dic["emisor"], CAMPOS_EMISOR)
        dic["receptor"] = SujetoExcluidoAdapter.adaptar_receptor(documentos, receptor)
        dic["cuerpoDocumento"] = SujetoExcluidoAdapter.adaptar_cuerpo(documentos, dic["cuerpoDocumento"])
        dic["resumen"] = SujetoExcluidoAdapter.adaptar_resumen(documentos, dic["resumen"])

        # Bloques que el schema FSE no admite
        dic = DiccionarioUtil.quitar(dic, [
            "compraTercero", "ventaTercero", "documentoRelacionado",
            "otrosDocumentos", "extension",
        ])
        return dic

    @staticmethod
    def adaptar_emisor(documentos, emisor):
        # En la version 2.0 Es necesrio quitar estos campos.
        # emisor = DiccionarioUtil.quitar(
        #     emisor,
        #     [
        #         "codEstableMH", "codPuntoVentaMH", "tipoEstablecimiento"
        #     ]
        # )
        emisor = {k: emisor.get(k) for k in CAMPOS_EMISOR}

        # Esto solo aplica a este cambio previo a la version 2.0, cuando este este completa se elimina y corrige el builder.
        emisor["direccion"] = {
                    "departamento": documentos.emisor_id.departamento.codigo,
                    "municipio": documentos.emisor_id.munidistrito.codigo, # Modificar
                    "distrito": documentos.emisor_id.municipio.codigo,      # Agregar
                    "complemento": documentos.emisor_id.direccion_complemento
        }       

        return emisor


    @staticmethod
    def adaptar_receptor(documentos, receptor):
        if not receptor:
            raise ValueError(
                f"Sujeto excluido {documentos.codigoGeneracion}: no se pudo construir el receptor "
                f"(¿proveedor_id vacío?)."
            )
        # Lista blanca: elimina nrc, nombreComercial, codPais, etc.
        receptor = {k: receptor.get(k) for k in CAMPOS_RECEPTOR}

        # El sujeto excluido es un proveedor, no un receptor
        # NIT (36) y DUI (13): el schema FSE exige solo dígitos, sin guiones ni espacios
        if receptor["tipoDocumento"] in ("36", "13") and receptor["numDocumento"]:
            receptor["numDocumento"] = re.sub(r"\D", "", receptor["numDocumento"])
        return receptor

    @staticmethod
    def adaptar_cuerpo(documentos, cuerpo):
        nuevo_cuerpo = []
        for item in cuerpo:
            cantidad = Decimal(str(item.get("cantidad") or 0))
            precio = Decimal(str(item.get("precioUni") or 0))
            descuento = Decimal(str(item.get("montoDescu") or 0))

            nuevo = {k: item.get(k) for k in CAMPOS_CUERPO if k != "compra"}
            # compra = cantidad * precioUni - montoDescu (por ítem)
            nuevo["compra"] = float(round(cantidad * precio - descuento, 8))
            nuevo_cuerpo.append(nuevo)
        return nuevo_cuerpo

    @staticmethod
    def adaptar_resumen(documentos, resumen):
        resumen["ivaRete1"] = documentos.ivaRete1 or 0
        resumen["reteRenta"] = documentos.reteRenta or 0
        resumen["totalCompra"] = documentos.totalSujetoRetenido or 0
        resumen["subTotal"] = documentos.totalSujetoRetenido or 0
        resumen['descu'] =  resumen['totalDescu']
        resumen['observaciones'] = None
        
        # Ajuste necesario en version 2.0, el campo pagos es obligatorio y depende de la condicionOperacion
        condicion = resumen.get("condicionOperacion")
        if condicion in (1, 3):
            # Contado u otra: monto con 2 decimales = totalPagar
            resumen["pagos"] = [{
                "codigo": "05",          # CAT-017; ajustar a la forma de pago real
                "montoPago": round(float(documentos.totalSujetoRetenido), 2),
                "referencia": None,
                "plazo": None,
                "periodo": None,
            }]
        elif condicion == 2:
            resumen["pagos"] = [{
                "codigo": "05",
                "montoPago": 0.00,
                "referencia": None,
                "plazo": "01",           # CAT-018: ajustar
                "periodo": 30,           # ajustar
            }]
        else:
            resumen["pagos"] = None        

        return {
            k: resumen.get(k)
            for k in CAMPOS_RESUMEN
        }
