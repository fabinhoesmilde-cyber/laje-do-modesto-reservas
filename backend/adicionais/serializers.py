from rest_framework import serializers
from .models import Adicional


class AdicionalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Adicional
        fields = '__all__'

        read_only_fields = [
            'criado_em',
        ]