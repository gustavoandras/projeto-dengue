"""
Estrutura comum devolvida por todos os algoritmos de busca.

A existência deste módulo é o que permite comparar os quatro algoritmos
na mesma tabela: todos preenchem exatamente os mesmos campos, com as
mesmas definições.

Definição das métricas (usada igualmente nos 4 algoritmos)
----------------------------------------------------------
gerados     sucessores criados, INCLUINDO os descartados por já terem
            sido visitados ou por já estarem na fronteira.
expandidos  nós retirados da fronteira e cujos sucessores foram gerados.
            O nó objetivo conta como expandido quando é retirado.
fronteira_maxima  maior tamanho que a fronteira atingiu durante a busca.

Separação de tempos (item 2.4.3 do edital)
------------------------------------------
`tempo_busca` mede SOMENTE a execução do algoritmo. O tempo de animação
do agente na tela é medido à parte, pela interface, e nunca entra aqui.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.grade import Estado, Grade


@dataclass
class Resultado:
    """Saída de uma execução de busca."""

    algoritmo: str
    encontrou: bool
    caminho: list[Estado] = field(default_factory=list)
    custo: int = 0
    expandidos: int = 0
    gerados: int = 0
    fronteira_maxima: int = 0
    tempo_busca: float = 0.0          # segundos
    # Ordem em que os estados foram expandidos. A interface usa esta lista
    # para animar a exploração — ela não influencia a busca em nada.
    ordem_exploracao: list[Estado] = field(default_factory=list)

    @property
    def passos(self) -> int:
        """Número de movimentos (o estado inicial não é um passo)."""
        return max(0, len(self.caminho) - 1)

    def __str__(self) -> str:
        if not self.encontrou:
            return f"{self.algoritmo}: sem solução"
        return (
            f"{self.algoritmo}: {self.passos} passos, custo {self.custo}, "
            f"expandidos {self.expandidos}, gerados {self.gerados}, "
            f"fronteira máx. {self.fronteira_maxima}, "
            f"{self.tempo_busca * 1000:.3f} ms"
        )


def reconstruir_caminho(
    anterior: dict[Estado, Estado | None], destino: Estado
) -> list[Estado]:
    """Percorre os ponteiros de pai do objetivo até a origem e inverte."""
    caminho: list[Estado] = []
    no: Estado | None = destino
    while no is not None:
        caminho.append(no)
        no = anterior[no]
    caminho.reverse()
    return caminho


def validar_caminho(grade: Grade, caminho: list[Estado]) -> None:
    """
    Confere que o caminho é realmente percorrível.

    Usado nos testes: garante que nenhum algoritmo "teletransportou" o
    agente ou atravessou um obstáculo.
    """
    if not caminho:
        raise ValueError("caminho vazio")
    if caminho[0] != grade.inicio:
        raise ValueError(f"caminho não começa no início: {caminho[0]}")
    if caminho[-1] != grade.foco:
        raise ValueError(f"caminho não termina no foco: {caminho[-1]}")

    for anterior, atual in zip(caminho, caminho[1:]):
        if not grade.transponivel(atual):
            raise ValueError(f"caminho passa por célula inválida: {atual}")
        distancia = abs(anterior[0] - atual[0]) + abs(anterior[1] - atual[1])
        if distancia != 1:
            raise ValueError(
                f"salto inválido de {anterior} para {atual} "
                "(só são permitidos movimentos ortogonais de 1 célula)"
            )
