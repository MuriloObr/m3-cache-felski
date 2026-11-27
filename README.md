# Simulador de cache — UNIVALI

Avaliação prática de Organização de Computadores.

**Autores:** Murilo Dressel Obregão

Simulador de cache em Python 3, sem dependências externas. Todos os parâmetros
são passados na linha de comando; nenhuma configuração exige editar o código.

## Uso

```sh
python3 simulador.py \
  --traco docs/calibracao/C1_mapeamento_direto.txt \
  --capacidade 128 \
  --bloco 16 \
  --vias 1 \
  --escrita WB
```

- `--capacidade`: bytes de dados da cache (potência de 2).
- `--bloco`: tamanho do bloco em bytes (potência de 2, mínimo 4).
- `--vias`: vias por conjunto (potência de 2, no máximo o número de blocos).
- `--escrita`: `WB` (write-back) ou `WT` (write-through), sem diferenciar
  maiúsculas de minúsculas.

A saída traz uma linha por acesso (rótulo, índice, offset, acerto ou falta,
tipo da falta, bloco expulso e writeback) e um resumo. Parâmetros impossíveis e
traços malformados terminam com código de saída diferente de zero e mensagem
com a linha do erro.

## Testes

```sh
python3 -m unittest discover -v
```

Os testes atravessam a fronteira do processo e comparam byte a byte a saída do
simulador com os quatro gabaritos de `docs/calibracao/`.

A associatividade usa LRU por conjunto: acertos e preenchimentos renovam o uso
da via, e a substituição escolhe a via menos recentemente usada. Os testes de
semântica verificam a vítima e o acerto no acesso 5 do C2 (que distingue LRU de
FIFO), a independência dos conjuntos e configurações de 2 a 16 vias:

```sh
python3 -m unittest tests.test_associatividade_lru -v
```
