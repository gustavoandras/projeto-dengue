"""
Os três cenários do projeto (item 2.5 do edital) e os focos de dengue
espalhados em cada um (item 2.2).

Tema: um QUINTAL residencial, que é o ambiente mais intuitivo para o
público-alvo do bônus (crianças do Ensino Fundamental).

Legenda dos mapas
-----------------
    S  posição inicial da missão
    .  calçada / caminho livre ....... custo 1
    g  grama ......................... custo 2
    t  terreno de difícil acesso ..... custo 4
    #  obstáculo (muro, casa, canteiro) .. intransponível

    Focos de dengue (todos sobre calçada, custo 1):
    P  pneu               V  prato de vaso        C  caixa d'água
    R  garrafas           B  balde                L  calha

Cada cenário tem VÁRIOS focos e um deles é o padrão da missão. O jogador
escolhe qual perseguir antes de iniciar — é o "foco selecionado" a que o
edital se refere nos itens 2.3.2 e 2.4.

IMPORTANTE: as células de foco ficam sobre calçada e têm custo 1. Trocar
uma calçada por um foco NÃO altera o grafo de busca, então as métricas
validadas abaixo continuam valendo para o foco padrão de cada cenário.

ATENÇÃO — Cenário 3
-------------------
Foi desenhado para satisfazer DOIS requisitos ao mesmo tempo:

1. Item 2.5 — o caminho com MENOR NÚMERO DE PASSOS não é o de MENOR CUSTO:
     * atravessar o campo de terra: 23 passos, custo 65
     * contornar pela calçada ..... 31 passos, custo 32

2. Observações finais — "permitir comparação efetiva entre os algoritmos":
   os quatro produzem caminhos e métricas DIFERENTES entre si.

     BFS            23 passos, custo 65   (ótimo em passos, caro)
     DFS            29 passos, custo 59   (vagueia, sem garantia nenhuma)
     Busca Gulosa   25 passos, custo 55   (mergulha na terra batida)
     A*             31 passos, custo 32   (ótimo em custo)

Um corredor reto e aberto entre S e F faria BFS, DFS e Gulosa
convergirem para o mesmo caminho trivial — por isso o mapa força
curvas e oferece rotas alternativas de qualidades diferentes.

Os valores são conferidos automaticamente por:
    ferramentas/validar_cenarios.py   (requisito 1)
    ferramentas/analisar_cenario.py   (requisitos 1 e 2)
"""

from dataclasses import dataclass

from . import focos
from .grade import Grade


@dataclass(frozen=True)
class Cenario:
    numero: int
    nome: str
    nivel: str
    descricao: str
    mapa: str
    foco_padrao: str      # código do foco usado como objetivo por omissão

    def criar_grade(self, codigo_foco: str | None = None) -> Grade:
        return Grade(
            self.mapa,
            nome=f"Cenário {self.numero} — {self.nome}",
            codigo_foco_padrao=codigo_foco or self.foco_padrao,
        )

    def tipos_de_foco(self) -> list[focos.TipoFoco]:
        return [tipo for _pos, tipo in self.criar_grade().focos_ordenados()]


# ---------------------------------------------------------------------------
# Cenário 1 — Simples
#   12 x 9 · poucos obstáculos · custos predominantemente uniformes
#   Foco padrão: pneu — 14 passos, custo 14 para os quatro algoritmos
# ---------------------------------------------------------------------------
CENARIO_1 = Cenario(
    numero=1,
    nome="Quintal da casa",
    nivel="Simples",
    descricao=(
        "Mapa pequeno, poucos obstáculos e poucos caminhos alternativos. "
        "Custos quase todos iguais (só um canteiro de grama)."
    ),
    mapa="""\
############
#S.........#
#..####...V#
#..#..g....#
#..#..ggg..#
#.....gg...#
#...##....P#
#...##..B..#
############""",
    foco_padrao="P",
)

# ---------------------------------------------------------------------------
# Cenário 2 — Intermediário
#   20 x 15 · muros dividindo o quintal em setores · vários caminhos
#   Foco padrão: prato de vaso
#     BFS 29/36 · DFS 99/116 · Gulosa 35/39 · A* 29/31
#
#   Mesmas dimensões do Cenário 3, para que os três ocupem a mesma área na
#   tela. Aqui o tamanho vem de conteúdo real, não de muro de enchimento.
# ---------------------------------------------------------------------------
CENARIO_2 = Cenario(
    numero=2,
    nome="Fundos e garagem",
    nivel="Intermediário",
    descricao=(
        "Ambiente maior, com muros e canteiros dividindo o quintal em "
        "setores. Existem várias rotas possíveis até o foco."
    ),
    mapa="""\
####################
#S...gg....#......L#
#....ggggg.#.......#
#....gg#gg.#.......#
#.....g#gg....#....#
#......#......#....#
#......######.#....#
####gg........#....#
#.gggg........#..tt#
#.R...........#..tt#
#...#####.....#....#
#......#ggg#########
#...ggg#ggg...#....#
#...ggg#..........V#
####################""",
    foco_padrao="V",
)

# ---------------------------------------------------------------------------
# Cenário 3 — Complexo
#   20 x 15 · múltiplos caminhos · três tipos de terreno
#   Foco padrão: caixa d'água — ver cabeçalho do módulo
# ---------------------------------------------------------------------------
CENARIO_3 = Cenario(
    numero=3,
    nome="Terreno ao lado",
    nivel="Complexo",
    descricao=(
        "Terreno baldio ao lado da casa. Um campo de terra batida ocupa "
        "o meio: atravessá-lo é o caminho mais curto, mas o mais caro. "
        "Contornar pela calçada é mais longo e mais barato."
    ),
    mapa="""\
####################
#S.##########..##.C#
#..##########..##..#
#..######......##..#
#.tttttttttttttt..##
#.tttttttttttttt..##
#.ttttttttttttgg..##
#.......##.....g...#
#..B...........g...#
#..................#
#####..........#...#
#..gggg........#...#
#..gggg............#
#...............P..#
####################""",
    foco_padrao="C",
)


CENARIOS: tuple[Cenario, ...] = (CENARIO_1, CENARIO_2, CENARIO_3)


def por_numero(numero: int) -> Cenario:
    for c in CENARIOS:
        if c.numero == numero:
            return c
    raise ValueError(f"Cenário {numero} não existe")
