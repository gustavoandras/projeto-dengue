"""
Função heurística usada pela Busca Gulosa e pelo A*.

Fórmula
-------
    h(n) = ManhattanDistance(n, foco) * CUSTO_MINIMO

onde ManhattanDistance((l1,c1),(l2,c2)) = |l1-l2| + |c1-c2|
e CUSTO_MINIMO é o menor custo de deslocamento existente no ambiente
(neste projeto, 1 — o custo da calçada).

Por que Manhattan
-----------------
O agente só realiza movimentos ortogonais (cima, baixo, esquerda,
direita). Não existe diagonal. Logo, o número MÍNIMO de movimentos entre
duas células, ignorando obstáculos, é exatamente a distância Manhattan.

Admissibilidade
---------------
Uma heurística é admissível quando nunca superestima o custo real
restante: h(n) <= h*(n) para todo n.

Prova para este problema:
  - qualquer caminho de n até o foco tem pelo menos Manhattan(n, foco)
    movimentos, pois cada movimento altera a soma |linha|+|coluna| em
    no máximo 1;
  - cada movimento custa no mínimo CUSTO_MINIMO, já que este é, por
    definição, o menor custo de entrada entre todas as células
    transponíveis;
  - portanto o custo real restante é >= Manhattan(n, foco) * CUSTO_MINIMO
    = h(n).
Obstáculos só podem obrigar desvios, ou seja, aumentar o custo real.
Isso reforça a desigualdade, nunca a quebra.

Consistência (monotonicidade)
-----------------------------
Uma heurística é consistente quando h(n) <= c(n, n') + h(n') para todo
sucessor n' de n.

Entre células vizinhas, a distância Manhattan até o foco muda em
exatamente 1 (para mais ou para menos), logo:
    h(n) - h(n') <= 1 * CUSTO_MINIMO <= c(n, n')
pois c(n, n') é o custo de entrar em n', que é >= CUSTO_MINIMO.

Consequência prática: com heurística consistente, o A* usando lista de
fechados encontra o caminho ótimo sem precisar reabrir nós já expandidos.
É por isso que a implementação em a_estrela.py pode descartar um nó
assim que ele sai da fronteira.

ARMADILHA a evitar
------------------
Multiplicar Manhattan pelo custo MÉDIO ou MÁXIMO do terreno (2 ou 4)
tornaria a heurística inadmissível: ela passaria a superestimar em
trechos de calçada, e o A* deixaria de garantir o menor custo.
"""

from core.celulas import CUSTO_MINIMO
from core.grade import Estado


def manhattan(origem: Estado, destino: Estado) -> int:
    """Distância Manhattan pura, em número de movimentos."""
    return abs(origem[0] - destino[0]) + abs(origem[1] - destino[1])


def h(estado: Estado, objetivo: Estado) -> int:
    """Heurística do projeto: Manhattan escalada pelo custo mínimo."""
    return manhattan(estado, objetivo) * CUSTO_MINIMO


# Nome descritivo para exibir na interface e no relatório.
DESCRICAO = f"Distância Manhattan × custo mínimo ({CUSTO_MINIMO})"
