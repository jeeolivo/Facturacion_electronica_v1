from venv import logger
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Count
from dtesv.models import User,Company,Documentos,Parametros,contingencias
from datetime import datetime

def solicitud_contingencias_view(request):
     
    return render(request, 'contingencias.html')


def data_contingencias(request,fecha_desde,fecha_hasta,empresa_id):
    #logger.error("Ingresando a Solicitud Contingencias.py", exc_info=True)
    
    es_admin = request.user.is_superuser
    fecha_desde_d = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    fecha_hasta_d = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    print(f"Fecha desde: {fecha_desde}, Fecha Hasta: {fecha_hasta}")

    company_id = Company.objects.filter(id=empresa_id).first()
    if company_id:
        print(f"Company ID: {company_id.id}, Emisor ID: {company_id.emisor_id}")

        # Consulta a la base de datos para obtener todos los registros y mostrarlos para depuración
        all_documents = contingencias.objects.all()
        print(f"Todos los documentos: {all_documents}")

        documentos = contingencias.objects.filter(
            emisor=company_id.emisor_id,
            fTransmision__gte=fecha_desde_d,
            fTransmision__lte=fecha_hasta_d,
            ).values(
                'codigoGeneracion',
                'tipoContingencia__valor',  # 'tipoContingencia__valor' Corregir el nombre del campo para obtener el ID de tipoContingencia
                'estado',
                'fTransmision',
                'hTransmision',
                'fInicio',
                'fFin',
                'hInicio',
                'hFin',
                'motivoContingencia',
                'selloRecepcion',
                'ambiente',
                'observacion_proceso',
                'observaciones_mh',
            )
        print(f"Documentos encontrados: {documentos}")
        # Logging intermedio para revisar los valores obtenidos
        #logger.error(f"Documentos antes de formatear fechas: {documentos}")

    else:
        print("Company not found")
        documentos = []
    
    documentos_con_fechas_formateadas = [
        {
            'codigoGeneracion': documento['codigoGeneracion'],
            'tipoContingencia': documento['tipoContingencia__valor'],
            'estado': documento['estado'],
            'fTransmision': documento['fTransmision'].strftime('%Y/%m/%d') if documento['fTransmision'] else None,
            'hTransmision': documento['hTransmision'].strftime('%H:%M:%S') if documento['hTransmision'] else None,
            'fInicio': documento['fInicio'].strftime('%Y/%m/%d') if documento['fInicio'] else None,  
            'hInicio': documento['hInicio'].strftime('%H:%M:%S') if documento['hInicio'] else None,
            'fFin': documento['fFin'].strftime('%Y/%m/%d') if documento['fFin'] else None,
            'hFin': documento['hFin'].strftime('%H:%M:%S') if documento['hFin'] else None,               
            'motivoContingencia': documento['motivoContingencia'],        
            'selloRecepcion': documento['selloRecepcion'],
            'observaciones_mh': documento['observaciones_mh'],         
            'observacion_proceso': documento['observacion_proceso'],
            'ambiente': documento['ambiente'],
        }
        for documento in documentos
    ]
    logger.error(f"Documentos después de formatear fechas: {documentos_con_fechas_formateadas}")
    context = {
        'documentos': documentos_con_fechas_formateadas,
        'es_admin': es_admin,
    }
    return render(request, 'contingencias.html', context)

# def data_contingencias(request,fecha_desde,fecha_hasta,empresa_id):
#     es_admin = request.user.is_superuser
#     fecha_desde_d = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
#     fecha_hasta_d = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
#     print(fecha_desde)
#     company_id = Company.objects.filter(id=empresa_id).first()
#     if company_id:
#         documentos = contingencias.objects.filter(
#     emisor=company_id.emisor_id,
#     fTransmision__gte=fecha_desde_d,
#         fTransmision__lte=fecha_hasta_d,
#                     ).values(
#                         'codigoGeneracion',
#                         'tipoContingencia__valor',  # Corregir el nombre del campo para obtener el ID de tipoContingencia
#                         'estado',
#                         'fTransmision',
#                         'hTransmision',
#                         'fInicio',
#                         'fFin',
#                         'hInicio',
#                         'hFin',
#                         'motivoContingencia',
#                         'selloRecepcion',
#                         'ambiente',
#                         'observacion_proceso',
#                         'observaciones_mh',
#                     )
#     else:
#         documentos = []
    
#     documentos_con_fechas_formateadas = [
#     {
#         'codigoGeneracion': documento['codigoGeneracion'],
#         'tipoContingencia': documento['tipoContingencia__valor'],
#         'estado': documento['estado'],
#         'fTransmision': documento['fTransmision'].strftime('%d/%m/%Y') if documento['fTransmision'] else None,
#         'hTransmision': documento['hTransmision'],
#         'fInicio': documento['fInicio'].strftime('%d/%m/%Y') if documento['fInicio'] else None,  
#         'hInicio': documento['hInicio'],
#         'fFin': documento['fFin'].strftime('%d/%m/%Y') if documento['fFin'] else None,
#         'hFin': documento['hFin'],        
#         'motivoContingencia': documento['motivoContingencia'],        
#         'selloRecepcion': documento['selloRecepcion'],
#         'observaciones_mh': documento['observaciones_mh'],         
#         'observacion_proceso': documento['observacion_proceso'],
#         'ambiente': documento['ambiente'],
        
#     }
#     for documento in documentos
#         ]
#     context = {
#         'documentos': documentos_con_fechas_formateadas,
#         'es_admin': es_admin,
#     }
#     return render(request, 'contingencias.html', context)