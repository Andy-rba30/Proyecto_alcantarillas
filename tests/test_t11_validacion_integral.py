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

pytestmark = pytest.mark.lento

from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src.modelos import TipoDeBloqueo
from src.modulos import M9_cabezal as M9
from tests.apoyo import validacion_integral as V
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
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
# Las corridas, una vez por modulo (A5: con xdist usar `--dist loadfile`)
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
        "exposicion_quimica_ems", "homogeneidad_serie_fen",
        # VE-5 / VE-7 (fix-suite): los de la Fase 0-bis y de los metrados.
        "Mw_licuefaccion", "incremento_acero_por_despiece",
        "clase_concreto_losa_entrega"}
    assert sin_valor_que_el_juego_declara <= set(J.DECLARACIONES)
    for clave in sin_valor_que_el_juego_declara:
        assert ca.CRITERIOS[clave].valor is None, clave
    # VE-3.16: el drenaje es «drenado» de archivo (AASHTO 11.6.6 manda
    # drenar); la reduccion de k_h sigue «sin_reduccion» porque aceptar el
    # desplazamiento es del Propietario y el programa no lo asume.
    assert ca.CRITERIOS["drenaje_trasdos"].valor == "drenado"
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


RUBRO_RELLENO = ("metrado de relleno para estructuras (EG-2013 502.A): no "
                 "medido")
RUBRO_REVESTIMIENTO = ("metrado de revestimiento de la entrada (emboquillado): "
                       "no medido")
RUBRO_CAMA_DEL_MARCO = "metrado de cama de apoyo del conducto: no medido"
ETAPA_VC1 = ("VC1 - alcance del requisito de la Sec. 2.3 (borde libre "
             "verificado; rasante hidraulica, no)")


def test_el_unico_bloqueo_de_la_corrida_completa_es_un_alcance_con_ficha(base):
    """
    Con el juego completo no queda ningun bloqueo por entrada ni por
    criterio: el unico es el ALCANCE del requisito de la Sec. 2.3 en C-01
    (la rasante hidraulica del canal no se mide; ficha VC1-01), que el punto
    lleva aunque dimensione.
    """
    bloqueos = V.todos_los_bloqueos(base)
    # CAMBIADO DECLARANDOLO (VE-5 met, ficha VE5-MET-01; VE-7 fix-suite):
    # desde que la Fase 11 MIDE, los rubros que el EG-2013 mide y el
    # programa no tiene con que medir (la seccion del relleno, la geometria
    # del revestimiento de la entrada, la cama del marco) salen como «metodo
    # no evaluable (metrados, Fase 11)» con su ficha. Son tambien ALCANCE
    # con ficha, no una entrada ni un criterio: el juicio del test no
    # cambia. Medido: los dos de cada punto, y la cama solo en el marco.
    assert all(b.clase == V.CLASE_METODO for b in bloqueos), bloqueos
    assert sorted((b.punto, b.que, b.etapa) for b in bloqueos) == sorted(
        [(i, "VE5-MET-01", etapa) for i in ("A-01", "A-02", "B-01", "C-01")
         for etapa in (RUBRO_RELLENO, RUBRO_REVESTIMIENTO)]
        + [("C-01", "VE5-MET-01", RUBRO_CAMA_DEL_MARCO),
           ("C-01", "VC1-01", ETAPA_VC1)])
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


def test_el_cabezal_se_dimensiona_y_pasa_E3_estatico_y_E1_sismico(base):
    """
    UN RESULTADO, NO UN FALLO DE LA VALIDACION (PRECISIONES_T-11). Hasta
    VE-3.5 este test se llamaba «el cabezal de la regla no pasa E3 estatico
    ni E1 sismico» y lo fijaba: con la zapata que propone la regla de T-7a,
    el deslizamiento estatico y la capacidad portante sismica del marco LRFD
    no pasaban en ningun punto. Desde VE-3.5 la zapata se DIMENSIONA por
    estabilidad (el juego declara el paso y el tope, datos de prueba) y las
    dos filas cumplen en los cuatro puntos, con el ancho «dimensionado por
    estabilidad». Que la regla sola no pasa lo fija
    `tests/test_ve3_dimensionamiento_cabezal.py` (sin el criterio) y la §3.1
    de la sensibilidad (base `juego_cabezal_de_la_regla`).
    """
    from src.modelos import ORIGEN_DIMENSION_ESTABILIDAD, ORIGEN_DIMENSION_REGLA
    origenes = {}
    for p in base.puntos:
        v = V.verificaciones_del_punto(base, p.punto.id)
        assert v["E3-LRFD.est.e"] == "cumple", p.punto.id
        assert v["E1-LRFD.sis.e"] == "cumple", p.punto.id
        for lado in ("entrada", "salida"):
            g = getattr(p.cabezal, lado)
            b = next(d for d in g.dimensiones
                     if d.nombre == "ancho de la zapata (B)")
            origenes[(p.punto.id, lado)] = b.origen
    # CAMBIADO DECLARANDOLO (VE-7 fix-suite): el juego declara el canto del
    # marco que la app pide (`espesor_pared_cajon` = 0.30 m, VE7B-11). Con
    # el la clave de C-01 sube 0.10 m, el cabezal de ENTRADA crece con ella
    # (H_c 2.35 -> 2.45 m, L_c 2.20 -> 2.40 m) y la zapata que la regla de
    # T-7a propone para esa altura (B = 1.715 m) ya pasa la estabilidad: no
    # hace falta dimensionarla (con 0.20 m crecia de la regla a 1.745 m).
    # Las otras siete zapatas crecen por estabilidad, como desde VE-3.5.
    assert {k for k, o in origenes.items()
            if o == ORIGEN_DIMENSION_REGLA} == {("C-01", "entrada")}
    assert {k for k, o in origenes.items()
            if o != ORIGEN_DIMENSION_REGLA} == {
        k for k, o in origenes.items() if o == ORIGEN_DIMENSION_ESTABILIDAD}


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
    # Hasta VE-3.9 tambien T7C-03 (el cortante de la zapata de C-01 con
    # lecho cohesivo, fuera de 5.7.3.4.1): desde VE-3.9 el peralte crece
    # por su armado hasta salir de esa franja (0.873 m) y ya no se detiene.
    # Y hasta VE-3.14 tambien T7B-05 y T7B-06 (el sismo con agua en el
    # plano de empuje): desde VE-3.14 se evalua con el peso total bajo el
    # agua (C11.6.5.3, 'agua_del_relleno_bajo_sismo' [C]) y ya no se detiene.
    # VE-5 met (VE-7 fix-suite): mas VE5-MET-01, los rubros de la Fase 11
    # que el programa no tiene con que medir (relleno, revestimiento de la
    # entrada, cama del marco) y el acero de un portico que no cierra.
    assert fichas == {"VC1-01", "VE5-MET-01"}
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
    `drenaje_trasdos` de archivo de entonces ('sin_drenaje') detenia 24
    etapas, y contradecia a la §3.3. VE-3.16: con 'drenado' de archivo
    ninguna base lo lee y pasa a las condicionales no medidas (§7).
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
        # VE-7 fix-suite: una entrada quitada puede detener con DOS clases
        # (`espesor_pared_cajon`: el portico, criterio que se declara, y el
        # metrado de su acero, metodo con ficha); si una es «criterio», la
        # §7 la imprime como criterio.
        if clases[nombre] == V.CLASE_METODO:
            assert clase_impresa.startswith("método diferido"), fila
        elif V.CLASE_CRITERIO in clases[nombre].split(" / "):
            assert clase_impresa == "criterio que se declara", fila
        else:
            assert clase_impresa.startswith("entrada del proyecto"), fila
    # Las cuatro clases de entrada que la cadena T prometio que quedarian
    # (cadena, §5): hidrologia del canal y del receptor, EMS, topografia,
    # trazo y decisiones del Propietario.
    assert {"luz_m", "NF_profundidad_m", "c_phi_fundacion", "phi_relleno_trasdos",
            "exposicion_quimica_ems", "Q_evento_extremo_m3s",
            "cota_coronacion_canal", "TR_evento_extremo",
            "remanso_derecho_via"} <= set(nombres)
    # VE-3.16 (CAMBIADO DECLARANDOLO): hasta entonces el γ saturado salia
    # SOLO de la segunda base (la titular, con el trasdos 'sin_drenaje' de
    # archivo), como entrada (ensayo). Con 'drenado' de archivo y el
    # freatico del juego bajo las zapatas ninguna base lo lee: no esta en
    # la medida y la §7 lo nombra entre las condicionales.
    assert "peso_especifico_saturado_relleno_kn_m3" not in set(nombres)
    assert "peso_especifico_saturado_relleno_kn_m3" in V.CONDICIONALES_NO_MEDIDAS
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
    # CAMBIADO DECLARANDOLO (VE-3.14, H-3): con agua en el plano de empuje
    # el sismo ya no se detiene (C11.6.5.3, peso total bajo el agua); hasta
    # VE-3.14 «freatico_a_2m» dejaba T7B-06 en A-01 y A-02, y
    # «drenaje_de_archivo» T7B-05 en los cuatro puntos. VE-3.16: esa
    # variante se llama «sin_drenaje_declarado» (declara 'sin_drenaje' sobre
    # el 'drenado' de archivo).
    assert fichas("freatico_a_2m") == set()
    assert fichas("sin_drenaje_declarado") == set()
    # Sin ("C-01", "T7C-03") desde VE-3.9: el peralte de la salida de C-01
    # partia de 0.473 m (H_c/10, ya sobre 16 in) con el cortante fuera de
    # 5.7.3.4.1, y hoy crece por su armado hasta 0.873 m, donde se verifica.
    assert fichas("C01_lecho_cohesivo") == set()


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
    no pasaba la capacidad portante sismica del marco LRFD con el peralte de
    la regla. CAMBIADO EN VE-3.9: el ancho declarado no se itera, pero el
    PERALTE no se declaro y crece por su armado (0.404 -> 0.704 m); con esa
    zapata la salida tambien pasa E1-LRFD sismica.
    """
    from src.modelos import ORIGEN_DIMENSION_ARMADO
    _t, informe, _ef = variantes["zapata_declarada_3m"]
    v = V.verificaciones_del_punto(informe, "A-01")
    entrada = {k: e for k, e in v.items() if k.startswith("E") and k.endswith(".e")}
    assert len(entrada) == 12 and set(entrada.values()) == {"cumple"}
    # CAMBIADO DECLARANDOLO (VE-3.14, bloque 3): con el acero que el
    # cortante general pide, el peralte de la salida baja de 0.704 a
    # 0.504 m; con el ANCHO DECLARADO (3.0 m, que no se itera) la zapata mas
    # liviana ya no pasa E1-LRFD sismica, y la app lo dice en vez de
    # cubrirlo con un peralte inflado. La entrada sigue pasando entera.
    # CAMBIADO DECLARANDOLO (VE-3.15, decisiones 11 y 14): con los factores
    # de la tabla de muros y el desplante sin margen bajo la hoya, la salida
    # con el ancho declarado vuelve a pasar E1-LRFD sismica.
    assert v["E1-LRFD.sis.s"] == "cumple"
    assert v["E3-LRFD.est.s"] == "cumple"
    salida = _punto(informe, "A-01").cabezal.salida
    assert salida.B == pytest.approx(3.0, abs=ABS_CERO)
    # CAMBIADO DECLARANDOLO (cierre de VE-3.15, decision 9): con el talon por
    # el metodo exacto el peralte de la REGLA (0.40414 m) ya cumple A1 a A6
    # de la punta y del talon, de modo que el armado no lo hace crecer y su
    # origen deja de ser «dimensionada por armado».
    espesor = next(d for d in salida.dimensiones
                   if d.nombre == "espesor de la zapata")
    assert espesor.origen != ORIGEN_DIMENSION_ARMADO
    assert espesor.valor == pytest.approx(0.40414, abs=ABS_CERO)
    assert all(estado == "cumple" for codigo, estado in v.items()
               if codigo.startswith(("A1.", "A2.", "A3.", "A4."))
               and codigo.endswith((".punta.s", ".talon.s")))


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
    criterios con valor de archivo, cada uno con su razon escrita
    (`J.PISA_EL_ARCHIVO_PORQUE`), y la variante titular los deja en su
    valor (desde VE-3.16 ya no `drenaje_trasdos`, cuyo archivo es el
    'drenado' que el juego declaraba). Con ellos los cuatro puntos
    dimensionan igual, las tres filas
    estaticas del marco LRFD pasan en los ocho cabezales con la zapata
    dimensionada (desde VE-3.5; antes no pasaban en ninguno) y la condicion
    sismica es «metodo no evaluable» (T7B-05) en los ocho.
    """
    pisadas = {k for k in J.DECLARACIONES if ca.CRITERIOS[k].valor is not None}
    # VE-3.15 (decision 12): el muro que cede del juego es UNA decision de
    # dos criterios (la reduccion de k_h y el armado «cedente»).
    # VE-3.16: `drenaje_trasdos` sale del grupo (su archivo es 'drenado',
    # lo que el juego declaraba) y el juego ya no lo declara.
    # VE-7 fix-suite (CAMBIADO DECLARANDOLO): el juego pisa ademas el canto
    # del marco con el valor que la app pide (VE7B-11), y la titular lo
    # CONSERVA (`J.LA_TITULAR_CONSERVA`): con el de archivo la app detiene
    # el portico y manda repetir con 0.30 m.
    assert pisadas == set(J.PISA_EL_ARCHIVO_PORQUE) == {
        "factor_muro_eleccion", "regimen_resistencia_elementos_cabezal",
        "espesor_pared_cajon"}
    assert set(J.LA_TITULAR_CONSERVA) == {"espesor_pared_cajon"}
    assert "drenaje_trasdos" not in J.DECLARACIONES
    assert [c for c, *_ in V.pisa_el_archivo()] == sorted(
        pisadas, key=list(J.DECLARACIONES).index)
    cambios = dict(((c[1], c[2]) for c in J.VARIANTES[V.VARIANTE_TITULAR][1]))
    assert cambios["factor_muro_eleccion"] is None
    assert cambios["regimen_resistencia_elementos_cabezal"] is None
    assert not set(J.LA_TITULAR_CONSERVA) & set(cambios)
    assert set(cambios) == pisadas - set(J.LA_TITULAR_CONSERVA)
    # VE-3.16 (CAMBIADO DECLARANDOLO): la titular ya no toca el drenaje ni
    # redeclara el γ saturado de prueba: con el relleno drenado de archivo
    # no se lee.
    assert "drenaje_trasdos" not in cambios
    assert "peso_especifico_saturado_relleno_kn_m3" not in cambios
    for p in titular.puntos:
        r = V.resumen_del_punto(titular, p)
        assert (r["familia"], r["material"], r["seccion"]) == \
            DISENO_ESPERADO[r["id"]], r["id"]
    # --- VE-3.5 --- hasta aqui las tres filas estaticas del marco LRFD no
    # pasaban en los ocho cabezales (la zapata de la regla); el juego
    # declara el paso y el tope del dimensionamiento (datos de prueba) y la
    # zapata crece hasta que pasan en los ocho.
    assert V.filas_estaticas_que_no_pasan(titular) == {
        "E1-LRFD.est": 0, "E2-LRFD.est": 0, "E3-LRFD.est": 0}
    assert V.zapatas_dimensionadas(titular)["dimensionadas"] == 8
    bloqueos = [(b.punto, b.que) for b in V.todos_los_bloqueos(titular)]
    # CAMBIADO DECLARANDOLO (VE-3.14, H-3): sin los dos T7B-05 por punto
    # (el sismo de los dos cabezales con el relleno saturado se evalua).
    # VE-5 met (VE-7 fix-suite): mas los rubros de la Fase 11 que no se
    # miden (VE5-MET-01), los mismos que en la corrida completa.
    assert sorted(set(bloqueos)) == [
        ("A-01", "VE5-MET-01"), ("A-02", "VE5-MET-01"),
        ("B-01", "VE5-MET-01"), ("C-01", "VC1-01"), ("C-01", "VE5-MET-01")]


def test_el_documento_presenta_primero_la_titular():
    """H2: el §2 del documento es la titular; el juego es su §2.1."""
    texto = V.DOCUMENTO.read_text(encoding="utf-8")
    i2 = texto.index("## 2. Corrida titular: el juego con las decisiones de archivo")
    # VE-3.16: el rotulo del §2.1 ya no habla del «caso drenado» (es el
    # archivo): la variante ejercita el empuje sismico reducido.
    i21 = texto.index("### 2.1 Variante que ejercita el empuje sísmico reducido")
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
    # 7 hasta VE-5 (catlic), 3 hasta VE-7: las dos ediciones que rigen el
    # expediente (medido con `V._sin_consumidor()`).
    assert len(SIN_CONSUMIDOR_Y_SIN_MEDIDA) == 2
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
    i4 = texto.index("## 4. Fundamentos que la corrida")
    cuerpo = texto[:i4]
    cuadro_4 = texto[i4:]
    # CAMBIADO EN EL CIERRE DE VE-7 (ficha VE7C-06), declarandolo: desde VE-7
    # la cuarta corrida de referencia (`materiales_y_ramas`, con cuenca de
    # 10 a 770 km2) SI ejercita los tres fundamentos del metodo racional
    # modificado (`FH.RM_*`), que salen del cuadro 4 y entran en §2. En §4.2
    # solo queda `FH.C_SUBAREAS` (VE-7 lote B, ficha VE7B-06: columna opcional
    # `subareas`, que ninguna corrida de referencia trae; medido en
    # `tests/test_ve7_lote_b_subareas.py`). Cualquier OTRO fundamento de la
    # Fase 1-bis sigue sin poder faltar.
    for f in ("`FH.RM_INTENSIDAD`", "`FH.RM_C`", "`FH.RM_CAUDAL`"):
        assert f in cuerpo, f
        assert f not in cuadro_4, f
    assert "`FH.C_SUBAREAS`" in cuadro_4
    cuadro_4 = cuadro_4.replace("`FH.C_SUBAREAS`", "")
    # Y VE-2 (d), declarandolo: el fundamento de la ELECCION del factor de
    # intervalo fijo viaja dentro del paso del ajuste (1b.2), no como paso
    # propio, y el cuadro solo cuenta pasos (como F5.V7_FILA). Esta corrida
    # SI lo ejercita: se comprueba en sus elecciones.
    elecciones = {e.fundamento_id
                  for p in ind.pasos_de_las_corridas([informe])
                  for e in p.elecciones if e.fundamento_id}
    assert "FH.FACTOR_P24" in elecciones
    cuadro_4 = cuadro_4.replace("`FH.FACTOR_P24`", "")
    assert "`FH." not in cuadro_4


# ===========================================================================
# 1d. El defecto que la validacion destapo, CORREGIDO (T11-03)
# ===========================================================================

def _bloqueo_de_diseno(informe, id_punto):
    """El UNICO bloqueo de diseño (no factible) del punto."""
    de_diseno = [b for b in _punto(informe, id_punto).bloqueos
                 if b.tipo is TipoDeBloqueo.DISENO_NO_FACTIBLE]
    assert len(de_diseno) == 1, _punto(informe, id_punto).bloqueos
    return de_diseno[0]


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
    # VE-7 fix-suite: el punto lleva tambien los bloqueos de las etapas que
    # corren al lado del diseño (VE6-02: la Fase 0-bis, los metrados); el
    # que se juzga es el de DISEÑO, no el primero de la lista.
    b = _bloqueo_de_diseno(informe, "A-01")
    assert "Dato invalido en 'cota_subrasante'" not in b.mensaje
    assert "material no evaluable" not in b.mensaje
    assert "NO FACTIBLE POR RASANTE" in b.mensaje
    assert "Ø 1.80 m no cabe bajo la subrasante" in b.mensaje
    assert b.delta_rasante_m == pytest.approx(
        42.10 + 1.95 + 0.01501 + 0.3048 + 0.15 - 44.20, rel=REL_TRANSPORTE)
    b = _bloqueo_de_diseno(informe, "A-02")
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
    # --- VE-2 (c2) ---
    "margen_estacional_nf_v7_m": (
        "el estudio geotecnico: el ascenso estacional del freatico sobre la "
        "lectura de NF_profundidad_m (solo lo lee V7 con "
        "'nivel_agua_diseno_v7' = 'nf_del_punto'; con el valor de archivo, "
        "'en_la_clave', nunca se lee)"),
    # --- Revision de VE-2 (M3) --- paso de expediente a perfil: con la misma
    # alternativa y el nivel sobre la clave, V7 lo lee y una corrida de
    # perfil se detiene en el.
    "peso_especifico_saturado_relleno_kn_m3": (
        "el ensayo del material de cantera del relleno (lo lee el cabezal "
        "con agua en el relleno, y V7 solo con 'nivel_agua_diseno_v7' = "
        "'nf_del_punto' y el nivel sobre la clave)"),
    # --- VE-5 (mh, ficha T1-05) --- medido con
    # `ca.criterios_de_perfil_sin_valor()`.
    "factores_idf_regional": (
        "el estudio regional de curvas IDF de la zona (o las curvas de una "
        "estacion pluviografica): K, m y n de la ecuacion (17) del Manual "
        "(num. 3.8.1). Solo los lee el caudal CALCULADO con "
        "'relacion_intensidad_duracion' = 'idf_regional_ec17'; con el valor "
        "de archivo ('dick_peschke') nunca se leen"),
}


def test_ningun_criterio_de_perfil_sin_valor_salvo_los_que_esperan_una_entrada():
    pendientes = {k for k, c in ca.CRITERIOS.items()
                  if c.valor is None and c.nivel == ca.NIVEL_PERFIL
                  and not getattr(c, "opcional", False)}
    assert pendientes == set(PERFIL_SIN_VALOR_QUE_ESPERA_UNA_ENTRADA)
    assert pendientes == set(ca.criterios_de_perfil_sin_valor())
    contrato = V.CONTRATO.read_text(encoding="utf-8")
    for clave in pendientes:
        assert f"`{clave}`" in contrato, clave


def _modulos_de_calculo():
    return [r for r in sorted((SRC / "modulos").rglob("*.py"))
            if "__pycache__" not in r.parts]


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
    definidas = {n.name
        for r in sorted((SRC / "modulos" / "M9_cabezal").glob("*.py"))
        for n in ast.parse(r.read_text(encoding="utf-8")).body
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
