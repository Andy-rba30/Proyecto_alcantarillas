"""
tests/test_ve5_m9_ciclopeo.py
=============================
Lote M9 del censo, item 10 (ficha T7C-09 (2) y (3)), cerrado en VE-6: el
cabezal de gravedad en concreto ciclopeo

  * C7: la zapata como VOLADIZO de concreto simple cuando vuela mas que la
    mitad de su peralte (E.060 22.10.2.2): traccion M_u/S <= phi·0,42·
    sqrt(f'c) y cortante V_u <= phi·0,11·sqrt(f'c)·b·h (22-7 y 22-9), con
    phi = 0,5, f'c <= 10 MPa y h - 50 mm (22.10.2.3 y 22.4.8), con las
    cargas de E.060 9.2.5;
  * C8: el cuerpo bajo SISMO, tracciones nulas con las cargas del Evento
    Extremo I sin factorar, en los dos casos de AASHTO 11.6.5.1 (incremento
    del empuje e inercia del cuerpo por encima de la seccion) y, con el
    muro que no cede, la resultante del empuje total no bajo h/2
    (C11.6.5.4), como la pantalla armada.

El muro es el de `CP_T7C_CICLOPEO` (H = 1.30, B = 1.00, zapata 0.30 m: la
punta vuela 0.30 > 0.15 y el talon 0.20 > 0.15), con el fixture `tanteo`
(k_h = k_h0 = 0.25, k_v = 0, regimen de resistencia 'no_cedente_k0' de
archivo, trasdos drenado: sin agua).

La sesion VE-5 dejo este archivo escrito ANTES del codigo con dos dorados
que VE-6 corrigio al escribir el codigo (ver la ficha VE6M9-01): la inercia
del cuerpo no esta a la mitad de su altura sino en el centro de gravedad del
trapecio, y el sismo no suma el 100 % del incremento y de la inercia sino
los dos casos de 11.6.5.1 (el «resultado mas conservador de estos dos
analisis»), los mismos de la fila E2.
"""

import math

import pytest

from src import criterios_adoptados as ca
from src.modelos import CondicionAnalisis, EstadoDeVerificacion
from src.modulos import M9_cabezal as M9
from tests.apoyo.aproximacion import ABS_CERO
from tests.fixtures.casos_patron import CP_T7C_CICLOPEO
from tests.test_t7c_cabezal_armado import _gravedad, tanteo  # noqa: F401

TOL = 1e-6
# Los dorados a mano de abajo llevan seis cifras decimales.
TOL_DORADO = 1e-5
SIS = CondicionAnalisis.SISMICO

# --- el dorado de C7, a mano ------------------------------------------------
# h = 0.30 - 0.05 = 0.25 m; S = 0.25²/6 = 0.0104167 m³/m
# phi·0,42·sqrt(10)·1000 = 664.0783 kPa; phi·0,11·sqrt(10)·1000·0.25 =
# 43.4813 kN/m. Rige en la punta la E.060 (9-6) con el reposo:
# M_u = 7.87279 kN·m/m -> 7.87279 / 0.0104167 / 664.0783 = 1.13810 (> 1),
# V_u = 35.7651 kN/m -> 0.82255.
H_ZAP = 0.30 - 0.05
F_T = 0.5 * 0.42 * math.sqrt(10.0) * 1000
V_R = 0.5 * 0.11 * math.sqrt(10.0) * 1000 * H_ZAP
C7_PUNTA = 1.138101

# --- el dorado de C8 a media altura, a mano ---------------------------------
# z = 0.30 + 1.30/2 = 0.95; por encima, 1.60 - 0.95 = 0.65 m de relleno y
# 0.65 m de cuerpo; t = 0.40, e_c = 0.30, W = 5.3599 (CP_T7C_CICLOPEO).
# y_W = 0.65·(0.40 + 2·0.30)/(3·0.70) = 0.309524 (trapecio)
# k_h·W·y_W = 0.25·5.3599·0.309524 = 0.414754
# M_EH = K_A·cos(delta + beta)·gamma·0.65³/6 = 0.229989 (plano virtual)
# M_LS = K_A·gamma·h_eq·0.65²/2 = 0.689050
# incremento: f = 0.73476 > 2/3 -> resultante entera a 1.17561 m:
#   M_dPAE = 4.56622·(1.17561 - 0.95) = 1.030196
# a h/2 (no cede): (6.431735 + 4.56622)·0.65²/(2·1.60) = 1.452067 > 1.260185
# la sobrecarga viva con gamma_EQ = 0.50 (criterio 'gamma_EQ', como E2;
# dictamen Fable de VE-6): 0.5·0.689050 = 0.344525
# caso 100 % P_AE + 50 % P_IR: M_H = 1.452067 + 0.344525 + 0.5·0.414754
#   = 2.003969;  caso 50 % P_AE (rige el piso: EH 1, incremento 0) + 100 %
#   P_IR: 6.431735·0.132031 + 0.344525 + 0.414754 = 1.608469
# e = (2.003969 - 5.3599·(0.20 - 0.176190))/5.3599 = 0.350074 > t/6
# (antes del dictamen, con la sobrecarga entera: 0.414352)
GAMMA_EQ = 0.50
C8_MEDIA = 0.350074


def _v(a, codigo):
    return next(v for v in a.verificaciones if v.codigo == codigo)


def test_C7_la_punta_y_el_talon_como_voladizos_de_concreto_simple(tanteo):
    """
    El aprovechamiento es el mayor de (M_u/S)/(0,5·0,42·sqrt(10)·1000) y
    V_u/(0,5·0,11·sqrt(10)·1000·0,25), S = 0,25²/6, sobre las solicitaciones
    de la zapata con las dos combinaciones de E.060 y cada juego de empujes
    (el regimen de archivo es 'no_cedente_k0': activo y reposo).
    """
    entorno = _gravedad()
    a = M9.verificar_cabezal_ciclopeo(entorno)
    cargas, datos = M9.cargas_del_cabezal(entorno, CondicionAnalisis.ESTATICO)
    juegos = [cargas, M9.cargas_en_reposo(cargas, datos)]
    for clave in ("punta", "talon"):
        peor = 0.0
        for juego in juegos:
            for combo in M9._combinaciones_e060(juego, entorno.geometria.B):
                z = M9.solicitaciones_de_la_zapata(entorno.geometria, juego,
                                                   combo, datos)
                if z is None:
                    continue
                V, M = z[clave]
                peor = max(peor, abs(M) / (H_ZAP ** 2 / 6) / F_T,
                           abs(V) / V_R)
        c7 = _v(a, f"C7.{clave}.e")
        assert c7.valor_obtenido == pytest.approx(peor, abs=TOL)
        assert c7.paso.umbral.cita_id == "E060.22.5.3#TRACCION"
        assert "E060.22.10.2#CICLOPEO" in c7.paso.citas_textuales
        assert "E060.22.4.8#PERALTE" in c7.paso.citas_textuales
    punta = _v(a, "C7.punta.e")
    assert punta.valor_obtenido == pytest.approx(C7_PUNTA, abs=TOL_DORADO)
    sus = {m.simbolo: m.valor for m in punta.paso.sustitucion}
    assert sus["phi·0,42·sqrt(f'c)"] == pytest.approx(664.078309, abs=TOL_DORADO)
    assert sus["phi·0,11·sqrt(f'c)·b·h"] == pytest.approx(43.481318,
                                                          abs=TOL_DORADO)
    assert sus["h"] == pytest.approx(0.25, abs=ABS_CERO)
    # decide: es la unica verificacion del corte y la flexion de la zapata
    assert punta.estado is EstadoDeVerificacion.NO_CUMPLE
    assert _v(a, "C7.talon.e").estado is EstadoDeVerificacion.CUMPLE
    assert not any("22.10.2.2 manda verificar" in x for x in a.avisos)
    assert any("C7.punta.e" in x and "22.10.2.2" in x for x in a.avisos)


def test_C7_no_aplica_si_el_vuelo_no_pasa_de_la_mitad_del_peralte(tanteo):
    a = M9.verificar_cabezal_ciclopeo(_gravedad(
        espesor_zapata=0.70, cota_coronacion=102.00, ancho_punta=0.30,
        ancho_talon=0.20))
    assert not any(v.codigo.startswith("C7") for v in a.verificaciones)


def test_C7_con_el_regimen_cedente_solo_el_activo(tanteo):
    """Con 'cedente' el reposo no entra: el aprovechamiento no sube."""
    k0 = _v(M9.verificar_cabezal_ciclopeo(_gravedad()), "C7.punta.e")
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 "cedente")
    ced = _v(M9.verificar_cabezal_ciclopeo(_gravedad()), "C7.punta.e")
    assert ced.valor_obtenido <= k0.valor_obtenido + TOL


def test_C8_el_cuerpo_bajo_sismo_lleva_el_incremento_y_la_inercia(tanteo):
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    assert a.sismico
    c3, c8 = _v(a, "C3.cuerpo.e"), _v(a, "C8.media.e")
    sus = {m.simbolo: m.valor for m in c8.paso.sustitucion}
    W = sus["W"]
    assert W == pytest.approx(CP_T7C_CICLOPEO["media"]["W"],
                              abs=CP_T7C_CICLOPEO["tolerancia"])
    y_W = 0.65 * (0.40 + 2 * 0.30) / (3 * 0.70)
    assert sus["y_W"] == pytest.approx(y_W, abs=TOL)
    assert sus["k_h·W·y_W"] == pytest.approx(0.25 * W * y_W, abs=TOL)
    assert sus["M_EH"] == pytest.approx(0.229989, abs=TOL_DORADO)
    assert sus["M_dPAE"] == pytest.approx(1.030196, abs=TOL_DORADO)
    assert sus["M_LS"] == pytest.approx(0.689050, abs=TOL_DORADO)
    assert sus["gamma_EQ"] == pytest.approx(GAMMA_EQ, abs=ABS_CERO)
    assert sus["M_WA"] == pytest.approx(0.0, abs=ABS_CERO)
    assert "MP.2.8.1.1.14.1#EXC" in c8.paso.citas_textuales
    assert c8.valor_obtenido == pytest.approx(C8_MEDIA, abs=TOL_DORADO)
    assert "h/2" in c8.paso.resultado.procedencia
    assert "100% P_AE + 50% P_IR" in c8.paso.resultado.procedencia
    assert c8.valor_obtenido > c3.valor_obtenido
    assert c8.valor_admisible == pytest.approx(0.40 / 6, abs=ABS_CERO)
    assert _v(a, "C8.arranque.e").paso.umbral.cita_id == "E060.22.4.7#JUNTAS"
    assert c8.paso.umbral.cita_id == "E060.22.6.3#TERCIO"
    assert c8.estado is EstadoDeVerificacion.NO_CUMPLE


def test_C8_los_dos_casos_de_11_6_5_1_por_un_camino_independiente(tanteo):
    """
    El mismo C8 recompuesto con los datos del ensamble sismico (que ya tiene
    sus dorados en T-7b) y la aritmetica escrita aqui: diagrama triangular
    del plano virtual, incremento entero a f·h (f > 2/3), resultante a h/2.
    """
    entorno = _gravedad()
    c, d = M9.cargas_del_cabezal(entorno, SIS, k_h=0.25)
    H = {x.codigo: x.H for x in c}
    h, z, t, e_c = d["h"], 0.95, 0.40, 0.30
    arriba = h - z
    W = d["gamma_c"] * (t + e_c) / 2 * 0.65
    x_W = (t ** 2 + t * e_c + e_c ** 2) / (3 * (t + e_c))
    y_W = 0.65 * (t + 2 * e_c) / (3 * (t + e_c))
    M_EH = (d["K_A"] * math.cos(d["inclinacion"]) * d["gamma"] * arriba ** 3
            / 6)
    M_LS = d["K_A"] * d["gamma"] * d["h_eq"] * arriba ** 2 / 2
    assert d["fraccion_brazo"] > 2 / 3
    M_dP = H["EQ.dPAE.h"] * (d["fraccion_brazo"] * h - z)
    excentricidades = []
    for f_eh, f_inc, f_ir in ((1.0, 1.0, 0.5), (1.0, 0.0, 1.0)):
        tierra = max(f_eh * M_EH + f_inc * M_dP,
                     (f_eh * H["EH.h"] + f_inc * H["EQ.dPAE.h"])
                     * arriba ** 2 / (2 * h))
        M_H = tierra + GAMMA_EQ * M_LS + f_ir * d["k_h"] * W * y_W
        excentricidades.append(abs((M_H - W * (t / 2 - x_W)) / W))
    a = M9.verificar_cabezal_ciclopeo(entorno)
    assert _v(a, "C8.media.e").valor_obtenido == pytest.approx(
        max(excentricidades), abs=TOL)
    assert max(excentricidades) == pytest.approx(C8_MEDIA, abs=TOL_DORADO)


def test_C8_con_el_muro_que_cede_no_toma_la_resultante_a_h_medios(tanteo):
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 "cedente")
    c8 = _v(M9.verificar_cabezal_ciclopeo(_gravedad()), "C8.media.e")
    assert "en su posicion" in c8.paso.resultado.procedencia
    assert c8.valor_obtenido < C8_MEDIA


def test_C8_con_la_traccion_admisible_a_media_altura_decide(tanteo):
    # --- VE-7 (lote A, A3; triaje VE-7 de Fable) --- hasta VE-7 la media
    # altura informaba con la traccion admisible de E.060; desde VE-7 decide
    # con cualquier criterio (ficha VE7A-03).
    ca.establecer_valor_dinamico("criterio_traccion_cabezal_ciclopeo",
                                 "traccion_admisible_e060")
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    assert _v(a, "C8.media.e").estado is EstadoDeVerificacion.NO_CUMPLE
    # el arranque es una junta de construccion: decide igual (22.4.7)
    assert _v(a, "C8.arranque.e").estado is EstadoDeVerificacion.NO_CUMPLE


def test_C8_sin_condicion_sismica_evaluable_no_hay_filas_y_se_avisa(
        tanteo, monkeypatch):
    from src.modelos import MetodoNoEvaluableError
    original = M9.cargas_del_cabezal

    def sin_sismo(entorno, condicion, **kw):
        if condicion is SIS:
            raise MetodoNoEvaluableError(
                "sismo", "de prueba", "la condicion sismica de prueba no se "
                "evalua")
        return original(entorno, condicion, **kw)

    monkeypatch.setattr(M9, "cargas_del_cabezal", sin_sismo)
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    assert not a.sismico
    assert not any(v.codigo.startswith("C8") for v in a.verificaciones)
    assert any("NO se verifico bajo sismo" in x for x in a.avisos)


# ===========================================================================
# Dictamen Fable de VE-6 sobre C7 y C8
# ===========================================================================

def test_C8_el_arranque_decide_aunque_no_haya_junta_ni_tracciones_nulas(
        tanteo):
    """
    Con el vaciado monolitico y la traccion admisible de E.060 el arranque
    bajo sismo DECIDE igual, atribuido al criterio de traccion del proyecto
    (E.060 9.2 no combina sismo con empuje: no hay contraste que lo cubra);
    la media altura, desde VE-7, tambien decide.
    """
    ca.establecer_valor_dinamico("criterio_traccion_cabezal_ciclopeo",
                                 "traccion_admisible_e060")
    ca.establecer_valor_dinamico("junta_arranque_cabezal_ciclopeo",
                                 "vaciado_monolitico")
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    arranque = _v(a, "C8.arranque.e")
    assert arranque.estado is EstadoDeVerificacion.NO_CUMPLE
    assert arranque.paso.umbral.criterio_aplicado == \
        "criterio_traccion_cabezal_ciclopeo"
    assert arranque.paso.umbral.cita_id == "E060.22.6.3#TERCIO"
    # --- VE-7 (lote A, A3) --- la media altura tambien decide (VE7A-03).
    assert _v(a, "C8.media.e").estado is EstadoDeVerificacion.NO_CUMPLE


def test_C7_avisa_las_combinaciones_sin_presion_y_decide_con_las_demas(
        tanteo, monkeypatch):
    """
    Si una combinacion de E.060 saca la resultante de la base y otras no, la
    fila sigue decidiendo con las evaluables y el cabezal lo AVISA nombrando
    las descartadas.
    """
    original = M9.solicitaciones_de_la_zapata

    def sin_la_9_7(g, juego, combo, datos):
        if combo.nombre == "E.060 (9-7)":
            return None
        return original(g, juego, combo, datos)

    monkeypatch.setattr(M9, "solicitaciones_de_la_zapata", sin_la_9_7)
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    assert _v(a, "C7.punta.e").estado is EstadoDeVerificacion.NO_CUMPLE
    avisos = [x for x in a.avisos if "C7" in x and "E.060 (9-7)" in x]
    assert avisos and "fuera de la base" in avisos[0]
