from decimal import Decimal
from datetime import datetime
## -- Agregado para pruebas 2025-04-07
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import io

import sys
import os
import math
import locale
from dtesv.tools.consecutivo_local import ConsecutivosSF
from dtesv.models import Documentos ,DocumentosDetalle,ExtencionEntrega,DocumentosAsociados,Pagos
from django.http import FileResponse, HttpResponse

import logging
import traceback
logger = logging.getLogger(__name__)


current_directory = os.path.dirname(os.path.abspath(__file__))
directorio_actual = os.getcwd()
mymodule_dir = os.path.join(directorio_actual, 'Facturacion_electronica\\dtesv')
image_dir = os.path.join(mymodule_dir, 'static\img')

from pathlib import Path
import random

#locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )
locale.setlocale(locale.LC_ALL, 'es_SV.UTF-8')

class ger_pdf():
    def __init__(self, args):
        self.args = args 

## -- Agregado para pruebas 2025-04-07        
    def dibujar_pie_pagina(self, p, num_pagina, total_paginas):
        width, height = letter
        p.setFont("Helvetica", 6)
        p.drawCentredString(width / 2, 15, f"Página {num_pagina} de {total_paginas}")


    def dibujar_encabezado(self, p, data):
        # Definiendo las medidas del Papel a Usar
        width, height = letter
        margin = 5 * mm
        y = height - margin
        # logger.error(f"Configuracion de papel, Ancho: {width}, Alto: {height}")

        # Cargando los datos a variables para facilitar su uso
        identificacion = data['identificacion']
        emisor = data['emisor']
        receptor = data['receptor']
        docRelacionado = data['documentoRelacionado']

        tipoDte = identificacion['tipoDte']
        codigo_generacion = identificacion['codigoGeneracion']
        fecha_emision = identificacion['fecEmi']
        nombreDocumento = identificacion['nombreDocumento']
        mod = {1: 'Previo', 2: 'Diferido'}
        modelo = mod.get(identificacion['tipoModelo'])
        tip_t = {None: 'Normal', 1: 'Contingencia'}
        Tipo_transmision = tip_t.get(identificacion['tipoContingencia'])
        cond_map = {1: 'Contado', 2: 'Credito'}
        condicion = cond_map.get(identificacion.get('condicionOperacion'), 'Otro')
        Documento_interno = identificacion.get('Documento_interno')
        direccion_completa = emisor.get('direccion_complemento', '')
        direccion = receptor.get('complemento', '')
        oCompra = data['apendice']['valor'] if data.get('apendice') and 'valor' in data['apendice'] else ""


        docRelCodigoGeneracion = docRelacionado.get('codigoGeneracion') if docRelacionado else ''
        numeroControl = docRelacionado.get('numeroControl') if docRelacionado else ''
        if docRelacionado:
            try:
                fecha_obj = datetime.strptime(str(docRelacionado.get('fecEmi')), '%Y-%m-%d')
                docRelFecha_emision = fecha_obj.strftime('%d-%m-%Y')
            except ValueError:
                docRelFecha_emision = ''
        else:
            docRelFecha_emision = ''

        #logger.error (f"Se pasan los siguientes datos: documento Relacionado {docRelCodigoGeneracion}, numeroControl {numeroControl}, fecha {docRelFecha_emision}")
        # Logo
        logo_path = emisor['logo']
        p.drawImage(logo_path, margin, y - 90, width=90, height=80, mask='auto')

        # Datos del emisor
        y -= 10
        value_x = margin + 126
        p.setFont("Helvetica-Bold", 8)
        p.drawString(value_x, y, f"{emisor['nombreComercial']}")
        y -= 9
        p.setFont("Helvetica", 6)
        p.drawString(value_x, y, f"{emisor['descActividad']}")
        y -= 9

        if len(direccion_completa) > 54:
            direccion_field = [("Dirección:", direccion_completa[:54]), ("", direccion_completa[54:])]
        else:
            direccion_field = [("Dirección:", direccion_completa)]

        emisor_data = direccion_field + [
            ("Teléfono:", f"{emisor['telefono']} / WhatsApp: +503 {emisor['whatsapp']}"),
            ("Correo:", emisor['correo']),
            ("Categoría:", emisor['categoria']),
            ("Tipo Estab.:", "Casa Matriz"),
            ("NIT:", emisor['nit']),
            ("NRC:", emisor['nrc']),
        ]

        label_x = margin + 94
        for i, (label, value) in enumerate(emisor_data):
            row_y = y - 9 * i
            p.setFont("Helvetica", 6)
            p.drawString(label_x, row_y, label)
            p.drawString(value_x, row_y, value)


        # Recuadro identificación DTE
        box_x = margin + 275
        box_y = height - margin - 90
        box_width = 310
        box_height = 95
        p.setLineWidth(0.5)
        p.rect(box_x, box_y, box_width, box_height)

        center_x = box_x + (box_width / 2)
        y_id = height - margin - 5

        p.setFont("Helvetica-Bold", 8)
        p.drawCentredString(center_x, y_id, "DOCUMENTO TRIBUTARIO ELECTRÓNICO")
        p.setFont("Helvetica-Bold", 8)
        p.drawCentredString(center_x, y_id - 10, identificacion['nombreDocumento'].upper())

        label_x = box_x + 5
        value_x = box_x + 75
        y = y_id - 30

        p.setFont("Helvetica-Bold", 7)
        p.drawString(label_x, y, "Código Generación:")
        p.setFont("Helvetica", 7)
        p.drawString(value_x, y, f"{identificacion['codigoGeneracion']}")
        y -= 10

        p.setFont("Helvetica-Bold", 7)
        p.drawString(label_x, y, "Sello de Recepción:")
        p.setFont("Helvetica", 7)
        p.drawString(value_x, y, f"{identificacion['selloRecibido']}")
        y -= 10

        p.setFont("Helvetica-Bold", 7)
        p.drawString(label_x, y, "Número de Control:")
        p.setFont("Helvetica", 7)
        p.drawString(value_x, y, f"{identificacion['numeroControl']}")
        y -= 10

        col1_x = box_x + 5
        col2_x = box_x + 75
        col3_x = box_x + 205
        col4_x = box_x + 270

        p.setFont("Helvetica-Bold", 7)
        p.drawString(col1_x, y, "Modelo facturación:")
        p.drawString(col3_x, y, "Versión del JSON:")
        p.setFont("Helvetica", 7)
        p.drawString(col2_x, y, f"{modelo}")
        p.drawString(col4_x, y, f"{identificacion['version']}")
        y -= 10

        p.setFont("Helvetica-Bold", 7)
        p.drawString(col1_x, y, "Tipo Transmisión:")
        p.drawString(col3_x, y, "Fecha emisión:")
        p.setFont("Helvetica", 7)
        p.drawString(col2_x, y, f"{Tipo_transmision}")
        p.drawString(col4_x, y, f"{identificacion['fecEmi']}")
        y -= 10

        p.setFont("Helvetica-Bold", 7)
        p.drawString(col1_x, y, "Documento Interno:")
        p.drawString(col3_x, y, "Hora de Emisión:")
        p.setFont("Helvetica", 7)
        p.drawString(col2_x, y, f"{Documento_interno}")
        p.drawString(col4_x, y, f"{identificacion['horEmi']}")
        y -= 12
        ## Control para la versión del formato
        p.setFont("Helvetica", 5)
        p.drawString(col4_x, y, f"RG.J01")
        
        # ========= DATOS DEL QR ================
        # Generar el código QR
        urlval1 = f'https://admin.factura.gob.sv/consultaPublica?ambiente=01&codGen={codigo_generacion}&fechaEmi={fecha_emision}'
        urlval2 = f'http://192.168.1.53:8000/dtesv/descargar/{codigo_generacion}/'
        qr_code = qr.QrCodeWidget(urlval1)

        # Definir dimensiones
        qr_width = 50
        qr_height = 50
        bounds = qr_code.getBounds()
        scale_x = qr_width / (bounds[2] - bounds[0])
        scale_y = qr_height / (bounds[3] - bounds[1])

        # Insertar QR en Drawing
        d = Drawing(qr_width, qr_height, transform=[scale_x, 0, 0, scale_y, 0, 0])
        d.add(qr_code)

        # Dibujar el QR en el canvas, junto al label "Categoría"
        renderPDF.draw(d, p, value_x-140, row_y-50)
        p.setFont("Helvetica", 5)
        p.drawString(value_x-148,row_y-51, "Portal Ministerio de Hacienda")

        #y -= 5 

        qr_download = qr.QrCodeWidget(urlval2)

        # Definir dimensiones
        qr_width = 50
        qr_height = 50
        bounds = qr_download.getBounds()
        scale_x = qr_width / (bounds[2] - bounds[0])
        scale_y = qr_height / (bounds[3] - bounds[1])

        # Insertar QR en Drawing
        d = Drawing(qr_width, qr_height, transform=[scale_x, 0, 0, scale_y, 0, 0])
        d.add(qr_download)

        # Dibujar el QR en el canvas, junto al label "Categoría"
        renderPDF.draw(d, p, value_x-40, row_y-50)
        p.setFont("Helvetica", 5)
        p.drawString(value_x-37,row_y-51, "Descargar Archivos")

        y -= 60   


        # ========== DATOS DEL CLIENTE ========== 
        # Precalcular altura total del bloque
        line_height = 10
        num_lines = 8  # Ajusta si agregas más líneas dinámicas
        extra_lines = 1 if len(direccion) > 60 else 0
        box_height = (num_lines + extra_lines + 1) * line_height + 10

        # Dibujar recuadro antes de pintar texto
        box_top_y = y
        box_bottom_y = y - box_height
        p.setStrokeColor(colors.black)
        p.rect(margin, box_bottom_y, width - 2 * margin, box_height, stroke=1, fill=0)

        y -= 10

        # Coordenadas base para columnas
        col1_x = margin + 5
        col2_x = margin + 200
        col3_x = margin + 460

        # Línea 1
        p.setFont("Helvetica-Bold", 8)
        p.drawString(col1_x, y, f"Cliente:")
        p.drawString(col3_x, y, f"NIT:")
        p.setFont("Helvetica", 8)
        p.drawString(col1_x + 80, y, f"{receptor['codigo']} - {receptor['nombre']}")
        p.drawString(col3_x + 38, y, f"{receptor['numDocumento']}")
        y -= 10

        # Línea 2
        p.setFont("Helvetica-Bold", 8)
        p.drawString(col1_x, y, f"Nombre Comercial:")
        p.drawString(col3_x, y, f"NRC:")
        p.setFont("Helvetica", 8)        
        p.drawString(col1_x + 80, y, f"{receptor['nombreComercial']}")
        p.drawString(col3_x + 38, y, f"{receptor.get('nrc')}")
        y -= 10

        # Línea 3
        p.setFont("Helvetica-Bold", 8)
        p.drawString(col1_x, y, f"Act. Económica:")
#        p.drawString(col3_x, y, f"Teléfono:")
        p.setFont("Helvetica", 8)
        p.drawString(col1_x + 80, y, f"{receptor.get('actividad_economica')}")
#        p.drawString(col3_x + 38, y, f"{receptor.get('telefono')}")
        y -= 10

        # Línea 4
        p.setFont("Helvetica-Bold", 8)
        p.drawString(col1_x, y, f"Correo:")
        p.drawString(col3_x, y, f"F. Pago:")
        p.setFont("Helvetica", 8)
        p.drawString(col1_x + 80, y, f"{receptor.get('correo')}")
        p.drawString(col3_x + 38, y, condicion)
        y -= 10

        # Línea 5 (Dirección con división automática)
        p.setFont("Helvetica-Bold", 8)
        p.drawString(col1_x, y, f"Dirección:")
        p.setFont("Helvetica", 8)
        if len(direccion) > 75:
            linea1 = direccion[:75]
            linea2 = direccion[75:]
            p.drawString(col1_x + 80, y, linea1)
            y -= 10
            p.drawString(col1_x + 80, y, linea2)
        else:
            p.drawString(col1_x + 80, y, direccion)
        y -= 10

        # Línea 6
        p.setFont("Helvetica-Bold", 8)
        p.drawString(col1_x, y, f"Municipio:")
        p.drawString(col2_x, y, f"Vendedor:")
        p.drawString(col2_x + 80, y, f"Entrega:")
        p.drawString(col3_x, y, f"Moneda:")
        p.setFont("Helvetica", 8)
        p.drawString(col1_x + 80, y, f"{receptor.get('municipio')}")
        p.drawString(col2_x + 45, y, f"{receptor.get('vendedor')}")
        p.drawString(col2_x + 120, y, f"{receptor.get('rutaEntrega')}")
        p.drawString(col3_x + 38, y, f"{identificacion.get('tipoMoneda')}")
        y -= 10

        # Línea 7
        p.setFont("Helvetica-Bold", 8)
        p.drawString(col1_x, y, f"Departamento:")
        p.drawString(col3_x, y, f"Teléfono:")        
        p.setFont("Helvetica", 8)
        p.drawString(col1_x + 80, y, f"{receptor.get('departamento')}")
        p.drawString(col3_x + 38, y, f"{receptor.get('telefono')}")
        if nombreDocumento =='Factura de exportación':
            p.setFont("Helvetica-Bold", 8)
            p.drawString(col2_x, y, f"Incoterms:")
            p.setFont("Helvetica", 8)
            p.drawString(col2_x + 45, y, f"{receptor.get('incoterms')}")

        # Linea 8: Documentos Relacionados
        if tipoDte in ['05', '06']:
            y -= 18
            p.setFont("Helvetica-Bold", 7)
            p.drawString(col1_x, y - 5, "Documento Relacionado:")
            p.drawString(col2_x + 56, y - 5, "Número Control:")
            p.drawString(col3_x, y - 5, "Fecha Documento:")
            p.setFont("Helvetica", 7)
            p.drawString(col1_x + 90, y - 5, docRelCodigoGeneracion)
            p.drawString(col2_x + 120, y - 5, numeroControl)
            p.drawString(col3_x + 65, y - 5, docRelFecha_emision)
        if oCompra != '':
            y -= 18             
            p.setFont("Helvetica-Bold", 7)
            p.drawString(col1_x, y - 5, "Orden de Compra:")
            p.setFont("Helvetica", 7)
            p.drawString(col1_x + 80, y - 5, oCompra)

        return y - 5  # o el valor que realmente se use



    def draw_headers(self, p, y):
        margin = 5 * mm
        x = margin
        headers = ["ITEM", "CANT.", "UNI.\nMED", "CODIGO", "DESCRIPCION", "PRECIO\nUNIT.", "DESCU.\nSKU", "VENTAS\nNO SUJ.", "VENTAS\nEXENTAS", "VENTAS\nGRAVADAS"]
        col_widths = [20, 20, 20, 60, 275, 35, 35, 35, 35, 45]
                
        p.setFont("Helvetica-Bold", 6)
        header_height = 20  # Altura de la fila del encabezado
        line_height = 6     # Espacio entre las líneas de texto
            
        for i, header in enumerate(headers):
            # Establecer color de fondo gris claro
            p.setFillColor(colors.grey, alpha=0.75)  # Gris claro con algo de transparencia
            p.rect(x, y, col_widths[i], header_height, fill=1)  # Dibujar el rectángulo con relleno

            # Dividir el texto en líneas si tiene salto de línea
            lines = header.split("\n")
            # Escribir y centrar cada línea del encabezado
            for j, line in enumerate(lines):
                text_width = p.stringWidth(line, "Helvetica-Bold", 6)
                text_x = x + (col_widths[i] - text_width) / 2  # Centrado horizontal
                p.setFillColor(colors.black)  # Establecer el color del texto a negro
                p.drawString(text_x, y + header_height - (j * line_height + 10), line)  # Ajustar la altura de cada línea
            x += col_widths[i]        

        p.setFont("Helvetica", 7)
        y -= 10 

        return y       


    # Función para alinear a la derecha los valores numéricos
    def draw_right_aligned_text(self, canvas, x, y, text, width, font, font_size):
        # Determinar el tamaño del texto para el ajuste de la posición
        text_width = canvas.stringWidth(text, font, font_size)
        # Dibujar el texto alineado a la derecha
        canvas.drawString(x + width - text_width - 3, y, text)  # 3 es un margen extra

    def generar_pdf_con_reportlab(self, data, total_page):
        buffer = io.BytesIO()

        estado = data['identificacion'].get('estado')

        # Etapa 1: Canvas en modo de conteo
        contar = canvas.Canvas(buffer, pagesize=letter)
        contar.setTitle("Documento Temporal")

        # Márgenes y medidas base
        paginas = total_page
        width, height = letter
        margin = 5 * mm  # Márgenes de 5 mm
        y = height - margin

        self.dibujar_encabezado(contar, data)
        y = height - 310  # Altura inicial después del encabezado

        # ========== TABLA DE DETALLES ========== 
        
        y = self.draw_headers(contar, y)
        contar.setFont("Helvetica", 7)

        col_widths = [20, 20, 20, 60, 275, 35, 35, 35, 35, 45]        
        line_height = 10     # Espacio entre las líneas de texto
        pagina_actual = 1

        detalles = data.get('detalle') or data.get('cuerpoDocumento', [])
        # logger.error(f"Estos son los valores de detalle: {detalles}")
        for item in detalles:
            if y is None or y < 100:  # Salto de página si se acaba el espacio
                self.dibujar_pie_pagina(contar, pagina_actual, "")
                contar.showPage()
                pagina_actual += 1
                self.dibujar_encabezado(contar, data)
                y = height - 310
                y = self.draw_headers(contar, y)

            x = margin
            valores = [
                   item['numItem'], 
                f"{item['cantidad']:.2f}", 
                   item['uniMedida'],
                   item['codigo'],
                   item['descripcion'],
                f"{item['precioUni']:.2f}",
                f"{item['montoDescu']:.2f}", 
                f"{item['ventaNoSuj']:.2f}",
                f"{item['ventaExenta']:.2f}",
                f"{item['ventaGravada']:.2f}"
            ]
            line_height = 10  # altura base para una línea

            max_height = line_height  # altura real usada por esta fila (inicialmente mínima)

            for i, val in enumerate(valores):
                texto = str(val)
                
                if i == 4:  # DESCRIPCIÓN: dividir manualmente si es larga
                    contar.setFont("Helvetica", 7)
                    if len(texto) > 62:
                        linea1 = texto[:62]
                        linea2 = texto[62:]
                        contar.drawString(x + 3, y, linea1)
                        contar.drawString(x + 3, y - line_height, linea2)
                        max_height = line_height * 2
                    else:
                        contar.drawString(x + 3, y, texto)
                        max_height = line_height
                elif i in [0, 3]:  # ITEM, CODIGO alineados a la izquierda
                    contar.drawString(x + 3, y, texto)
                else:  # numéricos alineados a la derecha
                    self.draw_right_aligned_text(contar, x, y, texto, col_widths[i], "Helvetica", 7)

                x += col_widths[i]

            y -= max_height  # ajustar y según lo que se usó            
            # for i, val in enumerate(valores):
            #     if i in [0, 3, 4]:  # El primer valor (número de ítem) y la descripción, alineados a la izquierda
            #         contar.drawString(x + 3, y, str(val))
            #     else:  # Los demás valores numéricos, alineados a la derecha
            #         self.draw_right_aligned_text(contar, x, y, str(val), col_widths[i], "Helvetica", 7)
            #     x += col_widths[i]
            # y -= line_height

        # logger.error (f"El valor de Y al terminar detalle es: {y}")

        # ========== RESUMEN ========== 
        inicio_resumen = y
        resumen = data.get("resumen", {})
        tipo_doc = resumen['tipoDocumento'].get('valor')
        lineas_resumen = 0
        # logger.error(f"El fijo al iniciar resumen es: {inicio_resumen}")
        if y < 150:
            self.dibujar_pie_pagina(contar, pagina_actual, "")
            contar.showPage()
            pagina_actual += 1
            self.dibujar_encabezado(contar, data)
            y = height - 310

        y -= 20

        # Configuración de las columnas para el resumen
        key_col_x = width - 120                                              # Esto me permite definir donde colocar las claves (labels)
        value_col_x = key_col_x + 100                                        # Ajuste para alinear el valor a la derecha
        y_resum = inicio_resumen - 20                                        # Esto me permitirar brindar el valor inicial para colocar el resumen segun la fila donde termina el detalle
        # logger.error(f"Asignado nuevas posiciones, para Y {y}, para y_resum = {y_resum}")
        contar.setFont("Helvetica", 7)

        # ====== LIMPIEZA DE CLAVES SEGÚN TIPO DE DOCUMENTO ======
        resumen.pop('tipoDocumento', {}).get('valor')

        elimina_claves_por_tipo = {
            '01': ['IVA (+)', 'Retencion Renta (-)', 'Flete (+)', 'Seguro (+)'],
            '14': ['IVA (+)', 'Sub Total (=)', 'IVA Percibido (+)', 'Monto Total Descuento (-)',
                'Otros Montos no Afectos(+)', 'Flete (+)', 'Seguro (+)'],
            '11': ['Monto Total Descuento (-)', 'Retencion Renta (-)', 'IVA (+)', 'Sub Total (=)',
                'IVA Percibido (+)', 'IVA Retenido (-)', 'Monto Total de la Operación (=)',
                'Otros Montos no Afectos (+)'],
            '07': ['Monto Total Descuento (-)', 'Retencion Renta (-)', 'IVA (+)', 'Sub Total (=)',
                'IVA Percibido (+)', 'IVA Retenido (-)', 'Monto Total de la Operación (=)',
                'Otros Montos no Afectos (+)', 'Flete (+)', 'Seguro (+)']
        }

        if tipo_doc in elimina_claves_por_tipo:
            for clave in elimina_claves_por_tipo[tipo_doc]:
                resumen.pop(clave, None)

        if tipo_doc == '07' and 'Suma Total Operación (+)' in resumen:
            resumen['IVA RETENIDO'] = resumen.pop('TOTAL A PAGAR (=)', resumen.get('TOTAL A PAGAR (=)'))

        # Mostrar 'Total en Letras' en su propia columna
        total_en_letras = data['resumen'].get('Total en Letras', {}).get('valor', '')

        for key, val in data['resumen'].items():
            if key not in ['tipoDocumento','Total en Letras']:
                # Si es necesario hacer un salto de página
                # logger.error(f"Inciando la evaluacion de y < 150: {y}")
                if y < 150:                                                 # Si el texto se sale del área de la página
                    self.dibujar_pie_pagina(contar, pagina_actual, paginas)
                    contar.showPage()             
                    pagina_actual += 1                    
                    # Redibujar los encabezados si se hace salto de contarágina
                    self.dibujar_encabezado(contar, data)
                    y = height - 310
                # Clave en la columna izquierda-
                contar.drawRightString(key_col_x, y_resum, f"{key}:")

                # Asegurarse de que 'val['valor']' es un número flotante antes de formatearlo
                try:
                    valor = float(val['valor'])  # Convertir a float
                    contar.drawRightString(value_col_x, y_resum, f"$ {valor:.2f}")     # Valor en la columna derecha, alineado a la derecha, con dos decimales
                except ValueError:
                    contar.drawRightString(value_col_x, y_resum, str(val['valor']))    # Si no es un número, mostrar el valor tal cual

                # Ajustar la posición `y` para el siguiente resumen
                y -= 10
                y_resum -=10
                lineas_resumen += 1
 
        altura_resumen = (lineas_resumen + 1) * 10  # línea por línea + "Resumen:"

        # Coordenadas del rectángulo
        x_rect = margin                                     # Un poco antes de la primera columna de clave
        y_rect = inicio_resumen - 5                         # Justo un poco más arriba del título
        ancho_rect = width - 2 * margin                     # Suficiente para cubrir claves y valores
        alto_rect = altura_resumen + 5                      # Espacio adicional para el borde superior
        # logger.error(f"Altura de resumen: {altura_resumen}")

        # De esta manera aseguro que el total en letras se coloque donde se inicia el rectangulo
        contar.rect(x_rect, y_rect - alto_rect, ancho_rect, alto_rect, stroke=1, fill=0)   
        if total_en_letras:
            contar.drawString(margin + 5, y_rect - 15, f"Total en Letras: ")
            contar.setFont("Helvetica-Bold", 8)
            contar.drawString(margin + 60, y_rect - 15, f"{total_en_letras.upper()}")
     
        # --- AL FINAL DEL DOCUMENTO, ANTES DEL ÚLTIMO SAVE ---
        if estado == 'INVALIDADO':
            self.dibujar_sello_anulado(contar)

        self.dibujar_pie_pagina(contar, pagina_actual, paginas)
        contar.showPage()
        contar.save()

        pdf_value = buffer.getvalue()
        buffer.close()
        return pdf_value


    def dibujar_sello_anulado(self, p):
        width, height = letter
        p.saveState()  # Guarda el estado actual del canvas
        p.setFont("Helvetica-Bold", 80)
        p.setStrokeColor(colors.red)
        p.setFillColor(colors.red, alpha=0.3) # Color rojo con transparencia
        
        # Mover el origen al centro para rotar
        p.translate(width / 2, height / 2)
        p.rotate(45)
        
        # Dibujar el texto centrado en el nuevo origen
        p.drawCentredString(0, 0, "INVALIDADO")
        
        p.restoreState() # Restaura el estado original (quitar rotación y traslación)            
            

    @staticmethod
    def construir_diccionario(codigoGeneracion):
        documentorel={}
        documentos = Documentos.objects.filter(codigoGeneracion = codigoGeneracion).first()
        if documentos.numeroDocumento_rel_guid:
            documento_rel = Documentos.objects.filter(codigoGeneracion = documentos.numeroDocumento_rel_guid).first()
            # logger.error(f"Documento relacionado: {documento_rel}")
            documentorel = {'codigoGeneracion':documento_rel.codigoGeneracion,'numeroControl':documento_rel.numeroControl,'fecEmi':documento_rel.fecEmi}
        else:
            documentorel = {}
        
        #logger.error(f"Documento relacionado: {documento_rel} y sus datos: {documentorel}")

        lineas= []
        # ++++++++++++++++++++++ DATOS LIENA DETALLE+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        DocumentosDetalle_new = list(DocumentosDetalle.objects.filter(codigoGeneracion_id = codigoGeneracion))
        tipo_doc_use = documentos.tipodocumento_id        
        for doc in DocumentosDetalle_new:
            if tipo_doc_use == '14':
                ventaGravada = doc.cantidad * doc.precioUni
            else:
                ventaGravada = doc.ventaGravada

            lineas.append({'numItem':doc.numItem,'tipoItem':int(doc.tipoItem),'numeroDocumento':None,'cantidad':doc.cantidad,
                                                'codigo':doc.codigo,'codTributo':None,'uniMedida':doc.uniMedida,
                                                'descripcion':doc.descripcion,'precioUni':doc.precioUni,
                                                'montoDescu':doc.montoDescu,'ventaNoSuj':doc.ventaNoSuj,'ventaExenta':doc.ventaExenta,
                                                'ventaGravada':ventaGravada,
                                                'tributos':None,'psv':doc.psv,
                                                'noGravado':doc.noGravado,'ivaItem':doc.ivaItem })
                    
        # ==================== DATOS  RESUMEN =======================================================================
        pagos = Pagos.objects.filter(codigogeneracion_doc = codigoGeneracion).first()
        #logger.info(f" datos: {lineas}", exc_info=True)
        traceback.print_exc()
               
        resumen = {
                            'totalNoSuj': {
                                'valor': documentos.totalNoSuj,
                            },
                            'totalExenta': {
                                'valor': documentos.totalExenta,
                                
                            },
                            'totalGravada': {
                                'valor': documentos.totalGravada,
                            },
                            'Suma Total Operación (+)': {
                                'valor': documentos.subTotalVentas if documentos.tipodocumento_id not in ['14','07'] else documentos.totalSujetoRetenido,
                            },
                            'descuNoSuj': {
                                'valor': documentos.descuNoSuj,
                            },
                            'descuExenta': {
                                'valor': documentos.descuExenta,
                            },
                            'Monto Total Descuento (-)': {
                                'valor': documentos.descuGravada,

                            },
                            'porcentajeDescuento': {
                                'valor': documentos.porcentajeDescuento,

                            },
                            'totalDescu': {
                                'valor': documentos.totalDescu,
                            },
                            
                            'Sub Total (=)': {
                                'valor': documentos.montoTotalOperacion,
                            },
                            'IVA Percibido (+)': {
                                'valor': documentos.ivaPerci1,
                            },
                            'IVA Retenido (-)': {
                                'valor': documentos.ivaRete1 ,
                            },
                            'Retencion Renta (-)': {
                                'valor': documentos.reteRenta,
                            },
                            'Monto Total de la Operación (=)': {
                                'valor': documentos.totalPagar,
                            },
                            'Otros Montos no Afectos (+)': {
                                'valor': documentos.totalNoGravado,
                            },
                            'TOTAL A PAGAR (=)': {
                                'valor': documentos.totalPagar,
                            },
                            'Total en Letras': {
                                'valor': documentos.totalLetras,
                            },
                            'IVA (+)': {
                                'valor': documentos.iva,
                            },
                            'saldoFavor': {
                                'valor': documentos.saldoFavor,
                            },
                            'condicionOperacion': {
                                'valor': documentos.condicionOperacion.codigo,
                            },
                             'tipoDocumento': {
                                'valor': documentos.tipodocumento_id,
                            },
                            'Flete (+)': {
                                'valor': documentos.flete,
                            },
                            'Seguro (+)': {
                                'valor': documentos.seguro,
                            },
                            
            }
        key_for_resumen = ('Total en Letras',
                                'Suma Total Operación (+)',
                                'Monto Total Descuento (-)',
                                'Retencion Renta (-)',
                                'IVA (+)',
                                'Sub Total (=)',
                                'IVA Percibido (+)',
                                'IVA Retenido (-)',
                                'Monto Total de la Operación (=)',
                                'Otros Montos no Afectos (+)',
                                'Flete (+)',
                                'Seguro (+)',
                                'TOTAL A PAGAR (=)',
                                'tipoDocumento',
                                )
        resumen_copia = {}

              
        for key in key_for_resumen:
            if key in resumen:
                resumen_copia[key] = resumen[key]     
        # ============================ IDENTIFICACION =====================================================================
        identificacion ={'version':documentos.tipodocumento.version_work,'ambiente':documentos.emisor_id.ambiente_trabajo,
                             'tipoDte':documentos.tipodocumento.codigo,'numeroControl':documentos.numeroControl,
                             'codigoGeneracion':documentos.codigoGeneracion,'tipoModelo':int(documentos.tipoModelo.codigo),
                             'tipoOperacion':int(documentos.tipoOperacion.codigo),'tipoContingencia':documentos.tipoContingencia.codigo if documentos.tipoContingencia else None,
                             'motivoContin':documentos.motivoContin if documentos.motivoContin else None ,'fecEmi':documentos.fecEmi.strftime('%Y-%m-%d')
                            ,'horEmi':documentos.horEmi.strftime('%H:%M:%S'),'tipoMoneda':documentos.tipoMoneda,'selloRecibido':documentos.selloRecibido if documentos.selloRecibido else 'NO ENVIADO'
                            ,'condicionOperacion':documentos.condicionOperacion.codigo,'nombreDocumento':documentos.tipodocumento.valor,'Documento_interno' : documentos.num_documento ,
                              'estado':documentos.estado
                                                                                                                 }    
             
        #=========================== INFO EMPRESA ===========================================================================
        info_empresa = {'ID':documentos.emisor_id.id,'nit':documentos.emisor_id.nit,'nrc':documentos.emisor_id.nrc,'nombre':documentos.emisor_id.nombre,
                                'codActividad':documentos.emisor_id.codactividad.codigo, 'descActividad':documentos.emisor_id.codactividad.nombre,
                                'nombreComercial':documentos.emisor_id.nombrecomercial,'tipoEstablecimiento':documentos.emisor_id.tipoestablecimiento.codigo,
                               'departamento':  documentos.emisor_id.departamento.codigo, 
                                'municipio': documentos.emisor_id.municipio.codigo, 
                                'direccion_complemento': documentos.emisor_id.direccion_complemento,
                                'telefono': documentos.emisor_id.telefono,
                                'correo': documentos.emisor_id.correo,
                                'codEstableMH':documentos.emisor_id.codestablemh,'codEstable':documentos.emisor_id.codestable,
                                'codPuntoVentaMH':documentos.emisor_id.codpuntoventamh,'codPuntoVenta':documentos.emisor_id.codpuntoventa ,
                                 'categoria':documentos.emisor_id.categoria,'whatsapp':documentos.emisor_id.whatsapp,'logo':documentos.emisor_id.company.logo.path }

        # Determinar cliente y factura
        receptor = documentos.receptor_id.codigo if documentos.receptor_id else documentos.proveedor_id.codigo if documentos.proveedor_id else None
        factura = documentos.num_documento

        if receptor == '16051':
                        info_cliente = ConsecutivosSF.obtener_info_cliente_desde_sqlserver(receptor, documentos.emisor_id.id, factura)
        else:
                        info_cliente = {'codigo': receptor,
                       'tipoDocumento':  documentos.receptor_id.tipodocumento.nombre if documentos.receptor_id else documentos.proveedor_id.nombre if documentos.proveedor_id else None,'numDocumento':documentos.receptor_id.numdocumento if documentos.receptor_id else documentos.proveedor_id.numdocumento if documentos.proveedor_id else None,
                        'nrc':documentos.receptor_id.nrc if documentos.receptor_id and documentos.receptor_id.nrc   else documentos.proveedor_id.nrc if documentos.proveedor_id else None,
                        'nombre':documentos.receptor_id.nombre if documentos.receptor_id else documentos.proveedor_id.nombre if documentos.proveedor_id else None,
                        'codActividad':documentos.receptor_id.codactividad.codigo if documentos.receptor_id else documentos.proveedor_id.codactividad.codigo if documentos.proveedor_id else None,
                        'actividad_economica':documentos.receptor_id.codactividad.codigo +" - "+ documentos.receptor_id.codactividad.nombre if documentos.receptor_id else
                          documentos.proveedor_id.codactividad.codigo +" - "+ documentos.proveedor_id.codactividad.nombre if documentos.proveedor_id else None,

                        'nombreComercial': documentos.receptor_origen.codigo +' - '+ documentos.receptor_origen.nombrecomercial if documentos.receptor_origen else  documentos.receptor_id.nombrecomercial
                                                if documentos.receptor_id else 
                                                documentos.proveedor_id.nombrecomercial
                                                if documentos.proveedor_id else None,
                        
                        'codPais':documentos.receptor_id.codpais.codigo if documentos.receptor_id else documentos.proveedor_id.codpais.codigo if documentos.proveedor_id else None,
                        'tipoPersona':documentos.receptor_id.tipopersona.codigo if documentos.receptor_id else documentos.proveedor_id.tipopersona.codigo if documentos.proveedor_id else None,
                        'tipoReceptor':documentos.receptor_id.tiporeceptor if documentos.receptor_id else documentos.proveedor_id.tiporeceptor if documentos.proveedor_id else None,
                        'departamento':documentos.receptor_origen.departamento.nombre if documentos.receptor_origen else documentos.receptor_id.departamento.nombre
                                        if documentos.receptor_id else documentos.proveedor_id.departamento.nombre if documentos.proveedor_id else None, 
                        'vendedor': documentos.vendedor_id ,
                        ##'municipio':documentos.receptor_origen.municipio.nombre if documentos.receptor_origen else documentos.receptor_id.municipio.nombre
                        ##                if documentos.receptor_id else documentos.proveedor_id.municipio.nombre if documentos.proveedor_id else None,         
                        'municipio':documentos.receptor_origen.munidistrito.nombre if documentos.receptor_origen else documentos.receptor_id.munidistrito.nombre
                                if documentos.receptor_id else documentos.proveedor_id.munidistrito.nombre if documentos.proveedor_id else None,
                        'complemento': documentos.receptor_origen.complemento if documentos.receptor_origen else documentos.receptor_id.complemento
                                        if documentos.receptor_id else documentos.proveedor_id.complemento if documentos.proveedor_id else None, 
                        'telefono':documentos.receptor_origen.telefono if documentos.receptor_origen else documentos.receptor_id.telefono
                                if documentos.receptor_id else documentos.proveedor_id.telefono if documentos.proveedor_id else None, 
                        'correo':documentos.receptor_origen.correo if documentos.receptor_origen else documentos.receptor_id.correo
                                        if documentos.receptor_id else documentos.proveedor_id.correo if documentos.proveedor_id else None, 
                        'incoterms':documentos.codIncoterms.descripcion if documentos.codIncoterms else None,
                        'rutaEntrega': documentos.rutaEntrega
                        }
        apendice = {'campo':'OrdenCompra','etiqueta':'Número de Orden de Compra','valor': documentos.orden_compra} if documentos.orden_compra else None


        total_lineas = len(lineas) + len(info_empresa) + len(info_cliente)                

        # Recopilación de datos como ya la tienes
        dic_final = {
            'emisor': info_empresa,
            'receptor': info_cliente,
            'detalle': lineas,
            'resumen': resumen_copia,
            'identificacion': identificacion,
            #'size': max_lineas + 1,
            'documentoRelacionado': documentorel,
            'apendice': apendice
        }

        #logger.error (f"Datos del dic_final: {dic_final}")

        return dic_final, total_lineas


    def generarPdf(request,codigoGeneracion):

        diccionario, total_lineas = ger_pdf.construir_diccionario(codigoGeneracion)

        #logger.error (f"Datos del dic_final: {dic_final}")

        max_lineas = 46

        total_pages = 0
        int_pages =   math.trunc(total_lineas/ max_lineas)
        dec_page = (total_lineas/ max_lineas) - int_pages


        if(dec_page>0.0):
            total_pages = int_pages + 1
        #    logger.error(f"Paginas totales: {total_pages}")
        else:
            total_pages = int_pages
        #    logger.error(f"Paginas totales: {total_pages}")

        generador = ger_pdf(args={})

        # Generar el PDF dentro del buffer usando ReportLab
        pdf_bytes = generador.generar_pdf_con_reportlab(diccionario, total_pages)

        # Preparar la respuesta HTTP con el contenido del buffer
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={codigoGeneracion}.pdf'
        return response
    
    def generar_pdf_byte(codigoGeneracion):
        
        diccionario, total_lineas = ger_pdf.construir_diccionario(codigoGeneracion)

        max_lineas = 46

        total_pages = 0
        int_pages =   math.trunc(total_lineas/ max_lineas)
        dec_page = (total_lineas/ max_lineas) - int_pages


        if(dec_page>0.0):
            total_pages = int_pages + 1
        #    logger.error(f"Paginas totales: {total_pages}")
        else:
            total_pages = int_pages
        #    logger.error(f"Paginas totales: {total_pages}")

        generador = ger_pdf(args={})

        # Generar el PDF dentro del buffer usando ReportLab
        pdf_bytes = generador.generar_pdf_con_reportlab(diccionario, total_pages) 
        return pdf_bytes        
         