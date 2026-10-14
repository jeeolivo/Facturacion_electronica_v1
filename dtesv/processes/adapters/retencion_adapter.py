from dtesv.processes.utils.diccionario import DiccionarioUtil

class RetencionAdapter:

    @staticmethod
    def aplicar(documentos, dic):

        dic["emisor"] = RetencionAdapter.adaptar_emisor(
            documentos,
            dic["emisor"]
        )

        dic["receptor"] = RetencionAdapter.adaptar_receptor(
            dic["receptor"]
        )

        dic["cuerpoDocumento"] = RetencionAdapter.adaptar_cuerpo(
            dic["cuerpoDocumento"]
        )

        dic["resumen"] = RetencionAdapter.adaptar_resumen(
            documentos,
            dic["resumen"]
        )

        dic = DiccionarioUtil.quitar(dic, ["extension", "otrosDocumentos", "ventaTercero", "documentoRelacionado", "compraTercero"]) 

        return dic

    @staticmethod
    def adaptar_emisor(documentos, emisor):
        emisor = DiccionarioUtil.quitar(
            emisor,
            [
                'codEstableMH',
                'codPuntoVentaMH',
                'numDocumento',
                'tipoDocumento',
                'tipoEstablecimiento',
                'direccion' # Esto se debe quitar cuando se haga la version 2.0 del builder, ya que este campo se construye a partir de los campos de direccion del emisor.
            ]
        )

        # Esto solo aplica a este cambio previo a la version 2.0, cuando este este completa se elimina y corrige el builder.
        emisor["direccion"] = {
                    "departamento": documentos.emisor_id.departamento.codigo,
                    "municipio": documentos.emisor_id.munidistrito.codigo, # Modificar
                    "distrito": documentos.emisor_id.municipio.codigo,      # Agregar
                    "complemento": documentos.emisor_id.direccion_complemento
        }        

        return emisor


    @staticmethod
    def adaptar_cuerpo(cuerpo):
        cuerpo = DiccionarioUtil.quitar_lista(
            cuerpo,
            [
                'cantidad', 'codTributo', 'codigo', 'ivaItem', 'montoDescu', 'noGravado', 'numDocumento', 'precioUni',
                #'numeroDocumento', # Este campo se usara a partir del 25-08-2026 de acuerdo a requerimiento de MH
                'psv', 'tipoItem', 'tributos', 'uniMedida', 'ventaExenta', 'ventaGravada', 'ventaNoSuj', 'ivaPerci',
                'tipoDoc', 'ivaRete', 'totalIva'
        ])

        return cuerpo


    @staticmethod
    def adaptar_receptor(receptor):
        receptor = DiccionarioUtil.quitar(
            receptor,
            [
                "codPais",
                "nombrePais",
                "tipoPersona"
            ]
        )

        return receptor    


    @staticmethod
    def adaptar_resumen(documentos, resumen):
        resumen = DiccionarioUtil.quitar(
            resumen,
            [
                'condicionOperacion', 'descuExenta', 'descuGravada', 'descuNoSuj', 'ivaRete1', 'ivaRete', 'montoTotalOperacion', 
                'numPagoElectronico', 'pagos', 'porcentajeDescuento', 'reteRenta', 'saldoFavor', 'subTotal', 
                'subTotalVentas', 'totalDescu', 'totalExenta', 'totalGravada', 'totalNoGravado', 'totalNoSuj', 'totalPagar', 'tributos'
            ]
        )
        return resumen            