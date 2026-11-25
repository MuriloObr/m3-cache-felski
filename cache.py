"""Nucleo da cache: vias, LRU, politicas de escrita e classificacao de faltas.

Autores:
  - Murilo Dressel Obregão
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass

from parametros import TAMANHO_PALAVRA


@dataclass
class Via:
    valida: bool = False
    rotulo: int = 0
    modificada: bool = False
    ultimo_uso: int = 0


@dataclass(frozen=True)
class ResultadoCache:
    acertou: bool
    bloco_expulso: int | None
    houve_writeback: bool


class Cache:
    def __init__(self, configuracao):
        self.configuracao = configuracao
        self.conjuntos = [
            [Via() for _ in range(configuracao.vias)]
            for _ in range(configuracao.conjuntos)
        ]
        self.relogio = 0

        self.blocos_lidos = 0
        self.bytes_lidos = 0
        self.escritas = 0
        self.bytes_escritos = 0
        self.writebacks = 0
        self.descarga_final = 0

    def acessar(self, rotulo, indice, operacao):
        conjunto = self.conjuntos[indice]
        via = self._procurar(conjunto, rotulo)

        if via is not None:
            self._tocar(via)
            if operacao == "W":
                self._aplicar_escrita(via)
            return ResultadoCache(
                acertou=True,
                bloco_expulso=None,
                houve_writeback=False,
            )

        vitima = self._escolher_vitima(conjunto)
        bloco_expulso = None
        houve_writeback = False

        if vitima.valida:
            bloco_expulso = self.configuracao.endereco_do_bloco(
                vitima.rotulo, indice
            )
            if vitima.modificada:
                self._registrar_writeback()
                houve_writeback = True

        self.blocos_lidos += 1
        self.bytes_lidos += self.configuracao.bloco

        vitima.valida = True
        vitima.rotulo = rotulo
        vitima.modificada = False
        self._tocar(vitima)

        if operacao == "W":
            self._aplicar_escrita(vitima)

        return ResultadoCache(
            acertou=False,
            bloco_expulso=bloco_expulso,
            houve_writeback=houve_writeback,
        )

    def descarregar(self):
        for conjunto in self.conjuntos:
            for via in conjunto:
                if via.valida and via.modificada:
                    via.modificada = False
                    self.descarga_final += 1
                    self.escritas += 1
                    self.bytes_escritos += self.configuracao.bloco

    def _procurar(self, conjunto, rotulo):
        for via in conjunto:
            if via.valida and via.rotulo == rotulo:
                return via
        return None

    def _escolher_vitima(self, conjunto):
        for via in conjunto:
            if not via.valida:
                return via
        return min(conjunto, key=lambda via: via.ultimo_uso)

    def _tocar(self, via):
        self.relogio += 1
        via.ultimo_uso = self.relogio

    def _aplicar_escrita(self, via):
        if self.configuracao.escrita == "WB":
            via.modificada = True
        else:
            self._registrar_escrita_de_palavra()

    def _registrar_escrita_de_palavra(self):
        self.escritas += 1
        self.bytes_escritos += TAMANHO_PALAVRA

    def _registrar_writeback(self):
        self.writebacks += 1
        self.escritas += 1
        self.bytes_escritos += self.configuracao.bloco


class ClassificadorFaltas:
    """Cache totalmente associativa LRU paralela, usada so para classificar.

    Ela recebe todos os acessos, inclusive os acertos da cache configurada, e
    atualiza o LRU em cada acesso. Nao aparece na saida.
    """

    def __init__(self, configuracao):
        self.total_de_blocos = configuracao.capacidade // configuracao.bloco
        self.blocos_vistos = set()
        self.ordem_lru = OrderedDict()

    def classificar(self, bloco):
        if bloco not in self.blocos_vistos:
            tipo = "compulsoria"
        elif bloco in self.ordem_lru:
            tipo = "conflito"
        else:
            tipo = "capacidade"

        self.blocos_vistos.add(bloco)
        self._atualizar(bloco)
        return tipo

    def registrar_acerto(self, bloco):
        self.blocos_vistos.add(bloco)
        self._atualizar(bloco)

    def _atualizar(self, bloco):
        if bloco in self.ordem_lru:
            self.ordem_lru.move_to_end(bloco)
            return
        if len(self.ordem_lru) >= self.total_de_blocos:
            self.ordem_lru.popitem(last=False)
        self.ordem_lru[bloco] = None
