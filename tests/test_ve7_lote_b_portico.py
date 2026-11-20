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


# ===========================================================================
# B3: el agua exterior
# ===========================================================================
# Geometria de `_disenar` (B = 2.0, H = 1.5, t = 0.20, H_rel = 1.0) y el
# paquete de A-01 (0.15): ejes a h = 1.70 m; el eje de la losa inferior a
# z_inf = 1.0 + 0.15 + 0.20 + 1.50 + 0.10 = 2.95 m bajo la rasante, el de la
# superior a z_sup = 1.25 m. Con el terreno a 1.0 m bajo la rasante, un NF a
# 0.25 m pone el agua EXACTAMENTE en el eje de la losa superior (triangulo
# entero en la pared).
GAMMA_SAT = 20.0
Z_INF, Z_SUP, H_EJES = 2.95, 1.25, 1.70
# El modelo cuenta la deformacion axial de las losas; la pendiente-deflexion
# de abajo no: el 1 % cubre esa diferencia.
REL_SIN_AXIAL = 0.01


def _con_nf(a01, nf):
    from dataclasses import replace
    return replace(a01, cota_terreno=a01.cota_rasante - 1.0,
                   NF_profundidad_m=nf)


def _con_saturado():
    return dict(DECLARACIONES_CAJON,
                peso_especifico_saturado_relleno_kn_m3=GAMMA_SAT)


def test_b3_con_el_nf_bajo_la_losa_inferior_los_numeros_son_los_de_hoy(a01):
    hoy = _disenar(a01)
    hondo = _disenar(_con_nf(a01, 5.0))      # NF a 4.0 m bajo z_inf
    assert M8.CASO_WA_EXT not in dict(hoy.casos)
    assert M8.CASO_WA_EXT not in dict(hondo.casos)
    assert hondo.envolventes == hoy.envolventes
    assert [a.As_adoptado for a in hondo.armados] == \
        [a.As_adoptado for a in hoy.armados]


def test_b3_con_el_nf_arriba_sin_el_saturado_se_detiene(a01):
    from src.modelos import CriterioPendienteError
    from tests.apoyo.criterios import sin_valor
    with sin_valor("peso_especifico_saturado_relleno_kn_m3"):
        with pytest.raises(CriterioPendienteError) as exc:
            _disenar(_con_nf(a01, 0.25))
    assert "peso_especifico_saturado_relleno_kn_m3" in str(exc.value)


def test_b3_el_momento_de_la_pared_a_mano(a01):
    """
    Pendiente-deflexion del marco cerrado simetrico con el triangulo de agua
    w0 = gamma_w (z_inf - z_NF) en las dos paredes (maximo abajo): momentos
    de empotramiento w0 h^2/20 abajo y w0 h^2/30 arriba, y en cada esquina
    la losa (rotaciones antisimetricas) responde con 2 E I_l / L. Con las
    rotaciones que alivian (phi_B, phi_T):

        (a + 2 k) phi_B - k phi_T = w0 h^2/20      a = 2 I_l / L
        -k phi_B + (a + 2 k) phi_T = w0 h^2/30     k = 2 I_p / h

    y el momento de la esquina inferior a phi_B, con traccion exterior.
    """
    from src.constantes_fisicas import GAMMA_AGUA_KN_M3
    from tests.apoyo.criterios import declarados
    d = _disenar(_con_nf(a01, 0.25), declaraciones=_con_saturado())
    g = d.geometria
    assert g.altura_ejes_m == pytest.approx(H_EJES, rel=REL_TRANSPORTE)
    w0 = GAMMA_AGUA_KN_M3 * (Z_INF - Z_SUP)
    sust = {m.simbolo: m.valor for m in d.pasos[0].sustitucion}
    assert sust["p_WA,ext"] == pytest.approx(w0, rel=REL_CONVERSION)
    L, h = g.ejes_x_m[-1], g.altura_ejes_m
    a = 2 * (g.t_losa_superior_m ** 3 / 12) / L
    k = 2 * (g.t_pared_m ** 3 / 12) / h
    F_B, F_T = w0 * h ** 2 / 20, w0 * h ** 2 / 30
    det = (a + 2 * k) ** 2 - k ** 2
    phi_B = (F_B * (a + 2 * k) + k * F_T) / det
    M_esquina = a * phi_B
    with declarados(_con_saturado()):
        casos = M8._casos_de_carga(
            punto=_con_nf(a01, 0.25), material=None,
            seccion=M8.SeccionRectangular(B=2.0, H=1.5), g=g, H_rel=1.0)[0]
    res = M8._ModeloPortico(g).resolver(casos[M8.CASO_WA_EXT])
    M_nudo = res["pared_0"][0.0][2]
    assert M_nudo == pytest.approx(-M_esquina, rel=REL_SIN_AXIAL)
    # y el caso entra al portico: la envolvente de la pared cambia
    assert M8.CASO_WA_EXT in dict(d.casos)


def test_b3_el_empuje_bajo_el_nf_es_el_sumergido(a01):
    """p_EH = k_o sigma'_v en los ejes: sobre el NF (en el eje de la losa
    superior) el seco de siempre; bajo el, + (gamma_sat - gamma_w) dz."""
    from src.constantes_fisicas import GAMMA_AGUA_KN_M3
    from tests.apoyo.criterios import declarados
    d = _disenar(_con_nf(a01, 0.25), declaraciones=_con_saturado())
    sust = {m.simbolo: m.valor for m in d.pasos[0].sustitucion}
    k0 = 1 - math.sin(math.radians(DECLARACIONES_CAJON["phi_relleno_trasdos"]))
    e_paq = a01.cota_rasante - a01.cota_subrasante
    with declarados(_con_saturado()):
        g_s, g_p, _ = M8.pesos_especificos_de_carga(piso_tubo_concreto=False)
    seco_sup = g_p * e_paq + g_s * (Z_SUP - e_paq)
    assert sust["p_EH,sup"] == pytest.approx(k0 * seco_sup, rel=REL_CONVERSION)
    assert sust["p_EH,inf"] == pytest.approx(
        k0 * (seco_sup + (GAMMA_SAT - GAMMA_AGUA_KN_M3) * (Z_INF - Z_SUP)),
        rel=REL_CONVERSION)
    assert {"AASHTO_LRFD_9.3.11.3", "MP.2.4.4.1.3#SUMERGIDO"} <= set(
        d.pasos[0].citas_textuales)
