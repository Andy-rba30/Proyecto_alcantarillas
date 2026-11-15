"""
tests/test_t1_hidrologia.py — aceptacion de T-1 de la cadena T
==============================================================
La Fase 1-bis: el caudal de diseño de las Familias A y B calculado dentro del
programa (`src/modulos/MH_hidrologia.py`) a partir de la cuenca de cada obra y
de la serie de lluvia de una estacion, sin quitar la via de siempre (`Q_m3s`
lleno gana). Cierra INF-3.1.2 a INF-3.1.6, INF-5.2.5 e INF-5.1.3, y da
consumidor real a 'homogeneidad_serie_fen' (INF-3.1.4).

DE DONDE SALEN LOS DORADOS, que es lo primero que hay que decir: el num.
3.12.2 del Manual de Hidrologia NO trae ejemplo numerico (leido entero, pags.
impresas 49 y 50), ni lo trae la Tabla N 05. Todos los valores esperados de
este archivo estan CALCULADOS A MANO con la formula que la pagina imprime, y
cada uno lleva la cuenta escrita al lado. No son la salida del programa: los
que se contrastan contra un segundo calculo lo hacen con `statistics` y
`math` aqui mismo, por un camino que no pasa por `MH_hidrologia`.

LOS DATOS SON SINTETICOS. `tests/fixtures/hidrologia/` trae una serie y tres
cuencas inventadas, rotuladas «DATOS DE PRUEBA, NO DEL PROYECTO» en su primera
linea, y un test lo exige. Ningun valor de este archivo es del corredor.

COMO SE MIDIO EL ROJO. Este archivo se escribio DESPUES de la implementacion,
no antes: la regla 4 de la cadena pide tests primero y T-1 no la cumplio en
ese orden, y se dice aqui en vez de fingirlo. Lo que si se hizo es medir el
rojo sobre el arbol anterior: el archivo, con un `xfail(strict=True)` de
modulo, se corrio sobre un checkout de `origin/main` en `87d1ce7` (T-0) con
los fixtures copiados: 119 tests, 105 xfailed y 14 XPASS. Los catorce que
ya pasaban valen antes y despues y no dependen del codigo nuevo: los doce
hechos del PDF (`test_lo_que_las_formulas_necesitan_esta_en_la_pagina`), el
rotulo de los fixtures y el periodo de retorno del fixture, que T-1 no mueve.
"""

from __future__ import annotations

import ast
import csv
import json
import math
from pathlib import Path
from statistics import NormalDist, fmean, stdev

import pytest

from tests.apoyo.aproximacion import REL_TRANSPORTE

RAIZ = Path(__file__).resolve().parent.parent
FIXTURES = RAIZ / "tests" / "fixtures" / "hidrologia"
CUENCAS = FIXTURES / "cuencas_prueba.csv"
ESTACION = FIXTURES / "estacion_prueba.csv"
PUNTOS = RAIZ / "tests" / "ejemplo_puntos.csv"
ROTULO_DE_PRUEBA = "DATOS DE PRUEBA, NO DEL PROYECTO"
ESTACION_DE_PRUEBA = "PRUEBA-SINTETICA"

REL = 1e-9          # dos caminos de la misma aritmetica
PASO_T08 = 0.05     # salto de C entre columnas vecinas de la Tabla N 08
ABS_T08 = 1e-9      # ruido de restar dos celdas de dos decimales
FEN = "homogeneidad_serie_fen"


# ---------------------------------------------------------------------------
# Apoyos
# ---------------------------------------------------------------------------

def _mh():
    from src.modulos import MH_hidrologia
    return MH_hidrologia


def _declarados(valores):
    from tests.apoyo.criterios import declarados
    return declarados(valores)


@pytest.fixture()
def MH():
    return _mh()


@pytest.fixture()
def serie(MH):
    return MH.cargar_estacion(ESTACION)[ESTACION_DE_PRUEBA]


@pytest.fixture()
def cuencas(MH):
    return MH.cargar_cuencas(CUENCAS)


@pytest.fixture()
def externos():
    from src import servicio
    return servicio.cargar_datos_externos(None, {"luz_m": 2.0, "TW_m": 0.0})


@pytest.fixture()
def hidrologia():
    from src import servicio
    return servicio.cargar_hidrologia(CUENCAS, ESTACION)


def _csv_con(tmp_path, cambios, nombre="puntos.csv"):
    """Una copia de `tests/ejemplo_puntos.csv` con celdas cambiadas por id."""
    with PUNTOS.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    for fila in filas:
        fila.update(cambios.get(fila["id"], {}))
    destino = tmp_path / nombre
    with destino.open("w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    return destino


def _cuencas_con(tmp_path, filas, nombre="cuencas.csv"):
    """Un CSV de cuencas de prueba escrito fila a fila (dicts)."""
    columnas = ["id", "area_km2", "L_cauce_m", "S_cauce_cuenca", "S_terreno",
                "cobertura", "suelo", "estacion", "metodo_tc", "H_desnivel_m",
                "ajuste_kirpich", "CN"]
    destino = tmp_path / nombre
    with destino.open("w", encoding="utf-8", newline="") as fh:
        fh.write(f"# {ROTULO_DE_PRUEBA}\n")
        escritor = csv.DictWriter(fh, fieldnames=columnas, restval="")
        escritor.writeheader()
        escritor.writerows(filas)
    return destino


# Una cuenca chica, para que el caudal calculado quepa en un tubo y el punto
# se dimensione: 0.12 km2 de cultivos sobre suelo permeable. El CSV de puntos
# del test tiene que decir la MISMA area en su columna `area_ha` (12 ha): con
# las 210 ha del fixture el programa se detiene por dos areas para una cuenca.
CUENCA_CHICA = {"id": "A-02", "area_km2": "0.12", "L_cauce_m": "600",
                "S_cauce_cuenca": "0.04", "S_terreno": "0.04",
                "cobertura": "cultivos", "suelo": "permeable",
                "estacion": ESTACION_DE_PRUEBA, "metodo_tc": "kirpich",
                "ajuste_kirpich": "ninguno"}
AREA_HA_DE_LA_CUENCA_CHICA = "12"
A02_SIN_Q = {"A-02": {"Q_m3s": "", "area_ha": AREA_HA_DE_LA_CUENCA_CHICA}}
REDONDEO_DEL_UMBRAL = 1e-5      # el umbral se imprime con tres decimales


PASOS_DE_LA_FASE_1B = ["1b.1", "1b.2", "1b.3", "1b.3b", "1b.4", "1b.5",
                       "1b.6", "1b.7", "1b.8"]


def _por_id(informe, id_punto):
    return next(i for i in informe.puntos if i.punto.id == id_punto)


# ===========================================================================
# 1. Lo que la fuente dice: registro y constantes
# ===========================================================================

def test_los_fixtures_estan_rotulados_como_datos_de_prueba():
    for ruta in (CUENCAS, ESTACION):
        primera = ruta.read_text(encoding="utf-8").splitlines()[0]
        assert primera.startswith("#") and ROTULO_DE_PRUEBA in primera, ruta


def test_la_tabla_05_no_lista_a_temez_y_el_registro_lo_dice():
    """El prompt de T-1 suponia a Temez en la Tabla N 05: no esta."""
    from src.normativa import registro
    t = registro.construir().tabla("MC_HHD.T05")
    claves = [t.clave_corta(f) for f in t.filas]
    assert claves == ["kirpich", "california_culverts_practice", "izzard",
                      "federal_aviation_administration", "onda_cinematica",
                      "retardo_scs"]
    assert any("Temez" in a.que_no_dice for a in t.afirmaciones_negativas)
    # Temez vive en el num. 3.12.2.1, con L en km y Tc en horas.
    cita = registro.construir().cita("MC_HHD.3.12.2.1#TC")
    assert cita.numeral == "3.12.2.1" and cita.pagina_impresa == "51"


def test_la_tabla_08_esta_entera_y_sus_celdas_son_las_de_la_pagina():
    """Quince filas por cinco columnas; seis celdas leidas de la imagen."""
    from src.constantes_normativas import TABLA_08_COEFICIENTE_DE_ESCORRENTIA as T
    assert len(T) == 15 and all(len(fila) == 5 for fila in T.values())
    leidas = {
        ("sin_vegetacion", "impermeable", "pronunciada"): 0.80,
        ("sin_vegetacion", "permeable", "despreciable"): 0.30,
        ("cultivos", "semipermeable", "media"): 0.50,
        ("pastos_vegetacion_ligera", "impermeable", "alta"): 0.60,
        ("hierba_grama", "permeable", "suave"): 0.15,
        ("bosques_densa_vegetacion", "permeable", "despreciable"): 0.05,
    }
    for (cobertura, suelo, pendiente), c in leidas.items():
        assert T[(cobertura, suelo)][pendiente] == pytest.approx(c, rel=REL_TRANSPORTE)
    # La estructura de la tabla, que es una comprobacion de transcripcion: C
    # baja 0.05 por columna hacia la derecha en TODAS las filas.
    orden = ("pronunciada", "alta", "media", "suave", "despreciable")
    for fila in T.values():
        for a, b in zip(orden, orden[1:]):
            assert fila[a] - fila[b] == pytest.approx(PASO_T08, abs=ABS_T08)


def test_la_tabla_08_no_tiene_fila_de_pavimento():
    from src.constantes_normativas import TABLA_08_COEFICIENTE_DE_ESCORRENTIA as T
    coberturas = {c for c, _ in T}
    assert coberturas == {"sin_vegetacion", "cultivos",
                          "pastos_vegetacion_ligera", "hierba_grama",
                          "bosques_densa_vegetacion"}
    from src.normativa import registro
    t = registro.construir().tabla("MC_HHD.T08")
    assert any("pavimento" in a.que_no_dice for a in t.afirmaciones_negativas)


def test_la_tabla_03_es_el_cuantil_exacto_de_kolmogorov_smirnov():
    """
    Lo que autoriza a cerrar la laguna de la tabla (n no tabulado) con el
    cuantil exacto: reproduce las 24 celdas impresas a sus dos decimales.
    """
    from scipy.stats import kstwo
    from src.constantes_normativas import TABLA_03_KS
    assert sorted(TABLA_03_KS) == [5, 10, 15, 20, 25, 30, 35, 40]
    for n, fila in TABLA_03_KS.items():
        assert sorted(fila) == pytest.approx([0.01, 0.05, 0.10], rel=REL_TRANSPORTE)
        for alfa, d in fila.items():
            exacto = round(float(kstwo.ppf(1 - alfa, n)), 2)
            assert exacto == pytest.approx(d, rel=REL_TRANSPORTE), (n, alfa)
    # Tres celdas leidas de la imagen.
    leidas = (TABLA_03_KS[5][0.05], TABLA_03_KS[25][0.10], TABLA_03_KS[40][0.01])
    assert leidas == pytest.approx((0.56, 0.24, 0.25), rel=REL_TRANSPORTE)


def test_la_tabla_04_son_dieciseis_coeficientes_de_duracion():
    from src.constantes_normativas import TABLA_04_COEFICIENTES_DE_DURACION as T
    assert sorted(T) == [1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 48]
    assert (T[1], T[6], T[12], T[24], T[48]) == pytest.approx(
        (0.25, 0.56, 0.79, 1.00, 1.32), rel=REL_TRANSPORTE)


def test_los_coeficientes_de_las_formulas_son_los_impresos():
    from src import constantes_normativas as CN
    impresos = {
        "RACIONAL_COEFICIENTE_SI": 0.278,
        "RACIONAL_AREA_MAX_KM2": 10.0,
        "TC_KIRPICH_SI": {"coeficiente": 0.01947, "exp_L": 0.77, "exp_S": -0.385},
        "TC_KIRPICH_RANGO_S": (0.03, 0.10),
        "TC_KIRPICH_AJUSTES": {"ninguno": 1,
                               "superficie_de_concreto_o_asfalto": 0.4,
                               "canal_de_concreto": 0.2},
        "TC_CALIFORNIA_SI": {"coeficiente": 0.0195, "exp_L": 3, "exp": 0.385},
        "TC_FAA_SI": {"coeficiente": 0.7035, "resta_C": 1.1, "exp_L": 0.50,
                      "exp_S": 0.333},
        "TC_RETARDO_SCS_SI": {"coeficiente": 0.0136, "exp_L": 0.8, "mil": 1000,
                              "resta": 9, "exp_CN": 0.7, "exp_S": 0.5},
        "TC_RETARDO_SCS_AREA_MAX_KM2": 8.0,
        "TC_TEMEZ_SI": {"coeficiente": 0.3, "exp_S": 0.25, "exp": 0.76},
        "UNIFORMIDAD_TEMEZ_SI": {"exponente": 1.25, "sumando": 14},
        "TC_TEMEZ_RANGO_H": (0.25, 24.0),
        "TC_TEMEZ_AREA_MAX_KM2": 770.0,
        "DICK_PESCHKE": {"minutos_en_24_h": 1440, "exponente": 0.25},
        "GUMBEL_MOMENTOS": {"alfa_por_sigma": 1.2825, "beta_resta_sigmas": 0.45},
    }
    for nombre, valor in impresos.items():
        assert getattr(CN, nombre) == pytest.approx(valor, rel=REL_TRANSPORTE), nombre
    assert CN.REGISTRO_MINIMO_RECOMENDADO_ANIOS == 25
    # UN solo coeficiente en la familia (auditoria de T-1, H12): el 1/3.6 con
    # que el num. 4.1.2.1 b) escribe el caudal de aporte de la cuneta no es
    # una segunda constante. Y las cuatro empiricas llevan el sufijo _SI que
    # la seccion «Unidades» de la constitucion pide (H13).
    assert not hasattr(CN, "CUNETA_APORTE_DIVISOR")
    for viejo in ("RACIONAL_COEFICIENTE", "TC_KIRPICH", "TC_CALIFORNIA", "TC_TEMEZ"):
        assert not hasattr(CN, viejo), viejo
    assert CN.KS_N_MINIMO_TABULADO == min(CN.TABLA_03_KS)


CITAS_DE_T1 = (
    "MC_HHD.3.4#FEN", "MC_HHD.3.4#REGISTRO", "MC_HHD.3.7.1", "MC_HHD.3.7.1.1",
    "MC_HHD.3.7.1.2", "MC_HHD.3.7.1.7", "MC_HHD.3.7.2b", "MC_HHD.3.7.2b#ELIGE",
    "MC_HHD.3.7.2b#T03", "MC_HHD.3.8.1#DURACION", "MC_HHD.3.8.1#T04",
    "MC_HHD.3.8.1#DICK_PESCHKE", "MC_HHD.3.9#T05", "MC_HHD.3.9#T05_KIRPICH",
    "MC_HHD.3.9#T05_CALIFORNIA", "MC_HHD.3.12.2", "MC_HHD.3.12.2#AREA",
    "MC_HHD.3.12.2#T08", "MC_HHD.3.12.2.1#TC", "MC_HHD.3.13",
    "MC_HHD.4.1.2.1b",
    # Las cuatro que sumo la auditoria adversarial de T-1.
    "MC_HHD.3.9#T05_FAA", "MC_HHD.3.9#T05_SCS", "MC_HHD.3.12.2.1#K",
    "MC_HHD.3.12.5#PIURA",
)
CITAS_DE_WSDOT_DE_T1 = ("WSDOT_HM.2-6.3#TC_MINIMO", "WSDOT_HM.2-6.2#T2-2",
                        "WSDOT_HM.2-6.2#FRECUENCIA")


@pytest.mark.parametrize("cita_id", CITAS_DE_T1)
def test_cada_cita_de_t1_esta_firmada_y_su_pagina_es_la_del_desfase(cita_id):
    """Firma de la sesion, y pagina PDF = impresa + 3 (el desfase del Manual)."""
    from src.normativa import registro
    c = registro.construir().cita(cita_id)
    assert c.verificado is not None and "T-1" in c.verificado.por
    assert c.pagina_pdf == int(c.pagina_impresa) + 3
    assert c.id in registro.construir().citas_referenciadas()


@pytest.mark.pdf
@pytest.mark.parametrize("pagina_pdf,texto", [
    (52, "Q = 0,278 CIA"),
    (52, "A<10 Km2"),
    (53, "Área de la cuenca (Km2)."),
    (53, "PENDIENTE DEL TERRENO"),
    (42, "(3 a 10%)"),
    (42, "FÓRMULA PARA tc (minutos)"),
    (54, "Longitud del cauce mayor (km)"),
    (54, "0.25 y 24 horas"),
    (40, "d = duración en minutos"),
    (35, "Fo(xm) = 1- m / (n+1)"),
    (32, "Utilizando el método de momentos"),
    (180, "Área aportante en Km2"),
    # Lo que sumo la auditoria adversarial de T-1.
    (43, "inferiores a 800 Ha"),
    (67, "Piura y Tumbes"),
])
def test_lo_que_las_formulas_necesitan_esta_en_la_pagina(pagina_pdf, texto):
    """Unidades y rangos de los que dependen las formulas, contra el PDF."""
    pytest.importorskip("fitz")
    from src.normativa import fuentes, registro
    from src.normativa.extraccion.pdf import aparece_en_pagina
    ruta = fuentes.ruta_pdf(registro.construir().fuente("MC_HHD"))
    if not ruta.exists():
        pytest.skip(f"no esta el PDF: {ruta}")
    assert aparece_en_pagina(ruta, pagina_pdf, texto)


@pytest.mark.pdf
@pytest.mark.parametrize("pagina_pdf,texto", [
    (46, "a minimum of 5 minutes shall be used as the duration"),
    (47, "shall never use a time of concentration that is less than 5 minutes"),
    (44, "10-year"),
    (44, "0.95"),
    (45, "Pavement and roofs"),
    (45, "Side slopes"),
])
def test_lo_que_se_toma_de_wsdot_esta_en_la_pagina(pagina_pdf, texto):
    """
    Las dos piezas [C] que la auditoria de T-1 pidio buscar en el WSDOT
    Hydraulics Manual (cap. 2): la duracion minima y la tabla de coeficientes
    con su incremento por frecuencia. El PDF vive solo en el repositorio de
    normas (`NORMAS_DIR`).
    """
    pytest.importorskip("fitz")
    from src.normativa import fuentes, registro
    from src.normativa.extraccion.pdf import aparece_en_pagina
    ruta = fuentes.ruta_pdf(registro.construir().fuente("WSDOT_HM"))
    if not ruta.exists():
        pytest.skip(f"no esta el PDF (NORMAS_DIR sin enlazar): {ruta}")
    assert aparece_en_pagina(ruta, pagina_pdf, texto)


@pytest.mark.parametrize("cita_id", CITAS_DE_WSDOT_DE_T1)
def test_las_citas_de_wsdot_de_t1_estan_firmadas_y_son_fuente_tecnica(cita_id):
    from src import criterios_adoptados as ca
    from src.normativa import registro
    c = registro.construir().cita(cita_id)
    assert c.fuente_id == "WSDOT_HM" and c.verificado is not None
    assert c.pagina_impresa.startswith("2-")
    # Ninguna es [N]: entran por un criterio [C], que dice que no son norma
    # peruana.
    for clave in ("duracion_minima_lluvia_min",
                  "coeficiente_escorrentia_superficie_vial"):
        criterio = ca.CRITERIOS[clave]
        assert criterio.etiqueta == "C" and "no norma peruana" in criterio.fuente
    # Y los cuatro coeficientes del criterio SON la tabla del registro.
    tabla = registro.construir().tabla("WSDOT_HM.T2-2")
    derivados = ca.CRITERIOS["coeficiente_escorrentia_superficie_vial"].valor
    for superficie, valor in derivados["coeficientes_10_anios"].items():
        assert set(tabla.fila(superficie).valores.values()) == {valor}


# ===========================================================================
# 4. La serie y los años FEN ('homogeneidad_serie_fen')
# ===========================================================================

def test_la_serie_de_prueba_declara_sus_anios_fen(serie, MH):
    assert len(serie.registros) == 40
    assert serie.anios_fen == (1983, 1998, 2017)
    # `cargar_entrada` cruza las dos: las tres cuencas nombran esa estacion.
    entrada = MH.cargar_entrada(CUENCAS, ESTACION)
    assert sorted(entrada.cuencas) == ["A-01", "A-02", "B-01"]
    assert entrada.ids_calculables() == frozenset(entrada.cuencas)
    assert entrada.cuenca_de("C-01") is None


def test_sin_declarar_el_tratamiento_fen_el_calculo_se_detiene(MH, serie):
    """T-1, punto 3: el criterio tiene consumidor real y bloquea el calculo."""
    from src.modelos import CriterioPendienteError
    from src import criterios_adoptados as ca
    assert ca.CRITERIOS[FEN].valor is None
    with pytest.raises(CriterioPendienteError) as exc:
        MH.precipitacion_de_diseno(serie, 71)
    assert exc.value.clave == FEN


def test_el_criterio_fen_es_una_categoria_de_tres_tratamientos():
    from src import criterios_adoptados as ca
    c = ca.CRITERIOS[FEN]
    assert c.forma == ca.FORMA_CATEGORIA and c.etiqueta == "A"
    assert c.sensibilidad == ("serie_completa", "serie_sin_fen", "dos_poblaciones")
    assert c.nivel == ca.NIVEL_PERFIL and "MC_HHD.3.4#FEN" in c.fuente
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(FEN, "con los años del Niño")
    ca.quitar_valor_dinamico(FEN)


def _con_fen_en(serie, anios):
    """La misma serie de prueba, con OTROS años marcados FEN."""
    from dataclasses import replace
    from src.modelos import RegistroDeLluvia
    return replace(serie, registros=tuple(
        RegistroDeLluvia(r.anio, r.p24_mm, r.anio in anios) for r in serie.registros))


# Tres años CORRIENTES de la serie de prueba. Marcados como FEN en lugar de
# los tres extremos, quitarlos SUBE la lluvia de diseño: es el caso en que
# `serie_sin_fen` es la mas conservadora de las dos, y pasa.
ANIOS_CORRIENTES = (1980, 2005, 2016)


def test_con_y_sin_fen_la_memoria_imprime_las_dos_precipitaciones(MH, serie):
    """La Fase 1-bis pide «reportar el ajuste con y sin ellos»."""
    with _declarados({FEN: "serie_completa"}):
        completo, _, trat, pasos, avisos = MH.precipitacion_de_diseno(serie, 71)
    otra = _con_fen_en(serie, ANIOS_CORRIENTES)
    with _declarados({FEN: "serie_sin_fen"}):
        sin_fen, _, trat2, pasos2, avisos2 = MH.precipitacion_de_diseno(otra, 71)
    assert (trat, trat2) == ("serie_completa", "serie_sin_fen")
    assert (completo.n, sin_fen.n) == (40, 37)
    for p, anios in ((pasos[0], "1983, 1998, 2017"), (pasos2[0], "1980, 2005, 2016")):
        assert p.codigo == "1b.1"
        entre = " | ".join(p.elecciones[0].entre)
        assert "serie_completa" in entre and "serie_sin_fen" in entre
        assert f"{completo.P_TR_mm:.1f} mm" in entre
        por_simbolo = {m.simbolo: m.valor for m in p.sustitucion}
        assert por_simbolo["años FEN"] == anios
        # H10: el paso dice de que periodo es la serie y que años le faltan.
        assert por_simbolo["periodo"] == "1980 a 2019"
        assert por_simbolo["años sin dato"] == "ninguno"
    assert f"{sin_fen.P_TR_mm:.1f} mm" in " | ".join(pasos2[0].elecciones[0].entre)


def test_serie_sin_fen_con_menos_lluvia_que_la_completa_detiene_el_calculo(MH, serie):
    """
    Auditoria de T-1 (H11), con la decision del dueño (ficha T1-09). La hoja
    de ruta manda «reportar el ajuste con y sin ellos, adoptar el mas
    conservador»: la sesion la habia rebajado a «no se impone» y se RESTAURO.
    `serie_sin_fen` sigue siendo declarable; cuando da MENOS lluvia que la
    serie completa el calculo hidrologico del punto SE DETIENE --un punto no
    queda dimensionado sobre un caudal que incumple la regla y la exigencia
    del num. 3.4--, con las dos lluvias y el remedio en el mensaje. Cuando da
    igual o mas, pasa, y el paso 1b.3b imprime el contraste.
    """
    from src.modelos import (MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA,
                             MetodoNoEvaluableError, TipoDeVeredicto)
    with _declarados({FEN: "serie_completa"}):
        completo, _, _, pasos, avisos = MH.precipitacion_de_diseno(serie, 71)
    # La otra lluvia, medida por el camino que no se detiene: la serie sin
    # sus tres años FEN, ajustada como serie completa.
    from dataclasses import replace
    neutra = replace(serie, registros=tuple(r for r in serie.registros if not r.fen))
    with _declarados({FEN: "serie_completa"}):
        sin_fen, *_ = MH.precipitacion_de_diseno(neutra, 71)
    assert sin_fen.P_TR_mm < completo.P_TR_mm        # quitar FEN baja la lluvia
    with _declarados({FEN: "serie_sin_fen"}):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            MH.precipitacion_de_diseno(serie, 71, id_punto="A-01")
    texto = str(exc.value)
    assert texto.startswith(MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA)
    for trozo in (f"{sin_fen.P_TR_mm:.1f} mm", f"{completo.P_TR_mm:.1f} mm",
                  "mas conservador", "num. 3.4",
                  f"declarar 'serie_completa' en '{FEN}'", "Q_m3s"):
        assert trozo in texto, trozo
    assert exc.value.id_punto == "A-01"
    # Con la serie completa el juicio CUMPLE y se imprime con las dos lluvias.
    juicio = pasos[3]
    assert juicio.codigo == MH.CODIGO_FEN == "1b.3b"
    assert juicio.fundamento_id == "FH.FEN"
    assert juicio.veredicto.tipo is TipoDeVeredicto.CUMPLE
    assert juicio.umbral.cita_id == "MC_HHD.3.4#FEN"
    assert juicio.umbral.criterio_aplicado == FEN
    assert "adoptar el mas conservador" in juicio.umbral.aplicacion
    assert juicio.umbral.valor == pytest.approx(sin_fen.P_TR_mm,
                                                rel=REDONDEO_DEL_UMBRAL)
    assert sorted(m.valor for m in juicio.sustitucion) == pytest.approx(
        sorted((completo.P_TR_mm, sin_fen.P_TR_mm)), rel=REL)
    assert juicio.veredicto.margen == pytest.approx(
        completo.P_TR_mm - sin_fen.P_TR_mm, rel=REL)
    # La regla esta en la hoja de ruta, y la nota de T-1 ya no la rebaja.
    hoja = (RAIZ / "docs" / "hoja_de_ruta_alcantarillas_v8.md").read_text(
        encoding="utf-8")
    assert "adoptar el más conservador" in hoja
    assert "no se impone" not in hoja
    assert "el cálculo hidrológico del punto se detiene" in hoja


def test_serie_sin_fen_pasa_cuando_da_igual_o_mas_que_la_completa(
        MH, serie, monkeypatch):
    """
    La otra mitad de la decision: el criterio sigue siendo declarable. Con
    tres años corrientes marcados FEN, quitarlos sube la lluvia de diseño:
    `serie_sin_fen` es la mas conservadora y el calculo se entrega, con el
    contraste impreso. Y la serie completa, que ahi da MENOS, no se detiene
    --es la que el Manual manda usar--: indicador con aviso.
    """
    from src.modelos import TipoDeVeredicto
    otra = _con_fen_en(serie, ANIOS_CORRIENTES)
    with _declarados({FEN: "serie_sin_fen"}):
        sin_fen, _, _, pasos, avisos = MH.precipitacion_de_diseno(otra, 71)
    with _declarados({FEN: "serie_completa"}):
        completo, _, _, pasos_c, avisos_c = MH.precipitacion_de_diseno(otra, 71)
    assert sin_fen.P_TR_mm > completo.P_TR_mm
    assert pasos[3].veredicto.tipo is TipoDeVeredicto.CUMPLE
    assert pasos[3].veredicto.margen == pytest.approx(
        sin_fen.P_TR_mm - completo.P_TR_mm, rel=REL)
    assert sorted(m.valor for m in pasos[3].sustitucion) == pytest.approx(
        sorted((completo.P_TR_mm, sin_fen.P_TR_mm)), rel=REL)
    assert pasos_c[3].veredicto.tipo is TipoDeVeredicto.INDICADOR
    assert sum("SUBE" in a for a in avisos_c) == 1
    assert not any("SUBE" in a for a in avisos)
    # Igual tambien pasa: la desigualdad que detiene es estricta. Se fuerza
    # el empate haciendo que las dos series entreguen el mismo ajuste.
    fijo = MH._elegir(tuple(r.p24_mm for r in serie.registros),
                      MH.MEJOR_AJUSTE_KS, TR=71, alfa=0.05)
    monkeypatch.setattr(MH, "_elegir", lambda *a, **k: fijo)
    with _declarados({FEN: "serie_sin_fen"}):
        _, _, _, pasos_i, _ = MH.precipitacion_de_diseno(serie, 71)
    assert pasos_i[3].veredicto.tipo is TipoDeVeredicto.CUMPLE
    assert pasos_i[3].veredicto.margen == pytest.approx(0, abs=ABS_T08)


def test_la_lluvia_de_diseno_por_debajo_de_lo_observado_se_avisa(MH, serie):
    """
    Auditoria de T-1 (H1), con su caso: serie completa de 40 años, TR 71. La
    log normal pasa Kolmogorov-Smirnov y da 99.8 mm, con 173.5 mm (1998)
    registrados. El paso 1b.2 lo contrasta con la probabilidad observada de
    la ecuacion (13) --el maximo tiene un periodo de retorno empirico de
    (40 + 1)/1 = 41 años, que no supera 71-- y lo dice: INDICADOR, y el
    aviso llega a la corrida con la advertencia del Manual sobre Piura.
    """
    from src.modelos import TipoDeVeredicto
    from src.normativa import registro
    maximo = max(serie.registros, key=lambda r: r.p24_mm)
    with _declarados({FEN: "serie_completa"}):
        adoptado, _, _, pasos, avisos = MH.precipitacion_de_diseno(serie, 71)
    assert adoptado.acepta and adoptado.P_TR_mm < maximo.p24_mm
    ajuste = pasos[1]
    assert ajuste.codigo == "1b.2"
    assert ajuste.veredicto.tipo is TipoDeVeredicto.INDICADOR
    assert ajuste.umbral.valor == pytest.approx(maximo.p24_mm, rel=REL)
    assert ajuste.umbral.cita_id == "MC_HHD.3.7.2b"
    assert str(maximo.anio) in ajuste.umbral.descripcion
    assert ajuste.veredicto.margen == pytest.approx(
        adoptado.P_TR_mm - maximo.p24_mm, rel=REL)
    del_ajuste = [a for a in avisos if "POR DEBAJO" in a]
    assert len(del_ajuste) == 1
    piura = registro.construir().cita("MC_HHD.3.12.5#PIURA")
    assert piura.texto_literal.texto in del_ajuste[0]
    assert "Piura y Tumbes" in piura.texto_literal.texto
    assert "MC_HHD.3.12.5#PIURA" in pasos[0].citas_textuales
    # Con TR = 35 el maximo (T empirico 41) ya no toca: se contrasta con el
    # SEGUNDO, cuyo periodo de retorno empirico es 41/2 = 20.5 años.
    segundo = sorted(serie.registros, key=lambda r: r.p24_mm)[-2]
    registro_35, m, T = MH._cubre_lo_observado(serie.registros, 35)
    assert (registro_35.anio, m) == (segundo.anio, 2)
    assert T == pytest.approx(41 / 2, rel=REL)
    # Y un periodo de retorno que ningun dato alcanza no tiene contraste.
    assert MH._cubre_lo_observado(serie.registros[:5], 1.1) is None
    # Cuando la lluvia de diseño SI cubre lo observado, el paso cumple: la
    # misma serie sin sus tres extremos.
    from dataclasses import replace
    neutra = replace(serie, registros=tuple(r for r in serie.registros if not r.fen))
    with _declarados({FEN: "serie_completa"}):
        _, _, _, pasos_sf, avisos_sf = MH.precipitacion_de_diseno(neutra, 71)
    assert pasos_sf[1].veredicto.tipo is TipoDeVeredicto.CUMPLE
    assert not any("POR DEBAJO" in a for a in avisos_sf)


def test_la_justificacion_del_criterio_dice_lo_que_ocurre_con_los_extremos():
    """H1: decia lo contrario de lo que pasa (que K-S rechazaria el ajuste)."""
    from src import criterios_adoptados as ca
    texto = ca.CRITERIOS["distribucion_precipitacion_maxima"].justificacion
    assert "no garantiza" in texto and "por debajo" in texto
    fen = ca.CRITERIOS[FEN].justificacion
    assert "adoptar el mas conservador" in fen and "se detiene" in fen


@pytest.mark.parametrize("TR", [1, 0.5, 0, -10, float("nan")])
def test_un_periodo_de_retorno_que_no_pasa_de_un_anio_es_dato_invalido(MH, serie, TR):
    """H10: antes salia un `ZeroDivisionError` o un `ValueError` desnudos."""
    from src.modelos import DatoInvalidoError
    with _declarados({FEN: "serie_completa"}):
        with pytest.raises(DatoInvalidoError) as exc:
            MH.precipitacion_de_diseno(serie, TR)
    assert exc.value.campo == "TR"


def test_una_serie_de_menos_de_cinco_anios_no_se_evalua(MH, serie):
    """H10: la Tabla N 03 empieza en n = 5; por debajo no hay ajuste."""
    from dataclasses import replace
    from src.constantes_normativas import KS_N_MINIMO_TABULADO
    from src.modelos import MetodoNoEvaluableError
    with _declarados({FEN: "serie_completa"}):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            MH.precipitacion_de_diseno(
                replace(serie, registros=serie.registros[:KS_N_MINIMO_TABULADO - 1]), 71)
        assert "Tabla N 03" in str(exc.value)
        adoptado, *_ = MH.precipitacion_de_diseno(
            replace(serie, registros=serie.registros[:KS_N_MINIMO_TABULADO]), 71)
    assert adoptado.n == KS_N_MINIMO_TABULADO


def test_un_anio_de_cero_se_admite_y_excluye_a_la_log_normal(MH, tmp_path):
    """H10: 0 mm es un dato de una costa arida; la log normal sale diciendolo."""
    from src.modelos import MetodoNoEvaluableError
    filas = ["estacion,anio,p24_mm,fen"] + [
        f"X,{2000 + i},{v},{'si' if v > 60 else 'no'}"
        for i, v in enumerate((0, 4.5, 12, 8, 21, 70, 15, 3, 9, 30))]
    ruta = tmp_path / "arida.csv"
    ruta.write_text("\n".join(filas) + "\n", encoding="utf-8")
    arida = MH.cargar_estacion(ruta)["X"]
    assert min(r.p24_mm for r in arida.registros) == pytest.approx(0, abs=ABS_T08)
    with _declarados({FEN: "serie_completa"}):
        adoptado, evaluados, _, pasos, avisos = MH.precipitacion_de_diseno(arida, 25)
        assert [a.distribucion for a in evaluados] == ["normal", "gumbel"]
        assert any("lognormal_2p" in a and "0 mm" in a for a in avisos)
        assert any("lognormal_2p" in e and "no evaluable" in e
                   for e in pasos[1].elecciones[0].entre)
        with _declarados({"distribucion_precipitacion_maxima": "lognormal_2p"}):
            with pytest.raises(MetodoNoEvaluableError):
                MH.precipitacion_de_diseno(arida, 25)


def test_el_contraste_sin_fen_no_detiene_el_calculo_adoptado(MH, serie):
    """
    H10: una estacion con TODOS sus años FEN no tiene serie sin ellos. El
    contraste queda sin numero, dicho, y el ajuste adoptado se entrega.
    """
    from dataclasses import replace
    from src.modelos import RegistroDeLluvia, TipoDeVeredicto
    todos_fen = replace(serie, registros=tuple(
        RegistroDeLluvia(r.anio, r.p24_mm, True) for r in serie.registros))
    with _declarados({FEN: "serie_completa"}):
        adoptado, _, _, pasos, _ = MH.precipitacion_de_diseno(todos_fen, 71)
    assert adoptado.n == 40
    entre = " | ".join(pasos[0].elecciones[0].entre)
    assert "serie_sin_fen: sin numero" in entre
    assert pasos[3].veredicto.tipo is TipoDeVeredicto.SIN_VEREDICTO
    assert pasos[3].umbral is None


def test_los_anios_que_faltan_en_la_serie_se_imprimen_y_se_avisan(MH, serie):
    """H10: el programa ajusta los años que hay y no rellena los que faltan."""
    from dataclasses import replace
    con_huecos = replace(serie, registros=tuple(
        r for r in serie.registros if r.anio not in (1991, 2004)))
    with _declarados({FEN: "serie_completa"}):
        *_, pasos, avisos = MH.precipitacion_de_diseno(con_huecos, 71)
    por_simbolo = {m.simbolo: m.valor for m in pasos[0].sustitucion}
    assert por_simbolo["años sin dato"] == "1991, 2004"
    assert any("no es continua" in a and "1991, 2004" in a for a in avisos)


def test_la_precipitacion_de_diseno_contra_un_segundo_calculo(MH, serie):
    """Log normal de 2 parametros sobre la serie completa, por otro camino."""
    logs = [math.log(r.p24_mm) for r in serie.registros]
    esperado = math.exp(fmean(logs) + NormalDist().inv_cdf(1 - 1 / 71) * stdev(logs))
    with _declarados({FEN: "serie_completa",
                      "distribucion_precipitacion_maxima": "lognormal_2p"}):
        ajuste, *_ = MH.precipitacion_de_diseno(serie, 71)
    assert ajuste.P_TR_mm == pytest.approx(esperado, rel=REL)


def test_mejor_ajuste_ks_elige_la_de_menor_D_entre_las_evaluadas(MH, serie):
    with _declarados({FEN: "serie_completa"}):
        adoptado, evaluados, _, pasos, _ = MH.precipitacion_de_diseno(serie, 71)
    assert [a.distribucion for a in evaluados] == ["normal", "lognormal_2p", "gumbel"]
    assert adoptado.D == min(a.D for a in evaluados) and adoptado.acepta
    # El paso del ajuste imprime la lluvia de las tres, para que se vea
    # cuanto pesa la eleccion.
    entre = pasos[1].elecciones[0].entre
    assert len(entre) == 3 and all("D = " in e for e in entre)
    assert pasos[2].codigo == "1b.3" and pasos[2].umbral.cita_id == "MC_HHD.3.7.2b#T03"
    assert pasos[2].veredicto.tipo.value == "cumple"


def test_una_distribucion_declarada_que_no_pasa_ks_detiene_el_calculo(MH, serie):
    """Gumbel sobre la serie con los tres extremos: D = 0.259 > d = 0.21."""
    from src.modelos import MetodoNoEvaluableError
    with _declarados({FEN: "serie_completa",
                      "distribucion_precipitacion_maxima": "gumbel"}):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            MH.precipitacion_de_diseno(serie, 71)
    assert "Kolmogorov-Smirnov" in str(exc.value) and "gumbel" in str(exc.value)
    # Sin los tres extremos la misma distribucion si pasa la prueba...
    from dataclasses import replace
    neutra = replace(serie, registros=tuple(r for r in serie.registros if not r.fen))
    with _declarados({FEN: "serie_completa",
                      "distribucion_precipitacion_maxima": "gumbel"}):
        ajuste, *_ = MH.precipitacion_de_diseno(neutra, 71)
    assert ajuste.acepta
    # ...pero declarar `serie_sin_fen` para conseguirlo no es una salida: da
    # menos lluvia que la serie completa y el calculo se detiene (T1-09). El
    # mensaje dice ademas que el ajuste de la completa NO pasa la prueba, de
    # modo que el unico remedio que queda es el caudal del estudio.
    with _declarados({FEN: "serie_sin_fen",
                      "distribucion_precipitacion_maxima": "gumbel"}):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            MH.precipitacion_de_diseno(serie, 71)
    assert "mas conservador" in str(exc.value) and "NO pasa" in str(exc.value)


def test_dos_poblaciones_se_declara_y_no_se_evalua(MH, serie):
    from src.modelos import MetodoNoEvaluableError
    with _declarados({FEN: "dos_poblaciones"}):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            MH.precipitacion_de_diseno(serie, 71)
    assert "poblacion mixta" in str(exc.value)


def test_una_serie_sin_anios_fen_lo_avisa_como_limitacion(MH, serie):
    from dataclasses import replace
    neutra = replace(serie, registros=tuple(r for r in serie.registros if not r.fen))
    with _declarados({FEN: "serie_completa"}):
        *_, pasos, avisos = MH.precipitacion_de_diseno(neutra, 71)
    assert sum("no declara ningun año FEN" in a for a in avisos) == 1
    assert "subestimado" in pasos[0].nota_del_proyecto
    # Sin años FEN no hay segundo ajuste: el juicio queda sin veredicto.
    assert pasos[3].codigo == "1b.3b" and pasos[3].umbral is None


def test_una_serie_corta_dispara_el_indicador_de_25_anios(MH, serie):
    """«se recomienda contar con un mínimo de 25 años»: aviso, no bloqueo."""
    from dataclasses import replace
    corta = replace(serie, registros=serie.registros[:20])
    with _declarados({FEN: "serie_completa"}):
        *_, pasos, avisos = MH.precipitacion_de_diseno(corta, 71)
    assert pasos[0].veredicto.tipo.value == "indicador"
    assert pasos[0].umbral.valor == 25 and pasos[0].umbral.caracter == "recomendacion"
    # H10: el aviso SUBE a la corrida (CLI y JSON), no se queda en el paso.
    assert sum("menos de los 25" in a for a in avisos) == 1
    with _declarados({FEN: "serie_completa"}):
        *_, pasos, avisos = MH.precipitacion_de_diseno(serie, 71)
    assert pasos[0].veredicto.tipo.value == "cumple"
    assert not any("menos de los 25" in a for a in avisos)


def test_la_serie_tiene_que_declarar_sus_anios_fen(MH, tmp_path):
    from src.modelos import DatoFaltanteError, DatoInvalidoError
    sin_columna = tmp_path / "e1.csv"
    sin_columna.write_text("estacion,anio,p24_mm\nX,2001,20\n", encoding="utf-8")
    with pytest.raises(DatoFaltanteError) as exc:
        MH.cargar_estacion(sin_columna)
    assert exc.value.campo == "fen"
    mala = tmp_path / "e2.csv"
    mala.write_text("estacion,anio,p24_mm,fen\nX,2001,20,quizas\n", encoding="utf-8")
    with pytest.raises(DatoInvalidoError):
        MH.cargar_estacion(mala)
    repetida = tmp_path / "e3.csv"
    repetida.write_text("estacion,anio,p24_mm,fen\nX,2001,20,no\nX,2001,25,no\n",
                        encoding="utf-8")
    with pytest.raises(DatoInvalidoError):
        MH.cargar_estacion(repetida)
    negativa = tmp_path / "e4.csv"
    negativa.write_text("estacion,anio,p24_mm,fen\nX,2001,-3,no\n", encoding="utf-8")
    with pytest.raises(DatoInvalidoError):
        MH.cargar_estacion(negativa)
    # Auditoria de T-1 (H2): una celda `fen` VACIA no es un «no». Leerla asi
    # era rellenar el hecho que el archivo tiene que declarar.
    vacia = tmp_path / "e5.csv"
    vacia.write_text("estacion,anio,p24_mm,fen\nX,2001,20,no\nX,2002,95,\n",
                     encoding="utf-8")
    with pytest.raises(DatoFaltanteError) as exc:
        MH.cargar_estacion(vacia)
    assert exc.value.campo == "fen" and "linea 3" in str(exc.value)
    assert "" not in MH.FEN_NO and "" not in MH.FEN_SI


# ===========================================================================
# 7. El caudal de diseño de punta a punta (MH)
# ===========================================================================

def test_el_caudal_calculado_es_el_producto_de_sus_pasos(MH, cuencas, serie):
    """Q = 0.278·C·I·A recompuesto con lo que cada paso publica."""
    with _declarados({FEN: "serie_completa"}):
        c = MH.caudal_de_diseno(cuencas["A-02"], serie, 71)
    assert c.calculado and c.origen == "calculado"
    assert [p.codigo for p in c.pasos] == PASOS_DE_LA_FASE_1B
    assert c.metodo_tc == "kirpich" and c.K_uniformidad is None
    assert c.duracion_min == pytest.approx(c.tc_min, rel=REL)
    por = {p.codigo: p for p in c.pasos}
    P24, tc = por["1b.2"].resultado.valor, por["1b.4"].resultado.valor
    I = P24 * (tc / 1440) ** 0.25 / (tc / 60)
    assert por["1b.5"].resultado.valor == pytest.approx(I, rel=REL)
    assert c.Q_m3s == pytest.approx(0.278 * por["1b.6"].resultado.valor * I * 2.1,
                                    rel=REL)
    assert por["1b.8"].resultado.valor == pytest.approx(c.Q_m3s / 2.1, rel=REL)
    # Cada paso lleva fundamento, cita y procedencia de lo que sustituye.
    for p in c.pasos:
        assert p.fundamento_id.startswith("FH.") and p.por_que and p.citas_textuales
        assert all(m.procedencia for m in p.sustitucion)
    # Dos pasos no citan su formula porque no es de una fuente: el recuento
    # de años (1b.1) y la regla de la hoja de ruta (1b.3b).
    assert all(p.formula_cita_id for p in c.pasos
               if p.codigo not in ("1b.1", "1b.3b"))


def test_el_caudal_crece_con_el_periodo_de_retorno(MH, cuencas, serie):
    """El enlace que V8 necesitara: la misma llamada con otro TR."""
    with _declarados({FEN: "serie_completa"}):
        q35 = MH.caudal_de_diseno(cuencas["A-02"], serie, 35).Q_m3s
        q71 = MH.caudal_de_diseno(cuencas["A-02"], serie, 71).Q_m3s
        q500 = MH.caudal_de_diseno(cuencas["A-02"], serie, 500).Q_m3s
    assert q35 < q71 < q500


def test_una_cuenca_de_10_km2_se_detiene_antes_de_ajustar_nada(MH, cuencas, serie):
    """Y no exige el criterio FEN para decirlo: el metodo no aplica."""
    from dataclasses import replace
    from src.modelos import MetodoNoEvaluableError
    with pytest.raises(MetodoNoEvaluableError):
        MH.caudal_de_diseno(replace(cuencas["A-01"], area_km2=12.0), serie, 71)


def test_la_relacion_intensidad_duracion_es_barrible(MH, cuencas, serie):
    """Temez da 146 min en A-01: la Tabla N 04 aplica y da menos caudal."""
    with _declarados({FEN: "serie_completa"}):
        dp = MH.caudal_de_diseno(cuencas["A-01"], serie, 71)
    with _declarados({FEN: "serie_completa", "relacion_intensidad_duracion":
                      "tabla_04_coeficientes_de_duracion"}):
        t04 = MH.caudal_de_diseno(cuencas["A-01"], serie, 71)
    assert t04.Q_m3s < dp.Q_m3s
    paso = next(p for p in t04.pasos if p.codigo == "1b.5")
    assert paso.formula_cita_id == "MC_HHD.3.8.1#T04"
    assert "LINEALMENTE" in paso.nota_del_proyecto


def test_el_tc_por_debajo_de_la_duracion_minima_adopta_el_minimo(MH, cuencas, serie):
    """
    Auditoria de T-1 (H3): una cuneta corta da tiempos de concentracion de 1
    o 2 minutos y la intensidad, extrapolada hasta ahi, pasa de 1000 mm/h. El
    Manual de Hidrologia no fija piso; lo cubre WSDOT [C] con 5 minutos. Si
    tc queda por debajo, la lluvia de diseño dura el minimo y se dice.
    """
    from dataclasses import replace
    from src import criterios_adoptados as ca
    from src.modelos import TipoDeVeredicto
    criterio = ca.CRITERIOS["duracion_minima_lluvia_min"]
    assert criterio.etiqueta == "C" and "WSDOT_HM.2-6.3#TC_MINIMO" in criterio.fuente
    minimo = criterio.valor
    cuneta = replace(cuencas["B-01"], L_cauce_m=4.0, S_cauce_cuenca=0.05,
                     area_km2=0.002, cobertura="pavimento")
    with _declarados({FEN: "serie_completa"}):
        corta = MH.caudal_de_aporte_cuneta(cuneta, serie, 35)
        larga = MH.caudal_de_aporte_cuneta(cuencas["B-01"], serie, 35)
    assert corta.tc_min < minimo
    assert corta.duracion_min == pytest.approx(minimo, rel=REL)
    paso = next(p for p in corta.pasos if p.codigo == "1b.5")
    assert paso.veredicto.tipo is TipoDeVeredicto.INDICADOR
    assert paso.umbral.cita_id == "WSDOT_HM.2-6.3#TC_MINIMO"
    assert paso.umbral.criterio_aplicado == "duracion_minima_lluvia_min"
    # La intensidad es la de la duracion minima, no la del tc.
    Pd = corta.P24_TR_mm * (minimo / 1440) ** 0.25
    assert corta.I_mm_h == pytest.approx(Pd / (minimo / 60), rel=REL)
    con_tc = corta.P24_TR_mm * (corta.tc_min / 1440) ** 0.25 / (corta.tc_min / 60)
    assert corta.I_mm_h < con_tc
    assert sum("duracion minima" in a for a in corta.avisos) == 1
    # Por encima del minimo no cambia nada, y el paso cumple.
    assert larga.duracion_min == pytest.approx(larga.tc_min, rel=REL)
    paso_l = next(p for p in larga.pasos if p.codigo == "1b.5")
    assert paso_l.veredicto.tipo is TipoDeVeredicto.CUMPLE
    assert not any("duracion minima" in a for a in larga.avisos)


def test_una_cuenca_plana_y_una_cuneta_tienen_un_tc_evaluable_y_citado(
        MH, cuencas, serie):
    """
    Auditoria de T-1 (H6 ii): con solo Kirpich, California y Temez, una
    cuenca de llanura al 0.2 % no tenia ningun metodo evaluable. La Tabla
    N 05 se transcribio entera y dos de sus filas de flujo superficial y de
    cuenca agricola estan implementadas.
    """
    from dataclasses import replace
    from src.modelos import MetodoNoEvaluableError
    plana = replace(cuencas["A-02"], S_cauce_cuenca=0.002, S_terreno=0.004)
    with _declarados({FEN: "serie_completa"}):
        with pytest.raises(MetodoNoEvaluableError):
            MH.caudal_de_diseno(plana, serie, 35)                      # Kirpich
        faa = MH.caudal_de_diseno(
            replace(plana, metodo_tc="federal_aviation_administration",
                    ajuste_kirpich=None), serie, 35)
        scs = MH.caudal_de_diseno(
            replace(plana, metodo_tc="retardo_scs", ajuste_kirpich=None, CN=78.0),
            serie, 35)
    for caudal, cita in ((faa, "MC_HHD.3.9#T05_FAA"), (scs, "MC_HHD.3.9#T05_SCS")):
        paso = next(p for p in caudal.pasos if p.codigo == "1b.4")
        assert paso.formula_cita_id == cita and caudal.tc_min > 0
        assert caudal.Q_m3s > 0
    # La tabla esta ENTERA en el registro: seis filas, y las dos que no se
    # implementan dicen por que.
    from src.normativa import registro
    from src.normativa.esquema import NoUsada
    filas = registro.construir().tabla("MC_HHD.T05").filas
    assert len(filas) == 6
    sin_uso = [f for f in filas if isinstance(f.uso, NoUsada)]
    assert len(sin_uso) == 2 and all("T1-07" in f.uso.por_que_no for f in sin_uso)
    assert set(MH.METODOS_TC) == {"kirpich", "california_culverts_practice",
                                  "federal_aviation_administration",
                                  "retardo_scs", "temez"}


def test_el_coeficiente_de_uniformidad_entra_solo_con_temez_y_por_criterio(
        MH, cuencas, serie):
    """
    Auditoria de T-1 (H7): la formula de Temez es del metodo racional
    modificado, cuyo caudal lleva K. El uso hibrido se declara y K lo decide
    un criterio [A]: «aplicar» (valor de archivo) o «no_aplicar».
    """
    from src import criterios_adoptados as ca
    criterio = ca.CRITERIOS["coeficiente_uniformidad_temez"]
    assert (criterio.valor, criterio.etiqueta) == ("aplicar", "A")
    assert criterio.sensibilidad == ("aplicar", "no_aplicar")
    with _declarados({FEN: "serie_completa"}):
        con = MH.caudal_de_diseno(cuencas["A-01"], serie, 71)
        with _declarados({"coeficiente_uniformidad_temez": "no_aplicar"}):
            sin = MH.caudal_de_diseno(cuencas["A-01"], serie, 71)
        kirpich = MH.caudal_de_diseno(cuencas["A-02"], serie, 71)
    K = 1 + (con.tc_min / 60) ** 1.25 / ((con.tc_min / 60) ** 1.25 + 14)
    assert con.K_uniformidad == pytest.approx(K, rel=REL) and K > 1
    assert sin.K_uniformidad is None and kirpich.K_uniformidad is None
    assert con.Q_m3s == pytest.approx(K * sin.Q_m3s, rel=REL)
    assert con.Q_m3s == pytest.approx(
        0.278 * con.C * con.I_mm_h * con.area_km2 * K, rel=REL)
    paso, paso_sin = (next(p for p in c.pasos if p.codigo == "1b.7")
                      for c in (con, sin))
    assert paso.formula_cita_id == "MC_HHD.3.12.2.1#K" and "· K" in paso.formula
    assert paso_sin.formula_cita_id == "MC_HHD.3.12.2"
    for p in (paso, paso_sin):
        assert "USO HIBRIDO" in p.nota_del_proyecto
        assert p.elecciones[0].clave_criterio == "coeficiente_uniformidad_temez"
        assert f"{con.Q_m3s:.3f}" in " ".join(p.elecciones[0].entre)
        assert f"{sin.Q_m3s:.3f}" in " ".join(p.elecciones[0].entre)
    assert "SUBE" in paso.nota_del_proyecto
    assert "no conservador" in paso_sin.nota_del_proyecto
    # El paso de Kirpich no nombra a K ni lee el criterio.
    paso_k = next(p for p in kirpich.pasos if p.codigo == "1b.7")
    assert paso_k.elecciones == () and "HIBRIDO" not in paso_k.nota_del_proyecto


def test_el_caudal_de_aporte_de_la_cuneta_devuelve_su_memoria(MH, cuencas, serie):
    """
    Auditoria de T-1 (H12), el enlace para T-9: la funcion devolvia un
    numero desnudo, con un segundo coeficiente (1/3.6) y sin pasar por el
    criterio FEN. Hoy devuelve el mismo `CaudalDeDiseno` que el caudal de
    diseño --tc, I, C, Q y sus pasos--, con el 0.278 de toda la familia.
    """
    from src.modelos import CaudalDeDiseno, CriterioPendienteError
    with pytest.raises(CriterioPendienteError) as exc:
        MH.caudal_de_aporte_cuneta(cuencas["B-01"], serie, 35)
    assert exc.value.clave == FEN
    with _declarados({FEN: "serie_completa"}):
        aporte = MH.caudal_de_aporte_cuneta(cuencas["B-01"], serie, 35)
        diseno = MH.caudal_de_diseno(cuencas["B-01"], serie, 35)
    assert isinstance(aporte, CaudalDeDiseno)
    assert [p.codigo for p in aporte.pasos] == PASOS_DE_LA_FASE_1B
    assert None not in (aporte.tc_min, aporte.I_mm_h, aporte.C, aporte.Q_m3s)
    assert aporte.Q_m3s == pytest.approx(diseno.Q_m3s, rel=REL)
    assert aporte.Q_m3s == pytest.approx(
        0.278 * aporte.C * aporte.I_mm_h * aporte.area_km2, rel=REL)
    paso = next(p for p in aporte.pasos if p.codigo == "1b.7")
    assert "MC_HHD.4.1.2.1b" in paso.citas_textuales
    assert "3.6" in paso.nota_del_proyecto and "cuneta" in paso.que
    # El coeficiente es el de la superficie vial, nunca una fila de la Tabla
    # N 08 puesta por omision.
    assert aporte.C == pytest.approx(0.72, rel=REL_TRANSPORTE)
    paso_c = next(p for p in aporte.pasos if p.codigo == "1b.6")
    assert "WSDOT_HM.2-6.2#T2-2" in paso_c.citas_textuales


def test_el_csv_de_cuencas_valida_claves_y_dominio(MH, tmp_path):
    from src.modelos import DatoFaltanteError, DatoInvalidoError
    base = dict(CUENCA_CHICA)
    assert MH.cargar_cuencas(_cuencas_con(tmp_path, [base]))["A-02"].area_km2 \
        == pytest.approx(float(base["area_km2"]), rel=REL_TRANSPORTE)
    for campo, valor, error in [
            ("cobertura", "pavimento", DatoInvalidoError),    # con suelo lleno
            ("cobertura", "asfalto", DatoInvalidoError),
            ("metodo_tc", "kirpitch", DatoInvalidoError),
            ("S_cauce_cuenca", "4", DatoInvalidoError),       # en porcentaje
            ("area_km2", "0", DatoInvalidoError),
            ("area_km2", "", DatoFaltanteError),
            ("ajuste_kirpich", "asfalto", DatoInvalidoError),
            # Auditoria de T-1 (H4): dos celdas que eran opcionales.
            ("ajuste_kirpich", "", DatoFaltanteError),
            ("S_terreno", "", DatoFaltanteError),
            ("S_terreno", "3", DatoInvalidoError),            # en porcentaje
            ("CN", "120", DatoInvalidoError)]:
        with pytest.raises(error) as exc:
            MH.cargar_cuencas(_cuencas_con(tmp_path, [{**base, campo: valor}]))
        if valor == "":
            assert exc.value.campo == campo
    # Un ajuste de Kirpich con OTRO metodo no se ignora: contradice.
    with pytest.raises(DatoInvalidoError) as exc:
        MH.cargar_cuencas(_cuencas_con(tmp_path, [
            {**base, "metodo_tc": "federal_aviation_administration",
             "ajuste_kirpich": "superficie_de_concreto_o_asfalto"}]))
    assert "contradice" in str(exc.value)
    # Una superficie vial entra con el suelo vacio, y se guarda sin suelo.
    vial = MH.cargar_cuencas(_cuencas_con(tmp_path, [
        {**base, "cobertura": "pavimento", "suelo": "",
         "metodo_tc": "federal_aviation_administration", "ajuste_kirpich": ""}]))
    assert (vial["A-02"].cobertura, vial["A-02"].suelo) == ("pavimento", "")
    # `S_terreno` es columna obligatoria del encabezado.
    assert "S_terreno" in MH.COLUMNAS_CUENCAS
    assert set(MH.COLUMNAS_CUENCAS_OPCIONALES) == {"H_desnivel_m",
                                                  "ajuste_kirpich", "CN"}
    with pytest.raises(DatoInvalidoError):        # dos filas para una obra
        MH.cargar_cuencas(_cuencas_con(tmp_path, [base, base]))
    sin_columna = tmp_path / "c.csv"
    sin_columna.write_text("id,area_km2\nA-02,1\n", encoding="utf-8")
    with pytest.raises(DatoFaltanteError):
        MH.cargar_cuencas(sin_columna)


# ===========================================================================
# 8. El servicio: de donde sale el caudal de cada punto
# ===========================================================================

def test_Q_lleno_gana_y_la_memoria_dice_que_es_declarado(externos, hidrologia):
    """T-1, punto 2: con cuencas y estacion, la columna llena sigue mandando."""
    from src import modelos, servicio
    sin = servicio.correr(PUNTOS, externos, "perfil")
    con = servicio.correr(PUNTOS, externos, "perfil", hidrologia)
    for id_punto, Q in (("A-01", 1.167), ("A-02", 0.480), ("B-01", 0.095)):
        a, b = _por_id(sin, id_punto), _por_id(con, id_punto)
        for informe in (a, b):
            assert informe.caudal.origen == modelos.ORIGEN_CAUDAL_DECLARADO
            assert informe.caudal.leyenda == "Q declarado por el estudio hidrológico"
            assert informe.caudal.Q_m3s == Q
            assert informe.punto_de_calculo.Q_m3s == Q
            assert [p.codigo for p in informe.caudal.pasos] == ["1b.8"]
        assert any("NO se usaron" in x for x in b.caudal.avisos)
        assert not any("NO se usaron" in x for x in a.caudal.avisos)
        # Y nada del diseño se mueve por traer la hidrologia.
        assert a.dimensionado == b.dimensionado
        if a.dimensionado:
            assert a.resultado.seccion.etiqueta() == b.resultado.seccion.etiqueta()
            assert a.resultado.resultado_hidraulico.HW == b.resultado.resultado_hidraulico.HW
    assert _por_id(con, "C-01").caudal is None        # la Familia C no pasa
    # La memoria publica esos mismos pasos, por la travesia de M11.
    from src.modulos import M11_reporte as M11
    assert M11.traza_hidrologia(_por_id(con, "A-01")) == _por_id(con, "A-01").caudal.pasos
    assert M11.traza_hidrologia(_por_id(con, "C-01")) == ()
    assert all(p in M11.pasos_impresos(con) for p in _por_id(con, "A-01").caudal.pasos)


def test_un_Q_declarado_en_datos_externos_gana_tambien_a_la_cuenca(tmp_path):
    """La precedencia de siempre: el dato externo pisa a la columna y al calculo."""
    from src import modelos, servicio
    ruta = _csv_con(tmp_path, A02_SIN_Q)
    h = servicio.cargar_hidrologia(_cuencas_con(tmp_path, [CUENCA_CHICA]), ESTACION)
    datos = tmp_path / "externos.json"
    datos.write_text(json.dumps({"globales": {"luz_m": 2.0, "TW_m": 0.0},
                                 "puntos": {"A-02": {"Q_m3s": 0.33}}}),
                     encoding="utf-8")
    ext = servicio.cargar_datos_externos(datos, {})
    punto = _por_id(servicio.correr(ruta, ext, "perfil", h), "A-02")
    assert punto.caudal.origen == modelos.ORIGEN_CAUDAL_DECLARADO
    assert punto.caudal.Q_m3s == ext.valor("A-02", "Q_m3s")
    assert "datos externos" in punto.caudal.de_donde
    assert punto.dimensionado
    assert punto.resultado.resultado_hidraulico.Q == pytest.approx(
        ext.valor("A-02", "Q_m3s"), rel=REL_TRANSPORTE)
    # No se invoco el criterio FEN: el calculo hidrologico no corrio.
    assert not any(b.criterio == FEN for b in punto.bloqueos)
    # Y con la columna LLENA el dato externo tambien manda, que es lo que
    # `disenar_punto` ya hacia: el caudal que la memoria declara es el mismo
    # con que se dimensiono.
    datos.write_text(json.dumps({"globales": {"luz_m": 2.0, "TW_m": 0.0},
                                 "puntos": {"A-01": {"Q_m3s": 0.5}}}),
                     encoding="utf-8")
    ext = servicio.cargar_datos_externos(datos, {})
    a01 = _por_id(servicio.correr(PUNTOS, ext, "perfil"), "A-01")
    assert a01.caudal.Q_m3s == ext.valor("A-01", "Q_m3s")
    assert a01.caudal.Q_m3s != a01.punto.Q_m3s
    assert a01.resultado.resultado_hidraulico.Q == pytest.approx(
        a01.caudal.Q_m3s, rel=REL_TRANSPORTE)


def test_Q_declarado_avisa_del_tratamiento_fen_y_no_bloquea(externos, hidrologia, MH):
    """
    Punto 3, reescrito tras la auditoria de T-1 (H5). Con el caudal
    declarado el criterio FEN no bloquea; y NO se le atribuye: el test
    anterior fijaba que, declarado el criterio, el JSON dijera que el caudal
    del estudio externo llevaba ese tratamiento, que es inventarle una
    procedencia. Hoy `tratamiento_fen` es None siempre que el origen es
    declarado, y el aviso de que el criterio solo rige el caudal calculado
    es permanente.
    """
    import cli
    from src import servicio
    informe = _por_id(servicio.correr(PUNTOS, externos, "perfil"), "A-01")
    assert informe.dimensionado
    assert informe.caudal.tratamiento_fen is None
    assert MH.AVISO_FEN_DEL_CAUDAL_DECLARADO in informe.caudal.avisos
    assert FEN in MH.AVISO_FEN_DEL_CAUDAL_DECLARADO
    assert "No detiene" in MH.AVISO_FEN_DEL_CAUDAL_DECLARADO
    assert not any(b.criterio == FEN for b in informe.bloqueos)
    with _declarados({FEN: "serie_sin_fen"}):
        corrida = servicio.correr(PUNTOS, externos, "perfil", hidrologia)
        volcado = cli.informe_json(corrida)
    declarado = _por_id(corrida, "A-01")
    assert declarado.caudal.tratamiento_fen is None
    assert MH.AVISO_FEN_DEL_CAUDAL_DECLARADO in declarado.caudal.avisos
    # La corrida ni siquiera leyo el criterio: no hubo caudal que calcular.
    assert FEN not in corrida.contexto.criterios_usados
    for id_punto in ("A-01", "A-02", "B-01"):
        caudal = next(p for p in volcado["puntos"] if p["id"] == id_punto)["caudal"]
        assert caudal["origen"] == "declarado" and caudal["tratamiento_fen"] is None


def test_dos_areas_para_una_cuenca_detienen_el_calculo_y_nombran_el_par(
        tmp_path, externos):
    """
    Auditoria de T-1 (H8): la cuenca de A-02 tiene 210 ha en el CSV de puntos
    (que fija su periodo de retorno) y 0.12 km2 en el de cuencas (que entra
    al caudal). El programa no elige: la etapa se bloquea con el par.
    """
    from src import servicio
    h = servicio.cargar_hidrologia(_cuencas_con(tmp_path, [CUENCA_CHICA]), ESTACION)
    ruta = _csv_con(tmp_path, {"A-02": {"Q_m3s": ""}})          # area_ha = 210
    with _declarados({FEN: "serie_completa"}):
        punto = _por_id(servicio.correr(ruta, externos, "perfil", h), "A-02")
    reales = punto.bloqueos_reales()
    assert [b.tipo.value for b in reales] == ["DatoInvalidoError"]
    assert reales[0].etapa == servicio.ETAPA_AREA_DE_LA_CUENCA
    for trozo in ("contradice a otro dato", "area_ha", "area_km2", "210", "0.12"):
        assert trozo in reales[0].mensaje, trozo
    assert punto.caudal is None and not punto.dimensionado
    # Con el caudal DECLARADO la contradiccion se dice igual, el punto se
    # dimensiona (ese caudal no depende de ninguna de las dos areas) y el
    # contraste Q/A no se emite: no hay un area que usar.
    declarado = _por_id(servicio.correr(PUNTOS, externos, "perfil", h), "A-02")
    assert declarado.dimensionado and declarado.caudal.pasos == ()
    assert any(b.etapa == servicio.ETAPA_AREA_DE_LA_CUENCA for b in declarado.bloqueos)
    # Y con las dos areas de acuerdo no hay bloqueo.
    with _declarados({FEN: "serie_completa"}):
        bien = _por_id(servicio.correr(_csv_con(tmp_path, A02_SIN_Q), externos,
                                       "perfil", h), "A-02")
    assert not any(b.etapa == servicio.ETAPA_AREA_DE_LA_CUENCA for b in bien.bloqueos)


def test_Q_vacio_sin_cuencas_ni_estacion_es_dato_faltante_como_antes(tmp_path, externos):
    from src import servicio
    from src.modelos import DatoFaltanteError
    ruta = _csv_con(tmp_path, A02_SIN_Q)
    with pytest.raises(DatoFaltanteError) as exc:
        servicio.correr(ruta, externos, "perfil")
    assert exc.value.campo == "Q_m3s" and exc.value.id_punto == "A-02"
    assert "--cuencas" in str(exc.value)


def test_Q_vacio_en_un_punto_sin_cuenca_sigue_siendo_dato_faltante(tmp_path, externos):
    """La hidrologia admite el vacio SOLO en las obras que tienen cuenca."""
    from src import servicio
    from src.modelos import DatoFaltanteError
    ruta = _csv_con(tmp_path, {"A-01": {"Q_m3s": ""}})
    h = servicio.cargar_hidrologia(_cuencas_con(tmp_path, [CUENCA_CHICA]), ESTACION)
    with pytest.raises(DatoFaltanteError) as exc:
        servicio.correr(ruta, externos, "perfil", h)
    assert exc.value.campo == "Q_m3s" and exc.value.id_punto == "A-01"


def test_Q_vacio_con_cuenca_y_estacion_se_calcula_y_el_punto_se_dimensiona(
        tmp_path, externos):
    from src import modelos, servicio
    ruta = _csv_con(tmp_path, A02_SIN_Q)
    h = servicio.cargar_hidrologia(_cuencas_con(tmp_path, [CUENCA_CHICA]), ESTACION)
    with _declarados({FEN: "serie_completa"}):
        informe = servicio.correr(ruta, externos, "perfil", h)
    punto = _por_id(informe, "A-02")
    assert punto.punto.Q_m3s is None                  # la fila no se toca
    assert punto.caudal.origen == modelos.ORIGEN_CAUDAL_CALCULADO
    # 12 ha: quebrada menor, y su periodo de retorno es el de la Fase 2.
    assert punto.caudal.TR_anios == punto.clasificacion.periodo_retorno.anios == 35
    # Los avisos del calculo suben al informe del punto (H1, H10).
    assert any("POR DEBAJO" in a for a in punto.caudal.avisos)
    assert punto.punto_de_calculo.Q_m3s == punto.caudal.Q_m3s
    assert punto.dimensionado, [b.mensaje for b in punto.bloqueos_reales()]
    assert punto.resultado.resultado_hidraulico.Q == pytest.approx(
        punto.caudal.Q_m3s, rel=REL_TRANSPORTE)
    # A-01, que trae su Q, no cambia.
    assert _por_id(informe, "A-01").caudal.Q_m3s == _por_id(informe, "A-01").punto.Q_m3s


def test_sin_el_criterio_fen_el_punto_calculado_se_bloquea_con_su_clave(
        tmp_path, externos):
    from src import servicio
    ruta = _csv_con(tmp_path, A02_SIN_Q)
    h = servicio.cargar_hidrologia(_cuencas_con(tmp_path, [CUENCA_CHICA]), ESTACION)
    informe = servicio.correr(ruta, externos, "perfil", h)
    punto = _por_id(informe, "A-02")
    reales = punto.bloqueos_reales()
    assert [b.tipo.value for b in reales] == ["CriterioPendienteError"]
    assert reales[0].criterio == FEN and reales[0].fase == servicio.FASE_HIDROLOGIA
    assert punto.caudal is None and not punto.dimensionado
    # Un solo bloqueo: no se repite como «falta Q_m3s» en el diseño.
    assert not any(b.campo == "Q_m3s" for b in punto.bloqueos)
    assert _por_id(informe, "A-01").dimensionado        # el declarado sigue


def test_los_avisos_de_la_fase_1b_salen_con_los_del_punto_y_cuentan_en_el_resumen(
        tmp_path, externos):
    """
    La integracion con T-2: todo aviso llega a `InformePunto.avisos()` --la
    CLI, el JSON y la memoria leen de ahi-- y un paso de la Fase 1-bis con
    veredicto INDICADOR cuenta en el RESUMEN junto a las verificaciones con
    aviso. Se imprime UNA vez, no dos.
    """
    import cli
    from src import servicio
    ruta = _csv_con(tmp_path, A02_SIN_Q)
    h = servicio.cargar_hidrologia(_cuencas_con(tmp_path, [CUENCA_CHICA]), ESTACION)
    with _declarados({FEN: "serie_completa"}):
        informe = servicio.correr(ruta, externos, "perfil", h)
    punto = _por_id(informe, "A-02")
    assert punto.caudal.calculado and punto.caudal.avisos
    assert set(punto.caudal.avisos) <= set(punto.avisos())
    assert [p.codigo for p in punto.indicadores_de_hidrologia()] == ["1b.2"]
    assert informe.resumen().con_aviso == sum(
        len(i.con_aviso()) + len(i.indicadores_de_hidrologia())
        for i in informe.puntos)
    assert informe.resumen().con_aviso >= 1
    texto = cli.volcar(informe)
    assert texto.count("POR DEBAJO") == 1
    volcado = next(p for p in cli.informe_json(informe)["puntos"] if p["id"] == "A-02")
    assert sum("POR DEBAJO" in a for a in volcado["avisos"]) == 1
    # Un caudal declarado no dispara ningun indicador de hidrologia: lleva
    # su aviso permanente, que es un texto y no un contraste.
    declarado = _por_id(informe, "A-01")
    assert declarado.indicadores_de_hidrologia() == ()
    assert declarado.avisos()[0] == _mh().AVISO_FEN_DEL_CAUDAL_DECLARADO
    assert _por_id(informe, "C-01").indicadores_de_hidrologia() == ()


def test_serie_sin_fen_bloquea_el_punto_calculado_y_no_el_declarado(
        tmp_path, externos):
    """
    T1-09, por el servicio: el punto cuyo caudal se CALCULA con
    `serie_sin_fen` no se dimensiona, y su bloqueo dice las dos lluvias y el
    remedio. Los puntos con el caudal declarado en la columna no cambian.
    """
    from src import servicio
    from src.modelos import TipoDeBloqueo
    ruta = _csv_con(tmp_path, A02_SIN_Q)
    h = servicio.cargar_hidrologia(_cuencas_con(tmp_path, [CUENCA_CHICA]), ESTACION)
    with _declarados({FEN: "serie_sin_fen"}):
        informe = servicio.correr(ruta, externos, "perfil", h)
    punto = _por_id(informe, "A-02")
    reales = punto.bloqueos_reales()
    assert [b.tipo for b in reales] == [TipoDeBloqueo.METODO_NO_EVALUABLE]
    assert reales[0].fase == servicio.FASE_HIDROLOGIA
    for trozo in ("serie_sin_fen", "serie_completa", "mas conservador", "Q_m3s"):
        assert trozo in reales[0].mensaje, trozo
    assert punto.caudal is None and not punto.dimensionado
    declarado = _por_id(informe, "A-01")
    assert declarado.dimensionado and declarado.caudal.tratamiento_fen is None
    assert not any(b.fase == servicio.FASE_HIDROLOGIA for b in declarado.bloqueos)


def test_la_familia_B_calcula_su_caudal_con_el_mismo_modulo(tmp_path, externos):
    """Punto 4: area tributaria como cuenca, la cuneta como cauce, TR 35."""
    from src import servicio
    cuneta = {"id": "B-01", "area_km2": "0.004", "L_cauce_m": "200",
              "S_cauce_cuenca": "0.01", "S_terreno": "0.02",
              "cobertura": "pavimento", "suelo": "",
              "estacion": ESTACION_DE_PRUEBA,
              "metodo_tc": "federal_aviation_administration"}
    ruta = _csv_con(tmp_path, {"B-01": {"Q_m3s": "", "area_ha": "0.4"}})
    h = servicio.cargar_hidrologia(_cuencas_con(tmp_path, [cuneta]), ESTACION)
    with _declarados({FEN: "serie_completa"}):
        punto = _por_id(servicio.correr(ruta, externos, "perfil", h), "B-01")
    assert punto.caudal.calculado and punto.caudal.TR_anios == 35
    # Pavimento a 35 años: 0.90 con el incremento de 50 años pasa del tope
    # de la fuente y queda en 0.95. Y el tiempo de concentracion es el de
    # flujo superficial, no el de un cauce de montaña.
    assert punto.caudal.C == pytest.approx(0.95, rel=REL_TRANSPORTE)
    assert punto.caudal.metodo_tc == "federal_aviation_administration"
    assert punto.punto_de_calculo.Q_m3s == pytest.approx(
        0.278 * 0.95 * punto.caudal.I_mm_h * 0.004, rel=REL)
    from src.modulos.M1_clasificacion import PERFILES
    from src.modelos import Familia
    assert "MH_hidrologia" in PERFILES[Familia.B].origen_del_caudal


def test_cuencas_y_estacion_van_juntas():
    from src import servicio
    from src.modelos import DatoFaltanteError
    assert servicio.cargar_hidrologia(None, None) is None
    with pytest.raises(DatoFaltanteError) as exc:
        servicio.cargar_hidrologia(CUENCAS, None)
    assert exc.value.campo == "estacion"
    with pytest.raises(DatoFaltanteError) as exc:
        servicio.cargar_hidrologia(None, ESTACION)
    assert exc.value.campo == "cuencas"


def test_una_cuenca_que_nombra_una_estacion_ausente_no_se_carga(tmp_path):
    from src import servicio
    from src.modelos import DatoFaltanteError
    otra = _cuencas_con(tmp_path, [{**CUENCA_CHICA, "estacion": "OTRA"}])
    with pytest.raises(DatoFaltanteError) as exc:
        servicio.cargar_hidrologia(otra, ESTACION)
    assert exc.value.campo == "estacion" and "OTRA" in str(exc.value)


def test_una_cuenca_sin_punto_en_el_csv_queda_avisada(tmp_path, externos):
    from src import servicio
    huerfana = _cuencas_con(tmp_path, [{**CUENCA_CHICA, "id": "Z-99"}])
    h = servicio.cargar_hidrologia(huerfana, ESTACION)
    informe = servicio.correr(PUNTOS, externos, "perfil", h)
    assert any("Z-99" in b.mensaje and b.campo == "cuencas"
               for b in informe.cabezal.bloqueos)


def test_los_criterios_hidrologicos_son_de_perfil_porque_el_perfil_los_invoca(
        tmp_path, externos):
    """El nivel medido: una corrida de perfil con hidrologia los usa."""
    from src import criterios_adoptados as ca, servicio
    ruta = _csv_con(tmp_path, A02_SIN_Q)
    h = servicio.cargar_hidrologia(_cuencas_con(tmp_path, [CUENCA_CHICA]), ESTACION)
    with _declarados({FEN: "serie_completa"}):
        informe = servicio.correr(ruta, externos, "perfil", h)
    usados = set(informe.contexto.criterios_usados)
    for clave in (FEN, "distribucion_precipitacion_maxima",
                  "nivel_significancia_ks", "relacion_intensidad_duracion"):
        assert clave in usados, clave
        assert ca.CRITERIOS[clave].nivel == ca.NIVEL_PERFIL
        assert ca.CRITERIOS[clave].etiqueta == "A" and ca.CRITERIOS[clave].sensibilidad
    # Los cuatro de la auditoria de T-1, medidos con las cuencas que los
    # alcanzan: una fuera de la poblacion de Kirpich (con el trato en
    # «indicador»), una con Temez y una superficie vial. La duracion minima
    # la lee todo caudal calculado.
    assert "duracion_minima_lluvia_min" in usados
    filas = [{"id": "A-01", "area_km2": "8.5", "L_cauce_m": "5200",
              "S_cauce_cuenca": "0.012", "S_terreno": "0.03",
              "cobertura": "pastos_vegetacion_ligera", "suelo": "semipermeable",
              "estacion": ESTACION_DE_PRUEBA, "metodo_tc": "temez"},
             {"id": "A-02", "area_km2": "2.1", "L_cauce_m": "2400",
              "S_cauce_cuenca": "0.004", "S_terreno": "0.01",
              "cobertura": "cultivos", "suelo": "semipermeable",
              "estacion": ESTACION_DE_PRUEBA, "metodo_tc": "kirpich",
              "ajuste_kirpich": "ninguno"},
             {"id": "B-01", "area_km2": "0.18", "L_cauce_m": "900",
              "S_cauce_cuenca": "0.008", "S_terreno": "0.02",
              "cobertura": "talud_de_tierra", "suelo": "",
              "estacion": ESTACION_DE_PRUEBA,
              "metodo_tc": "federal_aviation_administration"}]
    sin_q = _csv_con(tmp_path, {i: {"Q_m3s": ""} for i in ("A-01", "A-02", "B-01")},
                     nombre="sin_q.csv")
    h3 = servicio.cargar_hidrologia(_cuencas_con(tmp_path, filas, "tres.csv"),
                                    ESTACION)
    nuevos = ("duracion_minima_lluvia_min", "tc_fuera_de_la_poblacion_del_metodo",
              "coeficiente_uniformidad_temez",
              "coeficiente_escorrentia_superficie_vial")
    with _declarados({FEN: "serie_completa",
                      "tc_fuera_de_la_poblacion_del_metodo": "indicador_con_aviso"}):
        tres = servicio.correr(sin_q, externos, "perfil", h3)
    for clave in nuevos:
        assert clave in tres.contexto.criterios_usados, clave
        assert ca.CRITERIOS[clave].nivel == ca.NIVEL_PERFIL
    assert all(_por_id(tres, i).caudal.calculado for i in ("A-01", "A-02", "B-01"))
    assert any("EXTRAPOLADO" in a for a in _por_id(tres, "A-02").caudal.avisos)
    # Y la corrida del fixture, con Q lleno, no invoca ninguno.
    base = servicio.correr(PUNTOS, externos, "perfil")
    assert not usados & set(base.contexto.criterios_usados) & {
        FEN, "distribucion_precipitacion_maxima", "nivel_significancia_ks",
        "relacion_intensidad_duracion"}


def test_el_barrido_admite_la_hidrologia(tmp_path, externos):
    """Los criterios hidrologicos se barren como cualquier [A]."""
    import cli
    from src import barrido, servicio
    ruta = _csv_con(tmp_path, A02_SIN_Q)
    h = servicio.cargar_hidrologia(_cuencas_con(tmp_path, [CUENCA_CHICA]), ESTACION)
    resultado = barrido.barrer(
        ruta, externos, "perfil", FEN, ("serie_completa", "serie_sin_fen"),
        hidrologia=h, volcar=cli.informe_json)
    con, sin = (next(p for p in c.informe_json["puntos"] if p["id"] == "A-02")
                for c in resultado.corridas)
    assert con["caudal"]["origen"] == "calculado" and con["dimensionado"]
    # `serie_sin_fen` da menos lluvia que la completa: el punto se detiene
    # en la Fase 1-bis y no se dimensiona (T1-09), y el barrido lo muestra.
    assert sin["caudal"] is None and not sin["dimensionado"]
    assert any("mas conservador" in b["mensaje"] for b in sin["bloqueos"])


# ===========================================================================
# 9. La CLI, el JSON y la memoria
# ===========================================================================

def _correr_cli(tmp_path, args):
    import cli
    salida = tmp_path / "salida.json"
    html = tmp_path / "memoria.html"
    codigo = cli.main([*map(str, args), "--luz", "2.0", "--tw", "0",
                       "--alcance", "perfil", "--json", str(salida),
                       "--html", str(html)])
    return codigo, json.loads(salida.read_text(encoding="utf-8")), \
        html.read_text(encoding="utf-8")


def _bloque_del_punto(html, id_punto):
    from src.modulos import M11_reporte as M11
    inicio = html.index(f'id="{M11.ancla_de_punto(id_punto)}"')
    fin = html.find('<div class="punto', inicio + 1)
    return html[inicio:fin if fin != -1 else len(html)]


def test_la_cli_imprime_el_Q_declarado_en_el_json_y_en_la_memoria(tmp_path, capsys):
    _, volcado, html = _correr_cli(tmp_path, [PUNTOS])
    texto = capsys.readouterr().out
    assert "Q declarado por el estudio hidrológico" in texto
    for id_punto in ("A-01", "A-02", "B-01"):
        punto = next(p for p in volcado["puntos"] if p["id"] == id_punto)
        assert punto["caudal"]["origen"] == "declarado"
        assert punto["caudal"]["leyenda"] == "Q declarado por el estudio hidrológico"
        assert punto["caudal"]["pasos"] == ["1b.8"]
        bloque = _bloque_del_punto(html, id_punto)
        assert "Q declarado por el estudio hidrológico" in bloque
        assert FEN in bloque                              # el aviso, en el punto
    c = next(p for p in volcado["puntos"] if p["id"] == "C-01")
    assert c["caudal"] is None
    assert "hidrologia" not in volcado["expediente"]


def test_la_cli_calcula_con_cuencas_y_estacion_y_la_memoria_trae_los_ocho_pasos(
        tmp_path, capsys):
    ruta = _csv_con(tmp_path, A02_SIN_Q)
    cuencas = _cuencas_con(tmp_path, [CUENCA_CHICA])
    # El pre-vuelo (auditoria de T-1, H9): con --cuencas y --estacion no
    # llama falta a un Q_m3s vacio que la corrida va a calcular, y dice que
    # el no calcula la hidrologia.
    import cli
    capsys.readouterr()
    cli.main([str(ruta), "--prevuelo", "--luz", "2.0", "--tw", "0",
              "--alcance", "perfil", "--cuencas", str(cuencas),
              "--estacion", str(ESTACION)])
    prevuelo = capsys.readouterr().out
    linea = next(x for x in prevuelo.splitlines() if "A-02" in x and "Q_m3s" in x)
    assert "DETIENE" not in linea and "depende de la hidrologia" in linea
    assert "NO calcula la hidrologia" in prevuelo
    c01 = next(x for x in prevuelo.splitlines() if "C-01" in x and "· Q_m3s ·" in x)
    assert "MH_hidrologia" not in c01          # la Fase 1-bis no lee ese caudal
    codigo, volcado, html = _correr_cli(
        tmp_path, [ruta, "--cuencas", cuencas, "--estacion", ESTACION,
                   "--declarar", f"{FEN}=serie_completa"])
    from src import criterios_adoptados as ca
    ca.quitar_valor_dinamico(FEN)
    texto = capsys.readouterr().out
    punto = next(p for p in volcado["puntos"] if p["id"] == "A-02")
    assert punto["caudal"]["origen"] == "calculado" and punto["dimensionado"]
    assert punto["caudal"]["pasos"] == PASOS_DE_LA_FASE_1B
    assert punto["caudal"]["TR_anios"] == 35
    assert punto["caudal"]["metodo_tc"] == "kirpich"
    assert punto["caudal"]["duracion_min"] == pytest.approx(
        punto["caudal"]["tc_min"], rel=REL_TRANSPORTE)
    assert punto["caudal"]["K_uniformidad"] is None
    # Los avisos del calculo llegan al JSON y a la salida de texto (H1, H10).
    assert any("POR DEBAJO" in a for a in punto["caudal"]["avisos"])
    assert "POR DEBAJO" in texto
    assert punto["diseno"]["Q_m3s"] == pytest.approx(punto["caudal"]["Q_m3s"],
                                                     rel=REL_TRANSPORTE)
    assert volcado["expediente"]["hidrologia"]["obras_con_cuenca"] == ["A-02"]
    assert "Q calculado por el programa" in texto and "Hidrologia: TR 35" in texto
    bloque = _bloque_del_punto(html, "A-02")
    for rotulo in ("Q = 0.278 · C · I · A", "Tabla N 08", "Kolmogorov-Smirnov",
                   "tc = f · 0.01947", "Pd = P24 · (d / 1440)^0.25",
                   "Q calculado por el programa"):
        assert rotulo in bloque, rotulo
    # La celda vacia de Q_m3s no se imprime como «dato de un tablero
    # externo»: dice que el caudal lo calculo el programa.
    assert "columna <code>Q_m3s</code> vacia &mdash; Q calculado" in bloque
    # Las citas de los pasos estan en el anexo de referencias de la memoria.
    assert "Método Racional" in html and "Tiempo de Concentración" in html


def test_la_cli_rechaza_cuencas_sin_estacion(tmp_path, capsys):
    import cli
    codigo = cli.main([str(PUNTOS), "--luz", "2.0", "--cuencas", str(CUENCAS),
                       "--json", str(tmp_path / "x.json")])
    assert codigo == 2
    assert "estacion" in capsys.readouterr().err
    assert not (tmp_path / "x.json").exists()


# ===========================================================================
# 10. legacy/Tc.py deja de ser la fuente declarada (INF-5.2.5)
# ===========================================================================

def test_el_origen_del_caudal_de_la_familia_A_nombra_a_MH_hidrologia():
    from src.modelos import Familia
    from src.modulos.M1_clasificacion import PERFILES
    origen = PERFILES[Familia.A].origen_del_caudal
    assert "MH_hidrologia" in origen and "Q_m3s" in origen
    assert "Tc.py" not in origen


def test_legacy_tc_esta_marcado_superseded_y_no_se_borro():
    ruta = RAIZ / "legacy" / "Tc.py"
    assert ruta.exists()
    docstring = ast.get_docstring(ast.parse(ruta.read_text(encoding="utf-8")))
    assert "SUPERSEDED" in docstring and "MH_hidrologia" in docstring
    assert docstring.index("SUPERSEDED") < docstring.index("ESTATUS EN ESTE REPOSITORIO")


def test_solo_el_servicio_importa_MH_hidrologia():
    """«nuevo modulo, importado solo por servicio.py» (T-1, punto 1)."""
    importadores = []
    for ruta in [*sorted((RAIZ / "src").rglob("*.py")),
                 *sorted((RAIZ / "gui").rglob("*.py")), RAIZ / "cli.py"]:
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            nombres = []
            if isinstance(nodo, ast.ImportFrom):
                nombres = [nodo.module or ""] + [a.name for a in nodo.names]
            elif isinstance(nodo, ast.Import):
                nombres = [a.name for a in nodo.names]
            if any("MH_hidrologia" in n for n in nombres):
                importadores.append(ruta.relative_to(RAIZ).as_posix())
    assert sorted(set(importadores)) == ["src/servicio.py"]


def test_el_criterio_fen_tiene_consumidor_real():
    from src import variables_entrada as ve
    assert "MH_hidrologia" in " ".join(ve.variable(FEN).consumido_por)


# ===========================================================================
# 11. INF-5.1.3: el umbral de 100 ha ya no se justifica con el fixture
# ===========================================================================

def test_la_ficha_del_umbral_de_area_no_se_apoya_en_el_fixture():
    from src import criterios_adoptados as ca
    c = ca.CRITERIOS["umbral_area_quebrada_importante_ha"]
    # El valor y la ventana, intactos: los mismos que traia origin/main.
    assert (c.valor, *c.sensibilidad) == pytest.approx((100.0, 50.0, 200.0),
                                                      rel=REL_TRANSPORTE)
    assert c.etiqueta == "A"
    with PUNTOS.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    prosa = " ".join((c.justificacion, c.concepto, c.fuente,
                      c.verificacion_pendiente or "", c.reemplazado_por or ""))
    for fila in filas:
        assert fila["id"] not in prosa, fila["id"]
        if fila["area_ha"]:
            assert f"{fila['area_ha']} ha" not in prosa
    assert "fixture" not in prosa and "ejemplo_puntos" not in prosa
    # Lo que si tiene que decir: que la fuente no da regla, la direccion del
    # conservadurismo y que se defiende barriendo la ventana.
    assert "no hay umbral de area" in c.justificacion
    assert "conservador" in c.justificacion and "se barre" in c.justificacion
    assert "adopcion del proyecto" in c.justificacion


def test_el_periodo_de_retorno_del_fixture_no_se_movio(externos):
    """El valor no cambio: A-01 y A-02 siguen en TR 71 y B-01 en 35."""
    from src import servicio
    informe = servicio.correr(PUNTOS, externos, "perfil")
    tr = {i.punto.id: i.clasificacion.periodo_retorno.anios for i in informe.puntos}
    assert (tr["A-01"], tr["A-02"], tr["B-01"]) == (71, 71, 35)
