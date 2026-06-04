from django.db import models


class Cupom(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    tipo_desconto = models.CharField(max_length=20)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    uso_maximo = models.PositiveIntegerField()
    uso_atual = models.PositiveIntegerField(default=0)

    validade = models.DateField()
    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.codigo