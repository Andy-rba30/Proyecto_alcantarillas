"""
tests/test_t5_estructural_conducto.py
=====================================
La aceptacion de T-5 de la cadena T: la Fase 8 REAL del conducto
(INF-3.3.5; el INFORME lo numera 3.3.5 y la cadena lo llama «5.1.5 Fase 8 no
verifica nada», ficha T0-04).

Lo que fija, en el orden del prompt:

  1. la carga de tierra y la carga viva HL-93 a traves del relleno (AASHTO
     LRFD 3.6.1.2.6 con el HL-93, la presencia multiple y el IM de
     componentes enterrados del Manual de Puentes), con la altura REAL de
     relleno (subrasante menos clave) mas el paquete estructural;
  2. la clase del tubo de concreto por D-load (metodo indirecto de
     12.10.4.3), contra la Clase II de M 170M, y el relleno maximo;
  3. el calibre del TMC por 12.7.2 (empuje, area, pandeo, costura, factor de
     flexibilidad) con la progresion de plancha y el minimo de la Tabla
     507-01 del EG-2013, y el contraste ASD de ASTM A796 contra el
     expediente de referencia «VARIOS»;
  4. el HDPE por 12.12 (empuje, pandeo y deflexion) con el perfil minimo de
     la Tabla A12-11 y M 294;
  5. el marco: solo la DEMANDA, con el diseño del portico diferido;
  6. la mina retirada (`AssertionError("inalcanzable")` de M8) y lo que la
     Fase 8 sigue sin verificar.

LOS DORADOS SE CALCULARON A MANO en unidades inglesas, con la pagina de cada
numero: `tests/fixtures/casos_patron.py::CP_FASE_8_ESTRUCTURAL`. Ademas, la
carga viva se recalcula aqui con una implementacion INDEPENDIENTE en kip y
pies (`_hl93_a_mano`), que es como la escribe la fuente.

ESTOS TESTS NO SE ESCRIBIERON EN ROJO ANTES DEL CODIGO: se midieron despues
contra un arbol exportado de `7fb7926` (la base de T-5), y lo que cada uno
hace alli esta dicho en el informe de la sesion. Los que valen antes y
despues son guardias.
"""

import ast
import math
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from conftest import CLAVE_ESPESOR_PARED
from src import constantes_normativas as CN
from src import criterios_adoptados as ca
from src import servicio
from src.constantes_fisicas import KCF_EN_KN_M3, KIP_EN_KN, PIE_EN_METROS
from src.modelos import (CriterioPendienteError, DatoFaltanteError,
                         DatoInvalidoError, EstadoDeVerificacion, FormaSeccion,
                         MetodoNoEvaluableError,
                         MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL,
                         SeccionCircular, SeccionRectangular, TipoMaterial)
from src.modulos import M5_verificaciones as M5
from src.modulos import M8_estructural as M8
from src.modulos.M2_material import catalogo
from src.normativa import fuentes, registro
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import con_valor, declarados, sin_valor
from tests.fixtures.casos_patron import CP_FASE_8_ESTRUCTURAL as CP

RAIZ = Path(__file__).resolve().parent.parent
KSF_EN_KPA = KIP_EN_KN / PIE_EN_METROS ** 2

# LAS TOLERANCIAS DE ESTE ARCHIVO, con nombre y con su clase de igualdad:
#   REL               el dorado calculado a mano en unidades inglesas: lo
#                     declara el caso patron (la constante del agua, 62.4
#                     pcf frente a 9.81 kN/m3, difiere un 0.08 %).
#   REL_CONVERSION    la MISMA ecuacion escrita en kip y pies frente a la de
#                     M8 en SI: solo el redondeo de la aritmetica.
#   REL_LECTURA       un numero leido de una cifra impresa con tres o cuatro
#                     significativas (el 0.354 de VARIOS, el 0.41667 de una
#                     fraccion, los 18.85 kN/m3 de 0.120 kcf).
#   ABS_ALTURA_M      el relleno sobre la clave del dorado, escrito con tres
#                     decimales: 1 mm.
#   ABS_LIMITE_FF_MM  «unos 1.39 m» de la ficha T4-08: 2 mm sobre 1386.
#   ABS_PANDEO_MPA    el f_c del contraste se dio a una decimal: 0.2 MPa.
REL = CP["tolerancia_rel"]
REL_CONVERSION = 1e-9
REL_LECTURA = 1e-4
ABS_ALTURA_M = 1e-3
ABS_LIMITE_FF_MM = 2.0
ABS_PANDEO_MPA = 0.2


@pytest.fixture
def del_expediente():
    """Retira el espesor sintetico de `conftest`: queda el del archivo."""
    ca.quitar_valor_dinamico(CLAVE_ESPESOR_PARED)
    yield


@pytest.fixture
def a01():
    return CP["punto_A01"]()


def _material(tipo):
    return catalogo(tipo)


def _altura(punto, material, D):
    return M5.altura_relleno_sobre_clave(punto=punto, material=material,
                                        seccion=SeccionCircular(D))


def _hl93_a_mano(H_ft, Di_ft, LLDF):
    """
    3.6.1.2.6b en su unidad: kip, pies y ksf. Implementacion INDEPENDIENTE
    de M8 (no comparte una linea), para contrastar la conversion a SI.
    """
    wt, lt, sw = 20 / 12, 10 / 12, 6.0
    IM = max(0.0, 33 * (1 - 0.125 * H_ft))
    if H_ft > 8.0 and H_ft > Di_ft:       # 3.6.1.2.6a: se puede despreciar
        return (0.0, 0.0, IM)
    mejor = None
    for P_eje, sa in ((32.0, 14.0), (25.0, 4.0)):
        if H_ft < (sw - wt - 0.06 * Di_ft) / LLDF:
            ww, P = wt + LLDF * H_ft + 0.06 * Di_ft, P_eje / 2
        else:
            ww, P = wt + sw + LLDF * H_ft + 0.06 * Di_ft, P_eje
        if H_ft < (sa - lt) / LLDF:
            lw = lt + LLDF * H_ft
        else:
            lw, P = lt + sa + LLDF * H_ft, 2 * P
        PL = P * (1 + IM / 100) * 1.2 / (lw * ww)
        if mejor is None or PL > mejor[0]:
            mejor = (PL, lw, IM)
    return mejor


# ===========================================================================
# 1. La carga viva HL-93 a traves del relleno
# ===========================================================================

def test_la_carga_viva_sobre_el_concreto_de_A01_es_la_calculada_a_mano():
    g = CP["LL_concreto"]
    cv = M8.carga_viva_enterrada(H=CP["H_relleno"]["concreto_reforzado"]
                                 + CP["e_paquete"], D_i=CP["D"],
                                 conducto=M8.CONDUCTO_TUBO_CONCRETO)
    assert cv.LLDF == pytest.approx(g["LLDF"], rel=REL)
    assert cv.IM_pct == pytest.approx(g["IM_pct"], rel=REL)
    assert cv.l_w_m == pytest.approx(g["l_w_m"], rel=REL)
    assert cv.P_L_kPa == pytest.approx(g["P_L_kPa"], rel=REL)
    assert cv.vehiculo == g["vehiculo"] and not cv.despreciada
    assert cv.paso.fundamento_id == "F8.CARGA_VIVA"
    assert cv.paso.formula_cita_id == "AASHTO_LRFD_9.3.6.1.2.6b#PL"


@pytest.mark.parametrize("H_m", (0.62, 0.80, 1.10, 1.50, 2.20, 2.50))
@pytest.mark.parametrize("D_i", (0.90, 1.50, 2.40))
@pytest.mark.parametrize("conducto", (M8.CONDUCTO_TUBO_CONCRETO,
                                      M8.CONDUCTO_FLEXIBLE))
def test_la_carga_viva_en_si_es_la_de_la_fuente_en_kip_y_pies(H_m, D_i, conducto):
    """
    Malla de profundidades que cruza las dos interacciones (ruedas y ejes)
    y el cambio de vehiculo que gobierna: la conversion a SI que M8 hace una
    sola vez no puede mover el numero.
    """
    LLDF = M8._lldf(D_i, conducto)
    PL_ksf, lw_ft, IM = _hl93_a_mano(H_m / PIE_EN_METROS, D_i / PIE_EN_METROS,
                                     LLDF)
    cv = M8.carga_viva_enterrada(H=H_m, D_i=D_i, conducto=conducto)
    assert cv.P_L_kPa == pytest.approx(PL_ksf * KSF_EN_KPA, rel=REL_CONVERSION)
    assert cv.l_w_m == pytest.approx(lw_ft * PIE_EN_METROS, rel=REL_CONVERSION)
    assert cv.IM_pct == pytest.approx(IM, rel=REL_CONVERSION)


def test_el_IM_en_si_es_el_de_pies_del_manual():
    for D_E in (0.0, 0.5, 1.0, 2.0, 2.4384, 3.0):
        assert M8.incremento_dinamico_enterrado(D_E) == pytest.approx(
            33 * max(0.0, 1 - 0.125 * D_E / PIE_EN_METROS), rel=REL_CONVERSION)
    assert M8.incremento_dinamico_enterrado(10.0) == pytest.approx(
        0.0, abs=ABS_CERO)


def test_el_HL93_es_el_del_manual_en_su_unidad_primaria():
    assert CN.EJE_CAMION_HL93_KN == pytest.approx(32.0 * KIP_EN_KN, rel=REL_CONVERSION)
    assert CN.EJE_TANDEM_HL93_KN == pytest.approx(25.0 * KIP_EN_KN, rel=REL_CONVERSION)
    assert CN.SEPARACION_EJES_CAMION_MIN_M == pytest.approx(
        14 * PIE_EN_METROS, rel=REL_TRANSPORTE)
    assert CN.SEPARACION_EJES_TANDEM_M == pytest.approx(4 * PIE_EN_METROS,
                                                        rel=REL_TRANSPORTE)
    assert CN.PRESENCIA_MULTIPLE_UN_CARRIL == pytest.approx(1.20,
                                                            rel=REL_TRANSPORTE)
    # El parentesis redondeado del Manual (14.55 t) NO es el valor usado.
    assert CN.EJE_CAMION_HL93_KN != pytest.approx(14.55 * 9.80665, rel=REL_LECTURA)


def test_fuera_del_dominio_del_metodo_la_carga_viva_no_es_evaluable():
    """
    Concreto y marco: desde 2.0 ft; flexible: MAS de 1.0 ft (3.6.1.2.6a).
    Por debajo la fuente manda otro metodo, que no esta implementado.
    """
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M8.carga_viva_enterrada(H=0.60, D_i=0.90,
                                conducto=M8.CONDUCTO_TUBO_CONCRETO)
    assert str(exc.value).startswith(MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL)
    M8.carga_viva_enterrada(H=2 * PIE_EN_METROS, D_i=0.90,
                            conducto=M8.CONDUCTO_CAJON)
    with pytest.raises(MetodoNoEvaluableError):
        M8.carga_viva_enterrada(H=PIE_EN_METROS, D_i=0.90,
                                conducto=M8.CONDUCTO_FLEXIBLE)
    M8.carga_viva_enterrada(H=PIE_EN_METROS + 0.01, D_i=0.90,
                            conducto=M8.CONDUCTO_FLEXIBLE)


def test_con_mas_de_8_ft_que_superan_la_luz_la_carga_viva_se_desprecia():
    cv = M8.carga_viva_enterrada(H=2.50, D_i=0.90,
                                 conducto=M8.CONDUCTO_FLEXIBLE)
    assert cv.despreciada and cv.P_L_kPa == pytest.approx(0.0, abs=ABS_CERO)
    assert "AASHTO_LRFD_9.3.6.1.2.6a#DESPRECIABLE" in cv.paso.citas_textuales
    # Mas de 8 ft pero NO mas que la luz: se sigue aplicando.
    cv = M8.carga_viva_enterrada(H=2.50, D_i=3.00,
                                 conducto=M8.CONDUCTO_CAJON)
    assert not cv.despreciada and cv.P_L_kPa > 0


@pytest.mark.parametrize("H", (0.0, -1.0, float("nan"), float("inf")))
def test_una_profundidad_sin_sentido_es_dato_invalido(H):
    with pytest.raises(DatoInvalidoError):
        M8.carga_viva_enterrada(H=H, D_i=0.90, conducto=M8.CONDUCTO_FLEXIBLE)


def test_el_relleno_carga_con_el_mayor_peso_y_el_paquete_con_el_del_manual():
    """
    En V7 el relleno estabiliza y se adopta el extremo bajo (17.0); en la
    Fase 8 empuja, y gana la Tabla 2.4.2.1-1 del Manual (0.120 kcf).
    """
    gamma_s, gamma_p, procedencia = M8.pesos_especificos_de_carga(
        piso_tubo_concreto=True)
    assert ca.CRITERIOS["peso_especifico_relleno_kn_m3"].valor == pytest.approx(
        17.0, rel=REL_TRANSPORTE)
    assert gamma_s == pytest.approx(0.120 * KCF_EN_KN_M3, rel=REL_CONVERSION)
    assert gamma_s == pytest.approx(18.8505, rel=REL_LECTURA)
    assert gamma_p == pytest.approx(CN.PESO_PAQUETE_ESTRUCTURAL_KN_M3,
                                    rel=REL_TRANSPORTE)
    assert "Tabla 2.4.2.1-1" in procedencia
    with declarados({"peso_especifico_relleno_kn_m3": 20.0}):
        assert M8.pesos_especificos_de_carga(
            piso_tubo_concreto=False)[0] == pytest.approx(
                20.0, rel=REL_TRANSPORTE)


def test_el_paquete_negativo_es_dato_invalido(a01):
    malo = replace(a01, cota_rasante=a01.cota_subrasante - 0.10)
    with pytest.raises(DatoInvalidoError) as exc:
        M8.espesor_del_paquete(malo)
    assert exc.value.campo == "cota_rasante"
    assert M8.espesor_del_paquete(a01) == pytest.approx(CP["e_paquete"],
                                                        abs=ABS_ALTURA_M)


# ===========================================================================
# 2. El tubo de concreto: clase por D-load (12.10.4.3)
# ===========================================================================

def test_el_concreto_de_A01_es_clase_II_con_la_D_load_calculada_a_mano(
        del_expediente, a01):
    g = CP["concreto"]
    mat = _material(TipoMaterial.CONCRETO_REFORZADO)
    H = _altura(a01, mat, CP["D"])
    assert H == pytest.approx(CP["H_relleno"]["concreto_reforzado"],
                              abs=ABS_ALTURA_M)
    r = M8.verificar_concreto(punto=a01, material=mat,
                              seccion=SeccionCircular(CP["D"]), altura_relleno=H)
    (v,) = r.verificaciones
    assert v.codigo == M8.CODIGO_CLASE and v.cumple
    assert v.valor_obtenido == pytest.approx(g["D_req_N_m_mm"], rel=REL)
    assert v.valor_admisible == pytest.approx(g["D_clase"], rel=REL_TRANSPORTE)
    assert r.seleccion == f"Clase {g['clase']}"
    sust = {m.simbolo: m.valor for m in v.paso.sustitucion}
    for clave, simbolo in (("W_E_kN_m", "W_E"), ("W_F_kN_m", "W_F"),
                           ("W_L_kN_m", "W_L"), ("B_FE", "B_FE"),
                           ("B_FLL", "B_FLL")):
        assert sust[simbolo] == pytest.approx(g[clave], rel=REL), simbolo
    assert r.relleno_maximo_m is not None and r.relleno_maximo_m > H


def test_el_relleno_maximo_del_concreto_es_donde_la_clase_se_agota(
        del_expediente, a01):
    """El relleno maximo es un CRUCE: con 1 cm mas, la Clase II no alcanza."""
    mat = _material(TipoMaterial.CONCRETO_REFORZADO)
    sec = SeccionCircular(CP["D"])
    H = _altura(a01, mat, CP["D"])
    r = M8.verificar_concreto(punto=a01, material=mat, seccion=sec,
                              altura_relleno=H)
    H_max = r.relleno_maximo_m
    justo = M8.verificar_concreto(punto=a01, material=mat, seccion=sec,
                                  altura_relleno=H_max - 0.001)
    assert justo.verificaciones[0].cumple
    with pytest.raises(DatoFaltanteError) as exc:
        M8.verificar_concreto(punto=a01, material=mat, seccion=sec,
                              altura_relleno=H_max + 0.01)
    assert exc.value.campo == "clases_producto_por_relleno"
    assert "M 170M" in str(exc.value)


def test_el_tipo_1_multiplica_por_1_10_y_el_tipo_de_instalacion_decide(
        del_expediente, a01):
    mat = _material(TipoMaterial.CONCRETO_REFORZADO)
    sec = SeccionCircular(CP["D"])
    H = _altura(a01, mat, CP["D"])
    obtenidos, formulas = {}, {}
    for tipo in ("tipo_1", "tipo_2", "tipo_3"):
        with declarados({"instalacion_estandar_concreto": tipo}):
            r = M8.verificar_concreto(punto=a01, material=mat, seccion=sec,
                                      altura_relleno=H)
            obtenidos[tipo] = r.verificaciones[0].valor_obtenido
            formulas[tipo] = r.verificaciones[0].paso.formula
    # Tipo 3 (la instalacion mas debil que EG-2013 admite) pide mas que el 2,
    # y el 1 menos que el 2 aun con su factor de 1.10.
    assert obtenidos["tipo_3"] > obtenidos["tipo_2"] > obtenidos["tipo_1"]
    assert "x 1.10" in formulas["tipo_1"]
    assert "x 1.10" not in formulas["tipo_3"]


def test_la_instalacion_por_defecto_es_la_mas_desfavorable_que_admite_EG2013():
    c = ca.CRITERIOS["instalacion_estandar_concreto"]
    assert c.valor == "tipo_3" and c.etiqueta == "A"
    assert c.sensibilidad == ("tipo_1", "tipo_2", "tipo_3")
    assert CN.VAF_INSTALACION_ESTANDAR == pytest.approx(
        {"tipo_1": 1.35, "tipo_2": 1.40, "tipo_3": 1.40, "tipo_4": 1.45},
        rel=REL_TRANSPORTE)


def test_clases_producto_por_relleno_solo_trae_lo_que_el_ejemplar_deja_leer():
    c = ca.CRITERIOS["clases_producto_por_relleno"]
    assert set(c.valor) == {"concreto_reforzado"}
    assert c.valor["concreto_reforzado"] == pytest.approx({"II": 50.0},
                                                          rel=REL_TRANSPORTE)
    assert c.nivel == ca.NIVEL_PERFIL and c.etiqueta == "C"
    with con_valor("clases_producto_por_relleno", {"concreto_reforzado": {}},
                   motivo="un ejemplar sin ninguna clase legible"):
        assert M8._clases_transcritas() == {}


# ===========================================================================
# 3. La tuberia metalica corrugada: 12.7.2 y el contraste ASD
# ===========================================================================

def test_el_tmc_de_A01_empuje_area_y_pandeo_calculados_a_mano(
        del_expediente, a01):
    g = CP["tmc"]
    mat = _material(TipoMaterial.TMC)
    H = _altura(a01, mat, CP["D"])
    assert H == pytest.approx(CP["H_relleno"]["tmc"], abs=ABS_ALTURA_M)
    r = M8.verificar_tmc(punto=a01, material=mat,
                         seccion=SeccionCircular(CP["D"]), altura_relleno=H)
    area, costura, ff = r.verificaciones
    assert (area.codigo, costura.codigo, ff.codigo) == (
        M8.CODIGO_AREA, M8.CODIGO_COSTURA, M8.CODIGO_FF)
    assert r.seleccion == g["plancha"]
    assert area.valor_obtenido == pytest.approx(g["A_req_mm2_mm"], rel=REL)
    sust = {m.simbolo: m.valor for m in area.paso.sustitucion}
    assert sust["T_L"] == pytest.approx(g["T_L_kN_m"], rel=REL)
    assert sust["f_cr"] == pytest.approx(g["f_cr_MPa"], rel=REL)
    # La costura remachada simple de la Tabla 5: 266 kN/m por phi_s = 0.67.
    assert costura.valor_admisible == pytest.approx(0.67 * 266.0,
                                                    rel=REL_TRANSPORTE)
    assert all(v.cumple for v in r.verificaciones)


def test_la_tabla_507_01_del_eg2013_sube_la_plancha_y_el_resultado_lo_avisa(
        del_expediente, a01):
    """
    1.20 m: el EG-2013 exige 2.50 mm; la primera plancha de 68 x 13 que lo
    alcanza es la de 2.77, mas gruesa que la adoptada (2.01): la envolvente
    geometrica de 7.A y V7 se armo con la adoptada, y se avisa.
    """
    assert M8.espesor_minimo_tmc_eg2013(0.90) == pytest.approx(
        0.0020, rel=REL_TRANSPORTE)
    assert M8.espesor_minimo_tmc_eg2013(1.05) == pytest.approx(
        0.0025, rel=REL_TRANSPORTE)
    assert M8.espesor_minimo_tmc_eg2013(1.80) == pytest.approx(
        0.0033, rel=REL_TRANSPORTE)
    assert M8.espesor_minimo_tmc_eg2013(1.95) is None
    mat = _material(TipoMaterial.TMC)
    H = _altura(a01, mat, 1.20)
    r = M8.verificar_tmc(punto=a01, material=mat, seccion=SeccionCircular(1.20),
                         altura_relleno=H)
    assert r.seleccion == "68x13/2.77"
    assert r.avisos and "corrugacion_y_espesor_tmc" in r.avisos[0]
    assert "Tabla 507-01" in r.verificaciones[0].paso.nota_del_proyecto


def test_la_plancha_adoptada_falla_el_factor_de_flexibilidad_desde_1_39_m():
    """
    Ficha T4-08: la 68 x 13 / 2.01 cumple FF hasta unos 1.386 m. Medido aqui
    con el limite de la Tabla 12.5.6.1-1 (43 in/kip).
    """
    I = CN.TMC_PLANCHA_CORRUGADA["68x13/2.01"]["I_mm4_mm"]
    S_lim = math.sqrt(CN.FF_LIMITE_ACERO_MM_N["68x13"] * CN.ACERO_TMC_EM_MPA * I)
    assert S_lim == pytest.approx(1386.0, abs=ABS_LIMITE_FF_MM)
    assert CN.FF_LIMITE_ACERO_MM_N["68x13"] == pytest.approx(
        43 * 25.4 / (KIP_EN_KN * 1000), rel=REL_CONVERSION)


def test_la_costura_empernada_no_tiene_tabla_y_se_detiene_pidiendola(
        del_expediente, a01):
    mat = _material(TipoMaterial.TMC)
    H = _altura(a01, mat, CP["D"])
    with declarados({"fabricacion_tmc": "anular_empernada"}):
        with pytest.raises(DatoFaltanteError) as exc:
            M8.verificar_tmc(punto=a01, material=mat,
                             seccion=SeccionCircular(CP["D"]), altura_relleno=H)
    assert exc.value.campo == "resistencia_costura_empernada_tmc"


def test_la_helicoidal_no_verifica_costura_y_lo_dice(del_expediente, a01):
    mat = _material(TipoMaterial.TMC)
    H = _altura(a01, mat, CP["D"])
    with declarados({"fabricacion_tmc": "helicoidal"}):
        r = M8.verificar_tmc(punto=a01, material=mat,
                             seccion=SeccionCircular(CP["D"]), altura_relleno=H)
    costura = r.verificaciones[1]
    assert costura.estado is EstadoDeVerificacion.NO_APLICA
    assert "8.1.3.1" in costura.motivo_no_aplica


def test_la_remachada_simple_no_ofrece_las_planchas_que_la_tabla_no_fabrica():
    """La 1.32 de 68 x 13 lleva «. . .» en las cuatro columnas de costura."""
    assert CN.COSTURA_REMACHADA_TMC_KN_M["68x13/1.32"] == {"simple": None,
                                                         "doble": None}
    assert CN.COSTURA_REMACHADA_TMC_KN_M["68x13/2.01"] == pytest.approx(
        {"simple": 266.0, "doble": 435.0}, rel=REL_TRANSPORTE)
    assert CN.COSTURA_REMACHADA_TMC_KN_M["68x13/2.77"]["simple"] == \
        pytest.approx(341.0, rel=REL_TRANSPORTE)


def test_bajo_un_terraplen_alto_la_remachada_simple_no_desarrolla_el_empuje(
        a01):
    """
    El caso de la auditoria de T-4 (rasante 52.20, TMC de 1.95 m con ~8.5 m
    de relleno): con costura remachada SIMPLE ninguna plancha de 68 x 13
    desarrolla el empuje; con la DOBLE, si. Es la razon de que el test H1 de
    T-4 declare la doble para seguir midiendo lo que media.
    """
    mat = _material(TipoMaterial.TMC)
    alto = replace(a01, cota_rasante=52.20, cota_subrasante=52.05)
    H = _altura(alto, mat, 1.95)
    r = M8.verificar_tmc(punto=alto, material=mat,
                         seccion=SeccionCircular(1.95), altura_relleno=H)
    assert not r.verificaciones[1].cumple and r.seleccion == ""
    with declarados({"fabricacion_tmc": "anular_remachada_doble"}):
        r = M8.verificar_tmc(punto=alto, material=mat,
                             seccion=SeccionCircular(1.95), altura_relleno=H)
    assert all(v.cumple for v in r.verificaciones)


def test_el_contraste_asd_reproduce_el_expediente_VARIOS():
    """
    ASTM A796 num. 8 (tensiones admisibles): el expediente «VARIOS» publica
    C = 40.7 kN/m y A = 0.354 mm2/mm para D = 0.90 m con DL 4.5 + LL 86 kPa
    (H20). Se reproduce con f_y = 230 MPa, que es su redondeo; con el 225
    MPa de A796-13 la misma cuenta da 0.362 (+2.2 %), que es la diferencia
    DECLARADA. El pandeo no gobierna: f_c = 289 MPa > f_y.
    """
    g = CP["varios_asd"]
    T, f, A = M8.area_requerida_asd_a796(S_m=g["S_m"], P_kPa=g["P_kPa"],
                                         r_mm=g["r_mm"], f_y=230.0)
    assert T == pytest.approx(g["T_kN_m"], rel=REL_CONVERSION)
    assert f == pytest.approx(230.0, rel=REL_TRANSPORTE)
    assert A == pytest.approx(g["A_fy230"], rel=REL_LECTURA)
    assert round(A, 3) == g["A_publicado"]
    _, f225, A225 = M8.area_requerida_asd_a796(S_m=g["S_m"], P_kPa=g["P_kPa"],
                                               r_mm=g["r_mm"])
    assert f225 == pytest.approx(CN.A796_FY_MPA, rel=REL_TRANSPORTE)
    assert A225 == pytest.approx(g["A_fy225"], rel=REL_LECTURA)
    assert A225 / g["A_publicado"] - 1 == pytest.approx(0.0226, rel=REL)
    fc = M8.tension_critica_de_pandeo(S_mm=900.0, r_mm=g["r_mm"],
                                      E=CN.A796_E_MPA, F_u=CN.A796_FU_MPA,
                                      k=CN.A796_K_SUELO)
    assert fc == pytest.approx(289.2, abs=ABS_PANDEO_MPA) and fc > 230.0


def test_la_H20_de_A796_frente_al_HL93_a_la_misma_profundidad():
    """
    Lo que el expediente VARIOS usa (la H20 de A796 6.2.2.1: 86.2 kPa a 1 ft,
    con impacto) no es comparable con el HL-93 que rige aqui: a 1 ft el
    metodo de 3.6.1.2.6 ni siquiera aplica a un flexible (pide MAS de 1 ft),
    y apenas por encima da mas del doble. Se mide y se deja dicho.
    """
    with pytest.raises(MetodoNoEvaluableError):
        M8.carga_viva_enterrada(H=0.30, D_i=0.90, conducto=M8.CONDUCTO_FLEXIBLE)
    cv = M8.carga_viva_enterrada(H=0.31, D_i=0.90, conducto=M8.CONDUCTO_FLEXIBLE)
    assert cv.P_L_kPa > 2 * 86.2


# ===========================================================================
# 4. El HDPE: 12.12 con el perfil minimo de la Tabla A12-11
# ===========================================================================

def test_el_hdpe_de_A01_empuje_calculado_a_mano_con_la_suma_por_duracion(
        del_expediente, a01):
    g = CP["hdpe"]
    mat = _material(TipoMaterial.HDPE)
    H = _altura(a01, mat, CP["D"])
    assert H == pytest.approx(CP["H_relleno"]["hdpe"], abs=ABS_ALTURA_M)
    r = M8.verificar_hdpe(punto=a01, material=mat,
                          seccion=SeccionCircular(CP["D"]),
                          altura_relleno=CP["H_relleno"]["hdpe"])
    empuje, pandeo, deflexion = r.verificaciones
    assert (empuje.codigo, pandeo.codigo, deflexion.codigo) == (
        M8.CODIGO_EMPUJE, M8.CODIGO_PANDEO, M8.CODIGO_DEFLEXION)
    assert empuje.valor_obtenido == pytest.approx(g["eps_uc"], rel=REL)
    assert empuje.valor_admisible == pytest.approx(g["eps_lim"],
                                                   rel=REL_TRANSPORTE)
    assert empuje.cumple is g["cumple_empuje"]
    assert r.seleccion == "" and r.relleno_maximo_m is None
    assert "AASHTO_LRFD_9.12.12.3.10.1c#EP" in empuje.paso.citas_textuales


def test_el_area_efectiva_sale_del_minimo_de_M294_y_del_tiempo():
    """0.5 A_g F_u,ini K_t / F_u: 0.45 A_g inicial, 0.4167 A_g a 75 años."""
    fu_ini, _ = CN.PE_M294_PROPIEDADES_KSI["inicial"]
    fu_75, _ = CN.PE_M294_PROPIEDADES_KSI["75"]
    fraccion = CN.M294_FRACCION_CAPACIDAD_COMPRESION
    assert fraccion * fu_ini * CN.KT_PE["inicial"] / fu_ini == pytest.approx(
        0.45, rel=REL_TRANSPORTE)
    assert fraccion * fu_ini * CN.KT_PE["75"] / fu_75 == pytest.approx(
        0.41667, rel=REL_LECTURA)
    perfil = CN.PE_M294_PERFIL_MINIMO[900]
    assert perfil["A_mm2_mm"] == pytest.approx(4.5 * 25.4 ** 2 / 304.8,
                                               rel=REL_CONVERSION)
    assert perfil["od_max_m"] == pytest.approx(42.5 * 0.0254,
                                               rel=REL_CONVERSION)
    assert CN.PE_M294_PERFIL_MINIMO[1050]["nota_largo_plazo"]
    assert not perfil["nota_largo_plazo"]


def test_con_relleno_de_arena_el_hdpe_mejora_y_la_eleccion_lo_decide(
        del_expediente, a01):
    mat = _material(TipoMaterial.HDPE)
    sec = SeccionCircular(CP["D"])
    H = CP["H_relleno"]["hdpe"]
    arcilla = M8.verificar_hdpe(punto=a01, material=mat, seccion=sec,
                                altura_relleno=H)
    with declarados({"relleno_estructural_hdpe": "Sn-95"}):
        arena = M8.verificar_hdpe(punto=a01, material=mat, seccion=sec,
                                  altura_relleno=H)
    assert arena.verificaciones[2].valor_obtenido < \
        arcilla.verificaciones[2].valor_obtenido
    assert arena.verificaciones[0].valor_obtenido < \
        arcilla.verificaciones[0].valor_obtenido


def test_un_hdpe_que_la_tabla_a12_11_no_trae_es_dato_faltante(a01):
    mat = _material(TipoMaterial.HDPE)
    with pytest.raises(DatoFaltanteError) as exc:
        M8.verificar_hdpe(punto=a01, material=mat,
                          seccion=SeccionCircular(1.35), altura_relleno=0.5)
    assert exc.value.campo == "perfil_hdpe"


# ===========================================================================
# 5. El marco: demanda, y el diseño del portico diferido
# ===========================================================================

DECLARACIONES_CAJON = {
    "embocadura_cajon": "cajon_concreto_aletas_30_75",
    "n_manning_cajon": "concreto_afinado",
    "n_celdas_cajon": 1,
    "ke_entrada_cajon": "cajon_aletas_30_75_escuadra",
    "secciones_cajon_normalizadas": ((1.50, 1.20), (2.00, 1.50)),
    "espesor_pared_cajon": 0.15,
}


def test_el_marco_da_la_demanda_de_la_losa_y_difiere_el_portico(a01):
    """
    F_e = 1 + 0.20 H/B_c <= 1.15 (12.11.2.2.1); w_u = eta (1.35 w_EV + 1.75
    P_L); M_ref = w_u L^2/8. Calculado a mano sobre 2.00 x 1.50 con t = 0.15
    y 1.00 m de relleno mas 0.15 de paquete.
    """
    with declarados(DECLARACIONES_CAJON):
        marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                         forma=FormaSeccion.RECTANGULAR)
        sec = SeccionRectangular(B=2.00, H=1.50)
        d = M8.demanda_marco(punto=a01, material=marco, seccion=sec,
                             altura_relleno=1.00)
        r = M8.verificar_conducto(punto=a01, material=marco, seccion=sec,
                                  altura_relleno=1.00)
        assert M8.verificaciones_estructurales(
            punto=a01, material=marco, seccion=sec, altura_relleno=1.00) == ()
    assert d.F_e == pytest.approx(1 + 0.20 * 1.15 / 2.30, rel=REL_CONVERSION)
    gamma_s = CN.PESO_SUELO_COMPACTADO_KN_M3
    w_EV = d.F_e * (gamma_s * 1.00 + CN.PESO_PAQUETE_ESTRUCTURAL_KN_M3 * 0.15)
    assert d.w_tierra_kPa == pytest.approx(w_EV, rel=REL_CONVERSION)
    PL_ksf, _, _ = _hl93_a_mano(1.15 / PIE_EN_METROS, 2.00 / PIE_EN_METROS, 1.15)
    assert d.w_viva_kPa == pytest.approx(PL_ksf * KSF_EN_KPA, rel=REL_CONVERSION)
    w_u = 1.05 * (1.35 * w_EV + 1.75 * d.w_viva_kPa)
    assert d.w_u_kPa == pytest.approx(w_u, rel=REL_CONVERSION)
    assert d.M_u_referencia_kNm_m == pytest.approx(w_u * 2.15 ** 2 / 8, rel=REL_CONVERSION)
    assert r.verificaciones == () and r.demanda_marco == d
    assert M8.DIFERIDO_MARCO in r.diferido
    assert "diferido al expediente" in d.pasos[-1].que
    assert "kN·m/m" in d.pasos[-1].que


def test_el_factor_del_marco_tiene_su_tope_de_relleno_compactado(a01):
    with declarados(DECLARACIONES_CAJON):
        marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                         forma=FormaSeccion.RECTANGULAR)
        d = M8.demanda_marco(punto=a01, material=marco,
                             seccion=SeccionRectangular(B=1.50, H=1.20),
                             altura_relleno=4.00)
    assert d.F_e == pytest.approx(CN.FE_CAJON_MAX_COMPACTADO, rel=REL_TRANSPORTE)


# ===========================================================================
# 6. La Fase 8 en el pipeline: una verificacion por material, y la mina
# ===========================================================================

@pytest.mark.parametrize("tipo", (TipoMaterial.CONCRETO_REFORZADO,
                                  TipoMaterial.TMC, TipoMaterial.HDPE))
def test_la_fase_8_produce_al_menos_una_verificacion_con_veredicto_por_material(
        del_expediente, a01, tipo):
    """El criterio de aceptacion del prompt, sobre los tres candidatos."""
    mat = _material(tipo)
    filas = M5.fase_8_estructural(punto=a01, material=mat,
                                  seccion=SeccionCircular(CP["D"]))
    assert filas
    for v in filas:
        assert v.cumple in (True, False)
        assert v.codigo in M8.CODIGOS_FASE_8
        assert v.numeral
        assert v.paso is not None or v.estado is EstadoDeVerificacion.NO_APLICA


def test_m8_ya_no_tiene_ninguna_mina():
    """Ningun `raise AssertionError` en M8 (la de `seleccionar_clase_calibre`)."""
    arbol = ast.parse((RAIZ / "src/modulos/M8_estructural.py").read_text(
        encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Raise) and nodo.exc is not None:
            f = nodo.exc.func if isinstance(nodo.exc, ast.Call) else nodo.exc
            nombre = getattr(f, "id", getattr(f, "attr", None))
            assert nombre != "AssertionError", nodo.lineno


def test_la_corrida_de_perfil_verifica_la_clase_y_no_mueve_ningun_diametro():
    """
    PARADA (c) del encargo, medida: con la Fase 8 real, A-01 y A-02 siguen
    en concreto de 0.90 m y dimensionados; la clase es la II y el F8.CLASE
    entra a la tabla de la Fase 5 detras de V9.
    """
    externos = cli.cargar_datos_externos(
        RAIZ / "tests/linea_base_familia_c/entradas_ampliadas.json",
        {"luz_m": 2.75})
    informe = cli.correr(RAIZ / "tests/ejemplo_puntos.csv", externos,
                         alcance=cli.ALCANCE_PERFIL)
    por_id = {p.punto.id: p for p in informe.puntos}
    for id_ in ("A-01", "A-02"):
        p = por_id[id_]
        assert p.dimensionado, id_
        assert p.resultado.material.tipo is TipoMaterial.CONCRETO_REFORZADO
        assert p.resultado.seccion.etiqueta() == "Ø 0.90 m"
        codigos = [v.codigo for v in p.resultado.verificaciones]
        assert codigos[-1] == M8.CODIGO_CLASE and codigos[-2] == "V9", id_
        assert p.estructural is not None and p.estructural.seleccion == "Clase II"
        assert p.cama_apoyo is None
    datos = cli.informe_json(informe)
    a01 = next(p for p in datos["puntos"] if p["id"] == "A-01")
    assert a01["estructural"]["seleccion"] == "Clase II"
    assert a01["estructural"]["relleno_maximo_m"] > 1.0
    assert any(v["codigo"] == "F8.CLASE" for v in a01["verificaciones"])


def _condicion_que_guarda_la_fase_8(ruta: Path, funcion: str):
    """El `if` del AST de `funcion` cuyo cuerpo llama a `fase_8_estructural`."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    (fn,) = [n for n in ast.walk(arbol)
             if isinstance(n, ast.FunctionDef) and n.name == funcion]
    for nodo in ast.walk(fn):
        if isinstance(nodo, ast.If) and any(
                isinstance(c, ast.Call) and getattr(c.func, "attr", getattr(
                    c.func, "id", None)) == "fase_8_estructural"
                for c in ast.walk(nodo)):
            return nodo.test
    return None


@pytest.mark.parametrize("ruta, funcion", (
    ("src/modulos/M5_verificaciones.py", "verificar"),
    ("src/servicio.py", "_verificador_perfil")))
def test_un_incumplimiento_hidraulico_no_lo_tapa_la_fase_8(ruta, funcion):
    """
    La Fase 8 corre SOLO si todo lo anterior cumple: un escalon que ya
    incumple se rechaza igual, y un dato estructural que falta no puede
    reemplazar el incumplimiento real en el motivo. Se mide en el AST: la
    llamada esta guardada por `all(v.cumple for v in ...)`.
    """
    prueba = _condicion_que_guarda_la_fase_8(RAIZ / ruta, funcion)
    assert isinstance(prueba, ast.Call) and getattr(prueba.func, "id", "") == "all"
    (gen,) = prueba.args
    assert isinstance(gen, ast.GeneratorExp)
    assert isinstance(gen.elt, ast.Attribute) and gen.elt.attr == "cumple"


def test_con_relleno_somero_la_fase_8_no_es_evaluable(a01):
    """
    Un tubo de concreto con menos de 2 ft hasta la rasante: la carga viva
    no es evaluable con 3.6.1.2.6, y la Fase 8 lo dice con
    `MetodoNoEvaluableError` (no con un incumplimiento: subir de diametro
    solo reduce el relleno). Que a nivel de perfil se difiera y a nivel de
    expediente bloquee lo decide `servicio._verificador_perfil`, con la
    misma tabla que V1/V2 (`ALCANCES_QUE_DIFIEREN_METODO_NO_EVALUABLE`).
    """
    somero = replace(a01, cota_rasante=a01.cota_subrasante + 0.05)
    mat = _material(TipoMaterial.CONCRETO_REFORZADO)
    with pytest.raises(MetodoNoEvaluableError):
        M5.fase_8_estructural(punto=somero, material=mat,
                              seccion=SeccionCircular(1.35))


def test_el_diferimiento_de_perfil_ya_no_es_la_fase_8_entera():
    informe = servicio.InformePunto(punto=CP["punto_A01"]())
    servicio._diferir_fase_8(informe)
    (b,) = informe.bloqueos
    assert b.diferido_por_alcance
    assert "cama de apoyo y demanda del marco" in b.etapa
    assert "F8.*" in b.mensaje


def test_los_cinco_criterios_nuevos_son_de_perfil_con_ventana():
    for clave in ("instalacion_estandar_concreto", "fabricacion_tmc",
                  "eta_importancia_operativa_conducto",
                  "relleno_estructural_hdpe", "parametros_diseno_hdpe"):
        c = ca.CRITERIOS[clave]
        assert c.nivel == ca.NIVEL_PERFIL and c.etiqueta == "A", clave
        assert c.valor is not None and c.sensibilidad, clave
    eta = ca.CRITERIOS["eta_importancia_operativa_conducto"]
    assert eta.sensibilidad == pytest.approx((0.95, 1.05), rel=REL_TRANSPORTE)
    assert eta.valor == pytest.approx(1.05, rel=REL_TRANSPORTE)


def test_una_eta_fuera_de_la_ventana_no_entra_por_la_puerta():
    try:
        with pytest.raises(ValueError):
            ca.establecer_valor_dinamico("eta_importancia_operativa_conducto",
                                         1.20)
    finally:
        ca.quitar_valor_dinamico("eta_importancia_operativa_conducto")


def test_ningun_numero_de_lrfd_se_combina_con_un_fs_de_a796():
    """
    El marco de verificacion separado: el FS de A796 (SF = 2) solo vive en
    el contraste ASD, y ninguna verificacion F8.* lo usa. Medido en el AST:
    `A796_SF_AREA` aparece en el procedimiento ASD y una sola vez en
    `verificar_tmc`, dentro del paso del contraste.
    """
    arbol = ast.parse((RAIZ / "src/modulos/M8_estructural.py").read_text(
        encoding="utf-8"))
    usos = {}
    for fn in (n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)):
        cuantos = sum(1 for x in ast.walk(fn)
                      if isinstance(x, ast.Attribute) and x.attr == "A796_SF_AREA")
        if cuantos:
            usos[fn.name] = cuantos
    assert set(usos) <= {"area_requerida_asd_a796", "verificar_tmc"}
    assert usos.get("verificar_tmc", 0) == 1


# ===========================================================================
# Los numeros, en su pagina
# ===========================================================================

@pytest.mark.pdf
@pytest.mark.parametrize("fuente_id, pagina_pdf, fragmentos", [
    # HL-93 y el IM de componentes enterrados (Manual de Puentes).
    ("MP", 105, ("32.0-kips", "25.0 kip")),
    ("MP", 110, ("0.125",)),
    # Pesos especificos del relleno y del paquete.
    ("MP", 103, ("0.120", "0.140")),
    # La distribucion de la carga viva (AASHTO 3.6.1.2.6).
    ("AASHTO_LRFD_9", 81, ("1.15", "1.75")),
    # Resistencias del acero del TMC y limites del factor de flexibilidad.
    ("AASHTO_LRFD_9", 1745, ("45.0", "33.0", "29,000")),
    ("AASHTO_LRFD_9", 1651, ("43", "33")),
    # El tubo de concreto: VAF por tipo y factores de cama.
    ("AASHTO_LRFD_9", 1691, ("1.35", "1.40", "1.45")),
    ("AASHTO_LRFD_9", 1703, ("4.4", "3.2", "2.5", "1.7")),
    ("AASHTO_LRFD_9", 1704, ("3.2", "2.4", "2.2")),
    # El polietileno: propiedades, M_s y K_t.
    ("AASHTO_LRFD_9", 1715, ("5.0", "4.1", "110", "0.90")),
    ("AASHTO_LRFD_9", 1723, ("0.9", "0.3", "0.25")),
    # El marco y el espesor minimo de la plancha del EG-2013.
    ("AASHTO_LRFD_9", 1707, ("1.15", "1.40")),
    ("EG2013", 978, ("0.90 36 2.00", "1.20 48 2.50", "1.80 72 3.30")),
])
def test_los_numeros_de_T5_estan_en_la_pagina_que_se_cita(
        fuente_id, pagina_pdf, fragmentos):
    from src.normativa.extraccion import texto_de_pagina
    ruta = fuentes.ruta_pdf(fuentes.FUENTES[fuente_id])
    if not ruta.exists():
        pytest.skip(f"el PDF de {fuente_id} no esta enlazado (NORMAS_DIR)")
    texto = " ".join(texto_de_pagina(ruta, pagina_pdf).split())
    for fragmento in fragmentos:
        assert fragmento in texto, (fuente_id, pagina_pdf, fragmento)
