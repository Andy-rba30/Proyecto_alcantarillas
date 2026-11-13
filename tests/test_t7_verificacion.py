"""
tests/test_t7_verificacion.py
=============================
Aceptacion de la VERIFICACION DE FORMULAS de los cierres de T-7b y T-7c: los
tres defectos que el verificador dejo (seis de los nueve puntos salieron
conformes y no se tocan).

  PUNTO 3  V8 con el barril «a presion» podia dar MENOS carga que la lamina
           libre con un caudal menor (lado inseguro): `M4.hidraulica_a_
           presion` comparaba la aproximacion de barril lleno sin las dos
           reglas de la pag. 3.24 del HDS-5 que `M4.resolver_control` aplica
           desde E-A; y `M5.v8_evento_extremo` no tenia la guardia HW_ext >=
           HW de diseño.
  PUNTO 9  el cabezal usaba eta = 1.00 IMPLICITO en Resistencia I (AASHTO
           1.3.2.1) junto a un conducto con eta_I = 1.05 declarado.
  PUNTO 7  el piso del espesor de la zapata armada (0.30 + 0.070 = 0.37 m)
           no podia cumplir nunca E.060 15.7 tal como la fila A8 la mide.
  y el matiz de texto del punto 2 (la nota de V5 por cota de afectacion).

LOS DORADOS ESTAN A MANO, con la aritmetica escrita: el del modificador de
carga sobre el muro de tanteo en `tests/fixtures/casos_patron.py`
(`CP_T7V_ETA`), y los de A-01 en el docstring de cada test.

NO SE ESCRIBIO EN ROJO CON `xfail(strict=True)`: el codigo y este archivo se
escribieron en la misma sesion. El rojo se MIDIO copiando este archivo y el
fixture a un arbol exportado de `2b13dc1`, y se declara en la ficha T7V-04
de `docs/decisiones_diferidas.md`.
"""

import math
from types import SimpleNamespace

import pytest

from src import constantes_normativas as cn
from src import criterios_adoptados as ca
from src import modelos
from src import servicio
from src.modelos import (MARCO_ASD, MARCO_LRFD, ControlGobernante,
                         EstadoDeVerificacion, EventoExtremoDelPunto,
                         MetodoNoEvaluableError, SECCION_PANTALLA)
from src.modulos import M0_carga as M0
from src.modulos import M2_material as M2
from src.modulos import M3_hidraulica as M3
from src.modulos import M4_control as M4
from src.modulos import M5_verificaciones as M5
from src.modulos import M9_cabezal as M9
from src.normativa.registro import construir
from tests.apoyo.aproximacion import ABS_CERO
from tests.apoyo.criterios import con_valor
from tests.fixtures.casos_patron import CP_T7B_ESTABILIDAD, CP_T7V_ETA
from tests.test_t7b_cabezal_estabilidad import (CSV_EJEMPLO, _evento,
                                                _llamar_v8, _declarar_v8)
from tests.test_t7c_cabezal_armado import (_correr_de_prueba, _de,
                                           _sin_datos_de_exposicion, tanteo)

__all__ = ["tanteo"]        # el fixture del muro de tanteo de T-7c

EST = modelos.CondicionAnalisis.ESTATICO
SIS = modelos.CondicionAnalisis.SISMICO
CP = CP_T7V_ETA
CPB = CP_T7B_ESTABILIDAD
TOL = CP["tolerancia"]
REL = CP["tolerancia_rel"]
# Tolerancias de la ESCRITURA de cada cifra a mano, no de la maquina; todas
# con nombre.
TOL_HW = 2e-4               # cargas escritas a cuatro decimales, m
TOL_ZAPATA = 1e-9           # una suma o un producto de numeros exactos
TOL_FACTOR = 1e-6           # factores gamma·eta escritos a seis decimales
TOL_MM = 2e-3               # cifras escritas a tres decimales
TOL_CM = 6e-3               # cifras escritas a dos decimales
TOL_CINCO = 1e-5            # cifras escritas a cinco decimales
TOL_E = 5e-4                # excentricidades y fuerzas a cuatro decimales


# ===========================================================================
# PUNTO 3 -- V8 con el caudal que no cabe en flujo uniforme
# ===========================================================================

def _tubo_de_A01():
    """El tubo de concreto de Ø 0.90 m de A-01 (primer candidato de M2)."""
    punto = next(p for p in M0.cargar_puntos(CSV_EJEMPLO) if p.id == "A-01")
    return modelos.SeccionCircular(0.90), M2.materiales_candidatos(punto)[0]


def _carga(seccion, material, Q, S, L, TW):
    """
    La carga que V8 usaria para Q: en lamina libre (`resolver_control`) si
    M3 le encuentra tirante normal; si no, `hidraulica_a_presion`. Es lo que
    hace `servicio._datos_de_expediente.resolver`.
    """
    normal = M3.resolver_manning(seccion=seccion, Q=Q, S=S, material=material)
    if normal is not None:
        r = M4.resolver_control(seccion=seccion, Q=Q, S=S, L=L, TW=TW,
                                material=material, normal=normal)
        return r.HW, "lamina libre", ()
    p = M4.hidraulica_a_presion(seccion=seccion, Q=Q, S=S, L=L, TW=TW,
                                material=material)
    return p.HW, p.regimen, p.avisos


def test_p3_el_caudal_mayor_no_da_menos_carga_que_la_lamina_libre():
    """
    EL CONTROL DEL VERIFICADOR. Tubo de A-01 con S = 0.003, L = 60 m y TW =
    0; el caudal de flujo uniforme a seccion llena es 0.9915 m3/s.

        Q = 0.9866  lamina libre, control de salida, rige el remanso: 0.9654 m
        Q = 1.0213  no cabe en flujo uniforme. ANTES: 0.9570 m («a presion»,
                    la aproximacion de barril lleno tal cual: HW/D = 1.063),
                    MENOS que con el caudal menor. AHORA: 0.9890 m, la mayor
                    de la aproximacion y del remanso.
    """
    seccion, material = _tubo_de_A01()
    caso = dict(S=0.003, L=60.0, TW=0.0)
    HW_libre, regimen_libre, _ = _carga(seccion, material, 0.9866, **caso)
    assert regimen_libre == "lamina libre"
    assert HW_libre == pytest.approx(0.9654, abs=TOL_HW)
    extremo = M4.hidraulica_a_presion(seccion=seccion, Q=1.0213,
                                      material=material, **caso)
    assert extremo.regimen == modelos.REGIMEN_EVENTO_A_PRESION
    assert extremo.control_gobernante is ControlGobernante.SALIDA
    assert extremo.HW >= HW_libre
    assert extremo.HW == pytest.approx(0.9890, abs=TOL_HW)
    assert extremo.HW_salida == pytest.approx(extremo.HW, abs=ABS_CERO)
    # la aproximacion sola, que era lo que se entregaba, queda por debajo
    critico = M4.tirante_critico(1.0213, seccion)
    aprox = M4.control_salida(
        Q=1.0213, seccion=seccion, n=material.n_para_capacidad,
        critico=critico, criterio_ke=M4.criterio_ke_de(material), **caso)
    assert aprox.HW == pytest.approx(0.9570, abs=TOL_HW)
    assert aprox.HW < HW_libre < extremo.HW
    # y se AVISA, con el numero de la fuente y la pagina
    assert len(extremo.avisos) == 1
    aviso = extremo.avisos[0]
    assert "1.2" in aviso and "3.24" in aviso and "caution" in aviso
    assert "0.957" in aviso and "0.989" in aviso


def _Q_lleno(seccion, material, S):
    """Caudal de flujo uniforme a seccion llena (Manning, con n_max), m3/s."""
    return (seccion.area_llena * M4.radio_hidraulico_lleno(seccion) ** (2 / 3)
            * math.sqrt(S) / material.n_para_capacidad)


@pytest.mark.parametrize("S, L, TW", [(0.003, 60.0, 0.0), (0.004, 100.0, 0.0),
                                      (0.0002, 20.0, 0.0),
                                      (0.006, 18.869, 0.5)])
def test_p3_la_carga_no_cae_al_cruzar_el_caudal_de_seccion_llena(S, L, TW):
    """
    EL DEFECTO ERA UN ESCALON AL CAMBIAR DE VIA: al pasar de la lamina libre
    (`resolver_control`, con el perfil) al barril «a presion»
    (`hidraulica_a_presion`, sin el), la carga CAIA --de 0.9654 a 0.9347 m en
    el primer caso; de 1.0547 a 1.0315 m en el segundo--. Con el mismo
    metodo a los dos lados el cruce es continuo: del 99.5 % al 100.5 % del
    caudal de seccion llena la carga no baja y sube menos de 2 cm (lo que
    da la pendiente de la curva de gasto en un 1 % de caudal: 1.3 cm donde
    gobierna la entrada).
    """
    seccion, material = _tubo_de_A01()
    Q_lleno = _Q_lleno(seccion, material, S)
    HW_a, via_a, _ = _carga(seccion, material, 0.995 * Q_lleno, S, L, TW)
    HW_b, via_b, _ = _carga(seccion, material, 1.005 * Q_lleno, S, L, TW)
    assert (via_a, via_b) == ("lamina libre", modelos.REGIMEN_EVENTO_A_PRESION)
    assert HW_b >= HW_a
    assert HW_b - HW_a < 0.02


def test_p3_el_salto_del_borde_de_la_banda_lo_cubre_la_guardia_de_V8():
    """
    LO QUE LA CORRECCION DE M4 NO QUITA, medido al escribir este archivo: la
    regla de E-A tiene un escalon PROPIO donde la aproximacion cruza HW/D =
    1.2. Por debajo compite el remanso; por encima la fuente da la
    aproximacion por buena y el remanso deja de competir. Tubo de A-01 con
    S = 0.006, L = 18.869 m y TW = 0.5 m, los dos caudales en LAMINA LIBRE
    (el de seccion llena es 1.402 m3/s):

        Q = 0.91·1.402 = 1.276 m3/s   rige el remanso de salida   1.1507 m
        Q = 0.92·1.402 = 1.290 m3/s   rige la entrada             1.1394 m

    Un caudal mayor con 11 mm menos de carga. Es de `M4.resolver_control`
    (codigo de E-A, conforme; ficha T7V-01) y no se toca: lo cubre la
    guardia de `M5.v8_evento_extremo`, que con ese par acota la carga del
    evento a la de diseño y lo avisa.
    """
    seccion, material = _tubo_de_A01()
    caso = dict(S=0.006, L=18.869, TW=0.5)
    Q_lleno = _Q_lleno(seccion, material, caso["S"])
    Q_d, Q_ext = 0.91 * Q_lleno, 0.92 * Q_lleno
    HW_d, via_d, _ = _carga(seccion, material, Q_d, **caso)
    HW_ext, via_ext, _ = _carga(seccion, material, Q_ext, **caso)
    assert via_d == via_ext == "lamina libre"
    assert HW_d == pytest.approx(1.1507, abs=TOL_HW)
    assert HW_ext == pytest.approx(1.1394, abs=TOL_HW)
    _declarar_v8()
    v = _llamar_v8(_evento(Q=Q_ext, HW_ext=HW_ext), Q_diseno=Q_d,
                   HW_diseno=HW_d)
    assert v.valor_obtenido == pytest.approx(42.10 + HW_d, abs=TOL_ZAPATA)
    assert len(v.avisos) == 1 and "1.139 m" in v.avisos[0]


def test_p3_bajo_0_75_la_aproximacion_no_se_usa_y_se_avisa():
    """
    S = 0.0002, L = 20 m, TW = 0, Q = 0.257 m3/s (apenas sobre el caudal de
    flujo uniforme a seccion llena, 0.256): la aproximacion de barril lleno
    da 0.608 m, HW/D = 0.676 < 0.75, donde el HDS-5 dice «the approximate
    method should not be used». ANTES se entregaba ese 0.608 m rotulado
    «barril a presion», sin aviso. AHORA la carga de salida es la del
    remanso (0.458 m), como en lamina libre, y se avisa. No se levanta
    `MetodoNoEvaluableError`: la fuente dice que hacer (calculo de remanso,
    pag. 3.12) y M4 lo tiene.
    """
    seccion, material = _tubo_de_A01()
    r = M4.hidraulica_a_presion(seccion=seccion, Q=0.257, S=0.0002, L=20.0,
                                TW=0.0, material=material)
    assert r.HW == pytest.approx(0.4580, abs=TOL_HW)
    assert r.control_gobernante is ControlGobernante.SALIDA
    assert r.HW / 0.90 < cn.H_O_HW_SOBRE_D_MIN
    assert len(r.avisos) == 1
    assert "NO se usa" in r.avisos[0] and "0.676" in r.avisos[0]
    assert "should not be used" in r.avisos[0] and "0.458" in r.avisos[0]
    assert "0.608" in r.nota


def test_p3_A01_no_cambia():
    """
    A-01 con los datos de prueba del evento extremo (Q = 1.75 m3/s, TW =
    0.5 m, S = 0.006, L = 18.869 m): gobierna la ENTRADA, ec. (A.3):
    q* = 1.811·1.75/(0.63617·0.9^0.5) = 5.251; HW/D = 0.0398·5.251^2 + 0.67
    - 0.5·0.006 = 1.7645; HW = 1.588 m; cota 42.10 + 1.588 = 43.69 msnm. La
    correccion solo toca el control de salida bajo 1.2 D: aqui nada, y sin
    avisos.
    """
    seccion, material = _tubo_de_A01()
    r = M4.hidraulica_a_presion(seccion=seccion, Q=1.75, S=0.006, L=18.869,
                                TW=0.5, material=material)
    assert r.control_gobernante is ControlGobernante.ENTRADA
    assert r.HW == pytest.approx(1.5880, abs=TOL_HW)
    assert r.HW_entrada == pytest.approx(1.5880, abs=TOL_HW)
    assert r.HW_salida == pytest.approx(1.4779, abs=TOL_HW)
    assert r.avisos == ()
    cota_del_embalse = 42.10 + r.HW
    assert cota_del_embalse == pytest.approx(43.69, abs=TOL_CM)


def test_p3_V8_acota_la_carga_del_evento_a_la_de_diseno_y_avisa():
    """
    La guardia de `M5.v8_evento_extremo`: HW_ext >= HW de diseño. Con una
    carga del evento (0.90 m, de apoyo) MENOR que la de diseño de A-01
    (1.042 m), V8 no juzga con 0.90: cota del embalse = 42.10 + 1.042 =
    43.142 msnm, y lo dice en `Verificacion.avisos` y en el paso.
    """
    _declarar_v8()
    v = _llamar_v8(_evento(HW_ext=0.90))
    assert v.valor_obtenido == pytest.approx(42.10 + 1.042, abs=TOL_HW)
    assert v.estado is EstadoDeVerificacion.CUMPLE
    assert len(v.avisos) == 1
    assert "0.900 m" in v.avisos[0] and "1.042 m" in v.avisos[0]
    assert "un caudal mayor no puede dar menos carga" in v.avisos[0]
    hw = next(m for m in v.paso.sustitucion if m.simbolo == "HW_ext")
    assert hw.valor == pytest.approx(1.042, abs=ABS_CERO)
    assert "ACOTADA" in hw.procedencia and "0.900" in hw.procedencia
    assert v.avisos[0] in v.paso.nota_del_proyecto
    # y con ella puede NO cumplir donde la carga sin acotar cumplia
    v = _llamar_v8(_evento(HW_ext=0.90, cota=43.10))
    assert v.estado is EstadoDeVerificacion.NO_CUMPLE


def test_p3_V8_sin_acotar_no_avisa_y_los_avisos_de_M4_viajan():
    """
    Con HW_ext >= HW de diseño la guardia no actua (tampoco en el empate:
    «el caudal puede ser el de diseño»). Y los avisos que la hidraulica del
    evento trae (`HidraulicaDelEventoExtremo.avisos`) llegan a
    `Verificacion.avisos` con el codigo delante.
    """
    _declarar_v8()
    for HW_ext in (1.147, 1.042):
        v = _llamar_v8(_evento(HW_ext=HW_ext))
        assert v.avisos == ()
        assert v.valor_obtenido == pytest.approx(42.10 + HW_ext, abs=TOL_HW)

    def resolver(seccion, material):
        return modelos.HidraulicaDelEventoExtremo(
            HW=1.147, control_gobernante=ControlGobernante.SALIDA,
            regimen=modelos.REGIMEN_EVENTO_A_PRESION, HW_entrada=1.0,
            HW_salida=1.147, avisos=("evento extremo: de prueba",))
    v = _llamar_v8(_evento(resolver=resolver))
    assert v.avisos == ("V8: evento extremo: de prueba",)


def test_p3_los_avisos_de_una_verificacion_salen_por_avisos_del_punto():
    """`InformePunto.avisos()` recoge `Verificacion.avisos`, una vez."""
    _declarar_v8()
    v = _llamar_v8(_evento(HW_ext=0.90))
    punto = next(p for p in M0.cargar_puntos(CSV_EJEMPLO) if p.id == "A-01")
    informe = servicio.InformePunto(punto=punto)
    assert not [a for a in informe.avisos() if a.startswith("V8:")]
    informe.resultado = SimpleNamespace(verificaciones=(v, v), aceptado=True)
    assert [a for a in informe.avisos() if a.startswith("V8:")] == list(
        v.avisos)


def test_p3_el_resolver_del_servicio_usa_las_dos_vias(tmp_path):
    """
    De punta a punta: A-01 con el caudal del evento de prueba que no cabe en
    flujo uniforme (1.75 m3/s; el caudal a seccion llena es 1.402). V8
    cumple con 42.10 + 1.588 = 43.69 msnm <= 44.20, sin avisos de V8, y el
    diametro es el de la linea base.
    """
    _, a01 = _correr_de_prueba(
        tmp_path, extra_a01={"Q_evento_extremo_m3s": 1.75})
    assert a01.resultado.seccion.etiqueta() == "Ø 0.90 m"
    v8 = next(v for v in a01.resultado.verificaciones if v.codigo == "V8")
    assert v8.estado is EstadoDeVerificacion.CUMPLE
    assert v8.valor_obtenido == pytest.approx(43.688, abs=TOL_MM)
    assert v8.avisos == ()
    assert not [a for a in a01.avisos() if a.startswith("V8:")]


# ===========================================================================
# PUNTO 9 -- el modificador de carga de AASHTO 1.3.2.1 en el cabezal
# ===========================================================================

def test_p9_las_tres_citas_estan_en_su_pagina_y_los_criterios_declarados():
    r = construir()
    eta = r.cita("AASHTO_LRFD_9.1.3.2.1#ETA")
    assert (eta.pagina_impresa, eta.pagina_pdf) == ("1-3", 18)
    assert "Eq. 1.3.2.1-1" in eta.texto_literal.texto
    assert eta.interpretacion is not None       # WA y LS: gamma unico
    assert r.cita("AASHTO_LRFD_9.1.3.3").pagina_pdf == 20
    assert "conventional designs" in r.cita(
        "AASHTO_LRFD_9.1.3.3").texto_literal.texto
    assert r.cita("AASHTO_LRFD_9.1.3.4").pagina_pdf == 21
    for clave in ("eta_ductilidad_cabezal", "eta_redundancia_cabezal"):
        c = ca.CRITERIOS[clave]
        assert c.etiqueta == "A" and c.nivel == ca.NIVEL_EXPEDIENTE
        assert c.valor == pytest.approx(1.0, abs=ABS_CERO)
        assert c.sensibilidad == pytest.approx((0.95, 1.05), abs=ABS_CERO)
    # eta_I es UNO: el del cruce, la misma clave que lee el conducto
    from src.modulos import M8_estructural as M8
    assert M9.CRITERIO_ETA_IMPORTANCIA == M8.CRITERIO_ETA_CONDUCTO
    cruce = ca.CRITERIOS[M9.CRITERIO_ETA_IMPORTANCIA]
    assert cruce.valor == pytest.approx(1.05, abs=ABS_CERO)
    assert "CRUCE" in cruce.concepto and "cabezal" in cruce.concepto


def test_p9_el_modificador_de_carga_a_mano_y_acotado():
    """
    De archivo: eta_D = eta_R = 1.00, eta_I = 1.05 -> producto 1.05; maximo
    1.05, minimo 1/1.05 = 0.952381. Con los tres en 0.95 el producto es
    0.857375 < 0.95: el de gamma maximo se acota a 0.95 (Ec. 1.3.2.1-2) y el
    de gamma minimo, 1/0.857375 = 1.166351, a 1.0 (Ec. 1.3.2.1-3).
    """
    eta = M9.modificador_de_carga()
    assert (eta["eta_D"], eta["eta_R"], eta["eta_I"]) == pytest.approx(
        (1.0, 1.0, 1.05), abs=ABS_CERO)
    assert eta["maximo"] == pytest.approx(CP["eta_max"], abs=ABS_CERO)
    assert eta["minimo"] == pytest.approx(0.952381, abs=TOL_FACTOR)
    with con_valor("eta_ductilidad_cabezal", 0.95, motivo="de prueba"), \
            con_valor("eta_redundancia_cabezal", 0.95, motivo="de prueba"), \
            con_valor("eta_importancia_operativa_conducto", 0.95,
                      motivo="de prueba"):
        eta = M9.modificador_de_carga()
        assert eta["producto"] == pytest.approx(0.857375, abs=TOL_ZAPATA)
        assert eta["maximo"] == pytest.approx(0.95, abs=ABS_CERO)
        assert eta["minimo"] == pytest.approx(1.0, abs=ABS_CERO)
    with con_valor("eta_redundancia_cabezal", 1.05, motivo="de prueba"):
        eta = M9.modificador_de_carga()
        assert eta["maximo"] == pytest.approx(1.05 * 1.05, abs=TOL_ZAPATA)
        assert eta["minimo"] == pytest.approx(1 / 1.1025, abs=TOL_ZAPATA)


@pytest.fixture
def tanteo_con_eta(tanteo):
    """
    El muro de tanteo con el eta_I de ARCHIVO (1.05): el fixture `tanteo`
    declara 1.00 para sus dorados, y aqui se retira esa declaracion.
    """
    ca.quitar_valor_dinamico("eta_importancia_operativa_conducto")
    assert ca.valor("eta_importancia_operativa_conducto") == \
        pytest.approx(1.05, abs=ABS_CERO)
    return tanteo


def _combo(e, fragmento, marco=MARCO_LRFD):
    return next(c for c in e.combinaciones
                if fragmento in c.nombre and c.marco == marco)


def test_p9_resistencia_I_del_muro_de_tanteo_con_eta_a_mano(tanteo_con_eta):
    """`CP_T7V_ETA`: las dos combinaciones de Resistencia I, a mano."""
    e = M9.ensamble_estabilidad(tanteo_con_eta, EST)
    minimos = _combo(e, "(minimos)")
    for clave, valor in (("N", minimos.N), ("H", minimos.H),
                         ("M_e", minimos.M_estabilizante),
                         ("M_v", minimos.M_volcante)):
        assert valor == pytest.approx(CP["resistencia_min"][clave], abs=TOL)
    e_min = minimos.B / 2 - (minimos.M_estabilizante
                             - minimos.M_volcante) / minimos.N
    assert e_min == pytest.approx(CP["resistencia_min"]["e"], abs=TOL)
    maximos = _combo(e, "(maximos)")
    assert maximos.N == pytest.approx(CP["resistencia_max"]["N"], abs=TOL)
    assert maximos.M_estabilizante == pytest.approx(
        CP["resistencia_max"]["M_e"], abs=TOL)
    # cada factor es gamma·eta_i
    f_max, f_min = dict(maximos.factores), dict(minimos.factores)
    for codigo, tipo in (("DC.pantalla", "DC"), ("DC.zapata", "DC"),
                         ("EV.talon", "EV"), ("EH.h", "EH"), ("EH.v", "EH"),
                         ("LS.h", "LS")):
        assert f_max[codigo] == pytest.approx(CP["factores_max"][tipo],
                                              abs=TOL_FACTOR)
        assert f_min[codigo] == pytest.approx(CP["factores_min"][tipo],
                                              abs=TOL_FACTOR)
    assert f_max["LS.v"] == pytest.approx(1.8375, abs=TOL_FACTOR)
    assert f_min["LS.v"] == pytest.approx(0.0, abs=ABS_CERO)


def test_p9_eta_cambia_el_veredicto_del_deslizamiento_del_muro_de_tanteo(
        tanteo_con_eta):
    """
    E3-LRFD a mano (`CP_T7V_ETA`): H = 37.1770 > 0.8·74.3272·tan 32° =
    37.1558 kN/m: NO CUMPLE por 0.0211 kN/m. Con eta = 1.00 cumplia (35.4066
    <= 38.6066): el modificador no era un adorno. E1 y E2 siguen cumpliendo.
    """
    e = M9.ensamble_estabilidad(tanteo_con_eta, EST)
    por = {v.codigo: v for v in e.verificaciones}
    e3 = por["E3-LRFD.est.e"]
    assert e3.valor_obtenido == pytest.approx(CP["E3_LRFD"]["H"], abs=TOL)
    assert e3.valor_admisible == pytest.approx(CP["E3_LRFD"]["R_R"], abs=TOL)
    assert e3.estado is EstadoDeVerificacion.NO_CUMPLE
    assert e3.paso.veredicto.margen == pytest.approx(
        CP["E3_LRFD"]["margen"], abs=TOL)
    e2 = por["E2-LRFD.est.e"]
    assert e2.valor_obtenido == pytest.approx(CP["E2_LRFD"]["e"], abs=TOL)
    assert e2.estado is EstadoDeVerificacion.CUMPLE
    e1 = por["E1-LRFD.est.e"]
    assert e1.valor_obtenido == pytest.approx(CP["E1_LRFD"]["sigma_v"],
                                              rel=REL)
    assert e1.valor_admisible == pytest.approx(CP["E1_LRFD"]["q_R"], rel=REL)
    assert e1.estado is EstadoDeVerificacion.CUMPLE
    # con eta_I = 1.00 declarado, el dorado de T-7b: cumple
    with con_valor("eta_importancia_operativa_conducto", 1.0,
                   motivo="el valor «typical» de AASHTO 1.3.5"):
        e3 = {v.codigo: v for v in M9.ensamble_estabilidad(
            tanteo_con_eta, EST).verificaciones}["E3-LRFD.est.e"]
    assert e3.valor_obtenido == pytest.approx(CPB["E3_LRFD"]["H"], abs=TOL)
    assert e3.estado is EstadoDeVerificacion.CUMPLE


def test_p9_el_evento_extremo_el_marco_ASD_y_el_servicio_no_llevan_eta(
        tanteo_con_eta):
    """
    «For all other limit states» eta_D = eta_R = eta_I = 1.00 (1.3.3, 1.3.4,
    1.3.5): las combinaciones sismicas son las del dorado de T-7b, calculado
    con los factores de la tabla; y las del marco ASD (E.050) tienen todos
    sus factores en 1 o en 0. Los marcos no se cruzan.
    """
    sis = M9.ensamble_estabilidad(tanteo_con_eta, SIS)
    caso_1 = next(c for c in sis.combinaciones
                  if c.marco == MARCO_LRFD and "100% P_AE + 50%" in c.nombre
                  and "portante" not in c.nombre)
    assert caso_1.N == pytest.approx(CPB["sismico"]["caso_1"]["N"], abs=TOL)
    assert caso_1.H == pytest.approx(CPB["sismico"]["caso_1"]["H"], abs=TOL)
    est = M9.ensamble_estabilidad(tanteo_con_eta, EST)
    def _solo(factores, admitidos):
        """Cada factor es uno de los `admitidos` (sin eta: ni 1.05 ni 1/1.05)."""
        return all(min(abs(f - x) for x in admitidos) <= ABS_CERO
                   for _, f in factores)

    for e in (est, sis):
        for c in e.combinaciones:
            if c.marco == MARCO_ASD:
                assert _solo(c.factores, (0, 0.5, 1)), c
    for c in M9._combinaciones_de_servicio(est.cargas, 2.0):
        assert _solo(c.factores, (0, 1)), c
    for c in M9._combinaciones_e060(est.cargas, 2.0):
        assert _solo(c.factores, (0, 0.9, 1.4, 1.7)), c


def test_p9_el_armado_lleva_el_mismo_eta_que_la_estabilidad(tanteo_con_eta):
    """
    La pantalla en reposo del muro de tanteo (`CP_T7C_ARMADO`: V_u = 1.35·18.0
    + 1.75·10.9728 = 43.5024 kN/m y M_u = 1.35·12.0 + 1.75·10.9728 = 35.4024
    kN·m/m con eta = 1.00) solo recibe empuje y sobrecarga, cargas de gamma
    maximo en las dos combinaciones: con eta = 1.05, 45.6775 y 37.1725.
    """
    sol = M9.solicitaciones_de_resistencia(tanteo_con_eta)
    for fragmento in ("(maximos)", "(minimos)"):
        s = _de(sol, SECCION_PANTALLA, "Resistencia I " + fragmento)
        assert s.V_u_reposo == pytest.approx(CP["pantalla_reposo"]["V_u"],
                                             abs=TOL)
        assert s.M_u_reposo == pytest.approx(CP["pantalla_reposo"]["M_u"],
                                             abs=TOL)
    assert CP["pantalla_reposo"]["V_u"] == pytest.approx(45.6775, abs=TOL)
    assert CP["pantalla_reposo"]["M_u"] == pytest.approx(37.1725, abs=TOL)


def test_p9_la_memoria_dice_el_modificador_con_su_cita(tanteo_con_eta):
    """El paso de combinaciones y el del regimen del armado lo imprimen."""
    est = M9.ensamble_estabilidad(tanteo_con_eta, EST)
    combinaciones = next(p for p in est.pasos if p.codigo.startswith("9.2.5"))
    simbolos = {m.simbolo: m for m in combinaciones.sustitucion}
    assert simbolos["eta_I"].valor == pytest.approx(1.05, abs=ABS_CERO)
    assert "eta_importancia_operativa_conducto" in simbolos["eta_I"].procedencia
    assert simbolos["eta_i, cargas de gamma minimo"].valor == pytest.approx(
        1 / 1.05, abs=TOL_ZAPATA)
    for cita in M9.CITAS_DE_ETA:
        assert cita in combinaciones.citas_textuales
    assert "1.3.2.1" in combinaciones.nota_del_proyecto
    assert "mismo eta_I del conducto" in combinaciones.nota_del_proyecto
    sis = M9.ensamble_estabilidad(tanteo_con_eta, SIS)
    p_sis = next(p for p in sis.pasos if p.codigo.startswith("9.2.5"))
    assert "eta_I" not in {m.simbolo for m in p_sis.sustitucion}
    assert "For all other limit states" in p_sis.nota_del_proyecto
    armado = M9.armado_del_cabezal(tanteo_con_eta)
    regimen = armado.pasos[0]
    assert "eta_I" in {m.simbolo for m in regimen.sustitucion}
    assert "AASHTO_LRFD_9.1.3.2.1#ETA" in regimen.citas_textuales


# ===========================================================================
# PUNTO 7 -- el piso del espesor de la zapata armada (E.060 15.7)
# ===========================================================================

def test_p7_el_piso_de_la_zapata_armada_a_mano():
    """
    piso = 0.30 (E.060 15.7, sobre el refuerzo inferior, al EJE de la capa)
         + recubrimiento con que se arma la cara contra el suelo
         + medio diametro de la mayor barra del catalogo (Ø 1" = 25.4 mm)

      sin la categoria del acero ni el analisis quimico (como el programa
      corre hoy): la cota de 91.44 mm -> 0.30 + 0.09144 + 0.0127 = 0.40414 m
      con el acero «A» y el analisis quimico de prueba del conftest: los 70
      mm de E.060 7.7.1 a) -> 0.30 + 0.070 + 0.0127 = 0.3827 m
    ANTES era 0.30 + 0.070 = 0.37 m en los dos casos.
    """
    piso, texto, cita = M9.peralte_minimo_zapata(M9.TIPO_VOLADIZO)
    assert piso == pytest.approx(0.3827, abs=TOL_ZAPATA)
    assert cita == "E060.15.7#PERALTE"
    assert "70.00 mm" in texto and "12.70 mm" in texto and 'Ø 1"' in texto
    _sin_datos_de_exposicion()
    piso, texto, _ = M9.peralte_minimo_zapata(M9.TIPO_VOLADIZO)
    assert piso == pytest.approx(0.40414, abs=TOL_ZAPATA)
    assert "91.44 mm" in texto and "cota mas exigente" in texto
    # el de gravedad no cambia
    assert M9.peralte_minimo_zapata(M9.TIPO_GRAVEDAD)[0] == pytest.approx(
        0.30, abs=ABS_CERO)


@pytest.mark.parametrize("barra, diametro_mm", [("1/2", 12.7), ("5/8", 15.9),
                                                ("3/4", 19.1), ("1", 25.4)])
def test_p7_A8_cumple_por_construccion_con_cualquier_barra_del_catalogo(
        barra, diametro_mm):
    """
    Con la zapata en el piso de regla, la altura al eje de la capa inferior
    es 0.30 + (25.4 - diametro)/2 mm >= 0.30 m para toda barra del catalogo:
    0.30635 con Ø 1/2", 0.30475 con 5/8", 0.30315 con 3/4" y 0.30000 con 1".
    Y eso vale con la cota de recubrimiento y con el dato declarado.
    """
    catalogo = M9.catalogo_de_barras()
    assert dict((n, d) for d, _, n in catalogo["barras"])[barra] == \
        pytest.approx(diametro_mm, abs=ABS_CERO)
    for retirar in (False, True):
        if retirar:
            _sin_datos_de_exposicion()
        piso = M9.peralte_minimo_zapata(M9.TIPO_VOLADIZO)[0]
        rec = M9.recubrimiento_para_armar(
            condicion=M9.CONDICION_RECUBRIMIENTO_ZAPATA)[0]
        altura = piso - (rec + diametro_mm / 2) / 1000
        assert altura == pytest.approx(0.30 + (25.4 - diametro_mm) / 2000,
                                       abs=TOL_ZAPATA)
        assert altura >= 0.30 - TOL_ZAPATA


def test_p7_A8_del_muro_de_tanteo_y_de_una_zapata_declarada_mas_delgada(
        tanteo):
    """
    La fila A8 sigue pudiendo FALLAR. El muro de tanteo (zapata DECLARADA de
    0.40 m, Ø 1/2", cota de 91.44 mm): 0.40 - 0.09144 - 0.00635 = 0.30221 m
    >= 0.30: cumple. Con la zapata de 0.37 m de la regla anterior: 0.37 -
    0.09779 = 0.27221 m: NO cumple, y la nota ya no dice que baste bajar el
    recubrimiento.
    """
    a = M9.armado_del_cabezal(tanteo)
    a8 = next(v for v in a.verificaciones if v.codigo.startswith("A8"))
    assert a8.cumple
    assert a8.valor_obtenido == pytest.approx(0.30221, abs=TOL_CINCO)
    from dataclasses import replace
    delgada = replace(tanteo, geometria=replace(tanteo.geometria,
                                                espesor_zapata=0.37, H=2.03))
    a8 = next(v for v in M9.armado_del_cabezal(delgada).verificaciones
              if v.codigo.startswith("A8"))
    assert not a8.cumple
    assert a8.valor_obtenido == pytest.approx(0.27221, abs=TOL_CINCO)
    nota = a8.paso.nota_del_proyecto
    assert "no alcanza por si solo" in nota and "DECLARO" in nota
    assert "o bajar el recubrimiento con el dato de exposicion" not in nota
    lecturas = {m.simbolo for m in a8.paso.sustitucion}
    assert {"hasta la cara inferior de la barra",
            "hasta la cara superior de la barra"} <= lecturas


@pytest.mark.lento
def test_p7_p9_A01_con_los_datos_de_prueba_las_doce_filas_y_A8(tmp_path):
    """
    A-01 con los datos DE PRUEBA de T-7b y SIN la categoria del acero ni el
    analisis quimico (cota de 91.44 mm). La zapata de los dos cabezales pasa
    de 0.37 a 0.40414 m y Resistencia I lleva eta_I = 1.05.

    LAS DOCE FILAS LRFD (obtenido / admisible; kPa, m y kN/m), antes -> ahora:

      entrada, estatica
        E1   67.52 <= 87.41      ->  73.41 <= 86.72      cumple
        E2   0.352 <= 0.525      ->  0.396 <= 0.525      cumple
        E3   38.05 >  29.39      ->  39.95 >  28.70      NO cumple
      entrada, sismica (eta = 1.00: solo se mueve por la zapata)
        E1   80.26 >  52.94      ->  80.86 >  54.11      NO cumple
        E2   0.392 <= 0.578      ->  0.391 <= 0.578      cumple
        E3   38.82 <= 39.68      ->  38.89 <= 40.04      cumple
      salida, estatica
        E1   81.85 <= 100.81     ->  78.17 <= 91.57      cumple
        E2   0.362 <= 0.685      ->  0.415 <= 0.685      cumple
        E3   57.93 >  49.13      ->  60.83 >  47.90      NO cumple
      salida, sismica
        E1   97.13 >  56.22      ->  97.73 >  57.16      NO cumple
        E2   0.488 <= 0.754      ->  0.487 <= 0.754      cumple
        E3   62.79 <= 65.58      ->  62.89 <= 66.07      cumple

    NINGUN VEREDICTO CAMBIA. Y A8 pasa de 0.2722 m (no cumple) a 0.40414 -
    0.09144 - 0.00635 = 0.30635 m (cumple) en los dos cabezales.

    E3 ESTATICA, A MANO, sobre las cargas sin factorar del ensamble:
      entrada  H = 1.575·15.6318 + 1.8375·8.3429 = 24.6201 + 15.3301 = 39.9502
               N = (0.90·(13.0465 + 14.9964) + 24.1978)/1.05 + 1.575·6.5646
                 = (25.2386 + 24.1978)/1.05 + 10.3392 = 47.0823 + 10.3392
                 = 57.4215;  0.8·57.4215·tan 32° = 0.8·35.8809 = 28.7047
      salida   H = 1.575·26.3817 + 1.8375·10.4905 = 41.5512 + 19.2763 = 60.8275
               N = (0.90·(17.9007 + 19.5739) + 48.5710)/1.05 + 1.575·11.0790
                 = (33.7271 + 48.5710)/1.05 + 17.4494 = 78.3791 + 17.4494
                 = 95.8285;  0.8·95.8285·0.62486935 = 0.8·59.8803 = 47.9042
    """
    _sin_datos_de_exposicion()
    _, a01 = _correr_de_prueba(tmp_path)
    assert a01.dimensionado
    assert a01.resultado.seccion.etiqueta() == "Ø 0.90 m"
    for g in a01.cabezal.geometrias:
        assert g.espesor_zapata == pytest.approx(0.40414, abs=TOL_ZAPATA)
    esperado = {
        "E1-LRFD.est.e": (73.41, 86.72, True),
        "E2-LRFD.est.e": (0.3964, 0.5250, True),
        "E3-LRFD.est.e": (39.9502, 28.7047, False),
        "E1-LRFD.sis.e": (80.86, 54.11, False),
        "E2-LRFD.sis.e": (0.3912, 0.5775, True),
        "E3-LRFD.sis.e": (38.89, 40.04, True),
        "E1-LRFD.est.s": (78.17, 91.57, True),
        "E2-LRFD.est.s": (0.4149, 0.6852, True),
        "E3-LRFD.est.s": (60.8275, 47.9042, False),
        "E1-LRFD.sis.s": (97.73, 57.16, False),
        "E2-LRFD.sis.s": (0.4869, 0.7538, True),
        "E3-LRFD.sis.s": (62.89, 66.07, True),
    }
    filas = {v.codigo: v for v in a01.cabezal.verificaciones}
    for codigo, (obtenido, admisible, cumple) in esperado.items():
        v = filas[codigo]
        tol = TOL_E if codigo.startswith("E2") or "E3-LRFD.est" in codigo \
            else TOL_CM
        assert v.valor_obtenido == pytest.approx(obtenido, abs=tol), codigo
        assert v.valor_admisible == pytest.approx(admisible, abs=tol), codigo
        assert v.cumple is cumple, codigo
    for ext in ("e", "s"):
        a8 = filas[f"A8.zapata.{ext}"]
        assert a8.cumple
        assert a8.valor_obtenido == pytest.approx(0.30635, abs=TOL_CINCO)
    assert sorted(v.codigo for v in a01.incumplidas()) == [
        "E1-LRFD.sis.e", "E1-LRFD.sis.s", "E3-LRFD.est.e", "E3-LRFD.est.s"]
    # el paso de combinaciones del punto dice el modificador
    assert any("mismo eta_I del conducto" in p.nota_del_proyecto
               for e in a01.cabezal.estabilidad for p in e.pasos)


# ===========================================================================
# El matiz de texto del punto 2 (V5 por cota de afectacion)
# ===========================================================================

@pytest.mark.lento
def test_p2_la_nota_de_V5_no_llama_nivel_mas_alto_al_de_la_boca(tmp_path):
    """
    La nota decia que V5 compara «el nivel mas alto del embalse (en la
    boca)»: eso solo vale con el embalse a nivel. Con una curva de remanso
    la superficie sigue subiendo aguas arriba, y la nota lo dice.
    """
    _, a01 = _correr_de_prueba(tmp_path)
    v5 = next(v for v in a01.resultado.verificaciones if v.codigo == "V5")
    nota = v5.paso.nota_del_proyecto
    assert "el nivel mas alto del embalse (en la boca)" not in nota
    assert "EN LA BOCA" in nota and "solo si el embalse esta a nivel" in nota
    assert "curva de remanso" in nota


def test_no_evaluable_sigue_siendo_la_salida_cuando_las_piezas_no_corren():
    """La via del `MetodoNoEvaluableError` de `hidraulica_a_presion` sigue."""
    seccion, material = _tubo_de_A01()
    with pytest.raises(MetodoNoEvaluableError):
        M4.hidraulica_a_presion(seccion=seccion, Q=1.75, S=0.006, L=-1.0,
                                TW=0.5, material=material)
