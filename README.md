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

## Calibração obrigatória

Antes de executar qualquer experimento, rode na raiz do projeto:

```sh
python3 calibrar.py
```

O comando usa somente Python 3 e a biblioteca padrão. Executa C1 (128 B,
bloco 16 B, 1 via, WB), C2 (64 B, bloco 16 B, 2 vias, WB), C3 (64 B,
bloco 16 B, 1 via, WB e WT) e C4 (64 B, bloco 16 B, 1 via, WB).
Nenhum traço de experimento é executado.

As quatro respostas ficam em `resultados/calibracao/*_obtido.txt`. O C3 reúne
WB e WT em um arquivo: após a saída WB, acrescenta uma linha em branco,
70 sinais de igual e outra linha em branco antes da saída WT.

Cada resposta é comparada byte a byte com seu gabarito em `docs/calibracao/`,
incluindo espaços e quebras de linha. Sucesso termina com código 0; qualquer
divergência ou erro termina com código 1. Uma divergência mostra o diff e a
posição do primeiro byte diferente. Os outros casos continuam sendo verificados.
Os arquivos de resposta são sobrescritos a cada execução; os gabaritos são
apenas lidos. Só prossiga para os experimentos quando os quatro forem aprovados.

## Testes

Execute também a suíte de contrato, semântica e determinismo:

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
