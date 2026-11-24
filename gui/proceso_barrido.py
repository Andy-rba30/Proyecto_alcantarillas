# -*- coding: utf-8 -*-
"""
gui/proceso_barrido.py
======================
EL BARRIDO DE LA PESTAÑA 2 FUERA DEL HILO DE TK, POR SUBPROCESO (UI-3, ficha
PF-3-01; la decision, en la ficha UI3-01 de `docs/decisiones_diferidas.md`).

Por que un subproceso y no un hilo
----------------------------------
`barrido.barrer` corre el pipeline una vez por valor y, entre corrida y
corrida, DECLARA el valor barrido en el estado de modulo de
`criterios_adoptados` y `declaracion` (`_OVERRIDES`, el libro de
procedencias) y lo repone al salir con `restaurar_sesion(sustituir=True)`.
En el proceso de la ventana eso es, mientras dura, OTRO estado: la pestaña 2
pintaria el valor barrido como declarado, un «Aplicar» a medias se lo
llevaria la reposicion, y una corrida o una exportacion de la ventana en
ese intervalo leeria lo que no es. Es la razon por la que EXT-8 saco el PDF
a un proceso aparte (`gui/exportacion_pdf.py`), y aqui vale igual: el estado
de los tres archivos de valores no es seguro entre hilos.

El hijo es la propia CLI, con el patron de EXT-8:

    python cli.py --sesion <sesion.json> --barrido CLAVE=v1,v2,...
                  [--barrido-fila=<fila>] [--barrido-nota=<nota>]
                  --json <temporal>

La sesion es la de la ventana (`ExpedienteApp._datos_de_sesion`, lo que
«Guardar sesion» escribe: proyecto, CSV, datos externos, las dos rutas de
la hidrologia de UI-1, banderas, alcance y los criterios declarados CON su
procedencia), sin las corridas embebidas y con los datos de sitio que
EJECUTAR declararia (`sesion_para_el_barrido`). La CLI la repone por
`declaracion.restaurar_sesion` --- el mismo camino con guardia que la
ventana ---, vuelve a cerrar la puerta del barrido
(`barrido.verificar_valores`) y escribe el JSON del barrido, que la ventana
lee de vuelta con `barrido.resultado_del_volcado` para pintar las MISMAS
lineas que la CLI imprime (`barrido.lineas_de_la_tabla`).

Que hace este modulo y que no
-----------------------------
Aqui vive lo que NO necesita Tk: armar el texto de `--barrido` y el
comando, la sesion del hijo, lanzar el proceso, sondearlo sin bloquear,
cancelarlo y leer su resultado. La ventana (`gui/ventana_barrido.py`) solo
llama a `sondear()` desde un `after` y pinta lo que devuelve. No hay hilos ni
lectura bloqueante: stdout y stderr del hijo van a un archivo de trabajo,
como en `gui/exportacion_pdf.py`.
"""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import tempfile
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src import barrido as _barrido
from src import sesion as _sesion
from src.modelos import ResultadoDeBarrido

from gui.exportacion_pdf import lanzador_de_la_cli

# Lo que la ventana muestra mientras el hijo trabaja.
PROGRESO_INICIAL = "lanzando el proceso del barrido"

# El ORIGEN con que la ventana declara los [S] del bloque `sitio` de la
# sesion abierta cuando el campo «JSON de datos de sitio» esta vacio
# (`ExpedienteApp._declarar_datos_de_sitio` lo usa). Viaja al hijo en cada
# entrada que no traiga el suyo: sin el, el hijo registraba como origen su
# sesion TEMPORAL de trabajo, que se borra (revision de UI-3, H6; el mismo
# defecto que EXT-10 corrigio en el hijo del PDF).
ORIGEN_SESION_ABIERTA = "sesion abierta"

# Cuanto se espera, al CERRAR, a que el hijo terminado con `terminate()`
# salga antes de matarlo (`ProcesoBarrido.terminar_y_limpiar`). Solo al
# cerrar: mientras corre, la ventana sondea y nunca espera.
TOPE_AL_TERMINAR_S = 5   # literal-ok: espera acotada al cerrar, s; no es magnitud del expediente


class EstadoDelBarrido(str, Enum):
    """El estado del proceso hijo. Tres terminales y dos no."""
    SIN_INICIAR = "sin iniciar"
    EN_MARCHA = "en marcha"
    TERMINADO = "terminado"
    CANCELADO = "cancelado"
    FALLIDO = "fallido"

    @property
    def terminal(self) -> bool:
        return self in (EstadoDelBarrido.TERMINADO, EstadoDelBarrido.CANCELADO,
                        EstadoDelBarrido.FALLIDO)


def texto_del_barrido(clave: str, valores: Sequence[Any]) -> str:
    """
    El argumento de `--barrido` (`CLAVE=v1,v2,...`) para estos valores:
    cada uno por su `repr`, que `cli.valores_del_barrido` lee de vuelta con
    `ast.literal_eval` --- una tupla sigue siendo tupla, un texto con coma
    sigue siendo un texto ---. Se COMPRUEBA leyendolo con la misma funcion
    que el hijo: un valor que no volviera igual no se manda (`ValueError`),
    porque el hijo barreria otra cosa que lo pedido.
    """
    from cli import valores_del_barrido   # perezoso: la CLI es el contrato
    texto = f"{clave}=" + ",".join(repr(v) for v in valores)
    leida, leidos = valores_del_barrido(texto)
    if leida != clave or [repr(v) for v in leidos] != [repr(v) for v in valores]:
        raise ValueError(
            f"los valores {list(valores)!r} de '{clave}' no se pueden escribir "
            "para la linea de comandos sin cambiar: el hijo barreria otra cosa")
    return texto


def comando_del_barrido(*, interprete: str, cli: Optional[Path], sesion: Path, clave: str,
                        valores: Sequence[Any], fila: str, nota: str,
                        json_salida: Path) -> List[str]:
    """
    La linea de comandos del hijo. Es el contrato con `cli.main`. La fila y
    la nota van con `=` pegado, para que una nota que empiece por un guion
    no se lea como otra bandera.
    """
    # Sin `cli` (el paquete congelado): el programa ES la CLI
    # (`exportacion_pdf.lanzador_de_la_cli`).
    comando = [str(interprete), *([] if cli is None else [str(cli)]),
               "--sesion", str(sesion), "--barrido", texto_del_barrido(clave, valores)]
    if fila:
        comando.append(f"--barrido-fila={fila}")
    if nota:
        comando.append(f"--barrido-nota={nota}")
    comando += ["--json", str(json_salida)]
    return comando


def sesion_para_el_barrido(datos_de_sesion: Dict[str, Any], *,
                           sitio_de_la_sesion: Dict[str, Any]) -> Dict[str, Any]:
    """
    La sesion que el hijo repone: la de la ventana (`datos_de_sesion`, lo
    que «Guardar sesion» escribe) en una COPIA, sin las corridas embebidas
    (el hijo barre y no compara con ninguna) y con los datos de sitio que
    EJECUTAR declararia en este momento: con ruta en el campo, la ruta (la
    CLI la relee y el bloque se vacia, para que no avise de un bloque que no
    gobierna); sin ruta, el bloque de la sesion abierta
    (`ExpedienteApp._declarar_datos_de_sitio`, la misma regla que
    `cli._aplicar_datos_de_sitio`), con el origen que la ventana registra
    (`ORIGEN_SESION_ABIERTA`) en cada entrada que no traiga el suyo.
    """
    # Las corridas NO se copian: su `informe_json` lleva objetos del
    # registro normativo que no se copian en profundidad (los serializa
    # `escribir_json_atomico`), y el hijo no las lee.
    sesion = copy.deepcopy({clave: valor for clave, valor in datos_de_sesion.items()
                            if clave != "corridas"})
    sesion["corridas"] = []
    sesion["csv_sha1"] = ""
    if str(sesion.get("datos_sitio") or "").strip():
        sesion["sitio"] = {"valores": {}}
    else:
        sitio = copy.deepcopy(sitio_de_la_sesion or {"valores": {}})
        for entrada in (sitio.get("valores") or {}).values():
            if isinstance(entrada, dict) and not str(entrada.get("origen") or "").strip():
                entrada["origen"] = ORIGEN_SESION_ABIERTA
        sesion["sitio"] = sitio
    return sesion


class ProcesoBarrido:
    """
    Un proceso hijo que barre UNA clave sobre una lista de valores,
    sondeable.

    Ciclo: `iniciar()` -> `sondear()` hasta que `estado.terminal` ->
    `resultado` y `lineas` (TERMINADO) o `detalle` con el motivo. El
    directorio de trabajo (la sesion, la salida del hijo y su JSON) es suyo:
    lo crea al iniciar y `limpiar()` lo retira en un estado terminal.
    `cwd` es el directorio desde el que el hijo resuelve las rutas relativas
    de la sesion: por defecto el de la ventana, que es desde donde ella las
    resolveria al ejecutar.
    """

    def __init__(self, *, sesion: Dict[str, Any], clave: str, valores: Sequence[Any],
                 fila: str = "", nota: str = "",
                 directorio_trabajo: Optional[Path] = None,
                 interprete: Optional[str] = None, raiz: Optional[Path] = None,
                 cwd: Optional[Path] = None):
        self.sesion = sesion
        self.clave = clave
        self.valores = tuple(valores)
        self.fila = fila
        self.nota = nota
        self.directorio_trabajo = (Path(directorio_trabajo) if directorio_trabajo
                                   else Path(tempfile.mkdtemp(prefix="alcantarillas_barrido_")))
        self.raiz = Path(raiz) if raiz is not None else Path(__file__).resolve().parents[1]
        self.interprete, self.cli = lanzador_de_la_cli(interprete, self.raiz)
        self.cwd = Path(cwd) if cwd is not None else Path.cwd()
        self.ruta_sesion = self.directorio_trabajo / "sesion_para_el_barrido.json"
        self.ruta_json = self.directorio_trabajo / "barrido.json"
        self.ruta_salida = self.directorio_trabajo / "salida_del_hijo.txt"
        self.comando: List[str] = []
        self.estado = EstadoDelBarrido.SIN_INICIAR
        self.detalle = ""
        self.progreso = PROGRESO_INICIAL
        self.resultado: Optional[ResultadoDeBarrido] = None
        self.lineas: Tuple[str, ...] = ()
        self.inicio: Optional[float] = None
        self._proceso: Optional[subprocess.Popen] = None
        self._salida = None
        self._cancelado = False

    # ------------------------------------------------------------------
    def iniciar(self) -> None:
        """Escribe la sesion de trabajo y lanza el hijo. No espera."""
        self.directorio_trabajo.mkdir(parents=True, exist_ok=True)
        # Escritura atomica (E04): el hijo nunca lee una sesion a medias.
        _sesion.escribir_json_atomico(self.ruta_sesion, self.sesion)
        self.comando = comando_del_barrido(
            interprete=self.interprete, cli=self.cli,
            sesion=self.ruta_sesion, clave=self.clave, valores=self.valores,
            fila=self.fila, nota=self.nota, json_salida=self.ruta_json)
        self._salida = self.ruta_salida.open("w+b")
        try:
            self._proceso = subprocess.Popen(
                self.comando, cwd=str(self.cwd), stdout=self._salida,
                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        except OSError as exc:
            # Un hijo que no arranca es un estado TERMINAL, no uno «sin
            # iniciar» del que nadie sale (la leccion de EXT-8).
            self._salida.close()
            self.estado = EstadoDelBarrido.FALLIDO
            self.detalle = (f"No se pudo lanzar el proceso del barrido "
                            f"({type(exc).__name__}: {exc}). Comando: "
                            f"{' '.join(self.comando)}")
            return
        self.inicio = time.monotonic()
        self.estado = EstadoDelBarrido.EN_MARCHA
        self.progreso = (f"barriendo '{self.clave}' sobre {len(self.valores)} "
                         "valor(es) en un proceso aparte")

    def segundos(self) -> float:
        """Lo que lleva corriendo, para el rotulo de la ventana."""
        return 0.0 if self.inicio is None else time.monotonic() - self.inicio

    def cancelar(self) -> None:
        """Termina el hijo. El estado se cierra en el siguiente `sondear()`."""
        if self._proceso is None or self._proceso.poll() is not None:
            return
        self._cancelado = True
        self._proceso.terminate()

    def sondear(self) -> EstadoDelBarrido:
        """
        Devuelve el estado sin bloquear: es lo que la ventana llama desde
        `after`. Al terminar lee el JSON del hijo y arma la tabla.
        """
        if self._proceso is None or self.estado.terminal:
            return self.estado
        codigo = self._proceso.poll()
        if codigo is None:
            return self.estado
        self._salida.close()
        if self._cancelado:
            self.estado = EstadoDelBarrido.CANCELADO
            self.detalle = ("Barrido cancelado: el proceso se termino y no "
                            "dejo tabla.")
            self._retirar_json()
            return self.estado
        if codigo != 0 or not self.ruta_json.is_file():
            self.estado = EstadoDelBarrido.FALLIDO
            self.detalle = (f"El barrido no termino (codigo {codigo}). Lo que "
                            f"dijo el proceso:\n{self._cola_de_salida()}")
            return self.estado
        try:
            datos = json.loads(self.ruta_json.read_text(encoding="utf-8"))
            self.resultado = _barrido.resultado_del_volcado(
                datos["barridos"][0], valores=self.valores)
        except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
            self.estado = EstadoDelBarrido.FALLIDO
            self.detalle = (f"El barrido termino pero su JSON no se pudo leer "
                            f"({type(exc).__name__}: {exc})")
            return self.estado
        self.lineas = _barrido.lineas_de_la_tabla(self.resultado)
        self.estado = EstadoDelBarrido.TERMINADO
        self.detalle = (f"Barrido terminado: {len(self.resultado.corridas)} "
                        f"corrida(s) de '{self.clave}'.")
        return self.estado

    def copiar_json(self, destino: Path) -> Path:
        """El JSON del hijo, tal cual, donde el usuario lo pida."""
        if self.estado is not EstadoDelBarrido.TERMINADO:
            raise OSError("el barrido no termino: no hay JSON que guardar")
        destino = Path(destino)
        shutil.copyfile(self.ruta_json, destino)
        return destino

    def limpiar(self) -> None:
        """Retira el directorio de trabajo. Solo en estado terminal."""
        if self.estado.terminal:
            shutil.rmtree(self.directorio_trabajo, ignore_errors=True)

    def terminar_y_limpiar(self, tope_s: float = TOPE_AL_TERMINAR_S) -> None:
        """
        AL CERRAR (la ventana del barrido o la principal): termina el hijo si
        sigue en marcha, ESPERA a que salga --- acotado; si no sale, lo mata
        --- y retira el directorio de trabajo. Es la unica espera del
        modulo, y no es la del sondeo: hasta la revision de UI-3 (H3) la
        limpieza se reprogramaba con `after` sobre la ventana principal, y
        si esa ventana se destruia el hijo quedaba huerfano y su carpeta
        (la sesion con sus declaraciones y procedencias, el JSON) en el
        temporal para siempre.
        """
        if self._proceso is not None and self._proceso.poll() is None:
            self.cancelar()
            try:
                self._proceso.wait(timeout=tope_s)
            except subprocess.TimeoutExpired:
                self._proceso.kill()
                self._proceso.wait(timeout=tope_s)
        self.sondear()
        if self.estado is EstadoDelBarrido.SIN_INICIAR:
            self.estado = EstadoDelBarrido.CANCELADO
        self.limpiar()

    # ------------------------------------------------------------------
    def _cola_de_salida(self, lineas: int = 12) -> str:  # literal-ok: lineas de la cola del diagnostico
        try:
            texto = self.ruta_salida.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return "(sin salida)"
        return "\n".join(texto.rstrip().splitlines()[-lineas:]) or "(sin salida)"

    def _retirar_json(self) -> None:
        try:
            if self.ruta_json.exists():
                self.ruta_json.unlink()
        except OSError:
            pass
