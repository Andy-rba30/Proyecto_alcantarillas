# -*- coding: utf-8 -*-
"""
Lote VE5-GUI en la ventana de verdad (ítems 38, 40 y 49 del censo del
2026-11-20): lo que el doble de `tkinter` no puede ver. Corre
`tests/apoyo/gui_ve5_real.py` en un proceso limpio, con el mismo intérprete y
el mismo `xvfb-run` que los demás tests de ventana, y se salta diciendo por
qué si no hay ninguno que levante un `Tk`.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
TOPE_S = 600


@pytest.fixture(scope="module")
def ventana_real(tmp_path_factory):
    from tests.test_gui_contrato import _ENVOLTORIO, _INTERPRETE
    if _INTERPRETE is None:
        pytest.skip("ningun interprete disponible puede levantar una ventana "
                    "(falta tkinter, ttkbootstrap o el entorno grafico)")
    salida = tmp_path_factory.mktemp("ve5_ventana")
    hecho = subprocess.run(
        _ENVOLTORIO + [_INTERPRETE, "-m", "tests.apoyo.gui_ve5_real", str(salida)],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", timeout=TOPE_S)
    assert hecho.returncode == 0, (
        f"la ventana fallo:\n{hecho.stdout[-4000:]}\n{hecho.stderr[-4000:]}")
    return json.loads((salida / "resumen_ve5.json").read_text(encoding="utf-8"))


def test_38_la_ventana_se_mide_en_su_geometria_minima(ventana_real):
    import gui.app  # noqa: F401  (la geometria la fija el apoyo)
    if sys.platform == "win32":
        m_w, m_h = ventana_real["minsize"]
        g_w, g_h = ventana_real["geometria"]
        assert m_w >= 900 and m_h >= 620
        assert abs(g_w - m_w) <= 2 and abs(g_h - m_h) <= 2, (
            ventana_real["geometria"], ventana_real["minsize"])
    else:
        assert ventana_real["geometria"] == [900, 620]


def test_38_los_siete_exportadores_caben_a_900_px(ventana_real):
    for nombre, cabe in ventana_real["exportadores_900"].items():
        assert cabe == {"mapeado": True, "entero": True, "dentro": True}, nombre


def test_38_con_otra_letra_las_filas_se_parten_y_siguen_cabiendo(ventana_real):
    """
    El ancho de un boton depende de la tipografia de la pantalla: con la
    letra agrandada las filas se parten (lo que a 1100 px medido con otra
    letra salia cortado) y los siete siguen enteros y dentro.
    """
    for nombre, cabe in ventana_real["exportadores_letra_grande"].items():
        assert cabe == {"mapeado": True, "entero": True, "dentro": True}, nombre
    antes = ventana_real["filas_900"]
    despues = ventana_real["filas_letra_grande"]
    assert sum(map(len, despues)) > sum(map(len, antes))
    # Partir no reordena: los botones de cada grupo siguen en su orden.
    for filas in despues:
        orden = [i for fila in filas for i in fila]
        assert orden == sorted(orden)


def test_38_la_columna_derecha_de_la_pestana_2_se_desplaza_hasta_sus_botones(ventana_real):
    c = ventana_real["columna"]
    assert c["seleccionado"] == "n_manning_cajon"
    # Sin scroll el contenido no cabia: es lo que la ficha UI3-01 media.
    assert c["alto_contenido"] > c["alto_vista"]
    assert not all(c["visibles_arriba"].values())
    assert all(c["visibles_abajo"].values()), c["visibles_abajo"]


def test_40_los_tres_campos_existen_y_viajan_en_la_sesion(ventana_real):
    assert all(ventana_real["campos"].values())
    assert ventana_real["banderas"] == {"S_conducto": "0.004", "bombeo": None,
                                        "peralte": "-0.02"}
    assert ventana_real["sesion_externos"] == {"S_conducto": "0,004", "bombeo": "",
                                               "peralte": "-0,02"}


def test_40_una_sesion_de_formato_3_los_deja_vacios(ventana_real):
    assert ventana_real["tras_sesion_v3"] == {"S_conducto": "", "bombeo": "",
                                              "peralte": "", "luz_m": "2.0"}
    assert ventana_real["dialogos_de_error"] == []


def test_49_las_entradas_de_la_pestana_1_invalidan_el_informe(ventana_real):
    import gui.app as gapp
    for gesto, estado in ventana_real["invalidacion"].items():
        assert estado["corrio"], gesto
        assert estado["informe_es_None"], gesto
        assert estado["motivo"] == gapp.MOTIVO_ENTRADA_CAMBIADA, gesto


def test_45_la_pestana_4_lista_las_discrepancias_abiertas_y_las_corridas(ventana_real):
    from src import estado_del_expediente as estexp
    c = ventana_real["comparar"]
    for d in estexp.discrepancias_abiertas():
        assert d.id in c["discrepancias"]
    # Cuatro corridas de la misma obra antes de esta: la lista las ofrece,
    # la mas reciente primero, y la comparacion con la misma obra es igual.
    assert len(c["corridas"]) >= 1 and c["elegida"] == c["corridas"][0]
    assert c["boton_encendido"] and c["iguales"] is True
    assert c["tras_invalidar"] == {"corridas": [], "boton_encendido": False}
