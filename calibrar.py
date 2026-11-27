#!/usr/bin/env python3
"""Executa somente C1-C4 e compara as respostas byte a byte.

Autores:
  - Murilo Dressel Obregão
"""

import difflib
from pathlib import Path
import subprocess
import sys


RAIZ = Path(__file__).resolve().parent
CALIBRACAO = RAIZ / "docs" / "calibracao"
SAIDAS = RAIZ / "resultados" / "calibracao"
CASOS = (
    ("C1_mapeamento_direto", 128, 16, 1, ("WB",)),
    ("C2_associativa_LRU", 64, 16, 2, ("WB",)),
    ("C3_escrita", 64, 16, 1, ("WB", "WT")),
    ("C4_classificacao", 64, 16, 1, ("WB",)),
)
SEPARADOR_C3 = b"\n" + b"=" * 70 + b"\n\n"


def executar(nome, capacidade, bloco, vias, politicas):
    secoes = []
    for politica in politicas:
        comando = [
            sys.executable, str(RAIZ / "simulador.py"),
            "--traco", str(CALIBRACAO / f"{nome}.txt"),
            "--capacidade", str(capacidade), "--bloco", str(bloco),
            "--vias", str(vias), "--escrita", politica,
        ]
        resultado = subprocess.run(comando, capture_output=True, cwd=RAIZ)
        if resultado.returncode != 0:
            detalhe = resultado.stderr.decode("utf-8", errors="backslashreplace")
            raise RuntimeError(
                f"{politica}: simulador terminou com codigo {resultado.returncode}\n{detalhe}"
            )
        secoes.append(resultado.stdout)
    return SEPARADOR_C3.join(secoes)


def mostrar_diff(esperado, obtido, gabarito, resposta):
    # O indice e os bytes tornam visiveis diferencas como CRLF e ausencia
    # de LF final, mesmo quando o terminal exibe linhas parecidas.
    posicao = next(
        (i for i, (a, b) in enumerate(zip(esperado, obtido)) if a != b),
        min(len(esperado), len(obtido)),
    )
    print(
        f"Primeira diferenca no byte {posicao} (indice a partir de zero): "
        f"esperado {esperado[posicao:posicao + 1]!r}, "
        f"obtido {obtido[posicao:posicao + 1]!r}. "
        f"Tamanhos: {len(esperado)} e {len(obtido)} bytes.",
        file=sys.stderr,
    )
    linhas = difflib.diff_bytes(
        difflib.unified_diff,
        esperado.splitlines(keepends=True),
        obtido.splitlines(keepends=True),
        fromfile=str(gabarito).encode("utf-8"),
        tofile=str(resposta).encode("utf-8"),
    )
    for linha in linhas:
        sys.stderr.write(linha.decode("utf-8", errors="backslashreplace"))
        if not linha.endswith(b"\n"):
            sys.stderr.write("\n\\ Sem quebra de linha no final\n")


def principal():
    try:
        SAIDAS.mkdir(parents=True, exist_ok=True)
    except OSError as erro:
        print(f"ERRO ao criar diretorio de respostas: {erro}", file=sys.stderr)
        return 1

    falhas = 0
    for nome, capacidade, bloco, vias, politicas in CASOS:
        gabarito = CALIBRACAO / f"{nome}_esperado.txt"
        resposta = SAIDAS / f"{nome}_obtido.txt"
        try:
            obtido = executar(nome, capacidade, bloco, vias, politicas)
            resposta.write_bytes(obtido)
            esperado = gabarito.read_bytes()
        except (OSError, RuntimeError) as erro:
            print(f"ERRO {nome}: {erro}", file=sys.stderr)
            falhas += 1
            continue

        if obtido != esperado:
            print(f"FALHA {nome}: resposta diferente do gabarito.", file=sys.stderr)
            mostrar_diff(esperado, obtido, gabarito, resposta)
            falhas += 1
        else:
            print(f"OK {nome}: resposta identica byte a byte.")

    if falhas:
        print(f"Calibracao reprovada: {falhas} de 4 casos falharam.", file=sys.stderr)
        return 1
    print("Calibracao aprovada: 4 de 4 gabaritos identicos byte a byte.")
    print(f"Respostas salvas em: {SAIDAS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
