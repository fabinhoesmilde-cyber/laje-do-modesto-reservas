from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from datetime import datetime, timedelta

from clientes.models import Cliente
from adicionais.models import Adicional
from .models import ReservaAdicional

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

    if (
        not cpf
        or not codigo_reserva
        or not nova_data
        or not novo_horario_inicio
        or not novo_horario_fim
    ):
        return Response(
            {
                'erro': 'CPF, código da reserva, nova data e novos horários são obrigatórios.'
            },
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


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def aprovar_alteracao(request):
    codigo_reserva = request.data.get('codigo_reserva')

    if not codigo_reserva:
        return Response(
            {'erro': 'Código da reserva é obrigatório.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    reserva = Reserva.objects.filter(
        codigo_reserva=codigo_reserva
    ).first()

    if not reserva:
        return Response(
            {'erro': 'Reserva não encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not reserva.nova_data_solicitada:
        return Response(
            {'erro': 'Esta reserva não possui alteração solicitada.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    status_confirmada = StatusReserva.objects.filter(
        nome='CONFIRMADA'
    ).first()

    if not status_confirmada:
        return Response(
            {'erro': 'Status CONFIRMADA não encontrado.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    reserva.data_reserva = reserva.nova_data_solicitada
    reserva.hora_inicio = reserva.novo_horario_inicio_solicitado
    reserva.hora_fim = reserva.novo_horario_fim_solicitado

    reserva.nova_data_solicitada = None
    reserva.novo_horario_inicio_solicitado = None
    reserva.novo_horario_fim_solicitado = None

    reserva.status = status_confirmada
    reserva.save()

    return Response({
        'mensagem': 'Alteração aprovada com sucesso.',
        'codigo_reserva': reserva.codigo_reserva,
        'status': reserva.status.nome
    })

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def rejeitar_alteracao(request):
    codigo_reserva = request.data.get('codigo_reserva')

    if not codigo_reserva:
        return Response(
            {'erro': 'Código da reserva é obrigatório.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    reserva = Reserva.objects.filter(
        codigo_reserva=codigo_reserva
    ).first()

    if not reserva:
        return Response(
            {'erro': 'Reserva não encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not reserva.nova_data_solicitada:
        return Response(
            {'erro': 'Esta reserva não possui alteração solicitada.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    status_confirmada = StatusReserva.objects.filter(
        nome='CONFIRMADA'
    ).first()

    if not status_confirmada:
        return Response(
            {'erro': 'Status CONFIRMADA não encontrado.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    reserva.nova_data_solicitada = None
    reserva.novo_horario_inicio_solicitado = None
    reserva.novo_horario_fim_solicitado = None

    reserva.status = status_confirmada
    reserva.save()

    return Response({
        'mensagem': 'Alteração rejeitada com sucesso.',
        'codigo_reserva': reserva.codigo_reserva,
        'status': reserva.status.nome
    })

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def aprovar_cancelamento(request):
    codigo_reserva = request.data.get('codigo_reserva')

    if not codigo_reserva:
        return Response(
            {'erro': 'Código da reserva é obrigatório.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    reserva = Reserva.objects.filter(
        codigo_reserva=codigo_reserva
    ).first()

    if not reserva:
        return Response(
            {'erro': 'Reserva não encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    status_cancelada = StatusReserva.objects.filter(
        nome='CANCELADA'
    ).first()

    if not status_cancelada:
        return Response(
            {'erro': 'Status CANCELADA não encontrado.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    reserva.status = status_cancelada
    reserva.save()

    return Response({
        'mensagem': 'Cancelamento aprovado com sucesso.',
        'codigo_reserva': reserva.codigo_reserva,
        'status': reserva.status.nome
    })

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def rejeitar_cancelamento(request):
    codigo_reserva = request.data.get('codigo_reserva')

    if not codigo_reserva:
        return Response(
            {'erro': 'Código da reserva é obrigatório.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    reserva = Reserva.objects.filter(
        codigo_reserva=codigo_reserva
    ).first()

    if not reserva:
        return Response(
            {'erro': 'Reserva não encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    status_confirmada = StatusReserva.objects.filter(
        nome='CONFIRMADA'
    ).first()

    if not status_confirmada:
        return Response(
            {'erro': 'Status CONFIRMADA não encontrado.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    reserva.status = status_confirmada
    reserva.save()

    return Response({
        'mensagem': 'Cancelamento rejeitado com sucesso.',
        'codigo_reserva': reserva.codigo_reserva,
        'status': reserva.status.nome
    })

@api_view(['POST'])
def criar_reserva(request):

    dados = request.data

    try:

        cliente, _ = Cliente.objects.get_or_create(
            cpf=dados["cpf"],
            defaults={
                "nome": dados["nome"],
                "telefone": dados["telefone"],
                "email": dados["email"]

            }
        )

        status = StatusReserva.objects.get(
            nome="CONFIRMADA"
        )

        data = datetime.strptime(
            dados["data"],
            "%Y-%m-%d"
        ).date()

        hora_inicio = datetime.strptime(
            dados["hora_inicio"],
            "%H:%M"
        )

        duracao = int(dados["duracao"])

        horas_extras = int(
            dados.get("horas_extras", 0)
)

        hora_fim = (
            hora_inicio +
            timedelta(hours=duracao)
        ).time()



        conflito = Reserva.objects.filter(
            data_reserva=data,
            hora_inicio__lt=hora_fim,
            hora_fim__gt=hora_inicio.time()
        ).exists()

        if conflito:

            return Response(
                {
                    "erro": "Já existe uma reserva neste horário."
                },
                status=400
            )

        reserva = Reserva.objects.create(

            cliente=cliente,

            status=status,

            data_reserva=data,

            hora_inicio=hora_inicio.time(),

            hora_fim=hora_fim,

            valor_base=dados["valor_reserva"],

            valor_desconto=dados["desconto"],

            valor_adicionais=dados["valor_adicionais"],

            valor_total=dados["total"],

            horas_extras=horas_extras,

        )
        print(dados["adicionais"])


        for item in dados["adicionais"]:

            adicional = Adicional.objects.filter(
                id=item["id"],
                ativo=True
            ).first()

            if not adicional:
                return Response(
                    {
                        "erro": (
                            f"O adicional com ID {item.get('id')} "
                            "não existe ou está inativo."
                        )
                    },
                    status=400
                )


            ReservaAdicional.objects.create(

                reserva=reserva,

                adicional=adicional,

                quantidade=1,

                valor_unitario_momento=adicional.valor,

                valor_total=adicional.valor

            )

        return Response({

            "sucesso": True,

            "codigo_reserva": reserva.codigo_reserva

        })

    except Exception as erro:

        return Response(

            {

                "erro": str(erro)

            },

            status=400

        )