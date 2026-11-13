
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from adicionais.models import Adicional
from clientes.models import Cliente
from configuracao_laje.models import ConfiguracaoReserva
from cupons.models import Cupom
from reservas.models import StatusReserva, Reserva, ReservaAdicional


class TesteValidacaoCupom(TestCase):
    
    def setUp(self):
        hoje = date.today()

        self.cupom = Cupom.objects.create(
            codigo="TESTE10",
            tipo_desconto="fixo",
            valor=Decimal("60.00"),
            uso_maximo=5,
            uso_atual=0,
            data_inicio=hoje - timedelta(days=1),
            data_fim=hoje + timedelta(days=10),
            validade=hoje + timedelta(days=10),
            ativo=True,
        )


    def test_validar_cupom_calcula_desconto(self):
        resposta = self.client.post(
            "/api/validar-cupom/",
            {
                "cupom_codigo": "TESTE10",
                "subtotal": "700.00",
            },
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["valor_desconto"], "60.00")
        self.assertEqual(resposta.json()["valor_total"], "640.00")


    def test_validar_cupom_nao_incrementa_utilizacao(self):
        self.client.post(
            "/api/validar-cupom/",
            {
                "cupom_codigo": "TESTE10",
                "subtotal": "700.00",
            },
            content_type="application/json",
        )

        self.cupom.refresh_from_db()
        self.assertEqual(self.cupom.uso_atual, 0)

    def test_desconto_nao_supera_subtotal(self):
        resposta = self.client.post(
            "/api/validar-cupom/",
            {
                "cupom_codigo": "TESTE10",
                "subtotal": "40.00",
            },
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.json()["valor_desconto"],
            "40.00"
        )
        self.assertEqual(
            resposta.json()["valor_total"],
            "0.00"
        )

    def test_cupom_percentual_respeita_desconto_maximo(self):
        self.cupom.tipo_desconto = "percentual"
        self.cupom.valor = Decimal("20.00")
        self.cupom.desconto_maximo = Decimal("100.00")
        self.cupom.save()

        resposta = self.client.post(
            "/api/validar-cupom/",
            {
                "cupom_codigo": "TESTE10",
                "subtotal": "700.00",
            },
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.json()["valor_desconto"],
            "100.00"
        )
        self.assertEqual(
            resposta.json()["valor_total"],
            "600.00"
        )

class TesteCriacaoReservaComCupom(TestCase):
    def setUp(self):
        ConfiguracaoReserva.objects.create(
            valor_base=Decimal("700.00"),
            valor_hora_extra=Decimal("60.00"),
        )

        self.status = StatusReserva.objects.create(
            nome="CONFIRMADA"
        )

        self.cupom = Cupom.objects.create(
            codigo="TESTE_RESERVA",
            tipo_desconto="fixo",
            valor=Decimal("60.00"),
            uso_maximo=2,
            uso_atual=0,
            data_inicio=date.today() - timedelta(days=1),
            data_fim=date.today() + timedelta(days=10),
            validade=date.today() + timedelta(days=10),
            ativo=True,
        )



    def test_falha_ao_incrementar_cupom_desfaz_reserva(self):
        from unittest.mock import patch

        from django.db.models.query import QuerySet

        data_reserva = date.today() + timedelta(days=22)
        atualizar_original = QuerySet.update

        def simular_falha_no_incremento(queryset, **kwargs):
            if "uso_atual" in kwargs:
                return 0
            return atualizar_original(queryset, **kwargs)

        with patch.object(
            QuerySet,
            "update",
            simular_falha_no_incremento,
        ):
            resposta = self.client.post(
                "/api/criar-reserva/",
                {
                    "nome": "Cliente Teste",
                    "cpf": "12345678903",
                    "telefone": "21999999999",
                    "email": "teste.rollback@example.com",
                    "data": data_reserva.isoformat(),
                    "hora_inicio": "10:00",
                    "horas_extras": 0,
                    "adicionais": [],
                    "cupom_codigo": "TESTE_RESERVA",
                },
                content_type="application/json",
            )

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(Reserva.objects.count(), 0)

        self.cupom.refresh_from_db()
        self.assertEqual(self.cupom.uso_atual, 0)


    def test_criar_reserva_com_cupom_registra_desconto_e_uso(self):
        data_reserva = date.today() + timedelta(days=20)

        resposta = self.client.post(
            "/api/criar-reserva/",
            {
                "nome": "Cliente Teste",
                "cpf": "12345678901",
                "telefone": "21999999999",
                "email": "teste.reserva@example.com",
                "data": data_reserva.isoformat(),
                "hora_inicio": "10:00",
                "horas_extras": 0,
                "adicionais": [],
                "cupom_codigo": "TESTE_RESERVA",
            },
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 201, resposta.content)

        reserva = Reserva.objects.get(
            codigo_reserva=resposta.json()["codigo_reserva"]
        )
        self.cupom.refresh_from_db()

        self.assertEqual(reserva.cupom, self.cupom)
        self.assertEqual(reserva.valor_desconto, Decimal("60.00"))
        self.assertEqual(reserva.valor_total, Decimal("640.00"))
        self.assertEqual(self.cupom.uso_atual, 1)

    def test_cupom_no_limite_nao_cria_reserva(self):
        self.cupom.uso_atual = self.cupom.uso_maximo
        self.cupom.save()

        resposta = self.client.post(
            "/api/criar-reserva/",
            {
                "nome": "Cliente Teste",
                "cpf": "12345678902",
                "telefone": "21999999999",
                "email": "teste.limite@example.com",
                "data": (date.today() + timedelta(days=21)).isoformat(),
                "hora_inicio": "10:00",
                "horas_extras": 0,
                "adicionais": [],
                "cupom_codigo": "TESTE_RESERVA",
            },
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(Reserva.objects.count(), 0)


class TesteRegrasDoModeloCupom(TestCase):
    def criar_cupom(self, **alteracoes):
        dados = {
            "codigo": "VALIDACAO_TESTE",
            "tipo_desconto": "fixo",
            "valor": Decimal("10.00"),
            "desconto_maximo": None,
            "uso_maximo": 5,
            "uso_atual": 0,
            "data_inicio": date(2026, 10, 1),
            "data_fim": date(2026, 10, 31),
            "validade": date(2026, 10, 31),
            "ativo": True,
        }
        dados.update(alteracoes)
        return Cupom(**dados)

    def test_rejeita_desconto_percentual_acima_de_100(self):
        from django.core.exceptions import ValidationError

        cupom = self.criar_cupom(
            tipo_desconto="percentual",
            valor=Decimal("150.00"),
        )

        with self.assertRaises(ValidationError) as contexto:
            cupom.clean()

        self.assertIn("valor", contexto.exception.message_dict)

    def test_rejeita_valor_de_desconto_zero(self):
        from django.core.exceptions import ValidationError

        cupom = self.criar_cupom(valor=Decimal("0.00"))

        with self.assertRaises(ValidationError) as contexto:
            cupom.clean()

        self.assertIn("valor", contexto.exception.message_dict)

    def test_rejeita_desconto_maximo_zero(self):
        from django.core.exceptions import ValidationError

        cupom = self.criar_cupom(
            desconto_maximo=Decimal("0.00"),
        )

        with self.assertRaises(ValidationError) as contexto:
            cupom.clean()

        self.assertIn("desconto_maximo", contexto.exception.message_dict)

    def test_rejeita_data_final_anterior_a_data_inicial(self):
        from django.core.exceptions import ValidationError

        cupom = self.criar_cupom(
            data_inicio=date(2026, 10, 20),
            data_fim=date(2026, 10, 10),
        )

        with self.assertRaises(ValidationError) as contexto:
            cupom.clean()

        self.assertIn("data_fim", contexto.exception.message_dict)

    def test_rejeita_limite_de_utilizacoes_zero(self):
        from django.core.exceptions import ValidationError

        cupom = self.criar_cupom(uso_maximo=0)

        with self.assertRaises(ValidationError) as contexto:
            cupom.clean()

        self.assertIn("uso_maximo", contexto.exception.message_dict)


class TesteValidacaoCupomSerializer(TestCase):
    def dados_cupom(self, **alteracoes):
        dados = {
            "codigo": "API_TESTE",
            "tipo_desconto": "percentual",
            "valor": "150.00",
            "desconto_maximo": None,
            "uso_maximo": 5,
            "uso_atual": 0,
            "data_inicio": "2026-10-01",
            "data_fim": "2026-10-31",
            "validade": "2026-10-31",
            "ativo": True,
        }
        dados.update(alteracoes)
        return dados

    def test_api_rejeita_desconto_percentual_acima_de_100(self):
        from cupons.serializers import CupomSerializer

        serializer = CupomSerializer(data=self.dados_cupom())

        self.assertFalse(serializer.is_valid())
        self.assertIn("valor", serializer.errors)

    def test_api_rejeita_valor_de_desconto_zero(self):
        from cupons.serializers import CupomSerializer

        dados = self.dados_cupom(valor="0.00")
        serializer = CupomSerializer(data=dados)

        self.assertFalse(serializer.is_valid())
        self.assertIn("valor", serializer.errors)

    def test_api_rejeita_desconto_maximo_zero(self):
        from cupons.serializers import CupomSerializer

        dados = self.dados_cupom(
            valor="20.00",
            desconto_maximo="0.00",
        )
        serializer = CupomSerializer(data=dados)

        self.assertFalse(serializer.is_valid())
        self.assertIn("desconto_maximo", serializer.errors)
