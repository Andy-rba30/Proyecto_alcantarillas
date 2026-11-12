"""
src/servicio.py
===============
El SERVICIO DE CALCULO del expediente: la orquestacion que hasta EXT-9 vivia
en `cli.py`, separada de sus adaptadores (JSON, texto y argparse, que siguen
en `cli.py`). Es la fase E01 del plan de evolucion, fundida con E02 y E03 y
apoyada en PC-08 (`src/` como paquete real) y en el contexto de corrida de
EXT-4.

    M0 -> M1 -> MD (M2/M3/M4/M5) -> M6 -> M7 -> M8 -> M9 -> M10

Que vive aqui y que no
----------------------
AQUI: el alcance de la corrida y lo que cada alcance difiere
(`MODULOS_DIFERIDOS_POR_ALCANCE`, `VERIFICACIONES_DIFERIDAS_POR_ALCANCE`), las
familias que usan cada dato externo (`FAMILIAS_QUE_USAN`), la carga de datos
externos (`cargar_datos_externos`, `DatosExternos`, `CLAVES_EXTERNAS`), las
estructuras del informe (`InformePunto`, `InformeCabezal`, `Informe`,
`ResumenDeCorrida`, `DatoDeclarado`), la ejecucion de una etapa (`_etapa`,
`_bloqueo`), las fases (`_fase_2` ... `_fase_10`), el pipeline de un punto y
del proyecto (`correr_punto`, `correr_cabezal`, `correr`) y la foto del estado
con que corrio (`capturar_contexto`).

EN `cli.py`: el volcado a JSON (`informe_json`), el volcado a texto
(`volcar`), la plantilla por alcance, la sesion serializada, `--declarar`, el
`argparse` y `main`. La CLI importa de aqui; este modulo NO importa `cli`,
`gui`, `argparse` ni Tk, y un test lo fija en un proceso limpio: importar y
ejecutar el servicio no inicia la CLI ni la GUI.

Por que se separo
-----------------
Tres consumidores de `src/` --- `anticipo.py` (2 atributos), `ayuda_entrada.py`
(5) e `indice_formulas.py` (2) --- importaban `cli` desde DENTRO de sus
funciones para leer datos de la corrida (que difiere cada alcance, las claves
externas, la corrida de referencia): un modulo de `src/` que importa la capa
de arriba, en diferido para no arrastrar el pipeline al cargar. Con el
servicio en `src/`, los tres importan hacia abajo y sin diferir. Y la
equivalencia por las dos puertas --- las mismas entradas por el servicio y por
`cli.main` dan el mismo informe y el mismo contexto --- esta MEDIDA en
`tests/test_ext9_paquete_servicio.py`, no afirmada.

Lo que `cli.py` conserva como REEXPORTACION son los nombres que `gui/app.py`
lee de `cli` y los privados que la suite lee de `cli` (`_verificador_perfil`,
`_etapa`, `_numero_externo`, `_fase_*`, `_bloqueo`, ...): son el MISMO objeto
que el de aqui, no una copia, y se retiran solo cuando los archivos de tests
que los leen migren al servicio (ficha EXT-9-01 de
`docs/decisiones_diferidas.md`).

Datos que NO estan en el CSV
----------------------------
Las dos clases de clave (magnitudes que no son columna, y columnas que una
familia deja vacias por tablero), con lo que cada una significa, estan en el
docstring de `cli.py`, que es donde el proyectista las lee al pedir `--help`;
la lista que no envejece es `CLAVES_EXTERNAS`, de aqui.

Que hace con un criterio pendiente
----------------------------------
Lo registra como bloqueo de la etapa donde salto --- con clave, concepto y
fuente ---, sigue con las etapas que no dependen de el, y el informe los
agrupa aparte (Sec. 0.7). Nunca sustituye por un defecto ni convierte el
vacio en un incumplimiento. Solo se atrapa `ErrorProyecto`: un fallo de
programa se propaga con su traza.
"""

from __future__ import annotations

import copy
import json
import math
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src import declaracion as _declaracion
from src.constantes_normativas import (CUANTIA_MIN_MURO,
                                       H_O_HW_SOBRE_D_MIN,
                                       NIVELES_DE_ABRASION, RECUBRIMIENTO)
from src.dominios import (ALTURA_RECEPTOR_MAX_FISICA_M, N_MANNING_MAX_FISICO,
                          PH_MAX_FISICO, PPM_MAX_FISICO, S_CAUCE_MAX)
from src.modelos import ALCANCE_EXPEDIENTE as _ALCANCE_EXPEDIENTE
from src.modelos import ALCANCE_PERFIL as _ALCANCE_PERFIL
from src.modelos import (Bloqueo, CaudalDeDiseno, Clasificacion,
                         CompatibilidadGeometrica,
                         ContextoCorrida, CriterioPendienteError, DatoEfectivoDeSitio,
                         EntradaHidrologica,
                         DatoFaltanteError, DatoInvalidoError,
                         DictamenDurabilidad,
                         DisenoNoFactibleError, ENSAYOS_DE_DURABILIDAD,
                         EnsayosDurabilidad, ErrorProyecto, Espaciamiento,
                         Familia, MetodoNoEvaluableError, PasoDiseno,
                         ProteccionSalida, PuntoCritico, ResultadoPunto,
                         AVISO_SIN_ACCESO_DE_MANTENIMIENTO, SeccionReceptor,
                         TipoDeBloqueo, TWDeterminado, Verificacion)
from src.modelos import EstadoDeVerificacion, TipoDeVeredicto
from src.modulos.M0_carga import (COLUMNA_CAUDAL,
                                  FAMILIAS_CON_CAUDAL_HIDROLOGICO,
                                  cargar_puntos, cargar_puntos_de_bytes,
                                  leer_bytes)
# --- T-1 --- La Fase 1-bis. Este es el UNICO modulo que importa
# `MH_hidrologia`: el caudal calculado entra al pipeline como `Q_m3s` del
# punto de calculo, igual que el declarado, y ningun modulo de M1 a M11 sabe
# de cual de los dos se trata salvo por `InformePunto.caudal`.
from src.modulos import MH_hidrologia as MH
from src.modulos.M1_clasificacion import clasificar, exigir_alcance
from src.modulos.M2_material import matriz_durabilidad
from src.modulos.M6_proteccion import proteccion_salida
from src.modulos import M3_hidraulica as M3
from src.modulos.M7_geometria import (compatibilidad_geometrica,
                                      cota_salida, longitud_conducto)
# `altura_relleno_sobre_clave` vive en M5 y no aqui: la comparten V7 -- que
# pesa ese relleno como EV -- y la Fase 8, que con el entra a la norma de
# producto. La resta estaba escrita en los dos sitios y la copia de la CLI
# iba SIN la guarda de cotas incoherentes (SIS-A-21). Es el mismo defecto de
# `cota_clave` (MAT-D4), que por eso tambien vive en M5.
from src.modulos.M5_verificaciones import altura_relleno_sobre_clave
from src.modulos.M8_estructural import (cama_apoyo_relleno_lateral,
                                        seleccionar_clase_calibre)
from src.modulos.M9_cabezal import (aviso_ambiente_corrosivo,
                                    nota_excepcion_refuerzo_minimo,
                                    cadena_sismica,
                                    condicion_normativa_cabezal,
                                    cuantia_minima, geometria_adoptada,
                                    k_ae_del_proyecto,
                                    recubrimiento_de_diseno)
from src.modulos.M10_espaciamiento import espaciamiento_alivio
# De M11 solo las dos huellas y la ruta del archivo de criterios, para
# `capturar_contexto`: la agregacion de bloqueantes y la memoria son de la
# Fase 11 y las consumen los adaptadores, no el servicio.
from src.modulos.M11_reporte import (ARCHIVO_CRITERIOS, sha1_archivo,
                                     sha1_de_bytes)
from src.modulos import M5_verificaciones as M5
from src.modulos.MD import disenar_punto

# Alcance de la corrida. Es una bifurcacion declarada, no una poda: con
# "expediente" (el defecto) todo corre exactamente como siempre; con "perfil"
# V5 y V8 se INTENTAN pero su fallo se difiere al expediente en vez de frenar
# el dimensionamiento, y las Fases 8 y 9 no se ejecutan. Nada de lo diferido
# se pierde: queda registrado como Bloqueo con `diferido_por_alcance=True`,
# se imprime con su fundamento, y deja de contar solo para `Informe.cerrado`.
# Son rotulos de la corrida, no valores de proyecto.
#
# SE IMPORTAN DE `modelos.py` DESDE S18, donde se mudaron: M11 los necesita
# para decidir que va dentro del bloque de pendientes y no puede importar esta
# CLI. Los nombres siguen expuestos aqui para todo lo que ya los lee de
# `cli.ALCANCE_*` --- la GUI y los tests --- y son el MISMO objeto, no una
# copia.
ALCANCE_PERFIL = _ALCANCE_PERFIL
ALCANCE_EXPEDIENTE = _ALCANCE_EXPEDIENTE

# LOS MODULOS QUE CADA ALCANCE NO EJECUTA, como dato y no como prosa.
#
# Existe porque hay tres sitios que necesitan la MISMA respuesta y la
# necesitan por separado: `correr_punto` (que salta la Fase 8), `correr` (que
# salta la Fase 9) y `tests/test_nivel_medido.py`, que clasifica por esta via
# lo unico que ninguna corrida puede medir --- un criterio que ninguna de las
# dos llega a invocar porque su cadena se detiene antes en un pendiente ---.
# Tres `if` escritos aparte son tres sitios donde la respuesta puede divergir;
# este diccionario es uno solo, y es el que los dos `if` consultan, de modo
# que no puede quedarse describiendo un salto que el codigo ya no hace.
#
# LO QUE DIFIERE ES EL MODULO ENTERO, y por eso la clave es el nombre del
# modulo y no el de la fase: `variables_entrada` responde en modulos --- su
# `consumido_por` --- y traducir de fase a modulo en el punto de uso seria una
# segunda tabla. V5 y V8 NO estan aqui: no son modulos que se salten, son dos
# verificaciones que se INTENTAN igual y cuyo fallo se difiere
# (`_verificador_perfil`), de modo que sus criterios siguen siendo alcanzables
# a perfil. Esa pareja tiene su propio dato, justo debajo.
MODULOS_DIFERIDOS_POR_ALCANCE: Dict[str, Tuple[str, ...]] = {
    ALCANCE_EXPEDIENTE: (),
    ALCANCE_PERFIL: ("M8_estructural", "M9_cabezal"),
}

# LAS VERIFICACIONES QUE CADA ALCANCE DIFIERE, como dato y no como prosa.
#
# Es la otra mitad del diccionario de arriba, y la distincion ya estaba
# escrita alli: V5 y V8 no son modulos que se salten, son verificaciones que
# se INTENTAN igual y cuyo fallo se difiere al expediente. Hasta G3 la pareja
# solo existia como literales dentro de `_verificador_perfil`, y el anticipo
# de la pestana 1 --- que tiene que decir QUE difiere el alcance elegido sin
# escribir la lista a mano --- no tenia de donde leerla.
#
# Y NO ES UNA TABLA PARALELA, por la misma defensa que la de los modulos:
# `_verificador_perfil` CONSULTA esta tupla en sus dos puntos de
# diferimiento, de modo que no puede quedarse describiendo un diferimiento
# que el codigo ya no hace --- quitar "V8" de aqui haria que su fallo volviera
# a subir como en el alcance de expediente.
VERIFICACIONES_DIFERIDAS_POR_ALCANCE: Dict[str, Tuple[str, ...]] = {
    ALCANCE_EXPEDIENTE: (),
    ALCANCE_PERFIL: ("V5", "V8"),
}

# EN QUE ALCANCE UN «METODO NO EVALUABLE» SE DIFIERE (EXT-3; v8 §4.3
# enmendada en EXT-0). No es una tercera tabla de verificaciones: V1 y V2 no
# se difieren SIEMPRE --por eso no estan en la tupla de arriba, que el
# anticipo de la pestana 1 lee como «lo que el alcance aparta»--, sino solo
# cuando el barril va parcialmente lleno bajo control de salida, y la carga
# HW solo cuando el control de salida gobierna con HW/D < 0.75. Lo que este
# dato decide es que hace la corrida con ese `MetodoNoEvaluableError`: a nivel
# de perfil lo registra como bloqueo diferido y el punto sigue dimensionandose
# con HW no evaluable; a nivel de expediente es un bloqueo que impide cerrar,
# hasta que exista el calculo de remanso (Section 3.5) que la fuente manda.
# Lo consultan `_verificador_perfil` (V1/V2) y `_compuerta_metodo_h_o` (HW).
ALCANCES_QUE_DIFIEREN_METODO_NO_EVALUABLE: Tuple[str, ...] = (ALCANCE_PERFIL,)


def _difiere(alcance: str, modulo: str) -> bool:
    """Si esta corrida NO ejecuta ese modulo de calculo."""
    return modulo in MODULOS_DIFERIDOS_POR_ALCANCE[alcance]


# LAS FAMILIAS PARA LAS QUE CADA DATO DECLARADO CAMBIA ALGO.
#
# Los datos de `CLAVES_EXTERNAS` no son columna del CSV y la ventana los pide
# todos a la vez, sin decir que dos de ellos solo sirven para una familia. Esa
# distincion EXISTIA y estaba escrita como PROSA en el tooltip de la GUI
# ("Solo aplica a Familia B (Fase 10)"), que es la peor forma de tenerla: el
# programa no la puede leer, de modo que quien llena un expediente sin puntos
# de Familia B ve un campo que no le va a servir para nada y no tiene como
# saberlo. Aqui es dato, y con eso la pestana 1 lo puede ANOTAR.
#
# LO QUE NO ESTA AQUI SE USA EN LAS TRES. Solo se declara la excepcion, no la
# regla: `luz_m`, `TW_m` y `longitud_m` gobiernan el dimensionamiento de
# cualquier cruce.
#
# Y NO ES UNA TABLA PARALELA, que es lo que la haria inaceptable: la fila de
# `L_hidraulico_m` es la que `_fase_10` CONSULTA para decidir si esa fase
# corre, de modo que no puede quedarse describiendo una condicion que el
# codigo ya no aplica. La de `categoria_tr` no tiene esa suerte --- vive en
# `M1.periodo_retorno_de`, que esta CLI no gobierna ---, y por eso su unica
# defensa es la medida: `tests/test_familias_del_csv.py` corre el pipeline
# familia por familia y comprueba que declarar el dato no mueve nada en las
# que aqui no figuran.
#
# ANOTAR NO ES DESHABILITAR, y es deliberado: el proyectista puede estar
# preparando el dato de un punto que todavia no ha metido en el CSV.
FAMILIAS_QUE_USAN: Dict[str, Tuple[Familia, ...]] = {
    # La Fase 10 (espaciamiento de alivio, Sec. 10) es de la Familia B y de
    # ninguna otra: `_fase_10` lee esta fila.
    "L_hidraulico_m": (Familia.B,),
    # La fila de la Tabla N 02. AQUI HABIA UNA `(Familia.A,)` Y LA MEDIDA LA
    # CORRIGIO, que es justamente para lo que esta la medida:
    #
    #   Familia A   la elige, y sin declaracion cae en el criterio
    #               'umbral_area_quebrada_importante_ha'.
    #   Familia B   la tiene FIJA por Sec. 2.3 (descarga de cunetas ->
    #               quebrada menor), y aun asi NO es inerte: declararla
    #               cambia el FUNDAMENTO que la memoria imprime --- pasa de
    #               atribuir la fila a la Sec. 2.3 a atribuirsela al
    #               proyectista --- y declarar una fila distinta de la fija es
    #               `DatoInvalidoError`. El TR no se mueve; lo que la memoria
    #               dice, si. Eso es aplicar.
    #   Familia C   no tiene TR --- su caudal es el de diseño del canal ---, y
    #               la declaracion no se llega a mirar. Es la unica en la que
    #               este campo no aplica.
    #
    # La diferencia de la B no se dedujo leyendo M1: la encontro
    # `tests/test_familias_del_csv.py` comparando los dos volcados.
    "categoria_tr": (Familia.A, Familia.B),
}


# LO QUE EL PRE-VUELO DE DATOS LEE DE AQUI (PF-2), declarado UNA vez y en el
# sitio donde se aplica, para que `anticipo.datos_faltantes_por_punto` no lo
# escriba a mano:
#
#   * los textos con que `_fase_2` y `_fase_10` registran la falta de `luz_m`
#     y de `L_hidraulico_m` (etapa y detalle), que el pre-vuelo imprime tal
#     cual porque son los mismos que el Bloqueo llevara;
#   * las columnas admitidas vacias por M0 que una verificacion exige SOLO en
#     una familia: `cota_coronacion_canal` la exige VC1 (Familia C, Sec. 2.3)
#     y en las otras dos la celda vacia no detiene nada. Es un dato del
#     programa como FAMILIAS_QUE_USAN, y como aquel se contrasta por medida
#     (tests/test_pf2_prevuelo.py, la union contra la corrida real);
#   * las dos columnas que son VIAS del TW de Sec. 1.3 (`_resolver_tw`):
#     vacias no detienen nada por si solas, porque el TW tiene otras vias y
#     una ultima puerta (`TW_receptor`); `tw_sin_via_de_sec_1_3` es el
#     predicado que el resolvedor y el pre-vuelo comparten.
ETAPA_FALTA_LUZ = "umbral de luz (Sec. 2.1)"
DETALLE_FALTA_LUZ = ("no es columna de Sec. 1.2: declararla con --luz o en "
                     "--datos-externos. Sin ella no se puede separar "
                     "alcantarilla de puente y el punto no se dimensiona")
ETAPA_FALTA_L_HIDRAULICO = "espaciamiento maximo entre alivios"
DETALLE_FALTA_L_HIDRAULICO = ("Sec. 10 describe el procedimiento de la cuneta "
                              "pero no fija su seccion, su n de Manning ni la "
                              "formula de intensidad: la longitud por capacidad "
                              "hidraulica se declara, no se deduce")
FAMILIAS_QUE_EXIGEN_COLUMNA: Dict[str, Tuple[Familia, ...]] = {
    "cota_coronacion_canal": (Familia.C,),
    # `area_ha` la EXIGE unicamente `M1._categoria_por_area`, alcanzable solo
    # en la Familia A sin `categoria_tr` declarada (Sec. 2.2): la B tiene la
    # fila fija de Sec. 2.3 y la C no tiene TR (lo midio el auditor
    # adversarial de PF-2 sobre `periodo_retorno_de`). M0 solo la admite vacia
    # en C, y ahi vacia no detiene nada; en A y B es obligatoria y el gate no
    # se consulta. Desde T-1 la LEE ademas `_fase_hidrologia`, en A y en B,
    # para el contraste de caudal especifico Q/A del caudal declarado; no la
    # exige: sin area ese paso no se emite y nada se detiene.
    "area_ha": (Familia.A,),
}
COLUMNAS_DEL_TW: Tuple[str, ...] = ("cota_TW", "Q_receptor_m3s")
# Las claves externas que NO son columna y que el codigo resuelve por otra
# via cuando faltan --- y por eso el pre-vuelo no las lista como faltas ---:
# `longitud_m` la calcula 7.B (`_resolver_longitud`), `categoria_tr` cae en
# el criterio de la Tabla N 02 o en la fila fija de Sec. 2.3 (M1), y
# `S_conducto` cae en `S_cauce` (`disenar_punto`, `_resolver_tw`). Lo que
# queda de `CLAVES_EXTERNAS` sin columna --- luz_m, TW_m, L_hidraulico_m ---
# tiene su regla explicita en el pre-vuelo, y el test de PF-2 fija que la
# particion sea exacta: una clave nueva sin regla ni via alterna no pasa.
EXTERNOS_CON_VIA_ALTERNA: Tuple[str, ...] = (
    "longitud_m", "categoria_tr", "S_conducto",
    # --- T-2 --- Las dos claves que T-2 abre son OPCIONALES y ninguna falta
    # detiene nada: sin la seccion medida del receptor rige la adoptada del
    # criterio 'seccion_receptor' (y la memoria lo avisa), y sin la
    # declaracion del acceso de mantenimiento el punto se calcula igual.
    "seccion_receptor_medida", "acceso_mantenimiento_previsto")


def tw_sin_via_de_sec_1_3(tw_declarado: Optional[float], cota_TW: Optional[float],
                          Q_receptor: Optional[float],
                          hay_seccion_medida: bool = False) -> bool:
    """
    True cuando ninguna de las vias de Sec. 1.3 es recorrible con lo que hay
    --- ni TW declarado, ni `cota_TW`, ni Manning en el receptor (que exige
    `Q_receptor_m3s` y el criterio `seccion_receptor` declarado) --- y el TW
    cae en la ultima puerta, el criterio 'TW_receptor'. Lo lee `_resolver_tw`
    para decidir si consulta ese criterio, y el pre-vuelo (PF-2) para decir
    que el punto caera ahi sin correr nada.
    """
    # --- T-2 --- Con la seccion MEDIDA del receptor (`seccion_receptor_
    # medida` de --datos-externos) la via 4 se recorre aunque el criterio
    # 'seccion_receptor' este vacio: la medida gana y el criterio no se lee.
    return (tw_declarado is None and cota_TW is None and Q_receptor is None
            and not hay_seccion_medida
            and ca.valor_si_declarado(CRITERIO_SECCION_RECEPTOR) is None)


def familias_que_usan(clave: str) -> Tuple[Familia, ...]:
    """
    Las familias para las que declarar ese dato cambia algo. Sin fila
    declarada, las tres: la excepcion se declara, la regla no.
    """
    return FAMILIAS_QUE_USAN.get(clave, tuple(Familia))


def familias_del_csv(ruta_csv: Path) -> Tuple[Familia, ...]:
    """
    Las familias que el CSV trae, en el orden de Sec. 2.3.

    Es lo que la pestana 1 necesita para anotar los campos que no aplican y lo
    que la pestana 2 necesitaria para un filtro por familia. Sale de
    `cargar_puntos` --- la MISMA carga que corre el pipeline --- y no de una
    lectura propia del archivo: dos lectores del mismo CSV son dos
    validaciones que pueden discrepar, y la ventana acabaria anotando sobre
    una familia que M0 rechaza.
    """
    familias = {punto.familia for punto in cargar_puntos(ruta_csv)}
    return tuple(f for f in Familia if f in familias)


def puntos_por_familia(ruta_csv: Path) -> Dict[Familia, int]:
    """
    Cuantos puntos de cada familia trae el CSV, las tres familias siempre
    (con 0 para la que el archivo no trae).

    Es lo que la pestana 1 necesita para encabezar cada seccion de familia
    con su conteo. No es una poblacion nueva: es el tamano de la que
    `familias_del_csv` ya recorre, y sale de la MISMA carga
    (`cargar_puntos`) por la misma razon escrita alli --- dos lectores del
    mismo CSV son dos validaciones que pueden discrepar.
    """
    puntos = cargar_puntos(ruta_csv)
    return {familia: sum(1 for punto in puntos if punto.familia is familia)
            for familia in Familia}

# Etiquetas de fase. Son rotulos del informe, no valores de proyecto: cada uno
# nombra el modulo y la seccion de la hoja de ruta que ejecuta esa etapa.
FASE_CARGA = "Fase 1 - Carga y validacion (M0)"
FASE_CLASIFICACION = "Fase 2 - Clasificacion y TR (M1)"
FASE_HIDROLOGIA = "Fase 1-bis - Hidrologia: caudal de diseno (MH)"
ETAPA_CAUDAL_CALCULADO = "caudal de diseno por el metodo racional"
ETAPA_AREA_DE_LA_CUENCA = "area de la cuenca (area_ha frente a area_km2)"
ORIGEN_Q_DE_COLUMNA = "CSV Sec. 1.2, columna Q_m3s"
FASE_DISENO = "Fases 3-5 - Diseno hidraulico (MD: M2/M3/M4/M5)"
FASE_PROTECCION = "Fase 6 - Proteccion de salida (M6)"
FASE_GEOMETRIA = "Fase 7 - Compatibilidad geometrica (M7)"
FASE_ESTRUCTURAL = "Fase 8 - Estructural del conducto (M8)"
FASE_CABEZAL = "Fase 9 - Cabezal y aletas (M9)"
FASE_ALIVIO = "Fase 10 - Espaciamiento de alivio (M10)"

CRITERIO_TW = "TW_receptor"
# La seccion del receptor, que el paso 2 de Sec. 1.3 necesita.
CRITERIO_SECCION_RECEPTOR = "seccion_receptor"

# Claves admitidas en --datos-externos: los datos de entrada que una corrida
# puede declarar sin tocar el CSV. NO son «las que Sec. 1.2 no trae como
# columna» -- esa frase estuvo aqui hasta que la auditoria de C6 la encontro
# sobreviviendo al docstring que la retiro --: `Q_m3s` y `S_cauce` SI son
# columnas, y entran por aqui porque una familia las deja vacias por tablero.
# Las dos clases estan en el docstring del modulo. Las de texto van aparte
# porque no se validan como numero.
CLAVES_TEXTO: Tuple[str, ...] = ("categoria_tr",)
# --- T-2 --- (cadena T, 2026-11-11). DOS CLAVES NUEVAS, y ninguna es un
# numero suelto, de modo que cada una va en su clase y se valida por ella:
#
#   seccion_receptor_medida        (INF-3.2.8) la seccion LEVANTADA del
#       receptor, como objeto con los MISMOS cinco campos del criterio
#       'seccion_receptor' -- b_m, z_HV, S, n, altura_total_m --. Es entrada
#       del proyecto (topografia / ANA / Junta; el script de QGIS del
#       proyecto la puede exportar): opcional, sin valor por defecto, y
#       cuando viene GANA sobre el criterio adoptado en las vias 3 y 4 del
#       TW. Un objeto y no cinco claves porque media seccion no es una
#       seccion: los cinco campos entran juntos o no entra ninguno.
#   acceso_mantenimiento_previsto  (INF-0.5) booleano por punto: si los
#       planos preven el acceso de limpieza que el num. 4.1.1.3.7 d) del
#       Manual exige. Opcional; no decide ningun calculo: se imprime, y
#       `false` dispara un aviso.
CLAVE_SECCION_RECEPTOR_MEDIDA = "seccion_receptor_medida"
CLAVE_ACCESO_MANTENIMIENTO = "acceso_mantenimiento_previsto"
CLAVES_OBJETO: Tuple[str, ...] = (CLAVE_SECCION_RECEPTOR_MEDIDA,)
CLAVES_BOOLEANAS: Tuple[str, ...] = (CLAVE_ACCESO_MANTENIMIENTO,)
CAMPOS_SECCION_RECEPTOR: Tuple[str, ...] = ("b_m", "z_HV", "S", "n",
                                            "altura_total_m")
# Las claves numericas que admiten el CERO como dato, cada una con su
# significado: TW = 0 es salida libre y, desde T-2, S_conducto = 0 es un
# barril horizontal (INF-5.1.6; HDS-5 num. 3.3.4).
CLAVES_QUE_ADMITEN_CERO: Tuple[str, ...] = ("TW_m", "S_conducto")
CLAVES_EXTERNAS: Tuple[str, ...] = (("luz_m", "TW_m", "longitud_m", "Q_m3s",
                                     "S_conducto", "S_cauce",
                                     "L_hidraulico_m") + CLAVES_TEXTO
                                    + CLAVES_OBJETO + CLAVES_BOOLEANAS)

# --- T-4 --- LOS ENSAYOS DE DURABILIDAD (Sec. 3.3; INF-3.3.1).
#
# Entran por el MISMO archivo de `--datos-externos`, en las mismas dos
# secciones --`globales` para el sitio entero, `puntos` para una calicata--,
# y NO son claves de `CLAVES_EXTERNAS`. La separacion es deliberada y tiene
# consecuencia: toda clave de `CLAVES_EXTERNAS` es un dato que ALGUNA ETAPA
# EXIGE --su ausencia detiene o espera, y con esa lectura la consumen el
# pre-vuelo (`anticipo.datos_faltantes_por_punto`), la ayuda de entrada y la
# pestana 1--; un ensayo de durabilidad es OPCIONAL, sin valor por defecto, y
# su ausencia no detiene nada: la matriz no actua y la memoria lo dice
# (`modelos.DURABILIDAD_SIN_ENSAYOS`). Metidos en la tupla de arriba, el
# pre-vuelo los habria anunciado como seis faltas por punto.
#
# Son datos [S] del EMS y del estudio de campo (docs/contrato_entradas.md):
# el programa no los supone, no los interpola entre puntos y no los deduce
# --el nivel de abrasion, en particular, NO se deduce de la velocidad--.
# Los nombres son los de `modelos.ENSAYOS_DE_DURABILIDAD`, la misma tupla
# que arma `EnsayosDurabilidad`: no hay segunda lista.
CLAVES_DE_DURABILIDAD: Tuple[str, ...] = ENSAYOS_DE_DURABILIDAD
CLAVES_DE_DURABILIDAD_TEXTO: Tuple[str, ...] = ("abrasion",)
# Las que admiten el cero exacto: «no se detecto» es un resultado de ensayo
# legitimo en una concentracion. El pH y la resistividad no lo admiten.
CLAVES_DE_DURABILIDAD_CON_CERO: Tuple[str, ...] = (
    "sulfatos_suelo_ppm", "sulfatos_agua_ppm", "cloruros_ppm")
ETAPA_DURABILIDAD = "matriz de durabilidad (Sec. 3.3)"

# La geometria del cabezal es del proyecto entero, no de un punto: Sec. 9 no
# dimensiona un cabezal por punto y el criterio que la declara es uno solo.
NOTA_ESTABILIDAD_CABEZAL = (
    "Las verificaciones de estabilidad de Fase 9 no las ensambla esta CLI: "
    "M9.verificar_estabilidad devuelve E1-E3 (y E4-E5 si se le piden) a "
    "partir de las demandas YA calculadas, y E6 -- la ubicacion de la "
    "resultante en la base bajo sismo, que el Manual de Puentes exige y "
    "E.050 no escribe -- es funcion suelta, "
    "M9.verificar_excentricidad_sismica, porque no es un factor de seguridad "
    "y no cabe en la tabla de Sec. 9.3. Elegir el plano de empuje o los factores "
    "de combinacion aqui seria decidir por el proyectista. La CLI corre las "
    "piezas de Fase 9 que se sostienen solas: cadena sismica (9.2), K_AE, "
    "recubrimientos (9.4) y cuantias minimas de referencia. Que funciones de "
    "M9 quedan sin llamador de produccion, y por que cada una, se declara en "
    "UN SOLO SITIO -- M9.FUNCIONES_SIN_CONSUMIDOR -- y esta CLI lo lee de "
    "alli en vez de repetirlo."
)



# ===========================================================================
# Como el informe ESCRIBE una magnitud
# ===========================================================================
# `_fmt` y `DECIMALES_FACTOR` vivian en la CLI como formato del volcado a
# consola. Se mudaron con el servicio (EXT-9) porque no solo formatean el
# volcado: escriben los MENSAJES de dos bloqueos que forman parte del informe
# --- el «metodo no evaluable» de la carga HW (`_compuerta_metodo_h_o`) y el
# valor rechazado que `_valor_descartado` devuelve al remitente --- y esos
# textos viajan al JSON y a la memoria por cualquiera de las dos puertas. El
# volcado de texto de `cli.py` los sigue usando, importados de aqui.
DECIMALES_FACTOR = 2            # decimales con que se escribe un cociente HW/D


def _fmt(valor: Any, decimales: int = 3) -> str:   # literal-ok: decimales con que el informe escribe una magnitud
    """Un numero con decimales fijos; cualquier otra cosa, tal como viene."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return str(valor)
    if isinstance(valor, float) and not math.isfinite(valor):
        return repr(valor)
    return f"{float(valor):.{decimales}f}"



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
    if clave in CLAVES_DE_DURABILIDAD:
        return _dato_de_durabilidad(clave, bruto, origen)
    if clave in CLAVES_TEXTO:
        if not isinstance(bruto, str) or not bruto.strip():
            raise DatoInvalidoError(
                clave, valor=bruto,
                motivo=f"tiene que ser texto no vacio; origen: {origen}")
        return DatoDeclarado(nombre=clave, valor=bruto.strip(), origen=origen)
    if clave in CLAVES_BOOLEANAS:
        return _booleano_externo(clave, bruto, origen)
    if clave == CLAVE_SECCION_RECEPTOR_MEDIDA:
        return _seccion_receptor_externa(bruto, origen)
    return _numero_externo(clave, bruto, origen)


def _booleano_externo(clave: str, bruto: Any, origen: str) -> DatoDeclarado:
    """
    --- T-2 --- Un dato externo booleano es `true` o `false` del JSON, y nada
    mas: ni 0/1, ni "si"/"no". Es la contracara de PC-33 (un booleano no es
    un numero): un numero tampoco es un booleano, y `"acceso_mantenimiento_
    previsto": 0` no dice si el acceso esta previsto o si alguien dejo un
    cero de relleno.
    """
    if not isinstance(bruto, bool):
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"tiene que ser un booleano del JSON (true o false), no "
                   f"{type(bruto).__name__}; origen: {origen}")
    return DatoDeclarado(nombre=clave, valor=bruto, origen=origen)


def _seccion_receptor_externa(bruto: Any, origen: str) -> DatoDeclarado:
    """
    --- T-2 --- (INF-3.2.8) La seccion MEDIDA del receptor, validada campo a
    campo: es entrada del proyecto y entra completa o no entra.

    Los cinco campos son los del criterio 'seccion_receptor' y de
    `modelos.SeccionReceptor`, con los mismos nombres y unidades, para que
    quien pase de la seccion adoptada a la levantada no tenga que traducir
    nada: `b_m` (ancho de fondo, m), `z_HV` (talud, H:V), `altura_total_m`
    (profundidad del fondo a la corona, m), `n` (Manning del receptor) y `S`
    (pendiente del receptor, m/m). El dominio es el FISICO, no una banda de
    practica: una medicion no se acota con la ventana de una adopcion.
    """
    clave = CLAVE_SECCION_RECEPTOR_MEDIDA
    if not isinstance(bruto, dict):
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"tiene que ser un objeto con los cinco campos de la "
                   f"seccion ({', '.join(CAMPOS_SECCION_RECEPTOR)}); "
                   f"origen: {origen}")
    faltan = [c for c in CAMPOS_SECCION_RECEPTOR if c not in bruto]
    sobran = [c for c in bruto if c not in CAMPOS_SECCION_RECEPTOR]
    if faltan or sobran:
        raise DatoInvalidoError(
            clave, valor=sorted(bruto),
            motivo=f"la seccion medida lleva exactamente los campos "
                   f"{', '.join(CAMPOS_SECCION_RECEPTOR)}: "
                   + (f"faltan {faltan}" if faltan else "")
                   + ("; " if faltan and sobran else "")
                   + (f"sobran {sobran}" if sobran else "")
                   + f". Media seccion no es una seccion; origen: {origen}")
    valores: Dict[str, float] = {}
    for campo in CAMPOS_SECCION_RECEPTOR:
        crudo = bruto[campo]
        if isinstance(crudo, bool) or not isinstance(crudo, (int, float)) \
                or not math.isfinite(crudo):
            raise DatoInvalidoError(
                f"{clave}.{campo}", valor=crudo,
                motivo=f"no es un numero finito (SI); origen: {origen}")
        valores[campo] = float(crudo)
    # b_m y z_HV admiten el cero por separado (cuneta triangular, canal
    # rectangular) y no los dos a la vez: eso no es una seccion, es una linea.
    for campo in ("b_m", "z_HV"):
        if not valores[campo] >= 0:
            raise DatoInvalidoError(
                f"{clave}.{campo}", valor=valores[campo],
                motivo=f"no puede ser negativo; origen: {origen}")
    if not valores["b_m"] + valores["z_HV"] > 0:
        raise DatoInvalidoError(
            clave, valor=(valores["b_m"], valores["z_HV"]),
            motivo=f"con ancho de fondo 0 y talud 0 a la vez no hay seccion: "
                   f"es una linea; origen: {origen}")
    for campo in ("S", "n", "altura_total_m"):
        if not valores[campo] > 0:
            raise DatoInvalidoError(
                f"{clave}.{campo}", valor=valores[campo],
                motivo=f"tiene que ser positivo; origen: {origen}")
    if not valores["S"] < S_CAUCE_MAX:
        raise DatoInvalidoError(
            f"{clave}.S", valor=valores["S"],
            motivo=f"fuera del rango fisico posible ({S_CAUCE_MAX}): una "
                   f"pendiente en m/m; un valor >= 1 delata una celda en "
                   f"PORCENTAJE; origen: {origen}")
    # Los otros dos techos de dominio (`dominios.py`): lo que el dato puede
    # ser, no lo que conviene que sea.
    if not valores["n"] < N_MANNING_MAX_FISICO:
        raise DatoInvalidoError(
            f"{clave}.n", valor=valores["n"],
            motivo=f"fuera del rango fisico posible ({N_MANNING_MAX_FISICO}): "
                   f"un n de Manning >= 1 delata otra magnitud en la celda "
                   f"(el coeficiente de Strickler, K = 1/n); origen: {origen}")
    if not valores["altura_total_m"] < ALTURA_RECEPTOR_MAX_FISICA_M:
        raise DatoInvalidoError(
            f"{clave}.altura_total_m", valor=valores["altura_total_m"],
            motivo=f"fuera del rango fisico posible "
                   f"({ALTURA_RECEPTOR_MAX_FISICA_M} m): una profundidad asi "
                   f"delata una celda en CENTIMETROS; origen: {origen}")
    return DatoDeclarado(nombre=clave, valor=valores, origen=origen)


def _dato_de_durabilidad(clave: str, bruto: Any, origen: str) -> DatoDeclarado:
    """
    Valida un ensayo de durabilidad declarado (T-4). Es entrada de usuario y
    se rechaza en la puerta, con la misma forma que `_numero_externo`:

      * `abrasion` es TEXTO y tiene que ser uno de los cuatro niveles de la
        Table 8-4 de WSDOT (`constantes_normativas.NIVELES_DE_ABRASION`). M2
        lo vuelve a comprobar: esta es la primera linea, no la unica;
      * los demas son numeros finitos, nunca booleanos, y no negativos. Las
        tres concentraciones admiten el cero exacto; el pH y la resistividad
        no, y el pH tiene ademas el techo fisico de `dominios.PH_MAX_FISICO`.

    LAS CONCENTRACIONES TIENEN EL TECHO DE SU UNIDAD (`PPM_MAX_FISICO`, un
    millon de ppm: el 100 % de la muestra). La resistividad no tiene techo:
    `dominios.py` no lo declara y ponerlo aqui seria inventar un valor.
    """
    if clave in CLAVES_DE_DURABILIDAD_TEXTO:
        if not isinstance(bruto, str) or bruto.strip() not in NIVELES_DE_ABRASION:
            raise DatoInvalidoError(
                clave, valor=bruto,
                motivo="tiene que ser uno de los cuatro niveles de abrasion "
                       "de la Table 8-4 del WSDOT Hydraulics Manual: "
                       + ", ".join(NIVELES_DE_ABRASION)
                       + f"; origen: {origen}")
        return DatoDeclarado(nombre=clave, valor=bruto.strip(), origen=origen)
    if isinstance(bruto, bool):
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"es un booleano ({bruto!r}), no el resultado de un "
                   f"ensayo; origen: {origen}")
    try:
        valor = float(bruto)
    except (TypeError, ValueError):
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"no es un numero; origen: {origen}") from None
    if not math.isfinite(valor):
        raise DatoInvalidoError(
            clave, valor=bruto, motivo=f"no es finito; origen: {origen}")
    admite_cero = clave in CLAVES_DE_DURABILIDAD_CON_CERO
    if valor < 0 or (not admite_cero and not valor > 0):
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=("no puede ser negativo" if admite_cero
                    else "tiene que ser positivo") + f"; origen: {origen}")
    if clave in CLAVES_DE_DURABILIDAD_CON_CERO and valor > PPM_MAX_FISICO:
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"una concentracion en ppm no puede pasar de "
                   f"{PPM_MAX_FISICO} (el 100 % de la muestra); origen: "
                   f"{origen}")
    if clave == "pH" and valor > PH_MAX_FISICO:
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"fuera de la escala de pH (0 a {PH_MAX_FISICO:g}); "
                   f"origen: {origen}")
    return DatoDeclarado(nombre=clave, valor=valor, origen=origen)


def ensayos_de_durabilidad(externos: "DatosExternos",
                           id_punto: str) -> EnsayosDurabilidad:
    """
    Los ensayos de durabilidad que valen para ese punto, cada uno con su
    origen: el del punto pisa al del sitio (`DatosExternos.dato`), y lo que
    nadie declaro queda en None. NUNCA rellena: sin ningun ensayo devuelve un
    `EnsayosDurabilidad` vacio, con el que la matriz no actua.
    """
    valores: Dict[str, Any] = {}
    origenes: List[Tuple[str, str]] = []
    for clave in CLAVES_DE_DURABILIDAD:
        dato = externos.dato(id_punto, clave)
        if dato is not None:
            valores[clave] = dato.valor
            origenes.append((clave, dato.origen))
    return EnsayosDurabilidad(origenes=tuple(origenes), **valores)


# EL DOMINIO FISICO DE UNA CLAVE QUE TAMBIEN ES COLUMNA. Cuando el mismo dato
# puede entrar por dos puertas -- la columna del CSV y la clave de
# `--datos-externos` --, las dos tienen que acotarlo igual: si no, el mismo
# numero es invalido escrito en el CSV y admisible escrito en el JSON, y la
# puerta laxa es justamente la que usan los puntos de Familia C, que traen la
# columna vacia. Lo destapo C6 al abrir `S_cauce`, y estaba MEDIDO:
# `_numero_externo("S_cauce", 6.0)` devolvia el dato tan campante, mientras
# `M0` rechaza ese mismo 6.0 en la columna contra `S_CAUCE_MAX` -- que existe
# precisamente para atrapar «una celda cargada en porcentaje», el error de
# transcripcion mas frecuente de esa columna.
#
# EL MAPA NO SE CUBRE ENTERO, Y AQUI NO SE ESCRIBE CUANTAS ENTRADAS TIENE.
# Este parrafo decia «tiene UNA entrada» y «las otras seis claves no son
# columnas de Sec. 1.2», y las dos mitades caducaron: la primera en el commit
# que anadio `S_conducto` veinte lineas mas abajo, y la segunda contra el
# docstring del modulo, que dice que `Q_m3s` SI es columna. Un conteo escrito
# a mano al lado de la coleccion que cuenta es la forma de comentario que este
# modulo ya vio envejecer tres veces.
#
# Lo que sigue siendo cierto sin numero: hay claves FUERA del mapa, y estan
# fuera porque `dominios.py` no les declara techo. El de `Q_m3s` esta ausente
# A PROPOSITO (ver `modelos.py`: «'Q_m3s' solo exige ser positivo, y ponerle un
# techo...»). La forma de mapa es lo que hace que la proxima clave con dominio
# lo herede en vez de que haya que acordarse.
#
# EL DIAGNOSTICO DE LAS CLAVES QUE QUEDAN FUERA: ANOTADO, NO ABIERTO.
# Se deja escrito para que quien lo retome no tenga que rehacer la derivacion.
# El conjunto SE CALCULA --- `set(CLAVES_EXTERNAS) - set(_DOMINIO_DE_CLAVE)`,
# como en `test_cli` --- y no se escribe aqui: un conteo a mano al lado de la
# coleccion que cuenta es lo que este bloque ya vio envejecer tres veces.
#
#   - `categoria_tr` esta fuera POR CONSTRUCCION: es de `CLAVES_TEXTO` y no
#     pasa por `_numero_externo`. Su juego de valores lo valida M1 contra la
#     Tabla N 02, y repetirlo aqui seria una segunda fuente de verdad (ver el
#     docstring de `_dato_externo`). No es deuda.
#   - `Q_m3s` esta fuera A PROPOSITO y su decision ya esta tomada y escrita:
#     techo ausente --- ponerselo «seria inventar un valor de proyecto»,
#     `modelos.py` --- y guardia en la SALIDA de la aritmetica, con
#     `LimiteNumericoError`. Es el PRECEDENTE con el que se comparan las
#     demas, no un hueco.
#   - `luz_m` SI tiene un umbral normativo --- `LUZ_MAX_ALCANTARILLA`, num.
#     4.1.1.3.1 --- y aun asi NO se copia a este mapa. Conviene decir por que,
#     porque copiarlo parece lo obvio: ese 6.0 CLASIFICA (`>= 6 m` es puente,
#     `M1.denominacion_por_luz`), no invalida. Metido aqui lo atraparia el
#     `valor >= techo` de abajo --- con el MISMO borde --- y un cruce de
#     puente saldria como `DatoInvalidoError` en lugar de salir con su
#     veredicto de fuera de alcance (Sec. 3.1), que es justo el diagnostico
#     que el proyectista necesita. El umbral se queda donde clasifica.
#   - `TW_m` y `L_hidraulico_m`: sin techo en `dominios.py` y sin ninguno que
#     derivar. Inventar uno esta prohibido, de modo que hoy no hay nada que
#     decidir sobre ellas.
#
# Y `longitud_m` ES UN PUNTO DE DECISION, NO UNA DEUDA. Es la unica de las que
# quedan fuera cuya cota EXISTE y NO es una constante: `M7.longitud_conducto`
# la calcula por Sec. 7.B desde la geometria del propio punto, y es la puerta
# que se usa cuando la clave no se declara (`_resolver_longitud`). La regla de
# este bloque --- la misma magnitud por dos puertas se acota igual --- aqui
# APLICA ENTERA, y su remedio habitual no sirve: no hay simbolo de
# `dominios.py` que heredar y el unico limite verdadero es una FORMULA.
#
# MEDIDO, para que no haya que volver a medirlo: sobre A-01 de
# `tests/ejemplo_puntos.csv` (`ancho_plataforma` = 9.60 m), declarar
# `longitud_m` = 0.5 pasa entero --- Sec. 7.B imprime `longitud_m: 0.5` y
# `factible: true` --- sobre un conducto mas corto que la via que cruza.
# NINGUNA GUARDIA FALTA POR DESCUIDO, y por eso esto no es un defecto suelto:
# `_numero_externo` ya comprueba finitud y signo, y `M7._exigir_finito` hace
# lo propio en la otra puerta. Lo que no hay es la validacion CRUZADA de
# Sec. 1.5 --- un dato contra otro de su misma fila ---, y ponerla significa
# correr M7 para validar el dato que se declaro PRECISAMENTE PARA NO CORRER
# M7. Esa es la eleccion que hay que hacer, y es lo que la convierte en punto
# de decision y no en algo que se arregle de paso. Ficha, con lo que haria
# falta para cerrarla, en `docs/decisiones_diferidas.md`.
_DOMINIO_DE_CLAVE: Dict[str, Tuple[float, str]] = {
    "S_cauce": (S_CAUCE_MAX,
                "una pendiente de cauce en m/m: un valor >= 1 (100 %) delata "
                "una celda cargada en PORCENTAJE, que es el error de "
                "transcripcion mas frecuente de esta columna"),
    # `S_conducto` ENTRO AQUI POR LA AUDITORIA ADVERSARIAL DE C6, y su
    # argumento es mas fuerte que el de la clave de arriba: es LA MISMA
    # MAGNITUD FISICA -- una pendiente en m/m, con el mismo error de
    # transcripcion -- y ademas es la que va DIRECTA a Manning
    # (`MD.disenar_punto` -> `M3.resolver_manning`), cuya unica guardia es
    # `S <= 0`. `S_cauce`, en cambio, solo alimenta una comparacion en V2b.
    # C6 la habia dejado fuera con un argumento cierto -- «no es columna y no
    # tiene dominio declarado» -- que no cubre el principio que ella misma
    # enuncia: la misma magnitud por dos puertas tiene que acotarse igual.
    #
    # SE REUSA `S_CAUCE_MAX` Y NO SE INVENTA UN TECHO NUEVO. El nombre dice
    # «cauce» y el limite es de PENDIENTES: el 1.0 no acota un cauce en
    # particular, acota la ESCRITURA de cualquier pendiente en m/m. Ningun
    # numeral fija un maximo de pendiente -- `verificador-normativo` barrio el
    # Manual entero en C6 --, de modo que separarlos exigiria inventar el
    # segundo techo. El dia que haga falta uno distinto, se separan.
    "S_conducto": (S_CAUCE_MAX,
                   "una pendiente de conducto en m/m: es la MISMA magnitud "
                   "que `S_cauce` y el mismo error de transcripcion, y ademas "
                   "esta es la que entra en Manning"),
}


def _numero_externo(clave: str, bruto: Any, origen: str) -> DatoDeclarado:
    """Un dato externo numerico tiene que ser finito y positivo, en SI."""
    if isinstance(bruto, bool):
        # `float(True)` es 1.0 y `"luz_m": true` entraba como 1.0 m (PC-33).
        # Un booleano no es una longitud ni un caudal, y el JSON los
        # distingue: quien escribio `true` no escribio un numero.
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"es un booleano ({bruto!r}), no un numero (SI, metros o "
                   f"m3/s); origen: {origen}",
        )
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
    #
    # `valor == 0` es la UNICA comparacion de float con igualdad que queda en
    # produccion, y esta declarada a proposito: no compara dos resultados de
    # calculo -- lo que la regla de CLAUDE.md prohibe, porque ahi la igualdad
    # exacta es un accidente del ultimo bit -- sino un dato de entrada contra
    # un CENTINELA. El cero de "salida libre" es el cero exacto que el
    # proyectista escribe en el JSON o en la bandera; un TW de 1e-15 m no es
    # salida libre, es un tirante absurdo, y taparlo con una tolerancia lo
    # convertiria en salida libre en silencio.
    #
    # --- T-2 --- (INF-5.1.6) `S_conducto` ADMITE EL MISMO CERO, por la misma
    # razon: es el centinela con que el proyectista declara un barril
    # HORIZONTAL, que el HDS-5 admite (num. 3.3.4) y que M3 y M4 resuelven
    # desde T-2. `S_cauce` NO lo admite por esta puerta ni por la columna: la
    # pendiente del cauce natural es una medicion de M0 que T-2 no toca
    # (ficha T2-01).
    if valor < 0 or (valor == 0 and clave not in CLAVES_QUE_ADMITEN_CERO):
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"tiene que ser positivo (TW admite 0 = salida libre y "
                   f"S_conducto admite 0 = barril horizontal); "
                   f"origen: {origen}",
        )
    techo = _DOMINIO_DE_CLAVE.get(clave)
    if techo is not None and valor >= techo[0]:
        raise DatoInvalidoError(
            clave, valor=bruto,
            motivo=f"fuera del rango fisico posible ({techo[0]}): {techo[1]}; "
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
    if clave not in CLAVES_EXTERNAS and clave not in CLAVES_DE_DURABILIDAD:
        raise DatoInvalidoError(
            "datos_externos", valor=clave,
            motivo=f"clave no reconocida en {donde}. Las admitidas son: "
                   + ", ".join(CLAVES_EXTERNAS)
                   + "; y los ensayos de durabilidad, opcionales: "
                   + ", ".join(CLAVES_DE_DURABILIDAD),
        )


# ===========================================================================
# Datos de sitio de OTRA obra (EXT-10, EXT-V-01): --datos-sitio sitio.json
# ===========================================================================

def cargar_datos_sitio(ruta: Path, *, origen: Optional[str] = None):
    """
    Lee el JSON de datos de sitio de la obra que se va a calcular y los
    declara POR SESION, sustituyendo lo que otra obra hubiera declarado
    (`declaracion.restaurar_datos_de_sitio(sustituir=True)`). Hermano de
    `cargar_datos_externos`, y con la forma de la sesion escrita una vez:

        {
          "PGA_roca_B": {"valor": 0.30, "trazabilidad": "...", "fecha": "2026-09-21"},
          "corredor_del_proyecto": {"valor": "...", "trazabilidad": "...", "fecha": "..."}
        }

    Se admite tambien la envoltura `{"valores": {...}}`, que es el bloque
    `sitio` de la sesion: un solo parseo para las dos formas.

    UN DEFECTO RECHAZA EL ARCHIVO ENTERO, con `ValueError` y no con
    `DatoInvalidoError`: lo que se rechaza no es un dato del expediente sino
    una DECLARACION que alguien escribio, y el rechazo en la puerta de
    declaracion es `ValueError` (contrato SIS-E-05, el mismo de `--declarar`).
    La clave desconocida tambien sale como `ValueError` --- un [S] no se
    inventa por sesion: su ficha vive en `datos_sitio.py` --- para que las
    dos puertas atrapen UNA excepcion. Y NADA SE TOCA si algo se rechaza: la
    restauracion corre primero EN SECO, y solo con la cuenta limpia se vacia
    lo de la obra anterior y se vuelca lo nuevo. Una obra con la mitad de
    sus [S] seria la obra equivocada con mas silencio, y una obra que pierde
    los suyos porque el archivo de la siguiente venia mal, tambien.
    """
    ruta = Path(ruta)
    crudo = json.loads(ruta.read_text(encoding="utf-8-sig"))
    if not isinstance(crudo, dict):
        raise ValueError(
            f"'{ruta.name}' tiene que ser un objeto JSON con un dato de sitio "
            f"por clave, y trae {type(crudo).__name__}")
    valores = crudo.get("valores", crudo) if set(crudo) == {"valores"} else crudo
    if not isinstance(valores, dict):
        raise ValueError(
            f"'{ruta.name}': 'valores' tiene que ser un objeto con claves y "
            f"trae {type(valores).__name__}")
    for clave, entrada in valores.items():
        if not isinstance(entrada, dict):
            raise ValueError(
                f"'{ruta.name}': '{clave}' tiene que ser un objeto con valor, "
                f"trazabilidad y fecha, y trae {type(entrada).__name__}")
    origen_ = origen if origen is not None else str(ruta)
    en_seco = _declaracion.restaurar_datos_de_sitio(
        {"valores": valores}, sustituir=True, origen=origen_, en_seco=True)
    if en_seco.hubo_rechazos:
        detalle = "; ".join(f"{clave}: {motivo}" for clave, motivo in en_seco.rechazados)
        raise ValueError(
            f"'{ruta.name}' no se puede aplicar entero, y no se aplica a "
            f"medias: {detalle}")
    return _declaracion.restaurar_datos_de_sitio(
        {"valores": valores}, sustituir=True, origen=origen_)


def advertencia_de_corredor_de(proyecto: str, contexto: ContextoCorrida) -> Optional[str]:
    """
    La advertencia de corredor de UNA corrida: el corredor efectivo y su
    origen se leen de la foto, y el texto lo pone `datos_sitio`. La CLI lo
    imprime en consola y M11 en la memoria; ninguno la calcula por su cuenta.
    """
    corredor = contexto.dato_efectivo("corredor_del_proyecto")
    return ds.advertencia_de_corredor(proyecto, str(corredor.valor), corredor.origen)


# ===========================================================================
# Estructuras del informe
# ===========================================================================
# InformePunto, InformeCabezal e Informe no van en modelos.py a proposito: no
# fluyen entre modulos de calculo, son la forma del reporte de esta capa. Lo
# que fluye entre modulos (ResultadoPunto, Verificacion,
# CompatibilidadGeometrica...) se transporta tal cual, sin copiarlo a dicts
# paralelos.
#
# `Bloqueo` ESTABA AQUI Y YA NO (EXT-3, PC-27): su `tipo` pasa a ser el Enum
# `modelos.TipoDeBloqueo` y la clase vive en `modelos.py`, porque el estado
# «pendiente / diferido / no evaluable» dejo de ser de la capa de reporte -- lo
# produce la Fase 5 (`MetodoNoEvaluableError`), lo leen la CLI, la GUI y M11
# --. Se reexporta desde aqui para quien lo importaba como `cli.Bloqueo`.


@dataclass
class InformePunto:
    """Lo que la corrida pudo establecer de un punto, y lo que la freno."""

    punto: PuntoCritico
    clasificacion: Optional[Clasificacion] = None
    resultado: Optional[ResultadoPunto] = None
    luz: Optional[DatoDeclarado] = None
    # EL CAUDAL DE DISEÑO CON SU ORIGEN (T-1): declarado por el estudio
    # hidrologico (columna `Q_m3s` o dato externo) o calculado por la Fase
    # 1-bis. Solo Familias A y B; None en la C y cuando el calculo se detuvo.
    caudal: Optional[CaudalDeDiseno] = None
    categoria_tr: Optional[DatoDeclarado] = None
    longitud: Optional[DatoDeclarado] = None
    tw: Optional[DatoDeclarado] = None
    # El TW con su PROCEDENCIA: por cual de las cuatro vias de Sec. 1.3 salio,
    # con que cota de agua y -- si fue por escenarios acotados -- con los dos
    # numeros del paso 3. `tw` sigue siendo el float que MD consume; esto es
    # lo que la memoria imprime, y son dos cosas distintas a proposito.
    tw_sec13: Optional[TWDeterminado] = None
    # --- T-2 --- Lo que el punto declaro sobre el acceso de mantenimiento
    # (`acceso_mantenimiento_previsto`, booleano opcional de --datos-
    # externos), o None si no declaro nada. No entra en ningun calculo.
    acceso_mantenimiento: Optional[DatoDeclarado] = None
    # La pendiente del CAUCE cuando la columna va vacia y la aporta el
    # Tablero 3.1. Se guarda como `DatoDeclarado` -- no se mete de tapadillo
    # en `punto` -- porque la memoria tiene que decir de donde salio: la fila
    # del CSV sigue mostrando la columna vacia, y esta fila muestra el valor
    # con su origen. Es el mismo par que ya forman `longitud` y `tw`.
    s_cauce: Optional[DatoDeclarado] = None
    # El punto CON los datos de tablero completados. `punto` sigue siendo la
    # fila del CSV tal como M0 la cargo, y esa distincion es la que permite
    # que la memoria imprima «columna vacia -- dato de un tablero externo» en
    # la fila de la columna Y el valor con su origen en la suya.
    punto_completado: Optional[PuntoCritico] = None
    # --- T-4 --- El dictamen de la matriz de durabilidad (Sec. 3.3). Se
    # calcula para todo punto que pasa la Fase 2, antes del bucle de MD.
    # None si el punto no llego a la Fase 3, o si la etapa se bloqueo (hay
    # entonces un bloqueo `ETAPA_DURABILIDAD` y el bucle de MD no corre).
    durabilidad: Optional[DictamenDurabilidad] = None
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
    def punto_de_calculo(self) -> PuntoCritico:
        """
        El punto que va al pipeline: la fila del CSV completada con los datos
        que un tablero externo aporto.

        Existe para que `punto` NO cambie. Todo lo que imprime procedencia
        --`M11._tabla_datos`-- lee `punto` y sigue diciendo la verdad sobre el
        CSV; todo lo que CALCULA lee este.
        """
        return self.punto_completado or self.punto

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

    def con_aviso(self) -> Tuple[Verificacion, ...]:
        """
        --- T-2 --- Las verificaciones de la seccion aceptada cuyo estado es
        INDICADOR: se dispararon y el diseño NO se detuvo (V2b bajo
        'regimen_v2b' = indicador_con_aviso; V1 bajo
        'borde_libre_bajo_tw_ahogante' = aviso). No son incumplidas --el
        punto dimensiona-- y por eso mismo hay que contarlas aparte: un
        RESUMEN que dijera «incumplidas: 0» y nada mas las callaria.
        """
        return tuple(v for _, v in self.verificaciones()
                     if v.estado is EstadoDeVerificacion.INDICADOR)

    def indicadores_de_hidrologia(self) -> Tuple[Any, ...]:
        """
        --- T-1 --- Los pasos de la Fase 1-bis que salieron como INDICADOR:
        el caudal se calculo y el punto no se detiene, pero un contraste de
        la memoria hidrologica se disparo (la lluvia de diseño por debajo de
        un año ya registrado, la serie mas corta que lo recomendado, la
        cuenca fuera de la poblacion de su formula, el tiempo de
        concentracion por debajo de la duracion minima). Cuentan en el
        RESUMEN junto a las verificaciones con aviso (`Informe.resumen`);
        su texto esta en `avisos()`.
        """
        if self.caudal is None:
            return ()
        return tuple(p for p in self.caudal.pasos
                     if p.veredicto is not None
                     and p.veredicto.tipo is TipoDeVeredicto.INDICADOR)

    def avisos(self) -> Tuple[str, ...]:
        """
        --- T-2 --- Los AVISOS del punto: lo que la corrida tiene que decir
        en voz alta sin detenerse. Son tres clases: el TW obtenido con la
        seccion ADOPTADA del receptor (INF-3.2.8, `TWDeterminado.avisos`),
        el acceso de mantenimiento declarado como NO previsto, y cada
        verificacion que salio como INDICADOR (`con_aviso`), con su codigo y
        la explicacion de su veredicto. Los imprimen la CLI y el JSON con el
        MISMO texto, que sale de aqui.
        """
        avisos: List[str] = []
        # --- T-1 --- Primero los de la Fase 1-bis, en el orden del calculo:
        # el aviso permanente del caudal declarado (el criterio FEN no lo
        # alcanza), y los del caudal calculado (lluvia de diseño por debajo
        # de lo observado, serie corta o con huecos, tiempo de concentracion
        # extrapolado, duracion minima adoptada).
        if self.caudal is not None:
            avisos.extend(self.caudal.avisos)
        if self.tw_sec13 is not None:
            avisos.extend(self.tw_sec13.avisos)
        acceso = self.acceso_mantenimiento
        if acceso is not None and acceso.valor is False:
            avisos.append(AVISO_SIN_ACCESO_DE_MANTENIMIENTO)
        for v in self.con_aviso():
            explicacion = (v.paso.veredicto.explicacion
                           if v.paso is not None and v.paso.veredicto is not None
                           else "")
            avisos.append(
                f"{v.codigo}: indicador disparado; el diseño no se detiene"
                + (f" -- {explicacion}" if explicacion else ""))
        return tuple(avisos)

    def bloqueos_reales(self) -> Tuple[Bloqueo, ...]:
        """
        Los bloqueos que SI cuentan: los que no son una decision de alcance.
        Es la cuenta que la tabla de puntos de la GUI y el volcado tienen que
        compartir (EXT-G-02): sumar `len(bloqueos)` mezcla lo diferido.
        """
        return tuple(b for b in self.bloqueos if not b.diferido_por_alcance)


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


@dataclass(frozen=True)
class ResumenDeCorrida:
    """
    Las cifras del RESUMEN, calculadas UNA vez en `Informe.resumen` y
    leidas por las tres capas que las imprimen: el volcado de la CLI, la
    pestaña 4 de la GUI y el encabezado de la memoria HTML. Eran seis hasta
    T-2, que sumo `con_aviso`: las verificaciones que salieron como
    INDICADOR en la seccion aceptada. La imprimen la CLI y la memoria; la
    pestaña 4 la muestra fila a fila y todavia no la cuenta.

    Existe por EXT-G-02: la GUI decia «Etapas bloqueadas: 12» y la CLI, sobre
    el mismo `Informe`, 1, porque una contaba `len(bloqueos())` --- con lo
    diferido por alcance dentro --- y la otra lo restaba. Contar en cada capa
    reproduce la asimetria CLI/GUI (SIS-E-01); la cuenta va en el informe.
    """

    puntos: int
    dimensionados: int
    incumplidas: int
    bloqueadas: int          # reales: NO cuentan las diferidas por alcance
    diferidas: int
    cerrado: bool
    con_aviso: int = 0       # T-2: verificaciones con veredicto INDICADOR;
                             # T-1: y los pasos de la Fase 1-bis que lo llevan


@dataclass
class Informe:
    """El expediente completo de una corrida."""

    csv: Path
    generado: str
    alcance: str = ALCANCE_EXPEDIENTE
    # Las dos entradas de la Fase 1-bis con que corrio (T-1), o None.
    hidrologia: Optional[EntradaHidrologica] = None
    puntos: List[InformePunto] = field(default_factory=list)
    cabezal: InformeCabezal = field(default_factory=InformeCabezal)
    # LA FOTO DEL ESTADO CON QUE CORRIO (EXT-4, EXT-A-01). La pone `correr`
    # al salir y de ella leen los cuatro exportadores; un `Informe` armado a
    # mano no la tiene y `ContextoCorrida.de` lo dice en vez de leer el
    # estado vivo del proceso.
    contexto: Optional[ContextoCorrida] = None

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

    def bloqueos_reales(self) -> Tuple[Tuple[Optional[str], Bloqueo], ...]:
        """
        Los bloqueos que cuentan para el cierre: todos menos los diferidos
        por alcance. Es la UNICA definicion de «etapa bloqueada» del
        proyecto (EXT-G-02): `cerrado`, `resumen`, el volcado, la GUI y la
        memoria la leen de aqui.
        """
        return tuple((id_punto, b) for id_punto, b in self.bloqueos()
                     if not b.diferido_por_alcance)

    def resumen(self) -> ResumenDeCorrida:
        """Las cifras del resumen, una vez, para las tres capas."""
        return ResumenDeCorrida(
            puntos=len(self.puntos),
            dimensionados=self.dimensionados,
            incumplidas=sum(len(i.incumplidas()) for i in self.puntos),
            bloqueadas=len(self.bloqueos_reales()),
            diferidas=len(self.diferidos()),
            cerrado=self.cerrado,
            # T-1: y los pasos de la Fase 1-bis con veredicto INDICADOR,
            # que son lo mismo un escalon antes: un contraste que se disparo
            # sin detener el punto.
            con_aviso=sum(len(i.con_aviso()) + len(i.indicadores_de_hidrologia())
                          for i in self.puntos))

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
        if self.bloqueos_reales():
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
        # `ca.declaracion_de` y no `ca.criterio`: la misma excepcion la
        # levanta `datos_sitio.valor` para un [S] de corredor sin leer, y
        # resolverla solo contra CRITERIOS salia por KeyError -- un fallo de
        # programa dentro de la funcion que existe para evitarlo (SIS-A-05).
        declarado = ca.declaracion_de(exc.clave)
        datos = {"criterio": exc.clave, "etiqueta": declarado.etiqueta,
                 "concepto": declarado.concepto, "fuente": declarado.fuente}
    elif isinstance(exc, (DatoFaltanteError, DatoInvalidoError)):
        datos = {"campo": exc.campo}
    elif isinstance(exc, DisenoNoFactibleError):
        datos = {"delta_rasante_m": exc.delta_rasante_m}
    return Bloqueo(fase=fase, etapa=etapa, tipo=TipoDeBloqueo.de_excepcion(exc),
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
    punto = informe.punto_de_calculo
    declarada = externos.dato(punto.id, "longitud_m")
    if declarada is not None:
        return declarada
    longitud = _etapa(informe.bloqueos, FASE_GEOMETRIA,
                      "longitud del conducto (7.B)",
                      lambda: longitud_conducto(punto))
    if longitud is None:
        return None
    return DatoDeclarado("longitud_m", longitud, "M7.longitud_conducto (Sec. 7.B)")


def _resolver_tw(informe: InformePunto, externos: DatosExternos,
                 longitud: DatoDeclarado) -> Optional[DatoDeclarado]:
    """
    TW por el procedimiento de Sec. 1.3 (`M3.tw_seccion_1_3`), con el criterio
    'TW_receptor' como ultima puerta.

    LA CLI NO DECIDE NADA AQUI, y ese es el punto. Las cuatro vias de Sec. 1.3
    -- declarado, `cota_TW`, Manning en el receptor, escenarios acotados --
    las recorre M3, que es quien emite el `PasoDeMemoria` con la via por la
    que salio el numero. Esta funcion aporta lo unico que M3 no puede saber:
    la cota de fondo de la SALIDA, que sale de 7.B y necesita la longitud y la
    pendiente del diseño.

    LA PENDIENTE QUE SE USA ES LA MISMA DEL DISEÑO, no otra: `S_conducto` si
    el punto lo declara y la del cauce si no, que es lo que `disenar_punto`
    hara despues con el TW que esta funcion devuelve. Dos pendientes distintas
    darian dos cotas de salida distintas para el mismo punto, que es el
    defecto que MAT-D9 cerro en 7.B.

    SI 'TW_receptor' TIENE VALOR, MANDA SOBRE LAS VIAS 3 Y 4 pero no sobre las
    dos primeras. Es deliberado: el criterio es una declaracion del
    proyectista sobre el nivel del receptor, del mismo rango que `--tw`, y no
    tiene sentido calcular por Manning un numero que ya se declaro. Lo que si
    manda sobre el es un dato del expediente: una `cota_TW` en el CSV es una
    medicion o un calculo con procedencia, y no se pisa con una adopcion.
    """
    punto = informe.punto_de_calculo
    declarado = externos.dato(punto.id, "TW_m")
    S = externos.valor(punto.id, "S_conducto")
    # --- T-2 --- (INF-3.2.8) La seccion MEDIDA del receptor, si el
    # expediente la trae: gana sobre el criterio 'seccion_receptor' en las
    # vias 3 y 4, y M3 dice en el paso con cual corrio.
    medida = externos.valor(punto.id, CLAVE_SECCION_RECEPTOR_MEDIDA)
    seccion_medida = (None if medida is None else SeccionReceptor(**medida))

    def resolver():
        declarado_a_mano = (declarado.valor if declarado is not None else None)
        if tw_sin_via_de_sec_1_3(declarado_a_mano, punto.cota_TW,
                                 punto.Q_receptor_m3s,
                                 hay_seccion_medida=seccion_medida is not None):
            # Ninguna de las cuatro vias de Sec. 1.3 es recorrible: se cae al
            # criterio, que es la ultima puerta y la que detiene con su ficha
            # entera. Se consulta con `valor`, no con `valor_si_declarado`,
            # justamente para que detenga.
            declarado_a_mano = ca.valor(CRITERIO_TW)
        # LA COTA DE FONDO DE LA SALIDA SOLO SE CALCULA SI HACE FALTA. Con el
        # TW declarado a mano no hay ninguna cota que restar, y exigir la
        # pendiente del cauce para un dato que ya esta seria pedir un dato
        # para no usarlo: un punto de Familia C, cuya `S_cauce` va vacia
        # porque su pendiente es la del canal (Sec. 2.3), quedaria bloqueado
        # en el TW en vez de llegar al bloqueo que de verdad tiene.
        fondo_salida = None
        if declarado_a_mano is None:
            pendiente = S if S is not None else punto.exigir("S_cauce")
            fondo_salida = cota_salida(punto=punto, longitud=longitud.valor,
                                       S=pendiente)
        return M3.tw_seccion_1_3(punto=punto, cota_fondo_salida=fondo_salida,
                                 tw_declarado=declarado_a_mano,
                                 seccion_medida=seccion_medida)

    resuelto = _etapa(informe.bloqueos, FASE_DISENO,
                      "tirante en el receptor (TW, Sec. 1.3)", resolver)
    if resuelto is None:
        return None
    informe.tw_sec13 = resuelto
    origen = (declarado.origen if declarado is not None
              else f"Sec. 1.3 -- {resuelto.via.value}")
    return DatoDeclarado("TW_m", resuelto.valor, origen)


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
    La Fase 5 al alcance de perfil: las ONCE verificaciones de M5, en el
    orden de la tabla, con V5 y V8 DIFERIDAS al expediente.

    - Obligatorias (deciden si el diametro se acepta): V1, V2, V2b, V3, V4,
      V4b, V6, V7 y V9. Corren exactamente como en M5.verificar y sus
      excepciones suben igual: un criterio vacio en una obligatoria sigue
      bloqueando el material (y, por la regla de MD, el punto).
    - Y VC1 en la Familia C, que tambien es OBLIGATORIA: ocupa el hueco de V5
      y no se difiere. Ver el comentario del hueco, abajo.
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

    LA MINA DE V8 SE DESACTIVO EN S20, y hay que decir como. `v8_evento_extremo`
    terminaba en `raise AssertionError` en cuanto 'TR_evento_extremo' tuviera
    valor: aqui solo se captura `ErrorProyecto`, de modo que declarar ese
    criterio tumbaba la corrida ENTERA -- todos sus puntos -- con una traza de
    fallo de programa. La mina cumplia su proposito (avisar de que la logica
    de V8 no esta escrita) por el medio equivocado: un `AssertionError` no
    desciende de `ErrorProyecto` y la GUI no lo puede distinguir de un bug.
    Hoy V8 lanza `DatoFaltanteError` sobre el dato que de verdad falta -- el Q
    del evento extremo --, que es la MISMA solucion que ya se le habia dado a
    V5 y que CLAUDE.md contempla expresamente para el dato que un tablero
    externo tendria que aportar. El aviso sigue siendo ruidoso y ahora es del
    expediente, no del programa. (La mina hermana,
    `M8.seleccionar_clase_calibre` con 'clases_producto_por_relleno', esta
    documentada donde se salta la Fase 8 en `correr_punto`; y la de
    `M2.espesor_pared` se cerro en la misma sesion y por la misma razon.)
    """
    ya_registrados: set = set()

    def verificar(*, punto: PuntoCritico, material, seccion, resultado):
        # La altura para las tres que solo necesitan la altura. V7 pide la
        # SECCION entera, porque la subpresion actua sobre la superficie
        # exterior y ahi un prisma y un cilindro dejan de parecerse.
        D = seccion.altura
        # LO QUE YA SE VERIFICO NO SE TIRA, y hasta C5 aqui SI se tiraba.
        # `M5.verificar` lo resolvio en su dia --su docstring lo cuenta-- y
        # este verificador, que es el del alcance de perfil, se quedo con la
        # lista literal: cualquier `ErrorProyecto` de una obligatoria subia
        # sin `verificaciones_completadas` y el desarrollo de V1 a V4b, que si
        # se habia calculado entero, no llegaba nunca a la memoria. Dejo de
        # ser teorico en C5: un marco se detiene en V7 --su espesor de pared
        # no existe todavia-- y con la lista literal la advertencia de alcance
        # de §15.6.3, que viaja en los pasos de V1 y de V4, se perdia con
        # ellos. Es la trampa de NOR-MEM-01 otra vez: cierto sobre el codigo y
        # falso sobre el producto.
        filas: List[Verificacion] = []
        # V1 Y V2 SIGUEN SIENDO OBLIGATORIAS, con una salvedad que no es de
        # alcance sino de METODO (EXT-3, v8 §4.1): cuando el barril va
        # parcialmente lleno bajo control de SALIDA, M5 no puede evaluarlas
        # sin el perfil de la lamina de agua y lo dice con
        # `MetodoNoEvaluableError`. A nivel de perfil ese fallo se registra
        # como diferido --con la misma deduplicacion que V5 y V8-- y el
        # punto sigue dimensionandose; a nivel de expediente sube y bloquea
        # (`M5.verificar`). Cualquier OTRO ErrorProyecto de V1/V2 sube igual
        # que antes: no es el metodo, es el expediente.
        for codigo, pieza in (
            ("V1", lambda: M5.v1_borde_libre(D=D, material=material,
                                             punto=punto, resultado=resultado)),
            ("V2", lambda: M5.v2_velocidad_minima(resultado=resultado)),
        ):
            try:
                filas.append(pieza())
            except MetodoNoEvaluableError as exc:
                # Misma consulta que el hueco de V5 y que V8: este verificador
                # solo corre a nivel de perfil, asi que la condicion es hoy
                # siempre cierta, y esta escrita igual para que quitar el
                # perfil de la tupla vuelva a subir el fallo como en el
                # expediente, en vez de dejar el dato describiendo un
                # diferimiento que el codigo ya no hace.
                if ALCANCE_PERFIL in ALCANCES_QUE_DIFIEREN_METODO_NO_EVALUABLE:
                    _diferir_verificacion(informe, codigo, exc, ya_registrados)
                else:
                    exc.verificaciones_completadas = tuple(filas)
                    raise
            except ErrorProyecto as exc:
                exc.verificaciones_completadas = tuple(filas)
                raise
        obligatorias_previas = (
            # V2b entra como OBLIGATORIA, y no diferida: su indicador se
            # calcula con dos numeros que la corrida de perfil ya tiene (la
            # pendiente del diseño y la del cauce) y su criterio no depende
            # de ningun dato de expediente. Lo que difiere el alcance de
            # perfil son las verificaciones que necesitan el expediente, no
            # las que solo necesitan una declaracion del proyectista.
            lambda: M5.v2b_sedimentacion(punto=punto, resultado=resultado),
            lambda: M5.v3_velocidad_maxima(material=material,
                                           resultado=resultado),
            lambda: M5.v4_carga_entrada(punto=punto, resultado=resultado),
            # V4b se cableo en S14 y entra aqui como OBLIGATORIA, igual que
            # en `M5.verificar`: su umbral es un criterio con valor y no
            # depende de ningun dato de expediente que el alcance de perfil
            # difiera. Si alguien le quitara el valor a 'HW_D_max', la
            # `CriterioPendienteError` subiria y bloquearia el material, que
            # es lo que corresponde a un umbral sin declarar.
            lambda: M5.v4b_relacion_hw_d(D=D, resultado=resultado),
            # --- T-2 --- V10 (pendiente del conducto dentro de la banda
            # adoptada) entra como OBLIGATORIA y EN EL MISMO SITIO que en
            # `M5.verificar`: detras de V4b y antes del hueco de V5. Sus dos
            # criterios tienen valor y no depende del diametro ni de ningun
            # dato de expediente.
            lambda: M5.v10_pendiente_conducto(resultado=resultado),
        )
        for pieza in obligatorias_previas:
            try:
                filas.append(pieza())
            except ErrorProyecto as exc:
                exc.verificaciones_completadas = tuple(filas)
                raise
        # EL HUECO DE V5, QUE EN FAMILIA C LO OCUPA VC1, y las dos no se
        # tratan igual. Quien decide cual toca es `M5.pieza_del_hueco_de_V5`,
        # que es donde vive la regla de familia; lo que se decide AQUI --- y
        # es de la corrida, no de M5 --- es que hacer si la pieza falla:
        #
        #   V5   se DIFIERE. Lo que le falta (perfil de remanso, ancho de
        #        derecho de via) son datos de EXPEDIENTE, que es justo lo que
        #        el alcance de perfil aparta.
        #   VC1  es OBLIGATORIA. Lo que necesita ya esta al alcance de una
        #        corrida de perfil: una columna del CSV y un criterio
        #        declarado. Diferirla dejaria pasar el punto acreditado como
        #        alcantarilla de paso sin que nadie hubiera mirado el canal,
        #        que es exactamente el estado que esta sesion cierra.
        # La condicion consulta VERIFICACIONES_DIFERIDAS_POR_ALCANCE --- y no
        # el literal "V5" que habia --- para que ese dato no pueda quedarse
        # describiendo un diferimiento que este codigo ya no hace: VC1 no
        # esta en la tupla y por eso sube.
        codigo_hueco, pieza_hueco = M5.pieza_del_hueco_de_V5(
            punto=punto, resultado=resultado)
        try:
            filas.append(pieza_hueco())
            if codigo_hueco != "V5":
                # La fila sustituida, como «no aplica» y con su motivo
                # (PC-27): la tabla de la Fase 5 conserva sus once filas.
                filas.append(M5.v5_no_aplica_en_canal(punto=punto))
        except ErrorProyecto as exc:
            if codigo_hueco in VERIFICACIONES_DIFERIDAS_POR_ALCANCE[ALCANCE_PERFIL]:
                _diferir_verificacion(informe, codigo_hueco, exc,
                                      ya_registrados)
            else:
                exc.verificaciones_completadas = tuple(filas)
                raise
        for pieza in (
            lambda: M5.v6_material_solido_arrastre(material=material),
            lambda: M5.v7_flotacion(punto=punto, material=material,
                                    seccion=seccion, resultado=resultado),
        ):
            try:
                filas.append(pieza())
            except ErrorProyecto as exc:
                exc.verificaciones_completadas = tuple(filas)
                raise
        try:
            filas.append(M5.v8_evento_extremo(punto=punto, resultado=resultado))
        except ErrorProyecto as exc:
            # Misma consulta que el hueco de V5: si "V8" saliera de la tupla,
            # su fallo volveria a subir como una obligatoria, y el dato que el
            # anticipo lee no podria divergir de lo que esta corrida hace.
            if "V8" in VERIFICACIONES_DIFERIDAS_POR_ALCANCE[ALCANCE_PERFIL]:
                _diferir_verificacion(informe, "V8", exc, ya_registrados)
            else:
                exc.verificaciones_completadas = tuple(filas)
                raise
        try:
            filas.append(M5.v9_disponibilidad_diametro(D=D, material=material))
        except ErrorProyecto as exc:
            exc.verificaciones_completadas = tuple(filas)
            raise
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
        _falta_dato(informe.bloqueos, FASE_CLASIFICACION, ETAPA_FALTA_LUZ,
                    "luz_m", DETALLE_FALTA_LUZ)
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


def cargar_hidrologia(ruta_cuencas: Optional[Path],
                      ruta_estacion: Optional[Path],
                      ) -> Optional[EntradaHidrologica]:
    """
    Las dos entradas de la Fase 1-bis (--cuencas y --estacion), o None si la
    corrida no trae ninguna. Van JUNTAS: una cuenca sin serie de lluvia, o
    una serie sin cuencas, no calculan nada, y traer una sola es
    `DatoFaltanteError` con el nombre de la que falta. No hay valores por
    defecto: sin las dos, el caudal entra declarado por `Q_m3s` como siempre.
    """
    if ruta_cuencas is None and ruta_estacion is None:
        return None
    if ruta_cuencas is None:
        raise DatoFaltanteError(
            "cuencas",
            detalle="se declaro la serie de la estacion (--estacion) y no el "
                    "CSV de cuencas (--cuencas): el calculo hidrologico "
                    "necesita los dos")
    if ruta_estacion is None:
        raise DatoFaltanteError(
            "estacion",
            detalle="se declaro el CSV de cuencas (--cuencas) y no la serie "
                    "de la estacion (--estacion): el calculo hidrologico "
                    "necesita los dos")
    return MH.cargar_entrada(Path(ruta_cuencas), Path(ruta_estacion))


def _fase_hidrologia(informe: InformePunto, externos: DatosExternos,
                     hidrologia: Optional[EntradaHidrologica]) -> bool:
    """
    Fase 1-bis: de donde sale el caudal de diseño de un punto de Familia A o
    B (T-1). Devuelve False solo cuando el caudal habia que CALCULARLO y el
    calculo se detuvo: entonces el diseño no se intenta, porque repetiria el
    mismo bloqueo como «falta Q_m3s».

    LA PRECEDENCIA, que es la de siempre con un escalon nuevo al final:

      1. `Q_m3s` declarado en --datos-externos: gana, como ya ganaba
         (`disenar_punto` lo recibe explicito).
      2. La columna `Q_m3s` del CSV, llena: se usa tal cual. La memoria
         imprime «Q declarado por el estudio hidrológico».
      3. La columna vacia y la corrida trae la cuenca de la obra y la serie
         de su estacion: lo calcula `MH.caudal_de_diseno` con el TR de la
         Fase 2, y el punto de calculo lo lleva en `Q_m3s`.

    Sin ninguna de las tres no se llega aqui: M0 no carga el punto
    (`DatoFaltanteError('Q_m3s')`). En los escalones 1 y 2 NO se recalcula
    nada aunque haya cuenca: un dato del expediente no se corrige. La
    Familia C no pasa por esta fase: su caudal es el del canal.
    """
    punto = informe.punto
    if punto.familia not in FAMILIAS_CON_CAUDAL_HIDROLOGICO:
        return True
    cuenca = None if hidrologia is None else hidrologia.cuenca_de(punto.id)
    externo = externos.dato(punto.id, COLUMNA_CAUDAL)
    # EL AREA ESCRITA DOS VECES (auditoria de T-1). Con --cuencas la cuenca
    # de la obra esta en `area_ha` del CSV de puntos, que fijo su periodo de
    # retorno en la Fase 2, y en `area_km2` del CSV de cuencas, que entra al
    # caudal. Si no dicen lo mismo el programa no elige: la etapa se bloquea
    # con `DatoInvalidoError`. Un caudal DECLARADO no depende de ninguna de
    # las dos y el punto se dimensiona igual, sin el contraste Q/A; uno por
    # CALCULAR no se calcula.
    areas_coherentes = True
    if cuenca is not None and punto.area_ha is not None:
        areas_coherentes = _etapa(
            informe.bloqueos, FASE_HIDROLOGIA, ETAPA_AREA_DE_LA_CUENCA,
            lambda: MH.exigir_areas_coherentes(
                area_ha=punto.area_ha, area_km2=cuenca.area_km2,
                id_punto=punto.id, origen_cuenca=cuenca.origen) or True
        ) is not None
    if externo is not None or punto.Q_m3s is not None:
        if not areas_coherentes:
            area, origen_area = None, ""
        elif cuenca is not None:
            area, origen_area = cuenca.area_km2, f"columna area_km2 de {cuenca.origen}"
        elif punto.area_ha is not None:
            area = MH.area_de_columna_km2(punto.area_ha)
            origen_area = "CSV Sec. 1.2, columna area_ha, de ha a km2"
        else:
            area, origen_area = None, ""
        informe.caudal = MH.caudal_declarado(
            Q_m3s=punto.Q_m3s if externo is None else externo.valor,
            de_donde=ORIGEN_Q_DE_COLUMNA if externo is None else externo.origen,
            area_km2=area, origen_area=origen_area,
            cuenca_disponible=cuenca is not None)
        return True
    if not areas_coherentes:
        return False
    if cuenca is None:
        # M0 solo admite la celda vacia con cuenca; llegar aqui es un punto
        # armado a mano. Se dice como dato faltante, no se inventa.
        _falta_dato(informe.bloqueos, FASE_HIDROLOGIA, ETAPA_CAUDAL_CALCULADO,
                    COLUMNA_CAUDAL,
                    "la columna va vacia y la corrida no trae la cuenca de "
                    "esta obra (--cuencas) ni la serie de su estacion "
                    "(--estacion)")
        return False
    clasificacion = informe.clasificacion
    if clasificacion is None or clasificacion.periodo_retorno.anios is None:
        # Sin TR no hay lluvia de diseño que calcular; la Fase 2 ya dejo su
        # bloqueo y repetirlo aqui no añade nada.
        return False
    serie = hidrologia.estaciones[cuenca.estacion]
    informe.caudal = _etapa(
        informe.bloqueos, FASE_HIDROLOGIA, ETAPA_CAUDAL_CALCULADO,
        lambda: MH.caudal_de_diseno(cuenca, serie,
                                    clasificacion.periodo_retorno.anios))
    if informe.caudal is None:
        return False
    informe.punto_completado = replace(informe.punto_de_calculo,
                                       Q_m3s=informe.caudal.Q_m3s)
    return True


def _fase_durabilidad(informe: InformePunto,
                      externos: DatosExternos) -> None:
    """
    Sec. 3.3: la matriz de durabilidad del punto (T-4; INF-3.3.1, INF-5.1.9).

    Corre para todo punto que PASA LA FASE 2, antes del bucle de materiales
    --es Fase 3--: no necesita el caudal ni la longitud, solo los ensayos
    declarados --si los hay-- y la columna `sucs_fundacion`. Sin ensayos deja
    un dictamen «no aplicado», que es lo que la memoria y el volcado imprimen
    con `DURABILIDAD_SIN_ENSAYOS`. Un punto que se detiene en la Fase 2 (sin
    luz, o con luz de puente) no llega aqui y no invoca ningun criterio: no
    hay materiales que filtrar en una obra que no se va a dimensionar.

    SI LA ETAPA SE BLOQUEA --un criterio de la matriz vaciado, un nivel de
    abrasion que burlo la puerta-- `informe.durabilidad` queda en None y
    `_fase_diseno` NO corre el bucle de MD: dimensionar con los tres
    candidatos cuando el filtro no se pudo aplicar seria el relleno en
    silencio que este proyecto prohibe.
    """
    punto = informe.punto_de_calculo
    informe.durabilidad = _etapa(
        informe.bloqueos, FASE_DISENO, ETAPA_DURABILIDAD,
        lambda: matriz_durabilidad(
            punto, ensayos_de_durabilidad(externos, punto.id)))


def _fase_diseno(informe: InformePunto, externos: DatosExternos,
                 alcance: str = ALCANCE_EXPEDIENTE) -> None:
    """
    Fases 3-5: MD recorre materiales y diametros hasta que uno pase la Fase 5.

    Con alcance de expediente la Fase 5 es la de M5 completa (V1-V9). Con
    alcance de perfil se inyecta `_verificador_perfil`, que difiere V5 y V8
    al expediente y deja las otras siete como obligatorias.
    """
    punto = informe.punto_de_calculo
    informe.longitud = _resolver_longitud(informe, externos)
    # El TW se resuelve DESPUES de la longitud y con ella: la cota de fondo de
    # la salida que Sec. 1.3 necesita para convertir una cota de agua en un
    # tirante sale de 7.B, y 7.B necesita la longitud.
    informe.tw = (None if informe.longitud is None
                  else _resolver_tw(informe, externos, informe.longitud))
    if informe.longitud is None or informe.tw is None:
        return
    if informe.durabilidad is None:
        # La matriz de durabilidad se bloqueo (ver `_fase_durabilidad`): su
        # bloqueo ya esta registrado y el bucle no corre sin filtro.
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
                              registrar=informe.traza.append,
                              durabilidad=informe.durabilidad))

    if informe.resultado is not None and not informe.resultado.aceptado:
        informe.bloqueos.append(Bloqueo(
            fase=FASE_DISENO, etapa="material y diametro (bucle de MD)",
            tipo=TipoDeBloqueo.DISENO_NO_FACTIBLE,
            mensaje=informe.resultado.motivo_rechazo or "sin motivo declarado"))


def _fase_6(informe: InformePunto) -> None:
    """
    Proteccion de salida por Laushey, con la velocidad de SALIDA de HDS-5
    3.1.6 que M4 emite (EXT-3; PC-04, EXT-M-01).

    Hasta EXT-3 entraba `V_erosion` -- la rama de n minimo del flujo uniforme,
    la estimacion ALTA -- por ser el lado conservador de una proteccion cuyo
    d50 crece con V^2. Y lo sigue siendo bajo control de ENTRADA, donde la
    velocidad de salida es la del tirante normal; pero bajo control de SALIDA
    la velocidad a la salida es Q entre el area al tirante min(D, max(TW,
    y_c)), y en pendiente suave con salida libre es MAYOR que la uniforme
    (1.508 vs 1.184 m/s en el caso del dictamen): la piedra salia chica. Quien
    decide cual de las dos es M4, que tiene el control gobernante delante, y
    la decision viaja en la procedencia de la `Magnitud`; esta fase la pasa
    tal cual.
    """
    resultado = informe.resultado.resultado_hidraulico
    if resultado.V_salida is None:
        # Fallo de PROGRAMA, no del expediente: M4 llena V_salida siempre. Un
        # ResultadoHidraulico sin ella no salio de `resolver_control`, y
        # rellenarla aqui con V_erosion seria el default silencioso que este
        # proyecto prohibe.
        raise ValueError(
            f"el resultado hidraulico de {informe.punto.id} no trae la "
            "velocidad de salida (ResultadoHidraulico.V_salida): la Fase 6 "
            "no elige una velocidad por su cuenta")
    informe.proteccion = _etapa(
        informe.bloqueos, FASE_PROTECCION, "d50, espesor y longitud",
        lambda: proteccion_salida(V=resultado.V_salida))


def _fase_7(informe: InformePunto) -> None:
    """7.B con la SECCION adoptada y la MISMA longitud que uso la Fase 4."""
    resultado = informe.resultado
    informe.geometria = _etapa(
        informe.bloqueos, FASE_GEOMETRIA, "compatibilidad geometrica (7.B)",
        lambda: compatibilidad_geometrica(
            punto=informe.punto_de_calculo, material=resultado.material,
            seccion=resultado.seccion,
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
    material, seccion = resultado.material, resultado.seccion
    punto = informe.punto_de_calculo

    # Altura real de relleno sobre la clave FISICA (con espesor de pared), la
    # misma definicion que usa V7: subrasante menos clave, no el minimo de 7.A.
    # Se pide a M5 en vez de restarse aqui: esta copia iba sin la guarda de
    # `DatoInvalidoError` que V7 si tenia, y una altura negativa habria
    # entrado a la tabla de clases de la norma de producto el dia en que
    # 'clases_producto_por_relleno' se declare (SIS-A-21).
    altura = _etapa(informe.bloqueos, FASE_ESTRUCTURAL,
                    "altura de relleno sobre la clave",
                    lambda: altura_relleno_sobre_clave(
                        punto=punto, material=material, seccion=seccion))
    if altura is not None:
        _etapa(informe.bloqueos, FASE_ESTRUCTURAL,
               "clase o calibre por norma de producto (items 1-2)",
               lambda: seleccionar_clase_calibre(material=material,
                                                 altura_relleno=altura))
    informe.cama_apoyo = _etapa(informe.bloqueos, FASE_ESTRUCTURAL,
                                "cama de apoyo y relleno lateral (item 4)",
                                lambda: cama_apoyo_relleno_lateral(material))


def _fase_10(informe: InformePunto, externos: DatosExternos) -> None:
    """
    Espaciamiento de alivio: solo Familia B (Sec. 10).

    La condicion se lee de `FAMILIAS_QUE_USAN`, que es lo que hace de esa
    declaracion un dato del programa y no un comentario: la pestana 1 anota
    con la MISMA fila que decide aqui si la fase corre.
    """
    if informe.punto.familia not in familias_que_usan("L_hidraulico_m"):
        return
    L_hidraulico = externos.valor(informe.punto.id, "L_hidraulico_m")
    if L_hidraulico is None:
        _falta_dato(informe.bloqueos, FASE_ALIVIO, ETAPA_FALTA_L_HIDRAULICO,
                    "L_hidraulico_m", DETALLE_FALTA_L_HIDRAULICO)
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
        tipo=TipoDeBloqueo.DIFERIDO_POR_ALCANCE,
        mensaje=("clase o calibre por norma de producto (items 1-2) y cama "
                 "de apoyo (item 4) no se ejecutan en alcance de perfil: son "
                 "verificacion estructural del conducto, que la hoja de ruta "
                 "difiere al expediente (Sec. 7.A / Fase 8, 'Diferir al "
                 "expediente la verificacion detallada'). Disponibles sin "
                 "cambios con --alcance expediente"),
        diferido_por_alcance=True))


# ---------------------------------------------------------------------------
# La declaracion de alcance de la Familia C (§15.6)
# ---------------------------------------------------------------------------
# EL TEXTO ES EL QUE CN REDACTO EN §15.6.2 Y EL VEHICULO EL QUE CN MIDIO. Las
# otras dos opciones se descartaron por razones medidas, no de estilo:
#
#   `bloque_acotaciones` no puede llevarla por DOS motivos y cada uno basta.
#   Mecanico: `M11.acotaciones_declaradas()` filtra por `vacio_verificado` Y
#   por `valor is not None`, de modo que una acotacion seria invisible
#   exactamente durante todo el nivel de perfil, que es cuando la advertencia
#   hace falta. Y categorico, que es el que manda: acotaciones es «lo que el
#   proyectista adopto donde la norma no dice nada», y aqui la fuente NO
#   calla -- la Sec. 2.3 dice que hay que cumplir algo y el proyecto no lo
#   cumple todavia --. Eso es un diferimiento de una exigencia declarada, no
#   una adopcion sobre un vacio: meterlo ahi seria reetiquetar una deuda como
#   una decision.
#
#   `bloque_umbrales` tampoco: `M11.fundamento_del_umbral` es incondicional y
#   un `Fundamento` exige al menos una cita del registro. VC1 no tiene
#   ninguna -- se apoyaria en la Ley 29338 y la DG-2018, fuentes ausentes --,
#   de modo que una entrada de VC1 en `UMBRALES_DE_VERIFICACION` romperia la
#   construccion del bloque.
#
# LO QUE SI LA LLEVA es `bloque_alcance`, que imprime SIEMPRE -- tambien con
# el expediente abierto -- y que no depende de que ningun criterio tenga
# valor. Y es POR PUNTO, de modo que nombra los puntos afectados: es la
# leccion de NOR-HDS-05, un aviso que no señala el punto afectado es el «nadie
# se entera».
# REESCRITA ENTERA AL IMPLEMENTARSE VC1, y no retocada. Su version anterior
# --- la que declaraba la SUSTITUCION del criterio de dimensionamiento ---
# afirmaba cinco cosas que dejaron de ser ciertas de golpe: que «esta corrida
# NO EVALUA ese requisito»; que VC1 «necesita el nivel de agua de diseño del
# canal y su borde libre»; que esos datos «no son columna de la Sec. 1.2 ni
# los aporta ningun tablero»; que VC1 «queda DIFERIDA AL EXPEDIENTE»; y que
# «mientras VC1 no exista» un cumple solo acredita alcantarilla de paso.
#
# NO SE CONSERVA NADA DE AQUEL TEXTO POR PRUDENCIA. Un parrafo de alcance que
# describe un estado del programa que ya no existe se lee con la autoridad de
# una declaracion, y ese es SIS-A-03: es peor que no haberlo escrito, porque
# quien lo lea creera que el canal sigue sin verificarse y no ira a buscar la
# fila VC1 que ahora si trae veredicto. La huella de lo que decia queda en el
# historial y en §16 de `docs/ruta_familia_c.md`, que es donde se lee la
# evolucion; aqui va lo que la corrida hace HOY.
#
# LO QUE SI SOBREVIVE ES LA FORMA DEL ARGUMENTO: nombrar contra que cota mide
# cada umbral, y no dar por conservador lo que no se ha demostrado que lo sea.
# Aplicada ahora a la mitad del requisito que sigue abierta.
DECLARACION_ALCANCE_FAMILIA_C = (
    "ALCANCE DEL REQUISITO DE LA SEC. 2.3 -- FAMILIA C (cruces de canal y "
    "dren). "
    "La Sec. 2.3 de la hoja de ruta enuncia, para la Familia C, un requisito "
    "que ninguna otra familia tiene: la obra NO PUEDE ALTERAR LA RASANTE "
    "HIDRAULICA NI EL BORDE LIBRE DEL CANAL. Son DOS exigencias en una frase, "
    "y esta corrida evalua UNA. "
    "LO QUE SI SE EVALUA -- el borde libre. La verificacion VC1 compara el "
    "nivel que el agua alcanza a la entrada (cota del fondo del canal en el "
    "cruce mas la carga HW que gobierna) contra la coronacion del canal menos "
    "su borde libre, y emite veredicto con margen en metros. La coronacion es "
    "columna del CSV -- `cota_coronacion_canal`, dato de sitio [S] del "
    "levantamiento de los cruces -- y el borde libre sale del criterio "
    "'borde_libre_canal_m' [A]. Sin cualquiera de los dos VC1 SE DETIENE: no "
    "devuelve «no evaluable» ni da el requisito por cumplido. "
    "DE DONDE SALE EL BORDE LIBRE, QUE NO ES UN VALOR NORMATIVO DEL CANAL. El "
    "Manual de Hidrologia NO fija borde libre para un canal: barridas sus 225 "
    "paginas, «borde libre» aparece en dos apartados y ninguno tiene por "
    "objeto un canal -- el num. 4.1.1.3.7 b) es de ALCANTARILLAS y es "
    "relativo (>= 25 % de la altura del barril), y el num. 4.1.1.4.1 e) es de "
    "BADENES y mide contra la superficie de rodadura --. El proyecto adopta "
    "el par 0.30-0.50 m del segundo, en su extremo SUPERIOR, que aqui es el "
    "conservador porque el borde libre se resta de la coronacion. Son dos "
    "decisiones del proyectista y no una lectura de la fuente: la ANALOGIA "
    "(de la calzada de un baden a la coronacion de un canal) y la ELECCION "
    "dentro de una banda para la que el Manual no da regla. "
    "LO QUE NO SE EVALUA -- la rasante hidraulica. VC1 acota el NIVEL que el "
    "agua alcanza; no mide EN CUANTO la obra levanta el pelo de agua del "
    "canal respecto del que tendria sin ella. Un punto puede cumplir VC1 con "
    "holgura y haber elevado la rasante hidraulica del canal en una fraccion "
    "apreciable de su calado. Medirlo exige el tirante normal del canal en la "
    "seccion del cruce -- su geometria trapecial (ancho de solera y talud) y "
    "su n de Manning, ninguno de los dos columna de la Sec. 1.2 -- y la "
    "extension aguas arriba del remanso, que VC1 tampoco acota: mide EN LA "
    "SECCION DEL CRUCE, de modo que un tercero situado mas arriba, donde el "
    "canal tenga la coronacion mas baja, puede quedar afectado por un remanso "
    "que en el cruce cumple. "
    "V5 NO SE EVALUA EN ESTA FAMILIA, y no por falta de datos: por no "
    "aplicar. Su umbral es el ancho del derecho de via y presupone agua "
    "extendiendose lateralmente sobre la plataforma al remansarse contra el "
    "terraplen; en un paso de canal el agua sube confinada entre las dos "
    "coronaciones. VC1 ocupa su posicion en la tabla de la Fase 5 y mide "
    "contra la cota que si gobierna. La sustitucion no pierde alcance -- el "
    "umbral de V5 era un ancho, no una longitud aguas arriba -- pero tampoco "
    "cierra el hueco entero, y por eso el parrafo anterior existe. "
    "QUE SIGNIFICA UN «CUMPLE» EN UN PUNTO DE ESTA FAMILIA: que la obra es "
    "admisible como alcantarilla de paso Y que no invade el borde libre "
    "adoptado del canal en la seccion del cruce. NO significa que la "
    "alteracion de la rasante hidraulica del canal se haya medido. "
    "QUE CIERRA ESTA DECLARACION: la geometria de la seccion del canal (ancho "
    "de solera y talud) y su n de Manning en cada cruce, para calcular su "
    "tirante normal y con el la alteracion; y el borde libre que el propio "
    "canal adopto en SU proyecto (ANA o Junta de Usuarios del Bajo Piura), "
    "que sustituiria a la analogia con el baden."
)


def _declarar_alcance_familia_c(informe: InformePunto) -> None:
    """
    La declaracion de §15.6, emitida UNA VEZ por punto de Familia C.

    NO ES UN BLOQUEO DEL EXPEDIENTE y por eso lleva
    `diferido_por_alcance=True`: lo que dice no es que falte un dato para
    seguir, es que hay MEDIA exigencia de la Sec. 2.3 que esta corrida no
    evalua. Sin esa marca contaria ademas como defecto en `Informe.cerrado`,
    que seria contar dos veces la misma deuda.

    SIGUE EMITIENDOSE DESPUES DE VC1, Y ES EL PUNTO. La tentacion al cerrar
    una deuda declarada es retirar su declaracion, y aqui seria un error:
    VC1 cierra la mitad del requisito que habla del BORDE LIBRE y no la que
    habla de la RASANTE HIDRAULICA. Retirar el bloque dejaria una memoria en
    la que un «cumple» de VC1 se lee como el requisito entero satisfecho. Lo
    que cambio no es que el bloque exista: es lo que dice.

    SE EMITE AUNQUE EL PUNTO NO DIMENSIONE, y es deliberado: es justamente
    cuando el revisor necesita saber con que criterio se va a aceptar el punto
    el dia que declare lo que falte.
    """
    informe.bloqueos.append(Bloqueo(
        fase="Fase 5 - Verificaciones",
        etapa="VC1 - alcance del requisito de la Sec. 2.3 (borde libre "
              "verificado; rasante hidraulica, no)",
        tipo=TipoDeBloqueo.DIFERIDO_POR_ALCANCE,
        mensaje=DECLARACION_ALCANCE_FAMILIA_C,
        diferido_por_alcance=True))


def _valor_descartado(valor: float) -> str:
    """
    Un valor RECHAZADO, escrito para que quien lo declaro lo reconozca.

    NO ES EL FORMATO DE UNA MAGNITUD DEL PROYECTO y por eso no es exactamente
    `_fmt`: las magnitudes del expediente se redondean para leerse, pero un
    dato que se devuelve al remitente tiene que ser identificable. Con tres
    decimales a secas, un `1e-05` declarado se imprimiria «0.000» -- que no es
    lo que nadie escribio y no se puede buscar en el JSON --.

    De modo que se usa la precision del documento mientras alcanza, y por
    debajo de ella el numero entero. La auditoria adversarial de C6 lo encontro
    al ver un `1e-05` crudo -- del `repr` de Python -- conviviendo con un
    `0.006` de tres decimales en la misma celda, y hay que decir exactamente
    que cambio y que no: lo que se corrige son los valores QUE EL DOCUMENTO SI
    PUEDE ESCRIBIR, que antes salian con todos sus decimales (`1.23456` en vez
    de `1.235`). Un `1e-05` sigue imprimiendose asi, y a proposito: no hay
    forma de escribirlo con tres decimales sin borrarlo.
    """
    escrito = _fmt(valor)
    # El umbral NO se escribe: se le PREGUNTA a `_fmt`. Un `10.0 ** -3` aqui
    # seria una segunda copia de la precision del volcado, que ya vive en su
    # firma, y las segundas copias divergen. La condicion va en positivo y
    # negada, como la de MAT-D13, para que un NaN caiga del lado seguro.
    if not abs(float(escrito)) > 0 and abs(valor) > 0:
        return f"{valor:g}"
    return escrito


def _completar_s_cauce(informe: InformePunto,
                       externos: DatosExternos) -> None:
    """
    Completa la pendiente del CAUCE cuando la columna va vacia y el tablero
    la declara (Sec. 1.2 + Tablero 3.1).

    POR QUE HACE FALTA UN VEHICULO Y NO BASTA `S_conducto`. Son dos
    magnitudes distintas y V2b compara una contra otra: `resultado.S` es la
    pendiente CON QUE CORRIO EL DISENO -- que `S_conducto` puede fijar -- y
    `punto.S_cauce` la del cauce natural que alimenta el conducto. Igualarlas
    convertiria el indicador de sedimentacion del num. 5.3.3 del HDS-5 en una
    tautologia. Hasta C6 la Familia C no tenia por donde entregar la segunda:
    su columna va vacia por Tablero 3.1 y no habia clave. Medido en C5: un
    punto de Familia C con Q y S_conducto declarados llegaba hasta V2b y se
    detenia ahi con `DatoFaltanteError('S_cauce')`.

    SE SUSTITUYE EL PUNTO Y NO SE ANOTA APARTE, y hay que decir por que: el
    consumidor es `M5.v2b_sedimentacion`, que lee `punto.exigir("S_cauce")`.
    Pasarselo por parametro obligaria a cambiar la firma de una funcion de
    CALCULO para transportar un dato de ENTRADA, que es lo que este frente no
    hace. El punto efectivo va al pipeline; `informe.punto` NO se toca, de
    modo que la tabla de datos de partida sigue mostrando la columna vacia y
    la procedencia se imprime en su propia fila (`M11.DATOS_DECLARADOS`).

    Si la columna trae valor, el externo NO la pisa: una fila del CSV es un
    dato del expediente y un JSON de corrida no lo corrige en silencio --
    pero la memoria NOMBRA la declaracion descartada, porque «no la use» sin
    decirlo deja a quien la escribio mirando una V2b resuelta contra otro
    numero. Y si no hay externo, no pasa nada aqui: quien se detiene es el
    consumidor, con el nombre del dato que falta.
    """
    punto = informe.punto
    declarado = externos.dato(punto.id, "S_cauce")
    if punto.S_cauce is not None:
        # LA COLUMNA GANA, y aun asi se registra. El externo NO la pisa: una
        # fila del CSV es un dato del expediente y un JSON de corrida no lo
        # corrige en silencio. Se anota igual porque la fila de la memoria
        # dice cual es la pendiente EFECTIVA, la que V2b comparo, y «no
        # declarada» sobre un punto que la trae en su columna seria falso.
        #
        # Y SI ADEMAS SE DECLARO UNA, LA MEMORIA LO DICE. Descartar en
        # silencio la declaracion es lo que convierte una precedencia
        # correcta en un resultado inexplicable: quien escribio el JSON ve
        # V2b resuelta contra un numero que no es el suyo y no tiene donde
        # leer por que. No es un error del expediente -- no se detiene nada --
        # pero tampoco es callable.
        origen = "CSV Sec. 1.2, columna S_cauce"
        if declarado is not None:
            origen += (
                f"; se descarto la declaracion externa "
                f"({_valor_descartado(declarado.valor)} m/m, "
                f"{declarado.origen}) porque la columna tiene valor")
        informe.s_cauce = DatoDeclarado("S_cauce", punto.S_cauce, origen)
        return
    if declarado is None:
        return
    informe.s_cauce = declarado
    informe.punto_completado = replace(punto, S_cauce=declarado.valor)


def _compuerta_metodo_h_o(informe: InformePunto, alcance: str) -> None:
    """
    La compuerta de EXT-M-02 (EXT-3; v8 §4.3 enmendada en EXT-0): si el punto
    se dimensiono con el control de SALIDA gobernando y HW/D_salida < 0.75, el
    metodo aproximado de h_o NO esta definido para ese punto --HDS-5 pag.
    impresa 3.24, «should not be used»-- y el HW publicado no es un
    resultado. Se registra como `Bloqueo` «metodo no evaluable»: diferido a
    nivel de perfil (el punto sale dimensionado con HW no evaluable y el
    motivo impreso junto al HW) y NO diferido a nivel de expediente, donde el
    punto no cierra hasta que exista el calculo de remanso (Section 3.5).

    LEE EL MISMO CAMPO QUE EL PASO F4.HO JUZGA (SIS-A-07):
    `ResultadoHidraulico.h_o_fuera_de_rango`, ya filtrado por control
    gobernante en M4. No recalcula nada. Y va DESPUES del bucle de MD a
    proposito: no rechaza el diametro --subir D solo baja HW/D-- sino que
    marca el punto, sea cual sea el D que la Fase 5 acepto.

    DESDE E-A NO SE ALCANZA EN PRODUCCION, y conviene decirlo: M4 llena
    siempre `ResultadoHidraulico.perfil`, y con perfil la aproximacion fuera
    de rango NO se usa --el HW del punto es el del remanso (paso 4.3d) o
    gobierna la entrada--, de modo que la bandera `h_o_fuera_de_rango` queda
    en False y el bloqueo «metodo no evaluable» ya no se produce. La
    compuerta se conserva como GUARDIA del resultado sin perfil, que solo un
    `ResultadoHidraulico` armado a mano puede traer: su rama de expediente y
    su silencio con perfil los fijan `test_ext3_regimen_barril` y
    `test_ea_perfil_lamina` llamandola directamente, para que una mutacion
    que la difiriera siempre no sobreviva. (Hasta E-A tampoco se alcanzaba
    a nivel de expediente, por otra razon: V1/V2 lanzaban antes.)
    """
    if not informe.dimensionado:
        return
    hidraulica = informe.resultado.resultado_hidraulico
    if not hidraulica.h_o_fuera_de_rango:
        return
    exc = MetodoNoEvaluableError(
        que="HW",
        procedimiento=M5.PROCEDIMIENTO_PERFIL_LAMINA,
        motivo=(f"el control de SALIDA gobierna y HW/D_salida = "
                f"{_fmt(hidraulica.HW_sobre_D_salida)} queda por debajo de "
                f"{_fmt(H_O_HW_SOBRE_D_MIN, DECIMALES_FACTOR)}, donde HDS-5 "
                f"(pag. impresa 3.24) dice que la aproximacion "
                f"h_o = max(TW, (y_c + D)/2) no debe usarse; el HW publicado "
                f"no es un resultado del metodo. Subir de diametro solo baja "
                f"HW/D, y por eso no es un incumplimiento"),
        id_punto=informe.punto.id)
    informe.bloqueos.append(replace(
        _bloqueo(FASE_DISENO, "carga HW bajo control de salida (h_o, Sec. 4.3)",
                 exc),
        diferido_por_alcance=alcance in ALCANCES_QUE_DIFIEREN_METODO_NO_EVALUABLE))


def correr_punto(punto: PuntoCritico, externos: DatosExternos,
                 alcance: str = ALCANCE_EXPEDIENTE,
                 hidrologia: Optional[EntradaHidrologica] = None) -> InformePunto:
    """
    El pipeline de un punto, de la Fase 2 a la Fase 10. Cada etapa corre si su
    insumo existe; si no, queda registrada como bloqueo y las que no dependen
    de ella siguen (la Fase 10 no necesita el diametro, por ejemplo).

    Con alcance de perfil, la Fase 5 difiere V5 y V8 (ver
    `_verificador_perfil`) y la Fase 8 no se ejecuta: queda como bloqueo
    diferido con su fundamento (ver `_diferir_fase_8`). Y en los dos alcances,
    tras el bucle de MD, la compuerta de h_o (`_compuerta_metodo_h_o`, EXT-3):
    un punto dimensionado bajo control de salida con HW/D < 0.75 y SIN perfil
    de la lamina lleva el bloqueo «metodo no evaluable», diferido solo a
    nivel de perfil; con el perfil que M4 emite desde E-A, no se alcanza.
    """
    informe = InformePunto(punto=punto)
    # --- T-2 --- La declaracion del acceso de mantenimiento, si la hay: no
    # depende de ninguna fase y se anota antes que nada, para que viaje
    # tambien en el punto que no llega a dimensionarse.
    informe.acceso_mantenimiento = externos.dato(punto.id,
                                                 CLAVE_ACCESO_MANTENIMIENTO)

    if punto.familia is Familia.C:
        _declarar_alcance_familia_c(informe)

    _completar_s_cauce(informe, externos)

    # La Fase 1-bis va DESPUES de la 2 porque el caudal calculado necesita su
    # TR, y se llama aunque la 2 no cierre: el caudal declarado y su aviso se
    # anotan igual (T-1). La durabilidad (T-4) corre para todo punto que pasa
    # la Fase 2, tenga caudal o no: no lo necesita.
    clasificado = _fase_2(informe, externos)
    con_caudal = _fase_hidrologia(informe, externos, hidrologia)
    if clasificado:
        _fase_durabilidad(informe, externos)
    if clasificado and con_caudal:
        _fase_diseno(informe, externos, alcance)
        _compuerta_metodo_h_o(informe, alcance)
        if informe.dimensionado:
            _fase_6(informe)
            _fase_7(informe)
            if _difiere(alcance, "M8_estructural"):
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
    # Por que el minimo de cuantia se aplica entero: E.060 lo deja exceptuar
    # en muros de contencion y este expediente no ejerce la excepcion. Sin
    # esta linea la memoria presentaba el minimo como inexcusable, que es
    # afirmar de la norma algo que la norma no dice (NOR-E060-01).
    notas.append(nota_excepcion_refuerzo_minimo())
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
        tipo=TipoDeBloqueo.DIFERIDO_POR_ALCANCE,
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
           alcance: str = ALCANCE_EXPEDIENTE,
           hidrologia: Optional[EntradaHidrologica] = None) -> Informe:
    """
    Corre el expediente completo: M0 carga el CSV y cada punto recorre el
    pipeline; la Fase 9 corre una vez para el proyecto.

    `alcance` es la bifurcacion declarada de la corrida (--alcance):
    "expediente" (defecto) corre todo como siempre; "perfil" difiere V5, V8,
    la Fase 8 y la Fase 9 al expediente, dejando constancia de cada uno.

    M0 no se protege con `_etapa`: si el CSV no se puede cargar no hay
    expediente que informar, y la excepcion sale al `main`.

    `hidrologia` (T-1) son las dos entradas de la Fase 1-bis, ya cargadas
    por `cargar_hidrologia`, o None. Con ellas, un punto de Familia A o B
    que tenga cuenca puede traer `Q_m3s` vacio y el programa lo calcula; sin
    ellas todo corre exactamente como antes.

    EL REGISTRO DE USOS SE VACIA AL ENTRAR Y SE FOTOGRAFIA AL SALIR (EXT-4,
    EXT-A-01, PC-09). Es la correccion entera del cluster «estado»: los 79
    escritores de uso pasan por tres funciones, de modo que basta vaciar
    aqui y capturar en `Informe.contexto` un `ContextoCorrida` congelado con
    lo que ESTA corrida uso, los valores con que gobierno, sus procedencias y
    el SHA-1 de los MISMOS bytes que M0 leyo. Los cuatro exportadores leen
    de ahi: correr dos veces en el mismo proceso, declarar despues de correr
    o editar el CSV antes de exportar ya no mueven la memoria de una corrida
    que ya paso. No hace falta ningun objeto `Proyecto`.
    """
    ca.reiniciar_usos()
    ds.reiniciar_usos()
    ruta_csv = Path(ruta_csv)
    datos_csv = leer_bytes(ruta_csv)
    puntos = cargar_puntos_de_bytes(
        datos_csv, ruta_csv.name,
        ids_con_caudal_calculable=(frozenset() if hidrologia is None
                                   else hidrologia.ids_calculables()))
    informe = Informe(csv=ruta_csv,
                      generado=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                      alcance=alcance, hidrologia=hidrologia)
    informe.puntos = [correr_punto(punto, externos, alcance, hidrologia)
                      for punto in puntos]
    informe.cabezal = (_cabezal_diferido() if _difiere(alcance, "M9_cabezal")
                       else correr_cabezal())

    _avisar_ids_desconocidos(informe, externos)
    _avisar_cuencas_sin_punto(informe)
    informe.contexto = capturar_contexto(csv_sha1=sha1_de_bytes(datos_csv))
    return informe


def capturar_contexto(*, csv_sha1: str) -> ContextoCorrida:
    """
    La foto del estado del proceso AHORA, como `ContextoCorrida`.

    Lo llama `correr` al salir; es publica para que la suite pueda armar un
    contexto con el estado que acaba de preparar y pasarselo a los bloques de
    M11, en vez de dejar que M11 lea el estado vivo (que es lo que la guardia
    de `tests/test_ext4_contexto_corrida.py` prohibe).

    Los valores efectivos se copian EN PROFUNDIDAD: un dict declarado en
    caliente --- el espesor de pared por material y diametro --- y mutado
    despues no puede mover la memoria de una corrida que ya paso.
    """
    return ContextoCorrida(
        criterios_usados=tuple(ca.criterios_usados()),
        datos_usados=tuple(ds.datos_usados()),
        valores_efectivos={clave: copy.deepcopy(ca.criterio_efectivo(clave).valor)
                           for clave in sorted(ca.CRITERIOS)},
        procedencias=dict(_declaracion.procedencias()),
        declarados_en_caliente=tuple(ca.criterios_declarados_en_caliente()),
        pisados_en_caliente=tuple(ca.criterios_pisados_en_caliente()),
        criterios_sin_valor=tuple(ca.criterios_sin_valor()),
        criterios_opcionales_sin_declarar=tuple(
            ca.criterios_opcionales_sin_declarar()),
        criterios_con_verificacion_pendiente=tuple(
            ca.criterios_con_verificacion_pendiente()),
        csv_sha1=csv_sha1,
        criterios_sha1=sha1_archivo(ARCHIVO_CRITERIOS),
        # Los datos de sitio con que gobierno la corrida y de que archivo
        # salio cada uno (EXT-10): valor copiado en profundidad, como los
        # criterios; el resto de la ficha es lectura estatica de `ds.dato`.
        datos_efectivos={
            clave: DatoEfectivoDeSitio(
                valor=copy.deepcopy(ds.dato_efectivo(clave).valor),
                trazabilidad=ds.dato_efectivo(clave).trazabilidad,
                fecha=ds.fecha_de(clave),
                origen=ds.origen_de(clave),
                declarado_en_caliente=clave in ds.datos_dinamicos())
            for clave in sorted(ds.DATOS_SITIO)},
        datos_declarados_en_caliente=tuple(ds.datos_declarados_en_caliente()),
        datos_pisados_en_caliente=tuple(ds.datos_pisados_en_caliente()),
        datos_sin_valor=tuple(ds.datos_sin_valor()))


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


def _avisar_cuencas_sin_punto(informe: Informe) -> None:
    """
    Una fila del CSV de cuencas cuyo id no esta en el CSV de puntos es una
    cuenca que no se aplico a nada (T-1): mismo defecto y mismo aviso que un
    id desconocido de --datos-externos.
    """
    if informe.hidrologia is None:
        return
    del_csv = {i.punto.id for i in informe.puntos}
    for id_cuenca in sorted(informe.hidrologia.cuencas):
        if id_cuenca in del_csv:
            continue
        informe.cabezal.bloqueos.append(_bloqueo(
            FASE_CARGA, "cuencas declaradas",
            DatoInvalidoError("cuencas", valor=id_cuenca,
                              motivo="el id no esta en el CSV de puntos: su "
                                     "cuenca no se aplico a ninguna obra")))
