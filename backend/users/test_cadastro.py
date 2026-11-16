import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase

from clientes.models import Cliente
from users.models import CadastroPendente
from users.servicos import gerar_hash

CPF_VALIDO = "529.982.247-25"
OUTRO_CPF_VALIDO = "111.444.777-35"


class TesteCadastroCliente(TestCase):
    def setUp(self):
        # O limite de tentativas usa o cache; limpamos para não
        # atrapalhar um teste com as chamadas dos outros.
        cache.clear()

    def cadastrar(self, **alteracoes):
        dados = {
            "nome": "Maria Teste",
            "email": "maria@teste.com",
            "cpf": CPF_VALIDO,
            "telefone": "(21) 99999-9999",
        }
        dados.update(alteracoes)
        return self.client.post(
            "/api/cliente/cadastro/",
            dados,
            content_type="application/json",
        )

    def extrair_token(self, mensagem):
        return re.search(r"token=([\w-]+)", mensagem.body).group(1)

    def test_cadastro_valido_cria_pedido_e_envia_email(self):
        resposta = self.cadastrar()

        self.assertEqual(resposta.status_code, 201, resposta.content)
        self.assertEqual(CadastroPendente.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["maria@teste.com"])
        self.assertIn("confirmar-cadastro.html?token=", mail.outbox[0].body)

    def test_nenhuma_conta_e_criada_neste_passo(self):
        self.cadastrar()

        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(Cliente.objects.count(), 0)

    def test_token_e_guardado_apenas_como_hash(self):
        self.cadastrar()

        token = self.extrair_token(mail.outbox[0])
        pedido = CadastroPendente.objects.get()

        self.assertNotEqual(pedido.token_hash, token)
        self.assertEqual(pedido.token_hash, gerar_hash(token))

    def test_cpf_e_guardado_com_mascara(self):
        self.cadastrar(cpf="52998224725")

        self.assertEqual(CadastroPendente.objects.get().cpf, CPF_VALIDO)

    def test_email_e_guardado_em_minusculas(self):
        self.cadastrar(email="  Maria@Teste.COM ")

        self.assertEqual(
            CadastroPendente.objects.get().email, "maria@teste.com"
        )

    def test_cpf_invalido_e_recusado(self):
        resposta = self.cadastrar(cpf="111.111.111-11")

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(CadastroPendente.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_email_invalido_e_recusado(self):
        resposta = self.cadastrar(email="isso-nao-e-email")

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    def test_telefone_invalido_e_recusado(self):
        resposta = self.cadastrar(telefone="123")

        self.assertEqual(resposta.status_code, 400)

    def test_campo_ausente_e_recusado(self):
        resposta = self.cadastrar(nome="")

        self.assertEqual(resposta.status_code, 400)

    def test_email_de_conta_existente_recebe_a_mesma_resposta(self):
        nova = self.cadastrar(email="nova@teste.com")

        get_user_model().objects.create_user(
            username="maria@teste.com",
            email="maria@teste.com",
            password="uma-senha-qualquer-123",
        )
        mail.outbox.clear()
        existente = self.cadastrar(email="maria@teste.com")

        self.assertEqual(existente.status_code, 201)
        self.assertEqual(existente.json(), nova.json())
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            CadastroPendente.objects.filter(email="maria@teste.com").count(),
            0,
        )

    def test_cpf_de_cliente_com_outro_email_e_recusado(self):
        Cliente.objects.create(
            nome="Outra Pessoa",
            cpf=CPF_VALIDO,
            telefone="21988887777",
            email="outra@teste.com",
        )

        resposta = self.cadastrar()

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(CadastroPendente.objects.count(), 0)

    def test_cliente_visitante_com_mesmo_email_pode_se_cadastrar(self):
        Cliente.objects.create(
            nome="Maria Visitante",
            cpf=CPF_VALIDO,
            telefone="21988887777",
            email="maria@teste.com",
        )

        resposta = self.cadastrar()

        self.assertEqual(resposta.status_code, 201, resposta.content)

    def test_novo_pedido_substitui_o_anterior(self):
        self.cadastrar()
        primeiro = self.extrair_token(mail.outbox[0])

        self.cadastrar()
        segundo = self.extrair_token(mail.outbox[1])

        self.assertNotEqual(primeiro, segundo)
        self.assertEqual(CadastroPendente.objects.count(), 1)
        self.assertEqual(
            CadastroPendente.objects.get().token_hash, gerar_hash(segundo)
        )

    def test_limite_de_tentativas_por_hora(self):
        for numero in range(10):
            resposta = self.cadastrar(email=f"pessoa{numero}@teste.com")
            self.assertEqual(resposta.status_code, 201, resposta.content)

        resposta = self.cadastrar(email="pessoa11@teste.com")

        self.assertEqual(resposta.status_code, 429)