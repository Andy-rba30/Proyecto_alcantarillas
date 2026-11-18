"""
tests/test_ve2_velocidad_erosion.py
===================================
La aceptacion del BLOQUE 1 de VE-2: la decision (b) de la ficha VE1-02,
aprobada por el dueño el 2026-11-17. Es el unico defecto de METODO de las
siete decisiones, y el unico bloque que mueve numeros de la linea base.

EL DEFECTO. `M3.resolver_manning` resolvia UN tirante normal, con n_max, y
sobre esa misma geometria calculaba la velocidad alta como
V(n_max) * n_max / n_min: la velocidad de una rugosidad sobre el tirante de
otra. Para el concreto (0.010 / 0.013) eso es V * A = 1.3 * Q, un caudal que
no pasa por el conducto (`modelos.TiranteNormal` lo documentaba «por diseño»).
Ninguna fuente toma el tirante de un n y la velocidad de otro: el HDS-5
(hif12026, num. 3.3.2, pag. impresa 3.24) dice «determine the normal depth
and velocity in the culvert barrel.  The velocity at normal depth is assumed
to be the outlet velocity», y HEC-14 (num. 3.2.2, pag. impresa 3-7) «normal
flow is assumed at the culvert outlet and the outlet velocity is computed
using Manning's Equation»; su ejemplo de la pag. impresa 3-8 resuelve UN
tirante por cada n (y = 0.625 m con n = 0.012, y = 0.945 m con n = 0.024) y
toma Vo = Q/A de cada uno.

LA CORRECCION. La velocidad alta resuelve SU PROPIO tirante normal con n_min
(una segunda resolucion de Brent sobre la misma ecuacion) y
V_erosion = Q / A(y_n con n_min). La estimacion baja (n_max) y el tirante de
capacidad no cambian. Bajo control de SALIDA la velocidad de salida que toma
M4 (critico, TW o barril lleno, HDS-5 3.1.6) no se toca.

Escrita PRIMERO, en rojo (§1 regla 4 de la cadena; preambulo de VE-2): los
tests de la correccion llevaban `xfail(strict=True)` con la expectativa y
fallaban por su motivo antes de tocar M3 (medido con `--runxfail`: la
continuidad con V*A = 1.3*Q, el caso UPAO con 6.284 m/s y Ø 1.35 m, el
mutante sin el texto nuevo, el campo `geometria_erosion` ausente, el
fundamento y la cita de HEC-14 sin registrar, la ficha sin escribir). Los
que llevan GUARDIA en el docstring valen antes y despues: fijan lo que la
correccion NO puede mover.

Los datos del caso UPAO ALC46 (Q = 0.317 m3/s, S = 0.10, D = 0.90 m,
concreto) son los de la validacion externa (ficha VE1-02 (b)); el resto del
punto es el cruce sintetico P1 de `tests/test_ve1_validacion.py`, DATOS DE
PRUEBA y no de proyecto.

LA TOLERANCIA ES NOMBRADA (`TOL_REL_CONTINUIDAD_MANNING`) y se
midio sobre la malla de abajo al cerrar VE-2: la peor desviacion relativa
entre la velocidad de Manning sobre la geometria resuelta y Q/A fue de
8.1e-11 en la rama de n_min y de 3.6e-11 en la de n_max (la de EXT-11). El
mutante de la formula vieja se aparta de la continuidad un 4.8 % como
minimo en la misma malla. La tolerancia es 1e-8 desde las correcciones de
VE-2 (B3 de la revision Fable): fuera de esta malla, con Q bajo el 5 % del
lleno en los marcos, se midieron 1.81e-9 (el barrido, en el comentario de
`src/tolerancias.py`); el mutante sigue a cuatro millones ochocientas mil
veces la tolerancia.
"""

from __future__ import annotations

import ast
import json
import math
import re
import types
from pathlib import Path

import pytest

import cli
from src import servicio
from src.constantes_normativas import K_MANNING_SI
from src.modelos import (ControlGobernante, FormaSeccion, SeccionCircular,
                         SeccionRectangular, TiranteNormal, TipoMaterial)
from src.modulos import M3_hidraulica as M3
from src.modulos import M4_control as M4
from src.modulos import M5_verificaciones as M5
from src.modulos import M6_proteccion as M6
from src.modulos.M2_material import catalogo
from src.normativa import registro as _registro
from src.tolerancias import TOL_REL_CONTINUIDAD_MANNING
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.test_ext2_multicelda_transicion import CAJON_N3

RAIZ = Path(__file__).resolve().parents[1]
FUENTE_M3 = RAIZ / "src" / "modulos" / "M3_hidraulica.py"
REGISTRO_DE_DECISIONES = RAIZ / "docs" / "decisiones_diferidas.md"

CONCRETO = TipoMaterial.CONCRETO_REFORZADO
TMC = TipoMaterial.TMC
HDPE = TipoMaterial.HDPE

ID_CITA_HEC14 = "HEC14.3.2.2#V_SALIDA_NORMAL"
ID_CITA_HDS5 = "HDS5_3ED.3.3.2#V_SALIDA_ENTRADA"

# ---------------------------------------------------------------------------
# Las mallas (las de `tests/test_ext11_propiedades.py`, menos el 0.99 de
# Q_lleno: alli la curva circular pasa su pico y la rama de n_min ya no es la
# solucion baja de la misma familia)
# ---------------------------------------------------------------------------
DIAMETROS_M = (0.90, 1.05, 1.20, 1.50, 1.80, 2.40)
MARCOS_B_H = ((1.00, 1.00), (1.50, 1.00), (2.00, 1.50), (2.50, 2.00))
PENDIENTES = (0.002, 0.005, 0.010, 0.030)
FRACCIONES = (0.05, 0.10, 0.30, 0.50, 0.70, 0.90)
MATERIALES_CIRCULARES = (CONCRETO, TMC, HDPE)

# Tolerancia del caso UPAO: la validacion externa da dos decimales (5.81 m/s)
# y la ficha VE1-02 los mismos; se compara con media centesima.
ABS_CASO_UPAO_M_S = 0.005
# Los tirantes del caso UPAO se escriben aqui con cuatro decimales (0.1266 y
# 0.1438 m): una unidad del ultimo digito escrito.
ABS_TIRANTE_4_DECIMALES_M = 1e-4
# La velocidad del caso subcritico del dictamen (1.508 m/s) se imprime con
# tres decimales: media unidad del ultimo.
ABS_IMPRESO_3_DECIMALES = 5e-4
UPAO = {"Q": 0.317, "S": 0.10, "D": 0.90}

# Escritos en rojo con `xfail(strict=True)` y la razon «VE-2 (b): la velocidad
# de erosion todavia se calcula con n_min sobre la geometria de n_max (V*A =
# 1.3*Q)» --539 casos de los 553, medidos con `--runxfail`--, y liberados al
# corregir: el marcador se retiro y esta linea queda como constancia.


# ---------------------------------------------------------------------------
# Oraculo independiente: Manning resuelto aqui, sin M3
# ---------------------------------------------------------------------------

def _geometria_circular(D, theta):
    A = (D ** 2 / 8) * (theta - math.sin(theta))   # Sec. 4.1
    P = D * theta / 2
    return A, P


def _geometria_marco(B, y):
    return B * y, B + 2 * y


def _area_normal_independiente(seccion, Q, S, n):
    """
    El area del tirante normal de Manning para (Q, S, n), resuelta con brentq
    sobre las formulas de la Sec. 4.1 escritas aqui y no con `M3`: es lo que
    hace de la continuidad una comprobacion y no una tautologia.
    """
    from scipy.optimize import brentq

    if isinstance(seccion, SeccionCircular):
        geom = lambda x: _geometria_circular(seccion.D, x)
        a, b = 1e-9, 2 * math.pi - 1e-9
    else:
        geom = lambda x: _geometria_marco(seccion.B, x)
        a, b = 1e-12, seccion.H

    def f(x):
        A, P = geom(x)
        return (K_MANNING_SI / n) * A * (A / P) ** (2 / 3) * S ** 0.5 - Q

    x = brentq(f, a, b, xtol=1e-13)
    return geom(x)[0]


def _Q_lleno(seccion, n, S):
    return ((K_MANNING_SI / n) * seccion.area_llena
            * seccion.radio_hidraulico_lleno ** (2 / 3) * S ** 0.5)


@pytest.fixture
def marco():
    """El material del cajon, con los criterios de EXT-2 declarados."""
    with declarados(CAJON_N3):
        yield catalogo(CONCRETO, forma=FormaSeccion.RECTANGULAR)


def _continuidad(r, seccion, Q, S, material):
    """
    La comprobacion de la correccion, escrita UNA vez para que el mutante de
    abajo la reciba igual: V_erosion * A(y_n con n_min) = Q.
    """
    A_min = _area_normal_independiente(seccion, Q, S,
                                       material.n_para_velocidad_maxima)
    assert r.V_erosion * A_min == pytest.approx(
        Q, rel=TOL_REL_CONTINUIDAD_MANNING), (
        f"V_erosion * A(n_min) = {r.V_erosion * A_min!r} y Q = {Q!r}")


# ===========================================================================
# 1 · La continuidad de la rama de n_min
# ===========================================================================

@pytest.mark.parametrize("tipo", MATERIALES_CIRCULARES, ids=lambda t: t.value)
@pytest.mark.parametrize("D", DIAMETROS_M)
@pytest.mark.parametrize("S", PENDIENTES)
@pytest.mark.parametrize("fraccion", FRACCIONES)
def test_continuidad_circular_V_erosion_por_A_de_n_min_es_Q(tipo, D, S, fraccion):
    material = catalogo(tipo)
    seccion = SeccionCircular(D)
    Q = fraccion * _Q_lleno(seccion, material.n_para_capacidad, S)
    r = M3.resolver_manning(seccion, Q, S, material)
    assert isinstance(r, TiranteNormal)
    _continuidad(r, seccion, Q, S, material)


@pytest.mark.parametrize("B,H", MARCOS_B_H)
@pytest.mark.parametrize("S", PENDIENTES)
@pytest.mark.parametrize("fraccion", FRACCIONES)
def test_continuidad_marco_V_erosion_por_A_de_n_min_es_Q(marco, B, H, S, fraccion):
    seccion = SeccionRectangular(B, H)
    Q = fraccion * _Q_lleno(seccion, marco.n_para_capacidad, S)
    r = M3.resolver_manning(seccion, Q, S, marco)
    assert isinstance(r, TiranteNormal)
    assert marco.n_min < marco.n_max, "la fila del cajon es un rango"
    _continuidad(r, seccion, Q, S, marco)


@pytest.mark.parametrize("seccion", [SeccionCircular(1.20),
                                     SeccionRectangular(2.00, 1.50)],
                         ids=["circular", "marco"])
def test_V_erosion_es_ademas_la_velocidad_de_manning_sobre_su_propio_tirante(
        marco, seccion):
    """
    Q/A y la ec. (47) del num. 4.1.1.3.6 son la MISMA velocidad cuando se
    evaluan sobre el tirante que resolvio ese n: la correccion no cambia de
    formula, cambia de geometria. `geometria_erosion` es la que M3 publica.
    """
    material = (catalogo(CONCRETO) if isinstance(seccion, SeccionCircular)
                else marco)
    S = 0.01
    Q = 0.4 * _Q_lleno(seccion, material.n_para_capacidad, S)
    r = M3.resolver_manning(seccion, Q, S, material)
    g = r.geometria_erosion
    V_manning = (K_MANNING_SI / material.n_para_velocidad_maxima
                 * g.R ** (2 / 3) * S ** 0.5)
    assert r.V_erosion == pytest.approx(
        V_manning, rel=TOL_REL_CONTINUIDAD_MANNING)
    assert g.A == pytest.approx(
        _area_normal_independiente(seccion, Q, S,
                                   material.n_para_velocidad_maxima),
        rel=TOL_REL_CONTINUIDAD_MANNING)
    # Con un n menor el tirante normal baja (rama creciente de la curva).
    assert g.y < r.geometria.y


@pytest.mark.parametrize("tipo", MATERIALES_CIRCULARES, ids=lambda t: t.value)
@pytest.mark.parametrize("D", (0.90, 1.80))
@pytest.mark.parametrize("fraccion", (0.10, 0.70))
def test_guardia_la_rama_de_capacidad_y_V_sedimentacion_no_cambian(tipo, D, fraccion):
    """
    GUARDIA (vale antes y despues). El tirante de capacidad sigue siendo el
    de n_max --el que V1 juzga-- y V_sedimentacion su velocidad media:
    V_sedimentacion * A(n_max) = Q. La decision (b) solo cambia la rama alta.
    """
    material = catalogo(tipo)
    seccion, S = SeccionCircular(D), 0.005
    Q = fraccion * _Q_lleno(seccion, material.n_para_capacidad, S)
    r = M3.resolver_manning(seccion, Q, S, material)
    A_max = _area_normal_independiente(seccion, Q, S, material.n_para_capacidad)
    assert r.geometria.A == pytest.approx(
        A_max, rel=TOL_REL_CONTINUIDAD_MANNING)
    assert r.V_sedimentacion * A_max == pytest.approx(
        Q, rel=TOL_REL_CONTINUIDAD_MANNING)


# ===========================================================================
# 2 · El caso UPAO ALC46 de la validacion externa
# ===========================================================================

def test_upao_alc46_la_velocidad_de_erosion_a_0_90_m_es_5_81():
    """
    VE1-02 (b): a Ø 0.90 m la formula vieja daba 6.28 m/s, por encima del
    techo de 6.0 de la Tabla Nº 10, y la de cada rama con su tirante 5.81.
    """
    r = M3.resolver_manning(SeccionCircular(UPAO["D"]), UPAO["Q"], UPAO["S"],
                            catalogo(CONCRETO))
    assert r.V_erosion == pytest.approx(5.81, abs=ABS_CASO_UPAO_M_S)
    # El tirante de n_min, que es el que la memoria imprime.
    assert r.geometria_erosion.y == pytest.approx(
        0.1266, abs=ABS_TIRANTE_4_DECIMALES_M)
    # La rama de capacidad sigue con su tirante de siempre.
    assert r.geometria.y == pytest.approx(0.1438, abs=ABS_TIRANTE_4_DECIMALES_M)


CABECERA = (
    "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,"
    "cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,"
    "ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,"
    "sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,"
    "cota_coronacion_canal\n")
BANDERAS_VACIAS = {"luz_m": None, "TW_m": None, "longitud_m": None,
                   "L_hidraulico_m": None, "categoria_tr": None}


def _correr_upao(tmp_path: Path) -> dict:
    """
    El punto P1 de `tests/test_ve1_validacion.py` con el caudal y la
    pendiente de UPAO ALC46, a alcance de perfil y en proceso.
    """
    csv = tmp_path / "upao_alc46.csv"
    csv.write_text(CABECERA + f"P1,0+100,A,{UPAO['Q']},50,{UPAO['S']},100.0,"
                   "104.0,103.85,10,0,9.0,99.5,,,SM,,,\n", encoding="utf-8")
    externos_json = tmp_path / "externos.json"
    externos_json.write_text(json.dumps(
        {"globales": {"luz_m": 3.0, "TW_m": 0.3}}), encoding="utf-8")
    externos = cli.cargar_datos_externos(externos_json, BANDERAS_VACIAS)
    informe = servicio.correr(csv, externos, alcance=cli.ALCANCE_PERFIL)
    return cli.informe_json(informe)


def test_upao_alc46_de_punta_a_punta_dimensiona_0_90_y_no_1_35(tmp_path):
    """
    Con la formula vieja el concreto incumplia V3 en 0.90, 1.05 y 1.20 m
    (6.28, 6.16 y 6.05 m/s) y el punto dimensionaba Ø 1.35 m. Con cada rama
    sobre su tirante, 0.90 m cumple V3 con 5.81 m/s y es el primer escalon.
    """
    (punto,) = _correr_upao(tmp_path)["puntos"]
    assert punto["dimensionado"], punto["bloqueos"]
    assert punto["diseno"]["seccion"] == "Ø 0.90 m"
    assert [it["aceptado"] for it in punto["iteraciones"]] == [True]
    (v3,) = [v for v in punto["verificaciones"] if v["codigo"] == "V3"]
    assert v3["estado"] == "cumple"
    assert v3["valor_obtenido"] == pytest.approx(5.81, abs=ABS_CASO_UPAO_M_S)
    assert v3["valor_admisible"] == pytest.approx(6.0, rel=REL_TRANSPORTE)
    # Gobierna la entrada: la velocidad de salida es la del tirante normal
    # de n_min, la MISMA que V3 juzga (HDS-5 3.3.2).
    assert punto["diseno"]["control_gobernante"] == "entrada"
    assert punto["diseno"]["V_salida_m_s"] == pytest.approx(
        punto["diseno"]["V_erosion_m_s"], rel=REL_TRANSPORTE)


# ===========================================================================
# 3 · Lo que NO se toca: la velocidad de salida bajo control de salida
# ===========================================================================

def test_guardia_bajo_control_de_salida_la_velocidad_de_salida_no_cambia():
    """
    GUARDIA (vale antes y despues). El caso subcritico del dictamen
    (`tests/test_ext3_regimen_barril.py`): gobierna la salida con el TW bajo
    el critico, y la velocidad de salida es Q / A(y_c) = 1.508 m/s, sin n.
    La decision (b) no la mueve. LA MOVIO el cierre de T8-08 (2026-11-18),
    y se declara: desde entonces se mide en el tirante de BORDE de la
    Figura 3.4 de HEC-14, 2.227 m/s (aritmetica en
    `tests/test_ext3_regimen_barril.py`). Sigue sin llevar n.
    """
    r = M4.resolver_control(seccion=SeccionCircular(0.90), Q=0.3, S=0.001,
                            L=20.0, TW=0.0, material=catalogo(CONCRETO))
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.V_salida.valor == pytest.approx(2.227, abs=ABS_IMPRESO_3_DECIMALES)
    assert r.y_salida_m == pytest.approx(r.y_critico, rel=REL_TRANSPORTE)


def test_bajo_control_de_entrada_V_salida_es_V_erosion_y_su_paso_lo_dice():
    """
    Bajo control de entrada M4 toma la velocidad del tirante normal (HDS-5
    3.3.2): es V_erosion, y su procedencia nombra el tirante de n_min con
    que se midio, no el de registro.
    """
    material = catalogo(CONCRETO)
    seccion = SeccionCircular(UPAO["D"])
    r = M4.resolver_control(seccion=seccion, Q=UPAO["Q"], S=UPAO["S"],
                            L=20.0, TW=0.3, material=material)
    assert r.control_gobernante is ControlGobernante.ENTRADA
    assert r.V_salida.valor == pytest.approx(r.V_erosion, rel=REL_TRANSPORTE)
    normal = M3.resolver_manning(seccion, UPAO["Q"], UPAO["S"], material)
    assert f"{normal.geometria_erosion.y:.3f}" in r.V_salida.procedencia
    assert "su propio tirante" in r.V_salida.procedencia


# ===========================================================================
# 4 · El mutante que vuelve a la formula vieja muere
# ===========================================================================

# La expresion de la correccion en `resolver_manning` y la de la formula
# vieja. El mutante sustituye la primera por la segunda en el ARBOL del
# modulo (no en su texto), lo compila aparte y ejecuta esa copia: el arbol
# de trabajo no se toca.
EXPRESION_CORREGIDA = "Q / geom_erosion.A"
EXPRESION_VIEJA = "factor_geometrico / material.n_para_velocidad_maxima"


def _modulo_mutado():
    arbol = ast.parse(FUENTE_M3.read_text(encoding="utf-8"),
                      filename=str(FUENTE_M3))
    (funcion,) = [n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)
                  and n.name == "resolver_manning"]
    (llamada,) = [n for n in ast.walk(funcion) if isinstance(n, ast.Call)
                  and isinstance(n.func, ast.Name)
                  and n.func.id == "TiranteNormal"]
    (velocidad,) = [k for k in llamada.keywords if k.arg == "V_erosion"]
    assert ast.unparse(velocidad.value) == EXPRESION_CORREGIDA, (
        "la correccion de VE-2 no esta en resolver_manning con la expresion "
        "que el mutante espera")
    velocidad.value = ast.parse(EXPRESION_VIEJA, mode="eval").body
    ast.fix_missing_locations(arbol)
    modulo = types.ModuleType("M3_mutado_ve2")
    exec(compile(arbol, "M3_mutado_ve2", "exec"), modulo.__dict__)
    return modulo


@pytest.mark.parametrize("seccion", [SeccionCircular(0.90),
                                     SeccionRectangular(2.00, 1.50)],
                         ids=["circular", "marco"])
def test_el_mutante_de_la_formula_vieja_muere(marco, seccion):
    material = (catalogo(CONCRETO) if isinstance(seccion, SeccionCircular)
                else marco)
    S = 0.01
    Q = 0.5 * _Q_lleno(seccion, material.n_para_capacidad, S)
    # El original pasa la comprobacion...
    _continuidad(M3.resolver_manning(seccion, Q, S, material),
                 seccion, Q, S, material)
    # ...y el mutante no: V * A(n_min) se aparta de Q mucho mas que la
    # tolerancia (medido: un 4.8 % como minimo en la malla).
    mutado = _modulo_mutado().resolver_manning(seccion, Q, S, material)
    with pytest.raises(AssertionError):
        _continuidad(mutado, seccion, Q, S, material)


# ===========================================================================
# 5 · El fundamento, la cita y la memoria del paso
# ===========================================================================

def test_la_cita_de_hec14_3_2_2_esta_registrada_con_su_pagina():
    cita = _registro.construir().cita(ID_CITA_HEC14)
    assert cita.fuente_id == "HEC14"
    assert cita.numeral == "3.2.2"
    assert cita.pagina_impresa == "3-7"
    assert cita.pagina_pdf == 38
    assert ("normal flow is assumed at the culvert outlet and the outlet "
            "velocity is computed using Manning's Equation"
            in cita.texto_literal.texto)
    assert cita.verificado is not None


def test_el_fundamento_de_manning_ya_no_presenta_la_doble_n_como_norma():
    """
    F4.MANNING decia «UNA geometria y DOS velocidades ... una seccion y dos
    rugosidades sobre la misma seccion», con citas solo del Manual: leida en
    la memoria, la doble n parecia del Manual (la hoja de ruta la rotula
    «Regla [N]» sin numeral; ficha VE1-01, D3). Hoy dice que la eleccion de
    los dos extremos es adopcion del proyecto y cita la «velocidad a tirante
    normal» del HDS-5 y de HEC-14.
    """
    f = _registro.construir().fundamento("F4.MANNING")
    assert ID_CITA_HDS5 in f.citas and ID_CITA_HEC14 in f.citas
    texto = f.que_paso + " " + f.por_que
    assert "misma seccion" not in texto
    assert "UNA geometria" not in texto
    assert "adopcion" in texto.lower()
    assert "Regla [N]" in f.por_que, (
        "el fundamento declara en el punto de uso que la hoja de ruta sigue "
        "rotulando la doble n como «Regla [N]»")


def _pasos(resultado, fundamento_id):
    return [p for p in resultado.pasos if p.fundamento_id == fundamento_id]


def test_la_memoria_del_paso_de_manning_imprime_el_tirante_de_n_min():
    material = catalogo(CONCRETO)
    seccion = SeccionCircular(UPAO["D"])
    r = M4.resolver_control(seccion=seccion, Q=UPAO["Q"], S=UPAO["S"],
                            L=20.0, TW=0.3, material=material)
    normal = M3.resolver_manning(seccion, UPAO["Q"], UPAO["S"], material)
    (manning,) = _pasos(r, "F4.MANNING")
    simbolos = {m.simbolo: m.valor for m in manning.sustitucion}
    assert "y_n_min" not in simbolos     # es un resultado, no un dato
    nota = manning.nota_del_proyecto
    assert f"{normal.geometria_erosion.y:.3f}" in nota
    assert f"{normal.V_erosion:.3f}" in nota
    assert "Regla [N]" not in nota
    for cita in (ID_CITA_HDS5, ID_CITA_HEC14):
        assert cita in manning.citas_textuales
    (regimen,) = _pasos(r, "F4.REGIMEN")
    sustituidos = {m.simbolo: m.valor for m in regimen.sustitucion}
    assert sustituidos["y_n_min"] == pytest.approx(
        normal.geometria_erosion.y, rel=REL_TRANSPORTE)


# ===========================================================================
# 6 · Tabla Nº 10 contra Nº 11: que velocidad se compara con cual
# ===========================================================================

def test_guardia_V3_juzga_la_tabla_10_y_la_salida_la_tabla_11():
    """
    GUARDIA (vale antes y despues), verificada contra el Manual: la Tabla Nº
    10 (pag. impresa 76, PDF 79) es de «conductos revestidos» y la juzga V3
    con la velocidad DENTRO del conducto (V_erosion); la Nº 11 (pag. impresa
    77, PDF 80) es de «canales no revestidos», la presenta el parrafo de «la
    velocidad de flujo a la salida de la alcantarilla ... a fin de evitar
    procesos de socavacion del cauce aguas abajo», y la juzga el paso 6.4 con
    la velocidad de SALIDA.
    """
    material = catalogo(CONCRETO)
    r = M4.resolver_control(seccion=SeccionCircular(UPAO["D"]), Q=UPAO["Q"],
                            S=UPAO["S"], L=20.0, TW=0.3, material=material)
    v3 = M5.v3_velocidad_maxima(material=material, resultado=r)
    assert v3.paso.formula_cita_id == "MC_HHD.4.1.1.3.6#T10"
    assert v3.valor_obtenido == pytest.approx(r.V_erosion, rel=REL_TRANSPORTE)
    adm = M6.velocidad_admisible_del_cauce(
        V=r.V_salida, tipo_terreno="grava_fina", regimen_flujo="intermitente")
    assert adm.paso.formula_cita_id == "MC_HHD.4.1.1.3.6#T11"
    reg = _registro.construir()
    assert "conductos" in reg.cita("MC_HHD.4.1.1.3.6#T10").texto_literal.texto
    assert "canales no" in reg.cita("MC_HHD.4.1.1.3.6#T11").texto_literal.texto


# ===========================================================================
# 7 · La ficha
# ===========================================================================

def test_la_ficha_ve2_b_existe_y_cierra_el_inciso_b_de_ve1_02():
    texto = REGISTRO_DE_DECISIONES.read_text(encoding="utf-8")
    assert re.search(r"^## VE2-B · La velocidad de erosión resuelve su propio "
                     r"tirante con n mínimo", texto, re.M)
    ve1_02 = texto.split("## VE1-02 ·", 1)[1].split("\n## ", 1)[0]
    assert re.search(r"Cerrado \(VE-2\).*\(b\)", ve1_02)
