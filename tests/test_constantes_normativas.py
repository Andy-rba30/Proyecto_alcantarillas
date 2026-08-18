"""
tests/test_constantes_normativas.py
===================================
Contrasta el Anexo B contra los casos patron. No reescribe los valores: los
compara con los del fixture, que fueron recalculados de forma independiente.

El test que mas importa es el de la constante de friccion del control de
salida: usar 29 (valor ingles) en vez de 19.62 no falla ruidosamente, devuelve
numeros plausibles y equivocados (Sec. 4.3).
"""

import math

import pytest

import constantes_normativas as CN
import datos_sitio as ds
from tests.fixtures.casos_patron import (CP1_PERIODO_RETORNO,
                                         CP2_GEOMETRIA_MANNING,
                                         CP3_VELOCIDAD_MINIMA, CP4_LAUSHEY,
                                         CP5_TRANSICION_HDS5, CP5B_NO_SUMERGIDO,
                                         CP5C_SUMERGIDO, CP7_CADENA_SISMICA,
                                         CP8_CONTROL_SALIDA)


# ---------------------------------------------------------------------------
# CP-8 - la constante del control de salida es SI, no imperial
# ---------------------------------------------------------------------------

def test_la_constante_de_friccion_es_SI_y_no_imperial():
    cp = CP8_CONTROL_SALIDA
    assert CN.K_FRICCION_SI == pytest.approx(cp["K_friccion_SI_correcto"])
    assert CN.K_FRICCION_SI != pytest.approx(cp["K_friccion_imperial_incorrecto"])


def test_la_constante_SI_reproduce_la_H_del_caso_patron():
    """
    H = (1 + ke + K*n^2*L/R^(4/3)) * V^2/(2g). Con los datos de CP-8 la
    diferencia entre 19.62 y 29 es de ~9.6%: plausible a ojo, detectable aqui.
    """
    cp = CP8_CONTROL_SALIDA

    def perdida(k):
        friccion = k * cp["n"] ** 2 * cp["L"] / cp["R"] ** (4 / 3)
        return (1 + cp["ke"] + friccion) * cp["V"] ** 2 / (2 * CN.G)

    assert perdida(CN.K_FRICCION_SI) == pytest.approx(
        cp["H_esperado_con_19_62"], abs=1e-3)
    assert perdida(cp["K_friccion_imperial_incorrecto"]) == pytest.approx(
        cp["H_con_29_incorrecto"], abs=1e-3)
    assert perdida(CN.K_FRICCION_SI) < perdida(cp["K_friccion_imperial_incorrecto"])


# ---------------------------------------------------------------------------
# CP-1 - periodo de retorno
# ---------------------------------------------------------------------------

def test_el_riesgo_admisible_reproduce_los_TR_de_CP1():
    pares = [("quebrada_importante", CP1_PERIODO_RETORNO[0]),
             ("quebrada_menor", CP1_PERIODO_RETORNO[1])]
    for clave, caso in pares:
        entrada = CN.RIESGO_ADMISIBLE[clave]
        assert entrada["R"] == pytest.approx(caso["R"])
        assert entrada["n"] == caso["n"]
        TR = 1 / (1 - (1 - entrada["R"]) ** (1 / entrada["n"]))
        assert TR == pytest.approx(caso["TR_esperado"], abs=caso["tolerancia"])


def test_no_hay_piso_normativo_de_TR():
    """No adoptar 50 anios 'por costumbre': el Anexo B no declara ningun piso."""
    assert not [k for k in dir(CN) if k.upper().startswith("TR_MIN")]


# ---------------------------------------------------------------------------
# CP-2 y CP-3 - limites hidraulicos
# ---------------------------------------------------------------------------

def test_el_diametro_minimo_y_el_llenado_maximo_son_los_de_CP2():
    assert CN.DIAMETRO_MIN == pytest.approx(CP2_GEOMETRIA_MANNING["D"])
    assert CN.Y_SOBRE_D_MAX == pytest.approx(CP2_GEOMETRIA_MANNING["y_sobre_D"])


def test_el_n_del_concreto_es_el_par_de_CP2():
    n_min, n_max = CN.MANNING["concreto_recto"]
    assert n_min == pytest.approx(CP2_GEOMETRIA_MANNING["n_min"])
    assert n_max == pytest.approx(CP2_GEOMETRIA_MANNING["n_max"])


def test_la_velocidad_minima_es_la_de_CP3():
    assert CN.V_MIN == pytest.approx(CP3_VELOCIDAD_MINIMA["V_objetivo"])


def test_V2_nunca_gobierna_con_pendientes_constructivas():
    """
    Sec. 5.2: con D=0.90, y/D=0.75 y n=0.013, V_MIN se alcanza con
    S ~ 6e-5, muy por debajo de cualquier pendiente constructiva.
    """
    cp = CP3_VELOCIDAD_MINIMA
    R = CP2_GEOMETRIA_MANNING["R_esperado"]
    V = (1 / cp["n"]) * R ** (2 / 3) * cp["S_que_produce_V_objetivo"] ** 0.5
    assert V == pytest.approx(CN.V_MIN, abs=1e-3)
    assert cp["S_que_produce_V_objetivo"] < cp["S_constructiva_minima_referencia"]


# ---------------------------------------------------------------------------
# CP-4 - Laushey
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("caso", CP4_LAUSHEY)
def test_laushey_reproduce_los_d50_de_CP4(caso):
    d50 = caso["V"] ** 2 / (CN.LAUSHEY_K * CN.G)
    assert d50 == pytest.approx(caso["d50_esperado"], abs=caso["tolerancia"])


# ---------------------------------------------------------------------------
# CP-5 - caudal adimensional y zonas de HDS-5
# ---------------------------------------------------------------------------

def test_el_caudal_adimensional_reproduce_CP5():
    cp = CP5_TRANSICION_HDS5
    assert CN.KU_METRICO == pytest.approx(cp["Ku"])
    A_llena = math.pi * cp["D"] ** 2 / 4
    assert A_llena == pytest.approx(cp["A_llena_esperada"], abs=cp["tolerancia"])
    q = CN.KU_METRICO * cp["Q"] / (A_llena * cp["D"] ** 0.5)
    assert q == pytest.approx(cp["q_estrella_esperado"], abs=cp["tolerancia"])
    assert CN.Q_LIM_NO_SUMERGIDO < q < CN.Q_LIM_SUMERGIDO      # zona de transicion


@pytest.mark.parametrize("cp, dentro", [(CP5B_NO_SUMERGIDO, "no_sumergido"),
                                        (CP5C_SUMERGIDO, "sumergido")])
def test_las_ramas_puras_caen_fuera_de_la_zona_de_transicion(cp, dentro):
    A_llena = math.pi * cp["D"] ** 2 / 4
    q = CN.KU_METRICO * cp["Q"] / (A_llena * cp["D"] ** 0.5)
    assert q == pytest.approx(cp["q_estrella_aprox"], abs=CP5_TRANSICION_HDS5["tolerancia"])
    if dentro == "no_sumergido":
        assert q <= CN.Q_LIM_NO_SUMERGIDO
    else:
        assert q >= CN.Q_LIM_SUMERGIDO


def test_las_cartas_hds5_distinguen_material_y_no_solo_borde():
    """
    Sec. 4.2.1: la misma configuracion 'square edge w/headwall' tiene K
    distinto en concreto y en metal corrugado. Si algun dia coinciden, alguien
    fusiono las cartas.
    """
    concreto = CN.HDS5_INLET["circular_concreto_square_edge_headwall"]
    cmp_ = CN.HDS5_INLET["circular_cmp_headwall"]
    assert concreto["K"] != pytest.approx(cmp_["K"])


def test_ninguna_carta_omite_Ks():
    """Ks no figura en la Tabla A.1 pero pertenece a la formulacion."""
    for clave, fila in CN.HDS5_INLET.items():
        assert "Ks" in fila, f"la carta '{clave}' omite Ks"
    assert CN.HDS5_INLET["circular_cmp_mitered"]["Ks"] > 0      # inglete: +0.7
    assert CN.HDS5_INLET["circular_concreto_square_edge_headwall"]["Ks"] < 0


# ---------------------------------------------------------------------------
# CP-7 - factores de sitio
# ---------------------------------------------------------------------------

def test_la_tabla_de_F_pga_contiene_la_eleccion_de_CP7():
    assert CN.F_PGA_TABLA["C"] == pytest.approx(CP7_CADENA_SISMICA["F_pga"])
    assert CN.F_PGA_TABLA["D"] == pytest.approx(CP7_CADENA_SISMICA["F_pga"])
    assert CN.F_PGA_TABLA["E"] < CP7_CADENA_SISMICA["F_pga"]    # 0.9 para clase E


def test_el_Z_de_E030_ya_no_es_una_constante_normativa():
    """
    Sigue siendo referencia que no gobierna el cabezal (Tr = 475 anios,
    Sec. 0.4), pero no es una constante [N]: "a este distrito le toca Zona 4,
    y a la Zona 4 le toca Z = 0.45" es la lectura de un mapa sobre las
    coordenadas de esta obra. Vive en datos_sitio.py como [S].
    """
    for nombre in ("Z_E030", "ZONA_SISMICA_LA_UNION", "PERFIL_SUELO_PRESUNTO"):
        assert not hasattr(CN, nombre), (
            f"'{nombre}' volvio al anexo de constantes normativas")

    assert ds.dato("Z_E030").etiqueta == "S"
    assert ds.dato("Z_E030").valor != pytest.approx(CP7_CADENA_SISMICA["PGA"])
    assert ds.dato("ZONA_SISMICA_LA_UNION").trazabilidad


def test_la_tabla_del_factor_de_muro_trae_sus_dos_filas():
    """
    Las dos filas del num. 2.8.1.1.14.2 son [N]: el numeral las fija. La
    eleccion entre ellas no esta aqui, es el criterio 'factor_muro_eleccion'.
    """
    assert CN.FACTOR_MURO_TABLA["rigido"] == pytest.approx(
        CP7_CADENA_SISMICA["factor_muro_rigido"])
    assert CN.FACTOR_MURO_TABLA["desplazable"] == pytest.approx(
        CP7_CADENA_SISMICA["factor_muro_desplazable"])
    assert CN.NUMERAL_FACTOR_MURO == "2.8.1.1.14.2"


# ---------------------------------------------------------------------------
# Topes de diametro y coherencia interna del anexo
# ---------------------------------------------------------------------------

def test_el_hdpe_es_el_material_con_el_tope_mas_restrictivo():
    assert CN.D_MAX["hdpe"] == min(CN.D_MAX.values())
    assert CN.D_MAX["hdpe"] < CN.D_MAX["tmc"] < CN.D_MAX["concreto_reforzado"]


def test_la_progresion_de_diametros_arranca_en_el_minimo_normativo():
    assert CN.D_INICIO == pytest.approx(CN.DIAMETRO_MIN)


def test_el_paso_de_0_15_reproduce_la_serie_de_6_pulgadas():
    """Sec. 3.2: el error contra 6" (0.1524 m) debe ser despreciable."""
    paso_6_pulgadas = 6 * 0.0254
    assert abs(CN.D_PASO - paso_6_pulgadas) / paso_6_pulgadas < 0.02


def test_arrancar_en_0_90_en_vez_de_36_pulgadas_es_conservador():
    """Sec. 3.2: subestima el area ~3%, del lado de la seguridad."""
    D_36_pulgadas = 36 * 0.0254
    assert CN.D_INICIO < D_36_pulgadas
    subestimacion = 1 - CN.D_INICIO ** 2 / D_36_pulgadas ** 2
    assert 0.02 < subestimacion < 0.04


def test_todos_los_topes_de_diametro_son_alcanzables_desde_la_progresion():
    for material, tope in CN.D_MAX.items():
        assert tope >= CN.D_INICIO, f"el tope de {material} es menor que el minimo"


def test_ningun_diametro_de_alcantarilla_alcanza_la_luz_de_puente():
    """Sec. 2.1: con luz >= 6.0 m la obra sale del alcance del script."""
    assert max(CN.D_MAX.values()) < CN.LUZ_MAX_ALCANTARILLA
    assert CN.DIAMETRO_MIN < CN.LUZ_MAX_ALCANTARILLA


def test_el_resguardo_por_CBR_cubre_todo_el_rango_sin_huecos():
    """num. 4.5.4: a peor CBR, mayor resguardo. Los tramos deben encadenar."""
    tramos = CN.RESGUARDO_NAPA_SUBRASANTE
    resguardos = [r for _, _, r in tramos]
    assert resguardos == sorted(resguardos), "el resguardo no crece al bajar el CBR"
    for (cbr_min, _, _), (_, cbr_max_siguiente, _) in zip(tramos, tramos[1:]):
        assert cbr_min == cbr_max_siguiente     # 20-6, 6-3, 3-...


def test_los_factores_de_seguridad_sismicos_son_menores_que_los_estaticos():
    for verificacion, valores in CN.FS.items():
        assert valores["sismico"] < valores["estatico"], verificacion
