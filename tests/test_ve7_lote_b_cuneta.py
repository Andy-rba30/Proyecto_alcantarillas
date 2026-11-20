"""
tests/test_ve7_lote_b_cuneta.py
===============================
VE-7, lote B, item B11 (VE5-CAT-02; decision del consultor Fable, triaje
VE-7, 2026-11-20): el [S] OPCIONAL 'precipitacion_anual_corredor_mm' (estudio
hidrologico, sin valor de archivo). Declarado, `M10.capacidad_cuneta`
contrasta la seccion contra SU fila de la Tabla Nº 34; la ventana de la
profundidad baja a 0.30 (la trapezoidal de mas de 3000 mm/año). Sin
declarar, aviso «fila no verificada».

Oraculo independiente: las cuatro filas de la Tabla Nº 34 (pag. impresa
178, PDF 181) escritas aqui a mano --seca <400: 0.20 x 0.50; lluviosa 400 a
<1600: 0.30 x 0.75; muy lluviosa 1600 a <3000: 0.40 x 1.20; >3000: 0.30* x
1.20 trapezoidal con fondo 0.30--.
"""

import pytest

from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src.constantes_normativas import CUNETA_DIMENSIONES_MINIMAS_T34
from src.modelos import DatoInvalidoError
from src.modulos import M10_espaciamiento as M10
from tests.apoyo.aproximacion import REL_TRANSPORTE

S = 0.01
P = M10.DATO_PRECIPITACION_ANUAL
FILAS_A_MANO = {"seca": (0.20, 0.50), "lluviosa": (0.30, 0.75),
                "muy_lluviosa_1600_3000": (0.40, 1.20),
                "muy_lluviosa_mas_de_3000": (0.30, 1.20)}


@pytest.fixture
def precipitacion():
    def declarar(mm):
        ds.establecer_dato_dinamico(
            P, mm, "DATO DE PRUEBA: estacion sintetica, serie inventada",
            "2026-11-20", origen="test")
    try:
        yield declarar
    finally:
        ds.quitar_dato_dinamico(P)


@pytest.fixture
def seccion():
    def declarar(**campos):
        v = dict(ca.CRITERIOS["seccion_cuneta"].valor)
        v.update(campos)
        ca.establecer_valor_dinamico("seccion_cuneta", v)    # por la puerta
    try:
        yield declarar
    finally:
        ca.quitar_valor_dinamico("seccion_cuneta")


def test_el_dato_es_un_S_opcional_sin_valor_que_no_bloquea():
    d = ds.dato(P)
    assert d.valor is None and d.opcional and d.etiqueta == "S"
    assert P not in ds.datos_sin_valor()
    assert ds.valor_si_declarado(P) is None
    from tests.test_ext10_multiobra import DATOS_OPCIONALES_SIN_VALOR
    assert DATOS_OPCIONALES_SIN_VALOR == tuple(sorted(
        k for k, x in ds.DATOS_SITIO.items() if x.opcional and x.valor is None))


@pytest.mark.parametrize("mm,fila", [
    (100, "seca"), (399.9, "seca"), (400, "lluviosa"), (500, "lluviosa"),
    (1600, "muy_lluviosa_1600_3000"), (2999, "muy_lluviosa_1600_3000"),
    (3000, "muy_lluviosa_mas_de_3000"), (3200, "muy_lluviosa_mas_de_3000")])
def test_la_fila_de_la_precipitacion(mm, fila):
    assert M10.fila_de_la_tabla_34(mm) == fila
    assert CUNETA_DIMENSIONES_MINIMAS_T34[fila] == pytest.approx(
        FILAS_A_MANO[fila], rel=REL_TRANSPORTE)


def test_sin_declarar_avisa_fila_no_verificada():
    c = M10.capacidad_cuneta(S_cuneta=S)
    assert any("fila de la Tabla Nº 34 no verificada" in a for a in c.avisos)


def test_la_triangular_sigue_con_0_40_en_la_puerta():
    v = dict(ca.CRITERIOS["seccion_cuneta"].valor, profundidad_m=0.30)
    with pytest.raises(ValueError, match="fuera de la ventana"):
        ca.verificar_declaracion("seccion_cuneta", v)
    # la trapezoidal de 0.30 si entra por la puerta
    ca.verificar_declaracion("seccion_cuneta",
                             dict(v, ancho_fondo_m=0.30))


def test_3200_mm_con_la_triangular_es_invalido(precipitacion):
    precipitacion(3200)
    with pytest.raises(DatoInvalidoError) as exc:
        M10.capacidad_cuneta(S_cuneta=S)
    assert exc.value.campo == "seccion_cuneta.ancho_fondo_m"
    assert "TRAPEZOIDAL" in str(exc.value)


def test_3200_mm_con_la_trapezoidal_minima_vale(precipitacion, seccion):
    precipitacion(3200)
    seccion(profundidad_m=0.30, ancho_m=1.20, ancho_fondo_m=0.30)
    c = M10.capacidad_cuneta(S_cuneta=S)
    assert c.ancho_fondo_m == pytest.approx(0.30, rel=REL_TRANSPORTE)
    assert not any("no verificada" in a for a in c.avisos)


def test_500_mm_es_la_fila_0_30_por_0_75(precipitacion):
    precipitacion(500)
    c = M10.capacidad_cuneta(S_cuneta=S)          # la de archivo, 0.40 x 1.20
    assert not any("no verificada" in a for a in c.avisos)
    assert "Lluviosa (De 400 a <1600 mm/año)" in c.pasos[0].nota_del_proyecto
    assert M10.fila_de_la_tabla_34(500) == "lluviosa"
    # La segunda linea de M10: la triangular de 0.30 x 0.75, minimo de esa
    # fila, pasa (se pisa sin la puerta, que no ve la precipitacion).
    from tests.apoyo.criterios import con_valor
    v = dict(ca.CRITERIOS["seccion_cuneta"].valor, profundidad_m=0.30,
             ancho_m=0.75)
    with con_valor("seccion_cuneta", v, motivo="el minimo de la fila "
                   "lluviosa, para la segunda linea de M10"):
        assert M10.capacidad_cuneta(S_cuneta=S).profundidad_m == \
            pytest.approx(0.30, rel=REL_TRANSPORTE)


def test_2000_mm_y_0_30_de_profundidad_no_vale(precipitacion):
    precipitacion(2000)
    from tests.apoyo.criterios import con_valor
    v = dict(ca.CRITERIOS["seccion_cuneta"].valor, profundidad_m=0.30)
    with con_valor("seccion_cuneta", v, motivo="bajo el minimo de su fila, "
                   "para la segunda linea de M10"):
        with pytest.raises(DatoInvalidoError) as exc:
            M10.capacidad_cuneta(S_cuneta=S)
    assert exc.value.campo == "seccion_cuneta.profundidad_m"


# ===========================================================================
# Dictamen Fable sobre B11: 2a (3000 exactos) y 2b (la trapezoidal de 0.30
# sin la precipitacion)
# ===========================================================================

def test_3000_exactos_va_a_la_trapezoidal_y_lo_dice(precipitacion, seccion):
    precipitacion(3000)
    seccion(profundidad_m=0.30, ancho_m=1.20, ancho_fondo_m=0.30)
    c = M10.capacidad_cuneta(S_cuneta=S)
    assert M10.fila_de_la_tabla_34(3000) == "muy_lluviosa_mas_de_3000"
    nota = c.pasos[0].nota_del_proyecto
    assert "no cubre exactamente 3000" in nota
    assert "limite inferior cerrado" in nota


def test_trapezoidal_0_30_sin_precipitacion_se_detiene(seccion):
    from src.modelos import DatoFaltanteError
    seccion(profundidad_m=0.30, ancho_m=1.20, ancho_fondo_m=0.30)
    with pytest.raises(DatoFaltanteError) as exc:
        M10.capacidad_cuneta(S_cuneta=S)
    assert exc.value.campo == P
    assert "declarar la precipitacion" in str(exc.value)


def test_trapezoidal_de_0_40_sin_precipitacion_sigue_con_su_aviso(seccion):
    seccion(profundidad_m=0.40, ancho_m=1.20, ancho_fondo_m=0.30)
    c = M10.capacidad_cuneta(S_cuneta=S)
    assert any("no verificada" in a for a in c.avisos)
