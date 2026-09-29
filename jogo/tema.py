"""
Paleta de cores e medidas da interface.

A janela é redimensionável: as medidas aqui são mínimos e proporções,
não posições fixas. O layout é recalculado a cada mudança de tamanho.

Escolhas pensadas no público-alvo do bônus (item 2.11): cores saturadas,
alto contraste entre terrenos e formas grandes o suficiente para leitura
fácil. Nada de texturas ou sprites — tudo é desenhado com primitivas.
"""

from core import celulas

# --- Janela ----------------------------------------------------------------
LARGURA_MINIMA = 1024
ALTURA_MINIMA = 640
# fração da área de trabalho usada ao abrir o jogo
FRACAO_TELA = 0.94
FPS = 60

LARGURA_PAINEL = 320       # painel lateral de controles e métricas
MARGEM = 18
ESPACO_ENTRE_GRADES = 18
ALTURA_CABECALHO = 62
ALTURA_RODAPE = 30
FOLGA_SUBTITULO = 10   # respiro entre o título e a linha do cenário
# altura mínima para valer a pena desenhar a faixa inferior
FAIXA_MINIMA = 110
FAIXA_MAXIMA = 150

# --- Cores base ------------------------------------------------------------
FUNDO = (21, 26, 36)
FUNDO_PAINEL = (30, 37, 51)
BORDA_PAINEL = (52, 63, 84)

TEXTO = (232, 237, 245)
TEXTO_SUAVE = (196, 205, 220)
TEXTO_FRACO = (146, 159, 182)
TEXTO_DESTAQUE = (255, 210, 92)

# --- Botões ----------------------------------------------------------------
BOTAO = (41, 50, 68)
BOTAO_HOVER = (55, 67, 90)
BOTAO_ATIVO = (52, 78, 120)
BOTAO_ATIVO_BORDA = (104, 166, 255)
BOTAO_DESABILITADO = (34, 40, 53)
BOTAO_PRINCIPAL = (245, 196, 66)
BOTAO_PRINCIPAL_HOVER = (255, 214, 96)
BOTAO_PRINCIPAL_TEXTO = (40, 32, 10)

# --- Terrenos --------------------------------------------------------------
COR_TERRENO = {
    celulas.CALCADA.codigo: (206, 209, 214),   # cinza claro
    celulas.GRAMA.codigo: (106, 176, 88),      # verde
    celulas.TERRA.codigo: (166, 118, 74),      # marrom
    celulas.OBSTACULO.codigo: (58, 50, 46),    # muro escuro
    celulas.INICIO.codigo: (206, 209, 214),    # início fica sobre calçada
}
# focos também ficam sobre calçada
for _codigo in celulas.CELULAS_DE_FOCO:
    COR_TERRENO[_codigo] = (206, 209, 214)

# Detalhes desenhados por cima do terreno (tufos, pedras, tijolos)
COR_DETALHE = {
    celulas.CALCADA.codigo: (186, 190, 197),
    celulas.GRAMA.codigo: (76, 142, 62),
    celulas.TERRA.codigo: (137, 94, 57),
    celulas.OBSTACULO.codigo: (44, 38, 35),
}

# --- Personagens e marcadores ---------------------------------------------
COR_USUARIO = (64, 138, 240)          # azul
COR_USUARIO_BORDA = (28, 84, 168)
COR_AGENTE = (238, 92, 88)            # vermelho
COR_AGENTE_BORDA = (164, 44, 40)
COR_MARCA_INICIO = (128, 138, 156)   # cantos discretos do ponto de partida
COR_FOCO = (245, 196, 66)             # destaque do foco selecionado
COR_FOCO_BORDA = (176, 124, 16)
COR_AGUA = (86, 170, 226)             # água acumulada dentro do foco
COR_FOCO_INATIVO = (150, 156, 166)    # focos não selecionados

# --- Sobreposições da busca -----------------------------------------------
COR_EXPLORADO = (118, 178, 232, 120)  # estados explorados pelo algoritmo
COR_CAMINHO = (255, 214, 92, 170)     # caminho final encontrado
COR_RASTRO_USUARIO = (64, 138, 240, 110)

# --- Cabeçalhos das duas grades -------------------------------------------
COR_TITULO_USUARIO = (104, 166, 255)
COR_TITULO_AGENTE = (255, 128, 124)
COR_VENCEDOR = (126, 214, 130)


def cor_terreno(codigo: str):
    return COR_TERRENO[codigo]


def cor_detalhe(codigo: str):
    return COR_DETALHE.get(codigo, COR_TERRENO[codigo])
