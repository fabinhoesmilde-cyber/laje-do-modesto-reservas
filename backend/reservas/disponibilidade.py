from datetime import datetime, timedelta

from configuracao_laje.models import ConfiguracaoReserva

from .models import Reserva


def travar_agenda():
    """
    Trava a agenda até o fim da transação atual.

    Duas pessoas reservando ao mesmo tempo passariam juntas pela checagem
    de conflito. Com esta trava, a segunda espera a primeira terminar e só
    então confere o horário. Deve ser chamada dentro de transaction.atomic.

    No PostgreSQL e no MySQL a trava funciona de verdade. No SQLite
    (usado só em desenvolvimento) o Django simplesmente a ignora.
    """
    ConfiguracaoReserva.objects.select_for_update().filter(pk=1).first()


def existe_conflito(inicio_dt, fim_dt, excluir_id=None):
    """
    Diz se já existe uma reserva ativa que se sobrepõe ao período
    entre inicio_dt e fim_dt (datas com hora completa).

    - Reservas CANCELADA não bloqueiam o horário.
    - excluir_id permite ignorar uma reserva (útil ao alterar a própria).
    """
    # Uma reserva do dia anterior pode virar a madrugada e invadir este dia,
    # por isso olhamos também o dia anterior.
    datas = {
        inicio_dt.date() - timedelta(days=1),
        inicio_dt.date(),
        fim_dt.date(),
    }

    reservas = Reserva.objects.filter(
        data_reserva__in=datas
    ).exclude(
        status__nome="CANCELADA"
    )

    if excluir_id is not None:
        reservas = reservas.exclude(id=excluir_id)

    for existente in reservas:
        inicio_existente = datetime.combine(
            existente.data_reserva,
            existente.hora_inicio
        )
        fim_existente = datetime.combine(
            existente.data_reserva,
            existente.hora_fim
        )

        # Reserva que termina "antes" de começar atravessou a meia-noite
        if fim_existente <= inicio_existente:
            fim_existente += timedelta(days=1)

        # Dois períodos se sobrepõem quando um começa antes
        # de o outro terminar, e vice-versa.
        if inicio_dt < fim_existente and fim_dt > inicio_existente:
            return True

    return False