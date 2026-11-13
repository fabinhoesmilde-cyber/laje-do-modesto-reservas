
from django.db import models
from django.core.exceptions import ValidationError


class Cupom(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    tipo_desconto = models.CharField(max_length=20)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    desconto_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=None,
    )

    uso_maximo = models.PositiveIntegerField()
    uso_atual = models.PositiveIntegerField(default=0)

    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    validade = models.DateField()

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def clean(self):
        erros = {}

        if self.tipo_desconto not in ("fixo", "percentual"):
            erros["tipo_desconto"] = (
                "O tipo de desconto deve ser 'fixo' ou 'percentual'."
            )

        if self.valor is not None:
            if self.valor <= 0:
                erros["valor"] = (
                    "O valor do desconto deve ser maior que zero."
                )
            elif (
                self.tipo_desconto == "percentual"
                and self.valor > 100
            ):
                erros["valor"] = (
                    "O desconto percentual não pode ultrapassar 100%."
                )

        if (
            self.desconto_maximo is not None
            and self.desconto_maximo <= 0
        ):
            erros["desconto_maximo"] = (
                "O desconto máximo deve ser maior que zero."
            )

        if self.uso_maximo is not None and self.uso_maximo < 1:
            erros["uso_maximo"] = (
                "O limite de utilizações deve ser pelo menos 1."
            )

        if self.data_inicio and self.data_fim:
            if self.data_inicio > self.data_fim:
                erros["data_fim"] = (
                    "A data final não pode ser anterior à data inicial."
                )

        if self.data_fim and self.validade:
            if self.validade < self.data_fim:
                erros["validade"] = (
                    "A validade não pode terminar antes da data final."
                )

        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def calcular_desconto(self, subtotal):
        from decimal import Decimal

        subtotal = Decimal(str(subtotal))

        if subtotal <= Decimal("0.00"):
            return Decimal("0.00")

        if self.tipo_desconto == "percentual":
            desconto = subtotal * self.valor / Decimal("100")
        elif self.tipo_desconto == "fixo":
            desconto = self.valor
        else:
            return Decimal("0.00")

        if self.desconto_maximo is not None:
            desconto = min(desconto, self.desconto_maximo)

        # O desconto nunca pode superar o subtotal.
        desconto = min(desconto, subtotal)

        return desconto.quantize(Decimal("0.01"))

    def pode_ser_utilizado(self):
        from django.utils import timezone

        hoje = timezone.localdate()

        if not self.ativo:
            return False

        if not self.data_inicio or not self.data_fim:
            return False

        if hoje < self.data_inicio or hoje > self.data_fim:
            return False

        if hoje > self.validade:
            return False

        if self.uso_atual >= self.uso_maximo:
            return False

        return True

    def __str__(self):
        return self.codigo
