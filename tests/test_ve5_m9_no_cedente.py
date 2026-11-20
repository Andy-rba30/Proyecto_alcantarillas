"""
tests/test_ve5_m9_no_cedente.py
===============================
VE-5, lote M9, item 1 (ficha T7B-14): la estabilidad del cabezal con el
muro que NO cede ('regimen_cabezal' = 'no_cedente'). Hasta VE-5 declararlo
detenia el ensamble con `MetodoNoEvaluableError`; desde VE-5 el ensamble
calcula las presiones de AASHTO LRFD 11.6.5.4 y C11.6.5.4:

  * estatica: empuje en REPOSO, K0 = 1 - sen(phi) (3.11.5.2-1), sin friccion
    muro-relleno, con el factor de carga de la fila «En reposo» (1.35/0.90,
    Tabla 3.4.1-2). K0 es de terreno horizontal: si el empuje activo con la
    superficie real da MAS componente horizontal, rige el activo (la misma
    regla que el armado aplica por seccion, ficha T7C-02);
  * sismica: k_h = 1.0·k_h0 aunque 'factor_muro_eleccion' reduzca el de la
    cadena (11.6.5.4, «shall be increased to 1.0kh0»), y la resultante del
    estatico mas el sismico no bajo h/2 (C11.6.5.4);
  * el empuje sismico total del muro que no cede lo declara
    'empuje_sismico_muro_que_no_cede' [A]: el reposo mas el incremento de
    Mononobe-Okabe / cuña (archivo, lado seguro) o el mayor del reposo y del
    total pseudoestatico.

Los dorados son ARITMETICA ESCRITA sobre el muro de tanteo de T-7b
(`CP_T7B_ESTABILIDAD`: phi = 30, gamma = 18, h = 2.40 m, relleno horizontal,
seco). Escritos ANTES del codigo: en rojo contra la base de VE-5.
"""

import math
from types import SimpleNamespace

import pytest

from src import criterios_adoptados as ca
from src.modelos import CondicionAnalisis, DatoInvalidoError
from src.modulos import M9_cabezal as M9
from tests.apoyo.criterios import declarados
from tests.fixtures.casos_patron import CP_T7B_ESTABILIDAD as CP
from tests.test_t7b_cabezal_estabilidad import _declarar_sitio, _entorno

EST = CondicionAnalisis.ESTATICO
SIS = CondicionAnalisis.SISMICO
TOL = CP["tolerancia"]
CLAVE = "empuje_sismico_muro_que_no_cede"

# --- el dorado, a mano -------------------------------------------------------
# K0 = 1 - sen 30 = 0.5; h = 2.40; gamma = 18; seco (freatico a 5 m).
K0 = 0.5
P0 = K0 * 18.0 * 2.40 ** 2 / 2            # 25.92 kN/m, a h/3 = 0.80 m
LS0 = K0 * 18.0 * CP["h_eq"] * 2.40       # 13.16736 kN/m, a 1.20 m
# Resistencia I (minimos), eta = 1: DC 0.90, EV 1.00, EH (reposo) 1.35, LS 1.75
N_MIN = 0.90 * (14.136 + 18.848) + 1.00 * 39.600      # 69.2856 (EH.v = 0)
H_MIN = 1.35 * P0 + 1.75 * LS0                        # 58.03488
# Sismo: k_h0 = 0.25 (la cadena reduce a 0.125). P_AE de la cuña con k_h0 =
# 26.3503 (dorado de T-7b); P_A = 0.29726·18·2.88 = 15.4104; incremento
# 10.9399, horizontal 10.2740 (dorado de T-7b, dP_h).
DP_H = CP["sismico"]["dP_h"]
P_AE_H = CP["sismico"]["P_AE"] * math.cos(math.radians(CP["delta"]))  # 24.7454


@pytest.fixture
def no_cede(monkeypatch):
    """El muro de tanteo de T-7b, declarado NO cedente, con la cadena que
    REDUCE k_h (k_h0 = 0.25, k_h = 0.125): el muro que no cede no la hereda."""
    ca.establecer_valor_dinamico("eta_importancia_operativa_conducto", 1.0)
    ca.establecer_valor_dinamico("phi_relleno_trasdos", CP["phi_relleno"])
    ca.establecer_valor_dinamico("peso_especifico_relleno_kn_m3",
                                 CP["gamma_relleno"])
    ca.establecer_valor_dinamico("drenaje_trasdos", "drenado")
    ca.establecer_valor_dinamico("regimen_cabezal", "no_cedente")
    _declarar_sitio()
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h0=0.25, k_h=0.125, k_v=0.0))
    return _entorno()


def _c(e, codigo):
    return next(c for c in e.cargas if c.codigo == codigo)


def test_el_criterio_del_empuje_sismico_es_un_A_de_expediente_con_ventana():
    c = ca.CRITERIOS[CLAVE]
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_EXPEDIENTE
    assert c.valor == "reposo_mas_incremento"
    assert tuple(c.sensibilidad) == ("reposo_mas_incremento",
                                     "mayor_de_reposo_y_total")
    assert "AASHTO_LRFD_9.11.6.5.4#NO_CEDENTE" in (c.justificacion + c.fuente)


def test_no_cedente_ya_no_detiene_la_estabilidad_y_la_marca(no_cede):
    est = M9.ensamble_estabilidad(no_cede, EST)
    assert est.regimen == "no_cedente"
    assert all(s.coeficiente_de_empuje == "K0" for s in est.solicitaciones)
    assert all(s.K_empuje == pytest.approx(K0, abs=TOL)
               for s in est.solicitaciones)


def test_estatica_con_el_empuje_en_reposo_y_su_factor(no_cede):
    est = M9.ensamble_estabilidad(no_cede, EST)
    assert _c(est, "EH.h").H == pytest.approx(P0, abs=TOL)
    assert _c(est, "EH.h").z == pytest.approx(0.80, abs=TOL)
    assert _c(est, "EH.v").V == pytest.approx(0.0, abs=TOL)
    assert _c(est, "LS.h").H == pytest.approx(LS0, abs=TOL)
    minimos = next(c for c in est.combinaciones
                   if c.nombre == "Resistencia I (minimos)")
    f = dict(minimos.factores)
    assert f["EH.h"] == pytest.approx(1.35, abs=TOL)
    assert minimos.N == pytest.approx(N_MIN, abs=TOL)
    assert minimos.H == pytest.approx(H_MIN, abs=TOL)


def test_sismica_con_k_h0_sin_reduccion_y_reposo_mas_incremento(no_cede):
    sis = M9.ensamble_estabilidad(no_cede, SIS)
    assert sis.k_h == pytest.approx(0.25, abs=TOL)
    assert _c(sis, "EH.h").H == pytest.approx(P0, abs=TOL)
    inc = _c(sis, "EQ.dPAE.h")
    assert inc.H == pytest.approx(DP_H, abs=TOL)
    assert _c(sis, "EQ.dPAE.v").V == pytest.approx(0.0, abs=TOL)
    # resultante del estatico mas el sismico en h/2 = 1.20 m (C11.6.5.4):
    # z = (36.1940·1.20 - 25.92·0.80) / 10.2740 = 2.20915 m
    z = ((P0 + DP_H) * 1.20 - P0 * 0.80) / DP_H
    assert inc.z == pytest.approx(z, abs=TOL)
    assert _c(sis, "EQ.PIR.muro").H == pytest.approx(
        0.25 * (14.136 + 18.848), abs=TOL)


def test_la_otra_lectura_es_el_mayor_de_reposo_y_total(no_cede):
    with declarados({CLAVE: "mayor_de_reposo_y_total"}):
        sis = M9.ensamble_estabilidad(no_cede, SIS)
    # P_AE·cos(delta) = 24.7454 < P0 = 25.92: el reposo cubre el sismo.
    assert P_AE_H < P0
    assert _c(sis, "EQ.dPAE.h").H == pytest.approx(0.0, abs=TOL)
    assert _c(sis, "EH.h").H == pytest.approx(P0, abs=TOL)


def test_con_relleno_empinado_rige_el_activo_si_da_mas(no_cede):
    """
    K0 de 3.11.5.2-1 es de terreno HORIZONTAL. Con la pendiente declarada
    i = 28 grados (formula cerrada) el activo de Coulomb da mas componente
    horizontal que el reposo: rige el activo, con su friccion y SU factor.
    """
    with declarados({"regla_pendiente_relleno_trasdos": "talud_quebrado_2h",
                     "pendiente_relleno_trasdos_i": 28.0}):
        est = M9.ensamble_estabilidad(no_cede, EST)
        K_A = M9.k_a_coulomb(phi_grados=30.0, i_grados=28.0, beta_grados=0.0,
                             delta_grados=CP["delta"])
    incl = math.radians(CP["delta"])
    assert K_A * math.cos(incl) > K0
    P_A = K_A * 18.0 * 2.40 ** 2 / 2
    assert _c(est, "EH.h").H == pytest.approx(P_A * math.cos(incl), abs=TOL)
    assert _c(est, "EH.v").V == pytest.approx(P_A * math.sin(incl), abs=TOL)
    minimos = next(c for c in est.combinaciones
                   if c.nombre == "Resistencia I (minimos)")
    assert dict(minimos.factores)["EH.h"] == pytest.approx(1.50, abs=TOL)


def test_cargas_en_reposo_es_idempotente_sobre_el_muro_que_no_cede(no_cede):
    cargas, datos = M9.cargas_del_cabezal(no_cede, EST)
    otra = M9.cargas_en_reposo(cargas, datos)
    for codigo in ("EH.h", "EH.v", "LS.h"):
        a = next(c for c in cargas if c.codigo == codigo)
        b = next(c for c in otra if c.codigo == codigo)
        assert (a.H, a.V) == pytest.approx((b.H, b.V), abs=TOL)


def test_distribucion_estatica_sigue_rechazada_con_el_muro_que_no_cede(
        no_cede, monkeypatch):
    """Aunque 'factor_muro_eleccion' declare la reduccion (muro que cede para
    la cadena), el regimen del cabezal manda: la distribucion estatica es
    del muro que cede y se rechaza."""
    monkeypatch.setattr(M9.ca, "valor", _con({"factor_muro_eleccion":
                                              M9.FACTOR_MURO_CON_REDUCCION,
                                              "distribucion_incremento_sismico":
                                              "distribucion_estatica"}))
    with pytest.raises(DatoInvalidoError):
        M9.cargas_del_cabezal(no_cede, SIS)


def _con(fijos):
    original = ca.valor

    def valor(clave):
        return fijos[clave] if clave in fijos else original(clave)
    return valor
