from decimal import Decimal
from datetime import datetime
## -- Agregado para pruebas 2025-04-07
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.utils import simpleSplit
from reportlab.graphics import renderPDF
import io

import os
import math
import locale
from dtesv.models.documentos import Documentos
from dtesv.processes.PDF.resumen_pdf_adapter import construir_resumen
from dtesv.processes.PDF.identificacion_pdf_builder import construir_identificacion
from dtesv.processes.PDF.emisor_pdf_builder import construir_emisor
from dtesv.processes.PDF.receptor_pdf_builder import construir_receptor
from dtesv.processes.PDF.detalle_pdf_builder import construir_detalle
from dtesv.processes.PDF.apendice_pdf_builder import construir_apendice
from dtesv.processes.PDF.docRelacionado_pdf_builder import construir_documento_relacionado
from dtesv.processes.PDF.textos_pdf_fijos import PIE_PAGINA, SELLO_ANULADO
from dtesv.processes.PDF import encabezado_dte_config, encabezado_cliente_config
from dtesv.models.company import Company
from dtesv.models.settings import Parametros

import logging
logger = logging.getLogger(__name__)


current_directory = os.path.dirname(os.path.abspath(__file__))
directorio_actual = os.getcwd()
mymodule_dir = os.path.join(directorio_actual, 'Facturacion_electronica\\dtesv')
image_dir = os.path.join(mymodule_dir, 'static\img')

from pathlib import Path

locale.setlocale(locale.LC_ALL, 'es_SV.UTF-8')


class gen_pdf():
    def __init__(self, args):
        self.args = args 

## -- Agregado para pruebas 2025-04-07        
    def dibujar_pie_pagina(self, p, num_pagina, total_paginas):
        width, height = letter
        p.setFont(PIE_PAGINA["fuente"], PIE_PAGINA["tam_fuente"])
        texto = PIE_PAGINA["texto"].format(num_pagina=num_pagina, total_paginas=total_paginas)
        p.drawCentredString(width / 2, 15, texto)
        # width, height = letter
        # p.setFont("Helvetica", 6)
        # p.drawCentredString(width / 2, 15, f"Página {num_pagina} de {total_paginas}")

    # --- dibujar_sello_anulado: ahora solo lee de SELLO_ANULADO ---
    def dibujar_sello_anulado(self, p):
        width, height = letter
        cfg = SELLO_ANULADO
        p.saveState()
        p.setFont(cfg["fuente"], cfg["tam_fuente"])
        p.setStrokeColor(cfg["color"])
        p.setFillColor(cfg["color"], alpha=cfg["alpha_relleno"])
        p.translate(width / 2, height / 2)
        p.rotate(cfg["angulo"])
        p.drawCentredString(0, 0, cfg["texto"])
        p.restoreState()


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
        y_emisor = y

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
        p.drawCentredString(center_x, y_id - 10, identificacion['nombreDocumento'].upper())
    
        contexto_dte = {
            "codigoGeneracion": identificacion['codigoGeneracion'],
            "selloRecibido": identificacion['selloRecibido'],
            "numeroControl": identificacion['numeroControl'],
            "modelo": modelo,
            "version": identificacion['version'],
            "tipo_transmision": Tipo_transmision,
            "fecEmi": identificacion['fecEmi'],
            "documento_interno": Documento_interno,
            "horEmi": identificacion['horEmi'],
        }
        y = encabezado_dte_config.dibujar(p, box_x, y_id - 30, contexto_dte)
    
        p.setFont("Helvetica", 5)
        p.drawString(box_x + 270, y, "MH.J02")  # col4_x == box_x + 270
    

        # ========= DATOS DEL CLIENTE (recuadro de altura dinámica) =========
        y_ultima_fila = y_emisor - 9 * (len(emisor_data) - 1)
        y_top = min(y_ultima_fila - 8, box_y) - 8        
        col1_x = margin + 5
        col2_x = margin + 200
        col3_x = margin + 460

        contexto_cliente = {
            "receptor": receptor,
            "identificacion": identificacion,
            "condicion": condicion,
            "documentoRelacionado": docRelacionado,
            "docRelFecha_emision": docRelFecha_emision,
            "oCompra": oCompra,
        }

        y_fin = encabezado_cliente_config.dibujar(p, col1_x, col2_x, col3_x, y_top - 12, contexto_cliente)

        p.setStrokeColor(colors.black)
        p.setLineWidth(0.5)
        p.rect(margin, y_fin, width - 2 * margin, y_top - y_fin, stroke=1, fill=0)

        # ========= RECUADRO DE REFERENCIAS (solo si aplica) =========
        if encabezado_cliente_config.hay_referencias(contexto_cliente):
            y_ref_top = y_fin - 4
            y_ref_fin = encabezado_cliente_config.dibujar_referencias(
                p, col1_x, col2_x, col3_x, y_ref_top - 10, contexto_cliente
            )
            p.rect(margin, y_ref_fin, width - 2 * margin, y_ref_top - y_ref_fin, stroke=1, fill=0)
            y_fin = y_ref_fin

        return y_fin - 12


    def _urls_qr(self, data):
        ident = data['identificacion']
        cod = ident['codigoGeneracion']
        fec = ident['fecEmi']
        url_mh = f'https://admin.factura.gob.sv/consultaPublica?ambiente=01&codGen={cod}&fechaEmi={fec}'
        # url_desc = f'http://192.168.1.53:8000/dtesv/descargar/{cod}/'
        return [(url_mh, "Portal Ministerio de Hacienda") #, (url_desc, "Descargar Archivos")
                ]

    def _dibujar_qr(self, p, url, x, y, size, etiqueta):
        widget = qr.QrCodeWidget(url)
        x0, y0, x1, y1 = widget.getBounds()
        d = Drawing(size, size, transform=[size / (x1 - x0), 0, 0, size / (y1 - y0), 0, 0])
        d.add(widget)
        renderPDF.draw(d, p, x, y)
        p.setFont("Helvetica", 5)
        p.drawCentredString(x + size / 2, y - 7, etiqueta)   # etiqueta centrada bajo su QR

    def dibujar_qrs_centrados(self, p, x_centro, y_top, qrs, size=55, gap=25):
        """qrs = [(url, etiqueta), ...]. Devuelve la y donde termina el texto de las etiquetas."""
        total = len(qrs) * size + (len(qrs) - 1) * gap
        x = x_centro - total / 2
        y = y_top - size
        for url, etiqueta in qrs:
            self._dibujar_qr(p, url, x, y, size, etiqueta)
            x += size + gap
        return y - 7


    def _nueva_pagina_detalle(self, p, data):
        """Dibuja encabezado + cabecera de tabla; devuelve la y de la primera fila."""
        y_enc = self.dibujar_encabezado(p, data)      # ya es dinámico según el tipo de documento
        return self.draw_headers(p, y_enc - 20)       # 20 = header_height de draw_headers
    

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

    #def generar_pdf_con_reportlab(self, data, paginas): #total_page
    def _renderizar_pdf(self, data, paginas):
        """Dibuja el PDF completo. Devuelve (bytes, número real de páginas)."""    
        buffer = io.BytesIO()

        estado = data['identificacion'].get('estado')

        # Etapa 1: Canvas en modo de conteo
        contar = canvas.Canvas(buffer, pagesize=letter)
        contar.setTitle("Documento Temporal")

        # Márgenes y medidas base
        #paginas = total_page
        width, height = letter
        margin = 5 * mm  # Márgenes de 5 mm
        y = height - margin

        # self.dibujar_encabezado(contar, data)
        # y = height - 310  # Altura inicial después del encabezado
        y = self._nueva_pagina_detalle(contar, data)
        contar.setFont("Helvetica", 7)

        # ========== TABLA DE DETALLES ========== 
        
        # y = self.draw_headers(contar, y)
        # contar.setFont("Helvetica", 7)

        col_widths = [20, 20, 20, 60, 275, 35, 35, 35, 35, 45]        
        line_height = 10     # Espacio entre las líneas de texto
        pagina_actual = 1

        detalles = data.get('detalle') or data.get('cuerpoDocumento', [])
        # logger.error(f"Estos son los valores de detalle: {detalles}")
        for item in detalles:
            if y is None or y < 100:  # Salto de página si se acaba el espacio
                self.dibujar_pie_pagina(contar, pagina_actual, paginas) # Se reemplazo ""
                contar.showPage()
                pagina_actual += 1
                # self.dibujar_encabezado(contar, data)
                # y = height - 310
                y = self._nueva_pagina_detalle(contar, data)
                contar.setFont("Helvetica", 7)

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

        # ========== RESUMEN ==========
        resumen = data.get("resumen", {})
        claves_resumen = [k for k in resumen if k not in ('tipoDocumento', 'Total en Letras')]
        total_en_letras = resumen.get('Total en Letras', {}).get('valor', '')

        ALTO_MIN_IZQ = 120                                   # título + QR + total en letras
        altura_resumen = (len(claves_resumen) + 1) * 10
        alto_rect = max(altura_resumen, ALTO_MIN_IZQ) + 5

        if y - (alto_rect + 25) < 30:                        # el bloque completo no cabe: página nueva
            self.dibujar_pie_pagina(contar, pagina_actual, paginas)
            contar.showPage()
            pagina_actual += 1
            y = self.dibujar_encabezado(contar, data) - 10

        inicio_resumen = y
        y_rect = inicio_resumen - 5
        contar.setLineWidth(0.5)
        contar.rect(margin, y_rect - alto_rect, width - 2 * margin, alto_rect, stroke=1, fill=0)

        # --- Derecha: montos ---
        key_col_x = width - 120
        value_col_x = key_col_x + 100
        y_resum = inicio_resumen - 20
        contar.setFont("Helvetica", 7)
        for key in claves_resumen:
            valor = resumen[key]['valor']
            contar.drawRightString(key_col_x, y_resum, f"{key}:")
            try:
                contar.drawRightString(value_col_x, y_resum, f"$ {float(valor):.2f}")
            except (ValueError, TypeError):
                contar.drawRightString(value_col_x, y_resum, str(valor))
            y_resum -= 10

        # --- Izquierda: VALORES Y VALIDACIÓN ---
        # contar.setFont("Helvetica-Bold", 8)
        # contar.drawString(margin + 10, y_rect - 12, "VALORES Y VALIDACIÓN")

        qr_size, gap = 55, 25
        x_qr = margin + 10
        y_qr = y_rect - 8 - qr_size
        for url, etiqueta in self._urls_qr(data):
            self._dibujar_qr(contar, url, x_qr, y_qr, qr_size, etiqueta)
            x_qr += qr_size + gap

        y_tl = y_qr - 30
        contar.setFont("Helvetica", 7)
        contar.drawString(margin + 10, y_tl, "Total en Letras:")
        if total_en_letras:
            contar.setFont("Helvetica-Bold", 8)
            max_w = key_col_x - 130 - (margin + 10)
            for i, linea in enumerate(simpleSplit(total_en_letras.upper(), "Helvetica-Bold", 8, max_w)):
                contar.drawString(margin + 10, y_tl - 10 * (i + 1), linea)

     
        # --- AL FINAL DEL DOCUMENTO, ANTES DEL ÚLTIMO SAVE ---
        if estado == 'INVALIDADO':
            self.dibujar_sello_anulado(contar)

        self.dibujar_pie_pagina(contar, pagina_actual, paginas)
        contar.showPage()
        contar.save()

        pdf_value = buffer.getvalue()
        buffer.close()
        return pdf_value, pagina_actual  # número real de páginas generadas         
            

    def generar_pdf_con_reportlab(self, data, total_page=None):
        """total_page se ignora: se dibuja una vez para contar las páginas reales y otra con el total correcto."""
        _, n_paginas = self._renderizar_pdf(data, "")
        pdf_bytes, _ = self._renderizar_pdf(data, n_paginas)
        return pdf_bytes
    

    @staticmethod
    def construir_diccionario(codigoGeneracion):
        documentorel={}
        documentos = Documentos.objects.filter(codigoGeneracion = codigoGeneracion).first()

        identificacion = construir_identificacion(documentos)
        documentorel = construir_documento_relacionado(documentos)
        lineas = construir_detalle(codigoGeneracion, documentos.tipodocumento_id)
        resumen_copia = construir_resumen(documentos)
        info_empresa = construir_emisor(documentos)
        info_cliente = construir_receptor(documentos)
        apendice = construir_apendice(documentos)

        total_lineas = len(lineas) + len(info_empresa) + len(info_cliente)                

        # Recopilación de datos como ya la tienes
        dic_final = {
            'emisor': info_empresa,
            'receptor': info_cliente,
            'detalle': lineas,
            'resumen': resumen_copia,
            'identificacion': identificacion,
            'documentoRelacionado': documentorel,
            'apendice': apendice
        }

        #logger.error (f"Datos del dic_final: {dic_final}")
        return dic_final, total_lineas


    def generarPdf(request,codigoGeneracion):

        # diccionario, total_lineas = gen_pdf.construir_diccionario(codigoGeneracion)

        # #logger.error (f"Datos del dic_final: {dic_final}")

        # max_lineas = 46

        # total_pages = 0
        # int_pages =   math.trunc(total_lineas/ max_lineas)
        # dec_page = (total_lineas/ max_lineas) - int_pages


        # if(dec_page>0.0):
        #     total_pages = int_pages + 1
        # #    logger.error(f"Paginas totales: {total_pages}")
        # else:
        #     total_pages = int_pages
        # #    logger.error(f"Paginas totales: {total_pages}")

        # generador = gen_pdf(args={})

        # # Generar el PDF dentro del buffer usando ReportLab
        # pdf_bytes = generador.generar_pdf_con_reportlab(diccionario, total_pages)
        diccionario, _ = gen_pdf.construir_diccionario(codigoGeneracion)

        generador = gen_pdf(args={})
        pdf_bytes = generador.generar_pdf_con_reportlab(diccionario)        

        # Construir ruta absoluta del archivo
        # Obtener los parámetros de configuración basados en el código de generación
        documento = Documentos.objects.filter(codigoGeneracion=codigoGeneracion).first()
        if not documento:
            logger.error(f"Documento no encontrado para el código: {codigoGeneracion}")
            return None

        company = Company.objects.filter(emisor_id=documento.emisor_id).first()
        if not company:
            logger.error(f"Empresa no encontrada para el emisor_id: {documento.emisor_id}")
            return None

        parametros = Parametros.objects.filter(company_id=company).first()
        if not parametros:
            logger.error(f"Parámetros no configurados para la empresa: {company}")
            return None
            
        file_path = os.path.join(parametros.attachment_files_path, f"{codigoGeneracion}.pdf")

        logger.error(f"Direccion de almacenamiento PDF: {file_path}")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)            

        with open(file_path, "wb") as file:
            file.write(pdf_bytes)

        # ==========================
        # CONTRATO ORIGINAL
        # ==========================            
        return {'pdf_file': file_path}
    
    def generar_pdf_byte(codigoGeneracion):
        
        # diccionario, total_lineas = gen_pdf.construir_diccionario(codigoGeneracion)

        # max_lineas = 46

        # total_pages = 0
        # int_pages =   math.trunc(total_lineas/ max_lineas)
        # dec_page = (total_lineas/ max_lineas) - int_pages


        # if(dec_page>0.0):
        #     total_pages = int_pages + 1
        # #    logger.error(f"Paginas totales: {total_pages}")
        # else:
        #     total_pages = int_pages
        # #    logger.error(f"Paginas totales: {total_pages}")

        # generador = gen_pdf(args={})

        # # Generar el PDF dentro del buffer usando ReportLab
        # pdf_bytes = generador.generar_pdf_con_reportlab(diccionario, total_pages) 
        # return pdf_bytes       

        diccionario, _ = gen_pdf.construir_diccionario(codigoGeneracion)
        return gen_pdf(args={}).generar_pdf_con_reportlab(diccionario)         
         