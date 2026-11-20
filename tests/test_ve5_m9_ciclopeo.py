"""
tests/test_ve5_m9_ciclopeo.py
=============================
VE-5, lote M9, item 10 del censo (ficha T7C-09 (2) y (3)): el cabezal de
gravedad en concreto ciclopeo

  * C7: la zapata como VOLADIZO de concreto simple cuando vuela mas que la
    mitad de su peralte (E.060 22.10.2.2): traccion M_u/S <= phi·0,42·
    sqrt(f'c) y cortante V_u <= phi·0,11·sqrt(f'c)·b·h (22-7 y 22-9), con
    phi = 0,5, f'c <= 10 MPa y h - 50 mm (22.10.2.3 y 22.4.8);
  * C8: el cuerpo bajo SISMO, tracciones nulas con las cargas del Evento
    Extremo I sin factorar (incremento del empuje e inercia del cuerpo).

El muro es el de `CP_T7C_CICLOPEO` (H = 1.30, B = 1.00, zapata 0.30 m: la
punta vuela 0.30 > 0.15 y el talon 0.20 > 0.15). Escrito ANTES del codigo.
"""

import math
from dataclasses import replace

import pytest

from src import criterios_adoptados as ca
from src.modelos import CondicionAnalisis, EstadoDeVerificacion
from src.modulos import M9_cabezal as M9
from tests.apoyo.aproximacion import ABS_CERO
from tests.test_t7c_cabezal_armado import _gravedad, tanteo  # noqa: F401

TOL = 1e-6


def _v(a, codigo):
    return next(v for v in a.verificaciones if v.codigo == codigo)


def test_C7_la_punta_y_el_talon_como_voladizos_de_concreto_simple(tanteo):
    """
    El aprovechamiento es el mayor de (M_u/S)/(0,5·0,42·sqrt(10)·1000) y
    V_u/(0,5·0,11·sqrt(10)·1000·0,25), S = 0,25²/6, sobre las solicitaciones
    de la zapata con las dos combinaciones de E.060 y cada juego de empujes.
    """
    entorno = _gravedad()
    a = M9.verificar_cabezal_ciclopeo(entorno)
    cargas, datos = M9.cargas_del_cabezal(entorno, CondicionAnalisis.ESTATICO)
    juegos = [cargas, M9.cargas_en_reposo(cargas, datos)]
    h = 0.30 - 0.05
    f_t = 0.5 * 0.42 * math.sqrt(10.0) * 1000
    V_r = 0.5 * 0.11 * math.sqrt(10.0) * 1000 * h
    for clave in ("punta", "talon"):
        peor = 0.0
        for juego in juegos:
            for combo in M9._combinaciones_e060(juego, entorno.geometria.B):
                z = M9.solicitaciones_de_la_zapata(entorno.geometria, juego,
                                                   combo, datos)
                if z is None:
                    continue
                V, M = z[clave]
                peor = max(peor, abs(M) / (h ** 2 / 6) / f_t, abs(V) / V_r)
        c7 = _v(a, f"C7.{clave}.e")
        assert c7.valor_obtenido == pytest.approx(peor, abs=TOL)
        assert c7.paso.umbral.cita_id == "E060.22.10.2.2#VOLADIZO"
    assert not any("22.10.2.2 manda verificar" in x for x in a.avisos)


def test_C7_no_aplica_si_el_vuelo_no_pasa_de_la_mitad_del_peralte(tanteo):
    a = M9.verificar_cabezal_ciclopeo(_gravedad(
        espesor_zapata=0.70, cota_coronacion=102.00, ancho_punta=0.30,
        ancho_talon=0.20))
    assert not any(v.codigo.startswith("C7") for v in a.verificaciones)


def test_C8_el_cuerpo_bajo_sismo_lleva_el_incremento_y_la_inercia(tanteo):
    """
    k_h = 0.25 (fixture). A media altura (z = 0.95): la excentricidad con el
    sismo es la estatica mas (M_dPAE + k_h·W·y_W)/W, mayor que la de C3.
    """
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    assert a.sismico
    c3, c8 = _v(a, "C3.cuerpo.e"), _v(a, "C8.media.e")
    sus = {m.simbolo: m.valor for m in c8.paso.sustitucion}
    W = sus["W"]
    assert sus["k_h·W·y_W"] == pytest.approx(0.25 * W * (1.30 / 2) / 2,
                                            abs=TOL)
    assert c8.valor_obtenido > c3.valor_obtenido
    assert c8.valor_admisible == pytest.approx(0.40 / 6, abs=ABS_CERO)
    assert _v(a, "C8.arranque.e").paso.umbral.cita_id == "E060.22.4.7#JUNTAS"
    assert c8.estado is EstadoDeVerificacion.NO_CUMPLE
