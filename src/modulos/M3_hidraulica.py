"""
M3_hidraulica.py
================
Fase 4.1 de la hoja de ruta: motor hidraulico. Geometria de la seccion
circular parcialmente llena y tirante normal por Manning, resuelto con
scipy.optimize.brentq sobre theta en (0, 2*pi).

Y la Sec. 1.3: TW en el cuerpo receptor
---------------------------------------
Desde S20 este modulo lleva ademas el procedimiento de tres pasos de Sec. 1.3
("TW se calcula, no se mide"): Manning en la seccion TRAPECIAL del receptor,
con su propio caudal de diseño, para obtener la cota de agua y de ahi el TW
que consume el control de salida. Vive aqui y no en un modulo nuevo por la
misma razon por la que `G_LAUSHEY` vive con las constantes normativas: es
Manning, y Manning se resuelve en un solo sitio. Dos solvers de Manning en el
mismo repositorio son dos formulas que pueden divergir.

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

import criterios_adoptados as ca
from modelos import (CIFRAS_FINA, CIFRAS_MAGNITUD, DatoInvalidoError,
                     Geometria, LimiteNumericoError, Magnitud, Material,
                     PuntoCritico, SeccionReceptor, TiranteNormal,
                     TWDeterminado, ViaDelTW, paso)
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


# ===========================================================================
# Sec. 1.3 - TW: se calcula, no se mide
# ===========================================================================
# LOS TRES PASOS DE LA HOJA DE RUTA, tal como los escribe (Sec. 1.3):
#
#   1. Obtener Q de diseño del receptor (ANA / Junta de Usuarios)     [N]
#   2. Manning en la seccion del receptor con ese Q y su pendiente ->
#      tirante normal -> cota de agua                                 [N]
#   3. Sin caudal documentado: dos escenarios acotados (salida libre /
#      receptor a seccion llena), cumplir en ambos                    [A]
#
# QUE HABIA ANTES DE S20 (SIS-B-04). Nada de esto. `Q_receptor_m3s` y
# `cota_TW` se cargaban del CSV, se validaban -- una contra cero, la otra
# contra el fondo del receptor -- y no las leia ningun modulo: viajaban a la
# tabla de datos de la memoria y ahi morian. La consecuencia, que la ficha
# midio con un CSV construido a proposito, era que un expediente con las dos
# columnas LLENAS seguia deteniendose en `CriterioPendienteError('TW_receptor')`
# y exigiendo `--tw`. El bloqueo era ruidoso y por eso nunca hubo un numero
# inventado; pero el procedimiento que la hoja de ruta escribe no existia.

CRITERIO_SECCION_RECEPTOR = "seccion_receptor"
CRITERIO_TW_RECEPTOR = "TW_receptor"

# Escenarios del paso 3, con el nombre que la hoja de ruta les da. Son
# rotulos, no valores de proyecto.
ESCENARIO_SALIDA_LIBRE = "salida libre (receptor vacio)"
ESCENARIO_SECCION_LLENA = "receptor a seccion llena"

# TW de la salida libre. NO es un valor de proyecto ni una adopcion: es la
# definicion del escenario -- "el receptor no aporta lamina de agua sobre el
# fondo de la salida" es TW = 0 por construccion, no un numero elegido. Se
# nombra para que el escenario se lea en la formula y no como un cero suelto.
TW_SALIDA_LIBRE = 0.0            # literal-ok: definicion del escenario, no un valor adoptado


# Cuantas veces se duplica el corchete antes de declarar que el caudal no
# cabe. 40 duplicaciones sobre una semilla de 1 m llegan a ~1e12 m: no es un
# limite de proyecto (no dice cuan hondo puede ser un dren), es el punto en
# que seguir buscando ya no distingue "muy hondo" de "imposible".
DUPLICACIONES_MAX_CORCHETE = 40   # literal-ok: tope de la busqueda, no un valor de proyecto


def area_trapecial(*, b: float, z: float, y: float) -> float:
    """A = (b + z*y)*y, seccion trapecial de solera b y talud z (H:V)."""
    return (b + z * y) * y


def perimetro_trapecial(*, b: float, z: float, y: float) -> float:
    """P = b + 2*y*sqrt(1 + z^2), seccion trapecial."""
    return b + 2 * y * math.sqrt(1 + z ** 2)   # literal-ok: los DOS taludes de un trapecio


def caudal_manning_trapecial(*, b: float, z: float, y: float,
                             n: float, S: float) -> float:
    """
    Q = (1/n)*A*R^(2/3)*S^(1/2) sobre la seccion trapecial (misma formula de
    Manning que la seccion circular; lo unico que cambia es la geometria).
    """
    A = area_trapecial(b=b, z=z, y=y)
    P = perimetro_trapecial(b=b, z=z, y=y)
    if not P > 0:
        raise DatoInvalidoError(
            "seccion_receptor", valor=(b, z),
            motivo="perimetro mojado nulo: una seccion con solera b = 0 y "
                   "talud z = 0 no es una seccion, es una linea")
    R = A / P
    return (1 / n) * A * R ** (2 / 3) * S ** (1 / 2)  # literal-ok: exponentes de Manning, Sec. 4.1


def tirante_normal_trapecial(*, Q: float, seccion: SeccionReceptor) -> float:
    """
    Tirante normal del receptor por Manning (paso 2 de Sec. 1.3), m.

    POR QUE ESTE SOLVER NO SE PARECE AL DE LA SECCION CIRCULAR. En un conducto
    circular Q(theta) NO es monotona -- tiene un pico en y/D = 0.938 y por eso
    `tirante_normal` tiene que devolver `None` en la banda (Q_lleno, Q_pico) --.
    En una seccion trapecial ABIERTA, en cambio, A y R crecen los dos con y sin
    limite, de modo que Q(y) es estrictamente creciente y la raiz es UNICA.
    Eso es lo que permite abrir el corchete por duplicacion en vez de tener
    que razonar sobre el pico: no hay pico.

    La busqueda no tiene techo normativo -- un dren puede ser tan hondo como
    sea --, de modo que el corchete se duplica hasta cubrir el Q pedido. Si el
    caudal es tan grande que ni con un tirante absurdo se alcanza, es un
    `LimiteNumericoError` y no un dato fuera de rango: cada dato cumple lo
    suyo y es la aritmetica la que no cierra (CLAUDE.md, quinta excepcion).
    """
    if not Q > 0:
        raise DatoInvalidoError(
            "Q_receptor_m3s", valor=Q,
            motivo="el caudal del receptor debe ser positivo para que "
                   "Manning tenga solucion real")
    if not seccion.n > 0 or not seccion.S > 0:
        raise DatoInvalidoError(
            CRITERIO_SECCION_RECEPTOR, valor=(seccion.n, seccion.S),
            motivo="la seccion del receptor declara n y S que tienen que ser "
                   "positivos: sin ellos Manning no tiene solucion real")

    def f(y: float) -> float:
        return caudal_manning_trapecial(b=seccion.b_m, z=seccion.z_HV, y=y,
                                        n=seccion.n, S=seccion.S) - Q

    # Corchete: y_lo justo por encima de cero (en y = 0 el area es nula y
    # f = -Q < 0, siempre) y y_hi duplicando hasta que f cambie de signo.
    y_lo = TOL_THETA_BORDE
    y_hi = max(seccion.altura_total_m, seccion.b_m, 1.0)   # literal-ok: semilla del corchete, no un valor de proyecto
    for _ in range(DUPLICACIONES_MAX_CORCHETE):
        if f(y_hi) > 0:
            return brentq(f, y_lo, y_hi, xtol=TOL_BRENT)
        y_hi *= 2                                          # literal-ok: duplicacion del corchete
    raise LimiteNumericoError(
        "tirante_normal_receptor", valor=Q,
        motivo=f"el caudal del receptor ({Q} m3/s) no se alcanza en la "
               f"seccion declarada ni con un tirante de {y_hi:g} m. Los datos "
               "por separado son admisibles -- Q positivo, n y S positivos, "
               "seccion con area -- y lo que no cierra es la combinacion: una "
               "solera de "
               f"{seccion.b_m} m con talud {seccion.z_HV} H:V, n = "
               f"{seccion.n} y S = {seccion.S} m/m no transporta ese caudal "
               "en ninguna profundidad con sentido fisico")


def _seccion_declarada() -> SeccionReceptor:
    """
    La seccion del receptor, del criterio 'seccion_receptor' [A].

    `CriterioPendienteError` mientras siga vacia, que es lo correcto: la
    seccion de una obra de terceros no se aproxima.
    """
    d = ca.valor(CRITERIO_SECCION_RECEPTOR)   # CriterioPendienteError si falta
    if not isinstance(d, dict):
        raise DatoInvalidoError(
            CRITERIO_SECCION_RECEPTOR, valor=d,
            motivo="se declara como un dict con los cinco campos de la "
                   "seccion: {'b_m': ..., 'z_HV': ..., 'S': ..., 'n': ..., "
                   "'altura_total_m': ...}")
    faltan = [c for c in ("b_m", "z_HV", "S", "n", "altura_total_m")
              if c not in d]
    if faltan:
        raise DatoInvalidoError(
            CRITERIO_SECCION_RECEPTOR, valor=sorted(d),
            motivo=f"le faltan los campos {faltan}: sin ellos no hay "
                   "geometria con que correr Manning en el receptor "
                   "(Sec. 1.3, paso 2)")
    return SeccionReceptor(b_m=d["b_m"], z_HV=d["z_HV"], S=d["S"], n=d["n"],
                           altura_total_m=d["altura_total_m"])


def _paso_tw(*, punto: PuntoCritico, cota_fondo_salida: float,
             tw: float, cota_agua: Optional[float], via: ViaDelTW,
             sustitucion, escenarios=()):
    """El `PasoDeMemoria` del TW, comun a las cuatro vias de Sec. 1.3."""
    nota = (
        "TW ES UN TIRANTE, NO UNA COTA, y las dos cosas conviven en este "
        "expediente: `cota_TW` es una elevacion en msnm y TW es la altura de "
        "agua SOBRE EL FONDO DE LA SALIDA del conducto. Las separa "
        "exactamente esa cota: cota_TW = cota_fondo_salida + TW. Confundirlas "
        "desplaza el control de salida en la magnitud entera de la cota."
    )
    if escenarios:
        nota += (
            " ESCENARIOS DEL PASO 3: se calculan los dos que la hoja de ruta "
            "nombra y el diseño corre con el GOBERNANTE, que es el mayor. "
            "Cumplir con el mayor implica cumplir con el otro, y no es una "
            "conveniencia: h_o = max(TW, (y_c + D)/2) es no decreciente en "
            "TW, HW_salida = H + h_o - S*L es creciente en h_o, y el control "
            "que gobierna es max(HW_entrada, HW_salida); luego todas las "
            "verificaciones que dependen del TW (V4 y V4b) son monotonas y su "
            "peor caso es el TW mayor. Los dos numeros se imprimen igual, "
            "para que el revisor lo compruebe en vez de creerlo."
        )
    return paso(
        "F1.TW",
        codigo="1.3",
        que="TW en el cuerpo receptor durante la avenida",
        formula="TW = cota_TW - cota_fondo_salida",
        formula_cita_id="MC_HHD.4.1.1.3.6",
        citas_textuales=("MC_HHD.4.1.1.3.6",),
        sustitucion=tuple(sustitucion),
        resultado=Magnitud("TW", tw, "m",
                           f"tirante en el receptor sobre el fondo de la "
                           f"salida; via: {via.value}",
                           cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=nota,
    )


def tw_seccion_1_3(*, punto: PuntoCritico,
                   cota_fondo_salida: Optional[float],
                   tw_declarado: Optional[float] = None) -> TWDeterminado:
    """
    El TW del punto por el procedimiento de Sec. 1.3, con la via por la que
    salio (SIS-B-04).

    CUATRO VIAS, EN ORDEN DE PRECEDENCIA -- de lo mas determinado a lo mas
    supuesto --, y cada una queda escrita en `TWDeterminado.via`:

    1. `tw_declarado` (`--tw` / `TW_m`). El proyectista lo pone a mano y manda
       sobre todo lo demas: un dato entregado no se recalcula.
    2. Columna `cota_TW` del CSV. Tablero 3.1 la rotula «Calculada (1.3)»: ES
       el paso 2 resuelto fuera, y lo que falta aqui es la resta que lo
       convierte en tirante. Era exactamente lo que SIS-B-04 media -- «un CSV
       con `cota_TW` llena sigue exigiendo --tw» --, y el arreglo no es una
       conversion suelta: es que esta funcion existe.
    3. Columna `Q_receptor_m3s` + criterio 'seccion_receptor': pasos 1 y 2
       enteros, Manning en el receptor.
    4. Sin caudal documentado: paso 3, los DOS escenarios acotados que la hoja
       de ruta nombra -- salida libre y receptor a seccion llena --, con el
       gobernante para el diseño y los dos impresos.

    Si ninguna de las cuatro se puede recorrer, se cae al criterio
    'TW_receptor', que es donde el proyecto estuvo hasta S20 y sigue siendo la
    ultima puerta: `CriterioPendienteError`, nunca un relleno.

    POR QUE EL PASO 3 NECESITA LA SECCION IGUAL. «Receptor a seccion llena» es
    un nivel, y para conocerlo hay que saber hasta donde llega el bordo:
    `SeccionReceptor.altura_total_m`. Sin ese numero el segundo escenario no
    se puede escribir, y un escenario que no se puede escribir no acota nada.
    La salida libre, en cambio, es TW = 0 por definicion del escenario, sin
    dato ninguno.

    EL SIGNO DE LA RESTA, que es donde esta el error facil: si la cota de agua
    del receptor queda POR DEBAJO del fondo de la salida, TW no es negativo:
    es salida libre, TW = 0. Un TW negativo no significa nada fisico -- el
    conducto no puede tener menos que nada de agua encima -- y dejarlo pasar
    daria un h_o menor que el de la salida libre, que es imposible.
    """
    # --- Via 1: declarado por el proyectista
    #
    # `cota_fondo_salida` puede llegar None por esta via, y solo por esta: un
    # TW declarado no se obtiene restando cotas, de modo que quien llama no
    # tiene por que haberla podido calcular. La cota absoluta se compone si se
    # conoce y se omite si no; el TIRANTE, que es lo que consume el control de
    # salida, esta completo en los dos casos.
    if tw_declarado is not None:
        return TWDeterminado(
            valor=tw_declarado, via=ViaDelTW.DECLARADO,
            cota_TW_msnm=(None if cota_fondo_salida is None
                          else cota_fondo_salida + tw_declarado),
            paso=_paso_tw(
                punto=punto, cota_fondo_salida=cota_fondo_salida,
                tw=tw_declarado, cota_agua=None, via=ViaDelTW.DECLARADO,
                sustitucion=(
                    Magnitud("TW", tw_declarado, "m",
                             "declarado por el proyectista (--tw o TW_m de "
                             "--datos-externos): manda sobre el calculo",
                             cifras=CIFRAS_MAGNITUD),)))

    # --- Via 2: la columna `cota_TW`, que ES el paso 2 resuelto fuera
    if punto.cota_TW is not None:
        tw = _tw_desde_cota(punto.cota_TW, cota_fondo_salida)
        return TWDeterminado(
            valor=tw, via=ViaDelTW.COTA_TW, cota_TW_msnm=punto.cota_TW,
            paso=_paso_tw(
                punto=punto, cota_fondo_salida=cota_fondo_salida, tw=tw,
                cota_agua=punto.cota_TW, via=ViaDelTW.COTA_TW,
                sustitucion=(
                    Magnitud("cota_TW", punto.cota_TW, "msnm",
                             "columna del CSV (Sec. 1.2). Tablero 3.1 la "
                             "rotula «Calculada (1.3)»: es el paso 2 "
                             "resuelto fuera de este script",
                             cifras=CIFRAS_MAGNITUD),
                    Magnitud("cota_fondo_salida", cota_fondo_salida, "msnm",
                             "M7 (7.B): cota de entrada - S*L",
                             cifras=CIFRAS_MAGNITUD))))

    # --- Via 3: el caudal del receptor + su seccion (pasos 1 y 2)
    if punto.Q_receptor_m3s is not None:
        seccion = _seccion_declarada()
        y_n = tirante_normal_trapecial(Q=punto.Q_receptor_m3s, seccion=seccion)
        cota_agua = punto.cota_fondo_receptor + y_n
        tw = _tw_desde_cota(cota_agua, cota_fondo_salida)
        return TWDeterminado(
            valor=tw, via=ViaDelTW.MANNING_RECEPTOR, cota_TW_msnm=cota_agua,
            paso=_paso_tw(
                punto=punto, cota_fondo_salida=cota_fondo_salida, tw=tw,
                cota_agua=cota_agua, via=ViaDelTW.MANNING_RECEPTOR,
                sustitucion=(
                    Magnitud("Q_receptor", punto.Q_receptor_m3s, "m3/s",
                             "columna del CSV (Sec. 1.2), paso 1: caudal de "
                             "diseño del receptor (ANA / Junta de Usuarios)",
                             cifras=CIFRAS_MAGNITUD),
                    Magnitud("b", seccion.b_m, "m",
                             "solera de la seccion del receptor, criterio "
                             "'seccion_receptor' [A]", cifras=CIFRAS_MAGNITUD),
                    Magnitud("z", seccion.z_HV, "H:V",
                             "talud de la seccion del receptor, criterio "
                             "'seccion_receptor' [A]", cifras=CIFRAS_MAGNITUD),
                    Magnitud("n_receptor", seccion.n, "",
                             "Manning del receptor -- NO el del conducto --, "
                             "criterio 'seccion_receptor' [A]",
                             cifras=CIFRAS_FINA),
                    Magnitud("S_receptor", seccion.S, "m/m",
                             "pendiente del receptor, criterio "
                             "'seccion_receptor' [A]", cifras=CIFRAS_FINA),
                    Magnitud("y_n", y_n, "m",
                             "tirante normal en el receptor, paso 2: Manning "
                             "sobre la seccion trapecial",
                             cifras=CIFRAS_MAGNITUD),
                    Magnitud("cota_fondo_receptor", punto.cota_fondo_receptor,
                             "msnm", "columna del CSV (Sec. 1.2)",
                             cifras=CIFRAS_MAGNITUD),
                    Magnitud("cota_fondo_salida", cota_fondo_salida, "msnm",
                             "M7 (7.B): cota de entrada - S*L",
                             cifras=CIFRAS_MAGNITUD))))

    # --- Via 4: paso 3, los dos escenarios acotados
    seccion = _seccion_declarada()
    cota_llena = punto.cota_fondo_receptor + seccion.altura_total_m
    tw_llena = _tw_desde_cota(cota_llena, cota_fondo_salida)
    escenarios = ((ESCENARIO_SALIDA_LIBRE, TW_SALIDA_LIBRE),
                  (ESCENARIO_SECCION_LLENA, tw_llena))
    gobernante = max(tw for _rotulo, tw in escenarios)
    return TWDeterminado(
        valor=gobernante, via=ViaDelTW.ESCENARIOS_ACOTADOS,
        cota_TW_msnm=cota_fondo_salida + gobernante,
        escenarios=escenarios,
        paso=_paso_tw(
            punto=punto, cota_fondo_salida=cota_fondo_salida, tw=gobernante,
            cota_agua=cota_fondo_salida + gobernante,
            via=ViaDelTW.ESCENARIOS_ACOTADOS, escenarios=escenarios,
            sustitucion=(
                Magnitud("TW (salida libre)", TW_SALIDA_LIBRE, "m",
                         "primer escenario del paso 3: el receptor no aporta "
                         "lamina sobre el fondo de la salida. Es la "
                         "definicion del escenario, no un valor adoptado",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("altura_total", seccion.altura_total_m, "m",
                         "profundidad de la seccion del receptor, criterio "
                         "'seccion_receptor' [A]: es lo que acota el segundo "
                         "escenario", cifras=CIFRAS_MAGNITUD),
                Magnitud("TW (seccion llena)", tw_llena, "m",
                         "segundo escenario del paso 3: el receptor corre a "
                         "seccion llena y su agua llega a la corona del bordo",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("cota_fondo_salida", cota_fondo_salida, "msnm",
                         "M7 (7.B): cota de entrada - S*L",
                         cifras=CIFRAS_MAGNITUD))))


def _tw_desde_cota(cota_agua: float, cota_fondo_salida: float) -> float:
    """
    TW = cota_agua - cota_fondo_salida, acotado por abajo en la salida libre.

    Ver el docstring de `tw_seccion_1_3` sobre el signo: una cota de agua por
    debajo del fondo de la salida es salida libre, no un TW negativo.
    """
    return max(TW_SALIDA_LIBRE, cota_agua - cota_fondo_salida)

