from dtesv.processes.builders.receptor_builder import clean_text
from dtesv.processes.utils.diccionario import DiccionarioUtil

class FacturaAdapter:

    @staticmethod
    def aplicar(documentos, dic):
        # En la version 1 no es necesario modificar estos datos
        # dic["emisor"] = FacturaAdapter.adaptar_emisor(
        #     dic["emisor"]
        # )

        dic["receptor"] = FacturaAdapter.adaptar_receptor(
            documentos,
            dic["receptor"]
        )

        dic["cuerpoDocumento"] = FacturaAdapter.adaptar_cuerpo(
            dic["cuerpoDocumento"]
        )

        dic["resumen"] = FacturaAdapter.adaptar_resumen(
            documentos,
            dic["resumen"]
        )

        dic = DiccionarioUtil.quitar(
            dic, ["compraTercero"]  # "extension", es necesario quitarlo para la version 2.0
        )        

        return dic
    

    @staticmethod
    def adaptar_emisor(emisor):

        return DiccionarioUtil.quitar(
            emisor,
            [
                "tipoEstablecimiento",
                "codEstableMH",
                "codPuntoVentaMH"
            ]
        )


    @staticmethod
    def adaptar_receptor(documentos, receptor):
        receptor = DiccionarioUtil.quitar(
            receptor,
            [
                "codPais",
                "nombrePais",
                "tipoPersona",
                "nombreComercial"
            ]
        )
        if documentos.receptor_id.tipodocumento.codigo == "36":
            receptor["numDocumento"] = receptor["numDocumento"].replace("-", "")
        return receptor    


    @staticmethod
    def adaptar_cuerpo(cuerpo):
        cuerpo = DiccionarioUtil.quitar_lista(
            cuerpo,
            [
            "codigoRetencionMH",
            "tipoDte",
            "tipoDoc",
            "fechaEmision",
            "numDocumento",
            "montoSujetoGrav",
            "ivaRetenido", "tipoGeneracion",
            "ivaPerci", "ivaRete", "totalIva"
        ])

        return cuerpo
    
    @staticmethod
    def adaptar_resumen(documentos, resumen):

        resumen["ivaRete1"] = documentos.ivaRete1
        
        resumen = DiccionarioUtil.quitar(
            resumen,
            [
                #"ivaRete1",
                "ivaRete",
                #"reteRenta",
                "totalIvaRetenido", 
                "totalSujetoRetencion",
                "observaciones"     ## En la version 2.0 se permite el campo observaciones en el resumen
            ]
        )

        return resumen