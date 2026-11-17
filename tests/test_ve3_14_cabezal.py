"""
tests/test_ve3_14_cabezal.py
============================
VE-3.14: los defectos del diseño del cabezal que encontraron los ensayos de
diseño (proceso/planes_mejora/ve3_estado/ENSAYOS_DISENO_CABEZAL.md, §6).

BLOQUE 1 (H-2, parte D). EL CORTANTE FUERA DEL SIMPLIFICADO SE VERIFICA. Hasta
VE-3.14, una seccion sin estribos fuera de las condiciones de AASHTO 5.7.3.4.1
(peralte de 16.0 in o mas, o una zapata con el vuelo de 3·d_v o mas) se
detenia con «metodo no evaluable», y el dimensionamiento del peralte saltaba
ese peralte aunque nada fallara: los ensayos midieron zapatas de 0.70 a 1.00 m
donde, con el procedimiento GENERAL de 5.7.3.4.2, bastan 0.45 a 0.50 m. Hoy
la seccion se verifica con β de la ec. 5.7.3.4.2-2.

SE ESCRIBIO EN ROJO PRIMERO contra bd350f9.
"""

from __future__ import annotations

import math

import pytest

from src import constantes_normativas as cn
from src.constantes_fisicas import PULGADA_EN_MM
from src.dominios import MILIMETROS_POR_METRO
from src.modelos import (CondicionAnalisis, ELEMENTO_ZAPATA, SECCION_PUNTA,
                         SolicitacionDeArmado)
from src.modulos import M9_cabezal as M9
from tests.apoyo.aproximacion import REL_TRANSPORTE


def _beta_a_mano(M_u, V_u, d_v, A_s):
    """La ec. 5.7.3.4.2-2 con 5.7.3.4.2-4 y -7, escrita aparte (a_g = 0)."""
    M = max(M_u, V_u * d_v)
    eps = max((M / d_v + V_u) / (cn.ES_REFUERZO_AASHTO_MPA * A_s / 1000.0), 0.0)
    s_xe = d_v * 1000.0 / 25.4 * 1.38 / 0.63          # literal-ok: ec. 5.7.3.4.2-7 a mano
    s_xe = min(max(s_xe, 12.0), 80.0)                  # literal-ok: limites de s_xe a mano
    return 4.8 / (1 + 750 * eps) * 51 / (39 + s_xe)     # literal-ok: ec. 5.7.3.4.2-2 a mano


def test_beta_general_con_la_cuenta_a_mano():
    r = M9.beta_procedimiento_general(M_u=200.0, V_u=150.0, d_v=0.50,
                                      A_s=1500.0)
    assert r["beta"] == pytest.approx(_beta_a_mano(200.0, 150.0, 0.50, 1500.0),
                                      rel=REL_TRANSPORTE)
    assert r["s_x_in"] == pytest.approx(0.50 * MILIMETROS_POR_METRO
                                        / PULGADA_EN_MM, rel=REL_TRANSPORTE)
    # El momento no se toma menor que V_u·d_v.
    poco = M9.beta_procedimiento_general(M_u=1.0, V_u=150.0, d_v=0.50,
                                         A_s=1500.0)
    assert poco["M_u_efectivo"] == pytest.approx(75.0, rel=REL_TRANSPORTE)
    # s_xe acotado a [12, 80] in.
    chico = M9.beta_procedimiento_general(M_u=10.0, V_u=5.0, d_v=0.10,
                                          A_s=500.0)
    assert chico["s_xe_in"] == pytest.approx(cn.SXE_MIN_IN, rel=REL_TRANSPORTE)
    grande = M9.beta_procedimiento_general(M_u=10.0, V_u=5.0, d_v=1.20,
                                           A_s=500.0)
    assert grande["s_xe_in"] == pytest.approx(cn.SXE_MAX_IN, rel=REL_TRANSPORTE)


def test_una_pantalla_gruesa_se_verifica_con_el_procedimiento_general():
    """
    La pantalla de 0.45 m sin estribos (fuera de 5.7.3.4.1 por los 16.0 in)
    ya no se detiene: A2 se evalua con la β del procedimiento general.
    """
    s = M9.diseno_flexion_corte(momento=30.0, cortante=40.0, espesor=0.45,
                                id_punto="T-00")
    assert s.V_r is not None and s.V_r > 0
    a2 = next(v for v in s.verificaciones if v.codigo.startswith("A2"))
    beta = next(m for m in a2.paso.sustitucion if m.simbolo == "beta")
    esperado = _beta_a_mano(30.0, 40.0, s.d_v, s.barra.As_provisto)
    assert beta.valor == pytest.approx(esperado, rel=REL_TRANSPORTE)
    assert not math.isclose(beta.valor, cn.BETA_SIMPLIFICADO_AASHTO)
    assert "5.7.3.4.2" in a2.paso.formula


def test_una_zapata_gruesa_y_larga_se_verifica_con_el_general():
    kw = dict(momento=30.0, cortante=40.0, espesor=0.60, es_zapata=True,
              elemento=ELEMENTO_ZAPATA, clave=SECCION_PUNTA,
              seccion="punta de prueba", cara="inferior", ancho_seccion=2.0)
    corta = M9.diseno_flexion_corte(vuelo=0.80, **kw)     # simplificado
    larga = M9.diseno_flexion_corte(vuelo=2.50, **kw)     # general
    a2c = next(v for v in corta.verificaciones if v.codigo.startswith("A2"))
    a2l = next(v for v in larga.verificaciones if v.codigo.startswith("A2"))
    bc = next(m for m in a2c.paso.sustitucion if m.simbolo == "beta")
    bl = next(m for m in a2l.paso.sustitucion if m.simbolo == "beta")
    assert bc.valor == pytest.approx(cn.BETA_SIMPLIFICADO_AASHTO,
                                     rel=REL_TRANSPORTE)
    assert bl.valor < cn.BETA_SIMPLIFICADO_AASHTO
    assert larga.V_r < corta.V_r


def test_el_general_rige_por_combinacion():
    """β depende de M_u y V_u: cada combinacion se verifica con la suya."""
    sols = (SolicitacionDeArmado(
                combinacion="Resistencia I", condicion=CondicionAnalisis.ESTATICO,
                M_u=60.0, V_u=80.0, phi_flexion=0.9, phi_corte=0.9,
                M_u_cedente=60.0, V_u_cedente=80.0),
            SolicitacionDeArmado(
                combinacion="Evento Extremo I", condicion=CondicionAnalisis.SISMICO,
                M_u=90.0, V_u=95.0, phi_flexion=1.0, phi_corte=1.0,
                M_u_cedente=90.0, V_u_cedente=95.0))
    s = M9.diseno_flexion_corte(solicitaciones=sols, espesor=0.50)
    a2 = next(v for v in s.verificaciones if v.codigo.startswith("A2"))
    # Rige la combinacion de menor margen, con SU β.
    margenes = []
    for sol in sols:
        b = _beta_a_mano(sol.M_u, sol.V_u, s.d_v, s.barra.As_provisto)
        V_c = cn.VC_COEFICIENTE_AASHTO_SI * b * math.sqrt(21.0) * 1000.0 * s.d_v
        margenes.append((sol.phi_corte * V_c - sol.V_u, sol, b))
    _m, rige, b_rige = min(margenes, key=lambda x: x[0])
    assert s.rige_cortante.combinacion == rige.combinacion
    beta = next(m for m in a2.paso.sustitucion if m.simbolo == "beta")
    assert beta.valor == pytest.approx(b_rige, rel=REL_TRANSPORTE)
    assert "Resistencia I" in a2.paso.nota_del_proyecto and "Evento Extremo I" in a2.paso.nota_del_proyecto
