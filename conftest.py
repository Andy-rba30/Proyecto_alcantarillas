"""
conftest.py
===========
Hace importables los dos arboles que usan los tests:

    src/   -> modulos planos, tal como los nombra el Anexo C de la hoja de ruta
              (`from criterios_adoptados import valor`)
    raiz   -> `from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING`

Sin esto, pytest solo agrega el directorio del test al path y ninguno de los
dos imports funciona.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "src"

for ruta in (RAIZ, SRC):
    if str(ruta) not in sys.path:
        sys.path.insert(0, str(ruta))
