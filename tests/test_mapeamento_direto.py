"""Semantica do mapeamento direto e determinismo da saida.

Autores:
  - Murilo Dressel Obregão
"""

import unittest

from tests.apoio import TRACO_C1, criar_traco_temporario, rodar_configuracao


class TesteMapeamentoDireto(unittest.TestCase):
    def test_cache_comeca_vazia_e_expulsa_o_bloco_do_mesmo_indice(self):
        # Capacidade 32 B, bloco 16 B, 1 via: dois conjuntos.
        # 0x00, 0x08 e 0x40 caem no indice 0 e disputam a unica via.
        traco = criar_traco_temporario(
            self,
            "R 0x00000000\n"
            "R 0x00000004\n"
            "R 0x00000040\n"
            "R 0x00000008\n",
        )
        resultado = rodar_configuracao(traco, 32, 16, 1, "WB")

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        linhas = resultado.stdout.splitlines()
        self.assertIn(
            "   1  R 0x00000000  rot=0x0000000  idx=0   off=0   "
            "FALTA  compulsoria",
            linhas,
        )
        self.assertIn(
            "   2  R 0x00000004  rot=0x0000000  idx=0   off=4   ACERTO",
            linhas,
        )
        self.assertIn(
            "   3  R 0x00000040  rot=0x0000002  idx=0   off=0   "
            "FALTA  compulsoria expulsa 0x00000000",
            linhas,
        )
        self.assertIn(
            "   4  R 0x00000008  rot=0x0000000  idx=0   off=8   "
            "FALTA  conflito    expulsa 0x00000040",
            linhas,
        )
        self.assertIn(
            "faltas .............. 3  "
            "(compulsorias 2, conflito 1, capacidade 0)",
            resultado.stdout,
        )
        self.assertIn("blocos lidos da mem.  3  (48 B)", resultado.stdout)
        self.assertIn(
            "escritas na memoria  0  (0 B)  [writebacks 0 + descarga final 0]",
            resultado.stdout,
        )

    def test_duas_execucoes_do_mesmo_caso_produzem_saida_identica(self):
        primeira = rodar_configuracao(TRACO_C1, 128, 16, 1, "WB")
        segunda = rodar_configuracao(TRACO_C1, 128, 16, 1, "WB")

        self.assertEqual(primeira.returncode, 0, primeira.stderr)
        self.assertEqual(segunda.returncode, 0, segunda.stderr)
        self.assertEqual(primeira.stdout, segunda.stdout)

    def test_resumo_do_c1_tem_contadores_de_escrita_zerados(self):
        resultado = rodar_configuracao(TRACO_C1, 128, 16, 1, "WB")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn(
            "escritas na memoria  0  (0 B)  [writebacks 0 + descarga final 0]",
            resultado.stdout,
        )

    def test_cabecalho_do_c1_tem_a_divisao_do_endereco(self):
        resultado = rodar_configuracao(TRACO_C1, 128, 16, 1, "WB")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn(
            "CONFIGURACAO  capacidade=128 B  bloco=16 B  vias=1  "
            "conjuntos=8  escrita=WB",
            resultado.stdout,
        )
        self.assertIn(
            "CAMPOS        rotulo=25 bits  indice=3 bits  offset=4 bits",
            resultado.stdout,
        )


if __name__ == "__main__":
    unittest.main()
