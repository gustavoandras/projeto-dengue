from __future__ import annotations

import csv
import math
import os
import sys
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
MODO_CAPTURA = "--capturas" in sys.argv
if MODO_CAPTURA:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from core import celulas, cenarios
from jogo import tema
from jogo.animacao import AnimacaoAgente
from jogo.jogador import Jogador
from jogo.render import TAM_LOGICO, DesenhistaGrade
from jogo.ui import Botao, ColecaoBotoes
from search import ALGORITMOS

ARQUIVO_EXECUCOES = RAIZ / "resultados" / "execucoes_usuario.csv"

ATALHOS_ALGORITMO = {"BFS": "B", "DFS": "D", "Busca Gulosa": "G", "A*": "A"}
TECLAS_ALGORITMO = {
    pygame.K_b: "BFS",
    pygame.K_d: "DFS",
    pygame.K_g: "Busca Gulosa",
    pygame.K_a: "A*",
}
TECLAS_MOVIMENTO = {
    pygame.K_UP: (-1, 0),
    pygame.K_RIGHT: (0, 1),
    pygame.K_DOWN: (1, 0),
    pygame.K_LEFT: (0, -1),
    pygame.K_w: (-1, 0),
    pygame.K_d: (0, 1),
    pygame.K_s: (1, 0),
    pygame.K_a: (0, -1),
}


def ativar_consciencia_dpi() -> None:
    if sys.platform != "win32":
        return
    import ctypes
    try:

        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


class Estado(Enum):
    SELECAO = auto()
    MISSAO = auto()
    RESULTADO = auto()


class Fontes:

    def __init__(self, altura_janela: int):
        pygame.font.init()

        escala = max(0.90, min(1.9, altura_janela / 720))
        def tamanho(base):
            return max(10, int(base * escala))
        self.titulo = pygame.font.SysFont("dejavusans", tamanho(25), bold=True)
        self.grande = pygame.font.SysFont("dejavusans", tamanho(20), bold=True)
        self.cabecalho = pygame.font.SysFont("dejavusans", tamanho(16), bold=True)
        self.rotulo = pygame.font.SysFont("dejavusans", tamanho(13), bold=True)
        self.corpo = pygame.font.SysFont("dejavusans", tamanho(13))
        self.pequena = pygame.font.SysFont("dejavusans", tamanho(11))
        self.mono = pygame.font.SysFont("dejavusansmono", tamanho(13))


class Jogo:
    def __init__(self, tamanho: tuple[int, int] | None = None):
        ativar_consciencia_dpi()
        pygame.init()
        pygame.display.set_caption("Agente de Combate à Dengue")

        if tamanho is None:
            info = pygame.display.Info()
            largura = max(tema.LARGURA_MINIMA,
                          int(info.current_w * tema.FRACAO_TELA))
            altura = max(tema.ALTURA_MINIMA,
                         int(info.current_h * tema.FRACAO_TELA))
            tamanho = (largura, altura)

        self.tela_cheia = False
        self.tamanho_janela = tamanho
        self.tela = pygame.display.set_mode(tamanho, pygame.RESIZABLE)
        self.relogio = pygame.time.Clock()
        self.botoes = ColecaoBotoes()

        self.indice_cenario = 0
        self.algoritmo = "A*"
        self.estado = Estado.SELECAO
        self.tempo = 0.0
        self.jogador: Jogador | None = None
        self.agente: AnimacaoAgente | None = None
        self.resultado_busca = None
        self.ordem_chegada: list[str] = []
        self.ja_registrados = self._carregar_cenarios_registrados()

        self._ao_redimensionar(tamanho)
        self._montar_cenario()

    def _ao_redimensionar(self, tamanho) -> None:
        self.largura, self.altura = tamanho
        self.fontes = Fontes(self.altura)
        if hasattr(self, "grade"):
            self._montar_layout()

    def alternar_tela_cheia(self) -> None:
        self.tela_cheia = not self.tela_cheia
        if self.tela_cheia:
            self.tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.tela = pygame.display.set_mode(
                self.tamanho_janela, pygame.RESIZABLE
            )
        self._ao_redimensionar(self.tela.get_size())

    def _montar_layout(self) -> None:
        margem = tema.MARGEM
        largura_painel = min(
            tema.LARGURA_PAINEL, max(260, int(self.largura * 0.26))
        )

        topo = margem + tema.ALTURA_CABECALHO + 26
        altura_disponivel = self.altura - topo - margem - tema.ALTURA_RODAPE
        largura_util = (
            self.largura - largura_painel - 3 * margem
            - tema.ESPACO_ENTRE_GRADES
        )
        largura_grade = largura_util // 2

        bruto = min(
            largura_grade // self.grade.colunas,
            altura_disponivel // self.grade.linhas,
        )
        escala = max(1, bruto // TAM_LOGICO)
        lado = escala * TAM_LOGICO

        largura_grades = lado * self.grade.colunas
        altura_grades = lado * self.grade.linhas

        conjunto = 2 * largura_grades + tema.ESPACO_ENTRE_GRADES
        x0 = margem + max(
            0, (largura_util + tema.ESPACO_ENTRE_GRADES - conjunto) // 2
        )

        sobra = altura_disponivel - altura_grades
        altura_faixa = (
            min(sobra - margem, tema.FAIXA_MAXIMA)
            if sobra > tema.FAIXA_MINIMA else 0
        )

        respiro = max(0, sobra - altura_faixa - (margem if altura_faixa else 0))
        topo += respiro // 2

        area_usuario = pygame.Rect(x0, topo, largura_grades, altura_grades)
        area_agente = pygame.Rect(
            x0 + largura_grades + tema.ESPACO_ENTRE_GRADES,
            topo, largura_grades, altura_grades,
        )
        self.area_painel = pygame.Rect(
            self.largura - largura_painel - margem, margem,
            largura_painel, self.altura - 2 * margem,
        )
        self.area_faixa = pygame.Rect(
            x0, topo + altura_grades + margem, conjunto, altura_faixa,
        ) if altura_faixa else None

        self.desenhista_usuario = DesenhistaGrade(self.grade, area_usuario)
        self.desenhista_agente = DesenhistaGrade(self.grade, area_agente)

    def _montar_cenario(self, codigo_foco: str | None = None) -> None:
        self.cenario = cenarios.CENARIOS[self.indice_cenario]
        self.grade = self.cenario.criar_grade(codigo_foco)
        self.jogador = None
        self.agente = None
        self.resultado_busca = None
        self.ordem_chegada = []
        self.estado = Estado.SELECAO
        self._montar_layout()

    def _selecionar_foco(self, posicao) -> None:
        self.grade.definir_objetivo(posicao)

    def _iniciar_missao(self) -> None:
        self.jogador = Jogador(self.grade)
        self.resultado_busca = ALGORITMOS[self.algoritmo](self.grade)
        self.agente = AnimacaoAgente(self.resultado_busca, self.grade)
        self.ordem_chegada = []
        self.jogador.iniciar_cronometro()
        self.estado = Estado.MISSAO

    def _carregar_cenarios_registrados(self) -> set[tuple[int, str]]:
        if not ARQUIVO_EXECUCOES.exists():
            return set()
        registrados = set()
        with ARQUIVO_EXECUCOES.open(encoding="utf-8") as arquivo:
            for linha in csv.DictReader(arquivo):
                try:
                    registrados.add(
                        (int(linha["cenario"]), linha.get("foco", ""))
                    )
                except (KeyError, ValueError):
                    pass
        return registrados

    @property
    def _chave_execucao(self) -> tuple[int, str]:
        return (self.cenario.numero, self.grade.tipo_do_objetivo.codigo)

    def _registrar_execucao_usuario(self) -> None:
        if self._chave_execucao in self.ja_registrados or self.jogador is None:
            return

        ARQUIVO_EXECUCOES.parent.mkdir(parents=True, exist_ok=True)
        novo = not ARQUIVO_EXECUCOES.exists()
        with ARQUIVO_EXECUCOES.open("a", newline="", encoding="utf-8") as arq:
            escritor = csv.writer(arq)
            if novo:
                escritor.writerow([
                    "data_hora", "cenario", "nome_cenario", "foco",
                    "nome_foco", "passos", "custo", "tempo_s",
                    "movimentos_bloqueados", "caminho",
                ])
            resumo = self.jogador.resumo()
            tipo = self.grade.tipo_do_objetivo
            escritor.writerow([
                datetime.now().isoformat(timespec="seconds"),
                self.cenario.numero, self.cenario.nome,
                tipo.codigo, tipo.nome,
                resumo["passos"], resumo["custo"],
                f"{resumo['tempo']:.3f}",
                resumo["movimentos_bloqueados"],
                " ".join(f"{l},{c}" for l, c in resumo["caminho"]),
            ])
        self.ja_registrados.add(self._chave_execucao)

    def tratar_evento(self, evento) -> bool:
        if evento.type == pygame.QUIT:
            return False

        if evento.type == pygame.VIDEORESIZE and not self.tela_cheia:
            self.tamanho_janela = (
                max(tema.LARGURA_MINIMA, evento.w),
                max(tema.ALTURA_MINIMA, evento.h),
            )
            self.tela = pygame.display.set_mode(
                self.tamanho_janela, pygame.RESIZABLE
            )
            self._ao_redimensionar(self.tamanho_janela)
            return True

        if evento.type == pygame.MOUSEMOTION:
            self.botoes.posicao_mouse = evento.pos
            return True

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self._tratar_clique(evento.pos)

        if evento.type == pygame.KEYDOWN:
            return self._tratar_tecla(evento.key)

        return True

    def _tratar_clique(self, posicao) -> bool:
        identificador = self.botoes.clicado(posicao)
        if identificador is not None:
            return self._executar_acao(identificador)

        if self.estado is Estado.SELECAO:
            for desenhista in (self.desenhista_usuario, self.desenhista_agente):
                celula = desenhista.celula_em(posicao)
                if celula is not None and celula in self.grade.focos:
                    self._selecionar_foco(celula)
                    return True
        return True

    def _executar_acao(self, identificador: tuple) -> bool:
        acao, *argumentos = identificador

        if acao == "cenario":
            self.indice_cenario = argumentos[0]
            self._montar_cenario()
        elif acao == "algoritmo":
            self.algoritmo = argumentos[0]
        elif acao == "foco":
            self._selecionar_foco(argumentos[0])
        elif acao == "iniciar":
            self._iniciar_missao()
        elif acao == "pular" and self.agente:
            self.agente.concluir_imediatamente()
        elif acao == "repetir":

            self._montar_cenario(self.grade.tipo_do_objetivo.codigo)
            self._iniciar_missao()
        elif acao == "reiniciar":
            self._montar_cenario(self.grade.tipo_do_objetivo.codigo)
        elif acao == "sair":
            return False
        return True

    def _tratar_tecla(self, tecla) -> bool:
        if tecla == pygame.K_F11:
            self.alternar_tela_cheia()
            return True

        if tecla == pygame.K_ESCAPE:
            if self.estado is Estado.SELECAO:
                return False
            self._montar_cenario(self.grade.tipo_do_objetivo.codigo)
            return True

        if self.estado is Estado.SELECAO:
            if tecla in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.indice_cenario = tecla - pygame.K_1
                self._montar_cenario()
            elif tecla in TECLAS_ALGORITMO:
                self.algoritmo = TECLAS_ALGORITMO[tecla]
            elif tecla in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._iniciar_missao()
            elif tecla == pygame.K_TAB:
                self._proximo_foco()
        elif self.estado is Estado.MISSAO:
            if tecla == pygame.K_TAB and self.agente:
                self.agente.concluir_imediatamente()
            elif tecla == pygame.K_r:
                self._montar_cenario(self.grade.tipo_do_objetivo.codigo)
            elif tecla in TECLAS_MOVIMENTO and self.jogador:
                self.jogador.mover(*TECLAS_MOVIMENTO[tecla])
        else:
            if tecla == pygame.K_r:
                self._executar_acao(("repetir",))

        return True

    def _proximo_foco(self) -> None:
        posicoes = [p for p, _t in self.grade.focos_ordenados()]
        atual = posicoes.index(self.grade.objetivo)
        self._selecionar_foco(posicoes[(atual + 1) % len(posicoes)])

    def atualizar(self, dt: float) -> None:
        if self.estado is not Estado.MISSAO:
            return
        if self.agente:
            self.agente.atualizar(dt)

        if self.jogador and self.agente:

            if self.jogador.chegou and "Você" not in self.ordem_chegada:
                self.ordem_chegada.append("Você")
            if self.agente.chegou and "Agente" not in self.ordem_chegada:
                self.ordem_chegada.append("Agente")

            if self.jogador.chegou and self.agente.chegou:
                self._registrar_execucao_usuario()
                self.estado = Estado.RESULTADO

    def desenhar(self) -> None:
        self.botoes.limpar()
        self.tela.fill(tema.FUNDO)
        pulso = (math.sin(self.tempo * 3.0) + 1) / 2

        self._desenhar_cabecalho()
        self._desenhar_lado_usuario(pulso)
        self._desenhar_lado_agente(pulso)
        self._desenhar_faixa_inferior()
        self._desenhar_painel()
        self._desenhar_rodape()

        if self.estado is Estado.RESULTADO:
            self._desenhar_conclusao()

        self.botoes.desenhar(self.tela, self.fontes)

    def _desenhar_cabecalho(self) -> None:
        titulo = self.fontes.titulo.render(
            "Agente de Combate à Dengue", True, tema.TEXTO
        )
        self.tela.blit(titulo, (tema.MARGEM, tema.MARGEM))

        sub = (
            f"Cenário {self.cenario.numero} — {self.cenario.nome}  ·  "
            f"{self.cenario.nivel}  ·  {self.grade.linhas}x{self.grade.colunas}"
            f"  ·  objetivo: {self.grade.tipo_do_objetivo.nome}"
        )

        self.tela.blit(
            self.fontes.pequena.render(sub, True, tema.TEXTO_DESTAQUE),
            (tema.MARGEM, tema.MARGEM + titulo.get_height() + tema.FOLGA_SUBTITULO),
        )

    def _titulo_lado(self, desenhista, titulo, subtitulo, cor) -> None:
        x, y = desenhista.rect.x, desenhista.rect.y - 26
        texto = self.fontes.cabecalho.render(titulo, True, cor)
        self.tela.blit(texto, (x, y))
        self.tela.blit(
            self.fontes.pequena.render(subtitulo, True, tema.TEXTO_FRACO),
            (x + texto.get_width() + 10, y + 4),
        )

    def _desenhar_lado_usuario(self, pulso: float) -> None:
        d = self.desenhista_usuario
        if self.jogador and self.jogador.chegou:
            estado_txt = "chegou ao foco"
        elif self.estado is Estado.SELECAO:
            estado_txt = "clique num foco para escolher o objetivo"
        else:
            estado_txt = "use as setas"
        self._titulo_lado(d, "VOCÊ", estado_txt, tema.COR_TITULO_USUARIO)

        d.desenhar_terreno(self.tela)
        if self.jogador and len(self.jogador.caminho) > 1:
            d.desenhar_sobreposicao(
                self.tela, self.jogador.caminho[:-1], tema.COR_RASTRO_USUARIO
            )
            d.desenhar_trilha(
                self.tela, self.jogador.caminho, (*tema.COR_USUARIO, 200)
            )
        d.desenhar_inicio(self.tela)
        d.desenhar_focos(self.tela, pulso)
        posicao = self.jogador.posicao if self.jogador else self.grade.inicio
        d.desenhar_personagem(self.tela, *posicao, "usuario")

    def _desenhar_lado_agente(self, pulso: float) -> None:
        d = self.desenhista_agente
        if self.agente is None:
            estado_txt = "aguardando início"
        elif self.agente.chegou:
            estado_txt = "chegou ao foco"
        elif self.agente.fase.name == "EXPLORANDO":
            estado_txt = "explorando estados"
        else:
            estado_txt = "percorrendo o caminho"
        self._titulo_lado(
            d, f"AGENTE — {self.algoritmo}", estado_txt, tema.COR_TITULO_AGENTE
        )

        d.desenhar_terreno(self.tela)
        if self.agente:
            d.desenhar_sobreposicao(
                self.tela, self.agente.estados_revelados, tema.COR_EXPLORADO
            )
            percorrido = self.agente.caminho_percorrido
            if len(percorrido) > 1:
                d.desenhar_sobreposicao(self.tela, percorrido, tema.COR_CAMINHO)
                d.desenhar_trilha(
                    self.tela, percorrido, (*tema.COR_FOCO, 210)
                )
        d.desenhar_inicio(self.tela)
        d.desenhar_focos(self.tela, pulso)
        posicao = self.agente.posicao if self.agente else self.grade.inicio
        d.desenhar_personagem(self.tela, *posicao, "agente")

    def _desenhar_faixa_inferior(self) -> None:
        faixa = self.area_faixa
        if faixa is None:
            return

        pygame.draw.rect(self.tela, tema.FUNDO_PAINEL, faixa, border_radius=8)
        pygame.draw.rect(self.tela, tema.BORDA_PAINEL, faixa, width=1,
                         border_radius=8)

        if self.estado is Estado.SELECAO:
            self._faixa_explicacao(faixa)
        else:
            self._faixa_comparacao(faixa)

    def _faixa_explicacao(self, faixa) -> None:
        metade = faixa.width // 2
        x, y = faixa.x + 18, faixa.y + 14
        tipo = self.grade.tipo_do_objetivo

        self.tela.blit(
            self.fontes.rotulo.render("O CENÁRIO", True, tema.TEXTO_DESTAQUE),
            (x, y),
        )
        self._paragrafo(x, y + 20, metade - 40, self.cenario.descricao,
                        tema.TEXTO_SUAVE, self.fontes.corpo)

        x2 = faixa.x + metade + 10
        self.tela.blit(
            self.fontes.rotulo.render(
                f"FOCO ESCOLHIDO — {tipo.nome.upper()}",
                True, tema.TEXTO_DESTAQUE),
            (x2, y),
        )
        self._paragrafo(x2, y + 20, metade - 40, tipo.mensagem,
                        tema.TEXTO_SUAVE, self.fontes.corpo)

    def _faixa_comparacao(self, faixa) -> None:
        resultado = self.resultado_busca
        jogador, agente = self.jogador, self.agente
        metade = faixa.width // 2

        def bloco(x_base, titulo, cor, pares, marcado):
            y = faixa.y + 12
            rotulo = self.fontes.cabecalho.render(titulo, True, cor)
            self.tela.blit(rotulo, (x_base, y))
            if marcado:
                selo = self.fontes.pequena.render(
                    "chegou primeiro", True, tema.COR_VENCEDOR
                )
                self.tela.blit(
                    selo, (x_base + rotulo.get_width() + 10, y + 5)
                )
            y += 28
            largura_item = (metade - 40) // max(1, len(pares))
            for indice, (nome, valor) in enumerate(pares):
                cx = x_base + indice * largura_item
                self.tela.blit(
                    self.fontes.pequena.render(nome, True, tema.TEXTO_FRACO),
                    (cx, y),
                )
                self.tela.blit(
                    self.fontes.grande.render(valor, True, tema.TEXTO),
                    (cx, y + 16),
                )

        primeiro = self.ordem_chegada[0] if self.ordem_chegada else None

        bloco(
            faixa.x + 18, "VOCÊ", tema.COR_TITULO_USUARIO,
            [("Passos", f"{jogador.passos}"),
             ("Custo", f"{jogador.custo}"),
             ("Tempo", f"{jogador.tempo:.1f} s")],
            primeiro == "Você",
        )

        if resultado.encontrou:
            pares = [("Passos", f"{resultado.passos}"),
                     ("Custo", f"{resultado.custo}"),
                     ("Expandidos", f"{resultado.expandidos}"),
                     ("Gerados", f"{resultado.gerados}"),
                     ("Front. máx", f"{resultado.fronteira_maxima}")]
        else:
            pares = [("Resultado", "sem solução")]

        bloco(
            faixa.x + metade + 10, f"AGENTE — {self.algoritmo}",
            tema.COR_TITULO_AGENTE, pares, primeiro == "Agente",
        )

        pygame.draw.line(
            self.tela, tema.BORDA_PAINEL,
            (faixa.x + metade, faixa.y + 12),
            (faixa.x + metade, faixa.bottom - 12),
        )

    def _desenhar_painel(self) -> None:
        pygame.draw.rect(self.tela, tema.FUNDO_PAINEL, self.area_painel,
                         border_radius=8)
        pygame.draw.rect(self.tela, tema.BORDA_PAINEL, self.area_painel,
                         width=1, border_radius=8)

        x = self.area_painel.x + 14
        largura = self.area_painel.width - 28
        y = self.area_painel.y + 14

        if self.estado is Estado.SELECAO:
            self._painel_selecao(x, y, largura)
        else:
            self._painel_metricas(x, y, largura)

    def _painel_selecao(self, x, y, largura) -> int:
        y = self._secao(x, y, "CENÁRIO")
        coluna_largura = (largura - 12) // 3
        for indice, cenario in enumerate(cenarios.CENARIOS):
            rect = pygame.Rect(
                x + indice * (coluna_largura + 6), y, coluna_largura, 34
            )
            self.botoes.adicionar(Botao(
                ("cenario", indice), str(indice + 1), rect,
                ativo=indice == self.indice_cenario,
                estilo="normal",
            ))
        y += 40
        self.tela.blit(
            self.fontes.pequena.render(
                f"{self.cenario.nivel} — {self.cenario.nome}",
                True, tema.TEXTO_FRACO),
            (x, y),
        )
        y += 22

        y = self._secao(x, y, "FOCO A ELIMINAR")
        for posicao, tipo in self.grade.focos_ordenados():
            rect = pygame.Rect(x, y, largura, 32)
            self.botoes.adicionar(Botao(
                ("foco", posicao), tipo.dica, rect,
                ativo=posicao == self.grade.objetivo,
            ))
            y += 37
        y += 2

        y = self._secao(x, y, "ALGORITMO DO AGENTE")
        for nome in ALGORITMOS:
            rect = pygame.Rect(x, y, largura, 32)
            self.botoes.adicionar(Botao(
                ("algoritmo", nome), nome, rect,
                ativo=nome == self.algoritmo,
                marca=ATALHOS_ALGORITMO[nome],
            ))
            y += 37

        y += 8
        if self._chave_execucao in self.ja_registrados:
            y = self._paragrafo(
                x, y, largura,
                "Esta combinação já tem execução manual registrada. Pode "
                "jogar de novo para demonstrar, mas não será gravada "
                "outra vez.",
                tema.TEXTO_FRACO, self.fontes.pequena,
            )
            y += 8

        altura_botao = 44
        limite = self.area_painel.bottom - 16 - altura_botao
        y = min(y, limite)
        self.botoes.adicionar(Botao(
            ("iniciar",), "INICIAR MISSÃO",
            pygame.Rect(x, y, largura, altura_botao),
            estilo="principal",
        ))
        return y + altura_botao

    def _painel_metricas(self, x, y, largura) -> int:
        jogador, agente = self.jogador, self.agente
        resultado = self.resultado_busca

        y = self._secao(x, y, "VOCÊ")
        for rotulo, valor in (
            ("Passos", f"{jogador.passos}"),
            ("Custo total", f"{jogador.custo}"),
            ("Tempo", f"{jogador.tempo:.1f} s"),
        ):
            y = self._linha(x, y, largura, rotulo, valor,
                            tema.COR_TITULO_USUARIO)

        y += 12
        y = self._secao(x, y, f"AGENTE — {self.algoritmo}")

        if resultado and not resultado.encontrou:
            y = self._paragrafo(
                x, y, largura,
                "O algoritmo não encontrou caminho até este foco.",
                tema.COR_AGENTE, self.fontes.corpo,
            )
        else:
            for rotulo, valor in (
                ("Passos", f"{agente.passos_dados} / {resultado.passos}"),
                ("Custo total", f"{agente.custo_parcial} / {resultado.custo}"),
                ("Tempo da busca", f"{resultado.tempo_busca * 1000:.3f} ms"),
                ("Estados expandidos", f"{resultado.expandidos}"),
                ("Estados gerados", f"{resultado.gerados}"),
                ("Fronteira máxima", f"{resultado.fronteira_maxima}"),
            ):
                y = self._linha(x, y, largura, rotulo, valor,
                                tema.COR_TITULO_AGENTE)

        y += 8
        y = self._paragrafo(
            x, y, largura,
            "O tempo da busca é só do algoritmo. A animação na tela não "
            "entra nessa medição.",
            tema.TEXTO_FRACO, self.fontes.pequena,
        )

        if self.estado is Estado.MISSAO:
            y += 10
            meio = (largura - 8) // 2
            self.botoes.adicionar(Botao(
                ("pular",), "Pular animação",
                pygame.Rect(x, y, meio, 34), marca="TAB",
            ))
            self.botoes.adicionar(Botao(
                ("reiniciar",), "Reiniciar",
                pygame.Rect(x + meio + 8, y, meio, 34), marca="R",
            ))
            y += 40

        self._painel_legenda(x, self.area_painel.bottom - 150, largura)
        return y

    def _painel_legenda(self, x, y, largura) -> None:
        pygame.draw.line(self.tela, tema.BORDA_PAINEL, (x, y), (x + largura, y))
        y += 10
        for tipo in celulas.TERRENOS:
            amostra = pygame.Rect(x, y + 1, 15, 12)
            pygame.draw.rect(self.tela, tema.cor_terreno(tipo.codigo), amostra)
            pygame.draw.rect(self.tela, tema.BORDA_PAINEL, amostra, 1)
            rotulo = (tipo.nome if not tipo.transponivel
                      else f"{tipo.nome} — custo {tipo.custo}")
            self.tela.blit(
                self.fontes.pequena.render(rotulo, True, tema.TEXTO_FRACO),
                (x + 22, y),
            )
            y += 18

        for cor, rotulo in ((tema.COR_EXPLORADO[:3], "estados explorados"),
                            (tema.COR_CAMINHO[:3], "caminho encontrado")):
            amostra = pygame.Rect(x, y + 1, 15, 12)
            pygame.draw.rect(self.tela, cor, amostra)
            self.tela.blit(
                self.fontes.pequena.render(rotulo, True, tema.TEXTO_FRACO),
                (x + 22, y),
            )
            y += 18

    def _desenhar_conclusao(self) -> None:
        veu = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        veu.fill((10, 13, 20, 210))
        self.tela.blit(veu, (0, 0))

        largura = min(820, self.largura - 80)
        altura = min(418, self.altura - 60)
        caixa = pygame.Rect(
            (self.largura - largura) // 2, (self.altura - altura) // 2,
            largura, altura,
        )
        pygame.draw.rect(self.tela, tema.FUNDO_PAINEL, caixa, border_radius=12)
        pygame.draw.rect(self.tela, tema.COR_FOCO, caixa, width=2,
                         border_radius=12)

        x = caixa.x + 30
        y = caixa.y + 22
        util = largura - 60
        tipo = self.grade.tipo_do_objetivo

        self.tela.blit(
            self.fontes.titulo.render("Foco eliminado!", True, tema.COR_FOCO),
            (x, y),
        )
        if self.ordem_chegada:
            quem = self.ordem_chegada[0]
            aviso = self.fontes.corpo.render(
                f"{quem} chegou primeiro", True, tema.COR_VENCEDOR
            )
            self.tela.blit(aviso, (caixa.right - 30 - aviso.get_width(), y + 8))
        y += 38

        self.tela.blit(
            self.fontes.grande.render(tipo.nome, True, tema.TEXTO), (x, y)
        )
        y += 28
        y = self._paragrafo(x, y, util, tipo.mensagem, tema.TEXTO,
                            self.fontes.corpo)

        y += 14
        pygame.draw.line(self.tela, tema.BORDA_PAINEL, (x, y), (x + util, y))
        y += 12

        resultado = self.resultado_busca
        larguras = [0.26, 0.11, 0.11, 0.15, 0.13, 0.12, 0.12]
        colunas, acumulado = [], x
        for fracao in larguras:
            colunas.append(acumulado)
            acumulado += int(util * fracao)

        cabecalhos = ["", "Passos", "Custo", "Tempo", "Expand.", "Gerados",
                      "Front.máx"]
        for coluna, titulo in zip(colunas, cabecalhos):
            self.tela.blit(
                self.fontes.rotulo.render(titulo, True, tema.TEXTO_DESTAQUE),
                (coluna, y),
            )
        y += 22

        linhas = [
            ("Você", tema.COR_TITULO_USUARIO, [
                f"{self.jogador.passos}", f"{self.jogador.custo}",
                f"{self.jogador.tempo:.1f} s", "—", "—", "—",
            ]),
            (f"Agente ({self.algoritmo})", tema.COR_TITULO_AGENTE, [
                f"{resultado.passos}", f"{resultado.custo}",
                f"{resultado.tempo_busca * 1000:.2f} ms",
                f"{resultado.expandidos}", f"{resultado.gerados}",
                f"{resultado.fronteira_maxima}",
            ]),
        ]
        for rotulo, cor, valores in linhas:
            self.tela.blit(
                self.fontes.corpo.render(rotulo, True, cor), (colunas[0], y)
            )
            for coluna, valor in zip(colunas[1:], valores):
                self.tela.blit(
                    self.fontes.mono.render(valor, True, tema.TEXTO),
                    (coluna, y),
                )
            y += 22

        y += 8
        if self.jogador.custo < resultado.custo:
            veredito = "Você encontrou um caminho mais barato que o agente."
        elif self.jogador.custo == resultado.custo:
            veredito = "Você empatou com o agente em custo total."
        else:
            diferenca = self.jogador.custo - resultado.custo
            veredito = f"O agente gastou {diferenca} de custo a menos que você."
        self.tela.blit(
            self.fontes.corpo.render(veredito, True, tema.TEXTO_DESTAQUE),
            (x, y),
        )
        y += 20
        y = self._paragrafo(
            x, y, util,
            "Os dois tempos medem coisas diferentes: o seu é o tempo real de "
            "jogo, o do agente é só a execução do algoritmo. Compare passos, "
            "custo e estados.",
            tema.TEXTO_FRACO, self.fontes.pequena,
        )

        meio = (util - 10) // 2
        base = caixa.bottom - 52
        self.botoes.adicionar(Botao(
            ("repetir",), "Jogar de novo",
            pygame.Rect(x, base, meio, 38), marca="R",
        ))
        self.botoes.adicionar(Botao(
            ("reiniciar",), "Escolher outro foco",
            pygame.Rect(x + meio + 10, base, meio, 38), marca="ESC",
        ))

    def _secao(self, x, y, titulo) -> int:
        self.tela.blit(
            self.fontes.rotulo.render(titulo, True, tema.TEXTO_DESTAQUE), (x, y)
        )
        y += 18
        pygame.draw.line(self.tela, tema.BORDA_PAINEL, (x, y),
                         (x + self.area_painel.width - 28, y))
        return y + 8

    def _linha(self, x, y, largura, rotulo, valor, cor_valor) -> int:
        self.tela.blit(
            self.fontes.corpo.render(rotulo, True, tema.TEXTO_FRACO), (x, y)
        )
        render = self.fontes.mono.render(valor, True, cor_valor)
        self.tela.blit(render, (x + largura - render.get_width(), y))
        return y + 19

    def _paragrafo(self, x, y, largura, texto, cor, fonte) -> int:
        linha = ""
        for palavra in texto.split():
            teste = f"{linha} {palavra}".strip()
            if fonte.size(teste)[0] > largura:
                self.tela.blit(fonte.render(linha, True, cor), (x, y))
                y += fonte.get_height() + 2
                linha = palavra
            else:
                linha = teste
        if linha:
            self.tela.blit(fonte.render(linha, True, cor), (x, y))
            y += fonte.get_height() + 2
        return y

    def _desenhar_rodape(self) -> None:
        if self.estado is Estado.SELECAO:
            texto = ("clique nos botões ou no foco do mapa     "
                     "1 2 3 cenário · B D G A algoritmo · TAB foco · "
                     "ENTER iniciar · F11 tela cheia")
        elif self.estado is Estado.MISSAO:
            texto = ("setas  mover seu personagem     TAB  pular animação     "
                     "R  reiniciar     ESC  voltar")
        else:
            texto = "R  jogar de novo     ESC  escolher outro foco"
        self.tela.blit(
            self.fontes.pequena.render(texto, True, tema.TEXTO_FRACO),
            (tema.MARGEM, self.altura - tema.MARGEM - 12),
        )

    def executar(self) -> None:
        rodando = True
        while rodando:
            dt = self.relogio.tick(tema.FPS) / 1000.0
            self.tempo += dt
            for evento in pygame.event.get():
                rodando = self.tratar_evento(evento)
                if not rodando:
                    break
            self.atualizar(dt)
            self.desenhar()
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    Jogo().executar()
