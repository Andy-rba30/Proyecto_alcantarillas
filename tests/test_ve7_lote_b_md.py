"""
tests/test_ve7_lote_b_md.py
===========================
VE-7, lote B, items B1 y B2 (decision del consultor Fable, triaje VE-7,
2026-11-20), los dos en `MD`:

  * B1 (VE6-34 / T11-03 (5)): la regla del escalon mas bajo de G1 vale
    tambien en la rama «no cabe». Un marco con la serie (B, H) no creciente
    cuyo primer par no cabe bajo la subrasante sigue al par mas bajo y lo
    adopta; en el tubo (progresion ascendente) la traza es identica a la de
    antes. El verificador de prueba levanta la MISMA excepcion que M5 sobre
    `cota_subrasante` cuando la clave no cabe, calculada aqui por geometria
    (`M5.cota_clave` contra la subrasante), y cumple todo lo demas.
  * B2 (VE6-34 / VE3-08 H3a): bajo control de SALIDA el delta del resguardo
    se da con el HW de ENTRADA, cota inferior rigurosa (el HW gobernante
    nunca baja del de entrada, `HDS5_3ED.3.3.5#GOBIERNA`, y este no depende
    de L). Oraculo: entrada + HW_entrada + resguardo + e_paq - rasante,
    escrito a mano; y menor o igual que el que daria el HW gobernante.
"""

import dataclasses
from pathlib import Path

import pytest

import cli
from tests.apoyo.aproximacion import REL_TRANSPORTE
from src.modelos import ControlGobernante, DatoInvalidoError, Verificacion
from src.modulos import MD
from src.modulos import M5_verificaciones as M5
from src.modulos import M7_geometria as M7

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"



def _v(codigo, cumple):
    return Verificacion(cumple=cumple, numeral="caso de prueba",
                        valor_obtenido=0.0, valor_admisible=0.0,
                        criterio_aplicado=None, codigo=codigo)


def _verificador_con_cabida(**kw):
    """Cumple todo, salvo que la clave no quepa: entonces levanta lo de M5."""
    punto, material, seccion = kw["punto"], kw["material"], kw["seccion"]
    clave = M5.cota_clave(punto=punto, material=material, seccion=seccion)
    if not punto.cota_subrasante - clave > 0:
        exc = DatoInvalidoError(MD.CAMPO_SUBRASANTE,
                                valor=punto.cota_subrasante,
                                motivo="la clave no cabe bajo la subrasante")
        exc.verificaciones_completadas = (_v("V1", True), _v("V4", True))
        raise exc
    return [_v("V1", True), _v("V4", True), _v("V7", True)]


# ===========================================================================
# B1
# ===========================================================================

@pytest.fixture(scope="module")
def corrida():
    externos = cli.cargar_datos_externos(None, {"luz_m": 2.75, "TW_m": 0.3})
    return cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)


def _punto(corrida, id_punto):
    p = next(x for x in corrida.puntos if x.punto.id == id_punto)
    assert p.dimensionado
    return p


def test_b1_en_el_marco_el_par_mas_bajo_se_adopta_tras_uno_que_no_cabe(
        tmp_path):
    from tests.apoyo.criterios import declarados
    from tests.test_canal_discrepancias import DECLARACIONES_DEL_CAJON
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    fila = "C-01,3+100,C,,,,36.90,39.10,38.95,6.5,30,9.60,36.20,,,ML,,,"
    csv = tmp_path / "c01.csv"
    csv.write_text(texto.replace(fila + "\n", fila + "38.30\n"),
                   encoding="utf-8")
    externos = cli.cargar_datos_externos(
        RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json",
        {"luz_m": 2.75})
    serie = [[1.20, 0.90], [1.50, 0.60], [2.00, 1.50]]
    with declarados(dict(DECLARACIONES_DEL_CAJON,
                         secciones_cajon_normalizadas=serie)):
        informe = cli.correr(csv, externos, alcance=cli.ALCANCE_PERFIL)
        c01 = informe.puntos[3]
        assert c01.dimensionado, [b.mensaje for b in c01.bloqueos]
        material = c01.resultado.material
        r = c01.resultado.resultado_hidraulico
        base = c01.punto_de_calculo
        primero = c01.traza[0].seccion
        segundo = MD.siguiente_seccion(material, primero)
        assert segundo.H < primero.H
        clave_1 = M5.cota_clave(punto=base, material=material,
                                seccion=primero)
        clave_2 = M5.cota_clave(punto=base, material=material,
                                seccion=segundo)
        e_paq = base.cota_rasante - base.cota_subrasante
        # la subrasante BAJO la clave del primero (no cabe) y sobre la del
        # segundo (cabe): escrito a mano, no por MD
        sub = (clave_1 + clave_2) / 2
        assert sub < clave_1 and sub > clave_2
        punto = dataclasses.replace(base, cota_subrasante=sub,
                                    cota_rasante=sub + e_paq)
        escalones = []
        res, motivo = MD.disenar_material(
            punto, material, Q=r.Q, S=r.S, L=c01.longitud.valor, TW=r.TW_m,
            verificar=_verificador_con_cabida, registrar=escalones.append)
    assert escalones[0].sin_cabida is not None
    assert not escalones[0].sin_cabida.por_cobertura     # rama «no cabe»
    assert "mas bajo" in escalones[0].motivo
    assert "la progresion sigue" in escalones[0].motivo
    assert res is not None and res.aceptado, motivo
    assert res.seccion.H == pytest.approx(0.60, rel=REL_TRANSPORTE)


def test_b1_sin_par_mas_bajo_el_marco_se_descarta_por_rasante(tmp_path):
    from tests.apoyo.criterios import declarados
    from tests.test_canal_discrepancias import DECLARACIONES_DEL_CAJON
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    fila = "C-01,3+100,C,,,,36.90,39.10,38.95,6.5,30,9.60,36.20,,,ML,,,"
    csv = tmp_path / "c01.csv"
    csv.write_text(texto.replace(fila + "\n", fila + "38.30\n"),
                   encoding="utf-8")
    externos = cli.cargar_datos_externos(
        RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json",
        {"luz_m": 2.75})
    serie = [[1.20, 0.90], [1.50, 1.20], [2.00, 1.50]]      # creciente
    with declarados(dict(DECLARACIONES_DEL_CAJON,
                         secciones_cajon_normalizadas=serie)):
        informe = cli.correr(csv, externos, alcance=cli.ALCANCE_PERFIL)
        c01 = informe.puntos[3]
        material = c01.resultado.material
        r = c01.resultado.resultado_hidraulico
        base = c01.punto_de_calculo
        primero = c01.traza[0].seccion
        clave_1 = M5.cota_clave(punto=base, material=material,
                                seccion=primero)
        e_paq = base.cota_rasante - base.cota_subrasante
        sub = clave_1 - 0.05
        punto = dataclasses.replace(base, cota_subrasante=sub,
                                    cota_rasante=sub + e_paq)
        escalones = []
        res, motivo = MD.disenar_material(
            punto, material, Q=r.Q, S=r.S, L=c01.longitud.valor, TW=r.TW_m,
            verificar=_verificador_con_cabida, registrar=escalones.append)
    assert res is None
    assert motivo.startswith(MD.MENSAJE_SIN_CABIDA)
    assert len(escalones) == 1
    assert "la progresion sigue" not in escalones[0].motivo


def test_b1_en_el_tubo_la_traza_es_la_de_t11_03(corrida):
    """
    El tubo es ascendente: el primer escalon que no cabe termina la
    progresion con el motivo de T11-03, palabra por palabra (el texto se
    arma aqui con las mismas piezas y sin la cola de B1).
    """
    a01 = _punto(corrida, "A-01")
    r = a01.resultado.resultado_hidraulico
    base = a01.punto_de_calculo
    material = a01.resultado.material
    primero = a01.traza[0].seccion
    clave_1 = M5.cota_clave(punto=base, material=material, seccion=primero)
    e_paq = base.cota_rasante - base.cota_subrasante
    sub = clave_1 + 0.01         # el primero cabe; el siguiente (mayor) no
    punto = dataclasses.replace(base, cota_subrasante=sub,
                                cota_rasante=sub + e_paq)
    escalones = []
    res, motivo = MD.disenar_material(
        punto, material, Q=r.Q, S=r.S, L=a01.longitud.valor, TW=r.TW_m,
        verificar=lambda **kw: (
            [_v("V1", False)] if kw["seccion"].altura == primero.altura
            else _verificador_con_cabida(**kw)),
        registrar=escalones.append)
    assert res is None
    assert motivo.startswith(MD.MENSAJE_SIN_CABIDA)
    assert len(escalones) == 2
    ultimo = escalones[-1]
    assert ultimo.sin_cabida is not None
    assert ultimo.motivo == (
        f"{MD._lugar_sin_cabida(ultimo.seccion, ultimo.sin_cabida)}: no hay "
        "relleno sobre la clave, y la verificacion que lo pesa y las que la "
        "siguen en la tabla no se evaluan; lo que se le evaluo antes cumple")


# ===========================================================================
# B2
# ===========================================================================

def _punto_bajo(a01, bajar):
    base = a01.punto_de_calculo
    return dataclasses.replace(base, cota_rasante=base.cota_rasante - bajar,
                               cota_subrasante=base.cota_subrasante - bajar)


def test_b2_bajo_salida_el_delta_es_el_del_hw_de_entrada(corrida):
    a01 = _punto(corrida, "A-01")
    r0 = a01.resultado.resultado_hidraulico
    # Un resultado bajo control de SALIDA con el HW de salida MAYOR que el de
    # entrada (lo que el control de salida significa)
    r = dataclasses.replace(r0, control_gobernante=ControlGobernante.SALIDA,
                            HW_salida=r0.HW_entrada + 0.40)
    assert r.HW == pytest.approx(r0.HW_entrada + 0.40, rel=REL_TRANSPORTE)
    material, seccion = a01.resultado.material, a01.resultado.seccion
    punto = _punto_bajo(a01, 1.20)
    resguardo = M7.resguardo_por_cbr(punto.cbr_subrasante)
    e_paq = punto.cota_rasante - punto.cota_subrasante
    con_entrada = 42.10 + r0.HW_entrada + resguardo + e_paq
    con_gobernante = 42.10 + r.HW + resguardo + e_paq
    delta, nota = MD._delta_de_7A(punto, material, seccion,
                                  [_v("V1", True), _v("V4", False)], r)
    assert delta == pytest.approx(con_entrada - punto.cota_rasante, rel=REL_TRANSPORTE)
    assert delta <= con_gobernante - punto.cota_rasante
    assert "cota inferior con el HW de entrada" in nota


def test_b2_si_con_el_hw_de_entrada_el_resguardo_cabe_no_hay_delta(corrida):
    a01 = _punto(corrida, "A-01")
    r0 = a01.resultado.resultado_hidraulico
    r = dataclasses.replace(r0, control_gobernante=ControlGobernante.SALIDA,
                            HW_salida=r0.HW_entrada + 5.0)
    material, seccion = a01.resultado.material, a01.resultado.seccion
    # la rasante del CSV: con el HW de entrada el resguardo ya cabe
    delta, nota = MD._delta_de_7A(a01.punto_de_calculo, material, seccion,
                                  [_v("V1", True), _v("V4", False)], r)
    assert delta is None
    assert "longitud" in nota


# ===========================================================================
# Dictamen Fable (iii): el catalogo agotado tras un par que no cabe
# ===========================================================================

def _c01_con_serie(tmp_path, serie):
    from tests.apoyo.criterios import declarados
    from tests.test_canal_discrepancias import DECLARACIONES_DEL_CAJON
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    fila = "C-01,3+100,C,,,,36.90,39.10,38.95,6.5,30,9.60,36.20,,,ML,,,"
    csv = tmp_path / "c01.csv"
    csv.write_text(texto.replace(fila + "\n", fila + "38.30\n"),
                   encoding="utf-8")
    externos = cli.cargar_datos_externos(
        RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json",
        {"luz_m": 2.75})
    return declarados(dict(DECLARACIONES_DEL_CAJON,
                           secciones_cajon_normalizadas=serie)), csv, externos


def test_iii_el_par_que_no_cabe_y_el_mas_bajo_que_incumple(tmp_path):
    """Marco [(2 x 2) no cabe, (2 x 1) incumple V1]: el material sale POR
    RASANTE con el delta del 2 x 2, y el punto lleva ese delta."""
    from src.modelos import DisenoNoFactibleError
    ctx, csv, externos = _c01_con_serie(tmp_path, [[2.0, 2.0], [2.0, 1.0]])
    with ctx:
        informe = cli.correr(csv, externos, alcance=cli.ALCANCE_PERFIL)
        c01 = informe.puntos[3]
        base = c01.punto_de_calculo
        assert c01.dimensionado, [b.mensaje for b in c01.bloqueos]
        material = c01.resultado.material
        r = c01.resultado.resultado_hidraulico
        primero = MD.siguiente_seccion(material)
        segundo = MD.siguiente_seccion(material, primero)
        clave_1 = M5.cota_clave(punto=base, material=material, seccion=primero)
        clave_2 = M5.cota_clave(punto=base, material=material, seccion=segundo)
        e_paq = base.cota_rasante - base.cota_subrasante
        sub = (clave_1 + clave_2) / 2
        punto = dataclasses.replace(base, cota_subrasante=sub,
                                    cota_rasante=sub + e_paq)

        def verificar(**kw):
            if kw["seccion"].altura > segundo.altura:
                return _verificador_con_cabida(**kw)
            return [_v("V1", False), _v("V4", True)]
        escalones = []
        res, motivo = MD.disenar_material(
            punto, material, Q=r.Q, S=r.S, L=c01.longitud.valor, TW=r.TW_m,
            verificar=verificar, registrar=escalones.append)
        assert res is None
        assert motivo.startswith(MD.MENSAJE_SIN_CABIDA)
        assert "los escalones mas bajos que quedaban no cierran" in motivo
        delta_2x2 = escalones[0].sin_cabida.delta_rasante_m
        with pytest.raises(DisenoNoFactibleError) as exc:
            MD.disenar_punto(punto, L=c01.longitud.valor, TW=r.TW_m, Q=r.Q,
                             S=r.S, verificar=verificar)
    assert delta_2x2 is not None and delta_2x2 > 0
    assert exc.value.delta_rasante_m == pytest.approx(delta_2x2,
                                                      rel=REL_TRANSPORTE)
    assert MD.MENSAJE_SIN_CABIDA in str(exc.value)
