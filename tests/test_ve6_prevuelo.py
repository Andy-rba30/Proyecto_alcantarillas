# -*- coding: utf-8 -*-
"""
tests/test_ve6_prevuelo.py
==========================
VE-6 (pre-vuelo): las dos causas que la integracion de VE-5 dejo en rojo.

(a) M12 y `NF_profundidad_m`. El censo de `variables_entrada` le encuentra
    la columna a M12 (`renglones_excavacion`, partida 501.C/D), y M12 no se
    difiere entero a perfil: la fila del cuadro de compatibilidad corre en
    los dos alcances. El pre-vuelo le atribuia por eso la columna a nivel de
    perfil y la anunciaba como DATO QUE DETIENE en todos los puntos, y la
    corrida real no se detenia por ella: los metrados van detras de la Fase
    9. Desde VE-6 los dos leen el mismo dato, `servicio.CONSUMO_DETRAS_DE`.

(b) La Fase 0-bis (licuefaccion, ficha VE5-CAT-03) se registra AL LADO del
    dimensionado, sin anteponerse: la corrida sigue diciendo las faltas del
    bucle de MD, y quien busca por que un punto no llego a 7.A (la fila del
    cuadro de compatibilidad) salta esa fase.
"""

from __future__ import annotations

import ast
import inspect

import cli
from src import anticipo as antc
from src import servicio

NF = "NF_profundidad_m"


# --- (a) ------------------------------------------------------------------

def test_a_perfil_m12_no_consume_y_a_expediente_si():
    assert "M12_metrados" in antc._ve.variable(NF).consumido_por
    assert "M12_metrados" not in servicio.MODULOS_DIFERIDOS_POR_ALCANCE[
        cli.ALCANCE_PERFIL]
    assert servicio.consumo_diferido(cli.ALCANCE_PERFIL, "M12_metrados")
    assert not servicio.consumo_diferido(cli.ALCANCE_EXPEDIENTE, "M12_metrados")
    assert "M12_metrados" not in antc._consumidores_de_calculo(
        NF, cli.ALCANCE_PERFIL)
    assert "M12_metrados" in antc._consumidores_de_calculo(
        NF, cli.ALCANCE_EXPEDIENTE)


def test_el_salto_de_los_metrados_consulta_el_mismo_dato():
    """El `if` de `correr_punto` que salta los metrados llama a
    `consumo_diferido` con M12: no hay una segunda regla escrita aparte."""
    arbol = ast.parse(inspect.getsource(servicio.correr_punto))
    llamadas = [n for n in ast.walk(arbol) if isinstance(n, ast.If)
                and any(isinstance(c, ast.Call)
                        and getattr(c.func, "id", "") == "consumo_diferido"
                        and any(isinstance(a, ast.Constant)
                                and a.value == "M12_metrados" for a in c.args)
                        for c in ast.walk(n.test))
                and any(isinstance(c, ast.Call)
                        and getattr(c.func, "id", "") == "_fase_11_metrados"
                        for b in n.body for c in ast.walk(b))]
    assert len(llamadas) == 1


def test_la_relacion_es_la_que_test_nivel_medido_usa_para_los_criterios():
    from tests.test_nivel_medido import DETRAS_DEL_CABEZAL
    assert set(DETRAS_DEL_CABEZAL.values()) == {
        servicio.CONSUMO_DETRAS_DE["M12_metrados"]}
