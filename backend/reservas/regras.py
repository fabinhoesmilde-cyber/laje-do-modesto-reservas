from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

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