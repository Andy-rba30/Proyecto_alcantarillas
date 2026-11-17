"""
tests/test_ve3_11_ensayos_conducto.py
=====================================
VE-3.11: los hallazgos de los ENSAYOS DE DISEÑO DEL CONDUCTO
(`proceso/planes_mejora/ve3_estado/ENSAYOS_DISENO_CONDUCTO.md`) que no
esperan decision del dueño. Los casos son los del revisor, DATOS DE PRUEBA
rotulados (`/home/user/ensayos_conducto_casos/escenarios.py`), no del
proyecto.

H4 -- V7 SUMA EL PESO PROPIO DEL TUBO DE CONCRETO. La fila V7 de la hoja de
ruta (Fase 5) escribe «γ_DC,min · DC + γ_EV,min · EV ≥ γ_WA · U … la forma
0.90·(DC + EV) ≥ 1.00·U», y el codigo ponia DC = 0 porque «la densidad no la
declara nadie»; el proyecto declara `peso_especifico_concreto_kn_m3`
(23.56 kN/m3, [C], AASHTO Tabla 3.5.1-1). DC = γ_c · (A_exterior −
A_interior). Para TMC y HDPE no hay peso del producto declarado y DC sigue
en cero, dicho en el paso. MT08 del revisor: el concreto Ø 2.10 fallaba V7
por 0.34 kN/m sin su peso.

H2 -- V1 BAJO CONTROL DE ENTRADA CON EL RESALTO DENTRO DEL BARRIL. Con
pendiente fuerte y TW entre 0.75·D y D, si el TW supera el conjugado del
tirante normal el resalto se forma dentro del conducto (HDS-5 3.1.3, pag.
impresa 3.2: «submergence of the outlet end of the culvert does not assure
outlet control … a hydraulic jump forms in the culvert barrel») y aguas
abajo de el la lamina esta al nivel del TW. V1 tomaba el tirante normal y el
rechazo saltaba recien en TW = D, contra la nota T-2 de la hoja de ruta («La
lectura es una sola a lo largo del TW: no cambia al cruzar TW = D»). E13 del
revisor: Q 0.60 m3/s, S 0.030, Ø 0.90, TW 0.80 m (conjugado 0.729 m).

SE ESCRIBIO EN ROJO PRIMERO, contra 33bd7fc.
"""

from __future__ import annotations

import math

import pytest

from src import criterios_adoptados as ca
from src.modelos import (ControlGobernante, Familia, PuntoCritico,
                         SeccionCircular, TipoMaterial)
from src.modulos.M2_material import catalogo, espesor_pared
from src.modulos.M4_control import resolver_control
from src.modulos.M5_verificaciones import (cota_clave, v1_borde_libre,
                                           v7_flotacion)
from src.modulos.M3_hidraulica import tirante_conjugado_barril
from src.modulos.M8_estructural import (factores_carga_flotacion,
                                        peso_propio_conducto_kn_m)
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import con_valor
from tests.test_M5_verificaciones import _punto, _resultado

GAMMA_RELLENO_PRUEBA = 18.0          # kN/m3, dato de prueba (como en test_M5)
# El revisor imprimio el conjugado con tres decimales (0.729 m): la mitad de
# la ultima cifra es la tolerancia con que se compara su lectura.
MEDIO_MILIMETRO = 5e-4

# --- E13 / barrido MU del revisor (datos de prueba) ------------------------
Q_E13 = 0.60
S_E13 = 0.030
L_E13 = 22.570212765957436          # la longitud que 7.B dio en la corrida
D_E13 = 0.90


def _concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


# ===========================================================================
# H4 -- el peso propio del tubo de concreto entra en V7
# ===========================================================================

def _dc_concreto(D: float) -> float:
    t = espesor_pared(_concreto(), D)
    sec = SeccionCircular(D=D)
    gamma_c = ca.valor("peso_especifico_concreto_kn_m3")
    return gamma_c * (sec.area_exterior(t) - sec.area_llena)


def test_v7_suma_el_peso_propio_del_concreto():
    with con_valor("peso_especifico_relleno_kn_m3", GAMMA_RELLENO_PRUEBA,
                   motivo="dato de prueba"):
        v = v7_flotacion(punto=_punto(), material=_concreto(),
                         seccion=SeccionCircular(D=0.90),
                         resultado=_resultado())
        g = factores_carga_flotacion(material=_concreto())
    EV = GAMMA_RELLENO_PRUEBA * 1.10 * 0.95      # Bc = 1.10 m, h = 0.95 m
    DC = _dc_concreto(0.90)
    assert DC > 0
    assert v.valor_obtenido == pytest.approx(g.gamma_DC * DC + g.gamma_EV * EV,
                                             rel=REL_TRANSPORTE)
    dc = {m.simbolo: m for m in v.paso.sustitucion}["DC"]
    assert dc.valor == pytest.approx(DC, rel=REL_TRANSPORTE)
    assert "OMITIDO" not in dc.procedencia


def test_v7_del_tmc_sigue_sin_peso_propio_y_lo_dice():
    tmc = catalogo(TipoMaterial.TMC)
    with con_valor("peso_especifico_relleno_kn_m3", GAMMA_RELLENO_PRUEBA,
                   motivo="dato de prueba"):
        v = v7_flotacion(punto=_punto(), material=tmc,
                         seccion=SeccionCircular(D=0.90),
                         resultado=_resultado())
    dc = {m.simbolo: m for m in v.paso.sustitucion}["DC"]
    assert dc.valor == pytest.approx(0.0, abs=ABS_CERO)
    assert "peso del producto" in dc.procedencia


def test_mt08_el_concreto_que_solo_fallaba_por_omitir_su_peso_cumple():
    """
    Un concreto Ø 2.10 m con el relleno justo para que 0.90·EV quede un 3 %
    por debajo de U (el caso MT08 del revisor: fallaba por 0.34 kN/m): con su
    peso propio cumple.
    """
    D = 2.10
    mat = _concreto()
    sec = SeccionCircular(D=D)
    t = espesor_pared(mat, D)
    U = 9.81 * sec.area_exterior(t)
    Bc = sec.ancho_exterior(t)
    g = factores_carga_flotacion(material=mat)
    h = 0.97 * U / (g.gamma_EV * GAMMA_RELLENO_PRUEBA * Bc)
    base = _punto()
    clave = cota_clave(punto=base, material=mat, seccion=sec)
    punto = _punto(cota_subrasante=clave + h, cota_rasante=clave + h + 0.15)
    with con_valor("peso_especifico_relleno_kn_m3", GAMMA_RELLENO_PRUEBA,
                   motivo="dato de prueba"):
        v = v7_flotacion(punto=punto, material=mat, seccion=sec,
                         resultado=_resultado())
    EV = {m.simbolo: m.valor for m in v.paso.sustitucion}["EV"]
    assert g.gamma_EV * EV < v.valor_admisible        # sin DC no cumplia
    assert v.cumple


# ===========================================================================
# H2 -- V1 con el resalto dentro del barril bajo control de entrada
# ===========================================================================

def _e13(TW: float):
    return resolver_control(SeccionCircular(D=D_E13), Q_E13, S_E13, L_E13,
                            TW, _concreto())


def _punto_e13() -> PuntoCritico:
    return _punto(id="E13", Q_m3s=Q_E13, S_cauce=S_E13)


def test_e13_el_resalto_queda_dentro_del_barril_y_v1_no_cumple():
    r = _e13(0.80)
    assert r.control_gobernante is ControlGobernante.ENTRADA
    assert r.resalto_en_el_barril
    assert r.y_conjugado_m == pytest.approx(0.729, abs=MEDIO_MILIMETRO)
    v = v1_borde_libre(D=D_E13, material=_concreto(), punto=_punto_e13(),
                       resultado=r)
    assert not v.cumple
    sustituidas = {m.simbolo: m.valor for m in v.paso.sustitucion}
    assert "y_max" in sustituidas
    assert sustituidas["y_max"] == pytest.approx(0.80, rel=REL_TRANSPORTE)


def test_con_el_tw_bajo_el_conjugado_el_resalto_sale_y_v1_usa_el_normal():
    r = _e13(0.70)
    assert r.control_gobernante is ControlGobernante.ENTRADA
    assert not r.resalto_en_el_barril
    v = v1_borde_libre(D=D_E13, material=_concreto(), punto=_punto_e13(),
                       resultado=r)
    assert v.cumple
    assert "y_normal" in {m.simbolo for m in v.paso.sustitucion}


@pytest.mark.parametrize("TW", [0.80, 0.85, 0.89, 0.90, 1.00])
def test_la_lectura_no_cambia_al_cruzar_tw_igual_a_D(TW):
    """El barrido MU del revisor: con el resalto dentro, no cumple a ambos
    lados de TW = D (bajo la lectura de archivo, `no_cumple`)."""
    r = _e13(TW)
    v = v1_borde_libre(D=D_E13, material=_concreto(), punto=_punto_e13(),
                       resultado=r)
    assert not v.cumple


def test_bajo_aviso_el_caudal_propio_decide_y_el_diametro_no_se_descarta():
    r = _e13(0.80)
    with con_valor("borde_libre_bajo_tw_ahogante", "aviso",
                   motivo="la otra lectura de la ventana"):
        v = v1_borde_libre(D=D_E13, material=_concreto(), punto=_punto_e13(),
                           resultado=r)
    assert v.cumple


# ===========================================================================
# H6 -- el titular del «no factible» nombra la causa real
# ===========================================================================

def test_e12_v2_en_todo_diametro_no_es_no_factible_por_rasante():
    """
    El alivio E12 del revisor: V2 no cumple en NINGUN escalon (la velocidad
    cae al crecer el diametro) y la progresion termina ademas bajo la
    subrasante. El titular decia «NO FACTIBLE POR RASANTE»; ahora nombra V2.
    Verificador de prueba: V2 incumplida en todo escalon y el relleno pesado
    por M5, que levanta su `DatoInvalidoError` cuando la clave no cabe (como
    `tests/test_t11_no_factible_por_rasante.py::_GeometriaReal`).
    """
    from src.modelos import (DatoFaltanteError, DatoInvalidoError,
                             DisenoNoFactibleError, Verificacion)
    from src.modulos import M5_verificaciones as M5
    from src.modulos import MD
    from tests.test_MD import L_CONDUCTO, TW_LIBRE

    def v2_nunca(*, punto, material, seccion, resultado):
        hechas = (Verificacion(cumple=False, numeral="4.1.1.3.7 a)",
                               valor_obtenido=None, valor_admisible=None,
                               criterio_aplicado=None, codigo="V2"),)
        try:
            M5.altura_relleno_sobre_clave(punto=punto, material=material,
                                          seccion=seccion)
        except (DatoInvalidoError, DatoFaltanteError) as exc:
            exc.verificaciones_completadas = hechas
            raise
        return hechas

    with pytest.raises(DisenoNoFactibleError) as excinfo:
        MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                         verificar=v2_nunca)
    motivo = excinfo.value.motivo
    assert "NO FACTIBLE POR RASANTE" not in motivo
    assert "NO FACTIBLE POR V2" in motivo
    assert "crecer el diametro no lo resuelve" in motivo
    assert excinfo.value.delta_rasante_m is None


# ===========================================================================
# H3 (b) -- el delta de 7.A se rotula si con esa rasante V7 seguiria fallando
# ===========================================================================

def test_el_delta_de_7A_se_rotula_si_v7_seguiria_sin_cumplir():
    """
    El escenario de T11-03 (`tests/test_t11_no_factible_por_rasante.py`):
    el punto lleva el delta del TMC Ø 1.95 m (0.31981 m, recubrimiento), y
    ese escalon no tiene V7 evaluada porque no cabia. Con el peso del relleno
    declarado (dato de prueba), V7 pide para el mucho mas relleno que el
    recubrimiento: la nota lo dice, con el delta que daria. El delta del
    punto NO cambia (la regla de T11-03).
    """
    from src.modelos import DisenoNoFactibleError
    from src.modulos import MD
    from tests.test_MD import L_CONDUCTO, TW_LIBRE
    from tests.test_t11_no_factible_por_rasante import _GeometriaReal

    def solo_el_que_no_cabe(material, D):
        return D > (1.85 if material.tipo is TipoMaterial.TMC else 1.70)

    with con_valor("peso_especifico_relleno_kn_m3", GAMMA_RELLENO_PRUEBA,
                   motivo="dato de prueba"):
        with pytest.raises(DisenoNoFactibleError) as excinfo:
            MD.disenar_punto(_punto(), L=L_CONDUCTO, TW=TW_LIBRE,
                             verificar=_GeometriaReal(solo_el_que_no_cabe))
    exc = excinfo.value
    # El delta del punto sigue siendo el de 7.A (geometria pura); el rotulo
    # dice que con el V7 de ese escalon seguiria sin cumplir.
    assert exc.delta_rasante_m is not None
    assert "SEGUIRIA SIN CUMPLIR V7" in exc.motivo


# ===========================================================================
# Las dos funciones nuevas, contra su forma cerrada
# ===========================================================================

# Precision de la cuadratura del primer momento (`PUNTOS_MOMENTO_SECCION`):
# 1e-6 relativo es un orden por encima de lo medido (~1e-7) y muy por debajo
# de lo que distingue un TW de su conjugado.
REL_CUADRATURA_MOMENTO = 1e-6


def test_el_conjugado_del_barril_rectangular_es_el_de_belanger():
    """
    En un barril rectangular el conjugado tiene forma cerrada (Belanger):
    y2 = (y1/2)(sqrt(1 + 8 Fr1^2) - 1), Fr1 = V1 / sqrt(g y1). La funcion
    generica, con su cuadratura del primer momento, lo reproduce.
    """
    from src.modelos import SeccionRectangular
    B, H, Q, y1 = 1.20, 1.50, 1.0, 0.20
    sec = SeccionRectangular(B=B, H=H)
    q = Q / B
    y_c = (q * q / 9.81) ** (1 / 3)
    Fr1 = (q / y1) / math.sqrt(9.81 * y1)
    y2 = (y1 / 2) * (math.sqrt(1 + 8 * Fr1 ** 2) - 1)
    assert tirante_conjugado_barril(Q=Q, seccion=sec, y=y1, y_c=y_c) == \
        pytest.approx(y2, rel=REL_CUADRATURA_MOMENTO)


def test_el_conjugado_que_no_cabe_en_el_barril_es_none():
    from src.modelos import SeccionRectangular
    sec = SeccionRectangular(B=1.20, H=0.60)
    q = 1.0 / 1.20
    y_c = (q * q / 9.81) ** (1 / 3)
    assert tirante_conjugado_barril(Q=1.0, seccion=sec, y=0.10, y_c=y_c) is None


def test_el_peso_propio_es_el_del_anillo_de_concreto():
    mat = _concreto()
    sec = SeccionCircular(D=0.90)
    t = espesor_pared(mat, 0.90)
    DC, texto = peso_propio_conducto_kn_m(material=mat, seccion=sec, espesor=t)
    assert DC == pytest.approx(
        ca.valor("peso_especifico_concreto_kn_m3")
        * (math.pi / 4) * ((0.90 + 2 * t) ** 2 - 0.90 ** 2),
        rel=REL_CUADRATURA_MOMENTO)
    assert "peso_especifico_concreto_kn_m3" in texto
