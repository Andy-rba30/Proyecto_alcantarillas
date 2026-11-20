"""
tests/test_ve5_m45_rugosidad_v2b.py
===================================
VE-5, lote m45, item 19 (fichas T2-06 y C10-02): el SEGUNDO indicador de
sedimentacion del HDS-5 num. 5.3.3 (pag. impresa 5.11, cita
HDS5_3ED.5.3.3#INDICADORES): «roughness greater than the channel». Decision
adoptada en el censo: INDICADOR, no veredicto. El n del cauce natural entra
con la seccion del cauce de aproximacion del punto
(`seccion_cauce_aproximacion`, su campo `n`); sin ella no se evalua y el n
del cauce no se supone.

SE ESCRIBIO EN ROJO PRIMERO: V2b no recibia material ni expediente.
"""

from __future__ import annotations

import pytest

from src import criterios_adoptados as ca
from src.modelos import (DatosDeExpediente, DerechoDeViaDelPunto,
                         SeccionReceptor, TipoDeVeredicto)
from src.modulos.M5_verificaciones import v2b_sedimentacion
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.test_ve3_11_ensayos_conducto import _concreto
from tests.test_M5_verificaciones import _punto, _resultado

ORIGEN_DE_PRUEBA = "dato de prueba"


def _expediente(n_cauce):
    cauce = SeccionReceptor(b_m=2.0, z_HV=1.5, S=0.006, n=n_cauce,
                            altura_total_m=1.5)
    return DatosDeExpediente(derecho_de_via=DerechoDeViaDelPunto(
        ancho_m=None, origen_ancho="", semilongitud_entrada_m=7.0,
        origen_semilongitud=ORIGEN_DE_PRUEBA, seccion_cauce=cauce,
        origen_seccion_cauce=ORIGEN_DE_PRUEBA))


def _v2b(n_cauce, S=None, regimen=None):
    punto = _punto()
    if regimen is not None:
        ca.establecer_valor_dinamico("regimen_v2b", regimen)
    try:
        return v2b_sedimentacion(
            punto=punto, resultado=_resultado(S=S or punto.S_cauce),
            material=_concreto(),
            expediente=None if n_cauce is None else _expediente(n_cauce))
    finally:
        if regimen is not None:
            ca.quitar_valor_dinamico("regimen_v2b")


def test_conducto_mas_rugoso_que_el_cauce_dispara_el_aviso_sin_cambiar_el_veredicto():
    n_conducto = _concreto().n_para_capacidad
    v = _v2b(n_conducto / 2)
    assert v.cumple
    assert v.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE   # el de la pendiente
    assert len(v.avisos) == 1 and "MAS RUGOSO" in v.avisos[0]
    sustitucion = {m.simbolo: m.valor for m in v.paso.sustitucion}
    assert sustitucion["n_conducto"] == pytest.approx(n_conducto,
                                                    rel=REL_TRANSPORTE)
    assert sustitucion["n_cauce"] == pytest.approx(n_conducto / 2,
                                                 rel=REL_TRANSPORTE)
    assert "SE DISPARA" in v.paso.nota_del_proyecto


def test_ni_bajo_umbral_duro_la_rugosidad_descarta_el_diametro():
    v = _v2b(_concreto().n_para_capacidad / 2, regimen="umbral_duro")
    assert v.cumple and v.avisos


def test_conducto_menos_rugoso_que_el_cauce_no_dispara():
    v = _v2b(0.035)
    assert v.cumple and not v.avisos
    assert "no se dispara" in v.paso.nota_del_proyecto


def test_sin_la_seccion_del_cauce_no_se_evalua_ni_se_supone():
    v = _v2b(None)
    assert v.cumple and not v.avisos
    sustitucion = {m.simbolo: m.valor for m in v.paso.sustitucion}
    assert sustitucion["n_cauce"] == "no declarado"
    assert "n_conducto" not in sustitucion
    assert "no se evalua" in v.paso.nota_del_proyecto


def test_el_primer_indicador_sigue_decidiendo_bajo_umbral_duro():
    punto = _punto()
    v = _v2b(0.035, S=punto.S_cauce / 2, regimen="umbral_duro")
    assert not v.cumple
