from rest_framework import serializers
from dtesv.models import Receptor

class ReceptorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receptor
        fields = '__all__'
