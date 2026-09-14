"""
tests/test_trazabilidad_csv.py
==============================
La guardia de `docs/trazabilidad.csv`, la vista CSV del registro normativo
GENERADA desde los objetos (sesion T3): una fila por `Cita`, filtrable por
un revisor externo sin leer Markdown.

Calcada de `test_manifiesto_citas.test_T8_el_indice_del_registro_esta_
sincronizado` y de `test_indice_formulas`, y por la misma razon: un documento
que describe el registro y que nadie regenera envejece con el commit
siguiente sin que nada falle. Aqui el CSV se regenera a memoria y se compara
con el que esta en disco; si difieren, NO se edita a mano:

    python3 -m src.normativa.manifiesto --escribir --suite "<N passed, M skipped (entorno)>"

Lo que ademas se vigila, porque es lo que puede envejecer solo:

  1. que el SELLO de la primera linea lleve fecha, commit, alcance y par de
     la suite --la regla de sellos de los planes T3 e I4--, y que el test
     compare el CUERPO, no la fecha: el sello se lee del archivo y se pasa al
     generador.
  2. que las columnas sean exactamente las catorce del plan, en su orden.
  3. que el orden de las filas sea el determinista (fuente_id, numeral,
     cita_id) y que haya exactamente una fila por cita del registro.
  4. que los dos indices inversos que el CSV imprime --discrepancias y
     consumidores-- sean DERIVADOS de lo que los objetos ya declaran: cada
     fundamento aparece en las filas de sus citas y cada tabla, en la de la
     cita que la ancla.
  5. que el separador de listas no aparezca en ningun id ni consumidor, de
     modo que partir una celda por el separador devuelva los elementos.
"""

from __future__ import annotations

import csv
import io
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
for ruta in (str(RAIZ), str(SRC)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

from normativa import manifiesto as man                            # noqa: E402
from normativa.esquema import Usada                                # noqa: E402
from normativa.registro import construir                           # noqa: E402

COMO_REGENERAR = ('python3 -m src.normativa.manifiesto --escribir '
                  '--suite "N passed, M skipped (entorno)"')


@pytest.fixture(scope="module")
def registro():
    return construir()


@pytest.fixture(scope="module")
def texto_en_disco():
    assert man.TRAZABILIDAD_CSV.exists(), (
        f"falta docs/trazabilidad.csv: generalo con {COMO_REGENERAR}")
    return man.TRAZABILIDAD_CSV.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def filas_en_disco(texto_en_disco):
    """Las filas del CSV en disco, leidas con el lector estandar."""
    cuerpo = texto_en_disco.split("\n", 1)[1]
    return list(csv.DictReader(io.StringIO(cuerpo)))


# ---------------------------------------------------------------------------
# 1. Sincronia y sello
# ---------------------------------------------------------------------------

def test_T3_la_vista_csv_esta_sincronizada(registro, texto_en_disco):
    """
    Se regenera con el sello que el archivo YA lleva: lo que se compara es
    el cuerpo. Si difiere, se regenera, no se edita.
    """
    sello = man.leer_sello_csv(texto_en_disco)
    assert sello is not None, "el CSV en disco no lleva un sello legible"
    assert man.trazabilidad_csv(registro, sello) == texto_en_disco, (
        "docs/trazabilidad.csv esta desincronizado con el registro. NO se "
        f"edita a mano: {COMO_REGENERAR}")


def test_el_sello_va_en_la_primera_linea_y_lleva_sus_cuatro_partes(
        registro, texto_en_disco):
    primera = texto_en_disco.split("\n", 1)[0]
    assert primera.startswith("# "), (
        "la primera linea del CSV es el sello, como comentario `#`")
    sello = man.leer_sello_csv(texto_en_disco)
    assert sello is not None
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", sello.fecha), sello.fecha
    assert re.match(r"[0-9a-f]{7,40}", sello.commit), sello.commit
    assert re.search(r"\d+ passed, \d+ skipped", sello.suite), (
        f"el sello tiene que llevar el PAR de la suite: {sello.suite!r}")
    # El alcance lo deriva el generador y por eso no es campo del sello: se
    # comprueba que la linea lo lleve y que diga lo que el registro tiene.
    assert man.alcance_de_trazabilidad(registro) in primera
    assert f"{len(registro.citas)} citas" in primera


def test_leer_sello_csv_recupera_lo_que_linea_escribe():
    sello = man.SelloCSV("2026-09-14", "abc1234",
                         "1910 passed, 4 skipped (PyMuPDF sí · Tk sí)")
    linea = sello.linea("registro completo, una fila por Cita: 1 citas de 1 fuentes")
    assert man.leer_sello_csv(linea + "\ncabecera\nfila") == sello


def test_un_sello_sin_uno_de_sus_campos_no_se_construye():
    for campos in (("", "abc1234", "1 passed, 0 skipped"),
                   ("2026-09-14", "", "1 passed, 0 skipped"),
                   ("2026-09-14", "abc1234", "   ")):
        with pytest.raises(ValueError):
            man.SelloCSV(*campos)


def test_el_par_de_la_suite_no_puede_llevar_saltos_de_linea():
    """El sello es UNA linea de comentario; con un salto dejaria de serlo."""
    with pytest.raises(ValueError):
        man.SelloCSV("2026-09-14", "abc1234", "1 passed, 0 skipped\n(x)")


def test_el_entorno_del_par_puede_llevar_el_punto_medio():
    """
    «PyMuPDF sí · ventana Tk sí» es como la tabla de CLAUDE.md nombra el
    entorno, y el par es el ultimo campo del sello: se lee entero.
    """
    suite = "1949 passed, 4 skipped (PyMuPDF sí · ventana Tk sí), medidos sobre origin/main abc1234"
    sello = man.SelloCSV("2026-09-14", "abc1234", suite)
    assert man.leer_sello_csv(sello.linea("alcance x")) == sello


def test_un_csv_sin_sello_no_se_lee_como_sellado():
    assert man.leer_sello_csv("cita_id,fuente_id\nX,Y\n") is None


# ---------------------------------------------------------------------------
# 2. Columnas
# ---------------------------------------------------------------------------

def test_las_columnas_son_las_catorce_del_plan_en_su_orden(texto_en_disco):
    cabecera = texto_en_disco.split("\n")[1]
    assert cabecera.split(",") == list(man.COLUMNAS_TRAZABILIDAD)
    assert man.COLUMNAS_TRAZABILIDAD == (
        "cita_id", "fuente_id", "norma", "edicion", "numeral",
        "titulo_numeral", "pagina_impresa", "pagina_pdf", "caracter",
        "metodo_verificacion", "fecha_verificacion", "tiene_interpretacion",
        "discrepancias_que_la_tocan", "consumidores_declarados")


def test_ninguna_celda_queda_vacia_donde_hay_algo_pendiente(registro):
    """
    Lo pendiente se escribe con palabras: una celda vacia no puede
    significar «por transcribir» y «sin verificar» a la vez.
    """
    for c in registro.citas:
        fila = man.fila_de_trazabilidad(registro, c)
        for campo in ("titulo_numeral", "pagina_pdf", "metodo_verificacion",
                      "fecha_verificacion", "caracter", "tiene_interpretacion"):
            assert fila[campo].strip(), f"{c.id}: `{campo}` vacio"
        assert fila["tiene_interpretacion"] in ("sí", "no")
        if c.verificado is None:
            assert fila["metodo_verificacion"] == man.SIN_VERIFICAR
            assert fila["fecha_verificacion"] == man.SIN_VERIFICAR
        else:
            assert fila["metodo_verificacion"] == c.verificado.metodo.value
            assert fila["fecha_verificacion"] == c.verificado.fecha


# ---------------------------------------------------------------------------
# 3. Una fila por cita, en orden determinista
# ---------------------------------------------------------------------------

def test_hay_exactamente_una_fila_por_cita(registro, filas_en_disco):
    ids = [f["cita_id"] for f in filas_en_disco]
    assert len(ids) == len(set(ids)), "hay citas repetidas en el CSV"
    assert set(ids) == {c.id for c in registro.citas}


def test_las_filas_van_en_orden_fuente_numeral_cita(filas_en_disco):
    claves = [(f["fuente_id"], f["numeral"], f["cita_id"])
              for f in filas_en_disco]
    assert claves == sorted(claves), (
        "el orden del CSV no es (fuente_id, numeral, cita_id)")


def test_dos_regeneraciones_dan_los_mismos_bytes(registro):
    sello = man.SelloCSV("2026-09-14", "abc1234", "1 passed, 0 skipped (x)")
    assert man.trazabilidad_csv(registro, sello) == \
        man.trazabilidad_csv(construir(), sello)


def test_el_csv_no_lleva_saltos_de_linea_dentro_de_una_celda(
        registro, texto_en_disco, filas_en_disco):
    """Una fila por linea: es lo que hace legible el diff."""
    lineas = texto_en_disco.rstrip("\n").split("\n")
    assert len(lineas) == len(registro.citas) + 2, (   # sello + cabecera
        "el CSV tiene mas lineas que filas: alguna celda lleva un salto")
    assert len(filas_en_disco) == len(registro.citas)


# ---------------------------------------------------------------------------
# 4. Los dos indices inversos son derivados, no mantenidos
# ---------------------------------------------------------------------------

def test_cada_fundamento_aparece_en_las_filas_de_sus_citas(registro):
    for f in registro.fundamentos:
        for cita_id in f.citas:
            consumidores = registro.consumidores_de_cita(cita_id)
            assert any(x.startswith(f"fundamento {f.id} ")
                       for x in consumidores), (
                f"{cita_id}: no lista al fundamento {f.id} que la cita")


def test_cada_tabla_usada_aparece_en_la_fila_de_la_cita_que_la_ancla(registro):
    for t in registro.tablas:
        esperados = {por for e in (*t.columnas, *t.filas)
                     if isinstance(e.uso, Usada) for por in e.uso.por}
        consumidores = registro.consumidores_de_cita(t.cita_id)
        for por in esperados:
            assert f"tabla {t.id} -> {por}" in consumidores, (
                f"{t.cita_id}: no lista a {por} via la tabla {t.id}")


def test_los_consumidores_del_csv_cubren_los_declarados_del_registro(registro):
    """
    El indice inverso no pierde a nadie: todo consumidor que
    `consumidores_declarados` recoge para el registro entero aparece en la
    fila de al menos una cita.
    """
    en_filas = set()
    for c in registro.citas:
        for x in registro.consumidores_de_cita(c.id):
            if x.startswith("tabla "):
                en_filas.add(x.split(" -> ", 1)[1])
    assert set(registro.consumidores_declarados()) <= en_filas


def test_cada_discrepancia_aparece_en_las_filas_de_sus_citas(registro):
    for d in registro.discrepancias:
        for cita_id in d.citas:
            if cita_id not in {c.id for c in registro.citas}:
                continue   # parte sin cita transcrita: T2 lleva el trinquete
            fila = man.fila_de_trazabilidad(registro, registro.cita(cita_id))
            assert f"{d.id} [{d.estado.value}]" in fila[
                "discrepancias_que_la_tocan"], (
                f"{cita_id}: no lista a {d.id}")


def test_una_cita_sin_nada_que_la_toque_lleva_las_dos_celdas_vacias(registro):
    """Vacio aqui SI significa «ninguna»: no hay otra lectura posible."""
    huerfanas = [c for c in registro.citas
                 if not registro.discrepancias_de_cita(c.id)
                 and not registro.consumidores_de_cita(c.id)]
    assert huerfanas, "el test necesita al menos una cita sin indices"
    fila = man.fila_de_trazabilidad(registro, huerfanas[0])
    assert fila["discrepancias_que_la_tocan"] == ""
    assert fila["consumidores_declarados"] == ""


# ---------------------------------------------------------------------------
# 5. El separador de listas no colisiona con lo que separa
# ---------------------------------------------------------------------------

def test_el_separador_de_lista_no_aparece_en_ningun_elemento(registro):
    sep = man.SEPARADOR_DE_LISTA
    for d in registro.discrepancias:
        assert sep not in d.id and sep not in d.estado.value
    for c in registro.citas:
        for x in registro.consumidores_de_cita(c.id):
            assert sep not in x, x


def test_partir_una_celda_por_el_separador_devuelve_los_elementos(
        registro, filas_en_disco):
    por_id = {f["cita_id"]: f for f in filas_en_disco}
    for c in registro.citas:
        celda = por_id[c.id]["consumidores_declarados"]
        partes = celda.split(man.SEPARADOR_DE_LISTA) if celda else []
        assert tuple(partes) == registro.consumidores_de_cita(c.id)


# ---------------------------------------------------------------------------
# El modo informe de `main`
# ---------------------------------------------------------------------------

def test_escribir_sin_suite_se_niega(capsys):
    """El par de la suite es parte del sello y no se inventa."""
    assert man.main(["--escribir"]) == 2
    assert "--suite" in capsys.readouterr().out
