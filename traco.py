"""Leitura do arquivo de traco.

Formato: uma linha por acesso, `R` ou `W` seguido do endereco em hexadecimal.
Tudo depois de `#` e comentario. Linhas em branco sao ignoradas.

Autores:
  - Murilo Dressel Obregão
"""

from dataclasses import dataclass

from parametros import TAMANHO_PALAVRA

ENDERECO_MAXIMO = 0xFFFFFFFF


class ErroTraco(ValueError):
    """Arquivo de traco ausente ou malformado."""


@dataclass(frozen=True)
class Acesso:
    numero: int
    operacao: str
    endereco: int


def ler_traco(caminho):
    try:
        arquivo = open(caminho, "r", encoding="utf-8-sig", newline=None)
    except OSError as erro:
        motivo = erro.strerror or str(erro)
        raise ErroTraco(
            f"nao foi possivel ler o traco '{caminho}': {motivo}"
        ) from erro

    acessos = []
    with arquivo:
        for numero_da_linha, linha in enumerate(arquivo, start=1):
            conteudo = linha.split("#", 1)[0].strip()
            if not conteudo:
                continue

            campos = conteudo.split()
            if len(campos) != 2:
                raise ErroTraco(
                    f"linha {numero_da_linha}: esperado 'R 0x...' ou 'W 0x...', "
                    f"recebido '{conteudo}'"
                )

            operacao = campos[0].upper()
            if operacao not in ("R", "W"):
                raise ErroTraco(
                    f"linha {numero_da_linha}: operacao deve ser R ou W "
                    f"(recebido: '{campos[0]}')"
                )

            try:
                endereco = int(campos[1], 16)
            except ValueError as erro:
                raise ErroTraco(
                    f"linha {numero_da_linha}: endereco hexadecimal invalido "
                    f"'{campos[1]}'"
                ) from erro

            if endereco < 0 or endereco > ENDERECO_MAXIMO:
                raise ErroTraco(
                    f"linha {numero_da_linha}: endereco {campos[1]} nao cabe em "
                    "32 bits"
                )
            if endereco % TAMANHO_PALAVRA != 0:
                raise ErroTraco(
                    f"linha {numero_da_linha}: endereco 0x{endereco:08X} deve "
                    f"estar alinhado em {TAMANHO_PALAVRA} bytes"
                )

            acessos.append(
                Acesso(
                    numero=len(acessos) + 1,
                    operacao=operacao,
                    endereco=endereco,
                )
            )

    return acessos
