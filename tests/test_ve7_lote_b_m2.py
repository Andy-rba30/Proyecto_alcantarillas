"""
tests/test_ve7_lote_b_m2.py
===========================
VE-7, lote B, items B9 y B12 (decision del consultor Fable, triaje VE-7,
2026-11-20). Los dos tocan `M2_material`:

  * B9 (VE2-G (2)): con la opcion inglesa del concreto, el diametro de
    calculo 1.0668 m (42 in) es el MISMO tubo que el designado de 1050 mm
    (AASHTO M 170M num. 12.1 y Table 6). La pared se lee de la fila del
    designado cuando el criterio no trae la fila del diametro ingles.
    Oraculo independiente: la fila de 1050 mm de la columna «Wall B» que el
    archivo declara, leida del criterio y no de M2.
  * B12 (T11-03 (6)): el arranque de la progresion se valida en M2, con
    `campo="diametros_normalizados"`. Antes, un inicio negativo lo rechazaba
    la seccion sobre el dato `D`, que el usuario no escribio.
"""

import pytest

from src import criterios_adoptados as ca
from src.modelos import DatoFaltanteError, DatoInvalidoError, TipoMaterial
from src.modulos import M2_material as M2
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados


def _concreto():
    return M2.catalogo(TipoMaterial.CONCRETO_REFORZADO)


# ===========================================================================
# B9
# ===========================================================================

def test_el_diametro_ingles_toma_la_pared_del_designado():
    fila_1050 = ca.valor("espesor_pared_conducto")["concreto_reforzado"][1050]
    assert 1067 not in ca.valor("espesor_pared_conducto")["concreto_reforzado"]
    assert M2.espesor_pared(_concreto(), 1.0668) == pytest.approx(fila_1050, rel=REL_TRANSPORTE)
    # el ingles tal como lo imprime la Table 6, redondeado al mm
    assert M2.espesor_pared(_concreto(), 1.067) == pytest.approx(fila_1050, rel=REL_TRANSPORTE)


def test_si_el_criterio_trae_la_fila_del_ingles_gana_esa():
    pared = dict(ca.valor("espesor_pared_conducto"))
    pared["concreto_reforzado"] = {**pared["concreto_reforzado"],
                                   1067: 0.1143}
    with declarados({"espesor_pared_conducto": pared}):
        assert M2.espesor_pared(_concreto(), 1.0668) == pytest.approx(0.1143, rel=REL_TRANSPORTE)


def test_un_diametro_sin_fila_ni_designado_sigue_faltando():
    # 0.95 m no es designado ni ingles convertido de ningun designado
    with pytest.raises(DatoFaltanteError):
        M2.espesor_pared(_concreto(), 0.95)


def test_el_designado_se_lee_sin_cambios():
    fila_900 = ca.valor("espesor_pared_conducto")["concreto_reforzado"][900]
    assert M2.espesor_pared(_concreto(), 0.90) == pytest.approx(fila_900, rel=REL_TRANSPORTE)


# ===========================================================================
# B12
# ===========================================================================

def test_el_arranque_negativo_se_rechaza_sobre_el_criterio():
    with declarados({"diametros_normalizados": {"inicio": -0.90,
                                                "paso": 0.15}}):
        with pytest.raises(DatoInvalidoError) as exc:
            M2.siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO)
    assert exc.value.campo == "diametros_normalizados"
    assert "arranque" in str(exc.value)


def test_el_arranque_cero_tambien():
    with declarados({"diametros_normalizados": {"inicio": 0.0,
                                                "paso": 0.15}}):
        with pytest.raises(DatoInvalidoError) as exc:
            M2.siguiente_diametro(TipoMaterial.TMC)
    assert exc.value.campo == "diametros_normalizados"


def test_el_arranque_de_archivo_no_cambia():
    assert M2.siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO) == \
        pytest.approx(0.90, rel=REL_TRANSPORTE)
