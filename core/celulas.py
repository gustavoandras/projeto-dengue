from dataclasses import dataclass

from . import focos


@dataclass(frozen=True)
class TipoCelula:

    codigo: str
    nome: str
    custo: int
    transponivel: bool
    eh_foco: bool = False


CALCADA = TipoCelula(".", "Calçada", 1, True)
GRAMA = TipoCelula("g", "Grama", 2, True)
TERRA = TipoCelula("t", "Terreno de difícil acesso", 4, True)
OBSTACULO = TipoCelula("#", "Obstáculo", 0, False)


INICIO = TipoCelula("S", "Início da missão", 1, True)


CELULAS_DE_FOCO = {
    tipo.codigo: TipoCelula(tipo.codigo, tipo.nome, CALCADA.custo, True, True)
    for tipo in focos.TODOS
}


TODOS = (CALCADA, GRAMA, TERRA, OBSTACULO, INICIO, *CELULAS_DE_FOCO.values())

POR_CODIGO = {tipo.codigo: tipo for tipo in TODOS}


TERRENOS = (CALCADA, GRAMA, TERRA, OBSTACULO)


CUSTO_MINIMO = min(t.custo for t in TODOS if t.transponivel)


def tipo_de(codigo: str) -> TipoCelula:
    try:
        return POR_CODIGO[codigo]
    except KeyError:
        raise ValueError(
            f"Caractere desconhecido no mapa: {codigo!r}. "
            f"Válidos: {sorted(POR_CODIGO)}"
        ) from None
