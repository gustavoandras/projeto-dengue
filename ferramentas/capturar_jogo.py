"""
Teste de fumaça do jogo, sem janela.

Executa uma missão completa de ponta a ponta — seleção de cenário, foco
e algoritmo, movimentação do usuário, animação do agente, tela de
resultado — e salva capturas de cada etapa. Também exercita os botões
clicáveis, simulando cliques nas coordenadas que o próprio jogo gerou.

Uso:  python -m ferramentas.capturar_jogo
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

import main as jogo_principal  # noqa: E402

DESTINO = RAIZ / "resultados" / "capturas"
TAMANHO = (1440, 860)


def _tecla(jogo, chave) -> None:
    jogo.tratar_evento(pygame.event.Event(pygame.KEYDOWN, key=chave))


def _clicar(jogo, identificador) -> None:
    """Clica no botão com o identificador dado, usando o rect real."""
    jogo.desenhar()          # garante que os botões do quadro existem
    for botao in jogo.botoes.itens:
        if botao.identificador == identificador:
            jogo.tratar_evento(pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=botao.rect.center
            ))
            return
    disponiveis = [b.identificador for b in jogo.botoes.itens]
    raise AssertionError(
        f"botão {identificador} não encontrado. Disponíveis: {disponiveis}"
    )


def _clicar_celula(jogo, desenhista, celula) -> None:
    jogo.desenhar()
    rect = desenhista.retangulo_da_celula(*celula)
    jogo.tratar_evento(pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center
    ))


def _salvar(jogo, nome: str) -> Path:
    jogo.desenhar()
    caminho = DESTINO / nome
    pygame.image.save(jogo.tela, str(caminho))
    print(f"gerado: {caminho}")
    return caminho


def executar() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)

    jogo_principal.ARQUIVO_EXECUCOES = (
        RAIZ / "resultados" / "_teste_execucoes.csv"
    )
    if jogo_principal.ARQUIVO_EXECUCOES.exists():
        jogo_principal.ARQUIVO_EXECUCOES.unlink()

    jogo = jogo_principal.Jogo(tamanho=TAMANHO)

    # --- 1. seleção: tudo por clique --------------------------------------
    _clicar(jogo, ("cenario", 2))
    assert jogo.cenario.numero == 3, "clique no cenário não funcionou"

    _clicar(jogo, ("algoritmo", "A*"))
    assert jogo.algoritmo == "A*"

    # troca de foco pelo botão, depois volta clicando no mapa
    focos_do_cenario = [p for p, _ in jogo.grade.focos_ordenados()]
    outro = next(p for p in focos_do_cenario if p != jogo.grade.objetivo)
    _clicar(jogo, ("foco", outro))
    assert jogo.grade.objetivo == outro, "clique no botão de foco falhou"

    padrao = next(p for p, t in jogo.grade.focos_ordenados()
                  if t.codigo == jogo.cenario.foco_padrao)
    _clicar_celula(jogo, jogo.desenhista_usuario, padrao)
    assert jogo.grade.objetivo == padrao, "clique no foco do mapa falhou"

    jogo.tempo = 0.52
    _salvar(jogo, "jogo_1_selecao.png")

    # --- 2. missão pelo botão INICIAR -------------------------------------
    _clicar(jogo, ("iniciar",))
    assert jogo.estado is jogo_principal.Estado.MISSAO
    print(f"  busca: {jogo.resultado_busca}")

    for _ in range(16):
        jogo.atualizar(1 / 60)
    for _ in range(6):
        jogo.jogador.mover(1, 0)
    _salvar(jogo, "jogo_2_explorando.png")

    # --- 3. agente percorrendo --------------------------------------------
    for _ in range(150):
        jogo.atualizar(1 / 60)
    for _ in range(6):
        jogo.jogador.mover(1, 0)
    for _ in range(10):
        jogo.jogador.mover(0, 1)
    _salvar(jogo, "jogo_3_percorrendo.png")

    # --- 4. ambos chegam ao foco ------------------------------------------
    caminho = jogo.resultado_busca.caminho
    jogo.jogador.posicao = jogo.grade.inicio
    jogo.jogador.caminho = [jogo.grade.inicio]
    jogo.jogador.passos = 0
    jogo.jogador.custo = 0
    for anterior, atual in zip(caminho, caminho[1:]):
        jogo.jogador.mover(atual[0] - anterior[0], atual[1] - anterior[1])
    assert jogo.jogador.chegou, "usuário não chegou ao foco"

    jogo.agente.concluir_imediatamente()
    jogo.atualizar(1 / 60)
    assert jogo.estado is jogo_principal.Estado.RESULTADO, jogo.estado
    assert jogo.ordem_chegada, "ordem de chegada não foi registrada"
    print(f"  chegou primeiro: {jogo.ordem_chegada[0]}")
    _salvar(jogo, "jogo_4_resultado.png")

    # --- 5. registro da execução manual -----------------------------------
    arquivo = jogo_principal.ARQUIVO_EXECUCOES
    assert arquivo.exists(), "execução do usuário não foi registrada"
    linhas = arquivo.read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 2, f"esperava cabeçalho + 1 linha, veio {len(linhas)}"
    print(f"  registro: {linhas[1][:76]}…")
    arquivo.unlink()

    # --- 6. redimensionamento ---------------------------------------------
    for tamanho in ((1024, 640), (1920, 1080), TAMANHO):
        jogo.tratar_evento(pygame.event.Event(
            pygame.VIDEORESIZE, w=tamanho[0], h=tamanho[1], size=tamanho
        ))
        jogo.desenhar()
    print(f"  redimensionamento: ok em {len(3 * [0])} tamanhos")

    # --- 7. todos os cenários e focos na tela de seleção ------------------
    _clicar(jogo, ("reiniciar",))       # sai da tela de resultado
    assert jogo.estado is jogo_principal.Estado.SELECAO, jogo.estado
    for indice in range(3):
        _clicar(jogo, ("cenario", indice))
        for posicao, _tipo in jogo.grade.focos_ordenados():
            _clicar(jogo, ("foco", posicao))
            assert jogo.grade.objetivo == posicao
            jogo.desenhar()
        # volta ao foco padrão e guarda a captura do cenário
        padrao_do_cenario = next(
            p for p, t in jogo.grade.focos_ordenados()
            if t.codigo == jogo.cenario.foco_padrao
        )
        _clicar(jogo, ("foco", padrao_do_cenario))
        jogo.tempo = 0.52
        _salvar(jogo, f"cenario_{indice + 1}.png")
    print("  seleção de todos os focos de todos os cenários: ok")

    pygame.quit()
    print("\nTeste de fumaça concluído sem erros.")


if __name__ == "__main__":
    executar()
