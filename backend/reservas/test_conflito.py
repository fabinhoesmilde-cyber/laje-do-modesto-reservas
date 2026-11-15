from datetime import date, datetime, timedelta
from decimal import Decimal

from django.test import TestCase

from clientes.models import Cliente
from configuracao_laje.models import ConfiguracaoReserva
from reservas.disponibilidade import existe_conflito
from reservas.models import Reserva, StatusReserva


class BaseConflito(TestCase):
    def setUp(self):
        ConfiguracaoReserva.objects.create(
            valor_base=Decimal("700.00"),
            valor_hora_extra=Decimal("60.00"),
        )
        self.confirmada = StatusReserva.objects.create(nome="CONFIRMADA")
        self.cancelada = StatusReserva.objects.create(nome="CANCELADA")

        self.cliente = Cliente.objects.create(
            nome="Maria Teste",
            cpf="123.456.789-00",
            telefone="21999999999",
            email="maria@teste.com",
        )
        self.data = date.today() + timedelta(days=50)

    def criar_reserva(self, data, hora_inicio, hora_fim, status=None):
        return Reserva.objects.create(
            cliente=self.cliente,
            status=status or self.confirmada,
            data_reserva=data,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            valor_base=Decimal("700.00"),
            valor_total=Decimal("700.00"),
        )

    def momento(self, data, hora, minuto=0):
        return datetime(data.year, data.month, data.day, hora, minuto)


class TesteExisteConflito(BaseConflito):
    def test_sem_reservas_nao_ha_conflito(self):
        self.assertFalse(
            existe_conflito(
                self.momento(self.data, 18),
                self.momento(self.data, 23),
            )
        )

    def test_periodos_sobrepostos_geram_conflito(self):
        self.criar_reserva(self.data, "18:00", "02:00")

        self.assertTrue(
            existe_conflito(
                self.momento(self.data, 21),
                self.momento(self.data, 23),
            )
        )

    def test_reserva_cancelada_nao_bloqueia(self):
        self.criar_reserva(
            self.data, "18:00", "02:00", status=self.cancelada
        )

        self.assertFalse(
            existe_conflito(
                self.momento(self.data, 18),
                self.momento(self.data, 23),
            )
        )

    def test_reserva_do_dia_anterior_que_vira_a_madrugada_bloqueia(self):
        dia_anterior = self.data - timedelta(days=1)
        self.criar_reserva(dia_anterior, "21:00", "05:00")

        # Das 01:00 às 03:00 do dia seguinte ainda está dentro da festa
        self.assertTrue(
            existe_conflito(
                self.momento(self.data, 1),
                self.momento(self.data, 3),
            )
        )

    def test_comecar_exatamente_quando_a_outra_termina_nao_conflita(self):
        dia_anterior = self.data - timedelta(days=1)
        self.criar_reserva(dia_anterior, "21:00", "05:00")

        self.assertFalse(
            existe_conflito(
                self.momento(self.data, 5),
                self.momento(self.data, 13),
            )
        )

    def test_excluir_id_ignora_a_propria_reserva(self):
        reserva = self.criar_reserva(self.data, "18:00", "02:00")

        self.assertFalse(
            existe_conflito(
                self.momento(self.data, 18),
                self.momento(self.data, 23),
                excluir_id=reserva.id,
            )
        )


class TesteCriarReservaConflito(BaseConflito):
    def criar(self, hora_inicio, numero=1):
        return self.client.post(
            "/api/criar-reserva/",
            {
                "nome": "Cliente Novo",
                "cpf": f"3333333333{numero}",
                "telefone": "21988888888",
                "email": f"novo{numero}@example.com",
                "data": self.data.isoformat(),
                "hora_inicio": hora_inicio,
                "horas_extras": 0,
                "adicionais": [],
            },
            content_type="application/json",
        )

    def test_horario_ocupado_e_recusado(self):
        self.criar_reserva(self.data, "18:00", "02:00")

        resposta = self.criar("21:00")

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(Reserva.objects.count(), 1)

    def test_horario_de_reserva_cancelada_pode_ser_reservado(self):
        self.criar_reserva(
            self.data, "18:00", "02:00", status=self.cancelada
        )

        resposta = self.criar("18:00")

        self.assertEqual(resposta.status_code, 201, resposta.content)

    def test_dia_seguinte_a_uma_festa_da_noite_esta_livre(self):
        # Festa de ontem 21:00 até 05:00; a de hoje começa às 08:00
        dia_anterior = self.data - timedelta(days=1)
        self.criar_reserva(dia_anterior, "21:00", "05:00")

        resposta = self.criar("08:00")

        self.assertEqual(resposta.status_code, 201, resposta.content)

    def test_sem_status_confirmada_nao_cadastra_cliente(self):
        self.confirmada.delete()
        total_antes = Cliente.objects.count()

        resposta = self.criar("18:00", numero=7)

        self.assertEqual(resposta.status_code, 500)
        self.assertEqual(Cliente.objects.count(), total_antes)