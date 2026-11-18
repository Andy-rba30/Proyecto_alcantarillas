"""
VE-3.15 · Las decisiones 9 a 14 del dueño sobre el cabezal (2026-11-18).

Fija los VALORES DE ARCHIVO que el dueño eligió, con las condiciones de la
verificación independiente (`proceso/planes_mejora/ve3_estado/
verificaciones_del_dueno/cabezal_decisiones_9_14.md`), y la guardia de la
decisión 12: la reducción de k_h por desplazamiento (muro que CEDE) no se
puede declarar con el armado del muro que NO cede.
"""
from __future__ import annotations

import pytest

from src import criterios_adoptados as ca
from src.modelos import DatoInvalidoError
from src.modulos import M9_cabezal as M9


def _archivo(clave):
    return ca.criterio(clave).valor


def test_9_el_talon_se_arma_con_el_metodo_exacto():
    assert _archivo("momento_talon_cabezal") == M9.TALON_EXACTO


def test_10_la_pantalla_con_la_cuna_sobre_su_cara():
    assert _archivo("carga_pantalla_cabezal") == "cuna_sobre_la_pantalla"


def test_11_los_factores_de_la_tabla_de_muros():
    assert _archivo("fila_phi_estabilidad_cabezal") == M9.FILA_PHI_MUROS
    just = ca.criterio("fila_phi_estabilidad_cabezal").justificacion
    # La cita mal leída (barreras de sonido) no vuelve; la tensión con el
    # artículo de muros del Manual de Puentes y la salvedad de C11.5.7 sí.
    assert "2.11.8.5" not in just
    assert "2.8.1.1.12.6" in just
    assert "C11.5.7" in just


def test_12_un_solo_regimen_y_no_cede_de_archivo():
    assert _archivo("factor_muro_eleccion") == "sin_reduccion"
    assert _archivo("regimen_resistencia_elementos_cabezal") == "no_cedente_k0"
    assert _archivo("regimen_cabezal") == "cedente"


def test_12_la_reduccion_de_kh_exige_declarar_que_el_armado_cede():
    ca.establecer_valor_dinamico("factor_muro_eleccion",
                                 "reduccion_por_desplazamiento")
    try:
        with pytest.raises(DatoInvalidoError) as exc:
            M9.factor_muro()
        assert exc.value.campo == "factor_muro_eleccion"
        assert "regimen_resistencia_elementos_cabezal" in str(exc.value)
        ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                     "cedente")
        assert M9.factor_muro() == pytest.approx(0.5)
    finally:
        ca.quitar_valor_dinamico("factor_muro_eleccion")
        ca.quitar_valor_dinamico("regimen_resistencia_elementos_cabezal")


def test_13_la_distribucion_estatica_queda_para_el_muro_que_cede():
    # El archivo sigue con el muro que no cede: la fraccion fija; la
    # distribucion estatica se declara junto con la reduccion (y la
    # justificacion lo dice).
    assert _archivo("distribucion_incremento_sismico") == "fraccion_de_h"
    just = ca.criterio("distribucion_incremento_sismico").justificacion
    assert "decision 13 del dueño" in just


def test_14_margen_cero_bajo_la_hoya_sin_proteger():
    margen = _archivo("margen_zapata_bajo_socavacion_m")
    assert isinstance(margen, float) and not margen > 0 and not margen < 0
    just = ca.criterio("margen_zapata_bajo_socavacion_m").justificacion
    assert "HEC14.5.1.3#CABEZAL" in just
    assert "hoya protegida" in just
