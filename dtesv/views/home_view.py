from django.shortcuts import render, redirect
from django.db.models import DateTimeField
from django.db.models.functions import Cast
from datetime import datetime

from django.contrib.auth import login as django_login, logout as django_logout, authenticate 

from django.contrib.auth.decorators import login_required 
from django.urls import reverse_lazy
from dtesv.models import User,Company,Documentos,C002TipoDocumento,C005TipoContingencia
#from django.contrib.auth.views import logout_then_login
from django.contrib import messages
from django.http import JsonResponse



# Create your views here.
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        # Obtener la URL de destino después del inicio de sesión exitoso
        redirect_to = self.request.GET.get('next', '/dtesv/home/#dashboard')
        return redirect_to
    
    def form_invalid(self, form):
        messages.error(self.request, 'Credenciales inválidas')
        return super().form_invalid(form)   

    def form_valid(self, form):
        # Procesar el formulario de inicio de sesión y redirigir al usuario
       # self.request.session['some_variable'] = 'some_value'  # Ejemplo: almacenar alguna variable en la sesión
       # return redirect(self.get_success_url())
        user = form.get_user()
        if user:
            empresas = Company.objects.filter(users=user)  # Obtener las empresas del usuario
            if empresas.exists():
                django_login(self.request, user)
                self.request.session['empresas'] = list(empresas.values_list('name', flat=True))  # Almacenar las empresas en la sesión
                return redirect(self.get_success_url())
            else:
                messages.error(self.request, 'El usuario no tiene acceso a ninguna empresa.')
                
        return render(self.request, self.template_name, {'form': form}) 
# Create your views here.
@login_required
def profile_view(request):
    # Lógica de la vista de perfil
    # Puedes acceder a los datos del usuario a través de `request.user`
    # y devolver una respuesta adecuada, como renderizar una plantilla
    return render(request, 'profile.html')


@login_required
def home(request):
    # Lógica de la nueva vista de redirección
    return render(request, 'home.html')


 
@login_required
def home(request):
    if request.method == 'POST':
        isLogout = request.POST.get('btlogout')
        if isLogout:
            django_logout(request)
            return redirect('/dtesv/login/')

    user = request.user
    empresas = Company.objects.filter(users=user)

    # Verificar si se ha enviado una solicitud GET para ver los documentos
    if 'documentos' in request.GET:
        company_id = Company.objects.filter(users=request.user).first()
        if company_id:
            documentos = Documentos.objects.filter(emisor=company_id.emisor_id)
        else:
            documentos = []

        context = {
            'user': user,
            'empresas': empresas,
            'documentos': documentos,
        }
        return render(request, 'home.html', context)

    return render(request, 'home.html', {'user': user, 'empresas': empresas})

@login_required
def documentos(request):
    # Filtrar los documentos por el ID de la empresa
    
  
    
    es_admin = request.user.is_superuser
    company_id = Company.objects.filter(users=request.user).first()
    if company_id:
        #documentos = Documentos.objects.filter(emisor_id=company_id.emisor_id,)
        documentos = Documentos.objects.filter(
            emisor_id=company_id.emisor_id
             
        )
       
    else:
        documentos = []

    
    documentos_con_fechas_formateadas = []
    for documento in documentos:
       # tipo_documento_obj = C002TipoDocumento.objects.filter(codigo=documento.tipodocumento)
       # tipo_documento_nombre = tipo_documento_obj.valor
        
        if documento.fecEmi:
            fecemi_str = documento.fecEmi.strftime('%d/%m/%Y')
        else:
            fecemi_str = None

        if documento.fecha_proceso_mh:
            fecha_proceso_mh_str = documento.fecha_proceso_mh.strftime('%d/%m/%Y')
        else:
            fecha_proceso_mh_str = None

        documento_dict = {
            'tipodocumento': documento.tipodocumento.pk,
            'clase_documento': documento.clase_documento,
            'num_documento': documento.num_documento,
            'fecEmi': fecemi_str,
            'totalNoSuj': documento.totalNoSuj,
            'totalExenta': documento.totalExenta,
            'horEmi': documento.horEmi,
            'descuGravada': documento.descuGravada,
            'porcentajeDescuento': documento.porcentajeDescuento,
            'totalDescu': documento.totalDescu,
            'iva': documento.iva,
            'ivaRete1': documento.ivaRete1,
            'ivaPerci1': documento.ivaPerci1,
            'reteRenta': documento.reteRenta,
            'totalGravada': documento.totalGravada,
            'subTotalVentas': documento.subTotalVentas,
            #'descunosuj': documento.descunosuj,
            #'descuexenta': documento.descuexenta,
            'totalGravada': documento.totalGravada,
            'saldoFavor': documento.saldoFavor,
            'totalPagar': documento.totalPagar,
            'montoTotalOperacion': documento.montoTotalOperacion,
            'condicionOperacion': documento.condicionOperacion.pk if documento.condicionOperacion else None,
            'codigo_iva': documento.codigo_iva.pk if documento.codigo_iva else None,
            'totalLetras': documento.totalLetras,
            'receptor_id': documento.receptor_id.pk,
            'pagos': documento.pagos,
            'numPagoElectronico': documento.numPagoElectronico,
            'vendedor_id': documento.vendedor_id,
            'estado': documento.estado,
            'numeroControl': documento.numeroControl,
            'codigoGeneracion': documento.codigoGeneracion,
            'tipoModelo': documento.tipoModelo,
            'tipoOperacion': documento.tipoOperacion.pk,
            'tipoContingencia': documento.tipoContingencia.pk if documento.tipoContingencia else None,
            'motivoContin': documento.motivoContin,
            'tipoMoneda': documento.tipoMoneda,
            'emisor_id': documento.emisor_id.pk,
            'cod_entrega': documento.cod_entrega,
            'observaciones_entrega': documento.observaciones_entrega,
            'bienTitulo': documento.bienTitulo.pk if documento.bienTitulo else None,
            'numeroDocumento_rel_guid': documento.numeroDocumento_rel_guid,
            'numeroDocumento_rel_corr': documento.numeroDocumento_rel_corr,
            'recintoFiscal': documento.recintoFiscal.pk if documento.recintoFiscal else None,
            'regimen': documento.regimen.pk if documento.regimen else None,
            'tipoItemExpor': documento.tipoItemExpor,
            'seguro': documento.seguro,
            'flete': documento.flete,
            'codIncoterms': documento.codIncoterms.pk if documento.codIncoterms else None,
            'selloRecibido': documento.selloRecibido,
            'observaciones_mh': documento.observaciones_mh,
            'fecha_proceso_mh': fecha_proceso_mh_str,
            'cod_sucursal': documento.cod_sucursal,
            'observacion_proceso': documento.observacion_proceso,
            'tipo_documento':documento.tipodocumento.valor
        }

        documentos_con_fechas_formateadas.append(documento_dict)

     
    
     
    context = {
        'documentos': documentos_con_fechas_formateadas,
        'es_admin': es_admin,
    }
    return render(request, 'documentos.html', context)

@login_required
def documentos_by_fecha(request,fecha_desde,fecha_hasta,empresa_id):
    # Filtrar los documentos por el ID de la empresa
    es_admin = request.user.is_superuser
    fecha_desde_d = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    fecha_hasta_d = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    print(fecha_desde)
    company_id = Company.objects.filter(id=empresa_id).first()
    if company_id:
        #documentos = Documentos.objects.filter(emisor_id=company_id.emisor_id,)
        documentos = Documentos.objects.filter(
            emisor_id=company_id.emisor_id,fecEmi__gte=fecha_desde_d, fecEmi__lte=fecha_hasta_d
        ).values(
            'tipodocumento__pk',
            'clase_documento',
            'num_documento',
            # Otros campos necesarios...
            'observacion_proceso',
            'tipoOperacion__pk',  # Referencia al campo pk de tipoOperacion
            # Otros campos necesarios...
            'horEmi','totalPagar',
            'fecEmi',
            'receptor_id__pk',
            'estado',
            'codigoGeneracion',
            'emisor_id__pk',
            'selloRecibido',
            'observaciones_mh',
            'observacion_proceso',
             'tipodocumento__valor',
             'estado_anulado',
             'fecha_anula_mh',
             'fecha_proceso_mh',
             'receptor_origen__pk',
             'rutaEntrega',
             'anuladoErp',
             'proveedor_id__pk',
        )
       
    else:
        documentos = []

    
   # documentos_con_fechas_formateadas = []
    documentos_con_fechas_formateadas = [
    {
        'tipodocumento': documento['tipodocumento__pk'],
        'num_documento': documento['num_documento'],
        'fecEmi': documento['fecEmi'].strftime('%d/%m/%Y') if documento['fecEmi'] else None,
        'horEmi': documento['horEmi'],
        'totalPagar': documento['totalPagar'],
        'receptor_id': documento['receptor_origen__pk'] if documento['receptor_origen__pk'] else documento['receptor_id__pk'] if documento['receptor_id__pk'] else documento['proveedor_id__pk'] if documento['proveedor_id__pk'] else None ,
        'estado': documento['estado'],
        'codigoGeneracion': documento['codigoGeneracion'],
        'emisor_id': documento['emisor_id__pk'],
        'selloRecibido': documento['selloRecibido'],
        'observaciones_mh': documento['observaciones_mh'],
        'fecha_proceso_mh': documento['fecha_proceso_mh'].strftime('%d/%m/%Y') if documento['fecha_proceso_mh'] else None,
        'observacion_proceso': documento['observacion_proceso'],
        'tipo_documento': documento['tipodocumento__valor'],
        'estado_anulado': documento['estado_anulado'],
        'fecha_anula_mh': documento['fecha_anula_mh'],
        'rutaEntrega':documento['rutaEntrega'],
        'anuladoErp':documento['anuladoErp'],
    }
    for documento in documentos
        ]

     
    
     
    context = {
        'documentos': documentos_con_fechas_formateadas,
        'es_admin': es_admin,
    }
    return render(request, 'documentos.html', context)

def obtener_datos_documento(request, codigoGeneracion):
    company_id = Company.objects.filter(users=request.user).first()
    if company_id:
        documento = Documentos.objects.filter(emisor_id=company_id.emisor_id, codigoGeneracion=codigoGeneracion).first()
        if documento:
            datos_documento = {
            'tipodocumento': documento.tipodocumento.pk,
            'clase_documento': documento.clase_documento,
            'num_documento': documento.num_documento,
            'fecEmi': documento.fecEmi,
            'totalNoSuj': documento.totalNoSuj,
            'totalExenta': documento.totalExenta,
            'horEmi': documento.horEmi,
            'descuGravada': documento.descuGravada,
            'porcentajeDescuento': documento.porcentajeDescuento,
            'totalDescu': documento.totalDescu,
            'iva': documento.iva,
            'ivaRete1': documento.ivaRete1,
            'ivaPerci1': documento.ivaPerci1,
            'reteRenta': documento.reteRenta,
            'totalGravada': documento.totalGravada,
            'subTotalVentas': documento.subTotalVentas,
            #'descunosuj': documento.descunosuj,
            #'descuexenta': documento.descuexenta,
            'totalGravada': documento.totalGravada,
            'saldoFavor': documento.saldoFavor,
            'totalPagar': documento.totalPagar,
            'montoTotalOperacion': documento.montoTotalOperacion,
            'condicionOperacion': documento.condicionOperacion.pk if documento.condicionOperacion else None,
            'codigo_iva': documento.codigo_iva.pk if documento.codigo_iva else None,
            'totalLetras': documento.totalLetras,
            'receptor_id': documento.receptor_id.pk,
            'pagos': documento.pagos,
            'numPagoElectronico': documento.numPagoElectronico,
            'vendedor_id': documento.vendedor_id,
            'estado': documento.estado,
            'numeroControl': documento.numeroControl,
            'codigoGeneracion': documento.codigoGeneracion,
            'tipoModelo': documento.tipoModelo.pk,
            'tipoOperacion': documento.tipoOperacion.pk,
            'tipoContingencia': documento.tipoContingencia.pk if documento.tipoContingencia else None,
            'motivoContin': documento.motivoContin,
            'tipoMoneda': documento.tipoMoneda,
            'emisor_id': documento.emisor_id.pk,
            'cod_entrega': documento.cod_entrega,
            'observaciones_entrega': documento.observaciones_entrega,
            'bienTitulo': documento.bienTitulo.pk if documento.bienTitulo else None,
            'numeroDocumento_rel_guid': documento.numeroDocumento_rel_guid,
            'numeroDocumento_rel_corr': documento.numeroDocumento_rel_corr,
            'recintoFiscal': documento.recintoFiscal.pk if documento.recintoFiscal else None,
            'regimen': documento.regimen.pk if documento.regimen else None,
            'tipoItemExpor': documento.tipoItemExpor,
            'seguro': documento.seguro,
            'flete': documento.flete,
            'codIncoterms': documento.codIncoterms.pk if documento.codIncoterms else None,
            'selloRecibido': documento.selloRecibido,
            'observaciones_mh': documento.observaciones_mh,
            'fecha_proceso_mh': documento.fecha_proceso_mh,
            'cod_sucursal': documento.cod_sucursal,
            'observacion_proceso': documento.observacion_proceso,
            'estado_anulado':documento.estado_anulado,
            'fecha_anula_mh':documento.fecha_anula_mh
            }
            return JsonResponse(datos_documento)
        else:
            return JsonResponse({'error': 'Documento no encontrado'}, status=404)
    else:
        return JsonResponse({'error': 'Empresa no encontrada'}, status=404)
    
def tipo_contingencia(request):
    tipos_contingencia = C005TipoContingencia.objects.all()
    # Crear una lista de tipos de contingencia en formato JSON
    tipos_contingencia_json = [{'codigo': tipo.codigo, 'valor': tipo.valor} for tipo in tipos_contingencia]
    return JsonResponse({'tipos_contingencia': tipos_contingencia_json})
 