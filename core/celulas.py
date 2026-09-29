"""
Tipos de célula do ambiente e seus custos de deslocamento.

Convenção de custo adotada no projeto:
o custo é sempre o de ENTRAR em uma célula. A célula inicial não é cobrada.

    g(vizinho) = g(atual) + custo(vizinho)

Os valores seguem a sugestão do item 2.3.1 do edital.
"""

from dataclasses import dataclass

from . import focos


@dataclass(frozen=True)
class TipoCelula:
    """Descreve uma categoria de célula do ambiente."""

    codigo: str          # caractere usado nos mapas de texto
    nome: str            # nome exibido na legenda e no relatório
    custo: int           # custo para ENTRAR nesta célula
    transponivel: bool   # se o agente pode ocupá-la
    eh_foco: bool = False


# --- Terrenos -------------------------------------------------------------
CALCADA = TipoCelula(".", "Calçada", 1, True)
GRAMA = TipoCelula("g", "Grama", 2, True)
TERRA = TipoCelula("t", "Terreno de difícil acesso", 4, True)
OBSTACULO = TipoCelula("#", "Obstáculo", 0, False)

# --- Células especiais ----------------------------------------------------
# O início fica sobre calçada, portanto custa 1 para entrar.
INICIO = TipoCelula("S", "Início da missão", 1, True)

# Cada tipo de foco vira uma célula própria, todas sobre calçada. Assim
# transformar uma calçada em foco NÃO altera o grafo de busca: mesmo
# custo, mesma transponibilidade. Só muda o que aquela célula representa.
CELULAS_DE_FOCO = {
    tipo.codigo: TipoCelula(tipo.codigo, tipo.nome, CALCADA.custo, True, True)
    for tipo in focos.TODOS
}


TODOS = (CALCADA, GRAMA, TERRA, OBSTACULO, INICIO, *CELULAS_DE_FOCO.values())

POR_CODIGO = {tipo.codigo: tipo for tipo in TODOS}

# Terrenos que aparecem na legenda da interface (exclui início e focos).
TERRENOS = (CALCADA, GRAMA, TERRA, OBSTACULO)

# Menor custo possível de um movimento no ambiente.
# Usado na heurística: h(n) = Manhattan(n, foco) * CUSTO_MINIMO.
# É o que garante a admissibilidade (a prova está em search/heuristica.py).
CUSTO_MINIMO = min(t.custo for t in TODOS if t.transponivel)


def tipo_de(codigo: str) -> TipoCelula:
    """Converte um caractere do mapa no TipoCelula correspondente."""
    try:
        return POR_CODIGO[codigo]
    except KeyError:
        raise ValueError(
            f"Caractere desconhecido no mapa: {codigo!r}. "
            f"Válidos: {sorted(POR_CODIGO)}"
        ) from None
