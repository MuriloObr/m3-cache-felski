"""Regressao dos gabaritos C2, C3 e C4.

A fatia C1 e a entrega desta etapa, mas o nucleo ja cobre associatividade,
politicas de escrita e classificacao de faltas; estes testes de ouro evitam
que essas regras regridam sem aviso.

Autores:
  - Murilo Dressel Obregão
"""

import unittest

from tests.apoio import CALIBRACAO, rodar_configuracao_bytes

SEPARADOR_DO_C3 = b"=" * 70


class TesteCalibracaoC2C4(unittest.TestCase):
    def test_reproduz_o_gabarito_c2_byte_a_byte(self):
        resultado = rodar_configuracao_bytes(
            CALIBRACAO / "C2_associativa_LRU.txt", 64, 16, 2, "WB"
        )
        esperado = (
            CALIBRACAO / "C2_associativa_LRU_esperado.txt"
        ).read_bytes()

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stdout, esperado)

    def test_reproduz_o_gabarito_c3_byte_a_byte_com_as_duas_politicas(self):
        traco = CALIBRACAO / "C3_escrita.txt"
        resultado_wb = rodar_configuracao_bytes(traco, 64, 16, 1, "WB")
        resultado_wt = rodar_configuracao_bytes(traco, 64, 16, 1, "WT")

        combinado = (
            resultado_wb.stdout
            + b"\n"
            + SEPARADOR_DO_C3
            + b"\n\n"
            + resultado_wt.stdout
        )
        esperado = (CALIBRACAO / "C3_escrita_esperado.txt").read_bytes()

        self.assertEqual(resultado_wb.returncode, 0, resultado_wb.stderr)
        self.assertEqual(resultado_wt.returncode, 0, resultado_wt.stderr)
        self.assertEqual(combinado, esperado)

    def test_reproduz_o_gabarito_c4_byte_a_byte(self):
        resultado = rodar_configuracao_bytes(
            CALIBRACAO / "C4_classificacao.txt", 64, 16, 1, "WB"
        )
        esperado = (
            CALIBRACAO / "C4_classificacao_esperado.txt"
        ).read_bytes()

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stdout, esperado)


if __name__ == "__main__":
    unittest.main()
