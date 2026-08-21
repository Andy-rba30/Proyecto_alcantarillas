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


def test_los_vacios_de_velocidad_maxima_no_detienen_el_catalogo():
    """v_max_tmc y v_max_hdpe siguen sin valor (Tablero 1.3): el catalogo lo
    refleja con None en vez de lanzar CriterioPendienteError."""
    tmc = catalogo(TipoMaterial.TMC)
    hdpe = catalogo(TipoMaterial.HDPE)
    assert tmc.v_max_rango is None
    assert hdpe.v_max_rango is None
    assert not tmc.v_max_definida
    assert not hdpe.v_max_definida


def test_el_relleno_minimo_de_concreto_y_tmc_sigue_vacio():
    """'h_relleno_min_concreto_tmc' esta sin valor: el catalogo lo refleja."""
    concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    tmc = catalogo(TipoMaterial.TMC)
    assert concreto.h_relleno_min is None
    assert tmc.h_relleno_min is None


def test_el_relleno_minimo_declarado_dinamicamente_lo_ve_el_catalogo():
    """
    Regresion: `_valor_si_declarado` decidia "vacio" leyendo
    `ca.criterio(clave).valor`, que NO consulta los overrides en caliente
    (`ca.establecer_valor_dinamico`, la via de la GUI en gui/app.py:509).
    Un criterio declarado asi le seguia pareciendo vacio a M2, el catalogo
    salia con `h_relleno_min=None` para concreto y TMC, y M7 caia en su
    AssertionError en vez de usar el valor recien declarado.
    """
    ca.establecer_valor_dinamico("h_relleno_min_concreto_tmc", 0.60)
    try:
        concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
        tmc = catalogo(TipoMaterial.TMC)
        assert concreto.h_relleno_min == pytest.approx(0.60)
        assert tmc.h_relleno_min == pytest.approx(0.60)
    finally:
        ca.quitar_valor_dinamico("h_relleno_min_concreto_tmc")

    # y al retirar el override, vuelve a comportarse como vacio
    assert catalogo(TipoMaterial.CONCRETO_REFORZADO).h_relleno_min is None


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
