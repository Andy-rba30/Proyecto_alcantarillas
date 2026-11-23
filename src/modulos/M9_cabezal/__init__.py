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

--- T-7c --- Y LO QUE DESCRIBE DE 9.4 TAMBIEN CAMBIO. El diseño por flexion
y corte EXISTE (`diseno_flexion_corte`, bloque «9.4 · EL ARMADO DE CADA
CABEZAL» del final del modulo): cada cabezal de voladizo armado sale con el
armado de su pantalla, de la punta y del talon de su zapata y del arranque de
sus aleros (`armar_elemento`, `ensamblar_armado`), con AASHTO LRFD Seccion 5
y E.060 de contraste; y el de gravedad, con su verificacion como concreto
ciclopeo (`verificar_cabezal_ciclopeo`). De los vacios de abajo, tres dejaron
de serlo: los dos pisos de cuantia del cortante en el plano tienen el valor
de su articulo y el regimen del cortante esta declarado. Los parrafos
«cortante_alto_muro_...» y «procedimiento_flexion_...» de la lista de abajo
describen el estado ANTERIOR.

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
    talud_delante_del_cabezal    La geometria del talud que desciende delante
                                 de la zapata (H_s, beta, b), con
                                 'terreno_delante_del_cabezal' = talud: dato
                                 de topografia [S]. Desde VE-5 sustituye a
                                 'N_cq_N_gammaq_meyerhof' (las figuras de
                                 Meyerhof), retirado: la reduccion es la
                                 RC_BC de AASHTO 10.6.3.1.2c, que si se
                                 transcribe (tablas).
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

import sys as _sys
import types as _types

# Modulos externos expuestos en `M9_cabezal` (compatibilidad con tests)
import math
from typing import Any
from typing import Optional
from typing import Sequence
from typing import Tuple
from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src.constantes_fisicas import GAMMA_AGUA_KN_M3
from src.constantes_fisicas import PIE_EN_METROS
from src.constantes_normativas import AMBIENTE_CORROSIVO_AUMENTAR
from src.constantes_normativas import NUMERAL_CORTANTE_MUROS_E060
from src.constantes_normativas import AMBIENTE_CORROSIVO_TEXTO
from src.constantes_normativas import CARGA_VIVA
from src.constantes_normativas import CLASE_DE_SITIO_COHERENCIA_INTERNA
from src.constantes_normativas import CLASE_DE_SITIO_INDETERMINADA
from src.constantes_normativas import CLASE_DE_SITIO_POR_QUE_DEJA_DE_DECIRSE
from src.constantes_normativas import CLASE_DE_SITIO_QUE_LA_CIERRA
from src.constantes_normativas import HOMONIMIA_CLASE_F
from src.constantes_normativas import homonimia_como_texto
from src.constantes_normativas import CLASE_SITIO_EF_NO_SUPUESTA_MP_TEXTO
from src.constantes_normativas import CLASE_SITIO_EF_NO_SUPUESTA_TEXTO
from src.constantes_normativas import CLASE_SITIO_INVESTIGACION_TEXTO
from src.constantes_normativas import CICLOPEO_DOS_MINIMOS
from src.constantes_normativas import CICLOPEO_FC_MATRIZ_MIN_APLICABLE
from src.constantes_normativas import CICLOPEO_FRACCION_PIEDRA_MAX
from src.constantes_normativas import COMBINACIONES_AASHTO
from src.constantes_normativas import E030_AMBITO_LECTURA
from src.constantes_normativas import E030_S5_LECTURA
from src.constantes_normativas import E030_S5_TEXTO
from src.constantes_normativas import ESPACIAMIENTO_MAX_ABSOLUTO
from src.constantes_normativas import ESPACIAMIENTO_MAX_VECES_ESPESOR
from src.constantes_normativas import ESPESOR_DOS_CAPAS_REFUERZO
from src.constantes_normativas import ESPESOR_TEMPERATURA_DOS_CARAS
from src.constantes_normativas import EXCEPCION_DOS_CAPAS_REFUERZO
from src.constantes_normativas import EXCEPCION_REFUERZO_MIN_MURO_TEXTO
from src.constantes_normativas import EXPOSICION_ESPECIAL
from src.constantes_normativas import E030_ART_7_3_TEXTO
from src.constantes_normativas import EXCENTRICIDAD_ADMISIBLE_FRACCION_B
from src.constantes_normativas import EXCENTRICIDAD_ERRATA_MANUAL
from src.constantes_normativas import FACTOR_MURO_CON_REDUCCION
from src.constantes_normativas import FACTOR_MURO_DECLARACIONES
from src.constantes_normativas import F_PGA_CLASES_EN_ROCA
from src.constantes_normativas import F_PGA_EXIGE_ESTUDIO_DE_SITIO
from src.constantes_normativas import F_PGA_TABLA
from src.constantes_normativas import F_PGA_TABLA_PGA_COLUMNAS
from src.constantes_normativas import FS
from src.constantes_normativas import FS_NUMERAL
from src.constantes_normativas import GAMMA_P_MARCA
from src.constantes_normativas import HIPOTESIS_EMPUJE_BAJO_NF
from src.constantes_normativas import K_AE_ERRATA_MANUAL
from src.constantes_normativas import K_H0_FACTOR_ROCA_A_B
from src.constantes_normativas import K_H0_ROCA_ERRATA
from src.constantes_normativas import K_V_CASO_RESERVADO
from src.constantes_normativas import K_V_DECLARACION_PRESCRITO
from src.constantes_normativas import K_V_PRESCRITO
from src.constantes_normativas import LECTURA_COLUMNA_EXTREMA_ESTRICTA
from src.constantes_normativas import LECTURAS_COLUMNA_EXTREMA
from src.constantes_normativas import NQ_ZAPATA_EN_TALUD
from src.constantes_normativas import NUMERAL_AGUA_TRASDOS_AASHTO
from src.constantes_normativas import NUMERAL_C_PHI
from src.constantes_normativas import NUMERAL_CICLOPEO
from src.constantes_normativas import NUMERAL_CICLOPEO_APLICABLE
from src.constantes_normativas import NUMERAL_COMBINACION_4_2_4_4
from src.constantes_normativas import NUMERAL_DOS_CAPAS_REFUERZO
from src.constantes_normativas import NUMERAL_EXCEPCION_REFUERZO_MIN_MURO
from src.constantes_normativas import NUMERAL_EXPOSICION_ESPECIAL
from src.constantes_normativas import NUMERAL_PROTECCION_CORROSION
from src.constantes_normativas import PROTECCION_CORROSION_TEXTO
from src.constantes_normativas import NUMERAL_COMBINACIONES
from src.constantes_normativas import NUMERAL_CUANTIA_MIN
from src.constantes_normativas import NUMERAL_E030_AMBITO
from src.constantes_normativas import NUMERAL_CLASE_SITIO_AASHTO
from src.constantes_normativas import NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA
from src.constantes_normativas import NUMERAL_CLASE_SITIO_EF_NO_SUPUESTA_MP
from src.constantes_normativas import NUMERAL_CLASE_SITIO_INVESTIGACION
from src.constantes_normativas import NUMERAL_CLASE_SITIO_MP
from src.constantes_normativas import NUMERAL_LICUEFACCION_AASHTO
from src.constantes_normativas import NUMERAL_LICUEFACCION_ESPECTRO
from src.constantes_normativas import NUMERAL_RESPUESTA_DE_SITIO_AASHTO
from src.constantes_normativas import NUMERAL_RESPUESTA_DE_SITIO_MP
from src.constantes_normativas import NUMERAL_E030_S5
from src.constantes_normativas import NUMERAL_ESPACIAMIENTO
from src.constantes_normativas import NUMERAL_E030_ESTRUCTURAS_NO_EDIFICACION
from src.constantes_normativas import NUMERAL_EXCENTRICIDAD_ESTATICA
from src.constantes_normativas import NUMERAL_EXCENTRICIDAD_SISMICA
from src.constantes_normativas import NUMERAL_EXCENTRICIDAD_SISMICA_AASHTO
from src.constantes_normativas import NUMERAL_F_PGA_TABLA
from src.constantes_normativas import NUMERAL_FACTOR_MURO
from src.constantes_normativas import NUMERAL_K_AE_AASHTO
from src.constantes_normativas import NUMERAL_K_AE_MANUAL
from src.constantes_normativas import NUMERAL_KA_COULOMB
from src.constantes_normativas import KA_COULOMB_DECLARACION
from src.constantes_normativas import REGIMEN_CORTANTE_EN_EL_PLANO
from src.constantes_normativas import REGIMEN_CORTANTE_PERPENDICULAR
from src.constantes_normativas import REGIMENES_CORTANTE_MURO
from src.constantes_normativas import FS_CODIGO
from src.constantes_normativas import NUMERAL_K_H0
from src.constantes_normativas import NUMERAL_P_IR
from src.constantes_normativas import CUANTIA_MIN_MURO_E060_14_3_1
from src.constantes_normativas import NUMERAL_PRESION_CONTACTO
from src.constantes_normativas import NUMERAL_RECUBRIMIENTO
from src.constantes_normativas import NUMERAL_RECUBRIMIENTO_MP
from src.constantes_normativas import NUMERAL_SULFATOS
from src.constantes_normativas import NUMERAL_SOBRECARGA_TRASDOS
from src.constantes_normativas import NUMERAL_SOBRECARGA_TRASDOS_AASHTO
from src.constantes_normativas import NUMERAL_SOBRECARGA_TRASDOS_ALTURA
from src.constantes_normativas import NUMERAL_SOBRECARGA_TRASDOS_APLICA
from src.constantes_normativas import H_EQ_REPARTO_DE_TABLAS
from src.constantes_normativas import NUMERAL_TABLA_GAMMA_P
from src.constantes_normativas import NUMERAL_TEMPERATURA_DOS_CARAS
from src.constantes_normativas import NUMERAL_ZAPATA_EN_TALUD
from src.constantes_normativas import NUMERAL_ZAPATA_TALUD_E050
from src.constantes_normativas import P_SEIS_COMBINACIONES
from src.constantes_normativas import P_SEIS_PISO_ESTATICO
from src.constantes_normativas import RECUBRIMIENTO
from src.constantes_normativas import RECUBRIMIENTO_AC_UMBRAL_ALTO
from src.constantes_normativas import RECUBRIMIENTO_AC_UMBRAL_BAJO
from src.constantes_normativas import RECUBRIMIENTO_MP_FACTOR_AC
from src.constantes_normativas import RECUBRIMIENTO_MP_EQUIVALENCIA
from src.constantes_normativas import RECUBRIMIENTO_MP_MM
from src.constantes_normativas import RECUBRIMIENTO_MP_PISO_MM
from src.constantes_normativas import REDUCCION_KH_POR_DESPLAZAMIENTO
from src.constantes_normativas import SECCION_CABEZALES
from src.constantes_normativas import ORIENTACION_PARALELO_AL_TRAFICO
from src.constantes_normativas import ORIENTACION_PERPENDICULAR_AL_TRAFICO
from src.constantes_normativas import ORIENTACIONES_TABULADAS
from src.constantes_normativas import SOBRECARGA_TRASDOS_PISO_MP_M
from src.constantes_normativas import H_EQ_BORDE_UMBRAL_M
from src.constantes_normativas import H_EQ_ESTRIBO_PERPENDICULAR_FT
from src.constantes_normativas import H_EQ_MURO_PARALELO_FT
from src.constantes_normativas import SULFATOS
from src.constantes_normativas import TABLA_COMBINACIONES_FILAS
from src.constantes_normativas import TABLA_GAMMA_P_FILAS
from src.constantes_normativas import DQ_MAXIMO_10_6_3_1_2A_10
from src.constantes_normativas import FORMA_SC_PHI_CERO_DIVISOR
from src.constantes_normativas import FORMA_SGAMMA_COEFICIENTE
from src.constantes_normativas import NUMERAL_FORMA_PROFUNDIDAD
from src.constantes_normativas import NUMERAL_RCBC
from src.constantes_normativas import RCBC_BETAS_GRADOS
from src.constantes_normativas import RCBC_COLUMNAS_NS
from src.constantes_normativas import RCBC_EN_TALUD_T10_6_3_1_2C_1
from src.constantes_normativas import RCBC_JUNTO_AL_TALUD_T10_6_3_1_2C_2
from src.modelos import CIFRAS_FACTOR
from src.modelos import CadenaSismica
from src.modelos import CasoDemandaSismica
from src.modelos import CombinacionCarga
from src.modelos import EleccionDeProyecto
from src.modelos import Magnitud
from src.modelos import TipoDeVeredicto
from src.modelos import Umbral
from src.modelos import Veredicto
from src.modelos import paso
from src.modelos import CondicionAnalisis
from src.modelos import CuantiaRefuerzo
from src.modelos import DatoInvalidoError
from src.modelos import DemandaSismicaCabezal
from src.modelos import DisenoNoFactibleError
from src.modelos import EmpujeMononobeOkabe
from src.modelos import EmpujesTrasdos
from src.modelos import EstabilidadCabezal
from src.modelos import FuerzaInerciaMuro
from src.modelos import GeometriaCabezal
from src.modelos import PasoSismico
from src.modelos import PresionContactoBase
from src.modelos import RecubrimientoDiseno
from src.modelos import RequisitosDurabilidad
from src.modelos import ReferenciaNormativa
from src.modelos import Verificacion
from src.tolerancias import FRACCIONES_DE_ESTABILIDAD_DEL_ALERO
from src.tolerancias import TOL_ANGULO_CUNA
from src.tolerancias import TOL_UMBRAL_NORMATIVO
from src.tolerancias import TRAMOS_CUNA_DE_TANTEO
from src.constantes_normativas import BANDAS_ALETAS_CAJON_A1
from src.constantes_normativas import BANDAS_ALETAS_CAJON_C2
from src.constantes_normativas import BANDAS_ESVIAJE_CABEZAL_CAJON_A1
from src.constantes_normativas import KE_C2_POR_FILA_CARTA_11
from src.constantes_normativas import KE_C2_POR_FILA_SIN_ALETAS
from src.constantes_normativas import CAJON_A1_SIN_ALETAS
from src.constantes_normativas import CAJON_C2_SIN_ALETAS
from src.constantes_normativas import NUMERAL_ZAPATA_CONCRETO_SIMPLE
from src.dominios import MILIMETROS_POR_METRO
from src.modelos import ORIGEN_DIMENSION_DECLARADA
from src.modelos import ORIGEN_DIMENSION_DERIVADA
from src.modelos import ORIGEN_DIMENSION_ESTABILIDAD
from src.modelos import IntentoDeZapata
from src.modelos import ORIGEN_DIMENSION_ARMADO
from src.modelos import IntentoDePeralte
from src.modelos import ORIGEN_DIMENSION_REGLA
from src.modelos import Aleros
from src.modelos import CabezalDelPunto
from src.modelos import Familia
from src.modelos import LimiteNumericoError
from src.modelos import PasoDeMemoria
from src.modelos import DimensionDeCabezal
from src.modelos import EmbocaduraDelPunto
from src.modelos import ExtremoDelConducto
from src.modelos import LosaDeEntrega
from src.modelos import CIFRAS_MAGNITUD
from src.modelos import cifras_de_dimension
from src.modelos import FormaSeccion
from src.modelos import MetodoLongitud
from src.modulos.M2_material import espesor_pared
from src.modulos.M6_proteccion import EMBOCADURA_CABEZAL_CON_ALEROS
from src.modulos.M6_proteccion import EMBOCADURA_CABEZAL_RECTO
from src.constantes_normativas import C_DESLIZAMIENTO_10_6_3_4
from src.constantes_normativas import CW_NIVEL_FREATICO_T10_6_3_1_2A_2
from src.constantes_normativas import CW_PROFUNDIDAD_SIN_EFECTO_VECES_B
from src.constantes_normativas import ETA_OTROS_ESTADOS_LIMITE_AASHTO
from src.constantes_normativas import ETA_PISO_GAMMA_MAXIMO_AASHTO
from src.constantes_normativas import ETA_TECHO_GAMMA_MINIMO_AASHTO
from src.constantes_normativas import EXCENTRICIDAD_ESTATICA_FRACCION_B
from src.constantes_normativas import NUMERAL_ETA_DUCTILIDAD_AASHTO
from src.constantes_normativas import NUMERAL_ETA_REDUNDANCIA_AASHTO
from src.constantes_normativas import NUMERAL_MODIFICADOR_DE_CARGA_AASHTO
from src.constantes_normativas import FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1
from src.constantes_normativas import NUMERAL_CAPACIDAD_PORTANTE_AASHTO
from src.constantes_normativas import NUMERAL_DESLIZAMIENTO_AASHTO
from src.constantes_normativas import NUMERAL_EXCENTRICIDAD_ESTATICA_AASHTO
from src.constantes_normativas import NUMERAL_PHI_EVENTO_EXTREMO
from src.constantes_normativas import NUMERAL_PHI_MUROS
from src.constantes_normativas import NUMERAL_PHI_ZAPATAS
from src.constantes_normativas import PHI_EVENTO_EXTREMO_11_5_8
from src.constantes_normativas import PHI_MUROS_T11_5_7_1
from src.constantes_normativas import PHI_ZAPATAS_T10_5_5_2_2_1
from src.constantes_normativas import TALUD_QUEBRADO_DISTANCIA_VECES_H
from src.constantes_normativas import FS_NOMBRE_DE_LA_CONDICION
from src.constantes_normativas import NUMERAL_PHI_ESTABILIDAD_GLOBAL
from src.constantes_normativas import PHI_ESTABILIDAD_GLOBAL_11_6_3_7
from src.modelos import CARGA_DC
from src.modelos import CARGA_EH
from src.modelos import CARGA_EQ
from src.modelos import CARGA_EV
from src.modelos import CARGA_LS
from src.modelos import CARGA_WA
from src.modelos import ELEMENTO_ALEROS
from src.modelos import ELEMENTO_PANTALLA
from src.modelos import ELEMENTO_ZAPATA
from src.modelos import ELEMENTO_ZAPATA_ALEROS
from src.modelos import MURO_ALERO
from src.modelos import MURO_CABEZAL
from src.modelos import MARCO_ASD
from src.modelos import MARCO_ENVOLVENTE
from src.modelos import MARCO_LRFD
from src.modelos import MARCO_RIGE_ASD
from src.modelos import MARCO_RIGE_LRFD
from src.modelos import MOTIVO_METODO_NO_EVALUABLE_CABEZAL
from src.modelos import REGLAS_DE_MARCO
from src.modelos import CargaDeCabezal
from src.modelos import CombinacionDeEstabilidad
from src.modelos import CriterioPendienteError
from src.modelos import DatoFaltanteError
from src.modelos import EntornoDelCabezal
from src.modelos import ErrorProyecto
from src.modelos import EstabilidadDelCabezal
from src.modelos import MetodoNoEvaluableError
from src.modelos import SolicitacionDeElemento
from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace
from typing import Dict
from typing import List
from dataclasses import replace as _reemplazar
from src.constantes_fisicas import KPA_POR_MPA
from src.constantes_fisicas import N_POR_KN
from src.constantes_fisicas import PULGADA_EN_MM
from src.constantes_normativas import ALTURA_VOLADIZO_ACTIVO_M
from src.constantes_normativas import ALFA_1_BLOQUE_AASHTO
from src.constantes_normativas import ALFA_BLOQUE_E060
from src.constantes_normativas import BETA_1_BLOQUE_AASHTO
from src.constantes_normativas import BETA_1_E060
from src.constantes_normativas import BETA_1_E060_MINIMO
from src.constantes_normativas import BETA_1_MINIMO
from src.constantes_normativas import BETA_1_REDUCCION_AASHTO_SI
from src.constantes_normativas import CORTANTE_CONCRETO_SIMPLE_E060
from src.constantes_normativas import CUANTIA_MIN_CARA_TRACCION_E060
from src.constantes_normativas import CUANTIA_MIN_LOSA_E060
from src.constantes_normativas import DV_PISO_SOBRE_DE
from src.constantes_normativas import DV_PISO_SOBRE_H
from src.constantes_normativas import E060_FACTOR_CE
from src.constantes_normativas import E060_FACTOR_CM
from src.constantes_normativas import E060_FACTOR_CM_MINIMO
from src.constantes_normativas import E060_FACTOR_CV
from src.constantes_normativas import EC_11_32_ESBELTEZ
from src.constantes_normativas import EC_11_32_FACTOR
from src.constantes_normativas import EPSILON_CU_CONCRETO
from src.constantes_normativas import EPSILON_T_MIN_E060
from src.constantes_normativas import EPSILON_TL_AASHTO
from src.constantes_normativas import ESPACIAMIENTO_MAX_ABSOLUTO_AASHTO_M
from src.constantes_normativas import ESPACIAMIENTO_MAX_VECES_ESPESOR_AASHTO
from src.constantes_normativas import FACTOR_MOMENTO_REFUERZO_MINIMO_AASHTO
from src.constantes_normativas import FC_BETA_1_E060_MPA
from src.constantes_normativas import FC_DISENO_MAX_CICLOPEO_MPA
from src.constantes_normativas import FC_MAX_ALFA_1_MPA
from src.constantes_normativas import FC_MAX_BETA_1_MPA
from src.constantes_normativas import FY_ACERO_MPA
from src.constantes_normativas import FY_MAX_EPSILON_TL_MPA
from src.constantes_normativas import GAMMA_1_AGRIETAMIENTO_AASHTO
from src.constantes_normativas import GAMMA_3_AASHTO
from src.constantes_normativas import MODULO_ROTURA_AASHTO_SI
from src.constantes_normativas import NUCLEO_CENTRAL_DIVISOR
from src.constantes_normativas import PERALTE_MAX_SIMPLIFICADO_AASHTO_SI
from src.constantes_normativas import PHI_CICLOPEO_E060
from src.constantes_normativas import PHI_CORTE_E060
from src.constantes_normativas import PHI_FLEXION_E060
from src.constantes_normativas import RECUBRIMIENTO_BARRA_GRUESA_DESDE
from src.constantes_normativas import REDUCCION_PERALTE_CONTRA_SUELO_M
from src.constantes_normativas import TEMPERATURA_AS_MAX_AASHTO_SI
from src.constantes_normativas import TEMPERATURA_AS_MIN_AASHTO_SI
from src.constantes_normativas import TEMPERATURA_COEFICIENTE_AASHTO_SI
from src.constantes_normativas import TEMPERATURA_ESPESOR_GRUESO_M
from src.constantes_normativas import TEMPERATURA_S_MAX_GRUESO_M
from src.constantes_normativas import TEMPERATURA_S_PISO_M
from src.constantes_normativas import TEMPERATURA_S_VECES_ESPESOR
from src.constantes_normativas import TRACCION_CONCRETO_SIMPLE_E060
from src.constantes_normativas import VC_COEFICIENTE_AASHTO_SI
from src.constantes_normativas import VC_COEFICIENTE_E060
from src.constantes_normativas import VN_TOPE_SOBRE_FC_AASHTO
from src.constantes_normativas import ZAPATA_SIMPLIFICADO_VECES_DV
from src.constantes_normativas import GENERAL_BETA_NUMERADOR
from src.constantes_normativas import GENERAL_BETA_COEF_DEFORMACION
from src.constantes_normativas import GENERAL_BETA_NUMERADOR_SXE_IN
from src.constantes_normativas import GENERAL_BETA_SUMANDO_SXE_IN
from src.constantes_normativas import SXE_FACTOR_AGREGADO
from src.constantes_normativas import SXE_SUMANDO_AGREGADO_IN
from src.constantes_normativas import SXE_MIN_IN
from src.constantes_normativas import SXE_MAX_IN
from src.constantes_normativas import EC_COEFICIENTE_AASHTO_SI
from src.constantes_normativas import EC_EXPONENTE_AASHTO
from src.constantes_normativas import ES_REFUERZO_AASHTO_MPA
from src.constantes_normativas import EXCENTRICIDAD_MIN_MURO_CONCRETO_SIMPLE_E060
from src.constantes_normativas import FISURACION_BETA_S_FACTOR
from src.constantes_normativas import FISURACION_COEFICIENTE_AASHTO_SI
from src.constantes_normativas import FISURACION_FRACCION_FR
from src.constantes_normativas import FISURACION_FSS_MAX_SOBRE_FY
from src.constantes_normativas import FISURACION_GAMMA_E
from src.modelos import CIFRAS_FINA
from src.modelos import CLASE_EXPOSICION_1
from src.modelos import CLASE_EXPOSICION_2
from src.modelos import CLASES_DE_EXPOSICION
from src.modelos import CRITERIOS_DE_TRACCION_CICLOPEO
from src.modelos import EstadoDeVerificacion
from src.modelos import ArmadoDeSeccion
from src.modelos import ArmadoDelCabezal
from src.modelos import BarraPropuesta
from src.modelos import FilaDeArmado
from src.modelos import MARCO_E060
from src.modelos import MINIMOS_MAS_EXIGENTE
from src.modelos import MOTIVO_METODO_NO_EVALUABLE_ARMADO
from src.modelos import REGIMEN_RESISTENCIA_CEDENTE
from src.modelos import REGIMEN_RESISTENCIA_K0
from src.modelos import REGIMENES_DE_RESISTENCIA
from src.modelos import REGLAS_DE_MINIMOS
from src.modelos import SECCION_ALERO
from src.modelos import SECCION_ALERO_MITAD
from src.modelos import SECCION_TALON_ALERO
from src.modelos import SECCION_PANTALLA
from src.modelos import SECCION_PUNTA
from src.modelos import SECCION_TALON
from src.modelos import SolicitacionDeArmado
from src.modelos import TRACCION_NULA

# Reexportacion integra de todos los simbolos de M9_cabezal (en orden topologico)
from src.modulos.M9_cabezal import _criterios as _mod__criterios
from src.modulos.M9_cabezal._criterios import (
    NUMERAL_9_1,
    NUMERAL_9_2,
    NUMERAL_9_3,
    NUMERAL_MO,
    NUMERAL_PGA,
    NUMERAL_F_PGA,
    NUMERAL_SUBPRESION,
    NUMERAL_FLEXION_CORTE,
    NUMERAL_REGLA_RECUBRIMIENTO,
    NUMERAL_CORTANTE_ALTO,
    NUMERAL_CORTANTE_ALTO_VERTICAL,
    NUMERAL_CORTANTE_EN_EL_PLANO,
    NUMERAL_CORTANTE_PERPENDICULAR,
    CALCULADO,
    ETIQUETA_CALCULADO,
    DATO_SITIO_PGA,
    CRITERIO_F_PGA,
    CRITERIO_F_PGA_LECTURA,
    CRITERIO_FACTOR_MURO,
    CRITERIO_K_V,
    CRITERIO_GAMMA_EQ,
    CRITERIO_PHI_RELLENO,
    CRITERIO_I_RELLENO,
    CRITERIO_BETA_MURO,
    CRITERIO_DELTA_MURO,
    CRITERIO_BRAZO_SISMICO,
    CRITERIO_FACTORES_CARGA,
    CRITERIO_GAMMA_RELLENO,
    CRITERIO_GAMMA_CONCRETO,
    CRITERIO_GEOMETRIA,
    CRITERIO_DIMENSIONAMIENTO_ZAPATA,
    CRITERIO_TALUD_DELANTE,
    CRITERIO_PORTANTE_ADMISIBLE,
    CRITERIO_FORMA_PROFUNDIDAD,
    FORMA_CORRIDA,
    FORMA_CON_LONGITUD,
    FORMA_Y_PROFUNDIDAD,
    OPCIONES_FORMA_PROFUNDIDAD,
    CAMPOS_TALUD_DELANTE,
    CRITERIO_ESTABILIDAD_GLOBAL,
    CRITERIO_TABLA_RECUBRIMIENTO,
    CRITERIO_H_EQ_BAJO_TABLA,
    CRITERIO_H_EQ_BANDA_BORDE,
    H_EQ_BAJO_TABLA_PRIMERA_FILA,
    H_EQ_BAJO_TABLA_EXTRAPOLAR,
    H_EQ_BANDA_LEE_COLUMNA_CERO,
    H_EQ_BANDA_INTERPOLA,
    CRITERIO_CATEGORIA_REFUERZO,
    CRITERIO_SITUACION_RECUBRIMIENTO,
    CRITERIO_EXPOSICION_QUIMICA,
    CRITERIO_FACTOR_BANDA_AC,
    CLAVES_ESCALAS_SULFATOS,
    CLAVE_FILAS_TABLA_4_2,
    NOMBRE_TABLA_4_2,
    NOMBRE_TABLA_4_4,
    CATEGORIA_ACERO_SIN_RECUBRIR,
    CRITERIO_FLEXION_CORTE,
    CRITERIO_CORTANTE_ALTO,
    CRITERIO_REGIMEN_CORTANTE,
    CRITERIO_CUANTIA_VERTICAL_CORTANTE_ALTO,
    EXIGIDAS_SEC_9_3,
    COMPONENTES_COMBINACION,
    CRITERIO_TALUD_TERRAPLEN,
    CRITERIO_PERALTE_ZAPATA_ARMADA,
    CONDICION_RECUBRIMIENTO_ZAPATA,
    ORIENTACION_PARALELO_A_LA_VIA,
    EXTREMO_ENTRADA,
    EXTREMO_SALIDA,
    EXTREMOS,
    TIPO_VOLADIZO,
    TIPO_GRAVEDAD,
    _finito,
    _exigir_positivo,
    _exigir_finito,
    es_paralelo_a_la_via,
    _caracter_de,
    CRITERIO_TERRENO_DELANTE,
    CITA_ETA,
    CITAS_DE_ETA,
    TERRENO_HORIZONTAL,
    TERRENO_TALUD,
    CONDICIONES_DE_ESTABILIDAD,
    ABREVIATURA_DE_CONDICION,
    PHI_MAX_TABLA_GRADOS,
    CRITERIO_REGIMEN_RESISTENCIA,
    CRITERIO_CATALOGO_BARRAS,
    FILA_EH_EN_REPOSO,
    LADOS_DEL_TRIANGULO,
    catalogo_de_barras,
    ELEMENTOS_ARMADOS,
    FRACCION_MITAD_ALERO,
    SUFIJO_ALERO,
    FRACCION_ARRANQUE_ALERO,
    sufijo_de_la_franja,
    _rotulo_de_la_franja,
    _rotular_como_alero,
)
from src.modulos.M9_cabezal import durabilidad as _mod_durabilidad
from src.modulos.M9_cabezal.durabilidad import (
    recubrimiento_e060_mm,
    clase_exposicion_sulfatos,
    _exposicion_quimica_validada,
    _extremo_declarado,
    requisitos_durabilidad_concreto,
    factor_recubrimiento_por_ac,
    recubrimiento_aashto_mm,
    _recubrimiento_aashto_detallado,
    recubrimiento_de_diseno,
    _paso_recubrimiento,
    aviso_ambiente_corrosivo,
    CRITERIO_CUANTIA_MIN_MURO,
    DIRECCIONES_CUANTIA_MURO,
    cuantia_minima,
    nota_excepcion_refuerzo_minimo,
    _minimo_de_cuantia_aplicable,
    verificar_cuantia,
    cuantia_de_diseno,
    requiere_temperatura_dos_caras,
    requiere_refuerzo_dos_capas,
    nota_temperatura_dos_caras,
    espaciamiento_maximo,
    verificar_espaciamiento,
    verificar_ciclopeo,
    FUNCIONES_SIN_CONSUMIDOR,
    funciones_sin_consumidor,
    condicion_normativa_cabezal,
    recubrimiento_para_armar,
)
from src.modulos.M9_cabezal import empujes as _mod_empujes
from src.modulos.M9_cabezal.empujes import (
    pga_roca_b,
    clases_de_sitio_plausibles,
    _pga_en_rotulo_extremo,
    factor_sitio_desde_tabla,
    f_pga,
    lectura_columna_extrema,
    aceleracion_ajustada_sitio,
    cimentacion_en_roca,
    coeficiente_sismico_base,
    factor_muro,
    coeficiente_sismico_horizontal,
    coeficiente_sismico_vertical,
    cadena_sismica,
    ka_rankine,
    angulo_inercia_sismica,
    k_ae_mononobe_okabe,
    k_a_coulomb,
    empuje_mononobe_okabe,
    k_ae_del_proyecto,
    aplica_sobrecarga_trasdos,
    sobrecarga_trasdos_siempre_aplica,
    h_eq_sobrecarga_trasdos,
    _embocadura_paralela_del_cabezal,
    envolvente_de_h_eq_paralelo,
    h_eq_del_cabezal,
    _columna_de_borde,
    _interpolar_h_eq,
    presion_sobrecarga_trasdos,
    empuje_sobrecarga_trasdos,
    empuje_activo_estatico,
    empuje_activo_sismico_total,
    incremento_sismico,
    brazo_incremento_sismico,
    altura_agua_sobre_base,
    empuje_hidrostatico,
    subpresion,
    peso_especifico_relleno,
    peso_propio_cabezal,
    empujes_trasdos,
    peso_suelo_sobre_talon,
    fuerza_inercia_muro,
    demanda_sismica_cabezal,
)
from src.modulos.M9_cabezal import estabilidad_base as _mod_estabilidad_base
from src.modulos.M9_cabezal.estabilidad_base import (
    excentricidad_resultante,
    excentricidad_admisible_sismica,
    gamma_eq,
    presion_contacto_base,
    verificar_excentricidad_sismica,
    CARGAS_PERMANENTES,
    ELEMENTO_CABEZAL,
    FILA_GAMMA_P_DC,
    combinaciones,
    factores_de_carga,
    _gamma_permanente,
    fs_requerido,
    _verificacion_por_fs,
    verificar_capacidad_portante,
    verificar_volteo,
    verificar_deslizamiento,
    verificar_estabilidad_global,
    verificar_talud,
    parametros_resistencia_art20,
    _es_numero_finito,
    n_s_zapata_en_talud,
    n_q_zapata_en_talud,
    _interpolar_en,
    _multilineal,
    _fuera_de_la_tabla,
    coeficiente_rcbc,
    validar_talud_delante,
    DATO_TALUD_DELANTE_DEL_PUNTO,
    validar_talud_delante_del_punto,
    _terreno_delante,
    capacidad_portante_zapata_en_talud,
    verificar_estabilidad,
    factores_de_capacidad_de_carga,
)
from src.modulos.M9_cabezal import estabilidad_cargas as _mod_estabilidad_cargas
from src.modulos.M9_cabezal.estabilidad_cargas import (
    CRITERIO_MARCO,
    CRITERIO_FILA_PHI,
    CRITERIO_FILA_PHI_GLOBAL,
    CRITERIO_DRENAJE,
    CRITERIO_AGUA_SISMO,
    AGUA_SE_MUEVE_CON_EL_SUELO,
    AGUA_RELLENO_MUY_ABIERTO,
    CRITERIO_NIVEL_AGUA_SISMO,
    NIVEL_MEDIO_SUPERFICIE,
    NIVEL_MEDIO_FREATICO,
    NIVELES_MEDIOS_SIN_DRENAJE,
    CITA_NIVEL_MEDIO,
    CRITERIO_MOMENTO_TALON,
    TALON_PESO_ENTERO,
    TALON_EXACTO,
    CRITERIO_CARGA_PANTALLA,
    PANTALLA_PLANO_VIRTUAL,
    PANTALLA_CUNA,
    CRITERIO_DISTRIBUCION_INCREMENTO,
    INCREMENTO_FRACCION,
    INCREMENTO_DISTRIBUCION_ESTATICA,
    INCREMENTO_SEGUN_REGIMEN,
    _eleccion,
    CRITERIO_GAMMA_SATURADO,
    CRITERIO_FRACCION_DELTA,
    CRITERIO_REGLA_PENDIENTE,
    CRITERIO_INCLINACION_PORTANTE,
    CRITERIO_SUELO_FUNDACION,
    FILA_PHI_ZAPATAS,
    FILA_PHI_MUROS,
    FILAS_DE_PHI,
    DRENAJE_SIN,
    DRENAJE_CON,
    DRENAJES,
    REGLA_CUNA_DE_TANTEO,
    REGLA_TALUD_QUEBRADO,
    REGLA_TALUD_ENTERO,
    REGLAS_DE_PENDIENTE,
    METODO_EMPUJE_CUNA,
    METODO_EMPUJE_FORMULA,
    METODO_INCREMENTO_CUNA,
    CRITERIO_REGIMEN,
    CRITERIO_ETA_IMPORTANCIA,
    CRITERIO_ETA_DUCTILIDAD,
    CRITERIO_ETA_REDUNDANCIA,
    REGIMEN_CEDENTE,
    REGIMEN_NO_CEDENTE,
    REGIMENES_DEL_CABEZAL,
    CRITERIO_EMPUJE_SISMICO_NO_CEDE,
    NO_CEDE_REPOSO_MAS_INCREMENTO,
    NO_CEDE_MAYOR_DE_REPOSO_Y_TOTAL,
    EMPUJES_SISMICOS_NO_CEDE,
    EMPUJE_ESTATICO_ACTIVO,
    EMPUJE_ESTATICO_REPOSO,
    INCLINACION_APLICAR,
    INCLINACION_OMITIR,
    NUMERAL_9_3_LRFD,
    NUMERAL_9_3_ASD,
    CAMPOS_SUELO_OBLIGATORIOS,
    CAMPOS_SUELO_OPCIONALES,
    C_DC_PANTALLA,
    C_DC_ZAPATA,
    C_EV_TALON,
    C_EH_H,
    C_EH_V,
    C_LS_H,
    C_LS_V,
    C_WA_H,
    C_WA_U,
    C_EQ_H,
    C_EQ_V,
    C_EQ_PIR_MURO,
    C_EQ_PIR_SUELO,
    CARGAS_DE_INERCIA,
    C_EQ_KV,
    CITAS_K_V_EN_LOS_PESOS,
    CARGAS_DE_EMPUJE_ESTATICO,
    CARGAS_DE_INCREMENTO,
    _no_evaluable,
    validar_suelo_fundacion,
    suelo_de_fundacion,
    DATO_ESTABILIDAD_GLOBAL,
    CODIGOS_GLOBALES,
    CLAVE_FS_DE_CODIGO,
    CONDICIONES_GLOBALES,
    CAMPOS_TRAZA_GLOBAL,
    CAMPOS_TRAZA_GLOBAL_OPCIONALES,
    validar_estabilidad_global_declarada,
    DATO_EMPUJE_SISMICO,
    CAMPOS_EMPUJE_SISMICO,
    MAX_EMPUJES_POR_EXTREMO,
    NOTA_ARMADO_CON_EMPUJE_DECLARADO,
    CITAS_ARMADO_CON_EMPUJE_DECLARADO,
    CAMPOS_TRAZA_EMPUJE,
    METODO_INCREMENTO_DECLARADO,
    PUERTA_EMPUJE_DECLARADO,
    validar_empuje_sismico_declarado,
    _empuje_declarado_utilizable,
    _citas_del_empuje_declarado,
    _nota_del_empuje_declarado,
    _incremento_del_empuje_declarado,
    coeficientes_de_nivel_freatico,
    factores_de_forma,
    factor_de_profundidad,
    resistencia_portante_nominal,
    geometria_del_relleno,
    angulos_del_empuje,
    _sesgo,
    _regimen,
    _regla_de_marco,
    _decide,
    _area_de_la_cuna,
    empuje_de_una_cuna,
    cuna_de_tanteo,
    cargas_del_cabezal,
    _combinar,
    modificador_de_carga,
    _resistencia_i_con_eta,
    _casos_sismicos,
    combinaciones_de_estabilidad,
)
from src.modulos.M9_cabezal import geometria as _mod_geometria
from src.modulos.M9_cabezal.geometria import (
    CRITERIO_EMBOCADURA_CABEZAL,
    CRITERIO_ANGULO_ALETAS,
    CRITERIO_MARGEN_SOCAVACION,
    CRITERIO_DENTELLON,
    CRITERIO_EMBOCADURA_CAJON,
    CRITERIO_KE_CAJON,
    CRITERIO_DESPLANTE_MIN,
    CRITERIO_ESPESOR_ZAPATA_SIMPLE,
    EMBOCADURAS_DEL_CABEZAL,
    ORIENTACION_NORMAL_AL_EJE,
    CRITERIO_N_CELDAS_CAJON_EMBOCADURA,
    TIPOS_DE_CABEZAL,
    NUMERAL_9_0,
    CITA_PROFUNDIDAD_CIMENTACION,
    CITA_PERALTE_ZAPATA_ARMADA,
    CITA_ZAPATA_CONCRETO_SIMPLE,
    CITA_CICLOPEO_LIMITES,
    CITA_CONVENCION_ALEROS,
    CITA_BORDE_LIBRE_ESVIADO,
    DIMENSIONES_DECLARABLES,
    CAMPO_ANCHO_ZAPATA_ALEROS,
    CAMPO_ESPESOR_ZAPATA_ALEROS,
    CAMPO_TIPO_DECLARADO,
    CAMPO_ANGULO_ALERO_LARGO,
    ANGULOS_DECLARABLES,
    _exigir_angulo,
    _en_banda,
    embocadura_del_punto,
    _embocadura_paralela,
    factor_cara_del_muro,
    filas_hds5_del_cajon,
    _describir_embocadura,
    verificar_coherencia_embocadura_cajon,
    DATO_EMBOCADURA_CAJON_DEL_PUNTO,
    CAMPOS_EMBOCADURA_CAJON_DEL_PUNTO,
    CRITERIO_DE_CAMPO_EMBOCADURA,
    NOTA_EMBOCADURA_DECLARADA_POR_PUNTO,
    validar_embocadura_cajon_del_punto,
    extremos_del_conducto,
    _reglas,
    _desplante_minimo,
    _margen_socavacion,
    _lectura_del_margen,
    peralte_minimo_zapata,
    _dim,
    predimensionar_aleros,
    predimensionar_cabezal,
    _verificacion_cb,
    verificar_compatibilidad_cabezal,
    _registro_t7a,
    longitud_entre_cabezales,
    NOTA_FORMULA_DEL_PROYECTO,
    _pasos_del_extremo,
    _paso_embocadura,
    _motivo_sin_socavacion,
    cabezal_del_punto,
    CAMPO_ORIENTACION_DEL_PUNTO,
    CAMPO_DISTANCIA_BORDE_DEL_PUNTO,
    CAMPOS_DE_SOBRECARGA_DEL_PUNTO,
    validar_sobrecarga_del_punto,
    avisos_de_la_sobrecarga_del_punto,
    _texto_de_la_sobrecarga,
    validar_cabezal_declarado,
)
from src.modulos.M9_cabezal import estabilidad as _mod_estabilidad
from src.modulos.M9_cabezal.estabilidad import (
    factores_de_resistencia,
    _empotramiento_delante,
    _q_nominal,
    _resistencia_al_deslizamiento,
    _combo,
    _resultado_de_verificacion,
    _m,
    _verificaciones_lrfd,
    _exigir_compresion,
    _servicio_de,
    _verificaciones_asd,
    diagrama_del_suelo_sobre,
    _incremento_sobre_el_arranque,
    _diagrama_sobre_la_cara,
    empujes_sobre_la_cara_de_la_pantalla,
    empujes_sobre_el_arranque,
    solicitaciones_por_elemento,
    _solicitaciones_de_la_zapata,
    _agua_del_sismo_sin_drenaje,
    _nota_del_agua_del_sismo_sin_drenaje,
    _pasos_de_cargas,
    _eta_para_la_memoria,
    _carga,
    _tiene,
    PENDIENTES_E4_E5,
    NOMBRE_DE_LA_GLOBAL,
    CITA_ASD_DE_LA_GLOBAL,
    NUMERAL_DE_LA_GLOBAL,
    fila_phi_estabilidad_global,
    _traza_de_la_global,
    _fila_global_declarada,
    _filas_globales_declaradas,
    _paso_y_aviso_de_las_diferidas,
    ensamble_estabilidad,
    _sin_parar,
    _aviso_desembalse_rapido,
    _avisos_de_sensibilidad,
    datos_del_cabezal_del_punto,
    integrar_estabilidad,
    _carga_lineal_sobre_un_tramo,
)
from src.modulos.M9_cabezal import armado_secciones as _mod_armado_secciones
from src.modulos.M9_cabezal.armado_secciones import (
    CRITERIO_FC_CABEZAL,
    CRITERIO_ACERO_CABEZAL,
    CRITERIO_REGLA_MINIMOS,
    CRITERIO_TRACCION_CICLOPEO,
    CRITERIO_CONCRETO_CICLOPEO,
    CRITERIO_CLASE_EXPOSICION,
    CRITERIO_JUNTA_CICLOPEO,
    JUNTA_DE_CONSTRUCCION,
    JUNTA_MONOLITICA,
    JUNTAS_DEL_ARRANQUE,
    NUMERAL_9_4_ARMADO,
    NUMERAL_9_4_CICLOPEO,
    MM2_POR_M2,
    CONDICION_RECUBRIMIENTO_BARRA_GRUESA,
    CONDICION_RECUBRIMIENTO_BARRA_FINA,
    _aviso_cabezal,
    materiales_del_armado,
    regimen_de_resistencia,
    _regla_de_minimos,
    _procedimiento,
    beta_1_aashto,
    beta_1_e060,
    _exigir_seccion,
    acero_por_flexion,
    resistencia_a_flexion,
    momento_de_agrietamiento,
    cortante_del_concreto,
    fisuracion_aashto,
    clase_de_exposicion,
    _fila_de_fisuracion,
    simplificado_permitido,
    beta_procedimiento_general,
    acero_para_cortante_general,
    acero_de_temperatura_aashto,
    espaciamiento_maximo_del_armado,
    cuantia_vertical_ec_11_32,
    proponer_barra,
    _factores_por_tipo,
    cargas_en_reposo,
    _combinaciones_en_reposo,
    _combinaciones_e060,
    _clave_de,
    presion_de_contacto_lineal,
    solicitaciones_de_la_zapata,
    _talon_con_el_peso_entero,
    _pantalla_con_resultante_a_media_altura,
    _combinaciones_de_servicio,
    _momentos_de_servicio,
    solicitaciones_de_resistencia,
    _condicion_de_recubrimiento,
    minimo_e060_por_cara,
    _verificacion_de_armado,
    diseno_flexion_corte,
)
from src.modulos.M9_cabezal import armado as _mod_armado
from src.modulos.M9_cabezal.armado import (
    _altura_y_longitud,
    altura_del_fuste_del_alero,
    espesor_de_la_base_del_alero_de_gravedad,
    entorno_de_la_seccion_del_alero,
    alero_verificable_como_muro,
    fracciones_del_alero,
    franja_del_alero,
    franja_del_arranque_del_alero,
    _EntornoMinimo,
    clave_del_talon_del_alero,
    armar_elemento,
    _fila_de_reparto,
    _fila_de_peralte_de_zapata,
    _fila_de_durabilidad,
    _fila_de_durabilidad_no_aplica,
    ensamblar_armado,
    _armado_con_el_otro_regimen,
)
from src.modulos.M9_cabezal import ciclopeo as _mod_ciclopeo
from src.modulos.M9_cabezal.ciclopeo import (
    armado_del_cabezal,
    acciones_sobre_una_seccion,
    verificar_cabezal_ciclopeo,
    _verificar_zapata_ciclopea,
    _verificar_cuerpo_bajo_sismo,
    integrar_armado,
)
from src.modulos.M9_cabezal import dimensionamiento as _mod_dimensionamiento
from src.modulos.M9_cabezal.dimensionamiento import (
    DimensionadoDeZapatas,
    extremos_a_dimensionar,
    _regla_de_dimensionamiento,
    _intento,
    _estabilidades_evaluables,
    _texto_intentos,
    dimensionar_zapata_por_estabilidad,
    incorporar_dimensionado,
    DimensionadoDePeralte,
    FILAS_DEL_ARMADO_DE_LA_ZAPATA,
    CORTANTE_NO_VERIFICABLE,
    incumplidas_del_armado_de_la_zapata,
    _texto_intentos_de_peralte,
    dimensionar_peralte_por_armado,
    incorporar_peralte,
    FILAS_DEL_ARMADO_DE_LA_PANTALLA,
    _incumplidas_del_elemento,
    incumplidas_del_armado_de_la_pantalla,
    incumplidas_del_armado_del_alero,
    DimensionadoDePantalla,
    dimensionar_pantalla_por_armado,
    _dimensionar_aleros,
    rotular_estabilidad_incompleta,
    incorporar_pantalla,
)
from src.modulos.M9_cabezal import alero as _mod_alero
from src.modulos.M9_cabezal.alero import (
    DIMENSION_ZAPATA_ALEROS,
    DIMENSION_PERALTE_ZAPATA_ALEROS,
    FILAS_CICLOPEAS_SOLO_DEL_CABEZAL,
    _lecturas_de_la_forma,
    _portante_de_menor_resistencia,
    estabilidad_del_alero,
    _estabilidad_evaluable_del_alero,
    entorno_con_zapata_de_alero,
    paso_de_las_franjas_del_alero,
    DimensionadoDeZapataDelAlero,
    dimensionar_zapata_del_alero,
    incumplidas_del_armado_de_la_zapata_del_alero,
    DimensionadoDePeralteDelAlero,
    dimensionar_peralte_del_alero,
    verificacion_ciclopea_del_alero,
    con_zapata_del_alero,
    integrar_estabilidad_de_aleros,
)

_SUBMODULOS_M9 = (
    _mod__criterios,
    _mod_durabilidad,
    _mod_empujes,
    _mod_estabilidad_base,
    _mod_estabilidad_cargas,
    _mod_geometria,
    _mod_estabilidad,
    _mod_armado_secciones,
    _mod_armado,
    _mod_ciclopeo,
    _mod_dimensionamiento,
    _mod_alero,
)
_NOMBRES_SUBMODULOS = frozenset(('_criterios', 'durabilidad', 'empujes', 'estabilidad_base', 'estabilidad_cargas', 'geometria', 'estabilidad', 'armado_secciones', 'armado', 'ciclopeo', 'dimensionamiento', 'alero'))


class _PaqueteM9(_types.ModuleType):
    """Propaga reasignaciones de monkeypatch sobre `M9_cabezal` a sus submodulos."""

    def __setattr__(self, nombre: str, valor) -> None:
        super().__setattr__(nombre, valor)
        if nombre.startswith('_mod_') or nombre in _NOMBRES_SUBMODULOS:
            return
        for submod in _SUBMODULOS_M9:
            if nombre in submod.__dict__:
                setattr(submod, nombre, valor)

    def __delattr__(self, nombre: str) -> None:
        super().__delattr__(nombre)
        for submod in _SUBMODULOS_M9:
            if nombre in submod.__dict__:
                delattr(submod, nombre)


_sys.modules[__name__].__class__ = _PaqueteM9
