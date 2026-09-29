"""
Roda os experimentos e gera os gráficos em um comando só.

Existe para evitar depender da sintaxe do terminal: o PowerShell que vem
no Windows não aceita `&&` entre comandos.

Uso:  python -m experimentos.tudo
      python -m experimentos.tudo --repeticoes 5000
"""

import sys

from . import executar, graficos


def main() -> None:
    executar.main()
    print()
    graficos.main()


if __name__ == "__main__":
    main()
