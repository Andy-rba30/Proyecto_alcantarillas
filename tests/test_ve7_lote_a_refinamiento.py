"""
tests/test_ve7_lote_a_refinamiento.py
=====================================
VE-7, lote A (triaje VE-7 de Fable, 2026-11-20), A9 (ficha VE6-22): si con
la longitud entre cabezales V4 (o V1) dejaria de cumplirse
(`servicio._lo_que_no_se_cumpliria` no vacio), ademas del aviso hay un
`Bloqueo` de la Fase 9 a expediente con el remedio «declarar `longitud_m` =
L_cab»: el expediente no cierra.

El caso: A-01 con la cota del receptor (el de `test_ve6_refinamiento_
longitud.py`), con el refinamiento forzado bajo control de SALIDA y con
Delta = HW(L_cab) - HW(L) mayor que el margen de V4 del diseño, escrito a
mano desde la V4 de la Fase 5. A-01 tal cual no cambia: sin bloqueo.
"""

import pytest

import cli
from src import servicio
from src.modelos import ControlGobernante, TipoDeBloqueo
from src.modulos import M4_control as M4
from tests.test_ve6_refinamiento_longitud import (  # noqa: F401
    a01, csv_cota_tw)


def _corrida(csv):
    externos = cli.cargar_datos_externos(None, {"luz_m": 2.75})
    informe = cli.correr(csv, externos, alcance=cli.ALCANCE_PERFIL)
    punto = next(p for p in informe.puntos if p.punto.id == "A-01")
    servicio._fase_9(punto, externos)
    return punto, externos


def _del_refinamiento(punto):
    return [b for b in punto.bloqueos
            if b.etapa == servicio.ETAPA_REFINAMIENTO_LONGITUD]


def test_a01_no_cambia(a01):
    assert a01.refinamiento_longitud is not None
    assert not servicio._lo_que_no_se_cumpliria(a01,
                                                 a01.refinamiento_longitud)
    assert not _del_refinamiento(a01)


def test_bajo_salida_con_delta_mayor_que_el_margen_de_v4_no_cierra(
        csv_cota_tw, monkeypatch):
    punto, externos = _corrida(csv_cota_tw)
    v4 = next(v for v in punto.resultado.verificaciones if v.codigo == "V4")
    margen = v4.valor_admisible - v4.valor_obtenido
    assert margen > 0
    original = M4.refinar_con_longitud_entre_cabezales

    def bajo_salida_y_mas_alto(**kw):
        ref = original(**kw)
        return ref._replace(
            control_cabezales=ControlGobernante.SALIDA,
            HW_cabezales_m=ref.HW_diseno_m + margen + 0.05)

    monkeypatch.setattr(M4, "refinar_con_longitud_entre_cabezales",
                        bajo_salida_y_mas_alto)
    servicio._fase_9_refinamiento(punto, externos)
    bloqueos = _del_refinamiento(punto)
    assert len(bloqueos) == 1
    b = bloqueos[0]
    L_cab = punto.cabezal.longitud_entre_cabezales
    assert b.fase == servicio.FASE_CABEZAL
    assert b.tipo is TipoDeBloqueo.DATO_FALTANTE
    assert b.campo == "longitud_m"
    assert "V4 NO se cumpliria" in b.mensaje
    assert f"declarar `longitud_m` = {L_cab:.3f} m" in b.mensaje
    assert not b.diferido_por_alcance
    # y el aviso sigue
    assert any("V4 NO se cumpliria" in a for a in punto.cabezal.avisos)


# ===========================================================================
# A10 (VE5GUI-46) -- la D de la losa de entrega de M9 con los decimales del
# rotulo de la seccion (`modelos.cifras_de_dimension`), no tres fijos
# ===========================================================================

def test_A10_la_d_de_m9_lleva_los_decimales_del_rotulo(a01):
    from src.modelos import CIFRAS_MAGNITUD, cifras_de_dimension
    pasos = [p for p in a01.cabezal.pasos if p.codigo.startswith("9.0.4")]
    assert pasos
    for p in pasos:
        D = next(m for m in p.sustitucion if m.simbolo == "D")
        assert D.cifras == cifras_de_dimension(D.valor)
    # el diametro de A-01 se rotula con dos decimales: antes eran tres
    assert cifras_de_dimension(D.valor) != CIFRAS_MAGNITUD
    assert cifras_de_dimension(1.0668) == 4
