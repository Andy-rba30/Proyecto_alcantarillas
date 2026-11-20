"""
tests/test_ve5_v7_marco.py
==========================
VE-5 (lote m8), item 26 del censo (T3-08; T7V-01 y T8-08 del mismo item son
D y no se hacen): V7 del MARCO pesa su concreto con el gamma MINIMO. La
decision del dueño (censo del 2026-11-20): «contar el DC del marco con gamma
minimo». VE-3.11 ya lo habia cableado para el tubo y el marco de concreto
(`M8.peso_propio_conducto_kn_m`), y la ficha T3-08 y el alcance declarado
seguian diciendo DC = 0: aqui se fija por medicion y se retira la entrada
`flotacion_marco_sin_peso_propio` del alcance.

    DC = gamma_c (A_exterior - A_interior),  con gamma_DC,min = 0.90
    (fila «DC: Componentes y Auxiliares» de la Tabla 2.4.5.3.1-2)
"""

import pytest

from src import constantes_normativas as CN
from src import criterios_adoptados as ca
from src.modelos import (ALCANCE_DECLARADO, FormaSeccion, SeccionRectangular,
                         TipoMaterial)
from src.modulos import M5_verificaciones as M5
from src.modulos import M8_estructural as M8
from src.modulos.M2_material import catalogo, espesor_pared
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.fixtures.casos_patron import CP_FASE_8_ESTRUCTURAL as CP

DECLARACIONES_CAJON = {
    "embocadura_cajon": "cajon_concreto_aletas_30_75",
    "n_manning_cajon": "concreto_afinado",
    "n_celdas_cajon": 1,
    "ke_entrada_cajon": "cajon_aletas_30_75_escuadra",
    "secciones_cajon_normalizadas": ((1.50, 1.20), (2.00, 1.50)),
    "espesor_pared_cajon": 0.20,
}


def test_v7_del_marco_suma_su_peso_propio_con_el_gamma_minimo():
    a01 = CP["punto_A01"]()
    sec = SeccionRectangular(B=1.50, H=1.20)
    with declarados(DECLARACIONES_CAJON):
        marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                         forma=FormaSeccion.RECTANGULAR)
        t = espesor_pared(marco, sec.altura)
        v = M5.v7_flotacion(punto=a01, material=marco, seccion=sec,
                            resultado=None)
        g = M8.factores_carga_flotacion(material=marco)
    sust = {m.simbolo: m.valor for m in v.paso.sustitucion}
    gamma_c = ca.CRITERIOS["peso_especifico_concreto_kn_m3"].valor
    DC = gamma_c * ((1.50 + 2 * t) * (1.20 + 2 * t) - 1.50 * 1.20)
    assert sust["DC"] == pytest.approx(DC, rel=REL_TRANSPORTE)
    assert g.gamma_DC == pytest.approx(
        CN.TABLA_GAMMA_P_FILAS[M8.FILA_GAMMA_P_DC]["min"], rel=REL_TRANSPORTE)
    assert sust["gamma_DC_min"] == pytest.approx(g.gamma_DC,
                                                 rel=REL_TRANSPORTE)
    assert DC > 0


def test_el_alcance_declarado_ya_no_dice_que_el_marco_no_se_pesa():
    assert "flotacion_marco_sin_peso_propio" not in {
        a.clave for a in ALCANCE_DECLARADO}
