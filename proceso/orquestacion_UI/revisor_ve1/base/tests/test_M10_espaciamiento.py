"""
tests/test_M10_espaciamiento.py
=================================
Fase 10 (M10_espaciamiento.py): espaciamiento maximo entre alcantarillas de
alivio como el MINIMO entre el limite normativo ('long_max_cuneta', 200 m
adoptado por FEN) y la longitud por capacidad hidraulica de la cuneta.

Desde las correcciones de la auditoria de T-9 (H8) el modulo se contrasta
contra su caso patron, `CP_T9_CUNETA` de `tests/fixtures/casos_patron.py`
--la capacidad de la cuneta, VB2 y la longitud por capacidad, calculadas a
mano--, y sale de la exencion `SIN_CASO_PATRON` de
`tests/test_guardias_de_la_suite.py`: la exencion decia que faltaban la
seccion de la cuneta, su n y la longitud por capacidad, y T-9 los trajo.
"""

import pytest

from src import criterios_adoptados as ca
from src.modelos import CriterioPendienteError, DatoInvalidoError, GobiernaEspaciamiento
from src.modulos import M10_espaciamiento as M10
from src.modulos.M10_espaciamiento import espaciamiento_alivio
from tests.fixtures.casos_patron import CP_T9_CUNETA

REL_CASO_PATRON = 1e-4       # los dorados llevan cinco o seis cifras


def test_la_capacidad_de_la_seccion_de_archivo_es_la_del_caso_patron():
    cp = CP_T9_CUNETA["archivo"]
    c = M10.capacidad_cuneta(S_cuneta=cp["S"])
    assert c.area_llena_m2 == pytest.approx(cp["A"], rel=REL_CASO_PATRON)
    assert c.radio_llena_m == pytest.approx(cp["Rh"], rel=REL_CASO_PATRON)
    assert c.Q_admisible_m3s == pytest.approx(cp["Q_adm"], rel=REL_CASO_PATRON)


def test_el_caso_del_auditor_es_el_del_caso_patron(monkeypatch):
    cp = CP_T9_CUNETA["auditor"]
    original = ca.valor
    monkeypatch.setattr(ca, "valor", lambda clave: (
        dict(cp["seccion"]) if clave == "seccion_cuneta" else original(clave)))
    c = M10.capacidad_cuneta(S_cuneta=cp["S"])
    assert c.Q_admisible_m3s == pytest.approx(cp["Q_adm"], rel=REL_CASO_PATRON)
    assert not M10.verificar_aporte(capacidad=c, Q_aporte_m3s=cp["Q"],
                                    origen_aporte="caso patron"
                                    ).verificacion.cumple
    L = M10.longitud_hidraulica_por_tramo(
        capacidad=c, Q_aporte_m3s=cp["Q"], origen_aporte="caso patron",
        longitud_tramo_m=200.0, extremo="B-01")
    assert L.L_hidraulico == pytest.approx(cp["L_200"], rel=REL_CASO_PATRON)


def test_la_velocidad_con_talud_exterior_distinto_de_1_es_la_del_caso_patron():
    cp = CP_T9_CUNETA["velocidad_Z2"]
    y_v, Q_v = M10.caudal_a_velocidad(v=cp["v"], n=cp["n"], S=cp["S"],
                                      Z1=cp["Z1"], Z2=cp["Z2"])
    assert y_v == pytest.approx(cp["y_v"], rel=REL_CASO_PATRON)
    assert Q_v == pytest.approx(cp["Q_v"], rel=REL_CASO_PATRON)


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
