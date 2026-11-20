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

# --- dictamen Fable --- Aleros SIN caida (h0 = H_f): todas las franjas son
# la del arranque, y los dorados del dimensionamiento siguen leyendose en
# ella. Con caida (`ALEROS`), las franjas difieren (seccion 5).
PLANO = replace(ALEROS, altura_final=ALEROS.altura_inicial)

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


def test_sin_aleros_no_hay_muro(tanteo):
    """Sin aleros no hay muro que verificar; con aleros, de voladizo o de
    gravedad (dictamen Fable, abierto (c)), si."""
    from src.modelos import DatoInvalidoError
    with pytest.raises(DatoInvalidoError):
        M9.estabilidad_del_alero(tanteo, EST)
    assert not M9.alero_verificable_como_muro(tanteo)
    assert M9.alero_verificable_como_muro(_con_aleros(tanteo))
    gravedad = replace(_con_aleros(tanteo), geometria=replace(
        _con_aleros(tanteo).geometria, tipo=M9.TIPO_GRAVEDAD))
    assert M9.alero_verificable_como_muro(gravedad)


def test_la_franja_del_arranque_es_la_seccion_de_VE6_sin_el_FS_del_cabezal(
        tanteo):
    """La franja es `entorno_de_la_seccion_del_alero` en f = 0, sin el FS
    declarado de E4 y E5, que es del cabezal y no del alero."""
    from tests.test_ve4a_e4e5_declarado import FS_AMBOS, _declarado
    entorno = replace(_con_aleros(tanteo),
                      estabilidad_global=_declarado(**FS_AMBOS))
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
    entorno = _con_aleros(tanteo, PLANO)
    g = entorno.geometria
    salida = replace(g, extremo="salida")
    cabezal = CabezalDelPunto(id_punto="T-00", embocadura=None, entrada=g,
                              salida=salida, verificaciones=())
    d = M9.dimensionar_zapata_del_alero(entorno)
    est = M9.estabilidad_del_alero(
        _con_aleros(tanteo, replace(PLANO, ancho_zapata=d.ancho)), EST)
    franjas = M9.paso_de_las_franjas_del_alero(entorno)
    c = M9.integrar_estabilidad_de_aleros(cabezal, [est], [d],
                                          pasos_de_franjas=[franjas])
    assert c.estabilidad_aleros == (est,)
    assert {v.codigo for v in est.verificaciones} <= {
        v.codigo for v in c.verificaciones}
    assert c.pasos[0] is franjas and c.pasos[1] is d.paso
    assert c.entrada.aleros.ancho_zapata == pytest.approx(d.ancho, abs=TOL)
    assert c.salida.aleros.ancho_zapata == pytest.approx(1.20, abs=TOL)
    dim = next(x for x in c.entrada.dimensiones
               if x.nombre == M9.DIMENSION_ZAPATA_ALEROS)
    # una de las 5 franjas x 2 condiciones: el origen lo dice, y un aviso
    assert dim.origen == ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA
    assert dim.origen != ORIGEN_DIMENSION_ESTABILIDAD
    assert any("SOLO en 1 de 10" in a and "Aleros" in a for a in c.avisos)
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
    d = M9.dimensionar_zapata_del_alero(_con_aleros(tanteo, PLANO))
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
    d = M9.dimensionar_zapata_del_alero(_con_aleros(tanteo, PLANO))
    assert d.cumple
    B = d.ancho
    paso_m = ca.valor("dimensionamiento_zapata_cabezal")["paso_m"]
    k = (B - ALEROS.ancho_zapata) / paso_m
    assert k == pytest.approx(round(k), abs=TOL)
    con = _con_aleros(tanteo, replace(PLANO, ancho_zapata=B))
    sin = _con_aleros(tanteo, replace(PLANO, ancho_zapata=B - paso_m))
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
    entorno = _con_aleros(tanteo, PLANO)
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
    entorno = _con_aleros(tanteo, PLANO)
    piezas = M9.armar_elemento(entorno, ELEMENTO_ZAPATA_ALEROS)
    # una por franja (dictamen Fable, abierto (a)); sin caida son iguales
    assert [p.clave for p in piezas] == [
        SECCION_TALON_ALERO, "talon_alero_25", "talon_alero_50",
        "talon_alero_75", "talon_alero_100"]
    assert [M9.clave_del_talon_del_alero(f) for f in
            M9.FRACCIONES_DE_ESTABILIDAD_DEL_ALERO] == [p.clave
                                                        for p in piezas]
    talon = piezas[0]
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
    talon = M9.armar_elemento(_con_aleros(tanteo),
                              ELEMENTO_ZAPATA_ALEROS)[0]
    assert talon.clave == SECCION_TALON_ALERO
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
        _con_aleros(tanteo, PLANO))
    assert M9.dimensionar_peralte_del_alero(_con_aleros(tanteo, PLANO)) is None
    delgada = _con_aleros(tanteo, replace(PLANO, espesor_zapata=0.20))
    assert M9.incumplidas_del_armado_de_la_zapata_del_alero(delgada)
    d = M9.dimensionar_peralte_del_alero(delgada)
    assert d.cumple and d.espesor > 0.20
    paso_m = ca.valor("dimensionamiento_zapata_cabezal")["paso_m"]
    k = (d.espesor - 0.20) / paso_m
    assert k == pytest.approx(round(k), abs=TOL)
    con = _con_aleros(tanteo, replace(PLANO, espesor_zapata=d.espesor))
    sin = _con_aleros(tanteo, replace(PLANO,
                                      espesor_zapata=d.espesor - paso_m))
    assert not M9.incumplidas_del_armado_de_la_zapata_del_alero(con)
    assert M9.incumplidas_del_armado_de_la_zapata_del_alero(sin)
    assert d.paso.codigo == "9.3.e.e.alero"
    # decision 5 del dictamen: la herencia de A8 escrita en la nota
    assert "A8" in d.paso.nota_del_proyecto
    assert "hereda" in d.paso.nota_del_proyecto
    assert M9.dimensionar_peralte_del_alero(delgada, declarado=True) is None
    g = M9.con_zapata_del_alero(delgada.geometria, espesor=d.espesor)
    assert g.aleros.espesor_zapata == pytest.approx(d.espesor, abs=TOL)
    assert g.aleros.ancho_zapata == pytest.approx(1.20, abs=TOL)
    assert any(x.nombre == M9.DIMENSION_PERALTE_ZAPATA_ALEROS
               for x in g.dimensiones)


def test_el_aviso_del_alero_sin_verificar_sale_solo_si_no_se_verifico(tanteo):
    entorno = _con_aleros(tanteo, PLANO)
    sin = M9.armado_del_cabezal(entorno)
    assert any("no verificado como muro" in a and "VE7-01" in a
               for a in sin.avisos)
    con = M9.armado_del_cabezal(entorno, alero_verificado=True)
    assert not any("no verificado como muro" in a for a in con.avisos)
    # la tabla trae el reparto de la zapata del alero y UN talon, el de
    # mayor acero de las franjas
    assert any(f.elemento == ELEMENTO_ZAPATA_ALEROS and "cada cara"
               in f.posicion for f in con.tabla)
    talones = [f for f in con.tabla if f.elemento == ELEMENTO_ZAPATA_ALEROS
               and "cada cara" not in f.posicion]
    assert len(talones) == 1
    secciones = [x for x in con.secciones
                 if x.elemento == ELEMENTO_ZAPATA_ALEROS]
    assert talones[0].As_adoptado == pytest.approx(
        max(x.As_adoptado for x in secciones), abs=TOL)


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
            # todas las franjas con fuste, en las dos condiciones
            assert {e.fraccion_alero for e in propias} <= set(
                M9.FRACCIONES_DE_ESTABILIDAD_DEL_ALERO)
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
                if len(propias) == 2 * len(
                        M9.FRACCIONES_DE_ESTABILIDAD_DEL_ALERO):
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


# ---------------------------------------------------------------------------
# 5. Dictamen Fable sobre VE7-01: las franjas del alero (abierto (a))
# ---------------------------------------------------------------------------
# Un terraplen de talud 2.0 (de prueba) con el borde de la plataforma a la
# altura de la corona del arranque: detras de la franja del arranque el
# relleno es horizontal y detras de las de mas adelante SUBE (el borde no
# baja con el alero), con la pendiente equivalente creciendo.

def _con_talud(tanteo, aleros=ALEROS, talud=2.0):
    return replace(_con_aleros(tanteo, aleros), talud=talud)


def test_el_sufijo_y_las_fracciones_de_las_franjas(tanteo):
    assert [M9.sufijo_de_la_franja(f)
            for f in M9.FRACCIONES_DE_ESTABILIDAD_DEL_ALERO] == [
        ".alero", ".alero.25", ".alero.50", ".alero.75", ".alero.100"]
    assert M9.fracciones_del_alero(_con_aleros(tanteo)) == (
        M9.FRACCIONES_DE_ESTABILIDAD_DEL_ALERO, ())


def test_cada_franja_lleva_sus_codigos_y_su_rotulo(tanteo):
    entorno = _con_talud(tanteo)
    est = M9.estabilidad_del_alero(entorno, EST, 0.5)
    assert est.fraccion_alero == pytest.approx(0.5, abs=TOL)
    assert len(est.verificaciones) == 6
    assert all(v.codigo.endswith(".est.e.alero.50")
               for v in est.verificaciones)
    assert all("franja a 0.5·L" in v.paso.que for v in est.verificaciones)
    assert all(p.codigo.endswith(".alero.50") for p in est.pasos)
    # la del arranque conserva los codigos de siempre (dorados intactos)
    cero = M9.estabilidad_del_alero(entorno, EST)
    assert cero.fraccion_alero == pytest.approx(0.0, abs=TOL)
    assert all(v.codigo.endswith(".est.e.alero") for v in cero.verificaciones)


def test_dorado_a_mano_la_franja_de_la_mitad_no_cumple_E2_y_la_del_arranque_si(
        tanteo):
    """
    Zapata de 1.35 m (talon 1.10 m), talud 2.0. Arranque: relleno horizontal,
    los empujes del tanteo; con `_resistencia_minimos`, e = 0.4225 m <= B/3
    = 0.45 m. Mitad: baja Δ = 0.675 m; fuste H = 2.40 - 0.37 - 0.675 =
    1.355 m; relleno hasta z_rel = 1.725 m y, sobre el talon, una cuña que
    sube min(1.10/2.0, 0.675) = 0.55 m. A mano los pesos y sus brazos (x
    desde el pie del fuste):

        DC fuste  = 0.25·1.355·gamma_c          en 0.125
        DC zapata = 1.35·0.37·gamma_c           en 0.675
        EV rect   = 1.10·(1.725 - 0.37)·gamma   en 0.25 + 0.55
        EV cuña   = 1.10·0.55/2·gamma           en 0.25 + 2·1.10/3

    y el empuje del ensamble de esa franja (K_A de la cuña de tanteo sobre
    el relleno que sube, la parte que no es geometria): e = 0.675 -
    (M_e - M_v)/N > B/3.
    """
    _B = 1.35
    entorno = _con_talud(tanteo, replace(ALEROS, ancho_zapata=_B))
    N0, _H0, Me0, Mv0 = _resistencia_minimos(_B)
    arranque = _v(M9.estabilidad_del_alero(entorno, EST), "E2-LRFD")
    assert arranque.valor_obtenido == pytest.approx(_B / 2 - (Me0 - Mv0) / N0,
                                                    rel=REL)
    assert arranque.cumple
    est = M9.estabilidad_del_alero(entorno, EST, 0.5)
    cargas = {q.codigo: q for q in est.cargas}
    t, H, z_rel, r = _B - E_AL, H_C - E_Z - 0.675, Z_REL - 0.675, 0.55
    pesos = [(E_AL * H * GAMMA_C, E_AL / 2, 0.90),
             (_B * E_Z * GAMMA_C, _B / 2, 0.90),
             (t * (z_rel - E_Z) * GAMMA, E_AL + t / 2, 1.00),
             (t * r / 2 * GAMMA, E_AL + 2 * t / 3, 1.00)]
    EV = sum(w for w, _x, _f in pesos[2:])
    assert cargas["EV.talon"].V == pytest.approx(EV, rel=REL)
    eh_v, eh_h, ls_h = cargas["EH.v"], cargas["EH.h"], cargas["LS.h"]
    N = sum(f * w for w, _x, f in pesos) + 1.50 * eh_v.V
    M_e = sum(f * w * x for w, x, f in pesos) + 1.50 * eh_v.V * eh_v.x
    M_v = 1.50 * eh_h.H * eh_h.z + 1.75 * ls_h.H * ls_h.z
    e2 = _v(est, "E2-LRFD")
    assert e2.valor_obtenido == pytest.approx(_B / 2 - (M_e - M_v) / N,
                                              rel=REL)
    assert e2.valor_admisible == pytest.approx(_B / 3, rel=REL)
    assert not e2.cumple


def test_la_zapata_crece_por_la_franja_que_rige(tanteo, monkeypatch):
    """
    Con solo la franja del arranque (aleros sin caida) la estatica pide
    1.40 m (dorado de la seccion 2); con las franjas, la de la mitad y las
    de mas adelante piden mas, y lo dicen sus codigos en los intentos.
    """
    _sin_sismo(monkeypatch)
    plano = M9.dimensionar_zapata_del_alero(_con_talud(tanteo, PLANO))
    assert plano.ancho == pytest.approx(1.40, abs=TOL)
    d = M9.dimensionar_zapata_del_alero(_con_talud(tanteo))
    assert d.ancho > plano.ancho + TOL
    en_140 = next(i for i in d.intentos
                  if i.B == pytest.approx(1.40, abs=TOL))
    assert any(".alero." in c for c in en_140.incumplidas)
    assert not any(c.endswith(".alero") for c in en_140.incumplidas)


def test_una_franja_sin_fuste_no_se_verifica_y_el_paso_lo_dice(tanteo):
    """
    Zapata de los aleros de 1.10 m de espesor (de prueba): H(f) = 2.40 -
    1.10 - 1.35·f; en la punta H(1) = -0.05 m, sin fuste.
    """
    entorno = _con_aleros(tanteo, replace(ALEROS, espesor_zapata=1.10,
                                          ancho_zapata=2.0))
    con, sin = M9.fracciones_del_alero(entorno)
    assert sin == (1,)
    assert M9.altura_del_fuste_del_alero(entorno.geometria, 1) == \
        pytest.approx(2.40 - 1.10 - 1.35, abs=TOL)
    p = M9.paso_de_las_franjas_del_alero(entorno)
    assert p.codigo == "9.3.f.e.alero"
    assert "sin fuste" in p.resultado.procedencia.lower()
    assert p.resultado.valor == len(con)


# ---------------------------------------------------------------------------
# 6. Factores de forma con la longitud del alero (abierto (b))
# ---------------------------------------------------------------------------

def test_la_franja_tiene_la_longitud_del_alero_corto(tanteo):
    franja = M9.franja_del_alero(_con_aleros(tanteo), 0.0)
    assert franja.geometria.longitud == pytest.approx(ALEROS.longitud_corto,
                                                      abs=TOL)


def test_con_forma_rige_la_menor_resistencia_phi_cero(tanteo):
    """
    Suelo cohesivo (c = 60 kPa, phi = 0, de prueba), sin inclinacion: con
    phi = 0, N_c = 5.14, N_q = 1, N_gamma = 0 (Tabla 10.6.3.1.2a-1) y la
    zapata corrida da q_n = c·N_c + gamma·D_f = 60·5.14 + 18·0.80; con la
    L del alero, s_c = 1 + B'/(5L) > 1 la sube. Rige la corrida: q_R =
    0.55·q_n (phi_b de la tabla de muros, 11.5.7).
    """
    ca.establecer_valor_dinamico("factores_inclinacion_carga_portante",
                                 "omitir")
    ca.establecer_valor_dinamico("factores_forma_profundidad_portante",
                                 M9.FORMA_CON_LONGITUD)
    entorno = _con_aleros(tanteo, replace(PLANO, ancho_zapata=2.0))
    entorno = replace(entorno, suelo={"cohesivo": True, "c_kpa": 60.0,
                                      "phi_grados": 0.0,
                                      "gamma_kn_m3": 18.0})
    est = M9.estabilidad_del_alero(entorno, EST)
    e1 = _v(est, "E1-LRFD")
    assert e1.valor_admisible == pytest.approx(
        0.55 * (60.0 * 5.14 + 18.0 * 0.80), rel=REL)
    assert "menor resistencia" in e1.paso.nota_del_proyecto.lower()
    franja = M9.franja_del_alero(entorno, 0.0)
    con_L = M9.ensamble_estabilidad(franja, EST, muro=M9.MURO_ALERO)
    assert _v(con_L, "E1-LRFD").valor_admisible > e1.valor_admisible


def test_con_forma_rige_la_menor_resistencia_phi_positivo(tanteo):
    ca.establecer_valor_dinamico("factores_forma_profundidad_portante",
                                 M9.FORMA_CON_LONGITUD)
    entorno = _con_aleros(tanteo, replace(PLANO, ancho_zapata=1.70))
    est = M9.estabilidad_del_alero(entorno, EST)
    franja = M9.franja_del_alero(entorno, 0.0)
    lecturas = [M9.ensamble_estabilidad(
        replace(franja, geometria=replace(franja.geometria, longitud=L)),
        EST, muro=M9.MURO_ALERO) for L in (math.inf, ALEROS.longitud_corto)]
    for marco in ("LRFD", "ASD"):
        assert _v(est, f"E1-{marco}").valor_admisible == pytest.approx(
            min(_v(x, f"E1-{marco}").valor_admisible for x in lecturas),
            rel=TOL)
    # la L del cabezal (3.0 m) no aparece en el alero
    textos = " ".join(str(m.procedencia) for v in est.verificaciones
                      for m in v.paso.sustitucion + (v.paso.resultado,))
    assert "L = 3.000 m" not in textos


def test_con_la_zapata_corrida_nada_cambia(tanteo):
    entorno = _con_aleros(tanteo)
    franja = M9.franja_del_alero(entorno, 0.0)
    assert [(v.valor_obtenido, v.valor_admisible) for v in sorted(
        M9.estabilidad_del_alero(entorno, EST).verificaciones,
        key=lambda v: v.codigo)] == [
        (v.valor_obtenido, v.valor_admisible) for v in sorted(
            M9.ensamble_estabilidad(franja, EST).verificaciones,
            key=lambda v: v.codigo)]


# ---------------------------------------------------------------------------
# 7. Los aleros del cabezal de GRAVEDAD (abierto (c))
# ---------------------------------------------------------------------------
# El muro de tanteo como cabezal de gravedad (corona = base = 0.30 m, punta
# 0.60 m) con aleros de 0.30 m sobre una zapata de 2.00 x 0.40 m: la franja
# del arranque es la seccion del cabezal, y sus filas son las del caso
# patron.

ALEROS_G = replace(ALEROS, espesor=0.30, ancho_zapata=2.0,
                   espesor_zapata=0.40)


def _gravedad(tanteo, aleros=ALEROS_G, **geo):
    from tests.test_t7c_cabezal_armado import _geometria
    return replace(tanteo, geometria=_geometria(
        aleros=aleros, tipo=M9.TIPO_GRAVEDAD, **geo))


def test_la_franja_de_gravedad_es_la_seccion_del_cabezal_cortada(tanteo):
    """Con el cabezal de 0.30 a 0.60 m: la franja de la mitad (H = 2.0 -
    0.675 = 1.325 m) tiene base 0.30 + 0.30·1.325/2.0 = 0.49875 m, la
    punta del cabezal y el talon 2.00 - 0.60 - 0.49875 m."""
    entorno = _gravedad(tanteo, espesor_base_muro=0.60)
    f = M9.franja_del_alero(entorno, 0.5).geometria
    assert f.H == pytest.approx(1.325, abs=TOL)
    assert f.espesor_corona == pytest.approx(0.30, abs=TOL)
    assert f.espesor_base_muro == pytest.approx(0.49875, abs=TOL)
    assert f.ancho_punta == pytest.approx(0.60, abs=TOL)
    assert f.ancho_talon == pytest.approx(2.0 - 0.60 - 0.49875, abs=TOL)
    assert M9.espesor_de_la_base_del_alero_de_gravedad(
        entorno.geometria, 1.325) == pytest.approx(0.49875, abs=TOL)


def test_dorado_a_mano_de_E2_del_alero_de_gravedad_en_el_arranque(tanteo):
    """La franja del arranque es el muro del caso patron: e = 0.1453 m
    (`CP_T7B_ESTABILIDAD`, a mano) frente a B/3."""
    est = M9.estabilidad_del_alero(_gravedad(tanteo), EST)
    e2 = _v(est, "E2-LRFD")
    assert e2.codigo == "E2-LRFD.est.e.alero"
    assert e2.valor_obtenido == pytest.approx(CPB["E2_LRFD"]["e"],
                                              abs=CPB["tolerancia"])
    assert e2.valor_admisible == pytest.approx(2.0 / 3, abs=TOL)


def test_dorado_a_mano_de_C2_del_alero_de_gravedad_en_el_arranque(tanteo):
    """
    C2 en el arranque del cuerpo (z = 0.40 m), muro que cede, fuste de 0.30
    m: W = 0.30·2.0·gamma_c sobre el centro de la seccion; empuje del suelo
    K_A·cos(delta)·gamma·2.0³/6 y de la sobrecarga K_A·gamma·h_eq·2.0²/2
    (momentos sobre la seccion). Con las cargas de servicio e = M/W y con
    las de E.060 (0,9 CM, 1,7 CE + 1,7 CV) e = 1.7·M/(0.9·W): rige la mayor
    frente a t/6 = 0.05 m.
    """
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 "cedente")
    a = M9.verificacion_ciclopea_del_alero(_gravedad(tanteo), 0.0)
    c2 = next(v for v in a.verificaciones if v.codigo.startswith("C2."))
    assert c2.codigo.endswith(".e.alero")
    K, cos_d = CPB["K_A"], EH_H / (CPB["K_A"] * GAMMA * 2.40 ** 2 / 2)
    M = (K * cos_d * GAMMA * 2.0 ** 3 / 6 + K * GAMMA * H_EQ * 2.0 ** 2 / 2)
    W = 0.30 * 2.0 * GAMMA_C
    assert c2.valor_admisible == pytest.approx(0.30 / 6, abs=TOL)
    assert c2.valor_obtenido == pytest.approx(
        max(M / W, 1.7 * M / (0.9 * W)), rel=REL)
    # C4/C5 (el material) no se repiten; el vano no se avisa
    assert not any(v.codigo.split(".")[0] in ("C4", "C5")
                   for v in a.verificaciones)
    assert not any("vano" in x for x in a.avisos)
    assert {v.codigo.split(".")[0] for v in a.verificaciones} >= {
        "C1", "C2", "C3", "C6"}


def test_el_alero_de_gravedad_no_se_arma_y_su_zapata_crece(tanteo):
    entorno = _gravedad(tanteo, aleros=replace(ALEROS_G, ancho_zapata=1.30))
    assert M9.incumplidas_del_armado_de_la_zapata_del_alero(entorno) == ()
    assert M9.dimensionar_peralte_del_alero(entorno) is None
    d = M9.dimensionar_zapata_del_alero(entorno)
    assert d is not None and d.ancho > 1.30


def test_el_metrado_del_alero_de_gravedad_es_el_trapecio(tanteo):
    """
    Fuste del alero corto de 2.5 m, h de 1.75 + 0.80 - 0.40 = 2.15 m a 0.40
    + 0.40 = 0.80 m, k = (0.60 - 0.30)/2.0 = 0.15:
    V = 2.5·[0.30·(2.15 + 0.80)/2 + 0.075·(2.15² + 2.15·0.80 + 0.80²)/3].
    """
    from src.modulos import M12_metrados as M12
    g = _gravedad(tanteo, espesor_base_muro=0.60).geometria
    partes = dict(M12.volumen_cabezal(g, 0.0))
    h1, h2 = 2.15, 0.80
    esperado = 2.5 * (0.30 * (h1 + h2) / 2
                      + 0.15 / 2 * (h1 ** 2 + h1 * h2 + h2 ** 2) / 3)
    assert partes["fuste del alero corto"] == pytest.approx(esperado,
                                                            rel=TOL)


# ---------------------------------------------------------------------------
# 8. Lo declarado (decisiones 3 y 5, abierto (d)) y E4/E5 (decision 4)
# ---------------------------------------------------------------------------

def _predimensionar(**declaradas):
    from tests.test_t7a_cabezal_geometria import _embocadura, _extremo
    return M9.predimensionar_cabezal(extremo=_extremo(),
                                     embocadura=_embocadura(), talud=2.0,
                                     declaradas=declaradas)


def test_la_zapata_propia_declarada_gana_aunque_sea_menor(tanteo):
    from src.modelos import ORIGEN_DIMENSION_DECLARADA
    g = _predimensionar(ancho_zapata_aleros_m=0.90,
                        espesor_zapata_aleros_m=0.35)
    assert g.aleros.ancho_zapata == pytest.approx(0.90, abs=TOL)
    assert g.aleros.espesor_zapata == pytest.approx(0.35, abs=TOL)
    assert g.B > 0.90
    for nombre in (M9.DIMENSION_ZAPATA_ALEROS,
                   M9.DIMENSION_PERALTE_ZAPATA_ALEROS):
        d = next(x for x in g.dimensiones if x.nombre == nombre)
        assert d.origen == ORIGEN_DIMENSION_DECLARADA
    # declarada: no se itera, y sus filas quedan como salen
    entorno = replace(_con_aleros(tanteo), geometria=replace(
        _con_aleros(tanteo).geometria, aleros=replace(
            ALEROS, ancho_zapata=0.90)))
    assert M9.dimensionar_zapata_del_alero(entorno, declarado=True) is None
    assert not M9.estabilidad_del_alero(entorno, EST).cumple


def test_un_ancho_propio_menor_que_el_alero_es_invalido():
    from src.modelos import DatoInvalidoError
    with pytest.raises(DatoInvalidoError):
        _predimensionar(ancho_zapata_aleros_m=0.20)


def test_un_espesor_propio_bajo_el_piso_no_cumple_CB6():
    g = _predimensionar(espesor_zapata_aleros_m=0.10)
    from tests.test_t7a_cabezal_geometria import _embocadura, _extremo
    filas = M9.verificar_compatibilidad_cabezal(
        geometria=g, extremo=_extremo(), embocadura=_embocadura())
    cb6 = next(v for v in filas if v.codigo == "CB6.e.alero")
    assert not cb6.cumple
    assert "CB6.e" in {v.codigo for v in filas}


def test_lo_declarado_del_cabezal_es_solo_la_partida_y_el_alero_crece(
        tanteo):
    """Con `ancho_zapata_m` del cabezal (no el propio) la franja que no cumple
    hace crecer la zapata de los aleros: `declarado` es la clave propia."""
    d = M9.dimensionar_zapata_del_alero(_con_aleros(tanteo, PLANO),
                                        declarado=False)
    assert d is not None and d.ancho > PLANO.ancho_zapata


def test_E4_E5_diferidas_son_del_cabezal_y_de_sus_aleros(tanteo):
    est = M9.ensamble_estabilidad(_con_aleros(tanteo), EST)
    assert any("del cabezal y de sus aleros" in a for a in est.avisos)
    assert any("del cabezal y de sus aleros" in p.que for p in est.pasos)
    sin = M9.ensamble_estabilidad(tanteo, EST)
    assert not any("de sus aleros" in a for a in sin.avisos)


def test_el_FS_declarado_cubre_los_aleros_solo_si_el_analisis_los_incluyo(
        tanteo):
    from tests.test_ve4a_e4e5_declarado import FS_AMBOS, _declarado
    declarada = _declarado(**FS_AMBOS)
    est = M9.ensamble_estabilidad(
        replace(_con_aleros(tanteo), estabilidad_global=declarada), EST)
    assert any("cubre los aleros solo si el analisis externo incluyo su "
               "seccion" in a for a in est.avisos)
    sin = M9.ensamble_estabilidad(
        replace(tanteo, estabilidad_global=declarada), EST)
    assert not any("cubre los aleros" in a for a in sin.avisos)
