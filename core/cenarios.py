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
    foco_padrao: str

    def criar_grade(self, codigo_foco: str | None = None) -> Grade:
        return Grade(
            self.mapa,
            nome=f"Cenário {self.numero} — {self.nome}",
            codigo_foco_padrao=codigo_foco or self.foco_padrao,
        )

    def tipos_de_foco(self) -> list[focos.TipoFoco]:
        return [tipo for _pos, tipo in self.criar_grade().focos_ordenados()]


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
