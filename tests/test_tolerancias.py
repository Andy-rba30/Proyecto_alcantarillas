"""
tests/test_tolerancias.py
=========================
Las tolerancias tienen que hacer dos cosas opuestas: absorber el ruido del
punto flotante y NO tapar un incumplimiento real. Si solo hicieran la primera,
bastaria con poner 1.0 y todo cumpliria siempre.
"""

import sys

import pytest

import constantes_normativas as CN
from criterios_adoptados import CRITERIOS
from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING
from tolerancias import TOL_BRENT, TOL_UMBRAL_NORMATIVO


def test_son_positivas_y_estan_por_encima_del_epsilon_del_double():
    for tol in (TOL_BRENT, TOL_UMBRAL_NORMATIVO):
        assert tol > 0
        assert tol > sys.float_info.epsilon


def test_el_umbral_absorbe_el_ruido_del_borde_libre():
    """
    Caso real: y = 0.75*0.90 y luego y/D. La division puede devolver
    0.7500000000000001, que NO es un incumplimiento de V1.
    """
    c = CP2_GEOMETRIA_MANNING
    y_sobre_D = (c["y_sobre_D"] * c["D"]) / c["D"]
    assert y_sobre_D <= CN.Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO


def test_el_umbral_no_tapa_un_incumplimiento_real():
    """
    Un exceso del orden de la tolerancia hidraulica del caso patron (1e-3) es
    significativo y tiene que fallar igual.
    """
    exceso = CP2_GEOMETRIA_MANNING["tolerancia_hidraulica"]
    assert TOL_UMBRAL_NORMATIVO < exceso
    assert not (CN.Y_SOBRE_D_MAX + exceso <= CN.Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO)


def test_la_convergencia_de_brent_es_mas_fina_que_el_umbral():
    """
    Primero se resuelve theta y despues se compara contra el umbral: si el
    solver convergiera mas grueso que la comparacion, el "cumple" dependeria
    del solver y no del diseno.
    """
    assert TOL_BRENT < TOL_UMBRAL_NORMATIVO


def test_una_tolerancia_no_es_un_criterio_adoptado():
    """No llevan etiqueta [N], [C] ni [A]: no hay nada que declarar en M11."""
    for nombre in ("TOL_BRENT", "TOL_UMBRAL_NORMATIVO", "tol_brent"):
        assert nombre not in CRITERIOS


def test_el_tirante_de_referencia_de_CP2_no_se_ve_afectado_por_la_tolerancia():
    """La tolerancia mueve el ultimo bit, no el tirante: 1e-9 m es 1 nanometro."""
    y = CP2_GEOMETRIA_MANNING["y_sobre_D"] * CP2_GEOMETRIA_MANNING["D"]
    assert y + TOL_UMBRAL_NORMATIVO == pytest.approx(
        y, abs=CP2_GEOMETRIA_MANNING["tolerancia_geometria"])
