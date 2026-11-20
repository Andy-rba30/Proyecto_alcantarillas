"""
tests/test_ve7_lote_b_portico.py
================================
VE-7, lote B, items B4, B3 y B5 sobre el portico del marco (ficha T5-07;
decision del consultor Fable, triaje VE-7, 2026-11-20).

  * B4 (T5-07 (3)): las caras que ninguna combinacion tracciona llevan el
    minimo de retraccion y temperatura de AASHTO 5.10.6 (12.11.5.3.1 lo
    manda). Oraculo: toda cara de toda seccion tiene acero (un armado o una
    fila de minimo), y el minimo de la cara sin traccion es, a mano,
    max(5.10.6 con b = h, E.060 9.7.2 por cara) -- 5.10.6 escrito en su
    unidad (in2/ft) y convertido aqui.

Los casos se arman con los helpers de `tests/test_ve5_portico_marco.py`.
"""

import math

import pytest

from src.constantes_fisicas import KIP_EN_KN, PIE_EN_METROS
from src.modulos import M8_estructural as M8
from src.modulos import M9_cabezal as M9
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.test_ve5_portico_marco import (DECLARACIONES_CAJON, _disenar,
                                          a01)  # noqa: F401  (fixture)

PULG_EN_MM = 25.4
REL_CONVERSION = 1e-9


# ===========================================================================
# B4
# ===========================================================================

def test_b4_toda_cara_de_toda_seccion_tiene_acero(a01):
    d = _disenar(a01)
    armadas = {a.clave for a in d.armados}
    con_minimo = {f.posicion.split(":", 1)[0] for f in d.minimos}
    assert d.minimos                       # hay caras sin traccion
    assert not armadas & con_minimo        # una u otra, no las dos
    for (sec, *_r) in M8.secciones_del_portico(d.geometria):
        for cara in (M8.CARA_INTERIOR, M8.CARA_EXTERIOR):
            assert f"{sec}.{cara}" in armadas | con_minimo, (sec, cara)
    assert all(f.barra is not None for f in d.minimos)
    paso = next(p for p in d.pasos if p.codigo == M8.CODIGO_PASO_PORTICO_MINIMOS)
    assert "AASHTO_LRFD_9.12.11.5.3.1" in paso.citas_textuales


def test_b4_el_minimo_es_el_de_5_10_6_o_el_de_e060(a01):
    """5.10.6 a mano en su unidad: A_s = 1.30 b h / [2 (b + h) f_y] in2/ft
    (b, h en in; f_y en ksi), con b = h por metro de seccion, acotado a
    0.11-0.60 in2/ft; E.060 9.7.2: 0.0018 b h repartido en dos caras."""
    from tests.apoyo.criterios import declarados
    d = _disenar(a01)
    t = d.geometria.t_losa_superior_m
    with declarados(DECLARACIONES_CAJON):
        fy = M9.materiales_del_armado()["fy"]            # MPa
    h_in = t * 1000 / PULG_EN_MM
    fy_ksi = fy * 1000 / KIP_EN_KN * (PULG_EN_MM / 1000) ** 2
    As_in2_ft = 1.30 * h_in * h_in / (2 * (h_in + h_in) * fy_ksi)
    As_in2_ft = min(max(As_in2_ft, 0.11), 0.60)
    As_5106 = As_in2_ft * PULG_EN_MM ** 2 / PIE_EN_METROS
    As_e060 = 0.0018 * t * 1e6 / 2
    for f in d.minimos:
        assert f.As_minimo == pytest.approx(max(As_5106, As_e060),
                                            rel=REL_CONVERSION), f.posicion
        assert f.As_requerido == pytest.approx(0.0, abs=REL_TRANSPORTE)


# ===========================================================================
# B3: el agua exterior
# ===========================================================================
# Geometria de `_disenar` (B = 2.0, H = 1.5, t = 0.20, H_rel = 1.0) y el
# paquete de A-01 (0.15): ejes a h = 1.70 m; el eje de la losa inferior a
# z_inf = 1.0 + 0.15 + 0.20 + 1.50 + 0.10 = 2.95 m bajo la rasante, el de la
# superior a z_sup = 1.25 m. Con el terreno a 1.0 m bajo la rasante, un NF a
# 0.25 m pone el agua EXACTAMENTE en el eje de la losa superior (triangulo
# entero en la pared).
GAMMA_SAT = 20.0
Z_INF, Z_SUP, H_EJES = 2.95, 1.25, 1.70
# El modelo cuenta la deformacion axial de las losas; la pendiente-deflexion
# de abajo no: el 1 % cubre esa diferencia.
REL_SIN_AXIAL = 0.01


def _con_nf(a01, nf):
    from dataclasses import replace
    return replace(a01, cota_terreno=a01.cota_rasante - 1.0,
                   NF_profundidad_m=nf)


def _con_saturado():
    return dict(DECLARACIONES_CAJON,
                peso_especifico_saturado_relleno_kn_m3=GAMMA_SAT)


def test_b3_con_el_nf_bajo_la_losa_inferior_los_numeros_son_los_de_hoy(a01):
    hoy = _disenar(a01)
    hondo = _disenar(_con_nf(a01, 5.0))      # NF a 4.0 m bajo z_inf
    assert M8.CASO_WA_EXT not in dict(hoy.casos)
    assert M8.CASO_WA_EXT not in dict(hondo.casos)
    assert hondo.envolventes == hoy.envolventes
    assert [a.As_adoptado for a in hondo.armados] == \
        [a.As_adoptado for a in hoy.armados]


def test_b3_con_el_nf_arriba_sin_el_saturado_se_detiene(a01):
    from src.modelos import CriterioPendienteError
    from tests.apoyo.criterios import sin_valor
    with sin_valor("peso_especifico_saturado_relleno_kn_m3"):
        with pytest.raises(CriterioPendienteError) as exc:
            _disenar(_con_nf(a01, 0.25))
    assert "peso_especifico_saturado_relleno_kn_m3" in str(exc.value)


def test_b3_el_momento_de_la_pared_a_mano(a01):
    """
    Pendiente-deflexion del marco cerrado simetrico con el triangulo de agua
    w0 = gamma_w (z_inf - z_NF) en las dos paredes (maximo abajo): momentos
    de empotramiento w0 h^2/20 abajo y w0 h^2/30 arriba, y en cada esquina
    la losa (rotaciones antisimetricas) responde con 2 E I_l / L. Con las
    rotaciones que alivian (phi_B, phi_T):

        (a + 2 k) phi_B - k phi_T = w0 h^2/20      a = 2 I_l / L
        -k phi_B + (a + 2 k) phi_T = w0 h^2/30     k = 2 I_p / h

    y el momento de la esquina inferior a phi_B, con traccion exterior.
    """
    from src.constantes_fisicas import GAMMA_AGUA_KN_M3
    from tests.apoyo.criterios import declarados
    d = _disenar(_con_nf(a01, 0.25), declaraciones=_con_saturado())
    g = d.geometria
    assert g.altura_ejes_m == pytest.approx(H_EJES, rel=REL_TRANSPORTE)
    w0 = GAMMA_AGUA_KN_M3 * (Z_INF - Z_SUP)
    sust = {m.simbolo: m.valor for m in d.pasos[0].sustitucion}
    assert sust["p_WA,ext"] == pytest.approx(w0, rel=REL_CONVERSION)
    L, h = g.ejes_x_m[-1], g.altura_ejes_m
    a = 2 * (g.t_losa_superior_m ** 3 / 12) / L
    k = 2 * (g.t_pared_m ** 3 / 12) / h
    F_B, F_T = w0 * h ** 2 / 20, w0 * h ** 2 / 30
    det = (a + 2 * k) ** 2 - k ** 2
    phi_B = (F_B * (a + 2 * k) + k * F_T) / det
    M_esquina = a * phi_B
    with declarados(_con_saturado()):
        casos = M8._casos_de_carga(
            punto=_con_nf(a01, 0.25), material=None,
            seccion=M8.SeccionRectangular(B=2.0, H=1.5), g=g, H_rel=1.0)[0]
    res = M8._ModeloPortico(g).resolver(casos[M8.CASO_WA_EXT])
    M_nudo = res["pared_0"][0.0][2]
    assert M_nudo == pytest.approx(-M_esquina, rel=REL_SIN_AXIAL)
    # y el caso entra al portico: la envolvente de la pared cambia
    assert M8.CASO_WA_EXT in dict(d.casos)


def test_b3_el_empuje_bajo_el_nf_es_el_sumergido(a01):
    """p_EH = k_o sigma'_v en los ejes: sobre el NF (en el eje de la losa
    superior) el seco de siempre; bajo el, + (gamma_sat - gamma_w) dz."""
    from src.constantes_fisicas import GAMMA_AGUA_KN_M3
    from tests.apoyo.criterios import declarados
    d = _disenar(_con_nf(a01, 0.25), declaraciones=_con_saturado())
    sust = {m.simbolo: m.valor for m in d.pasos[0].sustitucion}
    k0 = 1 - math.sin(math.radians(DECLARACIONES_CAJON["phi_relleno_trasdos"]))
    e_paq = a01.cota_rasante - a01.cota_subrasante
    with declarados(_con_saturado()):
        g_s, g_p, _ = M8.pesos_especificos_de_carga(piso_tubo_concreto=False)
    seco_sup = g_p * e_paq + g_s * (Z_SUP - e_paq)
    assert sust["p_EH,sup"] == pytest.approx(k0 * seco_sup, rel=REL_CONVERSION)
    assert sust["p_EH,inf"] == pytest.approx(
        k0 * (seco_sup + (GAMMA_SAT - GAMMA_AGUA_KN_M3) * (Z_INF - Z_SUP)),
        rel=REL_CONVERSION)
    assert {"AASHTO_LRFD_9.3.11.3", "MP.2.4.4.1.3#SUMERGIDO"} <= set(
        d.pasos[0].citas_textuales)


# ===========================================================================
# B5: el canto que cerraria, sin adoptarlo
# ===========================================================================

def test_b5_el_canto_impreso_declarado_cierra_el_portico(a01):
    """
    Con 0.20 m el portico de prueba no cumple (A1, A2). El bloqueo dice el
    canto; declarado, con la MISMA seccion interior y el relleno sobre la
    clave reducido en lo que crecio la losa, el portico cumple y el bloqueo
    calla.
    """
    import re
    from src.modelos import DatoInvalidoError
    d = _disenar(a01, H_rel=1.0)
    assert not d.cumple
    with pytest.raises(DatoInvalidoError) as exc:
        M8.exigir_canto_del_portico(d, a01.id)
    assert exc.value.campo == "espesor_pared_cajon"
    texto = str(exc.value)
    assert "y repetir" in texto
    X = float(re.search(r">= (\d+\.\d+) m", texto).group(1))
    assert X == pytest.approx(d.canto_que_cierra_m, rel=REL_TRANSPORTE)
    t0 = d.geometria.t_losa_superior_m
    assert X > t0
    declarado = dict(DECLARACIONES_CAJON, espesor_pared_cajon=X)
    d2 = _disenar(a01, H_rel=1.0 - (X - t0), declaraciones=declarado)
    assert d2.cumple
    assert d2.canto_que_cierra_m is None
    M8.exigir_canto_del_portico(d2, a01.id)            # no levanta


def test_b5_el_canto_anterior_de_la_grilla_no_cierra(a01):
    """El MENOR: un paso por debajo del impreso el portico no cumple."""
    d = _disenar(a01, H_rel=1.0)
    X, t0 = d.canto_que_cierra_m, d.geometria.t_losa_superior_m
    from tests.apoyo.criterios import declarados
    from src.modulos import M9_cabezal as M9_
    with declarados(DECLARACIONES_CAJON):
        paso_m = M9_._regla_de_dimensionamiento()[0]
    anterior = X - paso_m
    if anterior > t0 + REL_CONVERSION:
        declarado = dict(DECLARACIONES_CAJON, espesor_pared_cajon=anterior)
        assert not _disenar(a01, H_rel=1.0 - (anterior - t0),
                            declaraciones=declarado).cumple
    paso = next(p for p in d.pasos if p.codigo == M8.CODIGO_PASO_PORTICO_CANTO)
    assert "no se adopta" in paso.que
    # el portico que se devuelve es el de 0.20 m: no se auto-adopta
    assert d.geometria.t_pared_m == pytest.approx(t0, rel=REL_TRANSPORTE)


# ===========================================================================
# B6: el acero del portico, metrado (VE5-MET-01)
# ===========================================================================

def test_b6_el_acero_del_portico_a_mano():
    """
    El portico de prueba (una celda de 2.0 x 1.5 m, t = 0.20 m): las losas
    miden B + t = 2.20 m entre ejes y las paredes H + t = 1.70 m. Cada cara
    de cada miembro lleva la barra de mayor acero por metro de sus
    secciones; P = (1 + i)·Σ (L_eje/s)·largo·w con w de la Tabla 504-01 y
    L_eje = L·sqrt(1 + S^2).
    """
    from types import SimpleNamespace
    from src.constantes_normativas import PESO_BARRA_KG_M_EG2013
    from src.modulos import M12_metrados as M12
    from tests.apoyo.criterios import declarados
    from tests.fixtures.casos_patron import CP_FASE_8_ESTRUCTURAL as CP
    d = _disenar(CP["punto_A01"]())
    largo_a_mano = {"losa_superior_1": 2.20, "losa_inferior_1": 2.20,
                    "pared_0": 1.70, "pared_1": 1.70}
    L, S, i = 10.0, 0.01, 0.10
    L_eje = L * math.sqrt(1 + S ** 2)
    mejor = {}
    for clave, barra in ([(a.clave, a.barra) for a in d.armados]
                         + [(f.posicion.split(":", 1)[0], f.barra)
                            for f in d.minimos]):
        sec, cara = clave.rsplit(".", 1)
        miembro = next(m for m in largo_a_mano if sec.startswith(m + "_"))
        if (miembro, cara) not in mejor or \
                barra.As_provisto > mejor[(miembro, cara)].As_provisto:
            mejor[(miembro, cara)] = barra
    assert len(mejor) == 8                       # 4 miembros x 2 caras
    neto = sum((L_eje / b.espaciamiento) * largo_a_mano[m]
               * PESO_BARRA_KG_M_EG2013[b.designacion]
               for (m, _c), b in mejor.items())
    cabezal = SimpleNamespace(longitud_metrado=L, id_punto="A-01")
    with declarados(dict(DECLARACIONES_CAJON,
                         incremento_acero_por_despiece=i)):
        (r,) = M12.renglones_acero_portico(portico=d, cabezal=cabezal, S=S)
    assert r.partida == "504.A" and r.unidad == "kg"
    assert r.cantidad == pytest.approx((1 + i) * neto, rel=REL_CONVERSION)
    assert {"EG2013.504.10", "EG2013.504.01#PESOS"} <= set(
        r.paso.citas_textuales)


def test_b6_sin_el_incremento_el_acero_del_portico_se_detiene():
    from types import SimpleNamespace
    from src.modelos import CriterioPendienteError
    from src.modulos import M12_metrados as M12
    from tests.apoyo.criterios import sin_valor
    from tests.fixtures.casos_patron import CP_FASE_8_ESTRUCTURAL as CP
    d = _disenar(CP["punto_A01"]())
    with sin_valor("incremento_acero_por_despiece"):
        with pytest.raises(CriterioPendienteError):
            M12.renglones_acero_portico(
                portico=d, cabezal=SimpleNamespace(longitud_metrado=10.0,
                                                   id_punto="A-01"), S=0.01)


def test_b6_los_largos_y_los_miembros_de_la_geometria_a_mano():
    """Una celda de 2.0 x 1.5 m con t = 0.20: losas de B + t, paredes de
    H + t entre ejes; cada seccion pertenece al miembro de su prefijo."""
    from tests.fixtures.casos_patron import CP_FASE_8_ESTRUCTURAL as CP
    g = _disenar(CP["punto_A01"]()).geometria
    largos = M8.largos_de_los_miembros(g)
    assert largos == pytest.approx({"losa_superior_1": 2.20,
                                    "losa_inferior_1": 2.20,
                                    "pared_0": 1.70, "pared_1": 1.70},
                                   rel=REL_CONVERSION)
    for sec, miembro in M8.miembros_de_las_secciones(g).items():
        assert sec.startswith(miembro + "_")


# ===========================================================================
# Dictamen Fable sobre B3: el ascenso estacional (defecto 1), el nivel sobre
# la rasante (defecto 2) y la envolvente seco/sumergido (decision 3)
# ===========================================================================

def _con_terreno(a01, bajo_rasante, nf):
    from dataclasses import replace
    return replace(a01, cota_terreno=a01.cota_rasante - bajo_rasante,
                   NF_profundidad_m=nf)


def test_f1_el_ascenso_estacional_sube_el_nivel_sobre_la_losa_inferior(a01):
    """NF crudo a z = 1.0 + 2.2 = 3.2 m (bajo z_inf = 2.95: sin agua); con
    un margen de 0.5 m sube a 2.7 m y el agua exterior entra."""
    crudo = _disenar(_con_terreno(a01, 1.0, 2.2), declaraciones=_con_saturado())
    assert M8.CASO_WA_EXT not in dict(crudo.casos)
    con_margen = _disenar(_con_terreno(a01, 1.0, 2.2),
                          declaraciones=dict(_con_saturado(),
                                             margen_estacional_nf_v7_m=0.5))
    assert M8.CASO_WA_EXT in dict(con_margen.casos)
    sust = {m.simbolo: m.valor for m in con_margen.pasos[0].sustitucion}
    assert sust["z_NF"] == pytest.approx(2.7, rel=REL_CONVERSION)


def test_f1_sin_margen_el_nivel_crudo_se_avisa(a01):
    d = _disenar(_con_nf(a01, 0.25), declaraciones=_con_saturado())
    assert any("sin ascenso estacional" in a for a in d.avisos)


def test_f1_un_margen_negativo_es_invalido(a01):
    from src.modelos import DatoInvalidoError
    from src import criterios_adoptados as ca
    from tests.apoyo.criterios import con_valor
    with con_valor("margen_estacional_nf_v7_m", -0.1,
                   motivo="margen negativo, para la guardia del portico"):
        with pytest.raises(DatoInvalidoError) as exc:
            _disenar(_con_nf(a01, 0.25), declaraciones=_con_saturado())
    assert exc.value.campo == "margen_estacional_nf_v7_m"
    assert ca.valor_si_declarado("margen_estacional_nf_v7_m") is None


def test_f2_el_nivel_sobre_la_rasante_es_invalido(a01):
    from src.modelos import DatoInvalidoError
    with pytest.raises(DatoInvalidoError) as exc:
        _disenar(_con_terreno(a01, 1.0, -1.5), declaraciones=_con_saturado())
    assert exc.value.campo == "NF_profundidad_m"


def test_d3_los_dos_casos_del_relleno_sumergido_a_mano(a01):
    """
    Terreno a 0.5 m bajo la rasante y NF a 0.1 m: z_NF = 0.6 m, sobre la
    cara de la losa superior (H_total = 1.15 m): d_w = 0.55 m, todo en el
    relleno (e_paq = 0.15). w_EV,sum = F_e (gamma' - gamma_s) d_w y
    w_WA,sup = gamma_w d_w, con F_e = 1 + 0.20·1.15/2.40 (B_c = 2.0 + 2·0.20).
    """
    from src.constantes_fisicas import GAMMA_AGUA_KN_M3
    from tests.apoyo.criterios import declarados
    d = _disenar(_con_terreno(a01, 0.5, 0.1), declaraciones=_con_saturado())
    sust = {m.simbolo: m.valor for m in d.pasos[0].sustitucion}
    with declarados(_con_saturado()):
        g_s, _g_p, _ = M8.pesos_especificos_de_carga(piso_tubo_concreto=False)
    F_e = min(1 + 0.20 * 1.15 / 2.40, 1.15)
    d_w = 0.55
    assert sust["d_w"] == pytest.approx(d_w, rel=REL_CONVERSION)
    assert sust["w_EV,sum"] == pytest.approx(
        F_e * (GAMMA_SAT - GAMMA_AGUA_KN_M3 - g_s) * d_w, rel=REL_CONVERSION)
    assert sust["w_WA,sup"] == pytest.approx(GAMMA_AGUA_KN_M3 * d_w,
                                             rel=REL_CONVERSION)
    casos = dict(d.casos)
    assert M8.CASO_EV_SUM in casos and M8.CASO_WA_SUP in casos
    sumergidas = [e for e in d.envolventes if e[0].endswith(M8.SUFIJO_SUMERGIDO)]
    assert len(sumergidas) == len(d.envolventes) // 2


def test_d3_con_saturado_22_el_servicio_del_centro_supera_al_seco(a01):
    def m_servicio(d):
        return max(e.M_kNm_m for (_n, estado, filas) in d.envolventes
                   if estado == M8.ESTADO_SERVICIO
                   for e in filas if e.seccion == "losa_superior_1_centro")
    seco = _disenar(_con_terreno(a01, 0.5, None),
                    declaraciones=_con_saturado())
    pesado = dict(_con_saturado(), peso_especifico_saturado_relleno_kn_m3=22.0)
    sumergido = _disenar(_con_terreno(a01, 0.5, 0.1), declaraciones=pesado)
    assert m_servicio(sumergido) > m_servicio(seco)


def test_d3_con_el_nf_entre_losas_no_hay_casos_nuevos(a01):
    d = _disenar(_con_nf(a01, 0.25), declaraciones=_con_saturado())
    casos = dict(d.casos)
    assert M8.CASO_EV_SUM not in casos and M8.CASO_WA_SUP not in casos
    assert not any(e[0].endswith(M8.SUFIJO_SUMERGIDO) for e in d.envolventes)
