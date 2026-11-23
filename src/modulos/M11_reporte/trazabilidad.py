# -*- coding: utf-8 -*-
"""
M11_reporte.trazabilidad
========================
Submodulo de Fase 11 (`M11_reporte`): bloque `trazabilidad` (D3).
"""

from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import (
    Any,
    Optional,
)
from src import criterios_adoptados as ca

from src.modulos.M11_reporte._base import (
    ARCHIVO_CRITERIOS,
    DIR_DOCS,
    PATRON_HOJA_RUTA,
    _esc,
)

# ===========================================================================
# 0. Encabezado de trazabilidad
# ===========================================================================

@dataclass(frozen=True)
class Trazabilidad:
    """
    Lo que identifica de forma inequivoca una corrida: con que reglas, sobre
    que datos y cuando. Es el encabezado del entregable, no un adorno -- dos
    memorias sin esto son indistinguibles.
    """

    version_hoja_ruta: str
    hoja_ruta: Path
    hoja_ruta_sha1: str
    csv: Path
    csv_sha1: str
    criterios_version: str
    criterios_fecha: str                         # ultima modificacion del archivo
    criterios_sha1: str
    generado_utc: str
    generado_local: str
    # UI-1 (ficha T1-04): las dos entradas de la hidrologia, ruta y huella.
    # La ruta es el origen que la corrida registro (`EntradaHidrologica`) y
    # la huella la del CONTEXTO (de los bytes que se parsearon). None sin
    # hidrologia, y entonces el encabezado no las nombra.
    cuencas: Optional[str] = None
    cuencas_sha1: Optional[str] = None
    estacion: Optional[str] = None
    estacion_sha1: Optional[str] = None


def sha1_de_bytes(datos: bytes) -> str:
    """
    SHA-1 de un contenido ya leido, en hexadecimal. Es lo que `servicio.correr`
    aplica a los MISMOS bytes que M0 parsea (PC-09): la huella del CSV que
    la memoria imprime es la de lo que se calculo, no la del archivo que hay
    en disco al exportar.
    """
    return hashlib.sha1(datos).hexdigest()


def sha1_archivo(ruta: Path) -> str:
    """
    SHA-1 del contenido del archivo, en hexadecimal.

    Es una huella de trazabilidad, no una medida de seguridad: sirve para
    responder "¿es este el mismo CSV con el que se corrio la memoria?".
    """
    return sha1_de_bytes(Path(ruta).read_bytes())


def ruta_hoja_de_ruta(dir_docs: Optional[Path] = None) -> Path:
    """
    Localiza la hoja de ruta vigente. Exige que haya exactamente una: con dos
    versiones en docs/ el reporte no puede decidir cual cito el calculo, y
    elegir la mas nueva seria inventar la respuesta.
    """
    carpeta = DIR_DOCS if dir_docs is None else dir_docs
    encontradas = sorted(carpeta.glob(PATRON_HOJA_RUTA))
    if not encontradas:
        raise FileNotFoundError(
            f"No se encontro la hoja de ruta ({PATRON_HOJA_RUTA}) en {carpeta}. "
            "Es la fuente normativa unica del proyecto: sin ella la memoria no "
            "puede declarar contra que version se calculo."
        )
    if len(encontradas) > 1:
        nombres = ", ".join(p.name for p in encontradas)
        raise ValueError(
            f"Hay mas de una hoja de ruta en {carpeta}: {nombres}. Deja una "
            "sola: el reporte no puede decidir cual de las dos sustenta los "
            "numerales citados."
        )
    return encontradas[0]


def version_hoja_de_ruta(ruta: Path) -> str:
    """
    Version declarada en el titulo de la hoja de ruta ('... · v8'; decia «v7» hasta T-0, INF-5.1.11).

    Se lee del documento, no del nombre del archivo ni de una constante: la
    version es una afirmacion de la fuente normativa. Si el titulo no la trae,
    se cae al nombre del archivo, y si tampoco, se detiene.
    """
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("# "):
            versiones = re.findall(r"\bv\d+\b", linea)
            if versiones:
                return versiones[-1]
            break
    del_nombre = re.findall(r"\bv\d+\b", ruta.stem)
    if del_nombre:
        return del_nombre[-1]
    raise ValueError(
        f"'{ruta.name}' no declara version en su titulo ni en su nombre. La "
        "memoria no puede citar numerales sin decir de que version salieron."
    )


def version_criterios(contexto: Any) -> str:
    """
    Huella legible de `criterios_adoptados.py`: cuantos criterios declara y
    cuantos siguen sin valor. Los dos conteos de estado --- sin valor y en
    caliente --- salen del `ContextoCorrida` de la corrida (EXT-4).

    No hay un numero de version escrito a mano a proposito. Un `__version__`
    que alguien olvida subir despues de tocar un criterio produce dos memorias
    distintas con la misma version, que es justo lo que este encabezado
    existe para impedir. El conteo y el SHA-1 del archivo no se pueden olvidar.
    """
    total = len(ca.CRITERIOS)
    sin_valor = len(contexto.criterios_sin_valor)
    en_caliente = len(contexto.declarados_en_caliente)
    # El conteo describe el estado de ESTA corrida, no solo el del archivo, y
    # por eso los declarados en caliente van dichos aparte: sin ellos el
    # encabezado presentaba como archivo lo que era archivo + declaraciones,
    # y el SHA-1 de al lado -- que si es solo del archivo -- no cuadraba.
    aparte = (f", mas {en_caliente} declarado(s) solo para esta corrida (NO "
              "en el archivo ni en su SHA-1)" if en_caliente else "")
    return (f"{total} criterios declarados, {sin_valor} todavia sin valor "
            f"(huella por SHA-1 del archivo){aparte}")


def fecha_archivo(ruta: Path) -> str:
    """
    Fecha de ultima modificacion del archivo, en hora local.

    Acompaña al SHA-1 en el encabezado porque responden preguntas distintas: el
    hash dice SI cambio, la fecha dice CUANDO. Un revisor que compara dos
    memorias necesita las dos.
    """
    return datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%d/%m/%Y %H:%M")


def trazabilidad(csv: Path, contexto: Any, *,
                 dir_docs: Optional[Path] = None,
                 generado_utc: str = "",
                 hidrologia: Any = None) -> Trazabilidad:
    """
    Arma el encabezado del entregable (bloque 0 de la Fase 11).

    `generado_utc` es la marca que ya trae el informe de la corrida; la fecha
    local se calcula aqui solo para la lectura humana. Las dos huellas de la
    corrida --- la del CSV y la del archivo de criterios --- vienen en el
    `ContextoCorrida` (EXT-4): la del CSV es de los bytes que M0 leyo, y
    editar el archivo entre correr y exportar ya no la mueve (PC-09). La de
    la hoja de ruta y la fecha del archivo de criterios se leen aqui, porque
    describen documentos y no estado.

    `hidrologia` (UI-1) es la `EntradaHidrologica` con que corrio el informe,
    o None: de ella sale la RUTA de cada entrada, y del contexto su huella.
    """
    hoja = ruta_hoja_de_ruta(dir_docs)
    return Trazabilidad(
        version_hoja_ruta=version_hoja_de_ruta(hoja),
        hoja_ruta=hoja,
        hoja_ruta_sha1=sha1_archivo(hoja),
        csv=csv,
        csv_sha1=contexto.csv_sha1,
        criterios_version=version_criterios(contexto),
        criterios_fecha=fecha_archivo(ARCHIVO_CRITERIOS),
        criterios_sha1=contexto.criterios_sha1,
        generado_utc=generado_utc,
        generado_local=datetime.now().strftime("%d/%m/%Y %H:%M"),
        cuencas=None if hidrologia is None else hidrologia.origen_cuencas,
        cuencas_sha1=contexto.cuencas_sha1,
        estacion=None if hidrologia is None else hidrologia.origen_estacion,
        estacion_sha1=contexto.estacion_sha1,
    )


# Los rotulos de las cuatro filas que el encabezado gana con hidrologia
# (UI-1). Con nombre, porque la suite los busca en las tres vistas.
ROTULO_CSV_CUENCAS = "CSV de cuencas (hidrologia)"
ROTULO_SHA1_CUENCAS = "SHA-1 del CSV de cuencas"
ROTULO_CSV_ESTACION = "CSV de la estacion (hidrologia)"
ROTULO_SHA1_ESTACION = "SHA-1 del CSV de la estacion"


def filas_hidrologia(traza: Trazabilidad) -> str:
    """
    Las filas del encabezado de trazabilidad para las dos entradas de la
    hidrologia (UI-1, ficha T1-04): ruta y SHA-1 de cada una, con la MISMA
    forma que las del CSV de puntos. La cadena vacia cuando la corrida no
    trajo hidrologia: ese es el contrato que deja la linea base intacta.
    """
    if traza.cuencas_sha1 is None and traza.estacion_sha1 is None:
        return ""
    filas = []
    for rotulo_ruta, ruta, rotulo_sha1, sha1 in (
            (ROTULO_CSV_CUENCAS, traza.cuencas, ROTULO_SHA1_CUENCAS,
             traza.cuencas_sha1),
            (ROTULO_CSV_ESTACION, traza.estacion, ROTULO_SHA1_ESTACION,
             traza.estacion_sha1)):
        filas.append(f'\n    <tr><th>{_esc(rotulo_ruta)}</th>\n'
                     f'        <td><span class="mono">{_esc(ruta)}</span></td></tr>')
        filas.append(f'\n    <tr><th>{_esc(rotulo_sha1)}</th>\n'
                     f'        <td class="mono">{_esc(sha1)}</td></tr>')
    return "".join(filas)
