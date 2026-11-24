"""
tests/test_ve5_m6_figura_10_3.py
================================
VE-5 (lote m6): la FIGURA 10.3 de HEC-14 (atenuacion de la velocidad del
eje aguas abajo de una salida sumergida) y la Ec. (10.6), para los dos
casos en que la fuente las manda usar:

  * el apron con el tirante del receptor sobre 1.0·D (Sec. 10.2: «Figure
    10.3 should be used to determine the velocity downstream of the
    culvert»), que hasta aqui salia como metodo no evaluable;
  * el paso 5 de la poza con TW/yo > 0.75 (num. 10.1.5).

ORACULOS: los cuatro puntos que la fuente imprime leyendo su figura y las
tablas de piedra de sus dos ejemplos de la poza (pags. impresas 10-8 y
10-11, PDF 209 y 212), y la Ec. (10.6) aplicada en ellas.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from src import servicio
from src.constantes_normativas import V_MAX_NO_REVESTIDOS
from src.modelos import (
    ControlGobernante, DatoFaltanteError, Magnitud, MetodoNoEvaluableError,
    SeccionCircular, SeccionRectangular)
from src.modulos import M6_proteccion as M6

REL_LECTURA = 2.5e-2   # la figura leida por imagen y los redondeos del ejemplo
REL_FORMULA = 1e-9
# La inversa en log-log deshace la directa salvo el redondeo de exp/log.
REL_INVERSA = 1e-6
M_POR_FT = 0.3048


def _V(valor):
    return Magnitud("V_salida", valor, "m/s", "dato del ejemplo resuelto")


@pytest.mark.parametrize("x, f", [(10, 0.59), (15, 0.42), (20, 0.30),
                                  (21, 0.28), (60, 0.10), (1, 1.0)])
def test_los_puntos_que_la_fuente_imprime(x, f):
    assert M6.atenuacion_figura_10_3(x) == pytest.approx(f, rel=REL_FORMULA)


def test_la_curva_baja_siempre_y_su_inversa_la_deshace():
    xs = [1.5, 2.5, 4.5, 7.5, 11, 17, 25, 45]
    fs = [M6.atenuacion_figura_10_3(x) for x in xs]
    assert all(a > b for a, b in zip(fs, fs[1:]))
    for x, f in zip(xs, fs):
        assert M6.distancia_figura_10_3(f) == pytest.approx(x, rel=REL_INVERSA)


def test_mas_alla_de_la_figura_no_se_extrapola():
    with pytest.raises(MetodoNoEvaluableError):
        M6.atenuacion_figura_10_3(80)
    with pytest.raises(MetodoNoEvaluableError):
        M6.distancia_figura_10_3(0.05)


@pytest.mark.parametrize("VL, D50", [(4.50, 0.43), (3.20, 0.22)])
def test_la_ec_10_6_contra_la_tabla_del_ejemplo_si(VL, D50):
    """Pag. 10-8: VL = 4.50 m/s -> 0.43 m; 3.20 -> 0.22 (S = 2.65)."""
    assert M6.d50_ec_10_6(V=VL) == pytest.approx(D50, rel=REL_LECTURA)


def test_la_poza_del_marco_si_con_el_tw_alto_protege_hasta_41_m():
    """
    Pags. 10-8: TW = 1.28 m, TW/yo = 1.05; De = 1.95 m; «Protection must
    extend at least 41.0 m downstream from the culvert brink» con Vallow =
    2.1 m/s. El ejemplo se queda en la seccion tabulada L/De = 21 (VL =
    2.13); el programa resuelve VL = 2.1 sobre la curva: 41.6 m.
    """
    p = M6.poza_de_enrocado_hec14(
        V=_V(7.63), Q_celda=22.7, seccion=SeccionRectangular(B=2.44, H=1.83),
        TW=1.28, y_salida=1.22, d50_piedra=0.55, origen_piedra="ejemplo",
        V_admisible=2.1)
    assert p.proteccion_adicional is True
    assert p.proteccion_adicional_hasta == pytest.approx(41.0, rel=REL_LECTURA)
    assert p.D50_proteccion_adicional is not None
    assert any("Figura 10.3" in a and "llega hasta" in a for a in p.avisos)


def test_la_poza_del_marco_cu_con_el_tw_alto_protege_hasta_135_pies():
    """Pag. 10-11: Vo = 25 ft/s, De = 6.4 ft, Vallow = 7 ft/s -> 135 ft."""
    ft = M_POR_FT
    p = M6.poza_de_enrocado_hec14(
        V=_V(25 * ft), Q_celda=800 * ft ** 3,
        seccion=SeccionRectangular(B=8 * ft, H=6 * ft), TW=4.2 * ft,
        y_salida=4 * ft, d50_piedra=1.83 * ft, origen_piedra="ejemplo",
        V_admisible=7.0 * ft)
    assert p.proteccion_adicional_hasta / ft == pytest.approx(
        135, rel=REL_LECTURA)


def test_el_apron_con_el_tw_alto_se_dimensiona_por_la_figura():
    """
    Tubo de 0.90 m, Q = 1.0, Vo = 2.0 m/s, TW = 1.2 m > D. A = 0.5 m2, De =
    0.798 m; Vallow = 1.0 -> VL/Vo = 0.5 -> L/De = 12 -> L = 9.58 m. D50 =
    0.692/1.65·2.0²/(2·9.81) = 0.0855 m.

    El espesor, desde N3: max(2·D50, 0.30 m), el piso de HEC-11 Sec. 4.3
    (PDF 48) [C] aplicado por analogia; con esta piedra 2·D50 = 0.171 m y
    gobiernan los 300 mm «for practical placement». El +50 % bajo agua no se
    aplica y se avisa con la frase de la fuente.
    """
    t = M6.proteccion_tw_alto_hec14(V=_V(2.0), Q_celda=1.0, TW=1.2,
                                    V_admisible=1.0)
    De = (4 * 0.5 / 3.141592653589793) ** 0.5
    assert M6.diametro_equivalente(0.5) == pytest.approx(De, rel=REL_FORMULA)
    assert t.De == pytest.approx(De, rel=REL_FORMULA)
    assert t.longitud == pytest.approx(12 * De, rel=REL_FORMULA)
    assert t.D50 == pytest.approx(0.692 / 1.65 * 4.0 / (2 * 9.81), rel=REL_FORMULA)
    assert 2 * t.D50 < 0.30
    assert t.espesor == pytest.approx(0.30, rel=REL_FORMULA)
    assert [x.codigo for x in t.pasos] == ["6.5t"]
    assert "HEC11.4.3#300_MM" in t.pasos[0].citas_textuales
    assert "analogia" in t.pasos[0].nota_del_proyecto.lower()
    assert len(t.avisos) == 1 and "underwater" in t.avisos[0]


def test_con_una_piedra_grande_el_tw_alto_conserva_el_piso_de_2_D50():
    """--- N3 --- Vo = 4 m/s: D50 = 0.342 m, 2·D50 = 0.684 m > 0.30 m."""
    t = M6.proteccion_tw_alto_hec14(V=_V(4.0), Q_celda=1.0, TW=1.2,
                                    V_admisible=1.0)
    assert t.espesor == pytest.approx(2 * t.D50, rel=REL_FORMULA)


def test_sin_la_admisible_el_tw_alto_pide_el_terreno():
    with pytest.raises(DatoFaltanteError) as e:
        M6.proteccion_tw_alto_hec14(V=_V(2.0), Q_celda=1.0, TW=1.2,
                                    V_admisible=None)
    assert e.value.campo == "tipo_terreno_receptor"


RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_ANCHOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"


@pytest.fixture(scope="module")
def corrida_base(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("ve5f103") / "externos.json"
    ruta.write_text(EXTERNOS_ANCHOS.read_text(encoding="utf-8"),
                    encoding="utf-8")
    return servicio.correr(
        CSV, servicio.cargar_datos_externos(ruta, {"luz_m": 2.75}), "perfil")


def _resultado(corrida_base, **cambios):
    p = next(x for x in corrida_base.puntos if x.punto.id == "A-01")
    base = dict(control_gobernante=ControlGobernante.SALIDA,
                V_salida_cota_inferior=False, numero_celdas=1)
    base.update(cambios)
    return replace(p.resultado.resultado_hidraulico, **base)


def test_la_fase_6_con_el_tw_alto_forma_la_envolvente(corrida_base):
    r = _resultado(corrida_base, Q=1.0, Q_celda_m3s=1.0, TW_m=1.2,
                   y_salida_m=0.9, y_critico=0.55, V_salida=_V(2.0))
    clave = next(iter(V_MAX_NO_REVESTIDOS))
    p = M6.proteccion_salida(V=r.V_salida, resultado=r,
                             seccion=SeccionCircular(0.9),
                             tipo_terreno=clave, regimen_flujo="permanente")
    assert p.apron is None and p.tw_alto is not None
    assert p.rige_la_envolvente
    assert p.longitud == pytest.approx(max(5.0, p.tw_alto.longitud),
                                       rel=REL_FORMULA)
    assert "6.5t" in [x.codigo for x in p.pasos]
    assert any("Figura 10.3" in a and "rige la envolvente" in a
               for a in p.avisos)


def test_la_fase_6_con_el_tw_alto_y_sin_terreno_avisa(corrida_base):
    r = _resultado(corrida_base, Q=1.0, Q_celda_m3s=1.0, TW_m=1.2,
                   y_salida_m=0.9, y_critico=0.55, V_salida=_V(2.0))
    p = M6.proteccion_salida(V=r.V_salida, resultado=r,
                             seccion=SeccionCircular(0.9))
    assert p.tw_alto is None and not p.rige_la_envolvente
    assert any("NO se evaluo" in a and "tipo_terreno_receptor" in a
               for a in p.avisos)
