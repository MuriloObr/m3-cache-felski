"""Execucao do traco e montagem do resumo.

Autores:
  - Murilo Dressel Obregão
"""

from __future__ import annotations

from dataclasses import dataclass

from cache import Cache, ClassificadorFaltas


@dataclass(frozen=True)
class ResultadoAcesso:
    numero: int
    operacao: str
    endereco: int
    rotulo: int
    indice: int
    offset: int
    acertou: bool
    tipo_falta: str | None
    bloco_expulso: int | None
    houve_writeback: bool


@dataclass(frozen=True)
class Resumo:
    acessos: int
    acertos: int
    compulsorias: int
    conflitos: int
    capacidades: int
    taxa_acerto: float
    blocos_lidos: int
    bytes_lidos: int
    escritas: int
    bytes_escritos: int
    writebacks: int
    descarga_final: int

    @property
    def faltas(self):
        return self.acessos - self.acertos


def simular(configuracao, acessos):
    cache = Cache(configuracao)
    classificador = ClassificadorFaltas(configuracao)

    resultados = []
    for acesso in acessos:
        rotulo, indice, offset = configuracao.decompor(acesso.endereco)
        bloco = acesso.endereco - offset
        resultado_da_cache = cache.acessar(rotulo, indice, acesso.operacao)

        if resultado_da_cache.acertou:
            classificador.registrar_acerto(bloco)
            tipo_falta = None
        else:
            tipo_falta = classificador.classificar(bloco)

        resultados.append(
            ResultadoAcesso(
                numero=acesso.numero,
                operacao=acesso.operacao,
                endereco=acesso.endereco,
                rotulo=rotulo,
                indice=indice,
                offset=offset,
                acertou=resultado_da_cache.acertou,
                tipo_falta=tipo_falta,
                bloco_expulso=resultado_da_cache.bloco_expulso,
                houve_writeback=resultado_da_cache.houve_writeback,
            )
        )

    cache.descarregar()

    acertos = sum(1 for resultado in resultados if resultado.acertou)
    compulsorias = sum(
        1 for resultado in resultados if resultado.tipo_falta == "compulsoria"
    )
    conflitos = sum(
        1 for resultado in resultados if resultado.tipo_falta == "conflito"
    )
    capacidades = sum(
        1 for resultado in resultados if resultado.tipo_falta == "capacidade"
    )

    total = len(resultados)
    taxa = (acertos / total * 100.0) if total else 0.0

    resumo = Resumo(
        acessos=total,
        acertos=acertos,
        compulsorias=compulsorias,
        conflitos=conflitos,
        capacidades=capacidades,
        taxa_acerto=taxa,
        blocos_lidos=cache.blocos_lidos,
        bytes_lidos=cache.bytes_lidos,
        escritas=cache.escritas,
        bytes_escritos=cache.bytes_escritos,
        writebacks=cache.writebacks,
        descarga_final=cache.descarga_final,
    )
    return resultados, resumo
