"""
tests/test_ve5_m45_v9_designado.py
==================================
VE-5, lote m45, item 24 (fichas VE2-G y T4-02).

(1) CON LA SERIE INGLESA, V9 Y EL TOPE COMPARAN EL DIAMETRO DESIGNADO
(decision adoptada en el censo). AASHTO M 170M num. 12.1 (cita
AASHTO_M170M.12.1) deja al fabricante diseñar con «the designated diameter
or the converted English diameter», y la Table 6 (AASHTO_M170M.T6) da el par:
el tubo de 108 in (2743 mm) ES el designado de 2700 mm. Hasta VE-5 el tope
de 2.70 m y V9 comparaban el diametro de calculo, y el escalon de 108 in
quedaba fuera de la serie a la que pertenece.

(2) EL CONCRETO DE 2850 A 3600 MM: el ejemplar de M 170M no deja leer las
seis filas de la Table 6 (releidas por imagen en VE-5: 2830 por 2850, iM8,
3333, U38, 3S05 y la ultima ilegible entera), y la norma no tabula diseño
estandar por encima de 2700 mm (ficha T4-02). Sigue como hoy: el tope es
2.70 m y la tabla, `Acotada`.

SE ESCRIBIO EN ROJO PRIMERO: `M2.diametro_designado` no existia y la
progresion inglesa terminaba en 2.5908 m.
"""

from __future__ import annotations

import pytest

from src.modelos import FormaSeccion, TipoMaterial
from src.modulos import M2_material as M2
from src.modulos.M5_verificaciones import v9_disponibilidad_diametro
from src.normativa import registro as _registro
from src.normativa.esquema import Acotada
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.test_ve2_materiales import (DIAMETRO_DE_DISENO, SERIE_6_IN,
                                       _recorrido)

CONCRETO = TipoMaterial.CONCRETO_REFORZADO
INGLES = {M2.CRITERIO_DIAMETROS: SERIE_6_IN,
          DIAMETRO_DE_DISENO: "designado_o_ingles_convertido"}
D_108_IN = 2.7432


@pytest.mark.parametrize("D, designado", [
    (D_108_IN, 2.70), (2.743, 2.70), (1.0668, 1.05), (0.9144, 0.90),
    (0.90, 0.90), (2.70, 2.70)])
def test_el_designado_de_un_diametro_ingles_es_el_de_su_fila(D, designado):
    assert M2.diametro_designado(CONCRETO, D) == pytest.approx(
        designado, rel=REL_TRANSPORTE)


@pytest.mark.parametrize("tipo", [TipoMaterial.TMC, TipoMaterial.HDPE])
def test_fuera_del_concreto_no_hay_ingles_convertido(tipo):
    D = 0.9144
    assert M2.diametro_designado(tipo, D) == pytest.approx(D, rel=REL_TRANSPORTE)


def test_la_serie_inglesa_del_concreto_llega_al_designado_de_2700():
    with declarados(INGLES):
        recorrido = _recorrido(CONCRETO)
    assert recorrido[-1] == repr(D_108_IN)


def test_v9_compara_el_designado():
    with declarados(INGLES):
        material = M2.catalogo(CONCRETO, forma=FormaSeccion.CIRCULAR)
        v = v9_disponibilidad_diametro(D=D_108_IN, material=material)
    assert material.D_max == pytest.approx(2.70, rel=REL_TRANSPORTE)
    assert v.cumple
    assert v.valor_obtenido == pytest.approx(D_108_IN, rel=REL_TRANSPORTE)
    sustitucion = {m.simbolo: m.valor for m in v.paso.sustitucion}
    assert sustitucion["D"] == pytest.approx(D_108_IN, rel=REL_TRANSPORTE)
    assert sustitucion["D_designado"] == pytest.approx(2.70, rel=REL_TRANSPORTE)
    assert "AASHTO_M170M.12.1" in v.paso.citas_textuales


def test_v9_con_el_designado_no_imprime_dos_diametros():
    material = M2.catalogo(CONCRETO, forma=FormaSeccion.CIRCULAR)
    v = v9_disponibilidad_diametro(D=2.70, material=material)
    assert v.cumple
    assert "D_designado" not in {m.simbolo for m in v.paso.sustitucion}


def test_el_concreto_de_2850_a_3600_sigue_fuera_y_la_tabla_acotada():
    t6 = _registro.construir().tabla("AASHTO_M170M.T6")
    assert isinstance(t6.alcance, Acotada)
    assert max(f.valores["dn_mm"] for f in t6.filas) == 2700
    material = M2.catalogo(CONCRETO, forma=FormaSeccion.CIRCULAR)
    assert material.D_max == pytest.approx(2.70, rel=REL_TRANSPORTE)
    assert M2.siguiente_diametro(CONCRETO, 2.70) is None
