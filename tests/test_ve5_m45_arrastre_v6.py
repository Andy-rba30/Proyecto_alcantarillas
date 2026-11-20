"""
tests/test_ve5_m45_arrastre_v6.py
=================================
VE-5, lote m45, item 18 (fichas EXT-2-01 y T3-05): V6 nunca aceptaba la
multicelda porque faltaba el dato del ARRASTRE del cauce. El Manual, num.
4.1.1.3.4 a) (pag. impresa 72, PDF 75; cita MC_HHD.4.1.1.3.4a#MULTIPLES),
condiciona la recomendacion de seccion libre sin subdivisiones a «la
capacidad de arrastre del curso natural (palizada, troncos y material de
cauce)». Se abre la puerta: `arrastre_de_solidos`, booleano por punto de
--datos-externos ([S] de la inspeccion del cauce), que V6 lee con N > 1.

Es la reescritura que la ficha EXT-2-01 pedia «en la misma sesion» para
`test_V6_sigue_rechazando_el_multicelda`, que sigue valiendo SIN el dato.

SE ESCRIBIO EN ROJO PRIMERO: la clave no existia y V6 no tenia `expediente`.
"""

from __future__ import annotations

import json

import pytest

from src import servicio
from src import variables_entrada as ve
from src.modelos import DatoInvalidoError, DatosDeExpediente, SeccionRectangular
from src.modulos.M5_verificaciones import (CLAVE_ARRASTRE_DE_SOLIDOS,
                                           v6_material_solido_arrastre)
from src.variables_entrada import Poblacion
from tests.apoyo.criterios import declarados
from tests.test_ext2_multicelda_transicion import CAJON_N3, _marco

ORIGEN_DE_PRUEBA = "dato de prueba"
SECCION = SeccionRectangular(B=2.00, H=1.50)


def _v6(arrastre, celdas=CAJON_N3):
    expediente = DatosDeExpediente(arrastre_de_solidos=arrastre,
                                   origen_arrastre=ORIGEN_DE_PRUEBA)
    with declarados(celdas):
        return v6_material_solido_arrastre(material=_marco(), seccion=SECCION,
                                           Q=9.0, expediente=expediente)


def test_la_clave_es_un_dato_externo_booleano_con_via_alterna():
    assert CLAVE_ARRASTRE_DE_SOLIDOS == "arrastre_de_solidos"
    assert servicio.CLAVE_ARRASTRE_DE_SOLIDOS == CLAVE_ARRASTRE_DE_SOLIDOS
    assert CLAVE_ARRASTRE_DE_SOLIDOS in servicio.CLAVES_EXTERNAS
    assert CLAVE_ARRASTRE_DE_SOLIDOS in servicio.CLAVES_BOOLEANAS
    # sin el dato V6 no se detiene: rechaza la multicelda
    assert CLAVE_ARRASTRE_DE_SOLIDOS in servicio.EXTERNOS_CON_VIA_ALTERNA
    # V6 corre en las tres familias: sin fila, las tres
    assert len(servicio.familias_que_usan(CLAVE_ARRASTRE_DE_SOLIDOS)) == 3
    assert ve.variable(CLAVE_ARRASTRE_DE_SOLIDOS).poblacion is \
        Poblacion.DATO_EXTERNO


def test_multicelda_en_cauce_sin_arrastre_se_acepta():
    v = _v6(False)
    assert v.cumple
    assert "NO arrastra" in v.valor_obtenido
    assert ORIGEN_DE_PRUEBA in v.valor_obtenido
    sustitucion = {m.simbolo: m.valor for m in v.paso.sustitucion}
    assert sustitucion["N_celdas"] == 3
    assert sustitucion["arrastre"] == "no"


def test_multicelda_en_cauce_con_arrastre_no_se_acepta():
    v = _v6(True)
    assert not v.cumple
    assert "ARRASTRA" in v.valor_obtenido


def test_multicelda_sin_el_dato_sigue_sin_aceptarse():
    v = _v6(None)
    assert not v.cumple
    assert {m.simbolo: m.valor for m in v.paso.sustitucion}["arrastre"] == \
        "no declarado"


def test_con_una_celda_el_dato_no_cuenta():
    una = dict(CAJON_N3, n_celdas_cajon=1)
    for arrastre in (True, False, None):
        v = _v6(arrastre, una)
        assert v.cumple
        assert "arrastre" not in {m.simbolo for m in v.paso.sustitucion}


def _externos(tmp_path, puntos):
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps({"globales": {}, "puntos": puntos}),
                    encoding="utf-8")
    return servicio.cargar_datos_externos(ruta, {})


def test_la_carga_admite_solo_un_booleano(tmp_path):
    ext = _externos(tmp_path, {"P-1": {CLAVE_ARRASTRE_DE_SOLIDOS: False}})
    assert ext.valor("P-1", CLAVE_ARRASTRE_DE_SOLIDOS) is False
    with pytest.raises(DatoInvalidoError):
        _externos(tmp_path, {"P-1": {CLAVE_ARRASTRE_DE_SOLIDOS: "no"}})
    with pytest.raises(DatoInvalidoError):
        _externos(tmp_path, {"P-1": {CLAVE_ARRASTRE_DE_SOLIDOS: 0}})
