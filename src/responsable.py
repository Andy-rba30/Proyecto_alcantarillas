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
from typing import Any, Optional

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


def donde_se_declara_criterio(clave: str) -> str:
    """
    En que lugar de la interfaz o de la entrada se declara un criterio o un
    dato de sitio `[S]` pendiente (C4). Derivado dinamicamente desde
    `datos_sitio.DATOS_SITIO` y `criterios_adoptados.CRITERIOS`, sin listas
    manuales.
    """
    from src import criterios_adoptados as _ca
    from src import datos_sitio as _ds

    if clave in _ds.DATOS_SITIO:
        return "Pestaña 1 -> Datos de sitio (archivo sitio.json) o CLI --datos-sitio"
    if clave in _ca.CRITERIOS:
        return ("Pestaña 2 -> Criterios ('Aplicar solo a esta corrida') "
                "o CLI --declarar")
    try:
        declarado = _ca.declaracion_de(clave)
    except KeyError:
        return "Pestaña 2 -> Criterios o Pestaña 1 -> Datos de entrada"
    if getattr(declarado, "etiqueta", "") == "S":
        return "Pestaña 1 -> Datos de sitio (sitio.json) o --datos-externos"
    return "Pestaña 2 -> Criterios o CLI --declarar"


def donde_se_declara_dato(campo: Optional[str]) -> str:
    """
    En que lugar de la interfaz o de los archivos de entrada se declara un dato
    cuya ausencia o invalidez detuvo una etapa (C4). Se deriva de
    `M0_carga.COLUMNAS`, `datos_sitio.DATOS_SITIO`, `sesion.CLAVE_EXTERNA_DE_CAMPO`
    y las colecciones de claves de `servicio`.
    """
    from src import datos_sitio as _ds
    from src import servicio as _srv
    from src import sesion as _sesion
    from src.modulos import M0_carga as _m0
    from src.modulos import MH_hidrologia as _mh

    nombre = str(campo or "").strip()
    if not nombre:
        return "Pestaña 1 -> revisar entradas del punto (ver docs/manual_usuario.md)"
    raiz = nombre.split(".", 1)[0]

    es_columna = raiz in _m0.COLUMNAS
    es_externo = (
        raiz in _srv.CLAVES_EXTERNAS
        or raiz in _srv.CLAVES_DE_CABEZAL
        or raiz in _srv.CLAVES_DE_DURABILIDAD
        or raiz in _srv.CLAVES_DE_LICUEFACCION
    )
    en_ventana = raiz in set(_sesion.CLAVE_EXTERNA_DE_CAMPO.values())
    columnas_hidrologia = (
        set(_mh.COLUMNAS_CUENCAS)
        | set(_mh.COLUMNAS_CUENCAS_OPCIONALES)
        | set(_mh.COLUMNAS_ESTACION)
        | {"cuencas", "hidrologia"}
    )

    if es_columna and es_externo:
        return (f"Pestaña 1 -> Columna '{raiz}' del CSV de puntos "
                "o 'puntos' en datos_externos.json (--datos-externos)")
    if es_columna:
        return f"Pestaña 1 -> Columna '{raiz}' del CSV de puntos criticos"
    if raiz in _ds.DATOS_SITIO:
        return "Pestaña 1 -> Datos de sitio (archivo sitio.json) o CLI --datos-sitio"
    if es_externo and en_ventana:
        return (f"Pestaña 1 -> Campo '{raiz}' de datos externos "
                "o archivo datos_externos.json (--datos-externos)")
    if es_externo:
        return ("Pestaña 1 -> Archivo datos_externos.json "
                "('globales' o 'puntos') o CLI --datos-externos")
    if raiz in columnas_hidrologia:
        return "Pestaña 1 -> Archivos CSV de hidrologia (--cuencas / --estacion)"
    return "Pestaña 1 -> Datos de entrada (ver docs/manual_usuario.md)"
