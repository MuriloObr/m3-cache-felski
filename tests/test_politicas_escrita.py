"""Semantica de write-allocate, WB e WT (issue #4).

Autores:
  - Murilo Dressel Obregão
"""

import unittest

from cache import Cache
from parametros import Configuracao
from simulacao import simular
from tests.apoio import CALIBRACAO
from traco import ler_traco


def acessar(cache, operacao, endereco):
    rotulo, indice, _ = cache.configuracao.decompor(endereco)
    return cache.acessar(rotulo, indice, operacao)


class TestePoliticasEscrita(unittest.TestCase):
    def test_escrita_com_falta_aloca_bloco_inteiro_em_ambas_as_politicas(self):
        for politica in ("WB", "WT"):
            for bloco in (4, 16, 32):
                with self.subTest(politica=politica, bloco=bloco):
                    cache = Cache(Configuracao.criar(128, bloco, 2, politica))

                    primeira = acessar(cache, "W", 0x10000000)
                    leitura = acessar(cache, "R", 0x10000000 + bloco - 4)
                    segunda = acessar(cache, "W", 0x10000000)

                    self.assertFalse(primeira.acertou)
                    self.assertIsNone(primeira.bloco_expulso)
                    self.assertTrue(leitura.acertou)
                    self.assertTrue(segunda.acertou)
                    self.assertEqual((cache.blocos_lidos, cache.bytes_lidos), (1, bloco))
                    # Escritas repetidas se acumulam no bit D em WB; em WT
                    # cada uma envia uma palavra, independente do bloco.
                    esperadas = 2 if politica == "WT" else 0
                    self.assertEqual(cache.escritas, esperadas)
                    self.assertEqual(cache.bytes_escritos, esperadas * 4)
                    self.assertEqual(cache.conjuntos[0][0].modificada, politica == "WB")

    def test_wb_escrita_em_acerto_suja_e_expulsao_separa_descarga_final(self):
        cache = Cache(Configuracao.criar(64, 16, 1, "WB"))
        acessar(cache, "R", 0x10000000)
        self.assertFalse(cache.conjuntos[0][0].modificada)
        self.assertTrue(acessar(cache, "W", 0x10000004).acertou)
        self.assertTrue(cache.conjuntos[0][0].modificada)

        expulsao = acessar(cache, "R", 0x10000040)
        self.assertEqual(expulsao.bloco_expulso, 0x10000000)
        self.assertTrue(expulsao.houve_writeback)
        self.assertEqual((cache.writebacks, cache.descarga_final), (1, 0))
        self.assertEqual((cache.escritas, cache.bytes_escritos), (1, 16))
        self.assertFalse(cache.conjuntos[0][0].modificada)

        # O bloco trazido por leitura nao herda o D da vitima anterior.
        limpa = acessar(cache, "R", 0x10000080)
        self.assertEqual(limpa.bloco_expulso, 0x10000040)
        self.assertFalse(limpa.houve_writeback)
        acessar(cache, "W", 0x10000084)
        cache.descarregar()
        self.assertEqual((cache.writebacks, cache.descarga_final), (1, 1))
        self.assertEqual((cache.escritas, cache.bytes_escritos), (2, 32))
        self.assertFalse(cache.conjuntos[0][0].modificada)

    def test_descarga_final_inclui_vias_e_conjuntos_e_nao_repete_escritas(self):
        cache = Cache(Configuracao.criar(128, 16, 2, "WB"))
        # Dois blocos modificados nos conjuntos 0 e 1, um limpo no 2,
        # e vias invalidas restantes: so os quatro modificados sao gravados.
        for endereco in (0x10000050, 0x10000010, 0x10000040, 0x10000000):
            acessar(cache, "W", endereco)
        acessar(cache, "R", 0x10000020)

        cache.descarregar()
        self.assertEqual((cache.writebacks, cache.descarga_final), (0, 4))
        self.assertEqual((cache.escritas, cache.bytes_escritos), (4, 64))
        self.assertTrue(all(not v.modificada for c in cache.conjuntos for v in c))
        self.assertTrue(acessar(cache, "R", 0x10000050).acertou)

        cache.descarregar()
        self.assertEqual((cache.escritas, cache.bytes_escritos), (4, 64))
        self.assertEqual(cache.descarga_final, 4)

    def test_wt_envia_palavra_em_acerto_e_falta_sem_sujar_ou_gerar_writeback(self):
        cache = Cache(Configuracao.criar(64, 16, 1, "WT"))
        operacoes = [
            ("W", 0x10000000), ("W", 0x10000004),
            ("R", 0x10000040), ("W", 0x10000044),
            ("R", 0x10000080), ("W", 0x10000010),
        ]
        resultados = []
        for operacao, endereco in operacoes:
            resultados.append(acessar(cache, operacao, endereco))
            self.assertTrue(all(not v.modificada for c in cache.conjuntos for v in c))

        self.assertEqual([r.acertou for r in resultados], [False, True, False, True, False, False])
        self.assertTrue(all(not r.houve_writeback for r in resultados))
        self.assertEqual((cache.blocos_lidos, cache.bytes_lidos), (4, 64))
        self.assertEqual((cache.escritas, cache.bytes_escritos), (4, 16))
        cache.descarregar()
        self.assertEqual((cache.writebacks, cache.descarga_final), (0, 0))
        self.assertEqual((cache.escritas, cache.bytes_escritos), (4, 16))

    def test_c3_politica_muda_trafego_de_escrita_sem_mudar_acertos(self):
        acessos = ler_traco(CALIBRACAO / "C3_escrita.txt")
        wb, resumo_wb = simular(Configuracao.criar(64, 16, 1, "WB"), acessos)
        wt, resumo_wt = simular(Configuracao.criar(64, 16, 1, "WT"), acessos)

        self.assertEqual([r.acertou for r in wb], [r.acertou for r in wt])
        self.assertEqual([r.tipo_falta for r in wb], [r.tipo_falta for r in wt])
        self.assertEqual([r.bloco_expulso for r in wb], [r.bloco_expulso for r in wt])
        self.assertEqual(resumo_wb.taxa_acerto, resumo_wt.taxa_acerto)
        self.assertEqual(resumo_wb.bytes_lidos, resumo_wt.bytes_lidos)
        self.assertEqual([r.numero for r in wb if r.houve_writeback], [4, 7, 9])
        self.assertTrue(all(not r.houve_writeback for r in wt))
        self.assertEqual((resumo_wb.writebacks, resumo_wb.descarga_final), (3, 1))
        self.assertEqual((resumo_wb.escritas, resumo_wb.bytes_escritos), (4, 64))
        self.assertEqual((resumo_wt.writebacks, resumo_wt.descarga_final), (0, 0))
        self.assertEqual((resumo_wt.escritas, resumo_wt.bytes_escritos), (6, 24))


if __name__ == "__main__":
    unittest.main()
