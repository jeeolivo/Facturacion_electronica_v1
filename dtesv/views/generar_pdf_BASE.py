from io import BytesIO
from borb.pdf import Document

from borb.pdf.page.page import Page
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from decimal import Decimal
from borb.pdf.canvas.color.color import RGBColor
from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.image.barcode import Barcode, BarcodeType
from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.annotation.square_annotation import SquareAnnotation
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf import FixedColumnWidthTable
from borb.pdf import HexColor ,X11Color
from datetime import datetime
from borb.pdf.pdf import PDF
from borb.pdf.page.page_size import PageSize
import sys
import os
import math
import locale
from dtesv.models import Documentos ,DocumentosDetalle,ExtencionEntrega,DocumentosAsociados,Pagos
from django.http import FileResponse, HttpResponse
from dtesv.tools.consecutivo_local import ConsecutivosSF
import logging
import traceback
logger = logging.getLogger(__name__)
 

current_directory = os.path.dirname(os.path.abspath(__file__))
directorio_actual = os.getcwd()
mymodule_dir = os.path.join(directorio_actual, 'Facturacion_electronica\\dtesv')
image_dir = os.path.join(mymodule_dir, 'static\img')

from pathlib import Path
import random

locale.setlocale(locale.LC_ALL, 'es_SV.UTF-8')

class ger_pdf():
        def __init__(self, args):
                self.args = args

        def _footer_page_table(self):
                resumen = self['resumen']
                num_rows = len(resumen)-1
                num_cols = 10
                try:    
                        tipo_doc = resumen['tipoDocumento']
                        resumen.pop('tipoDocumento', None)
                        # ======== SI ES FACTURA CONSUMIDOR FINAL ========================
                        if tipo_doc['valor'] in ['01']:
                              resumen.pop('IVA(+)')
                              resumen.pop('Retencion Renta (-)') 
                              resumen.pop('seguro') 
                              resumen.pop('flete') 
                     # ==== SI ES  SUJETO EXCLUIDO=====================================
                        elif  tipo_doc['valor'] in ['14']:
                              claves_a_eliminar = ['IVA(+)', 'Sub Total(=)', 'IVA Percibido(+)', 'Monto Total Descuento(-)','Otros Montos no Afectos(+)'
                                                   ,'flete','seguro']
                              for clave in claves_a_eliminar:
                                  resumen.pop(clave, None)
                        
                        elif  tipo_doc['valor'] in ['11']:
                                claves_a_eliminar = [ 'Monto Total Descuento(-)',
                                        'Retencion Renta (-)',
                                        'IVA(+)',
                                       'Sub Total(=)',
                                        'IVA Percibido(+)',
                                        'IVA Retenido(-)',
                                        'Monto Total de la Operación (=)',
                                        'Otros Montos no Afectos(+)',
                                        ]
                                for clave in claves_a_eliminar:
                                  resumen.pop(clave, None)
                              
                        elif tipo_doc['valor'] in ['07']:
                                claves_a_eliminar = [ 'Monto Total Descuento(-)',
                                        'Retencion Renta (-)',
                                        'IVA(+)',
                                        'Sub Total(=)',
                                        'IVA Percibido(+)',
                                        'IVA Retenido(-)',
                                        #'Suma Total Operación (+)',
                                        'Monto Total de la Operación (=)',
                                        'Otros Montos no Afectos(+)','seguro','flete',
                                        #'TOTAL A PAGAR(=)'
                                        ]
                                for clave in claves_a_eliminar:
                                        resumen.pop(clave, None)
                                if 'Suma Total Operación (+)' in resumen:
                                    resumen['IVA RETENIDO'] = resumen.pop('TOTAL A PAGAR(=)')

                        else:
                             resumen.pop('Retencion Renta (-)') 
                             resumen.pop('seguro') 
                             resumen.pop('flete') 
                                   
                        table_002 = Table(number_of_rows=len(resumen)-1, number_of_columns=num_cols)  

                        table_002._column_widths= [Decimal(0.5), Decimal(1), Decimal(0.5),Decimal(2), Decimal(5), Decimal(1),Decimal(1), Decimal(1), Decimal(1),Decimal(2)]

                        for key, value in resumen.items():
                               if key == 'Total en Letras':
                                     table_002.add(TableCell(Paragraph(str(key+':'+value['valor']), font_size=value['font_size'], horizontal_alignment=value['horizontal_alignment']), column_span=value['column_span']))
                               else:
                                table_002.add(TableCell(Paragraph(key, font_size=value['font_size'], horizontal_alignment=value['horizontal_alignment']), column_span=value['column_span']))
                                valor_decimal = Decimal(value['valor'])
                                valor_formateado = locale.currency(valor_decimal, grouping=True)

                                table_002.add(TableCell(Paragraph(str(valor_formateado), font_size=value['font_size'], horizontal_alignment=value['horizontal_alignment'])))
                                
                                       
                        table_002.set_padding_on_all_cells(Decimal(1), Decimal(1), Decimal(1), Decimal(1))  
                        table_002.outer_borders()  

                        return table_002

                except Exception as err:
                        print("Error En Query SQL.")
                        print(f"Unexpected {err=}, {type(err)=}")
                        sys.exit(0)


        def _build_itemized_description_table(self):  
                detalle = self['detalle']
                size = self['size']
                cantidad_linas = len(detalle)
               # numero_lineas = 32
                numero_lineas = size
                lineas_blanco = numero_lineas - cantidad_linas
                #if cantidad_linas < numero_lineas and lineas_blanco >=5:
                #        lineas_blanco =  2

                table_001 = Table(number_of_rows=numero_lineas, number_of_columns=10)  
                table_001._column_widths= [Decimal(0.5), Decimal(1), Decimal(0.5),Decimal(2), Decimal(5), Decimal(1),Decimal(1), Decimal(1), Decimal(1),Decimal(1)]
                for h in ["No.Item",  "Cant", "Uni.Med","Código","Descripción","Precio Unitario","Descuento SKU","Ventas no sujetas","Ventas exentas","Ventas gravadas"]:  
                        table_001.add(  
                        TableCell(  
                                Paragraph(h, font_color=X11Color("Black"),font_size = Decimal(6)),  
                                #background_color=HexColor("016934"),  
                                background_color=HexColor("BBBBBB"),  
                        )  
                        )  
                        

                
                odd_color = HexColor("FFFFFF")  
                even_color = HexColor("FFFFFF")  
                iva = Decimal(1.13)
                #for row_number, item in enumerate([('1',18.00,'59',"3001","Epson S015329 Black Ribbon 7.5 Million Characters", '5.91', '0','0','0','106.38')]):  
                for  item in detalle:  
                        c = even_color 
                        table_001.add(TableCell(Paragraph(str(item['numItem']),font_size = Decimal(7)), background_color=c))            
                        table_001.add(TableCell(Paragraph("{:,.2f}".format(item['cantidad']),font_size = Decimal(7)), background_color=c))  
                        table_001.add(TableCell(Paragraph(str(item['uniMedida']),font_size = Decimal(7)), background_color=c))  
                        table_001.add(TableCell(Paragraph(str(item['codigo']),font_size = Decimal(7)), background_color=c)) 
                        table_001.add(TableCell(Paragraph(str(item['descripcion']),font_size = Decimal(7)), background_color=c)) 
                        table_001.add(TableCell(Paragraph(str(round((item['precioUni']),4)),font_size = Decimal(7)), background_color=c)) 
                        table_001.add(TableCell(Paragraph(str(round(item['montoDescu'],4)),font_size = Decimal(7)), background_color=c)) 
                        table_001.add(TableCell(Paragraph(str(round(item['ventaNoSuj'],4)),font_size = Decimal(7)), background_color=c)) 
                        table_001.add(TableCell(Paragraph(str(round(item['ventaExenta'],4)),font_size = Decimal(7)), background_color=c)) 
                        table_001.add(TableCell(Paragraph("{:,.4f}".format(item['ventaGravada']),font_size = Decimal(7),horizontal_alignment=Alignment.RIGHT), background_color=c,)) 
                        
                        # Optionally add some empty rows to have a fixed number of rows for styling purposes
                
                for row_number in range(1, lineas_blanco):  
                        c = even_color if row_number % 2 == 0 else odd_color  
                        for _ in range(0, 10):  
                                 table_001.add(TableCell(Paragraph(" "), background_color=c))  
                
                
                table_001.set_padding_on_all_cells(Decimal(1), Decimal(1), Decimal(1), Decimal(1))  
                table_001.outer_borders()  
                return table_001




        def factura_pdf(self):
                
                data =self
                
                # Create document
                


                # Estraigo las medidas del Papel Carta  
                page_width: Decimal = PageSize.LETTER_PORTRAIT.value[0]
                page_height: Decimal = PageSize.LETTER_PORTRAIT.value[1]


                # creo una pagina tamaño carta con las medidas correctas

                page = Page(page_width,page_height)

                
                
                page_layout = SingleColumnLayout(page)

                #page_layout.vertical_margin = page_height
                #page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(0.00)

                # posicion X cuadro detalle
                page_layout._vertical_margin_top = Decimal(225)
                page_layout._vertical_margin_bottom = Decimal(0)
                page_layout._horizontal_margin = page.get_page_info().get_width() * Decimal(0.02)

                # ANCHO DEL CUADRO DEL DETALLE
                page_layout._column_width= page.get_page_info().get_height()- Decimal(200)

                



                margen_pagina = Decimal(50)
                height_of_textbox = Decimal(46)
                posiscion_y = page_height - margen_pagina- height_of_textbox - 40
                posiscion_x = Decimal(105)


                # == UBICACIONES DE IMAGENES ====================================================
                 
                
                IMAGE_PATH = Path(data['emisor']['logo'])
                tipoDte =data['identificacion']['tipoDte']
                posicionRcustomer = 540
                sizeRcustomer = 100
                if tipoDte == '05':
                      posicionRcustomer = 558
                      sizeRcustomer = 80        

                # === DIMENCION / POSISCION DE RECTANGULO  INFORMACION DE DOCUMENTO =================================================
                r: Rectangle = Rectangle(Decimal(posiscion_x + 200), Decimal(695), Decimal(300), Decimal(90)            
                )

                # === DIMENCION / POSISCION DE RECTANGULO  INFORMACION CLIENTE =================================================
                r_customer:Rectangle = Rectangle(Decimal(posiscion_x -95 ), Decimal(posicionRcustomer), Decimal(595), Decimal(sizeRcustomer)           # height
                )
                  # === DIMENCION / POSISCION DE RECTANGULO  DOCUMENTO REALCION  =================================================
                r_relariondoc:Rectangle = Rectangle(Decimal(posiscion_x -95 ), Decimal(538), Decimal(595), Decimal(20)            # height
                )

                # === DIMENCION / POSISCION DE RECTANGULO  INFORMACION EMPRESA =================================================

                rdes:Rectangle = Rectangle( Decimal(posiscion_x),                # x: 0 + page_margin
                        Decimal(posiscion_y),    # y: page_height - page_margin - height_of_textbox
                        Decimal(200),      # width: page_width - 2 * page_margin
                        Decimal(125), )

                #======== LOGO DE EMPRESA ========================================================================================================

                Image(        
                
                        image=IMAGE_PATH,
                        width=Decimal(100),        
                        height=Decimal(90),    
                        )  .paint(
                        page, Rectangle(Decimal(posiscion_x-99), Decimal(650), Decimal(120), Decimal(120))
                ) 
                
                
                #======================== DATOS DE EMPRESA ================================================================================================================


                

                #page.add_annotation(SquareAnnotation(rdes, stroke_color=HexColor("#000000")))

                m: Decimal = Decimal(5)
              

                Paragraph(data['emisor']['nombreComercial'], horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m, ).paint(page, rdes)
                
                Paragraph(data['emisor']['descActividad'], horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                padding_top=m+10,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m, ).paint(page, rdes)

                
                Paragraph(data['emisor']['direccion_complemento'], horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                padding_top=m+20,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m, ).paint(page, rdes)
                
                Paragraph("Tel."+data['emisor']['telefono'] + ' / ' +"WhatsApp: +503"+data['emisor']['whatsapp'], horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                padding_top=m+35,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m, ).paint(page, rdes)

               # Paragraph("WhatsApp: +503"+data['emisor']['whatsapp'], horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
               # padding_top=m+42,
               #         padding_left=m,
               #         padding_bottom=m,
               #         padding_right=m, ).paint(page, rdes)

                Paragraph(data['emisor']['correo'], horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                padding_top=m+42,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m, ).paint(page, rdes)
                
                Paragraph("Categoría:"+data['emisor']['categoria'], horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                padding_top=m+52,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m, ).paint(page, rdes)
                
                Paragraph("Tipo Establecimiento: Casa Matriz", horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                padding_top=m+62,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m, ).paint(page, rdes)
                
                Paragraph("NIT.:"+data['emisor']['nit'], horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                padding_top=m+72,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m, ).paint(page, rdes)
                
                Paragraph("NRC.:"+data['emisor']['nrc'], horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                padding_top=m+82,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m, ).paint(page, rdes)


                
                
                #Paragraph(data['emisor']['direccion']['complemento'], horizontal_alignment=Alignment.LEFT , font="Helvetica",font_size = Decimal(8)).paint(page, rdirec)
                #Paragraph("Tel."+data['emisor']['telefono'], horizontal_alignment=Alignment.LEFT , font="Helvetica",font_size = Decimal(8)).paint(page, Rectangle( Decimal(posiscion_x), Decimal(posiscion_y-45), Decimal(275 - 59 * 2),Decimal(100), ))
                #Paragraph("WhatsApp: +503 2555-3080.", horizontal_alignment=Alignment.LEFT , font="Helvetica",font_size = Decimal(8)).paint(page, Rectangle( Decimal(posiscion_x), Decimal(posiscion_y - 53), Decimal(275 - 59 * 2),Decimal(100), ))
                #Paragraph(data['emisor']['correo'], horizontal_alignment=Alignment.LEFT , font="Helvetica",font_size = Decimal(8)).paint(page, Rectangle( Decimal(posiscion_x), Decimal(posiscion_y-60), Decimal(275 - 59 * 2),Decimal(100), ))
                #Paragraph("Categoría: Gran contribuyente", horizontal_alignment=Alignment.LEFT , font="Helvetica",font_size = Decimal(8)).paint(page, Rectangle( Decimal(posiscion_x), Decimal(posiscion_y- 69), Decimal(275 - 59 * 2),Decimal(100), ))
                #Paragraph("Tipo Establecimiento: Casa Matriz", horizontal_alignment=Alignment.LEFT , font="Helvetica",font_size = Decimal(8)).paint(page, Rectangle( Decimal(posiscion_x), Decimal(posiscion_y-77), Decimal(275 - 59 * 2),Decimal(100), ))
                #Paragraph("NIT.:"+data['emisor']['nit'], horizontal_alignment=Alignment.LEFT , font="Helvetica",font_size = Decimal(8)).paint(page, Rectangle( Decimal(posiscion_x), Decimal(posiscion_y-85), Decimal(275 - 59 * 2),Decimal(100), ))
                #Paragraph("NCR.:"+data['emisor']['nrc'], horizontal_alignment=Alignment.LEFT , font="Helvetica",font_size = Decimal(8)).paint(page, Rectangle( Decimal(posiscion_x), Decimal(posiscion_y-92), Decimal(275 - 59 * 2),Decimal(100), ))



                # ================= RECTANGULO DE  INFORMACION DE DOCUMENTO =====================================================================================
                page.add_annotation(SquareAnnotation(r, stroke_color=HexColor("#000000")))
                # ================= RECTANGULO DE  INFORMACION DE CLIENTE =====================================================================================
                page.add_annotation(SquareAnnotation(r_customer, stroke_color=HexColor("#000000")))
                if tipoDte == '05':
                        # ===============================RECTANGULO DOC RELACION ===================================
                        page.add_annotation(SquareAnnotation(r_relariondoc, stroke_color=HexColor("#000000")))


                codigo_generacion =data['identificacion']['codigoGeneracion']
                estado = data['identificacion']['estado']
                Sello_recepcion = data['identificacion']['selloRecibido']
                Numero_control = data['identificacion']['numeroControl']
                mod = data['identificacion']['tipoModelo']
                modelo = ''
                if mod == 1:
                       modelo = 'Previo'         
                elif mod == 2:
                        modelo = 'Diferido'
                Modelo_facturación = modelo

                tip_t = data['identificacion']['tipoContingencia']
                if tip_t == None:
                   Tipo_transmision= 'Normal'
                else:
                   Tipo_transmision= 'Contingencia'     

                codigo_cliente = str(data['receptor']['codigo'])
                Hora_emision = str(data['identificacion']['horEmi'])
                Version_Json = str(data['identificacion']['version'])

                Fecha_emisions = str(data['identificacion']['fecEmi'])
                fecha = datetime.strptime(Fecha_emisions, '%Y-%m-%d')
                fecha_str = fecha.strftime('%d-%m-%Y')
                Fecha_emision = fecha_str

                razon_social= str(data['receptor']['codigo']) + ' ' + str(data['receptor']['nombre']) 
                nombreComercial =  str(data['receptor']['nombreComercial'])
                act_economica = str(data['receptor']['actividad_economica'])
                correo_cliente = str(data['receptor']['correo'])
                direccion_cliente = str(data['receptor']['complemento'])
                municipio_cliente  = data['receptor']['municipio']
                vendedor = data['receptor']['vendedor']  
                rutaEntrega = data['receptor']['rutaEntrega']  if   data['receptor']['rutaEntrega']  else 'CXC'                            
                incoterms = data['receptor']['incoterms']
                departamento_cliente =  data['receptor']['departamento']
                NIT_cliente = str(data['receptor']['numDocumento'])
                NCR_cliente= str(data['receptor']['nrc'])
                if NCR_cliente == 'None':
                      NCR_cliente= ''
                Telefono_cliente = str(data['receptor']['telefono'])
                if len(Telefono_cliente) < 8 or Telefono_cliente == '00000000':
                        Telefono_cliente = ''
                cond_p = data['identificacion']['condicionOperacion']
                nombreDocumento = data['identificacion']['nombreDocumento']
                condicion= ''
                if cond_p== 1:
                      condicion = 'Contado'          
                elif cond_p == 2 :
                        condicion = 'Credito'
                else:
                        condicion = 'Otro'
                Formapago_cliente = condicion
                Moneda= str(data['identificacion']['tipoMoneda'])

                ## 2025-03-24: Asignar la Orden de Compra a los documentos, Verifica si hay un valor antes de asignarlo
                oCompra = data['apendice']['valor'] if data.get('apendice') and 'valor' in data['apendice'] else ""

                Documento_interno = data['identificacion']['Documento_interno']
                fecha_doc = data['identificacion']['fecEmi'] 
                #fecha_emi = fecha_doc.strftime('%Y-%m-%d')
                fecha_emi = fecha_doc

                docRelCodigoGeneracion = data['documentoRelacionado']['codigoGeneracion'] if data['documentoRelacionado'] else None
                numeroControl = data['documentoRelacionado']['numeroControl'] if data['documentoRelacionado'] else None
                #docRelfecEmi = data['documentoRelacionado']['fecEmi'] if data['documentoRelacionado'] else None
                if data['documentoRelacionado']:
                        docRelFecha_emisions = str( data['documentoRelacionado']['fecEmi'])
                        docRelfecha = datetime.strptime(docRelFecha_emisions, '%Y-%m-%d')
                        docRelfecha_str = docRelfecha.strftime('%d-%m-%Y')
                        docRelFecha_emision = docRelfecha_str
                else:
                      docRelFecha_emision = None

                urlbase = 'https://webapp.dtes.mh.gob.sv/consultaPublica?ambiente=01&codGen=A7FC1FBE-E27E-45A8-9F14-166C2861E98E&fechaEmi=2022-10-11'
                urlval1 = 'https://webapp.dtes.mh.gob.sv/consultaPublica?ambiente=01&codGen='+codigo_generacion+'&fechaEmi='+fecha_emi


                ## =================================================CODIGOS QR =====================================================================================================================================
                Barcode(
                        urlval1,
                        type=BarcodeType.QR,
                        width=Decimal(80),
                        height=Decimal(80),
                ).paint(
                        page, Rectangle(Decimal(posiscion_x + 122), Decimal(660), Decimal(80), Decimal(80))
                )

               
                Paragraph("Portal Ministerio de Hacienda", horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                ).paint(page, Rectangle(Decimal(posiscion_x + 125), Decimal(585), Decimal(80), Decimal(80)))

                Barcode(
                        codigo_generacion,
                        type=BarcodeType.QR,
                        width=Decimal(54),
                        height=Decimal(54),
                ).paint(
                        page, Rectangle(Decimal(posiscion_x + 290), Decimal(635), Decimal(64), Decimal(64))
                )
                Paragraph("Código generación", horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                ).paint(page, Rectangle(Decimal(posiscion_x + 296), Decimal(567), Decimal(80), Decimal(80)))

                Barcode(
                        Sello_recepcion,
                        type=BarcodeType.QR,
                        width=Decimal(54),
                        height=Decimal(54),
                ).paint(
                        page, Rectangle(Decimal(posiscion_x + 360), Decimal(635), Decimal(64), Decimal(64))
                )

                Paragraph("Sello de recepción", horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                ).paint(page, Rectangle(Decimal(posiscion_x + 368), Decimal(567), Decimal(80), Decimal(80)))

                Barcode(
                        Numero_control,
                        type=BarcodeType.QR,
                        width=Decimal(54),
                        height=Decimal(54),
                ).paint(
                        page, Rectangle(Decimal(posiscion_x + 428), Decimal(635), Decimal(64), Decimal(64))
                )

                Paragraph("Número de control", horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                ).paint(page, Rectangle(Decimal(posiscion_x + 438), Decimal(567), Decimal(80), Decimal(80)))




                # ========================= DATOS DE DOCUMENTOS ================================================================================================================
                m: Decimal = Decimal(5)
                n:Decimal = Decimal(30)

                Paragraph("DOCUMENTO TRIBUTARIO ELECTRÓNICO", horizontal_alignment=Alignment.CENTERED,font="Helvetica-Bold",font_size = Decimal(9),
                padding_top=m,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m, ).paint(page, r)
                Paragraph(nombreDocumento, horizontal_alignment=Alignment.CENTERED,font="Helvetica-Bold",font_size = Decimal(10),
                padding_top=m+11,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)

                Paragraph("Código generación:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+25,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)



                Paragraph(codigo_generacion, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+25,
                        padding_left=m+80,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)

                Paragraph("Sello de recepción:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+35,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)
                Paragraph(Sello_recepcion, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+35,
                        padding_left=m+80,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)

                Paragraph("Número de control:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+45,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)

                Paragraph(Numero_control, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+45,
                        padding_left=m+80,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)

                Paragraph("Modélo facturación:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+55,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)

                Paragraph(Modelo_facturación, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+55,
                        padding_left=m+80,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)


                Paragraph("Tipo de transmisión:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+65,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)


                Paragraph(Tipo_transmision, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+65,
                        padding_left=m+80,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)

                Paragraph("Hora de emisión:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+75,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)

                Paragraph(Hora_emision, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+75,
                        padding_left=m+80,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)




                Paragraph("Versión del Json:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+55,
                        padding_left=m+135,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)


                Paragraph(Version_Json, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+55,
                        padding_left=m+205,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)

                Paragraph("Fecha emisión:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+65,
                        padding_left=m+135,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)

                Paragraph(Fecha_emision, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+65,
                        padding_left=m+205,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)


                Paragraph("Documento interno:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+75,
                        padding_left=m+135,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)

                Paragraph(Documento_interno, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+75,
                        padding_left=m+213,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r)


                #page_layout.add(_build_invoice_information())

                #+++++++++++++++++++++++++++++++++++++++ DATOS DE CLIENTE =============================================================

                razon_left = 65        
                vertical_position = m

                Paragraph("Cliente:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(razon_social, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m,
                        padding_left=m+razon_left,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)

                vertical_position += 10 

                Paragraph("Nombre Comercial:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(nombreComercial, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m+78,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                
                vertical_position += 10 


                Paragraph("Act. económica:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(act_economica, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m+65,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                vertical_position += 10 
                Paragraph("Correo:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(correo_cliente, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m+65,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)

                vertical_position +=10
                Paragraph("Dirección:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(direccion_cliente, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(6),
                padding_top=vertical_position,
                        padding_left=m+65,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                vertical_position +=10

                page_layout.add(Paragraph(" "))


                Paragraph("Municipio:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(7),
                padding_top=vertical_position,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(municipio_cliente, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(7),
                padding_top=vertical_position,
                        padding_left=m+65,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                
                
                Paragraph("Vendedor:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(7),
                padding_top=vertical_position,
                        padding_left=m+200,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(vendedor, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(7),
                padding_top=vertical_position,
                        padding_left=m+240,
                        padding_bottom=m,
                        padding_right=m,
                ).paint(page, r_customer)


                Paragraph("Entrega:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(7),
                padding_top=vertical_position,
                        padding_left=m+270,
                        padding_bottom=m,
                        padding_right=m,
                ).paint(page, r_customer)
                Paragraph(rutaEntrega, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(7),
                padding_top=vertical_position,
                        padding_left=m+300,
                        padding_bottom=m,
                        padding_right=m,
                ).paint(page, r_customer)
                vertical_position += 10 
                Paragraph("Departamento:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(7),
                padding_top=vertical_position,
                        padding_left=m,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(departamento_cliente, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(7),
                padding_top=vertical_position,
                        padding_left=m+65,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)

                ## 2025-03-24: Se agrega leyenda de Orden de Compra para Calleja
                if oCompra != "":
                        Paragraph("Orden Compra:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(7),
                        padding_top=vertical_position,
                                padding_left=m+170,
                                padding_bottom=m,
                                padding_right=m,
                        ).paint(page, r_customer)
                        Paragraph(oCompra, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(7),
                        padding_top=vertical_position,
                                padding_left=m+230,
                                padding_bottom=m,
                                padding_right=m,
                        ).paint(page, r_customer)                                       
                ##
                 
                if nombreDocumento =='Facturas de exportación':
                        Paragraph("Incoterms:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(7),
                        padding_top=vertical_position,
                                padding_left=m+150,
                                padding_bottom=m,
                                padding_right=m,

                        ).paint(page, r_customer)
                        Paragraph(incoterms, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(7),
                        padding_top=vertical_position,
                                padding_left=m+190,
                                padding_bottom=m,
                                padding_right=m,

                        ).paint(page, r_customer)
                        
                vertical_position = m
                Paragraph("NIT:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m+380,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(NIT_cliente, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m+430,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)

                vertical_position += 10 

                Paragraph("NRC:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m+380,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(NCR_cliente, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=vertical_position,
                        padding_left=m+430,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)



                Paragraph("Teléfono:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+29,
                        padding_left=m+380,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(Telefono_cliente, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+29,
                        padding_left=m+430,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)


                Paragraph("Forma pago:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+44,
                        padding_left=m+380,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(Formapago_cliente, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+44,
                        padding_left=m+430,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)


                Paragraph("Moneda:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(8),
                padding_top=m+55,
                        padding_left=m+380,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)
                Paragraph(Moneda, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(8),
                padding_top=m+55,
                        padding_left=m+430,
                        padding_bottom=m,
                        padding_right=m,

                ).paint(page, r_customer)

                if tipoDte == '05':
                        Paragraph("Documento Relacionado:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(7),
                        padding_top=vertical_position-10,
                                padding_left=m,
                                padding_bottom=m,
                                padding_right=m,

                        ).paint(page, r_relariondoc)
                        Paragraph(docRelCodigoGeneracion, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(7),
                        padding_top=vertical_position-10,
                                padding_left=m+100,
                                padding_bottom=m,
                                padding_right=m,

                        ).paint(page, r_relariondoc)


                        
                        Paragraph("Número de Control:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(7),
                        padding_top=vertical_position-10,
                                padding_left=m+250,
                                padding_bottom=m,
                                padding_right=m,

                        ).paint(page, r_relariondoc)
                        Paragraph(numeroControl, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(7),
                        padding_top=vertical_position-10,
                                padding_left=m+320,
                                padding_bottom=m,
                                padding_right=m,

                        ).paint(page, r_relariondoc)
                        

                        Paragraph("Fecha:", horizontal_alignment=Alignment.LEFT,font="Helvetica-Bold",font_size = Decimal(7),
                        padding_top=vertical_position-10,
                                padding_left=m+450,
                                padding_bottom=m,
                                padding_right=m,

                        ).paint(page, r_relariondoc)
                        Paragraph(docRelFecha_emision, horizontal_alignment=Alignment.LEFT,font="Helvetica",font_size = Decimal(7),
                        padding_top=vertical_position-10,
                                padding_left=m+490,
                                padding_bottom=m,
                                padding_right=m,

                        ).paint(page, r_relariondoc)

                # Accediendo a los valores con get para manejar posibles valores faltantes
                pagina_actual = data.get('pagina_actual',1)   # Predeterminado a 1 si no existe
                pagina_final = data.get('total_paginas',1)
                size = data.get('size', 46)                   # Predeterminado a 46 si no existe
                # Ajustando el tamaño en función del número de páginas
                if pagina_final > 1:
                            size = 40 if pagina_actual < pagina_final else 25

                # Bloque try para manejar errores en el proceso de agregar tablas o contenido
                try:              
                        # Agrega la tabla de descripción detallada usando el tamaño ajustado     
                        page_layout.add(ger_pdf._build_itemized_description_table({
                              'detalle':data.get('cuerpoDocumento',[]), # Predeterminado a lista vacía si falta
                              'size':size
                        }))
                        # Agrega la tabla del pie de página si estamos en la última página
                        if pagina_actual == pagina_final:
                                page_layout.add(ger_pdf._footer_page_table({'resumen': data.get('resumen', '')}))  # Predeterminado a cadena vacía     #page_layout.add(ger_pdf._footer_page_table({'resumen':data['resumen']}))
                        
                        # Añadiendo el número de página
                        Paragraph(
                              f"Hoja: {pagina_actual} de {pagina_final}", 
                              horizontal_alignment=Alignment.CENTERED , 
                              font="Helvetica",
                              font_size = Decimal(8)
                              ).paint(page, Rectangle( Decimal(posiscion_x), Decimal(posiscion_y-743), Decimal(432),Decimal(100), ))
                        # Verifica el estado del documento y pinta "ANULADO" si es inválido
                        if estado == 'INVALIDADO':
                                Paragraph(
                                        "ANULADO",
                                        font_color=RGBColor(1, 0, 0), 
                                        font_size=58,
                                        font="Courier-Bold",
                                ).paint(
                                        page, Rectangle(Decimal(posiscion_x+30), Decimal(250), Decimal(120), Decimal(120))
                                        )
                except Exception as err:
                #        print("Error en PDF.")
                #        print(f"Unexpected {err=}, {type(err)=}")
                #        sys.exit(0)
                        print(f"Error al generar la página PDF: {err}")

                return page

        

        def generarPdf(request, codigoGeneracion):
                documentorel={}
                documentos = Documentos.objects.filter(codigoGeneracion = codigoGeneracion).first()
                logger.error(f"Documentos a evaluar: {documentos}")
                if documentos.numeroDocumento_rel_guid:
                        documento_rel = Documentos.objects.filter(codigoGeneracion = documentos.numeroDocumento_rel_guid).first()
                        logger.error(f"Evaluando documento relacionado: {documento_rel}")
                        documentorel = {'codigoGeneracion':documento_rel.codigoGeneracion,'numeroControl':documento_rel.numeroControl
                                        ,'fecEmi':documento_rel.fecEmi}
                        logger.error(f"Datos documento relacionado: {documentorel}")
                else:
                      documentorel = None
                

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
                                                'ventaGravada':ventaGravada, 'tributos':None,'psv':doc.psv,
                                                'noGravado':doc.noGravado,'ivaItem':doc.ivaItem })
                    
                # ==================== DATOS  RESUMEN =======================================================================
                pagos = Pagos.objects.filter(codigogeneracion_doc = codigoGeneracion).first()
                logger.info(f" datos: {lineas}", exc_info=True)
                traceback.print_exc()
               
                resumen = {
                            'totalNoSuj': {
                                'valor': documentos.totalNoSuj,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'totalExenta': {
                                'valor': documentos.totalExenta,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9,
                                
                            },
                            'totalGravada': {
                                'valor': documentos.totalGravada,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'Suma Total Operación (+)': {
                                'valor': documentos.subTotalVentas if documentos.tipodocumento_id not in ['14','07'] else documentos.totalSujetoRetenido,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 3
                            },
                            'descuNoSuj': {
                                'valor': documentos.descuNoSuj,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'descuExenta': {
                                'valor': documentos.descuExenta,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'Monto Total Descuento(-)': {
                                'valor': documentos.descuGravada,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'porcentajeDescuento': {
                                'valor': documentos.porcentajeDescuento,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'totalDescu': {
                                'valor': documentos.totalDescu,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT ,
                                'column_span': 9

                            },
                            
                            'Sub Total(=)': {
                                'valor': documentos.montoTotalOperacion,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'IVA Percibido(+)': {
                                'valor': documentos.ivaPerci1,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'IVA Retenido(-)': {
                                'valor': documentos.ivaRete1 ,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'Retencion Renta (-)': {
                                'valor': documentos.reteRenta,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'Monto Total de la Operación (=)': {
                                'valor': documentos.totalPagar,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'Otros Montos no Afectos(+)': {
                                'valor': documentos.totalNoGravado,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'TOTAL A PAGAR(=)': {
                                'valor': documentos.totalPagar,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'Total en Letras': {
                                'valor': documentos.totalLetras,
                                'font': None,
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.LEFT,
                                'column_span': 6
                            },
                            'IVA(+)': {
                                'valor': documentos.iva,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'saldoFavor': {
                                'valor': documentos.saldoFavor,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'condicionOperacion': {
                                'valor': documentos.condicionOperacion.codigo,
                                'font': None,
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.LEFT,
                                'column_span': 6
                            },
                             'tipoDocumento': {
                                'valor': documentos.tipodocumento_id,
                                'font': None,
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.LEFT,
                                'column_span': 6
                            },
                            'flete': {
                                'valor': documentos.flete,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            'seguro': {
                                'valor': documentos.seguro,
                                'font': "Helvetica-Bold",
                                'font_size': Decimal(7),
                                'horizontal_alignment': Alignment.RIGHT,
                                'column_span': 9
                            },
                            
                        }
                key_for_resumen = ('Total en Letras',
                                'Suma Total Operación (+)',
                                'Monto Total Descuento(-)',
                                'Retencion Renta (-)',
                                'IVA(+)',
                                'Sub Total(=)',
                                'IVA Percibido(+)',
                                'IVA Retenido(-)',
                                'Monto Total de la Operación (=)',
                                'Otros Montos no Afectos(+)',
                                'flete',
                                'seguro',
                                'TOTAL A PAGAR(=)',
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
                                ### 2024-09-19: Se realiza cambio de la variable receptor_origen.municipo.nombre a receptor_origen.munidistrito.nombre para que refleje los nuevos municipios
                                #'municipio': documentos.emisor_id.munidistrito.nombre,                                 
                                'direccion_complemento': documentos.emisor_id.direccion_complemento,
                                'telefono': documentos.emisor_id.telefono,
                                'correo': documentos.emisor_id.correo,
                                'codEstableMH':documentos.emisor_id.codestablemh,'codEstable':documentos.emisor_id.codestable,
                                'codPuntoVentaMH':documentos.emisor_id.codpuntoventamh,'codPuntoVenta':documentos.emisor_id.codpuntoventa ,
                                'categoria':documentos.emisor_id.categoria,'whatsapp':documentos.emisor_id.whatsapp,'logo':documentos.emisor_id.company.logo.path }

                # Determinar cliente y factura
                receptor = documentos.receptor_id.codigo if documentos.receptor_id else documentos.proveedor_id.codigo if documentos.proveedor_id else None
                factura = documentos.num_documento

                if receptor == '16051' or (documentos.receptor_origen and documentos.receptor_origen.codigo == '16051'):
                        info_cliente = ConsecutivosSF.obtener_info_cliente_desde_sqlserver(receptor, documentos.emisor_id.id, factura)
                else:

                        info_cliente = {
                                'codigo': receptor, ## documentos.receptor_id.codigo if documentos.receptor_id else documentos.proveedor_id.codigo if documentos.proveedor_id else None,
                                'tipoDocumento':  documentos.receptor_id.tipodocumento.nombre if documentos.receptor_id else documentos.proveedor_id.nombre if documentos.proveedor_id else None,
                                                'numDocumento':documentos.receptor_id.numdocumento if documentos.receptor_id else documentos.proveedor_id.numdocumento if documentos.proveedor_id else None,
                                                'nrc':documentos.receptor_id.nrc if documentos.receptor_id and documentos.receptor_id.nrc   else documentos.proveedor_id.nrc if documentos.proveedor_id else None,
                                'nombre':documentos.receptor_id.nombre if documentos.receptor_id else documentos.proveedor_id.nombre if documentos.proveedor_id else None,
                                'codActividad':documentos.receptor_id.codactividad.codigo if documentos.receptor_id else documentos.proveedor_id.codactividad.codigo if documentos.proveedor_id else None,
                                'actividad_economica':documentos.receptor_id.codactividad.codigo +":"+ documentos.receptor_id.codactividad.nombre if documentos.receptor_id else
                                                                documentos.proveedor_id.codactividad.codigo +":"+ documentos.proveedor_id.codactividad.nombre if documentos.proveedor_id else None,
                                'nombreComercial': documentos.receptor_origen.codigo +':'+ documentos.receptor_origen.nombrecomercial if documentos.receptor_origen else  documentos.receptor_id.nombrecomercial
                                                                if documentos.receptor_id else 
                                                                documentos.proveedor_id.codigo +':'+ documentos.proveedor_id.nombrecomercial
                                                                if documentos.proveedor_id else None,
                                'codPais':documentos.receptor_id.codpais.codigo if documentos.receptor_id else documentos.proveedor_id.codpais.codigo if documentos.proveedor_id else None,
                                'tipoPersona':documentos.receptor_id.tipopersona.codigo if documentos.receptor_id else documentos.proveedor_id.tipopersona.codigo if documentos.proveedor_id else None,
                                'tipoReceptor':documentos.receptor_id.tiporeceptor if documentos.receptor_id else documentos.proveedor_id.tiporeceptor if documentos.proveedor_id else None,
                                'departamento':documentos.receptor_origen.departamento.nombre if documentos.receptor_origen else documentos.receptor_id.departamento.nombre
                                                        if documentos.receptor_id else documentos.proveedor_id.departamento.nombre if documentos.proveedor_id else None, 
                                'vendedor': documentos.vendedor_id ,
                                #       'municipio':documentos.receptor_origen.municipio.nombre if documentos.receptor_origen else documentos.receptor_id.municipio.nombre
                                #                         if documentos.receptor_id else documentos.proveedor_id.municipio.nombre 
                                #                         if documentos.proveedor_id else None,
                                ### 2024-09-19: Se realiza cambio de la variable receptor_origen.municipo.nombre a receptor_origen.munidistrito.nombre para que refleje los nuevos municipios
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
                ## 2025-03-24: Para agregar el valor de la Orden de Compra 
                apendice = {'campo':'OrdenCompra','etiqueta':'Número de Orden de Compra','valor': documentos.orden_compra} if documentos.orden_compra else None
             
                pdf = Document()

                max_lineas =35
               
                cantidad_lineas = len(lineas)
                if cantidad_lineas >= max_lineas or cantidad_lineas >= 26:
                     total_pages = 0
                     int_pages =   math.trunc(cantidad_lineas/ max_lineas)
                     dec_page = (cantidad_lineas/ max_lineas) - int_pages
                     
                     if(dec_page>0.0):
                        total_pages = int_pages + 1

                     else:
                        total_pages = int_pages
                     if cantidad_lineas > 45:   
                        max_lineas = 45
                     detalle_list = list(ger_pdf.divide_chunks(lineas, max_lineas))
                   #  n= round(cantidad_lineas/ total_pages )
                   #  detalle_list=[lineas[i:i + n] for i in range(0, len(lineas), n)]
                     for idx, x in enumerate(detalle_list):
                        pagina_actual = idx+1
                        dic_final = {'emisor':info_empresa,'receptor':info_cliente,'cuerpoDocumento':x,'resumen':resumen_copia,'identificacion':identificacion
                        ,'pagina_actual':pagina_actual,'total_paginas':total_pages,'size':max_lineas+1,'documentoRelacionado':documentorel,'apendice':apendice}
                        page = ger_pdf.factura_pdf(dic_final)
                        pdf.add_page(page)
                else:
                        pagina_actual = 1
                        total_pages = 1
                        dic_final = {'emisor':info_empresa,'receptor':info_cliente,'cuerpoDocumento':lineas,'resumen':resumen_copia,'identificacion':identificacion
                        ,'pagina_actual':pagina_actual,'total_paginas':total_pages,'size':26,'documentoRelacionado':documentorel,'apendice':apendice}
                        page = ger_pdf.factura_pdf(dic_final)
                        pdf.add_page(page)        
                
                file_path = codigoGeneracion + ".pdf"
                pdf_buffer = BytesIO()
                #with open(file_path, "wb") as file:
                PDF.dumps(pdf_buffer,pdf)
                
                response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=' + codigoGeneracion + '.pdf'

                return response

        def divide_chunks(l, n):     
                # looping till length l
                for i in range(0, len(l), n):
                        yield l[i:i + n]