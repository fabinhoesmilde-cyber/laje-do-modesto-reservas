from django.utils import timezone
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from dias_bloqueados.models import DiaBloqueado

from .models import Reserva


class DisponibilidadeThrottle(AnonRateThrottle):
    scope = "disponibilidade_publica"
    rate = "300/hour"


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([DisponibilidadeThrottle])
def disponibilidade(request):
    """
    Lista as datas que o calendário do site deve mostrar como indisponíveis:
    datas com reserva ativa (a Laje aceita uma reserva por dia) e datas
    bloqueadas pelo administrador.

    Rota pública, por isso devolve SOMENTE as datas, nunca dados de
    clientes ou das reservas. Reservas canceladas e datas passadas ficam
    de fora.
    """
    hoje = timezone.localdate()

    reservadas = Reserva.objects.filter(
        data_reserva__gte=hoje
    ).exclude(
        status__nome="CANCELADA"
    ).values_list("data_reserva", flat=True)

    bloqueadas = DiaBloqueado.objects.filter(
        data__gte=hoje
    ).values_list("data", flat=True)

    datas = sorted({data.isoformat() for data in [*reservadas, *bloqueadas]})

    return Response({"datas_indisponiveis": datas})