import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import status
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

from .cadastro import erro
from .models import ReinicioSenha
from .servicos import gerar_hash

logger = logging.getLogger(__name__)

VALIDADE_REDEFINICAO_HORAS = 1

# Depois de um pedido, o próximo só vale após este intervalo. Evita que
# alguém use o site para lotar a caixa de e-mail de outra pessoa.
INTERVALO_MINIMO_MINUTOS = 2

# A resposta é a mesma exista ou não a conta: ninguém descobre quem é
# cliente testando e-mails.
MENSAGEM_ESQUECI_SENHA = (
    "Se existir uma conta com este e-mail, enviamos um link para criar "
    "uma nova senha. Confira a caixa de entrada e o spam."
)

MENSAGEM_LINK_INVALIDO = (
    "Link inválido ou expirado. Peça um novo link de recuperação."
)


class EsqueciSenhaThrottle(AnonRateThrottle):
    scope = "esqueci_senha"
    rate = "5/hour"


class RedefinirSenhaThrottle(AnonRateThrottle):
    scope = "redefinir_senha"
    rate = "20/hour"


def conta_de_cliente_ativa(usuario):
    return bool(
        usuario.is_active
        and not usuario.is_staff
        and Cliente.objects.filter(user=usuario).exists()
    )


def criar_reinicio(usuario):
    """Guarda o pedido e devolve o token (texto puro). Anula os anteriores."""
    ReinicioSenha.objects.filter(
        user=usuario,
        usado_em__isnull=True,
    ).delete()

    token = secrets.token_urlsafe(32)

    ReinicioSenha.objects.create(
        user=usuario,
        token_hash=gerar_hash(token),
        expira_em=timezone.now() + timedelta(
            hours=VALIDADE_REDEFINICAO_HORAS
        ),
    )

    return token


def enviar_email_reinicio(usuario, token):
    base = settings.FRONTEND_URL.rstrip("/")
    link = f"{base}/redefinir_senha.html?token={token}"
    nome = usuario.first_name or "cliente"

    mensagem = (
        f"Olá, {nome}!\n\n"
        "Recebemos um pedido para criar uma nova senha na Laje do Modesto. "
        "Acesse o link abaixo "
        f"(válido por {VALIDADE_REDEFINICAO_HORAS} hora):\n\n"
        f"{link}\n\n"
        "Se você não pediu isso, ignore este e-mail: sua senha continua "
        "a mesma."
    )

    send_mail(
        subject="Nova senha - Laje do Modesto",
        message=mensagem,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[usuario.email],
        fail_silently=False,
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([EsqueciSenhaThrottle])
def esqueci_senha(request):
    dados = request.data

    if not isinstance(dados, dict):
        return erro("Dados inválidos.")

    email = str(dados.get("email") or "").strip().lower()

    if not email:
        return erro("Informe o e-mail.")

    resposta = Response(
        {"mensagem": MENSAGEM_ESQUECI_SENHA},
        status=status.HTTP_200_OK
    )

    usuario = get_user_model().objects.filter(
        username__iexact=email
    ).first()

    if usuario is None or not conta_de_cliente_ativa(usuario):
        return resposta

    limite = timezone.now() - timedelta(minutes=INTERVALO_MINIMO_MINUTOS)

    if ReinicioSenha.objects.filter(
        user=usuario, criado_em__gt=limite
    ).exists():
        return resposta

    try:
        with transaction.atomic():
            token = criar_reinicio(usuario)
            enviar_email_reinicio(usuario, token)
    except Exception:
        # Falha de e-mail não pode mudar a resposta (revelaria a conta).
        # O pedido é desfeito junto com a transação.
        logger.exception("Falha ao enviar o e-mail de nova senha.")

    return resposta


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([RedefinirSenhaThrottle])
@transaction.atomic
def redefinir_senha(request):
    dados = request.data

    if not isinstance(dados, dict):
        return erro("Dados inválidos.")

    token = str(dados.get("token") or "").strip()
    senha = str(dados.get("senha") or "")

    if not token or not senha:
        return erro("O link e a nova senha são obrigatórios.")

    pedido = ReinicioSenha.objects.select_for_update().filter(
        token_hash=gerar_hash(token),
        usado_em__isnull=True,
        expira_em__gt=timezone.now(),
    ).first()

    if pedido is None:
        return erro(MENSAGEM_LINK_INVALIDO)

    usuario = pedido.user

    if not conta_de_cliente_ativa(usuario):
        return erro(MENSAGEM_LINK_INVALIDO)

    try:
        validate_password(senha, user=usuario)
    except ValidationError as problema:
        # O link continua valendo para o cliente tentar outra senha
        return erro(" ".join(problema.messages))

    usuario.set_password(senha)
    usuario.save(update_fields=["password"])

    # Quem tinha a senha antiga (inclusive um invasor) perde o acesso
    Token.objects.filter(user=usuario).delete()

    pedido.usado_em = timezone.now()
    pedido.save(update_fields=["usado_em"])

    ReinicioSenha.objects.filter(
        user=usuario,
        usado_em__isnull=True,
    ).delete()

    return Response(
        {"mensagem": "Senha alterada. Agora você já pode entrar."}
    )