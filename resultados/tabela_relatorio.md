# Experimentos realizados

Tempo dos algoritmos: média de repetições da busca, sem a animação.
O tempo do usuário é tempo real de jogo e **não é comparável** ao 
tempo de execução dos algoritmos — compare passos, custo e estados.

## Cenário 1 — Quintal da casa (Simples, 9x12)

Foco: Pneu com água acumulada

| Método | Passos | Custo | Tempo | Expandidos | Gerados | Fronteira máx. |
|---|---:|---:|---:|---:|---:|---:|
| Usuário | 14 | 16 | 8.3 s | — | — | — |
| BFS | 14 | 14 | 0.1259 ms | 58 | 181 | 9 |
| DFS | 14 | 14 | 0.0351 ms | 15 | 37 | 10 |
| Busca Gulosa | 14 | 14 | 0.0416 ms | 15 | 37 | 10 |
| A* | 14 | 14 | 0.0461 ms | 15 | 37 | 9 |

## Cenário 2 — Fundos e garagem (Intermediário, 15x20)

Foco: Prato de vaso de planta com água

| Método | Passos | Custo | Tempo | Expandidos | Gerados | Fronteira máx. |
|---|---:|---:|---:|---:|---:|---:|
| Usuário | 29 | 32 | 9.4 s | — | — | — |
| BFS | 29 | 36 | 0.4432 ms | 194 | 635 | 14 |
| DFS | 99 | 116 | 0.2450 ms | 101 | 323 | 77 |
| Busca Gulosa | 35 | 39 | 0.1199 ms | 39 | 116 | 35 |
| A* | 29 | 31 | 0.2844 ms | 76 | 255 | 42 |

## Cenário 3 — Terreno ao lado (Complexo, 15x20)

Foco: Caixa d'água destampada

| Método | Passos | Custo | Tempo | Expandidos | Gerados | Fronteira máx. |
|---|---:|---:|---:|---:|---:|---:|
| Usuário | 31 | 33 | 8.4 s | — | — | — |
| BFS | 23 | 65 | 0.3779 ms | 165 | 582 | 16 |
| DFS | 29 | 59 | 0.0774 ms | 30 | 86 | 27 |
| Busca Gulosa | 25 | 55 | 0.1007 ms | 32 | 92 | 24 |
| A* | 31 | 32 | 0.2033 ms | 51 | 177 | 40 |
