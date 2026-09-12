"""
tests/test_traza_punto.py
=========================
La capa de CONTENIDO del detalle «¿De donde sale este numero?» de la pestaña
3 (G4): `src/traza_punto.py`.

Se prueba como se prueba `ventana_normativa`: el contenido es un DATO y se
compara campo a campo, sin ventana y sin escritorio, sobre una corrida real
de `tests/ejemplo_puntos.csv` --- la misma que usan `test_M11_reporte` y
`test_memoria_sustentada` ---. Lo que la GUI pinta de ese dato se comprueba
en `tests/test_gui_contrato.py`.

La comprobacion central es de NO-DIVERGENCIA: la traza que la GUI recibe
tiene que contar LO MISMO que la memoria HTML imprime, paso a paso y en el
mismo orden. No se compara contra una lista escrita a mano --- que es como se
desincronizan las listas --- sino contra el producto de M11 sobre el mismo
informe.

Y la guardia de AST, calcada de la que barre M11 (SIS-A-07): la capa de
contenido elige textos y orden, NO hace aritmetica sobre magnitudes.
"""

from __future__ import annotations

import html as _html
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
for ruta in (str(RAIZ), str(SRC)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

import traza_punto as tp                                           # noqa: E402
from cli import cargar_datos_externos, correr                      # noqa: E402
from modelos import TipoDeVeredicto                                # noqa: E402
from modulos import M11_reporte as M11                             # noqa: E402
from normativa.esquema import Verbo                                # noqa: E402
from normativa.registro import construir                           # noqa: E402

CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"

LOS_TRES_REGISTROS = {tp.REGISTRO_FUENTE, tp.REGISTRO_INTERPRETACION,
                      tp.REGISTRO_PROYECTO}


@pytest.fixture(scope="module")
def reg():
    return construir()


@pytest.fixture(scope="module")
def informe():
    externos = cargar_datos_externos(
        None, {"luz_m": 2.0, "TW_m": 0.0, "longitud_m": 14.0,
               "L_hidraulico_m": None, "categoria_tr": None})
    return correr(CSV_EJEMPLO, externos)


@pytest.fixture(scope="module")
def trazas(informe):
    return tuple(tp.traza_del_punto(ip) for ip in informe.puntos)


def _entradas(trazas):
    for traza in trazas:
        for seccion in traza.secciones:
            for entrada in seccion.entradas:
                yield entrada


def _detalles(trazas):
    for entrada in _entradas(trazas):
        if isinstance(entrada, tp.DetalleDePaso):
            yield entrada


# ===========================================================================
# La no-divergencia con la memoria: mismos pasos, mismo orden
# ===========================================================================

# El titular de cada paso en la memoria HTML: `<code>codigo</code> — que`
# para un `bloque_paso`, `<code>codigo</code> — sin fundamento...` para un
# `_paso_ausente` (que lleva ademas la clase `nota`).
_H5_DE_PASO = re.compile(
    r'<div class="paso(?: nota)?"><h5>(?:<code>(.*?)</code> &mdash; )?'
    r"(.*?)</h5>")


def _titulares_de_la_memoria(informe_punto) -> list:
    html = M11.memoria_de_punto(informe_punto)
    return [(_html.unescape(codigo or ""), _html.unescape(titulo))
            for codigo, titulo in _H5_DE_PASO.findall(html)]


def test_la_traza_cuenta_los_mismos_pasos_que_la_memoria_y_en_su_orden(
        informe, trazas):
    """
    EL CONTRATO DE G4: la GUI y la memoria no pueden contar historias
    distintas del mismo punto. La secuencia (codigo, titulo) de las entradas
    de la traza --- huecos incluidos --- es exactamente la de los bloques de
    paso que `memoria_de_punto` imprime, punto por punto.
    """
    for informe_punto, traza in zip(informe.puntos, trazas):
        en_memoria = _titulares_de_la_memoria(informe_punto)
        en_traza = [(e.codigo or "", e.titulo)
                    for s in traza.secciones for e in s.entradas]
        assert en_traza == en_memoria, traza.id_punto


def test_la_traza_tiene_pasos_y_titulos_de_seccion_de_M11(trazas):
    """El detalle no sale vacio, y sus secciones llevan los titulos de M11."""
    titulos_m11 = {M11.TITULO_TRAZA_CLASIFICACION, M11.TITULO_TRAZA_TW,
                   M11.TITULO_TRAZA_HIDRAULICA,
                   M11.TITULO_TRAZA_HIDRAULICA_ULTIMO,
                   M11.TITULO_TRAZA_VERIFICACIONES}
    assert trazas
    for traza in trazas:
        assert traza.secciones, traza.id_punto
        for seccion in traza.secciones:
            assert seccion.titulo in titulos_m11, seccion.titulo


def test_el_desarrollo_no_adoptado_llega_con_su_aviso(informe, trazas):
    """
    En este expediente ningun punto se dimensiona (V5 se detiene en
    `ancho_derecho_via_m`), asi que el desarrollo hidraulico es el del ultimo
    escalon evaluado y publicarlo SIN el aviso seria presentar calculo
    descartado como diseño adoptado.
    """
    assert informe.dimensionados == 0, (
        "si algun punto llegara a dimensionarse, este test deja de probar lo "
        "que dice: revisar el supuesto antes de tocarlo")
    con_hidraulica = [s for traza in trazas for s in traza.secciones
                      if s.titulo == M11.TITULO_TRAZA_HIDRAULICA_ULTIMO]
    assert con_hidraulica
    for seccion in con_hidraulica:
        assert "no se dimensiono" in seccion.aviso


# ===========================================================================
# Los huecos declarados: nunca una fila en blanco ni un texto inventado
# ===========================================================================

def test_las_verificaciones_sin_paso_llegan_como_hueco_censado(trazas):
    huecos = [e for e in _entradas(trazas)
              if isinstance(e, tp.HuecoDeVerificacion)]
    assert huecos, "la corrida de ejemplo emite al menos un hueco (V4b)"
    censo = M11.sin_fundamento_por_codigo()
    for hueco in huecos:
        assert hueco.codigo in censo
        por_que, que_haria_falta = censo[hueco.codigo]
        assert hueco.por_que == por_que
        assert hueco.que_haria_falta == que_haria_falta
        assert hueco.titulo == tp.TITULO_HUECO


def test_ninguna_entrada_llega_en_blanco(trazas):
    for entrada in _entradas(trazas):
        assert entrada.titulo.strip()
        assert entrada.lineas
        for linea in entrada.lineas:
            assert linea.registro in LOS_TRES_REGISTROS
            assert linea.rotulo.strip()
            assert linea.texto.strip(), (entrada.codigo, linea.rotulo)


# ===========================================================================
# El por que, con el verbo del fundamento
# ===========================================================================

def test_el_por_que_lleva_el_verbo_que_el_registro_sostiene(trazas, reg):
    """
    La primera linea de cada paso es su `por_que`, y cuando el paso declara
    fundamento el rotulo dice el VERBO --- obliga / recomienda / permite /
    define --- leido del registro, cuyo T11 ya garantiza que el caracter de
    alguna cita lo sostiene. Aqui se comprueba que la traza lo LEE y no lo
    redacta: el verbo del rotulo es exactamente el del `Fundamento`.
    """
    verbos = {v.value for v in Verbo}
    comprobados = 0
    for detalle in _detalles(trazas):
        primera = detalle.lineas[0]
        assert primera.rotulo.startswith(tp.ROTULO_POR_QUE)
        assert primera.texto == detalle.paso.por_que
        if detalle.paso.fundamento_id:
            verbo = reg.fundamento(detalle.paso.fundamento_id).verbo.value
            assert verbo in verbos
            assert primera.rotulo.endswith(verbo), detalle.codigo
            comprobados += 1
    assert comprobados, "ningun paso con fundamento: el test no probo nada"


# ===========================================================================
# Sustitucion con procedencia, umbral con caracter, veredicto con margen
# ===========================================================================

def _linea(detalle, rotulo):
    return next((l for l in detalle.lineas if l.rotulo == rotulo), None)


def test_cada_valor_de_la_sustitucion_llega_con_su_procedencia(trazas):
    comprobados = 0
    for detalle in _detalles(trazas):
        if not detalle.paso.sustitucion:
            continue
        linea = _linea(detalle, tp.ROTULO_SUSTITUCION)
        assert linea is not None, detalle.codigo
        for m in detalle.paso.sustitucion:
            assert m.simbolo in linea.texto
            assert m.procedencia in linea.texto, (detalle.codigo, m.simbolo)
        comprobados += 1
    assert comprobados


def test_el_resultado_llega_con_su_procedencia(trazas):
    for detalle in _detalles(trazas):
        linea = _linea(detalle, tp.ROTULO_RESULTADO)
        assert linea is not None
        assert detalle.paso.resultado.procedencia in linea.texto


def test_el_umbral_llega_con_su_caracter_separado_de_su_aplicacion(trazas):
    """
    NOR-MEM-01: lo que la FUENTE hace con el numero y lo que el PROYECTO hace
    con el son dos campos, y fundirlos fabrica exigencias que la norma no
    escribio. La traza los sirve como dos lineas.
    """
    comprobados = 0
    for detalle in _detalles(trazas):
        u = detalle.paso.umbral
        if u is None:
            assert _linea(detalle, tp.ROTULO_UMBRAL) is None
            continue
        assert _linea(detalle, tp.ROTULO_UMBRAL) is not None
        caracter = _linea(detalle, tp.ROTULO_CARACTER)
        aplicacion = _linea(detalle, tp.ROTULO_APLICACION)
        assert caracter is not None and caracter.texto == u.caracter
        assert aplicacion is not None and aplicacion.texto == u.aplicacion
        comprobados += 1
    assert comprobados


def test_el_veredicto_llega_con_su_margen(trazas):
    import math
    comprobados = 0
    for detalle in _detalles(trazas):
        v = detalle.paso.veredicto
        if v is None:
            continue
        linea = _linea(detalle, tp.ROTULO_VEREDICTO)
        assert linea is not None
        if v.tipo is TipoDeVeredicto.CUMPLE:
            assert linea.texto.startswith(M11.MARCA_CUMPLE)
        elif v.tipo is TipoDeVeredicto.NO_CUMPLE:
            assert linea.texto.startswith(M11.MARCA_INCUMPLE)
        if isinstance(v.margen, float) and math.isfinite(v.margen):
            assert "margen" in linea.texto, detalle.codigo
            comprobados += 1
    assert comprobados


# ===========================================================================
# Los tres registros separados (NOR-HID-04) y las discrepancias del registro
# ===========================================================================

def test_las_citas_van_en_el_registro_de_fuente_y_salen_del_registro(
        trazas, reg):
    """
    Toda linea del registro FUENTE lleva la transcripcion del registro
    normativo --- nunca una segunda transcripcion a mano (§4.5) --- y toda
    cita textual del paso llega.
    """
    comprobadas = 0
    for detalle in _detalles(trazas):
        lineas_fuente = [l for l in detalle.lineas
                         if l.registro == tp.REGISTRO_FUENTE]
        assert len(lineas_fuente) == len(detalle.paso.citas_textuales)
        for cita_id, linea in zip(detalle.paso.citas_textuales,
                                  lineas_fuente):
            c = reg.cita(cita_id)
            literal = getattr(c.texto_literal, "texto", "")
            assert literal in linea.texto
            assert c.como_texto() in linea.texto
            comprobadas += 1
    assert comprobadas


def test_las_discrepancias_son_las_de_la_vista_del_registro(trazas, reg):
    """
    La traza consume `Registro.discrepancias_que_tocan` sobre las MISMAS
    cuatro puertas que M11 (`citas_en_que_descansa`): ni una mas, ni una
    menos, y siempre en el registro de INTERPRETACION --- una discrepancia es
    lo que el proyecto lee, no lo que la fuente dice.
    """
    alguna = False
    for detalle in _detalles(trazas):
        esperadas = {d.id for d in reg.discrepancias_que_tocan(
            M11.citas_en_que_descansa(detalle.paso),
            getattr(detalle.paso, "discrepancias", ()))}
        lineas = [l for l in detalle.lineas
                  if l.rotulo == tp.ROTULO_DISCREPANCIA]
        vistas = set()
        for linea in lineas:
            assert linea.registro == tp.REGISTRO_INTERPRETACION
            vistas.add(linea.texto.split(" - ")[0])
        assert vistas == esperadas, detalle.codigo
        alguna = alguna or bool(esperadas)
    assert alguna, ("ningun paso de la corrida toca una discrepancia: el "
                    "test no probo el cruce")


def test_los_tres_registros_aparecen_y_no_se_funden(trazas):
    registros_vistos = {l.registro for e in _entradas(trazas)
                        for l in e.lineas}
    assert registros_vistos == LOS_TRES_REGISTROS


# ===========================================================================
# La guardia de AST, calcada de la que barre M11 (SIS-A-07)
# ===========================================================================

def test_traza_punto_no_hace_aritmetica_sobre_magnitudes():
    """
    El mismo contrato que M11 y la misma guardia
    (`test_memoria_sustentada.test_M11_no_calcula_y_sobre_D`, de donde esta
    calcada): la capa de contenido formatea la traza que el calculo emitio,
    no la recalcula. Una division entre atributos en este archivo es una
    magnitud partida por otra --- el segundo motor de calculo sin tests que
    SIS-A-07 denuncia.
    """
    import ast

    RUTAS = {"RAIZ", "SRC", "DIR_PLANTILLAS", "DIR_DOCS"}
    fuente = (SRC / "traza_punto.py").read_text(encoding="utf-8")

    def _es_ruta(nodo) -> bool:
        if isinstance(nodo, ast.Name):
            return nodo.id in RUTAS
        if isinstance(nodo, ast.Attribute):
            return nodo.attr in {"parent", "parents"}
        if isinstance(nodo, ast.BinOp) and isinstance(nodo.op, ast.Div):
            return _es_ruta(nodo.left)
        return False

    divisiones = [n for n in ast.walk(ast.parse(fuente))
                  if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)]
    sospechosas = [ast.unparse(n) for n in divisiones
                   if not _es_ruta(n.left) and not isinstance(n.left, ast.Call)]
    assert not sospechosas, (
        "traza_punto volvio a hacer aritmetica sobre magnitudes: la capa de "
        "contenido formatea la traza que el calculo emitio, no la recalcula. "
        f"{sospechosas}")
