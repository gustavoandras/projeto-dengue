from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path
from time import perf_counter

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from core import cenarios
from search import ALGORITMOS
from search.resultado import validar_caminho

DESTINO = RAIZ / "resultados"
ARQUIVO_ALGORITMOS = DESTINO / "experimentos_algoritmos.csv"
ARQUIVO_USUARIO = DESTINO / "execucoes_usuario.csv"
ARQUIVO_CONSOLIDADO = DESTINO / "experimentos_completo.csv"
ARQUIVO_TABELA = DESTINO / "tabela_relatorio.md"

COLUNAS = [
    "cenario", "nome_cenario", "nivel", "dimensoes", "foco", "metodo",
    "passos", "custo", "tempo_ms", "desvio_ms",
    "expandidos", "gerados", "fronteira_maxima", "caminho",
]


def medir_tempo(buscar, grade, repeticoes: int) -> tuple[float, float]:
    amostras = []
    for _ in range(repeticoes):
        inicio = perf_counter()
        buscar(grade)
        amostras.append((perf_counter() - inicio) * 1000)
    desvio = statistics.stdev(amostras) if len(amostras) > 1 else 0.0
    return statistics.fmean(amostras), desvio


def executar_algoritmos(repeticoes: int) -> list[dict]:
    linhas = []
    for cenario in cenarios.CENARIOS:
        grade = cenario.criar_grade()
        tipo_foco = grade.tipo_do_objetivo
        print(f"\nCenário {cenario.numero} — {cenario.nome} "
              f"({cenario.nivel}, {grade.linhas}x{grade.colunas})")
        print(f"  início {grade.inicio} → foco {grade.objetivo} "
              f"({tipo_foco.nome})")

        for nome, buscar in ALGORITMOS.items():
            resultado = buscar(grade)
            if resultado.encontrou:
                validar_caminho(grade, resultado.caminho)
            media, desvio = medir_tempo(buscar, grade, repeticoes)

            linhas.append({
                "cenario": cenario.numero,
                "nome_cenario": cenario.nome,
                "nivel": cenario.nivel,
                "dimensoes": f"{grade.linhas}x{grade.colunas}",
                "foco": tipo_foco.nome,
                "metodo": nome,
                "passos": resultado.passos,
                "custo": resultado.custo,
                "tempo_ms": f"{media:.4f}",
                "desvio_ms": f"{desvio:.4f}",
                "expandidos": resultado.expandidos,
                "gerados": resultado.gerados,
                "fronteira_maxima": resultado.fronteira_maxima,
                "caminho": " ".join(f"{l},{c}" for l, c in resultado.caminho),
            })
            print(f"    {nome:<14}{resultado.passos:>4} passos "
                  f"{resultado.custo:>4} custo "
                  f"{resultado.expandidos:>5} exp "
                  f"{resultado.gerados:>5} ger "
                  f"{resultado.fronteira_maxima:>4} front "
                  f"{media:>8.4f} ms ±{desvio:.4f}")
    return linhas


def carregar_usuario() -> tuple[list[dict], list[str]]:
    if not ARQUIVO_USUARIO.exists():
        return [], []
    linhas, descartadas = [], []
    with ARQUIVO_USUARIO.open(encoding="utf-8") as arquivo:
        for registro in csv.DictReader(arquivo):
            cenario = cenarios.por_numero(int(registro["cenario"]))
            if registro.get("foco") != cenario.foco_padrao:
                descartadas.append(
                    f"cenário {cenario.numero} jogado no foco "
                    f"{registro.get('nome_foco', '?')!r}, e não no foco "
                    f"padrão dos experimentos"
                )
                continue
            grade = cenario.criar_grade()
            linhas.append({
                "cenario": int(registro["cenario"]),
                "nome_cenario": registro["nome_cenario"],
                "nivel": cenario.nivel,
                "dimensoes": f"{grade.linhas}x{grade.colunas}",
                "foco": registro.get("nome_foco", ""),
                "metodo": "Usuário",
                "passos": registro["passos"],
                "custo": registro["custo"],

                "tempo_ms": f"{float(registro['tempo_s']) * 1000:.1f}",
                "desvio_ms": "",
                "expandidos": "",
                "gerados": "",
                "fronteira_maxima": "",
                "caminho": registro["caminho"],
            })
    return linhas, descartadas


def gravar(caminho: Path, linhas: list[dict]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(linhas)


def gerar_tabela(linhas: list[dict]) -> str:
    partes = [
        "# Experimentos realizados",
        "",
        "Tempo dos algoritmos: média de repetições da busca, sem a animação.",
        "O tempo do usuário é tempo real de jogo e **não é comparável** ao ",
        "tempo de execução dos algoritmos — compare passos, custo e estados.",
        "",
    ]
    for cenario in cenarios.CENARIOS:
        do_cenario = [l for l in linhas if int(l["cenario"]) == cenario.numero]
        if not do_cenario:
            continue
        cabecalho = do_cenario[0]
        partes += [
            f"## Cenário {cenario.numero} — {cenario.nome} "
            f"({cenario.nivel}, {cabecalho['dimensoes']})",
            "",
            f"Foco: {cabecalho['foco']}",
            "",
            "| Método | Passos | Custo | Tempo | Expandidos | Gerados | "
            "Fronteira máx. |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        ordem = {"Usuário": 0, "BFS": 1, "DFS": 2, "Busca Gulosa": 3, "A*": 4}
        for linha in sorted(do_cenario, key=lambda l: ordem.get(l["metodo"], 9)):
            if linha["metodo"] == "Usuário":
                tempo = f"{float(linha['tempo_ms']) / 1000:.1f} s"
            else:
                tempo = f"{float(linha['tempo_ms']):.4f} ms"
            partes.append(
                f"| {linha['metodo']} | {linha['passos']} | {linha['custo']} "
                f"| {tempo} | {linha['expandidos'] or '—'} "
                f"| {linha['gerados'] or '—'} "
                f"| {linha['fronteira_maxima'] or '—'} |"
            )
        partes.append("")
    return "\n".join(partes)


def main() -> None:
    analisador = argparse.ArgumentParser(description=__doc__)
    analisador.add_argument("--repeticoes", type=int, default=1000,
                            help="repetições por busca para a média de tempo")
    argumentos = analisador.parse_args()

    print("=" * 74)
    print(f"EXPERIMENTOS ALGORÍTMICOS  ·  {argumentos.repeticoes} repetições "
          "por busca para a média de tempo")
    print("=" * 74)

    algoritmicas = executar_algoritmos(argumentos.repeticoes)
    gravar(ARQUIVO_ALGORITMOS, algoritmicas)

    manuais, descartadas = carregar_usuario()
    consolidado = manuais + algoritmicas
    gravar(ARQUIVO_CONSOLIDADO, consolidado)
    ARQUIVO_TABELA.write_text(gerar_tabela(consolidado), encoding="utf-8")

    print("\n" + "=" * 74)
    print(f"  {len(algoritmicas)} execuções algorítmicas  →  "
          f"{ARQUIVO_ALGORITMOS.name}")
    if manuais:
        cenarios_feitos = sorted({l["cenario"] for l in manuais})
        print(f"  {len(manuais)} execuções manuais (cenários "
              f"{cenarios_feitos})  →  {ARQUIVO_USUARIO.name}")
        faltam = [c.numero for c in cenarios.CENARIOS
                  if c.numero not in cenarios_feitos]
        if faltam:
            print(f"  ⚠  faltam as execuções manuais dos cenários {faltam}")
        else:
            print(f"  ✓ total: {len(consolidado)} execuções "
                  "(3 humanas + 12 algorítmicas)")
    else:
        print("  ⚠  nenhuma execução manual encontrada.")
        print("     Jogue o main.py uma vez em cada cenário; o resultado é")
        print(f"     gravado em {ARQUIVO_USUARIO.name} e entra aqui sozinho.")
    for aviso in descartadas:
        print(f"  ⚠  execução manual ignorada: {aviso}")
    print(f"  tabela do relatório  →  {ARQUIVO_TABELA.name}")
    print("=" * 74)


if __name__ == "__main__":
    main()
