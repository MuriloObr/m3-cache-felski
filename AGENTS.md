# AGENTS.md — Simulador de Cache (UNIVALI)

## Contexto

Avaliação prática de Organização de Computadores (UNIVALI, Prof. Thiago Felski Pereira).
O simulador é o instrumento; o produto avaliado é o relatório de experimentos. A maior parte
da nota está em medir e explicar o efeito de cada decisão de projeto, não no código.

- Fonte de verdade: `docs/ATIVIDADE.pdf`. Este arquivo resume o enunciado; em caso de dúvida
  ou conflito, vale o PDF.
- Trabalho em duplas ou trios; código e relatório devem identificar os autores.
- Prazo no AVA 2.0. Entrega na aula seguinte vale 70% da nota.
- Linguagem livre; o simulador deve rodar várias configurações sem editar o código.

## Estado atual

- Simulador em Python 3 (apenas biblioteca padrão) na raiz: `simulador.py` e os módulos
  `parametros.py`, `traco.py`, `cache.py`, `simulacao.py` e `formatacao.py`.
- `docs/calibracao/` (C1–C4 com gabaritos) e `docs/experimentos/` (E1–E6) estão no repositório.
- Os quatro gabaritos de calibração são reproduzidos byte a byte e cobertos por testes de ouro
  (`python3 -m unittest discover -v`).
- Experimentos E1–E6, desafio, folha de previsões e relatório ainda pendentes.

## Entregáveis

1. Simulador de cache correto e configurável.
2. Calibração: reproduzir exatamente as saídas de C1–C4.
3. Experimentos E1–E6 com tabelas preenchidas e respostas.
4. Desafio: traço próprio, tabela medida e explicação da construção.
5. Relatório com Previsão, Medição, Justificativa e Conciliação por experimento.
6. Folha de previsões preenchida antes de rodar os experimentos.

## Regras do simulador

### Entrada

- Traço: uma linha por acesso, `R 0x...` ou `W 0x...`; tudo após `#` é comentário.
- Endereços de 32 bits, em bytes; cada acesso lê ou escreve uma palavra de 4 bytes alinhada.
- Parâmetros: capacidade (bytes de dados), tamanho do bloco (bytes), vias e política de
  escrita (`WT` ou `WB`).
- Todos os valores numéricos são potências de 2.
- `conjuntos = capacidade / (bloco × vias)`.
- Recusar combinações impossíveis (por exemplo, mais vias do que blocos).

### Funcionamento

- Divisão do endereço: `rótulo | índice | offset`.
- Apenas acessos a dados; busca de instruções não é simulada.
- LRU dentro do conjunto; um acerto também conta como uso.
- Write-allocate nas duas políticas: uma escrita que falta traz o bloco para a cache.
- `WT`: cada escrita envia uma palavra (4 bytes) à memória; blocos nunca ficam modificados.
- `WB`: a escrita liga o bit de modificação (D). Expulsão de bloco com D=1 gera writeback do
  bloco inteiro. Ao final do traço, blocos que continuam com D=1 são descarregados (descarga
  final), contados separadamente.
- A cache começa vazia: todos os bits de validade em 0.

### Classificação das faltas

- **Compulsória**: primeiro acesso, em todo o traço, àquele bloco de memória.
- **Capacidade**: não é compulsória e também faltaria numa cache totalmente associativa LRU
  com a mesma capacidade e o mesmo tamanho de bloco.
- **Conflito**: não é compulsória e acertaria nessa cache totalmente associativa.
- Implementação: simular em paralelo uma segunda cache totalmente associativa LRU, de mesma
  capacidade e bloco, que recebe todos os acessos. Ela não aparece na saída; serve apenas
  para decidir entre conflito e capacidade.

### Saída

- Por acesso: número, operação, endereço, rótulo, índice, offset, ACERTO/FALTA, tipo da falta
  e, quando houver, endereço do bloco expulso e se a expulsão gerou writeback.
- Resumo: acessos, acertos, faltas separadas por tipo, taxa de acerto, blocos/bytes lidos da
  memória, escritas/bytes enviados à memória. Em `WB`, separar writebacks durante a execução
  da descarga final.
- A aparência é livre, mas todos os campos devem estar presentes.

## Calibração (obrigatória, exata)

| Traço | Configuração | O que valida |
|---|---|---|
| C1_mapeamento_direto | 128 B, bloco 16 B, 1 via | divisão do endereço, bit de validade, expulsão no mesmo índice |
| C2_associativa_LRU | 64 B, bloco 16 B, 2 vias | escolha da vítima por LRU (FIFO erra) |
| C3_escrita | 64 B, bloco 16 B, 1 via, WB e WT | bit D, writeback na expulsão, descarga final, contagem do WT |
| C4_classificacao | 64 B, bloco 16 B, 1 via | os três tipos de falta, inclusive capacidade |

Reproduzir exatamente os quatro arquivos de resposta da pasta `calibracao`. Uma regra que
falha na calibração invalida (ou reduz pela metade) os experimentos que dependem dela.

## Experimentos

Todos os dados começam em `0x10000000`.

| Exp. | Traço | Configuração fixa | Variar | Foco |
|---|---|---|---|---|
| E1 | `E1_varredura.txt` — 128 palavras lidas uma vez | 256 B, 1 via, WB | bloco 4, 8, 16, 32, 64 B | efeito do bloco numa varredura |
| E2 | `E2_registros.txt` — 16 registros de 72 B; lê o 1º campo, 4 passadas | 256 B, 1 via, WB | bloco 4–64 B | bloco com dados espalhados; conflito |
| E3 | `E3_dois_vetores.txt` — soma de 2 vetores de 32 palavras; 2º em +256 B | 256 B, 16 B, WB | vias 1, 2, 4, 16 | associatividade contra conflito; traço modificado |
| E4 | `E1_varredura.txt` | 256 B, 16 B, WB | vias 1, 2, 4, 16 | associatividade numa varredura |
| E5 | `E5_laco_80.txt` e `E5_laco_60.txt` — 3 passadas | 256 B, 16 B, WB | vias 1, 2, 4, 16 | laço maior/menor que a cache; LRU |
| E6 | `E6_acumulador.txt`, `E6_copia.txt`, `E6_esparsa.txt` | 256 B, 16 B, 2 vias | WT, WB | políticas de escrita |

Para cada experimento: preencher a tabela pedida (uma linha por configuração), responder às
perguntas e citar os acessos da saída que comprovam cada afirmação. Tabelas típicas: acertos,
taxa de acerto, faltas compulsórias/conflito/capacidade, bytes lidos e, em E6, bytes escritos.

### Desafio

Com capacidade 256 B e bloco 16 B, construir um traço em que:

- a taxa de acerto com 1 via e com 2 vias seja a mesma e no máximo 10%;
- a taxa de acerto com 4 vias seja pelo menos 70%.

Entregar o arquivo do traço, a tabela medida (1, 2 e 4 vias) e a explicação de por que 2 vias
não bastam e 4 vias resolvem.

## Relatório

Para cada experimento, nesta ordem:

1. **Previsão** — o que se esperava antes de rodar, transcrito da folha de previsões.
2. **Medição** — tabela preenchida com os números do simulador.
3. **Justificativa** — respostas às perguntas, apoiadas em acessos específicos da saída.
4. **Conciliação** — onde previsão e medição divergiram e o erro de raciocínio; se não
   divergiram, basta uma frase.

A folha de previsões é entregue no início do laboratório, antes de qualquer execução.
Errar a previsão não tira ponto; não explicar o erro, sim.

## Distribuição da nota

| Item | Pontos |
|---|---:|
| Calibração C1–C4 | 2,0 |
| E1 | 0,5 |
| E2 | 1,5 |
| E3 | 1,0 |
| E4 | 0,75 |
| E5 | 1,5 |
| E6 | 1,25 |
| Desafio | 1,5 |
| **Total** | **10,0** |

Em cada experimento: 30% medição correta, 50% justificativa, 20% conciliação. A defesa é
individual e pode ajustar a nota de cada integrante.

## Fora do escopo

Políticas de substituição além de LRU, caches de vários níveis, busca de instruções,
prefetch, escrita sem alocação, interface gráfica e animações.

## Fluxo de trabalho

1. Obter no AVA os traços e gabaritos de `calibracao/` e `experimentos/`.
2. Definir linguagem e interface; implementar o simulador.
3. Passar C1–C4 com saída idêntica à dos gabaritos.
4. Preencher a folha de previsões antes de rodar E1–E6.
5. Rodar E1–E6 e o desafio; guardar as saídas brutas e os comandos usados.
6. Preencher as tabelas e escrever as justificativas citando acessos.
7. Montar o relatório e revisar as conciliações.

## Regras para agentes

- Nunca inventar números: toda medição deve vir de uma execução do simulador.
- Toda tabela do relatório deve ser reproduzível por um comando documentado.
- Preservar as regras acima ao refatorar; a calibração é o teste de regressão.
- Relatório, tabelas e justificativas em português.
