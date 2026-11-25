"""Apoio comum dos testes: executa o simulador pela fronteira do processo.

Autores:
  - Murilo Dressel Obregão
"""

import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SIMULADOR = RAIZ / "simulador.py"
DOCS = RAIZ / "docs"
CALIBRACAO = DOCS / "calibracao"
TRACO_C1 = CALIBRACAO / "C1_mapeamento_direto.txt"


def rodar_simulador(*argumentos):
    return subprocess.run(
        [sys.executable, str(SIMULADOR), *map(str, argumentos)],
        capture_output=True,
        text=True,
        cwd=RAIZ,
    )


def rodar_simulador_bytes(*argumentos):
    """Executa sem decodificar, para comparar a saida byte a byte."""
    return subprocess.run(
        [sys.executable, str(SIMULADOR), *map(str, argumentos)],
        capture_output=True,
        cwd=RAIZ,
    )


def rodar_configuracao(traco, capacidade, bloco, vias, escrita):
    return rodar_simulador(
        "--traco", traco,
        "--capacidade", capacidade,
        "--bloco", bloco,
        "--vias", vias,
        "--escrita", escrita,
    )


def rodar_configuracao_bytes(traco, capacidade, bloco, vias, escrita):
    return rodar_simulador_bytes(
        "--traco", traco,
        "--capacidade", capacidade,
        "--bloco", bloco,
        "--vias", vias,
        "--escrita", escrita,
    )


def criar_traco_temporario(caso, conteudo, nome="traco.txt", fim_de_linha="\n"):
    diretorio = tempfile.TemporaryDirectory()
    caso.addCleanup(diretorio.cleanup)
    caminho = Path(diretorio.name) / nome
    texto = conteudo.replace("\n", fim_de_linha)
    caminho.write_bytes(texto.encode("utf-8"))
    return caminho
