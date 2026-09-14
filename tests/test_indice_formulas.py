"""
tests/test_indice_formulas.py
=============================
La guardia de `docs/indice_formulas.md`, el indice de formulas GENERADO desde
los `PasoDeMemoria` de la corrida de referencia (sesion I4).

Calcado de `test_manifiesto_citas.test_T8_el_indice_del_registro_esta_
sincronizado`, y por la misma razon: un documento que describe el calculo y
que nadie regenera envejece con el commit siguiente sin que nada falle. Aqui
el documento se regenera a memoria y se compara con el que esta en disco; si
difieren, NO se edita a mano:

    python3 src/indice_formulas.py --escribir --suite "<N passed, M skipped (entorno)>"

Lo que ademas se vigila, porque es lo que puede envejecer solo:

  1. que el SELLO lleve fecha, commit y par de la suite --- la regla de
     sellos de los planes T3 e I4 ---, y que el test compare el CUERPO, no
     la fecha: el sello se lee del documento y se pasa al generador.
  2. que el modulo emisor de cada paso se LOCALICE: la derivacion es por
     AST sobre `paso("<id>", ...)`, y un `paso()` cuyo id no sea literal la
     deja ciega. Se exige que todos lo sean.
  3. que el recorrido del grafo recoja al menos los pasos que M11 publica
     (`traza_punto`): es la comprobacion de que la vista del indice no se
     queda corta frente a la memoria.
  4. que los huecos del indice sean exactamente los del censo
     `SIN_FUNDAMENTO`, repartidos entre los que la corrida emitio y los que
     no alcanzo, sin omitir ninguno.
  5. que el generador no haga aritmetica sobre magnitudes, con la misma
     guardia que M11 y `traza_punto` (SIS-A-07).
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
for ruta in (str(RAIZ), str(SRC)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

import indice_formulas as ind                                      # noqa: E402
import traza_punto as tp                                           # noqa: E402
from modulos import M11_reporte as M11                             # noqa: E402


@pytest.fixture(scope="module")
def informe():
    return ind.corrida_de_referencia()


@pytest.fixture(scope="module")
def pasos(informe):
    return ind.pasos_de_la_corrida(informe)


@pytest.fixture(scope="module")
def texto_en_disco():
    assert ind.INDICE_FORMULAS.exists(), (
        "falta docs/indice_formulas.md: generalo con "
        "python3 src/indice_formulas.py --escribir --suite \"...\"")
    return ind.INDICE_FORMULAS.read_text(encoding="utf-8")


# ===========================================================================
# 1. Sincronia y sello
# ===========================================================================

def test_el_indice_de_formulas_esta_sincronizado(informe, texto_en_disco):
    """
    Se regenera con el sello que el documento YA lleva: lo que se compara es
    el cuerpo --- filas, huecos, fundamentos sin ejercitar ---, no la fecha
    ni el commit, que cambian cada vez que alguien regenera.
    """
    sello = ind.leer_sello(texto_en_disco)
    assert sello is not None, "el indice en disco no lleva un sello legible"
    assert ind.indice_de_formulas(informe, sello) == texto_en_disco, (
        "el indice de formulas esta desincronizado. NO se edita a mano: "
        "python3 src/indice_formulas.py --escribir --suite \"<par de la suite>\"")


def test_el_sello_lleva_fecha_commit_y_par_de_la_suite(texto_en_disco):
    """
    La regla de sellos pide las tres cosas. El par se exige con la forma
    `N passed, M skipped`, que es como CLAUDE.md manda citar el conteo: un
    solo numero no dice cuanto de la suite corrio en ese entorno.
    """
    sello = ind.leer_sello(texto_en_disco)
    assert sello is not None
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", sello.fecha), sello.fecha
    assert re.match(r"[0-9a-f]{7,40}", sello.commit), sello.commit
    assert re.search(r"\d+ passed, \d+ skipped", sello.suite), (
        f"el sello tiene que llevar el PAR de la suite: {sello.suite!r}")


def test_leer_sello_recupera_lo_que_linea_escribe():
    sello = ind.Sello("2026-09-14", "abc1234", "1910 passed, 4 skipped (x)")
    assert ind.leer_sello("cabecera\n" + sello.linea + "\ncuerpo") == sello


def test_un_sello_sin_uno_de_sus_tres_campos_no_se_construye():
    for campos in (("", "abc1234", "1 passed, 0 skipped"),
                   ("2026-09-14", " ", "1 passed, 0 skipped"),
                   ("2026-09-14", "abc1234", "")):
        with pytest.raises(ValueError):
            ind.Sello(*campos)


def test_escribir_sin_el_par_de_la_suite_no_toca_el_documento(texto_en_disco):
    """`--escribir` sin `--suite` se niega: el par no se inventa."""
    assert ind.main(["--escribir"]) == 2
    assert ind.INDICE_FORMULAS.read_text(encoding="utf-8") == texto_en_disco


# ===========================================================================
# 2. El modulo emisor, derivado del AST
# ===========================================================================

def _llamadas_a_paso_en_modulos():
    for ruta in sorted(ind.MODULOS.glob("*.py")):
        arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=ruta.name)
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, ast.Call):
                continue
            funcion = nodo.func
            nombre = (funcion.id if isinstance(funcion, ast.Name)
                      else funcion.attr if isinstance(funcion, ast.Attribute)
                      else None)
            if nombre == "paso":
                yield ruta.stem, nodo


def test_todo_paso_del_pipeline_pasa_su_fundamento_como_literal():
    """
    La derivacion del emisor solo ve `paso("F4.MANNING", ...)`. Un
    `paso(fundamento_id, ...)` con el id en una variable la dejaria ciega y
    el indice imprimiria «emisor no localizado». Se exige el literal.
    """
    opacos = [f"{modulo}: {ast.unparse(nodo)[:60]}"
              for modulo, nodo in _llamadas_a_paso_en_modulos()
              if not nodo.args
              or not isinstance(nodo.args[0], ast.Constant)
              or not isinstance(nodo.args[0].value, str)]
    assert not opacos, f"llamadas a paso() sin id literal: {opacos}"


def test_todo_paso_de_la_corrida_tiene_emisor_localizado(pasos):
    emisores = ind.emisores_por_fundamento()
    sin_emisor = sorted({p.fundamento_id for p in pasos} - set(emisores))
    assert not sin_emisor, sin_emisor
    for paso in pasos:
        assert "no localizado" not in ind.emisor_de(paso, emisores)


def test_el_emisor_es_el_modulo_que_llama_a_paso_y_no_el_que_transporta(pasos):
    """
    Los pasos de Fase 3 los EMITE M2 y llegan a la memoria por la tupla que
    M4 devuelve (`material.pasos`). El emisor es quien llama a `paso()`, no
    quien lo transporta: la atribucion por AST lo distingue, y la de
    `PasoDeMemoria.fase` no podria.
    """
    emisores = ind.emisores_por_fundamento()
    assert emisores["F3.CELDAS"] == ("M2_material",)
    assert emisores["F4.MANNING"] == ("M4_control",)
    assert emisores["F1.TW"] == ("M3_hidraulica",)
    assert emisores["F5.V1"] == ("M5_verificaciones",)


def test_las_menciones_encuentran_las_puertas_que_no_son_paso():
    """
    `F5.V7_FILA` entra por `eleccion()` desde M5 y `F3.D_MIN` por el bloque
    fijo de umbrales de `constantes_normativas`: el §4 del indice los
    imprime con esa puerta en vez de decir «sin emisor».
    """
    menciones = ind.menciones_del_fundamento()
    assert "M5_verificaciones" in menciones["F5.V7_FILA"]
    assert "constantes_normativas" in menciones["F3.D_MIN"]


# ===========================================================================
# 3. El recorrido del grafo no se queda corto frente a la memoria
# ===========================================================================

def test_el_recorrido_recoge_todo_paso_que_la_memoria_publica(informe, pasos):
    recogidos = {id(p) for p in pasos}
    publicados = 0
    for informe_punto in informe.puntos:
        for seccion in tp.traza_del_punto(informe_punto).secciones:
            for entrada in seccion.entradas:
                if isinstance(entrada, tp.DetalleDePaso):
                    publicados += 1
                    assert id(entrada.paso) in recogidos, (
                        entrada.codigo, entrada.titulo)
    assert publicados > 0


def test_cada_paso_se_recoge_una_sola_vez(pasos):
    assert len({id(p) for p in pasos}) == len(pasos)


def test_una_fila_por_formula_distinta_y_las_emisiones_suman_los_pasos(pasos):
    filas = ind.filas_del_indice(pasos, ind.emisores_por_fundamento())
    assert len({f.firma for f in filas}) == len(filas)
    assert sum(f.emisiones for f in filas) == len(pasos)
    # Las firmas de la corrida de referencia son al menos las de la cadena
    # hidraulica: si M4 dejara de emitir alguna, el indice lo diria.
    fundamentos = {f.fundamento_id for f in filas}
    assert {"F4.SECCION", "F4.MANNING", "F4.YC_RECT", "F4.FORMA_HDS5",
            "F4.CONTROL", "F4.HO", "F5.V1", "F5.V2", "F5.V2b", "F5.V3",
            "F5.V4", "F1.TW", "F2.LUZ", "F2.TR"} <= fundamentos


def test_las_filas_conservan_el_orden_de_la_memoria_dentro_de_cada_fase(pasos):
    """Seccion antes que Manning; entrada antes que salida; V1 antes que V4."""
    filas = ind.filas_del_indice(pasos, ind.emisores_por_fundamento())
    ids = [f.fundamento_id for f in filas]
    assert ids.index("F4.SECCION") < ids.index("F4.MANNING") \
        < ids.index("F4.YC_RECT") < ids.index("F4.HO")
    assert ids.index("F5.V1") < ids.index("F5.V4")


# ===========================================================================
# 4. Los huecos: los del censo, ni uno mas ni uno menos
# ===========================================================================

def test_los_huecos_del_indice_son_exactamente_los_del_censo(texto_en_disco):
    censo = set(M11.sin_fundamento_por_codigo())
    seccion = texto_en_disco.split("## 3. ")[1].split("## 4. ")[0]
    listados = set(re.findall(r"^- \*\*`([A-Za-z0-9]+)`\*\* — ", seccion,
                              flags=re.M))
    assert listados == censo, (listados ^ censo)


def test_los_huecos_emitidos_son_los_que_traza_punto_construye(informe,
                                                              texto_en_disco):
    emitidos = set()
    for informe_punto in informe.puntos:
        for seccion in tp.traza_del_punto(informe_punto).secciones:
            for entrada in seccion.entradas:
                if isinstance(entrada, tp.HuecoDeVerificacion):
                    emitidos.add(entrada.codigo)
    assert "V4b" in emitidos
    parte_31 = texto_en_disco.split("### 3.1 ")[1].split("### 3.2 ")[0]
    assert set(re.findall(r"^- \*\*`([A-Za-z0-9]+)`\*\*", parte_31,
                          flags=re.M)) == emitidos


def test_hueco_censado_construye_la_misma_ficha_que_la_traza():
    censo = M11.sin_fundamento_por_codigo()
    for codigo, (por_que, que_haria_falta) in censo.items():
        hueco = tp.hueco_censado(codigo)
        assert hueco.codigo == codigo
        assert hueco.por_que == por_que
        assert hueco.que_haria_falta == que_haria_falta
        assert hueco.titulo == tp.TITULO_HUECO
    with pytest.raises(KeyError):
        tp.hueco_censado("V-inexistente")


def test_los_fundamentos_no_ejercitados_son_el_complemento(pasos,
                                                            texto_en_disco):
    from normativa.registro import construir
    declarados = {f.id for f in construir().fundamentos}
    emitidos = {p.fundamento_id for p in pasos}
    seccion = texto_en_disco.split("## 4. ")[1]
    listados = set(re.findall(r"^\| `(F[^`]+)` \|", seccion, flags=re.M))
    assert listados == declarados - emitidos


# ===========================================================================
# 5. El generador formatea, no calcula (SIS-A-07)
# ===========================================================================

def test_el_generador_no_hace_aritmetica_sobre_magnitudes():
    """
    La misma guardia que `test_M11_no_calcula_y_sobre_D` y que
    `test_traza_punto_no_hace_aritmetica_sobre_magnitudes`: una division en
    un modulo de vista es una magnitud partida por otra, salvo que sea una
    ruta. El indice imprime formulas y procedencias, nunca numeros.
    """
    RUTAS = {"RAIZ", "SRC", "MODULOS"}
    fuente = (SRC / "indice_formulas.py").read_text(encoding="utf-8")

    def _es_ruta(nodo) -> bool:
        if isinstance(nodo, ast.Name):
            return nodo.id in RUTAS
        if isinstance(nodo, ast.Attribute):
            return nodo.attr in {"parent", "parents"}
        if isinstance(nodo, ast.BinOp) and isinstance(nodo.op, ast.Div):
            return _es_ruta(nodo.left)
        return False

    arbol = ast.parse(fuente)
    divisiones = [n for n in ast.walk(arbol)
                  if isinstance(n, ast.BinOp)
                  and isinstance(n.op, (ast.Div, ast.Mult, ast.Pow))]
    sospechosas = [ast.unparse(n) for n in divisiones if not _es_ruta(n.left)]
    assert not sospechosas, sospechosas


def test_el_indice_no_imprime_los_valores_de_la_corrida(pasos, texto_en_disco):
    """
    Los numeros de la corrida son de la memoria. Se comprueba sobre el
    producto: ningun valor de resultado de los pasos aparece en el indice
    con la forma en que `Magnitud.texto` lo escribe.
    """
    cuerpo = texto_en_disco.split("## 2. ")[1].split("## 3. ")[0]
    for paso in pasos:
        r = paso.resultado
        if isinstance(r.valor, float) and r.cifras is not None:
            assert f"{r.valor:.{r.cifras}f} {r.unidad}".strip() not in cuerpo, (
                paso.codigo, r.simbolo)
