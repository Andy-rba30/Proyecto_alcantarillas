# -*- coding: utf-8 -*-
"""
responsable.py
==============
QUIEN resuelve un criterio pendiente y CON QUE evidencia, derivado de la
ficha (E-B, E13 reducido).

Por que existe este archivo
---------------------------
El tablero de la pestaña 4 y el anticipo de la pestaña 1 listan criterios
sin valor: dicen QUE falta y en que fase, y hasta E-B no decian a QUIEN
tocaba resolverlo ni con que documento. Las dos respuestas ya estaban
escritas en cada ficha --- son `Criterio.resolucion` (que lo fija: el
proyectista sobre una tabla, un ensayo, un catalogo, el programa) y
`Criterio.reemplazado_por` (el ensayo o dato que sustituye la adopcion) --- y
lo unico que faltaba era leerlas desde ahi. Este modulo NO escribe una
responsabilidad nueva para ningun criterio: la deriva, con una regla por tipo
de resolucion, y por eso vive aparte y sin estado: lo importan `anticipo.py`
(antes de correr) y `M11_reporte` (`criterios_bloqueantes`, despues), y una
lista escrita a mano en cualquiera de los dos divergiria de la ficha.

El dictamen (§2.2, P12) rechazo una «matriz requisito-aplicabilidad-
responsable-evidencia» porque no tenia forma en el esquema
`Fuente/Cita/Ausencia/Discrepancia`. Esto no es esa matriz: son dos columnas
leidas de objetos que ya existen, y el anticipo sigue siendo INFORMATIVO
(00_LEEME_DICTAMEN §3: ninguna estimacion gobierna un boton).

Vale para un `Criterio` y para un `DatoSitio`: los dos llevan `resolucion`,
`reemplazado_por` y `fuente`, que es lo que `ca.declaracion_de` promete a
`criterios_bloqueantes` (SIS-A-05).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.modelos import (DeCatalogo, DeEnsayo, Derivada, DeTabla, EnRango,
                         Libre)


@dataclass(frozen=True)
class Responsabilidad:
    """
    `responsable`: quien tiene que aportar el valor, segun como se resuelve.
    `evidencia`: con que se sostiene: lo que la ficha declara que sustituye
    la adopcion (`reemplazado_por`); si no lo declara, la trazabilidad que el
    ensayo exige; y si tampoco, la `fuente`, que en un criterio vacio es el
    enunciado de lo que hay que conseguir.
    """
    responsable: str
    evidencia: str


def responsable_de(resolucion: Any) -> str:
    """Quien fija el valor, leido del TIPO de la resolucion (Sec. 4.3)."""
    if isinstance(resolucion, Libre):
        return resolucion.que_lo_fija
    if isinstance(resolucion, DeEnsayo):
        return f"ensayo o medicion: {resolucion.ensayo}"
    if isinstance(resolucion, DeTabla):
        return (f"el proyectista, eligiendo sobre {', '.join(resolucion.tablas)}: "
                f"{resolucion.que_elige}")
    if isinstance(resolucion, EnRango):
        return (f"el proyectista, dentro del rango de {resolucion.tabla_id}: "
                f"{resolucion.que_acota}")
    if isinstance(resolucion, DeCatalogo):
        return (f"el proyectista, sobre el catalogo {resolucion.catalogo_id} "
                f"(que NO es una norma): {resolucion.que_elige}")
    if isinstance(resolucion, Derivada):
        return f"el programa, desde {', '.join(resolucion.de)}: {resolucion.regla}"
    return ""


def evidencia_de(declarado: Any) -> str:
    """Lo que sustituye o sostiene el valor, en el orden de la ficha."""
    reemplazado_por = getattr(declarado, "reemplazado_por", None)
    if reemplazado_por:
        return reemplazado_por
    resolucion = getattr(declarado, "resolucion", None)
    if isinstance(resolucion, DeEnsayo) and resolucion.trazabilidad_exigida:
        return resolucion.trazabilidad_exigida
    trazabilidad = getattr(declarado, "trazabilidad", None)
    if trazabilidad:
        return trazabilidad
    return getattr(declarado, "fuente", "") or ""


def responsabilidad_de(declarado: Any) -> Responsabilidad:
    """La pareja (responsable, evidencia) de un `Criterio` o un `DatoSitio`."""
    return Responsabilidad(
        responsable=responsable_de(getattr(declarado, "resolucion", None)),
        evidencia=evidencia_de(declarado))
