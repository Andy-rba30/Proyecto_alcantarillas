# -*- coding: utf-8 -*-
"""
M11_reporte.tableros
====================
Submodulo de Fase 11 (`M11_reporte`): bloque `tableros` (D3).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
)
from src import (
    criterios_adoptados as ca,
    responsable as _responsable,
)
from src.modelos import TipoDeBloqueo

from src.modulos.M11_reporte._base import (
    COLUMNA_ESTADO,
    ITEM_EMBOCADURA,
    _md_texto,
)
from src.modulos.M11_reporte.trazabilidad import (
    ruta_hoja_de_ruta,
)

# ===========================================================================
# Tableros de pendientes, leidos de la hoja de ruta
# ===========================================================================

@dataclass(frozen=True)
class Tablero:
    """Un tablero de pendientes tal como lo publica la hoja de ruta."""

    numero: str                                  # "1", "2", "3"
    titulo: str
    glosa: str                                   # la linea en cursiva
    encabezados: Tuple[str, ...]
    filas: Tuple[Tuple[str, ...], ...]


_RE_TITULO_TABLERO = re.compile(r"^###\s+Tablero\s+(\S+)\s*[—–-]+\s*(.+?)\s*$")
_RE_GLOSA = re.compile(r"^\*(.+)\*$")
_RE_SEPARADOR = re.compile(r"^\|[\s:|-]+\|$")


def _celdas(linea: str) -> Tuple[str, ...]:
    """Parte una fila de tabla Markdown en sus celdas."""
    return tuple(c.strip() for c in linea.strip().strip("|").split("|"))


def tableros_pendientes(ruta: Optional[Path] = None) -> Tuple[Tablero, ...]:
    """
    Lee los Tableros 1, 2 y 3 de la hoja de ruta.

    No se transcriben en este modulo a proposito: una copia en Python seria una
    segunda fuente de verdad que envejece en silencio en cuanto la hoja pase a
    v8. Si la hoja cambia de forma y los tableros no se pueden leer, esto se
    detiene con ValueError: una memoria con el bloque de pendientes vacio diria
    que no queda nada pendiente, que es la mentira mas cara del expediente.

    EL FALLO RUIDOSO CUBRE TAMBIEN LA DEGRADACION PARCIAL (SIS-C-13). La
    version anterior solo se detenia cuando NINGUN tablero se podia leer. Un
    cambio de formato que rompiera la tabla de UNO de los tres --- el caso
    realista, porque el formato se toca tablero a tablero --- dejaba pasar los
    otros dos en silencio: la memoria imprimia 10 filas donde hay 15 y
    declaraba cerrado lo que no lo esta. Se comprueba, por lo tanto, que cada
    encabezado `Tablero N` encontrado en la hoja produjo su tablero. Un
    `Tablero N` que no produce tabla es inequivocamente un formato roto,
    porque el tablero solo nace cuando aparece su fila de encabezados.

    Lo que NO se comprueba, deliberadamente, es que cada tablero traiga
    filas: una tabla bien formada con cero filas de datos es lo que se ve
    cuando ese tablero ya no tiene pendientes, que es hacia donde el proyecto
    trabaja. Ver el razonamiento en el punto de uso, mas abajo.
    """
    hoja = ruta_hoja_de_ruta() if ruta is None else ruta
    tableros: List[Tablero] = []

    numero = titulo = glosa = ""
    encabezados: Tuple[str, ...] = ()
    filas: List[Tuple[str, ...]] = []
    dentro = False

    def cerrar() -> None:
        if dentro and encabezados:
            tableros.append(Tablero(numero=numero, titulo=titulo, glosa=glosa,
                                    encabezados=encabezados,
                                    filas=tuple(filas)))

    encabezados_hallados: List[str] = []
    for linea in hoja.read_text(encoding="utf-8").splitlines():
        cabecera = _RE_TITULO_TABLERO.match(linea)
        if cabecera:
            encabezados_hallados.append(cabecera.group(1))
            cerrar()
            numero, titulo = cabecera.group(1), cabecera.group(2)
            glosa, encabezados, filas, dentro = "", (), [], True
            continue

        if not dentro:
            continue

        if linea.startswith("#") or linea.startswith("---"):
            cerrar()
            dentro = False
            continue

        cursiva = _RE_GLOSA.match(linea.strip())
        if cursiva and not glosa:
            glosa = cursiva.group(1)
            continue

        if linea.startswith("|"):
            if _RE_SEPARADOR.match(linea.strip()):
                continue
            if not encabezados:
                encabezados = _celdas(linea)
            else:
                filas.append(_celdas(linea))
    cerrar()

    if not tableros:
        raise ValueError(
            f"No se pudo leer ningun 'Tablero N' en {hoja.name}. El bloque de "
            "pendientes de la memoria sale de ahi y no se inventa: revisa si "
            "la hoja de ruta cambio el formato de esos encabezados."
        )

    leidos = [t.numero for t in tableros]
    perdidos = [n for n in encabezados_hallados if n not in leidos]
    if perdidos:
        raise ValueError(
            f"En {hoja.name} hay encabezados de tablero que no produjeron "
            f"ninguna tabla: {perdidos}. Se leyeron {leidos}. El bloque de "
            "pendientes saldria incompleto y la memoria diria que queda menos "
            "pendiente de lo que queda: revisa el formato de esas tablas."
        )
    # UN TABLERO CON CERO FILAS NO SE RECHAZA, y conviene decir por que se
    # penso lo contrario. La primera version de este cierre añadia aqui un
    # tercer `raise` --- "un tablero vacio no es un tablero sin pendientes, es
    # un tablero que no se pudo leer" --- y esa frase es un supuesto sobre el
    # FUTURO del expediente, no una propiedad del formato: el proyecto trabaja
    # precisamente para vaciar los tableros, y el dia que uno cierre su ultima
    # fila legitimamente la memoria entera habria dejado de generarse con un
    # ValueError, sin forma de distinguirlo de un cambio de formato.
    #
    # La degradacion parcial que SIS-C-13 pide detectar la coge `perdidos`, y
    # la coge sin ambiguedad: `cerrar()` solo produce un `Tablero` cuando
    # encontro la FILA DE ENCABEZADOS, de modo que una tabla rota o retirada
    # deja su `Tablero N` sin producir nada y cae ahi. Una tabla bien formada
    # con cero filas de datos, en cambio, es exactamente lo que se ve cuando
    # ya no queda nada pendiente en ese tablero.
    return tuple(tableros)


def decision_embocadura(tableros: Sequence[Tablero]) -> Optional[str]:
    """
    Estado de la decision de embocadura del cabezal (item 2.3 del Tablero 2).

    Hasta T-11 era la columna "Tipo de cabezal" del cuadro resumen, la misma
    en todos los puntos. Desde T-11 (H8 de su auditoria) esa columna sale
    del PUNTO (`tipo_cabezal_del_punto`: la embocadura que T-7a resuelve por
    punto y el tipo de sus cabezales), porque la decision 2.3 es el borde de
    entrada del TUBO y no describe el marco de la Familia C (Carta 8). Esta
    lectura del tablero se conserva: dice que dice la v8. Devuelve None si el
    item no esta.
    """
    for tablero in tableros:
        encabezados = [_md_texto(c).lower() for c in tablero.encabezados]
        for fila in tablero.filas:
            if not fila or _md_texto(fila[0]) != ITEM_EMBOCADURA:
                continue
            if COLUMNA_ESTADO in encabezados:
                columna = encabezados.index(COLUMNA_ESTADO)
                if columna < len(fila):
                    return _md_texto(fila[columna])
            # Sin columna 'Estado' se devuelve la fila entera antes que una
            # celda elegida a dedo: de mas informacion no sale una lectura
            # equivocada, de la celda equivocada si.
            return " - ".join(_md_texto(c) for c in fila[1:] if c.strip())
    return None


# ===========================================================================
# Criterios pendientes que bloquearon una etapa
# ===========================================================================

@dataclass(frozen=True)
class CriterioBloqueante:
    """
    Un criterio sin valor, con todo lo que freno en esta corrida.

    Vive aqui y no en modelos.py por lo mismo que las estructuras del informe
    de cli.py: no fluye entre modulos de calculo, es una agregacion del
    reporte. La produce M11 y la consume tanto la memoria HTML como el volcado
    de texto de la CLI.
    """

    clave: str
    etiqueta: str
    concepto: str
    fuente: str
    reemplazado_por: Optional[str]
    fases: Tuple[str, ...]
    etapas: Tuple[str, ...]
    puntos: Tuple[str, ...]
    # True cuando TODO lo que este criterio detuvo estaba diferido por
    # alcance (EXT-G-02): el criterio sigue pendiente, pero no bloquea el
    # cierre de ESTA corrida. Antes el agregador mezclaba los dos casos y el
    # tablero de la GUI, el bloque de la memoria y el JSON los imprimian
    # iguales, de modo que «bloqueo esta corrida» era falso de la mitad de
    # las filas de una corrida de perfil.
    diferido: bool = False
    # QUIEN lo fija y CON QUE evidencia (E-B, E13 reducido), derivados de la
    # ficha por `src/responsable.py`: `resolucion` y `reemplazado_por`. La
    # pestaña 4, el JSON y el anticipo (antes de correr) leen la misma
    # derivacion.
    responsable: str = ""
    evidencia: str = ""
    # Donde se declara el criterio o dato de sitio pendiente en la interfaz o
    # en la linea de comandos (C4), derivado de `src/responsable.py`.
    donde_se_declara: str = ""


def criterios_bloqueantes(informe: Any) -> Tuple[CriterioBloqueante, ...]:
    """
    Agrupa los bloqueos de la corrida por criterio pendiente: la lista que el
    revisor necesita para saber que declarar primero (Sec. 0.7).
    """
    acumulado: Dict[str, Dict[str, list]] = {}
    reales: set = set()
    for id_punto, bloqueo in informe.bloqueos():
        if bloqueo.criterio is None:
            continue
        if not bloqueo.diferido_por_alcance:
            reales.add(bloqueo.criterio)
        entrada = acumulado.setdefault(bloqueo.criterio,
                                       {"fases": [], "etapas": [], "puntos": []})
        for campo, dato in (("fases", bloqueo.fase), ("etapas", bloqueo.etapa),
                            ("puntos", id_punto)):
            if dato is not None and dato not in entrada[campo]:
                entrada[campo].append(dato)

    salida = []
    for clave in sorted(acumulado):
        # Ver `ca.declaracion_de`: un [S] de corredor pendiente levanta la
        # misma CriterioPendienteError y no esta en CRITERIOS (SIS-A-05).
        declarado = ca.declaracion_de(clave)
        quien = _responsable.responsabilidad_de(declarado)
        donde = _responsable.donde_se_declara_criterio(clave)
        salida.append(CriterioBloqueante(
            clave=clave, etiqueta=declarado.etiqueta,
            concepto=declarado.concepto, fuente=declarado.fuente,
            reemplazado_por=declarado.reemplazado_por,
            fases=tuple(acumulado[clave]["fases"]),
            etapas=tuple(acumulado[clave]["etapas"]),
            puntos=tuple(acumulado[clave]["puntos"]),
            diferido=clave not in reales,
            responsable=quien.responsable, evidencia=quien.evidencia,
            donde_se_declara=donde))
    return tuple(salida)


# ===========================================================================
# Datos faltantes o invalidos que bloquearon una etapa (C4)
# ===========================================================================

@dataclass(frozen=True)
class DatoBloqueante:
    """
    Un dato de entrada faltante o invalido que detuvo una etapa en esta
    corrida, agregado para la pestaña 4 (C4).
    """

    dato: str
    tipo: str
    fases: Tuple[str, ...]
    etapas: Tuple[str, ...]
    puntos: Tuple[str, ...]
    donde_se_declara: str
    detalle: str
    diferido: bool = False


def datos_bloqueantes(informe: Any) -> Tuple[DatoBloqueante, ...]:
    """
    Agrupa los bloqueos de `informe.bloqueos()` debidos a datos faltantes o
    invalidos (`criterio is None` con `DATO_FALTANTE`, `DATO_INVALIDO` o
    `campo` informado), indicando donde se declara cada dato (C4).
    """
    acumulado: Dict[Tuple[str, str], Dict[str, Any]] = {}
    reales: set = set()
    for id_punto, bloqueo in informe.bloqueos():
        if bloqueo.criterio is not None:
            continue
        es_dato = (
            bloqueo.tipo in (TipoDeBloqueo.DATO_FALTANTE,
                             TipoDeBloqueo.DATO_INVALIDO)
            or bool(bloqueo.campo)
        )
        if not es_dato:
            continue
        clave_dato = str(bloqueo.campo or bloqueo.etapa or bloqueo.tipo.value)
        tipo_texto = str(bloqueo.tipo.value)
        llave = (clave_dato, tipo_texto)
        if not bloqueo.diferido_por_alcance:
            reales.add(llave)
        entrada = acumulado.setdefault(
            llave, {"fases": [], "etapas": [], "puntos": [], "detalle": ""}
        )
        for campo_lista, val in (("fases", bloqueo.fase),
                                 ("etapas", bloqueo.etapa),
                                 ("puntos", id_punto)):
            if val is not None and val not in entrada[campo_lista]:
                entrada[campo_lista].append(val)
        if not entrada["detalle"] and bloqueo.mensaje:
            entrada["detalle"] = bloqueo.mensaje

    salida = []
    for (clave_dato, tipo_texto) in sorted(acumulado):
        info = acumulado[(clave_dato, tipo_texto)]
        salida.append(DatoBloqueante(
            dato=clave_dato,
            tipo=tipo_texto,
            fases=tuple(info["fases"]),
            etapas=tuple(info["etapas"]),
            puntos=tuple(info["puntos"]),
            donde_se_declara=_responsable.donde_se_declara_dato(clave_dato),
            detalle=info["detalle"],
            diferido=(clave_dato, tipo_texto) not in reales,
        ))
    return tuple(salida)
