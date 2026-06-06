from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import StatusReserva, Reserva
from .serializers import StatusReservaSerializer, ReservaSerializer


class StatusReservaViewSet(viewsets.ModelViewSet):
    queryset = StatusReserva.objects.all()
    serializer_class = StatusReservaSerializer


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer


@api_view(['POST'])
def consultar_reserva(request):
    cpf = request.data.get('cpf')
    codigo_reserva = request.data.get('codigo_reserva')

    if not cpf or not codigo_reserva:
        return Response(
            {'erro': 'CPF e código da reserva são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    reserva = Reserva.objects.filter(
        cliente__cpf=cpf,
        codigo_reserva=codigo_reserva
    ).first()

    if not reserva:
        return Response(
            {'erro': 'Reserva não encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({
        'codigo_reserva': reserva.codigo_reserva,
        'data_reserva': reserva.data_reserva,
        'hora_inicio': reserva.hora_inicio,
        'hora_fim': reserva.hora_fim,
        'status': reserva.status.nome,
    })
@api_view(['POST'])
def solicitar_cancelamento(request):
    cpf = request.data.get('cpf')
    codigo_reserva = request.data.get('codigo_reserva')

    if not cpf or not codigo_reserva:
        return Response(
            {'erro': 'CPF e código da reserva são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    reserva = Reserva.objects.filter(
        cliente__cpf=cpf,
        codigo_reserva=codigo_reserva
    ).first()

    if not reserva:
        return Response(
            {'erro': 'Reserva não encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    status_cancelamento = StatusReserva.objects.filter(
        nome='CANCELAMENTO_SOLICITADO'
    ).first()

    if not status_cancelamento:
        return Response(
            {'erro': 'Status CANCELAMENTO_SOLICITADO não encontrado.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    reserva.status = status_cancelamento
    reserva.save()

    return Response({
        'mensagem': 'Solicitação de cancelamento enviada com sucesso.',
        'codigo_reserva': reserva.codigo_reserva,
        'status': reserva.status.nome
    })
@api_view(['POST'])
def solicitar_alteracao(request):
    cpf = request.data.get('cpf')
    codigo_reserva = request.data.get('codigo_reserva')
    nova_data = request.data.get('nova_data')
    novo_horario_inicio = request.data.get('novo_horario_inicio')
    novo_horario_fim = request.data.get('novo_horario_fim')

    if not cpf or not codigo_reserva or not nova_data or not novo_horario_inicio or not novo_horario_fim:
        return Response(
            {'erro': 'CPF, código da reserva, nova data e novos horários são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    reserva = Reserva.objects.filter(
        cliente__cpf=cpf,
        codigo_reserva=codigo_reserva
    ).first()

    if not reserva:
        return Response(
            {'erro': 'Reserva não encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    status_alteracao = StatusReserva.objects.filter(
        nome='ALTERACAO_SOLICITADA'
    ).first()

    if not status_alteracao:
        return Response(
            {'erro': 'Status ALTERACAO_SOLICITADA não encontrado.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    conflito = Reserva.objects.filter(
        data_reserva=nova_data,
        hora_inicio__lt=novo_horario_fim,
        hora_fim__gt=novo_horario_inicio
    ).exclude(id=reserva.id).exists()

    if conflito:
        return Response(
            {'erro': 'A nova data e horário solicitados já estão indisponíveis.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    reserva.nova_data_solicitada = nova_data
    reserva.novo_horario_inicio_solicitado = novo_horario_inicio
    reserva.novo_horario_fim_solicitado = novo_horario_fim
    reserva.status = status_alteracao
    reserva.save()

    return Response({
        'mensagem': 'Solicitação de alteração enviada com sucesso.',
        'codigo_reserva': reserva.codigo_reserva,
        'status': reserva.status.nome
    })