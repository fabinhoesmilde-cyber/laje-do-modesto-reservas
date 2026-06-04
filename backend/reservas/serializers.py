from rest_framework import serializers
from .models import StatusReserva, Reserva


class StatusReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusReserva
        fields = '__all__'


class ReservaSerializer(serializers.ModelSerializer):

    cliente_nome = serializers.CharField(
        source='cliente.nome',
        read_only=True
    )

    status_nome = serializers.CharField(
        source='status.nome',
        read_only=True
    )

    cupom_codigo = serializers.CharField(
        source='cupom.codigo',
        read_only=True
    )

    class Meta:
        model = Reserva
        fields = '__all__'