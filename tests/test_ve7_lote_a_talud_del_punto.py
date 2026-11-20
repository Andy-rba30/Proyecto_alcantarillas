"""
tests/test_ve7_lote_a_talud_del_punto.py
========================================
VE-7, lote A (triaje VE-7 de Fable, 2026-11-20), A6 (ficha VE5M9-03): la
geometria del talud que baja delante del cabezal, POR PUNTO
(`talud_delante_del_cabezal_del_punto`), validada con el validador del [S]
y ganando al de corredor, como la sobrecarga del punto (VE6M9-04).

El oraculo del RC_BC es la tabla de AASHTO 10.6.3.1.2c leida por
`M9.coeficiente_rcbc` con la geometria de CADA punto: dos puntos con
taludes distintos dan RC_BC distintos, y cada uno el de su talud.
"""

import dataclasses
import json

import pytest

import cli
from src import servicio
from src.modelos import CondicionAnalisis, DatoInvalidoError
from src.modulos import M9_cabezal as M9
from tests.apoyo.criterios import declarados
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.test_ve5_m9_portante_talud import tanteo  # noqa: F401

EST = CondicionAnalisis.ESTATICO
CORREDOR = {"H_s_m": 4.0, "beta_grados": 20.0, "b_m": 0.0}
PUNTO_1 = {"H_s_m": 2.0, "beta_grados": 15.0, "b_m": 0.0}
PUNTO_2 = {"H_s_m": 6.0, "beta_grados": 30.0, "b_m": 0.0}


def test_la_clave_se_valida_con_el_validador_del_s(tmp_path):
    assert "talud_delante_del_cabezal_del_punto" in servicio.CLAVES_DE_CABEZAL
    uno = M9.validar_talud_delante_del_punto(PUNTO_1)
    assert uno == {"entrada": PUNTO_1, "salida": PUNTO_1}
    por_extremo = M9.validar_talud_delante_del_punto({"salida": PUNTO_2})
    assert por_extremo == {"entrada": None, "salida": PUNTO_2}
    for malo in ({"H_s_m": -1.0, "beta_grados": 20.0, "b_m": 0.0},
                 {"entrada": {"H_s_m": 1.0}}, {}, "x"):
        with pytest.raises(DatoInvalidoError):
            M9.validar_talud_delante_del_punto(malo)
    ruta = tmp_path / "e.json"
    ruta.write_text(json.dumps({"puntos": {"A-01": {
        "talud_delante_del_cabezal_del_punto": PUNTO_1}}}), encoding="utf-8")
    externos = cli.cargar_datos_externos(ruta, {})
    assert externos.valor("A-01", "talud_delante_del_cabezal_del_punto") \
        == {"entrada": PUNTO_1, "salida": PUNTO_1}


def _rcbc_del_ensamble(entorno, monkeypatch):
    vistos = []
    original = M9.capacidad_portante_zapata_en_talud

    def espia(**kw):
        q, det = original(**kw)
        vistos.append((kw["H_s"], kw["beta_grados"], det["RC_BC"]))
        return q, det

    monkeypatch.setattr(M9, "capacidad_portante_zapata_en_talud", espia)
    M9.ensamble_estabilidad(entorno, EST)
    monkeypatch.setattr(M9, "capacidad_portante_zapata_en_talud", original)
    assert vistos
    return vistos


def test_dos_puntos_con_taludes_distintos_dan_rcbc_distintos(
        tanteo, monkeypatch):
    with declarados({"terreno_delante_del_cabezal": "talud_descendente",
                     "talud_delante_del_cabezal": CORREDOR}):
        p1 = dataclasses.replace(tanteo, talud_delante=PUNTO_1)
        p2 = dataclasses.replace(tanteo, talud_delante=PUNTO_2)
        r1 = _rcbc_del_ensamble(p1, monkeypatch)
        r2 = _rcbc_del_ensamble(p2, monkeypatch)
        rc = _rcbc_del_ensamble(tanteo, monkeypatch)
    # cada punto con SU talud, y el de corredor solo sin talud del punto
    for vistos, talud in ((r1, PUNTO_1), (r2, PUNTO_2), (rc, CORREDOR)):
        assert [x for h, b, _ in vistos for x in (h, b)] == pytest.approx(
            [talud["H_s_m"], talud["beta_grados"]] * len(vistos),
            rel=REL_TRANSPORTE)
    rc1 = {x for _, _, x in r1}
    rc2 = {x for _, _, x in r2}
    assert rc1.isdisjoint(rc2)


# ===========================================================================
# Dictamen Fable, abierto (iii): el terreno de delante tambien por punto
# ===========================================================================

def _q_del_portante(entorno, monkeypatch):
    """Los (H_s, beta, RC_BC) con que el ensamble paso por la zapata en
    talud; vacio si no paso."""
    vistos = []
    original = M9.capacidad_portante_zapata_en_talud

    def espia(**kw):
        q, det = original(**kw)
        vistos.append((kw["H_s"], kw["beta_grados"], det["RC_BC"]))
        return q, det

    monkeypatch.setattr(M9, "capacidad_portante_zapata_en_talud", espia)
    e = M9.ensamble_estabilidad(entorno, EST)
    monkeypatch.setattr(M9, "capacidad_portante_zapata_en_talud", original)
    return vistos, e


def _dice_del_punto(e):
    return any("terreno delante: del punto" in str(p) for p in e.pasos) or \
        any("terreno delante: del punto" in str(v.paso)
            for v in e.verificaciones)


def test_la_clave_admite_horizontal_por_extremo():
    assert M9.validar_talud_delante_del_punto("horizontal") == {
        "entrada": "horizontal", "salida": "horizontal"}
    assert M9.validar_talud_delante_del_punto(
        {"entrada": "horizontal", "salida": PUNTO_1}) == {
        "entrada": "horizontal", "salida": PUNTO_1}
    with pytest.raises(DatoInvalidoError):
        M9.validar_talud_delante_del_punto("vertical")


def test_el_talud_del_punto_activa_la_zapata_en_talud_con_corredor_horizontal(
        tanteo, monkeypatch):
    with declarados({"terreno_delante_del_cabezal": "horizontal"}):
        vistos, e = _q_del_portante(
            dataclasses.replace(tanteo, talud_delante=PUNTO_1), monkeypatch)
        assert vistos
        assert [x for h, b, _ in vistos for x in (h, b)] == pytest.approx(
            [2.0, 15.0] * len(vistos), rel=REL_TRANSPORTE)
        assert _dice_del_punto(e)
        sin, _ = _q_del_portante(tanteo, monkeypatch)
    assert not sin


def test_horizontal_del_punto_gana_a_un_corredor_en_talud(
        tanteo, monkeypatch):
    with declarados({"terreno_delante_del_cabezal": "talud_descendente",
                     "talud_delante_del_cabezal": CORREDOR}):
        vistos, e = _q_del_portante(
            dataclasses.replace(tanteo, talud_delante="horizontal"),
            monkeypatch)
    assert not vistos
    assert _dice_del_punto(e)


def test_sin_declaracion_rige_el_corredor(tanteo, monkeypatch):
    with declarados({"terreno_delante_del_cabezal": "talud_descendente",
                     "talud_delante_del_cabezal": CORREDOR}):
        vistos, e = _q_del_portante(tanteo, monkeypatch)
    assert vistos
    assert [x for h, b, _ in vistos for x in (h, b)] == pytest.approx(
        [4.0, 20.0] * len(vistos), rel=REL_TRANSPORTE)
    assert not _dice_del_punto(e)
