from django.shortcuts import render, get_object_or_404, redirect
from dtesv.models import Documentos , DocumentosDetalle
from dtesv.forms import DocumentosForm
from django.forms.models import model_to_dict

def edit_Documento(request, codigoGeneracion):
    usuario = request.user
    form = None
    mensaje_exito = None

    if usuario.has_perm('dtesv.view_documentos') or usuario.has_perm('dtesv.change_documentos'):
        documento = get_object_or_404(Documentos, codigoGeneracion = codigoGeneracion)
        detalle_queryset = DocumentosDetalle.objects.filter(codigoGeneracion_id=documento.codigoGeneracion)



        # Puedes agregar valores extras al formulario utilizando el atributo initial
        initial_values = {
            'nombre_cliente': 'Mi Nombre',
            'tipoDocuemto': 'Factura',
            # Agrega más valores según sea necesario
        }

        # Combina los valores extras con los valores iniciales del modelo
        initial_values.update(model_to_dict(documento))

        form = DocumentosForm(instance=documento, initial=initial_values)
        if request.method == 'POST':
            put_data = request.POST.copy()
            if put_data.get('_method') == 'PUT':
                put_data.pop('_method')  # Elimina el campo _method
                put_data.update({'codigoGeneracion': codigoGeneracion})  # Añade el código para identificar el receptor

                form = DocumentosForm(put_data, instance=documento)
                if form.is_valid():
                    fields_list = list(form.changed_data)  # Obtiene los campos modificados
                    if fields_list:  # Si hay cambios
                        documento.save(update_fields=fields_list)  # Actualiza solo los campos modificados
                        mensaje_exito = 'Cambios guardados.'
            else:
                form = DocumentosForm(instance=documento)
        #else:
        #    form = DocumentosForm(instance=documento)
    
    return render(request, 'editar_documento.html', {'form': form, 'mensaje_exito': mensaje_exito,'detalle_queryset': detalle_queryset})

