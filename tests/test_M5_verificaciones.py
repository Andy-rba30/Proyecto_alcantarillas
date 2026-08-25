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
    V7              Fase 8 SI entrega procedimiento, y desde la correccion
                    del marco LRFD es un equilibrio de factores de carga
                    (gamma_DC*DC + gamma_EV*EV >= gamma_WA*U), no un FS
                    global. 'factores_carga_aashto' es [C] (AASHTO LRFD 9a
                    ed.) y ya no se detiene; el unico vacio que le queda a V7
                    es 'peso_especifico_relleno_kn_m3'.
    V6              cumple por construccion: M2/MD no ofrecen diseño
                    multibarril.
    verificar()     el agregado con la firma de MD.Verificador: se detiene
                    en la primera pendiente, en el orden de la tabla.
"""

import math

import pytest

import criterios_adoptados as ca
from constantes_normativas import V_MIN, Y_SOBRE_D_MAX
from modelos import (ControlGobernante, CriterioPendienteError,
                     DatoFaltanteError, ErrorProyecto, Familia,
                     PuntoCritico, ResultadoHidraulico, TipoMaterial)
from modulos.M2_material import catalogo
from modulos.M5_verificaciones import (CRITERIO_V_MAX_CONCRETO,
                                       resguardo_por_cbr, v1_borde_libre,
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
        NF_profundidad_m=None,     # lo da el estudio geotecnico, por punto
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

def test_v3_concreto_verifica_solo_el_techo(concreto):
    """
    El admisible que V3 publica es UN escalar -- el extremo superior de la
    Tabla N 10 -- no el par. Si vuelve a salir la tupla, alguien restauro la
    lectura de piso+techo que esta correccion elimino.
    """
    v = v3_velocidad_maxima(material=concreto, resultado=_resultado(V=4.5))
    assert v.cumple
    assert v.codigo == "V3"
    assert v.valor_admisible == pytest.approx(6.0)
    assert v.criterio_aplicado is None


def test_v3_concreto_incumple_sobre_el_maximo(concreto):
    v = v3_velocidad_maxima(material=concreto, resultado=_resultado(V=7.0))
    assert not v.cumple


def test_v3_concreto_cumple_bajo_el_extremo_inferior(concreto):
    """
    1.0 m/s en concreto CUMPLE V3.

    Los dos numeros de la Tabla N 10 son velocidades maximas (el titulo de la
    tabla, num. 4.1.1.3.6 pag. 76, es "Velocidades maximas admisibles en
    conductos revestidos"): el rango recorre la calidad del revestimiento, no
    un piso y un techo. Antes esta misma velocidad se rechazaba por V3, que
    era exigir un segundo piso, por material y mas alto que el normativo, sin
    numeral que lo sostenga. El piso lo pone V2 y son 0.25 m/s.
    """
    v = v3_velocidad_maxima(material=concreto, resultado=_resultado(V=1.0))
    assert v.cumple


def test_v3_sin_declarar_el_criterio_usa_el_techo_normativo(concreto, monkeypatch):
    """
    'v_max_concreto_eleccion' es OPCIONAL: sin declarar, V3 no se bloquea --
    aplica el 6.0 [N] de la Tabla N 10 y no registra el criterio como usado,
    de modo que no ensucia la declaracion de la memoria.
    """
    ca.limpiar_valores_dinamicos()
    assert ca.criterio(CRITERIO_V_MAX_CONCRETO).valor is None

    v = v3_velocidad_maxima(material=concreto, resultado=_resultado(V=5.5))
    assert v.cumple
    assert v.valor_admisible == pytest.approx(6.0)
    assert v.criterio_aplicado is None, (
        "sin declarar, el umbral es [N] de la tabla y la memoria no debe "
        "atribuirlo a un criterio adoptado")
    assert CRITERIO_V_MAX_CONCRETO not in ca.criterios_usados()


def test_v3_declarado_baja_el_techo_y_lo_atribuye(concreto, monkeypatch):
    """
    Declarado en 4.5, el techo baja: 4.0 m/s cumple y 5.0 no. Y la
    `Verificacion` lo ATRIBUYE al criterio, que es lo que permite a un revisor
    distinguir el umbral normativo del adoptado.
    """
    original = ca.CRITERIOS[CRITERIO_V_MAX_CONCRETO]
    monkeypatch.setitem(
        ca.CRITERIOS, CRITERIO_V_MAX_CONCRETO,
        original.__class__(**{**original.__dict__, "valor": 4.5}))

    pasa = v3_velocidad_maxima(material=concreto, resultado=_resultado(V=4.0))
    assert pasa.cumple
    assert pasa.valor_admisible == pytest.approx(4.5)
    assert pasa.criterio_aplicado == CRITERIO_V_MAX_CONCRETO

    falla = v3_velocidad_maxima(material=concreto, resultado=_resultado(V=5.0))
    assert not falla.cumple, (
        "5.0 m/s supera el techo declarado de 4.5: tiene que incumplir "
        "aunque siga por debajo del 6.0 normativo")


def test_v3_declarado_no_reintroduce_un_piso(concreto, monkeypatch):
    """
    El criterio baja el TECHO, no crea un piso. Con 4.5 declarado, 1.0 m/s
    sigue cumpliendo V3: la correccion de la Parte B no se deshace por
    declararlo.
    """
    original = ca.CRITERIOS[CRITERIO_V_MAX_CONCRETO]
    monkeypatch.setitem(
        ca.CRITERIOS, CRITERIO_V_MAX_CONCRETO,
        original.__class__(**{**original.__dict__, "valor": 4.5}))
    assert v3_velocidad_maxima(material=concreto,
                               resultado=_resultado(V=1.0)).cumple


def test_v3_solo_el_concreto_lee_ese_criterio(tmc, monkeypatch):
    """
    'v_max_concreto_eleccion' es del concreto. TMC y HDPE siguen leyendo su
    propio criterio y lanzando CriterioPendienteError mientras este vacio:
    declarar el del concreto no puede desbloquearlos por la puerta de atras.
    """
    original = ca.CRITERIOS[CRITERIO_V_MAX_CONCRETO]
    monkeypatch.setitem(
        ca.CRITERIOS, CRITERIO_V_MAX_CONCRETO,
        original.__class__(**{**original.__dict__, "valor": 4.5}))
    with pytest.raises(CriterioPendienteError):
        v3_velocidad_maxima(material=tmc, resultado=_resultado(V=2.0))


def test_v3_bajo_el_rango_lo_sigue_atrapando_v2_si_toca(concreto):
    """
    La contraparte que evita que el fix abra un agujero: por debajo de 0.25
    m/s el conducto sigue rechazandose, pero por V2 y con SU numeral, que es
    donde la norma pone el piso de autolimpieza.
    """
    lento = _resultado(V=0.10)
    assert v3_velocidad_maxima(material=concreto, resultado=lento).cumple
    assert not v2_velocidad_minima(resultado=lento).cumple


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


def test_v5_con_el_criterio_declarado_no_revienta_con_assertionerror():
    """
    Regresion: con 'remanso_derecho_via' DECLARADO, V5 lanzaba un
    `AssertionError` desnudo. Al no descender de ErrorProyecto, `cli._etapa`
    no lo capturaba y la corrida entera abortaba. Ahora sale DatoFaltanteError
    -- que si es ErrorProyecto -- y la CLI lo anota como bloqueo del punto.
    """
    punto = _punto()
    ca.establecer_valor_dinamico("remanso_derecho_via", "cumple")
    try:
        with pytest.raises(DatoFaltanteError) as excinfo:
            v5_remanso(punto=punto, resultado=_resultado())
    finally:
        ca.quitar_valor_dinamico("remanso_derecho_via")

    assert isinstance(excinfo.value, ErrorProyecto)
    assert excinfo.value.campo == "ancho_derecho_via_m"
    assert excinfo.value.id_punto == "A-01"


def test_v7_lanza_pendiente_por_falta_de_peso_especifico_del_relleno(concreto):
    """
    Con 'peso_especifico_relleno_kn_m3' vacio, V7 se detiene ahi -- antes de
    llegar a 'factores_carga_aashto' -- porque el termino EV se arma antes
    que los factores de carga en `v7_flotacion`.
    """
    punto = _punto()
    with pytest.raises(CriterioPendienteError) as excinfo:
        v7_flotacion(punto=punto, material=concreto, D=0.90,
                     resultado=_resultado())
    assert excinfo.value.clave == "peso_especifico_relleno_kn_m3"


TABLA_GAMMA_DEMO = {"Resistencia I": {"DC": {"min": 0.90, "max": 1.25},
                                      "EV": {"min": 1.00, "max": 1.35},
                                      "WA": {"min": 1.00, "max": 1.00}}}


def test_v7_calcula_completo_en_cuanto_declara_el_peso_del_relleno(
        concreto, monkeypatch):
    """
    'factores_carga_aashto' es [C] (AASHTO LRFD 9a ed.) y ya no se detiene:
    el unico vacio que le queda a V7 es 'peso_especifico_relleno_kn_m3'.
    Declarado ese, V7 calcula completo con los gamma REALES (Resistencia I:
    DC y EV minimos 0.90, WA 1.00) sin tocar nada mas.
    """
    original = ca.CRITERIOS["peso_especifico_relleno_kn_m3"]
    monkeypatch.setitem(
        ca.CRITERIOS, "peso_especifico_relleno_kn_m3",
        original.__class__(**{**original.__dict__, "valor": 18.0}),
    )
    punto = _punto()
    v = v7_flotacion(punto=punto, material=concreto, D=0.90,
                     resultado=_resultado())
    assert v.codigo == "V7"
    assert v.criterio_aplicado == "factores_carga_aashto"
    assert v.valor_obtenido == pytest.approx(0.90 * 17.01, abs=1e-6)
    assert v.valor_admisible == pytest.approx(
        1.00 * 9.81 * (math.pi / 4) * 0.90 ** 2, abs=1e-6)
    assert v.cumple


def test_v7_calcula_completo_con_los_dos_criterios_declarados(concreto,
                                                                monkeypatch):
    """
    cota_terreno=42.10 (= cota de entrada supuesta), D=0.90 -> clave=43.00.
    cota_subrasante=44.05 -> altura_relleno = 1.05 m.
    U  = 9.81 * (pi/4) * 0.90^2 = 6.2417... kN/m
    EV = 18.0 * 0.90 * 1.05 = 17.01 kN/m;  DC = 0 (peso propio omitido)
    estabilizante   = 0.90*0 + 1.00*17.01 = 17.01 kN/m
    desestabilizante = 1.00 * U = 6.2417... kN/m  -> cumple
    """
    for clave, val in (("peso_especifico_relleno_kn_m3", 18.0),
                       ("factores_carga_aashto", TABLA_GAMMA_DEMO)):
        original = ca.CRITERIOS[clave]
        monkeypatch.setitem(
            ca.CRITERIOS, clave,
            original.__class__(**{**original.__dict__, "valor": val}),
        )
    punto = _punto()
    v = v7_flotacion(punto=punto, material=concreto, D=0.90,
                     resultado=_resultado())
    assert v.codigo == "V7"
    assert v.criterio_aplicado == "factores_carga_aashto"
    assert v.valor_obtenido == pytest.approx(1.00 * 17.01, abs=1e-6)
    assert v.valor_admisible == pytest.approx(
        1.00 * 9.81 * (math.pi / 4) * 0.90 ** 2, abs=1e-6)
    assert v.cumple


def test_v7_no_es_un_factor_de_seguridad_global(concreto, monkeypatch):
    """
    El estabilizante y el desestabilizante llevan gamma DISTINTOS y cada uno
    el suyo. Con una tabla en la que gamma_EV_min != gamma_WA, un FS global
    no podria reproducir el resultado: es la prueba de que V7 dejo de serlo.
    """
    for clave, val in (("peso_especifico_relleno_kn_m3", 18.0),
                       ("factores_carga_aashto",
                        {"Resistencia I": {
                            "DC": {"min": 0.90, "max": 1.25},
                            "EV": {"min": 0.90, "max": 1.35},
                            "WA": {"min": 1.00, "max": 1.25}}})):
        original = ca.CRITERIOS[clave]
        monkeypatch.setitem(
            ca.CRITERIOS, clave,
            original.__class__(**{**original.__dict__, "valor": val}),
        )
    v = v7_flotacion(punto=_punto(), material=concreto, D=0.90,
                     resultado=_resultado())
    assert v.valor_obtenido == pytest.approx(0.90 * 17.01, abs=1e-6)
    assert v.valor_admisible == pytest.approx(
        1.25 * 9.81 * (math.pi / 4) * 0.90 ** 2, abs=1e-6)


def test_v8_lanza_pendiente_por_falta_de_TR_y_umbral():
    punto = _punto()
    with pytest.raises(CriterioPendienteError) as excinfo:
        v8_evento_extremo(punto=punto, resultado=_resultado())
    assert excinfo.value.clave == "TR_evento_extremo"


def test_los_criterios_nuevos_estan_declarados_vacios():
    for clave in ("remanso_derecho_via", "peso_especifico_relleno_kn_m3",
                 "TR_evento_extremo"):
        assert clave in ca.criterios_sin_valor()
    # 'factores_carga_aashto' se cerro como [C] (AASHTO LRFD 9a ed.)
    assert "factores_carga_aashto" not in ca.criterios_sin_valor()


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
