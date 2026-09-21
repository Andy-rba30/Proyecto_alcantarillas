# -*- coding: utf-8 -*-
"""
tests/test_pf3_barrido.py
=========================
La aceptacion de PF-3 (`docs/planes_mejora/08_CADENA_PROMPTS_PERFIL.md`): el
barrido de sensibilidad de un criterio [A] sobre su ventana, `src/barrido.py`,
que corre el pipeline una vez por valor, compara cada volcado con el del
primer valor por el comparador de E-B y arma una tabla por punto. Es lo que
una tesis tiene que mostrar de cada [A] de perfil: que pasa con el diametro,
el HW y las verificaciones cuando el criterio recorre su ventana.

Tres cosas que el barrido NO hace, y que estos tests fijan: no adopta un
valor fuera de la ventana (la misma puerta que una declaracion, antes de la
primera corrida), no deja al proceso con un estado distinto del que tenia
(cada corrida parte del estado de entrada, y al salir se repone), y no
recalcula nada por su cuenta (la aritmetica es la del pipeline y la
comparacion la del comparador; `src/barrido.py` no importa `src.modulos`).

Escritos primero EN ROJO con `xfail(strict=True)` por test sobre el
invariante, nunca sobre la salida actual; medidos antes de tocar codigo y
liberados al corregir.
"""

from __future__ import annotations

import ast
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import declaracion as dec
from src import editores as sed
from src import servicio
from tests.apoyo.aproximacion import REL_TRANSPORTE

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
# Los siete se escribieron en rojo con `xfail(strict=True)` (medidos 7 xfailed y
# 0 XPASS antes de tocar codigo) y se liberaron al corregir.

CLAVE = "ke_entrada"                 # float de_tabla, ventana (0.2, 0.9)
VALORES = (0.3, 0.5, 0.7)            # dentro de la ventana, en orden creciente
FUERA = 1.5                          # fuera de la ventana
NOTA = "barrido de sensibilidad de la tesis"
LUZ, TW = 2.75, 0.30


def _csv_a01(tmp_path):
    filas = list(csv.DictReader(CSV_EJEMPLO.open(encoding="utf-8")))
    fila = next(f for f in filas if f["id"] == "A-01")
    ruta = tmp_path / "a01.csv"
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fila))
        w.writeheader()
        w.writerow(fila)
    return ruta


def _externos():
    return cli.cargar_datos_externos(None, dict(luz_m=LUZ, TW_m=TW, longitud_m=None,
                                                L_hidraulico_m=None, categoria_tr=None))


@pytest.fixture
def _limpio():
    antes = dec.estado_de_sesion()
    yield
    dec.restaurar_sesion(antes, sustituir=True)


def _barrer(ruta, valores=VALORES, **kw):
    from src import barrido
    kw.setdefault("nota", NOTA)
    return barrido.barrer(ruta, _externos(), cli.ALCANCE_PERFIL, CLAVE, valores,
                          volcar=cli.informe_json, **kw)


# ===========================================================================
# 1 - Tres corridas, el mismo arbol, la carga que no baja con ke
# ===========================================================================

def test_pf3_el_barrido_corre_una_vez_por_valor_sobre_el_mismo_arbol(tmp_path, _limpio):
    r = _barrer(_csv_a01(tmp_path))
    assert r.clave == CLAVE and tuple(c.valor for c in r.corridas) == VALORES
    huellas = {(c.informe_json["expediente"]["criterios_sha1"],
                c.informe_json["expediente"]["csv_sha1"]) for c in r.corridas}
    assert len(huellas) == 1
    # Cada corrida declaro SU valor, y lo dice el volcado.
    for c in r.corridas:
        usados = {u["clave"]: u for u in c.informe_json["criterios"]["usados"]}
        assert usados[CLAVE]["valor"] == pytest.approx(c.valor, rel=REL_TRANSPORTE)
        assert usados[CLAVE]["declarado_en_caliente"]
        assert NOTA in c.procedencia
    # Mas perdida de entrada no puede dar menos carga gobernante.
    hw = [next(f for f in r.filas if f.valor == c.valor and f.id_punto == "A-01").HW_gobernante_m
          for c in r.corridas]
    assert all(h is not None for h in hw)
    for menor, mayor in zip(hw, hw[1:]):
        assert mayor >= menor * (1 - REL_TRANSPORTE)


def test_pf3_la_tabla_lee_el_volcado_y_la_primera_corrida_es_igual_a_si_misma(tmp_path, _limpio):
    r = _barrer(_csv_a01(tmp_path))
    assert r.corridas[0].comparable and r.corridas[0].comparacion_con_la_primera[0].startswith("IGUALES")
    for c in r.corridas[1:]:
        assert c.comparable
        assert c.comparacion_con_la_primera[0].startswith("DIFIEREN")
    filas = [f for f in r.filas if f.id_punto == "A-01"]
    assert [f.valor for f in filas] == list(VALORES)
    for f in filas:
        assert f.dimensionado and f.material and f.seccion and f.control_gobernante
        assert f.comparable and f.verificaciones_que_cambian == ()


# ===========================================================================
# 2 - La puerta: nada corre fuera de la ventana ni sin procedencia
# ===========================================================================

def test_pf3_un_valor_fuera_de_la_ventana_no_corre_nada(tmp_path, _limpio, monkeypatch):
    corridas = []
    original = servicio.correr
    monkeypatch.setattr(servicio, "correr",
                        lambda *a, **k: corridas.append(1) or original(*a, **k))
    with pytest.raises(ValueError, match="sensibilidad"):
        _barrer(_csv_a01(tmp_path), valores=(0.3, FUERA))
    assert corridas == []
    assert not ca.declarado_en_caliente(CLAVE) and dec.procedencia_de(CLAVE) is None


def test_pf3_un_criterio_de_tabla_exige_fila_o_nota_por_la_misma_puerta(tmp_path, _limpio, monkeypatch):
    corridas = []
    original = servicio.correr
    monkeypatch.setattr(servicio, "correr",
                        lambda *a, **k: corridas.append(1) or original(*a, **k))
    with pytest.raises(ValueError, match="procedencia"):
        _barrer(_csv_a01(tmp_path), nota="")
    assert corridas == []
    assert not ca.declarado_en_caliente(CLAVE)


def test_pf3_el_estado_del_proceso_queda_como_estaba(tmp_path, _limpio):
    # Un estado de entrada con dos declaraciones: una ajena al barrido y la
    # propia clave, con procedencia. Las corridas parten de ese estado y al
    # salir sigue ahi, con la MISMA procedencia.
    ca.establecer_valor_dinamico("longitud_proteccion_salida", 3.0)
    sed.declarar(CLAVE, 0.4, nota="valor de entrada")
    antes = dec.estado_de_sesion()
    r = _barrer(_csv_a01(tmp_path))
    assert dec.estado_de_sesion() == antes
    assert ca.valores_dinamicos()[CLAVE] == pytest.approx(0.4, rel=REL_TRANSPORTE)
    assert dec.procedencia_de(CLAVE).nota == "valor de entrada"
    # Y dentro de cada corrida gobernaba el valor barrido, no el de entrada.
    for c in r.corridas:
        usados = {u["clave"]: u for u in c.informe_json["criterios"]["usados"]}
        assert usados[CLAVE]["valor"] == pytest.approx(c.valor, rel=REL_TRANSPORTE)
        assert "longitud_proteccion_salida" in c.informe_json["criterios"]["declarados_en_caliente"]


# ===========================================================================
# 3 - Guardias y la CLI
# ===========================================================================

def test_pf3_el_barrido_no_recalcula_ni_toca_el_motor():
    arbol = ast.parse((RAIZ / "src" / "barrido.py").read_text(encoding="utf-8"))
    modulos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.add(nodo.module)
            modulos.update(f"{nodo.module}.{a.name}" for a in nodo.names)
        elif isinstance(nodo, ast.Import):
            modulos.update(a.name for a in nodo.names)
    assert not [m for m in modulos if m.startswith("src.modulos")], modulos
    assert "cli" not in modulos
    from src.modelos import ResultadoDeBarrido
    assert ResultadoDeBarrido.__module__ == "src.modelos"


def test_pf3_la_cli_barre_y_escribe_el_json_sin_memoria(tmp_path):
    ruta = _csv_a01(tmp_path)
    salida = tmp_path / "barrido.json"
    hecho = subprocess.run(
        [sys.executable, str(RAIZ / "cli.py"), str(ruta), "--alcance", "perfil",
         "--luz", str(LUZ), "--tw", str(TW),
         "--barrido", f"{CLAVE}=0.3,0.5,0.7", "--barrido-nota", NOTA,
         "--barrido", "TR_evento_extremo=35,50",
         "--json", str(salida), "--html", str(tmp_path / "no.html")],
        capture_output=True, text=True, cwd=RAIZ)
    assert hecho.returncode == 0, hecho.stdout + hecho.stderr
    for v in ("0.3", "0.5", "0.7"):
        assert v in hecho.stdout
    volcado = json.loads(salida.read_text(encoding="utf-8"))
    # Dos barridos, una clave a la vez: nunca el producto cartesiano.
    assert [b["clave"] for b in volcado["barridos"]] == [CLAVE, "TR_evento_extremo"]
    assert [c["valor"] for c in volcado["barridos"][0]["corridas"]] == pytest.approx(
        list(VALORES), rel=REL_TRANSPORTE)
    assert [c["valor"] for c in volcado["barridos"][1]["corridas"]] == [35, 50]
    assert all(c["informe_json"]["expediente"]["puntos"] == 1
               for b in volcado["barridos"] for c in b["corridas"])
    # La memoria no cambia: el barrido es un anexo, no parte del expediente.
    assert not (tmp_path / "no.html").exists()
    # Un valor fuera de la ventana no corre nada y sale con 2.
    hecho = subprocess.run(
        [sys.executable, str(RAIZ / "cli.py"), str(ruta), "--alcance", "perfil",
         "--luz", str(LUZ), "--tw", str(TW), "--barrido", f"{CLAVE}=0.3,{FUERA}",
         "--barrido-nota", NOTA],
        capture_output=True, text=True, cwd=RAIZ)
    assert hecho.returncode == 2 and "sensibilidad" in hecho.stderr
