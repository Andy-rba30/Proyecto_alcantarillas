"""
tests/test_ve7_lote_a_embocadura.py
===================================
VE-7, lote A (triaje VE-7 de Fable, 2026-11-20): la embocadura del marco.

A1 (VE6-T7A03 (4)) -- con el cabezal NORMAL sin aletas, el borde de la fila
de la Tabla A.1 empareja el ke de la C.2, como ya lo hacia la Carta 11. El
oraculo es el ROTULO literal de cada fila (`normativa/tablas.py::T_HDS5_A1`)
leido aqui: «chamfer» -> solo la escuadra (ke 0.5); «bevel» -> la de bordes
biselados (0.2) o la escuadra; la escala 2 de la Carta 8 («90° and 15°
wingwall flares», arista viva) -> la escuadra.
"""

import pytest

from src.constantes_normativas import CAJON_C2_SIN_ALETAS, KE_HDS5_C2
from src.modelos import DatoInvalidoError, Familia
from src.modulos import M9_cabezal as M9
from src.normativa import tablas
from tests.apoyo.criterios import declarados

ESCUADRA = "cajon_sin_aletas_escuadra_3"
BISELADA = "cajon_sin_aletas_redondeado_3"


def _rotulo_ta1(clave):
    tabla = tablas.TABLAS["HDS5_3ED.TA1"]
    fila = next(f for f in tabla.filas if f.id == f"HDS5_3ED.TA1#{clave}")
    return fila.etiqueta_literal.lower()


def _normal_sin_aletas(esviaje=0.0):
    with declarados({"embocadura_cabezal": M9.EMBOCADURA_CABEZAL_RECTO}):
        return M9.embocadura_del_punto(esviaje_grados=esviaje,
                                       familia=Familia.C, id_punto="P")


@pytest.mark.parametrize("fila", [
    "cajon_concreto_cabezal_90_chaflan",
    "cajon_concreto_cabezal_90_bisel_45",
    "cajon_concreto_cabezal_90_bisel_337",
])
def test_los_rotulos_de_la_carta_10_nombran_su_borde(fila):
    rotulo = _rotulo_ta1(fila)
    if "chaflan" in fila:
        assert "chamfer" in rotulo and "bevel" not in rotulo
    else:
        assert "bevel" in rotulo and "chamfer" not in rotulo


def _vale_por_rotulo(fila, ke):
    """El emparejamiento escrito aqui desde el rotulo, no desde la constante."""
    rotulo = _rotulo_ta1(fila)
    if ke == ESCUADRA:
        return True
    return "bevel" in rotulo


@pytest.mark.parametrize("fila", [
    "cajon_concreto_cabezal_90_chaflan",
    "cajon_concreto_cabezal_90_bisel_45",
    "cajon_concreto_cabezal_90_bisel_337",
    "cajon_concreto_aletas_90_15",
])
@pytest.mark.parametrize("ke", [ESCUADRA, BISELADA])
def test_el_borde_de_la_carta_10_empareja_el_ke(fila, ke):
    embocadura = _normal_sin_aletas()
    with declarados({"embocadura_cajon": fila, "ke_entrada_cajon": ke}):
        if _vale_por_rotulo(fila, ke):
            nota = M9.verificar_coherencia_embocadura_cajon(embocadura)
            assert fila in nota and ke in nota
        else:
            with pytest.raises(DatoInvalidoError) as exc:
                M9.verificar_coherencia_embocadura_cajon(embocadura)
            assert exc.value.campo == "ke_entrada_cajon"
            assert ESCUADRA in str(exc.value)


def test_chaflan_con_ke_02_se_detiene_y_bisel_con_ke_02_pasa():
    """El caso del dictamen, dicho con el ke de la tabla (0.2)."""
    assert KE_HDS5_C2[BISELADA]["ke"] == pytest.approx(0.2)
    embocadura = _normal_sin_aletas()
    with declarados({"embocadura_cajon": "cajon_concreto_cabezal_90_chaflan",
                     "ke_entrada_cajon": BISELADA}):
        with pytest.raises(DatoInvalidoError):
            M9.verificar_coherencia_embocadura_cajon(embocadura)
    with declarados({"embocadura_cajon": "cajon_concreto_cabezal_90_bisel_45",
                     "ke_entrada_cajon": BISELADA}):
        assert M9.verificar_coherencia_embocadura_cajon(embocadura)


def test_sin_carta_declarada_de_cabezal_normal_rigen_las_dos_filas():
    """Con una carta de aleros (la de archivo) y cabezal recto la coherencia
    se detiene en la carta, no en el ke: la banda del ke sigue entera."""
    _, c2 = M9.filas_hds5_del_cajon(_normal_sin_aletas())
    assert c2 == CAJON_C2_SIN_ALETAS
