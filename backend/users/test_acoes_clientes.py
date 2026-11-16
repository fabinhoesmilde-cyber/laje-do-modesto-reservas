from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from clientes.models import Cliente
from reservas.models import Reserva, StatusReserva

SENHA = "Laje-Segura-2026!"


class BaseAcoes(TestCase):
    def setUp(self):
        cache.clear()

        self.confirmada = StatusReserva.objects.create(nome="CONFIRMADA")
        self.cancelada = StatusReserva.objects.create(nome="CANCELADA")
        self.cancelamento_pendente = StatusReserva.objects.create(
            nome="CANCELAMENTO_SOLICITADO"
        )
        self.alteracao_pendente = StatusReserva.objects.create(
            nome="ALTERACAO_SOLICITADA"
        )

        usuario = get_user_model().objects.create_user(
            username="maria@teste.com",
            email="maria@teste.com",
            password=SENHA,
        )
        self.cliente = Cliente.objects.create(
            nome="Maria Teste",
            cpf="529.982.247-25",
            telefone="21999999999",
            email="maria@teste.com",
            user=usuario,
        )
        self.outro = Cliente.objects.create(
            nome="Outra Pessoa",
            cpf="111.444.777-35",
            telefone="21988887777",
            email="outra@teste.com",
        )

        self.hoje = timezone.localdate()

    def criar(self, cliente=None, dias=30, status=None, inicio="18:00",
              fim="02:00", **extras):
        return Reserva.objects.create(
            cliente=cliente or self.cliente,
            status=status or self.confirmada,
            data_reserva=self.hoje + timedelta(days=dias),
            hora_inicio=inicio,
            hora_fim=fim,
            valor_base=Decimal("700.00"),
            valor_total=Decimal("700.00"),
            **extras,
        )

    def cabecalho(self):
        token = self.client.post(
            "/api/cliente/login/",
            {"email": "maria@teste.com", "senha": SENHA},
            content_type="application/json",
        ).json()["token"]
        return {"HTTP_AUTHORIZATION": f"Token {token}"}


class TesteCancelarPelaConta(BaseAcoes):
    def cancelar(self, reserva, com_login=True):
        cabecalho = self.cabecalho() if com_login else {}
        return self.client.post(
            f"/api/cliente/minhas-reservas/{reserva.codigo_reserva}/cancelar/",
            **cabecalho,
        )

    def test_exige_login(self):
        reserva = self.criar()

        resposta = self.cancelar(reserva, com_login=False)

        self.assertIn(resposta.status_code, (401, 403))
        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "CONFIRMADA")

    def test_dentro_do_prazo_cancela_na_hora_sem_taxa(self):
        reserva = self.criar(dias=30)

        resposta = self.cancelar(reserva)

        self.assertEqual(resposta.status_code, 200, resposta.content)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "CANCELADA")
        self.assertEqual(reserva.taxa_cancelamento, Decimal("0"))
        self.assertEqual(reserva.valor_reembolso, Decimal("700.00"))
        self.assertIsNotNone(reserva.cancelado_em)

    def test_fora_do_prazo_fica_aguardando_aprovacao_com_taxa(self):
        reserva = self.criar(dias=3)

        resposta = self.cancelar(reserva)

        self.assertEqual(resposta.status_code, 200, resposta.content)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "CANCELAMENTO_SOLICITADO")
        self.assertEqual(reserva.taxa_cancelamento, Decimal("140.00"))
        self.assertEqual(reserva.valor_reembolso, Decimal("560.00"))
        self.assertIsNone(reserva.cancelado_em)

    def test_reserva_de_outra_pessoa_da_404_e_nao_e_alterada(self):
        alheia = self.criar(cliente=self.outro)

        resposta = self.cancelar(alheia)

        self.assertEqual(resposta.status_code, 404)
        alheia.refresh_from_db()
        self.assertEqual(alheia.status.nome, "CONFIRMADA")

    def test_codigo_inexistente_da_404(self):
        resposta = self.client.post(
            "/api/cliente/minhas-reservas/LDM-NAOEXISTE/cancelar/",
            **self.cabecalho(),
        )

        self.assertEqual(resposta.status_code, 404)

    def test_nao_cancela_duas_vezes(self):
        reserva = self.criar(dias=30)
        self.cancelar(reserva)

        segunda = self.cancelar(reserva)

        self.assertEqual(segunda.status_code, 400)

    def test_reserva_de_data_passada_nao_cancela(self):
        reserva = self.criar(dias=-2)

        resposta = self.cancelar(reserva)

        self.assertEqual(resposta.status_code, 400)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "CONFIRMADA")

    def test_status_ausente_no_sistema_da_erro_500_sem_alterar(self):
        reserva = self.criar(dias=30)
        self.cancelada.delete()

        resposta = self.cancelar(reserva)

        self.assertEqual(resposta.status_code, 500)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "CONFIRMADA")


class TesteAlterarPelaConta(BaseAcoes):
    def alterar(self, reserva, dados, com_login=True):
        cabecalho = self.cabecalho() if com_login else {}
        return self.client.post(
            f"/api/cliente/minhas-reservas/{reserva.codigo_reserva}/alterar/",
            dados,
            content_type="application/json",
            **cabecalho,
        )

    def nova_data(self, dias=45):
        return (self.hoje + timedelta(days=dias)).isoformat()

    def test_exige_login(self):
        reserva = self.criar()

        resposta = self.alterar(
            reserva,
            {"nova_data": self.nova_data(), "novo_horario_inicio": "18:00"},
            com_login=False,
        )

        self.assertIn(resposta.status_code, (401, 403))

    def test_pedido_valido_fica_aguardando_aprovacao(self):
        reserva = self.criar()

        resposta = self.alterar(
            reserva,
            {"nova_data": self.nova_data(), "novo_horario_inicio": "18:00"},
        )

        self.assertEqual(resposta.status_code, 200, resposta.content)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "ALTERACAO_SOLICITADA")
        self.assertEqual(
            reserva.nova_data_solicitada.isoformat(), self.nova_data()
        )
        # A data e o horário atuais só mudam quando o administrador aprovar
        self.assertEqual(
            reserva.data_reserva, self.hoje + timedelta(days=30)
        )

    def test_fim_e_calculado_pelo_servidor_ignorando_o_enviado(self):
        reserva = self.criar()

        self.alterar(
            reserva,
            {
                "nova_data": self.nova_data(),
                "novo_horario_inicio": "18:00",
                "novo_horario_fim": "23:59",
            },
        )

        reserva.refresh_from_db()
        self.assertEqual(reserva.novo_horario_fim_solicitado.hour, 2)
        self.assertEqual(reserva.novo_horario_fim_solicitado.minute, 0)

    def test_reserva_de_outra_pessoa_da_404(self):
        alheia = self.criar(cliente=self.outro)

        resposta = self.alterar(
            alheia,
            {"nova_data": self.nova_data(), "novo_horario_inicio": "18:00"},
        )

        self.assertEqual(resposta.status_code, 404)
        alheia.refresh_from_db()
        self.assertEqual(alheia.status.nome, "CONFIRMADA")

    def test_reserva_nao_confirmada_nao_altera(self):
        reserva = self.criar(status=self.cancelada)

        resposta = self.alterar(
            reserva,
            {"nova_data": self.nova_data(), "novo_horario_inicio": "18:00"},
        )

        self.assertEqual(resposta.status_code, 400)

    def test_campos_ausentes_sao_recusados(self):
        reserva = self.criar()

        resposta = self.alterar(reserva, {"nova_data": self.nova_data()})

        self.assertEqual(resposta.status_code, 400)

    def test_formato_invalido_da_400(self):
        reserva = self.criar()

        resposta = self.alterar(
            reserva,
            {"nova_data": "amanha", "novo_horario_inicio": "18:00"},
        )

        self.assertEqual(resposta.status_code, 400)

    def test_nova_data_no_passado_e_recusada(self):
        reserva = self.criar()

        resposta = self.alterar(
            reserva,
            {"nova_data": self.nova_data(-1), "novo_horario_inicio": "18:00"},
        )

        self.assertEqual(resposta.status_code, 400)

    def test_horario_fora_da_hora_cheia_e_recusado(self):
        reserva = self.criar()

        resposta = self.alterar(
            reserva,
            {"nova_data": self.nova_data(), "novo_horario_inicio": "18:30"},
        )

        self.assertEqual(resposta.status_code, 400)

    def test_extras_que_passam_das_5_da_manha_sao_recusadas(self):
        reserva = self.criar(horas_extras=1, fim="03:00")

        resposta = self.alterar(
            reserva,
            {"nova_data": self.nova_data(), "novo_horario_inicio": "21:00"},
        )

        self.assertEqual(resposta.status_code, 400)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "CONFIRMADA")

    def test_horario_ocupado_por_outra_reserva_e_recusado(self):
        self.criar(cliente=self.outro, dias=45)
        reserva = self.criar(dias=30)

        resposta = self.alterar(
            reserva,
            {"nova_data": self.nova_data(45), "novo_horario_inicio": "18:00"},
        )

        self.assertEqual(resposta.status_code, 400)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status.nome, "CONFIRMADA")

    def test_pode_mudar_para_o_mesmo_dia_sem_conflitar_com_ela_mesma(self):
        reserva = self.criar(dias=30)

        resposta = self.alterar(
            reserva,
            {"nova_data": self.nova_data(30), "novo_horario_inicio": "19:00"},
        )

        self.assertEqual(resposta.status_code, 200, resposta.content)

    def test_reserva_de_data_passada_nao_altera(self):
        reserva = self.criar(dias=-2)

        resposta = self.alterar(
            reserva,
            {"nova_data": self.nova_data(), "novo_horario_inicio": "18:00"},
        )

        self.assertEqual(resposta.status_code, 400)