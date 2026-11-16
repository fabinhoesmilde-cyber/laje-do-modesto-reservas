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