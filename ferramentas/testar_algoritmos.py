from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import cenarios, focos
from core.grade import Grade
from ferramentas.validar_cenarios import (
    caminho_minimo_em_custo,
    caminho_minimo_em_passos,
)
from search import ALGORITMOS, a_estrela, bfs
from search.resultado import validar_caminho


class Falha(Exception):
    pass


def _conferir(grade: Grade, rotulo: str) -> None:
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

        try:
            validar_caminho(grade, resultado.caminho)
        except ValueError as erro:
            raise Falha(f"[{rotulo}] {nome}: caminho inválido — {erro}") from None

        recalculado = grade.custo_do_caminho(resultado.caminho)
        if recalculado != resultado.custo:
            raise Falha(
                f"[{rotulo}] {nome}: custo relatado {resultado.custo} "
                f"!= recalculado {recalculado}"
            )

        if resultado.expandidos <= 0:
            raise Falha(f"[{rotulo}] {nome}: expandidos = 0")
        if resultado.gerados < resultado.expandidos:
            raise Falha(
                f"[{rotulo}] {nome}: gerados ({resultado.gerados}) < "
                f"expandidos ({resultado.expandidos})"
            )
        if resultado.fronteira_maxima <= 0:
            raise Falha(f"[{rotulo}] {nome}: fronteira máxima = 0")

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

    r_bfs = bfs.buscar(grade)
    if alcancavel and r_bfs.passos != otimo_passos[0]:
        raise Falha(
            f"[{rotulo}] BFS não achou o menor nº de passos: "
            f"{r_bfs.passos} != {otimo_passos[0]}"
        )

    r_estrela = a_estrela.buscar(grade)
    if alcancavel and r_estrela.custo != otimo_custo[1]:
        raise Falha(
            f"[{rotulo}] A* não achou o menor custo: "
            f"{r_estrela.custo} != {otimo_custo[1]}"
        )

def _mapa_aleatorio(rng: random.Random, linhas: int, colunas: int) -> str:
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

        quantidade_focos = min(rng.randint(1, 3), len(livres) - 1)
        escolhidas = rng.sample(livres, 1 + quantidade_focos)
        (li, ci), *posicoes_foco = escolhidas
        celulas[li][ci] = "S"
        for lf, cf in posicoes_foco:
            celulas[lf][cf] = rng.choice(codigos_foco)
        return "\n".join("".join(linha) for linha in celulas)

def executar() -> int:
    falhas: list[str] = []

    print("Cenários do projeto")
    print("-" * 70)
    for cenario in cenarios.CENARIOS:

        for posicao, tipo in cenario.criar_grade().focos_ordenados():
            grade = cenario.criar_grade(codigo_foco=tipo.codigo)
            rotulo = f"Cenário {cenario.numero} / {tipo.dica}"
            try:
                _conferir(grade, rotulo)
                print(f"  ✓ {rotulo} — objetivo em {posicao}")
            except Falha as erro:
                print(f"  ✗ {erro}")
                falhas.append(str(erro))

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

    print("\n" + "=" * 70)
    if falhas:
        print(f"{len(falhas)} FALHA(S)")
    else:
        print("Todos os testes passaram.")
    print("=" * 70)
    return len(falhas)

if __name__ == "__main__":
    sys.exit(1 if executar() else 0)
