"""
Ações sobre uma reserva que já foi localizada e conferida (de quem é).
Quem chama decide como achar a reserva; aqui ficam só as regras:
cancelamento com taxa, e pedido de alteração de data e horário.
"""
from datetime import datetime, timedelta

from django.utils import timezone

from .disponibilidade import existe_conflito, travar_agenda
from .models import StatusReserva
from .regras import (
    DURACAO_BASE_HORAS,
    calcular_cancelamento,
    horario_inicio_valido,
    horas_extras_maximas,
)


class ErroDeRegra(Exception):
    """Pedido recusado por uma regra de negócio (vira resposta de erro)."""

    def __init__(self, mensagem, codigo=400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.codigo = codigo


def cancelar_reserva(reserva):
    if reserva.status.nome != 'CONFIRMADA':
        raise ErroDeRegra(
            'Não é possível solicitar o cancelamento. '
            'Somente reservas confirmadas podem ser canceladas.'
        )

    if reserva.data_reserva < timezone.localdate():
        raise ErroDeRegra(
            'Não é possível cancelar uma reserva de data passada.'
        )

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

    novo_status = StatusReserva.objects.filter(
        nome=nome_novo_status
    ).first()

    if not novo_status:
        raise ErroDeRegra(f'Status {nome_novo_status} não encontrado.', 500)

    reserva.status = novo_status
    reserva.taxa_cancelamento = calculo['taxa']
    reserva.valor_reembolso = calculo['reembolso']

    if calculo['dentro_do_prazo']:
        reserva.cancelado_em = timezone.now()

    reserva.save()

    if calculo['dentro_do_prazo']:
        mensagem = 'Reserva cancelada com sucesso.'
    else:
        mensagem = (
            'Solicitação de cancelamento enviada. '
            'Como faltam menos de 7 dias para o evento, '
            'será cobrada uma taxa e o pedido aguarda aprovação.'
        )

    return {
        'mensagem': mensagem,
        'codigo_reserva': reserva.codigo_reserva,
        'status': reserva.status.nome,
        'taxa_cancelamento': str(calculo['taxa']),
        'valor_reembolso': str(calculo['reembolso']),
    }


def pedir_alteracao(reserva, nova_data, novo_horario_inicio):
    """
    nova_data ("AAAA-MM-DD") e novo_horario_inicio ("HH:MM") chegam como
    texto. O horário de fim é sempre calculado aqui, mantendo a duração
    já contratada (8 horas + extras pagas). Deve rodar dentro de uma
    transação, com a reserva travada.
    """
    if not nova_data or not novo_horario_inicio:
        raise ErroDeRegra(
            'Nova data e novo horário de início são obrigatórios.'
        )

    if reserva.status.nome != 'CONFIRMADA':
        raise ErroDeRegra(
            'Não é possível solicitar a alteração. '
            'Somente reservas confirmadas podem ser alteradas.'
        )

    try:
        nova_data = datetime.strptime(str(nova_data), '%Y-%m-%d').date()
        novo_horario_inicio = datetime.strptime(
            str(novo_horario_inicio), '%H:%M'
        ).time()
    except ValueError:
        raise ErroDeRegra(
            'Data ou horário inválido. '
            'Use AAAA-MM-DD para a data e HH:MM para o horário.'
        )

    if reserva.data_reserva < timezone.localdate():
        raise ErroDeRegra(
            'Não é possível alterar uma reserva de data passada.'
        )

    if nova_data < timezone.localdate():
        raise ErroDeRegra('A nova data não pode ser no passado.')

    if not horario_inicio_valido(novo_horario_inicio):
        raise ErroDeRegra(
            'Horário de início inválido. '
            'Escolha uma hora cheia entre 08:00 e 21:00.'
        )

    horas_extras = reserva.horas_extras or 0

    if horas_extras > horas_extras_maximas(nova_data, novo_horario_inicio):
        raise ErroDeRegra(
            'Com esse horário de início, a festa passaria das 05:00. '
            'Escolha um início mais cedo.'
        )

    inicio_dt = datetime.combine(nova_data, novo_horario_inicio)
    fim_dt = inicio_dt + timedelta(hours=DURACAO_BASE_HORAS + horas_extras)

    status_alteracao = StatusReserva.objects.filter(
        nome='ALTERACAO_SOLICITADA'
    ).first()

    if not status_alteracao:
        raise ErroDeRegra(
            'Status ALTERACAO_SOLICITADA não encontrado.', 500
        )

    # Trava a agenda e confere se o novo horário está livre.
    # A própria reserva é ignorada (pode se sobrepor ao horário antigo).
    travar_agenda()

    if existe_conflito(inicio_dt, fim_dt, excluir_id=reserva.id):
        raise ErroDeRegra(
            'A nova data e horário solicitados já estão indisponíveis.'
        )

    reserva.nova_data_solicitada = nova_data
    reserva.novo_horario_inicio_solicitado = novo_horario_inicio
    reserva.novo_horario_fim_solicitado = fim_dt.time()
    reserva.status = status_alteracao
    reserva.save()

    return {
        'mensagem': 'Solicitação de alteração enviada com sucesso.',
        'codigo_reserva': reserva.codigo_reserva,
        'status': reserva.status.nome,
    }