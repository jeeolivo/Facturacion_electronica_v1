from venv import logger
#from dtesv.models import Documentos ,DocumentosDetalle,ExtencionEntrega,DocumentosAsociados,Pagos, settings
from django.http import FileResponse, HttpResponse, JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
import dtesv.Apis.envio_email_dm as enviar_email
from dtesv.models import User,Company,Documentos, settings
#from dtesv.processes.procesorDocMh import MainProcessor
import os



def sent_email(request, codigoGeneracion):
    # Inicializar variables para los mensajes de archivos faltantes
    messagejson = ""
    messagepdf = ""
    message = ""
    status_code = 200

    # Supongamos que tienes una instancia de Parametros
    parametro_instance = settings.Parametros.objects.get(id=1)  # Ejemplo
    notice = parametro_instance.noticias  # Esto te da el valor del campo 'noticias'

    # Validar que sea una cadena
    if notice is None:
        notice = ""  # Valor predeterminado si está vacío
    elif not isinstance(notice, str):
        notice = str(notice)  # Convertir a cadena si es necesario


    if isinstance(request, HttpRequest):
            company_id = Company.objects.filter(users=request.user).first()
            parametro = company_id.parametros_company_id.first()
    else:
        parametro = request
        company_id = parametro.company_id
        
    if parametro:
        ruta_pdf = parametro.attachment_files_path+codigoGeneracion+'.pdf'
        ruta_json = parametro.attachment_files_path+codigoGeneracion+'.json'
        pdf_exists = os.path.isfile(ruta_pdf)
        json_exists = os.path.isfile(ruta_json)
    else:
        pdf_exists = False
        json_exists = False

    if company_id:
        if pdf_exists and json_exists:
            documento = Documentos.objects.filter(emisor_id=company_id.emisor_id, codigoGeneracion=codigoGeneracion).first()
            if documento:
                correo_destino = (
                    documento.receptor_origen.correo if documento.receptor_origen else
                    documento.receptor_id.correo if documento.receptor_id else
                    documento.proveedor_id.correo if documento.proveedor_id else 
                    'efactura@lamorazan.com'
                )

                dic_sent={
                    "mail" : correo_destino , 
                    #"mail" : 'carlos_hercules@lamorazan.com', 
                    "file_name" : codigoGeneracion,
                    #"pathfile" : parametro.attachment_email_path,
                    "pathfile" : '/mnt/h',
                    "doc_number" : documento.selloRecibido,
                    "customer_name" : documento.receptor_id.nombre if documento.receptor_id else documento.proveedor_id.nombre ,
                    "customer_code" : documento.receptor_id.pk if documento.receptor_id else documento.proveedor_id.codigo,
                    "date" : str(documento.fecEmi),
                    "doc_type" : documento.tipodocumento.valor + '-ANULADO' if documento.estado=='INVALIDADO' else documento.tipodocumento.valor  ,
                    "amount" : documento.totalPagar,
                    "notice" : f'Aprovecha nuestras promociones... <a href="{notice}" style="color: blue; font-size: medium;" target="_blank">¡Haz Click Aquí para Ver el Catálogo!</a>'
                            
                }

                # Ejecutar solo si el correo es diferente de 'efactura@lamorazan.com'
                if correo_destino.lower() != 'efactura@lamorazan.com':
                    message = enviar_email.sentEmail(dic_sent, parametro).sent()
                    
        else :
            # Comprobación individual y mensaje si falta algún archivo
            if not json_exists:
                messagejson = "JSON"
            if not pdf_exists:
                messagepdf = "PDF"

            # Crear mensaje de archivos faltantes
            missing_files = []
            if messagejson:
                missing_files.append(messagejson)
            if messagepdf:
                missing_files.append(messagepdf)
            
            message = f"El archivo(s): {', '.join(missing_files)} no existe(n)."
            status_code = 404  # Cambiar el código de estado a 404 si faltan archivos
              # result =  MainProcessor(request,codigoGeneracion).run_email_worker()

    # Retornar respuesta JSON con el mensaje de error o éxito
    return JsonResponse({'result': message, 'status': status_code}, status=status_code)


## 2024-10-16 Para actualizar el estado de envio del documento.
@csrf_exempt
def update_email_sent(request, codigoGeneracion):
    print(f"Request method: {request.method}")  # Registro para verificar el método
    if request.method == 'POST':
        try:
            # Actualiza directamente usando .update() en lugar de .save()
            updated_count = Documentos.objects.filter(codigoGeneracion=codigoGeneracion).update(email_enviado=1)
            
            if updated_count == 0:
                return JsonResponse({'status': 'error', 'message': 'Documento no encontrado.'}, status=404)
            
            logger.info(f"Se actualizo estado al reenviar correo: {codigoGeneracion}")
            return JsonResponse({'status': 'success', 'message': 'Campo email_enviado actualizado correctamente.'})
        except Documentos.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Documento no encontrado.'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)    