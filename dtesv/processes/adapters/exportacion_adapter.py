
from decimal import Decimal

from dtesv.processes.utils.diccionario import DiccionarioUtil
import logging

logger = logging.getLogger(__name__)


class ExportacionAdapter:

    @staticmethod
    def aplicar(documentos, dic):

        # dic["identificacion"] = ExportacionAdapter.adaptar_identificacion(documentos, dic["identificacion"]) # En la version 2.0 no es necesario modificar.

        dic["emisor"] = ExportacionAdapter.adaptar_emisor(documentos, dic["emisor"])
        
        dic["receptor"] = ExportacionAdapter.adaptar_receptor(documentos, dic["receptor"])

        dic["cuerpoDocumento"] = ExportacionAdapter.adaptar_cuerpo(dic["cuerpoDocumento"])

        dic["resumen"] = ExportacionAdapter.adaptar_resumen(documentos,dic["resumen"])

        dic = DiccionarioUtil.quitar(dic, [# "compraTercero",   # Este campo es necesario para la version 2.0 
                                           "extension", 
                                           # "documentoRelacionado"   # Este campo es necesario para la version 2.0
                                           ])          

        return dic

    @staticmethod
    def adaptar_identificacion(documentos, identificacion):
        identificacion = DiccionarioUtil.quitar(
            identificacion,
            [
                'motivoContin'
            ]
        )
       
        identificacion["motivoContigencia"] = documentos.motivoContin if documentos.motivoContin else None            # Usar segun CAT-029, los datos se agregan directo en adapter, aplica a: FEXE

        return identificacion

    @staticmethod
    def adaptar_emisor(documentos, emisor):
        # En la version 2.0 Es necesrio quitar estos campos.
        emisor = DiccionarioUtil.quitar(
            emisor,
            [
                "codEstableMH", "codPuntoVentaMH", "tipoEstablecimiento"
            ]
        )

        # Esto solo aplica a este cambio previo a la version 2.0, cuando este este completa se elimina y corrige el builder.
        emisor["direccion"] = {
                    "departamento": documentos.emisor_id.departamento.codigo,
                    "municipio": documentos.emisor_id.munidistrito.codigo, # Modificar
                    "distrito": documentos.emisor_id.municipio.codigo,      # Agregar
                    "complemento": documentos.emisor_id.direccion_complemento
        }
        
        emisor["tipoItemExpor"] = documentos.tipoItemExpor
        emisor["recintoFiscal"] = str(documentos.recintoFiscal.codigo) # Usar segun CAT-027, los datos se agregan directo en adapter, aplica a: FEXE
        emisor["tipoRegimen"] = "EX-1"  # Esta campo es obligatorio para la version 2.0, se debe agregar directamente en el adapter, aplica a: FEXE Usar segun CAT-033, los datos se agregan directo en adapter, aplica a: FEXE
        emisor["regimen"] = documentos.regimen.codigo  # Usar segun CAT-028, los datos se agregan directo en adapter, aplica a: FEXE

        return emisor
    
    @staticmethod
    def adaptar_cuerpo(cuerpo):
        cuerpo = DiccionarioUtil.quitar_lista(
            cuerpo,
            [
                # "numeroDocumento", # Este campo es necesario en la verision 2.0.
                # "codTributo",
                # "tipoItem", # Este campo es necesario en la verision 2.0.
                "ivaItem",
                "psv",
                "ventaExenta",
                "ventaNoSuj",
                "codigoRetencionMH","tipoDte","tipoDoc", "fechaEmision","numDocumento","montoSujetoGrav","ivaRetenido",
                "ivaPerci", "ivaRete", "totalIva", "tipoGeneracion"
            ]
        )

        return cuerpo


    @staticmethod
    def adaptar_receptor(documentos, receptor):
       
        receptor["codPais"] = str(documentos.receptor_id.codpais.codigo_v2)
        receptor["nombrePais"] = documentos.receptor_id.codpais.descripcion
        receptor["tipoPersona"] = int(documentos.receptor_id.tipopersona.codigo)
        receptor["complemento"] = (documentos.receptor_id.complemento)

        receptor = DiccionarioUtil.quitar(
            receptor,
            [
                'codActividad', 'direccion', 'nrc'
            ]
        )
        if documentos.receptor_id.tipodocumento.codigo == "36":
            receptor["numDocumento"] = receptor["numDocumento"].replace("-", "")

        return receptor    


    @staticmethod
    def adaptar_resumen(documentos, resumen):
        resumen = DiccionarioUtil.quitar(
            resumen,
            [
                'descuExenta',
                # 'descuGravada',   # Este campo es requerido en la version 2.0
                'descuNoSuj',
                'ivaRete1',
                'reteRenta',
                # 'saldoFavor',   # Este campo es requerido en la version 2.0
                'subTotal',
                'subTotalVentas',
                'totalExenta',
                'totalIva',
                'totalNoSuj',
                # 'tributos',   # Este campo es requerido en la version 2.0
                'ivaRete', 'totalIvaRetenido', 'totalSujetoRetencion'
            ]
        )
        # resumen = DiccionarioUtil.agregar_si(resumen, 'descuento', documentos.totalDescu)   # Este campo no es necesario para la version 2.0
        resumen = DiccionarioUtil.agregar_si(resumen, 'codIncoterms', documentos.codIncoterms.codigo if documentos.codIncoterms else None)
        resumen = DiccionarioUtil.agregar_si(resumen, 'descIncoterms', documentos.codIncoterms.descripcion if documentos.codIncoterms else None)
        resumen = DiccionarioUtil.agregar_si(resumen, 'observaciones', None)
        resumen = DiccionarioUtil.agregar_si(resumen, 'flete', documentos.flete)
        resumen = DiccionarioUtil.agregar_si(resumen, 'seguro', documentos.seguro)
        resumen["totalNoOnerosas"] = documentos.montoTotalOperacion if documentos.montoTotalOperacion is not None else 0

        return resumen        