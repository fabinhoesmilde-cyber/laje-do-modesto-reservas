import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import CadastroPendente

VALIDADE_CONFIRMACAO_HORAS = 24


def gerar_hash(token):
    """
    O token vai por e-mail em texto puro, mas no banco guardamos só o
    "hash" dele. Assim, se o banco vazar, ninguém consegue usar os links.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def criar_cadastro_pendente(email, nome, cpf, telefone):
    """Guarda o pedido de cadastro e devolve o token (texto puro)."""
    # Um pedido novo cancela o anterior ainda não usado do mesmo e-mail
    CadastroPendente.objects.filter(
        email__iexact=email,
        usado_em__isnull=True,
    ).delete()

    token = secrets.token_urlsafe(32)

    CadastroPendente.objects.create(
        email=email,
        nome=nome,
        cpf=cpf,
        telefone=telefone,
        token_hash=gerar_hash(token),
        expira_em=timezone.now() + timedelta(
            hours=VALIDADE_CONFIRMACAO_HORAS
        ),
    )

    return token


def enviar_email_confirmacao(email, nome, token):
    """Envia o link para o cliente confirmar o e-mail e criar a senha."""
    base = settings.FRONTEND_URL.rstrip("/")
    link = f"{base}/confirmar-cadastro.html?token={token}"

    mensagem = (
        f"Olá, {nome}!\n\n"
        "Para concluir seu cadastro na Laje do Modesto e criar sua senha, "
        "acesse o link abaixo "
        f"(válido por {VALIDADE_CONFIRMACAO_HORAS} horas):\n\n"
        f"{link}\n\n"
        "Se você não pediu este cadastro, ignore este e-mail."
    )

    send_mail(
        subject="Confirme seu cadastro - Laje do Modesto",
        message=mensagem,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )