from venv import logger
from django.shortcuts import render, get_object_or_404, redirect
from dtesv.models import Receptor, Proveedor, C012Departamento, C013Municipio, C014Distritos
from dtesv.forms import ReceptorForm

def edit_receptor(request, codigo, tipo_receptor):
    usuario = request.user
    form = None
    mensaje_exito = None
    logger.error(f"Edicion_Receptor, los siguientes datos se procesaran {tipo_receptor} {codigo}")


    # 2024-09-09: Aquí diferenciamos entre cliente y proveedor según el tipo_receptor
    if usuario.has_perm('dtesv.view_receptor') or usuario.has_perm('dtesv.change_receptor'):
        # Diferenciación entre cliente y proveedor según el campo 'tiporeceptor'
        if tipo_receptor == 'cliente':
            receptor = get_object_or_404(Receptor, codigo=codigo, tiporeceptor='cliente')
        elif tipo_receptor == 'proveedor':
            receptor = get_object_or_404(Proveedor, codigo=codigo, tiporeceptor='proveedor')
        elif tipo_receptor == 'empleado':
            receptor = get_object_or_404(Proveedor, codigo=codigo, tiporeceptor='empleado')
        elif tipo_receptor == 'excluido':
            receptor = get_object_or_404(Proveedor, codigo=codigo, tiporeceptor='excluido')            
        else:
            logger.error(f"Tipo de receptor inválido: {tipo_receptor}")
            receptor = None
        
        if receptor:
            if request.method == 'POST':
                put_data = request.POST.copy()
                #logger.error(f"Datos del POST: {put_data}", exc_info=True)

                if put_data.get('_method') == 'PUT':
                    put_data.pop('_method')  # Elimina el campo _method
                    put_data.update({'codigo': codigo})  # Añade el código para identificar el receptor

                    form = ReceptorForm(put_data, instance=receptor)
                    if form.is_valid():
                        fields_list = list(form.changed_data)  # Obtiene los campos modificados
                        #logger.error(f"Estos son los campos a modificar: {fields_list}", exc_info=True)
                        if fields_list:  # Si hay cambios
                            receptor.save(update_fields=fields_list)  # Actualiza solo los campos modificados
                            mensaje_exito = 'Cambios guardados.'
                else:
                    form = ReceptorForm(instance=receptor)
            else:
                form = ReceptorForm(instance=receptor)

            # Obtener el departamento, municipio y distrito seleccionados del receptor
            departamentos = C012Departamento.objects.all()
            #logger.error(f"departamentos: {departamentos}")
            departamento_seleccionado = receptor.departamento.codigo  # Usar el código en lugar del objeto completo
            #logger.error(f"departamento {receptor.departamento} codigo departamento: {departamento_seleccionado}")
            
            municipio_seleccionado = receptor.municipio.id if receptor.municipio else None # Usar el código en lugar del objeto completo
            #logger.error(f"municipio {receptor.municipio} codigo exMunicipio: {municipio_seleccionado}")
            municipios = C013Municipio.objects.filter(cod_departamento_id=departamento_seleccionado) if departamento_seleccionado else []
            #logger.error(f"municipios: {municipios}")

            distrito_seleccionado = receptor.munidistrito.id if receptor.munidistrito else None
            #logger.error(f"distrito {receptor.munidistrito} codigo municipio: {distrito_seleccionado}")
            distritos = C014Distritos.objects.filter(cod_departamento_id=departamento_seleccionado) if departamento_seleccionado else [] #(id=distrito_seleccionado) if distrito_seleccionado else []
            #logger.error(f"distritos: {distritos}")
                
        else:
            logger.error("Receptor no encontrado")
            return redirect('error_template.html')
    
    return render(request, 'editar_receptor.html', {
        'form': form, 
        'mensaje_exito': mensaje_exito,
        'tipo_receptor': tipo_receptor,
        'departamento': departamento_seleccionado,  # Valor del departamento seleccionado
        'municipio': municipio_seleccionado,  # Valor del municipio seleccionado
        'munidistrito': distrito_seleccionado,  # Valor del distrito seleccionado
        'departamentos': departamentos,  # Lista de todos los departamentos
        'municipios': municipios,  # Lista de municipios filtrados
        'distritos': distritos  # Lista de distritos filtrados
    })