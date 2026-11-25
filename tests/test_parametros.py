"""Contrato da linha de comando: parametros impossiveis sao recusados.

Autores:
  - Murilo Dressel Obregão
"""

import unittest

from tests.apoio import TRACO_C1, rodar_configuracao, rodar_simulador


class TesteParametrosInvalidos(unittest.TestCase):
    def assert_recusa(self, resultado, trecho):
        self.assertNotEqual(resultado.returncode, 0)
        self.assertEqual(resultado.stdout, "")
        self.assertIn(trecho, resultado.stderr)

    def test_recusa_capacidade_que_nao_e_potencia_de_2(self):
        resultado = rodar_configuracao(TRACO_C1, 100, 16, 1, "WB")
        self.assert_recusa(resultado, "capacidade")

    def test_recusa_bloco_menor_que_4_bytes(self):
        resultado = rodar_configuracao(TRACO_C1, 128, 2, 1, "WB")
        self.assert_recusa(resultado, "bloco")

    def test_recusa_bloco_que_nao_e_multiplo_de_4_bytes(self):
        resultado = rodar_configuracao(TRACO_C1, 128, 6, 1, "WB")
        self.assert_recusa(resultado, "bloco")

    def test_recusa_bloco_que_nao_e_potencia_de_2(self):
        resultado = rodar_configuracao(TRACO_C1, 128, 12, 1, "WB")
        self.assert_recusa(resultado, "bloco")

    def test_recusa_vias_maiores_que_o_numero_de_blocos(self):
        resultado = rodar_configuracao(TRACO_C1, 128, 16, 16, "WB")
        self.assert_recusa(resultado, "vias")

    def test_recusa_vias_que_nao_sao_potencia_de_2(self):
        resultado = rodar_configuracao(TRACO_C1, 128, 16, 3, "WB")
        self.assert_recusa(resultado, "vias")

    def test_recusa_politica_de_escrita_desconhecida(self):
        resultado = rodar_configuracao(TRACO_C1, 128, 16, 1, "XX")
        self.assert_recusa(resultado, "escrita")

    def test_recusa_traco_inexistente(self):
        resultado = rodar_configuracao(
            "/caminho/que/nao/existe.txt", 128, 16, 1, "WB"
        )
        self.assert_recusa(resultado, "traco")

    def test_aceita_politica_em_minusculas(self):
        resultado = rodar_configuracao(TRACO_C1, 128, 16, 1, "wb")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("escrita=WB", resultado.stdout)

    def test_ajuda_nao_depende_de_configuracao(self):
        resultado = rodar_simulador("--help")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("--traco", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
