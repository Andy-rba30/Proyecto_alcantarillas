"""
tests/test_ve6_refinamiento_longitud.py
=======================================
VE-6 (integrador), item 22 del censo de pendientes (fichas T6-01 y T7A-06):
LA PASADA DE REFINAMIENTO DEL CONTROL DE SALIDA CON LA LONGITUD ENTRE
CABEZALES.

Rojo medido contra la base `3ce07b5` (sin los cambios de `src/`): los seis
tests en error, porque `servicio._fase_9_refinamiento` y
`M4.refinar_con_longitud_entre_cabezales` no existian. Los oraculos van por
caminos independientes del que se prueba:

  * el TW con la longitud entre cabezales, por la RESTA escrita a mano
    (cota_TW - (cota de entrada - S·L_cab));
  * la carga refinada, contra OTRA CORRIDA del pipeline entero con
    `longitud_m` = L_cab declarada por punto (7.B con longitud declarada, el
    TW de la Sec. 1.3 y el bucle de MD), que es lo que la ficha T6-01 decia
    que habia que hacer a mano;
  * el aviso, con la formula del control de salida escrita en el test
    (H + TW - S·L, con H = (1 + ke + 19.63·n²·L/R^(4/3))·V²/2g a seccion
    llena) sobre un caso en que la carga sube.
"""

import json
import math
from pathlib import Path

import pytest

import cli
from src import servicio
from src.constantes_fisicas import G
from src.constantes_normativas import K_FRICCION_SI
from src.modelos import ControlGobernante
from src.modulos import M4_control as M4
from src.modulos import M11_reporte as M11

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
FILA_A01 = "A-01,0+380,A,1.167,850,0.006,42.10,44.20,44.05,8.5,15,9.60,41.30,,,SM,,,"
# La cota de agua del receptor en A-01: el TW sale por la via 2 de la Sec.
# 1.3 (la resta), y con la longitud menor la solera de salida sube.
COTA_TW_A01 = 42.40
COTA_ENTRADA_A01 = 42.10      # el terreno: `cota_fondo_entrada` va vacia
S_A01 = 0.006
REL = 1e-9


@pytest.fixture(scope="module")
def csv_cota_tw(tmp_path_factory):
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    assert FILA_A01 + "\n" in texto
    fila = FILA_A01.replace(",41.30,,,SM,", f",41.30,,{COTA_TW_A01},SM,")
    ruta = tmp_path_factory.mktemp("ve6") / "puntos_cota_tw.csv"
    ruta.write_text(texto.replace(FILA_A01 + "\n", fila + "\n"),
                    encoding="utf-8")
    return ruta


@pytest.fixture(scope="module")
def a01(csv_cota_tw):
    externos = cli.cargar_datos_externos(None, {"luz_m": 2.75})
    informe = cli.correr(csv_cota_tw, externos, alcance=cli.ALCANCE_PERFIL)
    punto = next(p for p in informe.puntos if p.punto.id == "A-01")
    assert punto.dimensionado, [b.mensaje for b in punto.bloqueos]
    assert "cota_TW" in punto.tw.origen or "1.3" in punto.tw.origen
    servicio._fase_9(punto, externos)
    assert punto.cabezal is not None, [b.mensaje for b in punto.bloqueos]
    servicio._fase_9_refinamiento(punto, externos)
    return punto


def test_el_tw_se_rehace_con_la_solera_de_salida_de_la_longitud_entre_cabezales(a01):
    ref = a01.refinamiento_longitud
    assert ref is not None
    L_cab = a01.cabezal.longitud_entre_cabezales
    assert ref.L_cabezales_m == pytest.approx(L_cab, rel=REL)
    assert ref.L_diseno_m == pytest.approx(a01.longitud.valor, rel=REL)
    # la resta, a mano
    assert ref.TW_cabezales_m == pytest.approx(
        COTA_TW_A01 - (COTA_ENTRADA_A01 - S_A01 * L_cab), rel=REL)
    assert ref.TW_diseno_m == pytest.approx(
        COTA_TW_A01 - (COTA_ENTRADA_A01 - S_A01 * a01.longitud.valor),
        rel=REL)
    # la solera sube S·ΔL: el TW baja lo mismo (centimetros)
    assert ref.TW_diseno_m - ref.TW_cabezales_m == pytest.approx(
        S_A01 * (a01.longitud.valor - L_cab), rel=REL)


def test_la_carga_refinada_es_la_de_declarar_longitud_m_igual_a_l_cab(
        a01, csv_cota_tw, tmp_path):
    """El camino independiente: otra corrida con `longitud_m` = L_cab."""
    ref = a01.refinamiento_longitud
    L_cab = a01.cabezal.longitud_entre_cabezales
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps({"puntos": {"A-01": {"longitud_m": L_cab}}}),
                    encoding="utf-8")
    externos = cli.cargar_datos_externos(ruta, {"luz_m": 2.75})
    otra = cli.correr(csv_cota_tw, externos, alcance=cli.ALCANCE_PERFIL)
    q = next(p for p in otra.puntos if p.punto.id == "A-01")
    assert q.dimensionado
    assert q.resultado.seccion.etiqueta() == a01.resultado.seccion.etiqueta()
    assert q.resultado.material.nombre == a01.resultado.material.nombre
    r = q.resultado.resultado_hidraulico
    assert r.TW_m == pytest.approx(ref.TW_cabezales_m, rel=REL)
    assert r.HW_salida == pytest.approx(ref.HW_salida_cabezales_m, rel=REL)
    assert r.HW == pytest.approx(ref.HW_cabezales_m, rel=REL)
    assert r.control_gobernante is ref.control_cabezales


def test_el_diseno_no_se_sustituye(a01):
    ref = a01.refinamiento_longitud
    r = a01.resultado.resultado_hidraulico
    assert ref.HW_diseno_m == r.HW
    assert ref.HW_salida_diseno_m == r.HW_salida
    assert ref.control_diseno is r.control_gobernante
    # la longitud del diseño sigue siendo la aproximada de 7.B
    assert a01.longitud.valor == pytest.approx(
        a01.longitud_calculada.longitud, rel=REL)
    assert a01.longitud.valor > ref.L_cabezales_m


def test_el_paso_9_0_6_va_a_la_memoria_y_el_aviso_solo_si_sube(a01):
    ref = a01.refinamiento_longitud
    pasos = [p for p in a01.cabezal.pasos
             if p.fundamento_id == "F9.REFINAMIENTO_LONGITUD"]
    assert len(pasos) == 1 and pasos[0].codigo == "9.0.6"
    html = M11.memoria_de_punto(a01)
    assert "9.0.6" in html
    sube = ref.HW_cabezales_m > ref.HW_diseno_m + 1e-9
    cambia = ref.control_cabezales is not ref.control_diseno
    assert bool(ref.aviso) == (sube or cambia)
    hay = any("Longitud entre cabezales de A-01" in a for a in a01.avisos())
    assert hay == bool(ref.aviso)


def test_sin_cabezal_o_sin_externos_no_corre(a01):
    copia = servicio.InformePunto(punto=a01.punto)
    servicio._fase_9_refinamiento(copia, None)
    assert copia.refinamiento_longitud is None


def test_el_aviso_cuando_la_carga_sube_con_la_formula_escrita(a01):
    """
    La seccion adoptada de A-01 bajo control de salida con el receptor
    sobre la clave: el diseño con TW = 1.10 m y la longitud aproximada, y el
    refinamiento con un TW mayor (un receptor que, con la longitud menor,
    queda mas alto sobre la solera: aqui se fuerza para que la carga suba).
    La carga esperada se escribe con la formula de la Sec. 4.3 a seccion
    llena; con HW/D >= 0.75 la aproximacion no se sustituye por el remanso.
    """
    res = a01.resultado
    seccion, material = res.seccion, res.material
    L, L_cab = a01.longitud.valor, a01.cabezal.longitud_entre_cabezales
    Q, S = res.resultado_hidraulico.Q, res.resultado_hidraulico.S
    TW, TW_cab = 1.10, 1.20
    diseno = M4.resolver_control(seccion=seccion, Q=Q, S=S, L=L, TW=TW,
                                 material=material)
    assert diseno.control_gobernante is ControlGobernante.SALIDA
    ref = M4.refinar_con_longitud_entre_cabezales(
        seccion=seccion, material=material, diseno=diseno, L_diseno=L,
        L_cabezales=L_cab, TW_cabezales=TW_cab, id_punto="A-01")
    D = seccion.altura
    A = math.pi * D ** 2 / 4
    V, R = Q / A, D / 4
    ke = M4.ke_declarado(M4.criterio_ke_de(material))[3]
    n = material.n_para_capacidad
    H = (1 + ke + K_FRICCION_SI * n ** 2 * L_cab / R ** (4 / 3)) \
        * V ** 2 / (2 * G)
    esperado = H + TW_cab - S * L_cab
    assert ref.HW_salida_cabezales_m == pytest.approx(esperado, rel=1e-6)
    assert ref.HW_cabezales_m > ref.HW_diseno_m
    assert "declarar `longitud_m`" in ref.aviso
    assert f"{L_cab:.3f}" in ref.aviso
