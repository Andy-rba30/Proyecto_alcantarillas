"""
tests/test_ve7_lote_b_subareas.py
=================================
VE-7, lote B, item B10 (VE5-MH-01) con el dictamen Fable (decision 1): la
columna OPCIONAL `subareas` del CSV de cuencas, «cobertura/suelo[/S]:area_ha»
o «cobertura:area_ha» en una superficie vial; el coeficiente NO se teclea:
cada C_k sale de su tabla (Tabla N 08 o la vial con su incremento por TR) y
C = ΣC·A/ΣA. Con `subareas`, `cobertura` y `suelo` de la fila van vacios.

DATOS DE PRUEBA, NO DEL PROYECTO: A-02 (210 ha, S_terreno 0.045) partida en
150 ha de cultivos semipermeables y 60 ha de pastos con vegetacion ligera
semipermeables sobre una pendiente propia de 0.005. Dorados a mano, leidos
de la Tabla N 08 transcrita (constantes_normativas, celdas por clave):

    C_1 = celda (cultivos, semipermeable) en la columna de S = 0.045
    C_2 = celda (pastos_vegetacion_ligera, semipermeable) en la de 0.005
    C   = (C_1·150 + C_2·60) / 210

y, como Kirpich no lleva C en el tiempo de concentracion, la intensidad es
la misma: Q_sub = Q_tabla x C_sub / C_tabla.
"""

import csv
from pathlib import Path

import pytest

from src import modelos
from src.constantes_normativas import TABLA_08_COEFICIENTE_DE_ESCORRENTIA as T08
from src.modulos import MH_hidrologia as MH
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "hidrologia"
CUENCAS = FIXTURES / "cuencas_prueba.csv"
ESTACION = FIXTURES / "estacion_prueba.csv"
FEN = "homogeneidad_serie_fen"
SUB = "cultivos/semipermeable:150;pastos_vegetacion_ligera/semipermeable/0.005:60"


def _columna(S):
    """La clase de pendiente de la Tabla N 08, escrita aqui (no por MH)."""
    if S > 0.50:
        return "pronunciada"
    if S > 0.20:
        return "alta"
    if S > 0.05:
        return "media"
    if S > 0.01:
        return "suave"
    return "despreciable"


C1 = T08[("cultivos", "semipermeable")][_columna(0.045)]
C2 = T08[("pastos_vegetacion_ligera", "semipermeable")][_columna(0.005)]
C_A_MANO = (C1 * 150 + C2 * 60) / 210


def _con_subareas(tmp_path, valor, *, vaciar=True):
    lineas = [l for l in CUENCAS.read_text(encoding="utf-8").splitlines()
              if not l.startswith("#")]
    filas = list(csv.DictReader(lineas))
    for f in filas:
        f["subareas"] = valor if f["id"] == "A-02" else ""
        if f["id"] == "A-02" and vaciar:
            f["cobertura"] = f["suelo"] = ""
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
    a02 = MH.cargar_cuencas(_con_subareas(tmp_path, SUB))["A-02"]
    (c1, s1, S1, A1), (c2, s2, S2, A2) = a02.subareas
    assert (c1, s1, S1) == ("cultivos", "semipermeable", None)
    assert (c2, s2) == ("pastos_vegetacion_ligera", "semipermeable")
    assert (S2, A1, A2) == pytest.approx((0.005, 150, 60), rel=REL_TRANSPORTE)
    assert a02.cobertura == "" and a02.suelo == ""


def test_si_las_subareas_no_suman_el_area_es_un_dato_invalido(tmp_path):
    with pytest.raises(modelos.DatoInvalidoError) as exc:
        MH.cargar_cuencas(_con_subareas(
            tmp_path, "cultivos/semipermeable:150;pavimento:50"))
    assert exc.value.campo == "subareas"
    assert "contradice" in str(exc.value)


@pytest.mark.parametrize("valor", [
    "0.6:1.2",                                   # un C tecleado
    "0.35:150;0.60:60",
    "cultivos:210",                              # sin suelo
    "cultivos/arcilla:210",                      # suelo que la tabla no tiene
    "pavimento/semipermeable:210",               # vial con suelo
    "cultivos/semipermeable-210",                # sin «:»
])
def test_la_forma_de_cada_subarea(tmp_path, valor):
    with pytest.raises(modelos.DatoInvalidoError) as exc:
        MH.cargar_cuencas(_con_subareas(tmp_path, valor))
    assert exc.value.campo == "subareas"


def test_con_subareas_la_cobertura_de_la_fila_va_vacia(tmp_path):
    with pytest.raises(modelos.DatoInvalidoError) as exc:
        MH.cargar_cuencas(_con_subareas(tmp_path, SUB, vaciar=False))
    assert exc.value.campo == "cobertura"
    assert "contradice" in str(exc.value)


def test_cada_C_es_la_celda_de_la_tabla_08(tmp_path):
    cuenca = MH.cargar_cuencas(_con_subareas(tmp_path, SUB))["A-02"]
    C, paso = MH._paso_c(cuenca, 35)
    sust = {m.simbolo: m.valor for m in paso.sustitucion}
    assert sust["C_1"] == pytest.approx(C1, rel=REL_TRANSPORTE)
    assert sust["C_2"] == pytest.approx(C2, rel=REL_TRANSPORTE)
    assert sust["S_1"] == pytest.approx(cuenca.S_terreno, rel=REL_TRANSPORTE)
    assert (sust["columna_1"], sust["columna_2"]) == (_columna(0.045),
                                                      _columna(0.005))
    assert C == pytest.approx(C_A_MANO, rel=REL_TRANSPORTE)
    assert MH.coeficiente_ponderado([(C1, 150), (C2, 60)]) == pytest.approx(
        C_A_MANO, rel=REL_TRANSPORTE)
    assert "MC_HHD.3.12.2#T08" in paso.citas_textuales
    assert "Equation 2-4" not in paso.nota_del_proyecto


def test_la_subarea_vial_lleva_el_incremento_por_TR(tmp_path):
    """Con TR = 50 el C del pavimento es el de la tabla vial aumentado: el
    mismo numero que `coeficiente_de_superficie_vial` (la funcion de la
    cuenca vial entera), y mayor que su C de 10 años."""
    cuenca = MH.cargar_cuencas(_con_subareas(
        tmp_path, "cultivos/semipermeable:150;pavimento:60"))["A-02"]
    C, paso = MH._paso_c(cuenca, 50)
    sust = {m.simbolo: m.valor for m in paso.sustitucion}
    C_vial, c10, *_ = MH.coeficiente_de_superficie_vial(
        superficie="pavimento", TR=50)
    assert C_vial > c10
    assert sust["C_2"] == pytest.approx(C_vial, rel=REL_TRANSPORTE)
    assert sust["C10_2"] == pytest.approx(c10, rel=REL_TRANSPORTE)
    assert C == pytest.approx((C1 * 150 + C_vial * 60) / 210,
                              rel=REL_TRANSPORTE)
    assert {"WSDOT_HM.2-6.2#T2-2", "WSDOT_HM.2-6.2#FRECUENCIA"} <= set(
        paso.citas_textuales)


def test_el_caudal_escala_con_el_coeficiente(tmp_path):
    serie = MH.cargar_estacion(ESTACION)["PRUEBA-SINTETICA"]
    base = MH.cargar_cuencas(CUENCAS)["A-02"]
    sub = MH.cargar_cuencas(_con_subareas(tmp_path, SUB))["A-02"]
    with declarados({FEN: "serie_completa"}):
        q_base = MH.caudal_de_diseno(base, serie, 35)
        q_sub = MH.caudal_de_diseno(sub, serie, 35)
    C_base, _ = MH._paso_c(base, 35)
    assert q_sub.tc_min == pytest.approx(q_base.tc_min, rel=REL_TRANSPORTE)
    assert q_sub.Q_m3s == pytest.approx(q_base.Q_m3s * C_A_MANO / C_base,
                                        rel=REL_TRANSPORTE)
