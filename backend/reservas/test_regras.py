from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase

from reservas.regras import calcular_cancelamento


class TesteCalcularCancelamento(SimpleTestCase):
    def setUp(self):
        self.hoje = date(2026, 11, 13)
        self.total = Decimal("700.00")

    def calcular(self, dias_ate_o_evento):
        data_evento = date.fromordinal(
            self.hoje.toordinal() + dias_ate_o_evento
        )
        return calcular_cancelamento(data_evento, self.total, self.hoje)

    def test_muito_antes_do_evento_nao_cobra_taxa(self):
        resultado = self.calcular(30)
        self.assertTrue(resultado["dentro_do_prazo"])
        self.assertEqual(resultado["taxa"], Decimal("0.00"))
        self.assertEqual(resultado["reembolso"], Decimal("700.00"))

    def test_exatamente_7_dias_antes_ainda_e_gratis(self):
        resultado = self.calcular(7)
        self.assertTrue(resultado["dentro_do_prazo"])
        self.assertEqual(resultado["taxa"], Decimal("0.00"))

    def test_6_dias_antes_cobra_20_por_cento(self):
        resultado = self.calcular(6)
        self.assertFalse(resultado["dentro_do_prazo"])
        self.assertEqual(resultado["taxa"], Decimal("140.00"))
        self.assertEqual(resultado["reembolso"], Decimal("560.00"))

    def test_no_dia_do_evento_cobra_taxa(self):
        resultado = self.calcular(0)
        self.assertFalse(resultado["dentro_do_prazo"])
        self.assertEqual(resultado["taxa"], Decimal("140.00"))

    def test_sem_informar_hoje_usa_a_data_local(self):
        with patch(
            "reservas.regras.timezone.localdate",
            return_value=date(2026, 11, 13),
        ):
            gratis = calcular_cancelamento(
                date(2026, 11, 20), self.total
            )
            com_taxa = calcular_cancelamento(
                date(2026, 11, 19), self.total
            )

        self.assertTrue(gratis["dentro_do_prazo"])
        self.assertFalse(com_taxa["dentro_do_prazo"])

    def test_taxa_arredonda_para_centavos(self):
        self.total = Decimal("333.33")
        resultado = self.calcular(3)
        self.assertEqual(resultado["taxa"], Decimal("66.67"))
        self.assertEqual(resultado["reembolso"], Decimal("266.66"))