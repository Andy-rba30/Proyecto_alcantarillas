"""
tests/test_ve3_v3_velocidad_de_salida.py
========================================
VE-3, parte 1 (ficha VE2-04, decision del dueño del 2026-11-17): bajo
control de SALIDA, V3 juzga la MAYOR de dos velocidades, la del tirante
normal de n minimo (`V_erosion`) y la de la seccion de salida
(`ResultadoHidraulico.V_salida`, HDS-5 num. 3.1.6, pag. impresa 3.18).

Por que: la Tabla Nº 10 del Manual de Hidrologia limita «la velocidad» del
flujo en el conducto (texto que la introduce, num. 4.1.1.3.6, pag. impresa
76: «Se debe tener en cuenta la velocidad, parametro que es necesario
verificar de tal manera que se encuentre dentro de un rango, cuyos limites
se describen a continuacion»), sin restringirla al tirante normal. Bajo
control de salida, en pendiente suave con salida libre, la lamina baja
hacia la salida y la velocidad de la seccion de salida supera a la normal:
la del caso de la ficha (Ø 0.90 m, Q = 0.3 m3/s, S = 0.001, L = 20 m,
TW = 0, concreto) es 1.508 m/s contra 1.107 m/s del tirante normal.

LO QUE NO CAMBIA, y esta fijado: bajo control de ENTRADA V3 sigue con
`V_erosion`; con S = 0 sigue con `V_salida` (T-2); y bajo control de salida
con la salida mas lenta que el tirante normal (salida ahogada, o un barril
que acelera aguas abajo) sigue con `V_erosion`.

SE ESCRIBIO EN ROJO PRIMERO, contra 3a65e30: fallaban los que piden
`V_salida` bajo control de salida con S > 0 y el de la salida que falta.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from src.modelos import (ControlGobernante, MetodoNoEvaluableError,
                         SeccionCircular, TipoMaterial)
from src.modulos import M4_control as M4
from src.modulos import M5_verificaciones as M5
from src.modulos.M2_material import catalogo
from tests.apoyo.aproximacion import REL_TRANSPORTE

D_FICHA = 0.90
L_FICHA = 20.0


def _resultado(Q, S, TW):
    material = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    return material, M4.resolver_control(
        seccion=SeccionCircular(D_FICHA), Q=Q, S=S, L=L_FICHA, TW=TW,
        material=material)


def test_bajo_control_de_salida_v3_juzga_la_velocidad_de_salida_si_es_mayor():
    """El caso de la ficha VE2-04: 1.508 m/s de la salida, no 1.107."""
    material, r = _resultado(0.3, 0.001, 0.0)
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.V_salida.valor > r.V_erosion
    v = M5._velocidad_de_v3(r)
    assert v.simbolo == "V_salida"
    assert v.valor == pytest.approx(r.V_salida.valor, rel=REL_TRANSPORTE)
    verif = M5.v3_velocidad_maxima(material=material, resultado=r)
    assert verif.valor_obtenido == pytest.approx(r.V_salida.valor,
                                                 rel=REL_TRANSPORTE)
    # El paso de memoria sustituye y concluye con la misma velocidad.
    assert verif.paso.resultado.simbolo == "V_salida"


def test_bajo_control_de_salida_con_la_salida_mas_lenta_sigue_v_erosion():
    """Salida ahogada (TW > D): la seccion de salida es la entera y frena."""
    _material, r = _resultado(0.3, 0.001, 1.0)
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.V_salida.valor < r.V_erosion
    v = M5._velocidad_de_v3(r)
    assert v.simbolo == "V_erosion"
    assert v.valor == pytest.approx(r.V_erosion, rel=REL_TRANSPORTE)
    # La procedencia dice que se comparo con la de salida.
    assert "SALIDA" in v.procedencia


def test_bajo_control_de_entrada_no_cambia():
    """El caso UPAO ALC46 de VE-1: control de entrada, V3 con V_erosion."""
    _material, r = _resultado(0.317, 0.10, 0.0)
    assert r.control_gobernante is ControlGobernante.ENTRADA
    v = M5._velocidad_de_v3(r)
    assert v.simbolo == "V_erosion"
    assert v.valor == pytest.approx(r.V_erosion, rel=REL_TRANSPORTE)


def test_con_el_barril_horizontal_sigue_la_velocidad_de_salida():
    """T-2: S = 0 no tiene tirante normal; la rama no cambia."""
    _material, r = _resultado(0.3, 0.0, 0.0)
    assert r.sin_tirante_normal
    v = M5._velocidad_de_v3(r)
    assert v.simbolo == "V_salida"


def test_bajo_control_de_salida_sin_velocidad_de_salida_no_cae_a_otra():
    """
    Un resultado de control de salida sin `V_salida` no se juzga con la del
    tirante normal a secas: falta la mitad de lo que V3 compara, y el
    metodo no puede evaluarlo (como la rama de S = 0).
    """
    _material, r = _resultado(0.3, 0.001, 0.0)
    with pytest.raises(MetodoNoEvaluableError):
        M5._velocidad_de_v3(replace(r, V_salida=None))
