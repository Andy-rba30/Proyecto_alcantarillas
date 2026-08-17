"""
tests/test_M5_verificaciones.py
=================================
M5 contra las nueve verificaciones de la tabla de Fase 5:

    V1, V2, V9      calculo directo, un umbral [N] o el tope de M2.
    V3              rango [N] para concreto; CriterioPendienteError para
                    TMC y HDPE mientras 'v_max_tmc' / 'v_max_hdpe' esten
                    vacios (Tablero 1.3).
    V4              resguardo de Sec. 5.1 leido desde 'resguardo_HW_subrasante'
                    (criterio_aplicado debe apuntar a ese criterio, cuya
                    etiqueta es [N->], no [N]).
    V5, V8          CriterioPendienteError: la hoja de ruta no entrega
                    formula/metodo/dato, y los dos criterios nuevos
                    ('remanso_derecho_via', 'TR_evento_extremo') se declaran
                    vacios a proposito.
    V7              Fase 8 SI entrega formula (ΣW >= FS*U): se calcula
                    completo cuando 'peso_especifico_relleno_kn_m3' y
                    'FS_flotacion' estan declarados, y se detiene en el
                    primero de los dos que falte.
    V6              cumple por construccion: M2/MD no ofrecen diseño
                    multibarril.
    verificar()     el agregado con la firma de MD.Verificador: se detiene
                    en la primera pendiente, en el orden de la tabla.
"""

import math

import pytest

import criterios_adoptados as ca
from constantes_normativas import V_MIN, Y_SOBRE_D_MAX
from modelos import (ControlGobernante, CriterioPendienteError, Familia,
                     PuntoCritico, ResultadoHidraulico, TipoMaterial)
from modulos.M2_material import catalogo
from modulos.M5_verificaciones import (resguardo_por_cbr, v1_borde_libre,
                                       v2_velocidad_minima,
                                       v3_velocidad_maxima,
                                       v4_carga_entrada, v5_remanso,
                                       v6_material_solido_arrastre,
                                       v7_flotacion, v8_evento_extremo,
                                       v9_disponibilidad_diametro, verificar)

D_REFERENCIA = 0.90


def _punto(**cambios) -> PuntoCritico:
    base = dict(
        id="A-01",
        progresiva_km=0.380,
        progresiva_display="0+380",
        familia=Familia.A,
        Q_m3s=1.1673,
        area_ha=850.0,
        S_cauce=0.006,
        cota_terreno=42.10,
        cota_rasante=44.20,
        cota_subrasante=44.05,
        cbr_subrasante=8.5,
        esviaje_grados=15.0,
        ancho_plataforma=9.60,
        cota_fondo_receptor=41.30,
        Q_receptor_m3s=None,
        cota_TW=None,
        sucs_fundacion="SM",
    )
    base.update(cambios)
    return PuntoCritico(**base)


def _resultado(*, y_normal=0.60, y_critico=0.40, V=1.5, Q=1.0,
              HW_entrada=0.50, HW_salida=0.20,
              control=ControlGobernante.ENTRADA) -> ResultadoHidraulico:
    return ResultadoHidraulico(
        y_normal=y_normal, y_critico=y_critico, V=V, Q=Q,
        HW_entrada=HW_entrada, HW_salida=HW_salida,
        control_gobernante=control,
    )


@pytest.fixture
def concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


@pytest.fixture
def tmc():
    return catalogo(TipoMaterial.TMC)


@pytest.fixture
def hdpe():
    return catalogo(TipoMaterial.HDPE)


# ===========================================================================
# V1 - Borde libre
# ===========================================================================

def test_v1_cumple_dentro_del_borde_libre():
    v = v1_borde_libre(D=0.90, resultado=_resultado(y_normal=0.60))
    assert v.cumple
    assert v.codigo == "V1"
    assert v.numeral == "4.1.1.3.7 b)"
    assert v.valor_admisible == pytest.approx(Y_SOBRE_D_MAX)
    assert v.criterio_aplicado is None


def test_v1_incumple_sobre_el_borde_libre():
    v = v1_borde_libre(D=0.90, resultado=_resultado(y_normal=0.80))
    assert not v.cumple
    assert v.valor_obtenido == pytest.approx(0.80 / 0.90)


def test_v1_en_el_limite_exacto_cumple():
    v = v1_borde_libre(D=0.90, resultado=_resultado(y_normal=0.90 * Y_SOBRE_D_MAX))
    assert v.cumple


# ===========================================================================
# V2 - Velocidad minima
# ===========================================================================

def test_v2_cumple_sobre_el_piso():
    v = v2_velocidad_minima(resultado=_resultado(V=1.0))
    assert v.cumple
    assert v.codigo == "V2"
    assert v.valor_admisible == pytest.approx(V_MIN)


def test_v2_incumple_bajo_el_piso():
    v = v2_velocidad_minima(resultado=_resultado(V=0.10))
    assert not v.cumple


# ===========================================================================
# V3 - Velocidad maxima
# ===========================================================================

def test_v3_concreto_cumple_dentro_del_rango(concreto):
    v = v3_velocidad_maxima(material=concreto, resultado=_resultado(V=4.5))
    assert v.cumple
    assert v.codigo == "V3"
    assert v.valor_admisible == pytest.approx((3.0, 6.0))
    assert v.criterio_aplicado is None


def test_v3_concreto_incumple_sobre_el_maximo(concreto):
    v = v3_velocidad_maxima(material=concreto, resultado=_resultado(V=7.0))
    assert not v.cumple


def test_v3_concreto_incumple_bajo_el_minimo(concreto):
    """El rango de la Tabla N 10 es de dos lados: 3.0-6.0, no solo un techo."""
    v = v3_velocidad_maxima(material=concreto, resultado=_resultado(V=1.0))
    assert not v.cumple


@pytest.mark.parametrize("material_fixture, clave", [
    ("tmc", "v_max_tmc"),
    ("hdpe", "v_max_hdpe"),
])
def test_v3_tmc_hdpe_lanza_pendiente_mientras_no_haya_valor(material_fixture,
                                                            clave, request):
    material = request.getfixturevalue(material_fixture)
    with pytest.raises(CriterioPendienteError) as excinfo:
        v3_velocidad_maxima(material=material, resultado=_resultado(V=2.0))
    assert excinfo.value.clave == clave


# ===========================================================================
# V4 - Carga a la entrada HW
# ===========================================================================

@pytest.mark.parametrize("cbr, resguardo_esperado", [
    (25.0, 0.60),   # >= 20 %: excelente-muy buena
    (20.0, 0.60),   # limite exacto, incluido en el primer tramo
    (15.0, 0.80),   # 6-20 %: buena-regular
    (6.0, 0.80),    # limite exacto
    (4.0, 1.00),    # 3-6 %: insuficiente
    (3.0, 1.00),    # limite exacto
    (1.5, 1.20),    # < 3 %: inadecuada
])
def test_resguardo_por_cbr_reproduce_la_tabla_5_1(cbr, resguardo_esperado):
    assert resguardo_por_cbr(cbr) == pytest.approx(resguardo_esperado)


def test_v4_usa_el_criterio_resguardo_y_su_etiqueta_es_N_flecha():
    punto = _punto(cota_terreno=42.10, cota_subrasante=44.05, cbr_subrasante=8.5)
    # resguardo(CBR=8.5) = 0.80 m (tramo 6-20%). admisible = 44.05 - 0.80 = 43.25
    # HW_cota = cota_terreno + HW = 42.10 + HW
    v = v4_carga_entrada(punto=punto, resultado=_resultado(HW_entrada=0.50))

    assert v.codigo == "V4"
    assert v.criterio_aplicado == "resguardo_HW_subrasante"
    assert ca.criterio(v.criterio_aplicado).etiqueta == "N->"
    assert v.valor_admisible == pytest.approx(44.05 - 0.80)
    assert v.valor_obtenido == pytest.approx(42.10 + 0.50)
    assert v.cumple      # 42.60 <= 43.25


def test_v4_incumple_cuando_el_HW_supera_la_subrasante_con_resguardo():
    punto = _punto(cota_terreno=42.10, cota_subrasante=44.05, cbr_subrasante=8.5)
    v = v4_carga_entrada(punto=punto, resultado=_resultado(HW_entrada=3.0))
    assert not v.cumple


def test_v4_usa_HW_del_control_gobernante():
    """Si gobierna salida, V4 debe leer HW_salida, no HW_entrada."""
    punto = _punto(cota_terreno=42.10, cota_subrasante=44.05, cbr_subrasante=8.5)
    resultado = _resultado(HW_entrada=0.10, HW_salida=3.0,
                           control=ControlGobernante.SALIDA)
    v = v4_carga_entrada(punto=punto, resultado=resultado)
    assert v.valor_obtenido == pytest.approx(42.10 + 3.0)
    assert not v.cumple


# ===========================================================================
# V5, V7, V8 - Pendientes declarados
# ===========================================================================

def test_v5_lanza_pendiente_por_falta_de_metodo_y_dato():
    punto = _punto()
    with pytest.raises(CriterioPendienteError) as excinfo:
        v5_remanso(punto=punto, resultado=_resultado())
    assert excinfo.value.clave == "remanso_derecho_via"


def test_v7_lanza_pendiente_por_falta_de_peso_especifico_del_relleno(concreto):
    """
    Con 'peso_especifico_relleno_kn_m3' vacio, V7 se detiene ahi -- antes de
    llegar a 'FS_flotacion' -- porque el peso del relleno se arma antes que
    el umbral en `v7_flotacion`.
    """
    punto = _punto()
    with pytest.raises(CriterioPendienteError) as excinfo:
        v7_flotacion(punto=punto, material=concreto, D=0.90,
                     resultado=_resultado())
    assert excinfo.value.clave == "peso_especifico_relleno_kn_m3"


def test_v7_lanza_pendiente_por_falta_de_FS_con_peso_ya_declarado(concreto,
                                                                   monkeypatch):
    """Con el peso del relleno declarado, el siguiente vacio es 'FS_flotacion'."""
    original = ca.CRITERIOS["peso_especifico_relleno_kn_m3"]
    monkeypatch.setitem(
        ca.CRITERIOS, "peso_especifico_relleno_kn_m3",
        original.__class__(**{**original.__dict__, "valor": 18.0}),
    )
    punto = _punto()
    with pytest.raises(CriterioPendienteError) as excinfo:
        v7_flotacion(punto=punto, material=concreto, D=0.90,
                     resultado=_resultado())
    assert excinfo.value.clave == "FS_flotacion"


def test_v7_calcula_completo_con_los_dos_criterios_declarados(concreto,
                                                                monkeypatch):
    """
    cota_terreno=42.10 (= cota de entrada supuesta), D=0.90 -> clave=43.00.
    cota_subrasante=44.05 -> altura_relleno = 1.05 m.
    U = 9.81 * (pi/4) * 0.90^2 = 6.2417... kN/m
    W = 18.0 * 0.90 * 1.05 = 17.01 kN/m
    FS = 1.5 -> FS*U = 9.3626... kN/m -> W >= FS*U: cumple.
    """
    for clave, val in (("peso_especifico_relleno_kn_m3", 18.0),
                       ("FS_flotacion", 1.5)):
        original = ca.CRITERIOS[clave]
        monkeypatch.setitem(
            ca.CRITERIOS, clave,
            original.__class__(**{**original.__dict__, "valor": val}),
        )
    punto = _punto()
    v = v7_flotacion(punto=punto, material=concreto, D=0.90,
                     resultado=_resultado())
    assert v.codigo == "V7"
    assert v.criterio_aplicado == "FS_flotacion"
    assert v.valor_obtenido == pytest.approx(17.01, abs=1e-6)
    assert v.valor_admisible == pytest.approx(1.5 * 9.81 * (math.pi / 4) * 0.90 ** 2, abs=1e-6)
    assert v.cumple


def test_v8_lanza_pendiente_por_falta_de_TR_y_umbral():
    punto = _punto()
    with pytest.raises(CriterioPendienteError) as excinfo:
        v8_evento_extremo(punto=punto, resultado=_resultado())
    assert excinfo.value.clave == "TR_evento_extremo"


def test_los_criterios_nuevos_estan_declarados_vacios():
    for clave in ("remanso_derecho_via", "peso_especifico_relleno_kn_m3",
                 "FS_flotacion", "TR_evento_extremo"):
        assert clave in ca.criterios_sin_valor()


# ===========================================================================
# V6 - Material solido de arrastre
# ===========================================================================

def test_v6_cumple_por_construccion():
    v = v6_material_solido_arrastre()
    assert v.cumple
    assert v.codigo == "V6"
    assert v.criterio_aplicado is None


# ===========================================================================
# V9 - Disponibilidad de diametro
# ===========================================================================

def test_v9_cumple_bajo_el_tope(concreto):
    v = v9_disponibilidad_diametro(D=0.90, material=concreto)
    assert v.cumple
    assert v.codigo == "V9"
    assert v.valor_admisible == pytest.approx(concreto.D_max)
    assert v.criterio_aplicado == "diametros_normalizados"


def test_v9_incumple_sobre_el_tope(hdpe):
    """HDPE topa en 1.50 m (el mas restrictivo): 1.65 ya lo supera."""
    v = v9_disponibilidad_diametro(D=1.65, material=hdpe)
    assert not v.cumple
    assert v.valor_admisible == pytest.approx(1.50)


def test_v9_en_el_tope_exacto_cumple(hdpe):
    v = v9_disponibilidad_diametro(D=hdpe.D_max, material=hdpe)
    assert v.cumple


# ===========================================================================
# verificar() - el agregado que llama MD
# ===========================================================================

def test_verificar_se_detiene_en_V5_la_primera_pendiente_en_orden(concreto):
    """
    Con concreto, V3 no esta pendiente (rango [N] directo): la primera
    excepcion de la secuencia V1..V9 es V5.
    """
    punto = _punto()
    with pytest.raises(CriterioPendienteError) as excinfo:
        verificar(punto=punto, material=concreto, D=0.90,
                 resultado=_resultado(y_normal=0.60, V=1.5))
    assert excinfo.value.clave == "remanso_derecho_via"


def test_verificar_con_tmc_se_detiene_antes_en_V3(tmc):
    """Con TMC, V3 esta pendiente y precede a V5 en el orden de la tabla."""
    punto = _punto()
    with pytest.raises(CriterioPendienteError) as excinfo:
        verificar(punto=punto, material=tmc, D=0.90,
                 resultado=_resultado(y_normal=0.60, V=1.5))
    assert excinfo.value.clave == "v_max_tmc"


def test_verificar_tiene_la_firma_del_protocol_de_MD(concreto):
    """MD.Verificador exige (punto=, material=, D=, resultado=), por keyword."""
    with pytest.raises(CriterioPendienteError):
        verificar(punto=_punto(), material=concreto, D=0.90,
                 resultado=_resultado())
