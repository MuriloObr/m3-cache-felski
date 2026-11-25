"""Contrato do leitor de traco: comentarios, CRLF e erro com numero de linha.

Autores:
  - Murilo Dressel Obregão
"""

import unittest

from tests.apoio import criar_traco_temporario, rodar_configuracao


class TesteLeitorDeTraco(unittest.TestCase):
    def test_aceita_comentarios_e_linhas_em_branco(self):
        traco = criar_traco_temporario(
            self,
            "R 0x10000000\n"
            "\n"
            "# comentario inteiro\n"
            "R 0x10000004  # comentario no fim da linha\n"
            "   \n"
            "R 0x1000000C\n",
            nome="com_comentarios.txt",
        )
        resultado = rodar_configuracao(traco, 128, 16, 1, "WB")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("acessos ............. 3", resultado.stdout)

    def test_crlf_produz_a_mesma_saida_que_lf(self):
        conteudo = (
            "# traco minimo\n"
            "R 0x10000000\n"
            "R 0x10000004\n"
            "R 0x10000010\n"
        )
        traco_lf = criar_traco_temporario(
            self, conteudo, nome="lf.txt", fim_de_linha="\n"
        )
        traco_crlf = criar_traco_temporario(
            self, conteudo, nome="crlf.txt", fim_de_linha="\r\n"
        )

        resultado_lf = rodar_configuracao(traco_lf, 128, 16, 1, "WB")
        resultado_crlf = rodar_configuracao(traco_crlf, 128, 16, 1, "WB")

        self.assertEqual(resultado_lf.returncode, 0, resultado_lf.stderr)
        self.assertEqual(resultado_crlf.returncode, 0, resultado_crlf.stderr)
        self.assertEqual(resultado_lf.stdout, resultado_crlf.stdout)

    def test_traco_malformado_aponta_o_numero_da_linha(self):
        traco = criar_traco_temporario(
            self,
            "# linha 1\n"
            "R 0x10000000\n"
            "X 0x10000004\n",
            nome="malformado.txt",
        )
        resultado = rodar_configuracao(traco, 128, 16, 1, "WB")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("linha 3", resultado.stderr)

    def test_endereco_desalinhado_aponta_a_linha(self):
        traco = criar_traco_temporario(
            self,
            "R 0x10000000\n"
            "R 0x10000002\n",
            nome="desalinhado.txt",
        )
        resultado = rodar_configuracao(traco, 128, 16, 1, "WB")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("linha 2", resultado.stderr)
        self.assertIn("alinhado", resultado.stderr)

    def test_endereco_fora_de_32_bits_aponta_a_linha(self):
        traco = criar_traco_temporario(
            self,
            "R 0x100000000\n",
            nome="fora.txt",
        )
        resultado = rodar_configuracao(traco, 128, 16, 1, "WB")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("linha 1", resultado.stderr)

    def test_endereco_hexadecimal_invalido_aponta_a_linha(self):
        traco = criar_traco_temporario(
            self,
            "R 0x10000000\n"
            "R 0xXYZ\n",
            nome="invalido.txt",
        )
        resultado = rodar_configuracao(traco, 128, 16, 1, "WB")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("linha 2", resultado.stderr)

    def test_traco_vazio_ainda_produz_cabecalho_e_resumo(self):
        traco = criar_traco_temporario(self, "# nada aqui\n", nome="vazio.txt")
        resultado = rodar_configuracao(traco, 128, 16, 1, "WB")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("acessos ............. 0", resultado.stdout)
        self.assertIn("taxa de acerto ...... 0.00%", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
