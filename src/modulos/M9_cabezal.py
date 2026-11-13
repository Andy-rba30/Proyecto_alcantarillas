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

--- T-7b --- LO QUE ESTE ENCABEZADO DESCRIBE DE 9.2 Y 9.3 ES LA CAJA DE
HERRAMIENTAS DE ANTES, que se conserva con sus tests. Desde T-7b la
estabilidad de cada cabezal la ENSAMBLA `ensamble_estabilidad` (bloque del
final del modulo): cargas con su brazo, combinaciones y las filas E1 a E3 en
DOS MARCOS que no se cruzan -- el LRFD de AASHTO 11.6, que rige, y el de los
factores de seguridad de E.050, que informa --. Y de los vacios que se listan
mas abajo, cuatro dejaron de serlo: beta vale 0, el brazo del incremento
sismico 0.6 [C], y la pendiente del relleno y la friccion muro-relleno son
opcionales (sin declarar salen de la geometria de cada cabezal y de phi).
Las funciones sueltas `k_ae_del_proyecto` y `empujes_trasdos` siguen
pidiendo los cuatro angulos por criterio y no tienen llamador.

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
(`k_ae_del_proyecto`, `empujes_trasdos`) se detienen con
`CriterioPendienteError` hasta que el expediente cierre esos vacios.

Por que la geometria entra por argumento y no por criterio
----------------------------------------------------------
Un cabezal se predimensiona tanteando: se propone B, se verifica volteo y
deslizamiento, se corrige B. Por eso toda funcion de calculo acepta
`GeometriaCabezal` explicita. --- T-7a --- Hasta T-7a habia ademas UNA
geometria por criterio para todo el corredor ('predimensionamiento_cabezal',
vacio, leido por `geometria_adoptada`), que era INF-5.1.15: un cabezal «del
proyecto» con el NF «del punto». Se retiro: el criterio guarda hoy las
REGLAS del predimensionamiento, y la geometria la propone
`predimensionar_cabezal` para cada extremo de cada punto, dimension por
dimension con su origen (regla o declarada en `--datos-externos`). Ver el
bloque «9.0» al final del modulo.

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
    from src.modelos import CondicionAnalisis
    from src.modulos.M9_cabezal import (cadena_sismica, k_ae_mononobe_okabe,
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

from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src.constantes_fisicas import GAMMA_AGUA_KN_M3, PIE_EN_METROS
from src.constantes_normativas import (AMBIENTE_CORROSIVO_AUMENTAR,
                                   NUMERAL_CORTANTE_MUROS_E060,
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
                                   CICLOPEO_DOS_MINIMOS,
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
                                   NUMERAL_KA_COULOMB,
                                   KA_COULOMB_DECLARACION,
                                   REGIMEN_CORTANTE_EN_EL_PLANO,
                                   REGIMEN_CORTANTE_PERPENDICULAR,
                                   REGIMENES_CORTANTE_MURO,
                                   FS_CODIGO,
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
from src.modelos import (CIFRAS_FACTOR, CadenaSismica, CasoDemandaSismica,
                     CombinacionCarga, EleccionDeProyecto, Magnitud,
                     TipoDeVeredicto, Umbral, Veredicto, paso,
                     CondicionAnalisis, CuantiaRefuerzo, DatoInvalidoError,
                     DemandaSismicaCabezal, DisenoNoFactibleError,
                     EmpujeMononobeOkabe, EmpujesTrasdos, EstabilidadCabezal,
                     FuerzaInerciaMuro, GeometriaCabezal, PasoSismico,
                     PresionContactoBase, RecubrimientoDiseno,
                     RequisitosDurabilidad,
                     ReferenciaNormativa, Verificacion)
from src.tolerancias import (TOL_ANGULO_CUNA, TOL_UMBRAL_NORMATIVO,
                             TRAMOS_CUNA_DE_TANTEO)

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
# El Art. 11.10.10.2 esta en la hoja de ruta desde EXT-0 (v8 §9.4) y en el
# registro desde EXT-6 (`constantes_normativas.NUMERAL_CORTANTE_MUROS_E060`,
# con 11.10.1, 11.10.2 y 11.10.10.3); lo que sigue pendiente es CABLEAR su
# valor con caso patron (EXT-7). Ver el criterio
# 'cortante_alto_muro_e060_art_11_10_10_2'.
NUMERAL_CORTANTE_ALTO = (NUMERAL_CORTANTE_MUROS_E060["cuantia_horizontal_min"]
                         + " (cortante alto en el plano; piso declarado en "
                           "'cortante_alto_muro_e060_art_11_10_10_2')")
# El piso VERTICAL bajo el mismo regimen (EXT-M-05 / R95-031) y las dos
# lecturas del plano del cortante que deciden si el regimen rige.
NUMERAL_CORTANTE_ALTO_VERTICAL = (
    NUMERAL_CORTANTE_MUROS_E060["cuantia_vertical_min"]
    + " (ec. 11-32, cortante alto en el plano; piso declarado en "
      "'cuantia_vertical_cortante_alto_e060_art_11_10_10_3')")
NUMERAL_CORTANTE_EN_EL_PLANO = NUMERAL_CORTANTE_MUROS_E060["en_el_plano"]
NUMERAL_CORTANTE_PERPENDICULAR = (
    NUMERAL_CORTANTE_MUROS_E060["perpendicular_al_plano"]
    + " (cortante perpendicular al plano: diseño por 11.12, el regimen de "
      "11.10.10 no rige)")

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
CRITERIO_REGIMEN_CORTANTE = "regimen_cortante_muro_e060_art_11_10_2"
CRITERIO_CUANTIA_VERTICAL_CORTANTE_ALTO = (
    "cuantia_vertical_cortante_alto_e060_art_11_10_10_3")
# LAS FILAS QUE LA TABLA DE SEC. 9.3 EXIGE, por su codigo y en su orden,
# derivadas de `constantes_normativas.FS` y no escritas aqui (EXT-M-07).
# `EstabilidadCabezal.estable` se mide contra esta tupla. E6 (la
# excentricidad sismica, `verificar_excentricidad_sismica`) NO esta: no es
# fila de esa tabla -- E.050 no la escribe; sale del Manual de Puentes -- y
# quien la quiera exigir la pasa ampliando `exigidas` en
# `verificar_estabilidad`. La decision esta en docs/decisiones_diferidas.md.
EXIGIDAS_SEC_9_3 = tuple(FS_CODIGO[clave] for clave in FS)

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

    NO ES EL Ka DEL EMPUJE ESTATICO (EXT-M-06): desde EXT-7 `empujes_trasdos`
    usa el de Coulomb del Manual de Puentes (`k_a_coulomb`), que es el de la
    fuente primaria y el homogeneo con K_AE; con i = beta = delta = 0 los dos
    coinciden exactamente, y en cuanto alguno deja de ser cero difieren.
    Esta funcion se conserva como PATRON: es la forma reducida que la hoja de
    ruta escribia en su Sec. 9.2 (enmendada en EXT-0, `DIS-HR-KA-COULOMB`) y
    el caso limite contra el que se contrasta Mononobe-Okabe.
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

    Que Ka usa el empuje estatico, y la sobrecarga: EL DE COULOMB del Manual
    de Puentes, num. 2.4.4.1.5.3 (`k_a_coulomb`, la formulacion de
    Mononobe-Okabe con k_h = k_v = 0), y no el de Rankine. Se declara aqui,
    en el punto de uso, porque la hoja de ruta decia otra cosa (EXT-M-06):
    su Sec. 9.2 escribia "Ka = tan^2(45 - phi/2)" sin decir de donde salia,
    y hasta EXT-7 esta funcion la seguia -- empuje estatico y sobrecarga con
    `ka_rankine` mientras el incremento sismico iba con Mononobe-Okabe, que
    es Coulomb con aceleracion: dos familias de coeficiente sobre el mismo
    muro, decision declarada en dos docstrings y autorizada por ninguna
    fuente. La fuente primaria del marco elegido en Sec. 9.1 escribe Coulomb
    (ecs. 2.4.4.1.5.3-1 y -2, pag. impresa 135; cita `MP.2.4.4.1.5.3`), y
    con trasdos vertical, delta = 0 y relleno horizontal se reduce
    EXACTAMENTE a la forma que la hoja escribia (diferencia medida
    -5.6e-17). EXT-0 enmendo la v8; la discrepancia queda registrada y
    resuelta como `DIS-HR-KA-COULOMB`, y la memoria la imprime por
    `condicion_normativa_cabezal`.

    Consecuencias que conviene leer antes de usarla: (1) los cuatro angulos
    de Sec. 9.2 son entrada tambien en condicion ESTATICA -- antes solo phi
    lo era -- y un vacio la detiene; (2) `K_A` y `mononobe_okabe.K_A` son
    el MISMO numero, tambien con angulos no nulos, de modo que el incremento
    K_AE - K_A resta dos coeficientes homogeneos; (3) con i = beta =
    delta = 0 ningun numero se mueve respecto de Rankine, y `ka_rankine` se
    conserva como patron del caso limite. Dentro de las ventanas declaradas
    la diferencia no es un matiz: en el bloque C de CP-9 (i = 5, beta = 5,
    delta = 17 grados) el COEFICIENTE de Coulomb da +9.7 % sobre Rankine, y
    barriendo las cuatro ventanas enteras va de -11.1 % (phi = 30, i = beta
    = 0, delta = 22.7) a +44.4 % (phi = 38, i = beta = 10, delta = 0).

    LA RESULTANTE DE COULOMB ESTA INCLINADA, Y AQUI SE TOMA ENTERA COMO
    HORIZONTAL (auditoria adversarial de EXT-7). P_A = gamma*H^2*K_A/2 es la
    resultante sobre el trasdos, que actua a delta de la normal al paramento
    (Figura 2.4.4.1.5.3-1 del Manual): delta + beta respecto de la
    horizontal. Con Rankine (delta = beta = 0) era exactamente horizontal;
    con Coulomb no, y `EmpujesTrasdos` la suma integra como carga EH
    horizontal sin descomponerla en E_h = P_A*cos(delta + beta) y
    E_v = P_A*sen(delta + beta). Lo mismo le pasa a la sobrecarga (mismo
    Ka) y le pasaba ya al incremento sismico (P_AE tambien inclinado). En el
    bloque C la sobreestimacion de la horizontal es +7.9 % (1/cos 22 - 1) y
    llega a +18.8 % en el extremo de ventana (delta = 22.7, beta = 10); la
    horizontal verdadera queda solo +1.7 % sobre Rankine. La direccion NO es
    una: CONSERVADORA para E2 y E3 (mas fuerza horizontal y mas momento
    volcante) y NO conservadora para E1 en la parte de la componente
    vertical que deja de cargar sobre la base (mas normal, mas presion de
    contacto). No se descompone en EXT-7 porque `EmpujesTrasdos` no tiene
    modelo de cargas verticales del trasdos donde llevar E_v --- el vertical
    que hoy existe es la subpresion ---; queda diferido con simbolo
    (EXT-7-04 en docs/decisiones_diferidas.md) y declarado en la memoria por
    `KA_COULOMB_DECLARACION`.

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
    # Coulomb (MP 2.4.4.1.5.3), con los cuatro angulos declarados: es el
    # mismo K_A que resta el incremento sismico. CriterioPendienteError en
    # el primero de los cuatro que siga vacio, tambien en condicion estatica.
    K_A = k_a_coulomb(phi_grados=ca.valor(CRITERIO_PHI_RELLENO),
                      i_grados=ca.valor(CRITERIO_I_RELLENO),
                      beta_grados=ca.valor(CRITERIO_BETA_MURO),
                      delta_grados=ca.valor(CRITERIO_DELTA_MURO))

    E_a = empuje_activo_estatico(gamma_relleno=gamma, k_a=K_A,
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
        gamma_relleno=gamma, k_a=K_A, H=altura_empuje,
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
        K_A=K_A,
        incremento_sismico=incremento,
        z_incremento=z_incremento,
        mononobe_okabe=mo,
        numeral=NUMERAL_9_2,
        h_eq_sobrecarga=h_eq,
        orientacion_muro=ds.valor("orientacion_muro_respecto_al_trafico"),
        numeral_sobrecarga=(f"{NUMERAL_SOBRECARGA_TRASDOS} + "
                            f"{NUMERAL_SOBRECARGA_TRASDOS_AASHTO}"),
        numeral_k_a=NUMERAL_KA_COULOMB,
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
# que produce `servicio._bloqueo` dice exactamente cual falta.
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
    metodo = ca.valor(CRITERIO_ESTABILIDAD_GLOBAL)   # CriterioPendienteError
    # --- T-7b --- Declarar el metodo no lo implementa: el analisis de
    # superficies de falla no esta en este programa. Era un AssertionError
    # desnudo, que no desciende de `ErrorProyecto` y tumbaba la corrida.
    raise MetodoNoEvaluableError(
        "E4, estabilidad global del muro",
        "analisis de equilibrio limite (Bishop modificado, Janbu "
        "simplificado o Spencer; AASHTO LRFD 11.6.3.7)",
        f"el metodo declarado ('{metodo}') exige la estratigrafia completa "
        "del EMS y un programa de superficies de falla: se resuelve fuera "
        "de este software y su resultado se adjunta al expediente",
        rotulo=MOTIVO_METODO_NO_EVALUABLE_CABEZAL)


def verificar_talud(*, condicion: CondicionAnalisis) -> Verificacion:
    """
    E5 - Estabilidad del talud: FS >= 1.50 estatico / 1.25 sismico (E.050
    Art. 30.3).

    Mismo vacio que E4 ('metodo_estabilidad_global') y no el mismo chequeo:
    E4 mira la masa que envuelve al muro, E5 el talud del terraplen que lo
    soporta, y Sec. 9.3 las lista como dos filas con numerales distintos.
    """
    fs_requerido(verificacion="talud", condicion=condicion)
    metodo = ca.valor(CRITERIO_ESTABILIDAD_GLOBAL)   # CriterioPendienteError
    raise MetodoNoEvaluableError(   # --- T-7b --- era un AssertionError
        "E5, estabilidad del talud",
        "analisis de equilibrio limite del talud con la estructura "
        "cargandolo (E.050 Art. 30)",
        f"el metodo declarado ('{metodo}') se resuelve fuera de este "
        "software, con la estratigrafia del EMS",
        rotulo=MOTIVO_METODO_NO_EVALUABLE_CABEZAL)


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


def _es_numero_finito(x: object) -> bool:
    """True para un int o float finito; un bool no es un numero."""
    return (not isinstance(x, bool) and isinstance(x, (int, float))
            and math.isfinite(x))


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
    factores = ca.valor(CRITERIO_MEYERHOF)   # CriterioPendienteError mientras falte
    # --- T-7b --- CON los factores declarados, la formula del numeral (era
    # un AssertionError desnudo): N_q = 0, y N_c y N_gamma reemplazados por
    # N_cq y N_gamma_q, que el proyectista lee de las Figuras 2.8.1.3.1.2c-1
    # y -2 del Manual de Puentes y declara. E.050 Art. 20: en friccionantes
    # c = 0 y solo cuenta el termino de N_gamma_q.
    if not hasattr(factores, "get") or not (
            _es_numero_finito(factores.get("N_cq"))
            and _es_numero_finito(factores.get("N_gamma_q"))):
        raise DatoInvalidoError(
            campo=CRITERIO_MEYERHOF, valor=factores,
            motivo="se esperan los dos factores leidos de las Figuras "
                   "2.8.1.3.1.2c-1 y -2: {'N_cq': ..., 'N_gamma_q': ...}")
    if not (B > 0 and gamma > 0 and c >= 0):
        raise DatoInvalidoError(
            campo="B", valor=(B, gamma, c),
            motivo="ancho y peso especifico positivos y cohesion no negativa")
    # El termino de sobrecarga lleva N_q = 0 (`n_q_zapata_en_talud`): no suma.
    return c * factores["N_cq"] + gamma * B * factores["N_gamma_q"] / 2


def verificar_estabilidad(*, geometria: GeometriaCabezal,
                          condicion: CondicionAnalisis,
                          q_actuante: float, q_ultima: float,
                          momento_estabilizante: float,
                          momento_volcante: float,
                          fuerza_resistente: float,
                          fuerza_actuante: float,
                          incluir_globales: bool = False,
                          exigidas: Tuple[str, ...] = EXIGIDAS_SEC_9_3
                          ) -> EstabilidadCabezal:
    """
    Las verificaciones de Sec. 9.3 para UNA condicion, a partir de las
    demandas ya calculadas por el llamador.

    Resuelve E1, E2 y E3, que son las que salen de las fuerzas y momentos
    del cabezal. E4 y E5 NO se omiten (EXT-M-07): quedan REGISTRADAS como
    pendientes en el objeto, con el criterio que las bloquea
    ('metodo_estabilidad_global') en `motivos_pendientes`, y por eso
    `estable` es False aunque las tres resueltas cumplan -- lo que cumple es
    `estabilidad_interna_cumple`. Con `incluir_globales=True` se intentan y
    la llamada se detiene con `CriterioPendienteError` en ese criterio: se
    deja opcional para que el expediente pueda cerrar la estabilidad interna
    mientras el analisis de taludes viaja por su cuenta en el EMS, sin que
    eso haga desaparecer las dos filas de la tabla ni las convierta en
    cumplidas.

    `exigidas` son las filas contra las que `estable` se mide: por defecto
    las cinco de la tabla de FS (`EXIGIDAS_SEC_9_3`). E6 -- la excentricidad
    sismica de `verificar_excentricidad_sismica` -- no es fila de esa tabla
    y no entra por defecto; quien la exija la añade y queda como pendiente
    hasta que la resuelva.

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

    # Las dos filas globales, cuando no se incluyen, quedan pendientes CON su
    # motivo: la memoria imprime de que criterio dependen, no una fila vacia.
    presentes = {v.codigo for v in verificaciones}
    motivos = tuple((FS_CODIGO[clave], CRITERIO_ESTABILIDAD_GLOBAL)
                    for clave in ("estabilidad_global", "talud")
                    if FS_CODIGO[clave] in exigidas
                    and FS_CODIGO[clave] not in presentes)

    return EstabilidadCabezal(condicion=condicion, geometria=geometria,
                              verificaciones=tuple(verificaciones),
                              exigidas=tuple(exigidas),
                              numeral=NUMERAL_9_3,
                              motivos_pendientes=motivos)


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

    Los pisos del regimen de cortante EN EL PLANO (11.10.10.2 horizontal,
    ec. 11-32 del 11.10.10.3 vertical) y la pregunta previa del plano
    (11.10.2 / 11.10.1): ver `cuantia_de_diseno` y los criterios
    'regimen_cortante_muro_e060_art_11_10_2',
    'cortante_alto_muro_e060_art_11_10_10_2' y
    'cuantia_vertical_cortante_alto_e060_art_11_10_10_3'. Este modulo NO
    calcula cortante, y por eso los tres quedan declarados como vacios y no
    resueltos en silencio.
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


def _minimo_de_cuantia_aplicable(*, direccion: str,
                                 cortante_alto: bool) -> Tuple[float, str,
                                                              Optional[str],
                                                              Optional[str]]:
    """
    El minimo que rige en una direccion, y de donde sale: (minimo, numeral,
    clave del criterio [A] que lo DECIDIO o None si es [N] puro, regimen
    declarado o None si la ficha no se abrio). Con cortante perpendicular el
    numero es el del 14.3.1 y aun asi la clave es la del regimen: lo eligio
    una declaracion, no la norma sola. Es el unico sitio donde se contesta la
    pregunta, para que `verificar_cuantia` y `cuantia_de_diseno` no puedan
    contestarla distinto (EXT-M-05).

    Sin cortante alto: Art. 14.3.1, [N] puro. Con cortante alto, en este
    orden y deteniendose en el primer vacio:

      1. EN QUE PLANO actua el cortante ('regimen_cortante_muro_e060_art_
         11_10_2'). E.060 11.10.2 restringe 11.10.3 a 11.10.10 al cortante
         EN EL PLANO del muro; 11.10.1 manda el perpendicular a las losas de
         11.12. Perpendicular: ni 11.10.10.2 ni .3 rigen, el minimo es el
         del 14.3.1 y el numeral lo dice.
      2. En el plano, el PISO de la direccion: horizontal, el 0.0025 del
         11.10.10.2 ('cortante_alto_muro_e060_art_11_10_10_2'); vertical, la
         ec. (11-32) del 11.10.10.3 ('cuantia_vertical_cortante_alto_e060_
         art_11_10_10_3'), que este software NO evalua -- faltan hm, lm y la
         rho_h requerida por 11.10.10.1 -- y por eso se declara.
    """
    minima = cuantia_minima(direccion=direccion)      # DatoInvalidoError si no es direccion
    if not cortante_alto:
        return minima, NUMERAL_CUANTIA_MIN, None, None

    regimen = ca.valor(CRITERIO_REGIMEN_CORTANTE)     # CriterioPendienteError mientras falte
    if regimen not in REGIMENES_CORTANTE_MURO:
        # Segunda linea: la puerta (categoria) ya lo rechaza; aqui es un dato
        # del expediente que no puede ser (SIS-E-05 / ficha EXT-5-02).
        raise DatoInvalidoError(
            campo=CRITERIO_REGIMEN_CORTANTE, valor=regimen,
            motivo="las lecturas del plano del cortante son "
                   + ", ".join(REGIMENES_CORTANTE_MURO))
    if regimen == REGIMEN_CORTANTE_PERPENDICULAR:
        # El numero es el del 14.3.1, pero QUIEN LO DECIDIO fue la
        # declaracion [A] del regimen: se atribuye a ella, no a [N] puro
        # (auditoria adversarial de EXT-7).
        return (minima,
                f"{NUMERAL_CUANTIA_MIN} / {NUMERAL_CORTANTE_PERPENDICULAR}",
                CRITERIO_REGIMEN_CORTANTE, regimen)

    if direccion == "horizontal":
        clave, numeral = CRITERIO_CORTANTE_ALTO, NUMERAL_CORTANTE_ALTO
    else:
        clave, numeral = (CRITERIO_CUANTIA_VERTICAL_CORTANTE_ALTO,
                          NUMERAL_CORTANTE_ALTO_VERTICAL)
    # CriterioPendienteError mientras el piso siga sin declarar. No hay rama
    # alternativa a proposito: sin el valor no se puede armar un muro en esta
    # condicion, y caer al 14.3.1 seria elegir el minimo menor en silencio.
    minima = float(ca.valor(clave))
    return minima, f"{NUMERAL_CUANTIA_MIN} / {numeral}", clave, regimen


def verificar_cuantia(*, cuantia_provista: float, direccion: str,
                      cortante_alto: bool) -> Verificacion:
    """
    R1 (horizontal) / R2 (vertical): contraste de la cuantia PROVISTA en el
    plano contra el minimo que rige en esa direccion: el de E.060 Art. 14.3.1
    o, con cortante alto EN EL PLANO del muro, el piso del regimen de
    11.10.10 (11.10.10.2 horizontal, ec. 11-32 del 11.10.10.3 vertical).

    `cortante_alto` NO tiene valor por defecto, por la misma razon que en
    `cuantia_de_diseno`: la pregunta se contesta una sola vez por muro y no
    la contesta esta funcion. Hasta EXT-7 este contraste ignoraba el
    argumento y comparaba siempre contra el 14.3.1, de modo que un armado
    vertical de 0.0020 «cumplia» bajo un regimen que le pide 0.0025.

    Es la comprobacion a posteriori, y no sustituye a `cuantia_de_diseno`:
    esta funcion detecta que un armado ya dibujado incumple el minimo, y
    aquella impide que el minimo se pierda al producir el armado. Las dos
    hacen falta -- la cuantia que llega aqui puede venir de un plano que
    nadie paso por `cuantia_de_diseno` -- y por eso las dos leen el minimo
    del mismo sitio, `_minimo_de_cuantia_aplicable`.
    """
    minima, numeral, criterio, _regimen = _minimo_de_cuantia_aplicable(
        direccion=direccion, cortante_alto=cortante_alto)
    codigo = "R1" if direccion == "horizontal" else "R2"
    return Verificacion(
        cumple=cuantia_provista >= minima - TOL_UMBRAL_NORMATIVO,
        numeral=numeral,
        valor_obtenido=cuantia_provista,
        valor_admisible=minima,
        criterio_aplicado=criterio,      # None: [N] puro, Art. 14.3.1
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
    dos regimenes de minimos -- el general del Art. 14.3.1 (0.0020 / 0.0015)
    y el de cortante en el plano de 11.10.10 -- y elegir el mas bajo porque
    es el unico que la hoja de ruta transcribia seria quedarse con el minimo
    menor por omision. Este modulo NO calcula cortante: el diseno por flexion
    y corte esta bloqueado entero en 'procedimiento_flexion_corte_aashto_sec5'
    (AASHTO LRFD Sec. 5, Via 1 de Sec. 0.2), asi que no hay Vu con que
    contestar la pregunta del 11.10.10.1. Se traslada a quien llama, que es
    quien tiene el diseno estructural delante:

        cortante_alto=False  el muro NO esta en la condicion de 11.10.10.1
                             (Vu > phi*Vc), y quien lo afirma lo justifica
                             en la memoria. Rige el 0.0020 / 0.0015 del
                             Art. 14.3.1.
        cortante_alto=True   se abre la cadena de abajo, que se DETIENE con
                             `CriterioPendienteError` en el primer vacio.

    LA CADENA CON CORTANTE ALTO, en el orden en que se pregunta (EXT-M-05,
    R95-031; v8 §9.4 enmendada en EXT-0):

      1. En que plano actua el cortante. E.060 11.10.2 aplica 11.10.3 a
         11.10.10 a las fuerzas cortantes EN EL PLANO del muro, y 11.10.1
         manda las PERPENDICULARES al plano a las disposiciones para losas
         de 11.12 (pag. 103). Un cabezal en voladizo bajo empuje de tierras
         trabaja perpendicular a su plano: si ese es el cortante, ni el
         11.10.10.2 ni el 11.10.10.3 rigen y el minimo es el del 14.3.1 en
         las DOS direcciones. Lo declara 'regimen_cortante_muro_e060_art_
         11_10_2', vacio: ninguna de las dos respuestas se da por defecto.
      2. En el plano, HORIZONTAL: el piso 0.0025 del 11.10.10.2, declarado
         en 'cortante_alto_muro_e060_art_11_10_10_2' (vacio).
      3. En el plano, VERTICAL: la ec. (11-32) del 11.10.10.3, rho_v =
         0.0025 + 0.5*(2.5 - hm/lm)*(rho_h - 0.0025) >= 0.0025, que no
         necesita superar la rho_h requerida por 11.10.10.1. Hasta EXT-7
         esta rama devolvia el 0.0015 del 14.3.1 -- 1.67 veces menos acero
         que el piso -- y este docstring afirmaba que el cortante alto no
         cambiaba el minimo vertical, que es lo contrario de lo que la norma
         dice (R95-031). La ecuacion NO se evalua aqui: faltan hm, lm (la
         geometria del cabezal no lleva longitud) y la rho_h requerida (sale
         de un Vu que no existe). Se declara evaluada fuera en
         'cuantia_vertical_cortante_alto_e060_art_11_10_10_3', vacio.

    `direccion` es 'horizontal' o 'vertical'. El resultado lleva el regimen
    declarado y la clave del criterio que fijo el minimo, para que la
    memoria diga en que plano actua el cortante y de donde salio el numero.
    """
    minima, numeral, criterio, regimen = _minimo_de_cuantia_aplicable(
        direccion=direccion, cortante_alto=cortante_alto)

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
        # Solo la clave del piso que SE LEYO; vacia si el minimo es el del
        # 14.3.1 (sin cortante alto, o con cortante perpendicular).
        criterio_cortante_alto=(
            criterio if criterio in (CRITERIO_CORTANTE_ALTO,
                                     CRITERIO_CUANTIA_VERTICAL_CORTANTE_ALTO)
            else ""),
        regimen_cortante=regimen,
        criterio_regimen_cortante=(CRITERIO_REGIMEN_CORTANTE
                                   if cortante_alto else ""),
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
    # El numeral llevo pegado, entre corchetes, el rotulo "[DISCREPA DE LA
    # HOJA DE RUTA: ...]" mientras DIS-HR-CICLOPEO estuvo abierta: era la
    # declaracion en el punto de uso que CLAUDE.md exige. I2 corrigio la
    # Sec. 9.4 de la v8 (escribe los dos minimos y el mayor) y la
    # discrepancia quedo RESUELTA, de modo que el rotulo pasaba a afirmar
    # algo falso. La regla de los dos minimos -- que sigue siendo la que
    # esta verificacion aplica -- queda dicha en CICLOPEO_DOS_MINIMOS.
    return (
        Verificacion(
            cumple=fc_matriz >= CICLOPEO_FC_MATRIZ_MIN_APLICABLE - TOL_UMBRAL_NORMATIVO,
            numeral=f"{NUMERAL_CICLOPEO_APLICABLE} "
                    f"[{CICLOPEO_DOS_MINIMOS}]",
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
    # --- T-7b --- LA LISTA SE ACORTA: el ensamble de estabilidad
    # (`ensamble_estabilidad`, que el servicio llama por cabezal y por
    # condicion) consume ahora la cadena sismica, Coulomb, Mononobe-Okabe,
    # h_eq, la presion de contacto, gamma_EQ, el limite de excentricidad
    # sismico, la regla de E.050 Art. 20 y los factores de seguridad. Lo que
    # queda aqui es lo que el ensamble NO usa, con su razon.
    "empujes_trasdos": (
        "El ensamble de EXT-7, que tomaba la resultante de Coulomb entera "
        "como horizontal y dejaba el plano de empuje al llamador. T-7b lo "
        "sustituye por `cargas_del_cabezal`, que la descompone sobre el "
        "plano vertical del talon (AASHTO C3.11.5.3) y usa el peso sumergido "
        "bajo el agua. Se conserva como la forma anterior, con sus tests, "
        "para quien tantee con un plano de empuje distinto; ninguna corrida "
        "la llama"),
    "peso_suelo_sobre_talon": (
        "El peso del relleno sobre el talon, de altura uniforme. "
        "`cargas_del_cabezal` lo calcula con la cuña que el talud deja sobre "
        "el talon y con el peso saturado bajo el agua, que esta no conoce. "
        "Se conserva como la pieza revisable del caso mas simple"),
    "fuerza_inercia_muro / peso_propio_cabezal / demanda_sismica_cabezal": (
        "Las formulas sueltas de la inercia del muro y de los dos casos del "
        "num. 2.8.1.1.14.1. `cargas_del_cabezal` calcula esas mismas cargas "
        "con su brazo (necesita el centro de gravedad de cada peso, que "
        "estas no dan) y `combinaciones_de_estabilidad` arma los dos casos "
        "con los mismos factores (`P_SEIS_COMBINACIONES`). Se conservan "
        "como piezas revisables una a una"),
    "verificar_estabilidad / verificar_capacidad_portante / verificar_volteo "
    "/ verificar_deslizamiento / verificar_excentricidad_sismica": (
        "Las cinco verificaciones sueltas de antes de T-7b, que comparan con "
        "los factores de seguridad de E.050 lo que el llamador les pase. El "
        "ensamble no las usa: emite sus propias verificaciones, una por fila "
        "y por marco, con el paso de memoria que dice que cargas recibio "
        "cada una -- que es justo lo que a estas les faltaba (INF-5.1.5). "
        "Se conservan con sus tests; ninguna corrida las llama"),
    "aplica_sobrecarga_trasdos": (
        "Comprueba la regla de la distancia H/2 para el trafico. No la llama "
        "nadie a proposito: Sec. 9.2 cierra el punto diciendo que en un "
        "cabezal bajo terraplen vial la sobrecarga SIEMPRE aplica, y el "
        "ensamble la aplica siempre; esta queda para quien tenga la "
        "distancia medida y quiera comprobarlo"),
    "sobrecarga_trasdos_siempre_aplica": (
        "Declaracion para la memoria; el paso de la sobrecarga del ensamble "
        "(F9.SOBRECARGA) dice lo mismo en su nota"),
    "verificar_estabilidad_global / verificar_talud": (
        "E4 y E5. El ensamble NO las llama: las imprime como diferidas al "
        "expediente con el EMS (`PENDIENTES_E4_E5`). Llamadas a mano se "
        "detienen en 'metodo_estabilidad_global' y, declarado este, con "
        "«metodo no evaluable»: el analisis de superficies de falla no esta "
        "en este programa (hasta T-7b terminaban en un AssertionError)"),
    "armado del num. 9.4 (ocho funciones)": (
        "`cuantia_de_diseno`, `verificar_cuantia`, `requiere_temperatura_dos_"
        "caras`, `requiere_refuerzo_dos_capas`, `nota_temperatura_dos_caras`, "
        "`espaciamiento_maximo`, `verificar_espaciamiento` y "
        "`verificar_ciclopeo` no tienen llamador "
        "porque su insumo es el diseno por flexion y corte, que se detiene en "
        "`diseno_flexion_corte` con NotImplementedError (T-7c). Desde T-7b "
        "las solicitaciones factoradas de cada elemento existen "
        "(`solicitaciones_por_elemento`). "
        "La CLI registra "
        "ese bloqueo en cada corrida (SIS-B-20). Desde EXT-7 las dos primeras "
        "leen ademas, con cortante alto, el plano del cortante y el piso de "
        "la direccion ('regimen_cortante_muro_e060_art_11_10_2', "
        "'cuantia_vertical_cortante_alto_e060_art_11_10_10_3'): siguen sin "
        "llamador, y por eso esos criterios no los invoca ninguna corrida"),
    "clase_exposicion_sulfatos / factor_recubrimiento_por_ac": (
        "No tienen llamador de PRODUCCION directo y no son deuda: las llama "
        "`requisitos_durabilidad_concreto` y "
        "`_recubrimiento_aashto_detallado`, que si estan en el camino de la "
        "CLI. Se declaran aparte porque son las dos piezas que un revisor va "
        "a querer ejecutar sueltas para reproducir la clasificacion de la "
        "Tabla 4.4 y el factor por a/c sin montar el recubrimiento entero"),
    "n_q_zapata_en_talud / n_s_zapata_en_talud": (
        "`capacidad_portante_zapata_en_talud` solo se alcanza con "
        "'terreno_delante_del_cabezal' = 'talud_descendente', que no es el "
        "valor de archivo, y entonces pide 'N_cq_N_gammaq_meyerhof': N_cq y "
        "N_gamma_q salen de FIGURAS del Manual de Puentes y no de una "
        "formula transcribible. N_s se calcula aparte al leer los abacos, "
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
        "(Sec. 9.1 y Tablero 2.3). Desde T-7a la embocadura es del PUNTO "
        "('embocadura_cabezal' y 'angulo_aletas', [A]): con tubo la Tabla C.2 "
        "agrupa el cabezal con y sin aleros en una fila y nada se mueve; con "
        "marco, su carta y su fila de ke tienen que ser de la banda de angulo "
        "del cabezal",
        f"Empuje hidrostatico y subpresion: con NF a 1.4 m NO son opcionales "
        f"({NUMERAL_SUBPRESION})",
        # El Ka estatico es el de Coulomb del Manual, no el tan^2 de la hoja
        # de ruta: declarado en el punto de uso (`empujes_trasdos`) y aqui,
        # para el revisor que lea la v8 antigua (EXT-M-06).
        KA_COULOMB_DECLARACION,
        # --- T-7b --- REESCRITA. La hoja de ruta afirmaba que el cabezal
        # «se apoya en el borde del terraplen, no en terreno horizontal» y
        # exigia siempre la zapata en talud; con la geometria que T-7a
        # propone no es asi, y lo declara 'terreno_delante_del_cabezal'.
        f"Terreno delante de la zapata: el cabezal se desplanta bajo el "
        f"terreno del pie del muro, que es el fondo del cauce, y el talud "
        f"del terraplen SUBE detras de el. La capacidad portante es por eso "
        f"la de terreno horizontal (AASHTO LRFD 10.6.3.1.2a), con el "
        f"empotramiento que quede bajo la socavacion "
        f"('terreno_delante_del_cabezal' [A] = horizontal). La zapata en "
        f"talud ({NUMERAL_ZAPATA_TALUD_E050} y {NUMERAL_ZAPATA_EN_TALUD}) "
        f"queda para el cabezal que si tenga un terreno que desciende "
        f"delante; la hoja de ruta la exigia para todos y se corrigio",
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
        f"reporta contra ella. Desde T-7b el ensamble de cada cabezal la "
        f"arma entera, con sus dos casos",
        # El limite de excentricidad: no es "el tercio central" a secas
        # (MAT-O16).
        f"Ubicacion de la resultante en la base bajo sismo: el "
        f"num. {NUMERAL_EXCENTRICIDAD_SISMICA} la acota a los dos tercios "
        f"centrales (e <= B/3) con gamma_EQ = 0.0 y a las ocho decimas "
        f"centrales (e <= 0.4*B) con gamma_EQ = 1.0, interpolando en medio. "
        f"Es una verificacion que la tabla de FS de Sec. 9.3 no trae, porque "
        f"E.050 no la escribe: desde T-7b es la fila E2 del marco LRFD en "
        f"condicion sismica, y depende de 'gamma_EQ' [A] (0.50 de archivo)",
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


# ===========================================================================
# --- T-7a --- 9.0 EL CABEZAL POR PUNTO: EMBOCADURA, GEOMETRIA Y ALEROS
# ===========================================================================
# Cierra INF-4.1, INF-4.2, INF-4.3 e INF-5.1.15. Hasta aqui la Fase 9 era
# «del proyecto»: una sola `GeometriaCabezal`, leida de un criterio vacio,
# para todos los puntos, mientras el NF que entra en sus empujes era el de
# cada punto. Desde T-7a:
#
#   * la EMBOCADURA es del punto (`embocadura_del_punto`) y se resuelve antes
#     de la Fase 4, porque en un marco elige la banda de filas del HDS-5 que
#     su embocadura declarada tiene que respetar
#     (`verificar_coherencia_embocadura_cajon`) y entra a la proteccion de
#     entrada de la Fase 6;
#   * el cabezal de CADA EXTREMO de cada punto dimensionado se predimensiona
#     con las reglas declaradas de 'predimensionamiento_cabezal' [A] sobre
#     lo que las fases 4, 6 y 7.B ya resolvieron (`extremos_del_conducto`,
#     `predimensionar_cabezal`, `predimensionar_aleros`), y cualquier
#     dimension se puede pisar por punto en `--datos-externos`;
#   * la compatibilidad con el conducto, y los minimos con numero que una
#     dimension declarada puede violar, son VERIFICACIONES (CB1 a CB7) y no
#     una frase en la ficha del criterio;
#   * la longitud entre cabezales queda cerrada con el relleno que retienen
#     los dos (ficha T6-01), sin sustituir a la que uso la hidraulica.
#
# LAS CORRECCIONES DE LA AUDITORIA ADVERSARIAL (2026-11-13), en una linea
# cada una: los aleros miden distinto con esviaje (H1); el dentellon se mide
# desde el terreno del pie, la misma referencia del desplante (H3); CB6 y CB7
# (H4); el talud muere en el relleno retenido y hay longitud de metrado
# (H6); la regla del tipo se mide sobre la altura total y se avisa (H7); los
# dos minimos de normas de edificacion son [N→] (H8, dudoso 4); el origen
# «derivada» y los avisos con su causa (H9).
#
# Lo que NO hace, y es de T-7b y T-7c: ensamblar cargas, verificar la
# estabilidad (E1-E6) o armar. La geometria sale con la interfaz que esas
# funciones ya aceptan (`GeometriaCabezal` con talon, espesores y zapata).

from src.constantes_normativas import (BANDAS_ALETAS_CAJON_A1,  # noqa: E402
                                       BANDAS_ALETAS_CAJON_C2,
                                       CAJON_A1_SIN_ALETAS,
                                       CAJON_C2_SIN_ALETAS,
                                       ESPESOR_MIN_ZAPATA_CONCRETO_SIMPLE_M,
                                       NUMERAL_ZAPATA_CONCRETO_SIMPLE)
from src.dominios import MILIMETROS_POR_METRO  # noqa: E402
from src.modelos import (ORIGEN_DIMENSION_DECLARADA,  # noqa: E402
                         ORIGEN_DIMENSION_DERIVADA,
                         ORIGEN_DIMENSION_REGLA, Aleros, CabezalDelPunto,
                         Familia, LimiteNumericoError, PasoDeMemoria,
                         DimensionDeCabezal, EmbocaduraDelPunto,
                         ExtremoDelConducto, LosaDeEntrega, CIFRAS_MAGNITUD,
                         FormaSeccion, MetodoLongitud)
from src.modulos.M2_material import espesor_pared  # noqa: E402
from src.modulos.M6_proteccion import (EMBOCADURA_CABEZAL_CON_ALEROS,  # noqa: E402
                                       EMBOCADURA_CABEZAL_RECTO)

CRITERIO_EMBOCADURA_CABEZAL = "embocadura_cabezal"
CRITERIO_ANGULO_ALETAS = "angulo_aletas"
CRITERIO_MARGEN_SOCAVACION = "margen_zapata_bajo_socavacion_m"
CRITERIO_DENTELLON = "dentellon_losa_entrega"
CRITERIO_TALUD_TERRAPLEN = "talud_terraplen"
CRITERIO_EMBOCADURA_CAJON = "embocadura_cajon"
CRITERIO_KE_CAJON = "ke_entrada_cajon"
# --- T-7a, correcciones (H8 y dudoso 4) --- los dos minimos de normas de
# edificacion aplicados por analogia al cabezal vial: [N→], no [N].
CRITERIO_DESPLANTE_MIN = "profundidad_cimentacion_min_cabezal_m"
CRITERIO_PERALTE_ZAPATA_ARMADA = "peralte_min_zapata_armada_m"
# El recubrimiento del refuerzo inferior de la zapata armada, contra el
# suelo: E.060 7.7.1 a), la fila de `RECUBRIMIENTO` que la §0.2 de la hoja de
# ruta admite por la excepcion de durabilidad.
CONDICION_RECUBRIMIENTO_ZAPATA = "contra_suelo"

EMBOCADURAS_DEL_CABEZAL = (EMBOCADURA_CABEZAL_CON_ALEROS,
                           EMBOCADURA_CABEZAL_RECTO)
EXTREMO_ENTRADA = "entrada"
EXTREMO_SALIDA = "salida"
EXTREMOS = (EXTREMO_ENTRADA, EXTREMO_SALIDA)
TIPO_VOLADIZO = "voladizo_armado"
TIPO_GRAVEDAD = "gravedad_ciclopeo"
TIPOS_DE_CABEZAL = (TIPO_VOLADIZO, TIPO_GRAVEDAD)
NUMERAL_9_0 = "Sec. 9 (cabezal por punto, T-7a)"
CITA_PROFUNDIDAD_CIMENTACION = "E050.26.2#PROFUNDIDAD"
CITA_PERALTE_ZAPATA_ARMADA = "E060.15.7#PERALTE"
CITA_ZAPATA_CONCRETO_SIMPLE = "E060.22.7.4#ZAPATA"
CITA_CICLOPEO_LIMITES = "E060.22.10.2#CICLOPEO"
CITA_CONVENCION_ALEROS = "HDS5_3ED.SIMBOLOS#THETA_W"

# Las dimensiones que el proyectista puede declarar por punto en
# `--datos-externos` (clave `cabezal_declarado`), en m. La validacion de
# forma y dominio es `validar_cabezal_declarado`; aqui, solo los nombres.
DIMENSIONES_DECLARABLES = (
    "altura_total_m", "profundidad_desplante_m", "longitud_m",
    "espesor_corona_m", "espesor_base_muro_m", "ancho_zapata_m",
    "espesor_zapata_m", "ancho_punta_m", "longitud_aleros_m",
    "altura_final_aleros_m", "espesor_aleros_m", "longitud_losa_m",
    "espesor_losa_m", "profundidad_dentellon_m",
)
CAMPO_TIPO_DECLARADO = "tipo"
# --- T-7a, integracion (decision del dueño del 2026-11-13) --- El angulo del
# alero LARGO (el que forma alfa + theta con la bajada del talud), en grados
# con la pared del barril: el remedio del alero largo de un cruce esviado
# -- 8.1 m en C-01 con 30 grados -- es declararlo menor de ese lado (aleros
# asimetricos). No es una dimension en m: se valida como angulo, en [0, 90).
CAMPO_ANGULO_ALERO_LARGO = "angulo_alero_largo_grados"
ANGULOS_DECLARABLES = (CAMPO_ANGULO_ALERO_LARGO,)


def _exigir_angulo(campo: str, x: object, que: str,
                   id_punto: Optional[str] = None) -> float:
    """Un angulo de aleros con la pared del barril: finito y en [0, 90)."""
    if not (_finito(x) and x >= 0
            and math.cos(math.radians(x)) > TOL_UMBRAL_NORMATIVO):
        raise DatoInvalidoError(
            campo, valor=x, id_punto=id_punto,
            motivo=f"{que}: se espera un angulo finito en [0, 90) grados con "
                   "la pared del barril (a 90 el alero esta en el plano del "
                   "muro)")
    return float(x)


# ---------------------------------------------------------------------------
# Guardias de segunda linea (forma MAT-D13: condicion en positivo y negada)
# ---------------------------------------------------------------------------

def _finito(x: object) -> bool:
    return (not isinstance(x, bool) and isinstance(x, (int, float))
            and math.isfinite(x))


def _exigir_positivo(campo: str, x: object, que: str,
                     id_punto: Optional[str] = None) -> float:
    if not (_finito(x) and x > 0):
        raise DatoInvalidoError(campo, valor=x, id_punto=id_punto,
                                motivo=f"{que}: se espera un numero finito "
                                       "mayor que cero")
    return float(x)


def _exigir_finito(campo: str, x: object, que: str,
                   id_punto: Optional[str] = None) -> float:
    if not _finito(x):
        raise DatoInvalidoError(campo, valor=x, id_punto=id_punto,
                                motivo=f"{que}: se espera un numero finito")
    return float(x)


def _en_banda(angulo: float, banda: Tuple[float, float]) -> bool:
    """`angulo` dentro de [min, max] con la tolerancia normativa nombrada."""
    minimo, maximo = banda
    return (minimo - TOL_UMBRAL_NORMATIVO <= angulo
            <= maximo + TOL_UMBRAL_NORMATIVO)


# ---------------------------------------------------------------------------
# La embocadura del punto (perfil: entra a la Fase 4 y a la Fase 6)
# ---------------------------------------------------------------------------

def embocadura_del_punto(*, esviaje_grados: float,
                         familia: Optional[Familia] = None,
                         id_punto: Optional[str] = None
                         ) -> EmbocaduraDelPunto:
    """
    La embocadura de un punto: cabezal con aleros o recto
    ('embocadura_cabezal' [A]) y, con aleros, su angulo con la prolongacion
    de la pared del barril (ΘW del HDS-5) por la regla de 'angulo_aletas'
    [A]: el de por defecto, salvo que el esviaje SUPERE el umbral, y
    entonces el otro (INFORME §4.3).

    La lee el servicio ANTES de la Fase 4 y en los dos alcances: en un marco
    gobierna la banda de filas del HDS-5 que la embocadura del cajon tiene
    que respetar, y en todo punto lo que protege la Fase 6 a la entrada. Por
    eso los dos criterios son de perfil aunque la geometria sea de
    expediente.

    LA CAJA RECEPTORA NO ESTA EN EL CATALOGO (decision 3 del dueño, ficha
    T7A-02): la Lamina Nº 02-A la dibuja como la entrada de una TMC, sin
    aleros, y es la entrada habitual de un alivio de cuneta. Un punto de la
    Familia B recibe la embocadura del criterio y la corrida lo AVISA
    (`EmbocaduraDelPunto.avisos`, que sale por `InformePunto.avisos()`).

    El esviaje se valida aqui en segunda linea (M0 ya lo valida contra
    `dominios.ESVIAJE_MAX`): un NaN es falso frente a `>` igual que frente a
    `<=`, y caeria en la rama del angulo por defecto sin decir nada.
    """
    if not (_finito(esviaje_grados) and esviaje_grados >= 0):
        raise DatoInvalidoError(
            "esviaje_grados", valor=esviaje_grados, id_punto=id_punto,
            motivo="el angulo de los aleros se elige con el esviaje del "
                   "cruce, y este no es un angulo finito y no negativo")
    tipo = ca.valor(CRITERIO_EMBOCADURA_CABEZAL)
    if tipo not in EMBOCADURAS_DEL_CABEZAL:
        raise DatoInvalidoError(
            CRITERIO_EMBOCADURA_CABEZAL, valor=tipo, id_punto=id_punto,
            motivo="se espera una de " + ", ".join(EMBOCADURAS_DEL_CABEZAL))
    avisos = ()
    if familia is Familia.B:
        avisos = (
            f"Embocadura de {id_punto}: la entrada de un alivio de cuneta "
            "(Familia B) suele ser una CAJA RECEPTORA (Lamina Nº 02-A del "
            "Manual, sin aleros), que el programa NO modela: el punto recibe "
            f"«{tipo}» ('{CRITERIO_EMBOCADURA_CABEZAL}'), y con esa "
            "embocadura se calculan su perdida de entrada, su proteccion de "
            "entrada y su cabezal de entrada. Una caja receptora no tiene "
            "fila en las Tablas A.1 y C.2 del HDS-5 (ficha T7A-02)",)
    if tipo == EMBOCADURA_CABEZAL_RECTO:
        return EmbocaduraDelPunto(
            tipo=tipo, angulo_aletas=None,
            regla="cabezal recto: sin aleros",
            esviaje_grados=float(esviaje_grados),
            criterio_tipo=CRITERIO_EMBOCADURA_CABEZAL,
            criterio_angulo="", avisos=avisos)
    regla = ca.valor(CRITERIO_ANGULO_ALETAS)
    por_defecto = _exigir_positivo(
        CRITERIO_ANGULO_ALETAS, regla.get("por_defecto_grados"),
        "angulo de los aleros por defecto", id_punto)
    umbral = _exigir_finito(
        CRITERIO_ANGULO_ALETAS, regla.get("umbral_esviaje_grados"),
        "umbral de esviaje de la regla de los aleros", id_punto)
    con_esviaje = _exigir_positivo(
        CRITERIO_ANGULO_ALETAS, regla.get("con_esviaje_mayor_grados"),
        "angulo de los aleros con esviaje mayor que el umbral", id_punto)
    if esviaje_grados > umbral:
        angulo = con_esviaje
        rama = (f"esviaje {esviaje_grados:g} grados > umbral {umbral:g}: "
                f"{con_esviaje:g} grados")
    else:
        angulo = por_defecto
        rama = (f"esviaje {esviaje_grados:g} grados <= umbral {umbral:g}: "
                f"{por_defecto:g} grados (por defecto)")
    return EmbocaduraDelPunto(
        tipo=tipo, angulo_aletas=angulo,
        regla=rama, esviaje_grados=float(esviaje_grados),
        criterio_tipo=CRITERIO_EMBOCADURA_CABEZAL,
        criterio_angulo=CRITERIO_ANGULO_ALETAS, avisos=avisos)


def filas_hds5_del_cajon(embocadura: EmbocaduraDelPunto
                         ) -> Tuple[frozenset, frozenset]:
    """
    Las claves de fila de las Tablas A.1 y C.2 del HDS-5 que valen para un
    MARCO con esta embocadura: (cartas de 'embocadura_cajon', filas de
    'ke_entrada_cajon').

    Sale de las bandas que el ROTULO de cada fila imprime
    (`constantes_normativas.BANDAS_ALETAS_CAJON_A1` / `_C2`): sin aleros,
    las filas de cabezal recto; con aleros, las que contienen su angulo con
    el barril. Con un TUBO no se llama: la Tabla C.2 agrupa «Headwall or
    headwall and wingwalls» y el angulo no elige fila.
    """
    if embocadura.angulo_aletas is None:
        return CAJON_A1_SIN_ALETAS, CAJON_C2_SIN_ALETAS
    angulo = embocadura.angulo_aletas
    a1 = frozenset(k for k, bandas in BANDAS_ALETAS_CAJON_A1.items()
                   if any(_en_banda(angulo, b) for b in bandas))
    c2 = frozenset(k for k, bandas in BANDAS_ALETAS_CAJON_C2.items()
                   if any(_en_banda(angulo, b) for b in bandas))
    return a1, c2


def _describir_embocadura(embocadura: EmbocaduraDelPunto) -> str:
    if embocadura.angulo_aletas is None:
        return "cabezal recto (sin aleros)"
    return (f"cabezal con aleros a {embocadura.angulo_aletas:g} grados con "
            "la pared del barril")


def verificar_coherencia_embocadura_cajon(embocadura: EmbocaduraDelPunto, *,
                                          id_punto: Optional[str] = None
                                          ) -> Optional[str]:
    """
    Que la embocadura DECLARADA del marco ('embocadura_cajon', carta de la
    Tabla A.1; 'ke_entrada_cajon', fila de la Tabla C.2) sea la del cabezal
    del punto. Es la frase de la Sec. 9.1 de la hoja de ruta -- «ambas
    decisiones deben moverse juntas» -- llevada a una puerta.

    Solo mira lo DECLARADO: si un criterio del cajon sigue sin valor no lo
    rellena ni lo deduce -- es de T-3 y su vacio lo levanta M2/M4, con su
    nombre, como hasta ahora --. Si uno declarado es de otra banda de angulo
    que la del cabezal, `DatoInvalidoError` nombrando el par y las filas que
    SI corresponden: el control de entrada y el de salida no corren con una
    embocadura distinta de la que el cabezal dibuja. Asi, cambiar el angulo
    de los aleros NO deja intactos ke ni la carta: o la fila declarada sigue
    siendo de la banda nueva, o el punto se detiene pidiendo la que es; y
    declarada, M4 recalcula con ella. Con las filas de 30 a 75 grados y los
    aleros de la ventana de 'angulo_aletas' (30 a 60 grados) la coherencia
    se cumple siempre: la nota que devuelve es un dato del punto (JSON, paso
    9.0.0), no un aviso.

    SE DECIDE POR LA FAMILIA (la llama `servicio._fase_embocadura` con un
    punto de la Familia C) y no por la forma de la seccion, porque corre
    ANTES del bucle de MD, cuando la seccion todavia no existe. Es
    equivalente mientras M2 solo ofrezca el marco a la Familia C, y
    `tests/test_t7a_cabezal_geometria.py` lo fija.

    Devuelve una nota con las filas comprobadas, o None si no habia nada
    declarado que comprobar.
    """
    a1_ok, c2_ok = filas_hds5_del_cajon(embocadura)
    comprobadas = []
    for criterio, admisibles, tabla in (
            (CRITERIO_EMBOCADURA_CAJON, a1_ok, "Tabla A.1"),
            (CRITERIO_KE_CAJON, c2_ok, "Tabla C.2")):
        declarado = ca.valor_si_declarado(criterio)
        if declarado is None:
            continue
        if declarado not in admisibles:
            raise DatoInvalidoError(
                criterio, valor=declarado, id_punto=id_punto,
                motivo=(f"la fila declarada de la {tabla} del HDS-5 no es de "
                        f"la embocadura del cabezal ({_describir_embocadura(embocadura)}, "
                        f"'{embocadura.criterio_tipo}'"
                        + (f" y '{embocadura.criterio_angulo}'"
                           if embocadura.criterio_angulo else "")
                        + "). Filas de esa embocadura: "
                        + (", ".join(sorted(admisibles)) or
                           "ninguna: la tabla no tiene fila para ese angulo")
                        + ". Declarar una de ellas, o cambiar la embocadura "
                          "del cabezal: las dos decisiones se mueven juntas "
                          "(Sec. 9.1)"))
        comprobadas.append(f"'{criterio}' = {declarado}")
    if not comprobadas:
        return None
    return ("Embocadura del marco coherente con la del cabezal ("
            + _describir_embocadura(embocadura) + "): "
            + "; ".join(comprobadas))


# ---------------------------------------------------------------------------
# Lo que el cabezal necesita del conducto, en cada extremo
# ---------------------------------------------------------------------------

def extremos_del_conducto(*, punto, resultado, geometria,
                          socavacion=None
                          ) -> Tuple[ExtremoDelConducto, ExtremoDelConducto]:
    """
    Los dos `ExtremoDelConducto` de un punto dimensionado, leidos de lo que
    las fases anteriores ya resolvieron -- la seccion y el material de la
    Fase 4 (`ResultadoPunto`), el HW de diseño y el tirante de salida de M4,
    las cotas de 7.B (`CompatibilidadGeometrica`) y la socavacion de la Fase
    6 (`SocavacionSalida`) -- sin decidir nada otra vez.

    La clave exterior es la FISICA (altura interior + pared, MAT-D4), la
    misma de `M5.cota_clave`, trasladada a cada extremo con su solera. El
    ancho exterior lleva todas las celdas del marco: N·B + (N+1)·t.

    EL PIE DEL MURO -- la superficie del terreno desde la que se miden el
    desplante (E.050 Art. 26.1, por analogia), el dentellon de la losa y las
    alturas de los aleros: UNA referencia por extremo -- es en la entrada la
    solera, y en la salida la MAS BAJA entre la solera y el fondo del cauce
    receptor: con la salida en caida sobre el lecho (G2 lo admite), el
    terreno delante del muro baja hasta el receptor, y medir desde la solera
    dejaria la zapata y el dentellon por encima del lecho. Es la lectura
    conservadora, la misma que T-8 adopto para la referencia de la hoya
    ('referencia_profundidad_socavacion').

    El nivel de agua contra el cabezal: en la entrada, solera + HW de diseño
    (el del control que gobierna); en la salida, solera + el mayor entre el
    TW y el tirante con que M4 midio la velocidad de salida. M4 llena los
    dos siempre (EXT-3); si faltan, es un fallo del programa y no se
    sustituye por cero.
    """
    seccion = resultado.seccion
    material = resultado.material
    h = resultado.resultado_hidraulico
    altura = seccion.altura
    t = espesor_pared(material, altura)
    n = h.numero_celdas
    ancho = n * seccion.ancho_exterior(t) - (n - 1) * t
    c = altura + t
    solera_e = geometria.cota_entrada.valor
    solera_s = geometria.cota_salida
    if h.TW_m is None and h.y_salida_m is None:
        raise ValueError(
            f"el resultado hidraulico de {punto.id} no trae ni el TW ni el "
            "tirante de salida: la Fase 9 no elige un nivel de agua por su "
            "cuenta")
    tirante_salida = max(x for x in (h.TW_m, h.y_salida_m) if x is not None)
    hoya = None if socavacion is None else socavacion.cota_fondo_de_la_hoya
    origen_soc = ("" if socavacion is None else socavacion.origen)
    receptor = punto.cota_fondo_receptor
    _exigir_finito("cota_fondo_receptor", receptor,
                   "fondo del cauce receptor", punto.id)
    pie_s = min(solera_s, receptor)
    entrada = ExtremoDelConducto(
        extremo=EXTREMO_ENTRADA, cota_solera=solera_e, cota_pie=solera_e,
        origen_cota_pie=("solera de entrada (regla de "
                         "'predimensionamiento_cabezal'); cota de entrada "
                         f"{geometria.cota_entrada.rotulo}"),
        cota_clave_exterior=solera_e + c,
        cota_agua=solera_e + h.HW,
        origen_cota_agua=(f"solera + HW de diseño ({h.control_gobernante.value}"
                          f", M4) = {h.HW:.3f} m"),
        ancho_exterior=ancho, altura_interior=altura)
    salida = ExtremoDelConducto(
        extremo=EXTREMO_SALIDA, cota_solera=solera_s, cota_pie=pie_s,
        origen_cota_pie=(
            "la MAS BAJA entre la solera de salida de 7.B y el fondo del "
            "cauce receptor (columna cota_fondo_receptor): con la salida "
            "sobre el lecho, el terreno delante del muro baja hasta el "
            "receptor, y medir el desplante y el dentellon desde la solera "
            "los dejaria colgados (regla de 'predimensionamiento_cabezal')"),
        cota_clave_exterior=solera_s + c,
        cota_agua=solera_s + tirante_salida,
        origen_cota_agua=("solera + max(TW, tirante de salida de M4) = "
                          f"{tirante_salida:.3f} m"),
        ancho_exterior=ancho, altura_interior=altura,
        cota_fondo_hoya=hoya, origen_socavacion=origen_soc)
    return entrada, salida


# ---------------------------------------------------------------------------
# El predimensionamiento de UN cabezal
# ---------------------------------------------------------------------------

def _reglas() -> dict:
    """Las reglas de 'predimensionamiento_cabezal', validadas en segunda linea."""
    reglas = ca.valor(CRITERIO_GEOMETRIA)
    if not isinstance(reglas, dict):
        raise DatoInvalidoError(CRITERIO_GEOMETRIA, valor=reglas,
                                motivo="se espera el dict de reglas")
    for campo, x in reglas.items():
        if campo in ("resguardo_agua_m", "bordillo_m"):
            if not (_finito(x) and x >= 0):
                raise DatoInvalidoError(
                    CRITERIO_GEOMETRIA, valor=x,
                    motivo=f"'{campo}' tiene que ser finito y no negativo")
        else:
            _exigir_positivo(CRITERIO_GEOMETRIA, x, f"regla '{campo}'")
    return reglas


def _desplante_minimo() -> float:
    """'profundidad_cimentacion_min_cabezal_m' [N→], en segunda linea."""
    return _exigir_positivo(CRITERIO_DESPLANTE_MIN,
                            ca.valor(CRITERIO_DESPLANTE_MIN),
                            "profundidad minima de desplante del cabezal")


def _margen_socavacion() -> float:
    """'margen_zapata_bajo_socavacion_m' [C], finito y no negativo."""
    margen = ca.valor(CRITERIO_MARGEN_SOCAVACION)
    if not (_finito(margen) and margen >= 0):
        raise DatoInvalidoError(CRITERIO_MARGEN_SOCAVACION, valor=margen,
                                motivo="margen finito y no negativo")
    return float(margen)


def peralte_minimo_zapata(tipo: str) -> Tuple[float, str, str]:
    """
    El espesor MINIMO de la zapata del cabezal segun su tipo, m, con el
    texto de su origen y la cita que lo fija:

      * gravedad ciclopeo: 300 mm de E.060 22.7.4 (concreto simple, [N]);
      * voladizo armado: la altura minima sobre el refuerzo inferior de E.060
        15.7 ('peralte_min_zapata_armada_m', [N→]) mas el recubrimiento del
        refuerzo contra el suelo de E.060 7.7.1 a) (70 mm).

    Es el piso del espesor PROPUESTO (la regla H/10 gobierna por encima) y el
    umbral de CB6 cuando el espesor se DECLARA. El peralte de diseño -- con
    el recubrimiento mayor entre AASHTO y E.060 y el diametro de la barra --
    es de T-7c.
    """
    if tipo not in TIPOS_DE_CABEZAL:
        raise DatoInvalidoError(
            "tipo", valor=tipo,
            motivo="el minimo de la zapata depende del tipo de cabezal; se "
                   "espera " + " o ".join(TIPOS_DE_CABEZAL))
    if tipo == TIPO_GRAVEDAD:
        return (ESPESOR_MIN_ZAPATA_CONCRETO_SIMPLE_M,
                f"minimo de 0.30 m de concreto simple "
                f"({NUMERAL_ZAPATA_CONCRETO_SIMPLE})",
                CITA_ZAPATA_CONCRETO_SIMPLE)
    altura = _exigir_positivo(
        CRITERIO_PERALTE_ZAPATA_ARMADA,
        ca.valor(CRITERIO_PERALTE_ZAPATA_ARMADA),
        "altura minima de la zapata armada sobre su refuerzo")
    recubrimiento = (RECUBRIMIENTO[CONDICION_RECUBRIMIENTO_ZAPATA]
                     / MILIMETROS_POR_METRO)
    return (altura + recubrimiento,
            f"minimo de la zapata armada: {altura:.2f} m sobre el refuerzo "
            f"inferior (E.060 15.7, por analogia, '{CRITERIO_PERALTE_ZAPATA_ARMADA}'"
            f" [N→]) + {recubrimiento:.3f} m de recubrimiento contra el suelo "
            f"({NUMERAL_RECUBRIMIENTO} a))",
            CITA_PERALTE_ZAPATA_ARMADA)


def _dim(nombre, valor, regla, criterio, declarado,
         de=frozenset()) -> DimensionDeCabezal:
    """
    Una fila de la tabla de geometria con su ORIGEN: «declarada» si el punto
    la trae; «derivada de dimensiones declaradas» si la regla la calcula a
    partir de alguna que el punto declaro (`de`, sus nombres); y «propuesta
    por regla» solo si ninguna de sus entradas se declaro (correcciones de
    T-7a, H9: el talon con B declarado se imprimia «propuesta por regla»).
    """
    if declarado:
        return DimensionDeCabezal(nombre=nombre, valor=valor, unidad="m",
                                  origen=ORIGEN_DIMENSION_DECLARADA,
                                  regla="dato externo del punto "
                                        "(`cabezal_declarado`)")
    if de:
        return DimensionDeCabezal(
            nombre=nombre, valor=valor, unidad="m",
            origen=ORIGEN_DIMENSION_DERIVADA,
            regla=f"{regla}, con {', '.join(sorted(de))} declarado",
            criterio=criterio)
    return DimensionDeCabezal(nombre=nombre, valor=valor, unidad="m",
                              origen=ORIGEN_DIMENSION_REGLA, regla=regla,
                              criterio=criterio)


def predimensionar_aleros(*, embocadura: EmbocaduraDelPunto,
                          altura_inicial: float, espesor: float,
                          ancho_zapata: float, espesor_zapata: float,
                          talud: float, reglas: dict,
                          declaradas: Optional[dict] = None,
                          de_altura_inicial: frozenset = frozenset(),
                          de_espesor: frozenset = frozenset(),
                          id_punto: Optional[str] = None
                          ) -> Tuple[Optional[Aleros], Tuple[DimensionDeCabezal, ...], str]:
    """
    Los dos aleros de UN cabezal (INF-4.3), o None con cabezal recto.

        L_corto = (h0 - H_f) · talud / cos(alfa - theta)
        L_largo = (h0 - H_f) · talud / cos(alfa + theta)

    alfa es el angulo de los aleros con la PROLONGACION DE LA PARED DEL
    BARRIL (ΘW del HDS-5, List of Symbols, pag. impresa xix: «Flare angle of
    wingwalls with respect to extension of culvert side wall»;
    `embocadura_del_punto`) y theta el esviaje del cruce. EL TALUD DEL
    TERRAPLEN BAJA PERPENDICULAR A LA VIA, como lo modela
    `M7.longitud_conducto`, y el eje del conducto forma theta con esa
    direccion: con el cabezal normal al eje, un alero forma alfa - theta con
    la bajada del talud y el otro alfa + theta. Para bajar de h0 a H_f el
    talud avanza (h0 - H_f)·talud en planta, y cada alero lo recorre
    dividido por el COSENO de su angulo con esa direccion (por eso coseno y
    no seno: la convencion de la fuente mide desde el barril, y con el seno
    un alero paralelo, alfa -> 0, seria infinito). Con theta = 0 las dos
    longitudes son la misma, (h0 - H_f)·talud/cos(alfa). El CSV trae la
    magnitud del esviaje y no su sentido de giro: cual de los dos lados es el
    largo lo fija la planta del cruce, y los dos se llaman «corto» y «largo».

    h0 Y H_f SE MIDEN IGUAL (correcciones de T-7a, H6): son las alturas del
    alero sobre el pie, la inicial la del cabezal en su arranque (coronacion
    menos pie, bordillo incluido) y la final la de la punta. Con la cresta
    del alero paralela al talud un bordillo por encima de el, la caida del
    talud entre el arranque y la punta es exactamente h0 - H_f. Si H_f se
    leyera como la altura del TALUD en la punta (el alero sin bordillo
    alli), la caida seria h0 - bordillo - H_f y los aleros saldrian mas
    cortos: la lectura adoptada es la de MAS longitud.

    GUARDIA (forma MAT-D13): con alfa + theta >= 90 grados el alero largo
    corre paralelo al talud, o se aleja de su bajada, y no alcanza nunca la
    altura final: el denominador se anula. `LimiteNumericoError` con el par
    (alfa, theta) y lo que lo resuelve -- declarar los aleros por
    `cabezal_declarado` o un alfa menor dentro de la ventana --. Con la
    longitud declarada la formula no se evalua y no hay guardia.

    El espesor y la zapata del alero son los del cabezal en su arranque
    (regla del proyecto: el alero se desplanta con el cabezal y se
    predimensiona con sus reglas y su altura inicial, que es su maxima).
    Devuelve (aleros, dimensiones, nota). Si el talud ya esta a la altura
    final en el arranque (h0 <= H_f) no hay alero que alargar: longitud 0 y
    la nota lo dice.
    """
    declaradas = declaradas or {}
    if embocadura.angulo_aletas is None:
        return None, (), ""
    alfa = embocadura.angulo_aletas
    theta = embocadura.esviaje_grados
    if not (_finito(alfa) and alfa >= 0
            and math.cos(math.radians(alfa)) > TOL_UMBRAL_NORMATIVO):
        raise DatoInvalidoError(
            CRITERIO_ANGULO_ALETAS, valor=alfa, id_punto=id_punto,
            motivo="el angulo de los aleros con la pared del barril tiene "
                   "que estar en [0, 90): a 90 grados el alero esta en el "
                   "plano del muro y el talud no baja a lo largo de el")
    if not (_finito(theta) and theta >= 0):
        raise DatoInvalidoError(
            "esviaje_grados", valor=theta, id_punto=id_punto,
            motivo="la longitud de los aleros se mide con el esviaje del "
                   "cruce, y este no es un angulo finito y no negativo")
    largo_decl = CAMPO_ANGULO_ALERO_LARGO in declaradas
    alfa_largo = (_exigir_angulo(f"cabezal_declarado.{CAMPO_ANGULO_ALERO_LARGO}",
                                 declaradas[CAMPO_ANGULO_ALERO_LARGO],
                                 "angulo declarado del alero largo", id_punto)
                  if largo_decl else alfa)
    _exigir_positivo("talud_terraplen", talud, "talud del terraplen (H:V)",
                     id_punto)
    h_f_decl = "altura_final_aleros_m" in declaradas
    H_f = (declaradas["altura_final_aleros_m"] if h_f_decl
           else reglas["altura_final_aleros_m"])
    caida = altura_inicial - H_f
    L_decl = "longitud_aleros_m" in declaradas
    if L_decl:
        L_corto = L_largo = declaradas["longitud_aleros_m"]
    else:
        cos_largo = math.cos(math.radians(alfa_largo + theta))
        if not cos_largo > TOL_UMBRAL_NORMATIVO:
            raise LimiteNumericoError(
                (f"cabezal_declarado.{CAMPO_ANGULO_ALERO_LARGO}" if largo_decl
                 else CRITERIO_ANGULO_ALETAS),
                valor=(alfa_largo, theta), id_punto=id_punto,
                motivo=(f"con el alero largo a alfa = {alfa_largo:g} grados de "
                        f"la pared del barril y un esviaje theta = {theta:g} "
                        "grados, el alero largo forma alfa + theta = "
                        f"{alfa_largo + theta:g} grados con la bajada del "
                        "talud: corre paralelo a ella o se aleja, y no alcanza "
                        "nunca la altura final (cos(alfa + theta) se anula). "
                        "Declarar los aleros en `cabezal_declarado` "
                        f"(longitud_aleros_m, o {CAMPO_ANGULO_ALERO_LARGO} "
                        "menor de ese lado) o un alfa menor dentro de la "
                        f"ventana de '{CRITERIO_ANGULO_ALETAS}'"))
        cos_corto = math.cos(math.radians(alfa - theta))
        avance = max(caida, 0.0) * talud
        L_corto = avance / cos_corto
        L_largo = avance / cos_largo
    nota = ("" if caida > 0 else
            f"el talud ya esta a la altura final en el arranque del alero "
            f"(h0 = {altura_inicial:.3f} m <= H_f = {H_f:.3f} m): el alero no "
            "se alarga")
    e_decl = "espesor_aleros_m" in declaradas
    e = declaradas["espesor_aleros_m"] if e_decl else espesor
    aleros = Aleros(angulo_grados=alfa, angulo_largo_grados=alfa_largo,
                    esviaje_grados=float(theta),
                    longitud_corto=L_corto, longitud_largo=L_largo,
                    altura_inicial=altura_inicial, altura_final=H_f,
                    espesor=e, ancho_zapata=ancho_zapata,
                    espesor_zapata=espesor_zapata)
    de_L = frozenset(de_altura_inicial) | (
        frozenset({"altura_final_aleros_m"}) if h_f_decl else frozenset())
    sustitucion = (f"({altura_inicial:.3f} - {H_f:.3f})·{talud:g}")
    angulo_largo = (
        (DimensionDeCabezal(nombre="angulo del alero largo", valor=alfa_largo,
                            unidad="grados", origen=ORIGEN_DIMENSION_DECLARADA,
                            regla="dato externo del punto "
                                  f"(`cabezal_declarado.{CAMPO_ANGULO_ALERO_LARGO}`)"
                                  ": aleros asimetricos"),)
        if largo_decl else ())
    dims = (
        DimensionDeCabezal(nombre="angulo de los aleros", valor=alfa,
                           unidad="grados", origen=ORIGEN_DIMENSION_REGLA,
                           regla=embocadura.regla,
                           criterio=embocadura.criterio_angulo),
    ) + angulo_largo + (
        _dim("altura final de los aleros (H_f)", H_f,
             "regla 'altura_final_aleros_m'", CRITERIO_GEOMETRIA, h_f_decl),
        _dim("longitud del alero corto (alfa - theta)", L_corto,
             f"(h0 - H_f)·talud/cos(alfa - theta) = {sustitucion}/"
             f"cos({alfa:g} - {theta:g})", CRITERIO_GEOMETRIA, L_decl,
             de=de_L),
        _dim("longitud del alero largo (alfa + theta)", L_largo,
             f"(h0 - H_f)·talud/cos(alfa + theta) = {sustitucion}/"
             f"cos({alfa_largo:g} + {theta:g})", CRITERIO_GEOMETRIA, L_decl,
             de=de_L | (frozenset({CAMPO_ANGULO_ALERO_LARGO})
                        if largo_decl else frozenset())),
        _dim("espesor de los aleros", e,
             "el de la pantalla del cabezal en la corona", CRITERIO_GEOMETRIA,
             e_decl, de=de_espesor),
    )
    return aleros, dims, nota


def predimensionar_cabezal(*, extremo: ExtremoDelConducto,
                           embocadura: EmbocaduraDelPunto,
                           talud: float,
                           declaradas: Optional[dict] = None,
                           tipo_declarado: Optional[str] = None,
                           id_punto: Optional[str] = None) -> GeometriaCabezal:
    """
    La geometria PROPUESTA del cabezal de UN extremo (INF-4.2), con las
    reglas declaradas de 'predimensionamiento_cabezal' [A] y los minimos que
    las normas escriben con su numero. Cada dimension sale con su origen
    (`GeometriaCabezal.dimensiones`): «propuesta por regla», «declarada» --
    la que el punto trae en `declaradas`, que gana -- o «derivada de
    dimensiones declaradas» -- la que la regla calcula a partir de una
    declarada --.

        coronacion   = max(clave exterior + recubrimiento + bordillo,
                           nivel de agua del extremo + resguardo)
        D_f          = max(0.80 m [N→, E.050 Art. 26.2 por analogia],
                           pie - (fondo de la hoya - margen) [C, AASHTO
                           12.6.5; solo a la salida y solo si la Fase 6
                           entrego la socavacion])
        desplante    = pie - D_f
        H_c          = coronacion - desplante  (= H + e_zapata)
        tipo         = gravedad ciclopeo si H_c <= altura maxima; si no,
                       voladizo armado (H_c es la altura TOTAL, desplante
                       incluido: con altura interior >= 0.90 m la rama de
                       gravedad no se alcanza con el umbral de archivo)
        pantalla     = 0.30 m (voladizo) | H_c / 6 (gravedad), corona = base
        zapata       = B = 0.7·H_c; e = max(H_c/10, minimo del tipo: 0.30 m
                       de concreto simple, E.060 22.7.4 [N]; 0.30 m sobre el
                       refuerzo + 0.07 m de recubrimiento en el armado, E.060
                       15.7 [N→] y 7.7.1); punta = 0.33·B;
                       talon = B - punta - pantalla
        L_c          = ancho exterior del conducto + 2·empotramiento
        losa         = 1.5·D de largo, 0.30 m de espesor, sobre el terreno
                       del pie; dentellon con su base en
                       min(pie - 0.80 m [N→, Lamina Nº 04],
                           fondo de la hoya - margen [C, AASHTO 12.6.5]),
                       0.40 m de ancho

    EL TERRENO ES UNO POR EXTREMO (correcciones de T-7a, H3): el pie del
    muro (`ExtremoDelConducto.cota_pie`) es la referencia del desplante, de
    la losa y del dentellon, cuya profundidad se mide desde ese terreno como
    la cota «0.80 min.» de la Lamina Nº 04 -- no desde la cara superior de
    la losa ni desde la solera --.

    El muro se supone NORMAL al eje del conducto y de trasdos vertical
    (beta = 0). CON ESVIAJE ESO TIENE UN PRECIO, y se dice: el talud baja
    perpendicular a la via, de modo que a lo largo de un muro normal al eje
    queda a cotas distintas en sus dos extremos, Δz = L_c·sen(theta)/talud,
    y la corona horizontal no coincide con el talud en toda su longitud;
    `cabezal_del_punto` lo avisa. Los dos aleros resultan de longitudes
    distintas (`predimensionar_aleros`). La alternativa -- un cabezal
    paralelo a la via, esviado respecto del barril (Carta 11 del HDS-5) --
    queda diferida (ficha T7A-03). La estabilidad de lo propuesto NO se
    juzga aqui (T-7b): esta funcion propone, y
    `verificar_compatibilidad_cabezal` comprueba que lo propuesto -- o lo
    declarado -- remate al conducto.
    """
    declaradas = dict(declaradas or {})
    reglas = _reglas()
    for nombre, x in declaradas.items():
        if nombre in ANGULOS_DECLARABLES:
            _exigir_angulo(f"cabezal_declarado.{nombre}", x,
                           f"angulo declarado del cabezal de "
                           f"{extremo.extremo}", id_punto)
            continue
        if nombre not in DIMENSIONES_DECLARABLES:
            raise DatoInvalidoError(
                "cabezal_declarado", valor=nombre, id_punto=id_punto,
                motivo="no es una dimension declarable del cabezal: "
                       + ", ".join(DIMENSIONES_DECLARABLES
                                   + ANGULOS_DECLARABLES))
        _exigir_positivo(f"cabezal_declarado.{nombre}", x,
                         f"dimension declarada del cabezal de "
                         f"{extremo.extremo}", id_punto)
    for campo in ("cota_solera", "cota_pie", "cota_clave_exterior",
                  "cota_agua"):
        _exigir_finito(campo, getattr(extremo, campo),
                       f"{campo} del extremo {extremo.extremo}", id_punto)
    _exigir_positivo("ancho_exterior", extremo.ancho_exterior,
                     "ancho exterior del conducto", id_punto)
    dims = []
    # De que dimensiones DECLARADAS depende cada cantidad (H9): vacio =
    # sale solo de las reglas.
    de: dict = {}
    nada = frozenset()

    # 1. Desplante
    df_min = _desplante_minimo()
    df_por_socavacion = None
    margen = None
    if extremo.cota_fondo_hoya is not None:
        margen = _margen_socavacion()
        _exigir_finito("cota_fondo_hoya", extremo.cota_fondo_hoya,
                       "fondo de la hoya de socavacion", id_punto)
        df_por_socavacion = extremo.cota_pie - (extremo.cota_fondo_hoya - margen)
    df_decl = "profundidad_desplante_m" in declaradas
    if df_decl:
        D_f = declaradas["profundidad_desplante_m"]
    else:
        D_f = max(df_min, df_por_socavacion if df_por_socavacion is not None
                  else df_min)
    de["desplante"] = (frozenset({"profundidad_desplante_m"}) if df_decl
                       else nada)
    desplante = extremo.cota_pie - D_f
    dims.append(_dim(
        "profundidad de desplante (D_f)", D_f,
        (f"max({df_min:.2f} m de E.050 Art. 26.2 por analogia, pie - (fondo "
         "de la hoya - margen) de AASHTO 12.6.5)"
         if df_por_socavacion is not None else
         f"{df_min:.2f} m de E.050 Art. 26.2 por analogia (sin socavacion "
         "entregada por la Fase 6)"),
        CRITERIO_DESPLANTE_MIN, df_decl))

    # 2. Coronacion y altura total
    h_decl = "altura_total_m" in declaradas
    cor_relleno = (extremo.cota_clave_exterior
                   + reglas["recubrimiento_clave_m"] + reglas["bordillo_m"])
    cor_agua = extremo.cota_agua + reglas["resguardo_agua_m"]
    if h_decl:
        H_c = declaradas["altura_total_m"]
        coronacion = desplante + H_c
        de["H_c"] = nada
        de["corona"] = frozenset({"altura_total_m"}) | de["desplante"]
    else:
        coronacion = max(cor_relleno, cor_agua)
        H_c = coronacion - desplante
        de["H_c"] = de["desplante"]
        de["corona"] = nada
    if not H_c > 0:
        raise DatoInvalidoError(
            "altura_total_m", valor=H_c, id_punto=id_punto,
            motivo=f"la coronacion ({coronacion:.3f} msnm) no queda sobre "
                   f"el desplante ({desplante:.3f} msnm) del cabezal de "
                   f"{extremo.extremo}")
    dims.append(_dim(
        "altura total del cabezal (H_c, base de zapata a corona)", H_c,
        "coronacion - desplante, coronacion = max(clave exterior + "
        "recubrimiento + bordillo, nivel de agua + resguardo)",
        CRITERIO_GEOMETRIA, h_decl, de=de["H_c"]))
    if h_decl:
        de["H_c"] = frozenset({"altura_total_m"})

    # 3. Tipo
    if tipo_declarado is not None:
        if tipo_declarado not in TIPOS_DE_CABEZAL:
            raise DatoInvalidoError(
                "cabezal_declarado.tipo", valor=tipo_declarado,
                id_punto=id_punto,
                motivo="se espera " + " o ".join(TIPOS_DE_CABEZAL))
        tipo = tipo_declarado
        de_tipo = frozenset({CAMPO_TIPO_DECLARADO})
    else:
        tipo = (TIPO_GRAVEDAD if H_c <= reglas["altura_max_gravedad_m"]
                + TOL_UMBRAL_NORMATIVO else TIPO_VOLADIZO)
        de_tipo = nada

    # 4. Pantalla
    if tipo == TIPO_VOLADIZO:
        e_regla = reglas["espesor_pantalla_voladizo_m"]
        texto_e = "regla 'espesor_pantalla_voladizo_m'"
        de_e = de_tipo
    else:
        e_regla = H_c / reglas["divisor_espesor_gravedad"]
        texto_e = (f"H_c / {reglas['divisor_espesor_gravedad']:g} (regla "
                   "'divisor_espesor_gravedad')")
        de_e = de_tipo | de["H_c"]
    ec_decl = "espesor_corona_m" in declaradas
    eb_decl = "espesor_base_muro_m" in declaradas
    e_corona = declaradas["espesor_corona_m"] if ec_decl else e_regla
    e_base = declaradas["espesor_base_muro_m"] if eb_decl else e_regla
    de["e_corona"] = frozenset({"espesor_corona_m"}) if ec_decl else de_e
    de["e_base"] = frozenset({"espesor_base_muro_m"}) if eb_decl else de_e
    dims.append(_dim("espesor de la pantalla en la corona", e_corona,
                     texto_e, CRITERIO_GEOMETRIA, ec_decl, de=de_e))
    dims.append(_dim("espesor de la pantalla en el arranque", e_base,
                     texto_e + "; trasdos vertical", CRITERIO_GEOMETRIA,
                     eb_decl, de=de_e))

    # 5. Zapata
    B_decl = "ancho_zapata_m" in declaradas
    B = (declaradas["ancho_zapata_m"] if B_decl
         else reglas["fraccion_ancho_zapata"] * H_c)
    dims.append(_dim("ancho de la zapata (B)", B,
                     f"{reglas['fraccion_ancho_zapata']:g}·H_c (regla "
                     "'fraccion_ancho_zapata')", CRITERIO_GEOMETRIA, B_decl,
                     de=de["H_c"]))
    de["B"] = frozenset({"ancho_zapata_m"}) if B_decl else de["H_c"]
    ez_decl = "espesor_zapata_m" in declaradas
    if ez_decl:
        e_z = declaradas["espesor_zapata_m"]
        texto_ez = ""
        de_ez = nada
        criterio_ez = CRITERIO_GEOMETRIA
    else:
        e_z = H_c / reglas["divisor_peralte_zapata"]
        texto_ez = (f"H_c / {reglas['divisor_peralte_zapata']:g} (regla "
                    "'divisor_peralte_zapata')")
        de_ez = de_tipo | de["H_c"]
        criterio_ez = CRITERIO_GEOMETRIA
        piso, texto_piso, _cita = peralte_minimo_zapata(tipo)
        if e_z < piso:
            e_z = piso
            texto_ez = f"{texto_piso}, mayor que {texto_ez}"
            de_ez = de_tipo
            criterio_ez = (CRITERIO_PERALTE_ZAPATA_ARMADA
                           if tipo == TIPO_VOLADIZO else CRITERIO_GEOMETRIA)
    dims.append(_dim("espesor de la zapata", e_z, texto_ez or "-",
                     criterio_ez, ez_decl, de=de_ez))
    if not H_c > e_z:
        raise DatoInvalidoError(
            "espesor_zapata_m", valor=e_z, id_punto=id_punto,
            motivo=f"la zapata ({e_z:.3f} m) no deja muro sobre ella con la "
                   f"altura total del cabezal de {extremo.extremo} "
                   f"({H_c:.3f} m)")
    p_decl = "ancho_punta_m" in declaradas
    punta = (declaradas["ancho_punta_m"] if p_decl
             else reglas["fraccion_punta"] * B)
    dims.append(_dim("ancho de la punta", punta,
                     f"{reglas['fraccion_punta']:g}·B (regla "
                     "'fraccion_punta')", CRITERIO_GEOMETRIA, p_decl,
                     de=de["B"]))
    de["punta"] = frozenset({"ancho_punta_m"}) if p_decl else de["B"]
    talon = B - punta - e_base
    if not talon >= 0:
        raise DatoInvalidoError(
            "ancho_zapata_m", valor=B, id_punto=id_punto,
            motivo=f"el talon sale negativo en el cabezal de "
                   f"{extremo.extremo}: B = {B:.3f} m no alcanza para la "
                   f"punta ({punta:.3f} m) y la pantalla ({e_base:.3f} m)")
    dims.append(_dim("ancho del talon", talon, "B - punta - pantalla",
                     CRITERIO_GEOMETRIA, False,
                     de=de["B"] | de["punta"] | de["e_base"]))

    # 6. Longitud del muro
    L_decl = "longitud_m" in declaradas
    L_c = (declaradas["longitud_m"] if L_decl else
           extremo.ancho_exterior + 2 * reglas["empotramiento_lateral_m"])
    dims.append(_dim("longitud del muro (L_c)", L_c,
                     f"ancho exterior del conducto ({extremo.ancho_exterior:.3f}"
                     " m) + 2·empotramiento (regla 'empotramiento_lateral_m')",
                     CRITERIO_GEOMETRIA, L_decl))

    # 7. Aleros: h0 = coronacion - pie (ver `predimensionar_aleros`)
    aleros, dims_aleros, _nota = predimensionar_aleros(
        embocadura=embocadura, altura_inicial=coronacion - extremo.cota_pie,
        espesor=e_corona, ancho_zapata=B, espesor_zapata=e_z, talud=talud,
        reglas=reglas, declaradas=declaradas,
        de_altura_inicial=de["corona"], de_espesor=de["e_corona"],
        id_punto=id_punto)
    dims.extend(dims_aleros)

    # 8. Losa de entrega y dentellon, sobre el terreno del pie (H3)
    dentellon = ca.valor(CRITERIO_DENTELLON)
    prof_min = _exigir_positivo(CRITERIO_DENTELLON,
                                dentellon.get("profundidad_min_m"),
                                "profundidad minima del dentellon")
    ancho_dent = _exigir_positivo(CRITERIO_DENTELLON, dentellon.get("ancho_m"),
                                  "ancho del dentellon")
    ll_decl = "longitud_losa_m" in declaradas
    largo_losa = (declaradas["longitud_losa_m"] if ll_decl else
                  reglas["fraccion_longitud_losa"] * extremo.altura_interior)
    el_decl = "espesor_losa_m" in declaradas
    e_losa = (declaradas["espesor_losa_m"] if el_decl
              else reglas["espesor_losa_m"])
    pd_decl = "profundidad_dentellon_m" in declaradas
    terreno = extremo.cota_pie
    if pd_decl:
        prof_dent = declaradas["profundidad_dentellon_m"]
        texto_dent = ""
    elif extremo.cota_fondo_hoya is not None:
        prof_dent = max(prof_min,
                        terreno - (extremo.cota_fondo_hoya - margen))
        texto_dent = (f"base en min(pie - {prof_min:.2f} m de la Lamina Nº 04 "
                      "[N→], fondo de la hoya - margen de AASHTO 12.6.5 [C])")
    else:
        prof_dent = prof_min
        texto_dent = (f"{prof_min:.2f} m de la Lamina Nº 04 [N→] bajo el "
                      "terreno del pie (sin socavacion entregada)")
    losa = LosaDeEntrega(longitud=largo_losa, espesor=e_losa,
                         profundidad_dentellon=prof_dent,
                         ancho_dentellon=ancho_dent, cota_terreno=terreno,
                         cota_base_dentellon=terreno - prof_dent)
    dims.append(_dim("longitud de la losa de entrega", largo_losa,
                     f"{reglas['fraccion_longitud_losa']:g}·D (regla "
                     "'fraccion_longitud_losa')", CRITERIO_GEOMETRIA, ll_decl))
    dims.append(_dim("espesor de la losa de entrega", e_losa,
                     "regla 'espesor_losa_m'", CRITERIO_GEOMETRIA, el_decl))
    dims.append(_dim("profundidad del dentellon (desde el terreno del pie)",
                     prof_dent, texto_dent or "-", CRITERIO_DENTELLON,
                     pd_decl))
    dims.append(_dim("ancho del dentellon", ancho_dent,
                     "0.40 m de la Lamina Nº 04 [N→]", CRITERIO_DENTELLON,
                     False))

    return GeometriaCabezal(
        H=H_c - e_z, B=B, D_f=D_f, espesor_corona=e_corona,
        espesor_base_muro=e_base, espesor_zapata=e_z, beta_grados=0.0,
        ancho_talon=talon, longitud=L_c, tipo=tipo, id_punto=id_punto,
        extremo=extremo.extremo, cota_coronacion=coronacion,
        cota_desplante=desplante, ancho_punta=punta, aleros=aleros,
        losa=losa, dimensiones=tuple(dims))


# ---------------------------------------------------------------------------
# Compatibilidad cabezal-conducto: CB1 a CB7 (T-7a punto 4 y correcciones)
# ---------------------------------------------------------------------------

def _caracter_de(cita_id: str) -> str:
    """El caracter de una cita, leido del registro y no escrito a mano."""
    from src.normativa import registro as _registro
    return _registro.construir().cita(cita_id).caracter.value.upper()


def _verificacion_cb(*, codigo: str, extremo: str, que: str, formula: str,
                     obtenido: float, admisible: float, mayor_o_igual: bool,
                     sustitucion: tuple, resultado: Magnitud,
                     descripcion_umbral: str, cita: str, aplicacion: str,
                     criterio: Optional[str], citas: Tuple[str, ...] = (),
                     numeral: str = "") -> Tuple[dict, dict]:
    """
    Lo comun de una verificacion CB, en la forma de las G de 7.B: los
    argumentos del paso y los de la `Verificacion`. El `paso()` lo llama
    cada verificacion con su fundamento LITERAL (el indice de formulas
    localiza al emisor por el literal: `test_indice_formulas`).
    """
    if mayor_o_igual:
        cumple = obtenido >= admisible - TOL_UMBRAL_NORMATIVO
        margen = obtenido - admisible
    else:
        cumple = obtenido <= admisible + TOL_UMBRAL_NORMATIVO
        margen = admisible - obtenido
    cod = f"{codigo}.{extremo[0]}"
    kw_paso = dict(
        codigo=cod, que=f"{que} (cabezal de {extremo})",
        formula=formula, citas_textuales=(cita,) + tuple(citas),
        sustitucion=sustitucion, resultado=resultado,
        umbral=Umbral(descripcion=descripcion_umbral, valor=admisible,
                      unidad=resultado.unidad, cita_id=cita,
                      caracter=_caracter_de(cita), aplicacion=aplicacion,
                      criterio_aplicado=criterio),
        veredicto=Veredicto(
            tipo=(TipoDeVeredicto.CUMPLE if cumple
                  else TipoDeVeredicto.NO_CUMPLE),
            margen=margen, unidad=resultado.unidad,
            explicacion=("cumple con margen" if cumple else
                         "no cumple: la dimension declarada no remata al "
                         "conducto o queda bajo su minimo; corregirla en "
                         "`cabezal_declarado` o retirarla para que rija la "
                         "regla")))
    kw_verificacion = dict(
        cumple=cumple,
        numeral=(numeral or NUMERAL_9_0) + f", cabezal de {extremo}",
        valor_obtenido=obtenido, valor_admisible=admisible,
        criterio_aplicado=criterio, codigo=cod)
    return kw_paso, kw_verificacion


def verificar_compatibilidad_cabezal(*, geometria: GeometriaCabezal,
                                     extremo: ExtremoDelConducto
                                     ) -> Tuple[Verificacion, ...]:
    """
    Lo que la ficha de 'predimensionamiento_cabezal' llevaba como
    `verificacion_pendiente` -- «la geometria tiene que ser COMPATIBLE con la
    SECCION adoptada y con la altura de terraplen» --, hecho verificacion, y
    los minimos con numero que una dimension DECLARADA puede violar
    (correcciones de T-7a, H4):

        CB1  L_c >= ancho exterior del conducto           (el muro contiene la boca)
        CB2  coronacion >= clave exterior + recubrimiento  (retiene el relleno)
        CB3  coronacion >= nivel de agua + resguardo      (el agua no lo rebasa)
        CB4  D_f >= 0.80 m                  [N→] E.050 Art. 26.2, por analogia
        CB5  desplante <= fondo de la hoya - margen        [C] AASHTO 12.6.5
             (solo a la salida y solo con socavacion entregada por la Fase 6)
        CB6  espesor de la zapata >= minimo de su tipo:
             gravedad 0.30 m [N] E.060 22.7.4; voladizo armado 0.30 m sobre
             el refuerzo [N→] E.060 15.7 + 0.07 m de recubrimiento (7.7.1)
        CB7  base del dentellon <= min(terreno del pie - 0.80 m [N→, Lamina
             Nº 04], fondo de la hoya - margen [C, AASHTO 12.6.5 «extending
             below»]); el segundo, solo con socavacion entregada

    Con las dimensiones propuestas por regla cumplen por construccion; las
    que el proyectista DECLARA por punto pueden no cumplir, y entonces el
    punto lleva la verificacion incumplida con su remedio. Codigo con el
    extremo: CB1.e, CB1.s, ...
    """
    reglas = _reglas()
    ext = extremo.extremo
    v = []
    kp, kv = _verificacion_cb(
            codigo="CB1", extremo=ext,
            que="Longitud del muro frente al ancho exterior del conducto",
            formula="L_c >= ancho exterior del conducto",
            obtenido=geometria.longitud, admisible=extremo.ancho_exterior,
            mayor_o_igual=True,
            sustitucion=(Magnitud("ancho_exterior", extremo.ancho_exterior,
                                  "m", "seccion adoptada (Fase 4) con su "
                                  "pared y sus celdas", cifras=CIFRAS_MAGNITUD),),
            resultado=Magnitud("L_c", geometria.longitud, "m",
                               "longitud del muro de cabecera",
                               cifras=CIFRAS_MAGNITUD),
            descripcion_umbral="ancho exterior del conducto en planta",
            cita="MC_HHD.LAMINA_02A",
            aplicacion="LECTURA DEL PROYECTO sobre la lamina: el muro de "
                       "cabecera tiene que contener la boca del conducto; "
                       "la lamina lo dibuja asi y no lo acota",
            criterio=CRITERIO_GEOMETRIA)
    v.append(Verificacion(**kv, paso=paso("F9.DIMENSIONES", **kp)))
    kp, kv = _verificacion_cb(
            codigo="CB2", extremo=ext,
            que="Coronacion frente a la clave exterior mas el relleno "
                "retenido",
            formula="coronacion >= clave exterior + recubrimiento",
            obtenido=geometria.cota_coronacion,
            admisible=(extremo.cota_clave_exterior
                       + reglas["recubrimiento_clave_m"]),
            mayor_o_igual=True,
            sustitucion=(
                Magnitud("clave_exterior", extremo.cota_clave_exterior,
                         "msnm", "solera + altura interior + pared "
                         "(M5.cota_clave)", cifras=CIFRAS_MAGNITUD),
                Magnitud("recubrimiento", reglas["recubrimiento_clave_m"],
                         "m", "regla 'recubrimiento_clave_m' de "
                         f"'{CRITERIO_GEOMETRIA}' [A]",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud("coronacion", geometria.cota_coronacion,
                               "msnm", "coronacion del cabezal",
                               cifras=CIFRAS_MAGNITUD),
            descripcion_umbral="clave exterior mas el relleno que el muro "
                               "retiene sobre ella",
            cita="HDS5_3ED.3.3.5#ENCAJE",
            aplicacion="REGLA DEL PROYECTO [A]: la fuente manda dimensionar "
                       "los cabezales al encajar la seccion; el relleno que "
                       "el muro retiene sobre la clave lo adopta el proyecto",
            criterio=CRITERIO_GEOMETRIA)
    v.append(Verificacion(**kv, paso=paso("F9.CORONACION", **kp)))
    kp, kv = _verificacion_cb(
            codigo="CB3", extremo=ext,
            que="Coronacion frente al nivel de agua del extremo",
            formula="coronacion >= nivel de agua + resguardo",
            obtenido=geometria.cota_coronacion,
            admisible=extremo.cota_agua + reglas["resguardo_agua_m"],
            mayor_o_igual=True,
            sustitucion=(
                Magnitud("nivel_agua", extremo.cota_agua, "msnm",
                         extremo.origen_cota_agua, cifras=CIFRAS_MAGNITUD),
                Magnitud("resguardo", reglas["resguardo_agua_m"], "m",
                         "regla 'resguardo_agua_m' de "
                         f"'{CRITERIO_GEOMETRIA}' [A]",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud("coronacion", geometria.cota_coronacion,
                               "msnm", "coronacion del cabezal",
                               cifras=CIFRAS_MAGNITUD),
            descripcion_umbral="nivel de agua de diseño contra el muro mas "
                               "el resguardo",
            cita="HDS5_3ED.3.3.5#ENCAJE",
            aplicacion="REGLA DEL PROYECTO [A] (INFORME §4.2: «el agua no "
                       "desborda el muro»)",
            criterio=CRITERIO_GEOMETRIA)
    v.append(Verificacion(**kv, paso=paso("F9.CORONACION", **kp)))
    df_min = _desplante_minimo()
    kp, kv = _verificacion_cb(
            codigo="CB4", extremo=ext,
            que="Profundidad de desplante frente al minimo de E.050, por "
                "analogia",
            formula=f"D_f >= {df_min:.2f} m",
            obtenido=geometria.D_f, admisible=df_min,
            mayor_o_igual=True,
            sustitucion=(Magnitud("pie", extremo.cota_pie, "msnm",
                                  extremo.origen_cota_pie,
                                  cifras=CIFRAS_MAGNITUD),),
            resultado=Magnitud("D_f", geometria.D_f, "m",
                               "profundidad de la base de la zapata bajo el "
                               "pie del muro", cifras=CIFRAS_MAGNITUD),
            descripcion_umbral="profundidad minima de cimentacion",
            cita=CITA_PROFUNDIDAD_CIMENTACION,
            aplicacion=f"ANALOGIA [N→] ('{CRITERIO_DESPLANTE_MIN}'): E.050 es "
                       "una norma de edificaciones y el proyecto aplica su "
                       "minimo al cabezal vial porque la misma norma manda "
                       "que el muro de contencion cumpla su Capitulo IV "
                       "(39.13.7). Medida desde la superficie del terreno "
                       "(26.1). Sobre roca el PR puede bajarla: el programa "
                       "no tiene el dato y no lo supone",
            criterio=CRITERIO_DESPLANTE_MIN,
            numeral=_registro_t7a().cita(
                CITA_PROFUNDIDAD_CIMENTACION).como_texto() + ", por analogia")
    v.append(Verificacion(**kv, paso=paso("F9.DESPLANTE", **kp)))
    margen = None
    if extremo.cota_fondo_hoya is not None:
        margen = _margen_socavacion()
        kp, kv = _verificacion_cb(
            codigo="CB5", extremo=ext,
            que="Desplante frente al fondo de la hoya de socavacion",
            formula="cota de desplante <= fondo de la hoya - margen",
            obtenido=geometria.cota_desplante,
            admisible=extremo.cota_fondo_hoya - margen,
            mayor_o_igual=False,
            sustitucion=(
                Magnitud("fondo_hoya", extremo.cota_fondo_hoya, "msnm",
                         "Fase 6: " + extremo.origen_socavacion,
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("margen", margen, "m",
                         f"criterio '{CRITERIO_MARGEN_SOCAVACION}' [C]",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud("cota_desplante", geometria.cota_desplante,
                               "msnm", "base de la zapata del cabezal",
                               cifras=CIFRAS_MAGNITUD),
            descripcion_umbral="fondo de la hoya menos el margen de AASHTO",
            cita="AASHTO_LRFD_9.12.6.5#ZAPATAS",
            aplicacion="EXIGENCIA de AASHTO para las zapatas de las "
                       "estructuras enterradas, leida por el proyecto como "
                       "aplicable a la del cabezal de salida ([C]; la "
                       "lectura y lo que juega en contra, en la "
                       "`Interpretacion` de la cita)",
            criterio=CRITERIO_MARGEN_SOCAVACION,
            citas=("HEC14.5.1.3#CABEZAL",))
        v.append(Verificacion(**kv, paso=paso("F9.DESPLANTE", **kp)))
    # CB6: el espesor de la zapata contra el minimo de su tipo
    minimo_ez, texto_minimo, cita_minimo = peralte_minimo_zapata(geometria.tipo)
    kp, kv = _verificacion_cb(
        codigo="CB6", extremo=ext,
        que=f"Espesor de la zapata frente al minimo del cabezal de "
            f"{geometria.tipo}",
        formula="espesor de la zapata >= minimo del tipo",
        obtenido=geometria.espesor_zapata, admisible=minimo_ez,
        mayor_o_igual=True,
        sustitucion=(Magnitud("minimo", minimo_ez, "m", texto_minimo,
                              cifras=CIFRAS_MAGNITUD),),
        resultado=Magnitud("espesor_zapata", geometria.espesor_zapata, "m",
                           "espesor de la zapata del cabezal",
                           cifras=CIFRAS_MAGNITUD),
        descripcion_umbral=texto_minimo,
        cita=cita_minimo,
        aplicacion=(f"EXIGENCIA de E.060 para las zapatas de concreto simple "
                    "([N], la que la §9.4 de la hoja de ruta hace regir sobre "
                    "el ciclopeo)" if geometria.tipo == TIPO_GRAVEDAD else
                    f"ANALOGIA [N→] ('{CRITERIO_PERALTE_ZAPATA_ARMADA}'): "
                    "E.060 15.7 es de edificaciones y la Via 1 de la §0.2 "
                    "saca a E.060 del diseño armado; se aplica como minimo "
                    "del predimensionamiento, y el peralte de diseño es de "
                    "T-7c"),
        criterio=(CRITERIO_GEOMETRIA if geometria.tipo == TIPO_GRAVEDAD
                  else CRITERIO_PERALTE_ZAPATA_ARMADA),
        citas=((CITA_CICLOPEO_LIMITES,) if geometria.tipo == TIPO_GRAVEDAD
               else ("E060.7.7.1",)))
    v.append(Verificacion(**kv, paso=paso("F9.DIMENSIONES", **kp)))
    # CB7: la base del dentellon contra el terreno y contra la hoya
    if geometria.losa is not None:
        lo = geometria.losa
        dentellon = ca.valor(CRITERIO_DENTELLON)
        prof_min = _exigir_positivo(CRITERIO_DENTELLON,
                                    dentellon.get("profundidad_min_m"),
                                    "profundidad minima del dentellon")
        por_terreno = lo.cota_terreno - prof_min
        sust = [Magnitud("terreno", lo.cota_terreno, "msnm",
                         extremo.origen_cota_pie, cifras=CIFRAS_MAGNITUD),
                Magnitud("profundidad_min", prof_min, "m",
                         f"criterio '{CRITERIO_DENTELLON}' [N→], Lamina Nº 04",
                         cifras=CIFRAS_MAGNITUD)]
        admisible, cita_dent = por_terreno, "MC_HHD.LAMINA_04#DENTELLON"
        descripcion = "terreno del pie menos la profundidad minima"
        citas_extra = ("AASHTO_LRFD_9.12.6.5#DENTELLON",)
        if extremo.cota_fondo_hoya is not None:
            por_hoya = extremo.cota_fondo_hoya - margen
            sust.append(Magnitud("fondo_hoya", extremo.cota_fondo_hoya,
                                 "msnm", "Fase 6: " + extremo.origen_socavacion,
                                 cifras=CIFRAS_MAGNITUD))
            sust.append(Magnitud("margen", margen, "m",
                                 f"criterio '{CRITERIO_MARGEN_SOCAVACION}' [C]",
                                 cifras=CIFRAS_MAGNITUD))
            if por_hoya < por_terreno:
                admisible, cita_dent = por_hoya, "AASHTO_LRFD_9.12.6.5#DENTELLON"
                descripcion = "fondo de la hoya menos el margen"
                citas_extra = ("MC_HHD.LAMINA_04#DENTELLON",
                               "AASHTO_LRFD_9.12.6.5#ZAPATAS")
        kp, kv = _verificacion_cb(
            codigo="CB7", extremo=ext,
            que="Base del dentellon de la losa frente al terreno y a la "
                "socavacion",
            formula=("cota de la base del dentellon <= min(terreno - "
                     "profundidad minima, fondo de la hoya - margen)"),
            obtenido=lo.cota_base_dentellon, admisible=admisible,
            mayor_o_igual=False, sustitucion=tuple(sust),
            resultado=Magnitud("base_dentellon", lo.cota_base_dentellon,
                               "msnm", "base del dentellon de la losa de "
                               "entrega", cifras=CIFRAS_MAGNITUD),
            descripcion_umbral=descripcion, cita=cita_dent,
            aplicacion=(
                "ANALOGIA [N→] con la cota «0.80 min.» del dentellon del "
                "aliviadero de la Lamina Nº 04, medida desde el terreno"
                if cita_dent == "MC_HHD.LAMINA_04#DENTELLON" else
                "EXIGENCIA de AASHTO 12.6.5 («extending below the maximum "
                "anticipated depth of scour») con el margen de 2.0 ft que el "
                "articulo da a las zapatas: lectura del proyecto, [C]"),
            criterio=(CRITERIO_DENTELLON
                      if cita_dent == "MC_HHD.LAMINA_04#DENTELLON"
                      else CRITERIO_MARGEN_SOCAVACION),
            citas=citas_extra)
        v.append(Verificacion(**kv, paso=paso("F9.LOSA", **kp)))
    return tuple(v)


def _registro_t7a():
    """El registro normativo, para leer el texto de una cita (perezoso)."""
    from src.normativa import registro as _registro
    return _registro.construir()


# ---------------------------------------------------------------------------
# La longitud entre cabezales (ficha T6-01)
# ---------------------------------------------------------------------------

def longitud_entre_cabezales(*, longitud, ancho_plataforma: float,
                             cota_relleno_entrada: float,
                             cota_relleno_salida: float
                             ) -> Tuple[Optional[float], str]:
    """
    La longitud del barril entre cabezales, m, MEDIDA ENTRE LAS CARAS
    INTERIORES (trasdos) DE LOS DOS MUROS, con el talud muriendo en el
    RELLENO que cada muro retiene, y la razon cuando no aplica (ficha
    T6-01).

        L_cab = [ancho + talud·(borde_e - rel_e + borde_s - rel_s)] / cos(esviaje)

    con `borde` la cota del borde de la plataforma en cada lado y `rel` la
    cota del relleno retenido por el cabezal de ese extremo: la coronacion
    MENOS EL BORDILLO, que por definicion sobresale del relleno (msnm,
    absolutas). Hasta las correcciones de T-7a (H6) el talud moria en la
    corona del bordillo, lo que acortaba la longitud en talud·bordillo por
    extremo (en A-01, 12.865 m en vez de 13.486 m). Es la formula de
    `M7.longitud_a_la_clave` con el relleno en lugar de la clave: el termino
    talud·S desaparece porque las dos cotas ya son absolutas. La longitud de
    METRADO del barril suma el espesor de los dos muros (`cabezal_del_punto`).

    La coronacion de SALIDA se fijo con la cota de salida de 7.B, que sale de
    la longitud aproximada; con la longitud entre cabezales el muro de salida
    queda mas cerca del eje de la via y la solera bajo el sube S·ΔL, con ΔL
    del orden de 2.5 a 3 m por extremo en el fixture: CENTIMETROS (1.6 cm en
    la salida de A-01 con S = 0.006). Se declara en vez de iterar.

    NO SUSTITUYE a la longitud del diseño (T6-01): la friccion, la caida y
    la cota de salida siguen con la aproximada. Solo con el metodo por
    extremo: con el terraplen simetrico la referencia es el terreno y no el
    conducto, y una longitud declarada no se recalcula.
    """
    if longitud is None:
        return None, ("la longitud del conducto se declaro (`longitud_m`): "
                      "no se recalcula")
    if longitud.metodo is not MetodoLongitud.POR_EXTREMO:
        return None, (f"metodo de longitud '{longitud.metodo.value}': la "
                      "referencia del talud es el terreno, no el cabezal")
    for nombre, x in (("cota_borde_entrada", longitud.cota_borde_entrada),
                      ("cota_borde_salida", longitud.cota_borde_salida),
                      ("talud", longitud.talud),
                      ("factor_esviaje", longitud.factor_esviaje)):
        _exigir_finito(nombre, x, "dato de la longitud por extremo de 7.B")
    proyeccion = longitud.talud * (
        (longitud.cota_borde_entrada - cota_relleno_entrada)
        + (longitud.cota_borde_salida - cota_relleno_salida))
    L = (ancho_plataforma + proyeccion) * longitud.factor_esviaje
    if not L > 0:
        raise LimiteNumericoError(
            "longitud_entre_cabezales", valor=L,
            motivo="el relleno que retienen los cabezales queda sobre el "
            "borde de la plataforma: el talud no llega a ellos y la longitud "
            "entre cabezales no existe (relleno a "
            f"{cota_relleno_entrada:.3f} y {cota_relleno_salida:.3f} msnm)")
    return L, ""


# ---------------------------------------------------------------------------
# Los pasos de memoria del cabezal de un extremo
# ---------------------------------------------------------------------------

# La nota comun de los pasos cuya formula es GEOMETRIA DEL PROYECTO (H9): la
# cita del fundamento sostiene por que se hace el paso, no la formula, y por
# eso `formula_cita_id` va vacio y el indice de formulas lo dice.
NOTA_FORMULA_DEL_PROYECTO = ("La formula es geometria del proyecto: ninguna "
                             "fuente de normas/ la escribe, y por eso el paso "
                             "no le atribuye una cita.")


def _pasos_del_extremo(*, geometria: GeometriaCabezal,
                       extremo: ExtremoDelConducto,
                       embocadura: EmbocaduraDelPunto,
                       talud: float) -> Tuple[PasoDeMemoria, ...]:
    """Los pasos 9.0.x de UN cabezal: coronacion, desplante, aleros, losa."""
    reglas = _reglas()
    ext = extremo.extremo
    e = ext[0]
    origen = {d.nombre: d.origen for d in geometria.dimensiones}
    pasos = [
        paso("F9.CORONACION", codigo=f"9.0.1{e}",
             que=f"Coronacion y altura del cabezal de {ext}",
             formula=("coronacion = max(clave exterior + recubrimiento + "
                      "bordillo, nivel de agua + resguardo);  H_c = "
                      "coronacion - desplante"),
             sustitucion=(
                 Magnitud("clave_exterior", extremo.cota_clave_exterior,
                          "msnm", "solera + altura interior + pared",
                          cifras=CIFRAS_MAGNITUD),
                 Magnitud("recubrimiento + bordillo",
                          reglas["recubrimiento_clave_m"] + reglas["bordillo_m"],
                          "m", f"reglas de '{CRITERIO_GEOMETRIA}' [A]",
                          cifras=CIFRAS_MAGNITUD),
                 Magnitud("nivel_agua", extremo.cota_agua, "msnm",
                          extremo.origen_cota_agua, cifras=CIFRAS_MAGNITUD),
                 Magnitud("resguardo", reglas["resguardo_agua_m"], "m",
                          f"regla de '{CRITERIO_GEOMETRIA}' [A]",
                          cifras=CIFRAS_MAGNITUD),
                 Magnitud("desplante", geometria.cota_desplante, "msnm",
                          "paso del desplante", cifras=CIFRAS_MAGNITUD)),
             resultado=Magnitud(
                 "H_c", geometria.altura_total, "m",
                 "altura total, base de zapata a corona: "
                 + origen.get("altura total del cabezal (H_c, base de "
                              "zapata a corona)", ORIGEN_DIMENSION_REGLA),
                 cifras=CIFRAS_MAGNITUD),
             nota_del_proyecto=(
                 f"Coronacion {geometria.cota_coronacion:.3f} msnm; relleno "
                 f"retenido a {geometria.cota_coronacion - reglas['bordillo_m']:.3f}"
                 " msnm (el bordillo sobresale de el); tipo "
                 f"{geometria.tipo} (gravedad en ciclopeo hasta "
                 f"{reglas['altura_max_gravedad_m']:g} m de altura TOTAL, "
                 "desplante incluido). El muro es normal al eje del "
                 "conducto y de trasdos vertical. Su estabilidad no se "
                 "verifica aqui (T-7b). " + NOTA_FORMULA_DEL_PROYECTO)),
    ]
    df_min = _desplante_minimo()
    sust_d = [Magnitud("pie", extremo.cota_pie, "msnm",
                       extremo.origen_cota_pie, cifras=CIFRAS_MAGNITUD),
              Magnitud("D_f_min", df_min, "m",
                       f"criterio '{CRITERIO_DESPLANTE_MIN}' [N→]: E.050 Art. "
                       "26.2 por analogia", cifras=CIFRAS_MAGNITUD)]
    if extremo.cota_fondo_hoya is not None:
        sust_d.append(Magnitud("fondo_hoya", extremo.cota_fondo_hoya, "msnm",
                               "Fase 6: " + extremo.origen_socavacion,
                               cifras=CIFRAS_MAGNITUD))
        sust_d.append(Magnitud("margen", _margen_socavacion(),
                               "m", f"criterio '{CRITERIO_MARGEN_SOCAVACION}' "
                               "[C]", cifras=CIFRAS_MAGNITUD))
        nota_d = ("La socavacion la entrega la Fase 6 (T-8) y se mide desde "
                  "la referencia de 'referencia_profundidad_socavacion'.")
    elif ext == EXTREMO_SALIDA:
        nota_d = ("SIN SOCAVACION ENTREGADA por la Fase 6 (el motivo va en los "
                  "avisos del punto). El desplante de salida queda con el "
                  "minimo de E.050, que no es el que AASHTO 12.6.5 pide en un "
                  "cauce que socava.")
    else:
        nota_d = ("En la entrada no se estima socavacion (HEC-14 Cap. 5 es "
                  "de la salida): rige el minimo de E.050.")
    pasos.append(paso(
        "F9.DESPLANTE", codigo=f"9.0.2{e}",
        que=f"Profundidad de desplante del cabezal de {ext}",
        formula=(f"D_f = max({df_min:.2f} m, pie - (fondo de la hoya - "
                 "margen));  desplante = pie - D_f"),
        formula_cita_id=CITA_PROFUNDIDAD_CIMENTACION,
        citas_textuales=("AASHTO_LRFD_9.12.6.5#ZAPATAS",),
        sustitucion=tuple(sust_d),
        resultado=Magnitud(
            "D_f", geometria.D_f, "m",
            origen.get("profundidad de desplante (D_f)",
                       ORIGEN_DIMENSION_REGLA)
            + f"; desplante {geometria.cota_desplante:.3f} msnm",
            cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=nota_d))
    if geometria.aleros is not None:
        a = geometria.aleros
        pasos.append(paso(
            "F9.ALEROS", codigo=f"9.0.3{e}",
            que=f"Aleros del cabezal de {ext}",
            formula=("L_corto = (h0 - H_f)·talud / cos(alfa - theta);  "
                     "L_largo = (h0 - H_f)·talud / cos(alfa_largo + theta)"),
            citas_textuales=(CITA_CONVENCION_ALEROS,),
            sustitucion=(
                Magnitud("alfa", a.angulo_grados, "grados",
                         embocadura.regla + f" ('{CRITERIO_ANGULO_ALETAS}' [A]"
                         "), medido con la prolongacion de la pared del "
                         "barril (ΘW del HDS-5)", cifras=CIFRAS_MAGNITUD),
                Magnitud("alfa_largo", a.angulo_largo_grados, "grados",
                         ("declarado en `cabezal_declarado."
                          f"{CAMPO_ANGULO_ALERO_LARGO}` (aleros asimetricos)"
                          if abs(a.angulo_largo_grados - a.angulo_grados)
                          > TOL_UMBRAL_NORMATIVO
                          else "el mismo alfa: ninguno declarado de ese lado"),
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("theta", a.esviaje_grados, "grados",
                         "esviaje del cruce (columna esviaje_grados): el "
                         "angulo del eje con la bajada del talud, que es "
                         "perpendicular a la via", cifras=CIFRAS_MAGNITUD),
                Magnitud("h0", a.altura_inicial, "m",
                         "coronacion - pie: la altura del cabezal en el "
                         "arranque, bordillo incluido", cifras=CIFRAS_MAGNITUD),
                Magnitud("H_f", a.altura_final, "m",
                         origen.get("altura final de los aleros (H_f)",
                                    ORIGEN_DIMENSION_REGLA),
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("talud", talud, "H:V",
                         "talud del terraplen (el de 7.B o "
                         f"'{CRITERIO_TALUD_TERRAPLEN}')",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud(
                "L_corto / L_largo",
                f"{a.longitud_corto:.3f} / {a.longitud_largo:.3f}", "m",
                origen.get("longitud del alero largo (alfa + theta)",
                           ORIGEN_DIMENSION_REGLA)),
            nota_del_proyecto=(
                "El talud baja perpendicular a la via y el cabezal es normal "
                "al eje del conducto: con esviaje, un alero forma alfa - "
                "theta con la bajada del talud y el otro alfa + theta, y no "
                "miden lo mismo. El CSV da la magnitud del esviaje y no su "
                "sentido: cual lado es el largo lo fija la planta del cruce. "
                "El cabezal se supone normal al eje del conducto (lo que "
                "supone la hidraulica del HDS-5); el alero largo se puede "
                "acortar declarando un alfa menor de ese lado en "
                f"`cabezal_declarado` (`{CAMPO_ANGULO_ALERO_LARGO}`): aleros "
                "asimetricos. "
                "h0 y H_f se miden igual (alturas del alero sobre el pie, con "
                "su bordillo), de modo que h0 - H_f es la caida del talud; "
                "medir H_f sobre el talud acortaria los aleros. El encargo "
                "escribia el seno con alfa medido desde el eje, que solo "
                "coincide con esto a 45 grados y sin esviaje (ficha T7A-03). "
                + NOTA_FORMULA_DEL_PROYECTO)))
    if geometria.losa is not None:
        lo = geometria.losa
        pasos.append(paso(
            "F9.LOSA", codigo=f"9.0.4{e}",
            que=f"Losa de entrega y dentellon del cabezal de {ext}",
            formula=("L_losa = fraccion·D;  base del dentellon = min(terreno "
                     "- profundidad minima, fondo de la hoya - margen)"),
            citas_textuales=("MC_HHD.LAMINA_04#DENTELLON",
                             "AASHTO_LRFD_9.12.6.5#DENTELLON"),
            sustitucion=(
                Magnitud("D", extremo.altura_interior, "m",
                         "altura interior de la seccion adoptada",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("terreno", lo.cota_terreno, "msnm",
                         "el pie del muro de este extremo, la misma "
                         "referencia del desplante", cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud(
                "profundidad del dentellon", lo.profundidad_dentellon, "m",
                origen.get("profundidad del dentellon (desde el terreno del "
                           "pie)", ORIGEN_DIMENSION_REGLA)
                + f"; base a {lo.cota_base_dentellon:.3f} msnm; losa "
                f"{lo.longitud:.2f} x {lo.espesor:.2f} m",
                cifras=CIFRAS_MAGNITUD),
            nota_del_proyecto=(
                "Geometria declarada (ficha T8-03): su verificacion "
                "hidraulica es de la Fase 6. La profundidad del dentellon se "
                "mide desde el TERRENO al borde de la losa, como la cota "
                "«0.80 min.» de la Lamina Nº 04 (de un aliviadero, aplicada "
                "por analogia, [N→]), y no desde la cara superior de la "
                "losa. " + NOTA_FORMULA_DEL_PROYECTO)))
    return tuple(pasos)


def _paso_embocadura(embocadura: EmbocaduraDelPunto,
                     es_marco: bool,
                     coherencia: Optional[str] = None) -> PasoDeMemoria:
    if embocadura.angulo_aletas is None:
        res = "cabezal recto, sin aleros"
    else:
        res = (f"aleros a {embocadura.angulo_aletas:g} grados con la pared "
               "del barril")
    if es_marco:
        hds5 = ("En un MARCO la embocadura elige la banda de filas de las "
                "Tablas A.1 y C.2 que 'embocadura_cajon' y 'ke_entrada_cajon' "
                "tienen que respetar; la coherencia se comprueba antes de la "
                "Fase 4" + (f" ({coherencia})." if coherencia else "."))
    else:
        hds5 = ("En un TUBO el angulo de los aleros no mueve ke ni la carta: "
                "la Tabla C.2 pone el tubo con cabezal y con cabezal y aleros "
                "en la misma fila («Headwall or headwall and wingwalls», "
                "0.5) y las Cartas 1 a 3 no separan aleros.")
    return paso(
        "F9.EMBOCADURA", codigo="9.0.0",
        que="Embocadura del punto",
        formula=("alfa = por defecto, salvo esviaje > umbral; tipo = "
                 "'embocadura_cabezal'"),
        sustitucion=(
            Magnitud("tipo", embocadura.tipo, "",
                     f"criterio '{embocadura.criterio_tipo}' [A]"),
            Magnitud("esviaje", embocadura.esviaje_grados, "grados",
                     "columna esviaje_grados del CSV",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("embocadura", res, "", embocadura.regla),
        nota_del_proyecto=hds5)


# ---------------------------------------------------------------------------
# La Fase 9 de UN punto
# ---------------------------------------------------------------------------

def _motivo_sin_socavacion(socavacion, motivo_externo: str) -> str:
    """
    Por que el cabezal de salida no tiene hoya (H9): lo que la Fase 6 dijo,
    y no siempre «falta el lecho». Sin objeto de socavacion, la etapa de la
    Fase 6 se bloqueo (o no corrio) y el motivo lo trae el servicio.
    """
    if socavacion is None:
        return (motivo_externo or
                "la Fase 6 no entrego la socavacion a la salida")
    if socavacion.profundidad_para_desplante is None:
        return (socavacion.motivo_no_estimada or
                "la Fase 6 no estimo la hoya ni hay una declarada")
    return ("la Fase 6 dio la profundidad pero no la cota del fondo de la "
            "hoya (faltan la cota del receptor o la de la solera de salida)")


def cabezal_del_punto(*, punto, resultado, geometria, embocadura,
                      socavacion=None,
                      declarados: Optional[dict] = None,
                      coherencia_embocadura: Optional[str] = None,
                      motivo_sin_socavacion: str = "") -> CabezalDelPunto:
    """
    Los dos cabezales de un punto DIMENSIONADO, con sus aleros, su losa, sus
    verificaciones de compatibilidad (CB1 a CB7), la longitud entre
    cabezales y la de metrado, sus pasos y sus avisos (T-7a, INF-4.1 a
    INF-4.3, INF-5.1.15).

    `declarados` es lo que el punto trae en `cabezal_declarado`, ya
    normalizado por `validar_cabezal_declarado`: {"entrada": {...},
    "salida": {...}}; cada dimension declarada gana sobre su regla.

    Usa el talud de 7.B si la longitud se calculo por extremo y, si no, el
    criterio 'talud_terraplen' -- el mismo que 7.B leeria --: los aleros
    siguen al talud del terraplen sea cual sea el metodo de longitud.

    LOS AVISOS (por `InformePunto.avisos()`): el desplante de salida sin
    socavacion, con SU motivo (`motivo_sin_socavacion` lo trae el servicio
    cuando la etapa de la Fase 6 se bloqueo); el desnivel del talud a lo
    largo de un muro normal al eje cuando hay esviaje, Δz = L_c·sen(theta)/
    talud (H1); y la regla del tipo por altura total, que con altura interior
    >= 0.90 m no alcanza nunca la rama de gravedad (H7).
    """
    declarados = declarados or {}
    entrada, salida = extremos_del_conducto(
        punto=punto, resultado=resultado, geometria=geometria,
        socavacion=socavacion)
    calculada = geometria.longitud_calculada
    talud = (calculada.talud if calculada is not None
             and calculada.talud is not None
             else ca.valor(CRITERIO_TALUD_TERRAPLEN))
    reglas = _reglas()
    geometrias = []
    verificaciones = []
    tipos_por_regla = []
    pasos = [_paso_embocadura(
        embocadura, resultado.material.forma is FormaSeccion.RECTANGULAR,
        coherencia_embocadura)]
    for extremo in (entrada, salida):
        propias = dict(declarados.get(extremo.extremo, {}))
        tipo = propias.pop(CAMPO_TIPO_DECLARADO, None)
        g = predimensionar_cabezal(
            extremo=extremo, embocadura=embocadura, talud=talud,
            declaradas=propias, tipo_declarado=tipo, id_punto=punto.id)
        geometrias.append(g)
        if tipo is None:
            tipos_por_regla.append(g)
        verificaciones.extend(verificar_compatibilidad_cabezal(
            geometria=g, extremo=extremo))
        pasos.extend(_pasos_del_extremo(geometria=g, extremo=extremo,
                                        embocadura=embocadura, talud=talud))
    bordillo = reglas["bordillo_m"]
    L, motivo = longitud_entre_cabezales(
        longitud=calculada, ancho_plataforma=punto.ancho_plataforma,
        cota_relleno_entrada=geometrias[0].cota_coronacion - bordillo,
        cota_relleno_salida=geometrias[1].cota_coronacion - bordillo)
    L_metrado = None
    if L is not None:
        L_metrado = (L + geometrias[0].espesor_base_muro
                     + geometrias[1].espesor_base_muro)
        pasos.append(paso(
            "F9.LONGITUD", codigo="9.0.5",
            que="Longitud entre cabezales y longitud de metrado del barril",
            formula=("L_cab = [ancho + talud·(borde_e - rel_e + borde_s - "
                     "rel_s)] / cos(esviaje), rel = coronacion - bordillo;  "
                     "L_metrado = L_cab + e_e + e_s"),
            sustitucion=(
                Magnitud("rel_e", geometrias[0].cota_coronacion - bordillo,
                         "msnm", "relleno retenido por el cabezal de entrada "
                         "(coronacion de 9.0.1e - bordillo)",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("rel_s", geometrias[1].cota_coronacion - bordillo,
                         "msnm", "relleno retenido por el cabezal de salida "
                         "(coronacion de 9.0.1s - bordillo)",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("e_e + e_s", geometrias[0].espesor_base_muro
                         + geometrias[1].espesor_base_muro, "m",
                         "espesor de los dos muros sobre el eje (normales a "
                         "el)", cifras=CIFRAS_MAGNITUD),
                Magnitud("L", calculada.longitud, "m",
                         "longitud aproximada de 7.B, la del diseño",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud(
                "L_cab / L_metrado", f"{L:.3f} / {L_metrado:.3f}", "m",
                "entre las caras interiores (trasdos) de los dos muros / "
                "barril completo, que atraviesa los dos muros"),
            nota_del_proyecto=(
                "El talud muere en el RELLENO que cada muro retiene "
                "(coronacion menos bordillo), contra su cara interior: L_cab "
                "se mide entre los trasdos. El barril atraviesa ademas los "
                "dos muros, normales al eje, y su longitud de metrado suma "
                f"sus espesores. L_cab es {calculada.longitud - L:.3f} m "
                "menor que la aproximada con que corrio el diseño hidraulico, "
                "que NO se sustituye (ficha T6-01): la friccion, la caida y "
                "la cota de salida siguen con la aproximada. Para que el "
                "control de salida use esta, declarar `longitud_m` por "
                "punto. " + NOTA_FORMULA_DEL_PROYECTO)))
    avisos = []
    if salida.cota_fondo_hoya is None:
        avisos.append(
            f"Cabezal de salida de {punto.id}: desplante sin socavacion "
            "entregada por la Fase 6 ("
            + _motivo_sin_socavacion(socavacion, motivo_sin_socavacion)
            + "); rige solo el minimo de "
            f"{_desplante_minimo():.2f} m de E.050 Art. 26.2 (por "
            "analogia), no el de AASHTO 12.6.5")
    theta = embocadura.esviaje_grados
    if theta > TOL_UMBRAL_NORMATIVO:
        seno = math.sin(math.radians(theta))
        partes = ", ".join(
            f"{g.extremo}: {g.longitud:.2f}·{seno:.3f}/{talud:g} = "
            f"{g.longitud * seno / talud:.3f} m" for g in geometrias)
        avisos.append(
            f"Cabezales de {punto.id}: el muro es NORMAL al eje del conducto "
            f"y el cruce tiene un esviaje de {theta:g} grados, de modo que el "
            "talud (que baja perpendicular a la via) queda a cotas distintas "
            "en los dos extremos de cada muro, Δz = L_c·sen(theta)/talud ("
            + partes + "): la corona horizontal no sigue al talud en toda su "
            f"longitud y, con el relleno al nivel de diseño en el eje, un "
            f"extremo queda Δz/2 por encima (bordillo de {bordillo:.2f} m). "
            "Los dos aleros de cada cabezal miden distinto (paso 9.0.3): el "
            f"largo se acorta declarando un alfa menor de ese lado en "
            f"`cabezal_declarado` (`{CAMPO_ANGULO_ALERO_LARGO}`, aleros "
            "asimetricos). El cabezal normal al eje es el de archivo en las "
            "tres familias; el paralelo a la via, solo para el marco (Carta "
            "11 del HDS-5), esta diferido (ficha T7A-03)")
    asimetricos = [g for g in geometrias if g.aleros is not None
                   and abs(g.aleros.angulo_largo_grados - g.aleros.angulo_grados)
                   > TOL_UMBRAL_NORMATIVO]
    if asimetricos and resultado.material.forma is FormaSeccion.RECTANGULAR:
        avisos.append(
            f"Cabezales de {punto.id}: aleros asimetricos declarados ("
            + ", ".join(f"{g.extremo}: {g.aleros.angulo_grados:g} / "
                        f"{g.aleros.angulo_largo_grados:g} grados"
                        for g in asimetricos)
            + "). Las filas de las Tablas A.1 y C.2 del HDS-5 nombran un solo "
            "angulo de aleros por embocadura: el ke y la carta del marco "
            "siguen siendo los del angulo de la regla, "
            f"{embocadura.angulo_aletas:g} grados")
    # --- correcciones de T-7b (H9) --- ALEROS DESPROPORCIONADOS. La guardia
    # de `predimensionar_aleros` solo cubre la singularidad (alfa + theta >=
    # 90); cerca de ella el alero largo crece sin cota (12 m con theta = 50 y
    # alfa = 30; decenas de metros cerca de 59). Sin umbral nuevo: se compara
    # con una magnitud que ya existe, la longitud entre cabezales. Un alero
    # mas largo que el conducto que encauza no es un alero.
    if L is not None:
        largos = [g for g in geometrias if g.aleros is not None
                  and g.aleros.longitud_largo > L + TOL_UMBRAL_NORMATIVO]
        if largos:
            avisos.append(
                f"Cabezales de {punto.id}: el alero largo "
                + ", ".join(f"del cabezal de {g.extremo} mide "
                            f"{g.aleros.longitud_largo:.2f} m (alfa + theta "
                            f"= {g.aleros.angulo_largo_grados + theta:g} "
                            "grados)" for g in largos)
                + f", MAS que la longitud entre cabezales ({L:.2f} m): con "
                "alfa + theta cerca de 90 grados el alero largo crece sin "
                "cota y queda desproporcionado. Declarar un alfa menor de "
                f"ese lado (`cabezal_declarado.{CAMPO_ANGULO_ALERO_LARGO}`, "
                "aleros asimetricos) o la longitud de los aleros")
    if tipos_por_regla and all(g.tipo == TIPO_VOLADIZO for g in tipos_por_regla):
        avisos.append(
            f"Cabezales de {punto.id}: tipo voladizo armado por la regla de "
            f"'{CRITERIO_GEOMETRIA}' (gravedad en ciclopeo hasta "
            f"{reglas['altura_max_gravedad_m']:g} m), que se mide sobre la "
            "altura TOTAL, desplante incluido (H_c = "
            + " / ".join(f"{g.altura_total:.2f}" for g in tipos_por_regla)
            + " m): con altura interior de 0.90 m o mas ningun cabezal de la "
            "obra alcanza la rama de gravedad con el umbral de archivo "
            "(ficha T7A-04)")
    gravedad = [g for g in geometrias if g.tipo == TIPO_GRAVEDAD]
    if gravedad:
        avisos.append(
            f"Cabezales de {punto.id}: "
            + ", ".join(f"el de {g.extremo}" for g in gravedad)
            + " sale de gravedad en concreto ciclopeo: E.060 22.10.2.1 limita "
            "ese concreto a los muros de contencion de GRAVEDAD y el "
            "22.10.2.2 exige verificar flexion y corte en voladizos mas "
            "largos que la mitad de su peralte (pag. 195); la seccion "
            "propuesta (pantalla, punta y talon) lo juzga T-7c")
    # Las CB incumplidas NO son avisos: son verificaciones, y salen por
    # `InformePunto.incumplidas` (un aviso repetido se cuenta dos veces).
    return CabezalDelPunto(
        id_punto=punto.id, embocadura=embocadura, entrada=geometrias[0],
        salida=geometrias[1], verificaciones=tuple(verificaciones),
        longitud_entre_cabezales=L, longitud_metrado=L_metrado,
        motivo_sin_longitud=motivo, pasos=tuple(pasos), avisos=tuple(avisos))




# ---------------------------------------------------------------------------
# La puerta del dato externo `cabezal_declarado`
# ---------------------------------------------------------------------------

def validar_cabezal_declarado(valor: Any, *,
                              id_punto: Optional[str] = None) -> dict:
    """
    Forma y dominio de `cabezal_declarado` (dato externo opcional, por punto
    o global), y su forma normalizada: {"entrada": {...}, "salida": {...}}.

    Admite las dimensiones de `DIMENSIONES_DECLARABLES` en m (finitas y
    mayores que cero, y no mayores que `dominios.DIMENSION_CABEZAL_MAX_M`),
    el angulo del alero largo (`ANGULOS_DECLARABLES`, en [0, 90) grados) y
    `tipo` (uno de `TIPOS_DE_CABEZAL`), en el nivel superior -- valen para
    los dos extremos -- o dentro de "entrada" / "salida", que ganan sobre el
    nivel superior. Una clave desconocida, un texto, un bool, un cero o un
    negativo se rechazan: un valor por defecto silencioso o una errata
    ignorada son el defecto que esta puerta existe para cerrar.
    """
    from src.dominios import DIMENSION_CABEZAL_MAX_M
    if not isinstance(valor, dict) or not valor:
        raise DatoInvalidoError(
            "cabezal_declarado", valor=valor, id_punto=id_punto,
            motivo="se espera un objeto con dimensiones del cabezal (y "
                   "opcionalmente 'entrada' / 'salida')")
    comunes = {k: v for k, v in valor.items() if k not in EXTREMOS}
    salida_norm = {}

    def _uno(bloque: dict, donde: str) -> dict:
        if not isinstance(bloque, dict):
            raise DatoInvalidoError(
                f"cabezal_declarado.{donde}", valor=bloque, id_punto=id_punto,
                motivo="se espera un objeto de dimensiones")
        limpio = {}
        for k, x in bloque.items():
            if k == CAMPO_TIPO_DECLARADO:
                if x not in TIPOS_DE_CABEZAL:
                    raise DatoInvalidoError(
                        f"cabezal_declarado.{donde}.tipo", valor=x,
                        id_punto=id_punto,
                        motivo="se espera " + " o ".join(TIPOS_DE_CABEZAL))
                limpio[k] = x
                continue
            if k in ANGULOS_DECLARABLES:
                limpio[k] = _exigir_angulo(f"cabezal_declarado.{donde}.{k}",
                                           x, "angulo declarado de los aleros",
                                           id_punto)
                continue
            if k not in DIMENSIONES_DECLARABLES:
                raise DatoInvalidoError(
                    f"cabezal_declarado.{donde}", valor=k, id_punto=id_punto,
                    motivo="no es una dimension declarable del cabezal: "
                           + ", ".join(DIMENSIONES_DECLARABLES
                                       + ANGULOS_DECLARABLES))
            if not (_finito(x) and 0 < x <= DIMENSION_CABEZAL_MAX_M):
                raise DatoInvalidoError(
                    f"cabezal_declarado.{donde}.{k}", valor=x,
                    id_punto=id_punto,
                    motivo="se espera un numero finito, mayor que cero y no "
                           f"mayor que {DIMENSION_CABEZAL_MAX_M:g} m")
            limpio[k] = float(x)
        return limpio

    base = _uno(comunes, "comun") if comunes else {}
    for extremo in EXTREMOS:
        propio = _uno(valor[extremo], extremo) if extremo in valor else {}
        fusion = dict(base)
        fusion.update(propio)
        salida_norm[extremo] = fusion
    if not any(salida_norm.values()):
        raise DatoInvalidoError(
            "cabezal_declarado", valor=valor, id_punto=id_punto,
            motivo="el objeto no declara ninguna dimension")
    return salida_norm


# ===========================================================================
# --- T-7b --- 9.2 y 9.3 EL ENSAMBLE DE ESTABILIDAD, POR CABEZAL Y EN DOS
# MARCOS QUE NO SE CRUZAN
# ===========================================================================
# Cierra INF-4.4, INF-4.5 e INF-5.1.5 y las fichas EXT-7-02 y EXT-7-04 (la
# EXT-7-03 no tenia nada que cerrar y la EXT-7-01 es del armado, de T-7c). Hasta
# aqui M9 era una caja de herramientas: daba los factores de carga del marco
# de estados limite (`factores_de_carga`) junto a verificaciones que comparan
# con los factores de seguridad de E.050 (`verificar_volteo`...), sin decir
# que cargas recibia cada una, y ninguna corrida las ensamblaba. Desde T-7b:
#
#   * el cabezal de CADA EXTREMO de cada punto dimensionado se verifica en
#     DOS MARCOS, cada uno con SUS cargas y SUS resistencias:
#       LRFD  AASHTO LRFD 11.6: cargas FACTORADAS (gamma maximos para el
#             portante; minimos de lo que estabiliza para el deslizamiento y
#             la excentricidad) contra resistencias MINORADAS por phi, y la
#             EXCENTRICIDAD de la resultante en lugar del volteo;
#       ASD   E.050 Art. 21 y 39.13.6, por analogia: cargas de SERVICIO
#             (todos los factores 1) contra la resistencia nominal dividida
#             por su FACTOR DE SEGURIDAD.
#     Cual RIGE lo declara 'marco_estabilidad_cabezal' [A] (decision del
#     dueño: rige LRFD y ASD informa); las verificaciones del marco que no
#     rige salen como INDICADOR y no detienen el punto;
#   * el empuje es el de COULOMB sobre el plano vertical del talon (AASHTO
#     C3.11.5.3), DESCOMPUESTO: la componente horizontal empuja y vuelca, la
#     vertical carga la base (EXT-7-04);
#   * el agua NO se cuenta dos veces: bajo su nivel el suelo empuja con su
#     peso sumergido y el agua aparte (AASHTO 3.11.3); hasta donde sube lo
#     declara 'drenaje_trasdos' (era la desviacion que declaraba
#     `HIPOTESIS_EMPUJE_BAJO_NF`);
#   * los cuatro angulos dejan de detener el caso estatico: phi es del
#     ensayo del relleno, delta sale de phi por una fraccion [C], i de la
#     GEOMETRIA de cada cabezal y beta del muro (punto 5 del encargo);
#   * la demanda sismica se ensambla entera: Mononobe-Okabe dentro de su
#     dominio de validez (AASHTO 11.6.5.3) y la inercia del muro, en los dos
#     casos del 11.6.5.1, con la excentricidad sismica (E6 de antes) como la
#     fila E2 del marco LRFD (EXT-7-02);
#   * E4 y E5 (estabilidad global y del talud) se IMPRIMEN como diferidas al
#     expediente con el EMS: ya no terminan en un AssertionError.
#
# EL MODELO, que es una HIPOTESIS y se dice: el cabezal se calcula como un
# muro de semigravedad en voladizo, por metro de muro, en la seccion llena
# junto al conducto. No se descuenta el vano del conducto ni se cuenta la
# restriccion que el barril y los aleros le dan; no se cuenta empuje pasivo
# delante de la zapata (AASHTO 11.6.3.5) ni el agua del cauce contra la cara
# frontal, que estabiliza: la condicion critica es el cauce vacio.
#
# LA INTERFAZ PARA T-7c: `EstabilidadDelCabezal.cargas` (cada carga sin
# factorar, con su brazo y el elemento al que llega) y `.combinaciones` (los
# factores de cada una), y `solicitaciones_por_elemento`, que entrega el
# cortante y el momento factorados de la pantalla y de la zapata (punta y
# talon) para cada combinacion del marco LRFD.

from src.constantes_normativas import (  # noqa: E402
    C_DESLIZAMIENTO_10_6_3_4, CW_NIVEL_FREATICO_T10_6_3_1_2A_2,
    CW_PROFUNDIDAD_SIN_EFECTO_VECES_B, EXCENTRICIDAD_ESTATICA_FRACCION_B,
    FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1,
    NUMERAL_CAPACIDAD_PORTANTE_AASHTO, NUMERAL_DESLIZAMIENTO_AASHTO,
    NUMERAL_EXCENTRICIDAD_ESTATICA_AASHTO, NUMERAL_PHI_EVENTO_EXTREMO,
    NUMERAL_PHI_MUROS, NUMERAL_PHI_ZAPATAS, PHI_EVENTO_EXTREMO_11_5_8,
    PHI_MUROS_T11_5_7_1, PHI_ZAPATAS_T10_5_5_2_2_1,
    TALUD_QUEBRADO_DISTANCIA_VECES_H)
from src.modelos import (  # noqa: E402
    CARGA_DC, CARGA_EH, CARGA_EQ, CARGA_EV, CARGA_LS, CARGA_WA,
    ELEMENTO_ALEROS, ELEMENTO_PANTALLA, ELEMENTO_ZAPATA, MARCO_ASD,
    MARCO_ENVOLVENTE, MARCO_LRFD, MARCO_RIGE_ASD, MARCO_RIGE_LRFD,
    MOTIVO_METODO_NO_EVALUABLE_CABEZAL, REGLAS_DE_MARCO, CargaDeCabezal,
    CombinacionDeEstabilidad, CriterioPendienteError, DatoFaltanteError,
    EntornoDelCabezal, ErrorProyecto, EstabilidadDelCabezal,
    MetodoNoEvaluableError, SolicitacionDeElemento)

CRITERIO_MARCO = "marco_estabilidad_cabezal"
CRITERIO_FILA_PHI = "fila_phi_estabilidad_cabezal"
CRITERIO_DRENAJE = "drenaje_trasdos"
CRITERIO_GAMMA_SATURADO = "peso_especifico_saturado_relleno_kn_m3"
CRITERIO_FRACCION_DELTA = "fraccion_delta_sobre_phi_trasdos"
CRITERIO_REGLA_PENDIENTE = "regla_pendiente_relleno_trasdos"
CRITERIO_INCLINACION_PORTANTE = "factores_inclinacion_carga_portante"
CRITERIO_TERRENO_DELANTE = "terreno_delante_del_cabezal"
CRITERIO_SUELO_FUNDACION = "c_phi_fundacion"

FILA_PHI_ZAPATAS = "zapatas_seccion_10"
FILA_PHI_MUROS = "muros_tabla_11_5_7"
FILAS_DE_PHI = (FILA_PHI_ZAPATAS, FILA_PHI_MUROS)
DRENAJE_SIN = "sin_drenaje"
DRENAJE_CON = "drenado"
DRENAJES = (DRENAJE_SIN, DRENAJE_CON)
REGLA_CUNA_DE_TANTEO = "cuna_de_tanteo"
REGLA_TALUD_QUEBRADO = "talud_quebrado_2h"
REGLA_TALUD_ENTERO = "talud_del_terraplen"
REGLAS_DE_PENDIENTE = (REGLA_CUNA_DE_TANTEO, REGLA_TALUD_QUEBRADO,
                       REGLA_TALUD_ENTERO)
# Como se calcula el empuje: por la cuña con la superficie real, o por la
# formula cerrada (Coulomb / Mononobe-Okabe) con una pendiente equivalente.
METODO_EMPUJE_CUNA = "cuna de tanteo (Culmann) con la superficie real"
METODO_EMPUJE_FORMULA = "formula cerrada con pendiente equivalente"
# El regimen del cabezal frente al empuje (correcciones de T-7b, H7).
CRITERIO_REGIMEN = "regimen_cabezal"
REGIMEN_CEDENTE = "cedente"
REGIMEN_NO_CEDENTE = "no_cedente"
REGIMENES_DEL_CABEZAL = (REGIMEN_CEDENTE, REGIMEN_NO_CEDENTE)
INCLINACION_APLICAR = "aplicar"
INCLINACION_OMITIR = "omitir"
TERRENO_HORIZONTAL = "horizontal"
TERRENO_TALUD = "talud_descendente"

CONDICIONES_DE_ESTABILIDAD = (CondicionAnalisis.ESTATICO,
                              CondicionAnalisis.SISMICO)
ABREVIATURA_DE_CONDICION = {CondicionAnalisis.ESTATICO: "est",
                            CondicionAnalisis.SISMICO: "sis"}
NUMERAL_9_3_LRFD = "Sec. 9.3, marco LRFD (AASHTO LRFD 11.6.3 y 11.6.5)"
NUMERAL_9_3_ASD = ("Sec. 9.3, marco ASD (E.050 Art. 21 y num. 39.13.6, por "
                   "analogia)")

CAMPOS_SUELO_OBLIGATORIOS = ("cohesivo", "c_kpa", "phi_grados", "gamma_kn_m3")
# (Correcciones de T-7b, H8: `gamma_saturado_kn_m3` se validaba y nadie lo
# consumia -- la capacidad portante bajo el freatico va con los coeficientes
# C_w de la Tabla 10.6.3.1.2a-2 sobre el peso total --; se retiro.)
CAMPOS_SUELO_OPCIONALES = ("q_n_kpa", "q_adm_kpa")
PHI_MAX_TABLA_GRADOS = max(FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1)

# Los codigos de las cargas del ensamble: nombres, no valores.
C_DC_PANTALLA = "DC.pantalla"
C_DC_ZAPATA = "DC.zapata"
C_EV_TALON = "EV.talon"
C_EH_H = "EH.h"
C_EH_V = "EH.v"
C_LS_H = "LS.h"
C_LS_V = "LS.v"
C_WA_H = "WA.h"
C_WA_U = "WA.u"
C_EQ_H = "EQ.dPAE.h"
C_EQ_V = "EQ.dPAE.v"
C_EQ_PIR_MURO = "EQ.PIR.muro"
C_EQ_PIR_SUELO = "EQ.PIR.suelo"
CARGAS_DE_INERCIA = (C_EQ_PIR_MURO, C_EQ_PIR_SUELO)
CARGAS_DE_EMPUJE_ESTATICO = (C_EH_H, C_EH_V)
CARGAS_DE_INCREMENTO = (C_EQ_H, C_EQ_V)


def _no_evaluable(que: str, procedimiento: str, motivo: str,
                  id_punto: Optional[str] = None) -> MetodoNoEvaluableError:
    """El `MetodoNoEvaluableError` del ensamble, con SU rotulo."""
    return MetodoNoEvaluableError(que, procedimiento, motivo,
                                  id_punto=id_punto,
                                  rotulo=MOTIVO_METODO_NO_EVALUABLE_CABEZAL)


# ---------------------------------------------------------------------------
# El suelo de fundacion: la puerta del dato y su lectura
# ---------------------------------------------------------------------------

def validar_suelo_fundacion(valor: Any, *, campo: str = "suelo_fundacion",
                            id_punto: Optional[str] = None) -> dict:
    """
    Forma y dominio de los parametros del suelo de fundacion del cabezal --
    el dato externo `suelo_fundacion` del punto, o el criterio de corredor
    'c_phi_fundacion' --, y su forma normalizada.

    Obligatorios: `cohesivo` (booleano: si el EMS lo trata como cohesivo o
    como friccionante; E.050 Art. 20 obliga a usar solo uno de c y phi),
    `c_kpa` (>= 0), `phi_grados` (0 a 45, que es hasta donde llega la Tabla
    10.6.3.1.2a-1 de AASHTO) y `gamma_kn_m3` (> 0). Opcionales: `q_n_kpa`
    (resistencia portante NOMINAL del EMS; gana en el marco LRFD),
    `q_adm_kpa` (presion ADMISIBLE del EMS; gana en el marco ASD). Una
    clave desconocida -- tambien `gamma_saturado_kn_m3`, que la FASE A
    validaba sin que nadie la leyera --, un texto o un bool donde va un
    numero se rechazan: ninguno tiene valor por defecto.
    """
    if not isinstance(valor, dict):
        raise DatoInvalidoError(
            campo, valor=valor, id_punto=id_punto,
            motivo="se espera un objeto con los parametros del suelo de "
                   "fundacion: " + ", ".join(CAMPOS_SUELO_OBLIGATORIOS))
    desconocidas = [k for k in valor if k not in CAMPOS_SUELO_OBLIGATORIOS
                    + CAMPOS_SUELO_OPCIONALES]
    faltan = [k for k in CAMPOS_SUELO_OBLIGATORIOS if k not in valor]
    if desconocidas or faltan:
        raise DatoInvalidoError(
            campo, valor=sorted(valor), id_punto=id_punto,
            motivo=("campos no reconocidos: " + ", ".join(desconocidas) + ". "
                    if desconocidas else "")
            + ("faltan: " + ", ".join(faltan) + ". " if faltan else "")
            + "Obligatorios: " + ", ".join(CAMPOS_SUELO_OBLIGATORIOS)
            + "; opcionales: " + ", ".join(CAMPOS_SUELO_OPCIONALES))
    if not isinstance(valor["cohesivo"], bool):
        raise DatoInvalidoError(
            f"{campo}.cohesivo", valor=valor["cohesivo"], id_punto=id_punto,
            motivo="se espera true o false: si el EMS trata el suelo de "
                   "fundacion como cohesivo (phi = 0) o como friccionante "
                   "(c = 0), E.050 Art. 20")
    limpio = {"cohesivo": valor["cohesivo"]}
    for k in CAMPOS_SUELO_OBLIGATORIOS[1:] + CAMPOS_SUELO_OPCIONALES:
        if k not in valor:
            continue
        x = valor[k]
        if not _finito(x):
            raise DatoInvalidoError(
                f"{campo}.{k}", valor=x, id_punto=id_punto,
                motivo="se espera un numero finito")
        limpio[k] = float(x)
    if not limpio["c_kpa"] >= 0:
        raise DatoInvalidoError(f"{campo}.c_kpa", valor=limpio["c_kpa"],
                                id_punto=id_punto,
                                motivo="la cohesion no puede ser negativa")
    if not 0 <= limpio["phi_grados"] <= PHI_MAX_TABLA_GRADOS:
        raise DatoInvalidoError(
            f"{campo}.phi_grados", valor=limpio["phi_grados"],
            id_punto=id_punto,
            motivo=f"se espera un angulo entre 0 y {PHI_MAX_TABLA_GRADOS} "
                   "grados, que es el alcance de la Tabla 10.6.3.1.2a-1 de "
                   "AASHTO")
    for k in ("gamma_kn_m3", "q_n_kpa", "q_adm_kpa"):
        if k in limpio and not limpio[k] > 0:
            raise DatoInvalidoError(f"{campo}.{k}", valor=limpio[k],
                                    id_punto=id_punto,
                                    motivo="tiene que ser mayor que cero")
    if limpio["cohesivo"] and not limpio["c_kpa"] > 0:
        raise DatoInvalidoError(
            f"{campo}.c_kpa", valor=limpio["c_kpa"], id_punto=id_punto,
            motivo="un suelo declarado cohesivo necesita su cohesion (E.050 "
                   "Art. 20: phi = 0 y solo cuenta c)")
    if not limpio["cohesivo"] and not limpio["phi_grados"] > 0:
        raise DatoInvalidoError(
            f"{campo}.phi_grados", valor=limpio["phi_grados"],
            id_punto=id_punto,
            motivo="un suelo declarado friccionante necesita su angulo de "
                   "friccion (E.050 Art. 20: c = 0 y solo cuenta phi)")
    return limpio


def suelo_de_fundacion(suelo_del_punto: Optional[dict] = None, *,
                       id_punto: Optional[str] = None) -> Tuple[dict, str]:
    """
    Los parametros del suelo de fundacion del cabezal y de donde salen: los
    del PUNTO (`suelo_fundacion` de `--datos-externos`, ya validados) si
    vienen, y si no los del corredor, el criterio 'c_phi_fundacion', que se
    detiene con `CriterioPendienteError` mientras el EMS no los de.
    """
    if suelo_del_punto is not None:
        return dict(suelo_del_punto), ("dato externo del punto "
                                       "(`suelo_fundacion`), del EMS")
    declarado = ca.valor(CRITERIO_SUELO_FUNDACION)   # CriterioPendienteError
    return (validar_suelo_fundacion(declarado, campo=CRITERIO_SUELO_FUNDACION,
                                    id_punto=id_punto),
            f"criterio de corredor '{CRITERIO_SUELO_FUNDACION}', del EMS")


# ---------------------------------------------------------------------------
# Capacidad portante nominal: AASHTO LRFD 10.6.3.1.2a
# ---------------------------------------------------------------------------

def factores_de_capacidad_de_carga(phi_grados: float
                                   ) -> Tuple[float, float, float]:
    """
    (N_c, N_q, N_gamma) de la Tabla 10.6.3.1.2a-1 de AASHTO LRFD (pag.
    impresa 10-72), para un angulo de friccion entre 0 y 45 grados.

    La tabla da los factores por grado entero. Para un angulo fraccionario
    se interpola linealmente entre las dos filas vecinas: la tabla no lo
    dice y es LECTURA DEL PROYECTO, declarada aqui y en el paso; como los
    tres factores son convexos en phi, la interpolacion lineal queda por
    ENCIMA de la curva en menos del 1 % entre dos grados consecutivos.
    """
    if not (_finito(phi_grados) and 0 <= phi_grados <= PHI_MAX_TABLA_GRADOS):
        raise DatoInvalidoError(
            "phi_grados", valor=phi_grados,
            motivo=f"la Tabla 10.6.3.1.2a-1 de AASHTO va de 0 a "
                   f"{PHI_MAX_TABLA_GRADOS} grados")
    inferior = int(math.floor(phi_grados))
    superior = min(inferior + 1, PHI_MAX_TABLA_GRADOS)
    fraccion = phi_grados - inferior
    a = FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1[inferior]
    b = FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1[superior]
    return tuple(x + (y - x) * fraccion for x, y in zip(a, b))


def coeficientes_de_nivel_freatico(*, D_w: float, D_f: float,
                                   B: float) -> Tuple[float, float]:
    """
    (C_wq, C_wgamma) de la Tabla 10.6.3.1.2a-2 de AASHTO LRFD (pag. impresa
    10-72) para un nivel freatico a la profundidad `D_w` bajo la superficie
    del terreno, con la zapata empotrada `D_f` y de ancho `B`.

    La tabla da tres filas: D_w = 0 -> (0.5, 0.5); D_w = D_f -> (1.0, 0.5);
    D_w > 1.5·B + D_f -> (1.0, 1.0). ENTRE FILAS LA TABLA CALLA: se interpola
    linealmente (C_wq entre la superficie y el desplante; C_wgamma entre el
    desplante y 1.5·B por debajo), que es lectura del proyecto y va del lado
    de la fuente -- «Where the position of groundwater is at a depth less
    than 1.5 times the footing width below the footing base, the bearing
    resistance is affected» --. Un nivel por encima del terreno se lee como
    en la superficie.
    """
    for nombre, x in (("D_w", D_w), ("D_f", D_f), ("B", B)):
        if not _finito(x):
            raise DatoInvalidoError(nombre, valor=x,
                                    motivo="se espera un numero finito")
    if not (B > 0 and D_f >= 0):
        raise DatoInvalidoError("B", valor=(B, D_f),
                                motivo="ancho positivo y empotramiento no "
                                       "negativo")
    sup = CW_NIVEL_FREATICO_T10_6_3_1_2A_2["en_la_superficie"]
    des = CW_NIVEL_FREATICO_T10_6_3_1_2A_2["en_el_desplante"]
    bajo = CW_NIVEL_FREATICO_T10_6_3_1_2A_2["bajo_la_zona_de_falla"]
    D_w = max(D_w, 0.0)
    if D_f > 0 and D_w < D_f:
        c_wq = sup[0] + (des[0] - sup[0]) * D_w / D_f
    else:
        c_wq = des[0]
    zona = CW_PROFUNDIDAD_SIN_EFECTO_VECES_B * B
    if D_w <= D_f:
        c_wg = des[1]
    elif D_w >= D_f + zona:
        c_wg = bajo[1]
    else:
        c_wg = des[1] + (bajo[1] - des[1]) * (D_w - D_f) / zona
    return c_wq, c_wg


def resistencia_portante_nominal(*, suelo: dict, B_efectivo: float,
                                 D_f: float, D_w: float, H_servicio: float,
                                 V_servicio: float,
                                 aplicar_inclinacion: bool
                                 ) -> Tuple[float, dict]:
    """
    q_n, resistencia portante NOMINAL del terreno bajo la zapata corrida del
    cabezal, kPa, con la ecuacion general de AASHTO LRFD 10.6.3.1.2a (ec.
    10.6.3.1.2a-1 a -4, pag. impresa 10-70), y el detalle de sus terminos:

        q_n = c·N_c·i_c + gamma·D_f·N_q·i_q·C_wq
              + 0.5·gamma·B'·N_gamma·i_gamma·C_wgamma

    LO QUE SE TOMA IGUAL A 1, y por que: los factores de FORMA (s_c, s_q,
    s_gamma), porque la zapata del cabezal continua bajo los aleros y se
    trata como corrida (B/L -> 0); y el de PROFUNDIDAD d_q, porque la fuente
    lo admite solo con suelo competente sobre el desplante y lo verifico para
    D_f/B de 1 a 8, que no es el caso de esta zapata.

    `B_efectivo` es B - 2e de la combinacion (10.6.3.1.1 manda usar las
    dimensiones efectivas). `D_f` es el empotramiento que queda DELANTE de la
    zapata -- bajo la hoya de socavacion, si la hay -- y `D_w` la profundidad
    del nivel freatico bajo ese mismo terreno.

    LOS FACTORES DE INCLINACION (ecs. 10.6.3.1.2a-5 a -9) usan las cargas SIN
    FACTORAR, como la fuente las define («H = unfactored horizontal load»),
    con n = 2: zapata corrida cargada en la direccion de su ancho. Con suelo
    friccionante, i_q = (1 - H/V)^n e i_gamma = (1 - H/V)^(n+1); con suelo
    cohesivo (phi = 0), i_c = 1 - n·H/(c·B'·N_c) e i_q = 1. Se aplican o se
    omiten segun 'factores_inclinacion_carga_portante' [A], que es lo que
    decide `aplicar_inclinacion`.

    E.050 Art. 20, que la hoja de ruta hace regir sobre los parametros: con
    suelo cohesivo phi = 0; con friccionante c = 0. No se combinan.
    """
    for nombre, x in (("B_efectivo", B_efectivo), ("D_f", D_f), ("D_w", D_w),
                      ("H_servicio", H_servicio), ("V_servicio", V_servicio)):
        if not _finito(x):
            raise DatoInvalidoError(nombre, valor=x,
                                    motivo="se espera un numero finito")
    if not (B_efectivo > 0 and V_servicio > 0 and D_f >= 0):
        raise DatoInvalidoError(
            "B_efectivo", valor=(B_efectivo, V_servicio, D_f),
            motivo="la resistencia portante necesita ancho efectivo y carga "
                   "vertical positivos, y un empotramiento no negativo")
    c, phi = parametros_resistencia_art20(c=suelo["c_kpa"],
                                          phi_grados=suelo["phi_grados"],
                                          cohesivo=suelo["cohesivo"])
    gamma = suelo["gamma_kn_m3"]
    N_c, N_q, N_g = factores_de_capacidad_de_carga(phi)
    c_wq, c_wg = coeficientes_de_nivel_freatico(D_w=D_w, D_f=D_f,
                                                B=B_efectivo)
    n = 2                       # zapata corrida cargada segun su ancho
    H = abs(H_servicio)
    i_c = i_q = i_g = 1.0
    if aplicar_inclinacion:
        if phi > 0:
            base = max(1.0 - H / V_servicio, 0.0)
            i_q = base ** n
            i_g = base ** (n + 1)
            i_c = i_q - (1.0 - i_q) / (N_q - 1.0)
        else:
            i_c = max(1.0 - n * H / (c * B_efectivo * N_c), 0.0)
    termino_c = c * N_c * i_c
    termino_q = gamma * D_f * N_q * i_q * c_wq
    termino_g = gamma * B_efectivo * N_g * i_g * c_wg / 2
    q_n = termino_c + termino_q + termino_g
    if not (math.isfinite(q_n) and q_n >= 0):
        raise LimiteNumericoError(
            "q_n", valor=q_n,
            motivo="la resistencia portante nominal no es un numero finito "
                   f"y no negativo (B' = {B_efectivo!r} m, H/V = "
                   f"{H!r}/{V_servicio!r})")
    return q_n, {"N_c": N_c, "N_q": N_q, "N_gamma": N_g, "i_c": i_c,
                 "i_q": i_q, "i_gamma": i_g, "C_wq": c_wq, "C_wgamma": c_wg,
                 "c": c, "phi": phi, "gamma": gamma,
                 "termino_c": termino_c, "termino_q": termino_q,
                 "termino_gamma": termino_g}


# ---------------------------------------------------------------------------
# El relleno detras del cabezal: angulos y geometria
# ---------------------------------------------------------------------------

def geometria_del_relleno(entorno: EntornoDelCabezal) -> dict:
    """
    La geometria del relleno detras de UN cabezal, que es de donde salen la
    altura del plano de empuje y la pendiente equivalente (punto 5 del
    encargo de T-7b: «i de la geometria del terraplen»).

    El relleno retenido llega, contra el trasdos, a `cota_relleno`
    (coronacion menos bordillo). Detras SUBE con el talud del terraplen
    (1 V : talud H) hasta el borde de la plataforma, donde se quiebra y
    sigue con la plataforma, que se toma horizontal:

        z_rel   = cota_relleno - cota_desplante       altura retenida
        subida  = max(cota_borde - cota_relleno, 0)   lo que el relleno sube
        h       = z_rel + min(talon / talud, subida)  plano de empuje: hasta
                  el terreno que queda encima del extremo del talon (AASHTO
                  11.6.5.2.2)
        i       = arctan( min(2·z_rel / talud, subida) / (2·z_rel) )
                  pendiente equivalente del relleno quebrado (Figura
                  C3.11.5.8.1-1 de AASHTO, por analogia), o arctan(1/talud)
                  con la regla «talud_del_terraplen»
        subida_sobre_plano = subida - (h - z_rel)
                  lo que el relleno sigue subiendo por encima del tope del
                  plano de empuje hasta la plataforma: la superficie que la
                  cuña de tanteo usa (regla «cuna_de_tanteo», la de archivo;
                  con ella la pendiente equivalente solo alimenta el
                  CONTRASTE de la formula cerrada)

    El plano de empuje es el vertical del extremo del talon (AASHTO
    C3.11.5.3) si la zapata tiene talon, y el propio trasdos si no lo tiene.
    """
    g = entorno.geometria
    for nombre, x in (("cota_relleno", entorno.cota_relleno),
                      ("cota_borde_plataforma", entorno.cota_borde_plataforma),
                      ("cota_desplante", g.cota_desplante)):
        _exigir_finito(nombre, x, f"{nombre} del cabezal de "
                       f"{entorno.extremo}", entorno.id_punto)
    talud = _exigir_positivo(CRITERIO_TALUD_TERRAPLEN, entorno.talud,
                             "talud del terraplen", entorno.id_punto)
    talon = g.exigir_ancho_talon()
    z_rel = entorno.cota_relleno - g.cota_desplante
    if not z_rel > g.espesor_zapata:
        raise DatoInvalidoError(
            "cota_relleno", valor=entorno.cota_relleno,
            id_punto=entorno.id_punto,
            motivo=f"el relleno retenido por el cabezal de {entorno.extremo} "
                   f"({z_rel:.3f} m sobre la base) no queda sobre la zapata "
                   f"({g.espesor_zapata:.3f} m)")
    subida = max(entorno.cota_borde_plataforma - entorno.cota_relleno, 0.0)
    sobre_talon = min(talon / talud, subida)
    h = z_rel + sobre_talon
    regla = ca.valor(CRITERIO_REGLA_PENDIENTE)
    if regla not in REGLAS_DE_PENDIENTE:
        raise DatoInvalidoError(CRITERIO_REGLA_PENDIENTE, valor=regla,
                                motivo="se espera una de: "
                                       + ", ".join(REGLAS_DE_PENDIENTE))
    declarado = ca.valor_si_declarado(CRITERIO_I_RELLENO)
    alcance = TALUD_QUEBRADO_DISTANCIA_VECES_H * z_rel
    if declarado is not None:
        i_grados = float(declarado)
        origen_i = (f"declarado en '{CRITERIO_I_RELLENO}' [A]: gana sobre el "
                    "que saldria de la geometria")
    elif regla in (REGLA_TALUD_QUEBRADO, REGLA_CUNA_DE_TANTEO):
        i_grados = math.degrees(math.atan2(min(alcance / talud, subida),
                                           alcance))
        origen_i = (f"regla '{regla}' ('{CRITERIO_REGLA_PENDIENTE}' [A]): "
                    "recta de la coronacion del relleno retenido al terreno "
                    f"a 2·{z_rel:.3f} = {alcance:.3f} m detras del muro "
                    "(Figura C3.11.5.8.1-1 de AASHTO, por analogia)"
                    + (": con la cuña de tanteo esta pendiente SOLO entra "
                       "en el contraste de la formula cerrada"
                       if regla == REGLA_CUNA_DE_TANTEO else ""))
    else:
        i_grados = (math.degrees(math.atan2(1.0, talud)) if subida > 0
                    else 0.0)
        origen_i = (f"regla '{regla}' ('{CRITERIO_REGLA_PENDIENTE}' [A]): "
                    "el talud del terraplen entero, sin quiebre")
    if not (_finito(i_grados) and i_grados >= 0):
        raise DatoInvalidoError(CRITERIO_I_RELLENO, valor=i_grados,
                                id_punto=entorno.id_punto,
                                motivo="pendiente finita y no negativa")
    # La cuña de relleno sobre el talon por encima de z_rel: triangulo hasta
    # donde el talud alcanza la plataforma, y rectangulo despues.
    x_quiebre = min(subida * talud, talon)
    area_tri = x_quiebre * (x_quiebre / talud) / 2
    area_rec = (talon - x_quiebre) * subida
    return {"z_rel": z_rel, "subida": subida, "h": h, "i_grados": i_grados,
            "origen_i": origen_i, "talon": talon, "talud": talud,
            "regla": regla, "x_quiebre": x_quiebre, "area_tri": area_tri,
            "area_rec": area_rec, "sobre_talon": sobre_talon,
            "subida_sobre_plano": subida - sobre_talon,
            "i_declarado": declarado is not None}


def angulos_del_empuje(entorno: EntornoDelCabezal, relleno: dict) -> dict:
    """
    Los cuatro angulos del empuje de UN cabezal (punto 5 del encargo):

        phi    del ensayo del relleno ('phi_relleno_trasdos'; sin el se
               detiene con `CriterioPendienteError`)
        delta  el declarado en 'friccion_muro_suelo_delta', o la fraccion de
               phi de 'fraccion_delta_sobre_phi_trasdos' [C] (0.67)
        i      de la geometria (`geometria_del_relleno`)
        beta   0 sobre el plano vertical del talon; el del trasdos
               (`GeometriaCabezal.beta_grados`) si la zapata no tiene talon
    """
    phi = _exigir_positivo(CRITERIO_PHI_RELLENO, ca.valor(CRITERIO_PHI_RELLENO),
                           "angulo de friccion del relleno", entorno.id_punto)
    declarado = ca.valor_si_declarado(CRITERIO_DELTA_MURO)
    if declarado is not None:
        delta = float(declarado)
        origen_delta = (f"declarado en '{CRITERIO_DELTA_MURO}' [A]")
    else:
        fraccion = ca.valor(CRITERIO_FRACCION_DELTA)
        if not (_finito(fraccion) and 0 <= fraccion <= 1):
            raise DatoInvalidoError(CRITERIO_FRACCION_DELTA, valor=fraccion,
                                    motivo="fraccion entre 0 y 1")
        delta = fraccion * phi
        origen_delta = (f"{fraccion:g}·phi ('{CRITERIO_FRACCION_DELTA}' [C], "
                        "AASHTO C3.11.5.3)")
    if not (_finito(delta) and 0 <= delta <= phi):
        raise DatoInvalidoError(CRITERIO_DELTA_MURO, valor=delta,
                                id_punto=entorno.id_punto,
                                motivo=f"delta entre 0 y phi = {phi:g} grados")
    con_talon = relleno["talon"] > TOL_UMBRAL_NORMATIVO
    beta = 0.0 if con_talon else float(entorno.geometria.beta_grados)
    return {"phi": float(phi), "delta": delta, "i": relleno["i_grados"],
            "beta": beta, "origen_delta": origen_delta,
            "plano": ("vertical del extremo del talon (AASHTO C3.11.5.3)"
                      if con_talon else "trasdos de la pantalla (sin talon)")}


def _sesgo(K_formula: float, K: float) -> str:
    """Cuanto se aparta la formula cerrada del coeficiente que rige, dicho."""
    diferencia = (K_formula - K) / K
    return (f"la formula da un {abs(diferencia):.1%} "
            + ("MENOS" if diferencia < 0 else "MAS") + " que la cuña")


def _regimen() -> str:
    """
    El regimen del cabezal ('regimen_cabezal' [A]): «cedente» es lo que el
    ensamble calcula; «no_cedente» lo detiene sin cifra, porque las
    presiones de un muro que no cede (K0 en resistencia, k_h = 1.0·k_h0 y
    resultante en h/2 bajo sismo, AASHTO 11.6.5.4 y su comentario) no estan
    implementadas.
    """
    regimen = ca.valor(CRITERIO_REGIMEN)
    if regimen not in REGIMENES_DEL_CABEZAL:
        raise DatoInvalidoError(CRITERIO_REGIMEN, valor=regimen,
                                motivo="se espera una de: "
                                       + ", ".join(REGIMENES_DEL_CABEZAL))
    return regimen


def _regla_de_marco() -> str:
    regla = ca.valor(CRITERIO_MARCO)
    if regla not in REGLAS_DE_MARCO:
        raise DatoInvalidoError(CRITERIO_MARCO, valor=regla,
                                motivo="se espera una de: "
                                       + ", ".join(REGLAS_DE_MARCO))
    return regla


def _decide(marco: str, regla: str) -> bool:
    """Si las verificaciones de ese marco DECIDEN con esa regla."""
    if regla == MARCO_ENVOLVENTE:
        return True
    return (marco == MARCO_LRFD) == (regla == MARCO_RIGE_LRFD)


# ---------------------------------------------------------------------------
# La cuña de tanteo de Coulomb (metodo de Culmann) sobre el plano del talon,
# con la superficie REAL del relleno (correcciones de T-7b, H4)
# ---------------------------------------------------------------------------
# Lo que la fuente pide cuando el relleno no es el de la Figura 3.11.5.3-1
# (talud uniforme): AASHTO 3.11.5.3, «the active pressure may be calculated
# by using a trial procedure based on wedge theory using the Culmann method»
# (cita AASHTO_LRFD_9.3.11.5.3#CULMANN); para el relleno quebrado, «a Coulomb
# trial wedge analysis should be used» (3.11.5.8.1, cita
# AASHTO_LRFD_9.3.11.5.8.1#CUNA, de los muros de suelo reforzado: por
# analogia); y bajo sismo, «the trial wedge method ... may also be used for
# situations when the M-O Method is not suitable» (C11.6.5.3, cita
# AASHTO_LRFD_9.C11.6.5.3#CUNA). La pendiente equivalente «2H» de la Figura
# C3.11.5.8.1-1 queda como alternativa barrible: medida en A-01, SUBESTIMA el
# empuje estatico un 7 a 11 % frente a esta cuña.

def _area_de_la_cuna(*, h: float, subida: float, talud: float,
                     tan_rho: float) -> float:
    """
    Area de la cuña entre el plano vertical (x = 0, de la base z = 0 a su
    tope z = h), el plano de falla z = x·tan(rho) y la superficie del relleno:
    sube desde (0, h) con 1 V : `talud` H y se quiebra, `subida` m mas arriba,
    en una plataforma horizontal (con `subida` infinita, el talud no se
    quiebra nunca). Area del poligono por la formula del cordon de zapato.
    """
    pendiente = 1.0 / talud
    x_quiebre = subida * talud
    if tan_rho > pendiente:
        x_corte = h / (tan_rho - pendiente)
        if x_corte <= x_quiebre:
            return h * x_corte / 2      # triangulo (0,0), (0,h), (x, x·tan)
    if math.isinf(subida):
        return math.inf                 # el plano no alcanza el talud
    tope = h + subida
    x_corte = tope / tan_rho
    vertices = ((0.0, 0.0), (x_corte, tope), (x_quiebre, tope), (0.0, h))
    n = len(vertices)
    doble = sum(vertices[k][0] * vertices[(k + 1) % n][1]
                - vertices[(k + 1) % n][0] * vertices[k][1]
                for k in range(n))
    return abs(doble) / 2


def empuje_de_una_cuna(*, rho_grados: float, h: float, subida: float,
                       talud: float, phi_grados: float, delta_grados: float,
                       gamma: float, k_h: float = 0.0,
                       k_v: float = 0.0) -> float:
    """
    El empuje, kN/m, que UNA cuña de prueba ejerce sobre el plano vertical
    del talon, con el plano de falla a `rho_grados` sobre la horizontal y la
    superficie del relleno de `_area_de_la_cuna`. Equilibrio de la cuña con
    su peso W, la inercia k_h·W hacia el muro y -k_v·W, la reaccion del plano
    vertical inclinada delta sobre su normal y la del plano de falla
    inclinada phi sobre la suya:

        P = W·(1 - k_v)·sen(rho - phi + psi) / [cos(psi)·cos(rho - phi - delta)]
        psi = arctan[k_h / (1 - k_v)]

    Con k_h = k_v = 0 es la cuña de Coulomb; el maximo sobre rho, con la
    superficie de talud uniforme, es la ec. 3.11.5.3-1 de AASHTO, y con el
    relleno horizontal y sismo, Mononobe-Okabe (A11.3.1): los dos dorados
    analiticos de la funcion.
    """
    psi = math.atan2(k_h, 1.0 - k_v)
    rho, phi, delta = (math.radians(rho_grados), math.radians(phi_grados),
                       math.radians(delta_grados))
    area = _area_de_la_cuna(h=h, subida=subida, talud=talud,
                            tan_rho=math.tan(rho))
    W = gamma * area
    return (W * (1.0 - k_v) * math.sin(rho - phi + psi)
            / (math.cos(psi) * math.cos(rho - phi - delta)))


def cuna_de_tanteo(*, h: float, subida: float, talud: float,
                   phi_grados: float, delta_grados: float, gamma: float,
                   k_h: float = 0.0, k_v: float = 0.0,
                   que: str = "empuje del relleno",
                   id_punto: Optional[str] = None,
                   remedio: str = "") -> Tuple[float, float]:
    """
    (P, rho_critico): el MAYOR empuje de las cuñas de prueba sobre el plano
    vertical de altura `h` y el angulo de su plano de falla, en grados
    (metodo de Culmann, AASHTO 3.11.5.3; bajo sismo, la cuña de tanteo de
    C11.6.5.3). Se muestrea el intervalo admisible de rho en
    `TRAMOS_CUNA_DE_TANTEO` tramos y se afina el mejor a `TOL_ANGULO_CUNA`.

    EL INTERVALO: rho entre phi - psi (por debajo la cuña no empuja) y 90
    grados; con el talud sin quiebre, ademas, por encima de su pendiente.

    SE DETIENE, sin cifra (forma MAT-D13):
      * datos fuera de su dominio -> `DatoInvalidoError`;
      * la cuña SIN MAXIMO interior -- el empuje crece hasta el borde del
        intervalo, que es lo que pasa con un talud sin quiebre mas empinado
        que phi - psi: la condicion de 11.6.5.3 en su forma de cuña -- ->
        `MetodoNoEvaluableError` con el rotulo del cabezal;
      * un empuje no finito o no positivo -> `LimiteNumericoError`.
    """
    from scipy.optimize import minimize_scalar   # en el punto de uso (EXT-8)
    for nombre, x in (("h", h), ("talud", talud), ("phi", phi_grados),
                      ("delta", delta_grados), ("gamma", gamma),
                      ("k_h", k_h), ("k_v", k_v)):
        if not _finito(x):
            raise DatoInvalidoError(nombre, valor=x, id_punto=id_punto,
                                    motivo="la cuña de tanteo necesita un "
                                           "numero finito")
    recto = math.degrees(math.pi / 2)       # el angulo recto, en grados
    if not (h > 0 and talud > 0 and gamma > 0 and 0 < phi_grados < recto
            and 0 <= delta_grados <= phi_grados and k_h >= 0
            and 0 <= k_v < 1):
        raise DatoInvalidoError(
            "cuña de tanteo", valor=(h, talud, phi_grados, delta_grados,
                                     k_h, k_v), id_punto=id_punto,
            motivo="altura, talud y peso positivos; 0 < phi < 90; 0 <= delta "
                   "<= phi; k_h >= 0 y 0 <= k_v < 1")
    if not (subida >= 0 and not math.isnan(subida)):
        raise DatoInvalidoError("subida", valor=subida, id_punto=id_punto,
                                motivo="lo que el relleno sube sobre el "
                                       "plano no puede ser negativo")
    psi = math.degrees(math.atan2(k_h, 1.0 - k_v))
    bajo = max(phi_grados - psi, 0.0)
    if math.isinf(subida):
        bajo = max(bajo, math.degrees(math.atan2(1.0, talud)))
    alto = recto

    def P(rho: float) -> float:
        return empuje_de_una_cuna(rho_grados=rho, h=h, subida=subida,
                                  talud=talud, phi_grados=phi_grados,
                                  delta_grados=delta_grados, gamma=gamma,
                                  k_h=k_h, k_v=k_v)

    paso_rho = (alto - bajo) / TRAMOS_CUNA_DE_TANTEO
    malla = [bajo + paso_rho * k for k in range(1, TRAMOS_CUNA_DE_TANTEO)]
    valores = [P(r) for r in malla]
    k_max = max(range(len(malla)), key=lambda k: valores[k])
    if k_max in (0, len(malla) - 1) or not math.isfinite(valores[k_max]):
        raise _no_evaluable(
            que, "metodo de equilibrio limite generalizado (GLE, AASHTO "
            "A11.3.3)",
            "la cuña de tanteo no tiene maximo dentro del intervalo "
            f"admisible ({bajo:.2f} a {alto:.2f} grados): el empuje crece "
            "hasta el borde, como en un talud sin quiebre mas empinado que "
            f"phi - psi = {phi_grados - psi:.2f} grados. La fuente pide otro "
            "metodo; el programa no lo tiene" + (". " + remedio if remedio
                                                 else ""), id_punto)
    fino = minimize_scalar(lambda r: -P(r), method="bounded",
                           bounds=(malla[k_max - 1], malla[k_max + 1]),
                           options={"xatol": math.degrees(TOL_ANGULO_CUNA)})
    rho_c = float(fino.x)
    P_max = P(rho_c)
    if P_max < valores[k_max]:          # el afinado no puede empeorar
        rho_c, P_max = malla[k_max], valores[k_max]
    if not (math.isfinite(P_max) and P_max > 0):
        raise LimiteNumericoError(
            "empuje de la cuña", valor=P_max, id_punto=id_punto,
            motivo=f"la cuña critica de {que} no da un empuje finito y "
                   f"positivo (h = {h!r} m, subida = {subida!r} m)")
    return P_max, rho_c


# ---------------------------------------------------------------------------
# Las cargas del ensamble, sin factorar y con su brazo
# ---------------------------------------------------------------------------

def cargas_del_cabezal(entorno: EntornoDelCabezal,
                       condicion: CondicionAnalisis) -> Tuple[tuple, dict]:
    """
    Las cargas de UN cabezal en UNA condicion, por metro de muro y SIN
    FACTORAR, cada una con su brazo (`CargaDeCabezal`), y el diccionario de
    lo que las produjo (coeficientes, alturas, niveles de agua).

      DC  peso de la pantalla (trapecio de trasdos vertical) y de la zapata.
      EV  peso del relleno sobre el talon, hasta la superficie del relleno.
      EH  empuje activo sobre el plano de empuje, de altura h, con el
          coeficiente de la cuña de tanteo (Culmann) sobre la superficie REAL
          del relleno -- la regla de archivo de
          'regla_pendiente_relleno_trasdos' -- o el de Coulomb con una
          pendiente equivalente (las otras dos reglas), DESCOMPUESTO: P·cos(delta + beta) horizontal y P·sen(delta + beta)
          vertical, aplicada en el plano (EXT-7-04). Bajo el nivel del agua
          el suelo empuja con su peso SUMERGIDO (AASHTO 3.11.3).
      LS  sobrecarga viva: empuje K_A·gamma·h_eq·h a media altura, y su peso
          gamma·h_eq sobre el talon (que solo entra en el portante).
      WA  empuje hidrostatico del agua del relleno sobre el plano de empuje
          y subpresion bajo la zapata, lineal entre el nivel de delante (el
          freatico natural) y el del relleno. Hasta donde sube el agua del
          relleno lo declara 'drenaje_trasdos'.
      EQ  (solo sismica) incremento sismico P_AE - P_A (cuña de tanteo
          pseudoestatica con k_h y k_v, o Mononobe-Okabe), con sus
          dos componentes, aplicado a la fraccion de h de
          'punto_aplicacion_incremento_sismico'; e inercia del muro y del
          relleno sobre el talon, k_h·W, en el centro de gravedad de cada
          uno (AASHTO 11.6.5.1).

    SE DETIENE, sin cifra (`MetodoNoEvaluableError`): bajo sismo con agua
    en el plano de empuje (relleno saturado: AASHTO 11.6.5.3 admite los
    metodos de equilibrio limite con el relleno no saturado, y su comentario
    pide entonces tratar el agua aparte); con la formula cerrada, cuando
    phi < i + arctan[k_h / (1 - k_v)]; y con la cuña, cuando no tiene maximo
    dentro de su intervalo (`cuna_de_tanteo`). La fuente pide entonces otro
    metodo (GLE), que el programa no tiene.
    """
    g = entorno.geometria
    ext = entorno.extremo
    idp = entorno.id_punto
    relleno = geometria_del_relleno(entorno)
    ang = angulos_del_empuje(entorno, relleno)
    gamma = _exigir_positivo(CRITERIO_GAMMA_RELLENO, peso_especifico_relleno(),
                             "peso especifico del relleno", idp)
    gamma_c = _exigir_positivo(CRITERIO_GAMMA_CONCRETO,
                               ca.valor(CRITERIO_GAMMA_CONCRETO),
                               "peso especifico del concreto", idp)
    B, e_z, H = g.B, g.espesor_zapata, g.H
    e_c, e_b = g.espesor_corona, g.espesor_base_muro
    talon = relleno["talon"]
    punta = B - talon - e_b
    if not punta >= -TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            "ancho_talon", valor=talon, id_punto=idp,
            motivo=f"talon ({talon:.3f} m) + pantalla ({e_b:.3f} m) no caben "
                   f"en la zapata (B = {B:.3f} m)")
    punta = max(punta, 0.0)
    x_trasdos = punta + e_b
    z_rel, h = relleno["z_rel"], relleno["h"]
    x_plano = B if talon > TOL_UMBRAL_NORMATIVO else x_trasdos

    # --- agua --------------------------------------------------------------
    # LA COTA DEL AGUA, no una profundidad (correcciones de T-7b, H1): la
    # columna NF_profundidad_m se mide bajo el terreno natural del CRUCE, como
    # en M8, y `datos_del_cabezal_del_punto` la convierte en cota; aqui solo
    # se compara con la base de cada zapata.
    if entorno.cota_freatico is None:
        raise DatoFaltanteError(
            "NF_profundidad_m", id_punto=idp,
            detalle="la estabilidad del cabezal necesita la profundidad del "
                    "nivel freatico bajo el terreno del cruce (columna "
                    "NF_profundidad_m del CSV, del EMS): decide el empuje "
                    "del agua, la subpresion y la capacidad portante. No "
                    "tiene valor por defecto")
    cota_nf = entorno.cota_freatico
    if not _finito(cota_nf):
        raise DatoInvalidoError("NF_profundidad_m", valor=cota_nf,
                                id_punto=idp,
                                motivo="la cota del nivel freatico no es un "
                                       "numero finito")
    D_f = entorno.cota_pie - g.cota_desplante
    h_w_natural = min(max(cota_nf - g.cota_desplante, 0.0), h)
    drenaje = ca.valor(CRITERIO_DRENAJE)
    if drenaje not in DRENAJES:
        raise DatoInvalidoError(CRITERIO_DRENAJE, valor=drenaje,
                                motivo="se espera una de: "
                                       + ", ".join(DRENAJES))
    # SIN DRENAJE el agua llena el relleno RETENIDO, hasta su superficie
    # contra el trasdos (`cota_relleno`, z_rel sobre la base) y no mas arriba:
    # el muro no retiene agua por encima de su relleno (correcciones de T-7b,
    # H6; la FASE A la subia hasta el terreno sobre el extremo del talon, por
    # encima de la coronacion). Con DRENAJE declarado queda en el freatico
    # natural. `HIPOTESIS_EMPUJE_BAJO_NF` lo dice con las mismas palabras.
    if drenaje == DRENAJE_SIN:
        h_w = max(min(z_rel, h), h_w_natural)
    else:
        h_w = h_w_natural
    gamma_sat = None
    if h_w > TOL_UMBRAL_NORMATIVO:
        gamma_sat = ca.valor(CRITERIO_GAMMA_SATURADO)   # CriterioPendienteError
        if not (_finito(gamma_sat) and gamma_sat > GAMMA_AGUA_KN_M3):
            raise DatoInvalidoError(
                CRITERIO_GAMMA_SATURADO, valor=gamma_sat,
                motivo="mayor que el peso especifico del agua")

    # --- empuje activo, con el suelo sumergido bajo el agua -----------------
    # Con la regla de archivo («cuna_de_tanteo») el coeficiente es el
    # EQUIVALENTE de la cuña critica de Culmann sobre la superficie real,
    # K_A = 2·P_cuña / (gamma·h²), y se reparte sobre el plano con el mismo
    # diagrama triangular que Coulomb (resultante a h/3 en seco); la formula
    # cerrada con la pendiente equivalente queda como CONTRASTE. Con una de
    # las otras dos reglas, o con la pendiente declarada, rige la formula.
    K_A_formula = k_a_coulomb(phi_grados=ang["phi"], i_grados=ang["i"],
                              beta_grados=ang["beta"],
                              delta_grados=ang["delta"])
    usa_cuna = (relleno["regla"] == REGLA_CUNA_DE_TANTEO
                and not relleno["i_declarado"])
    rho_A = None
    if usa_cuna:
        if ang["beta"] > TOL_UMBRAL_NORMATIVO:
            raise _no_evaluable(
                f"empuje del cabezal de {ext}",
                "cuña de tanteo sobre un plano inclinado",
                f"el plano de empuje es el trasdos inclinado (beta = "
                f"{ang['beta']:g} grados, zapata sin talon) y la cuña "
                "implementada es la del plano vertical del talon; declarar "
                f"'{CRITERIO_REGLA_PENDIENTE}' = '{REGLA_TALUD_QUEBRADO}' "
                "usa la formula cerrada", idp)
        P_unitario, rho_A = cuna_de_tanteo(
            h=h, subida=relleno["subida_sobre_plano"],
            talud=relleno["talud"], phi_grados=ang["phi"],
            delta_grados=ang["delta"], gamma=1.0,
            que=f"empuje estatico del cabezal de {ext}", id_punto=idp)
        K_A = 2 * P_unitario / h ** 2
        metodo = METODO_EMPUJE_CUNA
    else:
        K_A = K_A_formula
        metodo = METODO_EMPUJE_FORMULA
    inclinacion = math.radians(ang["delta"] + ang["beta"])
    h_seco = h - h_w
    gamma_sum = (gamma_sat - GAMMA_AGUA_KN_M3) if gamma_sat is not None else 0.0
    # Diagrama de presion del suelo: triangulo seco, rectangulo de su
    # continuacion bajo el agua, y triangulo sumergido.
    partes = (
        (K_A * gamma * h_seco ** 2 / 2, h_w + h_seco / 3),      # literal-ok: centroide del triangulo
        (K_A * gamma * h_seco * h_w, h_w / 2),
        (K_A * gamma_sum * h_w ** 2 / 2, h_w / 3),               # literal-ok: centroide del triangulo
    )
    P_A = sum(p for p, _ in partes)
    z_A = (sum(p * z for p, z in partes) / P_A) if P_A > 0 else 0.0

    cargas = []
    # --- DC ----------------------------------------------------------------
    W_rect = gamma_c * e_c * H
    W_tri = gamma_c * (e_b - e_c) * H / 2
    W_pant = W_rect + W_tri
    x_pant = ((W_rect * (x_trasdos - e_c / 2)
               + W_tri * (punta + 2 * (e_b - e_c) / 3))          # literal-ok: centroide del triangulo
              / W_pant) if W_pant > 0 else x_trasdos
    z_pant = ((W_rect * (e_z + H / 2) + W_tri * (e_z + H / 3))   # literal-ok: centroide del triangulo
              / W_pant) if W_pant > 0 else e_z
    W_zap = gamma_c * B * e_z
    cargas.append(CargaDeCabezal(
        C_DC_PANTALLA, CARGA_DC, "peso de la pantalla", V=W_pant, x=x_pant,
        z=z_pant, sobre=ELEMENTO_PANTALLA,
        procedencia=f"gamma_c·(e_corona + e_base)/2·H = {gamma_c:g}·"
                    f"({e_c:.3f} + {e_b:.3f})/2·{H:.3f}"))
    cargas.append(CargaDeCabezal(
        C_DC_ZAPATA, CARGA_DC, "peso de la zapata", V=W_zap, x=B / 2,
        z=e_z / 2, sobre=ELEMENTO_ZAPATA,
        procedencia=f"gamma_c·B·e_zapata = {gamma_c:g}·{B:.3f}·{e_z:.3f}"))
    # --- EV ----------------------------------------------------------------
    alto_talon = z_rel - e_z
    mojado = min(max(h_w - e_z, 0.0), alto_talon)
    area_seca = talon * (alto_talon - mojado)
    area_mojada = talon * mojado
    cuña = relleno["area_tri"] + relleno["area_rec"]
    gamma_cuña = gamma_sat if (gamma_sat is not None and h_w >= h
                               - TOL_UMBRAL_NORMATIVO) else gamma
    W_s = (gamma * area_seca
           + (gamma_sat if gamma_sat is not None else gamma) * area_mojada
           + gamma_cuña * cuña)
    xq = relleno["x_quiebre"]
    momento_cuña = (relleno["area_tri"] * (x_trasdos + 2 * xq / 3)   # literal-ok: centroide del triangulo
                    + relleno["area_rec"] * (x_trasdos + xq + (talon - xq) / 2))
    x_s = ((gamma * area_seca + (gamma_sat or gamma) * area_mojada)
           * (x_trasdos + talon / 2) + gamma_cuña * momento_cuña) / W_s \
        if W_s > 0 else x_trasdos
    z_s = e_z + alto_talon / 2
    if W_s > 0:
        cargas.append(CargaDeCabezal(
            C_EV_TALON, CARGA_EV, "peso del relleno sobre el talon", V=W_s,
            x=x_s, z=z_s, sobre=ELEMENTO_ZAPATA,
            procedencia=f"gamma·talon·(z_rel - e_z) = {gamma:g}·{talon:.3f}·"
                        f"{alto_talon:.3f}, mas la cuña sobre el talon "
                        f"({cuña:.3f} m2)"))
    # --- EH ----------------------------------------------------------------
    cargas.append(CargaDeCabezal(
        C_EH_H, CARGA_EH, "empuje activo, componente horizontal",
        H=P_A * math.cos(inclinacion), z=z_A, sobre=ELEMENTO_PANTALLA,
        procedencia="P_A·cos(delta + beta)"))
    cargas.append(CargaDeCabezal(
        C_EH_V, CARGA_EH, "empuje activo, componente vertical",
        V=P_A * math.sin(inclinacion), x=x_plano, sobre=ELEMENTO_ZAPATA,
        procedencia="P_A·sen(delta + beta), en el plano de empuje"))
    # --- LS ----------------------------------------------------------------
    h_eq = h_eq_sobrecarga_trasdos(altura_muro_total=h)
    cargas.append(CargaDeCabezal(
        C_LS_H, CARGA_LS, "sobrecarga viva, empuje",
        H=K_A * gamma * h_eq * h, z=h / 2, sobre=ELEMENTO_PANTALLA,
        procedencia=f"K_A·gamma·h_eq·h = {K_A:.4f}·{gamma:g}·{h_eq:.4f}·"
                    f"{h:.3f}"))
    if talon > TOL_UMBRAL_NORMATIVO:
        cargas.append(CargaDeCabezal(
            C_LS_V, CARGA_LS, "sobrecarga viva, peso sobre el talon",
            V=gamma * h_eq * talon, x=x_trasdos + talon / 2,
            sobre=ELEMENTO_ZAPATA,
            procedencia=f"gamma·h_eq·talon = {gamma:g}·{h_eq:.4f}·"
                        f"{talon:.3f}"))
    # --- WA ----------------------------------------------------------------
    u_punta = GAMMA_AGUA_KN_M3 * h_w_natural
    u_talon = GAMMA_AGUA_KN_M3 * h_w
    if h_w > TOL_UMBRAL_NORMATIVO:
        cargas.append(CargaDeCabezal(
            C_WA_H, CARGA_WA, "empuje hidrostatico del agua del relleno",
            H=GAMMA_AGUA_KN_M3 * h_w ** 2 / 2,
            z=h_w / 3,                                       # literal-ok: centroide del triangulo
            sobre=ELEMENTO_PANTALLA,
            procedencia=f"gamma_w·h_w^2/2 con h_w = {h_w:.3f} m"))
    if u_punta + u_talon > TOL_UMBRAL_NORMATIVO:
        U = (u_punta + u_talon) / 2 * B
        x_U = B * (u_punta + 2 * u_talon) / (3 * (u_punta + u_talon))   # literal-ok: centroide del trapecio
        cargas.append(CargaDeCabezal(
            C_WA_U, CARGA_WA, "subpresion bajo la zapata", V=-U, x=x_U,
            sobre=ELEMENTO_ZAPATA,
            procedencia=f"gamma_w·(h_delante + h_relleno)/2·B = "
                        f"{GAMMA_AGUA_KN_M3:.2f}·({h_w_natural:.3f} + "
                        f"{h_w:.3f})/2·{B:.3f}"))

    datos = {"relleno": relleno, "angulos": ang, "K_A": K_A, "P_A": P_A,
             "z_A": z_A, "h": h, "h_eq": h_eq, "h_w": h_w,
             "h_w_natural": h_w_natural, "drenaje": drenaje, "gamma": gamma,
             "gamma_saturado": gamma_sat, "gamma_c": gamma_c, "D_f": D_f,
             "cota_freatico": cota_nf, "W_w": W_pant + W_zap, "W_s": W_s, "x_plano": x_plano,
             "x_trasdos": x_trasdos, "punta": punta, "talon": talon,
             "inclinacion": inclinacion, "K_AE": None, "k_h": None,
             "k_v": None, "P_AE": None, "z_AE": None, "fraccion_brazo": None,
             "metodo_empuje": metodo, "K_A_formula": K_A_formula,
             "rho_A": rho_A, "K_AE_formula": None, "rho_AE": None,
             "cota_agua_diseno": entorno.cota_agua_diseno,
             "regimen": _regimen(), "z_rel": z_rel,
             # K0 de AASHTO 3.11.5.2-1, de REFERENCIA para T-7c: la ec. es
             # de muro vertical y terreno horizontal (cita
             # AASHTO_LRFD_9.3.11.5.2#K0).
             "K0": 1.0 - math.sin(math.radians(ang["phi"]))}

    # --- EQ ----------------------------------------------------------------
    if condicion is CondicionAnalisis.SISMICO:
        cadena = cadena_sismica()
        k_h, k_v = cadena.k_h, cadena.k_v
        psi = angulo_inercia_sismica(k_h=k_h, k_v=k_v)
        if h_w > TOL_UMBRAL_NORMATIVO:
            raise _no_evaluable(
                f"empuje sismico del cabezal de {ext}",
                "metodo de equilibrio limite generalizado (GLE, AASHTO "
                "A11.3.3) con el tratamiento del agua del relleno",
                f"hay agua en el plano de empuje (h_w = {h_w:.3f} m, "
                f"'{CRITERIO_DRENAJE}' = '{drenaje}') y AASHTO 11.6.5.3 "
                "admite el metodo de Mononobe-Okabe solo con el relleno no "
                "saturado; su comentario da dos tratamientos segun la "
                "permeabilidad del relleno, y uno exige la presion "
                "hidrodinamica. Declarar el drenaje del trasdos "
                "('drenaje_trasdos' = 'drenado') lo deja evaluable si el "
                "freatico queda bajo la zapata", idp)
        dominio_MO = ang["phi"] >= ang["i"] + psi - TOL_UMBRAL_NORMATIVO
        K_AE_formula = (k_ae_mononobe_okabe(
            phi_grados=ang["phi"], i_grados=ang["i"],
            beta_grados=ang["beta"], delta_grados=ang["delta"], k_h=k_h,
            k_v=k_v) if dominio_MO else None)
        rho_AE = None
        if usa_cuna:
            # La cuña de tanteo bajo sismo (C11.6.5.3): con el relleno que
            # se quiebra en la plataforma tiene maximo aunque Mononobe-Okabe
            # con la pendiente equivalente quede fuera de su dominio; esa
            # formula, si es evaluable, se imprime al lado como contraste.
            P_unitario_E, rho_AE = cuna_de_tanteo(
                h=h, subida=relleno["subida_sobre_plano"],
                talud=relleno["talud"], phi_grados=ang["phi"],
                delta_grados=ang["delta"], gamma=1.0, k_h=k_h, k_v=k_v,
                que=f"empuje sismico del cabezal de {ext}", id_punto=idp,
                remedio=("Lo que lo destraba es una decision del Propietario "
                         "-- admitir el desplazamiento del muro, "
                         f"'{CRITERIO_FACTOR_MURO}', que reduce k_h a la "
                         "mitad (11.6.5.2.2) --, un relleno de mayor "
                         "friccion o un analisis externo"))
            K_AE = 2 * P_unitario_E / (h ** 2 * (1.0 - k_v))
        elif not dominio_MO:
            raise _no_evaluable(
                f"empuje sismico del cabezal de {ext}",
                "metodo de equilibrio limite generalizado (GLE, AASHTO "
                "A11.3.3) o analisis de cuña",
                f"Mononobe-Okabe no es aceptable (AASHTO 11.6.5.3, ec. "
                f"11.6.5.3-1): phi = {ang['phi']:.2f} grados < i + "
                f"arctan[k_h/(1 - k_v)] = {ang['i']:.2f} + {psi:.2f} = "
                f"{ang['i'] + psi:.2f} grados (k_h = {k_h:.3f}). La fuente "
                "pide otro metodo y desaconseja forzar la ecuacion; el "
                "programa no lo tiene. Lo que lo destraba es una decision "
                "del Propietario -- admitir el desplazamiento del muro, "
                "'factor_muro_eleccion', que reduce k_h a la mitad --, un "
                "relleno de mayor friccion, la cuña de tanteo ('"
                f"{CRITERIO_REGLA_PENDIENTE}' = '{REGLA_CUNA_DE_TANTEO}') o "
                "un analisis externo", idp)
        else:
            K_AE = K_AE_formula
        P_AE = empuje_activo_sismico_total(gamma_relleno=gamma, K_AE=K_AE,
                                           H=h, k_v=k_v)
        dP = P_AE - P_A
        fraccion = ca.valor(CRITERIO_BRAZO_SISMICO)
        if not (_finito(fraccion) and 0 < fraccion <= 1):
            raise DatoInvalidoError(CRITERIO_BRAZO_SISMICO, valor=fraccion,
                                    motivo="fraccion de h entre 0 y 1")
        z_dP = fraccion * h
        cargas.append(CargaDeCabezal(
            C_EQ_H, CARGA_EQ, "incremento sismico del empuje, horizontal",
            H=dP * math.cos(inclinacion), z=z_dP, sobre=ELEMENTO_PANTALLA,
            procedencia="(P_AE - P_A)·cos(delta + beta), a "
                        f"{fraccion:g}·h"))
        cargas.append(CargaDeCabezal(
            C_EQ_V, CARGA_EQ, "incremento sismico del empuje, vertical",
            V=dP * math.sin(inclinacion), x=x_plano, sobre=ELEMENTO_ZAPATA,
            procedencia="(P_AE - P_A)·sen(delta + beta)"))
        z_muro = ((W_pant * z_pant + W_zap * e_z / 2)
                  / (W_pant + W_zap))
        cargas.append(CargaDeCabezal(
            C_EQ_PIR_MURO, CARGA_EQ, "inercia del muro", H=k_h * (W_pant + W_zap),
            z=z_muro, sobre=ELEMENTO_PANTALLA,
            procedencia=f"k_h·W_w = {k_h:.3f}·{W_pant + W_zap:.3f}"))
        if W_s > 0:
            cargas.append(CargaDeCabezal(
                C_EQ_PIR_SUELO, CARGA_EQ,
                "inercia del relleno sobre el talon", H=k_h * W_s, z=z_s,
                sobre=ELEMENTO_ZAPATA,
                procedencia=f"k_h·W_s = {k_h:.3f}·{W_s:.3f}"))
        datos.update(K_AE=K_AE, k_h=k_h, k_v=k_v, P_AE=P_AE,
                     z_AE=(P_A * z_A + dP * z_dP) / P_AE,
                     fraccion_brazo=fraccion, psi=psi,
                     K_AE_formula=K_AE_formula, rho_AE=rho_AE)
    return tuple(cargas), datos


# ---------------------------------------------------------------------------
# Las combinaciones de cada marco
# ---------------------------------------------------------------------------

def _combinar(nombre: str, marco: str, condicion: CondicionAnalisis,
              cargas: tuple, factores: dict, B: float,
              para: str) -> CombinacionDeEstabilidad:
    """Aplica `factores` (codigo -> factor) a las cargas y suma."""
    pares = tuple((c.codigo, float(factores.get(c.codigo, 0.0)))
                  for c in cargas)
    f = dict(pares)
    N = sum(f[c.codigo] * c.V for c in cargas)
    H = sum(f[c.codigo] * c.H for c in cargas)
    M_e = sum(f[c.codigo] * c.V * c.x for c in cargas if c.V > 0)
    M_v = (sum(f[c.codigo] * c.H * c.z for c in cargas)
           + sum(f[c.codigo] * -c.V * c.x for c in cargas if c.V < 0))
    for nombre_x, x in (("N", N), ("H", H), ("M_e", M_e), ("M_v", M_v)):
        if not math.isfinite(x):
            raise LimiteNumericoError(
                nombre_x, valor=x,
                motivo=f"la resultante de la combinacion «{nombre}» no es "
                       "finita")
    return CombinacionDeEstabilidad(
        nombre=nombre, marco=marco, condicion=condicion, factores=pares,
        N=N, H=H, M_estabilizante=M_e, M_volcante=M_v, B=B, para=para)


def _casos_sismicos(datos: dict) -> Tuple[Tuple[str, float, float, float], ...]:
    """
    Los dos casos del num. 11.6.5.1 (`P_SEIS_COMBINACIONES`), como factores
    sobre el empuje estatico (EH), el incremento (P_AE - P_A) y la inercia:

        100 % P_AE + 50 % P_IR   ->  EH 1, incremento 1, inercia 0.5
        50 % P_AE + 100 % P_IR   ->  si 0.5·P_AE >= P_A: EH 0.5, incremento
                                     0.5; si no rige el PISO estatico: EH 1,
                                     incremento 0. Inercia 1.
    """
    casos = []
    for nombre, f_ae, f_ir in P_SEIS_COMBINACIONES:
        con_piso = (nombre == P_SEIS_PISO_ESTATICO
                    and f_ae * datos["P_AE"] < datos["P_A"])
        if con_piso:
            casos.append((nombre + " (rige el piso del empuje estatico)",
                          1.0, 0.0, f_ir))
        else:
            casos.append((nombre, f_ae, f_ae, f_ir))
    return tuple(casos)


def combinaciones_de_estabilidad(cargas: tuple, datos: dict,
                                 condicion: CondicionAnalisis, B: float
                                 ) -> Tuple[CombinacionDeEstabilidad, ...]:
    """
    Las combinaciones de UN cabezal en UNA condicion, en los DOS marcos.

    MARCO LRFD (AASHTO 3.4.1 y C11.5.6, Figuras C11.5.6-1, -2 y -4):
      estatica   «Resistencia I, maximos» para el portante: gamma_p maximos
                 de DC y EV, EH maximo, LS 1.75 con su peso sobre el talon;
                 «Resistencia I, minimos» para la excentricidad y el
                 deslizamiento: gamma_p MINIMOS de DC y EV, EH maximo en sus
                 dos componentes, LS 1.75 solo como empuje.
      sismica    «Evento Extremo I», por cada caso del 11.6.5.1: permanentes
                 y sismo con 1.00, LS con gamma_EQ; una variante con el peso
                 de la sobrecarga (portante) y otra sin el.
    WA va siempre con 1.00 (C11.5.6).

    MARCO ASD (E.050 Art. 17.1): TODAS las cargas con factor 1, en las
    mismas variantes (con y sin el peso de la sobrecarga viva).
    """
    codigos = [c.codigo for c in cargas]
    combos = []

    def factores(**por_tipo) -> dict:
        f = {}
        for c in cargas:
            f[c.codigo] = por_tipo.get(c.codigo.replace(".", "_"),
                                       por_tipo.get(c.tipo, 0.0))
        return f

    if condicion is CondicionAnalisis.ESTATICO:
        g = factores_de_carga("Resistencia I")
        combos.append(_combinar(
            "Resistencia I (maximos)", MARCO_LRFD, condicion, cargas,
            factores(DC=g["DC"]["max"], EV=g["EV"]["max"], EH=g["EH"]["max"],
                     LS=g["LS"], WA=g["WA"]["max"]), B, "portante"))
        combos.append(_combinar(
            "Resistencia I (minimos)", MARCO_LRFD, condicion, cargas,
            factores(DC=g["DC"]["min"], EV=g["EV"]["min"], EH=g["EH"]["max"],
                     LS=g["LS"], LS_v=0.0, WA=g["WA"]["max"]), B,
            "excentricidad y deslizamiento"))
        combos.append(_combinar(
            "Servicio (portante)", MARCO_ASD, condicion, cargas,
            factores(DC=1.0, EV=1.0, EH=1.0, LS=1.0, WA=1.0), B, "portante"))
        combos.append(_combinar(
            "Servicio (volteo y deslizamiento)", MARCO_ASD, condicion, cargas,
            factores(DC=1.0, EV=1.0, EH=1.0, LS=1.0, LS_v=0.0, WA=1.0), B,
            "volteo y deslizamiento"))
        return tuple(combos)

    g = factores_de_carga("Evento Extremo I")
    g_eq = gamma_eq()
    if not (_finito(g_eq) and 0 <= g_eq <= 1):
        raise DatoInvalidoError(CRITERIO_GAMMA_EQ, valor=g_eq,
                                motivo="gamma_EQ entre 0 y 1")
    for nombre, f_eh, f_inc, f_ir in _casos_sismicos(datos):
        comunes = dict(DC=g["DC"]["max"], EV=g["EV"]["max"],
                       WA=g["WA"]["max"], EH=f_eh * g["EH"]["max"],
                       EQ_dPAE_h=f_inc, EQ_dPAE_v=f_inc,
                       EQ_PIR_muro=f_ir, EQ_PIR_suelo=f_ir)
        combos.append(_combinar(
            f"Evento Extremo I, {nombre} (portante)", MARCO_LRFD, condicion,
            cargas, factores(LS=g_eq, **comunes), B, "portante"))
        combos.append(_combinar(
            f"Evento Extremo I, {nombre}", MARCO_LRFD, condicion, cargas,
            factores(LS=g_eq, LS_v=0.0, **comunes), B,
            "excentricidad y deslizamiento"))
        servicio = dict(comunes, DC=1.0, EV=1.0, WA=1.0, EH=f_eh)
        combos.append(_combinar(
            f"Servicio con sismo, {nombre} (portante)", MARCO_ASD, condicion,
            cargas, factores(LS=1.0, **servicio), B, "portante"))
        combos.append(_combinar(
            f"Servicio con sismo, {nombre}", MARCO_ASD, condicion, cargas,
            factores(LS=1.0, LS_v=0.0, **servicio), B,
            "volteo y deslizamiento"))
    del codigos
    return tuple(combos)


# ---------------------------------------------------------------------------
# Las verificaciones E1 a E3 de cada marco
# ---------------------------------------------------------------------------

def factores_de_resistencia(condicion: CondicionAnalisis,
                            cohesivo: bool,
                            fila: Optional[str] = None) -> dict:
    """
    Los factores de resistencia phi del marco LRFD para el portante y el
    deslizamiento del cabezal, con la tabla de la que sale cada uno.

    ESTATICA (estado limite de resistencia): la fila que declara
    'fila_phi_estabilidad_cabezal' [A]. «zapatas_seccion_10», Tabla
    10.5.5.2.2-1: portante 0.45 en suelo friccionante (metodo teorico en
    arena con SPT, la menor de las de suelo) o 0.50 en cohesivo; deslizamiento
    0.80 (vaciado in situ sobre arena) u 0.85 (sobre arcilla).
    «muros_tabla_11_5_7», Tabla 11.5.7-1: 0.55 y 1.0.

    SISMICA (Evento Extremo I): sin eleccion. El Art. 11.5.8 fija 1.0 «unless
    otherwise specified» y especifica 0.8 para el portante de los muros de
    gravedad y semigravedad: NO es «phi = 1.0» a secas.
    """
    if condicion is CondicionAnalisis.SISMICO:
        return {"portante": PHI_EVENTO_EXTREMO_11_5_8[
                    "portante_gravedad_y_semigravedad"],
                "deslizamiento": PHI_EVENTO_EXTREMO_11_5_8["general"],
                "fuente": NUMERAL_PHI_EVENTO_EXTREMO, "criterio": None,
                "cita": "AASHTO_LRFD_9.11.5.8#PORTANTE"}
    if fila is None:
        fila = ca.valor(CRITERIO_FILA_PHI)
    if fila not in FILAS_DE_PHI:
        raise DatoInvalidoError(CRITERIO_FILA_PHI, valor=fila,
                                motivo="se espera una de: "
                                       + ", ".join(FILAS_DE_PHI))
    if fila == FILA_PHI_MUROS:
        return {"portante": PHI_MUROS_T11_5_7_1[
                    "portante_gravedad_y_semigravedad"],
                "deslizamiento": PHI_MUROS_T11_5_7_1["deslizamiento"],
                "fuente": NUMERAL_PHI_MUROS, "criterio": CRITERIO_FILA_PHI,
                "cita": "AASHTO_LRFD_9.11.5.7#MUROS"}
    t = PHI_ZAPATAS_T10_5_5_2_2_1
    return {"portante": (t["portante"]["teorico_arcilla"] if cohesivo
                         else t["portante"]["teorico_arena_spt"]),
            "deslizamiento": (t["deslizamiento"]["concreto_sobre_arcilla"]
                              if cohesivo else
                              t["deslizamiento"]["vaciado_in_situ_sobre_arena"]),
            "fuente": NUMERAL_PHI_ZAPATAS, "criterio": CRITERIO_FILA_PHI,
            "cita": "AASHTO_LRFD_9.10.5.5.2.2#T1"}


def _empotramiento_delante(entorno: EntornoDelCabezal, datos: dict
                           ) -> Tuple[float, float, str]:
    """
    (D_f, D_w, texto): el empotramiento que cuenta como sobrecarga DELANTE
    de la zapata y la profundidad del freatico bajo ese terreno. Con hoya de
    socavacion a la salida solo cuenta lo que queda bajo su fondo (AASHTO
    11.6.3.5 y 10.6.1.2); sin ella, la profundidad de desplante.
    """
    desplante = entorno.geometria.cota_desplante
    if entorno.cota_fondo_hoya is not None:
        terreno = min(entorno.cota_fondo_hoya, entorno.cota_pie)
        texto = ("empotramiento bajo el fondo de la hoya de socavacion de la "
                 "Fase 6")
    else:
        terreno = entorno.cota_pie
        texto = "profundidad de desplante bajo el terreno del pie"
    D_f = max(terreno - desplante, 0.0)
    # El freatico es una COTA (H1): su profundidad bajo ESE terreno.
    D_w = max(terreno - datos["cota_freatico"], 0.0)
    return D_f, D_w, texto


def _q_nominal(entorno: EntornoDelCabezal, datos: dict, suelo: dict,
               B_efectivo: float, servicio: CombinacionDeEstabilidad,
               inclinacion: Optional[str] = None
               ) -> Tuple[float, str, dict]:
    """
    La resistencia portante NOMINAL para una combinacion: la del EMS si el
    suelo trae `q_n_kpa` (gana), o la de la ecuacion de AASHTO 10.6.3.1.2a
    con el ancho efectivo. En roca, o con terreno que desciende delante de
    la zapata, la ecuacion no aplica.
    """
    if "q_n_kpa" in suelo:
        return suelo["q_n_kpa"], ("resistencia portante nominal del EMS "
                                  "(`q_n_kpa`): gana sobre la calculada"), {}
    if cimentacion_en_roca():
        raise _no_evaluable(
            f"capacidad portante del cabezal de {entorno.extremo}",
            "resistencia portante en roca (AASHTO 10.6.3.2)",
            "las filas de sitio declaradas en 'F_pga' son de roca y la "
            "ecuacion de capacidad de carga de 10.6.3.1.2a es de suelo; hace "
            "falta la resistencia nominal del EMS (`q_n_kpa`)",
            entorno.id_punto)
    terreno = ca.valor(CRITERIO_TERRENO_DELANTE)
    if terreno == TERRENO_TALUD:
        c_art20, phi_art20 = parametros_resistencia_art20(
            c=suelo["c_kpa"], phi_grados=suelo["phi_grados"],
            cohesivo=suelo["cohesivo"])
        q = capacidad_portante_zapata_en_talud(
            B=B_efectivo, H_s=0.0, gamma=suelo["gamma_kn_m3"],
            c=c_art20, phi_grados=phi_art20)
        return q, ("zapata en talud (Manual de Puentes 2.8.1.3.1.2c), con "
                   f"los factores de '{CRITERIO_MEYERHOF}'"), {}
    if terreno != TERRENO_HORIZONTAL:
        raise DatoInvalidoError(CRITERIO_TERRENO_DELANTE, valor=terreno,
                                motivo=f"se espera '{TERRENO_HORIZONTAL}' o "
                                       f"'{TERRENO_TALUD}'")
    D_f, D_w, texto = _empotramiento_delante(entorno, datos)
    if inclinacion is None:
        inclinacion = ca.valor(CRITERIO_INCLINACION_PORTANTE)
    if inclinacion not in (INCLINACION_APLICAR, INCLINACION_OMITIR):
        raise DatoInvalidoError(CRITERIO_INCLINACION_PORTANTE,
                                valor=inclinacion,
                                motivo="se espera 'aplicar' u 'omitir'")
    q_n, detalle = resistencia_portante_nominal(
        suelo=suelo, B_efectivo=B_efectivo, D_f=D_f, D_w=D_w,
        H_servicio=servicio.H, V_servicio=servicio.N,
        aplicar_inclinacion=inclinacion == INCLINACION_APLICAR)
    detalle.update(D_f=D_f, D_w=D_w, texto_D_f=texto, inclinacion=inclinacion)
    return q_n, ("ecuacion de AASHTO 10.6.3.1.2a con B' = B - 2e, "
                 f"D_f = {D_f:.3f} m ({texto}) y factores de inclinacion "
                 f"'{inclinacion}'"), detalle


def _resistencia_al_deslizamiento(suelo: dict, combo: CombinacionDeEstabilidad
                                  ) -> Tuple[float, str]:
    """
    R_tau, resistencia NOMINAL al deslizamiento por metro de muro, kN/m
    (AASHTO 10.6.3.4; E.050 Art. 20 para la regla de c y phi).

    Suelo friccionante: R_tau = C·V·tan(phi_f), con C = 1.0 de la zapata
    vaciada contra el suelo (ec. 10.6.3.4-2). Suelo cohesivo: la menor de la
    cohesion y la mitad del esfuerzo normal sobre el ancho efectivo, que es
    lo que la fuente admite cuando la zapata descansa sobre al menos 6.0 in
    de material granular compactado -- una condicion constructiva que el
    paso declara --.
    """
    if not suelo["cohesivo"]:
        C = C_DESLIZAMIENTO_10_6_3_4["vaciado_contra_el_suelo"]
        return (C * combo.N * math.tan(math.radians(suelo["phi_grados"])),
                f"C·V·tan(phi_f) = {C:g}·{combo.N:.3f}·tan("
                f"{suelo['phi_grados']:g}°)")
    e = abs(combo.excentricidad)
    B_ef = max(combo.B - 2 * e, 0.0)
    sigma = combo.N / B_ef if B_ef > 0 else 0.0
    q_s = min(suelo["c_kpa"], sigma / 2)
    return (q_s * B_ef,
            f"min(c, sigma_v/2)·B' = min({suelo['c_kpa']:g}, "
            f"{sigma / 2:.3f})·{B_ef:.3f} (sobre >= 6.0 in de material "
            "granular compactado)")


def _combo(combos, marco, para, peor) -> CombinacionDeEstabilidad:
    """La combinacion de ese marco y uso que da el peor efecto `peor(c)`."""
    candidatas = [c for c in combos if c.marco == marco and c.para == para]
    return max(candidatas, key=peor)


def _resultado_de_verificacion(*, fundamento: str, codigo: str, que: str,
                               formula: str, sustitucion: tuple,
                               resultado: Magnitud, descripcion_umbral: str,
                               admisible, unidad: str, cita: str,
                               aplicacion: str, criterio: Optional[str],
                               cumple: bool, margen: Optional[float],
                               decide: bool, numeral: str, obtenido,
                               nota: str, explicacion_falla: str,
                               citas: Tuple[str, ...] = ()) -> Verificacion:
    """
    Arma la `Verificacion` y su paso. Si el marco NO decide ('marco_
    estabilidad_cabezal'), un incumplimiento sale como INDICADOR: se imprime
    y se avisa, y no detiene el punto.
    """
    if cumple:
        tipo, texto = TipoDeVeredicto.CUMPLE, "cumple"
    elif decide:
        tipo, texto = TipoDeVeredicto.NO_CUMPLE, explicacion_falla
    else:
        tipo, texto = TipoDeVeredicto.INDICADOR, (
            explicacion_falla + ". Este marco NO rige "
            f"('{CRITERIO_MARCO}' [A]): se informa y no detiene el punto")
    kw = dict(codigo=codigo, que=que, formula=formula,
              sustitucion=sustitucion, resultado=resultado,
              citas_textuales=(cita,) + tuple(citas),
              umbral=Umbral(descripcion=descripcion_umbral, valor=admisible,
                            unidad=unidad, cita_id=cita,
                            caracter=_caracter_de(cita),
                            aplicacion=aplicacion,
                            criterio_aplicado=criterio),
              veredicto=Veredicto(tipo=tipo, margen=margen, unidad=unidad,
                                  explicacion=texto),
              nota_del_proyecto=nota)
    # El fundamento va LITERAL en cada rama (el indice de formulas localiza
    # al emisor por el literal).
    if fundamento == "F9.E1_LRFD":
        p = paso("F9.E1_LRFD", **kw)
    elif fundamento == "F9.E2_LRFD":
        p = paso("F9.E2_LRFD", **kw)
    elif fundamento == "F9.E3_LRFD":
        p = paso("F9.E3_LRFD", **kw)
    else:
        p = paso("F9.E_ASD", **kw)
    return Verificacion(
        cumple=tipo is not TipoDeVeredicto.NO_CUMPLE, numeral=numeral,
        valor_obtenido=obtenido, valor_admisible=admisible,
        criterio_aplicado=criterio or CRITERIO_MARCO, codigo=codigo, paso=p)


def _m(simbolo: str, valor, unidad: str, procedencia: str) -> Magnitud:
    return Magnitud(simbolo, valor, unidad, procedencia,
                    cifras=CIFRAS_MAGNITUD)


def _verificaciones_lrfd(entorno, datos, suelo, combos, condicion, decide,
                         sufijo, fila: Optional[str] = None,
                         inclinacion: Optional[str] = None
                         ) -> List[Verificacion]:
    """
    E1 a E3 del marco LRFD. `fila` e `inclinacion` sustituyen, SOLO para el
    contraste de sensibilidad del ensamble (`_avisos_de_sensibilidad`), las
    dos elecciones [A] de la ventana que mueven el veredicto: la fila de
    phi y los factores de inclinacion. Sin ellas valen las declaradas.
    """
    g = entorno.geometria
    B = g.B
    ext = entorno.extremo
    phis = factores_de_resistencia(condicion, suelo["cohesivo"], fila=fila)
    en_roca = cimentacion_en_roca()
    nota_marco = ("Marco LRFD (AASHTO LRFD 11.6): cargas factoradas contra "
                  "resistencias minoradas. El cabezal se MODELA como muro de "
                  "semigravedad en voladizo: es hipotesis del proyecto "
                  f"('{CRITERIO_MARCO}' [A]), no mandato de la fuente.")
    salida = []

    # --- E2: excentricidad (reemplaza al volteo) ---------------------------
    c2 = _combo(combos, MARCO_LRFD, "excentricidad y deslizamiento",
                lambda c: (abs(c.excentricidad) if c.N > 0 else math.inf))
    _exigir_compresion(c2, entorno)
    # En valor absoluto: la resultante tiene que quedar dentro de la franja
    # central hacia los DOS lados (con mucho peso sobre el talon cae del
    # lado del relleno, y el limite es el mismo).
    e = abs(c2.excentricidad)
    if condicion is CondicionAnalisis.SISMICO:
        g_eq = gamma_eq()
        e_max = excentricidad_admisible_sismica(B=B, gamma_EQ=g_eq)
        cita_e = "AASHTO_LRFD_9.11.6.5.1#EXC"
        desc_e = (f"limite sismico con gamma_EQ = {g_eq:g}: de los dos "
                  "tercios centrales (gamma_EQ = 0) a las ocho decimas "
                  "(gamma_EQ = 1)")
        criterio_e = CRITERIO_GAMMA_EQ
    else:
        clave = "roca" if en_roca else "suelo"
        e_max = EXCENTRICIDAD_ESTATICA_FRACCION_B[clave] * B
        cita_e = "AASHTO_LRFD_9.11.6.3.3#EXC"
        desc_e = ("resultante dentro de los dos tercios centrales de la "
                  "base, e <= B/3 (fundacion en suelo)" if not en_roca else
                  "resultante dentro de los nueve decimos centrales, e <= "
                  "0.45·B (fundacion en roca)")
        criterio_e = None
    cumple_e = e <= e_max + TOL_UMBRAL_NORMATIVO
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E2_LRFD", codigo=f"E2-LRFD.{sufijo}",
        que=f"E2 (LRFD), excentricidad de la resultante: cabezal de {ext}, "
            f"condicion {condicion.value}",
        formula="e = B/2 - (M_estabilizante - M_volcante) / N  <=  e_max",
        sustitucion=(
            _m("N", c2.N, "kN/m", f"suma vertical factorada, «{c2.nombre}»"),
            _m("M_estabilizante", c2.M_estabilizante, "kN·m/m",
               "momentos factorados que estabilizan, respecto de la punta"),
            _m("M_volcante", c2.M_volcante, "kN·m/m",
               "momentos factorados que vuelcan, respecto de la punta"),
            _m("B", B, "m", "ancho de la zapata")),
        resultado=_m("e", e, "m", "excentricidad respecto del centro de la "
                     "base, en valor absoluto ("
                     + ("hacia la punta" if c2.excentricidad >= 0
                        else "hacia el talon") + ")"),
        descripcion_umbral=desc_e, admisible=e_max, unidad="m", cita=cita_e,
        aplicacion="EXIGENCIA de la fuente para muros, aplicada al cabezal "
                   "por la hipotesis de modelacion",
        criterio=criterio_e, cumple=cumple_e, margen=e_max - e, decide=decide,
        numeral=NUMERAL_9_3_LRFD + f", cabezal de {ext}", obtenido=e,
        nota=nota_marco + " En este marco NO hay factor de seguridad al "
             "volteo: lo reemplaza esta excentricidad (C11.6.3.3).",
        explicacion_falla="la resultante factorada cae fuera del limite: la "
                          "base se despega en exceso; ampliar la zapata o "
                          "el talon",
        citas=("AASHTO_LRFD_9.C11.6.3.3#REEMPLAZA",)))

    # --- E3: deslizamiento ---------------------------------------------------
    c3 = _combo(combos, MARCO_LRFD, "excentricidad y deslizamiento",
                lambda c: c.H - phis["deslizamiento"]
                * _resistencia_al_deslizamiento(suelo, c)[0])
    R_tau, texto_R = _resistencia_al_deslizamiento(suelo, c3)
    R_R = phis["deslizamiento"] * R_tau
    cumple_d = c3.H <= R_R + TOL_UMBRAL_NORMATIVO
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E3_LRFD", codigo=f"E3-LRFD.{sufijo}",
        que=f"E3 (LRFD), deslizamiento: cabezal de {ext}, condicion "
            f"{condicion.value}",
        formula="H_u  <=  phi_tau · R_tau,  R_tau = C·V·tan(phi_f)",
        sustitucion=(
            _m("N", c3.N, "kN/m", f"suma vertical factorada, «{c3.nombre}»"),
            _m("R_tau", R_tau, "kN/m", texto_R),
            _m("phi_tau", phis["deslizamiento"], "-", phis["fuente"])),
        resultado=_m("H_u", c3.H, "kN/m", "suma horizontal factorada de la "
                     "misma combinacion"),
        descripcion_umbral="resistencia factorada al deslizamiento, "
                           "phi_tau·R_tau, sin empuje pasivo",
        admisible=R_R, unidad="kN/m",
        cita="AASHTO_LRFD_9.10.6.3.4#RESISTENCIA",
        aplicacion="EXIGENCIA de la fuente para zapatas y muros, aplicada "
                   "al cabezal por la hipotesis de modelacion",
        criterio=phis["criterio"], cumple=cumple_d, margen=R_R - c3.H,
        decide=decide, numeral=NUMERAL_9_3_LRFD + f", cabezal de {ext}",
        obtenido=c3.H,
        nota=nota_marco + " Empuje pasivo delante de la zapata: no se "
             "cuenta (AASHTO 11.6.3.5).",
        explicacion_falla="el empuje factorado supera la resistencia "
                          "factorada al deslizamiento; ampliar la zapata o "
                          "añadir un dentellon de corte",
        citas=("AASHTO_LRFD_9.11.6.3.6#DESLIZAMIENTO",
               "AASHTO_LRFD_9.11.6.3.5#PASIVA", phis["cita"])))

    # --- E1: capacidad portante ---------------------------------------------
    peor = None
    for c in (x for x in combos if x.marco == MARCO_LRFD):
        _exigir_compresion(c, entorno)
        e1 = abs(c.excentricidad)
        if e1 >= B / 2 - TOL_UMBRAL_NORMATIVO:
            peor = (math.inf, c, None, None, None, "", {})
            break
        servicio = _servicio_de(combos, c)
        presion = presion_contacto_base(N=c.N, momento_neto=c.N * e1, B=B,
                                        cimentacion_en_roca=en_roca)
        q_n, origen_q, det = _q_nominal(entorno, datos, suelo,
                                        presion.ancho_efectivo, servicio,
                                        inclinacion=inclinacion)
        q_R = phis["portante"] * q_n
        uso = presion.q_max / q_R if q_R > 0 else math.inf
        if peor is None or uso > peor[0]:
            peor = (uso, c, presion, q_n, q_R, origen_q, det)
    uso, c1, presion, q_n, q_R, origen_q, det = peor
    if presion is None:
        salida.append(_resultado_de_verificacion(
            fundamento="F9.E1_LRFD", codigo=f"E1-LRFD.{sufijo}",
            que=f"E1 (LRFD), capacidad portante: cabezal de {ext}, "
                f"condicion {condicion.value}",
            formula="sigma_v = N / (B - 2e)  <=  phi_b · q_n",
            sustitucion=(_m("N", c1.N, "kN/m", f"«{c1.nombre}»"),
                         _m("e", c1.excentricidad, "m", "excentricidad")),
            resultado=Magnitud("sigma_v", "no existe", "kPa",
                               "la resultante cae fuera de la zapata (e >= "
                               "B/2): no hay ancho efectivo"),
            descripcion_umbral="resistencia portante factorada",
            admisible=None, unidad="kPa",
            cita="AASHTO_LRFD_9.11.6.3.2#PORTANTE",
            aplicacion="EXIGENCIA de la fuente para muros",
            criterio=phis["criterio"], cumple=False, margen=None,
            decide=decide, numeral=NUMERAL_9_3_LRFD + f", cabezal de {ext}",
            obtenido=None, nota=nota_marco,
            explicacion_falla="la resultante factorada cae fuera de la "
                              "zapata: no hay presion de contacto que "
                              "equilibre el muro"))
        return salida
    cumple_q = presion.q_max <= q_R + TOL_UMBRAL_NORMATIVO
    sust = [_m("N", c1.N, "kN/m", f"suma vertical factorada, «{c1.nombre}»"),
            _m("e", abs(c1.excentricidad), "m", "excentricidad de esa "
               "combinacion"),
            _m("B'", presion.ancho_efectivo, "m", "ancho efectivo B - 2e"),
            _m("q_n", q_n, "kPa", origen_q),
            _m("phi_b", phis["portante"], "-", phis["fuente"])]
    for k in ("N_c", "N_q", "N_gamma", "i_q", "i_gamma", "C_wq", "C_wgamma"):
        if k in det:
            sust.append(_m(k, det[k], "-", "AASHTO 10.6.3.1.2a (Tablas "
                           "10.6.3.1.2a-1 y -2; ecs. -5 a -9)"))
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E1_LRFD", codigo=f"E1-LRFD.{sufijo}",
        que=f"E1 (LRFD), capacidad portante: cabezal de {ext}, condicion "
            f"{condicion.value}",
        formula=("sigma_v = N / (B - 2e)  <=  phi_b · q_n;  q_n = c·N_c·i_c "
                 "+ gamma·D_f·N_q·i_q·C_wq + 0.5·gamma·B'·N_gamma·i_gamma·"
                 "C_wgamma"),
        sustitucion=tuple(sust),
        resultado=_m("sigma_v", presion.q_max, "kPa", presion.distribucion),
        descripcion_umbral="resistencia portante factorada, phi_b·q_n",
        admisible=q_R, unidad="kPa", cita="AASHTO_LRFD_9.11.6.3.2#PORTANTE",
        aplicacion="EXIGENCIA de la fuente para muros, aplicada al cabezal "
                   "por la hipotesis de modelacion",
        criterio=phis["criterio"], cumple=cumple_q,
        margen=q_R - presion.q_max, decide=decide,
        numeral=NUMERAL_9_3_LRFD + f", cabezal de {ext}",
        obtenido=presion.q_max,
        nota=nota_marco + " Zapata tratada como corrida (factores de forma "
             "1) y sin factor de profundidad (d_q = 1). Entre filas de las "
             "Tablas 10.6.3.1.2a-1 y -2 se interpola linealmente (lectura "
             "del proyecto). Se imprime la combinacion de mayor "
             "aprovechamiento entre las del marco.",
        explicacion_falla="la presion factorada supera la resistencia "
                          "portante factorada; ampliar la zapata",
        citas=("AASHTO_LRFD_9.10.6.3.1.2a#QN", phis["cita"])))
    return salida


def _exigir_compresion(c: CombinacionDeEstabilidad,
                       entorno: EntornoDelCabezal) -> None:
    """Con N <= 0 no hay base comprimida: el problema es de flotacion."""
    if not c.N > 0:
        raise DisenoNoFactibleError(
            motivo=f"cabezal de {entorno.extremo} de {entorno.id_punto}: en "
                   f"la combinacion «{c.nombre}» la suma vertical no es de "
                   f"compresion (N = {c.N:.3f} kN/m): la subpresion iguala "
                   "o supera al peso. No es un problema de estabilidad sino "
                   "de flotacion del muro: hace falta mas peso o drenaje")


def _servicio_de(combos, c: CombinacionDeEstabilidad
                 ) -> CombinacionDeEstabilidad:
    """
    La combinacion de SERVICIO (marco ASD) hermana de una LRFD: sus cargas
    sin factorar son las que la fuente pide para los factores de inclinacion
    de la capacidad portante («unfactored»).
    """
    if c.condicion is CondicionAnalisis.ESTATICO:
        return next(x for x in combos if x.marco == MARCO_ASD
                    and x.para == "portante")
    caso = c.nombre.replace("Evento Extremo I, ", "").replace(
        " (portante)", "")
    return next(x for x in combos if x.marco == MARCO_ASD
                and x.para == "portante" and caso in x.nombre)


def _verificaciones_asd(entorno, datos, suelo, combos, condicion, decide,
                        sufijo, inclinacion: Optional[str] = None
                        ) -> List[Verificacion]:
    g = entorno.geometria
    B = g.B
    ext = entorno.extremo
    en_roca = cimentacion_en_roca()
    nota_marco = ("Marco ASD (E.050, norma de edificaciones, aplicada al "
                  "cabezal POR ANALOGIA, [N→]): TODAS las cargas de "
                  "servicio, con factor 1 (Art. 17.1), contra la "
                  "resistencia nominal dividida por el factor de seguridad. "
                  "Ningun factor de carga ni de resistencia del otro marco "
                  "entra aqui.")
    aplic = ("EXIGENCIA de E.050 para edificaciones; el proyecto la aplica "
             "al cabezal por analogia")
    salida = []

    # --- E2: volteo ----------------------------------------------------------
    c2 = _combo(combos, MARCO_ASD, "volteo y deslizamiento",
                lambda c: (c.M_volcante / c.M_estabilizante
                           if c.M_estabilizante > 0 else math.inf))
    fs_v_req = fs_requerido(verificacion="volteo", condicion=condicion)
    fs_v = (c2.M_estabilizante / c2.M_volcante
            if c2.M_volcante > TOL_UMBRAL_NORMATIVO else None)
    cumple_v = fs_v is None or fs_v >= fs_v_req - TOL_UMBRAL_NORMATIVO
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E_ASD", codigo=f"E2-ASD.{sufijo}",
        que=f"E2 (ASD), volteo: cabezal de {ext}, condicion "
            f"{condicion.value}",
        formula="FS = M_estabilizante / M_volcante  >=  FS minimo",
        sustitucion=(
            _m("M_estabilizante", c2.M_estabilizante, "kN·m/m",
               f"momentos de servicio que estabilizan, «{c2.nombre}»"),
            _m("M_volcante", c2.M_volcante, "kN·m/m",
               "momentos de servicio que vuelcan (empujes, inercia y "
               "subpresion)")),
        resultado=(_m("FS", fs_v, "-", "cociente de momentos respecto de "
                      "la punta") if fs_v is not None else
                   Magnitud("FS", "sin momento volcante", "-",
                            "no hay nada que vuelque el muro")),
        descripcion_umbral="factor de seguridad minimo al volteo",
        admisible=fs_v_req, unidad="-", cita="E050.39.13.6",
        aplicacion=aplic, criterio=None, cumple=cumple_v,
        margen=None if fs_v is None else fs_v - fs_v_req, decide=decide,
        numeral=NUMERAL_9_3_ASD + f", cabezal de {ext}", obtenido=fs_v,
        nota=nota_marco,
        explicacion_falla="el factor de seguridad al volteo no alcanza el "
                          "minimo de E.050",
        citas=("E050.17.1#SERVICIO",)))

    # --- E3: deslizamiento ---------------------------------------------------
    def _f_res(c):
        if suelo["cohesivo"]:
            return suelo["c_kpa"] * c.B
        return c.N * math.tan(math.radians(suelo["phi_grados"]))
    c3 = _combo(combos, MARCO_ASD, "volteo y deslizamiento",
                lambda c: (c.H / _f_res(c) if _f_res(c) > 0 else math.inf))
    _exigir_compresion(c3, entorno)
    f_res = _f_res(c3)
    fs_d_req = fs_requerido(verificacion="deslizamiento", condicion=condicion)
    fs_d = f_res / c3.H if c3.H > TOL_UMBRAL_NORMATIVO else None
    cumple_d = fs_d is None or fs_d >= fs_d_req - TOL_UMBRAL_NORMATIVO
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E_ASD", codigo=f"E3-ASD.{sufijo}",
        que=f"E3 (ASD), deslizamiento: cabezal de {ext}, condicion "
            f"{condicion.value}",
        formula=("FS = F_resistente / F_actuante  >=  FS minimo;  "
                 "F_resistente = N·tan(phi) (friccionante) o c·B (cohesivo)"),
        sustitucion=(
            _m("N", c3.N, "kN/m", f"suma vertical de servicio, «{c3.nombre}»"),
            _m("F_resistente", f_res, "kN/m",
               ("c·B, suelo cohesivo con phi = 0" if suelo["cohesivo"] else
                f"N·tan({suelo['phi_grados']:g}°), suelo friccionante con "
                "c = 0") + " (E.050 Art. 20)"),
            _m("F_actuante", c3.H, "kN/m", "suma horizontal de servicio")),
        resultado=(_m("FS", fs_d, "-", "cociente de fuerzas")
                   if fs_d is not None else
                   Magnitud("FS", "sin fuerza actuante", "-", "no hay empuje "
                            "horizontal")),
        descripcion_umbral="factor de seguridad minimo al deslizamiento",
        admisible=fs_d_req, unidad="-", cita="E050.39.13.6", aplicacion=aplic,
        criterio=None, cumple=cumple_d,
        margen=None if fs_d is None else fs_d - fs_d_req, decide=decide,
        numeral=NUMERAL_9_3_ASD + f", cabezal de {ext}", obtenido=fs_d,
        nota=nota_marco + " Sin empuje pasivo delante de la zapata.",
        explicacion_falla="el factor de seguridad al deslizamiento no "
                          "alcanza el minimo de E.050",
        citas=("E050.20", "E050.17.1#SERVICIO")))

    # --- E1: capacidad portante ---------------------------------------------
    fs_q_req = fs_requerido(verificacion="capacidad_portante",
                            condicion=condicion)
    peor = None
    for c in (x for x in combos if x.marco == MARCO_ASD
              and x.para == "portante"):
        _exigir_compresion(c, entorno)
        e1 = abs(c.excentricidad)
        if e1 >= B / 2 - TOL_UMBRAL_NORMATIVO:
            peor = (math.inf, c, None, None, "")
            break
        presion = presion_contacto_base(N=c.N, momento_neto=c.N * e1, B=B,
                                        cimentacion_en_roca=en_roca)
        if "q_adm_kpa" in suelo:
            q_adm, origen = suelo["q_adm_kpa"], (
                "presion admisible del EMS (`q_adm_kpa`): gana, y se usa "
                "sin aumento tambien con sismo")
        else:
            q_n, origen_q, _det = _q_nominal(entorno, datos, suelo,
                                             presion.ancho_efectivo, c,
                                             inclinacion=inclinacion)
            q_adm = q_n / fs_q_req
            origen = f"q_n / FS = {q_n:.3f} / {fs_q_req:g}; q_n: {origen_q}"
        uso = presion.q_max / q_adm if q_adm > 0 else math.inf
        if peor is None or uso > peor[0]:
            peor = (uso, c, presion, q_adm, origen)
    uso, c1, presion, q_adm, origen = peor
    if presion is None:
        salida.append(_resultado_de_verificacion(
            fundamento="F9.E_ASD", codigo=f"E1-ASD.{sufijo}",
            que=f"E1 (ASD), capacidad portante: cabezal de {ext}, "
                f"condicion {condicion.value}",
            formula="q_servicio = N / (B - 2e)  <=  q_admisible",
            sustitucion=(_m("N", c1.N, "kN/m", f"«{c1.nombre}»"),
                         _m("e", c1.excentricidad, "m", "excentricidad")),
            resultado=Magnitud("q_servicio", "no existe", "kPa",
                               "la resultante de servicio cae fuera de la "
                               "zapata (e >= B/2)"),
            descripcion_umbral="presion admisible",
            admisible=None, unidad="kPa", cita="E050.21", aplicacion=aplic,
            criterio=None, cumple=False, margen=None, decide=decide,
            numeral=NUMERAL_9_3_ASD + f", cabezal de {ext}", obtenido=None,
            nota=nota_marco,
            explicacion_falla="la resultante de servicio cae fuera de la "
                              "zapata"))
        return salida
    cumple_q = presion.q_max <= q_adm + TOL_UMBRAL_NORMATIVO
    salida.append(_resultado_de_verificacion(
        fundamento="F9.E_ASD", codigo=f"E1-ASD.{sufijo}",
        que=f"E1 (ASD), capacidad portante: cabezal de {ext}, condicion "
            f"{condicion.value}",
        formula="q_servicio = N / (B - 2e)  <=  q_admisible = q_n / FS",
        sustitucion=(
            _m("N", c1.N, "kN/m", f"suma vertical de servicio, «{c1.nombre}»"),
            _m("e", abs(c1.excentricidad), "m", "excentricidad de servicio"),
            _m("B'", presion.ancho_efectivo, "m", "ancho efectivo B - 2e"),
            _m("FS", fs_q_req, "-", "E.050 Art. 21 ("
               + ("21.1, cargas estaticas"
                  if condicion is CondicionAnalisis.ESTATICO
                  else "21.2, solicitacion maxima de sismo") + ")")),
        resultado=_m("q_servicio", presion.q_max, "kPa", presion.distribucion),
        descripcion_umbral="presion admisible del terreno (" + origen + ")",
        admisible=q_adm, unidad="kPa", cita="E050.21", aplicacion=aplic,
        criterio=None, cumple=cumple_q, margen=q_adm - presion.q_max,
        decide=decide, numeral=NUMERAL_9_3_ASD + f", cabezal de {ext}",
        obtenido=presion.q_max,
        nota=nota_marco + " La excentricidad de servicio se usa solo para "
             "el ancho efectivo: su limite de B/6 no es exigencia de E.050 "
             "y B/3 es del otro marco.",
        explicacion_falla="la presion de servicio supera la admisible",
        citas=("E050.17.1#SERVICIO",)))
    return salida


# ---------------------------------------------------------------------------
# Las solicitaciones factoradas por elemento: la interfaz para T-7c
# ---------------------------------------------------------------------------

def solicitaciones_por_elemento(entorno: EntornoDelCabezal, cargas: tuple,
                                combos: Tuple[CombinacionDeEstabilidad, ...],
                                datos: dict
                                ) -> Tuple[SolicitacionDeElemento, ...]:
    """
    El cortante y el momento FACTORADOS de cada elemento del cabezal en su
    seccion critica, por metro de muro, para cada combinacion del marco LRFD
    (lo que T-7c necesita para armar; este prompt no arma nada).

      pantalla  en su arranque (cara superior de la zapata): las cargas
                horizontales que le llegan (`CargaDeCabezal.sobre` =
                pantalla), tomadas de la altura sobre la zapata. Aproximacion
                DECLARADA y del lado seguro: se toma la resultante entera de
                cada empuje, que incluye el tramo del canto de la zapata, con
                su brazo medido desde el arranque (z - e_zapata, no menor
                que cero).
      zapata    punta: la presion de contacto uniforme sobre el ancho
                efectivo (que arranca en la punta) menos el peso propio, en
                la cara delantera de la pantalla. Talon: el relleno, la
                sobrecarga, la componente vertical del empuje y el peso
                propio, menos la presion de contacto que alcance al talon y
                la subpresion, en la cara trasera de la pantalla.
      aleros    la misma seccion de la pantalla en su arranque, que es la
                altura inicial del alero; a lo largo del alero la altura
                baja y T-7c reutiliza este ensamble con la geometria de cada
                seccion.

    CON QUE EMPUJE SALEN (correcciones de T-7b, H7): toda solicitacion lleva
    el regimen del cabezal ('regimen_cabezal' [A], «cedente» de archivo),
    el coeficiente con que se calcularon sus empujes ('K_A' en la estatica,
    'K_AE' en la sismica, con su valor) y el K0 de AASHTO 3.11.5.2 con el
    cociente K0/K_A: si T-7c juzga que la pantalla no cede, la fuente pide
    para la resistencia el empuje en reposo (C11.6.5.4), y sus empujes
    crecerian en ese factor. Este prompt no lo aplica: lo marca.
    """
    g = entorno.geometria
    e_z = g.espesor_zapata
    punta, talon = datos["punta"], datos["talon"]
    x_trasdos = datos["x_trasdos"]
    por_codigo = {c.codigo: c for c in cargas}
    salida = []
    sismica = datos["K_AE"] is not None
    marca = dict(regimen=datos["regimen"],
                 coeficiente_de_empuje="K_AE" if sismica else "K_A",
                 K_empuje=datos["K_AE"] if sismica else datos["K_A"],
                 K0=datos["K0"], K0_sobre_K_A=datos["K0"] / datos["K_A"])
    for combo in (c for c in combos if c.marco == MARCO_LRFD):
        f = dict(combo.factores)
        V_p = sum(f[c.codigo] * c.H for c in cargas
                  if c.sobre == ELEMENTO_PANTALLA)
        M_p = sum(f[c.codigo] * c.H * max(c.z - e_z, 0.0) for c in cargas
                  if c.sobre == ELEMENTO_PANTALLA)
        salida.append(SolicitacionDeElemento(**marca, 
            elemento=ELEMENTO_PANTALLA, seccion="arranque de la pantalla",
            combinacion=combo.nombre, V_u=V_p, M_u=M_p,
            nota="resultante entera de cada empuje; brazo desde el arranque"))
        salida.append(SolicitacionDeElemento(**marca, 
            elemento=ELEMENTO_ALEROS,
            seccion="arranque del alero (altura inicial, la del cabezal)",
            combinacion=combo.nombre, V_u=V_p, M_u=M_p,
            nota="la de la pantalla en su arranque: el alero empieza a la "
                 "altura del cabezal y baja con el talud"))
        if not combo.N > 0:
            continue
        e = abs(combo.excentricidad)
        B_ef = combo.B - 2 * e
        if not B_ef > 0:
            continue
        sigma = combo.N / B_ef
        f_dc = f.get(C_DC_ZAPATA, 0.0)
        w_zap = f_dc * datos["gamma_c"] * e_z
        a = min(punta, B_ef)
        salida.append(SolicitacionDeElemento(**marca, 
            elemento=ELEMENTO_ZAPATA, seccion="punta, cara de la pantalla",
            combinacion=combo.nombre,
            V_u=sigma * a - w_zap * punta,
            M_u=sigma * a * (punta - a / 2) - w_zap * punta ** 2 / 2,
            nota="presion uniforme sobre B - 2e desde la punta, menos el "
                 "peso propio; positivo = tracciona la cara inferior"))
        sobre_talon = max(B_ef - x_trasdos, 0.0)
        abajo = sum(f.get(k, 0.0) * por_codigo[k].V
                    for k in (C_EV_TALON, C_LS_V, C_EH_V, C_EQ_V)
                    if k in por_codigo)
        m_abajo = sum(f.get(k, 0.0) * por_codigo[k].V
                      * (por_codigo[k].x - x_trasdos)
                      for k in (C_EV_TALON, C_LS_V, C_EH_V, C_EQ_V)
                      if k in por_codigo)
        u = por_codigo.get(C_WA_U)
        sub = -f.get(C_WA_U, 0.0) * u.V * talon / combo.B if u else 0.0
        salida.append(SolicitacionDeElemento(**marca, 
            elemento=ELEMENTO_ZAPATA, seccion="talon, cara de la pantalla",
            combinacion=combo.nombre,
            V_u=abajo + w_zap * talon - sigma * sobre_talon - sub,
            M_u=(m_abajo + w_zap * talon ** 2 / 2
                 - sigma * sobre_talon ** 2 / 2 - sub * talon / 2),
            nota="relleno, sobrecarga, componente vertical del empuje y "
                 "peso propio, menos la presion de contacto que alcanza al "
                 "talon y la subpresion (repartida uniforme); positivo = "
                 "tracciona la cara superior"))
    return tuple(salida)


# ---------------------------------------------------------------------------
# El ensamble de UN cabezal en UNA condicion
# ---------------------------------------------------------------------------

def _pasos_de_cargas(entorno, condicion, cargas, combos, datos,
                     sufijo) -> List[PasoDeMemoria]:
    ext = entorno.extremo
    ang = datos["angulos"]
    rel = datos["relleno"]
    pasos = []
    if condicion is CondicionAnalisis.ESTATICO:
        pasos.append(paso(
            "F9.EMPUJES", codigo=f"9.2.1.{sufijo}",
            que=f"Empuje activo del relleno: cabezal de {ext}",
            formula=(("K_A = 2·max_rho P_cuña(rho) / (gamma·h²), P_cuña = "
                      "W·sen(rho - phi) / cos(rho - phi - delta);  "
                      if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else "")
                     + "P_A = K_A·[gamma·h1²/2 + gamma·h1·h_w + (gamma_sat - "
                     "gamma_w)·h_w²/2];  E_h = P_A·cos(delta + beta);  E_v = "
                     "P_A·sen(delta + beta)"),
            formula_cita_id=("AASHTO_LRFD_9.3.11.5.3#CULMANN"
                             if datos["metodo_empuje"] == METODO_EMPUJE_CUNA
                             else "MP.2.4.4.1.5.3"),
            sustitucion=(
                _m("phi", ang["phi"], "grados",
                   f"criterio '{CRITERIO_PHI_RELLENO}': ensayo del relleno"),
                _m("delta", ang["delta"], "grados", ang["origen_delta"]),
                _m("i", ang["i"], "grados", rel["origen_i"]),
                _m("beta", ang["beta"], "grados", "plano de empuje: "
                   + ang["plano"]),
                _m("gamma", datos["gamma"], "kN/m3",
                   f"criterio '{CRITERIO_GAMMA_RELLENO}'"),
                _m("h", datos["h"], "m",
                   "altura del plano de empuje: de la base de la zapata al "
                   "terreno que queda sobre el extremo del talon (relleno "
                   f"retenido {rel['z_rel']:.3f} m + {rel['sobre_talon']:.3f}"
                   " m que el talud sube sobre el talon)"),
                _m("h_w", datos["h_w"], "m",
                   "altura de agua en el plano de empuje (paso del agua)"),
                _m("subida", rel["subida_sobre_plano"], "m",
                   "lo que el relleno sigue subiendo sobre el tope del "
                   f"plano, con talud 1:{rel['talud']:g}, hasta la "
                   "plataforma (superficie de la cuña)"),
                _m("K_A", datos["K_A"], "-",
                   ("EQUIVALENTE de la cuña critica de Culmann sobre la "
                    f"superficie real (rho = {datos['rho_A']:.2f} grados; "
                    "AASHTO 3.11.5.3)"
                    if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                    "Coulomb con la pendiente i, Manual de Puentes "
                    "2.4.4.1.5.3 / AASHTO 3.11.5.3")),
                _m("K_A_formula", datos["K_A_formula"], "-",
                   ("CONTRASTE: Coulomb con la pendiente equivalente i "
                    f"(regla 2H); {_sesgo(datos['K_A_formula'], datos['K_A'])}"
                    if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                    "el que rige (formula cerrada)"))),
            resultado=Magnitud(
                "E_h / E_v",
                f"{_carga(cargas, C_EH_H).H:.3f} / "
                f"{_carga(cargas, C_EH_V).V:.3f}", "kN/m",
                f"P_A = {datos['P_A']:.3f} kN/m, a {datos['z_A']:.3f} m "
                "sobre la base"),
            citas_textuales=("AASHTO_LRFD_9.C3.11.5.3#PLANO_DEL_TALON",
                             "AASHTO_LRFD_9.C3.11.5.3#DELTA",
                             "AASHTO_LRFD_9.3.11.5.8.1#CUNA",
                             "AASHTO_LRFD_9.C3.11.5.8.1#TALUD_QUEBRADO",
                             # El regimen del cabezal y el K0 que la
                             # interfaz de T-7c marca (H7).
                             "AASHTO_LRFD_9.C11.6.5.4#K0",
                             "AASHTO_LRFD_9.3.11.5.2#K0"),
            nota_del_proyecto=(
                "El empuje ya no se toma entero como horizontal (ficha "
                "EXT-7-04): la componente vertical carga la base en el plano "
                "de empuje. "
                + ("METODO: la cuña de tanteo de Culmann sobre el plano "
                   "vertical del talon con la superficie REAL del relleno "
                   f"(regla '{rel['regla']}', '{CRITERIO_REGLA_PENDIENTE}' "
                   "[A]): lo que la fuente pide para un relleno que se "
                   "aparta del talud uniforme. Su coeficiente equivalente se "
                   "reparte con el diagrama triangular de Coulomb (resultante "
                   "a h/3 en seco) y, bajo el agua, con el suelo sumergido. "
                   "La pendiente equivalente 2H (Figura C3.11.5.8.1-1, de los "
                   "muros de suelo reforzado) queda como contraste y como "
                   "alternativa barrible."
                   if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                   "METODO: la formula cerrada con la pendiente i "
                   f"({rel['origen_i']}). La regla general de la fuente para "
                   "un relleno quebrado es la cuña de tanteo, que es la de "
                   "archivo; la pendiente equivalente 2H la subestima del 7 "
                   "al 11 % en los cabezales de A-01.")
                + f" Regimen del cabezal: '{datos['regimen']}' "
                f"('{CRITERIO_REGIMEN}' [A]): empuje activo de muro que "
                "cede, la hipotesis de la estabilidad externa (C11.6.5.4)."
                )))
        ls = _carga(cargas, C_LS_H)
        pasos.append(paso(
            "F9.SOBRECARGA", codigo=f"9.2.2.{sufijo}",
            que=f"Sobrecarga viva de trafico: cabezal de {ext}",
            formula="LS_h = K_A·gamma·h_eq·h;  LS_v = gamma·h_eq·talon",
            formula_cita_id="AASHTO_LRFD_9.3.11.6.4",
            sustitucion=(
                _m("h_eq", datos["h_eq"], "m",
                   "max(piso del Manual de Puentes, tabla de AASHTO "
                   "3.11.6.4 por altura h y orientacion del muro: [S] "
                   "'orientacion_muro_respecto_al_trafico' = "
                   f"'{ds.valor('orientacion_muro_respecto_al_trafico')}')"),
                _m("h", datos["h"], "m", "altura del plano de empuje, con "
                   "zapata"),
                _m("K_A", datos["K_A"], "-", "el del empuje activo")),
            resultado=Magnitud(
                "LS_h / LS_v",
                f"{ls.H:.3f} / "
                f"{(_carga(cargas, C_LS_V).V if _tiene(cargas, C_LS_V) else 0.0):.3f}",
                "kN/m", "empuje a h/2; peso sobre el talon"),
            citas_textuales=("AASHTO_LRFD_9.C11.5.6#SOBRECARGA",),
            nota_del_proyecto=(
                "Aplica siempre en un cabezal bajo terraplen vial (Sec. "
                "9.2). El cabezal es NORMAL al eje del conducto (decision "
                "del dueño): con un cruce sin esviaje su trasdos queda "
                "paralelo a la via, y con esviaje "
                f"({entorno.esviaje_grados:g} grados) forma ese angulo con "
                "ella; AASHTO solo tabula el muro paralelo y el estribo "
                "perpendicular, y se lee la tabla del dato de sitio "
                "declarado. El PESO de la sobrecarga sobre el talon entra "
                "solo en el portante.")))
        pasos.append(paso(
            "F9.AGUA", codigo=f"9.2.3.{sufijo}",
            que=f"Agua en el trasdos y subpresion: cabezal de {ext}",
            formula=("E_w = gamma_w·h_w²/2;  U = gamma_w·(h_delante + "
                     "h_w)/2·B"),
            formula_cita_id="AASHTO_LRFD_9.3.11.3",
            sustitucion=(
                _m("cota_NF", datos["cota_freatico"], "msnm",
                   entorno.origen_freatico or "cota del nivel freatico"),
                _m("cota_desplante", entorno.geometria.cota_desplante,
                   "msnm", "base de la zapata de este cabezal (T-7a)"),
                _m("D_f", datos["D_f"], "m", "profundidad de desplante"),
                _m("h_delante", datos["h_w_natural"], "m",
                   "agua sobre la base por el freatico natural: max(cota_NF "
                   "- cota_desplante, 0), no mayor que h"),
                _m("h_w", datos["h_w"], "m",
                   f"agua en el relleno con '{CRITERIO_DRENAJE}' = "
                   f"'{datos['drenaje']}': "
                   + ("hasta la superficie del relleno retenido contra el "
                      "trasdos (z_rel; sin drenaje declarado, AASHTO "
                      "11.6.6), nunca por encima del muro"
                      if datos["drenaje"] == DRENAJE_SIN else
                      "el freatico natural (drenaje declarado: filtro y "
                      "lloraderos en planos)"))),
            resultado=Magnitud(
                "E_w / U",
                f"{(_carga(cargas, C_WA_H).H if _tiene(cargas, C_WA_H) else 0.0):.3f}"
                f" / {(-_carga(cargas, C_WA_U).V if _tiene(cargas, C_WA_U) else 0.0):.3f}",
                "kN/m", "empuje hidrostatico sobre el plano de empuje / "
                "subpresion bajo la zapata"),
            citas_textuales=("AASHTO_LRFD_9.11.6.6#DRENAJE",
                             "E050.39.13.8#DRENAJE"),
            nota_del_proyecto=(
                "Bajo el nivel del agua el suelo empuja con su peso "
                "sumergido y el agua aparte: no se cuenta dos veces. "
                "El agua delante del muro no se cuenta como "
                "empuje que estabilice. El drenaje reduce el agua del "
                "relleno SOLO si se declara, y compromete un detalle que "
                "tiene que estar en los planos.")))
    else:
        pasos.append(paso(
            "F9.SISMO", codigo=f"9.2.4.{sufijo}",
            que=f"Demanda sismica: cabezal de {ext}",
            formula=("P_AE = gamma·h²·(1 - k_v)·K_AE / 2;  dP_AE = P_AE - "
                     "P_A, a f·h;  P_IR = k_h·(W_w + W_s)"),
            formula_cita_id="AASHTO_LRFD_9.A11.3.1#KAE",
            sustitucion=(
                _m("k_h", datos["k_h"], "-",
                   "cadena sismica de Sec. 9.2 (PGA, F_pga y "
                   f"'{CRITERIO_FACTOR_MURO}' = "
                   f"'{ca.valor(CRITERIO_FACTOR_MURO)}')"),
                _m("k_v", datos["k_v"], "-", f"criterio '{CRITERIO_K_V}'"),
                _m("phi", ang["phi"], "grados", "relleno"),
                _m("i", ang["i"], "grados", rel["origen_i"]),
                _m("delta", ang["delta"], "grados", ang["origen_delta"]),
                _m("K_AE", datos["K_AE"], "-",
                   ("EQUIVALENTE de la cuña critica pseudoestatica, "
                    "2·P_AE/(gamma·h²·(1 - k_v)) (rho = "
                    f"{datos['rho_AE']:.2f} grados; AASHTO C11.6.5.3)"
                    if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                    "Mononobe-Okabe")),
                _m("K_AE_formula",
                   (datos["K_AE_formula"] if datos["K_AE_formula"]
                    is not None else "no evaluable"), "-",
                   ("CONTRASTE: Mononobe-Okabe con la pendiente equivalente "
                    "i; " + (_sesgo(datos["K_AE_formula"], datos["K_AE"])
                             if datos["K_AE_formula"] is not None else
                             f"fuera de su dominio: phi = {ang['phi']:.2f} < "
                             f"i + psi = {ang['i'] + datos['psi']:.2f} "
                             "grados (11.6.5.3)")
                    if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                    "el que rige (formula cerrada)")),
                _m("K_A", datos["K_A"], "-", "el estatico, misma "
                   "formulacion"),
                _m("h", datos["h"], "m", "altura del plano de empuje"),
                _m("f", datos["fraccion_brazo"], "-",
                   f"criterio '{CRITERIO_BRAZO_SISMICO}' [C]"),
                _m("W_w", datos["W_w"], "kN/m", "peso del muro"),
                _m("W_s", datos["W_s"], "kN/m", "peso del relleno sobre el "
                   "talon")),
            resultado=Magnitud(
                "P_AE / P_IR",
                f"{datos['P_AE']:.3f} / "
                f"{datos['k_h'] * (datos['W_w'] + datos['W_s']):.3f}",
                "kN/m",
                f"resultante del empuje total a {datos['z_AE']:.3f} m "
                f"sobre la base ({datos['z_AE'] / datos['h']:.2f}·h)"),
            citas_textuales=("AASHTO_LRFD_9.11.6.5.3#VALIDEZ",
                             "AASHTO_LRFD_9.C11.6.5.3#CUNA",
                             "AASHTO_LRFD_9.C11.6.5.3#RESULTANTE",
                             "AASHTO_LRFD_9.C11.6.5.4#CEDENTE",
                             "AASHTO_LRFD_9.11.6.5.4#NO_CEDENTE"),
            nota_del_proyecto=(
                ("Cuña de tanteo pseudoestatica (C11.6.5.3) con la "
                 "superficie real, relleno sin agua en el plano de empuje; "
                 "Mononobe-Okabe con la pendiente equivalente queda al lado "
                 "como contraste. "
                 if datos["metodo_empuje"] == METODO_EMPUJE_CUNA else
                 "Mononobe-Okabe dentro de su dominio: relleno sin agua en "
                 f"el plano de empuje y phi = {ang['phi']:.2f} >= i + psi = "
                 f"{ang['i']:.2f} + {datos['psi']:.2f} grados. ")
                + "Regimen del cabezal CEDENTE ('regimen_cabezal' [A]): un "
                "muro que no cede pediria k_h = 1.0·k_h0 y presiones mayores "
                "(11.6.5.4). Los dos casos "
                "del 11.6.5.1 se combinan aparte: 100 % P_AE + 50 % P_IR, y "
                "50 % P_AE (no menos que el empuje estatico) + 100 % P_IR. "
                "La fraccion f se aplica al INCREMENTO; el empuje estatico "
                "sigue en su centroide.")))
    filas = tuple(
        Magnitud(c.codigo,
                 (f"V = {c.V:.3f} kN/m, x = {c.x:.3f} m" if c.V else "")
                 + (f"H = {c.H:.3f} kN/m, z = {c.z:.3f} m" if c.H else ""),
                 "", f"{c.descripcion}; {c.procedencia}")
        for c in cargas)
    resumen = "; ".join(
        f"«{c.nombre}»: N = {c.N:.2f}, H = {c.H:.2f} kN/m, M_e = "
        f"{c.M_estabilizante:.2f}, M_v = {c.M_volcante:.2f} kN·m/m"
        for c in combos)
    pasos.append(paso(
        "F9.COMBINACIONES", codigo=f"9.2.5.{sufijo}",
        que=f"Cargas con sus brazos y combinaciones: cabezal de {ext}, "
            f"condicion {condicion.value}",
        formula=("N = Σ gamma·V;  H = Σ gamma·H;  M respecto de la punta = "
                 "Σ gamma·(V·x - H·z)"),
        sustitucion=filas,
        resultado=Magnitud("combinaciones", len(combos), "",
                           "de los dos marcos, cada una con SUS factores"),
        citas_textuales=("AASHTO_LRFD_9.C11.5.6#FIGURAS",
                         "E050.17.1#SERVICIO"),
        nota_del_proyecto=(
            "x se mide desde la arista de la punta hacia el relleno y z "
            "desde la base de la zapata hacia arriba; V positiva hacia "
            "abajo y H positiva hacia el cauce. " + resumen + ". Factores "
            "de cada combinacion: "
            + "; ".join(
                f"«{c.nombre}»: " + ", ".join(
                    f"{k} {v:g}" for k, v in c.factores)
                for c in combos) + ".")))
    return pasos


def _carga(cargas: tuple, codigo: str) -> CargaDeCabezal:
    return next(c for c in cargas if c.codigo == codigo)


def _tiene(cargas: tuple, codigo: str) -> bool:
    return any(c.codigo == codigo for c in cargas)


PENDIENTES_E4_E5 = (
    ("E4", "estabilidad global del muro: analisis de equilibrio limite con "
           "la estratigrafia del EMS (AASHTO LRFD 11.6.3.7; E.050 39.13.6 "
           "b). Diferida al expediente: el programa no la evalua"),
    ("E5", "estabilidad del talud que soporta al cabezal (E.050 Art. 30.3). "
           "Diferida al expediente con el EMS: el programa no la evalua"),
)


def ensamble_estabilidad(entorno: EntornoDelCabezal,
                         condicion: CondicionAnalisis
                         ) -> EstabilidadDelCabezal:
    """
    La estabilidad externa de UN cabezal en UNA condicion (INF-4.4, INF-4.5,
    INF-5.1.5): cargas sin factorar con sus brazos, combinaciones de los dos
    marcos, las verificaciones E1 a E3 de cada marco -- seis filas --, las
    solicitaciones factoradas por elemento y los pasos de memoria.

    DOS MARCOS QUE NO SE CRUZAN. El LRFD compara cargas factoradas con
    resistencias minoradas y la excentricidad con su limite; el ASD compara
    cargas de servicio con la resistencia nominal dividida por el factor de
    seguridad de E.050. Cual decide lo declara 'marco_estabilidad_cabezal'
    [A]: las verificaciones del marco que no decide salen como INDICADOR.

    SE DETIENE -- con `ErrorProyecto`, que el servicio registra como
    `Bloqueo` del punto -- en lo que falte: el angulo de friccion del relleno
    o los parametros del suelo de fundacion (criterios sin valor), la
    profundidad del freatico (columna vacia), la orientacion del muro frente
    al trafico ([S] sin leer) o, bajo sismo, Mononobe-Okabe fuera de su
    dominio de validez (`MetodoNoEvaluableError`).

    E4 y E5 no se evaluan: viajan en `pendientes`, con su motivo.
    """
    if condicion not in CONDICIONES_DE_ESTABILIDAD:
        raise DatoInvalidoError("condicion", valor=condicion,
                                motivo="estatico o sismico")
    g = entorno.geometria
    regla = _regla_de_marco()
    if _regimen() == REGIMEN_NO_CEDENTE:
        raise _no_evaluable(
            f"estabilidad del cabezal de {entorno.extremo}",
            "presiones de un muro que no cede (empuje en reposo K0 en "
            "resistencia; k_h = 1.0·k_h0 y resultante en h/2 bajo sismo: "
            "AASHTO 11.6.5.4 y C11.6.5.4)",
            f"'{CRITERIO_REGIMEN}' = '{REGIMEN_NO_CEDENTE}': el ensamble "
            "calcula el cabezal que CEDE (empuje activo, 11.6.5.3) y no "
            "implementa el que no cede; el comentario de la fuente admite "
            "un analisis numerico aprobado por el Propietario",
            entorno.id_punto)
    suelo, origen_suelo = suelo_de_fundacion(entorno.suelo,
                                             id_punto=entorno.id_punto)
    cargas, datos = cargas_del_cabezal(entorno, condicion)
    combos = combinaciones_de_estabilidad(cargas, datos, condicion, g.B)
    sufijo = f"{ABREVIATURA_DE_CONDICION[condicion]}.{entorno.extremo[0]}"
    verificaciones = (
        _verificaciones_lrfd(entorno, datos, suelo, combos, condicion,
                             _decide(MARCO_LRFD, regla), sufijo)
        + _verificaciones_asd(entorno, datos, suelo, combos, condicion,
                              _decide(MARCO_ASD, regla), sufijo))
    verificaciones.sort(key=lambda v: v.codigo)
    pasos = _pasos_de_cargas(entorno, condicion, cargas, combos, datos,
                             sufijo)
    avisos = _avisos_de_sensibilidad(entorno, datos, suelo, combos,
                                     condicion, regla, sufijo,
                                     verificaciones)
    if condicion is CondicionAnalisis.ESTATICO:
        pasos.append(paso(
            "F9.GLOBAL", codigo=f"9.3.g.{entorno.extremo[0]}",
            que=f"E4 y E5, estabilidad global y del talud: cabezal de "
                f"{entorno.extremo}",
            formula="FS de equilibrio limite >= FS minimo (no evaluado)",
            sustitucion=(Magnitud("suelo de fundacion", origen_suelo, "",
                                  "lo que si se uso en E1 a E3"),),
            resultado=Magnitud("E4, E5", "diferidas al expediente con el "
                               "EMS", "", "; ".join(m for _, m in
                                                   PENDIENTES_E4_E5)),
            nota_del_proyecto=(
                "No son un cumplimiento: el cabezal queda verificado en E1 "
                "a E3 y PENDIENTE en estas dos, que necesitan la "
                "estratigrafia completa y un analisis de superficies de "
                "falla.")))
        avisos.append(
            f"Cabezal de {entorno.extremo} de {entorno.id_punto}: E4 y E5 "
            "(estabilidad global del muro y del talud) NO se evaluan; "
            "quedan diferidas al expediente con el estudio de suelos "
            "(AASHTO LRFD 11.6.3.7; E.050 39.13.6 b y Art. 30.3)")
        if datos["drenaje"] == DRENAJE_SIN:
            avisos.append(
                f"Cabezal de {entorno.extremo} de {entorno.id_punto}: sin "
                f"drenaje declarado del trasdos ('{CRITERIO_DRENAJE}' = "
                f"'{DRENAJE_SIN}'), la estabilidad se calcula con el relleno "
                "retenido lleno de agua hasta su superficie contra el "
                "trasdos (AASHTO 11.6.6), y la condicion sismica no es "
                "evaluable (relleno saturado, 11.6.5.3). Declarar el "
                "drenaje ('drenado') lo deja en el freatico natural y "
                "compromete el filtro y los lloraderos en planos")
        else:
            avisos.append(_aviso_desembalse_rapido(entorno, datos, cargas))
        if suelo["cohesivo"]:
            avisos.append(
                f"Cabezal de {entorno.extremo} de {entorno.id_punto}: suelo "
                "de fundacion cohesivo; la resistencia al deslizamiento del "
                "marco LRFD supone al menos 6.0 in (0.15 m) de material "
                "granular compactado bajo la zapata (AASHTO 10.6.3.4), que "
                "tiene que estar en los planos")
    return EstabilidadDelCabezal(
        id_punto=entorno.id_punto, extremo=entorno.extremo,
        condicion=condicion, regla_de_marco=regla, cargas=cargas,
        combinaciones=combos, verificaciones=tuple(verificaciones),
        solicitaciones=solicitaciones_por_elemento(entorno, cargas, combos,
                                                   datos),
        pasos=tuple(pasos), avisos=tuple(avisos),
        pendientes=PENDIENTES_E4_E5, K_A=datos["K_A"], K_AE=datos["K_AE"],
        i_grados=datos["angulos"]["i"], delta_grados=datos["angulos"]["delta"],
        altura_empuje=datos["h"], h_eq=datos["h_eq"], k_h=datos["k_h"],
        metodo_empuje=datos["metodo_empuje"],
        K_A_contraste=(datos["K_A_formula"] if datos["metodo_empuje"]
                       == METODO_EMPUJE_CUNA else None),
        K_AE_contraste=(datos["K_AE_formula"] if datos["metodo_empuje"]
                        == METODO_EMPUJE_CUNA else None),
        regimen=datos["regimen"], K0=datos["K0"])


def _sin_parar(calculo):
    """
    El contraste de sensibilidad no detiene el ensamble: si con la otra
    opcion algo no se puede evaluar, ese contraste se omite (devuelve None).
    """
    try:
        return calculo()
    except ErrorProyecto:
        return None


def _aviso_desembalse_rapido(entorno: EntornoDelCabezal, datos: dict,
                             cargas: tuple) -> str:
    """
    El aviso que acompaña al drenaje DECLARADO (correcciones de T-7b, H6):
    el modelo toma el agua del relleno en el freatico natural y NO el
    desembalse rapido tras la avenida -- el relleno mojado hasta la cota del
    agua de diseño con el cauce ya vacio --, que el comentario C11.6.6 hace
    plausible al advertir que los lloraderos no aseguran el drenaje. Con el
    nivel de diseño conocido da el orden de magnitud: la hidrostatica que
    ese relleno mojado ejerceria contra la componente horizontal del empuje.
    """
    base = (f"Cabezal de {entorno.extremo} de {entorno.id_punto}: con el "
            f"drenaje del trasdos declarado ('{CRITERIO_DRENAJE}' = "
            f"'{DRENAJE_CON}') el agua del relleno se toma en el freatico "
            "natural; el modelo NO contempla el desembalse rapido -- el "
            "relleno mojado por la avenida con el cauce ya vacio -- y la "
            "fuente advierte que los lloraderos solos no aseguran el drenaje "
            "(AASHTO C11.6.6)")
    if datos["cota_agua_diseno"] is None:
        return base
    h_av = min(max(datos["cota_agua_diseno"]
                   - entorno.geometria.cota_desplante, 0.0), datos["z_rel"])
    E_av = GAMMA_AGUA_KN_M3 * h_av ** 2 / 2
    EH = sum(c.H for c in cargas if c.codigo == C_EH_H)
    return (base + f". Orden de magnitud: con el relleno mojado hasta la "
            f"cota del agua de diseño ({datos['cota_agua_diseno']:.2f} msnm, "
            f"{h_av:.2f} m sobre la base) la hidrostatica seria del orden de "
            f"gamma_w·h²/2 = {E_av:.1f} kN/m, frente a {EH:.1f} kN/m de la "
            "componente horizontal del empuje del suelo")


def _avisos_de_sensibilidad(entorno, datos, suelo, combos, condicion, regla,
                            sufijo, verificaciones) -> List[str]:
    """
    Las filas cuyo VEREDICTO cambia entre las opciones de la ventana de las
    dos elecciones [A] que mas mueven la estabilidad (correcciones de T-7b,
    H5): la fila de phi ('fila_phi_estabilidad_cabezal', solo en la
    estatica: bajo sismo phi es del 11.5.8 y no se elige) y los factores de
    inclinacion de la carga en el portante
    ('factores_inclinacion_carga_portante', en las dos condiciones y en los
    dos marcos). Cada aviso dice la fila, las dos opciones y las dos cifras:
    un incumplimiento que se invierte dentro de la ventana es SENSIBLE a una
    eleccion, no un hecho del cabezal.
    """
    actual = {v.codigo: v for v in verificaciones}
    fila_actual = ca.valor(CRITERIO_FILA_PHI)
    inclinacion_actual = ca.valor(CRITERIO_INCLINACION_PORTANTE)
    contrastes = []
    if condicion is CondicionAnalisis.ESTATICO:
        for fila in FILAS_DE_PHI:
            if fila != fila_actual:
                contrastes.append((CRITERIO_FILA_PHI, fila_actual, fila,
                                   _sin_parar(lambda f=fila: _verificaciones_lrfd(
                                       entorno, datos, suelo, combos,
                                       condicion, _decide(MARCO_LRFD, regla),
                                       sufijo, fila=f))))
    for opcion in (INCLINACION_APLICAR, INCLINACION_OMITIR):
        if opcion != inclinacion_actual:
            contrastes.append((CRITERIO_INCLINACION_PORTANTE,
                               inclinacion_actual, opcion,
                               _sin_parar(lambda o=opcion: _verificaciones_lrfd(
                                   entorno, datos, suelo, combos, condicion,
                                   _decide(MARCO_LRFD, regla), sufijo,
                                   inclinacion=o)
                                   + _verificaciones_asd(
                                   entorno, datos, suelo, combos, condicion,
                                   _decide(MARCO_ASD, regla), sufijo,
                                   inclinacion=o))))

    def cifra(v) -> str:
        if v.valor_obtenido is None or v.valor_admisible is None:
            return "sin cifra"
        return (f"{v.valor_obtenido:.2f} contra {v.valor_admisible:.2f} "
                f"({'cumple' if v.cumple else 'no cumple'})")

    avisos = []
    for criterio, de_archivo, otra, alternativas in contrastes:
        if alternativas is None:
            continue
        for v in alternativas:
            base = actual.get(v.codigo)
            if base is None or base.cumple == v.cumple:
                continue
            avisos.append(
                f"Cabezal de {entorno.extremo} de {entorno.id_punto}, "
                f"condicion {condicion.value}: {v.codigo} CAMBIA DE "
                f"VEREDICTO dentro de la ventana de '{criterio}' [A]: con "
                f"'{de_archivo}' {cifra(base)}; con '{otra}' {cifra(v)}. El "
                "veredicto es sensible a esa eleccion")
    return avisos


def datos_del_cabezal_del_punto(*, punto, cabezal: CabezalDelPunto,
                                geometria, socavacion=None,
                                suelo_del_punto: Optional[dict] = None,
                                resultado=None
                                ) -> Tuple[EntornoDelCabezal, EntornoDelCabezal]:
    """
    Los dos `EntornoDelCabezal` de un punto (entrada y salida), leidos de lo
    que la Fase 9 de T-7a ya resolvio y de 7.B, sin decidir nada otra vez:
    el relleno retenido llega a la coronacion menos el bordillo; el talud y
    el borde de la plataforma de cada lado son los de la longitud por
    extremo de 7.B (o, si la longitud se declaro, el criterio
    'talud_terraplen' y la rasante en el eje); el freatico, la columna del
    CSV; el terreno del pie, el de la geometria del cabezal; y la hoya de
    socavacion, la que la Fase 6 entrego para la salida (`socavacion`, la
    misma que `extremos_del_conducto` leyo para el desplante).

    EL FREATICO VIAJA COMO COTA (correcciones de T-7b, H1): la columna
    NF_profundidad_m se mide bajo el terreno natural del CRUCE
    (`punto.cota_terreno`), como en M8, en el censo de `variables_entrada` y
    en el contrato de entradas, y la cota es la misma para los dos cabezales.
    La FASE A la medía bajo el pie de cada cabezal, y en la salida de A-01
    dejaba el agua 0.80 m mas baja que donde esta.

    Con `resultado` (el `ResultadoPunto` de la Fase 4) el entorno lleva
    tambien el nivel del agua de diseño contra cada cabezal, el mismo de
    `extremos_del_conducto`: solo lo lee el aviso del desembalse rapido.
    """
    reglas = _reglas()
    nf = punto.NF_profundidad_m
    if nf is None:
        cota_freatico, origen_nf = None, ""
    else:
        _exigir_finito("NF_profundidad_m", nf, "profundidad del nivel "
                       "freatico", punto.id)
        _exigir_finito("cota_terreno", punto.cota_terreno, "terreno del "
                       "cruce", punto.id)
        cota_freatico = punto.cota_terreno - nf
        origen_nf = (f"cota_terreno - NF_profundidad_m = "
                     f"{punto.cota_terreno:.3f} - {nf:.3f}: el freatico se "
                     "mide bajo el terreno natural del cruce (columna del "
                     "CSV, del EMS), la misma cota para los dos cabezales")
    agua_de = {}
    if resultado is not None:
        for x in extremos_del_conducto(punto=punto, resultado=resultado,
                                       geometria=geometria,
                                       socavacion=socavacion):
            agua_de[x.extremo] = x.cota_agua
    bordillo = reglas["bordillo_m"]
    calculada = geometria.longitud_calculada
    talud = (calculada.talud if calculada is not None
             and calculada.talud is not None
             else ca.valor(CRITERIO_TALUD_TERRAPLEN))
    entornos = []
    for g in cabezal.geometrias:
        es_entrada = g.extremo == EXTREMO_ENTRADA
        borde = None
        if calculada is not None:
            borde = (calculada.cota_borde_entrada if es_entrada
                     else calculada.cota_borde_salida)
        if borde is not None:
            origen = "borde de la plataforma de ese lado, de 7.B"
        else:
            borde = punto.cota_rasante
            origen = ("rasante en el eje (columna cota_rasante): 7.B no "
                      "calculo el borde de la plataforma")
        entornos.append(EntornoDelCabezal(
            id_punto=punto.id, extremo=g.extremo, geometria=g,
            cota_relleno=g.cota_coronacion - bordillo,
            cota_borde_plataforma=borde, origen_cota_borde=origen,
            talud=talud, esviaje_grados=punto.esviaje_grados,
            cota_freatico=cota_freatico, origen_freatico=origen_nf,
            cota_pie=g.losa.cota_terreno if g.losa is not None
            else g.cota_desplante + g.D_f,
            cota_fondo_hoya=(None if es_entrada or socavacion is None
                             else socavacion.cota_fondo_de_la_hoya),
            suelo=suelo_del_punto,
            cota_agua_diseno=agua_de.get(g.extremo)))
    return tuple(entornos)


def integrar_estabilidad(cabezal: CabezalDelPunto,
                         estabilidades: Sequence[EstabilidadDelCabezal]
                         ) -> CabezalDelPunto:
    """
    El `CabezalDelPunto` con la estabilidad de sus cabezales incorporada:
    las verificaciones E1 a E3 se suman a las CB (la via por la que
    `InformePunto` cuenta incumplidas e indicadores), los pasos y los avisos
    a los suyos, y los objetos enteros quedan en `estabilidad`.
    """
    from dataclasses import replace as _replace
    estabilidades = tuple(estabilidades)
    avisos = list(cabezal.avisos)
    for e in estabilidades:
        avisos.extend(a for a in e.avisos if a not in avisos)
    # --- correcciones de T-7b (H8) --- un cabezal con SOLO UNA de las dos
    # condiciones evaluadas se avisa: la otra quedo como `Bloqueo` del punto
    # y la tabla del cabezal no puede leerse como completa.
    for g in cabezal.geometrias:
        evaluadas = [e.condicion for e in estabilidades
                     if e.extremo == g.extremo]
        if len(evaluadas) == 1:
            falta = next(c for c in CONDICIONES_DE_ESTABILIDAD
                         if c not in evaluadas)
            avisos.append(
                f"Cabezal de {g.extremo} de {cabezal.id_punto}: su "
                f"estabilidad se evaluo SOLO en la condicion "
                f"{evaluadas[0].value}; la {falta.value} quedo sin evaluar "
                "(ver «Etapas bloqueadas»): E1 a E3 de ese cabezal no estan "
                "completas")
    return _replace(
        cabezal,
        verificaciones=cabezal.verificaciones + tuple(
            v for e in estabilidades for v in e.verificaciones),
        pasos=cabezal.pasos + tuple(p for e in estabilidades
                                    for p in e.pasos),
        avisos=tuple(avisos), estabilidad=estabilidades)
