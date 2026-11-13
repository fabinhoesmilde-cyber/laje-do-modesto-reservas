from django.db import models


class ConfiguracaoReserva(models.Model):

    valor_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=700.00
    )

    valor_hora_extra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=60.00
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        # Sempre será utilizada a configuração de ID 1
        self.pk = 1

        super().save(*args, **kwargs)

    def __str__(self):
        return "Configuração de Valores da Reserva"