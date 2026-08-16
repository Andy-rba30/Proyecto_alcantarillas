"""
M4_control.py
=============
Fases 4.2 y 4.3 de la hoja de ruta: control de entrada (HDS-5) y control de
salida. Tres piezas independientes y una regla de comparacion:

    1. tirante_critico(Q, D)        Sec. 4.2.1 - segundo Brent, sobre
                                    Q^2*T/(g*A^3) = 1
    2. control_entrada(...)         Sec. 4.2 - HDS-5, Tabla A.1, tres ramas
    3. control_salida(...)          Sec. 4.3 - HW = H + h_o - S*L
    4. hw_gobernante(...)           el mayor de las dos, CON su etiqueta

Las tres primeras son independientes entre si salvo por una dependencia real
de la fisica: tanto la Forma 1 del control de entrada (que necesita H_c) como
el h_o del control de salida (que necesita y_c) se apoyan en el tirante
critico. Por eso las dos aceptan un `TiranteCritico` ya resuelto como
argumento opcional: la pieza 1 se prueba sola, y las piezas 2 y 3 se prueban
solas inyectandole el critico que uno quiera, sin tener que resolver Brent
dentro del test.

Lo que M4 NO hace
-----------------
M4 no resuelve el tirante normal (eso es M3, Sec. 4.1), no elige material ni
diametro (M2), y no verifica nada: que HW/D <= 1.5 (V4b) o que HW quede bajo
la subrasante con su resguardo (V4) son verificaciones de la Fase 5 y las
hace M5 con el HW que este modulo entrega. M4 tampoco decide de donde sale el
TW: lo recibe como dato. El TW del cuerpo receptor es el criterio pendiente
'TW_receptor' (ANA / Junta de Usuarios) y quien lo resuelva debe declararlo,
no este modulo.

Los dos solvers de Brent (Sec. 4.2.1)
--------------------------------------
La hoja de ruta lo dice expresamente: "M4 requiere dos solvers, no uno". El
primero es el de M3 (tirante normal por Manning); el segundo es el de aqui:

    Q^2 * T / (g * A^3) = 1        con T = D*sen(theta/2)

Es otra ecuacion, no otra forma de la misma. El tirante normal depende de n y
de S; el critico NO depende de ninguno de los dos -- solo de Q y de la
geometria. De ahi que `TiranteCritico.V` si sea Q/A_c y no viole la regla de
doble n: no hay dos rugosidades entre las que elegir porque no hay rugosidad.

La ecuacion se resuelve en la forma equivalente A^3/T = Q^2/g (ver
`_residuo_critico`: la forma literal divide entre A^3 y ahi hay una division
por cero exacta en el borde vacio del intervalo). Asi escrita es monotona
creciente en theta sobre (0, 2*pi), de -Q^2/g en la seccion vacia a
+infinito en la llena: existe una unica raiz para todo Q > 0, de modo que --
a diferencia de `M3.tirante_normal` -- aqui no hay caso "sin solucion". Si Q
es enorme, el tirante critico simplemente se acerca a D, y quien decide que
eso es inadmisible es V1 (y/D <= 0.75), no este solver.

Control de entrada (Sec. 4.2)
------------------------------
    q* = Ku*Q / (A_llena * D^0.5)        Ku = 1.811 (SI)

    q* <= 3.5   HWi/D = H_c/D + K*(q*)^M + Ks*S      (no sumergido, Forma 1)
    q* >= 4.0   HWi/D = c*(q*)^2 + Y + Ks*S          (sumergido)
    entre ambos: interpolacion lineal

La interpolacion se hace entre el valor que da la forma NO SUMERGIDA evaluada
en q* = 3.5 y el que da la SUMERGIDA evaluada en q* = 4.0 -- no entre las dos
formas evaluadas en el q* real. Las dos ecuaciones son ajustes validos solo
dentro de su rango; extrapolarlas al interior de la zona de transicion, que
es justamente donde ninguna de las dos vale, seria usarlas fuera de su
dominio. Asi la curva HWi/D(q*) queda continua en los dos extremos.

K_s: no esta en la Tabla A.1
-----------------------------
Las cinco constantes de la Tabla A.1 son K, M, c e Y... y cuatro no son cinco.
K_s (-0.5 sin inglete, +0.7 con inglete) NO figura en esa tabla: proviene de
la formulacion de las ecuaciones y hay que traerlo aparte. Omitirlo es un
error silencioso, del mismo genero que el 29 imperial del control de salida:
con S = 0.005 y Ks = -0.5 el termino vale -0.0025 en HWi/D, unos 2 mm en un
tubo de 0.90 m -- invisible en una revision a ojo y sistematicamente sesgado.
Por eso `modelos.ConstantesHDS5` lo declara como campo obligatorio: no se
puede construir la carta sin el, y `constantes_normativas.HDS5_INLET` y el
criterio 'hds5_embocadura_hdpe' lo traen los cuatro.

Control de salida (Sec. 4.3)
-----------------------------
    HW = H + h_o - S*L
    H  = (1 + ke + 19.62*n^2*L/R^(4/3)) * V^2/(2g)
    h_o = max(TW, (y_c + D)/2)

19.62 es el valor SI (`constantes_normativas.K_FRICCION_SI`). El 29 de la
literatura FHWA es del sistema ingles y no falla ruidosamente en metrico:
devuelve numeros plausibles y equivocados -- con los datos de CP-8, 0.546 m
en vez de 0.498 m, un 9.6 % de diferencia. La guardia es
`test_constante_friccion_es_SI_no_imperial` (tests/test_M4_control.py), que
contrasta contra CP-8 y contra el valor que saldria con 29.

    NOTA DE COHERENCIA (declarar en la memoria): 19.62 = 2 * 9.81, mientras
    que la gravedad del proyecto es `constantes_normativas.G` = 9.8, el valor
    del Manual de Hidrologia MTC. Los dos numeros vienen de fuentes distintas
    (FHWA y MTC) y la hoja de ruta los da asi, cada uno con su origen; no se
    reconcilian aqui por cuenta propia. La discrepancia es del 0.1 % sobre el
    termino de friccion, tres ordenes por debajo de la incertidumbre de n.

De donde salen V y R en esa ecuacion: la hoja de ruta escribe la formula pero
no dice a que seccion pertenecen, y la eleccion mueve el resultado (R = D/4 =
0.225 m a seccion llena frente a R = 0.2715 m con y/D = 0.75, en un tubo de
0.90 m). No se rellena en silencio: esta declarado en el criterio
'geometria_control_salida' [C] = seccion llena, con su justificacion. Si se
cambia ese criterio, cambia el calculo sin tocar este archivo.

Cual gobierna
-------------
El HW de diseno es el MAYOR de los dos: cada control es una restriccion
independiente y la que exige mas carga es la que manda. `hw_gobernante()`
devuelve el par (HW, ControlGobernante) y `resolver_control()` lo deja
asentado en `ResultadoHidraulico.control_gobernante`, junto a los dos HW por
separado. Nunca se devuelve el maximo a secas: un HW sin la etiqueta de que
control lo produjo no le dice al revisor si el remedio es la embocadura o el
nivel del receptor.

Excepciones
-----------
    DatoInvalidoError        Q, D, S, L, n o TW no son fisicamente validos
                             para plantear el problema.
    CriterioPendienteError   llega desde 'ke_entrada' o
                             'geometria_control_salida' si alguno se vacia.

Uso
---
    from modulos.M4_control import (tirante_critico, control_entrada,
                                    control_salida, hw_gobernante,
                                    resolver_control)

    critico = tirante_critico(Q=1.0, D=0.90)
    entrada = control_entrada(Q=1.0, D=0.90, S=0.005, hds5=concreto.hds5)
    salida  = control_salida(Q=1.0, D=0.90, S=0.005, L=20.0, TW=0.30,
                             n=concreto.n_para_capacidad)
    HW, control = hw_gobernante(entrada, salida)
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

from scipy.optimize import brentq

import criterios_adoptados as ca
from constantes_normativas import (G, KU_METRICO, K_FRICCION_SI,
                                   Q_LIM_NO_SUMERGIDO, Q_LIM_SUMERGIDO)
from modelos import (ConstantesHDS5, ControlEntrada, ControlGobernante,
                     ControlSalida, DatoInvalidoError, Material,
                     RegimenEntrada, ResultadoHidraulico, TiranteCritico,
                     TiranteNormal)
from modulos.M3_hidraulica import geometria, resolver_manning
from tolerancias import TOL_BRENT, TOL_THETA_BORDE, TOL_UMBRAL_NORMATIVO

NUMERAL_CRITICO = "4.2.1"
NUMERAL_ENTRADA = "4.2"
NUMERAL_SALIDA = "4.3"

CRITERIO_KE = "ke_entrada"
CRITERIO_GEOMETRIA_SALIDA = "geometria_control_salida"

_THETA_MIN = TOL_THETA_BORDE
_THETA_MAX = 2 * math.pi - TOL_THETA_BORDE


# ---------------------------------------------------------------------------
# Validacion de entrada
# ---------------------------------------------------------------------------

def _validar_positivo(nombre: str, dato: float, motivo: str) -> None:
    if dato <= 0:
        raise DatoInvalidoError(nombre, valor=dato, motivo=motivo)


def _validar_Q_D(Q: float, D: float) -> None:
    _validar_positivo("Q", Q, "el caudal debe ser positivo")
    _validar_positivo("D", D, "el diametro debe ser positivo")


# ---------------------------------------------------------------------------
# Pieza 1 - Tirante critico (Sec. 4.2.1)
# ---------------------------------------------------------------------------

def area_llena(D: float) -> float:
    """A = pi*D^2/4, seccion circular llena. La usan q* (Sec. 4.2) y el
    control de salida (Sec. 4.3)."""
    return math.pi * D ** 2 / 4  # literal-ok: area del circulo, pi*D^2/4


def radio_hidraulico_lleno(D: float) -> float:
    """R = A/P = (pi*D^2/4)/(pi*D) = D/4, seccion circular llena (Sec. 4.3)."""
    return D / 4  # literal-ok: R = A/P de la seccion llena, D/4


def _residuo_critico(D: float, theta: float, Q: float) -> float:
    """
    Residuo de la ecuacion del tirante critico (Sec. 4.2.1), escrito como

        A^3/T - Q^2/g = 0

    que es la MISMA ecuacion que Q^2*T/(g*A^3) = 1 multiplicada por A^3/T.

    La reescritura no es cosmetica, es numerica: la forma literal de la hoja
    de ruta divide entre A^3, y en el extremo inferior del intervalo de Brent
    (theta = 1e-9 rad) el area vale CERO en aritmetica de doble precision --
    no un numero muy chico: cero exacto, porque theta - sen(theta) ~ theta^3/6
    ~ 1.7e-28 queda por debajo del ultimo bit de theta y la resta se cancela
    entera. Evaluar el residuo literal ahi es una division por cero, no una
    tendencia a infinito. Multiplicando por A^3/T la singularidad desaparece
    (T no se anula en ese extremo) y el residuo queda monotono CRECIENTE, de
    -Q^2/g en la seccion vacia a +infinito en la llena. La raiz es la misma.
    """
    geom = geometria(D, theta)
    return geom.A ** 3 / geom.T - Q ** 2 / G  # literal-ok: A^3/T = Q^2/g, Sec. 4.2.1


def tirante_critico(Q: float, D: float) -> TiranteCritico:
    """
    Tirante critico de la seccion circular (Sec. 4.2.1), raiz de

        Q^2 * T / (g * A^3) = 1        T = D*sen(theta/2)

    resuelta con Brent sobre theta en (0, 2*pi) -- el SEGUNDO solver que exige
    la hoja de ruta, distinto del de Manning: no interviene ni n ni S.

    Devuelve `TiranteCritico` con la geometria critica, la velocidad critica
    V_c = Q/A_c y la energia especifica critica H_c = y_c + V_c^2/(2g), que es
    lo que consume la Forma 1 del control de entrada.

    Siempre existe solucion para Q > 0 (el residuo cruza el cero una sola vez
    sobre el intervalo), de modo que esta funcion no tiene el caso "None" de
    `M3.tirante_normal`: un Q desmedido no deja al solver sin raiz, solo
    acerca y_c a D, y eso lo juzga V1 (y/D <= 0.75), no este solver.
    """
    _validar_Q_D(Q, D)

    def f(theta: float) -> float:
        return _residuo_critico(D, theta, Q)

    f_min, f_max = f(_THETA_MIN), f(_THETA_MAX)
    if not (f_min < 0 < f_max):
        # Inalcanzable con aritmetica finita para un Q y un D de proyecto: se
        # deja como guarda explicita en vez de dejar que brentq lance
        # ValueError, que la GUI no sabria clasificar (ErrorProyecto o crash).
        raise DatoInvalidoError(
            "Q", valor=Q,
            motivo=f"el residuo de {NUMERAL_CRITICO} no cambia de signo en "
                   f"(0, 2*pi) para D={D}: no hay tirante critico que resolver",
        )

    theta_critico = brentq(f, _THETA_MIN, _THETA_MAX, xtol=TOL_BRENT)
    geom = geometria(D, theta_critico)
    V_c = Q / geom.A
    return TiranteCritico(
        geometria=geom,
        V=V_c,
        H_c=geom.y + V_c ** 2 / (2 * G),
    )


# ---------------------------------------------------------------------------
# Pieza 2 - Control de entrada, HDS-5 (Sec. 4.2)
# ---------------------------------------------------------------------------

def caudal_adimensional(Q: float, D: float) -> float:
    """
    q* = Ku*Q / (A_llena * D^0.5), con Ku = 1.811 (SI), Sec. 4.2.

    El area es la de la seccion LLENA, no la del tirante: q* es un caudal
    adimensional de la abertura, no del flujo (asi lo fija el caso patron
    CP-5, que da A_llena = pi*D^2/4 = 0.63617 m2 para D = 0.90 m).
    """
    _validar_Q_D(Q, D)
    return KU_METRICO * Q / (area_llena(D) * math.sqrt(D))


def _hw_sobre_D_no_sumergido(q_estrella: float, H_c: float, D: float,
                             S: float, hds5: ConstantesHDS5) -> float:
    """HWi/D = H_c/D + K*(q*)^M + Ks*S, Forma 1 de Sec. 4.2 (q* <= 3.5)."""
    return H_c / D + hds5.K * q_estrella ** hds5.M + hds5.Ks * S


def _hw_sobre_D_sumergido(q_estrella: float, S: float,
                          hds5: ConstantesHDS5) -> float:
    """HWi/D = c*(q*)^2 + Y + Ks*S, regimen sumergido de Sec. 4.2 (q* >= 4.0)."""
    return hds5.c * q_estrella ** 2 + hds5.Y + hds5.Ks * S


def _regimen(q_estrella: float) -> RegimenEntrada:
    """Rama de Sec. 4.2 segun q*, con los limites [N] 3.5 y 4.0."""
    if q_estrella <= Q_LIM_NO_SUMERGIDO:
        return RegimenEntrada.NO_SUMERGIDO
    if q_estrella >= Q_LIM_SUMERGIDO:
        return RegimenEntrada.SUMERGIDO
    return RegimenEntrada.TRANSICION


def control_entrada(Q: float, D: float, S: float, hds5: ConstantesHDS5,
                    critico: Optional[TiranteCritico] = None) -> ControlEntrada:
    """
    Carga a la entrada bajo control de entrada (Sec. 4.2), HDS-5, Tabla A.1.

    Tres ramas segun el caudal adimensional q* = Ku*Q/(A_llena*D^0.5):

        q* <= 3.5   HWi/D = H_c/D + K*(q*)^M + Ks*S    (Forma 1, no sumergido)
        q* >= 4.0   HWi/D = c*(q*)^2 + Y + Ks*S        (sumergido)
        3.5 < q* < 4.0   interpolacion lineal entre el valor de la primera en
                    q* = 3.5 y el de la segunda en q* = 4.0

    El termino Ks*S no se omite: Ks no figura en la Tabla A.1 y viene de la
    formulacion (-0.5 sin inglete, +0.7 en inglete). Llega en
    `ConstantesHDS5.Ks`, que es un campo obligatorio justamente para que no se
    pueda armar una carta sin el.

    `critico` es opcional: si no se pasa, se resuelve aqui con la pieza 1. Se
    admite inyectarlo para no repetir Brent cuando el orquestador ya lo tiene
    (y para poder probar esta pieza sin depender de la anterior).
    """
    _validar_Q_D(Q, D)
    _validar_positivo("S", S, "la pendiente del conducto debe ser positiva")

    if critico is None:
        critico = tirante_critico(Q, D)

    q_estrella = caudal_adimensional(Q, D)
    regimen = _regimen(q_estrella)

    if regimen is RegimenEntrada.NO_SUMERGIDO:
        HW_sobre_D = _hw_sobre_D_no_sumergido(q_estrella, critico.H_c, D, S, hds5)
    elif regimen is RegimenEntrada.SUMERGIDO:
        HW_sobre_D = _hw_sobre_D_sumergido(q_estrella, S, hds5)
    else:
        # Interpolacion lineal entre los EXTREMOS del rango de validez de cada
        # forma, no entre las dos formas evaluadas en el q* real: dentro de la
        # transicion ninguna de las dos ecuaciones vale, y extrapolarlas seria
        # usarlas fuera de su dominio de ajuste. Asi la curva empalma continua
        # en q* = 3.5 y en q* = 4.0.
        extremo_inferior = _hw_sobre_D_no_sumergido(
            Q_LIM_NO_SUMERGIDO, critico.H_c, D, S, hds5)
        extremo_superior = _hw_sobre_D_sumergido(Q_LIM_SUMERGIDO, S, hds5)
        peso = ((q_estrella - Q_LIM_NO_SUMERGIDO)
                / (Q_LIM_SUMERGIDO - Q_LIM_NO_SUMERGIDO))
        HW_sobre_D = extremo_inferior + peso * (extremo_superior - extremo_inferior)

    return ControlEntrada(
        HW=HW_sobre_D * D,
        HW_sobre_D=HW_sobre_D,
        q_estrella=q_estrella,
        regimen=regimen,
        critico=critico,
        constantes=hds5,
    )


# ---------------------------------------------------------------------------
# Pieza 3 - Control de salida (Sec. 4.3)
# ---------------------------------------------------------------------------

def perdida_carga(V: float, R: float, n: float, L: float,
                  ke: Optional[float] = None) -> float:
    """
    H = (1 + ke + K_friccion*n^2*L/R^(4/3)) * V^2/(2g), Sec. 4.3, en SI.

    K_friccion es `constantes_normativas.K_FRICCION_SI` = 19.62. El 29 de la
    literatura FHWA es del sistema ingles: usarlo en metrico no falla
    ruidosamente, devuelve numeros plausibles y equivocados. Ver CP-8 y
    `test_constante_friccion_es_SI_no_imperial`.

    Los tres sumandos del parentesis son, en orden: carga de velocidad,
    perdida de entrada y perdida por friccion. `ke` sale del criterio
    'ke_entrada' [C] (0.5 para tubo a ras del muro) si no se pasa explicito.

    Toma V y R como argumentos sueltos, sin decidir de que seccion salen: esa
    decision es del criterio 'geometria_control_salida' y la aplica
    `control_salida()`. Asi esta funcion es exactamente la ecuacion de
    Sec. 4.3 y nada mas, que es lo que contrasta CP-8.
    """
    _validar_positivo("V", V, "la velocidad debe ser positiva")
    _validar_positivo("R", R, "el radio hidraulico debe ser positivo")
    _validar_positivo("n", n, "el coeficiente de Manning debe ser positivo")
    _validar_positivo("L", L, "la longitud del conducto debe ser positiva")

    if ke is None:
        ke = ca.valor(CRITERIO_KE)

    friccion = K_FRICCION_SI * n ** 2 * L / R ** (4 / 3)  # literal-ok: exponente 4/3 de Sec. 4.3
    return (1 + ke + friccion) * V ** 2 / (2 * G)


def _geometria_de_referencia(Q: float, D: float) -> Tuple[float, float]:
    """
    (V, R) de la seccion con la que se evalua Sec. 4.3, segun el criterio
    'geometria_control_salida' [C]. Hoy: seccion llena -- V = Q/(pi*D^2/4),
    R = D/4. Ver la justificacion completa en criterios_adoptados.py.
    """
    seleccion = ca.valor(CRITERIO_GEOMETRIA_SALIDA)
    if seleccion != "seccion_llena":
        raise DatoInvalidoError(
            CRITERIO_GEOMETRIA_SALIDA, valor=seleccion,
            motivo="M4 solo implementa la seccion llena de Sec. 4.3. Una "
                   "seccion de referencia distinta exige programar el "
                   "procedimiento de barril parcialmente lleno de HDS-5",
        )
    A = area_llena(D)
    return Q / A, radio_hidraulico_lleno(D)


def control_salida(Q: float, D: float, S: float, L: float, TW: float,
                   n: float, ke: Optional[float] = None,
                   critico: Optional[TiranteCritico] = None) -> ControlSalida:
    """
    Carga a la entrada bajo control de salida (Sec. 4.3):

        HW = H + h_o - S*L
        H  = (1 + ke + 19.62*n^2*L/R^(4/3)) * V^2/(2g)
        h_o = max(TW, (y_c + D)/2)

    `TW` es el tirante en el cuerpo receptor durante la avenida, en metros
    sobre el fondo de la SALIDA (no una cota): quien lo calcula es el modulo
    que resuelva Manning en el receptor, y mientras el criterio 'TW_receptor'
    siga vacio, quien lo pasa debe declarar con que escenario lo obtuvo. Se
    admite TW = 0 (salida libre); un TW negativo es DatoInvalidoError.

    `n` es el de la rama de CAPACIDAD (n_max, Sec. 4.1): HW es una carga, y la
    regla de doble n manda el n mayor -- mas friccion, mas H, mas remanso --
    del lado conservador de la inundacion. `resolver_control()` lo toma solo
    de `material.n_para_capacidad`; aqui se recibe explicito para poder
    probar la pieza aislada.

    El resultado puede salir negativo en un conducto largo y empinado, donde
    S*L supera a H + h_o. No es un error: significa que el control de salida
    no impone carga alguna a la entrada, y por eso siempre pierde frente al
    control de entrada en `hw_gobernante()`.
    """
    _validar_Q_D(Q, D)
    _validar_positivo("S", S, "la pendiente del conducto debe ser positiva")
    _validar_positivo("L", L, "la longitud del conducto debe ser positiva")
    if TW < 0:
        raise DatoInvalidoError("TW", valor=TW,
                                motivo="el tirante en el receptor no puede ser negativo")

    if critico is None:
        critico = tirante_critico(Q, D)

    V, R = _geometria_de_referencia(Q, D)
    H = perdida_carga(V=V, R=R, n=n, L=L, ke=ke)

    h_o_geometrico = (critico.y_c + D) / 2
    h_o = max(TW, h_o_geometrico)
    caida = S * L

    return ControlSalida(
        HW=H + h_o - caida,
        H=H,
        h_o=h_o,
        TW=TW,
        caida=caida,
        V=V,
        R=R,
        ahogado_por_TW=TW > h_o_geometrico,
        critico=critico,
    )


# ---------------------------------------------------------------------------
# Pieza 4 - Cual de los dos gobierna
# ---------------------------------------------------------------------------

def hw_gobernante(entrada: ControlEntrada,
                  salida: ControlSalida) -> Tuple[float, ControlGobernante]:
    """
    HW de diseno y control que lo produce (Sec. 4.2 y 4.3): el MAYOR de los
    dos. Cada control es una restriccion independiente sobre la misma
    estructura y la que exige mas carga es la que manda.

    Devuelve el par, nunca el maximo a secas: los dos numeros pueden estar a
    centimetros y el remedio de cada caso es distinto -- si gobierna la
    entrada se trabaja la embocadura o el diametro; si gobierna la salida,
    el problema esta aguas abajo (TW del receptor) y agrandar el tubo puede
    no mover el HW.

    Empate: se devuelve ENTRADA cuando la diferencia cae dentro de
    TOL_UMBRAL_NORMATIVO. No es una decision de calculo -- el HW es el mismo
    numero por ambos caminos, hasta la millonesima de milimetro -- sino la
    etiqueta con la que se reporta ese numero.
    """
    if salida.HW > entrada.HW + TOL_UMBRAL_NORMATIVO:
        return salida.HW, ControlGobernante.SALIDA
    return entrada.HW, ControlGobernante.ENTRADA


def resolver_control(D: float, Q: float, S: float, L: float, TW: float,
                     material: Material,
                     normal: Optional[TiranteNormal] = None
                     ) -> Optional[ResultadoHidraulico]:
    """
    Resultado hidraulico completo de una combinacion punto/material/diametro:
    junta el tirante normal de M3 (Sec. 4.1) con las tres piezas de M4
    (Sec. 4.2 y 4.3) en un `ResultadoHidraulico`.

    Devuelve None si M3 no encuentra tirante normal para esa D y ese material
    -- el conducto no transporta Q en flujo libre --, con la misma lectura que
    en M3: no es un fallo, es "este material y este diametro no alcanzan" y el
    orquestador de la Fase 4 pasa al siguiente diametro de M2.

    Reparto de rugosidades (regla de doble n, Sec. 4.1):
      - el tirante normal y la friccion del control de salida usan n_max
        (`material.n_para_capacidad`): conservador del lado de la inundacion;
      - la velocidad que sale en `ResultadoHidraulico.V` usa n_min, tal como
        la deja M3, para las verificaciones de erosion;
      - el tirante critico no usa ninguno: no depende de n.

    El tirante critico se resuelve UNA vez y se inyecta en las dos piezas que
    lo necesitan (Forma 1 del control de entrada y h_o del control de salida).
    """
    if normal is None:
        normal = resolver_manning(D=D, Q=Q, S=S, material=material)
    if normal is None:
        return None

    critico = tirante_critico(Q, D)
    entrada = control_entrada(Q=Q, D=D, S=S, hds5=material.hds5, critico=critico)
    salida = control_salida(Q=Q, D=D, S=S, L=L, TW=TW,
                            n=material.n_para_capacidad, critico=critico)
    _, control = hw_gobernante(entrada, salida)

    return ResultadoHidraulico(
        y_normal=normal.geometria.y,
        y_critico=critico.y_c,
        V=normal.V,
        Q=Q,
        HW_entrada=entrada.HW,
        HW_salida=salida.HW,
        control_gobernante=control,
    )
