from dtesv.processes.builders.receptor_builder import clean_text
from dtesv.processes.utils.diccionario import DiccionarioUtil

class CreditoFiscalAdapter:

    @staticmethod
    def aplicar(documentos, dic):

        # dic["emisor"] = CreditoFiscalAdapter.adaptar_emisor(
        #     documentos,
        #     dic["emisor"]
        # )

        dic["receptor"] = CreditoFiscalAdapter.adaptar_receptor(
            documentos,
            dic["receptor"]
        )

        dic["cuerpoDocumento"] = CreditoFiscalAdapter.adaptar_cuerpo(
            dic["cuerpoDocumento"]
        )

        dic["resumen"] = CreditoFiscalAdapter.adaptar_resumen(
            documentos,
            dic["resumen"]
        )

        dic = DiccionarioUtil.quitar(
            dic, ["compraTercero"] # "extension", Usar en la version 4.0
        )        

        return dic
    
    @staticmethod
    def adaptar_emisor(documentos, emisor):
        emisor = DiccionarioUtil.quitar(
            emisor,
            [
                "codEstableMH",
                "codPuntoVentaMH",
                "tipoEstablecimiento"
            ]
        )

        return emisor

    @staticmethod
    def adaptar_receptor(documentos, receptor):
        # eliminar = [
        #     "numDocumento",
        #     "tipoDocumento"
        # ]
        # receptor = {
        #     k:v
        #     for k,v in receptor.items()
        #     if k not in eliminar
        # }
        # Esto simplifica la eliminación de las claves "numDocumento" y "tipoDocumento" del diccionario receptor.
        receptor = DiccionarioUtil.quitar(
            receptor,
            [
                "codPais",
                "nombrePais",
                "tipoPersona",
                "numDocumento",
                "tipoDocumento"
            ]
        )

        receptor["nit"] = documentos.receptor_id.numdocumento.replace("-", "")
        receptor["nombreComercial"] = clean_text(documentos.receptor_id.nombrecomercial)

        return receptor
    

    @staticmethod
    def adaptar_cuerpo(cuerpo):
        
        cuerpo = DiccionarioUtil.quitar_lista(
            cuerpo,
            [
                "ivaItem",
                "tipoDte",
                "tipoDoc",
                "fechaEmision",
                "numDocumento",
                "montoSujetoGrav",
                "ivaRetenido", 'ivaPerci', 'ivaRete', 'totalIva','codigoRetencionMH','tipoGeneracion'
            ]
        )

        return cuerpo

    @staticmethod
    def adaptar_resumen(documentos, resumen):

        resumen = DiccionarioUtil.quitar(
            resumen,
            [
                'ivaPerci', 
                'ivaRete',
                #'reteRenta', 
                'totalIva', 'totalSujetoRetencion','totalIvaRetenido'
                ,'observaciones'   # En la version 2.0 se permite el campo observaciones.
            ]
        )

        resumen["ivaPerci1"] = documentos.ivaPerci1
        resumen["ivaRete1"] = documentos.ivaRete1

        tributos = []
        if documentos.codigo_iva:
            tributos.append({
                "codigo": documentos.codigo_iva.codigo,
                "descripcion": documentos.codigo_iva.descripcion,
                "valor": documentos.iva
            })

        resumen["tributos"] = tributos            

        return resumen    
    
