from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import cenarios
from core.grade import Grade
from ferramentas.validar_cenarios import (
    caminho_minimo_em_custo,
    caminho_minimo_em_passos,
)
from search import ALGORITMOS


def analisar(grade: Grade, titulo: str) -> dict:
    print(f"\n{titulo}")
    print("-" * 78)

    otimo_passos = caminho_minimo_em_passos(grade)
    otimo_custo = caminho_minimo_em_custo(grade)
    if otimo_passos is None:
        print("  FOCO INALCANÇÁVEL")
        return {"valido": False}

    print(f"  {'Método':<15}{'Passos':>7}{'Custo':>7}"
          f"{'Expand.':>9}{'Gerados':>9}{'Front.máx':>11}")

    assinaturas = {}
    caminhos = {}
    for nome, buscar in ALGORITMOS.items():
        r = buscar(grade)
        print(f"  {nome:<15}{r.passos:>7}{r.custo:>7}"
              f"{r.expandidos:>9}{r.gerados:>9}{r.fronteira_maxima:>11}")
        assinaturas[nome] = (r.passos, r.custo)
        caminhos[nome] = tuple(r.caminho)

    distintos_metricas = len(set(assinaturas.values()))
    distintos_caminhos = len(set(caminhos.values()))

    passos_diferem = otimo_passos[1] > otimo_custo[1]

    print()
    print(f"  menor nº de passos : {otimo_passos[0]:>3} passos, "
          f"custo {otimo_passos[1]:>3}")
    print(f"  menor custo        : {otimo_custo[0]:>3} passos, "
          f"custo {otimo_custo[1]:>3}")
    print(f"  {'✓' if passos_diferem else '✗'} menos passos "
          f"{'!=' if passos_diferem else '=='} menor custo")
    print(f"  {'✓' if distintos_metricas == 4 else '·'} "
          f"{distintos_metricas}/4 pares (passos,custo) distintos")
    print(f"  {'✓' if distintos_caminhos == 4 else '·'} "
          f"{distintos_caminhos}/4 caminhos distintos")

    return {
        "valido": True,
        "passos_diferem": passos_diferem,
        "metricas_distintas": distintos_metricas,
        "caminhos_distintos": distintos_caminhos,
    }


def main() -> None:
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        texto = Path(sys.argv[1]).read_text(encoding="utf-8")
        analisar(Grade(texto, nome="candidato"), f"Candidato: {sys.argv[1]}")
        return

    for cenario in cenarios.CENARIOS:
        analisar(
            cenario.criar_grade(),
            f"Cenário {cenario.numero} — {cenario.nome} ({cenario.nivel})",
        )


if __name__ == "__main__":
    main()
