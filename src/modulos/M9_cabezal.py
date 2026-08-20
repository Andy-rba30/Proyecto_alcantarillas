"""
M9_cabezal.py
==============
Fase 9 de la hoja de ruta: cabezal y aletas. Cuatro bloques, en el orden en
que la hoja de ruta los escribe:

    9.2  Cargas         cadena sismica DESAGREGADA, Mononobe-Okabe para K_AE,
                        combinaciones AASHTO LRFD y sobrecarga de trasdos
    9.3  Estabilidad    las cinco filas de la tabla de FS de E.050, cada una
                        con su condicion estatica y su condicion sismica
    9.4  Refuerzo       regla del recubrimiento MAYOR entre AASHTO y E.060,
                        cuantias minimas como PISO obligatorio del armado,
                        alternativa ciclopea

Por que la cadena sismica va desagregada
----------------------------------------
Hoy los seis pasos horizontales de Sec. 9.2 dan todos 0.50, y es tentador
escribir `k_h = 0.50` de una vez. Seria un error de trazabilidad, no de
aritmetica: coinciden SOLO porque F_pga y el factor de muro valen 1.0, y esos
dos numeros llegan por caminos distintos: los dos son la ELECCION [A] de una
fila de una tabla [N] (F_PGA_TABLA y FACTOR_MURO_TABLA), y el PGA que abre la
cadena no es ninguna de las dos cosas sino un dato de sitio [S] leido de un
mapa sobre las coordenadas de esta obra. Cuando llegue el
SPT y la clase de sitio se cierre en E, F_pga baja a 0.9 y la cadena entera
se mueve. Con los pasos separados, M11 imprime que paso cambio y por que; con
un 0.50 escrito a mano, no hay nada que recalcular ni que revisar.

    A_s  = F_pga * PGA
    k_h0 = A_s                          (Manual de Puentes, 2.8.1.1.14.2)
    k_h  = factor_muro * k_h0

k_v va aparte a proposito: no deriva de la cadena, es una adopcion propia
([A], criterio 'k_v') y la hoja de ruta lo pone en su propia fila.

Lo que este modulo SI calcula entero
------------------------------------
    * La cadena sismica completa: sus cuatro insumos (el dato de sitio [S]
      'PGA_roca_B' de datos_sitio.py, y los criterios 'F_pga',
      'factor_muro_eleccion' y 'k_v') tienen valor declarado.
    * Mononobe-Okabe: la formula esta implementada y verificada contra su
      caso limite (con k_h = k_v = 0 e i = beta = delta = 0 devuelve
      exactamente tan^2(45 - phi/2)). Lo que falta son sus ANGULOS, no el
      procedimiento.
    * Las cinco verificaciones de FS de Sec. 9.3, a partir de las demandas:
      los umbrales son [N] literales de `constantes_normativas.FS`.
    * La regla del recubrimiento mayor, el PISO de cuantia minima aplicado
      como rho_diseno = max(rho_calculado, rho_minimo) (`cuantia_de_diseno`),
      el espaciamiento maximo y la alternativa en concreto ciclopeo.
    * Las combinaciones AASHTO LRFD de Sec. 9.2 (`factores_de_carga()`), el
      peso propio del cabezal (`peso_propio_cabezal`, 'peso_especifico_
      concreto_kn_m3') y la regla del recubrimiento mayor
      (`recubrimiento_de_diseno`, 'recubrimiento_aashto_mm'): los tres
      criterios [C] se cerraron por verificacion externa contra AASHTO LRFD
      9a ed.

Lo que se detiene, y por que no se rellena
------------------------------------------
    pendiente_relleno_trasdos_i  Los tres angulos que Sec. 9.2 exige "ademas"
    inclinacion_muro_beta        de la cadena sismica para cerrar K_AE. El
    friccion_muro_suelo_delta    cuarto, phi, ya estaba vacio en GEOTECNIA
                                 ('phi_relleno_trasdos').
    punto_aplicacion_...         Mononobe-Okabe da el empuje, no su brazo.
    predimensionamiento_cabezal  H, B, D_f y espesores: Sec. 9 no dimensiona
                                 el cabezal y Sec. 1.2 no trae sus columnas.
    N_cq_N_gammaq_meyerhof       Salen de FIGURAS (2.8.1.3.1.2c-1 y -2), no de
                                 una formula transcribible.
    metodo_estabilidad_global    E4 y E5: el FS esta, el metodo con que
                                 producir el valor a comparar no.
    cortante_alto_muro_...       El escalon de cuantia horizontal minima a
                                 0.0025 de E.060 Art. 11.10.10.2. Su
                                 disparador es una demanda de CORTANTE, y
                                 este modulo no calcula cortante: sale del
                                 diseno bloqueado en la linea siguiente. Se
                                 declara vacio en vez de omitirse -- omitirlo
                                 equivale a aplicar siempre el minimo mas
                                 bajo de los dos que tiene E.060.
    procedimiento_flexion_...    Ya NO es un vacio de dato -- 'procedimiento_
                                 flexion_corte_aashto_sec5' esta citado (phi,
                                 MCFT beta-theta, Vc, Vs, dv). Lo que sigue
                                 deteniendo `diseno_flexion_corte()` es que el
                                 ENSAMBLE (iterar epsilon_s) no esta
                                 implementado todavia: se detiene con
                                 `NotImplementedError`, no con
                                 `CriterioPendienteError`.

Consecuencia practica, la misma de M5 y M8: las funciones de FORMULA son
utilizables hoy mismo pasandoles sus argumentos, y los ENSAMBLES automaticos
(`k_ae_del_proyecto`, `empujes_trasdos`, `geometria_adoptada`) se detienen con
`CriterioPendienteError` hasta que el expediente cierre esos vacios.

Por que la geometria entra por argumento y no solo por criterio
---------------------------------------------------------------
Un cabezal se predimensiona tanteando: se propone B, se verifica volteo y
deslizamiento, se corrige B. Si la unica via a la geometria fuese el criterio
'predimensionamiento_cabezal', tantear obligaria a editar
criterios_adoptados.py en cada iteracion. Por eso toda funcion de calculo
acepta `GeometriaCabezal` explicita, y `geometria_adoptada()` es la unica que
la lee del criterio. Lo que el vacio bloquea no es tantear: es que el cabezal
salga dimensionado del script sin que nadie declare de donde salieron las
dimensiones.

Unidades
--------
SI. Angulos en GRADOS en las interfaces (es como se declaran en
criterios_adoptados y como se escriben en la memoria), convertidos a radianes
dentro de cada funcion. Los nombres lo dicen: `phi_grados`, `psi_grados`.
Unica excepcion, heredada de `constantes_normativas.RECUBRIMIENTO`: los
recubrimientos van en mm, porque el Art. 7.7.1 esta escrito en mm y no entran
en ninguna ecuacion de equilibrio.

Excepciones
-----------
    CriterioPendienteError   cualquiera de los criterios listados arriba.
    DisenoNoFactibleError    Mononobe-Okabe fuera de su dominio de validez
                             (ver `k_ae_mononobe_okabe`).
    DatoInvalidoError        N_s con c = 0 (ver `n_s_zapata_en_talud`).

Uso
---
    from modelos import CondicionAnalisis
    from modulos.M9_cabezal import (cadena_sismica, k_ae_mononobe_okabe,
                                    verificar_volteo)

    cadena = cadena_sismica()                       # los 7 pasos de Sec. 9.2
    K_AE = k_ae_mononobe_okabe(phi_grados=34.0, i_grados=0.0,
                               beta_grados=0.0, delta_grados=0.0,
                               k_h=cadena.k_h, k_v=cadena.k_v)

    v = verificar_volteo(momento_estabilizante=Me, momento_volcante=Mv,
                         condicion=CondicionAnalisis.SISMICO)   # FS >= 1.25
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

import criterios_adoptados as ca
import datos_sitio as ds
from constantes_fisicas import GAMMA_AGUA_KN_M3
from constantes_normativas import (AMBIENTE_CORROSIVO_AUMENTAR,
                                   CARGA_VIVA,
                                   CICLOPEO_FC_MATRIZ_MIN,
                                   CICLOPEO_FRACCION_PIEDRA_MAX,
                                   COMBINACIONES_AASHTO,
                                   CUANTIA_MIN_MURO,
                                   ESPACIAMIENTO_MAX_ABSOLUTO,
                                   ESPACIAMIENTO_MAX_VECES_ESPESOR,
                                   ESPESOR_TEMPERATURA_DOS_CARAS,
                                   FACTOR_MURO_TABLA,
                                   FS, FS_NUMERAL,
                                   NQ_ZAPATA_EN_TALUD,
                                   NUMERAL_C_PHI,
                                   NUMERAL_CICLOPEO,
                                   NUMERAL_COMBINACIONES,
                                   NUMERAL_CUANTIA_MIN,
                                   NUMERAL_ESPACIAMIENTO,
                                   NUMERAL_FACTOR_MURO,
                                   NUMERAL_K_H0,
                                   NUMERAL_RECUBRIMIENTO,
                                   NUMERAL_SOBRECARGA_TRASDOS,
                                   NUMERAL_TEMPERATURA_DOS_CARAS,
                                   NUMERAL_ZAPATA_EN_TALUD,
                                   NUMERAL_ZAPATA_TALUD_E050,
                                   RECUBRIMIENTO,
                                   SECCION_CABEZALES,
                                   SOBRECARGA_TRASDOS_H_EQ)
from modelos import (CadenaSismica, CombinacionCarga, CondicionAnalisis,
                     CriterioPendienteError,
                     CuantiaRefuerzo, DatoInvalidoError, DisenoNoFactibleError,
                     EmpujeMononobeOkabe, EmpujesTrasdos, EstabilidadCabezal,
                     GeometriaCabezal, PasoSismico, RecubrimientoDiseno,
                     ReferenciaNormativa, Verificacion)
from tolerancias import TOL_UMBRAL_NORMATIVO

# --------------------------------------------------------------------------
# Numerales
# --------------------------------------------------------------------------

NUMERAL_9_1 = ReferenciaNormativa(
    seccion_hoja_ruta="Sec. 9.1",
    numeral_norma="EG-2013, Capitulo V, Seccion 503 (concreto estructural), "
                  "num. 503.01, pag. 905",
)
NUMERAL_9_2 = "Sec. 9.2"
NUMERAL_9_3 = "Sec. 9.3 (E.050)"
NUMERAL_MO = "Sec. 9.2 (Mononobe-Okabe)"
NUMERAL_PGA = "Manual de Puentes, Apendice A3, mapa PGA T = 0.0 seg"
NUMERAL_F_PGA = "Manual de Puentes, Tabla 2.4.3.11.2.1.2-1"
NUMERAL_SUBPRESION = "Manual de Puentes num. 2.4.3.8.2"
NUMERAL_FLEXION_CORTE = "Sec. 9.4 (AASHTO LRFD Seccion 5, via Seccion 2.9)"
NUMERAL_REGLA_RECUBRIMIENTO = "Sec. 0.2 (rige el recubrimiento mayor)"
# El Art. 11.10.10.2 NO esta en la hoja de ruta: se cita como pendiente de
# recoger en ella, no como numeral verificado. Ver el criterio
# 'cortante_alto_muro_e060_art_11_10_10_2'.
NUMERAL_CORTANTE_ALTO = ("E.060 Art. 11.10.10.2 (cortante alto) "
                         "- PENDIENTE de recoger en la hoja de ruta")

CALCULADO = "Calculado"
ETIQUETA_CALCULADO = "-"

# --------------------------------------------------------------------------
# Claves de criterios_adoptados
# --------------------------------------------------------------------------

# El PGA no es un criterio: es un dato de sitio [S] y vive en datos_sitio.py.
DATO_SITIO_PGA = "PGA_roca_B"

CRITERIO_F_PGA = "F_pga"
CRITERIO_FACTOR_MURO = "factor_muro_eleccion"
CRITERIO_K_V = "k_v"

CRITERIO_PHI_RELLENO = "phi_relleno_trasdos"
CRITERIO_I_RELLENO = "pendiente_relleno_trasdos_i"
CRITERIO_BETA_MURO = "inclinacion_muro_beta"
CRITERIO_DELTA_MURO = "friccion_muro_suelo_delta"
CRITERIO_BRAZO_SISMICO = "punto_aplicacion_incremento_sismico"

CRITERIO_FACTORES_CARGA = "factores_carga_aashto"
CRITERIO_GAMMA_RELLENO = "peso_especifico_relleno_kn_m3"
CRITERIO_GAMMA_CONCRETO = "peso_especifico_concreto_kn_m3"
CRITERIO_GEOMETRIA = "predimensionamiento_cabezal"
# El NF ya no es criterio: es la columna 'NF_profundidad_m' del CSV, medida en
# cada cruce. Entra por argumento a las funciones que lo necesitan.

CRITERIO_MEYERHOF = "N_cq_N_gammaq_meyerhof"
CRITERIO_ESTABILIDAD_GLOBAL = "metodo_estabilidad_global"
CRITERIO_RECUBRIMIENTO_AASHTO = "recubrimiento_aashto_mm"
CRITERIO_FLEXION_CORTE = "procedimiento_flexion_corte_aashto_sec5"
CRITERIO_CORTANTE_ALTO = "cortante_alto_muro_e060_art_11_10_10_2"

# Componentes de cada combinacion de Sec. 9.2, con la nomenclatura de cargas
# de AASHTO LRFD. Son NOMBRES, no factores: los factores son el vacio que
# declara 'factores_carga_aashto'.
COMPONENTES_COMBINACION = {
    "Resistencia I": ("DC", "EV", "EH", "LS", "WA"),
    "Servicio I": ("DC", "EV", "EH", "LS", "WA"),
    "Evento Extremo I": ("DC", "EV", "EH", "LS", "WA", "EQ"),
}


# ===========================================================================
# 9.2 - CADENA SISMICA DESAGREGADA
# Un paso, una funcion. Ver "Por que la cadena sismica va desagregada".
# ===========================================================================

def pga_roca_b() -> float:
    """
    Paso 1: PGA, aceleracion pico en roca Clase B para Tr = 1000 anios, en g.

    [S] leido del dato de sitio 'PGA_roca_B' -- vive en datos_sitio.py y no en
    constantes_normativas porque, aunque el mapa es normativo, el valor
    depende de la coordenada sobre la que se lea y esa lectura es trazabilidad
    del proyecto (Sec. 9.2, Apendice A3 del Manual de Puentes). Esa frase, que
    este docstring venia diciendo desde el principio, es exactamente la
    definicion de la etiqueta [S]; hasta la quinta etiqueta el valor figuraba
    como [N], que era la unica de las cuatro que no le corresponde.
    """
    return ds.valor(DATO_SITIO_PGA)


def f_pga() -> float:
    """
    Paso 2: F_pga, factor de sitio, adimensional.

    Es la UNICA pieza discutible de la cadena: la Tabla 2.4.3.11.2.1.2-1 es
    [N] (C = 1.0, D = 1.0, E = 0.9 para PGA >= 0.50) pero la ELECCION entre
    sus filas es [A] mientras no haya SPT que cierre la clase de sitio
    (criterio 'F_pga', regla de coherencia de la Sec. 0 preliminar: la tabla
    es [N], la eleccion es [A]).
    """
    return ca.valor(CRITERIO_F_PGA)


def aceleracion_ajustada_sitio(*, PGA: float, F_pga: float) -> float:
    """Paso 3: A_s = F_pga * PGA, en g (Sec. 9.2). Calculado, no declarado."""
    return F_pga * PGA


def coeficiente_sismico_base(*, A_s: float) -> float:
    """
    Paso 4: k_h0 = A_s (Manual de Puentes, num. 2.8.1.1.14.2).

    La igualdad es [N]: no es que k_h0 "se adopte" igual a A_s, es que el
    numeral la establece. Se deja como funcion propia y no como alias para
    que la memoria pueda citar el numeral en su fila de la tabla.
    """
    return A_s


def factor_muro() -> float:
    """
    Paso 5: factor de reduccion por desplazamiento admisible del muro
    (num. 2.8.1.1.14.2), adimensional.

    La TABLA es [N] y esta en `constantes_normativas.FACTOR_MURO_TABLA`: el
    numeral fija sus dos filas (rigido = 1.0, desplazable = 0.5, esta ultima
    el caso k_h = 0.5 * k_h0 = 0.25 de los muros que admiten 25-50 mm). Cual
    de las dos aplica a ESTE cabezal no lo dice el numeral: lo dice como se
    disena el cabezal, y por eso la ELECCION es [A] y se lee del criterio
    'factor_muro_eleccion' (empotrado en el terraplen, sin desplazamiento
    admisible garantizado -> fila rigida, sin reduccion). Es el mismo reparto
    tabla/eleccion que ya tenian `F_PGA_TABLA` y el criterio 'F_pga'.
    """
    elegido = ca.valor(CRITERIO_FACTOR_MURO)
    if elegido not in FACTOR_MURO_TABLA.values():
        raise DatoInvalidoError(
            CRITERIO_FACTOR_MURO, valor=elegido,
            motivo="la eleccion tiene que ser una de las filas de "
                   f"FACTOR_MURO_TABLA ({NUMERAL_FACTOR_MURO}): "
                   f"{FACTOR_MURO_TABLA}",
        )
    return elegido


def coeficiente_sismico_horizontal(*, k_h0: float, factor_muro: float) -> float:
    """Paso 6: k_h = factor_muro * k_h0 (Sec. 9.2). Calculado, no declarado."""
    return factor_muro * k_h0


def coeficiente_sismico_vertical() -> float:
    """
    k_v, coeficiente sismico vertical, adimensional.

    Fuera de la cadena a proposito: no deriva de PGA ni de k_h, es una
    adopcion [A] del criterio 'k_v' (0, "adopcion habitual en muros de baja
    altura") y la hoja de ruta la pone en su propia fila. Su sensibilidad
    declarada contempla 0.5*k_h como escenario alterno.
    """
    return ca.valor(CRITERIO_K_V)


def cadena_sismica() -> CadenaSismica:
    """
    Los seis pasos horizontales de Sec. 9.2 mas k_v, cada uno con su etiqueta
    y su origen, en el orden de la tabla de la hoja de ruta.

    `pasos` es lo que M11 imprime: la cadena entera, no el resultado. Todos
    los insumos tienen valor declarado, asi que esta funcion no se detiene
    hoy por ningun vacio.
    """
    PGA = pga_roca_b()
    Fpga = f_pga()
    A_s = aceleracion_ajustada_sitio(PGA=PGA, F_pga=Fpga)
    k_h0 = coeficiente_sismico_base(A_s=A_s)
    f_muro = factor_muro()
    k_h = coeficiente_sismico_horizontal(k_h0=k_h0, factor_muro=f_muro)
    k_v = coeficiente_sismico_vertical()

    pasos = (
        PasoSismico(simbolo="PGA", valor=PGA,
                    concepto="Aceleracion pico en roca Clase B, Tr = 1000 anios",
                    etiqueta=ds.dato(DATO_SITIO_PGA).etiqueta,
                    origen=NUMERAL_PGA, criterio=DATO_SITIO_PGA),
        PasoSismico(simbolo="F_pga", valor=Fpga,
                    concepto="Factor de sitio",
                    etiqueta=ca.criterio(CRITERIO_F_PGA).etiqueta,
                    origen=NUMERAL_F_PGA, criterio=CRITERIO_F_PGA),
        PasoSismico(simbolo="A_s", valor=A_s,
                    concepto="Aceleracion ajustada por sitio (F_pga * PGA)",
                    etiqueta=ETIQUETA_CALCULADO, origen=CALCULADO),
        PasoSismico(simbolo="k_h0", valor=k_h0,
                    concepto="Coeficiente sismico de base (= A_s)",
                    etiqueta="N", origen=NUMERAL_K_H0),
        PasoSismico(simbolo="factor_muro", valor=f_muro,
                    concepto="Factor de muro (rigido, empotrado)",
                    etiqueta=ca.criterio(CRITERIO_FACTOR_MURO).etiqueta,
                    origen=NUMERAL_K_H0, criterio=CRITERIO_FACTOR_MURO),
        PasoSismico(simbolo="k_h", valor=k_h,
                    concepto="Coeficiente sismico horizontal de diseno",
                    etiqueta=ETIQUETA_CALCULADO, origen=CALCULADO),
        PasoSismico(simbolo="k_v", valor=k_v,
                    concepto="Coeficiente sismico vertical",
                    etiqueta=ca.criterio(CRITERIO_K_V).etiqueta,
                    origen="Adopcion declarada", criterio=CRITERIO_K_V),
    )

    return CadenaSismica(PGA=PGA, F_pga=Fpga, A_s=A_s, k_h0=k_h0,
                         factor_muro=f_muro, k_h=k_h, k_v=k_v,
                         pasos=pasos, numeral=NUMERAL_9_2)


# ===========================================================================
# 9.2 - EMPUJE ACTIVO Y MONONOBE-OKABE
# ===========================================================================

def ka_rankine(*, phi_grados: float) -> float:
    """
    Ka = tan^2(45 - phi/2), el empuje activo que Sec. 9.2 escribe de forma
    literal. Es el caso de Rankine: muro vertical, relleno horizontal y
    friccion muro-suelo nula.

    No sustituye al Ka de Coulomb que devuelve `k_a_coulomb`: cuando i, beta
    o delta no son cero, el coeficiente estatico homogeneo con K_AE es el de
    Coulomb, y restar dos coeficientes de formulaciones distintas para
    obtener el incremento sismico no significa nada. Esta funcion existe
    porque es la formula que la hoja de ruta cita y porque es el patron
    contra el que se contrasta Mononobe-Okabe en su caso limite.
    """
    return math.tan(math.radians(45 - phi_grados / 2)) ** 2   # literal-ok: Ka = tan^2(45 - phi/2), Sec. 9.2


def angulo_inercia_sismica(*, k_h: float, k_v: float) -> float:
    """
    psi = arctan[k_h / (1 - k_v)], en GRADOS: el angulo con que la resultante
    de las fuerzas de inercia se aparta de la vertical. Es el unico punto por
    donde la cadena sismica entra en Mononobe-Okabe.

    Se usa atan2 y no una division: con k_v = 1 (aceleracion vertical igual a
    g, fisicamente absurdo pero declarable por error en un criterio) la
    division reventaria con ZeroDivisionError -- un fallo de programa, no del
    expediente. atan2 devuelve 90 grados y el caso se rechaza mas adelante,
    donde cos(psi) = 0 hace degenerar el denominador de K_AE, con un
    DisenoNoFactibleError que si explica que pasa.
    """
    return math.degrees(math.atan2(k_h, 1 - k_v))


def k_ae_mononobe_okabe(*, phi_grados: float, i_grados: float,
                        beta_grados: float, delta_grados: float,
                        k_h: float, k_v: float) -> float:
    """
    K_AE por Mononobe-Okabe (Sec. 9.2), adimensional.

                    cos^2(phi - psi - beta)
    K_AE = ----------------------------------------------------------
           cos(psi) cos^2(beta) cos(delta + beta + psi) [1 + R]^2

                 /  sen(phi + delta) sen(phi - psi - i)
    con   R = _ /  --------------------------------------
             V    cos(delta + beta + psi) cos(i - beta)

    Convenciones de angulo, que son la mitad del riesgo de esta formula:
        phi   friccion interna del relleno
        psi   arctan[k_h/(1-k_v)], de `angulo_inercia_sismica`
        i     pendiente del relleno sobre la HORIZONTAL
        beta  inclinacion del trasdos sobre la VERTICAL, positiva cuando el
              muro se aleja del relleno
        delta friccion muro-suelo

    Caso limite verificado en los tests: con k_h = k_v = 0 y
    i = beta = delta = 0, esta expresion devuelve exactamente
    tan^2(45 - phi/2), el Ka de Rankine que cita Sec. 9.2. Es la comprobacion
    que garantiza que los signos estan bien puestos.

    Dominio de validez. La formula tiene solucion real solo si
    phi - psi - i >= 0: por debajo de ese limite la cuna activa no encuentra
    equilibrio y K_AE no existe (no es que salga grande: no existe). Con
    k_h = 0.50 es psi = 26.6 grados, de modo que un relleno inclinado se
    acerca al limite muy rapido -- esa es la razon de la sensibilidad
    violenta que declara el criterio 'pendiente_relleno_trasdos_i'. Los dos
    cosenos del denominador se comprueban aparte por la misma razon. Los tres
    casos salen como `DisenoNoFactibleError` con su motivo, nunca como un
    ValueError de math.sqrt ni como un numero enorme sin explicacion.
    """
    psi = math.radians(angulo_inercia_sismica(k_h=k_h, k_v=k_v))
    phi = math.radians(phi_grados)
    i = math.radians(i_grados)
    beta = math.radians(beta_grados)
    delta = math.radians(delta_grados)

    cos_psi = math.cos(psi)
    cos_dbp = math.cos(delta + beta + psi)
    cos_ib = math.cos(i - beta)

    if cos_psi <= 0 or cos_dbp <= 0 or cos_ib <= 0:
        raise DisenoNoFactibleError(
            motivo=(
                "Mononobe-Okabe fuera de su dominio: algun coseno del "
                f"denominador es nulo o negativo (psi = {math.degrees(psi):.2f} "
                f"grados, delta+beta+psi = {math.degrees(delta + beta + psi):.2f}, "
                f"i-beta = {math.degrees(i - beta):.2f}). Revisar los angulos "
                f"declarados y k_v ({NUMERAL_MO})"
            )
        )

    radicando_seno = phi - psi - i
    if radicando_seno < 0:
        raise DisenoNoFactibleError(
            motivo=(
                f"Mononobe-Okabe sin solucion real: phi - psi - i = "
                f"{math.degrees(radicando_seno):.2f} grados < 0 "
                f"(phi = {phi_grados:.2f}, psi = {math.degrees(psi):.2f}, "
                f"i = {i_grados:.2f}). La cuna activa no encuentra equilibrio "
                f"bajo k_h = {k_h:.3f}: no hay K_AE que calcular, hay que "
                f"reducir la pendiente del relleno o revisar phi ({NUMERAL_MO})"
            )
        )

    radicando = (math.sin(phi + delta) * math.sin(radicando_seno)
                 / (cos_dbp * cos_ib))
    R = math.sqrt(max(radicando, 0.0))   # el max solo absorbe -0.0 del producto

    numerador = math.cos(phi - psi - beta) ** 2
    denominador = cos_psi * math.cos(beta) ** 2 * cos_dbp * (1 + R) ** 2
    return numerador / denominador


def k_a_coulomb(*, phi_grados: float, i_grados: float,
                beta_grados: float, delta_grados: float) -> float:
    """
    Coeficiente activo ESTATICO de la misma formulacion de Mononobe-Okabe,
    obtenido haciendo k_h = k_v = 0 (con lo que psi = 0 y la expresion se
    reduce a Coulomb).

    Existe para que `EmpujeMononobeOkabe.incremento` reste dos coeficientes
    homogeneos. Restar K_AE (Mononobe-Okabe, con i, beta y delta) menos Ka de
    Rankine (que ignora los tres) mezclaria dos modelos y daria un incremento
    sismico que no es tal.
    """
    return k_ae_mononobe_okabe(phi_grados=phi_grados, i_grados=i_grados,
                               beta_grados=beta_grados,
                               delta_grados=delta_grados, k_h=0.0, k_v=0.0)


def empuje_mononobe_okabe(*, phi_grados: float, i_grados: float,
                          beta_grados: float, delta_grados: float,
                          k_h: float, k_v: float) -> EmpujeMononobeOkabe:
    """
    K_AE y K_A con todos los angulos que los produjeron, empaquetados para la
    memoria: sin los cuatro angulos el coeficiente no es revisable, porque
    tres de ellos son adopciones del proyectista.
    """
    return EmpujeMononobeOkabe(
        K_AE=k_ae_mononobe_okabe(phi_grados=phi_grados, i_grados=i_grados,
                                 beta_grados=beta_grados,
                                 delta_grados=delta_grados, k_h=k_h, k_v=k_v),
        K_A=k_a_coulomb(phi_grados=phi_grados, i_grados=i_grados,
                        beta_grados=beta_grados, delta_grados=delta_grados),
        psi_grados=angulo_inercia_sismica(k_h=k_h, k_v=k_v),
        phi_grados=phi_grados, i_grados=i_grados,
        beta_grados=beta_grados, delta_grados=delta_grados,
        k_h=k_h, k_v=k_v, numeral=NUMERAL_MO,
    )


def k_ae_del_proyecto() -> EmpujeMononobeOkabe:
    """
    El K_AE del proyecto: cadena sismica declarada mas los cuatro angulos de
    `criterios_adoptados`.

    Se detiene con `CriterioPendienteError` en el primero de los cuatro que
    siga vacio -- hoy los cuatro lo estan ('phi_relleno_trasdos',
    'pendiente_relleno_trasdos_i', 'inclinacion_muro_beta',
    'friccion_muro_suelo_delta'). La formula de arriba SI es utilizable con
    argumentos explicitos: lo que falta son los datos, no el procedimiento.
    """
    cadena = cadena_sismica()
    return empuje_mononobe_okabe(
        phi_grados=ca.valor(CRITERIO_PHI_RELLENO),
        i_grados=ca.valor(CRITERIO_I_RELLENO),
        beta_grados=ca.valor(CRITERIO_BETA_MURO),
        delta_grados=ca.valor(CRITERIO_DELTA_MURO),
        k_h=cadena.k_h, k_v=cadena.k_v,
    )


# ===========================================================================
# 9.2 - EMPUJES SOBRE EL TRASDOS
# ===========================================================================

def aplica_sobrecarga_trasdos(*, distancia_trafico: float, H: float) -> bool:
    """
    Regla de Sec. 9.2 (num. 2.1.4.3.9): la sobrecarga vertical de trasdos
    aplica con trafico a distancia horizontal <= H/2 desde la parte superior
    de la estructura.

    La hoja de ruta anade que "en un cabezal bajo terraplen vial siempre
    aplica" -- ver `sobrecarga_trasdos_siempre_aplica`. Esta funcion existe
    para el caso en que alguien tenga la distancia medida y quiera
    comprobarlo en vez de invocar la regla general.
    """
    return distancia_trafico <= H / 2 + TOL_UMBRAL_NORMATIVO


def sobrecarga_trasdos_siempre_aplica() -> str:
    """
    Declaracion, para la memoria, de que la sobrecarga de trasdos aplica sin
    medir distancia: Sec. 9.2 cierra el punto con "en un cabezal bajo
    terraplen vial SIEMPRE aplica". No es un supuesto de este modulo.
    """
    return (
        f"Sobrecarga de trasdos: aplica siempre en un cabezal bajo terraplen "
        f"vial, con {SOBRECARGA_TRASDOS_H_EQ:.2f} m de relleno equivalente "
        f"y carga viva {CARGA_VIVA} ({NUMERAL_SOBRECARGA_TRASDOS})"
    )


def presion_sobrecarga_trasdos(*, gamma_relleno: float, k_a: float) -> float:
    """
    Presion horizontal constante de la sobrecarga de trasdos, kPa:

        p = gamma * 0.60 * k_a          (num. 2.1.4.3.9, Sec. 9.2)

    El 0.60 es `SOBRECARGA_TRASDOS_H_EQ`, [N] con numeral. La presion es
    uniforme en toda la altura porque la sobrecarga equivale a una altura de
    relleno adicional constante, no a una carga triangular.
    """
    return gamma_relleno * SOBRECARGA_TRASDOS_H_EQ * k_a


def empuje_sobrecarga_trasdos(*, gamma_relleno: float, k_a: float,
                              H: float) -> float:
    """
    Empuje horizontal de la sobrecarga por metro de muro, kN/m: la presion
    uniforme de `presion_sobrecarga_trasdos` por la altura H. Su resultante
    actua a H/2, por ser un diagrama rectangular (geometria, no criterio).
    """
    return presion_sobrecarga_trasdos(gamma_relleno=gamma_relleno, k_a=k_a) * H


def empuje_activo_estatico(*, gamma_relleno: float, k_a: float,
                           H: float) -> float:
    """
    P_A = gamma * H^2 * k_a / 2, kN/m: empuje activo del relleno (Sec. 9.2).
    Diagrama triangular, resultante a H/3 -- el centroide del triangulo, que
    es geometria y no una adopcion (a diferencia del brazo del incremento
    sismico, que si lo es: 'punto_aplicacion_incremento_sismico').
    """
    return gamma_relleno * H ** 2 * k_a / 2


def empuje_activo_sismico_total(*, gamma_relleno: float, K_AE: float,
                                H: float, k_v: float) -> float:
    """
    P_AE = gamma * H^2 * (1 - k_v) * K_AE / 2, kN/m: empuje TOTAL de
    Mononobe-Okabe, estatico mas sismico (Sec. 9.2). El factor (1 - k_v)
    recoge la aceleracion vertical; con el k_v = 0 adoptado vale 1.
    """
    return gamma_relleno * H ** 2 * (1 - k_v) * K_AE / 2


def incremento_sismico(*, gamma_relleno: float, K_AE: float, K_A: float,
                       H: float, k_v: float) -> float:
    """
    Delta P_AE = P_AE - P_A, kN/m: la parte estrictamente sismica del empuje,
    que es la que se suma en la combinacion Evento Extremo I. `K_A` debe ser
    el de `k_a_coulomb` (misma formulacion), no el de Rankine.
    """
    P_AE = empuje_activo_sismico_total(gamma_relleno=gamma_relleno,
                                       K_AE=K_AE, H=H, k_v=k_v)
    P_A = empuje_activo_estatico(gamma_relleno=gamma_relleno, k_a=K_A, H=H)
    return P_AE - P_A


def brazo_incremento_sismico(*, H: float) -> float:
    """
    Altura de aplicacion del incremento sismico sobre la base, en m.

    Se detiene en 'punto_aplicacion_incremento_sismico'
    (`CriterioPendienteError`): Mononobe-Okabe entrega el empuje y NO su punto
    de aplicacion, y sin brazo no hay momento de volteo sismico. El criterio
    guarda la fraccion de H, no la altura, para que sirva a cualquier cabezal.
    """
    return ca.valor(CRITERIO_BRAZO_SISMICO) * H


def altura_agua_sobre_base(*, D_f: float, NF_profundidad_m: float) -> float:
    """
    Altura de agua sobre el nivel de fundacion, en m: la profundidad de
    desplante menos la profundidad del NF, acotada en 0 cuando la zapata queda
    por encima del freatico.

    Sec. 9.2 es explicita: "empuje hidrostatico y subpresion: con NF a 1.4 m
    NO es opcional". El NF entra por argumento porque es la columna
    'NF_profundidad_m' del CSV, medida en el cruce -- dato de sitio [S] que
    varia punto a punto -- y no un criterio unico de proyecto: dos cabezales
    del mismo tramo pueden tener el freatico a profundidades distintas y cada
    uno se calcula con la suya. Quien lo lee de la fila usa
    `punto.exigir("NF_profundidad_m")`, que se detiene con DatoFaltanteError
    si el estudio geotecnico todavia no dio el valor de ese punto.
    """
    return max(D_f - NF_profundidad_m, 0.0)


def empuje_hidrostatico(*, h_agua: float) -> float:
    """
    E_w = gamma_agua * h_agua^2 / 2, kN/m (Sec. 9.2: "empuje hidrostatico y
    subpresion: con NF a 1.4 m no es opcional"). Es hidrostatica pura, no un
    coeficiente de empuje: el agua no tiene angulo de friccion y su empuje no
    se reduce por Ka. Confundirlos (multiplicar el empuje del agua por Ka) es
    el error clasico del trasdos con freatico.
    """
    return GAMMA_AGUA_KN_M3 * h_agua ** 2 / 2


def subpresion(*, h_agua: float, B: float) -> float:
    """
    U = gamma_agua * h_agua * B, kN/m: subpresion bajo la zapata
    (num. 2.4.3.8.2, el mismo numeral de la flotacion de M8).

    Hipotesis declarada: distribucion UNIFORME de valor gamma_agua * h_agua
    en todo el ancho B, es decir, sin alivio por drenaje ni gradiente de
    filtracion bajo la zapata. Es la lectura conservadora -- una distribucion
    con gradiente daria una resultante menor -- y es la coherente con la
    hipotesis de M8 para U ("NF en su cota mas alta"). Un diseno que necesite
    la distribucion real necesita una red de flujo, que no esta en el alcance
    de la hoja de ruta.
    """
    return GAMMA_AGUA_KN_M3 * h_agua * B


def peso_especifico_relleno() -> float:
    """
    Peso especifico del relleno del trasdos, kN/m3, del criterio
    'peso_especifico_relleno_kn_m3' -- el MISMO que usa M8 para el peso sobre
    la clave en V7. Un cabezal calculado con un relleno y un conducto
    verificado con otro seria una incoherencia de expediente.

    Se detiene con `CriterioPendienteError` mientras el criterio siga vacio.
    """
    return ca.valor(CRITERIO_GAMMA_RELLENO)


def peso_propio_cabezal(*, geometria: GeometriaCabezal) -> float:
    """
    Peso propio del cabezal por metro de muro, kN/m: la carga DC de las tres
    combinaciones de Sec. 9.2. Pantalla trapecial mas zapata rectangular.

        W = gamma_c * [ (e_corona + e_base_muro)/2 * H  +  B * e_zapata ]

    Es geometria exacta, no una aproximacion: el area de un trapecio es la
    semisuma de sus bases por la altura. Por eso `GeometriaCabezal` pide los
    DOS espesores de la pantalla -- con uno solo habria que suponer que es
    rectangular, y suponer eso subestima el peso, que aqui es el
    ESTABILIZANTE de volteo y deslizamiento.

    'peso_especifico_concreto_kn_m3' es [C] (AASHTO LRFD Tabla 3.5.1-1,
    23.56 kN/m3): la funcion calcula directo, ya no se detiene aqui.
    """
    gamma_c = ca.valor(CRITERIO_GAMMA_CONCRETO)
    area_pantalla = (geometria.espesor_corona + geometria.espesor_base_muro) / 2 * geometria.H
    area_zapata = geometria.B * geometria.espesor_zapata
    return gamma_c * (area_pantalla + area_zapata)


def empujes_trasdos(*, geometria: GeometriaCabezal,
                    condicion: CondicionAnalisis,
                    altura_empuje: float,
                    NF_profundidad_m: float) -> EmpujesTrasdos:
    """
    Ensambla las cargas horizontales de Sec. 9.2 sobre el trasdos, cada una
    con su brazo sobre la base: empuje activo (EH), sobrecarga de 0.60 m
    equivalente (LS), empuje hidrostatico y subpresion (WA) y, en condicion
    sismica, el incremento de Mononobe-Okabe (EQ).

    `altura_empuje` entra por argumento y NO se deduce de la geometria a
    proposito. La eleccion corriente es `geometria.altura_total`
    (H + espesor de zapata: el relleno actua contra el plano vertical que
    incluye el canto de la zapata), y para eso existe esa propiedad -- pero
    tambien se usa el plano vertical por el talon en muros con zapata larga,
    y son dos modelos distintos con dos resultados distintos. Escoger uno
    aqui y no decirlo seria decidir por el proyectista.

    Que Ka usa el empuje estatico. El de Rankine, tan^2(45 - phi/2), porque
    es el que Sec. 9.2 escribe de forma literal ("empuje de tierras: activo,
    Ka = tan^2(45 - phi/2)"). El incremento sismico, en cambio, se calcula
    homogeneo dentro de Mononobe-Okabe (K_AE - K_A de Coulomb), que es la
    unica resta con sentido. Con i = beta = delta = 0 los dos coeficientes
    estaticos coinciden exactamente y no hay nada que declarar; en cuanto
    alguno de los tres angulos deje de ser cero, difieren, y la memoria tiene
    que decir cual gobierna el empuje estatico. Ambos viajan en el resultado
    (`K_A` de Rankine y `mononobe_okabe.K_A` de Coulomb) para que la
    diferencia sea visible en vez de quedar escondida en una suma.

    Brazos. Los tres estaticos son geometria y no criterio: el empuje activo
    es triangular y su resultante cae en H/3, la sobrecarga es rectangular y
    cae en H/2, y el agua es triangular sobre su propia altura. El brazo del
    incremento sismico NO es geometria -- Mononobe-Okabe da el empuje y no su
    punto de aplicacion -- y sale de 'punto_aplicacion_incremento_sismico'.

    `NF_profundidad_m` entra por argumento, como `altura_empuje`, y por la
    misma razon: es un dato del punto (columna del CSV, dato de sitio [S]
    medido en el cruce), no un criterio de proyecto. Quien llama lo saca de la
    fila con `punto.exigir("NF_profundidad_m")` y se detiene con
    DatoFaltanteError si el estudio geotecnico aun no lo dio para ese punto.

    Se detiene con `CriterioPendienteError` en el primero de los vacios que
    toque: el peso especifico del relleno, los cuatro angulos de K_AE (solo
    en condicion sismica) o el brazo del incremento.
    """
    gamma = peso_especifico_relleno()
    K_A_rankine = ka_rankine(phi_grados=ca.valor(CRITERIO_PHI_RELLENO))

    E_a = empuje_activo_estatico(gamma_relleno=gamma, k_a=K_A_rankine,
                                 H=altura_empuje)
    E_s = empuje_sobrecarga_trasdos(gamma_relleno=gamma, k_a=K_A_rankine,
                                    H=altura_empuje)
    h_agua = altura_agua_sobre_base(D_f=geometria.D_f,
                                    NF_profundidad_m=NF_profundidad_m)
    E_w = empuje_hidrostatico(h_agua=h_agua)
    U = subpresion(h_agua=h_agua, B=geometria.B)

    incremento = None
    z_incremento = None
    mo = None
    if condicion is CondicionAnalisis.SISMICO:
        mo = k_ae_del_proyecto()          # CriterioPendienteError: los 4 angulos
        incremento = incremento_sismico(gamma_relleno=gamma, K_AE=mo.K_AE,
                                        K_A=mo.K_A, H=altura_empuje, k_v=mo.k_v)
        z_incremento = brazo_incremento_sismico(H=altura_empuje)

    return EmpujesTrasdos(
        condicion=condicion,
        altura_empuje=altura_empuje,
        gamma_relleno=gamma,
        E_activo=E_a, z_activo=altura_empuje / 3,   # literal-ok: centroide del triangulo
        E_sobrecarga=E_s, z_sobrecarga=altura_empuje / 2,
        E_hidrostatico=E_w, z_hidrostatico=h_agua / 3,   # literal-ok: centroide del triangulo
        U_subpresion=U,
        K_A=K_A_rankine,
        incremento_sismico=incremento,
        z_incremento=z_incremento,
        mononobe_okabe=mo,
        numeral=NUMERAL_9_2,
    )


# ===========================================================================
# 9.2 - COMBINACIONES AASHTO LRFD
# ===========================================================================

def combinaciones() -> Tuple[CombinacionCarga, ...]:
    """
    Las tres combinaciones de Sec. 9.2 (AASHTO LRFD Sec. 3.4.1, via Manual de
    Puentes num. 2.4.5.3): Resistencia I, Servicio I y Evento Extremo I, con
    las cargas que participan en cada una.

    Describe, no evalua: los nombres estan en el texto normativo citado, los
    factores gamma no. Esta funcion no se detiene -- es la que M11 usa para
    declarar QUE combinaciones rigen aunque el expediente todavia no haya
    transcrito la Tabla 3.4.1-1.
    """
    return tuple(
        CombinacionCarga(nombre=nombre, numeral=NUMERAL_COMBINACIONES,
                         componentes=COMPONENTES_COMBINACION[nombre],
                         criterio_factores=CRITERIO_FACTORES_CARGA)
        for nombre in COMBINACIONES_AASHTO
    )


def factores_de_carga(nombre: str) -> dict:
    """
    Factores gamma de una combinacion, por tipo de carga: Tablas 3.4.1-1 y
    3.4.1-2 de AASHTO LRFD, declaradas en 'factores_carga_aashto' ([C]) y
    anidadas por nombre de combinacion. Los factores de EH y EV son DOBLES
    (maximo y minimo) y cual gobierna depende de si la carga estabiliza o
    desestabiliza cada verificacion: tomar un solo numero por carga da del
    lado inseguro en volteo, por eso el criterio los trae completos y esta
    funcion no elige por quien la llama.
    """
    if nombre not in COMBINACIONES_AASHTO:
        raise DatoInvalidoError(
            campo="combinacion",
            valor=nombre,
            motivo=("no es una de las combinaciones de Sec. 9.2: "
                    + ", ".join(COMBINACIONES_AASHTO)),
        )
    tabla = ca.valor(CRITERIO_FACTORES_CARGA)
    return tabla[nombre]


# ===========================================================================
# 9.3 - ESTABILIDAD (E.050)
# Cinco verificaciones, codigos E1..E5, cada una en las dos condiciones.
# ===========================================================================

def fs_requerido(*, verificacion: str, condicion: CondicionAnalisis) -> float:
    """
    FS de la tabla de Sec. 9.3 para una verificacion y una condicion. [N]
    literal de `constantes_normativas.FS`, sin criterio adoptado de por medio.

    Las claves son las de esa tabla: 'capacidad_portante', 'volteo',
    'deslizamiento', 'estabilidad_global', 'talud'.
    """
    if verificacion not in FS:
        raise DatoInvalidoError(
            campo="verificacion",
            valor=verificacion,
            motivo="no es una fila de la tabla de FS de Sec. 9.3: "
                   + ", ".join(sorted(FS)),
        )
    return FS[verificacion][condicion.value]


def _verificacion_por_fs(*, clave: str, condicion: CondicionAnalisis,
                         fs_obtenido: float, codigo: str) -> Verificacion:
    """
    Arma el `Verificacion` de una fila de Sec. 9.3 comparando el FS obtenido
    contra el de la tabla. La tolerancia se resta del lado ADMISIBLE (que
    aqui es una cota inferior), nunca se suma al obtenido.
    """
    requerido = fs_requerido(verificacion=clave, condicion=condicion)
    return Verificacion(
        cumple=fs_obtenido >= requerido - TOL_UMBRAL_NORMATIVO,
        numeral=FS_NUMERAL[clave],
        valor_obtenido=fs_obtenido,
        valor_admisible=requerido,
        criterio_aplicado=None,          # [N] puro: tabla de Sec. 9.3
        codigo=codigo,
    )


def verificar_capacidad_portante(*, q_actuante: float, q_ultima: float,
                                 condicion: CondicionAnalisis) -> Verificacion:
    """
    E1 - Capacidad portante por falla por corte: FS = q_ultima / q_actuante
    >= 3.00 estatico / 2.50 sismico (E.050 Art. 21.1/21.2).

    `q_ultima` tiene que venir de `capacidad_portante_zapata_en_talud` y no de
    una formula de terreno horizontal: Sec. 9.3 es taxativa en que el cabezal
    se apoya en el borde del terraplen (ver esa funcion).
    """
    if q_actuante <= 0:
        raise DatoInvalidoError(
            campo="q_actuante", valor=q_actuante,
            motivo="la presion de contacto tiene que ser positiva para que "
                   "el FS de capacidad portante exista",
        )
    return _verificacion_por_fs(clave="capacidad_portante", condicion=condicion,
                                fs_obtenido=q_ultima / q_actuante, codigo="E1")


def verificar_volteo(*, momento_estabilizante: float,
                     momento_volcante: float,
                     condicion: CondicionAnalisis) -> Verificacion:
    """
    E2 - Volteo, estabilidad interna: FS = M_estabilizante / M_volcante
    >= 1.50 estatico / 1.25 sismico (E.050 num. 39.13.6 a).

    Con M_volcante <= 0 no hay volteo posible y el FS es infinito: se devuelve
    `math.inf` y cumple. Es un caso real (muro sin empuje neto), no una
    division que haya que esconder.
    """
    if momento_volcante <= 0:
        fs = math.inf
    else:
        fs = momento_estabilizante / momento_volcante
    return _verificacion_por_fs(clave="volteo", condicion=condicion,
                                fs_obtenido=fs, codigo="E2")


def verificar_deslizamiento(*, fuerza_resistente: float,
                            fuerza_actuante: float,
                            condicion: CondicionAnalisis) -> Verificacion:
    """
    E3 - Deslizamiento, estabilidad interna: FS = F_resistente / F_actuante
    >= 1.50 estatico / 1.25 sismico (E.050 num. 39.13.6 a).

    La fuerza resistente la calcula el llamador con los parametros que
    devuelve `parametros_resistencia_art20`: en suelo friccionante es
    N * tan(phi_base) con c = 0, en cohesivo es c * B con phi = 0. E.050
    Art. 20 prohibe sumar las dos.

    `fuerza_resistente` debe entrar YA descontada la subpresion en N (ver
    `subpresion`): con NF a 1.4 m, olvidarla sobrestima la normal en la base
    y con ella todo el FS de deslizamiento.
    """
    if fuerza_actuante <= 0:
        fs = math.inf
    else:
        fs = fuerza_resistente / fuerza_actuante
    return _verificacion_por_fs(clave="deslizamiento", condicion=condicion,
                                fs_obtenido=fs, codigo="E3")


def verificar_estabilidad_global(*, condicion: CondicionAnalisis) -> Verificacion:
    """
    E4 - Estabilidad global del muro: FS >= 1.50 estatico / 1.25 sismico
    (E.050 num. 39.13.6 b).

    Se detiene con `CriterioPendienteError` en 'metodo_estabilidad_global'.
    El UMBRAL esta transcrito y `fs_requerido(verificacion="estabilidad_global",
    ...)` lo devuelve hoy mismo; lo que no existe es con que producir el valor
    a comparar -- un FS de estabilidad global sale de un analisis de
    superficies de falla que exige el perfil estratigrafico completo, y ese no
    esta en el CSV de Sec. 1.2.
    """
    fs_requerido(verificacion="estabilidad_global", condicion=condicion)
    ca.valor(CRITERIO_ESTABILIDAD_GLOBAL)   # CriterioPendienteError mientras falte
    raise CriterioPendienteError(
        CRITERIO_ESTABILIDAD_GLOBAL,
        concepto="criterio declarado, pero E4 (estabilidad global de la masa "
                 "que envuelve al muro) queda DIFERIDA al expediente tecnico: "
                 "el FS a comparar sale de un analisis de superficies de "
                 "falla con el perfil estratigrafico completo, que no esta "
                 "en el CSV de Sec. 1.2",
        fuente="analisis del EMS del expediente; verificacion diferida al "
               "expediente tecnico, no omitida",
    )


def verificar_talud(*, condicion: CondicionAnalisis) -> Verificacion:
    """
    E5 - Estabilidad del talud: FS >= 1.50 estatico / 1.25 sismico (E.050
    Art. 30.3).

    Mismo vacio que E4 ('metodo_estabilidad_global') y no el mismo chequeo:
    E4 mira la masa que envuelve al muro, E5 el talud del terraplen que lo
    soporta, y Sec. 9.3 las lista como dos filas con numerales distintos.
    """
    fs_requerido(verificacion="talud", condicion=condicion)
    ca.valor(CRITERIO_ESTABILIDAD_GLOBAL)   # CriterioPendienteError mientras falte
    raise CriterioPendienteError(
        CRITERIO_ESTABILIDAD_GLOBAL,
        concepto="criterio declarado, pero E5 (estabilidad del talud del "
                 "terraplen que soporta al muro) queda DIFERIDA al expediente "
                 "tecnico: mismo vacio de metodo que E4 y no el mismo chequeo "
                 "-- exige el analisis de superficies de falla del EMS",
        fuente="analisis del EMS del expediente; verificacion diferida al "
               "expediente tecnico, no omitida",
    )


def parametros_resistencia_art20(*, c: float, phi_grados: float,
                                 cohesivo: bool) -> Tuple[float, float]:
    """
    Aplica E.050 Art. 20 (pag. 33): en suelos cohesivos phi = 0; en
    friccionantes c = 0. NO SE COMBINAN. Devuelve (c_efectivo, phi_grados).

    `cohesivo` entra por argumento y no se deduce del SUCS de la calicata: la
    hoja de ruta no transcribe ninguna tabla SUCS -> cohesivo/friccionante, y
    los casos de frontera (SC, SM, ML) son precisamente los que decide el
    geotecnista, no una regla de tres lineas. Deducirlo aqui seria rellenar un
    vacio en silencio.
    """
    if cohesivo:
        return c, 0.0
    return 0.0, phi_grados


def n_s_zapata_en_talud(*, B: float, H_s: float, gamma: float,
                        c: float) -> float:
    """
    Numero de estabilidad N_s de la zapata proxima al talud (Manual de
    Puentes num. 2.8.1.3.1.2c):

        N_s = 0            si B <  H_s
        N_s = gamma*H_s/c  si B >= H_s

    Con c = 0 la segunda rama no esta definida. No es un caso raro: E.050
    Art. 20 obliga a c = 0 en todo suelo friccionante, y ahi el caso no se
    resuelve con N_s sino con el abaco de N_gamma_q, que es el vacio del
    criterio 'N_cq_N_gammaq_meyerhof'. Se levanta `DatoInvalidoError` en vez
    de devolver infinito, para que el mensaje diga que hay que hacer.
    """
    if B < H_s:
        return 0.0
    if c <= 0:
        raise DatoInvalidoError(
            campo="c",
            valor=c,
            motivo=("N_s = gamma*H_s/c no esta definido con c = 0 (suelo "
                    f"friccionante, {NUMERAL_C_PHI}). Ese caso se resuelve "
                    f"con el abaco de N_gamma_q: ver el criterio "
                    f"'{CRITERIO_MEYERHOF}' ({NUMERAL_ZAPATA_EN_TALUD})"),
        )
    return gamma * H_s / c


def n_q_zapata_en_talud() -> float:
    """
    N_q = 0.0 para zapata proxima al talud (Manual de Puentes num.
    2.8.1.3.1.2c). [N] literal de `constantes_normativas`.

    Es el unico de los tres factores de capacidad de carga que la hoja de
    ruta entrega como NUMERO, y anularlo no es un detalle: el termino de
    sobrecarga desaparece por completo, que es la forma de escribir la
    perdida de confinamiento del borde del terraplen.
    """
    return NQ_ZAPATA_EN_TALUD


def capacidad_portante_zapata_en_talud(*, B: float, H_s: float,
                                       gamma: float, c: float,
                                       phi_grados: float) -> float:
    """
    q_ultima de una zapata proxima al talud, kPa (Manual de Puentes num.
    2.8.1.3.1.2c, pags. 272-273): N_q = 0.0, y N_c y N_gamma REEMPLAZADOS por
    N_cq y N_gamma_q de las figuras 2.8.1.3.1.2c-1 y -2 (Meyerhof 1957).

    Se detiene con `CriterioPendienteError` en 'N_cq_N_gammaq_meyerhof'. La
    penalizacion es severa por perdida de confinamiento y la hoja de ruta lo
    subraya: "el cabezal se apoya en el BORDE DEL TERRAPLEN, no en terreno
    horizontal". Usar aqui los N_c y N_gamma de terreno horizontal -- que
    cualquier formulario tiene a mano -- es exactamente la sobrestimacion que
    Sec. 9.3 advierte, y por eso este modulo no ofrece via alternativa.

    El vacio se comprueba ANTES que cualquier otra cosa a proposito: con suelo
    friccionante (c = 0 por E.050 Art. 20) `n_s_zapata_en_talud` levantaria
    `DatoInvalidoError` y el mensaje culparia al dato, cuando lo que falta de
    verdad es la lectura de los abacos. N_s se calcula aparte, con esa
    funcion, al ir a leerlos.

    E.050 Art. 30.1-30.2 exige ADEMAS la verificacion por inclinacion de la
    superficie y de la base y el analisis de estabilidad global con la
    estructura cargando el talud: son dos comprobaciones y no una (la "doble
    verificacion" de Sec. 9.3). La segunda es E4/E5.
    """
    ca.valor(CRITERIO_MEYERHOF)   # CriterioPendienteError mientras falte
    raise AssertionError(
        "inalcanzable mientras 'N_cq_N_gammaq_meyerhof' este vacio"
    )


def geometria_adoptada() -> GeometriaCabezal:
    """
    Geometria del cabezal declarada en 'predimensionamiento_cabezal'.

    Se detiene con `CriterioPendienteError` mientras el criterio siga vacio.
    Es la UNICA via a la geometria por criterio: las funciones de calculo la
    aceptan como argumento explicito para permitir el tanteo (ver "Por que la
    geometria entra por argumento" en el docstring del modulo).
    """
    dimensiones = ca.valor(CRITERIO_GEOMETRIA)   # CriterioPendienteError mientras falte
    return GeometriaCabezal(**dimensiones)


def verificar_estabilidad(*, geometria: GeometriaCabezal,
                          condicion: CondicionAnalisis,
                          q_actuante: float, q_ultima: float,
                          momento_estabilizante: float,
                          momento_volcante: float,
                          fuerza_resistente: float,
                          fuerza_actuante: float,
                          incluir_globales: bool = False) -> EstabilidadCabezal:
    """
    Las verificaciones de Sec. 9.3 para UNA condicion, a partir de las
    demandas ya calculadas por el llamador.

    Devuelve E1, E2 y E3, que son las que se resuelven con las fuerzas y
    momentos del cabezal. E4 y E5 solo se incluyen con
    `incluir_globales=True`, y entonces la llamada se detiene con
    `CriterioPendienteError` en 'metodo_estabilidad_global': se deja opcional
    para que el expediente pueda cerrar la estabilidad interna del cabezal
    mientras el analisis de taludes viaja por su cuenta en el EMS, sin que eso
    haga desaparecer las dos filas de la tabla.

    El mismo cabezal se verifica dos veces, una por condicion: no es la misma
    verificacion con otro umbral, cambian tambien las fuerzas (aparece el
    incremento de Mononobe-Okabe).
    """
    verificaciones = [
        verificar_capacidad_portante(q_actuante=q_actuante, q_ultima=q_ultima,
                                     condicion=condicion),
        verificar_volteo(momento_estabilizante=momento_estabilizante,
                         momento_volcante=momento_volcante,
                         condicion=condicion),
        verificar_deslizamiento(fuerza_resistente=fuerza_resistente,
                                fuerza_actuante=fuerza_actuante,
                                condicion=condicion),
    ]
    if incluir_globales:
        verificaciones.append(verificar_estabilidad_global(condicion=condicion))
        verificaciones.append(verificar_talud(condicion=condicion))

    return EstabilidadCabezal(condicion=condicion, geometria=geometria,
                              verificaciones=tuple(verificaciones),
                              numeral=NUMERAL_9_3)


# ===========================================================================
# 9.4 - REFUERZO Y DURABILIDAD
# ===========================================================================

def recubrimiento_e060_mm(*, condicion: str) -> float:
    """
    Recubrimiento minimo de E.060 Art. 7.7.1 (pag. 54), en mm. [N] por la
    excepcion declarada de durabilidad de Sec. 0.2: E.060 Cap. 4 y Art. 7.7
    si aplican, por ser especificacion de MATERIALES y estar calibrados con
    cementos peruanos.

    Condiciones: 'contra_suelo' (70), 'suelo_intemperie_ge_3_4' (50),
    'suelo_intemperie_le_5_8' (40).
    """
    if condicion not in RECUBRIMIENTO:
        raise DatoInvalidoError(
            campo="condicion", valor=condicion,
            motivo="no es una fila del Art. 7.7.1: " + ", ".join(sorted(RECUBRIMIENTO)),
        )
    return float(RECUBRIMIENTO[condicion])


def recubrimiento_aashto_mm(*, condicion: str) -> float:
    """
    Recubrimiento minimo de AASHTO LRFD para la misma condicion, en mm.

    'recubrimiento_aashto_mm' es [C] (AASHTO LRFD Tabla 5.10.1-1, exposicion
    costera, 75 mm en las tres condiciones de E.060): la funcion calcula
    directo, ya no se detiene aqui.
    """
    tabla = ca.valor(CRITERIO_RECUBRIMIENTO_AASHTO)
    if condicion not in tabla:
        raise DatoInvalidoError(
            campo="condicion", valor=condicion,
            motivo=f"no esta en la tabla declarada en '{CRITERIO_RECUBRIMIENTO_AASHTO}'",
        )
    return float(tabla[condicion])


def recubrimiento_de_diseno(*, condicion: str) -> RecubrimientoDiseno:
    """
    Regla de conflicto de Sec. 0.2: **rige el recubrimiento MAYOR entre AASHTO
    y E.060**. Devuelve los dos valores, el adoptado y cual de las dos normas
    gobierna.

    Por que no basta con tomar el de E.060. Sec. 0.2 adopta la Via 1 (AASHTO
    LRFD de extremo a extremo) y declara la durabilidad como EXCEPCION: E.060
    entra, pero no desplaza a AASHTO, se compara con el. Una regla del maximo
    evaluada con un solo operando no es una regla -- por eso esta funcion
    exige los dos lados. Con 'recubrimiento_aashto_mm' cerrado ([C], 75 mm
    por exposicion costera), la regla ya se evalua completa: AASHTO gobierna
    en las tres condiciones de E.060 (70/50/40 mm) porque 75 es mayor en las
    tres.

    Con NF a 1.4 m y suelos salinos, E.060 Art. 7.7.5.1 (ambiente corrosivo)
    es directamente invocable y manda AUMENTAR el resultado; el articulo no
    dice cuanto, y ese aumento se declara aparte (Sec. 3.3).
    """
    e060 = recubrimiento_e060_mm(condicion=condicion)
    aashto = recubrimiento_aashto_mm(condicion=condicion)
    if aashto > e060:
        adoptado, origen = aashto, "AASHTO"
    else:
        adoptado, origen = e060, "E.060"
    return RecubrimientoDiseno(
        condicion=condicion, e060_mm=e060, aashto_mm=aashto,
        adoptado_mm=adoptado, origen=origen,
        criterio_aashto=CRITERIO_RECUBRIMIENTO_AASHTO,
        numeral=f"{NUMERAL_RECUBRIMIENTO} / {NUMERAL_REGLA_RECUBRIMIENTO}",
    )


def aviso_ambiente_corrosivo() -> str:
    """
    Aviso para la memoria: el recubrimiento de `recubrimiento_de_diseno` es el
    MINIMO antes del aumento por ambiente corrosivo. E.060 Art. 7.7.5.1 dice
    "aumentar adecuadamente" y no fija cuanto, asi que el aumento no se
    calcula aqui: se declara.
    """
    return (
        "Recubrimiento: al valor adoptado hay que sumarle el aumento por "
        f"ambiente corrosivo ({AMBIENTE_CORROSIVO_AUMENTAR}), directamente "
        "invocable con NF a 1.4 m y suelos salinos (Sec. 3.3). El articulo "
        "dice 'aumentar adecuadamente' y no fija cuanto: el aumento se "
        "declara en la memoria, no lo calcula este modulo"
    )


def cuantia_minima(*, direccion: str) -> float:
    """
    Cuantia minima de refuerzo de muro, E.060 Art. 14.3.1 (pag. 133):
    horizontal >= 0.0020, vertical >= 0.0015.

    Es un MINIMO OBLIGATORIO, no un dato informativo. Sec. 9.4 lo llama
    "REFERENCIA de cuantias minimas" y el matiz es real pero no significa lo
    que parece: por la Via 1 de Sec. 0.2 el DISENO estructural es de AASHTO
    LRFD Sec. 5, de modo que E.060 no dicta cuanto acero pide la flexion. Lo
    que si hace el Art. 14.3.1, dentro de E.060, es fijar un piso por debajo
    del cual ningun muro se arma, gobierne quien gobierne el
    dimensionamiento. La consecuencia practica esta en `cuantia_de_diseno`:
    el minimo se aplica como rho_diseno = max(rho_calculado, rho_minimo), no
    se imprime al pie de la memoria.

    Escalon del Art. 11.10.10.2 (0.0025 bajo cortante alto): ver
    `cuantia_de_diseno` y el criterio 'cortante_alto_muro_e060_art_11_10_10_2'.
    Este modulo NO calcula cortante, y por eso el escalon queda declarado
    como vacio y no resuelto en silencio.
    """
    if direccion not in CUANTIA_MIN_MURO:
        raise DatoInvalidoError(
            campo="direccion", valor=direccion,
            motivo="las direcciones del Art. 14.3.1 son "
                   + ", ".join(sorted(CUANTIA_MIN_MURO)),
        )
    return CUANTIA_MIN_MURO[direccion]


def verificar_cuantia(*, cuantia_provista: float, direccion: str) -> Verificacion:
    """
    R1 (horizontal) / R2 (vertical): contraste de la cuantia PROVISTA en el
    plano contra el minimo obligatorio de E.060 Art. 14.3.1.

    Es la comprobacion a posteriori, y no sustituye a `cuantia_de_diseno`:
    esta funcion detecta que un armado ya dibujado incumple el minimo, y
    aquella impide que el minimo se pierda al producir el armado. Las dos
    hacen falta -- la cuantia que llega aqui puede venir de un plano que
    nadie paso por `cuantia_de_diseno`.
    """
    minima = cuantia_minima(direccion=direccion)
    codigo = "R1" if direccion == "horizontal" else "R2"
    return Verificacion(
        cumple=cuantia_provista >= minima - TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_CUANTIA_MIN,
        valor_obtenido=cuantia_provista,
        valor_admisible=minima,
        criterio_aplicado=None,          # [N] puro, Art. 14.3.1
        codigo=codigo,
    )


def cuantia_de_diseno(*, cuantia_calculada: float, direccion: str,
                      cortante_alto: bool) -> CuantiaRefuerzo:
    """
    Cuantia de refuerzo ADOPTADA para una direccion del muro:

        rho_diseno = max(rho_calculado, rho_minimo)

    El minimo de E.060 Art. 14.3.1 (pag. 133) es un piso obligatorio y aqui
    es donde se aplica. Antes de esta funcion el modulo tenia el minimo
    transcrito y `verificar_cuantia` para contrastarlo, pero nada que lo
    levantara: un rho calculado por debajo del minimo salia del modulo tal
    cual, y el minimo aparecia en la memoria como una linea al pie. Una
    exigencia que solo se imprime no es una exigencia aplicada.

    `cortante_alto` NO tiene valor por defecto, y es deliberado. E.060 tiene
    dos minimos horizontales -- 0.0020 (Art. 14.3.1) y el escalon del
    Art. 11.10.10.2 bajo demanda de cortante alta -- y elegir el mas bajo
    porque es el unico que la hoja de ruta transcribe seria quedarse con el
    minimo menor por omision. Este modulo NO calcula cortante: el diseno por
    flexion y corte esta bloqueado entero en
    'procedimiento_flexion_corte_aashto_sec5' (AASHTO LRFD Sec. 5, Via 1 de
    Sec. 0.2), asi que no hay Vu con que contestar la pregunta. Se traslada a
    quien llama, que es quien tiene el diseno estructural delante:

        cortante_alto=False  el muro NO esta en la condicion del
                             Art. 11.10.10.2, y quien lo afirma lo justifica
                             en la memoria. Rige el 0.0020 / 0.0015.
        cortante_alto=True   rige el escalon, cuyo valor esta declarado VACIO
                             en 'cortante_alto_muro_e060_art_11_10_10_2':
                             levanta `CriterioPendienteError` y detiene el
                             calculo. Es el comportamiento correcto -- el
                             numero no esta en la hoja de ruta y no se
                             inventa aqui.

    `direccion` es 'horizontal' o 'vertical'. El escalon del Art. 11.10.10.2
    es de la cuantia HORIZONTAL; en vertical, `cortante_alto=True` no cambia
    el minimo del Art. 14.3.1, pero se sigue exigiendo el argumento para que
    la pregunta se conteste una sola vez por muro y no por direccion.
    """
    minima = cuantia_minima(direccion=direccion)      # DatoInvalidoError si no es direccion
    numeral = NUMERAL_CUANTIA_MIN

    if cortante_alto and direccion == "horizontal":
        # CriterioPendienteError mientras el escalon siga sin declarar. No hay
        # rama alternativa a proposito: sin el valor del Art. 11.10.10.2 no se
        # puede armar un muro en esta condicion.
        minima = float(ca.valor(CRITERIO_CORTANTE_ALTO))
        numeral = f"{NUMERAL_CUANTIA_MIN} / {NUMERAL_CORTANTE_ALTO}"

    if cuantia_calculada >= minima - TOL_UMBRAL_NORMATIVO:
        adoptada, gobierna = cuantia_calculada, "calculo"
    else:
        adoptada, gobierna = minima, "minimo_normativo"

    return CuantiaRefuerzo(
        direccion=direccion,
        cuantia_calculada=cuantia_calculada,
        cuantia_minima=minima,
        cuantia_adoptada=adoptada,
        gobierna=gobierna,
        numeral=numeral,
        criterio_cortante_alto=CRITERIO_CORTANTE_ALTO,
    )


def requiere_temperatura_dos_caras(*, espesor: float) -> bool:
    """
    True si hace falta acero por temperatura en AMBAS caras: espesor >= 0.250
    m (250 mm), E.060 Art. 14.8.3. `espesor` en metros.
    """
    return espesor >= ESPESOR_TEMPERATURA_DOS_CARAS - TOL_UMBRAL_NORMATIVO


def nota_temperatura_dos_caras(*, espesor: float) -> str:
    """
    La frase para la memoria y el plano: en que cara o caras va el acero por
    temperatura, con su numeral. No es una verificacion con umbral contra un
    dato del proyecto -- es una regla de detalle que se dispara con el
    espesor -- y por eso sale como texto y no como `Verificacion`.
    """
    if requiere_temperatura_dos_caras(espesor=espesor):
        return (
            f"Acero por temperatura en AMBAS caras: espesor {espesor:.3f} m "
            f">= {ESPESOR_TEMPERATURA_DOS_CARAS:.3f} m "
            f"({NUMERAL_TEMPERATURA_DOS_CARAS})"
        )
    return (
        f"Acero por temperatura en UNA cara: espesor {espesor:.3f} m < "
        f"{ESPESOR_TEMPERATURA_DOS_CARAS:.3f} m ({NUMERAL_TEMPERATURA_DOS_CARAS})"
    )


def espaciamiento_maximo(*, espesor: float) -> float:
    """
    Espaciamiento maximo del refuerzo, en m: min(3h, 0.400 m), E.060
    Art. 14.3.3. `espesor` (h) en metros.
    """
    return min(ESPACIAMIENTO_MAX_VECES_ESPESOR * espesor,
               ESPACIAMIENTO_MAX_ABSOLUTO)


def verificar_espaciamiento(*, espaciamiento: float,
                            espesor: float) -> Verificacion:
    """
    R3: espaciamiento <= min(3h, 400 mm), E.060 Art. 14.3.3. Ambos argumentos
    en metros.
    """
    maximo = espaciamiento_maximo(espesor=espesor)
    return Verificacion(
        cumple=espaciamiento <= maximo + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_ESPACIAMIENTO,
        valor_obtenido=espaciamiento,
        valor_admisible=maximo,
        criterio_aplicado=None,          # [N] puro, Art. 14.3.3
        codigo="R3",
    )


def verificar_ciclopeo(*, fc_matriz: float,
                       fraccion_piedra: float) -> Tuple[Verificacion, ...]:
    """
    R4 / R5: alternativa en concreto ciclopeo, E.060 Art. 22.10 (pags.
    194-195): f'c de la matriz >= 10 MPa y piedra desplazadora <= 30 % del
    volumen. Admitido para muros de gravedad; Sec. 9.4 la llama "opcion
    realista para cabezales pequenos".

    `fc_matriz` en MPa, `fraccion_piedra` en tanto por uno (0.30, no 30).
    """
    return (
        Verificacion(
            cumple=fc_matriz >= CICLOPEO_FC_MATRIZ_MIN - TOL_UMBRAL_NORMATIVO,
            numeral=NUMERAL_CICLOPEO,
            valor_obtenido=fc_matriz,
            valor_admisible=CICLOPEO_FC_MATRIZ_MIN,
            criterio_aplicado=None,
            codigo="R4",
        ),
        Verificacion(
            cumple=fraccion_piedra <= CICLOPEO_FRACCION_PIEDRA_MAX + TOL_UMBRAL_NORMATIVO,
            numeral=NUMERAL_CICLOPEO,
            valor_obtenido=fraccion_piedra,
            valor_admisible=CICLOPEO_FRACCION_PIEDRA_MAX,
            criterio_aplicado=None,
            codigo="R5",
        ),
    )


def diseno_flexion_corte(*, momento: Optional[float] = None,
                         cortante: Optional[float] = None):
    """
    Diseno por flexion y corte del cabezal, AASHTO LRFD Seccion 5 (Sec. 9.4,
    via Manual de Puentes Seccion 2.9, pag. 337).

    El procedimiento (phi, MCFT beta-theta, Vc, Vs, dv) ya esta citado y
    disponible en 'procedimiento_flexion_corte_aashto_sec5'. Lo que falta no
    es el dato: es el ENSAMBLE. Este modulo todavia no implementa el calculo
    iterativo de deformacion unitaria epsilon_s que alimenta beta y theta
    (Art. 5.7.3.4.2), y sin epsilon_s no hay Vc ni Vs que resolver. Se
    detiene a proposito con `NotImplementedError`, para no fingir un
    resultado -- no es el mismo vacio que bloqueaba antes: ya no se puede
    responder "falta declarar el criterio", porque el criterio esta
    declarado.

    Lo que no se hara cuando se implemente, y es la tentacion evidente:
    sustituir el procedimiento por las expresiones de E.060, que si estan a
    mano. Romperia la consistencia carga-resistencia que Sec. 0.2 declara
    RESUELTA -- no se combinan demandas mayoradas por AASHTO con
    resistencias reducidas por E.060.
    """
    ca.valor(CRITERIO_FLEXION_CORTE)   # citado y disponible; ya no lanza CriterioPendienteError
    raise NotImplementedError(
        "'procedimiento_flexion_corte_aashto_sec5' esta citado y disponible "
        "(phi, MCFT beta-theta, Vc, Vs, dv); el ensamble del diseno por "
        "flexion y corte de este modulo (iterar epsilon_s, resolver Vs y "
        "el espaciamiento) todavia no esta implementado"
    )


# ===========================================================================
# 9.1 - Condicion normativa (declarativo, para M11)
# ===========================================================================

def condicion_normativa_cabezal() -> Tuple[str, ...]:
    """
    Lo que Sec. 9.1 obliga a escribir en la memoria sobre el cabezal, incluida
    la precision que la propia hoja de ruta hace contra si misma.
    """
    return (
        f"Cabezales y aletas: concreto estructural EG-2013 Seccion "
        f"{SECCION_CABEZALES} (+504 para el acero). NO tienen partida con "
        f"numeral propio: se pagan bajo el volumen de concreto y el acero. "
        f"Que aparezcan nominados en 503.01 confirma que son elemento "
        f"estandar de terminacion, pero el argumento es mas debil que "
        f"'existe una partida especifica' ({NUMERAL_9_1})",
        "Embocadura: tubo a ras del muro (square edge), coherente con las "
        "constantes HDS-5 adoptadas en Sec. 4.2. Ambas decisiones se mueven "
        "juntas: cambiar el detalle obliga a cambiar las constantes "
        "(Sec. 9.1 y Tablero 2.3)",
        f"Empuje hidrostatico y subpresion: con NF a 1.4 m NO son opcionales "
        f"({NUMERAL_SUBPRESION})",
        f"Zapata proxima al talud: doble verificacion, {NUMERAL_ZAPATA_TALUD_E050} "
        f"y {NUMERAL_ZAPATA_EN_TALUD}. El cabezal se apoya en el borde del "
        f"terraplen, no en terreno horizontal",
        f"Diseno por flexion y corte: {NUMERAL_FLEXION_CORTE}. E.060 no "
        f"gobierna el diseno estructural (Sec. 0.2, Via 1); si gobierna la "
        f"durabilidad y los recubrimientos, con la regla del mayor",
    )
