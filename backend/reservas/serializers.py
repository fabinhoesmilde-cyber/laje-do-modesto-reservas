from rest_framework import serializers
from .models import (
    StatusReserva,
    Reserva,
    ReservaAdicional
)


class StatusReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusReserva
        fields = "__all__"


class ReservaAdicionalSerializer(serializers.ModelSerializer):

    nome = serializers.CharField(
        source="adicional.nome",
        read_only=True
    )

    class Meta:
        model = ReservaAdicional

        fields = (
            "nome",
            "quantidade",
            "valor_unitario_momento",
            "valor_total",
        )


class ReservaSerializer(serializers.ModelSerializer):

    cliente_nome = serializers.CharField(
        source="cliente.nome",
        read_only=True
    )

    telefone = serializers.CharField(
        source="cliente.telefone",
        read_only=True
    )

    email = serializers.EmailField(
        source="cliente.email",
        read_only=True
    )

    cpf = serializers.CharField(
        source="cliente.cpf",
        read_only=True
    )

    status_nome = serializers.CharField(
        source="status.nome",
        read_only=True
    )

    cupom_codigo = serializers.CharField(
        source="cupom.codigo",
        read_only=True
    )

    adicionais = ReservaAdicionalSerializer(
        source="reservaadicional_set",
        many=True,
        read_only=True
    )

    class Meta:
        model = Reserva
        fields = "__all__"