"""
Validação dos cenários — ferramenta de desenvolvimento.

Confere, para cada cenário:
  1. o mapa é retangular;
  2. existe exatamente um 'S' e um 'F';
  3. o foco é alcançável a partir da posição inicial;
  4. (cenário 3) o caminho de MENOR NÚMERO DE PASSOS não é o de MENOR CUSTO.

IMPORTANTE
----------
As buscas usadas aqui são apenas uma inundação (flood fill) e um Dijkstra
de conferência, escritos para VALIDAR OS MAPAS. Não são os algoritmos
entregues no projeto — esses ficam em search/ e são implementados à parte,
conforme pede o edital.

Uso:  python -m ferramentas.validar_cenarios
"""

import heapq
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import cenarios  # noqa: E402
from core.grade import Estado, Grade  # noqa: E402


def caminho_minimo_em_passos(grade: Grade) -> tuple[int, int] | None:
    """Inundação por níveis. Devolve (passos, custo desse caminho)."""
    inicio = grade.inicio
    fila = deque([inicio])
    anterior: dict[Estado, Estado | None] = {inicio: None}

    while fila:
        atual = fila.popleft()
        if grade.eh_objetivo(atual):
            caminho = []
            no: Estado | None = atual
            while no is not None:
                caminho.append(no)
                no = anterior[no]
            caminho.reverse()
            return len(caminho) - 1, grade.custo_do_caminho(caminho)
        for vizinho, _c in grade.sucessores(atual):
            if vizinho not in anterior:
                anterior[vizinho] = atual
                fila.append(vizinho)
    return None


def caminho_minimo_em_custo(grade: Grade) -> tuple[int, int] | None:
    """Dijkstra de conferência. Devolve (passos, custo)."""
    inicio = grade.inicio
    melhor: dict[Estado, int] = {inicio: 0}
    anterior: dict[Estado, Estado | None] = {inicio: None}
    fila = [(0, 0, inicio)]
    contador = 1

    while fila:
        custo, _ordem, atual = heapq.heappop(fila)
        if custo > melhor.get(atual, float("inf")):
            continue
        if grade.eh_objetivo(atual):
            caminho = []
            no: Estado | None = atual
            while no is not None:
                caminho.append(no)
                no = anterior[no]
            return len(caminho) - 1, custo
        for vizinho, passo in grade.sucessores(atual):
            novo = custo + passo
            if novo < melhor.get(vizinho, float("inf")):
                melhor[vizinho] = novo
                anterior[vizinho] = atual
                heapq.heappush(fila, (novo, contador, vizinho))
                contador += 1
    return None


def validar() -> int:
    falhas = 0

    for cenario in cenarios.CENARIOS:
        print(f"\n{'=' * 64}")
        print(f"Cenário {cenario.numero} — {cenario.nome} ({cenario.nivel})")
        print("=" * 64)

        try:
            grade = cenario.criar_grade()
        except ValueError as erro:
            print(f"  ✗ MAPA INVÁLIDO: {erro}")
            falhas += 1
            continue

        livres = len(grade.estados_validos())
        total = grade.linhas * grade.colunas
        print(f"  ✓ retangular: {grade.linhas} linhas x {grade.colunas} colunas")
        print(f"  ✓ início {grade.inicio}   foco {grade.foco}")
        print(f"  · células transponíveis: {livres}/{total} "
              f"({100 * livres / total:.0f}%)")

        por_passos = caminho_minimo_em_passos(grade)
        por_custo = caminho_minimo_em_custo(grade)

        if por_passos is None or por_custo is None:
            print("  ✗ FOCO INALCANÇÁVEL a partir da posição inicial")
            falhas += 1
            continue

        p_passos, c_passos = por_passos
        p_custo, c_custo = por_custo
        print(f"  ✓ foco alcançável")
        print(f"  · menor nº de passos : {p_passos:>3} passos, custo {c_passos:>3}")
        print(f"  · menor custo        : {p_custo:>3} passos, custo {c_custo:>3}")

        if cenario.numero == 3:
            if c_passos > c_custo and p_custo > p_passos:
                print(f"  ✓ REQUISITO 2.5: menos passos != menor custo "
                      f"({c_passos} vs {c_custo})")
            else:
                print("  ✗ REQUISITO 2.5 NÃO ATENDIDO: o caminho mais curto "
                      "também é o mais barato")
                falhas += 1

    print(f"\n{'=' * 64}")
    if falhas:
        print(f"{falhas} problema(s) encontrado(s).")
    else:
        print("Todos os cenários passaram.")
    print("=" * 64)
    return falhas


if __name__ == "__main__":
    sys.exit(1 if validar() else 0)
