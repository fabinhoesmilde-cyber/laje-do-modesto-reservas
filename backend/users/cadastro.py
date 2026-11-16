import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.utils import timezone
from rest_framework import status
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
from clientes.utils import cpf_valido, formatar_cpf, somente_digitos

from .models import CadastroPendente
from .servicos import (
    criar_cadastro_pendente,
    enviar_email_confirmacao,
    gerar_hash,
)

logger = logging.getLogger(__name__)

# A resposta é sempre a mesma, exista ou não uma conta com aquele e-mail.
# Assim, ninguém consegue descobrir quem é cliente testando e-mails.
MENSAGEM_CADASTRO = (
    "Enviamos um link de confirmação para o e-mail informado. "
    "Confira sua caixa de entrada e o spam."
)


# Link inexistente, vencido ou já usado: a resposta não diz qual dos casos
MENSAGEM_LINK_INVALIDO = (
    "Link inválido ou expirado. Faça o cadastro novamente."
)

MENSAGEM_CPF_EM_USO = (
    "Não foi possível concluir o cadastro. "
    "Entre em contato com a Laje do Modesto."
)


class CadastroThrottle(AnonRateThrottle):
    """Limita quantos cadastros um mesmo endereço (IP) pode pedir."""
    scope = "cadastro"


class ConfirmacaoThrottle(AnonRateThrottle):
    """Limita as tentativas de confirmar o cadastro."""
    scope = "confirmacao"
    rate = "20/hour"


def erro(mensagem, codigo=status.HTTP_400_BAD_REQUEST):
    return Response({"erro": mensagem}, status=codigo)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([CadastroThrottle])
def cadastro_cliente(request):
    """
    Primeiro passo do cadastro: recebe os dados e manda um e-mail com
    o link para confirmar e criar a senha. Nenhuma conta é criada ainda.
    """
    dados = request.data

    if not isinstance(dados, dict):
        return erro("Dados inválidos.")

    nome = str(dados.get("nome") or "").strip()
    email = str(dados.get("email") or "").strip().lower()
    cpf = str(dados.get("cpf") or "").strip()
    telefone = str(dados.get("telefone") or "").strip()

    if not nome or not email or not cpf or not telefone:
        return erro("Nome, e-mail, CPF e telefone são obrigatórios.")

    if len(nome) > 150:
        return erro("O nome é muito longo.")

    try:
        validate_email(email)
    except ValidationError:
        return erro("E-mail inválido.")

    if not cpf_valido(cpf):
        return erro("CPF inválido.")

    if len(somente_digitos(telefone)) not in (10, 11):
        return erro("Telefone inválido. Informe o DDD e o número.")

    cpf_formatado = formatar_cpf(cpf)

    # Já existe uma conta com este e-mail: respondemos igual a um cadastro
    # novo, sem enviar nada nem alterar nada.
    Usuario = get_user_model()

    if Usuario.objects.filter(username__iexact=email).exists():
        return Response(
            {"mensagem": MENSAGEM_CADASTRO},
            status=status.HTTP_201_CREATED
        )

    # O CPF não pode pertencer a um cliente com outro e-mail (poderia ser
    # outra pessoa). A mensagem é genérica de propósito.
    cpf_de_outro = Cliente.objects.filter(
        cpf__in=[cpf_formatado, somente_digitos(cpf)]
    ).exclude(email__iexact=email).exists()

    if cpf_de_outro:
        return erro(MENSAGEM_CPF_EM_USO)

    try:
        with transaction.atomic():
            token = criar_cadastro_pendente(
                email=email,
                nome=nome,
                cpf=cpf_formatado,
                telefone=telefone,
            )
            enviar_email_confirmacao(email, nome, token)
    except Exception:
        # Se o e-mail não saiu, o pedido também é desfeito
        logger.exception("Falha ao enviar o e-mail de confirmação.")
        return erro(
            "Não foi possível enviar o e-mail agora. Tente novamente.",
            status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return Response(
        {"mensagem": MENSAGEM_CADASTRO},
        status=status.HTTP_201_CREATED
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([ConfirmacaoThrottle])
@transaction.atomic
def confirmar_cadastro(request):
    """
    Segundo passo: o cliente abriu o link do e-mail e escolheu a senha.
    Só agora a conta é criada e ligada ao cliente.
    """
    dados = request.data

    if not isinstance(dados, dict):
        return erro("Dados inválidos.")

    token = str(dados.get("token") or "").strip()
    senha = str(dados.get("senha") or "")

    if not token or not senha:
        return erro("O link e a senha são obrigatórios.")

    # Procura o pedido pelo hash do token: ainda não usado e dentro da validade
    pedido = CadastroPendente.objects.select_for_update().filter(
        token_hash=gerar_hash(token),
        usado_em__isnull=True,
        expira_em__gt=timezone.now(),
    ).first()

    if not pedido:
        return erro(MENSAGEM_LINK_INVALIDO)

    Usuario = get_user_model()

    if Usuario.objects.filter(username__iexact=pedido.email).exists():
        return erro(MENSAGEM_LINK_INVALIDO)

    # A senha precisa passar nas regras do Django (tamanho, não ser comum...)
    usuario_teste = Usuario(
        username=pedido.email,
        email=pedido.email,
        first_name=pedido.nome[:150],
    )

    try:
        validate_password(senha, user=usuario_teste)
    except ValidationError as problema:
        return erro(" ".join(problema.messages))

    # Se o cliente já reservou como visitante com este e-mail, a conta
    # passa a ser dele. Senão, criamos um cliente novo.
    cliente = Cliente.objects.filter(email__iexact=pedido.email).first()

    if cliente is None:
        cpf_de_outro = Cliente.objects.filter(
            cpf__in=[pedido.cpf, somente_digitos(pedido.cpf)]
        ).exists()

        if cpf_de_outro:
            return erro(MENSAGEM_CPF_EM_USO)

    elif cliente.user_id is not None:
        return erro(MENSAGEM_LINK_INVALIDO)

    # Daqui para baixo gravamos; tudo acima só conferiu.
    usuario = Usuario.objects.create_user(
        username=pedido.email,
        email=pedido.email,
        password=senha,
        first_name=pedido.nome[:150],
    )

    if cliente is None:
        Cliente.objects.create(
            nome=pedido.nome,
            cpf=pedido.cpf,
            telefone=pedido.telefone,
            email=pedido.email,
            user=usuario,
        )
    else:
        cliente.user = usuario
        cliente.save(update_fields=["user"])

    pedido.usado_em = timezone.now()
    pedido.save(update_fields=["usado_em"])

    return Response(
        {"mensagem": "Cadastro concluído. Agora você já pode entrar."},
        status=status.HTTP_201_CREATED
    )