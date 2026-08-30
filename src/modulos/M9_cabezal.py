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
fila de una tabla [N] (F_PGA_TABLA) o la declaracion [A] de si se aplica la
reduccion que un numeral autoriza -- el factor de muro NO sale de una tabla, y
decir que salia era el defecto NOR-PUE-07 --, y el PGA que abre la
cadena no es ninguna de las dos cosas sino un dato de sitio [S] leido de un
mapa sobre las coordenadas de esta obra. Cuando llegue el
SPT cierre la caracterizacion del sitio en la fila E, F_pga baja a 0.9 y la
cadena entera se mueve. Con los pasos separados, el informe dice que paso
cambio y por que; con un 0.50 escrito a mano, no hay nada que recalcular ni que
revisar. QUIEN LOS IMPRIME es la CLI -- `_lineas_cabezal` y `_cabezal_json` --,
no M11: la memoria de M11 recoge de Fase 9 la declaracion normativa y los
criterios usados, no la tabla de la cadena.

    A_s  = F_pga * PGA
    k_h0 = A_s                          (Manual de Puentes, 2.8.1.1.14.2.1)
    k_h0 = 1.2 * F_pga * PGA            (idem, cimentacion en Clase A o B)
    k_h  = factor_muro * k_h0

Y CADA PASO LLEVA AHORA LA CONDICION QUE SU FUENTE LE PONE. Tres de los siete
la llevaban implicita en el numero, que es como se pierde -- el numero se
revisa, el supuesto no se ve: de que filas de la tabla sale F_pga, en cual de
las dos ramas de k_h0 cae la cimentacion, y cual de los dos regimenes de k_v
rige. `PasoSismico.condicion` las imprime.

k_v va aparte a proposito, pero no por lo que este docstring decia: NO es una
adopcion propia. Lo fija el mismo numeral del que sale k_h0 -- "se asumira
cero... a no ser que" -- y por eso es [N] condicionado. Lo que el criterio
'k_v' declara es cual de los dos regimenes rige, no el numero.

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
      concreto_kn_m3'). La regla del recubrimiento mayor
      (`recubrimiento_de_diseno`) ya NO es de este grupo: su lado AASHTO se
      calcula y depende de dos declaraciones que el expediente no ha hecho
      -- 'categoria_refuerzo_aashto' y 'exposicion_quimica_ems' --, de modo
      que hoy se detiene. Los factores de
      carga ya no son un criterio [C]: las dos tablas del num. 2.4.5.3.1 del
      Manual de Puentes estan transcritas como [N] en constantes_normativas y
      'factores_carga_aashto' [A] declara solo de que FILA de gamma_p cuelga
      cada estructura -- el cabezal, de "Muros y estribos de retencion"
      (1.35/1.00, NOR-PUE-03).

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
from typing import Optional, Sequence, Tuple

import criterios_adoptados as ca
import datos_sitio as ds
from constantes_fisicas import GAMMA_AGUA_KN_M3, PIE_EN_METROS
from constantes_normativas import (AMBIENTE_CORROSIVO_AUMENTAR,
                                   AMBIENTE_CORROSIVO_TEXTO,
                                   CARGA_VIVA,
                                   CLASE_DE_SITIO_COHERENCIA_INTERNA,
                                   CLASE_DE_SITIO_INDETERMINADA,
                                   CLASE_DE_SITIO_POR_QUE_DEJA_DE_DECIRSE,
                                   CLASE_DE_SITIO_QUE_LA_CIERRA,
                                   HOMONIMIA_CLASE_F,
                                   homonimia_como_texto,
                                   CLASE_SITIO_EF_NO_SUPUESTA_MP_TEXTO,
                                   CLASE_SITIO_EF_NO_SUPUESTA_TEXTO,
                                   CLASE_SITIO_INVESTIGACION_TEXTO,
                                   CICLOPEO_DISCREPANCIA_HOJA_RUTA,
                                   CICLOPEO_FC_MATRIZ_MIN_APLICABLE,
                                   CICLOPEO_FRACCION_PIEDRA_MAX,
                                   COMBINACIONES_AASHTO,
                                   CUANTIA_MIN_MURO,
                                   E030_AMBITO_LECTURA,
                                   E030_S5_LECTURA,
                                   E030_S5_TEXTO,
                                   ESPACIAMIENTO_MAX_ABSOLUTO,
                                   ESPACIAMIENTO_MAX_VECES_ESPESOR,
                                   ESPESOR_DOS_CAPAS_REFUERZO,
                                   ESPESOR_TEMPERATURA_DOS_CARAS,
                                   EXCEPCION_DOS_CAPAS_REFUERZO,
                                   EXCEPCION_REFUERZO_MIN_MURO_TEXTO,
                                   EXPOSICION_ESPECIAL,
                                   E030_ART_7_3_TEXTO,
                                   EXCENTRICIDAD_ADMISIBLE_FRACCION_B,
                                   EXCENTRICIDAD_ERRATA_MANUAL,
                                   FACTOR_MURO_CON_REDUCCION,
                                   FACTOR_MURO_DECLARACIONES,
                                   F_PGA_CLASES_EN_ROCA,
                                   F_PGA_EXIGE_ESTUDIO_DE_SITIO,
                                   F_PGA_TABLA,
                                   F_PGA_TABLA_PGA_COLUMNAS,
                                   FS, FS_NUMERAL,
                                   GAMMA_P_MARCA,
                                   HIPOTESIS_EMPUJE_BAJO_NF,
                                   K_AE_ERRATA_MANUAL,
                                   K_H0_FACTOR_ROCA_A_B,
                                   K_H0_ROCA_ERRATA,
                                   K_V_CASO_RESERVADO,
                                   K_V_DECLARACION_PRESCRITO,
                                   K_V_PRESCRITO,
                                   LECTURA_COLUMNA_EXTREMA_ESTRICTA,
                                   LECTURAS_COLUMNA_EXTREMA,
                                   NQ_ZAPATA_EN_TALUD,
                                   NUMERAL_AGUA_TRASDOS_AASHTO,
                                   NUMERAL_C_PHI,
                                   NUMERAL_CICLOPEO,
                                   NUMERAL_CICLOPEO_APLICABLE,
                                   NUMERAL_COMBINACION_4_2_4_4,
                                   NUMERAL_DOS_CAPAS_REFUERZO,
                                   NUMERAL_EXCEPCION_REFUERZO_MIN_MURO,
                                   NUMERAL_EXPOSICION_ESPECIAL,
                                   NUMERAL_PROTECCION_CORROSION,
                                   PROTECCION_CORROSION_TEXTO,
                                   NUMERAL_COMBINACIONES,
                                   NUMERAL_CUANTIA_MIN,
                                   NUMERAL_E030_AMBITO,
                                   NUMERAL_CLASE_SITIO_AASHTO,
                                   NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA,
                                   NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA_MP,
                                   NUMERAL_CLASE_SITIO_INVESTIGACION,
                                   NUMERAL_CLASE_SITIO_MP,
                                   NUMERAL_LICUEFACCION_AASHTO,
                                   NUMERAL_LICUEFACCION_ESPECTRO,
                                   NUMERAL_RESPUESTA_DE_SITIO_AASHTO,
                                   NUMERAL_RESPUESTA_DE_SITIO_MP,
                                   NUMERAL_E030_S5,
                                   NUMERAL_ESPACIAMIENTO,
                                   NUMERAL_E030_ESTRUCTURAS_NO_EDIFICACION,
                                   NUMERAL_EXCENTRICIDAD_ESTATICA,
                                   NUMERAL_EXCENTRICIDAD_SISMICA,
                                   NUMERAL_EXCENTRICIDAD_SISMICA_AASHTO,
                                   NUMERAL_F_PGA_TABLA,
                                   NUMERAL_FACTOR_MURO,
                                   NUMERAL_K_AE_AASHTO,
                                   NUMERAL_K_AE_MANUAL,
                                   NUMERAL_K_H0,
                                   NUMERAL_P_IR,
                                   NUMERAL_PRESION_CONTACTO,
                                   NUMERAL_RECUBRIMIENTO,
                                   NUMERAL_RECUBRIMIENTO_MP,
                                   NUMERAL_SULFATOS,
                                   NUMERAL_SOBRECARGA_TRASDOS,
                                   NUMERAL_SOBRECARGA_TRASDOS_AASHTO,
                                   NUMERAL_SOBRECARGA_TRASDOS_ALTURA,
                                   NUMERAL_SOBRECARGA_TRASDOS_APLICA,
                                   H_EQ_REPARTO_DE_TABLAS,
                                   NUMERAL_TABLA_GAMMA_P,
                                   NUMERAL_TEMPERATURA_DOS_CARAS,
                                   NUMERAL_ZAPATA_EN_TALUD,
                                   NUMERAL_ZAPATA_TALUD_E050,
                                   P_SEIS_COMBINACIONES,
                                   P_SEIS_PISO_ESTATICO,
                                   RECUBRIMIENTO,
                                   RECUBRIMIENTO_AC_UMBRAL_ALTO,
                                   RECUBRIMIENTO_AC_UMBRAL_BAJO,
                                   RECUBRIMIENTO_MP_FACTOR_AC,
                                   RECUBRIMIENTO_MP_EQUIVALENCIA,
                                   RECUBRIMIENTO_MP_MM,
                                   RECUBRIMIENTO_MP_PISO_MM,
                                   REDUCCION_KH_POR_DESPLAZAMIENTO,
                                   SECCION_CABEZALES,
                                   ORIENTACION_PARALELO_AL_TRAFICO,
                                   ORIENTACION_PERPENDICULAR_AL_TRAFICO,
                                   ORIENTACIONES_TABULADAS,
                                   SOBRECARGA_TRASDOS_PISO_MP_M,
                                   H_EQ_BORDE_UMBRAL_M,
                                   H_EQ_ESTRIBO_PERPENDICULAR_FT,
                                   H_EQ_MURO_PARALELO_FT,
                                   SULFATOS,
                                   TABLA_COMBINACIONES_FILAS,
                                   TABLA_GAMMA_P_FILAS)
from modelos import (CIFRAS_FACTOR, CadenaSismica, CasoDemandaSismica,
                     CombinacionCarga, EleccionDeProyecto, Magnitud,
                     TipoDeVeredicto, Umbral, Veredicto, paso,
                     CondicionAnalisis, CuantiaRefuerzo, DatoInvalidoError,
                     DemandaSismicaCabezal, DisenoNoFactibleError,
                     EmpujeMononobeOkabe, EmpujesTrasdos, EstabilidadCabezal,
                     FuerzaInerciaMuro, GeometriaCabezal, PasoSismico,
                     PresionContactoBase, RecubrimientoDiseno,
                     RequisitosDurabilidad,
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
NUMERAL_F_PGA = NUMERAL_F_PGA_TABLA
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
CRITERIO_F_PGA_LECTURA = "F_pga_lectura_columna_extrema"
CRITERIO_FACTOR_MURO = "factor_muro_eleccion"
CRITERIO_K_V = "k_v"
CRITERIO_GAMMA_EQ = "gamma_EQ"

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
CRITERIO_TABLA_RECUBRIMIENTO = "tabla_recubrimiento_aashto_mm"
# Las dos lagunas de las tablas de h_eq de AASHTO 3.11.6.4, que el registro
# declara y que hasta esta sesion se resolvian en duro dentro del modulo.
CRITERIO_H_EQ_BAJO_TABLA = "h_eq_bajo_altura_tabulada"
CRITERIO_H_EQ_BANDA_BORDE = "h_eq_banda_intermedia_borde"
H_EQ_BAJO_TABLA_PRIMERA_FILA = "primera_fila"
H_EQ_BAJO_TABLA_EXTRAPOLAR = "extrapolar_lineal"
H_EQ_BANDA_LEE_COLUMNA_CERO = "columna_cero"
H_EQ_BANDA_INTERPOLA = "interpolar_entre_columnas"

CRITERIO_CATEGORIA_REFUERZO = "categoria_refuerzo_aashto"
CRITERIO_SITUACION_RECUBRIMIENTO = "situacion_recubrimiento_aashto"
CRITERIO_EXPOSICION_QUIMICA = "exposicion_quimica_ems"
CRITERIO_FACTOR_BANDA_AC = "factor_recubrimiento_banda_intermedia_ac"

# Claves obligatorias del dato de sitio 'exposicion_quimica_ems'. Se exigen
# TODAS y presentes: una clave ausente no es una lectura negativa.
CLAVES_ESCALAS_SULFATOS = ("so4_suelo_pct", "so4_agua_ppm")
CLAVE_FILAS_TABLA_4_2 = "tabla_4_2"
NOMBRE_TABLA_4_2 = "Tabla 4.2"
NOMBRE_TABLA_4_4 = "Tabla 4.4"

# La columna de la Tabla 5.10.1-1 que el corpus PERUANO tambien tabula: el
# Manual de Puentes transcribe esa y solo esa ("aceros no protegidas"). Con
# cualquiera de las otras dos, el numero deja de ser [N] y pasa a ser el [C]
# con que la Via 1 de Sec. 0.2 cubre lo que el corpus peruano no tabula.
CATEGORIA_ACERO_SIN_RECUBRIR = "A"
CRITERIO_FLEXION_CORTE = "procedimiento_flexion_corte_aashto_sec5"
CRITERIO_CORTANTE_ALTO = "cortante_alto_muro_e060_art_11_10_10_2"

# Componentes de cada combinacion de Sec. 9.2, con la nomenclatura de cargas
# de AASHTO LRFD. Son NOMBRES, no factores: los factores son [N] y estan en
# `constantes_normativas.TABLA_COMBINACIONES_FILAS` y `TABLA_GAMMA_P_FILAS`.
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


def clases_de_sitio_plausibles() -> Tuple[str, ...]:
    """
    Las FILAS de la Tabla 2.4.3.11.2.1.2-1 sobre las que este proyecto lee el
    factor de sitio ([A], criterio 'F_pga').

    Es el reparto R1 del proyecto -- la tabla es [N], la eleccion de fila es
    [A] -- aplicado por fin a F_pga. El criterio guardaba el RESULTADO (1.0),
    que es el mismo defecto que tenia 'factores_carga_aashto' antes de C03: un
    numero suelto no puede expresar de que filas salio ni que pasa cuando la
    campana geotecnica cierre la clase. Ahora guarda las filas, y el numero
    lo calcula `f_pga`.

    Se rechaza, con `DatoInvalidoError`:
      * una fila que no existe en la tabla;
      * una declaracion vacia;
      * la fila F, que la tabla marca con asterisco y sin factor: elegirla no
        es leer un valor, es leer una exigencia de estudio (Nota 2).
    """
    elegidas = ca.valor(CRITERIO_F_PGA)
    if isinstance(elegidas, str) or not isinstance(elegidas, (tuple, list)):
        raise DatoInvalidoError(
            campo=CRITERIO_F_PGA, valor=elegidas,
            motivo=f"la declaracion tiene que ser la tupla de filas de "
                   f"{NUMERAL_F_PGA_TABLA} sobre las que se lee el factor, "
                   f"no un factor ya resuelto",
        )
    if not elegidas:
        raise DatoInvalidoError(
            campo=CRITERIO_F_PGA, valor=elegidas,
            motivo="no declara ninguna fila: sin fila no hay factor que leer",
        )
    for clase in elegidas:
        if clase not in F_PGA_TABLA:
            raise DatoInvalidoError(
                campo=CRITERIO_F_PGA, valor=clase,
                motivo=f"no es una fila de {NUMERAL_F_PGA_TABLA}: "
                       f"{', '.join(sorted(F_PGA_TABLA))}",
            )
        if F_PGA_EXIGE_ESTUDIO_DE_SITIO in F_PGA_TABLA[clase]:
            raise DatoInvalidoError(
                campo=CRITERIO_F_PGA, valor=clase,
                motivo=f"la fila '{clase}' de {NUMERAL_F_PGA_TABLA} no trae "
                       f"factor: la fuente le pone asterisco en las cinco "
                       f"columnas y su Nota 2 exige investigaciones "
                       f"geotecnicas especificas del sitio y analisis de "
                       f"respuesta dinamica. No hay numero que leer ahi. Si "
                       f"esa es la fila que el expediente se atribuye, "
                       f"entonces lo que hay que declarar no es un factor de "
                       f"tabla sino la adopcion de seguir sin el, que es "
                       f"materia de la premisa abierta y no de este criterio",
            )
    return tuple(elegidas)


def _pga_en_rotulo_extremo(PGA: float) -> bool:
    """
    Si el PGA cae JUSTO sobre uno de los dos rotulos extremos de la tabla de
    F_pga, que son los unicos puntos donde la lectura declarada en
    'F_pga_lectura_columna_extrema' cambia algo.

    Existe para que la condicion que el informe imprime diga la verdad en los dos
    casos: con PGA = 0.50 la lectura del borde gobierna, y con un PGA
    interior no gobierna nada y decir que si seria falso.
    """
    limites = F_PGA_TABLA_PGA_COLUMNAS
    return any(math.isclose(PGA, x, abs_tol=TOL_UMBRAL_NORMATIVO)
               for x in (limites[0], limites[-1]))


def factor_sitio_desde_tabla(*, clase: str, PGA: float,
                             lectura_extremos: str) -> float:
    """
    F_pga de UNA fila de la Tabla 2.4.3.11.2.1.2-1 para un PGA dado, aplicando
    su Nota 1 ("usar linea recta de interpolacion para valores intermedios de
    PGA").

    Los cinco numeros de los rotulos -- 0.10, 0.20, 0.30, 0.40 y 0.50 -- son
    [N]: la tabla los imprime. Lo que la tabla NO resuelve es que hacer con un
    PGA que cae JUSTO en los rotulos extremos, porque los dos son
    desigualdades estrictas: "PGA < 0.10" y "PGA > 0.50". El de este proyecto
    es exactamente 0.50 y por tanto no cae en ninguna columna tabulada
    (NOR-PUE-11). Esa lectura es del proyectista y entra por argumento:

      'limite_inclusive'  las columnas extremas aplican TAMBIEN en su propio
                          limite, de modo que 0.50 lee la ultima columna. Es
                          la lectura corriente y la que este proyecto declara.
      'limite_estricto'   los rotulos se leen al pie de la letra: en 0.50 no
                          hay columna y no hay nada que interpolar, asi que el
                          calculo se DETIENE en vez de elegir una.

    Que la lectura no es neutra se ve en la fila D: con 'limite_inclusive' da
    1.0 y con la columna anterior daria 1.1. Por eso se declara.
    """
    if clase not in F_PGA_TABLA:
        raise DatoInvalidoError(
            campo="clase", valor=clase,
            motivo=f"no es una fila de {NUMERAL_F_PGA_TABLA}",
        )
    if lectura_extremos not in LECTURAS_COLUMNA_EXTREMA:
        raise DatoInvalidoError(
            campo="lectura_extremos", valor=lectura_extremos,
            motivo="la lectura de los rotulos extremos tiene que ser una de "
                   f"{LECTURAS_COLUMNA_EXTREMA}",
        )
    fila = F_PGA_TABLA[clase]
    if F_PGA_EXIGE_ESTUDIO_DE_SITIO in fila:
        # Misma excepcion que en `clases_de_sitio_plausibles` y a proposito:
        # el hecho es el mismo -- se pidio una fila que no trae factor -- y
        # dos excepciones distintas para un mismo hecho obligarian a quien
        # atrapa a saber por cual de las dos puertas entro.
        raise DatoInvalidoError(
            campo="clase", valor=clase,
            motivo=f"la fila '{clase}' de {NUMERAL_F_PGA_TABLA} no tiene "
                   f"factor tabulado: la fuente le pone asterisco en las "
                   f"cinco columnas y su Nota 2 exige estudio de respuesta "
                   f"dinamica de sitio. No hay numero que leer ahi",
        )

    limites = F_PGA_TABLA_PGA_COLUMNAS
    inferior, superior = limites[0], limites[-1]
    if lectura_extremos == LECTURA_COLUMNA_EXTREMA_ESTRICTA and (
            math.isclose(PGA, inferior, abs_tol=TOL_UMBRAL_NORMATIVO)
            or math.isclose(PGA, superior, abs_tol=TOL_UMBRAL_NORMATIVO)):
        raise DisenoNoFactibleError(
            motivo=f"PGA = {PGA:.3f} g cae justo sobre un rotulo extremo de "
                   f"{NUMERAL_F_PGA_TABLA}, y los dos son desigualdades "
                   f"estrictas ('PGA < {inferior}', 'PGA > {superior}'): con "
                   f"la lectura '{lectura_extremos}' no hay columna que leer "
                   f"ni valor entre el que interpolar"
        )

    if PGA <= inferior:
        return fila[0]
    if PGA >= superior:
        return fila[-1]
    for k in range(len(limites) - 1):
        x0, x1 = limites[k], limites[k + 1]
        if x0 <= PGA <= x1:
            y0, y1 = fila[k], fila[k + 1]
            return y0 + (y1 - y0) * (PGA - x0) / (x1 - x0)
    raise DisenoNoFactibleError(              # inalcanzable: los tramos cubren
        motivo=f"PGA = {PGA} fuera de {NUMERAL_F_PGA_TABLA}"   # todo el rango
    )


def f_pga() -> float:
    """
    Paso 2: F_pga, factor de sitio, adimensional.

    Es la ENVOLVENTE de la tabla sobre las filas que 'F_pga' declara
    plausibles: el mayor de sus factores al PGA del proyecto. Mientras la
    campana geotecnica no cierre la clase, adoptar el mayor es la lectura
    conservadora, y con las filas declaradas la memoria puede decir de cuales
    salio -- que es lo que un 1.0 escrito a mano no permitia (NOR-MEM-03).

    Lo que NO hace esta funcion, y hay que decirlo: no decide la clase del
    sitio. La premisa de la Sec. 0.5 -- que el sitio cae en la Clase F de
    AASHTO por licuefaccion -- sigue abierta en el criterio que la declara, y
    el salto de la clasificacion de E.030 a la de AASHTO no lo escribe
    ninguno de los dos documentos (NOR-AAS-02; la discrepancia entre los dos
    esquemas esta transcrita en
    `constantes_normativas.E030_S5_VS_CLASE_F`). Esta funcion lee las filas
    que el proyectista declara; no las deduce.
    """
    PGA = pga_roca_b()
    lectura = lectura_columna_extrema()
    return max(factor_sitio_desde_tabla(clase=clase, PGA=PGA,
                                        lectura_extremos=lectura)
               for clase in clases_de_sitio_plausibles())


def lectura_columna_extrema() -> str:
    """
    Como se leen los dos rotulos extremos de la tabla de F_pga, del criterio
    'F_pga_lectura_columna_extrema' ([A]). Ver `factor_sitio_desde_tabla`.
    """
    lectura = ca.valor(CRITERIO_F_PGA_LECTURA)
    if lectura not in LECTURAS_COLUMNA_EXTREMA:
        raise DatoInvalidoError(
            campo=CRITERIO_F_PGA_LECTURA, valor=lectura,
            motivo=f"tiene que ser una de {LECTURAS_COLUMNA_EXTREMA}",
        )
    return lectura


def aceleracion_ajustada_sitio(*, PGA: float, F_pga: float) -> float:
    """Paso 3: A_s = F_pga * PGA, en g (Sec. 9.2). Calculado, no declarado."""
    return F_pga * PGA


def cimentacion_en_roca() -> bool:
    """
    Si la cimentacion del cabezal cae en las filas de ROCA de la tabla de
    F_pga (Clase A o B), que es la condicion que dispara la clausula de roca
    del num. 2.8.1.1.14.2.1.

    Se resuelve con las MISMAS filas que declara 'F_pga' y no con un criterio
    nuevo: si el proyectista declara que las filas plausibles son C, D y E,
    ya esta diciendo que la cimentacion no es roca. Antes esa afirmacion
    estaba implicita en un 1.0 y la clausula no se implementaba ni se
    descartaba (MAT-O4, NOR-PUE-12); ahora se descarta de forma trazable, y
    el dia que alguien anada A o B a la declaracion la clausula se activa
    sola.

    Una declaracion MIXTA -- filas de roca y de suelo a la vez -- no se
    resuelve por mayoria ni por el lado conservador: son dos ramas distintas
    del numeral y elegir una seria decidir por el proyectista.
    """
    clases = clases_de_sitio_plausibles()
    en_roca = [c for c in clases if c in F_PGA_CLASES_EN_ROCA]
    if en_roca and len(en_roca) != len(clases):
        raise DatoInvalidoError(
            campo=CRITERIO_F_PGA, valor=clases,
            motivo=f"mezcla filas de roca {F_PGA_CLASES_EN_ROCA} con filas de "
                   f"suelo, y {NUMERAL_K_H0} da a cada grupo una expresion "
                   f"distinta de k_h0. Declarar en cual de las dos ramas cae "
                   f"la cimentacion del cabezal",
        )
    return bool(en_roca)


def coeficiente_sismico_base(*, A_s: float, F_pga: float, PGA: float,
                             cimentacion_en_roca: bool) -> float:
    """
    Paso 4: k_h0, coeficiente sismico de base (num. 2.8.1.1.14.2.1,
    `NUMERAL_K_H0`).

    DOS RAMAS, y el repositorio implementaba una sola sin decirlo:

        cimentacion en suelo   k_h0 = F_pga*PGA = A_s
        cimentacion en roca    k_h0 = 1.2 * F_pga * PGA
        (Clase de Sitio A o B)

    La igualdad de la primera rama es [N]: no es que k_h0 "se adopte" igual a
    A_s, es que el numeral la establece ("kh0=FpgaPGA = As donde kh0 es el
    coeficiente de aceleracion sismico horizontal asumiendo que el
    desplazamiento del muro sea cero").

    LA SEGUNDA RAMA SE TOMA DE LA PROSA Y NO DEL PARENTESIS. El Manual
    imprime "(es decir, 1.2 kh0=FpgaPGA)", que leido al pie de la letra daria
    k_h0 = A_s/1.2 -- una reduccion del 17 %, lo contrario de lo que la misma
    frase acaba de decir. Es errata de imprenta y esta declarada entera en
    `constantes_normativas.K_H0_ROCA_ERRATA`, con la ecuacion de AASHTO que
    la resuelve. Es la segunda de las tres erratas del Manual en esta misma
    cadena; las otras estan en `k_ae_mononobe_okabe` y en
    `excentricidad_admisible_sismica`.

    `cimentacion_en_roca` entra por argumento y no se deduce aqui: quien
    quiera la rama del proyecto usa `cimentacion_en_roca()`, que la resuelve
    con las filas declaradas en 'F_pga'.
    """
    if cimentacion_en_roca:
        return K_H0_FACTOR_ROCA_A_B * F_pga * PGA
    return A_s


def factor_muro() -> float:
    """
    Paso 5: factor por el que se multiplica k_h0 segun la deformacion lateral
    admitida al muro (num. 2.8.1.1.14.2.2, `NUMERAL_FACTOR_MURO`),
    adimensional.

    AQUI NO HAY TABLA. Este archivo declaraba `FACTOR_MURO_TABLA` con dos
    filas ("rigido" 1.0 / "desplazable" 0.5) afirmando que "las DOS filas son
    [N]: el numeral las fija". El numeral no presenta ninguna tabla -- en las
    pags. impresas 252-257 del Manual no hay una sola -- y fija UN valor, 0.5,
    de forma PERMISIVA ("kh puede ser reducido a 0.5kh0"). El 1.0 no es una
    fila tabulada: es la AUSENCIA de reduccion, que es la definicion misma de
    k_h0 (NOR-PUE-07).

    Lo que el proyectista declara, entonces, no es una fila sino si aplica o
    no la reduccion que el numeral autoriza. Y no es una decision solo
    tecnica: AASHTO, del que el numeral es traduccion, la condiciona ademas a
    que el movimiento lateral sea "acceptable to the Owner". Este cabezal va
    empotrado en el terraplen y no tiene desplazamiento admisible garantizado,
    de modo que se declara SIN reduccion -- el lado conservador, y el que la
    propia Sec. 9.2 subraya ("no asumirlo en un cabezal empotrado").
    """
    declarado = ca.valor(CRITERIO_FACTOR_MURO)
    if declarado not in FACTOR_MURO_DECLARACIONES:
        raise DatoInvalidoError(
            CRITERIO_FACTOR_MURO, valor=declarado,
            motivo=f"la declaracion tiene que ser una de "
                   f"{FACTOR_MURO_DECLARACIONES} ({NUMERAL_FACTOR_MURO}). El "
                   f"numeral no tabula filas: autoriza una reduccion",
        )
    if declarado == FACTOR_MURO_CON_REDUCCION:
        return REDUCCION_KH_POR_DESPLAZAMIENTO
    return 1.0   # literal-ok: ausencia de reduccion, k_h = k_h0 por definicion


def coeficiente_sismico_horizontal(*, k_h0: float, factor_muro: float) -> float:
    """Paso 6: k_h = factor_muro * k_h0 (Sec. 9.2). Calculado, no declarado."""
    return factor_muro * k_h0


def coeficiente_sismico_vertical() -> float:
    """
    k_v, coeficiente sismico vertical, adimensional.

    ES [N] CONDICIONADO, no una adopcion. El criterio 'k_v' declaraba 0.0 con
    la fuente "practica corriente; no fijado por el Manual de Puentes", y esa
    afirmacion negativa es falsa: el MISMO numeral del que la cadena toma
    k_h0 lo fija ("El coeficiente de aceleracion sismica vertical, kv, se
    asumira cero con el proposito de calcular las presiones laterales del
    terreno, a no ser que...", `NUMERAL_K_H0`). El valor era correcto; la
    cita y
    la etiqueta, no (NOR-PUE-08, MAT-O11, MAT-X4).

    El numeral reserva dos casos -- muro significativamente afectado por
    efectos de alguna falla cercana, y aceleraciones verticales relativamente
    altas simultaneas con la horizontal -- y no cuantifica ninguno ni escribe
    un k_v alternativo para ellos. Lo que el proyecto declara en el criterio
    'k_v' es, por tanto, una de dos cosas:

        la cadena prescrita       -> k_v = K_V_PRESCRITO, que es [N]
        un numero                 -> el caso reservado se da y el proyectista
                                     aporta el valor que el Manual no da

    Cualquier otra cosa es `DatoInvalidoError`. El rango de sensibilidad
    (0.0, 0.5) que el criterio declaraba sugeria una libertad que el numeral
    no concede, y ademas su comentario ("0.5*k_h") no coincidia con su propio
    extremo: con la cadena de hoy 0.5*k_h vale 0.25, no 0.5 (SIS-D-04).
    """
    declarado = ca.valor(CRITERIO_K_V)
    if declarado == K_V_DECLARACION_PRESCRITO:
        return K_V_PRESCRITO
    if isinstance(declarado, bool) or not isinstance(declarado, (int, float)):
        raise DatoInvalidoError(
            CRITERIO_K_V, valor=declarado,
            motivo=f"o se declara '{K_V_DECLARACION_PRESCRITO}' y rige el "
                   f"cero de {NUMERAL_K_H0}, o se declara el numero que "
                   f"corresponde al caso que ese numeral reserva y que no "
                   f"cuantifica. {K_V_CASO_RESERVADO}",
        )
    return float(declarado)


def cadena_sismica() -> CadenaSismica:
    """
    Los seis pasos horizontales de Sec. 9.2 mas k_v, cada uno con su etiqueta,
    su origen y LA CONDICION QUE SU FUENTE LE PONE, en el orden de la tabla de
    la hoja de ruta.

    `pasos` es lo que el informe imprime: la cadena entera, no el resultado. La
    columna nueva es `condicion`: cada eslabon dice bajo que supuesto vale, de
    modo que un revisor pueda comprobar el supuesto y no solo el numero. Los
    tres que mas pesan -- de que filas de la tabla sale F_pga, en que rama de
    k_h0 cae la cimentacion, y que caso de k_v rige -- eran justamente los que
    viajaban implicitos.

    Todos los insumos tienen valor declarado, asi que esta funcion no se
    detiene hoy por ningun vacio.
    """
    PGA = pga_roca_b()
    clases = clases_de_sitio_plausibles()
    lectura = lectura_columna_extrema()
    Fpga = f_pga()
    A_s = aceleracion_ajustada_sitio(PGA=PGA, F_pga=Fpga)
    en_roca = cimentacion_en_roca()
    k_h0 = coeficiente_sismico_base(A_s=A_s, F_pga=Fpga, PGA=PGA,
                                    cimentacion_en_roca=en_roca)
    f_muro = factor_muro()
    k_h = coeficiente_sismico_horizontal(k_h0=k_h0, factor_muro=f_muro)
    k_v = coeficiente_sismico_vertical()
    declarado_muro = ca.valor(CRITERIO_FACTOR_MURO)
    # La etiqueta y la condicion de k_v NO se cablean: dependen de cual de
    # los dos regimenes declaro el criterio. Cableadas, un k_v puesto a mano
    # por el proyectista para el caso reservado salia de la memoria como [N]
    # "exigencia normativa con numeral verificado" y con una condicion que
    # afirmaba lo contrario de lo que acababa de pasar -- el peor error
    # posible de la taxonomia, cometido justo por la funcion que existe para
    # arreglar etiquetas.
    rige_el_cero = ca.valor(CRITERIO_K_V) == K_V_DECLARACION_PRESCRITO
    if rige_el_cero:
        etiqueta_k_v = "N"
        origen_k_v = NUMERAL_K_H0
        condicion_k_v = ("El numeral lo fija en cero salvo muro "
                         "significativamente afectado por efectos de alguna "
                         "falla cercana, o aceleraciones verticales "
                         "relativamente altas simultaneas con la horizontal. "
                         "Ninguno de los dos casos se declara para este "
                         "cabezal, de modo que rige el cero prescrito")
    else:
        etiqueta_k_v = ca.criterio(CRITERIO_K_V).etiqueta
        origen_k_v = "Declarado por el proyectista"
        condicion_k_v = ("El expediente declara que se da uno de los dos "
                         f"casos que {NUMERAL_K_H0} reserva. Para ellos el "
                         "Manual NO escribe ningun k_v, asi que este valor es "
                         "del proyectista y no de la norma")

    pasos = (
        PasoSismico(simbolo="PGA", valor=PGA,
                    concepto="Aceleracion pico en roca Clase B, Tr = 1000 anios",
                    etiqueta=ds.dato(DATO_SITIO_PGA).etiqueta,
                    origen=NUMERAL_PGA, criterio=DATO_SITIO_PGA,
                    condicion="Lectura del mapa sobre las coordenadas de esta "
                              "obra; su reproducibilidad llega hoy hasta el "
                              "distrito"),
        PasoSismico(simbolo="F_pga", valor=Fpga,
                    concepto="Factor de sitio",
                    etiqueta=ca.criterio(CRITERIO_F_PGA).etiqueta,
                    origen=NUMERAL_F_PGA, criterio=CRITERIO_F_PGA,
                    condicion=f"Envolvente de las filas {', '.join(clases)} "
                              f"de la tabla" + (
                                  f"; PGA = {PGA:.2f} g cae justo sobre un "
                                  f"rotulo extremo, que es desigualdad "
                                  f"estricta, y ese borde se lee con "
                                  f"'{lectura}'"
                                  if _pga_en_rotulo_extremo(PGA) else
                                  f"; PGA = {PGA:.2f} g cae dentro de la "
                                  f"tabla y el factor sale de la "
                                  f"interpolacion de su Nota 1")),
        PasoSismico(simbolo="A_s", valor=A_s,
                    concepto="Aceleracion ajustada por sitio (F_pga * PGA)",
                    etiqueta=ETIQUETA_CALCULADO, origen=CALCULADO),
        PasoSismico(simbolo="k_h0", valor=k_h0,
                    concepto="Coeficiente sismico de base",
                    etiqueta="N", origen=NUMERAL_K_H0,
                    condicion=("Rama de roca: k_h0 = 1.2*F_pga*PGA, "
                               "cimentacion en Clase de Sitio A o B"
                               if en_roca else
                               "Rama de suelo: k_h0 = A_s. La rama de roca "
                               "(1.2*F_pga*PGA, Clase de Sitio A o B) queda "
                               "descartada porque ninguna fila declarada en "
                               "'F_pga' es de roca")),
        PasoSismico(simbolo="factor_muro", valor=f_muro,
                    concepto="Factor por deformacion lateral admitida al muro",
                    etiqueta=ca.criterio(CRITERIO_FACTOR_MURO).etiqueta,
                    origen=NUMERAL_FACTOR_MURO, criterio=CRITERIO_FACTOR_MURO,
                    condicion=f"Declaracion '{declarado_muro}'. El numeral no "
                              f"tabula filas: autoriza reducir k_h0 a la "
                              f"mitad si el muro admite 1.0 a 2.0 in o mas de "
                              f"desplazamiento Y el propietario acepta ese "
                              f"movimiento"),
        PasoSismico(simbolo="k_h", valor=k_h,
                    concepto="Coeficiente sismico horizontal de diseno",
                    etiqueta=ETIQUETA_CALCULADO, origen=CALCULADO),
        PasoSismico(simbolo="k_v", valor=k_v,
                    concepto="Coeficiente sismico vertical",
                    etiqueta=etiqueta_k_v, origen=origen_k_v,
                    criterio=CRITERIO_K_V, condicion=condicion_k_v),
    )

    return CadenaSismica(PGA=PGA, F_pga=Fpga, A_s=A_s, k_h0=k_h0,
                         factor_muro=f_muro, k_h=k_h, k_v=k_v,
                         pasos=pasos, numeral=NUMERAL_9_2,
                         clases_de_sitio=clases, cimentacion_en_roca=en_roca)


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
    con un DisenoNoFactibleError que es de la taxonomia.

    POR QUE GUARDA LO RECHAZA, dicho con precision. El texto que ocupaba este
    lugar decia "cos(psi) = 0 hace degenerar el denominador de K_AE", y eso es
    falso en aritmetica de maquina: `math.cos(math.radians(90.0))` vale
    6.123233995736766e-17, que es POSITIVO, de modo que la guarda de cosenos
    no dispara por psi. Con delta = 0 el rechazo lo produce la guarda
    siguiente, la de `phi - psi - i < 0` --- 34 - 90 - 0 = -56 grados ---, y
    su mensaje manda al revisor a "reducir la pendiente del relleno o revisar
    phi" cuando el disparate esta en k_v. Con delta > 0 dispara antes la de
    cosenos, pero por `delta + beta + psi` y no por psi.

    Se deja asi --- ninguna de las dos guardas nombra k_v --- porque las dos
    son correctas para lo que verifican y anadir una tercera que mire k_v
    exigiria un techo declarado para k_v que este expediente no tiene. Lo que
    no puede quedar es el docstring afirmando un mecanismo que no ocurre.
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
    tan^2(45 - phi/2), el Ka de Rankine que cita Sec. 9.2.

    ESE CASO LIMITE NO GARANTIZA LOS SIGNOS, y aqui decia que si (SIS-F-04,
    mitad documental). Con i = beta = delta = 0 los cuatro cosenos son PARES
    y por lo tanto insensibles al signo: de los quince mutantes de signo y
    operador de esta formula, DOCE devuelven el mismo double que el original
    en ese caso --- medido, 0.28271491971777263 para phi = 34 ---, y siete de
    ellos atravesaban la suite entera. Una comprobacion con todos los angulos
    en cero no puede ver una convencion de signo: no hay signo que ver.

    Lo que si los cubre es CP9_MONONOBE_OKABE (tests/fixtures/casos_patron.py),
    tres juegos con phi, i, beta, delta, k_h y k_v todos distintos y todos
    distintos de cero, autoverificados por recomputacion independiente. El
    caso limite se conserva porque prueba otra cosa --- la reduccion a
    Rankine, que es la que cita Sec. 9.2 --- y esa si la prueba.

    EL SIGNO DEL CORCHETE: [1 + R], Y EL MANUAL DE PUENTES IMPRIME [1 - R].
    Hay que decirlo aqui, en el punto de uso, porque un revisor que compare
    esta funcion con la letra impresa de la norma peruana va a creer que
    encontro un error de transcripcion, y "corregirla" rompe la formula.

    El Apendice A11 del Manual (num. A.11.3.1 "Metodo de Mononobe -Okabe",
    pag. impresa 586 / PDF 587) imprime el denominador con signo MENOS. Es
    ERRATA DE IMPRENTA, no una variante peruana:

      * el propio Manual declara transcribir a AASHTO, y AASHTO imprime "+"
        (Art. A11.3.1, ec. A11.3.1-1, pag. impresa 11-145 / PDF 1614);
      * con el menos, K_AE DIVERGE cuando el radicando tiende a 1, y el caso
        limite k_h = k_v = 0 deja de devolver el Ka de Coulomb -- la formula
        se rompe justo donde el Manual la manda coincidir.

    ESTE CODIGO SIGUE A AASHTO, y esa es la decision correcta. La declaracion
    completa, con las dos citas, esta en
    `constantes_normativas.K_AE_ERRATA_MANUAL`, y viaja a la memoria por
    `condicion_normativa_cabezal`. Es la primera de las TRES erratas del
    Manual en esta misma cadena sismica: las otras dos son el parentesis de
    la clausula de roca de k_h0, en `coeficiente_sismico_base`, y el "tercio
    central" del limite de excentricidad, en
    `excentricidad_admisible_sismica` -- la unica de las tres que mueve un
    numero.

    Se reporta contra la hoja de ruta: su Sec. 9.2 remite a Mononobe-Okabe
    sin escribir la formula ni advertir de la errata, de modo que quien la
    lea sin leer este codigo no tiene con que detectarla.

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
    Regla de Sec. 9.2: la sobrecarga vertical de trasdos aplica con trafico a
    distancia horizontal <= H/2 desde la parte superior de la estructura.

    NUMERAL CORREGIDO (NOR-PUE-01, MAT-D5). Esta regla se citaba al num.
    2.1.4.3.9 del Manual de Puentes, que se titula "Aparatos de Apoyo" y va de
    la conexion entre superestructura y subestructura. El texto que la sostiene
    esta en el num. 2.4.2.2 "Cargas de Suelo: EH, ES, y DD", pag. impresa 102:
    "Cuando se prevea trafico a una distancia horizontal, medida desde la parte
    superior de la estructura, menor o igual a la mitad de su altura, las
    presiones seran incrementadas...". El numeral viejo estaba propagado a seis
    puntos del repositorio.

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

    LA SEGUNDA MITAD DEL NUMERAL, que el expediente no declaraba: el 2.4.2.2
    EXIME expresamente del incremento "cuando se diseñe una losa de
    aproximacion soportada en un extremo del puente". Este proyecto no
    proyecta losa de aproximacion en ningun cabezal, de modo que la exencion
    no se invoca y la sobrecarga se aplica; se dice para que un revisor vea
    que la salida existe y que no se tomo.
    """
    return (
        f"Sobrecarga de trasdos: aplica siempre en un cabezal bajo terraplen "
        f"vial, con carga viva {CARGA_VIVA} ({NUMERAL_SOBRECARGA_TRASDOS}). "
        f"El numeral exime del incremento si hay losa de aproximacion; este "
        f"expediente no proyecta ninguna, de modo que la exencion no se invoca"
    )


def h_eq_sobrecarga_trasdos(*, altura_muro_total: float) -> float:
    """
    Altura de suelo equivalente de la sobrecarga viva de trafico, en m.

    Sec. 9.2. Numerales: Manual de Puentes num. 2.4.2.2 (pag. impresa 102) y
    AASHTO LRFD 9a ed. Art. 3.11.6.4 (pag. impresa 3-151).

    LOS DOS RIGEN A LA VEZ Y GOBIERNA EL MAYOR, que es la misma regla del
    mayor de la Sec. 0.2 que este proyecto ya aplica al recubrimiento:

        h_eq = max( piso del Manual , h_eq tabulado por AASHTO )

    El Manual escribe un PISO -- "una sobrecarga vertical NO MENOR QUE la
    equivalente a 0.60 m de altura de relleno" -- y no tabula nada: su
    traduccion de la Sec. 3.11 de AASHTO se corta en el empuje pasivo k_p y no
    tiene subnumeral LS (verificado barriendo las 673 paginas). AASHTO SI
    tabula, por altura del muro, y manda interpolar linealmente entre filas.

    POR QUE ESTA FUNCION PUEDE DETENERSE. Cual de las dos tablas de AASHTO
    aplica depende de la ORIENTACION del muro respecto del trafico, que es un
    dato de sitio de este expediente y todavia no esta declarado. Es la
    resolucion del conflicto vinculante #4 del plan de correcciones: "no hay
    contradiccion sino un dato faltante". Con el dato sin declarar se lanza
    `CriterioPendienteError` -- por la via que `datos_sitio.valor` ya usa, sin
    inventar un camino nuevo -- en vez de aplicar 0.60 m plano, que es lo que
    el expediente venia haciendo y que para un cabezal de 2.0 m con trafico
    perpendicular subestima la sobrecarga en un factor 1.87.

    `altura_muro_total` ES LA ALTURA CON ZAPATA, y no es un detalle: AASHTO lo
    escribe con un `shall` -- "The wall height shall be taken as the distance
    between the surface of the backfill and the bottom of the footing along
    the pressure surface being considered" --. Con `GeometriaCabezal` eso es
    `H + espesor_zapata`. Medirla sin la zapata subestima la altura y, como
    h_eq DECRECE con ella, sobrestima h_eq: conservador, pero es la lectura
    equivocada de la tabla.
    """
    orientacion = ds.valor("orientacion_muro_respecto_al_trafico")
    altura_ft = altura_muro_total / PIE_EN_METROS

    if orientacion == ORIENTACION_PERPENDICULAR_AL_TRAFICO:
        # ANALOGIA DECLARADA [N->]: la Tabla 3.11.6.4-1 es de ESTRIBOS -- su
        # variable se llama "Abutment Height" --, no de muros de contencion.
        # AASHTO no publica tabla para un muro perpendicular al trafico. La
        # analogia va del lado conservador: el propio comentario C3.11.6.4
        # dice que h_eq es MAYOR para un estribo que para un muro.
        puntos = sorted((a, h) for a, h in
                        H_EQ_ESTRIBO_PERPENDICULAR_FT.values())
    elif orientacion == ORIENTACION_PARALELO_AL_TRAFICO:
        borde = ds.valor("distancia_borde_calzada_al_trasdos_m")
        lejos = _columna_de_borde(borde)
        puntos = sorted((f[0], f[2] if lejos else f[1])
                        for f in H_EQ_MURO_PARALELO_FT.values())
    else:
        raise DatoInvalidoError(
            f"orientacion_muro_respecto_al_trafico = {orientacion!r} no es "
            f"una de las dos que AASHTO 3.11.6.4 tabula "
            f"({', '.join(ORIENTACIONES_TABULADAS)}). La fuente no ofrece un "
            f"eje libre de orientacion: ofrece dos binomios acoplados "
            f"(estribo+perpendicular y muro+paralelo) y no hay tabla para "
            f"ningun otro caso")

    h_eq_ft = _interpolar_h_eq(altura_ft, puntos)
    h_eq_aashto = h_eq_ft * PIE_EN_METROS
    # La regla del mayor de Sec. 0.2: el piso peruano y el valor tabulado de
    # AASHTO rigen a la vez.
    return max(SOBRECARGA_TRASDOS_PISO_MP_M, h_eq_aashto)


def _columna_de_borde(borde_m: float) -> bool:
    """
    Cual de las DOS columnas de la Tabla 3.11.6.4-2 aplica. True = la de
    "1.0 ft or Further".

    LA TABLA TIENE DOS COLUMNAS Y NADA EN MEDIO. Sus rotulos son "0.0 ft" y
    "1.0 ft or Further", y la unica interpolacion que AASHTO autoriza es la de
    ALTURAS ("for intermediate wall heights"), entre filas. La banda abierta
    0 < d < 1.0 ft es laguna de la fuente y la cierra un criterio [A] vacio,
    no un redondeo de este modulo: hasta que se declare, el calculo se detiene.

    LA TOLERANCIA DECIDE IGUALDAD, NO LADO SEGURO, y la distincion es el
    hallazgo que la corrigio. Antes la comparacion era
    `borde >= UMBRAL - TOL`, que redondea hacia "lejos" -- la columna de h_eq
    MENOR, o sea el lado RELAJADO --, justo la direccion que los comentarios de
    alrededor condenan. Ahora la tolerancia solo sirve para reconocer los dos
    valores que la tabla SI tabula (0.0 ft y 1.0 ft) pese a la representacion
    binaria; lo que cae de verdad entre ellos no se redondea a ninguno de los
    dos: bloquea.
    """
    if borde_m >= H_EQ_BORDE_UMBRAL_M - TOL_UMBRAL_NORMATIVO:
        return True                       # columna "1.0 ft or Further"
    if borde_m <= TOL_UMBRAL_NORMATIVO:
        if borde_m < -TOL_UMBRAL_NORMATIVO:
            raise DatoInvalidoError(
                campo="distancia_borde_calzada_al_trasdos_m", valor=borde_m,
                motivo="una distancia del trasdos al borde de calzada no "
                       "puede ser negativa")
        return False                      # columna "0.0 ft"
    # La banda abierta: la fuente calla y el criterio esta vacio.
    regla = ca.valor(CRITERIO_H_EQ_BANDA_BORDE)   # VACIO: detiene aqui
    if regla == H_EQ_BANDA_LEE_COLUMNA_CERO:
        return False
    raise DatoInvalidoError(
        campo=CRITERIO_H_EQ_BANDA_BORDE, valor=regla,
        motivo="las lecturas declaradas de la banda 0 < d < 1.0 ft son "
               f"'{H_EQ_BANDA_LEE_COLUMNA_CERO}' y "
               f"'{H_EQ_BANDA_INTERPOLA}'; interpolar entre las dos columnas "
               "exige ademas escribir la regla, que la fuente no da")


def _interpolar_h_eq(altura_ft: float,
                     puntos: Sequence[Tuple[float, float]]) -> float:
    """
    Interpolacion lineal entre filas de una tabla de h_eq, en pies.

    "Linear interpolation shall be used for intermediate wall heights"
    (AASHTO 3.11.6.4). Es EXIGENCIA, con `shall`.

    FUERA DEL RANGO TABULADO la fuente calla y esta funcion NO extrapola:
      - por encima de la ultima fila, esta se rotula ">=20.0" y su valor rige
        para toda altura mayor -- eso SI lo escribe la tabla;
      - por debajo de la primera (5.0 ft = 1.524 m) no hay fila con que
        interpolar y extrapolar no lo autoriza nadie. Es una LAGUNA de la
        fuente y la cierra un criterio [A] VACIO, no este modulo: hasta que se
        declare, el calculo se detiene. Antes se tomaba la primera fila en
        duro, con el argumento de que era el lado conservador; no lo decide
        eso, porque extrapolar el primer tramo da un h_eq AUN MAYOR y las dos
        lecturas son elegibles.
    """
    if altura_ft <= puntos[0][0]:
        if altura_ft >= puntos[0][0] - TOL_UMBRAL_NORMATIVO:
            return puntos[0][1]           # la fila existe: no hay laguna
        regla = ca.valor(CRITERIO_H_EQ_BAJO_TABLA)    # VACIO: detiene aqui
        if regla == H_EQ_BAJO_TABLA_PRIMERA_FILA:
            return puntos[0][1]
        if regla == H_EQ_BAJO_TABLA_EXTRAPOLAR:
            (a0, h0), (a1, h1) = puntos[0], puntos[1]
            return h0 + (h1 - h0) * (altura_ft - a0) / (a1 - a0)
        raise DatoInvalidoError(
            campo=CRITERIO_H_EQ_BAJO_TABLA, valor=regla,
            motivo="las lecturas declaradas por debajo de la primera fila "
                   f"son '{H_EQ_BAJO_TABLA_PRIMERA_FILA}' y "
                   f"'{H_EQ_BAJO_TABLA_EXTRAPOLAR}'")
    if altura_ft >= puntos[-1][0]:
        return puntos[-1][1]
    for (a0, h0), (a1, h1) in zip(puntos, puntos[1:]):
        if a0 <= altura_ft <= a1:
            return h0 + (h1 - h0) * (altura_ft - a0) / (a1 - a0)
    raise DatoInvalidoError(
        f"altura de muro {altura_ft} ft fuera de la tabla de h_eq")


def presion_sobrecarga_trasdos(*, gamma_relleno: float, k_a: float,
                               altura_muro_total: float) -> float:
    """
    Presion horizontal constante de la sobrecarga de trasdos, kPa:

        p = gamma * h_eq * k_a       (num. 2.4.2.2 / AASHTO 3.11.6.4)

    El h_eq ya NO es el escalar 0.60: sale de `h_eq_sobrecarga_trasdos`, que
    lo resuelve por altura y orientacion y se detiene si la orientacion no
    esta declarada.

    LA FORMA `p = gamma * h_eq * k_a` NO ESTA EN EL NUMERAL PERUANO: el
    Manual escribe la sobrecarga como "altura de relleno equivalente" y el
    paso a presion es derivacion del proyectista, correcta y declarada.
    AASHTO SI la escribe, en su ec. 3.11.6.4-1 (Dp = k*gamma_s*h_eq).

    La presion es uniforme en toda la altura porque la sobrecarga equivale a
    una altura de relleno adicional constante, no a una carga triangular.
    """
    h_eq = h_eq_sobrecarga_trasdos(altura_muro_total=altura_muro_total)
    return gamma_relleno * h_eq * k_a


def empuje_sobrecarga_trasdos(*, gamma_relleno: float, k_a: float,
                              H: float,
                              altura_muro_total: Optional[float] = None) -> float:
    """
    Empuje horizontal de la sobrecarga por metro de muro, kN/m: la presion
    uniforme de `presion_sobrecarga_trasdos` por la altura H. Su resultante
    actua a H/2, por ser un diagrama rectangular (geometria, no criterio).

    LAS DOS ALTURAS NO SON LA MISMA, y por eso son dos argumentos:
      `H`                  la altura sobre la que se integra el diagrama, que
                           es la del empuje del punto;
      `altura_muro_total`  la que ENTRA EN LA TABLA de h_eq, y que AASHTO
                           define desde la superficie del relleno hasta el
                           FONDO DE LA ZAPATA -- o sea con la zapata dentro.
    Si no se pasa la segunda se usa la primera, y eso subestima la altura de
    entrada: como h_eq decrece con ella, el resultado queda del lado
    conservador. Se admite por compatibilidad con los llamadores que solo
    tienen una altura; quien tenga la geometria completa pasa las dos.
    """
    return presion_sobrecarga_trasdos(
        gamma_relleno=gamma_relleno, k_a=k_a,
        altura_muro_total=H if altura_muro_total is None
        else altura_muro_total) * H


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

    EL AGUA BAJO EL NF, hipotesis declarada y no supuesta. El empuje activo
    se calcula con el peso especifico TOTAL del relleno en toda la altura y
    se le suma la hidrostatica completa, de modo que en la zona sumergida el
    agua de poros se cuenta dos veces. AASHTO 3.11.3 "Presence of Water"
    (pag. impresa 3-118 / PDF 172) exige lo contrario, y con un `shall`:
    "Submerged unit weights of the soil shall be used to determine the
    lateral earth pressure below the groundwater table". La desviacion es
    CONSERVADORA y esta acotada. El exceso NO es constante en la zona
    sumergida: es TRIANGULAR, crece desde 0 en el nivel freatico hasta
    Ka*gamma_agua*h_agua en la base --- 1.96 kPa con Ka = 1/3 y 0.60 m de
    agua, que es el valor EN LA BASE y no una constante. (El texto que ocupaba
    este lugar decia "constante en toda la zona sumergida" y se contradecia a
    si mismo tres lineas mas abajo: con el diagrama rectangular el muro de
    0.60 m daria +68 % y no el +25 % que el propio parrafo cita.)

    En porcentaje sobre el empuje lateral total, recomputado a mano contra
    AASHTO 3.11.3 con gamma = 19.0 kN/m3, gamma_agua = 9.81 kN/m3 y Ka = 1/3:
    +25.4 % sobre un muro de 0.60 m enteramente sumergido (el caso con que lo
    calculo la ficha MAT-O3) y +4.3 % sobre uno de 2.00 m con el freatico a
    1.40 m --- no el +11 % que decia este parrafo, que corresponderia a un
    muro de ~1.06 m. Menos cuanto mas alto el muro. Se
    mantiene porque corregirla exige un peso especifico SUMERGIDO del relleno
    que este expediente todavia no tiene: aplicar AASHTO con el unico gamma
    declarado seria aliviar el empuje sin dato que lo sostenga. El texto
    completo esta en `constantes_normativas.HIPOTESIS_EMPUJE_BAJO_NF` y viaja
    a la memoria por `condicion_normativa_cabezal`; la hoja de ruta no dice
    nada del NF en el empuje y por eso el defecto se reporta contra ella.

    Se detiene con `CriterioPendienteError` en el primero de los vacios que
    toque: el peso especifico del relleno, los cuatro angulos de K_AE (solo
    en condicion sismica) o el brazo del incremento.
    """
    gamma = peso_especifico_relleno()
    K_A_rankine = ka_rankine(phi_grados=ca.valor(CRITERIO_PHI_RELLENO))

    E_a = empuje_activo_estatico(gamma_relleno=gamma, k_a=K_A_rankine,
                                 H=altura_empuje)
    # AASHTO mide la altura de entrada de h_eq desde la superficie del relleno
    # hasta el FONDO DE LA ZAPATA, con un `shall`. `geometria.H` es la altura
    # del muro SOBRE la zapata, de modo que la de la tabla es la suma.
    altura_para_h_eq = geometria.H + geometria.espesor_zapata
    # h_eq SE CALCULA APARTE Y VIAJA EN EL RESULTADO. Antes solo existia dentro
    # de `empuje_sobrecarga_trasdos` y se perdia: la memoria recibia el empuje
    # y no la altura equivalente, la orientacion ni la segunda fuente.
    h_eq = h_eq_sobrecarga_trasdos(altura_muro_total=altura_para_h_eq)
    E_s = empuje_sobrecarga_trasdos(
        gamma_relleno=gamma, k_a=K_A_rankine, H=altura_empuje,
        altura_muro_total=altura_para_h_eq)
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
        h_eq_sobrecarga=h_eq,
        orientacion_muro=ds.valor("orientacion_muro_respecto_al_trafico"),
        numeral_sobrecarga=(f"{NUMERAL_SOBRECARGA_TRASDOS} + "
                            f"{NUMERAL_SOBRECARGA_TRASDOS_AASHTO}"),
    )


# ===========================================================================
# 9.2 - INERCIA DEL MURO Y DEMANDA SISMICA (100/50 - 50/100)
# El tramo de la cadena que faltaba entero: MAT-D6, MAT-X7, MAT-O16.
# ===========================================================================

def peso_suelo_sobre_talon(*, ancho_talon: float, altura_suelo: float,
                           gamma_relleno: float) -> float:
    """
    W_s, peso del suelo que gravita sobre el talon de la zapata, kN/m
    (num. 2.8.1.1.14.1).

    La fuente lo define ESTRECHO y conviene no ensancharlo: "el peso del
    suelo que esta inmediatamente encima del muro, incluyendo el talon del
    muro". No es el relleno del trasdos entero -- ese ya entra por el empuje
    activo -- sino la columna de suelo que la zapata carga y que, por tanto,
    acelera con el muro.

    `altura_suelo` entra por argumento y no se deduce de la geometria por la
    misma razon que `altura_empuje` en `empujes_trasdos`: la altura de suelo
    sobre el talon depende de donde se corte el plano de calculo, y elegirlo
    aqui seria decidir por el proyectista. La eleccion corriente es la altura
    del muro sobre la cara superior de la zapata.
    """
    return gamma_relleno * ancho_talon * altura_suelo


def fuerza_inercia_muro(*, k_h: float, W_w: float,
                        W_s: float) -> FuerzaInerciaMuro:
    """
    P_IR = k_h * (W_w + W_s), kN/m: la fuerza de inercia de la masa del muro
    (num. 2.8.1.1.14.1, ec. 2.8.1.1.14.1-1 = AASHTO 11.6.5.1-1).

    ESTE TERMINO NO EXISTIA EN EL REPOSITORIO. La cadena de la hoja de ruta
    termina en k_h y K_AE, y `empujes_trasdos` sumaba EH + LS + WA + el
    incremento de Mononobe-Okabe sin ninguna linea de inercia del muro. La
    omision es NO CONSERVADORA y no marginal: con k_h = 0.50, P_IR vale la
    mitad del peso movilizado, del mismo orden que el propio incremento
    sismico del empuje, y falta en el volteo y en el deslizamiento sismicos.

    Se reporta contra la hoja de ruta, que es la que hay que corregir: su
    Sec. 9.2 desagrega la cadena, cita el num. 2.8.1.1.14.2 para k_h0 y nunca
    menciona P_IR, que esta en el num. 2.8.1.1.14.1 -- la misma seccion, un
    nivel mas arriba.
    """
    return FuerzaInerciaMuro(P_IR=k_h * (W_w + W_s), W_w=W_w, W_s=W_s,
                             k_h=k_h, numeral=NUMERAL_P_IR)


def demanda_sismica_cabezal(*, P_AE: float, P_A: float,
                            inercia: FuerzaInerciaMuro
                            ) -> DemandaSismicaCabezal:
    """
    P_seis: los dos casos que el num. 2.8.1.1.14.1 manda investigar y el mas
    desfavorable de los dos.

        caso 1   100 % P_AE  +   50 % P_IR
        caso 2    50 % P_AE  +  100 % P_IR,
                  con el 50 % de P_AE acotado por abajo en el empuje activo
                  ESTATICO: "no sea menor que la presion estatica activa del
                  terreno (F = 1/2 gf h2 k)"

    La fuente dice por que son dos y no una suma: "los efectos de la
    combinacion de P_AE y P_IR NO SON SIMULTANEOS". Sumar el 100 % de los dos
    sobrestima; tomar solo uno subestima.

    ESTA FUNCION NO ELIGE EL QUE GOBIERNA, y es deliberado. La fuente manda
    quedarse con "el resultado mas conservador de estos dos ANALISIS", no con
    la mayor de las dos fuerzas: P_AE y P_IR actuan a alturas distintas, de
    modo que el orden por fuerza resultante no coincide con el orden por
    momento volcante, y elegir por la suma devuelve el caso equivocado justo
    donde equivocarse es no conservador. Quien evalue la estabilidad pasa el
    efecto que midio a `DemandaSismicaCabezal.mas_desfavorable`.

    QUE ES `P_AE` AQUI. El empuje TOTAL de Mononobe-Okabe -- estatico mas
    dinamico --, no el incremento. AASHTO lo advierte en el comentario del
    mismo articulo: "Since P_AE is the combined lateral earth pressure force
    resulting from static earth pressure plus dynamic effects, the static
    earth pressure ... K_a, should not be added to the seismic earth
    pressure". Pasarle el incremento de `incremento_sismico` en vez del total
    de `empuje_activo_sismico_total` es el error que este parrafo existe para
    impedir.

    QUE NO ENTRA. La sobrecarga de trasdos: el comentario excluye de P_AE las
    cargas de sobrecarga permanente sobre el muro, que aportan por su cuenta
    su empuje estatico y su propia inercia k_h*W_sobrecarga. Este objeto
    devuelve la demanda del PAR P_AE / P_IR, y quien ensamble la combinacion
    Evento Extremo I tiene que anadir esos dos terminos aparte.
    """
    # El piso estatico se identifica por el NOMBRE de la combinacion a la que
    # la fuente se lo pone, y ese nombre es dato [N]. Si alguna vez dejara de
    # coincidir, el piso se aplicaria a ninguna combinacion EN SILENCIO -- que
    # es exactamente la clase de omision no conservadora que este bloque
    # existe para cerrar --, asi que se comprueba en vez de confiarse.
    nombres = [nombre for nombre, _, _ in P_SEIS_COMBINACIONES]
    if P_SEIS_PISO_ESTATICO not in nombres:
        raise DatoInvalidoError(
            campo="P_SEIS_PISO_ESTATICO", valor=P_SEIS_PISO_ESTATICO,
            motivo=f"nombra una combinacion que no esta en "
                   f"P_SEIS_COMBINACIONES ({nombres}): el piso del empuje "
                   f"activo estatico que exige {NUMERAL_P_IR} no se estaria "
                   f"aplicando a ninguna",
        )
    casos = []
    for nombre, fraccion_ae, fraccion_ir in P_SEIS_COMBINACIONES:
        ae = fraccion_ae * P_AE
        piso = nombre == P_SEIS_PISO_ESTATICO and ae < P_A
        if piso:
            ae = P_A
        ir = fraccion_ir * inercia.P_IR
        casos.append(CasoDemandaSismica(
            nombre=nombre, fraccion_P_AE=fraccion_ae,
            fraccion_P_IR=fraccion_ir, P_AE_aplicado=ae, P_IR_aplicado=ir,
            total=ae + ir, piso_estatico_activo=piso,
        ))
    return DemandaSismicaCabezal(casos=tuple(casos), P_AE=P_AE, P_A=P_A,
                                 inercia=inercia, numeral=NUMERAL_P_IR)


# ===========================================================================
# 9.3 - PRESION DE CONTACTO Y EXCENTRICIDAD EN LA BASE
# ===========================================================================

def excentricidad_resultante(*, N: float, momento_neto: float,
                             B: float) -> float:
    """
    e, excentricidad de la resultante respecto del CENTRO de la zapata, en m.

        e = momento_neto / N

    `momento_neto` es el momento respecto del centro de la base -- el
    volcante menos el estabilizante --, y `N` la normal neta ya descontada la
    subpresion (ver `subpresion`). El signo de e no interesa: lo que se
    compara con el limite es su magnitud, y por eso se devuelve el valor
    absoluto.

    Con N <= 0 no hay resultante que ubicar: la zapata no esta comprimida y
    el problema no es de excentricidad sino de flotacion, que es otra
    verificacion.
    """
    if N <= 0:
        raise DatoInvalidoError(
            campo="N", valor=N,
            motivo="la normal neta en la base tiene que ser de compresion "
                   "para que la resultante tenga una ubicacion que comparar "
                   "con el limite de excentricidad. Con N <= 0 el problema es "
                   "de flotacion, no de excentricidad",
        )
    if B <= 0:
        raise DatoInvalidoError(
            campo="B", valor=B,
            motivo="el ancho de zapata tiene que ser positivo",
        )
    return abs(momento_neto / N)


def excentricidad_admisible_sismica(*, B: float, gamma_EQ: float) -> float:
    """
    Excentricidad maxima admisible de la resultante bajo sismo, en m
    (num. 2.8.1.1.14.1).

    NO ES UN LIMITE FIJO: el numeral lo hace depender de gamma_EQ.

        gamma_EQ = 0.0   dos tercios centrales   ->  e <= B/3
        gamma_EQ = 1.0   ocho decimas centrales  ->  e <= 0.4*B
        entre los dos    interpolacion lineal

    Y EL PRIMERO NO SALE DEL LITERAL DEL MANUAL, que imprime "tercio central"
    (e <= B/6). Es la TERCERA errata de imprenta de esta cadena y la unica
    que mueve un numero: AASHTO 11.6.5.1 escribe "middle two-thirds", el
    propio Manual traduce bien ese mismo giro tres paginas antes en su
    numeral estatico, y la lectura literal dejaria el limite bajo SISMO al
    doble de estricto que el estatico del mismo Manual -- imposible en la
    filosofia de estados limite. La declaracion entera, con las tres pruebas,
    esta en `constantes_normativas.EXCENTRICIDAD_ERRATA_MANUAL`. Con el texto
    de AASHTO el articulo es coherente: ANCLA en B/3, que es el limite
    estatico para fundacion en suelo, y RELAJA hasta 0.4*B.

    Quien adopte gamma_EQ distinto de 0 sin interpolar no tiene regla. Por eso
    el limite se calcula y gamma_EQ es un vacio declarado ('gamma_EQ'), no un
    supuesto.
    """
    tramos = EXCENTRICIDAD_ADMISIBLE_FRACCION_B
    g0, g1 = min(tramos), max(tramos)
    if not g0 - TOL_UMBRAL_NORMATIVO <= gamma_EQ <= g1 + TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            campo=CRITERIO_GAMMA_EQ, valor=gamma_EQ,
            motivo=f"el numeral tabula el limite de excentricidad solo entre "
                   f"gamma_EQ = {g0} y gamma_EQ = {g1}, e interpola en medio: "
                   f"fuera de ese rango no hay limite que leer",
        )
    f0, f1 = tramos[g0], tramos[g1]
    fraccion = f0 + (f1 - f0) * (gamma_EQ - g0) / (g1 - g0)
    return fraccion * B


def gamma_eq() -> float:
    """
    gamma_EQ, factor de carga viva de Evento Extremo I, del criterio del mismo
    nombre. Se detiene con `CriterioPendienteError` mientras siga vacio: ni la
    Tabla 2.4.5.3.1-1 ni AASHTO escriben un numero -- la tabla imprime el
    simbolo y AASHTO manda determinarlo "on a project-specific basis".
    """
    return ca.valor(CRITERIO_GAMMA_EQ)


def presion_contacto_base(*, N: float, momento_neto: float, B: float,
                          cimentacion_en_roca: bool) -> PresionContactoBase:
    """
    Presion de contacto bajo la zapata, en kPa, segun la distribucion que la
    fuente da a CADA TERRENO DE FUNDACION (num. 2.8.1.1.12.2, `NUMERAL_
    PRESION_CONTACTO`). Son dos ramas y no una:

        fundacion en SUELO   presion UNIFORME sobre el ancho efectivo:
                             q = N / (B - 2e)                  (-1)

        fundacion en ROCA    presion distribuida LINEALMENTE:
                             dentro del tercio central (e <= B/6)
                                 q = (N/B)(1 +- 6e/B)          (-2, -3)
                             fuera del tercio central
                                 q_max = 2N/[3(B/2 - e)], q_min = 0  (-4, -5)

    ESTO ES UN CAMBIO CONTRA LA FICHA DEL HALLAZGO, y hay que decir por que.
    MAT-O16 describe el procedimiento ausente como "excentricidad, e <= B/6,
    q_max = N/B*(1+6e/B)", que es la rama de ROCA. Implementarla sola, como
    se hizo primero, aplicaba a esta obra -- la llanura arenosa del Bajo
    Piura, que el propio proyecto declara en 'F_pga' que NO es roca -- la
    rama que la fuente reserva al otro terreno, y la elegia en silencio, que
    es justo lo que este cluster existe para no hacer. La direccion era
    conservadora (Navier sobre B da un pico mayor que el uniforme sobre
    B - 2e), de modo que no hay ningun numero emitido que corregir; lo que se
    corrige es la rama y la cita.

    `cimentacion_en_roca` entra por argumento, como en
    `coeficiente_sismico_base` y por lo mismo: quien quiera la rama del
    proyecto llama a `cimentacion_en_roca()`, que la resuelve con las filas
    declaradas en 'F_pga'. Es el MISMO reparto suelo/roca que gobierna k_h0,
    y que lo sea no es coincidencia: las dos ramas cuelgan de la clase de
    sitio.

    Con e >= B/2 la resultante cae fuera de la zapata y no hay equilibrio
    posible en ninguna de las dos ramas: sale como `DisenoNoFactibleError`
    con su motivo, no como una division por cero ni como una presion enorme
    sin explicacion.
    """
    e = excentricidad_resultante(N=N, momento_neto=momento_neto, B=B)
    if e >= B / 2 - TOL_UMBRAL_NORMATIVO:   # literal-ok: media zapata
        raise DisenoNoFactibleError(
            motivo=f"la resultante cae fuera de la zapata (e = {e:.4f} m, "
                   f"B/2 = {B / 2:.4f} m): no hay distribucion de presiones "
                   f"que equilibre el muro. Hay que ampliar B o reducir el "
                   f"momento volcante ({NUMERAL_PRESION_CONTACTO})"
        )
    ancho_efectivo = B - 2 * e
    limite_nucleo = B / 6                   # literal-ok: nucleo central, e = B/6
    dentro = e <= limite_nucleo + TOL_UMBRAL_NORMATIVO

    if not cimentacion_en_roca:
        # Rama de SUELO: uniforme sobre el ancho efectivo. No hay q_min
        # distinto: la fuente reparte la resultante por igual sobre B - 2e y
        # el resto de la zapata no toma presion.
        q = N / ancho_efectivo
        return PresionContactoBase(N=N, B=B, e=e, q_max=q, q_min=q,
                                   ancho_efectivo=ancho_efectivo,
                                   dentro_del_nucleo=dentro,
                                   distribucion="uniforme sobre B - 2e "
                                                "(fundacion en suelo)",
                                   numeral=NUMERAL_PRESION_CONTACTO)

    # Rama de ROCA: distribucion lineal, y su forma cambia en el tercio
    # central. Las dos expresiones empalman exactamente en e = B/6, donde las
    # dos dan 2N/B.
    if dentro:
        q_medio = N / B
        variacion = 6 * e / B               # literal-ok: q = N/B(1+-6e/B)
        q_max = q_medio * (1 + variacion)
        q_min = q_medio * (1 - variacion)
        forma = "lineal sobre B (fundacion en roca, resultante en el nucleo)"
    else:
        q_max = 2 * N / (3 * (B / 2 - e))   # literal-ok: triangular, base 3(B/2-e)
        q_min = 0.0
        forma = ("triangular sobre 3(B/2 - e) (fundacion en roca, resultante "
                 "fuera del nucleo)")
    return PresionContactoBase(N=N, B=B, e=e, q_max=q_max, q_min=q_min,
                               ancho_efectivo=ancho_efectivo,
                               dentro_del_nucleo=dentro, distribucion=forma,
                               numeral=NUMERAL_PRESION_CONTACTO)


def verificar_excentricidad_sismica(*, N: float, momento_neto: float,
                                    B: float,
                                    gamma_EQ: float) -> Verificacion:
    """
    E6 - Ubicacion de la resultante en la base bajo sismo (num.
    2.8.1.1.14.1): e <= B/6 con gamma_EQ = 0.0, e <= 0.4*B con gamma_EQ = 1.0,
    interpolado en medio.

    Es una fila que la tabla de Sec. 9.3 no trae -- E.050 no la escribe -- y
    que el Manual de Puentes si exige. Se numera E6 para no pisar las cinco
    de E.050 y se devuelve como `Verificacion`, no como bool, igual que las
    otras. El criterio aplicado es 'gamma_EQ' porque de el depende el umbral:
    a diferencia de los FS de E.050, este limite NO es un [N] puro.
    """
    e = excentricidad_resultante(N=N, momento_neto=momento_neto, B=B)
    admisible = excentricidad_admisible_sismica(B=B, gamma_EQ=gamma_EQ)
    return Verificacion(
        cumple=e <= admisible + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_EXCENTRICIDAD_SISMICA,
        valor_obtenido=e,
        valor_admisible=admisible,
        criterio_aplicado=CRITERIO_GAMMA_EQ,
        codigo="E6",
    )


# ===========================================================================
# 9.2 - COMBINACIONES AASHTO LRFD
# ===========================================================================

# Cargas de la Tabla 2.4.5.3.1-1 que comparten la columna de PERMANENTES: la
# tabla les da una sola celda ("DC DD DW EH EV ES EL PS CR SH"), y donde esa
# celda dice gamma_p hay que ir a la Tabla -2 fila por fila. Las demas cargas
# de Sec. 9.2 -- LS, WA, EQ -- tienen columna propia y no cuelgan de gamma_p.
CARGAS_PERMANENTES = ("DC", "EV", "EH")

# El cabezal, como elemento estructural de 'factores_carga_aashto'. M9 no
# dimensiona ninguna otra cosa: el conducto es de Fase 8 y lo resuelve M8 con
# el material del punto.
ELEMENTO_CABEZAL = "cabezal"

# DC no se elige: la Tabla 2.4.5.3.1-2 trae una sola fila de componentes
# (1.25/0.90); la otra, "DC: Resistencia IV Solamente", es de una combinacion
# que Sec. 9.2 no nombra.
FILA_GAMMA_P_DC = "DC_componentes_y_auxiliares"


def combinaciones() -> Tuple[CombinacionCarga, ...]:
    """
    Las tres combinaciones de Sec. 9.2 (AASHTO LRFD Sec. 3.4.1, via Manual de
    Puentes num. 2.4.5.3): Resistencia I, Servicio I y Evento Extremo I, con
    las cargas que participan en cada una.

    Describe, no evalua: nombra que cargas entran en cada combinacion. Esta
    funcion no se detiene, a diferencia de `factores_de_carga`, que si
    necesita la eleccion de fila y por eso puede quedarse bloqueada.

    NO LA LLAMA M11, Y EL DOCSTRING LO AFIRMABA. Decia «es la que M11 usa
    para declarar QUE combinaciones rigen aunque no se hayan evaluado», y
    `M11_reporte` no la referencia: sus unicos llamadores son cuatro tests.
    Es la misma forma de prometer un consumidor que este proyecto ya
    desterro en `ControlEntrada.HW_sobre_D` (SIS-B-02) --- «sin consumidor y
    con la razon escrita, no sin consumidor y con un consumidor prometido».
    Se conserva porque es la unica pieza que EMPAQUETA las tres combinaciones
    con sus componentes y con el criterio del que cuelgan sus factores. Los
    nombres sueltos ya son iterables --- `COMBINACIONES_AASHTO` es [N] y una
    tupla ---, asi que lo que se perderia al borrarla no es acceso al dato
    sino el objeto `CombinacionCarga` que la memoria necesitaria; que la
    memoria las declare es una fase que no esta escrita, no una llamada que
    falte.

    SI LA NOMBRA EL REGISTRO NORMATIVO, y conviene decirlo para que nadie lea
    una contradiccion donde no la hay: las tres filas de `T_MP_COMBINACIONES`
    llevan `uso=Usada(por=(..., "M9.combinaciones"))`, y la ventana emergente
    se lo muestra al proyectista. Es cierto --- esta funcion es la que lee la
    transcripcion de esas etiquetas --- y no promete un pipeline: dice QUE
    SIMBOLO lee la tabla, no que una corrida pase por el. Hallazgo abierto en
    S19 al cerrar SIS-B-18; anotado en `docs/decisiones_diferidas.md`.
    """
    return tuple(
        CombinacionCarga(nombre=nombre, numeral=NUMERAL_COMBINACIONES,
                         componentes=COMPONENTES_COMBINACION[nombre],
                         criterio_factores=CRITERIO_FACTORES_CARGA)
        for nombre in COMBINACIONES_AASHTO
    )


def factores_de_carga(nombre: str) -> dict:
    """
    Factores gamma de una combinacion DEL CABEZAL, por tipo de carga: Tablas
    2.4.5.3.1-1 y 2.4.5.3.1-2 del Manual de Puentes (= 3.4.1-1 y 3.4.1-2 de
    AASHTO LRFD), [N] en `constantes_normativas`.

    Los factores de EH y EV son DOBLES (maximo y minimo) y cual gobierna
    depende de si la carga estabiliza o desestabiliza cada verificacion:
    tomar un solo numero por carga da del lado inseguro en volteo, por eso
    esta funcion los devuelve completos y no elige por quien la llama.

    DEL CABEZAL, y hay que decirlo (NOR-PUE-03). La Tabla 2.4.5.3.1-2
    desglosa el empuje vertical de tierra por TIPO DE ESTRUCTURA, y M9 modela
    el cabezal como muro de contencion con zapata: su fila es "Muros y
    estribos de retencion", 1.35 / 1.00. El minimo es 1.00 y NO 0.90 -- el
    0.90 es de "Estructura rigida enterrada", la fila del conducto, que es lo
    que consume V7 en Fase 8. Que fila describe a cada estructura lo declara
    'factores_carga_aashto' ([A]); los numeros no salen de ahi.

    EN QUE DIRECCION VA ESO, porque es facil contarlo al reves: el empuje
    vertical de tierra sobre el talon ESTABILIZA el volteo y el
    deslizamiento, de modo que pasar su minimo de 0.90 a 1.00 RELAJA esas dos
    verificaciones alrededor de un 8 %; minorar lo que estabiliza es la
    direccion conservadora, no la insegura. Lo que se corrige es la
    conformidad con la fuente -- el par que el proyecto usaba no era ninguna
    fila de la tabla --, y la fuente lo prescribe sin rodeos (AASHTO LRFD 9a
    ed., C3.4.1, pag. impresa 3-15): "The vertical earth load on the rear of
    a cantilevered retaining wall would be multiplied by gamma_p min (1.00)
    and the weight of the structure would be multiplied by gamma_p min (0.90)
    because these forces result in an increase in the contact stress (and
    shear strength) at the base of the wall and foundation". Para la
    capacidad portante el mismo comentario manda los MAXIMOS (1.25, 1.35,
    1.50), que es la otra mitad de la razon por la que esta funcion devuelve
    los dos extremos y no elige por quien la llama.

    EH sale de la fila "Activa" porque el proyecto disena con empuje ACTIVO
    (Mononobe-Okabe / Coulomb, ver 'inclinacion_muro_beta' y companeros), y
    esa eleccion se declara en el mismo criterio. Las otras dos filas de EH
    -- "En reposo" (1.35/0.90) y "AEP Para paredes ancladas" (1.35/N/A) --
    estan en la tabla completa, con sus pares, para que se vea de que se
    eligio.

    La celda que la fuente marca N/A viaja como `GAMMA_P_NO_APLICA`: no es un
    cero ni un olvido, es la fuente diciendo que esa fila no tiene ese
    extremo. Ninguna de las dos filas que este proyecto usa lo lleva.
    """
    if nombre not in COMBINACIONES_AASHTO:
        raise DatoInvalidoError(
            campo="combinacion",
            valor=nombre,
            motivo=("no es una de las combinaciones de Sec. 9.2: "
                    + ", ".join(COMBINACIONES_AASHTO)),
        )
    eleccion = ca.valor(CRITERIO_FACTORES_CARGA)
    filas_del_cabezal = (eleccion.get(ELEMENTO_CABEZAL)
                         if hasattr(eleccion, "get") else None)
    if not hasattr(filas_del_cabezal, "get"):
        raise DatoInvalidoError(
            campo=CRITERIO_FACTORES_CARGA, valor=eleccion,
            motivo=f"Sec. 9.2 necesita saber que filas de gamma_p describen "
                   f"al elemento '{ELEMENTO_CABEZAL}' y la declaracion no lo "
                   "dice",
        )

    fila_combinacion = TABLA_COMBINACIONES_FILAS[nombre]
    factores = {}
    for carga in COMPONENTES_COMBINACION[nombre]:
        if carga in CARGAS_PERMANENTES:
            factores[carga] = _gamma_permanente(carga, fila_combinacion,
                                                filas_del_cabezal)
        else:
            celda = fila_combinacion[carga]
            # Copia por el mismo motivo que arriba: la celda es una constante
            # [N] y devolverla por referencia dejaria que un llamador mute la
            # tabla normativa para todo el proceso.
            factores[carga] = dict(celda) if isinstance(celda, dict) else celda
    return factores


def _gamma_permanente(carga: str, fila_combinacion: dict,
                      filas_del_cabezal: dict) -> dict:
    """
    El factor de una carga permanente en una combinacion. Si la Tabla
    2.4.5.3.1-1 imprime un numero en la columna de permanentes (Servicio I y
    Evento Extremo I imprimen 1.00), ese numero vale para las tres cargas; si
    imprime el simbolo gamma_p, hay que bajar a la fila que la Tabla -2 da a
    ESTA estructura y ESTA carga.

    Evento Extremo I lleva 1.00 y no gamma_p en las dos fuentes, y no es un
    descuido de transcripcion: C3.4.1 de AASHTO explica que antes de 2015 se
    usaba un gamma_p mayor que 1.0 y que esa practica iba contra la filosofia
    del estado limite de evento extremo.
    """
    celda = fila_combinacion["permanentes"]
    if celda != GAMMA_P_MARCA:
        # Copia: la celda es una constante [N] compartida por las tres cargas
        # de la combinacion, y devolver el mismo objeto dejaria que quien lo
        # reciba modifique la tabla normativa desde fuera.
        return dict(celda)
    fila = (FILA_GAMMA_P_DC if carga == "DC"
            else filas_del_cabezal.get(carga))
    if fila not in TABLA_GAMMA_P_FILAS:
        raise DatoInvalidoError(
            campo=CRITERIO_FACTORES_CARGA, valor=fila,
            motivo=f"la carga '{carga}' del cabezal se declara en la fila "
                   f"'{fila}', que no es una fila de {NUMERAL_TABLA_GAMMA_P}",
        )
    return {"max": TABLA_GAMMA_P_FILAS[fila]["max"],
            "min": TABLA_GAMMA_P_FILAS[fila]["min"]}


# ===========================================================================
# 9.3 - ESTABILIDAD (E.050)
# Cinco verificaciones, codigos E1..E5, cada una en las dos condiciones.
# ===========================================================================

# ---------------------------------------------------------------------------
# POR QUE ESTE MODULO VALIDA ARGUMENTOS INTERNOS CON `DatoInvalidoError`
# ---------------------------------------------------------------------------
# SIS-E-02. Cuatro funciones de aqui -- `fs_requerido` (verificacion),
# `recubrimiento_e060_mm` y `recubrimiento_aashto_mm` (condicion) y
# `verificar_cuantia` (direccion) -- validan cadenas que NO vienen del
# expediente: las escribe el propio codigo o las itera desde la misma tabla
# que se valida (cli.py recorre RECUBRIMIENTO y CUANTIA_MIN_MURO para
# construir la memoria). Un `DatoInvalidoError` ahi disfraza un fallo de
# PROGRAMA de problema del expediente, que es lo contrario de lo que la
# taxonomia de CLAUDE.md persigue, y la eleccion estaba fijada por tests pero
# no escrita en ninguna parte.
#
# SE MANTIENE, y esta es la razon: las cuatro cadenas son CLAVES DE UNA TABLA
# NORMATIVA -- las filas de Sec. 9.3, del Art. 7.7.1 de E.060, de la Tabla
# 5.10.1-1 de AASHTO y del Art. 14.3.1 --, y el mensaje que la excepcion
# construye ENUMERA las filas admisibles. Ese mensaje es util al revisor y no
# solo al programador: la forma en que una fila desaparece no es que alguien
# escriba mal un literal, es que la tabla cambie de transcripcion y un
# consumidor quede apuntando a una fila que ya no esta. Cuando eso pasa, el
# problema SI es del expediente -- la transcripcion -- y la fila del informe
# que produce `cli._bloqueo` dice exactamente cual falta.
#
# LA FRONTERA, para que no se estire: se usa `DatoInvalidoError` cuando el
# argumento es una CLAVE DE TABLA NORMATIVA y el mensaje enumera las
# admisibles. Para un argumento que no lo sea -- un flag, un modo interno --
# el error correcto es el que el programa merece, no el del expediente. El
# quinto sitio que la ficha SIS-E-02 listaba, `_recubrimiento_aashto_detallado`,
# no pertenece a esta lista por la razon contraria: su tabla sale de
# `ca.valor(CRITERIO_RECUBRIMIENTO_AASHTO)`, es decir del expediente, y ahi
# `DatoInvalidoError` es sencillamente la excepcion correcta.


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

    `q_actuante` sale de `presion_contacto_base` (su `q_max`). Esta funcion
    lo exigia YA RESUELTO y en el repositorio no habia con que producirlo: la
    excentricidad que decide cual de las dos distribuciones aplica no estaba
    ni como procedimiento ni como vacio declarado (MAT-O16). Ahora esta, y el
    limite sismico de esa excentricidad -- que no es "el tercio central" a
    secas, depende de gamma_EQ -- lo comprueba
    `verificar_excentricidad_sismica`.
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
    raise AssertionError(
        "inalcanzable mientras 'metodo_estabilidad_global' este vacio"
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
    raise AssertionError(
        "inalcanzable mientras 'metodo_estabilidad_global' este vacio"
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


def clase_exposicion_sulfatos(*, so4_suelo_pct: Optional[float],
                             so4_agua_ppm: Optional[float]) -> dict:
    """
    Fila de la Tabla 4.4 de E.060 (pag. impresa 38) que aplica al sitio.

    DOS ESCALAS PARALELAS, no una. La tabla clasifica por sulfato soluble en
    el SUELO (% en peso) o por sulfato en el AGUA (ppm), y son alternativas:
    el expediente puede traer una, la otra o las dos. Con las dos, gobierna la
    MAS exigente -- no promedian ni se eligen, y quedarse con la menor seria
    escoger el requisito mas bajo por omision.

    EL BORDE QUE LA TABLA IMPRESA DEJA ABIERTO -- SO4 = 2,0 % exacto no cae en
    ninguna fila -- lo cierra la hoja de ruta hacia la fila SEVERA, y cada fila
    de `SULFATOS` declara si su limite inferior es estricto en vez de dejar la
    respuesta escondida en un ">=" de este bucle. Ver
    `SULFATOS_BORDE_ABIERTO_TEXTO`.
    """
    if so4_suelo_pct is None and so4_agua_ppm is None:
        raise DatoInvalidoError(
            campo=CRITERIO_EXPOSICION_QUIMICA, valor=None,
            motivo="la Tabla 4.4 clasifica por sulfato en el suelo (% en "
                   "peso) o por sulfato en el agua (ppm), y el dato no trae "
                   "ninguna de las dos escalas",
        )
    indice = 0
    for posicion, fila in enumerate(SULFATOS):
        estricto = fila["limite_inferior_estricto"]
        alcanza = False
        for medida, clave in ((so4_suelo_pct, "so4_suelo_pct"),
                              (so4_agua_ppm, "so4_agua_ppm")):
            if medida is None:
                continue
            minimo = fila[clave][0]
            # El limite estricto NO se decide aqui: viaja en la fila, porque
            # es una lectura declarada y no una convencion del codigo.
            alcanza = alcanza or (medida > minimo if estricto
                                  else medida >= minimo)
        if alcanza:
            indice = max(indice, posicion)
    return SULFATOS[indice]


def _exposicion_quimica_validada() -> dict:
    """
    El dato de sitio 'exposicion_quimica_ems', comprobado ANTES de usarlo.

    POR QUE EXISTE ESTA FUNCION, y por que no basta con `.get()`. La version
    anterior leia `exposicion.get("cloruros_tabla_4_2")`: una clave AUSENTE
    daba None, None es falso, y el calculo seguia como si el EMS hubiera
    dicho "no hay cloruros". Con eso desaparecian en silencio la a/c <= 0.40
    y el f'c >= 35 MPa de esa fila -- que son justamente las exigencias que
    el expediente venia afirmando en prosa y que este cluster convirtio en
    dato. La ausencia de una lectura NO es una lectura negativa: es
    DatoInvalidoError, y el revisor tiene que anadir el analisis que falta.

    Lo segundo que comprueba es la FORMA. Este dato es el unico de todo el
    expediente que no es un numero ni un rotulo, sino un diccionario, y la
    unica via por la que hoy se puede declarar desde la ventana produce
    float o str. Sin esta comprobacion, declararlo mal no daba un problema
    del expediente sino un AttributeError -- un fallo del programa, que es
    precisamente la distincion que la taxonomia de excepciones existe para
    mantener.
    """
    exposicion = ca.valor(CRITERIO_EXPOSICION_QUIMICA)
    if not isinstance(exposicion, dict):
        raise DatoInvalidoError(
            campo=CRITERIO_EXPOSICION_QUIMICA, valor=exposicion,
            motivo="el analisis quimico del EMS se declara como un "
                   "diccionario con las claves "
                   + ", ".join(CLAVES_ESCALAS_SULFATOS)
                   + f" y {CLAVE_FILAS_TABLA_4_2}",
        )
    for clave in CLAVES_ESCALAS_SULFATOS:
        if clave not in exposicion:
            raise DatoInvalidoError(
                campo=CRITERIO_EXPOSICION_QUIMICA, valor=exposicion,
                motivo=f"falta la escala '{clave}' de la Tabla 4.4. Las dos "
                       f"escalas son alternativas y una puede venir en None, "
                       f"pero las dos claves tienen que estar declaradas: "
                       f"omitir una no es decir que no se midio",
            )
        medida = exposicion[clave]
        if medida is not None and (isinstance(medida, bool)
                                   or not isinstance(medida, (int, float))):
            raise DatoInvalidoError(
                campo=CRITERIO_EXPOSICION_QUIMICA, valor=medida,
                motivo=f"'{clave}' es una magnitud medida y tiene que ser un "
                       f"numero o None",
            )
    filas = exposicion.get(CLAVE_FILAS_TABLA_4_2)
    if not isinstance(filas, dict):
        raise DatoInvalidoError(
            campo=CRITERIO_EXPOSICION_QUIMICA, valor=filas,
            motivo=f"falta '{CLAVE_FILAS_TABLA_4_2}': las tres filas de la "
                   f"Tabla 4.2 se declaran como si/no en un diccionario",
        )
    for clave in EXPOSICION_ESPECIAL:
        if clave not in filas:
            raise DatoInvalidoError(
                campo=CRITERIO_EXPOSICION_QUIMICA, valor=filas,
                motivo=f"falta la fila '{clave}' de la Tabla 4.2. Se declaran "
                       f"LAS TRES porque la nota al pie manda tomar la menor "
                       f"relacion a/c APLICABLE, y aplicable no se puede "
                       f"evaluar sobre un conjunto incompleto",
            )
        if not isinstance(filas[clave], bool):
            raise DatoInvalidoError(
                campo=CRITERIO_EXPOSICION_QUIMICA, valor=filas[clave],
                motivo=f"la fila '{clave}' de la Tabla 4.2 aplica o no "
                       f"aplica: se declara True o False",
            )
    sobrantes = set(filas) - set(EXPOSICION_ESPECIAL)
    if sobrantes:
        raise DatoInvalidoError(
            campo=CRITERIO_EXPOSICION_QUIMICA, valor=sorted(sobrantes),
            motivo="la Tabla 4.2 tiene tres filas y no mas: "
                   + ", ".join(sorted(EXPOSICION_ESPECIAL)),
        )
    return exposicion


def _extremo_declarado(candidatos, funcion):
    """
    El extremo de una lista de (valor, fuente), con TODAS las fuentes que lo
    alcanzan, no solo una.

    Antes esto era `min(candidatos)` sobre tuplas, y con dos tablas empatadas
    en el valor el desempate lo decidia la comparacion alfabetica del nombre
    de la fuente. Ninguna de las dos tablas es "menor" que la otra: si las
    dos imponen el mismo limite, las dos gobiernan, y eso es lo que la
    memoria tiene que decir.
    """
    if not candidatos:
        return None, "-"
    extremo = funcion(valor for valor, _ in candidatos)
    fuentes = [fuente for valor, fuente in candidatos
               if abs(valor - extremo) <= TOL_UMBRAL_NORMATIVO]
    return extremo, " y ".join(fuentes)


def requisitos_durabilidad_concreto() -> RequisitosDurabilidad:
    """
    Relacion a/c maxima y f'c minimo del concreto, combinando las Tablas 4.2 y
    4.4 de E.060 con la nota al pie que las dos llevan:

        "Cuando se utilicen las Tablas 4.2 y 4.4 simultaneamente, se debe
        utilizar la MENOR relacion maxima agua-material cementante aplicable
        y el MAYOR f'c minimo"

    Es el eslabon que faltaba entero (NOR-E060-06): el expediente tenia las
    dos tablas transcritas y ninguna regla que las cruzara, de modo que en un
    sitio con sulfatos Y cloruros -- este -- no habia forma de decir que
    relacion a/c se especifica. Y de esa relacion a/c cuelga el recubrimiento,
    por el modificador del Art. 5.10.1 de AASHTO.

    QUE NUMERAL MANDA APLICAR LA TABLA 4.2, que la cadena habia perdido: el
    Art. 4.4.2 (pag. impresa 39), verificado contra el PDF. "Cuando el
    concreto con refuerzo vaya a estar expuesto a cloruros de quimicos
    descongelantes, sal, agua salobre, agua de mar o salpicaduras de las
    mismas, deben cumplirse los requisitos de la Tabla 4.2 para la maxima
    relacion agua-material cementante y valor minimo de f'c, Y LOS REQUISITOS
    DE RECUBRIMIENTO MINIMO DEL CONCRETO DE 7.7". Es el articulo que ata este
    cluster entero -- exposicion quimica, relacion a/c y recubrimiento en una
    sola frase --, y una version anterior de este cluster lo habia sacado de
    la cadena de numerales creyendo que citarlo era un error.

    LAS TRES FILAS DE LA TABLA 4.2 SE MIRAN, no solo la de cloruros. "La
    MENOR relacion a/c aplicable" es una comparacion, y una comparacion a la
    que le falta un candidato da el resultado equivocado sin avisar.

    Consume el dato de sitio 'exposicion_quimica_ems' ([S], pendiente de
    ensayo): sin el analisis quimico del EMS, `CriterioPendienteError` y el
    calculo se detiene. No hay lectura por defecto -- la afirmacion "corredor
    salino" viajaba en prosa por varias justificaciones y no era un dato.
    """
    exposicion = _exposicion_quimica_validada()
    fila = clase_exposicion_sulfatos(
        so4_suelo_pct=exposicion[CLAVES_ESCALAS_SULFATOS[0]],
        so4_agua_ppm=exposicion[CLAVES_ESCALAS_SULFATOS[1]])

    candidatos_ac = []
    candidatos_fc = []
    if fila["a_c_max"] is not None:
        candidatos_ac.append((fila["a_c_max"], NOMBRE_TABLA_4_4))
    if fila["fc_min_MPa"] is not None:
        candidatos_fc.append((fila["fc_min_MPa"], NOMBRE_TABLA_4_4))
    # LAS TRES FILAS DE LA TABLA 4.2, no solo la de cloruros. "La MENOR
    # relacion a/c APLICABLE" no se puede evaluar sobre un conjunto que el
    # dato deja a medias: si el concreto ademas debe ser de baja
    # permeabilidad, esa fila es aplicable y tiene que entrar a la
    # comparacion. El dato declara las tres, y aqui entran las que aplican.
    for clave, aplica in exposicion[CLAVE_FILAS_TABLA_4_2].items():
        if not aplica:
            continue
        requisito = EXPOSICION_ESPECIAL[clave]
        etiqueta = f"{NOMBRE_TABLA_4_2} ({clave})"
        candidatos_ac.append((requisito["a_c_max"], etiqueta))
        candidatos_fc.append((requisito["fc_min_MPa"], etiqueta))

    # La nota al pie, aplicada: MENOR a/c y MAYOR f'c de los aplicables.
    a_c_max, gobierna_a_c = _extremo_declarado(candidatos_ac, min)
    fc_min, gobierna_fc = _extremo_declarado(candidatos_fc, max)

    return RequisitosDurabilidad(
        a_c_max=a_c_max, fc_min_MPa=fc_min,
        clase_sulfatos=fila["exposicion"],
        gobierna_a_c=gobierna_a_c, gobierna_fc=gobierna_fc,
        cementos_admisibles=fila["cementos"],
        numeral=f"{NUMERAL_PROTECCION_CORROSION} / "
                f"{NUMERAL_EXPOSICION_ESPECIAL} / {NUMERAL_SULFATOS} / "
                f"{NUMERAL_COMBINACION_4_2_4_4}",
    )


def factor_recubrimiento_por_ac(*, a_c_max: Optional[float]) -> Tuple[float, str]:
    """
    Modificador del recubrimiento por relacion agua-cemento, con su origen.

        W/C <= 0.40  ->  0.8        W/C >= 0.50  ->  1.2

    El Art. 5.10.1 de AASHTO no deja la tabla de recubrimientos en bruto:
    "Cover ... shall not be less than that specified in Table 5.10.1-1 AND
    MODIFIED FOR W/CM RATIO". El Manual de Puentes trae los mismos factores en
    su num. 2.9.1.5.5.3. El criterio los ignoraba enteros, y son los que
    invierten la conclusion de la regla del mayor (NOR-AAS-05).

    QUE a/c ENTRA AQUI: la MAXIMA que la durabilidad permite, no la del diseno
    de mezcla. Es la eleccion conservadora de las dos -- una a/c mas alta da
    factor mas alto y por tanto MAS recubrimiento --, y ademas es la unica que
    el expediente conoce en fase de perfil.

    SIN LIMITE DE DURABILIDAD (`a_c_max=None`, exposicion insignificante y
    ninguna fila de la Tabla 4.2 aplicable) no hay a/c contra la que evaluar
    el modificador. No se inventa una: se aplica el factor MAS exigente de la
    tabla, 1.2, y la funcion lo declara en el origen que devuelve. Ese origen
    VIAJA hasta la memoria (`RecubrimientoDiseno.origen_factor`), porque del
    numero solo no se distingue esta situacion de un expediente cuya a/c
    maxima si es 0.50: son dos cosas distintas y la segunda es un dato,
    mientras la primera es una acotacion del calculo.

    LA BANDA INTERMEDIA no se resuelve aqui con un literal. El Manual de
    Puentes no imprime factor para 0.40 < a/c < 0.50 y AASHTO si; ese hueco
    es un [C] declarado ('factor_recubrimiento_banda_intermedia_ac'), no un
    1.0 escrito en este modulo por parecer neutro. Y la banda es alcanzable:
    con sulfatos severos y sin cloruros la a/c maxima resulta 0.45.
    """
    if a_c_max is None:
        return (max(RECUBRIMIENTO_MP_FACTOR_AC.values()),
                "conservador: ninguna de las dos tablas de E.060 limita la "
                "relacion a/c, y se aplica el factor mas exigente")
    if a_c_max <= RECUBRIMIENTO_AC_UMBRAL_BAJO + TOL_UMBRAL_NORMATIVO:
        return (RECUBRIMIENTO_MP_FACTOR_AC["a_c_menor_igual_0_40"],
                f"a/c maxima {a_c_max} <= 0.40")
    if a_c_max >= RECUBRIMIENTO_AC_UMBRAL_ALTO - TOL_UMBRAL_NORMATIVO:
        return (RECUBRIMIENTO_MP_FACTOR_AC["a_c_mayor_igual_0_50"],
                f"a/c maxima {a_c_max} >= 0.50")
    return (ca.valor(CRITERIO_FACTOR_BANDA_AC),
            f"a/c maxima {a_c_max} en la banda intermedia (0.40 < a/c < "
            f"0.50): el Manual de Puentes no imprime factor para esta banda "
            f"y el hueco lo cubre el criterio [C] "
            f"'{CRITERIO_FACTOR_BANDA_AC}' con el valor de AASHTO LRFD "
            f"Art. 5.10.1")


def recubrimiento_aashto_mm(*, condicion: str) -> float:
    """
    Lado AASHTO / Manual de Puentes de la regla del mayor, en mm, para la
    condicion de E.060 que se le pase. Ya NO es un valor declarado: se
    CALCULA, y por eso puede detenerse.

        tabulado      = max( tabla_aashto[situacion][categoria] ,
                             tabla_manual[fila equivalente] )   # solo cat. A
        recubrimiento = max( tabulado * factor_ac , piso de 1.0 in )

    Los tres eslabones y de donde sale cada uno:

      situacion   'situacion_recubrimiento_aashto' [A]: que fila de la tabla
                  se pone enfrente de cada condicion de E.060. Las dos tablas
                  no se indexan igual -- E.060 por diametro de barra, AASHTO
                  por severidad de exposicion -- y el emparejamiento no lo
                  dice ninguna de las dos normas.
      categoria   'categoria_refuerzo_aashto' [A], VACIO: la columna A/B/C.
                  Es la condicion de aplicacion que el expediente nunca
                  declaro (NOR-AAS-01) y la que puede invertir quien gobierna.
      factor_ac   modificador del Art. 5.10.1, via la durabilidad del
                  concreto, que a su vez cuelga del analisis quimico del EMS.

    DE QUE CORPUS SALE EL NUMERO, que la memoria tiene que declarar: con
    categoria A el valor es [N] peruano -- el Manual de Puentes transcribe esa
    columna en su Tabla 2.9.1.5.5.3-1, cuyo titulo dice "aceros no
    protegidas" -- y con B o C el corpus peruano no tabula nada para
    exposicion exterior y el hueco lo cubre AASHTO LRFD 9a ed. como [C], por
    la Via 1 de Sec. 0.2.
    """
    if condicion not in RECUBRIMIENTO:
        raise DatoInvalidoError(
            campo="condicion", valor=condicion,
            motivo="no es una fila del Art. 7.7.1: " + ", ".join(sorted(RECUBRIMIENTO)),
        )
    return _recubrimiento_aashto_detallado(condicion=condicion)[0]


def _recubrimiento_aashto_detallado(*, condicion: str) -> Tuple[float, dict]:
    """El valor y la cadena que lo produjo, para que la memoria la imprima."""
    situaciones = ca.valor(CRITERIO_SITUACION_RECUBRIMIENTO)
    if condicion not in situaciones:
        raise DatoInvalidoError(
            campo="condicion", valor=condicion,
            motivo=f"no tiene fila emparejada en "
                   f"'{CRITERIO_SITUACION_RECUBRIMIENTO}'",
        )
    situacion = situaciones[condicion]
    tabla = ca.valor(CRITERIO_TABLA_RECUBRIMIENTO)
    if situacion not in tabla:
        raise DatoInvalidoError(
            campo="situacion", valor=situacion,
            motivo=f"no es una fila de la Tabla 5.10.1-1 transcrita en "
                   f"'{CRITERIO_TABLA_RECUBRIMIENTO}'",
        )
    categoria = ca.valor(CRITERIO_CATEGORIA_REFUERZO)   # VACIO: detiene aqui
    if categoria not in tabla[situacion]:
        raise DatoInvalidoError(
            campo=CRITERIO_CATEGORIA_REFUERZO, valor=categoria,
            motivo="las categorias de la Tabla 5.10.1-1 son "
                   + ", ".join(sorted(tabla[situacion])),
        )

    tabulado = float(tabla[situacion][categoria])
    filas_mp = RECUBRIMIENTO_MP_EQUIVALENCIA.get(situacion)
    if filas_mp is None:
        # NO se sigue adelante saltandose el cruce. Una fila sin
        # correspondencia declarada significa que las dos transcripciones se
        # han desincronizado, y seguir seria calcular el recubrimiento con
        # una sola de las dos fuentes creyendo que se compararon.
        raise DatoInvalidoError(
            campo="situacion", valor=situacion,
            motivo="no tiene fila equivalente declarada en "
                   "RECUBRIMIENTO_MP_EQUIVALENCIA, y sin ella no se puede "
                   "cruzar la tabla de AASHTO con la del Manual de Puentes",
        )
    if categoria == CATEGORIA_ACERO_SIN_RECUBRIR:
        # El corpus peruano TABULA esta columna, asi que el valor sale de el y
        # no de AASHTO: es lo que pedia NOR-PUE-10, y no basta con nombrarlo en
        # la etiqueta. Se toma el mayor por la misma regla de conflicto de
        # Sec. 0.2 -- hoy coinciden en las 21 filas, y si alguna edicion las
        # separa, la regla ya esta escrita y no hay que decidir en caliente.
        #
        # EL CRUCE SE HACE POR MAPA Y NO POR NOMBRE DE CLAVE. Antes la guarda
        # era `situacion in RECUBRIMIENTO_MP_MM`, y en las 8 filas de la
        # familia de pilotes -- donde el Manual traduce "shafts" por "Pilares"
        # y ademas parte en dos la fila de ambiente corrosivo -- daba False:
        # el cruce se saltaba sin avisar y la red de seguridad cubria 14 filas
        # de 21 mientras el comentario afirmaba que las cubria todas.
        tabulado = max([tabulado]
                       + [float(RECUBRIMIENTO_MP_MM[fila])
                          for fila in filas_mp])
    requisitos = requisitos_durabilidad_concreto()
    factor, origen_factor = factor_recubrimiento_por_ac(
        a_c_max=requisitos.a_c_max)
    modificado = tabulado * factor
    # Piso absoluto sobre las barras principales: 1.0 in. Es lo que impide que
    # el 0.8 lleve el recubrimiento por debajo de la pulgada.
    piso_aplicado = modificado < RECUBRIMIENTO_MP_PISO_MM - TOL_UMBRAL_NORMATIVO
    valor = max(modificado, RECUBRIMIENTO_MP_PISO_MM)
    corpus = ("[N] Manual de Puentes Tabla 2.9.1.5.5.3-1 (aceros no "
              "protegidos), coincidente con AASHTO LRFD Tabla 5.10.1-1 "
              "columna A"
              if categoria == CATEGORIA_ACERO_SIN_RECUBRIR else
              "[C] AASHTO LRFD Tabla 5.10.1-1 columna " + str(categoria)
              + ": el Manual de Puentes no CALLA sobre el acero protegido "
                "-- su num. 2.9.1.5.5.4 lo trata --, pero solo autoriza usar "
                "la tabla con acero protegido 'Para exposicion interior'. "
                "Fuera de ella el corpus peruano no tabula, y el hueco lo "
                "cubre AASHTO por la Via 1 de Sec. 0.2. Es una lectura "
                "declarada, no neutra: la contraria mantendria la columna de "
                "aceros no protegidos y esta en la sensibilidad de "
                "'" + CRITERIO_CATEGORIA_REFUERZO + "'")
    detalle = {"situacion": situacion, "categoria": categoria,
               "tabulado_mm": tabulado, "factor_ac": factor,
               "origen_factor": origen_factor, "piso_aplicado": piso_aplicado,
               "corpus": corpus, "requisitos": requisitos,
               "filas_mp": filas_mp}
    return valor, detalle


def recubrimiento_de_diseno(*, condicion: str) -> RecubrimientoDiseno:
    """
    Regla de conflicto de Sec. 0.2: **rige el recubrimiento MAYOR entre AASHTO
    y E.060**. Devuelve los dos operandos, el adoptado, cual de las dos normas
    gobierna, y la cadena con que se produjo el lado AASHTO.

    Por que no basta con tomar el de E.060. Sec. 0.2 adopta la Via 1 (AASHTO
    LRFD de extremo a extremo) y declara la durabilidad como EXCEPCION: E.060
    entra, pero no desplaza a AASHTO, se compara con el. Una regla del maximo
    evaluada con un solo operando no es una regla -- por eso esta funcion
    exige los dos lados.

    QUE CAMBIO Y POR QUE (cluster C07; conflicto #3 del plan de correcciones).
    El lado AASHTO era un valor declarado, 75 mm en las tres condiciones, con
    la conclusion ya escrita: "AASHTO gobierna en los tres casos". Los 75 mm
    eran los 3.0 in de la columna A redondeados a la baja, sin el modificador
    por relacion a/c y sin decir que habia tres columnas. Con la cadena
    completa la conclusion deja de valer para las tres.

    EL RESULTADO, CONDICION POR CONDICION, para que nadie lo lea como una
    inversion general que no es. Con categoria A y el factor 0.8 de
    a/c <= 0.40, el lado AASHTO vale 76.2 x 0.8 = 61.0 mm en las tres:

        contra_suelo             E.060 70.0  AASHTO 61.0  ->  gobierna E.060
        suelo_intemperie_ge_3_4  E.060 50.0  AASHTO 61.0  ->  gobierna AASHTO
        suelo_intemperie_le_5_8  E.060 40.0  AASHTO 61.0  ->  gobierna AASHTO

    Es decir: la inversion ocurre en UNA de las tres condiciones -- la
    principal, la del concreto vaciado contra el suelo -- y en las otras dos
    AASHTO sigue gobernando, con 61.0 mm en vez de los 75 mm de antes.
    Corregir solo 75 -> 76.2, que era la correccion obvia que el conflicto #3
    prohibe, habria dejado la conclusion falsa con un numero mas exacto.

    EL EFECTO NETO, que conviene decir en voz alta: el recubrimiento adoptado
    BAJA en las tres condiciones respecto del expediente anterior (75 mm ->
    70.0 / 61.0 / 61.0). Es lo que la norma exige una vez aplicado el
    modificador que faltaba, y no es una holgura ganada: cuando la fila de
    cloruros de la Tabla 4.2 aplica, el Art. 4.4.2 remite al recubrimiento de
    7.7 y el Art. 7.7.5.1 manda AUMENTAR este minimo -- ver
    `aviso_ambiente_corrosivo`, que consume el mismo dato y lo dice sin
    condicional cuando el dato ya esta declarado.

    E.060 Art. 7.7.5.1 (ambiente corrosivo) manda AUMENTAR este resultado y no
    dice cuanto; ese aumento se declara aparte (`aviso_ambiente_corrosivo`).
    """
    e060 = recubrimiento_e060_mm(condicion=condicion)
    aashto, detalle = _recubrimiento_aashto_detallado(condicion=condicion)
    if aashto > e060 + TOL_UMBRAL_NORMATIVO:
        adoptado, origen = aashto, "AASHTO"
    else:
        adoptado, origen = e060, "E.060"
    return RecubrimientoDiseno(
        paso=_paso_recubrimiento(condicion=condicion, e060=e060, aashto=aashto,
                                 adoptado=adoptado, origen=origen,
                                 detalle=detalle),
        condicion=condicion, e060_mm=e060, aashto_mm=aashto,
        adoptado_mm=adoptado, origen=origen,
        criterio_aashto=CRITERIO_TABLA_RECUBRIMIENTO,
        numeral=f"{NUMERAL_RECUBRIMIENTO} / {NUMERAL_RECUBRIMIENTO_MP} / "
                f"{NUMERAL_REGLA_RECUBRIMIENTO}",
        situacion=detalle["situacion"], categoria=detalle["categoria"],
        tabulado_mm=detalle["tabulado_mm"], factor_ac=detalle["factor_ac"],
        piso_aplicado=detalle["piso_aplicado"], corpus_tabla=detalle["corpus"],
        origen_factor=detalle["origen_factor"],
        requisitos=detalle["requisitos"],
    )


def _paso_recubrimiento(*, condicion, e060, aashto, adoptado, origen,
                        detalle):
    """
    El paso de memoria del recubrimiento, con la regla del mayor a la vista.

    LA ELECCION QUE HAY QUE IMPRIMIR NO ES «cuanto recubrimiento»: es DE QUE
    CORPUS sale. Los dos regulan la misma pieza y ninguno deroga al otro, de
    modo que un revisor que vea «70 mm» sin ver el otro numero no puede saber
    si se cumplieron las dos normas o solo una. Es ademas la casilla donde el
    modificador por relacion a/c invierte la conclusion (NOR-AAS-05, conflicto
    vinculante n.3 del plan v12): sin el, AASHTO gobernaba las tres
    condiciones; con el, E.060 gana una.
    """
    return paso(
        "F8.RECUBRIMIENTO",
        codigo="8.R",
        que="Recubrimiento del refuerzo, por la regla del mayor",
        formula="recubrimiento = max(E.060 Art. 7.7.1, AASHTO 5.10.1 con su "
                "modificador por relacion a/c)",
        formula_cita_id="E060.7.7.1",
        citas_textuales=("E060.7.7.1", "AASHTO_LRFD_9.T5.10.1-1"),
        sustitucion=(
            Magnitud("E.060", e060, "mm",
                     f"Art. 7.7.1, condicion «{condicion}»",
                     cifras=CIFRAS_FACTOR),
            Magnitud("AASHTO", aashto, "mm",
                     f"{detalle['corpus']}, fila «{detalle['situacion']}», "
                     f"categoria {detalle['categoria']}: "
                     f"{detalle['tabulado_mm']} mm tabulados x factor "
                     f"{detalle['factor_ac']} por relacion a/c",
                     cifras=CIFRAS_FACTOR)),
        resultado=Magnitud("recubrimiento adoptado", adoptado, "mm",
                           f"el mayor de los dos; gobierna {origen}",
                           cifras=CIFRAS_FACTOR),
        umbral=Umbral(
            descripcion="recubrimiento minimo del refuerzo",
            valor=adoptado, unidad="mm",
            cita_id="E060.7.7.1",
            caracter="EXIGENCIA en los dos corpus",
            aplicacion="REGLA DEL MAYOR (Sec. 0.2): cumplir el menor de los "
                       "dos dejaria el otro incumplido. Este numero es el "
                       "MINIMO ANTES del aumento por ambiente corrosivo que "
                       "el Art. 7.7.5.1 manda y no cuantifica; ese aumento se "
                       "declara aparte y no se calcula aqui.",
            criterio_aplicado=CRITERIO_TABLA_RECUBRIMIENTO),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.CUMPLE,
            margen=abs(aashto - e060), unidad="mm",
            explicacion=f"gobierna {origen}; la diferencia entre los dos "
                        f"corpus es la holgura con que se cumple el que no "
                        f"gobierna"),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="corpus normativo que gobierna el recubrimiento",
            valor=f"{origen}, {adoptado} mm",
            entre=(f"E.060 Art. 7.7.1: {e060} mm",
                   f"AASHTO 5.10.1: {aashto} mm"),
            de_donde="la regla del mayor de la Sec. 0.2 del expediente",
            por_que=detalle["origen_factor"] or
                    "los dos corpus regulan la misma pieza y ninguno deroga "
                    "al otro",
            cita_id="AASHTO_LRFD_9.T5.10.1-1",
            clave_criterio=CRITERIO_TABLA_RECUBRIMIENTO),),
    )


def aviso_ambiente_corrosivo() -> str:
    """
    Aviso para la memoria: el recubrimiento de `recubrimiento_de_diseno` es el
    MINIMO antes del aumento por ambiente corrosivo. El aumento no se calcula
    aqui, se declara -- E.060 Art. 7.7.5.1 no fija cuanto.

    DOS CORRECCIONES DE CITA (NOR-E060-04). La primera, la forma verbal: el
    articulo imprime "debe aumentarse adecuadamente", no "aumentar
    adecuadamente", y entrecomillar lo segundo es citar mal aunque el fondo
    coincida. La segunda pesa mas: el articulo ofrece una ALTERNATIVA expresa
    -- "o debe disponerse de otro tipo de proteccion" -- que el aviso omitia,
    y que es un camino de cumplimiento distinto del que el expediente
    contempla. Con la alternativa a la vista, proteger el refuerzo (la
    categoria B o C de 'categoria_refuerzo_aashto') deja de ser solo una
    opcion de suministro y pasa a ser una forma de cumplir este articulo.
    Por eso el aviso transcribe el texto entero y no lo resume.

    Y EL AVISO EVALUA SU PROPIO ANTECEDENTE, que es lo que le faltaba. Decia
    "si el analisis quimico del EMS confirma la exposicion" -- un condicional
    cuyo antecedente el programa YA tiene resuelto en el mismo dato del que
    cuelga el factor por a/c. Dejarlo en potencial tenia una consecuencia
    concreta: en la misma corrida en que el modificador BAJA el recubrimiento
    adoptado, el aumento que la norma manda aplicar quedaba en prosa
    condicional. El Art. 4.4.2 cierra el circulo -- expuesto a cloruros ->
    Tabla 4.2 Y "los requisitos de recubrimiento minimo del concreto de 7.7"
    --, y el Art. 7.7.1 abre con la salvedad "excepto cuando se requieran
    recubrimientos mayores segun 7.7.5.1".
    """
    exposicion = _exposicion_quimica_validada()
    aplica = exposicion[CLAVE_FILAS_TABLA_4_2]["cloruros"]
    if aplica:
        cabecera = (
            "Recubrimiento: el valor adoptado es el MINIMO y HAY QUE "
            f"AUMENTARLO ({AMBIENTE_CORROSIVO_AUMENTAR}). No es un supuesto: "
            "el analisis quimico declarado en "
            f"'{CRITERIO_EXPOSICION_QUIMICA}' dice que el concreto queda "
            "expuesto a los cloruros de la Tabla 4.2, y con eso el "
            f"{NUMERAL_PROTECCION_CORROSION} manda cumplir tambien \""
            f"{PROTECCION_CORROSION_TEXTO}\". ")
    else:
        cabecera = (
            "Recubrimiento: el analisis quimico declarado en "
            f"'{CRITERIO_EXPOSICION_QUIMICA}' NO da por expuesto el concreto "
            "a los cloruros de la Tabla 4.2, de modo que el aumento de este "
            "articulo no se dispara por esa via. Queda anotado porque el "
            "ambiente corrosivo no se agota en los cloruros de esa fila. ")
    return (
        cabecera
        + f"Texto literal del articulo: \"{AMBIENTE_CORROSIVO_TEXTO}\". No "
        "fija cuanto, y ofrece la alternativa de disponer otro tipo de "
        "proteccion: las dos cosas se declaran en la memoria, no las calcula "
        "este modulo"
    )


def cuantia_minima(*, direccion: str) -> float:
    """
    Cuantia minima de refuerzo de muro, E.060 Art. 14.3.1 (pag. 133):
    horizontal >= 0.0020, vertical >= 0.0015.

    Es un MINIMO OBLIGATORIO, no un dato informativo. Sec. 9.4 lo llama
    "REFERENCIA de cuantias minimas" y el matiz es real pero no significa lo
    que parece: por la Via 1 de Sec. 0.2 el DISENO estructural es de AASHTO
    LRFD Sec. 5, de modo que E.060 no dicta cuanto acero pide la flexion. Lo
    que si hace el Art. 14.3.1, dentro de E.060, es fijar un piso, gobierne
    quien gobierne el dimensionamiento. La consecuencia practica esta en
    `cuantia_de_diseno`: el minimo se aplica como rho_diseno =
    max(rho_calculado, rho_minimo), no se imprime al pie de la memoria.

    LO QUE ESTE DOCSTRING AFIRMABA DE MAS (NOR-E060-01). Decia que el 14.3.1
    fija "un piso por debajo del cual NINGUN muro se arma". Para un muro de
    CONTENCION -- que es lo que el cabezal es -- eso no es lo que dice E.060:
    el Art. 14.8.2 remite a 14.3 y acto seguido permite exceptuarlo, "cuando
    el Ingeniero Proyectista disponga juntas de contraccion y señale
    procedimientos constructivos que controlen los efectos de contraccion y
    temperatura". La excepcion es potestativa y exige las DOS cosas a la vez.
    Este proyecto NO la invoca -- no hay juntas de contraccion ni
    procedimientos constructivos declarados en el expediente -- y por eso el
    minimo se aplica entero. Lo que cambia es el argumento: se aplica porque
    nadie ejercio la excepcion, no porque la norma no la ofrezca. La
    diferencia importa el dia que el proyectista quiera ejercerla:
    `nota_excepcion_refuerzo_minimo` le dice que tiene que declarar para eso.

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


def nota_excepcion_refuerzo_minimo() -> str:
    """
    La frase para la memoria: el minimo de E.060 Art. 14.3.1 se aplica entero
    porque el proyecto no ejercio la excepcion que el Art. 14.8.2 ofrece para
    muros de contencion, no porque la norma no la tenga.

    Sin esta nota, la memoria presentaba el minimo como inexcusable, que es
    afirmar de la norma algo que la norma no dice (NOR-E060-01). Con ella, el
    revisor ve las dos cosas: el numero que se aplico y la puerta que existia
    y no se uso.
    """
    return (
        "Cuantia minima de refuerzo del muro: se aplica integra la de "
        f"{NUMERAL_CUANTIA_MIN}. El {NUMERAL_EXCEPCION_REFUERZO_MIN_MURO} "
        f"permite exceptuarla en muros de contencion -- \"{EXCEPCION_REFUERZO_MIN_MURO_TEXTO}\" "
        "--, y este expediente NO ejerce esa excepcion: no declara juntas de "
        "contraccion ni procedimientos constructivos de control de "
        "contraccion y temperatura, que son las dos condiciones que el "
        "articulo exige a la vez. Ejercerla es una decision del proyectista y "
        "obliga a declarar las dos en el expediente"
    )


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
    m (250 mm), E.060 Art. 14.8.3. Umbral INCLUSIVO ("mayor o igual a").
    `espesor` en metros.

    Este es el umbral del acero POR TEMPERATURA Y CONTRACCION, y solo de el.
    El del refuerzo en dos capas es otro y esta 50 mm mas abajo: ver
    `requiere_refuerzo_dos_capas`.
    """
    return espesor >= ESPESOR_TEMPERATURA_DOS_CARAS - TOL_UMBRAL_NORMATIVO


def requiere_refuerzo_dos_capas(*, espesor: float) -> bool:
    """
    True si el refuerzo va en DOS CAPAS en cada direccion: espesor > 0.200 m
    (200 mm), E.060 Art. 14.3.2. Umbral ESTRICTO ("mayor que"), a diferencia
    del de temperatura. `espesor` en metros.

    POR QUE EXISTE ESTA FUNCION (NOR-E060-02). El modulo decidia el acero en
    dos caras con un solo umbral, el de 250 mm del Art. 14.8.3, y la memoria
    imprimia "Acero por temperatura en UNA cara" para todo espesor menor. Pero
    E.060 tiene DOS umbrales sobre cosas distintas: el 14.3.2 exige el
    refuerzo "en cada direccion colocado en dos capas paralelas a las caras
    del muro" a partir de 200 mm -- con una sola excepcion, los muros de
    sotanos, que un cabezal no es --, y el 14.8.2 remite expresamente a todo
    14.3, de modo que un muro de contencion lo hereda. Entre 200 y 250 mm el
    muro lleva dos capas por 14.3.2 aunque el acero por temperatura vaya en
    una cara por 14.8.3, y la memoria decia lo contrario.
    """
    return espesor > ESPESOR_DOS_CAPAS_REFUERZO + TOL_UMBRAL_NORMATIVO


def nota_temperatura_dos_caras(*, espesor: float) -> str:
    """
    La frase para la memoria y el plano: en que cara o caras va el refuerzo,
    con su numeral. No es una verificacion con umbral contra un dato del
    proyecto -- son dos reglas de detalle que se disparan con el espesor -- y
    por eso sale como texto y no como `Verificacion`.

    Los dos umbrales van juntos en la misma frase a proposito: separarlos era
    lo que permitia leer "en UNA cara" y creer que el muro entero lleva una
    sola parrilla.
    """
    if requiere_temperatura_dos_caras(espesor=espesor):
        temperatura = (
            f"Acero por temperatura en AMBAS caras: espesor {espesor:.3f} m "
            f">= {ESPESOR_TEMPERATURA_DOS_CARAS:.3f} m "
            f"({NUMERAL_TEMPERATURA_DOS_CARAS})"
        )
    else:
        temperatura = (
            f"Acero por temperatura en UNA cara: espesor {espesor:.3f} m < "
            f"{ESPESOR_TEMPERATURA_DOS_CARAS:.3f} m "
            f"({NUMERAL_TEMPERATURA_DOS_CARAS})"
        )
    if requiere_refuerzo_dos_capas(espesor=espesor):
        capas = (
            f"; refuerzo en cada direccion en DOS CAPAS paralelas a las caras: "
            f"espesor {espesor:.3f} m > {ESPESOR_DOS_CAPAS_REFUERZO:.3f} m "
            f"({NUMERAL_DOS_CAPAS_REFUERZO}, {EXCEPCION_DOS_CAPAS_REFUERZO})"
        )
    else:
        capas = (
            f"; refuerzo en una capa por direccion: espesor {espesor:.3f} m "
            f"<= {ESPESOR_DOS_CAPAS_REFUERZO:.3f} m "
            f"({NUMERAL_DOS_CAPAS_REFUERZO})"
        )
    return temperatura + capas


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
    R4 / R5: alternativa en concreto ciclopeo. Piedra desplazadora <= 30 % del
    volumen total de concreto ciclopeo (E.060 Art. 22.10, pags. 194-195) y
    f'c de la matriz >= el MAYOR de los dos minimos que rigen sobre el mismo
    material. Admitido para muros de gravedad; Sec. 9.4 la llama "opcion
    realista para cabezales pequenos".

    DOS MINIMOS, Y EL EXPEDIENTE DECLARABA EL MENOR (NOR-E060-07). E.060
    Art. 22.10 pide 10 MPa para la matriz. La Tabla 503-07 del EG-2013 -- cuya
    Seccion 503 es la que este proyecto cita para cabezales, y que es
    especificacion vial del MTC -- clasifica el concreto ciclopeo como Clase G
    y le pide 14 MPa. Los dos rigen sobre una obra vial peruana y ninguno
    deroga al otro, asi que se aplica el mayor: la misma regla del maximo que
    Sec. 0.2 usa para el recubrimiento y `M7.altura_recubrimiento` para la
    cobertura. Citar solo el 10 MPa era quedarse con el requisito mas bajo de
    los dos disponibles, y de los dos el que NO es de una norma vial.

    `fc_matriz` en MPa, `fraccion_piedra` en tanto por uno (0.30, no 30).
    """
    return (
        Verificacion(
            cumple=fc_matriz >= CICLOPEO_FC_MATRIZ_MIN_APLICABLE - TOL_UMBRAL_NORMATIVO,
            numeral=f"{NUMERAL_CICLOPEO_APLICABLE} "
                    f"[DISCREPA DE LA HOJA DE RUTA: "
                    f"{CICLOPEO_DISCREPANCIA_HOJA_RUTA}]",
            valor_obtenido=fc_matriz,
            valor_admisible=CICLOPEO_FC_MATRIZ_MIN_APLICABLE,
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

    DOS TRAMPAS QUE EL ENSAMBLE VA A ENCONTRAR, escritas aqui porque es donde
    se van a pisar y no en la ficha de una auditoria:

      LAS FORMULAS SON IMPERIALES (MAT-O9, MAT-X8). La 9a ed. no publica
      edicion SI: su C5.1 declara "These specifications use kips and ksi
      units", y el 0.0316 de la Ec. 5.7.3.3-3 no es una constante fisica sino
      1/raiz(1000), el factor de conversion psi->ksi. El criterio guardaba
      esas expresiones bajo claves "Vc_kN" y "dv_m" -- etiquetas SI sobre
      formulas en kip y pulgada --, y hoy las claves llevan la unidad real en
      el nombre ("Vc_kip", "dv_in"). Este modulo opera en SI: el ensamble
      tendra que convertir en la frontera, y declarar la conversion, no
      cambiarle el nombre a las variables.

      BETA TIENE DOS EXPRESIONES (NOR-AAS-06). La Ec. 5.7.3.4.2-1 vale solo
      "for sections containing at least the minimum amount of transverse
      reinforcement specified in Article 5.7.2.5"; sin ese refuerzo minimo
      rige la Ec. 5.7.3.4.2-2, que ademas depende del parametro de
      espaciamiento de fisura sxe. Un muro de cabezal delgado sin estribos
      cae normalmente en el segundo caso, de modo que el ensamble tiene que
      contestar primero si el muro lleva el refuerzo transversal minimo: la
      expresion no se elige por costumbre.

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
# 9.x - QUE FUNCIONES DE ESTE MODULO NO TIENEN LLAMADOR DE PRODUCCION, Y POR
#       QUE. Una sola escritura, como ya se hace con los criterios
#       (`criterios_adoptados.criterios_sin_consumidor`).
# ===========================================================================
# La razon de cada una vivia repartida entre la auditoria, el manifiesto, el
# docstring del modulo y la nota que la CLI imprime, y ninguno de los cuatro
# era la fuente: los tres hallazgos "deliberado documentado" de este cluster
# (SIS-B-17, SIS-B-20, SIS-B-21) son el mismo defecto de reparto. Aqui la
# razon se escribe una vez, y la CLI y la memoria la leen de aqui.
#
# "Sin llamador de produccion" NO es codigo muerto: son formulas utilizables
# hoy pasandoles sus argumentos, y lo que falta es el INSUMO -- un vacio
# declarado -- o el llamador que lo ensamble. Si alguna se cablea, sale de
# esta lista en el mismo commit.
#
# LA LISTA SE MANTIENE A MANO Y NO HAY GUARDIA QUE LA ATE al estado real del
# modulo. Es la misma deuda que `criterios_sin_consumidor` cerro con un test
# (`test_lo_que_declara_sin_consumidor_de_verdad_no_tiene_consumidor`), y aqui
# esta abierta: el test que la ate va en la fase de tests, no antes. Mientras
# tanto, la comprobacion es de revision: si una funcion de este modulo no
# aparece llamada desde cli.py, gui/app.py ni otro modulo de src/modulos/,
# tiene que estar aqui. La primera version de esta lista ya nacio incompleta
# -- le faltaban siete entradas, dos de ellas de funciones creadas en el mismo
# commit -- y eso es exactamente lo que el test tendra que impedir.
FUNCIONES_SIN_CONSUMIDOR = {
    "empujes_trasdos": (
        "Ensambla el plano de empuje del trasdos y ninguna corrida lo "
        "alcanza: la CLI no lo llama porque elegir el plano de empuje "
        "(`altura_empuje`) y los factores de combinacion seria decidir por el "
        "proyectista, y el criterio 'predimensionamiento_cabezal' esta vacio. "
        "Se conserva porque es la formula, no el ensamble, lo que el "
        "expediente necesita: quien tantee un cabezal la llama con su "
        "geometria"),
    "peso_suelo_sobre_talon": (
        "Produce el W_s de P_IR. Necesita el ancho del talon, que es parte "
        "de 'predimensionamiento_cabezal', y la altura de suelo sobre el "
        "talon, que depende de donde se corte el plano de calculo y por eso "
        "entra por argumento"),
    "fuerza_inercia_muro": (
        "Mismo caso que `empujes_trasdos`, y por el mismo vacio: W_s necesita "
        "el ancho del talon, que es parte de 'predimensionamiento_cabezal'. "
        "La formula si esta implementada, que es lo que faltaba (MAT-D6)"),
    "gamma_eq": (
        "Lee el criterio 'gamma_EQ', que es vacio: hoy detendria a quien la "
        "llamara, y quien la llamaria -- el chequeo de excentricidad -- ya "
        "esta detenido antes por la geometria"),
    "verificar_estabilidad": (
        "Agrega E1-E3 (y E4-E5 si se piden) a partir de demandas ya "
        "calculadas. La CLI no la llama porque ensamblar esas demandas exige "
        "elegir el plano de empuje y los factores de combinacion, que es "
        "decidir por el proyectista -- la misma razon de `empujes_trasdos`, y "
        "la que la nota de cli.py declara"),
    "peso_propio_cabezal": (
        "Formula de geometria exacta, utilizable hoy con una geometria de "
        "tanteo; sin 'predimensionamiento_cabezal' no hay geometria de "
        "proyecto que pasarle"),
    "parametros_resistencia_art20": (
        "Aplica la regla de E.050 Art. 20 (en cohesivos phi = 0, en "
        "friccionantes c = 0) sobre los parametros del terreno de fundacion. "
        "Quien la usaria es el calculo de la fuerza resistente al "
        "deslizamiento, que la CLI no ensambla por la misma razon que el "
        "resto de la estabilidad"),
    "aplica_sobrecarga_trasdos": (
        "Comprueba la regla de la distancia H/2 para el trafico. No la llama "
        "nadie a proposito: Sec. 9.2 cierra el punto diciendo que en un "
        "cabezal bajo terraplen vial la sobrecarga SIEMPRE aplica, de modo "
        "que el pipeline usa `sobrecarga_trasdos_siempre_aplica` y esta queda "
        "para quien tenga la distancia medida y quiera comprobarlo"),
    "sobrecarga_trasdos_siempre_aplica": (
        "Declaracion para la memoria. Hoy no la imprime nadie porque la "
        "seccion de la memoria que la llevaria es la de empujes, que esta "
        "detenida"),
    "demanda_sismica_cabezal": (
        "Combina P_AE con P_IR segun el num. 2.8.1.1.14.1. Sin geometria no "
        "hay ninguno de los dos, de modo que hereda el mismo vacio"),
    "presion_contacto_base": (
        "Produce el q_actuante que `verificar_capacidad_portante` exige ya "
        "resuelto, con la rama del numeral que corresponde al terreno de "
        "fundacion. Hereda el vacio de la geometria (MAT-O16)"),
    "verificar_excentricidad_sismica": (
        "Ademas de la geometria necesita 'gamma_EQ', que es vacio propio: el "
        "limite va de B/6 a 0.4*B segun su valor"),
    "armado del num. 9.4 (ocho funciones)": (
        "`cuantia_de_diseno`, `verificar_cuantia`, `requiere_temperatura_dos_"
        "caras`, `requiere_refuerzo_dos_capas`, `nota_temperatura_dos_caras`, "
        "`espaciamiento_maximo`, `verificar_espaciamiento` y "
        "`verificar_ciclopeo` no tienen llamador "
        "porque su insumo es el diseno por flexion y corte, que se detiene en "
        "`diseno_flexion_corte` con NotImplementedError, y el espesor del "
        "elemento, que sale de 'predimensionamiento_cabezal'. La CLI registra "
        "ese bloqueo en cada corrida (SIS-B-20)"),
    "clase_exposicion_sulfatos / factor_recubrimiento_por_ac": (
        "No tienen llamador de PRODUCCION directo y no son deuda: las llama "
        "`requisitos_durabilidad_concreto` y "
        "`_recubrimiento_aashto_detallado`, que si estan en el camino de la "
        "CLI. Se declaran aparte porque son las dos piezas que un revisor va "
        "a querer ejecutar sueltas para reproducir la clasificacion de la "
        "Tabla 4.4 y el factor por a/c sin montar el recubrimiento entero"),
    "n_q_zapata_en_talud / n_s_zapata_en_talud": (
        "No tienen llamador interno porque la funcion que las usaria, "
        "`capacidad_portante_zapata_en_talud`, se detiene antes en "
        "'N_cq_N_gammaq_meyerhof': N_cq y N_gamma_q salen de FIGURAS y no de "
        "una formula transcribible. N_s se calcula aparte al leer los abacos, "
        "que es justo para lo que existe la funcion (SIS-B-21)"),
}


def funciones_sin_consumidor() -> Tuple[str, ...]:
    """
    Las familias de funciones de M9 que ningun modulo de produccion invoca,
    cada una con su razon, para que la CLI y la memoria la impriman desde un
    solo sitio en vez de repetirla.
    """
    return tuple(f"{nombre}: {razon}"
                 for nombre, razon in FUNCIONES_SIN_CONSUMIDOR.items())


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
        # Las erratas de imprenta del Manual en la cadena sismica -- son TRES
        # y la tercera esta mas abajo, con la excentricidad. Van a
        # la memoria y no solo a un docstring porque quien las va a encontrar
        # es el revisor que compare el codigo con la norma impresa, y sin
        # esta nota concluira que el codigo esta mal (MAT-O2, MAT-X2).
        f"Mononobe-Okabe, signo del denominador: {K_AE_ERRATA_MANUAL} "
        f"({NUMERAL_K_AE_MANUAL}; {NUMERAL_K_AE_AASHTO})",
        f"k_h0 en cimentacion sobre roca: {K_H0_ROCA_ERRATA} "
        f"({NUMERAL_K_H0})",
        # LA SOBRECARGA VIVA DEL TRASDOS, con sus DOS fuentes. La memoria
        # imprimia solo el numeral peruano, que fija un PISO de 0.60 m, para
        # un h_eq que la tabla de AASHTO puede llevar a 1.12 m: el lector veia
        # el numero grande citado contra la fuente del numero pequeño
        # (NOR-PUE-01, NOR-PUE-02, MAT-O1, MAT-X1).
        f"Sobrecarga viva en el trasdos: h_eq = max(piso del Manual, tabla de "
        f"AASHTO por altura y orientacion). {NUMERAL_SOBRECARGA_TRASDOS} fija "
        f"el piso -- «no menor que» -- y no tabula nada; el valor sale de "
        f"{NUMERAL_SOBRECARGA_TRASDOS_AASHTO}. La altura de entrada es la del "
        f"muro CON zapata: {NUMERAL_SOBRECARGA_TRASDOS_ALTURA}",
        f"Cual de las dos tablas de AASHTO aplica: {H_EQ_REPARTO_DE_TABLAS}",
        f"Cuando la sobrecarga se aplica: {NUMERAL_SOBRECARGA_TRASDOS_APLICA}",
        # La hipotesis del agua en el trasdos: desviacion conservadora de un
        # `shall` de AASHTO, declarada (MAT-O3, MAT-X3).
        f"Empuje bajo el nivel freatico: {HIPOTESIS_EMPUJE_BAJO_NF} "
        f"({NUMERAL_AGUA_TRASDOS_AASHTO})",
        # Inercia del muro: el termino que faltaba, y el aviso de que la
        # combinacion no es una suma (MAT-D6, MAT-X7).
        f"Demanda sismica del cabezal: no basta el empuje. El num. {NUMERAL_P_IR} "
        f"exige combinar P_AE con la inercia de la masa del muro "
        f"P_IR = k_h*(W_w + W_s), en dos casos que se investigan por separado "
        f"porque sus efectos NO son simultaneos -- 100 % P_AE + 50 % P_IR, y "
        f"50 % P_AE (no menor que el empuje activo estatico) + 100 % P_IR --, "
        f"rigiendo el mas desfavorable. La Sec. 9.2 de la hoja de ruta "
        f"desagrega la cadena sismica y NO menciona P_IR: el defecto se "
        f"reporta contra ella",
        # El limite de excentricidad: no es "el tercio central" a secas
        # (MAT-O16).
        f"Ubicacion de la resultante en la base bajo sismo: el "
        f"num. {NUMERAL_EXCENTRICIDAD_SISMICA} la acota a los dos tercios "
        f"centrales (e <= B/3) con gamma_EQ = 0.0 y a las ocho decimas "
        f"centrales (e <= 0.4*B) con gamma_EQ = 1.0, interpolando en medio. "
        f"Es una verificacion que la tabla de FS de Sec. 9.3 no trae, porque "
        f"E.050 no la escribe, y depende de 'gamma_EQ', que sigue vacio",
        # La tercera errata, que mueve un numero y por eso pesa mas que las
        # otras dos.
        f"Excentricidad sismica, 'tercio central': {EXCENTRICIDAD_ERRATA_MANUAL} "
        f"({NUMERAL_EXCENTRICIDAD_SISMICA}; {NUMERAL_EXCENTRICIDAD_SISMICA_AASHTO}; "
        f"el limite estatico que sirve de ancla, en {NUMERAL_EXCENTRICIDAD_ESTATICA})",
        # La presion de contacto tiene dos ramas y el proyecto usa la de suelo.
        f"Presion de contacto en la base: el num. {NUMERAL_PRESION_CONTACTO} "
        f"la reparte por terreno de fundacion -- uniforme sobre el ancho "
        f"efectivo B - 2e en SUELO, lineal sobre B en ROCA -- y no la "
        f"escribe el numeral sismico. La rama que aplica a este cabezal es la "
        f"de suelo, coherente con las filas de sitio declaradas en 'F_pga'",
        # Por que E.030 no gobierna este cabezal. El descarte se defendia solo
        # por periodo de retorno, que es la via discutible (NOR-E030-03).
        f"E.030 no gobierna el diseno sismico de este cabezal, y el argumento "
        f"es de AMBITO antes que de periodo de retorno: {E030_AMBITO_LECTURA} "
        f"({NUMERAL_E030_AMBITO}; {NUMERAL_E030_ESTRUCTURAS_NO_EDIFICACION})",
        f"Texto literal del Art. 7.3 de E.030, que es el que cede el paso: "
        f"\"{E030_ART_7_3_TEXTO}\" ({NUMERAL_E030_ESTRUCTURAS_NO_EDIFICACION})",
        # LA CLASE DE SITIO, y por que este expediente no se atribuye
        # ninguna. Es la correccion de S13/S14 (conflicto #8): el expediente
        # afirmaba la Clase de Sitio F y ninguna de las dos fuentes la
        # sostiene -- pero lo que decide no es el silencio, es que las dos
        # PROHIBEN suponer la clase E o F sin dato geotecnico. El texto va a
        # la memoria entero, con las dos citas literales, porque un revisor
        # que solo lea "indeterminada" no sabra que ya se busco
        # (NOR-AAS-02, SIS-B-01, SIS-D-01, NOR-MEM-03).
        f"{CLASE_DE_SITIO_INDETERMINADA} ({NUMERAL_CLASE_SITIO_AASHTO})",
        f"Texto literal de la prohibicion, en el articulado y no en un "
        f"comentario: \"{CLASE_SITIO_EF_NO_SUPUESTA_TEXTO}\" "
        f"({NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA}). El Manual de Puentes lo "
        f"endurece a un futuro imperativo: "
        f"\"{CLASE_SITIO_EF_NO_SUPUESTA_MP_TEXTO}\" "
        f"({NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA_MP})",
        f"El deber positivo que abre la misma clausula, y que es lo que "
        f"convierte a la clase de sitio en un dato pendiente de ensayo y no "
        f"en un valor que el proyectista adopte: "
        f"\"{CLASE_SITIO_INVESTIGACION_TEXTO}\" "
        f"({NUMERAL_CLASE_SITIO_INVESTIGACION})",
        f"{CLASE_DE_SITIO_POR_QUE_DEJA_DE_DECIRSE} "
        f"({NUMERAL_CLASE_SITIO_MP}; {NUMERAL_LICUEFACCION_AASHTO}; "
        f"{NUMERAL_E030_S5})",
        f"{CLASE_DE_SITIO_COHERENCIA_INTERNA} "
        f"({NUMERAL_LICUEFACCION_ESPECTRO})",
        f"{CLASE_DE_SITIO_QUE_LA_CIERRA} "
        f"({NUMERAL_RESPUESTA_DE_SITIO_AASHTO}; "
        f"{NUMERAL_RESPUESTA_DE_SITIO_MP})",
        # La homonimia, que llega a la memoria por dos caminos distintos y
        # sin relacion entre si (NOR-VOC-04). Se imprime aqui, pegada a la
        # cadena sismica, porque es donde el lector se encuentra el termino;
        # el glosario completo de las cuatro homonimias del expediente lo
        # imprime M11 (`bloque_homonimias`), leyendo esta MISMA declaracion.
        homonimia_como_texto(HOMONIMIA_CLASE_F),
        # Lo que E.030 SI dice sobre este sitio, y que el expediente tenia
        # archivado como referencia muerta (NOR-E030-02).
        f"Perfil de suelo S5 de E.030: aunque la norma no gobierne el diseno "
        f"del cabezal, su clasificacion del sitio trae una consecuencia que "
        f"el expediente tiene que atender. Texto literal: \"{E030_S5_TEXTO}\" "
        f"({NUMERAL_E030_S5}). {E030_S5_LECTURA}",
        # Las funciones de este modulo que ningun llamador de produccion
        # alcanza, con su razon, desde un solo sitio (SIS-B-17/20/21).
        *(f"Sin llamador de produccion -- {linea}"
          for linea in funciones_sin_consumidor()),
    )
