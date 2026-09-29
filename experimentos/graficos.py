"""
Gráficos dos experimentos (item 2.8: "os resultados deverão ser
apresentados por meio de tabelas e gráficos").

Lê resultados/experimentos_completo.csv e gera um PNG por métrica, em
300 dpi, prontos para entrar no relatório.

Decisões de visualização
------------------------
* Uma métrica por figura. Nunca dois eixos y no mesmo gráfico: passos e
  custo têm escalas e significados diferentes, e sobrepô-los num eixo
  duplo induz comparações falsas.
* Valor escrito em cima de cada barra. Além de facilitar a leitura, é o
  que garante que a figura continue legível impressa em preto e branco,
  já que a cor deixa de distinguir as séries.
* O tempo de busca leva barra de erro com o desvio padrão das
  repetições, para deixar explícito que é média e não medição única.
* O usuário aparece só em passos e custo. Estados expandidos, gerados e
  fronteira são conceitos internos de uma busca: quem joga não expande
  estados nem mantém fronteira.

Uso:  python -m experimentos.graficos
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ENTRADA = RAIZ / "resultados" / "experimentos_completo.csv"
DESTINO = RAIZ / "resultados" / "graficos"

# Paleta categórica validada para daltonismo e para o fundo branco.
COR = {
    "Usuário": "#e87ba4",
    "BFS": "#2a78d6",
    "DFS": "#eb6834",
    "Busca Gulosa": "#1baf7a",
    "A*": "#eda100",
}
ORDEM = ["Usuário", "BFS", "DFS", "Busca Gulosa", "A*"]

TINTA = "#0b0b0b"
TINTA_FRACA = "#52514e"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"


def carregar() -> list[dict]:
    if not ENTRADA.exists():
        raise SystemExit(
            f"{ENTRADA.name} não encontrado. "
            "Rode antes: python -m experimentos.executar"
        )
    with ENTRADA.open(encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def _numero(valor: str) -> float | None:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def grafico(linhas, coluna, titulo, rotulo_y, arquivo,
            formato="{:.0f}", desvio=None, nota=None) -> Path:
    cenarios = sorted({int(l["cenario"]) for l in linhas})
    metodos = [m for m in ORDEM
               if any(l["metodo"] == m and _numero(l[coluna]) is not None
                      for l in linhas)]
    if not metodos:
        raise ValueError(f"nenhum dado para {coluna}")

    figura, eixos = plt.subplots(figsize=(8.6, 4.4), dpi=300)
    figura.patch.set_facecolor("white")
    eixos.set_facecolor("white")

    largura = 0.8 / len(metodos)
    for indice, metodo in enumerate(metodos):
        posicoes, valores, erros = [], [], []
        for c in cenarios:
            registro = next(
                (l for l in linhas
                 if int(l["cenario"]) == c and l["metodo"] == metodo), None
            )
            valor = _numero(registro[coluna]) if registro else None
            if valor is None:
                continue
            posicoes.append(cenarios.index(c) + indice * largura)
            valores.append(valor)
            erros.append(
                _numero(registro[desvio]) or 0.0 if desvio else 0.0
            )

        barras = eixos.bar(
            posicoes, valores, largura * 0.88,
            label=metodo, color=COR[metodo],
            edgecolor="white", linewidth=1.2, zorder=3,
            yerr=erros if desvio and any(erros) else None,
            error_kw={"ecolor": TINTA_FRACA, "elinewidth": 1, "capsize": 3},
        )
        # valor em cima de cada barra: legibilidade e impressão em P&B.
        # O rótulo sobe acima da barra de erro para não se sobrepor a ela.
        for barra, valor, erro in zip(barras, valores, erros):
            eixos.annotate(
                formato.format(valor),
                (barra.get_x() + barra.get_width() / 2,
                 barra.get_height() + erro),
                textcoords="offset points", xytext=(0, 3),
                ha="center", va="bottom",
                fontsize=7.5, color=TINTA_FRACA,
            )

    eixos.set_title(titulo, fontsize=12, fontweight="bold",
                    color=TINTA, pad=12, loc="left")
    eixos.set_ylabel(rotulo_y, fontsize=9, color=TINTA_FRACA)
    eixos.set_xticks([i + 0.4 - largura / 2 for i in range(len(cenarios))])
    eixos.set_xticklabels([f"Cenário {c}" for c in cenarios],
                          fontsize=10, color=TINTA)
    eixos.tick_params(axis="y", labelsize=8, colors=TINTA_FRACA, length=0)
    eixos.tick_params(axis="x", length=0)

    eixos.yaxis.grid(True, color=GRADE, linewidth=0.8, zorder=0)
    eixos.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        eixos.spines[lado].set_visible(False)
    eixos.spines["bottom"].set_color(EIXO)

    eixos.legend(
        frameon=False, fontsize=9, labelcolor=TINTA_FRACA,
        ncols=len(metodos), loc="upper center",
        bbox_to_anchor=(0.5, -0.09),
    )

    if nota:
        figura.text(0.01, -0.02, nota, fontsize=7.5, color=TINTA_FRACA,
                    ha="left", va="top")

    DESTINO.mkdir(parents=True, exist_ok=True)
    caminho = DESTINO / arquivo
    figura.savefig(caminho, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    print(f"gerado: {caminho}")
    return caminho


def main() -> None:
    linhas = carregar()
    tem_usuario = any(l["metodo"] == "Usuário" for l in linhas)

    grafico(linhas, "passos", "Quantidade de passos até o foco",
            "passos", "passos.png")

    grafico(linhas, "custo", "Custo total do caminho",
            "custo acumulado", "custo.png")

    somente_algoritmos = [l for l in linhas if l["metodo"] != "Usuário"]

    # Os gráficos abaixo não têm a série do usuário, e isso é proposital:
    # são métricas do funcionamento interno de uma busca. A nota de rodapé
    # existe para que o leitor do relatório não interprete como dado que
    # faltou coletar.
    nota_interna = (
        "Métrica interna da busca: o usuário não expande estados nem "
        "mantém fronteira, portanto não há valor a comparar."
    )

    grafico(somente_algoritmos, "expandidos",
            "Estados expandidos", "nós retirados da fronteira",
            "estados_expandidos.png", nota=nota_interna)

    grafico(somente_algoritmos, "gerados",
            "Estados gerados", "sucessores criados",
            "estados_gerados.png", nota=nota_interna)

    grafico(somente_algoritmos, "fronteira_maxima",
            "Tamanho máximo da fronteira",
            "nós guardados simultaneamente", "fronteira_maxima.png",
            nota=nota_interna)

    grafico(somente_algoritmos, "tempo_ms",
            "Tempo de execução da busca", "milissegundos",
            "tempo_busca.png", formato="{:.3f}", desvio="desvio_ms",
            nota="Média de 1000 repetições; barras de erro = desvio padrão. "
                 "Não inclui o tempo de animação. O tempo do usuário é tempo "
                 "real de jogo (segundos) e não é comparável a esta escala.")

    print()
    if tem_usuario:
        print("Gráficos gerados com as execuções manuais incluídas.")
    else:
        print("⚠  Sem execuções manuais: passos e custo mostram só os "
              "algoritmos.")
        print("   Jogue o main.py uma vez em cada cenário e rode de novo:")
        print("   python -m experimentos.tudo")


if __name__ == "__main__":
    main()
