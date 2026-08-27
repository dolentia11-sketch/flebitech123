"""Entry point para `python -m producto.engines.db <subcomando>`.

Delega en `_main()` de `__init__.py`. Existe porque Python, al ejecutar un
paquete con `-m`, busca este archivo — no dispara el bloque
`if __name__ == "__main__"` del `__init__.py`.
"""
import sys

from . import _main

if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
