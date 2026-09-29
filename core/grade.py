"""
Grade: a representação computacional do ambiente.

O ambiente é uma matriz bidimensional, mas os algoritmos de busca a tratam
como um GRAFO IMPLÍCITO (item 2.3.2 do edital): nenhum grafo explícito é
construído — os sucessores são gerados sob demanda por `sucessores()`.

Formulação do problema de busca:
    Estado inicial .. self.inicio          (linha, coluna) do 'S'
    Estado objetivo. self.objetivo         o foco SELECIONADO para a missão
    Estados ........ toda célula transponível
    Ações .......... cima, direita, baixo, esquerda
    Função sucessor. sucessores(estado)
    Teste objetivo.. eh_objetivo(estado)
    Custo do caminho soma dos custos das células ENTRADAS

Vários focos
------------
O cenário pode conter mais de um foco de dengue (item 2.2 lista pneus,
vasos, garrafas, baldes, caixas-d'água, calhas). Todos ficam em
`self.focos`, mas apenas UM é o objetivo da missão por vez — o
"foco selecionado" a que o edital se refere no item 2.3.2. Usuário e
agente sempre resolvem a mesma instância, com o mesmo objetivo.
"""

from __future__ import annotations

from . import celulas, focos

# Estado = (linha, coluna)
Estado = tuple[int, int]

# Ordem FIXA de geração dos sucessores, idêntica nos quatro algoritmos.
# DFS e Busca Gulosa dependem inteiramente desta ordem: alterá-la muda o
# caminho encontrado. Precisa estar documentada na Seção 4 do relatório.
ACOES: tuple[tuple[str, int, int], ...] = (
    ("Cima", -1, 0),
    ("Direita", 0, 1),
    ("Baixo", 1, 0),
    ("Esquerda", 0, -1),
)


class Grade:
    """Matriz de células com as operações do espaço de estados."""

    def __init__(self, mapa_texto: str, nome: str = "sem nome",
                 codigo_foco_padrao: str | None = None):
        self.nome = nome

        linhas_texto = mapa_texto.strip().splitlines()
        if not linhas_texto:
            raise ValueError(f"Mapa vazio em {nome!r}")

        larguras = {len(l) for l in linhas_texto}
        if len(larguras) != 1:
            detalhe = ", ".join(
                f"linha {i}: {len(l)}" for i, l in enumerate(linhas_texto)
            )
            raise ValueError(f"Mapa {nome!r} não é retangular ({detalhe})")

        self.linhas = len(linhas_texto)
        self.colunas = larguras.pop()

        # matriz[l][c] -> TipoCelula
        self.matriz: list[list[celulas.TipoCelula]] = [
            [celulas.tipo_de(ch) for ch in linha] for linha in linhas_texto
        ]

        self.inicio = self._localizar_inicio()
        self.focos: dict[Estado, focos.TipoFoco] = self._localizar_focos()
        self.objetivo: Estado = self._escolher_padrao(codigo_foco_padrao)

    # -- construção --------------------------------------------------------

    def _localizar_inicio(self) -> Estado:
        encontrados = [
            (l, c)
            for l in range(self.linhas)
            for c in range(self.colunas)
            if self.matriz[l][c] is celulas.INICIO
        ]
        if len(encontrados) != 1:
            raise ValueError(
                f"Mapa {nome_seguro(self.nome)} deve ter exatamente um "
                f"início 'S', encontrados: {len(encontrados)}"
            )
        return encontrados[0]

    def _localizar_focos(self) -> dict[Estado, focos.TipoFoco]:
        encontrados = {
            (l, c): focos.tipo_de(self.matriz[l][c].codigo)
            for l in range(self.linhas)
            for c in range(self.colunas)
            if self.matriz[l][c].eh_foco
        }
        if not encontrados:
            raise ValueError(
                f"Mapa {nome_seguro(self.nome)} não tem nenhum foco de dengue"
            )
        return encontrados

    def _escolher_padrao(self, codigo: str | None) -> Estado:
        if codigo is not None:
            for posicao, tipo in self.focos.items():
                if tipo.codigo == codigo:
                    return posicao
            raise ValueError(
                f"Mapa {nome_seguro(self.nome)} não contém o foco padrão "
                f"{codigo!r}. Presentes: "
                f"{sorted(t.codigo for t in self.focos.values())}"
            )
        # sem padrão declarado: o primeiro em ordem de leitura
        return sorted(self.focos)[0]

    # -- objetivo ----------------------------------------------------------

    def definir_objetivo(self, posicao: Estado) -> None:
        """Seleciona qual foco será o objetivo da missão."""
        if posicao not in self.focos:
            raise ValueError(f"{posicao} não é um foco deste cenário")
        self.objetivo = posicao

    @property
    def foco(self) -> Estado:
        """Apelido para o objetivo atual (usado pelos algoritmos)."""
        return self.objetivo

    @property
    def tipo_do_objetivo(self) -> focos.TipoFoco:
        return self.focos[self.objetivo]

    def focos_ordenados(self) -> list[tuple[Estado, focos.TipoFoco]]:
        return sorted(self.focos.items())

    # -- consultas ---------------------------------------------------------

    def tipo(self, estado: Estado) -> celulas.TipoCelula:
        linha, coluna = estado
        return self.matriz[linha][coluna]

    def dentro_dos_limites(self, estado: Estado) -> bool:
        linha, coluna = estado
        return 0 <= linha < self.linhas and 0 <= coluna < self.colunas

    def transponivel(self, estado: Estado) -> bool:
        """Movimentos para fora da matriz ou para obstáculos são proibidos."""
        return self.dentro_dos_limites(estado) and self.tipo(estado).transponivel

    def custo(self, estado: Estado) -> int:
        """Custo de ENTRAR na célula (a célula inicial nunca é cobrada)."""
        return self.tipo(estado).custo

    # -- espaço de estados -------------------------------------------------

    def sucessores(self, estado: Estado) -> list[tuple[Estado, int]]:
        """
        Função sucessor: gera dinamicamente os vizinhos válidos.

        Retorna [(novo_estado, custo_para_entrar), ...] na ordem fixa de ACOES.
        É isto que torna a matriz um grafo implícito: nenhuma lista de
        arestas é construída previamente.
        """
        linha, coluna = estado
        resultado = []
        for _nome, dl, dc in ACOES:
            vizinho = (linha + dl, coluna + dc)
            if self.transponivel(vizinho):
                resultado.append((vizinho, self.custo(vizinho)))
        return resultado

    def eh_objetivo(self, estado: Estado) -> bool:
        """Teste de objetivo: o estado atual é o foco selecionado?"""
        return estado == self.objetivo

    def custo_do_caminho(self, caminho: list[Estado]) -> int:
        """Soma dos custos de todas as células entradas (exclui a inicial)."""
        return sum(self.custo(e) for e in caminho[1:])

    # -- utilidades --------------------------------------------------------

    def estados_validos(self) -> list[Estado]:
        return [
            (l, c)
            for l in range(self.linhas)
            for c in range(self.colunas)
            if self.matriz[l][c].transponivel
        ]

    def __repr__(self) -> str:
        return (
            f"Grade({self.nome!r}, {self.linhas}x{self.colunas}, "
            f"inicio={self.inicio}, objetivo={self.objetivo}, "
            f"focos={len(self.focos)})"
        )


def nome_seguro(nome: str) -> str:
    return repr(nome)
