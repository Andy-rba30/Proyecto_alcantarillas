"""
tests/test_t9_espaciamiento.py
==============================
La aceptacion de T-9 de la cadena T: el espaciamiento de las alcantarillas de
alivio (Familia B) con la longitud por capacidad de la cuneta CALCULADA, y la
verificacion VB1 por tramo, que puede fallar (INF-5.1.12). Tambien cierra el
cableado de la aceptacion de la Familia B (v8 §2.3, ficha T0-03) y le da a
`area_ha` un consumidor real en la Familia B (INF-5.1.8).

LO QUE SE COMPRUEBA, en el orden del calculo:

  1. El registro: las citas del num. 4.1.2 / 4.1.2.1 del Manual de
     Hidrologia y del 304.11 del DG-2018, y las Tablas Nº 32, 33 y 34, contra
     su pagina (marca `pdf`); las vistas de `constantes_normativas` DERIVADAS
     de ellas.
  2. Los tres criterios de la cuneta: la seccion SIN valor (es del trazo), el
     revestimiento de concreto que la fuente recomienda, la lectura
     conservadora de la Tabla Nº 33; ventanas y puerta.
  3. M10: la capacidad (cuneta llena y velocidad limite), el caudal por
     metro, la longitud por capacidad y el espaciamiento maximo, contra la
     ARITMETICA ESCRITA a mano en este archivo (los dorados no salen del
     codigo).
  4. VB1 por tramo: cumple, NO cumple de verdad, el menor de dos maximos, el
     tramo sin extremo, el extremo cuya Fase 10 no cerro.
  5. El pipeline: dos alivios en un CSV de prueba, la verificacion en el
     informe, la CLI, el JSON y la memoria; los avisos por `avisos()`; el
     pre-vuelo; el puente con la hidrologia (`MH.caudal_de_aporte_cuneta`);
     el nivel medido por una corrida de perfil que calcula L_hidraulico.

LOS TESTS SE ESCRIBIERON DESPUES DEL CODIGO, y se dice en vez de disimularlo:
el rojo se midio corriendo este archivo contra un arbol exportado de
`df1b23c` (la base de T-9) con un `xfail(strict=True)` de modulo: 81 de 82
en rojo y 1 XPASS (la guardia de que M10 no importa la hidrologia, que vale
antes y despues); ver la ficha T9-06 de `docs/decisiones_diferidas.md`.

Los datos de los CSV y JSON de este archivo son DATOS DE PRUEBA, NO DEL
PROYECTO: secciones, anchos, pendientes y progresivas inventados para
ejercitar el calculo.

REESCRITO EN LAS CORRECCIONES DE LA AUDITORIA DE T-9 (2026-11-13), y se dice
test por test donde cambia la verdad. Tres causas, las tres decididas: (1)
la seccion de PRUEBA (0.30 x 0.75, region lluviosa) ya no entra por la
puerta del criterio --la decision A del dueño le dio a 'seccion_cuneta' el
minimo de la region muy lluviosa y la ventana empieza ahi--, de modo que los
dorados de la aritmetica se conservan SUSTITUYENDO el valor efectivo del
criterio (fixture `seccion`, la segunda linea de M10 la acepta) en vez de
declararlo; (2) la decision C hace de A-02 el extremo del tramo de B-01
(530 m), de modo que los tests que esperaban «B-01 sin extremo» lo piden
ahora con el criterio en «no»; (3) H1: con el tramo conocido la longitud
por capacidad ya no depende de `area_ha`. Los tests nuevos de las
correcciones estan en `tests/test_t9_correcciones.py`.
"""

from __future__ import annotations

import csv
import io
import json
import math
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from src import anticipo
from src import constantes_normativas as CN
from src import criterios_adoptados as ca
from src import servicio
from src.modelos import METODO_APORTE_AREA, METODO_APORTE_TRAMO
from src.modelos import (CODIGO_VB1, CriterioPendienteError,
                         DatoInvalidoError, EstadoDeVerificacion, Familia,
                         GobiernaEspaciamiento, TipoDeVeredicto)
from src.modulos import M10_espaciamiento as M10
from src.modulos import M11_reporte as M11
from src.modulos.M1_clasificacion import PERFILES
from src.normativa import registro as _registro
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "tests" / "ejemplo_puntos.csv"
HIDRO = RAIZ / "tests" / "fixtures" / "hidrologia"

# Tolerancias de este archivo, nombradas (CLAUDE.md).
REL_ARITMETICA = 1e-4        # la aritmetica escrita con cuatro o cinco cifras
REL_FORMULA = 1e-9           # una formula recomputada en el test

# La seccion de PRUEBA con que se ejercita la capacidad: la Tabla Nº 34 para
# region «lluviosa» (0.30 x 0.75 m), talud exterior 1:1 y sin borde libre.
SECCION_PRUEBA = {"profundidad_m": 0.30, "ancho_m": 0.75,
                  "talud_exterior_HV": 1.0, "borde_libre_m": 0.0}
CRITERIOS_DE_LA_CUNETA = ("seccion_cuneta", "revestimiento_cuneta",
                          "lectura_velocidad_limite_cuneta")


@pytest.fixture(autouse=True)
def _limpio():
    """Ningun test deja un criterio de la cuneta declarado en caliente."""
    yield
    for clave in CRITERIOS_DE_LA_CUNETA + ("homogeneidad_serie_fen",
                                           "obras_familia_a_extremo_de_cuneta"):
        if ca.declarado_en_caliente(clave):
            ca.quitar_valor_dinamico(clave)


def sustituir_seccion(monkeypatch, valor):
    """
    El valor EFECTIVO de 'seccion_cuneta' sustituido sin pasar por la puerta.
    Desde la decision A la ventana empieza en 0.40 x 1.20 m (minimo de la
    region muy lluviosa) y la seccion de prueba de la aritmetica escrita en
    este archivo (0.30 x 0.75) ya no se puede DECLARAR; M10 la acepta en su
    segunda linea (Z1 = 2.5 >= 2, Tabla 304.12 en casos muy especiales).
    """
    original = ca.valor
    monkeypatch.setattr(ca, "valor", lambda clave: (
        dict(valor) if clave == "seccion_cuneta" else original(clave)))


@pytest.fixture
def seccion(monkeypatch):
    sustituir_seccion(monkeypatch, SECCION_PRUEBA)


# ===========================================================================
# 1. El registro y las vistas de calculo
# ===========================================================================

CITAS_T9 = ("MC_HHD.4.1.2.1#SECCION", "MC_HHD.4.1.2.1a",
            "MC_HHD.4.1.2.1a#MANNING", "MC_HHD.4.1.2.1#T32",
            "MC_HHD.4.1.2.1#T33", "MC_HHD.4.1.2.1a#VELOCIDAD",
            "MC_HHD.4.1.2.1c#T34", "MC_HHD.4.1.2c", "MC_HHD.4.1.2a",
            "MC_HHD.4.1.2.1e", "DG2018.304.11")


@pytest.mark.parametrize("cita_id", CITAS_T9)
def test_las_citas_de_T9_estan_firmadas_por_T9(cita_id):
    c = _registro.construir().cita(cita_id)
    assert c.verificado is not None
    assert c.verificado.por.startswith("tesis/T-9")


def test_las_paginas_de_las_citas_del_manual_son_las_de_su_paginacion():
    """Desfase +3 del Manual de Hidrologia y +1 del DG-2018."""
    reg = _registro.construir()
    for cita_id in CITAS_T9:
        c = reg.cita(cita_id)
        desfase = 1 if c.fuente_id == "DG2018" else 3
        assert c.pagina_pdf == int(c.pagina_impresa) + desfase, cita_id


@pytest.mark.pdf
def test_cada_cita_de_T9_dice_lo_que_su_pagina_dice():
    from src.normativa import fuentes as F
    from src.normativa.extraccion import aparece_en_pagina, pymupdf_disponible
    if not pymupdf_disponible():
        pytest.skip("sin PyMuPDF")
    reg = _registro.construir()
    for cita_id in CITAS_T9:
        c = reg.cita(cita_id)
        ruta = F.ruta_pdf(getattr(F, c.fuente_id))
        if not ruta.exists():
            pytest.skip(f"sin el PDF de {c.fuente_id}")
        assert aparece_en_pagina(ruta, c.texto_literal.pagina_pdf,
                                 c.texto_literal.texto), cita_id
        assert aparece_en_pagina(ruta, c.pagina_del_titulo,
                                 c.titulo_numeral), cita_id


@pytest.mark.pdf
@pytest.mark.parametrize("tabla_id", ("MC_HHD.T32", "MC_HHD.T33", "MC_HHD.T34"))
def test_cada_fila_de_las_tablas_de_la_cuneta_esta_en_su_pagina(tabla_id):
    """Rotulo de la tabla, de cada fila y de cada columna, y las notas al pie."""
    from src.normativa import fuentes as F
    from src.normativa.extraccion import aparece_en_pagina, pymupdf_disponible
    if not pymupdf_disponible():
        pytest.skip("sin PyMuPDF")
    reg = _registro.construir()
    t = reg.tabla(tabla_id)
    ruta = F.ruta_pdf(F.MC_HHD)
    if not ruta.exists():
        pytest.skip("sin el PDF del Manual de Hidrologia")
    pagina = reg.cita(t.cita_id).texto_literal.pagina_pdf
    assert aparece_en_pagina(ruta, pagina, t.titulo_literal)
    for fila in t.filas:
        assert aparece_en_pagina(ruta, pagina, fila.etiqueta_literal), fila.id
    for columna in t.columnas:
        assert aparece_en_pagina(ruta, pagina, columna.etiqueta_literal)
    for nota in t.notas_al_pie:
        assert aparece_en_pagina(ruta, nota.texto.pagina_pdf, nota.texto.texto)


@pytest.mark.pdf
def test_los_valores_de_las_tres_tablas_estan_impresos_en_su_pagina():
    """Los numeros, no solo los rotulos: K, el intervalo de velocidad, d y a."""
    from src.normativa import fuentes as F
    from src.normativa.extraccion import pymupdf_disponible, texto_de_pagina
    if not pymupdf_disponible():
        pytest.skip("sin PyMuPDF")
    ruta = F.ruta_pdf(F.MC_HHD)
    if not ruta.exists():
        pytest.skip("sin el PDF del Manual de Hidrologia")
    p178 = " ".join(texto_de_pagina(ruta, 178).split())
    for K in (33, 25, 67):
        assert f"K = {K}" in p178
    for lo, hi in CN.CUNETA_VELOCIDAD_LIMITE_T33.values():
        assert f"{lo:.2f} – {hi:.2f}" in p178
    p181 = " ".join(texto_de_pagina(ruta, 181).split())
    for d, a in CN.CUNETA_DIMENSIONES_MINIMAS_T34.values():
        assert f"{d:.2f}" in p181 and f"{a:.2f}" in p181


def test_las_vistas_de_calculo_salen_del_registro():
    assert CN.CUNETA_STRICKLER_T32 == {"excavada_en_terreno": 33,
                                       "en_roca": 25, "de_concreto": 67}
    assert CN.CUNETA_VELOCIDAD_LIMITE_T33["concreto"] == pytest.approx(
        (4.50, 6.00), rel=REL_TRANSPORTE)
    assert CN.CUNETA_VELOCIDAD_LIMITE_T33["arena_fina_o_limo"] == pytest.approx(
        (0.20, 0.60), rel=REL_TRANSPORTE)
    assert len(CN.CUNETA_VELOCIDAD_LIMITE_T33) == 8
    assert CN.CUNETA_T33_MUY_CORTA_DURACION == ("mamposteria_rocas_duras",
                                                "concreto")
    esperadas = {"seca": (0.20, 0.50), "lluviosa": (0.30, 0.75),
                 "muy_lluviosa_1600_3000": (0.40, 1.20),
                 "muy_lluviosa_mas_de_3000": (0.30, 1.20)}
    assert set(CN.CUNETA_DIMENSIONES_MINIMAS_T34) == set(esperadas)
    for region, par in esperadas.items():
        assert CN.CUNETA_DIMENSIONES_MINIMAS_T34[region] == pytest.approx(
            par, rel=REL_TRANSPORTE), region
    assert CN.PENDIENTE_DRENAJE_LONGITUDINAL == pytest.approx(
        (0.005, 0.02), rel=REL_TRANSPORTE)
    assert CN.PENDIENTE_MIN_CUNETA_DG2018 == pytest.approx(
        {"revestida": 0.002, "sin_revestir": 0.005}, rel=REL_TRANSPORTE)


def test_cada_revestimiento_une_dos_filas_que_existen():
    for clave, (fila_32, fila_33) in ca.REVESTIMIENTOS_CUNETA.items():
        assert fila_32 in CN.CUNETA_STRICKLER_T32, clave
        assert fila_33 in CN.CUNETA_VELOCIDAD_LIMITE_T33, clave
    # Cada fila de la Tabla Nº 33 tiene su revestimiento: ninguna queda sin
    # poder elegirse.
    assert {f for _, f in ca.REVESTIMIENTOS_CUNETA.values()} == \
        set(CN.CUNETA_VELOCIDAD_LIMITE_T33)
    assert ca.REVESTIMIENTOS_CUNETA["concreto"] == ("de_concreto", "concreto")


def test_los_fundamentos_de_la_fase_10_existen_y_el_de_VB1_obliga():
    reg = _registro.construir()
    for fid in ("F10.CAPACIDAD", "F10.APORTE", "F10.L_HIDRAULICO",
                "F10.TRAMO", "F10.CUNETA"):
        reg.fundamento(fid)
    assert reg.fundamento("F10.TRAMO").verbo.value == "obliga"
    assert not reg.problemas_de_integridad()


# ===========================================================================
# 2. Los criterios de la cuneta
# ===========================================================================

def test_la_seccion_de_la_cuneta_tiene_el_minimo_muy_lluvioso_y_su_ventana_cita_sus_fuentes():
    """
    REESCRITO (decision A del dueño, correcciones de T-9). Antes: la seccion
    nacia SIN valor y la ventana empezaba en el minimo de la region SECA
    (0.20 x 0.50). Ahora: el valor de archivo es el minimo de la region MUY
    LLUVIOSA de la Tabla Nº 34 (0.40 x 1.20, la region que el proyecto adopta
    con 'long_max_cuneta'), con Z2 = 1.0 adoptado y borde libre 0, y la
    ventana empieza ahi (H5: un barrido no puede bajar del minimo EXIGIDO).
    """
    c = ca.CRITERIOS["seccion_cuneta"]
    assert c.etiqueta == "A" and c.nivel == ca.NIVEL_PERFIL
    assert c.valor == pytest.approx({"profundidad_m": 0.40, "ancho_m": 1.20,
                                     "talud_exterior_HV": 1.0,
                                     "borde_libre_m": 0.0},
                                    rel=REL_TRANSPORTE, abs=ABS_CERO)
    ventana = {"profundidad_m": (0.40, 0.60), "ancho_m": (1.20, 2.40),
               "talud_exterior_HV": (0.10, 2.0), "borde_libre_m": (0.0, 0.10)}
    assert set(c.sensibilidad) == set(ventana)
    for campo, par in ventana.items():
        assert c.sensibilidad[campo] == pytest.approx(par, rel=REL_TRANSPORTE,
                                                      abs=ABS_CERO), campo
    # Los pisos son los MINIMOS de la fila muy lluviosa de la Tabla Nº 34.
    d, a = CN.CUNETA_DIMENSIONES_MINIMAS_T34["muy_lluviosa_1600_3000"]
    assert c.sensibilidad["profundidad_m"][0] == pytest.approx(d, rel=REL_TRANSPORTE)
    assert c.sensibilidad["ancho_m"][0] == pytest.approx(a, rel=REL_TRANSPORTE)
    assert "Tabla Nº 34" in c.fuente and "304.11" in c.fuente
    assert ca.valor("seccion_cuneta") == c.valor


@pytest.mark.parametrize("campo,valor", [
    ("profundidad_m", 0.70),      # «Elijo una altura H, que sea menor a 0.60m»
    ("profundidad_m", 0.30),      # bajo el minimo de la region muy lluviosa
    ("ancho_m", 0.75),            # idem
    ("talud_exterior_HV", 3.0),
    ("borde_libre_m", 0.20),
])
def test_la_puerta_rechaza_una_seccion_fuera_de_su_ventana(campo, valor):
    """La base es el valor de archivo, que entra: solo el campo cambiado sale."""
    base = dict(ca.CRITERIOS["seccion_cuneta"].valor)
    ca.establecer_valor_dinamico("seccion_cuneta", dict(base))
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico("seccion_cuneta",
                                     dict(base, **{campo: valor}))


def test_el_revestimiento_es_el_concreto_que_la_fuente_recomienda():
    c = ca.CRITERIOS["revestimiento_cuneta"]
    assert c.valor == "concreto" and c.etiqueta == "A"
    assert c.sensibilidad == tuple(ca.REVESTIMIENTOS_CUNETA)
    assert c.nivel == ca.NIVEL_PERFIL
    assert "4.1.2.1" in c.fuente


def test_la_lectura_de_la_tabla_33_es_la_conservadora_y_barrible():
    c = ca.CRITERIOS["lectura_velocidad_limite_cuneta"]
    assert c.valor == "extremo_inferior"
    assert c.sensibilidad == ("extremo_inferior", "extremo_superior")
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico("lectura_velocidad_limite_cuneta",
                                     "promedio")


# ===========================================================================
# 3. M10, contra la aritmetica escrita
# ===========================================================================
#
# Cuneta de concreto, d = 0.30 m, a = 0.75 m, talud exterior 1:1, S = 0.01:
#
#   Z1 = 0.75 / 0.30 = 2.5 ; Z2 = 1.0
#   A  = (2.5 + 1.0) · 0.30² / 2 = 3.5 · 0.09 / 2 = 0.1575 m2
#   P  = 0.30 · (√7.25 + √2) = 0.30 · (2.692582 + 1.414214) = 1.232039 m
#   Rh = 0.1575 / 1.232039 = 0.127837 m ; Rh^(2/3) = 0.253771
#   Q_llena = 67 · 0.1575 · 0.253771 · 0.1 = 0.267789 m3/s
#   V_llena = 0.267789 / 0.1575 = 1.7002 m/s < 4.50 (concreto) -> cuneta llena
#
# Con q = 0.278 · 0.9 · 120 = 30.024 m3/s por km2 y b = 12 m:
#   q' = 30.024 · 12 / 10^6 = 3.60288e-4 m3/s por m
#   L_hidraulico = 0.267789 / 3.60288e-4 = 743.26 m -> gobierna el normativo
A_PRUEBA = 0.1575
RH_PRUEBA = 0.127837
Q_LLENA_PRUEBA = 0.267789
V_LLENA_PRUEBA = 1.7002
Q_POR_METRO_PRUEBA = 3.60288e-4
L_PRUEBA = 743.26


def test_la_geometria_del_triangulo_corrige_el_ejemplo_del_manual():
    """
    Con los dos taludes 1:2 (V:H) y profundidad H: A = 2·H² y Rh = H/√5, no
    los A = 5H²/4 y Rh = 5√H/6 de las ecuaciones (4.3) y (4.1) del Manual
    (ficha T9-04). Con H = 0.30: A = 0.18 m2, P = 2·0.30·√5 = 1.341641 m,
    Rh = 0.134164 m.
    """
    A, P, Rh = M10.geometria_triangular(y=0.30, Z1=2.0, Z2=2.0)
    assert A == pytest.approx(0.18, rel=REL_TRANSPORTE)
    assert P == pytest.approx(1.341641, rel=REL_ARITMETICA)
    assert Rh == pytest.approx(0.30 / math.sqrt(5), rel=REL_FORMULA)
    assert A != pytest.approx(5 * 0.30 ** 2 / 4, rel=REL_ARITMETICA)


def test_el_caudal_a_la_velocidad_limite_tiene_esa_velocidad():
    """La ecuacion (4.2) despejada: Manning en y_v da exactamente v."""
    n, S, Z1, Z2, v = 1 / 33, 0.01, 2.5, 1.0, 0.20
    y_v, Q_v = M10.caudal_a_velocidad(v=v, n=n, S=S, Z1=Z1, Z2=Z2)
    A, _P, Rh = M10.geometria_triangular(y=y_v, Z1=Z1, Z2=Z2)
    assert Q_v / A == pytest.approx(v, rel=REL_FORMULA)
    manning = (1 / n) * Rh ** (2 / 3) * math.sqrt(S)
    assert manning == pytest.approx(v, rel=REL_FORMULA)
    assert y_v == pytest.approx(0.0350138, rel=REL_ARITMETICA)


def test_la_capacidad_de_la_cuneta_llena_es_la_de_la_aritmetica(seccion):
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    assert c.talud_interior_HV == pytest.approx(2.5, rel=REL_TRANSPORTE)
    assert c.area_llena_m2 == pytest.approx(A_PRUEBA, rel=REL_ARITMETICA)
    assert c.radio_llena_m == pytest.approx(RH_PRUEBA, rel=REL_ARITMETICA)
    assert c.Q_llena_m3s == pytest.approx(Q_LLENA_PRUEBA, rel=REL_ARITMETICA)
    assert c.V_llena_m_s == pytest.approx(V_LLENA_PRUEBA, rel=REL_ARITMETICA)
    assert c.n == pytest.approx(1 / 67, rel=REL_TRANSPORTE)
    assert c.v_limite_m_s == pytest.approx(4.50, rel=REL_TRANSPORTE)
    assert c.gobierna == "cuneta llena"
    assert c.Q_admisible_m3s == pytest.approx(c.Q_llena_m3s, rel=REL_FORMULA)
    # REESCRITO (H5): antes `avisos == ()`. Z1 = 2.5 cae entre 1:2 y 1:3 de
    # la Tabla 304.12, y desde las correcciones eso se avisa; es el unico.
    assert len(c.avisos) == 1 and "talud interior" in c.avisos[0]


def test_en_tierra_gobierna_la_velocidad_limite_y_se_avisa(seccion):
    """
    Arena fina o limo (Tabla Nº 33: 0.20 – 0.60 m/s; Tabla Nº 32: K = 33):

      Rh_v = (n·v/√S)^(3/2) = (0.030303 · 0.20 / 0.1)^(3/2) = 0.0149202 m
      c    = Rh/y = 3.5 / (2 · 4.106796) = 0.426123
      y_v  = 0.0149202 / 0.426123 = 0.0350138 m
      A_v  = 3.5 · 0.0350138² / 2 = 0.00214544 m2
      Q_v  = 0.00214544 · 0.20 = 4.29088e-4 m3/s
    """
    ca.establecer_valor_dinamico("revestimiento_cuneta",
                                 "terreno_arena_fina_o_limo")
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    assert c.gobierna == "velocidad limite admisible"
    assert c.Q_velocidad_m3s == pytest.approx(4.29088e-4, rel=REL_ARITMETICA)
    assert c.Q_admisible_m3s == pytest.approx(c.Q_velocidad_m3s, rel=REL_TRANSPORTE)
    assert c.Q_llena_m3s == pytest.approx(0.131896, rel=REL_ARITMETICA)
    assert any("VELOCIDAD LIMITE" in a for a in c.avisos)


def test_el_extremo_superior_de_la_tabla_33_sube_la_capacidad_por_v_a_la_cuarta(seccion):
    """Q_v = A(y_v)·v con y_v ∝ v^(3/2): Q_v ∝ v^4, (0.60/0.20)^4 = 81."""
    ca.establecer_valor_dinamico("revestimiento_cuneta",
                                 "terreno_arena_fina_o_limo")
    inferior = M10.capacidad_cuneta(S_cuneta=0.01).Q_velocidad_m3s
    ca.establecer_valor_dinamico("lectura_velocidad_limite_cuneta",
                                 "extremo_superior")
    superior = M10.capacidad_cuneta(S_cuneta=0.01).Q_velocidad_m3s
    assert superior / inferior == pytest.approx(81.0, rel=REL_FORMULA)


def test_el_borde_libre_resta_profundidad_util(monkeypatch):
    """y_u = 0.30 − 0.05 = 0.25 m: A = 3.5·0.0625/2 = 0.109375, Q = 0.164681."""
    sustituir_seccion(monkeypatch, dict(SECCION_PRUEBA, borde_libre_m=0.05))
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    assert c.tirante_util_m == pytest.approx(0.25, rel=REL_TRANSPORTE)
    assert c.area_llena_m2 == pytest.approx(0.109375, rel=REL_TRANSPORTE)
    assert c.Q_llena_m3s == pytest.approx(0.164681, rel=REL_ARITMETICA)


@pytest.mark.parametrize("S,avisa", [(0.003, True), (0.005, True),
                                     (0.01, False), (0.02, True),
                                     (0.03, True)])
def test_la_pendiente_fuera_de_la_banda_del_manual_avisa_y_no_detiene(seccion, S, avisa):
    """0.5 % < i < 2 %, desigualdades estrictas (num. 4.1.2 c))."""
    c = M10.capacidad_cuneta(S_cuneta=S)
    hay = any("pendiente de la cuneta" in a for a in c.avisos)
    assert hay is avisa
    if avisa:
        texto = next(a for a in c.avisos if "pendiente de la cuneta" in a)
        assert "4.1.2 c)" in texto and "304.11" in texto


@pytest.mark.parametrize("S", [0.0, -0.01, float("nan"), float("inf"), True])
def test_una_pendiente_no_fisica_es_dato_invalido(seccion, S):
    with pytest.raises(DatoInvalidoError):
        M10.capacidad_cuneta(S_cuneta=S)


def test_sin_seccion_la_capacidad_es_un_pendiente(monkeypatch):
    """
    REESCRITO (decision A): la seccion tiene valor de archivo, y lo que se
    comprueba es que VACIADA la capacidad se detiene en el pendiente, no en
    un defecto.
    """
    monkeypatch.setitem(ca.CRITERIOS, "seccion_cuneta",
                        replace(ca.CRITERIOS["seccion_cuneta"], valor=None))
    with pytest.raises(CriterioPendienteError) as exc:
        M10.capacidad_cuneta(S_cuneta=0.01)
    assert exc.value.clave == "seccion_cuneta"


def test_la_segunda_linea_rechaza_un_borde_libre_que_burla_la_puerta(monkeypatch, seccion):
    malo = dict(SECCION_PRUEBA, borde_libre_m=0.30)
    original = ca.valor
    monkeypatch.setattr(ca, "valor", lambda clave: (
        malo if clave == "seccion_cuneta" else original(clave)))
    with pytest.raises(DatoInvalidoError):
        M10.capacidad_cuneta(S_cuneta=0.01)


def test_la_longitud_por_capacidad_es_la_de_la_aritmetica(seccion):
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    L = M10.longitud_hidraulica(capacidad=c, escorrentia_m3s_km2=30.024,
                                origen_escorrentia="dato del test",
                                ancho_tributario_m=12.0)
    assert L.q_por_metro_m3s_m == pytest.approx(Q_POR_METRO_PRUEBA,
                                                rel=REL_FORMULA)
    assert L.L_hidraulico == pytest.approx(L_PRUEBA, rel=REL_ARITMETICA)
    codigos = [p.codigo for p in L.pasos]
    assert codigos == ["10.2", "10.3", "10.4"]
    e = M10.espaciamiento_alivio(L.L_hidraulico, longitud_hidraulica=L)
    assert e.gobierna is GobiernaEspaciamiento.NORMATIVO
    assert e.espaciamiento_max == pytest.approx(200.0, rel=REL_TRANSPORTE)
    assert e.origen_L_hidraulico == "calculado"
    assert [p.codigo for p in e.pasos] == ["10.2", "10.3", "10.4", "10.1"]


def test_la_longitud_es_inversa_a_la_escorrentia_y_al_ancho(seccion):
    c = M10.capacidad_cuneta(S_cuneta=0.01)

    def L(q, b):
        return M10.longitud_hidraulica(
            capacidad=c, escorrentia_m3s_km2=q, origen_escorrentia="t",
            ancho_tributario_m=b).L_hidraulico
    assert L(60.048, 12.0) == pytest.approx(L(30.024, 12.0) / 2, rel=REL_TRANSPORTE)
    assert L(30.024, 24.0) == pytest.approx(L(30.024, 12.0) / 2, rel=REL_TRANSPORTE)


@pytest.mark.parametrize("q,b", [(0.0, 12.0), (-1.0, 12.0), (30.0, 0.0),
                                 (float("nan"), 12.0), (30.0, float("inf"))])
def test_la_longitud_rechaza_escorrentia_o_ancho_no_fisicos(seccion, q, b):
    c = M10.capacidad_cuneta(S_cuneta=0.01)
    with pytest.raises(DatoInvalidoError):
        M10.longitud_hidraulica(capacidad=c, escorrentia_m3s_km2=q,
                                origen_escorrentia="t", ancho_tributario_m=b)


def test_el_espaciamiento_maximo_ya_no_dice_cumple_por_construccion():
    """INF-5.1.12: el paso 10.1 es un LIMITE; su veredicto no juzga."""
    e = M10.espaciamiento_alivio(120.0)
    assert e.paso.veredicto.tipo is TipoDeVeredicto.SIN_VEREDICTO
    assert e.origen_L_hidraulico == "declarado"
    assert e.longitud_hidraulica is None
    assert [p.codigo for p in e.pasos] == ["10.1"]


# ===========================================================================
# 4. VB1 por tramo
# ===========================================================================

def _tramo(s_km_desde, s_km_hasta, *maximos, extremo="B-01",
           origen=M10.ORIGEN_EXTREMO_OBRA_B):
    return M10.verificar_tramo(
        id_punto="B-02", progresiva_km=s_km_hasta, extremo=extremo,
        progresiva_extremo_km=s_km_desde, origen_extremo=origen,
        maximos=maximos)


def test_VB1_cumple_con_un_tramo_de_150_m():
    e = M10.espaciamiento_alivio(250.0)              # maximo 200 m
    t = _tramo(2.450, 2.600, ("B-02", e), ("B-01", e))
    v = t.verificacion
    assert t.longitud_m == pytest.approx(150.0, rel=REL_TRANSPORTE)
    assert v.codigo == CODIGO_VB1 and v.cumple
    assert v.valor_admisible == pytest.approx(200.0, rel=REL_TRANSPORTE)
    assert v.criterio_aplicado == "long_max_cuneta"
    assert v.paso.veredicto.margen == pytest.approx(50.0, rel=REL_TRANSPORTE)


def test_VB1_FALLA_con_un_tramo_de_250_m():
    """La verificacion que hasta T-9 no podia fallar, fallando."""
    e = M10.espaciamiento_alivio(250.0)
    t = _tramo(2.450, 2.700, ("B-02", e), ("B-01", e))
    v = t.verificacion
    assert t.longitud_m == pytest.approx(250.0, rel=REL_TRANSPORTE)
    assert not v.cumple and v.estado is EstadoDeVerificacion.NO_CUMPLE
    assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
    assert v.paso.veredicto.margen == pytest.approx(-50.0, rel=REL_TRANSPORTE)
    assert "otra alcantarilla de alivio" in v.paso.veredicto.explicacion


def test_VB1_toma_el_menor_de_los_dos_maximos():
    """Con 120 m en un extremo, un tramo de 150 m no cumple aunque el otro dé 200."""
    corto = M10.espaciamiento_alivio(120.0)
    largo = M10.espaciamiento_alivio(250.0)
    t = _tramo(2.450, 2.600, ("B-02", largo), ("B-01", corto))
    assert not t.verificacion.cumple
    assert t.verificacion.valor_admisible == pytest.approx(120.0, rel=REL_TRANSPORTE)
    # L_hidraulico declarado: es un dato, no un criterio.
    assert t.verificacion.criterio_aplicado is None
    assert "MENOR" in t.verificacion.paso.nota_del_proyecto


def test_VB1_sin_extremo_no_se_evalua_y_lo_avisa():
    t = M10.verificar_tramo(id_punto="B-01", progresiva_km=2.45,
                            extremo=None, progresiva_extremo_km=None,
                            origen_extremo="", maximos=())
    assert t.verificacion is None and t.longitud_m is None
    assert t.aviso == M10.AVISO_TRAMO_SIN_EXTREMO


def test_VB1_con_un_maximo_desconocido_solo_falla_si_excede_el_normativo():
    e = M10.espaciamiento_alivio(250.0)
    dentro = _tramo(2.450, 2.600, ("B-02", e), ("B-01", None))
    assert dentro.verificacion is None
    assert "B-01" in dentro.aviso and "NO SE EVALUO" in dentro.aviso
    fuera = _tramo(2.450, 2.700, ("B-02", e), ("B-01", None))
    assert not fuera.verificacion.cumple
    assert fuera.verificacion.valor_admisible == pytest.approx(200.0, rel=REL_TRANSPORTE)


def test_VB1_con_el_inicio_declarado_usa_solo_el_maximo_del_punto():
    e = M10.espaciamiento_alivio(180.0)
    t = _tramo(2.270, 2.450, ("B-02", e), extremo=M10.EXTREMO_DECLARADO,
               origen=M10.ORIGEN_EXTREMO_DECLARADO)
    assert t.longitud_m == pytest.approx(180.0, rel=REL_TRANSPORTE)
    assert t.verificacion.cumple
    assert t.verificacion.valor_admisible == pytest.approx(180.0, rel=REL_TRANSPORTE)


@pytest.mark.parametrize("prog", [float("nan"), -0.1, float("inf")])
def test_VB1_rechaza_una_progresiva_no_fisica(prog):
    e = M10.espaciamiento_alivio(250.0)
    with pytest.raises(DatoInvalidoError):
        _tramo(prog, 2.450, ("B-02", e))


# ===========================================================================
# 5. El pipeline: dos alivios, la CLI, el JSON, la memoria, el pre-vuelo
# ===========================================================================

def _csv_con(tmp_path, filas_extra=(), cambios=None, nombre="puntos.csv"):
    """El fixture del repositorio con filas B extra (copias de B-01)."""
    texto = CSV.read_text(encoding="utf-8")
    lector = list(csv.DictReader(io.StringIO(texto)))
    campos = list(lector[0].keys())
    filas = [dict(f) for f in lector]
    b01 = next(f for f in filas if f["id"] == "B-01")
    for id_nuevo, prog in filas_extra:
        filas.append(dict(b01, id=id_nuevo, progresiva_km=prog))
    for id_punto, cambio in (cambios or {}).items():
        next(f for f in filas if f["id"] == id_punto).update(cambio)
    salida = io.StringIO()
    escritor = csv.DictWriter(salida, fieldnames=campos, lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(filas)
    ruta = tmp_path / nombre
    ruta.write_text(salida.getvalue(), encoding="utf-8")
    return ruta


def _externos(tmp_path, contenido, **banderas):
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps(contenido), encoding="utf-8")
    return servicio.cargar_datos_externos(ruta, banderas)


def _punto(informe, id_punto):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


@pytest.fixture
def dos_alivios_250(tmp_path):
    """
    B-01 en 2+450 y B-02 en 2+700, las dos con L_hidraulico declarado, y el
    criterio de la decision C en «no» (solo las obras B cierran tramos), que
    es el caso que este fixture ejercitaba en la FASE A: B-01 sin extremo.
    """
    ca.establecer_valor_dinamico("obras_familia_a_extremo_de_cuneta", "no")
    ruta = _csv_con(tmp_path, [("B-02", "2+700")])
    externos = _externos(tmp_path, {"globales": {"luz_m": 2.75,
                                                 "L_hidraulico_m": 250.0}})
    return servicio.correr(ruta, externos, "perfil")


def test_el_tramo_de_250_m_entre_dos_alivios_no_cumple_en_el_informe(dos_alivios_250):
    b01 = _punto(dos_alivios_250, "B-01")
    b02 = _punto(dos_alivios_250, "B-02")
    v = b02.tramo_alivio.verificacion
    assert v is not None and not v.cumple
    assert (servicio.FASE_ALIVIO, v) in b02.verificaciones()
    assert v in b02.incumplidas()
    assert dos_alivios_250.resumen().incumplidas >= 1
    assert not dos_alivios_250.cerrado
    # El primero no tiene extremo: no se evalua. REESCRITO (H2): antes lo
    # decia solo por `avisos()`; ahora es un BLOQUEO del punto que espera
    # `inicio_tramo_cuneta_km`, y cuenta para el cierre.
    assert b01.tramo_alivio.verificacion is None
    assert b01.tramo_alivio.falta == "inicio_tramo_cuneta_km"
    assert any(b.campo == "inicio_tramo_cuneta_km"
               and b.etapa == servicio.ETAPA_TRAMO_ALIVIO for b in b01.bloqueos)
    assert M10.AVISO_TRAMO_SIN_EXTREMO not in b01.avisos()


def test_A_y_C_no_tienen_tramo_ni_fase_10(dos_alivios_250):
    for id_punto in ("A-01", "A-02", "C-01"):
        p = _punto(dos_alivios_250, id_punto)
        assert p.tramo_alivio is None and p.espaciamiento is None


def test_VB1_llega_a_la_CLI_al_JSON_y_a_la_memoria(dos_alivios_250):
    texto = cli.volcar(dos_alivios_250)
    assert "VB1" in texto and "tramo de cuneta (VB1): 250.000 m desde B-01" in texto
    # REESCRITO (H2): el tramo sin extremo de B-01 sale como bloqueo, con el
    # dato que lo destraba, y no como «aviso:».
    assert f"aviso: {M10.AVISO_TRAMO_SIN_EXTREMO}" not in texto
    assert servicio.DETALLE_FALTA_EXTREMO_TRAMO in texto
    volcado = cli.informe_json(dos_alivios_250)
    b02 = next(p for p in volcado["puntos"] if p["id"] == "B-02")
    vb1 = next(v for v in b02["verificaciones"] if v["codigo"] == "VB1")
    assert vb1["cumple"] is False
    assert b02["tramo_alivio"]["longitud_m"] == pytest.approx(250.0, rel=REL_TRANSPORTE)
    assert b02["tramo_alivio"]["extremo"] == "B-01"
    b01 = next(p for p in volcado["puntos"] if p["id"] == "B-01")
    assert b01["tramo_alivio"]["evaluada"] is False
    assert b01["tramo_alivio"]["falta"] == "inicio_tramo_cuneta_km"
    html = M11.memoria_html(dos_alivios_250, proyecto="prueba T-9")
    assert "VB1" in html and "Tramo de cuneta que descarga en esta obra" in html
    # El bloqueo del tramo sin extremo de B-01 tambien llega a la memoria.
    assert "inicio_tramo_cuneta_km" in html


def test_con_el_inicio_declarado_el_primer_alivio_tambien_se_verifica(tmp_path):
    ruta = _csv_con(tmp_path, [("B-02", "2+600")])
    externos = _externos(tmp_path, {
        "globales": {"luz_m": 2.75, "L_hidraulico_m": 250.0},
        "puntos": {"B-01": {"inicio_tramo_cuneta_km": 2.27}}})
    informe = servicio.correr(ruta, externos, "perfil")
    b01, b02 = _punto(informe, "B-01"), _punto(informe, "B-02")
    assert b01.tramo_alivio.longitud_m == pytest.approx(180.0, rel=REL_TRANSPORTE)
    assert b01.tramo_alivio.verificacion.cumple
    assert b02.tramo_alivio.longitud_m == pytest.approx(150.0, rel=REL_TRANSPORTE)
    assert b02.tramo_alivio.verificacion.cumple


# La seccion de ARCHIVO (decision A): 0.40 x 1.20 m, Z2 = 1, concreto, S = 0.01.
#
#   Z1 = 1.20 / 0.40 = 3 ; A = (3 + 1) · 0.40² / 2 = 0.32 m2
#   P  = 0.40 · (√10 + √2) = 0.40 · (3.162278 + 1.414214) = 1.830596 m
#   Rh = 0.32 / 1.830596 = 0.174806 m ; Rh^(2/3) = 0.312635
#   Q_llena = 67 · 0.32 · 0.312635 · 0.1 = 0.670290 m3/s (V = 2.095 m/s < 4.50)
Q_ADM_ARCHIVO_S1 = 0.670290


def test_la_longitud_calculada_con_el_tramo_conocido_no_depende_de_area_ha(tmp_path):
    """
    REESCRITO DECLARANDOLO (H1 de la auditoria de T-9). Lo que este test
    fijaba en la FASE A: con el caudal declarado, q = Q / `area_ha` por el
    ancho tributario, de modo que B-01 daba L = 42 282 m (211 veces el
    recorrido normativo) y «duplicar `area_ha` duplica L». Ese era el SINTOMA
    del CUMPLE falso: 18 ha no es la faja de 12 m de un tramo de 200 m (seria
    0.24 ha), y con datos coherentes (b = A / s) la longitud por capacidad es
    Q_adm · s / Q y NO depende del area. Lo que fija ahora: con el tramo de
    B-01 conocido (A-02 lo cierra, decision C: s = 530 m) y el caudal
    declarado, el aporte se reparte en el tramo y

      q' = 0.095 / 530 = 1.792453e-4 m3/s por m
      L  = 0.670290 · 530 / 0.095 = 3739.5 m      (gobierna el normativo)

    y con el doble de area la longitud NO cambia. `area_ha` sigue teniendo
    consumidores (el contraste Q/A de T-1 y el reparto q · b sin tramo, que
    avisa la longitud implicita): ver tests/test_t9_correcciones.py.
    """
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"ancho_tributario_m": 12.0, "S_cuneta": 0.01}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    e = _punto(informe, "B-01").espaciamiento
    assert e.origen_L_hidraulico == "calculado"
    lh = e.longitud_hidraulica
    assert lh.metodo_aporte == METODO_APORTE_TRAMO
    assert lh.longitud_tramo_m == pytest.approx(530.0, rel=REL_ARITMETICA)
    assert lh.capacidad.Q_admisible_m3s == pytest.approx(Q_ADM_ARCHIVO_S1,
                                                         rel=REL_ARITMETICA)
    assert lh.q_por_metro_m3s_m == pytest.approx(1.792453e-4, rel=REL_ARITMETICA)
    assert lh.L_hidraulico == pytest.approx(3739.5, rel=REL_ARITMETICA)
    assert lh.escorrentia_m3s_km2 is None and lh.ancho_tributario_m is None
    assert e.espaciamiento_max == pytest.approx(200.0, rel=REL_TRANSPORTE)

    ruta = _csv_con(tmp_path, cambios={"B-01": {"area_ha": "36"}},
                    nombre="doble.csv")
    doble = servicio.correr(ruta, _externos(tmp_path, datos), "perfil")
    L2 = _punto(doble, "B-01").espaciamiento.longitud_hidraulica.L_hidraulico
    assert L2 == pytest.approx(lh.L_hidraulico, rel=REL_FORMULA)

    volcado = cli.informe_json(informe)
    b01 = next(p for p in volcado["puntos"] if p["id"] == "B-01")
    assert b01["espaciamiento_alivio"]["origen_L_hidraulico"] == "calculado"
    assert b01["espaciamiento_alivio"]["longitud_hidraulica"]["L_hidraulico_m"] \
        == pytest.approx(lh.L_hidraulico, rel=REL_TRANSPORTE)
    assert M11.traza_espaciamiento(_punto(informe, "B-01")) == e.pasos
    assert M11.traza_espaciamiento(_punto(informe, "A-01")) == ()
    html = M11.memoria_html(informe, proyecto="prueba T-9")
    assert M11.TITULO_TRAZA_ESPACIAMIENTO in html
    for que in ("Capacidad admisible de la cuneta",
                "Caudal aportante por metro de cuneta",
                "Longitud por capacidad de la cuneta"):
        assert que in html


def test_el_puente_con_la_hidrologia_no_recalcula_el_aporte_de_la_cuneta(tmp_path):
    """
    REESCRITO DECLARANDOLO (H11 de la auditoria de T-9). Lo que fijaba en la
    FASE A: la Fase 10 pedia a `MH.caudal_de_aporte_cuneta` el aporte sobre
    la MISMA cuenca y el MISMO TR que el caudal del punto --el mismo numero
    con otro rotulo-- y la memoria repetia los pasos de la Fase 1-bis. Lo que
    fija ahora: en la Familia B la Fase 1-bis calcula el caudal del punto con
    la puerta de la cuneta (es, por contrato, el de la cuneta que descarga en
    el alivio), UNA vez, y la Fase 10 lo reutiliza sin repetir sus pasos;
    con el caudal calculado, el aporte se reparte con q = Q / A por el ancho
    tributario (el camino de la FASE A). M10 no importa MH: el puente es el
    servicio.
    """
    ruta = _csv_con(tmp_path, cambios={"B-01": {"Q_m3s": ""}})
    hidrologia = servicio.cargar_hidrologia(HIDRO / "cuencas_prueba.csv",
                                            HIDRO / "estacion_prueba.csv")
    ca.establecer_valor_dinamico("homogeneidad_serie_fen", "serie_completa")
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"ancho_tributario_m": 12.0, "S_cuneta": 0.01}}}
    informe = servicio.correr(ruta, _externos(tmp_path, datos), "perfil",
                              hidrologia=hidrologia)
    b01 = _punto(informe, "B-01")
    lh = b01.espaciamiento.longitud_hidraulica
    aporte = lh.caudal_de_aporte
    assert aporte is b01.caudal                     # el MISMO objeto: no se recalcula
    assert lh.metodo_aporte == METODO_APORTE_AREA
    assert lh.escorrentia_m3s_km2 == pytest.approx(
        aporte.Q_m3s / aporte.area_km2, rel=REL_FORMULA)
    assert any(p.que == "Caudal de aporte a la cuneta por el metodo racional"
               for p in b01.caudal.pasos)
    assert not any(p.fundamento_id.startswith("FH.") for p in lh.pasos)
    assert "Fase 1-bis" in lh.origen_escorrentia
    assert b01.espaciamiento.L_hidraulico == pytest.approx(
        lh.capacidad.Q_admisible_m3s / (aporte.Q_m3s / aporte.area_km2
                                        * 12.0 / 1e6), rel=REL_FORMULA)


def test_sin_los_datos_de_la_cuneta_la_etapa_se_detiene_nombrandolos(tmp_path):
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"ancho_tributario_m": 12.0}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    b01 = _punto(informe, "B-01")
    bloqueo = next(b for b in b01.bloqueos if b.fase == servicio.FASE_ALIVIO)
    assert bloqueo.campo == "L_hidraulico_m"
    assert "S_cuneta" in bloqueo.mensaje
    assert "ancho_tributario_m" not in bloqueo.mensaje.split("faltan")[1]
    assert b01.espaciamiento is None


def test_sin_seccion_es_un_criterio_pendiente_de_la_etapa(tmp_path, monkeypatch):
    """
    REESCRITO (decision A): la seccion tiene valor de archivo; vaciada, la
    etapa de la capacidad se detiene en el pendiente declarable, sin caer.
    """
    monkeypatch.setitem(ca.CRITERIOS, "seccion_cuneta",
                        replace(ca.CRITERIOS["seccion_cuneta"], valor=None))
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"ancho_tributario_m": 12.0, "S_cuneta": 0.01}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    b01 = _punto(informe, "B-01")
    bloqueo = next(b for b in b01.bloqueos if b.fase == servicio.FASE_ALIVIO)
    assert bloqueo.criterio == "seccion_cuneta"
    assert bloqueo.etapa == servicio.ETAPA_CAPACIDAD_CUNETA
    assert "seccion_cuneta" in informe.contexto.criterios_usados


def test_el_prevuelo_dice_lo_que_falta_con_el_mismo_texto_del_bloqueo(tmp_path):
    datos = {"puntos": {"B-01": {"ancho_tributario_m": 12.0}}}
    ruta_json = tmp_path / "e.json"
    ruta_json.write_text(json.dumps(datos), encoding="utf-8")
    externos = servicio.cargar_datos_externos(ruta_json, {"luz_m": 2.75})
    estimado = anticipo.datos_faltantes_por_punto(CSV, externos, "perfil")
    entrada = next(e for e in estimado
                   if e.id_punto == "B-01" and e.dato == "L_hidraulico_m")
    assert entrada.detiene
    assert entrada.etapa == servicio.ETAPA_FALTA_L_HIDRAULICO
    assert servicio.detalle_falta_l_hidraulico(("S_cuneta",)) in entrada.de_donde
    # Con los dos datos de la cuneta ya no la anuncia como falta.
    datos["puntos"]["B-01"]["S_cuneta"] = 0.01
    ruta_json.write_text(json.dumps(datos), encoding="utf-8")
    externos = servicio.cargar_datos_externos(ruta_json, {"luz_m": 2.75})
    estimado = anticipo.datos_faltantes_por_punto(CSV, externos, "perfil")
    assert not [e for e in estimado
                if e.id_punto == "B-01" and e.dato == "L_hidraulico_m"]


@pytest.mark.parametrize("clave,valor,motivo", [
    ("S_cuneta", 1.5, "rango fisico"), ("S_cuneta", 0.0, "positivo"),
    ("ancho_tributario_m", -3.0, "positivo"),
    ("inicio_tramo_cuneta_km", -0.1, "positivo")])
def test_la_carga_rechaza_un_dato_de_la_cuneta_no_fisico(tmp_path, clave, valor,
                                                         motivo):
    """
    Se mide el MOTIVO y no solo la excepcion (leccion de T-8): en la base la
    clave era DESCONOCIDA y la carga la rechazaba igual, de modo que con solo
    `raises` el test pasaba vacuo antes de T-9.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        _externos(tmp_path, {"puntos": {"B-01": {clave: valor}}})
    assert exc.value.campo == clave
    assert motivo in str(exc.value)


def test_el_inicio_del_tramo_admite_el_cero_del_eje(tmp_path):
    externos = _externos(tmp_path, {"puntos": {"B-01": {
        "inicio_tramo_cuneta_km": 0}}})
    assert externos.valor("B-01", "inicio_tramo_cuneta_km") == pytest.approx(
        0.0, abs=ABS_CERO)


def test_las_tres_claves_nuevas_son_de_la_familia_B_y_su_regla_de_prevuelo():
    """
    REESCRITO (H2): `inicio_tramo_cuneta_km` sale de EXTERNOS_CON_VIA_ALTERNA
    -- un alivio sin extremo es un bloqueo que espera ese dato y el pre-vuelo
    tiene regla propia para el --; las otras dos siguen con via alterna (la
    longitud declarada).
    """
    for clave in ("ancho_tributario_m", "S_cuneta", "inicio_tramo_cuneta_km"):
        assert clave in servicio.CLAVES_EXTERNAS
        assert servicio.familias_que_usan(clave) == (Familia.B,)
    for clave in ("ancho_tributario_m", "S_cuneta"):
        assert clave in servicio.EXTERNOS_CON_VIA_ALTERNA
    assert "inicio_tramo_cuneta_km" not in servicio.EXTERNOS_CON_VIA_ALTERNA


def test_la_aceptacion_de_la_familia_B_lleva_VB1_y_VB2():
    """REESCRITO (H1): la condicion literal del Manual entra como VB2."""
    assert PERFILES[Familia.B].verificaciones_aceptacion == (
        "V1", "V2", "V4", "V5", CODIGO_VB1, "VB2")


def test_M10_no_importa_la_hidrologia():
    """
    Guardia que vale ANTES y DESPUES de T-9 (medido contra df1b23c): el
    puente con la hidrologia es el servicio, no M10.
    """
    import ast
    arbol = ast.parse((RAIZ / "src" / "modulos" / "M10_espaciamiento.py")
                      .read_text(encoding="utf-8"))
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ImportFrom):
            nombres.add(nodo.module or "")
            nombres.update(a.name for a in nodo.names)
        elif isinstance(nodo, ast.Import):
            nombres.update(a.name for a in nodo.names)
    assert not any("MH_hidrologia" in n for n in nombres)


def test_la_corrida_de_perfil_que_calcula_la_longitud_invoca_los_tres_criterios(tmp_path):
    """
    El NIVEL medido: los tres criterios de la cuneta son de perfil, y una
    corrida `--alcance perfil` que calcula L_hidraulico los invoca sin
    diferir su etapa (la Fase 10 no esta en MODULOS_DIFERIDOS_POR_ALCANCE).
    """
    assert "M10_espaciamiento" not in servicio.MODULOS_DIFERIDOS_POR_ALCANCE[
        servicio.ALCANCE_PERFIL]
    # REESCRITO (decision A): la seccion de archivo, sin declararla. Y desde
    # la decision C, la corrida invoca tambien el criterio de las obras A.
    datos = {"globales": {"luz_m": 2.75},
             "puntos": {"B-01": {"ancho_tributario_m": 12.0, "S_cuneta": 0.01}}}
    informe = servicio.correr(CSV, _externos(tmp_path, datos), "perfil")
    usados = set(informe.contexto.criterios_usados)
    for clave in CRITERIOS_DE_LA_CUNETA + ("long_max_cuneta",
                                           "obras_familia_a_extremo_de_cuneta"):
        assert clave in usados, clave
        assert ca.CRITERIOS[clave].nivel == ca.NIVEL_PERFIL


def test_el_comparador_de_E_B_ve_el_tramo_y_el_veredicto_de_VB1(tmp_path):
    """Dos corridas que solo difieren en la progresiva de B-02: 150 m y 250 m."""
    from src import comparador
    externos = {"globales": {"luz_m": 2.75, "L_hidraulico_m": 250.0}}
    corto = servicio.correr(_csv_con(tmp_path, [("B-02", "2+600")],
                                     nombre="corto.csv"),
                            _externos(tmp_path, externos), "perfil")
    largo = servicio.correr(_csv_con(tmp_path, [("B-02", "2+700")],
                                     nombre="largo.csv"),
                            _externos(tmp_path, externos), "perfil")
    r = comparador.comparar(cli.informe_json(corto), cli.informe_json(largo))
    en_b02 = [d for d in r.diferencias if d.donde == "B-02"]
    assert any(d.campo.startswith("tramo_alivio") for d in en_b02), en_b02
    assert any("VB1" in d.campo for d in en_b02), en_b02
