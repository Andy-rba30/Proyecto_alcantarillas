"""
M10_espaciamiento.py
=====================
Fase 10 de la hoja de ruta: espaciamiento maximo entre alcantarillas de
alivio (Familia B).

    espaciamiento_max = min(L_normativo, L_hidraulico)

L_normativo es el limite de num. 4.1.2.1 d), pag. 178: longitud maxima de
cuneta segun el regimen pluviometrico. La hoja de ruta lo ADOPTA en 200 m
-- el regimen normal de Piura es arido (250 m), pero el evento de diseno
relevante es el FEN, durante el cual la zona se comporta como region muy
lluviosa (Sec. 10, sensibilidad declarada (200, 250)) -- y ese valor vive en
`criterios_adoptados.valor('long_max_cuneta')`, nunca repetido aqui.

Lo que este modulo NO calcula
------------------------------
L_hidraulico: la longitud a la que la cuneta agota su capacidad admisible
frente al caudal aportante por metro lineal. Sec. 10 punto 2 describe el
procedimiento completo -- disenar la cuneta, capacidad admisible con borde
libre, caudal aportante por area tributaria e intensidad de TR = 35 anios,
longitud a la que se agota la capacidad -- pero no fija la seccion
transversal de la cuneta, su n de Manning, la formula de intensidad ni el
metodo de area tributaria. Ningun numeral de la hoja de ruta los trae.
Rellenar esos vacios en silencio es exactamente el error que Sec. 0 prohibe,
de modo que `espaciamiento_alivio()` EXIGE `L_hidraulico` como argumento ya
resuelto, en vez de derivarlo -- el mismo patron que `MD.disenar_punto` usa
para L y TW (Sec. 4 / 7.B), que tampoco calcula por no tener la regla.

Cual gobierna
-------------
El espaciamiento de diseno es el MENOR de los dos: cada limite es una
restriccion independiente y la que exige mas alivio es la que manda.
`espaciamiento_alivio()` devuelve el par (L, GobiernaEspaciamiento) dentro de
`Espaciamiento`, junto a los dos limites por separado -- nunca el minimo a
secas: un espaciamiento sin la etiqueta de que limite lo produjo no le dice
al revisor si el remedio esta en la norma (replantear puntos de alivio) o en
la cuneta (seccion, pendiente, area tributaria).

Excepciones
-----------
    CriterioPendienteError   'long_max_cuneta' sin valor (hoy tiene 200.0;
                             se detiene solo si alguien lo vacia).
    DatoInvalidoError        L_hidraulico no es un numero fisico positivo.

Uso
---
    from modulos.M10_espaciamiento import espaciamiento_alivio

    espaciamiento = espaciamiento_alivio(L_hidraulico=180.0)
    espaciamiento.espaciamiento_max, espaciamiento.gobierna
"""

from __future__ import annotations

import math

import criterios_adoptados as ca
from modelos import DatoInvalidoError, Espaciamiento, GobiernaEspaciamiento

NUMERAL_FASE_10 = "Fase 10 (num. 4.1.2.1 d), pag. 178)"

CRITERIO_LONG_MAX_CUNETA = "long_max_cuneta"


def espaciamiento_alivio(L_hidraulico: float) -> Espaciamiento:
    """
    Espaciamiento maximo entre alcantarillas de alivio, Sec. 10:

        espaciamiento_max = min(L_normativo, L_hidraulico)

    `L_hidraulico` llega resuelto por quien llama (ver el docstring del
    modulo): la longitud, en metros, a la que la cuneta agota su capacidad
    admisible con borde libre frente al caudal aportante de TR = 35 anios.

    `L_normativo` sale de `criterios_adoptados.valor('long_max_cuneta')`
    -- 200 m adoptado por el regimen FEN -- y lanza CriterioPendienteError
    si algun dia se deja sin valor.
    """
    if not math.isfinite(L_hidraulico) or L_hidraulico <= 0.0:
        raise DatoInvalidoError(
            campo="L_hidraulico",
            valor=L_hidraulico,
            motivo="la longitud por capacidad hidraulica de la cuneta debe "
                   "ser un numero finito positivo (Sec. 10, punto 2)",
        )

    L_normativo = ca.valor(CRITERIO_LONG_MAX_CUNETA)

    if L_hidraulico < L_normativo:
        gobierna = GobiernaEspaciamiento.HIDRAULICO
        espaciamiento_max = L_hidraulico
    else:
        gobierna = GobiernaEspaciamiento.NORMATIVO
        espaciamiento_max = L_normativo

    return Espaciamiento(
        L_normativo=L_normativo,
        L_hidraulico=L_hidraulico,
        espaciamiento_max=espaciamiento_max,
        gobierna=gobierna,
        criterio_normativo=CRITERIO_LONG_MAX_CUNETA,
        numeral=NUMERAL_FASE_10,
    )
