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
