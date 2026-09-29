# Agente de Combate à Dengue

Projeto nº 1 — Inteligência Artificial · BCC · UTFPR-PG

## Como rodar

```bash
pip install pygame-ce
python main.py
```

## Organização

```
core/          modelagem: grade, custos, focos, função sucessor, objetivo
search/        os 4 algoritmos — NÃO importam pygame
jogo/          interface: tema, desenho, botões, jogador, animação
ferramentas/   validação, testes e geração de figuras
resultados/    capturas e CSV das execuções manuais
```

A separação entre `search/` e `jogo/` é o que permite medir o tempo do
algoritmo separadamente do tempo de animação, como exige o item 2.4.3.

