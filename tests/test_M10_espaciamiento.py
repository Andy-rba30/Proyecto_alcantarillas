"""
tests/test_M10_espaciamiento.py
=================================
Fase 10 (M10_espaciamiento.py): espaciamiento maximo entre alcantarillas de
alivio como el MINIMO entre el limite normativo ('long_max_cuneta', 200 m
adoptado por FEN) y la longitud por capacidad hidraulica de la cuneta, que
llega como argumento porque la hoja de ruta no da su formula.
"""

import pytest

import criterios_adoptados as ca
from modelos import CriterioPendienteError, DatoInvalidoError, GobiernaEspaciamiento
from modulos.M10_espaciamiento import espaciamiento_alivio


def test_gobierna_normativo_cuando_la_cuneta_alcanza_mas():
    resultado = espaciamiento_alivio(L_hidraulico=250.0)

    assert resultado.gobierna is GobiernaEspaciamiento.NORMATIVO
    assert resultado.espaciamiento_max == pytest.approx(200.0)
    assert resultado.L_normativo == pytest.approx(200.0)
    assert resultado.L_hidraulico == pytest.approx(250.0)


def test_gobierna_hidraulico_cuando_la_cuneta_agota_antes():
    resultado = espaciamiento_alivio(L_hidraulico=120.0)

    assert resultado.gobierna is GobiernaEspaciamiento.HIDRAULICO
    assert resultado.espaciamiento_max == pytest.approx(120.0)
    assert resultado.L_normativo == pytest.approx(200.0)


def test_el_empate_lo_gana_el_normativo():
    """
    L_hidraulico == L_normativo no es "hidraulico": la rama < es estricta,
    de modo que el empate declara la condicion normativa, que es la que
    tiene numeral citable en la memoria.
    """
    resultado = espaciamiento_alivio(L_hidraulico=200.0)

    assert resultado.gobierna is GobiernaEspaciamiento.NORMATIVO
    assert resultado.espaciamiento_max == pytest.approx(200.0)


@pytest.mark.parametrize("valor_invalido", [0.0, -50.0, float("nan"), float("inf")])
def test_L_hidraulico_no_fisico_es_dato_invalido(valor_invalido):
    with pytest.raises(DatoInvalidoError):
        espaciamiento_alivio(L_hidraulico=valor_invalido)


def test_el_limite_normativo_sale_de_criterios_adoptados_no_de_un_literal(monkeypatch):
    """
    El modulo no repite 200.0: si el criterio 'long_max_cuneta' cambiara
    manana (p.ej. a la sensibilidad declarada de 250 m), el resultado se
    mueve sin tocar M10_espaciamiento.py.
    """
    monkeypatch.setitem(
        ca.CRITERIOS, "long_max_cuneta",
        ca.Criterio(valor=250.0, etiqueta="A", concepto="prueba",
                    justificacion="prueba", fuente="prueba"),
    )

    resultado = espaciamiento_alivio(L_hidraulico=225.0)

    assert resultado.L_normativo == pytest.approx(250.0)
    assert resultado.gobierna is GobiernaEspaciamiento.HIDRAULICO


def test_criterio_pendiente_si_long_max_cuneta_se_deja_sin_valor(monkeypatch):
    monkeypatch.setitem(
        ca.CRITERIOS, "long_max_cuneta",
        ca.Criterio(valor=None, etiqueta="A", concepto="prueba",
                    justificacion="prueba", fuente="prueba"),
    )

    with pytest.raises(CriterioPendienteError):
        espaciamiento_alivio(L_hidraulico=150.0)
