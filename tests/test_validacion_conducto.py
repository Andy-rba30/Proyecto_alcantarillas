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
    "CPDM-BFE-48-1",
    *(f"CPDM-BFE-{d}-{i}" for d in (12, 24, 36, 72, 144) for i in range(1, 5)),
    "CPDM-BFLL-36", "DD22-U", "USACE-T", "USACE-A", "USACE-FC",
    "USACE-CLASE-II",
    # --- VE-3.12 (decision 1 del dueño) --- Las Clases III a V se
    # transcriben DESDE esta tabla del USACE: el contraste comprueba la
    # transcripcion (fuente secundaria [C]), no una segunda fuente.
    "USACE-CLASE-III", "USACE-CLASE-IV", "USACE-CLASE-V",
)
POR_METODO = (
    "DD1-EJ1", "DD1-EJ4", "CPDM-BFLL-12", "CPDM-BFLL-24", "CPDM-BFLL-48",
    "CPDM-4-2", "CPDM-4-5", "CPDM-4-7", "DD22-WI", "DD22-V7",
)
SIN_FUENTE = ("M8-LW-72",)


def test_el_censo_de_clases_es_el_del_documento(contrastes):
    """Que ningun contraste cambie de clase sin que este censo lo diga."""
    assert sorted(contrastes) == sorted(COINCIDEN + POR_METODO + SIN_FUENTE)
    for i in COINCIDEN:
        assert contrastes[i].clase == V.COINCIDE, i
    for i in POR_METODO:
        assert contrastes[i].clase == V.METODO, i
    for i in SIN_FUENTE:
        assert contrastes[i].clase == V.SIN_FUENTE, i


def test_ninguna_cifra_de_W_L_ni_de_D_load_esta_contrastada_con_la_fuente(
        contrastes):
    """
    Correcciones de la revision Fable (A-1): la carga viva y la D-load de M8
    estan TODAS en la categoria «reproduce su propio metodo», y el resumen
    del documento lo dice; no se suman a lo contrastado con la fuente.
    """
    cargas = [i for i in contrastes
              if i.startswith(("DD1-EJ", "CPDM-4-", "M8-LW"))]
    assert cargas
    for i in cargas:
        assert contrastes[i].clase in V.REPRODUCE_SU_METODO, i
    assert "Ninguna cifra de W_L ni de D-load" in V.generar()


def test_la_rama_l_w_menor_que_B_c_se_ejercita(contrastes):
    """
    Correcciones de la revision Fable (A-2): un caso donde el ancho cargado
    l_w es MENOR que B_c, de modo que min(l_w, B_c) toma l_w; y el W_L del
    motor sale de `M8.verificar_concreto`, la ruta real. El mutante
    «W_L = P_L·B_c» lo convierte en DEFECTO.
    """
    det = V.hl93_detalle(2.0, 6.0, 86.0 / 12)
    assert det["l_w"] < 86.0 / 12
    c = contrastes["M8-LW-72"]
    assert c.motor == pytest.approx(c.referencia, rel=TOL_REL_MOTOR)


def test_la_referencia_interpola_sin_la_funcion_del_motor():
    """
    A-2: las referencias de la D-load y de la carga viva no llaman a
    `M8._interpolar` (en `_contrastes_tablas` solo lo usa la columna MOTOR).
    """
    import ast
    import inspect
    import textwrap
    for f in (V._dload_aashto_a_mano, V.hl93_detalle, V._interpolar_a_mano):
        arbol = ast.parse(textwrap.dedent(inspect.getsource(f)))
        llamadas_a_m8 = [
            n.func.attr for n in ast.walk(arbol)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and isinstance(n.func.value, ast.Name) and n.func.value.id == "M8"]
        assert not llamadas_a_m8, (f.__name__, llamadas_a_m8)
    assert V._interpolar_a_mano(48.0, (36.0, 72.0), (4.0, 3.8)) == \
        pytest.approx(3.9333333333333336, rel=TOL_REL_MOTOR)


def test_la_descomposicion_de_dd1_explica_todo_el_exceso(contrastes):
    """
    Correcciones de la revision Fable (M-3): el exceso de M8 sobre DD 1 es
    exactamente presion x longitud efectiva (l_w >= B_c en los dos), y casi
    todo es la L_e.
    """
    for d in V.descomposicion_dd1(list(contrastes.values())):
        assert d["l_w"] >= 37 / 12
        assert d["presion"] * d["longitud"] == pytest.approx(
            d["total"], rel=TOL_REL_MOTOR)
        assert d["longitud"] - 1 > abs(d["presion"] - 1)


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
