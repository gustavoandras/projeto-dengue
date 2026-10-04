from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from . import tema


@dataclass
class Botao:

    identificador: tuple
    rotulo: str
    rect: pygame.Rect
    ativo: bool = False
    habilitado: bool = True
    estilo: str = "normal"
    sublegenda: str | None = None
    marca: str | None = None
    _hover: bool = field(default=False, repr=False)

    def contem(self, posicao) -> bool:
        return self.habilitado and self.rect.collidepoint(posicao)

    def desenhar(self, tela: pygame.Surface, fontes) -> None:
        fundo, borda, cor_texto = self._cores()

        pygame.draw.rect(tela, fundo, self.rect, border_radius=7)
        if borda:
            pygame.draw.rect(tela, borda, self.rect, width=2, border_radius=7)

        fonte = fontes.cabecalho if self.estilo == "principal" else fontes.corpo
        texto = fonte.render(self.rotulo, True, cor_texto)

        if self.estilo == "principal":
            tela.blit(texto, (
                self.rect.centerx - texto.get_width() // 2,
                self.rect.centery - texto.get_height() // 2,
            ))
            return

        if self.sublegenda:
            tela.blit(texto, (self.rect.x + 11, self.rect.y + 6))
            sub = fontes.pequena.render(
                self.sublegenda, True, tema.TEXTO_FRACO
            )
            tela.blit(sub, (self.rect.x + 11, self.rect.y + 24))
        else:
            tela.blit(texto, (
                self.rect.x + 11,
                self.rect.centery - texto.get_height() // 2,
            ))

        if self.marca:
            marca = fontes.pequena.render(self.marca, True, tema.TEXTO_FRACO)

            espaco_livre = (
                self.rect.width - 21 - texto.get_width() - marca.get_width()
            )
            if espaco_livre >= 10:
                tela.blit(marca, (
                    self.rect.right - marca.get_width() - 10,
                    self.rect.centery - marca.get_height() // 2,
                ))

    def _cores(self):
        if not self.habilitado:
            return tema.BOTAO_DESABILITADO, None, tema.TEXTO_FRACO
        if self.estilo == "principal":
            fundo = tema.BOTAO_PRINCIPAL_HOVER if self._hover else tema.BOTAO_PRINCIPAL
            return fundo, None, tema.BOTAO_PRINCIPAL_TEXTO
        if self.ativo:
            return tema.BOTAO_ATIVO, tema.BOTAO_ATIVO_BORDA, tema.TEXTO
        if self._hover:
            return tema.BOTAO_HOVER, tema.BORDA_PAINEL, tema.TEXTO
        return tema.BOTAO, tema.BORDA_PAINEL, tema.TEXTO_SUAVE


class ColecaoBotoes:

    def __init__(self):
        self.itens: list[Botao] = []
        self.posicao_mouse = (-1, -1)

    def limpar(self) -> None:
        self.itens.clear()

    def adicionar(self, botao: Botao) -> Botao:
        botao._hover = botao.habilitado and botao.rect.collidepoint(
            self.posicao_mouse
        )
        self.itens.append(botao)
        return botao

    def desenhar(self, tela, fontes) -> None:
        for botao in self.itens:
            botao.desenhar(tela, fontes)

    def clicado(self, posicao) -> tuple | None:
        for botao in self.itens:
            if botao.contem(posicao):
                return botao.identificador
        return None
