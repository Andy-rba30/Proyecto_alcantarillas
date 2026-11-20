"""
tests/test_ve5_catlic.py
========================
VE-5, lote «catlic»: catalogo, Fase 10 y licuefaccion.

  * T4-06 (v8 Sec. 3.1): la rama de selva alta del catalogo del TMC, con el
    caracter de RECOMENDACION de su cita (Manual 4.1.1.3.7 a), PDF 82).
"""

import pytest

from src import datos_sitio as ds
from src.constantes_normativas import DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO
from src.modelos import NIVEL_PERFIL, TipoMaterial
from src.modulos import M2_material as M2
from src.normativa import registro as _registro
from src.normativa.esquema import Caracter, Verbo
from tests.apoyo.aproximacion import REL_TRANSPORTE

FECHA = "2026-11-20"
TRAZ_SELVA = ("prueba: corredor ficticio en selva alta, cauces con las cuatro "
              "caracteristicas del num. 4.1.1.3.7 a)")


@pytest.fixture
def selva_alta():
    ds.establecer_dato_dinamico("region_natural", ds.REGION_SELVA_ALTA,
                                TRAZ_SELVA, FECHA, origen="prueba")
    try:
        yield
    finally:
        ds.quitar_dato_dinamico("region_natural")


# ===========================================================================
# T4-06 - la rama de selva alta
# ===========================================================================

def test_t406_la_obra_del_repositorio_es_de_costa_y_la_rama_no_actua():
    assert ds.dato("region_natural").valor == ds.REGION_COSTA
    assert ds.dato("region_natural").nivel == NIVEL_PERFIL
    assert M2.piso_de_selva_alta(TipoMaterial.TMC) is None
    assert M2.siguiente_diametro(TipoMaterial.TMC) == pytest.approx(
        M2._progresion()["inicio"], rel=REL_TRANSPORTE)
    assert M2.catalogo(TipoMaterial.TMC).pasos == ()


def test_t406_la_rama_mira_la_region_siempre_que_el_material_es_tmc():
    ds.reiniciar_usos()
    M2.siguiente_diametro(TipoMaterial.TMC)
    assert "region_natural" in ds.datos_usados()
    ds.reiniciar_usos()
    M2.siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO)
    M2.siguiente_diametro(TipoMaterial.HDPE)
    assert "region_natural" not in ds.datos_usados()


def test_t406_en_selva_alta_el_tmc_arranca_en_el_primer_escalon_de_48_in(selva_alta):
    piso = M2.piso_de_selva_alta(TipoMaterial.TMC)
    assert piso == pytest.approx(DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO,
                                 rel=REL_TRANSPORTE)
    primero = M2.siguiente_diametro(TipoMaterial.TMC)
    # 0.90 + 0.15 k: 1.20 queda por debajo de 48 in (1.2192 m); el primero
    # que no baja es 1.35 m (designado de AASHTO M 36).
    assert primero == pytest.approx(1.35, rel=REL_TRANSPORTE)
    assert primero >= piso
    # El concreto y el HDPE no reciben piso: la recomendacion es solo TMC.
    assert M2.siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO) == \
        pytest.approx(M2._progresion()["inicio"], rel=REL_TRANSPORTE)
    assert M2.piso_de_selva_alta(TipoMaterial.HDPE) is None


def test_t406_la_memoria_dice_recomienda_y_no_obliga(selva_alta):
    pasos = M2.catalogo(TipoMaterial.TMC).pasos
    assert len(pasos) == 1
    p = pasos[0]
    assert p.fundamento_id == M2.FUNDAMENTO_SELVA_ALTA
    assert M2.CITA_SELVA_ALTA in p.citas_textuales
    reg = _registro.construir()
    assert reg.fundamento(M2.FUNDAMENTO_SELVA_ALTA).verbo is Verbo.RECOMIENDA
    assert reg.cita(M2.CITA_SELVA_ALTA).caracter is Caracter.RECOMENDACION
    assert "RECOMIENDA" in p.nota_del_proyecto
    assert p.resultado.valor == pytest.approx(1.35, rel=REL_TRANSPORTE)


def test_t406_la_region_es_un_conjunto_cerrado():
    with pytest.raises(ValueError):
        ds.verificar_declaracion_de_sitio("region_natural", "selva", TRAZ_SELVA)
