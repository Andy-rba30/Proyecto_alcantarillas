"""
tests/test_bloqueos_diferidos.py
================================
Regresion del bloqueo de M8 (items 1-2) que, con el criterio DECLARADO,
reventaba la corrida completa con un `AssertionError` desnudo.
`AssertionError` no desciende de `ErrorProyecto`, de modo que `cli._etapa`
no lo capturaba y una sola declaracion tumbaba el proceso entero con todos
sus puntos, en vez de anotarse como bloqueo del punto y seguir.

Ahora sale como `CriterioPendienteError` -- que si es ErrorProyecto -- con
un mensaje que dice explicitamente que la seleccion queda DIFERIDA al
expediente tecnico. Es manejo de errores, no ingenieria: el procedimiento
real (leer la tabla clase x diametro x rango de altura de relleno) sigue
sin implementarse a proposito.

Este archivo cubria originalmente CUATRO gates (V8, clases_producto, E4 y
E5). Solo queda el de M8: V8, E4 y E5 ya no bloquean -- van diferidas al
expediente con el mecanismo no bloqueante de Fase 8, item 5
(`verificacion_diferida_hidraulica` en M5 y
`verificacion_diferida_estabilidad_global` en M9), y ese comportamiento lo
fijan tests/test_M5_verificaciones.py y tests/test_M9_cabezal.py.
`clases_producto_por_relleno` es de otra familia: SI tiene codigo real
esperando el dato (`seleccionar_clase_calibre`), asi que sigue bloqueando
limpio hasta que se consiga la tabla de AASHTO M-170M.

El criterio se declara con `establecer_valor_dinamico` y se retira en el
finally. Ningun test toca criterios_adoptados.py.
"""

import pytest

import criterios_adoptados as ca
from modelos import CriterioPendienteError, ErrorProyecto, TipoMaterial
from modulos.M2_material import catalogo
from modulos.M8_estructural import seleccionar_clase_calibre


def _con_declarado(clave, valor, fn):
    """Corre `fn` con el criterio declarado en caliente y lo retira siempre."""
    ca.establecer_valor_dinamico(clave, valor)
    try:
        return fn()
    finally:
        ca.quitar_valor_dinamico(clave)


def test_clase_calibre_con_tabla_declarada_no_revienta_con_assertionerror():
    """Regresion probada corriendo: declarar la tabla tumbaba el proceso."""
    concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)

    def llamada():
        with pytest.raises(CriterioPendienteError) as excinfo:
            seleccionar_clase_calibre(material=concreto, altura_relleno=1.0)
        return excinfo

    excinfo = _con_declarado("clases_producto_por_relleno",
                             {"declarada": True}, llamada)
    assert isinstance(excinfo.value, ErrorProyecto)
    assert not isinstance(excinfo.value, AssertionError)
    assert excinfo.value.clave == "clases_producto_por_relleno"
    assert "DIFERIDA al expediente tecnico" in str(excinfo.value)


def test_sin_declarar_sigue_deteniendose_en_ca_valor():
    """El primer freno no cambio: vacio -> CriterioPendienteError de ca.valor."""
    with pytest.raises(CriterioPendienteError) as excinfo:
        seleccionar_clase_calibre(
            material=catalogo(TipoMaterial.CONCRETO_REFORZADO),
            altura_relleno=1.0)
    assert excinfo.value.clave == "clases_producto_por_relleno"
