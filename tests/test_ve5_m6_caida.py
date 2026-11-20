"""
tests/test_ve5_m6_caida.py
==========================
VE-5 (lote m6): la ESTRUCTURA DE CAIDA RECTA de HEC-14 Cap. 11 (num.
11.1.3), por decision del dueño dentro del alcance, donde la salida queda
colgada sobre el lecho y la Fase 6 no la puede cerrar con la hoya del Cap.
5: cuando gobierna la pendiente maxima del conducto (el desnivel del cauce
queda en la salida, ficha T6-02) o cuando la caida supera la ultima fila de
la Tabla 5.2 (4 alturas del conducto).

DE DONDE SALE CADA ORACULO, porque ninguno es la salida del codigo: los dos
ejemplos resueltos «Straight Drop Structure» de HEC-14 (pags. impresas 11-9
a 11-11, PDF 230 a 233), en SI y en unidades inglesas, y las Ec. (11.5) a
(11.16) leidas por imagen (pags. 11-6 a 11-8).
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from src import servicio
from src.constantes_normativas import (
    HEC14_CAIDA_HO_MAX_M, HEC14_CAIDA_HO_SOBRE_YC_MAX)
from src.modelos import (
    ControlGobernante, MOTIVO_METODO_NO_EVALUABLE_HEC14,
    MetodoNoEvaluableError, SeccionCircular, SeccionRectangular)
from src.modulos import M6_proteccion as M6
from src.normativa import registro as _registro

# Los ejemplos resueltos imprimen tres cifras y arrastran el redondeo de yc
# (0.812 m): 1 % cubre ese arrastre y no mas.
REL_EJEMPLO = 1e-2
REL_FORMULA = 1e-9
M_POR_FT = 0.3048            # exacto por definicion


# ===========================================================================
# 1 · La estructura contra los ejemplos resueltos (num. 11.1.3)
# ===========================================================================

def test_ejemplo_si_de_la_caida_recta():
    """
    «Design Example: Straight Drop Structure (SI)», pags. 11-9 y 11-10: Q =
    7.1 m3/s, Wo = 3.10 m, h = 1.83 m, yo = 1.025 m. q = 2.29; yc = 0.812;
    y3 = 2.15·yc = 1.745; h2 = -(1.83 - 1.025) = -0.805; ho = h2 - y3 =
    -2.55; el piso baja 0.72 m. Lf = 3.01, Lt = 1.90, Ls = 3.30, L1 = 3.15,
    L2 = 0.65, L3 = 1.43, LB = 5.23. Bloques de 0.65 m de alto y 0.325 de
    ancho y separacion; umbral 0.325; muro 0.69 sobre el TW; aproximacion
    revestida 2.44 m.
    """
    c = M6.caida_recta_hec14(Q=7.1, ancho_vertedero=3.10, desnivel_h=1.83,
                             tirante_aguas_abajo=1.025)
    assert c.q == pytest.approx(2.29, rel=REL_EJEMPLO)
    assert c.yc == pytest.approx(0.812, rel=REL_EJEMPLO)
    assert c.y3 == pytest.approx(1.745, rel=REL_EJEMPLO)
    assert c.h2 == pytest.approx(-0.805, rel=REL_EJEMPLO)
    assert c.ho == pytest.approx(-2.55, rel=REL_EJEMPLO)
    assert c.depresion_piso == pytest.approx(0.72, rel=REL_EJEMPLO)
    assert c.Lf == pytest.approx(3.01, rel=REL_EJEMPLO)
    assert c.Lt == pytest.approx(1.90, rel=REL_EJEMPLO)
    assert c.Ls == pytest.approx(3.30, rel=REL_EJEMPLO)
    assert c.L1 == pytest.approx(3.15, rel=REL_EJEMPLO)
    assert c.L2 == pytest.approx(0.65, rel=REL_EJEMPLO)
    assert c.L3 == pytest.approx(1.43, rel=REL_EJEMPLO)
    assert c.longitud == pytest.approx(5.23, rel=REL_EJEMPLO)
    assert c.altura_bloques == pytest.approx(0.65, rel=REL_EJEMPLO)
    assert c.ancho_bloques == pytest.approx(0.325, rel=REL_EJEMPLO)
    assert c.altura_umbral == pytest.approx(0.325, rel=REL_EJEMPLO)
    assert c.muro_sobre_tw == pytest.approx(0.69, rel=REL_EJEMPLO)
    assert c.longitud_aproximacion == pytest.approx(2.44, rel=REL_EJEMPLO)


def test_ejemplo_cu_de_la_caida_recta():
    """
    El mismo en unidades inglesas, pags. 11-10 y 11-11: Q = 250 ft3/s, Wo =
    10 ft, h = 6.0 ft, yo = 3.36 ft. yc = 2.69 ft; ho = -8.41 ft; el piso
    baja 2.4 ft; Lf = 9.94, Lt = 6.26, Ls = 10.89, L1 = 10.4, LB = 17.3 ft.
    """
    ft = M_POR_FT
    c = M6.caida_recta_hec14(Q=250 * ft ** 3, ancho_vertedero=10 * ft,
                             desnivel_h=6.0 * ft, tirante_aguas_abajo=3.36 * ft)
    assert c.yc / ft == pytest.approx(2.69, rel=REL_EJEMPLO)
    assert c.ho / ft == pytest.approx(-8.41, rel=REL_EJEMPLO)
    assert c.depresion_piso / ft == pytest.approx(2.4, rel=2 * REL_EJEMPLO)
    assert c.Lf / ft == pytest.approx(9.94, rel=REL_EJEMPLO)
    assert c.Lt / ft == pytest.approx(6.26, rel=REL_EJEMPLO)
    assert c.Ls / ft == pytest.approx(10.89, rel=REL_EJEMPLO)
    assert c.L1 / ft == pytest.approx(10.4, rel=REL_EJEMPLO)
    assert c.longitud / ft == pytest.approx(17.3, rel=REL_EJEMPLO)


def test_las_formulas_de_longitud_recomputadas_a_mano():
    """Ec. (11.12) a (11.14) con los numeros del ejemplo SI, sin redondear."""
    c = M6.caida_recta_hec14(Q=7.1, ancho_vertedero=3.10, desnivel_h=1.83,
                             tirante_aguas_abajo=1.025)
    yc, ho, h2 = c.yc, c.ho, c.h2
    Lf = (-0.406 + (3.195 - 4.368 * ho / yc) ** 0.5) * yc
    Lt = (-0.406 + (3.195 - 4.368 * h2 / yc) ** 0.5) * yc
    Ls = ((0.691 + 0.228 * (Lt / yc) ** 2 - ho / yc) * yc
          / (0.185 + 0.456 * Lt / yc))
    assert c.Lf == pytest.approx(Lf, rel=REL_FORMULA)
    assert c.Lt == pytest.approx(Lt, rel=REL_FORMULA)
    assert c.Ls == pytest.approx(Ls, rel=REL_FORMULA)
    assert c.L1 == pytest.approx((Lf + Ls) / 2, rel=REL_FORMULA)


def test_cada_paso_de_la_caida_cita_su_fuente():
    c = M6.caida_recta_hec14(Q=7.1, ancho_vertedero=3.10, desnivel_h=1.83,
                             tirante_aguas_abajo=1.025)
    reg = _registro.construir()
    assert [x.codigo for x in c.pasos] == ["6.15", "6.16"]
    for x in c.pasos:
        for cita_id in x.citas_textuales:
            reg.cita(cita_id)
    assert "HEC14.11.1.3#LIMITES" in c.pasos[0].citas_textuales
    assert "HEC14.11.1.3#BLOQUES" in c.pasos[1].citas_textuales


# ===========================================================================
# 2 · Los limites de la fuente (num. 11.1.3 y Tabla 1.1)
# ===========================================================================

def test_la_caida_de_mas_de_15_pies_no_se_evalua():
    """«Total drop, ho, less than 4.6 m (15 ft)»: rige 15 ft = 4.572 m."""
    with pytest.raises(MetodoNoEvaluableError) as e:
        M6.caida_recta_hec14(Q=7.1, ancho_vertedero=3.10, desnivel_h=4.0,
                             tirante_aguas_abajo=0.5)
    assert e.value.rotulo == MOTIVO_METODO_NO_EVALUABLE_HEC14
    assert HEC14_CAIDA_HO_MAX_M == pytest.approx(15 * M_POR_FT, rel=REL_FORMULA)
    assert "4.572" in e.value.motivo


def test_la_caida_relativa_fuera_de_1_a_15_no_se_evalua():
    """«Relative drop, ho/yc, between 1.0 and 15»: q chico, caida grande."""
    with pytest.raises(MetodoNoEvaluableError) as e:
        M6.caida_recta_hec14(Q=0.05, ancho_vertedero=3.0, desnivel_h=2.5,
                             tirante_aguas_abajo=0.1)
    assert f"{HEC14_CAIDA_HO_SOBRE_YC_MAX:g}" in e.value.motivo


def test_el_vertedero_angosto_no_se_evalua():
    """«Crest length, Wo, greater than 1.5yc»."""
    with pytest.raises(MetodoNoEvaluableError) as e:
        M6.caida_recta_hec14(Q=7.1, ancho_vertedero=0.6, desnivel_h=1.83,
                             tirante_aguas_abajo=1.025)
    assert "1.5" in e.value.motivo


def test_la_aproximacion_supercritica_no_se_evalua():
    """Paso 2: verificar el flujo subcritico; si no, la fuente no da diseño."""
    with pytest.raises(MetodoNoEvaluableError) as e:
        M6.caida_recta_hec14(Q=7.1, ancho_vertedero=3.10, desnivel_h=1.83,
                             tirante_aguas_abajo=1.025,
                             aproximacion_supercritica=True)
    assert "subcritic" in e.value.motivo


def test_el_receptor_sobre_la_cresta_no_se_evalua():
    """h2 = -(h - yo) >= 0: el TW no queda bajo la cresta y no hay lamina aireada."""
    with pytest.raises(MetodoNoEvaluableError) as e:
        M6.caida_recta_hec14(Q=7.1, ancho_vertedero=3.10, desnivel_h=0.8,
                             tirante_aguas_abajo=1.0)
    assert "aireada" in e.value.motivo


# ===========================================================================
# 3 · La Fase 6: entra donde la salida queda colgada, y en nada mas
# ===========================================================================

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_ANCHOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"


@pytest.fixture(scope="module")
def corrida_base(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("ve5m6") / "externos.json"
    ruta.write_text(EXTERNOS_ANCHOS.read_text(encoding="utf-8"),
                    encoding="utf-8")
    return servicio.correr(
        CSV, servicio.cargar_datos_externos(ruta, {"luz_m": 2.75}), "perfil")


def _resultado(corrida_base, **cambios):
    p = next(x for x in corrida_base.puntos if x.punto.id == "A-01")
    r = p.resultado.resultado_hidraulico
    base = dict(control_gobernante=ControlGobernante.SALIDA, numero_celdas=1)
    base.update(cambios)
    return replace(r, **base), p.resultado.seccion


def test_sin_caida_que_cerrar_la_fase_no_cambia(corrida_base):
    """A-01 y A-02 (caida menor que 4 alturas, pendiente del cauce): sin caida."""
    for id_punto in ("A-01", "A-02"):
        s = next(x for x in corrida_base.puntos if x.punto.id == id_punto)
        if s.socavacion is not None:
            assert s.socavacion.caida is None
            assert not any("caida recta" in a for a in s.socavacion.avisos)


def test_la_caida_por_pendiente_maxima_se_dimensiona(corrida_base):
    """
    El conducto mas tendido que su cauce deja el desnivel en la salida
    (ficha T6-02). Un marco de 3.10 m con el caudal del ejemplo SI, el TW
    del ejemplo y 1.83 m de caida: la Fase 6 da la estructura del ejemplo.
    """
    r, _ = _resultado(corrida_base, Q=7.1, Q_celda_m3s=7.1, TW_m=1.025,
                      y_normal=1.3, y_critico=0.81)
    s = M6.socavacion_salida(
        resultado=r, seccion=SeccionRectangular(B=3.10, H=1.5),
        altura_caida_m=1.83, pendiente_maxima_gobierna=True)
    assert s.caida is not None
    assert s.caida.longitud == pytest.approx(5.23, rel=REL_EJEMPLO)
    assert "6.15" in [x.codigo for x in s.pasos]
    assert any("caida recta" in a and "pendiente maxima" in a
               for a in s.avisos)


def test_la_caida_mas_alla_de_la_tabla_5_2_se_dimensiona(corrida_base):
    """
    Un tubo de 0.45 m con 1.83 m de caida: Hd = 4.07 > 4 (Tabla 5.2). Con Q =
    0.2 m3/s y el vertedero del ancho del tubo: q = 0.444, yc = 0.272 m,
    1.5·yc = 0.41 m < 0.45 m.
    """
    r, _ = _resultado(corrida_base, Q=0.2, Q_celda_m3s=0.2, TW_m=0.30,
                      y_normal=0.35, y_critico=0.30)
    s = M6.socavacion_salida(resultado=r, seccion=SeccionCircular(0.45),
                             altura_caida_m=1.83)
    assert s.caida is not None
    assert any("caida recta" in a and "Tabla 5.2" in a for a in s.avisos)


def test_la_caida_con_el_barril_supercritico_avisa_y_no_dimensiona(
        corrida_base):
    r, _ = _resultado(corrida_base, Q=7.1, Q_celda_m3s=7.1, TW_m=1.025,
                      y_normal=0.5, y_critico=0.81,
                      control_gobernante=ControlGobernante.ENTRADA)
    s = M6.socavacion_salida(
        resultado=r, seccion=SeccionRectangular(B=3.10, H=1.5),
        altura_caida_m=1.83, pendiente_maxima_gobierna=True)
    assert s.caida is None
    assert any("caida recta" in a and "NO se evaluo" in a
               and "subcritic" in a for a in s.avisos)
