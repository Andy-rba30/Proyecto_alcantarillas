"""
tests/test_ve7_lote_a_empuje_declarado.py
=========================================
VE-7, lote A (triaje VE-7 de Fable, 2026-11-20), A5 (fichas VE5M9-02 y
VE3-15): la puerta `empuje_sismico_declarado`, por punto y por cabezal, con
el dictamen de Fable sobre el lote A (5.1 a 5.8) aplicado.

Se consume SOLO donde `cargas_del_cabezal` levanta hoy
MetodoNoEvaluableError -- la cuña SISMICA sin maximo con psi >= phi (GLE de
A11.3.3) y el relleno muy abierto con agua (presion hidrodinamica) --, solo
si el analisis declarado es del MISMO k_h y k_v y de un plano no mas bajo,
y nunca sustituye un empuje que el programa calcula. El oraculo del
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
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.test_t7c_cabezal_armado import tanteo  # noqa: F401

SIS = CondicionAnalisis.SISMICO
EST = CondicionAnalisis.ESTATICO
TOL = 1e-9
# phi del relleno del muro de tanteo = 30 grados: con k_h = 0.70 psi =
# arctan(0.70) = 34.99 grados >= phi y la cuña no tiene maximo.
K_H_INESTABLE = 0.70
K_H_TANTEO = 0.25
PLANO = 10.0
TRAZA = {"documento": "EMS-PRUEBA-01", "fecha": "2026-11-20",
         "metodo": "GLE (Spencer), de prueba"}


def _declarado(P_AE=60.0, z=0.80, hidro=False, k_h=K_H_INESTABLE, k_v=0.0,
               plano=PLANO):
    return {"P_AE_kn_m": P_AE, "altura_aplicacion_m": z,
            "incluye_hidrodinamica": hidro, "k_h": k_h, "k_v": k_v,
            "altura_plano_m": plano, **TRAZA}


def _inestable(monkeypatch):
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h=K_H_INESTABLE, k_v=0.0, k_h0=K_H_INESTABLE))


def test_la_puerta_valida_la_forma_y_va_solo_por_punto(tmp_path):
    ok = M9.validar_empuje_sismico_declarado({"entrada": _declarado()})
    assert ok["entrada"][0]["P_AE_kn_m"] == pytest.approx(
        60.0, rel=REL_TRANSPORTE)
    assert ok["salida"] == []
    sin_traza = {k: v for k, v in _declarado().items() if k not in TRAZA}
    comun = M9.validar_empuje_sismico_declarado({**TRAZA, "salida": [
        sin_traza, dict(sin_traza, k_h=0.30)]})
    assert [d["documento"] for d in comun["salida"]] == ["EMS-PRUEBA-01"] * 2
    for malo in ({"entrada": {"P_AE_kn_m": 10}},
                 {"entrada": dict(_declarado(), P_AE_kn_m=-1)},
                 {"entrada": dict(_declarado(), incluye_hidrodinamica=1)},
                 {"entrada": {k: v for k, v in _declarado().items()
                              if k != "k_h"}},
                 {"entrada": dict(_declarado(), k_v=1.0)},
                 {"entrada": dict(_declarado(), altura_plano_m=0)},
                 {"entrada": {k: v for k, v in _declarado().items()
                              if k != "documento"}},
                 {"entrada": [_declarado(), _declarado()]},
                 {"entrada": [_declarado(k_h=x) for x in (0.1, 0.2, 0.3)]},
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


def _a_mano(est, P_AE, z_AE, P_ref, h_medios=True):
    """z_dP del dictamen 5.4 con el piso de h/2 del muro que no cede."""
    dP = P_AE - P_ref
    z = max((P_AE * z_AE - P_ref * est["z_A"]) / dP, est["h"] / 3)
    if h_medios:
        z = max(z, (P_AE * est["h"] / 2 - P_ref * est["z_A"]) / dP)
    return dP, z


def test_con_psi_mayor_que_phi_el_declarado_deja_de_bloquear(
        tanteo, monkeypatch):
    _inestable(monkeypatch)
    entorno = dataclasses.replace(tanteo, empuje_sismico=[_declarado()])
    resultado = M9.ensamble_estabilidad(entorno, SIS)
    assert resultado is not None
    cargas, datos = M9.cargas_del_cabezal(entorno, SIS)
    _, est = M9.cargas_del_cabezal(tanteo, EST)
    P_A_h = est["P_A"] * math.cos(est["inclinacion"])
    # el muro de tanteo: 'cedente' sin la reduccion -> no cede, piso h/2
    dP, z = _a_mano(est, 60.0, 0.80, P_A_h)
    por = {c.codigo: c for c in cargas}
    assert por["EQ.dPAE.h"].H == pytest.approx(dP, abs=TOL)
    assert por["EQ.dPAE.v"].V == pytest.approx(0.0, abs=ABS_CERO)
    assert por["EQ.dPAE.h"].z == pytest.approx(z, abs=TOL)
    assert datos["empuje_sismico_declarado"]["documento"] == "EMS-PRUEBA-01"
    assert datos["metodo_incremento"] == M9.METODO_INCREMENTO_DECLARADO
    # el paso 9.2.4 lo dice y cita la validez, el GLE y la distribucion
    pasos = [p for p in resultado.pasos if p.codigo.startswith("9.2.4")]
    assert pasos and "DECLARADO" in pasos[0].nota_del_proyecto
    for cita in ("AASHTO_LRFD_9.11.6.5.3#VALIDEZ",
                 "AASHTO_LRFD_9.3.11.5.8.1#CUNA",
                 "AASHTO_LRFD_9.11.6.5.3#DISTRIBUCION"):
        assert cita in pasos[0].citas_textuales


def test_k_h_distinto_no_se_usa_y_el_bloqueo_lo_dice(tanteo, monkeypatch):
    _inestable(monkeypatch)
    entorno = dataclasses.replace(
        tanteo, empuje_sismico=[_declarado(k_h=0.50)])
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M9.cargas_del_cabezal(entorno, SIS)
    assert "NO casa" in str(exc.value)
    assert "k_h = 0.7" in str(exc.value)


def test_altura_del_plano_mayor_que_la_declarada_no_se_usa(
        tanteo, monkeypatch):
    _inestable(monkeypatch)
    _, est = M9.cargas_del_cabezal(tanteo, EST)
    bajo = dataclasses.replace(
        tanteo, empuje_sismico=[_declarado(plano=est["h"] - 0.10)])
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M9.cargas_del_cabezal(bajo, SIS)
    assert "plano analizado" in str(exc.value)
    # un plano declarado MAS ALTO que el del ensamble si se usa, entero
    alto = dataclasses.replace(
        tanteo, empuje_sismico=[_declarado(plano=est["h"] + 0.50)])
    _, datos = M9.cargas_del_cabezal(alto, SIS)
    assert datos["P_AE"] == pytest.approx(60.0, rel=REL_TRANSPORTE)


def test_p_ae_menor_que_el_activo_se_rechaza(tanteo, monkeypatch):
    _inestable(monkeypatch)
    _, est = M9.cargas_del_cabezal(tanteo, EST)
    P_A_h = est["P_A"] * math.cos(est["inclinacion"])
    entorno = dataclasses.replace(
        tanteo, empuje_sismico=[_declarado(P_AE=0.5 * P_A_h)])
    with pytest.raises(DatoInvalidoError) as exc:
        M9.cargas_del_cabezal(entorno, SIS)
    assert exc.value.campo.endswith("P_AE_kn_m")
    assert "solo el incremento" in str(exc.value)


def test_no_cedente_honra_reposo_mas_incremento(tanteo, monkeypatch):
    _inestable(monkeypatch)
    ca.establecer_valor_dinamico("regimen_cabezal", "no_cedente")
    _, est = M9.cargas_del_cabezal(tanteo, EST)
    assert est["empuje_estatico"] == M9.EMPUJE_ESTATICO_REPOSO
    P_A_h = est["P_A"] * math.cos(est["inclinacion"])
    entorno = dataclasses.replace(tanteo, empuje_sismico=[_declarado()])
    for forma, P_ref in (("reposo_mas_incremento", P_A_h),
                         ("mayor_de_reposo_y_total", est["P_0"])):
        ca.establecer_valor_dinamico("empuje_sismico_muro_que_no_cede",
                                     forma)
        cargas, datos = M9.cargas_del_cabezal(entorno, SIS)
        por = {c.codigo: c for c in cargas}
        assert por["EQ.dPAE.h"].H == pytest.approx(60.0 - P_ref, abs=TOL)
        assert datos["empuje_sismico_no_cede"] == forma


def test_el_momento_total_no_baja_del_declarado(tanteo, monkeypatch):
    """Sum M de EH.h + EQ.dPAE.h sobre la base >= P_AE·z_AE, tambien con
    la resultante declarada baja (sin el techo que hubo hasta el dictamen)."""
    _inestable(monkeypatch)
    for z_AE in (0.30, 0.80, 1.40):
        entorno = dataclasses.replace(
            tanteo, empuje_sismico=[_declarado(z=z_AE)])
        cargas, _ = M9.cargas_del_cabezal(entorno, SIS)
        por = {c.codigo: c for c in cargas}
        M = sum(por[k].H * por[k].z for k in ("EH.h", "EQ.dPAE.h"))
        assert M >= 60.0 * z_AE - TOL


def test_k_ae_equivalente_solo_se_imprime(tanteo, monkeypatch):
    _inestable(monkeypatch)
    entorno = dataclasses.replace(tanteo, empuje_sismico=[_declarado()])
    resultado = M9.ensamble_estabilidad(entorno, SIS)
    assert all(s.coeficiente_de_empuje == "K_AE (equivalente del declarado)"
               for s in resultado.solicitaciones)


def test_nunca_sustituye_un_empuje_que_el_programa_calcula(tanteo):
    """Con el k_h del muro de tanteo la cuña tiene maximo: el declarado
    (con una cifra absurda y el mismo k_h) no se usa, y se avisa."""
    sin = M9.cargas_del_cabezal(tanteo, SIS)
    entorno = dataclasses.replace(
        tanteo, empuje_sismico=[_declarado(P_AE=999.0, k_h=K_H_TANTEO)])
    con = M9.cargas_del_cabezal(entorno, SIS)
    assert con[1]["empuje_sismico_declarado"] is None
    assert con[1]["empuje_declarado_no_usado"]
    assert {c.codigo: c.H for c in con[0]} == pytest.approx(
        {c.codigo: c.H for c in sin[0]}, rel=REL_TRANSPORTE)
    avisos = M9.ensamble_estabilidad(entorno, SIS).avisos
    assert any("declarado y NO usado" in a for a in avisos)


def test_la_cuna_estatica_que_falla_no_se_sustituye(tanteo, monkeypatch):
    """5.8: el `try` solo captura la cuña SISMICA (la de k_h)."""
    _inestable(monkeypatch)
    original = M9.cuna_de_tanteo

    def estatica_falla(**kw):
        if not kw.get("k_h"):
            raise MetodoNoEvaluableError("estatica", "de prueba",
                                         "la cuña estatica de prueba falla")
        return original(**kw)

    monkeypatch.setattr(M9, "cuna_de_tanteo", estatica_falla)
    entorno = dataclasses.replace(tanteo, empuje_sismico=[_declarado()])
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M9.cargas_del_cabezal(entorno, SIS)
    assert "cuña estatica de prueba" in str(exc.value)


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
        M9.cargas_del_cabezal(dataclasses.replace(entorno, empuje_sismico=[
            _declarado(hidro=False, k_h=K_H_TANTEO)]), SIS)
    assert "incluye_hidrodinamica" in exc.value.campo
    cargas, datos = M9.cargas_del_cabezal(dataclasses.replace(
        entorno, empuje_sismico=[_declarado(hidro=True, k_h=K_H_TANTEO)]),
        SIS)
    assert datos["metodo_incremento"] == M9.METODO_INCREMENTO_DECLARADO
