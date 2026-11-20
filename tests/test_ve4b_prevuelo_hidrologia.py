# -*- coding: utf-8 -*-
"""
tests/test_ve4b_prevuelo_hidrologia.py
======================================
La aceptacion de VE-4b: el ESTIMADOR DEL PRE-VUELO PARA LA FASE 1-bis, que
cierra la ficha T1-04 de `docs/decisiones_diferidas.md` («un estimador en
`anticipo` de lo que detiene la Fase 1-bis: criterio FEN sin declarar, cuenca
fuera de la poblacion de su metodo, dos areas»).

Hasta VE-4b, con `--cuencas` y `--estacion` el pre-vuelo CARGABA las dos
entradas y decia de un `Q_m3s` vacio que «dependia de la hidrologia», sin
decir si la Fase 1-bis lo iba a detener. Ahora lo anticipa, con las MISMAS
reglas que el bloque 4 de PF-2 (`tests/test_pf2_prevuelo.py`):

  * es una ESTIMACION: no gobierna ningun boton, no corre el pipeline, no
    registra el uso de ningun criterio y estima de MAS a proposito;
  * cada falta DETIENE con la MISMA etapa y el MISMO mensaje que el
    `Bloqueo` real (la union de abajo lo compara texto a texto);
  * lo que depende del periodo de retorno de la Fase 2, que el pre-vuelo no
    calcula, se anuncia como «puede detener» y detiene en la estimacion;
  * un `Q_m3s` lleno GANA y no se recalcula: no hay faltas del calculo
    hidrologico para un punto con caudal declarado. Lo que si se anuncia es
    el AREA ESCRITA DOS VECES, porque la corrida la contrasta y la bloquea
    tambien con el caudal declarado (`servicio._fase_hidrologia`).

Escritos PRIMERO, en rojo, sobre el invariante y no sobre la salida actual.
Los datos son DATOS DE PRUEBA: las cuencas y la serie SINTETICAS de
`tests/fixtures/hidrologia/` y el CSV de ejemplo, con variantes escritas en
`tmp_path`.
"""

from __future__ import annotations

import ast
import csv
import inspect
import subprocess
import sys
from pathlib import Path

import pytest

import cli
from src import anticipo as antc
from src import criterios_adoptados as ca
from src import servicio
from src.modelos import Familia
from tests.apoyo import doble_tkinter

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
AMPLIADAS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"
HIDRO = RAIZ / "tests" / "fixtures" / "hidrologia"
CUENCAS = HIDRO / "cuencas_prueba.csv"
CUENCAS_RM = HIDRO / "cuencas_racional_modificado_prueba.csv"
ESTACION = HIDRO / "estacion_prueba.csv"
OBRAS_CON_CUENCA = ("A-01", "A-02", "B-01")
FEN = "homogeneidad_serie_fen"
DISTRIBUCION = "distribucion_precipitacion_maxima"

LUZ_DEL_CASO = 2.75          # m: la de la linea base
TW_DEL_CASO = 0.30           # m

# EN ROJO hasta implementar el estimador (medido: 26 failed antes de tocar
# codigo). Se retira en el commit que lo implementa.
pytestmark = pytest.mark.xfail(strict=True, reason="VE-4b: estimador sin implementar")


# ---------------------------------------------------------------------------
# Apoyos
# ---------------------------------------------------------------------------

def _externos(ruta=AMPLIADAS, **banderas):
    base = dict(luz_m=LUZ_DEL_CASO, TW_m=None, longitud_m=None,
                L_hidraulico_m=None, categoria_tr=None)
    base.update(banderas)
    return cli.cargar_datos_externos(ruta, base)


def _leer(ruta):
    with Path(ruta).open(encoding="utf-8", newline="") as fh:
        lineas = [l for l in fh if not l.startswith("#")]
    return list(csv.DictReader(lineas))


def _escribir(ruta, filas):
    with Path(ruta).open("w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=list(filas[0]), restval="")
        escritor.writeheader()
        escritor.writerows(filas)
    return ruta


def _puntos(tmp_path, *, sin_q=OBRAS_CON_CUENCA, solo=None, **por_punto):
    """El CSV de ejemplo con el Q vaciado en `sin_q` y celdas cambiadas."""
    filas = _leer(CSV_EJEMPLO)
    if solo is not None:
        filas = [f for f in filas if f["id"] in solo]
    for fila in filas:
        if fila["id"] in sin_q:
            fila["Q_m3s"] = ""
        fila.update(por_punto.get(fila["id"].replace("-", "_"), {}))
    return _escribir(tmp_path / "puntos.csv", filas)


def _cuencas(tmp_path, base=CUENCAS, **por_punto):
    filas = _leer(base)
    for fila in filas:
        fila.update(por_punto.get(fila["id"].replace("-", "_"), {}))
    return _escribir(tmp_path / "cuencas.csv", filas)


def _hidro(cuencas=CUENCAS, estacion=ESTACION):
    return servicio.cargar_hidrologia(cuencas, estacion)


def _estimar(ruta, hidrologia, externos=None):
    return antc.datos_faltantes_por_punto(
        ruta, _externos() if externos is None else externos,
        cli.ALCANCE_PERFIL,
        ids_con_caudal_calculable=servicio.ids_con_caudal_calculable(hidrologia),
        hidrologia=hidrologia)


def _de_la_hidrologia(estimado):
    return [e for e in estimado if e.poblacion == antc.POBLACION_HIDROLOGIA]


def _bloqueos_reales(ruta, hidrologia, externos=None):
    """{id: [Bloqueo de la Fase 1-bis]} de la corrida real."""
    informe = cli.correr(ruta, _externos() if externos is None else externos,
                         alcance=cli.ALCANCE_PERFIL, hidrologia=hidrologia)
    reales = {}
    for punto in informe.puntos:
        for b in punto.bloqueos:
            if b.fase == servicio.FASE_HIDROLOGIA:
                reales.setdefault(punto.punto.id, []).append(b)
    return reales


def _cubre(e, b):
    """
    La entrada estimada `e` anuncia el bloqueo real `b`: la MISMA etapa y el
    MISMO mensaje; o, si depende del TR, el mismo encabezado del metodo no
    evaluable (rotulo, magnitud y punto) bajo el rotulo «puede detener».
    """
    if e.etapa != b.etapa or not e.detiene:
        return False
    if e.de_donde == b.mensaje:
        return True
    return (e.de_donde.startswith(antc.PUEDE_DETENER_SEGUN_TR)
            and b.mensaje.split(" -- ")[0] in e.de_donde)


@pytest.fixture
def declarar():
    """Declara criterios en caliente y los retira al salir."""
    puestos = []

    def _declarar(clave, valor):
        ca.establecer_valor_dinamico(clave, valor)
        puestos.append(clave)

    yield _declarar
    for clave in puestos:
        ca.quitar_valor_dinamico(clave)


# ===========================================================================
# 1 - Lo que el pre-vuelo anuncia
# ===========================================================================

def test_sin_el_criterio_fen_las_tres_obras_con_cuenca_se_detienen_en_el(tmp_path):
    ruta = _puntos(tmp_path)
    h = _hidro()
    estimado = _estimar(ruta, h)
    hidro = _de_la_hidrologia(estimado)
    por_punto = {}
    for e in hidro:
        por_punto.setdefault(e.id_punto, {})[e.dato] = e
    assert set(por_punto) == set(OBRAS_CON_CUENCA)
    for id_punto in OBRAS_CON_CUENCA:
        e = por_punto[id_punto][FEN]
        assert e.detiene and e.etapa == servicio.ETAPA_CAUDAL_CALCULADO
        assert FEN in e.de_donde
        assert e.familia in (Familia.A, Familia.B)
    # El Q_m3s vacio sigue diciendo que depende de la hidrologia, y espera.
    caudal = [e for e in estimado if e.dato == "Q_m3s" and e.id_punto in OBRAS_CON_CUENCA]
    assert caudal and all(not e.detiene and e.etapa == antc.ETAPA_DEPENDE_DE_LA_HIDROLOGIA
                          for e in caudal)


def test_un_caudal_declarado_gana_y_no_se_anticipa_el_calculo(tmp_path, declarar):
    """Con `Q_m3s` lleno no hay calculo hidrologico que anticipar."""
    h = _hidro()
    assert not _de_la_hidrologia(_estimar(CSV_EJEMPLO, h))
    declarar(FEN, "dos_poblaciones")
    assert not _de_la_hidrologia(_estimar(CSV_EJEMPLO, h))
    # Tambien cuando el Q lo trae el JSON de datos externos.
    ruta = _puntos(tmp_path, sin_q=("A-02",))
    json_q = tmp_path / "q.json"
    json_q.write_text('{"puntos": {"A-02": {"Q_m3s": 0.48}}}', encoding="utf-8")
    externos = _externos(json_q)
    assert not [e for e in _de_la_hidrologia(_estimar(ruta, h, externos))
                if e.id_punto == "A-02"]


def test_sin_hidrologia_no_hay_entradas_de_la_fase_1bis(tmp_path):
    estimado = antc.datos_faltantes_por_punto(_puntos(tmp_path), _externos(),
                                              cli.ALCANCE_PERFIL)
    assert not _de_la_hidrologia(estimado)


def test_el_area_escrita_dos_veces_se_anuncia_tambien_con_el_caudal_declarado(tmp_path):
    cuencas = _cuencas(tmp_path, A_02={"area_km2": "3.0"})
    h = _hidro(cuencas)
    estimado = _de_la_hidrologia(_estimar(CSV_EJEMPLO, h))
    assert [(e.id_punto, e.etapa) for e in estimado] == [
        ("A-02", servicio.ETAPA_AREA_DE_LA_CUENCA)]
    assert estimado[0].detiene and "area_ha" in estimado[0].dato
    reales = _bloqueos_reales(CSV_EJEMPLO, h)
    assert set(reales) == {"A-02"}
    assert all(any(_cubre(e, b) for e in estimado) for b in reales["A-02"])


def test_el_prevuelo_no_registra_el_uso_de_ningun_criterio(tmp_path, declarar):
    declarar(FEN, "serie_completa")
    ruta = _puntos(tmp_path)
    h = _hidro()
    ca.reiniciar_usos()
    _estimar(ruta, h)
    assert ca.criterios_usados() == []


# ===========================================================================
# 2 - La union: ningun bloqueo real de la Fase 1-bis escapa, y lo de mas se
#     censa con su razon
# ===========================================================================

def _serie_que_no_pasa_ks(tmp_path):
    """Dos poblaciones separadas: ninguna de las tres distribuciones pasa K-S."""
    filas = [{"estacion": "PRUEBA-SINTETICA", "anio": str(1980 + i),
              "p24_mm": ("10.0" if i % 2 else "200.0"), "fen": "no"}
             for i in range(30)]
    return _escribir(tmp_path / "estacion_ks.csv", filas)


# Cada configuracion: (nombre, criterios declarados, cambios al CSV de
# puntos, cambios al CSV de cuencas, base de cuencas, estacion, lo que el
# pre-vuelo estima DE MAS con su razon).
#
# LO QUE SOBRA, MEDIDO: la corrida se detiene en la PRIMERA compuerta de la
# Fase 1-bis y el pre-vuelo las dice todas. En «rm_sin_cn_con_kirpich» la
# corrida se detiene en el metodo de tiempo de concentracion (desde 10 km2
# el racional modificado pide Temez) y no llega a pedir el numero de curva;
# en «sin_fen_y_poblacion» se detiene en el criterio FEN y no llega al tiempo
# de concentracion. Es la clase de falso positivo que el pre-vuelo declara:
# cada entrada de mas es una falta REAL que la corrida sentiria despues.
CONFIGURACIONES = [
    ("fen_sin_declarar", {}, {}, {}, CUENCAS, ESTACION, {}),
    ("serie_completa", {FEN: "serie_completa"}, {}, {}, CUENCAS, ESTACION, {}),
    ("serie_sin_fen", {FEN: "serie_sin_fen"}, {}, {}, CUENCAS, ESTACION, {}),
    ("dos_poblaciones", {FEN: "dos_poblaciones"}, {}, {}, CUENCAS, ESTACION, {}),
    ("areas_distintas", {FEN: "serie_completa"}, {},
     {"A_02": {"area_km2": "3.0"}}, CUENCAS, ESTACION, {}),
    ("kirpich_fuera_de_poblacion", {FEN: "serie_completa"}, {},
     {"A_02": {"S_cauce_cuenca": "0.02"}}, CUENCAS, ESTACION, {}),
    ("sin_fen_y_poblacion", {}, {},
     {"A_02": {"S_cauce_cuenca": "0.02"}}, CUENCAS, ESTACION,
     {"A-02": {"tc"}}),
    ("california_sin_desnivel", {FEN: "serie_completa"}, {},
     {"A_02": {"metodo_tc": "california_culverts_practice",
               "ajuste_kirpich": ""}}, CUENCAS, ESTACION, {}),
    ("retardo_scs_sin_cn", {FEN: "serie_completa"}, {},
     {"A_02": {"metodo_tc": "retardo_scs", "ajuste_kirpich": ""}},
     CUENCAS, ESTACION, {}),
    ("temez_fuera_de_rango", {FEN: "serie_completa"}, {},
     {"A_01": {"L_cauce_m": "100", "S_cauce_cuenca": "0.1"}},
     CUENCAS, ESTACION, {}),
    ("alivio_de_10_km2", {FEN: "serie_completa"},
     {"B_01": {"area_ha": "1200"}}, {"B_01": {"area_km2": "12"}},
     CUENCAS, ESTACION, {}),
    ("racional_modificado", {FEN: "serie_completa"},
     {"A_01": {"area_ha": "5590"}}, {}, CUENCAS_RM, ESTACION, {}),
    ("rm_sin_cn_con_kirpich", {FEN: "serie_completa"},
     {"A_01": {"area_ha": "5590"}},
     {"A_01": {"CN": "", "metodo_tc": "kirpich", "ajuste_kirpich": "ninguno"}},
     CUENCAS_RM, ESTACION, {"A-01": {"CN"}}),
    ("rm_mas_de_770", {FEN: "serie_completa"},
     {"A_01": {"area_ha": "80000"}}, {"A_01": {"area_km2": "800"}},
     CUENCAS_RM, ESTACION, {}),
    ("ks_no_pasa", {FEN: "serie_completa"}, {}, {}, CUENCAS, None, {}),
    ("distribucion_sin_estimador", {FEN: "serie_completa",
                                    DISTRIBUCION: "log_pearson_3"},
     {}, {}, CUENCAS, ESTACION, {}),
]


@pytest.mark.parametrize("nombre, criterios, en_puntos, en_cuencas, base, "
                         "estacion, sobra", CONFIGURACIONES,
                         ids=[c[0] for c in CONFIGURACIONES])
def test_todo_bloqueo_real_de_la_fase_1bis_estaba_en_el_prevuelo(
        tmp_path, declarar, nombre, criterios, en_puntos, en_cuencas, base,
        estacion, sobra):
    for clave, valor in criterios.items():
        declarar(clave, valor)
    ruta = _puntos(tmp_path, **en_puntos)
    cuencas = _cuencas(tmp_path, base=base, **en_cuencas)
    if estacion is None:
        estacion = _serie_que_no_pasa_ks(tmp_path)
    h = _hidro(cuencas, estacion)
    estimado = _de_la_hidrologia(_estimar(ruta, h))
    reales = _bloqueos_reales(ruta, h)
    for id_punto, bloqueos in reales.items():
        del_punto = [e for e in estimado if e.id_punto == id_punto]
        for b in bloqueos:
            assert any(_cubre(e, b) for e in del_punto), (
                nombre, id_punto, b.etapa, b.mensaje, [e.de_donde for e in del_punto])
    de_mas = {}
    for e in estimado:
        if not any(_cubre(e, b) for b in reales.get(e.id_punto, [])):
            de_mas.setdefault(e.id_punto, set()).add(e.dato)
    assert de_mas == sobra, nombre
    # Cada configuracion menos la del caudal que se calcula entero bloquea
    # algo: la union no se cumple en el vacio.
    if nombre not in ("serie_completa", "racional_modificado"):
        assert reales, nombre


def test_lo_que_depende_del_tr_se_anuncia_como_puede_detener(tmp_path, declarar):
    declarar(FEN, "serie_sin_fen")
    ruta = _puntos(tmp_path)
    estimado = _de_la_hidrologia(_estimar(ruta, _hidro()))
    condicionales = [e for e in estimado
                     if e.de_donde.startswith(antc.PUEDE_DETENER_SEGUN_TR)]
    assert {e.id_punto for e in condicionales} == set(OBRAS_CON_CUENCA)
    assert all(e.detiene for e in condicionales)


# ===========================================================================
# 3 - Guardias: el pre-vuelo no calcula el caudal, y las dos puertas lo dicen
# ===========================================================================

def _llamadas(fn):
    arbol = ast.parse(inspect.getsource(fn))
    return {ast.unparse(n.func) for n in ast.walk(arbol) if isinstance(n, ast.Call)}


def test_el_anticipo_del_calculo_no_calcula_ni_la_lluvia_ni_el_caudal():
    from src.modulos import MH_hidrologia as MH
    prohibidas = ("caudal_de_diseno", "caudal_de_aporte_cuneta",
                  "precipitacion_de_diseno", "_caudal_calculado",
                  "_caudal_racional_modificado", "tiempo_de_concentracion",
                  "_paso_intensidad", "_paso_c", "ca.valor")
    for fn in (MH.anticipar_caudal, servicio.anticipar_fase_hidrologia):
        for llamada in _llamadas(fn):
            assert not llamada.endswith(prohibidas), (fn.__name__, llamada)
    # Y la cadena de llamadas del anticipo pasa por el servicio: anticipo no
    # importa MH_hidrologia (lo fija tambien test_t1_hidrologia).
    assert "servicio.anticipar_fase_hidrologia" in _llamadas(antc.datos_faltantes_por_punto)


def test_la_cli_imprime_las_faltas_de_la_fase_1bis_y_sale_con_1(tmp_path):
    ruta = _puntos(tmp_path, solo=("A-02",))
    base = [sys.executable, str(RAIZ / "cli.py"), str(ruta), "--prevuelo",
            "--alcance", "perfil", "--luz", str(LUZ_DEL_CASO),
            "--tw", str(TW_DEL_CASO), "--cuencas", str(CUENCAS),
            "--estacion", str(ESTACION)]
    hecho = subprocess.run(base, capture_output=True, text=True, cwd=RAIZ)
    assert hecho.returncode == 1, hecho.stdout + hecho.stderr
    linea = next(l for l in hecho.stdout.splitlines()
                 if "A-02" in l and FEN in l and "DETIENE" in l)
    assert servicio.ETAPA_CAUDAL_CALCULADO in linea
    assert antc.AVISO_HIDROLOGIA_NO_CALCULADA in hecho.stdout
    hecho = subprocess.run(base + ["--declarar", f"{FEN}=serie_completa"],
                           capture_output=True, text=True, cwd=RAIZ)
    assert hecho.returncode == 0, hecho.stdout + hecho.stderr


def test_las_dos_puertas_pasan_la_hidrologia_al_anticipo():
    for ruta, funcion in ((RAIZ / "cli.py", "_prevuelo"),
                          (RAIZ / "gui" / "app.py", "_pintar_anticipo")):
        arbol = ast.parse(ruta.read_text(encoding="utf-8-sig"))
        nodo = next(n for n in ast.walk(arbol)
                    if isinstance(n, ast.FunctionDef) and n.name == funcion)
        llamada = next(n for n in ast.walk(nodo) if isinstance(n, ast.Call)
                       and ast.unparse(n.func).endswith("datos_faltantes_por_punto"))
        assert any(kw.arg == "hidrologia" for kw in llamada.keywords), ruta.name


@pytest.fixture
def app():
    return doble_tkinter.gui_app()


def test_la_ventana_pinta_las_filas_de_la_fase_1bis(app, tmp_path):
    from tests.test_ui1_hidrologia_ventana import _ventana
    v = _ventana(app, csv_=_puntos(tmp_path), cuencas=CUENCAS, estacion=ESTACION)
    v._pintar_anticipo()
    filas = list(v.tree_prevuelo.filas.values())
    del_fen = [f for f in filas if f[1] == FEN]
    assert {f[0].split(" ")[0] for f in del_fen} == set(OBRAS_CON_CUENCA)
    assert all(f[2] == "DETIENE" and f[3] == servicio.ETAPA_CAUDAL_CALCULADO
               for f in del_fen)
