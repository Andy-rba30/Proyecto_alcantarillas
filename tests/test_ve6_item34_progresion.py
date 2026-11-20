"""
tests/test_ve6_item34_progresion.py
===================================
VE-6 (integrador), item 34 del censo de pendientes: lo que la progresion del
catalogo y el delta de rasante dejaban abierto (fichas VE3-08, T11-03 (2) y
VE3-13). Tres cierres, cada uno con su oraculo por un camino independiente:

  * H8 de los ensayos del conducto: la COBERTURA MINIMA (G1 de 7.A) dentro del
    bucle. Un escalon que cumple toda la Fase 5 pero cuya clave no deja la
    cobertura bajo la rasante no se adopta: el material se descarta POR
    RASANTE con el delta de G1, que se escribe a mano (clave + h_rec + e_paq
    - rasante). Un escalon mayor sube la clave y nunca lo mejora.
  * H7: la progresion se detiene con V10 incumplida. V10 juzga la pendiente
    con que corrio el diseño (`resultado.S`), la misma en todo escalon: un
    diametro mayor no la cambia. Se fija con un verificador falso que cuenta
    los escalones.
  * T11-03 (2) / VE3-08 (H3 a): el delta de rasante del escalon que no cabe
    y solo incumple V4, cuando gobierna el control de ENTRADA: el HW no
    depende de la longitud y el delta del resguardo es cota inferior para ese
    escalon. Oraculo: entrada + HW + resguardo + e_paq - rasante, escrito.
    Bajo control de SALIDA sigue sin darse (el HW cambia con la longitud).

Rojo medido contra la base (sin los cambios de `src/` de este item): fallan
los cuatro tests de los cierres; los tres de control pasan en la base.
"""

import dataclasses

import pytest

import cli
from pathlib import Path
from src.modelos import ControlGobernante, Verificacion
from src.modulos import MD
from src.modulos import M5_verificaciones as M5
from src.modulos import M7_geometria as M7
from src.modulos.M2_material import espesor_pared

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
REL = 1e-9


@pytest.fixture(scope="module")
def corrida():
    externos = cli.cargar_datos_externos(None, {"luz_m": 2.75, "TW_m": 0.3})
    return cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)


def _punto(corrida, id_punto):
    p = next(x for x in corrida.puntos if x.punto.id == id_punto)
    assert p.dimensionado
    return p


@pytest.fixture(scope="module")
def a01(corrida):
    return _punto(corrida, "A-01")


@pytest.fixture(scope="module")
def b01(corrida):
    return _punto(corrida, "B-01")


def _v(codigo, cumple):
    return Verificacion(cumple=cumple, numeral="caso de prueba",
                        valor_obtenido=0.0, valor_admisible=0.0,
                        criterio_aplicado=None, codigo=codigo)


def _todo_cumple(**_):
    return [_v("V1", True), _v("V4", True), _v("V7", True)]


def _correr_material(a01, punto, verificar):
    r = a01.resultado.resultado_hidraulico
    escalones = []
    res, motivo = MD.disenar_material(
        punto, a01.resultado.material, Q=r.Q, S=r.S, L=a01.longitud.valor,
        TW=r.TW_m, verificar=verificar, registrar=escalones.append)
    return res, motivo, escalones


# ===========================================================================
# H8: G1 dentro del bucle
# ===========================================================================

def test_con_la_rasante_del_csv_el_escalon_sigue_adoptandose(a01):
    res, _motivo, _ = _correr_material(a01, a01.punto_de_calculo,
                                       _todo_cumple)
    assert res is not None and res.aceptado


def test_el_escalon_sin_cobertura_bajo_la_rasante_no_se_adopta(b01):
    # B-01 (HW 0.23 m: manda la cobertura) con la rasante 0.90 m mas baja:
    # la clave del Ø 0.90 cabe bajo la subrasante y el resguardo se cumple
    # (V4, la condicion de 7.A escrita al reves, cumple), pero la cobertura
    # minima no
    base = b01.punto_de_calculo
    punto = dataclasses.replace(base, cota_rasante=base.cota_rasante - 0.90,
                                cota_subrasante=base.cota_subrasante - 0.90)
    material = b01.resultado.material
    seccion = b01.resultado.seccion
    clave = M5.cota_clave(punto=punto, material=material, seccion=seccion)
    assert punto.cota_subrasante - clave > 0          # cabe
    e_paq = punto.cota_rasante - punto.cota_subrasante
    resguardo = M7.resguardo_por_cbr(punto.cbr_subrasante)
    HW = b01.resultado.resultado_hidraulico.HW
    assert 38.40 + HW + resguardo + e_paq < punto.cota_rasante   # V4 cumple
    res, motivo, escalones = _correr_material(b01, punto, _todo_cumple)
    assert res is None
    assert motivo.startswith(MD.MENSAJE_SIN_CABIDA)
    ultimo = escalones[-1]
    assert ultimo.sin_cabida is not None and ultimo.sin_cabida.por_cobertura
    assert len(escalones) == 1             # el primero; no sigue creciendo
    # el delta, escrito: clave + h_rec + e_paq - rasante
    h_rec, _ = M7.altura_recubrimiento(material=material, seccion=seccion)
    t = espesor_pared(material, seccion.altura)
    clave_escrita = 38.40 + seccion.altura + t       # entrada = terreno
    assert clave == pytest.approx(clave_escrita, rel=REL)
    assert ultimo.sin_cabida.delta_rasante_m == pytest.approx(
        clave_escrita + h_rec + e_paq - punto.cota_rasante, rel=REL)
    assert "cobertura" in motivo


# ===========================================================================
# H7: V10 detiene la progresion
# ===========================================================================

def test_v10_incumplida_detiene_la_progresion(a01):
    def verificar(**_):
        return [_v("V1", True), _v("V10", False)]

    res, motivo, escalones = _correr_material(a01, a01.punto_de_calculo,
                                              verificar)
    assert res is None
    assert len(escalones) == 1
    assert "V10" in motivo and "no depende" in motivo


def test_otra_falla_sigue_recorriendo_el_catalogo(a01):
    def verificar(**_):
        return [_v("V1", False), _v("V10", True)]

    _res, _motivo, escalones = _correr_material(a01, a01.punto_de_calculo,
                                                verificar)
    assert len(escalones) > 1


# ===========================================================================
# T11-03 (2): el delta con V4 bajo control de entrada
# ===========================================================================

def _punto_bajo(a01, bajar):
    base = a01.punto_de_calculo
    return dataclasses.replace(base, cota_rasante=base.cota_rasante - bajar,
                               cota_subrasante=base.cota_subrasante - bajar)


def test_el_delta_del_resguardo_bajo_control_de_entrada(a01):
    r = a01.resultado.resultado_hidraulico
    assert r.control_gobernante is ControlGobernante.ENTRADA
    material, seccion = a01.resultado.material, a01.resultado.seccion
    punto = _punto_bajo(a01, 1.20)
    resguardo = M7.resguardo_por_cbr(punto.cbr_subrasante)
    e_paq = punto.cota_rasante - punto.cota_subrasante
    por_resguardo = 42.10 + r.HW + resguardo + e_paq
    h_rec, _ = M7.altura_recubrimiento(material=material, seccion=seccion)
    por_recubrimiento = (M5.cota_clave(punto=punto, material=material,
                                       seccion=seccion) + h_rec + e_paq)
    assert por_resguardo > por_recubrimiento           # gobierna el resguardo
    delta, nota = MD._delta_de_7A(punto, material, seccion,
                                  [_v("V1", True), _v("V4", False)], r)
    assert delta == pytest.approx(por_resguardo - punto.cota_rasante, rel=REL)
    assert "resguardo" in nota and "ENTRADA" in nota.upper()


def test_el_delta_del_resguardo_no_se_da_bajo_control_de_salida(a01):
    r = dataclasses.replace(a01.resultado.resultado_hidraulico,
                            control_gobernante=ControlGobernante.SALIDA)
    material, seccion = a01.resultado.material, a01.resultado.seccion
    delta, nota = MD._delta_de_7A(_punto_bajo(a01, 1.20), material, seccion,
                                  [_v("V1", True), _v("V4", False)], r)
    assert delta is None
    assert "longitud" in nota


def test_con_otra_falla_ademas_de_v4_no_hay_delta(a01):
    r = a01.resultado.resultado_hidraulico
    material, seccion = a01.resultado.material, a01.resultado.seccion
    delta, _nota = MD._delta_de_7A(_punto_bajo(a01, 1.20), material, seccion,
                                   [_v("V2", False), _v("V4", False)], r)
    assert delta is None
