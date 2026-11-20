"""
tests/test_ve5_m45_resalto.py
=============================
VE-5, lote m45, item 17 (fichas EA-02 y VE3-08): el resalto hidraulico por
CANTIDAD DE MOVIMIENTO (HEC-14 Cap. 6) y V2 con la velocidad aguas abajo del
resalto cuando el resalto queda dentro del barril.

ORACULO: los ejemplos resueltos de HEC-14 (FHWA-NHI-06-086), Cap. 6,
«Design Example: Hydraulic Jump in a Horizontal, Rectangular Channel (SI)»
(pag. impresa 6-6, PDF 69) y «... Circular Channel (SI)» (pag. impresa 6-11,
PDF 74). Los dos leen J de una FIGURA (6.4 y 6.6) a dos cifras (2.2 y 2.3) y
redondean el Froude a 1.9; la tolerancia contra lo IMPRESO es la de esa
lectura, y contra la ecuacion cerrada de Belanger (Ec. 6.3) es la de la
cuadratura del primer momento.

SE ESCRIBIO EN ROJO PRIMERO: `M3.resalto_hidraulico`, `M4.situar_resalto` y
`ResultadoHidraulico.resalto` no existian, y V2 juzgaba la velocidad
uniforme supercritica con el resalto dentro del barril.
"""

from __future__ import annotations

import dataclasses
import math

import pytest

from src.constantes_fisicas import G
from src.constantes_normativas import HEC14_RESALTO_PENDIENTE_HORIZONTAL_MAX
from src.modelos import (MOTIVO_METODO_NO_EVALUABLE_HEC14, ControlGobernante,
                         MetodoNoEvaluableError, SeccionCircular,
                         SeccionRectangular)
from src.modulos.M3_hidraulica import (_MomentoDelBarril,
                                       exigir_dominio_del_resalto,
                                       resalto_hidraulico)
from src.modulos.M4_control import situar_resalto, tirante_critico
from src.modulos.M5_verificaciones import v2_velocidad_minima
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.test_ve3_11_ensayos_conducto import _e13

# J leido de una figura a dos cifras (2.2, 2.3): media unidad de la ultima
# cifra es 0.05 sobre 2.2, un 2.3 %; el ejemplo rectangular redondea ademas
# el Froude (1.9 frente a 5.79/(9.81*0.914)^0.5 = 1.934), que mueve J otro
# 2 %. Cinco por ciento cubre las dos lecturas y nada mas.
REL_LECTURA_FIGURA = 0.05
# El ejemplo circular imprime A2 y V2 con dos decimales: media centesima.
ABS_DOS_DECIMALES = 0.005
# La cuadratura del primer momento sobre `PUNTOS_MOMENTO_SECCION` puntos
# contra la forma cerrada (el mismo margen de test_ve3_11).
REL_CUADRATURA_MOMENTO = 1e-6
S_HORIZONTAL = 0.002            # la pendiente del ejemplo rectangular (0.2 %)


def _belanger(y1: float, Fr1: float) -> float:
    """Ec. (6.3) de HEC-14: J^2 - 1 = 2 Fr1^2 (1 - 1/J), resuelta en J."""
    return y1 * (math.sqrt(1 + 8 * Fr1 ** 2) - 1) / 2


# ===========================================================================
# 1. El resalto suelto contra los ejemplos resueltos de HEC-14 Cap. 6
# ===========================================================================

def test_ejemplo_rectangular_si_de_hec14():
    """Cajon de 2.134 m de luz, Q = 11.33 m3/s, y1 = 0.914 m (pag. 6-6)."""
    B, Q, y1 = 2.134, 11.33, 0.914
    sec = SeccionRectangular(B=B, H=3.0)       # alto de sobra: lamina libre
    r = resalto_hidraulico(Q=Q, seccion=sec, y1=y1,
                           y_c=tirante_critico(Q, sec).y_c, S=S_HORIZONTAL)
    assert not r.lleno
    assert r.y2_m == pytest.approx(_belanger(y1, r.Fr1),
                                   rel=REL_CUADRATURA_MOMENTO)
    assert r.Fr1 == pytest.approx(Q / (B * y1) / math.sqrt(G * y1),
                                  rel=REL_CUADRATURA_MOMENTO)
    assert r.y2_m == pytest.approx(2.011, rel=REL_LECTURA_FIGURA)
    assert r.V2_m_s == pytest.approx(2.64, rel=REL_LECTURA_FIGURA)
    assert r.V2_m_s == pytest.approx(Q / (B * r.y2_m),
                                     rel=REL_CUADRATURA_MOMENTO)


def test_ejemplo_circular_si_de_hec14():
    """RCP de 2.134 m, Q = 5.664 m3/s, y1 = 0.732 m (pag. impresa 6-11)."""
    D, Q, y1 = 2.134, 5.664, 0.732
    sec = SeccionCircular(D=D)
    r = resalto_hidraulico(Q=Q, seccion=sec, y1=y1,
                           y_c=tirante_critico(Q, sec).y_c, S=0.02)
    assert not r.lleno
    assert r.y2_m == pytest.approx(1.684, rel=REL_LECTURA_FIGURA)
    assert r.A2_m2 == pytest.approx(2.99, abs=ABS_DOS_DECIMALES)
    assert r.V2_m_s == pytest.approx(1.89, abs=ABS_DOS_DECIMALES)


def test_seccion_2_llena_es_la_ec_6_5():
    """
    Con el conjugado por encima de la clave la seccion 2 va llena y y2 es la
    carga piezometrica: Q^2/(g A1) + A1 y1/2 = Q^2/(g B H) + B H (y2 - H/2)
    en el rectangulo (Ec. 6.5 escrita para el cajon).
    """
    B, H, Q, y1 = 1.20, 0.60, 1.0, 0.10
    sec = SeccionRectangular(B=B, H=H)
    r = resalto_hidraulico(Q=Q, seccion=sec, y1=y1,
                           y_c=tirante_critico(Q, sec).y_c, S=S_HORIZONTAL)
    A1, A = B * y1, B * H
    M1 = Q * Q / (G * A1) + A1 * y1 / 2
    y2 = (M1 - Q * Q / (G * A)) / A + H / 2
    assert r.lleno
    assert r.y2_m == pytest.approx(y2, rel=REL_CUADRATURA_MOMENTO)
    assert r.A2_m2 == pytest.approx(A, rel=REL_TRANSPORTE)
    assert r.V2_m_s == pytest.approx(Q / A, rel=REL_TRANSPORTE)


def test_fuera_del_10_por_ciento_no_es_evaluable():
    sec = SeccionCircular(D=0.90)
    with pytest.raises(MetodoNoEvaluableError) as e:
        resalto_hidraulico(Q=0.6, seccion=sec, y1=0.25,
                           y_c=tirante_critico(0.6, sec).y_c,
                           S=HEC14_RESALTO_PENDIENTE_HORIZONTAL_MAX)
    assert str(e.value).startswith(MOTIVO_METODO_NO_EVALUABLE_HEC14)


# ===========================================================================
# 2. El resalto SITUADO dentro del barril (E13 del revisor de VE-3.11)
# ===========================================================================

def test_e13_con_tw_070_el_resalto_queda_dentro_cerca_de_la_salida():
    """
    Hasta VE-5 el resalto entraba solo con TW >= conjugado del NORMAL
    (0.729 m). La S2 que baja desde la entrada no llega al normal en 22.6 m,
    y su conjugado a la salida es menor: con TW = 0.70 el resalto queda
    dentro, junto a la salida.
    """
    r = _e13(0.70)
    assert r.control_gobernante is ControlGobernante.ENTRADA
    assert r.resalto_en_el_barril and r.receptor_en_el_barril
    s = r.resalto
    assert s is not None and not s.lleno
    assert 0 < s.x_desde_salida_m < r.perfil.x_fin_remanso_m
    assert r.y_normal < s.y1_m < r.y_critico < s.y2_m <= 0.70
    # el conjugado conserva el momentum de la Ec. 6.1
    m = _MomentoDelBarril(r.Q_celda_m3s, SeccionCircular(D=0.90))
    assert m(s.y2_m) == pytest.approx(m(s.y1_m), rel=REL_CUADRATURA_MOMENTO)
    assert "4.4b" in [p.codigo for p in r.pasos]


def test_e13_el_resalto_avanza_aguas_arriba_al_subir_el_tw():
    x = [_e13(TW).resalto.x_desde_salida_m for TW in (0.70, 0.75, 0.80)]
    assert x[0] < x[1] < x[2]


def test_e13_con_tw_bajo_el_conjugado_de_la_s2_el_resalto_sale():
    r = _e13(0.68)
    assert not r.resalto_en_el_barril and r.resalto is None
    assert "4.4b" not in [p.codigo for p in r.pasos]


# ===========================================================================
# 3. V2 con la velocidad aguas abajo del resalto
# ===========================================================================

def test_v2_con_el_resalto_dentro_juzga_la_velocidad_minima_del_perfil():
    r = _e13(0.75)
    v = v2_velocidad_minima(resultado=r)
    sustitucion = {m.simbolo: m.valor for m in v.paso.sustitucion}
    assert v.valor_obtenido == pytest.approx(r.perfil.V_min_m_s,
                                             rel=REL_TRANSPORTE)
    assert v.valor_obtenido < r.resalto.V2_m_s < r.V_sedimentacion
    assert sustitucion["V_tras_resalto"] == pytest.approx(r.resalto.V2_m_s,
                                                        rel=REL_TRANSPORTE)
    assert "HEC14.6#V_TRAS_RESALTO" in v.paso.citas_textuales


def test_v2_con_el_resalto_fuera_sigue_con_el_uniforme():
    r = _e13(0.68)
    v = v2_velocidad_minima(resultado=r)
    assert v.valor_obtenido == pytest.approx(r.V_sedimentacion,
                                             rel=REL_TRANSPORTE)
    assert "V_tras_resalto" not in {m.simbolo for m in v.paso.sustitucion}


# ===========================================================================
# 4. Las dos piezas publicas, por su nombre
# ===========================================================================

def test_exigir_dominio_del_resalto_es_el_10_por_ciento_de_hec14_6_3():
    exigir_dominio_del_resalto(S_HORIZONTAL)          # dentro: no levanta
    with pytest.raises(MetodoNoEvaluableError):
        exigir_dominio_del_resalto(HEC14_RESALTO_PENDIENTE_HORIZONTAL_MAX)


def _piezas_e13(TW):
    from src.modulos.M3_hidraulica import resolver_manning
    from tests.test_ve3_11_ensayos_conducto import (D_E13, L_E13, S_E13,
                                                    _concreto)
    r = _e13(TW)
    sec = SeccionCircular(D=D_E13)
    normal = resolver_manning(seccion=sec, Q=r.Q_celda_m3s, S=S_E13,
                              material=_concreto())
    return r, dict(Q_celda=r.Q_celda_m3s, seccion=sec, S=S_E13, L=L_E13,
                   TW=TW, n=_concreto().n_para_capacidad,
                   critico=tirante_critico(r.Q_celda_m3s, sec),
                   llenado_normal=normal.geometria.llenado)


def test_situar_resalto_es_lo_que_viaja_en_el_resultado():
    r, piezas = _piezas_e13(0.75)
    resalto, dentro = situar_resalto(perfil=r.perfil, **piezas)
    assert dentro and resalto == r.resalto


def test_situar_resalto_con_la_s1_en_la_cara_de_entrada_lo_ahoga_en_la_boca():
    r, piezas = _piezas_e13(0.75)
    ahogado = dataclasses.replace(r.perfil, alcanza_entrada=True,
                                  x_fin_remanso_m=None,
                                  HW_remanso_m=r.HW_entrada)
    assert situar_resalto(perfil=ahogado, **piezas) == (None, True)
