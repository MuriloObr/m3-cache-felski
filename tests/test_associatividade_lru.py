"""Semantica da associatividade e da substituicao LRU (issue #3).

Autores:
  - Murilo Dressel Obregão
"""

import unittest

from parametros import Configuracao
from simulacao import simular
from tests.apoio import CALIBRACAO
from traco import Acesso, ler_traco


class TesteAssociatividadeLRU(unittest.TestCase):
    def test_c2_acerto_renova_uso_e_preserva_o_bloco_no_acesso_5(self):
        configuracao = Configuracao.criar(64, 16, 2, "WB")
        acessos = ler_traco(CALIBRACAO / "C2_associativa_LRU.txt")

        resultados, _ = simular(configuracao, acessos)

        # A, B, A, C: o acerto em A torna B a vitima. FIFO expulsaria A
        # no acesso 4 e erraria o acesso 5, que volta a ler A.
        self.assertEqual(
            [r.acertou for r in resultados[:6]],
            [False, False, True, False, True, False],
        )
        self.assertTrue(all(r.bloco_expulso is None for r in resultados[:3]))
        self.assertEqual(resultados[3].bloco_expulso, 0x10000020)
        # O preenchimento de C tambem conta como uso. A e tocado novamente
        # no acesso 5, portanto C deve sair quando B retorna no acesso 6.
        self.assertEqual(resultados[5].bloco_expulso, 0x10000040)

    def test_substituicao_fica_no_conjunto_do_indice_e_reconstroi_endereco(self):
        configuracao = Configuracao.criar(64, 16, 2, "WB")
        # Mesmo rotulo em indices diferentes deve ocupar blocos distintos.
        # O conjunto 1 recebe A, B, A, C; o conjunto 0 deve sobreviver.
        enderecos = [
            0x10000000, 0x10000010, 0x10000030,
            0x10000014, 0x10000054, 0x10000004, 0x10000018,
        ]
        acessos = [Acesso(i, "R", e) for i, e in enumerate(enderecos, 1)]

        resultados, _ = simular(configuracao, acessos)

        self.assertEqual([r.indice for r in resultados], [0, 1, 1, 1, 1, 0, 1])
        self.assertEqual(
            [r.acertou for r in resultados],
            [False, False, False, True, False, True, True],
        )
        self.assertTrue(all(r.bloco_expulso is None for r in resultados[:4]))
        # A vitima inclui o indice 1 e tem offset zero, embora C use offset 4.
        self.assertEqual(resultados[4].bloco_expulso, 0x10000030)
        self.assertFalse(resultados[4].houve_writeback)

    def test_lru_com_mais_vias_inclusive_cache_totalmente_associativa(self):
        for vias in (2, 4, 8, 16):
            with self.subTest(vias=vias):
                configuracao = Configuracao.criar(256, 16, vias, "WB")
                # O passo de um conjunto inteiro faz todos disputarem o
                # mesmo indice. Preenche as vias e renova o primeiro bloco.
                passo = configuracao.conjuntos * configuracao.bloco
                blocos = [0x10000000 + i * passo for i in range(vias + 1)]
                enderecos = blocos[:-1] + [blocos[0], blocos[-1], blocos[0]]
                acessos = [Acesso(i, "R", e) for i, e in enumerate(enderecos, 1)]

                resultados, _ = simular(configuracao, acessos)

                self.assertTrue(all(not r.acertou for r in resultados[:vias]))
                self.assertTrue(all(r.bloco_expulso is None for r in resultados[:vias]))
                self.assertTrue(resultados[vias].acertou)
                self.assertFalse(resultados[vias + 1].acertou)
                self.assertEqual(resultados[vias + 1].bloco_expulso, blocos[1])
                self.assertTrue(resultados[-1].acertou)


if __name__ == "__main__":
    unittest.main()
