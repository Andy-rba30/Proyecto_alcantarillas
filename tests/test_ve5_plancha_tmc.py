"""
tests/test_ve5_plancha_tmc.py
=============================
VE-5 (lote m8), item 23 del censo (ficha T5-03): la plancha del TMC que la
Fase 8 elige VUELVE A LA GEOMETRIA. Hasta VE-5 la Fase 8 subia de plancha
--desde el mayor de la adoptada y del minimo de la Tabla 507-01 del
EG-2013-- y la envolvente de 7.A y V7 seguia armada con la adoptada: el
punto solo lo avisaba («Declare la plancha requerida...»). Desde VE-5:

  * el `Material` lleva su plancha (`plancha_tmc`) y su espesor de pared por
    diametro con ella (`M2.material_con_plancha_tmc`);
  * la Fase 8 parte de la plancha del material (`M8.verificar_tmc`);
  * MD, cuando un escalon de TMC cumple la Fase 5 con una plancha mas gruesa
    que la del material, lo VUELVE A VERIFICAR con esa plancha
    (`M8.plancha_requerida_tmc`), y el punto se adopta con ella; el escalon
    siguiente parte otra vez de la adoptada.

El caso: el TMC de 1.20 m, cuyo minimo de la Tabla 507-01 (2.50 mm) obliga a
la plancha de 2.77 mm sobre la adoptada de 2.01 (0.76 mm de clave).
"""

import pytest

from src import constantes_normativas as CN
from src.modelos import (DatoInvalidoError, SeccionCircular, TipoMaterial,
                         Verificacion)
from src.modulos import M5_verificaciones as M5
from src.modulos import M8_estructural as M8
from src.modulos import MD
from src.modulos.M2_material import (catalogo, espesor_pared,
                                     material_con_plancha_tmc,
                                     plancha_del_material)
from tests.fixtures.casos_patron import CP_FASE_8_ESTRUCTURAL as CP

REL = 1e-9
# Los datos del bucle que el doble de la Fase 5 no mira: un conducto de 20 m
# con descarga libre.
L_PRUEBA = 20.0
TW_PRUEBA = 0.0
# El caudal del escalon de 0.90 m que no pide otra plancha: desde VE-5 (m45)
# MD descarta antes de la Fase 5 un conducto que no transporta Q en flujo libre
# (Sec. 4.1), y con el Q de A-01 (1.167 m3/s, S = 0.006) el TMC de 0.90 m ya no
# llega a la Fase 8. Con este Q lo transporta y el escalon se juzga por su
# plancha, que es lo que el test mide.
Q_ESCALON_090 = 0.30
ADOPTADA = "68x13/2.01"
REQUERIDA = "68x13/2.77"


@pytest.fixture
def a01():
    return CP["punto_A01"]()


@pytest.fixture
def tmc():
    return catalogo(TipoMaterial.TMC)


def test_el_material_lleva_su_plancha_y_su_espesor(tmc):
    assert plancha_del_material(tmc) == ADOPTADA
    otro = material_con_plancha_tmc(tmc, REQUERIDA)
    assert plancha_del_material(otro) == REQUERIDA
    delta = (CN.TMC_PLANCHA_CORRUGADA[REQUERIDA]["espesor_m"]
             - CN.TMC_PLANCHA_CORRUGADA[ADOPTADA]["espesor_m"])
    for D in (0.90, 1.20, 1.50):
        assert espesor_pared(otro, D) == pytest.approx(
            espesor_pared(tmc, D) + delta, rel=REL)
    # El catalogo no se toco.
    assert plancha_del_material(catalogo(TipoMaterial.TMC)) == ADOPTADA


@pytest.mark.parametrize("clave", ("75x25/2.77", "no_es_plancha"))
def test_la_plancha_no_cambia_de_corrugacion_ni_se_inventa(tmc, clave):
    with pytest.raises(DatoInvalidoError):
        material_con_plancha_tmc(tmc, clave)


def test_solo_el_tmc_lleva_plancha():
    with pytest.raises(DatoInvalidoError):
        material_con_plancha_tmc(catalogo(TipoMaterial.HDPE), REQUERIDA)


def test_la_fase_8_parte_de_la_plancha_del_material(a01, tmc):
    D = 1.20
    sec = SeccionCircular(D)
    r = M8.verificar_conducto(
        punto=a01, material=tmc, seccion=sec,
        altura_relleno=M5.altura_relleno_sobre_clave(punto=a01, material=tmc,
                                                     seccion=sec))
    assert r.seleccion == REQUERIDA
    assert any("Declare la plancha requerida" in a for a in r.avisos)
    assert M8.plancha_requerida_tmc(punto=a01, material=tmc,
                                    seccion=sec) == REQUERIDA
    otro = material_con_plancha_tmc(tmc, REQUERIDA)
    r2 = M8.verificar_conducto(
        punto=a01, material=otro, seccion=sec,
        altura_relleno=M5.altura_relleno_sobre_clave(punto=a01, material=otro,
                                                     seccion=sec))
    assert r2.seleccion == REQUERIDA
    assert not any("Declare la plancha requerida" in a for a in r2.avisos)
    assert M8.plancha_requerida_tmc(punto=a01, material=otro,
                                    seccion=sec) is None


def _verificador_desde(D_min):
    """Un doble de la Fase 5: incumple por debajo de D_min y, desde ahi,
    devuelve las verificaciones F8.* REALES del escalon (y nada mas)."""
    def verificar(*, punto, material, seccion, resultado):
        if seccion.altura < D_min - REL:
            return (Verificacion(cumple=False, numeral="doble", codigo="V3",
                                 valor_obtenido=1.0, valor_admisible=0.0,
                                 criterio_aplicado=""),)
        return M5.fase_8_estructural(punto=punto, material=material,
                                     seccion=seccion)
    return verificar


def test_md_vuelve_a_verificar_el_escalon_con_la_plancha_de_la_fase_8(a01, tmc):
    traza = []
    resultado, motivo = MD.disenar_material(
        a01, tmc, Q=a01.Q_m3s, S=a01.S_cauce, L=L_PRUEBA, TW=TW_PRUEBA,
        verificar=_verificador_desde(1.20), registrar=traza.append)
    assert resultado is not None, motivo
    assert resultado.seccion.altura == pytest.approx(1.20, rel=REL)
    assert plancha_del_material(resultado.material) == REQUERIDA
    delta = (CN.TMC_PLANCHA_CORRUGADA[REQUERIDA]["espesor_m"]
             - CN.TMC_PLANCHA_CORRUGADA[ADOPTADA]["espesor_m"])
    assert espesor_pared(resultado.material, 1.20) == pytest.approx(
        espesor_pared(tmc, 1.20) + delta, rel=REL)
    # La traza dice que el escalon se volvio a verificar, y con que plancha.
    de_1_20 = [p for p in traza
               if p.seccion.altura == pytest.approx(1.20, rel=REL)]
    assert len(de_1_20) == 2
    assert not de_1_20[0].aceptado and REQUERIDA in de_1_20[0].motivo
    assert de_1_20[1].aceptado


def test_un_escalon_que_no_pide_otra_plancha_no_se_repite(a01, tmc):
    """El TMC de 0.90 m: la Tabla 507-01 pide 2.00 mm y la adoptada (2.01)
    alcanza; se acepta a la primera, con la adoptada."""
    traza = []
    resultado, _ = MD.disenar_material(
        a01, tmc, Q=Q_ESCALON_090, S=a01.S_cauce, L=L_PRUEBA, TW=TW_PRUEBA,
        verificar=_verificador_desde(0.90), registrar=traza.append)
    assert resultado is not None
    assert resultado.seccion.altura == pytest.approx(0.90, rel=REL)
    assert plancha_del_material(resultado.material) == ADOPTADA
    assert [p.aceptado for p in traza] == [True]
