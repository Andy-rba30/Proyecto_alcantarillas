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

from src import constantes_normativas as cn
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


def test_12_un_solo_regimen_de_kh_y_el_armado_en_reposo_de_archivo():
    """La estabilidad externa sigue con el activo (mecanismo del muro que
    cede); lo que se unifica es k_h: sin reduccion y armado en reposo."""
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
        assert M9.factor_muro() is cn.REDUCCION_KH_POR_DESPLAZAMIENTO
    finally:
        ca.quitar_valor_dinamico("factor_muro_eleccion")
        ca.quitar_valor_dinamico("regimen_resistencia_elementos_cabezal")


def test_13_el_brazo_del_incremento_se_deriva_del_regimen():
    assert _archivo("distribucion_incremento_sismico") == \
        M9.INCREMENTO_SEGUN_REGIMEN
    just = ca.criterio("distribucion_incremento_sismico").justificacion
    assert "decision 13 del dueño" in just
    assert "AASHTO_LRFD_9.C11.6.5.4#H_MEDIOS" in just


def test_14_margen_cero_bajo_la_hoya_sin_proteger():
    margen = _archivo("margen_zapata_bajo_socavacion_m")
    assert isinstance(margen, float) and not margen > 0 and not margen < 0
    just = ca.criterio("margen_zapata_bajo_socavacion_m").justificacion
    assert "HEC14.5.1.3#CABEZAL" in just
    assert "hoya protegida" in just


# ---------------------------------------------------------------------------
# De punta a punta con el juego de la validacion integral (correcciones de la
# revision de VE-3.15: H2, H3, H5)
# ---------------------------------------------------------------------------
from tests.apoyo import validacion_integral as V  # noqa: E402
from src.modelos import CondicionAnalisis  # noqa: E402
from tests.apoyo.aproximacion import REL_TRANSPORTE  # noqa: E402


@pytest.fixture(scope="module")
def no_cede():
    """El juego titular: valores de archivo, muro que NO cede."""
    return V.correr_juego(V.juego_titular())


@pytest.fixture(scope="module")
def cede():
    """El juego tal cual: reduccion de k_h con el armado «cedente»."""
    return V.correr_juego(V.juego_completo())


def _a01(informe):
    return next(p for p in informe.puntos if p.punto.id == "A-01")


def _sismica(informe, extremo):
    return next(e for e in _a01(informe).cabezal.estabilidad
                if e.extremo == extremo
                and e.condicion is CondicionAnalisis.SISMICO)


def test_h2_con_margen_cero_el_desplante_cita_la_regla_sin_margen(no_cede):
    cab = _a01(no_cede).cabezal
    cb5 = next(v for v in cab.verificaciones if v.codigo == "CB5.s")
    assert cb5.paso.umbral.cita_id == "AASHTO_LRFD_9.10.6.1.2#DESPLANTE"
    assert "2.0 ft" not in cb5.paso.umbral.descripcion
    assert "decision 14" in cb5.paso.umbral.aplicacion


def _resultante_relativa(sis):
    eh = next(c for c in sis.cargas if c.codigo == "EH.h")
    dP = next(c for c in sis.cargas if c.codigo == "EQ.dPAE.h")
    return (eh.H * eh.z + dP.H * dP.z) / ((eh.H + dP.H) * sis.altura_empuje)


@pytest.mark.parametrize("extremo", ["entrada", "salida"])
def test_h3_con_el_muro_que_no_cede_la_resultante_no_queda_bajo_h_medios(
        no_cede, extremo):
    sis = _sismica(no_cede, extremo)
    assert _resultante_relativa(sis) >= 0.5 - 1e-9


@pytest.mark.parametrize("extremo", ["entrada", "salida"])
def test_h3_con_el_muro_que_cede_el_incremento_va_al_centroide_o_h_tercios(
        cede, extremo):
    sis = _sismica(cede, extremo)
    dP = next(c for c in sis.cargas if c.codigo == "EQ.dPAE.h")
    eh = next(c for c in sis.cargas if c.codigo == "EH.h")
    ls = next(c for c in sis.cargas if c.codigo == "LS.h")
    z_estatico = (eh.H * eh.z + ls.H * ls.z) / (eh.H + ls.H)
    h = sis.altura_empuje
    assert dP.z == pytest.approx(max(z_estatico, h / 3), rel=REL_TRANSPORTE)
    assert dP.z < 0.6 * h
