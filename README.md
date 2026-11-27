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

As duas políticas de escrita usam write-allocate: uma escrita que falta lê o
bloco inteiro. Em WB, a escrita marca o bloco como modificado; sua expulsão
grava o bloco inteiro e aparece como `(writeback)` na saída. O resumo separa
esses writebacks da descarga final, que percorre conjuntos e vias em ordem.
Em WT, cada escrita envia 4 bytes à memória e nenhum bloco fica modificado.
A política altera o tráfego de escrita, mantendo os mesmos acertos e faltas.

Os testes de semântica cobrem alocação em escrita, bit de modificação, expulsão
durante o traço e descarga final em múltiplos conjuntos e vias. O teste de ouro
do C3 compara as saídas de WB e WT byte a byte com as duas seções do gabarito:

```sh
python3 -m unittest tests.test_politicas_escrita tests.test_calibracao_c2_c4 -v
```

A classificação usa uma cache auxiliar totalmente associativa LRU, com a mesma
capacidade e o mesmo bloco da cache configurada. Ela recebe todos os acessos,
inclusive os acertos, e não aparece na saída. O primeiro acesso a um bloco é
compulsório; nas demais faltas, um acerto na auxiliar indica conflito e uma
falta nela indica capacidade.

Os testes verificam a atualização do LRU auxiliar tanto nos acertos da cache
configurada quanto nas faltas que acertam na auxiliar, a classificação por bloco,
os acessos 8 e 9 do C4 e a soma dos contadores:

```sh
python3 -m unittest tests.test_classificacao_faltas tests.test_calibracao_c2_c4 -v
```
