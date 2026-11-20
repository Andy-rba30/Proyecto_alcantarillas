"""
tests/test_ve7_lote_c_estado_expediente.py
==========================================
VE-7, lote C, item C5 (VE5GUI-45, «Abierto: la CLI no imprime el estado del
expediente»; decision del consultor Fable, triaje VE-7, 2026-11-20).

`cli.py --estado-expediente` imprime lo que `src/estado_del_expediente.py`
ofrece: las discrepancias abiertas contra la hoja de ruta, con independencia
de la corrida, y --- con `--sesion` --- las corridas embebidas que se pueden
comparar, la mas reciente primero. No corre el pipeline ni lee el CSV, como
`--comparar`. Se prueba por subprocess, que es como lo usa quien lo pide.
"""

import json
import subprocess
import sys
from pathlib import Path

from src import estado_del_expediente as estexp
from src import sesion as _sesion

RAIZ = Path(__file__).resolve().parents[1]


def _cli(*argumentos):
    return subprocess.run([sys.executable, str(RAIZ / "cli.py"), *argumentos],
                          cwd=RAIZ, capture_output=True, text=True,
                          encoding="utf-8", timeout=120)


def test_C5_imprime_las_discrepancias_abiertas_y_sale_con_cero():
    r = _cli("--estado-expediente")
    assert r.returncode == 0, r.stderr
    abiertas = estexp.discrepancias_abiertas()
    assert abiertas
    assert f"Discrepancias abiertas contra la hoja de ruta: {len(abiertas)}" in r.stdout
    for d in abiertas:
        assert d.linea() in r.stdout
    # no corrio el pipeline: ni pide el CSV ni escribe informe
    assert "hace falta el CSV" not in r.stderr
    assert "Corridas de la sesion" not in r.stdout


def test_C5_con_sesion_lista_las_corridas_para_comparar(tmp_path):
    data = _sesion.sesion_vacia("prueba VE-7")
    data["corridas"] = [
        {"generado_utc": "2026-11-20T01:00:00Z", "alcance": "perfil",
         "csv_sha1": "a" * 40, "criterios_sha1": "b" * 40,
         "informe_json": {"x": 1}},
        {"generado_utc": "2026-11-20T03:00:00Z", "alcance": "expediente",
         "csv_sha1": "c" * 40, "criterios_sha1": "d" * 40,
         "informe_json": {"x": 2}},
    ]
    ruta = tmp_path / "sesion.json"
    ruta.write_text(json.dumps(data), encoding="utf-8")
    r = _cli("--estado-expediente", "--sesion", str(ruta))
    assert r.returncode == 0, r.stderr
    lista = estexp.corridas_para_comparar(data["corridas"])
    assert "Corridas de la sesion para comparar (la mas reciente primero): 2" in r.stdout
    primera = r.stdout.index(lista[0].rotulo)
    segunda = r.stdout.index(lista[1].rotulo)
    assert primera < segunda
    for d in estexp.discrepancias_abiertas():
        assert d.linea() in r.stdout


def test_C5_una_sesion_ilegible_sale_con_dos(tmp_path):
    ruta = tmp_path / "rota.json"
    ruta.write_text("{no es json", encoding="utf-8")
    r = _cli("--estado-expediente", "--sesion", str(ruta))
    assert r.returncode == 2
    assert "No se pudo leer la sesion" in r.stderr
