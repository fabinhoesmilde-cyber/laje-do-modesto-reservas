from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token

from clientes.models import Cliente
from reservas.models import Reserva, StatusReserva


class TesteAprovacaoCancelamento(TestCase):
    def setUp(self):
        self.confirmada = StatusReserva.objects.create(nome="CONFIRMADA")
        self.solicitado = StatusReserva.objects.create(
            nome="CANCELAMENTO_SOLICITADO"
        )
        StatusReserva.objects.create(nome="CANCELADA")

        cliente = Cliente.objects.create(
            nome="Maria Teste",
            cpf="123.456.789-00",
            telefone="21999999999",
            email="maria@teste.com",
        )

        # Reserva com cancelamento pedido fora do prazo (taxa já gravada)
        self.reserva = Reserva.objects.create(
            cliente=cliente,
            status=self.solicitado,
            data_reserva=date.today() + timedelta(days=3),
            hora_inicio="18:00",
            hora_fim="02:00",
            valor_base=Decimal("700.00"),
            valor_total=Decimal("700.00"),
            taxa_cancelamento=Decimal("140.00"),
            valor_reembolso=Decimal("560.00"),
        )

        admin = get_user_model().objects.create_user(
            username="admin_teste",
            password="senha-de-teste-123",
            is_staff=True,
        )
        self.token = Token.objects.create(user=admin)

    def enviar(self, rota, com_token=True):
        cabecalhos = {}
        if com_token:
            cabecalhos["HTTP_AUTHORIZATION"] = f"Token {self.token.key}"

        return self.client.post(
            f"/api/{rota}/",
            {"codigo_reserva": self.reserva.codigo_reserva},
            content_type="application/json",
            **cabecalhos,
        )

    def test_aprovar_cancela_e_mantem_a_taxa(self):
        resposta = self.enviar("aprovar-cancelamento")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["status"], "CANCELADA")

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status.nome, "CANCELADA")
        self.assertEqual(self.reserva.taxa_cancelamento, Decimal("140.00"))
        self.assertEqual(self.reserva.valor_reembolso, Decimal("560.00"))
        self.assertIsNotNone(self.reserva.cancelado_em)

    def test_aprovar_pedido_antigo_sem_taxa_calcula_na_hora(self):
        self.reserva.taxa_cancelamento = None
        self.reserva.valor_reembolso = None
        self.reserva.save()

        resposta = self.enviar("aprovar-cancelamento")

        self.assertEqual(resposta.status_code, 200)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.taxa_cancelamento, Decimal("140.00"))
        self.assertEqual(self.reserva.valor_reembolso, Decimal("560.00"))

    def test_aprovar_sem_pedido_de_cancelamento_retorna_400(self):
        self.reserva.status = self.confirmada
        self.reserva.save()

        resposta = self.enviar("aprovar-cancelamento")

        self.assertEqual(resposta.status_code, 400)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status.nome, "CONFIRMADA")

    def test_aprovar_sem_token_e_negado(self):
        resposta = self.enviar("aprovar-cancelamento", com_token=False)

        self.assertIn(resposta.status_code, (401, 403))
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status.nome, "CANCELAMENTO_SOLICITADO")

    def test_rejeitar_volta_para_confirmada_e_limpa_a_taxa(self):
        resposta = self.enviar("rejeitar-cancelamento")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["status"], "CONFIRMADA")

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status.nome, "CONFIRMADA")
        self.assertIsNone(self.reserva.taxa_cancelamento)
        self.assertIsNone(self.reserva.valor_reembolso)
        self.assertIsNone(self.reserva.cancelado_em)

    def test_rejeitar_sem_pedido_de_cancelamento_retorna_400(self):
        self.reserva.status = self.confirmada
        self.reserva.save()

        resposta = self.enviar("rejeitar-cancelamento")

        self.assertEqual(resposta.status_code, 400)