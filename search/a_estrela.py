"""
A* (A estrela) — busca com informação.

Função de avaliação
-------------------
    f(n) = g(n) + h(n)

    g(n)  custo acumulado desde o estado inicial até n
    h(n)  estimativa do custo restante de n até o foco
          (ver heuristica.py: Manhattan x custo mínimo)

É a combinação das duas parcelas que diferencia o A* da Busca Gulosa
(que usa só h) e da Busca de Custo Uniforme (que usaria só g).

Estrutura de dados
------------------
FILA DE PRIORIDADE (min-heap) via heapq, ordenada por f. Um dicionário
`melhor_g` guarda o menor custo conhecido para chegar a cada estado.

Critério de desempate
---------------------
Entradas: (f, h, ordem_de_insercao, estado, pai).
  1. menor f;
  2. em caso de empate, menor h — prefere nós mais próximos do objetivo,
     o que costuma reduzir o número de expansões sem afetar a otimalidade;
  3. persistindo o empate, o inserido primeiro.

Lista de fechados
-----------------
O conjunto `visitados` guarda os nós já expandidos. Com heurística
CONSISTENTE — e a nossa é, ver a prova em heuristica.py — o A* expande
cada nó já com seu g ótimo. Por isso um nó pode ser descartado
definitivamente ao ser expandido, sem risco de precisar ser reaberto.

Entradas obsoletas
------------------
Não existe operação de "diminuir prioridade" no heapq. Quando um caminho
melhor até um estado é descoberto, uma nova entrada é empilhada e a
antiga fica obsoleta. Ela é simplesmente ignorada ao ser desempilhada,
pelo teste `atual in visitados`. Isso é padrão e não afeta a corretude.

Otimalidade
-----------
Com heurística admissível, o A* garante o caminho de MENOR CUSTO. E,
sendo a heurística também consistente, ele é ótimo em eficiência: nenhum
outro algoritmo com a mesma informação expande menos nós.

No Cenário 3 o A* deve contornar pela calçada (41 passos, custo 41) em
vez de atravessar a terra batida (17 passos, custo 53).
"""

from __future__ import annotations

import heapq
from time import perf_counter

from core.grade import Estado, Grade

from .heuristica import h
from .resultado import Resultado, reconstruir_caminho

NOME = "A*"


def buscar(grade: Grade) -> Resultado:
    inicio_relogio = perf_counter()

    inicio = grade.inicio
    objetivo = grade.foco

    contador = 0
    h_inicial = h(inicio, objetivo)
    fronteira: list[tuple[int, int, int, Estado, Estado | None]] = [
        (h_inicial, h_inicial, contador, inicio, None)
    ]
    melhor_g: dict[Estado, int] = {inicio: 0}
    visitados: set[Estado] = set()
    anterior: dict[Estado, Estado | None] = {}

    expandidos = 0
    gerados = 1
    fronteira_maxima = 1
    ordem: list[Estado] = []

    while fronteira:
        f_atual, _h_atual, _ins, atual, pai = heapq.heappop(fronteira)

        # Entrada obsoleta: este estado já foi expandido com g melhor.
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

        g_atual = melhor_g[atual]

        for vizinho, custo_entrada in grade.sucessores(atual):
            gerados += 1
            if vizinho in visitados:
                continue

            novo_g = g_atual + custo_entrada
            if novo_g < melhor_g.get(vizinho, float("inf")):
                melhor_g[vizinho] = novo_g
                h_vizinho = h(vizinho, objetivo)
                contador += 1
                heapq.heappush(
                    fronteira,
                    (novo_g + h_vizinho, h_vizinho, contador, vizinho, atual),
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
