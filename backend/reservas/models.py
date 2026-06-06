import uuid
from django.db import models
from clientes.models import Cliente
from cupons.models import Cupom
from adicionais.models import Adicional


class StatusReserva(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Status da Reserva"
        verbose_name_plural = "Status das Reservas"

    def __str__(self):
        return self.nome


class Reserva(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT
    )

    status = models.ForeignKey(
        StatusReserva,
        on_delete=models.PROTECT
    )

    cupom = models.ForeignKey(
        Cupom,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    data_reserva = models.DateField()

    hora_inicio = models.TimeField()

    hora_fim = models.TimeField()

    nova_data_solicitada = models.DateField(
        null=True,
        blank=True
    )

    novo_horario_inicio_solicitado = models.TimeField(
        null=True,
        blank=True
    )

    novo_horario_fim_solicitado = models.TimeField(
        null=True,
        blank=True
    )

    valor_base = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    valor_desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    valor_adicionais = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    observacao = models.TextField(
        blank=True,
        null=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    codigo_reserva = models.CharField(
    max_length=20,
    unique=True,
    blank=True,
    null=True
)
    def save(self, *args, **kwargs):
        if not self.codigo_reserva:
            self.codigo_reserva = f"LDM-{uuid.uuid4().hex[:8].upper()}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente.nome} - {self.data_reserva}"
    
class ReservaAdicional(models.Model):
        
    reserva = models.ForeignKey(
    Reserva,
    on_delete=models.CASCADE
    )

    adicional = models.ForeignKey(
        Adicional,
        on_delete=models.PROTECT
    )

    quantidade = models.PositiveIntegerField(default=1)

    valor_unitario_momento = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Adicional da Reserva"
        verbose_name_plural = "Adicionais da Reserva"


    def __str__(self):
        return f"{self.reserva} - {self.adicional}"