"""
tests/test_ve3_vc3_bloquea.py
=============================
VE-3.10 (decision del dueño, 2026-11-17, ficha VE3-06): en un paso de canal
(Familia C) SIN el desnivel F que el perfil del canal provee en el cruce
(`desnivel_perfil_canal_m`, de --datos-externos), VC3 ya no queda como un
aviso de 7.B: el punto se DETIENE pidiendo el dato, `DatoFaltanteError` con
la clave como `campo` (CLAUDE.md, «Excepciones»: si el revisor tiene que
AÑADIR algo es Faltante). Va en la posicion de VC1 y es obligatoria tambien
a `--alcance perfil`, como VC1, y el pre-vuelo la anuncia como falta que
DETIENE con la etapa y el detalle del bloqueo.

SE ESCRIBIO EN ROJO PRIMERO, contra 6a87006.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

import cli
from src import anticipo as antc
from src import servicio
from src.modelos import (DatoFaltanteError, DatosDeExpediente, Familia,
                         TipoDeBloqueo)
from src.modulos import M5_verificaciones as M5
from src.modulos import M7_geometria as M7
from tests.apoyo import validacion_integral as V
from tests.test_t3_familia_c import _punto_c01

CLAVE = "desnivel_perfil_canal_m"


def _sin_desnivel(punto=None):
    return M5.vc3_rasante_canal(
        punto=punto or replace(_punto_c01(), cota_fondo_receptor=36.20),
        cota_entrada_msnm=36.30, HW=0.62, TW=0.41, desnivel_perfil_m=None)


def test_vc3_sin_el_desnivel_lanza_el_dato_que_falta_con_su_clave():
    with pytest.raises(DatoFaltanteError) as exc:
        _sin_desnivel()
    assert exc.value.campo == CLAVE
    assert exc.value.id_punto == "C-01"
    # El mensaje dice de donde sale el dato: el proyecto del canal.
    assert "ANA" in str(exc.value) and "proyecto del canal" in str(exc.value)
    assert M5.DETALLE_FALTA_DESNIVEL_CANAL in str(exc.value)


def test_pieza_vc3_sin_expediente_o_sin_desnivel_tambien_se_detiene():
    """La puerta de las dos tablas de la Fase 5 no devuelve None en un
    paso de canal: no traer `DatosDeExpediente` es no traer F."""
    c01 = _c01()
    rh, punto = c01.resultado.resultado_hidraulico, c01.punto_de_calculo
    for expediente in (None, DatosDeExpediente()):
        with pytest.raises(DatoFaltanteError) as exc:
            M5.pieza_vc3(punto=punto, resultado=rh, expediente=expediente)
        assert exc.value.campo == CLAVE
    # Fuera de la Familia C no hay fila, con o sin F.
    otro = replace(punto, familia=Familia.A)
    assert M5.pieza_vc3(punto=otro, resultado=rh, expediente=None) is None


def _c01(cambios=(), alcance=V.ALCANCE):
    informe = V.correr_juego(V.aplicar(V.juego_completo(), cambios),
                             alcance=alcance)
    return next(p for p in informe.puntos if p.punto.id == "C-01")


SIN_DESNIVEL = (("externo", "C-01", CLAVE, None),)


@pytest.mark.parametrize("alcance", [cli.ALCANCE_PERFIL, cli.ALCANCE_EXPEDIENTE])
def test_sin_el_desnivel_C01_se_detiene_en_los_dos_alcances(alcance):
    c01 = _c01(SIN_DESNIVEL, alcance=alcance)
    assert not c01.dimensionado
    b = next(b for b in c01.bloqueos if b.tipo is TipoDeBloqueo.DATO_FALTANTE)
    assert b.campo == CLAVE
    assert b.etapa == servicio.ETAPA_BUCLE_DE_MD
    assert not b.diferido_por_alcance
    assert TipoDeBloqueo.DISENO_NO_FACTIBLE not in {x.tipo for x in c01.bloqueos}


def test_con_el_desnivel_del_juego_C01_dimensiona_como_antes_y_VC3_cumple():
    c01 = _c01()
    assert c01.dimensionado
    assert c01.resultado.seccion.etiqueta() == "marco 1.20 × 0.90 m"
    vc3 = [v for v in c01.resultado.verificaciones if v.codigo == "VC3"]
    assert len(vc3) == 1 and vc3[0].cumple


def test_el_aviso_de_7B_se_retiro():
    """Un paso de canal sin F ya no llega a 7.B: el aviso no tiene caso."""
    assert not hasattr(M5, "AVISO_VC3_SIN_DESNIVEL")
    assert not hasattr(M7, "AVISO_VC3_SIN_DESNIVEL")


def test_A_y_B_no_ven_la_clave():
    informe = V.correr_juego(V.aplicar(V.juego_completo(), SIN_DESNIVEL))
    for p in informe.puntos:
        if p.punto.familia is not Familia.C:
            assert all(b.campo != CLAVE for b in p.bloqueos), p.punto.id
    assert servicio.familias_que_usan(CLAVE) == (Familia.C,)


def test_el_prevuelo_anuncia_que_el_desnivel_detiene_y_solo_en_C(tmp_path):
    e = V.materializar(V.aplicar(V.juego_completo(), SIN_DESNIVEL), tmp_path)
    externos = servicio.cargar_datos_externos(e.externos, {})
    estimado = antc.datos_faltantes_por_punto(e.csv, externos,
                                              cli.ALCANCE_PERFIL)
    faltas = [x for x in estimado if x.dato == CLAVE]
    assert [x.id_punto for x in faltas] == ["C-01"]
    falta = faltas[0]
    assert falta.detiene
    assert falta.etapa == servicio.ETAPA_BUCLE_DE_MD
    assert M5.DETALLE_FALTA_DESNIVEL_CANAL in falta.de_donde
    # Con el dato declarado (el juego), no falta.
    e2 = V.materializar(V.juego_completo(), tmp_path / "con")
    con = antc.datos_faltantes_por_punto(
        e2.csv, servicio.cargar_datos_externos(e2.externos, {}), cli.ALCANCE_PERFIL)
    assert not [x for x in con if x.dato == CLAVE]


def test_la_clave_ya_no_es_una_entrada_con_via_alterna():
    assert CLAVE not in servicio.EXTERNOS_CON_VIA_ALTERNA
    assert servicio.DETALLE_FALTA_DESNIVEL_CANAL is M5.DETALLE_FALTA_DESNIVEL_CANAL
