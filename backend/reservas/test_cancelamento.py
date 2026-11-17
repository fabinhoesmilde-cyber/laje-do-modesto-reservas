from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from clientes.models import Cliente
from reservas.apoio_testes import criar_login_do_cliente
from reservas.models import Reserva, StatusReserva


class TesteSolicitarCancelamento(TestCase):
    def setUp(self):
        self.confirmada = StatusReserva.objects.create(nome="CONFIRMADA")
        StatusReserva.objects.create(nome="CANCELAMENTO_SOLICITADO")
        StatusReserva.objects.create(nome="CANCELADA")

        self.cliente = Cliente.objects.create(
            nome="Maria Teste",
            cpf="123.456.789-00",
            telefone="21999999999",
            email="maria@teste.com",
        )
        self.login = criar_login_do_cliente(self.cliente)

    def criar_reserva(self, dias_ate_o_evento):
        return Reserva.objects.create(
            cliente=self.cliente,
            status=self.confirmada,
            data_reserva=date.today() + timedelta(days=dias_ate_o_evento),
            hora_inicio="18:00",
            hora_fim="02:00",
            valor_base=Decimal("700.00"),
            valor_total=Decimal("700.00"),
        )

    def cancelar(self, reserva, com_login=True):
        cabecalho = self.login if com_login else {}
        return self.client.post(
            f"/api/cliente/minhas-reservas/{reserva.codigo_reserva}/cancelar/",
            **cabecalho,
        )

    def test_dentro_do_prazo_cancela_automaticamente(self):
        reserva = self.criar_reserva(10)

        resposta = self.cancelar(reserva)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["status"], "CANCELADA")
        self.assertEqual(resposta.json()["taxa_cancelamento"], "0.00")
        self.assertEqual(resposta.json()["valor_reembolso"], "700.00")

        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "CANCELADA")
        self.assertEqual(reserva.taxa_cancelamento, Decimal("0.00"))
        self.assertEqual(reserva.valor_reembolso, Decimal("700.00"))
        self.assertIsNotNone(reserva.cancelado_em)

    def test_exatamente_7_dias_antes_ainda_cancela_automaticamente(self):
        reserva = self.criar_reserva(7)

        resposta = self.cancelar(reserva)

        self.assertEqual(resposta.json()["status"], "CANCELADA")

    def test_fora_do_prazo_cobra_taxa_e_aguarda_aprovacao(self):
        reserva = self.criar_reserva(3)

        resposta = self.cancelar(reserva)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.json()["status"], "CANCELAMENTO_SOLICITADO"
        )
        self.assertEqual(resposta.json()["taxa_cancelamento"], "140.00")
        self.assertEqual(resposta.json()["valor_reembolso"], "560.00")

        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "CANCELAMENTO_SOLICITADO")
        self.assertEqual(reserva.taxa_cancelamento, Decimal("140.00"))
        self.assertEqual(reserva.valor_reembolso, Decimal("560.00"))
        self.assertIsNone(reserva.cancelado_em)

    def test_reserva_de_data_passada_nao_pode_ser_cancelada(self):
        reserva = self.criar_reserva(-2)

        resposta = self.cancelar(reserva)

        self.assertEqual(resposta.status_code, 400)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "CONFIRMADA")

    def test_reserva_de_outro_cliente_retorna_404(self):
        outro = Cliente.objects.create(
            nome="Outra Pessoa",
            cpf="111.444.777-35",
            telefone="21988887777",
            email="outra@teste.com",
        )
        alheia = Reserva.objects.create(
            cliente=outro,
            status=self.confirmada,
            data_reserva=date.today() + timedelta(days=10),
            hora_inicio="18:00",
            hora_fim="02:00",
            valor_base=Decimal("700.00"),
            valor_total=Decimal("700.00"),
        )

        resposta = self.cancelar(alheia)

        self.assertEqual(resposta.status_code, 404)
        alheia.refresh_from_db()
        self.assertEqual(alheia.status.nome, "CONFIRMADA")

    def test_sem_login_nao_cancela(self):
        reserva = self.criar_reserva(10)

        resposta = self.cancelar(reserva, com_login=False)

        self.assertIn(resposta.status_code, (401, 403))
        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "CONFIRMADA")

    def test_rotas_publicas_antigas_foram_removidas(self):
        for rota in ("solicitar-cancelamento", "solicitar-alteracao"):
            resposta = self.client.post(
                f"/api/{rota}/",
                {"cpf": "123.456.789-00", "codigo_reserva": "LDM-QUALQUER"},
                content_type="application/json",
            )

            self.assertEqual(resposta.status_code, 404, rota)

    def test_reserva_ja_cancelada_nao_cancela_de_novo(self):
        reserva = self.criar_reserva(10)
        self.cancelar(reserva)

        resposta = self.cancelar(reserva)

        self.assertEqual(resposta.status_code, 400)