"""
tests/test_t11_correcciones.py
==============================
Las correcciones de T-11 que tocan el PROGRAMA (y no solo la validacion):
tres hallazgos de la auditoria adversarial de T-11 que son de FORMATO o de
TRANSPARENCIA, ninguno de calculo. Los demas hallazgos (H1 a H7, H11 a H14)
son de los documentos de la validacion y los fijan
`tests/test_t11_validacion_integral.py`, `test_t11_sensibilidad.py` y
`test_t11_validacion_externa.py`.

- H9 (BAJA, decision del dueño del 2026-11-13 ~19:50 UTC): `diseno.HW_salida_m`
  del JSON es `null` cuando el control de salida NO SE FORMA --el perfil de
  la lamina sustituye a la aproximacion (HW_aprox/D < 0.75, HDS-5 pag.
  impresa 3.24) y su remanso no alcanza la entrada--; la aproximacion
  descartada sigue en `perfil_HW_aproximado_m`, y la linea «Control» del
  texto de la CLI dice «salida no se forma». El HW que gobierna, la entrada,
  los diametros y los materiales no cambian.
- H10 (BAJA): la fila A7 del armado existe con
  `EstadoDeVerificacion.NO_APLICA` y su razon cuando el analisis quimico esta
  declarado y E.060 no fija f'c minimo (exposicion a sulfatos «insignificante»
  de la Tabla 4.4, pag. impresa 38, y ninguna fila de la Tabla 4.2). No juzga
  ni rellena un minimo.
- H8 (BAJA): la columna «Tipo de cabezal» del cuadro resumen de la Fase 11
  sale DEL PUNTO (`M11.tipo_cabezal_del_punto`: su embocadura y el tipo de
  sus dos cabezales), no de la decision unica del Tablero 2.3 de la hoja de
  ruta («tubo a ras del muro»), que se imprimia igual tambien en el marco de
  la Familia C. Reporte, sin aritmetica.

NO SE ESCRIBIO EN ROJO PRIMERO con `xfail`: el rojo se midio con este
archivo contra el arbol previo (`10fb84b`), y el numero esta en el informe
de las correcciones de T-11.
"""

from __future__ import annotations

import csv

import pytest

import cli
from src.modelos import EstadoDeVerificacion
from src.modulos import M11_reporte as M11
from tests.apoyo import validacion_integral as V
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.fixtures import juego_validacion_integral as J


@pytest.fixture(scope="module")
def juego():
    return V.correr_juego()


def _punto(informe, id_punto):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


def _diseno(informe, id_punto):
    return next(p for p in cli.informe_json(informe)["puntos"]
                if p["id"] == id_punto)["diseno"]


# ===========================================================================
# H9 · `HW_salida_m` = null donde el control de salida no se forma
# ===========================================================================

def test_HW_salida_es_null_donde_el_perfil_no_alcanza_la_entrada(juego):
    """
    A-02 y B-01 del juego: el perfil S1 sustituye a la aproximacion y no
    alcanza la entrada. La clave va `null`; el numero descartado sigue en
    `perfil_HW_aproximado_m` y es el de `ResultadoHidraulico.HW_salida`, que
    no cambio.
    """
    for id_punto in ("A-02", "B-01"):
        d = _diseno(juego, id_punto)
        h = _punto(juego, id_punto).resultado.resultado_hidraulico
        assert d["perfil_sustituye_aproximacion"] is True
        assert d["perfil_HW_remanso_m"] is None
        assert d["HW_salida_m"] is None
        assert d["perfil_HW_aproximado_m"] == pytest.approx(
            h.HW_salida, rel=REL_TRANSPORTE)
        # Lo que gobierna no se toca.
        assert d["control_gobernante"] == "entrada"
        assert d["HW_gobernante_m"] == pytest.approx(d["HW_entrada_m"],
                                                     rel=REL_TRANSPORTE)
        assert d["HW_gobernante_m"] == pytest.approx(h.HW, rel=REL_TRANSPORTE)
        assert cli.salida_no_se_forma(h)


def test_HW_salida_sigue_siendo_un_numero_donde_el_control_se_forma(juego):
    """
    A-01 (la aproximacion se usa) y C-01 (el perfil sustituye y SI alcanza
    la entrada: la clave lleva el remanso): la clave no cambia.
    """
    a01 = _diseno(juego, "A-01")
    assert a01["perfil_sustituye_aproximacion"] is False
    assert a01["HW_salida_m"] == pytest.approx(
        _punto(juego, "A-01").resultado.resultado_hidraulico.HW_salida,
        rel=REL_TRANSPORTE)
    c01 = _diseno(juego, "C-01")
    assert c01["perfil_sustituye_aproximacion"] is True
    assert c01["perfil_HW_remanso_m"] is not None
    assert c01["HW_salida_m"] == pytest.approx(c01["perfil_HW_remanso_m"],
                                               rel=REL_TRANSPORTE)
    assert not cli.salida_no_se_forma(
        _punto(juego, "C-01").resultado.resultado_hidraulico)


def test_la_linea_control_del_texto_dice_que_la_salida_no_se_forma(juego):
    lineas = {p.punto.id: next(l for l in cli._lineas_punto(p)
                               if "Control  :" in l)
              for p in juego.puntos}
    for id_punto in ("A-02", "B-01"):
        assert "salida no se forma" in lineas[id_punto], lineas[id_punto]
    for id_punto in ("A-01", "C-01"):
        assert "no se forma" not in lineas[id_punto], lineas[id_punto]


def test_el_comparador_lee_el_null_como_una_diferencia_y_no_se_rompe(juego):
    """
    Los lectores de la clave: el comparador de E-B dice la diferencia entre
    un numero y `null` sin reventar y sin declararla «no comparable» (el
    metodo no cambio).
    """
    from src import comparador
    nuevo = cli.informe_json(juego)
    viejo = cli.informe_json(juego)
    for p in viejo["puntos"]:
        if p["id"] == "B-01":
            p["diseno"]["HW_salida_m"] = p["diseno"]["perfil_HW_aproximado_m"]
    c = comparador.comparar(viejo, nuevo)
    assert not c.no_comparables
    assert [(d.donde, d.campo) for d in c.diferencias] == [
        ("B-01", "diseno.HW_salida_m")]


# ===========================================================================
# H10 · la fila A7 con NO_APLICA y su razon
# ===========================================================================

def test_A7_existe_y_no_aplica_con_exposicion_insignificante(juego):
    for p in juego.puntos:
        filas = {v.codigo: v for v in p.cabezal.verificaciones
                 if v.codigo and v.codigo.startswith("A7.")}
        assert set(filas) == {"A7.concreto.e", "A7.concreto.s"}, p.punto.id
        for v in filas.values():
            assert v.estado is EstadoDeVerificacion.NO_APLICA
            assert v.cumple and v.paso is None
            assert v.valor_admisible is None
            assert "insignificante" in v.motivo_no_aplica
            assert "Tabla 4.4" in v.motivo_no_aplica
            assert "no impone un f'c minimo" in v.motivo_no_aplica
        # No cuenta como incumplida ni deja aviso.
        assert not any("A7" in a for a in p.cabezal.avisos)
        assert all(v.codigo is None or not v.codigo.startswith("A7")
                   for v in p.incumplidas())


def test_A7_decide_cuando_la_exposicion_impone_un_minimo():
    """El otro lado (variante `agua_con_cloruros`): A7 decide, como antes."""
    informe = V.correr_juego(V.aplicar(V.juego_completo(),
                                       J.VARIANTES["agua_con_cloruros"][1]))
    a01 = _punto(informe, "A-01")
    a7 = [v for v in a01.cabezal.verificaciones
          if v.codigo and v.codigo.startswith("A7.")]
    assert a7 and all(v.estado is EstadoDeVerificacion.NO_CUMPLE for v in a7)
    assert all(v.paso is not None for v in a7)


def test_A7_no_aplica_llega_a_la_memoria_y_a_la_cli(juego):
    html = M11.memoria_html(juego)
    assert 'A7.concreto.e</td>' in html
    assert M11.CLASE_NO_APLICA in html
    texto = cli.volcar(juego)
    assert "[N/A] A7.concreto.e" in texto


# ===========================================================================
# H8 · el tipo de cabezal del cuadro resumen, del punto
# ===========================================================================

def test_el_tipo_de_cabezal_sale_del_punto(juego):
    for p in juego.puntos:
        tipo = M11.tipo_cabezal_del_punto(p)
        assert tipo is not None
        assert tipo.startswith(p.embocadura.tipo), tipo
        assert "ras del muro" not in tipo
        for g in p.cabezal.geometrias:
            assert f"{g.extremo} {g.tipo}" in tipo
    c01 = _punto(juego, "C-01")
    assert "aleros" in M11.tipo_cabezal_del_punto(c01)


def test_el_cuadro_resumen_lleva_el_tipo_del_punto(juego, tmp_path):
    ruta = M11.exportar_csv(juego, tmp_path / "resumen.csv")
    filas = list(csv.DictReader(ruta.read_text(encoding="utf-8").splitlines()))
    assert [f["id"] for f in filas] == [p.punto.id for p in juego.puntos]
    for f, p in zip(filas, juego.puntos):
        assert f["tipo_cabezal"] == M11.tipo_cabezal_del_punto(p)
    html = M11.memoria_html(juego)
    for p in juego.puntos:
        assert M11.tipo_cabezal_del_punto(p) in html


def test_sin_embocadura_la_celda_queda_vacia_declarada():
    """Sin juego ningun punto pasa de la luz: la celda no se rellena."""
    por_defecto = V.correr(None)
    for p in por_defecto.puntos:
        assert M11.tipo_cabezal_del_punto(p) is None
        assert M11._fila_resumen_csv(p)[-1] == ""
        assert M11.fila_resumen(p).count(M11.VACIO) >= 1
