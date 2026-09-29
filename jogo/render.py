"""
Renderização do ambiente em Pygame, em estilo PIXEL ART.

Tudo aqui é apenas DESENHO. Nenhum algoritmo de busca passa por este
módulo — essa separação é o que permite medir o tempo do algoritmo
separadamente do tempo da animação (item 2.4.3 do edital).

Como o pixel art é feito
------------------------
Cada célula é desenhada numa grade lógica de 12x12 "pixels grandes" e
depois ampliada por um fator INTEIRO. É o fator inteiro que garante
pixels perfeitamente quadrados: ampliar 12 px por 2,4x deixaria umas
colunas com 2 px e outras com 3, e o resultado ficaria irregular.

Por isso `definir_area` não usa o tamanho de célula bruto que caberia na
tela: ele arredonda para baixo até o múltiplo de 12 mais próximo.

Nada é carregado de arquivo. Os sprites são mapas de caracteres
declarados no fim do módulo, o que os deixa fáceis de editar: cada
caractere é um pixel e a paleta diz qual cor ele representa.
"""

from __future__ import annotations

import pygame

from core import celulas
from core.grade import Estado, Grade

from . import tema

# Lado da grade lógica de cada célula, em pixels de arte.
TAM_LOGICO = 12

# Cache de superfícies já construídas: evita redesenhar pixel a pixel
# a cada quadro. A chave inclui a escala, porque redimensionar a janela
# exige sprites novos.
_CACHE: dict[tuple, pygame.Surface] = {}


def _ruido(linha: int, coluna: int, semente: int = 0) -> int:
    """Pseudo-aleatório determinístico: mesma célula, mesma variação."""
    valor = (linha * 73_856_093) ^ (coluna * 19_349_663) ^ (semente * 83_492_791)
    return (valor >> 8) & 0xFFFF


def _ampliar(superficie: pygame.Surface, escala: int) -> pygame.Surface:
    """Amplia por fator inteiro sem suavizar — pixels continuam quadrados."""
    if escala == 1:
        return superficie
    return pygame.transform.scale(
        superficie,
        (superficie.get_width() * escala, superficie.get_height() * escala),
    )


def _montar_sprite(mapa: tuple[str, ...], paleta: dict[str, tuple]) -> pygame.Surface:
    """Constrói uma superfície 12x12 a partir de um mapa de caracteres."""
    superficie = pygame.Surface((TAM_LOGICO, TAM_LOGICO), pygame.SRCALPHA)
    for y, linha in enumerate(mapa):
        for x, caractere in enumerate(linha):
            cor = paleta.get(caractere)
            if cor is not None:
                superficie.set_at((x, y), cor)
    return superficie


def _sprite(chave: tuple, mapa, paleta, escala: int) -> pygame.Surface:
    completa = (*chave, escala)
    if completa not in _CACHE:
        _CACHE[completa] = _ampliar(_montar_sprite(mapa, paleta), escala)
    return _CACHE[completa]


# ---------------------------------------------------------------------------
# Tiles de terreno
# ---------------------------------------------------------------------------

def _tile_terreno(codigo: str, variante: int) -> pygame.Surface:
    """Desenha o tile 12x12 de um tipo de terreno, com pequena variação."""
    superficie = pygame.Surface((TAM_LOGICO, TAM_LOGICO))
    base = tema.cor_terreno(codigo)
    superficie.fill(base)

    if codigo == celulas.OBSTACULO.codigo:
        _pixels_muro(superficie, variante)
    elif codigo == celulas.GRAMA.codigo:
        _pixels_grama(superficie, variante)
    elif codigo == celulas.TERRA.codigo:
        _pixels_terra(superficie, variante)
    else:
        _pixels_calcada(superficie, variante)

    return superficie


def _pixels_calcada(superficie, variante) -> None:
    """Lajota clara com rejunte nas bordas e algumas manchas."""
    rejunte = (178, 182, 190)
    for i in range(TAM_LOGICO):
        superficie.set_at((i, TAM_LOGICO - 1), rejunte)
        superficie.set_at((TAM_LOGICO - 1, i), rejunte)
    mancha = (192, 196, 203)
    manchas = (
        ((3, 4), (7, 2), (5, 8)),
        ((2, 7), (8, 5), (6, 3)),
        ((4, 2), (9, 8), (3, 9)),
        ((6, 6), (2, 3), (8, 9)),
    )[variante % 4]
    for x, y in manchas:
        superficie.set_at((x, y), mancha)


def _pixels_grama(superficie, variante) -> None:
    """Tufos de capim: traços verticais escuros e claros."""
    escuro = (74, 138, 60)
    claro = (138, 202, 112)
    tufos = (
        ((2, 3), (6, 1), (9, 5), (4, 8)),
        ((1, 6), (5, 2), (8, 7), (10, 3)),
        ((3, 7), (7, 4), (10, 9), (1, 1)),
        ((5, 5), (9, 2), (2, 9), (7, 8)),
    )[variante % 4]
    for x, y in tufos:
        for dy in range(3):
            if y + dy < TAM_LOGICO:
                superficie.set_at((x, y + dy), escuro)
        if x + 1 < TAM_LOGICO and y + 1 < TAM_LOGICO:
            superficie.set_at((x + 1, y + 1), claro)


def _pixels_terra(superficie, variante) -> None:
    """Terra batida: pedrinhas escuras e poeira clara."""
    pedra = (132, 90, 54)
    poeira = (196, 152, 108)
    grupos = (
        (((2, 2), (7, 5), (4, 9)), ((9, 3), (5, 7))),
        (((5, 1), (1, 6), (8, 8)), ((3, 4), (10, 6))),
        (((8, 2), (3, 6), (6, 10)), ((1, 9), (7, 3))),
        (((4, 4), (9, 7), (2, 10)), ((6, 6), (10, 2))),
    )[variante % 4]
    for x, y in grupos[0]:
        superficie.set_at((x, y), pedra)
        if x + 1 < TAM_LOGICO:
            superficie.set_at((x + 1, y), pedra)
    for x, y in grupos[1]:
        superficie.set_at((x, y), poeira)


def _pixels_muro(superficie, variante) -> None:
    """Tijolos aparentes: argamassa horizontal e juntas alternadas."""
    argamassa = (40, 34, 31)
    realce = (74, 64, 58)
    for y in (0, 6):
        for x in range(TAM_LOGICO):
            superficie.set_at((x, y), argamassa)
    deslocamento = 0 if variante % 2 == 0 else 6
    for y in range(1, 6):
        superficie.set_at((deslocamento % TAM_LOGICO, y), argamassa)
    for y in range(7, TAM_LOGICO):
        superficie.set_at(((deslocamento + 6) % TAM_LOGICO, y), argamassa)
    for x in range(TAM_LOGICO):
        superficie.set_at((x, 1), realce)
        superficie.set_at((x, 7), realce)


# ---------------------------------------------------------------------------
# Desenhista
# ---------------------------------------------------------------------------

class DesenhistaGrade:
    """Desenha uma grade dentro de um retângulo da tela."""

    def __init__(self, grade: Grade, retangulo: pygame.Rect):
        self.grade = grade
        self.definir_area(retangulo)

    def definir_area(self, retangulo: pygame.Rect) -> None:
        """
        Calcula o tamanho da célula para a grade caber na área dada.

        O tamanho é arredondado para um MÚLTIPLO de TAM_LOGICO, para que
        a ampliação dos sprites use fator inteiro e os pixels da arte
        fiquem quadrados.
        """
        bruto = min(
            retangulo.width // self.grade.colunas,
            retangulo.height // self.grade.linhas,
        )
        self.escala = max(1, bruto // TAM_LOGICO)
        self.lado = self.escala * TAM_LOGICO

        largura = self.lado * self.grade.colunas
        altura = self.lado * self.grade.linhas
        self.origem_x = retangulo.x + (retangulo.width - largura) // 2
        self.origem_y = retangulo.y + (retangulo.height - altura) // 2
        self.rect = pygame.Rect(self.origem_x, self.origem_y, largura, altura)

    # -- conversões --------------------------------------------------------

    def retangulo_da_celula(self, linha: int, coluna: int) -> pygame.Rect:
        return pygame.Rect(
            self.origem_x + coluna * self.lado,
            self.origem_y + linha * self.lado,
            self.lado, self.lado,
        )

    def centro_da_celula(self, linha: int, coluna: int) -> tuple[int, int]:
        r = self.retangulo_da_celula(linha, coluna)
        return r.centerx, r.centery

    def celula_em(self, posicao) -> Estado | None:
        """Converte uma coordenada de tela em (linha, coluna), se houver."""
        x, y = posicao
        if not self.rect.collidepoint(posicao):
            return None
        return ((y - self.origem_y) // self.lado,
                (x - self.origem_x) // self.lado)

    # -- terreno -----------------------------------------------------------

    def desenhar_terreno(self, tela: pygame.Surface) -> None:
        for linha in range(self.grade.linhas):
            for coluna in range(self.grade.colunas):
                codigo = self.grade.matriz[linha][coluna].codigo
                # focos e início ficam sobre calçada
                if codigo not in tema.COR_DETALHE:
                    codigo = celulas.CALCADA.codigo
                variante = _ruido(linha, coluna) % 4
                chave = ("terreno", codigo, variante)
                if (*chave, self.escala) not in _CACHE:
                    _CACHE[(*chave, self.escala)] = _ampliar(
                        _tile_terreno(codigo, variante), self.escala
                    )
                tela.blit(
                    _CACHE[(*chave, self.escala)],
                    self.retangulo_da_celula(linha, coluna).topleft,
                )

        pygame.draw.rect(tela, tema.BORDA_PAINEL, self.rect, width=2)

    # -- sobreposições -----------------------------------------------------

    def desenhar_sobreposicao(self, tela, estados, cor_rgba) -> None:
        """Pinta um conjunto de células com cor semitransparente."""
        if not estados:
            return
        camada = pygame.Surface((self.lado, self.lado), pygame.SRCALPHA)
        camada.fill(cor_rgba)
        for linha, coluna in estados:
            tela.blit(camada, self.retangulo_da_celula(linha, coluna).topleft)

    def desenhar_trilha(self, tela, estados, cor_rgba, espessura=0.34) -> None:
        """
        Liga células consecutivas com blocos retangulares.

        Retângulos em vez de linhas: como os movimentos são sempre
        ortogonais, os blocos ficam alinhados à grade de pixels e o
        caminho continua parecendo pixel art.
        """
        if len(estados) < 2:
            return
        grossura = max(2, int(self.lado * espessura))
        grossura -= grossura % max(1, self.escala)   # múltiplo da escala
        camada = pygame.Surface((self.rect.width, self.rect.height),
                                pygame.SRCALPHA)

        def bloco(linha, coluna):
            centro_x = coluna * self.lado + self.lado // 2
            centro_y = linha * self.lado + self.lado // 2
            return centro_x, centro_y

        for anterior, atual in zip(estados, estados[1:]):
            x1, y1 = bloco(*anterior)
            x2, y2 = bloco(*atual)
            rect = pygame.Rect(
                min(x1, x2) - grossura // 2, min(y1, y2) - grossura // 2,
                abs(x2 - x1) + grossura, abs(y2 - y1) + grossura,
            )
            pygame.draw.rect(camada, cor_rgba, rect)

        tela.blit(camada, self.rect.topleft)

    # -- marcadores --------------------------------------------------------

    def desenhar_inicio(self, tela) -> None:
        """Marca discreta de onde a missão começa."""
        linha, coluna = self.grade.inicio
        sprite = _sprite(
            ("inicio",), SPRITE_INICIO,
            {"m": tema.COR_MARCA_INICIO}, self.escala,
        )
        tela.blit(sprite, self.retangulo_da_celula(linha, coluna).topleft)

    def desenhar_focos(self, tela, pulso: float,
                       realcar_selecao: bool = True) -> None:
        """Desenha todos os focos; o selecionado ganha halo pulsante."""
        for posicao, tipo in self.grade.focos_ordenados():
            selecionado = (posicao == self.grade.objetivo) and realcar_selecao
            self._desenhar_foco(tela, posicao, tipo.codigo, selecionado, pulso)

    def _desenhar_foco(self, tela, posicao, codigo, selecionado, pulso) -> None:
        linha, coluna = posicao
        rect = self.retangulo_da_celula(linha, coluna)

        if selecionado:
            lado = self.lado
            halo = pygame.Surface((lado * 2, lado * 2), pygame.SRCALPHA)
            passo = max(2, self.escala)
            raio = int(lado * (0.40 + 0.14 * pulso) / passo) * passo
            pygame.draw.rect(
                halo, (*tema.COR_FOCO, int(50 + 50 * pulso)),
                pygame.Rect(lado - raio, lado - raio, raio * 2, raio * 2),
            )
            tela.blit(halo, (rect.centerx - lado, rect.centery - lado))

        paleta = PALETAS_FOCO["ativo" if selecionado else "inativo"]
        mapa = SPRITES_FOCO.get(codigo, SPRITES_FOCO["C"])
        sprite = _sprite(
            ("foco", codigo, selecionado), mapa, paleta, self.escala
        )
        tela.blit(sprite, rect.topleft)

    def desenhar_personagem(self, tela, linha, coluna, papel: str) -> None:
        """`papel` é "usuario" (pessoa) ou "agente" (robô)."""
        mapa, paleta = SPRITES_PERSONAGEM[papel]
        sprite = _sprite(("personagem", papel), mapa, paleta, self.escala)
        tela.blit(sprite, self.retangulo_da_celula(linha, coluna).topleft)


# ---------------------------------------------------------------------------
# Sprites — cada caractere é um pixel; '.' é transparente
# ---------------------------------------------------------------------------

# Marca do ponto de partida: quatro cantos, sem tapar o personagem.
SPRITE_INICIO = (
    "............",
    ".mm......mm.",
    ".m........m.",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    ".m........m.",
    ".mm......mm.",
    "............",
)

# Usuário: uma pessoa (agente de saúde de camiseta azul).
SPRITE_USUARIO = (
    "....hhhh....",
    "...hhhhhh...",
    "...hssssh...",
    "...ssssss...",
    "...soosoos..",
    "...ssssss...",
    "....smms....",
    "..bbbbbbbb..",
    ".bbbbbbbbbb.",
    ".bsbbbbbbsb.",
    "..dd....dd..",
    "..ddd..ddd..",
)

# Agente inteligente: um robozinho, para contrastar com a pessoa.
SPRITE_AGENTE = (
    ".....aa.....",
    ".....aa.....",
    "...rrrrrr...",
    "..rrrrrrrr..",
    "..rwwrrwwr..",
    "..rwwrrwwr..",
    "..rrrrrrrr..",
    "...rrmmrr...",
    "..rrrrrrrr..",
    ".rrrrrrrrrr.",
    "..rr....rr..",
    "..gg....gg..",
)

SPRITES_PERSONAGEM = {
    "usuario": (SPRITE_USUARIO, {
        "h": (92, 62, 40),       # cabelo
        "s": (232, 190, 152),    # pele
        "o": (40, 40, 52),       # olhos
        "m": (150, 90, 80),      # boca
        "b": tema.COR_USUARIO,   # camiseta
        "d": (46, 62, 96),       # calça
    }),
    "agente": (SPRITE_AGENTE, {
        "a": (168, 176, 190),    # antena
        "r": tema.COR_AGENTE,    # corpo
        "w": (226, 242, 255),    # visor
        "m": (110, 30, 28),      # boca
        "g": (120, 126, 138),    # pés
    }),
}

SPRITES_FOCO = {
    # Pneu: anel escuro com água empoçada no meio.
    "P": (
        "............",
        "...dddddd...",
        "..dddddddd..",
        ".dddddddddd.",
        ".dddwwwwddd.",
        ".ddwwwwwwdd.",
        ".ddwwwwwwdd.",
        ".dddwwwwddd.",
        ".dddddddddd.",
        "..dddddddd..",
        "...dddddd...",
        "............",
    ),
    # Vaso de planta sobre pratinho com água.
    "V": (
        "............",
        "............",
        "..tttttttt..",
        "..tttttttt..",
        "...tttttt...",
        "...tttttt...",
        "....tttt....",
        "....tttt....",
        "..wwwwwwww..",
        "..wwwwwwww..",
        "............",
        "............",
    ),
    # Caixa d'água ABERTA: sem tampa, água à mostra.
    "C": (
        "............",
        "...cccccc...",
        "..cwwwwwwc..",
        "..cwwwwwwc..",
        "..cwwwwwwc..",
        "..cwwwwwwc..",
        "..cwwwwwwc..",
        "..cwwwwwwc..",
        "..cwwwwwwc..",
        "..cccccccc..",
        "............",
        "............",
    ),
    # Garrafa de boca para cima.
    "R": (
        "............",
        ".....cc.....",
        ".....cc.....",
        "....cccc....",
        "...wwwwww...",
        "...wwwwww...",
        "...wwwwww...",
        "...wwwwww...",
        "...wwwwww...",
        "...cccccc...",
        "............",
        "............",
    ),
    # Balde virado para cima, mais estreito embaixo.
    "B": (
        "............",
        "............",
        "............",
        "..cccccccc..",
        "..cwwwwwwc..",
        "..cwwwwwwc..",
        "...cwwwwc...",
        "...cwwwwc...",
        "....cccc....",
        "............",
        "............",
        "............",
    ),
    # Calha horizontal entupida.
    "L": (
        "............",
        "............",
        "............",
        "............",
        ".cccccccccc.",
        ".cwwwwwwwwc.",
        ".cwwwwwwwwc.",
        ".cccccccccc.",
        "............",
        "............",
        "............",
        "............",
    ),
}

PALETAS_FOCO = {
    "ativo": {
        "c": tema.COR_FOCO,
        "w": tema.COR_AGUA,
        "d": (52, 52, 58),
        "t": (188, 106, 70),
    },
    "inativo": {
        "c": tema.COR_FOCO_INATIVO,
        "w": (128, 152, 172),
        "d": (96, 100, 108),
        "t": (150, 140, 136),
    },
}
