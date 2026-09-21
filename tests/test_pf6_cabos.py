"""
tests/test_pf6_cabos.py
=======================
Los tres cabos de PF-6, medidos: guardias pequenas que no mueven ningun
numero de calculo.

  (a) R48-007: el techo `dominios.CBR_MAX_FISICO` --- ver el bloque (a), que
      se escribe con el veredicto del verificador normativo sobre el Manual
      de Suelos, y no antes.
  (b) `gui/editores.py::EditorEscalar`: elegir una fila de CLAVE y reescribir
      el texto dejaba la fila vieja en `fila()`, y la puerta
      (`declaracion.declarar_desde_tabla`) rechazaba con «NOMBRA la fila…».
      El editor tiene que SOLTAR la fila cuando el texto deja de ser su clave,
      sin declarar nada por su cuenta (la guardia por AST de EB-01 sigue).
      Se mide en la ventana de verdad (`tests/apoyo/gui_eb_real.py`, bloque
      3b) y con el mismo salto que el resto de tests de ventana real.
  (c) `src/comparador.py`: `lineas()` decia «salvo la marca de tiempo y las
      rutas de origen» y callaba `expediente.csv`; `alcance.diferidos` se
      comparaba solo por longitud; `True` y `1` salian IGUALES. Se compara
      `diferidos` por contenido, se distingue bool de numero, y `lineas()`
      nombra exactamente lo que omite, leido de `CAMPOS_OMITIDOS`, que aqui
      se contrasta contra el comportamiento del comparador campo a campo.

Escritos primero en rojo con `xfail(strict=True)` y liberados al corregir.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from src import comparador as comp
from tests.test_eb_editores_comparador import _ENVOLTORIO, _INTERPRETE

RAIZ = Path(__file__).resolve().parents[1]
LINEA_BASE = RAIZ / "tests" / "linea_base_familia_c"
EMBOCADURA_FILA_A = "cajon_concreto_aletas_30_75"
EMBOCADURA_FILA_B = "cajon_concreto_aleta_45_d043"


def _volcado(nombre: str) -> dict:
    return json.loads((LINEA_BASE / nombre).read_text(encoding="utf-8"))


def _copia(d: dict) -> dict:
    return json.loads(json.dumps(d))


# ===========================================================================
# (b) El editor suelta la fila cuando el texto deja de ser su clave
# ===========================================================================

@pytest.fixture(scope="module")
def ventana_eb(tmp_path_factory):
    if _INTERPRETE is None:
        pytest.skip("ningun interprete disponible puede levantar una ventana "
                    "(falta tkinter, ttkbootstrap o el entorno grafico)")
    salida = tmp_path_factory.mktemp("pf6_ventana")
    hecho = subprocess.run(
        _ENVOLTORIO + [_INTERPRETE, "-m", "tests.apoyo.gui_eb_real", str(salida)],
        cwd=RAIZ, capture_output=True, text=True, timeout=900)
    assert hecho.returncode == 0, f"la ventana fallo:\n{hecho.stdout}\n{hecho.stderr}"
    return json.loads((salida / "resumen_eb.json").read_text(encoding="utf-8"))


def test_pf6b_reescribir_la_clave_de_otra_fila_suelta_la_elegida_y_declara_la_nombrada(ventana_eb):
    r = ventana_eb["embocadura"]
    # Elegir la fila A puso su clave en el texto y en `fila()`.
    assert r["fila_tras_elegir"] == EMBOCADURA_FILA_A
    assert r["texto_tras_elegir"] == EMBOCADURA_FILA_A
    # Reescribir el texto con la clave de B SUELTA la fila elegida...
    assert r["fila_tras_reescribir"] == ""
    # ...y «Aplicar» declara la fila que el texto nombra, sin el rechazo.
    assert not r["estado"].startswith("Error:"), r["estado"]
    assert r["declarado"] == EMBOCADURA_FILA_B
    assert r["procedencia_filas"] == [EMBOCADURA_FILA_B]


# ===========================================================================
# (c) El comparador: lo que omite, dicho; diferidos por contenido; bool ≠ numero
# ===========================================================================

def _mutando(base: dict, f) -> comp.ComparacionDeInformes:
    b = _copia(base)
    f(b)
    return comp.comparar(base, b)


def test_pf6c_campos_omitidos_existe_y_lineas_los_nombra_exactamente():
    omitidos = comp.CAMPOS_OMITIDOS
    assert isinstance(omitidos, tuple) and omitidos
    a = _volcado("informe_perfil_ancho.json")
    lineas = comp.comparar(a, _copia(a)).lineas()
    assert len(lineas) == 1 and comp.ROTULO_IGUALES in lineas[0]
    for campo in omitidos:
        assert campo in lineas[0], (campo, lineas[0])
    # Y no nombra nada que no este en la tupla: la frase antigua desaparece.
    assert "salvo la marca de tiempo" not in lineas[0]


def test_pf6c_lo_que_campos_omitidos_nombra_es_lo_unico_que_no_cuenta():
    """
    Contraste contra el CODIGO: cada campo de `CAMPOS_OMITIDOS` se puede
    mutar sin romper la igualdad, y cada hoja del bloque `expediente` que
    NO esta en la tupla la rompe. `expediente.csv` esta en la tupla porque
    el comparador nunca lo miro y `lineas()` no lo decia.
    """
    a = _volcado("informe_perfil_ancho.json")
    assert "expediente.csv" in comp.CAMPOS_OMITIDOS
    assert "expediente.generado_utc" in comp.CAMPOS_OMITIDOS
    assert "expediente.corredor_del_proyecto.origen" in comp.CAMPOS_OMITIDOS
    assert "datos_sitio.usados[].origen" in comp.CAMPOS_OMITIDOS

    def _muta(ruta: str):
        def f(b):
            partes = ruta.split(".")
            nodo = b
            for parte in partes[:-1]:
                if parte.endswith("[]"):
                    nodo = nodo[parte[:-2]][0]
                else:
                    nodo = nodo[parte]
            nodo[partes[-1]] = "OTRO VALOR"     # ausente o presente, se pisa igual
        return f

    # La corrida de perfil no lee ningun [S] (`datos_sitio.usados` vacia):
    # la ruta de los usados se contrasta sobre el volcado de expediente, que
    # si los lee. `generado` es la marca de tiempo de arriba del volcado, que
    # este formato no lleva; se contrasta anadiendola.
    expediente = _volcado("informe_expediente.json")
    assert expediente["datos_sitio"]["usados"], "la linea base de expediente lee [S]"
    for ruta in comp.CAMPOS_OMITIDOS:
        base = expediente if ruta.startswith("datos_sitio.usados[]") else a
        assert _mutando(base, _muta(ruta)).iguales, f"{ruta} esta en CAMPOS_OMITIDOS y cuenta"
    omitidos_de_expediente = {r.split(".", 1)[1] for r in comp.CAMPOS_OMITIDOS
                              if r.startswith("expediente.")}
    for clave in a["expediente"]:
        if clave in omitidos_de_expediente or f"{clave}.origen" in omitidos_de_expediente:
            continue
        assert not _mutando(a, _muta(f"expediente.{clave}")).iguales, (
            f"expediente.{clave} no esta en CAMPOS_OMITIDOS y no cuenta")


def test_pf6c_los_diferidos_se_comparan_por_contenido_y_no_solo_por_longitud():
    a = _volcado("informe_perfil_ancho.json")
    assert a["alcance"]["diferidos"], "la linea base de perfil difiere etapas"

    def f(b):
        b["alcance"]["diferidos"][0]["criterio"] = "otro_criterio"
    r = _mutando(a, f)
    assert not r.iguales
    assert any(d.donde == comp.ALCANCE and "diferidos" in d.campo for d in r.diferencias)
    # La longitud sigue contando, y se nombra como antes.
    r = _mutando(a, lambda b: b["alcance"]["diferidos"].pop())
    assert not r.iguales


@pytest.mark.parametrize("a_valor,b_valor", [(True, 1), (1, True), (False, 0), (0, False),
                                             (True, 1.0), (0.0, False)])
def test_pf6c_un_booleano_y_un_numero_nunca_son_iguales(a_valor, b_valor):
    a = _volcado("informe_perfil_ancho.json")
    a["expediente"]["cerrado"] = a_valor

    def f(b):
        b["expediente"]["cerrado"] = b_valor
    r = _mutando(a, f)
    assert not r.iguales
    assert any(d.donde == comp.EXPEDIENTE and d.campo == "cerrado" for d in r.diferencias)


def test_pf6c_un_booleano_igual_a_si_mismo_sigue_siendo_igual():
    a = _volcado("informe_perfil_ancho.json")
    assert comp.comparar(a, _copia(a)).iguales


# ===========================================================================
# (a) R48-007: el CBR no tiene techo que la fuente fije
# ===========================================================================
# Verificado contra el PDF del Manual de Suelos (verificador normativo,
# PF-6): Cuadro 4.11 «Categorías de Sub rasante», pág. impresa 37 / PDF 38,
# fila «S5 : Sub rasante Excelente | CBR ≥ 30%», abierta por arriba; Cuadro
# Nº 10.2 «Valor Relativo de Soporte, CBR en Base Granular», pág. impresa 108
# / PDF 109, «Mínimo 100%» para carreteras de primera clase o tráfico
# > 10 x 10^6 EE; Cuadro 12.13, pág. impresa 129 / PDF 130, fila «Base
# Granular CBR 100%, compactada al 100% de la MDS». Y en las 281 páginas no
# hay ningún techo del CBR ni la expresión «piedra patrón»: el 100 de
# `dominios.py` era un valor que la fuente no fija.

from src import dominios
from src.modulos.M0_carga import cargar_puntos
from tests.test_M0_carga import _con

CBR_QUE_EL_TECHO_RECHAZABA = "250"


def test_pf6a_dominios_ya_no_topa_el_cbr_en_100_y_declara_solo_su_piso():
    assert not hasattr(dominios, "CBR_MAX_FISICO"), "el techo que la fuente no fija sigue ahi"
    assert dominios.CBR_MIN_FISICO == 0  # float-exacto: es el cero de la escala, no una medida


def test_pf6a_un_cbr_por_encima_de_100_se_carga_como_dato_valido(tmp_path):
    puntos = cargar_puntos(_con(tmp_path, cbr_subrasante=CBR_QUE_EL_TECHO_RECHAZABA))
    assert puntos[0].cbr_subrasante > 100


@pytest.mark.parametrize("cbr", ["0", "-3"])
def test_pf6a_el_piso_del_cbr_sigue_vigente(tmp_path, cbr):
    from src.modelos import DatoInvalidoError
    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(_con(tmp_path, cbr_subrasante=cbr))
    assert exc.value.campo == "cbr_subrasante"
