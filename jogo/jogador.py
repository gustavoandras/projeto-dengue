from __future__ import annotations

from time import perf_counter

from core.grade import ACOES, Estado, Grade


class Jogador:

    def __init__(self, grade: Grade):
        self.grade = grade
        self.posicao: Estado = grade.inicio
        self.caminho: list[Estado] = [grade.inicio]
        self.custo: int = 0
        self.passos: int = 0
        self.movimentos_bloqueados: int = 0
        self._inicio_relogio: float | None = None
        self._tempo_final: float | None = None

    def iniciar_cronometro(self) -> None:
        self._inicio_relogio = perf_counter()
        self._tempo_final = None

    @property
    def tempo(self) -> float:
        if self._inicio_relogio is None:
            return 0.0
        if self._tempo_final is not None:
            return self._tempo_final
        return perf_counter() - self._inicio_relogio

    @property
    def chegou(self) -> bool:
        return self.grade.eh_objetivo(self.posicao)

    def mover(self, delta_linha: int, delta_coluna: int) -> bool:
        if self.chegou:
            return False

        destino = (
            self.posicao[0] + delta_linha,
            self.posicao[1] + delta_coluna,
        )

        if not self.grade.transponivel(destino):
            self.movimentos_bloqueados += 1
            return False

        self.posicao = destino
        self.caminho.append(destino)
        self.passos += 1
        self.custo += self.grade.custo(destino)

        if self.chegou and self._inicio_relogio is not None:
            self._tempo_final = perf_counter() - self._inicio_relogio

        return True

    def mover_por_nome(self, nome_acao: str) -> bool:
        for nome, dl, dc in ACOES:
            if nome == nome_acao:
                return self.mover(dl, dc)
        raise ValueError(f"Ação desconhecida: {nome_acao!r}")

    def resumo(self) -> dict:
        return {
            "passos": self.passos,
            "custo": self.custo,
            "tempo": self.tempo,
            "caminho": list(self.caminho),
            "movimentos_bloqueados": self.movimentos_bloqueados,
        }
