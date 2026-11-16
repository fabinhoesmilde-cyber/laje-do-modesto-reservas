from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from clientes.models import Cliente
from clientes.utils import formatar_cpf, somente_digitos

from .cadastro import erro
from .permissoes import IsCliente

# Igual para e-mail inexistente, senha errada, conta inativa ou da equipe:
# assim a resposta não revela quem é cliente.
MENSAGEM_LOGIN_INVALIDO = "E-mail ou senha incorretos."


class LoginThrottle(AnonRateThrottle):
    """Limita tentativas de login por endereço (IP), contra adivinhação."""
    scope = "login"
    rate = "20/hour"


def dados_do_cliente(cliente):
    cpf = formatar_cpf(cliente.cpf)

    return {
        "nome": cliente.nome,
        "email": cliente.email,
        "telefone": cliente.telefone,
        # CPF parcialmente escondido: o cliente se reconhece, mas quem
        # roubar o acesso não leva o número inteiro.
        "cpf": "***.***." + cpf[8:],
    }


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login_cliente(request):
    dados = request.data

    if not isinstance(dados, dict):
        return erro("Dados inválidos.")

    email = str(dados.get("email") or "").strip().lower()
    senha = str(dados.get("senha") or "")

    if not email or not senha:
        return erro("Informe o e-mail e a senha.")

    # authenticate já recusa contas desativadas
    usuario = authenticate(request=request, username=email, password=senha)

    if usuario is None or usuario.is_staff:
        return erro(MENSAGEM_LOGIN_INVALIDO, status.HTTP_401_UNAUTHORIZED)

    cliente = Cliente.objects.filter(user=usuario).first()

    if cliente is None:
        return erro(MENSAGEM_LOGIN_INVALIDO, status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=usuario)

    return Response({"token": token.key, "cliente": dados_do_cliente(cliente)})


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsCliente])
def logout_cliente(request):
    # Apaga o token: o acesso deste login deixa de valer
    Token.objects.filter(user=request.user).delete()

    return Response({"mensagem": "Você saiu da sua conta."})


@api_view(["GET", "PATCH"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsCliente])
def meus_dados(request):
    cliente = Cliente.objects.get(user=request.user)

    if request.method == "PATCH":
        dados = request.data

        if not isinstance(dados, dict):
            return erro("Dados inválidos.")

        # Só nome e telefone podem mudar por aqui. E-mail e CPF identificam
        # o cliente (e as reservas dele), então não são alterados.
        if "nome" in dados:
            nome = str(dados.get("nome") or "").strip()

            if not nome:
                return erro("O nome não pode ficar vazio.")

            if len(nome) > 150:
                return erro("O nome é muito longo.")

            cliente.nome = nome

        if "telefone" in dados:
            telefone = str(dados.get("telefone") or "").strip()

            if len(somente_digitos(telefone)) not in (10, 11):
                return erro("Telefone inválido. Informe o DDD e o número.")

            cliente.telefone = telefone

        cliente.save()

        request.user.first_name = cliente.nome[:150]
        request.user.save(update_fields=["first_name"])

    return Response(dados_do_cliente(cliente))