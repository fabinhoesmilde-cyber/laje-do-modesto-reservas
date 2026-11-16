import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from clientes.models import Cliente
from users.models import CadastroPendente

CPF_VALIDO = "529.982.247-25"
SENHA_FORTE = "Laje-Segura-2026!"


class TesteConfirmacaoCadastro(TestCase):
    def setUp(self):
        cache.clear()

    def cadastrar(self, **alteracoes):
        dados = {
            "nome": "Maria Teste",
            "email": "maria@teste.com",
            "cpf": CPF_VALIDO,
            "telefone": "(21) 99999-9999",
        }
        dados.update(alteracoes)
        resposta = self.client.post(
            "/api/cliente/cadastro/",
            dados,
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 201, resposta.content)
        return re.search(r"token=([\w-]+)", mail.outbox[-1].body).group(1)

    def confirmar(self, token, senha=SENHA_FORTE):
        return self.client.post(
            "/api/cliente/confirmar-cadastro/",
            {"token": token, "senha": senha},
            content_type="application/json",
        )

    def test_confirmacao_valida_cria_conta_e_cliente(self):
        token = self.cadastrar()

        resposta = self.confirmar(token)

        self.assertEqual(resposta.status_code, 201, resposta.content)

        usuario = get_user_model().objects.get(username="maria@teste.com")
        self.assertTrue(usuario.check_password(SENHA_FORTE))
        self.assertTrue(usuario.is_active)
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)

        cliente = Cliente.objects.get(email="maria@teste.com")
        self.assertEqual(cliente.user, usuario)
        self.assertEqual(cliente.cpf, CPF_VALIDO)

    def test_pedido_fica_marcado_como_usado(self):
        token = self.cadastrar()

        self.confirmar(token)

        self.assertIsNotNone(CadastroPendente.objects.get().usado_em)

    def test_link_nao_pode_ser_usado_duas_vezes(self):
        token = self.cadastrar()
        self.confirmar(token)

        segunda = self.confirmar(token, senha="Outra-Senha-2026!")

        self.assertEqual(segunda.status_code, 400)
        self.assertEqual(get_user_model().objects.count(), 1)

        usuario = get_user_model().objects.get()
        self.assertTrue(usuario.check_password(SENHA_FORTE))

    def test_token_inexistente_e_recusado(self):
        self.cadastrar()

        resposta = self.confirmar("token-que-nao-existe")

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_link_vencido_e_recusado(self):
        token = self.cadastrar()
        CadastroPendente.objects.update(
            expira_em=timezone.now() - timedelta(minutes=1)
        )

        resposta = self.confirmar(token)

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(Cliente.objects.count(), 0)

    def test_senha_fraca_e_recusada_e_o_link_continua_valido(self):
        token = self.cadastrar()

        fraca = self.confirmar(token, senha="123")

        self.assertEqual(fraca.status_code, 400)
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertIsNone(CadastroPendente.objects.get().usado_em)

        # O cliente pode tentar de novo com o mesmo link
        boa = self.confirmar(token)
        self.assertEqual(boa.status_code, 201, boa.content)

    def test_senha_ausente_e_recusada(self):
        token = self.cadastrar()

        resposta = self.confirmar(token, senha="")

        self.assertEqual(resposta.status_code, 400)

    def test_token_ausente_e_recusado(self):
        resposta = self.confirmar("")

        self.assertEqual(resposta.status_code, 400)

    def test_cliente_visitante_com_mesmo_email_ganha_a_conta(self):
        visitante = Cliente.objects.create(
            nome="Maria Visitante",
            cpf="123.456.789-00",
            telefone="21988887777",
            email="maria@teste.com",
        )
        token = self.cadastrar()

        resposta = self.confirmar(token)

        self.assertEqual(resposta.status_code, 201, resposta.content)

        # Continua sendo o mesmo cliente (e portanto as mesmas reservas)
        self.assertEqual(Cliente.objects.count(), 1)
        visitante.refresh_from_db()
        self.assertEqual(visitante.user.username, "maria@teste.com")

    def test_cliente_que_ja_tem_conta_e_recusado(self):
        token = self.cadastrar()
        outro_usuario = get_user_model().objects.create_user(
            username="outro-login",
            password="Qualquer-Senha-2026!",
        )
        Cliente.objects.create(
            nome="Maria Visitante",
            cpf="123.456.789-00",
            telefone="21988887777",
            email="maria@teste.com",
            user=outro_usuario,
        )

        resposta = self.confirmar(token)

        self.assertEqual(resposta.status_code, 400)
        self.assertFalse(
            get_user_model().objects.filter(
                username="maria@teste.com"
            ).exists()
        )

    def test_conta_com_o_mesmo_email_criada_no_meio_e_recusada(self):
        token = self.cadastrar()
        get_user_model().objects.create_user(
            username="maria@teste.com",
            email="maria@teste.com",
            password="Qualquer-Senha-2026!",
        )

        resposta = self.confirmar(token)

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_cpf_que_passou_a_pertencer_a_outro_cliente_e_recusado(self):
        token = self.cadastrar()
        Cliente.objects.create(
            nome="Outra Pessoa",
            cpf=CPF_VALIDO,
            telefone="21977776666",
            email="outra@teste.com",
        )

        resposta = self.confirmar(token)

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(Cliente.objects.count(), 1)

    def test_nada_e_gravado_quando_a_confirmacao_falha(self):
        token = self.cadastrar()

        self.confirmar(token, senha="123")

        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(Cliente.objects.count(), 0)

    def test_limite_de_tentativas_por_hora(self):
        for _ in range(20):
            resposta = self.confirmar("token-errado")
            self.assertEqual(resposta.status_code, 400)

        resposta = self.confirmar("token-errado")

        self.assertEqual(resposta.status_code, 429)