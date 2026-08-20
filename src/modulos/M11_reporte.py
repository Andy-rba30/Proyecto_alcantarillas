"""
M11_reporte.py
==============
Fase 11 - Memoria de calculo. Convierte el `Informe` de una corrida en el
documento que se entrega, sin calcular nada nuevo.

Estructura del documento (Sec. "Fase 11 - Entregables")
-------------------------------------------------------
    0. Encabezado de trazabilidad   version de la hoja de ruta, fecha, SHA-1
                                    del CSV de entrada y version de
                                    criterios_adoptados. Sin esto dos memorias
                                    no se distinguen y ninguna es auditable
    1. Memoria por punto            entregable 1: datos CON SU FUENTE,
                                    iteraciones del diseño y cada verificacion
                                    como cumple / no cumple JUNTO A SU NUMERAL
    2. Tabla resumen                entregable 3, con sus doce columnas
    3. Criterios adoptados          entregable 2: los criterios que el calculo
                                    invoco, con etiqueta, justificacion y fuente
    4. Pendientes                   Tableros 1, 2 y 3 EN BLOQUE APARTE

Por que el bloque 4 va aparte
-----------------------------
El bloque 3 lista criterios CERRADOS: tienen valor, fuente y justificacion, y
sostienen los numeros de la memoria. El bloque 4 lista lo que NO esta resuelto.
Mezclarlos daria a entender que el expediente esta mas cerrado de lo que esta.
La hoja de ruta segrego los pendientes en tres tableros precisamente para no
leerlos como una lista homogenea, y la memoria respeta esa separacion.

De donde sale cada cosa
-----------------------
Los tableros NO se transcriben aqui: se leen de la hoja de ruta en cada
corrida. Una copia en Python seria una segunda fuente de verdad que envejece
en silencio en cuanto la hoja pase a v8, que es el error que este proyecto
persigue. Si la hoja cambia de forma y el bloque no se puede leer, M11 se
detiene con ValueError en vez de emitir una memoria con un bloque vacio.

La plantilla
------------
Vive en `src/plantillas/memoria_alcantarillas.html` y se procesa con
`string.Template` y delimitador "%%", el mismo patron de `legacy/Tc.py`. Se
sustituye con `substitute`, no con `safe_substitute`: un marcador sin valor
tiene que reventar en la generacion, no imprimirse en la memoria.

PDF
---
La misma via que ya usa Tc.py, sin dependencia nueva: `weasyprint` si esta
instalado y, si no, se escribe el HTML y se abre en el navegador para
"Imprimir -> Guardar como PDF" (la hoja ya esta configurada en A4).
`exportar_pdf` declara en su resultado cual de las dos vias se uso: nunca
devuelve un PDF que no escribio.

Excepciones
-----------
M11 no produce `ErrorProyecto`: no evalua el expediente, lo transcribe. Un
expediente incompleto es contenido normal de la memoria -- se imprime con sus
bloqueos y sus pendientes -- y no una excepcion. Lo que si falla es la falta de
las piezas del propio reporte (plantilla o hoja de ruta ausentes,
FileNotFoundError; hoja de ruta ilegible, ValueError), que son fallos de
instalacion del script y no del expediente.

Uso
---
    from modulos.M11_reporte import memoria_html, exportar_html, exportar_pdf

    html_texto = memoria_html(informe, proyecto="Via de evitamiento - La Union")
    exportar_html(informe, Path("Memoria.html"))
"""

from __future__ import annotations

import csv
import hashlib
import html
import math
import re
import tempfile
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Any, Dict, List, Optional, Sequence, Tuple

import criterios_adoptados as ca
import datos_sitio as ds
# Los avisos de verificaciones DIFERIDAS al expediente tecnico. M11 no
# recalcula nada: son declaraciones de alcance de cada modulo (texto, no
# numeros), y se importan de su fuente unica en vez de transcribirse aqui.
from modulos.M5_verificaciones import verificacion_diferida_hidraulica
from modulos.M8_estructural import verificacion_diferida_estructural
from modulos.M9_cabezal import verificacion_diferida_estabilidad_global

try:
    from weasyprint import HTML as WeasyHTML
except Exception:  # ImportError o fallo de librerias nativas (GTK/cairo)
    WeasyHTML = None


# ---------------------------------------------------------------------------
# Rutas del reporte. Ninguna es un valor de proyecto: son la ubicacion de los
# archivos del propio script.
# ---------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parents[2]      # src/modulos/M11 -> src -> raiz
SRC = RAIZ / "src"
DIR_PLANTILLAS = SRC / "plantillas"
NOMBRE_PLANTILLA = "memoria_alcantarillas.html"
ARCHIVO_CRITERIOS = SRC / "criterios_adoptados.py"

DIR_DOCS = RAIZ / "docs"
# Con comodin de version: cuando la hoja pase a v8 el reporte la encuentra sin
# tocar este archivo, y la version que imprime sale del propio documento.
PATRON_HOJA_RUTA = "hoja_de_ruta_alcantarillas_v*.md"

# Presentacion. Son formatos de texto, no magnitudes: cambiar un decimal no
# mueve ningun resultado del calculo.
FMT_2 = "{:.2f}"
FMT_3 = "{:.3f}"
VACIO = "&ndash;"
MARCA_CUMPLE = "cumple"
MARCA_INCUMPLE = "NO cumple"

# Orden de lectura de las etiquetas, de mas normativo a mas adoptado. Reproduce
# el de `criterios_adoptados.reporte_criterios`.
ORDEN_ETIQUETAS: Tuple[str, ...] = ("N", "N->", "S", "C", "A")
CLASE_ETIQUETA: Dict[str, str] = {"N": "et-N", "N->": "et-Na", "S": "et-S",
                                  "C": "et-C", "A": "et-A"}
ETIQUETA_HTML: Dict[str, str] = {"N": "N", "N->": "N&rarr;", "S": "S",
                                 "C": "C", "A": "A"}

# Fila del Tablero 2 que declara el detalle de embocadura del cabezal. La
# columna "Tipo de cabezal" del cuadro resumen (entregable 3) sale de ahi y no
# de una constante de este modulo: es una DECISION de proyecto, y su estado
# -- cerrada o abierta -- lo lleva la hoja de ruta.
ITEM_EMBOCADURA = "2.3"
# Columna del Tablero 2 que lleva la decision adoptada. Se busca por NOMBRE de
# encabezado y no por posicion: una columna nueva en la hoja de ruta no debe
# hacer que la memoria imprima la celda equivocada en silencio.
COLUMNA_ESTADO = "estado"

VIA_WEASYPRINT = "weasyprint"
VIA_NAVEGADOR = "navegador"

# Columnas del CSV de Sec. 1.2 tal como se listan en la memoria del punto:
# (campo de PuntoCritico, rotulo, unidad). El campo es la fuente: la memoria
# cita la columna de la que salio el dato, no solo el numero.
CAMPOS_CSV: Tuple[Tuple[str, str, str], ...] = (
    ("progresiva_km", "Progresiva", "km"),
    ("familia", "Familia (Sec. 2.3)", ""),
    ("Q_m3s", "Caudal de diseño", "m3/s"),
    ("area_ha", "Area tributaria", "ha"),
    ("S_cauce", "Pendiente del cauce", "m/m"),
    ("cota_terreno", "Cota de terreno", "msnm"),
    ("cota_rasante", "Cota de rasante", "msnm"),
    ("cota_subrasante", "Cota de subrasante", "msnm"),
    ("cbr_subrasante", "CBR de subrasante", "%"),
    ("esviaje_grados", "Esviaje", "grados"),
    ("ancho_plataforma", "Ancho de plataforma", "m"),
    ("cota_fondo_receptor", "Cota de fondo del receptor", "msnm"),
    ("Q_receptor_m3s", "Caudal del receptor", "m3/s"),
    ("cota_TW", "Cota de TW", "msnm"),
    ("sucs_fundacion", "SUCS de la fundacion", ""),
)

# Datos que no son columna del CSV y llegan declarados (ver `DatoDeclarado` de
# cli.py): el rotulo y el atributo del informe donde vive cada uno.
DATOS_DECLARADOS: Tuple[Tuple[str, str, str], ...] = (
    ("luz", "Luz del cruce", "m"),
    ("categoria_tr", "Fila de la Tabla N 02", ""),
    ("longitud", "Longitud del conducto", "m"),
    ("tw", "TW en el receptor", "m"),
)


class PlantillaHTML(Template):
    """string.Template con delimitador '%%', igual que en legacy/Tc.py."""
    delimiter = "%%"


# Contrato entre este modulo y la plantilla: los marcadores que M11 entrega.
# Se declara aparte para que el test pueda contrastarlo contra el archivo en
# las dos direcciones -- un marcador que la plantilla pide y M11 no entrega
# revienta la generacion, y uno que M11 calcula y la plantilla no imprime es
# contenido de la memoria que se pierde en silencio.
MARCADORES: Tuple[str, ...] = (
    "proyecto", "subtitulo",
    "version_hoja_ruta", "hoja_ruta_archivo", "hoja_ruta_sha1",
    "csv_ruta", "csv_sha1",
    "criterios_version", "criterios_fecha", "criterios_sha1",
    "generado_local", "generado_utc",
    "estado_expediente", "resumen_expediente",
    "memorias_punto", "filas_resumen",
    "bloque_datos_sitio", "bloque_criterios", "bloque_pendientes",
)


def marcadores_de_la_memoria() -> Tuple[str, ...]:
    """Los marcadores que `memoria_html` sustituye en la plantilla."""
    return MARCADORES


# ===========================================================================
# Utilidades de formato
# ===========================================================================

def _esc(texto: Any) -> str:
    """Todo texto que venga de un dato se escapa antes de entrar al HTML."""
    return html.escape(str(texto))


def _num(valor: Any, fmt: str = FMT_3) -> str:
    """Un numero con decimales fijos; None es celda vacia declarada."""
    if valor is None:
        return VACIO
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return _esc(valor)
    if isinstance(valor, float) and not math.isfinite(valor):
        return _esc(repr(valor))
    return fmt.format(float(valor))


def _valor_legible(valor: Any) -> str:
    """
    Un valor de criterio como se lee en la memoria. Los rangos y los dicts se
    imprimen enteros: un criterio como el n de Manning del HDPE ES un rango, y
    reducirlo a un numero en el reporte contradiria su propia justificacion.
    """
    if valor is None:
        return '<span class="pendiente">sin valor declarado</span>'
    if isinstance(valor, dict):
        return _esc(", ".join(f"{k} = {v}" for k, v in valor.items()))
    if isinstance(valor, (tuple, list)):
        return _esc(", ".join(str(v) for v in valor))
    return _esc(valor)


def _etiqueta_html(etiqueta: str) -> str:
    clase = CLASE_ETIQUETA.get(etiqueta, "")
    texto = ETIQUETA_HTML.get(etiqueta, _esc(etiqueta))
    return f'<span class="etiqueta {clase}">{texto}</span>'


def _marca(cumple: bool) -> str:
    clase = "cumple" if cumple else "incumple"
    texto = MARCA_CUMPLE if cumple else MARCA_INCUMPLE
    return f'<span class="{clase}">{texto}</span>'


def _orden_etiqueta(etiqueta: str) -> int:
    """Posicion de la etiqueta en el orden de lectura; las raras van al final."""
    if etiqueta in ORDEN_ETIQUETAS:
        return ORDEN_ETIQUETAS.index(etiqueta)
    return len(ORDEN_ETIQUETAS)


def _md_inline(celda: str) -> str:
    """El subconjunto de Markdown que usan los tableros, convertido a HTML."""
    salida = _esc(celda.strip())
    salida = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", salida)
    salida = re.sub(r"\*(.+?)\*", r"<i>\1</i>", salida)
    salida = re.sub(r"`(.+?)`", r"<code>\1</code>", salida)
    return salida


def _md_texto(celda: str) -> str:
    """La misma celda sin marcas, para cuando va dentro de otra frase."""
    return re.sub(r"[*`]", "", celda).strip()


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


def sha1_archivo(ruta: Path) -> str:
    """
    SHA-1 del contenido del archivo, en hexadecimal.

    Es una huella de trazabilidad, no una medida de seguridad: sirve para
    responder "¿es este el mismo CSV con el que se corrio la memoria?".
    """
    return hashlib.sha1(ruta.read_bytes()).hexdigest()


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
    Version declarada en el titulo de la hoja de ruta ('... · v7').

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


def version_criterios() -> str:
    """
    Huella legible de `criterios_adoptados.py`: cuantos criterios declara y
    cuantos siguen sin valor.

    No hay un numero de version escrito a mano a proposito. Un `__version__`
    que alguien olvida subir despues de tocar un criterio produce dos memorias
    distintas con la misma version, que es justo lo que este encabezado
    existe para impedir. El conteo y el SHA-1 del archivo no se pueden olvidar.
    """
    total = len(ca.CRITERIOS)
    sin_valor = len(ca.criterios_sin_valor())
    return (f"{total} criterios declarados, {sin_valor} todavia sin valor "
            f"(huella por SHA-1 del archivo)")


def fecha_archivo(ruta: Path) -> str:
    """
    Fecha de ultima modificacion del archivo, en hora local.

    Acompaña al SHA-1 en el encabezado porque responden preguntas distintas: el
    hash dice SI cambio, la fecha dice CUANDO. Un revisor que compara dos
    memorias necesita las dos.
    """
    return datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%d/%m/%Y %H:%M")


def trazabilidad(csv: Path, *, dir_docs: Optional[Path] = None,
                 generado_utc: str = "") -> Trazabilidad:
    """
    Arma el encabezado del entregable (bloque 0 de la Fase 11).

    `generado_utc` es la marca que ya trae el informe de la corrida; la fecha
    local se calcula aqui solo para la lectura humana.
    """
    hoja = ruta_hoja_de_ruta(dir_docs)
    return Trazabilidad(
        version_hoja_ruta=version_hoja_de_ruta(hoja),
        hoja_ruta=hoja,
        hoja_ruta_sha1=sha1_archivo(hoja),
        csv=csv,
        csv_sha1=sha1_archivo(csv),
        criterios_version=version_criterios(),
        criterios_fecha=fecha_archivo(ARCHIVO_CRITERIOS),
        criterios_sha1=sha1_archivo(ARCHIVO_CRITERIOS),
        generado_utc=generado_utc,
        generado_local=datetime.now().strftime("%d/%m/%Y %H:%M"),
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

    for linea in hoja.read_text(encoding="utf-8").splitlines():
        cabecera = _RE_TITULO_TABLERO.match(linea)
        if cabecera:
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
    return tuple(tableros)


def decision_embocadura(tableros: Sequence[Tablero]) -> Optional[str]:
    """
    Estado de la decision de embocadura del cabezal (item 2.3 del Tablero 2).

    Es la columna "Tipo de cabezal" del cuadro resumen. Sale del tablero y no
    de una constante: mientras la decision siga cerrada la memoria imprime el
    detalle adoptado, y si alguien la reabre el cuadro lo dice solo. Devuelve
    None si el item no esta: entonces la celda se imprime como pendiente, no
    se rellena.
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


def criterios_bloqueantes(informe: Any) -> Tuple[CriterioBloqueante, ...]:
    """
    Agrupa los bloqueos de la corrida por criterio pendiente: la lista que el
    revisor necesita para saber que declarar primero (Sec. 0.7).
    """
    acumulado: Dict[str, Dict[str, list]] = {}
    for id_punto, bloqueo in informe.bloqueos():
        if bloqueo.criterio is None:
            continue
        entrada = acumulado.setdefault(bloqueo.criterio,
                                       {"fases": [], "etapas": [], "puntos": []})
        for campo, dato in (("fases", bloqueo.fase), ("etapas", bloqueo.etapa),
                            ("puntos", id_punto)):
            if dato is not None and dato not in entrada[campo]:
                entrada[campo].append(dato)

    salida = []
    for clave in sorted(acumulado):
        declarado = ca.criterio(clave)
        salida.append(CriterioBloqueante(
            clave=clave, etiqueta=declarado.etiqueta,
            concepto=declarado.concepto, fuente=declarado.fuente,
            reemplazado_por=declarado.reemplazado_por,
            fases=tuple(acumulado[clave]["fases"]),
            etapas=tuple(acumulado[clave]["etapas"]),
            puntos=tuple(acumulado[clave]["puntos"])))
    return tuple(salida)


# ===========================================================================
# 1. Memoria por punto
# ===========================================================================

def _fila(celdas: Sequence[str], clase: str = "") -> str:
    atributo = f' class="{clase}"' if clase else ""
    return f"<tr{atributo}>" + "".join(celdas) + "</tr>"


def _td(contenido: str, clase: str = "") -> str:
    atributo = f' class="{clase}"' if clase else ""
    return f"<td{atributo}>{contenido}</td>"


def _tabla_datos(informe: Any) -> str:
    """
    Datos de partida del punto CON SU FUENTE (entregable 1).

    La fuente no es decorativa: un dato de la columna del CSV y un dato
    declarado en el JSON de la corrida se corrigen en sitios distintos, y el
    TW puede venir ademas de un criterio adoptado. La memoria tiene que decir
    cual es cual.
    """
    punto = informe.punto
    filas = [_fila([f"<th>{_esc(punto.id)}</th>", "<th>Valor</th>",
                    "<th>Unidad</th>", "<th>Fuente</th>"])]

    for campo, rotulo, unidad in CAMPOS_CSV:
        bruto = getattr(punto, campo)
        if hasattr(bruto, "value"):                       # enumeraciones
            texto = _esc(bruto.value)
        elif isinstance(bruto, str):
            texto = _esc(bruto)
        else:
            texto = _num(bruto)
        fuente = f"CSV Sec. 1.2, columna <code>{_esc(campo)}</code>"
        if bruto is None:
            fuente = (f'<span class="pendiente">columna '
                      f'<code>{_esc(campo)}</code> vacia</span> '
                      "&mdash; dato de un tablero externo")
        filas.append(_fila([_td(_esc(rotulo)), _td(texto, "num"),
                            _td(_esc(unidad)), _td(fuente)]))

    for atributo, rotulo, unidad in DATOS_DECLARADOS:
        dato = getattr(informe, atributo, None)
        if dato is None:
            # "sin resolver", no "no declarado": un dato puede haberse pasado
            # en la corrida y no llegar aqui porque la etapa que lo fija quedo
            # bloqueada antes. Decir "no declarado" acusaria al expediente de
            # una falta que puede no tener.
            filas.append(_fila([
                _td(_esc(rotulo)), _td(VACIO, "num"), _td(_esc(unidad)),
                _td('<span class="pendiente">sin resolver en esta corrida'
                    "</span> &mdash; el dato no se declaro o la etapa que lo "
                    "fija quedo bloqueada (ver las etapas bloqueadas)")]))
            continue
        valor = dato.valor
        texto = _esc(valor) if isinstance(valor, str) else _num(valor)
        filas.append(_fila([_td(_esc(rotulo)), _td(texto, "num"),
                            _td(_esc(unidad)), _td(_esc(dato.origen))]))

    return '<table class="compacta">' + "".join(filas) + "</table>"


def _tabla_clasificacion(informe: Any) -> str:
    """Fase 2: denominacion por luz y periodo de retorno, con sus numerales."""
    clasificacion = informe.clasificacion
    if clasificacion is None:
        return ""
    tr = clasificacion.periodo_retorno
    if tr.anios is None:
        texto_tr = (f'<span class="pendiente">no procede</span> &mdash; '
                    f"{_esc(tr.fundamento)}")
    else:
        categoria = "" if tr.categoria is None else f" ({_esc(tr.categoria.value)})"
        texto_tr = (f"<b>{tr.anios} años</b>{categoria}, num. "
                    f"{_esc(tr.numeral)}. {_esc(tr.fundamento)}")

    filas = [
        _fila([_td("<b>Denominacion</b>"),
               _td(f"{_esc(clasificacion.denominacion.value)} &mdash; luz "
                   f"{_num(clasificacion.luz_m, FMT_2)} m, num. "
                   f"{_esc(clasificacion.verificacion_luz.numeral)}")]),
        _fila([_td("<b>Familia</b>"),
               _td(f"{_esc(clasificacion.perfil.nombre)} &mdash; caudal de "
                   f"{_esc(clasificacion.perfil.origen_del_caudal)} "
                   f"(num. {_esc(clasificacion.perfil.numeral)})")]),
        _fila([_td("<b>Periodo de retorno</b>"), _td(texto_tr)]),
    ]
    return "<h4>Fase 2 &mdash; Clasificacion y periodo de retorno</h4>" \
           '<table class="compacta">' + "".join(filas) + "</table>"


def _tabla_iteraciones(informe: Any) -> str:
    """
    Iteraciones del diseño (entregable 1): los escalones que MD probo, en
    orden, con el motivo de cada descarte.

    Sin traza no se imprime una tabla vacia: se dice que no se registro. Una
    tabla vacia se lee como "no hubo iteraciones", que es falso.
    """
    traza = tuple(getattr(informe, "traza", ()) or ())
    if not traza:
        return ('<div class="nota"><p>No se registro traza de iteraciones para '
                "este punto: el bucle de diseño no llego a correr (ver los "
                "bloqueos) o la corrida no la solicito.</p></div>")

    filas = [_fila(["<th>#</th>", "<th>Material</th>", "<th>D (m)</th>",
                    "<th>Resultado</th>", "<th>Motivo del descarte</th>"])]
    for indice, paso in enumerate(traza, start=1):
        if paso.aceptado:
            resultado = '<span class="cumple">adoptado</span>'
            motivo = "pasa todas las verificaciones de la Fase 5"
        else:
            resultado = '<span class="incumple">descartado</span>'
            motivo = _esc(paso.motivo)
        clase = "fila-aceptada" if paso.aceptado else ""
        filas.append(_fila([_td(str(indice), "num"), _td(_esc(paso.material)),
                            _td(_num(paso.D, FMT_2), "num"), _td(resultado),
                            _td(motivo)], clase))
    return "<h4>Iteraciones del diseño (Fases 3-5)</h4>" \
           '<table class="compacta">' + "".join(filas) + "</table>"


def _tabla_diseno(informe: Any) -> str:
    """La combinacion adoptada: material, diametro e hidraulica gobernante."""
    if not informe.dimensionado:
        return ('<div class="bloqueo"><p>El punto <b>no llego a dimensionarse'
                "</b>. El motivo esta en la tabla de bloqueos.</p></div>")
    resultado = informe.resultado
    material, hidraulica = resultado.material, resultado.resultado_hidraulico
    filas = [
        _fila([_td("<b>Material</b>"),
               _td(f"{_esc(material.nombre)} &mdash; norma de producto "
                   f"{_esc(material.norma_producto)}, EG-2013 Seccion "
                   f"{_esc(material.seccion_eg2013)}")]),
        _fila([_td("<b>Rugosidad (regla de doble n)</b>"),
               _td(f"n para capacidad y tirante = {_num(material.n_max)}; "
                   f"n para velocidad y socavacion = {_num(material.n_min)}")]),
        _fila([_td("<b>Diametro adoptado</b>"),
               _td(f"D = {_num(resultado.D, FMT_2)} m (tope de la norma de "
                   f"producto: {_num(material.D_max, FMT_2)} m)")]),
        _fila([_td("<b>Hidraulica</b>"),
               _td(f"Q = {_num(hidraulica.Q)} m3/s &middot; y<sub>n</sub> = "
                   f"{_num(hidraulica.y_normal)} m &middot; y<sub>c</sub> = "
                   f"{_num(hidraulica.y_critico)} m &middot; V = "
                   f"{_num(hidraulica.V, FMT_2)} m/s")]),
        _fila([_td("<b>Control gobernante</b>"),
               _td(f"{_esc(hidraulica.control_gobernante.value)} &mdash; "
                   f"HW = {_num(hidraulica.HW)} m (entrada "
                   f"{_num(hidraulica.HW_entrada)} / salida "
                   f"{_num(hidraulica.HW_salida)})")]),
    ]
    return "<h4>Fases 3-5 &mdash; Combinacion adoptada</h4>" \
           '<table class="compacta">' + "".join(filas) + "</table>"


def _tabla_verificaciones(informe: Any) -> str:
    """
    Cada verificacion como cumple / no cumple JUNTO A SU NUMERAL (entregable 1).

    Cuando el umbral proviene de un criterio adoptado se imprime la clave y su
    etiqueta: un revisor tiene que poder distinguir de un vistazo lo que se
    contrasto contra la norma de lo que se contrasto contra una adopcion.
    """
    verificaciones = informe.verificaciones()
    if not verificaciones:
        return ('<div class="nota"><p>Sin verificaciones registradas: el punto '
                "no alcanzo la Fase 5.</p></div>")

    filas = [_fila(["<th>Codigo</th>", "<th>Numeral</th>", "<th>Obtenido</th>",
                    "<th>Admisible</th>", "<th>Umbral</th>",
                    "<th>Resultado</th>"])]
    for fase, v in verificaciones:
        if v.criterio_aplicado:
            declarado = ca.criterio(v.criterio_aplicado)
            umbral = (f"{_etiqueta_html(declarado.etiqueta)} "
                      f"<code>{_esc(v.criterio_aplicado)}</code>")
        else:
            umbral = f"{_etiqueta_html('N')} constante normativa"
        codigo = v.codigo or fase.split(" - ")[0]
        clase = "" if v.cumple else "fila-incumple"
        filas.append(_fila([_td(_esc(codigo)), _td(_esc(v.numeral)),
                            _td(_num(v.valor_obtenido), "num"),
                            _td(_num(v.valor_admisible), "num"),
                            _td(umbral), _td(_marca(v.cumple))], clase))
    return "<h4>Verificaciones</h4>" \
           '<table class="compacta">' + "".join(filas) + "</table>"


def _notas_diferidas(titulo: str, avisos: Sequence[str]) -> str:
    """
    Un bloque de verificaciones DIFERIDAS al expediente tecnico, con el mismo
    formato para las tres fuentes (Fase 5 V5/V8, Fase 8 item 5, Fase 9 E4/E5).
    Diferir no es cumplir: se imprime como nota con su fundamento, nunca como
    una fila de verificacion con marca.
    """
    elementos = "".join(f"<li>{_esc(a)}</li>" for a in avisos)
    return (f'<div class="nota"><p><b>{_esc(titulo)}</b></p>'
            f"<ul>{elementos}</ul></div>")


def _bloques_fases_finales(informe: Any) -> str:
    """Fases 6, 7, 8 y 10 del punto, cada una con su numeral."""
    partes: List[str] = []

    if informe.proteccion is not None:
        p = informe.proteccion
        avisos = "".join(f'<div class="aviso"><p>{_esc(a)}</p></div>'
                         for a in p.advertencias)
        partes.append(
            "<h4>Fase 6 &mdash; Proteccion de salida</h4>"
            f"<p>d<sub>50</sub> = {_num(p.d50)} m (num. {_esc(p.numeral)}), "
            f"espesor {_num(p.espesor)} m (criterio "
            f"<code>{_esc(p.criterio_espesor)}</code>), longitud "
            f"{_num(p.longitud)} m (criterio "
            f"<code>{_esc(p.criterio_longitud)}</code>), con V = "
            f"{_num(p.V, FMT_2)} m/s.</p>" + avisos)

    if informe.geometria is not None:
        g = informe.geometria
        t = g.tamizado
        estado = ('<span class="cumple">compatible</span>' if g.factible
                  else '<span class="incumple">no compatible</span>')
        delta = ("" if g.delta_rasante_cm is None else
                 f" Requiere subir la rasante {_num(g.delta_rasante_cm, FMT_2)} cm.")
        partes.append(
            "<h4>Fase 7 &mdash; Compatibilidad geometrica</h4>"
            f"<p>L = {_num(g.longitud, FMT_2)} m, esviaje afectando con factor "
            f"{_num(g.factor_esviaje)}; cota de entrada {_num(g.cota_entrada)} "
            f"msnm y de salida {_num(g.cota_salida)} msnm (caida "
            f"{_num(g.caida)} m), num. {_esc(g.numeral)}. Tamizado 7.A: "
            f"{estado}, gobierna la condicion "
            f"<b>{_esc(t.condicion_gobernante.value)}</b> "
            f"(criterio <code>{_esc(t.criterio_gobernante)}</code>).{delta}</p>"
            f'<div class="nota"><p>{_esc(t.mensaje)}</p></div>')

    if informe.cama_apoyo is not None:
        c = informe.cama_apoyo
        partes.append(
            "<h4>Fase 8 &mdash; Cama de apoyo y relleno lateral</h4>"
            f"<p>Cama de apoyo: {_esc(c.cama_apoyo)}. Sujecion y relleno "
            f"lateral: {_esc(c.sujecion_relleno_lateral)} "
            f"(num. {_esc(c.numeral)}).</p>"
            + _notas_diferidas(
                "Fase 8, item 5 — verificaciones diferidas al expediente "
                "tecnico", verificacion_diferida_estructural()))

    if informe.espaciamiento is not None:
        e = informe.espaciamiento
        partes.append(
            "<h4>Fase 10 &mdash; Espaciamiento de alcantarillas de alivio</h4>"
            f"<p>Espaciamiento maximo {_num(e.espaciamiento_max, FMT_2)} m: "
            f"gobierna el limite <b>{_esc(e.gobierna.value)}</b> "
            f"(normativo {_num(e.L_normativo, FMT_2)} m por el criterio "
            f"<code>{_esc(e.criterio_normativo)}</code>, hidraulico "
            f"{_num(e.L_hidraulico, FMT_2)} m), num. {_esc(e.numeral)}.</p>")

    return "".join(partes)


def _tabla_bloqueos(bloqueos: Sequence[Any]) -> str:
    """Etapas que no se pudieron completar, con la causa del expediente."""
    if not bloqueos:
        return ""
    partes = ["<h4>Etapas bloqueadas</h4>"]
    for b in bloqueos:
        detalle = _esc(b.mensaje)
        if b.criterio:
            detalle = (f"falta declarar {_etiqueta_html(b.etiqueta or '')} "
                       f"<code>{_esc(b.criterio)}</code> &mdash; "
                       f"{_esc(b.concepto)}<br>Fuente: {_esc(b.fuente)}")
        elif b.campo:
            detalle = f"campo <code>{_esc(b.campo)}</code>: {_esc(b.mensaje)}"
        partes.append(
            f'<div class="bloqueo"><p><b>{_esc(b.fase)}</b> &rarr; '
            f"{_esc(b.etapa)} <i>({_esc(b.tipo)})</i><br>{detalle}</p></div>")
    return "".join(partes)


def memoria_de_punto(informe: Any) -> str:
    """Bloque completo de un punto critico (entregable 1 de la Fase 11)."""
    punto = informe.punto
    clase = "punto" if informe.dimensionado else "punto sin-cerrar"
    estado = ("dimensionado" if informe.dimensionado
              else "sin dimensionar")
    partes = [
        f'<div class="{clase}">',
        f"<h3>{_esc(punto.id)} &nbsp;|&nbsp; progresiva "
        f"{_esc(punto.progresiva_display)} &nbsp;|&nbsp; Familia "
        f"{_esc(punto.familia.value)} &nbsp;|&nbsp; {estado}</h3>",
        "<h4>Datos de partida y su fuente</h4>",
        _tabla_datos(informe),
        _tabla_clasificacion(informe),
        _tabla_iteraciones(informe),
        _tabla_diseno(informe),
        _tabla_verificaciones(informe),
        # V5 y V8 no son filas de la tabla: van diferidas al expediente
        # tecnico (mismo mecanismo que Fase 8, item 5) y acompañan siempre a
        # las verificaciones de un punto que completo la Fase 5.
        (_notas_diferidas(
            "Fase 5 — V5 (remanso) y V8 (evento extremo) diferidas al "
            "expediente tecnico", verificacion_diferida_hidraulica())
         if informe.dimensionado else ""),
        _bloques_fases_finales(informe),
        _tabla_bloqueos(informe.bloqueos),
        "</div>",
    ]
    return "".join(partes)


# ===========================================================================
# 2. Tabla resumen (entregable 3)
# ===========================================================================

def fila_resumen(informe: Any, tipo_cabezal: str) -> str:
    """
    Una fila del cuadro resumen: progresiva, familia, TR, tipo, material y
    norma de producto, diametro, V, y/D, HW, control gobernante, proteccion de
    salida y tipo de cabezal (entregable 3).

    Toda celda que dependa de una etapa bloqueada sale vacia declarada, nunca
    con un valor plausible.
    """
    punto = informe.punto
    celdas = [_td(_esc(punto.progresiva_display)),
              _td(_esc(punto.familia.value))]

    if informe.clasificacion is None or informe.clasificacion.periodo_retorno.anios is None:
        celdas.append(_td(VACIO, "num"))
    else:
        celdas.append(_td(str(informe.clasificacion.periodo_retorno.anios), "num"))

    if informe.dimensionado:
        resultado = informe.resultado
        material = resultado.material
        h = resultado.resultado_hidraulico
        celdas.extend([
            _td(_esc(material.tipo.value)),
            _td(f"{_esc(material.nombre)}<br>{_esc(material.norma_producto)}"),
            _td(_num(resultado.D, FMT_2), "num"),
            _td(_num(h.V, FMT_2), "num"),
            _td(_num(h.y_normal / resultado.D, FMT_2), "num"),
            _td(_num(h.HW, FMT_2), "num"),
            _td(_esc(h.control_gobernante.value)),
        ])
    else:
        celdas.extend([_td(VACIO), _td(VACIO), _td(VACIO, "num"),
                       _td(VACIO, "num"), _td(VACIO, "num"),
                       _td(VACIO, "num"), _td(VACIO)])

    if informe.proteccion is None:
        celdas.append(_td(VACIO))
    else:
        p = informe.proteccion
        celdas.append(_td(f"d50 {_num(p.d50)} m<br>e {_num(p.espesor, FMT_2)} m "
                          f"&middot; L {_num(p.longitud, FMT_2)} m"))

    celdas.append(_td(tipo_cabezal))
    clase = "" if informe.dimensionado else "fila-incumple"
    return _fila(celdas, clase)


COLUMNAS_RESUMEN_CSV = (
    "id", "progresiva", "familia", "TR_anios", "tipo_hidraulico",
    "material", "norma_producto", "D_m", "V_ms", "y_sobre_D", "HW_m",
    "control_gobernante", "proteccion_d50_m", "proteccion_espesor_m",
    "proteccion_longitud_m", "tipo_cabezal",
)


def _fila_resumen_csv(informe: Any, tipo_cabezal: str) -> List[Any]:
    """
    Una fila del cuadro resumen (entregable 3) en valores planos, para CSV.
    Misma fuente de datos que `fila_resumen`: toda celda que dependa de una
    etapa bloqueada sale vacia, nunca con un valor plausible.
    """
    punto = informe.punto
    fila: List[Any] = [punto.id, punto.progresiva_display, punto.familia.value]

    if informe.clasificacion is None or informe.clasificacion.periodo_retorno.anios is None:
        fila.append("")
    else:
        fila.append(informe.clasificacion.periodo_retorno.anios)

    if informe.dimensionado:
        resultado = informe.resultado
        material = resultado.material
        h = resultado.resultado_hidraulico
        fila.extend([
            material.tipo.value, material.nombre, material.norma_producto,
            _num(resultado.D, FMT_2), _num(h.V, FMT_2),
            _num(h.y_normal / resultado.D, FMT_2), _num(h.HW, FMT_2),
            h.control_gobernante.value,
        ])
    else:
        fila.extend(["", "", "", "", "", "", "", ""])

    if informe.proteccion is None:
        fila.extend(["", "", ""])
    else:
        p = informe.proteccion
        fila.extend([_num(p.d50), _num(p.espesor, FMT_2), _num(p.longitud)])

    fila.append(tipo_cabezal)
    return fila


# ===========================================================================
# 3. Declaracion de criterios adoptados (entregable 2)
# ===========================================================================

def bloque_datos_sitio(solo_usados: bool = True) -> str:
    """
    Los datos de sitio [S] que el calculo invoco, cada uno con el
    procedimiento que lo produjo y la trazabilidad que permite repetirlo.

    Va delante de los criterios y no mezclado con ellos: un [S] no se defiende
    con un rango de sensibilidad -- no hay nada que elegir -- sino diciendo
    donde se leyo. Mezclarlos daria a entender que el PGA del mapa y la
    eleccion de F_pga son la misma clase de afirmacion, y son lo contrario:
    uno es un hecho del sitio y el otro una decision del proyectista.
    """
    claves = sorted(ds.datos_usados() if solo_usados else ds.DATOS_SITIO)
    if not claves:
        return ('<div class="aviso"><p>Esta corrida no invoco ningun dato de '
                "sitio.</p></div>")

    partes: List[str] = []
    for clave in claves:
        d = ds.dato(clave)
        campos = [
            f"<dt>Concepto</dt><dd>{_esc(d.concepto)}</dd>",
            f"<dt>Valor</dt><dd>{_valor_legible(d.valor)}</dd>",
            f"<dt>Procedimiento</dt><dd>{_esc(d.procedimiento)}</dd>",
            f"<dt>Fuente</dt><dd>{_esc(d.fuente)}</dd>",
            f"<dt>Trazabilidad</dt><dd>{_esc(d.trazabilidad)}</dd>",
            f"<dt>Ambito</dt><dd>{_esc(d.ambito)}</dd>",
        ]
        if d.reemplazado_por:
            campos.append("<dt>Lo sustituye</dt>"
                          f"<dd>{_esc(d.reemplazado_por)}</dd>")
        if d.verificacion_pendiente:
            campos.append('<dt class="pendiente">Verificar</dt>'
                          f'<dd class="pendiente">'
                          f"{_esc(d.verificacion_pendiente)}</dd>")
        partes.append(
            '<div class="criterio">'
            f'<p class="clave">{_etiqueta_html(d.etiqueta)} '
            f"<code>{_esc(clave)}</code></p><dl>" + "".join(campos)
            + "</dl></div>")

    con_pendiente = [k for k in claves if ds.dato(k).verificacion_pendiente]
    if con_pendiente:
        lista = ", ".join(f"<code>{_esc(k)}</code>" for k in con_pendiente)
        partes.append(
            '<div class="aviso"><p><b>Advertencia.</b> Los datos de sitio '
            f"{lista} tienen la trazabilidad incompleta: el valor esta leido, "
            "pero la memoria todavia no dice sobre que punto exacto se leyo y "
            "un revisor no puede reproducir la lectura.</p></div>")
    return "".join(partes)


def bloque_criterios(solo_usados: bool = True) -> str:
    """
    El contenido de `criterios_adoptados.reporte_criterios` como HTML: cada
    criterio invocado con su etiqueta, su justificacion y su fuente.

    Lee los mismos objetos `Criterio` que la version en texto, en el mismo
    orden de etiqueta, para que las dos digan exactamente lo mismo.
    """
    claves = sorted(ca.criterios_usados() if solo_usados else ca.CRITERIOS,
                    key=lambda k: (_orden_etiqueta(ca.criterio(k).etiqueta), k))
    if not claves:
        return ('<div class="aviso"><p>Esta corrida no invoco ningun criterio '
                "adoptado.</p></div>")

    partes: List[str] = []
    for clave in claves:
        c = ca.criterio(clave)
        campos = [
            f"<dt>Concepto</dt><dd>{_esc(c.concepto)}</dd>",
            f"<dt>Valor</dt><dd>{_valor_legible(c.valor)}"
            + ('<b class="pendiente"> [PROVISIONAL: valor de prueba, '
               "NO verificado]</b>" if c.provisional else "")
            + "</dd>",
            f"<dt>Justificacion</dt><dd>{_esc(c.justificacion)}</dd>",
            f"<dt>Fuente</dt><dd>{_esc(c.fuente)}</dd>",
        ]
        if c.reemplazado_por:
            campos.append("<dt>Lo sustituye</dt>"
                          f"<dd>{_esc(c.reemplazado_por)}</dd>")
        if c.sensibilidad:
            campos.append("<dt>Sensibilidad</dt>"
                          f"<dd>{_valor_legible(c.sensibilidad)}</dd>")
        if c.trazabilidad:
            campos.append("<dt>Trazabilidad</dt>"
                          f"<dd>{_esc(c.trazabilidad)}</dd>")
        if c.verificacion_pendiente:
            campos.append('<dt class="pendiente">Verificar</dt>'
                          f'<dd class="pendiente">'
                          f"{_esc(c.verificacion_pendiente)}</dd>")
        partes.append(
            '<div class="criterio">'
            f'<p class="clave">{_etiqueta_html(c.etiqueta)} '
            f"<code>{_esc(clave)}</code></p><dl>" + "".join(campos)
            + "</dl></div>")

    con_pendiente = [k for k in claves if ca.criterio(k).verificacion_pendiente]
    if con_pendiente:
        lista = ", ".join(f"<code>{_esc(k)}</code>" for k in con_pendiente)
        partes.append(
            '<div class="aviso"><p><b>Advertencia.</b> Los criterios '
            f"{lista} tienen una verificacion documental pendiente y no deben "
            "citarse como cerrados en la memoria hasta resolverla. El detalle "
            "de cada una esta en el bloque 4.</p></div>")
    return "".join(partes)


# ===========================================================================
# 4. Bloque aparte de pendientes (Tableros 1, 2 y 3)
# ===========================================================================

def _tabla_tablero(tablero: Tablero) -> str:
    """Un tablero de la hoja de ruta, tal cual lo publica."""
    encabezado = "".join(f"<th>{_md_inline(c)}</th>" for c in tablero.encabezados)
    filas = "".join(
        _fila([_td(_md_inline(celda)) for celda in fila])
        for fila in tablero.filas)
    return (f'<div class="tablero"><h3>Tablero {_esc(tablero.numero)} '
            f"&mdash; {_md_inline(tablero.titulo)}</h3>"
            f'<p class="glosa">{_md_inline(tablero.glosa)}</p>'
            f'<table class="ancha"><thead><tr>{encabezado}</tr></thead>'
            f"<tbody>{filas}</tbody></table></div>")


def bloque_pendientes(tableros: Sequence[Tablero],
                      bloqueantes: Sequence[CriterioBloqueante]) -> str:
    """
    Bloque 5 del entregable: los pendientes de los Tableros 1, 2 y 3, mas los
    criterios que esta corrida dejo sin valor.

    Va separado de la declaracion de criterios a proposito (ver el docstring
    del modulo). Se imprime siempre, incluso vacio de bloqueos: que una corrida
    no haya tropezado con un pendiente no significa que el pendiente no exista.

    Incluye ademas las verificaciones de la Fase 9 diferidas al expediente
    (E4/E5): la memoria no tiene un bloque de cabezal por punto -- Sec. 9 es
    del proyecto -- y este es el bloque donde el revisor busca lo no resuelto.
    Las diferidas de Fase 5 (V5/V8) y Fase 8 (item 5) se imprimen en la
    memoria de cada punto, junto a la fase que las difiere.
    """
    partes = ["".join(_tabla_tablero(t) for t in tableros)]

    partes.append("<h3>Verificaciones diferidas al expediente tecnico "
                  "(Fase 9)</h3>")
    partes.append(_notas_diferidas(
        "Fase 9 — E4 (estabilidad global) y E5 (talud) diferidas al "
        "expediente tecnico", verificacion_diferida_estabilidad_global()))

    partes.append("<h3>Criterios declarados todavia sin valor</h3>")
    sin_valor = ca.criterios_sin_valor()
    if not sin_valor:
        partes.append("<p>Ninguno: todos los criterios de "
                      "<code>criterios_adoptados.py</code> tienen valor.</p>")
    else:
        partes.append(
            "<p>Estos criterios estan declarados pero vacios. Cualquier etapa "
            "que los invoque se detiene: no se sustituyen por un valor por "
            "defecto (Sec. 0.7).</p>")
        filas = [_fila(["<th>Criterio</th>", "<th>Etiqueta</th>",
                        "<th>Concepto</th>", "<th>Que lo resuelve</th>"])]
        for clave in sin_valor:
            c = ca.criterio(clave)
            filas.append(_fila([
                _td(f"<code>{_esc(clave)}</code>"),
                _td(_etiqueta_html(c.etiqueta)),
                _td(_esc(c.concepto)),
                _td(_esc(c.reemplazado_por or c.fuente))]))
        partes.append('<table class="ancha">' + "".join(filas) + "</table>")

    partes.append("<h3>Criterios sin valor que bloquearon una etapa de esta "
                  "corrida</h3>")
    if not bloqueantes:
        partes.append("<p>Ninguno: ningun criterio sin valor se invoco en esta "
                      "corrida. No significa que no queden pendientes, sino "
                      "que los puntos calculados no dependian de ellos.</p>")
    else:
        for c in bloqueantes:
            puntos = ", ".join(c.puntos) if c.puntos else "proyecto (Fase 9)"
            partes.append(
                '<div class="bloqueo"><p>'
                f"{_etiqueta_html(c.etiqueta)} <code>{_esc(c.clave)}</code> "
                f"&mdash; {_esc(c.concepto)}<br>"
                f"<b>Fuente:</b> {_esc(c.fuente)}<br>"
                f"<b>Detuvo:</b> {_esc('; '.join(c.etapas))}<br>"
                f"<b>Puntos afectados:</b> {_esc(puntos)}"
                + (f"<br><b>Lo resuelve:</b> {_esc(c.reemplazado_por)}"
                   if c.reemplazado_por else "")
                + "</p></div>")
    return "".join(partes)


# ===========================================================================
# Ensamblado del documento
# ===========================================================================

def cargar_plantilla(ruta: Optional[Path] = None) -> PlantillaHTML:
    """Carga la plantilla %% de la memoria."""
    destino = (DIR_PLANTILLAS / NOMBRE_PLANTILLA) if ruta is None else ruta
    if not destino.is_file():
        raise FileNotFoundError(
            f"No se encontro la plantilla «{destino.name}».\n"
            f"Debe estar en: {destino.parent}"
        )
    return PlantillaHTML(destino.read_text(encoding="utf-8"))


def _resumen_expediente(informe: Any) -> str:
    """Las cuatro cifras que resumen la corrida, bajo el encabezado."""
    incumplidas = sum(len(i.incumplidas()) for i in informe.puntos)
    filas = [
        _fila([_td("<b>Puntos del expediente</b>"),
               _td(str(len(informe.puntos)), "num")]),
        _fila([_td("<b>Puntos dimensionados</b>"),
               _td(str(informe.dimensionados), "num")]),
        _fila([_td("<b>Verificaciones incumplidas</b>"),
               _td(str(incumplidas), "num")]),
        _fila([_td("<b>Etapas bloqueadas</b>"),
               _td(str(len(informe.bloqueos())), "num")]),
    ]
    return '<table class="compacta">' + "".join(filas) + "</table>"


def memoria_html(informe: Any, *, proyecto: str = "",
                 subtitulo: str = "", ruta_plantilla: Optional[Path] = None,
                 ruta_hoja: Optional[Path] = None) -> str:
    """
    El HTML completo de la memoria de calculo (Fase 11).

    `informe` es el `Informe` que produce la CLI. M11 no recalcula nada: si un
    dato no esta en el informe, la memoria lo declara ausente.
    """
    tableros = tableros_pendientes(ruta_hoja)
    bloqueantes = criterios_bloqueantes(informe)
    traza = trazabilidad(Path(informe.csv), generado_utc=informe.generado)

    embocadura = decision_embocadura(tableros)
    tipo_cabezal = (_esc(embocadura) if embocadura else
                    f'<span class="pendiente">sin declarar '
                    f"(Tablero {ITEM_EMBOCADURA})</span>")

    if informe.cerrado:
        estado = ('<span class="cumple">cerrado</span> &mdash; todos los puntos '
                  "dimensionados, sin etapas bloqueadas y sin verificaciones "
                  "incumplidas")
    else:
        estado = ('<span class="incumple">NO cierra</span> &mdash; hay etapas '
                  "bloqueadas, puntos sin dimensionar o verificaciones "
                  "incumplidas; el detalle esta en los bloques 1 y 4")

    valores = {
        "proyecto": _esc(proyecto) or "(proyecto no declarado)",
        "subtitulo": _esc(subtitulo),
        "version_hoja_ruta": _esc(traza.version_hoja_ruta),
        "hoja_ruta_archivo": _esc(traza.hoja_ruta.name),
        "hoja_ruta_sha1": _esc(traza.hoja_ruta_sha1),
        "csv_ruta": _esc(traza.csv),
        "csv_sha1": _esc(traza.csv_sha1),
        "criterios_version": _esc(traza.criterios_version),
        "criterios_fecha": _esc(traza.criterios_fecha),
        "criterios_sha1": _esc(traza.criterios_sha1),
        "generado_local": _esc(traza.generado_local),
        "generado_utc": _esc(traza.generado_utc),
        "estado_expediente": estado,
        "resumen_expediente": _resumen_expediente(informe),
        "memorias_punto": "".join(memoria_de_punto(p) for p in informe.puntos),
        "filas_resumen": "".join(fila_resumen(p, tipo_cabezal)
                                 for p in informe.puntos),
        "bloque_datos_sitio": bloque_datos_sitio(solo_usados=True),
        "bloque_criterios": bloque_criterios(solo_usados=True),
        "bloque_pendientes": bloque_pendientes(tableros, bloqueantes),
    }
    if set(valores) != set(MARCADORES):
        diferencia = set(valores).symmetric_difference(MARCADORES)
        raise ValueError(
            f"El contrato de marcadores no cuadra: {sorted(diferencia)}. "
            "`MARCADORES` y el diccionario de `memoria_html` tienen que decir "
            "lo mismo, porque el test de la plantilla se apoya en esa lista."
        )
    # `substitute`, no `safe_substitute`: un marcador que la plantilla pide y
    # este modulo no entrega tiene que reventar aqui, no imprimirse.
    return cargar_plantilla(ruta_plantilla).substitute(valores)


# ===========================================================================
# Exportacion
# ===========================================================================

@dataclass(frozen=True)
class ResultadoExportacion:
    """
    Que se escribio y por que via. `via` importa: con weasyprint sale un PDF y
    sin el sale un HTML que el usuario todavia tiene que imprimir. Devolver lo
    mismo en los dos casos haria creer que hay un PDF donde no lo hay.
    """

    ruta: Path
    via: str
    mensaje: str


def exportar_html(informe: Any, destino: Path, **kwargs: Any) -> Path:
    """Escribe la memoria como HTML. Los kwargs van a `memoria_html`."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(memoria_html(informe, **kwargs), encoding="utf-8")
    return destino


def exportar_csv(informe: Any, destino: Path, *, ruta_hoja: Optional[Path] = None) -> Path:
    """
    Escribe el cuadro resumen (entregable 3) como CSV, una fila por punto.
    Mismas columnas y misma fuente de datos que `fila_resumen` en la memoria
    HTML: es el mismo cuadro, en un formato que se abre en una hoja de calculo.
    """
    tableros = tableros_pendientes(ruta_hoja)
    embocadura = decision_embocadura(tableros)
    tipo_cabezal = embocadura or f"sin declarar (Tablero {ITEM_EMBOCADURA})"

    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(COLUMNAS_RESUMEN_CSV)
        for p in informe.puntos:
            escritor.writerow(_fila_resumen_csv(p, tipo_cabezal))
    return destino


def exportar_pdf(informe: Any, destino: Path, *, abrir_navegador: bool = True,
                 **kwargs: Any) -> ResultadoExportacion:
    """
    Exporta la memoria a PDF por la misma via que ya usa `legacy/Tc.py`:

        1. `weasyprint` si esta instalado -> PDF directo en `destino`.
        2. Si no lo esta, se escribe el HTML (junto a `destino`, con extension
           .html) y se abre en el navegador para "Imprimir -> Guardar como
           PDF". La plantilla ya viene configurada en A4.

    No se agrega ninguna dependencia nueva: weasyprint es opcional en Tc.py y
    aqui tambien. El resultado declara cual de las dos vias se uso.
    """
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    contenido = memoria_html(informe, **kwargs)

    if WeasyHTML is not None:
        WeasyHTML(string=contenido, base_url=str(DIR_PLANTILLAS)).write_pdf(str(destino))
        return ResultadoExportacion(
            ruta=destino, via=VIA_WEASYPRINT,
            mensaje=f"Memoria exportada a PDF con weasyprint: {destino}")

    respaldo = destino.with_suffix(".html")
    respaldo.write_text(contenido, encoding="utf-8")
    if abrir_navegador:
        temporal = Path(tempfile.gettempdir()) / respaldo.name
        temporal.write_text(contenido, encoding="utf-8")
        webbrowser.open(temporal.as_uri())
    return ResultadoExportacion(
        ruta=respaldo, via=VIA_NAVEGADOR,
        mensaje=("weasyprint no esta instalado. Se escribio el HTML en "
                 f"{respaldo} y se abrio en el navegador: guardalo como PDF "
                 "con Ctrl+P (la hoja ya esta en A4). Para exportar directo: "
                 "pip install weasyprint"))
