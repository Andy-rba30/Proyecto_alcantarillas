# -*- coding: utf-8 -*-
"""
Lote VE5-GUI: cuatro huecos de la interfaz que el censo del 2026-11-20 dejó
como «implementable ya» (ítems 37, 38, 40 y 42). Ficha VE5GUI-01 de
`docs/decisiones_diferidas.md`.

- **42 (UI1-02):** el editor tipado ofrece las filas de TODAS las tablas de
  un criterio que se lee sobre varias, y declara cada una con su tabla.
- **37 (EB-06, T11-10):** la ventana emergente tiene campo de nota y declara
  por la MISMA puerta que la pestaña 2 (`src.editores.declarar`).
- **40 (T6-04):** `bombeo`, `peralte` y `S_conducto` tienen campo en la
  pestaña 1, viajan en la sesión y tienen bandera en la CLI.
- **38 (UI3-01, UI4-01):** el panel de declaración de la pestaña 2 tiene
  scroll y la fila de exportación cabe a 900 px (medido en ventana real, por
  `tests/apoyo/gui_ve5_real.py`, en `tests/test_ve5_gui_ventana.py`).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src import criterios_adoptados as ca
from src import declaracion as dec
from src import editores as sed

RAIZ = Path(__file__).resolve().parent.parent

N_CAJON = "n_manning_cajon"
TB1 = "HDS5_3ED.TB.1"
T09 = "MC_HHD.T09"
H_EQ = "h_eq_bajo_altura_tabulada"
H_EQ_T1 = "AASHTO_LRFD_9.T3.11.6.4-1"
H_EQ_T2 = "AASHTO_LRFD_9.T3.11.6.4-2"
KE = "ke_entrada"


# ===========================================================================
# 42 · Las filas de todas las tablas (UI1-02)
# ===========================================================================

def test_42_el_esquema_ofrece_las_filas_de_todas_las_tablas():
    e = sed.esquema_de(N_CAJON)
    assert e.tablas == (TB1, T09)
    # `tabla_id` sigue siendo la primera: lo leen los consumidores de
    # un criterio de una sola tabla y los tests de T11-10.
    assert e.tabla_id == TB1
    por_tabla = {}
    for o in e.opciones_de_tabla:
        por_tabla.setdefault(o.tabla_id, set()).add(o.fila)
    assert set(por_tabla) == {TB1, T09}
    assert "concrete_boxes" in por_tabla[TB1]
    assert "concreto_afinado" in por_tabla[T09]


def test_42_la_fila_de_la_segunda_tabla_entra_con_su_procedencia_y_sin_nota():
    # La alternativa barrible de la Tabla N 09: hasta VE5-GUI sólo entraba
    # con nota, como adopción, porque el editor no conocía esa tabla.
    p = sed.declarar(N_CAJON, "concreto_afinado")
    assert p.tabla_id == T09
    assert p.filas == ("concreto_afinado",)
    assert not ca.declarado_en_caliente(N_CAJON) or ca.valor(N_CAJON) == "concreto_afinado"
    assert ca.valor(N_CAJON) == "concreto_afinado"


def test_42_elegir_la_fila_por_su_referencia_calificada():
    e = sed.esquema_de(N_CAJON)
    o = next(o for o in e.opciones_de_tabla if o.fila == "concreto_afinado")
    assert o.referencia == f"{T09}#concreto_afinado"
    p = sed.declarar(N_CAJON, "concreto_afinado", fila=o.referencia)
    assert p.tabla_id == T09


def test_42_una_fila_repetida_en_dos_tablas_exige_decir_cual():
    e = sed.esquema_de(H_EQ)
    assert e.tablas == (H_EQ_T1, H_EQ_T2)
    referencias = {o.referencia for o in e.opciones_de_tabla}
    assert f"{H_EQ_T1}#5" in referencias and f"{H_EQ_T2}#5" in referencias
    with pytest.raises(ValueError, match="dos o mas tablas|varias tablas"):
        sed.declarar(H_EQ, "primera_fila", fila="5")
    p = sed.declarar(H_EQ, "primera_fila", fila=f"{H_EQ_T2}#5")
    assert p.tabla_id == H_EQ_T2
    assert p.filas == ("5",)


def test_42_una_fila_que_no_existe_en_ninguna_tabla_se_rechaza():
    with pytest.raises(ValueError):
        sed.declarar(N_CAJON, "concrete_boxes", fila="no_existe")
    with pytest.raises(ValueError):
        sed.declarar(N_CAJON, "concreto_afinado", fila=f"{TB1}#concreto_afinado")


def test_42_el_texto_que_nombra_una_fila_de_la_segunda_tabla_es_esa_fila():
    e = sed.esquema_de(N_CAJON)
    assert sed.fila_implicita(e, "concreto_afinado") == f"{T09}#concreto_afinado"
    assert sed.fila_implicita(e, "concrete_boxes") == f"{TB1}#concrete_boxes"


def test_42_un_criterio_de_una_sola_tabla_no_cambia():
    e = sed.esquema_de(KE)
    assert e.tablas == (e.tabla_id,)
    assert all(o.referencia == o.fila for o in e.opciones_de_tabla)
    assert all(o.tabla_id == e.tabla_id for o in e.opciones_de_tabla)


# ===========================================================================
# 37 · La ventana emergente con campo de nota (EB-06, T11-10)
# ===========================================================================

KE_TC2 = "HDS5_3ED.TC2"
KE_FILA = "concreto_headwall_square_edge"
ENSAYO = "capacidad_portante_adm"
NOTA = "adoptado del plano tipo del proyecto, hoja 3"


def _id_de_fila(tabla_id, clave_corta):
    from src import ventana_normativa as vn
    contenido = vn.contenido_de_tabla(tabla_id, KE)
    return next(f.id for f in contenido.filas if f.clave_corta == clave_corta)


def test_37_un_numero_que_difiere_de_la_celda_exige_nota_y_con_ella_entra():
    fila_id = _id_de_fila(KE_TC2, KE_FILA)
    with pytest.raises(ValueError):
        sed.declarar_desde_la_ventana(KE, 0.55, tabla_id=KE_TC2, fila=fila_id)
    assert not ca.declarado_en_caliente(KE)
    p = sed.declarar_desde_la_ventana(KE, 0.55, tabla_id=KE_TC2, fila=fila_id, nota=NOTA)
    assert p.tabla_id == KE_TC2 and p.filas == (KE_FILA,)
    assert p.nota == NOTA
    assert ca.valor(KE) == pytest.approx(0.55)


def test_37_la_fila_de_la_tabla_sin_nota_sigue_entrando_como_antes():
    p = sed.declarar_desde_la_ventana(KE, 0.5, tabla_id=KE_TC2,
                                      fila=_id_de_fila(KE_TC2, KE_FILA))
    assert p.filas == (KE_FILA,)


def test_37_un_criterio_de_tabla_sin_fila_entra_solo_con_nota():
    with pytest.raises(ValueError, match="fila"):
        sed.declarar_desde_la_ventana(KE, 0.55, tabla_id=KE_TC2)
    assert not ca.declarado_en_caliente(KE)
    p = sed.declarar_desde_la_ventana(KE, 0.55, tabla_id=KE_TC2, nota=NOTA)
    assert p.nota == NOTA and not p.filas


def test_37_un_dato_de_ensayo_exige_la_nota_que_es_su_trazabilidad():
    with pytest.raises(ValueError, match="TRAZABILIDAD"):
        sed.declarar_desde_la_ventana(ENSAYO, 150.0)
    assert not ca.declarado_en_caliente(ENSAYO)
    p = sed.declarar_desde_la_ventana(ENSAYO, 150.0, nota="ensayo de carga, informe EMS-03")
    assert p.nota.startswith("ensayo de carga")


def test_37_el_par_del_encofrado_de_t11_10_entra_por_la_ventana():
    par = (0.013, 0.016)
    with pytest.raises(ValueError):
        sed.declarar_desde_la_ventana(N_CAJON, par, tabla_id=TB1)
    p = sed.declarar_desde_la_ventana(
        N_CAJON, par, tabla_id=TB1, nota="encofrado metalico, especificacion E-12")
    assert tuple(ca.valor(N_CAJON)) == par
    assert p.nota


def test_37_la_ventana_declara_por_la_puerta_de_editores_y_no_por_declaracion():
    """La emergente sólo pinta: su declaración es `src.editores.declarar_desde_la_ventana`."""
    arbol = ast.parse((RAIZ / "gui" / "ventana_normativa.py").read_text(encoding="utf-8"))
    metodo = next(n for n in ast.walk(arbol)
                  if isinstance(n, ast.FunctionDef) and n.name == "_declarar_segun_cara")
    llamadas = {ast.unparse(n.func) for n in ast.walk(metodo) if isinstance(n, ast.Call)}
    assert any(l.endswith("declarar_desde_la_ventana") for l in llamadas), llamadas
    assert not any(l.startswith("dec.declarar") for l in llamadas), llamadas
    texto = (RAIZ / "gui" / "ventana_normativa.py").read_text(encoding="utf-8")
    assert "nota_var" in texto


def test_37_la_puerta_de_la_ventana_es_la_de_la_pestana_2():
    """Sin columna, la ventana pasa por `declarar` con la fila calificada por su tabla."""
    fuente = ast.parse((RAIZ / "src" / "editores.py").read_text(encoding="utf-8"))
    f = next(n for n in ast.walk(fuente)
             if isinstance(n, ast.FunctionDef) and n.name == "declarar_desde_la_ventana")
    llamadas = {ast.unparse(n.func) for n in ast.walk(f) if isinstance(n, ast.Call)}
    assert "declarar" in llamadas
