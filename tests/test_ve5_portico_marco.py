"""
tests/test_ve5_portico_marco.py
===============================
VE-5 (lote m8), item 1 del censo (ficha T5-07): el portico del marco se
ANALIZA y se ARMA (`M8.disenar_portico`). Tres oraculos:

  1. la SOLUCION CERRADA del marco rectangular cerrado de canto uniforme,
     cargado simetricamente (pendiente-deflexion con rotaciones antisimetri-
     cas en cada miembro: rigidez 2EI/L, momento de empotramiento w L^2/12):

        con w en las dos losas:   M_esq = (w L^2/12) / (1 + I_l h / (I_p L))
        con p en las dos paredes: M_esq = (p h^2/12) / (1 + I_p L / (I_l h))

     y el centro del miembro cargado w L^2/8 - M_esq; el otro miembro, -M_esq
     en toda su longitud. La deformacion axial no cambia nada aqui: con la
     carga simetrica las dos paredes (o las dos losas) se acortan igual;
  2. el ejemplo resuelto de MnDOT, LRFD Bridge Design Manual (sept. 2013),
     §12.5 (ejemplos_resueltos/cajon/mndot_lrfd_sec12.pdf, pags. 12-27 a
     12-36): cajon de 10 x 10 ft con cartelas de 12 in, Tabla 12.5.2 de
     momentos sin factorar por caso (EV, EH max, LL+IM);
  3. la propia tabla de combinaciones, leida del paso que el portico imprime.

TOLERANCIAS, con nombre:
  REL_CERRADA    la solucion cerrada contra el modelo, que es exacto en los
                 nudos (vector de carga consistente).
  REL_MNDOT      MnDOT modela la cartela con un canto escalonado que no
                 publica y redondea a dos decimales: 3.5 % del valor mas 1 %
                 del mayor momento del caso (la cartela pesa en las esquinas).
"""

from types import SimpleNamespace

import pytest

from src import constantes_normativas as CN
from src import servicio
from src.constantes_fisicas import KIP_EN_KN, PIE_EN_METROS
from src.modelos import (CriterioPendienteError, FormaSeccion,
                         GeometriaPortico, SeccionRectangular, TipoMaterial)
from src.modulos import M8_estructural as M8
from src.modulos.M2_material import catalogo
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados
from tests.fixtures.casos_patron import CP_FASE_8_ESTRUCTURAL as CP

REL_CERRADA = 1e-6
REL_MNDOT = 0.035
FRACCION_DEL_MAXIMO_MNDOT = 0.01

KSF_EN_KPA = KIP_EN_KN / PIE_EN_METROS ** 2
KIP_IN_POR_FT = KIP_EN_KN * 0.0254 / PIE_EN_METROS     # kN·m/m

DECLARACIONES_CAJON = {
    "embocadura_cajon": "cajon_concreto_aletas_30_75",
    "n_manning_cajon": "concreto_afinado",
    "n_celdas_cajon": 1,
    "ke_entrada_cajon": "cajon_aletas_30_75_escuadra",
    "secciones_cajon_normalizadas": ((1.50, 1.20), (2.00, 1.50)),
    "espesor_pared_cajon": 0.20,
    "phi_relleno_trasdos": 32.0,
}


def _momentos(g, cargas):
    secs = M8.secciones_del_portico(g)
    return M8._esfuerzos(M8._ModeloPortico(g).resolver(cargas), secs)


def _uniforme(t_losa, t_pared, B=2.0, H=1.5):
    return GeometriaPortico(n_celdas=1, luz_libre_m=B, altura_libre_m=H,
                            t_losa_superior_m=t_losa,
                            t_losa_inferior_m=t_losa, t_pared_m=t_pared,
                            t_tabique_m=t_pared)


# ===========================================================================
# 1. La solucion cerrada
# ===========================================================================

@pytest.mark.parametrize("t_losa, t_pared", ((0.20, 0.20), (0.30, 0.20),
                                             (0.20, 0.35)))
def test_carga_vertical_simetrica_contra_la_solucion_cerrada(t_losa, t_pared):
    g = _uniforme(t_losa, t_pared)
    L, h = g.ejes_x_m[-1], g.altura_ejes_m
    w = 30.0
    cargas = (M8._en_la_losa(g, M8.MIEMBRO_LOSA_SUPERIOR, 0.0, L, -w, -w)
              + M8._reaccion_del_suelo(g, [(0.0, L, -w, -w)]))
    M = _momentos(g, cargas)
    I_l, I_p = t_losa ** 3 / 12, t_pared ** 3 / 12
    M_esq = (w * L ** 2 / 12) / (1 + I_l * h / (I_p * L))
    # El centro de cada losa, y la pared en toda su altura (-M_esq).
    for losa in ("losa_superior_1_centro", "losa_inferior_1_centro"):
        assert M[losa][0] == pytest.approx(w * L ** 2 / 8 - M_esq,
                                           rel=REL_CERRADA)
    for pared in ("pared_0_superior", "pared_0_centro", "pared_1_inferior"):
        assert M[pared][0] == pytest.approx(-M_esq, rel=REL_CERRADA)
    # Y el cortante de la losa en la cara de la pared: w (L/2 - t_p/2).
    assert M["losa_superior_1_izquierda"][1] == pytest.approx(
        w * (L / 2 - t_pared / 2), rel=REL_CERRADA)


@pytest.mark.parametrize("t_losa, t_pared", ((0.20, 0.20), (0.30, 0.20)))
def test_empuje_uniforme_simetrico_contra_la_solucion_cerrada(t_losa, t_pared):
    g = _uniforme(t_losa, t_pared)
    L, h = g.ejes_x_m[-1], g.altura_ejes_m
    p = 12.0
    cargas = (M8._en_la_pared(g, 0, 0.0, h, p, p)
              + M8._en_la_pared(g, 1, 0.0, h, -p, -p))
    M = _momentos(g, cargas)
    I_l, I_p = t_losa ** 3 / 12, t_pared ** 3 / 12
    M_esq = (p * h ** 2 / 12) / (1 + I_p * L / (I_l * h))
    assert M["pared_0_centro"][0] == pytest.approx(p * h ** 2 / 8 - M_esq,
                                                   rel=REL_CERRADA)
    assert M["pared_1_centro"][0] == pytest.approx(p * h ** 2 / 8 - M_esq,
                                                   rel=REL_CERRADA)
    for losa in ("losa_superior_1_centro", "losa_inferior_1_derecha"):
        assert M[losa][0] == pytest.approx(-M_esq, rel=REL_CERRADA)


def test_dos_celdas_simetricas_el_tabique_no_flexa():
    """Con la carga vertical simetrica, el tabique central no se flexa y
    las dos celdas son espejo una de la otra."""
    g = GeometriaPortico(n_celdas=2, luz_libre_m=2.0, altura_libre_m=1.5,
                         t_losa_superior_m=0.25, t_losa_inferior_m=0.25,
                         t_pared_m=0.20, t_tabique_m=0.20)
    L = g.ejes_x_m[-1]
    w = 30.0
    cargas = (M8._en_la_losa(g, M8.MIEMBRO_LOSA_SUPERIOR, 0.0, L, -w, -w)
              + M8._reaccion_del_suelo(g, [(0.0, L, -w, -w)]))
    M = _momentos(g, cargas)
    escala = abs(M["losa_superior_1_centro"][0])
    for s in ("pared_1_superior", "pared_1_centro", "pared_1_inferior"):
        assert abs(M[s][0]) / escala == pytest.approx(0.0, abs=REL_CERRADA)
    assert M["losa_superior_1_centro"][0] == pytest.approx(
        M["losa_superior_2_centro"][0], rel=REL_CERRADA)
    assert M["losa_superior_1_derecha"][0] == pytest.approx(
        M["losa_superior_2_izquierda"][0], rel=REL_CERRADA)


# ===========================================================================
# 2. MnDOT §12.5: cajon de 10 x 10 ft con cartelas de 12 in
# ===========================================================================

def _mndot():
    ft = PIE_EN_METROS
    return GeometriaPortico(n_celdas=1, luz_libre_m=10 * ft,
                            altura_libre_m=10 * ft,
                            t_losa_superior_m=0.75 * ft,
                            t_losa_inferior_m=0.83 * ft,
                            t_pared_m=0.67 * ft, t_tabique_m=0.67 * ft,
                            cartela_m=1.0 * ft)


# Tabla 12.5.2 de MnDOT (kip-in por pie), en las secciones donde la cartela
# se encuentra con el canto tipico. Lo que el ejemplo publica de las LOSAS
# en el extremo para LL+IM no se compara: su carga viva no cubre la losa
# entera en todas sus posiciones, y el ejemplo no dice cuales probo.
MNDOT_EV = {"pared_0_superior": -44.97, "pared_0_centro": -39.44,
            "pared_0_inferior": -33.97, "losa_superior_1_centro": 89.03,
            "losa_superior_1_izquierda": 12.60,
            "losa_inferior_1_centro": 103.87,
            "losa_inferior_1_izquierda": 27.43}
MNDOT_EH = {"pared_0_superior": -4.84, "pared_0_centro": 63.02,
            "pared_0_inferior": -4.80, "losa_superior_1_centro": -50.54,
            "losa_superior_1_izquierda": -50.54,
            "losa_inferior_1_centro": -70.62,
            "losa_inferior_1_izquierda": -70.62}
MNDOT_LL = {"pared_0_superior": -21.57, "pared_0_centro": -18.82,
            "pared_0_inferior": -16.21, "losa_superior_1_centro": 42.49,
            "losa_inferior_1_centro": 49.57}


def _contra_mndot(M, tabla):
    maximo = max(abs(v) for v in tabla.values())
    for seccion, esperado in tabla.items():
        calculado = M[seccion][0] / KIP_IN_POR_FT
        assert abs(calculado - esperado) <= (
            REL_MNDOT * abs(esperado) + FRACCION_DEL_MAXIMO_MNDOT * maximo), (
            seccion, calculado, esperado)


def test_mndot_12_5_relleno_vertical():
    """EV = F_e gamma_s H = 1.106 x 0.120 x 6 ksf, F_e = 1 + 0.20 x 6/11.33."""
    g = _mndot()
    L = g.ejes_x_m[-1]
    w = (1 + 0.20 * 6 / 11.33) * 0.120 * 6 * KSF_EN_KPA
    cargas = (M8._en_la_losa(g, M8.MIEMBRO_LOSA_SUPERIOR, 0.0, L, -w, -w)
              + M8._reaccion_del_suelo(g, [(0.0, L, -w, -w)]))
    _contra_mndot(_momentos(g, cargas), MNDOT_EV)


def test_mndot_12_5_empuje_maximo():
    """EH max: fluido equivalente de 0.060 kcf, 0.360 ksf en la cara superior
    de la losa superior (6 ft de relleno) y 1.055 en la inferior de la losa
    inferior; lineal, llevado a los ejes de las losas."""
    g = _mndot()
    h = g.altura_ejes_m
    ft = PIE_EN_METROS
    z0, z1 = 6.0, 6.0 + 0.75 + 10.0 + 0.83

    def p(z):
        return (0.360 + (1.055 - 0.360) * (z - z0) / (z1 - z0)) * KSF_EN_KPA
    p_sup, p_inf = p(6.0 + 0.75 / 2), p(6.0 + 0.75 + 10.0 + 0.83 / 2)
    assert h == pytest.approx((10.0 + (0.75 + 0.83) / 2) * ft,
                              rel=REL_TRANSPORTE)
    cargas = (M8._en_la_pared(g, 0, 0.0, h, p_inf, p_sup)
              + M8._en_la_pared(g, 1, 0.0, h, -p_inf, -p_sup))
    _contra_mndot(_momentos(g, cargas), MNDOT_EH)


def test_mndot_12_5_carga_viva_del_tandem():
    """El tandem de MnDOT: 4 x 12.5 kip x 1.0825 x 1.2 sobre 14.57 x 11.73
    ft, un area mas larga que la luz: cubre la losa superior entera, y la
    reaccion uniforme la equilibra (12.11.2.3)."""
    g = _mndot()
    L = g.ejes_x_m[-1]
    w = 4 * 12.5 * (1 + 0.0825) * 1.2 / (14.57 * 11.73) * KSF_EN_KPA
    cargas = M8._carga_viva_en(g, w, 11.73 * PIE_EN_METROS, (0.0,), L / 2)
    _contra_mndot(_momentos(g, cargas), MNDOT_LL)


# ===========================================================================
# 3. El portico del punto: cargas, combinaciones y armado
# ===========================================================================

@pytest.fixture
def a01():
    return CP["punto_A01"]()


def _marco(declaraciones=DECLARACIONES_CAJON):
    with declarados(declaraciones):
        return catalogo(TipoMaterial.CONCRETO_REFORZADO,
                        forma=FormaSeccion.RECTANGULAR)


def _disenar(a01, H_rel=1.0, declaraciones=DECLARACIONES_CAJON, B=2.0,
             H=1.5):
    with declarados(declaraciones):
        marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                         forma=FormaSeccion.RECTANGULAR)
        return M8.disenar_portico(punto=a01, material=marco,
                                  seccion=SeccionRectangular(B=B, H=H),
                                  altura_relleno=H_rel)


def test_sin_el_angulo_de_friccion_del_relleno_el_portico_se_detiene(a01):
    """k_o = 1 - sen phi'_f (3.11.5.2): el relleno es el del cabezal, y su
    angulo es del EMS ('phi_relleno_trasdos' [A], sin valor)."""
    sin_phi = {k: v for k, v in DECLARACIONES_CAJON.items()
               if k != "phi_relleno_trasdos"}
    with pytest.raises(CriterioPendienteError) as exc:
        _disenar(a01, declaraciones=sin_phi)
    assert "phi_relleno_trasdos" in str(exc.value)


def test_el_portico_arma_sus_secciones_con_los_phi_del_cajon_in_situ(a01):
    d = _disenar(a01)
    assert d.armados and d.verificaciones
    codigos = [p.codigo for p in d.pasos]
    assert codigos[:3] == [M8.CODIGO_PASO_PORTICO_CARGAS,
                           M8.CODIGO_PASO_PORTICO_COMBINACIONES,
                           M8.CODIGO_PASO_PORTICO_ANALISIS]
    for a in d.armados:
        for s in a.solicitaciones:
            assert s.phi_flexion == pytest.approx(
                CN.PHI_FLEXION_CAJON_IN_SITU, rel=REL_TRANSPORTE)
            assert s.phi_corte == pytest.approx(CN.PHI_CORTE_CAJON_IN_SITU,
                                                rel=REL_TRANSPORTE)
        assert {v.codigo.split(".")[0] for v in a.verificaciones} >= {
            "A1", "A2", "A3", "A4"}
    claves = {a.clave for a in d.armados}
    # El centro de las losas se tracciona por dentro y las esquinas por fuera.
    assert "losa_superior_1_centro.interior" in claves
    assert "losa_inferior_1_centro.interior" in claves
    assert "pared_0_superior.exterior" in claves
    assert d.cumple == all(v.cumple for v in d.verificaciones)


def test_las_cargas_son_las_de_la_fuente(a01):
    d = _disenar(a01)
    sust = {m.simbolo: m.valor for m in d.pasos[0].sustitucion}
    assert sust["k_o"] == pytest.approx(1 - __import__("math").sin(
        __import__("math").radians(32.0)), rel=REL_CERRADA)
    assert sust["F_e"] <= CN.FE_CAJON_MAX_COMPACTADO
    assert sust["h_eq"] >= CN.SOBRECARGA_TRASDOS_PISO_MP_M
    assert sust["p_EH,inf"] > sust["p_EH,sup"] > 0
    combos = {m.simbolo: m.valor for m in d.pasos[1].sustitucion}
    assert combos["gamma_EH"] == pytest.approx(
        CN.TABLA_GAMMA_P_FILAS["EH_en_reposo"]["max"], rel=REL_TRANSPORTE)
    assert combos["gamma_EV"] == pytest.approx(
        CN.TABLA_GAMMA_P_FILAS["EV_porticos_rigidos"]["max"],
        rel=REL_TRANSPORTE)


def test_la_reduccion_de_3_11_7_solo_toca_el_positivo_de_la_losa_superior(
        a01, monkeypatch):
    """Decision del dueño: el 50 % de 3.11.7 solo en el momento positivo de
    la losa superior. Quitandola, solo cambia esa seccion y solo en la
    combinacion de horizontal minimo."""
    con = _disenar(a01)
    monkeypatch.setattr(M8._CN, "REDUCCION_EMPUJE_3_11_7", 1.0)
    sin = _disenar(a01)
    for (nombre, _e, filas_con), (_n, _e2, filas_sin) in zip(
            con.envolventes, sin.envolventes):
        for f_con, f_sin in zip(filas_con, filas_sin):
            igual = f_con.M_kNm_m == pytest.approx(f_sin.M_kNm_m,
                                                   rel=REL_CERRADA)
            if (f_con.seccion == "losa_superior_1_centro"
                    and "horizontal min" in nombre):
                assert f_con.M_kNm_m > f_sin.M_kNm_m
            else:
                assert igual, (nombre, f_con.seccion)


def test_con_relleno_somero_el_portico_carga_la_franja(a01):
    """Con menos de 2.0 ft hasta la rasante la carga viva es la de la franja
    de 4.6.2.10.2 (VE-4f), un eje por area: el tandem, dos areas a 4 ft."""
    d = _disenar(a01, H_rel=0.30)
    sust = {m.simbolo: m for m in d.pasos[0].sustitucion}
    assert "2 area(s)" in sust["P_L del tandem"].procedencia


def test_dos_celdas_arman_el_tabique(a01):
    d = _disenar(a01, declaraciones=dict(DECLARACIONES_CAJON,
                                         n_celdas_cajon=2))
    assert d.geometria.n_celdas == 2
    assert any(a.clave.startswith("pared_1_") for a in d.armados)


def test_la_etapa_del_servicio_suma_el_portico_al_punto(a01):
    """`servicio._fase_8` corre el portico detras de la demanda: sus pasos
    van con los de la Fase 8, sus verificaciones cuentan en el punto, y el
    diferido del marco cambia por el del portico."""
    marco = _marco()
    informe = servicio.InformePunto(punto=a01)
    informe.resultado = SimpleNamespace(material=marco,
                                        seccion=SeccionRectangular(B=2.0,
                                                                   H=1.5),
                                        verificaciones=())
    with declarados(DECLARACIONES_CAJON):
        servicio._fase_8(informe)
    e = informe.estructural
    assert e is not None and e.portico is not None, informe.bloqueos
    assert M8.DIFERIDO_PORTICO in e.diferido
    assert M8.DIFERIDO_MARCO not in e.diferido
    assert {v.codigo for _f, v in informe.verificaciones()} >= {
        v.codigo for v in e.portico.verificaciones}
    assert any(p.codigo == M8.CODIGO_PASO_PORTICO_ANALISIS for p in e.pasos)


def test_sin_phi_la_etapa_del_portico_se_bloquea_y_la_demanda_sigue(a01):
    marco = _marco()
    informe = servicio.InformePunto(punto=a01)
    informe.resultado = SimpleNamespace(material=marco,
                                        seccion=SeccionRectangular(B=2.0,
                                                                   H=1.5),
                                        verificaciones=())
    sin_phi = {k: v for k, v in DECLARACIONES_CAJON.items()
               if k != "phi_relleno_trasdos"}
    with declarados(sin_phi):
        servicio._fase_8(informe)
    assert informe.estructural is not None
    assert informe.estructural.demanda_marco is not None
    assert informe.estructural.portico is None
    (b,) = [b for b in informe.bloqueos
            if b.etapa == servicio.ETAPA_PORTICO_MARCO]
    assert b.criterio == "phi_relleno_trasdos"


def test_la_geometria_del_portico_es_la_del_programa(a01):
    """`geometria_del_portico`: un canto, el de 'espesor_pared_cajon', en
    losas, paredes y tabiques; sin cartelas."""
    with declarados(DECLARACIONES_CAJON):
        g = M8.geometria_del_portico(material=_marco(),
                                     seccion=SeccionRectangular(B=2.0, H=1.5))
    assert g.n_celdas == 1 and g.cartela_m == pytest.approx(0.0, abs=REL_CERRADA)
    for t in (g.t_losa_superior_m, g.t_losa_inferior_m, g.t_pared_m,
              g.t_tabique_m):
        assert t == pytest.approx(DECLARACIONES_CAJON["espesor_pared_cajon"],
                                  rel=REL_TRANSPORTE)


def test_el_analisis_envuelve_la_carga_viva_por_signo():
    """`analizar_portico`: sin vehiculos la envolvente es cero; con uno, el
    centro de la losa superior se tracciona por dentro."""
    g = _uniforme(0.25, 0.20)
    por_caso, ll = M8.analizar_portico(g, {"nada": []}, ())
    assert max(abs(x) for v in ll.values() for x in v) == pytest.approx(
        0.0, abs=REL_CERRADA)
    _, ll = M8.analizar_portico(g, {}, (("tandem", 30.0, 1.0, (0.0,)),))
    assert ll["losa_superior_1_centro"][0] > 0
    assert ll["losa_superior_1_izquierda"][1] < 0


def test_las_combinaciones_son_las_de_c12_11_2_1():
    """`combinaciones_del_portico`: cinco de resistencia (las de horizontal
    maximo con LS y sin LS) y tres de servicio; la de horizontal minimo es
    la unica que reduce EH."""
    f = {"DC": (1.25, 0.90), "EV": (1.35, 0.90), "EH": (1.35, 0.90),
         "LL": 1.75, "WA": 1.0, "eta": 1.05}
    combos = M8.combinaciones_del_portico(f)
    estados = [c[1] for c in combos]
    assert estados.count(M8.ESTADO_RESISTENCIA) == 5
    assert estados.count(M8.ESTADO_SERVICIO) == 3
    assert [c[0] for c in combos if c[4]] == [
        c[0] for c in combos if "horizontal min" in c[0]]
