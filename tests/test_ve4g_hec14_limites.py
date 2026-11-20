"""
tests/test_ve4g_hec14_limites.py
================================
VE-4g: la proteccion de salida de HEC-14 en los casos que el apron de la
Sec. 10.2 no cubre.

QUE DICE LA FUENTE, releido sobre el ejemplar (HEC-14 3a ed.,
FHWA-NHI-06-086), y que hace el programa con cada limite del rotulo
`MOTIVO_METODO_NO_EVALUABLE_HEC14`:

  * CONDUCTO DE MAS DE 60 in DE ALTO y MARCO (seccion rectangular). El apron
    de la Ec. (10.4) sigue sin evaluarse --la Tabla 1.1 lo limita a «Culvert
    rise less than or equal to 1500 mm (60 in)» (nota 8) y la Sec. 10.2 lo
    recomienda «for circular culverts»--, pero la MISMA tabla ofrece para
    esos casos la POZA DE ENROCADO de la Sec. 10.1 («Riprap basin», Froude
    «< 3», sin limite de altura), cuyo procedimiento (num. 10.1.5, pag.
    impresa 10-5) vale para marcos y para tubos: el tirante equivalente ye
    se define «to permit use of the same design relationships for
    rectangular and circular culverts» (pag. 10-2), y sus dos ejemplos
    resueltos son un marco de 2440 x 1830 mm y un tubo de 1830 mm, mayor que
    60 in. VE-4g la implementa: `M6.poza_de_enrocado_hec14`.
  * VARIOS BARRILES. Ninguna fuente del repositorio de normas da un
    procedimiento: los ensayos de la poza son de UN conducto (num. 10.1.1),
    los del apron y los del Cap. 5 tambien, y el HDS-5 solo reparte el
    caudal entre barriles para la hidraulica. El limite QUEDA, en el apron,
    en la poza y en la hoya.
  * TW SOBRE 1.0·D en un tubo de hasta 60 in: la fuente remite a la Figura
    10.3, que no esta digitalizada. QUEDA.
  * IP fuera de 5-16 y caida de mas de 4 alturas (Tabla 5.2): la fuente
    limita sus ecuaciones y no da otra. QUEDAN.

DE DONDE SALE CADA ORACULO, porque ninguno es la salida del codigo: los
cuatro ejemplos resueltos de la poza (pags. impresas 10-6 a 10-16, PDF 207
a 217), en SI y en unidades inglesas, y la aritmetica escrita en el
docstring de cada test.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from src import criterios_adoptados as ca
from src import servicio
from src.constantes_normativas import (
    HEC14_POZA_CO, HEC14_POZA_D50_SOBRE_YE_MIN, HEC14_POZA_FROUDE_MAX,
    V_MAX_NO_REVESTIDOS)
from src.modelos import (
    ControlGobernante, Magnitud, MOTIVO_METODO_NO_EVALUABLE_HEC14,
    MetodoNoEvaluableError, SeccionCircular, SeccionRectangular,
    TipoDeVeredicto)
from src.modulos import M6_proteccion as M6
from src.normativa import registro as _registro

# Tolerancias de este archivo, nombradas (CLAUDE.md).
# Los ejemplos resueltos redondean ye, Fr y hs/ye a dos o tres cifras y
# arrastran el redondeo (hs = 1.55·1.22 = 1.89 m contra 1.879 m sin
# redondear): 1.5 % cubre ese arrastre y no mas.
REL_EJEMPLO_POZA = 1.5e-2
REL_FORMULA = 1e-9           # una formula recomputada a mano en el test
REL_ARITMETICA = 1e-3        # la aritmetica escrita con cuatro cifras

M_POR_FT = 0.3048            # exacto por definicion
CRITERIO_CO = "relacion_co_poza_enrocado_hec14"
CRITERIO_REGLA = "regla_espesor_longitud_proteccion_salida"


def _V(valor: float) -> Magnitud:
    return Magnitud("V_salida", valor, "m/s", "dato del ejemplo resuelto")


def _con_criterio(clave, valor, funcion):
    ca.establecer_valor_dinamico(clave, valor)
    try:
        return funcion()
    finally:
        ca.quitar_valor_dinamico(clave)


# ===========================================================================
# 1 · La poza contra los ejemplos resueltos de HEC-14 (Sec. 10.1)
# ===========================================================================

def test_ejemplo_si_del_marco_en_pendiente_fuerte():
    """
    «Design Example: Riprap Basin (Culvert on a Steep Slope) (SI)», pags.
    impresas 10-6 y 10-7 (PDF 207 y 208): marco de 2440 x 1830 mm, Q = 22.7
    m3/s, yo = ye = 1.22 m, Vo = 7.63 m/s, TW = 0.85 m. Con D50 = 0.55 m:
    Fr = 2.21; TW/ye = 0.7 < 0.75 -> Co = 1.4; hs/ye = 0.86·(0.45)^-0.55·2.21
    - 1.4 = 1.55; hs = 1.89 m; hs/D50 = 3.4 >= 2; LS = 10·hs = 18.9 m (3·Wo
    = 7.3 m); LB = 15·hs = 28.4 m (4·Wo = 9.8 m); WB = 2.44 + 2·28.4/3 =
    21.4 m. El tirante del ejemplo, yo = 1.22 m, es el que sale de Q/(Vo·B)
    = 22.7/(7.63·2.44) = 1.219 m: el programa lo toma por continuidad.
    """
    p = M6.poza_de_enrocado_hec14(
        V=_V(7.63), Q_celda=22.7, seccion=SeccionRectangular(B=2.44, H=1.83),
        TW=0.85, y_salida=1.22, d50_piedra=0.55, origen_piedra="ejemplo")
    assert p.y_equivalente == pytest.approx(1.22, rel=REL_EJEMPLO_POZA)
    assert p.Fr == pytest.approx(2.21, rel=REL_EJEMPLO_POZA)
    assert p.Co == pytest.approx(1.4, rel=REL_FORMULA)
    assert p.D50_dimensionamiento == pytest.approx(0.55, rel=REL_FORMULA)
    assert not p.dimensionada_con_menor and not p.piedra_subida
    assert p.hs == pytest.approx(1.89, rel=REL_EJEMPLO_POZA)
    assert p.longitud_poza == pytest.approx(18.9, rel=REL_EJEMPLO_POZA)
    assert p.longitud_total == pytest.approx(28.4, rel=REL_EJEMPLO_POZA)
    assert p.ancho_final == pytest.approx(21.4, rel=REL_EJEMPLO_POZA)
    assert p.Wo == pytest.approx(2.44, rel=REL_FORMULA)
    # «lined with riprap that is at least 2D50 thick» (pag. 10-1); 3·D50 en
    # el talud de la salida (Figura 10.1 y num. 10.1.4).
    assert p.espesor == pytest.approx(2 * 0.55, rel=REL_FORMULA)
    assert p.espesor_talud == pytest.approx(3 * 0.55, rel=REL_FORMULA)
    # TW/yo = 0.85/1.22 = 0.70 <= 0.75: «No additional riprap needed».
    assert p.proteccion_adicional is False
    # Sin la admisible del terreno el paso 4 no se contrasta: se dice.
    assert p.V_admisible is None and not p.extendida
    assert any("admisible" in a for a in p.avisos)


def test_paso_4_el_tirante_critico_en_la_salida_de_la_poza():
    """
    Paso 4 del mismo ejemplo, sobre el WB IMPRESO (21.4 m) y z = 2 (los
    taludes 2:1 de la Figura 10.2): Q2/g = 52.5 = [yc(21.4 + 2yc)]^3/(21.4 +
    4yc) -> «yc = 0.48 m, Tc = 23.3 m, Ac = 10.7 m2», Vc = 22.7/10.7 = 2.1
    m/s. Y el del tubo SI (pag. 10-12): WB = 9.0 m, Q = 3.82 -> yc = 0.26 m,
    Ac = 2.48 m2.
    """
    yc, A, V = M6.salida_critica_de_la_poza(Q=22.7, ancho_fondo=21.4)
    assert yc == pytest.approx(0.48, rel=REL_EJEMPLO_POZA)
    assert A == pytest.approx(10.7, rel=REL_EJEMPLO_POZA)
    assert V == pytest.approx(22.7 / 10.7, rel=REL_EJEMPLO_POZA)
    # La definicion, recomputada: A^3/T = Q^2/g con A = yc·(b + z·yc).
    T = 21.4 + 2 * 2 * yc
    assert A ** 3 / T == pytest.approx(22.7 ** 2 / 9.81, rel=REL_ARITMETICA)
    yc, A, _ = M6.salida_critica_de_la_poza(Q=3.82, ancho_fondo=9.0)
    assert yc == pytest.approx(0.26, rel=REL_EJEMPLO_POZA)
    assert A == pytest.approx(2.48, rel=REL_EJEMPLO_POZA)


def test_ejemplo_si_del_tubo_de_1830_mm_mayor_que_60_pulgadas():
    """
    «Design Example: Riprap Basin (Culvert on a Mild Slope) (SI)», pags.
    impresas 10-11 a 10-13 (PDF 212 a 214): CMP de 1.83 m --MAS de 60 in, el
    caso que el apron no cubre--, Q = 3.82 m3/s, yo = 0.823 m (Figura 3.4),
    A = 1.15 m2, Vo = 3.32 m/s, ye = (1.15/2)^0.5 = 0.76 m, Fr = 1.22, TW =
    0.61 m. TW/ye = 0.80 -> Co = 4.0·0.80 - 1.6 = 1.61. Con D50 = 0.15 m:
    hs/ye = 0.933, hs = 0.71 m, LS = 7.1 m, LB = 10.7 m, WB = 9.0 m, yc =
    0.26 m, Vc = 1.5 m/s <= 2.1 («acceptable»). TW/yo = 0.61/0.823 = 0.74:
    sin proteccion adicional.
    """
    p = M6.poza_de_enrocado_hec14(
        V=_V(3.32), Q_celda=3.82, seccion=SeccionCircular(1.83), TW=0.61,
        y_salida=0.823, d50_piedra=0.15, origen_piedra="ejemplo",
        V_admisible=2.1)
    assert p.y_equivalente == pytest.approx(0.76, rel=REL_EJEMPLO_POZA)
    assert p.Fr == pytest.approx(1.22, rel=REL_EJEMPLO_POZA)
    assert p.Co == pytest.approx(1.61, rel=REL_EJEMPLO_POZA)
    assert p.hs == pytest.approx(0.71, rel=REL_EJEMPLO_POZA)
    assert p.longitud_poza == pytest.approx(7.1, rel=REL_EJEMPLO_POZA)
    assert p.longitud_total == pytest.approx(10.7, rel=REL_EJEMPLO_POZA)
    assert p.ancho_final == pytest.approx(9.0, rel=REL_EJEMPLO_POZA)
    assert p.yc_salida == pytest.approx(0.26, rel=REL_EJEMPLO_POZA)
    assert p.V_salida_poza < 2.1 and not p.extendida
    assert p.Wo == pytest.approx(1.83, rel=REL_FORMULA)
    assert p.proteccion_adicional is False


def test_ejemplo_si_del_tubo_con_la_piedra_mayor_dimensiona_con_la_menor():
    """
    Mismo ejemplo, «Step 2 (2nd iteration)»: D50 = 0.25 m da hs/D50 = 0.96 <
    2; «try a riprap size that will yield hS/D50 close to, but greater than
    2. (A basin sized for smaller riprap may be lined with larger riprap.)»
    El ejemplo prueba 0.205 m: hs = 0.41 m, hs/D50 = 2.0; LS = 3·Wo = 5.5 m
    (10·hs = 4.1 m); LB = 4·Wo = 7.3 m (15·hs = 6.2 m); WB = 6.7 m; yc =
    0.31 m, Ac = 2.28 m2, Vc = 1.7 m/s. «since the trial D50 is not
    available, the next larger riprap size (D50 = 0.25 m) would be used to
    line a basin with the given dimensions». El programa resuelve el D50 de
    hs/D50 = 2 EXACTO (0.204 m) y reviste con la piedra que se le da.
    """
    p = M6.poza_de_enrocado_hec14(
        V=_V(3.32), Q_celda=3.82, seccion=SeccionCircular(1.83), TW=0.61,
        y_salida=0.823, d50_piedra=0.25, origen_piedra="ejemplo",
        V_admisible=2.1)
    assert p.dimensionada_con_menor
    assert p.D50_dimensionamiento == pytest.approx(0.205, rel=REL_EJEMPLO_POZA)
    assert p.hs == pytest.approx(2 * p.D50_dimensionamiento, rel=REL_ARITMETICA)
    assert p.hs == pytest.approx(0.41, rel=REL_EJEMPLO_POZA)
    assert p.longitud_poza == pytest.approx(3 * 1.83, rel=REL_FORMULA)
    assert p.longitud_total == pytest.approx(4 * 1.83, rel=REL_FORMULA)
    assert p.longitud_apron == pytest.approx(1.83, rel=REL_FORMULA)
    assert p.ancho_final == pytest.approx(6.7, rel=REL_EJEMPLO_POZA)
    assert p.yc_salida == pytest.approx(0.31, rel=REL_EJEMPLO_POZA)
    assert p.V_salida_poza == pytest.approx(1.7, rel=REL_EJEMPLO_POZA)
    # Revestida con la piedra de 0.25 m: el espesor es el de ESA piedra.
    assert p.D50_piedra == pytest.approx(0.25, rel=REL_FORMULA)
    assert p.espesor == pytest.approx(0.50, rel=REL_FORMULA)


def test_ejemplo_cu_del_tubo_en_unidades_inglesas():
    """
    «Design Example: Riprap Basin (Culvert on a Mild Slope) (CU)», pags.
    impresas 10-14 a 10-16 (PDF 215 a 217): CMP de 6 ft, Q = 135 ft3/s, A =
    12.35 ft2, Vo = 10.9 ft/s, yo = 2.7 ft, ye = 2.48 ft, Fr = 1.22, TW = 2.0
    ft, Co = 1.62. D50 = 0.5 ft: hs = 2.3 ft, LS = 23 ft, LB = 34.5 ft, WB =
    29 ft, yc = 0.86 ft, Ac = 26.4 ft2, Vc = 5.1 ft/s.
    """
    ft = M_POR_FT
    p = M6.poza_de_enrocado_hec14(
        V=_V(10.9 * ft), Q_celda=135 * ft ** 3, seccion=SeccionCircular(6 * ft),
        TW=2.0 * ft, y_salida=2.7 * ft, d50_piedra=0.5 * ft,
        origen_piedra="ejemplo", V_admisible=7.0 * ft)
    assert p.y_equivalente / ft == pytest.approx(2.48, rel=REL_EJEMPLO_POZA)
    assert p.Co == pytest.approx(1.62, rel=REL_EJEMPLO_POZA)
    assert p.hs / ft == pytest.approx(2.3, rel=REL_EJEMPLO_POZA)
    assert p.longitud_total / ft == pytest.approx(34.5, rel=REL_EJEMPLO_POZA)
    assert p.ancho_final / ft == pytest.approx(29.0, rel=REL_EJEMPLO_POZA)
    assert p.V_salida_poza / ft == pytest.approx(5.1, rel=REL_EJEMPLO_POZA)


def test_ejemplo_cu_del_marco_extiende_la_poza_hasta_la_admisible():
    """
    «Design Example: Riprap Basin (Culvert on a Steep Slope) (CU)», pags.
    impresas 10-8 a 10-10 (PDF 209 a 211): marco de 8 x 6 ft, Q = 800 ft3/s,
    yo = 4 ft, Vo = 25 ft/s, TW = 2.8 ft, Vallow = 7 ft/s. Con D50 = 2.5 ft
    hs/D50 = 1.7 < 2: el ejemplo dimensiona con 2.3 ft (hs = 4.6 ft, LB = 69
    ft, WB = 54 ft) y en el paso 4 «VB = Vc = 7.5 ft/s (not acceptable). If
    the apron were extended (with a continued flare) such that the total
    basin length was 90 ft, the velocity would be reduced to the allowable
    level». El programa extiende el abocinado hasta Vc = Vallow y llega a la
    longitud total de la fuente (91 ft sin los redondeos del ejemplo).
    """
    ft = M_POR_FT
    p = M6.poza_de_enrocado_hec14(
        V=_V(25 * ft), Q_celda=800 * ft ** 3,
        seccion=SeccionRectangular(B=8 * ft, H=6 * ft), TW=2.8 * ft,
        y_salida=4 * ft, d50_piedra=2.5 * ft, origen_piedra="ejemplo",
        V_admisible=7.0 * ft)
    assert p.dimensionada_con_menor
    assert p.D50_dimensionamiento / ft == pytest.approx(2.3, rel=REL_EJEMPLO_POZA)
    assert p.hs / ft == pytest.approx(4.6, rel=REL_EJEMPLO_POZA)
    assert p.longitud_sin_extender / ft == pytest.approx(69, rel=REL_EJEMPLO_POZA)
    assert p.extendida
    assert p.longitud_total / ft == pytest.approx(90, rel=REL_EJEMPLO_POZA)
    assert p.V_salida_poza == pytest.approx(7.0 * ft, rel=REL_ARITMETICA)
    # El ancho final sigue el abocinado: WB = Wo + (2/3)·LB.
    assert p.ancho_final == pytest.approx(8 * ft + 2 / 3 * p.longitud_total,
                                          rel=REL_FORMULA)
    assert any("extiende" in a for a in p.avisos)


def test_paso_5_el_tw_alto_pide_proteccion_aguas_abajo_que_no_se_dimensiona():
    """
    Paso 5 (pag. 10-5): «With high tailwater (TW/yo ≥ 0.75), estimate
    centerline velocity at a series of downstream cross sections using
    Figure 10.3». El ejemplo del marco CU con TW = 4.2 ft: TW/yo = 1.05. La
    Figura 10.3 no esta digitalizada: se marca y se avisa, y Co = 2.4 (Ec.
    10.2, TW/ye > 1.0).
    """
    ft = M_POR_FT
    p = M6.poza_de_enrocado_hec14(
        V=_V(25 * ft), Q_celda=800 * ft ** 3,
        seccion=SeccionRectangular(B=8 * ft, H=6 * ft), TW=4.2 * ft,
        y_salida=4 * ft, d50_piedra=1.83 * ft, origen_piedra="ejemplo")
    assert p.Co == pytest.approx(2.4, rel=REL_FORMULA)
    assert p.proteccion_adicional is True
    assert any("Figura 10.3" in a for a in p.avisos)


# ===========================================================================
# 2 · La relacion de Co es un criterio [A]: envolvente o mejor ajuste
# ===========================================================================

def test_el_criterio_de_co_es_a_de_perfil_con_las_dos_relaciones():
    c = ca.CRITERIOS[CRITERIO_CO]
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert c.valor == "envolvente"
    assert tuple(c.sensibilidad) == ("envolvente", "mejor_ajuste")
    assert set(HEC14_POZA_CO) == set(c.sensibilidad)


@pytest.mark.parametrize("relacion, x, esperado", [
    # Ec. (10.2), envolvente: 1.4 | 4.0·x - 1.6 | 2.4
    ("envolvente", 0.5, 1.4), ("envolvente", 0.8, 4.0 * 0.8 - 1.6),
    ("envolvente", 1.2, 2.4),
    # Ec. (10.3), mejor ajuste: 2.0 | 4.0·x - 1.0 | 3.0
    ("mejor_ajuste", 0.5, 2.0), ("mejor_ajuste", 0.8, 4.0 * 0.8 - 1.0),
    ("mejor_ajuste", 1.2, 3.0),
])
def test_co_por_la_relacion_declarada(relacion, x, esperado):
    assert M6.parametro_co_poza(x, relacion) == pytest.approx(esperado,
                                                               rel=REL_FORMULA)


def test_las_dos_relaciones_son_continuas_en_sus_bordes():
    for relacion in HEC14_POZA_CO:
        for x in (0.75, 1.0):
            assert M6.parametro_co_poza(x - 1e-12, relacion) == pytest.approx(
                M6.parametro_co_poza(x + 1e-12, relacion), rel=REL_ARITMETICA)


def test_con_mejor_ajuste_la_poza_es_menos_profunda():
    """Co mayor resta mas: hs/ye baja 0.6 con TW/ye < 0.75 (2.0 contra 1.4)."""
    def poza():
        return M6.poza_de_enrocado_hec14(
            V=_V(7.63), Q_celda=22.7,
            seccion=SeccionRectangular(B=2.44, H=1.83), TW=0.85,
            y_salida=1.22, d50_piedra=0.55, origen_piedra="ejemplo")
    envolvente = poza()
    ajuste = _con_criterio(CRITERIO_CO, "mejor_ajuste", poza)
    assert ajuste.Co == pytest.approx(2.0, rel=REL_FORMULA)
    assert envolvente.hs - ajuste.hs == pytest.approx(
        0.6 * envolvente.y_equivalente, rel=REL_ARITMETICA)
    assert ajuste.relacion_co == "mejor_ajuste"


# ===========================================================================
# 3 · Los limites de la poza: los que la fuente pone y el que el proyecto no
#     extiende
# ===========================================================================

def test_la_poza_de_varios_barriles_no_se_evalua():
    """Ensayos de UN conducto (num. 10.1.1); la fuente no da el Wo de varios."""
    with pytest.raises(MetodoNoEvaluableError) as e:
        M6.poza_de_enrocado_hec14(
            V=_V(3.32), Q_celda=3.82, seccion=SeccionCircular(1.83), TW=0.61,
            y_salida=0.823, d50_piedra=0.15, origen_piedra="t",
            numero_celdas=2)
    assert e.value.rotulo == MOTIVO_METODO_NO_EVALUABLE_HEC14
    assert "barriles" in e.value.motivo


def test_la_poza_con_froude_de_3_o_mas_no_se_evalua():
    """Table 1.1, fila «Riprap basin»: Froude «< 3»."""
    # Marco de 1 m, Q = 2, V = 10 m/s: ye = 0.2 m, Fr = 10/(9.81·0.2)^0.5 = 7.1.
    with pytest.raises(MetodoNoEvaluableError) as e:
        M6.poza_de_enrocado_hec14(
            V=_V(10.0), Q_celda=2.0, seccion=SeccionRectangular(B=1.0, H=1.0),
            TW=0.1, y_salida=0.2, d50_piedra=0.3, origen_piedra="t")
    assert e.value.rotulo == MOTIVO_METODO_NO_EVALUABLE_HEC14
    assert f"{HEC14_POZA_FROUDE_MAX:g}" in e.value.motivo


def test_sin_piedra_admisible_en_el_rango_de_los_ensayos_no_se_evalua():
    """
    Con Fr bajo y TW alto la hoya de la Ec. (10.1) no llega a 2·D50 ni con
    la piedra MENOR del rango (D50/ye = 0.1): hs/ye = 0.86·0.1^-0.55·Fr - Co.
    Marco de 2 m, Q = 1, V = 1 m/s: ye = 0.5 m, Fr = 1/(9.81·0.5)^0.5 = 0.452;
    TW = 0.6 -> TW/ye = 1.2, Co = 2.4; hs/ye = 3.0499·0.452 - 2.4 = -1.02 < 0.2.
    La fuente descarto los ensayos de hs/D50 < 2 (pag. 10-3).
    """
    with pytest.raises(MetodoNoEvaluableError) as e:
        M6.poza_de_enrocado_hec14(
            V=_V(1.0), Q_celda=1.0, seccion=SeccionRectangular(B=2.0, H=1.0),
            TW=0.6, y_salida=0.5, d50_piedra=0.1, origen_piedra="t")
    assert "hs/D50" in e.value.motivo


def test_la_piedra_bajo_el_rango_de_los_ensayos_se_sube_a_0_1_ye():
    """
    «Check to see that ... D50/ye >= 0.1» (pag. 10-5): por debajo «did not
    exhibit relationships that appeared useful for design» (pag. 10-2). El
    ejemplo del marco SI con una piedra de 0.05 m (D50/ye = 0.04): la poza
    se reviste con 0.1·ye = 0.122 m y lo marca.
    """
    p = M6.poza_de_enrocado_hec14(
        V=_V(7.63), Q_celda=22.7, seccion=SeccionRectangular(B=2.44, H=1.83),
        TW=0.85, y_salida=1.22, d50_piedra=0.05, origen_piedra="t")
    assert p.piedra_subida
    assert p.D50_piedra == pytest.approx(
        HEC14_POZA_D50_SOBRE_YE_MIN * p.y_equivalente, rel=REL_FORMULA)
    assert p.D50_minimo == pytest.approx(p.D50_piedra, rel=REL_FORMULA)


def test_cada_paso_de_la_poza_cita_su_fuente():
    p = M6.poza_de_enrocado_hec14(
        V=_V(3.32), Q_celda=3.82, seccion=SeccionCircular(1.83), TW=0.61,
        y_salida=0.823, d50_piedra=0.25, origen_piedra="ejemplo",
        V_admisible=2.1)
    codigos = [x.codigo for x in p.pasos]
    assert codigos == ["6.5p", "6.6p"]
    reg = _registro.registro()
    for x in p.pasos:
        for cita_id in x.citas_textuales:
            reg.cita(cita_id)
    assert "HEC14.10.1#EC_10_1" in p.pasos[0].citas_textuales
    assert "HEC14.10.1#MAYOR_REVISTE" in p.pasos[0].citas_textuales
    assert p.pasos[1].veredicto.tipo is TipoDeVeredicto.CUMPLE


# ===========================================================================
# 4 · El apron sigue con sus limites, y dice donde esta la alternativa
# ===========================================================================

@pytest.mark.parametrize("seccion", [SeccionRectangular(B=1.5, H=1.0),
                                     SeccionCircular(1.83)])
def test_el_apron_sigue_sin_evaluarse_y_remite_a_la_poza(seccion):
    with pytest.raises(MetodoNoEvaluableError) as e:
        M6.apron_hec14(Q_celda=1.0, seccion=seccion, TW=0.5, y_salida=None,
                       y_critico=0.5)
    assert "10.1" in e.value.procedimiento
    assert "poza" in e.value.procedimiento
    assert "no implementa" not in e.value.procedimiento


# ===========================================================================
# 5 · La Fase 6: la poza entra donde el apron no llega, y en nada mas
# ===========================================================================

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_ANCHOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"


@pytest.fixture(scope="module")
def corrida_base(tmp_path_factory):
    """La corrida ancha de la linea base (la de tests/test_t8_correcciones)."""
    ruta = tmp_path_factory.mktemp("ve4g") / "externos.json"
    ruta.write_text(EXTERNOS_ANCHOS.read_text(encoding="utf-8"),
                    encoding="utf-8")
    return servicio.correr(
        CSV, servicio.cargar_datos_externos(ruta, {"luz_m": 2.75}), "perfil")


def _punto(informe, id_punto):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


def test_dentro_del_dominio_del_apron_nada_cambia(corrida_base):
    """A-01 y A-02 (tubos de 0.90 m, un barril, TW en rango): sin poza."""
    for id_punto in ("A-01", "A-02"):
        p = _punto(corrida_base, id_punto).proteccion
        assert p.apron is not None and p.poza is None
        assert not any("poza" in a.lower() for a in p.avisos)


def _resultado(corrida_base, **cambios):
    r = _punto(corrida_base, "A-01").resultado.resultado_hidraulico
    base = dict(control_gobernante=ControlGobernante.ENTRADA,
                V_salida_cota_inferior=False, numero_celdas=1)
    base.update(cambios)
    return replace(r, **base)


def _salida(resultado, seccion, **kw):
    return M6.proteccion_salida(V=resultado.V_salida, resultado=resultado,
                                seccion=seccion, **kw)


def test_un_tubo_de_mas_de_60_pulgadas_toma_la_poza_bajo_la_envolvente(
        corrida_base):
    """
    El ejemplo SI del tubo de 1.83 m llevado a la Fase 6. La piedra que el
    programa pone es la de Laushey con V = 3.32 m/s: d50 = 3.32^2/(3.1·9.8)
    = 0.3628 m. Con ella hs/D50 < 2: la poza se dimensiona con la menor
    (hs = 2·D50) y se reviste con la de Laushey. Rige la envolvente
    (archivo): espesor = max(1.75·d50, 2·d50) = 2·d50; longitud = max(5.0,
    LB). El apron no se evaluo y lo dice.
    """
    r = _resultado(corrida_base, Q=3.82, Q_celda_m3s=3.82, TW_m=0.61,
                   y_salida_m=0.823, y_critico=0.9,
                   V_salida=_V(3.32))
    p = _salida(r, SeccionCircular(1.83))
    assert p.apron is None and p.poza is not None
    d50 = 3.32 ** 2 / (3.1 * 9.8)
    assert p.d50_laushey == pytest.approx(d50, rel=REL_ARITMETICA)
    assert p.d50 == pytest.approx(d50, rel=REL_ARITMETICA)
    assert p.espesor == pytest.approx(2 * d50, rel=REL_ARITMETICA)
    assert p.longitud == pytest.approx(max(5.0, p.poza.longitud_total),
                                       rel=REL_FORMULA)
    assert p.rige_la_envolvente
    assert any("poza de enrocado" in a and "rige la envolvente" in a
               for a in p.avisos)
    assert any("Sec. 10.1" in x for x in p.advertencias)
    assert "6.6c" in [x.codigo for x in p.pasos]
    assert "6.5p" in [x.codigo for x in p.pasos]


def test_un_marco_de_una_celda_toma_la_poza(corrida_base):
    """Marco de 1.20 x 0.90 m, un barril: el caso de la linea base de la C."""
    r = _resultado(corrida_base, Q=1.0, Q_celda_m3s=1.0, TW_m=0.2,
                   y_salida_m=0.35, y_critico=0.44, V_salida=_V(2.4))
    p = _salida(r, SeccionRectangular(B=1.2, H=0.9))
    assert p.poza is not None and p.rige_la_envolvente
    assert p.espesor + 1e-12 >= 2 * p.d50
    assert p.longitud + 1e-12 >= p.poza.longitud_total


def test_varios_barriles_siguen_rigiendo_laushey_con_aviso(corrida_base):
    r = _resultado(corrida_base, Q=3.0, Q_celda_m3s=1.5, numero_celdas=2,
                   TW_m=0.3, y_salida_m=0.5, y_critico=0.6,
                   V_salida=_V(2.5))
    p = _salida(r, SeccionCircular(1.0))
    assert p.apron is None and p.poza is None and not p.rige_la_envolvente
    assert any("poza de enrocado" in a and "NO se evaluo" in a
               and "barriles" in a for a in p.avisos)


def test_con_la_regla_manual_la_poza_es_contraste_y_avisa(corrida_base):
    r = _resultado(corrida_base, Q=3.82, Q_celda_m3s=3.82, TW_m=0.61,
                   y_salida_m=0.823, y_critico=0.9, V_salida=_V(3.32))
    p = _con_criterio(CRITERIO_REGLA, "manual",
                      lambda: _salida(r, SeccionCircular(1.83)))
    d50 = 3.32 ** 2 / (3.1 * 9.8)
    assert p.poza is not None and not p.rige_la_envolvente
    assert p.espesor == pytest.approx(1.75 * d50, rel=REL_ARITMETICA)
    assert p.longitud == pytest.approx(5.0, rel=REL_FORMULA)
    assert any("poza" in a and "espesor" in a for a in p.avisos)


def test_la_admisible_del_terreno_entra_al_paso_4(corrida_base):
    """Con el terreno declarado, Vallow es la de la Tabla Nº 11."""
    r = _resultado(corrida_base, Q=3.82, Q_celda_m3s=3.82, TW_m=0.61,
                   y_salida_m=0.823, y_critico=0.9, V_salida=_V(3.32))
    terrenos = V_MAX_NO_REVESTIDOS
    clave = next(iter(terrenos))
    p = _salida(r, SeccionCircular(1.83), tipo_terreno=clave,
                regimen_flujo="permanente")
    assert p.poza.V_admisible == pytest.approx(
        terrenos[clave]["permanente"], rel=REL_FORMULA)
    assert not p.poza.V_salida_poza > p.poza.V_admisible + 1e-9
