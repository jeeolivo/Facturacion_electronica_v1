from rest_framework import serializers
from dtesv.models import Documentos, DocumentosDetalle

class DocumentosDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentosDetalle
        fields = '__all__'

class DocumentosSerializer(serializers.ModelSerializer):
    detalle = DocumentosDetalleSerializer(many=True)

    class Meta:
        model = Documentos
        fields = '__all__'

    def create(self, validated_data):
        # detalle_data = validated_data.pop('detalle', [])
        # codigo_generacion = validated_data.get('codigoGeneracion')

        # documento, _ = Documentos.objects.get_or_create(
        #     codigoGeneracion=codigo_generacion,
        #     defaults=validated_data
        # )

        # for detalle_item in detalle_data:
        #     num_item = detalle_item.pop('numItem')
        #     DocumentosDetalle.objects.update_or_create(
        #         codigoGeneracion_id=documento,
        #         numItem=num_item,
        #         defaults=detalle_item
        #     )

        # return documento
        detalle_data = validated_data.pop('detalle', [])
        documento = Documentos.objects.create(**validated_data)

        for detalle_item in detalle_data:
            detalle_item['codigoGeneracion_id'] = documento
            DocumentosDetalle.objects.create(**detalle_item)

        return documento
    
    def update(self, instance, validated_data):
        detalle_data = validated_data.pop('detalle', [])
       # DocumentosDetalle.objects.update(**validated_data)
        #instance.save()

        for detalle_item_data in detalle_data:
            detalle_item_codigo = detalle_item_data.pop('numItem')

            # Busca si existe un objeto con la misma clave primaria
            try:
                detalle_item = DocumentosDetalle.objects.get(
                    codigoGeneracion_id=instance,
                    numItem=detalle_item_codigo
                )
            except DocumentosDetalle.DoesNotExist:
                detalle_item = None

            if detalle_item:
                # Si el objeto existe, actualiza sus atributos
                for attr, value in detalle_item_data.items():
                    setattr(detalle_item, attr, value)
                detalle_item.save()
            else:
                # Si no existe, crea un nuevo objeto
                detalle_item_data['codigoGeneracion_id'] = instance
                DocumentosDetalle.objects.create(**detalle_item_data)
                
        return instance
        