# -*- coding: utf-8 -*-
"""
gui/exportacion_pdf.py
======================
LA EXPORTACION DEL PDF FUERA DEL HILO DE TK, POR SUBPROCESO (EXT-8, PC-11).

Por que un subproceso y no un hilo
----------------------------------
El unico cuello real de la ventana es el PDF: medido antes de EXT-8, 11 s y
287 MB para 4 puntos, 69 s y 1.29 GB para 40, 360 s y 5.7 GB para 200 --- y
todo en el hilo de Tk, o sea con la ventana congelada ---. El calculo es
despreciable (2 ms por punto). Un hilo no sirve: `criterios_adoptados`,
`datos_sitio` y `declaracion` guardan estado de modulo (`_OVERRIDES`,
`_USADOS`, el libro de procedencias) que no es seguro entre hilos, y
weasyprint tampoco libera la memoria que pide. Un PROCESO aparte aisla las
dos cosas: el estado no se comparte y la RAM vuelve al sistema al terminar.

El proceso hijo es la propia CLI:

    python cli.py --sesion <sesion.json> --pdf <destino> --json <aparte>
                  --plantilla <la del alcance> --progreso

La sesion serializada es la MISMA que «Guardar sesion» escribe (formato de
`src/sesion.py`): proyecto, CSV, datos externos, banderas, alcance y los
criterios declarados CON su procedencia, que la CLI repone por
`declaracion.restaurar_sesion` --- el mismo camino con guardia que la
ventana ---. Por eso el PDF del hijo describe la corrida de la ventana y no
otra: `sin_marca_de_tiempo` deja comparar los dos JSON, y el test de EXT-8
lo comprueba. El `--json` va a un archivo de trabajo aparte para que el hijo
no pise el `<csv>.informe.json` del usuario.

Que hace este modulo y que no
-----------------------------
Aqui vive lo que NO necesita Tk: armar el comando, lanzar el proceso, leer
su progreso de las lineas de stdout (`cli.PREFIJO_PROGRESO`), cancelarlo y
decir en que estado terminal quedo. La ventana solo llama a `sondear()`
desde un `after` periodico y pinta lo que devuelve. Asi la logica se prueba
sin ventana --- `tests/test_ext8_rendimiento_gui.py` corre el subproceso de
verdad --- y la ventana no tiene ninguna rama que un test de AST no vea.

No hay hilos ni lectura bloqueante: stdout y stderr del hijo van a un archivo
de trabajo y `sondear()` lee lo que haya llegado. Es la forma portable de
sondear un proceso sin bloquear (un pipe sin bloquear no existe igual en
Windows y en POSIX).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src import sesion as _sesion

# LOS LIMITES MEDIDOS, escritos donde el usuario los lee (la ayuda del
# boton). Son medidas del dictamen (PC-11), no valores de proyecto: no
# gobiernan ningun calculo. Por encima de `UMBRAL_PUNTOS_PDF` la ventana
# ofrece la via del navegador --- escribir el HTML y dejar que el navegador
# lo pagine con Ctrl+P ---, porque el PDF directo de 200 puntos costaba seis
# minutos y 5.7 GB y en un portatil de 8 GB no termina. El umbral es el
# tamano al que el PDF directo tardaba ~1 minuto (69 s para 40 puntos); con
# la memoria deduplicada de EXT-8 el coste marginal medido bajo a ~1.4 s y
# ~28 MB por punto, y el umbral se queda en el mismo numero porque 40 puntos
# siguen siendo ~1 minuto de espera con el boton apagado.
UMBRAL_PUNTOS_PDF = 40   # literal-ok: umbral de puntos medido (PC-11), no es magnitud del expediente
LIMITE_MEDIDO_PDF = ("medido: 11 s y 287 MB para 4 puntos, 69 s y 1.3 GB para 40, "
                     "360 s y 5.7 GB para 200 (antes de EXT-8); despues, "
                     "~1.4 s y ~28 MB por punto")

# Lo que la ventana muestra mientras el hijo trabaja, antes de la primera
# linea de progreso.
PROGRESO_INICIAL = "lanzando el proceso de exportacion"


class EstadoPdf(str, Enum):
    """El estado del proceso hijo. Tres terminales y dos no."""
    SIN_INICIAR = "sin iniciar"
    EN_MARCHA = "en marcha"
    TERMINADO = "terminado"
    CANCELADO = "cancelado"
    FALLIDO = "fallido"

    @property
    def terminal(self) -> bool:
        return self in (EstadoPdf.TERMINADO, EstadoPdf.CANCELADO,
                        EstadoPdf.FALLIDO)


def comando_exportar_pdf(*, interprete: str, cli: Path, sesion: Path,
                         destino: Path, plantilla: Path, json_aparte: Path) -> List[str]:
    """La linea de comandos del hijo. Es el contrato con `cli.main`."""
    return [str(interprete), str(cli), "--sesion", str(sesion),
            "--pdf", str(destino), "--json", str(json_aparte),
            "--plantilla", str(plantilla), "--progreso"]


def sesion_de_la_corrida(informe: Any, *, proyecto: str, csv: str,
                         datos_externos: str, externos: Dict[str, str],
                         alcance: str, formato_version: int,
                         app_version: str, datos_sitio: str = "",
                         id_sesion: str = "") -> Dict[str, Any]:
    """
    La sesion que describe LA CORRIDA que produjo `informe`, no los campos
    vivos de la ventana.

    Lo encontro el auditor adversarial de EXT-8: `_datos_de_sesion` leia
    `alcance_var`, `csv_var` y los externos AL EXPORTAR, y cambiar el radio o
    la luz despues de correr no invalida el informe (los `trace_add` solo
    refiltran). El hijo habria corrido OTRA obra --- expediente con luz 3,5
    --- sobre la plantilla del informe de perfil con 2,75: PC-15 reabierto
    por la via del PDF. Aqui las entradas son las que `ejecutar_pipeline`
    fotografio al correr, y los criterios salen del `ContextoCorrida`
    congelado (EXT-4): las claves declaradas o pisadas en caliente con el
    valor EFECTIVO con que gobernaron, y sus procedencias de entonces.
    """
    contexto = informe.contexto
    claves = tuple(contexto.declarados_en_caliente) + tuple(contexto.pisados_en_caliente)
    valores = {clave: contexto.valores_efectivos[clave] for clave in claves}
    procedencias = {clave: asdict(p) for clave, p in contexto.procedencias.items()
                    if clave in valores}
    # Los [S] declarados por sesion CON QUE CORRIO (EXT-10), de la foto y no
    # del registro vivo, con su trazabilidad y su fecha: el hijo los repone
    # por `declaracion.restaurar_datos_de_sitio`, la misma guardia.
    sitio = {clave: {"valor": contexto.dato_efectivo(clave).valor,
                     "trazabilidad": contexto.dato_efectivo(clave).trazabilidad,
                     "fecha": contexto.dato_efectivo(clave).fecha}
             for clave in contexto.datos_declarados_en_caliente}
    return {
        "formato_version": formato_version,
        "app_version": app_version,
        "id": id_sesion,
        "proyecto": proyecto,
        "csv": csv,
        "datos_externos": datos_externos,
        "datos_sitio": datos_sitio,
        "externos": dict(externos),
        "alcance": alcance,
        "criterios": {"valores": valores, "procedencias": procedencias},
        "sitio": {"valores": sitio},
        "csv_sha1": contexto.csv_sha1,
        # El hijo recalcula (ficha EXT-8-02): no necesita las corridas.
        "corridas": [],
    }


# `sin_marca_de_tiempo` vive en `src/sesion.py` desde EXT-10 (la CLI la usa
# para comparar su corrida con la embebida en la sesion) y se reexporta aqui
# con el mismo nombre, que es como la leen la ventana y la suite.
sin_marca_de_tiempo = _sesion.sin_marca_de_tiempo


class ProcesoPdf:
    """
    Un proceso hijo que escribe el PDF de UNA sesion, sondeable.

    Ciclo: `iniciar()` -> `sondear()` hasta que `estado.terminal` ->
    `detalle` con el mensaje terminal. `cancelar()` termina el hijo; el
    estado pasa a CANCELADO en el siguiente `sondear()`. `progreso` es la
    ultima linea de avance que llego; `progreso_visto`, todas.
    """

    def __init__(self, *, sesion: Dict[str, Any], destino: Path, plantilla: Path,
                 directorio_trabajo: Path, interprete: Optional[str] = None,
                 raiz: Optional[Path] = None):
        self.sesion = sesion
        self.destino = Path(destino)
        self.plantilla = Path(plantilla)
        self.directorio_trabajo = Path(directorio_trabajo)
        self.interprete = interprete or sys.executable
        self.raiz = Path(raiz) if raiz is not None else Path(__file__).resolve().parents[1]
        self.ruta_sesion = self.directorio_trabajo / "sesion_para_pdf.json"
        self.ruta_json = self.directorio_trabajo / "informe_para_pdf.json"
        self.ruta_salida = self.directorio_trabajo / "salida_del_hijo.txt"
        self.comando: List[str] = []
        self.estado = EstadoPdf.SIN_INICIAR
        self.detalle = ""
        self.progreso = PROGRESO_INICIAL
        self.progreso_visto: List[str] = []
        self._proceso: Optional[subprocess.Popen] = None
        self._salida = None
        self._cancelado = False
        self._leido = 0

    # ------------------------------------------------------------------
    def iniciar(self) -> None:
        """Escribe la sesion de trabajo y lanza el hijo. No espera."""
        from cli import PREFIJO_PROGRESO  # noqa: F401  (el contrato existe)
        self.directorio_trabajo.mkdir(parents=True, exist_ok=True)
        # Escritura atomica (E04): el hijo nunca lee una sesion a medias.
        _sesion.escribir_json_atomico(self.ruta_sesion, self.sesion)
        self.comando = comando_exportar_pdf(
            interprete=self.interprete, cli=self.raiz / "cli.py",
            sesion=self.ruta_sesion, destino=self.destino,
            plantilla=self.plantilla, json_aparte=self.ruta_json)
        self._salida = self.ruta_salida.open("w+b")
        try:
            self._proceso = subprocess.Popen(
                self.comando, cwd=str(self.raiz), stdout=self._salida,
                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        except OSError as exc:
            # Un hijo que no arranca (interprete inexistente, sin permisos)
            # es un estado TERMINAL, no uno «sin iniciar» del que nadie
            # sale: la ventana lo mostraria como «en marcha» para siempre
            # (auditoria adversarial de EXT-8).
            self._salida.close()
            self.estado = EstadoPdf.FALLIDO
            self.detalle = (f"No se pudo lanzar el proceso que escribe el PDF "
                            f"({type(exc).__name__}: {exc}). Comando: "
                            f"{' '.join(self.comando)}")
            return
        self.estado = EstadoPdf.EN_MARCHA

    def limpiar(self) -> None:
        """Retira el directorio de trabajo. Solo tiene sentido en estado terminal."""
        if self.estado.terminal:
            shutil.rmtree(self.directorio_trabajo, ignore_errors=True)

    def cancelar(self) -> None:
        """Termina el hijo. El estado se cierra en el siguiente `sondear()`."""
        if self._proceso is None or self._proceso.poll() is not None:
            return
        self._cancelado = True
        self._proceso.terminate()

    def sondear(self) -> EstadoPdf:
        """
        Lee lo nuevo de la salida del hijo y devuelve el estado. No bloquea:
        es lo que la ventana llama desde `after`.
        """
        if self._proceso is None or self.estado.terminal:
            return self.estado
        self._leer_salida()
        codigo = self._proceso.poll()
        if codigo is None:
            return self.estado
        self._salida.flush()
        self._leer_salida()
        self._salida.close()
        if self._cancelado:
            self.estado = EstadoPdf.CANCELADO
            self.detalle = ("Exportacion cancelada: el proceso se termino y no "
                            "se escribio el PDF.")
            self._retirar_pdf_a_medias()
        elif self.destino.is_file() and self.destino.stat().st_size > 0:
            self.estado = EstadoPdf.TERMINADO
            self.detalle = f"PDF escrito: {self.destino}"
        else:
            self.estado = EstadoPdf.FALLIDO
            cola = self._cola_de_salida()
            self.detalle = (f"La exportacion fallo (codigo {codigo}) y no dejo "
                            f"PDF. Lo que dijo el proceso:\n{cola}")
        return self.estado

    # ------------------------------------------------------------------
    def _leer_salida(self) -> None:
        from cli import PREFIJO_PROGRESO
        try:
            datos = self.ruta_salida.read_bytes()
        except OSError:
            return
        nuevo = datos[self._leido:]
        if not nuevo:
            return
        # Solo lineas completas: la ultima puede estar a medias.
        corte = nuevo.rfind(b"\n")
        if corte < 0:
            return
        self._leido += corte + 1
        for linea in nuevo[:corte].decode("utf-8", errors="replace").splitlines():
            if linea.startswith(PREFIJO_PROGRESO):
                texto = linea[len(PREFIJO_PROGRESO):].strip()
                self.progreso = texto
                self.progreso_visto.append(texto)

    def _cola_de_salida(self, lineas: int = 12) -> str:  # literal-ok: lineas de la cola del diagnostico
        try:
            texto = self.ruta_salida.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return "(sin salida)"
        return "\n".join(texto.rstrip().splitlines()[-lineas:]) or "(sin salida)"

    def _retirar_pdf_a_medias(self) -> None:
        # weasyprint escribe el archivo al final, de una vez; si el `terminate`
        # llego durante la escritura puede quedar un PDF truncado, que es
        # peor que ninguno.
        try:
            if self.destino.exists():
                self.destino.unlink()
        except OSError:
            pass
