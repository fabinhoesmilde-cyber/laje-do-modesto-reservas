import re
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token

from clientes.models import Cliente
from users.models import ReinicioSenha
from users.servicos import gerar_hash

SENHA = "Laje-Segura-2026!"
SENHA_NOVA = "Outra-Senha-Forte-2026!"


class TesteRecuperacaoDeSenha(TestCase):
    def setUp(self):
        cache.clear()

        self.usuario = get_user_model().objects.create_user(
            username="maria@teste.com",
            email="maria@teste.com",
            password=SENHA,
            first_name="Maria Teste",
        )
        self.cliente = Cliente.objects.create(
            nome="Maria Teste",
            cpf="529.982.247-25",
            telefone="21999999999",
            email="maria@teste.com",
            user=self.usuario,
        )

    def pedir(self, email="maria@teste.com"):
        return self.client.post(
            "/api/cliente/esqueci-senha/",
            {"email": email},
            content_type="application/json",
        )

    def redefinir(self, token, senha=SENHA_NOVA):
        return self.client.post(
            "/api/cliente/redefinir-senha/",
            {"token": token, "senha": senha},
            content_type="application/json",
        )

    def token_do_email(self):
        return re.search(r"token=([\w-]+)", mail.outbox[-1].body).group(1)

    def pedir_e_pegar_token(self):
        self.pedir()
        return self.token_do_email()

    def liberar_novo_pedido(self):
        """Simula que já passou o intervalo mínimo entre pedidos."""
        ReinicioSenha.objects.update(
            criado_em=timezone.now() - timedelta(minutes=10)
        )

    def entrar(self, senha):
        return self.client.post(
            "/api/cliente/login/",
            {"email": "maria@teste.com", "senha": senha},
            content_type="application/json",
        )

    # ---------- pedir o link ----------

    def test_conta_existente_recebe_o_link_por_email(self):
        resposta = self.pedir()

        self.assertEqual(resposta.status_code, 200, resposta.content)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["maria@teste.com"])
        self.assertIn("redefinir-senha.html?token=", mail.outbox[0].body)

    def test_token_e_guardado_apenas_como_hash(self):
        token = self.pedir_e_pegar_token()

        pedido = ReinicioSenha.objects.get()
        self.assertNotEqual(pedido.token_hash, token)
        self.assertEqual(pedido.token_hash, gerar_hash(token))

    def test_email_inexistente_recebe_a_mesma_resposta(self):
        existente = self.pedir()
        mail.outbox.clear()

        inexistente = self.pedir(email="ninguem@teste.com")

        self.assertEqual(inexistente.status_code, existente.status_code)
        self.assertEqual(inexistente.json(), existente.json())
        self.assertEqual(len(mail.outbox), 0)

    def test_maiusculas_no_email_funcionam(self):
        self.pedir(email="  Maria@Teste.COM ")

        self.assertEqual(len(mail.outbox), 1)

    def test_conta_da_equipe_nao_recebe_link(self):
        self.usuario.is_staff = True
        self.usuario.save()

        resposta = self.pedir()

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_conta_desativada_nao_recebe_link(self):
        self.usuario.is_active = False
        self.usuario.save()

        self.pedir()

        self.assertEqual(len(mail.outbox), 0)

    def test_conta_sem_cadastro_de_cliente_nao_recebe_link(self):
        self.cliente.delete()

        self.pedir()

        self.assertEqual(len(mail.outbox), 0)

    def test_email_vazio_e_recusado(self):
        resposta = self.pedir(email="")

        self.assertEqual(resposta.status_code, 400)

    def test_pedidos_seguidos_enviam_so_um_email(self):
        self.pedir()
        self.pedir()

        self.assertEqual(len(mail.outbox), 1)

    def test_novo_pedido_depois_do_intervalo_anula_o_link_antigo(self):
        primeiro = self.pedir_e_pegar_token()
        self.liberar_novo_pedido()

        self.pedir()
        segundo = self.token_do_email()

        self.assertEqual(len(mail.outbox), 2)
        self.assertNotEqual(primeiro, segundo)
        self.assertEqual(ReinicioSenha.objects.count(), 1)
        self.assertEqual(self.redefinir(primeiro).status_code, 400)
        self.assertEqual(self.redefinir(segundo).status_code, 200)

    def test_falha_no_envio_nao_muda_a_resposta_e_desfaz_o_pedido(self):
        normal = self.pedir()
        ReinicioSenha.objects.all().delete()
        cache.clear()

        with mock.patch(
            "users.senha.send_mail", side_effect=Exception("sem e-mail")
        ):
            falha = self.pedir()

        self.assertEqual(falha.status_code, 200)
        self.assertEqual(falha.json(), normal.json())
        self.assertEqual(ReinicioSenha.objects.count(), 0)

    def test_limite_de_pedidos_por_hora(self):
        for _ in range(5):
            resposta = self.pedir(email="ninguem@teste.com")
            self.assertEqual(resposta.status_code, 200)

        resposta = self.pedir(email="ninguem@teste.com")

        self.assertEqual(resposta.status_code, 429)

    # ---------- criar a nova senha ----------

    def test_redefinir_troca_a_senha(self):
        token = self.pedir_e_pegar_token()

        resposta = self.redefinir(token)

        self.assertEqual(resposta.status_code, 200, resposta.content)
        self.assertEqual(self.entrar(SENHA_NOVA).status_code, 200)
        self.assertEqual(self.entrar(SENHA).status_code, 401)

    def test_link_nao_pode_ser_usado_duas_vezes(self):
        token = self.pedir_e_pegar_token()
        self.redefinir(token)

        segunda = self.redefinir(token, senha="Terceira-Senha-2026!")

        self.assertEqual(segunda.status_code, 400)
        self.assertEqual(self.entrar(SENHA_NOVA).status_code, 200)

    def test_token_inexistente_e_recusado(self):
        resposta = self.redefinir("token-que-nao-existe")

        self.assertEqual(resposta.status_code, 400)

    def test_link_vencido_e_recusado(self):
        token = self.pedir_e_pegar_token()
        ReinicioSenha.objects.update(
            expira_em=timezone.now() - timedelta(minutes=1)
        )

        resposta = self.redefinir(token)

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(self.entrar(SENHA).status_code, 200)

    def test_senha_fraca_e_recusada_e_o_link_continua_valido(self):
        token = self.pedir_e_pegar_token()

        fraca = self.redefinir(token, senha="123")

        self.assertEqual(fraca.status_code, 400)
        self.assertIsNone(ReinicioSenha.objects.get().usado_em)
        self.assertEqual(self.entrar(SENHA).status_code, 200)

        boa = self.redefinir(token)
        self.assertEqual(boa.status_code, 200, boa.content)

    def test_campos_ausentes_sao_recusados(self):
        token = self.pedir_e_pegar_token()

        self.assertEqual(self.redefinir(token, senha="").status_code, 400)
        self.assertEqual(self.redefinir("").status_code, 400)

    def test_redefinir_encerra_os_logins_abertos(self):
        self.entrar(SENHA)
        self.assertTrue(Token.objects.filter(user=self.usuario).exists())

        token = self.pedir_e_pegar_token()
        self.redefinir(token)

        self.assertFalse(Token.objects.filter(user=self.usuario).exists())

    def test_conta_desativada_depois_do_pedido_nao_redefine(self):
        token = self.pedir_e_pegar_token()
        self.usuario.is_active = False
        self.usuario.save()

        resposta = self.redefinir(token)

        self.assertEqual(resposta.status_code, 400)

    def test_limite_de_tentativas_por_hora(self):
        for _ in range(20):
            resposta = self.redefinir("token-errado")
            self.assertEqual(resposta.status_code, 400)

        resposta = self.redefinir("token-errado")

        self.assertEqual(resposta.status_code, 429)