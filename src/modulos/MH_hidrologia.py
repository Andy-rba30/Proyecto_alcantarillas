"""
MH_hidrologia.py
================
Fase 1-bis: el CAUDAL DE DISEÑO de las Familias A y B, calculado dentro del
programa a partir de la cuenca de cada obra y de la serie de lluvia de una
estacion (T-1 de la cadena T; INF-3.1.2 a INF-3.1.6, INF-5.2.5).

    serie P24 --ajuste (num. 3.7)--> P24(TR) --num. 3.8.1--> I(tc, TR)
    cuenca --Tabla N 05 / ec. (30)--> tc        cuenca --Tabla N 08--> C
                     Q = 0.278 · C · I · A      (num. 3.12.2, ec. 28)

    Desde VE-2, de 10 a 770 km2, el metodo racional modificado completo
    (num. 3.12.2.1, ec. 29 a 35; `_caudal_racional_modificado`):
    Pd = P24(TR) ; KA = 1 − log10(A)/15 ; P = KA·Pd ; I = ec. (34) ;
    C = ec. (35) con CN ;  Q = 0.278 · C · I · A · K

Fuente unica: Manual de Hidrologia, Hidraulica y Drenaje (MTC), capitulo III.
Cada numero sale de `constantes_normativas.py` (bloque T-1), que a su vez
deriva las cuatro tablas del registro (`normativa/tablas.py`), y cada paso
lleva su cita.

QUE HACE Y QUE NO
-----------------
* NO sustituye a la via de siempre. Si `Q_m3s` viene lleno en el CSV de
  puntos, ese caudal se usa tal cual y este modulo solo emite el paso del
  caudal especifico y los avisos (`caudal_declarado`). Solo cuando la celda va
  vacia Y hay cuenca y estacion declaradas se calcula (`caudal_de_diseno`).
* NO rellena entradas. La cuenca, la serie y los años FEN son datos del
  estudio hidrologico (docs/contrato_entradas.md): se validan y no se
  corrigen. El metodo de tiempo de concentracion lo declara cada fila del CSV
  de cuencas; el tratamiento FEN, la distribucion, el nivel de significancia
  y la relacion intensidad-duracion son criterios [A] de
  `criterios_adoptados.py`.
* NO evalua fuera del rango que la fuente ESCRIBE: Temez fuera de 0.25-24 h
  o de 770 km2, el metodo racional simple desde 10 km2 (desde VE-2 una obra
  de 10 a 770 km2 pasa al racional modificado; el aporte de una cuneta no),
  el modificado desde 770 km2, la Tabla N 04 por debajo de 1 hora. En todos
  sale `MetodoNoEvaluableError` con lo que hace falta.
* Donde la fuente solo DESCRIBE de que cuencas salio una formula (Kirpich y
  California, 3-10 % de pendiente; la ecuacion de retardo, menos de 800 ha)
  decide el criterio 'tc_fuera_de_la_poblacion_del_metodo': no evaluar
  (valor de archivo) o evaluar con aviso. El MISMO trato para todas.
* La lluvia de diseño nunca dura menos que 'duracion_minima_lluvia_min'
  [C]; el caudal lleva el coeficiente de uniformidad K solo con la formula
  de Temez y segun 'coeficiente_uniformidad_temez' [A]; y el coeficiente de
  una superficie de la plataforma vial sale de
  'coeficiente_escorrentia_superficie_vial' [C], nunca de una fila de la
  Tabla N 08 puesta por omision.
* NINGUNA funcion publica entrega una lluvia o un caudal de diseño sin pasar
  por el criterio 'homogeneidad_serie_fen': `precipitacion_de_diseno`,
  `caudal_de_diseno` y `caudal_de_aporte_cuneta` son las tres puertas.

LO QUE EL MANUAL NO TRAE, y por eso este modulo no hace
--------------------------------------------------------
* Estimador de parametros para cinco de las ocho distribuciones del num.
  3.7.1 (Log Normal 3P, Gamma 2P y 3P, Log Pearson III, Log Gumbel): imprime
  su densidad y nada mas. Se ajustan las tres que si lo traen.
* Procedimiento de poblacion mixta (el tratamiento 'dos_poblaciones' de los
  años FEN).
* Fila de pavimento en la Tabla N 08 (lo cubre una fuente tecnica [C]), ni
  ponderacion de C por subareas.
* Hasta VE-2, el metodo racional modificado completo: de el se tomaban la
  formula de Temez y el coeficiente K (ficha T1-08). Desde VE-2 se calcula
  entero de 10 a 770 km2 (ficha VE2-F); lo que sigue sin hacerse son los
  metodos de hidrograma para cuencas mayores (SCS triangular, Snyder,
  HEC-HMS), que el mensaje nombra con su rango.
* Ejemplo numerico del metodo racional: los dorados de
  `tests/test_t1_hidrologia.py` estan calculados a mano y lo dicen.

UNIDADES
--------
La hidrologia del Manual se escribe en mm, mm/h, km2, minutos y horas, y sus
coeficientes empiricos SON de esas unidades. Cada argumento lleva la unidad
en el nombre (`area_km2`, `L_m`, `tc_min`, `I_mm_h`, `P24_mm`); el caudal
sale en m3/s, que es lo que consume el resto del pipeline.

Excepciones
-----------
    CriterioPendienteError   'homogeneidad_serie_fen' sin declarar.
    DatoFaltanteError        falta una columna o una celda obligatoria de los
                             CSV de cuencas o de la estacion (una celda `fen`
                             vacia lo es), el desnivel H que el metodo de
                             California exige, el numero de curva de la
                             ecuacion de retardo o el ajuste de Kirpich.
    DatoInvalidoError        una celda no es lo que su columna pide, una clave
                             no es fila de su tabla, un año se repite, un
                             dato contradice a otro (las dos areas de la
                             cuenca; un ajuste de Kirpich con otro metodo), o
                             el periodo de retorno no pasa de 1 año.
    MetodoNoEvaluableError   el metodo declarado no esta definido para esa
                             cuenca, o el Manual no da el procedimiento.
    LimiteNumericoError      la serie no tiene dispersion y el ajuste divide
                             por cero.
"""

from __future__ import annotations

import csv
import io
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist, fmean, median, stdev
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from src import criterios_adoptados as ca
from src.constantes_normativas import (COEFICIENTE_RACIONAL_MODIFICADO,
                                       DICK_PESCHKE, DISTRIBUCIONES_3_7_1,
                                       DISTRIBUCIONES_CON_ESTIMADOR_IMPRESO,
                                       FACTOR_REDUCTOR_AREA_SI,
                                       GUMBEL_MOMENTOS,
                                       INTENSIDAD_RACIONAL_MODIFICADO_SI,
                                       KS_N_MINIMO_TABULADO,
                                       NUMERAL_HEC_HMS,
                                       NUMERAL_HIDROGRAMA_SCS,
                                       NUMERAL_HIDROGRAMA_SNYDER,
                                       NUMERAL_RACIONAL_MODIFICADO,
                                       NUMERAL_TABLA_07, NUMERAL_TC_TEMEZ,
                                       RACIONAL_AREA_MAX_KM2,
                                       RACIONAL_COEFICIENTE_SI,
                                       REGISTRO_MINIMO_RECOMENDADO_ANIOS,
                                       TABLA_03_KS,
                                       TABLA_04_COEFICIENTES_DE_DURACION,
                                       TABLA_08_COEFICIENTE_DE_ESCORRENTIA,
                                       TABLA_08_PENDIENTE_MENOR,
                                       TABLA_08_PENDIENTES, TC_CALIFORNIA_SI,
                                       TC_FAA_SI, TC_IZZARD_PRODUCTO_IL_MAX,
                                       TC_IZZARD_SI, TC_KIRPICH_AJUSTES,
                                       TC_KIRPICH_RANGO_S, TC_KIRPICH_SI,
                                       TC_ONDA_CINEMATICA_SI,
                                       TC_RETARDO_SCS_AREA_MAX_KM2,
                                       TC_RETARDO_SCS_CN_MAX,
                                       TC_RETARDO_SCS_SI,
                                       TC_TEMEZ_AREA_MAX_KM2,
                                       TC_TEMEZ_RANGO_H, TC_TEMEZ_SI,
                                       UMBRAL_ESCORRENTIA_SI,
                                       UNIFORMIDAD_TEMEZ_SI)
from src.dominios import (HECTAREAS_POR_KM2, METROS_POR_KM, MINUTOS_POR_HORA,
                          S_CAUCE_MAX)
from src.modelos import (CIFRAS_FINA, CIFRAS_MAGNITUD, LEYENDA_CAUDAL_CALCULADO,
                         LEYENDA_CAUDAL_DECLARADO,
                         MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA,
                         ORIGEN_CAUDAL_CALCULADO, ORIGEN_CAUDAL_DECLARADO,
                         AjusteDeDistribucion, CaudalDeDiseno,
                         CriterioPendienteError, Cuenca,
                         DatoFaltanteError, DatoInvalidoError,
                         EleccionDeProyecto, EntradaHidrologica, ErrorProyecto,
                         LimiteNumericoError, Magnitud, MetodoNoEvaluableError,
                         ObstaculoAnticipado, PasoDeMemoria, RegistroDeLluvia,
                         SerieDeEstacion,
                         TipoDeVeredicto, Umbral, Veredicto, eleccion, paso)
from src.normativa import registro as _registro_normativo
from src.tolerancias import (ITERACIONES_MAX_PUNTO_FIJO_TC,
                             TOL_ABS_MISMO_MAXIMO_ANUAL_MM,
                             TOL_REL_AREA_ESCRITA_DOS_VECES,
                             TOL_REL_PUNTO_FIJO_TC)

_REG = _registro_normativo.construir()

# ---------------------------------------------------------------------------
# Claves: criterios, metodos y tratamientos
# ---------------------------------------------------------------------------
CRITERIO_FEN = "homogeneidad_serie_fen"
CRITERIO_DISTRIBUCION = "distribucion_precipitacion_maxima"
CRITERIO_ALFA = "nivel_significancia_ks"
CRITERIO_RELACION = "relacion_intensidad_duracion"
CRITERIO_DURACION_MINIMA = "duracion_minima_lluvia_min"
CRITERIO_POBLACION_TC = "tc_fuera_de_la_poblacion_del_metodo"
CRITERIO_K_TEMEZ = "coeficiente_uniformidad_temez"
CRITERIO_C_VIAL = "coeficiente_escorrentia_superficie_vial"
CRITERIO_FACTOR_P24 = "factor_intervalo_fijo_p24"     # VE-2 (d)

POBLACION_NO_EVALUABLE = "no_evaluable"
POBLACION_INDICADOR = "indicador_con_aviso"
K_APLICAR = "aplicar"
K_NO_APLICAR = "no_aplicar"

# Las superficies de la plataforma vial que la columna `cobertura` admite
# ademas de las cinco coberturas de la Tabla N 08. La lista es del criterio
# (derivada del registro), no de este modulo.
SUPERFICIES_VIALES: Tuple[str, ...] = ca.SUPERFICIES_VIALES_WSDOT

FEN_SERIE_COMPLETA = "serie_completa"
FEN_SERIE_SIN_FEN = "serie_sin_fen"
FEN_DOS_POBLACIONES = "dos_poblaciones"

MEJOR_AJUSTE_KS = "mejor_ajuste_ks"
# --- VE-5 (ficha T1-01) --- La prueba chi-cuadrado (num. 3.7.2 a), como
# contraste de la de Kolmogorov-Smirnov: la regla de su k es un criterio [A],
# y solo se aplica a las distribuciones que el numeral dice que verifica.
CRITERIO_INTERVALOS_CHI2 = "intervalos_de_clase_chi_cuadrado"
INTERVALOS_STURGES = "sturges"
INTERVALOS_RAIZ_DE_N = "raiz_de_n"
DISTRIBUCIONES_CHI2: Tuple[str, ...] = ("normal", "lognormal_2p")
RELACION_DICK_PESCHKE = "dick_peschke"
RELACION_TABLA_04 = "tabla_04_coeficientes_de_duracion"
# --- VE-5 (ficha T1-05) --- La relacion regional de la ecuacion (17):
# I = K·T^m / t^n, con los tres factores declarados en su criterio [S].
RELACION_IDF_REGIONAL = "idf_regional_ec17"
CRITERIO_IDF_REGIONAL = "factores_idf_regional"

# Los metodos de tiempo de concentracion que la columna `metodo_tc` admite:
# CUATRO de las seis filas de la Tabla N 05 y la ecuacion (30) del num.
# 3.12.2.1 (Temez), que NO es fila de esa tabla. Las dos de canal (Kirpich y
# California) salieron de cuencas empinadas; la de la FAA es de flujo
# superficial y la de retardo pide el numero de curva: con ellas una cuenca
# plana o el area tributaria de una cuneta tienen un tiempo de concentracion
# evaluable y citado. Desde VE-5 (ficha T1-07) tambien las dos filas que
# llevan la intensidad de la lluvia DENTRO de la formula (Izzard y la onda
# cinematica): se resuelven por punto fijo tc <-> I (`_punto_fijo_tc`), con
# el dato de la superficie que cada una pide en su columna opcional.
TC_METODO_KIRPICH = "kirpich"
TC_METODO_CALIFORNIA = "california_culverts_practice"
TC_METODO_FAA = "federal_aviation_administration"
TC_METODO_RETARDO_SCS = "retardo_scs"
TC_METODO_TEMEZ = "temez"
TC_METODO_IZZARD = "izzard"
TC_METODO_ONDA_CINEMATICA = "onda_cinematica"
METODOS_TC: Tuple[str, ...] = (TC_METODO_KIRPICH, TC_METODO_CALIFORNIA,
                               TC_METODO_FAA, TC_METODO_RETARDO_SCS,
                               TC_METODO_TEMEZ, TC_METODO_IZZARD,
                               TC_METODO_ONDA_CINEMATICA)
# Los que llevan la intensidad dentro de la formula, y el dato de la
# superficie que cada uno pide (columna opcional del CSV de cuencas).
METODOS_TC_ITERATIVOS: Dict[str, str] = {
    TC_METODO_IZZARD: "c_retardo_izzard",
    TC_METODO_ONDA_CINEMATICA: "n_manning_superficial",
}

# Columnas de los dos CSV de entrada. Las obligatorias tienen que estar en el
# encabezado y traer valor en cada fila; las opcionales pueden faltar del
# encabezado o ir vacias.
COLUMNAS_CUENCAS: Tuple[str, ...] = ("id", "area_km2", "L_cauce_m",
                                     "S_cauce_cuenca", "S_terreno",
                                     "cobertura", "suelo", "estacion",
                                     "metodo_tc")
COLUMNAS_CUENCAS_OPCIONALES: Tuple[str, ...] = ("H_desnivel_m",
                                                "ajuste_kirpich", "CN",
                                                "c_retardo_izzard",
                                                "n_manning_superficial")
COLUMNAS_ESTACION: Tuple[str, ...] = ("estacion", "anio", "p24_mm", "fen")
# Como se escribe el hecho «este año fue FEN» en la columna `fen`.
FEN_SI: Tuple[str, ...] = ("si", "sí", "1", "fen", "x")
# Una celda VACIA no esta en ninguna de las dos listas: no es un «no».
FEN_NO: Tuple[str, ...] = ("no", "0")
MARCA_COMENTARIO = "#"

PROCEDIMIENTO_HIDROGRAMA = ("otro metodo de estimacion de caudales: el "
                            "hidrograma unitario del num. 3.12.3 del Manual "
                            "de Hidrologia, o el caudal declarado por el "
                            "estudio hidrologico en la columna Q_m3s")

# --- VE-2 (f) --- Desde 10 km2 el caudal de una obra sale del metodo
# racional MODIFICADO (num. 3.12.2.1), hasta 770 km2; por encima, de un metodo
# de hidrograma que el programa no implementa. El mensaje los nombra con el
# rango y la pagina que el Manual les escribe.
PROCEDIMIENTO_FUERA_DEL_RACIONAL_MODIFICADO = (
    "un metodo de hidrograma, que el programa no implementa: el hidrograma "
    "triangular del SCS, recomendado para cuencas de hasta 30 km2 "
    f"({NUMERAL_HIDROGRAMA_SCS}); el de Snyder, de 30 a 30 000 km2 "
    f"({NUMERAL_HIDROGRAMA_SNYDER}); o el modelo HEC-HMS ({NUMERAL_HEC_HMS}). "
    "O el caudal declarado por el estudio hidrologico en la columna Q_m3s")

# Los dos metodos de caudal de la Fase 1-bis, y la frontera entre ellos: la
# del racional simple, «Muy usado para cuencas, A<10 Km2» (pag. impresa 49).
METODO_RACIONAL = "racional"
METODO_RACIONAL_MODIFICADO = "racional_modificado"

CODIGO_SERIE = "1b.1"
CODIGO_AJUSTE = "1b.2"
CODIGO_KS = "1b.3"
CODIGO_FEN = "1b.3b"
# --- VE-2 (e) --- el aviso de consistencia de la serie, el ULTIMO paso de la
# lluvia de diseño: va despues de los cuatro de T-1 para no mover las
# posiciones que aquellos tienen en `precipitacion_de_diseno`.
CODIGO_CONSISTENCIA = "1b.3c"
CODIGO_TC = "1b.4"
CODIGO_INTENSIDAD = "1b.5"
CODIGO_C = "1b.6"
CODIGO_RACIONAL = "1b.7"
CODIGO_Q_ESPECIFICO = "1b.8"


def _no_evaluable(que: str, motivo: str, procedimiento: str,
                  id_punto: Optional[str] = None) -> MetodoNoEvaluableError:
    return MetodoNoEvaluableError(
        que=que, procedimiento=procedimiento, motivo=motivo, id_punto=id_punto,
        rotulo=MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA)


def _caracter(cita_id: str) -> str:
    """El caracter de la cita en la fuente, leido del registro."""
    return _REG.cita(cita_id).caracter.value


# ===========================================================================
# 1. Tiempo de concentracion (num. 3.9, Tabla N 05; num. 3.12.2.1, ec. 30)
# ===========================================================================

def poblacion_del_metodo(metodo: str, *, pendiente: Optional[float] = None,
                         area_km2: Optional[float] = None,
                         ) -> Optional[Tuple[bool, str, str]]:
    """
    La POBLACION DE DESARROLLO que la Tabla N 05 del num. 3.9 describe para
    un metodo de tiempo de concentracion (pags. impresas 39 y 40), y si la
    cuenca cae dentro: (dentro, lo que la tabla describe, lo que la cuenca
    tiene). None cuando la tabla no le describe ninguna numerica (la formula
    de la FAA) o cuando el metodo trae un rango de aplicacion propio, que no
    pasa por aqui (Temez, num. 3.12.2.1).

    Kirpich: pendientes de 3 a 10 %. California Culverts Practice: la MISMA,
    medida como H / L, porque la tabla dice de ella que «esencialmente es la
    ecuación de Kirpich» (lectura del proyecto: la `Interpretacion` de
    `MC_HHD.3.9#T05_CALIFORNIA`). Ecuacion de retardo: areas inferiores a
    800 ha. Las condiciones van escritas de modo que un NaN caiga fuera.
    """
    if metodo in (TC_METODO_KIRPICH, TC_METODO_CALIFORNIA):
        minimo, maximo = TC_KIRPICH_RANGO_S
        return (minimo <= pendiente <= maximo,
                f"cuencas con pendientes de {minimo:.0%} a {maximo:.0%}",
                f"una pendiente de {pendiente:.2%}")
    if metodo == TC_METODO_RETARDO_SCS:
        techo_ha = TC_RETARDO_SCS_AREA_MAX_KM2 * HECTAREAS_POR_KM2
        return (area_km2 < TC_RETARDO_SCS_AREA_MAX_KM2,
                f"cuencas de area inferior a {techo_ha:g} ha",
                f"un area de {area_km2 * HECTAREAS_POR_KM2:g} ha")
    return None


def _exigir_poblacion(metodo: str, *, pendiente: Optional[float] = None,
                      area_km2: Optional[float] = None,
                      id_punto: Optional[str] = None,
                      leer=None) -> Optional[str]:
    """
    La compuerta de la poblacion de desarrollo. Dentro de ella, None. Fuera,
    lee el criterio 'tc_fuera_de_la_poblacion_del_metodo': con «no_evaluable»
    lanza `MetodoNoEvaluableError`; con «indicador_con_aviso» devuelve el
    AVISO que el paso y la corrida tienen que imprimir.

    El trato es UNO para todos los metodos que tienen poblacion descrita:
    hasta la auditoria de T-1 Kirpich se detenia y California no, de modo que
    el limite de una se saltaba cambiando el nombre del metodo.

    `leer` (VE-4b): como se lee el criterio. La corrida, con `ca.valor`, que
    registra el uso; el pre-vuelo (`anticipar_caudal`), con
    `_leer_sin_registrar`, que lanza lo mismo y no lo registra.
    """
    poblacion = poblacion_del_metodo(metodo, pendiente=pendiente,
                                     area_km2=area_km2)
    if poblacion is None or poblacion[0]:
        return None
    _, describe, tiene = poblacion
    hecho = (f"la Tabla N 05 dice que la formula «{metodo}» salio de "
             f"{describe}, y esta cuenca tiene {tiene}")
    trato = (ca.valor if leer is None else leer)(CRITERIO_POBLACION_TC)
    if trato == POBLACION_INDICADOR:
        return (f"Tiempo de concentracion EXTRAPOLADO: {hecho}. Se evalua "
                f"igual porque el criterio '{CRITERIO_POBLACION_TC}' = "
                f"{trato}; la formula no tiene respaldo fuera de las cuencas "
                "de las que salio y el estudio hidrologico tiene que "
                "defender el numero.")
    if trato != POBLACION_NO_EVALUABLE:
        raise DatoInvalidoError(
            CRITERIO_POBLACION_TC, valor=trato, id_punto=id_punto,
            motivo=f"los tratos admitidos son {POBLACION_NO_EVALUABLE} e "
                   f"{POBLACION_INDICADOR}")
    raise _no_evaluable(
        "tc",
        f"{hecho}. La tabla describe esa poblacion y no prohibe salir de "
        f"ella; no extrapolar es adopcion del proyecto (criterio "
        f"'{CRITERIO_POBLACION_TC}' = {trato})",
        "otro metodo de tiempo de concentracion en la columna `metodo_tc` "
        f"del CSV de cuencas ({', '.join(m for m in METODOS_TC if m != metodo)}), "
        f"declarar '{POBLACION_INDICADOR}' en '{CRITERIO_POBLACION_TC}' para "
        "evaluarla con aviso, o el caudal declarado en Q_m3s",
        id_punto)


def tc_kirpich_min(*, L_m: float, S: float, ajuste: Optional[str],
                   id_punto: Optional[str] = None) -> float:
    """
    Kirpich (1940), Tabla N 05 del num. 3.9 (pag. impresa 39):
    tc = f · 0.01947 · L^0.77 · S^-0.385, tc en MINUTOS, L en m, S en m/m.

    `ajuste` es la clave del factor f que la observacion de la tabla manda
    (0.4 en superficies de concreto o asfalto, 0.2 en canales de concreto,
    'ninguno' = 1) y es OBLIGATORIO: una celda vacia no elige fila. Fuera de
    3 a 10 % de pendiente --la poblacion de la que salio la formula-- decide
    el criterio 'tc_fuera_de_la_poblacion_del_metodo' (`_exigir_poblacion`).
    """
    if not ajuste:
        raise DatoFaltanteError(
            "ajuste_kirpich", id_punto=id_punto,
            detalle="con el metodo de Kirpich hay que declarar el ajuste por "
                    "tipo de superficie que la observacion de la Tabla N 05 "
                    "manda (" + ", ".join(TC_KIRPICH_AJUSTES) + "): «ninguno» "
                    "es una clave y se escribe; una celda vacia no elige")
    if ajuste not in TC_KIRPICH_AJUSTES:
        raise DatoInvalidoError(
            "ajuste_kirpich", valor=ajuste, id_punto=id_punto,
            motivo="los ajustes que la Tabla N 05 escribe para Kirpich son "
                   + ", ".join(TC_KIRPICH_AJUSTES))
    _exigir_poblacion(TC_METODO_KIRPICH, pendiente=S, id_punto=id_punto)
    k = TC_KIRPICH_SI
    return (TC_KIRPICH_AJUSTES[ajuste] * k["coeficiente"]
            * L_m ** k["exp_L"] * S ** k["exp_S"])


def tc_california_min(*, L_m: float, H_m: float,
                      id_punto: Optional[str] = None) -> float:
    """
    California Culverts Practice (1942), Tabla N 05 del num. 3.9 (pag.
    impresa 39): tc = 0.0195 · (L^3 / H)^0.385, tc en MINUTOS, L y H en m.

    La fila no imprime rango propio; dice que «esencialmente es la ecuación
    de Kirpich», y el proyecto le aplica la poblacion de Kirpich medida como
    H / L, con el mismo criterio (`_exigir_poblacion`).
    """
    _exigir_poblacion(TC_METODO_CALIFORNIA, pendiente=H_m / L_m,
                      id_punto=id_punto)
    k = TC_CALIFORNIA_SI
    return k["coeficiente"] * (L_m ** k["exp_L"] / H_m) ** k["exp"]


def tc_faa_min(*, C: float, L_m: float, S: float,
               id_punto: Optional[str] = None) -> float:
    """
    Federal Aviation Administration (1970), Tabla N 05 del num. 3.9 (pag.
    impresa 39): tc = 0.7035 · (1.1 − C) · L^0.50 / S^0.333, tc en MINUTOS,
    L = longitud del flujo superficial en m, S = pendiente de la superficie
    en m/m, C = coeficiente de escorrentia del metodo racional.

    Es una formula de FLUJO SUPERFICIAL: la que vale para una plataforma, un
    talud o una cuenca plana sin cauce definido. La tabla no le describe una
    poblacion numerica y no hay compuerta de poblacion.
    """
    k = TC_FAA_SI
    if not 0 < C < k["resta_C"]:
        raise DatoInvalidoError(
            "C", valor=C, id_punto=id_punto,
            motivo=f"la formula de la FAA lleva el factor ({k['resta_C']:g} "
                   "− C) y pide un coeficiente de escorrentia entre 0 y "
                   f"{k['resta_C']:g}")
    return (k["coeficiente"] * (k["resta_C"] - C) * L_m ** k["exp_L"]
            / S ** k["exp_S"])


def tc_retardo_scs_min(*, L_m: float, CN: float, S: float, area_km2: float,
                       id_punto: Optional[str] = None) -> float:
    """
    Ecuacion de retardo SCS (1973), Tabla N 05 del num. 3.9 (pag. impresa
    40): tc = 0.0136 · L^0.8 · (1000/CN − 9)^0.7 / S^0.5, tc en MINUTOS,
    L = longitud hidraulica de la cuenca en m, CN = numero de curva,
    S = pendiente promedio de la cuenca en m/m.

    El numero de curva es un dato del estudio hidrologico (columna `CN`); el
    programa no tiene tabla de la que leerlo. Por encima de 800 ha --el area
    a la que la tabla dice que se adapto-- decide el criterio
    'tc_fuera_de_la_poblacion_del_metodo'.
    """
    if not 0 < CN <= TC_RETARDO_SCS_CN_MAX:
        raise DatoInvalidoError(
            "CN", valor=CN, id_punto=id_punto,
            motivo="el numero de curva es mayor que 0 y no pasa de "
                   f"{TC_RETARDO_SCS_CN_MAX}")
    _exigir_poblacion(TC_METODO_RETARDO_SCS, area_km2=area_km2,
                      id_punto=id_punto)
    k = TC_RETARDO_SCS_SI
    return (k["coeficiente"] * L_m ** k["exp_L"]
            * (k["mil"] / CN - k["resta"]) ** k["exp_CN"] / S ** k["exp_S"])


def tc_temez_h(*, L_km: float, S: float, area_km2: float,
               id_punto: Optional[str] = None,
               procedimiento: Optional[str] = None) -> float:
    """
    Temez, ecuacion (30) del num. 3.12.2.1 (pag. impresa 51):
    Tc = 0.3 · (L / S^0.25)^0.76, Tc en HORAS, L en KM, S en m/m.

    El metodo del que la formula es pieza vale para areas menores de 770 km2
    y Tc de 0.25 a 24 horas: fuera de eso NO se evalua, sin criterio que lo
    relaje, porque aqui la fuente si escribe un rango de aplicacion.

    `procedimiento` (VE-2): lo que el mensaje de un Tc fuera de rango ofrece
    como remedio. Por omision, otro metodo de tiempo de concentracion (el uso
    hibrido, por debajo de 10 km2); el metodo racional modificado completo
    pasa los de hidrograma, porque desde 10 km2 otra formula de Tc no es
    remedio.
    """
    if not area_km2 < TC_TEMEZ_AREA_MAX_KM2:
        raise _no_evaluable(
            "tc",
            f"la formula de Temez es del metodo racional modificado, que el "
            f"Manual acota a areas menores de {TC_TEMEZ_AREA_MAX_KM2:g} km2, "
            f"y la cuenca tiene {area_km2:g} km2",
            PROCEDIMIENTO_HIDROGRAMA, id_punto)
    k = TC_TEMEZ_SI
    tc_h = k["coeficiente"] * (L_km / S ** k["exp_S"]) ** k["exp"]
    minimo, maximo = TC_TEMEZ_RANGO_H
    if not minimo <= tc_h <= maximo:
        raise _no_evaluable(
            "tc",
            f"la formula de Temez da Tc = {tc_h:.3f} h y el Manual la acota "
            f"a tiempos de concentracion de {minimo:g} a {maximo:g} horas "
            "(num. 3.12.2.1)",
            procedimiento or (
                "otro metodo de tiempo de concentracion en la columna "
                "`metodo_tc` del CSV de cuencas "
                f"({', '.join(m for m in METODOS_TC if m != TC_METODO_TEMEZ)}), "
                "o el caudal declarado en Q_m3s"),
            id_punto)
    return tc_h


def tc_izzard_min(*, i_mm_h: float, c: float, L_m: float, S: float,
                  id_punto: Optional[str] = None) -> float:
    """
    Izzard (1946), Tabla N 05 del num. 3.9 (pag. impresa 39):
    tc = 525 · (0.0000276·i + c) · L^0.33 / (S^0.333 · i^0.667), tc en
    MINUTOS, i = intensidad de la lluvia en mm/h, c = coeficiente de retardo,
    L = longitud de la trayectoria de flujo en m, S = su pendiente en m/m.

    La formula PURA, con una intensidad dada. La intensidad depende a su vez
    del tiempo de concentracion («la solución requiere de procesos
    iterativos»): el tc de una cuenca sale del punto fijo de
    `tiempo_de_concentracion`, y la condicion «el producto de i por L debe
    ser ≤ 3800» se exige sobre la intensidad que resulta
    (`exigir_producto_izzard`).
    """
    if not c > 0:
        raise DatoInvalidoError(
            "c_retardo_izzard", valor=c, id_punto=id_punto,
            motivo="el coeficiente de retardo de Izzard es positivo (la "
                   "Tabla N 05 lo describe de 0.0070 a 0.06)")
    if not i_mm_h > 0:
        raise LimiteNumericoError(
            "i", valor=i_mm_h, id_punto=id_punto,
            motivo="la formula de Izzard divide por la intensidad de la "
                   "lluvia, y no es un numero positivo")
    k = TC_IZZARD_SI
    return (k["coeficiente"] * (k["coeficiente_i"] * i_mm_h + c)
            * L_m ** k["exp_L"] / (S ** k["exp_S"] * i_mm_h ** k["exp_i"]))


def exigir_producto_izzard(*, i_mm_h: float, L_m: float,
                           id_punto: Optional[str] = None) -> float:
    """
    La condicion de aplicacion de Izzard, Tabla N 05 del num. 3.9 (pag.
    impresa 39): «el producto de i por L debe ser ≤ 3800», i en mm/h y L en
    m. Devuelve el producto; fuera de la condicion NO se evalua
    (`MetodoNoEvaluableError`), porque la fuente la escribe como exigencia.
    """
    producto = i_mm_h * L_m
    if not producto <= TC_IZZARD_PRODUCTO_IL_MAX:
        raise _no_evaluable(
            "tc",
            f"la formula de Izzard exige que el producto de la intensidad "
            f"por la longitud no pase de {TC_IZZARD_PRODUCTO_IL_MAX:g} "
            f"(Tabla N 05), y con la intensidad del punto fijo "
            f"(i = {i_mm_h:.2f} mm/h) y L = {L_m:g} m vale {producto:.0f}",
            "otro metodo de tiempo de concentracion en la columna "
            "`metodo_tc` del CSV de cuencas "
            f"({', '.join(m for m in METODOS_TC if m != TC_METODO_IZZARD)}), "
            "una trayectoria de flujo mas corta, o el caudal declarado en "
            "Q_m3s",
            id_punto)
    return producto


def tc_onda_cinematica_min(*, L_m: float, n: float, I_mm_h: float, S: float,
                           id_punto: Optional[str] = None) -> float:
    """
    Ecuaciones de onda cinematica, Morgali y Linsley (1965), Aron y Erborge
    (1973), Tabla N 05 del num. 3.9 (pag. impresa 40):
    tc = 7 · L^0.6 · n^0.6 / (I^0.4 · S^0.3), tc en MINUTOS, L = longitud
    del flujo superficial en m, n = coeficiente de rugosidad de Manning,
    I = intensidad de la lluvia en mm/h, S = pendiente promedio del terreno
    en m/m.

    La formula PURA, con una intensidad dada: «el método requiere
    iteraciones debido a que tanto I (Intensidad de lluvia) como tc son
    desconocidos». El tc de una cuenca sale del punto fijo de
    `tiempo_de_concentracion`. La fila no escribe rango de aplicacion.
    """
    if not n > 0:
        raise DatoInvalidoError(
            "n_manning_superficial", valor=n, id_punto=id_punto,
            motivo="el coeficiente de rugosidad de Manning es positivo")
    if not I_mm_h > 0:
        raise LimiteNumericoError(
            "I", valor=I_mm_h, id_punto=id_punto,
            motivo="la formula de la onda cinematica divide por la "
                   "intensidad de la lluvia, y no es un numero positivo")
    k = TC_ONDA_CINEMATICA_SI
    return (k["coeficiente"] * L_m ** k["exp_L"] * n ** k["exp_n"]
            / (I_mm_h ** k["exp_I"] * S ** k["exp_S"]))


def _punto_fijo_tc(formula: Callable[[float], float],
                   intensidad_de: Callable[[float], float], *,
                   id_punto: Optional[str] = None,
                   ) -> Tuple[float, float, int]:
    """
    El punto fijo tc = f(I(tc)) de una formula de la Tabla N 05 que lleva la
    intensidad dentro (Izzard, onda cinematica): (tc en min, I en mm/h,
    iteraciones).

    `formula(I)` da el tc con una intensidad; `intensidad_de(tc)` da la
    intensidad de la lluvia de diseño de esa duracion, con la MISMA relacion
    y la MISMA duracion minima que el paso de la intensidad
    (`_intensidad_de_diseno`), de modo que el tc y la I del paso son los del
    punto fijo. Es la «solución gráfica directa» de la observacion de la
    onda cinematica (superponer la curva intensidad-duracion), hecha por
    sustitucion sucesiva.

    Arranca de una lluvia de 24 horas (la duracion que las dos relaciones
    del num. 3.8.1 cubren) y para cuando dos iterados difieren menos que
    `TOL_REL_PUNTO_FIJO_TC` del ultimo. La aplicacion es creciente y
    contractiva, de modo que los iterados bajan hacia el punto fijo y la
    intensidad sube hacia la de diseño sin pasarla. Sin convergencia en
    `ITERACIONES_MAX_PUNTO_FIJO_TC` se detiene con `LimiteNumericoError`.
    """
    tc = float(DICK_PESCHKE["minutos_en_24_h"])
    for iteracion in range(1, ITERACIONES_MAX_PUNTO_FIJO_TC + 1):
        I = intensidad_de(tc)
        siguiente = formula(I)
        if not (math.isfinite(siguiente) and siguiente > 0):
            raise LimiteNumericoError(
                "tc", valor=siguiente, id_punto=id_punto,
                motivo=f"el punto fijo tc <-> I dio un tiempo de "
                       f"concentracion que no es un numero positivo con "
                       f"I = {I:g} mm/h (iteracion {iteracion})")
        if abs(siguiente - tc) <= TOL_REL_PUNTO_FIJO_TC * siguiente:
            return siguiente, intensidad_de(siguiente), iteracion
        tc = siguiente
    raise LimiteNumericoError(
        "tc", valor=tc, id_punto=id_punto,
        motivo=f"el punto fijo tc <-> I no convergio en "
               f"{ITERACIONES_MAX_PUNTO_FIJO_TC} iteraciones (tolerancia "
               f"relativa {TOL_REL_PUNTO_FIJO_TC:g})")


def _falta_dato_iterativo(cuenca: Cuenca) -> DatoFaltanteError:
    columna = METODOS_TC_ITERATIVOS[cuenca.metodo_tc]
    que = ("el coeficiente de retardo de la superficie (la Tabla N 05 lo "
           "describe de 0.0070 en pavimento muy liso a 0.06 en pasto denso)"
           if cuenca.metodo_tc == TC_METODO_IZZARD else
           "el coeficiente de rugosidad de Manning del flujo superficial")
    return DatoFaltanteError(
        columna, id_punto=cuenca.id,
        detalle=f"el metodo «{cuenca.metodo_tc}» (Tabla N 05) pide {que}: es "
                f"la columna opcional {columna} del CSV de cuencas, la "
                "entrega el estudio hidrologico y el programa no la elige")


def _lectura_del_proyecto(cita_id: str) -> str:
    """La `Interpretacion` de una cita, tal como esta en el registro."""
    return _REG.cita(cita_id).interpretacion.texto


def _juicio_de_poblacion(metodo: str, cita: str, aviso: Optional[str], *,
                         pendiente: Optional[float] = None,
                         area_km2: Optional[float] = None,
                         ) -> Tuple[Umbral, Veredicto]:
    """El umbral y el veredicto de la poblacion de desarrollo de un metodo."""
    if metodo == TC_METODO_RETARDO_SCS:
        descripcion = ("area maxima de las cuencas a las que se adapto la "
                       "ecuacion de retardo (exclusiva)")
        valor: Any = TC_RETARDO_SCS_AREA_MAX_KM2
        unidad = "km2"
    else:
        descripcion = ("pendientes de las cuencas de las que salio la "
                       "formula de Kirpich")
        valor, unidad = TC_KIRPICH_RANGO_S, "m/m"
    fuera = aviso is not None
    umbral = Umbral(
        descripcion=descripcion, valor=valor, unidad=unidad, cita_id=cita,
        caracter=_caracter(cita),
        aplicacion="poblacion de desarrollo: la tabla la DESCRIBE, no "
                   "prohibe salir de ella. Que se hace fuera lo decide el "
                   f"criterio '{CRITERIO_POBLACION_TC}' (no evaluar, o "
                   "evaluar con aviso)",
        criterio_aplicado=CRITERIO_POBLACION_TC if fuera else None)
    veredicto = Veredicto(
        tipo=TipoDeVeredicto.INDICADOR if fuera else TipoDeVeredicto.CUMPLE,
        explicacion=("la cuenca esta FUERA de la poblacion de la formula: el "
                     "tiempo de concentracion es una extrapolacion" if fuera
                     else "la cuenca esta dentro de la poblacion de la "
                          "formula"))
    return umbral, veredicto


def _falta_desnivel_california(cuenca: Cuenca) -> DatoFaltanteError:
    return DatoFaltanteError(
        "H_desnivel_m", id_punto=cuenca.id,
        detalle="el metodo de California Culverts Practice (Tabla "
                "N 05) pide el desnivel H entre la divisoria de "
                "aguas y la salida, en metros: es columna opcional "
                "del CSV de cuencas y no se deduce de S por L")


def _falta_cn_retardo(cuenca: Cuenca) -> DatoFaltanteError:
    return DatoFaltanteError(
        "CN", id_punto=cuenca.id,
        detalle="la ecuacion de retardo (Tabla N 05) pide el numero "
                "de curva de la cuenca: es columna opcional del CSV "
                "de cuencas, lo entrega el estudio hidrologico y el "
                "programa no tiene tabla de la que leerlo")


def tiempo_de_concentracion(cuenca: Cuenca, *, C: Optional[float] = None,
                            racional_modificado: bool = False,
                            intensidad_de: Optional[Callable[[float], float]] = None,
                            ) -> Tuple[float, PasoDeMemoria, Tuple[str, ...]]:
    """
    El tiempo de concentracion de la cuenca, en MINUTOS, por el metodo que su
    fila declara (`metodo_tc`), con el paso de memoria y los avisos (num. 3.9
    y Tabla N 05; num. 3.12.2.1 para Temez).

    `C` es el coeficiente de escorrentia del metodo racional, que solo la
    formula de la FAA usa. `racional_modificado` (VE-2): el caudal de la
    cuenca sale del metodo racional modificado completo, del que la formula
    de Temez es la ecuacion (30); entonces no hay uso hibrido que declarar,
    y un Tc fuera de 0.25-24 h remite a los metodos de hidrograma.

    `intensidad_de` (VE-5, ficha T1-07): la intensidad de la lluvia de
    diseño en mm/h para un tiempo de concentracion en minutos, que solo
    piden Izzard y la onda cinematica --llevan la intensidad DENTRO de la
    formula--. Con ella el tc sale del punto fijo tc <-> I
    (`_punto_fijo_tc`); sin ella esos dos metodos no se pueden evaluar.
    """
    metodo = cuenca.metodo_tc
    L = Magnitud("L", cuenca.L_cauce_m, "m",
                 f"columna L_cauce_m de {cuenca.origen}", cifras=CIFRAS_MAGNITUD)
    S = Magnitud("S", cuenca.S_cauce_cuenca, "m/m",
                 f"columna S_cauce_cuenca de {cuenca.origen}", cifras=CIFRAS_FINA)
    umbral: Optional[Umbral] = None
    notas: List[str] = []
    aviso: Optional[str] = None
    if metodo == TC_METODO_KIRPICH:
        cita = "MC_HHD.3.9#T05_KIRPICH"
        aviso = _exigir_poblacion(metodo, pendiente=cuenca.S_cauce_cuenca,
                                  id_punto=cuenca.id)
        tc = tc_kirpich_min(L_m=cuenca.L_cauce_m, S=cuenca.S_cauce_cuenca,
                            ajuste=cuenca.ajuste_kirpich, id_punto=cuenca.id)
        formula = "tc = f · 0.01947 · L^0.77 · S^-0.385   [min; L en m, S en m/m]"
        sustitucion: Tuple[Magnitud, ...] = (
            L, S,
            Magnitud("f", TC_KIRPICH_AJUSTES[cuenca.ajuste_kirpich], "",
                     f"ajuste '{cuenca.ajuste_kirpich}' de la observacion de "
                     "la fila Kirpich de la Tabla N 05 (columna "
                     f"ajuste_kirpich de {cuenca.origen})"))
        umbral, veredicto = _juicio_de_poblacion(
            metodo, cita, aviso, pendiente=cuenca.S_cauce_cuenca)
        notas.append(_lectura_del_proyecto(cita))
    elif metodo == TC_METODO_CALIFORNIA:
        if cuenca.H_desnivel_m is None:
            raise _falta_desnivel_california(cuenca)
        cita = "MC_HHD.3.9#T05_CALIFORNIA"
        pendiente = cuenca.H_desnivel_m / cuenca.L_cauce_m
        aviso = _exigir_poblacion(metodo, pendiente=pendiente,
                                  id_punto=cuenca.id)
        tc = tc_california_min(L_m=cuenca.L_cauce_m, H_m=cuenca.H_desnivel_m,
                               id_punto=cuenca.id)
        formula = "tc = 0.0195 · (L^3 / H)^0.385   [min; L y H en m]"
        sustitucion = (
            L,
            Magnitud("H", cuenca.H_desnivel_m, "m",
                     f"columna H_desnivel_m de {cuenca.origen}",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("H / L", pendiente, "m/m",
                     "la pendiente con que se compara la poblacion de "
                     "Kirpich", cifras=CIFRAS_FINA))
        umbral, veredicto = _juicio_de_poblacion(metodo, cita, aviso,
                                                 pendiente=pendiente)
        notas.append(_lectura_del_proyecto(cita))
    elif metodo == TC_METODO_FAA:
        if C is None:
            raise DatoFaltanteError(
                "C", id_punto=cuenca.id,
                detalle="la formula de la FAA usa el coeficiente de "
                        "escorrentia del metodo racional: el tiempo de "
                        "concentracion se pide con el C de la cuenca")
        cita = "MC_HHD.3.9#T05_FAA"
        tc = tc_faa_min(C=C, L_m=cuenca.L_cauce_m, S=cuenca.S_cauce_cuenca,
                        id_punto=cuenca.id)
        formula = ("tc = 0.7035 · (1.1 − C) · L^0.50 / S^0.333   "
                   "[min; L en m, S en m/m]")
        sustitucion = (
            Magnitud("C", C, "", f"paso {CODIGO_C}: el coeficiente de "
                     "escorrentia del metodo racional de esta misma cuenca",
                     cifras=CIFRAS_MAGNITUD),
            L, S)
        veredicto = Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="la fila de la Tabla N 05 no describe una poblacion "
                        "numerica para esta formula: dice para que se "
                        "desarrollo, y esa frase va en las citas del paso")
        notas.append(
            "Formula de flujo SUPERFICIAL. Las columnas L_cauce_m y "
            "S_cauce_cuenca de la fila se leen aqui como la longitud del "
            "flujo superficial y la pendiente de la superficie, que es lo "
            "que la formula pide: quien declara este metodo declara esas dos "
            "magnitudes en esas dos columnas.")
    elif metodo == TC_METODO_RETARDO_SCS:
        if cuenca.CN is None:
            raise _falta_cn_retardo(cuenca)
        cita = "MC_HHD.3.9#T05_SCS"
        aviso = _exigir_poblacion(metodo, area_km2=cuenca.area_km2,
                                  id_punto=cuenca.id)
        tc = tc_retardo_scs_min(L_m=cuenca.L_cauce_m, CN=cuenca.CN,
                                S=cuenca.S_terreno, area_km2=cuenca.area_km2,
                                id_punto=cuenca.id)
        formula = ("tc = 0.0136 · L^0.8 · (1000/CN − 9)^0.7 / S^0.5   "
                   "[min; L en m, S en m/m]")
        sustitucion = (
            L,
            Magnitud("CN", cuenca.CN, "",
                     f"columna CN de {cuenca.origen}", cifras=CIFRAS_MAGNITUD),
            Magnitud("S", cuenca.S_terreno, "m/m",
                     f"columna S_terreno de {cuenca.origen}: la formula pide "
                     "la pendiente promedio de la cuenca, no la del cauce",
                     cifras=CIFRAS_FINA))
        umbral, veredicto = _juicio_de_poblacion(metodo, cita, aviso,
                                                 area_km2=cuenca.area_km2)
    elif metodo in METODOS_TC_ITERATIVOS:
        dato = (cuenca.c_retardo_izzard if metodo == TC_METODO_IZZARD
                else cuenca.n_manning_superficial)
        if dato is None:
            raise _falta_dato_iterativo(cuenca)
        if intensidad_de is None:
            raise DatoFaltanteError(
                "I", id_punto=cuenca.id,
                detalle=f"el metodo «{metodo}» lleva la intensidad de la "
                        "lluvia dentro de la formula: el tiempo de "
                        "concentracion se pide con la relacion intensidad-"
                        "duracion de la cuenca (punto fijo tc <-> I)")
        if metodo == TC_METODO_IZZARD:
            cita = "MC_HHD.3.9#T05_IZZARD"
            S_flujo = cuenca.S_cauce_cuenca

            def formula_de(I_: float) -> float:
                return tc_izzard_min(i_mm_h=I_, c=dato, L_m=cuenca.L_cauce_m,
                                     S=S_flujo, id_punto=cuenca.id)
            formula = ("tc = 525 · (0.0000276·i + c) · L^0.33 / (S^0.333 · "
                       "i^0.667)   [min; i en mm/h, L en m, S en m/m]")
            S_magnitud = S
            dato_magnitud = Magnitud(
                "c", dato, "", f"columna c_retardo_izzard de {cuenca.origen}",
                cifras=CIFRAS_FINA)
        else:
            cita = "MC_HHD.3.9#T05_ONDA"
            S_flujo = cuenca.S_terreno

            def formula_de(I_: float) -> float:
                return tc_onda_cinematica_min(
                    L_m=cuenca.L_cauce_m, n=dato, I_mm_h=I_, S=S_flujo,
                    id_punto=cuenca.id)
            formula = ("tc = 7 · L^0.6 · n^0.6 / (I^0.4 · S^0.3)   "
                       "[min; L en m, I en mm/h, S en m/m]")
            S_magnitud = Magnitud(
                "S", cuenca.S_terreno, "m/m",
                f"columna S_terreno de {cuenca.origen}: la fila pide la "
                "«pendiente promedio del terreno»", cifras=CIFRAS_FINA)
            dato_magnitud = Magnitud(
                "n", dato, "",
                f"columna n_manning_superficial de {cuenca.origen}",
                cifras=CIFRAS_FINA)
        tc, I_fijo, iteraciones = _punto_fijo_tc(formula_de, intensidad_de,
                                                 id_punto=cuenca.id)
        sustitucion = (
            L, S_magnitud, dato_magnitud,
            Magnitud("i" if metodo == TC_METODO_IZZARD else "I", I_fijo,
                     "mm/h", f"la intensidad del punto fijo: la de la lluvia "
                     f"de diseño de duracion tc (paso {CODIGO_INTENSIDAD})",
                     cifras=CIFRAS_MAGNITUD))
        notas.append(
            f"PUNTO FIJO tc <-> I. La formula lleva la intensidad de la "
            "lluvia, y la intensidad depende de la duracion, que es el tiempo "
            "de concentracion que se busca: se itero tc = f(I(tc)) desde una "
            "lluvia de 24 horas, con la misma relacion intensidad-duracion y "
            f"la misma duracion minima del paso {CODIGO_INTENSIDAD}, hasta "
            f"que dos iterados difirieron menos de {TOL_REL_PUNTO_FIJO_TC:g} "
            f"relativo ({iteraciones} iteraciones). Es la «solución gráfica "
            "directa» de la observacion de la tabla, hecha numericamente.")
        if metodo == TC_METODO_IZZARD:
            cita_il = "MC_HHD.3.9#T05_IZZARD_IL"
            producto = exigir_producto_izzard(i_mm_h=I_fijo,
                                              L_m=cuenca.L_cauce_m,
                                              id_punto=cuenca.id)
            umbral = Umbral(
                descripcion="producto de la intensidad por la longitud de la "
                            "trayectoria de flujo (formula de Izzard)",
                valor=TC_IZZARD_PRODUCTO_IL_MAX, unidad="mm/h · m",
                cita_id=cita_il, caracter=_caracter(cita_il),
                aplicacion="condicion de la formula: fuera de ella el "
                           "programa no la evalua")
            veredicto = Veredicto(
                tipo=TipoDeVeredicto.CUMPLE,
                margen=TC_IZZARD_PRODUCTO_IL_MAX - producto,
                unidad="mm/h · m",
                explicacion=f"i · L = {producto:.0f} no pasa del limite")
            notas.append(
                "Las columnas L_cauce_m y S_cauce_cuenca de la fila se leen "
                "aqui como la longitud y la pendiente de la trayectoria del "
                "flujo superficial, que es lo que la formula pide. El "
                "coeficiente de retardo es un dato del estudio: la tabla lo "
                "describe de 0.0070 (pavimento muy liso) a 0.012 (pavimento "
                "de concreto) y 0.06 (pasto denso), y el programa no lo "
                "juzga contra esos valores.")
        else:
            veredicto = Veredicto(
                tipo=TipoDeVeredicto.SIN_VEREDICTO,
                explicacion="la fila de la Tabla N 05 no escribe rango de "
                            "aplicacion para esta formula")
            notas.append(_lectura_del_proyecto(cita))
    elif metodo == TC_METODO_TEMEZ:
        tc_h = tc_temez_h(L_km=cuenca.L_cauce_m / METROS_POR_KM,
                          S=cuenca.S_cauce_cuenca, area_km2=cuenca.area_km2,
                          id_punto=cuenca.id,
                          procedimiento=(
                              PROCEDIMIENTO_FUERA_DEL_RACIONAL_MODIFICADO
                              if racional_modificado else None))
        tc = tc_h * MINUTOS_POR_HORA
        formula = ("Tc = 0.3 · (L / S^0.25)^0.76   [horas; L en km, S en m/m]"
                   " ; tc = 60 · Tc [min]")
        cita = "MC_HHD.3.12.2.1#TC"
        sustitucion = (
            Magnitud("L", cuenca.L_cauce_m / METROS_POR_KM, "km",
                     f"columna L_cauce_m de {cuenca.origen}, de m a km",
                     cifras=CIFRAS_FINA),
            S,
            Magnitud("Tc", tc_h, "h", "ecuacion (30), antes de pasar a minutos",
                     cifras=CIFRAS_FINA))
        umbral = Umbral(
            descripcion="rango de tiempo de concentracion del metodo de Temez",
            valor=TC_TEMEZ_RANGO_H, unidad="h", cita_id=cita,
            caracter=_caracter(cita),
            aplicacion="rango de validez: fuera de el el programa no evalua "
                       "la formula")
        veredicto = Veredicto(
            tipo=TipoDeVeredicto.CUMPLE,
            explicacion="el tiempo de concentracion y el area estan dentro "
                        "del rango del metodo")
        if racional_modificado:
            notas.append(
                "Esta formula no es una fila de la Tabla N 05: es la "
                "ecuacion (30) del metodo racional modificado (num. "
                "3.12.2.1), que es el metodo con que se calcula el caudal de "
                f"esta cuenca de {cuenca.area_km2:g} km2. No hay uso hibrido: "
                "la intensidad, el coeficiente de escorrentia y el "
                "coeficiente de uniformidad son los del mismo metodo (pasos "
                f"{CODIGO_INTENSIDAD} a {CODIGO_RACIONAL}).")
        else:
            notas.append(
                "USO HIBRIDO, declarado. Esta formula no es una fila de la "
                "Tabla N 05: es la del tiempo de concentracion del metodo "
                "racional modificado (num. 3.12.2.1), y el caudal de este "
                "punto se calcula con la ecuacion (28) del metodo racional "
                "simple. De aquel metodo se toma el tiempo de concentracion "
                f"y, si el criterio '{CRITERIO_K_TEMEZ}' lo manda, el "
                f"coeficiente de uniformidad K (paso {CODIGO_RACIONAL}); no "
                "su intensidad ni su coeficiente de escorrentia por numero "
                "de curva, que el metodo completo usa desde 10 km2.")
    else:
        raise DatoInvalidoError(
            "metodo_tc", valor=metodo, id_punto=cuenca.id,
            motivo="los metodos de tiempo de concentracion que el programa "
                   "evalua son " + ", ".join(METODOS_TC))
    if not (math.isfinite(tc) and tc > 0):
        raise LimiteNumericoError(
            "tc", valor=tc, id_punto=cuenca.id,
            motivo=f"el tiempo de concentracion no es un numero positivo con "
                   f"L = {cuenca.L_cauce_m:g} m y S = {cuenca.S_cauce_cuenca:g} m/m")
    if aviso:
        notas.append(aviso)
    elecciones = [EleccionDeProyecto(
        que_se_adopto="metodo de tiempo de concentracion",
        valor=metodo, entre=METODOS_TC,
        de_donde=f"la columna metodo_tc de {cuenca.origen}",
        por_que="lo declara el estudio hidrologico cuenca por cuenca: cada "
                "formula salio de un tipo de cuenca y su validez depende de "
                "la pendiente y del tamaño de esta, de modo que no es un "
                "criterio unico del corredor sino un dato de la cuenca")]
    if aviso:
        elecciones.append(EleccionDeProyecto(
            que_se_adopto="trato de una cuenca fuera de la poblacion de la "
                          "formula",
            valor=POBLACION_INDICADOR,
            entre=(POBLACION_NO_EVALUABLE, POBLACION_INDICADOR),
            de_donde=f"el criterio adoptado '{CRITERIO_POBLACION_TC}' [A]",
            por_que="la tabla describe de que cuencas salio la formula y no "
                    "dice que hacer fuera de ellas; evaluarla fuera es una "
                    "extrapolacion que se declara",
            clave_criterio=CRITERIO_POBLACION_TC))
    return tc, paso(
        "FH.TC", codigo=CODIGO_TC,
        que=f"Tiempo de concentracion de la cuenca, metodo «{metodo}»",
        formula=formula, formula_cita_id=cita,
        citas_textuales=("MC_HHD.3.9#T05", cita),
        sustitucion=sustitucion,
        resultado=Magnitud("tc", tc, "min", "tiempo de concentracion",
                           cifras=CIFRAS_MAGNITUD),
        umbral=umbral, veredicto=veredicto,
        elecciones=tuple(elecciones),
        nota_del_proyecto=" ".join(notas)), ((aviso,) if aviso else ())


# ===========================================================================
# 2. Ajuste de frecuencia y bondad de ajuste (num. 3.7)
# ===========================================================================

def _estadisticos(valores: Sequence[float], que: str) -> Tuple[float, float]:
    """Media y desviacion estandar MUESTRAL (n − 1), como el num. 3.7.1.2."""
    if len(valores) < 2:
        raise DatoInvalidoError(
            "p24_mm", valor=len(valores),
            motivo=f"la serie con que se ajusta ({que}) tiene menos de 2 "
                   "años: no tiene desviacion estandar")
    media, desviacion = fmean(valores), stdev(valores)
    if not desviacion > 0:
        raise LimiteNumericoError(
            "p24_mm", valor=desviacion,
            motivo=f"la serie con que se ajusta ({que}) no tiene dispersion "
                   "(desviacion estandar nula): el ajuste divide por ella")
    return media, desviacion


def cuantil_gumbel(*, media: float, desviacion: float, TR: float) -> float:
    """
    Gumbel por momentos (num. 3.7.1.7, ec. 9): alfa = 1.2825/sigma,
    beta = mu − 0.45·sigma, y x_T = beta − ln(−ln(1 − 1/T)) / alfa.
    """
    alfa = GUMBEL_MOMENTOS["alfa_por_sigma"] / desviacion
    beta = media - GUMBEL_MOMENTOS["beta_resta_sigmas"] * desviacion
    return beta - math.log(-math.log(1 - 1 / TR)) / alfa


def _modelo(distribucion: str, valores: Sequence[float]):
    """
    (parametros, F, cuantil) de una distribucion ajustada a `valores` con el
    estimador que el Manual imprime. Solo las tres de
    `DISTRIBUCIONES_CON_ESTIMADOR_IMPRESO`.
    """
    if distribucion == "normal":
        # num. 3.7.1.1: mu = media aritmetica, S = desviacion estandar.
        media, s = _estadisticos(valores, "normal")
        normal = NormalDist(media, s)
        return ((("mu", media), ("S", s)), normal.cdf,
                lambda TR: normal.inv_cdf(1 - 1 / TR))
    if distribucion == "lognormal_2p":
        # num. 3.7.1.2: Y y Sy son la media y la desviacion (n − 1) de los
        # logaritmos. Se usa el natural para ajustar y para invertir.
        if not min(valores) > 0:
            raise _no_evaluable(
                "P24(TR)",
                "la serie trae al menos un año con 0 mm y la log normal se "
                "ajusta sobre los logaritmos, que no existen en 0",
                f"declarar en '{CRITERIO_DISTRIBUCION}' la normal, la Gumbel "
                f"o '{MEJOR_AJUSTE_KS}', que la excluye diciendolo")
        logs = [math.log(v) for v in valores]
        Y, Sy = _estadisticos(logs, "log normal")
        normal = NormalDist(Y, Sy)
        return ((("Y", Y), ("Sy", Sy)),
                lambda x: normal.cdf(math.log(x)),
                lambda TR: math.exp(normal.inv_cdf(1 - 1 / TR)))
    if distribucion == "gumbel":
        media, s = _estadisticos(valores, "Gumbel")
        alfa = GUMBEL_MOMENTOS["alfa_por_sigma"] / s
        beta = media - GUMBEL_MOMENTOS["beta_resta_sigmas"] * s
        return ((("alfa", alfa), ("beta", beta)),
                lambda x: math.exp(-math.exp(-alfa * (x - beta))),
                lambda TR: cuantil_gumbel(media=media, desviacion=s, TR=TR))
    if distribucion in DISTRIBUCIONES_3_7_1:
        raise _no_evaluable(
            "P24(TR)",
            f"el Manual lista la «{DISTRIBUCIONES_3_7_1[distribucion]}» en su "
            "num. 3.7.1 e imprime su funcion, pero no como se estiman sus "
            "parametros; el programa ajusta solo las que traen el estimador "
            "impreso (" + ", ".join(DISTRIBUCIONES_CON_ESTIMADOR_IMPRESO) + ")",
            f"declarar en '{CRITERIO_DISTRIBUCION}' una de las tres "
            f"evaluables o '{MEJOR_AJUSTE_KS}', o una fuente que fije el "
            "estimador de esa distribucion")
    raise DatoInvalidoError(
        CRITERIO_DISTRIBUCION, valor=distribucion,
        motivo="no es una distribucion del num. 3.7.1 del Manual")


def estadistico_ks(valores: Sequence[float], F) -> float:
    """
    D = max |Fo(xm) − F(xm)| (num. 3.7.2 b), con la probabilidad observada de
    la ecuacion (13): Fo(xm) = 1 − m/(n + 1), m el numero de orden del dato
    en una lista de MAYOR a menor.
    """
    n = len(valores)
    ordenados = sorted(valores, reverse=True)
    return max(abs((1 - m / (n + 1)) - F(x))
               for m, x in enumerate(ordenados, start=1))


def valor_critico_ks(n: int, alfa: float) -> Tuple[float, str]:
    """
    El valor critico d de Kolmogorov-Smirnov y de donde sale.

    En un n tabulado y con un alfa de columna, la celda de la Tabla N 03. En
    cualquier otro caso --n intermedio, n > 40 o alfa que no es columna-- el
    cuantil exacto del mismo estadistico (`scipy.stats.kstwo`), que es como
    el proyecto cierra la laguna de la tabla: reproduce sus 24 celdas a dos
    decimales (ver la `Laguna` de `MC_HHD.T03` y su test).
    """
    fila = TABLA_03_KS.get(n)
    if fila is not None:
        for columna, d in fila.items():
            if math.isclose(columna, alfa):
                return d, (f"Tabla N 03, fila n = {n}, columna alfa = "
                           f"{columna:g}")
    from scipy.stats import kstwo   # perezoso: solo si la tabla no alcanza
    d = float(kstwo.ppf(1 - alfa, n))
    return d, (f"cuantil exacto 1 − alfa del estadistico de "
               f"Kolmogorov-Smirnov para n = {n} y alfa = {alfa:g}: la Tabla "
               "N 03 no tiene esa fila o esa columna, y este calculo "
               "reproduce sus 24 celdas impresas")


def numero_de_intervalos(n: int, regla: str) -> int:
    """
    El numero k de intervalos de clase de la prueba chi-cuadrado (num. 3.7.2
    a), que el Manual pide y no fija: la regla la declara el criterio
    'intervalos_de_clase_chi_cuadrado' [A]. Sturges: k = 1 + ⌈log2 n⌉;
    raiz de n: k = ⌈√n⌉.
    """
    if regla == INTERVALOS_STURGES:
        return 1 + math.ceil(math.log2(n))
    if regla == INTERVALOS_RAIZ_DE_N:
        return math.ceil(math.sqrt(n))
    raise DatoInvalidoError(
        CRITERIO_INTERVALOS_CHI2, valor=regla,
        motivo=f"las reglas admitidas son {INTERVALOS_STURGES} y "
               f"{INTERVALOS_RAIZ_DE_N}")


def estadistico_chi_cuadrado(valores: Sequence[float], F, k: int,
                             ) -> Tuple[float, Tuple[int, ...],
                                        Tuple[float, ...]]:
    """
    D = Σ (θi − εi)² / εi, ecuacion (12) del num. 3.7.2 a) (pag. impresa
    31), con εi = n[F(Si) − F(Ii)]: (D, observados, esperados).

    Los k intervalos de clase son de IGUAL AMPLITUD entre el menor y el
    mayor dato, con el primero abierto por abajo y el ultimo por arriba
    (F = 0 y F = 1 en los extremos), para que los esperados sumen n: lectura
    del proyecto de «intervalos de clase», escrita en la justificacion del
    criterio 'intervalos_de_clase_chi_cuadrado'. Un dato en un limite cae en
    el intervalo de abajo (intervalos (Ii, Si]).
    """
    n = len(valores)
    menor, mayor = min(valores), max(valores)
    ancho = (mayor - menor) / k
    limites = [menor + ancho * i for i in range(1, k)]
    observados = [0] * k
    for x in valores:
        observados[sum(1 for lim in limites if x > lim)] += 1
    acumulada = [0.0, *(F(lim) for lim in limites), 1.0]
    esperados = tuple(n * (acumulada[i + 1] - acumulada[i]) for i in range(k))
    if not all(e > 0 for e in esperados):
        raise LimiteNumericoError(
            "D chi-cuadrado", valor=min(esperados),
            motivo="un intervalo de clase tiene cero eventos esperados y la "
                   "ecuacion (12) divide por el")
    D = sum((o - e) ** 2 / e for o, e in zip(observados, esperados))
    return D, tuple(observados), esperados


@dataclass(frozen=True)
class _ChiCuadrado:
    """La prueba chi-cuadrado de una distribucion (num. 3.7.2 a)."""

    regla: str
    k: int
    nu: int
    D: float
    critico: float
    observados: Tuple[int, ...]
    esperados: Tuple[float, ...]

    @property
    def acepta(self) -> bool:
        return self.D <= self.critico


def prueba_chi_cuadrado(valores: Sequence[float], distribucion: str, *,
                        alfa: float, regla: str) -> Optional[_ChiCuadrado]:
    """
    La prueba chi-cuadrado del num. 3.7.2 a) (pag. impresa 31): se acepta si
    D ≤ X²(1 − alfa, k − 1 − m), con m el numero de parametros estimados de
    los datos. None si los grados de libertad no son positivos (serie
    demasiado corta para la regla).

    Solo para las distribuciones de `DISTRIBUCIONES_CHI2`: el numeral dice
    que la prueba «se aplica para verificar bondad de las distribuciones
    normales y log normales». El valor critico es el cuantil 1 − alfa de la
    distribucion chi-cuadrado (`scipy.stats.chi2`), que el Manual no tabula.
    """
    if distribucion not in DISTRIBUCIONES_CHI2:
        raise _no_evaluable(
            "chi-cuadrado",
            f"el num. 3.7.2 a) dice que la prueba chi-cuadrado se aplica a "
            f"las distribuciones normales y log normales, y la "
            f"«{distribucion}» no lo es",
            "la prueba de Kolmogorov-Smirnov, que es la que el programa "
            "aplica a todas")
    parametros, F, _ = _modelo(distribucion, valores)
    k = numero_de_intervalos(len(valores), regla)
    nu = k - 1 - len(parametros)
    if nu < 1:
        return None
    D, observados, esperados = estadistico_chi_cuadrado(valores, F, k)
    from scipy.stats import chi2   # perezoso: solo si la prueba se hace
    return _ChiCuadrado(regla=regla, k=k, nu=nu, D=D,
                        critico=float(chi2.ppf(1 - alfa, nu)),
                        observados=observados, esperados=esperados)


def _ajustar(valores: Sequence[float], distribucion: str, *, TR: float,
             alfa: float) -> AjusteDeDistribucion:
    """
    Una distribucion ajustada, su prueba K-S y su cuantil (num. 3.7).

    PRIVADA A PROPOSITO (auditoria de T-1): recibe una lista de numeros, no
    una serie, de modo que no sabe que años son FEN ni que se decidio hacer
    con ellos. La puerta publica es `precipitacion_de_diseno`, que no ajusta
    nada sin el criterio 'homogeneidad_serie_fen' declarado.
    """
    bondad, cuantil = _bondad(valores, distribucion, alfa=alfa)
    return AjusteDeDistribucion(
        distribucion=distribucion, parametros=bondad.parametros, n=bondad.n,
        D=bondad.D, d_critico=bondad.d_critico, alfa=alfa,
        acepta=bondad.acepta, P_TR_mm=cuantil(TR))


@dataclass(frozen=True)
class _Bondad:
    """
    La prueba de bondad de una distribucion ajustada, SIN cuantil (VE-4b):
    lo que `_ajustar` calcula antes de saber el periodo de retorno. Lo usa
    tambien el pre-vuelo (`anticipar_caudal`), que no tiene TR: que una
    distribucion pase o no la prueba de Kolmogorov-Smirnov no depende de el.
    """

    distribucion: str
    parametros: Tuple[Tuple[str, float], ...]
    n: int
    D: float
    d_critico: float

    @property
    def acepta(self) -> bool:
        return self.D < self.d_critico


def _bondad(valores: Sequence[float], distribucion: str, *,
            alfa: float) -> Tuple[_Bondad, Any]:
    """(prueba de bondad, funcion cuantil de TR) de una distribucion (num. 3.7.2)."""
    parametros, F, cuantil = _modelo(distribucion, valores)
    n = len(valores)
    d, _ = valor_critico_ks(n, alfa)
    return _Bondad(distribucion=distribucion, parametros=parametros, n=n,
                   D=estadistico_ks(valores, F), d_critico=d), cuantil


def _elegir(valores: Sequence[float], declarada: str, *, TR: float,
            alfa: float) -> Tuple[AjusteDeDistribucion,
                                  Tuple[AjusteDeDistribucion, ...],
                                  Tuple[Tuple[str, str], ...]]:
    """
    (ajuste adoptado, todos los evaluados, las excluidas con su motivo). Con
    `mejor_ajuste_ks`, el de menor D entre las evaluables (num. 3.7.2 b: «la
    de mejor ajuste»); con una distribucion declarada, esa, y las otras solo
    para comparar.

    Una distribucion que la serie no admite --la log normal con un año de
    0 mm-- queda EXCLUIDA diciendolo, y no detiene a las demas; si es la
    declarada, se detiene.
    """
    return _elegir_con(
        valores, declarada,
        lambda distribucion: _ajustar(valores, distribucion, TR=TR, alfa=alfa))


def _elegir_con(valores: Sequence[float], declarada: str, evaluar):
    """
    La REGLA de eleccion de `_elegir`, con la evaluacion de cada distribucion
    como argumento (VE-4b): `_elegir` la evalua con su cuantil
    (`_ajustar`) y el pre-vuelo solo con su prueba de bondad (`_bondad`),
    porque no tiene periodo de retorno. Una sola regla para los dos: el
    pre-vuelo no puede adoptar otra distribucion que la corrida.
    """
    n = len(valores)
    if n < KS_N_MINIMO_TABULADO:
        raise _no_evaluable(
            "P24(TR)",
            f"la serie que entra al ajuste tiene {n} años y la Tabla N 03 de "
            f"valores criticos empieza en n = {KS_N_MINIMO_TABULADO}: por "
            "debajo no hay prueba de bondad que hacer ni ajuste que defender",
            "una serie mas larga u otra estacion, o el caudal de un estudio "
            "hidrologico en la columna Q_m3s")
    if declarada not in DISTRIBUCIONES_CON_ESTIMADOR_IMPRESO \
            and declarada != MEJOR_AJUSTE_KS:
        _modelo(declarada, valores)          # lanza: no evaluable o invalida
    evaluados: List[Any] = []
    excluidas: List[Tuple[str, str]] = []
    for distribucion in DISTRIBUCIONES_CON_ESTIMADOR_IMPRESO:
        try:
            evaluados.append(evaluar(distribucion))
        except MetodoNoEvaluableError as error:
            if distribucion == declarada:
                raise
            excluidas.append((distribucion, error.motivo))
    if declarada == MEJOR_AJUSTE_KS:
        adoptado = min(evaluados, key=lambda a: a.D)
    else:
        adoptado = next(a for a in evaluados if a.distribucion == declarada)
    return adoptado, tuple(evaluados), tuple(excluidas)


def _contraste_chi_cuadrado(valores: Sequence[float], distribucion: str, *,
                            alfa: float,
                            ) -> Tuple[str, Tuple[EleccionDeProyecto, ...],
                                       Tuple[str, ...]]:
    """
    (nota, elecciones, citas) del contraste chi-cuadrado (num. 3.7.2 a) que
    el paso de la bondad de ajuste imprime al lado de Kolmogorov-Smirnov
    (VE-5, ficha T1-01). NO detiene ni elige: la prueba que acepta es la de
    Kolmogorov-Smirnov. Con una distribucion que no es normal ni log normal
    no lee el criterio de los intervalos y solo dice que no se aplica.
    """
    cita_alcance = "MC_HHD.3.7.2a#ALCANCE"
    if distribucion not in DISTRIBUCIONES_CHI2:
        return (f"Contraste chi-cuadrado (num. 3.7.2 a): no se aplica a la "
                f"«{distribucion}»; el numeral dice que la prueba «se aplica "
                "para verificar bondad de las distribuciones normales y log "
                "normales».", (), (cita_alcance,))
    regla = ca.valor(CRITERIO_INTERVALOS_CHI2)
    prueba = prueba_chi_cuadrado(valores, distribucion, alfa=alfa, regla=regla)
    citas = ("MC_HHD.3.7.2a", "MC_HHD.3.7.2a#INTERVALOS", cita_alcance)
    k = numero_de_intervalos(len(valores), regla)
    entre = tuple(
        f"{r}: k = {numero_de_intervalos(len(valores), r)}"
        for r in ca.criterio(CRITERIO_INTERVALOS_CHI2).sensibilidad)
    eleccion_k = EleccionDeProyecto(
        que_se_adopto="regla del numero de intervalos de clase de la prueba "
                      "chi-cuadrado",
        valor=f"{regla}: k = {k}", entre=entre,
        de_donde=f"el criterio adoptado '{CRITERIO_INTERVALOS_CHI2}' [A]",
        por_que="el num. 3.7.2 a) pide dividir los datos en k intervalos de "
                "clase y no fija k; la prueba es un contraste y no decide",
        cita_id="MC_HHD.3.7.2a#INTERVALOS",
        clave_criterio=CRITERIO_INTERVALOS_CHI2)
    if prueba is None:
        return (f"Contraste chi-cuadrado (num. 3.7.2 a): con {len(valores)} "
                f"años y la regla '{regla}' hay k = {k} intervalos y ningun "
                "grado de libertad (ν = k − 1 − m < 1): no se evalua.",
                (eleccion_k,), citas)
    juicio = ("se aceptaria tambien por esta prueba" if prueba.acepta else
              "NO se aceptaria por esta prueba; la que decide es la de "
              "Kolmogorov-Smirnov")
    return (f"Contraste chi-cuadrado (num. 3.7.2 a, ecuacion 12), que no "
            f"detiene ni elige: k = {prueba.k} intervalos de igual amplitud "
            f"entre el menor y el mayor dato (regla '{regla}'), observados "
            f"{list(prueba.observados)}, esperados "
            f"[{', '.join(f'{e:.2f}' for e in prueba.esperados)}]; D = "
            f"{prueba.D:.3f} frente a X²(1 − {alfa:g}, {prueba.nu}) = "
            f"{prueba.critico:.3f}: {juicio}.", (eleccion_k,), citas)


def _registros_por_tratamiento(serie: SerieDeEstacion, tratamiento: str,
                               ) -> Tuple[RegistroDeLluvia, ...]:
    if tratamiento == FEN_SERIE_SIN_FEN:
        return tuple(r for r in serie.registros if not r.fen)
    return serie.registros


def _cubre_lo_observado(registros: Sequence[RegistroDeLluvia], TR: float,
                        ) -> Optional[Tuple[RegistroDeLluvia, int, float]]:
    """
    El año de la serie que la lluvia de diseño tendria que cubrir: el MAYOR
    registro cuyo periodo de retorno empirico no supera el de diseño.

    La ecuacion (13) del num. 3.7.2 b) da al dato de orden m, en una lista de
    mayor a menor, la probabilidad observada Fo = 1 − m/(n + 1); su periodo
    de retorno empirico es (n + 1)/m. El menor m que cumple (n + 1)/m <= TR
    es el de la mayor lluvia que, segun la propia serie, se iguala o supera
    en promedio una vez cada TR años o menos. Devuelve (registro, m, T
    empirico), o None si ningun dato cumple (TR menor que (n + 1)/n).

    NO es un umbral del Manual ni un numero elegido: es la serie contrastada
    consigo misma con la probabilidad que la prueba de bondad ya usa.
    """
    n = len(registros)
    m = math.ceil((n + 1) / TR)
    if not 1 <= m <= n:
        return None
    ordenados = sorted(registros, key=lambda r: r.p24_mm, reverse=True)
    return ordenados[m - 1], m, (n + 1) / m


# --- VE-4b --- LAS COMPUERTAS DEL AJUSTE, ESCRITAS UNA VEZ. Las levanta
# `precipitacion_de_diseno` y las anticipa el pre-vuelo (`anticipar_caudal`):
# el mensaje del `Bloqueo` real y el de la fila del pre-vuelo son el mismo
# texto, construido aqui.

def _no_evaluable_dos_poblaciones(id_punto: Optional[str]) -> MetodoNoEvaluableError:
    return _no_evaluable(
        "P24(TR)",
        "el tratamiento 'dos_poblaciones' pide un analisis de poblacion "
        "mixta (una distribucion para los años FEN, otra para los "
        "neutros, combinadas por su probabilidad de ocurrencia) y ni el "
        "Manual de Hidrologia ni ninguna fuente de normas/ da ese "
        "procedimiento",
        f"declarar '{FEN_SERIE_COMPLETA}' o '{FEN_SERIE_SIN_FEN}' en "
        f"'{CRITERIO_FEN}', o el caudal de un estudio hidrologico que "
        "haga el analisis de poblacion mixta, en la columna Q_m3s",
        id_punto)


def _no_evaluable_ks(adoptado, evaluados, *, serie: SerieDeEstacion,
                     tratamiento: str, alfa: float,
                     id_punto: Optional[str]) -> MetodoNoEvaluableError:
    """La distribucion adoptada no pasa K-S (`adoptado` con .D, .d_critico, .n)."""
    return _no_evaluable(
        "P24(TR)",
        f"la distribucion «{adoptado.distribucion}» no pasa la prueba de "
        f"Kolmogorov-Smirnov sobre la serie de «{serie.estacion}» con el "
        f"tratamiento '{tratamiento}': D = {adoptado.D:.4f} no es menor "
        f"que d = {adoptado.d_critico:.4f} (n = {adoptado.n}, alfa = "
        f"{alfa:g}). Las evaluadas: "
        + "; ".join(f"{a.distribucion} D = {a.D:.4f}" for a in evaluados),
        f"otra distribucion o regla en '{CRITERIO_DISTRIBUCION}', otro "
        f"tratamiento en '{CRITERIO_FEN}', o el caudal de un estudio "
        "hidrologico en la columna Q_m3s",
        id_punto)


def _procedimiento_del_otro_tratamiento(otro: str) -> str:
    return (f"declarar '{otro}' en '{CRITERIO_FEN}', o traer el caudal "
            "del estudio hidrologico en la columna Q_m3s")


def _serie_con_factor(serie: SerieDeEstacion, factor: float) -> SerieDeEstacion:
    """La serie con cada maximo anual multiplicado por el factor de intervalo fijo."""
    return SerieDeEstacion(
        estacion=serie.estacion, origen=serie.origen,
        registros=tuple(RegistroDeLluvia(anio=r.anio, p24_mm=r.p24_mm * factor,
                                         fen=r.fen)
                        for r in serie.registros))


def precipitacion_de_diseno(serie: SerieDeEstacion, TR: float, *,
                            id_punto: Optional[str] = None,
                            ) -> Tuple[AjusteDeDistribucion,
                                       Tuple[AjusteDeDistribucion, ...],
                                       str, Tuple[PasoDeMemoria, ...],
                                       Tuple[str, ...]]:
    """
    La precipitacion maxima en 24 horas del periodo de retorno `TR`, por
    ajuste de frecuencia de la serie de la estacion (num. 3.4 y 3.7).

    Devuelve (ajuste adoptado, ajustes evaluados, tratamiento FEN, pasos,
    avisos). SE DETIENE con `CriterioPendienteError` si
    'homogeneidad_serie_fen' no esta declarado: sin saber que se hace con los
    años FEN no hay serie que ajustar (T-1, punto 3). Es la UNICA puerta
    publica al ajuste.

    Los cinco pasos: la serie y su tratamiento (1b.1), el ajuste contrastado
    con lo ya observado (1b.2), la bondad (1b.3), el juicio del tratamiento
    FEN contra la regla de la hoja de ruta (1b.3b) y, desde VE-2, el aviso
    de consistencia de la serie, sin umbral (1b.3c, `_paso_consistencia`).

    SE DETIENE TAMBIEN, con `MetodoNoEvaluableError`, cuando `serie_sin_fen`
    da MENOS lluvia que la serie completa: la hoja de ruta manda adoptar el
    mas conservador de los dos ajustes, y un punto no se dimensiona sobre un
    caudal que lo incumple. El mensaje trae las dos lluvias y el remedio.
    """
    if not TR > 1:
        raise DatoInvalidoError(
            "TR", valor=TR, id_punto=id_punto,
            motivo="el periodo de retorno tiene que ser mayor de 1 año: con "
                   "T = 1 la probabilidad de no excedencia 1 − 1/T es cero y "
                   "ninguna distribucion tiene cuantil")
    tratamiento = ca.valor(CRITERIO_FEN)            # CriterioPendienteError
    if tratamiento == FEN_DOS_POBLACIONES:
        raise _no_evaluable_dos_poblaciones(id_punto)
    if tratamiento not in (FEN_SERIE_COMPLETA, FEN_SERIE_SIN_FEN):
        raise DatoInvalidoError(
            CRITERIO_FEN, valor=tratamiento, id_punto=id_punto,
            motivo="los tratamientos admitidos son "
                   f"{FEN_SERIE_COMPLETA}, {FEN_SERIE_SIN_FEN} y "
                   f"{FEN_DOS_POBLACIONES}")
    declarada = ca.valor(CRITERIO_DISTRIBUCION)
    alfa = ca.valor(CRITERIO_ALFA)

    # --- VE-2 (d) --- EL FACTOR DE INTERVALO FIJO, a la SERIE y antes del
    # ajuste (ficha VE2-D): corrige cada lectura, de modo que el contraste
    # con lo observado (1b.2) y el de los años FEN (1b.3b) comparan lo mismo;
    # y como las tres distribuciones que se ajustan son de escala, el cuantil
    # sale EXACTAMENTE multiplicado por el factor. Con el valor de archivo
    # (1.00, el Manual) cada dato se multiplica por 1.0 y no cambia en ningun
    # bit. El aviso de consistencia (1b.3c) sigue hablando de la serie
    # REGISTRADA, que es `serie_registrada`.
    factor = ca.valor(CRITERIO_FACTOR_P24)
    if not factor > 0:
        raise DatoInvalidoError(
            CRITERIO_FACTOR_P24, valor=factor, id_punto=id_punto,
            motivo="el factor multiplica la lluvia de la serie y tiene que "
                   "ser positivo")
    serie_registrada = serie
    serie = _serie_con_factor(serie, factor)

    anios_fen = serie.anios_fen
    registros = _registros_por_tratamiento(serie, tratamiento)
    valores = tuple(r.p24_mm for r in registros)
    adoptado, evaluados, excluidas = _elegir(valores, declarada, TR=TR,
                                             alfa=alfa)

    # El contraste que la hoja de ruta pide («reportar el ajuste con y sin
    # ellos»): la misma regla de eleccion sobre la otra serie. NO PUEDE
    # DETENER el calculo adoptado: si la otra serie no se deja ajustar --una
    # estacion con todos los años FEN no tiene serie sin ellos-- se dice por
    # que y el contraste queda sin numero.
    otro = (FEN_SERIE_SIN_FEN if tratamiento == FEN_SERIE_COMPLETA
            else FEN_SERIE_COMPLETA)
    contraste: Optional[AjusteDeDistribucion] = None
    sin_contraste = ""
    if not anios_fen:
        sin_contraste = "la serie no declara ningun año FEN"
    else:
        try:
            contraste, _, _ = _elegir(
                tuple(r.p24_mm for r in _registros_por_tratamiento(serie, otro)),
                declarada, TR=TR, alfa=alfa)
        except ErrorProyecto as error:
            sin_contraste = (f"la serie '{otro}' no se puede ajustar "
                             f"({type(error).__name__}: {error})")

    avisos: List[str] = []
    n_total, n = len(serie.registros), len(valores)
    anios = [r.anio for r in serie.registros]
    presentes = set(anios)
    faltantes = [a for a in range(min(anios), max(anios) + 1)
                 if a not in presentes]
    if not anios_fen:
        avisos.append(
            f"La serie de la estacion «{serie.estacion}» no declara ningun "
            "año FEN. La Fase 1-bis de la hoja de ruta dice que, si la serie "
            "no contiene los años del fenomeno El Niño extraordinario, el "
            "caudal de diseño esta subestimado de forma grave y eso es una "
            "limitacion central que la memoria tiene que declarar.")
    cita_registro = "MC_HHD.3.4#REGISTRO"
    corta = n < REGISTRO_MINIMO_RECOMENDADO_ANIOS
    if corta:
        avisos.append(
            f"La serie que entra al ajuste tiene {n} años, menos de los "
            f"{REGISTRO_MINIMO_RECOMENDADO_ANIOS} que el Manual recomienda "
            f"(num. 3.4): la extrapolacion a {TR:g} años de periodo de "
            "retorno es poco confiable, y la prueba de bondad de una serie "
            "corta rechaza muy poco.")
    if faltantes:
        avisos.append(
            f"La serie de «{serie.estacion}» no es continua: entre "
            f"{min(anios)} y {max(anios)} faltan {len(faltantes)} años ("
            + ", ".join(str(a) for a in faltantes) + "). El programa ajusta "
            "los años que hay y no rellena los que faltan; si entre ellos "
            "hay un año del fenomeno El Niño, la lluvia de diseño esta "
            "subestimada.")
    for distribucion, motivo in excluidas:
        avisos.append(f"La distribucion «{distribucion}» quedo fuera de la "
                      f"comparacion: {motivo}.")
    if not math.isclose(factor, 1):
        avisos.append(
            f"La serie de «{serie.estacion}» entro al ajuste con cada maximo "
            f"anual multiplicado por {factor:g} (criterio "
            f"'{CRITERIO_FACTOR_P24}' [A]): el Manual usa la maxima en 24 "
            "horas sin conversion (num. 3.8.1) y el factor es una practica "
            "sin fuente en el repositorio de normas. La lluvia de diseño y "
            "lo observado con que se contrasta suben en esa proporcion.")

    entre = [f"{tratamiento}: P24(TR) = {adoptado.P_TR_mm:.1f} mm "
             f"({adoptado.distribucion}, n = {adoptado.n})"]
    if contraste is not None:
        entre.append(f"{otro}: P24(TR) = {contraste.P_TR_mm:.1f} mm "
                     f"({contraste.distribucion}, n = {contraste.n})")
    else:
        entre.append(f"{otro}: sin numero ({sin_contraste})")
    entre.append(f"{FEN_DOS_POBLACIONES}: no evaluable (sin procedimiento "
                 "en las fuentes del expediente)")
    paso_serie = paso(
        "FH.SERIE", codigo=CODIGO_SERIE,
        que=(f"Serie de precipitacion maxima en 24 h de la estacion "
             f"«{serie.estacion}» y tratamiento de sus años FEN"),
        formula="n = años de la serie que entran al ajuste",
        citas_textuales=("MC_HHD.3.4#FEN", cita_registro,
                         "MC_HHD.3.12.5#PIURA"),
        sustitucion=(
            Magnitud("n_total", n_total, "años",
                     f"registros de {serie.origen}"),
            Magnitud("periodo", f"{min(anios)} a {max(anios)}", "",
                     "primer y ultimo año de la serie"),
            Magnitud("años sin dato",
                     ", ".join(str(a) for a in faltantes) or "ninguno", "",
                     "años del periodo que el archivo no trae: el programa "
                     "no los rellena"),
            Magnitud("años FEN",
                     ", ".join(str(a) for a in anios_fen) or "ninguno", "",
                     f"columna fen de {serie.origen}: los declara quien "
                     "entrega la serie, no el programa"),
            Magnitud("tratamiento", tratamiento, "",
                     f"criterio adoptado '{CRITERIO_FEN}' [A]")),
        resultado=Magnitud("n", n, "años",
                           "años con que se ajusta la distribucion"),
        umbral=Umbral(
            descripcion="longitud minima de registro recomendada",
            valor=REGISTRO_MINIMO_RECOMENDADO_ANIOS, unidad="años",
            cita_id=cita_registro, caracter=_caracter(cita_registro),
            aplicacion="indicador: una serie mas corta no detiene el "
                       "calculo, se imprime como aviso"),
        veredicto=Veredicto(
            tipo=(TipoDeVeredicto.INDICADOR if corta
                  else TipoDeVeredicto.CUMPLE),
            margen=float(n - REGISTRO_MINIMO_RECOMENDADO_ANIOS), unidad="años",
            explicacion=("la serie que entra al ajuste es mas corta que lo "
                         "que el Manual recomienda: la extrapolacion al "
                         "periodo de retorno es menos confiable" if corta
                         else "la serie alcanza la longitud recomendada")),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="tratamiento de los años FEN de la serie",
            valor=tratamiento, entre=tuple(entre),
            de_donde=f"el criterio adoptado '{CRITERIO_FEN}' [A]",
            por_que="el Manual manda incluir los años del fenomeno El Niño "
                    "y evaluarlos para no sobredimensionar, y no dice como: "
                    "la decision es del proyectista y se imprime con la "
                    "precipitacion de diseño de las dos series para que la "
                    "diferencia quede a la vista. La regla de la hoja de "
                    f"ruta la juzga el paso {CODIGO_FEN}",
            clave_criterio=CRITERIO_FEN),),
        nota_del_proyecto=" ".join(a for a in avisos))

    # --- 1b.2: el ajuste, contrastado con lo que la estacion ya registro ---
    z_o_y = {"gumbel": "x_T = beta − ln(−ln(1 − 1/T)) / alfa ; "
                       "alfa = 1.2825/sigma ; beta = mu − 0.45·sigma",
             "normal": "x_T = mu + z_T · S ; z_T = cuantil normal de 1 − 1/T",
             "lognormal_2p": "x_T = exp(Y + z_T · Sy) ; Y, Sy = media y "
                             "desviacion (n − 1) de ln x"}[adoptado.distribucion]
    cita_dist = {"gumbel": "MC_HHD.3.7.1.7", "normal": "MC_HHD.3.7.1.1",
                 "lognormal_2p": "MC_HHD.3.7.1.2"}[adoptado.distribucion]
    cita_ks = "MC_HHD.3.7.2b"
    observado = _cubre_lo_observado(registros, TR)
    umbral_obs: Optional[Umbral] = None
    notas_ajuste: List[str] = []
    if adoptado.distribucion == "gumbel":
        notas_ajuste.append(_lectura_del_proyecto(cita_dist))
    if observado is None:
        veredicto_ajuste = Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="ningun año de la serie tiene un periodo de retorno "
                        "empirico que no supere el de diseño: no hay "
                        "registro con que contrastar la lluvia de diseño")
    else:
        registro, m, T_empirico = observado
        cubre = not adoptado.P_TR_mm < registro.p24_mm
        umbral_obs = Umbral(
            descripcion=(f"mayor lluvia registrada cuyo periodo de retorno "
                         f"empirico no supera el de diseño (año "
                         f"{registro.anio}, T empirico = {T_empirico:.1f} "
                         "años)"),
            valor=registro.p24_mm, unidad="mm", cita_id=cita_ks,
            caracter=_caracter(cita_ks),
            aplicacion="indicador, no detiene el calculo: es la serie "
                       "contrastada consigo misma. La ecuacion (13) da al "
                       "dato de orden m el periodo de retorno empirico "
                       "(n + 1)/m; una lluvia ya registrada con un periodo "
                       "de retorno que no supera el de diseño deberia quedar "
                       "cubierta por la lluvia de diseño. El Manual no "
                       "escribe este contraste")
        veredicto_ajuste = Veredicto(
            tipo=TipoDeVeredicto.CUMPLE if cubre else TipoDeVeredicto.INDICADOR,
            margen=adoptado.P_TR_mm - registro.p24_mm, unidad="mm",
            explicacion=("la lluvia de diseño cubre lo ya registrado para "
                         "ese periodo de retorno" if cubre else
                         "la lluvia de diseño queda POR DEBAJO de una lluvia "
                         "que la estacion ya registro y cuyo periodo de "
                         "retorno empirico no supera el de diseño"))
        if not cubre:
            piura = _REG.cita("MC_HHD.3.12.5#PIURA")
            aviso = (
                f"La precipitacion de diseño P24({TR:g} años) = "
                f"{adoptado.P_TR_mm:.1f} mm queda POR DEBAJO de "
                f"{registro.p24_mm:.1f} mm, que la estacion "
                f"«{serie.estacion}» registro en {registro.anio} y cuyo "
                f"periodo de retorno empirico es {T_empirico:.1f} años "
                f"(ecuacion 13: (n + 1)/m con n = {n} y m = {m}). La "
                f"distribucion «{adoptado.distribucion}» pasa la prueba de "
                f"Kolmogorov-Smirnov y aun asi no cubre lo observado: la "
                "prueba mide el ajuste del conjunto de la serie, no el de "
                "sus extremos. El Manual advierte que hay "
                f"«{piura.texto_literal.texto}» ({piura.como_texto()}). El "
                "programa no corrige la lluvia de diseño: lo avisa.")
            avisos.append(aviso)
            notas_ajuste.append(aviso)
    paso_ajuste = paso(
        "FH.AJUSTE", codigo=CODIGO_AJUSTE,
        que=(f"Precipitacion maxima en 24 h para TR = {TR:g} años, "
             f"distribucion «{adoptado.distribucion}»"),
        formula=z_o_y, formula_cita_id=cita_dist,
        citas_textuales=("MC_HHD.3.7.1", cita_dist),
        sustitucion=(
            Magnitud("T", TR, "años",
                     "periodo de retorno de la Fase 2 (Tabla N 02)"),
            Magnitud("f_24h", factor, "",
                     f"criterio adoptado '{CRITERIO_FACTOR_P24}' [A]: "
                     "multiplica cada maximo anual de la serie ANTES del "
                     "ajuste (1.00: la serie tal cual, como el Manual)",
                     cifras=CIFRAS_FINA),
            *(Magnitud(nombre, valor, "", "estimado de la serie con la "
                       "expresion que el Manual imprime", cifras=CIFRAS_FINA)
              for nombre, valor in adoptado.parametros)),
        resultado=Magnitud("P24(TR)", adoptado.P_TR_mm, "mm",
                           "precipitacion maxima en 24 horas de diseño",
                           cifras=CIFRAS_MAGNITUD),
        umbral=umbral_obs, veredicto=veredicto_ajuste,
        elecciones=(EleccionDeProyecto(
            que_se_adopto="distribucion de probabilidad",
            valor=adoptado.distribucion,
            entre=(*(f"{a.distribucion}: P24(TR) = {a.P_TR_mm:.1f} mm, "
                     f"D = {a.D:.4f}" for a in evaluados),
                   *(f"{d}: no evaluable con esta serie" for d, _ in excluidas)),
            de_donde=(f"el criterio adoptado '{CRITERIO_DISTRIBUCION}' [A] "
                      f"= {declarada}"),
            por_que="el Manual recomienda ocho distribuciones sin preferir "
                    "ninguna y permite elegir por la prueba de "
                    "Kolmogorov-Smirnov; se ajustan las tres cuyo estimador "
                    "imprime, y la tabla de alternativas muestra cuanto "
                    "cambia la lluvia de diseño con cada una",
            cita_id="MC_HHD.3.7.2b#ELIGE",
            clave_criterio=CRITERIO_DISTRIBUCION),
            eleccion(
                "FH.FACTOR_P24",
                que_se_adopto=("factor de intervalo fijo de la serie de 24 "
                               "horas"),
                valor=factor,
                entre=tuple(
                    f"{f:.2f}: P24(TR) = {adoptado.P_TR_mm / factor * f:.1f} mm"
                    for f in ca.criterio(CRITERIO_FACTOR_P24).sensibilidad),
                de_donde=(f"el criterio adoptado '{CRITERIO_FACTOR_P24}' "
                          f"[A] = {factor:g}"),
                cita_id="MC_HHD.3.8.1#P24",
                clave_criterio=CRITERIO_FACTOR_P24)),
        nota_del_proyecto=" ".join(notas_ajuste))

    # --- 1b.3: bondad de ajuste ---
    _, origen_d = valor_critico_ks(adoptado.n, alfa)
    cita_t03 = "MC_HHD.3.7.2b#T03"
    nota_chi2, elecciones_chi2, citas_chi2 = _contraste_chi_cuadrado(
        valores, adoptado.distribucion, alfa=alfa)
    paso_ks = paso(
        "FH.KS", codigo=CODIGO_KS,
        que="Bondad de ajuste de Kolmogorov-Smirnov de la distribucion adoptada",
        formula="D = max |Fo(xm) − F(xm)| ; Fo(xm) = 1 − m/(n + 1) ; "
                "se acepta si D < d",
        formula_cita_id=cita_ks,
        citas_textuales=(cita_ks, cita_t03, *citas_chi2),
        sustitucion=(
            Magnitud("n", adoptado.n, "", "años que entran al ajuste"),
            Magnitud("alfa", alfa, "",
                     f"criterio adoptado '{CRITERIO_ALFA}' [A]"),
            Magnitud("d", adoptado.d_critico, "", origen_d,
                     cifras=CIFRAS_FINA)),
        resultado=Magnitud("D", adoptado.D, "",
                           "mayor diferencia entre la probabilidad observada "
                           "y la del modelo", cifras=CIFRAS_FINA),
        umbral=Umbral(
            descripcion="valor critico d de Kolmogorov-Smirnov",
            # Con las cifras con que se imprime `d` arriba: el umbral no
            # lleva formato propio y un cuantil exacto saldria con 16.
            valor=round(adoptado.d_critico, CIFRAS_FINA), unidad="",
            cita_id=cita_t03,
            caracter=_caracter(cita_t03),
            aplicacion="umbral duro: si D no baja de d el ajuste se rechaza "
                       "y el calculo hidrologico del punto se detiene",
            criterio_aplicado=CRITERIO_ALFA),
        veredicto=Veredicto(
            tipo=(TipoDeVeredicto.CUMPLE if adoptado.acepta
                  else TipoDeVeredicto.NO_CUMPLE),
            margen=adoptado.d_critico - adoptado.D, unidad="",
            explicacion=("se acepta la hipotesis de que la serie sale de la "
                         "distribucion adoptada" if adoptado.acepta else
                         "la serie no se ajusta a la distribucion adoptada")),
        elecciones=elecciones_chi2,
        nota_del_proyecto=nota_chi2)
    if not adoptado.acepta:
        raise _no_evaluable_ks(adoptado, evaluados, serie=serie,
                               tratamiento=tratamiento, alfa=alfa,
                               id_punto=id_punto)

    # --- 1b.3b: el tratamiento FEN contra la regla de la hoja de ruta ---
    cita_fen = "MC_HHD.3.4#FEN"
    de_cada_serie = [Magnitud(f"P24(TR) con '{tratamiento}'",
                              adoptado.P_TR_mm, "mm",
                              f"paso {CODIGO_AJUSTE}: la serie adoptada",
                              cifras=CIFRAS_MAGNITUD)]
    umbral_fen: Optional[Umbral] = None
    nota_fen = ""
    if contraste is None:
        veredicto_fen = Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="no hay segundo ajuste con que comparar: "
                        + sin_contraste)
    else:
        de_cada_serie.append(Magnitud(
            f"P24(TR) con '{otro}'", contraste.P_TR_mm, "mm",
            f"la misma regla de eleccion sobre la otra serie "
            f"({contraste.distribucion}, n = {contraste.n})",
            cifras=CIFRAS_MAGNITUD))
        # LA REGLA ES DURA (decision del dueño de la hoja de ruta, tras la
        # auditoria de T-1): un punto no queda dimensionado sobre un caudal
        # que incumple la exigencia del num. 3.4 y la regla «adoptar el mas
        # conservador». El criterio se puede declarar; si el tratamiento
        # declarado da MENOS lluvia que el otro, el calculo hidrologico del
        # punto se detiene por la misma via que un ajuste que no pasa la
        # prueba de bondad: hace falta OTRO tratamiento, o el caudal de un
        # estudio. Si da igual o mas, pasa y el paso lo imprime.
        #
        # SOLO `serie_sin_fen` se detiene. El caso inverso --la serie
        # completa da menos que la serie sin los años marcados FEN, que pasa
        # cuando un año FEN fue seco en la estacion-- no: la serie completa
        # es la que el num. 3.4 manda usar, y bloquearla remitiria a quitar
        # los años que el Manual manda incluir. Se imprime como INDICADOR y
        # se avisa.
        menos_que_el_otro = adoptado.P_TR_mm < contraste.P_TR_mm
        if menos_que_el_otro and tratamiento == FEN_SERIE_SIN_FEN:
            bondad = ("pasa" if contraste.acepta else "NO pasa")
            raise _no_evaluable(
                "P24(TR)",
                f"el tratamiento '{tratamiento}' da una precipitacion de "
                f"diseño de {adoptado.P_TR_mm:.1f} mm "
                f"({adoptado.distribucion}, n = {adoptado.n}) y con "
                f"'{otro}' es {contraste.P_TR_mm:.1f} mm "
                f"({contraste.distribucion}, n = {contraste.n}, que {bondad} "
                "la prueba de Kolmogorov-Smirnov): el adoptado NO es el mas "
                "conservador de los dos. La Fase 1-bis de la hoja de ruta "
                "manda reportar el ajuste con los años FEN y sin ellos y "
                "adoptar el mas conservador, y el num. 3.4 del Manual manda "
                "que la serie incluya los años del fenomeno El Niño",
                _procedimiento_del_otro_tratamiento(otro), id_punto)
        umbral_fen = Umbral(
            descripcion=f"precipitacion de diseño con '{otro}', el otro "
                        "ajuste que la regla manda reportar",
            valor=round(contraste.P_TR_mm, CIFRAS_MAGNITUD), unidad="mm",
            cita_id=cita_fen, caracter=_caracter(cita_fen),
            aplicacion="regla de la hoja de ruta (Fase 1-bis): reportar el "
                       "ajuste con los años FEN y sin ellos y adoptar el mas "
                       "conservador. Umbral duro para 'serie_sin_fen': si da "
                       "menos lluvia que la serie completa, el calculo "
                       "hidrologico del punto se detiene. Para la serie "
                       "completa, que es la que el Manual manda usar, "
                       "indicador con aviso",
            criterio_aplicado=CRITERIO_FEN)
        veredicto_fen = Veredicto(
            tipo=(TipoDeVeredicto.INDICADOR if menos_que_el_otro
                  else TipoDeVeredicto.CUMPLE),
            margen=adoptado.P_TR_mm - contraste.P_TR_mm, unidad="mm",
            explicacion=("la serie completa da MENOS lluvia que la serie sin "
                         "los años marcados FEN: se mantiene, porque es la "
                         "que el Manual manda usar, y se avisa"
                         if menos_que_el_otro else
                         "la lluvia adoptada es la mas conservadora de las "
                         "dos, o igual"))
        if menos_que_el_otro:
            nota_fen = (
                f"Con la serie completa la precipitacion de diseño es "
                f"{adoptado.P_TR_mm:.1f} mm y sin los años marcados FEN "
                f"seria {contraste.P_TR_mm:.1f} mm: quitar esos años SUBE la "
                "lluvia de diseño, que no es lo que se espera de los años "
                "del fenomeno El Niño. Conviene revisar que años declara "
                "como FEN el archivo de la estacion. El calculo sigue con la "
                "serie completa, que es la que el num. 3.4 del Manual manda "
                "usar.")
            avisos.append(nota_fen)
    paso_fen = paso(
        "FH.FEN", codigo=CODIGO_FEN,
        que="Tratamiento de los años FEN contra la regla de la hoja de ruta: "
            "el ajuste mas conservador",
        formula="P24(TR) adoptada >= P24(TR) de la otra serie",
        citas_textuales=(cita_fen, "MC_HHD.3.12.5#PIURA"),
        sustitucion=tuple(de_cada_serie),
        resultado=Magnitud("P24(TR) adoptada", adoptado.P_TR_mm, "mm",
                           f"tratamiento '{tratamiento}' (criterio "
                           f"'{CRITERIO_FEN}' [A])", cifras=CIFRAS_MAGNITUD),
        umbral=umbral_fen, veredicto=veredicto_fen,
        nota_del_proyecto=nota_fen)
    return (adoptado, evaluados, tratamiento,
            (paso_serie, paso_ajuste, paso_ks, paso_fen,
             _paso_consistencia(serie_registrada)), tuple(avisos))


def maximos_anuales_repetidos(serie: SerieDeEstacion,
                              ) -> Tuple[Tuple[float, Tuple[int, ...]], ...]:
    """
    (valor, años) de cada maximo anual de la serie REGISTRADA que aparece en
    mas de un año, del mayor al menor valor y con los años en orden (VE3-19).

    Es un dato para el aviso de consistencia (num. 3.3, pag. impresa 21, la
    consistencia de los datos registrados), no una verificacion: dos maximos anuales iguales son normales, y con un maximo
    por año el programa no puede distinguir una coincidencia de un año
    copiado de otro (en la serie de Cañaveral de UNTumbes, 2002 es copia de
    1989 y 2001 de 1996, y eso solo lo prueban los doce meses, que no
    entran). No quita ningun año ni lleva numero de corte: «mismo valor» es
    la tolerancia de representacion `TOL_ABS_MISMO_MAXIMO_ANUAL_MM`.
    """
    grupos: List[List[RegistroDeLluvia]] = []
    for r in sorted(serie.registros, key=lambda r: r.p24_mm, reverse=True):
        if grupos and math.isclose(r.p24_mm, grupos[-1][0].p24_mm, rel_tol=0,
                                   abs_tol=TOL_ABS_MISMO_MAXIMO_ANUAL_MM):
            grupos[-1].append(r)
        else:
            grupos.append([r])
    return tuple((g[0].p24_mm, tuple(sorted(r.anio for r in g)))
                 for g in grupos if len(g) > 1)


def _texto_de_repetidos(repetidos: Sequence[Tuple[float, Tuple[int, ...]]],
                        ) -> str:
    """El renglon del aviso de consistencia con los maximos repetidos."""
    if not repetidos:
        return ""

    def _anios(anios: Tuple[int, ...]) -> str:
        textos = [str(a) for a in anios]
        return ", ".join(textos[:-1]) + " y " + textos[-1]

    lista = "; ".join(f"{valor:.1f} mm ({_anios(anios)})"
                      for valor, anios in repetidos)
    return (f" Maximos anuales que se repiten en la serie registrada: {lista}. "
            "El programa no distingue una coincidencia de un año copiado de "
            "otro, y no quita ni juzga ninguno: el proyectista tiene que "
            "contrastar esos años con el registro mensual o diario de origen "
            "(ficha VE3-19).")


def _paso_consistencia(serie: SerieDeEstacion) -> PasoDeMemoria:
    """
    El AVISO DE CONSISTENCIA de la serie, SIN UMBRAL (VE-2, VE1-02 (e); ficha
    VE2-E). Patron de `_paso_q_especifico`: informa y no juzga.

    El Manual manda evaluar «la consistencia de los datos registrados» (num.
    3.3, pag. impresa 21) y dice que es primordial (num. 3.4, pag. impresa
    22), y ni el ni ninguna fuente del repositorio de normas dan el
    procedimiento ni un numero de corte. Inventar uno seria rellenar un
    vacio: el paso dice que el Manual lo exige, que el programa NO lo hace y
    que el proyectista tiene que declarar que lo hizo, e imprime el minimo,
    la mediana y el maximo de la serie ENTERA de la estacion --la que se
    registro, no la que entra al ajuste-- sin juzgarlos. Desde VE3-19 (H1
    de la validacion con casos reales, `docs/validacion_hidrologica.md`)
    suma un renglon con los maximos anuales que se repiten y sus años
    (`maximos_anuales_repetidos`), solo cuando los hay, sin juzgarlos.
    """
    cita_33, cita_34 = "MC_HHD.3.3#CONSISTENCIA", "MC_HHD.3.4#CONSISTENCIA"
    registros = serie.registros
    valores = [r.p24_mm for r in registros]
    menor = min(registros, key=lambda r: r.p24_mm)
    mayor = max(registros, key=lambda r: r.p24_mm)
    mediana = median(valores)
    # Una mediana de 0 mm (una costa arida con media serie seca) no tiene
    # cociente: se dice, no se divide.
    cociente: Any = (mayor.p24_mm / mediana if mediana > 0 else
                     "sin cociente: la mediana de la serie es 0 mm")
    texto_cociente = (f"{cociente:.1f}" if mediana > 0 else cociente)
    exigencia = _REG.cita(cita_33)
    return paso(
        "FH.CONSISTENCIA", codigo=CODIGO_CONSISTENCIA,
        que=(f"Consistencia de la serie de la estacion «{serie.estacion}» "
             "(aviso, sin umbral)"),
        formula=("maximo / mediana de la serie registrada   [indicador sin "
                 "umbral: el Manual no da procedimiento ni numero de corte]"),
        citas_textuales=(cita_33, cita_34),
        sustitucion=(
            Magnitud("n", len(valores), "años",
                     f"registros de {serie.origen}: la serie ENTERA, con sus "
                     "años FEN, porque la consistencia es de los datos "
                     "registrados"),
            Magnitud("minimo", menor.p24_mm, "mm",
                     f"columna p24_mm de {serie.origen}, año {menor.anio}",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("mediana", mediana, "mm",
                     f"de los {len(valores)} años de {serie.origen}",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("maximo", mayor.p24_mm, "mm",
                     f"columna p24_mm de {serie.origen}, año {mayor.anio}",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("maximo / mediana", cociente, "",
                           "cuantas veces la mayor lluvia registrada supera "
                           "a la mediana de la serie", cifras=CIFRAS_FINA),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="aviso, no verificacion: el Manual manda evaluar la "
                        "consistencia y no le pone umbral, y el programa no "
                        "inventa uno"),
        nota_del_proyecto=(
            "AVISO DE CONSISTENCIA, sin umbral. El Manual exige que se "
            f"evalue: «{exigencia.texto_literal.texto}» "
            f"({exigencia.como_texto()}), y dice que la consistencia de los "
            "datos es primordial para el inicio del estudio hidrologico "
            f"({_REG.cita(cita_34).como_texto()}). El programa NO la evalua: "
            "ni el Manual ni ninguna otra fuente del expediente dan el "
            "procedimiento ni un numero de corte, y fijar uno seria rellenar "
            "un vacio. El proyectista tiene que declarar en la memoria que "
            "la evaluo, con que procedimiento y con que resultado. Para "
            "orientarlo, la serie entera de la estacion "
            f"«{serie.estacion}» ({len(valores)} años) va de "
            f"{menor.p24_mm:.1f} mm ({menor.anio}) a {mayor.p24_mm:.1f} mm "
            f"({mayor.anio}), con mediana {mediana:.1f} mm y un cociente "
            f"maximo / mediana de {texto_cociente}: el programa no los "
            "juzga." + _texto_de_repetidos(maximos_anuales_repetidos(serie))))


# ===========================================================================
# 3. Intensidad de diseño (num. 3.8.1)
# ===========================================================================

def precipitacion_dick_peschke_mm(*, P24_mm: float, d_min: float) -> float:
    """Dick y Peschke, ecuacion (16): Pd = P24h · (d / 1440)^0.25, d en min."""
    return P24_mm * (d_min / DICK_PESCHKE["minutos_en_24_h"]) \
        ** DICK_PESCHKE["exponente"]


def coeficiente_de_duracion(d_h: float) -> float:
    """
    El coeficiente de la Tabla N 04 para una duracion en horas, interpolado
    LINEALMENTE entre las dos filas vecinas (lectura del proyecto: la tabla
    no dice que se interpole; ver la `Laguna` de `MC_HHD.T04`).
    """
    horas = sorted(TABLA_04_COEFICIENTES_DE_DURACION)
    if not horas[0] <= d_h <= horas[-1]:
        raise _no_evaluable(
            "I",
            f"la Tabla N 04 cubre duraciones de {horas[0]} a {horas[-1]} "
            f"horas y la duracion de diseño es {d_h:.3f} h",
            f"declarar '{RELACION_DICK_PESCHKE}' en '{CRITERIO_RELACION}', "
            "que es la relacion que el num. 3.8.1 nombra para duraciones "
            "menores de 1 hora")
    for abajo, arriba in zip(horas, horas[1:]):
        if abajo <= d_h <= arriba:
            k0 = TABLA_04_COEFICIENTES_DE_DURACION[abajo]
            k1 = TABLA_04_COEFICIENTES_DE_DURACION[arriba]
            return k0 + (k1 - k0) * (d_h - abajo) / (arriba - abajo)
    return TABLA_04_COEFICIENTES_DE_DURACION[horas[-1]]


def _intensidad(*, P24_mm: float, d_min: float,
                relacion: str, TR: Optional[float] = None,
                leer=None) -> Tuple[float, float]:
    """
    (Pd en mm, I en mm/h) de una lluvia de duracion `d_min`, desde la
    precipitacion maxima en 24 horas (num. 3.8.1). «La intensidad se halla
    dividiendo la precipitación Pd entre la duración.»

    Con la relacion regional de la ecuacion (17) (VE-5) la intensidad no
    sale de la P24 sino de I = K·T^m / t^n, con el periodo de retorno `TR` y
    los factores del criterio 'factores_idf_regional' [S]; Pd = I · d / 60.
    `leer` es como se lee ese criterio (el pre-vuelo no registra el uso).

    PRIVADA A PROPOSITO (auditoria de T-1): toma una P24 cualquiera, sin
    saber de que serie sale ni con que tratamiento FEN, y no aplica la
    duracion minima. La intensidad de diseño de una obra sale de
    `caudal_de_diseno` o de `caudal_de_aporte_cuneta`.
    """
    d_h = d_min / MINUTOS_POR_HORA
    if relacion == RELACION_DICK_PESCHKE:
        if not 0 < d_min <= DICK_PESCHKE["minutos_en_24_h"]:
            raise _no_evaluable(
                "I",
                f"la relacion de Dick y Peschke reparte la lluvia de 24 "
                f"horas y la duracion de diseño es {d_min:g} min",
                PROCEDIMIENTO_HIDROGRAMA)
        Pd = precipitacion_dick_peschke_mm(P24_mm=P24_mm, d_min=d_min)
    elif relacion == RELACION_TABLA_04:
        Pd = coeficiente_de_duracion(d_h) * P24_mm
    elif relacion == RELACION_IDF_REGIONAL:
        K, m, n = factores_idf_regional(leer=leer)
        if TR is None:
            raise DatoFaltanteError(
                "TR", detalle="la relacion regional de la ecuacion (17) pide "
                              "el periodo de retorno")
        I = intensidad_idf_regional_mm_h(K=K, m=m, n=n, TR=TR, t_min=d_min)
        return I * d_h, I
    else:
        raise DatoInvalidoError(
            CRITERIO_RELACION, valor=relacion,
            motivo=f"las relaciones admitidas son {RELACION_DICK_PESCHKE}, "
                   f"{RELACION_TABLA_04} y {RELACION_IDF_REGIONAL}")
    return Pd, Pd / d_h


def factores_idf_regional(*, leer=None) -> Tuple[float, float, float]:
    """
    (K, m, n) del criterio 'factores_idf_regional' [S], comprobados: las
    tres claves, numeros finitos y positivos. Sin valor,
    `CriterioPendienteError` (un dato de un estudio regional no se rellena).

    Positivos porque la ecuacion (17) del num. 3.8.1 es una CURVA IDF: K es
    su escala, m hace crecer la intensidad con el periodo de retorno y n la
    hace decrecer con la duracion --la «relación inversa entre la duración
    de una tormenta y su intensidad» del num. 3.9--. Un n negativo daria
    mas intensidad a una lluvia mas larga.
    """
    valor = (ca.valor if leer is None else leer)(CRITERIO_IDF_REGIONAL)
    try:
        factores = tuple(float(valor[clave]) for clave in ("K", "m", "n"))
    except (KeyError, TypeError, ValueError):
        raise DatoInvalidoError(
            CRITERIO_IDF_REGIONAL, valor=valor,
            motivo="es un diccionario con tres numeros: 'K', 'm' y 'n'"
                   ) from None
    if not all(math.isfinite(f) and f > 0 for f in factores):
        raise DatoInvalidoError(
            CRITERIO_IDF_REGIONAL, valor=valor,
            motivo="K, m y n son positivos: la ecuacion (17) es una curva "
                   "IDF, que crece con el periodo de retorno y decrece con "
                   "la duracion (num. 3.9)")
    return factores


def intensidad_idf_regional_mm_h(*, K: float, m: float, n: float, TR: float,
                                 t_min: float) -> float:
    """
    Ecuacion (17) del num. 3.8.1 del Manual de Hidrologia (pag. impresa 38):
    I = K · T^m / t^n, I en mm/h, T = periodo de retorno en años, t =
    duracion de la precipitacion en MINUTOS («equivalente al tiempo de
    concentración»). K, m y n son «factores característicos de la zona de
    estudio».
    """
    return K * TR ** m / t_min ** n


def _intensidad_de_diseno(P24_mm: float, tc_min: float,
                          TR: Optional[float] = None) -> float:
    """
    La intensidad de la lluvia de diseño, en mm/h, para un tiempo de
    concentracion en minutos: la MISMA regla que `_paso_intensidad` (la
    relacion del criterio 'relacion_intensidad_duracion' y la duracion
    minima 'duracion_minima_lluvia_min'), sin paso. Es la curva con que el
    punto fijo de Izzard y de la onda cinematica (`_punto_fijo_tc`) se cruza.
    """
    minimo = ca.valor(CRITERIO_DURACION_MINIMA)
    d_min = minimo if tc_min < minimo else tc_min
    return _intensidad(P24_mm=P24_mm, d_min=d_min,
                       relacion=ca.valor(CRITERIO_RELACION), TR=TR)[1]


def _paso_intensidad(P24_mm: float, tc_min: float,
                     TR: Optional[float] = None,
                     ) -> Tuple[float, float, PasoDeMemoria, Tuple[str, ...]]:
    """
    (I en mm/h, duracion adoptada en min, paso, avisos). La duracion de la
    lluvia de diseño es el tiempo de concentracion (num. 3.8.1) SALVO que
    este quede por debajo de 'duracion_minima_lluvia_min': entonces dura el
    minimo, y el paso y la corrida lo dicen.

    `TR` (VE-5): el periodo de retorno, que solo la relacion regional de la
    ecuacion (17) usa (I = K·T^m / t^n).
    """
    relacion = ca.valor(CRITERIO_RELACION)
    minimo = ca.valor(CRITERIO_DURACION_MINIMA)
    corta = tc_min < minimo
    d_min = minimo if corta else tc_min
    Pd, I = _intensidad(P24_mm=P24_mm, d_min=d_min, relacion=relacion, TR=TR)
    notas: List[str] = []
    avisos: List[str] = []
    de_la_relacion: Tuple[Magnitud, ...] = (
        Magnitud("P24", P24_mm, "mm",
                 f"precipitacion de diseño del paso {CODIGO_AJUSTE}",
                 cifras=CIFRAS_MAGNITUD),)
    if relacion == RELACION_IDF_REGIONAL:
        K, m, n = factores_idf_regional()
        formula = ("I = K · T^m / t^n ; Pd = I · d / 60   [I en mm/h, T en "
                   "años, t = d en min]")
        cita = "MC_HHD.3.8.1#EC17"
        procedencia = (f"criterio '{CRITERIO_IDF_REGIONAL}' [S]: factor de la "
                       "relacion regional, dato del estudio de la zona")
        de_la_relacion = (
            Magnitud("K", K, "", procedencia, cifras=CIFRAS_FINA),
            Magnitud("m", m, "", procedencia, cifras=CIFRAS_FINA),
            Magnitud("n", n, "", procedencia, cifras=CIFRAS_FINA),
            Magnitud("T", TR, "años", "periodo de retorno del caudal"))
        notas.append(
            "Relacion REGIONAL de la ecuacion (17): la intensidad sale de los "
            f"factores K, m y n del criterio '{CRITERIO_IDF_REGIONAL}' [S] y "
            f"no de la lluvia de 24 horas del paso {CODIGO_AJUSTE}, que se "
            "imprime al lado como contraste (Dick y Peschke con esa P24).")
    elif relacion == RELACION_DICK_PESCHKE:
        formula = ("Pd = P24 · (d / 1440)^0.25 ; I = Pd / (d / 60)   "
                   "[d en min, I en mm/h]")
        cita = "MC_HHD.3.8.1#DICK_PESCHKE"
    else:
        formula = ("Pd = k(d) · P24 ; I = Pd / d   [d en horas; k de la "
                   "Tabla N 04]")
        cita = "MC_HHD.3.8.1#T04"
        notas.append("El coeficiente k se interpolo LINEALMENTE entre las "
                     "dos filas vecinas de la Tabla N 04: la tabla no dice "
                     "que se interpole y es lectura del proyecto.")
    if corta:
        aviso = (f"El tiempo de concentracion ({tc_min:.2f} min) es menor "
                 f"que la duracion minima de la lluvia de diseño "
                 f"({minimo:g} min, criterio '{CRITERIO_DURACION_MINIMA}' "
                 "[C]): la intensidad se calculo con la duracion minima y "
                 "no con el tiempo de concentracion. El Manual de "
                 "Hidrologia no fija ese piso; es de una fuente tecnica.")
        avisos.append(aviso)
        notas.append(aviso)
    alternativa = (RELACION_TABLA_04 if relacion == RELACION_DICK_PESCHKE
                   else RELACION_DICK_PESCHKE)
    try:
        _, I_alt = _intensidad(P24_mm=P24_mm, d_min=d_min, relacion=alternativa,
                               TR=TR)
        texto_alt = f"{alternativa}: I = {I_alt:.2f} mm/h"
    except MetodoNoEvaluableError:
        texto_alt = (f"{alternativa}: no cubre una duracion de "
                     f"{d_min:.1f} min")
    cita_minimo = "WSDOT_HM.2-6.3#TC_MINIMO"
    return I, d_min, paso(
        "FH.INTENSIDAD", codigo=CODIGO_INTENSIDAD,
        que=("Intensidad de la lluvia de diseño, de duracion igual al minimo "
             "adoptado (el tiempo de concentracion es menor)" if corta else
             "Intensidad de la lluvia de diseño, de duracion igual al tiempo "
             "de concentracion"),
        formula=formula, formula_cita_id=cita,
        citas_textuales=("MC_HHD.3.8.1#DURACION", cita),
        sustitucion=(
            *de_la_relacion,
            Magnitud("tc", tc_min, "min",
                     f"tiempo de concentracion del paso {CODIGO_TC}",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("d", d_min, "min",
                     ("la duracion minima adoptada: el tiempo de "
                      "concentracion queda por debajo" if corta else
                      "la duracion de la lluvia de diseño es el tiempo de "
                      "concentracion"), cifras=CIFRAS_MAGNITUD),
            Magnitud("Pd", Pd, "mm", "precipitacion de esa duracion",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("I", I, "mm/h", "intensidad de diseño",
                           cifras=CIFRAS_MAGNITUD),
        umbral=Umbral(
            descripcion="duracion minima de la lluvia de diseño",
            valor=minimo, unidad="min", cita_id=cita_minimo,
            caracter=_caracter(cita_minimo),
            aplicacion="piso de la duracion, no de la obra: si el tiempo de "
                       "concentracion es menor, la lluvia de diseño dura el "
                       "minimo. Es de una fuente tecnica [C]; el Manual de "
                       "Hidrologia no fija ninguno",
            criterio_aplicado=CRITERIO_DURACION_MINIMA),
        veredicto=Veredicto(
            tipo=(TipoDeVeredicto.INDICADOR if corta
                  else TipoDeVeredicto.CUMPLE),
            margen=tc_min - minimo, unidad="min",
            explicacion=("el tiempo de concentracion no alcanza la duracion "
                         "minima: se adopto el minimo" if corta else
                         "el tiempo de concentracion supera la duracion "
                         "minima y es la duracion de la lluvia de diseño")),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="relacion entre la lluvia de 24 horas y la de la "
                          "duracion de diseño",
            valor=f"{relacion}: I = {I:.2f} mm/h",
            entre=(f"{relacion}: I = {I:.2f} mm/h", texto_alt),
            de_donde=f"el criterio adoptado '{CRITERIO_RELACION}' [A]",
            por_que=("el num. 3.8.1 del Manual escribe la relacion regional "
                     "de la ecuacion (17) para cuando hay curvas IDF de la "
                     "zona; la intensidad que daria la lluvia de 24 horas de "
                     "la estacion se imprime al lado como contraste"
                     if relacion == RELACION_IDF_REGIONAL else
                     "el num. 3.8.1 del Manual permite las dos relaciones "
                     "cuando no hay registros pluviograficos y no manda "
                     "ninguna; la alternativa se imprime al lado para que se "
                     "vea cuanto pesa la eleccion"),
            clave_criterio=CRITERIO_RELACION),),
        nota_del_proyecto=" ".join(notas)), tuple(avisos)


# ===========================================================================
# 4. Coeficiente de escorrentia (num. 3.12.2, Tabla N 08)
# ===========================================================================

def clase_de_pendiente(S: float) -> Tuple[str, bool]:
    """
    La columna de la Tabla N 08 para una pendiente del terreno en m/m, y si
    cayo en la LAGUNA de la tabla (exactamente 1 %, que «> 1%» y «< 1%»
    dejan sin cubrir: se lee «suave», la de mayor C).
    """
    for clave, umbral in TABLA_08_PENDIENTES:
        if S > umbral:
            return clave, False
    menor_umbral = TABLA_08_PENDIENTES[-1][1]
    if S < menor_umbral:
        return TABLA_08_PENDIENTE_MENOR, False
    return TABLA_08_PENDIENTES[-1][0], True


def coeficiente_de_escorrentia(*, cobertura: str, suelo: str,
                               S: float) -> Tuple[float, str, bool]:
    """
    (C, columna leida, si cayo en la laguna) de la Tabla N 08 del num. 3.12.2
    (pag. impresa 50), por cobertura vegetal, tipo de suelo y pendiente del
    terreno. La fila se pide por CLAVE: un C tecleado no entra.
    """
    fila = TABLA_08_COEFICIENTE_DE_ESCORRENTIA.get((cobertura, suelo))
    if fila is None:
        coberturas = sorted({c for c, _ in TABLA_08_COEFICIENTE_DE_ESCORRENTIA})
        suelos = sorted({s for _, s in TABLA_08_COEFICIENTE_DE_ESCORRENTIA})
        raise DatoInvalidoError(
            "cobertura / suelo", valor=f"{cobertura} / {suelo}",
            motivo="no es una fila de la Tabla N 08. Coberturas: "
                   + ", ".join(coberturas) + ". Suelos: " + ", ".join(suelos)
                   + ". Superficies de la plataforma vial, con el suelo "
                   "vacio: " + ", ".join(SUPERFICIES_VIALES))
    columna, laguna = clase_de_pendiente(S)
    return fila[columna], columna, laguna


def coeficiente_de_superficie_vial(*, superficie: str, TR: float,
                                   id_punto: Optional[str] = None,
                                   ) -> Tuple[float, float, float, int, bool]:
    """
    El coeficiente de escorrentia de una superficie de la plataforma vial
    --pavimento, berma de tierra, talud de tierra o con cesped--, que la
    Tabla N 08 no tiene: (C, C de 10 años, incremento, frecuencia tabulada
    que se tomo, si quedo en el tope).

    Fuente tecnica [C], criterio 'coeficiente_escorrentia_superficie_vial':
    WSDOT Hydraulics Manual, Table 2-2 (pag. 2-9), cuyos coeficientes son de
    10 años de periodo de retorno, y num. 2-6.2 (pag. 2-8), que manda
    aumentarlos 10, 20 y 25 % para 25, 50 y 100 años sin pasar de 0.95.
    Entre esas frecuencias se toma el incremento de la inmediatamente MAYOR
    (lectura del proyecto, lado conservador); por encima de 100 años la
    fuente no da incremento y no se evalua.
    """
    tabla = ca.valor(CRITERIO_C_VIAL)
    c10 = tabla["coeficientes_10_anios"].get(superficie)
    if c10 is None:
        raise DatoInvalidoError(
            "cobertura", valor=superficie, id_punto=id_punto,
            motivo="las superficies de la plataforma vial con coeficiente "
                   "son " + ", ".join(tabla["coeficientes_10_anios"]))
    incrementos = {int(anios): incremento for anios, incremento
                   in tabla["incremento_por_periodo_de_retorno"].items()}
    tomada = next((f for f in sorted(incrementos) if not TR > f), None)
    if tomada is None:
        raise _no_evaluable(
            "C",
            f"la fuente del coeficiente de una superficie vial da su "
            f"incremento hasta {max(incrementos)} años de periodo de retorno "
            f"y el de diseño es {TR:g}",
            "una fuente que fije el coeficiente de esa superficie para ese "
            "periodo de retorno, o el caudal declarado en Q_m3s",
            id_punto)
    sin_tope = c10 * (1 + incrementos[tomada])
    return (min(sin_tope, tabla["tope"]), c10, incrementos[tomada], tomada,
            sin_tope > tabla["tope"])


def _paso_c(cuenca: Cuenca, TR: float) -> Tuple[float, PasoDeMemoria]:
    if cuenca.cobertura in SUPERFICIES_VIALES:
        return _paso_c_vial(cuenca, TR)
    S = cuenca.S_terreno
    C, columna, laguna = coeficiente_de_escorrentia(
        cobertura=cuenca.cobertura, suelo=cuenca.suelo, S=S)
    nota = ""
    if laguna:
        nota = ("La pendiente es exactamente 1 %, que la tabla no cubre "
                "(«> 1%» y «< 1%»): se leyo la columna «suave», la de mayor "
                "coeficiente.")
    return C, paso(
        "FH.C", codigo=CODIGO_C,
        que="Coeficiente de escorrentia C de la cuenca",
        formula="C = Tabla N 08 [cobertura, tipo de suelo, pendiente del terreno]",
        formula_cita_id="MC_HHD.3.12.2#T08",
        citas_textuales=("MC_HHD.3.12.2#T08",),
        sustitucion=(
            Magnitud("cobertura", cuenca.cobertura, "",
                     f"columna cobertura de {cuenca.origen}"),
            Magnitud("suelo", cuenca.suelo, "",
                     f"columna suelo de {cuenca.origen}"),
            Magnitud("S", S, "m/m", f"columna S_terreno de {cuenca.origen}",
                     cifras=CIFRAS_FINA),
            Magnitud("columna", columna, "",
                     "clase de pendiente de la Tabla N 08 en que cae S")),
        resultado=Magnitud("C", C, "", "celda de la Tabla N 08",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="lectura de tabla, no verificacion"),
        nota_del_proyecto=nota)


def _paso_c_vial(cuenca: Cuenca, TR: float) -> Tuple[float, PasoDeMemoria]:
    C, c10, incremento, tomada, topado = coeficiente_de_superficie_vial(
        superficie=cuenca.cobertura, TR=TR, id_punto=cuenca.id)
    tope = ca.valor(CRITERIO_C_VIAL)["tope"]
    notas = ["La Tabla N 08 del Manual de Hidrologia no tiene fila para una "
             "superficie de la plataforma vial: el coeficiente sale de una "
             "fuente tecnica [C], no de norma peruana. Los coeficientes de "
             "esa tabla son de una tormenta de 10 años y se aumentan para "
             "una menos frecuente."]
    if not math.isclose(tomada, TR):
        notas.append(
            f"La fuente da el incremento para 10, 25, 50 y 100 años y no "
            f"para {TR:g}: se tomo el de {tomada} años, la frecuencia "
            "tabulada inmediatamente mayor. Es lectura del proyecto, por el "
            "lado conservador.")
    if topado:
        notas.append(f"El coeficiente aumentado pasaba del tope de la fuente "
                     f"y quedo en {tope:g}.")
    return C, paso(
        "FH.C", codigo=CODIGO_C,
        que="Coeficiente de escorrentia C de una superficie de la plataforma "
            "vial",
        formula="C = min(C10 · (1 + incremento), tope)   [C10 de la Table "
                "2-2, 10 años de periodo de retorno]",
        formula_cita_id="WSDOT_HM.2-6.2#FRECUENCIA",
        citas_textuales=("MC_HHD.3.12.2#T08", "WSDOT_HM.2-6.2#T2-2",
                         "WSDOT_HM.2-6.2#FRECUENCIA"),
        sustitucion=(
            Magnitud("superficie", cuenca.cobertura, "",
                     f"columna cobertura de {cuenca.origen}"),
            Magnitud("C10", c10, "",
                     f"criterio adoptado '{CRITERIO_C_VIAL}' [C]: fila de la "
                     "Table 2-2", cifras=CIFRAS_MAGNITUD),
            Magnitud("T", TR, "años", "periodo de retorno de diseño"),
            Magnitud("frecuencia tomada", tomada, "años",
                     "la tabulada igual o inmediatamente mayor que T"),
            Magnitud("incremento", incremento, "",
                     "el que la fuente manda para esa frecuencia",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("tope", tope, "", "maximo que la fuente admite",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("C", C, "", "coeficiente de escorrentia de la "
                           "superficie para el periodo de retorno de diseño",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="lectura de tabla y ajuste por frecuencia, no "
                        "verificacion"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="fuente del coeficiente de escorrentia de una "
                          "superficie de la plataforma vial",
            valor=f"{cuenca.cobertura}: C10 = {c10:g}",
            entre=tuple(SUPERFICIES_VIALES),
            de_donde=f"el criterio adoptado '{CRITERIO_C_VIAL}' [C]",
            por_que="la Tabla N 08 tabula cinco coberturas de cuenca natural "
                    "y ninguna superficie pavimentada ni talud, y el num. "
                    "4.1.2.1 b) pide el coeficiente de la cuenca de la "
                    "cuneta sin dar tabla",
            cita_id="WSDOT_HM.2-6.2#T2-2",
            clave_criterio=CRITERIO_C_VIAL),),
        nota_del_proyecto=" ".join(notas))


# ===========================================================================
# 5. Metodo racional y caudal especifico (num. 3.12.2 y 3.13)
# ===========================================================================

def exigir_alcance_del_racional(area_km2: float,
                                id_punto: Optional[str] = None) -> None:
    """
    El limite de validez del metodo racional (num. 3.12.2, pag. impresa 49):
    «Muy usado para cuencas, A<10 Km2», desigualdad ESTRICTA. Desde 10 km2
    lanza `MetodoNoEvaluableError` remitiendo al hidrograma unitario del num.
    3.12.3. La condicion va en positivo y negada para que un NaN caiga fuera.
    """
    if not area_km2 < RACIONAL_AREA_MAX_KM2:
        raise _no_evaluable(
            "Q",
            f"el Manual situa el metodo racional en cuencas de area menor "
            f"de {RACIONAL_AREA_MAX_KM2:g} km2 (num. 3.12.2) y la cuenca "
            f"tiene {area_km2:g} km2",
            PROCEDIMIENTO_HIDROGRAMA, id_punto)


def coeficiente_de_uniformidad(tc_h: float) -> float:
    """
    El coeficiente de uniformidad K del metodo racional modificado (num.
    3.12.2.1, ec. 31, pag. impresa 51): K = 1 + Tc^1.25 / (Tc^1.25 + 14),
    con Tc en HORAS. Es mayor que 1 y crece con el tiempo de concentracion.
    """
    k = UNIFORMIDAD_TEMEZ_SI
    potencia = tc_h ** k["exponente"]
    return 1 + potencia / (potencia + k["sumando"])


def caudal_racional(*, C: float, I_mm_h: float, area_km2: float,
                    K: float = 1,
                    id_punto: Optional[str] = None) -> float:
    """
    Q = 0.278 · C · I · A (num. 3.12.2, ec. 28), con I en mm/h, A en km2 y Q
    en m3/s. «Muy usado para cuencas, A<10 Km2»: desde 10 km2 no se evalua y
    se remite al hidrograma unitario del num. 3.12.3.

    `K` es el coeficiente de uniformidad de la ecuacion (29), Q = 0.278·CIAK,
    cuando el caudal lo lleva; por omision, la (28) tal cual. Es el UNICO
    coeficiente de la familia: el caudal de aporte de una cuneta (num.
    4.1.2.1 b, que escribe C·I·A/3.6) se calcula con este mismo 0.278.
    """
    exigir_alcance_del_racional(area_km2, id_punto)
    return RACIONAL_COEFICIENTE_SI * C * I_mm_h * area_km2 * K


def caudal_especifico(*, Q_m3s: float, area_km2: float) -> Tuple[float, float]:
    """
    (q = Q/A en m3/s por km2, lamina de escorrentia equivalente C·I en mm/h).
    La segunda es q / 0.278: lo que la ecuacion (28) da al despejar C·I.
    Indicador de plausibilidad, sin umbral (num. 3.13).
    """
    q = Q_m3s / area_km2
    return q, q / RACIONAL_COEFICIENTE_SI


def _paso_q_especifico(Q: Magnitud, A: Magnitud) -> Tuple[float, float, PasoDeMemoria]:
    q, lamina = caudal_especifico(Q_m3s=Q.valor, area_km2=A.valor)
    c_min = min(min(f.values()) for f in TABLA_08_COEFICIENTE_DE_ESCORRENTIA.values())
    c_max = max(max(f.values()) for f in TABLA_08_COEFICIENTE_DE_ESCORRENTIA.values())
    return q, lamina, paso(
        "FH.Q_ESPECIFICO", codigo=CODIGO_Q_ESPECIFICO,
        que="Caudal especifico del caudal de diseño (contraste de plausibilidad)",
        formula="q = Q / A ; C·I = q / 0.278   [de la ecuacion (28)]",
        formula_cita_id="MC_HHD.3.12.2",
        citas_textuales=("MC_HHD.3.13", "MC_HHD.3.12.2"),
        sustitucion=(Q, A),
        resultado=Magnitud("q", q, "m3/s por km2", "caudal especifico",
                           cifras=CIFRAS_FINA),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="contraste, no verificacion: el Manual define la "
                        "avenida de diseño sin ponerle umbral, y el programa "
                        "no inventa uno"),
        nota_del_proyecto=(
            f"AVISO DE PLAUSIBILIDAD, sin umbral. Este caudal equivale, por "
            f"la ecuacion (28), a una lamina de escorrentia C·I = "
            f"{lamina:.2f} mm/h sobre toda la cuenca. Con el menor y el "
            f"mayor coeficiente de la Tabla N 08 ({c_min:g} y {c_max:g}) eso "
            f"es una intensidad de lluvia de entre {lamina / c_max:.2f} y "
            f"{lamina / c_min:.2f} mm/h. Contrastese con la intensidad de "
            "diseño de la estacion y con el caudal especifico de cuencas "
            "vecinas: el programa no lo juzga."))


AVISO_FEN_DEL_CAUDAL_DECLARADO = (
    f"El criterio '{CRITERIO_FEN}' rige solo el caudal que el programa "
    "CALCULA. Este caudal entro declarado: el programa no sabe que serie lo "
    "respalda ni que se hizo con sus años del fenomeno El Niño, y no le "
    "atribuye ningun tratamiento. No detiene el calculo: un caudal declarado "
    "es responsabilidad del estudio hidrologico que lo entrego, y quien lo "
    "reciba tiene que exigir, aparte, el analisis de homogeneidad de la "
    "serie.")


def caudal_declarado(*, Q_m3s: float, de_donde: str,
                     area_km2: Optional[float] = None, origen_area: str = "",
                     cuenca_disponible: bool = False) -> CaudalDeDiseno:
    """
    El caudal que entra YA CALCULADO (columna `Q_m3s` o dato externo): no se
    recalcula ni se corrige. Se le añade el paso del caudal especifico (num.
    3.13) cuando hay area, y los avisos: SIEMPRE el de que el criterio FEN no
    lo alcanza y, si ademas habia cuenca y estacion para calcularlo, que el
    declarado gana.

    NO lee el criterio 'homogeneidad_serie_fen' y deja `tratamiento_fen` en
    None: hasta la auditoria de T-1 le ponia el tratamiento declarado para
    los puntos calculados, que era atribuirle al estudio externo algo que el
    programa no sabe.
    """
    avisos: List[str] = [AVISO_FEN_DEL_CAUDAL_DECLARADO]
    if cuenca_disponible:
        avisos.append(
            "Hay cuenca y estacion declaradas para este punto y NO se "
            "usaron: el caudal declarado gana. Para que el programa lo "
            "calcule, la celda Q_m3s tiene que ir vacia.")
    pasos: Tuple[PasoDeMemoria, ...] = ()
    q = lamina = None
    if area_km2 is not None:
        q, lamina, paso_q = _paso_q_especifico(
            Magnitud("Q", Q_m3s, "m3/s",
                     f"{LEYENDA_CAUDAL_DECLARADO}: {de_donde}",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("A", area_km2, "km2", origen_area, cifras=CIFRAS_FINA))
        pasos = (paso_q,)
    return CaudalDeDiseno(
        Q_m3s=Q_m3s, origen=ORIGEN_CAUDAL_DECLARADO,
        leyenda=LEYENDA_CAUDAL_DECLARADO, pasos=pasos, avisos=tuple(avisos),
        de_donde=de_donde, area_km2=area_km2, tratamiento_fen=None,
        q_especifico_m3s_km2=q, lamina_equivalente_mm_h=lamina)


def _caudal_calculado(cuenca: Cuenca, serie: SerieDeEstacion, TR: float, *,
                      de_cuneta: bool) -> CaudalDeDiseno:
    """El calculo comun de `caudal_de_diseno` y `caudal_de_aporte_cuneta`."""
    # --- VE-2 (f) --- Desde 10 km2 el caudal de una OBRA sale del metodo
    # racional modificado completo (num. 3.12.2.1). El aporte de una cuneta
    # no: el num. 4.1.2.1 b) escribe la ecuacion del racional simple, y un
    # area tributaria de 10 km2 no es una cuneta; sigue con su limite.
    if not de_cuneta and \
            metodo_de_caudal(cuenca.area_km2) == METODO_RACIONAL_MODIFICADO:
        return _caudal_racional_modificado(cuenca, serie, TR)
    # El area se comprueba ANTES de ajustar nada: si el metodo no aplica a
    # esta cuenca, lo demas no hace falta.
    exigir_alcance_del_racional(cuenca.area_km2, cuenca.id)
    adoptado, evaluados, tratamiento, pasos_lluvia, avisos_lluvia = \
        precipitacion_de_diseno(serie, TR, id_punto=cuenca.id)
    # C antes que tc: la formula de la FAA lleva el coeficiente de
    # escorrentia. Los pasos se imprimen en su orden de siempre.
    C, paso_c = _paso_c(cuenca, TR)
    tc, paso_tc, avisos_tc = tiempo_de_concentracion(
        cuenca, C=C,
        intensidad_de=lambda tc_min: _intensidad_de_diseno(adoptado.P_TR_mm,
                                                           tc_min, TR))
    I, d_min, paso_i, avisos_i = _paso_intensidad(adoptado.P_TR_mm, tc, TR)

    # El coeficiente de uniformidad K solo entra con la formula de Temez, que
    # es del metodo que lo define, y lo decide un criterio (uso hibrido).
    K: Optional[float] = None
    K_de_la_formula: Optional[float] = None
    trato_K = ""
    if cuenca.metodo_tc == TC_METODO_TEMEZ:
        trato_K = ca.valor(CRITERIO_K_TEMEZ)
        if trato_K not in (K_APLICAR, K_NO_APLICAR):
            raise DatoInvalidoError(
                CRITERIO_K_TEMEZ, valor=trato_K, id_punto=cuenca.id,
                motivo=f"los valores admitidos son {K_APLICAR} y {K_NO_APLICAR}")
        K_de_la_formula = coeficiente_de_uniformidad(tc / MINUTOS_POR_HORA)
        if trato_K == K_APLICAR:
            K = K_de_la_formula
    Q_sin_K = caudal_racional(C=C, I_mm_h=I, area_km2=cuenca.area_km2,
                              id_punto=cuenca.id)
    Q = Q_sin_K if K is None else caudal_racional(
        C=C, I_mm_h=I, area_km2=cuenca.area_km2, K=K, id_punto=cuenca.id)
    if not (math.isfinite(Q) and Q > 0):
        # El campo se llama «Q calculado» y NO como la columna del CSV: el
        # censo de consumidores (`variables_entrada`) atribuye una columna a
        # todo modulo que escriba su nombre, y este modulo no LEE esa
        # columna -- la produce. Con el nombre de la columna, el pre-vuelo
        # decia que la Fase 1-bis exigia el caudal del canal de la Familia C.
        raise LimiteNumericoError(
            "Q calculado", valor=Q, id_punto=cuenca.id,
            motivo=f"el caudal no es un numero positivo con C = {C:g}, "
                   f"I = {I:g} mm/h y A = {cuenca.area_km2:g} km2")
    A = Magnitud("A", cuenca.area_km2, "km2",
                 f"columna area_km2 de {cuenca.origen}", cifras=CIFRAS_FINA)
    cita_area = "MC_HHD.3.12.2#AREA"
    cita_K = "MC_HHD.3.12.2.1#K"
    sustitucion = [
        Magnitud("C", C, "", f"paso {CODIGO_C}", cifras=CIFRAS_MAGNITUD),
        Magnitud("I", I, "mm/h", f"paso {CODIGO_INTENSIDAD}",
                 cifras=CIFRAS_MAGNITUD),
        A]
    citas = ["MC_HHD.3.12.2", cita_area]
    formula, formula_cita = ("Q = 0.278 · C · I · A   [Q en m3/s, I en mm/h, "
                             "A en km2]"), "MC_HHD.3.12.2"
    elecciones: Tuple[EleccionDeProyecto, ...] = ()
    notas: List[str] = []
    if K_de_la_formula is not None:
        citas.append(cita_K)
        Q_con_K = caudal_racional(C=C, I_mm_h=I, area_km2=cuenca.area_km2,
                                  K=K_de_la_formula, id_punto=cuenca.id)
        sube = K_de_la_formula - 1
        elecciones = (EleccionDeProyecto(
            que_se_adopto="coeficiente de uniformidad K del metodo racional "
                          "modificado",
            valor=trato_K,
            entre=(f"{K_APLICAR}: K = {K_de_la_formula:.3f}, Q = "
                   f"{Q_con_K:.3f} m3/s",
                   f"{K_NO_APLICAR}: Q = {Q_sin_K:.3f} m3/s"),
            de_donde=f"el criterio adoptado '{CRITERIO_K_TEMEZ}' [A]",
            por_que="el tiempo de concentracion sale de la formula de Temez, "
                    "que es pieza del metodo racional modificado; ese metodo "
                    "multiplica el caudal por K y el Manual no dice si K "
                    "acompaña a la formula fuera del metodo",
            cita_id=cita_K, clave_criterio=CRITERIO_K_TEMEZ),)
        if K is not None:
            formula = ("Q = 0.278 · C · I · A · K ; K = 1 + Tc^1.25 / "
                       "(Tc^1.25 + 14)   [Q en m3/s, I en mm/h, A en km2, "
                       "Tc en horas]")
            formula_cita = cita_K
            sustitucion += [
                Magnitud("Tc", tc / MINUTOS_POR_HORA, "h",
                         f"paso {CODIGO_TC}, de minutos a horas",
                         cifras=CIFRAS_FINA),
                Magnitud("K", K, "", "coeficiente de uniformidad, ecuacion "
                         "(31)", cifras=CIFRAS_FINA)]
            notas.append(
                "USO HIBRIDO, declarado. El caudal lleva el coeficiente de "
                "uniformidad K del metodo racional modificado (ecuaciones "
                "29 y 31) porque el tiempo de concentracion sale de la "
                "formula de ese metodo; la intensidad y el coeficiente de "
                "escorrentia son los del metodo racional simple. K es mayor "
                f"que 1 y SUBE el caudal: aqui un {sube:.1%}.")
        else:
            notas.append(
                "USO HIBRIDO, declarado. El tiempo de concentracion sale de "
                "la formula del metodo racional modificado y el caudal NO "
                f"lleva su coeficiente de uniformidad K (criterio "
                f"'{CRITERIO_K_TEMEZ}' = {trato_K}). Con K el caudal subiria "
                f"un {sube:.1%}: no aplicarlo es el lado no conservador.")
    if de_cuneta:
        citas.append("MC_HHD.4.1.2.1b")
        notas.append(
            "Caudal de aporte de una cuneta. El num. 4.1.2.1 b) del Manual "
            "escribe esta ecuacion como Q = C·I·A / 3.6; el programa usa en "
            "toda la familia el 0.278 de la ecuacion (28), que es ese mismo "
            "cociente redondeado a tres cifras.")
    paso_q = paso(
        "FH.RACIONAL", codigo=CODIGO_RACIONAL,
        que=("Caudal de aporte a la cuneta por el metodo racional"
             if de_cuneta else "Caudal de diseño por el metodo racional"),
        formula=formula, formula_cita_id=formula_cita,
        citas_textuales=tuple(citas),
        sustitucion=tuple(sustitucion),
        resultado=Magnitud("Q", Q, "m3/s",
                           "caudal de aporte" if de_cuneta
                           else "caudal de diseño", cifras=CIFRAS_MAGNITUD),
        umbral=Umbral(
            descripcion="area maxima de cuenca del metodo racional (exclusiva)",
            valor=RACIONAL_AREA_MAX_KM2, unidad="km2", cita_id=cita_area,
            caracter=_caracter(cita_area),
            aplicacion="limite de validez: desde ese area el programa no "
                       "evalua el metodo y remite al hidrograma unitario "
                       "(la fuente dice donde se usa, no lo prohibe)"),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.CUMPLE,
            margen=RACIONAL_AREA_MAX_KM2 - cuenca.area_km2, unidad="km2",
            explicacion="el area de la cuenca esta dentro del alcance del "
                        "metodo racional"),
        elecciones=elecciones,
        nota_del_proyecto=" ".join(notas))
    q, lamina, paso_qa = _paso_q_especifico(
        Magnitud("Q", Q, "m3/s", f"paso {CODIGO_RACIONAL}",
                 cifras=CIFRAS_MAGNITUD), A)
    return CaudalDeDiseno(
        Q_m3s=Q, origen=ORIGEN_CAUDAL_CALCULADO,
        leyenda=LEYENDA_CAUDAL_CALCULADO,
        pasos=(*pasos_lluvia, paso_tc, paso_i, paso_c, paso_q, paso_qa),
        avisos=(*avisos_lluvia, *avisos_tc, *avisos_i),
        de_donde=(f"{cuenca.origen}; estacion «{serie.estacion}» de "
                  f"{serie.origen}"),
        TR_anios=TR, area_km2=cuenca.area_km2, tc_min=tc, I_mm_h=I, C=C,
        P24_TR_mm=adoptado.P_TR_mm, distribucion=adoptado.distribucion,
        tratamiento_fen=tratamiento, q_especifico_m3s_km2=q,
        lamina_equivalente_mm_h=lamina, ajustes=evaluados,
        metodo_tc=cuenca.metodo_tc, duracion_min=d_min, K_uniformidad=K)


# ===========================================================================
# 5-bis. Metodo racional modificado, de 10 a 770 km2 (num. 3.12.2.1) — VE-2
# ===========================================================================

def metodo_de_caudal(area_km2: float) -> str:
    """
    Con que metodo se calcula el caudal de una obra, por su area (VE-2,
    VE1-02 (f), ficha VE2-F). Por debajo de 10 km2 el racional simple de
    T-1 (num. 3.12.2, «Muy usado para cuencas, A<10 Km2», pag. impresa 49);
    desde 10 km2 el racional modificado (num. 3.12.2.1), que el Manual acota
    a areas menores de 770 km2. Los dos rangos se SOLAPAN por debajo de
    10 km2 y el Manual no dice cual usar ahi: que la frontera entre los dos
    sea esos 10 km2 es lectura del proyecto, la que deja intacto todo lo que
    T-1 calculaba. La condicion va en positivo, de modo que un NaN cae en el
    modificado y su limite de area lo detiene.
    """
    if area_km2 < RACIONAL_AREA_MAX_KM2:
        return METODO_RACIONAL
    return METODO_RACIONAL_MODIFICADO


def exigir_alcance_del_racional_modificado(area_km2: float,
                                           id_punto: Optional[str] = None,
                                           ) -> None:
    """
    El limite de area del metodo racional modificado (num. 3.12.2.1, pag.
    impresa 51): «áreas menores de 770 km2», desigualdad ESTRICTA. Desde ahi
    lanza `MetodoNoEvaluableError` nombrando los metodos de hidrograma que el
    Manual describe para cuencas mayores y que el programa NO implementa.
    """
    if not area_km2 < TC_TEMEZ_AREA_MAX_KM2:
        raise _no_evaluable(
            "Q",
            f"el metodo racional modificado vale para areas menores de "
            f"{TC_TEMEZ_AREA_MAX_KM2:g} km2 ({NUMERAL_TC_TEMEZ}) y la cuenca "
            f"tiene {area_km2:g} km2",
            PROCEDIMIENTO_FUERA_DEL_RACIONAL_MODIFICADO, id_punto)


def factor_reductor_por_area(area_km2: float) -> float:
    """
    El factor reductor KA de la ecuacion (32) del num. 3.12.2.1 (pag. impresa
    51): KA = 1 – (log10 A/15), A en km2, leido como 1 − log10(A)/15 (la
    `Interpretacion` de la cita MC_HHD.3.12.2.1#KA dice por que).
    """
    return 1 - math.log10(area_km2) / FACTOR_REDUCTOR_AREA_SI["divisor"]


def intensidad_racional_modificado_mm_h(*, P_mm: float, Tc_h: float) -> float:
    """
    La intensidad del metodo racional modificado, ecuacion (34) del num.
    3.12.2.1 (pag. impresa 52):

        I = (P/24) · (11)^((28^0.1 − Tc^0.1)/(28^0.1 − 1))

    P = precipitacion maxima corregida sobre la cuenca en mm (ecuacion 33),
    Tc en HORAS, I en mm/h. El 11 esta escrito en la ecuacion, fijo: la
    pagina no le da nombre, mapa ni tabla por region.
    """
    k = INTENSIDAD_RACIONAL_MODIFICADO_SI
    referencia = k["horas_de_referencia"] ** k["exponente"]
    exponente = (referencia - Tc_h ** k["exponente"]) / (referencia - 1)
    return P_mm / k["horas_del_dia"] * k["factor"] ** exponente


def umbral_de_escorrentia_mm(CN: float) -> float:
    """
    El umbral de escorrentia de la ecuacion (35), en mm: Po = (5000/CN) − 50
    (num. 3.12.2.1, pag. impresa 52). Con CN = 100 vale 0.
    """
    k = UMBRAL_ESCORRENTIA_SI
    return k["numerador"] / CN - k["resta"]


def _c_de_la_35(lluvia_mm: float, Po_mm: float) -> float:
    """La aritmetica de la ecuacion (35), con la lluvia que se le pase."""
    k = COEFICIENTE_RACIONAL_MODIFICADO
    return ((lluvia_mm - Po_mm) * (lluvia_mm + k["suma_numerador"] * Po_mm)
            / (lluvia_mm + k["suma_denominador"] * Po_mm) ** 2)


def coeficiente_racional_modificado(*, Pd_mm: float, CN: float,
                                    id_punto: Optional[str] = None) -> float:
    """
    El coeficiente de escorrentia del metodo racional modificado, ecuacion
    (35) del num. 3.12.2.1 (pag. impresa 52):

        C = (Pd − Po)(Pd + 23·Po) / (Pd + 11·Po)^2 ,  Po = (5000/CN) − 50

    Pd es la precipitacion maxima DIARIA, la que la ecuacion escribe, y NO la
    P corregida por el area de la (33): se aplica como esta escrita, sin
    corregirla, y el paso lo declara (ficha VE2-F). La «p» minuscula del
    denominador se lee Pd (`Interpretacion` de MC_HHD.3.12.2.1#C).

    Si la lluvia no pasa del umbral la ecuacion da un coeficiente nulo o
    negativo, y el Manual no dice que hacer: `MetodoNoEvaluableError`, no un
    cero que dejaria la obra sin caudal.
    """
    Po = umbral_de_escorrentia_mm(CN)
    if not Pd_mm > Po:
        raise _no_evaluable(
            "C",
            f"la precipitacion maxima diaria de diseño, Pd = {Pd_mm:.1f} mm, "
            f"no supera el umbral de escorrentia Po = {Po:.1f} mm que el "
            f"numero de curva CN = {CN:g} da: la ecuacion (35) del num. "
            "3.12.2.1 da un coeficiente de escorrentia nulo o negativo, y el "
            "Manual no dice que hacer con el",
            "revisar el numero de curva de la cuenca (columna CN, Tabla N 07)"
            ", o el caudal declarado por el estudio hidrologico en la "
            "columna Q_m3s",
            id_punto)
    return _c_de_la_35(Pd_mm, Po)


def caudal_racional_modificado(*, C: float, I_mm_h: float, area_km2: float,
                               K: float, id_punto: Optional[str] = None,
                               ) -> float:
    """
    Q = 0,278 · C · I · A · K, ecuacion (29) del num. 3.12.2.1 (pag. impresa
    51): I en mm/h, A en km2, Q en m3/s, K el coeficiente de uniformidad de
    la (31). Desde 770 km2 no se evalua
    (`exigir_alcance_del_racional_modificado`).
    """
    exigir_alcance_del_racional_modificado(area_km2, id_punto)
    return RACIONAL_COEFICIENTE_SI * C * I_mm_h * area_km2 * K


def _tc_ajeno_al_racional_modificado(cuenca: Cuenca) -> MetodoNoEvaluableError:
    return _no_evaluable(
        "tc",
        f"desde {RACIONAL_AREA_MAX_KM2:g} km2 el caudal se calcula por el "
        f"metodo racional modificado ({NUMERAL_RACIONAL_MODIFICADO}), "
        "cuyo tiempo de concentracion es el de su ecuacion (30), la de "
        f"Temez; la fila de la cuenca declara metodo_tc = "
        f"{cuenca.metodo_tc}",
        f"declarar metodo_tc = {TC_METODO_TEMEZ} en la fila de la cuenca "
        "(con ajuste_kirpich vacio), o el caudal declarado en Q_m3s",
        cuenca.id)


def _falta_cn_racional_modificado(cuenca: Cuenca) -> DatoFaltanteError:
    return DatoFaltanteError(
        "CN", id_punto=cuenca.id,
        detalle=f"desde {RACIONAL_AREA_MAX_KM2:g} km2 el caudal se calcula "
                "por el metodo racional modificado, cuyo coeficiente de "
                "escorrentia --ecuacion (35) del num. 3.12.2.1-- pide el "
                "numero de curva de la cuenca. Es la columna opcional CN "
                "del CSV de cuencas (la misma de la ecuacion de retardo); "
                "la lee el estudio hidrologico en la Tabla N 07 "
                f"({NUMERAL_TABLA_07}) y el programa no tiene tabla de la "
                "que leerla")


def _caudal_racional_modificado(cuenca: Cuenca, serie: SerieDeEstacion,
                                TR: float) -> CaudalDeDiseno:
    """
    El caudal de diseño de una obra de 10 a 770 km2 por el metodo racional
    modificado completo (num. 3.12.2.1, ecuaciones 29 a 35; VE-2, ficha
    VE2-F), por la MISMA puerta del criterio 'homogeneidad_serie_fen' que el
    racional simple (`precipitacion_de_diseno`).

    Lo que se comprueba ANTES de ajustar nada: el area (menor de 770 km2),
    que el tiempo de concentracion sea el del metodo --su ecuacion (30),
    `metodo_tc` = temez-- y que la cuenca traiga su numero de curva (columna
    CN, la MISMA columna opcional de la ecuacion de retardo, REUSADA: desde
    10 km2 la exige la ecuacion 35).

    Lo que NO lee: la Tabla N 08 (el metodo da su propio C), la relacion
    intensidad-duracion (su intensidad es la ecuacion 34), la duracion
    minima de la lluvia (el metodo acota Tc desde 0.25 h) ni el criterio
    'coeficiente_uniformidad_temez' (K es parte de la ecuacion 29, no una
    eleccion: el criterio rige solo el uso hibrido por debajo de 10 km2).
    """
    exigir_alcance_del_racional_modificado(cuenca.area_km2, cuenca.id)
    if cuenca.metodo_tc != TC_METODO_TEMEZ:
        raise _tc_ajeno_al_racional_modificado(cuenca)
    if cuenca.CN is None:
        raise _falta_cn_racional_modificado(cuenca)
    tc, paso_tc, avisos_tc = tiempo_de_concentracion(cuenca,
                                                     racional_modificado=True)
    adoptado, evaluados, tratamiento, pasos_lluvia, avisos_lluvia = \
        precipitacion_de_diseno(serie, TR, id_punto=cuenca.id)
    Tc_h = tc / MINUTOS_POR_HORA
    Pd = adoptado.P_TR_mm
    A_km2, CN = cuenca.area_km2, cuenca.CN
    KA = factor_reductor_por_area(A_km2)
    P = KA * Pd
    I = intensidad_racional_modificado_mm_h(P_mm=P, Tc_h=Tc_h)
    Po = umbral_de_escorrentia_mm(CN)
    C = coeficiente_racional_modificado(Pd_mm=Pd, CN=CN, id_punto=cuenca.id)
    K = coeficiente_de_uniformidad(Tc_h)
    Q = caudal_racional_modificado(C=C, I_mm_h=I, area_km2=A_km2, K=K,
                                   id_punto=cuenca.id)
    if not (math.isfinite(Q) and Q > 0):
        raise LimiteNumericoError(
            "Q calculado", valor=Q, id_punto=cuenca.id,
            motivo=f"el caudal no es un numero positivo con C = {C:g}, "
                   f"I = {I:g} mm/h, A = {A_km2:g} km2 y K = {K:g}")

    cita_metodo = _REG.cita("MC_HHD.3.12.2.1#METODO")
    A = Magnitud("A", A_km2, "km2", f"columna area_km2 de {cuenca.origen}",
                 cifras=CIFRAS_FINA)
    Pd_mag = Magnitud("Pd", Pd, "mm",
                      f"paso {CODIGO_AJUSTE}: la precipitacion maxima en 24 "
                      "horas del periodo de retorno de diseño, que el "
                      "programa toma por la «Precitación máxima diaria» del "
                      "metodo", cifras=CIFRAS_MAGNITUD)
    Tc_mag = Magnitud("Tc", Tc_h, "h", f"paso {CODIGO_TC}, de minutos a horas",
                      cifras=CIFRAS_FINA)
    sin_veredicto = Veredicto(
        tipo=TipoDeVeredicto.SIN_VEREDICTO,
        explicacion="calculo de un factor del metodo, no verificacion")

    paso_i = paso(
        "FH.RM_INTENSIDAD", codigo=CODIGO_INTENSIDAD,
        que=("Intensidad del metodo racional modificado: precipitacion "
             "corregida por el area y ecuacion (34)"),
        formula=("KA = 1 − log10(A)/15 ; P = KA · Pd ; I = (P/24) · "
                 "11^((28^0.1 − Tc^0.1)/(28^0.1 − 1))   [A en km2, P y Pd en "
                 "mm, Tc en horas, I en mm/h]"),
        formula_cita_id="MC_HHD.3.12.2.1#I",
        citas_textuales=("MC_HHD.3.12.2.1#METODO", "MC_HHD.3.12.2.1#KA",
                         "MC_HHD.3.12.2.1#P", "MC_HHD.3.12.2.1#I"),
        sustitucion=(
            A,
            Magnitud("KA", KA, "", "factor reductor por area, ecuacion (32)",
                     cifras=CIFRAS_FINA),
            Pd_mag,
            Magnitud("P", P, "mm", "precipitacion maxima corregida sobre la "
                     "cuenca, ecuacion (33)", cifras=CIFRAS_MAGNITUD),
            Tc_mag),
        resultado=Magnitud("I", I, "mm/h", "intensidad de diseño, ecuacion "
                           "(34)", cifras=CIFRAS_MAGNITUD),
        veredicto=sin_veredicto,
        nota_del_proyecto=(
            f"{_lectura_del_proyecto('MC_HHD.3.12.2.1#KA')} El 11 de la "
            "ecuacion (34) esta escrito en la pagina, fijo: el Manual no le "
            "da nombre, mapa ni tabla por region. La intensidad no sale de "
            "la relacion intensidad-duracion de la Fase 1-bis (Dick y "
            "Peschke o la Tabla N 04) sino de la ecuacion del metodo, y la "
            "duracion es el tiempo de concentracion, que el metodo acota "
            "desde 0.25 h."))

    C_con_P = _c_de_la_35(P, Po)
    texto_C_con_P = (f"{C_con_P:.3f}" if P > Po else
                     "nulo o negativo (P no supera Po)")
    paso_c = paso(
        "FH.RM_C", codigo=CODIGO_C,
        que=("Coeficiente de escorrentia del metodo racional modificado, por "
             "el numero de curva"),
        formula=("Po = 5000/CN − 50 ; C = (Pd − Po)·(Pd + 23·Po) / "
                 "(Pd + 11·Po)^2   [Pd y Po en mm]"),
        formula_cita_id="MC_HHD.3.12.2.1#C",
        citas_textuales=("MC_HHD.3.12.2.1#C", "MC_HHD.3.11#T07"),
        sustitucion=(
            Magnitud("CN", CN, "", f"columna CN de {cuenca.origen}: numero de "
                     "curva que el estudio hidrologico lee en la Tabla N 07",
                     cifras=CIFRAS_MAGNITUD),
            Pd_mag,
            Magnitud("Po", Po, "mm", "umbral de escorrentia, (5000/CN) − 50",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("C", C, "", "coeficiente de escorrentia, ecuacion "
                           "(35)", cifras=CIFRAS_MAGNITUD),
        veredicto=sin_veredicto,
        nota_del_proyecto=(
            "DECLARADO EN EL PUNTO DE USO. La ecuacion (35) escribe Pd, la "
            "precipitacion maxima diaria, y no la P corregida por el area de "
            "la ecuacion (33), que la (34) si usa: el programa la aplica "
            "como esta escrita, sin corregirla. Con P = "
            f"{P:.1f} mm en lugar de Pd = {Pd:.1f} mm el coeficiente seria "
            f"{texto_C_con_P} en vez de {C:.3f}. "
            f"{_lectura_del_proyecto('MC_HHD.3.12.2.1#C')} La Tabla N 08 no "
            "entra: el metodo da su propio coeficiente, y las columnas "
            "cobertura y suelo de la fila no se leen para esta cuenca."))

    cita_rango = "MC_HHD.3.12.2.1#TC"
    frontera = _REG.cita("MC_HHD.3.12.2#AREA")
    paso_q = paso(
        "FH.RM_CAUDAL", codigo=CODIGO_RACIONAL,
        que="Caudal de diseño por el metodo racional modificado",
        formula=("Q = 0.278 · C · I · A · K ; K = 1 + Tc^1.25 / (Tc^1.25 + 14)"
                 "   [Q en m3/s, I en mm/h, A en km2, Tc en horas]"),
        formula_cita_id="MC_HHD.3.12.2.1#K",
        citas_textuales=("MC_HHD.3.12.2.1#K", "MC_HHD.3.12.2#AREA",
                         "MC_HHD.3.12.3.2a#AREA", "MC_HHD.3.12.3.2b#AREA",
                         "MC_HHD.3.12.4"),
        sustitucion=(
            Magnitud("C", C, "", f"paso {CODIGO_C}", cifras=CIFRAS_MAGNITUD),
            Magnitud("I", I, "mm/h", f"paso {CODIGO_INTENSIDAD}",
                     cifras=CIFRAS_MAGNITUD),
            A, Tc_mag,
            Magnitud("K", K, "", "coeficiente de uniformidad, ecuacion (31): "
                     "parte de la ecuacion del metodo, no una eleccion",
                     cifras=CIFRAS_FINA)),
        resultado=Magnitud("Q", Q, "m3/s", "caudal de diseño",
                           cifras=CIFRAS_MAGNITUD),
        umbral=Umbral(
            descripcion=("area maxima de cuenca del metodo racional "
                         "modificado (exclusiva)"),
            valor=TC_TEMEZ_AREA_MAX_KM2, unidad="km2", cita_id=cita_rango,
            caracter=_caracter(cita_rango),
            aplicacion="limite de validez: desde ese area el programa no "
                       "evalua el metodo y nombra los de hidrograma, que no "
                       "implementa (la fuente dice para que cuencas vale, "
                       "no prohibe salir)"),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.CUMPLE,
            margen=TC_TEMEZ_AREA_MAX_KM2 - A_km2, unidad="km2",
            explicacion="el area de la cuenca esta dentro del alcance del "
                        "metodo racional modificado"),
        nota_del_proyecto=(
            f"Metodo racional modificado ({cita_metodo.como_texto()}): "
            f"«{cita_metodo.texto_literal.texto}». La frontera con el "
            "racional simple es la de siempre: el Manual dice del racional "
            f"«{frontera.texto_literal.texto}» ({frontera.como_texto()}), y "
            "usar el modificado desde ahi y no por debajo es lectura del "
            "proyecto --los dos rangos se solapan bajo 10 km2, donde sigue "
            "el racional simple de T-1--. K va siempre: es parte de la "
            "ecuacion (29); el criterio "
            f"'{CRITERIO_K_TEMEZ}' rige solo el uso hibrido de la formula "
            "de Temez por debajo de 10 km2."))
    q, lamina, paso_qa = _paso_q_especifico(
        Magnitud("Q", Q, "m3/s", f"paso {CODIGO_RACIONAL}",
                 cifras=CIFRAS_MAGNITUD), A)
    aviso_espana = (
        f"El caudal de esta cuenca ({A_km2:g} km2) se calculo por el metodo "
        "racional modificado, que el Manual describe asi: "
        f"«{cita_metodo.texto_literal.texto}» ({cita_metodo.como_texto()}). "
        "El Manual lo adopta para el Peru sin decir como se adapto; el "
        "estudio hidrologico tiene que defender su uso en esta cuenca.")
    return CaudalDeDiseno(
        Q_m3s=Q, origen=ORIGEN_CAUDAL_CALCULADO,
        leyenda=LEYENDA_CAUDAL_CALCULADO,
        pasos=(*pasos_lluvia, paso_tc, paso_i, paso_c, paso_q, paso_qa),
        avisos=(*avisos_lluvia, *avisos_tc, aviso_espana),
        de_donde=(f"{cuenca.origen}; estacion «{serie.estacion}» de "
                  f"{serie.origen}; metodo racional modificado (num. "
                  "3.12.2.1)"),
        TR_anios=TR, area_km2=A_km2, tc_min=tc, I_mm_h=I, C=C,
        P24_TR_mm=Pd, distribucion=adoptado.distribucion,
        tratamiento_fen=tratamiento, q_especifico_m3s_km2=q,
        lamina_equivalente_mm_h=lamina, ajustes=evaluados,
        metodo_tc=cuenca.metodo_tc, duracion_min=tc, K_uniformidad=K)


def caudal_de_diseno(cuenca: Cuenca, serie: SerieDeEstacion,
                     TR: float) -> CaudalDeDiseno:
    """
    El caudal de diseño de una obra por el metodo racional (num. 3.12.2), con
    la memoria hidrologica completa: serie y FEN, ajuste, bondad, juicio del
    tratamiento FEN, tiempo de concentracion, intensidad, C, Q y Q/A.

    `TR` es el periodo de retorno en años: el de la Fase 2 para el caudal de
    diseño, y el de cualquier otro evento --el extremo de V8-- con la misma
    llamada. Vale igual para la cuenca de una quebrada (Familia A) y para el
    area tributaria de una cuneta (Familia B).
    """
    return _caudal_calculado(cuenca, serie, TR, de_cuneta=False)


def caudal_de_aporte_cuneta(cuenca: Cuenca, serie: SerieDeEstacion,
                            TR: float) -> CaudalDeDiseno:
    """
    El caudal que el area tributaria entrega a un tramo de cuneta (num.
    4.1.2.1 b, «Caudal Q de aporte», pag. impresa 177), CON su memoria: el
    mismo `CaudalDeDiseno` que `caudal_de_diseno` --tc, I, C, Q y sus pasos--
    y por la misma compuerta del criterio FEN. Es el enlace para la longitud
    de cuneta por capacidad de la Fase 10 (T-9).

    El Manual escribe aqui Q = C·I·A / 3.6. No hay un segundo coeficiente: se
    calcula con el 0.278 de la ecuacion (28), y el paso lo declara.

    `cuenca` describe el area tributaria del tramo: `L_cauce_m` y
    `S_cauce_cuenca` son la longitud y la pendiente del recorrido del flujo,
    y `cobertura` una superficie de la plataforma vial o una fila de la
    Tabla N 08. NUNCA se rellena una cobertura por omision.
    """
    return _caudal_calculado(cuenca, serie, TR, de_cuneta=True)


# ===========================================================================
# 5-ter. Lo que detendria el calculo, anticipado sin TR (pre-vuelo) — VE-4b
# ===========================================================================
#
# EL PRE-VUELO NO CALCULA EL CAUDAL (ficha T1-04). Lo que anticipa son las
# COMPUERTAS del calculo que no dependen del periodo de retorno de la Fase 2
# --que el pre-vuelo no tiene, porque es de M1 y pide la luz y el punto
# cargado--, con las MISMAS funciones o los MISMOS constructores de la
# excepcion que la corrida levanta, para que la fila del pre-vuelo y el
# `Bloqueo` real digan el mismo texto. Y sin registrar el uso de ningun
# criterio: un pre-vuelo no es una corrida y M11 imprime solo los usados.
#
# Lo que SI depende del TR se anuncia con `depende_del_tr` y un mensaje que
# dice la condicion (hoy, `serie_sin_fen` con años FEN: se detiene si da menos
# lluvia que la serie completa en el TR de diseño). Lo que no se anticipa, y
# por que, esta en la ficha T1-04 de `docs/decisiones_diferidas.md`.

def _leer_sin_registrar(clave: str) -> Any:
    """
    `ca.valor` SIN registrar el uso: el valor efectivo (declarado en caliente
    o de archivo), o `CriterioPendienteError` con el mismo concepto y la misma
    fuente que `ca.valor` pondria.
    """
    criterio = ca.criterio_efectivo(clave)
    if criterio.valor is None:
        raise CriterioPendienteError(clave, concepto=criterio.concepto,
                                     fuente=criterio.fuente)
    return criterio.valor


def _dato_de(exc: ErrorProyecto) -> str:
    """Lo que hay que tocar: la clave, el campo o la magnitud no evaluable."""
    if isinstance(exc, CriterioPendienteError):
        return exc.clave
    if isinstance(exc, MetodoNoEvaluableError):
        return exc.que
    return str(getattr(exc, "campo", "") or type(exc).__name__)


def anticipar_caudal(cuenca: Cuenca, serie: SerieDeEstacion, *,
                     de_cuneta: bool) -> Tuple[ObstaculoAnticipado, ...]:
    """
    Lo que DETENDRIA `caudal_de_diseno` (o `caudal_de_aporte_cuneta`, con
    `de_cuneta`) para esta cuenca y esta serie, sin calcular la lluvia ni el
    caudal y sin registrar el uso de ningun criterio (VE-4b, ficha T1-04).

    Recorre las compuertas en el orden del calculo y las dice TODAS: la
    corrida se detiene en la primera, el pre-vuelo estima de mas a proposito.
    Las que anticipa, por metodo (num. 3.12.2 y 3.12.2.1 del Manual de
    Hidrologia):

      * el area contra el metodo: el racional desde 10 km2 en una cuneta, el
        racional modificado desde 770 km2; y desde 10 km2 en una obra, que su
        Tc sea el de Temez y que traiga numero de curva;
      * la serie (num. 3.4 y 3.7): los cuatro criterios del ajuste, el
        tratamiento 'dos_poblaciones', la serie mas corta que la Tabla N 03,
        la distribucion sin estimador impreso y la prueba de Kolmogorov-
        Smirnov de la adoptada (no depende del TR: `_bondad`, con la MISMA
        regla de eleccion, `_elegir_con`);
      * el tiempo de concentracion (num. 3.9, Tabla N 05; num. 3.12.2.1): la
        poblacion del metodo con su criterio, el desnivel de California, el
        numero de curva de la ecuacion de retardo, el area y el rango de Tc
        de Temez;
      * los criterios del coeficiente vial, de la intensidad y del
        coeficiente de uniformidad, cuando la ruta los lee.

    Y una que depende del TR, marcada: `serie_sin_fen` sobre una serie con
    años FEN «puede detener».
    """
    obstaculos: List[ObstaculoAnticipado] = []

    def anotar(exc: ErrorProyecto, *, depende_del_tr: bool = False) -> None:
        obstaculos.append(ObstaculoAnticipado.de_excepcion(
            exc, _dato_de(exc), depende_del_tr=depende_del_tr))

    def criterio(clave: str) -> Any:
        try:
            return _leer_sin_registrar(clave)
        except CriterioPendienteError as exc:
            anotar(exc)
            return None

    def compuerta(fn) -> bool:
        try:
            fn()
        except ErrorProyecto as exc:
            anotar(exc)
            return False
        return True

    def tiempo_de_concentracion_(racional_modificado: bool) -> None:
        metodo = cuenca.metodo_tc
        if metodo == TC_METODO_KIRPICH:
            compuerta(lambda: _exigir_poblacion(
                metodo, pendiente=cuenca.S_cauce_cuenca, id_punto=cuenca.id,
                leer=_leer_sin_registrar))
        elif metodo == TC_METODO_CALIFORNIA:
            if cuenca.H_desnivel_m is None:
                anotar(_falta_desnivel_california(cuenca))
            else:
                compuerta(lambda: _exigir_poblacion(
                    metodo, pendiente=cuenca.H_desnivel_m / cuenca.L_cauce_m,
                    id_punto=cuenca.id, leer=_leer_sin_registrar))
        elif metodo == TC_METODO_RETARDO_SCS:
            if cuenca.CN is None:
                anotar(_falta_cn_retardo(cuenca))
            compuerta(lambda: _exigir_poblacion(
                metodo, area_km2=cuenca.area_km2, id_punto=cuenca.id,
                leer=_leer_sin_registrar))
        elif metodo in METODOS_TC_ITERATIVOS:
            # VE-5: el dato de la superficie. La condicion i·L de Izzard
            # depende de la intensidad, que depende del TR: no se anticipa.
            dato = (cuenca.c_retardo_izzard if metodo == TC_METODO_IZZARD
                    else cuenca.n_manning_superficial)
            if dato is None:
                anotar(_falta_dato_iterativo(cuenca))
        elif metodo == TC_METODO_TEMEZ:
            compuerta(lambda: tc_temez_h(
                L_km=cuenca.L_cauce_m / METROS_POR_KM, S=cuenca.S_cauce_cuenca,
                area_km2=cuenca.area_km2, id_punto=cuenca.id,
                procedimiento=(PROCEDIMIENTO_FUERA_DEL_RACIONAL_MODIFICADO
                               if racional_modificado else None)))
        # La formula de la FAA no tiene poblacion descrita ni rango propio, y
        # su C de la Tabla N 08 cae siempre dentro de (0, 1.1).

    def lluvia() -> None:
        tratamiento = criterio(CRITERIO_FEN)
        if tratamiento == FEN_DOS_POBLACIONES:
            anotar(_no_evaluable_dos_poblaciones(cuenca.id))
        declarada = criterio(CRITERIO_DISTRIBUCION)
        alfa = criterio(CRITERIO_ALFA)
        factor = criterio(CRITERIO_FACTOR_P24)
        if (tratamiento not in (FEN_SERIE_COMPLETA, FEN_SERIE_SIN_FEN)
                or declarada is None or alfa is None or factor is None
                or not factor > 0):
            # Sin tratamiento evaluable no hay serie que ajustar; un factor
            # que no es positivo lo rechaza ya la ventana del criterio.
            return
        serie_ajustada = _serie_con_factor(serie, factor)
        valores = tuple(r.p24_mm for r in
                        _registros_por_tratamiento(serie_ajustada, tratamiento))
        try:
            adoptado, evaluados, _ = _elegir_con(
                valores, declarada,
                lambda distribucion: _bondad(valores, distribucion, alfa=alfa)[0])
        except ErrorProyecto as exc:
            anotar(exc)
            return
        if not adoptado.acepta:
            anotar(_no_evaluable_ks(adoptado, evaluados, serie=serie_ajustada,
                                    tratamiento=tratamiento, alfa=alfa,
                                    id_punto=cuenca.id))
            return
        if tratamiento == FEN_SERIE_SIN_FEN and serie_ajustada.anios_fen:
            anotar(_no_evaluable(
                "P24(TR)",
                f"PUEDE detenerse: con '{FEN_SERIE_SIN_FEN}' el calculo se "
                "detiene si la precipitacion de diseño da MENOS que con "
                f"'{FEN_SERIE_COMPLETA}' (regla de la Fase 1-bis de la hoja "
                "de ruta y num. 3.4 del Manual), y esa comparacion se hace "
                "con el periodo de retorno de la Fase 2, que el pre-vuelo no "
                f"calcula; la serie de «{serie.estacion}» declara "
                f"{len(serie_ajustada.anios_fen)} años FEN",
                _procedimiento_del_otro_tratamiento(FEN_SERIE_COMPLETA),
                cuenca.id), depende_del_tr=True)

    if not de_cuneta and \
            metodo_de_caudal(cuenca.area_km2) == METODO_RACIONAL_MODIFICADO:
        # El orden de `_caudal_racional_modificado`. Desde 770 km2 el area
        # detiene el metodo entero: el limite de area de Temez seria el MISMO
        # hecho dicho dos veces, y no se repite.
        area_en_rango = compuerta(lambda: exigir_alcance_del_racional_modificado(
            cuenca.area_km2, cuenca.id))
        if cuenca.metodo_tc != TC_METODO_TEMEZ:
            anotar(_tc_ajeno_al_racional_modificado(cuenca))
        if cuenca.CN is None:
            anotar(_falta_cn_racional_modificado(cuenca))
        if cuenca.metodo_tc == TC_METODO_TEMEZ and area_en_rango:
            tiempo_de_concentracion_(racional_modificado=True)
        lluvia()
        return tuple(obstaculos)
    # El orden de `_caudal_calculado`: area, lluvia, C, Tc, intensidad, K.
    compuerta(lambda: exigir_alcance_del_racional(cuenca.area_km2, cuenca.id))
    lluvia()
    if cuenca.cobertura in SUPERFICIES_VIALES:
        criterio(CRITERIO_C_VIAL)
    tiempo_de_concentracion_(racional_modificado=False)
    if criterio(CRITERIO_RELACION) == RELACION_IDF_REGIONAL:
        # VE-5: la relacion regional pide sus tres factores [S]; los mismos
        # que lanzaria la corrida (`factores_idf_regional`), sin registrar.
        compuerta(lambda: factores_idf_regional(leer=_leer_sin_registrar))
    criterio(CRITERIO_DURACION_MINIMA)
    if cuenca.metodo_tc == TC_METODO_TEMEZ:
        criterio(CRITERIO_K_TEMEZ)
    return tuple(obstaculos)


def exigir_areas_coherentes(*, area_ha: float, area_km2: float,
                            id_punto: Optional[str] = None,
                            origen_cuenca: str = "") -> None:
    """
    El area de la cuenca de una obra esta escrita DOS veces cuando la corrida
    trae --cuencas: `area_ha` en el CSV de puntos (Sec. 1.2), que clasifica
    la obra y fija su periodo de retorno, y `area_km2` en el CSV de cuencas,
    que entra al metodo racional (num. 3.12.2). Tienen que decir lo mismo; si
    difieren mas que un redondeo (`TOL_REL_AREA_ESCRITA_DOS_VECES`) lanza
    `DatoInvalidoError` nombrando el par. El programa no elige una.
    """
    de_puntos_km2 = area_de_columna_km2(area_ha)
    if not math.isclose(de_puntos_km2, area_km2,
                        rel_tol=TOL_REL_AREA_ESCRITA_DOS_VECES):
        raise DatoInvalidoError(
            "area_ha / area_km2",
            valor=f"{area_ha:g} ha / {area_km2:g} km2", id_punto=id_punto,
            motivo=f"contradice a otro dato: la columna area_ha del CSV de "
                   f"puntos dice {area_ha:g} ha ({de_puntos_km2:g} km2) y la "
                   f"columna area_km2 de {origen_cuenca or 'el CSV de cuencas'} "
                   f"dice {area_km2:g} km2. Son la misma cuenca: la primera "
                   "fija el periodo de retorno y la segunda entra al caudal, "
                   "y el programa no elige cual vale")


def area_de_columna_km2(area_ha: float) -> float:
    """El area de la columna `area_ha` del CSV de puntos, en km2."""
    return area_ha / HECTAREAS_POR_KM2


# ===========================================================================
# 6. Carga de las dos entradas (--cuencas y --estacion)
# ===========================================================================

def _texto_de(ruta: Path, datos: Optional[bytes]) -> str:
    """
    El texto del archivo: el de `datos` si ya se leyo, o el del disco.

    Con `datos` se decodifica EXACTAMENTE como `Path.read_text` decodifica el
    archivo (UTF-8 con BOM opcional y saltos de linea universales), de modo
    que leer por la ruta o por los bytes da las mismas filas. Es lo que deja
    a `servicio.cargar_hidrologia` leer cada archivo UNA vez y sacar la huella
    de los mismos bytes que aqui se parsean (UI-1, como `csv_sha1`: PC-09).
    """
    if datos is None:
        return Path(ruta).read_text(encoding="utf-8-sig")
    return io.TextIOWrapper(io.BytesIO(datos), encoding="utf-8-sig").read()


def _filas(ruta: Path, obligatorias: Sequence[str],
           opcionales: Sequence[str] = (), *,
           datos: Optional[bytes] = None) -> List[Tuple[int, Dict[str, str]]]:
    """
    Las filas de datos de un CSV de entrada, con su numero de linea. Las
    lineas que empiezan por `#` son comentarios (asi un archivo de prueba
    puede decir que lo es). Un fallo de E/S sale como tal. `datos` son los
    bytes del archivo ya leidos (`_texto_de`); `ruta` sigue nombrandolo en
    los mensajes.
    """
    texto = _texto_de(ruta, datos)
    lineas = [(n, linea) for n, linea in enumerate(texto.splitlines(), start=1)
              if linea.strip() and not linea.lstrip().startswith(MARCA_COMENTARIO)]
    if not lineas:
        raise DatoFaltanteError(
            obligatorias[0],
            detalle=f"'{Path(ruta).name}' no tiene ni encabezado")
    encabezado = [c.strip() for c in next(csv.reader(io.StringIO(lineas[0][1])))]
    faltan = [c for c in obligatorias if c not in encabezado]
    if faltan:
        raise DatoFaltanteError(
            faltan[0],
            detalle=f"el encabezado de '{Path(ruta).name}' no trae "
                    f"{', '.join(faltan)}. Columnas obligatorias: "
                    f"{', '.join(obligatorias)}"
                    + (f"; opcionales: {', '.join(opcionales)}"
                       if opcionales else ""))
    sobran = [c for c in encabezado
              if c and c not in obligatorias and c not in opcionales]
    if sobran:
        raise DatoInvalidoError(
            "(encabezado)", valor=", ".join(sobran),
            motivo=f"columna no reconocida en '{Path(ruta).name}': revisar "
                   "si esta mal escrita")
    filas: List[Tuple[int, Dict[str, str]]] = []
    for numero, linea in lineas[1:]:
        celdas = [c.strip() for c in next(csv.reader(io.StringIO(linea)))]
        if len(celdas) > len(encabezado):
            raise DatoInvalidoError(
                "(fila completa)", valor=linea,
                motivo=f"la linea {numero} de '{Path(ruta).name}' trae mas "
                       "celdas que el encabezado")
        celdas += [""] * (len(encabezado) - len(celdas))
        filas.append((numero, dict(zip(encabezado, celdas))))
    if not filas:
        raise DatoFaltanteError(
            obligatorias[0],
            detalle=f"'{Path(ruta).name}' trae el encabezado pero ninguna "
                    "fila de datos")
    return filas


def _texto(fila: Dict[str, str], columna: str, donde: str) -> str:
    valor = fila.get(columna, "")
    if not valor:
        raise DatoFaltanteError(columna, detalle=f"celda vacia en {donde}")
    return valor


def _numero(fila: Dict[str, str], columna: str, donde: str, *,
            opcional: bool = False, techo: Optional[float] = None,
            admite_cero: bool = False,
            id_punto: Optional[str] = None) -> Optional[float]:
    """
    Un numero finito y positivo; `techo` es exclusivo. Con `admite_cero`, un
    0 es un dato (un año sin lluvia en una estacion de costa arida lo es).
    """
    bruto = fila.get(columna, "")
    if not bruto:
        if opcional:
            return None
        raise DatoFaltanteError(columna, id_punto=id_punto,
                                detalle=f"celda vacia en {donde}")
    try:
        valor = float(bruto)
    except ValueError:
        raise DatoInvalidoError(columna, valor=bruto, id_punto=id_punto,
                                motivo=f"no es un numero ({donde})") from None
    if admite_cero:
        if not (math.isfinite(valor) and valor >= 0):
            raise DatoInvalidoError(
                columna, valor=bruto, id_punto=id_punto,
                motivo=f"tiene que ser un numero finito y no negativo ({donde})")
    elif not (math.isfinite(valor) and valor > 0):
        raise DatoInvalidoError(
            columna, valor=bruto, id_punto=id_punto,
            motivo=f"tiene que ser un numero finito y positivo ({donde})")
    if techo is not None and not valor < techo:
        raise DatoInvalidoError(
            columna, valor=bruto, id_punto=id_punto,
            motivo=f"una pendiente en m/m es menor de {techo:g}: un valor "
                   f"mayor delata una celda en porcentaje ({donde})")
    return valor


def cargar_cuencas(ruta: Any, *, datos: Optional[bytes] = None) -> Dict[str, Cuenca]:
    """
    Lee el CSV de cuencas (--cuencas): una fila por obra, con el `id` del CSV
    de puntos. Valida forma y dominio y NO corrige nada. Las claves de
    cobertura, suelo, metodo y ajuste se comprueban contra sus tablas aqui,
    para que un error de tipeo salga al cargar y no a mitad de la corrida.

    Tres reglas que la auditoria de T-1 dejo: `S_terreno` es columna
    obligatoria (antes, vacia, la Tabla N 08 se leia con la pendiente del
    cauce); `ajuste_kirpich` es obligatoria con el metodo de Kirpich y va
    vacia con cualquier otro (un factor escrito que no se aplica es un dato
    contradicho, no ignorado); y con una superficie de la plataforma vial en
    `cobertura` la celda `suelo` va vacia, porque esa tabla no tiene suelo.

    `datos` (UI-1): los bytes del archivo ya leidos; sin ellos se lee `ruta`.
    """
    ruta = Path(ruta)
    cuencas: Dict[str, Cuenca] = {}
    for numero, fila in _filas(ruta, COLUMNAS_CUENCAS,
                               COLUMNAS_CUENCAS_OPCIONALES, datos=datos):
        donde = f"'{ruta.name}', linea {numero}"
        id_ = _texto(fila, "id", donde)
        if id_ in cuencas:
            raise DatoInvalidoError(
                "id", valor=id_, id_punto=id_,
                motivo=f"la obra tiene dos filas en '{ruta.name}': una "
                       "cuenca por obra")
        cobertura = _texto(fila, "cobertura", donde)
        if cobertura in SUPERFICIES_VIALES:
            suelo = fila.get("suelo", "")
            if suelo:
                raise DatoInvalidoError(
                    "suelo", valor=suelo, id_punto=id_,
                    motivo=f"contradice a otro dato: la cobertura "
                           f"'{cobertura}' es una superficie de la "
                           "plataforma vial, cuyo coeficiente no depende "
                           f"del tipo de suelo; la celda va vacia ({donde})")
        else:
            suelo = _texto(fila, "suelo", donde)
            if (cobertura, suelo) not in TABLA_08_COEFICIENTE_DE_ESCORRENTIA:
                coeficiente_de_escorrentia(cobertura=cobertura, suelo=suelo,
                                           S=1)
        metodo = _texto(fila, "metodo_tc", donde)
        if metodo not in METODOS_TC:
            raise DatoInvalidoError(
                "metodo_tc", valor=metodo, id_punto=id_,
                motivo="los metodos de tiempo de concentracion que el "
                       "programa evalua son " + ", ".join(METODOS_TC)
                       + f" ({donde})")
        ajuste = fila.get("ajuste_kirpich", "") or None
        if metodo == TC_METODO_KIRPICH:
            if ajuste is None:
                raise DatoFaltanteError(
                    "ajuste_kirpich", id_punto=id_,
                    detalle="con metodo_tc = kirpich hay que declarar el "
                            "ajuste por tipo de superficie de la Tabla N 05 "
                            "(" + ", ".join(TC_KIRPICH_AJUSTES) + "): "
                            "«ninguno» es una clave y se escribe "
                            f"({donde})")
            if ajuste not in TC_KIRPICH_AJUSTES:
                raise DatoInvalidoError(
                    "ajuste_kirpich", valor=ajuste, id_punto=id_,
                    motivo="los ajustes que la Tabla N 05 escribe para "
                           "Kirpich son " + ", ".join(TC_KIRPICH_AJUSTES)
                           + f" ({donde})")
        elif ajuste is not None:
            raise DatoInvalidoError(
                "ajuste_kirpich", valor=ajuste, id_punto=id_,
                motivo=f"contradice a otro dato: el ajuste es de la fila "
                       f"Kirpich de la Tabla N 05 y esta fila declara "
                       f"metodo_tc = {metodo}, que no lo aplica; la celda va "
                       f"vacia ({donde})")
        # --- VE-5 (ficha T1-07) --- El dato de la superficie de Izzard y de
        # la onda cinematica: opcional, y escrito con OTRO metodo es un dato
        # contradicho (como el ajuste de Kirpich), no ignorado. Que falte con
        # su metodo se dice al calcular, y lo anticipa el pre-vuelo.
        de_superficie: Dict[str, Optional[float]] = {}
        for metodo_suyo, columna in METODOS_TC_ITERATIVOS.items():
            de_superficie[columna] = _numero(fila, columna, donde,
                                             opcional=True, id_punto=id_)
            if de_superficie[columna] is not None and metodo != metodo_suyo:
                raise DatoInvalidoError(
                    columna, valor=fila.get(columna), id_punto=id_,
                    motivo=f"contradice a otro dato: la columna es de la "
                           f"fila «{metodo_suyo}» de la Tabla N 05 y esta "
                           f"fila declara metodo_tc = {metodo}, que no la "
                           f"usa; la celda va vacia ({donde})")
        CN = _numero(fila, "CN", donde, opcional=True, id_punto=id_)
        if CN is not None and not CN <= TC_RETARDO_SCS_CN_MAX:
            raise DatoInvalidoError(
                "CN", valor=fila.get("CN"), id_punto=id_,
                motivo="el numero de curva no pasa de "
                       f"{TC_RETARDO_SCS_CN_MAX} ({donde})")
        cuencas[id_] = Cuenca(
            id=id_,
            area_km2=_numero(fila, "area_km2", donde, id_punto=id_),
            L_cauce_m=_numero(fila, "L_cauce_m", donde, id_punto=id_),
            S_cauce_cuenca=_numero(fila, "S_cauce_cuenca", donde,
                                   techo=S_CAUCE_MAX, id_punto=id_),
            cobertura=cobertura, suelo=suelo,
            estacion=_texto(fila, "estacion", donde), metodo_tc=metodo,
            S_terreno=_numero(fila, "S_terreno", donde, techo=S_CAUCE_MAX,
                              id_punto=id_),
            H_desnivel_m=_numero(fila, "H_desnivel_m", donde, opcional=True,
                                 id_punto=id_),
            ajuste_kirpich=ajuste, CN=CN, origen=donde,
            c_retardo_izzard=de_superficie["c_retardo_izzard"],
            n_manning_superficial=de_superficie["n_manning_superficial"])
    return cuencas


def cargar_estacion(ruta: Any, *,
                    datos: Optional[bytes] = None) -> Dict[str, SerieDeEstacion]:
    """
    Lee el CSV de la estacion (--estacion): una fila por año, con las
    columnas `estacion`, `anio`, `p24_mm` y `fen`. Un archivo puede traer
    varias estaciones. La columna `fen` es OBLIGATORIA y cada celda dice si
    ese año fue del fenomeno El Niño, «si» o «no»: es la declaracion que la
    Fase 1-bis pide de la serie. Una celda VACIA no es un «no» --seria
    rellenar el hecho que el archivo tiene que declarar-- y detiene la carga.
    Un `p24_mm` de 0 es un dato y se admite.

    `datos` (UI-1): los bytes del archivo ya leidos; sin ellos se lee `ruta`.
    """
    ruta = Path(ruta)
    por_estacion: Dict[str, List[RegistroDeLluvia]] = {}
    for numero, fila in _filas(ruta, COLUMNAS_ESTACION, datos=datos):
        donde = f"'{ruta.name}', linea {numero}"
        estacion = _texto(fila, "estacion", donde)
        bruto_anio = _texto(fila, "anio", donde)
        try:
            anio = int(bruto_anio)
        except ValueError:
            raise DatoInvalidoError("anio", valor=bruto_anio,
                                    motivo=f"no es un año entero ({donde})") from None
        marca = fila.get("fen", "").casefold()
        if not marca:
            raise DatoFaltanteError(
                "fen",
                detalle=f"celda vacia en {donde}: cada año de la serie tiene "
                        "que decir si fue del fenomeno El Niño, «si» o «no». "
                        "Una celda vacia no se lee como «no»")
        if marca in FEN_SI:
            fen = True
        elif marca in FEN_NO:
            fen = False
        else:
            raise DatoInvalidoError(
                "fen", valor=fila.get("fen"),
                motivo="la columna fen dice si el año fue del fenomeno El "
                       f"Niño: «si» o «no» ({donde})")
        registros = por_estacion.setdefault(estacion, [])
        if any(r.anio == anio for r in registros):
            raise DatoInvalidoError(
                "anio", valor=anio,
                motivo=f"el año esta dos veces en la serie de «{estacion}» "
                       f"({donde}): un maximo anual por año")
        registros.append(RegistroDeLluvia(
            anio=anio,
            p24_mm=_numero(fila, "p24_mm", donde, admite_cero=True), fen=fen))
    return {estacion: SerieDeEstacion(
                estacion=estacion,
                registros=tuple(sorted(registros, key=lambda r: r.anio)),
                origen=f"'{ruta.name}'")
            for estacion, registros in por_estacion.items()}


def cargar_entrada(ruta_cuencas: Any, ruta_estacion: Any) -> EntradaHidrologica:
    """Las dos entradas de la Fase 1-bis, cargadas y cruzadas."""
    return cruzar_entradas(cargar_cuencas(ruta_cuencas),
                           cargar_estacion(ruta_estacion),
                           ruta_cuencas, ruta_estacion)


def cruzar_entradas(cuencas: Dict[str, Cuenca],
                    estaciones: Dict[str, SerieDeEstacion],
                    ruta_cuencas: Any, ruta_estacion: Any) -> EntradaHidrologica:
    """
    Las dos entradas ya cargadas, CRUZADAS: cada cuenca nombra una estacion
    que el archivo de la estacion trae. Aparte de `cargar_entrada` desde UI-1
    para que `servicio.cargar_hidrologia` lea y parsee cada archivo en el
    MISMO orden de siempre --- cuencas y despues estacion --- con sus bytes
    leidos una sola vez, que son de los que saca la huella. Las rutas son el
    origen que la memoria imprime.
    """
    for cuenca in cuencas.values():
        if cuenca.estacion not in estaciones:
            raise DatoFaltanteError(
                "estacion", id_punto=cuenca.id,
                detalle=f"la cuenca nombra la estacion «{cuenca.estacion}» "
                        f"({cuenca.origen}) y el archivo "
                        f"'{Path(ruta_estacion).name}' trae: "
                        + ", ".join(f"«{e}»" for e in estaciones))
    return EntradaHidrologica(
        cuencas=cuencas, estaciones=estaciones,
        origen_cuencas=str(ruta_cuencas), origen_estacion=str(ruta_estacion))
