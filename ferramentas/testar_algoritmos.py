"""
Testes de corretude dos quatro algoritmos.

Verifica, em todos os cenários e também em centenas de mapas aleatórios:

  1. todo caminho devolvido é realmente percorrível (sem saltos, sem
     atravessar obstáculo, começando na origem e terminando no foco);
  2. o custo relatado bate com a soma recalculada do caminho;
  3. BFS devolve o menor NÚMERO DE PASSOS possível;
  4. A* devolve o menor CUSTO possível (conferido contra um Dijkstra
     de referência, independente da implementação testada);
  5. as métricas são coerentes (gerados >= expandidos > 0).

Uso:  python -m ferramentas.testar_algoritmos
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import cenarios, focos  # noqa: E402
from core.grade import Grade  # noqa: E402
from ferramentas.validar_cenarios import (  # noqa: E402
    caminho_minimo_em_custo,
    caminho_minimo_em_passos,
)
from search import ALGORITMOS, a_estrela, bfs  # noqa: E402
from search.resultado import validar_caminho  # noqa: E402


class Falha(Exception):
    pass


def _conferir(grade: Grade, rotulo: str) -> None:
    """Roda os 4 algoritmos numa grade e aplica todas as verificações."""
    otimo_passos = caminho_minimo_em_passos(grade)
    otimo_custo = caminho_minimo_em_custo(grade)
    alcancavel = otimo_passos is not None

    for nome, buscar in ALGORITMOS.items():
        resultado = buscar(grade)

        if resultado.encontrou != alcancavel:
            raise Falha(
                f"[{rotulo}] {nome}: encontrou={resultado.encontrou}, "
                f"mas o foco {'é' if alcancavel else 'não é'} alcançável"
            )

        if not alcancavel:
            continue

        # 1. caminho percorrível
        try:
            validar_caminho(grade, resultado.caminho)
        except ValueError as erro:
            raise Falha(f"[{rotulo}] {nome}: caminho inválido — {erro}") from None

        # 2. custo relatado confere com o recalculado
        recalculado = grade.custo_do_caminho(resultado.caminho)
        if recalculado != resultado.custo:
            raise Falha(
                f"[{rotulo}] {nome}: custo relatado {resultado.custo} "
                f"!= recalculado {recalculado}"
            )

        # 5. métricas coerentes
        if resultado.expandidos <= 0:
            raise Falha(f"[{rotulo}] {nome}: expandidos = 0")
        if resultado.gerados < resultado.expandidos:
            raise Falha(
                f"[{rotulo}] {nome}: gerados ({resultado.gerados}) < "
                f"expandidos ({resultado.expandidos})"
            )
        if resultado.fronteira_maxima <= 0:
            raise Falha(f"[{rotulo}] {nome}: fronteira máxima = 0")

        # nenhum algoritmo pode ser melhor que o ótimo
        if resultado.passos < otimo_passos[0]:
            raise Falha(
                f"[{rotulo}] {nome}: {resultado.passos} passos é MENOR que o "
                f"ótimo {otimo_passos[0]} — impossível"
            )
        if resultado.custo < otimo_custo[1]:
            raise Falha(
                f"[{rotulo}] {nome}: custo {resultado.custo} é MENOR que o "
                f"ótimo {otimo_custo[1]} — impossível"
            )

    # 3. BFS é ótimo em passos
    r_bfs = bfs.buscar(grade)
    if alcancavel and r_bfs.passos != otimo_passos[0]:
        raise Falha(
            f"[{rotulo}] BFS não achou o menor nº de passos: "
            f"{r_bfs.passos} != {otimo_passos[0]}"
        )

    # 4. A* é ótimo em custo
    r_estrela = a_estrela.buscar(grade)
    if alcancavel and r_estrela.custo != otimo_custo[1]:
        raise Falha(
            f"[{rotulo}] A* não achou o menor custo: "
            f"{r_estrela.custo} != {otimo_custo[1]}"
        )


def _mapa_aleatorio(rng: random.Random, linhas: int, colunas: int) -> str:
    """Gera um mapa aleatório com início, focos e mistura de terrenos."""
    codigos_foco = sorted(focos.POR_CODIGO)
    while True:
        celulas = []
        for _ in range(linhas):
            linha = []
            for _ in range(colunas):
                linha.append(rng.choices(".gt#", weights=[45, 20, 15, 20])[0])
            celulas.append(linha)

        livres = [
            (l, c)
            for l in range(linhas)
            for c in range(colunas)
            if celulas[l][c] != "#"
        ]
        if len(livres) < 2:
            continue
        # um início e de 1 a 3 focos, para exercitar também a seleção
        quantidade_focos = min(rng.randint(1, 3), len(livres) - 1)
        escolhidas = rng.sample(livres, 1 + quantidade_focos)
        (li, ci), *posicoes_foco = escolhidas
        celulas[li][ci] = "S"
        for lf, cf in posicoes_foco:
            celulas[lf][cf] = rng.choice(codigos_foco)
        return "\n".join("".join(linha) for linha in celulas)


def executar() -> int:
    falhas: list[str] = []

    # --- cenários do projeto ---------------------------------------------
    print("Cenários do projeto")
    print("-" * 70)
    for cenario in cenarios.CENARIOS:
        # testa TODOS os focos de cada cenário, não só o padrão
        for posicao, tipo in cenario.criar_grade().focos_ordenados():
            grade = cenario.criar_grade(codigo_foco=tipo.codigo)
            rotulo = f"Cenário {cenario.numero} / {tipo.dica}"
            try:
                _conferir(grade, rotulo)
                print(f"  ✓ {rotulo} — objetivo em {posicao}")
            except Falha as erro:
                print(f"  ✗ {erro}")
                falhas.append(str(erro))

    # --- mapas aleatórios -------------------------------------------------
    print("\nMapas aleatórios (incluindo casos sem solução)")
    print("-" * 70)
    rng = random.Random(20260929)
    total = 400
    testados = 0
    sem_solucao = 0
    for i in range(total):
        linhas = rng.randint(3, 14)
        colunas = rng.randint(3, 14)
        texto = _mapa_aleatorio(rng, linhas, colunas)
        try:
            grade = Grade(texto, nome=f"rnd{i}")
        except ValueError as erro:
            # um mapa descartado em silêncio tornaria o teste vazio
            falhas.append(f"mapa aleatório #{i} não pôde ser lido: {erro}")
            print(f"  ✗ mapa aleatório #{i} inválido: {erro}")
            continue
        testados += 1
        if caminho_minimo_em_passos(grade) is None:
            sem_solucao += 1
        try:
            _conferir(grade, f"aleatório #{i} ({linhas}x{colunas})")
        except Falha as erro:
            print(f"  ✗ {erro}")
            falhas.append(str(erro))

    if testados != total:
        falhas.append(f"só {testados} de {total} mapas aleatórios foram testados")
    print(f"  {'✓' if testados == total else '✗'} {testados}/{total} mapas "
          f"testados ({sem_solucao} deles sem caminho até o foco)")

    # --- resumo -----------------------------------------------------------
    print("\n" + "=" * 70)
    if falhas:
        print(f"{len(falhas)} FALHA(S)")
    else:
        print("Todos os testes passaram.")
    print("=" * 70)
    return len(falhas)


if __name__ == "__main__":
    sys.exit(1 if executar() else 0)
