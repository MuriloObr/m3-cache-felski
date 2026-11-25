#!/usr/bin/env python3
"""Simulador de cache configuravel — UNIVALI, Organizacao de Computadores.

Executa um traco de acessos a memoria com capacidade, tamanho de bloco,
numero de vias e politica de escrita escolhidos na linha de comando.

Autores:
  - Murilo Dressel Obregão
"""

import argparse
import sys

from formatacao import formatar_saida
from parametros import Configuracao, ErroParametros
from simulacao import simular
from traco import ErroTraco, ler_traco


def montar_analisador():
    analisador = argparse.ArgumentParser(
        description=(
            "Simula uma cache e imprime um relatorio por acesso e um resumo."
        )
    )
    analisador.add_argument(
        "--traco",
        required=True,
        metavar="ARQUIVO",
        help="arquivo de traco (uma linha por acesso: 'R 0x...' ou 'W 0x...')",
    )
    analisador.add_argument(
        "--capacidade",
        required=True,
        type=int,
        metavar="BYTES",
        help="capacidade de dados da cache em bytes (potencia de 2)",
    )
    analisador.add_argument(
        "--bloco",
        required=True,
        type=int,
        metavar="BYTES",
        help="tamanho do bloco em bytes (potencia de 2, minimo 4)",
    )
    analisador.add_argument(
        "--vias",
        required=True,
        type=int,
        help="numero de vias por conjunto (potencia de 2)",
    )
    analisador.add_argument(
        "--escrita",
        required=True,
        metavar="WB|WT",
        help="politica de escrita: WB (write-back) ou WT (write-through)",
    )
    return analisador


def principal(argumentos=None):
    analisador = montar_analisador()
    opcoes = analisador.parse_args(argumentos)

    try:
        configuracao = Configuracao.criar(
            capacidade=opcoes.capacidade,
            bloco=opcoes.bloco,
            vias=opcoes.vias,
            escrita=opcoes.escrita,
        )
        acessos = ler_traco(opcoes.traco)
    except (ErroParametros, ErroTraco) as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2

    resultados, resumo = simular(configuracao, acessos)
    sys.stdout.write(formatar_saida(configuracao, resultados, resumo))
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
