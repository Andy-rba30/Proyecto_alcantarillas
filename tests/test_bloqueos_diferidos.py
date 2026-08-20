"""
tests/test_bloqueos_diferidos.py
================================
Regresion de los cuatro bloqueos que, con el criterio DECLARADO, reventaban
la corrida completa con un `AssertionError` desnudo. `AssertionError` no
desciende de `ErrorProyecto`, de modo que `cli._etapa` no lo capturaba y una
sola declaracion (p.ej. 'TR_evento_extremo') tumbaba el proceso entero con
todos sus puntos, en vez de anotarse como bloqueo del punto y seguir.

Ahora cada uno sale como `CriterioPendienteError` -- que si es ErrorProyecto
-- con un mensaje que dice explicitamente que la verificacion queda DIFERIDA
al expediente tecnico (mismo patron que la rigidez de anillo y el pandeo de
la Fase 8, item 5). Es manejo de errores, no ingenieria: el procedimiento
real de cada verificacion sigue sin implementarse a proposito.

Los criterios se declaran con `establecer_valor_dinamico` y se retiran en el
finally, el mismo patron del test de regresion de V5 en
tests/test_M5_verificaciones.py. Ningun test toca criterios_adoptados.py.
"""

import pytest

import criterios_adoptados as ca
from modelos import (CondicionAnalisis, CriterioPendienteError, ErrorProyecto,
                     TipoMaterial)
from modulos.M2_material import catalogo
from modulos.M5_verificaciones import v8_evento_extremo
from modulos.M8_estructural import seleccionar_clase_calibre
from modulos.M9_cabezal import verificar_estabilidad_global, verificar_talud

from tests.test_M5_verificaciones import _punto, _resultado


def _con_declarado(clave, valor, fn):
    """Corre `fn` con el criterio declarado en caliente y lo retira siempre."""
    ca.establecer_valor_dinamico(clave, valor)
    try:
        return fn()
    finally:
        ca.quitar_valor_dinamico(clave)


def _exige_diferido(excinfo, clave):
    """Lo comun a los cuatro: ErrorProyecto, la clave, y el mensaje diferido."""
    assert isinstance(excinfo.value, ErrorProyecto)
    assert not isinstance(excinfo.value, AssertionError)
    assert excinfo.value.clave == clave
    assert "DIFERIDA al expediente tecnico" in str(excinfo.value)


def test_v8_con_tr_declarado_no_revienta_con_assertionerror():
    """Regresion probada corriendo: declarar el TR tumbaba el proceso."""
    def llamada():
        with pytest.raises(CriterioPendienteError) as excinfo:
            v8_evento_extremo(punto=_punto(), resultado=_resultado())
        return excinfo

    excinfo = _con_declarado("TR_evento_extremo", 500, llamada)
    _exige_diferido(excinfo, "TR_evento_extremo")


def test_clase_calibre_con_tabla_declarada_no_revienta_con_assertionerror():
    concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)

    def llamada():
        with pytest.raises(CriterioPendienteError) as excinfo:
            seleccionar_clase_calibre(material=concreto, altura_relleno=1.0)
        return excinfo

    excinfo = _con_declarado("clases_producto_por_relleno",
                             {"declarada": True}, llamada)
    _exige_diferido(excinfo, "clases_producto_por_relleno")


@pytest.mark.parametrize("funcion", [verificar_estabilidad_global,
                                     verificar_talud])
@pytest.mark.parametrize("condicion", list(CondicionAnalisis))
def test_e4_y_e5_con_metodo_declarado_no_revientan_con_assertionerror(
        funcion, condicion):
    """E4 y E5 comparten el criterio y no el chequeo: se prueban las dos."""
    def llamada():
        with pytest.raises(CriterioPendienteError) as excinfo:
            funcion(condicion=condicion)
        return excinfo

    excinfo = _con_declarado("metodo_estabilidad_global",
                             "bishop_simplificado", llamada)
    _exige_diferido(excinfo, "metodo_estabilidad_global")


def test_sin_declarar_los_cuatro_siguen_deteniendose_en_ca_valor():
    """El primer freno no cambio: vacio -> CriterioPendienteError de ca.valor."""
    with pytest.raises(CriterioPendienteError) as excinfo:
        v8_evento_extremo(punto=_punto(), resultado=_resultado())
    assert excinfo.value.clave == "TR_evento_extremo"

    with pytest.raises(CriterioPendienteError) as excinfo:
        seleccionar_clase_calibre(
            material=catalogo(TipoMaterial.CONCRETO_REFORZADO),
            altura_relleno=1.0)
    assert excinfo.value.clave == "clases_producto_por_relleno"

    for funcion in (verificar_estabilidad_global, verificar_talud):
        with pytest.raises(CriterioPendienteError) as excinfo:
            funcion(condicion=CondicionAnalisis.ESTATICO)
        assert excinfo.value.clave == "metodo_estabilidad_global"
