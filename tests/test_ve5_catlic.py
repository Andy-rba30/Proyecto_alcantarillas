"""
tests/test_ve5_catlic.py
========================
VE-5, lote «catlic»: catalogo, Fase 10 y licuefaccion.

  * T4-06 (v8 Sec. 3.1): la rama de selva alta del catalogo del TMC, con el
    caracter de RECOMENDACION de su cita (Manual 4.1.1.3.7 a), PDF 82).
"""

import pytest

from src import datos_sitio as ds
from src.constantes_normativas import DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO
from src.modelos import NIVEL_PERFIL, TipoMaterial
from src.modulos import M2_material as M2
from src.normativa import registro as _registro
from src.normativa.esquema import Caracter, Verbo
from tests.apoyo.aproximacion import REL_TRANSPORTE

FECHA = "2026-11-20"
TRAZ_SELVA = ("prueba: corredor ficticio en selva alta, cauces con las cuatro "
              "caracteristicas del num. 4.1.1.3.7 a)")


@pytest.fixture
def selva_alta():
    ds.establecer_dato_dinamico("region_natural", ds.REGION_SELVA_ALTA,
                                TRAZ_SELVA, FECHA, origen="prueba")
    try:
        yield
    finally:
        ds.quitar_dato_dinamico("region_natural")


# ===========================================================================
# T4-06 - la rama de selva alta
# ===========================================================================

def test_t406_la_obra_del_repositorio_es_de_costa_y_la_rama_no_actua():
    assert ds.dato("region_natural").valor == ds.REGION_COSTA
    assert ds.dato("region_natural").nivel == NIVEL_PERFIL
    assert M2.piso_de_selva_alta(TipoMaterial.TMC) is None
    assert M2.siguiente_diametro(TipoMaterial.TMC) == pytest.approx(
        M2._progresion()["inicio"], rel=REL_TRANSPORTE)
    assert M2.catalogo(TipoMaterial.TMC).pasos == ()


def test_t406_la_rama_mira_la_region_siempre_que_el_material_es_tmc():
    ds.reiniciar_usos()
    M2.siguiente_diametro(TipoMaterial.TMC)
    assert "region_natural" in ds.datos_usados()
    ds.reiniciar_usos()
    M2.siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO)
    M2.siguiente_diametro(TipoMaterial.HDPE)
    assert "region_natural" not in ds.datos_usados()


def test_t406_en_selva_alta_el_tmc_arranca_en_el_primer_escalon_de_48_in(selva_alta):
    piso = M2.piso_de_selva_alta(TipoMaterial.TMC)
    assert piso == pytest.approx(DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO,
                                 rel=REL_TRANSPORTE)
    primero = M2.siguiente_diametro(TipoMaterial.TMC)
    # 0.90 + 0.15 k: 1.20 queda por debajo de 48 in (1.2192 m); el primero
    # que no baja es 1.35 m (designado de AASHTO M 36).
    assert primero == pytest.approx(1.35, rel=REL_TRANSPORTE)
    assert primero >= piso
    # El concreto y el HDPE no reciben piso: la recomendacion es solo TMC.
    assert M2.siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO) == \
        pytest.approx(M2._progresion()["inicio"], rel=REL_TRANSPORTE)
    assert M2.piso_de_selva_alta(TipoMaterial.HDPE) is None


def test_t406_la_memoria_dice_recomienda_y_no_obliga(selva_alta):
    pasos = M2.catalogo(TipoMaterial.TMC).pasos
    assert len(pasos) == 1
    p = pasos[0]
    assert p.fundamento_id == M2.FUNDAMENTO_SELVA_ALTA
    assert M2.CITA_SELVA_ALTA in p.citas_textuales
    reg = _registro.construir()
    assert reg.fundamento(M2.FUNDAMENTO_SELVA_ALTA).verbo is Verbo.RECOMIENDA
    assert reg.cita(M2.CITA_SELVA_ALTA).caracter is Caracter.RECOMENDACION
    assert "RECOMIENDA" in p.nota_del_proyecto
    assert p.resultado.valor == pytest.approx(1.35, rel=REL_TRANSPORTE)


def test_t406_la_region_es_un_conjunto_cerrado():
    with pytest.raises(ValueError):
        ds.verificar_declaracion_de_sitio("region_natural", "selva", TRAZ_SELVA)


# ===========================================================================
# T9-01 - la cuneta trapezoidal de la Tabla Nº 34 (> 3000 mm/año)
# ===========================================================================

import math                                                     # noqa: E402

from src import criterios_adoptados as ca                       # noqa: E402
from src.constantes_normativas import (                         # noqa: E402
    CUNETA_DIMENSIONES_MINIMAS_T34, CUNETA_FONDO_MIN_TRAPEZOIDAL_T34,
    K_MANNING_SI)
from src.modelos import DatoInvalidoError                       # noqa: E402
from src.modulos import M10_espaciamiento as M10                # noqa: E402

S_PRUEBA = 0.01


@pytest.fixture
def seccion():
    """Declara una seccion de cuneta y la retira al salir."""
    def declarar(**campos):
        v = dict(ca.CRITERIOS["seccion_cuneta"].valor)
        v.update(campos)
        ca.establecer_valor_dinamico("seccion_cuneta", v)
        return v
    try:
        yield declarar
    finally:
        ca.quitar_valor_dinamico("seccion_cuneta")


def test_t901_el_minimo_de_la_nota_es_el_del_pdf():
    # PDF 181, pag. impresa 178: «* Sección Trapezoidal con un ancho mínimo
    # de fondo de 0.30»; fila «Muy lluviosa (>3000 mm/año)» 0.30* x 1.20.
    assert CUNETA_FONDO_MIN_TRAPEZOIDAL_T34 == pytest.approx(0.30, rel=REL_TRANSPORTE)
    assert CUNETA_DIMENSIONES_MINIMAS_T34["muy_lluviosa_mas_de_3000"] == \
        pytest.approx((0.30, 1.20), rel=REL_TRANSPORTE)


def test_t901_el_archivo_sigue_siendo_triangular_y_no_mueve_la_capacidad(seccion):
    base = M10.capacidad_cuneta(S_cuneta=S_PRUEBA)
    assert base.ancho_fondo_m == 0.0
    # Sin el campo no se le supone una seccion: M10 lo rechaza.
    v = dict(ca.CRITERIOS["seccion_cuneta"].valor)
    del v["ancho_fondo_m"]
    ca._OVERRIDES["seccion_cuneta"] = v
    with pytest.raises(DatoInvalidoError):
        M10.capacidad_cuneta(S_cuneta=S_PRUEBA)

def test_t901_la_capacidad_trapezoidal_contra_el_calculo_a_mano(seccion):
    d, a, b, Z2 = 0.40, 1.20, 0.30, 1.0
    seccion(profundidad_m=d, ancho_m=a, ancho_fondo_m=b, talud_exterior_HV=Z2)
    c = M10.capacidad_cuneta(S_cuneta=S_PRUEBA)
    Z1 = (a - b) / d
    A = b * d + (Z1 + Z2) * d ** 2 / 2
    P = b + d * (math.sqrt(1 + Z1 ** 2) + math.sqrt(1 + Z2 ** 2))
    n = c.n          # 1/K de la Tabla Nº 32, contrastado en test_t9_*
    Q = (K_MANNING_SI / n) * A * (A / P) ** (2 / 3) * S_PRUEBA ** 0.5
    assert c.talud_interior_HV == pytest.approx(Z1, rel=1e-12)
    assert c.area_llena_m2 == pytest.approx(A, rel=1e-12)
    assert c.Q_llena_m3s == pytest.approx(Q, rel=1e-9)
    assert c.ancho_fondo_m == pytest.approx(b, rel=REL_TRANSPORTE)
    assert c.pasos[0].sustitucion[2].simbolo == "b"


def test_t901_el_tirante_de_la_velocidad_limite_cumple_manning(seccion):
    b, Z1, Z2, n, v = 0.30, 3.0, 1.0, 1 / 67, 1.5
    y_v, Q_v = M10.caudal_a_velocidad(v=v, n=n, S=S_PRUEBA, Z1=Z1, Z2=Z2, b=b)
    A, _P, Rh = M10.geometria_cuneta(y=y_v, Z1=Z1, Z2=Z2, b=b)
    V = (K_MANNING_SI / n) * Rh ** (2 / 3) * S_PRUEBA ** 0.5
    assert V == pytest.approx(v, rel=1e-8)
    assert Q_v == pytest.approx(A * v, rel=1e-12)
    # Con b = 0 es la cerrada de siempre.
    assert M10.caudal_a_velocidad(v=v, n=n, S=S_PRUEBA, Z1=Z1, Z2=Z2, b=0.0) == \
        M10.caudal_a_velocidad(v=v, n=n, S=S_PRUEBA, Z1=Z1, Z2=Z2)


@pytest.mark.parametrize("campos,culpable", [
    (dict(ancho_fondo_m=0.20), "ancho_fondo_m"),
    (dict(ancho_fondo_m=1.30), "ancho_fondo_m"),
    (dict(ancho_fondo_m=-0.1), "ancho_fondo_m"),
])
def test_t901_un_fondo_fuera_del_minimo_es_dato_invalido(seccion, campos, culpable):
    v = dict(ca.CRITERIOS["seccion_cuneta"].valor)
    v.update(campos)
    # Se pisa sin la puerta para probar la guardia de segunda linea de M10.
    ca._OVERRIDES["seccion_cuneta"] = v
    with pytest.raises(DatoInvalidoError) as exc:
        M10.capacidad_cuneta(S_cuneta=S_PRUEBA)
    assert culpable in exc.value.campo
