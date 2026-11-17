"""
tests/test_ve3_datos_de_ensayo_s.py
===================================
VE-3, parte 2 (ficha VE2-05, decision del dueño del 2026-11-17): los
parametros del suelo de fundacion (`c_phi_fundacion`) y la capacidad
portante admisible (`capacidad_portante_adm`) son [S] pendientes de
ensayo, no [A]. Salen del estudio de mecanica de suelos de ESTE sitio y no
hay rango que elegir: se defienden con la trazabilidad de la lectura
(CLAUDE.md, «Taxonomia»), la misma razon por la que N2 de VE-2 reetiqueto
el peso especifico saturado del relleno.

`Mw_licuefaccion` SE QUEDA [A]: elegir el escenario sismico (desagregacion
del peligro o el sismo de subduccion adoptado) es una decision del
proyectista, no la lectura de un ensayo.

El signo: la capacidad portante es un `float` y no puede ser <= 0, y lleva
`positivo` (el campo de N2). `c_phi_fundacion` es un dict con campos (un
booleano y tres numeros): `positivo` solo se declara en un numero escalar,
y sus campos los valida el consumidor (`M9.validar_suelo_fundacion`).

SE ESCRIBIO EN ROJO PRIMERO, contra adaa96a.
"""

from __future__ import annotations

import math
from dataclasses import replace

import pytest

from src import criterios_adoptados as ca

CLAVE_C_PHI = "c_phi_fundacion"
CLAVE_PORTANTE = "capacidad_portante_adm"
CLAVE_MW = "Mw_licuefaccion"


@pytest.mark.parametrize("clave", [CLAVE_C_PHI, CLAVE_PORTANTE])
def test_el_suelo_de_fundacion_es_s_con_trazabilidad(clave):
    c = ca.CRITERIOS[clave]
    assert c.etiqueta == "S"
    assert c.trazabilidad and "NO SE HA EJECUTADO" in c.trazabilidad
    assert c.sensibilidad is None
    assert isinstance(c.resolucion, ca.DeEnsayo)
    assert c.valor is None          # ningun valor de archivo cambia
    assert c.nivel == ca.NIVEL_EXPEDIENTE


def test_la_magnitud_de_licuefaccion_sigue_siendo_a():
    c = ca.CRITERIOS[CLAVE_MW]
    assert c.etiqueta == "A"
    assert c.trazabilidad is None


def test_la_capacidad_portante_declara_su_signo_y_c_phi_no():
    assert ca.CRITERIOS[CLAVE_PORTANTE].positivo is True
    assert ca.CRITERIOS[CLAVE_C_PHI].positivo is False


@pytest.mark.parametrize("valor", [0, 0.0, -150.0])
def test_la_capacidad_portante_no_entra_con_cero_ni_negativa(valor):
    c = replace(ca.CRITERIOS[CLAVE_PORTANTE], valor=valor)
    with pytest.raises(ValueError, match="positivo"):
        ca._verificar_criterio(CLAVE_PORTANTE, c)
    with pytest.raises(ValueError, match="positivo"):
        ca.verificar_declaracion(CLAVE_PORTANTE, valor)


def test_la_capacidad_portante_positiva_entra_y_el_nan_no():
    ca.verificar_declaracion(CLAVE_PORTANTE, 150.0)
    with pytest.raises(ValueError):
        ca.verificar_declaracion(CLAVE_PORTANTE, math.nan)
