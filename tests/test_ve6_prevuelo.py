# -*- coding: utf-8 -*-
"""
tests/test_ve6_prevuelo.py
==========================
VE-6 (pre-vuelo): las dos causas que la integracion de VE-5 dejo en rojo.

(a) M12 y `NF_profundidad_m`. El censo de `variables_entrada` le encuentra
    la columna a M12 (`renglones_excavacion`, partida 501.C/D), y M12 no se
    difiere entero a perfil: la fila del cuadro de compatibilidad corre en
    los dos alcances. El pre-vuelo le atribuia por eso la columna a nivel de
    perfil y la anunciaba como DATO QUE DETIENE en todos los puntos, y la
    corrida real no se detenia por ella: los metrados van detras de la Fase
    9. Desde VE-6 los dos leen el mismo dato, `servicio.CONSUMO_DETRAS_DE`.

(b) La Fase 0-bis (licuefaccion, ficha VE5-CAT-03) se registra AL LADO del
    dimensionado, sin anteponerse: la corrida sigue diciendo las faltas del
    bucle de MD, y quien busca por que un punto no llego a 7.A (la fila del
    cuadro de compatibilidad) salta esa fase.
"""

from __future__ import annotations

import ast
import inspect

import cli
from src import anticipo as antc
from src import servicio
from src.modelos import TipoDeBloqueo
from tests.apoyo import validacion_integral as V
from tests.fixtures import juego_validacion_integral as J

NF = "NF_profundidad_m"


# --- (a) ------------------------------------------------------------------

def test_a_perfil_m12_no_consume_y_a_expediente_si():
    assert "M12_metrados" in antc._ve.variable(NF).consumido_por
    assert "M12_metrados" not in servicio.MODULOS_DIFERIDOS_POR_ALCANCE[
        cli.ALCANCE_PERFIL]
    assert servicio.consumo_diferido(cli.ALCANCE_PERFIL, "M12_metrados")
    assert not servicio.consumo_diferido(cli.ALCANCE_EXPEDIENTE, "M12_metrados")
    assert "M12_metrados" not in antc._consumidores_de_calculo(
        NF, cli.ALCANCE_PERFIL)
    assert "M12_metrados" in antc._consumidores_de_calculo(
        NF, cli.ALCANCE_EXPEDIENTE)


def test_el_salto_de_los_metrados_consulta_el_mismo_dato():
    """El `if` de `correr_punto` que salta los metrados llama a
    `consumo_diferido` con M12: no hay una segunda regla escrita aparte.
    Desde VE-7 (lote A, A2) el pipeline del punto es `_correr_punto`:
    `correr_punto` lo envuelve con la embocadura declarada por punto."""
    arbol = ast.parse(inspect.getsource(servicio._correr_punto))
    llamadas = [n for n in ast.walk(arbol) if isinstance(n, ast.If)
                and any(isinstance(c, ast.Call)
                        and getattr(c.func, "id", "") == "consumo_diferido"
                        and any(isinstance(a, ast.Constant)
                                and a.value == "M12_metrados" for a in c.args)
                        for c in ast.walk(n.test))
                and any(isinstance(c, ast.Call)
                        and getattr(c.func, "id", "") == "_fase_11_metrados"
                        for b in n.body for c in ast.walk(b))]
    assert len(llamadas) == 1


def test_la_relacion_es_la_que_test_nivel_medido_usa_para_los_criterios():
    from tests.test_nivel_medido import DETRAS_DEL_CABEZAL
    assert set(DETRAS_DEL_CABEZAL.values()) == {
        servicio.CONSUMO_DETRAS_DE["M12_metrados"]}


# --- (b) ------------------------------------------------------------------

def test_la_licuefaccion_no_es_el_motivo_del_cuadro_de_compatibilidad():
    """
    A expediente, sin `licuefaccion_ems` declarado, cada punto lleva el
    bloqueo de la Fase 0-bis, el primero de su lista. (Desde VE-7 fix-suite
    el juego SI lo declara; el test lo quita: lo que mide es la falta.) B-01 de la variante
    de referencia se detiene en el bucle de MD por `Q_evento_extremo_m3s`:
    la fila del cuadro dice esa fase, no la 0-bis, y las dos faltas estan.
    """
    informe = V.correr_juego(V.aplicar(
        V.juego_completo(),
        tuple(J.VARIANTES[V.VARIANTE_DE_REFERENCIA][1]) + (_SIN_EMS,)))
    b01 = next(p for p in informe.puntos if p.punto.id == "B-01")
    faltan = {(b.fase, b.campo) for b in b01.bloqueos
              if b.tipo is TipoDeBloqueo.DATO_FALTANTE}
    assert (servicio.FASE_LICUEFACCION, servicio.CLAVE_LICUEFACCION_EMS) in faltan
    assert any(campo == "Q_evento_extremo_m3s" for _f, campo in faltan)
    motivo = b01.compatibilidad_rasante.motivo
    assert servicio.FASE_LICUEFACCION not in motivo
    assert servicio.ETAPA_BUCLE_DE_MD in motivo


# ===========================================================================
# VE-6, dictamen Fable («aprobar con cambios» en las dos decisiones)
# ===========================================================================

import copy                                                    # noqa: E402

import pytest                                                  # noqa: E402

from src.modelos import Bloqueo, DatoInvalidoError             # noqa: E402
from src.modulos import M12_metrados as M12                    # noqa: E402

_DEFECTO_SIN_TAMIZADO = "el punto no llego a 7.A con una seccion adoptada"


@pytest.fixture(scope="module")
def juego_expediente():
    return V.correr_juego(V.juego_completo())


# --- VE-7 fix-suite --- el juego declara `licuefaccion_ems` (global); lo que
# depende de la Fase 0-bis ABIERTA se mide quitandolo.
_SIN_EMS = ("externo", "globales", servicio.CLAVE_LICUEFACCION_EMS, None)


@pytest.fixture(scope="module")
def juego_expediente_sin_ems():
    return V.correr_juego(V.aplicar(V.juego_completo(), (_SIN_EMS,)))


def _bloqueo(fase, etapa):
    return Bloqueo(fase=fase, etapa=etapa, tipo=TipoDeBloqueo.DATO_INVALIDO,
                   mensaje="(prueba)")


def _sin_tamizado(punto, bloqueos):
    informe = servicio.InformePunto(punto=punto)
    informe.bloqueos.extend(bloqueos)
    servicio._fase_11_compatibilidad(informe)
    return informe.compatibilidad_rasante.motivo


# --- 1 (b): seleccion positiva de las fases que llevan a 7.A ---------------

def test_las_fases_que_llevan_a_7a_son_las_cinco_y_la_0bis_queda_fuera():
    assert servicio.FASES_QUE_LLEVAN_A_7A == (
        servicio.FASE_CARGA, servicio.FASE_CLASIFICACION,
        servicio.FASE_HIDROLOGIA, servicio.FASE_DISENO,
        servicio.FASE_GEOMETRIA)
    assert servicio.FASE_LICUEFACCION in servicio.FASES_AL_MARGEN_DEL_DIMENSIONADO
    assert servicio.FASE_PROTECCION in servicio.FASES_AL_MARGEN_DEL_DIMENSIONADO
    assert not set(servicio.FASES_AL_MARGEN_DEL_DIMENSIONADO) & set(
        servicio.FASES_QUE_LLEVAN_A_7A)


def test_un_techo_de_transcripcion_mal_declarado_no_es_el_motivo(monkeypatch):
    """(i) El bloqueo de los techos (Fase 6, antes que nada en el punto) en
    B-01, que se detiene en el bucle de MD: el motivo es el del bucle."""
    def _techo_mal_declarado(_dato):
        raise DatoInvalidoError("techos_de_transcripcion_fase_6",
                                valor="Sv: -1", motivo="(prueba)")
    monkeypatch.setattr(servicio, "avisos_de_transcripcion", _techo_mal_declarado)
    informe = V.correr_juego(V.aplicar(V.juego_completo(),
                                       J.VARIANTES[V.VARIANTE_DE_REFERENCIA][1]))
    b01 = next(p for p in informe.puntos if p.punto.id == "B-01")
    assert b01.bloqueos[0].fase == servicio.FASE_PROTECCION
    motivo = b01.compatibilidad_rasante.motivo
    assert servicio.FASE_PROTECCION not in motivo
    assert servicio.FASE_DISENO in motivo and servicio.ETAPA_BUCLE_DE_MD in motivo


def test_un_bloqueo_de_la_fase_6_con_7b_fallida_nombra_la_geometria(
        juego_expediente):
    """(ii) La proteccion se bloquea y 7.B tambien: el motivo es 7.B."""
    punto = juego_expediente.puntos[0].punto
    motivo = _sin_tamizado(punto, [
        _bloqueo(servicio.FASE_LICUEFACCION, "evaluacion de licuefaccion"),
        _bloqueo(servicio.FASE_PROTECCION, "d50, espesor y longitud"),
        _bloqueo(servicio.FASE_GEOMETRIA, "compatibilidad geometrica (7.B)")])
    assert servicio.FASE_GEOMETRIA in motivo
    assert servicio.FASE_PROTECCION not in motivo


def test_sin_bloqueo_que_lleve_a_7a_el_motivo_es_el_de_m12(juego_expediente):
    punto = juego_expediente.puntos[0].punto
    motivo = _sin_tamizado(punto, [
        _bloqueo(servicio.FASE_LICUEFACCION, "evaluacion de licuefaccion"),
        _bloqueo(servicio.FASE_ESTRUCTURAL, "(prueba)")])
    assert motivo == _DEFECTO_SIN_TAMIZADO


# --- 2 (a): el renglon bajo agua avisa que la partida la fija el Supervisor -

def test_todo_renglon_bajo_agua_lleva_el_aviso_y_el_seco_no(juego_expediente):
    renglones = [r for p in juego_expediente.puntos if p.metrado
                 for r in p.metrado.renglones if r.rubro == M12.RUBRO_EXCAVACION]
    assert renglones
    for r in renglones:
        bajo_agua = r.partida in ("501.B", "501.D")
        assert (M12.AVISO_PARTIDA_BAJO_AGUA in r.avisos) is bajo_agua, r.elemento
    # La pieza directa, con volumen bajo agua seguro.
    salida = M12._renglones_por_agua(
        punto=None, en_roca=False, elemento="zanja", V=2.0, V_agua=1.0,
        paso_=renglones[0].paso)
    por_partida = {r.partida: r for r in salida}
    assert M12.AVISO_PARTIDA_BAJO_AGUA in por_partida["501.D"].avisos
    assert M12.AVISO_PARTIDA_BAJO_AGUA not in por_partida["501.C"].avisos
    for necesario in ("NF_profundidad_m", "Supervisor", "501.09", "501.01",
                      "886"):
        assert necesario in M12.AVISO_PARTIDA_BAJO_AGUA, necesario


# --- 3: un alcance desconocido falla igual que en `_difiere` --------------

def test_consumo_diferido_con_un_alcance_desconocido_falla_como_difiere():
    with pytest.raises(KeyError):
        servicio._difiere("otro", "M12_metrados")
    with pytest.raises(KeyError):
        servicio.consumo_diferido("otro", "M12_metrados")


# --- 4: sin cabezal, la Fase 11 lo dice ------------------------------------

def _sin_cabezal(juego_expediente, previos=()):
    informe = copy.copy(next(p for p in juego_expediente.puntos
                             if p.punto.id == "A-01"))
    informe.cabezal, informe.metrado = None, None
    informe.bloqueos = list(previos)
    servicio._fase_11_metrados(informe)
    return informe


def test_sin_cabezal_la_fase_11_registra_su_bloqueo(juego_expediente):
    informe = _sin_cabezal(juego_expediente)
    propios = [b for b in informe.bloqueos if b.fase == servicio.FASE_METRADOS]
    assert len(propios) == 1
    assert propios[0].etapa == servicio.ETAPA_METRADOS_SIN_CABEZAL
    assert informe.metrado is None


def test_sin_cabezal_con_bloqueo_de_la_fase_9_remite_a_el(juego_expediente):
    previo = _bloqueo(servicio.FASE_CABEZAL, "estabilidad del cabezal (prueba)")
    informe = _sin_cabezal(juego_expediente, (previo,))
    propios = [b for b in informe.bloqueos if b.fase == servicio.FASE_METRADOS]
    assert len(propios) == 1
    assert servicio.FASE_CABEZAL in propios[0].mensaje
    assert "estabilidad del cabezal (prueba)" in propios[0].mensaje


# --- 5: la cimentacion del cabezal es provisional con la 0-bis abierta -----

def test_con_la_0bis_abierta_la_cimentacion_del_cabezal_es_provisional(
        juego_expediente_sin_ems):
    for p in juego_expediente_sin_ems.puntos:
        abierta = any(b.fase == servicio.FASE_LICUEFACCION
                      and not b.diferido_por_alcance for b in p.bloqueos)
        assert abierta, p.punto.id          # sin el EMS declarado
        assert servicio.AVISO_CIMENTACION_PROVISIONAL in p.avisos_de_expediente
    assert "10.5.4.2" in servicio.AVISO_CIMENTACION_PROVISIONAL


def test_a_perfil_no_hay_aviso_de_cimentacion_provisional():
    informe = V.correr_juego(V.juego_completo(), alcance=cli.ALCANCE_PERFIL)
    for p in informe.puntos:
        assert servicio.AVISO_CIMENTACION_PROVISIONAL not in p.avisos_de_expediente
