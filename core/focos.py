"""
Tipos de foco de dengue e o conteúdo educacional de cada um.

Atende ao item 2.4.4 do edital ("mensagem educativa relacionada ao
elemento encontrado") e à Seção 6 do relatório, que pede os tipos de
foco utilizados no ambiente e a informação educativa de CADA UM deles.

Os tipos aqui foram escolhidos entre os criadouros listados no item 2.2:
pneus, vasos e pratos de plantas, garrafas, baldes, recipientes
destampados, caixas-d'água mal fechadas e calhas.

ATENÇÃO — Seção 6 do relatório
------------------------------
A grade de avaliação exige "uso de fontes confiáveis". As orientações
abaixo seguem as recomendações usuais de prevenção, mas as REFERÊNCIAS
ainda precisam ser levantadas e citadas em ABNT (Ministério da Saúde,
Fiocruz ou secretaria estadual/municipal de saúde).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TipoFoco:
    """Um criadouro possível do Aedes aegypti."""

    codigo: str        # caractere usado nos mapas
    nome: str          # nome exibido na interface
    dica: str          # rótulo curto para os botões de seleção
    mensagem: str      # orientação educativa mostrada ao alcançar o foco


PNEU = TipoFoco(
    codigo="P",
    nome="Pneu com água acumulada",
    dica="Pneu",
    mensagem=(
        "Pneus guardados ao ar livre acumulam água da chuva e viram "
        "criadouro do mosquito. Guarde-os em local coberto, fure-os para "
        "a água escorrer ou leve-os a um ponto de coleta."
    ),
)

VASO = TipoFoco(
    codigo="V",
    nome="Prato de vaso de planta com água",
    dica="Vaso",
    mensagem=(
        "A água parada no pratinho embaixo do vaso é um dos criadouros "
        "mais comuns dentro de casa. Encha o prato com areia até a borda "
        "ou lave-o com escova pelo menos uma vez por semana."
    ),
)

CAIXA_DAGUA = TipoFoco(
    codigo="C",
    nome="Caixa d'água destampada",
    dica="Caixa d'água",
    mensagem=(
        "Caixas d'água, tonéis e cisternas sem tampa deixam o mosquito "
        "entrar e pôr ovos. Mantenha sempre bem tampados e verifique se "
        "a tampa não está rachada ou fora do lugar."
    ),
)

GARRAFA = TipoFoco(
    codigo="R",
    nome="Garrafas e recipientes destampados",
    dica="Garrafas",
    mensagem=(
        "Garrafas, latas e potes jogados no quintal juntam água da chuva. "
        "Guarde as garrafas sempre de boca para baixo e descarte o que "
        "não for usar em saco fechado."
    ),
)

BALDE = TipoFoco(
    codigo="B",
    nome="Balde virado para cima",
    dica="Balde",
    mensagem=(
        "Baldes, bacias e regadores deixados de boca para cima acumulam "
        "água sem ninguém perceber. Guarde-os sempre virados para baixo e "
        "em local coberto."
    ),
)

CALHA = TipoFoco(
    codigo="L",
    nome="Calha entupida",
    dica="Calha",
    mensagem=(
        "Folhas e sujeira entopem a calha e formam poças que duram dias. "
        "Limpe as calhas com regularidade para que a água escoe sem "
        "empoçar."
    ),
)


TODOS: tuple[TipoFoco, ...] = (
    PNEU, VASO, CAIXA_DAGUA, GARRAFA, BALDE, CALHA
)

POR_CODIGO = {foco.codigo: foco for foco in TODOS}

CODIGOS = frozenset(POR_CODIGO)


def tipo_de(codigo: str) -> TipoFoco:
    try:
        return POR_CODIGO[codigo]
    except KeyError:
        raise ValueError(
            f"Código de foco desconhecido: {codigo!r}. "
            f"Válidos: {sorted(POR_CODIGO)}"
        ) from None
