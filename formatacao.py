"""Formatacao da saida no contrato dos gabaritos de calibracao.

Esta e a unica parte sensivel a espacos, larguras e alinhamento; por isso fica
isolada do nucleo da simulacao.

Autores:
  - Murilo Dressel Obregão
"""


def formatar_saida(configuracao, resultados, resumo):
    linhas = [
        (
            f"CONFIGURACAO  capacidade={configuracao.capacidade} B  "
            f"bloco={configuracao.bloco} B  vias={configuracao.vias}  "
            f"conjuntos={configuracao.conjuntos}  "
            f"escrita={configuracao.escrita}"
        ),
        (
            f"{'CAMPOS':<14}rotulo={configuracao.bits_rotulo} bits  "
            f"indice={configuracao.bits_indice} bits  "
            f"offset={configuracao.bits_offset} bits"
        ),
        "",
    ]

    for resultado in resultados:
        linhas.append(_formatar_acesso(configuracao, resultado))

    if resultados:
        linhas.append("")

    linhas.extend(_formatar_resumo(configuracao, resumo))
    return "\n".join(linhas) + "\n"


def _formatar_acesso(configuracao, resultado):
    prefixo = (
        f"{resultado.numero:4d}  {resultado.operacao} "
        f"0x{resultado.endereco:08X}  "
        f"rot=0x{resultado.rotulo:0{configuracao.largura_rotulo}X}  "
        f"idx={resultado.indice:<3d} off={resultado.offset:<3d} "
    )

    if resultado.acertou:
        return prefixo + "ACERTO"

    if resultado.bloco_expulso is None:
        return prefixo + "FALTA  " + resultado.tipo_falta

    linha = (
        prefixo
        + f"FALTA  {resultado.tipo_falta:<12}"
        + f"expulsa 0x{resultado.bloco_expulso:08X}"
    )
    if resultado.houve_writeback:
        linha += " (writeback)"
    return linha


def _formatar_resumo(configuracao, resumo):
    linhas = [
        _com_pontos("acessos", resumo.acessos),
        _com_pontos("acertos", resumo.acertos),
        _com_pontos(
            "faltas",
            (
                f"{resumo.faltas}  (compulsorias {resumo.compulsorias}, "
                f"conflito {resumo.conflitos}, "
                f"capacidade {resumo.capacidades})"
            ),
        ),
        _com_pontos("taxa de acerto", f"{resumo.taxa_acerto:.2f}%"),
        f"blocos lidos da mem.  {resumo.blocos_lidos}  ({resumo.bytes_lidos} B)",
    ]

    escritas = (
        f"escritas na memoria  {resumo.escritas}  "
        f"({resumo.bytes_escritos} B)"
    )
    if configuracao.escrita == "WB":
        escritas += (
            f"  [writebacks {resumo.writebacks} + "
            f"descarga final {resumo.descarga_final}]"
        )
    linhas.append(escritas)
    return linhas


def _com_pontos(rotulo, valor):
    return f"{rotulo} {'.' * (20 - len(rotulo))} {valor}"
