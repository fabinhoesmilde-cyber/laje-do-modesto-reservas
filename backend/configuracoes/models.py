from django.db import models


class Configuracao(models.Model):

    valor_reserva = models.DecimalField(
        "Valor da Reserva",
        max_digits=10,
        decimal_places=2,
        default=700
    )

    valor_hora_extra = models.DecimalField(
        "Valor da Hora Extra",
        max_digits=10,
        decimal_places=2,
        default=60
    )

    duracao_reserva = models.PositiveIntegerField(
        "Duração da Reserva (horas)",
        default=8
    )

    horario_limite = models.TimeField(
        "Horário Limite",
        default="05:00"
    )

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"

    def __str__(self):
        return "Configuração Geral"