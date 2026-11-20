"""
tests/test_ve7_lote_b_portico.py
================================
VE-7, lote B, items B4, B3 y B5 sobre el portico del marco (ficha T5-07;
decision del consultor Fable, triaje VE-7, 2026-11-20).

  * B4 (T5-07 (3)): las caras que ninguna combinacion tracciona llevan el
    minimo de retraccion y temperatura de AASHTO 5.10.6 (12.11.5.3.1 lo
    manda). Oraculo: toda cara de toda seccion tiene acero (un armado o una
    fila de minimo), y el minimo de la cara sin traccion es, a mano,
    max(5.10.6 con b = h, E.060 9.7.2 por cara) -- 5.10.6 escrito en su
    unidad (in2/ft) y convertido aqui.

Los casos se arman con los helpers de `tests/test_ve5_portico_marco.py`.
"""

import math

import pytest

from src.constantes_fisicas import KIP_EN_KN, PIE_EN_METROS
from src.modulos import M8_estructural as M8
from src.modulos import M9_cabezal as M9
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.test_ve5_portico_marco import (DECLARACIONES_CAJON, _disenar,
                                          a01)  # noqa: F401  (fixture)

PULG_EN_MM = 25.4
REL_CONVERSION = 1e-9


# ===========================================================================
# B4
# ===========================================================================

def test_b4_toda_cara_de_toda_seccion_tiene_acero(a01):
    d = _disenar(a01)
    armadas = {a.clave for a in d.armados}
    con_minimo = {f.posicion.split(":", 1)[0] for f in d.minimos}
    assert d.minimos                       # hay caras sin traccion
    assert not armadas & con_minimo        # una u otra, no las dos
    for (sec, *_r) in M8.secciones_del_portico(d.geometria):
        for cara in (M8.CARA_INTERIOR, M8.CARA_EXTERIOR):
            assert f"{sec}.{cara}" in armadas | con_minimo, (sec, cara)
    assert all(f.barra is not None for f in d.minimos)
    paso = next(p for p in d.pasos if p.codigo == M8.CODIGO_PASO_PORTICO_MINIMOS)
    assert "AASHTO_LRFD_9.12.11.5.3.1" in paso.citas_textuales


def test_b4_el_minimo_es_el_de_5_10_6_o_el_de_e060(a01):
    """5.10.6 a mano en su unidad: A_s = 1.30 b h / [2 (b + h) f_y] in2/ft
    (b, h en in; f_y en ksi), con b = h por metro de seccion, acotado a
    0.11-0.60 in2/ft; E.060 9.7.2: 0.0018 b h repartido en dos caras."""
    from tests.apoyo.criterios import declarados
    d = _disenar(a01)
    t = d.geometria.t_losa_superior_m
    with declarados(DECLARACIONES_CAJON):
        fy = M9.materiales_del_armado()["fy"]            # MPa
    h_in = t * 1000 / PULG_EN_MM
    fy_ksi = fy * 1000 / KIP_EN_KN * (PULG_EN_MM / 1000) ** 2
    As_in2_ft = 1.30 * h_in * h_in / (2 * (h_in + h_in) * fy_ksi)
    As_in2_ft = min(max(As_in2_ft, 0.11), 0.60)
    As_5106 = As_in2_ft * PULG_EN_MM ** 2 / PIE_EN_METROS
    As_e060 = 0.0018 * t * 1e6 / 2
    for f in d.minimos:
        assert f.As_minimo == pytest.approx(max(As_5106, As_e060),
                                            rel=REL_CONVERSION), f.posicion
        assert f.As_requerido == pytest.approx(0.0, abs=REL_TRANSPORTE)
