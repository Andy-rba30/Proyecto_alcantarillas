"""
tests/test_t11_validacion_integral.py
=====================================
La aceptacion de T-11 de la cadena T: la VALIDACION INTEGRAL de las tres
familias.

Lo que fija, punto por punto del prompt (y de PRECISIONES_T-11):

1. Con el juego de datos de prueba COMPLETO
   (`tests/fixtures/juego_validacion_integral.py`, rotulado «DATOS DE
   PRUEBA, NO DEL PROYECTO»), los cuatro puntos del fixture llegan a la Fase
   11 con diseño a `--alcance expediente` (A y B circulares, C marco), por
   la CLI real y por el servicio; sin el juego, cada bloqueo cae en una de
   las tres clases de PRECISIONES_T-11; ninguna corrida de la validacion
   (completa, por defecto, una entrada quitada, variantes) deja salir una
   excepcion fuera de `ErrorProyecto`; la lista exacta de lo que sigue
   requiriendo entrada esta nombrada en `docs/contrato_entradas.md`; y
   `docs/validacion_integral.md` esta sincronizado con el programa.
2. (validacion externa: `tests/test_t11_validacion_externa.py`).
3. (sensibilidad: `tests/test_t11_sensibilidad.py`).
4. El censo final: ningun criterio de perfil sin valor salvo los que
   esperan una entrada, ninguna `assert`/`AssertionError`/
   `NotImplementedError` en los modulos de calculo, y
   `M9.FUNCIONES_SIN_CONSUMIDOR` sin llamador de produccion.

NO SE ESCRIBIO EN ROJO PRIMERO, y se dice: T-11 valida, no cambia calculo,
y casi todo lo que estos tests fijan es comportamiento que ya existia y que
la validacion MIDE; el rojo de lo nuevo (el juego, el documento, el
alcance declarado) se midio contra la base `14f6138` con el archivo final
(el numero, en el informe de la FASE A). El unico defecto que la validacion
destapo quedo reproducido en `xfail(strict=True)` y lo corrigio la sesion
de T11-03 (ficha T11-03; `tests/test_t11_no_factible_por_rasante.py`): el
test de la seccion 1d ya no es un `xfail`.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src.modelos import TipoDeBloqueo
from src.modulos import M9_cabezal as M9
from tests.apoyo import validacion_integral as V
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.fixtures import juego_validacion_integral as J

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"

# Correcciones de T-11: el HW del marco con la entrada en el canal frente al
# del juego cambia en la cuarta cifra (0.62307 frente a 0.62309 m): se
# compara a la decima de milimetro.
ABS_HW_DE_LA_VARIANTE_M = 1e-4
# La cuenta a mano de Manning en el canal se hace con tres cifras (0.662,
# 0.415, 0.0775): el 1 % es su redondeo.
REL_MANNING_A_MANO = 0.01


# ===========================================================================
# Las corridas, una vez por modulo
# ===========================================================================

@pytest.fixture(scope="module")
def base():
    return V.correr_juego()


@pytest.fixture(scope="module")
def por_defecto():
    return V.correr(None)


@pytest.fixture(scope="module")
def una(base):
    return V.quitar_una(base)


@pytest.fixture(scope="module")
def variantes(base):
    return {nombre: (texto, informe, ef)
            for nombre, texto, informe, ef in V.variantes(base)}


@pytest.fixture(scope="module")
def titular(variantes):
    """La corrida TITULAR (H2): el juego con las decisiones de archivo."""
    return variantes[V.VARIANTE_TITULAR][1]


@pytest.fixture(scope="module")
def una_titular(titular):
    return V.quitar_una_en_la_titular(titular)


@pytest.fixture(scope="module")
def q_extremo():
    return V.sensibilidad_q_extremo_A01()


def _punto(informe, id_punto):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


# ===========================================================================
# 0. El juego es de prueba y no toca los tres archivos de valores
# ===========================================================================

def test_el_juego_se_rotula_datos_de_prueba():
    assert J.__doc__.lstrip().startswith(J.ROTULO)
    assert J.ROTULO == "DATOS DE PRUEBA, NO DEL PROYECTO"
    for clave, d in J.SITIO.items():
        assert J.ROTULO in d["trazabilidad"], clave
    # Las dos entradas de hidrologia que reutiliza llevan su propio rotulo.
    for ruta in (J.CUENCAS, J.ESTACION):
        assert ruta.read_text(encoding="utf-8").startswith(f"# {J.ROTULO}")


def test_ningun_vacio_del_proyecto_se_relleno_en_los_archivos_de_valores():
    """
    PRECISIONES_T-11: los criterios y [S] que el dueño dejo sin valor siguen
    sin valor; el juego los declara SOLO por la puerta. Lo que el juego
    declara sobre un criterio CON valor de archivo (dos decisiones de
    proyectista y Propietario) no movio el archivo.
    """
    sin_valor_que_el_juego_declara = {
        "remanso_derecho_via", "TR_evento_extremo",
        "umbral_no_colapso_evento_extremo", "phi_relleno_trasdos",
        "c_phi_fundacion", "peso_especifico_saturado_relleno_kn_m3",
        "categoria_refuerzo_aashto", "clase_exposicion_fisuracion_cabezal",
        "exposicion_quimica_ems", "homogeneidad_serie_fen"}
    assert sin_valor_que_el_juego_declara <= set(J.DECLARACIONES)
    for clave in sin_valor_que_el_juego_declara:
        assert ca.CRITERIOS[clave].valor is None, clave
    assert ca.CRITERIOS["drenaje_trasdos"].valor == "sin_drenaje"
    assert ca.CRITERIOS["factor_muro_eleccion"].valor == "sin_reduccion"
    for clave in J.SITIO:
        assert ds.DATOS_SITIO[clave].valor is None, clave


def test_el_juego_solo_entra_por_las_puertas_de_la_cli(tmp_path):
    e = V.materializar(V.juego_completo(), tmp_path)
    args = V.argumentos_cli(e)
    assert args[:3] == [str(e.csv), "--alcance", "expediente"]
    assert "--datos-externos" in args and "--datos-sitio" in args
    assert "--cuencas" in args and "--estacion" in args
    assert args.count("--declarar") == len(J.DECLARACIONES)
    # El CSV es una COPIA del fixture con las celdas del juego y nada mas:
    # CELDA A CELDA (correcciones de T-11, H13: comparaba solo la cabecera y
    # el numero de lineas, y un cambio de otra celda pasaba).
    import csv as _csv
    original = list(_csv.reader((RAIZ / "tests" / "ejemplo_puntos.csv")
                                .read_text(encoding="utf-8").splitlines()))
    copia = list(_csv.reader(e.csv.read_text(encoding="utf-8").splitlines()))
    assert copia[0] == original[0]
    assert len(copia) == len(original)
    cabecera = original[0]
    for fo, fc in zip(original[1:], copia[1:]):
        assert fo[0] == fc[0]
        for columna, vo, vc in zip(cabecera, fo, fc):
            esperado = J.CELDAS.get((fo[0], columna), vo)
            assert vc == esperado, (fo[0], columna, vo, vc)


# ===========================================================================
# 1. La corrida completa llega a la Fase 11 con diseño en las tres familias
# ===========================================================================

DISENO_ESPERADO = {
    # Los mismos diametros y la misma seccion que la linea base: el juego no
    # mueve ninguno (A-01 y A-02, Ø 0.90 de la linea base; C-01, el marco
    # 1.20 x 0.90 de la corrida 6; B-01 dimensiona con el TW de la guia).
    "A-01": ("A", "Concreto reforzado", "Ø 0.90 m"),
    "A-02": ("A", "Concreto reforzado", "Ø 0.90 m"),
    "B-01": ("B", "Concreto reforzado", "Ø 0.90 m"),
    "C-01": ("C", "Concreto reforzado", "marco 1.20 × 0.90 m"),
}


def test_las_tres_familias_llegan_a_la_fase_11_con_diseno(base):
    fase11 = V.llega_a_la_fase_11(base)
    for p in base.puntos:
        r = V.resumen_del_punto(base, p)
        assert (r["familia"], r["material"], r["seccion"]) == \
            DISENO_ESPERADO[r["id"]], r["id"]
        assert r["dimensionado"], r["id"]
        assert fase11[r["id"]] == (True, True), r["id"]


def test_el_unico_bloqueo_de_la_corrida_completa_es_un_alcance_con_ficha(base):
    """
    Con el juego completo no queda ningun bloqueo por entrada ni por
    criterio: el unico es el ALCANCE del requisito de la Sec. 2.3 en C-01
    (la rasante hidraulica del canal no se mide; ficha VC1-01), que el punto
    lleva aunque dimensione.
    """
    bloqueos = V.todos_los_bloqueos(base)
    assert [(b.punto, b.clase, b.que) for b in bloqueos] == [
        ("C-01", V.CLASE_METODO, "VC1-01")]
    assert _punto(base, "C-01").bloqueos[0].tipo \
        is TipoDeBloqueo.DIFERIDO_POR_ALCANCE


def test_B01_corre_con_el_TW_de_la_guia_y_el_tramo_declarado(base):
    """El juego decide el TW de B-01 (0.30 m) y su tramo (150 m), y lo dice."""
    assert J.EXTERNOS["globales"]["TW_m"] == pytest.approx(0.3, rel=REL_TRANSPORTE)
    assert "TW_m" not in J.EXTERNOS["puntos"]["B-01"]
    assert J.EXTERNOS["puntos"]["B-01"]["inicio_tramo_cuneta_km"] == \
        pytest.approx(2.3, rel=REL_TRANSPORTE)
    v = V.verificaciones_del_punto(base, "B-01")
    assert v["VB1"] == "cumple" and v["VB2"] == "cumple"
    assert v["V2"] == "cumple"


def test_el_cabezal_de_la_regla_no_pasa_E3_estatico_ni_E1_sismico(base):
    """
    UN RESULTADO, NO UN FALLO DE LA VALIDACION (PRECISIONES_T-11): con la
    zapata que propone la regla de T-7a, el deslizamiento estatico y la
    capacidad portante sismica del marco LRFD no pasan en ningun punto. La
    variante `zapata_declarada_3m` muestra el otro lado.
    """
    for p in base.puntos:
        v = V.verificaciones_del_punto(base, p.punto.id)
        assert v["E3-LRFD.est.e"] == "no cumple", p.punto.id
        assert v["E1-LRFD.sis.e"] == "no cumple", p.punto.id


@pytest.mark.lento
def test_la_cli_real_dice_lo_mismo_que_el_servicio(base, tmp_path):
    """La puerta real: `cli.py` en subproceso con los archivos materializados."""
    e = V.materializar(V.juego_completo(), tmp_path / "juego")
    destino = tmp_path / "informe.json"
    proc = subprocess.run(
        [sys.executable, str(RAIZ / "cli.py"), *V.argumentos_cli(e),
         "--json", str(destino), "--html", str(tmp_path / "memoria.html"),
         "--csv-resumen", str(tmp_path / "resumen.csv")],
        cwd=RAIZ, capture_output=True, text=True, timeout=600)
    assert proc.returncode in (0, 1), proc.stderr[-2000:]
    assert "Traceback" not in proc.stderr
    volcado = json.loads(destino.read_text(encoding="utf-8"))
    propio = V.volcado(base)
    for a, b in zip(volcado["puntos"], propio["puntos"]):
        assert a["id"] == b["id"]
        assert a["dimensionado"] and b["dimensionado"]
        assert a["diseno"] == b["diseno"], a["id"]
        assert {v["codigo"]: v["estado"] for v in a["verificaciones"]} == \
            {v["codigo"]: v["estado"] for v in b["verificaciones"]}
    html = (tmp_path / "memoria.html").read_text(encoding="utf-8")
    # El bloque de cada punto, por su ancla (correcciones de T-11, H13: la
    # segunda mitad, `or id_punto in html`, era siempre cierta).
    from src.modulos import M11_reporte as M11
    for id_punto in DISENO_ESPERADO:
        assert f'id="{M11.ancla_de_punto(id_punto)}"' in html, id_punto


# ===========================================================================
# 1b. Sin el juego, y con una entrada quitada: tres clases y ninguna excepcion
# ===========================================================================

def test_sin_juego_cada_bloqueo_cae_en_una_de_las_tres_clases(por_defecto):
    bloqueos = V.todos_los_bloqueos(por_defecto)
    assert bloqueos
    assert {b.clase for b in bloqueos} <= {V.CLASE_ENTRADA, V.CLASE_CRITERIO,
                                           V.CLASE_METODO}
    # Sin juego, ningun punto pasa de la luz.
    for p in por_defecto.puntos:
        assert not p.dimensionado
        assert any(b.campo == "luz_m" for b in p.bloqueos)


def test_ninguna_corrida_de_la_validacion_saca_una_excepcion_fuera_de_ErrorProyecto(
        una, variantes):
    """
    Cada corrida de §4 y §5 TERMINO (si una excepcion fuera de
    `ErrorProyecto` hubiera salido de una etapa, `servicio.correr` no
    habria devuelto informe) y cada bloqueo se clasifico (`clasificar`
    lanza `ValueError` ante un tipo fuera de las clases).
    """
    assert len(una) == len(V.elementos_del_juego())
    assert set(variantes) == set(J.VARIANTES)
    for _el, ef in una:
        for b in ef.bloqueos_nuevos:
            assert b.clase in (V.CLASE_ENTRADA, V.CLASE_CRITERIO,
                               V.CLASE_METODO, V.CLASE_NO_FACTIBLE)


def test_cada_metodo_no_evaluable_nombra_una_ficha_que_existe(una, variantes,
                                                              base):
    texto = V.DECISIONES.read_text(encoding="utf-8")
    fichas = {b.que for _el, ef in una for b in ef.bloqueos_nuevos
              if b.clase == V.CLASE_METODO}
    fichas |= {b.que for _t, _i, ef in variantes.values()
               for b in ef.bloqueos_nuevos if b.clase == V.CLASE_METODO}
    fichas |= {b.que for b in V.todos_los_bloqueos(base)
               if b.clase == V.CLASE_METODO}
    assert fichas == {"T7B-05", "T7B-06", "T7C-03", "VC1-01"}
    for ficha in fichas:
        assert f"## {ficha} · " in texto, ficha


def _tabla_de_la_seccion_7_del_contrato():
    """
    Los nombres de la primera columna de la tabla de la §7 del contrato
    («La lista exacta…»), en su orden: la primera celda de cada fila de la
    tabla, entre backticks.
    """
    texto = V.CONTRATO.read_text(encoding="utf-8")
    inicio = texto.index("## 7. La lista exacta")
    nombres = []
    en_tabla = False
    for linea in texto[inicio:].splitlines():
        if linea.startswith("| Entrada |"):
            en_tabla = True
            continue
        if en_tabla:
            if not linea.startswith("|"):
                break
            if linea.startswith("|---"):
                continue
            primera = linea.split("|")[1].strip()
            assert primera.startswith("`") and primera.endswith("`"), linea
            nombres.append(primera.strip("`"))
    return nombres


def test_la_lista_exacta_esta_nombrada_en_el_contrato_de_entradas(
        por_defecto, una, una_titular):
    """
    PRECISIONES_T-11, punto 1: la lista exacta y el contrato de entradas
    «deben decir lo mismo». La §7 del contrato es esa lista, escrita a mano
    con quien la debe; este test exige que nombre EXACTAMENTE las entradas
    que la medida dice --ni una de mas, ni una de menos-- y que cada una
    este ademas en el cuerpo del contrato fuera de la §7. Desde las
    correcciones de T-11 (H1, ALTA) la medida es sobre DOS BASES --el juego
    y el juego con las decisiones de archivo--: sobre una sola, la §7 no
    nombraba el peso especifico saturado del relleno, que con el
    `drenaje_trasdos` de archivo detiene 24 etapas, y contradecia a la §3.3.
    """
    contrato = V.CONTRATO.read_text(encoding="utf-8")
    cuerpo = contrato[:contrato.index("## 7. La lista exacta")]
    lista = V.lista_exacta(por_defecto, una, una_titular)
    nombres = [n for n, _c, _d in lista]
    assert nombres == sorted(set(nombres))
    for nombre in nombres:
        assert f"`{nombre}`" in cuerpo, nombre
    seccion_7 = _tabla_de_la_seccion_7_del_contrato()
    assert len(seccion_7) == len(set(seccion_7))
    assert set(seccion_7) == set(nombres), (
        "la §7 de docs/contrato_entradas.md no dice lo mismo que la medida: "
        f"sobran {sorted(set(seccion_7) - set(nombres))}, "
        f"faltan {sorted(set(nombres) - set(seccion_7))}")
    # La clase que la §7 imprime es la que la medida da.
    clases = {n: c for n, c, _d in lista}
    texto = contrato[contrato.index("## 7. La lista exacta"):]
    for nombre in nombres:
        fila = next(l for l in texto.splitlines()
                    if l.startswith(f"| `{nombre}` |"))
        clase_impresa = fila.split("|")[2].strip()
        if clases[nombre] == V.CLASE_METODO:
            assert clase_impresa.startswith("método diferido"), fila
        elif clases[nombre] == V.CLASE_CRITERIO:
            assert clase_impresa == "criterio que se declara", fila
        else:
            assert clase_impresa.startswith("entrada del proyecto"), fila
    # Las cuatro clases de entrada que la cadena T prometio que quedarian
    # (cadena, §5): hidrologia del canal y del receptor, EMS, topografia,
    # trazo y decisiones del Propietario.
    assert {"luz_m", "NF_profundidad_m", "c_phi_fundacion", "phi_relleno_trasdos",
            "exposicion_quimica_ems", "Q_evento_extremo_m3s",
            "cota_coronacion_canal", "TR_evento_extremo",
            "remanso_derecho_via",
            # H1: la entrada que la segunda base destapa (ensayo del EMS).
            "peso_especifico_saturado_relleno_kn_m3"} <= set(nombres)
    # El γ saturado sale SOLO de la segunda base, y como entrada (ensayo).
    clases = {n: c for n, c, _d in lista}
    assert clases["peso_especifico_saturado_relleno_kn_m3"] == V.CLASE_ENTRADA
    assert "peso_especifico_saturado_relleno_kn_m3" not in {
        n for n, _c, _d in V.lista_exacta(por_defecto, una)}
    # Las condicionales que ninguna base dispara: nombradas en la §7, y la
    # frase que decia «lo que no esta aqui no detiene nada» ya no esta.
    seccion_7 = contrato[contrato.index("## 7. La lista exacta"):]
    for clave in V.CONDICIONALES_NO_MEDIDAS:
        assert f"`{clave}`" in seccion_7, clave
    assert "no detiene nada si falta" not in seccion_7
    assert "además de las columnas obligatorias" in seccion_7
    # La §7 no contradice a la §3.3: las dos nombran el γ saturado.
    s33 = contrato[contrato.index("### 3.3"):contrato.index("### 3.4")]
    assert "`peso_especifico_saturado_relleno_kn_m3`" in s33


def test_el_documento_de_validacion_esta_sincronizado(base, por_defecto, una,
                                                      variantes, titular,
                                                      una_titular, q_extremo):
    var = tuple((n, t, i, ef) for n, (t, i, ef) in variantes.items())
    texto = V.generar(base=base, por_defecto=por_defecto, una=una, var=var,
                      titular=titular, una_titular=una_titular,
                      q_extremo=q_extremo)
    assert V.DOCUMENTO.read_text(encoding="utf-8") == texto, (
        "docs/validacion_integral.md no esta sincronizado: "
        "python -m tests.apoyo.validacion_integral --escribir")


# ===========================================================================
# 1c. Las variantes: lo que el juego decidio, del otro lado
# ===========================================================================

def test_B01_con_el_TW_de_la_linea_base_no_dimensiona_por_V2(variantes):
    _t, informe, _ef = variantes["B01_tw_de_la_linea_base"]
    b01 = _punto(informe, "B-01")
    assert not b01.dimensionado
    volcado = V.volcado(informe)
    p = next(x for x in volcado["puntos"] if x["id"] == "B-01")
    assert any("V2" in (it.get("incumplidas") or []) for it in p["iteraciones"])


def test_B01_sin_inicio_de_tramo_no_cumple_VB1(variantes):
    _t, informe, ef = variantes["B01_sin_inicio_de_tramo"]
    assert V.verificaciones_del_punto(informe, "B-01")["VB1"] == "no cumple"
    assert ("B-01", "VB1", "cumple", "no cumple") in ef.veredictos


def test_las_variantes_que_dejan_un_metodo_sin_evaluar(variantes):
    def fichas(nombre):
        return {(b.punto, b.que) for b in variantes[nombre][2].bloqueos_nuevos}
    assert fichas("freatico_a_2m") == {("A-01", "T7B-06"), ("A-02", "T7B-06")}
    assert fichas("drenaje_de_archivo") == {(i, "T7B-05") for i in DISENO_ESPERADO}
    assert fichas("C01_lecho_cohesivo") == {("C-01", "T7B-06"), ("C-01", "T7C-03")}


def test_el_caudal_calculado_sin_tratamiento_FEN_detiene_por_el_criterio(variantes):
    """
    La condicional que el juego completo no dispara (contrato §7): con el
    caudal CALCULADO y sin `homogeneidad_serie_fen`, la Fase 1-bis se
    detiene en el criterio, y solo en los tres puntos que lo calculan.
    """
    _t, _informe, ef = variantes["caudal_calculado_sin_fen"]
    fen = {(b.punto, b.clase) for b in ef.bloqueos_nuevos
           if b.que == "homogeneidad_serie_fen"}
    assert fen == {(i, V.CLASE_CRITERIO) for i in ("A-01", "A-02", "B-01")}


def test_con_la_zapata_de_3m_el_cabezal_de_entrada_de_A01_pasa_entero(variantes):
    """
    MEDIDO, no supuesto: con la zapata declarada de 3.00 m (la prueba de
    T-7b), las doce filas E del cabezal de ENTRADA de A-01 pasan en los dos
    marcos. El de SALIDA, desplantado en el fondo de la hoya de socavacion,
    sigue sin pasar la capacidad portante sismica del marco LRFD: la zapata
    sola no lo resuelve.
    """
    _t, informe, _ef = variantes["zapata_declarada_3m"]
    v = V.verificaciones_del_punto(informe, "A-01")
    entrada = {k: e for k, e in v.items() if k.startswith("E") and k.endswith(".e")}
    assert len(entrada) == 12 and set(entrada.values()) == {"cumple"}
    assert v["E1-LRFD.sis.s"] == "no cumple"
    assert v["E3-LRFD.est.s"] == "cumple"


def test_ninguna_variante_mueve_un_diametro_que_dimensiona(variantes):
    """
    Lo que una variante cambia es un VEREDICTO o deja un punto sin diseño;
    ninguna lo lleva a OTRA seccion (parada c de la orquestacion: el juego no
    es un atajo para mover diametros).
    """
    for nombre, (_t, _informe, ef) in variantes.items():
        assert not ef.cambia_seccion, nombre


# ===========================================================================
# 1c-ter. Correcciones de T-11 (auditoria adversarial): la corrida titular,
# C-01 en el canal, el evento extremo, el censo del §6
# ===========================================================================

def test_la_corrida_titular_es_la_de_las_decisiones_de_archivo(titular):
    """
    H2 (MEDIA), con la resolucion del orquestador aceptada por el dueño: el
    resultado TITULAR del §2 es el de los valores de ARCHIVO. El juego pisa
    exactamente dos criterios con valor de archivo, cada uno con su razon
    escrita (`J.PISA_EL_ARCHIVO_PORQUE`), y la variante titular los deja en
    su valor. Con ellos los cuatro puntos dimensionan igual, las tres filas
    estaticas del marco LRFD no pasan en los ocho cabezales y la condicion
    sismica es «metodo no evaluable» (T7B-05) en los ocho.
    """
    pisadas = {k for k in J.DECLARACIONES if ca.CRITERIOS[k].valor is not None}
    assert pisadas == set(J.PISA_EL_ARCHIVO_PORQUE) == {
        "drenaje_trasdos", "factor_muro_eleccion"}
    assert [c for c, *_ in V.pisa_el_archivo()] == sorted(
        pisadas, key=list(J.DECLARACIONES).index)
    cambios = dict(((c[1], c[2]) for c in J.VARIANTES[V.VARIANTE_TITULAR][1]))
    assert cambios["drenaje_trasdos"] is None
    assert cambios["factor_muro_eleccion"] is None
    # El γ saturado de prueba, declarado por la puerta de los ensayos.
    assert cambios["peso_especifico_saturado_relleno_kn_m3"] == \
        pytest.approx(20.0, rel=REL_TRANSPORTE)
    for p in titular.puntos:
        r = V.resumen_del_punto(titular, p)
        assert (r["familia"], r["material"], r["seccion"]) == \
            DISENO_ESPERADO[r["id"]], r["id"]
    assert V.filas_estaticas_que_no_pasan(titular) == {
        "E1-LRFD.est": 8, "E2-LRFD.est": 8, "E3-LRFD.est": 8}
    bloqueos = [(b.punto, b.que) for b in V.todos_los_bloqueos(titular)]
    assert sorted(bloqueos) == sorted(
        [("C-01", "VC1-01")] + [(i, "T7B-05") for i in DISENO_ESPERADO] * 2)


def test_el_documento_presenta_primero_la_titular():
    """H2: el §2 del documento es la titular; el juego es su §2.1."""
    texto = V.DOCUMENTO.read_text(encoding="utf-8")
    i2 = texto.index("## 2. Corrida titular: el juego con las decisiones de archivo")
    i21 = texto.index("### 2.1 Variante que ejercita la cadena sísmica")
    assert i2 < i21
    for clave in J.PISA_EL_ARCHIVO_PORQUE:
        assert f"| `{clave}` |" in texto[i2:i21], clave


def test_C01_con_el_fondo_en_el_canal_empalma_y_el_marco_no_cambia(base,
                                                                  variantes):
    """
    H7 (MEDIA): con la regla de archivo (`origen_cota_fondo_entrada` =
    'cota_terreno') la salida de C-01 queda colgada sobre el canal y VC2
    avisa; con la entrada en el canal (variante `C01_fondo_en_el_canal`,
    36.30 msnm) VC2 y G2 cumplen, el remanso del canal concluye, y el marco
    y su HW son los mismos.
    """
    j = V._c01_en_el_canal(base)
    v = V._c01_en_el_canal(variantes["C01_fondo_en_el_canal"][1])
    assert j["VC2"] == "indicador" and j["desnivel"] > 0.5
    assert not j["remanso"]
    assert v["VC2"] == "cumple" and v["G2"] == "cumple" and v["remanso"]
    assert 0.0 <= v["desnivel"] <= 0.010
    assert v["seccion"] == j["seccion"] == "marco 1.20 × 0.90 m"
    assert v["HW"] == pytest.approx(j["HW"], abs=ABS_HW_DE_LA_VARIANTE_M)


def test_el_TW_de_C01_es_el_tirante_normal_del_canal_del_juego():
    """
    H7: el TW de C-01 (0.41 m) es el tirante normal del canal que el mismo
    juego declara (b 1.0, z 1.5, S 0.006, n 0.025, Q 0.85). Dorado a mano en
    la linea del juego: con y = 0.41, Manning da 0.85 m3/s.
    """
    c01 = J.EXTERNOS["puntos"]["C-01"]
    s = c01["seccion_receptor_medida"]
    y = c01["TW_m"]
    A = (s["b_m"] + s["z_HV"] * y) * y
    P = s["b_m"] + 2 * y * (1 + s["z_HV"] ** 2) ** 0.5
    Q = A * (A / P) ** (2 / 3) * s["S"] ** 0.5 / s["n"]
    assert Q == pytest.approx(c01["Q_m3s"], rel=REL_MANNING_A_MANO)


def test_el_caudal_extremo_de_A01_decide_su_diametro_por_V8(q_extremo):
    """
    H14 (BAJA): con el caudal del evento extremo de prueba (1.11 veces el de
    diseño) A-01 llega con Ø 0.90; el documento mide que de 1.8 veces en
    adelante pasa a Ø 1.05 por V8.
    """
    # Por posicion, en el orden de `FACTORES_Q_EXTREMO_A01` (1.5, 1.71, 1.8
    # y 2.0 veces el de diseño).
    assert len(q_extremo) == len(V.FACTORES_Q_EXTREMO_A01) == 4
    assert [(sec, inc) for _k, _q, sec, inc in q_extremo] == [
        ("Ø 0.90 m", "ninguna"), ("Ø 0.90 m", "ninguna"),
        ("Ø 1.05 m", "V8"), ("Ø 1.05 m", "V8")]


def test_el_censo_del_paragrafo_6_dice_que_criterio_no_tiene_consumidor():
    """
    H11 (BAJA): los criterios sin valor que ningun modulo consume salen en el
    §6 como «no (censado)», y son los del censo de `test_nivel_medido`
    (siete, que CLAUDE.md llamaba «ocho»). `TW_receptor` es un dato del
    receptor, no una decision.
    """
    from tests.test_nivel_medido import SIN_CONSUMIDOR_Y_SIN_MEDIDA
    assert set(V._sin_consumidor()) == set(SIN_CONSUMIDOR_Y_SIN_MEDIDA)
    assert len(SIN_CONSUMIDOR_Y_SIN_MEDIDA) == 7
    texto = V.DOCUMENTO.read_text(encoding="utf-8")
    seccion_6 = texto[texto.index("## 6. Criterios sin valor de archivo"):]
    no_censados = {l.split("|")[1].strip().strip("`")
                   for l in seccion_6.splitlines()
                   if l.startswith("| `") and "| no (censado) |" in l}
    assert no_censados == {k for k in SIN_CONSUMIDOR_Y_SIN_MEDIDA
                           if ca.CRITERIOS[k].valor is None}
    assert V._origen_del_criterio("TW_receptor").startswith("dato del receptor")


# ===========================================================================
# 1c-bis. La tercera corrida de referencia del indice de formulas (T10-02)
# ===========================================================================

def test_la_corrida_de_referencia_con_hidrologia_es_el_juego_materializado(
        tmp_path):
    """
    `tests/fixtures/corridas_de_referencia/hidrologia_calculada/` es la
    variante `caudal_calculado` del juego, escrita por
    `escribir_corrida_de_referencia`: los seis archivos versionados son,
    byte a byte, los que el juego produce hoy. Una copia que divergiera del
    juego haria del indice un documento de otra corrida.
    """
    from src import indice_formulas as ind
    corrida = next(c for c in ind.CORRIDAS_DE_REFERENCIA
                   if c.nombre == "hidrologia_calculada")
    assert corrida.carpeta == V.CORRIDA_DE_REFERENCIA
    assert corrida.alcance == "expediente"
    assert J.ROTULO in corrida.rotulo
    fresca = V.escribir_corrida_de_referencia(tmp_path / "fresca")
    nombres = sorted(x.name for x in V.CORRIDA_DE_REFERENCIA.iterdir())
    # El LEEME rotulado (correcciones de T-11, H12): tres de los seis no
    # admiten la cabecera, y la carpeta la lleva una vez.
    assert nombres == sorted(x.name for x in fresca.iterdir()) == [
        "LEEME.md", "cuencas.csv", "declaraciones.json", "estacion.csv",
        "externos.json", "puntos.csv", "sitio.json"]
    assert (V.CORRIDA_DE_REFERENCIA / "LEEME.md").read_text(
        encoding="utf-8").startswith(f"# {J.ROTULO}")
    for nombre in nombres:
        assert (V.CORRIDA_DE_REFERENCIA / nombre).read_bytes() == \
            (fresca / nombre).read_bytes(), nombre
    assert corrida.cuencas is not None and corrida.estacion is not None


def test_la_hidrologia_calculada_entra_al_indice_de_formulas():
    """
    Pregunta 3 de T-10 (decision del dueño): con la tercera corrida, los
    ocho fundamentos de la Fase 1-bis calculada tienen paso en el indice, y
    ninguno queda en el cuadro de «no ejercitados».
    """
    from src import indice_formulas as ind
    corrida = next(c for c in ind.CORRIDAS_DE_REFERENCIA
                   if c.nombre == "hidrologia_calculada")
    informe = ind.correr_referencia(corrida)
    fundamentos = {p.fundamento_id for p in ind.pasos_de_las_corridas([informe])}
    for f in ("FH.SERIE", "FH.AJUSTE", "FH.KS", "FH.FEN", "FH.TC",
              "FH.INTENSIDAD", "FH.C", "FH.RACIONAL"):
        assert f in fundamentos, f
    calculados = {p.punto.id for p in informe.puntos
                  if p.caudal is not None and p.caudal.calculado}
    assert calculados == {"A-01", "A-02", "B-01"}
    texto = ind.INDICE_FORMULAS.read_text(encoding="utf-8")
    cuadro_4 = texto[texto.index("## 4. Fundamentos que la corrida"):]
    assert "`FH." not in cuadro_4


# ===========================================================================
# 1d. El defecto que la validacion destapo, CORREGIDO (T11-03)
# ===========================================================================

def test_el_escalon_que_no_cabe_bajo_la_subrasante_es_no_factible_por_rasante():
    """
    T-11 lo dejo reproducido en `xfail(strict=True)` y lo corrigio la sesion
    de T11-03 (hallazgo H4 de su auditoria): sin `TW_m`, el TW de los
    escenarios acotados lleva a A-01 hasta Ø 1.80 m de concreto, donde la
    clave queda 0.025 m SOBRE la subrasante. Salia como `DatoInvalidoError`
    sobre 'cota_subrasante' --un dato que M0 acepto y que nadie cambio--, el
    material como «no evaluable» y el punto «no factible» sin
    `delta_rasante_m`. Ahora es no factible POR RASANTE, con el delta de 7.A
    del escalon que no cabe y cumple lo evaluado.

    Los dos dorados, a mano (fondo de entrada = terreno; pavimento flexible:
    h_rec = max(D/8 o Bc/8, 0.3048 m) = 0.3048 m; paquete 0.15 m):

      A-01  TMC Ø 1.95 m       42.10 + 1.95 + 0.01501 + 0.3048 + 0.15
                               - 44.20 = 0.31981 m  (el menor; el concreto
                               de Ø 1.80 m pide 0.3298 m)
      A-02  Concreto Ø 1.95 m  39.85 + 1.95 + 0.188 + 0.3048 + 0.15
                               - 42.00 = 0.4428 m   (el TMC de Ø 2.10 m
                               incumple V2 y no da delta)
    """
    informe = V.correr_juego(V.aplicar(V.juego_completo(),
                                       (("externo", "globales", "TW_m", None),)))
    b = _punto(informe, "A-01").bloqueos[0]
    assert b.tipo is TipoDeBloqueo.DISENO_NO_FACTIBLE
    assert "Dato invalido en 'cota_subrasante'" not in b.mensaje
    assert "material no evaluable" not in b.mensaje
    assert "NO FACTIBLE POR RASANTE" in b.mensaje
    assert "Ø 1.80 m no cabe bajo la subrasante" in b.mensaje
    assert b.delta_rasante_m == pytest.approx(
        42.10 + 1.95 + 0.01501 + 0.3048 + 0.15 - 44.20, rel=REL_TRANSPORTE)
    b = _punto(informe, "A-02").bloqueos[0]
    assert b.tipo is TipoDeBloqueo.DISENO_NO_FACTIBLE
    assert b.delta_rasante_m == pytest.approx(
        39.85 + 1.95 + 0.188 + 0.3048 + 0.15 - 42.00, rel=REL_TRANSPORTE)


# ===========================================================================
# 4. El censo final
# ===========================================================================

# Los criterios de PERFIL sin valor de archivo que no son opcionales, cada uno
# con la entrada del proyecto que lo destraba. Un criterio de perfil nuevo sin
# valor pone este test en rojo: o se le da valor, o se dice aqui que espera.
PERFIL_SIN_VALOR_QUE_ESPERA_UNA_ENTRADA = {
    "homogeneidad_serie_fen": (
        "el estudio hidrologico: el tratamiento de los años FEN de la serie "
        "(solo rige el caudal que el programa calcula con --cuencas y "
        "--estacion; un Q_m3s declarado no lo usa)"),
    "TW_receptor": (
        "el nivel del receptor de la ANA / Junta de Usuarios: solo se lee si "
        "ninguna via de la Sec. 1.3 es recorrible --sin TW declarado, sin "
        "cota_TW, sin Q_receptor_m3s, sin seccion medida y con "
        "seccion_receptor vacio (`servicio.tw_sin_via_de_sec_1_3`)--; con la "
        "seccion de archivo de seccion_receptor nunca se lee"),
}


def test_ningun_criterio_de_perfil_sin_valor_salvo_los_que_esperan_una_entrada():
    pendientes = {k for k, c in ca.CRITERIOS.items()
                  if c.valor is None and c.nivel == ca.NIVEL_PERFIL
                  and not getattr(c, "opcional", False)}
    assert pendientes == set(PERFIL_SIN_VALOR_QUE_ESPERA_UNA_ENTRADA)
    contrato = V.CONTRATO.read_text(encoding="utf-8")
    for clave in pendientes:
        assert f"`{clave}`" in contrato, clave


def _modulos_de_calculo():
    return sorted((SRC / "modulos").glob("*.py"))


def test_ningun_modulo_de_calculo_tiene_assert_ni_inalcanzables_desnudos():
    """
    Punto 4 del prompt: ningun `AssertionError("inalcanzable")` en M8/M9.
    Se mide en todos los modulos de calculo, y tambien `NotImplementedError`
    (PRECISIONES_T-11: ninguna de las dos corridas puede terminar en una).
    """
    for ruta in _modulos_de_calculo():
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            assert not isinstance(nodo, ast.Assert), f"{ruta.name}:{nodo.lineno}"
            if isinstance(nodo, ast.Raise) and nodo.exc is not None:
                exc = nodo.exc.func if isinstance(nodo.exc, ast.Call) else nodo.exc
                nombre = getattr(exc, "id", getattr(exc, "attr", None))
                assert nombre not in ("AssertionError", "NotImplementedError"), \
                    f"{ruta.name}:{nodo.lineno}"


def _llamadas_de_produccion(excluir=frozenset()):
    """
    Todos los nombres que el codigo de produccion LLAMA (src/, cli, gui),
    sin contar las llamadas que estan DENTRO de una funcion de `excluir`
    (las del propio censo: una pieza suelta que llama a otra pieza suelta
    no le da consumidor).
    """
    nombres = set()
    rutas = list(SRC.rglob("*.py")) + [RAIZ / "cli.py"] + \
        list((RAIZ / "gui").rglob("*.py"))
    for ruta in rutas:
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        pila = [n for n in arbol.body
                if not (isinstance(n, ast.FunctionDef) and n.name in excluir)]
        for raiz in pila:
            for nodo in ast.walk(raiz):
                if isinstance(nodo, ast.Call):
                    f = nodo.func
                    nombres.add(getattr(f, "id", getattr(f, "attr", None)))
    return nombres


def _funciones_del_censo():
    salida = []
    for nombre in M9.FUNCIONES_SIN_CONSUMIDOR:
        if nombre.startswith("piezas sueltas"):
            razon = M9.FUNCIONES_SIN_CONSUMIDOR[nombre]
            salida += [t.strip("` ") for t in razon.split("`")[1:12:2]]
            continue
        salida += [n.strip() for n in nombre.split("/")]
    return salida


def test_las_funciones_sin_consumidor_de_M9_no_tienen_llamador_de_produccion():
    """
    Punto 4 del prompt: «ninguna funcion en M9.FUNCIONES_SIN_CONSUMIDOR que
    T-7 debia consumir». El censo esta al dia si (a) cada funcion que nombra
    existe y (b) no la llama ningun modulo de produccion --salvo las dos que
    el propio censo declara llamadas por dentro--, y (c) las funciones que
    T-7 SI consume (el ensamble, el armado, el ciclopeo) no estan en el.
    """
    definidas = {n.name for n in ast.parse(
        (SRC / "modulos" / "M9_cabezal.py").read_text(encoding="utf-8")).body
        if isinstance(n, ast.FunctionDef)}
    censadas = _funciones_del_censo()
    llamadas = _llamadas_de_produccion(frozenset(censadas))
    assert len(censadas) >= 20
    llamadas_por_dentro = {"clase_exposicion_sulfatos", "factor_recubrimiento_por_ac",
                           "n_q_zapata_en_talud", "n_s_zapata_en_talud"}
    for nombre in censadas:
        assert nombre in definidas, nombre
        if nombre not in llamadas_por_dentro:
            assert nombre not in llamadas, nombre
    for nombre in ("ensamble_estabilidad", "armar_elemento", "ensamblar_armado",
                   "verificar_cabezal_ciclopeo", "cabezal_del_punto"):
        assert nombre in definidas and nombre in llamadas, nombre
        assert nombre not in censadas, nombre
