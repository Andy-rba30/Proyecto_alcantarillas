"""
tests/test_ve4d_v8_desborde.py
==============================
VE-4d: el umbral «desborde_admitido_con_terraplen_protegido» de V8 (ficha
T7B-02 de docs/decisiones_diferidas.md). Hasta VE-4d declararlo detenía V8
con «método no evaluable»; desde VE-4d el caudal del evento extremo se
REPARTE entre el conducto (la carga de M4) y el vertedero que forma la
plataforma (HDS-5 3a ed., num. 3.1.5, Ec. 3.9, con el C_r y el k_t de la
Figura 3.11), por tanteo sobre el caudal del conducto, y «no colapsa» se
juzga con el caudal unitario sobre la plataforma frente al que la protección
del terraplén admite ('caudal_unitario_admisible_desborde_m2s' [A], sin
valor de archivo).

LOS ORÁCULOS SON DE LA FUENTE, no del módulo:

  * la Figura 3.11 se contrasta con las DOS lecturas que el propio HDS-5
    imprime en su ejemplo resuelto DG 1.5 (pag. impresa DG1.12, PDF 283):
    C_r = 2.7 con HW_r = 0.5 ft y C_r = 2.92 con HW_r = 1.5 ft, grava;
  * la Ec. 3.9 con la fila del mismo ejemplo: Q_c = 800 ft3/s, HW_r =
    0.5 ft, Q_o = 2.7 · 200 · 0.5^1.5 = 191 ft3/s;
  * el reparto con la curva del conducto que el EJEMPLO publica (Q_c contra
    EL_hi, misma pagina): con Q = 991 ft3/s el tanteo tiene que devolver
    Q_c = 800 ft3/s y HW_r = 0.5 ft;
  * y el reparto con la carga de ESTE programa (M4, Carta 8 del cajon 7 x 7
    ft) contra la solucion HY-8 que el HDS-5 imprime (pag. impresa DG1.13,
    PDF 284): con Q = 1000 ft3/s, 816.23 ft3/s por el conducto, 183.52
    ft3/s sobre la via y EL_hi = 116.49 ft. Tolerancia: la de lectura del
    proyecto (3 %, `CP_HDS5_DG1["tolerancia_de_lectura"]`).

Las cifras del ejemplo estan en `tests/fixtures/casos_patron.py::CP_HDS5_DG15`.
ROJO MEDIDO: este archivo se escribio antes que el codigo (VE-4d) y no
llegaba ni a recogerse: `KeyError: 'coeficientes_desborde_plataforma'` (el
criterio nuevo), y detras `M4.coeficiente_de_desborde`,
`M4.repartir_caudal_con_desborde` y la clave externa de la cresta.
"""

from types import SimpleNamespace

import pytest

from src import criterios_adoptados as ca
from src import modelos
from src import servicio
from src.constantes_normativas import HDS5_INLET
from src.modelos import (ConstantesHDS5, ControlGobernante,
                         CriterioPendienteError, DatoFaltanteError,
                         DatoInvalidoError, EventoExtremoDelPunto,
                         MetodoNoEvaluableError, SeccionRectangular)
from src.modulos import M4_control as M4
from src.modulos import M5_verificaciones as M5
from tests.apoyo.aproximacion import ABS_CERO
from tests.fixtures.casos_patron import (CP_HDS5_DG1, CP_HDS5_DG15,
                                         PIE_EN_METROS)

PIE = PIE_EN_METROS
PIE3 = PIE ** 3
LECTURA = CP_HDS5_DG1["tolerancia_de_lectura"]          # 3 %
COEF = ca.CRITERIOS["coeficientes_desborde_plataforma"].valor
CRITERIO_Q_ADM = "caudal_unitario_admisible_desborde_m2s"
UMBRAL = "umbral_no_colapso_evento_extremo"
DESBORDE = "desborde_admitido_con_terraplen_protegido"


# ===========================================================================
# 1. La Figura 3.11 y la Ec. 3.9, contra lo que el ejemplo imprime
# ===========================================================================

@pytest.mark.parametrize("HW_r_ft, C_r", CP_HDS5_DG15["lecturas_C_r_grava"])
def test_la_figura_digitalizada_da_las_lecturas_del_ejemplo(HW_r_ft, C_r):
    coef = M4.coeficiente_de_desborde(
        HW_r=HW_r_ft * PIE, ancho_cresta=CP_HDS5_DG15["L_r_ft"] * PIE,
        h_t=0.0, superficie=modelos.SUPERFICIE_CRESTA_GRAVA,
        coeficientes=COEF)
    assert coef.C_r == pytest.approx(C_r, abs=CP_HDS5_DG15["tolerancia_C_r"])
    assert coef.k_t == pytest.approx(1.0, abs=ABS_CERO)
    assert coef.panel == modelos.PANEL_DESBORDE_SOMERO
    assert coef.C_d_si == pytest.approx(
        COEF["conversion_cd_si"] * coef.C_r, abs=ABS_CERO)


def test_la_ecuacion_3_9_reproduce_la_fila_del_ejemplo():
    """Q_o = C_d L HW_r^1.5: 191 ft3/s con HW_r = 0.5 ft y L = 200 ft."""
    fila = CP_HDS5_DG15["fila_800"]
    Q_o, coef = M4.caudal_sobre_la_plataforma(
        HW_r=fila["HW_r_ft"] * PIE, longitud_cresta=CP_HDS5_DG15["L_ft"] * PIE,
        ancho_cresta=CP_HDS5_DG15["L_r_ft"] * PIE, h_t=0.0,
        superficie=modelos.SUPERFICIE_CRESTA_GRAVA, coeficientes=COEF)
    assert Q_o / PIE3 == pytest.approx(fila["Q_o_ft3_s"], rel=LECTURA)
    assert coef.C_r == pytest.approx(fila["C_r"],
                                     abs=CP_HDS5_DG15["tolerancia_C_r"])


def test_el_panel_lo_decide_HW_r_sobre_L_r_y_la_pavimentada_corre_mas():
    """
    Con L_r = 3 m, HW_r = 0.30 m es somero (0.10 <= 0.15) y 0.60 m profundo
    (0.20 > 0.15). A igual tirante la cresta pavimentada tiene mayor C_r que
    la de grava en los dos paneles (la figura dibuja la roja encima).
    """
    def c(HW_r, sup):
        return M4.coeficiente_de_desborde(HW_r=HW_r, ancho_cresta=3.0, h_t=0.0,
                                          superficie=sup, coeficientes=COEF)
    pav, gra = modelos.SUPERFICIE_CRESTA_PAVIMENTADA, modelos.SUPERFICIE_CRESTA_GRAVA
    assert c(0.30, pav).panel == modelos.PANEL_DESBORDE_SOMERO
    assert c(0.60, pav).panel == modelos.PANEL_DESBORDE_PROFUNDO
    for HW_r in (0.30, 0.60):
        assert c(HW_r, pav).C_r > c(HW_r, gra).C_r


def test_la_sumergencia_reduce_el_coeficiente_y_fuera_de_la_figura_se_detiene():
    """
    k_t = 1 sin agua de aguas abajo sobre la cresta, y mientras h_t/HW_r no
    llegue al inicio de la curva; baja con la sumergencia; y donde la curva
    de la Figura 3.11C termina (k_t = 0.5) el vertedero sumergido no tiene
    coeficiente: «metodo no evaluable», con el rotulo del evento extremo.
    """
    def kt(h_t, HW_r=0.30):
        return M4.coeficiente_de_desborde(
            HW_r=HW_r, ancho_cresta=10.0, h_t=h_t,
            superficie=modelos.SUPERFICIE_CRESTA_PAVIMENTADA,
            coeficientes=COEF).k_t
    assert kt(0.0) == pytest.approx(1.0, abs=ABS_CERO)
    assert kt(0.30 * 0.70) == pytest.approx(1.0, abs=ABS_CERO)
    assert 0.5 < kt(0.30 * 0.95) < kt(0.30 * 0.90) < 1.0
    with pytest.raises(MetodoNoEvaluableError) as e:
        kt(0.30 * 0.99)
    assert str(e.value).startswith(
        modelos.MOTIVO_METODO_NO_EVALUABLE_EVENTO_EXTREMO)


@pytest.mark.parametrize("HW_r, L_r", [
    (1.30, 20.0),     # somero, mas alla de los 4 ft del panel B
    (1.20, 3.50),     # profundo, HW_r/L_r = 0.34 > 0.32 del panel A
])
def test_fuera_del_dominio_de_la_figura_no_hay_coeficiente(HW_r, L_r):
    with pytest.raises(MetodoNoEvaluableError):
        M4.coeficiente_de_desborde(
            HW_r=HW_r, ancho_cresta=L_r, h_t=0.0,
            superficie=modelos.SUPERFICIE_CRESTA_GRAVA, coeficientes=COEF)


def test_una_superficie_que_la_figura_no_tiene_es_dato_invalido():
    with pytest.raises(DatoInvalidoError):
        M4.coeficiente_de_desborde(HW_r=0.3, ancho_cresta=10.0, h_t=0.0,
                                   superficie="adoquin", coeficientes=COEF)


# ===========================================================================
# 2. El reparto, contra el ejemplo DG 1.5 del HDS-5
# ===========================================================================

def _curva_publicada(Q):
    """La curva del conducto que el ejemplo imprime (EL_hi contra Q_c),
    interpolada linealmente: es el ORACULO del tanteo, no M4."""
    puntos = CP_HDS5_DG15["curva_conducto_publicada"]
    Q_ft = Q / PIE3
    for (q0, z0), (q1, z1) in zip(puntos, puntos[1:]):
        if q0 <= Q_ft <= q1:
            z = z0 + (Q_ft - q0) * (z1 - z0) / (q1 - q0)
            return SimpleNamespace(
                HW=(z - CP_HDS5_DG15["EL_i_ft"]) * PIE,
                control_gobernante=ControlGobernante.ENTRADA)
    raise AssertionError(f"fuera de la curva publicada: {Q_ft} ft3/s")


def _repartir(Q_ft, hidraulica_de, Q_min_ft=400.0):
    ej = CP_HDS5_DG15
    return M4.repartir_caudal_con_desborde(
        Q_total=Q_ft * PIE3, hidraulica_de=hidraulica_de,
        cota_entrada=ej["EL_i_ft"] * PIE, cota_cresta=ej["EL_o_ft"] * PIE,
        longitud_cresta=ej["L_ft"] * PIE, ancho_cresta=ej["L_r_ft"] * PIE,
        cota_agua_abajo=(ej["EL_i_ft"] - ej["S"] * ej["L_conducto_ft"]
                         + ej["TW_ft"]) * PIE,
        superficie=modelos.SUPERFICIE_CRESTA_GRAVA, coeficientes=COEF,
        Q_minimo=Q_min_ft * PIE3, HW_minimo=0.0)


def test_el_tanteo_reproduce_la_fila_del_ejemplo_con_su_propia_curva():
    fila = CP_HDS5_DG15["fila_800"]
    r = _repartir(fila["Q_total_ft3_s"], _curva_publicada)
    assert r.desborda
    assert r.Q_conducto / PIE3 == pytest.approx(fila["Q_c_ft3_s"], rel=LECTURA)
    assert r.HW_r / PIE == pytest.approx(fila["HW_r_ft"], rel=LECTURA)
    assert r.Q_conducto + r.Q_plataforma == pytest.approx(r.Q_total,
                                                          rel=1e-6)
    assert r.q_unitario == pytest.approx(
        r.Q_plataforma / r.longitud_cresta, rel=1e-9)
    assert r.k_t == pytest.approx(1.0, abs=ABS_CERO)


def _carga_m4_del_cajon(Q):
    """La carga de ESTE programa para el cajon 7 x 7 ft del ejemplo: control
    de entrada de la Carta 8 (cabezal, aristas en escuadra) y de salida con
    n = 0.012 y k_e = 0.5; gobierna la mayor."""
    ej = CP_HDS5_DG15
    seccion = SeccionRectangular(B=ej["B_ft"] * PIE, H=ej["D_ft"] * PIE)
    hds5 = ConstantesHDS5.desde_dict(HDS5_INLET[ej["carta"]])
    critico = M4.tirante_critico(Q, seccion)
    entrada = M4.control_entrada(Q, seccion, ej["S"], hds5, critico)
    salida = M4.control_salida(Q, seccion, ej["S"], ej["L_conducto_ft"] * PIE,
                               ej["TW_ft"] * PIE, ej["n"], ke=ej["ke"],
                               critico=critico)
    return SimpleNamespace(
        HW=max(entrada.HW, salida.HW),
        control_gobernante=(ControlGobernante.ENTRADA
                            if entrada.HW >= salida.HW
                            else ControlGobernante.SALIDA))


def test_el_reparto_con_la_carga_de_M4_reproduce_la_solucion_HY8():
    hy8 = CP_HDS5_DG15["hy8"]
    r = _repartir(hy8["Q_total_ft3_s"], _carga_m4_del_cajon)
    assert r.desborda
    assert r.Q_conducto / PIE3 == pytest.approx(hy8["Q_c_ft3_s"], rel=LECTURA)
    assert r.Q_plataforma / PIE3 == pytest.approx(hy8["Q_o_ft3_s"],
                                                  rel=LECTURA)
    altura = r.cota_embalse / PIE - CP_HDS5_DG15["EL_i_ft"]
    assert altura == pytest.approx(hy8["EL_hi_ft"] - CP_HDS5_DG15["EL_i_ft"],
                                   rel=LECTURA)
    assert r.hidraulica.control_gobernante is ControlGobernante.ENTRADA


def test_sin_alcanzar_la_cresta_no_hay_reparto():
    """Con 700 ft3/s el embalse (113.7 ft) no llega a la cresta (116 ft)."""
    r = _repartir(700.0, _curva_publicada)
    assert not r.desborda
    assert r.Q_plataforma == pytest.approx(0.0, abs=ABS_CERO)
    assert r.Q_conducto == pytest.approx(700.0 * PIE3, rel=1e-12)
    assert r.C_r is None and r.k_t is None


def test_si_la_carga_de_diseno_ya_desborda_el_tanteo_no_se_busca():
    """El reparto no baja del caudal minimo (el de diseño): si con el ya
    hay desborde, «metodo no evaluable»."""
    with pytest.raises(MetodoNoEvaluableError):
        _repartir(1000.0, _curva_publicada, Q_min_ft=850.0)


# ===========================================================================
# 3. V8 con el umbral del desborde admitido
# ===========================================================================

def _punto():
    from src.modulos import M0_carga as M0
    from tests.test_t7b_cabezal_estabilidad import CSV_EJEMPLO
    return next(p for p in M0.cargar_puntos(CSV_EJEMPLO) if p.id == "A-01")


def _reparto_de_prueba(q_unitario, desborda=True):
    """Un reparto armado a mano: V8 no recalcula, lee."""
    Q_o = q_unitario * 30.0 if desborda else 0.0
    return modelos.RepartoDelDesborde(
        Q_total=2.5, Q_conducto=2.5 - Q_o, Q_plataforma=Q_o,
        cota_embalse=44.30 if desborda else 43.80, HW_conducto=2.2,
        hidraulica=SimpleNamespace(
            HW=2.2, control_gobernante=ControlGobernante.ENTRADA,
            regimen=modelos.REGIMEN_EVENTO_A_PRESION, nota="", avisos=()),
        desborda=desborda, cota_cresta=44.20, longitud_cresta=30.0,
        ancho_cresta=9.60, HW_r=0.10 if desborda else 0.0,
        panel=modelos.PANEL_DESBORDE_SOMERO if desborda else "",
        C_r=3.0 if desborda else None, k_t=1.0 if desborda else None,
        C_d_si=1.656 if desborda else None, q_unitario=q_unitario)


def _evento(L=30.0, q_unitario=0.05, desborda=True, llamadas=None):
    def repartir(**kw):
        if llamadas is not None:
            llamadas.append(kw)
        return _reparto_de_prueba(q_unitario, desborda)
    return EventoExtremoDelPunto(
        Q_m3s=2.5, TW_m=0.5, origen="dato externo de prueba",
        cota_desborde=44.20, origen_cota_desborde="rasante (de prueba)",
        resolver=lambda seccion, material, Q=None: None,
        longitud_cresta_m=L,
        origen_longitud_cresta="`longitud_cresta_desborde_m` de prueba",
        repartir=repartir)


def _v8(evento):
    return M5.v8_evento_extremo(
        punto=_punto(),
        resultado=SimpleNamespace(Q=1.167, HW=1.042, S=0.006,
                                  control_gobernante=ControlGobernante.ENTRADA),
        material=SimpleNamespace(nombre="concreto"),
        seccion=SimpleNamespace(etiqueta=lambda: "Ø 0.90 m"), evento=evento)


def _declarar(q_adm=None):
    ca.establecer_valor_dinamico("TR_evento_extremo", 500.0)
    ca.establecer_valor_dinamico(UMBRAL, DESBORDE)
    if q_adm is not None:
        ca.establecer_valor_dinamico(CRITERIO_Q_ADM, q_adm)


def test_el_umbral_del_desborde_se_detiene_en_su_criterio_y_en_su_dato():
    _declarar()
    with pytest.raises(CriterioPendienteError) as e:
        _v8(_evento())
    assert e.value.clave == CRITERIO_Q_ADM
    ca.establecer_valor_dinamico(CRITERIO_Q_ADM, 0.20)
    with pytest.raises(DatoFaltanteError) as e:
        _v8(_evento(L=None))
    assert e.value.campo == "longitud_cresta_desborde_m"


def test_V8_cumple_si_el_caudal_unitario_no_supera_el_admisible():
    _declarar(q_adm=0.20)
    llamadas = []
    v = _v8(_evento(q_unitario=0.05, llamadas=llamadas))
    assert v.codigo == "V8" and v.cumple
    assert v.valor_obtenido == pytest.approx(0.05, abs=ABS_CERO)
    assert v.valor_admisible == pytest.approx(0.20, abs=ABS_CERO)
    assert v.criterio_aplicado == CRITERIO_Q_ADM
    assert v.paso.veredicto.margen == pytest.approx(0.15, abs=ABS_CERO)
    # V8 le entrega al servicio la superficie (de 'condicion_pavimento',
    # 'flexible' en el archivo -> pavimentada), los coeficientes de la
    # Figura 3.11 y los minimos del diseño.
    kw = llamadas[0]
    assert kw["superficie"] == modelos.SUPERFICIE_CRESTA_PAVIMENTADA
    assert kw["coeficientes"] == COEF
    assert kw["Q_minimo"] == pytest.approx(1.167, abs=ABS_CERO)
    assert kw["HW_minimo"] == pytest.approx(1.042, abs=ABS_CERO)
    v = _v8(_evento(q_unitario=0.25))
    assert not v.cumple


def test_V8_sin_desborde_cumple_con_caudal_unitario_cero():
    _declarar(q_adm=0.20)
    v = _v8(_evento(desborda=False))
    assert v.cumple
    assert v.valor_obtenido == pytest.approx(0.0, abs=ABS_CERO)


def test_la_superficie_sale_de_condicion_pavimento():
    _declarar(q_adm=0.20)
    llamadas = []
    ca.establecer_valor_dinamico("condicion_pavimento", "no_pavimentado")
    _v8(_evento(llamadas=llamadas))
    assert llamadas[0]["superficie"] == modelos.SUPERFICIE_CRESTA_GRAVA


def test_el_umbral_sin_desborde_no_cambia():
    """Con «sin_desborde_de_la_plataforma» V8 no reparte ni lee el admisible."""
    ca.establecer_valor_dinamico("TR_evento_extremo", 500.0)
    ca.establecer_valor_dinamico(UMBRAL, "sin_desborde_de_la_plataforma")
    llamadas = []
    evento = _evento(llamadas=llamadas)
    evento = EventoExtremoDelPunto(
        **{**evento.__dict__,
           "resolver": lambda seccion, material, Q=None: SimpleNamespace(
               HW=1.147, control_gobernante=ControlGobernante.ENTRADA)})
    v = _v8(evento)
    assert v.cumple and v.criterio_aplicado == UMBRAL
    assert not llamadas


# ===========================================================================
# 4. Las puertas: criterio, dato externo y pre-vuelo
# ===========================================================================

def test_los_criterios_nuevos_y_su_etiqueta():
    q = ca.CRITERIOS[CRITERIO_Q_ADM]
    assert q.valor is None and q.etiqueta == "A"
    assert q.nivel == ca.NIVEL_EXPEDIENTE
    c = ca.CRITERIOS["coeficientes_desborde_plataforma"]
    assert c.etiqueta == "C" and c.nivel == ca.NIVEL_EXPEDIENTE
    assert set(c.valor) == {"conversion_cd_si", "limite_HWr_sobre_Lr",
                            "Cr_profundo", "Cr_somero_m", "kt"}
    for curva in ("Cr_profundo", "Cr_somero_m", "kt"):
        assert set(c.valor[curva]) == set(modelos.SUPERFICIES_CRESTA)
    # El umbral ya no anuncia «no implementado».
    assert "no esta implementado" not in ca.CRITERIOS[UMBRAL].justificacion


def test_la_longitud_de_la_cresta_es_dato_externo_de_V8(tmp_path):
    clave = servicio.CLAVE_LONGITUD_CRESTA_DESBORDE
    assert clave == "longitud_cresta_desborde_m"
    assert clave in servicio.CLAVES_EXTERNAS
    assert clave in servicio.CLAVES_DE_V5_Y_V8
    assert servicio.CRITERIO_QUE_EXIGE_LA_CLAVE[clave] == UMBRAL
    assert servicio.METODO_QUE_EXIGE_LA_CLAVE[clave] == DESBORDE
    assert servicio.VERIFICACION_QUE_EXIGE_LA_CLAVE[clave] == "V8"
    import json
    ruta = tmp_path / "ext.json"
    for malo in (0.0, -5.0, "treinta"):
        ruta.write_text(json.dumps({"puntos": {"A-01": {clave: malo}}}),
                        encoding="utf-8")
        with pytest.raises(DatoInvalidoError):
            servicio.cargar_datos_externos(ruta, {})


def test_el_prevuelo_anuncia_la_cresta_solo_con_el_umbral_del_desborde():
    from src import anticipo
    from tests.test_t7b_cabezal_estabilidad import CSV_EJEMPLO
    externos = servicio.cargar_datos_externos(None, {})
    clave = servicio.CLAVE_LONGITUD_CRESTA_DESBORDE

    def faltas():
        return {f.id_punto for f in anticipo.datos_faltantes_por_punto(
            CSV_EJEMPLO, externos, servicio.ALCANCE_EXPEDIENTE)
            if f.dato == clave}
    ca.establecer_valor_dinamico("TR_evento_extremo", 500.0)
    ca.establecer_valor_dinamico(UMBRAL, "sin_desborde_de_la_plataforma")
    assert not faltas()
    ca.establecer_valor_dinamico(UMBRAL, DESBORDE)
    assert faltas() == {"A-01", "A-02", "B-01", "C-01"}


# ===========================================================================
# 5. De punta a punta por `servicio.correr`
# ===========================================================================

@pytest.mark.lento
def test_A01_con_el_desborde_admitido_reparte_y_juzga(tmp_path):
    """
    A-01 con un evento extremo que desborda el Ø 0.90 m (2.3 m3/s, DE
    PRUEBA): con «sin_desborde» MD sube de diametro; con el desborde
    admitido y un admisible holgado el Ø 0.90 m cumple V8 por el caudal
    unitario, y la memoria lleva el reparto.
    """
    from tests.test_t7b_cabezal_estabilidad import _correr_de_prueba
    extra = {"Q_evento_extremo_m3s": 2.3,
             "longitud_cresta_desborde_m": 40.0}
    _, sin = _correr_de_prueba(tmp_path, extra_a01=extra)
    _, con = _correr_de_prueba(
        tmp_path, extra_a01=extra,
        declaraciones={UMBRAL: DESBORDE, CRITERIO_Q_ADM: 1.0})
    assert sin.resultado.seccion.etiqueta() != "Ø 0.90 m"
    assert con.resultado.seccion.etiqueta() == "Ø 0.90 m"
    v8 = next(v for v in con.resultado.verificaciones if v.codigo == "V8")
    assert v8.cumple and v8.criterio_aplicado == CRITERIO_Q_ADM
    assert 0.0 < v8.valor_obtenido < 1.0
    nombres = {m.nombre for m in v8.paso.sustitucion}
    assert {"Q_conducto", "Q_plataforma", "HW_r", "C_r", "k_t",
            "L_cresta", "L_r"} <= nombres
