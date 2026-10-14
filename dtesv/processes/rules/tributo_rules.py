from decimal import Decimal, ROUND_HALF_UP


class TributoRuleError(Exception):
    """
    Excepción de negocio para reglas de tributos/resumen que no deben llegar a certificarse silenciosamente. El adapter/vista que llama
    a estas funciones debe capturarla y mostrar el mensaje al usuario ANTES de intentar el envío a MH.
    """
    pass
 
# Códigos de tributo por defecto según CAT-015, ajustar si tu catálogo interno usa otros valores para estos conceptos.
COD_TRIBUTO_IVA = "20"
 
# tipoDte donde el ítem requiere codTributo (singular) cuando tipoItem == 4
TIPOS_DTE_CON_COD_TRIBUTO = ("03", "05", "06")
 
# tipoDte donde el campo tributos (array) es obligatorio a nivel de ítem cuando el ítem tiene ventaGravada > 0 (CCF, NC, ND)
TIPOS_DTE_CON_TRIBUTOS_ARRAY = ("03", "05", "06")
 
# tipoDte donde totalIva a nivel de ítem debe reportarse (según comentario original del adapter: "Requerido en NCE y NDE"). 
# Ajustar aquí si se confirma que CCF (03) también lo exige a nivel de ítem.
TIPOS_DTE_CON_TOTAL_IVA_ITEM = ("05", "06")


def obtener_cod_tributo(detalle, tipo_dte):
    """
    Determina el valor de codTributo (campo singular, #84) según las reglas oficiales del MH. Aplica únicamente cuando tipoItem == 4
    (CAT-011), y solo para los tipos de documento donde este campo tiene sentido (CCF, NC, ND).
    """

    if int(detalle.tipoItem) != 4:
        return None
 
    if tipo_dte in TIPOS_DTE_CON_COD_TRIBUTO:
        # Prioriza el dato real capturado en el detalle; solo cae al default de IVA si no hay un codTributo explícito asignado.
        # Esto evita etiquetar como "20" (IVA) ítems que en realidad correspondan a otro tributo (turismo, FOVIAL, COTRANS, etc.).
        return (
            detalle.codTributo.codigo
            if detalle.codTributo
            else COD_TRIBUTO_IVA
        )
 
    if tipo_dte in ("01", "11"):
        return None
 
    return (
        detalle.codTributo.codigo
        if detalle.codTributo
        else None
    )


def obtener_tributos_detalle(detalle, tipo_dte):
    """
    Determina el valor de cuerpoDocumento[].tributos (campo #96, array).
 
    Este campo es distinto de codTributo (singular, #84): aquí se listan los códigos de tributo aplicables al ítem según CAT-015,
    secciones 1 y 3. Para CCF/NC/ND, MH exige que este array venga poblado cuando el ítem tiene ventaGravada > 0; dejarlo en null
    provoca rechazo ("[cuerpoDocumento.item.N] DEBE PROPORCIONAR UN VALOR").
 
    Ajusta el nombre de la relación (`detalle.tributos_adicionales`) al campo real de tu modelo si manejas tributos adicionales (turismo,
    FOVIAL, COTRANS) por ítem; si no existe tal relación en tu esquema actual, esta función seguirá funcionando devolviendo solo IVA.
    """
 
    if tipo_dte not in TIPOS_DTE_CON_TRIBUTOS_ARRAY:
        return None
 
    venta_gravada = detalle.ventaGravada or Decimal("0.00")
    if venta_gravada <= Decimal("0.00"):
        return None
 
    codigos = [COD_TRIBUTO_IVA]
 
    # Si el modelo tiene una relación con tributos adicionales por ítem (p. ej. M2M), se agregan aquí sin duplicar el código de IVA.
    tributos_adicionales = getattr(detalle, "tributos_adicionales", None)
    if tributos_adicionales is not None:
        try:
            for tributo in tributos_adicionales.all():
                codigo = getattr(tributo, "codigo", None)
                if codigo and codigo not in codigos:
                    codigos.append(codigo)
        except AttributeError:
            # tributos_adicionales no es un manager M2M; se ignora de forma segura en vez de romper la certificación.
            pass
 
    return codigos


def obtener_campos_iva_detalle(detalle, tipo_dte):
    """
    Determina los campos relacionados con IVA que irán en cuerpoDocumento.
 
    totalIva a nivel de ítem sigue la misma restricción que codTributo (CAT-011): MH solo permite valor en este campo cuando tipoItem == 4
    ("Otros tributos, exceptuando el IVA"). Para ítems normales (tipoItem 1, el caso típico de venta gravada con IVA estándar), el IVA del ítem ya viaja implícito en ventaGravada/precioUni,
    y MH rechaza (VALOR NO ES PERMITIDO) si aquí se informa el monto de IVA calculado — debe ir 0.00.
    """

    iva_item = detalle.ivaItem or Decimal("0.00")
 
    total_iva = Decimal("0.00")

    if tipo_dte in TIPOS_DTE_CON_TOTAL_IVA_ITEM and int(detalle.tipoItem) == 4:
        total_iva = iva_item
 
    return {
        "ivaItem": iva_item,
        "totalIva": total_iva,
        "ivaPerci": getattr(detalle, "ivaPerci", None) or Decimal("0.00"),
        "ivaRete": getattr(detalle, "ivaRete", None) or Decimal("0.00") # detalle.ivaRete or Decimal("0.00"),
    }


def obtener_total_iva_resumen(documentos, detalles, tipo_dte, tipo_doc_relacionado=None):
    """
    Determina el valor de resumen.totalIva según las reglas del MH.
 
    NCE / NDE: 0.00 (Cuando se emite una Nota de Crédito o Nota de Débito para relacionar o ajustar un Comprobante de Crédito Fiscal,
               este campo debe ingresar 0.00). Esta regla asume que el documento relacionado es un CCF (tipoDte 03); si el
               documento relacionado es una Factura de Consumidor (tipoDte 01), esa operación NO es válida y se detiene el
               proceso con TributoRuleError.
    FE: Valor informativo proveniente del documento.
    CRE: 0.00 para retenciones normales. Para ajustes a personas excluidas de IVA (C4), ingresa el 13% de la retención de IVA.
    Otros documentos: 0.00
    """
    total_iva = Decimal("0.00")
 
    if tipo_dte in ("05", "06"):
        if tipo_doc_relacionado is None:
            # No se puede validar sin el dato: quien llama debe resolver esto ANTES de certificar. No se asume "0.00" a ciegas para
            # no enmascarar el caso de una relación inválida.
            raise TributoRuleError(
                "No se pudo determinar el tipo de documento relacionado para validar la Nota de Crédito/Débito. Verifique que "
                "el documento relacionado exista y esté correctamente vinculado antes de certificar."
            )
 
        if tipo_doc_relacionado == "01":
            raise TributoRuleError(
                f"No es posible emitir una Nota de "
                f"{'Crédito' if tipo_dte == '05' else 'Débito'} "
                f"relacionando una Factura de Consumidor (tipoDte 01). "
                f"Las NCE/NDE solo pueden relacionar un Comprobante de "
                f"Crédito Fiscal (tipoDte 03). Verifique el documento "
                f"relacionado antes de continuar."
            )
 
        # Regla MH: NCE y NDE que relacionan un CCF siempre deben tener totalIva = 0.00
        total_iva = Decimal("0.00")
 
    elif tipo_dte in ("01", "18"):
        # FE: valor informativo del documento
        total_iva = documentos.iva or Decimal("0.00")
 
    elif tipo_dte == "07":
        # CRE: 0.00 normalmente, excepto en ajuste a código C4 (excluido de IVA). En ese caso se ingresa el 13% de la retención de IVA.
        tiene_c4 = any(
            getattr(detalle, "codigoRetencionMH", None)
            and getattr(detalle.codigoRetencionMH, "codigo", None) == "C4"
            for detalle in detalles
        )
 
        if tiene_c4:
            iva_retenido = documentos.totalIVAretenido or Decimal("0.00")
            total_iva = (iva_retenido * Decimal("0.13")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            total_iva = Decimal("0.00")
 
    return total_iva.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

# def obtener_total_iva_resumen(documentos, detalles, tipo_dte):

#     """
#     Determina el valor de resumen.totalIva según las reglas del MH.

#     NCE / NDE: 0.00 (Cuando se emite una Nota de Crédito o Nota de Débito para 
#                relacionar o ajustar un Comprobante de Crédito Fiscal, 
#                este campo debe ingresar 0.00)
#     FE: Valor informativo proveniente del documento.
#     CRE: 0.00 para retenciones normales. Para ajustes a personas excluidas de IVA (C4),
#          ingresa el 13% de la retención de IVA.
#     Otros documentos: 0.00
#     """
#     total_iva = Decimal("0.00")

#     # Según regla MH: NCE y NDE siempre deben tener totalIva = 0.00
#     if tipo_dte in ("05", "06"):
#         total_iva = Decimal("0.00")

#     # FE: valor informativo del documento
#     elif tipo_dte in ("01", "18"):
#         total_iva = documentos.iva or Decimal("0.00")

#     # CRE: 0.00 normalmente, excepto en ajuste a código C4 (excluido de IVA)
#     # En ese caso se ingresa el 13% de la retención de IVA
#     elif tipo_dte == "07":
#         # Verificar si hay algún detalle con código de retención C4 (excluido de IVA)
#         tiene_c4 = any(
#             getattr(detalle, 'codigoRetencionMH', None) and 
#             getattr(detalle.codigoRetencionMH, 'codigo', None) == 'C4'
#             for detalle in detalles
#         )
        
#         if tiene_c4:
#             # Ingresar el 13% de la retención de IVA total del documento
#             iva_retenido = documentos.totalIVAretenido or Decimal("0.00")
#             total_iva = (iva_retenido * Decimal("0.13")).quantize(
#                 Decimal("0.01"),
#                 rounding=ROUND_HALF_UP
#             )
#         else:
#             total_iva = Decimal("0.00")

#     return total_iva.quantize(
#         Decimal("0.01"),
#         rounding=ROUND_HALF_UP
#     )

