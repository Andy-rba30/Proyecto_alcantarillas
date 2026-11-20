"""
tests/test_ve4e_agua_por_condicion.py
=====================================
VE-4e (ficha VE3-21 de `docs/decisiones_diferidas.md`): las cargas WA del
cabezal --empuje del agua del relleno y subpresion-- POR CONDICION cuando el
trasdos se declara sin drenaje.

  * ESTATICA, con 'drenaje_trasdos' = 'sin_drenaje': el agua sigue llenando
    el relleno retenido hasta su superficie (AASHTO 11.6.6, la hidrostatica
    plena del agua del relleno; lectura del proyecto, cita
    AASHTO_LRFD_9.11.6.6#DRENAJE).
  * SISMICA: el comentario C11.6.5.3 recomienda el nivel MEDIO del agua en
    el tiempo (cita AASHTO_LRFD_9.C11.6.5.3#NIVEL_MEDIO). Cual es ese nivel
    en un relleno que no drena NO lo dice la fuente: lo decide un [A] nuevo,
    'nivel_agua_relleno_sin_drenaje_bajo_sismo', SIN valor de archivo (la
    regla de CLAUDE.md para un vacio: se declara o se detiene), con dos
    opciones que el programa ya sabe calcular --la superficie del relleno
    (el relleno queda lleno en el tiempo) o el freatico natural del punto
    (se llena solo por episodios)--.
  * Con 'drenado' --el valor de archivo desde VE-3.16-- el criterio nuevo NO
    SE LEE y ningun numero cambia: el agua bajo sismo es la del freatico del
    punto, la misma que en la estatica. Se mide sobre el muro de tanteo de
    T-7b y sobre el juego de la validacion integral (base y titular).

SE ESCRIBIO EN ROJO PRIMERO contra 7826184.
"""

from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

import pytest

from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src.modelos import (CARGA_WA, CondicionAnalisis, CriterioPendienteError,
                         EntornoDelCabezal, GeometriaCabezal,
                         TipoDeBloqueo)
from src.modulos import M9_cabezal as M9
from src.normativa.esquema import Caracter
from src.normativa.registro import construir
from tests.apoyo.aproximacion import ABS_CERO
from tests.apoyo.criterios import con_valor, sin_valor
from tests.fixtures.casos_patron import CP_T7B_ESTABILIDAD

CP = CP_T7B_ESTABILIDAD
EST = CondicionAnalisis.ESTATICO
SIS = CondicionAnalisis.SISMICO
CLAVE = "nivel_agua_relleno_sin_drenaje_bajo_sismo"
CITA_NIVEL_MEDIO = "AASHTO_LRFD_9.C11.6.5.3#NIVEL_MEDIO"
GAMMA_SAT_DE_PRUEBA = 20.0          # kN/m3, el del dorado de T-7b


# ---------------------------------------------------------------------------
# El muro de tanteo de T-7b (`CP_T7B_ESTABILIDAD`), con su coeficiente
# sismico impuesto (k_h = 0.25, k_v = 0)
# ---------------------------------------------------------------------------

def _entorno(**cambios) -> EntornoDelCabezal:
    g = GeometriaCabezal(**dict(CP["geometria"], cota_desplante=100.0,
                                cota_coronacion=102.55, id_punto="T-00",
                                extremo="entrada"))
    base = dict(id_punto="T-00", extremo=g.extremo, geometria=g,
                cota_relleno=100.0 + CP["h"],
                cota_borde_plataforma=100.0 + CP["h"],
                origen_cota_borde="de prueba", talud=1.5, esviaje_grados=0.0,
                cota_freatico=100.0 + g.D_f - CP["NF"],
                cota_pie=100.0 + g.D_f, suelo=dict(CP["suelo"]))
    base.update(cambios)
    return EntornoDelCabezal(**base)


@pytest.fixture
def tanteo(monkeypatch):
    """El muro de tanteo de T-7b, con el freatico bajo la zapata."""
    ca.establecer_valor_dinamico("phi_relleno_trasdos", CP["phi_relleno"])
    ca.establecer_valor_dinamico("peso_especifico_relleno_kn_m3",
                                 CP["gamma_relleno"])
    ds.establecer_dato_dinamico(
        "orientacion_muro_respecto_al_trafico", "paralelo_al_trafico",
        "de prueba (VE-4e)", "2026-11-20", origen="prueba")
    ds.establecer_dato_dinamico(
        "distancia_borde_calzada_al_trasdos_m", 1.6,
        "de prueba (VE-4e)", "2026-11-20", origen="prueba")
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h=CP["sismico"]["k_h"], k_v=0.0))
    return _entorno()


def _freatico_a(entorno, profundidad):
    """El freatico a `profundidad` bajo el terreno del pie."""
    return replace(entorno, cota_freatico=entorno.cota_pie - profundidad)


def _por_codigo(cargas):
    return {c.codigo: c for c in cargas}


def _mismas_cargas(a, b):
    """Las dos tuplas de cargas tienen los mismos codigos y las mismas cifras."""
    pa, pb = _por_codigo(a), _por_codigo(b)
    assert set(pa) == set(pb)
    for codigo in pa:
        for campo in ("V", "H", "x", "z"):
            assert getattr(pa[codigo], campo) == pytest.approx(
                getattr(pb[codigo], campo), abs=ABS_CERO), (codigo, campo)


def _leido(clave):
    return clave in ca.criterios_usados()


# ===========================================================================
# 1. La ficha y la cita
# ===========================================================================

def test_el_nivel_medio_de_un_relleno_sin_drenar_es_un_A_sin_valor():
    c = ca.CRITERIOS[CLAVE]
    assert c.valor is None and not c.opcional
    assert c.etiqueta == "A"
    assert c.nivel == ca.NIVEL_EXPEDIENTE
    assert c.forma == ca.FORMA_CATEGORIA
    assert c.sensibilidad == (M9.NIVEL_MEDIO_SUPERFICIE,
                              M9.NIVEL_MEDIO_FREATICO)
    assert M9.NIVELES_MEDIOS_SIN_DRENAJE == c.sensibilidad
    assert M9.CRITERIO_NIVEL_AGUA_SISMO == CLAVE
    for cita in (CITA_NIVEL_MEDIO, "AASHTO_LRFD_9.11.6.6#DRENAJE"):
        assert cita in c.justificacion, cita
    # Las dos opciones entran por la puerta de la ventana.
    for opcion in c.sensibilidad:
        ca.verificar_declaracion(CLAVE, opcion)
    with pytest.raises(ValueError):
        ca.verificar_declaracion(CLAVE, "a_media_altura")


def test_la_cita_del_nivel_medio_es_la_recomendacion_de_C11_6_5_3():
    reg = construir()
    cita = reg.cita(CITA_NIVEL_MEDIO)
    assert cita.numeral == "C11.6.5.3"
    assert cita.pagina_impresa == "11-31" and cita.pagina_pdf == 1500
    assert cita.caracter is Caracter.RECOMENDACION
    assert ("time-averaged mean groundwater elevation should be used when "
            "assessing groundwater effects") in cita.texto_literal.texto
    # La lectura del proyecto se declara aparte, con lo que juega en contra.
    assert cita.interpretacion is not None
    assert cita.interpretacion.en_contra


# ===========================================================================
# 2. Con 'drenado' (archivo) nada cambia y el criterio nuevo no se lee
# ===========================================================================

def test_drenado_el_sismo_tiene_el_agua_de_la_estatica_y_no_lee_el_nivel(
        tanteo):
    assert ca.valor("drenaje_trasdos") == "drenado"
    entorno = _freatico_a(tanteo, 0.30)         # 0.50 m de agua sobre la base
    ca.reiniciar_usos()
    with con_valor("peso_especifico_saturado_relleno_kn_m3",
                   GAMMA_SAT_DE_PRUEBA, motivo="dato de ensayo de prueba"):
        _c, d_est = M9.cargas_del_cabezal(entorno, EST)
        _c, d_sis = M9.cargas_del_cabezal(entorno, SIS)
    assert d_est["h_w"] == pytest.approx(0.50, abs=ABS_CERO)
    assert d_sis["h_w"] == pytest.approx(d_est["h_w"], abs=ABS_CERO)
    assert not _leido(CLAVE)
    # Y el ensamble no lo pide aunque el criterio siga sin valor.
    with con_valor("peso_especifico_saturado_relleno_kn_m3",
                   GAMMA_SAT_DE_PRUEBA, motivo="dato de ensayo de prueba"):
        M9.ensamble_estabilidad(entorno, SIS)
    assert not _leido(CLAVE)


# ===========================================================================
# 3. Sin drenaje: estatica llena, sismo con el nivel medio declarado
# ===========================================================================

def test_sin_drenaje_la_estatica_llena_el_relleno_y_no_lee_el_nivel(tanteo):
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    ca.reiniciar_usos()
    with con_valor("peso_especifico_saturado_relleno_kn_m3",
                   GAMMA_SAT_DE_PRUEBA, motivo="dato de ensayo de prueba"):
        cargas, datos = M9.cargas_del_cabezal(tanteo, EST)
    assert datos["h_w"] == pytest.approx(CP["h"], abs=ABS_CERO)
    assert _por_codigo(cargas)["WA.h"].H == pytest.approx(
        9.81 * CP["h"] ** 2 / 2, abs=ABS_CERO)
    assert not _leido(CLAVE)


def test_sin_drenaje_el_sismo_sin_el_nivel_declarado_se_detiene(tanteo):
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    with con_valor("peso_especifico_saturado_relleno_kn_m3",
                   GAMMA_SAT_DE_PRUEBA, motivo="dato de ensayo de prueba"):
        M9.ensamble_estabilidad(tanteo, EST)          # la estatica sigue
        with pytest.raises(CriterioPendienteError) as exc:
            M9.ensamble_estabilidad(tanteo, SIS)
    assert exc.value.clave == CLAVE


def test_sin_drenaje_con_la_superficie_el_sismo_es_el_de_antes(tanteo):
    """
    'superficie_del_relleno': el relleno sin drenar queda lleno en el tiempo,
    y su nivel medio es su superficie. Es lo que el programa hacia hasta
    VE-4e con 'sin_drenaje': el agua del sismo es la de la estatica, y el
    incremento va con el peso total bajo el agua (VE-3.14, C11.6.5.3).
    """
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    ca.establecer_valor_dinamico(CLAVE, M9.NIVEL_MEDIO_SUPERFICIE)
    with con_valor("peso_especifico_saturado_relleno_kn_m3",
                   GAMMA_SAT_DE_PRUEBA, motivo="dato de ensayo de prueba"):
        c_est, d_est = M9.cargas_del_cabezal(tanteo, EST)
        c_sis, d_sis = M9.cargas_del_cabezal(tanteo, SIS)
    assert d_sis["h_w"] == pytest.approx(d_est["h_w"], abs=ABS_CERO)
    assert d_sis["h_w"] == pytest.approx(CP["h"], abs=ABS_CERO)
    est, sis = _por_codigo(c_est), _por_codigo(c_sis)
    for codigo in ("WA.h", "WA.u", "EH.h", "EH.v", "EV.talon"):
        for campo in ("V", "H", "x", "z"):
            assert getattr(sis[codigo], campo) == pytest.approx(
                getattr(est[codigo], campo), abs=ABS_CERO), (codigo, campo)
    assert d_sis["tratamiento_agua_sismo"] == M9.AGUA_SE_MUEVE_CON_EL_SUELO
    assert d_sis["nivel_agua_sismo"] == M9.NIVEL_MEDIO_SUPERFICIE


def test_sin_drenaje_con_el_freatico_el_sismo_es_el_del_relleno_drenado(
        tanteo):
    """
    'freatico_natural': el relleno sin drenar se llena solo por episodios y
    su nivel medio es el freatico natural del punto. Con el freatico bajo la
    zapata el sismo va en seco: sin WA, sin el peso saturado (que no se
    pide), y con las MISMAS cargas que el relleno drenado.
    """
    ca.establecer_valor_dinamico(CLAVE, M9.NIVEL_MEDIO_FREATICO)
    drenado, _ = M9.cargas_del_cabezal(tanteo, SIS)
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    with sin_valor("peso_especifico_saturado_relleno_kn_m3"):
        cargas, datos = M9.cargas_del_cabezal(tanteo, SIS)
        # La estatica sigue llena y pide el peso saturado.
        with pytest.raises(CriterioPendienteError) as exc:
            M9.cargas_del_cabezal(tanteo, EST)
    assert exc.value.clave == "peso_especifico_saturado_relleno_kn_m3"
    assert datos["h_w"] == pytest.approx(0.0, abs=ABS_CERO)
    assert not [c for c in cargas if c.tipo == CARGA_WA]
    assert datos["tratamiento_agua_sismo"] is None
    _mismas_cargas(cargas, drenado)


def test_sin_drenaje_con_el_freatico_alto_el_sismo_moja_hasta_el_natural(
        tanteo):
    """
    Freatico a 0.30 m bajo el pie (0.50 m sobre la base): con
    'freatico_natural' el agua del sismo es esa, delante y detras --la
    subpresion uniforme y el empuje del agua de 0.50 m--, la misma que con
    el relleno drenado; la estatica sigue con el relleno lleno.
    """
    entorno = _freatico_a(tanteo, 0.30)
    ca.establecer_valor_dinamico(CLAVE, M9.NIVEL_MEDIO_FREATICO)
    with con_valor("peso_especifico_saturado_relleno_kn_m3",
                   GAMMA_SAT_DE_PRUEBA, motivo="dato de ensayo de prueba"):
        drenado, _ = M9.cargas_del_cabezal(entorno, SIS)
        ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
        c_sis, d_sis = M9.cargas_del_cabezal(entorno, SIS)
        _c, d_est = M9.cargas_del_cabezal(entorno, EST)
    assert d_sis["h_w"] == pytest.approx(0.50, abs=ABS_CERO)
    assert d_est["h_w"] == pytest.approx(CP["h"], abs=ABS_CERO)
    sis = _por_codigo(c_sis)
    assert sis["WA.u"].V == pytest.approx(-9.81 * 0.50 * 2.0, abs=ABS_CERO)
    assert sis["WA.u"].x == pytest.approx(1.0, abs=ABS_CERO)
    assert sis["WA.h"].H == pytest.approx(9.81 * 0.50 ** 2 / 2, abs=ABS_CERO)
    _mismas_cargas(c_sis, drenado)


# ===========================================================================
# 4. Lo que la corrida dice
# ===========================================================================

def test_la_memoria_del_sismo_dice_el_nivel_y_su_cita(tanteo):
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    ca.establecer_valor_dinamico(CLAVE, M9.NIVEL_MEDIO_FREATICO)
    with con_valor("peso_especifico_saturado_relleno_kn_m3",
                   GAMMA_SAT_DE_PRUEBA, motivo="dato de ensayo de prueba"):
        e = M9.ensamble_estabilidad(tanteo, SIS)
        e_est = M9.ensamble_estabilidad(tanteo, EST)
    p = next(p for p in e.pasos if p.fundamento_id == "F9.SISMO")
    assert CITA_NIVEL_MEDIO in p.citas_textuales
    h_w = next(m for m in p.sustitucion if m.simbolo == "h_w")
    assert h_w.valor == pytest.approx(0.0, abs=ABS_CERO)
    assert CLAVE in h_w.procedencia and M9.NIVEL_MEDIO_FREATICO in \
        h_w.procedencia
    # El aviso de la estatica ya no dice que el sismo va con el relleno lleno:
    # nombra la eleccion de la que depende.
    aviso = next(a for a in e_est.avisos if "sin drenaje" in a.lower())
    assert CLAVE in aviso
    assert "tambien bajo sismo" not in aviso


def test_con_drenado_la_memoria_del_sismo_no_cambia(tanteo):
    """El relleno drenado no imprime ni la cita ni el nivel nuevos."""
    e = M9.ensamble_estabilidad(tanteo, SIS)
    p = next(p for p in e.pasos if p.fundamento_id == "F9.SISMO")
    assert CITA_NIVEL_MEDIO not in p.citas_textuales
    assert not [m for m in p.sustitucion if m.simbolo == "h_w"]


# ===========================================================================
# 5. Sobre el juego de la validacion integral
# ===========================================================================

@pytest.fixture(scope="module")
def corridas_del_juego():
    from tests.apoyo import validacion_integral as V
    return {"juego": V.correr_juego(V.juego_completo()),
            "titular": V.correr_juego(V.juego_titular())}


@pytest.mark.parametrize("base", ("juego", "titular"))
def test_en_el_juego_drenado_el_nivel_medio_no_se_lee(corridas_del_juego,
                                                      base):
    """
    Las dos bases de la validacion integral corren con el trasdos drenado de
    archivo: llegan al sismo del cabezal y no leen el criterio nuevo, de
    modo que sus numeros son los de antes (lo que fija ademas, cifra a
    cifra, la sincronia de `docs/validacion_integral.md`).
    """
    informe = corridas_del_juego[base]
    usados = informe.contexto.criterios_usados
    assert "drenaje_trasdos" in usados
    assert CLAVE not in usados
    assert CLAVE in informe.contexto.criterios_sin_valor


def test_en_el_juego_sin_drenaje_el_sismo_pide_el_nivel_medio():
    """
    El juego con 'sin_drenaje' declarado y el nivel medio sin declarar: la
    estabilidad sismica de los cabezales se detiene por el criterio --un
    `Bloqueo` de criterio pendiente que nombra la clave--, y la estatica no.
    """
    from tests.apoyo import validacion_integral as V
    informe = V.correr_juego(V.aplicar(V.juego_completo(), (
        ("declarar", "drenaje_trasdos", "sin_drenaje"),)))
    pendientes = [b for p in informe.puntos for b in p.bloqueos
                  if b.criterio == CLAVE]
    assert pendientes, "el sismo sin el nivel medio declarado no se detuvo"
    assert all(b.tipo is TipoDeBloqueo.CRITERIO_PENDIENTE for b in pendientes)
    assert all("sis" in b.etapa.lower() for b in pendientes), \
        [b.etapa for b in pendientes]
    assert CLAVE in informe.contexto.criterios_usados
