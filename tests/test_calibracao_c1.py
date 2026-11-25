"""Teste de ouro do C1: a saida do simulador deve ser identica ao gabarito.

Toda a suite atravessa a fronteira do processo: entra um arquivo de traco e
parametros na linha de comando, sai texto em stdout.

Autores:
  - Murilo Dressel Obregão
"""

import unittest

from tests.apoio import CALIBRACAO, TRACO_C1, rodar_configuracao_bytes


class TesteCalibracaoC1(unittest.TestCase):
    def test_reproduz_o_gabarito_c1_byte_a_byte(self):
        resultado = rodar_configuracao_bytes(TRACO_C1, 128, 16, 1, "WB")
        esperado = (
            CALIBRACAO / "C1_mapeamento_direto_esperado.txt"
        ).read_bytes()

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stdout, esperado)


if __name__ == "__main__":
    unittest.main()
