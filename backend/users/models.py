from django.conf import settings
from django.db import models


class CadastroPendente(models.Model):
    """Pedido de cadastro aguardando o cliente confirmar o e-mail."""

    email = models.EmailField()
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14)
    telefone = models.CharField(max_length=20)

    # Guardamos só o hash do token enviado por e-mail, nunca o token
    token_hash = models.CharField(max_length=64, unique=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    usado_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.email} ({self.criado_em:%d/%m/%Y %H:%M})"


class ReinicioSenha(models.Model):
    """Pedido de "esqueci minha senha" aguardando o cliente abrir o link."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reinicios_de_senha",
    )

    # Só o hash do token fica no banco; o token vai apenas por e-mail
    token_hash = models.CharField(max_length=64, unique=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    usado_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} ({self.criado_em:%d/%m/%Y %H:%M})"