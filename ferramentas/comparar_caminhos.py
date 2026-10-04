from __future__ import annotations

import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from core import cenarios
from jogo import tema
from jogo.render import DesenhistaGrade
from search import ALGORITMOS

DESTINO = RAIZ / "resultados" / "capturas"

LARGURA, ALTURA = 1120, 940
MARGEM = 22
ESPACO = 18
ALTURA_TITULO = 56


def gerar(cenario) -> Path:
    grade = cenario.criar_grade()
    tela = pygame.Surface((LARGURA, ALTURA))
    tela.fill(tema.FUNDO)

    fonte_titulo = pygame.font.SysFont("dejavusans", 24, bold=True)
    fonte_sub = pygame.font.SysFont("dejavusans", 14)
    fonte_alg = pygame.font.SysFont("dejavusans", 18, bold=True)
    fonte_met = pygame.font.SysFont("dejavusansmono", 13)

    tela.blit(
        fonte_titulo.render(
            f"Cenário {cenario.numero} — {cenario.nome}: caminho de cada "
            f"algoritmo", True, tema.TEXTO),
        (MARGEM, MARGEM),
    )
    tela.blit(
        fonte_sub.render(
            "azul claro = estados explorados · amarelo = caminho encontrado",
            True, tema.TEXTO_FRACO),
        (MARGEM, MARGEM + 30),
    )

    topo = MARGEM + ALTURA_TITULO
    largura_celula = (LARGURA - 2 * MARGEM - ESPACO) // 2
    altura_celula = (ALTURA - topo - MARGEM - ESPACO) // 2

    for indice, (nome, buscar) in enumerate(ALGORITMOS.items()):
        resultado = buscar(grade)
        coluna, linha = indice % 2, indice // 2
        area = pygame.Rect(
            MARGEM + coluna * (largura_celula + ESPACO),
            topo + linha * (altura_celula + ESPACO) + 46,
            largura_celula,
            altura_celula - 46,
        )
        desenhista = DesenhistaGrade(grade, area)

        x = desenhista.rect.x
        y = area.y - 42
        tela.blit(
            fonte_alg.render(nome, True, tema.COR_TITULO_AGENTE), (x, y)
        )
        metricas = (
            f"{resultado.passos} passos · custo {resultado.custo} · "
            f"{resultado.expandidos} expandidos · "
            f"fronteira máx. {resultado.fronteira_maxima}"
        )
        tela.blit(fonte_met.render(metricas, True, tema.TEXTO), (x, y + 22))

        desenhista.desenhar_terreno(tela)
        desenhista.desenhar_sobreposicao(
            tela, resultado.ordem_exploracao, tema.COR_EXPLORADO
        )
        if resultado.encontrou:
            desenhista.desenhar_sobreposicao(
                tela, resultado.caminho, tema.COR_CAMINHO
            )
            desenhista.desenhar_trilha(
                tela, resultado.caminho, (*tema.COR_FOCO, 220)
            )
        desenhista.desenhar_inicio(tela)
        desenhista.desenhar_focos(tela, 0.8)

    DESTINO.mkdir(parents=True, exist_ok=True)
    caminho = DESTINO / f"comparacao_cenario_{cenario.numero}.png"
    pygame.image.save(tela, str(caminho))
    print(f"gerado: {caminho}")
    return caminho


def main() -> None:
    pygame.init()
    pygame.font.init()
    alvos = cenarios.CENARIOS
    if len(sys.argv) > 1:
        alvos = [cenarios.por_numero(int(sys.argv[1]))]
    for cenario in alvos:
        gerar(cenario)
    pygame.quit()


if __name__ == "__main__":
    main()
