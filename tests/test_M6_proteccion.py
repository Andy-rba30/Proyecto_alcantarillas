"""
tests/test_M6_proteccion.py
============================
M6 contra Fase 6: d50 de Laushey (CP-4) y el ensamblado con criterios
adoptados de espesor y longitud.

    laushey_d50()        contra CP4_LAUSHEY (tests/fixtures/casos_patron.py).
    proteccion_salida()  espesor = 1.75 * d50 ('espesor_proteccion_salida');
                         CriterioPendienteError por 'longitud_proteccion_salida'
                         cuando esta vacio (`tests.apoyo.criterios.sin_valor`,
                         porque el criterio quedo declarado en S20); las dos
                         advertencias de Sec. 6 viajan en el resultado.
"""

import pytest

from modelos import CriterioPendienteError, ProteccionSalida
from modulos.M6_proteccion import (ADVERTENCIA_FALTA_FILTRO,
                                   ADVERTENCIA_NO_ES_DISENO,
                                   CRITERIO_ESPESOR, CRITERIO_LONGITUD,
                                   laushey_d50, proteccion_salida)
from tests.fixtures.casos_patron import CP4_LAUSHEY
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import sin_valor


@pytest.mark.parametrize("caso", CP4_LAUSHEY)
def test_laushey_d50_contra_casos_patron(caso):
    d50 = laushey_d50(V=caso["V"])
    assert d50 == pytest.approx(caso["d50_esperado"], abs=caso["tolerancia"])


def test_proteccion_salida_se_detiene_en_longitud_pendiente():
    """
    Sin 'longitud_proteccion_salida' la Fase 6 completa no devuelve resultado.

    El criterio quedo DECLARADO en S20, al cerrarse el nivel de perfil, y por
    eso el vacio se devuelve aqui dentro: lo que este test fija es el
    comportamiento del modulo ante un criterio vacio -- que se detiene y no
    rellena --, que es permanente, y no el estado del expediente, que no lo
    es.
    """
    with sin_valor(CRITERIO_LONGITUD):
        with pytest.raises(CriterioPendienteError) as exc:
            proteccion_salida(V=2.0)
        assert exc.value.clave == CRITERIO_LONGITUD


def test_proteccion_salida_calcula_espesor_antes_de_detenerse(monkeypatch):
    """
    Con 'longitud_proteccion_salida' declarado (simulado aqui), el resultado
    trae d50, espesor = 1.75*d50 y las dos advertencias de Sec. 6.
    """
    import criterios_adoptados as ca

    original = ca.CRITERIOS[CRITERIO_LONGITUD]
    monkeypatch.setitem(
        ca.CRITERIOS, CRITERIO_LONGITUD,
        original.__class__(**{**original.__dict__, "valor": 5.0}),
    )

    resultado = proteccion_salida(V=2.0)

    assert isinstance(resultado, ProteccionSalida)
    assert resultado.d50 == pytest.approx(0.13167, abs=1e-4)
    assert resultado.espesor == pytest.approx(1.75 * resultado.d50, abs=1e-9)
    assert resultado.longitud == pytest.approx(5.0, rel=REL_TRANSPORTE)
    assert resultado.criterio_espesor == CRITERIO_ESPESOR
    assert resultado.criterio_longitud == CRITERIO_LONGITUD
    assert ADVERTENCIA_NO_ES_DISENO in resultado.advertencias
    assert ADVERTENCIA_FALTA_FILTRO in resultado.advertencias
