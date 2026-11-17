"""
tests/test_validacion_cabezal.py
================================
La validacion externa de M9 (VE-3.3) contra dos ejemplos resueltos de
departamentos de transporte de EE. UU.: Caltrans BDP 11.2.2 y CDOT Example
11. El generador y las cifras transcritas estan en
`tests/apoyo/validacion_cabezal.py`; el documento, en
`docs/validacion_cabezal.md`.

Lo que se fija aqui:
  * el documento esta sincronizado con el programa;
  * ningun contraste es un DEFECTO del motor;
  * cada contraste que COINCIDE coincide con la tolerancia nombrada de un
    ejemplo impreso, motor contra lo recalculado y fuente contra su cuenta;
  * el CENSO de erratas de las fuentes y de diferencias de metodo no crece ni
    mengua en silencio;
  * la aritmetica de Caltrans: solo no cuadran las dos filas declaradas;
  * mutar una formula de M9 rompe el contraste (el contraste ve el motor);
  * los dos [S] que la tabla de h_eq pide no quedan declarados al salir.

Ninguno abre un PDF ni la hoja de calculo: las cifras estan transcritas.
"""

from __future__ import annotations

import pytest

from src import datos_sitio as ds
from src.modulos import M9_cabezal as M9
from tests.apoyo import validacion_cabezal as VC
from tests.apoyo.validacion_externa import TOLERANCIA_EJEMPLO_IMPRESO


def test_el_documento_esta_sincronizado():
    assert VC.DOCUMENTO.read_text(encoding="utf-8") == VC.generar(), (
        "docs/validacion_cabezal.md no esta sincronizado: "
        "python -m tests.apoyo.validacion_cabezal --escribir")


def test_ningun_contraste_es_un_defecto_del_motor():
    defectos = [(c.ejemplo, c.paso, c.publicado, c.recalculado, c.motor)
                for c in VC.contrastes() if c.juicio == VC.JUICIO_DEFECTO]
    assert not defectos, defectos


def _id(c):
    return f"{c.ejemplo}: {c.paso}"


COINCIDEN = [c for c in VC.contrastes() if c.juicio == VC.JUICIO_COINCIDE]


@pytest.mark.parametrize("c", COINCIDEN, ids=_id)
def test_cada_contraste_que_coincide_coincide(c):
    if isinstance(c.motor, bool):
        assert c.motor is c.recalculado is c.publicado
        return
    assert c.motor == pytest.approx(c.recalculado, rel=TOLERANCIA_EJEMPLO_IMPRESO)
    assert c.publicado == pytest.approx(c.recalculado,
                                        rel=TOLERANCIA_EJEMPLO_IMPRESO)


ERRATAS_ESPERADAS = {
    (VC.CALTRANS, "q = V/B', sismo (Evento Extremo)"),
    (VC.CALTRANS, "e = B/2 − ΣM_O/V, servicio"),
    (VC.CDOT, "k de la seccion fisurada"),
    (VC.CDOT, "dv (5.7.2.8)"),
    (VC.CDOT, "Vc con β = 1.81 (β del procedimiento general, dato de la "
              "fuente)"),
}
# Hasta las correcciones de la revision Fable (A-3) el censo traia una sexta,
# «As de temperatura por cara con b = 12 in, h = 21 in»: NO era errata (la
# hoja comprueba el piso de 5.10.6-2 en AD456) y se retiro.


def test_el_censo_de_erratas_de_las_fuentes():
    """
    Las erratas son de las FUENTES, no del motor, y se fijan por su nombre:
    una nueva aparece aqui como un cambio, no se cuela en el documento.
    """
    assert {(c.ejemplo, c.paso) for c in VC.contrastes() if c.errata} == \
        ERRATAS_ESPERADAS


# El k de CDOT es errata Y metodo a la vez (O-1): lo fija el test de metodo.
ERRATAS_SIN_METODO = [c for c in VC.contrastes()
                      if c.errata and c.juicio != VC.JUICIO_METODO]


@pytest.mark.parametrize("c", ERRATAS_SIN_METODO, ids=_id)
def test_en_una_errata_el_motor_sigue_a_la_cuenta_y_no_a_lo_impreso(c):
    assert c.juicio == VC.JUICIO_ERRATA
    assert c.motor == pytest.approx(c.recalculado, rel=TOLERANCIA_EJEMPLO_IMPRESO)


def test_las_diferencias_de_metodo_son_las_declaradas():
    """
    Hoy son tres, y las tres son el mismo hecho: el modulo de elasticidad
    del concreto (observacion O-1). Un metodo que aparezca sin declararse
    seria un DEFECTO (lo vigila el test de arriba); uno declarado de mas
    aparece aqui.
    """
    metodo = {(c.ejemplo, c.paso.split(" (")[0]) for c in VC.contrastes()
              if c.juicio == VC.JUICIO_METODO}
    assert metodo == {(VC.CALTRANS, "n = Es/Ec"), (VC.CDOT, "n = Es/Ec"),
                      (VC.CDOT, "k de la seccion fisurada")}


def test_toda_fila_de_metodo_trae_la_referencia_del_motor():
    """
    Correcciones de la revision Fable (M-1): una fila que difiere por metodo
    fija tambien lo que el motor TIENE que dar con su metodo, calculado
    aparte; sin eso, cualquier valor del motor fuera del 1 % pasaba.
    """
    sin_referencia = [_id(c) for c in VC.contrastes()
                      if c.metodo and c.referencia is None]
    assert not sin_referencia, sin_referencia


def test_la_ecuacion_de_temperatura_del_motor_se_contrasta_y_no_su_piso():
    """
    Correcciones de la revision Fable (A-3): las tres filas de la ec.
    5.10.6-1 de CDOT (0.083, 0.072 y 0.078 in2/ft, todas bajo el piso de
    0.11) se leen en el motor por la escala de f_y y no devuelven el piso.
    """
    filas = [c for c in VC.contrastes()
             if c.paso.startswith("As de la ec. 5.10.6-1 sin acotar")]
    assert len(filas) == 3
    for c in filas:
        assert c.juicio == VC.JUICIO_COINCIDE
        assert c.motor < 0.11, c.paso


def test_la_aritmetica_de_caltrans_solo_falla_donde_se_declara():
    no_cuadran = [r for r in VC.revisiones_caltrans() if not r.cuadra]
    assert {r.fila for r in no_cuadran} == {
        "parte 6: F·brazo", "parte PA·cos δA: F·brazo"}
    assert all(r.nota for r in no_cuadran)
    assert all("servicio" in r.tabla for r in no_cuadran)


@pytest.mark.parametrize("constante, factor, paso", [
    ("MODULO_ROTURA_AASHTO_SI", 1.05, "Mcr"),
    ("NUCLEO_CENTRAL_DIVISOR", 5.0 / 6.0, "trapecio"),
    # Los de la revision Fable que sobrevivian (M-1 y A-3):
    ("EC_COEFICIENTE_AASHTO_SI", 0.90, "n = Es/Ec"),
    ("EC_COEFICIENTE_AASHTO_SI", 1.04, "n = Es/Ec"),
    ("ES_REFUERZO_AASHTO_MPA", 0.95, "n = Es/Ec"),
    ("TEMPERATURA_COEFICIENTE_AASHTO_SI", 1.0 / 1.30, "ec. 5.10.6-1"),
])
def test_mutar_una_formula_de_M9_rompe_el_contraste(monkeypatch, constante,
                                                     factor, paso):
    """
    El contraste mira el MOTOR: un 5 % en el modulo de rotura o el nucleo
    central en B/5 en vez de B/6 sale como DEFECTO en las filas que los usan.
    """
    monkeypatch.setattr(M9, constante, getattr(M9, constante) * factor)
    defectos = [c.paso for c in VC.contrastes()
                if c.juicio == VC.JUICIO_DEFECTO]
    assert any(paso in p for p in defectos), defectos


def test_el_sitio_de_la_fuente_no_queda_declarado():
    antes = dict(ds.datos_dinamicos())
    VC.contrastes_cdot()
    assert dict(ds.datos_dinamicos()) == antes
