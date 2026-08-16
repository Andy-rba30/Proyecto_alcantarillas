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
la inundacion. n MINIMO para velocidad y socavacion (V2, V3, Laushey):
conservador del lado de la erosion.

La UNICA resolucion de Brent usa n_max: es el n que, para el mismo Q y D,
exige mas area y por lo tanto fija el theta real de diseño (mas resistencia
-> mas tirante para el mismo caudal). La velocidad de la rama de erosion NO
sale de una segunda resolucion de Brent con un theta distinto: sale de
recalcular Manning con n_min SOBRE ESA MISMA geometria (mismo theta, mismo
R) -- el mismo canal visto con la rugosidad mas baja. Asi lo fija el fixture
CP-2 (tests/fixtures/casos_patron.py: D, y/D, S fijos, y las dos velocidades
V_con_n_max y V_con_n_min salen de la MISMA R con dos n distintos).

`resolver_manning()` aplica la regla completa: una resolucion de Brent con
`material.n_para_capacidad`, y sobre su geometria, V = (1/n_min)*R^(2/3)*S^0.5
con `material.n_para_velocidad`. Ver la advertencia ya documentada en
`modelos.TiranteNormal` (V*A != Q, por diseño).

`tirante_normal()`, la pieza mas chica, resuelve Manning para un solo n. Queda
publica porque M4 la reutiliza para lo que si necesita geometria de un n
suelto (p. ej. pruebas o un chequeo de capacidad a secas); el tirante critico
en si es una ecuacion distinta (Sec. 4.2.1) y vive en M4.

De donde sale el n de HDPE
----------------------------
M3 no lee `criterios_adoptados` en ningun punto: consume el `Material` que M2
ya resolvio (Sec. 3.4), incluidos `n_para_capacidad` y `n_para_velocidad`. Para
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
    V = resolucion.V
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

    Devuelve None si el conducto no puede transportar Q en flujo libre a esa
    pendiente y ese n: no hay theta en el intervalo donde Manning iguale Q
    (el conducto trabajaria a presion). No es un fallo del programa -- es el
    resultado de diseño "este material y este diametro no alcanzan" -- y el
    orquestador de la Fase 4 lo lee como señal de pasar al siguiente
    diametro de la progresion de M2.
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
    2. Sobre esa MISMA geometria (mismo R), la velocidad se recalcula con
       `material.n_para_velocidad` (n_min): el mismo canal con la rugosidad
       mas baja, conservador del lado de la erosion (V2, V3, Laushey).

    Devuelve None si la resolucion de Brent con n_max no converge: el
    material no alcanza a transportar Q en flujo libre a esta D y S, y no
    hay geometria sobre la que evaluar la segunda rama.
    """
    geom = tirante_normal(D, Q, S, material.n_para_capacidad)
    if geom is None:
        return None

    n_min = material.n_para_velocidad
    V = (1 / n_min) * geom.R ** (2 / 3) * S ** (1 / 2)  # literal-ok: exponentes de Manning, Sec. 4.1
    return TiranteNormal(geometria=geom, V=V)
