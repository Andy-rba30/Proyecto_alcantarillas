"""
tests/test_ve7_alero_estabilidad.py
===================================
VE-7 (cierre de T7C-04, ficha VE7-01): el ALERO se verifica como MURO EN
VOLADIZO independiente, con su propia zapata.

La seccion que se verifica es la franja gobernante del alero, la del
ARRANQUE (la mas alta: el alero baja con el talud de h0 a H_f), con la
geometria que VE-6 ya definio (`M9.entorno_de_la_seccion_del_alero`): fuste
del espesor del alero sobre la zapata del alero, toda como talon, y el
relleno que sube hasta la plataforma detras de ella. Sobre esa franja:

1. las MISMAS filas E1 a E3 de AASHTO LRFD 11.6 que el cabezal, en los dos
   marcos y en las dos condiciones (el ensamble del cabezal, reutilizado),
   con codigos propios (`.alero`) para que no se confundan con las del
   cabezal;
2. si no cumple, su zapata crece por el TALON con el paso y el tope del
   cabezal ('dimensionamiento_zapata_cabezal' [A]); al tope, NO FACTIBLE con
   estos criterios, sin proponer otra cosa;
3. su zapata (el talon, en la cara del alero) se arma con el procedimiento
   de la zapata del cabezal.

Escrito ANTES del codigo. Los dorados, A MANO sobre el muro de tanteo de
T-7b (`CP_T7B_ESTABILIDAD`): los empujes del cabezal de tanteo valen para la
franja del arranque porque el relleno es horizontal (h = 2.40 m en los dos
planos virtuales) y la sobrecarga es la misma; lo que cambia es la seccion
(fuste de 0.25 m, zapata de B x 0.37 m sin punta) y por lo tanto los pesos y
sus brazos, que se recalculan aqui a mano.
"""

from __future__ import annotations

import math
from dataclasses import replace

import pytest

from src import criterios_adoptados as ca
from src.modelos import (CondicionAnalisis, CriterioPendienteError,
                         ELEMENTO_ZAPATA_ALEROS, MURO_ALERO,
                         SECCION_TALON, SECCION_TALON_ALERO)
from src.modulos import M9_cabezal as M9
from tests.fixtures.casos_patron import CP_T7B_ESTABILIDAD as CPB
from tests.test_t7c_cabezal_armado import tanteo  # noqa: F401
from tests.test_ve6_m9_alero import ALEROS, _con_aleros

EST = CondicionAnalisis.ESTATICO
SIS = CondicionAnalisis.SISMICO
REL = CPB["tolerancia_rel"]
TOL = 1e-9

# --- los datos del muro de tanteo, de la ficha del caso patron ------------
GAMMA_C = CPB["cargas"]["DC.zapata"][0] / (2.0 * 0.40)   # 23.56 kN/m3
GAMMA = CPB["gamma_relleno"]                               # 18 kN/m3
EH_H = CPB["cargas"]["EH.h"][1]                            # z = h/3 = 0.80
EH_V = CPB["cargas"]["EH.v"][0]                            # en el extremo
LS_H = CPB["cargas"]["LS.h"][1]                            # z = h/2 = 1.20
H_EQ = CPB["h_eq"]
TAN_PHI_F = math.tan(math.radians(CPB["suelo"]["phi_grados"]))
# la franja del arranque: fuste 0.25 m, zapata 0.37 m, H = 2.40 - 0.37
E_AL, E_Z, H_C, Z_REL = 0.25, 0.37, 2.40, 2.40
H_FUSTE = H_C - E_Z


def _franja_a_mano(B: float) -> dict:
    """
    Las cargas sin factorar de la franja del arranque con su zapata de
    ancho B, toda como talon (x desde la arista delantera, el pie del
    fuste):

        DC fuste  = e·H·gamma_c                 en x = e/2
        DC zapata = B·e_z·gamma_c               en x = B/2
        EV talon  = (B - e)·(z_rel - e_z)·gamma en x = e + (B - e)/2
        EH.v      la del tanteo (mismo plano)   en x = B
    """
    t = B - E_AL
    return {
        "DC.pantalla": (E_AL * H_FUSTE * GAMMA_C, E_AL / 2),
        "DC.zapata": (B * E_Z * GAMMA_C, B / 2),
        "EV.talon": (t * (Z_REL - E_Z) * GAMMA, E_AL + t / 2),
        "EH.v": (EH_V, B),
        "LS.v": (GAMMA * H_EQ * t, E_AL + t / 2),
    }


def _resistencia_minimos(B: float):
    """
    Resistencia I con los factores minimos de los permanentes que
    estabilizan (AASHTO 3.4.1-2: DC 0.90, EV 1.00) y los maximos de los que
    empujan (EH 1.50, LS 1.75), sin la sobrecarga sobre el talon: la que el
    cabezal de tanteo fija en `resistencia_min`. Devuelve (N, H, M_e, M_v).
    """
    c = _franja_a_mano(B)
    N = (0.90 * (c["DC.pantalla"][0] + c["DC.zapata"][0])
         + 1.00 * c["EV.talon"][0] + 1.50 * c["EH.v"][0])
    M_e = (0.90 * (c["DC.pantalla"][0] * c["DC.pantalla"][1]
                   + c["DC.zapata"][0] * c["DC.zapata"][1])
           + 1.00 * c["EV.talon"][0] * c["EV.talon"][1]
           + 1.50 * c["EH.v"][0] * c["EH.v"][1])
    H = 1.50 * EH_H + 1.75 * LS_H
    M_v = 1.50 * EH_H * 0.80 + 1.75 * LS_H * 1.20
    return N, H, M_e, M_v


def _v(est, prefijo):
    return next(v for v in est.verificaciones
                if v.codigo.startswith(prefijo + "."))


# ---------------------------------------------------------------------------
# 1. La franja del arranque, verificada con las filas del cabezal
# ---------------------------------------------------------------------------

def test_el_alero_se_verifica_con_las_seis_filas_del_cabezal(tanteo):
    entorno = _con_aleros(tanteo)
    for condicion, abrev in ((EST, "est"), (SIS, "sis")):
        est = M9.estabilidad_del_alero(entorno, condicion)
        assert est.muro == MURO_ALERO
        assert est.extremo == "entrada" and est.condicion is condicion
        codigos = sorted(v.codigo for v in est.verificaciones)
        assert codigos == sorted(
            f"{f}-{m}.{abrev}.e.alero" for f in ("E1", "E2", "E3")
            for m in ("LRFD", "ASD"))
        # Los pasos y las filas dicen que es el alero, no el cabezal.
        assert all("alero" in p.que for p in est.pasos)
        assert all(p.codigo.endswith(".alero") for p in est.pasos)
        assert all("alero" in v.paso.que for v in est.verificaciones)
        # E4 y E5 siguen sin evaluar, y no repiten el paso del cabezal.
        assert [p[0] for p in est.pendientes] == ["E4", "E5"]
        assert not any(p.codigo.startswith("9.3.g") for p in est.pasos)


def test_es_el_ensamble_del_cabezal_sobre_la_franja_del_arranque(tanteo):
    """Reutiliza el ensamble: las mismas cifras que el cabezal daria con la
    geometria de la franja, solo con otro rotulo."""
    entorno = _con_aleros(tanteo)
    franja = M9.entorno_de_la_seccion_del_alero(entorno, 0.0)
    for condicion in (EST, SIS):
        alero = M9.estabilidad_del_alero(entorno, condicion)
        cabezal = M9.ensamble_estabilidad(franja, condicion)
        assert [(v.valor_obtenido, v.valor_admisible, v.cumple)
                for v in sorted(alero.verificaciones,
                                key=lambda v: v.codigo)] == [
            (v.valor_obtenido, v.valor_admisible, v.cumple)
            for v in sorted(cabezal.verificaciones, key=lambda v: v.codigo)]


def test_dorado_a_mano_de_E2_y_E3_estaticos_con_la_zapata_de_1_20(tanteo):
    """
    A mano, zapata del alero de 1.20 m (toda talon, 0.95 m tras el fuste):

        N   = 0.90·(11.957 + 10.461) + 34.713 + 1.50·5.2958 = 62.832 kN/m
        M_e = 0.90·(11.957·0.125 + 10.461·0.60) + 34.713·0.725
              + 1.50·5.2958·1.20 = 41.693 kN·m/m
        M_v = 1.50·14.4714·0.80 + 1.75·7.8283·1.20 = 33.805 kN·m/m
        e   = 0.60 - (41.693 - 33.805)/62.832 = 0.4745 m > B/3 = 0.40 m
        E3: H_u = 35.4066 <= phi_tau·N·tan(32) = 1.0·62.832·0.62487
            = 39.262 kN/m (phi_tau = 1.0, fila de muros de 11.5.7)
    """
    N, H, M_e, M_v = _resistencia_minimos(1.20)
    est = M9.estabilidad_del_alero(_con_aleros(tanteo), EST)
    e2 = _v(est, "E2-LRFD")
    assert e2.valor_obtenido == pytest.approx(0.60 - (M_e - M_v) / N,
                                              rel=REL)
    assert e2.valor_admisible == pytest.approx(1.20 / 3, rel=REL)
    assert not e2.cumple
    e3 = _v(est, "E3-LRFD")
    assert e3.valor_obtenido == pytest.approx(H, rel=REL)
    assert e3.valor_admisible == pytest.approx(1.0 * N * TAN_PHI_F, rel=REL)
    assert e3.cumple
    assert not est.cumple


def test_dorado_a_mano_de_E2_estatico_con_la_zapata_de_1_40(tanteo):
    """
    Con 1.40 m (talon 1.15 m): N = 71.710 kN/m, M_e = 54.822 kN·m/m,
    e = 0.70 - (54.822 - 33.805)/71.710 = 0.4069 m <= B/3 = 0.4667 m.
    """
    N, _H, M_e, M_v = _resistencia_minimos(1.40)
    entorno = _con_aleros(tanteo, replace(ALEROS, ancho_zapata=1.40))
    e2 = _v(M9.estabilidad_del_alero(entorno, EST), "E2-LRFD")
    assert e2.valor_obtenido == pytest.approx(0.70 - (M_e - M_v) / N,
                                              rel=REL)
    assert e2.cumple


def test_sin_aleros_o_de_gravedad_no_hay_muro_que_verificar(tanteo):
    from src.modelos import DatoInvalidoError
    with pytest.raises(DatoInvalidoError):
        M9.estabilidad_del_alero(tanteo, EST)
    assert not M9.alero_verificable_como_muro(tanteo)
    assert M9.alero_verificable_como_muro(_con_aleros(tanteo))
    gravedad = replace(_con_aleros(tanteo), geometria=replace(
        _con_aleros(tanteo).geometria, tipo=M9.TIPO_GRAVEDAD))
    assert not M9.alero_verificable_como_muro(gravedad)


def test_la_franja_del_arranque_es_la_seccion_de_VE6_sin_el_FS_del_cabezal(
        tanteo):
    """La franja es `entorno_de_la_seccion_del_alero` en f = 0, sin el FS
    declarado de E4 y E5, que es del cabezal y no del alero."""
    entorno = replace(_con_aleros(tanteo),
                      estabilidad_global={"E4": {"FS": 1.6}})
    franja = M9.franja_del_arranque_del_alero(entorno)
    seccion = M9.entorno_de_la_seccion_del_alero(entorno, 0.0)
    assert franja.geometria == seccion.geometria
    assert franja.cota_relleno == pytest.approx(seccion.cota_relleno,
                                                abs=TOL)
    assert franja.estabilidad_global is None
    assert franja.geometria.H == pytest.approx(H_FUSTE, abs=TOL)
    assert franja.geometria.ancho_punta == pytest.approx(0.0, abs=TOL)


def test_integrar_la_estabilidad_de_los_aleros_al_cabezal(tanteo):
    """
    Las filas del alero se suman a las del cabezal, el paso del dimensionado
    va primero, la zapata de los aleros cambia en su geometria con su
    origen, y una sola condicion evaluada se avisa.
    """
    from src.modelos import CabezalDelPunto, ORIGEN_DIMENSION_ESTABILIDAD
    from src.modelos import ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA
    entorno = _con_aleros(tanteo)
    g = entorno.geometria
    salida = replace(g, extremo="salida")
    cabezal = CabezalDelPunto(id_punto="T-00", embocadura=None, entrada=g,
                              salida=salida, verificaciones=())
    d = M9.dimensionar_zapata_del_alero(entorno)
    est = M9.estabilidad_del_alero(
        _con_aleros(tanteo, replace(ALEROS, ancho_zapata=d.ancho)), EST)
    c = M9.integrar_estabilidad_de_aleros(cabezal, [est], [d])
    assert c.estabilidad_aleros == (est,)
    assert {v.codigo for v in est.verificaciones} <= {
        v.codigo for v in c.verificaciones}
    assert c.pasos[0] is d.paso
    assert c.entrada.aleros.ancho_zapata == pytest.approx(d.ancho, abs=TOL)
    assert c.salida.aleros.ancho_zapata == pytest.approx(1.20, abs=TOL)
    dim = next(x for x in c.entrada.dimensiones
               if x.nombre == M9.DIMENSION_ZAPATA_ALEROS)
    # solo la estatica se evaluo: el origen lo dice, y un aviso tambien
    assert dim.origen == ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA
    assert dim.origen != ORIGEN_DIMENSION_ESTABILIDAD
    assert any("SOLO en la condicion estatico" in a and "Aleros" in a
               for a in c.avisos)
    assert c.intentos_de_zapata_aleros == d.intentos


# ---------------------------------------------------------------------------
# 2. La zapata del alero, dimensionada por estabilidad
# ---------------------------------------------------------------------------

def _sin_sismo(monkeypatch):
    """La condicion sismica no evaluable: el dimensionamiento sigue con lo
    evaluable (como el del cabezal) y el dorado estatico se lee solo."""
    def falta():
        raise CriterioPendienteError("PGA_roca_B", "de prueba")
    monkeypatch.setattr(M9, "cadena_sismica", falta)


def test_dorado_a_mano_del_ancho_con_la_condicion_estatica(tanteo,
                                                           monkeypatch):
    """
    Paso 0.10 m y tope 1.5·H_c = 3.60 m (valor de archivo). A mano con
    `_resistencia_minimos`: 1.20 y 1.30 m no cumplen E2 (e = 0.4745 y
    0.4385 m frente a 0.40 y 0.4333 m); 1.40 m si. E1 y E3 cumplen con
    1.40 m (medido; E3 ya con 1.20 m, dorado arriba).
    """
    _sin_sismo(monkeypatch)
    for B, cumple in ((1.20, False), (1.30, False), (1.40, True)):
        N, _H, M_e, M_v = _resistencia_minimos(B)
        assert (B / 2 - (M_e - M_v) / N <= B / 3) is cumple
    d = M9.dimensionar_zapata_del_alero(_con_aleros(tanteo))
    assert d.ancho == pytest.approx(1.40, abs=TOL)
    assert d.cumple and not d.al_tope
    assert [i.B for i in d.intentos] == pytest.approx([1.20, 1.30, 1.40],
                                                      abs=TOL)
    assert [i.cumple for i in d.intentos] == [False, False, True]
    assert d.paso.codigo == "9.3.d.e.alero"
    assert "alero" in d.paso.que
    assert d.paso.resultado.valor == pytest.approx(1.40, abs=TOL)
    assert not d.avisos


def test_con_las_dos_condiciones_el_ancho_es_el_primero_que_cumple(tanteo):
    d = M9.dimensionar_zapata_del_alero(_con_aleros(tanteo))
    assert d.cumple
    B = d.ancho
    paso_m = ca.valor("dimensionamiento_zapata_cabezal")["paso_m"]
    k = (B - ALEROS.ancho_zapata) / paso_m
    assert k == pytest.approx(round(k), abs=TOL)
    con = _con_aleros(tanteo, replace(ALEROS, ancho_zapata=B))
    sin = _con_aleros(tanteo, replace(ALEROS, ancho_zapata=B - paso_m))
    assert all(M9.estabilidad_del_alero(con, c).cumple for c in (EST, SIS))
    assert not all(M9.estabilidad_del_alero(sin, c).cumple
                   for c in (EST, SIS))
    # el bajo sismo es el que pide mas: con solo la estatica bastaban 1.40
    assert B > 1.40


def test_al_tope_la_zapata_del_alero_es_no_factible(tanteo):
    """
    Datos de prueba dentro de la ventana del criterio: paso 0.20 m y tope
    1.0·H_c = 2.40 m, con un suelo de fundacion de phi = 20 grados. Se
    prueban 1.40 a 2.40 m y ninguno cumple (E1 no alcanza); 2.60 m pasaria
    el tope. Queda el mayor ancho probado, 2.40 m, NO FACTIBLE con estos
    criterios, sin proponer dentellon ni pilotes.
    """
    ca.establecer_valor_dinamico("dimensionamiento_zapata_cabezal",
                                 {"paso_m": 0.20, "fraccion_ancho_max": 1.0})
    entorno = _con_aleros(tanteo)
    entorno = replace(entorno, suelo=dict(entorno.suelo, phi_grados=20.0))
    d = M9.dimensionar_zapata_del_alero(entorno)
    assert not d.cumple and d.al_tope
    assert d.ancho == pytest.approx(1.0 * H_C, abs=TOL)
    assert [i.B for i in d.intentos] == pytest.approx(
        [1.20, 1.40, 1.60, 1.80, 2.00, 2.20, 2.40], abs=TOL)
    assert len(d.avisos) == 1
    aviso = d.avisos[0]
    assert "NO FACTIBLE con estos criterios" in aviso and "alero" in aviso
    assert "dentellon" not in aviso.lower() and "pilote" not in aviso.lower()


def test_lo_que_cumple_o_lo_declarado_no_se_dimensiona(tanteo):
    ancho = _con_aleros(tanteo, replace(ALEROS, ancho_zapata=2.0))
    assert M9.dimensionar_zapata_del_alero(ancho) is None
    assert M9.dimensionar_zapata_del_alero(_con_aleros(tanteo),
                                           declarado=True) is None


def test_sin_el_criterio_el_dimensionamiento_se_detiene(tanteo):
    from tests.apoyo.criterios import sin_valor
    with sin_valor("dimensionamiento_zapata_cabezal"):
        with pytest.raises(CriterioPendienteError):
            M9.dimensionar_zapata_del_alero(_con_aleros(tanteo))


def test_incorporar_el_ancho_al_cabezal(tanteo):
    """La geometria del alero lleva el ancho nuevo con su origen."""
    from src.modelos import ORIGEN_DIMENSION_ESTABILIDAD
    entorno = _con_aleros(tanteo)
    g = M9.con_zapata_del_alero(entorno.geometria, 1.70)
    assert g.aleros.ancho_zapata == pytest.approx(1.70, abs=TOL)
    dim = next(d for d in g.dimensiones
               if d.nombre == M9.DIMENSION_ZAPATA_ALEROS)
    assert dim.origen == ORIGEN_DIMENSION_ESTABILIDAD
    assert dim.valor == pytest.approx(1.70, abs=TOL)
    # lo demas del cabezal no se mueve
    assert g.B == entorno.geometria.B
    assert g.aleros.espesor == entorno.geometria.aleros.espesor


# ---------------------------------------------------------------------------
# 3. El armado de la zapata del alero
# ---------------------------------------------------------------------------

def test_la_zapata_del_alero_se_arma_como_la_del_cabezal(tanteo):
    entorno = _con_aleros(tanteo)
    piezas = M9.armar_elemento(entorno, ELEMENTO_ZAPATA_ALEROS)
    assert [p.clave for p in piezas] == [SECCION_TALON_ALERO]
    (talon,) = piezas
    assert talon.elemento == ELEMENTO_ZAPATA_ALEROS
    assert talon.espesor == pytest.approx(E_Z, abs=TOL)
    franja = M9.entorno_de_la_seccion_del_alero(entorno, 0.0)
    propias = M9.solicitaciones_de_resistencia(franja)["secciones"][
        SECCION_TALON]
    assert [s.M_u for s in talon.solicitaciones] == pytest.approx(
        [s.M_u for s in propias], abs=TOL)
    codigos = {v.codigo for v in talon.verificaciones}
    assert {"A1.talon_alero.e", "A2.talon_alero.e"} <= codigos
    assert ELEMENTO_ZAPATA_ALEROS in M9.ELEMENTOS_ARMADOS
    # sin aleros no hay nada que armar
    assert M9.armar_elemento(tanteo, ELEMENTO_ZAPATA_ALEROS) == ()


def test_dorado_a_mano_del_momento_del_talon_del_alero(tanteo):
    """
    Talon por el peso entero ('momento_talon_cabezal' = 'peso_entero',
    AASHTO 11.6.1.2), muro que cede, Resistencia I (maximos), en la cara del
    alero (x = 0.25 m), talon de 0.95 m:

        M_u = (1.35·EV + 1.75·LS.v)·0.475 + 1.50·EH.v·0.95
              + 1.25·gamma_c·0.37·0.95²/2
            = (1.35·34.713 + 1.75·10.424)·0.475 + 1.50·5.2958·0.95
              + 1.25·23.56·0.37·0.45125 = 43.39 kN·m/m
    """
    ca.establecer_valor_dinamico("momento_talon_cabezal", "peso_entero")
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 "cedente")
    c = _franja_a_mano(1.20)
    t = 1.20 - E_AL
    M_u = ((1.35 * c["EV.talon"][0] + 1.75 * c["LS.v"][0]) * t / 2
           + 1.50 * EH_V * t + 1.25 * GAMMA_C * E_Z * t ** 2 / 2)
    (talon,) = M9.armar_elemento(_con_aleros(tanteo), ELEMENTO_ZAPATA_ALEROS)
    resistencia = [s for s in talon.solicitaciones if s.condicion is EST
                   and s.combinacion.startswith("Resistencia I (maximos)")]
    assert resistencia
    assert resistencia[0].M_u_cedente == pytest.approx(M_u, rel=REL)


def test_el_peralte_de_la_zapata_del_alero_crece_por_el_armado_del_talon(
        tanteo):
    """
    Con una zapata de los aleros delgada (0.20 m, de prueba) el talon no se
    arma; el peralte crece con el paso del cabezal hasta el primero de la
    grilla con el que A1 a A4 y A6 del talon cumplen, y el anterior no.
    Con el de 0.37 m del tanteo ya cumple: no hay nada que dimensionar.
    """
    assert not M9.incumplidas_del_armado_de_la_zapata_del_alero(
        _con_aleros(tanteo))
    assert M9.dimensionar_peralte_del_alero(_con_aleros(tanteo)) is None
    delgada = _con_aleros(tanteo, replace(ALEROS, espesor_zapata=0.20))
    assert M9.incumplidas_del_armado_de_la_zapata_del_alero(delgada)
    d = M9.dimensionar_peralte_del_alero(delgada)
    assert d.cumple and d.espesor > 0.20
    paso_m = ca.valor("dimensionamiento_zapata_cabezal")["paso_m"]
    k = (d.espesor - 0.20) / paso_m
    assert k == pytest.approx(round(k), abs=TOL)
    con = _con_aleros(tanteo, replace(ALEROS, espesor_zapata=d.espesor))
    sin = _con_aleros(tanteo, replace(ALEROS,
                                      espesor_zapata=d.espesor - paso_m))
    assert not M9.incumplidas_del_armado_de_la_zapata_del_alero(con)
    assert M9.incumplidas_del_armado_de_la_zapata_del_alero(sin)
    assert d.paso.codigo == "9.3.e.e.alero"
    assert M9.dimensionar_peralte_del_alero(delgada, declarado=True) is None
    g = M9.con_zapata_del_alero(delgada.geometria, espesor=d.espesor)
    assert g.aleros.espesor_zapata == pytest.approx(d.espesor, abs=TOL)
    assert g.aleros.ancho_zapata == pytest.approx(1.20, abs=TOL)
    assert any(x.nombre == M9.DIMENSION_PERALTE_ZAPATA_ALEROS
               for x in g.dimensiones)


def test_el_aviso_del_alero_sin_verificar_sale_solo_si_no_se_verifico(tanteo):
    entorno = _con_aleros(tanteo)
    sin = M9.armado_del_cabezal(entorno)
    assert any("no verificado como muro" in a and "VE7-01" in a
               for a in sin.avisos)
    con = M9.armado_del_cabezal(entorno, alero_verificado=True)
    assert not any("no verificado como muro" in a for a in con.avisos)
    # la tabla trae el reparto de la zapata del alero
    assert any(f.elemento == ELEMENTO_ZAPATA_ALEROS and "cada cara"
               in f.posicion for f in con.tabla)


# ---------------------------------------------------------------------------
# 4. De punta a punta: el servicio, la memoria, el JSON y el metrado
# ---------------------------------------------------------------------------

@pytest.mark.lento
def test_el_expediente_verifica_y_arma_los_aleros():
    from cli import informe_json
    from src.modelos import ORIGEN_DIMENSION_ESTABILIDAD
    from src.modulos import M11_reporte as M11
    from tests.apoyo import validacion_integral as V
    informe = V.correr_juego(V.juego_completo())
    con_aleros = 0
    for p in informe.puntos:
        c = p.cabezal
        if c is None:
            continue
        for g in c.geometrias:
            if not (g.aleros is not None and g.tipo == M9.TIPO_VOLADIZO):
                continue
            con_aleros += 1
            propias = [e for e in c.estabilidad_aleros
                       if e.extremo == g.extremo]
            assert {e.condicion for e in propias} <= {EST, SIS}
            bloqueada = [b for b in p.bloqueos if "alero" in b.etapa
                         and g.extremo in b.etapa]
            assert propias or bloqueada
            codigos = {v.codigo for v in c.verificaciones}
            for e in propias:
                assert {v.codigo for v in e.verificaciones} <= codigos
            armado = next((a for a in c.armado if a.extremo == g.extremo),
                          None)
            if armado is not None:
                assert any(s.clave == SECCION_TALON_ALERO
                           for s in armado.secciones)
                if len(propias) == 2:
                    assert not any("no verificado como muro" in a
                                   for a in armado.avisos)
            dim = [d for d in g.dimensiones
                   if d.nombre == M9.DIMENSION_ZAPATA_ALEROS]
            if dim:
                assert dim[0].origen.startswith(
                    ORIGEN_DIMENSION_ESTABILIDAD.split(" ")[0])
                assert g.aleros.ancho_zapata == pytest.approx(dim[0].valor,
                                                              abs=TOL)
        # el metrado del acero mide la zapata de los aleros (sus dos filas);
        # el incremento por despiece es un vacio del juego: de prueba aqui.
        from src.modulos import M12_metrados as M12
        ca.establecer_valor_dinamico("incremento_acero_por_despiece", 0.10)
        try:
            acero = M12.renglones_acero_cabezales(cabezal=c)
        finally:
            ca.quitar_valor_dinamico("incremento_acero_por_despiece")
        filas = [m.simbolo for r in acero for m in r.paso.sustitucion]
        assert any(f.startswith(SECCION_TALON_ALERO + ":") for f in filas)
        assert any(f.startswith("zapata de los aleros:") for f in filas)
    assert con_aleros
    datos = informe_json(informe)
    assert any("estabilidad_aleros" in (p.get("cabezal") or {})
               for p in datos["puntos"])
    html = M11.memoria_html(informe)
    assert "Estabilidad del alero del cabezal de" in html
