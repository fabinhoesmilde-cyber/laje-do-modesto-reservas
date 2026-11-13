
from rest_framework import serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cliente
        fields = [
            'id',
            'nome',
            'cpf',
            'telefone',
            'email',
            'criado_em',
        ]

        read_only_fields = [
            'id',
            'criado_em',
        ]
