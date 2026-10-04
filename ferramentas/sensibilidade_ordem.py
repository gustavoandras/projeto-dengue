from __future__ import annotations

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import cenarios
from core import grade as mod_grade
from search import ALGORITMOS


def medir(cenario) -> dict:
    ordem_original = mod_grade.ACOES
    dados = {
        nome: {"passos": [], "custo": [], "caminhos": set()}
        for nome in ALGORITMOS
    }
    detalhe_dfs = []

    try:
        for permutacao in itertools.permutations(ordem_original):
            mod_grade.ACOES = permutacao
            grade = cenario.criar_grade()
            for nome, buscar in ALGORITMOS.items():
                resultado = buscar(grade)
                dados[nome]["passos"].append(resultado.passos)
                dados[nome]["custo"].append(resultado.custo)
                dados[nome]["caminhos"].add(tuple(resultado.caminho))
                if nome == "DFS":
                    detalhe_dfs.append((
                        " ".join(acao[0] for acao in permutacao),
                        resultado.passos,
                        resultado.custo,
                        permutacao == ordem_original,
                    ))
    finally:
        mod_grade.ACOES = ordem_original

    return dados, detalhe_dfs


def imprimir(cenario) -> None:
    dados, detalhe_dfs = medir(cenario)

    print(f"\nCenário {cenario.numero} — {cenario.nome}")
    print("24 permutações da ordem dos vizinhos, mapa inalterado")
    print("-" * 76)
    print(f"{'Algoritmo':<15}{'Passos':>16}{'Custo':>16}"
          f"{'Caminhos distintos':>22}")
    print("-" * 76)

    for nome, d in dados.items():
        passos, custo = d["passos"], d["custo"]
        f_passos = (f"{min(passos)} (sempre)" if min(passos) == max(passos)
                    else f"{min(passos)} – {max(passos)}")
        f_custo = (f"{min(custo)} (sempre)" if min(custo) == max(custo)
                   else f"{min(custo)} – {max(custo)}")
        print(f"{nome:<15}{f_passos:>16}{f_custo:>16}"
              f"{len(d['caminhos']):>22}")

    print()
    problemas = []
    if len(set(dados["A*"]["custo"])) != 1:
        problemas.append("A* variou de custo — otimalidade comprometida")
    if len(set(dados["BFS"]["passos"])) != 1:
        problemas.append("BFS variou de passos — fila FIFO suspeita")
    if problemas:
        for p in problemas:
            print(f"  ✗ {p}")
    else:
        print("  ✓ A* manteve o custo ótimo nas 24 ordens")
        print("  ✓ BFS manteve o menor nº de passos nas 24 ordens")

    print("\n  Detalhe da DFS (ordenado do pior para o melhor):")
    for rotulo, passos, custo, atual in sorted(
        detalhe_dfs, key=lambda t: -t[1]
    ):
        marca = "   <- ordem adotada no projeto" if atual else ""
        print(f"    {rotulo:<40}{passos:>4} passos{custo:>6} custo{marca}")


def main() -> None:
    alvos = cenarios.CENARIOS
    if len(sys.argv) > 1:
        alvos = [cenarios.por_numero(int(sys.argv[1]))]
    for cenario in alvos:
        imprimir(cenario)


if __name__ == "__main__":
    main()
