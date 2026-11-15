"""
tests/test_t9_correcciones.py
=============================
La aceptacion de las CORRECCIONES de la auditoria adversarial de T-9 (Fase
10, espaciamiento de alivios; `docs/planes_mejora/orquestacion_T/
AUDITORIA_T-9.md`, 2026-11-13) y de las decisiones A-D del dueño del
2026-11-12, hallazgo por hallazgo:

  H1  (ALTA)  la condicion LITERAL del Manual -- el caudal de aporte contra la
              capacidad de la cuneta -- es VB2 y puede fallar; con el tramo
              conocido el aporte se reparte como Q / s; sin el, q · b con la
              longitud implicita avisada.
  H2          un VB1 sin evaluar es un BLOQUEO del punto, no un aviso.
  H3          los huecos de cuneta que VB1 no mira se avisan; un inicio
              posterior a la obra no se acepta; los textos no suponen el
              sentido del flujo.
  H4 + D      el TR del aporte es el del PUNTO, y la fila de la Tabla Nº 02
              es una envolvente declarada como `Interpretacion`.
  H5 + A      'seccion_cuneta' con el minimo muy lluvioso de la Tabla Nº 34,
              la ventana desde ahi y el talud interior contra la Tabla 304.12.
  B           la v8 ya no pide «con borde libre» sin cifra.
  C           las obras de Familia A cierran el tramo por defecto
              ('obras_familia_a_extremo_de_cuneta'): B-01 queda a 530 m de A-02
              y VB1 NO CUMPLE en el fixture, sin mover ningun diametro.
  H6-H11      la justificacion del revestimiento, los mutantes vivos de M10,
              la exencion de caso patron, `area_ha` en B, las lecturas como
              `Interpretacion` y el aporte calculado que no se recalcula.
  Dudosos     la cuneta del tramo y no la del cruce, la Tabla Nº 32 frente a
              la Nº 09, y la nota «*» de la Tabla Nº 33 desde el registro.

LOS TESTS SE ESCRIBIERON DESPUES DEL CODIGO y se dice: el rojo se midio
corriendo este archivo contra un arbol exportado de `304cea6` (la FASE A de
T-9), con el resultado que la ficha de las correcciones en
`docs/decisiones_diferidas.md` declara.

Los dorados son ARITMETICA ESCRITA en este archivo; los CSV y JSON son DATOS
DE PRUEBA, no del proyecto.
"""

from __future__ import annotations

import ast
import csv
import io
import json
import math
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from src import anticipo
from src import constantes_normativas as CN
from src import criterios_adoptados as ca
from src import servicio
from src.modelos import (CriterioPendienteError, DatoInvalidoError,
                         EstadoDeVerificacion, Familia, TipoDeBloqueo,
                         TipoDeVeredicto)
from src.modulos import M10_espaciamiento as M10
from src.modulos import M11_reporte as M11
from src.modulos.M1_clasificacion import PERFILES
from src.normativa import registro as _registro
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.fixtures.casos_patron import CP_T9_CUNETA

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
V8 = RAIZ / "docs" / "hoja_de_ruta_alcantarillas_v8.md"
GUIA = RAIZ / "docs" / "guia_perfil.md"
HIDRO = RAIZ / "tests" / "fixtures" / "hidrologia"

REL_ARITMETICA = 1e-4        # la aritmetica escrita con cuatro o cinco cifras
REL_FORMULA = 1e-9           # una formula recomputada en el test

CRITERIOS_QUE_SE_TOCAN = ("seccion_cuneta", "revestimiento_cuneta",
                          "lectura_velocidad_limite_cuneta",
                          "obras_familia_a_extremo_de_cuneta",
                          "riesgo_admisible_propietario",
                          "homogeneidad_serie_fen")


@pytest.fixture(autouse=True)
def _limpio():
    yield
    for clave in CRITERIOS_QUE_SE_TOCAN:
        if ca.declarado_en_caliente(clave):
            ca.quitar_valor_dinamico(clave)


def _sustituir_seccion(monkeypatch, seccion):
    """La seccion del AUDITOR (0.20 x 0.50) ya no entra por la puerta."""
    original = ca.valor
    monkeypatch.setattr(ca, "valor", lambda clave: (
        dict(seccion) if clave == "seccion_cuneta" else original(clave)))


def _csv_con(tmp_path, filas_extra=(), cambios=None, nombre="puntos.csv",
             solo=None):
    """El fixture del repositorio con filas B extra (copias de B-01)."""
    texto = CSV.read_text(encoding="utf-8")
    lector = list(csv.DictReader(io.StringIO(texto)))
    campos = list(lector[0].keys())
    filas = [dict(f) for f in lector]
    b01 = next(f for f in filas if f["id"] == "B-01")
    for id_nuevo, prog in filas_extra:
        filas.append(dict(b01, id=id_nuevo, progresiva_km=prog))
    for id_punto, cambio in (cambios or {}).items():
        next(f for f in filas if f["id"] == id_punto).update(cambio)
    if solo is not None:
        filas = [f for f in filas if f["id"] in solo]
    salida = io.StringIO()
    escritor = csv.DictWriter(salida, fieldnames=campos, lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(filas)
    ruta = tmp_path / nombre
    ruta.write_text(salida.getvalue(), encoding="utf-8")
    return ruta


def _externos(tmp_path, contenido, nombre="externos.json"):
    ruta = tmp_path / nombre
    ruta.write_text(json.dumps(contenido), encoding="utf-8")
    return servicio.cargar_datos_externos(ruta, {})


def _punto(informe, id_punto):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


def _verificacion(punto, codigo):
    return next((v for _f, v in punto.verificaciones() if v.codigo == codigo),
                None)


# ===========================================================================
# H1 - VB2: la condicion literal del Manual, y el aporte por metro
# ===========================================================================

def test_h1_la_cita_de_la_condicion_esta_en_su_pagina_y_exige():
    c = _registro.construir().cita("MC_HHD.4.1.2.1a#CONDICION")
    assert "Q manning > Q de aporte" in c.texto_literal.texto
    assert c.pagina_impresa == "177" and c.texto_literal.pagina_pdf == 180
    assert c.caracter.value == "exigencia"
    f = _registro.construir().fundamento("F10.APORTE_CAPACIDAD")
    assert f.verbo.value == "obliga" and "MC_HHD.4.1.2.1a#CONDICION" in f.citas


def test_h1_el_caso_del_auditor_da_VB2_no_cumple_en_M10(monkeypatch):
    """
    El caso del auditor, contra su aritmetica (CP_T9_CUNETA['auditor']):
    seccion 0.20 x 0.50, Z2 = 0.5, concreto, S = 0.005, Q = 0.095.
    """
    cp = CP_T9_CUNETA["auditor"]
    _sustituir_seccion(monkeypatch, cp["seccion"])
    c = M10.capacidad_cuneta(S_cuneta=cp["S"])
    assert c.area_llena_m2 == pytest.approx(cp["A"], rel=REL_ARITMETICA)
    assert c.radio_llena_m == pytest.approx(cp["Rh"], rel=REL_ARITMETICA)
    assert c.Q_admisible_m3s == pytest.approx(cp["Q_adm"], rel=REL_ARITMETICA)
    assert c.gobierna == "cuneta llena"
    aporte = M10.verificar_aporte(capacidad=c, Q_aporte_m3s=cp["Q"],
                                  origen_aporte="dato del test")
    v = aporte.verificacion
    assert v.codigo == "VB2" and not v.cumple
    assert v.estado is EstadoDeVerificacion.NO_CUMPLE
    assert v.paso.veredicto.margen == pytest.approx(cp["margen_VB2"],
                                                    rel=REL_ARITMETICA)
    assert v.criterio_aplicado == "seccion_cuneta"
    assert v.paso.umbral.cita_id == "MC_HHD.4.1.2.1a#CONDICION"


def test_h1_el_caso_del_auditor_en_la_corrida_falla_VB2_y_VB1(tmp_path,
                                                              monkeypatch):
    """
    La corrida del auditor (B-02 en 2+650 tras B-01), y lo que da ahora:

      B-02: tramo desde B-01 de 200 m; L = Q_adm · s / Q
            = 0.052215 · 200 / 0.095 = 109.93 m < 200  -> VB1 NO CUMPLE
      B-01: tramo desde A-02 (decision C) de 530 m;
            L = 0.052215 · 530 / 0.095 = 291.30 m      -> maximo 200 m
      las dos: Q = 0.095 > Q_adm = 0.052215            -> VB2 NO CUMPLE

    En la FASE A el mismo caso daba L = 8 244 m y VB1 CUMPLE.
    """
    cp = CP_T9_CUNETA["auditor"]
    _sustituir_seccion(monkeypatch, cp["seccion"])
    ruta = _csv_con(tmp_path, [("B-02", "2+650")])
    datos = {"globales": {"luz_m": 2.75, "ancho_tributario_m": 12.0,
                          "S_cuneta": cp["S"]}}
    informe = servicio.correr(ruta, _externos(tmp_path, datos), "perfil")
    b01, b02 = _punto(informe, "B-01"), _punto(informe, "B-02")
    for p in (b01, b02):
        vb2 = _verificacion(p, "VB2")
        assert vb2 is not None and not vb2.cumple
        assert vb2 in p.incumplidas()
    lh2 = b02.espaciamiento.longitud_hidraulica
    assert lh2.longitud_tramo_m == pytest.approx(200.0, rel=REL_ARITMETICA)
    assert lh2.L_hidraulico == pytest.approx(cp["L_200"], rel=REL_ARITMETICA)
    vb1 = _verificacion(b02, "VB1")
    assert not vb1.cumple
    assert vb1.valor_admisible == pytest.approx(cp["L_200"], rel=REL_ARITMETICA)
    assert vb1.criterio_aplicado == "seccion_cuneta"
    lh1 = b01.espaciamiento.longitud_hidraulica
    assert lh1.L_hidraulico == pytest.approx(cp["L_530"], rel=REL_ARITMETICA)
    assert not informe.cerrado and informe.resumen().incumplidas >= 3


def test_h1_con_el_tramo_conocido_la_longitud_es_la_condicion_escrita_como_longitud(monkeypatch):
    """L >= s si y solo si Q_adm >= Q, sin area ni ancho."""
    cp = CP_T9_CUNETA["auditor"]
    _sustituir_seccion(monkeypatch, cp["seccion"])
    c = M10.capacidad_cuneta(S_cuneta=cp["S"])
    for Q in (0.03, cp["Q"]):
        L = M10.longitud_hidraulica_por_tramo(
            capacidad=c, Q_aporte_m3s=Q, origen_aporte="t",
            longitud_tramo_m=200.0, extremo="B-01")
        assert L.L_hidraulico == pytest.approx(c.Q_admisible_m3s * 200.0 / Q,
                                               rel=REL_FORMULA)
        S_TRAMO = 200.0
        assert (L.L_hidraulico >= S_TRAMO) == (c.Q_admisible_m3s >= Q)
        assert L.escorrentia_m3s_km2 is None and L.ancho_tributario_m is None
        assert [p.codigo for p in L.pasos] == ["10.2", "10.3", "10.4"]


def test_h1_sin_tramo_se_conserva_q_por_b_y_se_avisa_la_longitud_implicita(tmp_path):
    """
    B-01 sin extremo (decision C en «no» y sin otra obra B), caudal declarado:

      q      = 0.095 / 0.18 = 0.527778 m3/s por km2
      q'     = 0.527778 · 12 / 10^6 = 6.333333e-6 m3/s por m
      L      = 0.670290 / 6.333333e-6 = 105 835 m
      s_impl = 0.18 · 10^6 / 12 = 15 000 m  >  200 m   -> aviso
    """
    ca.establecer_valor_dinamico("obras_familia_a_extremo_de_cuneta", "no")
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"ancho_tributario_m": 12.0, "S_cuneta": 0.01}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    b01 = _punto(informe, "B-01")
    lh = b01.espaciamiento.longitud_hidraulica
    assert lh.metodo_aporte.startswith("escorrentia especifica")
    assert lh.escorrentia_m3s_km2 == pytest.approx(0.527778, rel=REL_ARITMETICA)
    assert lh.q_por_metro_m3s_m == pytest.approx(6.333333e-6, rel=REL_ARITMETICA)
    assert lh.L_hidraulico == pytest.approx(105835.0, rel=REL_ARITMETICA)
    assert lh.s_implicita_m == pytest.approx(15000.0, rel=REL_ARITMETICA)
    aviso = next(a for a in b01.avisos() if "NO ES FIABLE" in a)
    assert "15000" in aviso and "'long_max_cuneta'" in aviso


def test_h1_un_area_que_si_es_la_faja_del_tramo_no_avisa(monkeypatch):
    """s_impl = 0.0024 km2 · 10^6 / 12 m = 200 m: no supera el normativo."""
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    L = M10.longitud_hidraulica(capacidad=c, escorrentia_m3s_km2=30.0,
                                origen_escorrentia="t", ancho_tributario_m=12.0,
                                area_km2=0.0024)
    assert L.s_implicita_m == pytest.approx(200.0, rel=REL_FORMULA)
    assert not any("NO ES FIABLE" in a for a in L.avisos)


def test_h1_L_declarado_gana_y_VB2_se_evalua_si_hay_pendiente(tmp_path):
    """
    Con la longitud declarada (120 m) y la pendiente de la cuneta, VB2 se
    evalua igual. Arena fina o limo (v = 0.20 m/s, K = 33) con la seccion de
    archivo y S = 0.005 (CP_T9_CUNETA['arena_fina']): Q_v = 0.0013188 m3/s,
    y el aporte de B-01 (0.095) la supera.
    """
    ca.establecer_valor_dinamico("revestimiento_cuneta",
                                 "terreno_arena_fina_o_limo")
    cp = CP_T9_CUNETA["arena_fina"]
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"L_hidraulico_m": 120.0,
                                 "S_cuneta": cp["S"]}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    b01 = _punto(informe, "B-01")
    assert b01.espaciamiento.L_hidraulico == pytest.approx(120.0, rel=REL_FORMULA)
    assert b01.espaciamiento.origen_L_hidraulico == "declarado"
    c = b01.aporte_alivio.capacidad
    assert c.Q_velocidad_m3s == pytest.approx(cp["Q_v"], rel=REL_ARITMETICA)
    assert c.gobierna == "velocidad limite admisible"
    assert not _verificacion(b01, "VB2").cumple


def test_h1_L_declarado_sin_pendiente_VB2_no_se_evalua_y_solo_avisa(tmp_path):
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"L_hidraulico_m": 120.0}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    b01 = _punto(informe, "B-01")
    assert b01.aporte_alivio.verificacion is None
    assert M10.AVISO_VB2_SIN_PENDIENTE in b01.avisos()
    assert not any(b.etapa == servicio.ETAPA_APORTE_CAPACIDAD
                   for b in b01.bloqueos)
    assert not any(b.campo == "S_cuneta" for b in b01.bloqueos)


def test_h1_sin_L_ni_pendiente_el_aviso_de_VB2_no_dice_que_se_declaro(tmp_path):
    informe = servicio.correr(CSV, _externos(tmp_path, {"globales": {
        "luz_m": 2.75}}), "perfil")
    b01 = _punto(informe, "B-01")
    assert M10.AVISO_VB2_SIN_PENDIENTE_NI_LONGITUD in b01.avisos()
    assert M10.AVISO_VB2_SIN_PENDIENTE not in b01.avisos()


def test_h1_con_el_tramo_conocido_la_fase_10_no_pide_el_ancho(tmp_path):
    """Q declarado y tramo conocido: q' = Q / s, el ancho no hace falta."""
    datos = {"globales": {"luz_m": 2.75}, "puntos": {"B-01": {"S_cuneta": 0.01}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    b01 = _punto(informe, "B-01")
    assert b01.espaciamiento is not None
    assert not any(b.campo == "L_hidraulico_m" for b in b01.bloqueos)


def test_h1_la_aceptacion_de_B_lleva_VB1_y_VB2():
    assert PERFILES[Familia.B].verificaciones_aceptacion == (
        "V1", "V2", "V4", "V5", "VB1", "VB2")


def test_h1_VB2_llega_a_la_CLI_al_JSON_y_a_la_memoria(tmp_path, monkeypatch):
    cp = CP_T9_CUNETA["auditor"]
    _sustituir_seccion(monkeypatch, cp["seccion"])
    datos = {"globales": {"luz_m": 2.75, "S_cuneta": cp["S"],
                          "L_hidraulico_m": 150.0}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    texto = cli.volcar(informe)
    assert "VB2" in texto and "Q de aporte" in texto
    volcado = cli.informe_json(informe)
    b01 = next(p for p in volcado["puntos"] if p["id"] == "B-01")
    vb2 = next(v for v in b01["verificaciones"] if v["codigo"] == "VB2")
    assert vb2["cumple"] is False
    assert b01["aporte_alivio"]["evaluada"] is True
    assert b01["aporte_alivio"]["capacidad"]["Q_admisible_m3s"] == \
        pytest.approx(cp["Q_adm"], rel=REL_ARITMETICA)
    html = M11.memoria_html(informe, proyecto="prueba T-9")
    assert "VB2" in html and "Capacidad admisible de la cuneta" in html


def test_h1_el_comparador_ve_el_aporte(tmp_path):
    from src import comparador
    datos = {"globales": {"luz_m": 2.75, "L_hidraulico_m": 150.0,
                          "S_cuneta": 0.01}}
    a = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    ca.establecer_valor_dinamico("revestimiento_cuneta",
                                 "terreno_arena_fina_o_limo")
    b = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    r = comparador.comparar(cli.informe_json(a), cli.informe_json(b))
    assert any(d.donde == "B-01" and d.campo.startswith("aporte_alivio")
               for d in r.diferencias)


# ===========================================================================
# H2 - un VB1 sin evaluar cuenta para el cierre
# ===========================================================================

def test_h2_un_tramo_sin_extremo_es_un_bloqueo_y_el_expediente_no_cierra(tmp_path):
    """El caso del auditor (A-01 + B-01, L 150, TW 0.3), con la decision C en «no»."""
    ca.establecer_valor_dinamico("obras_familia_a_extremo_de_cuneta", "no")
    ruta = _csv_con(tmp_path, solo=("A-01", "B-01"))
    datos = {"globales": {"luz_m": 2.75, "TW_m": 0.3, "L_hidraulico_m": 150.0}}
    informe = servicio.correr(ruta, _externos(tmp_path, datos), "perfil")
    b01 = _punto(informe, "B-01")
    bloqueo = next(b for b in b01.bloqueos
                   if b.etapa == servicio.ETAPA_TRAMO_ALIVIO)
    assert bloqueo.tipo is TipoDeBloqueo.DATO_FALTANTE
    assert bloqueo.campo == "inicio_tramo_cuneta_km"
    assert not bloqueo.diferido_por_alcance
    r = informe.resumen()
    assert not r.cerrado and r.bloqueadas >= 1


def test_h2_el_prevuelo_lee_la_progresiva_como_la_carga():
    from src.modulos import M0_carga as m0
    assert m0.km_de_progresiva("2+450", "B-01") == pytest.approx(2.45, rel=REL_FORMULA)
    assert m0.km_de_progresiva("0.380", "A-01") == pytest.approx(0.38, rel=REL_FORMULA)
    with pytest.raises(DatoInvalidoError):
        m0.km_de_progresiva("2+1450", "B-01")


def test_h2_el_prevuelo_estima_el_extremo_que_falta(tmp_path):
    ca.establecer_valor_dinamico("obras_familia_a_extremo_de_cuneta", "no")
    externos = _externos(tmp_path, {"globales": {"luz_m": 2.75}})
    estimado = anticipo.datos_faltantes_por_punto(CSV, externos, "perfil")
    entrada = next(e for e in estimado if e.id_punto == "B-01"
                   and e.dato == "inicio_tramo_cuneta_km")
    assert entrada.detiene and entrada.etapa == servicio.ETAPA_TRAMO_ALIVIO
    ca.quitar_valor_dinamico("obras_familia_a_extremo_de_cuneta")
    estimado = anticipo.datos_faltantes_por_punto(CSV, externos, "perfil")
    assert not [e for e in estimado if e.dato == "inicio_tramo_cuneta_km"]


def test_h2_un_maximo_desconocido_sin_exceder_el_normativo_tambien_cuenta(tmp_path):
    """
    B-02 en 2+600, sin longitud ni datos de cuneta: su Fase 10 no cierra, el
    tramo de 150 m no excede los 200 m y VB1 no se puede evaluar. Es un
    bloqueo de B-02 que espera `L_hidraulico_m`.
    """
    ruta = _csv_con(tmp_path, [("B-02", "2+600")])
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"L_hidraulico_m": 250.0}}}
    informe = servicio.correr(ruta, _externos(tmp_path, datos), "perfil")
    b02 = _punto(informe, "B-02")
    assert b02.tramo_alivio.verificacion is None
    assert any(b.etapa == servicio.ETAPA_TRAMO_ALIVIO
               and b.campo == "L_hidraulico_m" for b in b02.bloqueos)


# ===========================================================================
# H3 - los huecos que VB1 no mira, el inicio posterior, el sentido del flujo
# ===========================================================================

OBRAS = (("A-02", Familia.A, 1.92), ("B-01", Familia.B, 2.45),
         ("B-02", Familia.B, 2.90), ("C-01", Familia.C, 3.10))


def test_h3_el_hueco_entre_la_obra_anterior_y_el_inicio_declarado_se_avisa():
    e = M10.extremo_del_tramo(id_punto="B-02", progresiva_km=2.90,
                              inicio_declarado_km=2.80, obras=OBRAS)
    assert e.extremo == M10.EXTREMO_DECLARADO
    assert e.longitud_m == pytest.approx(100.0, rel=REL_ARITMETICA)
    hueco = next(a for a in e.avisos if "B-01" in a)
    assert "350.0 m" in hueco


def test_h3_un_inicio_posterior_a_la_obra_es_dato_invalido_que_nombra_el_par():
    with pytest.raises(DatoInvalidoError) as exc:
        M10.extremo_del_tramo(id_punto="B-02", progresiva_km=2.90,
                              inicio_declarado_km=3.00, obras=OBRAS)
    assert exc.value.campo == "inicio_tramo_cuneta_km / progresiva_km"


def test_h3_el_inicio_posterior_bloquea_el_punto_sin_tumbar_la_corrida(tmp_path):
    ruta = _csv_con(tmp_path, [("B-02", "2+900")])
    datos = {"globales": {"luz_m": 2.75, "L_hidraulico_m": 250.0},
             "puntos": {"B-02": {"inicio_tramo_cuneta_km": 3.0}}}
    informe = servicio.correr(ruta, _externos(tmp_path, datos), "perfil")
    b02 = _punto(informe, "B-02")
    bloqueo = next(b for b in b02.bloqueos
                   if b.etapa == servicio.ETAPA_TRAMO_ALIVIO)
    assert bloqueo.tipo is TipoDeBloqueo.DATO_INVALIDO
    assert b02.tramo_alivio is None


def test_h3_el_lado_de_progresivas_mayores_del_ultimo_alivio_se_avisa():
    e = M10.extremo_del_tramo(id_punto="B-02", progresiva_km=2.90,
                              inicio_declarado_km=None, obras=OBRAS)
    assert e.extremo == "B-01"
    assert any("progresivas mayores de B-02" in a for a in e.avisos)


def test_h3_entre_un_alivio_y_la_obra_A_siguiente_se_avisa():
    obras = (("B-01", Familia.B, 2.45), ("A-09", Familia.A, 2.60))
    e = M10.extremo_del_tramo(id_punto="B-01", progresiva_km=2.45,
                              inicio_declarado_km=None, obras=obras)
    assert any("150.0 m" in a and "A-09" in a for a in e.avisos)


def test_h3_entre_dos_alivios_no_hay_hueco_del_lado_mayor_del_primero():
    e = M10.extremo_del_tramo(id_punto="B-01", progresiva_km=2.45,
                              inicio_declarado_km=None, obras=OBRAS)
    assert not any("progresivas mayores" in a for a in e.avisos)


def test_h3_los_textos_de_M10_no_suponen_el_sentido_del_flujo():
    """
    Ninguna cadena de M10 que llegue al usuario --todas menos los docstrings--
    dice «aguas arriba» ni «aguas abajo» (por AST).
    """
    arbol = ast.parse((RAIZ / "src" / "modulos" / "M10_espaciamiento.py")
                      .read_text(encoding="utf-8"))
    docstrings = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.Module, ast.FunctionDef, ast.ClassDef)) \
                and nodo.body and isinstance(nodo.body[0], ast.Expr) \
                and isinstance(nodo.body[0].value, ast.Constant):
            docstrings.add(id(nodo.body[0].value))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str) \
                and id(nodo) not in docstrings:
            texto = nodo.value.lower()
            assert "aguas arriba" not in texto and "aguas abajo" not in texto, \
                nodo.value[:80]


# ===========================================================================
# H4 + D - el TR del aporte es el del punto; la fila es una envolvente
# ===========================================================================

def test_d_la_tabla_02_da_riesgo_y_la_envolvente_es_una_interpretacion():
    """
    T = 1 / (1 − (1 − R)^(1/n)), con n = 15 (nota (**) de la Tabla Nº 02):
      R 0.35: (0.65)^(1/15) = 0.971690 -> T = 1 / 0.028310 = 35.32 años
      R 0.40: (0.60)^(1/15) = 0.966518 -> T = 1 / 0.033482 = 29.87 años
    """
    reg = _registro.construir()
    t02 = reg.tabla("MC_HHD.T02")
    menor = next(f for f in t02.filas if f.id == "MC_HHD.T02#quebrada_menor")
    plataforma = next(f for f in t02.filas
                      if f.id == "MC_HHD.T02#drenaje_plataforma")
    assert menor.valores["riesgo"] == 35 and plataforma.valores["riesgo"] == 40
    for fila, T in ((menor, 35.32), (plataforma, 29.87)):
        R, n = fila.valores["riesgo"] / 100, fila.valores["vida_util_anios"]
        assert 1 / (1 - (1 - R) ** (1 / n)) == pytest.approx(T, rel=REL_ARITMETICA)
    c = reg.cita("MC_HHD.4.1.2a")
    assert c.interpretacion is not None and c.interpretacion.en_contra
    assert "ENVOLVENTE" in c.interpretacion.texto
    assert "conservador" not in c.nota


def test_h4_la_nota_del_aporte_imprime_el_TR_del_punto_con_el_riesgo_del_propietario(tmp_path):
    """R 0.20, n 15 del Propietario: T = 1 / (1 − 0.8^(1/15)) = 67.72 años."""
    ca.establecer_valor_dinamico("riesgo_admisible_propietario",
                                 {"quebrada_menor": {"R": 0.20, "n": 15}})
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"ancho_tributario_m": 12.0, "S_cuneta": 0.01}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    paso = next(p for p in _punto(informe, "B-01").espaciamiento.pasos
                if p.codigo == "10.3")
    assert "TR = 67.7 años" in paso.nota_del_proyecto
    assert "no conoce el periodo de retorno" in paso.nota_del_proyecto
    assert "TR = 35 años" not in paso.nota_del_proyecto


def test_h4_ningun_texto_de_M10_lleva_el_TR_cableado():
    arbol = ast.parse((RAIZ / "src" / "modulos" / "M10_espaciamiento.py")
                      .read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str):
            assert "TR = 35" not in nodo.value, nodo.value[:80]


# ===========================================================================
# H5 + A - la seccion de archivo, su ventana y el talud interior
# ===========================================================================

def test_a_la_seccion_es_el_minimo_muy_lluvioso_y_Z2_es_eleccion_declarada():
    c = ca.CRITERIOS["seccion_cuneta"]
    d, a = CN.CUNETA_DIMENSIONES_MINIMAS_T34["muy_lluviosa_1600_3000"]
    assert c.valor["profundidad_m"] == pytest.approx(d, rel=REL_TRANSPORTE)
    assert c.valor["ancho_m"] == pytest.approx(a, rel=REL_TRANSPORTE)
    assert c.valor["talud_exterior_HV"] == pytest.approx(1.0, rel=REL_TRANSPORTE)
    assert c.valor["borde_libre_m"] == pytest.approx(0.0, abs=ABS_CERO)
    for texto in ("ELECCION [A]", "3000", "TRAPEZOIDAL", "304.12", "FEN"):
        assert texto in c.justificacion, texto
    assert "seccion_cuneta" not in ca.criterios_de_perfil_sin_valor()


def test_a_la_sensibilidad_de_Z2_que_la_ficha_declara():
    """
    Concreto, S = 0.01, 0.40 x 1.20 (Z1 = 3):
      Z2 = 0.1: A = 3.1 · 0.16 / 2 = 0.248 ; P = 0.4 · (√10 + √1.01) = 1.66691
               Rh = 0.148779 ; Q = 67 · 0.248 · 0.280776 · 0.1 = 0.46654
      Z2 = 2.0: A = 0.40 ; P = 0.4 · (√10 + √5) = 2.15934 ; Rh = 0.185242
               Q = 67 · 0.40 · 0.324957 · 0.1 = 0.87089
    """
    for Z2, Q in ((0.1, 0.46654), (2.0, 0.87089)):
        ca.establecer_valor_dinamico("seccion_cuneta", {
            "profundidad_m": 0.40, "ancho_m": 1.20, "talud_exterior_HV": Z2,
            "borde_libre_m": 0.0})
        assert M10.capacidad_cuneta(S_cuneta=0.01).Q_admisible_m3s == \
            pytest.approx(Q, rel=REL_ARITMETICA)


def test_a_con_la_seccion_de_archivo_se_avisa_la_fila_1_4_de_la_tabla_304_12():
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    assert c.talud_interior_HV == pytest.approx(3.0, rel=REL_FORMULA)
    assert any("1:4" in a and "IMDA" in a for a in c.avisos)


@pytest.mark.parametrize("Z1,aviso", [(4.0, ""), (3.0, "1:4"),
                                       (2.5, "muy especiales")])
def test_a_el_aviso_de_talud_interior_por_fila_de_la_tabla_304_12(Z1, aviso):
    texto = M10.aviso_de_talud_interior(Z1)
    assert (texto == "") if not aviso else (aviso in texto)


def test_a_un_talud_interior_mas_empinado_que_1_2_es_dato_invalido(monkeypatch):
    _sustituir_seccion(monkeypatch, {"profundidad_m": 0.50, "ancho_m": 0.75,
                                     "talud_exterior_HV": 1.0,
                                     "borde_libre_m": 0.0})
    with pytest.raises(DatoInvalidoError) as exc:
        M10.capacidad_cuneta(S_cuneta=0.01)
    assert "304.12" in str(exc.value)


def test_a_la_cita_de_la_tabla_304_12_y_las_vistas_de_calculo():
    c = _registro.construir().cita("MC_HHD.4.1.2.1#T304_12")
    assert c.pagina_impresa == "173" and "Tabla Nº 304.12" in c.texto_literal.texto
    assert CN.CUNETA_Z1_MIN_T304_12 == pytest.approx(
        {"casos_muy_especiales": 2.0, "general": 3.0,
         "vd_mas_70_imda_mas_750": 4.0}, rel=REL_TRANSPORTE)


def test_a_el_ejemplo_de_declarar_seccion_cuneta_salio_de_la_guia():
    assert '--declarar "seccion_cuneta=' not in GUIA.read_text(encoding="utf-8")


# ===========================================================================
# B - la v8 ya no pide «con borde libre» sin cifra
# ===========================================================================

def test_b_el_punto_2_de_la_fase_10_no_pide_borde_libre():
    linea = next(l for l in V8.read_text(encoding="utf-8").splitlines()
                 if l.startswith("**2. Límite hidráulico"))
    assert "borde libre" not in linea
    assert "cuneta llena" in V8.read_text(encoding="utf-8")


def test_b_el_borde_libre_vale_0_y_su_ventana_es_0_a_0_10():
    c = ca.CRITERIOS["seccion_cuneta"]
    assert c.valor["borde_libre_m"] == pytest.approx(0.0, abs=ABS_CERO)
    assert c.sensibilidad["borde_libre_m"] == pytest.approx((0.0, 0.10),
                                                            rel=REL_TRANSPORTE)
    assert "adopcion" in c.justificacion


# ===========================================================================
# C - las obras de Familia A cierran el tramo por defecto
# ===========================================================================

def test_c_el_criterio_de_las_obras_A_es_si_y_no_es_barrible():
    c = ca.CRITERIOS["obras_familia_a_extremo_de_cuneta"]
    assert c.valor == "si" and c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert c.sensibilidad == ("si", "no")
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico("obras_familia_a_extremo_de_cuneta",
                                     "tal vez")


def test_c_la_cita_del_DG2018_lleva_la_lectura_como_interpretacion():
    reg = _registro.construir()
    c = reg.cita("DG2018.304.11#DESAGUE")
    assert "obras de drenaje transversal" in c.texto_literal.texto
    assert c.pagina_impresa == "208" and c.texto_literal.pagina_pdf == 209
    assert c.interpretacion is not None and len(c.interpretacion.en_contra) >= 2
    assert "alcantarillas de alivio" in reg.cita(
        "MC_HHD.4.1.2.1d#ALIVIO").texto_literal.texto


def test_c_en_el_fixture_B01_queda_a_530_m_de_A02_y_VB1_no_cumple(tmp_path):
    """
    La consecuencia que el auditor midio y que se DECLARA: la corrida
    estrecha de la linea base (luz 2.75, sin mas datos). La Fase 10 de B-01
    no cierra (sin longitud ni datos de la cuneta), el tramo de 530 m excede
    los 200 m del recorrido maximo y VB1 no cumple contra el normativo.
    """
    informe = servicio.correr(CSV, _externos(tmp_path, {"globales": {
        "luz_m": 2.75}}), "perfil")
    b01 = _punto(informe, "B-01")
    t = b01.tramo_alivio
    assert t.extremo == "A-02"
    assert t.longitud_m == pytest.approx(530.0, rel=REL_ARITMETICA)
    v = t.verificacion
    assert not v.cumple and v.valor_admisible == pytest.approx(200.0, rel=REL_TRANSPORTE)
    assert "DG2018.304.11#DESAGUE" in v.paso.citas_textuales
    assert any(e.clave_criterio == "obras_familia_a_extremo_de_cuneta"
               for e in v.paso.elecciones)
    assert "obras_familia_a_extremo_de_cuneta" in informe.contexto.criterios_usados


def test_c_con_no_la_obra_A_no_cierra_el_tramo():
    ca.establecer_valor_dinamico("obras_familia_a_extremo_de_cuneta", "no")
    e = M10.extremo_del_tramo(id_punto="B-01", progresiva_km=2.45,
                              inicio_declarado_km=None, obras=OBRAS)
    assert e.extremo is None


def test_c_el_inicio_declarado_gana_sobre_la_obra_A():
    e = M10.extremo_del_tramo(id_punto="B-01", progresiva_km=2.45,
                              inicio_declarado_km=2.35, obras=OBRAS)
    assert e.extremo == M10.EXTREMO_DECLARADO
    assert e.longitud_m == pytest.approx(100.0, rel=REL_ARITMETICA)
    # y el hueco entre A-02 (1.92) y el inicio (2.35) se avisa: 430 m.
    assert any("430.0 m" in a for a in e.avisos)


def test_c_una_obra_C_no_cierra_el_tramo():
    obras = (("C-01", Familia.C, 2.00), ("B-01", Familia.B, 2.45))
    e = M10.extremo_del_tramo(id_punto="B-01", progresiva_km=2.45,
                              inicio_declarado_km=None, obras=obras)
    assert e.extremo is None


# ===========================================================================
# Dudosos del auditor, resueltos
# ===========================================================================

def test_dudoso1_el_paso_dice_que_la_cuneta_es_la_del_tramo_y_no_la_del_cruce():
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    nota = c.pasos[0].nota_del_proyecto
    assert "LECTURA DEL PROYECTO" in nota and "terraplen" in nota
    assert "MC_HHD.4.1.2.1#UBICACION" in c.pasos[0].citas_textuales


def test_dudoso2_el_paso_declara_la_tabla_32_y_nombra_la_09():
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    eleccion = next(e for e in c.pasos[0].elecciones
                    if e.que_se_adopto == "tabla de la que sale el n de la cuneta")
    assert "Tabla Nº 32" in eleccion.valor
    assert any("Tabla Nº 09" in alt for alt in eleccion.entre)
    assert eleccion.cita_id == "MC_HHD.4.1.2.1#T09"


def test_dudoso3_la_nota_de_muy_corta_duracion_sale_del_registro_con_concreto():
    reg = _registro.construir()
    nota = next(n.texto.texto for n in reg.tabla("MC_HHD.T33").notas_al_pie
                if n.marca == "*")
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    assert f"«{nota}»" in c.pasos[0].nota_del_proyecto
    assert "conservadora" in c.pasos[0].nota_del_proyecto
    ca.establecer_valor_dinamico("revestimiento_cuneta", "terreno_hierba")
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    assert nota not in c.pasos[0].nota_del_proyecto


# ===========================================================================
# H6 - la justificacion del revestimiento dice lo que cuesta
# ===========================================================================

def test_h6_el_concreto_es_el_extremo_menos_conservador_y_la_ficha_lo_dice():
    j = ca.CRITERIOS["revestimiento_cuneta"].justificacion
    assert "MENOS conservadora" in j and "K = 67" in j
    assert "muy corta duracion" in j


# ===========================================================================
# H7 - los mutantes vivos de la auditoria
# ===========================================================================

def test_h7_caudal_a_velocidad_con_Z2_distinto_de_1():
    """
    CP_T9_CUNETA['velocidad_Z2'], a mano: v = 0.20, n = 1/33, S = 0.01,
    Z1 = 3, Z2 = 2 (mata Z2**2 -> Z2**3).
    """
    cp = CP_T9_CUNETA["velocidad_Z2"]
    y_v, Q_v = M10.caudal_a_velocidad(v=cp["v"], n=cp["n"], S=cp["S"],
                                      Z1=cp["Z1"], Z2=cp["Z2"])
    assert y_v == pytest.approx(cp["y_v"], rel=REL_ARITMETICA)
    assert Q_v == pytest.approx(cp["Q_v"], rel=REL_ARITMETICA)


def test_h7_el_criterio_de_VB1_con_el_hidraulico_calculado_es_la_seccion():
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    L = M10.longitud_hidraulica_por_tramo(capacidad=c, Q_aporte_m3s=2.0,
                                          origen_aporte="t",
                                          longitud_tramo_m=150.0,
                                          extremo="B-01")
    e = M10.espaciamiento_alivio(L.L_hidraulico, longitud_hidraulica=L)
    t = M10.verificar_tramo(id_punto="B-02", progresiva_km=2.60, extremo="B-01",
                            progresiva_extremo_km=2.45,
                            origen_extremo=M10.ORIGEN_EXTREMO_OBRA_B,
                            maximos=(("B-02", e),))
    assert e.gobierna.value == "hidraulico"
    assert t.verificacion.criterio_aplicado == "seccion_cuneta"


def test_h7_frontera_del_normativo_con_un_maximo_desconocido():
    """s = 200 m exactos (a la tolerancia) con un maximo desconocido: no se evalua."""
    t = M10.verificar_tramo(id_punto="B-02", progresiva_km=2.65, extremo="B-01",
                            progresiva_extremo_km=2.45,
                            origen_extremo=M10.ORIGEN_EXTREMO_OBRA_B,
                            maximos=(("B-02", None),))
    assert t.longitud_m == pytest.approx(200.0, rel=REL_ARITMETICA)
    assert t.verificacion is None and t.falta == "L_hidraulico_m"


def test_h7_la_progresiva_cero_se_acepta_en_verificar_tramo():
    e = M10.espaciamiento_alivio(250.0)
    t = M10.verificar_tramo(id_punto="B-01", progresiva_km=0.15,
                            extremo=M10.EXTREMO_DECLARADO,
                            progresiva_extremo_km=0.0,
                            origen_extremo=M10.ORIGEN_EXTREMO_DECLARADO,
                            maximos=(("B-01", e),))
    assert t.verificacion.cumple
    assert t.longitud_m == pytest.approx(150.0, rel=REL_ARITMETICA)


def test_h7_un_Q_declarado_con_cuenca_presente_no_se_recalcula(tmp_path,
                                                                monkeypatch):
    """Con la celda Q_m3s LLENA y su cuenca en la corrida, gana el declarado."""
    from src.modulos import MH_hidrologia as MH

    def _prohibido(*_a, **_k):
        raise AssertionError("un Q declarado no se recalcula")
    monkeypatch.setattr(MH, "caudal_de_aporte_cuneta", _prohibido)
    monkeypatch.setattr(MH, "caudal_de_diseno", _prohibido)
    hidrologia = servicio.cargar_hidrologia(HIDRO / "cuencas_prueba.csv",
                                            HIDRO / "estacion_prueba.csv")
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"S_cuneta": 0.01}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil",
                              hidrologia=hidrologia)
    b01 = _punto(informe, "B-01")
    assert b01.aporte_alivio.Q_aporte_m3s == pytest.approx(0.095, rel=REL_FORMULA)
    assert b01.espaciamiento.longitud_hidraulica.caudal_de_aporte is None


# ===========================================================================
# H8 - M10 consume su caso patron
# ===========================================================================

def test_h8_M10_salio_de_la_exencion_de_caso_patron():
    from tests import test_guardias_de_la_suite as g
    assert "M10_espaciamiento" not in g.SIN_CASO_PATRON
    assert {"auditor", "arena_fina", "velocidad_Z2", "archivo"} <= set(CP_T9_CUNETA)


# ===========================================================================
# H9 - area_ha la exigen A y B
# ===========================================================================

def test_h9_area_ha_la_exigen_las_familias_A_y_B():
    assert servicio.FAMILIAS_QUE_EXIGEN_COLUMNA["area_ha"] == (Familia.A,
                                                               Familia.B)


# ===========================================================================
# H10 - las lecturas del proyecto, como Interpretacion
# ===========================================================================

def test_h10_la_union_de_las_tablas_32_y_33_es_interpretacion_y_el_paso_la_lee():
    reg = _registro.construir()
    interp = reg.cita("MC_HHD.4.1.2.1#T33").interpretacion
    assert interp is not None and interp.en_contra
    ca.establecer_valor_dinamico("revestimiento_cuneta", "terreno_hierba")
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    assert interp.texto in c.pasos[0].nota_del_proyecto


def test_h10_F10_TRAMO_separa_lo_que_la_fuente_exige_de_lo_que_el_proyecto_adopta():
    f = _registro.construir().fundamento("F10.TRAMO")
    assert "lo que el Manual admite" not in f.por_que
    assert "EXIGE" in f.por_que and "RECOMIENDA" in f.por_que
    assert "adopta" in f.por_que


# ===========================================================================
# H11 - el aporte calculado no se recalcula ni repite pasos
# ===========================================================================

def test_h11_la_fase_1_bis_calcula_el_aporte_de_la_cuneta_una_vez(tmp_path,
                                                                  monkeypatch):
    from src.modulos import MH_hidrologia as MH
    llamadas = []
    original = MH.caudal_de_aporte_cuneta

    def _contado(*a, **k):
        llamadas.append(a[0].id)
        return original(*a, **k)
    monkeypatch.setattr(MH, "caudal_de_aporte_cuneta", _contado)
    ruta = _csv_con(tmp_path, cambios={"B-01": {"Q_m3s": ""}})
    hidrologia = servicio.cargar_hidrologia(HIDRO / "cuencas_prueba.csv",
                                            HIDRO / "estacion_prueba.csv")
    ca.establecer_valor_dinamico("homogeneidad_serie_fen", "serie_completa")
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"ancho_tributario_m": 12.0, "S_cuneta": 0.01}}}
    informe = servicio.correr(ruta, _externos(tmp_path, datos), "perfil",
                              hidrologia=hidrologia)
    assert llamadas == ["B-01"]
    b01 = _punto(informe, "B-01")
    aporte = next(p for p in b01.espaciamiento.pasos if p.codigo == "10.3")
    assert "el del punto" in aporte.nota_del_proyecto
    pasos_10 = M11.traza_espaciamiento(b01)
    assert not any(p.fundamento_id.startswith("FH.") for p in pasos_10)
    assert b01.espaciamiento.longitud_hidraulica.caudal_de_aporte is b01.caudal


# ===========================================================================
# Las citas nuevas, contra su pagina
# ===========================================================================

CITAS_DE_LAS_CORRECCIONES = ("MC_HHD.4.1.2.1a#CONDICION", "MC_HHD.4.1.2.1#T09",
                             "MC_HHD.4.1.2.1#T304_12",
                             "MC_HHD.4.1.2.1#UBICACION",
                             "MC_HHD.4.1.2.1d#ALIVIO", "DG2018.304.11#DESAGUE")


@pytest.mark.parametrize("cita_id", CITAS_DE_LAS_CORRECCIONES)
def test_las_citas_de_las_correcciones_estan_firmadas(cita_id):
    c = _registro.construir().cita(cita_id)
    assert c.verificado is not None
    assert c.verificado.por.startswith("tesis/T-9 (correcciones)")


@pytest.mark.pdf
def test_cada_cita_de_las_correcciones_dice_lo_que_su_pagina_dice():
    from src.normativa import fuentes as F
    from src.normativa.extraccion import aparece_en_pagina, pymupdf_disponible
    if not pymupdf_disponible():
        pytest.skip("sin PyMuPDF")
    reg = _registro.construir()
    for cita_id in CITAS_DE_LAS_CORRECCIONES + ("MC_HHD.4.1.2a",
                                                "MC_HHD.4.1.2.1#T33"):
        c = reg.cita(cita_id)
        ruta = F.ruta_pdf(getattr(F, c.fuente_id))
        if not ruta.exists():
            pytest.skip(f"sin el PDF de {c.fuente_id}")
        assert aparece_en_pagina(ruta, c.texto_literal.pagina_pdf,
                                 c.texto_literal.texto), cita_id
        assert aparece_en_pagina(ruta, c.pagina_del_titulo,
                                 c.titulo_numeral), cita_id


@pytest.mark.pdf
def test_la_tabla_02_y_la_304_12_estan_en_su_pagina():
    """Los riesgos 35 y 40 (PDF 28) y las cuatro inclinaciones (PDF 176)."""
    from src.normativa import fuentes as F
    from src.normativa.extraccion import pymupdf_disponible, texto_de_pagina
    if not pymupdf_disponible():
        pytest.skip("sin PyMuPDF")
    ruta = F.ruta_pdf(F.MC_HHD)
    if not ruta.exists():
        pytest.skip("sin el PDF del Manual de Hidrologia")
    p28 = " ".join(texto_de_pagina(ruta, 28).split())
    assert "descarga de agua de cunetas 35" in p28
    assert "Drenaje de la plataforma (a nivel longitudinal) 40" in p28
    assert "Drenaje de plataforma y Sub-drenes n= 15 años" in p28
    p176 = " ".join(texto_de_pagina(ruta, 176).split())
    for celda in ("1:02", "1:03", "1:04", "Sólo en casos muy especiales",
                  "INCLINACIONES MÁXIMAS DEL TALUD (V:H)"):
        assert celda in p176, celda


# ===========================================================================
# La mutacion de la integracion: los vivos que importaban, cerrados
# ===========================================================================
# El arnes de EXT-11 (`tests/apoyo/mutacion.py`) sobre una copia del arbol
# fusionado, con estos dos archivos y `test_M10_espaciamiento.py` de
# objetivos: en M10, 240 de 288 mutantes muertos (83.3 %); en las seis
# funciones de la Fase 10 de `servicio`, 66 de 78 (84.6 %). Los tests de
# abajo matan los vivos que cambian una conducta o un texto que el lector
# usa; el resto queda censado con su razon en la ficha T9-10.

@pytest.mark.parametrize("S,lado", [(0.003, "autolimpieza"),
                                    (0.005, "autolimpieza"),
                                    (0.03, "erosivas")])
def test_mut_el_aviso_de_pendiente_dice_el_lado_de_la_banda(S, lado):
    assert lado in M10.aviso_de_pendiente(S)


def test_mut_las_fronteras_de_la_tabla_304_12_son_las_de_la_tabla():
    assert M10.aviso_de_talud_interior(4.0) == ""
    tres = M10.aviso_de_talud_interior(3.0)
    assert "1:4" in tres and "muy especiales" not in tres
    assert "muy especiales" in M10.aviso_de_talud_interior(2.0)


def test_mut_las_notas_de_la_capacidad_siguen_a_lo_declarado(monkeypatch):
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    nota = c.pasos[0].nota_del_proyecto
    assert "Borde libre de" not in nota
    assert M10.aviso_de_talud_interior(3.0) in nota
    otro = next(e for e in c.pasos[0].elecciones
                if e.que_se_adopto == "extremo de la fila de la Tabla Nº 33")
    assert "el otro extremo, 6.00 m/s" in otro.entre[1]
    _sustituir_seccion(monkeypatch, {"profundidad_m": 0.40, "ancho_m": 1.20,
                                     "talud_exterior_HV": 1.0,
                                     "borde_libre_m": 0.05})
    assert "Borde libre de 0.05 m" in \
        M10.capacidad_cuneta(S_cuneta=0.01).pasos[0].nota_del_proyecto


def test_mut_VB2_cumple_con_el_aporte_igual_a_la_capacidad():
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    v = M10.verificar_aporte(capacidad=c, Q_aporte_m3s=c.Q_admisible_m3s,
                             origen_aporte="t").verificacion
    assert v.cumple


def test_mut_el_espaciamiento_admite_menos_de_un_metro_y_su_margen():
    assert M10.espaciamiento_alivio(0.5).espaciamiento_max == pytest.approx(
        0.5, rel=REL_TRANSPORTE)
    assert M10.espaciamiento_alivio(120.0).paso.veredicto.margen == \
        pytest.approx(80.0, rel=REL_TRANSPORTE)
    assert M10.espaciamiento_alivio(250.0).paso.veredicto.margen == \
        pytest.approx(0.0, abs=ABS_CERO)


def test_mut_el_extremo_del_tramo_en_sus_fronteras():
    # el inicio en la misma progresiva de la obra: un tramo nulo, admitido
    e = M10.extremo_del_tramo(id_punto="B-01", progresiva_km=2.45,
                              inicio_declarado_km=2.45, obras=OBRAS)
    assert e.longitud_m == pytest.approx(0.0, abs=ABS_CERO)
    # sin obra anterior y con inicio declarado: ni error ni hueco
    e = M10.extremo_del_tramo(id_punto="B-01", progresiva_km=2.45,
                              inicio_declarado_km=2.30,
                              obras=(("B-01", Familia.B, 2.45),))
    assert e.extremo == M10.EXTREMO_DECLARADO
    assert not any("quedan" in a for a in e.avisos)
    # el inicio en la obra anterior: no hay hueco entre las dos
    e = M10.extremo_del_tramo(id_punto="B-01", progresiva_km=2.45,
                              inicio_declarado_km=1.92, obras=OBRAS)
    assert not any("quedan" in a for a in e.avisos)


def test_mut_la_obra_anterior_y_la_siguiente_no_se_confunden():
    obras = (("A-02", Familia.A, 1.92), ("B-01", Familia.B, 2.45),
             ("A-09", Familia.A, 2.53))
    e = M10.extremo_del_tramo(id_punto="B-01", progresiva_km=2.45,
                              inicio_declarado_km=None, obras=obras)
    assert e.extremo == "A-02" and e.familia_extremo is Familia.A
    assert e.origen_extremo == M10.ORIGEN_EXTREMO_OBRA_A
    (hueco,) = e.avisos
    assert "A-09" in hueco and "80.0 m" in hueco and "A-02" not in hueco
    e = M10.extremo_del_tramo(id_punto="B-02", progresiva_km=2.90,
                              inicio_declarado_km=None, obras=OBRAS)
    assert e.origen_extremo == M10.ORIGEN_EXTREMO_OBRA_B
    # entre una obra A y un alivio B: ningun hueco del lado mayor de B-01
    e = M10.extremo_del_tramo(id_punto="B-01", progresiva_km=2.45,
                              inicio_declarado_km=None, obras=OBRAS)
    assert e.avisos == ()


def test_mut_VB1_sin_la_progresiva_del_extremo_no_se_evalua():
    t = M10.verificar_tramo(id_punto="B-01", progresiva_km=2.45,
                            extremo="A-02", progresiva_extremo_km=None,
                            origen_extremo="t", maximos=())
    assert t.verificacion is None and t.falta == "inicio_tramo_cuneta_km"


def test_mut_con_un_solo_maximo_la_nota_no_habla_de_dos_alivios():
    e = M10.espaciamiento_alivio(250.0)
    t = M10.verificar_tramo(id_punto="B-02", progresiva_km=2.60,
                            extremo=M10.EXTREMO_DECLARADO,
                            progresiva_extremo_km=2.45,
                            origen_extremo=M10.ORIGEN_EXTREMO_DECLARADO,
                            maximos=(("B-02", e),))
    assert "MENOR" not in t.verificacion.paso.nota_del_proyecto


def test_mut_las_claves_de_la_cuneta_que_hacen_falta():
    ambas = ("ancho_tributario_m", "S_cuneta")
    assert servicio.claves_de_la_cuneta_necesarias(True, False) == ("S_cuneta",)
    assert servicio.claves_de_la_cuneta_necesarias(False, False) == ambas
    assert servicio.claves_de_la_cuneta_necesarias(True, True) == ambas


def test_mut_sin_caudal_la_fase_10_se_detiene_sin_caer(tmp_path):
    """Q por calcular y el criterio FEN sin declarar: la Fase 1-bis no da caudal."""
    ruta = _csv_con(tmp_path, cambios={"B-01": {"Q_m3s": ""}})
    hidrologia = servicio.cargar_hidrologia(HIDRO / "cuencas_prueba.csv",
                                            HIDRO / "estacion_prueba.csv")
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"ancho_tributario_m": 12.0, "S_cuneta": 0.01}}}
    informe = servicio.correr(ruta, _externos(tmp_path, datos), "perfil",
                              hidrologia=hidrologia)
    b01 = _punto(informe, "B-01")
    assert b01.caudal is None and b01.aporte_alivio is None
    assert any(b.campo == "L_hidraulico_m" and "caudal de aporte" in b.mensaje
               for b in b01.bloqueos)


@pytest.mark.parametrize("inicio,metodo", [(2.45, "area"), (2.4495, "tramo")])
def test_mut_un_tramo_nulo_reparte_por_area_y_uno_de_medio_metro_por_tramo(
        tmp_path, inicio, metodo):
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"ancho_tributario_m": 12.0, "S_cuneta": 0.01,
                                 "inicio_tramo_cuneta_km": inicio}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    lh = _punto(informe, "B-01").espaciamiento.longitud_hidraulica
    esperado = {"area": "escorrentia especifica", "tramo": "caudal del alivio"}
    assert lh.metodo_aporte.startswith(esperado[metodo])


def test_mut_con_el_caudal_calculado_el_tramo_no_exime_del_ancho(tmp_path):
    ruta = _csv_con(tmp_path, cambios={"B-01": {"Q_m3s": ""}})
    hidrologia = servicio.cargar_hidrologia(HIDRO / "cuencas_prueba.csv",
                                            HIDRO / "estacion_prueba.csv")
    ca.establecer_valor_dinamico("homogeneidad_serie_fen", "serie_completa")
    datos = {"globales": {"luz_m": 2.75}, "puntos": {"B-01": {"S_cuneta": 0.01}}}
    informe = servicio.correr(ruta, _externos(tmp_path, datos), "perfil",
                              hidrologia=hidrologia)
    b01 = _punto(informe, "B-01")
    bloqueo = next(b for b in b01.bloqueos if b.campo == "L_hidraulico_m")
    assert "ancho_tributario_m" in bloqueo.mensaje


def test_mut_sin_luz_la_longitud_se_calcula_y_dice_que_no_hay_TR(tmp_path):
    """Sin la Fase 2 no hay TR ni tramo: q · b, y el paso lo dice sin caer."""
    datos = {"puntos": {"B-01": {"ancho_tributario_m": 12.0, "S_cuneta": 0.01}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    b01 = _punto(informe, "B-01")
    assert b01.clasificacion is None and b01.tramo_alivio is None
    paso = next(p for p in b01.espaciamiento.pasos if p.codigo == "10.3")
    assert "no asigno periodo de retorno" in paso.nota_del_proyecto


def test_mut_entre_dos_alivios_rige_el_maximo_menor_en_la_corrida(tmp_path):
    ruta = _csv_con(tmp_path, [("B-02", "2+600")])
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"L_hidraulico_m": 120.0},
                        "B-02": {"L_hidraulico_m": 250.0}}}
    informe = servicio.correr(ruta, _externos(tmp_path, datos), "perfil")
    v = _punto(informe, "B-02").tramo_alivio.verificacion
    assert v.valor_admisible == pytest.approx(120.0, rel=REL_TRANSPORTE)
    assert not v.cumple


def test_mut_un_VB1_evaluado_no_deja_bloqueo_de_su_etapa(tmp_path):
    informe = servicio.correr(CSV, _externos(tmp_path, {"globales": {
        "luz_m": 2.75}}), "perfil")
    b01 = _punto(informe, "B-01")
    assert b01.tramo_alivio.verificacion is not None
    assert not any(b.etapa == servicio.ETAPA_TRAMO_ALIVIO for b in b01.bloqueos)


def test_mut_la_segunda_linea_rechaza_un_revestimiento_que_burla_la_puerta(monkeypatch):
    original = ca.valor
    monkeypatch.setattr(ca, "valor", lambda clave: (
        "adoquin" if clave == "revestimiento_cuneta" else original(clave)))
    with pytest.raises(DatoInvalidoError) as exc:
        M10.capacidad_cuneta(S_cuneta=0.01)
    assert "los revestimientos admitidos son concreto" in str(exc.value)


def test_mut_con_una_obra_A_de_extremo_rige_solo_el_maximo_del_alivio(tmp_path):
    """
    La obra A no tiene Fase 10 ni espaciamiento maximo: no entra a los
    maximos de VB1. Con `L_hidraulico_m` = 120 m, el admisible es 120 m y no
    el normativo de 200 m que daria un maximo «desconocido» de A-02.
    """
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"L_hidraulico_m": 120.0}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    v = _punto(informe, "B-01").tramo_alivio.verificacion
    assert v.valor_admisible == pytest.approx(120.0, rel=REL_TRANSPORTE)
