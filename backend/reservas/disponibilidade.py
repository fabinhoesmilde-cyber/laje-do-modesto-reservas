from datetime import timedelta

from configuracao_laje.models import ConfiguracaoReserva
from dias_bloqueados.models import DiaBloqueado

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
    Regra da Laje: só pode haver UMA reserva ativa por dia.

    Diz se já existe outra reserva, que não esteja cancelada, no dia em
    que a festa começa (inicio_dt). Não importa o horário: duas festas no
    mesmo dia não são permitidas.

    - Reservas CANCELADA não ocupam o dia.
    - excluir_id permite ignorar uma reserva (útil ao alterar a própria).
    - Uma festa da noite que termina de madrugada (até as 05:00) pertence
      ao dia em que começou. A festa do dia seguinte começa às 08:00 ou
      depois, então as duas nunca se encontram.
    - fim_dt não é usado hoje; continua como parâmetro para que quem
      chama a função não precise mudar.
    """
    reservas = Reserva.objects.filter(
        data_reserva=inicio_dt.date()
    ).exclude(
        status__nome="CANCELADA"
    )

    if excluir_id is not None:
        reservas = reservas.exclude(id=excluir_id)

    return reservas.exists()


def existe_dia_bloqueado(inicio_dt, fim_dt):
    """Verifica se o intervalo da reserva toca alguma data bloqueada."""
    data_atual = inicio_dt.date()
    ultima_data = (fim_dt - timedelta(microseconds=1)).date()
    while data_atual <= ultima_data:
        if DiaBloqueado.objects.filter(data=data_atual).exists():
            return True
        data_atual += timedelta(days=1)
    return False