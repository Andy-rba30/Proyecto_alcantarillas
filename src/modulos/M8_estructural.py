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
         `fs_flotacion()` -- SI implementadas: son las piezas de la formula
         ΣW >= FS*U que modulos.M5_verificaciones.v7_flotacion ensambla.
         El empuje U es siempre calculable (geometria + constante fisica);
         el peso del relleno se detiene en 'peso_especifico_relleno_kn_m3'
         y el umbral en 'FS_flotacion' -- ninguno de los dos esta en la
         hoja de ruta.

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

Por que el peso propio del conducto no entra en V7
----------------------------------------------------
ΣW = peso propio + peso del relleno, por la formula de la tabla de Fase 5
(fila V7). El peso propio depende del espesor de pared, que sale de la
clase/calibre seleccionada en los items 1-2 -- hoy bloqueados. Sumarlo
supondria inventar un espesor. Omitirlo es la alternativa conservadora, NO
una aproximacion optimista: un ΣW mas chico hace el chequeo MAS dificil de
cumplir, nunca lo relaja. Se declara aqui, en cada resultado y en la memoria,
en vez de aproximar en silencio.

Por que U asume sumersion completa
-------------------------------------
La fila V7 de la Fase 5 fija la hipotesis de calculo: "tuberia vacia, NF en
su cota mas alta". Con el NF somero del sitio (1.4 m, criterio
'NF_profundidad_m', [N]) y sin una columna de invert real en el CSV (Sec.
1.2 -- misma limitacion que `M5_verificaciones.cota_entrada_supuesta`), la
lectura conservadora de "NF en su cota mas alta" es sumersion completa del
conducto, no una geometria de sumersion parcial contra una cota de invert
supuesta. Nunca subestima el empuje.

Excepciones
-----------
    CriterioPendienteError   'clases_producto_por_relleno' (items 1-2);
                             'peso_especifico_relleno_kn_m3' o
                             'FS_flotacion' (V7, via
                             modulos.M5_verificaciones.v7_flotacion).

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
from constantes_normativas import CAMA_RELLENO_LATERAL, GAMMA_AGUA_KN_M3
from modelos import CamaApoyoRelleno, Material

NUMERAL_8_1_2 = "Fase 8, items 1-2"
NUMERAL_8_1 = "Sec. 8.1 (EG-2013 Seccion 500)"
NUMERAL_8_5 = "Fase 8, item 5"
NUMERAL_V7 = "Fase 5, V7 (Manual de Puentes num. 2.4.3.8.2)"

CRITERIO_CLASES_PRODUCTO = "clases_producto_por_relleno"
CRITERIO_FS_FLOTACION = "FS_flotacion"
CRITERIO_PESO_RELLENO = "peso_especifico_relleno_kn_m3"
CRITERIO_NF = "NF_profundidad_m"


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
    raise AssertionError(
        "inalcanzable mientras 'clases_producto_por_relleno' este vacio"
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
    ca.valor(CRITERIO_NF)      # registra el uso: el NF somero es la razon de la hipotesis
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


def fs_flotacion() -> float:
    """FS de V7, leido de 'FS_flotacion' (CriterioPendienteError mientras falte)."""
    return ca.valor(CRITERIO_FS_FLOTACION)


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
