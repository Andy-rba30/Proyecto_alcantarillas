"""
tests/test_ve7_lote_b_cifras.py
===============================
VE-7, lote B, item B13 (VE5GUI-46, abierto; decision del consultor Fable,
triaje VE-7, 2026-11-20): las magnitudes `D` de M5 y M6 que salian con
`CIFRAS_MAGNITUD` fijo (tres decimales) usan `modelos.cifras_de_dimension`,
la regla del rotulo: 0.90 -> «0.90», 1.0668 -> «1.0668».

Dos caminos: (1) el AST de los dos modulos (toda `Magnitud("D", ...)` lleva
`cifras_de_dimension`), y (2) el paso de V9, construido de verdad, con el
diametro ingles convertido: sus cifras son las de la forma decimal mas corta
del numero, contadas aqui a mano.
"""

import ast
from pathlib import Path

import pytest

from src.modelos import TipoMaterial
from src.modulos import M2_material as M2
from src.modulos import M5_verificaciones as M5
from src.modulos import M6_proteccion as M6
from tests.apoyo.criterios import declarados

RAIZ = Path(__file__).resolve().parents[1]


def _magnitudes_D(ruta: Path):
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
                and nodo.func.id == "Magnitud" and nodo.args
                and isinstance(nodo.args[0], ast.Constant)
                and nodo.args[0].value == "D"):
            yield nodo


@pytest.mark.parametrize("modulo", ["M5_verificaciones", "M6_proteccion"])
def test_toda_magnitud_D_usa_cifras_de_dimension(modulo):
    ruta = RAIZ / "src" / "modulos" / f"{modulo}.py"
    llamadas = list(_magnitudes_D(ruta))
    assert llamadas, modulo
    for nodo in llamadas:
        cifras = next(k.value for k in nodo.keywords if k.arg == "cifras")
        assert (isinstance(cifras, ast.Call)
                and getattr(cifras.func, "id", "") == "cifras_de_dimension"), \
            f"{modulo}, linea {nodo.lineno}"


def _cifras_de_D(verificacion):
    paso = verificacion.paso
    return next(m.cifras for m in paso.sustitucion if m.simbolo == "D")


def test_v9_con_el_diametro_ingles_lleva_sus_cuatro_decimales():
    with declarados({"diametro_de_diseno_concreto":
                     "designado_o_ingles_convertido"}):
        material = M2.catalogo(TipoMaterial.CONCRETO_REFORZADO)
        v = M5.v9_disponibilidad_diametro(D=1.0668, material=material)
    assert _cifras_de_D(v) == 4            # «1.0668»: cuatro decimales


def test_v9_con_el_designado_lleva_dos():
    material = M2.catalogo(TipoMaterial.CONCRETO_REFORZADO)
    v = M5.v9_disponibilidad_diametro(D=0.90, material=material)
    assert _cifras_de_D(v) == 2            # «0.90»


def test_la_clase_hec14_con_el_diametro_ingles():
    clase = M6.clase_hec14_de_la_piedra(d50=0.15, D=1.0668)
    pasos = [p for p in (getattr(clase, "pasos", None) or
                         (getattr(clase, "paso", None),)) if p is not None]
    cifras = [m.cifras for p in pasos for m in p.sustitucion
              if m.simbolo == "D"]
    assert cifras and set(cifras) == {4}
