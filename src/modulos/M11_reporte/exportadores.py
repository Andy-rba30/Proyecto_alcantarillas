# -*- coding: utf-8 -*-
"""
M11_reporte.exportadores
========================
Submodulo de Fase 11 (`M11_reporte`): bloque `exportadores` (D3).
"""

from __future__ import annotations

import csv
import os
import tempfile
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Callable,
    Optional,
)

from src.modulos.M11_reporte._base import (
    DIR_PLANTILLAS,
    ETAPA_NAVEGADOR,
    ETAPA_PDF,
    VIA_NAVEGADOR,
    VIA_WEASYPRINT,
)
from src.modulos.M11_reporte.proyecto import (
    COLUMNAS_RESUMEN_CSV,
    _fila_resumen_csv,
)
from src.modulos.M11_reporte.memoria import (
    memoria_html,
    memoria_html_por_partes,
)
from src.modulos.M11_reporte.resumida import (
    memoria_resumida_html,
)

# EL FALLO DEL IMPORT SE GUARDA, NO SE TIRA. Hasta aqui este `except` se
# comia la excepcion y el mensaje de mas abajo afirmaba «weasyprint no esta
# instalado» en los DOS casos. En Windows eso es falso y ademas insultante: el
# paquete SI esta --- viene en `requirements.txt` --- y lo que no carga son sus
# librerias nativas (GTK: GObject, Pango, Cairo, GDK-PixBuf), que `pip` no
# instala. El mensaje mandaba a hacer `pip install weasyprint` a quien ya lo
# tenia hecho, que es exactamente el defecto que este proyecto persigue --- un
# bloqueo mal nombrado --- escrito en una cadena.
#
# Los dos casos se distinguen por la CLASE de la excepcion: `ImportError` es
# «no esta»; cualquier otra (tipicamente `OSError` desde `ctypes`/`cffi` al
# resolver una DLL) es «esta y no carga». Y el texto de la excepcion NOMBRA la
# biblioteca que falta, que es el unico dato con el que se puede arreglar:
# adivinarlo desde aqui seria suponer, y la regla del proyecto es declarar.
#
# Y SE CARGA PEREZOSAMENTE (EXT-8, PC-10). Hasta EXT-8 el `try` de arriba
# corria al importar este modulo, o sea en CADA `import cli` --- 383 ms
# medidos, tambien en una corrida sin `--pdf`, en la ayuda y al abrir la
# GUI ---. Ahora corre UNA vez por proceso, la primera vez que alguien
# pregunta (`weasyprint_disponible()`) o exporta (`exportar_pdf`). El
# contrato no cambia: `WeasyHTML` sigue siendo EL simbolo que decide la via
# --- la GUI lo sondea y `tests/test_M11_reporte.py` lo parchea --- y
# `FALLO_WEASYPRINT` / `WEASYPRINT_AUSENTE` conservan el diagnostico de
# arriba. Un test parchea `WeasyHTML` DESPUES de sondear (o marca
# `_WEASYPRINT_SONDEADO`), porque la sonda solo escribe la primera vez.
WeasyHTML: Any = None
FALLO_WEASYPRINT: Optional[str] = None
WEASYPRINT_AUSENTE = False
_WEASYPRINT_SONDEADO = False


def _importar_weasyprint() -> Any:
    """El import de verdad, separado para que la sonda se pueda probar."""
    from weasyprint import HTML
    return HTML


def weasyprint_disponible() -> bool:
    """
    La SONDA: si weasyprint esta operativo en este proceso.

    Carga una sola vez y deja escrito el diagnostico: `WEASYPRINT_AUSENTE`
    (no esta: ImportError) frente a `FALLO_WEASYPRINT` (esta y no carga:
    cualquier otra excepcion, tipicamente OSError desde ctypes/cffi por una
    DLL de GTK). Es lo que `_por_que_no_hay_weasyprint` lee para decirle al
    usuario que hacer.
    """
    global WeasyHTML, FALLO_WEASYPRINT, WEASYPRINT_AUSENTE, _WEASYPRINT_SONDEADO
    if not _WEASYPRINT_SONDEADO:
        _WEASYPRINT_SONDEADO = True
        try:
            WeasyHTML = _importar_weasyprint()
            FALLO_WEASYPRINT = None
            WEASYPRINT_AUSENTE = False
        except Exception as exc:  # ImportError o fallo de librerias nativas (GTK/cairo)
            WeasyHTML = None
            FALLO_WEASYPRINT = f"{type(exc).__name__}: {exc}"
            WEASYPRINT_AUSENTE = isinstance(exc, ImportError)
    return WeasyHTML is not None


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
    # Por trozos (EXT-8, PC-12): el archivo se escribe segun se construye y
    # la memoria de los puntos --- el bloque que crece con N --- nunca esta
    # entera en RAM. Se escribe en un archivo temporal AL LADO y se renombra
    # al terminar: un fallo a mitad (un `ErrorProyecto` en el punto 7) no
    # deja un HTML truncado con el nombre del bueno (auditoria adversarial de
    # EXT-8); antes, con `write_text` de la cadena entera, tampoco lo dejaba.
    #
    # --- VE-5 (ficha UI5-01 d) --- por `escritura_atomica.escribir_atomico`,
    # la de los PDF: el temporal FIJO «<destino>.parcial» tenia los cuatro
    # defectos que la revision de UI-5 midio (H3): nombre largo, archivo del
    # usuario pisado, temporal compartido entre dos exportaciones y enlace
    # simbolico convertido en archivo regular sin conservar el modo.
    from src import escritura_atomica

    def escribir(temporal: Path) -> None:
        with Path(temporal).open("w", encoding="utf-8") as f:
            for trozo in memoria_html_por_partes(informe, **kwargs):
                f.write(trozo)

    escritura_atomica.escribir_atomico(destino, escribir)
    return destino


def exportar_csv(informe: Any, destino: Path) -> Path:
    """
    Escribe el cuadro resumen (entregable 3) como CSV, una fila por punto.
    Mismas columnas y misma fuente de datos que `fila_resumen` en la memoria
    HTML: es el mismo cuadro, en un formato que se abre en una hoja de calculo.
    Desde T-11 (H8) no lee la hoja de ruta: el tipo de cabezal es el de cada
    punto (`tipo_cabezal_del_punto`), y el parametro `ruta_hoja` se retiro.
    """
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    # --- VE-5 (ficha UI5-01 d) --- atomica, como la memoria: hasta VE-5
    # escribia directo y un fallo a mitad dejaba el cuadro cortado con el
    # nombre del bueno.
    from src import escritura_atomica

    def escribir(temporal: Path) -> None:
        with Path(temporal).open("w", encoding="utf-8", newline="") as f:
            escritor = csv.writer(f)
            escritor.writerow(COLUMNAS_RESUMEN_CSV)
            for p in informe.puntos:
                escritor.writerow(_fila_resumen_csv(p))

    escritura_atomica.escribir_atomico(destino, escribir)
    return destino


def exportar_html_resumida(informe: Any, destino: Path, **kwargs: Any) -> Path:
    """
    --- T-12 --- Escribe la memoria RESUMIDA como HTML (los kwargs van a
    `memoria_resumida_html`). Atomica como `exportar_html`: un fallo no deja
    un archivo a medias con el nombre del bueno.
    """
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    contenido = memoria_resumida_html(informe, **kwargs)
    # --- VE-5 (ficha UI5-01 d) --- la misma escritura que la completa.
    from src import escritura_atomica
    escritura_atomica.escribir_atomico(
        destino, lambda temporal: Path(temporal).write_text(contenido, encoding="utf-8"))
    return destino


def exportar_pdf_resumida(informe: Any, destino: Path, *,
                          abrir_navegador: bool = True,
                          forzar_navegador: bool = False,
                          progreso: Optional[Callable[[str, int, int], None]] = None,
                          **kwargs: Any) -> ResultadoExportacion:
    """
    --- T-12 --- La memoria RESUMIDA en PDF, por las dos vias de
    `exportar_pdf` (weasyprint, o el HTML para imprimir desde el navegador).

    --- UI-2 --- `progreso(etapa, hecho, total)` recibe el avance del PDF
    (`ETAPA_PDF`) o del HTML para el navegador (`ETAPA_NAVEGADOR`), como en
    la completa: es lo que la CLI imprime con `--progreso` y la ventana lee
    del proceso hijo (EXT-8). La resumida se arma de una vez y no informa
    punto a punto. Plomeria: no cambia el contenido de la memoria.
    """
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    contenido = memoria_resumida_html(informe, **kwargs)
    return _escribir_pdf(contenido, destino, abrir_navegador=abrir_navegador,
                         forzar_navegador=forzar_navegador, progreso=progreso,
                         rotulo="Memoria resumida")


def exportar_pdf(informe: Any, destino: Path, *, abrir_navegador: bool = True,
                 forzar_navegador: bool = False,
                 progreso: Optional[Callable[[str, int, int], None]] = None,
                 **kwargs: Any) -> ResultadoExportacion:
    """
    Exporta la memoria a PDF por la misma via que ya usa `legacy/Tc.py`:

        1. `weasyprint` si esta instalado -> PDF directo en `destino`.
        2. Si no lo esta, se escribe el HTML (junto a `destino`, con extension
           .html) y se abre en el navegador para "Imprimir -> Guardar como
           PDF". La plantilla ya viene configurada en A4.

    No se agrega ninguna dependencia nueva: weasyprint es opcional en Tc.py y
    aqui tambien. El resultado declara cual de las dos vias se uso.

    `forzar_navegador` toma la via 2 CON weasyprint operativo: es la que la
    ventana ofrece por encima de `UMBRAL_PUNTOS_PDF` (EXT-8, PC-11), porque
    el PDF directo de 200 puntos costaba 6 minutos y 5.7 GB y el navegador
    pagina lo mismo sin que el proceso lo pague. `progreso(etapa, hecho,
    total)` recibe el avance de la memoria (`ETAPA_PUNTO`, `ETAPA_BLOQUES`)
    y del PDF (`ETAPA_PDF`), que la CLI vuelca como lineas de stdout.
    """
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    contenido = memoria_html(informe, progreso=progreso, **kwargs)
    return _escribir_pdf(contenido, destino, abrir_navegador=abrir_navegador,
                         forzar_navegador=forzar_navegador, progreso=progreso,
                         rotulo="Memoria")


def _escribir_pdf(contenido: str, destino: Path, *, abrir_navegador: bool,
                  forzar_navegador: bool,
                  progreso: Optional[Callable[[str, int, int], None]],
                  rotulo: str) -> ResultadoExportacion:
    """
    Las dos vias de `exportar_pdf` (weasyprint o el HTML para el navegador)
    sobre una memoria ya armada: la usan la completa y, desde T-12, la
    resumida (`exportar_pdf_resumida`). `rotulo` encabeza el mensaje.

    --- UI-5 (decision del dueño del 2026-11-15, ficha UI2-03) --- LAS DOS
    VIAS ESCRIBEN DE FORMA ATOMICA (`src/escritura_atomica.escribir_atomico`,
    la misma funcion que la entrega del PDF del hijo de la ventana):
    weasyprint escribe el PDF por partes, y sobre el destino final un fallo a
    mitad (disco lleno, cuota, E/S) dejaba el destino truncado y destruia el
    PDF que el usuario tuviera ahi. Vale para la CLI directa y para el
    proceso hijo de la ventana, que es la misma CLI. `ruta` es lo que se
    pidio; si es un enlace simbolico, se reemplaza el archivo enlazado.
    """
    # Importada aqui y no en la cabecera: es lo unico de este modulo que la
    # usa, y la cabecera no se mueve (las anclas por linea del manifiesto).
    from src import escritura_atomica
    weasyprint_disponible()
    if WeasyHTML is not None and not forzar_navegador:
        if progreso is not None:
            progreso(ETAPA_PDF, 0, 1)
        documento = WeasyHTML(string=contenido, base_url=str(DIR_PLANTILLAS))
        escritura_atomica.escribir_atomico(
            destino, lambda temporal: documento.write_pdf(str(temporal)))
        if progreso is not None:
            progreso(ETAPA_PDF, 1, 1)
        return ResultadoExportacion(
            ruta=destino, via=VIA_WEASYPRINT,
            mensaje=f"{rotulo} exportada a PDF con weasyprint: {destino}")

    respaldo = destino.with_suffix(".html")
    escritura_atomica.escribir_atomico(
        respaldo, lambda temporal: temporal.write_text(contenido, encoding="utf-8"))
    if progreso is not None:
        progreso(ETAPA_NAVEGADOR, 1, 1)
    if abrir_navegador:
        # --- VE-5 (ficha UI5-01 d) --- la copia que abre el navegador, con
        # un nombre UNICO del temporal del sistema: con el nombre fijo del
        # respaldo, dos memorias del mismo nombre se pisaban la una a la otra
        # mientras el navegador todavia leia la primera.
        descriptor, nombre = tempfile.mkstemp(prefix=f"{respaldo.stem}-",
                                              suffix=respaldo.suffix)
        with os.fdopen(descriptor, "w", encoding="utf-8") as f:
            f.write(contenido)
        webbrowser.open(Path(nombre).as_uri())
    return ResultadoExportacion(
        ruta=respaldo, via=VIA_NAVEGADOR,
        mensaje=_mensaje_via_navegador(respaldo))


def _por_que_no_hay_weasyprint() -> str:
    """
    Que le pasa a weasyprint en ESTA maquina, con la excepcion que lo dijo.

    Tres casos y no uno, porque las tres se arreglan distinto:
    no esta instalado (se instala), esta y sus librerias nativas no cargan (se
    instala GTK, no el paquete), o esta y funciona (y entonces no se llama a
    esta funcion).
    """
    if WEASYPRINT_AUSENTE:
        return ("weasyprint no esta instalado. Para exportar el PDF directo: "
                "pip install weasyprint")
    if FALLO_WEASYPRINT is None:                     # pragma: no cover
        return "weasyprint no se pudo usar en esta corrida"
    return (
        "weasyprint SI esta instalado y no pudo cargarse: le faltan sus "
        "librerias nativas (GTK -- GObject, Pango, Cairo, GDK-PixBuf), que "
        "`pip install weasyprint` NO trae y que en Windows hay que instalar "
        f"aparte. Lo que dijo el sistema al cargarlo: {FALLO_WEASYPRINT}")


def _mensaje_via_navegador(respaldo: Path) -> str:
    """El mensaje de la via de respaldo: que paso, que se hizo y que hacer."""
    return (
        f"{_por_que_no_hay_weasyprint()}\n\n"
        f"NO se perdio la memoria: se escribio en {respaldo} y se abrio en el "
        "navegador. Guardala como PDF con Ctrl+P -- la hoja ya esta en A4 y la "
        "plantilla trae su CSS de impresion, de modo que el PDF que sale por "
        "esta via es equivalente al que escribiria weasyprint. Es una VIA "
        "ALTERNATIVA, no un fallo de la exportacion.")
