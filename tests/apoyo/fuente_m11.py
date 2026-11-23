"""
tests/apoyo/fuente_m11.py
=========================
D3 partio `src/modulos/M11_reporte.py` en el subpaquete
`src/modulos/M11_reporte/`. Las guardias por AST sobre M11 («no hace
aritmetica sobre magnitudes», «de los catalogos solo hace lecturas
ESTATICAS», ...) tienen que barrer TODO el subpaquete, no solo `__init__.py`:
este apoyo da la fuente y el arbol de todos sus archivos, juntos, para que
cada guardia conserve su regla sin aflojarla.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List

RAIZ = Path(__file__).resolve().parents[2]
DIR_M11 = RAIZ / "src" / "modulos" / "M11_reporte"


def rutas_m11() -> List[Path]:
    """Todos los archivos del subpaquete, en orden alfabetico."""
    rutas = sorted(DIR_M11.glob("*.py"))
    assert rutas, f"el subpaquete {DIR_M11} no tiene archivos"
    return rutas


def fuente_m11() -> str:
    """La fuente de todo el subpaquete, concatenada."""
    return "\n".join(r.read_text(encoding="utf-8-sig") for r in rutas_m11())


def arbol_m11() -> ast.Module:
    """Un solo `ast.Module` con el cuerpo de todos los archivos del subpaquete."""
    return ast.Module(
        body=[n for r in rutas_m11()
              for n in ast.parse(r.read_text(encoding="utf-8-sig"),
                                 filename=r.name).body],
        type_ignores=[])
