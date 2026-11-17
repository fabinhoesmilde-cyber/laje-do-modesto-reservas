from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


def criar_login_do_cliente(cliente):
    """
    Cria uma conta para o cliente e devolve o cabeçalho de login, pronto
    para usar nas chamadas de teste: self.client.post(..., **cabecalho).
    """
    usuario = get_user_model().objects.create_user(
        username=cliente.email,
        email=cliente.email,
        password="Senha-De-Teste-2026!",
    )
    cliente.user = usuario
    cliente.save(update_fields=["user"])

    token = Token.objects.create(user=usuario)

    return {"HTTP_AUTHORIZATION": f"Token {token.key}"}