"""
tests/test_ve6_m9_sobrecarga_por_punto.py
=========================================
Lote M9 del censo, item 28 (ficha T7B-11), VE-6: la orientacion del muro
frente al trafico y la distancia del borde de calzada al trasdos, POR PUNTO.

Hasta VE-6 las dos eran solo [S] de corredor (`datos_sitio`): un cruce con
esviaje distinto del resto, o con su cabezal a otra distancia de la calzada,
no se podia declarar. Desde VE-6 entran por `--datos-externos` con dos
claves, por punto o en `globales`, y valen para los dos cabezales o por
extremo ({"entrada": ..., "salida": ...}); el dato del punto GANA sobre el
de corredor, y sin el rige el de corredor. Ninguna regla deduce la
orientacion del esviaje: AASHTO 3.11.6.4 no da tabla para el muro oblicuo
(ficha T7B-11), y una deduccion seria un umbral inventado.

Escrito ANTES del codigo. Dorados a mano con las Tablas 3.11.6.4-1 y -2.
"""

from dataclasses import replace

import pytest

from src import datos_sitio as ds
from src import servicio
from src.modelos import CondicionAnalisis, DatoInvalidoError
from src.modulos import M9_cabezal as M9
from tests.apoyo.aproximacion import ABS_CERO
from tests.fixtures.casos_patron import CP_T7B_ESTABILIDAD as CPB
from tests.test_t7c_cabezal_armado import _geometria, tanteo  # noqa: F401

EST = CondicionAnalisis.ESTATICO
PIE = 0.3048
TOL = 1e-9
# Los dorados a mano de abajo llevan seis cifras decimales.
TOL_DORADO = 1e-6
ORI = M9.CAMPO_ORIENTACION_DEL_PUNTO
DIS = M9.CAMPO_DISTANCIA_BORDE_DEL_PUNTO

# --- los dorados, a mano --------------------------------------------------
# h = 2.40 m = 7.874016 ft.
# Tabla 3.11.6.4-1 (estribo perpendicular): 5 ft -> 4.0 ft, 10 ft -> 3.0 ft
#   h_eq = 4.0 - (7.874016 - 5)/5 = 3.425197 ft = 1.044000 m
# Tabla 3.11.6.4-2 (muro paralelo), columna «0.0 ft»: 5 -> 5.0, 10 -> 3.5
#   h_eq = 5.0 - 1.5·(2.874016/5) = 4.137795 ft = 1.261200 m
# y la columna «1.0 ft or Further»: 2.0 ft = 0.6096 m (el de CPB).
ALTURA_FT = 2.40 / PIE
H_EQ_PERPENDICULAR = (4.0 - (ALTURA_FT - 5) / 5) * PIE
H_EQ_PARALELO_PEGADO = (5.0 - 1.5 * (ALTURA_FT - 5) / 5) * PIE


def test_los_dorados_son_los_de_la_tabla():
    assert H_EQ_PERPENDICULAR == pytest.approx(1.044000, abs=TOL_DORADO)
    assert H_EQ_PARALELO_PEGADO == pytest.approx(1.261200, abs=TOL_DORADO)


@pytest.mark.parametrize("bruto, esperado", [
    ("paralelo_al_trafico", {"entrada": "paralelo_al_trafico",
                             "salida": "paralelo_al_trafico"}),
    ({"salida": "perpendicular_al_trafico"},
     {"entrada": None, "salida": "perpendicular_al_trafico"}),
])
def test_la_orientacion_del_punto_se_valida_y_se_normaliza(bruto, esperado):
    assert M9.validar_sobrecarga_del_punto(ORI, bruto) == esperado


@pytest.mark.parametrize("bruto, esperado", [
    (1.6, {"entrada": 1.6, "salida": 1.6}),
    (0, {"entrada": 0.0, "salida": 0.0}),
    ({"entrada": 0.2, "salida": 2.5}, {"entrada": 0.2, "salida": 2.5}),
])
def test_la_distancia_del_punto_se_valida_y_se_normaliza(bruto, esperado):
    assert M9.validar_sobrecarga_del_punto(DIS, bruto) == esperado


@pytest.mark.parametrize("clave, bruto", [
    (ORI, "oblicuo"), (ORI, 30.0), (ORI, {"centro": "paralelo_al_trafico"}),
    (ORI, {}), (DIS, -0.1), (DIS, True), (DIS, "1.6"), (DIS, float("nan")),
    (DIS, {"entrada": -1.0}), ("otra_clave", 1.0),
])
def test_lo_que_no_es_dato_se_rechaza_en_la_puerta(clave, bruto):
    with pytest.raises(DatoInvalidoError):
        M9.validar_sobrecarga_del_punto(clave, bruto)


def test_h_eq_con_la_orientacion_y_la_distancia_del_punto(tanteo):
    """
    El corredor del fixture dice «paralelo, borde a 1.60 m» (h_eq = 0.6096);
    lo que el punto declara gana, y sin declarar rige el corredor.
    """
    assert M9.h_eq_sobrecarga_trasdos(altura_muro_total=2.40) == \
        pytest.approx(CPB["h_eq"], abs=TOL)
    assert M9.h_eq_sobrecarga_trasdos(
        altura_muro_total=2.40, orientacion="perpendicular_al_trafico") == \
        pytest.approx(H_EQ_PERPENDICULAR, abs=TOL)
    assert M9.h_eq_sobrecarga_trasdos(
        altura_muro_total=2.40, orientacion="paralelo_al_trafico",
        borde_m=0.0) == pytest.approx(H_EQ_PARALELO_PEGADO, abs=TOL)
    # sin orientacion del punto, la distancia del punto gana igual
    assert M9.h_eq_sobrecarga_trasdos(altura_muro_total=2.40, borde_m=0.0) \
        == pytest.approx(H_EQ_PARALELO_PEGADO, abs=TOL)


def test_sin_corredor_el_dato_del_punto_basta(tanteo):
    """El [S] de corredor sin valor no detiene si el punto lo declara."""
    ds.quitar_dato_dinamico("orientacion_muro_respecto_al_trafico")
    ds.quitar_dato_dinamico("distancia_borde_calzada_al_trasdos_m")
    assert M9.h_eq_sobrecarga_trasdos(
        altura_muro_total=2.40, orientacion="perpendicular_al_trafico") == \
        pytest.approx(H_EQ_PERPENDICULAR, abs=TOL)


def test_el_ensamble_lee_el_dato_de_la_geometria_del_cabezal(tanteo):
    """
    La geometria del cabezal lleva lo que el punto declara para SU extremo
    (`GeometriaCabezal.orientacion_trafico` y `.distancia_borde_calzada_m`),
    y el ensamble lo usa y lo dice en el paso de la sobrecarga.
    """
    g = replace(tanteo.geometria, orientacion_trafico="perpendicular_al_trafico")
    e = M9.ensamble_estabilidad(replace(tanteo, geometria=g), EST)
    _, d = M9.cargas_del_cabezal(replace(tanteo, geometria=g), EST)
    assert d["h_eq"] == pytest.approx(H_EQ_PERPENDICULAR, abs=TOL)
    paso = next(p for p in e.pasos if p.codigo.startswith("9.2.2"))
    texto = " ".join(m.procedencia for m in paso.sustitucion)
    assert "declarada por punto" in texto


def test_el_alero_hereda_el_dato_de_su_cabezal(tanteo):
    from src.modelos import Aleros
    aleros = Aleros(angulo_grados=45.0, angulo_largo_grados=45.0,
                    esviaje_grados=0.0, longitud_corto=2.5, longitud_largo=2.5,
                    altura_inicial=1.75, altura_final=0.40, espesor=0.30,
                    ancho_zapata=2.0, espesor_zapata=0.40)
    g = _geometria(aleros=aleros, distancia_borde_calzada_m=0.0)
    x = M9.entorno_de_la_seccion_del_alero(replace(tanteo, geometria=g), 0.5)
    assert x.geometria.distancia_borde_calzada_m == pytest.approx(0.0,
                                                                 abs=ABS_CERO)


def test_predimensionar_lleva_el_dato_del_punto_a_la_geometria():
    """
    `predimensionar_cabezal` toma los dos campos de `declaradas` (el
    servicio los pone ahi desde las dos claves) y no los cuenta como
    dimensiones.
    """
    from tests.test_t7a_cabezal_geometria import _extremo, _embocadura
    g = M9.predimensionar_cabezal(
        extremo=_extremo(), embocadura=_embocadura(), talud=1.5,
        declaradas={ORI: "perpendicular_al_trafico", DIS: 0.5})
    assert g.orientacion_trafico == "perpendicular_al_trafico"
    assert g.distancia_borde_calzada_m == pytest.approx(0.5, abs=ABS_CERO)
    assert all(d.nombre != ORI for d in g.dimensiones)


def test_el_servicio_lleva_las_dos_claves_al_cabezal_declarado():
    """
    Las dos claves estan en `CLAVES_DE_CABEZAL` (opcionales: no detienen
    nada) y el servicio las funde, por extremo, en lo que pasa a M9 como
    `declarados`.
    """
    assert {ORI, DIS} <= set(servicio.CLAVES_DE_CABEZAL)
    assert ORI not in servicio.CLAVES_EXTERNAS
    dato = servicio._dato_externo(ORI, {"entrada": "paralelo_al_trafico"},
                                  "puntos")
    assert dato.valor == {"entrada": "paralelo_al_trafico", "salida": None}
    fundido = servicio.fundir_sobrecarga_del_punto(
        {"entrada": {"altura_total_m": 2.4}, "salida": {}},
        orientacion={"entrada": "paralelo_al_trafico", "salida": None},
        distancia={"entrada": 0.0, "salida": 1.6})
    # el valor se TRANSPORTA (no se calcula): se compara con approx
    assert fundido["entrada"][ORI] == "paralelo_al_trafico"
    assert ORI not in fundido["salida"]
    assert fundido["entrada"]["altura_total_m"] == pytest.approx(
        2.4, abs=ABS_CERO)
    assert fundido["entrada"][DIS] == pytest.approx(0.0, abs=ABS_CERO)
    assert fundido["salida"][DIS] == pytest.approx(1.6, abs=ABS_CERO)
    assert set(fundido["salida"]) == {DIS}
    assert servicio.fundir_sobrecarga_del_punto(None, orientacion=None,
                                                distancia=None) is None
