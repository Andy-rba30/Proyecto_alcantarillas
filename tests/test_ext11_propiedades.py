"""
tests/test_ext11_propiedades.py
===============================
Las SIETE propiedades de EXT-11 (propuesta 4 del dictamen de la auditoria
externa del 2026-09-19, prompt EXT-11 de
`docs/planes_mejora/07_CADENA_PROMPTS_EXT.md`): los invariantes del motor
hidraulico que hasta aqui no defendia nadie mas que la linea base de la
Familia C, que es un oraculo copiado de la salida del codigo (PC-18).

POR QUE `pytest.parametrize` SOBRE MALLAS Y NO `hypothesis`. El prompt manda
consultar antes de sumar `hypothesis` y `mutmut` como dependencias de TEST
(regla de dependencias de CLAUDE.md) y, si no se aprueban, escribir las
propiedades con `parametrize` sobre mallas. La consulta no obtuvo respuesta
en la sesion, y la regla es que sin respuesta no se suma nada: las mallas de
abajo son la via aprobada por defecto. Lo que se pierde es la busqueda
aleatoria de contraejemplos y el encogimiento; lo que se gana es una malla
determinista que se lee entera y que la mutacion (`tests/apoyo/mutacion.py`)
puede correr en segundos. La decision esta en la ficha EXT-11-01 de
`docs/decisiones_diferidas.md`.

UNA PROPIEDAD NO ES UN DORADO. Ninguno de estos tests conoce un numero
esperado: cada uno afirma una relacion entre dos salidas del codigo (o entre
una salida y una entrada) que la fuente hace obligatoria, y la afirma sobre
toda la malla. Por eso ninguno se escribio en rojo con `xfail`: son
invariantes que el motor ya cumplia y que ningun test defendia. Se midieron
en verde antes de tocar nada, y su valor esta en lo que MATAN: la mutacion
medida en EXT-11 sobre M3-M5/MD dice cuales mutantes sobreviven solo a la
linea base y mueren aqui.

Las siete, con la fuente de cada una:

  P1  Q = V_sedimentacion * A, en circular y en rectangular. `V_sedimentacion`
      sale de la MISMA expresion de Manning y del MISMO n (n_max) con que
      Brent resolvio el tirante (Sec. 4.1, num. 4.1.1.3.6 ec. 47), de modo
      que V*A tiene que devolver el Q de entrada. `V_erosion` (n_min) NO:
      `test_M3_hidraulica` ya fija esa asimetria en un solo punto.
  P2  Q_total = N * Q_celda A TRAVES de MD -> M4 (regla vinculante #3,
      HDS-5 num. 5.4.3): lo que llega al `ResultadoHidraulico` desde el
      bucle de diseño reparte igual que `M4.caudal_por_celda`.
  P3  V_erosion >= V_sedimentacion, estricta cuando n_min < n_max: misma R,
      n menor, velocidad mayor.
  P4  Continuidad de HW en q* = 3.5 y 4.0 y LINEALIDAD de la recta de
      transicion (EXT-M-04), en las dos formas de la ec. no sumergida y en
      las dos geometrias; y la recta es exactamente
      HW_lo + peso * (HW_hi - HW_lo) con los extremos que M4 publica.
  P5  Monotonia de HW(Q) bajo control de entrada con cartas de Forma 1: mas
      caudal, mas carga, en las tres ramas y en sus empalmes.
  P6  `tirante_normal` devuelve None para Q >= Q_lleno y una geometria para
      Q < Q_lleno, en las dos formas (PC-06).
  P7  HW(N=3) != HW(N=1) para el mismo Q total (el reparto MUEVE la carga), y
      HW(N, N*Q) == HW(1, Q): con N celdas iguales cada barril ve Q.

Las tolerancias van nombradas aqui arriba con su razon, como manda
`tests/apoyo/aproximacion.py`.
"""

import math

import pytest

from src.constantes_normativas import (KU_SI, K_MANNING_SI, Q_LIM_NO_SUMERGIDO,
                                       Q_LIM_SUMERGIDO)
from src.modelos import (ConstantesHDS5, FormaSeccion, RegimenEntrada,
                         SeccionCircular, SeccionRectangular, TipoMaterial)
from src.modulos import MD
from src.modulos.M2_material import catalogo
from src.modulos.M3_hidraulica import resolver_manning, tirante_normal
from src.modulos.M4_control import (caudal_por_celda, control_entrada,
                                    resolver_control)
from src.tolerancias import TOL_UMBRAL_NORMATIVO
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.fixtures.casos_patron import CP5D_FORMA2
from tests.test_MD import _punto, _todo_cumple
from tests.test_ext2_multicelda_transicion import CAJON_N3

# ---------------------------------------------------------------------------
# Tolerancias, nombradas y con su razon
# ---------------------------------------------------------------------------
# Q = V*A recorre Brent: el llenado resuelto reproduce Q hasta `TOL_BRENT`
# (1e-10 en el parametro de llenado), y el producto V*A hereda ese ruido
# amplificado por dQ/dllenado. MEDIDO sobre la malla entera (10 secciones x
# 3 materiales o el marco x 4 pendientes x 6 fracciones): la peor desviacion
# relativa es 3.6e-11 (marco 1.00 x 1.00, S = 0.01, 0.9 Q_lleno). Se fija
# treinta veces por encima de lo medido y muy por debajo de cualquier
# diferencia que un n distinto produciria (n_max/n_min - 1 >= 0.27).
REL_IDENTIDAD_MANNING = 1e-9
# Continuidad en los bordes de la ventana de transicion: la misma que
# `test_ext2` (epsilon de 1e-7 en q*, un HW en metros).
TOL_CONTINUIDAD_M = 1e-6
# Segundas diferencias de una recta evaluada en punto flotante sobre HW de
# hasta ~3 m: el ruido es de ~1e-15; se fija en 1e-11 para las secciones
# grandes de la malla (CP-5T usa 1e-12 solo para D = 0.90).
TOL_LINEALIDAD_M = 1e-11
# La recta reconstruida desde los extremos publicados tiene que ser el MISMO
# numero que M4 devuelve: una suma y un producto, ruido de 1 ulp.
REL_RECTA_PUBLICADA = 1e-12
# Dos cargas que deben DIFERIR (P7): si difieren en menos de esto son la misma.
REL_DISTINCION = 1e-6
# Epsilon en q* con que se entra a la ventana por cada borde.
EPSILON_Q_ESTRELLA = 1e-7

# ---------------------------------------------------------------------------
# Las mallas
# ---------------------------------------------------------------------------
DIAMETROS_M = (0.90, 1.05, 1.20, 1.50, 1.80, 2.40)
MARCOS_B_H = ((1.00, 1.00), (1.50, 1.00), (2.00, 1.50), (2.50, 2.00))
PENDIENTES = (0.002, 0.005, 0.010, 0.030)
# Fracciones de Q_lleno con tirante normal (P1, P3, P6) y sin el (P6).
FRACCIONES_CON_TIRANTE = (0.10, 0.30, 0.50, 0.70, 0.90, 0.99)
FRACCIONES_A_PRESION = (1.0, 1.000001, 1.10, 1.50, 2.00)
# Rugosidades para P6, que no pasa por un material: las dos del concreto y
# el n_max de la fila del TMC.
RUGOSIDADES = (0.010, 0.013, 0.030)
MATERIALES_CIRCULARES = (TipoMaterial.CONCRETO_REFORZADO, TipoMaterial.TMC,
                         TipoMaterial.HDPE)
# El marco de la aceptacion de EXT-2, con N variable.
N_CELDAS = (1, 2, 3, 4)
CAUDALES_TOTALES_M3S = (1.5, 3.0, 6.0)
CAUDALES_POR_CELDA_M3S = (1.0, 2.0)
S_MARCO, L_MARCO, TW_LIBRE = 0.004, 24.0, 0.0
# Barrido de q* para P4 y P5.
PASO_Q_ESTRELLA_TRANSICION = 0.05
Q_ESTRELLA_MONOTONIA = tuple(x / 10 for x in range(2, 60))   # 0.2 ... 5.9


def _Q_de(q_estrella, seccion):
    """El Q que produce ese q* en la seccion (inversa de `caudal_adimensional`)."""
    return q_estrella * seccion.area_llena * math.sqrt(seccion.altura) / KU_SI


def _Q_lleno(seccion, n, S):
    """La misma expresion de `M3.tirante_normal`, escrita aqui como oraculo."""
    return ((K_MANNING_SI / n) * seccion.area_llena
            * seccion.radio_hidraulico_lleno ** (2 / 3) * S ** (1 / 2))


def _secciones():
    return ([SeccionCircular(D) for D in DIAMETROS_M]
            + [SeccionRectangular(B, H) for B, H in MARCOS_B_H])


def _id_seccion(sec):
    if isinstance(sec, SeccionCircular):
        return f"D{sec.D:.2f}"
    return f"B{sec.B:.2f}xH{sec.H:.2f}"


@pytest.fixture
def marco():
    """El material del cajon, con los criterios de EXT-2 declarados."""
    with declarados(CAJON_N3):
        yield catalogo(TipoMaterial.CONCRETO_REFORZADO,
                       forma=FormaSeccion.RECTANGULAR)


def _carta_forma_2():
    d = CP5D_FORMA2
    return ConstantesHDS5(K=d["K"], M=d["M"], c=d["c"], Y=d["Y"], Ks=d["Ks"],
                          forma=d["forma"])


# ===========================================================================
# P1 y P3 - Q = V_sedimentacion * A ; V_erosion >= V_sedimentacion
# ===========================================================================

@pytest.mark.parametrize("tipo", MATERIALES_CIRCULARES)
@pytest.mark.parametrize("D", DIAMETROS_M)
@pytest.mark.parametrize("S", PENDIENTES)
@pytest.mark.parametrize("fraccion", FRACCIONES_CON_TIRANTE)
def test_P1_P3_circular_Q_es_V_sedimentacion_por_A_y_V_erosion_no_es_menor(
        tipo, D, S, fraccion):
    material = catalogo(tipo)
    sec = SeccionCircular(D)
    Q = fraccion * _Q_lleno(sec, material.n_para_capacidad, S)
    r = resolver_manning(sec, Q, S, material)
    assert r is not None, "por debajo de Q_lleno tiene que haber tirante normal"
    # P1: la rama n_max reproduce el caudal que Brent resolvio.
    assert r.V_sedimentacion * r.geometria.A == pytest.approx(
        Q, rel=REL_IDENTIDAD_MANNING)
    # P3: misma R, n menor, velocidad mayor (o igual si el rango es un punto).
    assert r.V_erosion >= r.V_sedimentacion
    if material.n_min < material.n_max:
        assert r.V_erosion > r.V_sedimentacion
        assert r.V_erosion * r.geometria.A > Q


@pytest.mark.parametrize("B,H", MARCOS_B_H)
@pytest.mark.parametrize("S", PENDIENTES)
@pytest.mark.parametrize("fraccion", FRACCIONES_CON_TIRANTE)
def test_P1_P3_rectangular_Q_es_V_sedimentacion_por_A_y_V_erosion_no_es_menor(
        marco, B, H, S, fraccion):
    sec = SeccionRectangular(B, H)
    Q = fraccion * _Q_lleno(sec, marco.n_para_capacidad, S)
    r = resolver_manning(sec, Q, S, marco)
    assert r is not None
    assert r.V_sedimentacion * r.geometria.A == pytest.approx(
        Q, rel=REL_IDENTIDAD_MANNING)
    assert marco.n_min < marco.n_max, "la fila del cajon es un rango"
    assert r.V_erosion > r.V_sedimentacion


def test_P3_la_desigualdad_es_la_de_los_n_y_no_un_orden_de_campos():
    """
    Un mutante que intercambiara los dos n en `resolver_manning` invertiria
    la desigualdad en TODA la malla, pero un material con n_min == n_max la
    dejaria pasar: se comprueba que la desigualdad vale exactamente n_max/n_min.
    """
    c = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    sec = SeccionCircular(DIAMETROS_M[0])
    S = PENDIENTES[1]
    r = resolver_manning(sec, 0.5 * _Q_lleno(sec, c.n_max, S), S, c)
    assert r.V_erosion / r.V_sedimentacion == pytest.approx(
        c.n_max / c.n_min, rel=REL_TRANSPORTE)


# ===========================================================================
# P2 - Q_total = N * Q_celda a traves de MD -> M4
# ===========================================================================

def _disenar(marco, Q_total, n_celdas):
    """`MD.disenar_material` sobre el marco con N celdas declaradas."""
    with declarados({**CAJON_N3, "n_celdas_cajon": n_celdas}):
        material = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                            forma=FormaSeccion.RECTANGULAR)
        resultado, motivo = MD.disenar_material(
            _punto(), material, Q=Q_total, S=S_MARCO, L=L_MARCO,
            TW=TW_LIBRE, verificar=_todo_cumple)
    assert resultado is not None, motivo
    return resultado


@pytest.mark.parametrize("n_celdas", N_CELDAS)
@pytest.mark.parametrize("Q_total", CAUDALES_TOTALES_M3S)
def test_P2_el_bucle_de_diseno_reparte_Q_entre_N_y_lo_publica(
        marco, n_celdas, Q_total):
    r = _disenar(marco, Q_total, n_celdas).resultado_hidraulico
    assert r.numero_celdas == n_celdas
    assert r.Q == pytest.approx(Q_total, rel=REL_TRANSPORTE)
    assert r.Q_celda_m3s * r.numero_celdas == pytest.approx(
        Q_total, rel=REL_TRANSPORTE)
    # Y lo que M3 resolvio fue el caudal de la CELDA: el tirante normal del
    # resultado es el de Q/N sobre esa seccion, no el de Q.
    resultado = _disenar(marco, Q_total, n_celdas)
    de_la_celda = resolver_manning(resultado.seccion, Q_total / n_celdas,
                                   S_MARCO, marco)
    assert r.y_normal == pytest.approx(de_la_celda.geometria.y,
                                       rel=REL_TRANSPORTE)
    assert (r.V_sedimentacion * de_la_celda.geometria.A
            == pytest.approx(Q_total / n_celdas, rel=REL_IDENTIDAD_MANNING))


@pytest.mark.parametrize("n_celdas", N_CELDAS)
@pytest.mark.parametrize("Q_total", CAUDALES_TOTALES_M3S)
def test_P2_resolver_control_reparte_igual_que_caudal_por_celda(
        marco, n_celdas, Q_total):
    with declarados({**CAJON_N3, "n_celdas_cajon": n_celdas}):
        material = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                            forma=FormaSeccion.RECTANGULAR)
        Q_celda, N = caudal_por_celda(Q_total, material)
        r = resolver_control(SeccionRectangular(*MARCOS_B_H[2]), Q_total,
                             S_MARCO, L_MARCO, TW_LIBRE, material)
    assert N == n_celdas
    assert Q_celda * N == pytest.approx(Q_total, rel=REL_TRANSPORTE)
    assert r is not None
    assert r.Q_celda_m3s == pytest.approx(Q_celda, rel=REL_TRANSPORTE)
    assert r.numero_celdas == N


def test_P2_la_circular_no_reparte():
    c = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    for Q_total in CAUDALES_TOTALES_M3S:
        Q_celda, N = caudal_por_celda(Q_total, c)
        assert N == 1
        assert Q_celda == pytest.approx(Q_total, rel=REL_TRANSPORTE)


# ===========================================================================
# P4 - continuidad y linealidad de la transicion, en las dos formas
# ===========================================================================

CARTAS = {
    "forma_1_concreto": catalogo(TipoMaterial.CONCRETO_REFORZADO).hds5,
    "forma_2_carta_9": _carta_forma_2(),
}


@pytest.mark.parametrize("carta", sorted(CARTAS))
@pytest.mark.parametrize("sec", _secciones(), ids=_id_seccion)
@pytest.mark.parametrize("S", PENDIENTES)
def test_P4_la_carga_es_continua_en_los_dos_bordes_de_la_ventana(carta, sec, S):
    hds5 = CARTAS[carta]
    for limite, signo in ((Q_LIM_NO_SUMERGIDO, +1), (Q_LIM_SUMERGIDO, -1)):
        borde = control_entrada(Q=_Q_de(limite, sec), seccion=sec, S=S,
                                hds5=hds5)
        dentro = control_entrada(
            Q=_Q_de(limite + signo * EPSILON_Q_ESTRELLA, sec), seccion=sec,
            S=S, hds5=hds5)
        assert dentro.regimen is RegimenEntrada.TRANSICION
        # El borde mismo puede caer de un lado o del otro por el redondeo de
        # ida y vuelta Q -> q* (3.5000000000000004 medido en D = 1.50): lo
        # que se afirma es la continuidad del NUMERO, no la rama del borde.
        assert dentro.HW == pytest.approx(borde.HW, abs=TOL_CONTINUIDAD_M)


@pytest.mark.parametrize("carta", sorted(CARTAS))
@pytest.mark.parametrize("sec", _secciones(), ids=_id_seccion)
@pytest.mark.parametrize("S", PENDIENTES)
def test_P4_la_recta_es_una_recta_y_es_la_que_M4_publica(carta, sec, S):
    hds5 = CARTAS[carta]
    n = round((Q_LIM_SUMERGIDO - Q_LIM_NO_SUMERGIDO) / PASO_Q_ESTRELLA_TRANSICION)
    q_estrellas = [Q_LIM_NO_SUMERGIDO + i * PASO_Q_ESTRELLA_TRANSICION
                   for i in range(n + 1)]
    resultados = [control_entrada(Q=_Q_de(q, sec), seccion=sec, S=S, hds5=hds5)
                  for q in q_estrellas]
    hw = [r.HW for r in resultados]
    # Linealidad: segundas diferencias nulas en toda la ventana.
    segundas = [hw[i + 2] - 2 * hw[i + 1] + hw[i] for i in range(n - 1)]
    assert all(abs(d) < TOL_LINEALIDAD_M for d in segundas), segundas
    # Y la recta es la de los extremos publicados, con el peso publicado:
    # los extremos no dependen del q* real, solo el peso.
    interiores = [r for r in resultados
                  if r.regimen is RegimenEntrada.TRANSICION]
    assert interiores, "la malla tiene que caer dentro de la ventana"
    HW_lo = {r.transicion.HW_lo for r in interiores}
    HW_hi = {r.transicion.HW_hi for r in interiores}
    assert len(HW_lo) == 1 and len(HW_hi) == 1, "los extremos son fijos"
    for r in interiores:
        t = r.transicion
        assert r.HW == pytest.approx(t.HW_lo + t.peso * (t.HW_hi - t.HW_lo),
                                     rel=REL_RECTA_PUBLICADA)
        assert 0.0 < t.peso < 1.0
        assert t.Q_lo == pytest.approx(_Q_de(Q_LIM_NO_SUMERGIDO, sec),
                                       rel=REL_TRANSPORTE)
        if hds5.forma == 1:
            assert t.H_c_lo is not None and t.H_c_lo > 0
        else:
            assert t.H_c_lo is None


# ===========================================================================
# P5 - monotonia de HW(Q) bajo control de entrada, Forma 1
# ===========================================================================

@pytest.mark.parametrize("tipo", MATERIALES_CIRCULARES)
@pytest.mark.parametrize("sec", _secciones(), ids=_id_seccion)
@pytest.mark.parametrize("S", PENDIENTES)
def test_P5_mas_caudal_es_mas_carga_en_las_tres_ramas_y_sus_empalmes(
        tipo, sec, S):
    hds5 = catalogo(tipo).hds5
    assert hds5.forma == 1, "la propiedad se enuncia para cartas de Forma 1"
    hw = [control_entrada(Q=_Q_de(q, sec), seccion=sec, S=S, hds5=hds5).HW
          for q in Q_ESTRELLA_MONOTONIA]
    for anterior, siguiente, q in zip(hw, hw[1:], Q_ESTRELLA_MONOTONIA[1:]):
        assert siguiente > anterior, (
            f"HW bajo en q* = {q:.1f}: {anterior} -> {siguiente}")
    # Y la malla atraviesa las tres ramas, o la propiedad no dice lo que dice.
    regimenes = {control_entrada(Q=_Q_de(q, sec), seccion=sec, S=S,
                                 hds5=hds5).regimen
                 for q in (Q_ESTRELLA_MONOTONIA[0], 3.75,
                           Q_ESTRELLA_MONOTONIA[-1])}
    assert regimenes == set(RegimenEntrada)


# ===========================================================================
# P6 - tirante_normal = None para Q >= Q_lleno, en las dos formas
# ===========================================================================

@pytest.mark.parametrize("sec", _secciones(), ids=_id_seccion)
@pytest.mark.parametrize("n", RUGOSIDADES)
@pytest.mark.parametrize("S", PENDIENTES)
def test_P6_a_presion_no_hay_tirante_normal_y_bajo_Q_lleno_si(sec, n, S):
    Q_lleno = _Q_lleno(sec, n, S)
    for fraccion in FRACCIONES_A_PRESION:
        assert tirante_normal(sec, fraccion * Q_lleno, S, n) is None, (
            f"{_id_seccion(sec)}: con Q = {fraccion} Q_lleno hay tirante")
    for fraccion in FRACCIONES_CON_TIRANTE:
        g = tirante_normal(sec, fraccion * Q_lleno, S, n)
        assert g is not None, (
            f"{_id_seccion(sec)}: con Q = {fraccion} Q_lleno no hay tirante")
        assert 0.0 < g.y < sec.altura


# ===========================================================================
# P7 - HW(N=3) != HW(N=1); HW(N, N*Q) == HW(1, Q)
# ===========================================================================

@pytest.mark.parametrize("Q_total", CAUDALES_TOTALES_M3S)
def test_P7_el_reparto_mueve_las_dos_cargas(marco, Q_total):
    tres = _disenar(marco, Q_total, 3).resultado_hidraulico
    una = _disenar(marco, Q_total, 1).resultado_hidraulico
    assert tres.HW_entrada != pytest.approx(una.HW_entrada, rel=REL_DISTINCION)
    assert tres.HW_salida != pytest.approx(una.HW_salida, rel=REL_DISTINCION)
    assert tres.HW_entrada < una.HW_entrada
    assert tres.HW_salida < una.HW_salida


@pytest.mark.parametrize("n_celdas", N_CELDAS[1:])
@pytest.mark.parametrize("Q_celda", CAUDALES_POR_CELDA_M3S)
def test_P7_N_celdas_con_N_veces_Q_es_una_celda_con_Q(marco, n_celdas, Q_celda):
    """La identidad del dictamen: N = 3 / Q = 9 equivale a N = 1 / Q = 3."""
    varias = _disenar(marco, n_celdas * Q_celda, n_celdas).resultado_hidraulico
    una = _disenar(marco, Q_celda, 1).resultado_hidraulico
    for campo in ("HW_entrada", "HW_salida", "y_normal", "y_critico",
                  "V_erosion", "V_sedimentacion", "control_gobernante"):
        assert getattr(varias, campo) == getattr(una, campo), campo  # float-exacto: el mismo camino con el mismo Q_celda da los mismos bits
    assert varias.Q_celda_m3s == pytest.approx(una.Q_celda_m3s,
                                                rel=REL_TRANSPORTE)


# ===========================================================================
# Lo que la MUTACION enseño (EXT-11): mutantes que sobrevivian a toda la
# suite objetivo y que no eran equivalentes. Cada test de aqui mata uno.
# ===========================================================================

@pytest.mark.parametrize("tipo,clave_v_max", [(TipoMaterial.HDPE, "v_max_hdpe"),
                                              (TipoMaterial.TMC, "v_max_tmc")])
def test_V3_juzga_la_estimacion_ALTA_y_no_la_baja(tipo, clave_v_max):
    """
    Siete mutantes `V_erosion -> V_sedimentacion` en `v3_velocidad_maxima` y
    `_paso_v3` sobrevivian: ningun test tenia un techo ENTRE las dos
    velocidades. Con v_max entre V_sedimentacion (n_max) y V_erosion (n_min),
    V3 tiene que NO cumplir, y el numero que publica es el de n_min: es el
    lado conservador contra un techo (MAT-D1).
    """
    from src.modulos.M5_verificaciones import v3_velocidad_maxima
    material = catalogo(tipo)
    sec = SeccionCircular(DIAMETROS_M[0])
    S = PENDIENTES[1]
    normal = resolver_manning(sec, 0.5 * _Q_lleno(sec, material.n_max, S), S, material)
    assert normal.V_sedimentacion < normal.V_erosion
    techo = (normal.V_sedimentacion + normal.V_erosion) / 2
    r = resolver_control(sec, normal.geometria.A * normal.V_sedimentacion, S,
                         L_MARCO, TW_LIBRE, material, normal=normal)
    with declarados({clave_v_max: techo}):
        v3 = v3_velocidad_maxima(material=material, resultado=r)
    assert not v3.cumple
    assert v3.valor_obtenido == pytest.approx(normal.V_erosion, rel=REL_TRANSPORTE)
    _el_paso_de_v3_publica_la_rama_alta(v3.paso, normal, techo)


def _el_paso_de_v3_publica_la_rama_alta(paso, normal, techo):
    """
    La sustitucion, el resultado y el MARGEN del paso llevan V_erosion: los
    mutantes `par_v` de `_paso_v3` (Magnitud de la sustitucion y margen) y el
    signo del margen sobrevivian a todo menos a la linea base.
    """
    assert paso.resultado.valor == pytest.approx(normal.V_erosion, rel=REL_TRANSPORTE)
    assert "V_erosion" in paso.resultado.simbolo
    sustituidas = {m.simbolo: m.valor for m in paso.sustitucion}
    assert "V_erosion" in sustituidas
    assert sustituidas["V_erosion"] == pytest.approx(normal.V_erosion, rel=REL_TRANSPORTE)
    assert "V_sedimentacion" not in sustituidas
    assert paso.veredicto.margen == pytest.approx(techo - normal.V_erosion,
                                                  rel=REL_TRANSPORTE)
    assert paso.veredicto.margen < 0


def test_V3_del_concreto_con_techo_bajado_tambien_juzga_la_estimacion_ALTA():
    from src.modulos.M5_verificaciones import (CRITERIO_V_MAX_CONCRETO,
                                               v3_velocidad_maxima)
    c = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    sec = SeccionCircular(DIAMETROS_M[0])
    S = PENDIENTES[3]
    normal = resolver_manning(sec, 0.5 * _Q_lleno(sec, c.n_max, S), S, c)
    techo = (normal.V_sedimentacion + normal.V_erosion) / 2
    assert min(c.v_max_tabla10) <= techo <= max(c.v_max_tabla10), (
        "el caso tiene que caer dentro de la ventana que el criterio admite")
    r = resolver_control(sec, normal.geometria.A * normal.V_sedimentacion, S,
                         L_MARCO, TW_LIBRE, c, normal=normal)
    with declarados({CRITERIO_V_MAX_CONCRETO: techo}):
        v3 = v3_velocidad_maxima(material=c, resultado=r)
    assert not v3.cumple
    assert v3.valor_obtenido == pytest.approx(normal.V_erosion, rel=REL_TRANSPORTE)
    _el_paso_de_v3_publica_la_rama_alta(v3.paso, normal, techo)


def test_un_caudal_nulo_es_dato_invalido_en_M3():
    """`Q > 0 -> Q >= 0` sobrevivia: nadie pedia el tirante de Q = 0."""
    from src.modelos import DatoInvalidoError
    with pytest.raises(DatoInvalidoError) as exc:
        tirante_normal(SeccionCircular(DIAMETROS_M[0]), 0.0, PENDIENTES[1],
                       RUGOSIDADES[1])
    assert exc.value.campo == "Q"


def test_un_par_de_manning_degenerado_es_un_rango_valido():
    """`n_min <= n_max -> n_min < n_max` sobrevivia: un rango de un punto vale."""
    from src.modulos.M2_material import _par_de_manning
    assert _par_de_manning("n_manning_hdpe", (0.013, 0.013)) == (0.013, 0.013)  # float-exacto: el par se transporta sin operar (float(x) de un float)


def test_ke_cero_es_una_embocadura_sin_perdida_y_se_admite():
    """`ke >= 0 -> ke > 0` sobrevivia: el cero que el docstring admite no se probaba."""
    from src.modulos.M4_control import _validar_ke
    assert _validar_ke(0.0, "ke_entrada") == 0.0  # float-exacto: el cero se transporta sin operar


# --- P8: los umbrales de M5 son INCLUSIVOS ---------------------------------
# Doce mutantes `<= -> <`, `>= -> >` y `+ TOL -> - TOL` sobre los umbrales
# de M5 sobrevivian a todo: ningun test ponia el valor EN el umbral. La
# lectura de la fuente es inclusiva («no menor que», «no debe exceder»),
# y la banda TOL_UMBRAL_NORMATIVO existe para que la igualdad en punto
# flotante caiga del lado del cumplimiento. Aqui se fija con los dobles de
# test_M5 en las verificaciones cuyo umbral es un escalar de entrada.

def test_P8_en_el_umbral_exacto_las_verificaciones_escalares_cumplen():
    from src.constantes_normativas import V_MIN, Y_SOBRE_D_MAX
    from src.modulos.M5_verificaciones import (v1_borde_libre,
                                               v2_velocidad_minima,
                                               v3_velocidad_maxima,
                                               v9_disponibilidad_diametro)
    from tests.test_M5_verificaciones import _punto as _punto_m5
    from tests.test_M5_verificaciones import _resultado
    c = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    D = DIAMETROS_M[0]
    assert v1_borde_libre(D=D, material=c, punto=_punto_m5(),
                          resultado=_resultado(y_normal=Y_SOBRE_D_MAX * D)).cumple
    assert v2_velocidad_minima(resultado=_resultado(V=V_MIN)).cumple
    assert not v2_velocidad_minima(
        resultado=_resultado(V=V_MIN - 2 * TOL_UMBRAL_NORMATIVO)).cumple
    hdpe = catalogo(TipoMaterial.HDPE)
    with declarados({"v_max_hdpe": 3.0}):
        assert v3_velocidad_maxima(material=hdpe,
                                   resultado=_resultado(V=3.0)).cumple
        assert not v3_velocidad_maxima(
            material=hdpe,
            resultado=_resultado(V=3.0 + 2 * TOL_UMBRAL_NORMATIVO)).cumple
    # El concreto, por sus DOS techos: el [N] de la Tabla N 10 y el criterio
    # opcional que lo baja. `v_max + TOL -> v_max - TOL` en esa rama
    # sobrevivia a todo porque el umbral exacto solo se probaba en HDPE.
    from src.modulos.M5_verificaciones import CRITERIO_V_MAX_CONCRETO
    techo_tabla = max(c.v_max_tabla10)
    assert v3_velocidad_maxima(material=c, resultado=_resultado(V=techo_tabla)).cumple
    assert not v3_velocidad_maxima(
        material=c, resultado=_resultado(V=techo_tabla + 2 * TOL_UMBRAL_NORMATIVO)).cumple
    with declarados({CRITERIO_V_MAX_CONCRETO: min(c.v_max_tabla10)}):
        bajado = min(c.v_max_tabla10)
        assert v3_velocidad_maxima(material=c, resultado=_resultado(V=bajado)).cumple
        assert not v3_velocidad_maxima(
            material=c, resultado=_resultado(V=bajado + 2 * TOL_UMBRAL_NORMATIVO)).cumple
    assert v9_disponibilidad_diametro(D=c.D_max, material=c).cumple
    assert not v9_disponibilidad_diametro(
        D=c.D_max + 2 * TOL_UMBRAL_NORMATIVO, material=c).cumple


# --- Guardias de entrada que ningun test tocaba -----------------------------

def test_las_guardias_del_receptor_trapecial_rechazan_lo_que_dicen_rechazar():
    """`P > 0`, `n > 0`, `S > 0` y `Q > 0` de la Sec. 1.3: en el borde, y no solo lejos."""
    from src.modelos import DatoInvalidoError, SeccionReceptor
    from src.modulos.M3_hidraulica import (caudal_manning_trapecial,
                                           tirante_normal_trapecial)
    # Una seccion pequeña pero real (P = 0.7 m) funciona: la guardia es
    # contra el perimetro NULO, no contra uno menor que 1 m.
    assert caudal_manning_trapecial(b=0.5, z=0.0, y=0.1, n=0.03, S=0.01) > 0
    with pytest.raises(DatoInvalidoError):
        caudal_manning_trapecial(b=0.0, z=0.0, y=0.0, n=0.03, S=0.01)
    buena = dict(b_m=1.0, z_HV=1.0, S=0.004, n=0.03, altura_total_m=1.0)
    assert tirante_normal_trapecial(Q=0.5, seccion=SeccionReceptor(**buena)) > 0
    for mala in ({**buena, "S": 0.0}, {**buena, "n": 0.0}):
        with pytest.raises(DatoInvalidoError):
            tirante_normal_trapecial(Q=0.5, seccion=SeccionReceptor(**mala))
    with pytest.raises(DatoInvalidoError):
        tirante_normal_trapecial(Q=0.0, seccion=SeccionReceptor(**buena))


def test_la_cota_de_agua_del_TW_es_el_fondo_de_la_salida_mas_el_tirante():
    """Tres `cota_fondo_salida + tw -> -` sobrevivian: nadie leia la cota."""
    from src.modelos import ViaDelTW
    from src.modulos.M3_hidraulica import tw_seccion_1_3
    cota_fondo = 41.30
    declarado = tw_seccion_1_3(punto=_punto(), cota_fondo_salida=cota_fondo,
                               tw_declarado=0.5)
    assert declarado.valor == pytest.approx(0.5, rel=REL_TRANSPORTE)
    assert declarado.cota_TW_msnm == pytest.approx(cota_fondo + 0.5,
                                                    rel=REL_TRANSPORTE)
    escenarios = tw_seccion_1_3(punto=_punto(), cota_fondo_salida=cota_fondo)
    assert escenarios.via is ViaDelTW.ESCENARIOS_ACOTADOS
    assert escenarios.cota_TW_msnm == pytest.approx(
        cota_fondo + escenarios.valor, rel=REL_TRANSPORTE)
    assert escenarios.cota_TW_msnm > cota_fondo


def test_el_par_de_manning_rechaza_lo_que_no_es_un_par_y_admite_el_vacio():
    from src.modelos import DatoInvalidoError
    from src.modulos.M2_material import _par_de_manning
    assert _par_de_manning("n_manning_hdpe", None) == (None, None)
    for malo in ("0.013", b"x", 0.013, (0.013,), (0.010, 0.013, 0.015),
                 ("a", "b"), (0.013, float("inf")), (0.013, True),
                 (0.014, 0.013)):
        with pytest.raises(DatoInvalidoError):
            _par_de_manning("n_manning_hdpe", malo)


def test_un_ke_que_no_es_numero_es_dato_invalido():
    from src.modelos import DatoInvalidoError
    from src.modulos.M4_control import _validar_ke
    for malo in ("texto", True, [1, 2], None, float("nan"), -0.1):
        with pytest.raises(DatoInvalidoError):
            _validar_ke(malo, "ke_entrada")


def test_la_progresion_que_repite_un_escalon_se_detiene_con_su_clave(marco):
    """`_mismo_escalon` y `_exigir_progreso` (EXT-A-03) no tenian ningun caso."""
    from src.modelos import DatoInvalidoError
    from src.modulos.MD import _exigir_progreso, _mismo_escalon
    circular = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    a, b = SeccionCircular(0.90), SeccionCircular(1.05)
    m, n = SeccionRectangular(2.0, 1.5), SeccionRectangular(2.5, 1.5)
    assert _mismo_escalon(a, SeccionCircular(0.90))
    assert not _mismo_escalon(a, b)
    assert _mismo_escalon(m, SeccionRectangular(2.0, 1.5))
    assert not _mismo_escalon(m, n)
    assert not _mismo_escalon(m, SeccionRectangular(2.0, 1.05))
    assert not _mismo_escalon(a, SeccionRectangular(0.9, 0.9)), (
        "una circular y un marco de la misma altura no son el mismo escalon")
    _exigir_progreso(circular, b, [a])          # avanza: no pasa nada
    _exigir_progreso(marco, n, [m])
    with pytest.raises(DatoInvalidoError) as exc:
        _exigir_progreso(circular, SeccionCircular(0.90), [a, b])
    assert exc.value.campo == "diametros_normalizados"
    with pytest.raises(DatoInvalidoError) as exc:
        _exigir_progreso(marco, SeccionRectangular(2.0, 1.5), [m])
    assert exc.value.campo == "secciones_cajon_normalizadas"


def test_el_tirante_publico_de_M3_es_el_de_la_geometria():
    from src.modulos.M3_hidraulica import geometria, tirante
    sec = SeccionCircular(DIAMETROS_M[0])
    llenado = sum(sec.bracket_llenado()) / 2
    assert tirante(sec, llenado) == geometria(sec, llenado).y  # float-exacto: es el mismo campo leido por dos caminos


def test_el_primer_metodo_no_evaluable_es_el_que_sale():
    from src.modelos import MetodoNoEvaluableError
    from src.modulos.MD import _exigir_metodo_evaluable
    uno = MetodoNoEvaluableError(que="V1", procedimiento="x", motivo="y")
    _exigir_metodo_evaluable([])
    with pytest.raises(MetodoNoEvaluableError) as exc:
        _exigir_metodo_evaluable([uno])
    assert exc.value is uno


# --- Segunda tanda de la mutacion (tras la corrida final, 46 supervivientes) --

def test_el_motivo_de_descarte_nombra_el_criterio_de_la_progresion_de_cada_forma(marco):
    """`is RECTANGULAR -> is not` en `_motivo_descarte` solo cambiaba la clave del texto."""
    from src.modulos.MD import _motivo_descarte
    circular = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    assert "D_max_catalogo" in _motivo_descarte(circular, "ultimo motivo")
    assert "secciones_cajon_normalizadas" in _motivo_descarte(marco, "ultimo motivo")
    assert "D_max_catalogo" not in _motivo_descarte(marco, "ultimo motivo")


def test_mismo_escalon_compara_anchos_por_valor_y_no_por_identidad():
    """
    `ancho_b is None -> is not None` sobrevivia porque el test comparaba dos
    marcos escritos con el MISMO literal 2.0 (el interprete los interna y un
    `is` accidental da True). Con anchos calculados en tiempo de ejecucion
    la identidad no salva al mutante.
    """
    from src.modulos.MD import _mismo_escalon
    b_uno, b_dos = float("2.0"), 1.0 + 1.0
    assert b_uno is not b_dos
    assert _mismo_escalon(SeccionRectangular(b_uno, 1.5), SeccionRectangular(b_dos, 1.5))
    assert not _mismo_escalon(SeccionRectangular(b_uno, 1.5), SeccionRectangular(2.5, 1.5))


def test_la_procedencia_de_un_ke_explicito_lo_dice():
    """`return <texto> -> return None` en `_procedencia_ke` dejaba la memoria sin procedencia."""
    from src.modulos.M4_control import _procedencia_ke, control_salida
    c = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    sec = SeccionCircular(DIAMETROS_M[0])
    salida = control_salida(1.0, sec, PENDIENTES[1], L_MARCO, TW_LIBRE, c.n_max, ke=0.5)
    assert not salida.ke_criterio
    procedencia = _procedencia_ke(salida)
    assert isinstance(procedencia, str) and "explicito" in procedencia
    # Y por la otra puerta, la del criterio, la procedencia nombra la clave.
    del_criterio = control_salida(1.0, sec, PENDIENTES[1], L_MARCO, TW_LIBRE, c.n_max)
    assert del_criterio.ke_criterio
    assert del_criterio.ke_criterio in _procedencia_ke(del_criterio)


def test_el_resguardo_por_cbr_lee_la_tabla_con_el_borde_superior_abierto():
    """
    `cbr < cbr_max -> <=` sobrevivia: nadie pedia el resguardo EN un borde
    de la tabla. El docstring fija «[CBR_min, CBR_max)»: en el borde manda la
    fila siguiente, la de menor resguardo.
    """
    from src.constantes_normativas import RESGUARDO_NAPA_SUBRASANTE
    from src.modulos.M5_verificaciones import resguardo_por_cbr
    for cbr_min, cbr_max, resguardo in RESGUARDO_NAPA_SUBRASANTE:
        if cbr_max is None:
            continue
        siguiente = next(r for lo, hi, r in RESGUARDO_NAPA_SUBRASANTE if lo == cbr_max)
        assert resguardo_por_cbr(cbr_max) == pytest.approx(siguiente, rel=REL_TRANSPORTE)
        assert siguiente < resguardo
        assert resguardo_por_cbr(cbr_max - 2 * TOL_UMBRAL_NORMATIVO) == pytest.approx(
            resguardo, rel=REL_TRANSPORTE)


# ===========================================================================
# PF-1 (PC-03) - P9: el limite de signo de la correccion por pendiente
# ===========================================================================
#
# Para todo (Q, D) de la malla y toda S por debajo de S*(Q, D), la ecuacion
# de control de entrada entrega HWi/D > 0; y S* no crece con D, que es lo
# que hace correcto descartar el material ENTERO bajo «descartar» (si la
# carta se cae en el D minimo, ninguno mayor la levanta). Se escribio en rojo
# junto a `tests/test_pf1_hw_fuera_de_rango.py` porque `pendiente_limite_de_
# signo` no existia; a diferencia de P1-P8 no defiende un invariante que el
# motor ya cumplia sino uno que PF-1 abrio.

# Fracciones de S* a las que se evalua la carga: por debajo del limite en
# toda la malla, sin acercarse al ruido del borde.
FRACCIONES_DE_S_LIMITE = (0.1, 0.5, 0.9)
D_MALLA_SIGNO = (0.90, 1.20, 1.50, 2.00, 2.40)
Q_MALLA_SIGNO = (0.05, 0.10, 0.30, 1.0)


@pytest.mark.parametrize("Q", Q_MALLA_SIGNO)
@pytest.mark.parametrize("D", D_MALLA_SIGNO)
@pytest.mark.parametrize("fraccion", FRACCIONES_DE_S_LIMITE)
def test_P9_bajo_el_limite_de_signo_la_carta_entrega_carga(Q, D, fraccion):
    from src.modulos.M4_control import pendiente_limite_de_signo
    hds5 = catalogo(TipoMaterial.CONCRETO_REFORZADO).hds5
    seccion = SeccionCircular(D)
    limite = pendiente_limite_de_signo(Q=Q, seccion=seccion, hds5=hds5)
    assert limite is not None and limite > 0
    entrada = control_entrada(Q=Q, seccion=seccion, S=fraccion * limite, hds5=hds5)
    assert entrada.HW_sobre_D > 0 and entrada.piso is None


@pytest.mark.parametrize("Q", Q_MALLA_SIGNO)
def test_P9_el_limite_de_signo_no_crece_con_D(Q):
    from src.modulos.M4_control import pendiente_limite_de_signo
    hds5 = catalogo(TipoMaterial.CONCRETO_REFORZADO).hds5
    limites = [pendiente_limite_de_signo(Q=Q, seccion=SeccionCircular(D), hds5=hds5)
               for D in D_MALLA_SIGNO]
    for menor, mayor in zip(limites, limites[1:]):
        assert mayor <= menor * (1 + REL_TRANSPORTE)
