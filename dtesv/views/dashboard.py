import requests
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Count
from dtesv.models import User,Company,Documentos,Parametros, Receptor, Proveedor
from datetime import datetime, timedelta
 
# def dashboard_view(request):
#     return render(request, 'dashboard.html')

def is_url_online(url):
   
    try:
        response =  requests.head(url)
        if response.status_code == 200:
            return True
        else:
           response = requests.post(url)
           return response.status_code == 200
         
    except requests.exceptions.RequestException:        
            return False

# 2024-10-15: Se actualiza Vista para validar el estado de las URLs
def urls_status_data(request, filtro):
    urls = Parametros.objects.values_list('url', flat=True)
    url_states = [{'name': url, 'state': is_url_online(url)} for url in urls]
    return JsonResponse(url_states, safe=False)



# 2024-10-15: Función para obtener datos agrupados por estado según el filtro proporcionado
def obtener_documentos_data(filtro):
    company_id = Company.objects.filter(id=1).first()
    if company_id:
        documentos = Documentos.objects.filter(emisor_id=company_id.emisor_id)
        if filtro == 'mesActual':
            documentos = documentos.filter(fecEmi__month=datetime.now().month )
        elif filtro == 'mesAnterior':
            documentos = documentos.filter(fecEmi__month=datetime.now().month - 1)
        elif filtro == 'anioActual':
            documentos = documentos.filter(fecEmi__year=datetime.now().year)
        elif filtro == 'diaActual':
            documentos = documentos.filter(fecEmi=datetime.now())
        else:
            raise ValueError(f"Filtro no válido {filtro}")
        
        documentos_agrupados = documentos.values('estado').annotate(cantidad=Count('codigoGeneracion'))
        data = [{'estado': doc['estado'], 'cantidad': doc['cantidad']} for doc in documentos_agrupados]
        return data
    return []



# 2024-10-15: Función para obtener el total de documentos
def obtener_total_documentos():
    company_id = Company.objects.filter(id=1).first()
    if company_id:
        total_documentos = Documentos.objects.filter(emisor_id=company_id.emisor_id).count()
        return total_documentos
    return 0

# 2024-10-15: Vista principal del dashboard
def dashboard_view(request, filtro=None):
    estados = ['PROCESADO', 'INVALIDADO', 'RECHAZADO', 'ERROR', 'ERR_INVALI','ANULADONC']
    documentos_data_mes_actual = obtener_documentos_data('mesActual')
    documentos_data_mes_anterior = obtener_documentos_data('mesAnterior')

    # Obtener cantidad de correos en receptores y proveedores
    email = 'efactura@lamorazan.com'
    
    # Verificamos el filtro recibido
    if filtro == 'mesActual':
        documentos_data = obtener_documentos_data('mesActual')
    elif filtro == 'mesAnterior':
        documentos_data = obtener_documentos_data('mesAnterior')
    else:
        documentos_data = obtener_documentos_data('mesActual')

    # Obtenemos también los datos para el mes anterior
    documentos_data_mes_anterior = obtener_documentos_data('mesAnterior')

    # Calculamos los totales por estado para el filtro seleccionado y el mes anterior
    totales_mes_actual = {estado: sum(doc['cantidad'] for doc in documentos_data if doc['estado'] == estado) for estado in estados}
    totales_mes_anterior = {estado: sum(doc['cantidad'] for doc in documentos_data_mes_anterior if doc['estado'] == estado) for estado in estados}

    # Calculamos los porcentajes de crecimiento para cada estado
    porcentajes_crecimiento = {}
    for estado in estados:
        if totales_mes_anterior[estado] > 0:
            crecimiento = ((totales_mes_actual[estado] - totales_mes_anterior[estado]) / totales_mes_anterior[estado]) * 100
            porcentajes_crecimiento[estado] = round(crecimiento, 2)
        else:
            porcentajes_crecimiento[estado] = 0  # Si no hay documentos el mes anterior, establecemos 0%

    # Calcular usuarios en línea
    tiempo_limite = timezone.now() - timedelta(minutes=5)  # Cambia este valor según lo necesites
    usuarios_en_linea = User.objects.filter(last_activity__gte=tiempo_limite).count()

    receptores_count = Receptor.objects.filter(correo=email).count()
    proveedores_count = Proveedor.objects.filter(correo=email).count()

    context = {
        'documentos_data': documentos_data,  # Datos del filtro seleccionado
        'totales_mes_actual': totales_mes_actual,
        'totales_mes_anterior': totales_mes_anterior,
        'porcentajes_crecimiento': porcentajes_crecimiento,
        'usuarios_en_linea': usuarios_en_linea,
        'receptores_count': receptores_count,
        'proveedores_count': proveedores_count
    }

    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'totales_mes_actual': totales_mes_actual,
            'totales_mes_anterior': totales_mes_anterior,
            'porcentajes_crecimiento': porcentajes_crecimiento,
        })
    
    # Si no es AJAX, devolver la página HTML normalmente
    return render(request, 'dashboard.html', context)




# 2024-10-15: Vista del dashboard para datos JSON
def dashboard_json_view(request, filtro):

    estados = ['PROCESADO', 'INVALIDADO', 'RECHAZADO', 'ERROR']

    if filtro == 'mesActual':
        documentos_data = obtener_documentos_data('mesActual')
    elif filtro == 'mesAnterior':
        documentos_data = obtener_documentos_data('mesAnterior')
    else:
        return JsonResponse({'error': 'No es posible usar este filtro.'}, status=400)

    # Formatear los datos en JSON
    data = [{'estado': doc['estado'], 'cantidad': doc['cantidad']} for doc in documentos_data]

    return JsonResponse(data, safe=False)



# 2024-10-10: Esto permite obtener la facturacion mensual, para gráfica documentosEstadoChart
def dashboard_json_totalMeses(request):
    # Crear listas de estados y meses
    estados = ['PROCESADO', 'INVALIDADO', 'RECHAZADO', 'ERROR', 'ERR_INVALI']
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    #print("Generando datos para el dashboard...")

    # Aquí simula la obtención de documentos por estado y mes
    documentos_estado_mensual = obtener_documentos_estado_mensual()
    #print("Documentos mensuales obtenidos:", documentos_estado_mensual)

    # Inicializa el diccionario con estados y 12 ceros para cada mes
    datos_por_estado = {estado: [0] * 12 for estado in estados}

    # Recorremos los documentos y agregamos los totales a su mes correspondiente
    for entry in documentos_estado_mensual:
        mes = entry['fecEmi__month'] - 1  # Restamos 1 porque las listas en Python son 0-index
        estado = entry['estado']
        if estado in datos_por_estado:
            datos_por_estado[estado][mes] = entry['total_documentos']  # Añadimos el total de documentos al mes correcto

    # Crear el JSON agrupando los datos de estados y meses
    data = {
        'meses': meses,
        'datos_por_estado': datos_por_estado
    }
    #print("Datos generados:", data)

    return JsonResponse({'meses': meses, 'datos_por_estado': datos_por_estado})



# 2024-10-10: Esto permite obtener la facturacion mensual, para la tablaDocumentosNoEnviados
def obtener_documentos_estado_mensual():
    # Filtramos las facturas del año actual
    documentos_estado_mensual = (
        Documentos.objects.filter(fecEmi__year=timezone.now().year)
        .values('fecEmi__month', 'estado')  # Agrupamos por mes y estado
        .annotate(total_documentos=Count('codigoGeneracion'))  # Sumamos el total por mes
        .order_by('fecEmi__month')  # Ordenamos por mes
    )
    # Esto devolverá algo como:
    # [{'fecha__month': 1, 'total_facturado': 5000.00}, {'fecha__month': 2, 'total_facturado': 3000.00}, ...]
    return documentos_estado_mensual

# 2024-10-15: Vista para obtener documentos no enviados
def obtener_documentos_no_enviados(request):
# Obtener documentos con email_enviado = 0
    filtro = request.GET.get('filtro', 'mesActual')  # Obtener filtro desde la solicitud (predeterminado es 'mesActual')

    # Obtener mes y día de la solicitud si el filtro lo requiere
    mes = request.GET.get('mes', None)
    dia = request.GET.get('dia', None)

    # Validación del parámetro 'mes' si se ha proporcionado
    if mes:
        try:
            mes = int(mes)
        except ValueError:
            return JsonResponse({'error': 'Mes no válido'}, status=400)

    # Validación del parámetro 'dia' si se ha proporcionado
    if dia:
        try:
            # Verificar que el día esté en formato válido (YYYY-MM-DD)
            datetime.strptime(dia, '%Y-%m-%d')
        except ValueError:
            return JsonResponse({'error': 'Día no válido, debe estar en formato YYYY-MM-DD'}, status=400)


    # documentos = obtener_documentos_filtrados(filtro, email_enviado=0,mes=mes,dia=dia).values(
    #     'num_documento', 'receptor_id', 'receptor_origen', 'proveedor_id', 'fecEmi'
    # )
    
    # 2025-09-26: Usamos select_related para precargar receptor y proveedor
    documentos = (
        obtener_documentos_filtrados(filtro, email_enviado=0, mes=mes, dia=dia)
        .select_related("receptor", "proveedor")
        .only("num_documento", "receptor__codigo", "receptor__nombre",
              "proveedor__codigo", "proveedor__nombre", "fecEmi", "receptor_origen")
    )

    documentos_list = []

    for doc in documentos:
        # Lógica para obtener el nombre y código del cliente
        if doc.receptor:
            nombre = doc.receptor.nombre or "Desconocido"
            codigo_cliente = doc.receptor.codigo
            receptor_id = doc.receptor.codigo
        elif doc.proveedor:
            nombre = doc.proveedor.nombre or "Desconocido"
            codigo_cliente = doc.proveedor.codigo
            receptor_id = None  # porque no aplica
        else:
            # Usamos un valor predeterminado si ambos son None
            nombre = "Desconocido"
            codigo_cliente = "Sin Código"
            receptor_id = None

        # Añadir a la lista
        documentos_list.append({
            'num_documento': doc['num_documento'],
            'Receptor_id': receptor_id,
            'Nombre': nombre,
            'fecEmi': doc['fecEmi'],
        })

    return JsonResponse(documentos_list, safe=False)



# 2024-10-15: Función genérica para obtener documentos aplicando filtro en la tablaDocumentosNoEnviados
def obtener_documentos_filtrados(filtro, email_enviado=None, mes=None, dia=None):
    company_id = Company.objects.filter(id=1).first()
    if company_id:
        # Filtrar documentos por emisor y estado 'procesado'
        documentos = Documentos.objects.filter(emisor_id=company_id.emisor_id, estado='PROCESADO')

        # Filtrar por el parámetro 'email_enviado' si se proporciona
        if email_enviado is not None:
            documentos = documentos.filter(email_enviado=email_enviado)

        # Aplicar filtro de fechas
        ahora = datetime.now()

        if filtro == 'mesActual':
            documentos = documentos.filter(fecEmi__month=ahora.month, fecEmi__year=ahora.year)

        elif filtro == 'mesAnterior':
            mes_anterior = (ahora.month - 1) if ahora.month > 1 else 12
            anio_mes_anterior = ahora.year if ahora.month > 1 else ahora.year - 1
            documentos = documentos.filter(fecEmi__month=mes_anterior, fecEmi__year=anio_mes_anterior)

        elif filtro == 'mesExacto':
            if mes is None or not (1 <= mes <= 12):
                raise ValueError(f"Mes no válido: {mes}")
            documentos = documentos.filter(fecEmi__month=mes, fecEmi__year=ahora.year)

        elif filtro == 'diaActual':
            documentos = documentos.filter(fecEmi__date=ahora.date())

        elif filtro == 'diaExacto':
            if dia is None:
                raise ValueError("Debe proporcionar un día exacto para el filtro 'diaExacto'")
            try:
                fecha_exacta = datetime.strptime(dia, "%Y-%m-%d").date()
                documentos = documentos.filter(fecEmi__date=fecha_exacta)
            except ValueError:
                raise ValueError(f"Formato de fecha no válido para 'diaExacto': {dia}")

        else:
            raise ValueError(f"Filtro no válido: {filtro}")

        return documentos
    return Documentos.objects.none()  # Retorna un queryset vacío si no hay compañía