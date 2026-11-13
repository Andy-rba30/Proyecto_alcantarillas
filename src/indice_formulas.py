"""
indice_formulas.py
==================
El INDICE DE FORMULAS, generado desde los `PasoDeMemoria` de una corrida de
referencia. Hermano de `normativa/manifiesto.py::indice_del_registro` y con
el mismo contrato: se GENERA, no se edita, y un test lo regenera y compara.

Por que existe (plan I, sesion I4)
----------------------------------
El plan de cierre ingenieril pedia una «matriz de formulas» escrita a mano:
modulo, funcion, formula, cita y variables. Un documento asi envejece con el
commit siguiente, igual que el manifiesto anclado por numero de linea que
produjo NOR-MAN-04. Lo que no envejece solo es DERIVARLO del calculo: cada
funcion de calculo ya emite, con su resultado, el `PasoDeMemoria` que lo
explica --formula, `formula_cita_id`, sustitucion con la procedencia de cada
valor, umbral con su cita--, de modo que el indice es una VISTA de esos
objetos y no una segunda transcripcion.

Que son las corridas de referencia, y que alcanzan (T-10)
--------------------------------------------------------
HASTA T-10 ERA UNA SOLA CORRIDA, y no dimensionaba ningun punto:
`tests/ejemplo_puntos.csv` a `--alcance expediente` con
`tests/ejemplo_puntos.referencia.json`, donde las filas A y B se detenian en
V5 (`remanso_derecho_via` sin valor) y C-01 no traia caudal. El indice
listaba entonces las Fases 1, 2 y 4 y las verificaciones V1 a V4, y la
Fase 6, la 7, la 8, la 9 y la 10 quedaban en el cuadro de «no ejercitados».
INF-5.1.10 (que el prompt T-10 llama INF-5.1.9) pedia ver el paso del
control gobernante con su cita correcta en una corrida que DIMENSIONE.

DESDE T-10 SON DOS CORRIDAS (TRES DESDE T-11), con DATOS DE PRUEBA que se
leen de `tests/fixtures/corridas_de_referencia/` (ver
`CORRIDAS_DE_REFERENCIA`; ningun valor es del proyecto). Las dos de T-10 ya
EXISTIAN en el repositorio: `test_t10_memoria` comprueba que son los mismos
que la guia y que los tests de T-7b/T-7c. La tercera, de T-11, trae datos
NUEVOS --los del juego de la validacion integral: el freatico a 3.0 m, los
datos de A-02, B-01 y C-01, los [S] de sitio--, y la ata al juego un test de
T-11 que exige que sus archivos sean, byte a byte, su materializacion
(corregido en las correcciones de T-11, H12: decia que ninguno era nuevo).
Ninguna de las tres es una segunda copia que pueda divergir:

  1. `perfil_guia`: la corrida de `docs/guia_perfil.md` (CSV con la
     coronacion de C-01, externos y sitio de la guia, `--luz 2.75`) a
     `--alcance perfil`. DIMENSIONA LOS CUATRO PUNTOS --- B-01 con el TW de
     0.30 m de la guia, no con el de 1.00 m de la linea base, con el que el
     perfil de la lamina lo deja sin dimension --- y alcanza las Fases 1-bis
     (caudal declarado), 2, 3, 4, 5, 6, 7, 8 y 10.
  2. `expediente_cabezal`: la corrida de punta a punta de T-7b/T-7c
     (`_correr_de_prueba` de sus tests: freatico de A-01 a 2.0 m, V5 por la
     cota de afectacion de prueba, evento extremo de prueba, relleno y
     fundacion de prueba, muro paralelo al trafico a 1.60 m del borde) a
     `--alcance expediente`, SIN las declaraciones del `conftest` de la
     suite. A-01 dimensiona y llega a la Fase 9 entera: geometria, estabilidad
     en los dos marcos y armado.

  3. `hidrologia_calculada` (T-11, ficha T10-02): el juego de la validacion
     integral de T-11 con la variante `caudal_calculado` --- A-01, A-02 y
     B-01 sin `Q_m3s`, con las cuencas y la serie SINTETICAS de T-1 --- a
     `--alcance expediente`. Lleva la Fase 1-bis CALCULADA al indice; con
     los caudales de esas cuencas los tres puntos no caben bajo la
     subrasante (resultado, `docs/validacion_integral.md` §5), y C-01
     dimensiona y llega a la Fase 9. Un test de T-11 exige que sus archivos
     sean la materializacion del juego, de modo que no son una copia que
     pueda divergir.

Las tres corren con el estado de declaraciones VACIO y lo reponen al salir
(`correr_referencia`). La razon es la de siempre: la suite declara criterios
de prueba en `conftest.py`, y un indice que dijera una cosa generado desde la
CLI y otra bajo pytest seria un documento sin referencia.

Los fundamentos que ni asi se ejercitan --- los de las ramas que estos
datos no recorren --- se listan al final del documento con su modulo
emisor, para que el hueco sea visible y no se lea como cobertura.

Que hace y que no hace este modulo
----------------------------------
- RECOGE todos los `PasoDeMemoria` del `Informe` recorriendo el grafo de
  objetos (`pasos_de_la_corrida`): los del resultado adoptado, los de cada
  escalon de la traza de MD, los de clasificacion, TW, verificaciones. No
  elige cuales publicar: el indice es de FORMULAS, y una formula que el
  pipeline evaluo en un escalon descartado sigue siendo una formula del
  calculo.
- AGRUPA por firma (fase, modulo emisor, codigo, fundamento, que, formula,
  cita, variables con su unidad, resultado, umbral): una fila por formula
  distinta, con cuantas veces la corrida la emitio y, por variable, las
  procedencias distintas que la memoria imprimio para ella.
- DERIVA el modulo emisor del codigo, no de una tabla a mano: parsea el AST
  de `src/modulos/` y atribuye cada `fundamento_id` al modulo que llama a
  `paso("<id>", ...)` con ese literal (`emisores_por_fundamento`). Es el
  mismo recurso que `variables_entrada._consumo_por_modulo`, y con el mismo
  limite: un `paso()` cuyo primer argumento no sea un literal no se ve. Hoy
  todos son literales, y un test lo exige.
- Las verificaciones SIN paso no se omiten: llegan como los
  `HuecoDeVerificacion` que `traza_punto` ya construye desde el censo
  `SIN_FUNDAMENTO` (vacio desde T-10: ninguna en estas corridas), y las
  censadas que las corridas no alcancen se listan aparte, con la misma
  ficha.
- NO HACE ARITMETICA SOBRE MAGNITUDES: los numeros no se imprimen. El indice
  es de formulas y procedencias; los valores son de la memoria.

El sello
--------
La cabecera lleva fecha, commit del arbol sobre el que se genero y el par de
la suite (`passed`/`skipped`) con su entorno, como pide la regla de sellos
de los planes (T3, I4). Los tres los pone quien regenera --`main` los toma
de `git` y de `--suite`--, y el test de sincronia los LEE del documento y
los pasa al generador, de modo que compara el cuerpo y no la fecha. El
commit es el del arbol de ORIGEN: el commit que contiene el documento es
necesariamente posterior, y no puede conocerse antes de hacerlo.

Regenerar::

    python3 -m src.indice_formulas --escribir --suite "1910 passed, 4 skipped (PyMuPDF si, Tk si)"
"""

from __future__ import annotations

import ast
import dataclasses
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

import json

from src import criterios_adoptados as _ca
from src import datos_sitio as _ds
from src import traza_punto as _tp
from src import servicio
from src.modelos import PasoDeMemoria
from src.modulos import M11_reporte as _M11
from src.normativa import registro as _registro

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
MODULOS = SRC / "modulos"
INDICE_FORMULAS = RAIZ / "docs" / "indice_formulas.md"
# Las rutas de las corridas se componen con `joinpath` y no con `/`: la
# guardia de `test_indice_formulas` lee toda division de este modulo como
# aritmetica sobre magnitudes salvo que la izquierda sea una de sus rutas.
DIR_CORRIDAS_DE_REFERENCIA = RAIZ.joinpath("tests", "fixtures",
                                           "corridas_de_referencia")


@dataclass(frozen=True)
class CorridaDeReferencia:
    """
    --- T-10 --- Una corrida con la que se genera el indice: su carpeta de
    entradas (`puntos.csv`, `externos.json` y, si los hay, `sitio.json` y
    `declaraciones.json`), el alcance y el ROTULO que dice de donde salen
    los datos. Los datos son de PRUEBA y el rotulo lo dice en el documento.
    """

    nombre: str
    alcance: str
    rotulo: str

    @property
    def carpeta(self) -> Path:
        return DIR_CORRIDAS_DE_REFERENCIA.joinpath(self.nombre)

    @property
    def csv(self) -> Path:
        return self.carpeta.joinpath("puntos.csv")

    @property
    def externos(self) -> Path:
        return self.carpeta.joinpath("externos.json")

    @property
    def sitio(self) -> Optional[Path]:
        ruta = self.carpeta.joinpath("sitio.json")
        return ruta if ruta.exists() else None

    @property
    def declaraciones(self) -> Dict[str, Any]:
        ruta = self.carpeta.joinpath("declaraciones.json")
        if not ruta.exists():
            return {}
        return json.loads(ruta.read_text(encoding="utf-8"))

    # --- T-11 --- Las dos entradas de la Fase 1-bis (`--cuencas` y
    # `--estacion`), si la carpeta las trae: con ellas un punto de Familia A
    # o B con la celda `Q_m3s` vacia calcula su caudal (ficha T10-02).
    @property
    def cuencas(self) -> Optional[Path]:
        ruta = self.carpeta.joinpath("cuencas.csv")
        return ruta if ruta.exists() else None

    @property
    def estacion(self) -> Optional[Path]:
        ruta = self.carpeta.joinpath("estacion.csv")
        return ruta if ruta.exists() else None


CORRIDAS_DE_REFERENCIA: Tuple[CorridaDeReferencia, ...] = (
    CorridaDeReferencia(
        nombre="perfil_guia", alcance="perfil",
        rotulo=("DATOS DE PRUEBA, NO DEL PROYECTO: los de la corrida de "
                "`docs/guia_perfil.md` (CSV de ejemplo con la coronacion de "
                "C-01 que la guia rellena, externos y sitio de la guia; la "
                "luz de 2.75 m que la guia pasa por `--luz` va aqui como "
                "global del JSON). Dimensiona los cuatro puntos.")),
    CorridaDeReferencia(
        nombre="expediente_cabezal", alcance="expediente",
        rotulo=("DATOS DE PRUEBA, NO DEL PROYECTO: los de la corrida de punta "
                "a punta de los tests de T-7b y T-7c (`_correr_de_prueba`): "
                "freatico, cota de afectacion, evento extremo, relleno, "
                "fundacion y sobrecarga de prueba para A-01. A-01 llega a la "
                "Fase 9 entera (geometria, estabilidad y armado).")),
    # --- T-11 --- La TERCERA corrida (decision del dueño del 2026-11-13,
    # ficha T10-02): la hidrologia CALCULADA entra al indice.
    CorridaDeReferencia(
        nombre="hidrologia_calculada", alcance="expediente",
        rotulo=("DATOS DE PRUEBA, NO DEL PROYECTO: el juego de la validacion "
                "integral de T-11 (`tests/fixtures/juego_validacion_integral.py`)"
                " con la variante `caudal_calculado`: A-01, A-02 y B-01 traen "
                "la celda `Q_m3s` vacia y la Fase 1-bis calcula su caudal con "
                "las cuencas y la serie SINTETICAS de T-1 "
                "(`tests/fixtures/hidrologia/`). Con esos caudales ninguno de "
                "los tres cabe bajo la subrasante y no dimensiona; C-01 "
                "dimensiona y llega a la Fase 9.")),
)

# El sello, en una linea que `leer_sello` reconoce. Los tres campos van
# separados por " · " y el commit entre backticks; cambiar el formato aqui
# obliga a cambiar la regex de abajo, y el test de sincronia lo diria.
_ROTULO_SELLO = "> **Sello.** Fecha de generación: "
_SELLO = re.compile(
    r"^> \*\*Sello\.\*\* Fecha de generación: (?P<fecha>\S+) · "
    r"Commit del árbol de origen: `(?P<commit>[^`]+)` · "
    r"Suite: (?P<suite>.+?)\s*$")


@dataclass(frozen=True)
class Sello:
    """Fecha, commit de origen y par de la suite con su entorno."""

    fecha: str
    commit: str
    suite: str

    def __post_init__(self) -> None:
        for campo in ("fecha", "commit", "suite"):
            if not str(getattr(self, campo)).strip():
                raise ValueError(f"Sello sin `{campo}`: la regla de sellos "
                                 "pide fecha, commit y par de la suite")

    @property
    def linea(self) -> str:
        return (f"{_ROTULO_SELLO}{self.fecha} · Commit del árbol de origen: "
                f"`{self.commit}` · Suite: {self.suite}")


def leer_sello(texto: str) -> Optional[Sello]:
    """El sello que un indice ya escrito lleva, o None si no lo tiene."""
    for linea in texto.split("\n"):
        m = _SELLO.match(linea)
        if m:
            return Sello(m.group("fecha"), m.group("commit"), m.group("suite"))
    return None


# ---------------------------------------------------------------------------
# La corrida de referencia y sus pasos
# ---------------------------------------------------------------------------

def correr_referencia(corrida: CorridaDeReferencia) -> Any:
    """
    `servicio.correr` sobre las entradas de `corrida`, con las declaraciones
    en caliente y los datos de sitio por sesion VACIOS al entrar y REPUESTOS
    al salir, clave a clave. La corrida la hace el servicio de calculo
    (`src/servicio.py`, EXT-9).

    LAS DECLARACIONES DE LA SUITE SE RETIRAN MIENTRAS DURA LA CORRIDA. La
    suite corre con criterios declarados por `conftest.py` como VALORES DE
    LA CORRIDA DE PRUEBAS (el espesor de pared del TMC y del HDPE, la
    categoria de refuerzo y la exposicion quimica), y con ellos la misma
    corrida emite pasos que el expediente, tal como esta en
    `criterios_adoptados.py`, no emite. La referencia es el expediente tal
    cual esta MAS lo que la corrida declara en su carpeta.
    """
    previas = _ca.valores_dinamicos()
    sitio_previo = _ds.datos_dinamicos()
    for clave in previas:
        _ca.quitar_valor_dinamico(clave)
    _ds.limpiar_datos_dinamicos()
    try:
        if corrida.sitio is not None:
            servicio.cargar_datos_sitio(corrida.sitio)
        for clave, valor in corrida.declaraciones.items():
            _ca.establecer_valor_dinamico(clave, valor)
        externos = servicio.cargar_datos_externos(corrida.externos, {})
        hidrologia = servicio.cargar_hidrologia(corrida.cuencas,
                                                corrida.estacion)
        return servicio.correr(corrida.csv, externos, alcance=corrida.alcance,
                               hidrologia=hidrologia)
    finally:
        for clave in _ca.valores_dinamicos():
            _ca.quitar_valor_dinamico(clave)
        for clave, valor in previas.items():
            _ca.establecer_valor_dinamico(clave, valor)
        _ds.limpiar_datos_dinamicos()
        for clave, d in sitio_previo.items():
            _ds.establecer_dato_dinamico(clave, d.dato.valor,
                                         d.dato.trazabilidad, d.fecha,
                                         origen=d.origen)


def corridas_de_referencia() -> Tuple[Tuple[CorridaDeReferencia, Any], ...]:
    """Las corridas de referencia con su informe, en su orden."""
    return tuple((c, correr_referencia(c)) for c in CORRIDAS_DE_REFERENCIA)


def pasos_de_la_corrida(informe: Any) -> Tuple[PasoDeMemoria, ...]:
    """
    TODOS los `PasoDeMemoria` que el informe contiene, recorriendo el grafo
    de objetos en orden determinista (campos de dataclass en su orden,
    secuencias en el suyo). Cada objeto se visita una vez.

    Se recorre el grafo y no una lista de atributos a mano por la misma
    razon por la que `test_memoria_sustentada._pasos_de` tuvo que crecer
    cuando S20 añadio el paso del TW: una lista escrita a mano se queda corta
    en silencio cuando un modulo empieza a emitir por un campo nuevo.
    """
    vistos: set = set()
    salida: List[PasoDeMemoria] = []

    def _visitar(objeto: Any) -> None:
        if isinstance(objeto, (str, bytes, int, float, bool, type)) \
                or objeto is None:
            return
        if id(objeto) in vistos:
            return
        vistos.add(id(objeto))
        if isinstance(objeto, PasoDeMemoria):
            salida.append(objeto)
            return
        if dataclasses.is_dataclass(objeto):
            for campo in dataclasses.fields(objeto):
                _visitar(getattr(objeto, campo.name))
        elif isinstance(objeto, dict):
            for valor in objeto.values():
                _visitar(valor)
        elif isinstance(objeto, (list, tuple, set, frozenset)):
            for elemento in objeto:
                _visitar(elemento)
        elif hasattr(objeto, "__dict__"):
            for valor in vars(objeto).values():
                _visitar(valor)

    _visitar(informe)
    return tuple(salida)


def pasos_de_las_corridas(informes: Any) -> Tuple[PasoDeMemoria, ...]:
    """
    --- T-10 --- Los pasos de varias corridas, en su orden y cada objeto una
    vez: `pasos_de_la_corrida` de cada informe, concatenados.
    """
    vistos: set = set()
    salida: List[PasoDeMemoria] = []
    for informe in informes:
        for paso in pasos_de_la_corrida(informe):
            if id(paso) not in vistos:
                vistos.add(id(paso))
                salida.append(paso)
    return tuple(salida)


# ---------------------------------------------------------------------------
# El modulo emisor, derivado del AST
# ---------------------------------------------------------------------------

def _llamadas_a_paso(arbol: ast.AST) -> Iterator[str]:
    """Los `fundamento_id` literales con que un arbol llama a `paso(...)`."""
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Call) or not nodo.args:
            continue
        funcion = nodo.func
        nombre = (funcion.id if isinstance(funcion, ast.Name)
                  else funcion.attr if isinstance(funcion, ast.Attribute)
                  else None)
        if nombre != "paso":
            continue
        primero = nodo.args[0]
        if isinstance(primero, ast.Constant) and isinstance(primero.value, str):
            yield primero.value


def emisores_por_fundamento() -> Dict[str, Tuple[str, ...]]:
    """
    {fundamento_id: (modulos de src/modulos/ que llaman a paso() con ese
    id, ...)}. Es una derivacion del codigo, no una tabla: si alguien mueve
    la emision de un paso a otro modulo, el indice lo sigue solo.
    """
    salida: Dict[str, List[str]] = {}
    for ruta in sorted(MODULOS.glob("*.py")):
        arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=ruta.name)
        for fundamento_id in _llamadas_a_paso(arbol):
            modulos = salida.setdefault(fundamento_id, [])
            if ruta.stem not in modulos:
                modulos.append(ruta.stem)
    return {k: tuple(v) for k, v in salida.items()}


def menciones_del_fundamento() -> Dict[str, Tuple[str, ...]]:
    """
    {fundamento_id: (modulos de src/ que escriben el id como literal, ...)},
    fuera de `normativa/fundamentos.py` y sin distinguir la puerta. Sirve
    para decir de un fundamento SIN `paso()` por donde entra al calculo:
    `F5.V7_FILA` llega por `eleccion()` desde M5 y `F3.D_MIN` por el bloque
    fijo de umbrales de `constantes_normativas`. Es la misma derivacion que
    `emisores_por_fundamento`, con la red mas ancha.
    """
    salida: Dict[str, List[str]] = {}
    for ruta in sorted(SRC.rglob("*.py")):
        if "__pycache__" in ruta.parts or ruta.name == "fundamentos.py":
            continue
        arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=ruta.name)
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str) \
                    and re.fullmatch(r"F\d+\.[A-Za-z0-9_]+", nodo.value):
                modulos = salida.setdefault(nodo.value, [])
                if ruta.stem not in modulos:
                    modulos.append(ruta.stem)
    return {k: tuple(v) for k, v in salida.items()}


def emisor_de(paso: PasoDeMemoria,
              emisores: Dict[str, Tuple[str, ...]]) -> str:
    """El modulo emisor del paso como texto; declara cuando no se localiza."""
    modulos = emisores.get(paso.fundamento_id)
    if not modulos:
        return "*(emisor no localizado: el `paso()` no lleva el id como literal)*"
    return ", ".join(f"`{m}`" for m in modulos)


# ---------------------------------------------------------------------------
# Las filas
# ---------------------------------------------------------------------------

@dataclass
class FilaDelIndice:
    """Una formula distinta de la corrida, con cuantas veces se emitio."""

    fase: str
    emisor: str
    codigo: str
    fundamento_id: str
    que: str
    formula: str
    formula_cita_id: str
    variables: Tuple[Tuple[str, str], ...]          # (simbolo, unidad)
    resultado: Tuple[str, str]                      # (simbolo, unidad)
    umbral: Optional[Tuple[str, str, str, str]]     # descripcion, unidad, cita, criterio
    procedencias: Dict[str, List[str]] = dataclasses.field(default_factory=dict)
    emisiones: int = 0
    # Posicion de la PRIMERA emision en el recorrido del informe: es lo que
    # conserva, dentro de cada fase, el orden en que la memoria imprime los
    # pasos (seccion antes que Manning, entrada antes que salida), en vez del
    # orden alfabetico del id.
    orden: int = 0

    @property
    def firma(self) -> tuple:
        return (self.fase, self.emisor, self.codigo, self.fundamento_id,
                self.que, self.formula, self.formula_cita_id, self.variables,
                self.resultado, self.umbral)


def _numero_de_fase(fase: str) -> int:
    m = re.search(r"\d+", fase)
    return int(m.group(0)) if m else 0


def _clave_de_orden(fila: FilaDelIndice) -> tuple:
    return (_numero_de_fase(fila.fase), fila.fase, fila.orden)


# --- T-10 --- Un modulo puede escribir VALORES dentro de una procedencia
# («D' = (D + yn)/2, con D = 0.900 m e yn = 0.627 m...», paso 6.5). En la
# memoria es correcto; en el indice no, que es de formulas y procedencias y
# no de numeros (`test_el_indice_no_imprime_los_valores_de_la_corrida`).
# Hasta T-10 la corrida de referencia no llegaba a ningun paso asi, porque no
# dimensionaba. El indice ENMASCARA el valor de cada «simbolo = numero» de
# una procedencia: no hace aritmetica, sustituye texto, y las procedencias
# que solo diferian en el numero colapsan en una.
_VALOR_EN_PROCEDENCIA = re.compile(r"(=\s*)[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?")
# Y todo numero seguido de una UNIDAD (un numeral --- «num. 2.2.4», «Tabla
# 10.1 de» --- no lleva unidad detras y no se toca). --- T-11 --- `m2`: la
# tercera corrida de referencia llega a la procedencia de la cuña sobre el
# talon del cabezal del marco («(0.290 m2)»), y sin la unidad el «0.290 m»
# del resultado de otro paso quedaba impreso dentro de «0.290 m2».
_MAGNITUD_EN_PROCEDENCIA = re.compile(
    r"(?<![\w.])[-+]?\d+(?:\.\d+)?(?=\s*(?:m3/s|m/s2|m/s|m/m|msnm|"
    r"kN·m/m|kN/m|kN|kPa|MPa|mm2/m|mm|m2|m|%)(?![\w/²³]))")


def _sin_valores(texto: str) -> str:
    texto = _VALOR_EN_PROCEDENCIA.sub(r"\1…", texto)
    return _MAGNITUD_EN_PROCEDENCIA.sub("…", texto)


def filas_del_indice(pasos: Tuple[PasoDeMemoria, ...],
                     emisores: Dict[str, Tuple[str, ...]]
                     ) -> List[FilaDelIndice]:
    """Agrupa los pasos por firma y acumula procedencias y emisiones."""
    por_firma: Dict[tuple, FilaDelIndice] = {}
    for orden, paso in enumerate(pasos):
        u = paso.umbral
        # --- T-10 --- la descripcion del umbral sin los valores que un
        # modulo escribe dentro (ver `_sin_valores`): agrupa por formula.
        umbral = (None if u is None else
                  (_sin_valores(u.descripcion), u.unidad, u.cita_id,
                   u.criterio_aplicado or ""))
        fila = FilaDelIndice(
            fase=paso.fase, emisor=emisor_de(paso, emisores),
            codigo=paso.codigo, fundamento_id=paso.fundamento_id,
            que=paso.que, formula=paso.formula,
            formula_cita_id=paso.formula_cita_id,
            variables=tuple((m.simbolo, m.unidad) for m in paso.sustitucion),
            resultado=(paso.resultado.simbolo, paso.resultado.unidad),
            umbral=umbral, orden=orden)
        fila = por_firma.setdefault(fila.firma, fila)
        fila.emisiones += 1
        for m in paso.sustitucion:
            textos = fila.procedencias.setdefault(m.simbolo, [])
            procedencia = _sin_valores(m.procedencia)
            if procedencia not in textos:
                textos.append(procedencia)
    return sorted(por_firma.values(), key=_clave_de_orden)


# ---------------------------------------------------------------------------
# El documento
# ---------------------------------------------------------------------------

def _celda(texto: str) -> str:
    """Texto plano dentro de una celda de tabla Markdown."""
    return (str(texto).replace("\\", "\\\\").replace("|", "\\|")
            .replace("\n", " ").strip())


def _unidad(unidad: str) -> str:
    return f"[{unidad}]" if unidad else "[adimensional]"


def _etiqueta_del_criterio(clave: str) -> str:
    declarado = _ca.CRITERIOS.get(clave)
    return f"[{declarado.etiqueta}] " if declarado is not None else ""


def _texto_cita(reg: Any, cita_id: str) -> str:
    return reg.cita(cita_id).como_texto() if cita_id else ""


def _variables(fila: FilaDelIndice) -> str:
    partes = []
    for simbolo, unidad in fila.variables:
        textos = fila.procedencias.get(simbolo, [])
        procedencia = " ‖ ".join(f"«{_celda(t)}»" for t in textos)
        partes.append(f"**{_celda(simbolo)}** {_unidad(unidad)} ← {procedencia}")
    return "<br>".join(partes) if partes else "*(sin sustitución)*"


def _umbral(reg: Any, fila: FilaDelIndice) -> str:
    if fila.umbral is None:
        return "—"
    descripcion, unidad, cita_id, criterio = fila.umbral
    texto = f"{_celda(descripcion)} {_unidad(unidad)} · {_celda(_texto_cita(reg, cita_id))}"
    if criterio:
        texto += f" · criterio {_etiqueta_del_criterio(criterio)}`{criterio}`"
    return texto


def _resumen_de_la_corrida(corrida: CorridaDeReferencia,
                           informe: Any) -> List[str]:
    L: List[str] = []
    carpeta = corrida.carpeta.relative_to(RAIZ)
    L.append(f"### Corrida `{corrida.nombre}`")
    L.append("")
    L.append(f"> {corrida.rotulo}")
    L.append("")
    entradas = [f"`{carpeta.joinpath('puntos.csv')}`",
                f"datos externos `{carpeta.joinpath('externos.json')}`"]
    if corrida.sitio is not None:
        entradas.append(f"datos de sitio `{carpeta.joinpath('sitio.json')}`")
    L.append(f"- Entradas: {' · '.join(entradas)} · alcance: "
             f"`{informe.alcance}`.")
    if corrida.declaraciones:
        L.append("- Criterios declarados SOLO para esta corrida: "
                 + ", ".join(f"`{c}`" for c in corrida.declaraciones) + ".")
    else:
        L.append("- Criterios declarados para esta corrida: ninguno (los del "
                 "archivo).")
    L.append(f"- Puntos: {len(informe.puntos)} · dimensionados: "
             f"{informe.dimensionados} ("
             + ", ".join(p.punto.id for p in informe.puntos if p.dimensionado)
             + ").")
    L.append("- Etapas que la corrida no completó (la razón está en el "
             "informe; aquí sólo se nombra la etapa):")
    bloqueos = list(informe.bloqueos())
    if not bloqueos:
        L.append("  - *(ninguna)*")
    for id_punto, b in bloqueos:
        quien = id_punto or "proyecto"
        L.append(f"  - {quien}: {_celda(b.fase)} → {_celda(b.etapa)} "
                 f"(`{b.tipo}`).")
    L.append("")
    return L


def _huecos(informes: Any) -> Tuple[List[Any], List[Any]]:
    """
    (huecos que la corrida emitio, huecos censados que no alcanzo). Los
    primeros son los `HuecoDeVerificacion` de `traza_punto`, exactamente los
    que la GUI muestra; los segundos se construyen con la misma ficha del
    censo, para que el indice no calle las verificaciones que la corrida no
    llego a evaluar.
    """
    emitidos: Dict[str, Any] = {}
    con_paso: set = set()
    for informe_punto in (p for informe in informes for p in informe.puntos):
        for seccion in _tp.traza_del_punto(informe_punto).secciones:
            for entrada in seccion.entradas:
                if isinstance(entrada, _tp.HuecoDeVerificacion):
                    emitidos.setdefault(entrada.codigo, entrada)
                else:
                    con_paso.add(entrada.codigo)
    censo = _M11.sin_fundamento_por_codigo()
    no_alcanzados = [_tp.hueco_censado(codigo) for codigo in sorted(censo)
                     if codigo not in emitidos and codigo not in con_paso]
    return list(emitidos.values()), no_alcanzados


def _fundamentos_no_ejercitados(reg: Any, pasos: Tuple[PasoDeMemoria, ...],
                                emisores: Dict[str, Tuple[str, ...]]
                                ) -> List[str]:
    emitidos = {p.fundamento_id for p in pasos}
    menciones = menciones_del_fundamento()
    L: List[str] = []
    for f in sorted(reg.fundamentos, key=lambda x: x.id):
        if f.id in emitidos:
            continue
        modulos = emisores.get(f.id)
        if modulos:
            emisor = ", ".join(f"`{m}`" for m in modulos)
        elif menciones.get(f.id):
            emisor = ("sin `paso()`; entra por otra puerta desde "
                      + ", ".join(f"`{m}`" for m in menciones[f.id]))
        else:
            emisor = "sin `paso()` y sin mención fuera del registro"
        L.append(f"| `{f.id}` | {_celda(f.fase)} | {_celda(f.que_paso)} | "
                 f"{emisor} |")
    return L


def indice_de_formulas(corridas: Any, sello: Sello) -> str:
    """
    El indice, generado entero desde los pasos de las `corridas` de
    referencia: pares `(CorridaDeReferencia, Informe)`.

    Ninguna fila lleva un numero de linea ni un valor: se ancla a
    `fundamento_id` + `codigo` + formula, que solo cambian si alguien cambia
    el calculo a proposito, y entonces el test de sincronia lo dice.
    """
    reg = _registro.construir()
    emisores = emisores_por_fundamento()
    informes = [informe for _corrida, informe in corridas]
    pasos = pasos_de_las_corridas(informes)
    filas = filas_del_indice(pasos, emisores)

    L: List[str] = []
    A = L.append
    A("# Índice de fórmulas de la corrida de referencia")
    A("")
    A("> **Este documento se GENERA.** No se edita a mano: lo produce")
    A("> `src/indice_formulas.py` desde los `PasoDeMemoria` que emite una")
    A("> corrida de referencia, y el test")
    A("> `test_el_indice_de_formulas_esta_sincronizado` lo regenera y compara.")
    A("> Si difieren, lo que hay que corregir es el cálculo o el registro, no")
    A("> este archivo.")
    A(">")
    A(sello.linea)
    A(">")
    A("> **Qué es una fila.** Una fórmula distinta que la corrida evaluó:")
    A("> fase, módulo emisor (derivado del AST de `src/modulos/`, no de una")
    A("> tabla), código del paso en la memoria, fundamento, fórmula con su")
    A("> cita (numeral + página, vía `Cita.como_texto`), variables con la")
    A("> procedencia que la memoria imprime para cada una, resultado y umbral.")
    A("> Los VALORES no se imprimen: son de la memoria, no del índice. La")
    A("> columna «Emisiones» dice cuántas veces la corrida emitió esa fórmula")
    A("> (una por punto y por escalón de MD que la evaluó). Cuando la misma")
    A("> variable llegó con más de una procedencia, se listan todas,")
    A("> separadas por «‖».")
    A("")
    A("## 1. Las corridas de referencia")
    A("")
    A("Tres corridas con DATOS DE PRUEBA que ya estaban en el repositorio")
    A("(`tests/fixtures/corridas_de_referencia/`, ver `CORRIDAS_DE_REFERENCIA`")
    A("en `src/indice_formulas.py`): la de la guía de perfil, que dimensiona")
    A("los cuatro puntos; la de punta a punta de T-7b/T-7c, que lleva a A-01")
    A("hasta la Fase 9; y la de la validación integral de T-11 con el caudal")
    A("calculado, que lleva la Fase 1-bis al índice. Ningún valor de entrada")
    A("es del proyecto.")
    A("")
    for corrida, informe in corridas:
        L.extend(_resumen_de_la_corrida(corrida, informe))
    A(f"Pasos emitidos: **{len(pasos)}** · fórmulas distintas: "
      f"**{len(filas)}** · fundamentos ejercitados: "
      f"**{len({p.fundamento_id for p in pasos})}** de "
      f"{len(reg.fundamentos)}.")
    A("")

    A("## 2. Índice")
    A("")
    A("| Fase | Módulo emisor | Código | Paso | Fundamento | Fórmula | "
      "Cita de la fórmula | Variables (símbolo [unidad] ← procedencia) | "
      "Resultado | Umbral | Emisiones |")
    A("|---|---|---|---|---|---|---|---|---|---|---|")
    for fila in filas:
        f = reg.fundamento(fila.fundamento_id)
        fundamento = f"`{fila.fundamento_id}` ({f.verbo.value})"
        cita = (_celda(_texto_cita(reg, fila.formula_cita_id))
                if fila.formula_cita_id else
                "*(sin `formula_cita_id`; el fundamento cita: "
                + ", ".join(f"`{c}`" for c in f.citas) + ")*")
        resultado = (f"**{_celda(fila.resultado[0])}** "
                     f"{_unidad(fila.resultado[1])}")
        A(f"| {_celda(fila.fase)} | {fila.emisor} | `{_celda(fila.codigo)}` "
          f"| {_celda(fila.que)} | {fundamento} | `{_celda(fila.formula)}` "
          f"| {cita} | {_variables(fila)} | {resultado} "
          f"| {_umbral(reg, fila)} | {fila.emisiones} |")
    A("")

    A("## 3. Verificaciones sin paso: los huecos declarados")
    A("")
    A("Una verificación sin `PasoDeMemoria` no se omite ni se inventa: llega")
    A("como el `HuecoDeVerificacion` que `traza_punto` construye desde el")
    A("censo `normativa.fundamentos.SIN_FUNDAMENTO`, con la razón de por qué")
    A("no puede tener fundamento normativo hoy y qué haría falta para traerlo.")
    A("")
    emitidos, no_alcanzados = _huecos(informes)
    A("### 3.1 Huecos que la corrida emitió")
    A("")
    if not emitidos:
        A("*(ninguno)*")
    for hueco in emitidos:
        A(f"- **`{hueco.codigo}`** — {hueco.titulo}.")
        A(f"  - {_tp.ROTULO_HUECO_POR_QUE}: {hueco.por_que}")
        A(f"  - {_tp.ROTULO_HUECO_FALTA}: {hueco.que_haria_falta}")
    A("")
    A("### 3.2 Huecos censados que la corrida no alcanzó a evaluar")
    A("")
    A("Las corridas no llegan a ellos (ver §1). Se listan con")
    A("la misma ficha para que el censo entero sea visible desde aquí.")
    A("")
    if not no_alcanzados:
        A("*(ninguno)*")
    for hueco in no_alcanzados:
        A(f"- **`{hueco.codigo}`** — {hueco.titulo}.")
        A(f"  - {_tp.ROTULO_HUECO_POR_QUE}: {hueco.por_que}")
        A(f"  - {_tp.ROTULO_HUECO_FALTA}: {hueco.que_haria_falta}")
    A("")

    A("## 4. Fundamentos que la corrida de referencia no ejercita")
    A("")
    A("Declarados en `normativa/fundamentos.py` y sin paso en las corridas")
    A("de referencia, porque sus datos no recorren esa rama (§1). Sus")
    A("fórmulas no están en el §2 y este cuadro es lo que impide leer el")
    A("índice como cobertura.")
    A("")
    A("| Fundamento | Fase | Paso | Módulo emisor |")
    A("|---|---|---|---|")
    L.extend(_fundamentos_no_ejercitados(reg, pasos, emisores))
    A("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def _commit_de_origen() -> str:
    """El SHA corto de HEAD, con marca si el arbol tiene cambios sin commit."""
    import subprocess

    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ,
                         capture_output=True, text=True, check=True).stdout.strip()
    # El propio indice no cuenta como cambio: regenerarlo lo modifica
    # siempre, y la marca es para lo DEMAS que el arbol tenga sin commit.
    sucio = subprocess.run(
        ["git", "status", "--porcelain", "--", ".",
         # Los cuatro documentos generados quedan fuera del chequeo, no solo
         # este: regenerarlos en fila no puede ensuciar el sello del siguiente
         # (misma regla, y misma razon, que en normativa.manifiesto).
         f":!{INDICE_FORMULAS.relative_to(RAIZ)}",
         ":!docs/manifiesto_citas.md",
         ":!docs/manifiesto_registro_normativo.md",
         ":!docs/trazabilidad.csv"],
        cwd=RAIZ, capture_output=True, text=True, check=True).stdout
    return sha + ("+cambios-sin-commit" if sucio.strip() else "")


def main(argv: List[str]) -> int:
    """
    `python3 -m src.indice_formulas [--escribir] [--suite "N passed, M skipped (entorno)"]`

    Sin `--escribir` solo informa si el documento esta sincronizado. Con
    `--escribir` exige `--suite`: el par de la suite es parte del sello y
    no se puede inventar.
    """
    import datetime as _dt

    escribir = "--escribir" in argv
    suite = None
    if "--suite" in argv:
        suite = argv[argv.index("--suite") + 1]
    if escribir and not suite:
        print("--escribir exige --suite \"N passed, M skipped (entorno)\": "
              "el par de la suite es parte del sello")
        return 2
    corridas = corridas_de_referencia()
    if escribir:
        sello = Sello(fecha=_dt.date.today().isoformat(),
                      commit=_commit_de_origen(), suite=suite)
        INDICE_FORMULAS.write_text(indice_de_formulas(corridas, sello),
                                   encoding="utf-8")
        print(f"{INDICE_FORMULAS.relative_to(RAIZ)}: escrito con sello "
              f"{sello.fecha} · {sello.commit} · {sello.suite}")
        return 0
    if not INDICE_FORMULAS.exists():
        print(f"{INDICE_FORMULAS.relative_to(RAIZ)}: no existe todavia")
        return 1
    texto = INDICE_FORMULAS.read_text(encoding="utf-8")
    sello = leer_sello(texto)
    if sello is None:
        print("el documento no lleva sello legible")
        return 1
    en_sincronia = indice_de_formulas(corridas, sello) == texto
    print(f"{INDICE_FORMULAS.relative_to(RAIZ)}: "
          f"{'sincronizado' if en_sincronia else 'DESINCRONIZADO'} "
          f"(sello {sello.fecha} · {sello.commit})")
    return 0 if en_sincronia else 1


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
