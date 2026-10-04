from __future__ import annotations

from . import celulas, focos


Estado = tuple[int, int]


ACOES: tuple[tuple[str, int, int], ...] = (
    ("Cima", -1, 0),
    ("Direita", 0, 1),
    ("Baixo", 1, 0),
    ("Esquerda", 0, -1),
)


class Grade:

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

        self.matriz: list[list[celulas.TipoCelula]] = [
            [celulas.tipo_de(ch) for ch in linha] for linha in linhas_texto
        ]

        self.inicio = self._localizar_inicio()
        self.focos: dict[Estado, focos.TipoFoco] = self._localizar_focos()
        self.objetivo: Estado = self._escolher_padrao(codigo_foco_padrao)

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

        return sorted(self.focos)[0]

    def definir_objetivo(self, posicao: Estado) -> None:
        if posicao not in self.focos:
            raise ValueError(f"{posicao} não é um foco deste cenário")
        self.objetivo = posicao

    @property
    def foco(self) -> Estado:
        return self.objetivo

    @property
    def tipo_do_objetivo(self) -> focos.TipoFoco:
        return self.focos[self.objetivo]

    def focos_ordenados(self) -> list[tuple[Estado, focos.TipoFoco]]:
        return sorted(self.focos.items())

    def tipo(self, estado: Estado) -> celulas.TipoCelula:
        linha, coluna = estado
        return self.matriz[linha][coluna]

    def dentro_dos_limites(self, estado: Estado) -> bool:
        linha, coluna = estado
        return 0 <= linha < self.linhas and 0 <= coluna < self.colunas

    def transponivel(self, estado: Estado) -> bool:
        return self.dentro_dos_limites(estado) and self.tipo(estado).transponivel

    def custo(self, estado: Estado) -> int:
        return self.tipo(estado).custo

    def sucessores(self, estado: Estado) -> list[tuple[Estado, int]]:
        linha, coluna = estado
        resultado = []
        for _nome, dl, dc in ACOES:
            vizinho = (linha + dl, coluna + dc)
            if self.transponivel(vizinho):
                resultado.append((vizinho, self.custo(vizinho)))
        return resultado

    def eh_objetivo(self, estado: Estado) -> bool:
        return estado == self.objetivo

    def custo_do_caminho(self, caminho: list[Estado]) -> int:
        return sum(self.custo(e) for e in caminho[1:])

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
