from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework.authtoken.models import Token

from clientes.models import Cliente

SENHA = "Laje-Segura-2026!"


class TesteAreaDoCliente(TestCase):
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

    def entrar(self, email="maria@teste.com", senha=SENHA):
        return self.client.post(
            "/api/cliente/login/",
            {"email": email, "senha": senha},
            content_type="application/json",
        )

    def cabecalho(self):
        token = self.entrar().json()["token"]
        return {"HTTP_AUTHORIZATION": f"Token {token}"}

    # ---------- login ----------

    def test_login_valido_devolve_token_e_dados(self):
        resposta = self.entrar()

        self.assertEqual(resposta.status_code, 200, resposta.content)
        corpo = resposta.json()
        self.assertTrue(corpo["token"])
        self.assertEqual(corpo["cliente"]["nome"], "Maria Teste")

    def test_login_ignora_maiusculas_e_espacos_no_email(self):
        resposta = self.entrar(email="  Maria@Teste.COM ")

        self.assertEqual(resposta.status_code, 200, resposta.content)

    def test_senha_errada_e_recusada(self):
        resposta = self.entrar(senha="senha-errada")

        self.assertEqual(resposta.status_code, 401)
        self.assertNotIn("token", resposta.json())

    def test_email_inexistente_recebe_a_mesma_resposta_da_senha_errada(self):
        errada = self.entrar(senha="senha-errada")
        inexistente = self.entrar(email="ninguem@teste.com")

        self.assertEqual(inexistente.status_code, errada.status_code)
        self.assertEqual(inexistente.json(), errada.json())

    def test_campos_ausentes_sao_recusados(self):
        resposta = self.entrar(email="", senha="")

        self.assertEqual(resposta.status_code, 400)

    def test_conta_desativada_nao_entra(self):
        self.usuario.is_active = False
        self.usuario.save()

        self.assertEqual(self.entrar().status_code, 401)

    def test_conta_da_equipe_nao_entra_pela_area_do_cliente(self):
        self.usuario.is_staff = True
        self.usuario.save()

        self.assertEqual(self.entrar().status_code, 401)

    def test_conta_sem_cadastro_de_cliente_nao_entra(self):
        self.cliente.delete()

        self.assertEqual(self.entrar().status_code, 401)

    def test_login_repetido_reaproveita_o_mesmo_token(self):
        primeiro = self.entrar().json()["token"]
        segundo = self.entrar().json()["token"]

        self.assertEqual(primeiro, segundo)

    def test_limite_de_tentativas_de_login(self):
        for _ in range(20):
            resposta = self.entrar(senha="senha-errada")
            self.assertEqual(resposta.status_code, 401)

        resposta = self.entrar(senha="senha-errada")

        self.assertEqual(resposta.status_code, 429)

    # ---------- meus dados ----------

    def test_meus_dados_exige_login(self):
        resposta = self.client.get("/api/cliente/meus-dados/")

        self.assertIn(resposta.status_code, (401, 403))

    def test_meus_dados_devolve_os_dados_com_cpf_parcial(self):
        resposta = self.client.get(
            "/api/cliente/meus-dados/", **self.cabecalho()
        )

        self.assertEqual(resposta.status_code, 200, resposta.content)
        corpo = resposta.json()
        self.assertEqual(corpo["email"], "maria@teste.com")
        self.assertEqual(corpo["telefone"], "21999999999")
        self.assertEqual(corpo["cpf"], "***.***.247-25")

    def test_alterar_nome_e_telefone(self):
        resposta = self.client.patch(
            "/api/cliente/meus-dados/",
            {"nome": "Maria Silva", "telefone": "(21) 98888-7777"},
            content_type="application/json",
            **self.cabecalho(),
        )

        self.assertEqual(resposta.status_code, 200, resposta.content)
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.nome, "Maria Silva")
        self.assertEqual(self.cliente.telefone, "(21) 98888-7777")

    def test_email_e_cpf_nao_mudam_por_aqui(self):
        self.client.patch(
            "/api/cliente/meus-dados/",
            {"email": "outro@teste.com", "cpf": "111.444.777-35"},
            content_type="application/json",
            **self.cabecalho(),
        )

        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.email, "maria@teste.com")
        self.assertEqual(self.cliente.cpf, "529.982.247-25")

    def test_telefone_invalido_e_recusado(self):
        resposta = self.client.patch(
            "/api/cliente/meus-dados/",
            {"telefone": "123"},
            content_type="application/json",
            **self.cabecalho(),
        )

        self.assertEqual(resposta.status_code, 400)
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.telefone, "21999999999")

    def test_nome_vazio_e_recusado(self):
        resposta = self.client.patch(
            "/api/cliente/meus-dados/",
            {"nome": "  "},
            content_type="application/json",
            **self.cabecalho(),
        )

        self.assertEqual(resposta.status_code, 400)

    # ---------- logout ----------

    def test_logout_invalida_o_token(self):
        cabecalho = self.cabecalho()

        saida = self.client.post("/api/cliente/logout/", **cabecalho)
        self.assertEqual(saida.status_code, 200, saida.content)
        self.assertFalse(Token.objects.filter(user=self.usuario).exists())

        depois = self.client.get("/api/cliente/meus-dados/", **cabecalho)
        self.assertIn(depois.status_code, (401, 403))

    def test_logout_sem_login_e_negado(self):
        resposta = self.client.post("/api/cliente/logout/")

        self.assertIn(resposta.status_code, (401, 403))

    # ---------- separação entre cliente e administrador ----------

    def test_token_de_cliente_nao_abre_rotas_do_administrador(self):
        resposta = self.client.post(
            "/api/aprovar-cancelamento/",
            {"codigo_reserva": "QUALQUER"},
            content_type="application/json",
            **self.cabecalho(),
        )

        self.assertIn(resposta.status_code, (401, 403))

    def test_token_de_administrador_nao_abre_a_area_do_cliente(self):
        admin = get_user_model().objects.create_user(
            username="admin_teste",
            password="senha-de-teste-123",
            is_staff=True,
        )
        token = Token.objects.create(user=admin)

        resposta = self.client.get(
            "/api/cliente/meus-dados/",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        self.assertIn(resposta.status_code, (401, 403))