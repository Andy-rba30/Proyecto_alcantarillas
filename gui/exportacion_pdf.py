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

    python cli.py --sesion <sesion.json> --pdf <pdf de trabajo>
                  --json <aparte> --plantilla <la del alcance> --progreso

y desde UI-2 (ficha T12-04) escribe tambien la memoria RESUMIDA, la vista
para imprimir, con la MISMA linea salvo la bandera de la vista:

    python cli.py --sesion <sesion.json> --pdf-resumida <pdf de trabajo>
                  --json <aparte> --progreso

La resumida no lleva `--plantilla`: la suya es fija
(`M11.NOMBRE_PLANTILLA_RESUMIDA`) y la CLI solo usa `--plantilla` para la
completa. Las dos salen de `comando_exportar_pdf`, con la vista como
parametro: una sola funcion arma el contrato con `cli.main`.

El hijo NO escribe en el destino que eligio el usuario (revision de UI-2,
ficha UI2-03): escribe en su directorio de trabajo, y el PDF se ENTREGA al
destino solo si el hijo salio con un codigo que escribe la memoria
(`CODIGOS_DE_SALIDA_CON_MEMORIA`) y dejo un PDF suyo y ENTERO, con su
trailer (`_pdf_de_trabajo_entero`). Hasta UI-2 escribia en
el destino y el exito se leia de «el destino existe y no esta vacio»: un
hijo que fallaba sobre un destino con un PDF anterior se daba por terminado
con el archivo VIEJO, y cancelar borraba un PDF bueno que ya estuviera ahi.
Fallar o cancelar no tocan el destino.

La sesion serializada es la MISMA que «Guardar sesion» escribe (formato de
`src/sesion.py`): proyecto, CSV, datos externos, las dos entradas de la
hidrologia (desde el formato 4, UI-1), banderas, alcance y los
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
import os
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


# QUE CODIGOS DE SALIDA DEL HIJO DEJAN MEMORIA (revision de UI-2, ficha
# UI2-03). Es el contrato de `cli.main` (README, §4): 0 si el expediente
# cierra y 1 si corre y NO cierra --- en los dos escribe la memoria ---, 2 si
# no se pudo correr. Exigir 0 daria por fallido el PDF de todo expediente que
# todavia no cierra, que es el caso corriente mientras se diseña. Un 1 de
# Python (una excepcion sin atrapar) no se confunde con el de «no cierra»
# porque el exito exige ADEMAS un PDF de trabajo de este hijo y ENTERO
# (`_pdf_de_trabajo_entero`): weasyprint escribe por partes, cabecera primero
# y `%%EOF` al final, y un fallo a mitad (disco lleno, cuota, E/S) dejaba un
# archivo que empieza por `%PDF`, sale con 1 y se entregaba truncado
# (verificacion de la revision de UI-2).
CODIGOS_DE_SALIDA_CON_MEMORIA = (0, 1)

# Donde tiene que estar el marcador de fin de archivo de un PDF entero: en
# sus ultimos 1024 bytes, que es lo que la referencia de PDF admite (y lo que
# los lectores buscan). Es un limite del FORMATO, no un valor del expediente.
COLA_DEL_PDF_BYTES = 1024   # literal-ok: ventana del trailer %%EOF de la referencia de PDF, bytes

# LO QUE EL PDF DEL HIJO ES, dicho antes de pulsar (revision de UI-2). El
# hijo VUELVE A CORRER la obra con la sesion de la corrida (ficha EXT-8-02):
# su encabezado de trazabilidad lleva la hora de ESA corrida, no la de la
# ventana, y las huellas de los archivos tal como esten al exportar. Un solo
# texto para las ayudas de los dos botones de PDF.
AVISO_EL_HIJO_RECALCULA = (
    "El proceso aparte VUELVE A CORRER la obra con la sesion de esta\n"
    "corrida: el encabezado de trazabilidad del PDF lleva la hora de\n"
    "ESA corrida, no la de la ventana, y las huellas de los archivos\n"
    "tal como esten en disco al exportar.")

# LAS DOS VISTAS DE LA MEMORIA QUE EL HIJO SABE ESCRIBIR (T-12, UI-2): la
# completa (el anexo digital) y la resumida (la que se imprime), las dos del
# MISMO informe. Cada una con la bandera de `cli.py` que la pide y con el
# rotulo con que la ventana la nombra mientras se escribe y al terminar.
VISTA_COMPLETA = "completa"
VISTA_RESUMIDA = "resumida"
BANDERA_DE_LA_VISTA = {VISTA_COMPLETA: "--pdf", VISTA_RESUMIDA: "--pdf-resumida"}
ROTULO_DE_LA_VISTA = {VISTA_COMPLETA: "PDF", VISTA_RESUMIDA: "PDF resumido"}


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
                         destino: Path, json_aparte: Path,
                         plantilla: Optional[Path] = None,
                         vista: str = VISTA_COMPLETA) -> List[str]:
    """
    La linea de comandos del hijo. Es el contrato con `cli.main`.

    `vista` elige la bandera (`BANDERA_DE_LA_VISTA`); el resto de la linea
    es el mismo para las dos. La completa exige su plantilla --- la del
    alcance de la corrida, la que la ventana elige con
    `cli.plantilla_por_alcance` ---; la resumida no la lleva, porque la CLI
    solo la aplica a `--html` y `--pdf`.
    """
    if vista not in BANDERA_DE_LA_VISTA:
        raise ValueError(f"vista de la memoria desconocida: {vista!r}; las que "
                         f"el hijo escribe son {sorted(BANDERA_DE_LA_VISTA)}")
    if vista == VISTA_COMPLETA and plantilla is None:
        raise ValueError("la memoria completa necesita su plantilla (la del "
                         "alcance de la corrida)")
    comando = [str(interprete), str(cli), "--sesion", str(sesion),
               BANDERA_DE_LA_VISTA[vista], str(destino), "--json", str(json_aparte)]
    if vista == VISTA_COMPLETA:
        comando += ["--plantilla", str(plantilla)]
    return comando + ["--progreso"]


def sesion_de_la_corrida(informe: Any, *, proyecto: str, csv: str,
                         datos_externos: str, externos: Dict[str, str],
                         alcance: str, formato_version: int,
                         app_version: str, datos_sitio: str = "",
                         id_sesion: str = "", cuencas: str = "",
                         estacion: str = "") -> Dict[str, Any]:
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

    `cuencas` y `estacion` (UI-1, ficha T1-04, formato 4) son las rutas de
    las dos entradas de la hidrologia CON QUE CORRIO el informe, tambien
    fotografiadas por `ejecutar_pipeline`: sin ellas el hijo recalculaba sin
    la hidrologia que la ventana uso, con el `Q_m3s` vacio de una obra con
    cuenca convertido en «falta el dato». A diferencia del `sitio.json`
    viajan como RUTAS --- no hay bloque que las sustituya ---, igual que el CSV
    y el JSON de datos externos: el hijo relee los tres archivos (ficha
    EXT-8-02), y la huella de cada uno queda en su JSON para compararla.
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
                     "fecha": contexto.dato_efectivo(clave).fecha,
                     "origen": contexto.dato_efectivo(clave).origen}
             for clave in contexto.datos_declarados_en_caliente}
    return {
        "formato_version": formato_version,
        "app_version": app_version,
        "id": id_sesion,
        "proyecto": proyecto,
        "csv": csv,
        "datos_externos": datos_externos,
        # La RUTA del sitio.json no viaja al hijo: si la sesion trae ruta y
        # bloque, la ruta gana (misma regla en las dos puertas) y el hijo
        # releeria un archivo que pudo cambiar tras la corrida (PC-15). El
        # bloque lleva el origen real de cada dato, que es lo que imprime.
        "datos_sitio": "",
        "cuencas": cuencas,
        "estacion": estacion,
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

    `vista` (UI-2) dice cual de las dos memorias escribe el hijo: la completa,
    con su `plantilla`, o la resumida, que no la lleva. El ciclo, el
    progreso, la cancelacion y el estado terminal son los mismos.
    """

    def __init__(self, *, sesion: Dict[str, Any], destino: Path,
                 directorio_trabajo: Path, plantilla: Optional[Path] = None,
                 vista: str = VISTA_COMPLETA, interprete: Optional[str] = None,
                 raiz: Optional[Path] = None):
        self.sesion = sesion
        self.destino = Path(destino)
        self.plantilla = None if plantilla is None else Path(plantilla)
        self.vista = vista
        self.directorio_trabajo = Path(directorio_trabajo)
        self.interprete = interprete or sys.executable
        self.raiz = Path(raiz) if raiz is not None else Path(__file__).resolve().parents[1]
        self.ruta_sesion = self.directorio_trabajo / "sesion_para_pdf.json"
        self.ruta_json = self.directorio_trabajo / "informe_para_pdf.json"
        self.ruta_salida = self.directorio_trabajo / "salida_del_hijo.txt"
        # Donde escribe el hijo: en el directorio de trabajo, nunca en el
        # destino del usuario (ficha UI2-03). Se entrega al terminar bien.
        self.ruta_pdf_de_trabajo = self.directorio_trabajo / "memoria_del_hijo.pdf"
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
        # Lo que un hijo ANTERIOR hubiera dejado en este directorio no es de
        # este: si este falla sin escribir, no se entrega lo de aquel.
        for anterior in (self.ruta_pdf_de_trabajo, self.ruta_json):
            anterior.unlink(missing_ok=True)
        # Escritura atomica (E04): el hijo nunca lee una sesion a medias.
        _sesion.escribir_json_atomico(self.ruta_sesion, self.sesion)
        self.comando = comando_exportar_pdf(
            interprete=self.interprete, cli=self.raiz / "cli.py",
            sesion=self.ruta_sesion, destino=self.ruta_pdf_de_trabajo,
            plantilla=self.plantilla, json_aparte=self.ruta_json,
            vista=self.vista)
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

    def terminar_y_limpiar(self, tope_s: float) -> None:
        """
        AL CERRAR LA VENTANA PRINCIPAL (UI-4, fichas UI4-01 y UI4-03). Al
        final siempre retira el directorio de trabajo; antes, uno de dos
        casos, que separa el `poll()` del cierre:

        - El hijo SIGUE EN MARCHA: se termina, se ESPERA a que salga ---
          acotado por `tope_s`; si no sale, se mata --- y el estado es
          CANCELADO: el destino del usuario no se toca, como al pulsar
          «Cancelar PDF».
        - El hijo YA SALIO y la ventana no llego a sondearlo (el sondeo es
          cada `CADENCIA_SONDEO_PDF_MS` de `gui/app.py`): se cierra como lo
          habria cerrado ese sondeo (`sondear`). Un PDF entero se entrega al
          destino (TERMINADO): el usuario lo pidio y ya esta escrito, y
          tirarlo al cerrar perderia un trabajo terminado. Un hijo que fallo
          no lo toca (FALLIDO).

        Es el gesto de `proceso_barrido.ProcesoBarrido.terminar_y_limpiar`
        (H3 de UI-3): sin el, cerrar la ventana con un PDF en marcha dejaba
        el hijo escribiendo para nadie y su carpeta --- la sesion con sus
        declaraciones --- en el temporal (ficha UI3-02, abierto (3)).
        """
        if self._proceso is not None and self._proceso.poll() is None:
            self.cancelar()
            try:
                self._proceso.wait(timeout=tope_s)
            except subprocess.TimeoutExpired:
                self._proceso.kill()
                self._proceso.wait(timeout=tope_s)
        self.sondear()
        if self.estado is EstadoPdf.SIN_INICIAR:
            self.estado = EstadoPdf.CANCELADO
        self.limpiar()

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
        rotulo = ROTULO_DE_LA_VISTA[self.vista]
        if self._cancelado:
            # Lo que el hijo dejara a medias esta en el directorio de
            # trabajo, que `limpiar()` retira: el destino no se toca.
            self.estado = EstadoPdf.CANCELADO
            self.detalle = ("Exportacion cancelada: el proceso se termino y no "
                            f"se escribio el {rotulo}; {self.destino} no se toco.")
        elif codigo in CODIGOS_DE_SALIDA_CON_MEMORIA and self._pdf_de_trabajo_entero():
            try:
                self._entregar()
            except OSError as exc:
                self.estado = EstadoPdf.FALLIDO
                self.detalle = (f"El proceso escribio el {rotulo} pero no se pudo "
                                f"copiar a {self.destino}: {exc}")
            else:
                self.estado = EstadoPdf.TERMINADO
                self.detalle = f"{rotulo} escrito: {self.destino}"
        else:
            self.estado = EstadoPdf.FALLIDO
            cola = self._cola_de_salida()
            self.detalle = (f"La exportacion fallo (codigo {codigo}) y no dejo "
                            f"PDF; {self.destino} no se toco. Lo que dijo el "
                            f"proceso:\n{cola}")
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

    def _pdf_de_trabajo_entero(self) -> bool:
        """
        El hijo dejo SU PDF y ENTERO: el de trabajo (que `iniciar` vacio)
        empieza por `%PDF` y termina con el trailer `%%EOF` en sus ultimos
        `COLA_DEL_PDF_BYTES`. Un PDF cortado a mitad de la escritura empieza
        bien y no termina: no se entrega.
        """
        try:
            with self.ruta_pdf_de_trabajo.open("rb") as f:
                if f.read(len(b"%PDF")) != b"%PDF":
                    return False
                f.seek(0, os.SEEK_END)
                f.seek(max(0, f.tell() - COLA_DEL_PDF_BYTES))
                return b"%%EOF" in f.read()
        except OSError:
            return False

    def _entregar(self) -> None:
        """
        Copia el PDF de trabajo al destino, de forma atomica: primero a un
        `.parcial` junto al destino (el directorio de trabajo puede estar en
        otro sistema de archivos, y `os.replace` no cruza de uno a otro) y
        despues `os.replace`. Un fallo a mitad deja el destino como estaba.
        """
        self.destino.parent.mkdir(parents=True, exist_ok=True)
        parcial = self.destino.with_name(self.destino.name + ".parcial")
        try:
            shutil.copyfile(self.ruta_pdf_de_trabajo, parcial)
            os.replace(parcial, self.destino)
        finally:
            if parcial.exists():
                parcial.unlink()
