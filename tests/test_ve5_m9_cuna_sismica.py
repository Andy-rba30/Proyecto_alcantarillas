"""
tests/test_ve5_m9_cuna_sismica.py
=================================
VE-5, lote M9, item 4 del censo (ficha T7B-06): la cuña de tanteo de
Coulomb (AASHTO C11.6.5.3: «the trial wedge method ... may also be used for
situations when the M–O Method is not suitable») donde el ensamble se
detenia:

  * sobre un trasdos INCLINADO (zapata sin talon, beta != 0): la cuña era la
    del plano vertical y se detenia pidiendo la formula cerrada;
  * con la formula cerrada (reglas «talud_quebrado_2h» y
    «talud_del_terraplen») fuera del dominio de Mononobe-Okabe
    (phi < i + psi): ahora la cuña con la superficie REAL del relleno da el
    incremento sismico;
  * la cuña sin maximo interior sigue sin cifra -- es el relleno mismo el
    que no es estable bajo k_h -- y lo dice.

ORACULOS ANALITICOS: con el talud uniforme e indefinido, el maximo de la
cuña sobre un plano inclinado beta es Coulomb (3.11.5.3-1) y, con k_h,
Mononobe-Okabe (A11.3.1-1), las dos con beta; la funcion de Mononobe-Okabe
del modulo esta verificada con beta != 0 por CP9_MONONOBE_OKABE. Escritos
ANTES del codigo: en rojo contra la base.
"""

import math
from types import SimpleNamespace

import pytest

from src import criterios_adoptados as ca
from src import modelos
from src.modelos import CondicionAnalisis, MetodoNoEvaluableError
from src.modulos import M9_cabezal as M9
from tests.apoyo.criterios import declarados
from tests.fixtures.casos_patron import CP_T7B_ESTABILIDAD as CP
from tests.test_t7b_cabezal_estabilidad import (_declarar_sitio, _entorno,
                                                _geometria)

EST = CondicionAnalisis.ESTATICO
SIS = CondicionAnalisis.SISMICO
TOL_K = 1e-5       # la cuña se afina a TOL_ANGULO_CUNA: cinco decimales en K
TOL_KN = 1e-4      # empujes en kN/m a cuatro decimales


@pytest.mark.parametrize("beta, k_h, k_v", [
    (8.0, 0.0, 0.0), (-6.0, 0.0, 0.0), (8.0, 0.20, 0.05), (-6.0, 0.15, 0.0)])
def test_la_cuna_sobre_un_plano_inclinado_es_coulomb_y_mononobe_okabe(
        beta, k_h, k_v):
    phi, i, delta = 34.0, 10.0, 20.0
    P, _rho = M9.cuna_de_tanteo(h=1.0, subida=math.inf,
                                talud=1.0 / math.tan(math.radians(i)),
                                phi_grados=phi, delta_grados=delta, gamma=2.0,
                                k_h=k_h, k_v=k_v, beta_grados=beta)
    K = 2 * P / (2.0 * (1.0 - k_v))
    K_MO = M9.k_ae_mononobe_okabe(phi_grados=phi, i_grados=i,
                                  beta_grados=beta, delta_grados=delta,
                                  k_h=k_h, k_v=k_v)
    assert K == pytest.approx(K_MO, abs=TOL_K)


@pytest.fixture
def tanteo(monkeypatch):
    ca.establecer_valor_dinamico("eta_importancia_operativa_conducto", 1.0)
    ca.establecer_valor_dinamico("phi_relleno_trasdos", CP["phi_relleno"])
    ca.establecer_valor_dinamico("peso_especifico_relleno_kn_m3",
                                 CP["gamma_relleno"])
    ca.establecer_valor_dinamico("drenaje_trasdos", "drenado")
    _declarar_sitio()
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h0=0.25, k_h=0.25, k_v=0.0))
    return _entorno()


def test_el_ensamble_usa_la_cuna_sobre_el_trasdos_inclinado(tanteo):
    """Zapata sin talon, trasdos a beta = 5 grados, relleno horizontal: la
    cuña de archivo da el K_A de Coulomb con beta (ya no se detiene)."""
    g = _geometria(ancho_talon=0.0, ancho_punta=1.70, beta_grados=5.0)
    entorno = _entorno(geometria=g)
    _cargas, datos = M9.cargas_del_cabezal(entorno, EST)
    assert datos["metodo_empuje"] == M9.METODO_EMPUJE_CUNA
    K = M9.k_a_coulomb(phi_grados=CP["phi_relleno"], i_grados=0.0,
                       beta_grados=5.0, delta_grados=CP["delta"])
    assert datos["K_A"] == pytest.approx(K, abs=TOL_K)
    _c, datos_s = M9.cargas_del_cabezal(entorno, SIS)
    K_AE = M9.k_ae_mononobe_okabe(phi_grados=CP["phi_relleno"], i_grados=0.0,
                                  beta_grados=5.0, delta_grados=CP["delta"],
                                  k_h=0.25, k_v=0.0)
    assert datos_s["K_AE"] == pytest.approx(K_AE, abs=TOL_K)


def test_la_formula_fuera_de_dominio_pasa_a_la_cuna_con_la_superficie_real(
        tanteo, monkeypatch):
    """
    Regla «talud_quebrado_2h» (i = arctan(0.40 / 4.80) = 4.76 grados) sobre
    el relleno que sube 0.40 m y se quiebra, con k_h = 0.50 (psi = 26.57):
    Mononobe-Okabe no es aceptable (phi = 30 < i + psi = 31.3). La cuña con
    la superficie real tiene maximo (phi - psi = 3.43 > 0): el incremento
    sale de ella (P_AE - P_A de la MISMA cuña), el estatico sigue con la
    formula de la regla.
    """
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h0=0.50, k_h=0.50, k_v=0.0))
    entorno = _entorno(cota_borde_plataforma=100.0 + CP["h"] + 0.40)
    with declarados({"regla_pendiente_relleno_trasdos":
                     "talud_quebrado_2h"}):
        cargas, datos = M9.cargas_del_cabezal(entorno, SIS)
        rel = M9.geometria_del_relleno(entorno)
    assert datos["metodo_empuje"] == M9.METODO_EMPUJE_FORMULA
    assert datos["K_AE_formula"] is None           # fuera de su dominio
    P_c, _ = M9.cuna_de_tanteo(h=rel["h"], subida=rel["subida_sobre_plano"],
                               talud=rel["talud"], phi_grados=30.0,
                               delta_grados=CP["delta"], gamma=1.0)
    P_cE, _ = M9.cuna_de_tanteo(h=rel["h"], subida=rel["subida_sobre_plano"],
                                talud=rel["talud"], phi_grados=30.0,
                                delta_grados=CP["delta"], gamma=1.0,
                                k_h=0.50, k_v=0.0)
    dP = (P_cE - P_c) * CP["gamma_relleno"]
    inc = next(c for c in cargas if c.codigo == "EQ.dPAE.h")
    assert inc.H == pytest.approx(
        dP * math.cos(math.radians(CP["delta"])), abs=TOL_KN)
    assert datos["metodo_incremento"] == M9.METODO_INCREMENTO_CUNA


def test_la_cuna_sin_maximo_dice_que_el_relleno_no_es_estable(tanteo,
                                                               monkeypatch):
    """k_h = 0.60: psi = 31 > phi = 30. Ni Mononobe-Okabe ni la cuña: el
    relleno horizontal no se sostiene bajo ese k_h. Sin cifra, y lo dice."""
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h0=0.60, k_h=0.60, k_v=0.0))
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M9.ensamble_estabilidad(tanteo, SIS)
    texto = str(exc.value)
    assert texto.startswith(modelos.MOTIVO_METODO_NO_EVALUABLE_CABEZAL)
    assert "el relleno no es estable" in texto
