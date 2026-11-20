"""
tests/test_ve7_lote_a_empuje_declarado.py
=========================================
VE-7, lote A (triaje VE-7 de Fable, 2026-11-20), A5 (fichas VE5M9-02 y
VE3-15): la puerta `empuje_sismico_declarado`, por punto y por cabezal.

Se consume SOLO donde `cargas_del_cabezal` levanta hoy
MetodoNoEvaluableError -- la cuña sin maximo con psi >= phi (GLE de
A11.3.3) y el relleno muy abierto con agua (presion hidrodinamica) --, y
nunca sustituye un empuje que el programa calcula. El oraculo del
incremento es la aritmetica escrita aqui sobre el P_A del ensamble.
"""

import dataclasses
import json
import math
from types import SimpleNamespace

import pytest

import cli
from src import criterios_adoptados as ca
from src import servicio
from src.modelos import (CondicionAnalisis, DatoInvalidoError,
                         MetodoNoEvaluableError)
from src.modulos import M9_cabezal as M9
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.test_t7c_cabezal_armado import tanteo  # noqa: F401

SIS = CondicionAnalisis.SISMICO
EST = CondicionAnalisis.ESTATICO
TOL = 1e-9
# phi del relleno del muro de tanteo = 30 grados: con k_h = 0.70 psi =
# arctan(0.70) = 34.99 grados >= phi y la cuña no tiene maximo.
K_H_INESTABLE = 0.70
TRAZA = {"documento": "EMS-PRUEBA-01", "fecha": "2026-11-20",
         "metodo": "GLE (Spencer), de prueba"}


def _declarado(P_AE=60.0, z=0.80, hidro=False):
    return {"P_AE_kn_m": P_AE, "altura_aplicacion_m": z,
            "incluye_hidrodinamica": hidro, **TRAZA}


def _inestable(monkeypatch):
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h=K_H_INESTABLE, k_v=0.0, k_h0=K_H_INESTABLE))


def test_la_puerta_valida_la_forma_y_va_solo_por_punto(tmp_path):
    ok = M9.validar_empuje_sismico_declarado(
        {"entrada": _declarado(), **{}})
    assert ok["entrada"]["P_AE_kn_m"] == pytest.approx(
        60.0, rel=REL_TRANSPORTE)
    assert ok["salida"] == {}
    comun = M9.validar_empuje_sismico_declarado(
        {**TRAZA, "salida": {"P_AE_kn_m": 10, "altura_aplicacion_m": 1,
                             "incluye_hidrodinamica": True}})
    assert comun["salida"]["documento"] == "EMS-PRUEBA-01"
    for malo in ({"entrada": {"P_AE_kn_m": 10}},
                 {"entrada": dict(_declarado(), P_AE_kn_m=-1)},
                 {"entrada": dict(_declarado(), incluye_hidrodinamica=1)},
                 {"entrada": {k: v for k, v in _declarado().items()
                              if k != "documento"}},
                 {"P_AE_kn_m": 10, **TRAZA}, {}, "x"):
        with pytest.raises(DatoInvalidoError):
            M9.validar_empuje_sismico_declarado(malo)
    assert "empuje_sismico_declarado" in servicio.CLAVES_DE_CABEZAL
    ruta = tmp_path / "g.json"
    ruta.write_text(json.dumps({"globales": {
        "empuje_sismico_declarado": {"entrada": _declarado()}}}),
        encoding="utf-8")
    with pytest.raises(DatoInvalidoError):
        cli.cargar_datos_externos(ruta, {})


def test_sin_declarar_el_bloqueo_nombra_la_clave(tanteo, monkeypatch):
    _inestable(monkeypatch)
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M9.ensamble_estabilidad(tanteo, SIS)
    assert "empuje_sismico_declarado" in str(exc.value)
    assert "GLE" in str(exc.value)


def test_con_psi_mayor_que_phi_el_declarado_deja_de_bloquear(
        tanteo, monkeypatch):
    _inestable(monkeypatch)
    entorno = dataclasses.replace(tanteo, empuje_sismico=_declarado())
    resultado = M9.ensamble_estabilidad(entorno, SIS)
    assert resultado is not None
    cargas, datos = M9.cargas_del_cabezal(entorno, SIS)
    # el incremento, a mano: P_AE declarado menos el estatico horizontal,
    # sin componente vertical, con la resultante total a la altura declarada
    _, est = M9.cargas_del_cabezal(tanteo, EST)
    P_est = est["P_A"] * math.cos(est["inclinacion"])
    dP = 60.0 - P_est
    por = {c.codigo: c for c in cargas}
    assert por["EQ.dPAE.h"].H == pytest.approx(dP, abs=TOL)
    assert por["EQ.dPAE.v"].V == pytest.approx(0.0, abs=TOL)
    z = (60.0 * 0.80 - P_est * est["z_A"]) / dP
    z = min(max(z, est["h"] / 3), est["h"])
    assert por["EQ.dPAE.h"].z == pytest.approx(z, abs=TOL)
    assert datos["empuje_sismico_declarado"]["documento"] == "EMS-PRUEBA-01"
    assert datos["metodo_incremento"] == M9.METODO_INCREMENTO_DECLARADO
    # el paso 9.2.4 lo dice y cita el GLE
    pasos = [p for p in resultado.pasos if p.codigo.startswith("9.2.4")]
    assert pasos and "DECLARADO" in pasos[0].nota_del_proyecto
    assert "AASHTO_LRFD_9.3.11.5.8.1#CUNA" in pasos[0].citas_textuales


def test_nunca_sustituye_un_empuje_que_el_programa_calcula(tanteo):
    """Con el k_h del muro de tanteo la cuña tiene maximo: el declarado
    (con una cifra absurda) no se usa."""
    sin = M9.cargas_del_cabezal(tanteo, SIS)
    con = M9.cargas_del_cabezal(dataclasses.replace(
        tanteo, empuje_sismico=_declarado(P_AE=999.0)), SIS)
    assert con[1]["empuje_sismico_declarado"] is None
    assert {c.codigo: c.H for c in con[0]} == pytest.approx(
        {c.codigo: c.H for c in sin[0]}, rel=REL_TRANSPORTE)


def _con_agua_muy_abierta(entorno):
    ca.establecer_valor_dinamico("agua_del_relleno_bajo_sismo",
                                 "relleno_muy_abierto")
    ca.establecer_valor_dinamico("peso_especifico_saturado_relleno_kn_m3",
                                 20.0)
    g = entorno.geometria
    return dataclasses.replace(
        entorno, cota_freatico=g.cota_desplante + g.espesor_zapata + 0.50)


def test_con_relleno_muy_abierto_exige_la_hidrodinamica(tanteo):
    entorno = _con_agua_muy_abierta(tanteo)
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M9.cargas_del_cabezal(entorno, SIS)
    assert "empuje_sismico_declarado" in str(exc.value)
    with pytest.raises(DatoInvalidoError) as exc:
        M9.cargas_del_cabezal(dataclasses.replace(
            entorno, empuje_sismico=_declarado(hidro=False)), SIS)
    assert "incluye_hidrodinamica" in exc.value.campo
    cargas, datos = M9.cargas_del_cabezal(dataclasses.replace(
        entorno, empuje_sismico=_declarado(hidro=True)), SIS)
    assert datos["metodo_incremento"] == M9.METODO_INCREMENTO_DECLARADO
