from core.celulas import CUSTO_MINIMO
from core.grade import Estado


def manhattan(origem: Estado, destino: Estado) -> int:
    return abs(origem[0] - destino[0]) + abs(origem[1] - destino[1])


def h(estado: Estado, objetivo: Estado) -> int:
    return manhattan(estado, objetivo) * CUSTO_MINIMO


DESCRICAO = f"Distância Manhattan × custo mínimo ({CUSTO_MINIMO})"
