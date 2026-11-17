"""
tests/test_validacion_conducto.py
=================================
La validacion externa de M8 contra ejemplos publicados (ACPA DD 1, DD 22 y
CPDM; USACE EM 1110-2-2902): `docs/validacion_conducto.md` se GENERA
(`tests/apoyo/validacion_conducto.py`) y este archivo lo regenera a memoria y
lo compara; y fija cada juicio que el documento imprime: que contrastes
COINCIDEN, cuales difieren por METODO o edicion, que NINGUNO es un defecto
del motor, y las erratas de las fuentes.

NO SE ESCRIBIO EN ROJO PRIMERO, y se dice: es una validacion, no una
correccion; ningun numero del motor se toca. El rojo que si se midio es el de
la mutacion de abajo: alterar una constante del metodo indirecto convierte el
contraste correspondiente en DEFECTO.
"""

from __future__ import annotations

import pytest

from src import constantes_normativas as CN
from tests.apoyo import validacion_conducto as V
from tests.apoyo.validacion_conducto import TOL_REL_CIFRA_IMPRESA, TOL_REL_MOTOR


@pytest.fixture(scope="module")
def contrastes():
    return {c.id: c for c in V.contrastes()}


# ===========================================================================
# Sincronia
# ===========================================================================

def test_validacion_conducto_esta_sincronizado():
    assert V.DOCUMENTO.read_text(encoding="utf-8") == V.generar(), (
        "docs/validacion_conducto.md no esta sincronizado: "
        "python -m tests.apoyo.validacion_conducto --escribir")


# ===========================================================================
# Ningun defecto, y la clase de cada contraste
# ===========================================================================

def test_ningun_contraste_es_un_defecto_del_motor(contrastes):
    defectos = [i for i, c in contrastes.items() if c.clase == V.DEFECTO]
    assert not defectos, defectos


COINCIDEN = (
    "DD1-IM-2ft", "DD1-IM-6ft",
    *(f"CPDM-VAF-{i}" for i in range(1, 5)),
    *(f"CPDM-BFE-{d}-{i}" for d in (12, 24, 36, 72, 144) for i in range(1, 5)),
    "CPDM-BFLL-36", "DD22-U", "USACE-T", "USACE-A", "USACE-FC",
    "USACE-CLASE-II",
)
POR_METODO = (
    "DD1-EJ1", "DD1-EJ4", "CPDM-BFLL-12", "CPDM-BFLL-24", "CPDM-BFLL-48",
    "CPDM-4-2", "CPDM-4-5", "CPDM-4-7", "DD22-WI", "DD22-V7",
)


def test_el_censo_de_clases_es_el_del_documento(contrastes):
    """Que ningun contraste cambie de clase sin que este censo lo diga."""
    assert sorted(contrastes) == sorted(COINCIDEN + POR_METODO)
    for i in COINCIDEN:
        assert contrastes[i].clase == V.COINCIDE, i
    for i in POR_METODO:
        assert contrastes[i].clase == V.METODO, i


@pytest.mark.parametrize("id_", COINCIDEN)
def test_lo_que_coincide_coincide_con_lo_publicado(contrastes, id_):
    c = contrastes[id_]
    assert c.motor == pytest.approx(c.referencia, rel=TOL_REL_MOTOR)
    assert c.motor == pytest.approx(c.publicado, rel=TOL_REL_CIFRA_IMPRESA)


@pytest.mark.parametrize("id_", POR_METODO)
def test_lo_que_difiere_por_metodo_es_el_metodo_de_M8_a_mano(contrastes, id_):
    """
    El motor reproduce su metodo (escrito a mano en el modulo de apoyo, sin
    llamar a M8) y la diferencia con el ejemplo supera la de una cifra
    impresa: es de metodo, y tiene su explicacion.
    """
    c = contrastes[id_]
    assert c.motor == pytest.approx(c.referencia, rel=TOL_REL_MOTOR)
    assert c.referencia != pytest.approx(c.recalculado,
                                         rel=TOL_REL_CIFRA_IMPRESA)
    assert c.explicacion


# ===========================================================================
# Las erratas de las fuentes, fijadas
# ===========================================================================

def test_las_erratas_de_las_fuentes_son_las_dos_censadas(contrastes):
    con_errata = sorted(i for i, c in contrastes.items()
                        if c.errata_de_la_fuente)
    assert con_errata == ["CPDM-4-7", "DD22-WI"]


def test_el_cpdm_4_7_responde_bien_y_su_intermedio_esta_mal(contrastes):
    """
    El CPDM imprime «597.3» en la Ec. 28 y responde «563.2»: con los datos
    que el ejemplo escribe, la cuenta da la respuesta, no el intermedio.
    """
    c = contrastes["CPDM-4-7"]
    assert c.recalculado == pytest.approx(c.publicado,
                                          rel=TOL_REL_CIFRA_IMPRESA)
    assert c.recalculado != pytest.approx(V.CPDM_INTERMEDIO_4_7,
                                          rel=TOL_REL_CIFRA_IMPRESA)


def test_dd22_recalculado_reproduce_su_respuesta(contrastes):
    """La transposicion 4267 no es la cuenta: la Ec. 5 da 4276."""
    c = contrastes["DD22-WI"]
    assert c.recalculado == pytest.approx(c.publicado,
                                          rel=TOL_REL_CIFRA_IMPRESA)


# ===========================================================================
# Mutacion: el contraste mata una constante del metodo indirecto alterada
# ===========================================================================

def test_un_VAF_alterado_vuelve_defecto_el_ejemplo_del_tipo_1(monkeypatch):
    monkeypatch.setitem(CN.VAF_INSTALACION_ESTANDAR, "tipo_1", 1.40)
    (e,) = [x for x in V.EJEMPLOS_DLOAD if x.id == "CPDM-4-2"]
    motor, _sust = V.dload_del_motor(e)
    referencia, _t = V._dload_aashto_a_mano(e, 0.0)
    assert motor != pytest.approx(referencia, rel=TOL_REL_MOTOR)


def test_un_B_FE_alterado_vuelve_defecto_su_contraste(monkeypatch):
    fila = list(CN.BFE_POR_TIPO["tipo_4"])
    fila[1] = 1.8
    monkeypatch.setitem(CN.BFE_POR_TIPO, "tipo_4", tuple(fila))
    c = {x.id: x for x in V._contrastes_tablas()}["CPDM-BFE-24-4"]
    assert c.clase == V.DEFECTO
