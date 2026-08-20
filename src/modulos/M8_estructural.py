"""
M8_estructural.py
==================
Fase 8 de la hoja de ruta: verificacion estructural del conducto, sin
catalogo de proveedor -- la seleccion se hace contra las NORMAS DE PRODUCTO
(AASHTO M-170M clases I-V para concreto, ASTM A-807/AASHTO M36 para TMC,
AASHTO M294 para HDPE), coherente con la neutralidad comercial de Sec. 3.2.

Los cinco puntos de Fase 8, y lo que hace este modulo con cada uno:

    1-2  Seleccionar clase/calibre segun la altura real de relleno y
         verificar que esa altura cae en su rango admisible.
         `seleccionar_clase_calibre()` -- se detiene con
         CriterioPendienteError: ninguna de las dos tablas (AASHTO M-170M,
         ASTM A-807/AASHTO M36) esta transcrita en la hoja de ruta. Ver el
         criterio 'clases_producto_por_relleno' en criterios_adoptados.py.

    3    Flotacion (V7), obligatoria con NF a 1.4 m.
         `empuje_flotacion_kn_m()`, `peso_relleno_kn_m()` y
         `factores_carga_flotacion()` -- SI implementadas: son las piezas
         del EQUILIBRIO DE FACTORES DE CARGA LRFD que
         modulos.M5_verificaciones.v7_flotacion ensambla,

             gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U

         El empuje U es siempre calculable (geometria + constante fisica);
         el peso del relleno se detiene en 'peso_especifico_relleno_kn_m3'
         (todavia vacio). Los factores gamma salen de 'factores_carga_aashto'
         ([C], AASHTO LRFD 9a ed., Tablas 3.4.1-1/-2, fila 'Resistencia I'):
         ya no se detienen.

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
         `verificacion_diferida_estructural()` -- NO se calcula, por
         decision EXPRESA de la hoja de ruta ("Diferir al expediente").
         Devuelve el texto que declara el diferimiento con su fundamento,
         para que M11 lo imprima; no es un vacio a rellenar, es un alcance
         que la propia Fase 8 excluye del script.

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
gamma MINIMOS de la Tabla 3.4.1-2) y se MAYORA la que desestabiliza (la
subpresion, carga de agua WA, con su gamma de la Tabla 3.4.1-1),

    gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U

que con los minimos de la tabla es la forma 0.90*(DC + EV) >= 1.00*U. Los
gamma NO estan escritos en este modulo: salen de 'factores_carga_aashto', el
mismo criterio del que come M9 (Sec. 9.2). Que las dos fases lean la misma
declaracion es justamente lo que impide que el expediente tenga dos juegos de
factores de carga distintos.

Consecuencia de taxonomia: 'FS_flotacion' se RETIRO de criterios_adoptados.py.
No se le redefinio el contenido porque en LRFD no queda nada que represente:
el papel que hacia -- el margen entre estabilizante y desestabilizante -- lo
hacen ahora los propios gamma, y dejarlo declarado invitaria a multiplicar dos
veces el mismo margen.

Por que el peso propio del conducto no entra en V7
----------------------------------------------------
DC = 0. El peso propio depende del espesor de pared, que sale de la
clase/calibre seleccionada en los items 1-2 -- hoy bloqueados. Sumarlo
supondria inventar un espesor. Omitirlo es la alternativa conservadora, NO
una aproximacion optimista: reduce el lado estabilizante y hace el chequeo MAS
dificil de cumplir, nunca lo relaja. Que su gamma sea el MINIMO (0.90, no
1.25) va en la misma direccion y por la misma razon: en flotacion el peso
propio ayuda, y en LRFD lo que ayuda se minora. Se declara aqui, en cada
resultado y en la memoria, en vez de aproximar en silencio.

Por que U asume sumersion completa
-------------------------------------
La fila V7 de la Fase 5 fija la hipotesis de calculo: "tuberia vacia, NF en
su cota mas alta". Con el NF somero de la llanura del Bajo Piura y sin una
columna de invert real en el CSV (Sec. 1.2 -- misma limitacion que
`M5_verificaciones.cota_entrada_supuesta`), la lectura conservadora de "NF en
su cota mas alta" es sumersion completa del conducto, no una geometria de
sumersion parcial contra una cota de invert supuesta. Nunca subestima el
empuje.

Por eso U NO depende del valor del NF: la hipotesis es sumersion completa, y
sumergido del todo el conducto desplaza su volumen entero este el freatico a
1.4 m o a 0.8 m. El NF de cada cruce llega hoy por la columna
'NF_profundidad_m' del CSV (dato de sitio [S] que se mide punto a punto, ya
no un criterio unico de proyecto), y lo que si lo usa es la subpresion del
cabezal en M9. Que U no lo lea es la razon de que V7 siga siendo calculable
en un punto cuyo NF todavia no ha medido el estudio geotecnico.

Excepciones
-----------
    CriterioPendienteError   'clases_producto_por_relleno' (items 1-2);
                             'peso_especifico_relleno_kn_m3' (V7, via
                             modulos.M5_verificaciones.v7_flotacion).
                             'factores_carga_aashto' ya no esta vacio ([C]).

Uso
---
    from modulos.M8_estructural import (cama_apoyo_relleno_lateral,
                                        verificacion_diferida_estructural)

    cama = cama_apoyo_relleno_lateral(material)          # informativo
    diferido = verificacion_diferida_estructural()       # tupla de avisos
"""

from __future__ import annotations

import math
from typing import Tuple

import criterios_adoptados as ca
from constantes_fisicas import GAMMA_AGUA_KN_M3
from constantes_normativas import CAMA_RELLENO_LATERAL
from modelos import (CamaApoyoRelleno, CriterioPendienteError,
                     DatoInvalidoError, FactoresFlotacion, Material,
                     ReferenciaNormativa)

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
              "factores de carga: AASHTO LRFD Tablas 3.4.1-1 y 3.4.1-2)")

CRITERIO_CLASES_PRODUCTO = "clases_producto_por_relleno"
CRITERIO_FACTORES_CARGA = "factores_carga_aashto"
CRITERIO_PESO_RELLENO = "peso_especifico_relleno_kn_m3"

# Tipos de carga de las Tablas 3.4.1-1/-2 que intervienen en V7, y con que
# extremo entra cada uno. En flotacion, DC y EV ESTABILIZAN (se minoran, gamma
# minimo) y WA DESESTABILIZA (se mayora, gamma maximo). Los nombres viajan
# aqui, los NUMEROS en 'factores_carga_aashto': este modulo no declara ninguno.
CARGA_PESO_PROPIO = "DC"
CARGA_RELLENO = "EV"
CARGA_AGUA = "WA"
EXTREMO_ESTABILIZANTE = "min"
EXTREMO_DESESTABILIZANTE = "max"


# ---------------------------------------------------------------------------
# Items 1-2 - Seleccion de clase/calibre por norma de producto
# ---------------------------------------------------------------------------

def seleccionar_clase_calibre(*, material: Material, altura_relleno: float):
    """
    Clase (concreto, AASHTO M-170M I-V) o calibre (TMC, ASTM A-807/AASHTO
    M36) segun la altura real de relleno del punto, y verificacion de que
    esa altura cae en el rango admisible de la clase elegida.

    Ninguna de las dos tablas esta transcrita en la hoja de ruta -- el mismo
    vacio de norma de producto que 'h_relleno_min_concreto_tmc' declara en
    Sec. 7.A, pero alli bastaba un minimo escalar y aqui hace falta la tabla
    completa con su rango admisible por clase. Se detiene en
    'clases_producto_por_relleno' (ver su justificacion en
    criterios_adoptados.py). HDPE no tiene tabla de clase por altura: su
    verificacion detallada queda diferida al expediente por el item 5 (ver
    `verificacion_diferida_estructural`), no por este vacio.
    """
    ca.valor(CRITERIO_CLASES_PRODUCTO)    # CriterioPendienteError mientras falte
    raise CriterioPendienteError(
        CRITERIO_CLASES_PRODUCTO,
        concepto="criterio declarado, pero la seleccion de clase/calibre "
                 "(items 1-2) queda DIFERIDA al expediente tecnico: a nivel "
                 "de perfil no esta implementado leer la tabla clase x "
                 "diametro x rango de altura de relleno",
        fuente="misma via que la rigidez de anillo y el pandeo del item 5 "
               "(verificacion_diferida_estructural): verificacion diferida "
               "al expediente tecnico, no omitida",
    )


# ---------------------------------------------------------------------------
# Item 3 - V7: Flotacion del conducto
# ---------------------------------------------------------------------------

def empuje_flotacion_kn_m(*, D: float) -> float:
    """
    U, empuje de flotacion por metro lineal de conducto, kN/m (num.
    2.4.3.8.2): conducto totalmente sumergido, la hipotesis conservadora de
    "NF en su cota mas alta" que fija la fila V7 de la Fase 5 (ver "Por que
    U asume sumersion completa" en el docstring del modulo).

    U = gamma_agua * (pi/4) * D^2 -- el area exterior del conducto, D como
    aproximacion del diametro exterior (el catalogo de Sec. 3.2 no separa
    diametro interior de exterior; usarlo es del lado conservador, un
    exterior real algo mayor daria un U un poco mayor).
    """
    return GAMMA_AGUA_KN_M3 * (math.pi / 4) * D ** 2   # literal-ok: area de circulo, num. 2.4.3.8.2


def peso_relleno_kn_m(*, D: float, altura_relleno: float) -> float:
    """
    Peso del relleno sobre la clave, kN/m: prisma de ancho D (el diametro
    del conducto, la misma aproximacion de `empuje_flotacion_kn_m`) y altura
    `altura_relleno`, con el peso especifico del criterio
    'peso_especifico_relleno_kn_m3'.

    NO suma el peso propio del conducto -- ver "Por que el peso propio del
    conducto no entra en V7" en el docstring del modulo: omitirlo es
    conservador, no una aproximacion optimista.
    """
    gamma_relleno = ca.valor(CRITERIO_PESO_RELLENO)   # CriterioPendienteError mientras falte
    return gamma_relleno * D * altura_relleno


COMBINACION_V7 = "Resistencia I"
# V7 es un equilibrio de factores de carga LRFD -- MINORA lo que estabiliza
# (DC, EV) y MAYORA lo que desestabiliza (WA) -- y esos son exactamente los
# extremos que trae Resistencia I (Strength I) en la Tabla 3.4.1-1/-2; las
# otras dos combinaciones (Servicio I, Evento Extremo I) colapsan DC/EV/WA a
# 1.00 y no aportarian el margen que V7 exige. Se fija aqui, no en el
# criterio: 'factores_carga_aashto' declara las TRES combinaciones (Sec. 9.2
# de M9 las necesita todas), y cual de las tres usa V7 es una decision de
# este modulo, no del dato.


def factores_carga_flotacion() -> FactoresFlotacion:
    """
    Los tres gamma que V7 necesita, leidos de la fila 'Resistencia I' de
    'factores_carga_aashto' (Tablas 3.4.1-1 y 3.4.1-2 de AASHTO LRFD): el
    MINIMO de DC y de EV, que son las cargas estabilizantes, y el de WA, que
    es la desestabilizante.

    'factores_carga_aashto' es [C] (AASHTO LRFD 9a ed., Tablas 3.4.1-1/-2) y
    es el MISMO criterio que consumen las combinaciones de M9 (Sec. 9.2):
    dos juegos de factores de carga en un mismo expediente es exactamente la
    contradiccion que Sec. 0.7 existe para impedir.

    Forma esperada del criterio: un dict por combinacion, y dentro de cada
    combinacion un dict por tipo de carga con sus dos extremos::

        {"Resistencia I": {"DC": {"min": ..., "max": ...},
                           "EV": {"min": ..., "max": ...},
                           "WA": {"min": ..., "max": ...}, ...},
         "Servicio I": {...}, "Evento Extremo I": {...}}
    """
    tabla = ca.valor(CRITERIO_FACTORES_CARGA)
    fila_combinacion = tabla.get(COMBINACION_V7) if hasattr(tabla, "get") else None
    if fila_combinacion is None:
        raise DatoInvalidoError(
            campo=CRITERIO_FACTORES_CARGA, valor=tabla,
            motivo=f"V7 necesita la combinacion '{COMBINACION_V7}' "
                   f"declarada en '{CRITERIO_FACTORES_CARGA}' y la "
                   "declaracion no la trae",
        )
    return FactoresFlotacion(
        gamma_DC=_gamma(fila_combinacion, CARGA_PESO_PROPIO, EXTREMO_ESTABILIZANTE),
        gamma_EV=_gamma(fila_combinacion, CARGA_RELLENO, EXTREMO_ESTABILIZANTE),
        gamma_WA=_gamma(fila_combinacion, CARGA_AGUA, EXTREMO_DESESTABILIZANTE),
        criterio=CRITERIO_FACTORES_CARGA,
    )


def _gamma(fila_combinacion, tipo_de_carga: str, extremo: str) -> float:
    """
    Un gamma de la fila de combinacion declarada, con el error del
    expediente cuando la declaracion no trae la carga o el extremo que V7
    pide. Es `DatoInvalidoError` y no `KeyError` porque el problema esta en
    lo que el revisor escribio en 'factores_carga_aashto', no en el
    programa.
    """
    fila = fila_combinacion.get(tipo_de_carga) if hasattr(fila_combinacion, "get") else None
    if fila is None or not hasattr(fila, "get") or extremo not in fila:
        raise DatoInvalidoError(
            campo=CRITERIO_FACTORES_CARGA, valor=fila_combinacion,
            motivo=f"V7 necesita el gamma '{extremo}' de la carga "
                   f"'{tipo_de_carga}' (combinacion '{COMBINACION_V7}', "
                   "Tablas 3.4.1-1/-2) y la declaracion no lo trae. Se "
                   f"espera un dict {{'{COMBINACION_V7}': "
                   "{'DC': {'min': ..., 'max': ...}, 'EV': {...}, "
                   "'WA': {...}}}",
        )
    return float(fila[extremo])


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
# Item 5 - Rigidez de anillo, pandeo y costura: diferido al expediente
# ---------------------------------------------------------------------------

def verificacion_diferida_estructural() -> Tuple[str, ...]:
    """
    Fase 8, item 5: "Diferir al expediente la verificacion detallada:
    rigidez de anillo, pandeo y resistencia de costura por AASHTO LRFD
    Sec. 12 (que el Manual de Puentes no incorpora), o clase D-load con
    factor de cama."

    NO es un vacio a rellenar -- es un alcance que la propia hoja de ruta
    excluye del script. No se calcula ni se aproxima: se declara diferido,
    con su fundamento, para que M11 lo imprima siempre junto al resto de
    Fase 8.
    """
    return (
        "Rigidez de anillo: diferida al expediente tecnico -- AASHTO LRFD "
        f"Sec. 12 no esta incorporada por el Manual de Puentes ({NUMERAL_8_5})",
        "Pandeo (buckling): diferido al expediente tecnico, misma razon "
        f"({NUMERAL_8_5})",
        "Resistencia de costura: diferida al expediente tecnico, misma "
        f"razon ({NUMERAL_8_5}); alternativa: clase D-load con factor de cama",
    )
