"""
tests/test_M2_material.py
==========================
M2 contra la Fase 3: catalogo de diametros normalizado (Sec. 3.2) y matriz de
decision de material (Sec. 3.4).

Los tests que mas importan son cuatro:

    - la progresion arranca en 0.90 m y sube de 0.15 m en 0.15 m;
    - cada material se detiene en SU tope de Sec. 3.2 (el de HDPE es el mas
      restrictivo: ~1.50 m) y siguiente_diametro() devuelve None ahi, nunca
      un numero que no existe como producto;
    - v_max_rango y h_relleno_min salen en None para TMC/HDPE sin lanzar
      CriterioPendienteError, porque el vacio esta documentado, no relleno;
    - la Familia C no tiene candidatos: su seccion es marco o multicelda.
"""

from pathlib import Path

import pytest

import criterios_adoptados as ca
from modelos import DatoInvalidoError, Familia, Material, TipoMaterial
from modulos.M0_carga import cargar_puntos
from modulos.M2_material import catalogo, materiales_candidatos, siguiente_diametro

CSV_VALIDO = Path(__file__).resolve().parent / "ejemplo_puntos.csv"


@pytest.fixture
def puntos():
    return cargar_puntos(CSV_VALIDO)


@pytest.fixture
def punto_a(puntos):
    return puntos[0]        # A-01, Familia A


@pytest.fixture
def punto_c(puntos):
    return puntos[3]        # C-01, Familia C


# ---------------------------------------------------------------------------
# Sec. 3.2 - Progresion de diametros
# ---------------------------------------------------------------------------

def test_el_primer_diametro_es_el_minimo_normativo():
    assert siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO) == pytest.approx(0.90)


def test_el_paso_es_de_15_cm():
    D0 = siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO)
    D1 = siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO, D0)
    D2 = siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO, D1)
    assert D1 == pytest.approx(1.05)
    assert D2 == pytest.approx(1.20)


def test_admite_el_tipo_de_material_como_string():
    assert siguiente_diametro("concreto_reforzado") == pytest.approx(0.90)


@pytest.mark.parametrize("material, esperado", [
    (TipoMaterial.CONCRETO_REFORZADO, 2.70),
    (TipoMaterial.TMC, 2.10),
    (TipoMaterial.HDPE, 1.50),
])
def test_cada_material_se_detiene_en_su_tope(material, esperado):
    D = siguiente_diametro(material)
    ultimo = None
    while D is not None:
        assert D <= esperado + 1e-6
        ultimo = D
        D = siguiente_diametro(material, D)
    assert ultimo == pytest.approx(esperado)


def test_el_hdpe_es_el_mas_restrictivo():
    """Sec. 3.2: sin tope, el solver podria converger a un HDPE de 2.70 m,
    que no existe como producto AASHTO M294."""
    D = 1.50
    assert siguiente_diametro(TipoMaterial.HDPE, D) is None


def test_un_diametro_fuera_de_la_progresion_es_invalido():
    with pytest.raises(DatoInvalidoError) as exc:
        siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO, 1.00)
    assert exc.value.campo == "D"


def test_un_material_desconocido_es_invalido():
    with pytest.raises(DatoInvalidoError) as exc:
        siguiente_diametro("fierro_fundido")
    assert exc.value.campo == "material"


# ---------------------------------------------------------------------------
# Sec. 3.4 - Catalogo de material
# ---------------------------------------------------------------------------

def test_catalogo_devuelve_un_material_completo():
    concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    assert isinstance(concreto, Material)
    assert concreto.tipo is TipoMaterial.CONCRETO_REFORZADO
    assert concreto.D_max == pytest.approx(2.70)
    assert concreto.n_min == pytest.approx(0.010)
    assert concreto.n_max == pytest.approx(0.013)
    assert concreto.v_max_rango == pytest.approx((3.0, 6.0))
    assert concreto.seccion_eg2013 == "506"


def test_el_hdpe_usa_el_rango_de_manning_por_analogia():
    hdpe = catalogo(TipoMaterial.HDPE)
    assert hdpe.n_min == pytest.approx(0.010)
    assert hdpe.n_max == pytest.approx(0.013)
    assert hdpe.seccion_eg2013 == "508"
    assert hdpe.h_relleno_min == pytest.approx(0.30)   # [N] directo, sin vacio


def test_la_velocidad_maxima_declarada_llega_al_catalogo():
    """
    'v_max_tmc' y 'v_max_hdpe' ya estan declarados (WSDOT Hydraulics Manual,
    Tabla 8-4): el catalogo los trae y `v_max_definida` lo confirma.
    """
    tmc = catalogo(TipoMaterial.TMC)
    hdpe = catalogo(TipoMaterial.HDPE)
    assert tmc.v_max_rango == ca.valor("v_max_tmc")
    assert hdpe.v_max_rango == ca.valor("v_max_hdpe")
    assert tmc.v_max_definida
    assert hdpe.v_max_definida


def test_un_vacio_de_velocidad_maxima_no_detiene_el_catalogo(monkeypatch):
    """
    Lo que el test anterior protegia antes de que el criterio tuviera valor, y
    sigue siendo la conducta correcta si alguna vez vuelve a vaciarse: M2 lee
    esos criterios con tolerancia y refleja el vacio con None, en vez de
    lanzar CriterioPendienteError al construir el catalogo. Quien se detiene
    es V3, que es donde el numero hace falta.
    """
    original = ca.CRITERIOS["v_max_tmc"]
    monkeypatch.setitem(ca.CRITERIOS, "v_max_tmc",
                        original.__class__(**{**original.__dict__,
                                              "valor": None}))
    tmc = catalogo(TipoMaterial.TMC)
    assert tmc.v_max_rango is None
    assert not tmc.v_max_definida


# ---------------------------------------------------------------------------
# Declaracion en caliente: la via de la GUI
# ---------------------------------------------------------------------------
#
# `ca.establecer_valor_dinamico` es como la pestana "Criterios" de la GUI
# declara un criterio pendiente sin tocar criterios_adoptados.py. El catalogo
# tiene que verlo igual que si estuviera escrito en el archivo.
#
# El caso que fallaba era exactamente este: criterio VACIO en el archivo y
# declarado en caliente. `_valor_si_declarado` miraba `ca.criterio().valor` --
# el dict del archivo -- y devolvia None sin consultar los overrides, de modo
# que la declaracion del usuario se perdia. Con la clave YA declarada en el
# archivo el bug no se veia, porque la lectura caia en `ca.valor()`, que si
# resuelve overrides.

@pytest.fixture
def vaciar_criterio(monkeypatch):
    """Deja un criterio sin valor en el archivo, como estaba antes de cerrarse."""
    def _vaciar(clave):
        original = ca.CRITERIOS[clave]
        monkeypatch.setitem(ca.CRITERIOS, clave,
                            original.__class__(**{**original.__dict__,
                                                  "valor": None}))
    return _vaciar


def test_el_n_de_manning_del_hdpe_declarado_en_caliente_llega_al_catalogo(
        vaciar_criterio):
    """
    El peor de los tres: el None se desempaquetaba en (n_min, n_max) y
    reventaba con TypeError -- un fallo de PROGRAMA por un dato que el usuario
    si habia declarado.
    """
    vaciar_criterio("n_manning_hdpe")
    ca.establecer_valor_dinamico("n_manning_hdpe", (0.011, 0.012))
    try:
        hdpe = catalogo(TipoMaterial.HDPE)
        assert (hdpe.n_min, hdpe.n_max) == (0.011, 0.012)
    finally:
        ca.quitar_valor_dinamico("n_manning_hdpe")


def test_el_relleno_minimo_declarado_en_caliente_llega_al_catalogo(
        vaciar_criterio):
    vaciar_criterio("h_relleno_min_concreto_tmc")
    ca.establecer_valor_dinamico("h_relleno_min_concreto_tmc", 0.75)
    try:
        concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
        assert concreto.h_relleno_min == pytest.approx(0.75)
    finally:
        ca.quitar_valor_dinamico("h_relleno_min_concreto_tmc")


def test_la_velocidad_maxima_declarada_en_caliente_llega_al_catalogo(
        vaciar_criterio):
    vaciar_criterio("v_max_tmc")
    ca.establecer_valor_dinamico("v_max_tmc", 3.9)
    try:
        tmc = catalogo(TipoMaterial.TMC)
        assert tmc.v_max_rango == pytest.approx(3.9)
        assert tmc.v_max_definida
    finally:
        ca.quitar_valor_dinamico("v_max_tmc")


def test_la_declaracion_en_caliente_pisa_al_valor_del_archivo():
    """
    Sin vaciar nada: el override tiene que ganar sobre el valor escrito. Esta
    rama ya funcionaba antes del arreglo (caia en `ca.valor()`), y el test la
    fija para que siga funcionando.
    """
    assert ca.criterio("v_max_tmc").valor is not None
    ca.establecer_valor_dinamico("v_max_tmc", 3.9)
    try:
        assert catalogo(TipoMaterial.TMC).v_max_rango == pytest.approx(3.9)
    finally:
        ca.quitar_valor_dinamico("v_max_tmc")
    assert catalogo(TipoMaterial.TMC).v_max_rango == ca.valor("v_max_tmc")


def test_el_relleno_minimo_de_concreto_y_tmc_es_el_0_30_adoptado():
    """
    'h_relleno_min_concreto_tmc' dejo de estar vacio: se adopto 0.30 m [N->]
    por analogia con el unico valor que EG-2013 si fija (508.07, HDPE), sobre
    el vacio verificado de Sec. 14.a del manifiesto. El catalogo lo refleja
    para los DOS materiales -- el criterio no se partio, porque con un valor
    compartido el split no aporta nada.
    """
    concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    tmc = catalogo(TipoMaterial.TMC)
    assert concreto.h_relleno_min == pytest.approx(0.30)
    assert tmc.h_relleno_min == pytest.approx(0.30)
    # Y es el MISMO numero que el [N] del HDPE: eso es la analogia.
    assert catalogo(TipoMaterial.HDPE).h_relleno_min == pytest.approx(0.30)


def test_un_material_desconocido_en_catalogo_es_invalido():
    with pytest.raises(DatoInvalidoError):
        catalogo("pvc")


# ---------------------------------------------------------------------------
# Filtro de candidatos
# ---------------------------------------------------------------------------

def test_familia_a_tiene_los_tres_materiales_candidatos(punto_a):
    candidatos = materiales_candidatos(punto_a)
    assert {m.tipo for m in candidatos} == set(TipoMaterial)


def test_familia_c_no_tiene_candidatos(punto_c):
    """Sec. 2.3: la Familia C es marco o multicelda, no un conducto circular."""
    assert punto_c.familia is Familia.C
    assert materiales_candidatos(punto_c) == ()
