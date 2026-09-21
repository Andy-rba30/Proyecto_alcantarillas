# -*- coding: utf-8 -*-
"""
tests/test_pf2_prevuelo.py
==========================
La aceptacion de PF-2 (`docs/planes_mejora/08_CADENA_PROMPTS_PERFIL.md`): el
cuarto bloque del anticipo, `anticipo.datos_faltantes_por_punto`, que dice
ANTES de correr que datos le faltan a cada punto --- columnas obligatorias
vacias, columnas admitidas vacias que una etapa de este alcance exige, y
claves externas de `servicio.CLAVES_EXTERNAS` sin declarar ---, de donde
tendria que venir cada uno, y si detiene una etapa o espera a un tablero.

Evidencia que lo abrio: la corrida de perfil de la revision de E-B necesito
cuatro corridas para dimensionar C-01 porque cada bloqueo aparecio despues
del anterior (luz_m, los siete del cajon, cota_coronacion_canal, S_conducto).

SIGUE SIENDO UNA ESTIMACION (`AVISO_DEL_ANTICIPO`): no gobierna ningun
filtro ni el boton de ejecutar. Lo que la vuelve honesta es el test de la
UNION de abajo: todo `DatoFaltanteError` que la corrida real produce sobre
una columna o una clave externa esta en lo que el pre-vuelo estimo para ese
punto, y lo que estima de mas queda censado con su razon.

Escritos primero EN ROJO con `xfail(strict=True)` por test sobre el
invariante, nunca sobre la salida actual; medidos antes de tocar codigo y
liberados al corregir.
"""

from __future__ import annotations

import ast
import csv
import inspect
import subprocess
import sys
from pathlib import Path

import pytest

import cli
from src import anticipo as antc
from src import servicio
from src.modelos import Familia, TipoDeBloqueo

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
AMPLIADAS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"
ROJO = pytest.mark.xfail(strict=True, reason="PF-2 todavia no ejecutado")

LUZ_DEL_CASO = 2.75          # m: la de la linea base, separa alcantarilla de puente
TW_DEL_CASO = 0.30           # m: el TW global de entradas_ampliadas.json


def _externos(ruta=None, **banderas):
    base = dict(luz_m=None, TW_m=None, longitud_m=None, L_hidraulico_m=None,
                categoria_tr=None)
    base.update(banderas)
    return cli.cargar_datos_externos(ruta, base)


def _por_punto(estimado):
    """{id_punto: {dato: entrada}} de lo que DETIENE, y aparte lo que espera."""
    detiene, espera = {}, {}
    for e in estimado:
        (detiene if e.detiene else espera).setdefault(e.id_punto, {})[e.dato] = e
    return detiene, espera


# ===========================================================================
# 1 - Lo que el CSV de ejemplo necesita, punto a punto
# ===========================================================================

def test_pf2_sin_json_el_prevuelo_nombra_la_luz_en_los_cuatro_y_lo_de_cada_familia():
    estimado = antc.datos_faltantes_por_punto(CSV_EJEMPLO, _externos(), cli.ALCANCE_PERFIL)
    detiene, espera = _por_punto(estimado)
    assert set(detiene) == {"A-01", "A-02", "B-01", "C-01"}
    for id_punto in detiene:
        assert "luz_m" in detiene[id_punto], id_punto
    # Lo que solo la Familia C exige (VC1), y lo que solo la B (Fase 10).
    assert "cota_coronacion_canal" in detiene["C-01"]
    assert all("cota_coronacion_canal" not in detiene[p] for p in ("A-01", "A-02", "B-01"))
    assert "L_hidraulico_m" in detiene["B-01"]
    assert all("L_hidraulico_m" not in detiene[p] for p in ("A-01", "A-02", "C-01"))
    # El caudal y la pendiente del cruce de canal, que van vacios por tablero
    # y que el diseño exige; la via alterna de la pendiente (S_conducto por
    # --datos-externos) va dicha en la misma entrada, no como falta aparte,
    # porque el codigo nunca la exige por su nombre (cae a S_cauce).
    for dato in ("Q_m3s", "S_cauce"):
        assert dato in detiene["C-01"], dato
    assert "S_conducto" in detiene["C-01"]["S_cauce"].de_donde
    # Cada entrada dice de donde viene el dato y en que etapa detiene.
    luz = detiene["A-01"]["luz_m"]
    assert luz.de_donde and luz.etapa
    assert luz.familia is Familia.A


def test_pf2_con_el_json_ampliado_y_la_luz_solo_queda_la_coronacion_del_canal():
    estimado = antc.datos_faltantes_por_punto(
        CSV_EJEMPLO, _externos(AMPLIADAS, luz_m=LUZ_DEL_CASO), cli.ALCANCE_PERFIL)
    detiene, espera = _por_punto(estimado)
    assert "C-01" in detiene and set(detiene["C-01"]) == {"cota_coronacion_canal"}
    for p in ("A-01", "A-02"):
        assert p not in detiene, detiene.get(p)
    assert set(detiene.get("B-01", {})) == {"L_hidraulico_m"}


def test_pf2_lo_que_espera_a_un_tablero_no_se_confunde_con_lo_que_detiene():
    """
    `NF_profundidad_m` va vacia en dos filas y la admite el estudio
    geotecnico: a perfil ningun modulo de calculo la consume, de modo que
    ESPERA y no detiene. `cota_fondo_entrada` tiene regla declarada y no
    espera a nadie: no aparece.
    """
    estimado = antc.datos_faltantes_por_punto(
        CSV_EJEMPLO, _externos(AMPLIADAS, luz_m=LUZ_DEL_CASO), cli.ALCANCE_PERFIL)
    detiene, espera = _por_punto(estimado)
    nf = [e for e in estimado if e.dato == "NF_profundidad_m"]
    assert nf and all(not e.detiene for e in nf)
    assert "geotecnico" in nf[0].de_donde
    assert not [e for e in estimado if e.dato == "cota_fondo_entrada"]


def test_pf2_el_tw_sin_ninguna_via_cae_en_el_criterio_y_el_prevuelo_lo_dice(monkeypatch):
    """
    A-01 no trae cota_TW ni Q_receptor y no hay TW declarado. Con
    'seccion_receptor' declarado en el archivo, `_resolver_tw` recorre las
    vias de Sec. 1.3 y NO cae en el criterio: el pre-vuelo tampoco lo dice
    (es el MISMO predicado, `servicio.tw_sin_via_de_sec_1_3`). Sin la seccion
    del receptor, el TW cae en la ultima puerta, 'TW_receptor', que es un
    CriterioPendienteError y no un DatoFaltanteError: el pre-vuelo lo dice
    sin detener.
    """
    estimado = antc.datos_faltantes_por_punto(
        CSV_EJEMPLO, _externos(luz_m=LUZ_DEL_CASO), cli.ALCANCE_PERFIL)
    assert not [e for e in estimado if e.id_punto == "A-01" and e.dato == "TW_m"]
    monkeypatch.setattr(servicio.ca, "valor_si_declarado",
                        lambda clave: None if clave == servicio.CRITERIO_SECCION_RECEPTOR
                        else servicio.ca.CRITERIOS[clave].valor)
    estimado = antc.datos_faltantes_por_punto(
        CSV_EJEMPLO, _externos(luz_m=LUZ_DEL_CASO), cli.ALCANCE_PERFIL)
    tw = [e for e in estimado if e.id_punto == "A-01" and e.dato == "TW_m"]
    assert tw and not tw[0].detiene and "TW_receptor" in tw[0].de_donde
    con_tw = antc.datos_faltantes_por_punto(
        CSV_EJEMPLO, _externos(luz_m=LUZ_DEL_CASO, TW_m=TW_DEL_CASO), cli.ALCANCE_PERFIL)
    assert not [e for e in con_tw if e.dato == "TW_m"]


# ===========================================================================
# 2 - La union: nada real escapa a la estimacion, y lo de mas queda censado
# ===========================================================================

def _faltas_reales(externos):
    informe = cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)
    reales = {}
    for punto in informe.puntos:
        for b in punto.bloqueos:
            if b.tipo is TipoDeBloqueo.DATO_FALTANTE and b.campo in (
                    tuple(servicio.CLAVES_EXTERNAS) + tuple(antc.m0.COLUMNAS)):
                reales.setdefault(punto.punto.id, set()).add(b.campo)
    return reales


# Lo que el pre-vuelo estima de MAS respecto de cada corrida real, MEDIDO y
# con la razon: la corrida se detiene en la primera falta de cada punto
# (`servicio._etapa` registra UN bloqueo por etapa) y las siguientes no
# llegan a producirse. Sin luz, C-01 no pasa de la Fase 2; con luz y TW, M1
# se detiene en Q_m3s antes de que MD pida S_cauce y VC1 la coronacion; con
# el JSON ampliado, MD se detiene en los criterios del cajon (bloque 1)
# antes de que VC1 llegue a exigir cota_coronacion_canal --- que es la capa
# que la revision de E-B midio al declarar los siete ---. Es la clase de
# falso positivo que una estimacion honesta declara, no esconde: cada
# entrada de mas es una falta REAL que la corrida sentiria despues.
SOBRA_SIN_LUZ = {"C-01": {"Q_m3s", "S_cauce", "cota_coronacion_canal"}}
SOBRA_CON_LUZ = {"C-01": {"S_cauce", "cota_coronacion_canal"}}
SOBRA_CON_TODO = {"C-01": {"cota_coronacion_canal"}}


@pytest.mark.parametrize("externos, sobra", [
    (_externos(), SOBRA_SIN_LUZ),
    (_externos(luz_m=LUZ_DEL_CASO, TW_m=TW_DEL_CASO), SOBRA_CON_LUZ),
    (_externos(AMPLIADAS, luz_m=LUZ_DEL_CASO), SOBRA_CON_TODO),
], ids=["sin_luz", "con_luz_y_tw", "con_todo"])
def test_pf2_todo_dato_faltante_real_estaba_en_el_prevuelo(externos, sobra):
    estimado = antc.datos_faltantes_por_punto(CSV_EJEMPLO, externos, cli.ALCANCE_PERFIL)
    detiene, _ = _por_punto(estimado)
    reales = _faltas_reales(externos)
    for id_punto, campos in reales.items():
        assert campos <= set(detiene.get(id_punto, {})), (id_punto, campos, detiene.get(id_punto))
    de_mas = {p: set(d) - reales.get(p, set()) for p, d in detiene.items()}
    de_mas = {p: s for p, s in de_mas.items() if s}
    assert de_mas == sobra


# ===========================================================================
# 3 - Guardias: no corre el pipeline, y la CLI lo expone
# ===========================================================================

def _llamadas(fn):
    arbol = ast.parse(inspect.getsource(fn))
    return {ast.unparse(n.func) for n in ast.walk(arbol) if isinstance(n, ast.Call)}


def test_pf2_el_prevuelo_no_ejecuta_el_pipeline():
    for fn in (antc.datos_faltantes_por_punto, cli._prevuelo):
        llamadas = _llamadas(fn)
        for prohibida in llamadas:
            assert not prohibida.endswith(("correr", "correr_punto", "disenar_punto",
                                           "cargar_puntos")), (fn.__name__, prohibida)


def test_pf2_la_cli_imprime_el_prevuelo_y_sale_sin_correr(tmp_path):
    hecho = subprocess.run(
        [sys.executable, str(RAIZ / "cli.py"), str(CSV_EJEMPLO), "--prevuelo",
         "--alcance", "perfil", "--json", str(tmp_path / "no.json")],
        capture_output=True, text=True, cwd=RAIZ)
    assert hecho.returncode == 1, hecho.stderr
    assert "luz_m" in hecho.stdout and "cota_coronacion_canal" in hecho.stdout
    assert antc.AVISO_DEL_ANTICIPO.split(".")[0] in hecho.stdout
    assert not (tmp_path / "no.json").exists()
    # Un punto de Familia A con luz y TW: nada detiene, y la CLI lo dice con 0.
    filas = list(csv.DictReader(CSV_EJEMPLO.open(encoding="utf-8")))
    fila = next(f for f in filas if f["id"] == "A-02")
    ruta = tmp_path / "a02.csv"
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fila))
        w.writeheader()
        w.writerow(fila)
    hecho = subprocess.run(
        [sys.executable, str(RAIZ / "cli.py"), str(ruta), "--prevuelo",
         "--luz", str(LUZ_DEL_CASO), "--tw", str(TW_DEL_CASO)],
        capture_output=True, text=True, cwd=RAIZ)
    assert hecho.returncode == 0, hecho.stdout + hecho.stderr


def test_pf2_las_lineas_del_bloque_4_las_produce_src_y_nombran_cada_dato():
    estimado = antc.datos_faltantes_por_punto(CSV_EJEMPLO, _externos(), cli.ALCANCE_PERFIL)
    lineas = antc.lineas_del_prevuelo(estimado)
    texto = "\n".join(lineas)
    for dato in ("luz_m", "cota_coronacion_canal", "L_hidraulico_m", "S_conducto"):
        assert dato in texto
    assert "C-01" in texto and "A-01" in texto
    assert antc.lineas_del_prevuelo(()) and "nada" in antc.lineas_del_prevuelo(())[0].lower()
