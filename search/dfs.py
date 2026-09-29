"""
Busca em Profundidade (DFS) — busca sem informação.

Ideia
-----
Aprofunda um caminho até o fim antes de considerar alternativas. Só volta
atrás (backtracking) quando não há mais para onde ir.

Estrutura de dados
------------------
PILHA (LIFO), implementada com uma lista Python. O último estado a entrar
é o primeiro a sair, e é isso que produz o mergulho em profundidade.

Implementação iterativa, e não recursiva: em um grid de 20x15 a recursão
poderia atingir o limite de pilha do Python, e a versão iterativa deixa
as métricas (tamanho da fronteira) diretamente observáveis.

Ordem de expansão
-----------------
Os sucessores são empilhados na ORDEM INVERSA de ACOES. Como a pilha
devolve o último primeiro, o efeito é que o agente tenta primeiro Cima,
depois Direita, Baixo e Esquerda — a mesma ordem dos demais algoritmos.
Sem essa inversão, a DFS percorreria a vizinhança ao contrário dos
outros e a comparação ficaria injusta.

Tratamento de estados visitados
-------------------------------
DFS em GRAFO (graph search): mantém um conjunto `visitados`. Sem ele, o
agente entraria em ciclo infinito, já que o grid tem caminhos que voltam
sobre si mesmos.

Cada item da pilha guarda o par (estado, pai). O pai só é registrado no
momento em que o estado é efetivamente expandido — um mesmo estado pode
estar na pilha várias vezes, vindo de pais diferentes, e gravar o pai na
hora de empilhar produziria um caminho incoerente.

Otimalidade
-----------
Nenhuma. DFS não garante menor número de passos nem menor custo. É comum
ela devolver caminhos longos e tortuosos — exatamente o comportamento
desfavorável que a pergunta 4 do item 2.9 pede para discutir.
"""

from __future__ import annotations

from time import perf_counter

from core.grade import Estado, Grade

from .resultado import Resultado, reconstruir_caminho

NOME = "DFS"


def buscar(grade: Grade) -> Resultado:
    inicio_relogio = perf_counter()

    inicio = grade.inicio
    pilha: list[tuple[Estado, Estado | None]] = [(inicio, None)]
    visitados: set[Estado] = set()
    anterior: dict[Estado, Estado | None] = {}

    expandidos = 0
    gerados = 1
    fronteira_maxima = 1
    ordem: list[Estado] = []

    while pilha:
        atual, pai = pilha.pop()

        # O mesmo estado pode ter sido empilhado por vários vizinhos.
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

        # Empilha na ordem inversa para desempilhar na ordem de ACOES.
        for vizinho, _custo in reversed(grade.sucessores(atual)):
            gerados += 1
            if vizinho not in visitados:
                pilha.append((vizinho, atual))

        fronteira_maxima = max(fronteira_maxima, len(pilha))

    return Resultado(
        algoritmo=NOME,
        encontrou=False,
        expandidos=expandidos,
        gerados=gerados,
        fronteira_maxima=fronteira_maxima,
        tempo_busca=perf_counter() - inicio_relogio,
        ordem_exploracao=ordem,
    )
