"""
tests/test_ve4f_relleno_bajo.py
===============================
VE-4f: la carga viva cuando el relleno queda FUERA del dominio de la rueda
distribuida de AASHTO LRFD 3.6.1.2.6a (menos de 2.0 ft sobre un tubo de
concreto o un marco; 1.0 ft o menos sobre un flexible). Hasta VE-4f la Fase 8
se detenia ahi con `MetodoNoEvaluableError`; lo que la fuente manda, leido en
su pagina (ficha VE4F-01 de docs/decisiones_diferidas.md):

  * el MARCO con menos de 2.0 ft: la franja equivalente de 4.6.2.10.2
    (4.6.2.10.1 y 12.11.2.1), E = 96 + 1.44 S y E_span = L_T + LLDF H, un
    carril con su m; contrastado con el ejemplo resuelto de MnDOT, LRFD
    Bridge Design Manual §12.6 (cajon de 16 ft bajo 1 ft de relleno);
  * el TUBO DE CONCRETO con 1.0 a 2.0 ft: la Eq. 4.6.2.10.2-1 a lo largo del
    tubo, «designed for a depth of 1.0 ft», el B_FLL de la fila «< 2.0 ft» y
    el largo a traves del tubo que declare 'carga_viva_tubo_concreto_somero'
    [A] (sin valor: la fuente no lo dice);
  * el conducto REDONDO bajo la cobertura minima de la Tabla 12.6.6.3-1:
    INCUMPLE (F8.COBERTURA), no es «no evaluable»;
  * lo unico que sigue sin metodo: el tubo de concreto bajo pavimento rigido
    entre 9 y 12 in («more comprehensive methods») y el flexible justo en
    1.0 ft, que la fuente no cubre.

Con el relleno dentro del dominio de antes no cambia nada: lo fijan los
tests de T-5 y VE-3 sin tocar.

TOLERANCIAS, con nombre:
  REL_MNDOT        el ejemplo de MnDOT imprime tres cifras y redondea E a
                   9.92 ft y E_span a 1.98 ft (23.8 in = 1.9833 ft): 0.5 %.
  REL_CONVERSION   la misma ecuacion en kip y pies frente a la de M8 en SI.
"""

import pytest

from src import constantes_normativas as CN
from src.constantes_fisicas import KIP_EN_KN, PIE_EN_METROS
from src.modelos import (CriterioPendienteError, FormaSeccion,
                         MetodoNoEvaluableError,
                         MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL,
                         SeccionCircular, SeccionRectangular, TipoMaterial)
from src import variables_entrada as ve
from src.modulos import M5_verificaciones as M5
from src.modulos import M8_estructural as M8
from src.modulos.M2_material import catalogo, espesor_pared
from tests.apoyo.criterios import declarados
from tests.fixtures.casos_patron import CP_FASE_8_ESTRUCTURAL as CP

KSF_EN_KPA = KIP_EN_KN / PIE_EN_METROS ** 2
KLF_EN_KN_M = KIP_EN_KN / PIE_EN_METROS
REL_MNDOT = 5e-3
REL_CONVERSION = 1e-9
ABS_IM_PCT = 0.05            # el «28.9%» de MnDOT, a una decimal

CRITERIO = "carga_viva_tubo_concreto_somero"
NEUMATICO = "largo_del_neumatico"
E_SPAN = "e_span_a_un_pie"

# Los criterios del cajon que la seccion rectangular pide (los mismos que
# declara tests/test_t5_estructural_conducto.py para su marco).
DECLARACIONES_CAJON = {
    "embocadura_cajon": "cajon_concreto_aletas_30_75",
    "n_manning_cajon": "concreto_afinado",
    "n_celdas_cajon": 1,
    "ke_entrada_cajon": "cajon_aletas_30_75_escuadra",
    "secciones_cajon_normalizadas": ((1.50, 1.20), (2.00, 1.50)),
    "espesor_pared_cajon": 0.15,
}


@pytest.fixture
def a01():
    return CP["punto_A01"]()


def _franja_a_mano(S_ft, DE_ft, l_ft, B_c_ft=None):
    """
    4.6.2.10.2 en su unidad (kip, pies, ksf), INDEPENDIENTE de M8: el eje
    sobre E x l, con el IM de 3.6.2.2 y m = 1.2. Devuelve ({vehiculo: (P_L
    en ksf, W en klf sobre un conducto de ancho B_c)}, IM, E en ft). Con
    B_c, W suma lo que de cada area cae sobre el conducto (los dos ejes del
    tandem, separados 4 ft, no interactuan con menos de 2 ft de relleno).
    """
    E_ft = (96 + 1.44 * S_ft) / 12
    IM = max(0.0, 33 * (1 - 0.125 * DE_ft))
    vehiculos = {}
    for nombre, P_eje, sa in (("camion", 32.0, 14.0), ("tandem", 25.0, 4.0)):
        P_L = P_eje * (1 + IM / 100) * 1.2 / (E_ft * l_ft)
        if B_c_ft is None:
            largo = l_ft
        else:
            largo = min(B_c_ft, l_ft) + max(0.0, min(l_ft, B_c_ft - sa))
        vehiculos[nombre] = (P_L, P_L * largo)
    return vehiculos, IM, E_ft


def _material(tipo):
    return catalogo(tipo)


def _codigos(r):
    return {v.codigo: v for v in r.verificaciones}


# ===========================================================================
# 1. El marco: la franja de 4.6.2.10.2, contra MnDOT §12.6
# ===========================================================================

def test_mndot_12_6_cajon_de_16_pies_bajo_1_pie_de_relleno():
    """
    MnDOT LRFD Bridge Design Manual (sept. 2013), §12.6, pags. 12-51 y
    12-52 (ejemplos_resueltos/cajon/mndot_lrfd_sec12.pdf): cajon
    prefabricado de 16 ft de luz bajo 1 ft de relleno. IM = 28.9 %, E =
    119.04 in, E_span = 23.8 in, y la intensidad del eje: 2.52 (camion) y
    1.97 (tandem), que el ejemplo escribe «klf» y son ksf (kip sobre ft²).
    La carga de carril que el ejemplo suma (0.056) NO entra: la 9.ª ed.
    3.6.1.2.6a manda solo los ejes (y MnDOT dice no haber adoptado la
    revision de 2013 de 3.6.1.2.6).
    """
    cv = M8.carga_viva_enterrada(H=PIE_EN_METROS, D_i=16 * PIE_EN_METROS,
                                 D_E=PIE_EN_METROS,
                                 conducto=M8.CONDUCTO_CAJON)
    assert cv.relleno_somero
    assert cv.IM_pct == pytest.approx(28.9, abs=ABS_IM_PCT)
    assert cv.w_w_m / PIE_EN_METROS * 12 == pytest.approx(119.04, rel=REL_MNDOT)
    assert cv.l_w_m / PIE_EN_METROS * 12 == pytest.approx(23.8, rel=REL_MNDOT)
    por = {c[0]: c for c in cv.candidatos}
    assert por["camion"][4] / KSF_EN_KPA == pytest.approx(2.52, rel=REL_MNDOT)
    assert por["tandem"][4] / KSF_EN_KPA == pytest.approx(1.97, rel=REL_MNDOT)
    assert cv.vehiculo == M8.VEHICULO_CAMION
    assert cv.paso.formula_cita_id == "AASHTO_LRFD_9.4.6.2.10.2#FRANJA"


@pytest.mark.parametrize("H_rel", (0.05, 0.30, 0.40))
def test_el_marco_con_menos_de_2_pies_da_su_demanda(a01, H_rel):
    """
    Hasta VE-4f el marco con menos de 2.0 ft hasta la rasante se detenia
    con «metodo no evaluable»; hoy su demanda lleva la presion de la franja
    (el camion gobierna: 32 kip sobre la misma area que los 25 del tandem).
    """
    H_tot = H_rel + CP["e_paquete"]
    assert H_tot < 2 * PIE_EN_METROS
    with declarados(DECLARACIONES_CAJON):
        marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                         forma=FormaSeccion.RECTANGULAR)
        sec = SeccionRectangular(B=2.00, H=1.50)
        d = M8.demanda_marco(punto=a01, material=marco, seccion=sec,
                             altura_relleno=H_rel)
        r = M8.verificar_conducto(punto=a01, material=marco, seccion=sec,
                                  altura_relleno=H_rel)
    l_ft = (10 + 1.15 * H_tot / PIE_EN_METROS * 12) / 12
    a_mano, _IM, _E = _franja_a_mano(2.00 / PIE_EN_METROS,
                                     H_rel / PIE_EN_METROS, l_ft)
    assert d.w_viva_kPa == pytest.approx(a_mano["camion"][0] * KSF_EN_KPA,
                                         rel=REL_CONVERSION)
    assert r.verificaciones == () and r.demanda_marco == d
    (p_ll,) = [p for p in d.pasos if p.codigo == "F8.LL"]
    assert "AASHTO_LRFD_9.4.6.2.10.1" in p_ll.citas_textuales
    assert "AASHTO_LRFD_9.12.11.2.1#SOMERO" in p_ll.citas_textuales


def test_el_marco_desde_2_pies_sigue_con_la_rueda_distribuida(a01):
    with declarados(DECLARACIONES_CAJON):
        marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                         forma=FormaSeccion.RECTANGULAR)
        d = M8.demanda_marco(punto=a01, material=marco,
                             seccion=SeccionRectangular(B=2.00, H=1.50),
                             altura_relleno=1.00)
    (p_ll,) = [p for p in d.pasos if p.codigo == "F8.LL"]
    assert p_ll.formula_cita_id == "AASHTO_LRFD_9.3.6.1.2.6b#PL"
    # El dorado de T-5 (tests/test_t5_estructural_conducto.py::MARCO_A_MANO).
    assert d.w_viva_kPa == pytest.approx(34.250, rel=CP["tolerancia_rel"])


# ===========================================================================
# 2. El tubo de concreto con 1.0 a 2.0 ft
# ===========================================================================

def test_el_tubo_de_concreto_somero_pide_el_criterio_que_la_fuente_no_fija(a01):
    """
    Sin el largo a traves del tubo, la Fase 8 no lo inventa. Desde VE-7
    (B8) el criterio tiene valor de archivo; la propiedad se fija vaciandolo.
    """
    from tests.apoyo.criterios import sin_valor
    mat = _material(TipoMaterial.CONCRETO_REFORZADO)
    with sin_valor(CRITERIO), pytest.raises(CriterioPendienteError) as exc:
        M8.verificar_conducto(punto=a01, material=mat,
                              seccion=SeccionCircular(0.90),
                              altura_relleno=0.40)
    assert CRITERIO in str(exc.value)


def test_el_criterio_es_un_A_de_perfil_con_sus_dos_lecturas():
    # Sin valor hasta VE-7; desde VE-7 (lote B, B8, ficha VE7B-05) el de
    # archivo es el largo del neumatico, la cota superior.
    from src import criterios_adoptados as ca
    c = ca.CRITERIOS[CRITERIO]
    assert c.valor == NEUMATICO and c.etiqueta == "A"
    assert c.nivel == ca.NIVEL_PERFIL
    assert set(c.sensibilidad) == {NEUMATICO, E_SPAN}
    assert "M8_estructural" in ve.variable(CRITERIO).consumido_por


@pytest.mark.parametrize("lectura", (NEUMATICO, E_SPAN))
def test_el_tubo_de_concreto_somero_tiene_clase(a01, lectura):
    """
    D = 0.90 m (B_c = 1.10 m < 4 ft: un solo eje cabe, y el camion
    gobierna) con 0.40 m de relleno y 0.15 de paquete (0.55 m = 1.80 ft
    hasta la rasante): E sobre la luz interior, IM a la profundidad de
    diseño de 1.0 ft (la cubierta de tierra, 0.40 m, es mayor), B_FLL de la
    fila «< 2.0 ft» (30 in o mas: 2.2). El camion carga entero sobre el
    tubo con las dos lecturas.
    """
    D = 0.90
    mat = _material(TipoMaterial.CONCRETO_REFORZADO)
    B_c = SeccionCircular(D).ancho_exterior(espesor_pared(mat, D))
    with declarados({CRITERIO: lectura}):
        r = M8.verificar_conducto(punto=a01, material=mat,
                                  seccion=SeccionCircular(D),
                                  altura_relleno=0.40)
    cods = _codigos(r)
    assert cods["F8.COBERTURA"].cumple
    v = cods[M8.CODIGO_CLASE]
    assert v.cumple in (True, False) and r.seleccion
    sust = {m.simbolo: m.valor for m in v.paso.sustitucion}
    l_ft = (10 if lectura == NEUMATICO else 10 + 1.15 * 12) / 12
    a_mano, IM, _E = _franja_a_mano(D / PIE_EN_METROS, 1.0, l_ft,
                                    B_c / PIE_EN_METROS)
    W_L = max(w for _p, w in a_mano.values()) * KLF_EN_KN_M
    assert IM == pytest.approx(28.875, rel=REL_CONVERSION)
    assert sust["W_L"] == pytest.approx(W_L, rel=REL_CONVERSION)
    assert sust["W_L"] == pytest.approx(
        CN.EJE_CAMION_HL93_KN * 1.28875 * 1.2
        / (CN.FRANJA_CAJON_BASE_M + CN.FRANJA_CAJON_PENDIENTE_SI * D),
        rel=REL_CONVERSION)
    assert sust["B_FLL"] == pytest.approx(2.2, rel=REL_CONVERSION)
    (p_ll,) = [p for p in r.pasos if p.codigo == "F8.LL"]
    assert "AASHTO_LRFD_9.3.6.1.2.6a#UN_PIE" in p_ll.citas_textuales
    # La D-load se rehace con lo que el paso imprime.
    D_req = ((sust["W_E"] + sust["W_F"]) / sust["B_FE"]
             + sust["W_L"] / sust["B_FLL"]) * 1000 / sust["S_i"]
    assert v.valor_obtenido == pytest.approx(D_req, rel=REL_CONVERSION)


def test_las_dos_lecturas_solo_difieren_con_el_tandem_en_su_banda(a01):
    """
    D = 1.20 m (B_c = 1.45 m, entre s_a = 1.22 y s_a + E_span = 1.82): con
    el largo del neumatico el segundo eje del tandem cae casi entero sobre
    el tubo, con el de E_span solo en parte; los dos dan mas que el camion.
    """
    D = 1.20
    mat = _material(TipoMaterial.CONCRETO_REFORZADO)
    B_c = SeccionCircular(D).ancho_exterior(espesor_pared(mat, D))
    W = {}
    for lectura, l_ft in ((NEUMATICO, 10 / 12), (E_SPAN, (10 + 1.15 * 12) / 12)):
        with declarados({CRITERIO: lectura}):
            r = M8.verificar_conducto(punto=a01, material=mat,
                                      seccion=SeccionCircular(D),
                                      altura_relleno=0.40)
        (p_ll,) = [p for p in r.pasos if p.codigo == "F8.LL"]
        assert "gobierna el tandem" in p_ll.que
        sust = {m.simbolo: m.valor
                for m in _codigos(r)[M8.CODIGO_CLASE].paso.sustitucion}
        a_mano, _IM, _E = _franja_a_mano(D / PIE_EN_METROS, 1.0, l_ft,
                                         B_c / PIE_EN_METROS)
        assert sust["W_L"] == pytest.approx(a_mano["tandem"][1] * KLF_EN_KN_M,
                                            rel=REL_CONVERSION)
        W[lectura] = sust["W_L"]
    assert W[NEUMATICO] > W[E_SPAN]


# ===========================================================================
# 3. Bajo la cobertura minima: incumplimiento, no «no evaluable»
# ===========================================================================

@pytest.mark.parametrize("tipo, minimo", (
        (TipoMaterial.CONCRETO_REFORZADO, 0.3048),   # max(Bc/8, 12 in), flexible
        (TipoMaterial.TMC, 0.3048),                  # S/8 >= 12 in
        (TipoMaterial.HDPE, 0.6096)))                # ID/2 >= 24 in, pavimentado
def test_bajo_la_cobertura_minima_el_conducto_incumple(a01, tipo, minimo):
    mat = _material(tipo)
    r = M8.verificar_conducto(punto=a01, material=mat,
                              seccion=SeccionCircular(0.90),
                              altura_relleno=0.10)
    (v,) = r.verificaciones
    assert v.codigo == "F8.COBERTURA" and not v.cumple
    assert "12.6.6.3" in v.numeral
    assert v.valor_obtenido == pytest.approx(0.25, rel=REL_CONVERSION)
    assert v.valor_admisible == pytest.approx(minimo, rel=REL_CONVERSION)
    assert v.criterio_aplicado == "cobertura_minima_aashto"
    assert r.seleccion == ""
    # Es lo que la Fase 5 suma a su tabla.
    assert M8.verificaciones_estructurales(
        punto=a01, material=mat, seccion=SeccionCircular(0.90),
        altura_relleno=0.10) == r.verificaciones


def test_bajo_pavimento_rigido_entre_9_y_12_in_sigue_sin_metodo(a01):
    """«Round culverts with less than 1.0 ft of fill shall be analyzed with
    more comprehensive methods»: con la cobertura de 9 in del pavimento
    rigido cumplida, eso es lo unico que el programa no implementa."""
    mat = _material(TipoMaterial.CONCRETO_REFORZADO)
    with declarados({"condicion_pavimento": "rigido"}):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            M8.verificar_conducto(punto=a01, material=mat,
                                  seccion=SeccionCircular(0.90),
                                  altura_relleno=0.12)
    assert str(exc.value).startswith(MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL)
    assert "more comprehensive" in str(exc.value)


def test_el_flexible_justo_en_1_pie_sigue_sin_metodo(a01):
    """El metodo vale con MAS de 1.0 ft y la cobertura del TMC pide 12 in o
    mas: justo en 1.0 ft la fuente no da metodo."""
    mat = _material(TipoMaterial.TMC)
    with pytest.raises(MetodoNoEvaluableError):
        M8.verificar_conducto(punto=a01, material=mat,
                              seccion=SeccionCircular(0.90),
                              altura_relleno=PIE_EN_METROS - CP["e_paquete"])


def _somero(a01, mat, D, H_rel, e_paq):
    """A-01 con la subrasante bajada hasta dejar `H_rel` sobre la clave del
    tubo de diametro D, y la rasante `e_paq` encima."""
    from dataclasses import replace
    actual = M5.altura_relleno_sobre_clave(punto=a01, material=mat,
                                           seccion=SeccionCircular(D))
    sub = a01.cota_subrasante - (actual - H_rel)
    return replace(a01, cota_subrasante=sub, cota_rasante=sub + e_paq)


def test_en_la_fase_5_el_tubo_somero_tiene_veredicto(a01):
    """
    Desde la Fase 5, la entrada del pipeline. La rasante 5 cm sobre la
    subrasante de A-01 deja al tubo de concreto de 1.35 m con 0.46 + 0.05 m
    hasta la rasante (1.68 ft): hasta VE-4f «metodo no evaluable»; hoy pide
    el criterio y, declarado, da la clase.
    """
    from tests.apoyo.criterios import sin_valor
    mat = _material(TipoMaterial.CONCRETO_REFORZADO)
    somero = _somero(a01, mat, 1.35, 0.46, 0.05)
    # Sin valor (lo tuvo hasta VE-7, B8) la Fase 5 se detiene en el criterio
    with sin_valor(CRITERIO), pytest.raises(CriterioPendienteError):
        M5.fase_8_estructural(punto=somero, material=mat,
                              seccion=SeccionCircular(1.35))
    with declarados({CRITERIO: NEUMATICO}):
        vs = M5.fase_8_estructural(punto=somero, material=mat,
                                   seccion=SeccionCircular(1.35))
    assert [v.codigo for v in vs] == ["F8.COBERTURA", M8.CODIGO_CLASE]
    assert vs[0].cumple


def test_en_la_fase_5_el_escalon_sin_cobertura_se_rechaza(a01):
    """Con 0.10 + 0.05 m hasta la rasante el tubo no alcanza los 12 in de
    la Tabla 12.6.6.3-1: F8.COBERTURA incumple y el escalon se rechaza."""
    mat = _material(TipoMaterial.CONCRETO_REFORZADO)
    somero = _somero(a01, mat, 1.35, 0.10, 0.05)
    vs = M5.fase_8_estructural(punto=somero, material=mat,
                               seccion=SeccionCircular(1.35))
    assert [v.codigo for v in vs] == ["F8.COBERTURA"]
    assert not vs[0].cumple


def test_el_dominio_la_cobertura_y_la_lectura_tienen_su_puerta(a01):
    """Las tres funciones publicas de VE-4f: el dominio de la rueda
    distribuida, la cobertura de la Tabla 12.6.6.3-1 y la lectura del
    criterio, que sin valor se detiene."""
    con = _material(TipoMaterial.CONCRETO_REFORZADO)
    tmc = _material(TipoMaterial.TMC)
    pie = PIE_EN_METROS
    assert M8.bajo_el_dominio_de_la_rueda_distribuida(material=con,
                                                      H_total=1.5 * pie)
    assert not M8.bajo_el_dominio_de_la_rueda_distribuida(material=con,
                                                          H_total=2 * pie)
    assert M8.bajo_el_dominio_de_la_rueda_distribuida(material=tmc,
                                                      H_total=pie)
    assert not M8.bajo_el_dominio_de_la_rueda_distribuida(material=tmc,
                                                          H_total=1.1 * pie)
    v = M8.verificar_cobertura(punto=a01, material=con,
                               seccion=SeccionCircular(0.90),
                               altura_relleno=0.40)
    assert v.cumple and v.codigo == M8.CODIGO_COBERTURA
    from tests.apoyo.criterios import sin_valor
    with sin_valor(CRITERIO), pytest.raises(CriterioPendienteError):
        M8.lectura_del_tubo_de_concreto_somero()
    assert M8.lectura_del_tubo_de_concreto_somero() == NEUMATICO  # VE-7, B8
    with declarados({CRITERIO: E_SPAN}):
        assert M8.lectura_del_tubo_de_concreto_somero() == E_SPAN
