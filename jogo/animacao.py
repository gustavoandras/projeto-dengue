"""
Animação do agente inteligente.

PONTO CENTRAL DO ITEM 2.4.3 DO EDITAL
-------------------------------------
A busca já terminou antes de esta classe existir. O algoritmo roda de uma
vez só, em microssegundos, e devolve um Resultado contendo:

  - `ordem_exploracao`: os estados na ordem em que foram expandidos;
  - `caminho`: a solução encontrada.

Esta classe apenas REPRODUZ essas duas listas ao longo do tempo. O
`tempo_busca` gravado no Resultado é o tempo do algoritmo; o tempo que a
animação leva na tela não é medido nem reportado como desempenho.

Fases
-----
  1. EXPLORANDO — revela progressivamente os estados expandidos, para o
     usuário ver o algoritmo "pensando";
  2. PERCORRENDO — o agente caminha pela solução encontrada;
  3. CONCLUIDO — chegou ao foco.
"""

from __future__ import annotations

from enum import Enum, auto

from core.grade import Estado
from search.resultado import Resultado


class Fase(Enum):
    EXPLORANDO = auto()
    PERCORRENDO = auto()
    CONCLUIDO = auto()


class AnimacaoAgente:
    """Reproduz visualmente um Resultado já calculado."""

    # Ritmo da animação. Só afeta a apresentação, nunca as métricas.
    ESTADOS_POR_SEGUNDO = 140.0     # revelação dos estados explorados
    PASSOS_POR_SEGUNDO = 7.0        # caminhada do agente

    def __init__(self, resultado: Resultado, grade):
        self.resultado = resultado
        self.grade = grade
        self.fase = Fase.EXPLORANDO
        self._explorados_revelados = 0.0
        self._passo_atual = 0.0
        self.posicao = grade.inicio

    # -- consulta ----------------------------------------------------------

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
        """Custo acumulado até onde o agente já caminhou."""
        return self.grade.custo_do_caminho(self.caminho_percorrido)

    @property
    def chegou(self) -> bool:
        return self.fase is Fase.CONCLUIDO

    # -- atualização -------------------------------------------------------

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
        """Pula a animação (tecla de atalho durante a demonstração)."""
        self._explorados_revelados = len(self.resultado.ordem_exploracao)
        if self.resultado.encontrou:
            self._passo_atual = len(self.resultado.caminho) - 1
            self.posicao = self.resultado.caminho[-1]
        self.fase = Fase.CONCLUIDO
