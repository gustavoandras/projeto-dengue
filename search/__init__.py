from . import a_estrela, bfs, dfs, gulosa
from .resultado import Resultado


ALGORITMOS = {
    bfs.NOME: bfs.buscar,
    dfs.NOME: dfs.buscar,
    gulosa.NOME: gulosa.buscar,
    a_estrela.NOME: a_estrela.buscar,
}

NOMES = tuple(ALGORITMOS)

__all__ = ["ALGORITMOS", "NOMES", "Resultado", "bfs", "dfs", "gulosa",
           "a_estrela"]
