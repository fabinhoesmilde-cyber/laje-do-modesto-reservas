from datetime import date, time, timedelta
from decimal import Decimal

from django.test import TestCase

from clientes.models import Cliente
from configuracao_laje.models import ConfiguracaoReserva
from reservas.apoio_testes import criar_login_do_cliente
from reservas.models import Reserva, StatusReserva


class TesteAlteracaoComConflito(TestCase):
    def setUp(self):
        ConfiguracaoReserva.objects.create(
            valor_base=Decimal("700.00"),
            valor_hora_extra=Decimal("60.00"),
        )
        self.confirmada = StatusReserva.objects.create(nome="CONFIRMADA")
        StatusReserva.objects.create(nome="ALTERACAO_SOLICITADA")
        self.cancelada = StatusReserva.objects.create(nome="CANCELADA")

        self.cliente = Cliente.objects.create(
            nome="Maria Teste",
            cpf="123.456.789-00",
            telefone="21999999999",
            email="maria@teste.com",
        )
        self.login = criar_login_do_cliente(self.cliente)

        self.data = date.today() + timedelta(days=10)
        self.outra_data = date.today() + timedelta(days=20)

        self.reserva = self.criar_reserva(self.data, "18:00", "02:00")

    def criar_reserva(self, data, inicio, fim, status=None, horas_extras=0):
        return Reserva.objects.create(
            cliente=self.cliente,
            status=status or self.confirmada,
            data_reserva=data,
            hora_inicio=inicio,
            hora_fim=fim,
            horas_extras=horas_extras,
            valor_base=Decimal("700.00"),
            valor_total=Decimal("700.00"),
        )

    def alterar(self, nova_data, novo_inicio, reserva=None, **extra):
        reserva = reserva or self.reserva
        dados = {
            "nova_data": str(nova_data),
            "novo_horario_inicio": novo_inicio,
        }
        dados.update(extra)
        return self.client.post(
            f"/api/cliente/minhas-reservas/{reserva.codigo_reserva}/alterar/",
            dados,
            content_type="application/json",
            **self.login,
        )

    def test_novo_horario_ocupado_e_recusado(self):
        self.criar_reserva(self.outra_data, "18:00", "02:00")

        resposta = self.alterar(self.outra_data, "21:00")

        self.assertEqual(resposta.status_code, 400)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status.nome, "CONFIRMADA")

    def test_horario_de_reserva_cancelada_esta_livre(self):
        self.criar_reserva(
            self.outra_data, "18:00", "02:00", status=self.cancelada
        )

        resposta = self.alterar(self.outra_data, "18:00")

        self.assertEqual(resposta.status_code, 200, resposta.content)

    def test_pode_se_sobrepor_ao_proprio_horario_antigo(self):
        # Mesmo dia, uma hora depois: conflita só com a própria reserva
        resposta = self.alterar(self.data, "19:00")

        self.assertEqual(resposta.status_code, 200, resposta.content)

    def test_servidor_calcula_o_fim_e_ignora_o_enviado(self):
        resposta = self.alterar(
            self.outra_data, "18:00", novo_horario_fim="23:59"
        )

        self.assertEqual(resposta.status_code, 200, resposta.content)
        self.reserva.refresh_from_db()
        self.assertEqual(
            self.reserva.novo_horario_fim_solicitado, time(2, 0)
        )

    def test_inicio_fora_dos_horarios_do_site_e_recusado(self):
        self.assertEqual(self.alterar(self.outra_data, "20:30").status_code, 400)
        self.assertEqual(self.alterar(self.outra_data, "07:00").status_code, 400)

    def test_nova_data_no_passado_e_recusada(self):
        ontem = date.today() - timedelta(days=1)

        resposta = self.alterar(ontem, "18:00")

        self.assertEqual(resposta.status_code, 400)

    def test_horas_extras_que_nao_cabem_no_novo_inicio_sao_recusadas(self):
        reserva = self.criar_reserva(
            date.today() + timedelta(days=30),
            "18:00",
            "05:00",
            horas_extras=3,
        )

        resposta = self.alterar(self.outra_data, "21:00", reserva=reserva)

        self.assertEqual(resposta.status_code, 400)

    def test_horas_extras_que_cabem_no_novo_inicio_sao_aceitas(self):
        reserva = self.criar_reserva(
            date.today() + timedelta(days=30),
            "18:00",
            "05:00",
            horas_extras=3,
        )

        resposta = self.alterar(self.outra_data, "18:00", reserva=reserva)

        self.assertEqual(resposta.status_code, 200, resposta.content)

    def test_horario_original_continua_bloqueado_durante_a_alteracao(self):
        self.alterar(self.outra_data, "18:00")

        resposta = self.client.post(
            "/api/criar-reserva/",
            {
                "nome": "Outro Cliente",
                "cpf": "44444444444",
                "telefone": "21977777777",
                "email": "outro@example.com",
                "data": self.data.isoformat(),
                "hora_inicio": "18:00",
                "horas_extras": 0,
                "adicionais": [],
            },
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 400)