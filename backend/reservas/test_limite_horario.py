from datetime import date, time, timedelta
from decimal import Decimal

from django.test import SimpleTestCase, TestCase

from configuracao_laje.models import ConfiguracaoReserva
from reservas.models import Reserva, StatusReserva
from reservas.regras import horas_extras_maximas


class TesteHorasExtrasMaximas(SimpleTestCase):
    def setUp(self):
        self.data = date(2026, 12, 5)

    def test_inicio_as_18h_permite_3_horas_extras(self):
        # 18:00 + 8h = 02:00; sobram 3h até as 05:00
        self.assertEqual(horas_extras_maximas(self.data, time(18, 0)), 3)

    def test_inicio_as_21h_nao_permite_extras(self):
        # 21:00 + 8h = 05:00 exatamente
        self.assertEqual(horas_extras_maximas(self.data, time(21, 0)), 0)

    def test_minutos_contam_20h30_nao_permite_extra(self):
        # 20:30 + 8h = 04:30; sobram só 30 min, não dá 1 hora inteira
        self.assertEqual(horas_extras_maximas(self.data, time(20, 30)), 0)

    def test_inicio_as_22h_e_invalido(self):
        # 22:00 + 8h = 06:00, passa das 05:00
        self.assertLess(horas_extras_maximas(self.data, time(22, 0)), 0)

    def test_inicio_21h01_e_invalido(self):
        self.assertLess(horas_extras_maximas(self.data, time(21, 1)), 0)


class TesteLimiteHorarioNaCriacao(TestCase):
    def setUp(self):
        ConfiguracaoReserva.objects.create(
            valor_base=Decimal("700.00"),
            valor_hora_extra=Decimal("60.00"),
        )
        StatusReserva.objects.create(nome="CONFIRMADA")
        self.data = date.today() + timedelta(days=30)

    def criar(self, hora_inicio, horas_extras=0, numero=1):
        return self.client.post(
            "/api/criar-reserva/",
            {
                "nome": "Cliente Teste",
                "cpf": f"1111111111{numero}",
                "telefone": "21999999999",
                "email": f"limite{numero}@example.com",
                "data": self.data.isoformat(),
                "hora_inicio": hora_inicio,
                "horas_extras": horas_extras,
                "adicionais": [],
            },
            content_type="application/json",
        )

    def test_inicio_valido_sem_extras_e_aceito(self):
        resposta = self.criar("21:00")
        self.assertEqual(resposta.status_code, 201, resposta.content)

    def test_extras_dentro_do_limite_sao_aceitas(self):
        resposta = self.criar("18:00", horas_extras=3)
        self.assertEqual(resposta.status_code, 201, resposta.content)

    def test_extra_alem_do_limite_e_recusada(self):
        resposta = self.criar("18:00", horas_extras=4)
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(Reserva.objects.count(), 0)

    def test_minutos_nao_permitem_hora_extra_indevida(self):
        resposta = self.criar("20:30", horas_extras=1)
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(Reserva.objects.count(), 0)

    def test_inicio_que_nao_comporta_8_horas_e_recusado(self):
        resposta = self.criar("22:00")
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(Reserva.objects.count(), 0)