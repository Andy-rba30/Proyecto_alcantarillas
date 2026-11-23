"""
src/modelos/memoria.py
======================
Verificacion, traza de la memoria, bloqueos, contexto de corrida y fabricas de pasos.

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Mapping, Optional, Tuple

from src.modelos.errores import (
    CriterioPendienteError, DatoFaltanteError, DatoInvalidoError,
    DisenoNoFactibleError, LimiteNumericoError, MetodoNoEvaluableError
)

if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.errores import ErrorProyecto

class EstadoDeVerificacion(str, Enum):
    """
    EL ESTADO DE UNA VERIFICACION, con una sola fuente (PC-27, cierre del
    2026-09-22). Hasta aqui habia TRES capas que decian lo mismo sin que
    nada las atara: `Verificacion.cumple` (lo que lee el pipeline), el
    `TipoDeVeredicto` del `PasoDeMemoria` (lo que lee la memoria) y el
    `Bloqueo` (lo que no llego a evaluarse). PF-4 midio la grieta: una misma
    verificacion decia `cumple=True` al pipeline e INDICADOR a la memoria,
    a proposito, y nada impedia que dijera dos cosas incompatibles.

    Desde aqui `Verificacion.estado` ES la fuente, y las otras dos son
    vistas: `cumple` se deriva de el (`EstadoDeVerificacion.cumple`) y el
    veredicto del paso tiene que coincidir (`Verificacion.__post_init__` lo
    exige). Lo que NO llego a evaluarse no es un estado de aqui: sigue siendo
    un `Bloqueo`, porque no hay `Verificacion` que lo lleve. Cuatro valores:

        CUMPLE       se evaluo y pasa.
        NO_CUMPLE    se evaluo y no pasa: el punto se detiene.
        INDICADOR    se evaluo, el indicador se disparo, y un [A] declarado
                     decidio no detener el punto (PF-4, `regimen_v2b`).
        NO_APLICA    la fila existe en la tabla de la Fase 5 y en ESTE punto
                     no dice nada: V5 en la Familia C, SUSTITUIDA por VC1
                     (`M5.v5_no_aplica_en_canal`). No cuenta como
                     incumplida y la memoria lo imprime con esas palabras,
                     con el motivo al lado; hasta aqui la fila simplemente
                     no aparecia.
    """
    CUMPLE = "cumple"
    NO_CUMPLE = "no cumple"
    INDICADOR = "indicador"
    NO_APLICA = "no aplica"

    @property
    def cumple(self) -> bool:
        """La vista que lee el pipeline: solo NO_CUMPLE detiene el punto."""
        return self is not EstadoDeVerificacion.NO_CUMPLE

    @classmethod
    def de_veredicto(cls, tipo: "TipoDeVeredicto") -> Optional["EstadoDeVerificacion"]:
        """
        El estado que un veredicto de paso implica, o None si el veredicto
        no juzga (SIN_VEREDICTO) o no se evaluo (DIFERIDO, que es un
        `Bloqueo` y no un estado de verificacion).
        """
        return {
            TipoDeVeredicto.CUMPLE: cls.CUMPLE,
            TipoDeVeredicto.NO_CUMPLE: cls.NO_CUMPLE,
            TipoDeVeredicto.INDICADOR: cls.INDICADOR,
        }.get(tipo)


@dataclass(frozen=True)
class Verificacion:
    """
    Resultado de una verificacion de la Fase 5. Nunca se devuelve un bool
    desnudo: sin numeral, la memoria de calculo no es defendible.

    `estado` es LA FUENTE del resultado desde el cierre de PC-27; `cumple`
    sigue en la firma porque veinte constructores lo escriben, y desde aqui
    es una VISTA comprobada: `__post_init__` deriva el estado cuando no viene
    (del veredicto del paso, o de `cumple`) y rechaza con `ValueError` un
    `cumple` que no sea el del estado, o un veredicto del paso que diga otra
    cosa. `motivo_no_aplica` es obligatorio con NO_APLICA: una fila que «no
    aplica» sin decir por que es un hueco con otro nombre.

    `criterio_aplicado` es la clave de `criterios_adoptados.py` cuando el
    umbral proviene de un criterio [N->], [C] o [A]; None cuando el umbral es
    [N] puro y se lee de `constantes_normativas.py`.
    """

    cumple: bool
    numeral: str                          # "4.1.1.3.7 b)", "HDS-5 Ap. A", ...
    valor_obtenido: Any
    valor_admisible: Any
    criterio_aplicado: Optional[str]
    codigo: Optional[str] = None          # "V1" .. "V9" (Fase 5)
    # LA TRAZA DE LA MEMORIA, emitida por la propia funcion que verifica.
    #
    # Va aqui y no en un canal aparte porque es lo mismo que `cumple`: el
    # resultado de la verificacion. Lo que cambia es a quien se lo cuenta --
    # `cumple` al pipeline, `paso` al lector de la memoria -- y separarlos en
    # dos objetos permitiria que dijeran cosas distintas, que es exactamente
    # lo que pasaba cuando M11 reconstruia el relato leyendo resultados
    # (SIS-A-07).
    #
    # `None` NO significa "sin fundamentar": significa que esa verificacion
    # todavia no puede tener `Fundamento`, y la razon se censa en
    # `normativa.fundamentos.SIN_FUNDAMENTO` con lo que habria que transcribir
    # para traerla; M11 la imprime en el sitio del paso ausente, en vez de
    # dejar el hueco callado. El censo esta VACIO desde T-10: V5 y V8 salieron
    # en T-7b y V4b, V6 y V9 en T-10 (cuando el tope de V9 es de catalogo o
    # del marco su paso sustituye sin juzgar).
    paso: Optional["PasoDeMemoria"] = None
    estado: Optional[EstadoDeVerificacion] = None
    motivo_no_aplica: str = ""
    # --- verificacion de T-7 --- Lo que la verificacion tiene que decir en
    # voz alta SIN cambiar su veredicto: una carga que se acoto, una
    # aproximacion usada en su banda de cautela. No es un INDICADOR (el
    # veredicto sigue siendo el de la comparacion): es texto que
    # `InformePunto.avisos()` recoge de las verificaciones de la seccion
    # aceptada. V8 es su primer productor.
    avisos: Tuple[str, ...] = ()
    # --- VE-3.13 (decision 8 del dueño) --- True SOLO en un V1 que no
    # cumple porque el NIVEL DEL RECEPTOR deja al barril sin borde libre,
    # con el tirante PROPIO del caudal de diseño conservandolo, bajo la
    # lectura «no_cumple» de 'borde_libre_bajo_tw_ahogante'. Es lo que MD
    # necesita para decir que el diametro lo goberno el receptor y no el
    # caudal (`MD._descartado_solo_por_el_receptor`); V1 lo sabe y MD no
    # tiene que repetir su logica.
    descarta_solo_el_receptor: bool = False

    def __post_init__(self) -> None:
        veredicto = getattr(self.paso, "veredicto", None)
        derivado = (EstadoDeVerificacion.de_veredicto(veredicto.tipo)
                    if veredicto is not None else None)
        estado = self.estado
        if estado is None:
            if derivado is not None and derivado.cumple != bool(self.cumple):
                raise ValueError(
                    f"Verificacion {self.codigo or self.numeral}: el veredicto "
                    f"del paso dice «{veredicto.tipo.value}» y `cumple`="
                    f"{self.cumple!r}. La memoria y el pipeline tienen que "
                    "decir lo mismo (SIS-A-07, PC-27)")
            estado = derivado if derivado is not None else (
                EstadoDeVerificacion.CUMPLE if self.cumple
                else EstadoDeVerificacion.NO_CUMPLE)
            object.__setattr__(self, "estado", estado)
        if estado.cumple != bool(self.cumple):
            raise ValueError(
                f"Verificacion {self.codigo or self.numeral}: `cumple`="
                f"{self.cumple!r} no es la vista del `estado` "
                f"«{estado.value}». El estado es la fuente y `cumple` se "
                "deriva de el; dos valores que discrepan son la grieta de "
                "PC-27")
        if derivado is not None and derivado is not estado:
            raise ValueError(
                f"Verificacion {self.codigo or self.numeral}: el veredicto "
                f"del paso dice «{veredicto.tipo.value}» y el estado "
                f"«{estado.value}». La memoria y el pipeline tienen que "
                "decir lo mismo (SIS-A-07, PC-27)")
        if estado is EstadoDeVerificacion.NO_APLICA and \
                not str(self.motivo_no_aplica).strip():
            raise ValueError(
                f"Verificacion {self.codigo or self.numeral}: NO_APLICA sin "
                "`motivo_no_aplica`. Una fila que no aplica tiene que decir "
                "por que y que la sustituye")


# ===========================================================================
# La traza de la memoria (Sec. 4.4 del plan de correcciones v12)
# ---------------------------------------------------------------------------
# EL CAMBIO DE FONDO. Hasta S18 la memoria se RECONSTRUIA: M11 leia los
# resultados y volvia a armar el relato -- y, para poder armarlo, volvia a
# calcular (`y/D` en dos sitios, contra su propio docstring; SIS-A-07). Un
# reporte que recalcula es un segundo motor de calculo sin tests, y lo que
# imprime puede divergir de lo que el pipeline verifico sin que nada avise.
#
# A partir de aqui el calculo EMITE la traza y M11 la FORMATEA. `PasoDeMemoria`
# es la unidad de esa traza: los ocho campos de la §4.4, y cada uno responde a
# una pregunta que un revisor hace en voz alta delante de la memoria.
#
#     que              que se esta calculando
#     por_que          por que la norma obliga o recomienda hacerlo
#     formula          la expresion como la escribe la fuente, con su cita
#     sustitucion      los valores que entran, con unidad y PROCEDENCIA
#     resultado        el numero, con unidad y cifras declaradas
#     umbral           contra que se compara, con cita y CARACTER
#     veredicto        cumple / no cumple / diferido, con el margen
#     citas_textuales  las transcripciones literales que lo sostienen
#
# TRES REGLAS ESTAN EN LOS TIPOS, no en un test que alguien puede no correr:
#
#   1. `por_que` es obligatorio y no vacio. Un paso sin fundamento no se
#      construye. (Criterio de salida de la §4.4: "ningun PasoDeMemoria sin
#      por_que".)
#   2. Un `Umbral` sin `cita_id` no se construye. ("ningun umbral sin cita".)
#   3. Un veredicto de cumplimiento sin umbral no se construye: decir "cumple"
#      sin decir contra que es lo que hace indefendible una memoria.
#
# La cuarta -- que toda cita referenciada EXISTA en el registro -- no puede
# vivir aqui: este archivo no importa `normativa`, y no debe. La comprueba
# `modelos.paso()`, que si lo consulta, y la vuelve a comprobar el test sobre
# la memoria generada.
# ===========================================================================

# DECIMALES DE PRESENTACION de la traza. Son de la misma naturaleza que los
# `FMT_*` de M11 -- cuantos decimales se imprimen -- y por eso no son valores
# de proyecto: `Magnitud` guarda el float entero y `cifras` solo dice como
# escribirlo. Viven aqui, con nombre y una sola vez, en lugar de repetirse
# como enteros sueltos en cada llamada de cada modulo de calculo: asi el
# barrido de literales tiene tres lineas que mirar y no ochenta.
CIFRAS_MAGNITUD = 3        # literal-ok: decimales de presentacion; no entra en ningun calculo
# Cuatro para la PENDIENTE y para n: con tres, una S de 0.0006 se imprime
# 0.001 y la caida S*L deja de poder recomputarse desde la memoria, que es
# justo lo que esas filas existen para permitir (MAT-D9). Es la misma razon
# por la que M11 tiene un FMT_4.
CIFRAS_FINA = 4            # literal-ok: decimales de presentacion; no entra en ningun calculo
CIFRAS_FACTOR = 2          # el 2 y el 1 no necesitan marca: la regla los exime
CIFRAS_PORCENTAJE = 1


def cifras_de_dimension(valor: float) -> int:
    """
    Los decimales con que la memoria escribe una dimension de seccion: los
    de `texto_de_dimension`, para el campo `cifras` de una `Magnitud`.

    --- VE-5 (ficha VE1-01, abierto) --- hasta VE-5 las magnitudes `D`, `B`
    y `H` de los pasos de la memoria salian con `CIFRAS_FACTOR` fijo: con la
    serie de 6 in, el rotulo decia «Ø 1.0668 m» (VE-1, H1) y la sustitucion
    del mismo paso «D = 1.07 m». Una sola regla para el rotulo y para la
    sustitucion. Presentacion: no redondea el valor con que se calcula.
    """
    from decimal import Decimal

    if not math.isfinite(valor):
        return CIFRAS_FACTOR
    return max(CIFRAS_FACTOR, -Decimal(repr(float(valor))).as_tuple().exponent)


def texto_de_dimension(valor: float) -> str:
    """
    Una dimension de seccion, en metros, como la ROTULA la memoria: con
    `CIFRAS_FACTOR` decimales como minimo y con TODOS los que el numero
    declarado tenga (Sec. 3.2; VE-1, hallazgo H1 de su revision).

        0.9 -> «0.90»     1.05 -> «1.05»     1.0668 -> «1.0668»

    POR QUE NO DOS FIJOS. El rotulo nombra el PRODUCTO, y con dos decimales
    la serie de 6 in de 'diametros_normalizados' se leia «Ø 1.07 m» y
    «Ø 1.22 m» en el JSON, la memoria y el CSV de resumen mientras el calculo
    corria con 1.0668 y 1.2192: el lector veia un diametro que nadie
    declaro. Los decimales salen de la forma decimal mas corta del float
    (`repr`, la que lo reproduce exacto), que para un escalon de la serie es
    la que se declaro (`M2._escalon_de_la_serie`). Con la progresion de
    archivo y el marco de la linea base el texto es el de siempre.

    Un valor no finito se escribe como antes, con `CIFRAS_FACTOR` («nan»).
    """
    return f"{valor:.{cifras_de_dimension(valor)}f}"


# Alcance de la corrida. Rotulos, no valores de proyecto: con "expediente"
# (el defecto) todo corre como siempre; con "perfil" V5 y V8 se INTENTAN pero
# su fallo se difiere, y las Fases 8 y 9 no se ejecutan.
#
# VIVEN AQUI DESDE S18, y no en `cli.py`, porque dejaron de ser de la CLI:
# M11 los necesita para decidir que va dentro de `bloque_pendientes` (el
# volcado de los Tableros 1-2-3 es de la corrida de expediente), y M11 no
# puede importar `cli` --- es `cli` quien importa M11 ---. La alternativa era
# que M11 llevara su propia copia de las dos cadenas, que es como nacen las
# dos fuentes de verdad que este proyecto persigue: `bloque_acotaciones` ya
# comparaba contra un "expediente" escrito a mano.
ALCANCE_PERFIL = "perfil"
ALCANCE_EXPEDIENTE = "expediente"

# LOS DOS NIVELES DE ENTREGA. No son etiquetas de la taxonomia de CLAUDE.md
# (esas son [N], [N->], [S], [C], [A]) ni fases del calculo: dicen a que
# ENTREGA pertenece un criterio o un dato de sitio. Un estudio de PERFIL
# cierra con los primeros declarados; los segundos son del expediente
# tecnico, y `--alcance perfil` difiere sus etapas con su fundamento.
#
# VIVEN AQUI DESDE EXT-10, y no en `criterios_adoptados.py` donde nacieron
# (S20), porque desde EXT-10 los lleva tambien `DatoSitio.nivel`:
# `criterios_adoptados` importa `datos_sitio` y `datos_sitio` no puede
# importar `criterios_adoptados`, de modo que el unico hogar comun es este.
# `criterios_adoptados` los reexporta con los mismos nombres (`ca.NIVEL_PERFIL`),
# que es como los leen la GUI, `variables_entrada` y la suite.
NIVEL_PERFIL = "perfil"
NIVEL_EXPEDIENTE = "expediente"
NIVELES = (NIVEL_PERFIL, NIVEL_EXPEDIENTE)


class TipoDeVeredicto(str, Enum):
    """
    CUATRO estados, y el cuarto no es relleno. Un paso puede calcular sin
    juzgar --el tirante normal es un numero, no un aprobado-- y forzarlo a
    "cumple" o "no cumple" obligaria a inventarle un umbral, que es la forma
    exacta de la cita falsa que este proyecto viene retirando.

    DIFERIDO es distinto de NO_CUMPLE y de SIN_VEREDICTO: la verificacion
    existe, tiene umbral y no se evaluo. Dos razones, y el `Bloqueo` del
    punto dice cual: porque el alcance de la corrida la dejo fuera
    (`--alcance perfil`), o porque el METODO disponible no la puede evaluar
    ahi (`MetodoNoEvaluableError`, EXT-3: el paso F4.HO bajo control de
    salida con HW/D < 0.75, hasta E-A). Imprimirla como "cumple" seria mentir
    y como "no cumple" tambien: hasta EXT-3 el paso de h_o decia NO_CUMPLE
    mientras el pipeline aceptaba el punto CON ESE HW, que es la divergencia
    que SIS-A-07 prohibe.

    NO_CUMPLE SOBRE UNA CONDICION DE USO DE UN METODO (E-A) no es esa
    divergencia, y conviene decirlo porque se parece: los pasos F4.HO (bajo
    HW/D < 0.75) y F4.PERFIL 4.3c (barril que no va lleno en la mayor parte)
    juzgan la condicion que la fuente pone a la APROXIMACION de h_o, no al
    diseño. Cuando dicen NO_CUMPLE, el paso dice ademas que hace el pipeline
    con ello --usa el remanso, o conserva la aproximacion porque la pag. 3.12
    la avala hasta 0.75D--, y el punto no se rechaza porque ninguna exigencia
    sobre el diseño se incumple: `ResultadoPunto.verificaciones_incumplidas`
    lee las `Verificacion`, no los pasos. Memoria y pipeline dicen lo mismo:
    «esta condicion del metodo no se cumple, y por eso el HW es este».

    INDICADOR (PF-4) ES EL QUINTO, Y ES UN VALOR DE ESTA CAPA, NO UNA CAPA
    NUEVA. PC-27 («Cerrado parcial») deja escrito que el estado de
    verificacion ya vive en tres capas que no se reducen entre si --
    `Verificacion.cumple: bool`, este enum adosado al `PasoDeMemoria`, y
    `Bloqueo` -- y que formalizar sin decidir cual gobierna produce una
    cuarta. PF-4 no la produce: `cumple` sigue siendo el bool que lee la
    compuerta de MD (`all(v.cumple ...)`) y `Bloqueo` no se toca. Lo que hace
    falta es que ESTA capa pueda decir una cosa que ninguno de los cuatro
    valores anteriores decia sin mentir: «la comparacion se evaluo, el
    indicador que la fuente nombra SE DISPARO, y el proyecto decidio --por un
    criterio [A] declarado, `regimen_v2b` = indicador_con_aviso-- no detener
    el punto por ello». CUMPLE mentiria (el indicador se disparo); NO_CUMPLE
    haria divergir la memoria del pipeline, que acepta el punto (SIS-A-07,
    el mismo defecto que EXT-3 corrigio en F4.HO); DIFERIDO es «no se
    evaluo» y aqui se evaluo; SIN_VEREDICTO es «no juzga» y aqui se juzgo
    contra un umbral. Por eso INDICADOR exige umbral igual que CUMPLE y
    NO_CUMPLE (`PasoDeMemoria.__post_init__`), y M11 lo pinta como AVISO --
    ni incumple ni diferido--. `Veredicto.cumple` sigue diciendo solo
    CUMPLE: un indicador disparado no «cumple», aunque el punto no se
    detenga; esa propiedad no tiene consumidor de produccion (medido por
    grep en PF-4) y se deja como esta. La fuente que lo sostiene es la que
    lo nombra asi: HDS-5 3.a ed. num. 5.3.3, «are key indicators of
    potential problems», `caracter` DEFINICION, sin umbral ni «shall».
    """

    CUMPLE = "cumple"
    NO_CUMPLE = "no cumple"
    DIFERIDO = "diferido"
    SIN_VEREDICTO = "sin veredicto"
    INDICADOR = "indicador"


class TipoDeBloqueo(str, Enum):
    """
    Por que una etapa no se completo. Hasta EXT-3 `cli.Bloqueo.tipo` era un
    `str` libre que valia `type(exc).__name__` o el literal "DiferidoPorAlcance"
    escrito en tres sitios (PC-27). Los VALORES son esos mismos textos, a
    proposito: la linea base, el JSON y los tests que comparan
    `b.tipo == "CriterioPendienteError"` siguen leyendo lo mismo.

    Cinco son excepciones del expediente (`de_excepcion` las traduce), el
    sexto es una decision de la corrida y no una excepcion.
    """
    CRITERIO_PENDIENTE = "CriterioPendienteError"
    DISENO_NO_FACTIBLE = "DisenoNoFactibleError"
    DATO_FALTANTE = "DatoFaltanteError"
    DATO_INVALIDO = "DatoInvalidoError"
    LIMITE_NUMERICO = "LimiteNumericoError"
    METODO_NO_EVALUABLE = "MetodoNoEvaluableError"
    DIFERIDO_POR_ALCANCE = "DiferidoPorAlcance"

    @classmethod
    def de_excepcion(cls, exc: ErrorProyecto) -> "TipoDeBloqueo":
        """El tipo de bloqueo que corresponde a una excepcion del expediente."""
        for clase, tipo in _TIPO_DE_BLOQUEO_POR_CLASE:
            if isinstance(exc, clase):
                return tipo
        raise TypeError(
            f"{type(exc).__name__} no es una excepcion del expediente con "
            f"tipo de bloqueo: la taxonomia de ErrorProyecto y "
            f"TipoDeBloqueo tienen que crecer juntas")


_TIPO_DE_BLOQUEO_POR_CLASE = (
    (CriterioPendienteError, TipoDeBloqueo.CRITERIO_PENDIENTE),
    (DisenoNoFactibleError, TipoDeBloqueo.DISENO_NO_FACTIBLE),
    (DatoFaltanteError, TipoDeBloqueo.DATO_FALTANTE),
    (DatoInvalidoError, TipoDeBloqueo.DATO_INVALIDO),
    (LimiteNumericoError, TipoDeBloqueo.LIMITE_NUMERICO),
    (MetodoNoEvaluableError, TipoDeBloqueo.METODO_NO_EVALUABLE),
)


@dataclass(frozen=True)
class Bloqueo:
    """
    Una etapa que no se pudo completar, con la causa del expediente.

    VIVE AQUI DESDE EXT-3, y antes en `cli.py` «a proposito» porque no fluia
    entre modulos de calculo. Dejo de ser cierto cuando el estado
    «pendiente / diferido / no evaluable» paso a ser un estado del DOMINIO y
    no de la capa de reporte (PC-27): lo producen la Fase 5 y el bucle de MD
    (`MetodoNoEvaluableError`), lo leen la CLI, la GUI y M11, y una misma
    clase con `tipo` cerrado es lo que impide que cada capa escriba el suyo.
    `InformePunto` e `Informe` siguen en `cli.py`: esos si son la forma del
    reporte.

    `criterio` esta relleno solo cuando la causa es un criterio pendiente: es
    la clave que hay que declarar para desbloquear la etapa. `campo` cuando
    falta o esta mal un dato. `delta_rasante_m` cuando el diseño no es
    factible y 7.A pudo decir cuanto subir la rasante.
    """

    fase: str
    etapa: str
    tipo: TipoDeBloqueo
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
    # constancia -- pero no cuenta para `Informe.cerrado`. Un
    # METODO_NO_EVALUABLE lo lleva en True solo a nivel de perfil (v8 §4.3).
    diferido_por_alcance: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.tipo, TipoDeBloqueo):
            raise TypeError(
                f"Bloqueo.tipo tiene que ser un TipoDeBloqueo, no "
                f"{self.tipo!r}: el texto libre es lo que PC-27 retiro")


@dataclass(frozen=True)
class ObstaculoAnticipado:
    """
    Lo que DETENDRIA una etapa, anticipado sin correrla (VE-4b, ficha T1-04):
    el `Bloqueo` que la corrida registraria, antes de que exista.

    Lo produce el estimador de la Fase 1-bis (`MH_hidrologia.anticipar_caudal`
    y `servicio.anticipar_fase_hidrologia`) y lo lee el pre-vuelo
    (`anticipo.datos_faltantes_por_punto`). Se construye desde la MISMA
    excepcion que la etapa levantaria (`de_excepcion`), de modo que `tipo` y
    `mensaje` son los del `Bloqueo` real: el texto no se escribe dos veces.

    `dato` es lo que hay que tocar: la clave del criterio, el campo que falta
    o esta mal, o la magnitud que el metodo no evalua (`que` de
    `MetodoNoEvaluableError`). `depende_del_tr` marca la compuerta que solo
    se decide con el periodo de retorno de la Fase 2, que el pre-vuelo no
    calcula: entonces el `mensaje` dice la condicion y no el numero, y el
    pre-vuelo la anuncia como «puede detener» (estima de MAS a proposito).
    """

    dato: str
    tipo: TipoDeBloqueo
    mensaje: str
    depende_del_tr: bool = False

    @classmethod
    def de_excepcion(cls, exc: ErrorProyecto, dato: str, *,
                     depende_del_tr: bool = False) -> "ObstaculoAnticipado":
        return cls(dato=dato, tipo=TipoDeBloqueo.de_excepcion(exc),
                   mensaje=str(exc), depende_del_tr=depende_del_tr)


@dataclass(frozen=True)
class DatoEfectivoDeSitio:
    """
    Lo que un dato de sitio [S] APORTO a una corrida, y de donde (EXT-10).

    Es la mitad de ESTADO de un `DatoSitio`, y solo esa: el valor con que
    gobierno, la trazabilidad de ESA lectura, la fecha en que se declaro y
    el archivo del que salio (`datos_sitio.py`, o el `sitio.json` / la sesion
    de otra obra). La otra mitad --- concepto, procedimiento, fuente, ambito
    --- es del ARCHIVO y la capa de reporte la sigue leyendo de `ds.dato`,
    que es una lectura estatica. No es un segundo `DatoSitio`: es lo que
    `ContextoCorrida.valores_efectivos` es para los criterios, con los tres
    campos que un [S] lleva ademas del valor porque se defiende con
    trazabilidad y no con rango.
    """

    valor: Any
    trazabilidad: str
    fecha: str
    origen: str
    declarado_en_caliente: bool


@dataclass(frozen=True)
class ContextoCorrida:
    """
    LA FOTO DEL ESTADO CON QUE CORRIO EL EXPEDIENTE, tomada por `servicio.correr`
    al salir y colgada del `Informe` (EXT-A-01, PC-09; EXT-4).

    Por que existe. Los tres archivos de valores llevan estado de PROCESO:
    el registro de usos (`criterios_adoptados._USADOS`, `datos_sitio._USADOS`),
    las declaraciones en caliente (`_OVERRIDES`) y el libro de procedencias
    (`declaracion._PROCEDENCIAS`). Hasta EXT-4 los cuatro exportadores ---
    `informe_json`, `volcar`, la memoria HTML y la trazabilidad --- los leian
    AL EXPORTAR, en 39 sitios medidos. Con un proceso de un solo uso (la CLI)
    daba igual; con la GUI, o con cualquier consumidor que reutilice el
    proceso, la memoria de una corrida imprimia lo que otra corrida uso, lo
    que se declaro DESPUES de correr, y el SHA-1 del CSV que hay en disco al
    exportar y no del que se leyo. Una memoria que afirma algo falso sobre su
    propia corrida es el peor defecto que puede tener este proyecto.

    Que lleva, y por que cada cosa:

    - `criterios_usados`, `datos_usados`: lo que ESTA corrida invoco. El
      registro se vacia al entrar en `servicio.correr` y se fotografia al salir.
    - `valores_efectivos`: el valor con que gobierno cada criterio del
      catalogo, copiado EN PROFUNDIDAD --- un dict declarado en caliente y
      mutado despues no puede mover la memoria de una corrida que ya paso ---.
    - `procedencias`: el libro de `declaracion` tal como estaba, por clave.
    - `declarados_en_caliente`, `pisados_en_caliente`: las dos listas que la
      memoria imprime en bloques distintos (tantear no es falsear).
    - `criterios_sin_valor`, `criterios_opcionales_sin_declarar`,
      `criterios_con_verificacion_pendiente`: las tres listas derivadas que
      `criterios_adoptados` calcula sobre el estado vivo, calculadas ENTONCES
      y no al exportar.
    - `csv_sha1`: de los MISMOS BYTES que M0 leyo, no del archivo en disco.
    - `criterios_sha1`: la huella del archivo de criterios al correr.
    - `datos_efectivos`, `datos_declarados_en_caliente`,
      `datos_pisados_en_caliente`, `datos_sin_valor` (EXT-10): los datos de
      sitio con que gobierno la corrida y de que archivo salio cada uno.
    - `cuencas_sha1`, `estacion_sha1` (UI-1): las huellas de las dos
      entradas de la hidrologia, de los bytes que se parsearon; None sin
      hidrologia.

    Que NO lleva: nada que sea del ARCHIVO y no del estado --- concepto,
    fuente, justificacion, etiqueta, sensibilidad ---, que la capa de reporte
    sigue leyendo del catalogo (`ca.criterio`, `ds.dato`): son lecturas
    estaticas, y `tests/test_ext4_contexto_corrida.py` barre el AST de M11
    para que sean las unicas.

    Es `frozen` y vive aqui, en modelos.py, porque fluye entre la corrida y
    las tres capas que la publican. Si un dia la GUI corre en hilo, el mismo
    almacen pasa a `contextvars` sin tocar M2-M10: los 79 escritores de uso
    pasan por tres funciones.
    """

    criterios_usados: Tuple[str, ...]
    datos_usados: Tuple[str, ...]
    valores_efectivos: Mapping[str, Any]
    procedencias: Mapping[str, Any]
    declarados_en_caliente: Tuple[str, ...]
    pisados_en_caliente: Tuple[str, ...]
    criterios_sin_valor: Tuple[str, ...]
    criterios_opcionales_sin_declarar: Tuple[str, ...]
    criterios_con_verificacion_pendiente: Tuple[str, ...]
    csv_sha1: str
    criterios_sha1: str
    # LOS DATOS DE SITIO EFECTIVOS (EXT-10, EXT-V-01). Hasta EXT-10 la foto
    # solo llevaba `datos_usados`, porque un [S] no tenia mas estado que el
    # uso: su valor era el del archivo. Desde que un [S] de OTRA OBRA puede
    # entrar por sesion (`datos_sitio.establecer_dato_dinamico`), el valor,
    # la trazabilidad, la fecha y el ORIGEN con que gobierno cada dato son
    # estado de la corrida, y viajan aqui con la misma regla que los
    # criterios: se fotografian al salir y ningun exportador los lee del
    # registro vivo. `datos_sin_valor` tambien es foto: una sesion puede
    # rellenar un [S] vacio del archivo, y la lista cambia con el estado.
    datos_efectivos: Mapping[str, "DatoEfectivoDeSitio"]
    datos_declarados_en_caliente: Tuple[str, ...]
    datos_pisados_en_caliente: Tuple[str, ...]
    datos_sin_valor: Tuple[str, ...]
    # LAS HUELLAS DE LAS DOS ENTRADAS DE LA HIDROLOGIA (UI-1, ficha T1-04),
    # con la misma regla que `csv_sha1`: de los MISMOS bytes que el cargador
    # parseo (`EntradaHidrologica.cuencas_sha1`), no del archivo que haya en
    # disco al exportar. None cuando la corrida no trajo `--cuencas` ni
    # `--estacion`: entonces la memoria y el JSON no imprimen nada de ellas y
    # la linea base no cambia.
    cuencas_sha1: Optional[str] = None
    estacion_sha1: Optional[str] = None
    # --- dictamen Fable (VE-7 lote A, A2) --- LOS CRITERIOS QUE UN PUNTO
    # PISO PARA SI (`embocadura_cajon_del_punto`): {criterio: {id_punto:
    # valor}}. Sin ellos la tabla de criterios diria, para esos puntos, el
    # valor de proyecto con que NO corrieron. Vacio por defecto.
    criterios_por_punto: Mapping[str, Mapping[str, Any]] = \
        MappingProxyType({})

    def __post_init__(self) -> None:
        # `frozen` solo impide REASIGNAR los campos; un dict dentro seguia
        # siendo mutable y `informe.contexto.valores_efectivos[k] = x` movia
        # el JSON y el HTML de una corrida ya pasada sin excepcion (auditoria
        # adversarial de EXT-4). Los mapas quedan de solo lectura y las
        # secuencias, tuplas: la foto no se puede retocar, ni a proposito.
        object.__setattr__(self, "criterios_por_punto", MappingProxyType({
            k: MappingProxyType(dict(v))
            for k, v in dict(self.criterios_por_punto).items()}))
        for campo in ("valores_efectivos", "procedencias", "datos_efectivos"):
            valor = getattr(self, campo)
            if not isinstance(valor, MappingProxyType):
                object.__setattr__(self, campo, MappingProxyType(dict(valor)))
        for campo in ("criterios_usados", "datos_usados",
                      "declarados_en_caliente", "pisados_en_caliente",
                      "criterios_sin_valor", "criterios_opcionales_sin_declarar",
                      "criterios_con_verificacion_pendiente",
                      "datos_declarados_en_caliente", "datos_pisados_en_caliente",
                      "datos_sin_valor"):
            object.__setattr__(self, campo, tuple(getattr(self, campo)))

    def declarado_en_caliente(self, clave: str) -> bool:
        """True si el valor que GOBERNO esa corrida entro en caliente."""
        return clave in self.declarados_en_caliente

    def dato_efectivo(self, clave: str) -> "DatoEfectivoDeSitio":
        """El dato de sitio TAL COMO GOBERNO esa corrida, con su origen."""
        return self.datos_efectivos[clave]

    def dato_declarado_en_caliente(self, clave: str) -> bool:
        """True si el [S] que goberno esa corrida entro por sesion."""
        return clave in self.datos_declarados_en_caliente

    def valor_efectivo(self, clave: str) -> Any:
        """El valor con que gobierno el criterio en esa corrida."""
        return self.valores_efectivos[clave]

    def procedencia_de(self, clave: str) -> Optional[Any]:
        """La procedencia registrada de la clave en esa corrida, o None."""
        return self.procedencias.get(clave)

    @staticmethod
    def de(informe: Any) -> "ContextoCorrida":
        """
        El contexto de un informe, o un error que dice que el informe no lo
        lleva. Solo `servicio.correr` lo produce: un `Informe` armado a mano no
        tiene corrida que describir, y exportarlo leyendo el estado vivo
        seria exactamente el defecto que este objeto cierra.
        """
        contexto = getattr(informe, "contexto", None)
        if not isinstance(contexto, ContextoCorrida):
            raise ValueError(
                "el informe no lleva ContextoCorrida: solo servicio.correr lo "
                "produce, y sin el la capa de reporte no puede decir con que "
                "estado corrio el expediente")
        return contexto


@dataclass(frozen=True)
class Magnitud:
    """
    Un numero de la memoria con las tres cosas que lo hacen rastreable: su
    unidad, sus cifras y DE DONDE SALIO.

    `procedencia` es obligatoria y es la mitad que faltaba. "V = 2.31 m/s" y
    "V = 2.31 m/s, de M3 por Manning con la rama de n maximo" son la misma
    linea en la pagina y no son la misma informacion: la primera obliga al
    revisor a abrir el codigo, que es justo lo que el criterio de salida de la
    §4.4 prohibe.

    `cifras` es de PRESENTACION: cuantos decimales se imprimen. No redondea el
    valor almacenado -- el calculo sigue con el float entero -- y por eso no
    es un valor de proyecto.
    """

    simbolo: str
    valor: Any
    unidad: str
    procedencia: str
    cifras: Optional[int] = None

    def __post_init__(self) -> None:
        if not str(self.simbolo).strip():
            raise ValueError("Magnitud sin simbolo: no se puede citar")
        if not str(self.procedencia).strip():
            raise ValueError(
                f"Magnitud «{self.simbolo}» sin procedencia. La §4.4 exige "
                "que la sustitucion diga de donde sale cada valor; un numero "
                "sin origen es el que obliga a abrir el codigo")

    @property
    def texto(self) -> str:
        """El valor con su unidad, como lo imprime la memoria."""
        v = self.valor
        if isinstance(v, float) and math.isfinite(v) and self.cifras is not None:
            texto = f"{v:.{self.cifras}f}"
        elif isinstance(v, float) and not math.isfinite(v):
            texto = "no finito"
        else:
            texto = str(v)
        return f"{texto} {self.unidad}".strip()


@dataclass(frozen=True)
class Umbral:
    """
    Contra que se compara un resultado, con su cita y con su CARACTER.

    `cita_id` es obligatorio: es la regla 2 de arriba y el corazon de
    NOR-MEM-01. Un umbral sin cita es un numero que la memoria presenta como
    normativo sin poder decir de donde sale.

    `caracter` y `aplicacion` van SEPARADOS a proposito. El primero es lo que
    la FUENTE hace con el numero (exigencia, recomendacion, aproximacion); el
    segundo es lo que el PROYECTO hace con el. Los dos coinciden casi siempre,
    y donde no coinciden esta lo unico que hay que declarar: el 0.25 m/s de V2
    y el 0.75 de V1 los RECOMIENDA el Manual y este proyecto los aplica como
    umbral duro por decision conservadora propia (NOR-MEM-01, MAT-O13).
    Fundirlos en un campo es como se fabrica una exigencia que la norma no
    escribio.
    """

    descripcion: str
    valor: Any
    unidad: str
    cita_id: str
    caracter: str
    aplicacion: str
    criterio_aplicado: Optional[str] = None

    def __post_init__(self) -> None:
        if not str(self.cita_id).strip():
            raise ValueError(
                f"Umbral «{self.descripcion}» sin `cita_id`. La §4.4 exige "
                "que todo umbral de aceptacion lleve la frase de la fuente "
                "que lo fija; sin id no hay frase que buscar en el registro")
        if not str(self.aplicacion).strip():
            raise ValueError(
                f"Umbral «{self.descripcion}» sin `aplicacion`: hay que decir "
                "que hace el proyecto con el, que es lo que separa una "
                "recomendacion aplicada como dura de una exigencia")


@dataclass(frozen=True)
class Veredicto:
    """
    El resultado del contraste, con el MARGEN.

    El margen es lo que convierte "cumple" en informacion: un punto que pasa
    por 0.002 y otro que pasa por 0.4 se imprimen igual sin el, y no son el
    mismo diseno.
    """

    tipo: TipoDeVeredicto
    margen: Optional[float] = None
    unidad: str = ""
    explicacion: str = ""

    @property
    def cumple(self) -> bool:
        return self.tipo is TipoDeVeredicto.CUMPLE


@dataclass(frozen=True)
class EleccionDeProyecto:
    """
    La PROCEDENCIA de una eleccion, que es la regla R1 del plan v12: «se
    adopto X, elegido entre X1...Xn de la Tabla T (numeral N, pag. P), por la
    razon R».

    `entre` no es decorado: es lo que da sentido al analisis de sensibilidad.
    Sin las alternativas, el rango declarado de un criterio [A] es un par de
    numeros sueltos al pie de una ficha -- que es como estaba, consumido solo
    por los tests (SIS-B-05).

    `de_donde` es texto legible y `cita_id` el ancla al registro. `cita_id`
    queda VACIO a proposito cuando la eleccion no sale de una norma: un tope
    de catalogo no tiene numeral, y ponerle uno seria la cita falsa que
    NOR-PRO-01 y NOR-PRO-02 retiraron. Por eso el vacio esta permitido aqui y
    prohibido en `Umbral`.

    `fundamento_id` ES OPCIONAL Y NO DEBERIA SERLO, y conviene decir por que
    esta a medias en vez de dejarlo como si fuera una eleccion de diseno. La
    §4.5 de la constitucion prohibe escribir el `por_que` en el modulo que
    calcula -- sale de un `Fundamento`, cuyo verbo el registro contrasta
    contra el `caracter` de sus citas --, y `PasoDeMemoria` lo cumple porque
    `paso()` es su unica puerta. `EleccionDeProyecto` NO lo cumple: sus
    `por_que` se escriben a mano en los modulos, uno por uno, y ninguno pasa
    por T11. C7 abre la puerta que faltaba -- `eleccion()`, aqui al lado -- y
    la usa en el unico sitio donde el `por_que` estaba diciendo algo que la
    fuente no sostiene (la fila de gamma_p de V7, F5.V7_FILA). Migrar los
    demas es trabajo aparte y no de esta sesion; mientras tanto el campo vacio
    es la marca legible de cuales faltan.
    """

    que_se_adopto: str
    valor: Any
    entre: Tuple[str, ...]
    de_donde: str
    por_que: str
    cita_id: str = ""
    clave_criterio: str = ""
    fundamento_id: str = ""

    def __post_init__(self) -> None:
        if not str(self.por_que).strip():
            raise ValueError(
                f"EleccionDeProyecto «{self.que_se_adopto}» sin `por_que`. La "
                "R1 pide las tres cosas: que se eligio, entre que, y por que")

    @property
    def texto(self) -> str:
        entre = ", ".join(str(x) for x in self.entre)
        alternativas = f", elegido entre {entre}" if entre else ""
        de = f" de {self.de_donde}" if self.de_donde else ""
        return (f"se adopto {self.que_se_adopto} = {self.valor}"
                f"{alternativas}{de}, por: {self.por_que}")


@dataclass(frozen=True)
class PasoDeMemoria:
    """
    Un paso de la memoria, emitido por la funcion que lo calcula.

    No es un registro de depuracion ni una traza de ejecucion: es el parrafo
    de la memoria, con sus numeros ya atados a su fuente, escrito por quien
    tiene delante los valores. Por eso lo emite el calculo y no el reporte --
    M11 no puede saber de donde salio un numero que le llega suelto.
    """

    que: str
    por_que: str
    formula: str
    sustitucion: Tuple[Magnitud, ...]
    resultado: Magnitud
    umbral: Optional[Umbral] = None
    veredicto: Optional[Veredicto] = None
    citas_textuales: Tuple[str, ...] = ()
    fundamento_id: str = ""
    formula_cita_id: str = ""
    elecciones: Tuple[EleccionDeProyecto, ...] = ()
    fase: str = ""
    codigo: str = ""
    nota_del_proyecto: str = ""
    # LAS DISCREPANCIAS QUE ESTE PASO TOCA POR SU VALOR Y NO POR SU CITA.
    #
    # La mayoria de las discrepancias llegan solas a la memoria: el registro
    # cruza las citas que el paso imprime contra las `Parte.cita_id` que la
    # discrepancia ya declara (`Registro.discrepancias_que_tocan`). Este
    # campo es para las que hablan de un NUMERO que el paso sustituye y no de
    # un texto que el paso cita -- `DIS-HR-G-LAUSHEY` es sobre el valor
    # `G_LAUSHEY = 9.8`, `DIS-HR-D-MAX` sobre los topes de catalogo --, donde
    # el cruce por cita no las alcanza.
    #
    # No es una lista de ids sueltos: el registro comprueba que cada uno
    # exista, y M11 imprime la discrepancia entera desde el registro, de modo
    # que aqui viaja el ID Y NUNCA EL TEXTO. Escribir aqui la discrepancia en
    # prosa seria la segunda transcripcion que la §4.5 prohibe -- y es
    # exactamente como llegaban a la memoria las dos que llegaban antes de
    # C8: con el id escrito a mano dentro de la justificacion de un criterio.
    discrepancias: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not str(self.que).strip():
            raise ValueError("PasoDeMemoria sin `que`")
        if not str(self.por_que).strip():
            raise ValueError(
                f"PasoDeMemoria «{self.que}» sin `por_que`. Es la regla 1 de "
                "la §4.4 y no admite excepcion: el fundamento se declara en "
                "`normativa/fundamentos.py` y se trae con `modelos.paso()`, "
                "nunca se escribe suelto en el modulo de calculo")
        # INDICADOR entra en la lista desde PF-4: decir que un indicador se
        # disparo sin decir contra que es tan indefendible como un «cumple»
        # sin umbral.
        if self.veredicto is not None and self.umbral is None and \
                self.veredicto.tipo in (TipoDeVeredicto.CUMPLE,
                                        TipoDeVeredicto.NO_CUMPLE,
                                        TipoDeVeredicto.INDICADOR):
            raise ValueError(
                f"PasoDeMemoria «{self.que}»: veredicto "
                f"«{self.veredicto.tipo.value}» sin umbral. Decir que algo "
                "cumple sin decir contra que es lo que hace indefendible una "
                "memoria")
        if self.umbral is not None and \
                self.umbral.cita_id not in self.citas_textuales:
            raise ValueError(
                f"PasoDeMemoria «{self.que}»: la cita del umbral "
                f"«{self.umbral.cita_id}» no esta en `citas_textuales`. El "
                "umbral y su frase se imprimen juntos o el revisor lee el "
                "numero sin la frase que lo fija")

    @property
    def juzga(self) -> bool:
        """True si el paso contrasta contra un umbral."""
        return self.umbral is not None


@lru_cache(maxsize=1)
def _registro_normativo():
    """
    El registro, armado una sola vez. Mismo patron y misma razon que
    `criterios_adoptados._registro`: `paso()` lo consulta en cada llamada y
    reconstruirlo por paso convertiria la traza en el cuello de botella del
    pipeline.
    """
    from src.normativa import registro as _rn

    return _rn.construir()


def paso(fundamento_id: str, **kw: Any) -> PasoDeMemoria:
    """
    Construye un `PasoDeMemoria` trayendo el `por_que` del registro.

    ES LA UNICA PUERTA que los modulos de calculo usan, y por eso el `por_que`
    no se puede escribir a mano en un modulo: sale del `Fundamento`, que a su
    vez esta atado a sus citas y a su verbo por la invariante T11. Escribirlo
    suelto permitiria redactar «la norma obliga» encima de un parrafo que
    recomienda, que es el defecto que NOR-MEM-01 y MAT-O13 dejaron por escrito.

    El import del registro es DIFERIDO, igual que en
    `criterios_adoptados.tabla_del_criterio`: `modelos.py` no depende de
    `normativa` en su cabecera y no debe -- es el tipo que fluye entre modulos,
    y la regla de dependencias del registro pone a `normativa` a la izquierda
    de todo.

    Comprueba ademas que toda cita referenciada EXISTA: es la unica de las
    cuatro reglas de la §4.4 que este archivo no puede poner en un
    `__post_init__`.
    """
    reg = _registro_normativo()
    f = reg.fundamento(fundamento_id)
    citas = tuple(kw.pop("citas_textuales", ()) or ())
    umbral = kw.get("umbral")
    if umbral is not None and umbral.cita_id not in citas:
        citas = (umbral.cita_id,) + citas
    for cita_id in citas:
        reg.cita(cita_id)                       # KeyError si no existe
    for eleccion in kw.get("elecciones", ()):
        if eleccion.cita_id:
            reg.cita(eleccion.cita_id)
    if kw.get("formula_cita_id"):
        reg.cita(kw["formula_cita_id"])
    for discrepancia_id in kw.get("discrepancias", ()):
        d = reg.discrepancia(discrepancia_id)   # KeyError si no existe
        if not d.viva:
            raise ValueError(
                f"PasoDeMemoria: la discrepancia «{discrepancia_id}» esta "
                f"{d.estado.value} y no llega a la memoria. Lo resuelto es "
                "material del manifiesto -- para quien audita el codigo --, "
                "no de la memoria, que es para quien sustenta: quien abra hoy "
                "el PDF encuentra lo que la memoria dice y no hay nada que "
                "defender. Ver `EstadoDiscrepancia.viva`")
    kw.setdefault("fase", f.fase)
    return PasoDeMemoria(por_que=f.por_que, fundamento_id=f.id,
                         citas_textuales=citas, **kw)


def eleccion(fundamento_id: str, **kw: Any) -> EleccionDeProyecto:
    """
    Construye una `EleccionDeProyecto` trayendo el `por_que` del registro, que
    es lo mismo que `paso()` hace con un `PasoDeMemoria` y por la misma razon.

    POR QUE HACIA FALTA, con el caso que lo abrio delante: el `por_que` de la
    eleccion de fila de gamma_p de V7 estaba escrito a mano en
    `M5.v7_flotacion` y decia, en mayusculas, que la tabla es normativa y que
    que fila describe a la obra no lo es. Eso es cierto y es exactamente lo
    que hay que decir -- pero escrito suelto no lo comprueba nadie: nada ataba
    esa frase a un verbo, ni el verbo a las citas que lo sostienen. Puesto en
    un `Fundamento`, T11 contrasta el verbo contra el `caracter` de las citas
    y el censo de `test_memoria_sustentada` comprueba que no quede huerfano.

    NO ES UN ATAJO PARA REPETIR EL `por_que` DEL PASO. Un `Fundamento` propio
    para la eleccion es lo contrario de eso: separa la afirmacion fuerte del
    paso -- «hay que verificar la flotacion», EXIGENCIA de tres numerales --
    de la debil de la eleccion -- «esta obra es un portico rigido», que no lo
    dice ninguna fuente --, que es lo que NOR-HID-04 pide y lo que una sola
    cadena de texto no puede hacer.
    """
    f = _registro_normativo().fundamento(fundamento_id)
    return EleccionDeProyecto(por_que=f.por_que, fundamento_id=f.id, **kw)
