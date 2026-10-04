import sys

from . import executar, graficos


def main() -> None:
    executar.main()
    print()
    graficos.main()


if __name__ == "__main__":
    main()
