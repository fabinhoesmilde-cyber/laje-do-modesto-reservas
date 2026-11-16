from django.conf import settings
from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    # Conta de acesso do cliente (opcional: quem reservou como visitante
    # não tem conta). Se a conta for apagada, o cliente e as reservas ficam.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cliente",
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome