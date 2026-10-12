
from rest_framework import serializers
from .models import DiaBloqueado


class DiaBloqueadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaBloqueado
        fields = "__all__"
