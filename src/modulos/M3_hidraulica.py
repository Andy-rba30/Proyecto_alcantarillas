"""
M3_hidraulica.py
================
Fase 4.1 de la hoja de ruta: motor hidraulico. Geometria de la seccion
circular parcialmente llena y tirante normal por Manning, resuelto con
scipy.optimize.brentq sobre theta en (0, 2*pi).

Lo que M3 NO hace
-----------------
M3 no resuelve el control de entrada (HDS-5) ni el control de salida, ni el
tirante critico (Q^2*T/(g*A^3) = 1): eso es Sec. 4.2-4.3, modulo M4, que
combina su salida con la de este modulo en `modelos.ResultadoHidraulico`. M3
tampoco decide que material ni que diametro usar (M2) ni si el resultado
cumple las verificaciones de la Fase 5 (M5). Se limita a: dado D, Q, S y un n,
devolver la geometria del tirante que transporta ese Q, o None si ninguna
seccion entre vacio y lleno lo logra a esa pendiente.

Geometria (Sec. 4.1)
---------------------
    A = (D^2/8)(theta - sen theta)      P = D*theta/2      R = A/P
    Q = (1/n)*A*R^(2/3)*S^(1/2)

theta en radianes, mojado, sobre (0, 2*pi). `geometria()` arma el
`modelos.Geometria` completo (incluye y = (D/2)(1 - cos(theta/2)), la
identidad que la hoja de ruta no escribe explicita en Sec. 4.1 pero que hace
falta para poblar el campo `y` del tipo).

Regla de doble n (Sec. 4.1)
-----------------------------
n MAXIMO para capacidad y tirante (V1, borde libre): conservador del lado de
la inundacion. n MINIMO para velocidad MAXIMA y socavacion (V3, Laushey):
conservador del lado de la erosion.

La UNICA resolucion de Brent usa n_max: es el n que, para el mismo Q y D,
exige mas area y por lo tanto fija el theta real de diseño (mas resistencia
-> mas tirante para el mismo caudal). Las velocidades NO salen de una segunda
resolucion de Brent con un theta distinto: salen de recalcular Manning SOBRE
ESA MISMA geometria (mismo theta, mismo R) con cada uno de los dos n -- el
mismo canal visto con la rugosidad mas baja y con la mas alta. Asi lo fija el
fixture CP-2 (tests/fixtures/casos_patron.py: D, y/D, S fijos, y las dos
velocidades V_con_n_max y V_con_n_min salen de la MISMA R con dos n
distintos).

DOS VELOCIDADES, NO UNA (MAT-D1)
---------------------------------
Un umbral de velocidad no tiene un extremo conservador: tiene dos, y son
opuestos. Contra un TECHO (V3, Laushey) lo conservador es suponer la
velocidad mas ALTA que el rango de n admite, o sea calcularla con n_min.
Contra un PISO (V2, autolimpieza) lo conservador es exactamente lo contrario:
suponer la mas BAJA, que sale de n_max.

`resolver_manning()` devuelve las dos:

    V_erosion       = (1/n_min)*R^(2/3)*S^0.5    estimacion ALTA  -> V3, d50
    V_sedimentacion = (1/n_max)*R^(2/3)*S^0.5    estimacion BAJA  -> V2

Hasta esta correccion devolvia solo la primera, bajo el nombre `V`, y V2 la
consumia: un piso verificado con la estimacion alta. La Sec. 4.1 de la hoja
de ruta asigna n minimo a "velocidad maxima y socavacion" -- V2 no esta en
esa lista -- y el fixture CP-3 modela el umbral de V2 con n = 0.013, que es
n_max: el repositorio se contradecia a si mismo.

`V_sedimentacion` es ademas el minimo REAL de la velocidad sobre todo el rango
de n de la Tabla N 09, no solo el minimo sobre esta geometria: con un n menor
el tirante normal baja, el area baja y la velocidad media Q/A sube -- mientras
theta este en la rama creciente de la curva de capacidad, que es donde V1
mantiene el diseño (y/D <= 0.75); ver `modelos.TiranteNormal`, que enuncia la
condicion. Y cumple `V_sedimentacion * A = Q` exactamente, porque es la
velocidad media del mismo n con que se resolvio el tirante. Ver la advertencia
ya documentada en `modelos.TiranteNormal` (V_erosion*A != Q, por diseño).

`tirante_normal()`, la pieza mas chica, resuelve Manning para un solo n. Queda
publica porque M4 la reutiliza para lo que si necesita geometria de un n
suelto (p. ej. pruebas o un chequeo de capacidad a secas); el tirante critico
en si es una ecuacion distinta (Sec. 4.2.1) y vive en M4.

De donde sale el n de HDPE
----------------------------
M3 no lee `criterios_adoptados` en ningun punto: consume el `Material` que M2
ya resolvio (Sec. 3.4), incluidos `n_para_capacidad`,
`n_para_velocidad_maxima` y `n_para_velocidad_minima`. Para
HDPE, M2 ya puso alli el RANGO completo por analogia al concreto (0.010-0.013,
criterio 'n_manning_hdpe', Sec. 4.1.1) y no un valor puntual: un n unico
rompiria la regla de doble n porque las dos ramas usarian la misma rugosidad y
una de las dos dejaria de ser conservadora. `resolver_manning()` hereda esa
garantia sin tener que saber que material esta resolviendo.

El caso "sin solucion"
------------------------
Para una D chica y un Q grande, puede no existir theta en (0, 2*pi) donde
Manning iguale Q: el conducto trabajaria a presion, fuera del regimen de flujo
libre que modela este script. Eso NO es un error del programa: es un
resultado de diseño valido -- "este material y este diametro no alcanzan" --
y `tirante_normal()` y `resolver_manning()` lo devuelven como None, nunca como
una excepcion generica, para que el orquestador de la Fase 4 pase al siguiente
diametro de la progresion de M2.

Excepciones
-----------
    DatoInvalidoError   D, Q, S o n no son fisicamente validos para plantear
                        el problema (no negativos, no cero). No es el caso
                        "sin solucion": ese es un None, no una excepcion.

Uso
---
    from modulos.M3_hidraulica import resolver_manning, tirante_normal, geometria

    resolucion = resolver_manning(D=0.90, Q=1.1673, S=0.005, material=concreto)
    if resolucion is None:
        ...  # pasar al siguiente diametro
    y_normal = resolucion.geometria.y
    V_techo = resolucion.V_erosion        # contra V3 y el d50 de Laushey
    V_piso = resolucion.V_sedimentacion   # contra V2
"""

from __future__ import annotations

import math
from typing import Optional

from scipy.optimize import brentq

from modelos import DatoInvalidoError, Geometria, Material, TiranteNormal
from tolerancias import TOL_BRENT, TOL_THETA_BORDE

NUMERAL_MANNING = "4.1"

_THETA_MIN = TOL_THETA_BORDE
_THETA_MAX = 2 * math.pi - TOL_THETA_BORDE


# ---------------------------------------------------------------------------
# Validacion de entrada
# ---------------------------------------------------------------------------

def _validar_parametros(D: float, Q: float, S: float, n: float) -> None:
    if D <= 0:
        raise DatoInvalidoError("D", valor=D, motivo="el diametro debe ser positivo")
    if Q <= 0:
        raise DatoInvalidoError("Q", valor=Q, motivo="el caudal debe ser positivo")
    if S <= 0:
        raise DatoInvalidoError("S", valor=S, motivo="la pendiente debe ser positiva "
                                                       "para que Manning tenga solucion real")
    if n <= 0:
        raise DatoInvalidoError("n", valor=n, motivo="el coeficiente de Manning debe ser positivo")


# ---------------------------------------------------------------------------
# Geometria de la seccion circular parcialmente llena (Sec. 4.1)
# ---------------------------------------------------------------------------

def area(D: float, theta: float) -> float:
    """A = (D^2/8)(theta - sen theta), Sec. 4.1."""
    return (D ** 2 / 8) * (theta - math.sin(theta))  # literal-ok: Sec. 4.1


def perimetro(D: float, theta: float) -> float:
    """P = D*theta/2, Sec. 4.1."""
    return D * theta / 2


def tirante(D: float, theta: float) -> float:
    """
    y = (D/2)(1 - cos(theta/2)): identidad geometrica de la seccion circular,
    no un valor normativo -- se deriva de la propia definicion de theta como
    angulo mojado. La necesita `geometria()` para poblar `Geometria.y` y M4
    para el tirante critico (Sec. 4.2.1). Ya documentada en
    `modelos.Geometria.T`, que se apoya en la misma identidad.
    """
    return (D / 2) * (1 - math.cos(theta / 2))


def geometria(D: float, theta: float) -> Geometria:
    """Arma el `Geometria` completo (A, P, R, y) para un D y un theta dados."""
    A = area(D, theta)
    P = perimetro(D, theta)
    return Geometria(D=D, theta=theta, A=A, P=P, R=A / P, y=tirante(D, theta))


def _caudal_manning(D: float, theta: float, n: float, S: float) -> float:
    """Q = (1/n)*A*R^(2/3)*S^(1/2), Sec. 4.1."""
    A = area(D, theta)
    P = perimetro(D, theta)
    R = A / P
    return (1 / n) * A * R ** (2 / 3) * S ** (1 / 2)  # literal-ok: exponentes de Manning, Sec. 4.1


# ---------------------------------------------------------------------------
# Tirante normal (una rama, un n)
# ---------------------------------------------------------------------------

def tirante_normal(D: float, Q: float, S: float, n: float) -> Optional[Geometria]:
    """
    Resuelve el tirante normal de Manning (Sec. 4.1) para un D/Q/S/n dados,
    con Brent sobre theta en (0, 2*pi).

    Devuelve None cuando la busqueda de Brent no encuentra raiz con el signo
    esperado en los dos extremos del intervalo. No es un fallo del programa --
    es el resultado de diseño "este material y este diametro no alcanzan" -- y
    el orquestador de la Fase 4 lo lee como señal de pasar al siguiente
    diametro de la progresion de M2.

    EL CONTRATO, DICHO CON PRECISION (MAT-O18). El texto que ocupaba este
    lugar decia que None significa "no hay theta donde Manning iguale Q", y
    eso NO es exacto: la curva Q(theta) de una seccion circular no es
    monotona. Crece hasta un PICO en y/D = 0.93818 y despues BAJA hasta el
    caudal a seccion llena, que es menor. Para D = 0.90 m, S = 0.005 y
    n = 0.013 el pico vale 1.377 m3/s y el lleno 1.280 m3/s: en la banda
    (1.280, 1.377] SI existe un theta que transporta Q -- dos, de hecho --,
    y esta funcion devuelve None igual, porque `f(_THETA_MAX) < 0` y Brent no
    tiene un cambio de signo que morder en el intervalo completo.

    Se deja asi a proposito, y la direccion importa: devolver None de mas es
    CONSERVADOR -- manda a M2 al siguiente diametro --, mientras que resolver
    en esa banda daria un tirante por encima de y/D = 0.82 -- la RAIZ BAJA de
    las dos, que es la que Brent devolveria con un bracket sobre la rama
    creciente: 0.8203 en Q = 1.281, 0.8344 en Q = 1.30, 0.8806 en Q = 1.35 --,
    por encima del 0.75 que V1 admite (Sec. 4.1.1.3.7 b), de modo que el
    diseño se rechazaria igual una fase mas tarde. (El 0.94 es donde esta el
    PICO de la curva, no el tirante que se obtendria: decir "por encima de
    0.94" era confundir el maximo de Q con la raiz, y la conclusion se
    sostiene igual pero con el numero correcto.) Lo que no se puede es que el
    docstring afirme lo contrario de lo que el codigo hace: quien lea "no hay
    theta" concluira que el conducto no da, cuando lo que pasa es que da por
    encima del llenado admisible.
    """
    _validar_parametros(D, Q, S, n)

    def f(theta: float) -> float:
        return _caudal_manning(D, theta, n, S) - Q

    f_min, f_max = f(_THETA_MIN), f(_THETA_MAX)
    if f_min > 0 or f_max < 0:
        return None

    theta_solucion = brentq(f, _THETA_MIN, _THETA_MAX, xtol=TOL_BRENT)
    return geometria(D, theta_solucion)


# ---------------------------------------------------------------------------
# Resolucion completa con la regla de doble n
# ---------------------------------------------------------------------------

def resolver_manning(D: float, Q: float, S: float, material: Material) -> Optional[TiranteNormal]:
    """
    Resuelve el tirante normal (Sec. 4.1) aplicando la regla de doble n:

    1. Una unica resolucion de Brent con `material.n_para_capacidad` (n_max):
       fija el theta real de diseño -- el mas conservador del lado de la
       inundacion, el que alimenta V1 (borde libre).
    2. Sobre esa MISMA geometria (mismo R), las DOS velocidades del rango de
       n de la Tabla N 09:
         - con `material.n_para_velocidad_maxima` (n_min), la estimacion ALTA,
           conservadora contra los TECHOS (V3, Laushey);
         - con `material.n_para_velocidad_minima` (n_max), la estimacion BAJA,
           conservadora contra el PISO (V2, autolimpieza).

    Las dos salen de la misma expresion de Manning -- V = (1/n)*R^(2/3)*S^0.5,
    ec. (47) del num. 4.1.1.3.6 -- con la misma R y distinto n. Ninguna se
    obtiene dividiendo Q entre A: hacerlo devolveria siempre la segunda, y con
    ella un techo verificado del lado inseguro.

    Devuelve None si la resolucion de Brent con n_max no converge: el
    material no alcanza a transportar Q en flujo libre a esta D y S, y no
    hay geometria sobre la que evaluar las velocidades.
    """
    geom = tirante_normal(D, Q, S, material.n_para_capacidad)
    if geom is None:
        return None

    factor_geometrico = geom.R ** (2 / 3) * S ** (1 / 2)  # literal-ok: exponentes de Manning, ec. (47) del num. 4.1.1.3.6 / Sec. 4.1
    return TiranteNormal(
        geometria=geom,
        V_erosion=factor_geometrico / material.n_para_velocidad_maxima,
        V_sedimentacion=factor_geometrico / material.n_para_velocidad_minima,
    )
