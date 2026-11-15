from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

# Regras de horário da festa (decididas pelo dono do negócio):
# - a reserva padrão dá direito a 8 horas de festa;
# - a festa não pode passar das 05:00 da manhã do dia seguinte.
DURACAO_BASE_HORAS = 8
HORA_LIMITE_FIM = time(5, 0)

# A festa só pode começar em hora cheia, entre 08:00 e 21:00
# (os mesmos horários que o site oferece ao cliente).
HORA_INICIO_MINIMA = time(8, 0)
HORA_INICIO_MAXIMA = time(21, 0)


def horario_inicio_valido(hora_inicio):
    """True se o início é uma hora cheia entre 08:00 e 21:00."""
    return (
        hora_inicio.minute == 0
        and HORA_INICIO_MINIMA <= hora_inicio <= HORA_INICIO_MAXIMA
    )


def horas_extras_maximas(data, hora_inicio):
    """
    Diz quantas horas extras (inteiras) cabem sem passar das 05:00.

    Retorna um número negativo quando nem as 8 horas base cabem
    (ou seja, o horário de início é inválido).
    """
    inicio = datetime.combine(data, hora_inicio)
    limite = datetime.combine(
        data + timedelta(days=1),
        HORA_LIMITE_FIM
    )

    minutos_disponiveis = (limite - inicio).total_seconds() // 60
    minutos_extras = minutos_disponiveis - DURACAO_BASE_HORAS * 60

    # // arredonda para baixo: só contam horas extras inteiras
    return int(minutos_extras // 60)

# Regras de cancelamento (decididas pelo dono do negócio):
# - cancelamento grátis até 7 dias antes da data do evento;
# - depois disso, cobra-se 20% do valor total da reserva.
PRAZO_CANCELAMENTO_GRATIS_DIAS = 7
TAXA_CANCELAMENTO = Decimal("0.20")

CENTAVOS = Decimal("0.01")


def calcular_cancelamento(data_reserva, valor_total, hoje=None):
    """
    Calcula o que acontece se a reserva for cancelada hoje.

    Retorna um dicionário com:
    - dentro_do_prazo: True se o cancelamento é grátis;
    - taxa: valor retido pela laje;
    - reembolso: valor que volta para o cliente.
    """
    if hoje is None:
        # Data de hoje no fuso configurado em settings.TIME_ZONE
        hoje = timezone.localdate()

    valor_total = Decimal(valor_total)

    # Quantos dias faltam até o evento (pode ser 0 ou negativo).
    dias_restantes = (data_reserva - hoje).days

    dentro_do_prazo = dias_restantes >= PRAZO_CANCELAMENTO_GRATIS_DIAS

    if dentro_do_prazo:
        taxa = Decimal("0.00")
    else:
        taxa = (valor_total * TAXA_CANCELAMENTO).quantize(
            CENTAVOS, rounding=ROUND_HALF_UP
        )

    return {
        "dentro_do_prazo": dentro_do_prazo,
        "taxa": taxa,
        "reembolso": valor_total - taxa,
    }