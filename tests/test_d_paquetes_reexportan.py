# -*- coding: utf-8 -*-
"""
tests/test_d_paquetes_reexportan.py
===================================
D1 y D3 partieron `M9_cabezal.py` y `M11_reporte.py` en subpaquetes que
REEXPORTAN en su `__init__.py` los nombres del archivo unico que reemplazan
(`CLAUDE.md`, «Subpaquetes»), y cambian la clase del paquete para que un
`monkeypatch.setattr(M9, ...)` llegue al submodulo dueño del nombre. Ningun
test fijaba ni el invariante ni el mecanismo, y el primer cambio posterior a
la particion ya rompio el primero (`TOL_REL_SESGO_CONTRASTE`, importado en
`estabilidad_cargas` y no en el paquete) y el `undo` de `monkeypatch.delattr`
no devolvia el nombre al submodulo (auditoria del 2026-11-24, hallazgo N4).
"""
from __future__ import annotations

import types

import pytest

from src.modulos import M9_cabezal as M9
from src.modulos import M11_reporte as M11

PAQUETES = ((M9, M9._SUBMODULOS_M9), (M11, M11._SUBMODULOS_M11))


@pytest.mark.parametrize("paquete, submodulos", PAQUETES,
                         ids=["M9_cabezal", "M11_reporte"])
def test_el_paquete_reexporta_todo_nombre_de_sus_submodulos(paquete, submodulos):
    """
    Todo nombre de nivel superior de un submodulo (salvo los dunder y los
    modulos importados) se lee en el paquete y es el MISMO objeto: lo que
    `from src.modulos import M9_cabezal as M9; M9.x` daba con el archivo unico.
    """
    faltan, distintos = [], []
    for submodulo in submodulos:
        corto = submodulo.__name__.rsplit(".", 1)[1]
        for nombre, valor in vars(submodulo).items():
            if nombre.startswith("__") or isinstance(valor, types.ModuleType):
                continue
            if not hasattr(paquete, nombre):
                faltan.append(f"{corto}.{nombre}")
            elif getattr(paquete, nombre) is not valor:
                distintos.append(f"{corto}.{nombre}")
    assert faltan == [], f"el paquete no reexporta: {faltan}"
    assert distintos == [], f"el paquete reexporta otro objeto: {distintos}"


@pytest.mark.parametrize("paquete, submodulos", PAQUETES,
                         ids=["M9_cabezal", "M11_reporte"])
def test_monkeypatch_sobre_el_paquete_llega_al_submodulo_y_se_deshace(
        paquete, submodulos):
    """
    `setattr` sobre el paquete llega a todo submodulo que tenga el nombre;
    `delattr` lo borra de todos; y el `undo` de los dos deja paquete y
    submodulos como estaban, tambien tras `delattr`.
    """
    nombre = next(n for n in ("TOL_ANGULO_CUNA", "ARCHIVO_CRITERIOS")
                  if hasattr(paquete, n))
    duenos = [s for s in submodulos if nombre in vars(s)]
    assert duenos, f"ningun submodulo de {paquete.__name__} tiene {nombre}"
    original = getattr(paquete, nombre)
    centinela = object()

    mp = pytest.MonkeyPatch()
    mp.setattr(paquete, nombre, centinela)
    assert all(vars(s)[nombre] is centinela for s in duenos)
    mp.undo()
    assert getattr(paquete, nombre) is original
    assert all(vars(s)[nombre] is original for s in duenos)

    mp = pytest.MonkeyPatch()
    mp.delattr(paquete, nombre)
    assert not hasattr(paquete, nombre)
    assert all(nombre not in vars(s) for s in duenos)
    mp.undo()
    assert getattr(paquete, nombre) is original
    assert all(vars(s)[nombre] is original for s in duenos), (
        "el undo de delattr no devolvio el nombre al submodulo dueño")
