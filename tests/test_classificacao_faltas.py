"""Semantica dos tres tipos de falta e do LRU auxiliar (issue #5).

Autores:
  - Murilo Dressel Obregão
"""

import unittest

from parametros import Configuracao
from simulacao import simular
from tests.apoio import CALIBRACAO
from traco import Acesso, ler_traco


def simular_enderecos(configuracao, enderecos):
    acessos = [Acesso(i, "R", e) for i, e in enumerate(enderecos, 1)]
    return simular(configuracao, acessos)


class TesteClassificacaoFaltas(unittest.TestCase):
    def test_c4_inclui_capacidade_nos_acessos_8_e_9_e_fecha_contadores(self):
        configuracao = Configuracao.criar(64, 16, 1, "WB")
        acessos = ler_traco(CALIBRACAO / "C4_classificacao.txt")

        resultados, resumo = simular(configuracao, acessos)

        self.assertEqual(
            [r.tipo_falta for r in resultados],
            [
                "compulsoria", "compulsoria", "conflito", "compulsoria",
                "compulsoria", "compulsoria", "compulsoria", "capacidade",
                "capacidade", None,
            ],
        )
        self.assertEqual((resumo.compulsorias, resumo.conflitos, resumo.capacidades), (6, 1, 2))
        self.assertEqual(resumo.faltas, 9)
        self.assertEqual(resumo.acertos, 1)
        self.assertEqual(
            resumo.compulsorias + resumo.conflitos + resumo.capacidades,
            resumo.faltas,
        )
        self.assertEqual(resumo.acertos + resumo.faltas, resumo.acessos)

    def test_acerto_na_cache_configurada_renova_lru_da_auxiliar(self):
        configuracao = Configuracao.criar(32, 16, 1, "WB")
        # A e B ocupam indices diferentes. O acerto em A deve torna-lo MRU
        # na auxiliar. C expulsa A da cache direta, mas B da auxiliar.
        resultados, _ = simular_enderecos(
            configuracao, [0x10000000, 0x10000010, 0x10000004, 0x10000020, 0x10000008]
        )

        self.assertTrue(resultados[2].acertou)
        self.assertIsNone(resultados[2].tipo_falta)
        self.assertEqual(resultados[3].bloco_expulso, 0x10000000)
        self.assertFalse(resultados[4].acertou)
        # Ignorar o acerto na auxiliar faria A sair e daria capacidade.
        self.assertEqual(resultados[4].tipo_falta, "conflito")

    def test_acerto_auxiliar_em_falta_da_configurada_tambem_renova_lru(self):
        configuracao = Configuracao.criar(64, 16, 1, "WB")
        # A, B, C, D disputam o indice 0, mas cabem juntos na auxiliar.
        # Voltar a A deve protege-lo quando E entra; FIFO expulsaria A.
        resultados, _ = simular_enderecos(
            configuracao,
            [
                0x10000000, 0x10000040, 0x10000080, 0x100000C0,
                0x10000004, 0x10000100, 0x10000008,
            ],
        )

        self.assertTrue(all(not r.acertou for r in resultados))
        self.assertEqual(resultados[4].tipo_falta, "conflito")
        self.assertEqual(resultados[5].tipo_falta, "compulsoria")
        self.assertEqual(resultados[6].tipo_falta, "conflito")

    def test_compulsoria_e_por_bloco_e_historico_sobrevive_a_expulsao(self):
        for bloco in (4, 16, 32):
            for vias in (1, 2):
                with self.subTest(bloco=bloco, vias=vias):
                    configuracao = Configuracao.criar(64, bloco, vias, "WB")
                    quantidade = 64 // bloco
                    # Um bloco a mais que a capacidade real e auxiliar.
                    enderecos = [0x10000000 + i * bloco for i in range(quantidade + 1)]
                    # Outra palavra do ultimo bloco acerta; retornar ao
                    # primeiro bloco expulso e capacidade, nao compulsoria.
                    enderecos += [enderecos[-1] + bloco - 4, 0x10000000 + bloco - 4]

                    resultados, resumo = simular_enderecos(configuracao, enderecos)

                    self.assertTrue(all(r.tipo_falta == "compulsoria" for r in resultados[:-2]))
                    self.assertTrue(resultados[-2].acertou)
                    self.assertIsNone(resultados[-2].tipo_falta)
                    self.assertEqual(resultados[-1].tipo_falta, "capacidade")
                    self.assertEqual(resumo.compulsorias, quantidade + 1)
                    self.assertEqual((resumo.conflitos, resumo.capacidades), (0, 1))


if __name__ == "__main__":
    unittest.main()
