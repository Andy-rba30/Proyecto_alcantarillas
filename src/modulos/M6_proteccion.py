"""
M6_proteccion.py
=================
Fase 6 de la hoja de ruta: proteccion de entrada y salida por Laushey.

    d50 = V^2 / (LAUSHEY_K * G_LAUSHEY)  num. 4.1.1.3.7 c), pag. 80

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

DIVERGENCIA DECLARADA ENTRE LAS DOS NORMAS DEL EXPEDIENTE (MAT-X6)
-------------------------------------------------------------------
Las dos fuentes que este proyecto usa para alcantarillas dimensionan la
proteccion de salida de forma distinta, y hasta ahora la divergencia no
estaba escrita en ninguna parte:

    Manual MTC, num. 4.1.1.3.7 c): d50 = V^2/(3.1*g). Funcion de UNA sola
        variable, la velocidad de salida.

    HDS-5 3a ed. (FHWA-HIF-12-026, abril 2012), Sec. 5.3.2 "Scour at
        Outlets", pag. impresa 5.11: remite el apron de enrocado a HEC-14
        Sec. 10.2, que lo dimensiona en funcion de Q, D y TW. Literal:
        "many state DOTs use riprap aprons (HEC-14, Section 10.2) to provide
        a minimum amount of protection for small culverts (...) Providing
        scour protection for large floods or when more serious erosion
        problems exist requires protection measures designed based on
        HEC-14."

QUE SE HACE Y POR QUE. Se calcula el d50 del Manual MTC y no el apron de
HEC-14. Dos razones, en este orden: (1) el Manual MTC es norma peruana
vigente [N] y HDS-5 entra en este proyecto como fuente tecnica [C] para
cubrir vacios del Manual -- aqui no hay vacio que cubrir, el Manual da
formula; (2) HEC-14 NO esta en normas/, de modo que su procedimiento no se
puede transcribir ni contrastar: no hay contradiccion NUMERICA demostrable,
solo dos alcances distintos.

QUE SIGNIFICA PARA EL REVISOR. Lo que el Manual entrega es un tamaño de
piedra, no un diseño de proteccion; lo que HDS-5 llama proteccion incluye
la geometria del apron, y para "large floods or more serious erosion
problems" remite entero a HEC-14. Las dos cosas apuntan al mismo sitio: lo
que este modulo calcula es un punto de partida, y la proteccion de salida se
cierra en el expediente. `ADVERTENCIA_ALCANCE_HDS5` lo transporta con el
resultado, junto a las otras dos.

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
from constantes_normativas import G_LAUSHEY, LAUSHEY_K
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
ADVERTENCIA_ALCANCE_HDS5 = (
    "Alcance: d50 sale del Manual MTC (num. 4.1.1.3.7 c), funcion solo de V. "
    "HDS-5 3a ed. (FHWA-HIF-12-026), Sec. 5.3.2 'Scour at Outlets', "
    "pag. 5.11, dimensiona el apron de enrocado "
    "por HEC-14 Sec. 10.2, en funcion de Q, D y TW, y remite a HEC-14 entero "
    "la proteccion frente a avenidas grandes. Se aplica el Manual MTC por ser "
    "norma peruana vigente y porque HEC-14 no esta en el expediente; la "
    "geometria de la proteccion se cierra en el expediente tecnico"
)
ADVERTENCIAS_PROTECCION_SALIDA: Tuple[str, ...] = (
    ADVERTENCIA_NO_ES_DISENO,
    ADVERTENCIA_FALTA_FILTRO,
    ADVERTENCIA_ALCANCE_HDS5,
)


# ---------------------------------------------------------------------------
# d50 - Laushey (num. 4.1.1.3.7 c)
# ---------------------------------------------------------------------------

def laushey_d50(*, V: float) -> float:
    """d50 = V^2 / (LAUSHEY_K * G_LAUSHEY), sistema metrico (num. 4.1.1.3.7 c)."""
    return V ** 2 / (LAUSHEY_K * G_LAUSHEY)


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

    Devuelve siempre las TRES advertencias: las dos de Sec. 6 -- d50 no es un
    diseño de enrocado, y falta el filtro -- y la del alcance frente a HDS-5,
    que dimensiona el apron por HEC-14 (ver la divergencia declarada en el
    docstring del modulo, MAT-X6).
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
