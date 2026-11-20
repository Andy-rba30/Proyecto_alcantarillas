"""
tests/test_ve5_mh.py — VE-5, lote «mh»: lo que quedaba implementable de la
hidrologia (Fase 1-bis)
=========================================================================
Cuatro fichas de `docs/decisiones_diferidas.md`:

  * T1-07: el tiempo de concentracion por Izzard y por la onda cinematica
    (Tabla N 05 del Manual de Hidrologia, pags. impresas 39 y 40) y el punto
    fijo tc <-> I que las dos piden («la solución requiere de procesos
    iterativos»).
  * T1-05, ec. (17): la puerta para la relacion regional I = K·T^m / t^n.
  * T1-01: la prueba chi-cuadrado (num. 3.7.2 a) y las cinco distribuciones
    sin estimador impreso, que siguen sin evaluarse.
  * T1-03: V8 pide su caudal a la Fase 1-bis.

DE DONDE SALEN LOS DORADOS: el Manual no trae ejemplo numerico de ninguna de
estas formulas. Los valores esperados se calculan AQUI, con la formula que la
pagina imprime y por un camino que no pasa por `MH_hidrologia` (forma
cerrada cuando la hay; `scipy.optimize.brentq` sobre la ecuacion del punto
fijo cuando no). Los datos son sinteticos.
"""

from __future__ import annotations

import csv
import math
from dataclasses import replace
from pathlib import Path

import pytest
from scipy.optimize import brentq

from src import modelos
from src.modulos import MH_hidrologia as MH
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import declarados

RAIZ = Path(__file__).resolve().parent.parent
FIXTURES = RAIZ / "tests" / "fixtures" / "hidrologia"
CUENCAS = FIXTURES / "cuencas_prueba.csv"
ESTACION = FIXTURES / "estacion_prueba.csv"
ESTACION_DE_PRUEBA = "PRUEBA-SINTETICA"
ROTULO_DE_PRUEBA = "DATOS DE PRUEBA, NO DEL PROYECTO"
FEN = "homogeneidad_serie_fen"

REL = 1e-8          # el punto fijo itera a 1e-10 relativo
REL_ARITMETICA = 1e-12
# Los dorados escritos a mano con cuatro cifras: medio ultimo digito.
ABS_CUATRO_CIFRAS = 5e-4
ABS_DOS_DECIMALES = 5e-3
# El brentq del dorado de Izzard, muy por debajo de la tolerancia del punto
# fijo; y el margen de i·L, que arrastra la tolerancia relativa de I.
XTOL_DORADO = 1e-14
REL_MARGEN = 1e-6


@pytest.fixture()
def serie():
    return MH.cargar_estacion(ESTACION)[ESTACION_DE_PRUEBA]


@pytest.fixture()
def cuencas():
    return MH.cargar_cuencas(CUENCAS)


def _cuneta_izzard(cuencas, **cambios):
    base = replace(cuencas["B-01"], metodo_tc="izzard", L_cauce_m=8.0,
                   S_cauce_cuenca=0.02, area_km2=0.002, cobertura="pavimento",
                   c_retardo_izzard=0.012)
    return replace(base, **cambios)


def _cuneta_onda(cuencas, **cambios):
    base = replace(cuencas["B-01"], metodo_tc="onda_cinematica",
                   L_cauce_m=60.0, S_cauce_cuenca=0.02, S_terreno=0.03,
                   area_km2=0.004, cobertura="pavimento",
                   n_manning_superficial=0.013)
    return replace(base, **cambios)


# ===========================================================================
# T1-07 — Izzard y onda cinematica: las formulas puras
# ===========================================================================

def test_izzard_es_la_formula_de_la_tabla_05():
    # tc = 525 · (0.0000276·i + c) · L^0.33 / (S^0.333 · i^0.667)
    i, c, L, S = 100.0, 0.012, 40.0, 0.02
    a_mano = 525 * (0.0000276 * i + c) * L ** 0.33 / (S ** 0.333 * i ** 0.667)
    assert MH.tc_izzard_min(i_mm_h=i, c=c, L_m=L, S=S) == pytest.approx(
        a_mano, rel=REL_ARITMETICA)
    # A mano, con cuatro cifras: 525·0.014760·3.3784/(0.27146·21.627) = 4.464
    assert a_mano == pytest.approx(4.464, abs=ABS_CUATRO_CIFRAS)


def test_onda_cinematica_es_la_formula_de_la_tabla_05():
    # tc = 7 · L^0.6 · n^0.6 / (I^0.4 · S^0.3)
    L, n, I, S = 60.0, 0.013, 100.0, 0.03
    a_mano = 7 * L ** 0.6 * n ** 0.6 / (I ** 0.4 * S ** 0.3)
    assert MH.tc_onda_cinematica_min(L_m=L, n=n, I_mm_h=I, S=S) == \
        pytest.approx(a_mano, rel=REL_ARITMETICA)
    # A mano: 7·11.664·0.073767/(6.3096·0.34900) = 2.737
    assert a_mano == pytest.approx(2.737, abs=ABS_CUATRO_CIFRAS)


def test_los_datos_de_superficie_tienen_que_ser_positivos():
    with pytest.raises(modelos.DatoInvalidoError) as exc:
        MH.tc_izzard_min(i_mm_h=50, c=0.0, L_m=40, S=0.02)
    assert exc.value.campo == "c_retardo_izzard"
    with pytest.raises(modelos.DatoInvalidoError) as exc:
        MH.tc_onda_cinematica_min(L_m=40, n=-0.01, I_mm_h=50, S=0.02)
    assert exc.value.campo == "n_manning_superficial"


def test_la_condicion_de_izzard_es_la_del_producto_i_por_L():
    """«el producto de i por L debe ser ≤ 3800» (los dos lados incluidos)."""
    assert MH.exigir_producto_izzard(i_mm_h=95.0, L_m=40.0) == pytest.approx(3800, rel=REL_ARITMETICA)
    with pytest.raises(modelos.MetodoNoEvaluableError) as exc:
        MH.exigir_producto_izzard(i_mm_h=95.01, L_m=40.0)
    texto = str(exc.value)
    assert texto.startswith(modelos.MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA)
    assert "3800" in texto and "onda_cinematica" in texto


# ===========================================================================
# T1-07 — el punto fijo tc <-> I
# ===========================================================================

def test_el_punto_fijo_de_la_onda_cinematica_reproduce_la_forma_cerrada(
        cuencas):
    """
    Con una curva I = a / tc^b el punto fijo tiene forma cerrada:
    tc = 7·L^0.6·n^0.6·S^-0.3·(a/tc^b)^-0.4  =>
    tc^(1 − 0.4·b) = 7·L^0.6·n^0.6·S^-0.3·a^-0.4.
    """
    a, b = 600.0, 0.75
    cuenca = _cuneta_onda(cuencas)
    A = 7 * 60.0 ** 0.6 * 0.013 ** 0.6 * 0.03 ** -0.3 * a ** -0.4
    esperado = A ** (1 / (1 - 0.4 * b))
    tc, paso, avisos = MH.tiempo_de_concentracion(
        cuenca, intensidad_de=lambda t: a / t ** b)
    assert tc == pytest.approx(esperado, rel=REL)
    assert paso.formula_cita_id == "MC_HHD.3.9#T05_ONDA"
    assert "PUNTO FIJO" in paso.nota_del_proyecto and not avisos
    # La S que entra es la del TERRENO (la fila dice «del terreno»).
    s = next(m for m in paso.sustitucion if m.simbolo == "S")
    assert s.valor == pytest.approx(0.03, rel=REL_TRANSPORTE) and "S_terreno" in s.procedencia
    i = next(m for m in paso.sustitucion if m.simbolo == "I")
    assert i.valor == pytest.approx(a / esperado ** b, rel=REL)


def test_el_punto_fijo_de_izzard_coincide_con_brentq(cuencas):
    a, b = 200.0, 0.75
    cuenca = _cuneta_izzard(cuencas)

    def residuo(t):
        i = a / t ** b
        return 525 * (0.0000276 * i + 0.012) * 8.0 ** 0.33 / (
            0.02 ** 0.333 * i ** 0.667) - t
    esperado = brentq(residuo, 1e-3, 1440.0, xtol=XTOL_DORADO)
    tc, paso, _ = MH.tiempo_de_concentracion(
        cuenca, intensidad_de=lambda t: a / t ** b)
    assert tc == pytest.approx(esperado, rel=REL)
    assert paso.formula_cita_id == "MC_HHD.3.9#T05_IZZARD"
    assert paso.umbral.cita_id == "MC_HHD.3.9#T05_IZZARD_IL"
    assert paso.umbral.caracter == "exigencia"
    assert paso.veredicto.tipo is modelos.TipoDeVeredicto.CUMPLE
    assert paso.veredicto.margen == pytest.approx(
        3800 - a / esperado ** b * 8.0, rel=REL_MARGEN)


def test_izzard_fuera_del_producto_no_se_evalua(cuencas):
    # Una trayectoria de 200 m bajo una lluvia de 600/tc^0.75: i·L ~ 1e4.
    cuenca = _cuneta_izzard(cuencas, L_cauce_m=200.0)
    with pytest.raises(modelos.MetodoNoEvaluableError) as exc:
        MH.tiempo_de_concentracion(cuenca,
                                   intensidad_de=lambda t: 6000 / t ** 0.75)
    assert "3800" in str(exc.value)


def test_sin_curva_de_intensidad_los_metodos_iterativos_no_se_evaluan(cuencas):
    with pytest.raises(modelos.DatoFaltanteError) as exc:
        MH.tiempo_de_concentracion(_cuneta_onda(cuencas))
    assert exc.value.campo == "I"


@pytest.mark.parametrize("metodo, columna", [
    ("izzard", "c_retardo_izzard"),
    ("onda_cinematica", "n_manning_superficial")])
def test_sin_el_dato_de_superficie_el_metodo_se_detiene(cuencas, metodo,
                                                        columna):
    cuenca = replace(cuencas["B-01"], metodo_tc=metodo)
    with pytest.raises(modelos.DatoFaltanteError) as exc:
        MH.tiempo_de_concentracion(cuenca, intensidad_de=lambda t: 50.0)
    assert exc.value.campo == columna


def test_el_punto_fijo_que_no_converge_es_limite_numerico(cuencas, monkeypatch):
    monkeypatch.setattr(MH, "ITERACIONES_MAX_PUNTO_FIJO_TC", 2)
    with pytest.raises(modelos.LimiteNumericoError) as exc:
        MH.tiempo_de_concentracion(_cuneta_onda(cuencas),
                                   intensidad_de=lambda t: 600 / t ** 0.75)
    assert "no convergio" in str(exc.value)


def test_el_caudal_de_la_cuneta_cierra_el_punto_fijo_con_la_lluvia_de_diseno(
        cuencas, serie):
    """
    Con la serie de prueba y los criterios de archivo (Dick y Peschke, 5 min
    de duracion minima): el tc del caudal satisface la formula con la
    intensidad del paso 1b.5, y esa intensidad es la de una lluvia de
    duracion tc.
    """
    with declarados({FEN: "serie_completa"}):
        izz = MH.caudal_de_aporte_cuneta(_cuneta_izzard(cuencas), serie, 35)
        onda = MH.caudal_de_aporte_cuneta(_cuneta_onda(cuencas), serie, 35)
    for caudal in (izz, onda):
        d = max(caudal.tc_min, 5.0)
        Pd = caudal.P24_TR_mm * (d / 1440) ** 0.25
        assert caudal.I_mm_h == pytest.approx(Pd / (d / 60), rel=REL)
    assert izz.tc_min == pytest.approx(
        525 * (0.0000276 * izz.I_mm_h + 0.012) * 8.0 ** 0.33
        / (0.02 ** 0.333 * izz.I_mm_h ** 0.667), rel=REL)
    assert onda.tc_min == pytest.approx(
        7 * 60.0 ** 0.6 * 0.013 ** 0.6 / (onda.I_mm_h ** 0.4 * 0.03 ** 0.3),
        rel=REL)
    assert izz.metodo_tc == "izzard" and onda.metodo_tc == "onda_cinematica"
    assert izz.Q_m3s > 0 and onda.Q_m3s > 0


# ===========================================================================
# T1-07 — el cargador, el registro y el pre-vuelo
# ===========================================================================

def _cuencas_con(tmp_path, filas):
    columnas = list(MH.COLUMNAS_CUENCAS + MH.COLUMNAS_CUENCAS_OPCIONALES)
    destino = tmp_path / "cuencas.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        fh.write(f"# {ROTULO_DE_PRUEBA}\n")
        escritor = csv.DictWriter(fh, fieldnames=columnas, restval="")
        escritor.writeheader()
        escritor.writerows(filas)
    return destino


BASE = {"id": "B-01", "area_km2": "0.002", "L_cauce_m": "40",
        "S_cauce_cuenca": "0.02", "S_terreno": "0.02", "cobertura": "pavimento",
        "suelo": "", "estacion": ESTACION_DE_PRUEBA}


def test_el_cargador_lee_las_dos_columnas_nuevas(tmp_path):
    cuencas = MH.cargar_cuencas(_cuencas_con(tmp_path, [
        {**BASE, "metodo_tc": "izzard", "c_retardo_izzard": "0.012"},
        {**BASE, "id": "B-02", "metodo_tc": "onda_cinematica",
         "n_manning_superficial": "0.013"}]))
    assert cuencas["B-01"].c_retardo_izzard == pytest.approx(0.012, rel=REL_TRANSPORTE)
    assert cuencas["B-02"].n_manning_superficial == pytest.approx(0.013, rel=REL_TRANSPORTE)
    assert {"izzard", "onda_cinematica"} <= set(MH.METODOS_TC)


def test_un_dato_de_superficie_con_otro_metodo_contradice(tmp_path):
    with pytest.raises(modelos.DatoInvalidoError) as exc:
        MH.cargar_cuencas(_cuencas_con(tmp_path, [
            {**BASE, "metodo_tc": "federal_aviation_administration",
             "c_retardo_izzard": "0.012"}]))
    assert exc.value.campo == "c_retardo_izzard"
    assert "contradice" in str(exc.value)


def test_las_seis_filas_de_la_tabla_05_tienen_funcion():
    from src.normativa import registro
    from src.normativa.esquema import NoUsada
    filas = registro.construir().tabla("MC_HHD.T05").filas
    assert len(filas) == 6
    assert not [f for f in filas if isinstance(f.uso, NoUsada)]


def test_el_prevuelo_anticipa_el_dato_de_superficie_que_falta(cuencas, serie):
    with declarados({FEN: "serie_completa"}):
        obstaculos = MH.anticipar_caudal(
            replace(_cuneta_onda(cuencas), n_manning_superficial=None), serie,
            de_cuneta=True)
    assert [o.dato for o in obstaculos] == ["n_manning_superficial"]


# ===========================================================================
# T1-05, ec. (17) — la puerta de la relacion regional I = K·T^m / t^n
# ===========================================================================

RELACION = "relacion_intensidad_duracion"
IDF = "factores_idf_regional"
FACTORES = {"K": 120.0, "m": 0.2, "n": 0.6}


def test_la_ecuacion_17_es_la_de_la_pagina():
    # I = K·T^m / t^n = 120 · 35^0.2 / 20^0.6 = 120·2.0360/6.0342 = 40.49
    I = MH.intensidad_idf_regional_mm_h(K=120.0, m=0.2, n=0.6, TR=35, t_min=20)
    assert I == pytest.approx(120 * 35 ** 0.2 / 20 ** 0.6, rel=REL_ARITMETICA)
    assert I == pytest.approx(40.49, abs=ABS_DOS_DECIMALES)


def test_el_criterio_de_los_factores_es_un_dato_de_sitio_sin_valor():
    from src import criterios_adoptados as ca
    c = ca.CRITERIOS[IDF]
    assert c.valor is None and c.etiqueta == "S" and c.nivel == ca.NIVEL_PERFIL
    assert c.forma == ca.FORMA_DICT_CON_CAMPOS and c.trazabilidad
    assert "idf_regional_ec17" in ca.CRITERIOS[RELACION].sensibilidad
    assert "MC_HHD.3.8.1#EC17" in c.justificacion


def test_la_relacion_regional_da_la_intensidad_del_caudal(cuencas, serie):
    with declarados({FEN: "serie_completa", RELACION: "idf_regional_ec17",
                     IDF: FACTORES}):
        caudal = MH.caudal_de_diseno(cuencas["A-02"], serie, 35)
    d = max(caudal.tc_min, 5.0)
    assert caudal.I_mm_h == pytest.approx(120 * 35 ** 0.2 / d ** 0.6, rel=REL)
    paso = next(p for p in caudal.pasos if p.codigo == "1b.5")
    assert paso.formula_cita_id == "MC_HHD.3.8.1#EC17"
    simbolos = {m.simbolo: m.valor for m in paso.sustitucion}
    assert simbolos["K"] == pytest.approx(FACTORES["K"], rel=REL_TRANSPORTE)
    assert simbolos["n"] == pytest.approx(FACTORES["n"], rel=REL_TRANSPORTE)
    assert simbolos["T"] == 35
    # La lluvia de 24 horas de la estacion se imprime al lado, como contraste.
    assert any("dick_peschke" in e for e in paso.elecciones[0].entre)


def test_sin_los_factores_la_relacion_regional_se_detiene(cuencas, serie):
    with declarados({FEN: "serie_completa", RELACION: "idf_regional_ec17"}):
        with pytest.raises(modelos.CriterioPendienteError) as exc:
            MH.caudal_de_diseno(cuencas["A-02"], serie, 35)
        obstaculos = MH.anticipar_caudal(cuencas["A-02"], serie,
                                         de_cuneta=False)
    assert exc.value.clave == IDF
    assert IDF in [o.dato for o in obstaculos]


@pytest.mark.parametrize("factores", [
    {"K": 120.0, "m": 0.2}, {"K": 120.0, "m": 0.2, "n": -0.6},
    {"K": 0.0, "m": 0.2, "n": 0.6}, {"K": 120.0, "m": "x", "n": 0.6}])
def test_los_factores_tienen_que_ser_tres_y_positivos(cuencas, serie,
                                                      factores):
    with declarados({FEN: "serie_completa", RELACION: "idf_regional_ec17",
                     IDF: factores}):
        with pytest.raises(modelos.DatoInvalidoError) as exc:
            MH.caudal_de_diseno(cuencas["A-02"], serie, 35)
    assert exc.value.campo == IDF


def test_el_punto_fijo_cruza_la_curva_regional(cuencas, serie):
    """
    Onda cinematica con la ecuacion (17): I = (K·T^m) / t^n es exactamente la
    curva a / t^b de la forma cerrada, con a = K·T^m y b = n.
    """
    cuenca = replace(_cuneta_onda(cuencas), L_cauce_m=150.0, area_km2=0.01,
                     n_manning_superficial=0.4)
    a, b = 120 * 35 ** 0.2, 0.6
    A = 7 * 150.0 ** 0.6 * 0.4 ** 0.6 * 0.03 ** -0.3 * a ** -0.4
    esperado = A ** (1 / (1 - 0.4 * b))
    assert esperado > 5.0                    # por encima de la duracion minima
    with declarados({FEN: "serie_completa", RELACION: "idf_regional_ec17",
                     IDF: FACTORES}):
        caudal = MH.caudal_de_aporte_cuneta(cuenca, serie, 35)
    assert caudal.tc_min == pytest.approx(esperado, rel=REL)
    assert caudal.I_mm_h == pytest.approx(a / esperado ** b, rel=REL)


def test_factores_idf_regional_lee_el_criterio_y_lo_comprueba():
    with declarados({IDF: FACTORES}):
        assert MH.factores_idf_regional() == pytest.approx(
            (FACTORES["K"], FACTORES["m"], FACTORES["n"]), rel=REL_TRANSPORTE)
    with pytest.raises(modelos.CriterioPendienteError):
        MH.factores_idf_regional()


# ===========================================================================
# T1-01 — la prueba chi-cuadrado y las cinco distribuciones sin estimador
# ===========================================================================

CHI2 = "intervalos_de_clase_chi_cuadrado"


@pytest.mark.parametrize("n, sturges, raiz", [(5, 4, 3), (16, 5, 4),
                                              (25, 6, 5), (40, 7, 7)])
def test_el_numero_de_intervalos_sigue_su_regla(n, sturges, raiz):
    assert MH.numero_de_intervalos(n, "sturges") == sturges
    assert MH.numero_de_intervalos(n, "raiz_de_n") == raiz
    with pytest.raises(modelos.DatoInvalidoError):
        MH.numero_de_intervalos(n, "otra")


def _chi2_a_mano(valores, k, alfa):
    """La ecuacion (12) por un camino que no pasa por MH: statistics y scipy."""
    from statistics import NormalDist, fmean, stdev
    from scipy.stats import chi2
    F = NormalDist(fmean(valores), stdev(valores)).cdf
    menor, mayor, n = min(valores), max(valores), len(valores)
    bordes = [menor + (mayor - menor) * i / k for i in range(1, k)]
    cdf = [0.0] + [F(b) for b in bordes] + [1.0]
    obs = [0] * k
    for x in valores:
        obs[sum(x > b for b in bordes)] += 1
    esp = [n * (cdf[i + 1] - cdf[i]) for i in range(k)]
    D = sum((o - e) ** 2 / e for o, e in zip(obs, esp))
    return D, obs, chi2.ppf(1 - alfa, k - 3)


def test_la_chi_cuadrado_de_la_normal_coincide_con_el_calculo_a_mano(serie):
    valores = [r.p24_mm for r in serie.registros]
    k = MH.numero_de_intervalos(len(valores), "sturges")
    D, obs, critico = _chi2_a_mano(valores, k, 0.05)
    prueba = MH.prueba_chi_cuadrado(valores, "normal", alfa=0.05,
                                    regla="sturges")
    assert prueba.k == k and prueba.nu == k - 3
    assert list(prueba.observados) == obs and sum(obs) == len(valores)
    assert sum(prueba.esperados) == pytest.approx(len(valores),
                                                  rel=REL_ARITMETICA)
    assert prueba.D == pytest.approx(D, rel=REL_ARITMETICA)
    assert prueba.critico == pytest.approx(critico, rel=REL_ARITMETICA)
    assert prueba.acepta == (D <= critico)


def test_la_chi_cuadrado_no_se_aplica_a_la_gumbel(serie):
    valores = [r.p24_mm for r in serie.registros]
    with pytest.raises(modelos.MetodoNoEvaluableError):
        MH.prueba_chi_cuadrado(valores, "gumbel", alfa=0.05, regla="sturges")


def test_el_paso_de_la_bondad_imprime_el_contraste_sin_decidir(serie):
    # La serie de prueba solo pasa Kolmogorov-Smirnov con la log normal.
    with declarados({FEN: "serie_completa",
                     "distribucion_precipitacion_maxima": "lognormal_2p"}):
        _, _, _, pasos, _ = MH.precipitacion_de_diseno(serie, 35)
    ks = next(p for p in pasos if p.codigo == "1b.3")
    assert "Contraste chi-cuadrado" in ks.nota_del_proyecto
    assert "MC_HHD.3.7.2a" in ks.citas_textuales
    assert ks.elecciones[0].clave_criterio == CHI2
    # La prueba que decide sigue siendo Kolmogorov-Smirnov.
    assert ks.umbral.cita_id == "MC_HHD.3.7.2b#T03"
    # Con la Gumbel no se aplica, y no se lee el criterio de los intervalos.
    valores = [r.p24_mm for r in serie.registros]
    nota, elecciones, citas = MH._contraste_chi_cuadrado(valores, "gumbel",
                                                         alfa=0.05)
    assert "no se aplica" in nota and not elecciones
    assert citas == ("MC_HHD.3.7.2a#ALCANCE",)


def test_el_criterio_de_los_intervalos_es_un_A_de_perfil_con_ventana():
    from src import criterios_adoptados as ca
    c = ca.CRITERIOS[CHI2]
    assert (c.valor, c.etiqueta, c.nivel) == ("sturges", "A", ca.NIVEL_PERFIL)
    assert c.sensibilidad == ("sturges", "raiz_de_n")


@pytest.mark.parametrize("distribucion", [
    "lognormal_3p", "gamma_2p", "gamma_3p", "log_pearson_3", "log_gumbel"])
def test_las_cinco_sin_estimador_impreso_siguen_sin_evaluarse(serie,
                                                              distribucion):
    """
    Decision del dueño (VE-5): solo con un estimador que una fuente del
    repositorio de normas imprima. Ninguna lo imprime (ficha T1-01), y
    declararlas detiene el calculo con el rotulo de la hidrologia.
    """
    from src.constantes_normativas import DISTRIBUCIONES_3_7_1
    assert distribucion in DISTRIBUCIONES_3_7_1
    with declarados({FEN: "serie_completa",
                     "distribucion_precipitacion_maxima": distribucion}):
        with pytest.raises(modelos.MetodoNoEvaluableError) as exc:
            MH.precipitacion_de_diseno(serie, 35)
    assert str(exc.value).startswith(
        modelos.MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA)


def test_estadistico_chi_cuadrado_con_una_uniforme_a_mano():
    """
    Diez datos 0.5, 1.5, …, 9.5 contra la uniforme de 0 a 10, en k = 2
    intervalos de igual amplitud entre 0.5 y 9.5 (corte en 5.0): observados
    [5, 5], esperados [5, 5] y D = 0.
    """
    valores = [i + 0.5 for i in range(10)]
    D, obs, esp = MH.estadistico_chi_cuadrado(
        valores, lambda x: min(max(x / 10, 0.0), 1.0), 2)
    assert obs == (5, 5)
    assert esp == pytest.approx((5.0, 5.0), rel=REL_ARITMETICA)
    assert D == pytest.approx(0.0, abs=ABS_CERO)


# ===========================================================================
# T1-03 — V8 pide su caudal a la Fase 1-bis
# ===========================================================================

TR_EXTREMO = "TR_evento_extremo"
PUNTOS = RAIZ / "tests" / "ejemplo_puntos.csv"


def _informe_de(id_punto, **cambios):
    from src import servicio
    from src.modulos.M0_carga import cargar_puntos
    punto = next(p for p in cargar_puntos(PUNTOS) if p.id == id_punto)
    return servicio.InformePunto(punto=replace(punto, **cambios))


def _hidrologia_chica(tmp_path):
    """A-02 con una cuenca de 0.12 km2 (12 ha en el CSV de puntos)."""
    from src import servicio
    ruta = _cuencas_con(tmp_path, [{
        "id": "A-02", "area_km2": "0.12", "L_cauce_m": "600",
        "S_cauce_cuenca": "0.04", "S_terreno": "0.04",
        "cobertura": "cultivos", "suelo": "permeable",
        "estacion": ESTACION_DE_PRUEBA, "metodo_tc": "kirpich",
        "ajuste_kirpich": "ninguno"}])
    return servicio.cargar_hidrologia(ruta, ESTACION)


def test_sin_declarar_el_caudal_extremo_lo_calcula_la_fase_1_bis(tmp_path):
    from src import criterios_adoptados as ca
    from src import servicio
    h = _hidrologia_chica(tmp_path)
    informe = _informe_de("A-02", area_ha=12.0)
    with declarados({FEN: "serie_completa", TR_EXTREMO: 100.0}):
        ca.reiniciar_usos()
        dato = servicio._caudal_del_evento_extremo(informe, h)
        # El TR se lee sin registrar: quien lo registra es V8 al correr.
        assert TR_EXTREMO not in ca.criterios_usados()
        esperado = MH.caudal_de_diseno(h.cuenca_de("A-02"),
                                       h.estaciones[ESTACION_DE_PRUEBA], 100.0)
        de_diseno = MH.caudal_de_diseno(h.cuenca_de("A-02"),
                                        h.estaciones[ESTACION_DE_PRUEBA], 25.0)
    assert dato.nombre == "Q_evento_extremo_m3s"
    assert dato.valor == pytest.approx(esperado.Q_m3s, rel=REL_TRANSPORTE)
    assert dato.valor > de_diseno.Q_m3s          # crece con el TR
    assert "Fase 1-bis" in dato.origen and "TR = 100" in dato.origen


def test_sin_TR_o_sin_cuenca_no_se_calcula_nada(tmp_path):
    from src import servicio
    h = _hidrologia_chica(tmp_path)
    with declarados({FEN: "serie_completa"}):
        assert servicio._caudal_del_evento_extremo(
            _informe_de("A-02", area_ha=12.0), h) is None
    with declarados({FEN: "serie_completa", TR_EXTREMO: 100.0}):
        assert servicio._caudal_del_evento_extremo(
            _informe_de("A-02", area_ha=12.0), None) is None
        assert servicio._caudal_del_evento_extremo(
            _informe_de("A-01"), h) is None          # sin fila de cuenca


def test_si_la_fase_1_bis_no_puede_el_motivo_queda_en_un_aviso(tmp_path):
    from src import servicio
    h = _hidrologia_chica(tmp_path)
    informe = _informe_de("A-02", area_ha=210.0)     # dos areas distintas
    with declarados({FEN: "serie_completa", TR_EXTREMO: 100.0}):
        assert servicio._caudal_del_evento_extremo(informe, h) is None
    assert any("V8 de A-02" in a and "evento extremo" in a
               for a in informe.avisos_de_expediente)


def test_el_caudal_extremo_declarado_gana(tmp_path):
    """
    `_datos_de_expediente` solo pide la Fase 1-bis cuando el dato externo
    falta: con `Q_evento_extremo_m3s` declarado, el evento lleva ese valor y
    su origen de dato externo.
    """
    import ast
    import inspect
    from src import servicio
    arbol = ast.parse(inspect.getsource(servicio._datos_de_expediente))
    llamadas = [n for n in ast.walk(arbol) if isinstance(n, ast.IfExp)
                and any(isinstance(c, ast.Call)
                        and getattr(c.func, "id", "") == "_caudal_del_evento_extremo"
                        for c in ast.walk(n.body))]
    assert len(llamadas) == 1
    # La condicion es «Q_ext is None»: el declarado gana.
    condicion = llamadas[0].test
    assert isinstance(condicion, ast.Compare) and \
        isinstance(condicion.ops[0], ast.Is) and \
        getattr(condicion.left, "id", "") == "Q_ext"
