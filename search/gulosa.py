"""
Busca Gulosa (Greedy Best-First Search) — busca com informação.

Função de avaliação
-------------------
    f(n) = h(n)

Ou seja, usa EXCLUSIVAMENTE a heurística. O custo já percorrido, g(n),
é completamente ignorado na escolha do próximo nó — essa é a diferença
essencial em relação ao A*.

Estrutura de dados
------------------
FILA DE PRIORIDADE (min-heap), via heapq. `heapq` é apenas uma estrutura
de dados da biblioteca padrão, não um algoritmo de busca pronto: a
política de busca (o que entra na fila, com qual prioridade, e o que
fazer ao desempilhar) está toda escrita aqui.

Critério de desempate
---------------------
Entradas da fila: (h, ordem_de_insercao, estado). Quando dois estados
têm o mesmo h, vence o que foi inserido primeiro. Sem esse contador, o
heapq tentaria comparar as tuplas de estado, e a ordem de expansão
passaria a depender das coordenadas — o que tornaria o resultado difícil
de justificar na defesa.

Tratamento de estados visitados
-------------------------------
Conjunto `visitados`, marcado na expansão. O par (estado, pai) viaja na
fila pelo mesmo motivo descrito em dfs.py: um estado pode ser alcançado
por vários vizinhos antes de ser expandido.

Otimalidade
-----------
Nenhuma. A Busca Gulosa é apenas *míope*: segue sempre o que parece mais
perto do objetivo em linha reta, e por isso costuma mergulhar de cabeça
em terreno caro quando este aponta na direção do foco. No Cenário 3 ela
tende a atravessar a faixa de terra batida em vez de contornar.

A vantagem é expandir poucos estados: normalmente é o algoritmo que
menos explora o espaço de estados, ainda que a solução saia pior.
"""

from __future__ import annotations

import heapq
from time import perf_counter

from core.grade import Estado, Grade

from .heuristica import h
from .resultado import Resultado, reconstruir_caminho

NOME = "Busca Gulosa"


def buscar(grade: Grade) -> Resultado:
    inicio_relogio = perf_counter()

    inicio = grade.inicio
    objetivo = grade.foco

    contador = 0
    fronteira: list[tuple[int, int, Estado, Estado | None]] = [
        (h(inicio, objetivo), contador, inicio, None)
    ]
    visitados: set[Estado] = set()
    anterior: dict[Estado, Estado | None] = {}

    expandidos = 0
    gerados = 1
    fronteira_maxima = 1
    ordem: list[Estado] = []

    while fronteira:
        _f, _ordem_insercao, atual, pai = heapq.heappop(fronteira)

        if atual in visitados:
            continue

        visitados.add(atual)
        anterior[atual] = pai
        expandidos += 1
        ordem.append(atual)

        if grade.eh_objetivo(atual):
            caminho = reconstruir_caminho(anterior, atual)
            return Resultado(
                algoritmo=NOME,
                encontrou=True,
                caminho=caminho,
                custo=grade.custo_do_caminho(caminho),
                expandidos=expandidos,
                gerados=gerados,
                fronteira_maxima=fronteira_maxima,
                tempo_busca=perf_counter() - inicio_relogio,
                ordem_exploracao=ordem,
            )

        for vizinho, _custo in grade.sucessores(atual):
            gerados += 1
            if vizinho not in visitados:
                contador += 1
                heapq.heappush(
                    fronteira,
                    (h(vizinho, objetivo), contador, vizinho, atual),
                )

        fronteira_maxima = max(fronteira_maxima, len(fronteira))

    return Resultado(
        algoritmo=NOME,
        encontrou=False,
        expandidos=expandidos,
        gerados=gerados,
        fronteira_maxima=fronteira_maxima,
        tempo_busca=perf_counter() - inicio_relogio,
        ordem_exploracao=ordem,
    )
