"""
tests/test_ML_licuefaccion.py
=============================
Fase 0-bis (VE-5, lote catlic): la licuefaccion como RESULTADO DECLARADO del
EMS, contrastado contra el caso patron `CP_ML_LICUEFACCION` (AASHTO LRFD
10.5.4.2, pag. impresa 10-34; E.050 38.3, pag. 51). El resto de la Fase 0-bis
--la corrida, la puerta del dato y la clase de sitio-- esta en
tests/test_ve5_catlic.py.
"""

import pytest

from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src.constantes_normativas import PROF_NF_LICUEFACCION_SI
from src.modelos import (DatoFaltanteError, DatoInvalidoError,
                         EstadoDeVerificacion)
from src.modulos import ML_licuefaccion as ML
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.fixtures.casos_patron import CP_ML_LICUEFACCION as CP

FECHA = "2026-11-20"
TRAZ = "prueba: lectura ficticia de S_D1 del caso patron"
EMS = {"resultado": "no_licua", "Mw": CP["Mw_adoptada_prueba"],
       "periodo_retorno_anios": CP["Tr_adoptado"],
       "documento": "EMS de PRUEBA", "fecha": FECHA, "metodo": "PRUEBA"}


@pytest.fixture
def con_zona():
    def declarar(z):
        ds.establecer_dato_dinamico("zona_sismica_aashto", z, TRAZ, FECHA,
                                    origen="prueba")
    try:
        yield declarar
    finally:
        ds.quitar_dato_dinamico("zona_sismica_aashto")


def test_el_limite_del_nf_es_el_de_la_cuenta_a_mano():
    assert PROF_NF_LICUEFACCION_SI == pytest.approx(
        CP["pies"] * CP["m_por_pie"], rel=REL_TRANSPORTE)
    assert PROF_NF_LICUEFACCION_SI == pytest.approx(CP["NF_limite_m"],
                                                    rel=REL_TRANSPORTE)


@pytest.mark.parametrize("zona,NF,exigida,con_aviso", CP["disparador"])
def test_el_disparador_de_10_5_4_2(con_zona, zona, NF, exigida, con_aviso):
    con_zona(zona)
    if exigida:
        with pytest.raises(DatoFaltanteError) as exc:
            ML.evaluar_licuefaccion(id_punto="P", NF_profundidad_m=NF,
                                    declarada=None)
        assert exc.value.campo == ML.CLAVE_LICUEFACCION_EMS
        return
    v = ML.evaluar_licuefaccion(id_punto="P", NF_profundidad_m=NF,
                                declarada=None)
    assert v.estado is EstadoDeVerificacion.NO_APLICA
    assert bool(v.avisos) is con_aviso


def test_el_tr_adoptado_es_el_del_caso():
    assert ca.valor(ML.CRITERIO_TR) == CP["Tr_adoptado"]


@pytest.mark.parametrize("campo,valor", [
    ("periodo_retorno_anios", CP["Tr_corto"]),
    ("Mw", CP["Mw_menor"]),
])
def test_el_resultado_del_ems_por_debajo_de_lo_adoptado(campo, valor):
    ca.establecer_valor_dinamico(ML.CRITERIO_MW, CP["Mw_adoptada_prueba"])
    try:
        declarada = ML.validar_licuefaccion_declarada(dict(EMS, **{campo: valor}))
        with pytest.raises(DatoInvalidoError) as exc:
            ML.evaluar_licuefaccion(id_punto="P", NF_profundidad_m=1.4,
                                    declarada=declarada)
        assert exc.value.campo.endswith(campo)
        v = ML.evaluar_licuefaccion(
            id_punto="P", NF_profundidad_m=1.4,
            declarada=ML.validar_licuefaccion_declarada(EMS))
        assert v.estado is EstadoDeVerificacion.CUMPLE
    finally:
        ca.quitar_valor_dinamico(ML.CRITERIO_MW)
