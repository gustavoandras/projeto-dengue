"""
Algoritmos de busca do projeto.

Nenhum módulo deste pacote importa pygame. A busca é pura: recebe uma
Grade, devolve um Resultado. Quem desenha é o pacote jogo/.

Isso é o que permite medir o tempo do algoritmo separadamente do tempo
de animação, como exige o item 2.4.3 do edital.
"""

from . import a_estrela, bfs, dfs, gulosa
from .resultado import Resultado

# Registro usado pela interface e pelos experimentos.
# A ordem aqui é a ordem em que os algoritmos aparecem nas tabelas.
ALGORITMOS = {
    bfs.NOME: bfs.buscar,
    dfs.NOME: dfs.buscar,
    gulosa.NOME: gulosa.buscar,
    a_estrela.NOME: a_estrela.buscar,
}

NOMES = tuple(ALGORITMOS)

__all__ = ["ALGORITMOS", "NOMES", "Resultado", "bfs", "dfs", "gulosa",
           "a_estrela"]
