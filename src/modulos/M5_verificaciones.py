"""
M5_verificaciones.py
=====================
Fase 5 de la hoja de ruta: las nueve verificaciones de la tabla principal
(V1 a V9), cada una como funcion propia que devuelve un `Verificacion` (nunca
un bool desnudo), mas `verificar()`, el agregado que MD.py llama con la firma
que declara su Protocol `Verificador`.

    V1  Borde libre               y/D <= 0.75                    [N] 4.1.1.3.7 b)
    V2  Velocidad minima          V >= 0.25 m/s                   [N] 4.1.1.3.6
    V3  Velocidad maxima          concreto: rango Tabla N 10 [N]
                                  TMC / HDPE: criterio pendiente   [C]
    V4  Carga a la entrada HW     HW <= cota subrasante - resguardo(CBR)  [N->]
    V5  Remanso aguas arriba      sin metodo declarado -> pendiente       [A]
    V6  Material solido de arrastre  seccion unica (cumple por construccion)
    V7  Flotacion del conducto    sin procedimiento declarado -> pendiente [C]
    V8  Evento extremo (FEN)      sin TR mayor ni umbral -> pendiente      [A]
    V9  Disponibilidad de diametro  D <= tope de M2                        [C]

Lo que NO se rellena en silencio
---------------------------------
V5, V7 y V8 enuncian un REQUISITO en la hoja de ruta pero no entregan la
formula, el metodo o el dato con que evaluarlo (ver el detalle en cada
funcion). Rellenarlos con un supuesto no declarado es exactamente lo que
CLAUDE.md prohibe como "el peor error posible en este proyecto": cada uno se
detiene con `CriterioPendienteError` desde un criterio nuevo en
`criterios_adoptados.py` ('remanso_derecho_via', 'flotacion_conducto',
'TR_evento_extremo'), con su justificacion y lo que falta para resolverlo. En
cuanto alguno de los tres reciba valor Y metodo, esta funcion se amplia --
hoy no hay ecuacion que escribir.

Consecuencia practica: mientras esos tres criterios sigan vacios,
`verificar()` (y por lo tanto `MD.disenar_punto` / `MD.disenar_lote`) se
detiene con `CriterioPendienteError` para CUALQUIER punto. No es un defecto
de este modulo: es la misma regla que ya aplica a 'TW_receptor' o
'v_max_tmc' -- un vacio real bloquea el calculo, no lo esconde. Las nueve
funciones individuales (v1_borde_libre, ..., v9_disponibilidad_diametro) SI
son utilizables una por una hoy mismo; es el AGREGADO el que hereda el
bloqueo de las tres pendientes.

V4 -- el supuesto de la cota de entrada (declarar en la memoria)
-------------------------------------------------------------------
`modelos.ResultadoHidraulico` documenta que HW es una carga en metros SOBRE
EL FONDO DE LA ENTRADA, y que la conversion a cota (msnm) es tarea de M7
("sumando la cota de entrada"). M7 todavia no existe, y `PuntoCritico` no
trae una columna de cota de fondo de entrada (a diferencia de
`cota_fondo_receptor`, que si la trae para la salida) -- Sec. 7.B llama a
esto "acoplamiento circular" y dice que se corta fijando la rasante en 7.A,
que tampoco existe aun.

V4 no puede esperar a M7 sin dejar de existir, asi que este modulo adopta
`punto.cota_terreno` como la cota de entrada: es el UNICO campo de Sec. 1.1
que describe la elevacion natural del cruce (el nivel del cauce antes de
cualquier obra), y por eso es la lectura mas defendible disponible hoy sin
inventar una columna que el CSV no tiene. Es una INTERPRETACION, no un
criterio adoptado con fuente propia -- declarala en la memoria como tal, y
reemplazala en cuanto M7 fije la cota real de invert de entrada.

Excepciones
-----------
    CriterioPendienteError   V3 en TMC/HDPE ('v_max_tmc' / 'v_max_hdpe');
                             V5 ('remanso_derecho_via'); V7
                             ('flotacion_conducto'); V8 ('TR_evento_extremo').
    DatoInvalidoError        el 'material' de V3 no es de TipoMaterial (no
                             deberia llegar aqui: M2 ya lo valido antes).

Uso
---
    from modulos.M5_verificaciones import verificar

    verificaciones = verificar(punto=punto, material=material, D=D,
                               resultado=resultado_hidraulico)
"""

from __future__ import annotations

from typing import Tuple

import criterios_adoptados as ca
from constantes_normativas import (RESGUARDO_NAPA_SUBRASANTE, V_MIN,
                                   Y_SOBRE_D_MAX)
from modelos import Material, PuntoCritico, ResultadoHidraulico, Verificacion
from modulos.M2_material import CRITERIO_DIAMETROS, CRITERIO_V_MAX
from tolerancias import TOL_UMBRAL_NORMATIVO

NUMERAL_V1 = "4.1.1.3.7 b)"
NUMERAL_V2 = "4.1.1.3.6"
NUMERAL_V3 = "Tabla Nº 10 (num. 4.1.1.3.6)"
NUMERAL_V4 = "5.1 (Manual de Suelos, num. 4.5.4 y 9.1(3))"
NUMERAL_V5 = "Fase 5, V5 (DG-2018 + Ley 29338)"
NUMERAL_V6 = "3.1"
NUMERAL_V7 = "Fase 5, V7 (Manual de Puentes num. 2.4.3.8.2)"
NUMERAL_V8 = "Fase 5, V8"
NUMERAL_V9 = "Sec. 3.2 (V9, nuevo en v7)"

CRITERIO_RESGUARDO = "resguardo_HW_subrasante"
CRITERIO_REMANSO = "remanso_derecho_via"
CRITERIO_FLOTACION = "flotacion_conducto"
CRITERIO_EVENTO_EXTREMO = "TR_evento_extremo"


# ---------------------------------------------------------------------------
# V1 - Borde libre (Sec. 4.1.1.3.7 b)
# ---------------------------------------------------------------------------

def v1_borde_libre(*, D: float, resultado: ResultadoHidraulico) -> Verificacion:
    """y/D <= 0.75: minimo 25 % de borde libre sobre el tirante normal."""
    y_sobre_D = resultado.y_normal / D
    return Verificacion(
        cumple=y_sobre_D <= Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V1,
        valor_obtenido=y_sobre_D,
        valor_admisible=Y_SOBRE_D_MAX,
        criterio_aplicado=None,          # [N] puro, sin criterio adoptado
        codigo="V1",
    )


# ---------------------------------------------------------------------------
# V2 - Velocidad minima (Sec. 4.1.1.3.6)
# ---------------------------------------------------------------------------

def v2_velocidad_minima(*, resultado: ResultadoHidraulico) -> Verificacion:
    """
    V >= 0.25 m/s. Sec. 5.2 de la hoja de ruta ya advierte que este piso casi
    nunca gobierna (se necesitaria una pendiente ~0.00006 para violarlo); la
    verificacion se calcula igual, sin dar por hecho el resultado.
    """
    return Verificacion(
        cumple=resultado.V >= V_MIN - TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V2,
        valor_obtenido=resultado.V,
        valor_admisible=V_MIN,
        criterio_aplicado=None,
        codigo="V2",
    )


# ---------------------------------------------------------------------------
# V3 - Velocidad maxima (Tabla N 10 / vacios PPI-FHWA)
# ---------------------------------------------------------------------------

def v3_velocidad_maxima(*, material: Material,
                        resultado: ResultadoHidraulico) -> Verificacion:
    """
    Concreto: rango [N] de la Tabla N 10, ya resuelto por M2 en
    `material.v_max_rango` (3.0-6.0 m/s) -- se verifican los DOS extremos,
    tal como los da la tabla.

    TMC y HDPE: la Tabla N 10 no los cubre (Tablero 1.3). El valor sale de
    `criterios_adoptados.valor('v_max_tmc' | 'v_max_hdpe')`, que hoy es None
    y por lo tanto lanza `CriterioPendienteError` -- V3 no puede evaluarse
    para estos materiales hasta que se extraiga el numero de PPI/FHWA. No es
    un fallo de este modulo: es el vacio que la hoja de ruta declara.
    """
    if material.tipo in CRITERIO_V_MAX:
        clave = CRITERIO_V_MAX[material.tipo]
        v_max = ca.valor(clave)     # CriterioPendienteError mientras falte
        return Verificacion(
            cumple=resultado.V <= v_max + TOL_UMBRAL_NORMATIVO,
            numeral=NUMERAL_V3,
            valor_obtenido=resultado.V,
            valor_admisible=v_max,
            criterio_aplicado=clave,
            codigo="V3",
        )

    v_min, v_max = material.v_max_rango
    cumple = (v_min - TOL_UMBRAL_NORMATIVO <= resultado.V
             <= v_max + TOL_UMBRAL_NORMATIVO)
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V3,
        valor_obtenido=resultado.V,
        valor_admisible=(v_min, v_max),
        criterio_aplicado=None,          # [N] puro, Tabla N 10
        codigo="V3",
    )


# ---------------------------------------------------------------------------
# V4 - Carga a la entrada HW (Sec. 5.1, resguardo por analogia [N->])
# ---------------------------------------------------------------------------

def _resguardo_por_cbr(cbr: float) -> float:
    """
    Resguardo de Sec. 5.1 segun el CBR de subrasante (Manual de Suelos, num.
    4.5.4): busca en `RESGUARDO_NAPA_SUBRASANTE` [N] la fila cuyo rango
    [CBR_min, CBR_max) contiene el dato, con los extremos None como
    ilimitados. Recorre las cuatro filas de la tabla, exhaustivas por
    construccion (cubren todo el dominio fisico del CBR).
    """
    for cbr_min, cbr_max, resguardo in RESGUARDO_NAPA_SUBRASANTE:
        piso = cbr_min is None or cbr >= cbr_min
        techo = cbr_max is None or cbr < cbr_max
        if piso and techo:
            return resguardo
    raise ValueError(
        f"CBR = {cbr} no cae en ninguna fila de RESGUARDO_NAPA_SUBRASANTE: "
        "la tabla deberia ser exhaustiva sobre el dominio fisico del dato"
    )


def v4_carga_entrada(*, punto: PuntoCritico,
                     resultado: ResultadoHidraulico) -> Verificacion:
    """
    HW <= cota de subrasante - resguardo(CBR), Sec. 5.1. El resguardo sale
    del criterio 'resguardo_HW_subrasante' [N->] (analogia declarada al nivel
    freatico, no un valor puntual: la tabla de CBR vive en
    `constantes_normativas.RESGUARDO_NAPA_SUBRASANTE`, [N] por numeral, y es
    la aplicacion de ESA tabla al HW lo que Sec. 5.1 etiqueta [N->]).

    `HW` es una carga en metros sobre el fondo de la entrada (Sec. 4.2/4.3);
    convertirla a cota exige la cota de esa entrada. Este modulo adopta
    `punto.cota_terreno` para eso -- ver "V4 -- el supuesto de la cota de
    entrada" en el docstring del modulo: es una interpretacion declarada, no
    un criterio con fuente propia, y debe citarse como tal en la memoria.
    """
    ca.valor(CRITERIO_RESGUARDO)      # registra el uso; "segun_CBR" no es numerico
    resguardo_m = _resguardo_por_cbr(punto.cbr_subrasante)

    cota_entrada = punto.cota_terreno     # ver supuesto declarado arriba
    HW_cota = cota_entrada + resultado.HW
    admisible = punto.cota_subrasante - resguardo_m

    return Verificacion(
        cumple=HW_cota <= admisible + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V4,
        valor_obtenido=HW_cota,
        valor_admisible=admisible,
        criterio_aplicado=CRITERIO_RESGUARDO,   # su etiqueta en ca.criterio() es "N->"
        codigo="V4",
    )


# ---------------------------------------------------------------------------
# V5 - Remanso aguas arriba (DG-2018 + Ley 29338)
# ---------------------------------------------------------------------------

def v5_remanso(*, punto: PuntoCritico,
              resultado: ResultadoHidraulico) -> Verificacion:
    """
    Embalse dentro del derecho de via, sin afectar terceros ni la faja
    marginal. La hoja de ruta fija el REQUISITO pero no un metodo de perfil
    de remanso ni el ancho de derecho de via por punto (no es columna del
    CSV, Sec. 1.2): sin los dos, V5 no tiene con que comparar el HW de M4.

    Se detiene en el criterio 'remanso_derecho_via' -- vacio a proposito, ver
    su justificacion en criterios_adoptados.py -- en vez de aproximar con el
    ancho de plataforma (`punto.ancho_plataforma`), que es la seccion vial
    construida y NO el derecho de via legal: usarlo seria inventar un dato
    que el expediente no declaro.
    """
    ca.valor(CRITERIO_REMANSO)        # CriterioPendienteError: sin metodo ni dato
    raise AssertionError("inalcanzable mientras 'remanso_derecho_via' este vacio")


# ---------------------------------------------------------------------------
# V6 - Material solido de arrastre (Sec. 3.1)
# ---------------------------------------------------------------------------

def v6_material_solido_arrastre() -> Verificacion:
    """
    Con palizada: seccion unica mayor, nunca multiple (Sec. 3.1). El
    catalogo de M2 (Sec. 3.2) y el bucle de MD solo ofrecen conductos
    circulares de UNA seccion -- el diseño multiceldular es Familia C
    (marco/multicelda, Sec. 2.3) y queda fuera del alcance de M2/MD. Por
    construccion del pipeline, esta verificacion nunca puede fallar hoy: si
    el proyecto alguna vez agrega diseño multibarril, esta funcion deja de
    ser trivial y hay que darle logica real.
    """
    return Verificacion(
        cumple=True,
        numeral=NUMERAL_V6,
        valor_obtenido="sección única (M2/MD no ofrecen diseño multibarril)",
        valor_admisible="sección única con palizada",
        criterio_aplicado=None,
        codigo="V6",
    )


# ---------------------------------------------------------------------------
# V7 - Flotacion del conducto (Manual de Puentes num. 2.4.3.8.2)
# ---------------------------------------------------------------------------

def v7_flotacion(*, punto: PuntoCritico, material: Material, D: float,
                 resultado: ResultadoHidraulico) -> Verificacion:
    """
    Sigma W (peso propio + relleno) >= FS * U, tuberia vacia, NF en su cota
    mas alta. El Manual de Puentes define la subpresion pero no incorpora
    AASHTO LRFD Sec. 12 (de donde sale el procedimiento): faltan el peso
    propio del conducto (Fase 8, sin programar), la altura de relleno sobre
    la clave (Fase 7.A, sin programar) y el FS de flotacion, ninguno
    declarado. Se detiene en el criterio 'flotacion_conducto'.
    """
    ca.valor(CRITERIO_FLOTACION)      # CriterioPendienteError: sin procedimiento
    raise AssertionError("inalcanzable mientras 'flotacion_conducto' este vacio")


# ---------------------------------------------------------------------------
# V8 - Evento extremo / FEN (Fase 5, V8)
# ---------------------------------------------------------------------------

def v8_evento_extremo(*, punto: PuntoCritico,
                      resultado: ResultadoHidraulico) -> Verificacion:
    """
    A un TR mayor que el de diseño, la via no colapsa aunque desborde. La
    hoja de ruta no fija ese TR mayor ni un umbral cuantitativo de colapso
    (p.ej. HW sobre la corona del terraplen): sin el TR no hay Q que correr
    aparte del de diseño, y sin el umbral no hay con que comparar el HW
    resultante. Se detiene en el criterio 'TR_evento_extremo'.
    """
    ca.valor(CRITERIO_EVENTO_EXTREMO)   # CriterioPendienteError: sin TR ni umbral
    raise AssertionError("inalcanzable mientras 'TR_evento_extremo' este vacio")


# ---------------------------------------------------------------------------
# V9 - Disponibilidad de diametro (Sec. 3.2, nuevo en v7)
# ---------------------------------------------------------------------------

def v9_disponibilidad_diametro(*, D: float, material: Material) -> Verificacion:
    """
    D requerido <= tope de la norma de producto del material. El tope es
    `material.D_max`, que M2 ya resolvio desde el criterio
    'diametros_normalizados' -- V9 solo lo consulta, no lo recalcula.
    """
    return Verificacion(
        cumple=D <= material.D_max + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V9,
        valor_obtenido=D,
        valor_admisible=material.D_max,
        criterio_aplicado=CRITERIO_DIAMETROS,
        codigo="V9",
    )


# ---------------------------------------------------------------------------
# Agregado: la firma que llama MD.py
# ---------------------------------------------------------------------------

def verificar(*, punto: PuntoCritico, material: Material, D: float,
             resultado: ResultadoHidraulico) -> Tuple[Verificacion, ...]:
    """
    Las nueve verificaciones de la Fase 5, en el orden de la tabla. Coincide
    con la firma de `modulos.MD.Verificador`: MD la importa como
    `modulos.M5_verificaciones.verificar` cuando no se le inyecta otra.

    Se detiene -- sin devolver nada -- en la primera de V3 (TMC/HDPE), V5, V7
    o V8 que este pendiente: son excepciones, no verificaciones incumplidas,
    y el bucle de MD no debe tratarlas como un diametro rechazado sino como
    lo que son, un calculo que no puede completarse todavia.
    """
    return (
        v1_borde_libre(D=D, resultado=resultado),
        v2_velocidad_minima(resultado=resultado),
        v3_velocidad_maxima(material=material, resultado=resultado),
        v4_carga_entrada(punto=punto, resultado=resultado),
        v5_remanso(punto=punto, resultado=resultado),
        v6_material_solido_arrastre(),
        v7_flotacion(punto=punto, material=material, D=D, resultado=resultado),
        v8_evento_extremo(punto=punto, resultado=resultado),
        v9_disponibilidad_diametro(D=D, material=material),
    )
