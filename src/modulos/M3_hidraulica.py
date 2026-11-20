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
conservador del lado de la erosion. Cada extremo con SU tirante normal (VE-2,
ver abajo).

LA DOBLE N ES ADOPCION [A], NO NORMA. El Manual de Hidrologia, num.
4.1.1.3.6, pag. impresa 74, solo dice
«n : Coeficiente de Manning (Ver Tabla Nº 09)», y la Tabla Nº 09 (pag.
impresa 75) da las columnas MINIMO, NORMAL y MAXIMO sin decir cual se usa.
Los valores de la tabla son [N]; que columna rige cada verificacion es
ADOPCION del proyecto: para el tubo de concreto, el criterio [A]
'columna_n_manning_concreto' (VE-2, ficha VE2-A), que este modulo recibe ya
resuelto en `Material.n_min` / `n_max`. La hoja de ruta (Sec. 4.1) la dice
asi desde su correccion del 2026-11-18; hasta entonces la rotulaba «Regla
[N]», y la discrepancia se declaraba aqui (ficha VE1-01, D3, cerrada).

CADA EXTREMO RESUELVE SU PROPIO TIRANTE (VE-2, decision (b) de VE1-02)
-------------------------------------------------------------------------
Dos resoluciones de Brent sobre la misma ecuacion, una por extremo del
rango: con n_max el tirante de CAPACIDAD (el theta de diseño, el que juzga
V1), y con n_min el tirante de EROSION, mas bajo. Cada velocidad es la de su
propio tirante, y por eso cada una cumple la continuidad Q = V*A con SU area.

Hasta VE-2 habia UNA sola resolucion, con n_max, y la velocidad alta se
recalculaba con n_min SOBRE ESA MISMA geometria (mismo theta, mismo R): la
velocidad de una rugosidad sobre el tirante de otra, con V*A = Q*n_max/n_min
(1.3*Q en el concreto). Lo fijaba el fixture CP-2 y lo documentaba
`modelos.TiranteNormal` como «V_erosion*A != Q, por diseño». La revision de
la ficha VE1-02 contra los PDF no encontro ninguna fuente que tome el tirante
de un n y la velocidad de otro: el HDS-5 (hif12026, num. 3.3.2, pag. impresa
3.24, `HDS5_3ED.3.3.2#V_SALIDA_ENTRADA`) dice «determine the normal depth and
velocity in the culvert barrel.  The velocity at normal depth is assumed to
be the outlet velocity», y HEC-14 (num. 3.2.2, pag. impresa 3-7,
`HEC14.3.2.2#V_SALIDA_NORMAL`) calcula la velocidad de salida con Manning a
tirante normal; su ejemplo de la pag. 3-8 resuelve un tirante por cada n y
toma Vo = Q/A de cada uno. El dueño aprobo la correccion el 2026-11-17.

DOS VELOCIDADES, NO UNA (MAT-D1)
---------------------------------
Un umbral de velocidad no tiene un extremo conservador: tiene dos, y son
opuestos. Contra un TECHO (V3, Laushey) lo conservador es suponer la
velocidad mas ALTA que el rango de n admite, o sea calcularla con n_min.
Contra un PISO (V2, autolimpieza) lo conservador es exactamente lo contrario:
suponer la mas BAJA, que sale de n_max.

`resolver_manning()` devuelve las dos:

    V_erosion       = Q / A(y_n con n_min)                estimacion ALTA  -> V3, d50
    V_sedimentacion = (1/n_max)*R(n_max)^(2/3)*S^0.5      estimacion BAJA  -> V2

(la segunda es Q / A(y_n con n_max), la misma cuenta escrita como Manning).
Hasta MAT-D1 devolvia solo la primera, bajo el nombre `V`, y V2 la
consumia: un piso verificado con la estimacion alta. La Sec. 4.1 de la hoja
de ruta asigna n minimo a "velocidad maxima y socavacion" -- V2 no esta en
esa lista -- y el fixture CP-3 modela el umbral de V2 con n = 0.013, que es
n_max: el repositorio se contradecia a si mismo.

`V_sedimentacion` es ademas el minimo REAL de la velocidad sobre todo el rango
de n de la Tabla N 09: con un n menor el tirante normal baja, el area baja y
la velocidad media Q/A sube -- mientras theta este en la rama creciente de
la curva de capacidad, que es donde V1 mantiene el diseño (y/D <= 0.75); ver
`modelos.TiranteNormal`, que enuncia la condicion. Y `V_erosion`, por la
misma cadena, es el maximo real: la de n_min con su tirante.

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
                        el problema: D, Q y n tienen que ser positivos, y S
                        no puede ser NEGATIVA. No es el caso "sin solucion":
                        ese es un None, no una excepcion. Y desde T-2 tampoco
                        lo es S = 0 (barril horizontal), que hasta entonces
                        se rechazaba aqui (INF-5.1.6): `resolver_manning`
                        devuelve `SinTiranteNormal` y M4 sigue.

Uso
---
    from src.modulos.M3_hidraulica import resolver_manning, tirante_normal, geometria

    resolucion = resolver_manning(D=0.90, Q=1.1673, S=0.005, material=concreto)
    if resolucion is None:
        ...  # pasar al siguiente diametro
    y_normal = resolucion.geometria.y
    V_techo = resolucion.V_erosion        # contra V3 y el d50 de Laushey
    V_piso = resolucion.V_sedimentacion   # contra V2
"""

from __future__ import annotations

import math
from typing import Optional, Tuple, Union

# EL RESOLUTOR SE IMPORTA EN EL PUNTO DE USO (EXT-8, PC-10): `scipy.optimize`
# costaba 230-310 ms en CADA `import cli`, tambien en una corrida que no
# llega a resolver nada (--criterios, la ayuda, la GUI al abrirse). Es el
# mismo `brentq` de siempre --- la referencia del docstring de modulo sigue
# valiendo --- traido la primera vez que hace falta; el segundo import es una
# busqueda en `sys.modules`.

from src import criterios_adoptados as ca
from src.constantes_fisicas import G
from src.constantes_normativas import (HEC14_RESALTO_PENDIENTE_HORIZONTAL_MAX,
                                       K_MANNING_SI)
from src.modelos import (CIFRAS_FINA, CIFRAS_MAGNITUD, DatoInvalidoError,
                     MOTIVO_METODO_NO_EVALUABLE_HEC14, MetodoNoEvaluableError,
                     ResaltoHidraulico,
                     Seccion, SeccionCircular,
                     Geometria, LimiteNumericoError, Magnitud, Material,
                     PuntoCritico, RAMA_REMANSO_M1, RAMA_REMANSO_NINGUNA,
                     RAMA_REMANSO_S1, RemansoAguasArriba,
                     SECCION_RECEPTOR_ADOPTADA,
                     SECCION_RECEPTOR_MEDIDA, SeccionReceptor,
                     SinTiranteNormal, TiranteNormal,
                     TWDeterminado, ViaDelTW, paso)
from src.tolerancias import (PASOS_PERFIL_REMANSO, PUNTOS_MOMENTO_SECCION,
                             TOL_BRENT, TOL_UMBRAL_NORMATIVO,
                              TOL_THETA_BORDE)

NUMERAL_MANNING = "4.1"

# EL BRACKET DE THETA SE FUE A `SeccionCircular.bracket_llenado()` en C1:
# es la seccion la que sabe sobre que parametro se la recorre. M3 lo pide
# y no lo construye.


# ---------------------------------------------------------------------------
# Validacion de entrada
# ---------------------------------------------------------------------------

def _validar_parametros(seccion: Seccion, Q: float, S: float, n: float) -> None:
    # QUIEN NOMBRA EL DATO ES LA SECCION, Y ESA ES LA RESPUESTA DE C4 A LA
    # ANOTACION A-4 DE §16.4. C1 llego a renombrar el `campo` a "altura" y lo
    # devolvio a "D", porque de esta excepcion se imprimen LAS DOS CADENAS --
    # `campo` y `motivo` viajan juntos dentro de `str(exc)`, que `servicio._bloqueo`
    # guarda como `mensaje`, `cli._bloqueo_json` publica y `M11._tabla_bloqueos`
    # pinta -- y renombrar movia salida. La anotacion quedaba para C4 "que es
    # la primera sesion en que 'D' es falso -- una SeccionRectangular no tiene
    # diametro -- y la unica que puede elegir el nombre viendo las dos formas
    # a la vez".
    #
    # Vistas las dos: "D" NO ERA FALSO AQUI. Un tubo tiene diametro y el dato
    # que un revisor corregiria se llama asi. Lo falso era SUPONER QUE HAY UN
    # SOLO NOMBRE. El nombre del dato es una propiedad de la forma, y por eso
    # la validacion entera --campo y motivo-- se le pide a la seccion:
    # `SeccionCircular` sigue diciendo "D" y "el diametro debe ser positivo",
    # letra por letra, de modo que la rama de error de la linea base no se
    # mueve; `SeccionRectangular` dice "B" y "H" con sus propios motivos.
    #
    # Y ADEMAS RETIRA UNA COPIA: la misma pareja de cadenas estaba escrita dos
    # veces, aqui y en `M4._validar_Q_D`. Eran dos sitios que habia que editar
    # juntos para siempre, que es el defecto que este repositorio persigue en
    # todas partes.
    seccion.exigir_dimensiones_positivas()
    # Forma MAT-D13 (PC-05): condicion EN POSITIVO Y NEGADA. `if Q <= 0` era
    # permeable a NaN -- falso frente a `<=` igual que frente a `>` -- y el
    # NaN seguia hasta brentq, que lo devolvia como ValueError: un fallo de
    # programa donde hay un dato del expediente que no puede ser.
    if not Q > 0:
        raise DatoInvalidoError("Q", valor=Q, motivo="el caudal debe ser positivo")
    # --- T-2 --- (INF-5.1.6) LA GUARDIA ES SOLO CONTRA S < 0. Hasta T-2 era
    # `not S > 0` y rechazaba el barril HORIZONTAL como dato invalido; el
    # HDS-5 lo admite (num. 3.3.4, pag. impresa 3.25: «can be reasonably
    # applied to culverts with no slope (horizontal)»), de modo que S = 0 es
    # un dato valido que Manning no puede resolver, no un dato que no puede
    # ser. La pendiente ADVERSA si se sigue rechazando: la fuente la trata
    # como un asentamiento, no como un diseño. Forma MAT-D13: condicion en
    # positivo y negada, para que un NaN tampoco pase.
    if not S >= 0:
        raise DatoInvalidoError("S", valor=S, motivo="la pendiente no puede ser "
                                "negativa: S = 0 es un barril horizontal, que "
                                "se admite; una pendiente adversa no")
    if not n > 0:
        raise DatoInvalidoError("n", valor=n, motivo="el coeficiente de Manning debe ser positivo")


# ---------------------------------------------------------------------------
# Geometria de la seccion circular parcialmente llena (Sec. 4.1)
# ---------------------------------------------------------------------------

# LA FORMA YA NO VIVE AQUI. Las formulas de area, perimetro y tirante se
# mudaron a `modelos.SeccionCircular` en C1a: M3 pide la geometria y no sabe
# de que forma es. Las tres siguen existiendo porque nombran, en el lenguaje
# de la Sec. 4.1, lo que la seccion devuelve junto.
#
# QUIEN LAS LLAMA, MEDIDO Y NO SUPUESTO. La primera redaccion de este
# comentario decia "son la API publica que la suite contrasta contra
# `geometria()`", y eso es cierto de DOS de las tres:
# `test_M3_hidraulica.test_area_y_perimetro_funciones_sueltas_coinciden_con_geometria`
# contrasta `area` y `perimetro`. `tirante` NO LO LLAMA NADIE, ni produccion
# ni la suite: lo llamaba `M3.geometria` antes de C1, y desde que `geometria`
# delega se quedo sin consumidor. Predecirle uno que no existe es el
# antipatron que este repositorio ya tiene fichado; su ficha esta en
# `docs/decisiones_diferidas.md`.
#
# Y OJO CON EL CASO DEGENERADO, QUE C1 MOVIO. Las tres pasan ahora por
# `geometria_en()`, que construye la `Geometria` entera y con ella el
# `R = A/P`. En `llenado = 0` el perimetro vale 0 y sale ZeroDivisionError,
# donde antes `area(D, 0.0)` devolvia 0.0. No es alcanzable desde produccion
# -- el bracket arranca en TOL_THETA_BORDE, nunca en 0, y `geometria()` ya
# dividia igual antes de C1 --, pero es un modo de fallo nuevo de estas tres,
# y ZeroDivisionError no desciende de ErrorProyecto. Queda ANOTADO en §16.4 y
# no corregido: evitarlo pide tres miembros nuevos en el protocolo `Seccion`,
# y reestructurar el protocolo al cierre de la sesion de mayor riesgo del
# plan arriesga mas de lo que arregla.
#
# `llenado` es el PARAMETRO PROPIO de la seccion, opaco para M3: en la
# circular es el angulo mojado theta y en una rectangular seria el tirante.
# Que sea opaco es justamente lo que permite que Brent lo recorra sin que este
# modulo sepa sobre que esta resolviendo.

def area(seccion: Seccion, llenado: float) -> float:
    """A de la seccion al llenado dado, Sec. 4.1."""
    return seccion.geometria_en(llenado).A


def perimetro(seccion: Seccion, llenado: float) -> float:
    """P mojado de la seccion al llenado dado, Sec. 4.1."""
    return seccion.geometria_en(llenado).P


def tirante(seccion: Seccion, llenado: float) -> float:
    """Tirante de la seccion al llenado dado, Sec. 4.1."""
    return seccion.geometria_en(llenado).y


def geometria(seccion: Seccion, llenado: float) -> Geometria:
    """Arma el `Geometria` completo (A, P, R, y) para un llenado dado."""
    return seccion.geometria_en(llenado)


def _caudal_manning(seccion: Seccion, llenado: float, n: float, S: float) -> float:
    """
    Q = (K_MANNING_SI/n)*A*R^(2/3)*S^(1/2), Sec. 4.1 (num. 4.1.1.3.6).

    `K_MANNING_SI` es el coeficiente de unidades de Manning, 1.0 m^(1/3)/s en
    SI (1.486 ft^(1/3)/s en el sistema ingles, que NO se usa): la formula no
    es homogenea y es el quien cierra la dimension L^(1/3)/T que separa a Q
    de A*R^(2/3)*S^(1/2). Hasta PD estaba implicito en el (1/n); declararlo
    no mueve ningun numero, porque multiplicar por 1.0 es la identidad.
    """
    g = seccion.geometria_en(llenado)
    return (K_MANNING_SI / n) * g.A * g.R ** (2 / 3) * S ** (1 / 2)  # literal-ok: exponentes de Manning, Sec. 4.1


# ---------------------------------------------------------------------------
# Tirante normal (una rama, un n)
# ---------------------------------------------------------------------------

def tirante_normal(seccion: Seccion, Q: float, S: float, n: float) -> Optional[Geometria]:
    """
    Resuelve el tirante normal de Manning (Sec. 4.1) para un D/Q/S/n dados,
    con Brent sobre theta en (0, 2*pi).

    Devuelve None cuando Q alcanza o supera el caudal a seccion llena, o
    cuando la busqueda de Brent no encuentra raiz con el signo esperado en
    los dos extremos del intervalo. No es un fallo del programa -- es el
    resultado de diseño "este material y este diametro no alcanzan en lamina
    libre" -- y el orquestador de la Fase 4 lo lee como señal de pasar al
    siguiente escalon de la progresion de M2.

    EL CONTRATO, DICHO CON PRECISION (MAT-O18). El texto que ocupaba este
    lugar decia que None significa "no hay theta donde Manning iguale Q", y
    eso NO es exacto: la curva Q(theta) de una seccion circular no es
    monotona. Crece hasta un PICO en y/D = 0.93818 y despues BAJA hasta el
    caudal a seccion llena, que es menor. Para D = 0.90 m, S = 0.005 y
    n = 0.013 el pico vale 1.377 m3/s y el lleno 1.280 m3/s: en la banda
    (1.280, 1.377] SI existe un theta que transporta Q -- dos, de hecho --,
    y esta funcion devuelve None igual, porque `f` en el extremo superior del
    bracket de la seccion es < 0 y Brent no
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

    Y EL TECHO ES EL CAUDAL A SECCION LLENA, EN LAS DOS FORMAS (PC-06). En la
    circular el bracket ya lo ponia solo: Q(theta_max) ES el caudal a seccion
    llena, porque en theta = 2*pi el perimetro mojado es el perimetro entero.
    En el marco NO: el bracket es (0, H) y en y = H el perimetro de lamina
    libre es B + 2H, no 2B + 2H, de modo que Q_manning(H) SUPERA al caudal a
    seccion llena -- para 2.00 x 1.50, n = 0.014 y S = 0.004: 9.64 frente a
    7.70 m3/s -- y en la banda (7.70, 9.64) Brent encontraba una raiz y esta
    funcion publicaba un «tirante normal» (y/H = 0.86 con Q = 8.0) por encima
    del caudal que el conducto lleva a seccion llena. La solucion uniforme
    con y < H existe en esa banda -- es el mismo fenomeno Q_pico > Q_lleno
    que MAT-O18 documenta arriba para la circular --, de modo que lo que se
    fija no es que el flujo «sea imposible» sino la CONVENCION que la
    circular ya tenia por su bracket: la capacidad en lamina libre se acota
    en Q_lleno, y por encima el escalon no alcanza. V1 rechazaba esos
    tirantes de todos modos (y/H > 0.75), asi que ningun diseño aceptado se
    mueve: se mueven el motivo y la traza, que publicaban un regimen que el
    proyecto no admite. Por eso la guardia compara Q con
    Q_lleno = (k_n/n) * A_llena * R_lleno^(2/3) * S^(1/2) ANTES del bracket,
    con el radio hidraulico de la seccion llena que aporta la seccion; y lo
    hace en las dos formas, porque en la circular no cambia nada (el techo
    coincide con el que el bracket ya ponia, salvo el borde exacto) y una
    guardia que bifurcara por forma seria la forma cableada en M3 que C1
    retiro. Escrita en positivo y negada (MAT-D13): `not Q < Q_lleno`.
    """
    _validar_parametros(seccion, Q, S, n)
    # --- T-2 --- Con S = 0 el caudal a seccion llena vale 0 y la guardia de
    # abajo devuelve None para todo Q > 0: «ningun tirante transporta Q en
    # flujo uniforme», que con un barril horizontal es literalmente cierto.
    # Quien distingue ese None del de «el escalon no alcanza» es
    # `resolver_manning`, que para S = 0 no llega a llamar aqui.
    Q_lleno = (K_MANNING_SI / n) * seccion.area_llena \
        * seccion.radio_hidraulico_lleno ** (2 / 3) * S ** (1 / 2)  # literal-ok: exponentes de Manning, Sec. 4.1
    if not Q < Q_lleno:
        return None
    llenado_min, llenado_max = seccion.bracket_llenado()

    def f(llenado: float) -> float:
        return _caudal_manning(seccion, llenado, n, S) - Q

    f_min, f_max = f(llenado_min), f(llenado_max)
    if f_min > 0 or f_max < 0:
        return None

    from scipy.optimize import brentq   # perezoso: ver la nota junto a los imports
    llenado_solucion = brentq(f, llenado_min, llenado_max, xtol=TOL_BRENT)
    return geometria(seccion, llenado_solucion)


# ---------------------------------------------------------------------------
# Resolucion completa con la regla de doble n
# ---------------------------------------------------------------------------

def resolver_manning(seccion: Seccion, Q: float, S: float, material: Material
                     ) -> Union[TiranteNormal, SinTiranteNormal, None]:
    """
    Resuelve el tirante normal (Sec. 4.1) con los DOS extremos del rango de n
    de la Tabla N 09, cada uno con SU tirante (VE-2, decision (b)):

    1. Brent con `material.n_para_capacidad` (n_max): el tirante de
       CAPACIDAD, el mas conservador del lado de la inundacion, el que
       alimenta V1 (borde libre). Sobre el, con el mismo n,
       `V_sedimentacion` = (K_MANNING_SI/n_max)*R^(2/3)*S^0.5 (ec. (47) del
       num. 4.1.1.3.6), la estimacion BAJA, conservadora contra el PISO (V2,
       autolimpieza); cumple V*A = Q porque es la velocidad media del mismo
       n con que se resolvio el tirante.
    2. Brent con `material.n_para_velocidad_maxima` (n_min), SOBRE LA MISMA
       ECUACION: el tirante normal de esa rugosidad, mas bajo, y
       `V_erosion` = Q / A(y_n con n_min), la estimacion ALTA, conservadora
       contra los TECHOS (V3, Laushey). Es tambien la ec. (47) evaluada sobre
       su propio tirante: Q/A y Manning coinciden alli hasta la convergencia
       de Brent (`tolerancias.TOL_REL_CONTINUIDAD_MANNING`).

    POR QUE DOS RESOLUCIONES Y NO UNA (VE-2). Hasta VE-2 habia una sola, con
    n_max, y la velocidad alta se calculaba con n_min SOBRE ESA geometria: la
    velocidad de una rugosidad sobre el tirante de otra, con V*A = Q*n_max/
    n_min (1.3*Q en el concreto), un caudal que no pasa por el conducto.
    Ninguna fuente lo hace asi: el HDS-5 (num. 3.3.2, pag. impresa 3.24)
    manda «determine the normal depth and velocity in the culvert barrel», y
    HEC-14 (num. 3.2.2, pag. impresa 3-7) calcula la velocidad de salida con
    Manning a tirante normal, y su ejemplo de la pag. 3-8 resuelve un tirante
    por cada n. En UPAO ALC46 (Q = 0.317 m3/s, S = 0.10) la formula vieja daba
    6.28 m/s a Ø 0.90 m, sobre el techo de 6.0 del concreto, y esta da 5.81.

    Devuelve None si la resolucion de Brent con n_max no converge: el
    material no alcanza a transportar Q en flujo libre a esta D y S, y no
    hay geometria sobre la que evaluar las velocidades. La de n_min recibe el
    MISMO trato: None, nunca un sustituto.

    Y `SinTiranteNormal` SI EL BARRIL ES HORIZONTAL, S = 0 (T-2, INF-5.1.6):
    no hay tirante normal para ningun caudal ni seccion, y eso no es «este
    escalon no alcanza» --subir de diametro no lo cambia-- sino otro
    regimen, el que el HDS-5 num. 3.3.4 (pag. impresa 3.25) admite. M4 lo
    recibe y resuelve los dos controles y el perfil de la lamina sin flujo
    uniforme. EL CERO ES EXACTO, como el de `TW_m`: es el centinela que el
    proyectista escribe para «barril plano», no el resultado de una cuenta;
    una pendiente diminuta y positiva (1e-9) no es un barril horizontal, es
    una pendiente que Manning no puede aprovechar, y ahi la respuesta sigue
    siendo None. La banda intermedia la acota V10 con
    'pendiente_minima_conducto' (ficha T2-01 de decisiones_diferidas.md).

    LA DISCONTINUIDAD QUE ESO DEJA, Y SU DIRECCION (medida; auditor de T-2).
    Con D = 0.90 m, Q = 0.6 m3/s, L = 18 m y salida libre, el perfil de la
    lamina (`M4.perfil_lamina`) da y_max/D = 0.6426 con S = 0, 0.6291 con
    S = 0.0005 y 0.6151 con S = 0.001: el barril horizontal es la ENVOLVENTE,
    el mayor llenado de los tres, de modo que aceptarlo no es lo optimista.
    Lo SOBRECONSERVADOR es el None de aqui para 0 < S <~ 0.00105 --hasta que
    el caudal a seccion llena de Manning alcanza a Q--: ese tubo se rechaza
    sin integrar el perfil, que daria MENOS llenado que el horizontal. La
    consecuencia hay que saberla: declarar S = 0 en vez de 0.001 da un tubo
    menor, y no porque el horizontal conduzca mejor sino porque un caso se
    resuelve por el perfil y el otro por la capacidad de Manning (PC-06).
    Unificarlos cambia el criterio de capacidad de todo el catalogo.
    """
    # `tirante_normal` valida los cuatro parametros (S < 0 y NaN incluidos) y
    # con S = 0 devuelve None por su propia guardia de capacidad; por eso se
    # llama PRIMERO y el caso horizontal se separa despues: una sola lectura
    # del n de capacidad, y ninguna validacion duplicada aqui.
    geom = tirante_normal(seccion, Q, S, material.n_para_capacidad)
    if not S > 0:
        return SinTiranteNormal(S=S)
    if geom is None:
        return None
    # --- VE-2 (decision (b) de VE1-02) --- LA RAMA ALTA RESUELVE SU PROPIO
    # TIRANTE: la misma ecuacion, la misma seccion y el mismo Q, con n_min.
    # Hasta VE-2 la velocidad alta era la de n_min SOBRE LA GEOMETRIA DE
    # n_max, V(n_max)*n_max/n_min, y su V*A no era Q sino Q*n_max/n_min (1.3*Q
    # en el concreto). Si esta segunda resolucion no converge, el trato es el
    # de la primera: None, sin sustituto. Con n_min <= n_max no ocurre --el
    # caudal a seccion llena crece al bajar n--, y no se le pone un default
    # para el dia en que un material traiga el par al reves.
    geom_erosion = tirante_normal(seccion, Q, S,
                                  material.n_para_velocidad_maxima)
    if geom_erosion is None:
        return None

    factor_geometrico = K_MANNING_SI * geom.R ** (2 / 3) * S ** (1 / 2)  # literal-ok: exponentes de Manning, ec. (47) del num. 4.1.1.3.6 / Sec. 4.1
    return TiranteNormal(
        geometria=geom,
        V_erosion=Q / geom_erosion.A,
        V_sedimentacion=factor_geometrico / material.n_para_velocidad_minima,
        geometria_erosion=geom_erosion,
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
    Q = (K_MANNING_SI/n)*A*R^(2/3)*S^(1/2) sobre la seccion trapecial (misma
    formula de Manning que la seccion circular, con el mismo coeficiente de
    unidades; lo unico que cambia es la geometria).
    """
    A = area_trapecial(b=b, z=z, y=y)
    P = perimetro_trapecial(b=b, z=z, y=y)
    if not P > 0:
        raise DatoInvalidoError(
            "seccion_receptor", valor=(b, z),
            motivo="perimetro mojado nulo: una seccion con solera b = 0 y "
                   "talud z = 0 no es una seccion, es una linea")
    R = A / P
    return (K_MANNING_SI / n) * A * R ** (2 / 3) * S ** (1 / 2)  # literal-ok: exponentes de Manning, Sec. 4.1


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
    # --- T-2 --- (INF-5.1.7) EL RECEPTOR SECO SE ADMITE. Hasta T-2 la
    # guardia era `not Q > 0`, M0 exigia lo mismo y la ayuda de la variable
    # decia «m3/s >= 0»: un dren que no lleva agua durante la avenida --el
    # dato de quien lo opera-- se rechazaba como invalido. Con Q = 0 no hay
    # lamina: el tirante es cero por definicion y no hace falta Manning.
    # Forma MAT-D13: en positivo y negada, un NaN tampoco pasa.
    if not Q >= 0:
        raise DatoInvalidoError(
            "Q_receptor_m3s", valor=Q,
            motivo="el caudal del receptor no puede ser negativo (0 es un "
                   "receptor seco)")
    if not Q > 0:
        return TW_SALIDA_LIBRE
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
    from scipy.optimize import brentq   # perezoso: ver la nota junto a los imports
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


def tirante_critico_trapecial(*, Q: float, seccion: SeccionReceptor) -> float:
    """
    --- T-3 (auditoria adversarial, H2) --- Tirante critico de una seccion
    trapecial abierta, m: la condicion de flujo critico Q^2 * T = g * A^3
    (HDS-5 num. A.3.1, pag. impresa A.3, cita HDS5_3ED.A.3.1#CRITICO: la
    carga de velocidad critica es la mitad del tirante hidraulico, A/T, que
    con V = Q/A es esta igualdad; la algebra es del proyecto).

    Lo pide el remanso de un paso de canal (`M7.remanso_canal`): si el
    tirante normal del canal no supera al critico, el canal es de pendiente
    FUERTE y la lamina remansada es una S1 que termina en resalto, de modo
    que la distancia a la que la horizontal del embalse corta la lamina
    normal ya no es cota inferior del remanso.

    En un trapecio abierto A^3/T crece con y sin limite, de modo que la raiz
    es UNICA y el corchete se abre por duplicacion, igual que en
    `tirante_normal_trapecial`. Con Q = 0 no hay lamina y el tirante es cero.
    """
    if not Q >= 0:
        raise DatoInvalidoError(
            "Q_m3s", valor=Q,
            motivo="el caudal del canal no puede ser negativo")
    if not Q > 0:
        return TW_SALIDA_LIBRE

    def f(y: float) -> float:
        A = area_trapecial(b=seccion.b_m, z=seccion.z_HV, y=y)
        T = seccion.b_m + 2 * seccion.z_HV * y      # ancho superficial
        return G * A * A * A - Q * Q * T             # Q^2 T = g A^3

    y_lo = TOL_THETA_BORDE
    y_hi = max(seccion.altura_total_m, seccion.b_m, 1)    # semilla del corchete
    from scipy.optimize import brentq   # perezoso: ver la nota junto a los imports
    for _ in range(DUPLICACIONES_MAX_CORCHETE):
        if f(y_hi) > 0:
            return brentq(f, y_lo, y_hi, xtol=TOL_BRENT)
        y_hi *= 2                                         # duplicacion del corchete
    raise LimiteNumericoError(
        "tirante_critico_canal", valor=Q,
        motivo=f"el caudal del canal ({Q} m3/s) no alcanza el regimen "
               f"critico en la seccion declarada ni con un tirante de "
               f"{y_hi:g} m: la combinacion de solera {seccion.b_m} m y "
               f"talud {seccion.z_HV} H:V no tiene sentido fisico para ese "
               "caudal")


class _MomentoDelBarril:
    """
    La funcion momentum de HEC-14 num. 6.2, Ec. (6.1), pag. impresa 6-3 (PDF
    66): M(t) = Q^2 / (g A) + A Y, con A Y el primer momento del area mojada
    respecto de la lamina, int_0^t A(z) dz, integrado por trapecios sobre el
    llenado PROPIO de la seccion (via canonica, `geometria_en`), con
    `PUNTOS_MOMENTO_SECCION` puntos. Vale para cualquier forma del protocolo
    `Seccion`: HEC-14 da la Ec. (6.2) con los K y C de Sylvester para cada
    forma, y aqui se integra la propia seccion en vez de leer la Tabla 6.1.

    POR ENCIMA DE LA CLAVE (t >= altura) la seccion va llena y t es la carga
    piezometrica sobre la solera: A = A_llena y el primer momento crece a
    razon de A_llena por metro, int_0^H A dz + A_llena (t - H). Es la Ec.
    (6.5) del circular (pag. impresa 6-8, «For y2 greater than or equal to
    D»: el termino 0.5 C2 D / (C1 y1) es el centroide de la seccion llena a
    D/2), escrita para cualquier forma.
    """

    def __init__(self, Q: float, seccion: Seccion) -> None:
        import numpy as np
        self.Q, self.seccion = Q, seccion
        self.lo, self.hi = seccion.bracket_llenado()
        llenados = np.linspace(self.lo, self.hi, PUNTOS_MOMENTO_SECCION)
        geos = [seccion.geometria_en(float(l)) for l in llenados]
        self._ys = np.array([g.y for g in geos])
        As = np.array([g.A for g in geos])
        self._As = As
        self._primer_momento = np.concatenate(
            ([0.0], np.cumsum((As[1:] + As[:-1]) / 2 * np.diff(self._ys))))
        self.altura = float(self._ys[-1])
        self.A_llena = seccion.area_llena

    def llenado_de(self, t: float) -> float:
        """El llenado propio cuyo tirante es t (t bajo la clave)."""
        from scipy.optimize import brentq   # perezoso: ver la nota junto a los imports
        return brentq(lambda l: self.seccion.geometria_en(l).y - t,
                      self.lo, self.hi, xtol=TOL_BRENT)

    def area(self, t: float) -> float:
        """A(t); la llena por encima de la clave."""
        if not t < self.altura:
            return self.A_llena
        return self.seccion.geometria_en(self.llenado_de(t)).A

    def __call__(self, t: float) -> float:
        import numpy as np
        if not t < self.altura:
            return (self.Q * self.Q / (G * self.A_llena)
                    + float(self._primer_momento[-1])
                    + self.A_llena * (t - self.altura))
        g = self.seccion.geometria_en(self.llenado_de(t))
        return (self.Q * self.Q / (G * g.A)
                + float(np.interp(g.y, self._ys, self._primer_momento)))

    def tabulado(self, t: float) -> float:
        """
        M(t) con el area INTERPOLADA en la misma tabla del primer momento, sin
        resolver el llenado: es la que `M4` evalua estacion a estacion para
        situar el resalto (miles de estaciones por corrida). La diferencia
        con `__call__` es de interpolacion lineal sobre
        `PUNTOS_MOMENTO_SECCION` puntos: precision numerica.
        """
        import numpy as np
        if not t < self.altura:
            return self(t)
        A = float(np.interp(t, self._ys, self._As))
        return (self.Q * self.Q / (G * A)
                + float(np.interp(t, self._ys, self._primer_momento)))

    def conjugado(self, y1: float, y_c: float) -> float:
        """
        El tirante subcritico (o la carga piezometrica, si no cabe bajo la
        clave) con el mismo momentum que el supercritico y1 < y_c.
        """
        from scipy.optimize import brentq   # perezoso: ver la nota junto a los imports
        objetivo = self(y1)
        if not self(self.altura) < objetivo:
            return brentq(lambda t: self(t) - objetivo, y_c, self.altura,
                          xtol=TOL_BRENT)
        # Lleno: M crece linealmente con la carga (A_llena por metro).
        return self.altura + (objetivo - self(self.altura)) / self.A_llena


def tirante_conjugado_barril(*, Q: float, seccion: Seccion, y: float,
                             y_c: float) -> Optional[float]:
    """
    --- VE-3.11 (H2 de los ensayos de diseño del conducto) --- El tirante
    CONJUGADO (secuente) del tirante supercritico `y` dentro del barril, m, o
    `None` si no cabe en la seccion (el momentum de `y` supera al de la
    seccion llena: el resalto no se forma a lamina libre).

    Es donde HDS-5 situa el resalto bajo control de ENTRADA con la salida
    alta: num. 3.1.3, pag. impresa 3.2 («submergence of the outlet end of the
    culvert does not assure outlet control. In this case, the flow just
    downstream of the inlet is supercritical and a hydraulic jump forms in the
    culvert barrel»). Si el TW alcanza el conjugado del tirante normal, el
    resalto entra al barril y aguas abajo de el la lamina esta al nivel del
    TW; si no, el resalto sale y el barril va a tirante normal.

    La funcion momentum es la de HEC-14 Ec. (6.1) (`_MomentoDelBarril`,
    desde VE-5; la misma ecuacion que `tirante_conjugado_trapecial` escribe
    con el centroide del trapecio). El conjugado que no cabe bajo la clave
    lo resuelve `resalto_hidraulico` (Ec. 6.5); esta funcion conserva su
    contrato de VE-3.11 y devuelve None.
    """
    momento = _MomentoDelBarril(Q, seccion)
    y2 = momento.conjugado(y, y_c)
    if not y2 < momento.altura:
        return None
    return y2


def exigir_dominio_del_resalto(S: float) -> None:
    """
    El dominio de la Ec. (6.1) de HEC-14 aplicada a un barril con pendiente:
    num. 6.3, pag. impresa 6-13 (PDF 76), «This volume may be neglected for
    slopes less than 10 percent and the jump analyzed as a horizontal
    channel» (`HEC14_RESALTO_PENDIENTE_HORIZONTAL_MAX`). Por encima levanta
    `MetodoNoEvaluableError` con el rotulo de HEC-14: el peso del agua dentro
    del resalto entra a la ecuacion y la fuente remite a Bradley (1961) y a
    ensayos de modelo, que este software no implementa.
    """
    if not S < HEC14_RESALTO_PENDIENTE_HORIZONTAL_MAX:
        raise MetodoNoEvaluableError(
            que="resalto hidraulico",
            procedimiento=("el resalto en canal inclinado con el peso del agua "
                           "dentro del volumen de control (HEC-14 num. 6.3, "
                           "Bradley 1961) o ensayos de modelo"),
            motivo=(f"la pendiente del barril ({S:g}) no es menor que "
                    f"{HEC14_RESALTO_PENDIENTE_HORIZONTAL_MAX:g}: HEC-14 num. "
                    "6.3 solo deja analizar el resalto como en canal "
                    "horizontal por debajo del 10 %"),
            rotulo=MOTIVO_METODO_NO_EVALUABLE_HEC14)


def resalto_hidraulico(*, Q: float, seccion: Seccion, y1: float, y_c: float,
                       S: float, x_desde_salida_m: Optional[float] = None
                       ) -> ResaltoHidraulico:
    """
    --- VE-5 (lote m45, item 17; fichas EA-02 y VE3-08) --- El resalto
    hidraulico del tirante supercritico `y1` en el barril, por CANTIDAD DE
    MOVIMIENTO: HEC-14 (FHWA-NHI-06-086) num. 6.2 «Hydraulic Jump in
    Horizontal Channels», Ec. (6.1), pag. impresa 6-3 (PDF 66): «The general
    form of the momentum equation can be used for the solution of the
    hydraulic jump sequent-depth relationship in any shape of channel with a
    horizontal floor». El conjugado sale de `_MomentoDelBarril`; con la
    seccion 2 llena (el conjugado no cabe bajo la clave) es la Ec. (6.5),
    pag. impresa 6-8, escrita para cualquier forma.

    El Froude es el de la pag. impresa 6-9 («Fr1 is computed using the
    maximum depth in the channel»): V1 / sqrt(g y1). La velocidad tras el
    resalto es V2 = Q / A2, el paso 3 de los ejemplos resueltos (pags.
    impresas 6-6 y 6-11); con la seccion llena, A2 = A_llena.

    DOMINIO: la Ec. (6.1) es de fondo HORIZONTAL. El num. 6.3 (pag. impresa
    6-13, PDF 76) deja despreciar el peso del agua dentro del resalto «for
    slopes less than 10 percent» (`HEC14_RESALTO_PENDIENTE_HORIZONTAL_MAX`);
    por encima la fuente remite a Bradley (1961) y a ensayos de modelo, y la
    funcion levanta `MetodoNoEvaluableError` con el rotulo de HEC-14. Un
    `y1` que no es supercritico (y1 >= y_c) no tiene resalto: DatoInvalido.
    """
    exigir_dominio_del_resalto(S)
    if not 0 < y1 < y_c:
        raise DatoInvalidoError(
            "y1", valor=y1,
            motivo=f"el resalto parte de un tirante supercritico, 0 < y1 < "
                   f"y_c = {y_c} m")
    momento = _MomentoDelBarril(Q, seccion)
    y2 = momento.conjugado(y1, y_c)
    A1 = momento.area(y1)
    A2 = momento.area(y2)
    V1 = Q / A1
    return ResaltoHidraulico(
        y1_m=y1, A1_m2=A1, V1_m_s=V1, Fr1=V1 / math.sqrt(G * y1),
        y2_m=y2, A2_m2=A2, V2_m_s=Q / A2,
        lleno=not y2 < momento.altura,
        x_desde_salida_m=x_desde_salida_m)


def tirante_conjugado_trapecial(*, Q: float, seccion: SeccionReceptor,
                                y: float) -> float:
    """
    --- VE-3.7 --- El tirante CONJUGADO (secuente) de `y` en la seccion
    trapecial del canal, m: el otro tirante con la misma funcion momentum
    M(y) = Q^2 / (g A) + y_G A, con y_G = y (3 b + 2 z y) / (6 (b + z y)) la
    profundidad del centroide del trapecio bajo la lamina. Es donde el
    HDS-5 situa el resalto al final de una S1 (num. 3.5.1, la profundidad
    secuente; cita HDS5_3ED.3.5.1#S1 en su nota); la ecuacion de momentum
    de un resalto en canal prismatico horizontal es de manual y el
    algebra del trapecio, del proyecto.

    Con `y` supercritico devuelve el subcritico, y al reves. El corchete se
    abre desde el critico por duplicacion, como en los tirantes normal y
    critico de esta seccion.
    """
    from scipy.optimize import brentq   # perezoso: ver la nota junto a los imports
    b, z = seccion.b_m, seccion.z_HV

    def M(t: float) -> float:
        A = area_trapecial(b=b, z=z, y=t)
        y_G = t * (3 * b + 2 * z * t) / (6 * (b + z * t))  # literal-ok: centroide del trapecio
        return Q * Q / (G * A) + y_G * A

    y_c = tirante_critico_trapecial(Q=Q, seccion=seccion)
    objetivo = M(y)
    if y < y_c:
        y_hi = max(2 * y_c, seccion.altura_total_m)
        for _ in range(DUPLICACIONES_MAX_CORCHETE):
            if M(y_hi) > objetivo:
                return brentq(lambda t: M(t) - objetivo, y_c, y_hi,
                              xtol=TOL_BRENT)
            y_hi *= 2                                     # duplicacion del corchete
    else:
        return brentq(lambda t: M(t) - objetivo, TOL_THETA_BORDE, y_c,
                      xtol=TOL_BRENT)
    raise LimiteNumericoError(
        "tirante_conjugado_canal", valor=y,
        motivo=f"no hay tirante conjugado de y = {y} m con Q = {Q} m3/s en "
               "la seccion declarada del canal")


def energia_y_friccion_trapecial(*, Q: float, b: float, z: float, n: float,
                                 y: float) -> Tuple[float, float]:
    """
    --- VE-4c --- (E, Sf) en una seccion trapecial con tirante VERTICAL y:
    la energia especifica E = y + V^2 / (2 g) y la pendiente de friccion de
    Manning Sf = (n V / (K R^(2/3)))^2, con V = Q / A (Manual num. 4.1.1.3.6
    para Manning; K = K_MANNING_SI). Son las dos piezas de cada escalon del
    paso directo de `perfil_remanso_trapecial`, sacadas a una funcion para
    que el escalon se pueda contrastar por si solo: la validacion contra el
    perfil publicado del USBR (223-E3WSP, «Design of Small Canal Structures»,
    pag. impresa 428) cierra el balance de energia de cada tramo con ellas
    (tests/test_ve4c_v5_remanso.py).
    """
    A = area_trapecial(b=b, z=z, y=y)
    R = A / perimetro_trapecial(b=b, z=z, y=y)
    V = Q / A
    return (y + V * V / (2 * G),                                # literal-ok: carga de velocidad V^2/(2g)
            (n * V / (K_MANNING_SI * R ** (2 / 3))) ** 2)      # literal-ok: Manning, Sf = (n V / R^(2/3))^2


def remanso_aguas_arriba(*, Q: float, seccion: SeccionReceptor, HW: float,
                         sobreelevacion_admisible: float
                         ) -> RemansoAguasArriba:
    """
    --- VE-4c --- (ficha T7B-01) El remanso que la obra forma en el cauce de
    APROXIMACION, aguas arriba de la boca, por el paso directo de
    `perfil_remanso_trapecial` con la carga a la entrada como condicion de
    borde: el tirante del cauce en la boca es HW (la solera del cauce en la
    boca se toma en la cota de entrada del conducto, y el HW sin la carga de
    velocidad de aproximacion, como lo da M4: HDS-5 la desprecia).

    Lo que mide es lo que la obra AÑADE sobre el cauce natural: la distancia
    hasta la que la lamina queda MAS de `sobreelevacion_admisible` (Δ) por
    encima del tirante natural, que es el normal de Manning y_n en la seccion
    del cauce (HDS-5 num. 2.2.3 e.: la lamina del cauce natural «as defined
    by the normal depth»).

        cauce suave  (y_n > y_c):  M1 de HW a y_fin = y_n + Δ. Con Δ = 0 la M1
                                   es asintotica al normal y no tiene final:
                                   `longitud_m` None y `asintotico`.
        cauce fuerte (y_n <= y_c): S1 de HW a y_fin = max(y_conj, y_n + Δ), con
                                   y_conj el conjugado del normal: el resalto.
                                   Aguas arriba el cauce corre a su normal.

    Si HW no supera y_fin, la obra no remansa el cauce por encima del
    admisible (o el resalto queda en la boca): longitud 0. El corte entre
    suave y fuerte es el de `M7.remanso_canal` (y_n > y_c + TOL_UMBRAL_
    NORMATIVO).

    No juzga el dominio del metodo (la altura de la seccion, Δ = 0 en un
    cauce suave): lo hace quien lo usa, V5, con su rotulo.
    """
    y_n = tirante_normal_trapecial(Q=Q, seccion=seccion)
    y_c = tirante_critico_trapecial(Q=Q, seccion=seccion)
    suave = y_n > y_c + TOL_UMBRAL_NORMATIVO
    y_conj = None
    if suave:
        if not sobreelevacion_admisible > 0:
            if HW > y_n:
                return RemansoAguasArriba(
                    y_normal_m=y_n, y_critico_m=y_c, suave=True,
                    rama=RAMA_REMANSO_M1, y_conjugado_m=None, y_fin_m=None,
                    longitud_m=None, asintotico=True)
            y_fin = y_n
        else:
            y_fin = y_n + sobreelevacion_admisible
        rama = RAMA_REMANSO_M1
    else:
        y_conj = tirante_conjugado_trapecial(Q=Q, seccion=seccion, y=y_n)
        y_fin = max(y_conj, y_n + sobreelevacion_admisible)
        rama = RAMA_REMANSO_S1
    if not HW > y_fin:
        return RemansoAguasArriba(
            y_normal_m=y_n, y_critico_m=y_c, suave=suave,
            rama=RAMA_REMANSO_NINGUNA, y_conjugado_m=y_conj, y_fin_m=y_fin,
            longitud_m=0.0, estaciones=((0.0, HW),))
    L, estaciones = perfil_remanso_trapecial(Q=Q, seccion=seccion,
                                             y_inicio=HW, y_fin=y_fin)
    return RemansoAguasArriba(
        y_normal_m=y_n, y_critico_m=y_c, suave=suave, rama=rama,
        y_conjugado_m=y_conj, y_fin_m=y_fin, longitud_m=L,
        estaciones=estaciones)


def perfil_remanso_trapecial(*, Q: float, seccion: SeccionReceptor,
                             y_inicio: float, y_fin: float,
                             pasos: int = PASOS_PERFIL_REMANSO
                             ) -> Tuple[float, Tuple[Tuple[float, float], ...]]:
    """
    --- VE-3.7 --- El perfil de la lamina en el canal prismatico trapecial
    por PASO DIRECTO, aguas ARRIBA desde la boca de la obra (`y_inicio`)
    hasta `y_fin`: el mismo metodo con que el HDS-5 calcula la lamina en el
    barril (num. 3.5, cita HDS5_3ED.3.5#PERFIL; aqui sobre el canal), en
    cada escalon

        dx = (E_abajo - E_arriba) / (S - Sf_medio),   E = y + V^2 / (2 g),
        Sf = (n Q / (A R^(2/3)))^2   (Manning, Manual num. 4.1.1.3.6)

    Devuelve (longitud aguas arriba en m, estaciones (x, y)). Los escalones
    van en progresion GEOMETRICA de (y - y_n), con y_n el tirante normal del
    canal, para que la escalera no pierda precision cerca de la asintota de
    una M1 (`tolerancias.PASOS_PERFIL_REMANSO`). Sirve para la M1 de un
    canal suave (y_inicio > y_fin > y_n) y para la S1 de uno fuerte, hasta
    el conjugado del normal (y_inicio > y_fin > y_c > y_n).
    """
    b, z = seccion.b_m, seccion.z_HV
    S, n = seccion.S, seccion.n
    y_n = tirante_normal_trapecial(Q=Q, seccion=seccion)
    if not (y_inicio > y_fin > y_n and pasos >= 2):
        raise DatoInvalidoError(
            "perfil_remanso", valor=(y_inicio, y_fin, y_n),
            motivo="el paso directo del remanso va de la boca hacia aguas "
                   "arriba con el tirante decreciendo hacia el normal: "
                   "y_inicio > y_fin > y_n")

    def _E_Sf(t: float) -> Tuple[float, float]:
        return energia_y_friccion_trapecial(Q=Q, b=b, z=z, n=n, y=t)

    d0, d1 = y_inicio - y_n, y_fin - y_n
    x = 0.0
    estaciones = [(0.0, y_inicio)]
    E_a, Sf_a = _E_Sf(y_inicio)
    for i in range(1, pasos + 1):
        t = y_n + d0 * (d1 / d0) ** (i / pasos)
        E_b, Sf_b = _E_Sf(t)
        x += (E_a - E_b) / (S - (Sf_a + Sf_b) / 2)   # literal-ok: Sf medio del escalon
        estaciones.append((x, t))
        E_a, Sf_a = E_b, Sf_b
    if not (x > 0 and math.isfinite(x)):
        raise LimiteNumericoError(
            "perfil_remanso", valor=x,
            motivo=f"el paso directo del remanso no dio una longitud finita "
                   f"y positiva entre y = {y_inicio} m y y = {y_fin} m "
                   f"(y_n = {y_n} m)")
    return x, tuple(estaciones)


def seccion_del_receptor(seccion_medida: Optional[SeccionReceptor] = None
                         ) -> Tuple[SeccionReceptor, str]:
    """
    --- T-2 --- (INF-3.2.8) La seccion del receptor con que corre Sec. 1.3,
    y DE DONDE SALE: la MEDIDA si el expediente la trae, la ADOPTADA si no.

    La medida GANA siempre: es un levantamiento del dren o del canal (ancho
    de fondo, talud, profundidad, n y pendiente; `servicio.CLAVES_RECEPTOR`
    de --datos-externos, que el script de QGIS del proyecto puede exportar),
    y un dato entregado no se sustituye por una adopcion. Con ella el
    criterio 'seccion_receptor' NI SE INVOCA, de modo que la memoria no lo
    lista entre los usados. Sin ella rige el criterio [A], y el rotulo que
    vuelve --`SECCION_RECEPTOR_ADOPTADA`-- es el que la memoria imprime y
    el que dispara el aviso de `tw_seccion_1_3`.
    """
    if seccion_medida is not None:
        return seccion_medida, SECCION_RECEPTOR_MEDIDA
    return _seccion_declarada(), SECCION_RECEPTOR_ADOPTADA


def _de_la_seccion(origen: str) -> str:
    """La procedencia de un campo de la seccion, segun de donde salio."""
    if origen == SECCION_RECEPTOR_MEDIDA:
        return ("seccion MEDIDA del receptor (--datos-externos, claves "
                "`receptor_*`: levantamiento del dren o canal)")
    return ("criterio 'seccion_receptor' [A]: seccion ADOPTADA por falta de "
            "levantamiento")


def _aviso_seccion_adoptada(via: ViaDelTW) -> str:
    """
    El aviso que dispara un TW obtenido con la seccion ADOPTADA (INF-3.2.8).
    Un solo texto para la CLI, el JSON y la memoria.
    """
    que = ("el nivel de «receptor a seccion llena» es la profundidad adoptada"
           if via is ViaDelTW.ESCENARIOS_ACOTADOS else
           "el tirante del receptor sale de Manning sobre la geometria "
           "adoptada")
    return (f"TW del receptor: {SECCION_RECEPTOR_ADOPTADA} -- {que} en el "
            f"criterio '{CRITERIO_SECCION_RECEPTOR}', no una medicion, y ese "
            "TW entra al control de salida, al regimen del barril y a V1: "
            "puede decidir el diametro. Lo sustituye el levantamiento del "
            "receptor (claves `receptor_b_m`, `receptor_z_HV`, "
            "`receptor_altura_m`, `receptor_n` y `receptor_S` de "
            "--datos-externos), su nivel de agua (`cota_TW`) o un TW "
            "declarado (`TW_m`)")


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
                   tw_declarado: Optional[float] = None,
                   seccion_medida: Optional[SeccionReceptor] = None
                   ) -> TWDeterminado:
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

    `seccion_medida` (T-2, INF-3.2.8): la seccion del receptor LEVANTADA, que
    gana sobre el criterio 'seccion_receptor' en las vias 3 y 4
    (`seccion_del_receptor`). El `TWDeterminado` dice con cual corrio
    (`seccion`, `origen_seccion`) y, si fue la adoptada, lleva el AVISO que
    la CLI, el JSON y la memoria imprimen.
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
        seccion, origen = seccion_del_receptor(seccion_medida)
        de_la_seccion = _de_la_seccion(origen)
        y_n = tirante_normal_trapecial(Q=punto.Q_receptor_m3s, seccion=seccion)
        cota_agua = punto.cota_fondo_receptor + y_n
        tw = _tw_desde_cota(cota_agua, cota_fondo_salida)
        return TWDeterminado(
            valor=tw, via=ViaDelTW.MANNING_RECEPTOR, cota_TW_msnm=cota_agua,
            seccion=seccion, origen_seccion=origen,
            avisos=(() if origen == SECCION_RECEPTOR_MEDIDA else
                    (_aviso_seccion_adoptada(ViaDelTW.MANNING_RECEPTOR),)),
            paso=_paso_tw(
                punto=punto, cota_fondo_salida=cota_fondo_salida, tw=tw,
                cota_agua=cota_agua, via=ViaDelTW.MANNING_RECEPTOR,
                sustitucion=(
                    Magnitud("Q_receptor", punto.Q_receptor_m3s, "m3/s",
                             "columna del CSV (Sec. 1.2), paso 1: caudal de "
                             "diseño del receptor (ANA / Junta de Usuarios)",
                             cifras=CIFRAS_MAGNITUD),
                    Magnitud("b", seccion.b_m, "m",
                             f"solera de la seccion del receptor, "
                             f"{de_la_seccion}", cifras=CIFRAS_MAGNITUD),
                    Magnitud("z", seccion.z_HV, "H:V",
                             f"talud de la seccion del receptor, "
                             f"{de_la_seccion}", cifras=CIFRAS_MAGNITUD),
                    Magnitud("n_receptor", seccion.n, "",
                             f"Manning del receptor -- NO el del conducto --, "
                             f"{de_la_seccion}",
                             cifras=CIFRAS_FINA),
                    Magnitud("S_receptor", seccion.S, "m/m",
                             f"pendiente del receptor, {de_la_seccion}",
                             cifras=CIFRAS_FINA),
                    Magnitud("y_n", y_n, "m",
                             "tirante normal en el receptor, paso 2: Manning "
                             "sobre la seccion trapecial"
                             + ("" if punto.Q_receptor_m3s > 0 else
                                ". El receptor va SECO (Q_receptor = 0): no "
                                "hay lamina y el tirante es cero sin resolver "
                                "nada"),
                             cifras=CIFRAS_MAGNITUD),
                    Magnitud("cota_fondo_receptor", punto.cota_fondo_receptor,
                             "msnm", "columna del CSV (Sec. 1.2)",
                             cifras=CIFRAS_MAGNITUD),
                    Magnitud("cota_fondo_salida", cota_fondo_salida, "msnm",
                             "M7 (7.B): cota de entrada - S*L",
                             cifras=CIFRAS_MAGNITUD))))

    # --- Via 4: paso 3, los dos escenarios acotados
    seccion, origen = seccion_del_receptor(seccion_medida)
    de_la_seccion = _de_la_seccion(origen)
    cota_llena = punto.cota_fondo_receptor + seccion.altura_total_m
    tw_llena = _tw_desde_cota(cota_llena, cota_fondo_salida)
    escenarios = ((ESCENARIO_SALIDA_LIBRE, TW_SALIDA_LIBRE),
                  (ESCENARIO_SECCION_LLENA, tw_llena))
    gobernante = max(tw for _rotulo, tw in escenarios)
    return TWDeterminado(
        valor=gobernante, via=ViaDelTW.ESCENARIOS_ACOTADOS,
        cota_TW_msnm=cota_fondo_salida + gobernante,
        escenarios=escenarios,
        seccion=seccion, origen_seccion=origen,
        avisos=(() if origen == SECCION_RECEPTOR_MEDIDA else
                (_aviso_seccion_adoptada(ViaDelTW.ESCENARIOS_ACOTADOS),)),
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
                         f"profundidad de la seccion del receptor, "
                         f"{de_la_seccion}: es lo que acota el segundo "
                         f"escenario", cifras=CIFRAS_MAGNITUD),
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

