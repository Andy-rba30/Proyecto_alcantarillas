"""
tests/test_seccion_rectangular.py
=================================
`SeccionRectangular` (C4): la hidraulica del marco, contra los casos patron
CP-2R, CP-5R, CP-6R, CP-8R y CP-5DR, todos calculados A MANO desde la ecuacion.

QUE VIGILA ESTE ARCHIVO, y por que cada bloque existe:

  1. La geometria de la forma, y las DOS "R" que un marco tiene y un tubo no.
  2. Que las dos parametrizaciones de `Seccion` coincidan BIT A BIT aqui -- y
     que eso NO se pueda leer como permiso para cambiar de via en M3 o en M4
     (regla vinculante #12: en la circular no coinciden).
  3. Que el Brent de Manning encaje sin tocarlo (punto 3 del prompt de C4).
  4. El tirante critico CERRADO, con sus tres identidades y con sus guardias
     de aritmetica, cada una con el par que la dispara MEDIDO.
  5. El control de entrada por las DOS formas y el de salida.
  6. Que los CP5D_* de C3 den el MISMO numero sobre la rectangular: la
     ecuacion no mira la forma de la seccion, mira q*, K y M.
  7. La traza de memoria de los pasos nuevos, con mutaciones que tienen que
     matarlos.
"""

import math

import pytest

from constantes_fisicas import G
from constantes_normativas import HDS5_INLET, KU_SI
from modelos import (ConstantesHDS5, DatoInvalidoError, LimiteNumericoError,
                     SeccionCircular, SeccionRectangular)
from modulos.M3_hidraulica import resolver_manning, tirante_normal
from modulos.M4_control import (_pasos_hidraulicos, caudal_adimensional,
                                control_entrada, control_salida,
                                tirante_critico)
from modulos.M2_material import catalogo
from tests.apoyo.aproximacion import ABS_CERO
from modelos import ControlGobernante, TipoMaterial
from tests.fixtures.casos_patron import (CP2R_GEOMETRIA_MANNING_RECTANGULAR,
                                         CP5D_FORMA2,
                                         CP5DR_TRANSICION_CAJON,
                                         CP5R_CONTROL_ENTRADA_RECTANGULAR,
                                         CP6R_TIRANTE_CRITICO_RECTANGULAR,
                                         CP8R_CONTROL_SALIDA_RECTANGULAR)


def _material(carta=None, n_min=None, n_max=None):
    """
    El material del catalogo, con la carta y el rango de n que pida el caso.

    Se parte del CONCRETO REFORZADO real y se le reemplazan los campos, en vez
    de construir un `Material` a mano: es el mismo patron que usa
    `test_M4_control._pasos_con`, y evita que un campo nuevo del tipo deje
    este archivo con un material a medio armar.
    """
    import dataclasses
    base = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    cambios = {}
    if carta is not None:
        cambios["hds5"] = ConstantesHDS5.desde_dict(HDS5_INLET[carta])
    if n_min is not None:
        cambios["n_min"] = n_min
    if n_max is not None:
        cambios["n_max"] = n_max
    return dataclasses.replace(base, **cambios)


CP2R = CP2R_GEOMETRIA_MANNING_RECTANGULAR
CP5R = CP5R_CONTROL_ENTRADA_RECTANGULAR
CP6R = CP6R_TIRANTE_CRITICO_RECTANGULAR
CP8R = CP8R_CONTROL_SALIDA_RECTANGULAR


def _marco():
    return SeccionRectangular(CP2R["B"], CP2R["H"])


# ===========================================================================
# 1 - Geometria de la forma
# ===========================================================================

def test_geometria_del_marco_es_la_del_caso_patron():
    """A = B*y, P = B + 2y, R = A/P, T = B. Las cuatro, contra CP-2R."""
    m = _marco()
    tol = CP2R["tolerancia_geometria"]
    y = CP2R["y"]
    assert m.area(y) == pytest.approx(CP2R["A_esperado"], abs=tol)
    assert m.perimetro(y) == pytest.approx(CP2R["P_esperado"], abs=tol)
    assert m.ancho_superficial(y) == pytest.approx(CP2R["T_esperado"], abs=tol)
    assert m.geometria_en(y).R == pytest.approx(CP2R["R_esperado"], abs=tol)
    assert m.area_llena == pytest.approx(CP2R["A_llena_esperada"], abs=tol)
    assert m.radio_hidraulico_lleno == pytest.approx(
        CP2R["R_lleno_esperado"], abs=tol)


def test_el_ancho_superficial_no_depende_del_tirante():
    """
    T = B, constante. Es la propiedad que CIERRA el tirante critico, y por eso
    se fija aparte: si alguien escribiera T = B*algo(y), la solucion cerrada
    dejaria de ser valida y ningun otro test lo diria.
    """
    m = _marco()
    for y in (0.01, 0.25, 0.90, 1.49, CP2R["H"]):
        assert m.ancho_superficial(y) == pytest.approx(
            CP2R["B"], abs=CP2R["tolerancia_geometria"])


def test_las_dos_R_del_marco_no_son_la_misma_y_es_correcto():
    """
    LA DISTINCION QUE EN LA CIRCULAR NO SE VE. `geometria_en(H).R` es de
    LAMINA LIBRE (P = B + 2H, sin la losa superior) y `radio_hidraulico_lleno`
    es de PRESION (P = 2(B+H), con ella). En un marco no convergen nunca; en
    un circulo si, porque en theta = 2*pi el ancho de la lamina se anula.

    Se fija con numeros porque la diferencia es del 40 %: quien las confunda
    no comete un error de ultimos bits.
    """
    m = _marco()
    tol = CP2R["tolerancia_geometria"]
    assert m.geometria_en(CP2R["H"]).R == pytest.approx(
        CP2R["R_lamina_libre_en_H"], abs=tol)
    assert m.radio_hidraulico_lleno == pytest.approx(
        CP2R["R_lleno_esperado"], abs=tol)
    assert m.geometria_en(CP2R["H"]).R != pytest.approx(
        m.radio_hidraulico_lleno, abs=tol)

    # En la circular SI convergen, y por eso la confusion no se detecta ahi.
    c = SeccionCircular(0.90)
    theta_lleno = c.bracket_llenado()[1]
    assert c.geometria_en(theta_lleno).R == pytest.approx(
        c.radio_hidraulico_lleno,
        abs=CP2R["tolerancia_convergencia_circular"])


def test_la_etiqueta_es_la_que_fija_la_especificacion():
    assert _marco().etiqueta() == "marco 2.00 × 1.50 m"


# ===========================================================================
# 2 - Las dos parametrizaciones (regla vinculante #12)
# ===========================================================================

def test_en_el_marco_las_dos_vias_coinciden_bit_a_bit():
    """
    El parametro propio de un marco ES el tirante: no hay inversion por medio
    y las dos vias tienen que dar el MISMO float, no uno parecido. Se compara
    con `==` a proposito -- es la unica forma de afirmar identidad de bits --
    y por eso no rompe la regla de no comparar floats: lo que se afirma es que
    NO hay operacion intermedia.
    """
    m = _marco()
    for y in (0.001, 0.10, 0.50, 0.90, 1.25, 1.50):
        g = m.geometria_en(y)
        assert g.A == m.area(y)
        assert g.P == m.perimetro(y)
        assert g.T == m.ancho_superficial(y)
        assert g.y == y


def test_que_coincidan_en_el_marco_no_las_hace_intercambiables():
    """
    LA TRAMPA DE ESTA SESION, fijada como test -- y con la medida CORREGIDA,
    porque la regla vinculante #12 la enunciaba de mas.

    Lo que C1 escribio: «en los DOS extremos de `bracket_llenado()` la via por
    tirante devuelve 0.0 exacto para P y para T». Medido en C4 sobre D = 0.90:

        theta = 1e-9 (extremo INFERIOR)
            canonica   P = T = 4.5e-10        via por tirante  P = T = 0.0
            -> 100 %, y es 0.0 EXACTO. La frase vale entera aqui.
        theta = 2*pi - 1e-9 (extremo SUPERIOR)
            canonica   T = 4.500001474513789e-10
            via por y  T = 1.1021821192326179e-16   -> ~100 % relativo, pero
                                                       NO es cero exacto
            canonica   P = 2.8274333877808138
            via por y  P = 2.827433388230814        -> 1.6e-10 relativo, que
                                                       NO es 100 %

    La CONSECUENCIA no cambia --la division por cero esta en el extremo
    inferior, que es de los primeros puntos donde Brent evalua, y T es el
    denominador de A^3/T en `_residuo_critico`--, pero el enunciado si: en el
    extremo superior el perimetro no se anula ni de lejos. Queda corregido en
    §6 #12 y en el docstring de `modelos.Seccion`.
    """
    c = SeccionCircular(0.90)
    theta_min, theta_max = c.bracket_llenado()

    g_min = c.geometria_en(theta_min)
    assert g_min.P > 0 and g_min.T > 0
    # «Cero exacto» se afirma con la tolerancia de cero, que es como esta
    # suite tiene que escribirlo (SIS-F-16): la via canonica devuelve 4.5e-10
    # y ABS_CERO vale 1e-12, de modo que la distincion se conserva entera.
    assert c.perimetro(g_min.y) == pytest.approx(0.0, abs=ABS_CERO)
    assert c.ancho_superficial(g_min.y) == pytest.approx(0.0, abs=ABS_CERO)

    g_max = c.geometria_en(theta_max)
    assert g_max.T > 0
    # No es cero exacto, pero esta siete ordenes por debajo del canonico.
    assert 0 < c.ancho_superficial(g_max.y) < g_max.T / 1e6
    # Y el perimetro, en cambio, coincide en los ultimos bits.
    assert c.perimetro(g_max.y) == pytest.approx(
        g_max.P, abs=CP2R["tolerancia_convergencia_circular"])


def test_el_bracket_del_marco_no_necesita_margen_de_borde():
    """
    (0, H) entero. En y = 0 el area vale 0 pero el perimetro vale B > 0, de
    modo que R = 0/B esta definido -- a diferencia de la circular, donde
    R = 0/0 --. Copiarle el margen a la circular seria arrastrar una defensa
    contra una singularidad que esta forma no tiene.
    """
    m = _marco()
    inferior, superior = m.bracket_llenado()
    assert inferior == pytest.approx(0.0, abs=ABS_CERO)
    assert superior == pytest.approx(CP2R["H"],
                                     abs=CP2R["tolerancia_geometria"])
    g = m.geometria_en(inferior)
    assert g.A == pytest.approx(0.0, abs=ABS_CERO)
    assert g.P == pytest.approx(CP2R["B"], abs=CP2R["tolerancia_geometria"])
    assert g.R == pytest.approx(0.0, abs=ABS_CERO)


# ===========================================================================
# 3 - Manning sobre el marco (punto 3 del prompt)
# ===========================================================================

def test_manning_sobre_el_marco_da_el_caso_patron():
    """V = (1/n) R^(2/3) S^(1/2) y Q = V*A, con las DOS ramas de n."""
    m = _marco()
    g = m.geometria_en(CP2R["y"])
    tol = CP2R["tolerancia_hidraulica"]
    for clave, n in (("V_con_n_max_esperado", CP2R["n_max"]),
                     ("V_con_n_min_esperado", CP2R["n_min"])):
        V = (1 / n) * g.R ** (2 / 3) * CP2R["S"] ** 0.5
        assert V == pytest.approx(CP2R[clave], abs=tol)
    Q = CP2R["V_con_n_max_esperado"] * g.A
    assert Q == pytest.approx(CP2R["Q_con_n_max_esperado"], abs=tol)


def test_el_brent_de_la_circular_encaja_en_el_marco_sin_tocarlo():
    """
    PUNTO 3 DEL PROMPT, contestado con una medida. `tirante_normal` resuelve
    el marco con el MISMO solver, sin cambiarle nada: se le pide el caudal del
    caso patron y tiene que devolver su tirante.
    """
    m = _marco()
    g = tirante_normal(m, CP2R["Q_con_n_max_esperado"], CP2R["S"],
                       CP2R["n_max"])
    assert g is not None
    assert g.y == pytest.approx(CP2R["y"], abs=CP2R["tolerancia_brent"])
    assert g.llenado == g.y      # el parametro propio ES el tirante


def test_el_caudal_de_manning_es_monotono_creciente_en_el_marco():
    """
    Y ESO ES UNA DIFERENCIA CON LA CIRCULAR, no un detalle. La curva Q(theta)
    de un tubo tiene un PICO en y/D = 0.938 y despues baja; la de un marco
    crece hasta y = H sin pico, porque ni el area ni el radio hidraulico
    dejan de crecer. Consecuencia: el `None` de `tirante_normal` significa
    aqui, literalmente, "no hay tirante que transporte ese caudal en lamina
    libre", que es lo que MAT-O18 tuvo que matizar para el tubo.
    """
    m = _marco()
    n, S = CP2R["n_max"], CP2R["S"]
    caudales = []
    pasos = 400
    for i in range(1, pasos + 1):
        g = m.geometria_en(CP2R["H"] * i / pasos)
        caudales.append((1 / n) * g.A * g.R ** (2 / 3) * S ** 0.5)
    assert all(b > a for a, b in zip(caudales, caudales[1:]))

    # Por encima del caudal a seccion llena en lamina libre, no hay solucion.
    assert tirante_normal(m, caudales[-1] * 2, S, n) is None


def test_resolver_manning_da_las_dos_velocidades_sobre_el_marco():
    """La regla de doble n no cambia con la forma: misma R, dos n."""
    m = _marco()
    material = _material(n_min=CP2R["n_min"], n_max=CP2R["n_max"])
    resuelto = resolver_manning(seccion=m, Q=CP2R["Q_con_n_max_esperado"],
                                S=CP2R["S"], material=material)
    assert resuelto is not None
    assert resuelto.V_erosion > resuelto.V_sedimentacion
    assert resuelto.V_sedimentacion == pytest.approx(
        CP2R["V_con_n_max_esperado"], abs=CP2R["tolerancia_brent"])


# ===========================================================================
# 4 - Tirante critico cerrado
# ===========================================================================

def test_el_marco_despeja_su_tirante_critico_y_la_circular_no():
    """
    El contrato que hace que M4 no tenga que preguntar de que forma es la
    seccion: la que despeja devuelve un numero, la que no, `None`.
    """
    assert _marco().llenado_critico_cerrado(6.0, G) is not None
    assert SeccionCircular(0.90).llenado_critico_cerrado(6.0, G) is None


@pytest.mark.parametrize("caso", CP6R["casos"])
def test_tirante_critico_cerrado_contra_el_caso_patron(caso):
    """y_c = (q^2/g)^(1/3), V_c = Q/A_c y H_c = y_c + V_c^2/(2g)."""
    m = SeccionRectangular(CP6R["B"], CP6R["H"])
    critico = tirante_critico(caso["Q"], m)
    tol = CP6R["tolerancia"]
    assert critico.cerrado is True
    assert critico.y_c == pytest.approx(caso["y_c_esperado"], abs=tol)
    assert critico.V == pytest.approx(caso["V_c_esperado"], abs=tol)
    assert critico.H_c == pytest.approx(caso["H_c_esperado"], abs=tol)


@pytest.mark.parametrize("caso", CP6R["casos"])
def test_las_dos_identidades_del_critico_rectangular(caso):
    """
    H_c = 1.5*y_c y Froude = 1. LA PRIMERA ES EL MEJOR ORACULO QUE TIENE ESTE
    CASO: sale en dos renglones de y_c^3 = q^2/g, no depende ni de Q ni de B,
    y ningun error de transcripcion de constantes la reproduce por casualidad.
    """
    m = SeccionRectangular(CP6R["B"], CP6R["H"])
    critico = tirante_critico(caso["Q"], m)
    tol = CP6R["tolerancia_identidad"]
    assert critico.H_c / critico.y_c == pytest.approx(
        CP6R["H_c_sobre_y_c"], abs=tol)
    geom = critico.geometria
    froude = critico.V / math.sqrt(CP6R["g"] * geom.A / geom.T)
    assert froude == pytest.approx(CP6R["froude_esperado"], abs=tol)


def test_el_critico_cerrado_no_pasa_por_brent():
    """
    Que la solucion sea exacta no se puede afirmar leyendo el numero: se
    afirma comprobando que el solver NO se llama. Si alguien reintroduce Brent
    aqui -- "por uniformidad" -- este test cae, y con el vuelve la clase de
    fallo de convergencia que la forma cerrada retira.
    """
    llamadas = []
    import modulos.M4_control as M4
    original = M4.brentq
    M4.brentq = lambda *a, **k: llamadas.append(a) or original(*a, **k)
    try:
        tirante_critico(6.0, _marco())
    finally:
        M4.brentq = original
    assert llamadas == []


# ===========================================================================
# 4-bis - Las guardias de aritmetica, cada una con su par MEDIDO
# ===========================================================================

def test_el_cuadrado_del_caudal_por_unidad_de_ancho_que_no_cabe():
    """q >= 1.3407807929942597e+154 hace desbordar `q ** 2`."""
    m = SeccionRectangular(2.00, 1.50)
    with pytest.raises(LimiteNumericoError) as exc:
        tirante_critico(2.6815615859885194e+154, m)
    assert "no cabe en doble precision" in str(exc.value)
    assert "B = 2.0" in str(exc.value)      # nombra al PAR, no a un dato solo


def test_el_tirante_critico_que_sale_infinito():
    """
    `Q/B` puede dar `inf` SIN excepcion, y entonces y_c sale `inf`: un informe
    entero de diagnosticos sobre algo que no es un numero (SIS-G-01).
    """
    m = SeccionRectangular(1e-5, 1.50)
    with pytest.raises(LimiteNumericoError) as exc:
        tirante_critico(1e308, m)
    assert "no es un numero finito" in str(exc.value)


def test_el_tirante_critico_que_se_anula():
    """q <= 4.715183354107886e-162 cancela q^2/g a 0.0 exacto."""
    m = SeccionRectangular(2.00, 1.50)
    with pytest.raises(LimiteNumericoError) as exc:
        tirante_critico(4.715183354107886e-162 * 2.00, m)
    assert "se cancela entero" in str(exc.value)
    # Y el primer caudal que SI deja tirante positivo no lanza nada.
    assert tirante_critico(4.715183354107887e-162 * 2.00, m).y_c > 0


def test_el_area_que_se_anula_con_un_tirante_positivo():
    """
    LA CUARTA, que la seccion no puede guardar sola y guarda M4: con
    B = Q = 5e-324 el tirante critico vale 0.4671363512679737 m -- positivo --
    y el area B*y_c se anula en doble precision.
    """
    m = SeccionRectangular(5e-324, 1.50)
    with pytest.raises(LimiteNumericoError) as exc:
        tirante_critico(5e-324, m)
    assert "el area de la seccion a ese tirante se anula" in str(exc.value)


def test_las_dos_dimensiones_del_marco_se_validan_con_su_propio_nombre():
    """
    ANOTACION A-4 DE §16.4, cerrada: el nombre del dato lo pone la seccion.
    Un marco no tiene diametro; tiene B y H, y su mensaje lo dice.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        SeccionRectangular(0.0, 1.50).exigir_dimensiones_positivas()
    assert exc.value.campo == "B"
    assert "ancho interior del marco" in str(exc.value)

    with pytest.raises(DatoInvalidoError) as exc:
        SeccionRectangular(2.00, -1.0).exigir_dimensiones_positivas()
    assert exc.value.campo == "H"
    assert "altura interior del marco" in str(exc.value)

    # La circular sigue diciendo lo de siempre, letra por letra: es lo que
    # mantiene quieta la rama de error de la linea base.
    with pytest.raises(DatoInvalidoError) as exc:
        SeccionCircular(-0.90).exigir_dimensiones_positivas()
    assert exc.value.campo == "D"
    assert "el diametro debe ser positivo" in str(exc.value)


def test_la_condicion_esta_escrita_en_positivo_y_negada():
    """
    Plantilla de MAT-D13. Con `<= 0` un NaN se colaba -- es falso frente a los
    dos operadores -- y llegaba hasta Brent, que revienta fuera de
    `ErrorProyecto`. Es la tercera anotacion que C1 dejo abierta.
    """
    for seccion in (SeccionCircular(float("nan")),
                    SeccionRectangular(float("nan"), 1.50),
                    SeccionRectangular(2.00, float("nan"))):
        with pytest.raises(DatoInvalidoError):
            seccion.exigir_dimensiones_positivas()


# ===========================================================================
# 5 - Control de entrada por las dos formas, y control de salida
# ===========================================================================

def test_caudal_adimensional_del_marco_no_usa_diametro_equivalente():
    """
    q* = Ku*Q / (A_llena * altura^0.5), con `altura` = H y A_llena = B*H
    (regla vinculante #4). No hay diametro equivalente en ningun sitio.
    """
    m = SeccionRectangular(CP5R["B"], CP5R["H"])
    esperado = KU_SI * CP5R["Q"] / (CP5R["A_llena_esperada"]
                                    * math.sqrt(CP5R["H"]))
    assert caudal_adimensional(CP5R["Q"], m) == pytest.approx(
        CP5R["q_estrella_esperado"], abs=CP5R["tolerancia"])
    assert esperado == pytest.approx(CP5R["q_estrella_esperado"],
                                     abs=CP5R["tolerancia"])


@pytest.mark.parametrize("clave", ("forma_1", "forma_2"))
def test_control_de_entrada_sobre_el_marco_por_las_dos_formas(clave):
    """
    LAS DOS CARTAS SON DE CAJON (regla vinculante #5: no se cruzan
    geometrias), y cual ecuacion aplica lo fija la columna «Equation Form».
    Con q* = 2.957 la rama es la no sumergida en las dos, o sea la (A.1) pura
    frente a la (A.2) pura.
    """
    caso = CP5R[clave]
    m = SeccionRectangular(CP5R["B"], CP5R["H"])
    hds5 = ConstantesHDS5.desde_dict(HDS5_INLET[caso["carta"]])
    assert hds5.forma == caso["forma"]
    entrada = control_entrada(CP5R["Q"], m, CP5R["S"], hds5)
    assert entrada.regimen.value == CP5R["zona"]
    assert entrada.HW == pytest.approx(caso["HW_esperado"],
                                       abs=CP5R["tolerancia"])
    assert entrada.HW / CP5R["H"] == pytest.approx(
        caso["hw_sobre_D_esperado"], abs=CP5R["tolerancia"])


def test_la_forma_1_del_marco_lleva_H_c_sobre_D_y_la_forma_2_no():
    """
    La diferencia entre las dos, medida sobre el MISMO punto y con las dos
    cartas de cajon: la (A.1) arranca de H_c/D y corrige por pendiente; la
    (A.2) no lleva ninguno de los dos terminos.
    """
    m = SeccionRectangular(CP5R["B"], CP5R["H"])
    critico = tirante_critico(CP5R["Q"], m)
    assert critico.H_c == pytest.approx(CP5R["H_c_esperado"],
                                        abs=CP5R["tolerancia"])
    f1, f2 = CP5R["forma_1"], CP5R["forma_2"]
    reconstruida = (CP5R["H_c_sobre_D_esperado"] + f1["termino_directo"]
                    + f1["Ks"] * CP5R["S"])
    assert reconstruida == pytest.approx(f1["hw_sobre_D_esperado"],
                                         abs=CP5R["tolerancia"])
    assert f2["hw_sobre_D_esperado"] == pytest.approx(
        f2["K"] * CP5R["q_estrella_esperado"] ** f2["M"],
        abs=CP5R["tolerancia"])


def test_control_de_salida_sobre_el_marco():
    """
    Misma ecuacion que CP-8 y misma constante SI; lo que cambia es de donde
    sale la R -- B*H/(2(B+H)) y no D/4 --, y ese es el punto.
    """
    m = SeccionRectangular(CP8R["B"], CP8R["H"])
    critico = tirante_critico(CP8R["Q"], m)
    salida = control_salida(CP8R["Q"], m, CP8R["S"], CP8R["L"], CP8R["TW"],
                            CP8R["n"], ke=CP8R["ke"], critico=critico)
    tol = CP8R["tolerancia"]
    assert salida.H == pytest.approx(CP8R["H_esperado_con_K_SI"], abs=tol)
    assert salida.h_o == pytest.approx(CP8R["h_o_esperado"], abs=tol)
    assert salida.HW == pytest.approx(CP8R["HW_salida_esperado"], abs=tol)
    # El 29 imperial daria un 6.5 % mas: es el error que CP-8 existe para
    # atrapar, y no cambia al cambiar de forma.
    assert CP8R["H_con_29_incorrecto"] > CP8R["H_esperado_con_K_SI"]


# ===========================================================================
# 6 - Los CP5D_* de C3, repetidos sobre la seccion que les corresponde
# ===========================================================================

def test_los_casos_de_forma_2_dan_el_mismo_numero_sobre_la_rectangular():
    """
    C3 dejo escrito que estos casos «se repiten sobre la seccion que les
    corresponde; el numero de la ecuacion no cambia, porque la ecuacion no
    mira la forma: mira q*, K y M». COMPROBADO, no supuesto: se construye el
    q* del caso con un marco de verdad y se contrasta el HW/D contra el mismo
    dorado que C3 calculo a mano.

    La carta es la 9 escala 1, DE CAJON, de modo que aqui la pareja
    carta/seccion es ademas la correcta -- en C3 era una sonda de la ecuacion
    sobre una circular, que el num. A.3 no admitiria como diseño --.
    """
    hds5 = ConstantesHDS5(K=CP5D_FORMA2["K"], M=CP5D_FORMA2["M"],
                          c=CP5D_FORMA2["c"], Y=CP5D_FORMA2["Y"],
                          Ks=CP5D_FORMA2["Ks"], forma=CP5D_FORMA2["forma"])
    tol = CP5D_FORMA2["no_sumergido"]["tolerancia"]
    for rama in ("no_sumergido", "sumergido", "transicion"):
        caso = CP5D_FORMA2[rama]
        # El marco cuya altura y area llena producen EXACTAMENTE ese q*: se
        # despeja B de q* = Ku*Q/(B*H*sqrt(H)) con H y Q fijos, en vez de
        # tantear. Asi el caso viaja entero a la otra forma sin retocar el
        # dorado.
        H, Q = 1.50, 6.00
        B = KU_SI * Q / (caso["q_estrella"] * H * math.sqrt(H))
        m = SeccionRectangular(B, H)
        assert caudal_adimensional(Q, m) == pytest.approx(
            caso["q_estrella"], abs=CP5D_FORMA2["tolerancia_identidad"])
        entrada = control_entrada(Q, m, caso["S"], hds5)
        assert entrada.HW / H == pytest.approx(
            caso["hw_sobre_D_esperado"], abs=tol)


def test_la_transicion_no_monotona_tambien_en_carta_de_cajon_y_marco():
    """
    PUNTO 8 DEL PROMPT DE C4, con el numero delante. La propiedad que C3
    declaro sobre la Carta 9 evaluada en una circular se repite donde
    corresponde -- carta de cajon y seccion rectangular --, y ademas se barren
    las DOCE cartas de cajon con Forma 2 para quedarse con la peor.

    NO MUERDE EN ESTE PROYECTO: la pendiente mas alta del expediente de prueba
    es 0.010 m/m y el umbral mas bajo de las doce es 0.215192, veintiuna veces
    mayor. Pero NO esta excluida por ninguna guardia -- `dominios.S_CAUCE_MAX`
    admite hasta 1.0 --, y por eso queda fijada aqui en vez de darse por
    descartada de vista.
    """
    caso = CP5DR_TRANSICION_CAJON
    tol = caso["tolerancia"]
    hds5 = ConstantesHDS5.desde_dict(HDS5_INLET[caso["carta"]])
    assert hds5.forma == caso["forma"]

    # El umbral, rehecho desde la formula con las constantes de la carta.
    umbral = (hds5.c * 4.0 ** 2 + hds5.Y - hds5.K * 3.5 ** hds5.M) / abs(hds5.Ks)
    assert umbral == pytest.approx(caso["S_umbral"], abs=tol)

    # Y el barrido de las doce, que es lo que hace que el numero sea el PEOR y
    # no uno cualquiera.
    de_cajon = {k: v for k, v in HDS5_INLET.items() if k.startswith("cajon")}
    forma_2 = {k: v for k, v in de_cajon.items() if v["forma"] == 2}
    assert len(forma_2) == caso["cartas_cajon_forma_2"]
    assert len(de_cajon) - len(forma_2) == caso["cartas_cajon_forma_1"]
    umbrales = [(v["c"] * 4.0 ** 2 + v["Y"] - v["K"] * 3.5 ** v["M"])
                / abs(v["Ks"]) for v in forma_2.values()]
    assert min(umbrales) == pytest.approx(
        caso["S_umbral_minimo_de_las_doce"], abs=tol)
    assert max(umbrales) == pytest.approx(
        caso["S_umbral_maximo_de_las_doce"], abs=tol)

    # La propiedad, sobre el marco: por encima del umbral la recta BAJA.
    m = SeccionRectangular(caso["B"], caso["H"])
    hw_35 = hds5.K * 3.5 ** hds5.M * caso["H"]
    hw_40 = (hds5.c * 4.0 ** 2 + hds5.Y + hds5.Ks * caso["S_ensayada"]) * caso["H"]
    assert hw_35 == pytest.approx(caso["HW_en_q_3_5_m"], abs=tol)
    assert hw_40 == pytest.approx(caso["HW_en_q_4_0_m"], abs=tol)
    assert (hw_40 - hw_35) * 1000 == pytest.approx(
        caso["delta_mm"], abs=caso["tolerancia_mm"])
    assert caso["delta_mm"] < 0

    # Y por debajo del umbral crece, que es lo esperable.
    hw_40_baja = (hds5.c * 4.0 ** 2 + hds5.Y
                  + hds5.Ks * caso["S_baja"]) * caso["H"]
    assert (hw_40_baja - hw_35) * 1000 == pytest.approx(
        caso["delta_mm_con_S_baja"], abs=caso["tolerancia_mm"])

    # La pendiente del expediente esta MUY por debajo, y se dice con el numero.
    assert caso["S_maxima_del_expediente"] * 21 < caso["S_umbral_minimo_de_las_doce"]
    # ...pero el dominio la admite, de modo que no esta excluida por guardia.
    assert caso["S_maxima_admitida_por_dominios"] > caso["S_umbral_maximo_de_las_doce"]
    assert m.altura == caso["H"]


# ===========================================================================
# 7 - La traza de memoria de los pasos nuevos
# ===========================================================================

def _pasos_del_marco(carta="cajon_concreto_aleta_45_d043"):
    m = SeccionRectangular(CP5R["B"], CP5R["H"])
    material = _material(carta=carta, n_min=CP2R["n_min"],
                         n_max=CP2R["n_max"])
    normal = resolver_manning(seccion=m, Q=CP5R["Q"], S=CP5R["S"],
                              material=material)
    critico = tirante_critico(CP5R["Q"], m)
    entrada = control_entrada(CP5R["Q"], m, CP5R["S"], material.hds5, critico)
    salida = control_salida(CP5R["Q"], m, CP5R["S"], CP8R["L"], CP8R["TW"],
                            material.n_para_capacidad, critico=critico)
    gobierna_salida = salida.HW > entrada.HW
    return _pasos_hidraulicos(
        seccion=m, Q=CP5R["Q"], S=CP5R["S"], L=CP8R["L"], TW=CP8R["TW"],
        material=material, normal=normal, critico=critico, entrada=entrada,
        salida=salida,
        control=(ControlGobernante.SALIDA if gobierna_salida
                 else ControlGobernante.ENTRADA),
        gobierna_salida=gobierna_salida)


def _paso(pasos, fundamento):
    return next(p for p in pasos if p.fundamento_id == fundamento)


def test_el_paso_de_geometria_publica_las_formulas_de_la_forma():
    """
    F4.SECCION. La memoria tiene que decir COMO se calculan A, P y R, porque
    el num. 4.1.1.3.6 no lo dice: define las tres variables y no fija ninguna
    forma. Con un marco la frase de la circular ademas seria falsa.
    """
    paso = _paso(_pasos_del_marco(), "F4.SECCION")
    assert paso.formula == "A = B*y, P = B + 2y, R = A/P, con y el tirante"
    assert paso.formula_cita_id == "MC_HHD.4.1.1.3.6"
    simbolos = [mag.simbolo for mag in paso.sustitucion]
    assert simbolos == ["B", "H", "y", "A", "P"]
    assert paso.resultado.simbolo == "R"

    # Y la circular publica LA SUYA, no una generica.
    circular = _paso(_pasos_circulares(), "F4.SECCION")
    assert "theta" in circular.formula
    assert [mag.simbolo for mag in circular.sustitucion] == ["D", "y", "A", "P"]


def _pasos_circulares():
    c = SeccionCircular(0.90)
    material = _material()
    normal = resolver_manning(seccion=c, Q=0.30, S=0.005, material=material)
    critico = tirante_critico(0.30, c)
    entrada = control_entrada(0.30, c, 0.005, material.hds5, critico)
    salida = control_salida(0.30, c, 0.005, 20.0, 0.30,
                            material.n_para_capacidad, critico=critico)
    return _pasos_hidraulicos(
        seccion=c, Q=0.30, S=0.005, L=20.0, TW=0.30, material=material,
        normal=normal, critico=critico, entrada=entrada, salida=salida,
        control=ControlGobernante.ENTRADA, gobierna_salida=False)


def test_el_paso_del_critico_dice_por_que_via_se_resolvio():
    """
    Imprimir «resuelta con Brent» sobre un numero que salio de una formula
    cerrada deja al revisor sin poder rehacerlo. Es el mismo defecto que C3
    tuvo que corregir en el paso de la Forma 2, mudado a la otra pieza.
    """
    del_marco = _paso(_pasos_del_marco(), "F4.YC_RECT")
    assert "solucion CERRADA" in del_marco.formula
    assert "sin Brent" in del_marco.formula
    assert "T" in [mag.simbolo for mag in del_marco.sustitucion]

    de_la_circular = _paso(_pasos_circulares(), "F4.YC_RECT")
    assert "Brent" in de_la_circular.formula
    assert "CERRADA" not in de_la_circular.formula
    assert "T" not in [mag.simbolo for mag in de_la_circular.sustitucion]


def test_el_paso_del_critico_no_toma_prestado_el_fundamento_de_los_controles():
    """
    `F4.CONTROL` describe OTRO paso -- «Carga a la entrada HW por los dos
    controles del HDS-5» -- y el critico lo tomaba prestado porque no habia
    uno propio. Ahora lo hay, y esta comprobacion impide que vuelva.
    """
    for pasos in (_pasos_del_marco(), _pasos_circulares()):
        critico = [p for p in pasos if p.codigo == "4.2.1"]
        assert len(critico) == 1
        assert critico[0].fundamento_id == "F4.YC_RECT"


def test_la_sustitucion_de_los_pasos_nombra_las_dimensiones_de_la_forma():
    """
    Un marco se define con DOS numeros y un tubo con uno: la sustitucion no
    puede cablear ni cuantos son ni como se llaman. Es lo que hacia
    `Magnitud("D", ...)`, y con un marco habria impreso «D» sobre una seccion
    que no tiene diametro.
    """
    for paso in _pasos_del_marco():
        if paso.codigo in ("4.1", "4.2.1"):
            simbolos = [mag.simbolo for mag in paso.sustitucion]
            assert "B" in simbolos and "H" in simbolos
            assert "D" not in simbolos


# ===========================================================================
# 8 - Que las dos implementaciones sean SUSTITUIBLES, y no de palabra
# ===========================================================================

def test_las_dos_secciones_implementan_el_protocolo_entero():
    """
    NADIE LO COMPROBABA, y el `Protocol` no lo comprueba solo: no lleva
    `@runtime_checkable` y, aunque lo llevara, `isinstance` contra un Protocol
    mira los NOMBRES y no las firmas. Una erratа en el nombre de un metodo
    --`geometria_em` por `geometria_en`-- daria una clase que funciona por los
    caminos que los tests recorren y revienta por el primero que no.

    Lo que se comprueba es la sustituibilidad: MISMOS miembros publicos, y con
    la MISMA firma. Es lo que hace que M3 y M4 puedan quedarse ciegos a la
    forma; sin ello, «ciegos» es una intencion, no una propiedad.
    """
    import inspect
    from modelos import Seccion

    del_protocolo = {n for n in vars(Seccion)
                     if not n.startswith("_")}
    assert del_protocolo, "el protocolo se quedo sin miembros publicos"

    for implementacion in (SeccionCircular(0.90), SeccionRectangular(2.0, 1.5)):
        clase = type(implementacion)
        faltan = del_protocolo - set(dir(clase))
        assert not faltan, f"{clase.__name__} no implementa {sorted(faltan)}"

        for nombre in sorted(del_protocolo):
            del_p = getattr(Seccion, nombre)
            del_i = getattr(clase, nombre)
            # Las propiedades se comparan como propiedades; los metodos, por
            # firma. Confundir las dos es la otra mitad del defecto: una
            # `altura` que en una forma es propiedad y en otra metodo obliga a
            # quien la consume a saber cual tiene delante.
            assert isinstance(del_p, property) == isinstance(del_i, property), (
                f"{clase.__name__}.{nombre}: una es propiedad y la otra no")
            if isinstance(del_p, property):
                continue
            assert (inspect.signature(del_p).parameters.keys()
                    == inspect.signature(del_i).parameters.keys()), (
                f"{clase.__name__}.{nombre} no tiene la firma del protocolo")
