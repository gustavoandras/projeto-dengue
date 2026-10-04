from __future__ import annotations

from collections import deque
from time import perf_counter

from core.grade import Estado, Grade

from .resultado import Resultado, reconstruir_caminho

NOME = "BFS"


def buscar(grade: Grade) -> Resultado:
    inicio_relogio = perf_counter()

    inicio = grade.inicio
    fila: deque[Estado] = deque([inicio])
    anterior: dict[Estado, Estado | None] = {inicio: None}

    expandidos = 0
    gerados = 1
    fronteira_maxima = 1
    ordem: list[Estado] = []

    while fila:
        atual = fila.popleft()
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
            if vizinho not in anterior:
                anterior[vizinho] = atual
                fila.append(vizinho)

        fronteira_maxima = max(fronteira_maxima, len(fila))

    return Resultado(
        algoritmo=NOME,
        encontrou=False,
        expandidos=expandidos,
        gerados=gerados,
        fronteira_maxima=fronteira_maxima,
        tempo_busca=perf_counter() - inicio_relogio,
        ordem_exploracao=ordem,
    )
