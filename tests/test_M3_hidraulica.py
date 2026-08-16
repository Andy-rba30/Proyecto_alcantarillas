"""
tests/test_M3_hidraulica.py
============================
M3 contra la Fase 4.1: geometria circular parcialmente llena y tirante normal
por Manning + Brent, con la regla de doble n.

Los tests que mas importan son cuatro:

    - la geometria (A, P, R) reproduce el caso patron CP-2 dentro de su
      tolerancia;
    - la regla de doble n da dos thetas distintos para el mismo Q/D/S (n_max
      frente a n_min) y V sale del theta de n_min, NO de Q/A(theta n_max);
    - un Q que ningun theta en (0, 2*pi) puede transportar devuelve None, sin
      lanzar una excepcion generica;
    - HDPE hereda el rango de Manning por analogia (Sec. 4.1.1) y por eso
      produce dos ramas distintas igual que concreto y TMC, nunca una sola.
"""

import math

import pytest

from modelos import DatoInvalidoError, Geometria, TiranteNormal, TipoMaterial
from modulos.M2_material import catalogo
from modulos.M3_hidraulica import area, geometria, perimetro, resolver_manning, tirante_normal
from tests.fixtures.casos_patron import CP2_GEOMETRIA_MANNING, CP3_VELOCIDAD_MINIMA


@pytest.fixture
def concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


@pytest.fixture
def hdpe():
    return catalogo(TipoMaterial.HDPE)


# ---------------------------------------------------------------------------
# CP-2 - Geometria circular y Manning (Sec. 4.1)
# ---------------------------------------------------------------------------

def test_geometria_reproduce_cp2():
    c = CP2_GEOMETRIA_MANNING
    theta = c["theta_esperado"]
    g = geometria(c["D"], theta)

    assert isinstance(g, Geometria)
    assert g.A == pytest.approx(c["A_esperado"], abs=c["tolerancia_geometria"])
    assert g.P == pytest.approx(c["P_esperado"], abs=c["tolerancia_geometria"])
    assert g.R == pytest.approx(c["R_esperado"], abs=c["tolerancia_geometria"])
    assert g.y_sobre_D == pytest.approx(c["y_sobre_D"], abs=c["tolerancia_geometria"])


def test_area_y_perimetro_funciones_sueltas_coinciden_con_geometria():
    c = CP2_GEOMETRIA_MANNING
    theta = c["theta_esperado"]
    assert area(c["D"], theta) == pytest.approx(c["A_esperado"], abs=c["tolerancia_geometria"])
    assert perimetro(c["D"], theta) == pytest.approx(c["P_esperado"], abs=c["tolerancia_geometria"])


def test_tirante_normal_resuelve_el_theta_de_cp2_desde_Q():
    """
    CP-2 da y/D=0.75 y deriva Q_con_n_max = V_con_n_max * A. Yendo en sentido
    inverso -- desde ese Q hasta el theta -- tirante_normal() debe encontrar
    el mismo theta, con Brent y no con la formula cerrada de y/D.
    """
    c = CP2_GEOMETRIA_MANNING
    g = tirante_normal(D=c["D"], Q=c["Q_con_n_max_esperado"], S=c["S"], n=c["n_max"])

    assert g is not None
    assert g.theta == pytest.approx(c["theta_esperado"], rel=1e-4)
    assert g.A == pytest.approx(c["A_esperado"], abs=c["tolerancia_geometria"])


def test_velocidad_con_n_max_reproduce_cp2():
    c = CP2_GEOMETRIA_MANNING
    g = tirante_normal(D=c["D"], Q=c["Q_con_n_max_esperado"], S=c["S"], n=c["n_max"])
    V = c["Q_con_n_max_esperado"] / g.A
    assert V == pytest.approx(c["V_con_n_max_esperado"], abs=c["tolerancia_hidraulica"])


# ---------------------------------------------------------------------------
# Regla de doble n (Sec. 4.1)
# ---------------------------------------------------------------------------

def test_resolver_manning_aplica_doble_n(concreto):
    c = CP2_GEOMETRIA_MANNING
    Q = c["Q_con_n_max_esperado"]

    resolucion = resolver_manning(D=c["D"], Q=Q, S=c["S"], material=concreto)

    assert isinstance(resolucion, TiranteNormal)
    assert resolucion.geometria.theta == pytest.approx(c["theta_esperado"], rel=1e-4)
    assert resolucion.V == pytest.approx(c["V_con_n_min_esperado"], abs=c["tolerancia_hidraulica"])


def test_v_con_n_min_no_es_Q_sobre_area(concreto):
    """
    Guarda de diseno explicita: V*A != Q en general. Si un modulo calculara V
    como Q / geometria.A estaria ignorando la regla de doble n (Sec. 4.1) y
    devolviendo la velocidad de la rama de n_max en vez de la de n_min.
    """
    c = CP2_GEOMETRIA_MANNING
    Q = c["Q_con_n_max_esperado"]
    resolucion = resolver_manning(D=c["D"], Q=Q, S=c["S"], material=concreto)

    V_incorrecta = Q / resolucion.geometria.A
    assert resolucion.V != pytest.approx(V_incorrecta, rel=1e-3)
    assert resolucion.V > V_incorrecta   # n_min < n_max -> misma R, mas velocidad


def test_las_dos_ramas_comparten_la_misma_geometria(concreto):
    """
    La regla de doble n NO resuelve Brent dos veces: la velocidad de n_min se
    calcula sobre el mismo theta/R que fijo la rama de n_max (ver CP-2).
    """
    c = CP2_GEOMETRIA_MANNING
    Q = c["Q_con_n_max_esperado"]

    resolucion = resolver_manning(D=c["D"], Q=Q, S=c["S"], material=concreto)
    V_esperada = (1 / concreto.n_para_velocidad) * resolucion.geometria.R ** (2 / 3) * c["S"] ** (1 / 2)

    assert resolucion.V == pytest.approx(V_esperada, rel=1e-9)


def test_hdpe_tambien_aplica_doble_n_por_el_rango_de_criterios_adoptados(hdpe):
    """Sec. 4.1.1: el n de HDPE es un RANGO (0.010-0.013), no un valor puntual;
    resolver_manning() debe seguir dando una V de erosion distinta de la
    velocidad implicita en la rama de capacidad."""
    c = CP2_GEOMETRIA_MANNING
    Q = c["Q_con_n_max_esperado"]

    assert hdpe.n_min != hdpe.n_max
    resolucion = resolver_manning(D=c["D"], Q=Q, S=c["S"], material=hdpe)

    assert resolucion is not None
    V_con_n_max = Q / resolucion.geometria.A
    assert resolucion.V > V_con_n_max


# ---------------------------------------------------------------------------
# CP-3 - la velocidad minima nunca gobierna (Sec. 5.2), contraste adicional
# de la formula de velocidad usando el R de CP-2 con otra pendiente
# ---------------------------------------------------------------------------

def test_pendiente_que_produce_v_objetivo_de_cp3():
    c = CP3_VELOCIDAD_MINIMA
    R = CP2_GEOMETRIA_MANNING["R_esperado"]
    V = (1 / c["n"]) * R ** (2 / 3) * c["S_que_produce_V_objetivo"] ** (1 / 2)
    assert V == pytest.approx(c["V_objetivo"], abs=1e-3)


# ---------------------------------------------------------------------------
# El caso "sin solucion"
# ---------------------------------------------------------------------------

def test_un_caudal_que_ningun_theta_transporta_devuelve_none():
    """D=0.90 lleno a presion (Sec. 4.1) no llega a transportar un Q absurdo:
    tirante_normal() debe devolver None, no lanzar una excepcion generica."""
    g = tirante_normal(D=0.90, Q=100.0, S=0.005, n=0.013)
    assert g is None


def test_resolver_manning_devuelve_none_si_la_rama_de_n_max_no_converge(concreto):
    resolucion = resolver_manning(D=0.90, Q=100.0, S=0.005, material=concreto)
    assert resolucion is None


def test_none_no_es_una_excepcion():
    """El caso sin solucion es un resultado de diseño, no un fallo del programa."""
    try:
        resultado = tirante_normal(D=0.90, Q=100.0, S=0.005, n=0.013)
    except Exception as exc:   # pragma: no cover - documenta la intencion del test
        pytest.fail(f"tirante_normal() no debe lanzar excepcion en el caso "
                    f"sin solucion, lanzo {type(exc).__name__}: {exc}")
    assert resultado is None


# ---------------------------------------------------------------------------
# Validacion de parametros
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("kwargs, campo", [
    ({"D": 0.0, "Q": 1.0, "S": 0.005, "n": 0.013}, "D"),
    ({"D": 0.90, "Q": -1.0, "S": 0.005, "n": 0.013}, "Q"),
    ({"D": 0.90, "Q": 1.0, "S": 0.0, "n": 0.013}, "S"),
    ({"D": 0.90, "Q": 1.0, "S": 0.005, "n": 0.0}, "n"),
])
def test_parametros_invalidos_lanzan_dato_invalido(kwargs, campo):
    with pytest.raises(DatoInvalidoError) as exc:
        tirante_normal(**kwargs)
    assert exc.value.campo == campo
