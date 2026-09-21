# -*- coding: utf-8 -*-
"""
anticipo.py
===========
EL CONTENIDO del panel «Anticipo antes de correr» de la pestana 1 (G3): lo
que se puede saber ANTES de ejecutar el pipeline, en tres bloques, todos
DERIVADOS.

Que es esto, y por que no esta en gui/
--------------------------------------
El mismo reparto que `ayuda_entrada.py` y `traza_punto.py`, y por las mismas
razones: `gui/` importa `tkinter`, que no esta en toda imagen donde corre la
suite, y lo que el panel AFIRMA tiene que poder compararse sin escritorio.
Aqui el contenido es un DATO; `gui/app.py` lo pinta y no sabe nada mas.

ES UNA ESTIMACION, Y ESA PALABRA NO ES OPCIONAL
-----------------------------------------------
El proyecto distingue estimaciones de medidas, y este panel esta del lado de
las estimaciones: la invocacion real de un criterio depende de la ruta que
tome cada punto, y la verdad post-corrida es el tablero de la pestana 4
(`M11.criterios_bloqueantes`, que se puebla DESPUES de ejecutar --- ese
diseño se conserva porque es la verdad medida). Por eso:

  * el aviso `AVISO_DEL_ANTICIPO` viaja con el panel y dice «estimacion»;
  * NADA de este modulo gobierna un filtro ni un boton: el boton de EJECUTAR
    no se entera de que el anticipo existe, porque correr siempre se puede
    --- el pipeline convierte cada falta en un `Bloqueo` declarado ---.

NINGUNA LISTA DE ESTE MODULO ESTA ESCRITA A MANO
------------------------------------------------
Todo sale de donde ya vive, que es la regla que S21/S22 dejaron asentada:

    criterios vacios alcanzables   ca.criterios_del_alcance (Criterio.nivel,
                                   contrastado por tests/test_nivel_medido.py)
                                   x ca.criterios_sin_valor (que ya excluye
                                   opcionales y declarados en caliente)
    columnas del CSV               M0_carga.COLUMNAS, M0_carga.VACIOS_ADMITIDOS
                                   y M0_carga.leer_cabecera --- SOLO cabecera y
                                   conteo de celdas vacias, sin ejecutar la
                                   carga completa ---
    lo que el alcance difiere      cli.VERIFICACIONES_DIFERIDAS_POR_ALCANCE y
                                   cli.MODULOS_DIFERIDOS_POR_ALCANCE, los dos
                                   consultados por la propia corrida

Este modulo no hace aritmetica sobre magnitudes --- cuenta filas y celdas,
que es lo unico que un contraste de cabecera necesita --- y no toma ninguna
decision de diseño: elige textos y orden, igual que M11.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple

from src import criterios_adoptados as ca
from src import servicio
from src.modelos import Familia, VacioAdmitido
# Por el modulo y no por el valor, por la razon escrita en `ayuda_entrada.py`:
# un `from ... import COLUMNAS` copia la tupla y la deja leyendo una foto.
from src.modulos import M0_carga as m0

# La linea fija del panel (regla dura de G3). La palabra «estimacion» no es
# opcional: el proyecto distingue estimaciones de medidas y esta es una
# estimacion. Vive aqui --- y la GUI la lee --- para que el texto que la
# ventana muestra y el que los tests comprueban sean EL MISMO.
AVISO_DEL_ANTICIPO = ("Estimación derivada del alcance; la lista definitiva "
                      "la da la corrida (pestaña 4).")

# Lo que el bloque de columnas dice mientras no hay CSV legible. `None` es
# «no se sabe», no «esta mal»: el anticipo se refresca al teclear la ruta y
# la mitad de las veces el archivo aun no existe (misma decision, escrita,
# que `gui/app.py::_releer_familias`).
SIN_CSV = ("Sin CSV legible todavía: el contraste de columnas se hace al "
           "cargar uno.")


# ===========================================================================
# Bloque 1 - criterios vacios que el alcance elegido puede invocar
# ===========================================================================

@dataclass(frozen=True)
class CriterioVacio:
    """Una fila del bloque 1: clave y concepto, para pintar y navegar."""

    clave: str
    concepto: str


def criterios_vacios_alcanzables(alcance: str) -> Tuple[CriterioVacio, ...]:
    """
    Los criterios SIN VALOR, no opcionales y sin declaracion en caliente que
    una corrida de ese alcance PUEDE invocar.

    Es la INTERSECCION de dos respuestas que ya existen, no una tercera:
    `ca.criterios_del_alcance` dice que criterios puede necesitar el alcance
    (lee `Criterio.nivel`), y `ca.criterios_sin_valor` dice cuales siguen
    vacios (y ya deja fuera los opcionales --- que no bloquean nada --- y los
    declarados en caliente). Una regla propia aqui seria una segunda
    clasificacion capaz de contradecir a las dos.

    Sigue siendo una ESTIMACION: que un criterio alcanzable este vacio no
    garantiza que esta corrida lo invoque --- eso depende de la ruta de cada
    punto --- y la lista definitiva la da `M11.criterios_bloqueantes` despues
    de correr.
    """
    alcanzables = set(ca.criterios_del_alcance(alcance))
    return tuple(
        CriterioVacio(clave=clave, concepto=ca.criterio(clave).concepto)
        for clave in ca.criterios_sin_valor() if clave in alcanzables)


# ===========================================================================
# Bloque 2 - contraste de la cabecera del CSV, sin ejecutar el pipeline
# ===========================================================================

@dataclass(frozen=True)
class ColumnaConVacios:
    """
    Una columna del CSV cargado que trae celdas vacias.

    `grupos` son los `VacioAdmitido` de M0 que la cubren: vacio significa que
    NINGUN grupo la admite y la carga completa se detendria en esa fila con
    `DatoFaltanteError`.
    """

    columna: str
    vacias: int
    grupos: Tuple[VacioAdmitido, ...]

    @property
    def admite_vacio(self) -> bool:
        return bool(self.grupos)

    @property
    def familias_del_vacio(self) -> Tuple[Familia, ...]:
        """
        Las familias en las que el vacio se admite; las tres cuando algun
        grupo no declara familias (el significado de `VacioAdmitido.familias`
        vacio, igual que en `ayuda_entrada.FichaDeColumna`).
        """
        familias = [familia
                    for vacio in self.grupos
                    for familia in (vacio.familias or tuple(Familia))]
        return tuple(f for f in Familia if f in familias)


@dataclass(frozen=True)
class ContrasteDelCSV:
    """El bloque 2 entero: cabecera contra Sec. 1.2 y celdas vacias."""

    filas: int
    faltan: Tuple[str, ...]
    sobran: Tuple[str, ...]
    con_vacios: Tuple[ColumnaConVacios, ...]

    @property
    def cabecera_completa(self) -> bool:
        return not self.faltan and not self.sobran


def contraste_de_cabecera(ruta: Any) -> ContrasteDelCSV:
    """
    La cabecera del CSV contra `M0_carga.COLUMNAS`, y sus celdas vacias
    contra `M0_carga.VACIOS_ADMITIDOS` --- SIN ejecutar el pipeline: la
    lectura es `M0_carga.leer_cabecera`, que no valida ni lanza por el
    contenido ---.

    Los grupos de cada columna se piden a `VACIOS_ADMITIDOS`, que es el dato
    publico que `_punto_desde_fila` consulta al cargar de verdad: una regla
    propia aqui podria admitir un vacio que la carga rechaza. La lectura por
    UNION de familias (sin fijar una) es la misma que usa la ayuda de la
    pestana 1, y es parte de por que esto es una estimacion: cual familia
    trae cada fila solo lo dice la carga completa.
    """
    cabecera = m0.leer_cabecera(ruta)
    faltan = tuple(c for c in m0.COLUMNAS if c not in cabecera.columnas)
    sobran = tuple(c for c in cabecera.columnas if c not in m0.COLUMNAS)
    con_vacios = tuple(
        ColumnaConVacios(
            columna=columna, vacias=vacias,
            grupos=tuple(vacio for vacio in m0.VACIOS_ADMITIDOS
                         if columna in vacio.columnas))
        for columna, vacias in cabecera.vacias_por_columna.items() if vacias)
    return ContrasteDelCSV(filas=cabecera.filas, faltan=faltan, sobran=sobran,
                           con_vacios=con_vacios)


def _celdas(cuantas: int) -> str:
    return f"{cuantas} celda" + ("" if cuantas == 1 else "s")


def _en_que_familias(columna: ColumnaConVacios) -> str:
    familias = columna.familias_del_vacio
    if len(familias) == len(tuple(Familia)):
        return "en las tres familias"
    return "solo en " + ", ".join(f"Familia {f.value}" for f in familias)


def lineas_del_contraste(contraste: ContrasteDelCSV) -> Tuple[str, ...]:
    """
    Las lineas del bloque 2, elegidas aqui para que gui/ solo pinte (el
    reparto de `traza_punto`). El orden es el del riesgo: primero lo que
    detendria la carga, despues lo que espera a un tablero.
    """
    lineas = []
    if contraste.faltan:
        lineas.append(
            "Faltan columnas de Sec. 1.2 (la carga del CSV se detendrá): "
            + ", ".join(contraste.faltan) + ".")
    if contraste.sobran:
        lineas.append("Columnas no reconocidas: "
                      + ", ".join(contraste.sobran)
                      + " — revisa si alguna está mal escrita.")
    if contraste.cabecera_completa:
        lineas.append(
            f"Cabecera completa: las {len(m0.COLUMNAS)} columnas de "
            f"Sec. 1.2, con {contraste.filas} fila"
            + ("" if contraste.filas == 1 else "s") + " de datos.")
    for columna in contraste.con_vacios:
        if not columna.admite_vacio:
            lineas.append(
                f"{columna.columna}: {_celdas(columna.vacias)} sin dato — la "
                "columna no admite vacío y la carga del CSV se detendrá ahí.")
            continue
        quien = "; ".join(vacio.quien_lo_debe for vacio in columna.grupos)
        lineas.append(
            f"{columna.columna}: {_celdas(columna.vacias)} sin dato — vacío "
            f"admitido {_en_que_familias(columna)} (lo debe: {quien}).")
    return tuple(lineas)


# ===========================================================================
# Bloque 3 - lo que el alcance elegido difiere
# ===========================================================================

@dataclass(frozen=True)
class DiferimientosDelAlcance:
    """Lo que una corrida de ese alcance difiere, leido de cli."""

    alcance: str
    verificaciones: Tuple[str, ...]
    modulos: Tuple[str, ...]

    @property
    def difiere_algo(self) -> bool:
        return bool(self.verificaciones or self.modulos)


def diferimientos_del_alcance(alcance: str) -> DiferimientosDelAlcance:
    """
    La lista REAL de lo que ese alcance difiere, leida del servicio de
    calculo y no escrita a mano: `VERIFICACIONES_DIFERIDAS_POR_ALCANCE` (las
    que se intentan y cuyo fallo se difiere, hoy V5 y V8 a perfil) y
    `MODULOS_DIFERIDOS_POR_ALCANCE` (los que la corrida no ejecuta). Los dos
    diccionarios los consulta la propia corrida, de modo que esta lista no
    puede divergir de lo que la corrida hace.

    Hasta EXT-9 los dos se leian de `cli`, importado DENTRO de la funcion
    para no arrastrar la capa de arriba al cargar este modulo; desde EXT-9
    viven en `src/servicio.py`, que es un modulo de esta misma capa y se
    importa arriba, como cualquier otro.
    """
    return DiferimientosDelAlcance(
        alcance=alcance,
        verificaciones=tuple(servicio.VERIFICACIONES_DIFERIDAS_POR_ALCANCE[alcance]),
        modulos=tuple(servicio.MODULOS_DIFERIDOS_POR_ALCANCE[alcance]))


def lineas_de_diferimientos(diferido: DiferimientosDelAlcance) -> Tuple[str, ...]:
    """Las lineas del bloque 3. Nada diferido tambien se dice, en positivo."""
    if not diferido.difiere_algo:
        return (f"El alcance «{diferido.alcance}» no difiere nada: corre el "
                "pipeline completo.",)
    lineas = []
    if diferido.verificaciones:
        lineas.append(
            "Verificaciones que se intentan y cuyo fallo se difiere al "
            "expediente: " + ", ".join(diferido.verificaciones) + ".")
    if diferido.modulos:
        lineas.append(
            "Módulos de cálculo que esta corrida no ejecuta: "
            + ", ".join(diferido.modulos) + ".")
    return tuple(lineas)
