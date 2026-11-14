from decimal import Decimal
from django.db import transaction
from django.db.models import F
from config.permissions import IsAdminUser




from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from datetime import datetime, timedelta

from django.utils import timezone

from cupons.models import Cupom
from clientes.models import Cliente
from adicionais.models import Adicional
from .models import ReservaAdicional
from configuracao_laje.models import ConfiguracaoReserva

from .models import StatusReserva, Reserva
from .serializers import StatusReservaSerializer, ReservaSerializer
from .regras import calcular_cancelamento

class StatusReservaViewSet(viewsets.ModelViewSet):
    queryset = StatusReserva.objects.all()
    serializer_class = StatusReservaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

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

    # 1. Validar os dados recebidos
    if not cpf or not codigo_reserva:
        return Response(
            {'erro': 'CPF e código da reserva são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 2. Localizar a reserva do cliente
    reserva = Reserva.objects.filter(
        cliente__cpf=cpf,
        codigo_reserva=codigo_reserva
    ).first()

    if not reserva:
        return Response(
            {'erro': 'Reserva não encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # 3. Verificar se a reserva está confirmada
    if reserva.status.nome != 'CONFIRMADA':
        return Response(
            {
                'erro': (
                    'Não é possível solicitar o cancelamento. '
                    'Somente reservas confirmadas podem ser canceladas.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # 4. Não é possível cancelar um evento que já aconteceu
    if reserva.data_reserva < timezone.localdate():
        return Response(
            {'erro': 'Não é possível cancelar uma reserva de data passada.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 5. Calcular a taxa e o reembolso segundo a regra de cancelamento
    calculo = calcular_cancelamento(
        reserva.data_reserva,
        reserva.valor_total
    )

    # Dentro do prazo grátis o cancelamento é automático.
    # Fora do prazo (com taxa), o administrador ainda precisa aprovar.
    if calculo['dentro_do_prazo']:
        nome_novo_status = 'CANCELADA'
    else:
        nome_novo_status = 'CANCELAMENTO_SOLICITADO'

    # 6. Buscar o novo status
    novo_status = StatusReserva.objects.filter(
        nome=nome_novo_status
    ).first()

    if not novo_status:
        return Response(
            {'erro': f'Status {nome_novo_status} não encontrado.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 7. Atualizar a reserva
    reserva.status = novo_status
    reserva.taxa_cancelamento = calculo['taxa']
    reserva.valor_reembolso = calculo['reembolso']

    if calculo['dentro_do_prazo']:
        reserva.cancelado_em = timezone.now()

    reserva.save()

    # 8. Retornar o resultado
    if calculo['dentro_do_prazo']:
        mensagem = 'Reserva cancelada com sucesso.'
    else:
        mensagem = (
            'Solicitação de cancelamento enviada. '
            'Como faltam menos de 7 dias para o evento, '
            'será cobrada uma taxa e o pedido aguarda aprovação.'
        )

    return Response({
        'mensagem': mensagem,
        'codigo_reserva': reserva.codigo_reserva,
        'status': reserva.status.nome,
        'taxa_cancelamento': str(calculo['taxa']),
        'valor_reembolso': str(calculo['reembolso']),
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

    # Somente reservas confirmadas podem pedir alteração
    if reserva.status.nome != 'CONFIRMADA':
        return Response(
            {
                'erro': (
                    'Não é possível solicitar a alteração. '
                    'Somente reservas confirmadas podem ser alteradas.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Converter os textos recebidos em data e hora de verdade.
    # Se o formato estiver errado, devolvemos 400 em vez de estourar 500.
    try:
        nova_data = datetime.strptime(nova_data, '%Y-%m-%d').date()
        novo_horario_inicio = datetime.strptime(
            novo_horario_inicio, '%H:%M'
        ).time()
        novo_horario_fim = datetime.strptime(
            novo_horario_fim, '%H:%M'
        ).time()
    except (ValueError, TypeError):
        return Response(
            {
                'erro': (
                    'Data ou horário inválido. '
                    'Use AAAA-MM-DD para a data e HH:MM para os horários.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
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
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
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

    # Só dá para aprovar um cancelamento que foi solicitado
    if reserva.status.nome != 'CANCELAMENTO_SOLICITADO':
        return Response(
            {'erro': 'Esta reserva não possui cancelamento solicitado.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    status_cancelada = StatusReserva.objects.filter(
        nome='CANCELADA'
    ).first()

    if not status_cancelada:
        return Response(
            {'erro': 'Status CANCELADA não encontrado.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Pedidos feitos antes desta regra existir não têm taxa gravada.
    # Nesse caso, calculamos agora.
    if reserva.taxa_cancelamento is None:
        calculo = calcular_cancelamento(
            reserva.data_reserva,
            reserva.valor_total
        )
        reserva.taxa_cancelamento = calculo['taxa']
        reserva.valor_reembolso = calculo['reembolso']

    reserva.status = status_cancelada
    reserva.cancelado_em = timezone.now()
    reserva.save()

    return Response({
        'mensagem': 'Cancelamento aprovado com sucesso.',
        'codigo_reserva': reserva.codigo_reserva,
        'status': reserva.status.nome,
        'taxa_cancelamento': str(reserva.taxa_cancelamento),
        'valor_reembolso': str(reserva.valor_reembolso),
    })

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
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

    # Só dá para rejeitar um cancelamento que foi solicitado
    if reserva.status.nome != 'CANCELAMENTO_SOLICITADO':
        return Response(
            {'erro': 'Esta reserva não possui cancelamento solicitado.'},
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

    # A reserva continua valendo: apagamos a taxa e o reembolso
    # que tinham sido calculados para o pedido rejeitado.
    reserva.taxa_cancelamento = None
    reserva.valor_reembolso = None
    reserva.cancelado_em = None

    reserva.status = status_confirmada
    reserva.save()

    return Response({
        'mensagem': 'Cancelamento rejeitado com sucesso.',
        'codigo_reserva': reserva.codigo_reserva,
        'status': reserva.status.nome
    })


@api_view(['POST'])
def validar_cupom(request):
    codigo_cupom = request.data.get("cupom_codigo")
    subtotal_recebido = request.data.get("subtotal")

    if not codigo_cupom:
        return Response(
            {"erro": "Digite o código do cupom."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        subtotal = Decimal(str(subtotal_recebido))

        if not subtotal.is_finite() or subtotal < 0:
            raise ValueError

    except (ValueError, TypeError, ArithmeticError):
        return Response(
            {"erro": "O valor da reserva é inválido."},
            status=status.HTTP_400_BAD_REQUEST
        )

    codigo_cupom = str(codigo_cupom).strip().upper()

    cupom = Cupom.objects.filter(codigo=codigo_cupom).first()

    if not cupom:
        return Response(
            {"erro": "Cupom não encontrado."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not cupom.pode_ser_utilizado():
        return Response(
            {
                "erro": (
                    "Este cupom está inativo, fora da validade "
                    "ou atingiu o limite de utilizações."
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    desconto = cupom.calcular_desconto(subtotal)

    return Response({
        "valido": True,
        "cupom_codigo": cupom.codigo,
        "tipo_desconto": cupom.tipo_desconto,
        "valor_desconto": str(desconto),
        "subtotal": str(subtotal),
        "valor_total": str(max(Decimal("0.00"), subtotal - desconto))
    })


@api_view(['POST'])
@transaction.atomic
def criar_reserva(request):
    dados = request.data

    try:
        # 1. Validar os dados básicos
        campos_obrigatorios = [
            "cpf", "nome", "telefone", "email",
            "data", "hora_inicio"
        ]

        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return Response(
                    {"erro": f"O campo {campo} é obrigatório."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 2. Buscar os preços oficiais
        configuracao = ConfiguracaoReserva.objects.filter(
            pk=1
        ).first()

        if not configuracao:
            return Response(
                {"erro": "A configuração de preços da laje não foi encontrada."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        valor_base = configuracao.valor_base
        valor_hora_extra = configuracao.valor_hora_extra

        # 3. Validar data, horário e horas extras
        data = datetime.strptime(
            dados["data"], "%Y-%m-%d"
        ).date()

        hora_inicio = datetime.strptime(
            dados["hora_inicio"], "%H:%M"
        ).time()

        horas_extras = int(dados.get("horas_extras", 0))

        if horas_extras < 0:
            return Response(
                {"erro": "A quantidade de horas extras não pode ser negativa."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reserva padrão de 8 horas, com limite até 05:00
        max_horas_extras = max(
            0, 29 - (hora_inicio.hour + 8)
        )

        if horas_extras > max_horas_extras:
            return Response(
                {"erro": "A quantidade de horas extras ultrapassa o limite permitido para esse horário."},
                status=status.HTTP_400_BAD_REQUEST
            )

        duracao = 8 + horas_extras

        inicio_dt = datetime.combine(data, hora_inicio)
        fim_dt = inicio_dt + timedelta(hours=duracao)
        hora_fim = fim_dt.time()

        # 4. Validar os adicionais
        adicionais_enviados = dados.get("adicionais", [])

        if not isinstance(adicionais_enviados, list):
            return Response(
                {"erro": "A lista de adicionais é inválida."},
                status=status.HTTP_400_BAD_REQUEST
            )

        ids_adicionais = []

        for item in adicionais_enviados:
            if not isinstance(item, dict) or not item.get("id"):
                return Response(
                    {"erro": "Um dos adicionais enviados é inválido."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ids_adicionais.append(item["id"])

        if len(ids_adicionais) != len(set(ids_adicionais)):
            return Response(
                {"erro": "Existem adicionais duplicados na solicitação."},
                status=status.HTTP_400_BAD_REQUEST
            )

        adicionais = list(
            Adicional.objects.filter(
                id__in=ids_adicionais,
                ativo=True
            )
        )

        if len(adicionais) != len(ids_adicionais):
            return Response(
                {"erro": "Um ou mais adicionais não existem ou estão inativos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        valor_adicionais = sum(
            (adicional.valor for adicional in adicionais),
            Decimal("0.00")
        )

        # 5. Calcular os valores e validar o cupom
        valor_extras = valor_hora_extra * horas_extras
        valor_desconto = Decimal("0.00")
        cupom = None

        codigo_cupom = dados.get("cupom_codigo")
        codigo_cupom = (
            str(codigo_cupom).strip().upper()
            if codigo_cupom is not None
            else ""
        )

        subtotal = valor_base + valor_extras + valor_adicionais

        if codigo_cupom:
            cupom = Cupom.objects.filter(
                codigo=codigo_cupom
            ).first()

            if not cupom:
                return Response(
                    {"erro": "Cupom não encontrado."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not cupom.pode_ser_utilizado():
                return Response(
                    {"erro": "Este cupom está inativo, fora da validade ou atingiu o limite de utilizações."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            valor_desconto = cupom.calcular_desconto(subtotal)

        valor_total = subtotal - valor_desconto

        # 6. Verificar conflitos de horário
        datas_verificacao = {
            data - timedelta(days=1),
            data,
            fim_dt.date()
        }

        reservas_existentes = Reserva.objects.filter(
            data_reserva__in=datas_verificacao
        )

        for existente in reservas_existentes:
            inicio_existente = datetime.combine(
                existente.data_reserva,
                existente.hora_inicio
            )

            fim_existente = datetime.combine(
                existente.data_reserva,
                existente.hora_fim
            )

            if fim_existente <= inicio_existente:
                fim_existente += timedelta(days=1)

            if (
                inicio_dt < fim_existente
                and fim_dt > inicio_existente
            ):
                return Response(
                    {"erro": "Já existe uma reserva neste horário."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 7. Buscar ou cadastrar o cliente
        cliente, _ = Cliente.objects.get_or_create(
            cpf=dados["cpf"],
            defaults={
                "nome": dados["nome"],
                "telefone": dados["telefone"],
                "email": dados["email"]
            }
        )

        status_confirmada = StatusReserva.objects.filter(
            nome="CONFIRMADA"
        ).first()

        if not status_confirmada:
            return Response(
                {"erro": "Status CONFIRMADA não encontrado."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 8. Criar a reserva com os valores calculados no servidor
        reserva = Reserva.objects.create(
            cliente=cliente,
            status=status_confirmada,
            cupom=cupom,
            data_reserva=data,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            valor_base=valor_base,
            valor_desconto=valor_desconto,
            valor_adicionais=valor_adicionais,
            valor_total=valor_total,
            horas_extras=horas_extras
        )

        # 9. Atualizar o contador do cupom com segurança
        if cupom:
            atualizado = Cupom.objects.filter(
                pk=cupom.pk,
                ativo=True,
                uso_atual__lt=F("uso_maximo")
            ).update(
                uso_atual=F("uso_atual") + 1
            )

            if atualizado == 0:
                # Garante o rollback da reserva e de todas
                # as alterações desta transação.
                transaction.set_rollback(True)

                return Response(
                    {"erro": "Este cupom atingiu o limite de utilizações ou foi desativado. Tente novamente."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 10. Registrar os adicionais e seus preços
        for adicional in adicionais:
            ReservaAdicional.objects.create(
                reserva=reserva,
                adicional=adicional,
                quantidade=1,
                valor_unitario_momento=adicional.valor,
                valor_total=adicional.valor
            )

        # 11. Retornar os valores calculados
        return Response({
            "sucesso": True,
            "codigo_reserva": reserva.codigo_reserva,
            "valores": {
                "valor_base": str(valor_base),
                "valor_horas_extras": str(valor_extras),
                "valor_adicionais": str(valor_adicionais),
                "valor_desconto": str(valor_desconto),
                "valor_total": str(valor_total)
            }
        }, status=status.HTTP_201_CREATED)

    except (KeyError, ValueError, TypeError):
        return Response(
            {
                "erro": (
                    "Os dados enviados são inválidos. "
                    "Confira a data, o horário e as horas extras."
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )