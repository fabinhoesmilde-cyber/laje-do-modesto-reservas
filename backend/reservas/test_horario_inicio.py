from datetime import date, time, timedelta
from decimal import Decimal

from django.test import SimpleTestCase, TestCase

from configuracao_laje.models import ConfiguracaoReserva
from reservas.models import Reserva, StatusReserva
from reservas.regras import horario_inicio_valido


class TesteHorarioInicioValido(SimpleTestCase):
    def test_primeiro_e_ultimo_horarios_sao_validos(self):
        self.assertTrue(horario_inicio_valido(time(8, 0)))
        self.assertTrue(horario_inicio_valido(time(21, 0)))

    def test_hora_cheia_no_meio_do_dia_e_valida(self):
        self.assertTrue(horario_inicio_valido(time(15, 0)))

    def test_antes_das_8h_e_invalido(self):
        self.assertFalse(horario_inicio_valido(time(7, 0)))
        self.assertFalse(horario_inicio_valido(time(3, 0)))

    def test_depois_das_21h_e_invalido(self):
        self.assertFalse(horario_inicio_valido(time(22, 0)))
        self.assertFalse(horario_inicio_valido(time(21, 1)))

    def test_meia_hora_e_invalida(self):
        self.assertFalse(horario_inicio_valido(time(20, 30)))
        self.assertFalse(horario_inicio_valido(time(8, 30)))


class TesteHorarioInicioNaCriacao(TestCase):
    def setUp(self):
        ConfiguracaoReserva.objects.create(
            valor_base=Decimal("700.00"),
            valor_hora_extra=Decimal("60.00"),
        )
        StatusReserva.objects.create(nome="CONFIRMADA")
        self.data = date.today() + timedelta(days=40)

    def criar(self, hora_inicio, numero=1):
        return self.client.post(
            "/api/criar-reserva/",
            {
                "nome": "Cliente Teste",
                "cpf": f"2222222222{numero}",
                "telefone": "21999999999",
                "email": f"inicio{numero}@example.com",
                "data": self.data.isoformat(),
                "hora_inicio": hora_inicio,
                "horas_extras": 0,
                "adicionais": [],
            },
            content_type="application/json",
        )

    def test_horario_do_site_e_aceito(self):
        resposta = self.criar("08:00")
        self.assertEqual(resposta.status_code, 201, resposta.content)

    def test_antes_das_8h_e_recusado(self):
        resposta = self.criar("03:00")
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(Reserva.objects.count(), 0)

    def test_meia_hora_e_recusada(self):
        resposta = self.criar("20:30")
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(Reserva.objects.count(), 0)