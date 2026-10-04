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
