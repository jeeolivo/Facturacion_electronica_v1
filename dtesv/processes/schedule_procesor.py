# dtesv/processes/schedule_procesor.py
import json
import os
from celery import shared_task
from datetime import datetime
import dtesv.processes.create_pdf as gen_pdf
import dtesv.processes.create_json as gen_json
import dtesv.views.sent_email as enviar_email

 


from dtesv.models import Documentos, Company, Parametros

@shared_task
def execute_processor():
    documents = Documentos.objects.filter(estado__in=('RECHAZADO', 'NUEVO'))

@shared_task
def sent_mail():
   '''' companys = Company.objects.filter(id=1).first()
    documentos = Documentos.objects.filter(email_enviado=False, estado='PROCESADO')
    parametros = Parametros.objects.filter(company_id=companys).first()
    for res in documentos:
        codigo_gen = res.codigoGeneracion
        ruta_pdf_file = gen_pdf.gen_pdf.generarPdf(codigo_gen)
        
        if os.path.isfile(ruta_pdf_file['pdf_file']):
            ruta_json_file = gen_json.gen_json.create_fileJson(res, parametros)
            
        if os.path.isfile(ruta_json_file):
            result_mail = enviar_email.sent_email(parametros, codigo_gen)
            estadoml = json.loads(result_mail.content)['result']
            if 'Enviado!' in json.loads(result_mail.content)['result']:
                res.email_enviado = True
            else:
                res.email_enviado = False
            res.save()'''
   print("HELLON")

@shared_task
def send_emails_for_pending_documents():
    # Obtén todos los documentos con email_enviado=False y estado='PROCESADO'
    pending_documents = Documentos.objects.filter(email_enviado=False, estado='PROCESADO')
    
    # Itera sobre los documentos pendientes y ejecuta send_email_task para cada uno
    for document in pending_documents:
        company = document.emisor_id.company.id
        parametros = Parametros.objects.filter(company_id=company).first()
        codigoGen = document.codigoGeneracion   
        ruta_pdf_file = gen_pdf.gen_pdf.generarPdf(document,codigoGen)
        if os.path.isfile(ruta_pdf_file['pdf_file']): 
              result_mail = enviar_email.sent_email(parametros,codigoGen)
              estadoml = json.loads(result_mail.content)['result']
              if 'Enviado!' in json.loads(result_mail.content)['result'] :
                    document.email_enviado = True
                    document.save()
                    estado = print(f'Correo enviado para {codigoGen}. Estado: {estadoml}')
                            
              else :
                    estado = estadoml