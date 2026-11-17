"""
tests/test_ve2_hidrologia.py — VE-2, la parte de hidrologia: (e), (f) y (d)
==========================================================================
Tres decisiones del dueño (2026-11-17) sobre la ficha VE1-02 de
`docs/decisiones_diferidas.md`, en la Fase 1-bis (`MH_hidrologia`):

(e) Paso 8 del prompt VE-2. Un AVISO DE CONSISTENCIA de la serie de lluvias,
    SIN UMBRAL: el Manual de Hidrologia manda evaluar «la consistencia de los
    datos registrados» (num. 3.3, pag. impresa 21) y ninguna fuente del
    repositorio de normas da el procedimiento ni un numero de corte. La
    memoria lo dice, dice que el programa no lo evalua y que el proyectista
    tiene que declarar que lo hizo. Patron de `FH.Q_ESPECIFICO`.

COMO SE MIDIO EL ROJO. Cada bloque de este archivo se escribio ANTES que su
implementacion, con `xfail(strict=True)` y la expectativa (nunca la salida
del programa como oraculo), y se corrio en rojo; al implementar se quito la
marca. Los dorados numericos estan calculados a mano en el propio test, con
`math` y `statistics`, por un camino que no pasa por `MH_hidrologia`.

LOS DATOS SON SINTETICOS: la serie de `tests/fixtures/hidrologia/` (rotulada
«DATOS DE PRUEBA, NO DEL PROYECTO»), la misma que T-1.
"""

from __future__ import annotations

import statistics
from dataclasses import replace
from pathlib import Path

import pytest

from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE

RAIZ = Path(__file__).resolve().parent.parent
FIXTURES = RAIZ / "tests" / "fixtures" / "hidrologia"
CUENCAS = FIXTURES / "cuencas_prueba.csv"
ESTACION = FIXTURES / "estacion_prueba.csv"
ESTACION_DE_PRUEBA = "PRUEBA-SINTETICA"
FEN = "homogeneidad_serie_fen"
REL = 1e-9          # dos caminos de la misma aritmetica
# Los dorados del caso a mano se escriben con seis cifras significativas.
REL_DORADO = 1e-5
# «Distinto» de verdad: los dos C de la ec. (35), con Pd y con P, difieren en
# la segunda cifra; una tolerancia de una millonesima no los confunde.
REL_DISTINTO = 1e-6
# El cuantil (o el caudal) multiplicado por el factor frente al calculado con
# la serie multiplicada: la misma aritmetica salvo una multiplicacion.
REL_ESCALA = 1e-12


def _declarados(valores):
    from tests.apoyo.criterios import declarados
    return declarados(valores)


@pytest.fixture()
def MH():
    from src.modulos import MH_hidrologia
    return MH_hidrologia


@pytest.fixture()
def serie(MH):
    return MH.cargar_estacion(ESTACION)[ESTACION_DE_PRUEBA]


@pytest.fixture()
def cuencas(MH):
    return MH.cargar_cuencas(CUENCAS)


@pytest.fixture()
def reg():
    from src.normativa import registro
    return registro.construir()


# ===========================================================================
# (e) Aviso de consistencia de la serie, SIN umbral — VE1-02 (e)
# ===========================================================================

CITA_33 = "MC_HHD.3.3#CONSISTENCIA"
CITA_34 = "MC_HHD.3.4#CONSISTENCIA"
FUNDAMENTO_CONSISTENCIA = "FH.CONSISTENCIA"


def _paso_de_consistencia(pasos):
    candidatos = [p for p in pasos if p.fundamento_id == FUNDAMENTO_CONSISTENCIA]
    assert len(candidatos) == 1, [p.fundamento_id for p in pasos]
    return candidatos[0]


def test_e_las_dos_citas_de_consistencia_son_las_de_la_pagina(reg):
    """
    Num. 3.3 «Estudios de Campo», pag. impresa 21 (PDF 24): «Se debe evaluar
    las condiciones de las estaciones pluviométricas e hidrométricas, así
    como la consistencia de los datos registrados.» Es EXIGENCIA («Se
    debe»). Num. 3.4, pag. impresa 22 (PDF 25): «La representatividad,
    calidad, extensión y consistencia de los datos es primordial para el
    inicio del estudio hidrológico» — no manda nada por si misma.
    """
    from src.normativa.esquema import Caracter
    c33 = reg.cita(CITA_33)
    assert (c33.numeral, c33.pagina_impresa, c33.pagina_pdf) == ("3.3", "21", 24)
    assert c33.titulo_numeral == "Estudios de Campo"
    assert c33.texto_literal.texto == (
        "Se debe evaluar las condiciones de las estaciones pluviométricas e "
        "hidrométricas, así como la consistencia de los datos registrados.")
    assert c33.caracter is Caracter.EXIGENCIA
    assert c33.verificado is not None
    c34 = reg.cita(CITA_34)
    assert (c34.numeral, c34.pagina_impresa, c34.pagina_pdf) == ("3.4", "22", 25)
    assert "consistencia de los datos es primordial" in c34.texto_literal.texto
    assert c34.caracter is not Caracter.EXIGENCIA


def test_e_el_fundamento_dice_obliga_y_lo_sostiene_la_exigencia_del_3_3(reg):
    from src.normativa.esquema import Verbo
    f = reg.fundamento(FUNDAMENTO_CONSISTENCIA)
    assert f.verbo is Verbo.OBLIGA
    assert CITA_33 in f.citas and CITA_34 in f.citas
    assert f.fase == reg.fundamento("FH.SERIE").fase
    assert not [p for p in reg.problemas_de_integridad()
                if FUNDAMENTO_CONSISTENCIA in p]


def test_e_la_lluvia_de_diseno_emite_el_aviso_sin_umbral_y_sin_veredicto(MH, serie):
    """
    El paso dice las tres cosas que el prompt pide: que el Manual EXIGE
    evaluar la consistencia, que el programa NO la evalua y que el
    proyectista tiene que DECLARAR que lo hizo. Sin umbral ni veredicto: no
    hay numero de corte en ninguna fuente, e inventarlo seria rellenar un
    vacio.
    """
    from src.modelos import TipoDeVeredicto
    with _declarados({FEN: "serie_completa"}):
        *_, pasos, _avisos = MH.precipitacion_de_diseno(serie, 71)
    p = _paso_de_consistencia(pasos)
    assert p.umbral is None
    assert p.veredicto.tipo is TipoDeVeredicto.SIN_VEREDICTO
    nota = p.nota_del_proyecto
    assert nota.startswith("AVISO DE CONSISTENCIA, sin umbral")
    for trozo in ("consistencia de los datos registrados", "3.3",
                  "NO la evalua", "declarar"):
        assert trozo in nota, trozo
    assert CITA_33 in p.citas_textuales and CITA_34 in p.citas_textuales
    # Va DESPUES de los cuatro pasos de siempre (1b.1, 1b.2, 1b.3, 1b.3b):
    # las posiciones que T-1 fijo no se mueven.
    assert [x.codigo for x in pasos] == ["1b.1", "1b.2", "1b.3", "1b.3b",
                                         MH.CODIGO_CONSISTENCIA]
    assert MH.CODIGO_CONSISTENCIA == "1b.3c"


def test_e_el_paso_imprime_la_serie_entera_sin_juzgarla(MH, serie):
    """
    Lo que el paso imprime para orientar al proyectista, calculado aqui a
    mano con `statistics` sobre la serie ENTERA de la estacion (la
    consistencia es de los datos registrados, no de la serie que entra al
    ajuste): n, minimo, mediana, maximo y maximo / mediana.
    """
    valores = [r.p24_mm for r in serie.registros]
    mediana = statistics.median(valores)
    maximo = max(valores)
    with _declarados({FEN: "serie_completa"}):
        *_, pasos, _ = MH.precipitacion_de_diseno(serie, 71)
    p = _paso_de_consistencia(pasos)
    por = {m.simbolo: m.valor for m in p.sustitucion}
    assert por["n"] == len(valores) == 40
    assert por["minimo"] == pytest.approx(min(valores), rel=REL)
    assert por["mediana"] == pytest.approx(mediana, rel=REL)
    assert por["maximo"] == pytest.approx(maximo, rel=REL)
    assert p.resultado.simbolo == "maximo / mediana"
    assert p.resultado.valor == pytest.approx(maximo / mediana, rel=REL)
    # El año del maximo, para que el proyectista sepa que dato revisar.
    anio_max = max(serie.registros, key=lambda r: r.p24_mm).anio
    assert str(anio_max) in " ".join(m.procedencia for m in p.sustitucion)


@pytest.mark.parametrize("multiplicador", [1.0, 30.0])
def test_e_ningun_numero_de_corte_cambia_el_trato(MH, serie, multiplicador):
    """
    La misma serie con su maximo multiplicado por 30 (cociente maximo /
    mediana de casi 300): el paso sigue SIN veredicto, sin umbral, y el
    calculo NO se detiene. Si alguien le pusiera un corte, este test muere.
    """
    from src.modelos import TipoDeVeredicto
    mayor = max(serie.registros, key=lambda r: r.p24_mm)
    registros = tuple(replace(r, p24_mm=r.p24_mm * multiplicador)
                      if r is mayor else r for r in serie.registros)
    otra = replace(serie, registros=registros)
    with _declarados({FEN: "serie_completa"}):
        ajuste, *_, pasos, avisos = MH.precipitacion_de_diseno(otra, 71)
    p = _paso_de_consistencia(pasos)
    assert p.umbral is None
    assert p.veredicto.tipo is TipoDeVeredicto.SIN_VEREDICTO
    assert ajuste.P_TR_mm > 0
    # No es un aviso que cambie con el dato: la nota dice lo mismo.
    with _declarados({FEN: "serie_completa"}):
        *_, pasos_base, _ = MH.precipitacion_de_diseno(serie, 71)
    base = _paso_de_consistencia(pasos_base)
    assert p.nota_del_proyecto.split(". ")[0] == base.nota_del_proyecto.split(". ")[0]


def test_e_el_caudal_calculado_lo_lleva_y_el_declarado_no(MH, serie, cuencas):
    with _declarados({FEN: "serie_completa"}):
        c = MH.caudal_de_diseno(cuencas["A-02"], serie, 71)
    assert MH.CODIGO_CONSISTENCIA in [p.codigo for p in c.pasos]
    declarado = MH.caudal_declarado(Q_m3s=1.0, de_donde="columna Q_m3s",
                                    area_km2=2.1, origen_area="prueba")
    assert FUNDAMENTO_CONSISTENCIA not in [p.fundamento_id for p in declarado.pasos]


def test_e_el_modulo_no_tiene_umbral_de_consistencia():
    """
    Por AST: ningun nombre de `MH_hidrologia` ni de `constantes_normativas`
    habla de un umbral o un limite de consistencia. Un corte inventado
    tendria que vivir en uno de los dos.
    """
    import ast
    for ruta in (RAIZ / "src" / "modulos" / "MH_hidrologia.py",
                 RAIZ / "src" / "constantes_normativas.py"):
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        nombres = {n.id for n in ast.walk(arbol) if isinstance(n, ast.Name)}
        nombres |= {n.name for n in ast.walk(arbol)
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        sospechosos = {x for x in nombres if "CONSISTENCIA" in x.upper()
                       and any(t in x.upper() for t in ("UMBRAL", "LIMITE",
                                                         "MAX", "CORTE"))}
        assert not sospechosos, (ruta.name, sospechosos)


def test_e_la_consistencia_es_de_la_serie_registrada_no_de_la_ajustada(MH, serie):
    """
    Con `serie_sin_fen` el ajuste usa 37 años, y el aviso sigue hablando de
    los 40 registrados: la consistencia es de los datos que la estacion
    registro. Para que `serie_sin_fen` no se detenga (T1-09) se marcan FEN
    los tres años MAS SECOS: quitarlos sube la lluvia de diseño.
    """
    secos = sorted(serie.registros, key=lambda r: r.p24_mm)[:3]
    registros = tuple(replace(r, fen=r in secos) for r in serie.registros)
    otra = replace(serie, registros=registros)
    with _declarados({FEN: "serie_sin_fen"}):
        ajuste, *_, pasos, _ = MH.precipitacion_de_diseno(otra, 71)
    assert ajuste.n == 37
    p = _paso_de_consistencia(pasos)
    por = {m.simbolo: m.valor for m in p.sustitucion}
    assert por["n"] == 40
    assert por["minimo"] == pytest.approx(secos[0].p24_mm, rel=REL)


# ===========================================================================
# (f) Metodo racional modificado de 10 a 770 km2 — VE1-02 (f), T1-08
# ===========================================================================
# El num. 3.12.2.1 del Manual (pags. impresas 50 a 52, PDF 53 a 55), leido
# en la IMAGEN de las dos paginas (la capa de texto parte las formulas):
#
#   (29) Q = 0,278 C I A K               (30) Tc = 0.3 (L / S^0.25)^0.76
#   (31) K = 1 + Tc^1.25 / (Tc^1.25 + 14) (32) KA = 1 – (log10 A/15)
#   (33) P = kA Pd
#   (34) I = (P/24) * (11)^((28^0.1 – Tc^0.1)/(28^0.1 – 1))
#   (35) C = (Pd – Po)(Pd + 23 Po) / (pd + 11 Po)^2 ,  Po = (5000/CN) – 50
#
# «áreas menores de 770 km2 y con tiempos de concentración (Tc) de entre
# 0.25 y 24 horas». La frontera de 10 km2 con el racional simple es la de
# siempre («Muy usado para cuencas, A<10 Km2», pag. impresa 49).

CUENCAS_RM = FIXTURES / "cuencas_racional_modificado_prueba.csv"
ROTULO_DE_PRUEBA = "DATOS DE PRUEBA, NO DEL PROYECTO"
ID_RM = "A-01"                       # el id de una obra de ejemplo_puntos.csv
AREA_RM_KM2 = 55.9
L_RM_KM, S_RM, CN_RM = 15.0, 0.02, 75.0
PUNTOS = RAIZ / "tests" / "ejemplo_puntos.csv"


def _a_mano(*, A, L_km, S, CN, Pd):
    """
    Las ecuaciones (29) a (35) escritas aqui, con `math` y sin pasar por
    `MH_hidrologia`. Devuelve un dict con cada factor.
    """
    import math
    Tc = 0.3 * (L_km / S ** 0.25) ** 0.76                       # (30), horas
    K = 1 + Tc ** 1.25 / (Tc ** 1.25 + 14)                      # (31)
    KA = 1 - math.log10(A) / 15                                 # (32)
    P = KA * Pd                                                 # (33)
    I = (P / 24) * 11 ** ((28 ** 0.1 - Tc ** 0.1) / (28 ** 0.1 - 1))   # (34)
    Po = 5000 / CN - 50                                         # umbral
    C = (Pd - Po) * (Pd + 23 * Po) / (Pd + 11 * Po) ** 2        # (35), con Pd
    Q = 0.278 * C * I * A * K                                   # (29)
    return dict(Tc=Tc, K=K, KA=KA, P=P, I=I, Po=Po, C=C, Q=Q)


def _cuenca_rm(MH, **cambios):
    from src.modelos import Cuenca
    base = dict(id=ID_RM, area_km2=AREA_RM_KM2, L_cauce_m=L_RM_KM * 1000,
                S_cauce_cuenca=S_RM, cobertura="pastos_vegetacion_ligera",
                suelo="semipermeable", estacion=ESTACION_DE_PRUEBA,
                metodo_tc="temez", S_terreno=0.03, H_desnivel_m=None,
                ajuste_kirpich=None, CN=CN_RM, origen="prueba VE-2")
    base.update(cambios)
    return Cuenca(**base)


def test_f_un_caso_a_mano_con_las_ecuaciones_transcritas(MH):
    """
    Pd = 100 mm, A = 55.9 km2, L = 15 km, S = 0.02, CN = 75. A mano:
      Tc = 0.3 · (15 / 0.02^0.25)^0.76 = 0.3 · (15 / 0.376060)^0.76
         = 0.3 · 39.8873^0.76 = 4.94032 h
      K  = 1 + 4.94032^1.25 / (4.94032^1.25 + 14) = 1.344734
      KA = 1 − log10(55.9)/15 = 1 − 1.747412/15 = 0.883506
      P  = 0.883506 · 100 = 88.3506 mm
      I  = (88.3506/24) · 11^((28^0.1 − 4.94032^0.1)/(28^0.1 − 1))
         = 3.681274 · 11^0.58 = 14.16644 mm/h
      Po = 5000/75 − 50 = 16.6667 mm
      C  = (100 − 16.6667)(100 + 383.333)/(100 + 183.333)^2 = 0.501730
      Q  = 0.278 · 0.501730 · 14.16644 · 55.9 · 1.344734 = 148.533 m3/s
    """
    h = _a_mano(A=AREA_RM_KM2, L_km=L_RM_KM, S=S_RM, CN=CN_RM, Pd=100.0)
    dorado = dict(Tc=4.94032, K=1.344734, KA=0.883506, P=88.3506, I=14.16644,
                  Po=16.6667, C=0.501730, Q=148.533)
    for clave, valor in dorado.items():
        assert h[clave] == pytest.approx(valor, rel=REL_DORADO), clave
    assert MH.factor_reductor_por_area(AREA_RM_KM2) == pytest.approx(h["KA"], rel=REL)
    assert MH.intensidad_racional_modificado_mm_h(P_mm=h["P"], Tc_h=h["Tc"]) \
        == pytest.approx(h["I"], rel=REL)
    assert MH.umbral_de_escorrentia_mm(CN_RM) == pytest.approx(h["Po"], rel=REL)
    assert MH.coeficiente_racional_modificado(Pd_mm=100.0, CN=CN_RM) \
        == pytest.approx(h["C"], rel=REL)
    assert MH.caudal_racional_modificado(C=h["C"], I_mm_h=h["I"],
                                         area_km2=AREA_RM_KM2, K=h["K"]) \
        == pytest.approx(h["Q"], rel=REL)


def test_f_una_cuenca_de_55_9_km2_se_calcula_por_el_racional_modificado(MH, serie):
    """La cuenca de 55.9 km2 entera, con la lluvia de diseño de la serie."""
    cuenca = _cuenca_rm(MH)
    with _declarados({FEN: "serie_completa"}):
        c = MH.caudal_de_diseno(cuenca, serie, 71)
    Pd = c.P24_TR_mm
    por = {p.codigo: p for p in c.pasos}
    assert Pd == pytest.approx(por["1b.2"].resultado.valor, rel=REL)
    h = _a_mano(A=AREA_RM_KM2, L_km=L_RM_KM, S=S_RM, CN=CN_RM, Pd=Pd)
    assert c.calculado and c.metodo_tc == "temez"
    assert c.tc_min == pytest.approx(h["Tc"] * 60, rel=REL)
    assert c.duracion_min == pytest.approx(c.tc_min, rel=REL)
    assert c.K_uniformidad == pytest.approx(h["K"], rel=REL)
    assert c.I_mm_h == pytest.approx(h["I"], rel=REL)
    assert c.C == pytest.approx(h["C"], rel=REL)
    assert c.Q_m3s == pytest.approx(h["Q"], rel=REL)
    fundamentos = [p.fundamento_id for p in c.pasos]
    assert fundamentos == ["FH.SERIE", "FH.AJUSTE", "FH.KS", "FH.FEN",
                           "FH.CONSISTENCIA", "FH.TC", "FH.RM_INTENSIDAD",
                           "FH.RM_C", "FH.RM_CAUDAL", "FH.Q_ESPECIFICO"]
    assert [p.codigo for p in c.pasos][-5:] == ["1b.4", "1b.5", "1b.6",
                                                 "1b.7", "1b.8"]
    assert "racional modificado" in c.de_donde
    # El paso del caudal lleva su umbral (770 km2, exclusivo) con su cita.
    q = por["1b.7"]
    assert q.umbral.valor == pytest.approx(770.0, rel=REL_TRANSPORTE) and \
        q.umbral.cita_id == "MC_HHD.3.12.2.1#TC"
    assert q.formula_cita_id == "MC_HHD.3.12.2.1#K"
    # Y el paso del tiempo de concentracion NO dice «uso hibrido»: aqui la
    # formula de Temez es la del metodo con que se calcula el caudal.
    assert "HIBRIDO" not in por["1b.4"].nota_del_proyecto


def test_f_el_metodo_esta_adaptado_a_espana_y_se_avisa(MH, serie):
    with _declarados({FEN: "serie_completa"}):
        c = MH.caudal_de_diseno(_cuenca_rm(MH), serie, 71)
    assert any("adaptada para las condiciones climáticas de España" in a
               for a in c.avisos)


def test_f_la_ecuacion_35_lleva_Pd_y_no_la_P_corregida_y_se_declara(MH, serie):
    """
    La pagina escribe Pd en la (35) y P = kA·Pd en la (34): se aplica como
    esta escrito, SIN corregirlo, y se declara en el punto de uso.
    """
    import math
    with _declarados({FEN: "serie_completa"}):
        c = MH.caudal_de_diseno(_cuenca_rm(MH), serie, 71)
    P = c.P24_TR_mm * (1 - math.log10(AREA_RM_KM2) / 15)
    con_P = _a_mano(A=AREA_RM_KM2, L_km=L_RM_KM, S=S_RM, CN=CN_RM, Pd=P)
    assert c.C != pytest.approx(con_P["C"], rel=REL_DISTINTO)
    paso_c = next(p for p in c.pasos if p.fundamento_id == "FH.RM_C")
    nota = paso_c.nota_del_proyecto
    assert "Pd" in nota and "no la P corregida" in nota and "sin corregir" in nota
    assert {"MC_HHD.3.12.2.1#C", "MC_HHD.3.11#T07"} <= set(paso_c.citas_textuales)


def test_f_K_va_siempre_y_no_lo_gobierna_el_criterio_del_hibrido(MH, serie):
    """
    En el metodo completo K es parte de la ec. (29): el criterio
    'coeficiente_uniformidad_temez' decide solo el uso hibrido (Temez con el
    racional simple, por debajo de 10 km2). Tampoco la relacion
    intensidad-duracion: la intensidad es la de la ec. (34).
    """
    with _declarados({FEN: "serie_completa"}):
        base = MH.caudal_de_diseno(_cuenca_rm(MH), serie, 71)
    with _declarados({FEN: "serie_completa",
                      "coeficiente_uniformidad_temez": "no_aplicar",
                      "relacion_intensidad_duracion":
                          "tabla_04_coeficientes_de_duracion"}):
        otra = MH.caudal_de_diseno(_cuenca_rm(MH), serie, 71)
    assert otra.Q_m3s == pytest.approx(base.Q_m3s, rel=REL)
    assert otra.K_uniformidad == pytest.approx(base.K_uniformidad, rel=REL)
    assert base.K_uniformidad > 1


@pytest.mark.parametrize("area,metodo", [(9.99, "FH.RACIONAL"),
                                         (10.0, "FH.RM_CAUDAL"),
                                         (769.9, "FH.RM_CAUDAL")])
def test_f_la_frontera_de_10_km2_separa_los_dos_metodos(MH, serie, area, metodo):
    """«A<10 Km2» (pag. 49): por debajo el simple, desde 10 el modificado."""
    with _declarados({FEN: "serie_completa"}):
        c = MH.caudal_de_diseno(_cuenca_rm(MH, area_km2=area), serie, 71)
    assert metodo in [p.fundamento_id for p in c.pasos]
    assert MH.metodo_de_caudal(area) == (
        MH.METODO_RACIONAL if area < 10 else MH.METODO_RACIONAL_MODIFICADO)


@pytest.mark.parametrize("area", [770.0, 800.0, 30000.0])
def test_f_desde_770_km2_no_se_evalua_y_nombra_los_metodos_sin_implementar(
        MH, serie, area):
    from src.modelos import (MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA,
                             MetodoNoEvaluableError)
    with _declarados({FEN: "serie_completa"}):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            MH.caudal_de_diseno(_cuenca_rm(MH, area_km2=area), serie, 71)
    texto = str(exc.value)
    assert texto.startswith(MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA)
    for trozo in ("770", "Snyder", "30 a 30 000", "58", "SCS", "hasta 30",
                  "56", "HEC-HMS", "3.12.4", "no implementa", "Q_m3s"):
        assert trozo in texto, trozo


@pytest.mark.parametrize("L_km,S,area", [(0.5, 0.2, 12.0),        # Tc 0.24 h
                                         (400.0, 0.0001, 700.0)]) # Tc 164 h
def test_f_tc_fuera_de_0_25_a_24_h_no_se_evalua(MH, serie, L_km, S, area):
    from src.modelos import (MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA,
                             MetodoNoEvaluableError)
    cuenca = _cuenca_rm(MH, area_km2=area, L_cauce_m=L_km * 1000,
                        S_cauce_cuenca=S)
    with _declarados({FEN: "serie_completa"}):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            MH.caudal_de_diseno(cuenca, serie, 71)
    texto = str(exc.value)
    assert texto.startswith(MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA)
    assert "0.25" in texto and "24" in texto
    # Desde 10 km2 otro metodo de tiempo de concentracion no es remedio: el
    # mensaje remite a los metodos de hidrograma y al caudal declarado.
    assert "Snyder" in texto and "Q_m3s" in texto


def test_f_desde_10_km2_el_tiempo_de_concentracion_es_el_de_la_ec_30(MH, serie):
    from src.modelos import MetodoNoEvaluableError
    cuenca = _cuenca_rm(MH, metodo_tc="kirpich", ajuste_kirpich="ninguno")
    with _declarados({FEN: "serie_completa"}):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            MH.caudal_de_diseno(cuenca, serie, 71)
    assert "temez" in str(exc.value) and "(30)" in str(exc.value)


def test_f_sin_numero_de_curva_desde_10_km2_falta_un_dato(MH, serie):
    """CN es columna opcional (la de la ecuacion de retardo, REUSADA): desde
    10 km2 la exige la ec. (35), y se dice antes de ajustar nada."""
    from src.modelos import DatoFaltanteError
    with pytest.raises(DatoFaltanteError) as exc:
        MH.caudal_de_diseno(_cuenca_rm(MH, CN=None), serie, 71)
    assert exc.value.campo == "CN" and "(35)" in str(exc.value)


def test_f_un_umbral_de_escorrentia_mayor_que_la_lluvia_no_se_rellena(MH, serie):
    """CN = 30: Po = 116.7 mm > Pd ≈ 99.8 mm, y la (35) da C <= 0."""
    from src.modelos import MetodoNoEvaluableError
    with _declarados({FEN: "serie_completa"}):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            MH.caudal_de_diseno(_cuenca_rm(MH, CN=30.0), serie, 71)
    assert "umbral de escorrentia" in str(exc.value)


def test_f_pasa_por_la_puerta_del_criterio_fen(MH, serie):
    from src.modelos import CriterioPendienteError
    from tests.apoyo.criterios import sin_valor
    with sin_valor(FEN):
        with pytest.raises(CriterioPendienteError):
            MH.caudal_de_diseno(_cuenca_rm(MH), serie, 71)


def test_f_el_limite_de_770_km2_es_exclusivo_y_un_nan_cae_fuera(MH):
    """«áreas menores de 770 km2»: desigualdad estricta, condicion en
    positivo (un NaN cae fuera)."""
    from src.modelos import MetodoNoEvaluableError
    assert MH.exigir_alcance_del_racional_modificado(769.9) is None
    for fuera in (770.0, float("nan")):
        with pytest.raises(MetodoNoEvaluableError):
            MH.exigir_alcance_del_racional_modificado(fuera)


def test_f_la_cuneta_sigue_con_el_racional_simple_y_su_limite(MH, serie):
    """GUARDIA (pasaba antes y tiene que seguir pasando). El num. 4.1.2.1 b)
    escribe la ecuacion del racional SIMPLE: el aporte de una cuneta no pasa
    al modificado (y un area tributaria de 10 km2 no es una cuneta)."""
    from src.modelos import MetodoNoEvaluableError
    with _declarados({FEN: "serie_completa"}):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            MH.caudal_de_aporte_cuneta(_cuenca_rm(MH, area_km2=12.0), serie, 71)
    assert "hidrograma unitario" in str(exc.value)


def test_f_las_citas_de_las_ecuaciones_estan_en_el_registro(reg):
    from src.normativa.esquema import Caracter
    paginas = {"MC_HHD.3.12.2.1#METODO": ("50", 53),
               "MC_HHD.3.12.2.1#KA": ("51", 54),
               "MC_HHD.3.12.2.1#P": ("52", 55),
               "MC_HHD.3.12.2.1#I": ("52", 55),
               "MC_HHD.3.12.2.1#C": ("52", 55),
               "MC_HHD.3.12.3.2a#AREA": ("56", 59),
               "MC_HHD.3.12.3.2b#AREA": ("58", 61),
               "MC_HHD.3.12.4": ("58", 61),
               "MC_HHD.3.11#T07": ("47", 50)}
    for cita_id, (impresa, pdf) in paginas.items():
        c = reg.cita(cita_id)
        assert (c.pagina_impresa, c.pagina_pdf) == (impresa, pdf), cita_id
        assert c.verificado is not None, cita_id
    metodo = reg.cita("MC_HHD.3.12.2.1#METODO")
    assert "adaptada para las condiciones climáticas de España" in \
        metodo.texto_literal.texto
    assert reg.cita("MC_HHD.3.12.3.2a#AREA").texto_literal.texto == (
        "Este método es recomendable tan solo para cuencas de hasta a 30 Km2.")
    assert reg.cita("MC_HHD.3.12.3.2b#AREA").texto_literal.texto == (
        "El rango de aplicación de este método es de 30 a 30 000 Km2")
    # Las dos lecturas del proyecto, con lo que juega en contra.
    ka = reg.cita("MC_HHD.3.12.2.1#KA")
    assert ka.texto_literal.texto == "KA =   1 – (log10 A/15)"
    assert ka.interpretacion is not None and ka.interpretacion.en_contra
    assert reg.cita("MC_HHD.3.12.2.1#C").interpretacion.en_contra
    for f in ("FH.RM_INTENSIDAD", "FH.RM_C", "FH.RM_CAUDAL"):
        assert reg.fundamento(f).citas
    assert reg.cita("MC_HHD.3.12.3.2a#AREA").caracter is Caracter.RECOMENDACION


def test_f_los_literales_de_las_ecuaciones_son_N_en_constantes(MH):
    from src import constantes_normativas as CN
    assert CN.FACTOR_REDUCTOR_AREA_SI == {"divisor": 15}
    assert CN.INTENSIDAD_RACIONAL_MODIFICADO_SI == pytest.approx({
        "horas_del_dia": 24, "factor": 11, "horas_de_referencia": 28,
        "exponente": 0.1}, rel=REL_TRANSPORTE)
    assert CN.UMBRAL_ESCORRENTIA_SI == {"numerador": 5000, "resta": 50}
    assert CN.COEFICIENTE_RACIONAL_MODIFICADO == {"suma_numerador": 23,
                                                  "suma_denominador": 11}


def test_f_el_fixture_de_prueba_tiene_la_cuenca_de_10_a_770_km2(MH):
    primera = CUENCAS_RM.read_text(encoding="utf-8").splitlines()[0]
    assert primera.startswith("#") and ROTULO_DE_PRUEBA in primera
    c = MH.cargar_cuencas(CUENCAS_RM)[ID_RM]
    assert 10 <= c.area_km2 < 770 and c.CN is not None
    assert c.area_km2 == pytest.approx(AREA_RM_KM2, rel=REL_TRANSPORTE)
    # Las cuencas de la corrida de referencia no se tocaron.
    assert {k: v.area_km2 for k, v in MH.cargar_cuencas(CUENCAS).items()} == \
        pytest.approx({"A-01": 8.5, "A-02": 2.1, "B-01": 0.18},
                      rel=REL_TRANSPORTE)


def test_f_de_punta_a_punta_por_el_servicio(tmp_path):
    """El CSV de puntos con A-01 de 5590 ha (55.9 km2) y Q vacio."""
    import csv
    from src import servicio
    with PUNTOS.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    for fila in filas:
        if fila["id"] == ID_RM:
            fila.update({"Q_m3s": "", "area_ha": "5590"})
    ruta = tmp_path / "puntos.csv"
    with ruta.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    externos = servicio.cargar_datos_externos(None, {"luz_m": 2.0, "TW_m": 0.0})
    h = servicio.cargar_hidrologia(CUENCAS_RM, ESTACION)
    with _declarados({FEN: "serie_completa"}):
        informe = servicio.correr(ruta, externos, "perfil", h)
    punto = next(i for i in informe.puntos if i.punto.id == ID_RM)
    assert punto.caudal is not None and punto.caudal.calculado
    assert "FH.RM_CAUDAL" in [p.fundamento_id for p in punto.caudal.pasos]


def test_f_el_contrato_y_la_ficha_T1_08_lo_dicen():
    contrato = (RAIZ / "docs" / "contrato_entradas.md").read_text(encoding="utf-8")
    seccion = contrato[contrato.index("## 2-bis"):contrato.index("## 3.")]
    assert "racional modificado" in seccion and "770" in seccion
    assert "Desde 10 km² el método racional no se evalúa" not in seccion
    fichas = (RAIZ / "docs" / "decisiones_diferidas.md").read_text(encoding="utf-8")
    i = fichas.index("## T1-08")
    t108 = fichas[i:fichas.index("\n## ", i + 3)]
    assert "Cerrado (VE-2)" in t108
    assert "que el Manual da para España" not in t108
    assert "## VE2-F" in fichas


# ===========================================================================
# (d) Factor de intervalo fijo de la serie de 24 h, criterio [A] — VE1-02 (d)
# ===========================================================================
# El Manual usa la maxima en 24 horas SIN conversion: «Ordinariamente solo se
# cuenta con lluvias máximas en 24 horas, por lo que el valor de la
# Intensidad ... se estima a partir de la precipitación máxima en 24 horas,
# multiplicada por un coeficiente de duración» (num. 3.8.1, pag. impresa 36),
# y la fila de 24 horas de su Tabla Nº 04 vale 1.00 (pag. impresa 37). El 1.13
# no esta en ningun PDF del repositorio de normas. Valor de archivo 1.00,
# ventana 1.00-1.13.

FACTOR = "factor_intervalo_fijo_p24"


def test_d_el_criterio_es_A_de_perfil_con_valor_1_y_ventana_hasta_1_13():
    from src import criterios_adoptados as ca
    c = ca.CRITERIOS[FACTOR]
    assert c.valor == pytest.approx(1.0, rel=REL_TRANSPORTE)
    assert isinstance(c.valor, float)
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert c.forma == "float"
    assert c.sensibilidad == pytest.approx((1.0, 1.13), rel=REL_TRANSPORTE)
    assert c.resolucion is not None
    texto = c.justificacion + " " + c.fuente
    for trozo in ("1.13", "sin fuente", "repositorio de normas", "[C]", "OMM",
                  "Weiss", "3.8.1", "Tabla N 04"):
        assert trozo in texto, trozo


@pytest.mark.parametrize("fuera", [0.99, 1.14, 1.2])
def test_d_fuera_de_la_ventana_no_se_declara(fuera):
    from src import criterios_adoptados as ca
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(FACTOR, fuera)
    assert FACTOR not in ca.valores_dinamicos()


@pytest.mark.parametrize("distribucion", ["normal", "lognormal_2p", "gumbel",
                                          "mejor_ajuste_ks"])
def test_d_con_1_13_la_lluvia_de_diseno_sube_un_13_por_ciento_exacto(
        MH, serie, distribucion):
    """
    Las tres distribuciones que el programa ajusta son de escala: multiplicar
    cada dato por f multiplica el cuantil por f y deja D de Kolmogorov-
    Smirnov igual. Por eso aplicar el factor A LA SERIE, antes del ajuste, da
    EXACTAMENTE f veces la lluvia de diseño (y la misma distribucion
    elegida), y ademas corrige lo observado con que se contrasta.

    Sobre la serie SIN los tres años FEN: con ellos la Normal y la Gumbel no
    pasan la prueba de bondad (D = 0.26 > 0.21) y no hay cuantil que medir;
    sin ellos pasan las tres.
    """
    serie = replace(serie, registros=tuple(r for r in serie.registros
                                           if not r.fen))
    base = {FEN: "serie_completa",
            "distribucion_precipitacion_maxima": distribucion}
    with _declarados(base):
        sin, *_ = MH.precipitacion_de_diseno(serie, 71)
    with _declarados({**base, FACTOR: 1.13}):
        con, evaluados, _, pasos, avisos = MH.precipitacion_de_diseno(serie, 71)
    assert con.P_TR_mm == pytest.approx(1.13 * sin.P_TR_mm, rel=REL_ESCALA)
    assert con.distribucion == sin.distribucion
    assert con.D == pytest.approx(sin.D, rel=REL, abs=ABS_CERO)
    # Lo observado con que se contrasta tambien lleva el factor.
    ajuste_paso = next(p for p in pasos if p.codigo == "1b.2")
    with _declarados(base):
        *_, pasos_sin, _ = MH.precipitacion_de_diseno(serie, 71)
    sin_paso = next(p for p in pasos_sin if p.codigo == "1b.2")
    assert ajuste_paso.umbral.valor == pytest.approx(
        1.13 * sin_paso.umbral.valor, rel=REL_ESCALA)
    assert any("1.13" in a and FACTOR in a for a in avisos)


def test_d_con_1_00_la_lluvia_es_la_de_la_serie_tal_cual(MH, serie):
    """
    GUARDIA (valia antes del factor y tiene que seguir valiendo con el valor
    de archivo).

    Con el valor de archivo la lluvia de diseño es la de la serie SIN
    conversion: la Normal ajustada aqui a mano con `statistics` da el mismo
    cuantil, bit a bit en la practica, y no hay aviso del factor. Sobre la
    serie sin los años FEN, donde la Normal pasa la prueba de bondad.
    """
    from statistics import NormalDist, fmean, stdev
    serie = replace(serie, registros=tuple(r for r in serie.registros
                                           if not r.fen))
    valores = [r.p24_mm for r in serie.registros]
    esperado = NormalDist(fmean(valores), stdev(valores)).inv_cdf(1 - 1 / 71)
    with _declarados({FEN: "serie_completa",
                      "distribucion_precipitacion_maxima": "normal"}):
        ajuste, *_, avisos = MH.precipitacion_de_diseno(serie, 71)
    assert ajuste.P_TR_mm == pytest.approx(esperado, rel=REL_ESCALA)
    assert not any(FACTOR in a for a in avisos)


def test_d_la_memoria_imprime_el_factor_y_su_procedencia(MH, serie):
    with _declarados({FEN: "serie_completa"}):
        ajuste, *_, pasos, _ = MH.precipitacion_de_diseno(serie, 71)
    p = next(x for x in pasos if x.codigo == "1b.2")
    factor = next(m for m in p.sustitucion if m.simbolo == "f_24h")
    assert factor.valor == pytest.approx(1.0, rel=REL_TRANSPORTE)
    assert FACTOR in factor.procedencia and "[A]" in factor.procedencia
    eleccion = next(e for e in p.elecciones if e.clave_criterio == FACTOR)
    assert eleccion.fundamento_id == "FH.FACTOR_P24"
    assert eleccion.cita_id == "MC_HHD.3.8.1#P24"
    assert len(eleccion.entre) == 2
    assert f"{ajuste.P_TR_mm:.1f}" in eleccion.entre[0]
    assert f"{1.13 * ajuste.P_TR_mm:.1f}" in eleccion.entre[1]


def test_d_la_consistencia_sigue_hablando_de_lo_registrado(MH, serie):
    """El aviso (e) describe los datos REGISTRADOS, no los multiplicados."""
    with _declarados({FEN: "serie_completa", FACTOR: 1.13}):
        *_, pasos, _ = MH.precipitacion_de_diseno(serie, 71)
    p = _paso_de_consistencia(pasos)
    por = {m.simbolo: m.valor for m in p.sustitucion}
    assert por["maximo"] == pytest.approx(max(r.p24_mm for r in serie.registros),
                                          rel=REL)


def test_d_el_caudal_calculado_sube_con_el_factor_en_los_dos_metodos(MH, serie,
                                                                     cuencas):
    """
    En el racional simple Q es proporcional a P24 (Q sube un 13 %); en el
    modificado C depende de Pd y Q sube MAS de un 13 %.
    """
    with _declarados({FEN: "serie_completa"}):
        simple = MH.caudal_de_diseno(cuencas["A-02"], serie, 71)
        rm = MH.caudal_de_diseno(_cuenca_rm(MH), serie, 71)
    with _declarados({FEN: "serie_completa", FACTOR: 1.13}):
        simple_f = MH.caudal_de_diseno(cuencas["A-02"], serie, 71)
        rm_f = MH.caudal_de_diseno(_cuenca_rm(MH), serie, 71)
    assert simple_f.P24_TR_mm == pytest.approx(1.13 * simple.P24_TR_mm,
                                               rel=REL_ESCALA)
    assert simple_f.Q_m3s == pytest.approx(1.13 * simple.Q_m3s, rel=REL)
    assert rm_f.Q_m3s > 1.13 * rm.Q_m3s


def test_d_el_nivel_de_perfil_lo_mide_una_corrida_de_perfil(tmp_path):
    """La corrida de perfil con hidrologia lo invoca; con Q lleno, no."""
    import csv
    from src import criterios_adoptados as ca, servicio
    with PUNTOS.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    for fila in filas:
        if fila["id"] == "A-02":
            fila["Q_m3s"] = ""
    ruta = tmp_path / "puntos.csv"
    with ruta.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    externos = servicio.cargar_datos_externos(None, {"luz_m": 2.0, "TW_m": 0.0})
    h = servicio.cargar_hidrologia(CUENCAS, ESTACION)
    with _declarados({FEN: "serie_completa"}):
        informe = servicio.correr(ruta, externos, "perfil", h)
    assert FACTOR in informe.contexto.criterios_usados
    assert ca.CRITERIOS[FACTOR].nivel == ca.NIVEL_PERFIL
    base = servicio.correr(PUNTOS, externos, "perfil")
    assert FACTOR not in base.contexto.criterios_usados


def test_d_la_cita_del_3_8_1_y_el_fundamento(reg):
    from src.normativa.esquema import Verbo
    c = reg.cita("MC_HHD.3.8.1#P24")
    assert (c.numeral, c.pagina_impresa, c.pagina_pdf) == ("3.8.1", "36", 39)
    assert "precipitación máxima en 24 horas" in c.texto_literal.texto
    f = reg.fundamento("FH.FACTOR_P24")
    assert f.verbo is Verbo.DEFINE
    assert "MC_HHD.3.8.1#P24" in f.citas and "MC_HHD.3.8.1#T04" in f.citas


def test_d_entra_a_la_validacion_de_sensibilidad_donde_se_lee():
    """
    Se barre sobre la variante con el caudal CALCULADO: en el juego completo
    el caudal es el declarado y el factor no se lee.
    """
    from tests.apoyo import sensibilidad as S
    barridos = [b for b in S.BARRIDOS if b.clave == FACTOR]
    assert len(barridos) == 1
    b = barridos[0]
    assert b.base == "juego_caudal_calculado" and b.grupo == S.GRUPO_HIDROLOGIA
    assert S.valores_de(b) == pytest.approx((1.0, 1.13), rel=REL_TRANSPORTE)


def test_d_la_ficha_lo_dice():
    fichas = (RAIZ / "docs" / "decisiones_diferidas.md").read_text(encoding="utf-8")
    i = fichas.index("## VE2-D")
    ficha = fichas[i:]
    for trozo in ("1.13", "OMM", "Weiss", "[C]", "antes del ajuste"):
        assert trozo in ficha, trozo
