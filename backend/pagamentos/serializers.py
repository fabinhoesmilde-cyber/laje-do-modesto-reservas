
from rest_framework import serializers
from .models import Pagamento


class PagamentoSerializer(serializers.ModelSerializer):

    cliente_nome = serializers.CharField(
        source='reserva.cliente.nome',
        read_only=True
    )

    data_reserva = serializers.DateField(
        source='reserva.data_reserva',
        read_only=True
    )

    status_reserva = serializers.CharField(
        source='reserva.status.nome',
        read_only=True
    )

    class Meta:
        model = Pagamento
        fields = '__all__'

        read_only_fields = [
            'created_at',
            'reserva',
            'forma_pagamento',
            'status_pagamento',
            'valor_pago',
            'data_pagamento',
            'codigo_transacao',
            'cliente_nome',
            'data_reserva',
            'status_reserva',
        ]
