from django.db import transaction
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response

from clientes.models import Cliente
from reservas.acoes import ErroDeRegra, cancelar_reserva, pedir_alteracao
from reservas.models import Reserva

from .permissoes import IsCliente


def reserva_do_cliente(usuario, codigo):
    """
    Acha a reserva travada para escrita, mas só se for do cliente logado.
    Reserva de outra pessoa é tratada como inexistente.
    """
    cliente = Cliente.objects.get(user=usuario)

    return Reserva.objects.select_for_update().filter(
        cliente=cliente,
        codigo_reserva=codigo,
    ).first()


def nao_encontrada():
    return Response(
        {"erro": "Reserva não encontrada."},
        status=status.HTTP_404_NOT_FOUND
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsCliente])
@transaction.atomic
def cancelar_minha_reserva(request, codigo):
    reserva = reserva_do_cliente(request.user, codigo)

    if reserva is None:
        return nao_encontrada()

    try:
        resultado = cancelar_reserva(reserva)
    except ErroDeRegra as erro:
        return Response({"erro": erro.mensagem}, status=erro.codigo)

    return Response(resultado)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsCliente])
@transaction.atomic
def alterar_minha_reserva(request, codigo):
    dados = request.data

    if not isinstance(dados, dict):
        return Response(
            {"erro": "Dados inválidos."},
            status=status.HTTP_400_BAD_REQUEST
        )

    reserva = reserva_do_cliente(request.user, codigo)

    if reserva is None:
        return nao_encontrada()

    # O horário de fim, se vier, é ignorado: o servidor calcula.
    try:
        resultado = pedir_alteracao(
            reserva,
            dados.get("nova_data"),
            dados.get("novo_horario_inicio"),
        )
    except ErroDeRegra as erro:
        return Response({"erro": erro.mensagem}, status=erro.codigo)

    return Response(resultado)