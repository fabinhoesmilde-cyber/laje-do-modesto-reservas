from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response

from clientes.models import Cliente
from reservas.models import Reserva, ReservaAdicional
from reservas.regras import calcular_cancelamento

from .permissoes import IsCliente


def dinheiro(valor):
    """Valores em reais viajam como texto ("700.00"), sem erro de arredondamento."""
    return None if valor is None else str(valor)


def previa_do_cancelamento(reserva):
    """
    Mostra ao cliente, antes de ele decidir, quanto pagaria de taxa e
    quanto receberia de volta se cancelasse agora.
    """
    resultado = calcular_cancelamento(
        reserva.data_reserva, reserva.valor_total
    )

    return {
        "dentro_do_prazo": resultado["dentro_do_prazo"],
        "taxa": dinheiro(resultado["taxa"]),
        "reembolso": dinheiro(resultado["reembolso"]),
    }


def dados_da_reserva(reserva, detalhado=False):
    nome_status = reserva.status.nome

    # Só dá para mexer numa reserva confirmada e que ainda não aconteceu
    futura_confirmada = (
        nome_status == "CONFIRMADA"
        and reserva.data_reserva >= timezone.localdate()
    )

    dados = {
        "codigo_reserva": reserva.codigo_reserva,
        "status": nome_status,
        "data_reserva": reserva.data_reserva,
        "hora_inicio": reserva.hora_inicio.strftime("%H:%M"),
        "hora_fim": reserva.hora_fim.strftime("%H:%M"),
        "valor_total": dinheiro(reserva.valor_total),
        "pode_cancelar": futura_confirmada,
        "pode_alterar": futura_confirmada,
    }

    if futura_confirmada:
        dados["previa_cancelamento"] = previa_do_cancelamento(reserva)

    if nome_status == "ALTERACAO_SOLICITADA":
        dados["alteracao_solicitada"] = {
            "nova_data": reserva.nova_data_solicitada,
            "novo_horario_inicio": (
                reserva.novo_horario_inicio_solicitado.strftime("%H:%M")
                if reserva.novo_horario_inicio_solicitado else None
            ),
        }

    if nome_status in ("CANCELAMENTO_SOLICITADO", "CANCELADA"):
        dados["taxa_cancelamento"] = dinheiro(reserva.taxa_cancelamento)
        dados["valor_reembolso"] = dinheiro(reserva.valor_reembolso)
        dados["cancelado_em"] = reserva.cancelado_em

    if detalhado:
        dados.update({
            "valor_base": dinheiro(reserva.valor_base),
            "valor_desconto": dinheiro(reserva.valor_desconto),
            "valor_adicionais": dinheiro(reserva.valor_adicionais),
            "horas_extras": reserva.horas_extras,
            "adicionais": [
                {
                    "nome": item.adicional.nome,
                    "quantidade": item.quantidade,
                    "valor_total": dinheiro(item.valor_total),
                }
                for item in ReservaAdicional.objects.filter(
                    reserva=reserva
                ).select_related("adicional")
            ],
        })

    return dados


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsCliente])
def minhas_reservas(request):
    cliente = Cliente.objects.get(user=request.user)

    reservas = Reserva.objects.filter(cliente=cliente).select_related(
        "status"
    ).order_by("-data_reserva", "-hora_inicio")

    return Response([dados_da_reserva(reserva) for reserva in reservas])


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsCliente])
def detalhe_reserva(request, codigo):
    cliente = Cliente.objects.get(user=request.user)

    # Filtra pelo dono: reserva de outra pessoa responde igual a uma que
    # não existe, para não revelar quais códigos são válidos.
    reserva = Reserva.objects.select_related("status").filter(
        cliente=cliente,
        codigo_reserva=codigo,
    ).first()

    if reserva is None:
        return Response(
            {"erro": "Reserva não encontrada."},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(dados_da_reserva(reserva, detalhado=True))