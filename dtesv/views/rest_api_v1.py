from venv import logger
from dtesv.processes import create_pdf
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from dtesv.models import Receptor, Documentos, DocumentosDetalle,Vendedores,User,proveedores,Company,Parametros
from dtesv.serializers import ReceptorSerializer, DocumentosSerializer, DocumentosDetalleSerializer,ProveedorSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import Http404 ,StreamingHttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView,RetrieveUpdateAPIView
from dtesv.processes import DataProcessor,validate_schema,InvalidProcessor,procesorLote,create_json,constructor_dicionario
from dtesv.processes.procesorDocMh import MainProcessor
from dtesv.processes import validate_doc_no_proc
from rest_framework import mixins,generics
from datetime import datetime, timedelta
import dtesv.views.sent_email as enviar_email
import json
from django.utils import timezone
import zipfile
from dtesv.tasks import procesar_documentos,invalidacion_documento
import os
from django.core.exceptions import ObjectDoesNotExist

TOKEN_EXPIRATION = timedelta(minutes=5)

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # Llama al método post de la clase padre para obtener el token
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            # El inicio de sesión fue exitoso
            user = User.objects.get(username=request.data['username'])
            token, _ = Token.objects.get_or_create(user=user)

            # Verifica si el token ha expirado
            if token.created and not self.expires_in(token):
                # El token ha expirado, elimina el token anterior
                Token.objects.filter(user=user).delete()

                # Crea un nuevo token y actualiza la respuesta
                new_token = Token.objects.create(user=user)
                response.data['token'] = new_token.key

        return response

    def expires_in(self, token):
        # Agrega la lógica para verificar si el token ha expirado
        # Puedes usar la lógica que ya tienes en tu ExpiringTokenAuthentication
        # o personalizarla según tus necesidades
        time_elapsed = timezone.now() - token.created
        return time_elapsed < TOKEN_EXPIRATION




class ReceptorDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, codigo):
        try:
            return Receptor.objects.get(codigo=codigo)
        except Receptor.DoesNotExist:
            raise Http404

    def get(self, request, codigo, format=None):
        receptor = self.get_object(codigo)
        serializer = ReceptorSerializer(receptor)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ReceptorSerializer(data=request.data)
        
         
      #  validate_schema.schemaValidate({'json':request.data}).validate_schema_receptor()
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "Receptor": serializer.data["codigo"],
                "Nombre": serializer.data["nombre"],
                "message": "Creado Exitosamente"
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_200_OK)

    def put(self, request, codigo, format=None):
        receptor = self.get_object(codigo)
        serializer = ReceptorSerializer(receptor, data=request.data, partial=True)  # Use partial=True
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "Receptor": serializer.data["codigo"],
                "Nombre": serializer.data["nombre"],
                "message": "Actualizado Exitosamente"
            }
            result = validate_doc_no_proc.buscar_documentos.no_procesados(self,serializer.data["codigo"])
            response_data['reproceso_documentos']=result
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, codigo, format=None):
        receptor = self.get_object(codigo)
        receptor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProveedorDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, codigo):
        try:
            return proveedores.objects.get(codigo=codigo)
        except proveedores.DoesNotExist:
            raise Http404

    def get(self, request, codigo, format=None):
        proveedor = self.get_object(codigo)
        serializer = ProveedorSerializer(proveedor)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProveedorSerializer(data=request.data)
        
         
      #  validate_schema.schemaValidate({'json':request.data}).validate_schema_receptor()
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "Proveedor": serializer.data["codigo"],
                "Nombre": serializer.data["nombre"],
                "message": "Creado Exitosamente"
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_200_OK)

    def put(self, request, codigo, format=None):
        proveedor = self.get_object(codigo)
        serializer = ProveedorSerializer(proveedor, data=request.data, partial=True)  # Use partial=True
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "Proveedor": serializer.data["codigo"],
                "Nombre": serializer.data["nombre"],
                "message": "Actualizado Exitosamente"
            }
            result = validate_doc_no_proc.buscar_documentos.no_procesados(self,serializer.data["codigo"])
            response_data['reproceso_documentos']=result
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, codigo, format=None):
        proveedor = self.get_object(codigo)
        proveedores.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentosCreateAPIView(CreateAPIView):
    serializer_class = DocumentosSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        codigoGeneracion = data['codigoGeneracion']
        fecha_hora_emision = datetime.strptime(data['fecEmi'] + ' ' + data['horEmi'], "%Y-%m-%d %H:%M:%S")
        fecha_hora_actual = datetime.now()

        #diferencia = fecha_hora_actual - fecha_hora_emision
        #if timedelta(days=0) <= diferencia <= timedelta(days=1):
        serializer = self.get_serializer(data =request.data)
        if serializer.is_valid():
            data = serializer.data        
            result= self.perform_create(request,serializer)
            if result.data['result_sent_dte']:
                data.update({'result_sent_dte':result.data['result_sent_dte'] })
            headers = self.get_success_headers(serializer.data)
            status_code  = status.HTTP_201_CREATED
            response_data = {
            'message': 'Solicitud exitosa' if status_code == status.HTTP_201_CREATED else 'Error en la solicitud',
            'data': data
        }
        else:
            status_code  = status.HTTP_400_BAD_REQUEST
            headers = self.get_success_headers(serializer.data)
            response_data = {
                "error": "Error en la validación del documento",
                "errors": serializer.errors
                }
        
        #else:
            
    #        data = {            
    #        'documento': codigoGeneracion,
    #        'ERROR': '''El Documento esta fuera de la Fecha de Envio \n
    #                    se deben especificar los campos tipoContingencia y motivoContin''',
    #             }
    #        headers = self.get_success_headers(data)
    #        status_code  = status.HTTP_400_BAD_REQUEST
        
        return Response(response_data, status=status_code , headers=headers)

    def perform_create(self, request,serializer):
        documento_data = serializer.validated_data
        detalle_data = documento_data.pop('detalle', [])
       
        documento = Documentos.objects.create(**documento_data)

        for detalle_item in detalle_data:
            detalle_item['codigoGeneracion_id'] = documento
            DocumentosDetalle.objects.create(**detalle_item)
            
        if not documento_data['en_contingencia']:    
            
            #result = MainProcessor(request, documento.codigoGeneracion).run()
            #result = MainProcessor(request, documento.codigoGeneracion).run()
            result = procesar_documentos.delay(documento.codigoGeneracion)
            
             
        else:
            result = "Documento Ingresado en Contingencia"
        response_data = {
            'result_sent_dte':result.id if hasattr(result, 'id') else result,
            'documento': serializer.data,
            'detalle': detalle_data,
        }
        #if 'estado' in  result:
        #    if result['estado'] == 'PROCESADO':
        #        result_email = send_emails_for_pending_documents.delay(documento.codigoGeneracion)

        return Response(response_data, status=status.HTTP_201_CREATED)
    


class DocumentosRetrieveAPIView(RetrieveAPIView):
    serializer_class = DocumentosSerializer
    queryset = Documentos.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        codigo_generacion = self.kwargs['codigo_generacion']
        try:
            documento = self.queryset.get(codigoGeneracion=codigo_generacion)
            return documento
        except Documentos.DoesNotExist:
            raise Http404

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['show_detalle'] = True  # Incluye el detalle en la respuesta
        return context

class DocumentosRetrieveAPIView(RetrieveAPIView):
    serializer_class = DocumentosSerializer
    queryset = Documentos.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        codigo_generacion = self.kwargs['codigo_generacion']
        try:
            documento = self.queryset.get(codigoGeneracion=codigo_generacion)
            return documento
        except Documentos.DoesNotExist:
            raise Http404

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['show_detalle'] = True  # Incluye el detalle en la respuesta
        return context

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

class DocumentosUpdateCompleteAPIView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Documentos.objects.all()
    serializer_class = DocumentosSerializer
    lookup_url_kwarg = 'codigo_generacion'  # Indicar que se utiliza "codigo_generacion" como identificador

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        documento = self.get_object()
        if documento.estado != "PROCESADO":
            serializer = DocumentosSerializer(documento, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
               # result = DataProcessor.process_data_document(self,request, documento.codigoGeneracion)
                result = procesar_documentos.delay(documento.codigoGeneracion)
                response_data = {
                    "message": "Documento actualizado exitosamente",
                    "documento": documento.codigoGeneracion,
                    'result_sent_dte': result.id,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                "message": str(serializer.errors),
                "documento": documento.codigoGeneracion,
                
            }
                
        else:
            response_data = {
                "message": "El documento ya fue procesado y no se puede editar",
                "documento": documento.codigoGeneracion,
                
            }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

  #--- API APRA INVALIDACION------------------------------------  
class InvalidacionClass(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data

        
        
         
        # Llamar al método InvalidProcessor con el diccionario completo
        #processor = InvalidProcessor.invalid_document(self,data)        
        processor =  invalidacion_documento.delay(data)

        response_data = {
            "message": "Documento Invalidador",
            "documento": data['identificacion']['codigoGeneracion'],
            "result_processor": processor.id
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class DocumentoClienteTelefono(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, telefono, format=None):
        
        # Obtiene el número de teléfono del cliente desde la solicitud GET
        telefono_cliente = telefono
        
        if not telefono_cliente:
            return Response({'error': 'Debe proporcionar un número de teléfono.'}, status=status.HTTP_200_OK)
        
        # Busca todos los receptores con el número de teléfono especificado
        receptores = Receptor.objects.filter(telefono=telefono_cliente)
         
        
        if receptores:
            # Si solo hay un receptor con ese número de teléfono, buscar el último documento procesado
            receptor = receptores.first()
            try:
                ultimo_documento = Documentos.objects.filter(receptor_id=receptor.codigo, estado='PROCESADO',enviado_movil =False).latest('condicionOperacion')
                ultimo_documento.enviado_movil = True
                ultimo_documento.save()
                return Response({'codigoGeneracion': ultimo_documento.codigoGeneracion}, status=status.HTTP_200_OK)
            except Documentos.DoesNotExist:
                return Response({'error': 'No se encontraron documentos procesados para este receptor. '+receptor.pk}, status=status.HTTP_200_OK)
         
        else:
            try:
                # Si no se encontraron receptores, busca el teléfono en el modelo Vendedores
                vendedor = Vendedores.objects.get(telefono=telefono_cliente)
                # Retorna el código y el nombre del vendedor
                return Response({'tipo':'vendedor','codigo': vendedor.codigo, 'nombre': vendedor.nombre}, status=status.HTTP_200_OK)
            except Vendedores.DoesNotExist:
                return Response({'error': 'No se encontró un receptor ni un vendedor con ese número de teléfono.'}, status=status.HTTP_200_OK)
            
    
class DocumentoCliente(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, codigo, format=None):
        
        codigo_cliente = codigo
        
        if not codigo_cliente:
            return Response({'error': 'Debe proporcionar un codigo de cliente.'}, status=status.HTTP_200_OK)
        
        receptores = Receptor.objects.filter(codigo=codigo_cliente)
        if receptores:
            try:
            # Si solo hay un receptor con ese número de teléfono, buscar el último documento procesado
                receptor = receptores.first()
                try:
                    ultimo_documento = Documentos.objects.filter(receptor_id=receptor.codigo, estado='PROCESADO',enviado_movil =False).latest('condicionOperacion')
                    # este guarda si el cliente ya se le envio el documento
                    #ultimo_documento.enviado_movil = True
                    #ultimo_documento.save()
                    return Response({'codigoGeneracion': ultimo_documento.codigoGeneracion}, status=status.HTTP_200_OK)
                except Documentos.DoesNotExist:
                    return Response({'error': 'No se encontraron documentos procesados para este receptor.'}, status=status.HTTP_200_OK)
            except Vendedores.DoesNotExist:
                return Response({'error': 'No se encontró un receptor  con ese codigo.'}, status=status.HTTP_200_OK)
        else:
             return Response({'error': 'No se encontró un receptor  con ese codigo.'}, status=status.HTTP_200_OK)   
class DocumentosLoteCreateAPIView(CreateAPIView):
    serializer_class = DocumentosSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Obtén los datos de los documentos del cuerpo de la solicitud
        data = request.data
        if 'documentos' in data:
            data =data['documentos']
        # Si es una lista de documentos, realiza el insert en bulk
            if isinstance(data, list):
                documentos = []
                result = []

                for doc_data in data:
                    serializer = DocumentosSerializer(data=doc_data)
                    if serializer.is_valid():
                        documento = serializer.save()
                        documentos.append(documento)
                    else:
                        result.append({
                            "error": "Error en la validación del documento",
                            "codigoGeneracion": doc_data['codigoGeneracion'],
                            "errors": serializer.errors
                        })
                if documentos:
                    respuesta_mh = procesorLote.get_documentos_lote(self, request, documentos)
                    result.append({'respuesta_mh':respuesta_mh})    

                
                return Response({"Respuesta": result}, status=status.HTTP_201_CREATED)
            # Si es un solo documento, crea una lista con un solo elemento
            
            else:
                return Response({"error": "Los datos de entrada no son válidos debe enviar un List con documentos"}, status=status.HTTP_400_BAD_REQUEST)

            # Obtén los códigos de generación de los documentos creados
           # codigos_generacion = [documento.codigoGeneracion for documento in documentos]

            # Llama al proceso de procesamiento de datos
            
            #result = DataProcessor.process_data_document(self, request, codigos_generacion)
            
        else:
            return Response({"error": "no se econtro el list documentos en el JSON"}, status=status.HTTP_400_BAD_REQUEST)



def file_iterator(pdf_path, json_path):
    try:
        # Intenta abrir y leer el archivo PDF
        with open(pdf_path, 'rb') as pdf_file:
            chunk = pdf_file.read(8192)
            while chunk:
                yield chunk
                chunk = pdf_file.read(8192)
        
        # Intenta abrir y leer el archivo JSON
        with open(json_path, 'rb') as json_file:
            chunk = json_file.read(8192)
            while chunk:
                yield chunk
                chunk = json_file.read(8192)

    except FileNotFoundError:
        # Manejar el caso en que uno o ambos archivos no existan
        raise StopIteration

@authentication_classes([])  
@permission_classes([])      
class DownloadFilesAPI(APIView):
    def get(self, request, codigo_generacion):
        parametros = Parametros.objects.filter(company_id=Company.objects.get(id=1)).first()
        if parametros and parametros.attachment_files_path:
            dirercion_archivos = 'opt/DTESV/dtesv/archivos_pruebas' ## parametros.attachment_files_path Ruta original
            logger.error(f"La ruta de los archivos es: {dirercion_archivos}")
        else:
            return JsonResponse({"error": "La configuración de archivos adjuntos no está disponible"}, status=500)

        if not codigo_generacion:
            return JsonResponse({"error": "El parámetro 'codigoGeneracion' es requerido"}, status=400)

        # Construir rutas a los archivos utilizando el parámetro
        pdf_path = os.path.join(dirercion_archivos, f"{codigo_generacion}.pdf")
        json_path = os.path.join(dirercion_archivos, f"{codigo_generacion}.json")

        # Verificar si los archivos existen
        if os.path.exists(pdf_path) and os.path.exists(json_path):
            zip_filename = f"{codigo_generacion}_archivos.zip"
            zip_path = os.path.join(dirercion_archivos, zip_filename)

            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.write(pdf_path, os.path.basename(pdf_path))
                zip_file.write(json_path, os.path.basename(json_path))
        
            # Enviar el archivo ZIP para su descarga
            def file_iterator(zip_path, chunk_size=8192):
                with open(zip_path, 'rb') as file:
                    while True:
                        chunk = file.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk

            response = StreamingHttpResponse(file_iterator(zip_path))
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'            
            
            return response
            
        else:
            return JsonResponse({"error": "Los archivos no existen"}, status=404)

@authentication_classes([])  
@permission_classes([])
class createPDFJSONSENMAIL(APIView):
    def get(self, request, codigoGeneracion):
        try:
            parametros = Parametros.objects.filter(company_id=Company.objects.get(id=1)).first()
            documento = Documentos.objects.filter(codigoGeneracion=codigoGeneracion,en_contingencia=False)
            if documento:
                logger.error(f"JSONPDF evaluando la creacion de los documentos:")
                ruta_pdf_file = create_pdf.gen_pdf.generarPdf(self,codigoGeneracion)
                logger.error(f"La ruta del PDF es: {ruta_pdf_file}")
                ## Verifica la existencia del archivo que se ha creado
                if os.path.isfile(ruta_pdf_file['pdf_file']):
                    document = constructor_dicionario.DocumentoDiccionarioStruc.get_diccionario(documento)
                    for doc in document:
                        doc['identificacion']['selloRecibido'] = documento[0].selloRecibido
                        jsonpha = create_json.gen_json.create_fileJson(None, doc) 
                        if jsonpha:        
                            email_return = enviar_email.sent_email(parametros,codigoGeneracion)
                            logger.error(f"Respuesta del envio de correo {email_return}")
                            # Verificar si el envío del email fue exitoso
                            if email_return.get('status') == 'success':
                                # Actualizar el campo email_enviado
                                documento.update(email_enviado=1)

                            return email_return
                        else:
                            return JsonResponse({'error': 'No se encontró el archivo Json.'}, status=404) 
                else:
                ## Si el archivo creado no existe se retorna el mensaje de error
                    return JsonResponse({'error': 'No se encontró el archivo PDF.'}, status=404)
            else:
                return JsonResponse({'error': 'No se Existe El documento:'+codigoGeneracion}, status=404) 
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

class descargaPDFJSONS(APIView):
    def get(self, request, codigoGeneracion):
        try:
            parametros = Parametros.objects.filter(company_id=Company.objects.get(id=1)).first()
            documento = Documentos.objects.filter(codigoGeneracion=codigoGeneracion,en_contingencia=False)
            if documento:
                logger.error(f"JSONPDF evaluando la creacion de los documentos:")
                ruta_pdf_file = create_pdf.gen_pdf.generarPdf(self,codigoGeneracion)
                logger.error(f"La ruta del PDF es: {ruta_pdf_file}")
                ## Verifica la existencia del archivo que se ha creado
                if os.path.isfile(ruta_pdf_file['pdf_file']):
                    document = constructor_dicionario.DocumentoDiccionarioStruc.get_diccionario(documento)
                    for doc in document:
                        doc['identificacion']['selloRecibido'] = documento[0].selloRecibido
                        jsonpha = create_json.gen_json.create_fileJson(None, doc) 
                        # if jsonpha:        
                        #     email_return = enviar_email.sent_email(parametros,codigoGeneracion)
                        #     logger.error(f"Respuesta del envio de correo {email_return}")
                        #     # Verificar si el envío del email fue exitoso
                        #     if email_return.get('status') == 'success':
                        #         # Actualizar el campo email_enviado
                        #         documento.update(email_enviado=1)

                        #     return email_return
                        # else:
                        #     return JsonResponse({'error': 'No se encontró el archivo Json.'}, status=404) 
                else:
                ## Si el archivo creado no existe se retorna el mensaje de error
                    return JsonResponse({'error': 'No se encontró el archivo PDF.'}, status=404)
            else:
                return JsonResponse({'error': 'No se Existe El documento:'+codigoGeneracion}, status=404) 
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)        