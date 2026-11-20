"""
tests/test_ve7_lote_b_subareas.py
=================================
VE-7, lote B, item B10 (VE5-MH-01; decision del consultor Fable, triaje
VE-7, 2026-11-20): la columna OPCIONAL `subareas` del CSV de cuencas
(«C:area_ha;...»), con la suma de las areas igual al area de la cuenca, y el
paso del coeficiente que imprime cada subarea y C = ΣC·A/ΣA.

DATOS DE PRUEBA, NO DEL PROYECTO: las subareas de A-02 (210 ha) son
inventadas, 150 ha con C = 0.35 y 60 ha con C = 0.60. Dorados a mano:

    C = (0.35 x 150 + 0.60 x 60) / 210 = 88.5 / 210 = 0.42142857...

y, como Kirpich no lleva C en el tiempo de concentracion, la intensidad es
la misma con y sin subareas: Q_sub = Q_tabla x C_sub / C_tabla.
"""

import csv
from pathlib import Path

import pytest

from src import modelos
from src.modulos import MH_hidrologia as MH
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "hidrologia"
CUENCAS = FIXTURES / "cuencas_prueba.csv"
ESTACION = FIXTURES / "estacion_prueba.csv"
FEN = "homogeneidad_serie_fen"
C_A_MANO = 88.5 / 210


def _con_subareas(tmp_path, valor):
    lineas = [l for l in CUENCAS.read_text(encoding="utf-8").splitlines()
              if not l.startswith("#")]
    filas = list(csv.DictReader(lineas))
    for f in filas:
        f["subareas"] = valor if f["id"] == "A-02" else ""
    destino = tmp_path / "cuencas_subareas.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    return destino


def test_sin_la_columna_la_cuenca_es_la_de_hoy():
    cuencas = MH.cargar_cuencas(CUENCAS)
    assert all(c.subareas == () for c in cuencas.values())


def test_el_cargador_lee_las_subareas(tmp_path):
    cuencas = MH.cargar_cuencas(_con_subareas(tmp_path, "0.35:150;0.60:60"))
    (C1, A1), (C2, A2) = cuencas["A-02"].subareas
    assert (C1, A1, C2, A2) == pytest.approx((0.35, 150, 0.60, 60),
                                             rel=REL_TRANSPORTE)
    assert cuencas["A-01"].subareas == ()


def test_si_las_subareas_no_suman_el_area_es_un_dato_invalido(tmp_path):
    with pytest.raises(modelos.DatoInvalidoError) as exc:
        MH.cargar_cuencas(_con_subareas(tmp_path, "0.35:150;0.60:50"))
    assert exc.value.campo == "subareas"
    assert "contradice" in str(exc.value)


@pytest.mark.parametrize("valor", ["0.35-150", "1.2:150;0.6:60",
                                   "0.35:abc", "0:210"])
def test_la_forma_de_cada_subarea(tmp_path, valor):
    with pytest.raises(modelos.DatoInvalidoError) as exc:
        MH.cargar_cuencas(_con_subareas(tmp_path, valor))
    assert exc.value.campo == "subareas"


def test_el_paso_imprime_cada_subarea_y_el_ponderado(tmp_path):
    cuenca = MH.cargar_cuencas(_con_subareas(tmp_path,
                                             "0.35:150;0.60:60"))["A-02"]
    C, paso = MH._paso_c(cuenca, 35)
    assert C == pytest.approx(C_A_MANO, rel=REL_TRANSPORTE)
    simbolos = {m.simbolo: m.valor for m in paso.sustitucion}
    assert sorted(simbolos) == ["A_1", "A_2", "C_1", "C_2"]
    assert [simbolos[k] for k in ("C_1", "A_1", "C_2", "A_2")] == \
        pytest.approx([0.35, 150, 0.60, 60], rel=REL_TRANSPORTE)
    assert MH.coeficiente_ponderado(cuenca.subareas) == pytest.approx(
        C_A_MANO, rel=REL_TRANSPORTE)
    assert paso.resultado.valor == pytest.approx(C_A_MANO,
                                                 rel=REL_TRANSPORTE)
    assert paso.formula_cita_id == "MC_HHD.3.12.2"
    assert "Equation 2-4" in paso.nota_del_proyecto


def test_el_caudal_escala_con_el_coeficiente(tmp_path):
    serie = MH.cargar_estacion(ESTACION)["PRUEBA-SINTETICA"]
    base = MH.cargar_cuencas(CUENCAS)["A-02"]
    sub = MH.cargar_cuencas(_con_subareas(tmp_path,
                                          "0.35:150;0.60:60"))["A-02"]
    with declarados({FEN: "serie_completa"}):
        q_base = MH.caudal_de_diseno(base, serie, 35)
        q_sub = MH.caudal_de_diseno(sub, serie, 35)
    C_base, _ = MH._paso_c(base, 35)
    assert q_sub.tc_min == pytest.approx(q_base.tc_min, rel=REL_TRANSPORTE)
    assert q_sub.Q_m3s == pytest.approx(q_base.Q_m3s * C_A_MANO / C_base,
                                        rel=REL_TRANSPORTE)
