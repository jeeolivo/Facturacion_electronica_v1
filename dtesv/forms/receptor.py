### 2024-09-19: Se modifican datos del formulario para adecuarlo al requerimiento de MH para Sistema de Facturación v1.1

from django import forms
from dtesv.models import Receptor,C012Departamento,C013Municipio, C014Distritos

class ReceptorForm(forms.ModelForm):
    munidistrito = forms.ModelChoiceField(queryset=C014Distritos.objects.all(), required=False)
    municipio = forms.ModelChoiceField(queryset=C013Municipio.objects.all(), required=False)
    departamento = forms.ModelChoiceField(queryset=C012Departamento.objects.all(), required=False)

    class Meta:
        model = Receptor
        fields = ['tipodocumento',
            'numdocumento',
            'nrc',
            'nombre',
            'codactividad',
            'nombrecomercial',
            'telefono',
            'correo',
            'complemento',
            'municipio',
            'munidistrito',
            'departamento',
            'codpais',
            'tipopersona',
            'tiporeceptor',
            'codigo'
        ]

        # Esto me permite las personalizaciones de etiquetas (Como se vera el nombre del campo)
        labels = {
            'tipodocumento': 'Tipo de Documento',
            'numdocumento': 'Número de Documento',
            'nrc':'NRC',
            'nombrecomercial': 'Nombre Comercial',
            'codactividad': 'Actividad Económica',
            'codpais': 'País',
            'tipopersona': 'Figura Económica',
            'tiporeceptor': 'Categoria del Receptor',
            'municipio': 'Distrito',
            'munidistrito': 'Municipio',
        }
        

    def __init__(self, *args, **kwargs):
    # Permitir pasar valores iniciales a través de kwargs
        super().__init__(*args, **kwargs)

    # Agregar atributo 'id' al campo de correo electrónico
        self.fields['correo'].widget.attrs['id'] = 'id_correo'
    # Hacer el campo 'codigo' de solo lectura
        self.fields['codigo'].widget.attrs['readonly'] = True
    # Agregar clases CSS a los widgets de los campos
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           

