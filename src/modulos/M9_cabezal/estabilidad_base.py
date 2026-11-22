# -*- coding: utf-8 -*-
"""
M9_cabezal.estabilidad_base
===========================
Submodulo de Fase 9 (`M9_cabezal`): bloque `estabilidad_base` (D1).
"""

from __future__ import annotations

import math
from typing import Any, Optional, Tuple

from src import criterios_adoptados as ca
from src.constantes_normativas import (
    COMBINACIONES_AASHTO,
    EXCENTRICIDAD_ADMISIBLE_FRACCION_B,
    FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1,
    FS,
    FS_CODIGO,
    FS_NUMERAL,
    GAMMA_P_MARCA,
    NQ_ZAPATA_EN_TALUD,
    NUMERAL_COMBINACIONES,
    NUMERAL_C_PHI,
    NUMERAL_EXCENTRICIDAD_SISMICA,
    NUMERAL_PRESION_CONTACTO,
    NUMERAL_RCBC,
    NUMERAL_TABLA_GAMMA_P,
    RCBC_BETAS_GRADOS,
    RCBC_COLUMNAS_NS,
    RCBC_EN_TALUD_T10_6_3_1_2C_1,
    RCBC_JUNTO_AL_TALUD_T10_6_3_1_2C_2,
    TABLA_COMBINACIONES_FILAS,
    TABLA_GAMMA_P_FILAS,
)
from src.modelos import (
    CombinacionCarga,
    CondicionAnalisis,
    DatoInvalidoError,
    DisenoNoFactibleError,
    EntornoDelCabezal,
    EstabilidadCabezal,
    GeometriaCabezal,
    LimiteNumericoError,
    MOTIVO_METODO_NO_EVALUABLE_CABEZAL,
    MetodoNoEvaluableError,
    PresionContactoBase,
    Verificacion,
)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

from src.modulos.M9_cabezal._criterios import (
    CAMPOS_TALUD_DELANTE,
    COMPONENTES_COMBINACION,
    CRITERIO_ESTABILIDAD_GLOBAL,
    CRITERIO_FACTORES_CARGA,
    CRITERIO_GAMMA_EQ,
    CRITERIO_TALUD_DELANTE,
    CRITERIO_TERRENO_DELANTE,
    EXIGIDAS_SEC_9_3,
    EXTREMOS,
    NUMERAL_9_3,
    PHI_MAX_TABLA_GRADOS,
    TERRENO_HORIZONTAL,
    TERRENO_TALUD,
    _finito,
)

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
# que se valida (cli.py recorre RECUBRIMIENTO y DIRECCIONES_CUANTIA_MURO para
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


def n_s_zapata_en_talud(*, H_s: float, gamma: float, c: float) -> float:
    """
    Factor de estabilidad del talud N_s de AASHTO LRFD 10.6.3.1.2c (ec.
    10.6.3.1.2c-2, pag. impresa 10-75):

        N_s = gamma·H_s / c

    --- VE-5 (ficha T7B-04) --- Hasta VE-5 era la del Manual de Puentes
    2.8.1.3.1.2c (N_s = 0 si B < H_s), la de los abacos de Meyerhof que el
    proyecto ya no lee. Con c = 0 (suelo friccionante, E.050 Art. 20) N_s no
    esta definido: las tablas tienen para ese caso su columna «c' = 0», que
    elige `coeficiente_rcbc`; aqui se levanta `DatoInvalidoError` en vez de
    devolver infinito.
    """
    if not c > 0:
        raise DatoInvalidoError(
            campo="c", valor=c,
            motivo=("N_s = gamma·H_s/c no esta definido con c = 0 (suelo "
                    f"friccionante, {NUMERAL_C_PHI}): las tablas de "
                    f"{NUMERAL_RCBC} lo resuelven con su columna c' = 0"))
    return gamma * H_s / c


def n_q_zapata_en_talud() -> float:
    """
    N_q = 0.0 para la zapata en talud. [N] literal de `constantes_normativas`.

    --- VE-5 --- La ec. 10.6.3.1.2c-1 de AASHTO tampoco lleva el termino de
    sobrecarga (q_n = RC_BC·(c·N_cm + 0.5·gamma·B·N_gamma_m)): sus
    coeficientes son de zapatas sin empotramiento, y la perdida de
    confinamiento del borde se escribe anulando ese termino, como en el
    Manual de Puentes.
    """
    return NQ_ZAPATA_EN_TALUD


def _interpolar_en(nodo: dict, x: float) -> Tuple[Any, Any, float]:
    """(inferior, superior, fraccion) de `x` entre las claves de `nodo`."""
    claves = sorted(nodo)
    if x <= claves[0] + TOL_UMBRAL_NORMATIVO:
        return nodo[claves[0]], nodo[claves[0]], 0.0
    for a, b in zip(claves, claves[1:]):
        if x <= b + TOL_UMBRAL_NORMATIVO:
            f = min(max((x - a) / (b - a), 0.0), 1.0)
            return nodo[a], nodo[b], f
    return nodo[claves[-1]], nodo[claves[-1]], 0.0


def _multilineal(nodo, coordenadas: Tuple[float, ...]):
    """Interpolacion lineal anidada sobre las claves de un dict de tablas;
    la hoja es una tupla, que se interpola componente a componente."""
    if not coordenadas:
        return nodo
    a, b, f = _interpolar_en(nodo, coordenadas[0])
    va = _multilineal(a, coordenadas[1:])
    vb = _multilineal(b, coordenadas[1:])
    return tuple(x + (y - x) * f for x, y in zip(va, vb))


def _fuera_de_la_tabla(que: str, id_punto: Optional[str]
                       ) -> MetodoNoEvaluableError:
    return MetodoNoEvaluableError(
        "reduccion por talud de la capacidad portante del cabezal",
        "analisis limite o de equilibrio limite de la zapata en el talud "
        "(AASHTO C10.6.3.1.2c)",
        f"{que}: fuera de las Tablas 10.6.3.1.2c-1 y -2 ({NUMERAL_RCBC}). "
        "El comentario pide entonces el analisis limite; la tabla no se "
        "extrapola", id_punto=id_punto,
        rotulo=MOTIVO_METODO_NO_EVALUABLE_CABEZAL)


def coeficiente_rcbc(*, phi_grados: float, c_kpa: float, gamma: float,
                     B: float, H_s: float, b: float, beta_grados: float,
                     id_punto: Optional[str] = None) -> Tuple[float, dict]:
    """
    RC_BC, coeficiente de reduccion de la capacidad portante por talud de
    AASHTO LRFD 10.6.3.1.2c (Tablas 10.6.3.1.2c-1 y -2, pags. impresas 10-76
    a 10-78), y el detalle de la lectura.

      b = 0     zapata EN el talud: Tabla 10.6.3.1.2c-1, por phi, B/H_s y
                beta (B/H_s de 0.1 a 3);
      b > 0     zapata JUNTO al talud: Tabla 10.6.3.1.2c-2, por phi, B/H_s,
                b/B y beta (B/H_s de 0.2 a 2, b/B de 0 a 10; mas alla de 10
                se toma la fila de 10, que ya es 1.00 o casi: lado seguro).
      columna   c = 0 (friccionante, E.050 Art. 20): la columna «c' = 0»;
                c > 0: N_s = gamma·H_s/c (`n_s_zapata_en_talud`) entre sus
                columnas 0, 2 y 4.

    «Use linear interpolation to obtain reduction coefficients for values
    not provided»: interpolacion lineal anidada en phi, B/H, [b/B], beta y
    N_s. Bajo beta = 10 grados (el talud mas tendido de la tabla) se toma la
    fila de 10: el coeficiente crece al tender el talud, y no se inventa el
    valor de 0 grados. LO QUE NO SE EXTRAPOLA -- beta > 40, N_s > 4, phi >
    40, B/H fuera de su rango -- detiene con `MetodoNoEvaluableError`: el
    comentario pide el analisis limite para geometrias y suelos fuera de las
    de la referencia.
    """
    for nombre, x in (("phi", phi_grados), ("c", c_kpa), ("gamma", gamma),
                      ("B", B), ("H_s", H_s), ("b", b),
                      ("beta", beta_grados)):
        if not _finito(x):
            raise DatoInvalidoError(nombre, valor=x, id_punto=id_punto,
                                    motivo="se espera un numero finito")
    if not (B > 0 and H_s > 0 and gamma > 0 and b >= 0 and c_kpa >= 0
            and phi_grados >= 0 and beta_grados > 0):
        raise DatoInvalidoError(
            "talud delante del cabezal", id_punto=id_punto,
            valor=(B, H_s, b, beta_grados, c_kpa, phi_grados),
            motivo="B, H_s, gamma y beta positivos; b, c y phi no negativos")
    t1, t2 = RCBC_EN_TALUD_T10_6_3_1_2C_1, RCBC_JUNTO_AL_TALUD_T10_6_3_1_2C_2
    if phi_grados > max(t1) + TOL_UMBRAL_NORMATIVO:
        raise _fuera_de_la_tabla(f"phi = {phi_grados:g} grados > {max(t1)}",
                                 id_punto)
    if beta_grados > max(RCBC_BETAS_GRADOS) + TOL_UMBRAL_NORMATIVO:
        raise _fuera_de_la_tabla(f"talud de {beta_grados:g} grados > "
                                 f"{max(RCBC_BETAS_GRADOS)}", id_punto)
    beta = max(beta_grados, min(RCBC_BETAS_GRADOS))
    B_H = B / H_s
    if c_kpa > 0:
        N_s = n_s_zapata_en_talud(H_s=H_s, gamma=gamma, c=c_kpa)
        if N_s > max(RCBC_COLUMNAS_NS) + TOL_UMBRAL_NORMATIVO:
            raise _fuera_de_la_tabla(f"N_s = gamma·H_s/c = {N_s:.3f} > "
                                     f"{max(RCBC_COLUMNAS_NS)}", id_punto)
    else:
        N_s = None
    if b > TOL_UMBRAL_NORMATIVO:
        tabla, nombre = t2, "10.6.3.1.2c-2"
        filas_BH = sorted(next(iter(t2.values())))
        b_B = min(b / B, max(next(iter(next(iter(t2.values())).values()))))
        coordenadas = (phi_grados, B_H, b_B, beta)
    else:
        tabla, nombre = t1, "10.6.3.1.2c-1"
        filas_BH = sorted(next(iter(t1.values())))
        b_B = 0.0
        coordenadas = (phi_grados, B_H, beta)
    if not (filas_BH[0] - TOL_UMBRAL_NORMATIVO <= B_H
            <= filas_BH[-1] + TOL_UMBRAL_NORMATIVO):
        raise _fuera_de_la_tabla(
            f"B/H_s = {B:.3f}/{H_s:.3f} = {B_H:.3f} fuera de "
            f"{filas_BH[0]:g} a {filas_BH[-1]:g} (Tabla {nombre})", id_punto)
    fila = _multilineal(tabla, coordenadas)
    if N_s is None:
        rc = fila[len(RCBC_COLUMNAS_NS)]           # la columna c' = 0
        columna = "c' = 0"
    else:
        columnas = dict(zip(RCBC_COLUMNAS_NS, fila))
        a, b2, f = _interpolar_en(columnas, N_s)
        rc = a + (b2 - a) * f
        columna = f"N_s = {N_s:.3f}"
    return rc, {"tabla": nombre, "B_H": B_H, "b_B": b_B, "beta": beta,
                "N_s": N_s, "columna": columna, "RC_BC": rc}


def validar_talud_delante(valor: Any, *, id_punto: Optional[str] = None
                          ) -> dict:
    """
    La geometria del talud que desciende delante de la zapata (Figura
    10.6.3.1.2c-1 de AASHTO): `H_s_m`, la altura del terreno inclinado bajo
    la base de la zapata (m, > 0); `beta_grados`, su inclinacion (> 0 y <
    90); `b_m`, la distancia del borde de la zapata a la coronacion del
    talud (m, >= 0; 0 = zapata en el talud). Forma y dominio, o
    `DatoInvalidoError`.
    """
    if not hasattr(valor, "get") or set(valor) != set(CAMPOS_TALUD_DELANTE):
        raise DatoInvalidoError(
            CRITERIO_TALUD_DELANTE, valor=valor, id_punto=id_punto,
            motivo="se espera {'H_s_m': ..., 'beta_grados': ..., 'b_m': ...}")
    H_s, beta, b = (valor["H_s_m"], valor["beta_grados"], valor["b_m"])
    recto = math.degrees(math.pi / 2)
    if not (all(_es_numero_finito(x) for x in (H_s, beta, b))
            and H_s > 0 and 0 < beta < recto and b >= 0):
        raise DatoInvalidoError(
            CRITERIO_TALUD_DELANTE, valor=valor, id_punto=id_punto,
            motivo="H_s > 0 m, 0 < beta < 90 grados y b >= 0 m, numeros "
                   "finitos")
    return {"H_s_m": float(H_s), "beta_grados": float(beta),
            "b_m": float(b)}


# --- VE-7 (lote A, A6; ficha VE5M9-03) --- LA GEOMETRIA DEL TALUD DE
# DELANTE, POR PUNTO (o en `globales`), un valor para los dos cabezales o
# {"entrada": ..., "salida": ...}: gana al [S] de corredor
# 'talud_delante_del_cabezal', como la sobrecarga del punto (VE6M9-04).
DATO_TALUD_DELANTE_DEL_PUNTO = "talud_delante_del_cabezal_del_punto"


def validar_talud_delante_del_punto(valor: Any, *,
                                    id_punto: Optional[str] = None) -> dict:
    """
    Forma y dominio de `talud_delante_del_cabezal_del_punto`, normalizada a
    {"entrada": x | None, "salida": x | None}. Cada x es la geometria del
    talud (`validar_talud_delante`, el validador del [S] de corredor) o
    --- dictamen Fable (VE-7 lote A, (iii)) --- el texto
    `TERRENO_HORIZONTAL`: el terreno de delante de ESE cabezal es
    horizontal, aunque el corredor diga talud.
    """
    def _uno(x):
        if x == TERRENO_HORIZONTAL:
            return TERRENO_HORIZONTAL
        return validar_talud_delante(x, id_punto=id_punto)

    if isinstance(valor, dict) and valor and set(valor) <= set(EXTREMOS):
        return {e: (_uno(valor[e]) if e in valor else None)
                for e in EXTREMOS}
    limpio = _uno(valor)
    return {e: (limpio if isinstance(limpio, str) else dict(limpio))
            for e in EXTREMOS}


def _terreno_delante(entorno: EntornoDelCabezal
                     ) -> Tuple[str, Optional[dict], str]:
    """
    --- dictamen Fable (VE-7 lote A, (iii)) --- (terreno, talud, origen) de
    delante de este cabezal: lo del PUNTO gana -- una geometria de talud ->
    `TERRENO_TALUD` con ella; «horizontal» -> `TERRENO_HORIZONTAL` --; sin
    declaracion, el criterio de corredor 'terreno_delante_del_cabezal' y,
    con talud, el [S] de corredor de su geometria.
    """
    del_punto = getattr(entorno, "talud_delante", None)
    if del_punto == TERRENO_HORIZONTAL:
        return TERRENO_HORIZONTAL, None, "del punto"
    if del_punto:
        return (TERRENO_TALUD,
                validar_talud_delante(del_punto, id_punto=entorno.id_punto),
                "del punto")
    terreno = ca.valor(CRITERIO_TERRENO_DELANTE)
    if terreno not in (TERRENO_HORIZONTAL, TERRENO_TALUD):
        raise DatoInvalidoError(CRITERIO_TERRENO_DELANTE, valor=terreno,
                                motivo=f"se espera '{TERRENO_HORIZONTAL}' o "
                                       f"'{TERRENO_TALUD}'")
    talud = (validar_talud_delante(ca.valor(CRITERIO_TALUD_DELANTE),
                                   id_punto=entorno.id_punto)
             if terreno == TERRENO_TALUD else None)
    return terreno, talud, "de corredor"


def capacidad_portante_zapata_en_talud(*, B: float, H_s: float, b: float,
                                       beta_grados: float, gamma: float,
                                       c: float, phi_grados: float,
                                       C_wgamma: float = 1.0,
                                       i_c: float = 1.0, i_gamma: float = 1.0,
                                       s_c: float = 1.0, s_gamma: float = 1.0,
                                       id_punto: Optional[str] = None
                                       ) -> Tuple[float, dict]:
    """
    q_n de la zapata EN o JUNTO a un talud, kPa, por AASHTO LRFD
    10.6.3.1.2c (ec. 10.6.3.1.2c-1, pag. impresa 10-74):

        q_n = RC_BC·(c·N_cm + 0.5·gamma·B·N_gamma_m)
        N_cm = N_c·s_c·i_c;  N_gamma_m = N_gamma·s_gamma·i_gamma·C_wgamma

    con N_c y N_gamma de la Tabla 10.6.3.1.2a-1 (`factores_de_capacidad_de_
    carga`) y RC_BC de `coeficiente_rcbc`. Sin termino de sobrecarga
    (`n_q_zapata_en_talud`): los coeficientes son de zapatas sin
    empotramiento, y la fuente avisa que con empotramiento pueden ser
    conservadores. C_wgamma, el del nivel freatico (Tabla 10.6.3.1.2a-2),
    se conserva: el agua bajo la zapata no deja de restar por estar en un
    talud.

    --- VE-5 (ficha T7B-04) --- SUSTITUYE la ecuacion del Manual de Puentes
    2.8.1.3.1.2c con los abacos de Meyerhof ('N_cq_N_gammaq_meyerhof',
    retirado), que no se podian transcribir: las tablas de la 9a edicion si.
    """
    if not (_finito(B) and B > 0 and _finito(gamma) and gamma > 0
            and _finito(c) and c >= 0):
        raise DatoInvalidoError(
            campo="B", valor=(B, gamma, c), id_punto=id_punto,
            motivo="ancho y peso especifico positivos y cohesion no negativa")
    rc, detalle = coeficiente_rcbc(phi_grados=phi_grados, c_kpa=c,
                                   gamma=gamma, B=B, H_s=H_s, b=b,
                                   beta_grados=beta_grados, id_punto=id_punto)
    N_c, _N_q, N_g = factores_de_capacidad_de_carga(phi_grados)
    termino_c = c * N_c * s_c * i_c
    termino_g = gamma * B * N_g * s_gamma * i_gamma * C_wgamma / 2
    q = rc * (termino_c + termino_g + n_q_zapata_en_talud())
    if not (math.isfinite(q) and q >= 0):
        raise LimiteNumericoError(
            "q_n", valor=q, id_punto=id_punto,
            motivo="la capacidad portante en talud no es finita y no "
                   "negativa")
    detalle.update(N_c=N_c, N_gamma=N_g, termino_c=termino_c,
                   termino_gamma=termino_g)
    return q, detalle


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
