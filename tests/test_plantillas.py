# -*- coding: utf-8 -*-
"""
tests/test_plantillas.py
========================
Guardia C2 del plan de mantenibilidad: verifica que todas las plantillas de
`plantillas/` (CSV mínimos por familia A/B/C, `datos_externos.json`,
`sitio.json` y `sesion_nueva.json`) sigan siendo válidas para el esquema vigente
y pasen `cli.py --prevuelo` sin bloqueos de carga ni faltas bloqueantes a nivel
de perfil, evitando que las plantillas envejezcan en silencio.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

import cli
from src import datos_sitio as ds
from src import modelos, sesion
from src import servicio as srv
from src.modulos import M0_carga as m0

RAIZ = Path(__file__).resolve().parents[1]
PLANTILLAS = RAIZ / "plantillas"

CSVS_POR_FAMILIA = (
    ("familia_A_quebrada.csv", "A", "A-01"),
    ("familia_B_alivio_cuneta.csv", "B", "B-01"),
    ("familia_C_canal.csv", "C", "C-01"),
)


def test_existen_todas_las_plantillas_esperadas():
    esperados = {
        "README.md",
        "familia_A_quebrada.csv",
        "familia_B_alivio_cuneta.csv",
        "familia_C_canal.csv",
        "datos_externos.json",
        "sitio.json",
        "sesion_nueva.json",
    }
    presentes = {p.name for p in PLANTILLAS.iterdir() if p.is_file()}
    assert esperados <= presentes


@pytest.mark.parametrize("nombre,familia_esperada,id_esperado", CSVS_POR_FAMILIA)
def test_csv_plantilla_tiene_las_19_columnas_y_carga_por_m0(
    nombre: str, familia_esperada: str, id_esperado: str
):
    ruta = PLANTILLAS / nombre
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        lector = csv.reader(f)
        encabezado = tuple(next(lector))
        filas = list(lector)
    assert encabezado == m0.COLUMNAS
    assert len(filas) == 1
    assert filas[0][encabezado.index("id")] == id_esperado
    assert filas[0][encabezado.index("familia")] == familia_esperada
    puntos = m0.cargar_puntos(ruta)
    assert len(puntos) == 1
    assert puntos[0].id == id_esperado


def test_datos_externos_plantilla_pasa_validador_de_servicio():
    ext = srv.cargar_datos_externos(PLANTILLAS / "datos_externos.json", {})
    assert "luz_m" in ext.globales
    assert set(ext.por_punto) >= {"A-01", "B-01", "C-01"}


def test_sitio_plantilla_declara_todos_los_s_declarables_sin_rechazos():
    res = cli.cargar_datos_sitio(PLANTILLAS / "sitio.json")
    assert res.rechazados == ()
    esperados = {
        k
        for k, d in ds.DATOS_SITIO.items()
        if not isinstance(d.resolucion, modelos.Derivada)
    }
    assert set(res.restaurados) == esperados
    assert set(ds.datos_dinamicos()) == esperados


def test_sesion_nueva_plantilla_es_v4_valida_sin_avisos_de_migracion():
    crudo = json.loads((PLANTILLAS / "sesion_nueva.json").read_text(encoding="utf-8"))
    assert sesion.errores_de_sesion(crudo) == []
    assert crudo["formato_version"] == sesion.FORMATO_SESION
    assert set(crudo) == set(sesion.sesion_vacia("1.0"))
    migrada, avisos = sesion.migrar_a_actual(crudo)
    assert avisos == []
    assert migrada["formato_version"] == sesion.FORMATO_SESION


@pytest.mark.parametrize("nombre,familia_esperada,id_esperado", CSVS_POR_FAMILIA)
def test_prevuelo_cli_sobre_cada_plantilla_sale_con_0(
    nombre: str, familia_esperada: str, id_esperado: str
):
    cp = subprocess.run(
        [
            sys.executable,
            str(RAIZ / "cli.py"),
            str(PLANTILLAS / nombre),
            "--datos-externos",
            str(PLANTILLAS / "datos_externos.json"),
            "--datos-sitio",
            str(PLANTILLAS / "sitio.json"),
            "--alcance",
            "perfil",
            "--prevuelo",
        ],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert cp.returncode == 0, f"stderr={cp.stderr}\nstdout={cp.stdout}"
    assert "Cabecera completa" in cp.stdout
    assert "0 que detienen una etapa" in cp.stdout
