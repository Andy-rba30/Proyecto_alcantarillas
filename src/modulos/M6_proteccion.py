"""
M6_proteccion.py
=================
Fase 6 de la hoja de ruta: proteccion de entrada y salida por Laushey.

    d50 = V^2 / (LAUSHEY_K * G)          num. 4.1.1.3.7 c), pag. 80

`V` es la velocidad de salida en m/s (sistema metrico: la constante 3.1 de
Laushey asume metrico, no imperial); `d50` sale en metros. La formula es la
UNICA pieza de la Fase 6 con numeral normativo: espesor y longitud no estan
normados y se leen de `criterios_adoptados.py`, donde ambos viven etiquetados
[A] ("espesor_proteccion_salida", "longitud_proteccion_salida").

**d50 no es un diseño de enrocado.** La hoja de ruta (Sec. 6) lo dice de
forma expresa: falta completar con granulometria completa y FILTRO -- sin
filtro el enrocado se socava por debajo y falla. `proteccion_salida()`
transporta esa advertencia en el resultado para que ningun consumidor
(GUI, M11) la pierda de vista; no la resuelve, porque no hay con que.

Excepciones
-----------
    CriterioPendienteError   'longitud_proteccion_salida' esta vacio (Anexo A):
                             la Fase 6 se detiene ahi hasta que se declare un
                             valor, igual que V5/V7/V8 de M5.

Uso
---
    from modulos.M6_proteccion import laushey_d50, proteccion_salida

    d50 = laushey_d50(V=resultado.V)
    proteccion = proteccion_salida(V=resultado.V)   # exige 'longitud_proteccion_salida'
"""

from __future__ import annotations

from typing import Tuple

import criterios_adoptados as ca
from constantes_normativas import G, LAUSHEY_K
from modelos import ProteccionSalida

NUMERAL_LAUSHEY = "4.1.1.3.7 c)"

CRITERIO_ESPESOR = "espesor_proteccion_salida"
CRITERIO_LONGITUD = "longitud_proteccion_salida"

ADVERTENCIA_NO_ES_DISENO = (
    "d50 no es un diseño de enrocado: falta la granulometria completa "
    f"(Sec. 6 de la hoja de ruta, {NUMERAL_LAUSHEY})"
)
ADVERTENCIA_FALTA_FILTRO = (
    "Falta el filtro. Sin filtro el enrocado se socava por debajo y falla "
    "(Sec. 6 de la hoja de ruta)"
)
ADVERTENCIAS_PROTECCION_SALIDA: Tuple[str, ...] = (
    ADVERTENCIA_NO_ES_DISENO,
    ADVERTENCIA_FALTA_FILTRO,
)


# ---------------------------------------------------------------------------
# d50 - Laushey (num. 4.1.1.3.7 c)
# ---------------------------------------------------------------------------

def laushey_d50(*, V: float) -> float:
    """d50 = V^2 / (LAUSHEY_K * G), sistema metrico (num. 4.1.1.3.7 c)."""
    return V ** 2 / (LAUSHEY_K * G)


# ---------------------------------------------------------------------------
# Proteccion de salida completa: d50 + espesor + longitud + advertencia
# ---------------------------------------------------------------------------

def proteccion_salida(*, V: float) -> ProteccionSalida:
    """
    d50 de Laushey mas espesor y longitud, leidos de `criterios_adoptados.py`
    (ambos [A], Sec. 6). El espesor es el multiplicador de
    'espesor_proteccion_salida' (1.75) aplicado a d50; la longitud es
    'longitud_proteccion_salida', hoy sin valor -- la llamada se detiene con
    `CriterioPendienteError` hasta que se declare (ver el criterio en
    criterios_adoptados.py: la hoja de ruta no entrega un procedimiento).

    Devuelve siempre las dos advertencias de Sec. 6: d50 no es un diseño de
    enrocado, y falta el filtro.
    """
    d50 = laushey_d50(V=V)
    mult_espesor = ca.valor(CRITERIO_ESPESOR)
    espesor = mult_espesor * d50
    longitud = ca.valor(CRITERIO_LONGITUD)   # CriterioPendienteError mientras falte

    return ProteccionSalida(
        d50=d50,
        espesor=espesor,
        longitud=longitud,
        V=V,
        criterio_espesor=CRITERIO_ESPESOR,
        criterio_longitud=CRITERIO_LONGITUD,
        advertencias=ADVERTENCIAS_PROTECCION_SALIDA,
        numeral=NUMERAL_LAUSHEY,
    )
