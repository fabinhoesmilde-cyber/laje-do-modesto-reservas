from django.db import models
from reservas.models import Reserva


class Pagamento(models.Model):

    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.PROTECT
    )

    forma_pagamento = models.CharField(
        max_length=50
    )

    status_pagamento = models.CharField(
        max_length=30
    )

    valor_pago = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    data_pagamento = models.DateTimeField()

    codigo_transacao = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    observacao = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    

    def __str__(self):
        return f"{self.reserva} - R$ {self.valor_pago}"
