# -*- coding: utf-8 -*-
"""
tests/test_c4_bloqueos_gui.py
=============================
Pruebas de C4 del plan de mantenibilidad:
- `src/responsable.donde_se_declara_criterio` y `donde_se_declara_dato`
  derivan de `CRITERIOS`, `DATOS_SITIO`, `M0_carga.COLUMNAS` y `servicio` sin
  listas manuales ni remitir al usuario a `CLAUDE.md`.
- `M11_reporte.criterios_bloqueantes` expone `donde_se_declara`.
- `M11_reporte.datos_bloqueantes` agrega `DatoBloqueante` por dato faltante o
  invalido con su ubicacion de declaracion, y se reexporta en `cli.py`.
- En `gui/app.py`, la pestaña 4 (`tree_criterios` y `tree_datos_bloqueantes`)
  muestra que dato falta y donde se declara sobre una corrida real de las
  plantillas sin `--datos-externos` ni `--datos-sitio`.
"""
from __future__ import annotations

from pathlib import Path

import cli
from src import responsable
from src import servicio
from src.modelos import ALCANCE_EXPEDIENTE, ALCANCE_PERFIL
from src.modulos import M11_reporte as M11

RAIZ = Path(__file__).resolve().parents[1]
PLANTILLAS = RAIZ / "plantillas"


def test_responsable_dice_donde_se_declara_criterio_y_dato_sin_claude_md():
    para_a = responsable.donde_se_declara_criterio("remanso_derecho_via")
    para_s = responsable.donde_se_declara_criterio("zona_sismica_aashto")
    assert "Pestaña 2" in para_a and "CLAUDE.md" not in para_a
    assert "Pestaña 1" in para_s and "sitio.json" in para_s and "CLAUDE.md" not in para_s

    para_luz = responsable.donde_se_declara_dato("luz_m")
    para_nf = responsable.donde_se_declara_dato("NF_profundidad_m")
    para_q = responsable.donde_se_declara_dato("Q_m3s")
    para_li = responsable.donde_se_declara_dato("licuefaccion_ems.mitigacion")
    assert "Pestaña 1" in para_luz and "datos_externos.json" in para_luz
    assert "Pestaña 1" in para_nf and "CSV" in para_nf
    assert "Pestaña 1" in para_q and "CSV" in para_q
    assert "Pestaña 1" in para_li and "datos_externos.json" in para_li
    for texto in (para_luz, para_nf, para_q, para_li):
        assert "CLAUDE.md" not in texto


def test_m11_agrega_datos_bloqueantes_y_criterios_sobre_plantilla_sin_externos():
    externos_vacios = servicio.cargar_datos_externos(None, {})
    informe_sin_luz = servicio.correr(
        PLANTILLAS / "familia_B_alivio_cuneta.csv",
        externos_vacios,
        alcance=ALCANCE_EXPEDIENTE,
    )
    datos = M11.datos_bloqueantes(informe_sin_luz)
    assert datos
    assert all(isinstance(d, M11.DatoBloqueante) for d in datos)
    por_dato = {d.dato: d for d in datos}
    assert "luz_m" in por_dato
    assert "L_hidraulico_m" in por_dato
    assert "Pestaña 1" in por_dato["luz_m"].donde_se_declara
    assert "B-01" in por_dato["luz_m"].puntos
    assert cli.datos_bloqueantes is M11.datos_bloqueantes
    assert cli.DatoBloqueante is M11.DatoBloqueante

    # Con luz declarada, la corrida expone criterios bloqueantes por punto + datos en M10.
    externos_con_luz = servicio.cargar_datos_externos(None, {"luz_m": "2.75"})
    informe_con_luz = servicio.correr(
        PLANTILLAS / "familia_B_alivio_cuneta.csv",
        externos_con_luz,
        alcance=ALCANCE_EXPEDIENTE,
    )
    crits = M11.criterios_bloqueantes(informe_con_luz)
    assert crits
    assert all(c.donde_se_declara for c in crits)
    assert any("Pestaña 2" in c.donde_se_declara and "CLAUDE.md" not in c.donde_se_declara
               for c in crits)


def test_llenar_resumen_puebla_tree_criterios_con_donde_y_tree_datos_bloqueantes():
    from gui import app as gapp
    from tests.test_ui1_hidrologia_ventana import _Arbol

    class _DummyInsignia:
        def configurar(self, *_a, **_k):
            pass

        def config(self, **_k):
            pass

    class _DummyLabel:
        def config(self, **_k):
            pass

    externos_con_luz = servicio.cargar_datos_externos(None, {"luz_m": "2.75"})
    informe = servicio.correr(
        PLANTILLAS / "familia_B_alivio_cuneta.csv",
        externos_con_luz,
        alcance=ALCANCE_PERFIL,
    )

    ventana = gapp.ExpedienteApp.__new__(gapp.ExpedienteApp)
    ventana.informe = informe
    ventana.tree_puntos = _Arbol()
    ventana.tree_criterios = _Arbol()
    ventana.tree_datos_bloqueantes = _Arbol()
    ventana.lbl_estado = _DummyLabel()
    ventana.lbl_resumen = {
        "CSV": _DummyLabel(),
        "Alcance de la corrida": _DummyLabel(),
        "Diferidas por alcance": _DummyInsignia(),
        "Puntos del expediente": _DummyInsignia(),
        "Puntos dimensionados": _DummyInsignia(),
        "Verificaciones incumplidas": _DummyInsignia(),
        "Etapas bloqueadas": _DummyInsignia(),
        "Expediente cerrado": _DummyInsignia(),
    }
    ventana._pintar_cabezal_del_proyecto = lambda motivo=None: None
    ventana._al_seleccionar_punto = lambda *_a: None
    ventana._pintar_recuentos_de_puntos = lambda: None
    ventana._refiltrar = lambda: None
    ventana._refrescar_corridas_para_comparar = lambda: None

    gapp.ExpedienteApp._llenar_resumen(ventana)

    filas_datos = list(ventana.tree_datos_bloqueantes.filas.values())
    assert filas_datos, "Se esperaba al menos un bloqueo de dato en Pestaña 4"
    fila_l = next((f for f in filas_datos if f[0] == "L_hidraulico_m"), None)
    assert fila_l is not None
    assert "Pestaña 1" in fila_l[4]

    # Las filas de criterios pendientes incluyen ahora la 9.a columna (`donde_se_declara`).
    filas_crits = list(ventana.tree_criterios.filas.values())
    assert filas_crits
    assert all(len(f) == 9 and "Pestaña 2" in f[8] for f in filas_crits)

    # Vaciar el informe limpia tambien tree_datos_bloqueantes sin fallar.
    gapp.ExpedienteApp._vaciar_tablas_del_informe(ventana, gapp.MOTIVO_CSV_CAMBIADO)
    assert list(ventana.tree_datos_bloqueantes.get_children()) == []
