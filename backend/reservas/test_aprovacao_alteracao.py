from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token

from clientes.models import Cliente
from reservas.models import Reserva, StatusReserva


class TesteAprovacaoAlteracao(TestCase):
    def setUp(self):
        self.confirmada = StatusReserva.objects.create(nome="CONFIRMADA")
        self.pendente = StatusReserva.objects.create(
            nome="ALTERACAO_SOLICITADA"
        )
        self.cancelada = StatusReserva.objects.create(nome="CANCELADA")

        self.cliente = Cliente.objects.create(
            nome="Maria Teste",
            cpf="123.456.789-00",
            telefone="21999999999",
            email="maria@teste.com",
        )

        self.data = date.today() + timedelta(days=10)
        self.nova_data = date.today() + timedelta(days=20)

        # Reserva com alteração pedida: de D 18:00 para E 18:00
        self.reserva = Reserva.objects.create(
            cliente=self.cliente,
            status=self.pendente,
            data_reserva=self.data,
            hora_inicio="18:00",
            hora_fim="02:00",
            valor_base=Decimal("700.00"),
            valor_total=Decimal("700.00"),
            nova_data_solicitada=self.nova_data,
            novo_horario_inicio_solicitado="18:00",
            novo_horario_fim_solicitado="02:00",
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

    def test_aprovar_aplica_a_nova_data_e_horario(self):
        resposta = self.enviar("aprovar-alteracao")

        self.assertEqual(resposta.status_code, 200, resposta.content)

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status.nome, "CONFIRMADA")
        self.assertEqual(self.reserva.data_reserva, self.nova_data)
        self.assertEqual(self.reserva.hora_inicio, time(18, 0))
        self.assertEqual(self.reserva.hora_fim, time(2, 0))
        self.assertIsNone(self.reserva.nova_data_solicitada)
        self.assertIsNone(self.reserva.novo_horario_inicio_solicitado)
        self.assertIsNone(self.reserva.novo_horario_fim_solicitado)

    def test_aprovar_recalcula_o_fim_pela_duracao_contratada(self):
        # Pedido antigo, com fim errado enviado pelo cliente
        self.reserva.novo_horario_fim_solicitado = "23:59"
        self.reserva.save()

        self.enviar("aprovar-alteracao")

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.hora_fim, time(2, 0))

    def test_aprovar_nao_conflita_com_a_propria_reserva(self):
        self.reserva.nova_data_solicitada = self.data
        self.reserva.novo_horario_inicio_solicitado = "19:00"
        self.reserva.save()

        resposta = self.enviar("aprovar-alteracao")

        self.assertEqual(resposta.status_code, 200, resposta.content)

    def test_aprovar_recusa_se_outra_reserva_ocupou_o_horario(self):
        Reserva.objects.create(
            cliente=self.cliente,
            status=self.confirmada,
            data_reserva=self.nova_data,
            hora_inicio="18:00",
            hora_fim="02:00",
            valor_base=Decimal("700.00"),
            valor_total=Decimal("700.00"),
        )

        resposta = self.enviar("aprovar-alteracao")

        self.assertEqual(resposta.status_code, 400)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status.nome, "ALTERACAO_SOLICITADA")
        self.assertEqual(self.reserva.data_reserva, self.data)

    def test_aprovar_sem_pedido_de_alteracao_retorna_400(self):
        self.reserva.status = self.confirmada
        self.reserva.save()

        resposta = self.enviar("aprovar-alteracao")

        self.assertEqual(resposta.status_code, 400)

    def test_aprovar_sem_token_e_negado(self):
        resposta = self.enviar("aprovar-alteracao", com_token=False)

        self.assertIn(resposta.status_code, (401, 403))
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status.nome, "ALTERACAO_SOLICITADA")

    def test_rejeitar_mantem_data_original_e_limpa_o_pedido(self):
        resposta = self.enviar("rejeitar-alteracao")

        self.assertEqual(resposta.status_code, 200, resposta.content)

        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status.nome, "CONFIRMADA")
        self.assertEqual(self.reserva.data_reserva, self.data)
        self.assertIsNone(self.reserva.nova_data_solicitada)
        self.assertIsNone(self.reserva.novo_horario_inicio_solicitado)
        self.assertIsNone(self.reserva.novo_horario_fim_solicitado)

    def test_rejeitar_sem_pedido_de_alteracao_retorna_400(self):
        self.reserva.status = self.cancelada
        self.reserva.save()

        resposta = self.enviar("rejeitar-alteracao")

        self.assertEqual(resposta.status_code, 400)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status.nome, "CANCELADA")