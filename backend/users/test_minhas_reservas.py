from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from adicionais.models import Adicional
from clientes.models import Cliente
from reservas.models import Reserva, ReservaAdicional, StatusReserva

SENHA = "Laje-Segura-2026!"


class TesteMinhasReservas(TestCase):
    def setUp(self):
        cache.clear()

        self.confirmada = StatusReserva.objects.create(nome="CONFIRMADA")
        self.cancelada = StatusReserva.objects.create(nome="CANCELADA")
        self.pendente = StatusReserva.objects.create(
            nome="ALTERACAO_SOLICITADA"
        )

        self.usuario = get_user_model().objects.create_user(
            username="maria@teste.com",
            email="maria@teste.com",
            password=SENHA,
        )
        self.cliente = Cliente.objects.create(
            nome="Maria Teste",
            cpf="529.982.247-25",
            telefone="21999999999",
            email="maria@teste.com",
            user=self.usuario,
        )
        self.outro = Cliente.objects.create(
            nome="Outra Pessoa",
            cpf="111.444.777-35",
            telefone="21988887777",
            email="outra@teste.com",
        )

        self.hoje = timezone.localdate()

    def criar(self, cliente=None, dias=30, status=None, **extras):
        return Reserva.objects.create(
            cliente=cliente or self.cliente,
            status=status or self.confirmada,
            data_reserva=self.hoje + timedelta(days=dias),
            hora_inicio="18:00",
            hora_fim="02:00",
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

    def listar(self):
        return self.client.get(
            "/api/cliente/minhas-reservas/", **self.cabecalho()
        )

    def test_exige_login(self):
        resposta = self.client.get("/api/cliente/minhas-reservas/")

        self.assertIn(resposta.status_code, (401, 403))

    def test_lista_so_as_reservas_do_proprio_cliente(self):
        minha = self.criar()
        self.criar(cliente=self.outro, dias=40)

        resposta = self.listar()

        self.assertEqual(resposta.status_code, 200, resposta.content)
        codigos = [r["codigo_reserva"] for r in resposta.json()]
        self.assertEqual(codigos, [minha.codigo_reserva])

    def test_lista_vazia_para_quem_nao_reservou(self):
        resposta = self.listar()

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), [])

    def test_mais_recentes_primeiro(self):
        perto = self.criar(dias=10)
        longe = self.criar(dias=50)

        codigos = [r["codigo_reserva"] for r in self.listar().json()]

        self.assertEqual(
            codigos, [longe.codigo_reserva, perto.codigo_reserva]
        )

    def test_reserva_feita_como_visitante_aparece_depois_da_conta(self):
        # A reserva já existia no cliente; a conta foi ligada depois
        visitante = Cliente.objects.create(
            nome="Joao Visitante",
            cpf="390.533.447-05",
            telefone="21977776666",
            email="joao@teste.com",
        )
        reserva = self.criar(cliente=visitante)

        usuario = get_user_model().objects.create_user(
            username="joao@teste.com", email="joao@teste.com", password=SENHA
        )
        visitante.user = usuario
        visitante.save()

        token = self.client.post(
            "/api/cliente/login/",
            {"email": "joao@teste.com", "senha": SENHA},
            content_type="application/json",
        ).json()["token"]
        resposta = self.client.get(
            "/api/cliente/minhas-reservas/",
            HTTP_AUTHORIZATION=f"Token {token}",
        )

        self.assertEqual(
            [r["codigo_reserva"] for r in resposta.json()],
            [reserva.codigo_reserva],
        )

    def test_reserva_confirmada_futura_pode_cancelar_e_alterar(self):
        self.criar(dias=30)

        reserva = self.listar().json()[0]

        self.assertTrue(reserva["pode_cancelar"])
        self.assertTrue(reserva["pode_alterar"])

    def test_previa_sem_taxa_dentro_do_prazo(self):
        self.criar(dias=30)

        previa = self.listar().json()[0]["previa_cancelamento"]

        self.assertTrue(previa["dentro_do_prazo"])
        self.assertEqual(Decimal(previa["taxa"]), Decimal("0"))
        self.assertEqual(Decimal(previa["reembolso"]), Decimal("700.00"))

    def test_previa_com_taxa_de_20_por_cento_fora_do_prazo(self):
        self.criar(dias=3)

        previa = self.listar().json()[0]["previa_cancelamento"]

        self.assertFalse(previa["dentro_do_prazo"])
        self.assertEqual(Decimal(previa["taxa"]), Decimal("140.00"))
        self.assertEqual(Decimal(previa["reembolso"]), Decimal("560.00"))

    def test_reserva_que_ja_passou_nao_pode_mexer(self):
        self.criar(dias=-5)

        reserva = self.listar().json()[0]

        self.assertFalse(reserva["pode_cancelar"])
        self.assertFalse(reserva["pode_alterar"])
        self.assertNotIn("previa_cancelamento", reserva)

    def test_reserva_cancelada_mostra_taxa_e_reembolso(self):
        self.criar(
            dias=2,
            status=self.cancelada,
            taxa_cancelamento=Decimal("140.00"),
            valor_reembolso=Decimal("560.00"),
        )

        reserva = self.listar().json()[0]

        self.assertFalse(reserva["pode_cancelar"])
        self.assertEqual(Decimal(reserva["taxa_cancelamento"]), Decimal("140"))
        self.assertEqual(Decimal(reserva["valor_reembolso"]), Decimal("560"))

    def test_alteracao_pendente_mostra_o_pedido(self):
        nova = self.hoje + timedelta(days=60)
        self.criar(
            status=self.pendente,
            nova_data_solicitada=nova,
            novo_horario_inicio_solicitado="19:00",
        )

        reserva = self.listar().json()[0]

        self.assertFalse(reserva["pode_alterar"])
        self.assertEqual(
            reserva["alteracao_solicitada"]["nova_data"], nova.isoformat()
        )
        self.assertEqual(
            reserva["alteracao_solicitada"]["novo_horario_inicio"], "19:00"
        )

    def test_resposta_nao_traz_dados_internos(self):
        self.criar(observacao="anotacao interna")

        reserva = self.listar().json()[0]

        self.assertNotIn("observacao", reserva)
        self.assertNotIn("cliente", reserva)
        self.assertNotIn("cpf", reserva)

    # ---------- detalhe ----------

    def test_detalhe_da_propria_reserva(self):
        reserva = self.criar(horas_extras=1)
        adicional = Adicional.objects.create(nome="Churrasqueira", valor=50)
        ReservaAdicional.objects.create(
            reserva=reserva,
            adicional=adicional,
            quantidade=1,
            valor_unitario_momento=Decimal("50.00"),
            valor_total=Decimal("50.00"),
        )

        resposta = self.client.get(
            f"/api/cliente/minhas-reservas/{reserva.codigo_reserva}/",
            **self.cabecalho(),
        )

        self.assertEqual(resposta.status_code, 200, resposta.content)
        corpo = resposta.json()
        self.assertEqual(corpo["codigo_reserva"], reserva.codigo_reserva)
        self.assertEqual(corpo["horas_extras"], 1)
        self.assertEqual(corpo["adicionais"][0]["nome"], "Churrasqueira")

    def test_detalhe_de_reserva_de_outra_pessoa_da_404(self):
        alheia = self.criar(cliente=self.outro)

        resposta = self.client.get(
            f"/api/cliente/minhas-reservas/{alheia.codigo_reserva}/",
            **self.cabecalho(),
        )
        inexistente = self.client.get(
            "/api/cliente/minhas-reservas/LDM-NAOEXISTE/",
            **self.cabecalho(),
        )

        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(resposta.json(), inexistente.json())

    def test_detalhe_exige_login(self):
        reserva = self.criar()

        resposta = self.client.get(
            f"/api/cliente/minhas-reservas/{reserva.codigo_reserva}/"
        )

        self.assertIn(resposta.status_code, (401, 403))