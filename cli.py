"""
cli.py
======
Orquestador de linea de comandos del expediente: corre el pipeline completo
sobre el CSV de puntos criticos de Sec. 1.2 y vuelca el resultado a stdout mas
un JSON.

    M0 -> M1 -> MD (M2/M3/M4/M5) -> M6 -> M7 -> M8 -> M9 -> M10

Uso
---
    python cli.py tests/ejemplo_puntos.csv --luz 2.0 --json salida.json

Que reporta por punto
---------------------
    material y diametro adoptados (Fase 4)
    control gobernante (entrada / salida) y la hidraulica que lo sostiene
    verificaciones con su numeral: la luz de Sec. 2.1, V1-V9 de la Fase 5 y
        G1/G2 de Sec. 7.B, cada una con valor obtenido, admisible y el
        criterio adoptado del que sale el umbral
    los criterios pendientes que bloquearon una etapa, con el concepto y la
        fuente que los resolveria

Datos que NO estan en el CSV
----------------------------
Cinco magnitudes que el pipeline necesita no son columnas de Sec. 1.2 y
ningun numeral las deduce. Entran declaradas por quien corre el calculo -- por
bandera o por el JSON de `--datos-externos` -- y el informe registra de donde
salio cada una, igual que MD recibe L y TW en vez de derivarlos:

    luz_m           m     luz del cruce, de la topografia o del QGIS. Sin ella
                          no se puede aplicar el umbral binario de Sec. 2.1 y
                          el punto no se disena: un cruce de 6 m o mas es
                          PUENTE y esta fuera de alcance (Sec. 3.1).
    TW_m            m     tirante en el receptor sobre el fondo de la SALIDA.
                          Si no se declara se pide a `criterios_adoptados`
                          ('TW_receptor'), que hoy es un vacio.
    longitud_m      m     longitud del conducto. Si no se declara la calcula
                          M7 (7.B), que exige 'talud_terraplen'.
    Q_m3s, S_conducto     caudal y pendiente cuando no son los de la columna:
                          Sec. 2.3 dice que el caudal de la Familia B es el
                          del drenaje longitudinal y el de la C el del canal.
    L_hidraulico_m  m     longitud a la que la cuneta agota su capacidad, para
                          la Fase 10 (Familia B). Sec. 10 describe el
                          procedimiento pero no fija la seccion de la cuneta.
    categoria_tr          fila de la Tabla N 02 del punto ('quebrada_importante'
                          o 'quebrada_menor'). Sec. 2.2 la declara cauce por
                          cauce y el Manual no da un umbral para deducirla; sin
                          ella la Familia A se detiene en
                          'umbral_area_quebrada_importante_ha'.

Ninguna de las cinco tiene valor por defecto. Sin declararla, la etapa que la
necesita queda bloqueada y el informe lo dice; no se sustituye por un numero
plausible.

Que hace con un criterio pendiente
----------------------------------
Lo registra como bloqueo de la etapa donde salto -- con clave, concepto y
fuente -- sigue con las etapas que no dependen de el, y al final los agrupa en
un bloque aparte con las fases y los puntos que bloquearon (Sec. 0.7). Nunca
sustituye por un defecto ni convierte el vacio en un incumplimiento: un
criterio sin valor es un calculo que todavia no se puede completar, no una
verificacion que falla.

Como declarar uno sin tocar el archivo: `--declarar CLAVE=VALOR`, repetible.
Es la MISMA via que la pestana "Criterios" de la GUI --
`criterios_adoptados.establecer_valor_dinamico`, que somete el valor a la
guardia del archivo -- y vale solo para esa corrida:
`criterios_adoptados.py` no se modifica. La memoria imprime esos valores con
su procedencia ("declarado para esta corrida, no en archivo") y los lista
aparte, para que nadie los lea como transcritos de una norma.

Misma via NO es misma politica, y conviene saberlo: la GUI solo ofrece el
boton para los criterios VACIOS (y para retirar lo que ella misma declaro),
mientras que `--declarar` acepta cualquier clave declarada, incluidas las que
ya traen valor en el archivo. Es deliberado -- una corrida de sensibilidad
consiste justamente en mover un valor que ya existe -- y no abre un agujero:
el valor pasa por la misma guardia, la memoria lo marca como declarado para
la corrida y dice ademas QUE valor trae el archivo, de modo que sustituir un
valor transcrito queda a la vista en el entregable. Lo que no se puede por
ninguna de las dos vias es declarar `None` -- ni la cadena vacia
(`--declarar CLAVE=` se rechaza): retirar una declaracion es otra operacion, y
aqui consiste en no pasar la bandera.

Solo se atrapa `ErrorProyecto` (criterio pendiente, dato faltante, dato
invalido, diseno no factible): es un problema del expediente y va al informe.
Un fallo de programa (ImportError, AssertionError) se propaga con su traza,
porque significa que un modulo esta incompleto.

Codigos de salida
-----------------
    0   el expediente cerro AL ALCANCE DECLARADO (--alcance, por defecto
        "expediente"): todos los puntos dimensionados, sin bloqueos y con
        todas las verificaciones cumpliendo. Lo diferido por alcance no
        cuenta como bloqueo, pero queda impreso con su fundamento
    1   el expediente esta incompleto: hay bloqueos, puntos sin dimensionar o
        verificaciones incumplidas. Es el resultado normal mientras el
        Tablero 3 siga abierto
    2   no se pudo correr: el CSV o el JSON de datos externos no se pueden
        leer o no tienen la forma esperada
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import sys
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "src"
for _ruta in (RAIZ, SRC):
    if str(_ruta) not in sys.path:
        sys.path.insert(0, str(_ruta))

import criterios_adoptados as ca                                    # noqa: E402
import datos_sitio as ds                                            # noqa: E402
from constantes_normativas import CUANTIA_MIN_MURO, RECUBRIMIENTO   # noqa: E402
from modelos import (Clasificacion, CompatibilidadGeometrica,       # noqa: E402
                     CriterioPendienteError, DatoFaltanteError,
                     DatoInvalidoError, DisenoNoFactibleError,
                     ErrorProyecto, Espaciamiento, Familia, PasoDiseno,
                     ProteccionSalida, PuntoCritico, ResultadoPunto,
                     Verificacion)
from modulos.M0_carga import cargar_puntos                          # noqa: E402
from modulos.M1_clasificacion import clasificar, exigir_alcance     # noqa: E402
from modulos.M6_proteccion import proteccion_salida                 # noqa: E402
from modulos.M7_geometria import (compatibilidad_geometrica,        # noqa: E402
                                  longitud_conducto)
# `cota_clave` vive en M5 y no en M7: la comparten V7 y el tamizado de 7.A, y
# tenerla en dos sitios fue el defecto MAT-D4 (las dos copias la calculaban
# sin espesor de pared).
from modulos.M5_verificaciones import cota_clave                    # noqa: E402
from modulos.M8_estructural import (cama_apoyo_relleno_lateral,     # noqa: E402
                                    seleccionar_clase_calibre,
                                    verificacion_diferida_estructural)
from modulos.M9_cabezal import (aviso_ambiente_corrosivo,           # noqa: E402
                                cadena_sismica,
                                condicion_normativa_cabezal,
                                cuantia_minima, geometria_adoptada,
                                k_ae_del_proyecto,
                                recubrimiento_de_diseno)
from modulos.M10_espaciamiento import espaciamiento_alivio          # noqa: E402
# La agregacion de criterios bloqueantes y el armado de la memoria son de la
# Fase 11: viven en M11 y aqui solo se usan. `CriterioBloqueante` y
# `criterios_bloqueantes` se reexportan porque el JSON y el volcado de texto de
# esta CLI los siguen publicando con el mismo nombre.
from modulos.M11_reporte import (CriterioBloqueante,                # noqa: E402,F401
                                 DIR_PLANTILLAS, NOMBRE_PLANTILLA,
                                 NOMBRE_PLANTILLA_PERFIL,
                                 criterios_bloqueantes,
                                 exportar_csv, exportar_html, exportar_pdf)
from modulos import M5_verificaciones as M5                        # noqa: E402
from modulos.MD import disenar_punto                                # noqa: E402

# Alcance de la corrida. Es una bifurcacion declarada, no una poda: con
# "expediente" (el defecto) todo corre exactamente como siempre; con "perfil"
# V5 y V8 se INTENTAN pero su fallo se difiere al expediente en vez de frenar
# el dimensionamiento, y las Fases 8 y 9 no se ejecutan. Nada de lo diferido
# se pierde: queda registrado como Bloqueo con `diferido_por_alcance=True`,
# se imprime con su fundamento, y deja de contar solo para `Informe.cerrado`.
# Son rotulos de la corrida, no valores de proyecto.
ALCANCE_PERFIL = "perfil"
ALCANCE_EXPEDIENTE = "expediente"

# Etiquetas de fase. Son rotulos del informe, no valores de proyecto: cada uno
# nombra el modulo y la seccion de la hoja de ruta que ejecuta esa etapa.
FASE_CARGA = "Fase 1 - Carga y validacion (M0)"
FASE_CLASIFICACION = "Fase 2 - Clasificacion y TR (M1)"
FASE_DISENO = "Fases 3-5 - Diseno hidraulico (MD: M2/M3/M4/M5)"
FASE_PROTECCION = "Fase 6 - Proteccion de salida (M6)"
FASE_GEOMETRIA = "Fase 7 - Compatibilidad geometrica (M7)"
FASE_ESTRUCTURAL = "Fase 8 - Estructural del conducto (M8)"
FASE_CABEZAL = "Fase 9 - Cabezal y aletas (M9)"
FASE_ALIVIO = "Fase 10 - Espaciamiento de alivio (M10)"

CRITERIO_TW = "TW_receptor"

# Claves admitidas en --datos-externos. Cada una es un dato de entrada que
# Sec. 1.2 no trae como columna (ver el docstring del modulo). Las de texto van
# aparte porque no se validan como numero.
CLAVES_TEXTO: Tuple[str, ...] = ("categoria_tr",)
CLAVES_EXTERNAS: Tuple[str, ...] = ("luz_m", "TW_m", "longitud_m", "Q_m3s",
                                    "S_conducto", "L_hidraulico_m") + CLAVES_TEXTO

# La geometria del cabezal es del proyecto entero, no de un punto: Sec. 9 no
# dimensiona un cabezal por punto y el criterio que la declara es uno solo.
NOTA_ESTABILIDAD_CABEZAL = (
    "Las verificaciones E1-E5 de Sec. 9.3 no las ensambla esta CLI: "
    "M9.verificar_estabilidad recibe las demandas YA calculadas (capacidad "
    "portante, momentos y fuerzas) y elegir el plano de empuje o los factores "
    "de combinacion aqui seria decidir por el proyectista. La CLI corre las "
    "piezas de Fase 9 que se sostienen solas: cadena sismica (9.2), K_AE, "
    "recubrimientos (9.4) y cuantias minimas de referencia."
)

# Presentacion. Ninguno entra en un calculo: mueven columnas de texto.
ANCHO = 78
SANGRIA = "  "
MARCA_CUMPLE = "[OK]"
MARCA_INCUMPLE = "[NO]"


# ===========================================================================
# Datos declarados que no vienen del CSV
# ===========================================================================

@dataclass(frozen=True)
class DatoDeclarado:
    """
    Un dato de entrada que no es columna de Sec. 1.2, con su procedencia.

    `origen` viaja siempre: la memoria tiene que poder decir si la luz de un
    punto salio del JSON del expediente, de una bandera de la corrida o -- en
    el caso de TW -- de un criterio adoptado.
    """

    nombre: str
    valor: Any
    origen: str


class DatosExternos:
    """
    Los datos de `--datos-externos` y de las banderas, resueltos por punto.

    Un valor por punto pisa al global, y el global pisa a nada: si no hay
    ninguno, `dato()` devuelve None y la etapa que lo necesitaba se bloquea
    con el motivo escrito. No hay defaults.
    """

    def __init__(self, globales: Dict[str, DatoDeclarado],
                 por_punto: Dict[str, Dict[str, DatoDeclarado]]) -> None:
        self.globales = globales
        self.por_punto = por_punto

    def dato(self, id_punto: str, clave: str) -> Optional[DatoDeclarado]:
        propio = self.por_punto.get(id_punto, {}).get(clave)
        return propio if propio is not None else self.globales.get(clave)

    def valor(self, id_punto: str, clave: str) -> Optional[Any]:
        dato = self.dato(id_punto, clave)
        return None if dato is None else dato.valor

    def ids_declarados(self) -> Tuple[str, ...]:
        return tuple(sorted(self.por_punto))


def _dato_externo(clave: str, bruto: Any, origen: str) -> DatoDeclarado:
    """
    Valida un dato declarado segun su clave. Los de texto se comprueban solo
    como texto no vacio: el juego de valores admitidos lo conoce el modulo que
    los consume (M1 valida `categoria_tr` contra la Tabla N 02) y repetirlo
    aqui seria una segunda fuente de verdad.
    """
    if clave in CLAVES_TEXTO:
        if not isinstance(bruto, str) or not bruto.strip():
            raise DatoInvalidoError(
                clave, valor=bruto,
                motivo=f"tiene que ser texto no vacio; origen: {origen}")
        return DatoDeclarado(nombre=clave, valor=bruto.strip(), origen=origen)
    return _numero_externo(clave, bruto, origen)


def _numero_externo(clave: str, bruto: Any, origen: str) -> DatoDeclarado:
    """Un dato externo numerico tiene que ser finito y positivo, en SI."""
    try:
        valor = float(bruto)
    except (TypeError, ValueError):
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"no es un numero (SI, metros o m3/s); origen: {origen}",
        ) from None
    if not math.isfinite(valor):
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"no es finito; origen: {origen}",
        )
    # TW = 0 es salida libre y es un valor legitimo (ver MD.disenar_punto);
    # el resto de las claves son longitudes o caudales estrictamente positivos.
    if valor < 0 or (valor == 0 and clave != "TW_m"):
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"tiene que ser positivo (TW admite 0 = salida libre); "
                   f"origen: {origen}",
        )
    return DatoDeclarado(nombre=clave, valor=valor, origen=origen)


def cargar_datos_externos(ruta: Optional[Path],
                          banderas: Dict[str, Any]) -> DatosExternos:
    """
    Lee el JSON de datos externos y le superpone las banderas de la corrida.

    Forma del archivo -- las dos secciones son opcionales:

        {
          "globales": {"luz_m": 2.0, "TW_m": 0.0},
          "puntos": {"A-01": {"luz_m": 3.5, "longitud_m": 12.4}}
        }

    Una clave desconocida es `DatoInvalidoError` y no un aviso: un 'luz'
    escrito 'luz_m2' pasaria inadvertido y el punto quedaria sin luz por un
    error de tipeo, no por un dato que falta de verdad.
    """
    globales: Dict[str, DatoDeclarado] = {}
    por_punto: Dict[str, Dict[str, DatoDeclarado]] = {}

    if ruta is not None:
        crudo = json.loads(ruta.read_text(encoding="utf-8-sig"))
        if not isinstance(crudo, dict):
            raise DatoInvalidoError(
                "datos_externos", valor=type(crudo).__name__,
                motivo=f"'{ruta.name}' tiene que ser un objeto JSON con las "
                       "secciones 'globales' y/o 'puntos'",
            )
        sobran = [k for k in crudo if k not in ("globales", "puntos")]
        if sobran:
            raise DatoInvalidoError(
                "datos_externos", valor=", ".join(sobran),
                motivo=f"seccion no reconocida en '{ruta.name}': solo existen "
                       "'globales' y 'puntos'",
            )
        for clave, bruto in (crudo.get("globales") or {}).items():
            _exige_clave(clave, f"globales de '{ruta.name}'")
            globales[clave] = _dato_externo(clave, bruto,
                                            "datos externos (globales)")
        for id_punto, campos in (crudo.get("puntos") or {}).items():
            if not isinstance(campos, dict):
                raise DatoInvalidoError(
                    "datos_externos", valor=id_punto,
                    motivo="cada punto lleva un objeto con sus datos declarados",
                )
            for clave, bruto in campos.items():
                _exige_clave(clave, f"punto '{id_punto}' de '{ruta.name}'")
                por_punto.setdefault(id_punto, {})[clave] = _dato_externo(
                    clave, bruto, f"datos externos (punto {id_punto})")

    # Las banderas se aplican al final: una bandera de la corrida pisa al
    # global del archivo, que es lo que espera quien tantea un valor.
    for clave, bruto in banderas.items():
        if bruto is None:
            continue
        globales[clave] = _dato_externo(clave, bruto,
                                        f"linea de comandos (--{clave})")
    return DatosExternos(globales, por_punto)


def _exige_clave(clave: str, donde: str) -> None:
    if clave not in CLAVES_EXTERNAS:
        raise DatoInvalidoError(
            "datos_externos", valor=clave,
            motivo=f"clave no reconocida en {donde}. Las admitidas son: "
                   + ", ".join(CLAVES_EXTERNAS),
        )


# ===========================================================================
# Estructuras del informe
# ===========================================================================
# No van en modelos.py a proposito: no fluyen entre modulos de calculo, son la
# forma del reporte de esta capa. Lo que fluye entre modulos (ResultadoPunto,
# Verificacion, CompatibilidadGeometrica...) se transporta tal cual, sin
# copiarlo a dicts paralelos.

@dataclass(frozen=True)
class Bloqueo:
    """
    Una etapa que no se pudo completar, con la causa del expediente.

    `criterio` esta relleno solo cuando la causa es un criterio pendiente: es
    la clave que hay que declarar para desbloquear la etapa.
    """

    fase: str
    etapa: str
    tipo: str
    mensaje: str
    criterio: Optional[str] = None
    etiqueta: Optional[str] = None
    concepto: Optional[str] = None
    fuente: Optional[str] = None
    campo: Optional[str] = None
    delta_rasante_m: Optional[float] = None
    # True cuando la etapa no se completo POR DECISION DE ALCANCE de la
    # corrida (--alcance perfil), no por un defecto del expediente. Se imprime
    # con su fundamento igual que cualquier bloqueo -- la memoria necesita esa
    # constancia -- pero no cuenta para `Informe.cerrado`.
    diferido_por_alcance: bool = False


@dataclass
class InformePunto:
    """Lo que la corrida pudo establecer de un punto, y lo que la freno."""

    punto: PuntoCritico
    clasificacion: Optional[Clasificacion] = None
    resultado: Optional[ResultadoPunto] = None
    luz: Optional[DatoDeclarado] = None
    categoria_tr: Optional[DatoDeclarado] = None
    longitud: Optional[DatoDeclarado] = None
    tw: Optional[DatoDeclarado] = None
    proteccion: Optional[ProteccionSalida] = None
    geometria: Optional[CompatibilidadGeometrica] = None
    cama_apoyo: Optional[Any] = None
    espaciamiento: Optional[Espaciamiento] = None
    # Escalones que MD probo, en orden. Es el entregable 1 de la Fase 11
    # ("iteraciones"): la memoria tiene que poder decir por que se descarto el
    # diametro anterior al adoptado. Se llena tambien cuando el punto no cierra.
    traza: List[PasoDiseno] = field(default_factory=list)
    bloqueos: List[Bloqueo] = field(default_factory=list)

    @property
    def dimensionado(self) -> bool:
        return self.resultado is not None and self.resultado.aceptado

    def verificaciones(self) -> Tuple[Tuple[str, Verificacion], ...]:
        """Las verificaciones de todas las fases, cada una con su fase."""
        filas: List[Tuple[str, Verificacion]] = []
        if self.clasificacion is not None:
            filas.append((FASE_CLASIFICACION,
                          self.clasificacion.verificacion_luz))
        if self.resultado is not None:
            filas.extend((FASE_DISENO, v) for v in self.resultado.verificaciones)
        if self.geometria is not None:
            filas.extend((FASE_GEOMETRIA, v) for v in self.geometria.verificaciones)
        return tuple(filas)

    def incumplidas(self) -> Tuple[Verificacion, ...]:
        return tuple(v for _, v in self.verificaciones() if not v.cumple)


@dataclass
class InformeCabezal:
    """Fase 9: es del proyecto, no de un punto (Sec. 9 no lo dimensiona por punto)."""

    cadena: Optional[Any] = None
    mononobe_okabe: Optional[Any] = None
    geometria: Optional[Any] = None
    recubrimientos: List[Any] = field(default_factory=list)
    cuantias: Dict[str, float] = field(default_factory=dict)
    notas: Tuple[str, ...] = ()
    bloqueos: List[Bloqueo] = field(default_factory=list)


@dataclass
class Informe:
    """El expediente completo de una corrida."""

    csv: Path
    generado: str
    alcance: str = ALCANCE_EXPEDIENTE
    puntos: List[InformePunto] = field(default_factory=list)
    cabezal: InformeCabezal = field(default_factory=InformeCabezal)

    @property
    def dimensionados(self) -> int:
        return sum(1 for i in self.puntos if i.dimensionado)

    def bloqueos(self) -> Tuple[Tuple[Optional[str], Bloqueo], ...]:
        """Todos los bloqueos con el id del punto (None = de proyecto)."""
        filas: List[Tuple[Optional[str], Bloqueo]] = []
        for informe in self.puntos:
            filas.extend((informe.punto.id, b) for b in informe.bloqueos)
        filas.extend((None, b) for b in self.cabezal.bloqueos)
        return tuple(filas)

    def diferidos(self) -> Tuple[Tuple[Optional[str], Bloqueo], ...]:
        """Solo lo diferido por alcance, con el id del punto (None = proyecto)."""
        return tuple((id_punto, b) for id_punto, b in self.bloqueos()
                     if b.diferido_por_alcance)

    @property
    def cerrado(self) -> bool:
        """
        True solo si no falta nada AL ALCANCE DECLARADO de la corrida: todos
        los puntos dimensionados, ninguna etapa bloqueada y ninguna
        verificacion incumplida.

        Lo diferido por alcance (`diferido_por_alcance=True`) no cuenta como
        bloqueo: no es un defecto del expediente sino una etapa que ESTA
        corrida declaro fuera de su alcance. Sigue impreso, con fundamento,
        en el informe -- cerrado a nivel de perfil no significa que el
        expediente este completo, y el bloque de alcance lo dice.
        """
        if not self.puntos:
            return False
        if any(not b.diferido_por_alcance for _, b in self.bloqueos()):
            return False
        return all(i.dimensionado and not i.incumplidas() for i in self.puntos)


# ===========================================================================
# Ejecucion de una etapa
# ===========================================================================

def _bloqueo(fase: str, etapa: str, exc: ErrorProyecto) -> Bloqueo:
    """
    Traduce la excepcion del expediente a una fila del informe, conservando lo
    que cada tipo lleva: la clave del criterio, el campo que falta o el delta
    de rasante. Sin eso el informe diria solo "no se pudo".
    """
    datos: Dict[str, Any] = {}
    if isinstance(exc, CriterioPendienteError):
        declarado = ca.criterio(exc.clave)
        datos = {"criterio": exc.clave, "etiqueta": declarado.etiqueta,
                 "concepto": declarado.concepto, "fuente": declarado.fuente}
    elif isinstance(exc, (DatoFaltanteError, DatoInvalidoError)):
        datos = {"campo": exc.campo}
    elif isinstance(exc, DisenoNoFactibleError):
        datos = {"delta_rasante_m": exc.delta_rasante_m}
    return Bloqueo(fase=fase, etapa=etapa, tipo=type(exc).__name__,
                   mensaje=str(exc), **datos)


def _etapa(bloqueos: List[Bloqueo], fase: str, etapa: str, fn) -> Optional[Any]:
    """
    Corre una etapa. Si el expediente la impide, registra el bloqueo y
    devuelve None para que el pipeline siga con lo que no depende de ella.

    Solo `ErrorProyecto`: un fallo de programa se propaga (ver el docstring
    del modulo).
    """
    try:
        return fn()
    except ErrorProyecto as exc:
        bloqueos.append(_bloqueo(fase, etapa, exc))
        return None


def _falta_dato(bloqueos: List[Bloqueo], fase: str, etapa: str,
                campo: str, detalle: str) -> None:
    """Registra la ausencia de un dato externo que nadie puede deducir."""
    bloqueos.append(_bloqueo(fase, etapa,
                             DatoFaltanteError(campo, detalle=detalle)))


# ===========================================================================
# Pipeline de un punto
# ===========================================================================

def _resolver_longitud(informe: InformePunto,
                       externos: DatosExternos) -> Optional[DatoDeclarado]:
    """
    L del conducto: la declarada, o la de M7 (7.B), que exige 'talud_terraplen'.

    Se resuelve ANTES de la Fase 4 porque MD la necesita para el control de
    salida, y es la MISMA que se le pasa despues a 7.B: dos longitudes
    distintas en el mismo punto darian dos cotas de salida distintas.
    """
    punto = informe.punto
    declarada = externos.dato(punto.id, "longitud_m")
    if declarada is not None:
        return declarada
    longitud = _etapa(informe.bloqueos, FASE_GEOMETRIA,
                      "longitud del conducto (7.B)",
                      lambda: longitud_conducto(punto))
    if longitud is None:
        return None
    return DatoDeclarado("longitud_m", longitud, "M7.longitud_conducto (Sec. 7.B)")


def _resolver_tw(informe: InformePunto,
                 externos: DatosExternos) -> Optional[DatoDeclarado]:
    """TW: el declarado, o el criterio 'TW_receptor' (Tablero 3.1)."""
    declarado = externos.dato(informe.punto.id, "TW_m")
    if declarado is not None:
        return declarado
    tw = _etapa(informe.bloqueos, FASE_DISENO,
                "tirante en el receptor (TW)", lambda: ca.valor(CRITERIO_TW))
    if tw is None:
        return None
    return DatoDeclarado("TW_m", tw, f"criterio '{CRITERIO_TW}'")


def _diferir_verificacion(informe: InformePunto, codigo: str,
                          exc: ErrorProyecto, ya_registrados: set) -> None:
    """
    Anota una verificacion diferida al expediente por alcance, UNA vez por
    causa: MD llama al verificador en cada escalon (material x D) y la misma
    V5 fallaria identica en todos; repetir la fila no anade informacion.
    """
    etapa = (f"verificacion {codigo} diferida al expediente "
             f"(alcance {ALCANCE_PERFIL})")
    bloqueo = replace(_bloqueo(FASE_DISENO, etapa, exc),
                      diferido_por_alcance=True)
    clave = (codigo, bloqueo.tipo, bloqueo.criterio, bloqueo.campo)
    if clave in ya_registrados:
        return
    ya_registrados.add(clave)
    informe.bloqueos.append(bloqueo)


def _verificador_perfil(informe: InformePunto):
    """
    La Fase 5 al alcance de perfil: las nueve verificaciones de M5, en el
    orden de la tabla, con V5 y V8 DIFERIDAS al expediente.

    - Obligatorias (deciden si el diametro se acepta): V1, V2, V3, V4, V6,
      V7 y V9. Corren exactamente como en M5.verificar y sus excepciones
      suben igual: un criterio vacio en una obligatoria sigue bloqueando el
      material (y, por la regla de MD, el punto).
    - Diferidas: V5 (remanso / derecho de via) y V8 (evento extremo). Se
      INTENTAN igual en cada escalon -- si algun dia su logica existe y
      devuelven una Verificacion, entra a la tabla en su posicion y vuelve a
      decidir --; mientras lancen ErrorProyecto, el fallo se registra como
      bloqueo diferido con su clave/concepto/fuente y el punto sigue
      dimensionandose. Sus motivos son datos del EXPEDIENTE (perfil de
      remanso, derecho de via, TR de evento extremo), que es exactamente lo
      que el alcance de perfil difiere.

    Vive aqui y no en M5 a proposito: M5 declara QUE exige la Fase 5 completa
    y no sabe de alcances; la decision de diferir es de la corrida, y entra
    por el parametro `verificar` que MD ya expone.

    MINA DELIBERADA (no desactivar): `M5.v8_evento_extremo` termina en
    `raise AssertionError` en cuanto 'TR_evento_extremo' tenga valor -- el
    criterio tendria dato pero la LOGICA de V8 no esta escrita. Aqui solo se
    captura ErrorProyecto, de modo que esa AssertionError PROPAGA y tumba la
    corrida con su traza: es un modulo incompleto, no un asunto de alcance, y
    diferirlo lo escondería. Antes de declarar ese criterio hay que escribir
    el cuerpo de la funcion. (La mina hermana, `M8.seleccionar_clase_calibre`
    con 'clases_producto_por_relleno', esta documentada donde se salta la
    Fase 8 en `correr_punto`.)
    """
    ya_registrados: set = set()

    def verificar(*, punto: PuntoCritico, material, D: float, resultado):
        filas: List[Verificacion] = [
            M5.v1_borde_libre(D=D, resultado=resultado),
            M5.v2_velocidad_minima(resultado=resultado),
            M5.v3_velocidad_maxima(material=material, resultado=resultado),
            M5.v4_carga_entrada(punto=punto, resultado=resultado),
        ]
        try:
            filas.append(M5.v5_remanso(punto=punto, resultado=resultado))
        except ErrorProyecto as exc:
            _diferir_verificacion(informe, "V5", exc, ya_registrados)
        filas.extend([
            M5.v6_material_solido_arrastre(),
            M5.v7_flotacion(punto=punto, material=material, D=D,
                            resultado=resultado),
        ])
        try:
            filas.append(M5.v8_evento_extremo(punto=punto, resultado=resultado))
        except ErrorProyecto as exc:
            _diferir_verificacion(informe, "V8", exc, ya_registrados)
        filas.append(M5.v9_disponibilidad_diametro(D=D, material=material))
        return tuple(filas)

    return verificar


def _fase_2(informe: InformePunto, externos: DatosExternos) -> bool:
    """
    Clasificacion y TR. Devuelve False si el punto no sigue: sin luz no se
    sabe si es alcantarilla o puente, y un puente no se disena aqui (Sec. 3.1).
    """
    punto = informe.punto
    informe.luz = externos.dato(punto.id, "luz_m")
    informe.categoria_tr = externos.dato(punto.id, "categoria_tr")
    luz = None if informe.luz is None else informe.luz.valor
    if luz is None:
        _falta_dato(informe.bloqueos, FASE_CLASIFICACION,
                    "umbral de luz (Sec. 2.1)", "luz_m",
                    "no es columna de Sec. 1.2: declararla con --luz o en "
                    "--datos-externos. Sin ella no se puede separar "
                    "alcantarilla de puente y el punto no se dimensiona")
        return False

    categoria = externos.valor(punto.id, "categoria_tr")
    informe.clasificacion = _etapa(informe.bloqueos, FASE_CLASIFICACION,
                                   "clasificacion y periodo de retorno",
                                   lambda: clasificar(punto, luz, categoria))
    if informe.clasificacion is None:
        return False
    # El TR puede no proceder (Familia C) sin que eso frene el dimensionamiento;
    # la luz que hace puente si lo frena, y sale como no factible.
    return _etapa(informe.bloqueos, FASE_CLASIFICACION,
                  "alcance por luz (Sec. 2.1 / 3.1)",
                  lambda: exigir_alcance(informe.clasificacion)) is not None


def _fase_diseno(informe: InformePunto, externos: DatosExternos,
                 alcance: str = ALCANCE_EXPEDIENTE) -> None:
    """
    Fases 3-5: MD recorre materiales y diametros hasta que uno pase la Fase 5.

    Con alcance de expediente la Fase 5 es la de M5 completa (V1-V9). Con
    alcance de perfil se inyecta `_verificador_perfil`, que difiere V5 y V8
    al expediente y deja las otras siete como obligatorias.
    """
    punto = informe.punto
    informe.longitud = _resolver_longitud(informe, externos)
    informe.tw = _resolver_tw(informe, externos)
    if informe.longitud is None or informe.tw is None:
        return

    verificar = (_verificador_perfil(informe)
                 if alcance == ALCANCE_PERFIL else None)
    Q = externos.valor(punto.id, "Q_m3s")
    S = externos.valor(punto.id, "S_conducto")
    # `informe.traza.append` es el observador de MD: los escalones quedan
    # anotados aunque la etapa termine en DisenoNoFactibleError, que es cuando
    # la memoria mas necesita ver que se probo.
    informe.resultado = _etapa(
        informe.bloqueos, FASE_DISENO, "material y diametro (bucle de MD)",
        lambda: disenar_punto(punto, L=informe.longitud.valor,
                              TW=informe.tw.valor, Q=Q, S=S,
                              verificar=verificar,
                              registrar=informe.traza.append))

    if informe.resultado is not None and not informe.resultado.aceptado:
        informe.bloqueos.append(Bloqueo(
            fase=FASE_DISENO, etapa="material y diametro (bucle de MD)",
            tipo="DisenoNoFactibleError",
            mensaje=informe.resultado.motivo_rechazo or "sin motivo declarado"))


def _fase_6(informe: InformePunto) -> None:
    """
    Proteccion de salida por Laushey, con la V de la regla de doble n.

    Entra `V_erosion` -- la rama de n minimo, la estimacion ALTA -- porque el
    d50 crece con V^2 y la piedra mas grande es el lado conservador de una
    proteccion contra socavacion. La otra rama, `V_sedimentacion`, es la del
    piso de V2 y aqui daria una piedra mas chica que la necesaria.
    """
    resultado = informe.resultado.resultado_hidraulico
    informe.proteccion = _etapa(
        informe.bloqueos, FASE_PROTECCION, "d50, espesor y longitud",
        lambda: proteccion_salida(V=resultado.V_erosion))


def _fase_7(informe: InformePunto) -> None:
    """7.B con el diametro adoptado y la MISMA longitud que uso la Fase 4."""
    resultado = informe.resultado
    informe.geometria = _etapa(
        informe.bloqueos, FASE_GEOMETRIA, "compatibilidad geometrica (7.B)",
        lambda: compatibilidad_geometrica(
            punto=informe.punto, material=resultado.material, D=resultado.D,
            resultado=resultado.resultado_hidraulico,
            longitud=informe.longitud.valor))


def _fase_8(informe: InformePunto) -> None:
    """
    Estructural del conducto. La flotacion (item 3) ya viaja como V7 en la
    tabla de la Fase 5: aqui van la clase o calibre de la norma de producto
    (items 1-2) y la cama de apoyo (item 4). El item 5 esta diferido al
    expediente por la propia hoja de ruta y se imprime como nota.

    Los items 1-2 son hoy un tope declarado en M8: en cuanto
    'clases_producto_por_relleno' tenga valor, `seleccionar_clase_calibre`
    lanza AssertionError porque la tabla todavia no esta transcrita. Esa
    excepcion NO se atrapa -- es un modulo incompleto, no un expediente
    incompleto -- y sale con su traza para que se vea que falta implementarla.
    """
    resultado = informe.resultado
    material, D = resultado.material, resultado.D
    punto = informe.punto

    # Altura real de relleno sobre la clave FISICA (con espesor de pared), la
    # misma definicion que usa V7: subrasante menos clave, no el minimo de 7.A.
    altura = _etapa(informe.bloqueos, FASE_ESTRUCTURAL,
                    "altura de relleno sobre la clave",
                    lambda: punto.cota_subrasante - cota_clave(
                        punto=punto, material=material, D=D))
    if altura is not None:
        _etapa(informe.bloqueos, FASE_ESTRUCTURAL,
               "clase o calibre por norma de producto (items 1-2)",
               lambda: seleccionar_clase_calibre(material=material,
                                                 altura_relleno=altura))
    informe.cama_apoyo = _etapa(informe.bloqueos, FASE_ESTRUCTURAL,
                                "cama de apoyo y relleno lateral (item 4)",
                                lambda: cama_apoyo_relleno_lateral(material))


def _fase_10(informe: InformePunto, externos: DatosExternos) -> None:
    """Espaciamiento de alivio: solo Familia B (Sec. 10)."""
    if informe.punto.familia is not Familia.B:
        return
    L_hidraulico = externos.valor(informe.punto.id, "L_hidraulico_m")
    if L_hidraulico is None:
        _falta_dato(informe.bloqueos, FASE_ALIVIO,
                    "espaciamiento maximo entre alivios", "L_hidraulico_m",
                    "Sec. 10 describe el procedimiento de la cuneta pero no "
                    "fija su seccion, su n de Manning ni la formula de "
                    "intensidad: la longitud por capacidad hidraulica se "
                    "declara, no se deduce")
        return
    informe.espaciamiento = _etapa(
        informe.bloqueos, FASE_ALIVIO, "min(L_normativo, L_hidraulico)",
        lambda: espaciamiento_alivio(L_hidraulico))


def _diferir_fase_8(informe: InformePunto) -> None:
    """
    Constancia del salto de la Fase 8 en alcance de perfil. La etapa completa
    queda disponible, sin cambios, con --alcance expediente.

    MINA DELIBERADA (no desactivar): `M8.seleccionar_clase_calibre` termina
    en `raise AssertionError` en cuanto 'clases_producto_por_relleno' tenga
    valor -- el criterio tendria dato pero la tabla de la norma de producto
    no esta transcrita ni la logica escrita. En alcance de perfil esta guarda
    nunca se alcanza porque la Fase 8 no corre; NO por eso deja de ser
    necesaria: antes de declarar ese criterio hay que escribir el cuerpo de
    la funcion. Igual que su hermana `M5.v8_evento_extremo` con
    'TR_evento_extremo' (documentada en `_verificador_perfil`).
    """
    informe.bloqueos.append(Bloqueo(
        fase=FASE_ESTRUCTURAL,
        etapa=f"Fase 8 completa diferida al expediente (alcance {ALCANCE_PERFIL})",
        tipo="DiferidoPorAlcance",
        mensaje=("clase o calibre por norma de producto (items 1-2) y cama "
                 "de apoyo (item 4) no se ejecutan en alcance de perfil: son "
                 "verificacion estructural del conducto, que la hoja de ruta "
                 "difiere al expediente (Sec. 7.A / Fase 8, 'Diferir al "
                 "expediente la verificacion detallada'). Disponibles sin "
                 "cambios con --alcance expediente"),
        diferido_por_alcance=True))


def correr_punto(punto: PuntoCritico, externos: DatosExternos,
                 alcance: str = ALCANCE_EXPEDIENTE) -> InformePunto:
    """
    El pipeline de un punto, de la Fase 2 a la Fase 10. Cada etapa corre si su
    insumo existe; si no, queda registrada como bloqueo y las que no dependen
    de ella siguen (la Fase 10 no necesita el diametro, por ejemplo).

    Con alcance de perfil, la Fase 5 difiere V5 y V8 (ver
    `_verificador_perfil`) y la Fase 8 no se ejecuta: queda como bloqueo
    diferido con su fundamento (ver `_diferir_fase_8`).
    """
    informe = InformePunto(punto=punto)

    if _fase_2(informe, externos):
        _fase_diseno(informe, externos, alcance)
        if informe.dimensionado:
            _fase_6(informe)
            _fase_7(informe)
            if alcance == ALCANCE_PERFIL:
                _diferir_fase_8(informe)
            else:
                _fase_8(informe)
    _fase_10(informe, externos)
    return informe


# ===========================================================================
# Fase 9 - Cabezal (del proyecto, no del punto)
# ===========================================================================

def correr_cabezal() -> InformeCabezal:
    """
    Las piezas de Fase 9 que se sostienen solas: la cadena sismica de 9.2, el
    K_AE de Mononobe-Okabe, la geometria declarada, los recubrimientos de 9.4
    y las cuantias minimas de referencia de E.060.

    La tabla de estabilidad E1-E5 no se ensambla aqui: ver
    NOTA_ESTABILIDAD_CABEZAL.
    """
    informe = InformeCabezal()
    informe.cadena = _etapa(informe.bloqueos, FASE_CABEZAL,
                            "cadena sismica (9.2)", cadena_sismica)
    informe.mononobe_okabe = _etapa(informe.bloqueos, FASE_CABEZAL,
                                    "K_AE de Mononobe-Okabe (9.2)",
                                    k_ae_del_proyecto)
    informe.geometria = _etapa(informe.bloqueos, FASE_CABEZAL,
                               "predimensionamiento del cabezal (9.3, E1-E5)",
                               geometria_adoptada)
    for condicion in RECUBRIMIENTO:
        recubrimiento = _etapa(
            informe.bloqueos, FASE_CABEZAL,
            f"recubrimiento de diseno '{condicion}' (9.4)",
            lambda c=condicion: recubrimiento_de_diseno(condicion=c))
        if recubrimiento is not None:
            informe.recubrimientos.append(recubrimiento)
    for direccion in CUANTIA_MIN_MURO:
        cuantia = _etapa(informe.bloqueos, FASE_CABEZAL,
                         f"cuantia minima {direccion} (9.4, referencia)",
                         lambda d=direccion: cuantia_minima(direccion=d))
        if cuantia is not None:
            informe.cuantias[direccion] = cuantia

    notas = list(condicion_normativa_cabezal())
    notas.append(NOTA_ESTABILIDAD_CABEZAL)
    aviso = _etapa(informe.bloqueos, FASE_CABEZAL,
                   "aviso de ambiente corrosivo (9.4)", aviso_ambiente_corrosivo)
    if aviso is not None:
        notas.append(aviso)
    informe.notas = tuple(notas)
    return informe


def _cabezal_diferido() -> InformeCabezal:
    """La Fase 9 entera como diferida por alcance, con su constancia."""
    informe = InformeCabezal()
    informe.bloqueos.append(Bloqueo(
        fase=FASE_CABEZAL,
        etapa=f"Fase 9 completa diferida al expediente (alcance {ALCANCE_PERFIL})",
        tipo="DiferidoPorAlcance",
        mensaje=("cadena sismica, Mononobe-Okabe, predimensionamiento, "
                 "recubrimientos y cuantias del cabezal no se ejecutan en "
                 "alcance de perfil: dependen de datos del expediente "
                 "(ensayos de fundacion y relleno del Tablero 3 y criterios "
                 "C.3) y de la estabilidad E1-E5 que la propia Fase 9 remite "
                 "al expediente. Disponibles sin cambios con --alcance "
                 "expediente"),
        diferido_por_alcance=True))
    return informe


def correr(ruta_csv: Path, externos: DatosExternos,
           alcance: str = ALCANCE_EXPEDIENTE) -> Informe:
    """
    Corre el expediente completo: M0 carga el CSV y cada punto recorre el
    pipeline; la Fase 9 corre una vez para el proyecto.

    `alcance` es la bifurcacion declarada de la corrida (--alcance):
    "expediente" (defecto) corre todo como siempre; "perfil" difiere V5, V8,
    la Fase 8 y la Fase 9 al expediente, dejando constancia de cada uno.

    M0 no se protege con `_etapa`: si el CSV no se puede cargar no hay
    expediente que informar, y la excepcion sale al `main`.
    """
    puntos = cargar_puntos(ruta_csv)
    informe = Informe(csv=ruta_csv,
                      generado=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                      alcance=alcance)
    informe.puntos = [correr_punto(punto, externos, alcance)
                      for punto in puntos]
    informe.cabezal = (_cabezal_diferido() if alcance == ALCANCE_PERFIL
                       else correr_cabezal())

    _avisar_ids_desconocidos(informe, externos)
    return informe


def _avisar_ids_desconocidos(informe: Informe, externos: DatosExternos) -> None:
    """
    Un id de --datos-externos que no esta en el CSV es un dato declarado que
    no se aplico a nada: casi siempre un id mal escrito, y silenciarlo deja al
    punto real sin su luz o sin su longitud.
    """
    del_csv = {i.punto.id for i in informe.puntos}
    for id_punto in externos.ids_declarados():
        if id_punto in del_csv:
            continue
        informe.cabezal.bloqueos.append(_bloqueo(
            FASE_CARGA, "datos externos declarados",
            DatoInvalidoError("datos_externos", valor=id_punto,
                              motivo="el id no esta en el CSV: sus datos "
                                     "declarados no se aplicaron a ningun punto")))


# ===========================================================================
# Volcado a JSON
# ===========================================================================

def _num(valor: Any) -> Any:
    """
    Un float no finito no es JSON valido. Sale como texto para que el archivo
    se pueda leer siempre y el problema quede visible en el propio campo.
    """
    if isinstance(valor, float) and not math.isfinite(valor):
        return repr(valor)
    return valor


def _verificacion_json(fase: str, v: Verificacion) -> Dict[str, Any]:
    return {"fase": fase, "codigo": v.codigo, "numeral": v.numeral,
            "cumple": v.cumple, "valor_obtenido": _num(v.valor_obtenido),
            "valor_admisible": _num(v.valor_admisible),
            "criterio_aplicado": v.criterio_aplicado}


def _paso_json(paso: PasoDiseno) -> Dict[str, Any]:
    return {"material": paso.material, "D_m": _num(paso.D),
            "aceptado": paso.aceptado, "motivo": paso.motivo,
            "incumplidas": [v.codigo or v.numeral for v in paso.incumplidas]}


def _dato_json(dato: Optional[DatoDeclarado]) -> Optional[Dict[str, Any]]:
    if dato is None:
        return None
    return {"valor": _num(dato.valor), "origen": dato.origen}


def _bloqueo_json(bloqueo: Bloqueo) -> Dict[str, Any]:
    return {"fase": bloqueo.fase, "etapa": bloqueo.etapa, "tipo": bloqueo.tipo,
            "criterio": bloqueo.criterio, "etiqueta": bloqueo.etiqueta,
            "concepto": bloqueo.concepto, "fuente": bloqueo.fuente,
            "campo": bloqueo.campo,
            "delta_rasante_m": _num(bloqueo.delta_rasante_m),
            "diferido_por_alcance": bloqueo.diferido_por_alcance,
            "mensaje": bloqueo.mensaje}


def _clasificacion_json(c: Clasificacion) -> Dict[str, Any]:
    tr = c.periodo_retorno
    return {"luz_m": _num(c.luz_m), "denominacion": c.denominacion.value,
            "numeral_luz": c.verificacion_luz.numeral,
            "familia": c.perfil.familia.value,
            "origen_del_caudal": c.perfil.origen_del_caudal,
            "TR_procede": tr.procede,
            "TR_anios": tr.anios,
            "TR_categoria": None if tr.categoria is None else tr.categoria.value,
            "TR_numeral": tr.numeral, "TR_fundamento": tr.fundamento,
            "datos_pendientes": list(c.datos_pendientes)}


def _diseno_json(resultado: ResultadoPunto) -> Dict[str, Any]:
    material, hidraulica = resultado.material, resultado.resultado_hidraulico
    return {"material": material.nombre, "tipo": material.tipo.value,
            "norma_producto": material.norma_producto,
            "seccion_eg2013": material.seccion_eg2013,
            "n_min": _num(material.n_min), "n_max": _num(material.n_max),
            "D_m": _num(resultado.D), "D_max_material_m": _num(material.D_max),
            "control_gobernante": hidraulica.control_gobernante.value,
            "Q_m3s": _num(hidraulica.Q),
            # Dos claves y no una "V_m_s": la velocidad de la rama n_min
            # (techos: V3, d50) y la de la rama n_max (piso: V2) son numeros
            # distintos, y una sola clave obligaba a adivinar cual (MAT-D1).
            "V_erosion_m_s": _num(hidraulica.V_erosion),
            "V_sedimentacion_m_s": _num(hidraulica.V_sedimentacion),
            "y_normal_m": _num(hidraulica.y_normal),
            "y_critico_m": _num(hidraulica.y_critico),
            "HW_entrada_m": _num(hidraulica.HW_entrada),
            "HW_salida_m": _num(hidraulica.HW_salida),
            "HW_gobernante_m": _num(hidraulica.HW)}


def _proteccion_json(p: ProteccionSalida) -> Dict[str, Any]:
    return {"numeral": p.numeral, "V_m_s": _num(p.V), "d50_m": _num(p.d50),
            "espesor_m": _num(p.espesor), "longitud_m": _num(p.longitud),
            "criterio_espesor": p.criterio_espesor,
            "criterio_longitud": p.criterio_longitud,
            "advertencias": list(p.advertencias)}


def _geometria_json(g: CompatibilidadGeometrica) -> Dict[str, Any]:
    t = g.tamizado
    return {"numeral": g.numeral, "longitud_m": _num(g.longitud),
            "proyeccion_taludes_m": _num(g.proyeccion_taludes),
            "factor_esviaje": _num(g.factor_esviaje),
            "altura_terraplen_m": _num(g.altura_terraplen),
            "S_conducto": _num(g.S_conducto),
            "cota_entrada_msnm": _num(g.cota_entrada),
            # El consumidor del JSON tiene que poder distinguir una cota
            # levantada de una adoptada sin leer la memoria: el mismo archivo
            # ya declara el origen de los datos externos ("origen": "criterio
            # 'TW_receptor'") y esta cota no lo hacia (SIS-A-04).
            "cota_entrada_origen": {
                "adoptada": True,
                "criterio": M5.CRITERIO_ORIGEN_COTA_ENTRADA,
                "regla": ca.valor_si_declarado(M5.CRITERIO_ORIGEN_COTA_ENTRADA),
                "nota": "no es cota medida: sale de la regla declarada en ese "
                        "criterio mientras el expediente no entregue la cota "
                        "de invert de entrada por punto",
            },
            "cota_salida_msnm": _num(g.cota_salida), "caida_m": _num(g.caida),
            "factible": g.factible,
            "delta_rasante_cm": _num(g.delta_rasante_cm),
            "tamizado": {"cota_rasante_min_msnm": _num(t.cota_rasante_min),
                         "cota_rasante_actual_msnm": _num(t.cota_rasante_actual),
                         "cota_por_recubrimiento_msnm": _num(t.cota_por_recubrimiento),
                         "cota_por_resguardo_msnm": _num(t.cota_por_resguardo),
                         "condicion_gobernante": t.condicion_gobernante.value,
                         "criterio_gobernante": t.criterio_gobernante,
                         "mensaje": t.mensaje}}


def _espaciamiento_json(e: Espaciamiento) -> Dict[str, Any]:
    return {"numeral": e.numeral, "L_normativo_m": _num(e.L_normativo),
            "L_hidraulico_m": _num(e.L_hidraulico),
            "espaciamiento_max_m": _num(e.espaciamiento_max),
            "gobierna": e.gobierna.value,
            "criterio_normativo": e.criterio_normativo}


def _punto_json(informe: InformePunto) -> Dict[str, Any]:
    punto = informe.punto
    salida: Dict[str, Any] = {
        "id": punto.id, "progresiva": punto.progresiva_display,
        "familia": punto.familia.value,
        "pendientes_externos": list(punto.pendientes_externos),
        "dimensionado": informe.dimensionado,
        "datos_declarados": {"luz_m": _dato_json(informe.luz),
                             "categoria_tr": _dato_json(informe.categoria_tr),
                             "longitud_m": _dato_json(informe.longitud),
                             "TW_m": _dato_json(informe.tw)},
        "clasificacion": (None if informe.clasificacion is None
                          else _clasificacion_json(informe.clasificacion)),
        "diseno": (None if not informe.dimensionado
                   else _diseno_json(informe.resultado)),
        "proteccion_salida": (None if informe.proteccion is None
                              else _proteccion_json(informe.proteccion)),
        "geometria": (None if informe.geometria is None
                      else _geometria_json(informe.geometria)),
        "estructural": None,
        "espaciamiento_alivio": (None if informe.espaciamiento is None
                                 else _espaciamiento_json(informe.espaciamiento)),
        "iteraciones": [_paso_json(p) for p in informe.traza],
        "verificaciones": [_verificacion_json(fase, v)
                           for fase, v in informe.verificaciones()],
        # Las filas V2b y V4b de la tabla de Fase 5 no se evaluan, y la
        # constancia viaja con el punto igual que la del item 5 de Fase 8:
        # contar nueve verificaciones donde la hoja de ruta lista ONCE no
        # puede quedar como un ejercicio de resta del lector
        # (SIS-A-13 / MAT-O15).
        "verificaciones_no_evaluadas": list(M5.verificaciones_no_evaluadas()),
        "bloqueos": [_bloqueo_json(b) for b in informe.bloqueos],
    }
    if informe.cama_apoyo is not None:
        salida["estructural"] = {
            "cama_apoyo": informe.cama_apoyo.cama_apoyo,
            "sujecion_relleno_lateral": informe.cama_apoyo.sujecion_relleno_lateral,
            "numeral": informe.cama_apoyo.numeral,
            "verificacion_diferida": list(verificacion_diferida_estructural())}
    return salida


def _cabezal_json(informe: InformeCabezal) -> Dict[str, Any]:
    cadena = informe.cadena
    return {
        "cadena_sismica": (None if cadena is None else {
            "numeral": cadena.numeral, "PGA": _num(cadena.PGA),
            "F_pga": _num(cadena.F_pga), "A_s": _num(cadena.A_s),
            "k_h0": _num(cadena.k_h0), "factor_muro": _num(cadena.factor_muro),
            "k_h": _num(cadena.k_h), "k_v": _num(cadena.k_v),
            "pasos": [{"simbolo": p.simbolo, "valor": _num(p.valor),
                       "concepto": p.concepto} for p in cadena.pasos]}),
        "mononobe_okabe": (None if informe.mononobe_okabe is None else {
            "K_AE": _num(informe.mononobe_okabe.K_AE),
            "K_A": _num(informe.mononobe_okabe.K_A)}),
        "geometria": (None if informe.geometria is None else {
            "H_m": _num(informe.geometria.H), "B_m": _num(informe.geometria.B),
            "D_f_m": _num(informe.geometria.D_f)}),
        "recubrimientos": [{"condicion": r.condicion,
                            "e060_mm": _num(r.e060_mm),
                            "aashto_mm": _num(r.aashto_mm),
                            "adoptado_mm": _num(r.adoptado_mm),
                            "origen": r.origen, "numeral": r.numeral}
                           for r in informe.recubrimientos],
        "cuantias_minimas": {k: _num(v) for k, v in informe.cuantias.items()},
        "notas": list(informe.notas),
        "bloqueos": [_bloqueo_json(b) for b in informe.bloqueos],
    }


def informe_json(informe: Informe) -> Dict[str, Any]:
    """El expediente completo como dict listo para `json.dump`."""
    bloqueantes = criterios_bloqueantes(informe)
    return {
        "expediente": {
            "csv": str(informe.csv), "generado_utc": informe.generado,
            "puntos": len(informe.puntos),
            "dimensionados": informe.dimensionados,
            "cerrado": informe.cerrado},
        # Constancia del alcance de la corrida (no cosmetica: es la
        # declaracion que la memoria necesita). "cerrado" de arriba se lee AL
        # ALCANCE declarado aqui: lo diferido no cuenta como bloqueo, pero
        # queda listado entero, con su fundamento, en "diferidos".
        "alcance": {
            "nivel": informe.alcance,
            "diferidos": [{"punto": id_punto, **_bloqueo_json(b)}
                          for id_punto, b in informe.diferidos()]},
        "puntos": [_punto_json(p) for p in informe.puntos],
        "cabezal": _cabezal_json(informe.cabezal),
        "datos_sitio": {
            "usados": [{"clave": k, "etiqueta": ds.dato(k).etiqueta,
                        "valor": _num(ds.dato(k).valor),
                        "concepto": ds.dato(k).concepto,
                        "trazabilidad": ds.dato(k).trazabilidad,
                        "ambito": ds.dato(k).ambito}
                       for k in ds.datos_usados()],
            "sin_valor_declarados": ds.datos_sin_valor(),
            "trazabilidad_incompleta": ds.datos_con_verificacion_pendiente()},
        "criterios": {
            # Valor EFECTIVO y procedencia: el JSON es el otro reporte de la
            # corrida y tenia el mismo defecto que la memoria HTML -- leia el
            # valor del ARCHIVO, de modo que un criterio declarado en
            # caliente viajaba con "valor": null mientras gobernaba el
            # calculo (SIS-A-01).
            "usados": [{"clave": k,
                        "etiqueta": ca.criterio(k).etiqueta,
                        "valor": _num(ca.criterio_efectivo(k).valor),
                        "declarado_en_caliente": ca.declarado_en_caliente(k),
                        "concepto": ca.criterio(k).concepto}
                       for k in ca.criterios_usados()],
            "sin_valor_declarados": ca.criterios_sin_valor(),
            "declarados_en_caliente": ca.criterios_declarados_en_caliente(),
            # Hermano de `trazabilidad_incompleta` de los datos de sitio: sin
            # el, un consumidor del JSON veia que datos de sitio quedaban sin
            # cerrar documentalmente y no veia que criterios (SIS-D-07).
            "verificacion_pendiente": ca.criterios_con_verificacion_pendiente(),
            "sin_consumidor": ca.criterios_sin_consumidor(),
            "bloquearon": [{"clave": c.clave, "etiqueta": c.etiqueta,
                            "concepto": c.concepto, "fuente": c.fuente,
                            "reemplazado_por": c.reemplazado_por,
                            "fases": list(c.fases), "etapas": list(c.etapas),
                            "puntos": list(c.puntos)}
                           for c in bloqueantes]},
    }


# ===========================================================================
# Volcado a stdout
# ===========================================================================

def _fmt(valor: Any, decimales: int = 3) -> str:
    """Un numero con decimales fijos; cualquier otra cosa, tal como viene."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return str(valor)
    if isinstance(valor, float) and not math.isfinite(valor):
        return repr(valor)
    return f"{float(valor):.{decimales}f}"


def _titulo(texto: str, marca: str = "=") -> List[str]:
    return [marca * ANCHO, texto, marca * ANCHO]


def _lineas_verificaciones(informe: InformePunto) -> List[str]:
    filas = informe.verificaciones()
    if not filas:
        return []
    out = [f"{SANGRIA}Verificaciones:"]
    for fase, v in filas:
        marca = MARCA_CUMPLE if v.cumple else MARCA_INCUMPLE
        codigo = v.codigo or fase.split(" - ")[0]
        out.append(f"{SANGRIA * 2}{marca} {codigo:<4} {v.numeral:<28} "
                   f"obtenido {_fmt(v.valor_obtenido)} | admisible "
                   f"{_fmt(v.valor_admisible)}")
        if v.criterio_aplicado:
            # Consulta tolerante: una clave que no este en CRITERIOS se imprime
            # tal cual, sin etiqueta. Un desajuste de nombre es un problema de
            # reporte y no puede tumbar la memoria del punto.
            declarado = ca.CRITERIOS.get(v.criterio_aplicado)
            etiqueta = f" [{declarado.etiqueta}]" if declarado is not None else ""
            out.append(f"{SANGRIA * 4}umbral del criterio "
                       f"'{v.criterio_aplicado}'{etiqueta}")
    return out


def _lineas_bloqueos(bloqueos: Sequence[Bloqueo]) -> List[str]:
    if not bloqueos:
        return []
    out = [f"{SANGRIA}Bloqueos:"]
    for b in bloqueos:
        out.append(f"{SANGRIA * 2}[{b.tipo}] {b.fase} -> {b.etapa}")
        if b.criterio:
            out.append(f"{SANGRIA * 4}falta declarar: {b.criterio} "
                       f"[{b.etiqueta}] - {b.concepto}")
            out.append(f"{SANGRIA * 4}fuente: {b.fuente}")
        else:
            out.append(f"{SANGRIA * 4}{b.mensaje}")
    return out


def _lineas_punto(informe: InformePunto) -> List[str]:
    punto = informe.punto
    out = ["-" * ANCHO,
           f"{punto.id}  |  progresiva {punto.progresiva_display}  |  "
           f"Familia {punto.familia.value}",
           "-" * ANCHO]

    if informe.clasificacion is not None:
        c = informe.clasificacion
        tr = (f"TR {c.periodo_retorno.anios} anios"
              if c.periodo_retorno.anios is not None
              else "TR no procede (ver fundamento en el JSON)")
        out.append(f"{SANGRIA}Fase 2  {c.denominacion.value} "
                   f"(luz {_fmt(c.luz_m)} m, num. {c.verificacion_luz.numeral}) "
                   f"| {tr}")

    if informe.dimensionado:
        r = informe.resultado
        h = r.resultado_hidraulico
        out.append(f"{SANGRIA}Fase 4  Material : {r.material.nombre} "
                   f"({r.material.norma_producto})")
        out.append(f"{SANGRIA}        Diametro : D = {_fmt(r.D)} m")
        out.append(f"{SANGRIA}        Control  : {h.control_gobernante.value} "
                   f"(HW = {_fmt(h.HW)} m; entrada {_fmt(h.HW_entrada)} / "
                   f"salida {_fmt(h.HW_salida)})")
        out.append(f"{SANGRIA}        Hidraulica: y_n = {_fmt(h.y_normal)} m, "
                   f"y_c = {_fmt(h.y_critico)} m, "
                   f"V_erosion = {_fmt(h.V_erosion)} m/s (n min), "
                   f"V_sedimentacion = {_fmt(h.V_sedimentacion)} m/s (n max), "
                   f"Q = {_fmt(h.Q)} m3/s")
        out.append(f"{SANGRIA}        Longitud : L = {_fmt(informe.longitud.valor)} m "
                   f"({informe.longitud.origen}) | TW = "
                   f"{_fmt(informe.tw.valor)} m ({informe.tw.origen})")
    else:
        out.append(f"{SANGRIA}Fase 4  sin dimensionar")

    out.extend(_lineas_verificaciones(informe))

    if informe.proteccion is not None:
        p = informe.proteccion
        out.append(f"{SANGRIA}Fase 6  d50 = {_fmt(p.d50)} m, espesor "
                   f"{_fmt(p.espesor)} m, longitud {_fmt(p.longitud)} m "
                   f"(num. {p.numeral})")
        for advertencia in p.advertencias:
            out.append(f"{SANGRIA * 4}aviso: {advertencia}")
    if informe.geometria is not None:
        g = informe.geometria
        # La cota de entrada NO es un dato del CSV: sale de la regla que el
        # proyectista declaro en 'origen_cota_fondo_entrada'. Va marcada en
        # las TRES salidas (texto, JSON y HTML) y no solo en la memoria: la
        # GUI pinta el detalle del punto con estas mismas lineas, y un numero
        # en msnm sin marca se lee como cota levantada en campo (SIS-A-04).
        out.append(f"{SANGRIA}Fase 7  L = {_fmt(g.longitud)} m, cota entrada "
                   f"{_fmt(g.cota_entrada)} (ADOPTADA, criterio "
                   f"'{M5.CRITERIO_ORIGEN_COTA_ENTRADA}': no es cota medida) "
                   f"/ salida {_fmt(g.cota_salida)} msnm")
        out.append(f"{SANGRIA * 4}{g.tamizado.mensaje}")
    if informe.cama_apoyo is not None:
        out.append(f"{SANGRIA}Fase 8  cama: {informe.cama_apoyo.cama_apoyo} "
                   f"(num. {informe.cama_apoyo.numeral})")
    if informe.espaciamiento is not None:
        e = informe.espaciamiento
        out.append(f"{SANGRIA}Fase 10 espaciamiento max = "
                   f"{_fmt(e.espaciamiento_max)} m (gobierna {e.gobierna.value}; "
                   f"normativo {_fmt(e.L_normativo)} / hidraulico "
                   f"{_fmt(e.L_hidraulico)})")

    out.extend(_lineas_bloqueos(informe.bloqueos))
    return out


def _lineas_cabezal(informe: InformeCabezal) -> List[str]:
    out = _titulo(f"{FASE_CABEZAL} - del proyecto, no del punto", "-")
    if informe.cadena is not None:
        c = informe.cadena
        out.append(f"{SANGRIA}Cadena sismica (num. {c.numeral}): "
                   f"PGA {_fmt(c.PGA, 2)} g -> A_s {_fmt(c.A_s, 2)} g -> "
                   f"k_h {_fmt(c.k_h, 2)} | k_v {_fmt(c.k_v, 2)}")
    for r in informe.recubrimientos:
        out.append(f"{SANGRIA}Recubrimiento '{r.condicion}': "
                   f"{_fmt(r.adoptado_mm, 0)} mm (gobierna {r.origen}, "
                   f"{r.numeral})")
    for direccion, cuantia in informe.cuantias.items():
        out.append(f"{SANGRIA}Cuantia minima {direccion}: {cuantia}")
    for nota in informe.notas:
        out.append(f"{SANGRIA * 2}nota: {nota}")
    out.extend(_lineas_bloqueos(informe.bloqueos))
    return out


def _lineas_criterios_bloqueantes(informe: Informe) -> List[str]:
    bloqueantes = criterios_bloqueantes(informe)
    out = _titulo("CRITERIOS PENDIENTES QUE BLOQUEARON UNA ETAPA")
    if not bloqueantes:
        out.append("Ninguno: ningun criterio sin valor se invoco en esta corrida.")
        return out
    for c in bloqueantes:
        puntos = ", ".join(c.puntos) if c.puntos else "proyecto (Fase 9)"
        out.append(f"[{c.etiqueta}] {c.clave}")
        out.append(f"{SANGRIA}Concepto : {c.concepto}")
        out.append(f"{SANGRIA}Fuente   : {c.fuente}")
        if c.reemplazado_por:
            out.append(f"{SANGRIA}Lo resuelve: {c.reemplazado_por}")
        out.append(f"{SANGRIA}Bloqueo  : {'; '.join(c.etapas)}")
        out.append(f"{SANGRIA}Puntos   : {puntos}")
        out.append("")
    return out


def _lineas_alcance(informe: Informe) -> List[str]:
    """
    La declaracion de alcance de la corrida. En alcance de expediente basta
    la linea; en alcance de perfil se lista TODO lo diferido con su
    fundamento: es la constancia que la memoria de tesis necesita para que
    "cerrado" no se lea como "expediente completo".
    """
    out = _titulo("ALCANCE DE LA CORRIDA")
    out.append(f"Alcance declarado: {informe.alcance} (bandera --alcance; "
               f"por defecto {ALCANCE_EXPEDIENTE})")
    diferidos = informe.diferidos()
    if not diferidos:
        out.append("Ninguna etapa diferida por alcance: la corrida ejecuto "
                   "el pipeline completo.")
        return out
    out.append("Diferido al expediente por alcance (registrado con su "
               "fundamento; NO cuenta como bloqueo para el cierre):")
    for id_punto, b in diferidos:
        donde = id_punto if id_punto is not None else "proyecto"
        out.append(f"{SANGRIA}[{donde}] {b.fase}")
        out.append(f"{SANGRIA * 2}{b.etapa}")
        if b.criterio:
            out.append(f"{SANGRIA * 2}falta declarar: {b.criterio} "
                       f"[{b.etiqueta}] - {b.concepto}")
            out.append(f"{SANGRIA * 2}fuente: {b.fuente}")
        else:
            out.append(f"{SANGRIA * 2}{b.mensaje}")
    return out


def _lineas_resumen(informe: Informe) -> List[str]:
    total = len(informe.puntos)
    incumplidas = sum(len(i.incumplidas()) for i in informe.puntos)
    diferidos = len(informe.diferidos())
    bloqueos = len(informe.bloqueos()) - diferidos
    out = _titulo("RESUMEN")
    out.append(f"CSV                     : {informe.csv}")
    out.append(f"Alcance de la corrida   : {informe.alcance}")
    out.append(f"Puntos del expediente   : {total}")
    out.append(f"Puntos dimensionados    : {informe.dimensionados}")
    out.append(f"Verificaciones incumplidas: {incumplidas}")
    out.append(f"Etapas bloqueadas       : {bloqueos}")
    if diferidos:
        out.append(f"Diferidas por alcance   : {diferidos} (ver ALCANCE DE "
                   "LA CORRIDA; no cuentan para el cierre)")
    out.append(f"Expediente cerrado      : {'si' if informe.cerrado else 'no'}")
    if not informe.cerrado:
        out.append("")
        out.append("El expediente NO cierra. Mientras un criterio siga sin "
                   "valor, la etapa que lo invoca se detiene: no se sustituye "
                   "por un defecto (Sec. 0.7).")
    return out


def volcar(informe: Informe, con_criterios: bool = False) -> str:
    """El informe completo como texto, en el orden en que se lee la memoria."""
    lineas = _titulo("EXPEDIENTE DE ALCANTARILLAS - "
                     "M0 -> M1 -> MD -> M6 -> M7 -> M8 -> M9 -> M10")
    lineas.append(f"CSV: {informe.csv}    generado (UTC): {informe.generado}")
    lineas.append("")
    for punto in informe.puntos:
        lineas.extend(_lineas_punto(punto))
        lineas.append("")
    lineas.extend(_lineas_cabezal(informe.cabezal))
    lineas.append("")
    lineas.extend(_lineas_alcance(informe))
    lineas.append("")
    lineas.extend(_lineas_criterios_bloqueantes(informe))
    lineas.extend(_lineas_resumen(informe))
    if con_criterios:
        lineas.append("")
        lineas.append(ds.reporte_datos_sitio(solo_usados=True))
        lineas.append("")
        lineas.append(ca.reporte_criterios(solo_usados=True))
    return "\n".join(lineas)


# ===========================================================================
# Entrada
# ===========================================================================

def plantilla_por_alcance(alcance: str,
                          forzada: Optional[Path] = None) -> Path:
    """
    Que plantilla de M11 usa la memoria: la explicita si se paso --plantilla,
    y si no la que corresponde al alcance de la corrida.

    El alcance elige el DEFECTO, no una obligacion: la de perfil y la de
    expediente comparten el contrato de marcadores, de modo que cualquiera de
    las dos se puede forzar sobre cualquier corrida. Una memoria de perfil
    impresa con la plantilla de expediente sigue siendo correcta -- solo trae
    ademas el volcado de Tableros 1-2-3 -- y esa combinacion tiene su uso al
    revisar que quedo fuera.
    """
    if forzada is not None:
        return Path(forzada)
    nombre = (NOMBRE_PLANTILLA_PERFIL if alcance == ALCANCE_PERFIL
              else NOMBRE_PLANTILLA)
    return DIR_PLANTILLAS / nombre


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cli.py",
        description="Corre el pipeline de alcantarillas (M0 a M10) sobre el "
                    "CSV de puntos criticos de Sec. 1.2.",
        epilog="Los datos que no son columna de Sec. 1.2 (luz, TW, longitud, "
               "Q/S de Familias B y C, L_hidraulico) se declaran con las "
               "banderas o con --datos-externos. No tienen valor por defecto.")
    p.add_argument("csv", type=Path, help="ruta del CSV de puntos criticos")
    p.add_argument("--json", type=Path, dest="json_salida",
                   help="ruta del JSON de salida (por defecto, junto al CSV "
                        "como <csv>.informe.json)")
    p.add_argument("--datos-externos", type=Path, dest="datos_externos",
                   help="JSON con los datos declarados, globales y por punto")
    p.add_argument("--declarar", action="append", default=[],
                   metavar="CLAVE=VALOR", dest="declaraciones",
                   help="declara un criterio de criterios_adoptados.py SOLO "
                        "para esta corrida (repetible). Es la misma via que "
                        "la GUI: el archivo no se toca y la memoria imprime "
                        "el valor marcado como declarado para la corrida")
    p.add_argument("--luz", type=float, help="luz del cruce, m (Sec. 2.1)")
    p.add_argument("--tw", type=float, dest="TW",
                   help="tirante en el receptor sobre el fondo de la salida, m")
    p.add_argument("--longitud", type=float,
                   help="longitud del conducto, m (si no, la calcula 7.B)")
    p.add_argument("--l-hidraulico", type=float, dest="l_hidraulico",
                   help="longitud por capacidad de la cuneta, m (Fase 10)")
    p.add_argument("--categoria-tr", dest="categoria_tr",
                   help="fila de la Tabla N 02: quebrada_importante o "
                        "quebrada_menor (Sec. 2.2, Familia A)")
    p.add_argument("--criterios", action="store_true",
                   help="imprime tambien la declaracion completa de los "
                        "datos de sitio [S] y de los criterios usados "
                        "(reporte_datos_sitio + reporte_criterios)")
    p.add_argument("--html", type=Path, dest="html_salida",
                   help="escribe la memoria de calculo de la Fase 11 (M11) "
                        "en esa ruta, como HTML")
    p.add_argument("--pdf", type=Path, dest="pdf_salida",
                   help="escribe la memoria en PDF con weasyprint; si no esta "
                        "instalado, deja el HTML y lo abre en el navegador "
                        "para Ctrl+P (misma via que legacy/Tc.py)")
    p.add_argument("--csv-resumen", type=Path, dest="csv_resumen_salida",
                   help="escribe el cuadro resumen de la Fase 11 (entregable "
                        "3) en esa ruta, como CSV")
    p.add_argument("--proyecto", default="",
                   help="nombre del proyecto que encabeza la memoria")
    p.add_argument("--plantilla", type=Path, dest="plantilla",
                   help="fuerza la plantilla HTML de la memoria (M11). Por "
                        f"defecto, '{NOMBRE_PLANTILLA_PERFIL}' con --alcance "
                        f"perfil y '{NOMBRE_PLANTILLA}' con --alcance "
                        "expediente. Las dos aceptan cualquier corrida")
    p.add_argument("--alcance", choices=(ALCANCE_PERFIL, ALCANCE_EXPEDIENTE),
                   default=ALCANCE_EXPEDIENTE,
                   help="alcance de la corrida. 'expediente' (defecto): el "
                        "pipeline completo, como siempre. 'perfil': V5 y V8 "
                        "se intentan pero su fallo se difiere al expediente, "
                        "y las Fases 8 y 9 no se ejecutan; todo lo diferido "
                        "queda registrado con su fundamento y no cuenta para "
                        "el cierre")
    return p


def declarar_criterios(declaraciones: Sequence[str]) -> List[str]:
    """
    Aplica las declaraciones `CLAVE=VALOR` de `--declarar` a la corrida.

    Pasa por `criterios_adoptados.establecer_valor_dinamico`, el UNICO camino
    de declaracion en caliente, que a su vez somete el valor a la misma
    guardia que el archivo (`_verificar_criterio`): un valor fuera del rango
    de sensibilidad se rechaza aqui y la corrida no empieza.

    El texto se interpreta con `ast.literal_eval` -- 1.5, (0.010, 0.013),
    'cota_terreno' -- y lo que no sea un literal de Python se toma como
    cadena, que es lo que declara un criterio categorico. No hay conversion
    de unidades ni default: lo que el usuario escribe es lo que se declara.
    """
    aplicadas = []
    for declaracion in declaraciones:
        clave, sep, texto = declaracion.partition("=")
        if not sep or not clave.strip():
            raise ValueError(
                f"--declarar {declaracion!r} no tiene la forma CLAVE=VALOR")
        clave, texto = clave.strip(), texto.strip()
        if not texto:
            # Sin esto, `ast.literal_eval("")` lanza SyntaxError, el texto cae
            # al respaldo y se declara la CADENA VACIA: un valor que nadie
            # quiso declarar entrando por la puerta de una errata.
            raise ValueError(
                f"--declarar {declaracion!r} no trae valor. Para retirar una "
                "declaracion no se declara vacio: se omite la bandera")
        try:
            valor_nuevo = ast.literal_eval(texto)
        except (ValueError, SyntaxError):
            valor_nuevo = texto
        ca.establecer_valor_dinamico(clave, valor_nuevo)
        aplicadas.append(clave)
    return aplicadas


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parser().parse_args(argv)

    try:
        declaradas = declarar_criterios(args.declaraciones)
    except (ValueError, KeyError) as exc:
        print(f"No se pudo declarar el criterio: {exc}", file=sys.stderr)
        return 2
    for clave in declaradas:
        print(f"Criterio declarado SOLO para esta corrida: {clave} = "
              f"{ca.valores_dinamicos()[clave]!r} "
              "(criterios_adoptados.py no se modifico)")

    banderas = {"luz_m": args.luz, "TW_m": args.TW,
                "longitud_m": args.longitud,
                "L_hidraulico_m": args.l_hidraulico,
                "categoria_tr": args.categoria_tr}
    try:
        externos = cargar_datos_externos(args.datos_externos, banderas)
        informe = correr(args.csv, externos, alcance=args.alcance)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"No se pudo leer la entrada: {exc}", file=sys.stderr)
        return 2
    except ErrorProyecto as exc:
        # Un fallo de carga: sin puntos no hay expediente que informar.
        print(f"El expediente no se puede cargar: {exc}", file=sys.stderr)
        return 2

    print(volcar(informe, con_criterios=args.criterios))

    destino = args.json_salida or args.csv.with_suffix(".informe.json")
    destino.write_text(
        json.dumps(informe_json(informe), ensure_ascii=False, indent=2,
                   allow_nan=False),
        encoding="utf-8")
    print(f"\nJSON del expediente: {destino}")

    plantilla = plantilla_por_alcance(args.alcance, args.plantilla)

    if args.html_salida is not None:
        ruta = exportar_html(informe, args.html_salida,
                             proyecto=args.proyecto,
                             ruta_plantilla=plantilla)
        print(f"Memoria de calculo (HTML): {ruta}")
        print(f"Plantilla usada          : {plantilla.name}")

    if args.pdf_salida is not None:
        salida = exportar_pdf(informe, args.pdf_salida,
                              proyecto=args.proyecto,
                              ruta_plantilla=plantilla)
        print(salida.mensaje)

    if args.csv_resumen_salida is not None:
        ruta = exportar_csv(informe, args.csv_resumen_salida)
        print(f"Cuadro resumen (CSV): {ruta}")

    return 0 if informe.cerrado else 1


if __name__ == "__main__":
    sys.exit(main())
