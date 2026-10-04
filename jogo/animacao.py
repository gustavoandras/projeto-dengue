from __future__ import annotations

from enum import Enum, auto

from core.grade import Estado
from search.resultado import Resultado


class Fase(Enum):
    EXPLORANDO = auto()
    PERCORRENDO = auto()
    CONCLUIDO = auto()


class AnimacaoAgente:

    ESTADOS_POR_SEGUNDO = 140.0
    PASSOS_POR_SEGUNDO = 7.0

    def __init__(self, resultado: Resultado, grade):
        self.resultado = resultado
        self.grade = grade
        self.fase = Fase.EXPLORANDO
        self._explorados_revelados = 0.0
        self._passo_atual = 0.0
        self.posicao = grade.inicio

    @property
    def estados_revelados(self) -> list[Estado]:
        return self.resultado.ordem_exploracao[: int(self._explorados_revelados)]

    @property
    def caminho_percorrido(self) -> list[Estado]:
        if self.fase is Fase.EXPLORANDO:
            return []
        return self.resultado.caminho[: int(self._passo_atual) + 1]

    @property
    def passos_dados(self) -> int:
        if self.fase is Fase.EXPLORANDO:
            return 0
        return int(self._passo_atual)

    @property
    def custo_parcial(self) -> int:
        return self.grade.custo_do_caminho(self.caminho_percorrido)

    @property
    def chegou(self) -> bool:
        return self.fase is Fase.CONCLUIDO

    def atualizar(self, dt: float) -> None:
        if self.fase is Fase.EXPLORANDO:
            self._explorados_revelados += self.ESTADOS_POR_SEGUNDO * dt
            if self._explorados_revelados >= len(self.resultado.ordem_exploracao):
                self._explorados_revelados = len(self.resultado.ordem_exploracao)
                if self.resultado.encontrou:
                    self.fase = Fase.PERCORRENDO
                else:
                    self.fase = Fase.CONCLUIDO

        elif self.fase is Fase.PERCORRENDO:
            self._passo_atual += self.PASSOS_POR_SEGUNDO * dt
            ultimo = len(self.resultado.caminho) - 1
            if self._passo_atual >= ultimo:
                self._passo_atual = ultimo
                self.fase = Fase.CONCLUIDO
            self.posicao = self.resultado.caminho[int(self._passo_atual)]

    def concluir_imediatamente(self) -> None:
        self._explorados_revelados = len(self.resultado.ordem_exploracao)
        if self.resultado.encontrou:
            self._passo_atual = len(self.resultado.caminho) - 1
            self.posicao = self.resultado.caminho[-1]
        self.fase = Fase.CONCLUIDO
