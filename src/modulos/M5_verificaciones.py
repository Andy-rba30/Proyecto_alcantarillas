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
    V7  Flotacion del conducto    equilibrio LRFD de factores de carga
                                  (Fase 8, M8_estructural); pendiente en
                                  'factores_carga_aashto' o
                                  'peso_especifico_relleno_kn_m3'              [A]
    V8  Evento extremo (FEN)      sin TR mayor ni umbral -> pendiente      [A]
    V9  Disponibilidad de diametro  D <= tope de M2                        [C]

Lo que NO se rellena en silencio
---------------------------------
V5 y V8 enuncian un REQUISITO en la hoja de ruta pero no entregan la formula,
el metodo o el dato con que evaluarlo (ver el detalle en cada funcion).
Rellenarlos con un supuesto no declarado es exactamente lo que CLAUDE.md
prohibe como "el peor error posible en este proyecto": cada uno se detiene
con `CriterioPendienteError` desde un criterio nuevo en
`criterios_adoptados.py` ('remanso_derecho_via', 'TR_evento_extremo'), con su
justificacion y lo que falta para resolverlo.

V7 SI tiene formula y metodo -- Fase 8, item 3 de la hoja de ruta, y
`modulos.M8_estructural` la implementa completa ("tuberia vacia, NF en su cota
mas alta"). Ya NO como un factor de seguridad global ΣW >= FS*U, sino como el
equilibrio de factores de carga que corresponde al marco LRFD de Sec. 0.2:

    gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U

Lo que sigue pendiente son dos DATOS puntuales del procedimiento, no el
procedimiento: el peso especifico del relleno
('peso_especifico_relleno_kn_m3') y los factores gamma
('factores_carga_aashto', el mismo criterio del que come M9). Ver el docstring
de `v7_flotacion` mas abajo.

Consecuencia practica: mientras 'remanso_derecho_via', 'TR_evento_extremo' y
los dos criterios de V7 sigan vacios, `verificar()` (y por lo tanto
`MD.disenar_punto` / `MD.disenar_lote`) se detiene con
`CriterioPendienteError` para CUALQUIER punto. No es un defecto de este
modulo: es la misma regla que ya aplica a 'TW_receptor' o 'v_max_tmc' -- un
vacio real bloquea el calculo, no lo esconde. Las nueve funciones
individuales (v1_borde_libre, ..., v9_disponibilidad_diametro) SI son
utilizables una por una hoy mismo; es el AGREGADO el que hereda el bloqueo de
las pendientes.

V4 -- el supuesto de la cota de entrada (declarar en la memoria)
-------------------------------------------------------------------
`modelos.ResultadoHidraulico` documenta que HW es una carga en metros SOBRE
EL FONDO DE LA ENTRADA, y que la conversion a cota (msnm) exige la cota de esa
entrada. `PuntoCritico` no trae una columna de cota de fondo de entrada (a
diferencia de `cota_fondo_receptor`, que si la trae para la salida).

V4 no puede existir sin esa cota, asi que este modulo adopta
`punto.cota_terreno`: es el UNICO campo de Sec. 1.1 que describe la elevacion
natural del cruce (el nivel del cauce antes de cualquier obra), y por eso es
la lectura mas defendible disponible sin inventar una columna que el CSV no
tiene. Es una INTERPRETACION, no un criterio adoptado con fuente propia --
declarala en la memoria como tal, y reemplazala el dia que el expediente
entregue la cota real de invert de entrada.

La interpretacion vive en `cota_entrada_supuesta()`, publica, porque M7
(tamizado de 7.A) convierte el MISMO HW a cota para fijar la rasante minima:
las dos tienen que leer la misma referencia o el acoplamiento circular que
7.A dice cortar sigue abierto. Lo mismo vale para `resguardo_por_cbr()`, que
es la segunda condicion del tamizado.

Excepciones
-----------
    CriterioPendienteError   V3 en TMC/HDPE ('v_max_tmc' / 'v_max_hdpe');
                             V5 ('remanso_derecho_via'); V7
                             ('peso_especifico_relleno_kn_m3' o
                             'factores_carga_aashto'); V8
                             ('TR_evento_extremo').
    DatoInvalidoError        el 'material' de V3 no es de TipoMaterial (no
                             deberia llegar aqui: M2 ya lo valido antes); en
                             V7, la clave del conducto queda a nivel de la
                             subrasante o por encima (no hay relleno que
                             pesar).

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
from modelos import (DatoFaltanteError, DatoInvalidoError, Material, PuntoCritico,
                     ReferenciaNormativa, ResultadoHidraulico, TipoMaterial,
                     Verificacion)
from modulos.M2_material import CRITERIO_DIAMETROS, CRITERIO_V_MAX
from modulos.M8_estructural import (CRITERIO_FACTORES_CARGA,
                                    empuje_flotacion_kn_m,
                                    factores_carga_flotacion,
                                    peso_relleno_kn_m)
from tolerancias import TOL_UMBRAL_NORMATIVO

NUMERAL_V1 = "4.1.1.3.7 b)"

# V2 y V3 salen del MISMO numeral y de la MISMA pagina, y por eso los dos
# numerales se escriben largos: lo que separa un piso de un techo no es el
# numero, es el titulo de la tabla y el parrafo que la sigue. Estos dos
# strings son lo UNICO que la memoria imprime de cada verificacion (M11 los
# vuelca en la columna "numeral"), asi que el sustento tiene que viajar aqui
# dentro o el revisor no lo ve: el titulo y la pagina vivian solo en el
# comentario de constantes_normativas y en docs/manifiesto_citas.md, que no
# van al expediente.
NUMERAL_V2 = ('MC-HHD (RD 20-2011-MTC/14), num. 4.1.1.3.6, pag. 76, parrafo '
              'inmediatamente posterior a la Tabla Nº 10. El numeral RECOMIENDA '
              'este minimo ("recomendandose que la velocidad minima sea igual '
              'a 0.25 m/s"), no lo prohibe: aqui se aplica como umbral duro '
              'por decision conservadora del proyecto')
NUMERAL_V3 = ('MC-HHD (RD 20-2011-MTC/14), Tabla Nº 10 "Velocidades maximas '
              'admisibles en conductos revestidos", num. 4.1.1.3.6, pag. 76. '
              'Los DOS numeros de cada fila son maximos segun la calidad del '
              'revestimiento: se verifica solo el superior, el piso lo pone V2')
NUMERAL_V4 = ReferenciaNormativa(
    seccion_hoja_ruta="Sec. 5.1",
    numeral_norma="Manual de Suelos, Geologia, Geotecnia y Pavimentos (MTC), "
                  "num. 4.5.4 y 9.1(3)",
)
NUMERAL_V5 = "Fase 5, V5 (DG-2018 + Ley 29338)"
NUMERAL_V6 = "3.1"
NUMERAL_V7 = ("Fase 5, V7 (subpresion: Manual de Puentes num. 2.4.3.8.2; "
              "equilibrio de factores de carga: AASHTO LRFD Tablas 3.4.1-1 y "
              "3.4.1-2, via el criterio 'factores_carga_aashto'; "
              "procedimiento: Fase 8, item 3)")
NUMERAL_V8 = "Fase 5, V8"
NUMERAL_V9 = "Sec. 3.2 (V9, nuevo en v7)"

CRITERIO_RESGUARDO = "resguardo_HW_subrasante"
CRITERIO_REMANSO = "remanso_derecho_via"
CRITERIO_EVENTO_EXTREMO = "TR_evento_extremo"
# Techo OPCIONAL del concreto. Se lee con `valor_si_declarado`, no con
# `valor`: sin declarar no bloquea nada y V3 usa el maximo [N] de la tabla.
CRITERIO_V_MAX_CONCRETO = "v_max_concreto_eleccion"


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

    Texto que lo sustenta, literal (MC-HHD, RD 20-2011-MTC/14, num. 4.1.1.3.6,
    pag. 76, parrafo inmediatamente posterior a la Tabla Nº 10):

        "Se deberá verificar que la velocidad mínima del flujo dentro del
        conducto no produzca sedimentación que pueda incidir en una reducción
        de su capacidad hidráulica, recomendándose que la velocidad mínima sea
        igual a 0.25 m/s."

    DOS COSAS QUE ESE TEXTO FIJA Y QUE HAY QUE LEER JUNTAS:

    (1) El 0.25 es una RECOMENDACION, no una prohibicion -- el numeral dice
        "recomendandose". Esta funcion lo aplica igualmente como umbral duro
        (`V >= V_MIN` decide `cumple`), que es la lectura conservadora y es la
        que el proyecto adopta. Pero el matiz no puede quedarse en el codigo:
        `NUMERAL_V2` lo lleva escrito, de modo que la memoria lo imprime junto
        al resultado y un revisor que vea un punto rechazado por V2 sepa que
        esta ante una recomendacion incumplida y no ante una infraccion.

    (2) La RAZON del minimo es la sedimentacion que reduce la capacidad
        hidraulica, no el desgaste. Es lo que separa a V2 de V3: el piso lo
        pone la sedimentacion y vale para todos los materiales por igual; el
        techo lo pone la abrasion del revestimiento y cambia con el material.
        Por eso los dos numeros de la Tabla Nº 10 son maximos y ninguno es
        este piso (ver `v3_velocidad_maxima`).
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
    V3 verifica UN SOLO extremo: el techo. V <= v_max.

    Materiales de la Tabla N 10 (concreto, ladrillo con concreto, mamposteria
    de piedra): M2 trae el par en `material.v_max_rango`, pero los DOS
    numeros del par son velocidades MAXIMAS -- la tabla se titula
    "Velocidades maximas admisibles en conductos revestidos" (num. 4.1.1.3.6,
    pag. 76) y el rango recorre la calidad del revestimiento, no un piso y un
    techo. El extremo inferior es el maximo admisible del acabado mas pobre;
    exigirlo como MINIMO era leer la tabla al reves.

    Ese error tenia consecuencia real: rechazaba por V3 un conducto de
    concreto a 1.5 m/s, que es una velocidad perfectamente admisible y que
    cumple de sobra el unico piso que la norma fija. Porque el piso existe y
    es otro: **V2**, autolimpieza, V >= 0.25 m/s, declarado aparte en la misma
    pagina y aplicable a todos los materiales por igual. Un segundo piso, mas
    alto y por material, no lo respalda ningun numeral.

    Se toma el extremo SUPERIOR del par como admisible: es el techo del
    revestimiento de mejor calidad.

    Techo mas conservador, OPCIONAL. Para el concreto, el proyectista puede
    declarar 'v_max_concreto_eleccion' y bajar ese techo -- hasta 3.0 m/s, el
    maximo del acabado mas pobre -- si las condiciones del acabado de ESTA
    obra lo ameritan. Se lee con `ca.valor_si_declarado`, NO con `ca.valor`:
    es un criterio opcional que refina un valor que la norma ya fija, no un
    vacio que la norma deje abierto. Sin declarar devuelve None, V3 aplica el
    6.0 de la tabla y el criterio no entra en la memoria. Leerlo con
    `ca.valor` bloquearia el concreto por un criterio que nadie tiene
    obligacion de declarar.

    `criterio_aplicado` distingue las dos procedencias, que es lo que un
    revisor necesita: None cuando el umbral es el [N] de la tabla, y la clave
    del criterio cuando el proyectista lo bajo.

    TMC y HDPE: la Tabla N 10 no los cubre (Tablero 1.3). El valor sale de
    `criterios_adoptados.valor('v_max_tmc' | 'v_max_hdpe')`, hoy 4.6 m/s los
    dos, con cita de WSDOT Hydraulics Manual M 23-03.12, Cap. 8, Tabla 8-4
    (el vacio que la hoja de ruta declaraba quedo cerrado). Se leen con
    `ca.valor`, no con `ca.valor_si_declarado`: no son opcionales -- si
    alguien los vaciara, V3 debe detenerse y no caer a un techo inventado,
    porque para estos materiales no hay ningun valor normativo de respaldo
    al que volver. Son un techo escalar, de modo que esta rama no cambia.
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

    # Solo el techo: el par de la Tabla N 10 son dos MAXIMOS, no un piso y un
    # techo (ver el docstring). El extremo inferior no se verifica.
    _, v_max = material.v_max_rango
    clave = None

    if material.tipo is TipoMaterial.CONCRETO_REFORZADO:
        adoptado = ca.valor_si_declarado(CRITERIO_V_MAX_CONCRETO)
        if adoptado is not None:
            v_max = adoptado
            clave = CRITERIO_V_MAX_CONCRETO

    return Verificacion(
        cumple=resultado.V <= v_max + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V3,
        valor_obtenido=resultado.V,
        valor_admisible=v_max,
        criterio_aplicado=clave,   # None = [N] puro de la Tabla N 10
        codigo="V3",
    )


# ---------------------------------------------------------------------------
# V4 - Carga a la entrada HW (Sec. 5.1, resguardo por analogia [N->])
# ---------------------------------------------------------------------------

def cota_entrada_supuesta(punto: PuntoCritico) -> float:
    """
    Cota del fondo de la entrada, msnm. Es la INTERPRETACION declarada en el
    docstring del modulo ("V4 -- el supuesto de la cota de entrada"): se adopta
    `punto.cota_terreno` mientras M7 no fije la cota real de invert.

    Es publica y con nombre propio porque V4 no es su unico consumidor: el
    tamizado de 7.A (M7) convierte el mismo HW a cota para fijar la rasante
    minima. Si cada modulo eligiera su propia cota de entrada, V4 y 7.A
    quedarian evaluando dos condiciones distintas y el acoplamiento circular
    que 7.A dice cortar seguiria abierto: la rasante se fijaria contra una
    referencia y se verificaria contra otra.
    """
    return punto.cota_terreno


def resguardo_por_cbr(cbr: float) -> float:
    """
    Resguardo de Sec. 5.1 segun el CBR de subrasante (Manual de Suelos, num.
    4.5.4): busca en `RESGUARDO_NAPA_SUBRASANTE` [N] la fila cuyo rango
    [CBR_min, CBR_max) contiene el dato, con los extremos None como
    ilimitados. Recorre las cuatro filas de la tabla, exhaustivas por
    construccion (cubren todo el dominio fisico del CBR).

    Publica por el mismo motivo que `cota_entrada_supuesta`: la segunda
    condicion del tamizado de 7.A (M7) es la misma tabla aplicada al mismo
    CBR, y duplicarla alli seria abrir la puerta a que las dos se separen.
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
    resguardo_m = resguardo_por_cbr(punto.cbr_subrasante)

    cota_entrada = cota_entrada_supuesta(punto)   # ver supuesto declarado arriba
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

    Los dos vacios se detienen por separado, y ninguno con un fallo de
    programa:

    - Criterio SIN valor -> `CriterioPendienteError` (la lanza `ca.valor`).
    - Criterio CON valor -> `DatoFaltanteError`. Declarar el criterio no
      cierra V5: sigue faltando el ancho de derecho de via del punto y el
      perfil de remanso con que comparar el HW de M4. El revisor tiene que
      ANADIR esos dos, y por eso es Faltante y no Invalido (CLAUDE.md).

    Antes esta segunda rama era un `raise AssertionError` desnudo: no
    descendia de `ErrorProyecto`, de modo que `cli._etapa` no lo capturaba y
    una corrida con el criterio declarado abortaba entera, con todos sus
    puntos, en vez de anotar el bloqueo y seguir.
    """
    ca.valor(CRITERIO_REMANSO)        # CriterioPendienteError: sin metodo ni dato
    raise DatoFaltanteError(
        "ancho_derecho_via_m",
        id_punto=punto.id,
        detalle=(
            f"el criterio '{CRITERIO_REMANSO}' esta declarado, pero V5 sigue "
            "sin poder resolverse: falta el ancho de derecho de via del punto "
            "(no es columna de Sec. 1.2) y el perfil de remanso aguas arriba "
            "con que comparar el HW de M4. La hoja de ruta fija el requisito "
            "y no el metodo: mientras no exista, V5 no se declara cumplida"
        ),
    )


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
# V7 - Flotacion del conducto (Manual de Puentes num. 2.4.3.8.2 + Fase 8.3)
# ---------------------------------------------------------------------------

def v7_flotacion(*, punto: PuntoCritico, material: Material, D: float,
                 resultado: ResultadoHidraulico) -> Verificacion:
    """
    Flotacion del conducto por EQUILIBRIO DE FACTORES DE CARGA LRFD, tuberia
    vacia y NF en su cota mas alta (Fase 5, fila V7):

        gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U

    Se minoran las cargas que estabilizan -- peso propio del conducto (DC) y
    peso del relleno sobre la clave (EV), con sus gamma MINIMOS de la Tabla
    3.4.1-2 -- y se mayora la subpresion, que desestabiliza (WA, Tabla
    3.4.1-1). Con los minimos de la tabla es la forma 0.90*(DC + EV) >= 1.00*U.

    NO es un FS global. La fila V7 de la hoja de ruta lo enuncia como
    ΣW >= FS*U, que es lenguaje de tension admisible; Sec. 0.2 adopta AASHTO
    LRFD de extremo a extremo, y verificar una demanda LRFD contra un FS
    clasico es la misma incoherencia carga-resistencia que esa seccion declara
    resuelta. El criterio 'FS_flotacion' que sostenia el umbral se retiro: en
    LRFD el margen lo hacen los propios gamma, y conservar ademas un FS seria
    contar dos veces el mismo margen. Ver "Por que V7 ya no usa un factor de
    seguridad global" en el docstring de `modulos.M8_estructural`.

    El procedimiento esta completo en `modulos.M8_estructural` (Fase 8, item
    3); esta funcion solo arma la altura de relleno del punto y ensambla el
    resultado.

    La altura de relleno sobre la clave es la REAL del punto -- cota de
    subrasante menos la cota de la clave -- no el minimo normativo de Sec.
    7.A ('h_relleno_min_concreto_tmc', que sigue sin valor para concreto y
    TMC): V7 pesa el relleno que de verdad hay encima, no un piso admisible.
    Usa la misma cota de entrada supuesta que V4 y M7 (`cota_entrada_supuesta`),
    para no evaluar la flotacion contra una referencia distinta de la que fija
    la rasante.

    DC = 0: no suma el peso propio del conducto (ver "Por que el peso propio
    del conducto no entra en V7" en el docstring de M8_estructural). Omitirlo
    es conservador, reduce el lado estabilizante en vez de inflarlo.

    Se detiene en 'peso_especifico_relleno_kn_m3' (el termino EV) o en
    'factores_carga_aashto' (los gamma), los dos vacios que le faltan al
    procedimiento -- no en un vacio de METODO: ver el docstring del modulo.
    """
    clave = cota_entrada_supuesta(punto) + D
    altura_relleno = punto.cota_subrasante - clave
    if altura_relleno <= TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            "cota_subrasante", valor=punto.cota_subrasante, id_punto=punto.id,
            motivo="la clave del conducto queda a nivel de la subrasante o "
                   "por encima: no hay relleno sobre la clave que pesar "
                   f"en V7 ({NUMERAL_V7})",
        )

    U = empuje_flotacion_kn_m(D=D)
    EV = peso_relleno_kn_m(D=D, altura_relleno=altura_relleno)
    DC = 0.0                 # peso propio omitido, del lado conservador
    g = factores_carga_flotacion()   # CriterioPendienteError si EV no se detuvo antes

    estabilizante = g.gamma_DC * DC + g.gamma_EV * EV
    desestabilizante = g.gamma_WA * U

    return Verificacion(
        cumple=estabilizante >= desestabilizante - TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V7,
        valor_obtenido=estabilizante,
        valor_admisible=desestabilizante,
        criterio_aplicado=CRITERIO_FACTORES_CARGA,
        codigo="V7",
    )


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
