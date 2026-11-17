"""
tests/test_ve3_remanso.py
=========================
VE-3.7: el REMANSO del canal por paso directo (Familia C), que la ficha
VC1-01 y la deuda §13 de docs/ruta_familia_c.md dejaban abierto («Cerrarlo
exige un perfil de remanso (paso a paso o HEC-RAS)»).

Hasta aqui `M7.remanso_canal` daba la sobreelevacion en el cruce y una COTA
INFERIOR de la longitud (dh / S, la horizontal del embalse contra la lamina
normal) en un canal suave, y en uno de pendiente fuerte «no concluia»: la
lamina es una S1 que termina en resalto y la horizontal no la acota.

Ahora:
  - `M3.perfil_remanso_trapecial`: el perfil por PASO DIRECTO (el metodo con
    que el HDS-5 calcula la lamina en el barril, num. 3.5) en el canal
    prismatico trapecial, con escalones geometricos en (y - y_n).
  - `M3.tirante_conjugado_trapecial`: el tirante secuente por la funcion
    momentum en el trapecio.
  - canal FUERTE: la S1 hasta el resalto (el conjugado del normal) ya
    CONCLUYE, con su longitud.
  - canal SUAVE: la M1 es asintotica al normal y no tiene un final que la
    fuente fije; la longitud del perfil hasta (1 + f) y_n se da solo si se
    declara el criterio [A] OPCIONAL 'fraccion_fin_remanso_canal'. Sin el,
    queda la cota inferior de siempre.

VALIDACION DEL METODO. No se encontro un ejemplo resuelto de paso directo de
acceso legal y verificable (el clasico es Chow 1959, cap. 10, con derechos;
las copias en Scribd no dicen de donde salen). El contraste es contra una
integracion INDEPENDIENTE de la ecuacion del flujo gradualmente variado,
dx/dy = (1 - Fr^2) / (S - Sf), con scipy (`solve_ivp`, rtol 1e-11), escrita
aqui y no en el modulo; y el conjugado, contra la formula cerrada de
Belanger en la seccion rectangular.

SE ESCRIBIO EN ROJO PRIMERO, contra 207daa5.
"""

from __future__ import annotations

import math

import pytest
from scipy.integrate import solve_ivp

from src import criterios_adoptados as ca
from src.constantes_fisicas import G
from src.modelos import SeccionReceptor
from src.modulos import M3_hidraulica as M3
from src.modulos import M7_geometria as M7
from src.tolerancias import TOL_REL_PASO_DIRECTO_REMANSO
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import con_valor
from tests.test_t3_familia_c import _punto_c01

CRITERIO = "fraccion_fin_remanso_canal"
Q = 0.85
# El canal de C-01 del juego de T-11 (b 1.0, z 1.5, n 0.025, S 0.006): suave.
SUAVE = SeccionReceptor(b_m=1.0, z_HV=1.5, S=0.006, n=0.025,
                        altura_total_m=2.1)
# El canal del auditor de T-3 (rectangular, b 1.20, n 0.014, S 0.02): fuerte.
FUERTE = SeccionReceptor(b_m=1.20, z_HV=0.0, S=0.02, n=0.014,
                         altura_total_m=1.20)


def _referencia(seccion, y0, y1):
    """La longitud de la integracion independiente de la ecuacion del FGV."""
    b, z, S, n = seccion.b_m, seccion.z_HV, seccion.S, seccion.n

    def dxdy(y, _x):
        A = (b + z * y) * y
        P = b + 2 * y * math.sqrt(1 + z * z)
        T = b + 2 * z * y
        Sf = (n * Q / (A * (A / P) ** (2 / 3))) ** 2
        Fr2 = Q * Q * T / (G * A ** 3)
        return [-(1 - Fr2) / (S - Sf)]

    sol = solve_ivp(dxdy, (y0, y1), [0.0], rtol=1e-11, atol=1e-12)
    return sol.y[0][-1]


@pytest.mark.parametrize("fraccion", (0.05, 0.01, 0.001))
def test_el_paso_directo_de_la_M1_coincide_con_la_integracion_independiente(
        fraccion):
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=SUAVE)
    y_fin = y_n * (1 + fraccion)
    L, estaciones = M3.perfil_remanso_trapecial(
        Q=Q, seccion=SUAVE, y_inicio=0.80, y_fin=y_fin)
    assert L == pytest.approx(_referencia(SUAVE, 0.80, y_fin),
                              rel=TOL_REL_PASO_DIRECTO_REMANSO)
    assert estaciones[0][0] == pytest.approx(0.0, abs=ABS_CERO)
    assert estaciones[0][1] == pytest.approx(0.80, rel=REL_TRANSPORTE)
    assert estaciones[-1][1] == pytest.approx(y_fin,
                                              rel=TOL_REL_PASO_DIRECTO_REMANSO)
    xs = [e[0] for e in estaciones]
    assert xs == sorted(xs)


def test_el_conjugado_rectangular_es_el_de_belanger():
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=FUERTE)
    Fr1 = (Q / (FUERTE.b_m * y_n)) / math.sqrt(G * y_n)
    belanger = y_n / 2 * (math.sqrt(1 + 8 * Fr1 ** 2) - 1)
    assert M3.tirante_conjugado_trapecial(
        Q=Q, seccion=FUERTE, y=y_n) == pytest.approx(
        belanger, rel=TOL_REL_PASO_DIRECTO_REMANSO)


def test_el_paso_directo_de_la_S1_hasta_el_resalto_coincide():
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=FUERTE)
    y_j = M3.tirante_conjugado_trapecial(Q=Q, seccion=FUERTE, y=y_n)
    L, _ = M3.perfil_remanso_trapecial(Q=Q, seccion=FUERTE, y_inicio=0.90,
                                       y_fin=y_j)
    assert L == pytest.approx(_referencia(FUERTE, 0.90, y_j),
                              rel=TOL_REL_PASO_DIRECTO_REMANSO)


def test_el_canal_fuerte_ya_concluye_con_la_longitud_hasta_el_resalto():
    """El caso del auditor de T-3 (HW = 0.90): antes «no concluye»."""
    rem = M7.remanso_canal(punto=_punto_c01(), cota_entrada_msnm=36.90,
                           HW=0.90, Q=Q, seccion_canal=FUERTE)
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=FUERTE)
    y_j = M3.tirante_conjugado_trapecial(Q=Q, seccion=FUERTE, y=y_n)
    assert rem.concluye
    assert rem.y_conjugado_canal_m == pytest.approx(
        y_j, rel=TOL_REL_PASO_DIRECTO_REMANSO)
    assert rem.longitud_remanso_m == pytest.approx(
        _referencia(FUERTE, 0.90, y_j), rel=TOL_REL_PASO_DIRECTO_REMANSO)
    assert "resalto" in rem.metodo_longitud


def test_en_el_canal_fuerte_un_HW_bajo_el_conjugado_deja_el_resalto_en_la_boca():
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=FUERTE)
    y_j = M3.tirante_conjugado_trapecial(Q=Q, seccion=FUERTE, y=y_n)
    rem = M7.remanso_canal(punto=_punto_c01(), cota_entrada_msnm=36.90,
                           HW=(y_n + y_j) / 2, Q=Q, seccion_canal=FUERTE)
    assert rem.concluye
    assert rem.longitud_remanso_m == pytest.approx(0.0, abs=ABS_CERO)


def test_el_canal_suave_sin_el_criterio_queda_con_la_cota_inferior():
    rem = M7.remanso_canal(punto=_punto_c01(), cota_entrada_msnm=36.90,
                           HW=0.80, Q=Q, seccion_canal=SUAVE)
    assert rem.concluye and rem.longitud_remanso_m is None
    assert rem.longitud_minima_m is not None
    assert CRITERIO in rem.aviso


def test_el_canal_suave_con_el_criterio_da_la_longitud_del_perfil():
    with con_valor(CRITERIO, 0.01, motivo="test de VE-3.7"):
        rem = M7.remanso_canal(punto=_punto_c01(), cota_entrada_msnm=36.90,
                               HW=0.80, Q=Q, seccion_canal=SUAVE)
    y_n = M3.tirante_normal_trapecial(Q=Q, seccion=SUAVE)
    esperado = _referencia(SUAVE, 0.80, y_n * 1.01)
    assert rem.longitud_remanso_m == pytest.approx(
        esperado, rel=TOL_REL_PASO_DIRECTO_REMANSO)
    # La M1 queda por encima de la horizontal: llega mas lejos que dh / S.
    assert rem.longitud_remanso_m > rem.longitud_minima_m


def test_el_criterio_es_un_A_de_perfil_opcional_con_ventana():
    c = ca.CRITERIOS[CRITERIO]
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert c.opcional and c.valor is None
    assert c.sensibilidad is not None and c.resolucion is not None
