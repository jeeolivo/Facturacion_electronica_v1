from dtesv.models import C015Tributos
from dtesv.processes.builders.receptor_builder import clean_text
from dtesv.processes.utils.diccionario import DiccionarioUtil

class EventoRetornoAdapter:

    @staticmethod
    def aplicar(documentos, dic):

        dic["identificacion"] = EventoRetornoAdapter.adaptar_identificacion(
            documentos,
            dic["identificacion"]
        )

        dic["emisor"] = EventoRetornoAdapter.adaptar_emisor(
            documentos,
            dic["emisor"]
        )

        dic["documento"] = EventoRetornoAdapter.adaptar_documento(
            documentos,
            dic["receptor"]
        )

        dic["resumen"] = EventoRetornoAdapter.adaptar_resumen(
            documentos,
            dic["resumen"],
            dic.get("documentoRelacionado")
        )
        # El Evento de Retorno no utiliza estos objetos
        dic = DiccionarioUtil.quitar(dic, ["receptor","extension", "otrosDocumentos"])          

        return dic

    @staticmethod
    def adaptar_identificacion(documentos, identificacion):
        # Nuevo campo MH v2.0
        fusion = None
        fusion = getattr(documentos, "nit_fusionado", None)

        # Se agrega el nuevo campor requerido por MH v2.0, El schema de la NCE exige la propiedad aunque no exista una fusión.
        identificacion["fusion"] = fusion if fusion else None
        identificacion["tipoEvento"] = identificacion["tipoDte"]

        return identificacion


    @staticmethod
    def adaptar_emisor(documentos, emisor):
        eliminar = [
            "nrc",
            "codActividad",
            "descActividad",
            "nombreComercial",
            "direccion",
            "telefono",
            "correo",
            "tipoEstablecimiento"
        ]

        emisor = {
            k: v
            for k, v in emisor.items()
            if k not in eliminar
        }    

        # if documentos.documento_relacionado.tipoDte.codigo in ["01", "11"]:
            # 34
        emisor["tipoItemExpor"] = None
            # 35
        emisor["recintoFiscal"] = None
            # 36
        emisor["tipoRegimen"] = None
            # 37
        emisor["regimen"] = None
        # else:
        #     # 34
        #     tipo_item_export = getattr(documentos.emisor_id, "tipoItemExpor", None)
        #     emisor["tipoItemExpor"] = (int(tipo_item_export.codigo) if tipo_item_export and tipo_item_export.codigo is not None else None)
        #     # 35
        #     recinto_fiscal = getattr(documentos.emisor_id, "recintoFiscal", None)        
        #     emisor["recintoFiscal"] = (recinto_fiscal.codigo if recinto_fiscal else None)
        #     # 36
        #     tipo_regimen = getattr(documentos.emisor_id,"tipoRegimen",None)
        #     emisor["tipoRegimen"] = getattr(tipo_regimen,"codigo",None)
        #     # 37
        #     regimen = getattr(documentos.emisor_id, "regimen", None)        
        #     emisor["regimen"] = (regimen.codigo if regimen else None)            

        return emisor

    @staticmethod
    def adaptar_documento(documentos, receptor):
        eliminar = [
            "nrc",
            "nombreComercial",
            "codActividad",
            "descActividad",
            "direccion"]
        receptor = {
            k:v
            for k,v in receptor.items()
            if k not in eliminar
        }
        receptor["numDocumento"] = documentos.receptor_id.numdocumento.replace("-", "")
        # 51 codPais: de acuerdo al CAT-020: Pais Destino para FEXE, Nacionalidad del Donante para CDE
        # codpais = getattr(documentos.receptor_id, "codpais", None)
        # receptor["codPais"] = (str(codpais.codigo) if codpais and codpais.codigo is not None else None)
        receptor["codPais"] = None
        # 52 nombrePais: nombre del Pais Destino para FEXE
        # receptor["nombrePais"] = (codpais.descripcion if codpais and codpais.descripcion is not None else None)
        receptor["nombrePais"] = None
        # 53 codDomicilio: Ingresar codificacion de acuerdo al CAT-032: Domicilio Fiscal, aplica a: CDE y CLE
        # receptor = DiccionarioUtil.agregar_si(receptor, 'codDomicilio', str(documentos.receptor_id.codDomicilio), None)
        # 55  tipoPersona: Segun CAT-029, clasifica al receptor en Persona Juridica o Persona Natural, aplica a: FEXE
        #receptor = DiccionarioUtil.agregar_si(receptor, 'tipoPersona', int(documentos.receptor_id.tipopersona.codigo))

        return receptor
    

    @staticmethod
    def adaptar_resumen(documentos, resumen, documento_relacionado):

        eliminar = [
            "descuExenta",
            "descuGravada",
            "descuNoSuj",
            "numPagoElectronico",
            "pagos",
            "porcentajeDescuento",
            "subTotal",
            "condicionOperacion",
            "totalDescu",
            "totalIvaRetenido",
            "totalSujetoRetencion",
            "totalCompraExcluidos",         
        ]

        resumen = {
            k:v
            for k,v in resumen.items()
            if k not in eliminar
        }

        tipo_dte_relacionado = None

        if isinstance(documento_relacionado, list) and documento_relacionado:
            tipo_dte_relacionado = documento_relacionado[0].get("tipoDocumento")

        elif isinstance(documento_relacionado, dict):
            tipo_dte_relacionado = documento_relacionado.get("tipoDocumento")

        if tipo_dte_relacionado in ("01", "14"):

            resumen["tributos"] = None
        else:
            tributo_db = C015Tributos.objects.filter(codigo="20").first()
            resumen["tributos"] = [{
                "codigo": tributo_db.codigo,
                "descripcion": tributo_db.descripcion,
                "valor": documentos.iva
            }]

        resumen["totalCompraExcluidos"] = 0.00
        resumen["totalSeguro"] = None
        resumen["totalFlete"] = None
        resumen["totalNoOnerosas"] = 0.00

        return resumen    
    