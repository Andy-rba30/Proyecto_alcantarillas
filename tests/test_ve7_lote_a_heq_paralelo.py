"""
tests/test_ve7_lote_a_heq_paralelo.py
=====================================
VE-7, lote A (triaje VE-7 de Fable, 2026-11-20), A7 (VE6-T7A03 (3)): la
h_eq de la sobrecarga viva con el cabezal PARALELO A LA VIA.

Con una fila de la Carta 11 el muro es paralelo a la via y, por tanto, al
trafico. Si la orientacion vigente es la perpendicular del corredor y el
punto no declara otra, h_eq es la MAYOR de las dos tablas de AASHTO
3.11.6.4 (la del muro paralelo, sin distancia del punto, con su columna
«0.0 ft»), con un aviso que pide la orientacion y la distancia del punto.

El oraculo: las dos tablas leidas fila a fila del registro
(`constantes_normativas.H_EQ_ESTRIBO_PERPENDICULAR_FT` y
`H_EQ_MURO_PARALELO_FT`) e interpoladas aqui a mano en pies.
"""

import dataclasses

import pytest

from src import datos_sitio as ds
from src.constantes_normativas import (H_EQ_ESTRIBO_PERPENDICULAR_FT,
                                       H_EQ_MURO_PARALELO_FT,
                                       SOBRECARGA_TRASDOS_PISO_MP_M)
from src.modelos import CondicionAnalisis
from src.modulos import M9_cabezal as M9
from tests.test_t7c_cabezal_armado import tanteo  # noqa: F401

PIE = 0.3048
EST = CondicionAnalisis.ESTATICO


def _interpolar(puntos, x):
    puntos = sorted(puntos)
    for (a0, h0), (a1, h1) in zip(puntos, puntos[1:]):
        if a0 <= x <= a1:
            return h0 + (h1 - h0) * (x - a0) / (a1 - a0)
    # fuera de la tabla por debajo: el primer tramo extrapolado
    (a0, h0), (a1, h1) = puntos[0], puntos[1]
    return h0 + (h1 - h0) * (x - a0) / (a1 - a0)


def _perpendicular(h):
    return max(SOBRECARGA_TRASDOS_PISO_MP_M, PIE * _interpolar(
        [(a, v) for a, v in H_EQ_ESTRIBO_PERPENDICULAR_FT.values()], h / PIE))


def _paralelo(h, lejos):
    return max(SOBRECARGA_TRASDOS_PISO_MP_M, PIE * _interpolar(
        [(f[0], f[2] if lejos else f[1])
         for f in H_EQ_MURO_PARALELO_FT.values()], h / PIE))


def _corredor(orientacion):
    ds.establecer_dato_dinamico(
        "orientacion_muro_respecto_al_trafico", orientacion,
        "de prueba (VE-7)", "2026-11-20", origen="prueba")


def _h_eq(entorno):
    _, datos = M9.cargas_del_cabezal(entorno, EST)
    return datos["h_eq"], datos["h"]


def test_paralelo_a_la_via_con_corredor_perpendicular_toma_la_mayor(tanteo):
    _corredor("perpendicular_al_trafico")
    entorno = dataclasses.replace(tanteo, paralelo_a_la_via=True)
    h_eq, h = _h_eq(entorno)
    esperado = max(_perpendicular(h), _paralelo(h, lejos=False))
    assert h_eq == pytest.approx(esperado, rel=1e-12)
    avisos = M9.avisos_de_la_sobrecarga_del_punto(entorno)
    assert any("MAYOR de las dos tablas" in a
               and "distancia_borde_calzada_del_punto_m" in a
               and "orientacion_muro_del_punto" in a for a in avisos)
    # el cabezal normal al eje, con el mismo corredor: solo la -1
    h_normal, _ = _h_eq(tanteo)
    assert h_normal == pytest.approx(_perpendicular(h), rel=1e-12)
    assert not any("MAYOR de las dos tablas" in a for a in
                   M9.avisos_de_la_sobrecarga_del_punto(tanteo))


def test_con_la_distancia_del_punto_la_tabla_paralela_la_usa(tanteo):
    _corredor("perpendicular_al_trafico")
    g = dataclasses.replace(tanteo.geometria, distancia_borde_calzada_m=1.6)
    entorno = dataclasses.replace(tanteo, geometria=g, paralelo_a_la_via=True)
    h_eq, h = _h_eq(entorno)
    assert h_eq == pytest.approx(
        max(_perpendicular(h), _paralelo(h, lejos=True)), rel=1e-12)


def test_paralelo_a_la_via_con_corredor_paralelo_no_cambia(tanteo):
    """La otra orientacion: el corredor ya dice paralelo (el del muro de
    tanteo, borde a 1.60 m) y rige su tabla, sin envolvente ni aviso."""
    _corredor("paralelo_al_trafico")
    entorno = dataclasses.replace(tanteo, paralelo_a_la_via=True)
    h_eq, h = _h_eq(entorno)
    assert h_eq == pytest.approx(_paralelo(h, lejos=True), rel=1e-12)
    assert not any("MAYOR de las dos tablas" in a for a in
                   M9.avisos_de_la_sobrecarga_del_punto(entorno))


def test_con_la_orientacion_del_punto_rige_la_del_punto(tanteo):
    _corredor("perpendicular_al_trafico")
    g = dataclasses.replace(tanteo.geometria,
                            orientacion_trafico="paralelo_al_trafico",
                            distancia_borde_calzada_m=0.0)
    entorno = dataclasses.replace(tanteo, geometria=g, paralelo_a_la_via=True)
    h_eq, h = _h_eq(entorno)
    assert h_eq == pytest.approx(_paralelo(h, lejos=False), rel=1e-12)
