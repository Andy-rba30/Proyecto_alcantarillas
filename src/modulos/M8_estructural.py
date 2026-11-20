"""
M8_estructural.py
==================
Fase 8 de la hoja de ruta: verificacion estructural del conducto, sin
catalogo de proveedor -- la seleccion se hace contra las NORMAS DE PRODUCTO
(AASHTO M 170M-04 clases I-V para concreto, ASTM A796/A796M para el calibre
por altura de cobertura del TMC, AASHTO M 294-11 para HDPE -- que no
clasifica por altura: su num. 1.4 remite el diseño estructural a AASHTO LRFD
Sec. 12, verificado en N2 sobre su traduccion no oficial --), coherente con
la neutralidad comercial de Sec. 3.2.

LA NORMA DEL TMC NO ES ASTM A-807 (NOR-PRO-04). Este modulo la citaba tres
veces y esa designacion no aparece ni una vez en M 170M, M 36 ni A760. La que
lleva el diseno estructural es ASTM A796/A796M, citada siete veces por A760 y
en la lista de normas de M 36; A798/A798M es la de instalacion, Y TAMBIEN
A807/A807M: desde N1 A796-13 esta en normas/ y su num. 22.1 manda que la
instalacion se ajuste a «Practice A798/A798M or A807/A807M» (cita
ASTM_A796.22.1) -- que es para lo que las Subsecciones 507.05/.06/.08 del
EG-2013 la invocan --. Y LEIDA ENTERA, A796 NO TABULA EL CALIBRE POR ALTURA
DE COBERTURA: el espesor es la SALIDA de su procedimiento (num. 7 a 10) y se
elige de sus Tablas 2 a 35 (num. 8.1.1.2); la cobertura minima sale de su
num. 11.1 (ecs. 13 a 16, con pisos de 300 y 600 mm). Las tablas de «calibre
por altura» de la practica norteamericana son derivadas de ese procedimiento
por fabricantes y no estan en la norma (afirmacion negativa
SIN_TABLA_CALIBRE_POR_COBERTURA_A796 en el registro).

Los cinco puntos de Fase 8, y lo que hace este modulo con cada uno:

    1-2  Seleccionar clase/calibre segun la altura real de relleno y
         verificar que esa altura cae en su rango admisible.
         DESDE T-5 SE CALCULA (INF-3.3.5), con el ítem 5: ver el bloque
         «--- T-5 ---» al final del modulo. La clase del concreto sale del
         metodo indirecto de AASHTO LRFD 12.10.4.3 contra la D-load de la
         clase (de M 170M solo la Clase II es legible: 'clases_producto_por_
         relleno'); el calibre del TMC, de AASHTO LRFD 12.7.2 con la
         progresion de plancha; el perfil del HDPE, de 12.12 con el perfil
         minimo de la Tabla A12-11. El «rango admisible» es el RELLENO
         MAXIMO de lo elegido, que cada resultado imprime.
         `verificaciones_estructurales()` (Fase 5, codigos F8.*) y
         `seleccionar_clase_calibre()` (etapa de la Fase 8).

    3    Flotacion (V7), «obligatoria con NF a 1.4 m» en la letra de la
         hoja de ruta. LA OBLIGACION NO SALE DE ESE NF (VE-2, c1): el NF ya
         no es un valor unico de proyecto sino la columna 'NF_profundidad_m'
         de cada cruce, y lo que obliga a verificar la flotacion es AASHTO
         LRFD 12.6.1 y 12.6.2.3 con la subpresion del Manual de Puentes
         2.4.3.8.2; ver «Por que U asume sumersion completa». La hoja de
         ruta lo dice asi desde su correccion del 2026-11-18 (el nivel de
         agua de diseño es el criterio [A] 'nivel_agua_diseno_v7'; fichas
         VE2-C y VE2-01).
         `empuje_flotacion_kn_m()`, `peso_relleno_kn_m()` y
         `factores_carga_flotacion()` -- SI implementadas: son las piezas
         del EQUILIBRIO DE FACTORES DE CARGA LRFD que
         modulos.M5_verificaciones.v7_flotacion ensambla,

             gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U

         El empuje U YA NO es siempre calculable: se calcula sobre el
         diametro EXTERIOR (num. 2.4.3.8.2 -- volumen desplazado, MAT-D3) y
         por eso se detiene en 'espesor_pared_conducto'. El peso del relleno
         se detiene ademas en 'peso_especifico_relleno_kn_m3'. Los factores
         gamma son [N] y estan en constantes_normativas (las dos tablas del
         num. 2.4.5.3.1, fila 'Resistencia I'); de 'factores_carga_aashto'
         ([A]) sale solo QUE FILA de gamma_p describe al conducto de cada
         material: ninguno de los dos se detiene.

    4    Cama de apoyo y relleno lateral segun EG-2013 (8.1).
         `cama_apoyo_relleno_lateral()` -- SI implementada: la tabla 8.1
         esta transcrita completa, con numeral, en
         constantes_normativas.CAMA_RELLENO_LATERAL. Es informacion para la
         memoria y los planos (Sec. 11, entregable 7), no una verificacion
         con umbral: el CSV no trae una columna de compactacion realmente
         lograda contra la que comparar.

    5    Rigidez de anillo, pandeo y resistencia de costura por AASHTO LRFD
         Sec. 12 (que el Manual de Puentes NO incorpora), o clase D-load
         con factor de cama.
         DESDE T-5 SE CALCULA, contra la letra de la v8 («Diferir al
         expediente», que su nota «Corregido (INF-3.3.5, T-5)» enmienda):
         sin el, una corrida de perfil aceptaba tubos que no existen (ficha
         T4-08). `verificacion_diferida_estructural()` devuelve hoy solo lo
         que sigue sin verificarse, con su razon (el diseño del portico del
         marco, la flexion combinada del HDPE, las clases ilegibles de
         M 170M, la costura empernada...).

Por que V7 ya no usa un factor de seguridad global
----------------------------------------------------
La version anterior evaluaba ΣW >= FS*U con un FS clasico leido del criterio
'FS_flotacion'. Estaba mal encuadrada: Sec. 0.2 adopta la Via 1 -- AASHTO
LRFD de extremo a extremo -- y un FS global es de estados limite ADMISIBLES,
el marco contrario. Mezclar los dos es la misma incoherencia carga-resistencia
que Sec. 0.2 declara resuelta, solo que en el otro sentido: alli era no
combinar demandas AASHTO con resistencias E.060; aqui es no verificar una
demanda LRFD con un FS de tension admisible.

La forma correcta en LRFD es un equilibrio de factores de carga: se MINORAN
las cargas que estabilizan (peso propio DC y peso del relleno EV, con sus
gamma MINIMOS de la Tabla 2.4.5.3.1-2) y se MAYORA la que desestabiliza (la
subpresion, carga de agua WA, con su gamma de la Tabla 2.4.5.3.1-1),

    gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U

que para un conducto enterrado es la forma 0.90*(DC + EV) >= 1.00*U. Los
gamma NO estan escritos en este modulo: son [N] y viven en
constantes_normativas, y de que FILA de gamma_p cuelga cada estructura lo
declara 'factores_carga_aashto', el mismo criterio del que come M9
(Sec. 9.2). Que las dos fases lean las mismas tablas y la misma declaracion
es justamente lo que impide que el expediente tenga dos juegos de factores de
carga distintos -- y que las lean POR ESTRUCTURA es lo que impide lo
contrario, que el conducto herede el factor del muro o al reves: la Tabla
2.4.5.3.1-2 da 0.90 de minimo a la estructura enterrada y 1.00 al muro de
retencion, y durante un tiempo el proyecto uso un unico par que no era
ninguna de las dos filas (MAT-D8, NOR-PUE-03).

Consecuencia de taxonomia: 'FS_flotacion' se RETIRO de criterios_adoptados.py.
No se le redefinio el contenido porque en LRFD no queda nada que represente:
el papel que hacia -- el margen entre estabilizante y desestabilizante -- lo
hacen ahora los propios gamma, y dejarlo declarado invitaria a multiplicar dos
veces el mismo margen.

El peso propio del conducto en V7 (DC): el del concreto entra, el de los demas no
-------------------------------------------------------------------------------
--- VE-3.11 (H4 de los ensayos de diseño del conducto) --- DESDE VE-3.11 EL
TUBO Y EL MARCO DE CONCRETO SUMAN SU PESO PROPIO, como escribe la fila V7 de la
hoja de ruta: «γ_DC,min · DC + γ_EV,min · EV ≥ γ_WA · U … la forma 0.90·(DC +
EV) ≥ 1.00·U». DC = γ_c · (area exterior − area interior), con γ_c el de
'peso_especifico_concreto_kn_m3' ([C], AASHTO LRFD Tabla 3.5.1-1, el mismo que
pesa el cabezal) y el espesor de 'espesor_pared_conducto'
(`peso_propio_conducto_kn_m`). Hasta VE-3.11 DC era cero porque «la densidad no
la declara nadie»; esa razon dejo de ser cierta cuando el cabezal declaro el
peso del concreto, y el revisor de los ensayos midio la consecuencia: omitir DC
penaliza al material PESADO (mas pared, mas U sin contar su peso) y empujaba al
liviano, el que si puede flotar --MT08: el concreto Ø 2.10 m fallaba V7 por
0.34 kN/m y el punto se iba a un TMC--. El TMC y el HDPE SIGUEN CON DC = 0: el
peso del producto (calibre, perfil del fabricante) no es un dato declarado del
proyecto, y omitirlo esta del lado seguro. Lo que sigue explica por que la
omision era defendible, y vale hoy para esos dos.
LO QUE LA NORMA ADMITIRIA, dicho para que DC = 0 se lea como lo que es (VE-2,
c1): el num. 2.4.5.3.1 del Manual de Puentes (pag. impresa 142) manda
investigar el factor MINIMO de la carga permanente que aumenta la estabilidad,
y la Tabla 2.4.5.3.1-2 (pag. impresa 143) le da a «DC: Componentes y
Auxiliares» un minimo de 0.90; el lado estabilizante podria llevar 0.90·DC.
Omitirlo esta del lado seguro frente a esa suma, y es ademas la forma que el
comentario C12.6.2.3 de AASHTO describe: «the dead load on the crown of the
structure should exceed the buoyancy of the culvert» -- el peso SOBRE la
clave contra el empuje, sin el peso propio --, que es comentario y dice
`should`, de modo que sostiene la forma y no la exigencia.
ESTE PARRAFO DECIA que el espesor estaba «hoy sin valor», que ademas se
contradecia con el «ya esta declarado» de la misma linea. El que falta es el
otro. Omitirlo es la alternativa conservadora, NO una
aproximacion optimista: reduce el lado estabilizante y hace el chequeo MAS
dificil de cumplir, nunca lo relaja. Es lo contrario de lo que pasaba con U,
donde usar el diametro interior tambien "aproximaba" y lo hacia del lado
INSEGURO (MAT-D3): una omision es conservadora o no segun de que lado del
equilibrio caiga, y hay que decir de cual. Que su gamma sea el MINIMO (0.90, no
1.25) va en la misma direccion y por la misma razon: en flotacion el peso
propio ayuda, y en LRFD lo que ayuda se minora. Se declara aqui, en cada
resultado y en la memoria, en vez de aproximar en silencio. Ese 0.90 es el
minimo de la fila "DC: Componentes y Auxiliares" de la Tabla 2.4.5.3.1-2, la
unica fila de DC que Sec. 9.2 puede usar: la otra, "DC: Resistencia IV
Solamente", es de una combinacion que Sec. 9.2 no nombra.

Por que U asume sumersion completa
-------------------------------------
La fila V7 de la Fase 5 fija la hipotesis de calculo: "tuberia vacia, NF en
su cota mas alta". CUAL ES ESA COTA NO LA FIJA LA NORMA (VE-2, c1), y la
hoja de ruta lo dice en esa fila desde su correccion del 2026-11-18: es la
hipotesis del valor de archivo `en_la_clave` del criterio [A]
'nivel_agua_diseno_v7'. El Manual de Puentes, num. 2.4.3.8.1
(pag. impresa 113): «Los niveles de agua de diseño para los diferentes estados
límites serán los especificados y/o aprobados por el Propietario» (AASHTO LRFD
3.7.1, pag. 3-45, igual); la subpresion del num. 2.4.3.8.2, en la misma
pagina, actua sobre lo que esta «debajo del nivel de agua de diseño»; y AASHTO
12.6.2.3 manda considerar el levantamiento «below the highest anticipated
groundwater level» sin dar su cota. Sumergir el conducto entero --el nivel de
agua de diseño en la clave-- es por eso una ADOPCION [A] del proyecto en el
sitio de la decision del Propietario, y es la conservadora: sumergido entero
el conducto desplaza todo su volumen, y ningun nivel mas bajo daria mas
empuje. Nunca subestima el empuje.

HASTA VE-2 ESTE APARTADO SE APOYABA EN EL SITIO: «con el NF somero de la llanura
del Bajo Piura», un argumento que la norma no usa y que no es portable a otra
obra (en un cruce con el freatico a 10 m, V7 descarta igual). Se reemplazo; la
falta de una columna de invert real en el CSV (Sec. 1.2, la misma limitacion
de `M5_verificaciones.cota_de_entrada`) sigue siendo cierta, y es una razon
mas para no construir una sumersion parcial contra una cota supuesta.

Por eso, CON EL VALOR DE ARCHIVO, U NO depende del valor del NF: la hipotesis
es sumersion completa, y sumergido del todo el conducto desplaza su volumen
entero este el freatico a 1.4 m o a 0.8 m. El NF de cada cruce llega hoy por
la columna 'NF_profundidad_m' del CSV (dato de sitio [S] que se mide punto a
punto, ya no un criterio unico de proyecto), y lo que si lo usa es la
subpresion del cabezal en M9. Que U no lo lea es la razon de que V7 siga
siendo calculable en un punto cuyo NF todavia no ha medido el estudio
geotecnico.

DESDE VE-2 (c2) EL NIVEL SE PUEDE DECLARAR, porque la eleccion es del
Propietario y no del programa: 'nivel_agua_diseno_v7' [A] vale «en_la_clave»
en el archivo -- lo de este apartado, sin cambiar un bit -- y admite
«nf_del_punto», que lee la columna del cruce y le suma el ascenso estacional
'margen_estacional_nf_v7_m' [A] (sin valor: una lectura de campo no es el
freatico mas alto previsto de 12.6.2.3). Con esa alternativa V7 se evalua
solo si el fondo exterior queda bajo el nivel (12.6.1; si no, «no aplica»),
U es la del area exterior bajo el nivel (`empuje_flotacion_bajo_el_nivel_kn_m`)
y el relleno bajo el agua pesa sumergido (`peso_relleno_bajo_el_nivel_kn_m`).
Ver `cota_nivel_agua_v7_del_nf` y la ficha VE2-C.

Excepciones
-----------
    CriterioPendienteError   los criterios de la Fase 8 si se vacian (T-5);
                             'espesor_pared_conducto' (el D exterior de U y
                             de EV, via Seccion.ancho_exterior);
                             'peso_especifico_relleno_kn_m3' (V7, via
                             modulos.M5_verificaciones.v7_flotacion).
                             'factores_carga_aashto' ya no esta vacio ([A]:
                             la eleccion de fila de gamma_p por estructura).
                             (VE-2) Con 'nivel_agua_diseno_v7' =
                             «nf_del_punto»: 'margen_estacional_nf_v7_m', y
                             con el nivel sobre la clave
                             'peso_especifico_saturado_relleno_kn_m3'.
    DatoInvalidoError        la eleccion de 'factores_carga_aashto' no cubre
                             el material del punto, nombra una fila que no
                             esta en la Tabla 2.4.5.3.1-2, o nombra una cuyo
                             extremo la fuente declara N/A; un paquete
                             estructural negativo (rasante bajo subrasante).
                             (VE-2) Un margen estacional negativo, o un peso
                             saturado que no supera al del agua.
    DatoFaltanteError        (T-5) la D-load de una clase de M 170M que el
                             ejemplar no deja leer; la resistencia de una
                             costura empernada; el perfil de un HDPE que la
                             Tabla A12-11 no trae. (VE-2) Con «nf_del_punto»,
                             la columna 'NF_profundidad_m' vacia.
    MetodoNoEvaluableError   (T-5) relleno fuera del dominio de la carga viva
                             de AASHTO LRFD 3.6.1.2.6. Desde VE-4f solo lo
                             que la fuente deja sin metodo: el tubo redondo
                             con menos de 1.0 ft («more comprehensive
                             methods») y el flexible con 1.0 ft o menos que
                             cumple la cobertura minima. El marco con menos
                             de 2.0 ft y el tubo de concreto con 1.0 a 2.0 ft
                             usan la franja de 4.6.2.10.2, y el conducto
                             redondo sin la cobertura de la Tabla 12.6.6.3-1
                             INCUMPLE (F8.COBERTURA).

Uso
---
    from src.modulos.M8_estructural import (cama_apoyo_relleno_lateral,
                                        verificacion_diferida_estructural)

    cama = cama_apoyo_relleno_lateral(material)          # informativo
    diferido = verificacion_diferida_estructural()       # lo que no se verifica
    r = verificar_conducto(punto=p, material=m, seccion=s,
                           altura_relleno=h)             # Fase 8 (T-5)
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Callable, List, Optional, Tuple

from src import constantes_normativas as _CN
from src import criterios_adoptados as ca
from src.constantes_fisicas import (GAMMA_AGUA_KN_M3, KPA_POR_MPA, KSI_EN_MPA,
                                    N_POR_KN, PIE_EN_METROS, PSI_EN_KPA,
                                    PULGADA_EN_MM)
from src.constantes_normativas import (CAMA_RELLENO_LATERAL,
                                   GAMMA_P_NO_APLICA,
                                   NUMERAL_TABLA_GAMMA_P,
                                   TABLA_COMBINACIONES_FILAS,
                                   TABLA_GAMMA_P_FILAS,
                                   fila_gamma_p_legible)
from src.dominios import MILIMETROS_POR_METRO
from src.modelos import (CIFRAS_FACTOR, CIFRAS_FINA, CIFRAS_MAGNITUD,
                         CamaApoyoRelleno, CargaVivaEnterrada,
                         CondicionAnalisis, DatoFaltanteError,
                         DatoInvalidoError, DemandaMarco, DisenoPortico,
                         ErrorProyecto,
                         EsfuerzoDeSeccion, GeometriaPortico,
                         SolicitacionDeArmado,
                         EstadoDeVerificacion, FactoresFlotacion,
                         FormaSeccion, LimiteNumericoError, Magnitud,
                         Material, MetodoNoEvaluableError,
                         MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL, PasoDeMemoria,
                         PuntoCritico, ReferenciaNormativa,
                         ResultadoEstructural, Seccion, SeccionCircular,
                         SeccionRectangular, TipoDeVeredicto,
                         TipoMaterial, Umbral, Verificacion, Veredicto, paso)
from src.modulos.M2_material import espesor_pared, numero_de_celdas
from src.tolerancias import (DIVISIONES_MIEMBRO_PORTICO,
                             POSICIONES_CARGA_VIVA_POR_CELDA, TOL_BRENT,
                             TOL_UMBRAL_NORMATIVO,
                             TRAMOS_BUSQUEDA_RELLENO_MAXIMO)

NUMERAL_8_1_2 = "Fase 8, items 1-2"
# La cita anterior, "Sec. 8.1 (EG-2013 Seccion 500)", era doblemente falsa:
# ni "Sec. 8.1" es del EG-2013 (es el apartado de la hoja de ruta) ni existe
# una "Seccion 500" en el EG-2013. Los conductos son SECCIONES del Capitulo V,
# una por material (505 concreto simple, 506 concreto reforzado, 507 TMC,
# 508 HDPE), y la fila concreta de cada uno la trae
# `constantes_normativas.CAMA_RELLENO_LATERAL[material]["numeral"]`, que si
# baja al numeral exacto (505.03/.07/.10/.11, pags. 950-951, etc.). Este
# constante es solo el encabezado del bloque.
NUMERAL_8_1 = ReferenciaNormativa(
    seccion_hoja_ruta="Sec. 8.1",
    numeral_norma="EG-2013, Capitulo V, Seccion de cada material "
                  "(505 / 506 / 507 / 508); rellenos generales en la "
                  "Seccion 502",
)
NUMERAL_8_5 = "Fase 8, item 5"
NUMERAL_V7 = ("Fase 5, V7 (subpresion: Manual de Puentes num. 2.4.3.8.2; "
              "factores de carga: Manual de Puentes Tablas 2.4.5.3.1-1 y "
              "2.4.5.3.1-2, pag. impresa 143)")

CRITERIO_CLASES_PRODUCTO = "clases_producto_por_relleno"
CRITERIO_FACTORES_CARGA = "factores_carga_aashto"
CRITERIO_PESO_RELLENO = "peso_especifico_relleno_kn_m3"

# Tipos de carga de las Tablas 2.4.5.3.1-1/-2 que intervienen en V7, y con
# que extremo entra cada uno. En flotacion, DC y EV ESTABILIZAN (se minoran,
# gamma minimo) y WA DESESTABILIZA (se mayora, gamma maximo). Los nombres
# viajan aqui; los NUMEROS estan en constantes_normativas ([N], las dos tablas
# del num. 2.4.5.3.1 completas) y la ELECCION de fila en
# 'factores_carga_aashto' ([A]). Este modulo no declara ni una cosa ni la otra.
CARGA_PESO_PROPIO = "DC"
CARGA_RELLENO = "EV"
CARGA_AGUA = "WA"
EXTREMO_ESTABILIZANTE = "min"
EXTREMO_DESESTABILIZANTE = "max"

# DC no se elige: la Tabla 2.4.5.3.1-2 tiene una sola fila de componentes
# (1.25/0.90) y la otra, "DC: Resistencia IV Solamente", pertenece a una
# combinacion que Sec. 9.2 no usa. Por eso la fila esta aqui y no en el
# criterio: no hay eleccion que declarar.
FILA_GAMMA_P_DC = "DC_componentes_y_auxiliares"
# La clave del marco en `factores_carga_aashto`. No es un `TipoMaterial`
# porque un marco y un tubo de concreto comparten el suyo; es la misma
# razon por la que 'cabezal' tampoco lo es.
ELEMENTO_CAJON = "cajon"
# Las filas de EV se reconocen por su prefijo de clave. Es la unica marca
# que `TABLA_GAMMA_P_FILAS` da para agruparlas sin volver a escribir sus
# nombres, que es lo que se quiere evitar.
PREFIJO_FILA_EV = "EV_"


# ---------------------------------------------------------------------------
# Items 1-2 - Seleccion de clase/calibre por norma de producto
# ---------------------------------------------------------------------------

def seleccionar_clase_calibre(*, punto: PuntoCritico, material: Material,
                              seccion: Seccion, altura_relleno: float
                              ) -> ResultadoEstructural:
    """
    Clase (concreto, AASHTO M 170M), calibre (TMC, ASTM A796 por AASHTO
    LRFD 12.7.2) o perfil (HDPE, AASHTO M 294 por AASHTO LRFD 12.12) segun
    la altura REAL de relleno del punto, con el relleno maximo de lo elegido;
    para el marco, la demanda de la losa superior. Es la etapa de la Fase 8
    que `servicio._fase_8` corre a nivel de expediente; las verificaciones
    que deciden si el escalon existe ya corrieron en la Fase 5 por
    `verificaciones_estructurales`, con la misma funcion.

    HASTA T-5 ESTA FUNCION ERA UNA MINA: leia 'clases_producto_por_relleno'
    --vacio-- y, si alguien lo declaraba, terminaba en
    `AssertionError("inalcanzable...")`, que no desciende de `ErrorProyecto`
    y tumbaba la corrida entera. T-5 escribio el cuerpo (INF-3.3.5): ver
    `verificar_conducto` y el bloque «--- T-5 ---» de este modulo. Lo que
    no se puede verificar sale como `DatoFaltanteError` (una clase de M 170M
    cuya D-load no se lee, una costura empernada sin tabla, un perfil de PE
    que la Tabla A12-11 no trae) o `MetodoNoEvaluableError` (relleno por
    debajo del dominio del metodo de la carga viva), nunca como un error de
    programa.
    """
    return verificar_conducto(punto=punto, material=material,
                              seccion=seccion, altura_relleno=altura_relleno)


# ---------------------------------------------------------------------------
# Item 3 - V7: Flotacion del conducto
# ---------------------------------------------------------------------------

def empuje_flotacion_kn_m(*, seccion: Seccion, espesor: float) -> float:
    """
    U, empuje de flotacion por metro lineal de conducto, kN/m: conducto
    totalmente sumergido, la hipotesis conservadora de "NF en su cota mas
    alta" que fija la fila V7 de la Fase 5.

        U = gamma_agua * area_exterior

    EL NIVEL EN LA CLAVE ES UNA ADOPCION, NO UNA LECTURA (VE-2, c1): el nivel
    de agua de diseño lo especifica o aprueba el Propietario (Manual de
    Puentes num. 2.4.3.8.1, pag. impresa 113; AASHTO 3.7.1), y el proyecto
    lo pone en la clave porque sumergido entero el conducto desplaza todo su
    volumen y ningun nivel mas bajo da mas empuje. Ver «Por que U asume
    sumersion completa» en el docstring del modulo.

    DE DONDE SALE LA OBLIGACION, que hasta C7 no estaba citada: el num.
    2.4.3.8.2 del Manual de Puentes manda considerar la subpresion como una
    fuerza de levantamiento sobre "todos los componentes de la estructura que
    se encuentran debajo del nivel de agua de diseno" -- ambito NEUTRO
    respecto de la forma, y por eso el marco entra directo --. AASHTO lo
    refuerza con dos exigencias propias (12.6.1 y 12.6.2.3) sobre "buried
    structures", cuyo alcance nombra el cajon (12.1 SCOPE).

    EL AREA ES LA EXTERIOR, y ese es el punto (MAT-D3): la subpresion actua
    sobre el VOLUMEN DESPLAZADO, que es el que encierra la superficie
    exterior. Con el interior, un tubo de D = 0.90 m y t = 0.100 salia un
    33 % por debajo.

    Y LA PIDE A LA SECCION EN VEZ DE CALCULARLA, que es lo que C7 cambia. La
    firma recibia `D_exterior: float` y calculaba `pi/4 * D^2`: un CILINDRO
    cableado. Un marco al que se le pasara su altura exterior se evaluaba
    como el cilindro circunscrito a esa altura, y ahi la subpresion sale un
    39 % MENOR que la real -- 24.96 kN/m contra 40.61 sobre un marco de
    2.00 x 1.50 m con t = 0.15 --, que es la direccion insegura. Ahora la
    forma la resuelve `Seccion.area_exterior` y este modulo no la conoce.

    Y ESE CAMBIO MOVIO UN NUMERO, en 1 ULP, que hay que declarar en vez de
    dejar que se lo trague la regeneracion de la linea base -- lo encontro la
    auditoria adversarial de C7 --. Antes: `GAMMA * (pi/4) * D_ext**2`, que
    Python asocia `(GAMMA*(pi/4)) * D_ext**2`. Ahora: `GAMMA *
    seccion.area_exterior(t)`, o sea `GAMMA * (pi*d**2/4)`. Medido sobre los
    cuatro D_ext que la linea base imprime, SOLO UNO cambia:

        D_ext = 1.976 m ->  30.083805296800858  antes
                            30.08380529680086   ahora   (3.6e-15 kN/m)

    NO ES RECUPERABLE reordenando dentro de `area_exterior`: escribirla como
    `(pi/4)*d**2` da el mismo resultado que la forma actual, porque la
    diferencia nace de la asociacion A TRAVES del `GAMMA *`, y plegarla dentro
    de la seccion exigiria darle a la seccion el peso especifico del agua --
    o sea devolverle a `Seccion` una responsabilidad que no es suya --.
    Se acepta y se declara. El precedente contrario es `M4_control`, que en un
    traslado equivalente si conservo la identidad al ultimo bit y lo dijo; ahi
    se pudo y aqui no, y esa es la diferencia que este parrafo existe para no
    dejar implicita.

    EL 39 % ES «MENOR QUE LA REAL» Y NO ES EL 63 % DE LA FRASE HERMANA, que
    es lo que este parrafo decia hasta que lo refuto la auditoria adversarial
    de C7. Son las DOS FORMAS de enunciar la misma diferencia, y el propio
    caso patron CP10 advierte contra confundirlas: 24.96/40.61 = 0.615, o sea
    el cilindro pide un 39 % MENOS; y 40.61/24.96 = 1.63, o sea el prisma pide
    un 63 % MAS. La cifra que iba aqui era la de la segunda forma con el
    rotulo de la primera.
    """
    return GAMMA_AGUA_KN_M3 * seccion.area_exterior(espesor)


def peso_relleno_kn_m(*, seccion: Seccion, espesor: float,
                      altura_relleno: float) -> float:
    """
    Peso del relleno sobre la clave, kN/m: prisma del ANCHO EXTERIOR de la
    seccion -- el que el conducto ocupa de verdad en planta -- por la altura
    `altura_relleno`, con el peso especifico de 'peso_especifico_relleno_kn_m3'.

    EV es "presion vertical del peso propio del suelo de relleno" (num. 2.4.5.2
    del Manual de Puentes). Que sea el relleno SOBRE la estructura y que el
    prisma tenga el ancho exterior NO lo dice la fuente: es la convencion
    declarada del proyecto, y por eso viaja como `Interpretacion` en la
    memoria y no como cita (§15.2.7 de docs/ruta_familia_c.md).

    EL ANCHO, NO EL CANTO. Es `Bc` -- "outside diameter or width", la
    dimension HORIZONTAL -- y en un marco NO coincide con `B'c`. Cambiarlos
    de sitio da un prisma con el ancho equivocado: sobre 2.00 x 1.50 m con
    t = 0.15, Bc = 2.30 y B'c = 1.80, un 28 % de diferencia en EV.

    QUE U Y EV USEN LA MISMA SECCION NO ES UN DETALLE: V7 compara
    gamma_EV*EV contra gamma_WA*U y los dos crecen con el tamano, U con las
    DOS dimensiones exteriores y EV solo con el ancho. Hasta VE-3.11, sin el
    peso propio, eso hacia que engrosar la pared EMPEORARA la flotacion;
    desde VE-3.11 el concreto suma su peso (`peso_propio_conducto_kn_m`), que
    crece con la misma area que U y con un peso especifico mayor que el del
    agua, y engrosar la pared la MEJORA. Esta escrito en la sensibilidad de
    'espesor_pared_cajon'.

    NO suma el peso propio del conducto: eso es DC, aparte
    (`peso_propio_conducto_kn_m`, VE-3.11).
    """
    gamma_relleno = ca.valor(CRITERIO_PESO_RELLENO)   # CriterioPendienteError mientras falte
    return gamma_relleno * seccion.ancho_exterior(espesor) * altura_relleno


# --- VE-3.11 (H4) --- El peso especifico del concreto, el MISMO criterio que
# pesa el cabezal (`M9.CRITERIO_GAMMA_CONCRETO`): un solo concreto en la obra.
CRITERIO_PESO_CONCRETO = "peso_especifico_concreto_kn_m3"


def peso_propio_conducto_kn_m(*, material: Material, seccion: Seccion,
                              espesor: float) -> Tuple[float, str]:
    """
    DC de V7, kN/m, y la procedencia que el paso imprime: el par (DC, texto).

    Fila V7 de la Fase 5 de la hoja de ruta: «γ_DC,min · DC + γ_EV,min · EV
    ≥ γ_WA · U». Para el CONCRETO (tubo o marco) DC = γ_c · (area exterior −
    area interior llena), con γ_c de 'peso_especifico_concreto_kn_m3' [C]
    (AASHTO LRFD Tabla 3.5.1-1) y el espesor con que V7 forma U y EV: el
    anillo -- o el marco hueco -- que de verdad pesa, por metro lineal. Las
    cartelas del marco no se cuentan, del lado seguro.

    Para el TMC y el HDPE devuelve 0: el peso del producto no es un dato
    declarado del proyecto, y omitirlo reduce el lado estabilizante (es la
    omision conservadora que hasta VE-3.11 se aplicaba tambien al concreto;
    ver el docstring del modulo).
    """
    if material.tipo is not TipoMaterial.CONCRETO_REFORZADO:
        return 0.0, ("peso propio del conducto, OMITIDO: el peso del "
                     "producto (calibre, perfil del fabricante) no es un dato "
                     "declarado del proyecto, y omitirlo reduce el lado "
                     "estabilizante, del lado conservador")
    gamma_c = ca.valor(CRITERIO_PESO_CONCRETO)
    area_pared = seccion.area_exterior(espesor) - seccion.area_llena
    return gamma_c * area_pared, (
        f"peso propio del conducto de concreto: gamma_c = {gamma_c:g} kN/m3 "
        f"('{CRITERIO_PESO_CONCRETO}', AASHTO LRFD Tabla 3.5.1-1) por el "
        f"area de la pared, A_exterior - A_interior = {area_pared:.4f} m2 "
        "(sin cartelas, del lado seguro); la fila V7 de la hoja de ruta lo "
        "suma con su gamma minimo")


# ---------------------------------------------------------------------------
# --- VE-2 (c2) --- El nivel de agua de diseño de V7, declarable
# ---------------------------------------------------------------------------
# El Manual de Puentes, num. 2.4.3.8.1, deja el nivel de agua de diseño al
# Propietario (cita MP.2.4.3.8.1#NIVEL_DE_DISENO), y hasta VE-2 este modulo lo
# fijaba sin decirlo: sumersion completa. Hoy lo dice 'nivel_agua_diseno_v7'
# [A]: «en_la_clave» (archivo) es exactamente lo de antes -- V7 no pasa por
# ninguna de las funciones de abajo salvo `regla_nivel_agua_v7`, y la linea
# base no se mueve -- y «nf_del_punto» lee el freatico del cruce.
CRITERIO_NIVEL_AGUA_V7 = "nivel_agua_diseno_v7"
NIVEL_V7_EN_LA_CLAVE = "en_la_clave"
NIVEL_V7_NF_DEL_PUNTO = "nf_del_punto"
NIVELES_AGUA_V7 = (NIVEL_V7_EN_LA_CLAVE, NIVEL_V7_NF_DEL_PUNTO)
CRITERIO_MARGEN_NF_V7 = "margen_estacional_nf_v7_m"
# El MISMO dato de ensayo que el cabezal lee para su relleno bajo el agua
# (`M9.CRITERIO_GAMMA_SATURADO`): el proyecto usa un solo relleno, y su peso
# humedo ya es uno solo ('peso_especifico_relleno_kn_m3', que leen V7 y M9).
CRITERIO_PESO_SATURADO = "peso_especifico_saturado_relleno_kn_m3"


def regla_nivel_agua_v7() -> str:
    """
    El nivel de agua de diseño con que V7 evalua la flotacion, leido de
    'nivel_agua_diseno_v7' [A] (registra el uso: la memoria lo imprime).

    Una regla que no es de la ventana no llega aqui por la puerta de los
    criterios --es una `categoria`--; la guardia de abajo es la segunda
    linea, para el que monte un `Criterio` por otra via.
    """
    regla = ca.valor(CRITERIO_NIVEL_AGUA_V7)
    if regla not in NIVELES_AGUA_V7:
        raise DatoInvalidoError(
            CRITERIO_NIVEL_AGUA_V7, valor=regla,
            motivo=f"no es una de las reglas implementadas {NIVELES_AGUA_V7}")
    return regla


def v7_lee_el_nivel_freatico() -> bool:
    """
    Si V7, con lo que hoy esta declarado, lee la columna 'NF_profundidad_m'.
    NO registra el uso del criterio: es la pregunta del pre-vuelo
    (`anticipo.datos_faltantes_por_punto`), que no corre el calculo y no
    puede ensuciar el registro de la corrida.
    """
    regla = ca.criterio_efectivo(CRITERIO_NIVEL_AGUA_V7).valor
    return regla == NIVEL_V7_NF_DEL_PUNTO


def cota_nivel_agua_v7_del_nf(*, punto: PuntoCritico
                              ) -> Tuple[float, float, float]:
    """
    El nivel de agua de diseño de V7 con «nf_del_punto», msnm, y las dos
    lecturas de las que sale: `(cota, NF_profundidad_m, margen)`.

        cota = cota_terreno - NF_profundidad_m + margen

    El NF se mide bajo el terreno natural del CRUCE (la misma lectura que la
    Fase 9 hace en `M9.altura_agua_sobre_base`). Es una LECTURA DE CAMPO y
    no necesariamente el freatico mas alto previsto que AASHTO 12.6.2.3
    nombra, y por eso se le suma 'margen_estacional_nf_v7_m' [A]: sin valor,
    `CriterioPendienteError`; nunca 0 por defecto, que seria afirmar sin
    dato que la lectura ya es el nivel mas alto.

    Se detiene, en este orden: `DatoFaltanteError` sin 'NF_profundidad_m'
    (la columna admite la celda vacia: la debe el EMS);
    `CriterioPendienteError` sin el margen; `DatoInvalidoError` con un margen
    negativo, que bajaria el nivel por debajo de la lectura (la ventana del
    criterio es simbolica y no lo evalua).
    """
    nf = punto.exigir("NF_profundidad_m")
    margen = ca.valor(CRITERIO_MARGEN_NF_V7)
    if not margen >= 0:
        raise DatoInvalidoError(
            CRITERIO_MARGEN_NF_V7, valor=margen, id_punto=punto.id,
            motivo="el ascenso estacional del freatico no puede ser negativo: "
                   "bajaria el nivel de agua de diseño por debajo de la "
                   "lectura de NF_profundidad_m")
    return punto.cota_terreno - nf + margen, nf, margen


def empuje_flotacion_bajo_el_nivel_kn_m(*, seccion: Seccion, espesor: float,
                                        altura_agua: float) -> float:
    """
    U con el nivel de agua de diseño a `altura_agua` m sobre el fondo
    EXTERIOR del conducto, kN/m: la sumatoria de las componentes verticales
    de la presion hidrostatica sobre lo que queda bajo el nivel (Manual de
    Puentes 2.4.3.8.2), o sea gamma_agua por el AREA EXTERIOR SUMERGIDA.

    Con el nivel en el canto exterior o por encima es `empuje_flotacion_kn_m`
    -- el mismo numero, por la misma funcion --; por debajo, el area de la
    MISMA forma con las dimensiones exteriores bajo esa altura: un segmento
    de circulo (Sec. 4.1, A = (D^2/8)(theta - sen theta), sobre el diametro
    exterior) o un rectangulo (Bc * h). La geometria no se reescribe: es la
    de `SeccionCircular.area` y `SeccionRectangular.area`, que son las de la
    lamina libre, construidas sobre el contorno exterior.
    """
    canto = seccion.canto_exterior(espesor)
    if not altura_agua < canto:
        return empuje_flotacion_kn_m(seccion=seccion, espesor=espesor)
    if not altura_agua > 0:
        return 0.0
    if isinstance(seccion, SeccionRectangular):
        exterior = SeccionRectangular(B=seccion.ancho_exterior(espesor),
                                      H=canto)
    elif isinstance(seccion, SeccionCircular):
        exterior = SeccionCircular(D=seccion.ancho_exterior(espesor))
    else:
        raise TypeError(f"forma de seccion no implementada: {seccion!r}")
    return GAMMA_AGUA_KN_M3 * exterior.area(altura_agua)


def peso_relleno_bajo_el_nivel_kn_m(*, seccion: Seccion, espesor: float,
                                    altura_relleno: float,
                                    altura_sumergida: float
                                    ) -> Tuple[float, Optional[float]]:
    """
    EV con `altura_sumergida` m del relleno sobre la clave bajo el nivel de
    agua de diseño, kN/m, y el peso saturado con que se peso (None si no
    hizo falta):

        EV = Bc * [ gamma_r * (H - h_s) + (gamma_sat - gamma_agua) * h_s ]

    con h_s acotada por la altura de relleno H (sobre la subrasante el
    paquete no entra en EV, como siempre). El relleno bajo el agua pesa
    SUMERGIDO por ANALOGIA [N->] con el Manual de Puentes 2.4.4.1.3, que
    exige las densidades del suelo sumergido para el empuje LATERAL bajo el
    freatico (cita MP.2.4.4.1.3#SUMERGIDO): para el peso vertical que
    estabiliza el conducto no hay frase, y la analogia va del lado
    conservador (sujeta menos).

    El saturado es 'peso_especifico_saturado_relleno_kn_m3', dato de ensayo
    sin valor de archivo: solo se lee si hay relleno bajo el agua (mas que
    `TOL_UMBRAL_NORMATIVO`, para que el ruido flotante de un nivel en la
    clave no lo exija) y sin el, `CriterioPendienteError`. Un saturado que
    no supera al agua daria un peso sumergido nulo o negativo:
    `DatoInvalidoError`, como en el cabezal.
    """
    if not altura_sumergida > TOL_UMBRAL_NORMATIVO:
        return peso_relleno_kn_m(seccion=seccion, espesor=espesor,
                                 altura_relleno=altura_relleno), None
    h_s = min(altura_sumergida, altura_relleno)
    gamma_relleno = ca.valor(CRITERIO_PESO_RELLENO)
    gamma_sat = ca.valor(CRITERIO_PESO_SATURADO)   # CriterioPendienteError
    if not (math.isfinite(gamma_sat) and gamma_sat > GAMMA_AGUA_KN_M3):
        raise DatoInvalidoError(
            CRITERIO_PESO_SATURADO, valor=gamma_sat,
            motivo="tiene que ser mayor que el peso especifico del agua: "
                   "el relleno bajo el nivel pesa el saturado menos el agua")
    ancho = seccion.ancho_exterior(espesor)
    return (ancho * (gamma_relleno * (altura_relleno - h_s)
                     + (gamma_sat - GAMMA_AGUA_KN_M3) * h_s), gamma_sat)


COMBINACION_V7 = "Resistencia I"
# V7 es un equilibrio de factores de carga LRFD -- MINORA lo que estabiliza
# (DC, EV) y MAYORA lo que desestabiliza (WA) -- y esos son exactamente los
# extremos que trae Resistencia I (Strength I) en las Tablas 2.4.5.3.1-1/-2;
# las otras dos combinaciones (Servicio I, Evento Extremo I) colapsan las
# cargas permanentes y WA a 1.00 y no aportarian el margen que V7 exige. Se
# fija aqui, no en constantes_normativas: la tabla trae las tres combinaciones
# (Sec. 9.2 de M9 las necesita todas), y cual de las tres usa V7 es una
# decision de este modulo, no del dato.
#
# ESTE COMENTARIO SE PERDIO EN C7d Y LO ENCONTRO LA AUDITORIA ADVERSARIAL DE
# C7, que lo dice mejor que yo: la sesion que escribe «un defecto declarado
# que desaparece del docstring sin decir como se cerro es indistinguible de
# uno que se borro» borro una justificacion entera sin decirlo. No fue una
# decision: fue un reemplazo de bloque que se llevo por delante el comentario
# y dejo la constante. El `NameError` que produjo hizo restaurar la constante
# y nadie miro que faltaba lo de debajo. Se restaura literal, del arbol de
# `cd8d4f2~1`, con esta nota encima para que la perdida quede contada.


def factores_carga_flotacion(*, material: Material) -> FactoresFlotacion:
    """
    Los tres gamma que V7 necesita para EL CONDUCTO DE ESTE MATERIAL: el
    MINIMO de DC y el de EV, que son las cargas estabilizantes, y el de WA,
    que es la desestabilizante.

    De donde sale cada uno, que ya no es de un solo sitio:

      * gamma_DC y gamma_EV son de la Tabla 2.4.5.3.1-2 (gamma_p), [N],
        transcrita completa en `constantes_normativas.TABLA_GAMMA_P_FILAS`.
      * gamma_WA es de la fila "Resistencia I" de la Tabla 2.4.5.3.1-1, [N],
        en `TABLA_COMBINACIONES_FILAS`.
      * QUE FILA de gamma_p describe a este conducto lo declara
        'factores_carga_aashto' ([A]), indexado por material.

    POR QUE ESTA FUNCION RECIBE EL MATERIAL (MAT-D8, NOR-PUE-03). Antes leia
    un par unico de EV, {max 1.35, min 0.90}, que no es ninguna fila de la
    tabla: mezclaba el maximo de "Muros y estribos de retencion" con el
    minimo de "Estructura rigida enterrada". La tabla desglosa EV por TIPO DE
    ESTRUCTURA, y un conducto enterrado no es un muro: el tubo de concreto
    cuelga de "Estructura rigida enterrada" (1.30/0.90), el HDPE de
    "Alcantarillas termoplasticas" (1.30/0.90) y el TMC de la subfila
    flexible "Entre otros" (1.95/0.90). Los tres minimos valen 0.90, de modo
    que el numero que V7 usa hoy no cambia; lo que cambia es que ya no se
    puede leer sin decir de que fila sale, que es lo que dejaba a un
    consumidor futuro heredar el extremo de otra estructura.

    Se detiene con `CriterioPendienteError` si la eleccion no esta declarada,
    y con `DatoInvalidoError` si lo declarado no cubre a este material o
    nombra una fila que no es de la tabla.
    """
    eleccion = ca.valor(CRITERIO_FACTORES_CARGA)
    fila_EV = _fila_elegida(eleccion, _elemento_de(material), CARGA_RELLENO)
    return FactoresFlotacion(
        gamma_DC=_gamma_p(FILA_GAMMA_P_DC, EXTREMO_ESTABILIZANTE),
        gamma_EV=_gamma_p(fila_EV, EXTREMO_ESTABILIZANTE),
        gamma_WA=_gamma_de_la_combinacion(CARGA_AGUA, EXTREMO_DESESTABILIZANTE),
        criterio=CRITERIO_FACTORES_CARGA,
        fila_gamma_EV=fila_gamma_p_legible(fila_EV),
    )


def filas_ev_de_la_tabla() -> Tuple[str, ...]:
    """
    Las filas de EV de la Tabla 2.4.5.3.1-2, legibles, LEIDAS DE LA
    TRANSCRIPCION.

    Existe para que la memoria pueda decir «entre estas» sin copiar la lista a
    mano. La copia a mano era el defecto D-8: la `EleccionDeProyecto` de V7
    enumeraba CUATRO filas escritas a pulso y la tabla tiene SIETE -- faltaba
    «Porticos rigidos», que es justamente la del cajon, de modo que la memoria
    presentaba una eleccion sin listar la opcion que se estaba eligiendo --.
    Derivandola, no puede volver a divergir.
    """
    return tuple(fila_gamma_p_legible(clave)
                 for clave in TABLA_GAMMA_P_FILAS
                 if clave.startswith(PREFIJO_FILA_EV))


def _elemento_de(material: Material) -> str:
    """
    Con que clave de 'factores_carga_aashto' se busca la fila de este
    conducto.

    NO ES `material.tipo.value`, Y ESE ERA EL DEFECTO. Un marco de concreto y
    un tubo de concreto son el MISMO `TipoMaterial`, de modo que indexar por
    material no puede distinguirlos: el marco recibia la fila del tubo --
    «Estructura rigida enterrada» -- en vez de la suya. Quien los separa es la
    FORMA, que es lo que la Tabla 2.4.5.3.1-2 desglosa (por tipo de
    ESTRUCTURA, no de material). La clave 'cajon' la dejo puesta C5 esperando
    a este consumidor.

    EL NUMERO NO CAMBIA Y LA CITA SI, que es lo que lo hacia peligroso: el
    MINIMO de las dos filas vale 0.90 y V7 lee el minimo, de modo que nada
    fallaba de forma ruidosa mientras la fila impresa era la equivocada. Es el
    precedente NOR-HID-01 -- valor que acierta por casualidad, cita falsa --.
    Lo que si cambia es el maximo, 1.35 frente a 1.30, y ese gobierna la Fase
    8, que `--alcance perfil` difiere.
    """
    if material.forma is FormaSeccion.RECTANGULAR:
        return ELEMENTO_CAJON
    return material.tipo.value


def _fila_elegida(eleccion, elemento: str, tipo_de_carga: str) -> str:
    """
    La fila de gamma_p que el criterio declara para un elemento estructural,
    con el error del EXPEDIENTE cuando la declaracion no lo cubre o nombra
    una fila que la Tabla 2.4.5.3.1-2 no tiene. Es `DatoInvalidoError` y no
    `KeyError` porque el problema esta en lo que el revisor escribio en
    'factores_carga_aashto', no en el programa.
    """
    del_elemento = eleccion.get(elemento) if hasattr(eleccion, "get") else None
    fila = (del_elemento.get(tipo_de_carga)
            if hasattr(del_elemento, "get") else None)
    if not isinstance(fila, str):
        raise DatoInvalidoError(
            campo=CRITERIO_FACTORES_CARGA, valor=eleccion,
            motivo=f"V7 necesita saber que fila de gamma_p describe al "
                   f"elemento '{elemento}' para la carga '{tipo_de_carga}', y "
                   "la declaracion no lo dice. Se espera un dict "
                   "{'<elemento>': {'EV': '<clave de "
                   "TABLA_GAMMA_P_FILAS>'}}",
        )
    if fila not in TABLA_GAMMA_P_FILAS:
        raise DatoInvalidoError(
            campo=CRITERIO_FACTORES_CARGA, valor=fila,
            motivo=f"el elemento '{elemento}' se declara en la fila "
                   f"'{fila}', que no es una fila de {NUMERAL_TABLA_GAMMA_P}",
        )
    return fila


def _gamma_p(fila: str, extremo: str) -> float:
    """
    Un extremo de una fila de la Tabla 2.4.5.3.1-2, [N].

    El N/A de la tabla NO es un cero ni una omision: hay filas -- "Estabilidad
    global" y "AEP Para paredes ancladas" -- en las que la fuente declara que
    ese extremo no existe. Pedirlo es un error del expediente y se dice asi,
    en vez de dejar pasar un None que mas abajo seria un TypeError o, peor,
    un numero inventado (MAT-D15, NOR-AAS-04).
    """
    valor_gamma = TABLA_GAMMA_P_FILAS[fila][extremo]
    if valor_gamma is GAMMA_P_NO_APLICA:
        raise DatoInvalidoError(
            campo=CRITERIO_FACTORES_CARGA, valor=fila,
            motivo=f"la fila '{fila}' de {NUMERAL_TABLA_GAMMA_P} declara N/A "
                   f"en su extremo '{extremo}': la fuente dice que esa fila "
                   "no tiene ese factor, de modo que no hay gamma que aplicar",
        )
    return float(valor_gamma)


def _gamma_de_la_combinacion(tipo_de_carga: str, extremo: str) -> float:
    """
    Un gamma de la fila 'Resistencia I' de la Tabla 2.4.5.3.1-1, [N]. Es el
    camino de las cargas que NO son permanentes -- aqui WA --, que no cuelgan
    de la tabla de gamma_p y por lo tanto no tienen fila que elegir.

    No lleva guardia de dato del expediente, a diferencia de la eleccion: esa
    tabla es [N] y esta transcrita completa: si le faltara la carga WA no
    seria un error del revisor sino de la transcripcion, o sea del programa,
    y un KeyError es la senal honesta de eso.
    """
    return float(TABLA_COMBINACIONES_FILAS[COMBINACION_V7][tipo_de_carga][extremo])


# ---------------------------------------------------------------------------
# Item 4 - Cama de apoyo y relleno lateral (EG-2013 Sec. 500, num. 8.1)
# ---------------------------------------------------------------------------

def cama_apoyo_relleno_lateral(material: Material) -> CamaApoyoRelleno:
    """
    Fila de la tabla 8.1 para el material dado: cama de apoyo, sujecion /
    relleno lateral y numeral. [N] literal, transcrita completa en
    `constantes_normativas.CAMA_RELLENO_LATERAL`. Informativo para la
    memoria y los planos (Sec. 11, entregable 7): no compara contra ningun
    dato del punto.

    La clave de `CAMA_RELLENO_LATERAL` es el `TipoMaterial.value`. El
    catalogo de M2 (Sec. 3.4) solo ofrece concreto REFORZADO -- concreto
    simple no es un `TipoMaterial` candidato -- por eso la fila
    'concreto_simple' de la tabla 8.1 vive en `constantes_normativas.py`
    (transcripcion completa del Anexo) pero esta funcion nunca la devuelve.
    """
    return CamaApoyoRelleno(**CAMA_RELLENO_LATERAL[material.tipo.value])


# ---------------------------------------------------------------------------
# Item 5 - Lo que la Fase 8 sigue sin hacer, dicho con su razon
# ---------------------------------------------------------------------------

# Hasta T-5 el item 5 entero --rigidez de anillo, pandeo, costura, clase
# D-load con factor de cama-- se declaraba diferido al expediente por la
# hoja de ruta, y esta funcion devolvia tres frases que lo decian. T-5 lo
# implementa (ver el bloque «--- T-5 ---»); lo que SIGUE diferido es lo que
# la propia v8 deja fuera («diseño completo por AASHTO LRFD Seccion 5» del
# marco) y lo que necesita un dato que el proyecto no tiene.
DIFERIDO_MARCO = (
    "Diseño del portico del marco (momentos y acero de losas y paredes, "
    "AASHTO LRFD Seccion 5 y 12.11.3 a 12.11.5): desde VE-5 lo hace la etapa "
    "del portico a nivel de expediente (`disenar_portico`), que la tabla de "
    "bloqueos nombra si no se pudo completar. La Fase 8 calcula ademas la "
    "DEMANDA de referencia de la losa superior en kN·m/m (paso F8.MARCO)")
DIFERIDO_EMPUJE_LATERAL_MARCO = (
    "Empuje lateral del relleno sobre los muros del marco: lo calcula el "
    "portico en reposo (3.11.5.2) con el angulo de friccion del relleno "
    "('phi_relleno_trasdos', del EMS); sin el, el portico se detiene")
DIFERIDO_FLEXION_HDPE = (
    "Deformacion combinada de flexion y empuje del HDPE (AASHTO LRFD "
    "12.12.3.10.2): necesita la geometria del perfil del fabricante --la "
    "distancia minima a la fibra extrema de la Tabla A12-11 no describe el "
    "perfil--; la deflexion de servicio, el empuje y el pandeo si se "
    "verifican")
DIFERIDO_CONCRETO_DIRECTO = (
    "Metodo directo del tubo de concreto (AASHTO LRFD 12.10.4.2): no se usa; "
    "la clase sale del metodo indirecto de 12.10.4.3, que la norma admite "
    "como alternativa")
DIFERIDO_CLASES_M170M = (
    "Clases de AASHTO M 170M que el ejemplar de normas/ no deja verificar: "
    "la D-load de la Clase I no se transcribe (solo se tabula desde 1500 mm); "
    "las de las Clases III, IV y V vienen de una fuente SECUNDARIA (la tabla "
    "de ASTM C76 de un ejemplo resuelto del USACE EM 1110-2-2902, B-7); y el "
    "ultimo diametro con pared B de la Clase IV no se lee, de modo que la "
    "Clase IV queda BLOQUEADA por encima de 300 mm. Lo destraba un ejemplar "
    "legible de M 170M o de ASTM C76M ('clases_producto_por_relleno')")
DIFERIDO_PANDEO_LOCAL_HDPE = (
    "Pandeo local de los elementos del perfil del HDPE (AASHTO LRFD "
    "12.12.3.10.1b, ancho efectivo por elemento): necesita la geometria "
    "idealizada del perfil; el area efectiva se toma del minimo que AASHTO "
    "M 294 num. 7.7 exige al ensayo de compresion")
DIFERIDO_COSTURA_EMPERNADA = (
    "Resistencia de la costura EMPERNADA del TMC: ninguna fuente del "
    "repositorio la tabula; declarar esa fabricacion detiene la Fase 8 "
    "('fabricacion_tmc')")
DIFERIDO_CAMA = (
    "Cama de apoyo y relleno lateral (item 4, EG-2013): informacion para los "
    "planos, no una verificacion; la imprime la etapa de la Fase 8 a nivel "
    "de expediente")


def verificacion_diferida_estructural() -> Tuple[str, ...]:
    """
    Lo que la Fase 8 NO verifica, con su razon: la lista ENTERA, de todos
    los materiales. Ya no es el item 5 entero (T-5 lo implemento): es solo
    lo que de verdad queda fuera.

    M11 y el JSON imprimen por punto `ResultadoEstructural.diferido`, que es
    la parte de esta lista que toca al conducto de ESE punto (auditoria de
    T-5: el bloque del tubo de concreto de A-01 listaba el portico del
    marco, la flexion del HDPE y la costura empernada del TMC). Esta funcion
    queda para el punto que solo trae la cama de apoyo y para quien quiera
    la lista completa.
    """
    return (DIFERIDO_MARCO, DIFERIDO_EMPUJE_LATERAL_MARCO,
            DIFERIDO_FLEXION_HDPE, DIFERIDO_PANDEO_LOCAL_HDPE,
            DIFERIDO_CONCRETO_DIRECTO, DIFERIDO_CLASES_M170M,
            DIFERIDO_COSTURA_EMPERNADA)


# ===========================================================================
# --- T-5 --- (cadena T, 2026-11-12) LA FASE 8 REAL (INF-3.3.5)
# ===========================================================================
# Lo que la v8 llamaba «item 5 diferido al expediente» --rigidez de anillo,
# pandeo, costura, clase D-load con factor de cama-- y los items 1-2 --clase
# o calibre por la altura real de relleno-- se calculan aqui, con la carga de
# tierra y la carga viva HL-93 a traves del relleno.
#
# QUE CORRE A NIVEL DE PERFIL Y POR QUE (ficha T5-01 de
# docs/decisiones_diferidas.md). Lo que decide si la combinacion material /
# diametro / plancha / clase EXISTE --la clase del tubo de concreto, el area
# de pared con pandeo, la costura y el factor de flexibilidad del TMC, el
# empuje, el pandeo y la deflexion del HDPE-- entra a la tabla de la Fase 5
# como verificaciones F8.* (`verificaciones_estructurales`), igual que V7
# --que es Fase 8, item 3-- ya entraba: si no cumplen, el escalon se rechaza
# y MD prueba el siguiente. Lo que NO decide la existencia --la cama de
# apoyo para los planos y la demanda del marco, cuyo diseño la hoja de ruta
# deja fuera del alcance-- sigue en la etapa `servicio._fase_8`, que el
# alcance de perfil difiere.
#
# EL MARCO DE VERIFICACION, declarado por comprobacion y sin mezclas: el TMC
# y el HDPE se verifican por FACTORES DE CARGA Y RESISTENCIA (AASHTO LRFD
# 12.7.2 y 12.12.3, con gamma de las Tablas 2.4.5.3.1-1/-2 del Manual de
# Puentes, phi de la Tabla 12.5.5-1 y eta de 12.5.4); la deflexion del HDPE
# en SERVICIO (12.12.2.2); el tubo de concreto por el METODO INDIRECTO de
# 12.10.4.3, que es de SERVICIO (sin gamma ni phi: la D-load de la clase ya
# es una carga de ensayo a grieta de 0.3 mm); y el contraste de ASTM A796
# num. 8 se imprime por TENSIONES ADMISIBLES, aparte y rotulado «no rige».
# Ningun numero de una comprobacion LRFD se combina con un FS de A796.
# ===========================================================================

CRITERIO_INSTALACION_CONCRETO = "instalacion_estandar_concreto"
CRITERIO_FABRICACION_TMC = "fabricacion_tmc"
CRITERIO_ETA_CONDUCTO = "eta_importancia_operativa_conducto"
CRITERIO_RELLENO_HDPE = "relleno_estructural_hdpe"
CRITERIO_PARAMETROS_HDPE = "parametros_diseno_hdpe"
CRITERIO_PLANCHA_TMC = "corrugacion_y_espesor_tmc"
# --- T-5 (cierre) --- Los dos criterios que salieron de las auditorias.
CRITERIO_CARGA_VIVA_ALTA = "carga_viva_bajo_relleno_alto"
CRITERIO_PERFIL_HDPE = "perfil_hdpe_fabricante"
CARGA_VIVA_CONSERVAR = "conservar"
CARGA_VIVA_DESPRECIAR = "despreciar_3_6_1_2_6a"
# --- VE-4f --- El largo del area cargada a traves del tubo de concreto somero.
CRITERIO_CARGA_VIVA_SOMERA = "carga_viva_tubo_concreto_somero"
LECTURA_LARGO_NEUMATICO = "largo_del_neumatico"
LECTURA_E_SPAN_UN_PIE = "e_span_a_un_pie"
LECTURAS_TUBO_SOMERO = (LECTURA_LARGO_NEUMATICO, LECTURA_E_SPAN_UN_PIE)
# Los tres campos del perfil del fabricante por diametro.
CAMPOS_PERFIL_HDPE = ("A_mm2_mm", "I_mm4_mm", "od_m")
# El rotulo del HDPE calculado sin el perfil del fabricante (decision del
# dueño del proyecto, 2026-11-12): no es «no cumple».
ROTULO_HDPE_SIN_PRODUCTO = "no verificado con un producto real"

# Las tres formas en que la carga viva atraviesa el relleno (3.6.1.2.6a),
# cada una con su LLDF y su relleno minimo de metodo.
CONDUCTO_TUBO_CONCRETO = "tubo_concreto"
CONDUCTO_FLEXIBLE = "flexible"
CONDUCTO_CAJON = "cajon"
CONDUCTOS = (CONDUCTO_TUBO_CONCRETO, CONDUCTO_FLEXIBLE, CONDUCTO_CAJON)

VEHICULO_CAMION = "camion"
VEHICULO_TANDEM = "tandem"
# Las clases de M 170M, en el orden en que crece su resistencia.
CLASES_M170M = ("I", "II", "III", "IV", "V")
INSTALACION_TIPO_1 = "tipo_1"
INSTALACION_TIPO_4 = "tipo_4"
# Los codigos con que las verificaciones de la Fase 8 entran a la tabla de
# la Fase 5. No empiezan por «V»: no son filas de la tabla de la hoja de
# ruta (V1 a V10) sino de la Fase 8, que la corrida ensambla detras.
CODIGO_CLASE = "F8.CLASE"
CODIGO_AREA = "F8.AREA"
CODIGO_COSTURA = "F8.COSTURA"
CODIGO_FF = "F8.FF"
CODIGO_EMPUJE = "F8.EMPUJE"
CODIGO_PANDEO = "F8.PANDEO"
CODIGO_DEFLEXION = "F8.DEFLEXION"
# --- VE-4f --- La cobertura minima de la Tabla 12.6.6.3-1, juzgada cuando el
# relleno de un conducto redondo queda por debajo del dominio de la rueda
# distribuida (`verificar_conducto`).
CODIGO_COBERTURA = "F8.COBERTURA"
CODIGOS_FASE_8 = (CODIGO_COBERTURA, CODIGO_CLASE, CODIGO_AREA, CODIGO_COSTURA,
                  CODIGO_FF, CODIGO_EMPUJE, CODIGO_PANDEO, CODIGO_DEFLEXION)
# Los dos pasos del CONTRASTE con la instalacion Tipo 4 del tubo de concreto
# (no rigen): la D-load y, si alguna clase transcrita la alcanza, el relleno
# maximo. La CLI de texto lee el segundo por su codigo.
CODIGO_PASO_TIPO4 = "F8.TIPO4"
CODIGO_PASO_HMAX_TIPO4 = "F8.HMAX_TIPO4"
# --- VE-3.12 (decision 6 del dueño) --- El contraste de la practica ACPA en
# el paso F8.CLASE del tubo de concreto con poco relleno (no rige).
CODIGO_CONTRASTE_ACPA = "F8.ACPA"
CRITERIO_UMBRAL_ACPA = "relleno_max_contraste_acpa_m"
# Las clases cuya D-load viene de la fuente SECUNDARIA del USACE (VE-3.12):
# su paso cita esa tabla y no la de M 170M.
CLASES_DESDE_USACE = ("III", "IV", "V")
CITA_CLASES_USACE = "USACE_EM_1110_2_2902.B-7#C76"
# El aviso FIJO de la costura del TMC (auditoria de T-5 y decision del
# dueño del 2026-11-12): la resistencia con que se verifica es la de una
# costura REMACHADA de ASTM A796, y el EG-2013 507.02 a) describe tuberia
# armada con pernos, cuya costura no tiene resistencia tabulada. Mientras
# sea asi, un F8.COSTURA que cumple no es la costura del producto peruano.
AVISO_COSTURA_DE_OTRA_FABRICACION = (
    "la costura longitudinal del TMC se verifico con la resistencia de la "
    "costura {fabricacion} de ASTM A796 (Tabla 5 o 7), que es la de OTRA "
    "fabricacion: el EG-2013 507.02 a) describe tuberia armada con pernos, "
    "cuya costura no tiene resistencia tabulada en ninguna fuente del "
    "repositorio. Confirmar con el fabricante la resistencia de la costura "
    "del producto que se especifique")
FABRICACION_HELICOIDAL = "helicoidal"
FABRICACION_EMPERNADA = "anular_empernada"
# Que columna de COSTURA_REMACHADA_TMC_KN_M lee cada fabricacion remachada.
REMACHE_DE_FABRICACION = {"anular_remachada_simple": "simple",
                          "anular_remachada_doble": "doble"}
DURACION_INICIAL = "inicial"

NUMERAL_F8_CLASE = ("AASHTO LRFD 12.10.4.3 (metodo indirecto, servicio) y "
                    "AASHTO M 170M-04; clase indicada en el Proyecto (EG-2013 "
                    "506.02)")
NUMERAL_F8_TMC = "AASHTO LRFD 12.7.2 (LRFD); EG-2013 Tabla 507-01"
NUMERAL_F8_HDPE = "AASHTO LRFD 12.12 (LRFD y servicio); AASHTO M 294"
NUMERAL_F8_COBERTURA = ("AASHTO LRFD 12.6.6.3 y Tabla 12.6.6.3-1 (cobertura "
                        "minima del conducto redondo)")

# Decimales de presentacion de una deformacion unitaria: no entra en ningun
# calculo (mismo regimen que CIFRAS_* de modelos.py).
CIFRAS_DEFORMACION = 5      # literal-ok: decimales de presentacion; no entra en ningun calculo


def _finito_positivo(nombre: str, valor, id_punto=None) -> float:
    """Guardia de segunda linea en forma MAT-D13: `not v > 0` atrapa el NaN."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) \
            or not math.isfinite(valor) or not valor > 0:
        raise DatoInvalidoError(
            campo=nombre, valor=valor, id_punto=id_punto,
            motivo="la Fase 8 necesita un numero finito y positivo")
    return float(valor)


def _interpolar(x: float, xs, ys) -> float:
    """Interpolacion lineal con los extremos de la tabla como tope."""
    if x <= xs[0]:
        return float(ys[0])
    for x0, y0, x1, y1 in zip(xs, ys, xs[1:], ys[1:]):
        if x <= x1:
            return float(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
    return float(ys[-1])


def _veredicto_f8(cumple: bool, margen: float, unidad: str,
                  explicacion: str) -> Veredicto:
    return Veredicto(
        tipo=TipoDeVeredicto.CUMPLE if cumple else TipoDeVeredicto.NO_CUMPLE,
        margen=margen, unidad=unidad, explicacion=explicacion)


# ---------------------------------------------------------------------------
# La carga viva HL-93 a traves del relleno (AASHTO LRFD 3.6.1.2.6)
# ---------------------------------------------------------------------------

def _lldf(D_i: float, conducto: str) -> float:
    """
    Tabla 3.6.1.2.6a-1 de AASHTO LRFD: el tubo de concreto con 2.0 ft o mas
    de relleno interpola entre 1.15 (D_i <= 2.0 ft) y 1.75 (D_i >= 8.0 ft);
    toda otra alcantarilla, 1.15.
    """
    if conducto != CONDUCTO_TUBO_CONCRETO:
        return _CN.LLDF_OTRAS_ALCANTARILLAS
    return _interpolar(D_i, (_CN.LLDF_TUBO_CONCRETO_D_MIN_M,
                             _CN.LLDF_TUBO_CONCRETO_D_MAX_M),
                       (_CN.LLDF_TUBO_CONCRETO_MIN,
                        _CN.LLDF_TUBO_CONCRETO_MAX))


def incremento_dinamico_enterrado(D_E: float) -> float:
    """
    IM de los componentes enterrados, en %: IM = 33 (1 - 0.125 D_E) >= 0 %,
    con D_E, la profundidad minima de relleno, en PIES (Manual de Puentes
    2.4.3.3.2, cita MP.2.4.3.3.2). En SI la pendiente es
    `IM_ENTERRADO_PENDIENTE_SI` por metro (0.125/0.3048 = 0.4101 1/m).

    Guardia de segunda linea (auditoria de T-5): una cubierta negativa daba
    un IM de mas del 33 % --`incremento_dinamico_enterrado(-5.0)` devolvia
    100.7 %--; no finita o negativa es `DatoInvalidoError`.
    """
    if isinstance(D_E, bool) or not isinstance(D_E, (int, float)) \
            or not math.isfinite(D_E) or not D_E >= 0:
        raise DatoInvalidoError(
            campo="D_E", valor=D_E,
            motivo="la cubierta de tierra del incremento por carga dinamica "
                   "es un numero finito y no negativo")
    return max(0.0, _CN.IM_ENTERRADO_MAXIMO_PCT
               * (1.0 - _CN.IM_ENTERRADO_PENDIENTE_SI * D_E))


def _presion_de_un_vehiculo(H: float, D_i: float, LLDF: float, IM: float,
                            eje_kN: float, s_a: float):
    """
    P_L de UN vehiculo de diseño (AASHTO LRFD 3.6.1.2.6b, ecs. -1 a -7,
    trafico paralelo al vano). Devuelve (P, l_w, w_w, P_L). Dos
    interacciones: las ruedas del mismo eje si H >= H_int-t, y los ejes del
    vehiculo si H >= H_int-p; en cada caso la carga P se dobla y el area
    crece en la separacion.
    """
    w_t, l_t = _CN.ANCHO_NEUMATICO_M, _CN.LARGO_NEUMATICO_M
    s_w = _CN.SEPARACION_RUEDAS_M
    termino_luz = 0.06 * D_i     # literal-ok: el 0.06 D_i de las Eqs. 3.6.1.2.6b-1 a -3
    H_int_t = (s_w - w_t - termino_luz) / LLDF
    if H < H_int_t:
        w_w, P = w_t + LLDF * H + termino_luz, eje_kN / 2
    else:
        w_w, P = w_t + s_w + LLDF * H + termino_luz, eje_kN
    H_int_p = (s_a - l_t) / LLDF
    if H < H_int_p:
        l_w = l_t + LLDF * H
    else:
        l_w, P = l_t + s_a + LLDF * H, 2 * P
    m = _CN.PRESENCIA_MULTIPLE_UN_CARRIL
    P_L = P * (1 + IM / 100) * m / (l_w * w_w)   # literal-ok: el 100 de (1 + IM/100), Eq. 3.6.1.2.6b-7
    return P, l_w, w_w, P_L


def regla_de_la_carga_viva_bajo_relleno_alto(id_punto=None) -> str:
    """
    El valor de 'carga_viva_bajo_relleno_alto' [A], validado en segunda
    linea: `CARGA_VIVA_CONSERVAR` o `CARGA_VIVA_DESPRECIAR`.
    """
    regla = ca.valor(CRITERIO_CARGA_VIVA_ALTA)
    if regla not in (CARGA_VIVA_CONSERVAR, CARGA_VIVA_DESPRECIAR):
        raise DatoInvalidoError(
            campo=CRITERIO_CARGA_VIVA_ALTA, valor=regla, id_punto=id_punto,
            motivo=f"tiene que ser '{CARGA_VIVA_CONSERVAR}' o "
                   f"'{CARGA_VIVA_DESPRECIAR}'")
    return regla


def carga_viva_enterrada(*, H: float, D_i: float, conducto: str,
                         D_E: Optional[float] = None,
                         id_punto=None,
                         efecto: Optional[Callable[[float, float], float]] = None,
                         efecto_descripcion: str = "",
                         luz_del_permiso: Optional[float] = None,
                         ancho_del_conducto: Optional[float] = None
                         ) -> CargaVivaEnterrada:
    """
    Presion vertical de la carga viva HL-93 sobre el conducto, kPa (AASHTO
    LRFD 3.6.1.2.6; el HL-93, la presencia multiple y el IM de componentes
    enterrados del Manual de Puentes 2.4.3.2.2.2/.3/.5/.6 y 2.4.3.3.2).

    `H` es la profundidad del relleno sobre el conducto hasta la RASANTE
    --relleno mas paquete estructural--, que es la que distribuye la carga;
    `D_E`, la «cubierta de tierra» del IM, es el relleno SIN el paquete
    (subrasante menos clave): leerla asi da el IM mayor, que es el lado
    conservador (por defecto, `H`). `D_i` es el diametro interior o la luz
    libre. Trafico PARALELO al vano y un carril (3.6.1.2.6a): el de casi toda
    alcantarilla vial (C3.6.1.2.6b).

    GOBIERNA EL VEHICULO DE MAYOR EFECTO, NO EL DE MAYOR PRESION (auditoria
    de T-5). Lo que carga al conducto no es P_L sino P_L por el largo del
    area cargada que cae sobre el, y con poco relleno y luz grande el camion
    da mas presion sobre un area corta y el tandem --ejes a 4 ft, que
    interactuan desde ~0.8 m-- menos presion sobre un area 1.6 a 1.9 veces
    mas larga: medido en el tubo de concreto de 2.10 m con 0.47 m de
    relleno, W_L pasa de 65.5 kN/m (camion) a 102.4 (tandem). `efecto(P_L,
    l_w)` es la medida con que cada consumidor ordena los dos vehiculos
    --W_L = P_L min(l_w, B_c) el tubo de concreto, P_L C_L F_1 los
    flexibles, P_L el marco--; sin ella, P_L min(l_w, D_i).

    POR DEBAJO DEL DOMINIO DE LA RUEDA DISTRIBUIDA (VE-4f, ficha VE4F-01):
    el marco con menos de 2.0 ft y el tubo de concreto con 1.0 ft o mas y
    menos de 2.0 ft reparten el eje en la franja equivalente de 4.6.2.10.2
    (`_carga_viva_en_la_franja`; 3.6.1.2.6a, 4.6.2.10.1 y 12.11.2.1). Lo
    que sigue sin metodo se detiene con `MetodoNoEvaluableError`: el tubo
    redondo con menos de 1.0 ft («more comprehensive methods») y el flexible
    con 1.0 ft o menos, para el que la fuente no da otro reparto. La
    cobertura minima de la Tabla 12.6.6.3-1, que en esos casos se juzga
    antes, no es de esta funcion: es F8.COBERTURA (`verificar_conducto`).
    `ancho_del_conducto` (B_c) es el ancho del tubo sobre el que caen los
    ejes cuando el relleno es somero: con el, el efecto de cada vehiculo
    suma lo que de cada eje cae sobre el tubo.

    CON MAS DE 8.0 FT QUE ADEMAS SUPERAN LA LUZ la fuente PERMITE despreciar
    la carga viva («may be neglected»), y un permiso no se toma en silencio:
    lo decide 'carga_viva_bajo_relleno_alto' [A]. Con «conservar» (valor de
    archivo) la carga se distribuye como a cualquier otra profundidad; con
    «despreciar_3_6_1_2_6a», P_L = 0. `luz_del_permiso` es la luz de esa
    condicion cuando no es `D_i`: en una alcantarilla de varios vanos, la
    distancia entre las caras interiores de los muros extremos.
    """
    H = _finito_positivo("H_relleno_total", H, id_punto)
    D_i = _finito_positivo("D_interior", D_i, id_punto)
    D_E = H if D_E is None else _finito_positivo("D_E", D_E, id_punto)
    if conducto not in CONDUCTOS:
        raise DatoInvalidoError(
            campo="conducto", valor=conducto, id_punto=id_punto,
            motivo=f"tiene que ser uno de {CONDUCTOS}: de el salen el LLDF y "
                   "el relleno minimo del metodo (3.6.1.2.6a)")
    if efecto is None:
        def efecto(P_L: float, l_w: float) -> float:
            return P_L * min(l_w, D_i)
        efecto_descripcion = ("P_L min(l_w, D_i): la carga por unidad de "
                              "longitud sobre la luz")
    if conducto == CONDUCTO_FLEXIBLE:
        minimo = _CN.RELLENO_MIN_METODO_NO_CONCRETO_M
        if not H > minimo + TOL_UMBRAL_NORMATIVO:
            raise MetodoNoEvaluableError(
                que="carga viva sobre el conducto flexible (Fase 8)",
                procedimiento=("un analisis mas completo, que la fuente no "
                               "describe y este programa no implementa; o "
                               "subir la rasante"),
                motivo=(f"el relleno sobre la clave hasta la rasante es "
                        f"{H:.3f} m y el metodo de la rueda distribuida de "
                        f"3.6.1.2.6 vale con mas de {minimo:.4f} m sobre un "
                        "conducto redondo que no es de concreto; por debajo "
                        "AASHTO LRFD 3.6.1.2.6a no da otro reparto («Round "
                        "culverts with less than 1.0 ft of fill shall be "
                        "analyzed with more comprehensive methods»)"),
                id_punto=id_punto,
                rotulo=MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL)
    elif not H >= _CN.RELLENO_MIN_METODO_TUBO_CONCRETO_M - TOL_UMBRAL_NORMATIVO:
        if (conducto == CONDUCTO_TUBO_CONCRETO
                and not H >= (_CN.RELLENO_MIN_FRANJA_TUBO_CONCRETO_M
                              - TOL_UMBRAL_NORMATIVO)):
            raise MetodoNoEvaluableError(
                que="carga viva sobre el tubo de concreto (Fase 8)",
                procedimiento=("los «more comprehensive methods» que AASHTO "
                               "LRFD 3.6.1.2.6a manda y no describe, que este "
                               "programa no implementa; o subir la rasante"),
                motivo=(f"el relleno sobre la clave hasta la rasante es "
                        f"{H:.3f} m, menos de 1.0 ft "
                        f"({_CN.RELLENO_MIN_FRANJA_TUBO_CONCRETO_M:.4f} m): "
                        "«Round culverts with less than 1.0 ft of fill shall "
                        "be analyzed with more comprehensive methods»"),
                id_punto=id_punto,
                rotulo=MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL)
        return _carga_viva_en_la_franja(
            H=H, D_i=D_i, D_E=D_E, conducto=conducto, id_punto=id_punto,
            efecto=efecto, efecto_descripcion=efecto_descripcion,
            ancho_del_conducto=ancho_del_conducto)
    LLDF = _lldf(D_i, conducto)
    IM = incremento_dinamico_enterrado(D_E)
    m = _CN.PRESENCIA_MULTIPLE_UN_CARRIL
    luz = (D_i if luz_del_permiso is None
           else _finito_positivo("luz_del_permiso", luz_del_permiso, id_punto))
    en_zona = H > _CN.RELLENO_DESPRECIA_CARGA_VIVA_M and H > luz
    regla_alto = regla_de_la_carga_viva_bajo_relleno_alto(id_punto)
    despreciada = en_zona and regla_alto == CARGA_VIVA_DESPRECIAR
    candidatos = []
    for nombre, eje, s_a in (
            (VEHICULO_CAMION, _CN.EJE_CAMION_HL93_KN,
             _CN.SEPARACION_EJES_CAMION_MIN_M),
            (VEHICULO_TANDEM, _CN.EJE_TANDEM_HL93_KN,
             _CN.SEPARACION_EJES_TANDEM_M)):
        P_v, l_v, w_v, PL_v = _presion_de_un_vehiculo(H, D_i, LLDF, IM, eje, s_a)
        candidatos.append((nombre, P_v, l_v, w_v, PL_v, efecto(PL_v, l_v)))
    if despreciada:
        vehiculo, P, l_w, w_w, P_L, e_gob = VEHICULO_CAMION, 0.0, 0.0, 0.0, 0.0, 0.0
    else:
        # El de MAYOR EFECTO; en el empate, el camion (el primero).
        vehiculo, P, l_w, w_w, P_L, e_gob = max(candidatos, key=lambda c: c[-1])
    sust = (
        Magnitud("H", H, "m", "relleno sobre la clave fisica hasta la "
                 "RASANTE: subrasante menos clave mas el paquete estructural "
                 "(rasante menos subrasante, columnas del CSV)",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("D_i", D_i, "m", "diametro interior o luz libre del escalon",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("LLDF", LLDF, "", "Tabla 3.6.1.2.6a-1 de AASHTO LRFD"
                 + (" (tubo de concreto: interpolado por diametro)"
                    if conducto == CONDUCTO_TUBO_CONCRETO else ""),
                 cifras=CIFRAS_FACTOR),
        Magnitud("IM", IM, "%", f"33 (1 - 0.125 D_E), D_E en pies (Manual de "
                 f"Puentes 2.4.3.3.2), con D_E = {D_E:.3f} m de cubierta de "
                 "tierra: el relleno sin el paquete estructural, que da el IM "
                 "mayor", cifras=CIFRAS_MAGNITUD),
        Magnitud("m", m, "", "un carril cargado, Tabla 2.4.3.2.2.6-1 del "
                 "Manual de Puentes", cifras=CIFRAS_FACTOR),
        Magnitud("P", P, "kN", f"ruedas que interactuan del {vehiculo} HL-93 "
                 "(ejes de 32.0 kip el camion y de 25.0 kip el tandem; Manual "
                 "de Puentes 2.4.3.2.2.2 y .3)", cifras=CIFRAS_MAGNITUD),
        Magnitud("l_w", l_w, "m", "largo del area cargada a la profundidad H, "
                 "paralelo al vano: l_t + LLDF H, mas s_a si los ejes "
                 "interactuan", cifras=CIFRAS_MAGNITUD),
        Magnitud("w_w", w_w, "m", "ancho del area cargada, transversal al "
                 "vano: w_t + LLDF H + 0.06 D_i, mas s_w si las ruedas "
                 "interactuan", cifras=CIFRAS_MAGNITUD),
    ) + tuple(
        Magnitud(f"P_L del {nombre}", PL_v, "kPa",
                 f"sobre l_w = {l_v:.3f} m; efecto = {e_v:.3f} "
                 f"({efecto_descripcion})", cifras=CIFRAS_MAGNITUD)
        for nombre, _P, l_v, _w, PL_v, e_v in candidatos)
    citas = ("AASHTO_LRFD_9.3.6.1.2.6a#RELLENO", "AASHTO_LRFD_9.3.6.1.2.6a#EJES",
             "AASHTO_LRFD_9.3.6.1.2.6a#UN_CARRIL", "AASHTO_LRFD_9.T3.6.1.2.6a-1",
             "AASHTO_LRFD_9.C3.6.1.2.6b", "MP.2.4.3.2.2.2", "MP.2.4.3.2.2.3",
             "MP.2.4.3.2.2.5", "MP.2.4.3.2.2.6", "MP.2.4.3.3.2")
    if en_zona:
        citas += ("AASHTO_LRFD_9.3.6.1.2.6a#DESPRECIABLE",)
        if luz_del_permiso is not None:
            citas += ("AASHTO_LRFD_9.3.6.1.2.6a#VARIOS_VANOS",)
    nota_permiso = ""
    if en_zona and not despreciada:
        nota_permiso = (
            f" El relleno ({H:.3f} m) supera 8.0 ft y la luz ({luz:.3f} m): "
            "la fuente PERMITE despreciar la carga viva y el proyecto la "
            f"CONSERVA ('{CRITERIO_CARGA_VIVA_ALTA}' = {regla_alto}).")
    elif despreciada:
        nota_permiso = (
            f" El relleno ({H:.3f} m) supera 8.0 ft y la luz ({luz:.3f} m): "
            "la carga viva se DESPRECIA por el permiso de la fuente, que el "
            f"proyecto toma ('{CRITERIO_CARGA_VIVA_ALTA}' = {regla_alto}); "
            "conservarla es el valor de archivo y el lado seguro.")
    p = paso(
        "F8.CARGA_VIVA", codigo="F8.LL",
        que=(f"Carga viva HL-93 sobre el conducto (gobierna el {vehiculo}, "
             "por efecto)"
             if not despreciada else
             "Carga viva HL-93 sobre el conducto: despreciada (relleno de "
             "mas de 8.0 ft que ademas supera la luz; permiso de 3.6.1.2.6a "
             "que el proyecto declara tomar)"),
        formula=("P_L = P (1 + IM/100) m / (l_w w_w); l_w = l_t [+ s_a] + "
                 "LLDF H; w_w = w_t [+ s_w] + LLDF H + 0.06 D_i"),
        formula_cita_id="AASHTO_LRFD_9.3.6.1.2.6b#PL",
        citas_textuales=citas,
        sustitucion=sust,
        resultado=Magnitud("P_L", P_L, "kPa", "presion vertical de la carga "
                           "viva sobre el conducto, con IM y m",
                           cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=(
            "GOBIERNA EL VEHICULO DE MAYOR EFECTO sobre este conducto "
            f"({efecto_descripcion}), no el de mayor presion: con poco "
            "relleno y luz grande el tandem carga mas con menos presion, "
            "porque su area es mas larga. "
            "Trafico PARALELO al vano: el vano de un tubo es su diametro, "
            "medido a lo largo de la via, y la fuente dice que es el caso de "
            "la gran mayoria de las alcantarillas viales; el esviaje no lo "
            "cambia. Las cifras del HL-93 son las del Manual de Puentes en su "
            "unidad primaria (kip, ft, in) convertidas con los factores "
            "exactos: 32.0 kip = 142.3 kN, no las 14.55 t del parentesis."
            + nota_permiso))
    return CargaVivaEnterrada(H_m=H, LLDF=LLDF, IM_pct=IM, m=m,
                              vehiculo=vehiculo, P_kN=P, l_w_m=l_w, w_w_m=w_w,
                              P_L_kPa=P_L, despreciada=despreciada, paso=p,
                              efecto=e_gob,
                              efecto_descripcion=efecto_descripcion,
                              candidatos=tuple(candidatos),
                              en_zona_de_permiso=en_zona)


def lectura_del_tubo_de_concreto_somero(id_punto=None) -> str:
    """
    El valor de 'carga_viva_tubo_concreto_somero' [A] (VE-4f), validado en
    segunda linea: `LECTURA_LARGO_NEUMATICO` o `LECTURA_E_SPAN_UN_PIE`.
    `CriterioPendienteError` mientras siga sin valor: la fuente no dice que
    largo tiene el area cargada A TRAVES del tubo de concreto somero.
    """
    lectura = ca.valor(CRITERIO_CARGA_VIVA_SOMERA)
    if lectura not in LECTURAS_TUBO_SOMERO:
        raise DatoInvalidoError(
            campo=CRITERIO_CARGA_VIVA_SOMERA, valor=lectura, id_punto=id_punto,
            motivo=f"tiene que ser una de {LECTURAS_TUBO_SOMERO}")
    return lectura


def _carga_viva_en_la_franja(*, H: float, D_i: float, D_E: float,
                             conducto: str, id_punto,
                             efecto: Callable[[float, float], float],
                             efecto_descripcion: str,
                             ancho_del_conducto: Optional[float]
                             ) -> CargaVivaEnterrada:
    """
    --- VE-4f --- La carga viva con relleno SOMERO: menos de 2.0 ft hasta la
    rasante sobre un marco o sobre un tubo de concreto (con 1.0 ft o mas).
    AASHTO LRFD 4.6.2.10.2 (Case 1, trafico paralelo al vano), al que
    remiten 3.6.1.2.6a (tubo de concreto), 4.6.2.10.1 y 12.11.2.1 (cajon):

        E      = 96 + 1.44 S       (in, S en ft)        (4.6.2.10.2-1)
        E_span = L_T + LLDF H      (in)                 (4.6.2.10.2-2)
        P_L    = P (1 + IM/100) m / (E E_span)

    con P la carga de UN eje (los ejes del tandem, a 4 ft, no interactuan
    con menos de 2.0 ft: E_span <= 10 + 1.15 x 24 in = 3.13 ft), m de un
    carril y LLDF el de «All other culverts» (1.15: la fila del tubo de
    concreto de la Tabla 3.6.1.2.6a-1 es para 2.0 ft o mas).

    EL MARCO usa la profundidad que tiene: H en E_span y D_E en el IM. Es el
    reparto del ejemplo resuelto de MnDOT, LRFD Bridge Design Manual §12.6
    (cajon de 16 ft bajo 1 ft: E = 119.04 in, E_span = 23.8 in, 2.52 y 1.97
    ksf), contrastado en tests/test_ve4f_relleno_bajo.py.

    EL TUBO DE CONCRETO se diseña «for a depth of 1.0 ft» (cita #UN_PIE): el
    IM con D_E = 1.0 ft, o la cubierta de tierra si es menor (el IM mayor), y
    el largo del area cargada A TRAVES del tubo lo declara
    'carga_viva_tubo_concreto_somero' [A] -- L_T, o L_T + LLDF (1.0 ft) --
    porque la fuente da el ancho E a lo largo del tubo y calla ese largo.
    Con `ancho_del_conducto` (B_c), el efecto de un vehiculo suma lo que de
    cada uno de sus ejes cae sobre el tubo, min(B_c, l) + min(l, B_c - s_a)
    cuando el segundo eje alcanza; sin el, el del primero.
    """
    LLDF = _CN.LLDF_OTRAS_ALCANTARILLAS
    m = _CN.PRESENCIA_MULTIPLE_UN_CARRIL
    E = _CN.FRANJA_CAJON_BASE_M + _CN.FRANJA_CAJON_PENDIENTE_SI * D_i
    es_tubo = conducto == CONDUCTO_TUBO_CONCRETO
    if es_tubo:
        lectura = lectura_del_tubo_de_concreto_somero(id_punto)
        H_diseno = _CN.PROFUNDIDAD_DISENO_TUBO_CONCRETO_SOMERO_M
        D_E_im = min(D_E, H_diseno)
        l = (_CN.LARGO_NEUMATICO_M if lectura == LECTURA_LARGO_NEUMATICO
             else _CN.LARGO_NEUMATICO_M + LLDF * H_diseno)
        desc_l = (f"largo del area cargada A TRAVES del tubo, "
                  f"'{CRITERIO_CARGA_VIVA_SOMERA}' [A] = {lectura}: "
                  + ("L_T, el del neumatico (3.6.1.2.5), sin el aumento por "
                     "el relleno que C4.6.2.10.2 permite despreciar"
                     if lectura == LECTURA_LARGO_NEUMATICO else
                     "E_span = L_T + LLDF (1.0 ft), la Eq. 4.6.2.10.2-2 a la "
                     "profundidad de diseño"))
    else:
        lectura = ""
        H_diseno = H
        D_E_im = D_E
        l = _CN.LARGO_NEUMATICO_M + LLDF * H
        desc_l = ("E_span = L_T + LLDF H, largo del area cargada paralelo al "
                  "vano (Eq. 4.6.2.10.2-2)")
    IM = incremento_dinamico_enterrado(D_E_im)
    candidatos = []
    for nombre, eje, s_a in (
            (VEHICULO_CAMION, _CN.EJE_CAMION_HL93_KN,
             _CN.SEPARACION_EJES_CAMION_MIN_M),
            (VEHICULO_TANDEM, _CN.EJE_TANDEM_HL93_KN,
             _CN.SEPARACION_EJES_TANDEM_M)):
        P_L_v = eje * (1 + IM / 100) * m / (E * l)   # literal-ok: el 100 de (1 + IM/100), Eq. 3.6.1.2.6b-7
        if ancho_del_conducto is None:
            largo = l
        else:
            largo = (min(ancho_del_conducto, l)
                     + max(0.0, min(l, ancho_del_conducto - s_a)))
        candidatos.append((nombre, eje, l, E, P_L_v, efecto(P_L_v, largo)))
    # El de MAYOR EFECTO; en el empate, el camion (el primero).
    vehiculo, P, l_w, w_w, P_L, e_gob = max(candidatos, key=lambda c: c[-1])
    sust = (
        Magnitud("H", H, "m", "relleno sobre la clave fisica hasta la "
                 "RASANTE: subrasante menos clave mas el paquete estructural",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("S", D_i, "m", "luz libre (interior) del escalon",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("E", E, "m", "ancho de la franja a lo largo del conducto, "
                 "96 + 1.44 S (in, S en ft; Eq. 4.6.2.10.2-1)",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("LLDF", LLDF, "", "Tabla 3.6.1.2.6a-1, «All other "
                 "culverts» (la fila del tubo de concreto es de 2.0 ft o "
                 "mas)", cifras=CIFRAS_FACTOR),
        Magnitud("l", l, "m", desc_l, cifras=CIFRAS_MAGNITUD),
        Magnitud("IM", IM, "%", f"33 (1 - 0.125 D_E), D_E en pies (Manual de "
                 f"Puentes 2.4.3.3.2), con D_E = {D_E_im:.3f} m"
                 + (": la profundidad de diseño de 1.0 ft, o la cubierta de "
                    "tierra si es menor (el IM mayor)" if es_tubo else
                    " de cubierta de tierra, sin el paquete estructural"),
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("m", m, "", "un carril cargado (4.6.2.10.2; Tabla "
                 "2.4.3.2.2.6-1 del Manual de Puentes)", cifras=CIFRAS_FACTOR),
        Magnitud("P", P, "kN", f"un eje del {vehiculo} HL-93 (32.0 kip el "
                 "camion, 25.0 kip el tandem; Manual de Puentes 2.4.3.2.2.2 "
                 "y .3)", cifras=CIFRAS_MAGNITUD),
    ) + tuple(
        Magnitud(f"P_L del {nombre}", PL_v, "kPa",
                 f"un eje sobre E x l; efecto = {e_v:.3f} "
                 f"({efecto_descripcion})", cifras=CIFRAS_MAGNITUD)
        for nombre, _P, _l, _E, PL_v, e_v in candidatos)
    citas = ("AASHTO_LRFD_9.4.6.2.10.2#UN_CARRIL",
             "AASHTO_LRFD_9.3.6.1.2.6a#EJES", "AASHTO_LRFD_9.T3.6.1.2.6a-1",
             "MP.2.4.3.2.2.2", "MP.2.4.3.2.2.3", "MP.2.4.3.2.2.5",
             "MP.2.4.3.2.2.6", "MP.2.4.3.3.2")
    if es_tubo:
        citas = ("AASHTO_LRFD_9.3.6.1.2.6a#CONCRETO_SOMERO",
                 "AASHTO_LRFD_9.3.6.1.2.6a#UN_PIE",
                 "AASHTO_LRFD_9.C4.6.2.10.2#E_SPAN") + citas
        nota = (
            "TUBO DE CONCRETO CON 1.0 A 2.0 FT HASTA LA RASANTE: el eje se "
            "reparte a lo largo del tubo en el ancho E de la Eq. "
            "4.6.2.10.2-1 «regardless of the direction of travel», y el tubo "
            "se diseña a la profundidad de 1.0 ft. Que esa profundidad entre "
            "en el IM y en E_span, y no en la carga de tierra, es lectura del "
            "proyecto; el largo A TRAVES del tubo es la eleccion "
            f"'{CRITERIO_CARGA_VIVA_SOMERA}' [A], que la fuente no fija. "
            "GOBIERNA EL VEHICULO DE MAYOR CARGA SOBRE EL TUBO "
            f"({efecto_descripcion}): con un tubo mas ancho que la "
            "separacion de los ejes del tandem, su segundo eje tambien cae "
            "en el.")
    else:
        citas = ("AASHTO_LRFD_9.4.6.2.10.1", "AASHTO_LRFD_9.12.11.2.1#SOMERO",
                 ) + citas
        nota = (
            "MARCO CON MENOS DE 2.0 FT DE RELLENO: el eje se reparte en la "
            "franja equivalente de 4.6.2.10.2 (12.11.2.1 y 4.6.2.10.1), con "
            "la profundidad que tiene. Es el reparto del ejemplo resuelto de "
            "MnDOT (LRFD Bridge Design Manual §12.6), que suma ademas la "
            "carga de carril: la 9.a ed. 3.6.1.2.6a manda aplicar a una "
            "alcantarilla SOLO los ejes, y la carga de carril no entra. "
            f"GOBIERNA EL VEHICULO DE MAYOR EFECTO ({efecto_descripcion}).")
    p = paso(
        "F8.CARGA_VIVA", codigo="F8.LL",
        que=("Carga viva HL-93 con relleno somero: franja equivalente de "
             f"4.6.2.10.2 (gobierna el {vehiculo}, por efecto)"),
        formula=("E = 96 + 1.44 S (in, S en ft); E_span = L_T + LLDF H (in); "
                 "P_L = P (1 + IM/100) m / (E l)"),
        formula_cita_id="AASHTO_LRFD_9.4.6.2.10.2#FRANJA",
        citas_textuales=citas,
        sustitucion=sust,
        resultado=Magnitud("P_L", P_L, "kPa", "presion de un eje sobre la "
                           "franja, con IM y m", cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=nota)
    return CargaVivaEnterrada(H_m=H, LLDF=LLDF, IM_pct=IM, m=m,
                              vehiculo=vehiculo, P_kN=P, l_w_m=l_w, w_w_m=w_w,
                              P_L_kPa=P_L, despreciada=False, paso=p,
                              efecto=e_gob,
                              efecto_descripcion=efecto_descripcion,
                              candidatos=tuple(candidatos),
                              en_zona_de_permiso=False, relleno_somero=True)


def _aviso_de_carga_viva_despreciada(cv: CargaVivaEnterrada) -> Tuple[str, ...]:
    """El aviso del punto cuando la carga viva se desprecio a la altura REAL."""
    if not cv.despreciada:
        return ()
    return (
        f"F8: la carga viva se DESPRECIO con {cv.H_m:.2f} m de relleno hasta "
        f"la rasante, por el permiso de AASHTO LRFD 3.6.1.2.6a que "
        f"'{CRITERIO_CARGA_VIVA_ALTA}' declara tomar; el valor de archivo "
        "(conservarla) es el lado seguro",)


# ---------------------------------------------------------------------------
# Lo comun: alturas, pesos especificos, factores
# ---------------------------------------------------------------------------

def espesor_del_paquete(punto: PuntoCritico) -> float:
    """
    Espesor del paquete estructural del pavimento, m: cota de rasante menos
    cota de subrasante (las dos columnas del CSV). Negativo no puede ser:
    `DatoInvalidoError` sobre 'cota_rasante' (hay que CORREGIR una cota).
    """
    e = punto.cota_rasante - punto.cota_subrasante
    if not e >= 0:
        raise DatoInvalidoError(
            campo="cota_rasante", valor=punto.cota_rasante, id_punto=punto.id,
            motivo=(f"la rasante queda {e:+.3f} m respecto de la subrasante: "
                    "el paquete estructural no puede tener espesor negativo"))
    return e


def pesos_especificos_de_carga(*, piso_tubo_concreto: bool
                               ) -> Tuple[float, float, str]:
    """
    (gamma del relleno, gamma del paquete, procedencia) de la carga sobre el
    conducto, kN/m3.

    EL RELLENO CARGA AQUI, Y EN V7 ESTABILIZA. 'peso_especifico_relleno_kn_m3'
    adopta el extremo BAJO de su ventana (17.0) porque en la flotacion el
    relleno ayuda; en la Fase 8 empuja, y el extremo bajo no es el
    conservador. Se toma el MAYOR de: el declarado; el que el Manual de
    Puentes permite usar a falta de informacion precisa para un suelo
    compactado (Tabla 2.4.2.1-1, 0.120 kcf); y, para el tubo de concreto, el
    piso de AASHTO LRFD 12.10.2.1 (110 lb/ft3). El paquete pesa como la
    superficie de rodadura de la misma tabla del Manual (0.140 kcf).

    EL PISO DE 110 lb/ft3 (17.28 kN/m3) NO PUEDE GOBERNAR HOY: los 0.120 kcf
    del Manual (18.85 kN/m3) entran siempre en el maximo y son mayores. Se
    lista para que la procedencia diga que la exigencia de 12.10.2.1 se
    cumple, no porque mueva el resultado (auditoria de T-5).
    """
    declarado = _finito_positivo(CRITERIO_PESO_RELLENO,
                                 ca.valor(CRITERIO_PESO_RELLENO))
    candidatos = [("'peso_especifico_relleno_kn_m3' [A]", declarado),
                  ("Manual de Puentes Tabla 2.4.2.1-1, arena, limo o arcilla "
                   "compactado, 0.120 kcf [N]", _CN.PESO_SUELO_COMPACTADO_KN_M3)]
    if piso_tubo_concreto:
        candidatos.append(("piso de AASHTO LRFD 12.10.2.1, 110 lb/ft3 [C]",
                           _CN.PESO_SUELO_MIN_TUBO_CONCRETO_KN_M3))
    origen, gamma = max(candidatos, key=lambda c: c[1])
    procedencia = ("el mayor de " + "; ".join(
        f"{t} = {v:.2f}" for t, v in candidatos) + f" -- gobierna {origen}")
    return gamma, _CN.PESO_PAQUETE_ESTRUCTURAL_KN_M3, procedencia


def _gamma_ev_max(material: Material) -> Tuple[float, str]:
    """El gamma_EV MAXIMO de la fila de este conducto (Tabla 2.4.5.3.1-2)."""
    fila = _fila_elegida(ca.valor(CRITERIO_FACTORES_CARGA),
                         _elemento_de(material), CARGA_RELLENO)
    return _gamma_p(fila, EXTREMO_DESESTABILIZANTE), fila_gamma_p_legible(fila)


def _gamma_ll() -> float:
    """
    gamma de la carga viva en 'Resistencia I' (columna «LL IM CE BR PL LS»
    de la Tabla 2.4.5.3.1-1 del Manual de Puentes): 1.75.
    """
    return float(TABLA_COMBINACIONES_FILAS[COMBINACION_V7]["LS"])


def _eta() -> float:
    """eta = eta_D eta_R eta_I con eta_D = eta_R = 1.00 (12.5.4)."""
    return _finito_positivo(CRITERIO_ETA_CONDUCTO, ca.valor(CRITERIO_ETA_CONDUCTO))


def _campos_f8(*, codigo: str, que: str, formula: str, sust,
               obtenido: Magnitud, admisible: float, unidad: str,
               cita_umbral: str, descripcion_umbral: str, aplicacion: str,
               criterio: Optional[str], cumple: bool, margen: float,
               explicacion: str, citas=(), formula_cita_id: str = "",
               nota: str = "") -> dict:
    """
    Los campos del paso de una verificacion F8.*: el mismo molde para todas.
    El paso lo construye el llamador con `paso("F8.X", **...)`, con el id del
    fundamento LITERAL, que es lo que `src/indice_formulas.py` lee del AST.
    """
    return dict(codigo=codigo, que=que, formula=formula,
                formula_cita_id=formula_cita_id,
                citas_textuales=tuple(citas), sustitucion=tuple(sust),
                resultado=obtenido,
                # El CARACTER del umbral se lee de la cita que lo sostiene, no
                # se escribe a mano: la FASE A fijaba "EXIGENCIA" para todas
                # las F8, tambien para el 5 % de la deflexion del HDPE, que
                # es la recomendacion de un comentario (auditoria de T-5;
                # es NOR-MEM-01 en pequeño).
                umbral=Umbral(descripcion=descripcion_umbral, valor=admisible,
                              unidad=unidad, cita_id=cita_umbral,
                              caracter=_CN.caracter_del_umbral(
                                  {"citas": (cita_umbral,)}),
                              aplicacion=aplicacion,
                              criterio_aplicado=criterio),
                veredicto=_veredicto_f8(cumple, margen, unidad, explicacion),
                nota_del_proyecto=nota)


def _verificacion_f8(p: PasoDeMemoria, *, numeral: str) -> Verificacion:
    """La `Verificacion` de un paso F8.*: el veredicto, el umbral y el codigo
    salen del paso, de modo que la tabla y la memoria no pueden discrepar."""
    return Verificacion(cumple=p.veredicto.cumple, numeral=numeral,
                        valor_obtenido=p.resultado.valor,
                        valor_admisible=p.umbral.valor,
                        criterio_aplicado=p.umbral.criterio_aplicado,
                        codigo=p.codigo, paso=p)


def _relleno_maximo(margen_de: Callable[[float], float], H_rel: float,
                    D: float, id_punto=None) -> Optional[float]:
    """
    El mayor relleno sobre la clave con que la eleccion sigue cumpliendo: el
    PRIMER cruce por cero de `margen_de(H)` (margen >= 0 cumple) por encima
    de la altura real. None si ya no cumple en la altura real.

    El techo de la busqueda parte del umbral en que la carga viva se
    desprecia (8.0 ft por encima de la luz) y se dobla hasta que el margen
    es negativo: siempre llega, porque la carga de tierra crece sin tope con
    el relleno y la resistencia no; si la aritmetica desbordara antes,
    `LimiteNumericoError`. El intervalo se muestrea en
    `TRAMOS_BUSQUEDA_RELLENO_MAXIMO` tramos y Brent se aplica en el primero
    que cambia de signo (ver tolerancias.py: el margen no es monotono).
    """
    if margen_de(H_rel) < 0:
        return None
    H_techo = max(2 * H_rel, _CN.RELLENO_DESPRECIA_CARGA_VIVA_M + D)
    while margen_de(H_techo) >= 0:
        H_techo *= 2
        if not math.isfinite(H_techo):
            raise LimiteNumericoError(
                "altura_relleno", valor=H_rel, id_punto=id_punto,
                motivo="la busqueda del relleno maximo de la Fase 8 desbordo "
                       "sin que el margen se hiciera negativo")
    tramo = (H_techo - H_rel) / TRAMOS_BUSQUEDA_RELLENO_MAXIMO
    H_a = H_rel
    for i in range(1, TRAMOS_BUSQUEDA_RELLENO_MAXIMO + 1):
        H_b = H_techo if i == TRAMOS_BUSQUEDA_RELLENO_MAXIMO else H_rel + i * tramo
        if margen_de(H_b) < 0:
            from scipy.optimize import brentq     # perezoso (PC-10), como M4
            return brentq(margen_de, H_a, H_b, xtol=TOL_BRENT)
        H_a = H_b
    raise LimiteNumericoError(                  # inalcanzable: margen(H_techo) < 0
        "altura_relleno", valor=H_rel, id_punto=id_punto,
        motivo="el muestreo del relleno maximo no encontro el cruce")


# ---------------------------------------------------------------------------
# Tubo de concreto reforzado: metodo indirecto (AASHTO LRFD 12.10.4.3)
# ---------------------------------------------------------------------------

def _clases_transcritas() -> dict:
    """
    {clase: D-load de 0.3 mm} del tubo de concreto, de
    'clases_producto_por_relleno', en el orden de `CLASES_M170M`. Una clave
    que no sea una de las cinco clases de M 170M es `DatoInvalidoError`: la
    version anterior la ignoraba en silencio (`{"VI": 200}` desaparecia).
    """
    tabla = ca.valor(CRITERIO_CLASES_PRODUCTO)
    del_material = (tabla.get(TipoMaterial.CONCRETO_REFORZADO.value)
                    if hasattr(tabla, "get") else None)
    if not hasattr(del_material, "get"):
        raise DatoInvalidoError(
            campo=CRITERIO_CLASES_PRODUCTO, valor=tabla,
            motivo="se espera {'concreto_reforzado': {clase: D-load de "
                   "0.3 mm en N/m/mm}}")
    ajenas = sorted(str(c) for c in del_material if c not in CLASES_M170M)
    if ajenas:
        raise DatoInvalidoError(
            campo=CRITERIO_CLASES_PRODUCTO, valor=ajenas,
            motivo=f"AASHTO M 170M tiene las clases {', '.join(CLASES_M170M)}"
                   "; no existe otra")
    return {c: _finito_positivo(CRITERIO_CLASES_PRODUCTO, del_material[c])
            for c in CLASES_M170M if c in del_material}


def _clase_tabulada_con_pared_b(clase: str, D_mm: float) -> bool:
    """
    True si AASHTO M 170M tabula la clase con PARED B en el diametro `D_mm`:
    desde su primera fila (`DIAMETRO_MIN_TABULADO_POR_CLASE_M170M_MM`) hasta
    su ultima fila con pared B leida (`DIAMETRO_MAX_TABULADO_PARED_B_POR_
    CLASE_M170M_MM`; sin entrada, el tope general del catalogo de concreto).
    Por encima la clase es diseño especial de la Seccion 7.2 (VE-3.12, H1 de
    la verificacion de las clases: la Clase V con pared B solo llega a 1200
    mm).
    """
    minimo = _CN.DIAMETRO_MIN_TABULADO_POR_CLASE_M170M_MM[clase]
    maximo = _CN.DIAMETRO_MAX_TABULADO_PARED_B_POR_CLASE_M170M_MM.get(
        clase, _CN.DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM)
    return (D_mm + TOL_UMBRAL_NORMATIVO >= minimo
            and D_mm <= maximo + TOL_UMBRAL_NORMATIVO)


def _clase_bloqueada(clase: str, D_mm: float) -> bool:
    """
    True si el ejemplar de M 170M no deja verificar que la clase se tabule
    en el diametro `D_mm`: su tabla solo se lee hasta
    `DIAMETRO_MAX_LEGIBLE_POR_CLASE_M170M_MM` (la Clase IV, 300 mm). No se
    inventa el tope (decision 7 del dueño, 2026-11-17): por encima, BLOQUEADA.
    """
    legible = _CN.DIAMETRO_MAX_LEGIBLE_POR_CLASE_M170M_MM.get(clase)
    return legible is not None and D_mm > legible + TOL_UMBRAL_NORMATIVO


def clases_de_concreto_para(D: float) -> Tuple[dict, Tuple[str, ...]]:
    """
    Las clases de M 170M que se le pueden ofrecer a un tubo de diametro `D`
    (m): ({clase: D-load} de las TRANSCRITAS que la norma tabula con pared B
    para ese diametro y que el ejemplar deja VERIFICAR, en orden creciente;
    las clases SUPERIORES a la mayor ofrecida que la norma tabula para ese
    diametro y no estan transcritas).

    La norma no tabula todas las clases en todos los diametros: la Clase I
    empieza en 1500 mm (`DIAMETRO_MIN_TABULADO_POR_CLASE_M170M_MM`) y, desde
    VE-3.12, la Clase V con pared B termina en 1200 mm. Sin esta guardia,
    completar el criterio con la D-load de la Clase I hacia que un tubo de
    0.90 m saliera «Clase I» (auditoria de T-5). Una clase BLOQUEADA en el
    diametro (`clases_bloqueadas_para`) no se ofrece ni cuenta como que falta.
    """
    D_mm = D * MILIMETROS_POR_METRO
    transcritas = _clases_transcritas()
    tabuladas = [c for c in CLASES_M170M
                 if _clase_tabulada_con_pared_b(c, D_mm)]
    ofrecidas = {c: transcritas[c] for c in tabuladas
                 if c in transcritas and not _clase_bloqueada(c, D_mm)}
    ultima = max((tabuladas.index(c) for c in ofrecidas), default=-1)
    faltan = tuple(c for c in tabuladas[ultima + 1:] if c not in transcritas)
    return ofrecidas, faltan


def clases_bloqueadas_para(D: float) -> Tuple[str, ...]:
    """
    Las clases TRANSCRITAS que M 170M tabularia en el diametro `D` (m) segun
    su primera fila, pero cuyo ultimo diametro el ejemplar no deja leer y que
    quedan por encima de lo legible (VE-3.12, decision 7 del dueño): hoy la
    Clase IV por encima de 300 mm. Un tubo que necesite una de ellas se
    detiene con el dato que falta (`verificar_concreto`); no recibe otra
    clase ni otro diametro para esquivarla.
    """
    D_mm = D * MILIMETROS_POR_METRO
    transcritas = _clases_transcritas()
    return tuple(c for c in CLASES_M170M
                 if c in transcritas and _clase_tabulada_con_pared_b(c, D_mm)
                 and _clase_bloqueada(c, D_mm))


def verificar_concreto(*, punto: PuntoCritico, material: Material,
                       seccion: Seccion, altura_relleno: float
                       ) -> ResultadoEstructural:
    """
    Clase minima del tubo de concreto reforzado por el METODO INDIRECTO de
    AASHTO LRFD 12.10.4.3 (servicio) y relleno maximo de esa clase:

        W_E = VAF B_c (gamma_s H_rel + gamma_p e_paq)      (12.10.2.1-1)
        W_F = gamma_w pi D^2 / 4                           (12.10.2.2)
        W_L = P_L min(l_w, B_c)                            (12.10.2.3)
        D   = [(W_E + W_F)/B_FE + W_L/B_FLL] / S_i  [x 1.10 en el Tipo 1]
                                                          (12.10.4.3.1-1)

    D en N/m/mm (W en N/m, S_i en mm), contra la D-load de 0.3 mm de la
    clase (AASHTO M 170M). Gobierna el vehiculo de mayor W_L, no el de mayor
    presion.

    QUE PASA CUANDO NINGUNA CLASE OFRECIDA ALCANZA, que son dos casos y no
    uno (auditoria de T-5):

      * FALTA transcribir una clase superior que la norma SI tabula para
        este diametro -> `DatoFaltanteError` sobre
        'clases_producto_por_relleno', nombrando las clases que faltan y lo
        que lo destraba (un ejemplar legible de AASHTO M 170M o ASTM C76M).
        Es decision del dueño del proyecto (2026-11-12) BLOQUEAR: la
        solucion de ingenieria de un tubo que pide mas que la Clase II es
        una clase superior, no un tubo mayor para esquivarla. (La version
        anterior de este docstring lo justificaba con «subir de diametro no
        la baja», y es falso en general: con relleno somero la D-load BAJA
        al crecer el diametro --52.2, 41.7 y 36.0 N/m/mm en 0.90, 1.20 y
        1.50 m con 0.50 m de relleno--; solo sube con relleno profundo.)
      * estan transcritas TODAS las superiores y ni la mayor alcanza -> no
        falta ningun dato: el tubo NO CUMPLE (`Verificacion` con
        `cumple=False` frente a la mayor clase), y MD prueba el escalon o el
        material siguiente.

    Y DESDE VE-3.12 UN TERCER CASO, el de la clase BLOQUEADA (decision 7 del
    dueño, 2026-11-17): si la menor clase que alcanza es una que el ejemplar
    de M 170M no deja verificar a este diametro (`clases_bloqueadas_para`: la
    Clase IV por encima de 300 mm), `DatoFaltanteError` nombrando la clase y
    lo legible; no se le da la clase siguiente para esquivarla. Las D-load de
    III a V vienen de la tabla de ASTM C76 de un ejemplo resuelto del USACE
    (fuente secundaria [C]) y el paso lo dice en su umbral y en sus citas.

    EL CONTRASTE ACPA SE IMPRIME AL LADO con poco relleno, y no rige
    (`_contraste_acpa`, decision 6 del dueño).

    EL TIPO 4 SE IMPRIME AL LADO, como contraste que no rige (decision del
    dueño): la D-load, la clase y el relleno maximo que saldrian sin
    compactacion exigida, para que se vea cuanto pesa la instalacion.
    """
    D = seccion.altura
    t = espesor_pared(material, D)
    B_c = seccion.ancho_exterior(t)
    e_paq = espesor_del_paquete(punto)
    H_rel = _finito_positivo("altura_relleno", altura_relleno, punto.id)
    gamma_s, gamma_p, proc_gamma = pesos_especificos_de_carga(
        piso_tubo_concreto=True)
    tipo = ca.valor(CRITERIO_INSTALACION_CONCRETO)
    if tipo not in _CN.VAF_INSTALACION_ESTANDAR:
        raise DatoInvalidoError(
            campo=CRITERIO_INSTALACION_CONCRETO, valor=tipo, id_punto=punto.id,
            motivo=f"tiene que ser uno de {sorted(_CN.VAF_INSTALACION_ESTANDAR)}")
    S_i_mm = D * MILIMETROS_POR_METRO
    D_pulg = S_i_mm / PULGADA_EN_MM
    W_F = GAMMA_AGUA_KN_M3 * seccion.area_llena
    # La Tabla 12.10.4.3.2c-1 tiene dos filas de B_FLL. Hasta VE-4f la de
    # «< 2.0 ft» no se alcanzaba (con menos de 2.0 ft `carga_viva_enterrada`
    # se detenia); desde VE-4f el tubo con 1.0 a 2.0 ft hasta la rasante
    # tiene carga viva (la franja de 4.6.2.10.2) y la lee: `_b_fll(cv)`.
    def _b_fll(cv) -> float:
        return _interpolar(D_pulg, _CN.BFLL_DIAMETROS_PULG,
                           _CN.BFLL_RELLENO_MENOR_2_PIES if cv.relleno_somero
                           else _CN.BFLL_RELLENO_DESDE_2_PIES)

    def _efecto(P_L: float, l_w: float) -> float:
        return P_L * min(l_w, B_c)

    def _factores(tipo_inst: str):
        return (_CN.VAF_INSTALACION_ESTANDAR[tipo_inst],
                _interpolar(D_pulg, _CN.BFE_DIAMETROS_PULG,
                            _CN.BFE_POR_TIPO[tipo_inst]),
                (_CN.FACTOR_INSTALACION_TIPO_1
                 if tipo_inst == INSTALACION_TIPO_1 else 1.0))

    def _demanda(H: float, tipo_inst: str):
        VAF_i, B_FE_i, factor_i = _factores(tipo_inst)
        cv = carga_viva_enterrada(
            H=H + e_paq, D_i=D, D_E=H, conducto=CONDUCTO_TUBO_CONCRETO,
            id_punto=punto.id, efecto=_efecto,
            efecto_descripcion="W_L = P_L min(l_w, B_c), kN/m",
            ancho_del_conducto=B_c)
        W_E = VAF_i * B_c * (gamma_s * H + gamma_p * e_paq)
        # W_L es el EFECTO del vehiculo que gobierna: P_L min(l_w, B_c) con
        # la rueda distribuida, y con el relleno somero la suma de lo que de
        # cada eje cae sobre el tubo (VE-4f).
        W_L = cv.efecto
        D_req = (factor_i * ((W_E + W_F) / B_FE_i + W_L / _b_fll(cv))
                 * N_POR_KN / S_i_mm)
        return D_req, W_E, W_L, cv

    VAF, B_FE, factor_tipo = _factores(tipo)
    D_req, W_E, W_L, cv = _demanda(H_rel, tipo)
    B_FLL = _b_fll(cv)
    ofrecidas, faltan = clases_de_concreto_para(D)
    bloqueadas = clases_bloqueadas_para(D)
    transcritas = _clases_transcritas()
    candidatas = {c: transcritas[c] for c in CLASES_M170M
                  if c in ofrecidas or c in bloqueadas}

    def _clase_minima(D_pedida: float):
        # --- VE-3.12 --- La menor de las ofrecidas Y de las bloqueadas: si la
        # que alcanza es una bloqueada, el tubo se detiene (abajo) en vez de
        # recibir la siguiente para esquivarla (decision 7 del dueño).
        return next(((c, d) for c, d in candidatas.items()
                     if d + TOL_UMBRAL_NORMATIVO >= D_pedida), None)

    elegida = _clase_minima(D_req)
    if elegida is not None and elegida[0] in bloqueadas:
        legible = _CN.DIAMETRO_MAX_LEGIBLE_POR_CLASE_M170M_MM[elegida[0]]
        raise DatoFaltanteError(
            CRITERIO_CLASES_PRODUCTO, id_punto=punto.id,
            detalle=(f"el tubo de concreto de {D:.2f} m pide una D-load de "
                     f"{D_req:.1f} N/m/mm (metodo indirecto, AASHTO LRFD "
                     f"12.10.4.3, instalacion {tipo}) y la clase que la "
                     f"alcanza es la Clase {elegida[0]} "
                     f"({elegida[1]:.1f} N/m/mm), que esta BLOQUEADA a este "
                     "diametro: de su tabla de AASHTO M 170M el ejemplar de "
                     f"normas/ solo deja leer hasta {legible} mm, y no se "
                     "inventa hasta donde la norma la tabula con pared B "
                     "(decision del dueño, 2026-11-17). Se destraba con un "
                     "ejemplar legible de AASHTO M 170M (el vigente) o de "
                     "ASTM C76M. No se resuelve con otra clase ni subiendo "
                     "de diametro"))
    if elegida is None and (faltan or not ofrecidas):
        nombres = ", ".join(faltan) if faltan else "ninguna transcrita"
        raise DatoFaltanteError(
            CRITERIO_CLASES_PRODUCTO, id_punto=punto.id,
            detalle=(f"el tubo de concreto de {D:.2f} m pide una D-load de "
                     f"{D_req:.1f} N/m/mm (metodo indirecto, AASHTO LRFD "
                     f"12.10.4.3, instalacion {tipo}) y la mayor clase "
                     f"transcrita para ese diametro "
                     f"({', '.join(ofrecidas) or 'ninguna'}) no la alcanza. "
                     f"FALTA la D-load de 0.3 mm de las Clases {nombres} de "
                     "AASHTO M 170M, que la norma tabula para este diametro "
                     "y no se leen en el ejemplar de normas/. Se destraba "
                     "con un ejemplar legible de AASHTO M 170M (el vigente) "
                     "o de ASTM C76M, transcribiendolas en "
                     "'clases_producto_por_relleno' (entrada que debe "
                     "conseguir el dueño del proyecto: "
                     "docs/contrato_entradas.md). No se resuelve subiendo de "
                     "diametro: lo que el punto pide es una clase superior"))
    cumple = elegida is not None
    clase, D_clase = elegida if cumple else list(ofrecidas.items())[-1]
    desde_usace = clase in CLASES_DESDE_USACE
    contraste = _contraste_acpa(
        D=D, B_c=B_c, H_total=H_rel + e_paq, cv=cv, W_L=W_L, W_E=W_E,
        W_F=W_F, B_FE=B_FE, B_FLL=B_FLL, S_i_mm=S_i_mm,
        factor_tipo=factor_tipo, D_req=D_req, clase_minima=_clase_minima,
        clase_que_rige=(f"Clase {clase}" if cumple else
                        f"ninguna (ni la Clase {clase})"))
    p_tierra = paso(
        "F8.CARGA_TIERRA", codigo="F8.EV",
        que="Carga de tierra sobre el tubo de concreto (instalacion estandar)",
        formula=("W_E = VAF B_c (gamma_s H_rel + gamma_p e_paq); "
                 "W_F = gamma_w pi D^2/4"),
        formula_cita_id="AASHTO_LRFD_9.12.10.2.1#VAF",
        citas_textuales=("AASHTO_LRFD_9.12.10.2.1#PESO_MIN",
                         "AASHTO_LRFD_9.12.10.2.2", "MP.2.4.2.1#PESOS"),
        sustitucion=(
            Magnitud("VAF", VAF, "", f"Tabla 12.10.2.1-3, instalacion {tipo} "
                     f"('{CRITERIO_INSTALACION_CONCRETO}' [A])",
                     cifras=CIFRAS_FACTOR),
            Magnitud("B_c", B_c, "m", "diametro exterior, D + 2t",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("gamma_s", gamma_s, "kN/m3", proc_gamma,
                     cifras=CIFRAS_FACTOR),
            Magnitud("H_rel", H_rel, "m", "subrasante menos clave fisica "
                     "(M5.altura_relleno_sobre_clave)", cifras=CIFRAS_MAGNITUD),
            Magnitud("gamma_p", gamma_p, "kN/m3", "Manual de Puentes Tabla "
                     "2.4.2.1-1, superficie de rodadura, 0.140 kcf [N]",
                     cifras=CIFRAS_FACTOR),
            Magnitud("e_paq", e_paq, "m", "rasante menos subrasante",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("W_F", W_F, "kN/m", "peso del agua que llena el tubo "
                     "(12.10.2.2)", cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("W_E", W_E, "kN/m", "carga de tierra sin factorar",
                           cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=(
            "Que la fila «Arena, limo o arcilla compactado» describa el "
            "relleno y la de las superficies de rodadura el paquete es "
            "lectura del proyecto; los dos pesan en el prisma porque la Eq. "
            "12.10.2.1-1 no distingue capas."))
    nota_clases = (
        "Solo la D-load de la Clase II es legible en el ejemplar de M 170M; "
        "las de las Clases III, IV y V vienen de la tabla de ASTM C76 de un "
        "ejemplo resuelto del USACE EM 1110-2-2902 (B-7), fuente "
        "SECUNDARIA [C] (decision del dueño, 2026-11-17). La clase elegida es "
        "la menor de las transcritas que la norma tabula con pared B para "
        "este diametro (la Clase I solo desde 1500 mm; la V con pared B solo "
        "hasta 1200 mm) y que el ejemplar deja verificar (la IV, por encima "
        "de 300 mm, BLOQUEADA: si es la que alcanza, el tubo se detiene con "
        "el dato que falta). "
        + ("Un tubo que pida mas que la mayor transcrita se detiene diciendo "
           "que clases faltan. " if faltan else
           "Si ninguna de las ofrecidas alcanza, el tubo no cumple. "))
    v = _verificacion_f8(paso("F8.CLASE_CONCRETO", **_campos_f8(
            codigo=CODIGO_CLASE,
            que=f"Clase del tubo de concreto: D-load requerida frente a la Clase {clase}",
            formula="D = [(W_E + W_F)/B_FE + W_L/B_FLL] / S_i"
                 + (" x 1.10 (Tipo 1)" if factor_tipo != 1.0 else ""),
            formula_cita_id="AASHTO_LRFD_9.12.10.4.3.1",
            sust=(Magnitud("W_E", W_E, "kN/m", "paso F8.EV", cifras=CIFRAS_MAGNITUD),
              Magnitud("W_F", W_F, "kN/m", "paso F8.EV", cifras=CIFRAS_MAGNITUD),
              Magnitud("W_L", W_L, "kN/m", f"P_L del {cv.vehiculo} (paso "
                       "F8.LL, el de mayor W_L) por "
                       + ("lo que de cada eje cae sobre el tubo, min(B_c, l) "
                          "+ min(l, B_c - s_a) (relleno somero, franja de "
                          "4.6.2.10.2)" if cv.relleno_somero else
                          "min(l_w, B_c): la parte del area cargada que cae "
                          "sobre el tubo"),
                       cifras=CIFRAS_MAGNITUD),
              Magnitud("B_FE", B_FE, "", f"Tabla 12.10.4.3.2a-1, {tipo}, "
                       f"interpolado en D = {D_pulg:.1f} in",
                       cifras=CIFRAS_FACTOR),
              Magnitud("B_FLL", B_FLL, "", "Tabla 12.10.4.3.2c-1, fila "
                       + ("«< 2.0 ft»" if cv.relleno_somero else
                          "«>= 2.0 ft»"), cifras=CIFRAS_FACTOR),
              Magnitud("S_i", S_i_mm, "mm", "diametro interior",
                       cifras=CIFRAS_MAGNITUD)),
            obtenido=Magnitud("D", D_req, "N/m/mm", "D-load requerida a grieta "
                          "de 0.3 mm", cifras=CIFRAS_MAGNITUD),
            admisible=D_clase,
            unidad="N/m/mm",
            cita_umbral="AASHTO_LRFD_9.12.10.4.3.1#DLOAD",
            descripcion_umbral=(
                f"D-load de 0.3 mm de la Clase {clase} (ASTM C76M / AASHTO "
                "M 170M, por la tabla del ejemplo resuelto del USACE EM "
                "1110-2-2902, B-7 [C], fuente secundaria)" if desde_usace else
                f"D-load de 0.3 mm de la Clase {clase} (AASHTO M 170M)"),
            aplicacion="umbral duro: la clase elegida es la MINIMA transcrita "
                    "cuya D-load alcanza la requerida; la EG-2013 manda "
                    "indicarla en el Proyecto",
            criterio=CRITERIO_CLASES_PRODUCTO,
            cumple=cumple,
            margen=D_clase - D_req,
            explicacion=(f"el tubo es Clase {clase} o superior" if cumple else
                         f"ni la Clase {clase}, la mayor de AASHTO M 170M "
                         "para este diametro, alcanza la D-load requerida"),
            citas=((CITA_CLASES_USACE, "AASHTO_M170M.T5#PARED_B",
                    "AASHTO_M170M.T4#LEGIBLE") if desde_usace else ())
              + ("AASHTO_M170M.T2#DLOAD", "AASHTO_M170M.T1#DIAMETROS",
                   "EG2013.506.02#CLASE", "AASHTO_LRFD_9.12.10.2.3",
                   "AASHTO_LRFD_9.12.10.4.3.2a", "AASHTO_LRFD_9.12.10.4.3.2c",
                   "AASHTO_LRFD_9.T12.10.2.1-1", "EG2013.506.07",
                   "EG2013.506.10", "EG2013.T205-01",
                   "EG2013.205.12#COMPACTACION")
        + (("AASHTO_LRFD_9.12.10.4.3.1#TIPO1",) if factor_tipo != 1.0 else ()),
            nota=nota_clases
              + ("CON POCO RELLENO, el paso F8.ACPA imprime al lado el "
                 "contraste de la practica ACPA (longitud efectiva de DD 1), "
                 "que NO GOBIERNA. " if contraste is not None else "")
              + "W_L = P_L min(l_w, B_c) es la lectura del proyecto de la "
              "carga viva «uniformly distributed across the top of the "
              "pipe». La instalacion es una ELECCION del proyecto "
              f"('{CRITERIO_INSTALACION_CONCRETO}' = {tipo}): que la "
              "compactacion que el EG-2013 exige corresponde al Tipo 3 de la "
              "Tabla 12.10.2.1-1 es lectura del proyecto, con la condicion "
              "que la ficha del criterio declara; el paso F8.TIPO4 imprime "
              "al lado lo que saldria con el Tipo 4.")),
        numeral=NUMERAL_F8_CLASE)
    pasos: List[PasoDeMemoria] = [cv.paso, p_tierra]
    avisos_acpa: Tuple[str, ...] = ()
    if contraste is not None:
        pasos.append(contraste[0])
        avisos_acpa = (contraste[1],)
    H_max = None
    if cumple:
        def _margen(H: float) -> float:
            return D_clase - _demanda(H, tipo)[0]

        H_max = _relleno_maximo(_margen, H_rel, D, punto.id)
        pasos.append(paso(
            "F8.CLASE_CONCRETO", codigo="F8.HMAX",
            que=f"Relleno maximo sobre la clave con la Clase {clase}",
            formula="H_max: D(H_max) = D-load de la clase",
            sustitucion=(Magnitud("D_clase", D_clase, "N/m/mm",
                                  "'clases_producto_por_relleno' [C]",
                                  cifras=CIFRAS_MAGNITUD),),
            resultado=Magnitud("H_max", H_max, "m", "relleno sobre la clave "
                               "hasta la subrasante, con el mismo paquete y "
                               "la misma instalacion", cifras=CIFRAS_MAGNITUD),
            citas_textuales=("AASHTO_LRFD_9.12.10.4.3.1",)))
    if tipo != INSTALACION_TIPO_4:
        pasos.extend(_contraste_tipo_4(
            D=D, D_pulg=D_pulg, H_rel=H_rel, demanda=_demanda,
            clase_minima=_clase_minima, factores=_factores,
            id_punto=punto.id))
    return ResultadoEstructural(
        material=TipoMaterial.CONCRETO_REFORZADO.value, H_relleno_m=H_rel,
        e_paquete_m=e_paq, H_total_m=H_rel + e_paq,
        seleccion=f"Clase {clase}" if cumple else "", relleno_maximo_m=H_max,
        verificaciones=(v,), pasos=tuple(pasos),
        avisos=_aviso_de_carga_viva_despreciada(cv) + avisos_acpa,
        diferido=(DIFERIDO_CONCRETO_DIRECTO,)
        + ((DIFERIDO_CLASES_M170M,)
           if len(_clases_transcritas()) < len(CLASES_M170M) else ()))


def _contraste_acpa(*, D: float, B_c: float, H_total: float, cv, W_L: float,
                    W_E: float, W_F: float, B_FE: float, B_FLL: float,
                    S_i_mm: float, factor_tipo: float, D_req: float,
                    clase_minima, clase_que_rige: str):
    """
    El CONTRASTE DE LA PRACTICA ACPA, que NO GOBIERNA (VE-3.12, decision 6 del
    dueño, 2026-11-17): con menos relleno total hasta la rasante que
    'relleno_max_contraste_acpa_m', la carga viva repartida ademas en la
    longitud efectiva de ACPA Design Data 1 (2009), Eq. [2]:

        L_e = w_w + 1.75 (3/4) B_c        W_L,ACPA = W_L w_w / L_e

    aplicada sobre el reparto de la 9.a ed. (w_w es la dimension del area
    cargada a lo largo del tubo, la «L» de ACPA), y la clase que saldria con
    ella. La que rige es la de la lectura literal de AASHTO LRFD 9.a ed.
    12.10.2.3 (sin L_e: ficha VE3-04); el contraste existe para que el
    revisor vea cuanto pesa esa lectura con poco relleno (una o dos clases en
    tubos de 0.60 a 0.90 m con menos de ~1.0 m). Devuelve (paso, aviso), o
    None por encima del umbral o si la carga viva se desprecio.
    """
    if cv.relleno_somero:
        # --- VE-4f --- La L_e de ACPA corrige el reparto de la rueda
        # distribuida (3.6.1.2.6b); con relleno somero rige la franja de
        # 4.6.2.10.2, que ya reparte el eje a lo largo del tubo en E: sumarle
        # L_e contaria dos veces ese reparto. No hay contraste.
        return None
    umbral = ca.valor(CRITERIO_UMBRAL_ACPA)
    if cv.despreciada or not H_total < umbral:
        return None
    w_w = cv.w_w_m
    L_e = w_w + (_CN.COEFICIENTE_LONGITUD_EFECTIVA_ACPA
                 * _CN.FRACCION_DEL_RISE_LONGITUD_EFECTIVA_ACPA * B_c)
    W_L_acpa = W_L * w_w / L_e
    D_acpa = (factor_tipo * ((W_E + W_F) / B_FE + W_L_acpa / B_FLL)
              * N_POR_KN / S_i_mm)
    elegida = clase_minima(D_acpa)
    texto = (f"Clase {elegida[0]}" if elegida is not None else
             "ninguna de las transcritas")
    p = paso(
        "F8.CLASE_CONCRETO", codigo=CODIGO_CONTRASTE_ACPA,
        que=("Contraste con la practica ACPA (longitud efectiva L_e de DD 1, "
             "Eq. [2]): carga viva y D-load -- NO GOBIERNA"),
        formula=("L_e = w_w + 1.75 (3/4) B_c; W_L,ACPA = W_L w_w / L_e; "
                 "D_ACPA = [(W_E + W_F)/B_FE + W_L,ACPA/B_FLL] / S_i"),
        formula_cita_id="AASHTO_LRFD_9.12.10.4.3.1",
        citas_textuales=("AASHTO_LRFD_9.12.10.2.3",
                         "AASHTO_LRFD_9.12.10.4.3.2c"),
        sustitucion=(
            Magnitud("W_L", W_L, "kN/m", "la que rige (paso F8.CLASE), sin "
                     "L_e", cifras=CIFRAS_MAGNITUD),
            Magnitud("w_w", w_w, "m", f"area cargada a lo largo del tubo, "
                     f"{cv.vehiculo} (paso F8.LL)", cifras=CIFRAS_MAGNITUD),
            Magnitud("B_c", B_c, "m", "diametro exterior (el R_o de ACPA)",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("L_e", L_e, "m", "ACPA DD 1 (2009), Eq. [2] [C], solo "
                     "para este contraste", cifras=CIFRAS_MAGNITUD),
            Magnitud("D_ACPA", D_acpa, "N/m/mm", "D-load con W_L,ACPA",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("clase_ACPA", texto, "", "la menor de las transcritas "
                     "que alcanzaria D_ACPA")),
        resultado=Magnitud("W_L_ACPA", W_L_acpa, "kN/m", "carga viva por "
                           "metro con la longitud efectiva de ACPA",
                           cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=(
            "CONTRASTE QUE NO GOBIERNA (decision del dueño, 2026-11-17). La "
            "carga viva que rige es la lectura literal de AASHTO LRFD 9.a "
            "ed., que reparte la carga «across the top of the pipe» sin "
            "longitud efectiva y compensa el reparto a lo largo del tubo con "
            "0.06 D_i y B_FLL (C12.10.4.3.2c); la practica ACPA le suma "
            "L_e. Se imprime con menos de "
            f"{umbral:.2f} m de relleno hasta la rasante "
            f"('{CRITERIO_UMBRAL_ACPA}' [A]), donde las dos lecturas pueden "
            "dar clases distintas."))
    aviso = (
        f"F8 (contraste ACPA, NO GOBIERNA): con {H_total:.2f} m de relleno "
        f"hasta la rasante el tubo de {D:.2f} m pide {D_req:.1f} N/m/mm con "
        f"la lectura literal de AASHTO LRFD 9.a ed. ({clase_que_rige}); con "
        f"la longitud efectiva de ACPA DD 1 (L_e = {L_e:.2f} m) pediria "
        f"{D_acpa:.1f} N/m/mm ({texto}). Rige la primera")
    return p, aviso


def _contraste_tipo_4(*, D: float, D_pulg: float, H_rel: float, demanda,
                      clase_minima, factores, id_punto
                      ) -> Tuple[PasoDeMemoria, ...]:
    """
    Los pasos del CONTRASTE con la instalacion Tipo 4 (no rige): la D-load,
    la clase y el relleno maximo del mismo tubo sin compactacion exigida.
    Decision del dueño del proyecto (2026-11-12): que la memoria imprima al
    lado del Tipo adoptado lo que pesa la compactacion.
    """
    VAF_4, B_FE_4, _ = factores(INSTALACION_TIPO_4)
    D_4 = demanda(H_rel, INSTALACION_TIPO_4)[0]
    elegida_4 = clase_minima(D_4)
    H_max_4 = None
    if elegida_4 is not None:
        H_max_4 = _relleno_maximo(
            lambda H: elegida_4[1] - demanda(H, INSTALACION_TIPO_4)[0],
            H_rel, D, id_punto)
    texto_clase = (f"Clase {elegida_4[0]}" if elegida_4 is not None else
                   "ninguna de las clases transcritas alcanza")
    if (elegida_4 is not None
            and elegida_4[0] in clases_bloqueadas_para(D)):
        texto_clase += " (bloqueada a este diametro)"
    citas = ("AASHTO_LRFD_9.T12.10.2.1-1", "AASHTO_LRFD_9.T12.10.2.1-1#PROCTOR",
             "EG2013.506.07", "EG2013.506.10", "EG2013.T205-01",
             "EG2013.205.12#COMPACTACION")
    p_d = paso(
        "F8.CLASE_CONCRETO", codigo=CODIGO_PASO_TIPO4,
        que=("Contraste con la instalacion Tipo 4 (sin compactacion "
             "exigida): D-load requerida -- NO RIGE"),
        formula="D_T4 = [(W_E,T4 + W_F)/B_FE,T4 + W_L/B_FLL] / S_i",
        formula_cita_id="AASHTO_LRFD_9.12.10.4.3.1",
        citas_textuales=citas,
        sustitucion=(
            Magnitud("VAF_T4", VAF_4, "", "Tabla 12.10.2.1-3, Tipo 4",
                     cifras=CIFRAS_FACTOR),
            Magnitud("B_FE_T4", B_FE_4, "", "Tabla 12.10.4.3.2a-1, Tipo 4, "
                     f"en D = {D_pulg:.1f} in", cifras=CIFRAS_FACTOR),
            Magnitud("clase_T4", texto_clase, "", "la menor de las "
                     "transcritas que alcanzaria la D-load del Tipo 4")),
        resultado=Magnitud("D_T4", D_4, "N/m/mm", "D-load requerida a grieta "
                           "de 0.3 mm si la instalacion fuera de Tipo 4",
                           cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=(
            "Informativo. El Tipo 4 es la instalacion que no exige "
            "compactar: verificar con el es valido para cualquier relleno "
            "compactado y es la cota conservadora de la ventana de "
            f"'{CRITERIO_INSTALACION_CONCRETO}'. Se imprime para que se vea "
            "cuanto pesa en la clase y en el relleno maximo la compactacion "
            "que el EG-2013 exige."))
    if H_max_4 is None:
        return (p_d,)
    p_h = paso(
        "F8.CLASE_CONCRETO", codigo=CODIGO_PASO_HMAX_TIPO4,
        que=(f"Contraste con la instalacion Tipo 4: relleno maximo con la "
             f"{texto_clase} -- NO RIGE"),
        formula="H_max,T4: D_T4(H_max,T4) = D-load de la clase",
        citas_textuales=citas,
        sustitucion=(Magnitud("D_clase", elegida_4[1], "N/m/mm",
                              "'clases_producto_por_relleno' [C]",
                              cifras=CIFRAS_MAGNITUD),),
        resultado=Magnitud("H_max_T4", H_max_4, "m", "relleno sobre la clave "
                           "hasta la subrasante si la instalacion fuera de "
                           "Tipo 4", cifras=CIFRAS_MAGNITUD))
    return (p_d, p_h)


# ---------------------------------------------------------------------------
# Tuberia metalica corrugada: AASHTO LRFD 12.7.2 (LRFD), con plancha
# ---------------------------------------------------------------------------

def espesor_minimo_tmc_eg2013(D: float) -> Optional[float]:
    """
    Espesor minimo de la plancha por la Tabla 507-01 del EG-2013, m: la fila
    del diametro tabulado inmediato SUPERIOR (lectura del proyecto, del lado
    del mayor espesor); None por encima de la ultima fila (1.80 m), donde la
    tabla no dice nada y manda el calculo.
    """
    D_mm = D * MILIMETROS_POR_METRO
    for d_mm, t_mm in sorted(_CN.ESPESOR_MIN_TMC_EG2013_MM.items()):
        if D_mm <= d_mm + TOL_UMBRAL_NORMATIVO:
            return t_mm / MILIMETROS_POR_METRO
    return None


def tension_critica_de_pandeo(*, S_mm: float, r_mm: float, E: float,
                              F_u: float, k: float) -> float:
    """
    f_cr de AASHTO LRFD 12.7.2.4, MPa (la misma forma que ASTM A796 ecs. 5
    y 6): si S < (r/k) sqrt(24 E/F_u), f_cr = F_u - (F_u k S/r)^2/(48 E); si
    no, f_cr = 12 E/(k S/r)^2.
    """
    esbeltez = k * S_mm / r_mm
    if S_mm < (r_mm / k) * math.sqrt(24 * E / F_u):   # literal-ok: 24 de la Eq. 12.7.2.4-1
        return F_u - (F_u * esbeltez) ** 2 / (48 * E)  # literal-ok: 48 de la Eq. 12.7.2.4-1
    return 12 * E / esbeltez ** 2                      # literal-ok: 12 de la Eq. 12.7.2.4-2


def area_requerida_asd_a796(*, S_m: float, P_kPa: float, r_mm: float,
                            f_y: float = _CN.A796_FY_MPA,
                            f_u: float = _CN.A796_FU_MPA,
                            E: float = _CN.A796_E_MPA,
                            k: float = _CN.A796_K_SUELO,
                            SF: float = _CN.A796_SF_AREA
                            ) -> Tuple[float, float, float]:
    """
    CONTRASTE por tensiones admisibles de ASTM A796/A796M-13, num. 8 (NO
    RIGE): T = P S/2 (ec. 3); A = T SF / f, con f = min(f_y, f_c) y f_c de
    las ecs. 5 y 6. Devuelve (T en kN/m, f en MPa, A en mm2/mm). Los valores
    por defecto son los de A796 en SI (num. 4: f_y 225, f_u 310, E 200 000
    MPa, k 0.22; num. 8.1.1.2: SF 2); el dorado de un expediente de
    referencia pasa los suyos.
    """
    T = P_kPa * S_m / 2
    f_c = tension_critica_de_pandeo(S_mm=S_m * MILIMETROS_POR_METRO,
                                    r_mm=r_mm, E=E, F_u=f_u, k=k)
    f = min(f_y, f_c)
    return T, f, T * SF / f


def _planchas_a_probar(D: float, fabricacion: str, id_punto,
                       plancha_del_material: str = ""):
    """
    Las planchas de la corrugacion ADOPTADA que la Fase 8 recorre, de menor
    a mayor espesor: desde el mayor de la plancha adoptada y del minimo de la
    Tabla 507-01 del EG-2013, y solo las que la fabricacion declarada puede
    hacer (una remachada necesita su costura en la tabla de A796).

    --- VE-5 (m8), item 23 --- La «adoptada» es la del MATERIAL cuando la
    lleva (`Material.plancha_tmc`, la que MD le devolvio), y si no la del
    criterio.
    """
    clave_adopt = plancha_del_material or ca.valor(CRITERIO_PLANCHA_TMC)
    if clave_adopt not in _CN.TMC_PLANCHA_CORRUGADA:
        raise DatoInvalidoError(
            campo=CRITERIO_PLANCHA_TMC, valor=clave_adopt, id_punto=id_punto,
            motivo="tiene que ser una clave de TMC_PLANCHA_CORRUGADA")
    adopt = _CN.TMC_PLANCHA_CORRUGADA[clave_adopt]
    t_min_eg = espesor_minimo_tmc_eg2013(D)
    piso = max(adopt["espesor_m"], t_min_eg or 0.0)
    remache = REMACHE_DE_FABRICACION.get(fabricacion)
    planchas = []
    for clave, f in sorted(_CN.TMC_PLANCHA_CORRUGADA.items(),
                           key=lambda kf: kf[1]["espesor_m"]):
        if f["corrugacion"] != adopt["corrugacion"]:
            continue
        if f["espesor_m"] + TOL_UMBRAL_NORMATIVO < piso:
            continue
        SS = (None if remache is None
              else _CN.COSTURA_REMACHADA_TMC_KN_M[clave][remache])
        if remache is not None and SS is None:
            continue           # la tabla dice «. . .»: no se fabrica asi
        planchas.append((clave, f, SS))
    if not planchas:
        raise DatoFaltanteError(
            "resistencia_costura_tmc", id_punto=id_punto,
            detalle=(f"la corrugacion {adopt['corrugacion']} no tiene en ASTM "
                     f"A796 ninguna plancha de {piso * MILIMETROS_POR_METRO:.2f}"
                     f" mm o mas con costura {fabricacion}: declare otra "
                     "fabricacion ('fabricacion_tmc') u otra corrugacion "
                     f"('{CRITERIO_PLANCHA_TMC}')"))
    return clave_adopt, adopt, t_min_eg, piso, planchas


def verificar_tmc(*, punto: PuntoCritico, material: Material,
                  seccion: Seccion, altura_relleno: float
                  ) -> ResultadoEstructural:
    """
    Calibre de la tuberia metalica corrugada por AASHTO LRFD 12.7.2 (LRFD):

        T_L = P_FD S/2 + P_FL C_L F_1/2                     (12.7.2.2-1)
        P_FD = eta (gamma_EV P_sp + gamma_WA P_w); P_FL = eta gamma_LL P_L
        A >= T_L / (phi min(F_y, f_cr))                      (12.7.2.3, .4)
        phi_s SS >= T_L      (costura longitudinal)           (12.7.2.5)
        FF = S^2 / (E_m I) <= limite de la corrugacion        (12.5.6.1)

    PROGRESION DE PLANCHA dentro de la corrugacion adoptada, desde el mayor
    de la plancha adoptada ('corrugacion_y_espesor_tmc') y del minimo de la
    Tabla 507-01 del EG-2013, hasta la primera que cumple las tres. Si
    ninguna cumple, las tres verificaciones salen con la ultima plancha
    probada y su veredicto, y MD rechaza el escalon.

    La plancha que la Fase 8 elige puede ser mas gruesa que la adoptada, que
    es con la que M2 armo la envolvente geometrica de 7.A y V7 (ficha T4-08):
    el relleno sobre la clave se recalcula para cada plancha (una plancha
    mas gruesa sube la clave) y, si la elegida no es la adoptada, el
    resultado lo AVISA para que el proyectista la declare.
    """
    D = seccion.altura
    fabricacion = ca.valor(CRITERIO_FABRICACION_TMC)
    if fabricacion == FABRICACION_EMPERNADA:
        raise DatoFaltanteError(
            "resistencia_costura_empernada_tmc", id_punto=punto.id,
            detalle=("'fabricacion_tmc' declara costura longitudinal "
                     "EMPERNADA y ninguna fuente del repositorio tabula su "
                     "resistencia (ASTM A796 Tablas 5 y 7 y AASHTO Tabla A12-7 "
                     "son de costura remachada). Se destraba con la "
                     "resistencia que garantice el fabricante, o declarando "
                     "otra fabricacion"))
    if fabricacion != FABRICACION_HELICOIDAL and \
            fabricacion not in REMACHE_DE_FABRICACION:
        raise DatoInvalidoError(campo=CRITERIO_FABRICACION_TMC,
                                valor=fabricacion, id_punto=punto.id,
                                motivo="fabricacion no reconocida")
    clave_adopt, adopt, t_min_eg, piso, planchas = _planchas_a_probar(
        D, fabricacion, punto.id, material.plancha_tmc)
    t_env_adopt = espesor_pared(material, D)
    e_paq = espesor_del_paquete(punto)
    H_rel0 = _finito_positivo("altura_relleno", altura_relleno, punto.id)
    gamma_s, gamma_p, proc_gamma = pesos_especificos_de_carga(
        piso_tubo_concreto=False)
    eta = _eta()
    gamma_EV, fila_EV = _gamma_ev_max(material)
    gamma_WA = _gamma_de_la_combinacion(CARGA_AGUA, EXTREMO_DESESTABILIZANTE)
    gamma_LL = _gamma_ll()
    E_m, F_y, F_u = _CN.ACERO_TMC_EM_MPA, _CN.ACERO_TMC_FY_MPA, _CN.ACERO_TMC_FU_MPA
    phi = _CN.PHI_AREA_Y_PANDEO_TMC
    phi_s = _CN.PHI_COSTURA_LONGITUDINAL_TMC
    k = _CN.K_RIGIDEZ_SUELO_TMC
    FF_lim = _CN.FF_LIMITE_ACERO_MM_N[adopt["corrugacion"]]
    S_mm = D * MILIMETROS_POR_METRO
    nf = punto.NF_profundidad_m

    F_min = max(_CN.F_MIN_NUMERADOR_M / D, 1.0)

    def _efecto(P_L: float, l_w: float) -> float:
        return P_L * min(l_w, D) * max(0.75 * D / l_w, F_min)  # literal-ok: el 0.75 de la Eq. 12.7.2.2-3

    def _empuje(H_rel: float, t_env: float):
        cv = carga_viva_enterrada(
            H=H_rel + e_paq, D_i=D, D_E=H_rel, conducto=CONDUCTO_FLEXIBLE,
            id_punto=punto.id, efecto=_efecto,
            efecto_descripcion="P_L C_L F_1, kN/m (Eqs. 12.7.2.2-2 a -4)")
        P_sp = gamma_s * H_rel + gamma_p * e_paq
        H_w = D / 2 + t_env       # agua hasta la clave: la hipotesis de V7
        if nf is not None:
            centro = punto.cota_subrasante - H_rel - t_env - D / 2
            H_w = max(H_w, (punto.cota_terreno - nf) - centro)
        P_w = GAMMA_AGUA_KN_M3 * H_w
        P_FD = eta * (gamma_EV * P_sp + gamma_WA * P_w)
        P_FL = eta * gamma_LL * cv.P_L_kPa
        if cv.despreciada:
            C_L, F_1 = 0.0, 0.0
        else:
            C_L = min(cv.l_w_m, D)
            F_1 = max(0.75 * D / cv.l_w_m, F_min)  # literal-ok: el 0.75 de la Eq. 12.7.2.2-3
        T_L = P_FD * D / 2 + P_FL * C_L * F_1 / 2
        return T_L, dict(cv=cv, P_sp=P_sp, P_w=P_w, P_FD=P_FD, P_FL=P_FL,
                         C_L=C_L, F_1=F_1, H_total=H_rel + e_paq)

    intentos = []
    for clave, plancha, SS in planchas:
        t_env = plancha["profundidad_m"] + plancha["espesor_m"]
        H_rel = H_rel0 - (t_env - t_env_adopt)
        if not H_rel > 0:
            continue
        T_L, aux = _empuje(H_rel, t_env)
        f_cr = tension_critica_de_pandeo(S_mm=S_mm, r_mm=plancha["r_mm"],
                                         E=E_m, F_u=F_u, k=k)
        f_res = min(F_y, f_cr)
        A_req = T_L / (phi * f_res)     # kN/m / MPa = N/mm / (N/mm2) = mm2/mm
        FF = S_mm ** 2 / (E_m * plancha["I_mm4_mm"])
        ok_area = plancha["A_mm2_mm"] + TOL_UMBRAL_NORMATIVO >= A_req
        ok_costura = SS is None or phi_s * SS + TOL_UMBRAL_NORMATIVO >= T_L
        ok_ff = FF <= FF_lim + TOL_UMBRAL_NORMATIVO
        intentos.append((clave, plancha, SS, H_rel, T_L, aux, f_cr, f_res,
                         A_req, FF, ok_area, ok_costura, ok_ff))
        if ok_area and ok_costura and ok_ff:
            break
    if not intentos:
        raise DatoInvalidoError(
            campo="cota_subrasante", valor=punto.cota_subrasante,
            id_punto=punto.id,
            motivo="con la plancha minima la clave del TMC queda a nivel de "
                   "la subrasante o por encima")
    (clave, plancha, SS, H_rel, T_L, aux, f_cr, f_res, A_req, FF, ok_area,
     ok_costura, ok_ff) = intentos[-1]
    cumple_todo = ok_area and ok_costura and ok_ff
    cv = aux["cv"]
    probadas = ", ".join(i[0] for i in intentos)
    nota_eleccion = (
        f"Planchas probadas de la corrugacion {adopt['corrugacion']}, desde "
        f"{piso * MILIMETROS_POR_METRO:.2f} mm --el mayor de la adoptada "
        f"'{clave_adopt}' y del minimo de la Tabla 507-01 del EG-2013"
        + (f" ({t_min_eg * MILIMETROS_POR_METRO:.2f} mm)" if t_min_eg
           else ", que no tabula este diametro")
        + f"--, solo las que se fabrican con costura {fabricacion}: "
        f"{probadas}. El relleno sobre la clave se recalcula con cada una "
        "(una plancha mas gruesa sube la clave).")
    sust_plancha = (
        Magnitud("T_L", T_L, "kN/m", "empuje de anillo mayorado, paso F8.T",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("plancha", clave, "", "TMC_PLANCHA_CORRUGADA (ASTM A796 "
                 "Tablas 5, 7 y 9)"),
    )
    p_empuje = paso(
        "F8.CARGA_TIERRA", codigo="F8.T",
        que=f"TMC: presion mayorada en la clave y empuje de anillo, plancha {clave}",
        formula=("P_FD = eta (gamma_EV P_sp + gamma_WA P_w); P_FL = eta "
                 "gamma_LL P_L; T_L = P_FD S/2 + P_FL C_L F_1/2"),
        formula_cita_id="AASHTO_LRFD_9.12.7.2.2",
        citas_textuales=("AASHTO_LRFD_9.C12.7.2.2", "ASTM_A796.9.1",
                         "AASHTO_LRFD_9.12.5.4", "MP.2.4.2.1#PESOS",
                         "MP.2.3.2.5"),
        sustitucion=(
            Magnitud("eta", eta, "", f"'{CRITERIO_ETA_CONDUCTO}' [A]; eta_D = "
                     "eta_R = 1.00 (12.5.4)", cifras=CIFRAS_FACTOR),
            Magnitud("gamma_EV", gamma_EV, "", f"maximo de «{fila_EV}», Tabla "
                     "2.4.5.3.1-2 del Manual de Puentes ('factores_carga_"
                     "aashto')", cifras=CIFRAS_FACTOR),
            Magnitud("P_sp", aux["P_sp"], "kPa",
                     f"gamma_s H_rel + gamma_p e_paq; {proc_gamma}",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("H_rel", H_rel, "m", "subrasante menos clave con esta "
                     "plancha", cifras=CIFRAS_MAGNITUD),
            Magnitud("gamma_WA", gamma_WA, "", "Resistencia I, Tabla "
                     "2.4.5.3.1-1", cifras=CIFRAS_FACTOR),
            Magnitud("P_w", aux["P_w"], "kPa", "agua hasta la clave (la "
                     "hipotesis de V7), o el NF del punto medido desde la cota "
                     "de terreno si queda mas alto, sobre el arranque",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("gamma_LL", gamma_LL, "", "Resistencia I, Tabla "
                     "2.4.5.3.1-1", cifras=CIFRAS_FACTOR),
            Magnitud("P_L", cv.P_L_kPa, "kPa", f"paso F8.LL ({cv.vehiculo}, "
                     "el de mayor P_L C_L F_1)", cifras=CIFRAS_MAGNITUD),
            Magnitud("C_L", aux["C_L"], "m", "l_w <= S (Eq. 12.7.2.2-2)",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("F_1", aux["F_1"], "", "0.75 S/l_w >= F_min (Eqs. "
                     "12.7.2.2-3 y -4)", cifras=CIFRAS_FACTOR),
            Magnitud("S", D, "m", "diametro del escalon", cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("T_L", T_L, "kN/m", "empuje de anillo mayorado",
                           cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=(
            "LECTURA DE LA REMISION DE 12.7.2.2 A 12.12.3.4: la presion en la "
            "clave se toma como la de campo libre a la cota de la clave "
            "(C12.7.2.2), sin el factor de instalacion K_gammaE del "
            "termoplastico; es la misma presion que ASTM A796 num. 9.1 "
            "mayora con 1.95. ES LA LECTURA DE LA MENOR DEMANDA Y LA LETRA NO "
            "LA DICE (12.7.2.2 remite a 12.12.3.4 «with VAF taken as 1.0 and "
            "D_o taken as S», y la ecuacion a la que remite lleva K_gammaE): "
            "se adopta porque el gamma_EV = 1.95 del metal ya trae la "
            "seguridad que K_gammaE = 1.5 da al termoplastico sobre su 1.30 "
            "(1.30 x 1.5 = 1.95), y aplicar los dos seria contarla dos veces. El "
            "suelo pesa humedo tambien bajo el agua, que es una cota superior "
            "del peso sumergido mas la presion del agua."))
    v_area = _verificacion_f8(paso("F8.TMC_AREA", **_campos_f8(
            codigo=CODIGO_AREA,
            que=f"TMC: area de pared con pandeo, plancha {clave}",
            formula="A >= T_L / (phi min(F_y, f_cr))",
            formula_cita_id="AASHTO_LRFD_9.12.7.2.3",
            sust=sust_plancha + (
            Magnitud("phi", phi, "", "Tabla 12.5.5-1, area de pared y pandeo",
                     cifras=CIFRAS_FACTOR),
            Magnitud("F_y", F_y, "MPa", "Tabla A12-9, 33.0 ksi",
                     cifras=CIFRAS_FACTOR),
            Magnitud("f_cr", f_cr, "MPa", f"12.7.2.4 con r = "
                     f"{plancha['r_mm']} mm, k = {k}, E_m = 29 000 ksi, F_u = "
                     "45.0 ksi", cifras=CIFRAS_FACTOR),
            Magnitud("A", plancha["A_mm2_mm"], "mm2/mm", "area de la plancha "
                     "(ASTM A796)", cifras=CIFRAS_MAGNITUD)),
            obtenido=Magnitud("A_req", A_req, "mm2/mm", "area de pared requerida",
                          cifras=CIFRAS_MAGNITUD),
            admisible=plancha["A_mm2_mm"],
            unidad="mm2/mm",
            cita_umbral="AASHTO_LRFD_9.12.7.2.4",
            descripcion_umbral=f"area de la plancha {clave}",
            aplicacion="umbral duro de resistencia (LRFD)",
            criterio=CRITERIO_PLANCHA_TMC,
            cumple=ok_area,
            margen=plancha["A_mm2_mm"] - A_req,
            explicacion="la pared resiste el empuje" if ok_area else
                     "ninguna plancha probada resiste el empuje",
            citas=("AASHTO_LRFD_9.TA12-9", "AASHTO_LRFD_9.12.5.5",
               "EG2013.T507-01"),
            nota=nota_eleccion)),
        numeral=NUMERAL_F8_TMC)
    if SS is None:
        v_costura = Verificacion(
            cumple=True, numeral=NUMERAL_F8_TMC, valor_obtenido=T_L,
            valor_admisible=None, criterio_aplicado=CRITERIO_FABRICACION_TMC,
            codigo=CODIGO_COSTURA, estado=EstadoDeVerificacion.NO_APLICA,
            motivo_no_aplica=("tuberia helicoidal ('fabricacion_tmc'): no "
                              "tiene costura longitudinal, y AASHTO LRFD "
                              "12.7.2.5 solo la exige a la que la tiene "
                              "(ASTM A796 num. 8.1.3.1)"))
    else:
        # Si la costura no desarrolla el empuje, dice si OTRA fabricacion
        # tabulada lo haria: la fabricacion es una eleccion declarada y la
        # progresion no la cambia sola, pero el motivo tiene que decir que
        # se puede hacer antes de dar el TMC por no factible.
        pista = ""
        if not ok_costura:
            otras = []
            for otra, columna in REMACHE_DE_FABRICACION.items():
                if otra == fabricacion:
                    continue
                mejor = max((_CN.COSTURA_REMACHADA_TMC_KN_M[c][columna] or 0.0
                             for c, f in _CN.TMC_PLANCHA_CORRUGADA.items()
                             if f["corrugacion"] == adopt["corrugacion"]),
                            default=0.0)
                if phi_s * mejor + TOL_UMBRAL_NORMATIVO >= T_L:
                    otras.append(f"{otra} (hasta phi_s SS = "
                                 f"{phi_s * mejor:.1f} kN/m)")
            pista = (
                f" Se probaron todas las planchas de {adopt['corrugacion']} "
                f"con costura {fabricacion} ({probadas}). "
                + ("La desarrollaria la fabricacion " + " o ".join(otras)
                   + f", o la helicoidal, que no tiene costura longitudinal: "
                   f"declarar '{CRITERIO_FABRICACION_TMC}'."
                   if otras else
                   "Ninguna costura remachada tabulada la desarrolla; la "
                   "helicoidal no tiene costura longitudinal "
                   f"('{CRITERIO_FABRICACION_TMC}')."))
        v_costura = _verificacion_f8(paso("F8.TMC_COSTURA", **_campos_f8(
                codigo=CODIGO_COSTURA,
                que=f"TMC: costura longitudinal ({fabricacion}), plancha {clave}",
                formula="phi_s SS >= T_L",
                sust=sust_plancha + (
                Magnitud("phi_s", phi_s, "", "Tabla 12.5.5-1, costura "
                         "longitudinal", cifras=CIFRAS_FACTOR),
                Magnitud("SS", SS, "kN/m", "resistencia ultima de la costura "
                         "remachada, ASTM A796 (COSTURA_REMACHADA_TMC_KN_M)",
                         cifras=CIFRAS_MAGNITUD)),
                obtenido=Magnitud("T_L", T_L, "kN/m", "empuje mayorado",
                              cifras=CIFRAS_MAGNITUD),
                admisible=phi_s * SS,
                unidad="kN/m",
                cita_umbral="AASHTO_LRFD_9.12.7.2.5",
                descripcion_umbral="resistencia mayorada de la costura, phi_s SS",
                aplicacion="umbral duro de resistencia (LRFD)",
                criterio=CRITERIO_FABRICACION_TMC,
                cumple=ok_costura,
                margen=phi_s * SS - T_L,
                explicacion="la costura desarrolla el empuje" if ok_costura else
                         "la costura no desarrolla el empuje." + pista,
                citas=("ASTM_A796.T5", "ASTM_A796.8.1.3.1",
                       "AASHTO_LRFD_9.12.5.5", "EG2013.507.02#EMPERNADA"),
                nota=AVISO_COSTURA_DE_OTRA_FABRICACION.format(
                    fabricacion=fabricacion))),
            numeral=NUMERAL_F8_TMC)
    v_ff = _verificacion_f8(paso("F8.TMC_FF", **_campos_f8(
            codigo=CODIGO_FF,
            que=f"TMC: factor de flexibilidad, plancha {clave}",
            formula="FF = S^2 / (E_m I)",
            sust=(Magnitud("S", S_mm, "mm", "diametro", cifras=CIFRAS_MAGNITUD),
              Magnitud("E_m", E_m, "MPa", "Tabla A12-9, 29 000 ksi",
                       cifras=CIFRAS_MAGNITUD),
              Magnitud("I", plancha["I_mm4_mm"], "mm4/mm", "inercia de la "
                       "plancha (ASTM A796)", cifras=CIFRAS_MAGNITUD)),
            obtenido=Magnitud("FF", FF, "mm/N", "factor de flexibilidad",
                          cifras=CIFRAS_FINA),
            admisible=FF_lim,
            unidad="mm/N",
            cita_umbral="AASHTO_LRFD_9.12.5.6.1#FF",
            descripcion_umbral=f"limite de la Tabla 12.5.6.1-1 para la "
                            f"corrugacion {adopt['corrugacion']}",
            aplicacion="exigencia de la Tabla 12.5.6.1-1 («shall not "
                       "exceed»), umbral duro; es de manejo e instalacion, "
                       "no un estado limite del tubo ya enterrado",
            criterio=CRITERIO_PLANCHA_TMC,
            cumple=ok_ff,
            margen=FF_lim - FF,
            explicacion="rigidez suficiente para el manejo y la compactacion"
                     if ok_ff else "la plancha es demasiado flexible",
            citas=("ASTM_A796.10.3",))),
        numeral=NUMERAL_F8_TMC)
    # El CONTRASTE ASD: las mismas cargas, SIN factorar, por A796 num. 8.
    T_asd, f_asd, A_asd = area_requerida_asd_a796(
        S_m=D, P_kPa=aux["P_sp"] + cv.P_L_kPa, r_mm=plancha["r_mm"])
    p_asd = paso(
        "F8.TMC_ASD", codigo="F8.ASD",
        que=(f"TMC: contraste por tensiones admisibles (ASTM A796 num. 8), "
             f"plancha {clave} -- NO RIGE"),
        formula="T = (EL + LL) S/2; A = T SF / min(f_y, f_c)",
        sustitucion=(
            Magnitud("EL+LL", aux["P_sp"] + cv.P_L_kPa, "kPa", "presion sin "
                     "factorar: P_sp + P_L (HL-93, no la H20 del num. 6.2.2.1)",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("T", T_asd, "kN/m", "empuje de servicio",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("SF", _CN.A796_SF_AREA, "", "ASTM A796 num. 8.1.1.2",
                     cifras=CIFRAS_FACTOR),
            Magnitud("f", f_asd, "MPa", "min(f_y = 225, f_c), ASTM A796 num. 4 "
                     "y ecs. 5 y 6", cifras=CIFRAS_FACTOR)),
        resultado=Magnitud("A_ASD", A_asd, "mm2/mm", "area requerida por "
                           f"tensiones admisibles, frente a "
                           f"{plancha['A_mm2_mm']} de la plancha",
                           cifras=CIFRAS_MAGNITUD),
        citas_textuales=("ASTM_A796.7.1", "ASTM_A796.8.1.1.2#SELECCION"),
        nota_del_proyecto=(
            "Informativo: el marco que rige es el de AASHTO LRFD 12.7.2 "
            "(arriba). Este paso usa los parametros de A796 en SI y no se "
            "combina con ningun factor de carga de LRFD. NO ES «A796 PURO»: "
            "la carga viva es el P_L del HL-93 del paso F8.LL, que ya lleva "
            "el factor de presencia multiple de 1.20 y el IM del Manual de "
            "Puentes --conceptos de LRFD que A796 no tiene--, y no la H20 de "
            "su num. 6.2.2.1."))
    pasos: List[PasoDeMemoria] = [cv.paso, p_empuje, p_asd]
    H_max = None
    if cumple_todo:
        t_env = plancha["profundidad_m"] + plancha["espesor_m"]

        def _margen(H: float) -> float:
            T, _ = _empuje(H, t_env)
            m = plancha["A_mm2_mm"] * phi * f_res - T
            if SS is not None:
                m = min(m, phi_s * SS - T)
            return m

        H_max = _relleno_maximo(_margen, H_rel, D, punto.id)
        pasos.append(paso(
            "F8.TMC_AREA", codigo="F8.HMAX",
            que=f"Relleno maximo sobre la clave con la plancha {clave}",
            formula="H_max: T_L(H_max) = min(phi A min(F_y, f_cr), phi_s SS)",
            sustitucion=(Magnitud("phi A f", plancha["A_mm2_mm"] * phi * f_res,
                                  "kN/m", "resistencia de la pared",
                                  cifras=CIFRAS_MAGNITUD),),
            resultado=Magnitud("H_max", H_max, "m", "relleno sobre la clave "
                               "hasta la subrasante, con el mismo paquete",
                               cifras=CIFRAS_MAGNITUD),
            citas_textuales=("AASHTO_LRFD_9.12.7.2.2",)))
    avisos = list(_aviso_de_carga_viva_despreciada(cv))
    if SS is not None:
        avisos.append("F8: " + AVISO_COSTURA_DE_OTRA_FABRICACION.format(
            fabricacion=fabricacion))
    else:
        avisos.append(
            f"F8: el TMC se verifico como HELICOIDAL ('{CRITERIO_FABRICACION_TMC}'"
            "), sin costura longitudinal; el EG-2013 507.02 a) describe "
            "tuberia armada con pernos: confirmar la fabricacion con el "
            "fabricante")
    if cumple_todo and clave != clave_adopt:
        avisos.append(
            f"F8: el TMC de {D:.2f} m necesita la plancha {clave} y el "
            f"catalogo adopta '{clave_adopt}' ('{CRITERIO_PLANCHA_TMC}'): la "
            "envolvente geometrica de 7.A y de V7 se armo con la adoptada, y "
            "con la requerida la clave sube "
            f"{(plancha['espesor_m'] - adopt['espesor_m']) * MILIMETROS_POR_METRO:.2f}"
            " mm. Declare la plancha requerida para que la geometria la use "
            "(el bucle de MD ya lo hace: vuelve a verificar el escalon con "
            "ella, ficha T5-03)")
    return ResultadoEstructural(
        material=TipoMaterial.TMC.value, H_relleno_m=H_rel, e_paquete_m=e_paq,
        H_total_m=aux["H_total"], seleccion=clave if cumple_todo else "",
        relleno_maximo_m=H_max, verificaciones=(v_area, v_costura, v_ff),
        pasos=tuple(pasos), avisos=tuple(avisos),
        diferido=(DIFERIDO_COSTURA_EMPERNADA,))


def plancha_requerida_tmc(*, punto: PuntoCritico, material: Material,
                          seccion: Seccion) -> Optional[str]:
    """
    --- VE-5 (m8), item 23 (ficha T5-03) --- La plancha que la Fase 8 elige
    para este escalon de TMC (AASHTO LRFD 12.7.2, con el minimo de la Tabla
    507-01 del EG-2013) cuando NO es la del material, o None si es la misma
    o si nada cumple. Es lo que MD lee para devolver la plancha a la
    geometria (`M2.material_con_plancha_tmc`) y volver a verificar el
    escalon con ella.
    """
    from src.modulos.M2_material import plancha_del_material
    from src.modulos.M5_verificaciones import altura_relleno_sobre_clave   # perezoso: M5 importa M8
    r = verificar_conducto(
        punto=punto, material=material, seccion=seccion,
        altura_relleno=altura_relleno_sobre_clave(punto=punto,
                                                  material=material,
                                                  seccion=seccion))
    if not (r.cumple and r.seleccion):
        return None
    return (None if r.seleccion == plancha_del_material(material)
            else r.seleccion)


# ---------------------------------------------------------------------------
# Tuberia de polietileno corrugado: AASHTO LRFD 12.12
# ---------------------------------------------------------------------------

def _modulo_del_suelo(P_sp_kPa: float, columna: str) -> float:
    """
    M_s de la Tabla 12.12.3.5-1, en kPa, interpolado por P_sp; fuera de la
    tabla, el extremo (abajo de 1 psi, el de 1 psi, que es el menor).
    """
    pares = [(p, m) for p, m in zip(_CN.MS_NIVELES_PSP_PSI,
                                    _CN.MS_TABLA_KSI[columna]) if m is not None]
    xs, ys = zip(*pares)
    return (_interpolar(P_sp_kPa / PSI_EN_KPA, xs, ys) * KSI_EN_MPA
            * KPA_POR_MPA)


def _perfil_minimo_hdpe(D: float, id_punto) -> Tuple[int, dict]:
    """La fila de la Tabla A12-11 de AASHTO LRFD del diametro, o se detiene."""
    D_mm = round(D * MILIMETROS_POR_METRO)
    perfil = _CN.PE_M294_PERFIL_MINIMO.get(D_mm)
    if perfil is None:
        raise DatoFaltanteError(
            "perfil_hdpe", id_punto=id_punto,
            detalle=(f"la Table A12-11 de AASHTO LRFD no trae el tubo de PE de "
                     f"{D_mm} mm: sin su fila la Fase 8 no se puede "
                     "verificar"))
    return D_mm, perfil


def perfil_declarado_hdpe(D: float, id_punto=None) -> Optional[dict]:
    """
    El perfil del FABRICANTE para el tubo de diametro `D` (m), de
    'perfil_hdpe_fabricante' [A] opcional, validado en segunda linea; None
    si el criterio no esta declarado o no trae ese diametro.

    Cada propiedad tiene que ser al menos el minimo de la Tabla A12-11 (el
    area y la inercia) y el diametro exterior no pasar de su maximo: un
    producto conforme a M 294 no puede tener menos, y una declaracion por
    debajo es un dato que hay que CORREGIR (`DatoInvalidoError`).
    """
    D_mm, minimo = _perfil_minimo_hdpe(D, id_punto)
    declarado = ca.valor_si_declarado(CRITERIO_PERFIL_HDPE)
    if declarado is None:
        return None
    if not hasattr(declarado, "get"):
        raise DatoInvalidoError(
            campo=CRITERIO_PERFIL_HDPE, valor=declarado, id_punto=id_punto,
            motivo="se espera {'<diametro nominal en mm>': {'A_mm2_mm', "
                   "'I_mm4_mm', 'od_m'}}, p. ej. {'900': {...}}")
    fila = next((v for k, v in declarado.items()
                 if not isinstance(k, bool) and isinstance(k, (int, float, str))
                 and str(k).strip().replace(".0", "") == str(D_mm)), None)
    if fila is None:
        return None
    if not hasattr(fila, "get") or sorted(fila) != sorted(CAMPOS_PERFIL_HDPE):
        raise DatoInvalidoError(
            campo=CRITERIO_PERFIL_HDPE, valor=fila, id_punto=id_punto,
            motivo=f"el perfil de {D_mm} mm lleva exactamente los campos "
                   f"{CAMPOS_PERFIL_HDPE}")
    A = _finito_positivo(CRITERIO_PERFIL_HDPE, fila["A_mm2_mm"], id_punto)
    I = _finito_positivo(CRITERIO_PERFIL_HDPE, fila["I_mm4_mm"], id_punto)
    od = _finito_positivo(CRITERIO_PERFIL_HDPE, fila["od_m"], id_punto)
    if (not A + TOL_UMBRAL_NORMATIVO >= minimo["A_mm2_mm"]
            or not I + TOL_UMBRAL_NORMATIVO >= minimo["I_mm4_mm"]
            or not od <= minimo["od_max_m"] + TOL_UMBRAL_NORMATIVO
            or not od > D):
        raise DatoInvalidoError(
            campo=CRITERIO_PERFIL_HDPE, valor=fila, id_punto=id_punto,
            motivo=(f"el perfil de {D_mm} mm tiene que tener al menos el "
                    f"area ({minimo['A_mm2_mm']:.3f} mm2/mm) y la inercia "
                    f"({minimo['I_mm4_mm']:.0f} mm4/mm) minimas de la Tabla "
                    "A12-11 de AASHTO LRFD, y un diametro exterior mayor que "
                    f"el interior y no mayor que su maximo "
                    f"({minimo['od_max_m']:.4f} m)"))
    return dict(minimo, A_mm2_mm=A, I_mm4_mm=I, od_max_m=od)


def cota_inferior_hdpe(*, punto: PuntoCritico, material: Material,
                       seccion: Seccion, altura_relleno: float
                       ) -> ResultadoEstructural:
    """
    La Fase 8 del HDPE calculada con el perfil MINIMO de la Tabla A12-11 de
    AASHTO LRFD: una COTA INFERIOR, no un veredicto sobre un producto. La
    propia norma dice que esos minimos «are not meaningful for design»
    (C12.12.3.2) y manda tomar las propiedades del fabricante (12.12.3.2).
    El resultado lleva `cota_inferior=True` y no entra nunca a la tabla de
    la Fase 5: lo usan `verificar_hdpe`, para decir en su detencion cuanto
    daria el minimo, y quien quiera imprimirlo.
    """
    _D_mm, minimo = _perfil_minimo_hdpe(seccion.altura, punto.id)
    return _evaluar_hdpe(punto=punto, material=material, seccion=seccion,
                         altura_relleno=altura_relleno, perfil=minimo,
                         es_minimo=True)


def verificar_hdpe(*, punto: PuntoCritico, material: Material,
                   seccion: Seccion, altura_relleno: float
                   ) -> ResultadoEstructural:
    """
    Tuberia de polietileno corrugado (AASHTO M 294) por AASHTO LRFD 12.12:
    empuje (12.12.3.5 y 12.12.3.10.1d), pandeo general (12.12.3.10.1e),
    deflexion de servicio (12.12.2.2) y factor de flexibilidad (12.12.3.6),
    con el perfil que el FABRICANTE declare ('perfil_hdpe_fabricante').

    SIN EL PERFIL DEL FABRICANTE NO HAY VEREDICTO (decision del dueño del
    proyecto, 2026-11-12, sobre las dos auditorias de T-5). Se calcula con
    el perfil minimo de la Tabla A12-11 solo para dar la cota inferior, y la
    funcion se detiene con `DatoFaltanteError` sobre
    'perfil_hdpe_fabricante': el HDPE queda «no verificado con un producto
    real» y NO se adopta. La cota viaja en el mensaje y en el atributo
    `cota_inferior` de la excepcion. El HDPE es el ULTIMO candidato del
    orden de M2, de modo que su dato faltante no bloquea a ningun otro
    material (regla T4-10 de `MD.disenar_punto`).
    """
    perfil = perfil_declarado_hdpe(seccion.altura, punto.id)
    if perfil is None:
        cota = cota_inferior_hdpe(punto=punto, material=material,
                                  seccion=seccion,
                                  altura_relleno=altura_relleno)
        veredictos = "; ".join(
            f"{v.codigo} {v.valor_obtenido:.4g} frente a "
            f"{v.valor_admisible:.4g} ({'cumpliria' if v.cumple else 'no cumpliria'})"
            for v in cota.verificaciones)
        exc = DatoFaltanteError(
            CRITERIO_PERFIL_HDPE, id_punto=punto.id,
            detalle=(f"el HDPE de {seccion.altura:.2f} m queda "
                     f"{ROTULO_HDPE_SIN_PRODUCTO}: falta el perfil del "
                     "fabricante (area, inercia y diametro exterior). COTA "
                     "INFERIOR con el perfil minimo de la Tabla A12-11 de "
                     f"AASHTO LRFD: {veredictos}. No es un veredicto: AASHTO "
                     "C12.12.3.2 dice que esos minimos «are not meaningful "
                     "for design». Se destraba declarando "
                     f"'{CRITERIO_PERFIL_HDPE}' con el catalogo o la "
                     "certificacion del fabricante (EG-2013 508.02 b)"))
        exc.cota_inferior = cota
        raise exc
    return _evaluar_hdpe(punto=punto, material=material, seccion=seccion,
                         altura_relleno=altura_relleno, perfil=perfil,
                         es_minimo=False)


def _evaluar_hdpe(*, punto: PuntoCritico, material: Material,
                  seccion: Seccion, altura_relleno: float, perfil: dict,
                  es_minimo: bool) -> ResultadoEstructural:
    """
    El calculo de AASHTO LRFD 12.12 con un perfil dado (el del fabricante o
    el minimo de la Tabla A12-11), y el area efectiva que el ensayo de
    compresion de M 294 num. 7.7 garantiza al producto: A_eff = 0.5 A_g
    F_u,ini K_t / F_u <= A_g (12.12.3.10.1b-5).

    LA DEFORMACION DE EMPUJE SE SUMA POR DURACION, que es la lectura del
    proyecto de la definicion de E_p en 12.12.3.10.1c («short-term modulus
    for short-term loading or long-term modulus ... for long-term loading»):
    la de las cargas permanentes (tierra y agua) con el modulo y el area
    efectiva de LARGO PLAZO ('parametros_diseno_hdpe', 50 o 75 años) y la de
    la carga viva con los INICIALES; el arqueo (S_H, VAF, F_2) se evalua con
    el modulo de la duracion de cada carga.

    EL PANDEO GENERAL VA CON EL MODULO DE LA VIDA DE DISEÑO, que es lo que
    manda la letra de 12.12.3.3 («Investigation of general buckling shall be
    based on the value of modulus of elasticity that represents the design
    life of the project»): TODO --la deformacion de la carga viva, su arqueo
    y la capacidad-- con el modulo y el area efectiva de largo plazo. La
    FASE A lo sumaba por duracion sin citar esa frase; se conserva esa suma
    como segundo termino y rige EL MAYOR de los dos, porque cual es mayor
    depende del suelo (medido por el auditor: con Cl-95 la letra da mas, con
    Sn-95 y Si-95 da menos) y la lectura tiene que ser la conservadora.
    """
    D = seccion.altura
    D_mm = round(D * MILIMETROS_POR_METRO)
    params = ca.valor(CRITERIO_PARAMETROS_HDPE)
    lp = str(int(round(params["anios_largo_plazo"])))
    if lp not in _CN.PE_M294_PROPIEDADES_KSI or lp == DURACION_INICIAL:
        raise DatoInvalidoError(campo=CRITERIO_PARAMETROS_HDPE,
                                valor=params["anios_largo_plazo"],
                                id_punto=punto.id,
                                motivo="anios_largo_plazo es 50 o 75 (Tabla "
                                       "12.12.3.3-1)")
    columna = ca.valor(CRITERIO_RELLENO_HDPE)
    if columna not in _CN.MS_TABLA_KSI:
        raise DatoInvalidoError(campo=CRITERIO_RELLENO_HDPE, valor=columna,
                                id_punto=punto.id,
                                motivo=f"columnas: {sorted(_CN.MS_TABLA_KSI)}")
    e_paq = espesor_del_paquete(punto)
    H_rel = _finito_positivo("altura_relleno", altura_relleno, punto.id)
    gamma_s, gamma_p, proc_gamma = pesos_especificos_de_carga(
        piso_tubo_concreto=False)
    eta = _eta()
    gamma_EV, fila_EV = _gamma_ev_max(material)
    gamma_WA = _gamma_de_la_combinacion(CARGA_AGUA, EXTREMO_DESESTABILIZANTE)
    gamma_LL = _gamma_ll()
    K_gE, nu = params["K_gamma_E"], params["nu_suelo"]
    D_o = perfil["od_max_m"]
    A_g = perfil["A_mm2_mm"] / MILIMETROS_POR_METRO              # m2/m
    I_p = perfil["I_mm4_mm"] / MILIMETROS_POR_METRO ** 3         # literal-ok: mm4/mm a m4/m, el cubo del factor de unidad
    R = (D + D_o) / 4            # literal-ok: radio medio de la pared, (D + D_o)/2/2 (lectura declarada)
    D_c = 2 * R
    Fu_ini, E_inicial = (x * KSI_EN_MPA * KPA_POR_MPA
                         for x in _CN.PE_M294_PROPIEDADES_KSI[DURACION_INICIAL])
    Fu_lp, E_lp = (x * KSI_EN_MPA * KPA_POR_MPA
                   for x in _CN.PE_M294_PROPIEDADES_KSI[lp])
    fraccion = _CN.M294_FRACCION_CAPACIDAD_COMPRESION
    A_lp = min(A_g, fraccion * A_g * Fu_ini * _CN.KT_PE[lp] / Fu_lp)
    A_ini = min(A_g, fraccion * A_g * _CN.KT_PE[DURACION_INICIAL])
    E_ini = E_inicial
    if perfil["nota_largo_plazo"]:
        # Nota «*» de la Tabla A12-11 (42 y 48 in): diseñar la pared con la
        # resistencia de largo plazo. En el metodo de deformaciones la
        # lectura conservadora es tratar tambien la carga viva con el modulo
        # y el area efectiva de largo plazo. (El factor de flexibilidad NO:
        # 12.12.3.6 manda el modulo INICIAL, `E_inicial`.)
        E_ini, A_ini = E_lp, A_lp
    phi_s = _CN.PHI_SUELO_PE
    nf = punto.NF_profundidad_m

    def _arqueo(M_s: float, E: float):
        S_H = phi_s * M_s * R / (E * A_g)
        VAF = 0.76 - 0.71 * (S_H - 1.17) / (S_H + 2.92)  # literal-ok: Eq. 12.12.3.5-3
        F_2 = 0.95 / (1 + 0.6 * S_H)                     # literal-ok: Eq. 12.12.3.5-8
        return S_H, VAF, F_2

    def _capacidad_pandeo(M_s: float, E: float, A_eff: float, R_h: float):
        return (1.2 * _CN.CN_PANDEO_PE * (E * I_p) ** (1 / 3)   # literal-ok: el 1.2 y el 1/3 de la Eq. 12.12.3.10.1e-2
                * (phi_s * M_s * (1 - 2 * nu) / (1 - nu) ** 2) ** (2 / 3)  # literal-ok: el exponente 2/3 de la Eq. 12.12.3.10.1e-2
                * R_h / (A_eff * E))

    F_min = max(_CN.F_MIN_NUMERADOR_M / D, 1.0)

    def _efecto(P_L: float, l_w: float) -> float:
        return (P_L * min(l_w / D_o, 1.0)
                * max(0.75 * D_o / l_w, F_min))          # literal-ok: el 0.75 de la Eq. 12.12.3.5-6

    def _estado(H: float) -> dict:
        H_total = H + e_paq
        cv = carga_viva_enterrada(
            H=H_total, D_i=D, D_E=H, conducto=CONDUCTO_FLEXIBLE,
            id_punto=punto.id, efecto=_efecto,
            efecto_descripcion="P_L C_L F_1, kPa (Eqs. 12.12.3.5-5 a -7)")
        P_sp = gamma_s * (H + 0.11 * D_o) + gamma_p * e_paq  # literal-ok: el 0.11 D_o de la Eq. 12.12.3.7-3
        H_w = D_o / 2
        if nf is not None:
            centro = punto.cota_subrasante - H - D_o / 2
            H_w = max(H_w, (punto.cota_terreno - nf) - centro)
        P_w = GAMMA_AGUA_KN_M3 * H_w
        M_s = _modulo_del_suelo(P_sp, columna)
        if cv.despreciada:
            C_L, F_1 = 0.0, 0.0
        else:
            C_L = min(cv.l_w_m / D_o, 1.0)
            F_1 = max(0.75 * D_o / cv.l_w_m, F_min)          # literal-ok: el 0.75 de la Eq. 12.12.3.5-6
        R_h = 11.4 / (11 + D_c / H)                          # literal-ok: Eq. 12.12.3.10.1e-3
        S_H_lp, VAF_lp, F_2_lp = _arqueo(M_s, E_lp)
        S_H_ini, _, F_2_ini = _arqueo(M_s, E_ini)
        T_d = eta * (gamma_EV * K_gE * _CN.K2_EMPUJE_ARRANQUE * VAF_lp * P_sp
                     + gamma_WA * P_w) * D_o / 2
        T_l = eta * gamma_LL * cv.P_L_kPa * C_L * F_1 * F_2_ini * D_o / 2
        eps_d = T_d / (A_lp * E_lp)
        eps_l = T_l / (A_ini * E_ini)
        bck_lp = _capacidad_pandeo(M_s, E_lp, A_lp, R_h)
        bck_ini = _capacidad_pandeo(M_s, E_ini, A_ini, R_h)
        # Pandeo general por la LETRA de 12.12.3.3: la carga viva tambien
        # con el modulo, el arqueo y el area efectiva de la vida de diseño.
        T_l_lp = eta * gamma_LL * cv.P_L_kPa * C_L * F_1 * F_2_lp * D_o / 2
        eps_l_lp = T_l_lp / (A_lp * E_lp)
        u_letra = (eps_d + eps_l_lp) / bck_lp
        u_duracion = eps_d / bck_lp + eps_l / bck_ini
        # Servicio (12.12.2.2): el empuje sin factorar, con la misma suma.
        Ts_d = (_CN.K2_EMPUJE_ARRANQUE * VAF_lp * P_sp + P_w) * D_o / 2
        Ts_l = cv.P_L_kPa * C_L * F_1 * F_2_ini * D_o / 2
        eps_sc = Ts_d / (A_lp * E_lp) + Ts_l / (A_ini * E_ini)
        Delta = (params["K_B"] * (params["D_L"] * P_sp + C_L * cv.P_L_kPa) * D_o
                 / (E_lp * I_p / R ** 3 + 0.061 * M_s)       # literal-ok: el 0.061 de la Eq. 12.12.2.2-2
                 + eps_sc * D_c)
        return dict(cv=cv, P_sp=P_sp, P_w=P_w, M_s=M_s, C_L=C_L, F_1=F_1,
                    R_h=R_h, S_H_lp=S_H_lp, S_H_ini=S_H_ini, VAF_lp=VAF_lp,
                    F_2_ini=F_2_ini, F_2_lp=F_2_lp, T_d=T_d, T_l=T_l,
                    eps_d=eps_d, eps_l=eps_l, eps_uc=eps_d + eps_l,
                    eps_l_lp=eps_l_lp, u_letra=u_letra,
                    u_duracion=u_duracion,
                    u_bck=max(u_letra, u_duracion),
                    bck_lp=bck_lp, bck_ini=bck_ini, eps_sc=eps_sc,
                    Delta=Delta, H_total=H_total)

    est = _estado(H_rel)
    cv = est["cv"]
    eps_lim = _CN.PHI_EMPUJE_PE * _CN.PE_M294_EPS_YC
    phi_bck = _CN.PHI_PANDEO_PE
    Delta_A = params["deflexion_admisible"] * D
    # Factor de flexibilidad (12.12.3.6): mm/N con S en mm, E en MPa e I en
    # mm4/mm. S es el «diameter of pipe»: se toma el EXTERIOR, que da el FF
    # mayor; E es el modulo INICIAL, como manda el numeral.
    FF = ((D_o * MILIMETROS_POR_METRO) ** 2
          / (E_inicial / KPA_POR_MPA * perfil["I_mm4_mm"]))
    FF_lim = _CN.FF_LIMITE_TERMOPLASTICO_MM_N
    ok_emp = est["eps_uc"] <= eps_lim + TOL_UMBRAL_NORMATIVO
    ok_bck = est["u_bck"] <= phi_bck + TOL_UMBRAL_NORMATIVO
    ok_def = est["Delta"] <= Delta_A + TOL_UMBRAL_NORMATIVO
    ok_ff = FF <= FF_lim + TOL_UMBRAL_NORMATIVO
    origen_perfil = ("perfil MINIMO de M 294 (Table A12-11 de AASHTO LRFD): "
                     "COTA INFERIOR, no un producto" if es_minimo else
                     f"perfil declarado del fabricante "
                     f"('{CRITERIO_PERFIL_HDPE}')")
    perfil_txt = (f"{origen_perfil}, {D_mm} mm: A = "
                  f"{perfil['A_mm2_mm']:.3f} mm2/mm, I = "
                  f"{perfil['I_mm4_mm']:.0f} mm4/mm, OD = {D_o:.4f} m")
    nota_cota = (
        f" {ROTULO_HDPE_SIN_PRODUCTO.upper()}: el calculo usa el perfil "
        "minimo de la Tabla A12-11, que el comentario C12.12.3.2 declara no "
        "significativo para el diseño; el veredicto es una cota inferior."
        if es_minimo else "")
    nota_lp = (" Fila con la llamada «*» de la Tabla A12-11: la carga viva se "
               "trata tambien con el modulo y el area efectiva de largo plazo "
               "(lectura conservadora del proyecto)."
               if perfil["nota_largo_plazo"] else "")
    nota_duracion = (
        "LECTURA DEL PROYECTO de la definicion de E_p (12.12.3.10.1c): la "
        f"deformacion de las cargas permanentes se calcula con E_p y A_eff de "
        f"{lp} años y la de la carga viva con los iniciales, y se suman; el "
        "arqueo de cada una con el modulo de su duracion. El area efectiva "
        "sale del MINIMO de producto que M 294 num. 7.7 exige al ensayo de "
        "compresion (traduccion no oficial), con el «limite elastico minimo "
        "especificado» leido como el F_u inicial de la Tabla 12.12.3.3-1, a "
        "falta de la geometria idealizada del perfil. El relleno es el "
        f"GRANULAR que el EG-2013 508.02 d) exige, leido como la columna "
        f"{columna} de la Tabla 12.12.3.5-1 "
        f"('{CRITERIO_RELLENO_HDPE}')." + nota_lp + nota_cota)
    sust_carga = (
        Magnitud("P_sp", est["P_sp"], "kPa", "prisma de suelo en el arranque, "
                 f"gamma_s (H + 0.11 D_o) + gamma_p e_paq; {proc_gamma}",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("P_w", est["P_w"], "kPa", "agua al menos hasta la clave "
                 "(hipotesis de V7) o el NF del punto si queda mas alto",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("M_s", est["M_s"] / KPA_POR_MPA, "MPa",
                 f"Tabla 12.12.3.5-1, columna {columna} "
                 f"('{CRITERIO_RELLENO_HDPE}' [A])", cifras=CIFRAS_FACTOR),
        Magnitud("P_L", cv.P_L_kPa, "kPa", f"paso F8.LL ({cv.vehiculo}, el de "
                 "mayor P_L C_L F_1)", cifras=CIFRAS_MAGNITUD),
        Magnitud("gamma_EV", gamma_EV, "", f"maximo de «{fila_EV}»",
                 cifras=CIFRAS_FACTOR),
        Magnitud("K_gammaE", K_gE, "", f"'{CRITERIO_PARAMETROS_HDPE}' [A]",
                 cifras=CIFRAS_FACTOR),
        Magnitud("eta", eta, "", f"'{CRITERIO_ETA_CONDUCTO}' [A]",
                 cifras=CIFRAS_FACTOR),
        Magnitud("VAF", est["VAF_lp"], "", "Eq. 12.12.3.5-3 con el modulo de "
                 f"{lp} años", cifras=CIFRAS_FACTOR),
        Magnitud("F_2", est["F_2_ini"], "", "Eq. 12.12.3.5-8 con el modulo "
                 "inicial", cifras=CIFRAS_FACTOR),
        Magnitud("C_L", est["C_L"], "", "l_w/D_o <= 1 (Eq. 12.12.3.5-5)",
                 cifras=CIFRAS_FACTOR),
        Magnitud("F_1", est["F_1"], "", "0.75 D_o/l_w >= F_min (Eqs. "
                 "12.12.3.5-6 y -7)", cifras=CIFRAS_FACTOR),
    )
    v_emp = _verificacion_f8(paso("F8.HDPE_EMPUJE", **_campos_f8(
            codigo=CODIGO_EMPUJE,
            que="HDPE: deformacion de compresion por empuje",
            formula="eps_uc = T_d/(A_eff,lp E_lp) + T_l/(A_eff,ini E_ini); "
                 "T_d = eta (gamma_EV K_gammaE K_2 VAF P_sp + gamma_WA P_w) "
                 "D_o/2; T_l = eta gamma_LL P_L C_L F_1 F_2 D_o/2",
            formula_cita_id="AASHTO_LRFD_9.12.12.3.5",
            sust=sust_carga + (
            Magnitud("T_d", est["T_d"], "kN/m", "empuje mayorado de las "
                     "cargas permanentes", cifras=CIFRAS_MAGNITUD),
            Magnitud("T_l", est["T_l"], "kN/m", "empuje mayorado de la carga "
                     "viva", cifras=CIFRAS_MAGNITUD),
            Magnitud("A_eff,lp", A_lp * MILIMETROS_POR_METRO, "mm2/mm",
                     f"0.5 A_g F_u,ini K_t / F_u a {lp} años (M 294 num. 7.7 y "
                     f"Eq. 12.12.3.10.1b-5); {perfil_txt}",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("A_eff,ini", A_ini * MILIMETROS_POR_METRO, "mm2/mm",
                     "idem, inicial", cifras=CIFRAS_MAGNITUD)),
            obtenido=Magnitud("eps_uc", est["eps_uc"], "", "deformacion de "
                          "compresion mayorada", cifras=CIFRAS_DEFORMACION),
            admisible=eps_lim,
            unidad="",
            cita_umbral="AASHTO_LRFD_9.12.12.3.10.1d",
            descripcion_umbral="phi_T eps_yc (Tabla 12.12.3.3-1, PE de M 294: "
                            "4.1 %)",
            aplicacion="umbral duro de resistencia (LRFD)",
            criterio=CRITERIO_PARAMETROS_HDPE,
            cumple=ok_emp,
            margen=eps_lim - est["eps_uc"],
            explicacion="la pared resiste el empuje" if ok_emp else
                     "el empuje supera la deformacion limite de la pared",
            citas=("AASHTO_LRFD_9.12.12.3.10.1c#EP",
               "AASHTO_LRFD_9.12.12.3.10.1b#STUB", "AASHTO_M294_TRAD.7.7",
               "AASHTO_LRFD_9.T12.12.3.3-1", "AASHTO_LRFD_9.T12.12.3.5-1",
               "AASHTO_LRFD_9.T12.12.3.5-2", "AASHTO_LRFD_9.12.12.3.2",
               "AASHTO_LRFD_9.C12.12.3.2", "EG2013.508.02#GRANULAR",
               "EG2013.T301-01", "EG2013.508.07#COMPACTACION",
               "AASHTO_LRFD_9.12.5.5"),
            nota=nota_duracion)),
        numeral=NUMERAL_F8_HDPE)
    gobierna_letra = est["u_letra"] >= est["u_duracion"]
    v_bck = _verificacion_f8(paso("F8.HDPE_PANDEO", **_campos_f8(
            codigo=CODIGO_PANDEO,
            que="HDPE: pandeo general",
            formula="u = max[(eps_d + eps_l,lp)/eps_bck,lp ; eps_d/eps_bck,lp "
                 "+ eps_l/eps_bck,ini] <= phi_bck; eps_bck = 1.2 C_n (E_p "
                 "I_p)^(1/3) [phi_s M_s (1-2 nu)/(1-nu)^2]^(2/3) R_h/(A_eff "
                 "E_p)",
            formula_cita_id="AASHTO_LRFD_9.12.12.3.10.1e",
            sust=(Magnitud("eps_bck,lp", est["bck_lp"], "", f"capacidad de pandeo "
                       f"general con el modulo de {lp} años, el de la vida de "
                       "diseño (12.12.3.3)", cifras=CIFRAS_DEFORMACION),
              Magnitud("eps_bck,ini", est["bck_ini"], "", "idem, inicial "
                       "(solo para la suma por duracion)",
                       cifras=CIFRAS_DEFORMACION),
              Magnitud("u_letra", est["u_letra"], "", "TODO con el modulo de "
                       f"{lp} años: (eps_d + eps_l,lp)/eps_bck,lp, con la "
                       "carga viva, su arqueo y su area efectiva de largo "
                       "plazo (letra de 12.12.3.3)", cifras=CIFRAS_FINA),
              Magnitud("u_duracion", est["u_duracion"], "", "suma por "
                       "duracion: eps_d/eps_bck,lp + eps_l/eps_bck,ini "
                       "(lectura de 12.12.3.10.1c)", cifras=CIFRAS_FINA),
              Magnitud("R_h", est["R_h"], "", "11.4/(11 + D/H), con H el "
                       "relleno sobre la clave hasta la subrasante (sin el "
                       "paquete: del lado de la capacidad menor)",
                       cifras=CIFRAS_FACTOR),
              Magnitud("nu", nu, "", f"'{CRITERIO_PARAMETROS_HDPE}' [A]",
                       cifras=CIFRAS_FACTOR),
              Magnitud("C_n", _CN.CN_PANDEO_PE, "", "12.12.3.10.1e",
                       cifras=CIFRAS_FACTOR)),
            obtenido=Magnitud("u_bck", est["u_bck"], "", "razon de utilizacion "
                          "frente al pandeo general: la mayor de las dos "
                          "lecturas", cifras=CIFRAS_FINA),
            admisible=phi_bck,
            unidad="",
            cita_umbral="AASHTO_LRFD_9.12.12.3.10.1e",
            descripcion_umbral="phi_bck (Tabla 12.5.5-1)",
            aplicacion="umbral duro de resistencia (LRFD)",
            criterio=CRITERIO_PARAMETROS_HDPE,
            cumple=ok_bck,
            margen=phi_bck - est["u_bck"],
            explicacion="el anillo no pandea" if ok_bck else
                     "el anillo pandea antes de agotar la pared",
            citas=("AASHTO_LRFD_9.12.12.3.3#PANDEO",
                   "AASHTO_LRFD_9.12.12.3.10.1c#EP", "AASHTO_LRFD_9.12.5.5"),
            nota="12.12.3.3 MANDA investigar el pandeo general con el modulo "
              "de la vida de diseño: u_letra. La suma por duracion del paso "
              "F8.EMPUJE (u_duracion) se conserva al lado y RIGE LA MAYOR, "
              "porque cual es mayor depende del suelo. Aqui gobierna "
              + ("la letra de 12.12.3.3." if gobierna_letra else
                 "la suma por duracion, que da mas que la letra.")
              + nota_cota)),
        numeral=NUMERAL_F8_HDPE)
    v_def = _verificacion_f8(paso("F8.HDPE_DEFLEXION", **_campos_f8(
            codigo=CODIGO_DEFLEXION,
            que="HDPE: deflexion vertical de servicio",
            formula="Delta_t = K_B (D_L P_sp + C_L P_L) D_o / (E_p I_p/R^3 + "
                 "0.061 M_s) + eps_sc D",
            formula_cita_id="AASHTO_LRFD_9.12.12.2.2",
            sust=(Magnitud("K_B", params["K_B"], "",
                       f"'{CRITERIO_PARAMETROS_HDPE}' [A]", cifras=CIFRAS_FINA),
              Magnitud("D_L", params["D_L"], "",
                       f"'{CRITERIO_PARAMETROS_HDPE}' [A]", cifras=CIFRAS_FACTOR),
              Magnitud("E_p", E_lp / KPA_POR_MPA, "MPa", f"modulo a {lp} años "
                       "(Tabla 12.12.3.3-1) en el termino de Spangler",
                       cifras=CIFRAS_FACTOR),
              Magnitud("eps_sc", est["eps_sc"], "", "deformacion de servicio, "
                       "con la misma suma por duracion",
                       cifras=CIFRAS_DEFORMACION),
              Magnitud("R", R, "m", "radio medio de la pared, (D + D_o)/4: la "
                       "tabla no da el centroide del perfil", cifras=CIFRAS_FINA)),
            obtenido=Magnitud("Delta_t", est["Delta"], "m", "deflexion total",
                          cifras=CIFRAS_FINA),
            admisible=Delta_A,
            unidad="m",
            cita_umbral="AASHTO_LRFD_9.C12.12.2.2",
            descripcion_umbral=f"{params['deflexion_admisible'] * 100:.1f} % "  # literal-ok: el 100 del porcentaje de presentacion
                            "del diametro",
            aplicacion="12.12.2.2 exige Delta_t <= Delta_A; el VALOR de "
                    "Delta_A (5 % del diametro) es la RECOMENDACION de su "
                    "comentario, que el proyecto adopta como umbral duro "
                    f"('{CRITERIO_PARAMETROS_HDPE}', deflexion_admisible)",
            criterio=CRITERIO_PARAMETROS_HDPE,
            cumple=ok_def,
            margen=Delta_A - est["Delta"],
            explicacion="deflexion dentro del limite" if ok_def else
                     "el tubo se ovaliza mas de lo admisible",
            citas=("AASHTO_LRFD_9.12.12.2.2",),
            nota=nota_cota.strip())),
        numeral=NUMERAL_F8_HDPE)
    v_ff = _verificacion_f8(paso("F8.HDPE_FF", **_campos_f8(
            codigo=CODIGO_FF,
            que="HDPE: factor de flexibilidad",
            formula="FF = S^2 / (E I)",
            formula_cita_id="AASHTO_LRFD_9.12.12.3.6",
            sust=(Magnitud("S", D_o * MILIMETROS_POR_METRO, "mm", "diametro "
                           "EXTERIOR del tubo: la norma dice «diameter of "
                           "pipe» y el exterior da el FF mayor",
                           cifras=CIFRAS_MAGNITUD),
                  Magnitud("E", E_inicial / KPA_POR_MPA, "MPa", "modulo "
                           "INICIAL del PE de M 294 (Tabla 12.12.3.3-1, 110 "
                           "ksi), como manda 12.12.3.6",
                           cifras=CIFRAS_FACTOR),
                  Magnitud("I", perfil["I_mm4_mm"], "mm4/mm", origen_perfil,
                           cifras=CIFRAS_MAGNITUD)),
            obtenido=Magnitud("FF", FF, "mm/N", "factor de flexibilidad",
                              cifras=CIFRAS_FINA),
            admisible=FF_lim,
            unidad="mm/N",
            cita_umbral="AASHTO_LRFD_9.12.5.6.3",
            descripcion_umbral="95.0 in/kip, tubo termoplastico (12.5.6.3)",
            aplicacion="exigencia de manejo e instalacion, umbral duro",
            criterio=CRITERIO_PERFIL_HDPE,
            cumple=ok_ff,
            margen=FF_lim - FF,
            explicacion="rigidez suficiente para el manejo y la compactacion"
                        if ok_ff else "el perfil es demasiado flexible",
            citas=("AASHTO_LRFD_9.12.12.3.6", "AASHTO_LRFD_9.TA12-11"),
            nota=nota_cota.strip())),
        numeral=NUMERAL_F8_HDPE)
    cumple_todo = ok_emp and ok_bck and ok_def and ok_ff
    pasos: List[PasoDeMemoria] = [cv.paso]
    H_max = None
    if cumple_todo:
        def _margen(H: float) -> float:
            e = _estado(H)
            return min(eps_lim - e["eps_uc"], phi_bck - e["u_bck"],
                       (Delta_A - e["Delta"]) / D)

        H_max = _relleno_maximo(_margen, H_rel, D, punto.id)
        pasos.append(paso(
            "F8.HDPE_EMPUJE", codigo="F8.HMAX",
            que=f"Relleno maximo sobre la clave del HDPE de {D_mm} mm",
            formula="H_max: la primera de las tres comprobaciones que se agota",
            sustitucion=(Magnitud("perfil", perfil_txt, "", "Table A12-11"
                                  if es_minimo else CRITERIO_PERFIL_HDPE),),
            resultado=Magnitud("H_max", H_max, "m", "relleno sobre la clave "
                               "hasta la subrasante", cifras=CIFRAS_MAGNITUD),
            citas_textuales=("AASHTO_LRFD_9.12.12.3.5",)))
    avisos = list(_aviso_de_carga_viva_despreciada(cv))
    if es_minimo:
        avisos.append(
            f"F8: HDPE de {D_mm} mm {ROTULO_HDPE_SIN_PRODUCTO}: calculado "
            "con el perfil minimo de la Tabla A12-11 de AASHTO LRFD, que su "
            "comentario C12.12.3.2 declara no significativo para el diseño. "
            "Es una cota inferior; falta el perfil del fabricante "
            f"('{CRITERIO_PERFIL_HDPE}')")
    if es_minimo:
        seleccion = (f"cota inferior con el perfil minimo de M 294, {D_mm} mm"
                     if cumple_todo else "")
    else:
        seleccion = (f"perfil declarado del fabricante, {D_mm} mm"
                     if cumple_todo else "")
    return ResultadoEstructural(
        material=TipoMaterial.HDPE.value, H_relleno_m=H_rel, e_paquete_m=e_paq,
        H_total_m=est["H_total"], seleccion=seleccion,
        relleno_maximo_m=H_max, verificaciones=(v_emp, v_bck, v_def, v_ff),
        pasos=tuple(pasos), avisos=tuple(avisos),
        diferido=(DIFERIDO_FLEXION_HDPE, DIFERIDO_PANDEO_LOCAL_HDPE),
        cota_inferior=es_minimo)


# ---------------------------------------------------------------------------
# Marco de concreto: demanda (AASHTO LRFD 12.11.2); el diseño se difiere
# ---------------------------------------------------------------------------

def demanda_marco(*, punto: PuntoCritico, material: Material,
                  seccion: Seccion, altura_relleno: float) -> DemandaMarco:
    """
    Demanda sobre la losa superior del marco (AASHTO LRFD 12.11.2):

        F_e = 1 + 0.20 H/B_c <= 1.15 (relleno compactado)   (12.11.2.2.1-2)
        w_EV = F_e (gamma_s H_rel + gamma_p e_paq); w_LL = P_L (3.6.1.2.6)
        w_u = eta (gamma_EV w_EV + gamma_LL w_LL)
        M_ref = w_u L^2 / 8, L = B + t

    M_ref es la cota superior del momento positivo de la losa como viga
    simplemente apoyada: una DEMANDA DE REFERENCIA en kN·m/m, no el momento
    del portico, cuyo analisis y diseño la hoja de ruta difiere al
    expediente. El peso propio de la losa no entra: necesita su canto y el
    peso del concreto, que son del diseño diferido.

    LA CARGA VIVA ES LA MAYOR PRESION DE LOS DOS VEHICULOS, aplicada a toda
    la luz: aqui la presion SI es la medida correcta, porque M_ref supone la
    carga uniforme en toda la luz, y eso es cota superior del momento de
    cualquiera de los dos (el del area mas larga y menos cargada del tandem
    no puede pasar de P_L,max L^2/8). Y la luz del PERMISO de 3.6.1.2.6a,
    cuando 'carga_viva_bajo_relleno_alto' lo toma, es en un marco de varias
    celdas la distancia entre las caras interiores de los muros extremos
    (N B + (N - 1) t, con los muros interiores del mismo espesor que los
    exteriores, a falta del diseño), no la luz de una celda.
    """
    t = espesor_pared(material, seccion.altura)
    B_c = seccion.ancho_exterior(t)
    e_paq = espesor_del_paquete(punto)
    H_rel = _finito_positivo("altura_relleno", altura_relleno, punto.id)
    H_total = H_rel + e_paq
    gamma_s, gamma_p, proc_gamma = pesos_especificos_de_carga(
        piso_tubo_concreto=False)
    F_e = min(1 + 0.20 * H_total / B_c,                    # literal-ok: el 0.20 de la Eq. 12.11.2.2.1-2
              _CN.FE_CAJON_MAX_COMPACTADO)
    w_EV = F_e * (gamma_s * H_rel + gamma_p * e_paq)
    N = numero_de_celdas(material)
    cv = carga_viva_enterrada(
        H=H_total, D_i=seccion.B, D_E=H_rel, conducto=CONDUCTO_CAJON,
        id_punto=punto.id, efecto=lambda P_L, _l_w: P_L,
        efecto_descripcion="P_L, kPa: la mayor presion, aplicada a toda la "
                           "luz (cota superior del momento de los dos)",
        luz_del_permiso=(N * seccion.B + (N - 1) * t if N > 1 else None))
    eta = _eta()
    gamma_EV, fila_EV = _gamma_ev_max(material)
    gamma_LL = _gamma_ll()
    w_u = eta * (gamma_EV * w_EV + gamma_LL * cv.P_L_kPa)
    L = seccion.B + t
    M_ref = w_u * L ** 2 / 8                                # literal-ok: el w L^2/8 de la viga simplemente apoyada
    p_tierra = paso(
        "F8.CARGA_TIERRA", codigo="F8.EV",
        que="Carga de tierra sobre la losa superior del marco",
        formula=("w_EV = F_e (gamma_s H_rel + gamma_p e_paq); "
                 "F_e = 1 + 0.20 H/B_c <= 1.15"),
        formula_cita_id="AASHTO_LRFD_9.12.11.2.2.1",
        citas_textuales=("MP.2.4.2.1#PESOS", "EG2013.205.12#COMPACTACION"),
        sustitucion=(
            Magnitud("F_e", F_e, "", "12.11.2.2.1, con el tope del relleno "
                     "compactado (la EG-2013 exige compactarlo)",
                     cifras=CIFRAS_FACTOR),
            Magnitud("B_c", B_c, "m", "ancho exterior", cifras=CIFRAS_MAGNITUD),
            Magnitud("gamma_s", gamma_s, "kN/m3", proc_gamma, cifras=CIFRAS_FACTOR),
            Magnitud("H_rel", H_rel, "m", "subrasante menos clave",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("e_paq", e_paq, "m", "rasante menos subrasante",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("w_EV", w_EV, "kPa", "presion de tierra sin factorar",
                           cifras=CIFRAS_MAGNITUD))
    p_demanda = paso(
        "F8.MARCO_DEMANDA", codigo="F8.MARCO",
        que=("Demanda de referencia de la losa superior en kN·m/m (el "
             "portico se analiza y se arma en su etapa, a expediente)"),
        formula="w_u = eta (gamma_EV w_EV + gamma_LL P_L); M_ref = w_u L^2/8",
        citas_textuales=("AASHTO_LRFD_9.12.11.2.1#LL",),
        sustitucion=(Magnitud("w_EV", w_EV, "kPa", "paso F8.EV",
                              cifras=CIFRAS_MAGNITUD),
                     Magnitud("P_L", cv.P_L_kPa, "kPa", "paso F8.LL",
                              cifras=CIFRAS_MAGNITUD),
                     Magnitud("eta", eta, "", f"'{CRITERIO_ETA_CONDUCTO}' [A]",
                              cifras=CIFRAS_FACTOR),
                     Magnitud("gamma_EV", gamma_EV, "", f"maximo de «{fila_EV}»",
                              cifras=CIFRAS_FACTOR),
                     Magnitud("gamma_LL", gamma_LL, "", "Resistencia I",
                              cifras=CIFRAS_FACTOR),
                     Magnitud("L", L, "m", "luz entre ejes de muros, B + t",
                              cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("M_ref", M_ref, "kN·m/m", "cota superior del "
                           "momento positivo de la losa (viga simplemente "
                           "apoyada); el portico lo reparte entre el centro y "
                           "las esquinas", cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=DIFERIDO_MARCO)
    return DemandaMarco(F_e=F_e, w_tierra_kPa=w_EV, w_viva_kPa=cv.P_L_kPa,
                        w_u_kPa=w_u, luz_m=L, M_u_referencia_kNm_m=M_ref,
                        pasos=(cv.paso, p_tierra, p_demanda))


# ---------------------------------------------------------------------------
# Las dos puertas: la de la Fase 5 y la de la etapa de la Fase 8
# ---------------------------------------------------------------------------

def bajo_el_dominio_de_la_rueda_distribuida(*, material: Material,
                                             H_total: float) -> bool:
    """
    True si el relleno hasta la rasante de un conducto REDONDO queda por
    debajo del dominio del metodo de 3.6.1.2.6a: menos de 2.0 ft sobre el
    tubo de concreto, 1.0 ft o menos sobre un flexible (VE-4f).
    """
    if material.tipo is TipoMaterial.CONCRETO_REFORZADO:
        return not H_total >= (_CN.RELLENO_MIN_METODO_TUBO_CONCRETO_M
                               - TOL_UMBRAL_NORMATIVO)
    return not H_total > (_CN.RELLENO_MIN_METODO_NO_CONCRETO_M
                          + TOL_UMBRAL_NORMATIVO)


def verificar_cobertura(*, punto: PuntoCritico, material: Material,
                        seccion: Seccion, altura_relleno: float
                        ) -> Verificacion:
    """
    --- VE-4f --- F8.COBERTURA: el relleno hasta la rasante frente a la
    cobertura minima de AASHTO LRFD 12.6.6.3 (Tabla 12.6.6.3-1, leida por
    `M7.cobertura_minima_aashto` con 'condicion_pavimento' [A]).

        H_total = H_rel + e_paq  >=  cobertura minima

    La fuente la cuenta «including a well-compacted granular subbase and base
    course», y por eso entra el paquete estructural: medirla hasta la
    rasante es lectura del proyecto (la base forma parte del paquete), y la
    G1 de la Fase 7 la vuelve a juzgar, hasta la subrasante, que es lo
    conservador. Se juzga SOLO por debajo del dominio de la rueda
    distribuida (`bajo_el_dominio_de_la_rueda_distribuida`): ahi el
    conducto sin cobertura INCUMPLE, y no es «no evaluable» (fundamento
    F8.COBERTURA). El marco no entra: la tabla no tiene fila de cajon.
    """
    from src.modulos.M7_geometria import (       # perezoso: M7 importa M5, que importa M8
        CRITERIO_COBERTURA_AASHTO, CRITERIO_CONDICION_PAVIMENTO,
        cobertura_minima_aashto)
    e_paq = espesor_del_paquete(punto)
    H_rel = _finito_positivo("altura_relleno", altura_relleno, punto.id)
    H_total = H_rel + e_paq
    minimo = cobertura_minima_aashto(material=material, seccion=seccion)
    condicion = ca.valor(CRITERIO_CONDICION_PAVIMENTO)
    cumple = H_total + TOL_UMBRAL_NORMATIVO >= minimo
    p = paso("F8.COBERTURA", **_campos_f8(
        codigo=CODIGO_COBERTURA,
        que=("Cobertura minima del conducto redondo con relleno por debajo "
             "del dominio de la rueda distribuida"),
        formula="H_total = H_rel + e_paq >= cobertura minima (Tabla 12.6.6.3-1)",
        formula_cita_id="AASHTO_LRFD_9.12.6.6.3#COBERTURA",
        sust=(Magnitud("H_rel", H_rel, "m", "subrasante menos clave fisica "
                       "(M5.altura_relleno_sobre_clave)",
                       cifras=CIFRAS_MAGNITUD),
              Magnitud("e_paq", e_paq, "m", "rasante menos subrasante: el "
                       "paquete, que la fuente cuenta en la cobertura "
                       "(«including a well-compacted granular subbase and "
                       "base course»)", cifras=CIFRAS_MAGNITUD)),
        obtenido=Magnitud("H_total", H_total, "m", "relleno sobre la clave "
                          "hasta la rasante", cifras=CIFRAS_MAGNITUD),
        admisible=minimo, unidad="m",
        cita_umbral="AASHTO_LRFD_9.T12.6.6.3-1",
        descripcion_umbral=(f"cobertura minima de la Tabla 12.6.6.3-1 para "
                            f"{material.tipo.value}, condicion «{condicion}» "
                            "('condicion_pavimento' [A])"),
        aplicacion=("umbral duro: un conducto redondo sin la cobertura minima "
                    "no se verifica con otra carga, incumple"),
        criterio=CRITERIO_COBERTURA_AASHTO,
        cumple=cumple, margen=H_total - minimo,
        explicacion=("el conducto tiene la cobertura minima" if cumple else
                     "el relleno hasta la rasante no alcanza la cobertura "
                     "minima: subir la rasante o bajar el conducto"),
        citas=("AASHTO_LRFD_9.3.6.1.2.6a#MENOS_DE_UN_PIE",),
        nota=("Se juzga porque el relleno queda por debajo del dominio de la "
              "rueda distribuida de 3.6.1.2.6a. Medida hasta la rasante: la "
              "G1 de la Fase 7 la juzga tambien hasta la subrasante.")))
    return _verificacion_f8(p, numeral=NUMERAL_F8_COBERTURA)


def verificar_conducto(*, punto: PuntoCritico, material: Material,
                       seccion: Seccion, altura_relleno: float
                       ) -> ResultadoEstructural:
    """
    La Fase 8 del conducto, por material y forma. Para el marco devuelve la
    DEMANDA, sin verificaciones: el portico lo analiza y lo arma
    `disenar_portico`, en su propia etapa del servicio (VE-5).

    --- VE-4f --- Con el relleno de un conducto REDONDO por debajo del
    dominio de la rueda distribuida, primero F8.COBERTURA (12.6.6.3): si
    incumple, el resultado lleva SOLO esa verificacion y nada elegido (no
    hay carga que calcular sobre un conducto que no puede quedar ahi); si
    cumple, va delante de las del material, que con relleno somero usan la
    franja de 4.6.2.10.2 (tubo de concreto) o se detienen sin metodo.
    """
    if material.forma is FormaSeccion.RECTANGULAR:
        dem = demanda_marco(punto=punto, material=material, seccion=seccion,
                            altura_relleno=altura_relleno)
        e_paq = espesor_del_paquete(punto)
        return ResultadoEstructural(
            material=ELEMENTO_CAJON, H_relleno_m=altura_relleno,
            e_paquete_m=e_paq, H_total_m=altura_relleno + e_paq, seleccion="",
            relleno_maximo_m=None, verificaciones=(), pasos=dem.pasos,
            diferido=(DIFERIDO_MARCO, DIFERIDO_EMPUJE_LATERAL_MARCO),
            demanda_marco=dem)
    funcion = {TipoMaterial.CONCRETO_REFORZADO: verificar_concreto,
               TipoMaterial.TMC: verificar_tmc,
               TipoMaterial.HDPE: verificar_hdpe}[material.tipo]
    e_paq = espesor_del_paquete(punto)
    H_rel = _finito_positivo("altura_relleno", altura_relleno, punto.id)
    if not bajo_el_dominio_de_la_rueda_distribuida(material=material,
                                                   H_total=H_rel + e_paq):
        return funcion(punto=punto, material=material, seccion=seccion,
                       altura_relleno=altura_relleno)
    v_cob = verificar_cobertura(punto=punto, material=material,
                                seccion=seccion, altura_relleno=altura_relleno)
    if not v_cob.cumple:
        return ResultadoEstructural(
            material=material.tipo.value, H_relleno_m=H_rel, e_paquete_m=e_paq,
            H_total_m=H_rel + e_paq, seleccion="", relleno_maximo_m=None,
            verificaciones=(v_cob,), pasos=(v_cob.paso,))
    r = funcion(punto=punto, material=material, seccion=seccion,
                altura_relleno=altura_relleno)
    return replace(r, verificaciones=(v_cob,) + r.verificaciones,
                   pasos=(v_cob.paso,) + r.pasos)


def verificaciones_estructurales(*, punto: PuntoCritico, material: Material,
                                 seccion: Seccion, altura_relleno: float
                                 ) -> Tuple[Verificacion, ...]:
    """
    Lo que la Fase 5 suma a su tabla: las verificaciones F8.* que deciden si
    la combinacion material / diametro / plancha / clase EXISTE. El marco no
    aporta ninguna --su diseño se difiere; la demanda se calcula en la etapa
    de la Fase 8--.
    """
    if material.forma is FormaSeccion.RECTANGULAR:
        return ()
    return verificar_conducto(punto=punto, material=material, seccion=seccion,
                              altura_relleno=altura_relleno).verificaciones


# ===========================================================================
# --- VE-5 (m8), item 1 del censo --- EL PORTICO DEL MARCO (ficha T5-07)
# ===========================================================================
# Hasta aqui la Fase 8 del marco calculaba la DEMANDA de referencia de la
# losa superior y el portico se difería («diseño completo por AASHTO LRFD
# Seccion 5», Fase 8 de la v8). Desde VE-5 se ANALIZA y se ARMA:
#
#   1. el portico cerrado de ejes (una o varias celdas) por RIGIDEZ DIRECTA
#      exacta (`_ModeloPortico`): elementos de barra con deformacion axial y
#      de flexion, vector de carga consistente con las funciones de Hermite
#      (exacto para cargas lineales por tramos) y la cartela, si la hay,
#      como canto creciente junto a cada cara. Contrastado con el ejemplo
#      resuelto de MnDOT, LRFD Bridge Design Manual §12.5 (cajon de 10 x 10
#      ft, Tabla 12.5.2) y con la solucion cerrada del marco rectangular
#      cerrado (tests/test_ve5_portico_marco.py);
#   2. las cargas de 12.11.2 y Tabla 3.4.1-1: DC (losa superior y paredes;
#      la losa inferior apoya en el suelo), EV (12.11.2.2.1), EH en REPOSO
#      (3.11.5.2, decision del dueño), LS (3.11.6.4), WA (agua interior) y
#      la carga viva HL-93 de 3.6.1.2.6 o de la franja de 4.6.2.10 movida a
#      lo largo de la losa superior, con la reaccion del suelo lineal bajo la
#      losa inferior (12.11.2.3);
#   3. las tres combinaciones de C12.11.2.1 en Resistencia I y Servicio I,
#      las de horizontal maximo con LS y sin LS, con el eta del conducto
#      (1.3.2.1) y la reduccion del 50 % de 3.11.7 SOLO en el momento
#      positivo de la losa superior (decision del dueño);
#   4. el armado de cada seccion con el del cabezal (`M9.diseno_flexion_corte`:
#      flexion de 5.6, cortante de 5.7 --que 5.12.7.3 deja en pie--, minimos
#      de 5.6.3.3 y 5.10.6 con los de E.060, y fisuracion de 5.6.7), con los
#      factores de resistencia del cajon vaciado in situ (Tabla 12.5.5-1:
#      0.90 y 0.85).
#
# LOS CANTOS. La geometria del portico los separa (`GeometriaPortico`:
# losas, paredes, tabiques), como decidio el dueño; la del PROGRAMA tiene
# todavia uno solo, 'espesor_pared_cajon', con el que M2, M5 y M7 forman la
# clave fisica, el relleno y V7. Hasta que esa geometria los separe, el
# portico se analiza con ese espesor en los cuatro (ficha T5-07).

CRITERIO_PHI_RELLENO = "phi_relleno_trasdos"
CARGA_EMPUJE = "EH"
FILA_EH_DEL_CAJON = "EH"
ELEMENTO_PORTICO = "portico"
CODIGO_PASO_PORTICO_CARGAS = "F8.PORTICO_CARGAS"
CODIGO_PASO_PORTICO_COMBINACIONES = "F8.PORTICO_COMBINACIONES"
CODIGO_PASO_PORTICO_ANALISIS = "F8.PORTICO_ANALISIS"
CODIGO_PASO_PORTICO_MINIMOS = "F8.PORTICO_MINIMOS"      # VE-7 lote B, B4
CODIGO_PASO_PORTICO_CANTO = "F8.PORTICO_CANTO"          # VE-7 lote B, B5
CRITERIO_ESPESOR_CAJON = "espesor_pared_cajon"
NUMERAL_F8_PORTICO = ("AASHTO LRFD 12.11 (12.11.2, 12.11.4, 12.11.5) y "
                      "Seccion 5; Tabla 3.4.1-1 del Manual de Puentes")

MIEMBRO_LOSA_SUPERIOR = "losa_superior"
MIEMBRO_LOSA_INFERIOR = "losa_inferior"
MIEMBRO_PARED = "pared"

CASO_DC = "DC"
CASO_EV = "EV"
CASO_EH = "EH"
CASO_LS = "LS"
CASO_WA = "WA"
CASO_LL = "LL+IM"
CASOS_PERMANENTES = (CASO_DC, CASO_EV, CASO_EH, CASO_LS, CASO_WA)
# --- VE-7 lote B, B3 (T5-07 (5)) --- el agua EXTERIOR sobre las paredes, con
# el nivel freatico sobre el eje de la losa inferior. Solo existe en esos
# puntos: sin el, los casos y las envolventes son los de antes.
CASO_WA_EXT = "WA_ext"
# --- VE-7, dictamen Fable (decision 3) --- con el nivel sobre la losa
# superior: lo que el relleno sumergido le quita al EV seco (F_e sigma'_v
# menos F_e sigma_v, con gamma_EV) y el agua sobre la losa (gamma_w d_w, con
# gamma_WA). Entran en combinaciones DUPLICADAS: la envolvente seco/sumergido.
CASO_EV_SUM = "EV_sum"
CASO_WA_SUP = "WA_sup"
SUFIJO_SUMERGIDO = " (relleno sumergido sobre la losa superior)"

ESTADO_RESISTENCIA = "Resistencia I"
ESTADO_SERVICIO = "Servicio I"
CARA_INTERIOR = "interior"
CARA_EXTERIOR = "exterior"
SECCION_CENTRO = "centro"

# Lo que el resultado del marco dice diferido y el portico, si corre, cierra
# (`servicio._fase_8` los cambia por `DIFERIDO_PORTICO`).
DIFERIDOS_QUE_EL_PORTICO_CIERRA = (DIFERIDO_MARCO, DIFERIDO_EMPUJE_LATERAL_MARCO)

DIFERIDO_PORTICO = (
    "Del portico del marco sigue fuera: (1) los cantos separados de losa y "
    "pared EN LA GEOMETRIA DEL PROGRAMA (M2, M5 y M7 forman la clave fisica "
    "con 'espesor_pared_cajon', y el portico se analiza con ese espesor en "
    "losas, paredes y tabiques); (2) el refuerzo de distribucion de la losa "
    "superior con menos de 2.0 ft de relleno (9.7.3.2, que 12.11.2.1 manda) "
    "y las vigas de borde de C12.11.2.1; (3) [desde VE-7 el acero de las "
    "caras que no se traccionan se tabula con el minimo de 5.10.6]; (4) el "
    "desarrollo y los empalmes de las barras; (5) [desde VE-7 el agua "
    "EXTERIOR entra en las paredes con el nivel sobre la losa inferior, y "
    "sobre la losa superior con la envolvente seco/sumergido]; y (6) "
    "el V_c de la Eq. 5.12.7.3-1 para las losas con 2.0 ft o mas, que la "
    "fuente PERMITE y el proyecto no toma (rige 5.7)")


# ---------------------------------------------------------------------------
# El modelo: rigidez directa del portico cerrado
# ---------------------------------------------------------------------------

# Los grados de libertad de un elemento de portico plano: u, v, giro en cada
# nudo. Con nombre, para que la matriz se lea sin indices sueltos.
_U1, _V1, _G1, _U2, _V2, _G2 = range(6)                   # literal-ok: 3 grados de libertad por nudo, 2 nudos
_GDL_POR_NUDO = _U2
_GDL_ELEMENTO = 2 * _GDL_POR_NUDO
# Cuadratura de Gauss de tres puntos: exacta para polinomios de grado 5, y
# el producto de una funcion de Hermite (cubica) por una carga lineal es de
# grado 4.
_GAUSS_3 = ((-math.sqrt(3 / 5), 5 / 9), (0.0, 8 / 9),     # literal-ok: puntos y pesos de Gauss-Legendre de 3 puntos
            (math.sqrt(3 / 5), 5 / 9))                     # literal-ok: puntos y pesos de Gauss-Legendre de 3 puntos


def _rigidez_local(EA: float, EI: float, l: float):
    """Matriz de rigidez de un elemento de portico plano (Euler-Bernoulli,
    con deformacion axial), ejes locales."""
    import numpy as np
    k = np.zeros((_GDL_ELEMENTO, _GDL_ELEMENTO))
    a = EA / l
    b, c, d, e = (12 * EI / l ** 3, 6 * EI / l ** 2,      # literal-ok: coeficientes de la viga de Euler-Bernoulli
                  4 * EI / l, 2 * EI / l)                  # literal-ok: coeficientes de la viga de Euler-Bernoulli
    k[_U1, _U1] = k[_U2, _U2] = a
    k[_U1, _U2] = k[_U2, _U1] = -a
    k[_V1, _V1] = k[_V2, _V2] = b
    k[_V1, _V2] = k[_V2, _V1] = -b
    k[_V1, _G1] = k[_G1, _V1] = k[_V1, _G2] = k[_G2, _V1] = c
    k[_G1, _V2] = k[_V2, _G1] = k[_V2, _G2] = k[_G2, _V2] = -c
    k[_G1, _G1] = k[_G2, _G2] = d
    k[_G1, _G2] = k[_G2, _G1] = e
    return k


def _rotacion(c: float, s: float):
    """Transformacion de ejes globales a locales de un elemento."""
    import numpy as np
    t = np.zeros((_GDL_ELEMENTO, _GDL_ELEMENTO))
    for u, v, g in ((_U1, _V1, _G1), (_U2, _V2, _G2)):
        t[u, u] = t[v, v] = c
        t[u, v], t[v, u] = s, -s
        t[g, g] = 1.0
    return t


def _carga_consistente(l: float, s0: float, s1: float, p0: float, p1: float,
                       q0: float, q1: float):
    """
    Vector de cargas nodales consistente de un elemento de largo l con una
    carga axial p y transversal q, LINEALES entre s0 y s1 (ejes locales):
    integral de las funciones de forma (lineales en axial, de Hermite en
    flexion) por la carga, con Gauss de 3 puntos (exacto). Con el vector
    consistente los desplazamientos nodales y los esfuerzos en los extremos
    del elemento son exactos.
    """
    import numpy as np
    F = np.zeros(_GDL_ELEMENTO)
    h, m = (s1 - s0) / 2, (s1 + s0) / 2
    for xi, w in _GAUSS_3:
        x = m + h * xi
        t = (x - s0) / (s1 - s0)
        p, q = p0 + (p1 - p0) * t, q0 + (q1 - q0) * t
        r = x / l
        N = np.array([1 - r, 1 - 3 * r ** 2 + 2 * r ** 3,          # literal-ok: funciones de forma de Hermite
                      l * (r - 2 * r ** 2 + r ** 3), r,             # literal-ok: funciones de forma de Hermite
                      3 * r ** 2 - 2 * r ** 3, l * (r ** 3 - r ** 2)])  # literal-ok: funciones de forma de Hermite
        F += w * h * N * np.array([p, q, q, p, q, q])
    return F


class _Miembro:
    """Una losa (de una celda) o una pared del portico, con su orientacion."""

    def __init__(self, nombre: str, tipo: str, nodo_i: str, nodo_j: str,
                 xi: float, yi: float, xj: float, yj: float, espesor: float,
                 cara_i: float, cara_j: float, cartela: float):
        self.nombre, self.tipo = nombre, tipo
        self.nodo_i, self.nodo_j = nodo_i, nodo_j
        self.xi, self.yi, self.xj, self.yj = xi, yi, xj, yj
        self.L = math.hypot(xj - xi, yj - yi)
        self.c, self.s = (xj - xi) / self.L, (yj - yi) / self.L
        self.espesor, self.cara_i, self.cara_j = espesor, cara_i, cara_j
        self.cartela = cartela

    def canto(self, s: float) -> float:
        """El canto en la abscisa local s: el del miembro mas la cartela a
        45 grados junto a cada cara (y entera dentro del nudo)."""
        if not self.cartela > 0:
            return self.espesor
        distancia = min(s - self.cara_i, self.L - self.cara_j - s)
        return self.espesor + max(0.0, min(self.cartela,
                                           self.cartela - distancia))


def _miembros_del_portico(g: GeometriaPortico) -> List[_Miembro]:
    """
    Las losas y las paredes en ejes, orientadas para que el momento con
    signo de viga (positivo traccionando el lado derecho del sentido de
    avance) sea el que tracciona la CARA INTERIOR de la celda: la losa
    superior de izquierda a derecha, la inferior de derecha a izquierda, la
    pared izquierda de abajo arriba y la derecha de arriba abajo. Los
    tabiques van de abajo arriba: su momento positivo tracciona la cara que
    mira a la celda de su derecha.
    """
    x = g.ejes_x_m
    h = g.altura_ejes_m
    N = g.n_celdas
    t_sup, t_inf = g.t_losa_superior_m, g.t_losa_inferior_m
    miembros = []
    for c in range(N):
        a, b = g.espesor_de_pared(c) / 2, g.espesor_de_pared(c + 1) / 2
        miembros.append(_Miembro(f"{MIEMBRO_LOSA_SUPERIOR}_{c + 1}",
                                 MIEMBRO_LOSA_SUPERIOR, f"T{c}", f"T{c + 1}",
                                 x[c], h, x[c + 1], h, t_sup, a, b,
                                 g.cartela_m))
        miembros.append(_Miembro(f"{MIEMBRO_LOSA_INFERIOR}_{c + 1}",
                                 MIEMBRO_LOSA_INFERIOR, f"B{c + 1}", f"B{c}",
                                 x[c + 1], 0.0, x[c], 0.0, t_inf, b, a,
                                 g.cartela_m))
    for j in range(N + 1):
        t = g.espesor_de_pared(j)
        if j == N:
            miembros.append(_Miembro(f"{MIEMBRO_PARED}_{j}", MIEMBRO_PARED,
                                     f"T{j}", f"B{j}", x[j], h, x[j], 0.0, t,
                                     t_sup / 2, t_inf / 2, g.cartela_m))
        else:
            miembros.append(_Miembro(f"{MIEMBRO_PARED}_{j}", MIEMBRO_PARED,
                                     f"B{j}", f"T{j}", x[j], 0.0, x[j], h, t,
                                     t_inf / 2, t_sup / 2, g.cartela_m))
    return miembros


class _ModeloPortico:
    """
    El portico cerrado por rigidez directa, ensamblado y factorizado UNA vez
    para todos los casos de carga (las posiciones de la carga viva son solo
    vectores de carga nuevos). Apoyos: articulacion en el nudo inferior
    izquierdo y rodillo en el inferior derecho (el modelo de MnDOT §12.5):
    las cargas que se le aplican estan en equilibrio --la reaccion del suelo
    bajo la losa inferior equilibra lo vertical y el momento--, y los dos
    apoyos solo fijan el movimiento de cuerpo rigido.

    El modulo de elasticidad no entra: es el mismo en todos los miembros, y
    los esfuerzos de un portico hiperestatico dependen de las rigideces
    RELATIVAS. Se toma la unidad.
    """

    def __init__(self, g: GeometriaPortico):
        import numpy as np
        from scipy.sparse import coo_matrix          # perezoso (PC-10), como M4
        from scipy.sparse.linalg import splu
        self.g = g
        self.miembros = {m.nombre: m for m in _miembros_del_portico(g)}
        self._nudo = {}
        coords = []

        def nudo(clave, x, y):
            if clave not in self._nudo:
                self._nudo[clave] = len(coords)
                coords.append((x, y))
            return self._nudo[clave]

        self.elementos = []      # (miembro, i, j, s0, s1, EA, EI)
        for m in self.miembros.values():
            ni = nudo(m.nodo_i, m.xi, m.yi)
            nj = nudo(m.nodo_j, m.xj, m.yj)
            estaciones = {0.0, m.L, m.L / 2, m.cara_i, m.L - m.cara_j,
                          m.cara_i + m.cartela, m.L - m.cara_j - m.cartela}
            estaciones |= {m.L * k / DIVISIONES_MIEMBRO_PORTICO
                           for k in range(1, DIVISIONES_MIEMBRO_PORTICO)}
            # Con cartela, la seccion variable se parte mas fino (el canto
            # de cada elemento es el de su punto medio).
            if m.cartela > 0:
                paso_c = m.cartela / DIVISIONES_MIEMBRO_PORTICO
                for k in range(1, DIVISIONES_MIEMBRO_PORTICO):
                    estaciones |= {m.cara_i + k * paso_c,
                                   m.L - m.cara_j - k * paso_c}
            est = sorted(e for e in estaciones if 0.0 <= e <= m.L)
            limpias = [est[0]]
            for e in est[1:]:
                if e - limpias[-1] > TOL_UMBRAL_NORMATIVO:
                    limpias.append(e)
            limpias[-1] = m.L
            m.estaciones = tuple(limpias)
            previo = ni
            for k in range(len(limpias) - 1):
                s0, s1 = limpias[k], limpias[k + 1]
                siguiente = (nj if k + 2 == len(limpias) else
                             nudo((m.nombre, k + 1), m.xi + m.c * s1,
                                  m.yi + m.s * s1))
                t = m.canto((s0 + s1) / 2)
                self.elementos.append(
                    (m, previo, siguiente, s0, s1, t,
                     t ** 3 / 12))                         # literal-ok: inercia de la seccion rectangular b h^3/12
                previo = siguiente
        n = len(coords) * _GDL_POR_NUDO
        izq, der = self._nudo["B0"], self._nudo[f"B{g.n_celdas}"]
        fijos = {_GDL_POR_NUDO * izq + _U1, _GDL_POR_NUDO * izq + _V1,
                 _GDL_POR_NUDO * der + _V1}
        self.libres = [i for i in range(n) if i not in fijos]
        reducido = {gl: k for k, gl in enumerate(self.libres)}
        filas, columnas, valores = [], [], []
        for (m, a, b, s0, s1, EA, EI) in self.elementos:
            t = _rotacion(m.c, m.s)
            kg = t.T @ _rigidez_local(EA, EI, s1 - s0) @ t
            dofs = self._gl(a, b)
            for p_, gp in enumerate(dofs):
                if gp not in reducido:
                    continue
                for q_, gq in enumerate(dofs):
                    if gq in reducido:
                        filas.append(reducido[gp])
                        columnas.append(reducido[gq])
                        valores.append(kg[p_, q_])
        m_ = len(self.libres)
        self.n = n
        # Matriz dispersa y factorizacion LU dispersa: la densa tardaba
        # segundos en una maquina compartida, y la del portico es de banda.
        self._lu = splu(coo_matrix((valores, (filas, columnas)),
                                   shape=(m_, m_)).tocsc())

    @staticmethod
    def _gl(a: int, b: int):
        return ([_GDL_POR_NUDO * a + k for k in (_U1, _V1, _G1)]
                + [_GDL_POR_NUDO * b + k for k in (_U1, _V1, _G1)])

    def resolver(self, cargas):
        """
        Los esfuerzos de un caso de carga: {miembro: {s: (N, V, M)}} en cada
        estacion, con N positivo en traccion, V el cortante de viga y M
        positivo traccionando la cara interior. `cargas` son tuplas
        (miembro, s_a, s_b, qx_a, qx_b, qy_a, qy_b): carga repartida lineal
        entre las abscisas locales s_a y s_b, en kN/m por metro de marco,
        con sus componentes en ejes GLOBALES.
        """
        import numpy as np
        F = np.zeros(self.n)
        locales = []
        for (m, a, b, s0, s1, EA, EI) in self.elementos:
            Fl = np.zeros(_GDL_ELEMENTO)
            for (nombre, sa, sb, qxa, qxb, qya, qyb) in cargas:
                if nombre != m.nombre:
                    continue
                lo, hi = max(sa, s0), min(sb, s1)
                if not hi > lo + TOL_UMBRAL_NORMATIVO:
                    continue
                f_lo, f_hi = (lo - sa) / (sb - sa), (hi - sa) / (sb - sa)
                qx0, qx1 = qxa + (qxb - qxa) * f_lo, qxa + (qxb - qxa) * f_hi
                qy0, qy1 = qya + (qyb - qya) * f_lo, qya + (qyb - qya) * f_hi
                Fl += _carga_consistente(
                    s1 - s0, lo - s0, hi - s0,
                    m.c * qx0 + m.s * qy0, m.c * qx1 + m.s * qy1,
                    -m.s * qx0 + m.c * qy0, -m.s * qx1 + m.c * qy1)
            F[self._gl(a, b)] += _rotacion(m.c, m.s).T @ Fl
            locales.append(Fl)
        u = np.zeros(self.n)
        u[self.libres] = self._lu.solve(F[self.libres])
        res = {}
        for (m, a, b, s0, s1, EA, EI), Fl in zip(self.elementos, locales):
            ul = _rotacion(m.c, m.s) @ u[self._gl(a, b)]
            f = _rigidez_local(EA, EI, s1 - s0) @ ul - Fl
            por_s = res.setdefault(m.nombre, {})
            # Los esfuerzos salen como `float` de Python, no `numpy.float64`:
            # el informe se embebe en la sesion (`serializacion_informe`) y
            # un `numpy.bool` derivado de ellos (la fisuracion) no se escribe.
            por_s.setdefault(s0, (float(-f[_U1]), float(f[_V1]), float(-f[_G1])))
            por_s[s1] = (float(f[_U2]), float(-f[_V2]), float(f[_G2]))
        return res


# ---------------------------------------------------------------------------
# Las secciones de diseño y la geometria del punto
# ---------------------------------------------------------------------------

def geometria_del_portico(*, material: Material,
                          seccion: Seccion) -> GeometriaPortico:
    """
    La geometria del portico de la seccion adoptada: N celdas de B x H con
    el espesor que el programa usa para el marco ('espesor_pared_cajon', via
    `espesor_pared`) en las losas, las paredes y los tabiques, sin cartelas
    (el catalogo no las lleva). Los cantos separados existen en
    `GeometriaPortico`; la geometria del programa todavia no los tiene
    (ficha T5-07).
    """
    if not isinstance(seccion, SeccionRectangular):
        raise DatoInvalidoError(
            campo="seccion", valor=seccion,
            motivo="el portico es del marco: hace falta una seccion "
                   "rectangular")
    t = espesor_pared(material, seccion.altura)
    return GeometriaPortico(
        n_celdas=numero_de_celdas(material), luz_libre_m=seccion.B,
        altura_libre_m=seccion.H, t_losa_superior_m=t, t_losa_inferior_m=t,
        t_pared_m=t, t_tabique_m=t)


def secciones_del_portico(g: GeometriaPortico):
    """
    Las secciones de diseño: (nombre, miembro, s, canto, descripcion, es
    centro de losa superior, cara exterior contra el suelo). En cada losa,
    el centro y las dos caras de las paredes; en cada pared, las dos caras
    de las losas y el centro de la altura libre. Con cartela, las de borde
    se toman donde la cartela termina (12.11.5.2 lo permite para el acero
    negativo).
    """
    secciones = []
    for m in _miembros_del_portico(g):
        if m.tipo == MIEMBRO_PARED:
            j = int(m.nombre.rsplit("_", 1)[1])
            sube = not j == g.n_celdas
            abajo = m.cara_i + m.cartela if sube else m.L - m.cara_j - m.cartela
            arriba = m.L - m.cara_j - m.cartela if sube else m.cara_i + m.cartela
            centro = (abajo + arriba) / 2
            for etiqueta, s in (("superior", arriba), (SECCION_CENTRO, centro),
                                ("inferior", abajo)):
                secciones.append((f"{m.nombre}_{etiqueta}", m.nombre, s,
                                  m.espesor, f"pared {j}, {etiqueta}", False,
                                  False))
        else:
            celda = m.nombre.rsplit("_", 1)[1]
            superior = m.tipo == MIEMBRO_LOSA_SUPERIOR
            nombre_losa = "losa superior" if superior else "losa inferior"
            i_, j_ = (("izquierda", "derecha") if superior
                      else ("derecha", "izquierda"))
            for etiqueta, s in ((i_, m.cara_i + m.cartela),
                                (SECCION_CENTRO, m.L / 2),
                                (j_, m.L - m.cara_j - m.cartela)):
                secciones.append((f"{m.nombre}_{etiqueta}", m.nombre, s,
                                  m.espesor,
                                  f"{nombre_losa}, celda {celda}, {etiqueta}",
                                  superior and etiqueta == SECCION_CENTRO,
                                  not superior))
    return tuple(secciones)


def largos_de_los_miembros(g: GeometriaPortico) -> dict:
    """
    --- VE-7 lote B, B6 --- {miembro: largo entre ejes, m} de las losas, las
    paredes y los tabiques del portico (`_miembros_del_portico`). Lo lee el
    metrado del acero del portico (`M12.renglones_acero_portico`).
    """
    return {m.nombre: m.L for m in _miembros_del_portico(g)}


def miembros_de_las_secciones(g: GeometriaPortico) -> dict:
    """--- VE-7 lote B, B6 --- {seccion de diseño: miembro al que pertenece}."""
    return {nombre: miembro
            for (nombre, miembro, *_r) in secciones_del_portico(g)}


def _esfuerzos(res, secciones) -> dict:
    """{seccion: (M, |V|, N de compresion)} de un resultado del modelo."""
    salida = {}
    for (nombre, miembro, s, *_r) in secciones:
        por_s = res[miembro]
        clave = min(por_s, key=lambda x: abs(x - s))
        N, V, M = por_s[clave]
        salida[nombre] = (M, abs(V), -N)
    return salida


# ---------------------------------------------------------------------------
# Las cargas
# ---------------------------------------------------------------------------

def _en_la_losa(g: GeometriaPortico, tipo: str, x_a: float, x_b: float,
                q_a: float, q_b: float):
    """Una carga vertical (global y) lineal entre las abscisas GLOBALES x_a
    y x_b de la losa superior o inferior, partida por celdas y llevada a las
    abscisas locales de cada losa."""
    x = g.ejes_x_m
    cargas = []
    for c in range(g.n_celdas):
        lo, hi = max(x_a, x[c]), min(x_b, x[c + 1])
        if not hi > lo + TOL_UMBRAL_NORMATIVO:
            continue
        q_lo = q_a + (q_b - q_a) * (lo - x_a) / (x_b - x_a)
        q_hi = q_a + (q_b - q_a) * (hi - x_a) / (x_b - x_a)
        nombre = f"{tipo}_{c + 1}"
        if tipo == MIEMBRO_LOSA_SUPERIOR:
            cargas.append((nombre, lo - x[c], hi - x[c], 0.0, 0.0, q_lo, q_hi))
        else:
            cargas.append((nombre, x[c + 1] - hi, x[c + 1] - lo, 0.0, 0.0,
                           q_hi, q_lo))
    return cargas


def _en_la_pared(g: GeometriaPortico, j: int, y_a: float, y_b: float,
                 p_a: float, p_b: float):
    """Una carga horizontal (global x) lineal entre las ordenadas GLOBALES
    y_a y y_b (0 en el eje de la losa inferior) de la pared j."""
    h = g.altura_ejes_m
    nombre = f"{MIEMBRO_PARED}_{j}"
    if j == g.n_celdas:
        return [(nombre, h - y_b, h - y_a, p_b, p_a, 0.0, 0.0)]
    return [(nombre, y_a, y_b, p_a, p_b, 0.0, 0.0)]


def _reaccion_del_suelo(g: GeometriaPortico, verticales,
                        puntuales=()) -> list:
    """
    La reaccion del suelo bajo la losa inferior que equilibra las cargas
    verticales `verticales` (lista de (x_a, x_b, q_a, q_b) en ejes globales,
    q hacia arriba positivo): LINEAL, con la misma resultante y el mismo
    momento (uniforme si la carga esta centrada, trapecial si no; 12.11.2.3
    y su comentario). `puntuales` son cargas concentradas (x, F): el peso de
    cada pared, que baja por ella hasta la losa inferior.
    """
    L = g.ejes_x_m[-1]
    F = M = 0.0
    for (x_p, F_p) in puntuales:
        F += F_p
        M += F_p * (x_p - L / 2)
    for (x_a, x_b, q_a, q_b) in verticales:
        largo = x_b - x_a
        F_i = (q_a + q_b) / 2 * largo
        # Centroide del trapecio desde x_a.
        x_c = (x_a + largo * (q_a + 2 * q_b) / (3 * (q_a + q_b))    # literal-ok: centroide del trapecio
               if abs(q_a + q_b) > TOL_UMBRAL_NORMATIVO else (x_a + x_b) / 2)
        F += F_i
        M += F_i * (x_c - L / 2)
    q_medio = -F / L
    pendiente = -12 * M / L ** 3                           # literal-ok: momento de inercia de la distribucion lineal L^3/12
    return _en_la_losa(g, MIEMBRO_LOSA_INFERIOR, 0.0, L,
                       q_medio - pendiente * L / 2,
                       q_medio + pendiente * L / 2)


def _k0(id_punto=None) -> Tuple[float, float]:
    """(phi'_f, k_o = 1 - sen phi'_f) del relleno (3.11.5.2)."""
    phi = ca.valor(CRITERIO_PHI_RELLENO)
    if isinstance(phi, bool) or not isinstance(phi, (int, float)) \
            or not math.isfinite(phi) or not 0 < phi < 90:  # literal-ok: el angulo de friccion esta entre 0 y 90 grados
        raise DatoInvalidoError(
            campo=CRITERIO_PHI_RELLENO, valor=phi, id_punto=id_punto,
            motivo="el angulo de friccion del relleno es un numero entre 0 y "
                   "90 grados")
    return float(phi), 1.0 - math.sin(math.radians(phi))


def _h_eq_portico(altura_m: float) -> Tuple[float, str]:
    """
    La altura de suelo equivalente de la sobrecarga viva sobre las paredes
    del marco (3.11.6.4): la Tabla 3.11.6.4-1 (estribos perpendiculares al
    trafico) con la «wall height» desde la rasante hasta la cara inferior
    de la losa inferior, interpolada, y el piso del Manual de Puentes
    2.4.2.2 (0.60 m), gobierna el mayor (la regla del cabezal,
    `M9.h_eq_sobrecarga_trasdos`). Las paredes del marco son perpendiculares
    al trafico porque la carga viva supone el trafico PARALELO al vano
    (3.6.1.2.6a): ANALOGIA [N->], la misma que el cabezal declara.
    """
    filas = sorted(_CN.H_EQ_ESTRIBO_PERPENDICULAR_FT.values())
    alturas = [a for a, _h in filas]
    h_eq_ft = _interpolar(altura_m / PIE_EN_METROS, alturas,
                          [h for _a, h in filas])
    h_tabla = h_eq_ft * PIE_EN_METROS
    piso = _CN.SOBRECARGA_TRASDOS_PISO_MP_M
    if h_tabla >= piso:
        return h_tabla, (f"Tabla 3.11.6.4-1 en {altura_m:.2f} m de altura "
                         "(rasante a la cara inferior de la losa inferior), "
                         "por analogia con un estribo perpendicular al "
                         "trafico; mayor que el piso de 0.60 m del Manual de "
                         "Puentes 2.4.2.2")
    return piso, ("piso de 0.60 m del Manual de Puentes 2.4.2.2, mayor que "
                  f"la Tabla 3.11.6.4-1 en {altura_m:.2f} m")


def _casos_de_carga(*, punto: PuntoCritico, material: Material,
                    seccion: Seccion, g: GeometriaPortico, H_rel: float):
    """
    Los casos de carga del portico, sin factorar, por metro de marco, y lo
    que el paso de cargas imprime. Devuelve (casos, candidatos de la carga
    viva, magnitudes, cv).

      DC  el peso de la losa superior y de las paredes; la losa inferior
          apoya en el suelo y su peso no flexa el portico (MnDOT §12.5).
      EV  F_e (gamma_s H_rel + gamma_p e_paq), 12.11.2.2.1.
      EH  k_o sigma_v en las paredes exteriores, con sigma_v entre los ejes
          de las losas (3.11.5.2, reposo).
      LS  k_o gamma_s h_eq, uniforme en las paredes exteriores (3.11.6.4).
      WA  el agua interior, con el conducto lleno: la presion hidrostatica
          sobre las paredes de cada celda y su peso sobre la losa inferior.
    Cada uno con la reaccion del suelo que lo equilibra.
    """
    e_paq = espesor_del_paquete(punto)
    H_total = H_rel + e_paq
    gamma_s, gamma_p, proc_gamma = pesos_especificos_de_carga(
        piso_tubo_concreto=False)
    gamma_c = ca.valor(CRITERIO_PESO_CONCRETO)
    phi, k0 = _k0(punto.id)
    x = g.ejes_x_m
    L, h, N = x[-1], g.altura_ejes_m, g.n_celdas
    t_sup, t_inf = g.t_losa_superior_m, g.t_losa_inferior_m

    # DC
    w_sup = gamma_c * t_sup
    casos = {}
    dc = _en_la_losa(g, MIEMBRO_LOSA_SUPERIOR, 0.0, L, -w_sup, -w_sup)
    verticales = [(0.0, L, -w_sup, -w_sup)]
    paredes = []
    for j in range(N + 1):
        w_p = gamma_c * g.espesor_de_pared(j)
        dc.append((f"{MIEMBRO_PARED}_{j}", 0.0, h, 0.0, 0.0, -w_p, -w_p))
        paredes.append((x[j], -w_p * h))
    casos[CASO_DC] = dc + _reaccion_del_suelo(g, verticales, paredes)

    # EV
    B_c = seccion.ancho_exterior(g.t_pared_m)
    F_e = min(1 + 0.20 * H_total / B_c,                   # literal-ok: el 0.20 de la Eq. 12.11.2.2.1-2
              _CN.FE_CAJON_MAX_COMPACTADO)
    w_ev = F_e * (gamma_s * H_rel + gamma_p * e_paq)
    casos[CASO_EV] = (_en_la_losa(g, MIEMBRO_LOSA_SUPERIOR, 0.0, L, -w_ev, -w_ev)
                      + _reaccion_del_suelo(g, [(0.0, L, -w_ev, -w_ev)]))

    # EH: sigma_v lineal bajo el paquete, en los ejes de las losas.
    def sigma_v(z: float) -> float:
        return gamma_p * min(z, e_paq) + gamma_s * max(0.0, z - e_paq)
    z_sup = H_total + t_sup / 2
    z_inf = H_total + t_sup + g.altura_libre_m + t_inf / 2
    # --- VE-7 lote B, B3 --- con el nivel freatico sobre el eje de la losa
    # inferior, bajo el agua el suelo empuja con su peso SUMERGIDO y el agua
    # aparte (AASHTO 3.11.3; Manual de Puentes 2.4.4.1.3): el diagrama del
    # ensamble de M9 (seco, su continuacion y el sumergido).
    agua = _agua_exterior_del_portico(punto, z_sup=z_sup, z_inf=z_inf)
    avisos_agua: Tuple[str, ...] = ()
    mags_sumergido: Tuple[Magnitud, ...] = ()
    if agua is not None and agua[2] is None:
        avisos_agua = (
            f"portico del marco: nivel sin ascenso estacional -- el agua "
            f"exterior se toma en la lectura de NF_profundidad_m; "
            f"'{CRITERIO_MARGEN_NF_V7}' [A] no esta declarado (con el, el "
            "nivel sube como en V7)",)
    if agua is None:
        p_sup, p_inf = k0 * sigma_v(z_sup), k0 * sigma_v(z_inf)
        casos[CASO_EH] = (_en_la_pared(g, 0, 0.0, h, p_inf, p_sup)
                          + _en_la_pared(g, N, 0.0, h, -p_inf, -p_sup))
    else:
        z_nf, gamma_sat, _margen = agua
        gamma_sum = gamma_sat - GAMMA_AGUA_KN_M3

        def sigma_ef(z: float) -> float:
            return sigma_v(min(z, z_nf)) + gamma_sum * max(0.0, z - z_nf)
        p_sup, p_inf = k0 * sigma_ef(z_sup), k0 * sigma_ef(z_inf)
        # La presion efectiva tiene un quiebre en el nivel: dos tramos
        # lineales, cada uno exacto.
        y_nf = min(z_inf - z_nf, h)
        eh = []
        for (y_a, y_b) in ((0.0, y_nf), (y_nf, h)):
            if not y_b > y_a + TOL_UMBRAL_NORMATIVO:
                continue
            q_a, q_b = k0 * sigma_ef(z_inf - y_a), k0 * sigma_ef(z_inf - y_b)
            eh += (_en_la_pared(g, 0, y_a, y_b, q_a, q_b)
                   + _en_la_pared(g, N, y_a, y_b, -q_a, -q_b))
        casos[CASO_EH] = eh
        # WA_ext: la presion hidrostatica del agua exterior, gamma_w (z -
        # z_NF), lineal en la pared mojada (triangular; trapecial si el
        # nivel pasa el eje de la losa superior). La subpresion bajo la losa
        # inferior no se aplica: con la reaccion del suelo LINEAL que el
        # portico supone, una carga uniforme sobre la losa inferior la
        # equilibra la misma reaccion y no flexa el portico.
        w_inf = GAMMA_AGUA_KN_M3 * (z_inf - z_nf)
        w_top = GAMMA_AGUA_KN_M3 * max(z_inf - h - z_nf, 0.0)
        casos[CASO_WA_EXT] = (_en_la_pared(g, 0, 0.0, y_nf, w_inf, w_top)
                              + _en_la_pared(g, N, 0.0, y_nf, -w_inf, -w_top))
        # --- dictamen Fable (decision 3) --- con el nivel sobre la losa
        # superior, la losa carga F_e sigma'_v (12.11.2.2.1) con gamma_EV mas
        # el agua gamma_w d_w con gamma_WA (AASHTO 3.11.3; Manual de Puentes
        # 2.4.4.1.3): dos casos que corrigen el EV seco, cada uno con la
        # reaccion lineal que lo equilibra.
        if z_nf < H_total - TOL_UMBRAL_NORMATIVO:
            d_w = H_total - z_nf
            w_sum = F_e * (sigma_ef(H_total) - sigma_v(H_total))
            w_wa = GAMMA_AGUA_KN_M3 * d_w
            casos[CASO_EV_SUM] = (
                _en_la_losa(g, MIEMBRO_LOSA_SUPERIOR, 0.0, L, -w_sum, -w_sum)
                + _reaccion_del_suelo(g, [(0.0, L, -w_sum, -w_sum)]))
            casos[CASO_WA_SUP] = (
                _en_la_losa(g, MIEMBRO_LOSA_SUPERIOR, 0.0, L, -w_wa, -w_wa)
                + _reaccion_del_suelo(g, [(0.0, L, -w_wa, -w_wa)]))
            mags_sumergido = (
                Magnitud("d_w", d_w, "m", "agua sobre la losa superior: "
                         "H_total - z_NF", cifras=CIFRAS_MAGNITUD),
                Magnitud("w_EV,sum", w_sum, "kPa", "F_e (sigma'_v - sigma_v) "
                         "en la cara de la losa superior: lo que el relleno "
                         "sumergido le quita al EV seco (gamma_EV)",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("w_WA,sup", w_wa, "kPa", "gamma_w d_w, el agua "
                         "sobre la losa superior (gamma_WA)",
                         cifras=CIFRAS_MAGNITUD))

    # LS
    altura_muro = H_total + t_sup + g.altura_libre_m + t_inf
    h_eq, origen_heq = _h_eq_portico(altura_muro)
    p_ls = k0 * gamma_s * h_eq
    casos[CASO_LS] = (_en_la_pared(g, 0, 0.0, h, p_ls, p_ls)
                      + _en_la_pared(g, N, 0.0, h, -p_ls, -p_ls))

    # WA: el agua llena cada celda, desde la cara inferior de la losa
    # superior hasta la cara superior de la inferior.
    y_fondo, y_techo = t_inf / 2, h - t_sup / 2
    p_fondo = GAMMA_AGUA_KN_M3 * g.altura_libre_m
    wa, verticales = [], []
    for c in range(N):
        wa += _en_la_pared(g, c, y_fondo, y_techo, -p_fondo, 0.0)
        wa += _en_la_pared(g, c + 1, y_fondo, y_techo, p_fondo, 0.0)
        x_a = x[c] + g.espesor_de_pared(c) / 2
        x_b = x[c + 1] - g.espesor_de_pared(c + 1) / 2
        wa += _en_la_losa(g, MIEMBRO_LOSA_INFERIOR, x_a, x_b, -p_fondo,
                          -p_fondo)
        verticales.append((x_a, x_b, -p_fondo, -p_fondo))
    casos[CASO_WA] = wa + _reaccion_del_suelo(g, verticales)

    # LL: la carga viva de 3.6.1.2.6 o, con menos de 2.0 ft, la franja de
    # 4.6.2.10 (`carga_viva_enterrada`). Cada vehiculo es un grupo de areas
    # cargadas: una sola si sus ejes interactuan (l_w ya incluye s_a), dos a
    # s_a si no.
    luz_permiso = (N * seccion.B + (N - 1) * g.t_tabique_m if N > 1 else None)
    cv = carga_viva_enterrada(
        H=H_total, D_i=seccion.B, D_E=H_rel, conducto=CONDUCTO_CAJON,
        id_punto=punto.id, efecto=lambda P_L, _l_w: P_L,
        efecto_descripcion="P_L, kPa: el portico prueba los dos vehiculos",
        luz_del_permiso=luz_permiso)
    separacion = {VEHICULO_CAMION: _CN.SEPARACION_EJES_CAMION_MIN_M,
                  VEHICULO_TANDEM: _CN.SEPARACION_EJES_TANDEM_M}
    vehiculos = []
    if not cv.despreciada:
        for (nombre, _P, l_w, _w, P_L, _e) in cv.candidatos:
            s_a = separacion[nombre]
            ejes = ((0.0,) if l_w + TOL_UMBRAL_NORMATIVO >= s_a
                    else (0.0, s_a))
            vehiculos.append((nombre, P_L, l_w, ejes))
    magnitudes = (
        Magnitud("gamma_c", gamma_c, "kN/m3", f"'{CRITERIO_PESO_CONCRETO}' "
                 "[C], AASHTO LRFD Tabla 3.5.1-1", cifras=CIFRAS_FACTOR),
        Magnitud("t", g.t_losa_superior_m, "m", "canto de losas, paredes y "
                 "tabiques: 'espesor_pared_cajon', el de la geometria del "
                 "programa (ficha T5-07)", cifras=CIFRAS_MAGNITUD),
        Magnitud("w_DC", w_sup, "kPa", "peso de la losa superior; las "
                 "paredes cargan su peso y la losa inferior apoya en el "
                 "suelo", cifras=CIFRAS_MAGNITUD),
        Magnitud("F_e", F_e, "", "1 + 0.20 H/B_c <= 1.15 (12.11.2.2.1)",
                 cifras=CIFRAS_FACTOR),
        Magnitud("gamma_s", gamma_s, "kN/m3", proc_gamma, cifras=CIFRAS_FACTOR),
        Magnitud("w_EV", w_ev, "kPa", "F_e (gamma_s H_rel + gamma_p e_paq)",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("phi_f", phi, "grados", f"'{CRITERIO_PHI_RELLENO}' [A], el "
                 "relleno del proyecto (el mismo del cabezal)",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("k_o", k0, "", "1 - sen phi_f (Eq. 3.11.5.2-1, reposo: "
                 "decision del dueño)", cifras=CIFRAS_FACTOR),
        Magnitud("p_EH,sup", p_sup, "kPa", f"k_o sigma_v en el eje de la "
                 f"losa superior (z = {z_sup:.3f} m)", cifras=CIFRAS_MAGNITUD),
        Magnitud("p_EH,inf", p_inf, "kPa", f"k_o sigma_v en el eje de la "
                 f"losa inferior (z = {z_inf:.3f} m)", cifras=CIFRAS_MAGNITUD),
        Magnitud("h_eq", h_eq, "m", origen_heq, cifras=CIFRAS_MAGNITUD),
        Magnitud("p_LS", p_ls, "kPa", "k_o gamma_s h_eq", cifras=CIFRAS_MAGNITUD),
        Magnitud("p_WA", p_fondo, "kPa", "presion del agua interior en la "
                 "cara superior de la losa inferior (conducto lleno)",
                 cifras=CIFRAS_MAGNITUD),
    ) + (() if agua is None else (
        Magnitud("z_NF", agua[0], "m", "profundidad del nivel freatico bajo "
                 "la rasante: cota_rasante - (cota_terreno - "
                 "NF_profundidad_m + margen)"
                 + (f", margen '{CRITERIO_MARGEN_NF_V7}' = {agua[2]:g} m"
                    if agua[2] is not None else
                    ", nivel sin ascenso estacional (margen sin declarar)"),
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("gamma_sat", agua[1], "kN/m3",
                 f"'{CRITERIO_PESO_SATURADO}' [S], el relleno bajo el agua "
                 "pesa gamma_sat - gamma_w", cifras=CIFRAS_FACTOR),
        Magnitud("p_WA,ext", GAMMA_AGUA_KN_M3 * (z_inf - agua[0]), "kPa",
                 "presion del agua exterior en el eje de la losa inferior, "
                 "gamma_w (z_inf - z_NF)", cifras=CIFRAS_MAGNITUD),
    )) + mags_sumergido + tuple(
        Magnitud(f"P_L del {nombre}", P_L, "kPa",
                 f"sobre {l_w:.3f} m paralelos al vano, "
                 f"{len(ejes)} area(s) cargada(s) a {separacion[nombre]:.3f} "
                 "m; se mueve a lo largo de la losa superior (paso F8.LL)",
                 cifras=CIFRAS_MAGNITUD)
        for nombre, P_L, l_w, ejes in vehiculos)
    return casos, vehiculos, magnitudes, cv, w_ev, avisos_agua


# --- VE-7 lote B, B3 --- las citas del agua del ensamble de M9: el suelo
# bajo el agua con su peso sumergido y el agua aparte.
_CITAS_AGUA_EXTERIOR = ("AASHTO_LRFD_9.3.11.3", "MP.2.4.4.1.3#SUMERGIDO")


def _agua_exterior_del_portico(punto: PuntoCritico, *, z_sup: float,
                               z_inf: float
                               ) -> Optional[Tuple[float, float,
                                                   Optional[float]]]:
    """
    --- VE-7 lote B, B3 (T5-07 (5); decision del consultor Fable, triaje
    VE-7, 2026-11-20) --- El agua EXTERIOR del portico: (z_NF, gamma_sat),
    con z_NF la profundidad del nivel freatico bajo la rasante, o None si el
    nivel no pasa del eje de la losa inferior (o el punto no trae
    'NF_profundidad_m'): entonces el portico es el de antes.

    El nivel es el de V7 (`cota_nivel_agua_v7_del_nf`): la columna
    'NF_profundidad_m' del CSV, medida bajo el terreno natural del cruce,
    mas el ascenso estacional 'margen_estacional_nf_v7_m' [A] SI ESTA
    DECLARADO (negativo, `DatoInvalidoError`); sin el, la lectura cruda y un
    aviso (dictamen Fable, defecto 1):
    z_NF = cota_rasante - (cota_terreno - NF_profundidad_m + margen). Un
    nivel sobre la rasante (z_NF < 0) es `DatoInvalidoError` sobre la
    columna (defecto 2). Devuelve (z_NF, gamma_sat, margen o None). Con el agua
    arriba hace falta el peso del relleno bajo el agua, que es un dato de
    ensayo: 'peso_especifico_saturado_relleno_kn_m3' (`CriterioPendienteError`
    sin el; `DatoInvalidoError` si no supera al agua, como en V7).
    `z_sup` no limita: con el nivel sobre la losa superior el agua de la
    pared es trapecial.
    """
    nf = punto.NF_profundidad_m
    if nf is None:
        return None
    margen = ca.valor_si_declarado(CRITERIO_MARGEN_NF_V7)
    if margen is not None and not margen >= 0:
        raise DatoInvalidoError(
            CRITERIO_MARGEN_NF_V7, valor=margen, id_punto=punto.id,
            motivo="el ascenso estacional del freatico no puede ser negativo: "
                   "bajaria el nivel por debajo de la lectura de "
                   "NF_profundidad_m")
    z_nf = punto.cota_rasante - (punto.cota_terreno - nf + (margen or 0.0))
    if not z_nf >= 0:
        raise DatoInvalidoError(
            "NF_profundidad_m", valor=nf, id_punto=punto.id,
            motivo=f"el nivel freatico queda {-z_nf:.3f} m sobre la rasante "
                   "(cota_terreno - NF_profundidad_m + margen > "
                   "cota_rasante): el agua exterior del portico no se puede "
                   "plantear sobre la via")
    if not z_nf < z_inf - TOL_UMBRAL_NORMATIVO:
        return None
    gamma_sat = ca.valor(CRITERIO_PESO_SATURADO)     # CriterioPendienteError
    if not (math.isfinite(gamma_sat) and gamma_sat > GAMMA_AGUA_KN_M3):
        raise DatoInvalidoError(
            CRITERIO_PESO_SATURADO, valor=gamma_sat, id_punto=punto.id,
            motivo="tiene que ser mayor que el peso especifico del agua: "
                   "el relleno bajo el nivel pesa el saturado menos el agua")
    return z_nf, float(gamma_sat), margen


def _carga_viva_en(g: GeometriaPortico, P_L: float, l_w: float, ejes,
                   x_centro: float):
    """Las areas de un vehiculo con el primer eje centrado en x_centro, con
    la reaccion del suelo que las equilibra."""
    L = g.ejes_x_m[-1]
    cargas, verticales = [], []
    for desfase in ejes:
        x_a = max(0.0, x_centro + desfase - l_w / 2)
        x_b = min(L, x_centro + desfase + l_w / 2)
        if not x_b > x_a + TOL_UMBRAL_NORMATIVO:
            continue
        cargas += _en_la_losa(g, MIEMBRO_LOSA_SUPERIOR, x_a, x_b, -P_L, -P_L)
        verticales.append((x_a, x_b, -P_L, -P_L))
    if not verticales:
        return []
    return cargas + _reaccion_del_suelo(g, verticales)


# ---------------------------------------------------------------------------
# Analisis, combinaciones y armado
# ---------------------------------------------------------------------------

def analizar_portico(g: GeometriaPortico, casos: dict, vehiculos=()
                     ) -> Tuple[dict, dict]:
    """
    Los esfuerzos sin factorar de cada seccion en cada caso permanente
    ({caso: {seccion: (M, |V|, N)}}), y la ENVOLVENTE de la carga viva
    ({seccion: (M max, M min, |V| max)}) moviendo cada vehiculo a lo largo
    de la losa superior en `POSICIONES_CARGA_VIVA_POR_CELDA` posiciones por
    celda (AASHTO LRFD 12.11.2; la reaccion del suelo de cada posicion la
    equilibra).
    """
    modelo = _ModeloPortico(g)
    secciones = secciones_del_portico(g)
    por_caso = {caso: _esfuerzos(modelo.resolver(cargas), secciones)
                for caso, cargas in casos.items()}
    envolvente = {s[0]: (0.0, 0.0, 0.0) for s in secciones}
    L = g.ejes_x_m[-1]
    n_pos = POSICIONES_CARGA_VIVA_POR_CELDA * g.n_celdas
    for (_nombre, P_L, l_w, ejes) in vehiculos:
        for k in range(n_pos + 1):
            x_c = L * k / n_pos
            cargas = _carga_viva_en(g, P_L, l_w, ejes, x_c)
            if not cargas:
                continue
            for sec, (M, V, _N) in _esfuerzos(modelo.resolver(cargas),
                                              secciones).items():
                M_mas, M_menos, V_max = envolvente[sec]
                envolvente[sec] = (max(M_mas, M), min(M_menos, M),
                                   max(V_max, V))
    return por_caso, envolvente


def _factores_del_portico(material: Material) -> dict:
    """Los gamma de Resistencia I (Manual de Puentes Tablas 2.4.5.3.1-1/-2)
    del marco, por carga y extremo, y el eta del conducto."""
    eleccion = ca.valor(CRITERIO_FACTORES_CARGA)
    fila_ev = _fila_elegida(eleccion, ELEMENTO_CAJON, CARGA_RELLENO)
    fila_eh = _fila_elegida(eleccion, ELEMENTO_CAJON, CARGA_EMPUJE)
    return {
        "DC": (_gamma_p(FILA_GAMMA_P_DC, EXTREMO_DESESTABILIZANTE),
               _gamma_p(FILA_GAMMA_P_DC, EXTREMO_ESTABILIZANTE)),
        "EV": (_gamma_p(fila_ev, EXTREMO_DESESTABILIZANTE),
               _gamma_p(fila_ev, EXTREMO_ESTABILIZANTE)),
        "EH": (_gamma_p(fila_eh, EXTREMO_DESESTABILIZANTE),
               _gamma_p(fila_eh, EXTREMO_ESTABILIZANTE)),
        "LL": _gamma_ll(),
        "WA": _gamma_de_la_combinacion(CARGA_AGUA, EXTREMO_DESESTABILIZANTE),
        "eta": _eta(),
        "filas": (fila_gamma_p_legible(FILA_GAMMA_P_DC),
                  fila_gamma_p_legible(fila_ev),
                  fila_gamma_p_legible(fila_eh)),
    }


def combinaciones_del_portico(f: dict, sumergido: bool = False):
    """
    Las combinaciones de C12.11.2.1 (tres envolventes, las de horizontal
    maximo con LS y sin LS), en Resistencia I con el eta de 1.3.2.1 (eta en
    las cargas de gamma maximo, 1/eta en las de gamma minimo) y en Servicio
    I. Cada una: (nombre, estado, {caso: factor}, factor de LL, reduce EH
    en el positivo de la losa superior). En la de horizontal MINIMO el
    empuje va con su gamma minimo, y en el momento positivo de la losa
    superior ademas reducido a la mitad (3.11.7).
    """
    eta = f["eta"]
    g_dc, g_ev, g_eh, g_ll, g_wa = f["DC"], f["EV"], f["EH"], f["LL"], f["WA"]
    combos = []
    for con_ls in (True, False):
        sufijo = "con LS" if con_ls else "sin LS"
        combos.append((f"{ESTADO_RESISTENCIA}, vertical max. y horizontal "
                       f"max. ({sufijo})", ESTADO_RESISTENCIA,
                       {CASO_DC: eta * g_dc[0], CASO_EV: eta * g_ev[0],
                        CASO_EH: eta * g_eh[0],
                        CASO_LS: eta * g_ll if con_ls else 0.0,
                        CASO_WA: 0.0, CASO_WA_EXT: eta * g_wa},
                       eta * g_ll, False))
    # El agua exterior se opone a la interior: en el horizontal minimo no
    # entra (VE-7, B3).
    combos.append((f"{ESTADO_RESISTENCIA}, vertical max. y horizontal min. "
                   "(agua interior)", ESTADO_RESISTENCIA,
                   {CASO_DC: eta * g_dc[0], CASO_EV: eta * g_ev[0],
                    CASO_EH: g_eh[1] / eta, CASO_LS: 0.0, CASO_WA: g_wa,
                    CASO_WA_EXT: 0.0},
                   eta * g_ll, True))
    for con_ls in (True, False):
        sufijo = "con LS" if con_ls else "sin LS"
        combos.append((f"{ESTADO_RESISTENCIA}, vertical min. y horizontal "
                       f"max. ({sufijo})", ESTADO_RESISTENCIA,
                       {CASO_DC: g_dc[1] / eta, CASO_EV: g_ev[1] / eta,
                        CASO_EH: eta * g_eh[0],
                        CASO_LS: eta * g_ll if con_ls else 0.0,
                        CASO_WA: 0.0, CASO_WA_EXT: eta * g_wa}, 0.0, False))
    servicio = {caso: 1.0 for caso in CASOS_PERMANENTES + (CASO_WA_EXT,)}
    combos.append((f"{ESTADO_SERVICIO}, vertical max. y horizontal max.",
                   ESTADO_SERVICIO, dict(servicio, **{CASO_WA: 0.0}), 1.0,
                   False))
    combos.append((f"{ESTADO_SERVICIO}, vertical max. y horizontal min. "
                   "(agua interior)", ESTADO_SERVICIO,
                   dict(servicio, **{CASO_LS: 0.0, CASO_WA_EXT: 0.0}), 1.0,
                   True))
    combos.append((f"{ESTADO_SERVICIO}, vertical min. y horizontal max.",
                   ESTADO_SERVICIO, dict(servicio, **{CASO_WA: 0.0}), 0.0,
                   False))
    if not sumergido:
        return tuple(combos)
    # --- dictamen Fable (decision 3) --- la envolvente seco/sumergido: cada
    # combinacion se repite con EV_sum al factor de su EV y WA_sup con
    # gamma_WA (por eta donde el EV va al maximo; 1.0 en Servicio I). Las
    # originales los dejan fuera (factor 0, caso ausente del diccionario).
    duplicadas = []
    for (nombre, estado, factores, f_ll, reduce) in combos:
        if estado == ESTADO_SERVICIO:
            f_wa = 1.0
        elif factores[CASO_EV] > g_ev[1] / eta + TOL_UMBRAL_NORMATIVO:
            f_wa = eta * g_wa
        else:
            f_wa = g_wa
        duplicadas.append((nombre + SUFIJO_SUMERGIDO, estado,
                           dict(factores, **{CASO_EV_SUM: factores[CASO_EV],
                                             CASO_WA_SUP: f_wa}),
                           f_ll, reduce))
    return tuple(combos) + tuple(duplicadas)


def _envolvente_de_la_combinacion(combo, por_caso, ll, secciones):
    """
    Los esfuerzos factorados de cada seccion en una combinacion, por SIGNO:
    {seccion: (M que tracciona la cara interior, M que tracciona la
    exterior --negativo--, |V|, N)}, con la carga viva en su posicion mas
    desfavorable para cada uno.
    """
    _nombre, _estado, factores, f_ll, reduce = combo
    salida = {}
    for (sec, _m, _s, _t, _d, centro_sup, _suelo) in secciones:
        M = V_perm = N = 0.0
        for caso, factor in factores.items():
            if caso not in por_caso:      # WA_ext, solo con el NF arriba
                continue
            m, v, n = por_caso[caso][sec]
            if caso == CASO_EH and reduce:
                factor = factor * (_CN.REDUCCION_EMPUJE_3_11_7 if centro_sup
                                   else 1.0)
            M += factor * m
            V_perm += factor * v
            N += factor * n
        M_mas, M_menos, V_ll = ll[sec]
        salida[sec] = (M + f_ll * max(M_mas, 0.0), M + f_ll * min(M_menos, 0.0),
                       V_perm + f_ll * V_ll, N)
    return salida


def disenar_portico(*, punto: PuntoCritico, material: Material,
                    seccion: Seccion, altura_relleno: float) -> DisenoPortico:
    """
    Analisis y armado del portico del marco (AASHTO LRFD 12.11.5.1: «All
    sections shall be designed for the applicable factored loads specified
    in Table 3.4.1-1 at the strength limit state»; 12.11.4: fisuracion de
    5.6.7; 12.11.5.3.1: minimos de 5.6.3.3 y 5.10.6; 12.11.5.1 y 5.12.7.3:
    cortante por 5.7).

    Cada seccion de `secciones_del_portico` se arma en la cara que alguna
    combinacion de resistencia tracciona, con `M9.diseno_flexion_corte` (el
    armado del cabezal: flexion, cortante sin estribos, minimos de AASHTO y
    E.060, espaciamiento y fisuracion en Servicio I) y los factores de
    resistencia del cajon vaciado in situ de la Tabla 12.5.5-1 (0.90 y
    0.85). Las verificaciones (A1 a A6 por seccion y cara) son las del
    punto: una que no cumple deja el expediente abierto. No itera el canto:
    si no cumple, la salida es mas canto (ficha T5-07).

    Se detiene con `CriterioPendienteError` sin el angulo de friccion del
    relleno ('phi_relleno_trasdos', el k_o del empuje en reposo) y con los
    criterios del armado del cabezal que falten.

    LECTURAS DEL PROYECTO, declaradas tambien en el paso F8.PORTICO_CARGAS:
    el peso de la losa inferior no flexa el portico (apoya en el suelo, como
    en MnDOT §12.5); la reaccion del suelo es lineal bajo la losa inferior;
    el empuje se toma entre los ejes de las losas; la sobrecarga viva
    lateral sale de la Tabla 3.11.6.4-1 de estribos con la altura desde la
    rasante hasta la cara inferior de la losa inferior, por analogia; el
    agua interior, con el conducto lleno; el relleno es el mismo del cabezal
    ('phi_relleno_trasdos'), y el material, el recubrimiento y la clase de
    exposicion del armado son los del cabezal (`M9.diseno_flexion_corte` los
    lee). La reduccion de 3.11.7 se combina con el gamma minimo y 1/eta, que
    la fuente permite no combinar: es el lado conservador del positivo.
    """
    H_rel = _finito_positivo("altura_relleno", altura_relleno, punto.id)
    g = geometria_del_portico(material=material, seccion=seccion)
    d = _disenar_portico_con(punto=punto, material=material, seccion=seccion,
                             H_rel=H_rel, g=g)
    if d.cumple:
        return d
    return _con_el_canto_que_cierra(d, punto=punto, material=material,
                                    seccion=seccion, H_rel=H_rel)


def _disenar_portico_con(*, punto: PuntoCritico, material: Material,
                         seccion: Seccion, H_rel: float,
                         g: GeometriaPortico) -> DisenoPortico:
    """El analisis y el armado del portico con la geometria `g` y el relleno
    `H_rel` (el cuerpo de `disenar_portico`, que VE-7 separa para buscar el
    canto que cerraria sin repetirlo)."""
    from src.modulos import M9_cabezal as M9      # perezoso: M9 importa de M2 y M6
    casos, vehiculos, mags, cv, w_ev, avisos_agua = _casos_de_carga(
        punto=punto, material=material, seccion=seccion, g=g, H_rel=H_rel)
    por_caso, ll = analizar_portico(g, casos, vehiculos)
    secciones = secciones_del_portico(g)
    f = _factores_del_portico(material)
    combos = combinaciones_del_portico(f, sumergido=CASO_EV_SUM in casos)
    envolventes = {c[0]: _envolvente_de_la_combinacion(c, por_caso, ll,
                                                      secciones)
                   for c in combos}
    p_cargas = paso(
        "F8.PORTICO", codigo=CODIGO_PASO_PORTICO_CARGAS,
        que="Portico del marco: cargas sin factorar por metro de marco",
        formula=("DC = gamma_c t; EV = F_e (gamma_s H_rel + gamma_p e_paq); "
                 "EH = k_o sigma_v; LS = k_o gamma_s h_eq; WA = gamma_w y; "
                 "LL+IM = P_L sobre l_w (paso F8.LL)"),
        formula_cita_id="AASHTO_LRFD_9.12.11.2.1#CARGAS",
        citas_textuales=("AASHTO_LRFD_9.12.11.2.3", "AASHTO_LRFD_9.3.11.5.2#K0",
                         "AASHTO_LRFD_9.3.11.6.4#APLICA",
                         "AASHTO_LRFD_9.T3.11.6.4-1")
        + (_CITAS_AGUA_EXTERIOR if CASO_WA_EXT in casos else ()),
        sustitucion=mags,
        resultado=Magnitud("w_EV", w_ev, "kPa", "presion de tierra sobre la "
                           "losa superior", cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=(
            "Lecturas del proyecto: la losa inferior apoya en el suelo y su "
            "peso no flexa el portico (como el ejemplo resuelto de MnDOT "
            "§12.5); la reaccion del suelo es LINEAL bajo la losa inferior; "
            "el empuje se toma entre los ejes de las losas; la sobrecarga "
            "viva lateral con la Tabla 3.11.6.4-1 de estribos, por analogia "
            "[N->]; y el agua interior con el conducto lleno. El agua "
            "EXTERIOR entra con el nivel freatico sobre el eje de la losa "
            "inferior (VE-7): triangular en las paredes y el suelo bajo el "
            "nivel con su peso sumergido (AASHTO 3.11.3, Manual de Puentes "
            "2.4.4.1.3); la subpresion no cambia la flexion, porque la "
            "reaccion lineal del suelo la equilibra en la misma losa."))
    nombres_eta = (f"eta = {f['eta']:g} en las cargas de gamma maximo y "
                   f"1/eta en las de gamma minimo (1.3.2.1)")
    p_combos = paso(
        "F8.PORTICO", codigo=CODIGO_PASO_PORTICO_COMBINACIONES,
        que="Portico del marco: combinaciones de carga (C12.11.2.1)",
        formula=("Resistencia I: eta gamma_max Q (o gamma_min Q / eta); "
                 "Servicio I: 1.0 Q; EH reducido al 50 % solo en el momento "
                 "positivo de la losa superior (3.11.7)"),
        formula_cita_id="AASHTO_LRFD_9.12.11.5.1",
        citas_textuales=("AASHTO_LRFD_9.C12.11.2.1#COMBINACIONES",
                         "AASHTO_LRFD_9.3.11.7", "AASHTO_LRFD_9.T3.4.1-1",
                         "AASHTO_LRFD_9.T3.4.1-2"),
        sustitucion=(
            Magnitud("gamma_DC", f["DC"][0], "", f"{f['filas'][0]}; minimo "
                     f"{f['DC'][1]:g}", cifras=CIFRAS_FACTOR),
            Magnitud("gamma_EV", f["EV"][0], "", f"{f['filas'][1]} "
                     f"('{CRITERIO_FACTORES_CARGA}' [A]); minimo "
                     f"{f['EV'][1]:g}", cifras=CIFRAS_FACTOR),
            Magnitud("gamma_EH", f["EH"][0], "", f"{f['filas'][2]} "
                     f"('{CRITERIO_FACTORES_CARGA}' [A]); minimo "
                     f"{f['EH'][1]:g}", cifras=CIFRAS_FACTOR),
            Magnitud("gamma_LL", f["LL"], "", "LL, IM y LS en Resistencia I",
                     cifras=CIFRAS_FACTOR),
            Magnitud("gamma_WA", f["WA"], "", "WA en Resistencia I",
                     cifras=CIFRAS_FACTOR),
            Magnitud("eta", f["eta"], "", f"'{CRITERIO_ETA_CONDUCTO}' [A]; "
                     + nombres_eta, cifras=CIFRAS_FACTOR),
            Magnitud("reduccion", _CN.REDUCCION_EMPUJE_3_11_7, "",
                     "3.11.7, con el gamma minimo y 1/eta (la fuente permite "
                     "no combinarlos: combinarlos es el lado conservador "
                     "del momento positivo)", cifras=CIFRAS_FACTOR)),
        resultado=Magnitud("eta", f["eta"], "", "modificador de carga",
                           cifras=CIFRAS_FACTOR),
        nota_del_proyecto="; ".join(c[0] for c in combos))
    resistencia = [c for c in combos if c[1] == ESTADO_RESISTENCIA]
    servicio = [c for c in combos if c[1] == ESTADO_SERVICIO]

    def extremo(sec, signo, lista):
        return max((max(0.0, signo * envolventes[c[0]][sec][0 if signo > 0
                                                            else 1])
                    for c in lista), default=0.0)

    sust_analisis = []
    for (sec, _m, _s, _t, desc, _c, _su) in secciones:
        M_mas, M_menos = extremo(sec, 1, resistencia), extremo(sec, -1,
                                                               resistencia)
        V_max = max(envolventes[c[0]][sec][2] for c in resistencia)
        sust_analisis.append(Magnitud(
            f"M {sec}", M_mas if M_mas >= M_menos else -M_menos, "kN·m/m",
            f"{desc}: Resistencia I, cara interior {M_mas:.2f}, exterior "
            f"{M_menos:.2f} kN·m/m; V = {V_max:.2f} kN/m",
            cifras=CIFRAS_MAGNITUD))
    centros = [s[0] for s in secciones if s[5]]
    M_centro = max(extremo(s, 1, resistencia) for s in centros)
    p_analisis = paso(
        "F8.PORTICO", codigo=CODIGO_PASO_PORTICO_ANALISIS,
        que=("Portico del marco: esfuerzos factorados de las secciones "
             "(rigidez directa, envolvente de la carga viva)"),
        formula=("K u = F (portico cerrado de ejes; vector de carga "
                 "consistente; reaccion del suelo lineal)"),
        formula_cita_id="AASHTO_LRFD_9.12.11.5.1",
        citas_textuales=("AASHTO_LRFD_9.12.11.2.3",),
        sustitucion=tuple(sust_analisis),
        resultado=Magnitud("M_u+", M_centro, "kN·m/m", "momento positivo "
                           "factorado de la losa superior en el centro",
                           cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=(
            f"{g.n_celdas} celda(s) de {g.luz_libre_m:.2f} x "
            f"{g.altura_libre_m:.2f} m; momento positivo = traccion en la "
            "cara interior de la celda (en un tabique, la que mira a la "
            "celda de su derecha). Contrastado con MnDOT §12.5 y con la "
            "solucion cerrada del marco cerrado (tests/test_ve5_portico_"
            "marco.py)."))
    armados, verificaciones, pasos_armado = [], [], []
    avisos = list(avisos_agua)
    minimos = []
    # --- dictamen Fable (defecto 3) --- 5.10.6 con el ANCHO REAL del
    # elemento (decision 3 del dueño en O-2, `M9.acero_de_temperatura_aashto`:
    # «el ancho es el real del elemento»): el largo del miembro entre ejes,
    # en las caras armadas y en las de minimo.
    largos = largos_de_los_miembros(g)
    for (sec, miembro, _s, t, desc, _c, contra_suelo) in secciones:
        for signo, cara in ((1, CARA_INTERIOR), (-1, CARA_EXTERIOR)):
            indice = 0 if signo > 0 else 1
            sols = tuple(
                SolicitacionDeArmado(
                    combinacion=c[0], condicion=CondicionAnalisis.ESTATICO,
                    M_u=max(0.0, signo * envolventes[c[0]][sec][indice]),
                    V_u=envolventes[c[0]][sec][2],
                    phi_flexion=_CN.PHI_FLEXION_CAJON_IN_SITU,
                    phi_corte=_CN.PHI_CORTE_CAJON_IN_SITU,
                    M_u_cedente=max(0.0, signo * envolventes[c[0]][sec][indice]),
                    V_u_cedente=envolventes[c[0]][sec][2])
                for c in resistencia)
            if not max(s.M_u for s in sols) > TOL_UMBRAL_NORMATIVO:
                # --- VE-7 lote B, B4 (T5-07 (3); decision del consultor
                # Fable, triaje VE-7, 2026-11-20) --- la cara que ninguna
                # combinacion tracciona lleva el acero de retraccion y
                # temperatura (12.11.5.3.1: «Shrinkage and temperature
                # reinforcement shall be provided near the inside surfaces
                # of walls and slabs in accordance with Article 5.10.6»).
                # La fila es la de REPARTO del cabezal, la MISMA funcion de
                # M9 (5.10.6 con el ancho de la seccion por metro, y E.060
                # 9.7.2 con la regla del mas exigente): no se duplica.
                minimos.append(_minimo_de_la_cara(M9, sec, cara, desc, t,
                                                  largos[miembro]))
                continue
            M_s = extremo(sec, signo, servicio)
            a = M9.diseno_flexion_corte(
                solicitaciones=sols, espesor=t, elemento=ELEMENTO_PORTICO,
                clave=f"{sec}.{cara}", seccion=desc, cara=cara,
                es_zapata=True, momento_servicio=M_s,
                ancho_seccion=largos[miembro],
                contra_el_suelo=contra_suelo and cara == CARA_EXTERIOR,
                regimen="portico cerrado (12.11)", id_punto=punto.id)
            armados.append(a)
            verificaciones.extend(a.verificaciones)
            pasos_armado.extend(a.pasos)
            avisos.extend(a.avisos)
    p_minimos = _paso_de_los_minimos(minimos)
    avisos.extend(
        f"portico del marco, {f.posicion}: ninguna barra del catalogo da el "
        f"minimo de {f.As_minimo:.0f} mm2/m con s <= {f.s_max:.3f} m"
        for f in minimos if f.barra is None)
    return DisenoPortico(
        geometria=g,
        casos=tuple((caso, tuple(EsfuerzoDeSeccion(s, m, *por_caso[caso][s])
                                 for (s, m, *_r) in secciones))
                    for caso in por_caso),
        envolventes=tuple(
            (c[0], c[1], tuple(EsfuerzoDeSeccion(
                s, m, envolventes[c[0]][s][0]
                if abs(envolventes[c[0]][s][0]) >= abs(envolventes[c[0]][s][1])
                else envolventes[c[0]][s][1],
                envolventes[c[0]][s][2], envolventes[c[0]][s][3])
                for (s, m, *_r) in secciones))
            for c in combos),
        armados=tuple(armados), verificaciones=tuple(verificaciones),
        pasos=(p_cargas, p_combos, p_analisis) + tuple(pasos_armado)
        + ((p_minimos,) if p_minimos is not None else ()),
        avisos=tuple(dict.fromkeys(avisos)), diferido=(DIFERIDO_PORTICO,),
        minimos=tuple(minimos))


def _con_el_canto_que_cierra(d: DisenoPortico, *, punto: PuntoCritico,
                             material: Material, seccion: Seccion,
                             H_rel: float) -> DisenoPortico:
    """
    --- VE-7 lote B, B5 (T5-07 (1); decision del consultor Fable, triaje
    VE-7, 2026-11-20) --- EL PORTICO NO ITERA EL CANTO, pero dice cual
    cerraria. 'espesor_pared_cajon' es el canto de la geometria del programa
    (M2, M5 y M7 forman con el la clave fisica, V4, V7 y G1): adoptarlo aqui
    dejaria esas verificaciones con otro conducto. Si A1 a A6 no cumplen, se
    busca en la grilla del dimensionamiento del cabezal
    ('dimensionamiento_zapata_cabezal' [A], su paso: el mismo con que crecen
    la zapata y su peralte) el MENOR canto uniforme t_k = t_0 + k·paso
    (aritmetica decimal, `M2._escalon_de_la_serie`) con el que el portico
    cumple, con la SECCION INTERIOR FIJA y el relleno sobre la clave
    reducido en Δt = t_k - t_0 (la losa superior crece hacia arriba). El
    tope es fisico: el relleno reducido tiene que seguir siendo positivo. Lo
    que la busqueda no puede evaluar (un relleno fuera del dominio de la
    carga viva) la termina. El resultado va en el `DisenoPortico`
    (`canto_que_cierra_m`) y en un paso; el bloqueo lo levanta
    `exigir_canto_del_portico`, que la etapa del servicio llama.
    """
    from src.modulos import M9_cabezal as M9
    from src.modulos.M2_material import _escalon_de_la_serie
    t0 = d.geometria.t_losa_superior_m
    paso_m, _fraccion = M9._regla_de_dimensionamiento()
    cierra, hasta, motivo_fin = None, t0, ""
    k = 1
    while True:
        t = _escalon_de_la_serie(t0, paso_m, k)
        H_k = H_rel - (t - t0)
        if not H_k > TOL_UMBRAL_NORMATIVO:
            motivo_fin = (f"con {t:.2f} m el relleno sobre la clave se "
                          "agota (la seccion interior es fija)")
            break
        g_k = replace(d.geometria, t_losa_superior_m=t, t_losa_inferior_m=t,
                      t_pared_m=t, t_tabique_m=t)
        try:
            d_k = _disenar_portico_con(punto=punto, material=material,
                                       seccion=seccion, H_rel=H_k, g=g_k)
        except ErrorProyecto as exc:
            motivo_fin = (f"con {t:.2f} m el portico no se pudo evaluar -- "
                          f"{type(exc).__name__}: {exc}")
            break
        hasta = t
        if d_k.cumple:
            cierra = t
            break
        k += 1
    incumplidas = sorted({v.codigo.split(".")[0] for v in d.verificaciones
                          if not v.cumple})
    p_canto = paso(
        "F8.PORTICO", codigo=CODIGO_PASO_PORTICO_CANTO,
        que=("Portico del marco: el canto uniforme que cerraria (no se "
             "adopta)"),
        formula=("t_k = t_0 + k·paso; H_rel,k = H_rel - (t_k - t_0); el menor "
                 "t_k con A1 a A6 cumplidas"),
        formula_cita_id="AASHTO_LRFD_9.12.11.5.1",
        citas_textuales=("AASHTO_LRFD_9.12.11.5.1",),
        sustitucion=(
            Magnitud("t_0", t0, "m", f"'{CRITERIO_ESPESOR_CAJON}' [A], el "
                     "canto de la geometria del programa", cifras=CIFRAS_MAGNITUD),
            Magnitud("paso", paso_m, "m", "'dimensionamiento_zapata_cabezal' "
                     "[A], el paso del cabezal", cifras=CIFRAS_MAGNITUD),
            Magnitud("H_rel", H_rel, "m", "relleno sobre la clave con t_0",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("t buscado hasta", hasta, "m", motivo_fin or
                     "el primero que cumple", cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("t_cierra", cierra if cierra is not None else "—",
                           "m", "menor canto uniforme con el que el portico "
                           "cumple", cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="busqueda, no verificacion: el canto no se adopta"),
        nota_del_proyecto=(
            f"Con {t0:.2f} m el portico incumple {', '.join(incumplidas)}. "
            + (f"Declarar '{CRITERIO_ESPESOR_CAJON}' >= {cierra:.2f} m y "
               "repetir la corrida: el canto mueve la clave fisica, V4, V7 "
               "y G1, que se verifican con la geometria del programa."
               if cierra is not None else
               f"Ningun canto uniforme de la grilla cierra el portico "
               f"({motivo_fin}).")))
    return replace(d, pasos=d.pasos + (p_canto,), canto_que_cierra_m=cierra,
                   canto_buscado_hasta_m=hasta)


def exigir_canto_del_portico(portico: DisenoPortico,
                             id_punto: Optional[str] = None) -> None:
    """
    --- VE-7 lote B, B5 --- El BLOQUEO del portico que no cumple: dice que
    canto declarar ('espesor_pared_cajon' >= X y repetir) o que ninguno de
    la grilla cierra. `DatoInvalidoError` sobre el criterio: el valor
    declarado no cierra el portico y lo que hay que hacer es corregirlo. Con
    el portico que cumple, no hace nada.
    """
    if portico.cumple:
        return
    incumplidas = sorted({v.codigo.split(".")[0]
                          for v in portico.verificaciones if not v.cumple})
    t0 = portico.geometria.t_losa_superior_m
    if portico.canto_que_cierra_m is not None:
        motivo = (f"el portico del marco no cumple {', '.join(incumplidas)} "
                  f"con {t0:.2f} m: declarar '{CRITERIO_ESPESOR_CAJON}' >= "
                  f"{portico.canto_que_cierra_m:.2f} m y repetir (el canto "
                  "mueve la clave, V4, V7 y G1: no se adopta solo)")
    else:
        hasta = portico.canto_buscado_hasta_m
        motivo = (f"el portico del marco no cumple {', '.join(incumplidas)} "
                  f"con {t0:.2f} m y ningun canto uniforme de la grilla lo "
                  "cierra" + (f" (buscado hasta {hasta:.2f} m)"
                              if hasta is not None else ""))
    raise DatoInvalidoError(campo=CRITERIO_ESPESOR_CAJON, valor=t0,
                            id_punto=id_punto, motivo=motivo)


def _minimo_de_la_cara(M9, sec: str, cara: str, desc: str, t: float,
                       ancho: float):
    """
    --- VE-7 lote B, B4 --- La `FilaDeArmado` de una cara del portico que no
    se tracciona en ninguna combinacion: `M9._fila_de_reparto`, la fila de
    reparto del cabezal (AASHTO 5.10.6 por cara y por direccion, con el
    ANCHO REAL del elemento --el largo del miembro entre ejes, dictamen
    Fable, defecto 3--, y E.060 9.7.2 con la regla del mas exigente). La posicion empieza por la clave
    de la cara («seccion.cara»), la misma de `ArmadoDeSeccion.clave`.
    """
    mat = M9.materiales_del_armado()
    return M9._fila_de_reparto(
        elemento=ELEMENTO_PORTICO,
        posicion=f"{sec}.{cara}: {desc}, cara {cara} sin traccion en ninguna "
                 "combinacion (12.11.5.3.1: retraccion y temperatura)",
        es_zapata=True, direccion="reparto", espesor=t, ancho=ancho,
        fy=mat["fy"], regla=M9._regla_de_minimos(),
        catalogo=M9.catalogo_de_barras(), hm=None, lm=None)


def _paso_de_los_minimos(minimos) -> Optional[PasoDeMemoria]:
    """--- VE-7 lote B, B4 --- El paso que imprime las caras con minimo."""
    if not minimos:
        return None
    return paso(
        "F8.PORTICO", codigo=CODIGO_PASO_PORTICO_MINIMOS,
        que=("Portico del marco: acero de retraccion y temperatura en las "
             "caras que ninguna combinacion tracciona"),
        formula=("A_s >= 1.30 b h / [2 (b + h) f_y], 0.11 <= A_s <= 0.60 "
                 "in2/ft por cara y direccion (5.10.6), b el largo del "
                 "miembro; con la regla del mas exigente, y E.060 9.7.2"),
        formula_cita_id="AASHTO_LRFD_9.5.10.6#TEMPERATURA",
        citas_textuales=("AASHTO_LRFD_9.12.11.5.3.1",
                         "AASHTO_LRFD_9.5.10.6#TEMPERATURA"),
        sustitucion=tuple(
            Magnitud(f"A_s {f.posicion.split(':', 1)[0]}", f.As_adoptado,
                     "mm2/m", f"{f.gobierna}; "
                     + (f"{f.barra.designacion} @ "
                        f"{f.barra.espaciamiento:.3f} m"
                        if f.barra is not None else "sin barra del catalogo"),
                     cifras=CIFRAS_MAGNITUD)
            for f in minimos),
        resultado=Magnitud("caras con minimo", len(minimos), "",
                           "caras del portico sin traccion en ninguna "
                           "combinacion"),
        veredicto=Veredicto(
            tipo=TipoDeVeredicto.SIN_VEREDICTO,
            explicacion="minimo constructivo, no verificacion: la cara no "
                        "tiene solicitacion que juzgar"),
        nota_del_proyecto=(
            "El acero de estas caras es el minimo de retraccion y "
            "temperatura de la fila de reparto del cabezal "
            "(`M9._fila_de_reparto`), con el ancho REAL del elemento: el "
            "largo del miembro entre ejes (5.10.6, «least width of "
            "component section»)."))
