"""
Busca em Largura (BFS) — busca sem informação.

Ideia
-----
Explora o espaço de estados por NÍVEIS: primeiro todos os estados a 1
movimento da origem, depois todos a 2 movimentos, e assim por diante.

Estrutura de dados
------------------
FILA (FIFO), implementada com collections.deque. É a fila que garante a
ordem por níveis: o primeiro a entrar é o primeiro a sair.

Tratamento de estados visitados
-------------------------------
Um dicionário `anterior` faz dois papéis ao mesmo tempo: guarda o pai de
cada estado (para reconstruir o caminho no final) e serve como conjunto
de visitados. Um estado entra nele no momento em que é GERADO, não
quando é expandido — isso evita que o mesmo estado entre na fila duas
vezes.

Otimalidade
-----------
BFS encontra o caminho com o MENOR NÚMERO DE PASSOS. Não encontra
necessariamente o de menor CUSTO, porque ignora completamente os pesos
das arestas. O Cenário 3 foi desenhado justamente para expor essa
diferença.
"""

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
    gerados = 1                      # o estado inicial conta como gerado
    fronteira_maxima = 1
    ordem: list[Estado] = []

    while fila:
        atual = fila.popleft()
        expandidos += 1
        ordem.append(atual)

        # Teste de objetivo na EXPANSÃO, para manter o critério idêntico
        # ao dos outros três algoritmos e tornar as métricas comparáveis.
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
