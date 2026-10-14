from decimal import Decimal

from dtesv.models import C015Tributos
from dtesv.processes.builders.receptor_builder import clean_text
from dtesv.processes.utils.diccionario import DiccionarioUtil

class NotaCreditoAdapter:

    @staticmethod
    def aplicar(documentos, dic):

        # dic["identificacion"] = NotaCreditoAdapter.adaptar_identificacion(
        #     documentos,
        #     dic["identificacion"]
        # )
        
        dic["emisor"] = NotaCreditoAdapter.adaptar_emisor(
            documentos,
            dic["emisor"]
        )

        dic["receptor"] = NotaCreditoAdapter.adaptar_receptor(
            documentos,
            dic["receptor"]
        )

        dic["cuerpoDocumento"] = NotaCreditoAdapter.adaptar_cuerpo(
            dic["cuerpoDocumento"]
        )

        dic["resumen"] = NotaCreditoAdapter.adaptar_resumen(
            documentos,
            dic["resumen"]
        )

        # dic = DiccionarioUtil.quitar(dic, ["otrosDocumentos", "extension", "compraTercero"])          
        dic = DiccionarioUtil.quitar(dic, ["otrosDocumentos", "compraTercero"])  # "extension", Colocar en la version 2.0 del schema de MH

        return dic

    @staticmethod
    def adaptar_identificacion(documentos, identificacion):
        # Nuevo campo MH v2.0
        fusion = None
        fusion = getattr(documentos, "nit_fusionado", None)

        # Se agrega el nuevo campor requerido por MH v2.0, El schema de la NCE exige la propiedad aunque no exista una fusión.
        identificacion["fusion"] = fusion if fusion else None

        return identificacion

    @staticmethod
    def adaptar_emisor(documentos, emisor):
        eliminar = [
            "codEstable",
            "codEstableMH",
            "codPuntoVenta",
            "codPuntoVentaMH"
            # "tipoEstablecimiento"
        ]

        return {
            k: v
            for k, v in emisor.items()
            if k not in eliminar
        }    


    @staticmethod
    def adaptar_receptor(documentos, receptor):
        #receptor = DiccionarioUtil.quitar(receptor, ["tipoDocumento"])

        # receptor["numDocumento"] = documentos.receptor_id.numdocumento.replace("-", "")
        #receptor["nombreComercial"] = clean_text(documentos.receptor_id.nombrecomercial)
        
        # Remover tipoDocumento para NCE ya que MH no lo permite
        #receptor["tipoDocumento"] = "36"

        eliminar = [
            "tipoDocumento",
            "numDocumento"
        ]

        receptor = {
            k:v
            for k,v in receptor.items()
            if k not in eliminar
        }        

        receptor["nit"] = documentos.receptor_id.numdocumento.replace("-", "")        

        return receptor
    

    @staticmethod
    def adaptar_cuerpo(cuerpo):
        # eliminar = [
        #     "ivaItem",
        #     "psv",
        #     "codigoRetencionMH",
        #     "tipoDte",
        #     "tipoDoc",
        #     "fechaEmision",
        #     "numDocumento",
        #     "montoSujetoGrav",
        #     "ivaRetenido",
        #     "tipoGeneracion"
        # ]
        eliminar = [
            "ivaItem",
            "psv",
            "codigoRetencionMH",
            "tipoDte",
            "tipoDoc",
            "fechaEmision",
            "numDocumento",
            "montoSujetoGrav",
            "ivaRetenido",
            "tipoGeneracion"
            ,'ivaPerci', 'ivaRete', 'noGravado', 'totalIva'            
        ]

        nuevo = []

        for item in cuerpo:
            registro = {
                k:v
                for k,v in item.items()
                if k not in eliminar
            }

            nuevo.append(registro)
            

        return nuevo

    @staticmethod
    def adaptar_resumen(documentos, resumen):

        # eliminar = [
        #     "descuExenta",
        #     "descuGravada",
        #     "descuNoSuj",
        #     "numPagoElectronico",
        #     "pagos",
        #     "porcentajeDescuento",
        #     "saldoFavor",
        #     "subTotal",
        #     "reteRenta",
        #     "totalIvaRetenido",
        #     "totalSujetoRetencion",
        # ]
        eliminar = [
            #"descuExenta",
            #"descuGravada",
            #"descuNoSuj",
            "numPagoElectronico",
            "pagos",
            "porcentajeDescuento",
            "saldoFavor",
            #"subTotal",
            #"reteRenta",
            "totalIvaRetenido",
            "totalSujetoRetencion",
            "ivaRete", "totalIva", "totalNoGravado", "totalPagar", "observaciones"             # Quitar el usuar version 2.0 del schema de MH
        ]        

        # resumen = {
        #     k:v
        #     for k,v in resumen.items()
        #     if k not in eliminar
        # }

        # # totalIva ya viene calculado y validado desde resumen_builder (única fuente de verdad para esta regla) — no se toca aquí.
        
        # resumen["ivaPerci"] = documentos.ivaPerci1
        # resumen["codigoRetencionMH"] = None

        # tributo_db = C015Tributos.objects.filter(codigo="20").first()

        # resumen["tributos"] = [{
        #     "codigo": tributo_db.codigo,
        #     "descripcion": tributo_db.descripcion,
        #     "valor": documentos.iva
        # }]
        resumen = {
            k:v
            for k,v in resumen.items()
            if k not in eliminar
        }


        resumen["ivaPerci1"] = documentos.ivaPerci1 # Cambiar a ivaPerci en la version 2.0 del schema de MH
        resumen["ivaRete1"] = (
            Decimal(str(documentos.ivaRete1))
            if documentos.ivaRete1 is not None
            else Decimal("0")
        ) # Cambiar a ivaPerci en la version 2.0 del schema de MH
        # resumen["codigoRetencionMH"] = None  # Activar en la version 2.0 del schema de MH

        tributo_db = C015Tributos.objects.filter(codigo="20").first()

        resumen["tributos"] = [{
            "codigo": tributo_db.codigo,
            "descripcion": tributo_db.descripcion,
            "valor": documentos.iva
        }]        

        return resumen    
    