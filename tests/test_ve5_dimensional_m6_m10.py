# -*- coding: utf-8 -*-
"""
EL CHEQUEO DIMENSIONAL, EXTENDIDO A M6-M10 (VE-5, fichas I4-01 (b), T10-02 y
T11-06; ítem 47 del censo del 2026-11-20).

El piloto de I4 (`tests/test_dimensional_piloto.py`) mira los pasos de M3, M4
y M5 de SU corrida, que no alcanzaba M6-M10. Desde T-10 y T-11 las tres
corridas de referencia del indice de formulas (`indice_formulas.
CORRIDAS_DE_REFERENCIA`) SI los alcanzan: medido al escribir esto, 401 pasos
(M9 244, M7 74, M6 43, M8 31, M10 9). Este archivo les aplica las dos
comprobaciones del piloto que NO necesitan una relacion escrita a mano por
paso:

  1. toda unidad que una sustitucion, un resultado o un umbral declara tiene
     dimension en el mapa (el del piloto, mas las unidades propias de estas
     fases, que se declaran aqui con su razon);
  2. todo umbral es conmensurable con el resultado que juzga.

Las RELACIONES por paso (la tercera comprobacion del piloto: que la formula
cierre dimensionalmente con lo que sustituye) siguen sin escribirse para
M6-M10: son 401 pasos y se escriben a mano desde la formula impresa. Queda en
la ficha I4-01 con este numero.
"""

from __future__ import annotations

from fractions import Fraction as F
from typing import Dict

import pytest

pytestmark = pytest.mark.lento

from src import indice_formulas as ind
from tests.test_dimensional_piloto import ADIM, L, M, T, UNIDADES, Dim

MODULOS = ("M6_proteccion", "M7_geometria", "M8_estructural", "M9_cabezal",
           "M10_espaciamiento")

# Las unidades que aparecen en M6-M10 y no en M3-M5, cada una con su
# dimension. Viven aqui por la misma razon que el mapa del piloto: es una
# guardia de la suite, no un valor de proyecto.
UNIDADES_DE_M6_A_M10: Dict[str, Dim] = {
    **UNIDADES,
    "-": ADIM,                          # adimensional escrito con guion
    "km": L,                            # progresivas de la Fase 10
    "km2": L ** 2,                      # area de cuenca
    "mm2/m": L,                         # area de acero por metro de ancho
    "kN·m/m": M * L / T ** 2,           # momento por metro de ancho
    "N/m/mm": M / (L * T ** 2),         # D-load: fuerza por metro y por mm de diametro
    "m3/s por m": L ** 2 / T,           # caudal por metro de cuneta
    "m3/s por km2": L / T,              # caudal especifico
    # --- VE-7, lote C (C6) --- las que trae la cuarta corrida de referencia
    # (el TMC y el HDPE en la Fase 8, el filtro y la hoya de la Fase 6).
    "mm2/mm": L,                        # area de pared por mm de longitud
    "mm4/mm": L ** 3,                   # inercia de pared por mm de longitud
    "mm/N": T ** 2 / M,                 # factor de flexibilidad (D^2/(E*I))
    "s-1": ADIM / T,                    # permitividad del geotextil
    "min": T,                           # duracion del caudal pico
    # --- VE-7 (dictamen Fable, (i-c)) --- la quinta corrida: el s_xe del
    # cortante del armado (AASHTO 5.7.3.4.2) se imprime en pulgadas.
    "in": L,
}


@pytest.fixture(scope="module")
def pasos_de_m6_a_m10():
    emisores = ind.emisores_por_fundamento()
    pasos = []
    for referencia in ind.CORRIDAS_DE_REFERENCIA:
        for paso in ind.pasos_de_la_corrida(ind.correr_referencia(referencia)):
            modulos = [m for m in emisores.get(paso.fundamento_id, ()) if m in MODULOS]
            if modulos:
                pasos.append((tuple(modulos), paso))
    return tuple(pasos)


def test_las_corridas_de_referencia_alcanzan_los_cinco_modulos(pasos_de_m6_a_m10):
    alcanzados = {m for modulos, _p in pasos_de_m6_a_m10 for m in modulos}
    assert alcanzados == set(MODULOS), alcanzados


def test_toda_unidad_de_M6_a_M10_tiene_dimension(pasos_de_m6_a_m10):
    sin_dimension = {}
    for _modulos, paso in pasos_de_m6_a_m10:
        magnitudes = paso.sustitucion + (paso.resultado,)
        unidades = [m.unidad for m in magnitudes]
        if paso.umbral is not None:
            unidades.append(paso.umbral.unidad)
        for unidad in unidades:
            if unidad not in UNIDADES_DE_M6_A_M10:
                sin_dimension.setdefault(unidad, f"{paso.fundamento_id}@{paso.codigo}")
    assert not sin_dimension, sin_dimension


def test_las_unidades_de_presentacion_son_de_la_dimension_que_dicen():
    """El mapa probandose: lo que es la misma magnitud tiene la misma dimension."""
    assert UNIDADES_DE_M6_A_M10["kN·m/m"] == UNIDADES["kN"]
    assert UNIDADES_DE_M6_A_M10["N/m/mm"] == UNIDADES["kN/m2"]
    assert UNIDADES_DE_M6_A_M10["m3/s por m"] * L == UNIDADES["m3/s"]
    assert UNIDADES_DE_M6_A_M10["mm2/m"] ** F(2) == L ** 2


def test_todo_umbral_de_M6_a_M10_es_conmensurable_con_su_resultado(pasos_de_m6_a_m10):
    inconmensurables = {}
    for _modulos, paso in pasos_de_m6_a_m10:
        if paso.umbral is None:
            continue
        r = UNIDADES_DE_M6_A_M10[paso.resultado.unidad]
        u = UNIDADES_DE_M6_A_M10[paso.umbral.unidad]
        if r != u:
            inconmensurables[f"{paso.fundamento_id}@{paso.codigo}"] = (
                paso.resultado.unidad, paso.umbral.unidad)
    assert not inconmensurables, inconmensurables
