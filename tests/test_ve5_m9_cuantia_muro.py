"""
tests/test_ve5_m9_cuantia_muro.py
=================================
VE-5, lote M9, item 29 del censo (ficha T7C-10): las cuantias minimas de
muros de E.060 14.3.1 pasan de constante [N] (`CUANTIA_MIN_MURO`) a criterio
[N→] ('cuantia_minima_muro_e060'): E.060 es norma de edificaciones, y la
excepcion de la §0.2 de la hoja de ruta que la hace regir en el cabezal
cubre la durabilidad, no los minimos estructurales (el mismo argumento que
movio el 0.30 m de 22.7.4 al cierre de T-7c). Escrito ANTES del codigo.
"""

import pytest

from src import constantes_normativas as cn
from src import criterios_adoptados as ca
from src.modulos import M9_cabezal as M9
from tests.apoyo.aproximacion import ABS_CERO

CLAVE = "cuantia_minima_muro_e060"


def test_la_constante_ya_no_esta_y_el_criterio_es_N_por_analogia():
    assert not hasattr(cn, "CUANTIA_MIN_MURO")
    c = ca.CRITERIOS[CLAVE]
    assert c.etiqueta == "N->" and c.nivel == ca.NIVEL_EXPEDIENTE
    assert c.valor == {"horizontal": pytest.approx(0.0020, abs=ABS_CERO),
                       "vertical": pytest.approx(0.0015, abs=ABS_CERO)}
    assert "E060.14.3.1" in c.fuente or "14.3.1" in c.fuente


@pytest.mark.parametrize("direccion, minima", [("horizontal", 0.0020),
                                               ("vertical", 0.0015)])
def test_la_cuantia_minima_se_lee_del_criterio(direccion, minima):
    assert M9.cuantia_minima(direccion=direccion) == pytest.approx(
        minima, abs=ABS_CERO)
    assert direccion in M9.DIRECCIONES_CUANTIA_MURO


def test_declarar_otra_cuantia_la_cambia():
    from tests.apoyo.criterios import con_valor
    with con_valor(CLAVE, {"horizontal": 0.0025, "vertical": 0.0015},
                   motivo="el minimo de 11.10.10.2, de prueba"):
        assert M9.cuantia_minima(direccion="horizontal") == pytest.approx(
            0.0025, abs=ABS_CERO)



@pytest.mark.parametrize("valor", [
    {"horizontal": 0.0019, "vertical": 0.0015},
    {"horizontal": 0.0020, "vertical": 0.0010},
])
def test_por_debajo_de_la_norma_se_rechaza(valor):
    """
    Dictamen Fable de VE-6: con etiqueta [N→] el criterio aplica la norma;
    un valor por debajo de 14.3.1 la bajaria, y se rechaza.
    """
    from src.modelos import DatoInvalidoError
    from tests.apoyo.criterios import con_valor
    with con_valor(CLAVE, valor, motivo="por debajo de 14.3.1, de prueba"):
        for direccion in M9.DIRECCIONES_CUANTIA_MURO:
            if valor[direccion] < cn.CUANTIA_MIN_MURO_E060_14_3_1[direccion]:
                with pytest.raises(DatoInvalidoError):
                    M9.cuantia_minima(direccion=direccion)


def test_la_ficha_dice_que_la_reemplazaria_y_cita_14_8():
    c = ca.CRITERIOS[CLAVE]
    assert "14.8.1" in c.fuente and "14.8.2" in c.fuente
    assert "5.10.6" in c.reemplazado_por and "14.8.2" in c.reemplazado_por
    assert c.valor == cn.CUANTIA_MIN_MURO_E060_14_3_1
