"""Configuracao e validacao dos parametros da cache.

Autores:
  - Murilo Dressel Obregão
"""

from dataclasses import dataclass

TAMANHO_PALAVRA = 4


class ErroParametros(ValueError):
    """Parametros de cache invalidos ou impossiveis."""


def eh_potencia_de_dois(valor):
    return valor > 0 and (valor & (valor - 1)) == 0


@dataclass(frozen=True)
class Configuracao:
    capacidade: int
    bloco: int
    vias: int
    escrita: str

    @classmethod
    def criar(cls, capacidade, bloco, vias, escrita):
        if not eh_potencia_de_dois(capacidade):
            raise ErroParametros(
                "capacidade deve ser uma potencia de 2 maior que zero "
                f"(recebido: {capacidade})"
            )
        if bloco < 4:
            raise ErroParametros(
                f"bloco deve ter no minimo 4 bytes (recebido: {bloco})"
            )
        if bloco % 4 != 0:
            raise ErroParametros(
                f"bloco deve ser multiplo de 4 bytes (recebido: {bloco})"
            )
        if not eh_potencia_de_dois(bloco):
            raise ErroParametros(
                f"bloco deve ser uma potencia de 2 (recebido: {bloco})"
            )
        if not eh_potencia_de_dois(vias):
            raise ErroParametros(
                f"vias deve ser uma potencia de 2 maior que zero (recebido: {vias})"
            )
        if capacidade < bloco:
            raise ErroParametros(
                f"capacidade ({capacidade}) deve ser pelo menos um bloco ({bloco})"
            )

        numero_de_blocos = capacidade // bloco
        if vias > numero_de_blocos:
            raise ErroParametros(
                f"vias ({vias}) nao pode ser maior que o numero de blocos "
                f"({numero_de_blocos})"
            )

        politica = escrita.strip().upper()
        if politica not in ("WB", "WT"):
            raise ErroParametros(
                f"politica de escrita deve ser WB ou WT (recebido: {escrita})"
            )

        configuracao = cls(
            capacidade=capacidade,
            bloco=bloco,
            vias=vias,
            escrita=politica,
        )
        if configuracao.bits_rotulo <= 0:
            raise ErroParametros(
                "capacidade, bloco e vias geram um indice que nao cabe em "
                "enderecos de 32 bits"
            )
        return configuracao

    @property
    def conjuntos(self):
        return self.capacidade // (self.bloco * self.vias)

    @property
    def bits_offset(self):
        return self.bloco.bit_length() - 1

    @property
    def bits_indice(self):
        return self.conjuntos.bit_length() - 1

    @property
    def bits_rotulo(self):
        return 32 - self.bits_indice - self.bits_offset

    @property
    def largura_rotulo(self):
        return (self.bits_rotulo + 3) // 4

    def decompor(self, endereco):
        offset = endereco & (self.bloco - 1)
        indice = (endereco >> self.bits_offset) & (self.conjuntos - 1)
        rotulo = endereco >> (self.bits_offset + self.bits_indice)
        return rotulo, indice, offset

    def endereco_do_bloco(self, rotulo, indice):
        deslocamento = self.bits_offset + self.bits_indice
        return (rotulo << deslocamento) | (indice << self.bits_offset)
