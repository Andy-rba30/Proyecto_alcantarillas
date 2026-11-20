"""
tests/test_ve7_lote_b_carga_viva.py
===================================
VE-7, lote B, item B8 (VE4F-01; decision del consultor Fable, triaje VE-7,
2026-11-20): 'carga_viva_tubo_concreto_somero' pasa a valor de archivo
«largo_del_neumatico» (L_T): area menor, presion mayor, lado seguro, y
C4.6.2.10.2 permite despreciar el aumento por el relleno (cota superior).

Oraculo independiente: la franja de 4.6.2.10.2 en kip y pies, escrita a mano
en `tests/test_ve4f_relleno_bajo.py::_franja_a_mano`, con el tandem sobre un
tubo de B_c = 1.5 m (entre s_a = 4 ft = 1.22 m y s_a + E_span = 1.82 m, la
banda donde las dos lecturas difieren). Con la lectura de archivo M8 da el
W_L de L_T, y ese W_L es mayor o igual que el de la otra lectura.
"""

import pytest

from src import criterios_adoptados as ca
from src.constantes_fisicas import PIE_EN_METROS
from src.modelos import SeccionCircular, TipoMaterial
from src.modulos import M8_estructural as M8
from src.modulos.M2_material import catalogo, espesor_pared
from tests.apoyo.criterios import declarados
from tests.test_ve4f_relleno_bajo import (CP, CRITERIO, E_SPAN, KLF_EN_KN_M,
                                          NEUMATICO, REL_CONVERSION,
                                          _codigos, _franja_a_mano)

L_T_FT = 10 / 12                        # el neumatico, 10 in
E_SPAN_FT = (10 + 1.15 * 12) / 12       # L_T + LLDF x 1.0 ft


def test_el_valor_de_archivo_es_el_largo_del_neumatico():
    assert ca.CRITERIOS[CRITERIO].valor == NEUMATICO
    assert set(ca.CRITERIOS[CRITERIO].sensibilidad) == {NEUMATICO, E_SPAN}
    assert CRITERIO not in ca.criterios_de_perfil_sin_valor()


def test_con_el_tandem_y_bc_de_1_5_m_el_neumatico_carga_mas_o_igual():
    """La comparacion entera a mano, sin M8: S = 1.2 m de luz, D_E = 1 ft."""
    B_c_ft = 1.5 / PIE_EN_METROS
    neum, _, _ = _franja_a_mano(1.2 / PIE_EN_METROS, 1.0, L_T_FT, B_c_ft)
    espan, _, _ = _franja_a_mano(1.2 / PIE_EN_METROS, 1.0, E_SPAN_FT, B_c_ft)
    assert neum["tandem"][1] >= espan["tandem"][1]
    assert max(w for _p, w in neum.values()) >= \
        max(w for _p, w in espan.values())


def test_m8_con_el_valor_de_archivo_da_el_wl_del_neumatico():
    """
    D = 1.20 m (B_c = 1.45 m, en la banda del tandem) con 0.40 m de relleno:
    sin declarar nada, M8 lee L_T; declarada la otra lectura, da menos.
    """
    a01 = CP["punto_A01"]()
    D = 1.20
    mat = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    B_c = SeccionCircular(D).ancho_exterior(espesor_pared(mat, D))
    r = M8.verificar_conducto(punto=a01, material=mat,
                              seccion=SeccionCircular(D), altura_relleno=0.40)
    sust = {m.simbolo: m.valor
            for m in _codigos(r)[M8.CODIGO_CLASE].paso.sustitucion}
    a_mano, _IM, _E = _franja_a_mano(D / PIE_EN_METROS, 1.0, L_T_FT,
                                     B_c / PIE_EN_METROS)
    W_neum = max(w for _p, w in a_mano.values()) * KLF_EN_KN_M
    assert sust["W_L"] == pytest.approx(W_neum, rel=REL_CONVERSION)
    with declarados({CRITERIO: E_SPAN}):
        r2 = M8.verificar_conducto(punto=a01, material=mat,
                                   seccion=SeccionCircular(D),
                                   altura_relleno=0.40)
    W_espan = {m.simbolo: m.valor for m in
               _codigos(r2)[M8.CODIGO_CLASE].paso.sustitucion}["W_L"]
    assert sust["W_L"] >= W_espan
