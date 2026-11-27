"""Contrato do comando de calibracao, incluindo divergencias e erros.

Autores:
  - Murilo Dressel Obregão
"""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from tests.apoio import CALIBRACAO, RAIZ


class TesteComandoCalibracao(unittest.TestCase):
    def setUp(self):
        temporario = tempfile.TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.diretorio = Path(temporario.name)
        self.projeto = self.diretorio / "projeto"
        self.projeto.mkdir()
        for arquivo in RAIZ.glob("*.py"):
            shutil.copy2(arquivo, self.projeto / arquivo.name)
        self.calibracao = self.projeto / "docs" / "calibracao"
        shutil.copytree(CALIBRACAO, self.calibracao)
        # Nao copiamos experimentos: o comando deve funcionar sem eles.

    def executar(self):
        return subprocess.run(
            [sys.executable, str(self.projeto / "calibrar.py")],
            cwd=self.diretorio, capture_output=True, text=True,
        )

    def test_aprova_quatro_gabaritos_salva_respostas_e_independe_do_cwd(self):
        resultado = self.executar()

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stderr, "")
        self.assertIn("Calibracao aprovada: 4 de 4", resultado.stdout)
        respostas = sorted((self.projeto / "resultados" / "calibracao").glob("*.txt"))
        gabaritos = sorted(self.calibracao.glob("*_esperado.txt"))
        self.assertEqual(len(respostas), 4)
        for resposta, gabarito in zip(respostas, gabaritos):
            self.assertEqual(resposta.stem, gabarito.stem.replace("_esperado", "_obtido"))
            self.assertEqual(resposta.read_bytes(), gabarito.read_bytes())

    def test_qualquer_gabarito_divergente_reprova_com_diff_sem_pular_outros(self):
        for gabarito in sorted(self.calibracao.glob("*_esperado.txt")):
            with self.subTest(gabarito=gabarito.name):
                original = gabarito.read_bytes()
                gabarito.write_bytes(original.replace(b"CONFIGURACAO", b"XONFIGURACAO", 1))
                try:
                    resultado = self.executar()
                finally:
                    gabarito.write_bytes(original)

                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn("Calibracao reprovada: 1 de 4", resultado.stderr)
                self.assertIn(f"--- {gabarito}", resultado.stderr)
                self.assertIn("+++ ", resultado.stderr)
                self.assertIn("-XONFIGURACAO", resultado.stderr)
                self.assertIn("+CONFIGURACAO", resultado.stderr)
                self.assertEqual(resultado.stdout.count("OK C"), 3)

    def test_comparacao_recusa_crlf_e_ausencia_de_lf_final(self):
        gabarito = self.calibracao / "C1_mapeamento_direto_esperado.txt"
        original = gabarito.read_bytes()
        for nome, alterado in (
            ("CRLF", original.replace(b"\n", b"\r\n")),
            ("sem LF final", original[:-1]),
        ):
            with self.subTest(alteracao=nome):
                gabarito.write_bytes(alterado)
                resultado = self.executar()
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn("Primeira diferenca no byte", resultado.stderr)
                self.assertIn("--- ", resultado.stderr)
                self.assertIn("+++ ", resultado.stderr)

    def test_gabarito_ausente_reprova_com_mensagem_sem_traceback(self):
        (self.calibracao / "C4_classificacao_esperado.txt").unlink()

        resultado = self.executar()

        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("ERRO C4_classificacao", resultado.stderr)
        self.assertNotIn("Traceback", resultado.stderr)

    def test_erro_do_simulador_reprova_e_preserva_diagnostico(self):
        (self.calibracao / "C2_associativa_LRU.txt").write_text("R 0x1\n", encoding="utf-8")

        resultado = self.executar()

        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("ERRO C2_associativa_LRU", resultado.stderr)
        self.assertIn("simulador terminou com codigo 2", resultado.stderr)
        self.assertIn("linha 1", resultado.stderr)
        self.assertEqual(resultado.stdout.count("OK C"), 3)


if __name__ == "__main__":
    unittest.main()
