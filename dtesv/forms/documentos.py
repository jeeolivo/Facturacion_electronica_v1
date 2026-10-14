from django import forms
from dtesv.models import Documentos,DocumentosDetalle


class DocumentosForm(forms.ModelForm):
    class Meta:
        model = Documentos
        fields = '__all__'
        #exclude = ['codigoGeneracion']  # Excluye el campo clave principal
    detalle = forms.ModelChoiceField(queryset=DocumentosDetalle.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limita el queryset de detalle a los detalles relacionados con el documento actual
        if self.instance and self.instance.pk:
            detalle = DocumentosDetalle.objects.filter(codigoGeneracion_id=self.instance.codigoGeneracion)
            self.fields['detalle'].queryset = detalle
    # Puedes agregar personalizaciones o validaciones aquí si es necesario
