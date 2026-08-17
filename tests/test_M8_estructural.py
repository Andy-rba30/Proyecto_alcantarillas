"""
tests/test_M8_estructural.py
=============================
Fase 8 (M8_estructural.py):

    seleccionar_clase_calibre()      CriterioPendienteError:
                                      'clases_producto_por_relleno' vacio.
    empuje_flotacion_kn_m()          U = gamma_agua * (pi/4) * D^2, siempre
                                      calculable (usa 'NF_profundidad_m',
                                      que SI tiene valor).
    peso_relleno_kn_m()              CriterioPendienteError:
                                      'peso_especifico_relleno_kn_m3' vacio;
                                      calculo directo con el criterio declarado.
    fs_flotacion()                   CriterioPendienteError: 'FS_flotacion' vacio.
    cama_apoyo_relleno_lateral()     tabla 8.1, [N] literal, sin vacio.
    verificacion_diferida_estructural()  tupla de avisos, nunca calcula.
"""

import math

import pytest

import criterios_adoptados as ca
from constantes_normativas import GAMMA_AGUA_KN_M3
from modelos import CamaApoyoRelleno, CriterioPendienteError, TipoMaterial
from modulos.M2_material import catalogo
from modulos.M8_estructural import (cama_apoyo_relleno_lateral,
                                    empuje_flotacion_kn_m, fs_flotacion,
                                    peso_relleno_kn_m,
                                    seleccionar_clase_calibre,
                                    verificacion_diferida_estructural)


@pytest.fixture
def concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


@pytest.fixture
def hdpe():
    return catalogo(TipoMaterial.HDPE)


# ===========================================================================
# Items 1-2 - Seleccion de clase/calibre
# ===========================================================================

def test_seleccionar_clase_calibre_lanza_pendiente(concreto):
    with pytest.raises(CriterioPendienteError) as excinfo:
        seleccionar_clase_calibre(material=concreto, altura_relleno=1.0)
    assert excinfo.value.clave == "clases_producto_por_relleno"


def test_clases_producto_por_relleno_esta_declarado_vacio():
    assert "clases_producto_por_relleno" in ca.criterios_sin_valor()


# ===========================================================================
# Item 3 - Piezas de V7
# ===========================================================================

def test_empuje_flotacion_es_siempre_calculable():
    """U no depende de ningun criterio pendiente: NF_profundidad_m ya vale 1.4."""
    U = empuje_flotacion_kn_m(D=0.90)
    assert U == pytest.approx(GAMMA_AGUA_KN_M3 * (math.pi / 4) * 0.90 ** 2)


def test_empuje_flotacion_crece_con_el_diametro():
    assert empuje_flotacion_kn_m(D=1.20) > empuje_flotacion_kn_m(D=0.90)


def test_peso_relleno_lanza_pendiente():
    with pytest.raises(CriterioPendienteError) as excinfo:
        peso_relleno_kn_m(D=0.90, altura_relleno=1.0)
    assert excinfo.value.clave == "peso_especifico_relleno_kn_m3"


def test_peso_relleno_calcula_con_el_criterio_declarado(monkeypatch):
    original = ca.CRITERIOS["peso_especifico_relleno_kn_m3"]
    monkeypatch.setitem(
        ca.CRITERIOS, "peso_especifico_relleno_kn_m3",
        original.__class__(**{**original.__dict__, "valor": 18.0}),
    )
    W = peso_relleno_kn_m(D=0.90, altura_relleno=1.05)
    assert W == pytest.approx(18.0 * 0.90 * 1.05)


def test_fs_flotacion_lanza_pendiente():
    with pytest.raises(CriterioPendienteError) as excinfo:
        fs_flotacion()
    assert excinfo.value.clave == "FS_flotacion"


def test_NF_profundidad_m_tiene_valor_declarado():
    """Es un dato de sitio [N], no un vacio: distinto de los otros dos de V7."""
    assert ca.valor("NF_profundidad_m") == pytest.approx(1.4)
    assert "NF_profundidad_m" not in ca.criterios_sin_valor()


# ===========================================================================
# Item 4 - Cama de apoyo y relleno lateral (tabla 8.1, [N])
# ===========================================================================

def test_cama_apoyo_relleno_lateral_concreto_reforzado(concreto):
    fila = cama_apoyo_relleno_lateral(concreto)
    assert isinstance(fila, CamaApoyoRelleno)
    assert "1/6" in fila.sujecion_relleno_lateral
    assert "506" in fila.numeral


def test_cama_apoyo_relleno_lateral_hdpe(hdpe):
    fila = cama_apoyo_relleno_lateral(hdpe)
    assert "arena" in fila.cama_apoyo.lower()
    assert "508" in fila.numeral


# ===========================================================================
# Item 5 - Diferido al expediente (nunca calcula)
# ===========================================================================

def test_verificacion_diferida_no_lanza_y_devuelve_los_tres_avisos():
    avisos = verificacion_diferida_estructural()
    assert len(avisos) == 3
    conceptos = " ".join(avisos).lower()
    for palabra in ("rigidez de anillo", "pandeo", "costura"):
        assert palabra in conceptos
