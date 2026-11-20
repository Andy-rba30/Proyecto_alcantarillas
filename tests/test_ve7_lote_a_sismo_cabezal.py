"""
tests/test_ve7_lote_a_sismo_cabezal.py
======================================
VE-7, lote A (triaje VE-7 de Fable, 2026-11-20): el cabezal ciclopeo bajo
sismo (C8, ficha VE6M9-01).

A3 (VE6M9-01 (b)) -- con 'traccion_admisible_e060' la media altura bajo
sismo tambien DECIDE, atribuida a 'criterio_traccion_cabezal_ciclopeo'.

A4 (VE6M9-01 (a)) -- con k_v distinto de cero el peso estabilizante del
cuerpo va con (1 - k_v); el oraculo es la aritmetica de C8 escrita aqui
sobre los datos del ensamble sismico (el mismo camino independiente de
`test_ve5_m9_ciclopeo.py`), con el (1 - k_v) puesto a mano.
"""

import math
from types import SimpleNamespace

import pytest

from src import criterios_adoptados as ca
from src.modelos import CondicionAnalisis, EstadoDeVerificacion
from src.modulos import M9_cabezal as M9
from tests.test_t7c_cabezal_armado import _gravedad, tanteo  # noqa: F401
from tests.test_ve5_m9_ciclopeo import C8_MEDIA, GAMMA_EQ, TOL, _v

SIS = CondicionAnalisis.SISMICO
K_V = 0.10


def test_A3_la_media_altura_bajo_sismo_decide_con_la_traccion_admisible(
        tanteo):
    """e > t/6 a media altura con 'traccion_admisible_e060': incumple y
    CUENTA (decide), atribuida al criterio de traccion del proyecto."""
    ca.establecer_valor_dinamico("criterio_traccion_cabezal_ciclopeo",
                                 "traccion_admisible_e060")
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    media = _v(a, "C8.media.e")
    assert media.valor_obtenido > media.valor_admisible
    assert media.estado is EstadoDeVerificacion.NO_CUMPLE
    assert not media.cumple
    assert not a.cumple
    assert media.paso.umbral.criterio_aplicado == \
        "criterio_traccion_cabezal_ciclopeo"


def _c8_media_a_mano(entorno, k_v):
    """C8 a media altura con la aritmetica escrita aqui (ver el modulo)."""
    c, d = M9.cargas_del_cabezal(entorno, SIS, k_h=0.25)
    assert d["k_v"] == pytest.approx(k_v)
    H = {x.codigo: x.H for x in c}
    h, z, t, e_c = d["h"], 0.95, 0.40, 0.30
    arriba = h - z
    W = d["gamma_c"] * (t + e_c) / 2 * 0.65
    x_W = (t ** 2 + t * e_c + e_c ** 2) / (3 * (t + e_c))
    y_W = 0.65 * (t + 2 * e_c) / (3 * (t + e_c))
    M_EH = (d["K_A"] * math.cos(d["inclinacion"]) * d["gamma"] * arriba ** 3
            / 6)
    M_LS = d["K_A"] * d["gamma"] * d["h_eq"] * arriba ** 2 / 2
    assert d["fraccion_brazo"] > 2 / 3
    M_dP = H["EQ.dPAE.h"] * (d["fraccion_brazo"] * h - z)
    W_v = W * (1 - k_v)
    excentricidades = []
    for f_eh, f_inc, f_ir in ((1.0, 1.0, 0.5), (1.0, 0.0, 1.0)):
        tierra = max(f_eh * M_EH + f_inc * M_dP,
                     (f_eh * H["EH.h"] + f_inc * H["EQ.dPAE.h"])
                     * arriba ** 2 / (2 * h))
        M_H = tierra + GAMMA_EQ * M_LS + f_ir * d["k_h"] * W * y_W
        excentricidades.append(abs((M_H - W_v * (t / 2 - x_W)) / W_v))
    return max(excentricidades)


def test_A4_con_k_v_cero_c8_no_cambia(tanteo):
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    media = _v(a, "C8.media.e")
    assert media.valor_obtenido == pytest.approx(C8_MEDIA, abs=1e-5)
    assert not any("(1 - k_v)" in x for x in a.avisos)
    sus = {m.simbolo: m.valor for m in media.paso.sustitucion}
    assert sus["k_v"] == pytest.approx(0.0)


def _con_k_v(monkeypatch):
    """La cadena impuesta del muro de tanteo (`tanteo`), con k_v = 0.10."""
    base = M9.cadena_sismica()
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h=base.k_h, k_v=K_V, k_h0=base.k_h0))


def test_A4_con_k_v_el_peso_estabilizante_va_con_uno_menos_k_v(
        tanteo, monkeypatch):
    _con_k_v(monkeypatch)
    entorno = _gravedad()
    a = M9.verificar_cabezal_ciclopeo(entorno)
    media = _v(a, "C8.media.e")
    assert media.valor_obtenido == pytest.approx(
        _c8_media_a_mano(entorno, K_V), abs=TOL)
    assert "W·(1 - k_v)" in media.paso.formula
    sus = {m.simbolo: m.valor for m in media.paso.sustitucion}
    assert sus["k_v"] == pytest.approx(K_V)
    # el aviso: el ensamble E1-E3 no lo aplica a los pesos
    assert any("NO aplica k_v a los pesos" in x for x in a.avisos)


def test_A4_el_ensamble_no_aplica_k_v_a_los_pesos(tanteo, monkeypatch):
    """Lo que el aviso afirma, medido: los pesos del ensamble sismico son
    los del estatico con k_v distinto de cero."""
    _con_k_v(monkeypatch)
    entorno = _gravedad()
    est, _ = M9.cargas_del_cabezal(entorno, CondicionAnalisis.ESTATICO)
    sis, _ = M9.cargas_del_cabezal(entorno, SIS)
    pesos = ("DC.pantalla", "DC.zapata", "EV.talon")
    V_est = {c.codigo: c.V for c in est if c.codigo in pesos}
    V_sis = {c.codigo: c.V for c in sis if c.codigo in pesos}
    assert V_est and V_est == pytest.approx(V_sis)
