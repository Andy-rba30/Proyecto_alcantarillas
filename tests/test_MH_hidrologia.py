"""
tests/test_MH_hidrologia.py — el modulo de la Fase 1-bis contra su caso patron
==============================================================================
Las funciones de calculo de `src/modulos/MH_hidrologia.py`, una a una, contra
`CP13_HIDROLOGIA` de `tests/fixtures/casos_patron.py`.

LOS DORADOS DE CP-13 ESTAN CALCULADOS A MANO, y el fixture lo dice: el Manual
de Hidrologia no trae ejemplo numerico de ninguna de estas formulas. Cada
valor sale de la formula que la pagina imprime, con la cuenta escrita al lado
del dorado, y la tolerancia del caso es la precision con que se escribio.

La aceptacion de T-1 --el servicio, la CLI, la memoria, los años FEN, el
registro normativo-- esta en `tests/test_t1_hidrologia.py`.
"""

from __future__ import annotations

import pytest

from src import modelos
from src.modulos import MH_hidrologia as MH
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.fixtures.casos_patron import CP13_HIDROLOGIA as CP13

TOL = CP13["tolerancia"]
POBLACION = "tc_fuera_de_la_poblacion_del_metodo"
SIN_AJUSTE = "ninguno"


# ===========================================================================
# 1. Tiempo de concentracion (Tabla N 05 y ecuacion 30)
# ===========================================================================

def test_kirpich_reproduce_el_caso_patron():
    c = CP13["kirpich"]
    assert MH.tc_kirpich_min(L_m=c["L_m"], S=c["S"], ajuste=SIN_AJUSTE) \
        == pytest.approx(c["tc_min_esperado"], rel=TOL)


def test_kirpich_aplica_los_ajustes_de_la_observacion():
    c = CP13["kirpich"]
    base = MH.tc_kirpich_min(L_m=c["L_m"], S=c["S"], ajuste=SIN_AJUSTE)
    for clave, factor in c["ajustes"].items():
        assert MH.tc_kirpich_min(L_m=c["L_m"], S=c["S"], ajuste=clave) \
            == pytest.approx(factor * base, rel=REL_TRANSPORTE)
    with pytest.raises(modelos.DatoInvalidoError):
        MH.tc_kirpich_min(L_m=c["L_m"], S=c["S"], ajuste="asfalto")


@pytest.mark.parametrize("vacio", [None, ""])
def test_kirpich_sin_ajuste_declarado_es_dato_faltante(vacio):
    """
    Auditoria de T-1 (H4): «ninguno» es una clave y hay que escribirla. Una
    celda vacia no elige la fila sin factor: el factor 0.4 de una superficie
    de asfalto baja el tiempo de concentracion a menos de la mitad.
    """
    c = CP13["kirpich"]
    with pytest.raises(modelos.DatoFaltanteError) as exc:
        MH.tc_kirpich_min(L_m=c["L_m"], S=c["S"], ajuste=vacio)
    assert exc.value.campo == "ajuste_kirpich" and SIN_AJUSTE in str(exc.value)


@pytest.mark.parametrize("S", [0.0299, 0.006, 0.1001, 0.25])
def test_kirpich_fuera_de_3_a_10_por_ciento_no_se_evalua(S):
    """INF-3.1.2: en llanura Kirpich queda fuera de su rango de pendiente."""
    with pytest.raises(modelos.MetodoNoEvaluableError) as exc:
        MH.tc_kirpich_min(L_m=CP13["kirpich"]["L_m"], S=S, ajuste=SIN_AJUSTE)
    texto = str(exc.value)
    assert texto.startswith(modelos.MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA)
    assert "HDS-5" not in texto            # no se cita la fuente de otro caso
    assert "temez" in texto and "california_culverts_practice" in texto
    assert "federal_aviation_administration" in texto and POBLACION in texto


def test_kirpich_incluye_los_dos_extremos_de_su_rango():
    for S in CP13["kirpich"]["rango_S"]:
        assert MH.tc_kirpich_min(L_m=CP13["kirpich"]["L_m"], S=S,
                                 ajuste=SIN_AJUSTE) > 0


def test_california_reproduce_el_caso_patron_y_coincide_con_kirpich():
    """La tabla dice que «esencialmente es la ecuación de Kirpich»."""
    c = CP13["california"]
    tc = MH.tc_california_min(L_m=c["L_m"], H_m=c["H_m"])
    assert tc == pytest.approx(c["tc_min_esperado"], rel=TOL)
    k = CP13["kirpich"]
    cerca = c["coincide_con_kirpich_dentro_de"]
    kirpich = MH.tc_kirpich_min(L_m=k["L_m"], S=k["S"], ajuste=SIN_AJUSTE)
    assert abs(tc / kirpich - 1) < cerca


@pytest.mark.parametrize("pendiente", [0.008, 0.0299, 0.1001])
def test_california_y_kirpich_tienen_la_misma_poblacion_y_el_mismo_trato(pendiente):
    """
    Auditoria de T-1 (H6): hasta entonces Kirpich se detenia fuera de 3 a
    10 % y California no, de modo que el limite se saltaba cambiando el
    nombre del metodo. Hoy las dos miden la misma poblacion --California como
    H / L-- y las gobierna el MISMO criterio, en los dos sentidos.
    """
    L = CP13["california"]["L_m"]
    H = pendiente * L
    for llamada in (lambda: MH.tc_kirpich_min(L_m=L, S=pendiente, ajuste=SIN_AJUSTE),
                    lambda: MH.tc_california_min(L_m=L, H_m=H)):
        with pytest.raises(modelos.MetodoNoEvaluableError) as exc:
            llamada()
        assert POBLACION in str(exc.value)
        with declarados({POBLACION: MH.POBLACION_INDICADOR}):
            assert llamada() > 0
    dentro, describe, tiene = MH.poblacion_del_metodo(
        MH.TC_METODO_CALIFORNIA, pendiente=pendiente)
    assert not dentro and "3%" in describe and "pendiente" in tiene
    assert MH.poblacion_del_metodo(MH.TC_METODO_KIRPICH, pendiente=float("nan"))[0] \
        is False                                   # un NaN cae fuera


def test_la_faa_reproduce_el_caso_patron_y_no_tiene_poblacion_numerica():
    """Tabla N 05, fila de la FAA: flujo superficial, valida en llanura."""
    c = CP13["faa"]
    assert MH.tc_faa_min(C=c["C"], L_m=c["L_m"], S=c["S"]) \
        == pytest.approx(c["tc_min_esperado"], rel=TOL)
    assert MH.poblacion_del_metodo(MH.TC_METODO_FAA) is None
    assert MH.poblacion_del_metodo(MH.TC_METODO_TEMEZ) is None
    # Una pendiente de llanura, que Kirpich no admite, aqui se evalua.
    assert MH.tc_faa_min(C=c["C"], L_m=c["L_m"], S=0.002) > c["tc_min_esperado"]
    with pytest.raises(modelos.DatoInvalidoError):
        MH.tc_faa_min(C=1.1, L_m=c["L_m"], S=c["S"])


def test_la_ecuacion_de_retardo_reproduce_el_caso_patron():
    c = CP13["retardo_scs"]
    assert MH.tc_retardo_scs_min(L_m=c["L_m"], CN=c["CN"], S=c["S"],
                                 area_km2=c["area_km2"]) \
        == pytest.approx(c["tc_min_esperado"], rel=TOL)
    for CN in (0.0, 100.5):
        with pytest.raises(modelos.DatoInvalidoError):
            MH.tc_retardo_scs_min(L_m=c["L_m"], CN=CN, S=c["S"],
                                  area_km2=c["area_km2"])
    # «áreas inferiores a 800 Ha»: 8 km2 exactos quedan fuera, con el mismo
    # criterio que Kirpich.
    with pytest.raises(modelos.MetodoNoEvaluableError) as exc:
        MH.tc_retardo_scs_min(L_m=c["L_m"], CN=c["CN"], S=c["S"],
                              area_km2=c["area_max_km2"])
    assert "800 ha" in str(exc.value) and POBLACION in str(exc.value)
    with declarados({POBLACION: MH.POBLACION_INDICADOR}):
        assert MH.tc_retardo_scs_min(L_m=c["L_m"], CN=c["CN"], S=c["S"],
                                     area_km2=c["area_max_km2"]) > 0


def test_temez_reproduce_el_caso_patron_en_horas():
    c = CP13["temez"]
    assert MH.tc_temez_h(L_km=c["L_km"], S=c["S"], area_km2=c["area_km2"]) \
        == pytest.approx(c["Tc_h_esperado"], rel=TOL)


def test_temez_fuera_de_su_rango_no_se_evalua():
    """
    Una cuneta de 200 m da 0.2416 h < 0.25 h; y 770 km2 queda fuera. Aqui la
    fuente SI escribe un rango de aplicacion, y el criterio de la poblacion
    no lo relaja (auditoria de T-1, H6 iii).
    """
    c = CP13["temez"]
    fuera = c["fuera_de_rango"]
    with declarados({POBLACION: MH.POBLACION_INDICADOR}):
        with pytest.raises(modelos.MetodoNoEvaluableError):
            MH.tc_temez_h(L_km=fuera["L_km"], S=fuera["S"],
                          area_km2=fuera["area_km2"])
    with pytest.raises(modelos.MetodoNoEvaluableError) as exc:
        MH.tc_temez_h(L_km=fuera["L_km"], S=fuera["S"], area_km2=fuera["area_km2"])
    assert f"{fuera['Tc_h']:.3f}" in str(exc.value)
    assert f"{c['rango_h'][0]:g}" in str(exc.value)
    with pytest.raises(modelos.MetodoNoEvaluableError):
        MH.tc_temez_h(L_km=c["L_km"], S=c["S"], area_km2=c["area_max_km2"])
    assert MH.tc_temez_h(L_km=c["L_km"], S=c["S"],
                         area_km2=c["area_max_km2"] - c["area_km2"]) > 0


# ===========================================================================
# 2. Ajuste de frecuencia y Kolmogorov-Smirnov (num. 3.7)
# ===========================================================================

def test_gumbel_por_momentos_reproduce_el_caso_patron():
    c = CP13["gumbel"]
    for TR, esperado in c["cuantiles"]:
        assert MH.cuantil_gumbel(media=c["media"], desviacion=c["desviacion"],
                                 TR=TR) == pytest.approx(esperado, rel=TOL)


def test_normal_y_log_normal_reproducen_el_caso_patron():
    c = CP13["serie"]
    normal = MH._ajustar(c["valores"], "normal", TR=c["TR"], alfa=c["alfa"])
    parametros = dict(normal.parametros)
    assert parametros["mu"] == pytest.approx(c["media"], rel=REL_TRANSPORTE)
    assert parametros["S"] == pytest.approx(c["S"], rel=TOL)
    assert normal.P_TR_mm == pytest.approx(c["normal_P_TR"], rel=TOL)
    log = MH._ajustar(c["valores"], "lognormal_2p", TR=c["TR"], alfa=c["alfa"])
    assert log.P_TR_mm == pytest.approx(c["lognormal_P_TR"], rel=TOL)


def test_kolmogorov_smirnov_reproduce_el_caso_patron():
    c = CP13["serie"]
    a = MH._ajustar(c["valores"], "normal", TR=c["TR"], alfa=c["alfa"])
    assert a.D == pytest.approx(c["D_normal"], rel=c["tolerancia_D"])
    assert a.d_critico == pytest.approx(c["d_critico"], rel=REL_TRANSPORTE)
    assert a.acepta and a.n == len(c["valores"])
    # El orden de entrada no importa: Fo se asigna sobre la lista ordenada.
    invertida = MH._ajustar(c["valores"][::-1], "normal", TR=c["TR"], alfa=c["alfa"])
    assert invertida.D == pytest.approx(a.D, rel=REL_TRANSPORTE)
    # Y `estadistico_ks` es la misma cuenta, suelta.
    from statistics import NormalDist
    F = NormalDist(c["media"], dict(a.parametros)["S"]).cdf
    assert MH.estadistico_ks(c["valores"], F) == pytest.approx(a.D, rel=REL_TRANSPORTE)


def test_el_valor_critico_sale_de_la_tabla_o_del_cuantil_exacto():
    from src.constantes_normativas import TABLA_03_KS
    d, origen = MH.valor_critico_ks(25, 0.05)
    assert d == pytest.approx(TABLA_03_KS[25][0.05], rel=REL_TRANSPORTE)
    assert "Tabla N 03" in origen
    # n = 37 no esta tabulado: tiene que caer entre las filas 40 y 35.
    d37, origen37 = MH.valor_critico_ks(37, 0.05)
    assert TABLA_03_KS[40][0.05] < d37 < TABLA_03_KS[35][0.05]
    assert "exacto" in origen37
    # Mas alla de la tabla el valor critico sigue bajando.
    d60, _ = MH.valor_critico_ks(60, 0.05)
    assert d60 < TABLA_03_KS[40][0.05]
    # Un alfa que no es columna tampoco se interpola: cae entre sus vecinas.
    d02, _ = MH.valor_critico_ks(25, 0.02)
    assert TABLA_03_KS[25][0.05] < d02 < TABLA_03_KS[25][0.01]


def test_la_aceptacion_es_estricta_D_menor_que_d(monkeypatch):
    """«Si D<d, se acepta»: con D = d no se acepta."""
    c = CP13["serie"]
    D = MH._ajustar(c["valores"], "normal", TR=c["TR"], alfa=c["alfa"]).D
    monkeypatch.setattr(MH, "valor_critico_ks", lambda n, alfa: (D, "igual a D"))
    assert MH._ajustar(c["valores"], "normal", TR=c["TR"],
                      alfa=c["alfa"]).acepta is False


@pytest.mark.parametrize("distribucion", ["lognormal_3p", "gamma_2p", "gamma_3p",
                                          "log_pearson_3", "log_gumbel"])
def test_las_cinco_sin_estimador_impreso_no_se_evaluan(distribucion):
    """El Manual imprime su densidad y no como se estiman sus parametros."""
    c = CP13["serie"]
    with pytest.raises(modelos.MetodoNoEvaluableError) as exc:
        MH._ajustar(c["valores"], distribucion, TR=c["TR"], alfa=c["alfa"])
    assert "estimador" in str(exc.value)


def test_la_log_normal_no_se_ajusta_con_un_anio_de_cero():
    """Auditoria de T-1 (H10): 0 mm es un dato, y la log normal no lo admite."""
    with pytest.raises(modelos.MetodoNoEvaluableError) as exc:
        MH._ajustar((0.0, 12.0, 20.0, 31.0, 44.0), "lognormal_2p", TR=50, alfa=0.05)
    assert "0 mm" in str(exc.value)
    assert MH._ajustar((0.0, 12.0, 20.0, 31.0, 44.0), "gumbel", TR=50,
                       alfa=0.05).P_TR_mm > 0


def test_ajustar_e_intensidad_no_son_puertas_publicas():
    """
    Auditoria de T-1 (H12): ninguna funcion PUBLICA entrega una lluvia o una
    intensidad de diseño sin pasar por el criterio FEN. Las dos que lo
    permitian son privadas; las puertas son tres.
    """
    for nombre in ("ajustar", "intensidad_de_diseno"):
        assert not hasattr(MH, nombre)
    for nombre in ("precipitacion_de_diseno", "caudal_de_diseno",
                   "caudal_de_aporte_cuneta"):
        assert callable(getattr(MH, nombre))


def test_una_serie_sin_dispersion_es_limite_numerico():
    with pytest.raises(modelos.LimiteNumericoError):
        MH._ajustar((20.0, 20.0, 20.0), "gumbel", TR=50, alfa=0.05)
    with pytest.raises(modelos.DatoInvalidoError):
        MH._ajustar((20.0,), "gumbel", TR=50, alfa=0.05)


# ===========================================================================
# 3. Intensidad (num. 3.8.1)
# ===========================================================================

def test_dick_peschke_reproduce_el_caso_patron():
    c = CP13["dick_peschke"]
    for caso in c["casos"]:
        Pd, I = MH._intensidad(P24_mm=c["P24_mm"], d_min=caso["d_min"],
                                        relacion=MH.RELACION_DICK_PESCHKE)
        assert Pd == pytest.approx(caso["Pd_mm"], rel=TOL)
        assert I == pytest.approx(caso["I_mm_h"], rel=TOL)


def test_la_tabla_04_interpola_y_no_baja_de_una_hora():
    c = CP13["tabla_04"]
    Pd, I = MH._intensidad(P24_mm=c["P24_mm"], d_min=c["d_min"],
                                    relacion=MH.RELACION_TABLA_04)
    assert Pd == pytest.approx(c["Pd_mm"], rel=TOL)
    assert I == pytest.approx(c["I_mm_h"], rel=TOL)
    horas, k = c["fila_exacta"]
    assert MH.coeficiente_de_duracion(horas) == pytest.approx(k, rel=REL_TRANSPORTE)
    with pytest.raises(modelos.MetodoNoEvaluableError) as exc:
        MH._intensidad(P24_mm=c["P24_mm"], d_min=30,
                                relacion=MH.RELACION_TABLA_04)
    assert MH.RELACION_DICK_PESCHKE in str(exc.value)
    with pytest.raises(modelos.DatoInvalidoError):
        MH._intensidad(P24_mm=c["P24_mm"], d_min=30, relacion="otra")


def test_dick_peschke_da_mas_lluvia_que_la_tabla_04_bajo_24_horas():
    """La razon de adoptarla como valor de archivo: es el lado conservador."""
    from src.constantes_normativas import TABLA_04_COEFICIENTES_DE_DURACION as T
    from src.dominios import MINUTOS_POR_HORA
    for horas, k in T.items():
        fraccion = MH.precipitacion_dick_peschke_mm(
            P24_mm=1, d_min=MINUTOS_POR_HORA * horas)
        if horas < 24:
            assert fraccion > k, horas
        elif horas == 24:
            assert fraccion == pytest.approx(k, rel=REL_TRANSPORTE)


# ===========================================================================
# 4. Coeficiente C, metodo racional y caudal especifico
# ===========================================================================

@pytest.mark.parametrize("S,columna,laguna", [
    (0.60, "pronunciada", False), (0.50, "alta", False), (0.21, "alta", False),
    (0.20, "media", False), (0.05, "suave", False), (0.011, "suave", False),
    (0.01, "suave", True), (0.009, "despreciable", False),
])
def test_la_columna_de_la_tabla_08_sigue_los_rotulos_impresos(S, columna, laguna):
    """«> 50%», «> 20%», «> 5%», «> 1%», «< 1%»: 1 % exacto es la laguna."""
    assert MH.clase_de_pendiente(S) == (columna, laguna)


def test_el_coeficiente_se_pide_por_clave_de_fila():
    from src.constantes_normativas import TABLA_08_COEFICIENTE_DE_ESCORRENTIA as T
    C, columna, _ = MH.coeficiente_de_escorrentia(
        cobertura="cultivos", suelo="semipermeable", S=0.045)
    assert columna == "suave"
    assert C == pytest.approx(T[("cultivos", "semipermeable")]["suave"],
                              rel=REL_TRANSPORTE)
    # Una superficie vial no es fila de la Tabla N 08, y el mensaje dice
    # por donde entra.
    with pytest.raises(modelos.DatoInvalidoError) as exc:
        MH.coeficiente_de_escorrentia(cobertura="pavimento", suelo="impermeable",
                                      S=0.02)
    assert "pavimento" in str(exc.value) and "vacio" in str(exc.value)


def test_el_coeficiente_de_una_superficie_vial_reproduce_el_caso_patron():
    """
    Auditoria de T-1 (H12): la Tabla N 08 no tiene pavimento ni talud. Lo
    cubre la Table 2-2 de WSDOT [C], con su incremento por periodo de retorno
    y su tope; nunca una fila de la Tabla N 08 puesta por omision.
    """
    c = CP13["superficie_vial"]
    for superficie, TR, esperado, topado in c["casos"]:
        C, c10, incremento, tomada, en_tope = MH.coeficiente_de_superficie_vial(
            superficie=superficie, TR=TR)
        assert C == pytest.approx(esperado, rel=TOL), (superficie, TR)
        assert en_tope is topado and not TR > tomada
        assert C >= c10
    with pytest.raises(modelos.MetodoNoEvaluableError):
        MH.coeficiente_de_superficie_vial(
            superficie="pavimento", TR=c["sin_incremento_por_encima_de"] + 1)
    with pytest.raises(modelos.DatoInvalidoError):
        MH.coeficiente_de_superficie_vial(superficie="cultivos", TR=10.0)
    assert set(MH.SUPERFICIES_VIALES) == {s for s, *_ in c["casos"]}


def test_el_coeficiente_de_uniformidad_reproduce_el_caso_patron():
    """Ecuacion (31): K = 1 + Tc^1.25 / (Tc^1.25 + 14), Tc en horas."""
    for tc_h, esperado in CP13["uniformidad"]["casos"]:
        assert MH.coeficiente_de_uniformidad(tc_h) == pytest.approx(esperado, rel=TOL)
    c = CP13["racional"]
    assert MH.caudal_racional(C=c["C"], I_mm_h=c["I_mm_h"], area_km2=c["area_km2"],
                              K=c["K"]) == pytest.approx(c["Q_con_K_m3s"], rel=TOL)


def test_el_metodo_racional_reproduce_el_caso_patron():
    c = CP13["racional"]
    assert MH.caudal_racional(C=c["C"], I_mm_h=c["I_mm_h"], area_km2=c["area_km2"]) \
        == pytest.approx(c["Q_m3s"], rel=TOL)


@pytest.mark.parametrize("exceso", [0.0, 0.5, 840.0])
def test_desde_10_km2_el_metodo_racional_no_se_evalua(exceso):
    """«A<10 Km2», desigualdad estricta: 10 km2 exactos quedan fuera."""
    c = CP13["racional"]
    with pytest.raises(modelos.MetodoNoEvaluableError) as exc:
        MH.caudal_racional(C=c["C"], I_mm_h=c["I_mm_h"],
                           area_km2=c["area_limite_km2"] + exceso)
    assert "3.12.3" in str(exc.value) and "hidrograma unitario" in str(exc.value)
    assert str(exc.value).startswith(modelos.MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA)


def test_justo_por_debajo_de_10_km2_el_metodo_racional_se_evalua():
    c = CP13["racional"]
    assert MH.exigir_alcance_del_racional(c["area_km2"]) is None
    with pytest.raises(modelos.MetodoNoEvaluableError):
        MH.exigir_alcance_del_racional(float("nan"))     # un NaN cae fuera
    assert MH.caudal_racional(C=c["C"], I_mm_h=c["I_mm_h"],
                              area_km2=c["area_limite_km2"] - c["area_km2"]) > 0


def test_dos_areas_distintas_para_una_cuenca_son_dato_invalido():
    """
    Auditoria de T-1 (H8): `area_ha` fija el periodo de retorno y `area_km2`
    entra al caudal. Si difieren mas que un redondeo, el programa no elige.
    """
    from src.tolerancias import TOL_REL_AREA_ESCRITA_DOS_VECES as tol
    assert MH.exigir_areas_coherentes(area_ha=850.0, area_km2=8.5) is None
    assert MH.exigir_areas_coherentes(
        area_ha=850.0, area_km2=8.5 * (1 + tol / 2)) is None    # un redondeo
    with pytest.raises(modelos.DatoInvalidoError) as exc:
        MH.exigir_areas_coherentes(area_ha=210.0, area_km2=0.12, id_punto="A-02")
    texto = str(exc.value)
    assert "contradice a otro dato" in texto
    assert "area_ha" in texto and "area_km2" in texto and "210" in texto
    with pytest.raises(modelos.DatoInvalidoError):
        MH.exigir_areas_coherentes(area_ha=float("nan"), area_km2=8.5)


def test_el_caudal_especifico_reproduce_el_caso_del_informe():
    """INF-3.1.6: 850 ha con 1.167 m3/s son medio milimetro por hora."""
    c = CP13["caudal_especifico"]
    q, lamina = MH.caudal_especifico(Q_m3s=c["Q_m3s"], area_km2=c["area_km2"])
    assert q == pytest.approx(c["q_m3s_km2"], rel=TOL)
    assert lamina == pytest.approx(c["lamina_mm_h"], rel=TOL)
    assert MH.area_de_columna_km2(850.0) == pytest.approx(c["area_km2"],
                                                          rel=REL_TRANSPORTE)


def test_el_caudal_declarado_no_se_recalcula_y_lleva_su_contraste():
    """`caudal_declarado`: el numero entra y sale igual, con el paso de Q/A."""
    c = CP13["caudal_especifico"]
    caudal = MH.caudal_declarado(Q_m3s=c["Q_m3s"], de_donde="columna de prueba",
                                 area_km2=c["area_km2"], origen_area="de prueba")
    assert caudal.Q_m3s == pytest.approx(c["Q_m3s"], rel=REL_TRANSPORTE)
    assert caudal.origen == modelos.ORIGEN_CAUDAL_DECLARADO and not caudal.calculado
    assert caudal.leyenda == modelos.LEYENDA_CAUDAL_DECLARADO
    assert [p.codigo for p in caudal.pasos] == [MH.CODIGO_Q_ESPECIFICO]
    paso = caudal.pasos[0]
    assert paso.resultado.valor == pytest.approx(c["q_m3s_km2"], rel=TOL)
    assert paso.veredicto.tipo is modelos.TipoDeVeredicto.SIN_VEREDICTO
    assert "AVISO DE PLAUSIBILIDAD" in paso.nota_del_proyecto
    # Auditoria de T-1 (H5): del caudal declarado el programa no sabe que se
    # hizo con los años FEN, y no se lo atribuye, este declarado o no.
    assert caudal.tratamiento_fen is None
    assert MH.AVISO_FEN_DEL_CAUDAL_DECLARADO in caudal.avisos
    with declarados({MH.CRITERIO_FEN: MH.FEN_SERIE_SIN_FEN}):
        otra = MH.caudal_declarado(Q_m3s=c["Q_m3s"], de_donde="columna de prueba")
        assert otra.tratamiento_fen is None
        assert otra.avisos == caudal.avisos
    # Sin area no hay contraste que emitir, y tampoco se inventa.
    sin_area = MH.caudal_declarado(Q_m3s=c["Q_m3s"], de_donde="columna de prueba")
    assert sin_area.pasos == () and sin_area.q_especifico_m3s_km2 is None


# ===========================================================================
# 5. Los pasos de memoria de la cuenca (tc y C), sobre las cuencas de prueba
# ===========================================================================
# `tests/fixtures/hidrologia/cuencas_prueba.csv` son DATOS DE PRUEBA, NO DEL
# PROYECTO: tres cuencas sinteticas, una por metodo.

@pytest.fixture(scope="module")
def cuencas():
    from pathlib import Path
    ruta = (Path(__file__).resolve().parent / "fixtures" / "hidrologia"
            / "cuencas_prueba.csv")
    return MH.cargar_cuencas(ruta)


def test_el_paso_del_tc_lleva_metodo_cita_y_rango(cuencas):
    from src.constantes_normativas import TC_KIRPICH_RANGO_S
    from src.dominios import METROS_POR_KM, MINUTOS_POR_HORA
    tc, paso, avisos = MH.tiempo_de_concentracion(cuencas["A-02"])     # Kirpich
    c = cuencas["A-02"]
    assert paso.codigo == MH.CODIGO_TC and paso.fundamento_id == "FH.TC"
    assert paso.formula_cita_id == "MC_HHD.3.9#T05_KIRPICH"
    assert paso.umbral.valor == TC_KIRPICH_RANGO_S
    assert paso.umbral.cita_id in paso.citas_textuales
    assert paso.veredicto.tipo is modelos.TipoDeVeredicto.CUMPLE and avisos == ()
    assert paso.resultado.valor == pytest.approx(
        MH.tc_kirpich_min(L_m=c.L_cauce_m, S=c.S_cauce_cuenca,
                          ajuste=c.ajuste_kirpich), rel=REL_TRANSPORTE)
    assert tc == pytest.approx(paso.resultado.valor, rel=REL_TRANSPORTE)
    assert paso.elecciones[0].valor == MH.TC_METODO_KIRPICH
    assert paso.elecciones[0].entre == MH.METODOS_TC
    # La lectura del proyecto va IMPRESA, y sale del registro, no del modulo.
    from src.normativa import registro
    lectura = registro.construir().cita("MC_HHD.3.9#T05_KIRPICH").interpretacion.texto
    assert lectura in paso.nota_del_proyecto
    assert "S_cauce_cuenca" in lectura and "DESCRIBE" in lectura

    t = cuencas["A-01"]                                         # Temez
    tc_t, paso_t, _ = MH.tiempo_de_concentracion(t)
    assert paso_t.formula_cita_id == "MC_HHD.3.12.2.1#TC"
    assert "USO HIBRIDO" in paso_t.nota_del_proyecto
    assert tc_t == pytest.approx(
        MINUTOS_POR_HORA * MH.tc_temez_h(L_km=t.L_cauce_m / METROS_POR_KM,
                                         S=t.S_cauce_cuenca, area_km2=t.area_km2),
        rel=REL_TRANSPORTE)

    b = cuencas["B-01"]                                         # FAA
    C, _ = MH._paso_c(b, 35)
    tc_f, paso_f, _ = MH.tiempo_de_concentracion(b, C=C)
    assert paso_f.formula_cita_id == "MC_HHD.3.9#T05_FAA"
    assert paso_f.umbral is None and "SUPERFICIAL" in paso_f.nota_del_proyecto
    assert paso_f.veredicto.tipo is modelos.TipoDeVeredicto.SIN_VEREDICTO
    assert tc_f == pytest.approx(
        MH.tc_faa_min(C=C, L_m=b.L_cauce_m, S=b.S_cauce_cuenca), rel=REL_TRANSPORTE)
    with pytest.raises(modelos.DatoFaltanteError):
        MH.tiempo_de_concentracion(b)              # la FAA pide el C


def _california(cuencas, **cambios):
    from dataclasses import replace
    return replace(cuencas["A-02"], metodo_tc=MH.TC_METODO_CALIFORNIA,
                   ajuste_kirpich=None, **cambios)


def test_el_paso_de_california_juzga_la_poblacion_de_kirpich(cuencas):
    """Dentro, CUMPLE; fuera y con el criterio en «indicador», INDICADOR."""
    dentro = _california(cuencas, H_desnivel_m=108.0)       # 108 / 2400 = 4.5 %
    tc, paso, avisos = MH.tiempo_de_concentracion(dentro)
    assert paso.formula_cita_id == "MC_HHD.3.9#T05_CALIFORNIA"
    assert paso.veredicto.tipo is modelos.TipoDeVeredicto.CUMPLE and avisos == ()
    assert "MISMA poblacion" in paso.nota_del_proyecto
    fuera = _california(cuencas, H_desnivel_m=12.0)         # 0.5 %
    with pytest.raises(modelos.MetodoNoEvaluableError):
        MH.tiempo_de_concentracion(fuera)
    with declarados({POBLACION: MH.POBLACION_INDICADOR}):
        tc, paso, avisos = MH.tiempo_de_concentracion(fuera)
    assert paso.veredicto.tipo is modelos.TipoDeVeredicto.INDICADOR
    assert paso.umbral.criterio_aplicado == POBLACION
    assert len(avisos) == 1 and "EXTRAPOLADO" in avisos[0]
    assert avisos[0] in paso.nota_del_proyecto
    assert [e.clave_criterio for e in paso.elecciones] == ["", POBLACION]


def test_california_sin_desnivel_es_dato_faltante_y_no_se_deduce(cuencas):
    with pytest.raises(modelos.DatoFaltanteError) as exc:
        MH.tiempo_de_concentracion(_california(cuencas))
    assert exc.value.campo == "H_desnivel_m"


def test_la_ecuacion_de_retardo_pide_el_numero_de_curva_y_usa_S_terreno(cuencas):
    from dataclasses import replace
    base = replace(cuencas["A-02"], metodo_tc=MH.TC_METODO_RETARDO_SCS,
                   ajuste_kirpich=None)
    with pytest.raises(modelos.DatoFaltanteError) as exc:
        MH.tiempo_de_concentracion(base)
    assert exc.value.campo == "CN"
    con = replace(base, CN=75.0, S_terreno=0.09)
    tc, paso, _ = MH.tiempo_de_concentracion(con)
    assert paso.formula_cita_id == "MC_HHD.3.9#T05_SCS"
    assert tc == pytest.approx(MH.tc_retardo_scs_min(
        L_m=con.L_cauce_m, CN=75.0, S=0.09, area_km2=con.area_km2),
        rel=REL_TRANSPORTE)
    # la pendiente que entra es la del TERRENO, no la del cauce
    assert any(m.simbolo == "S" and "S_terreno" in m.procedencia
               for m in paso.sustitucion)


def test_un_metodo_que_no_es_de_la_lista_es_dato_invalido(cuencas):
    from dataclasses import replace
    with pytest.raises(modelos.DatoInvalidoError) as exc:
        MH.tiempo_de_concentracion(replace(cuencas["A-02"], metodo_tc="izzard"))
    assert exc.value.campo == "metodo_tc"


def test_el_paso_de_C_lee_la_tabla_con_la_pendiente_del_terreno(cuencas):
    """
    Auditoria de T-1 (H4): `S_terreno` es obligatoria y la Tabla N 08 no se
    lee nunca con la pendiente del cauce.
    """
    from dataclasses import replace
    from src.constantes_normativas import TABLA_08_COEFICIENTE_DE_ESCORRENTIA as T
    fila = T[("cultivos", "semipermeable")]
    C, paso = MH._paso_c(cuencas["A-02"], 35)
    assert paso.codigo == MH.CODIGO_C and paso.formula_cita_id == "MC_HHD.3.12.2#T08"
    assert paso.nota_del_proyecto == ""
    assert any("S_terreno" in m.procedencia for m in paso.sustitucion)
    assert not any("S_cauce_cuenca" in m.procedencia for m in paso.sustitucion)
    # La pendiente del cauce NO mueve el coeficiente; la del terreno si.
    C_cauce, _ = MH._paso_c(replace(cuencas["A-02"], S_cauce_cuenca=0.30), 35)
    assert C_cauce == pytest.approx(C, rel=REL_TRANSPORTE)
    C_terreno, _ = MH._paso_c(replace(cuencas["A-02"], S_terreno=0.30), 35)
    assert C_terreno == pytest.approx(fila["alta"], rel=REL_TRANSPORTE)
    assert C == pytest.approx(fila["suave"], rel=REL_TRANSPORTE)


def test_el_paso_de_C_de_una_superficie_vial_cita_su_fuente(cuencas):
    C, paso = MH._paso_c(cuencas["B-01"], 35)        # talud_de_tierra, 35 años
    caso = next(c for c in CP13["superficie_vial"]["casos"]
                if c[0] == "talud_de_tierra" and c[1] > 25 and c[1] < 50)
    assert C == pytest.approx(caso[2], rel=TOL)
    assert paso.formula_cita_id == "WSDOT_HM.2-6.2#FRECUENCIA"
    assert "WSDOT_HM.2-6.2#T2-2" in paso.citas_textuales
    assert paso.elecciones[0].clave_criterio == MH.CRITERIO_C_VIAL
    assert "no de norma peruana" in paso.nota_del_proyecto
    assert "50 años" in paso.nota_del_proyecto     # la frecuencia que se tomo
