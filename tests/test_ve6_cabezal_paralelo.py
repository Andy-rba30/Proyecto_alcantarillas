"""
tests/test_ve6_cabezal_paralelo.py
==================================
VE-6 (integrador), ficha T7A-03: EL CABEZAL PARALELO A LA VIA EN UN MARCO.

Lo que la ficha dejo abierto y la decision del dueño (2026-11-13) acoto: el
cabezal NORMAL al eje sigue siendo el de archivo en las tres familias, y el
PARALELO a la via es la alternativa SOLO para el marco, con las filas de la
Carta 11 del HDS-5 («skewed headwall», sin aletas), hasta hoy sin banda.

Rojo medido contra la base (sin los cambios de `src/` de este item): los
doce tests fallan. Los oraculos:

  * las bandas de esviaje, leidas a mano del ROTULO literal de cada fila de
    la Carta 11 (`normativa/tablas.py::T_HDS5_A1`), no de la constante nueva;
  * la longitud del muro, con la aritmetica escrita (B/cos theta + 2·emp);
  * la carga de entrada del marco con la fila de la Carta 11, con la Forma 2
    no sumergida escrita en el test (HW/D = K·(Ku·Q/(A·D^0.5))^M, HDS-5 ec.
    A.2), con K y M copiados del rotulo de la tabla.
"""

import math
from pathlib import Path

import pytest

import cli
from src import servicio
from src.constantes_normativas import (CAJON_C2_SIN_ALETAS, KU_SI,
                                       Q_LIM_NO_SUMERGIDO)
from src.modelos import (DatoInvalidoError, ExtremoDelConducto, Familia)
from src.modulos import M6_proteccion as M6
from src.modulos import M9_cabezal as M9
from src.normativa import tablas
from tests.apoyo.criterios import declarados
from tests.test_canal_discrepancias import DECLARACIONES_DEL_CAJON

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_AMPLIADOS = RAIZ / "tests" / "linea_base_familia_c" / \
    "entradas_ampliadas.json"
FILA_C01 = "C-01,3+100,C,,,,36.90,39.10,38.95,6.5,30,9.60,36.20,,,ML,,,"
REL = 1e-9

CARTA_11_30 = "cajon_concreto_chaflan_esviaje_30"
PARALELO = {"embocadura_cajon": CARTA_11_30,
            "ke_entrada_cajon": "cajon_sin_aletas_escuadra_3"}


def _fila_ta1(clave):
    tabla = tablas.TABLAS["HDS5_3ED.TA1"]
    return next(f for f in tabla.filas
                if f.id == f"HDS5_3ED.TA1#{clave}")


@pytest.fixture
def csv_c01(tmp_path):
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    assert FILA_C01 + "\n" in texto
    ruta = tmp_path / "puntos_c01.csv"
    ruta.write_text(texto.replace(FILA_C01 + "\n", f"{FILA_C01}38.30\n"),
                    encoding="utf-8")
    return ruta


def _externos():
    return cli.cargar_datos_externos(EXTERNOS_AMPLIADOS, {"luz_m": 2.75})


# ===========================================================================
# 1. La embocadura y las filas
# ===========================================================================

def test_los_rotulos_de_la_carta_11_dicen_cabezal_esviado_sin_aletas():
    """Las cuatro filas de la Carta 11 transcritas: «skewed headwall», sin
    la palabra wingwall. El angulo de esviaje se lee del rotulo."""
    for clave, esperado in (("cajon_concreto_chaflan_esviaje_45", (45, 45)),
                            ("cajon_concreto_chaflan_esviaje_30", (30, 30)),
                            ("cajon_concreto_chaflan_esviaje_15", (15, 15)),
                            ("cajon_concreto_bisel_45_esviaje_10_45",
                             (10, 45))):
        fila = _fila_ta1(clave)
        assert fila.valores["chart_no"] == 11
        rotulo = fila.etiqueta_literal
        assert "skewed headw" in rotulo and "wingwall" not in rotulo
        if esperado[0] == esperado[1]:
            assert f"{esperado[0]}° skewed" in rotulo
        else:
            assert f"{esperado[0]}°-{esperado[1]}° skewed" in rotulo
        banda = M9.BANDAS_ESVIAJE_CABEZAL_CAJON_A1[clave]
        assert banda == ((float(esperado[0]), float(esperado[1])),)


def test_el_marco_con_fila_de_la_carta_11_lleva_cabezal_paralelo():
    with declarados(PARALELO):
        e = M9.embocadura_del_punto(esviaje_grados=30.0, familia=Familia.C,
                                    id_punto="C-01")
        tubo = M9.embocadura_del_punto(esviaje_grados=30.0,
                                       familia=Familia.A, id_punto="A-01")
    assert e.orientacion == M9.ORIENTACION_PARALELO_A_LA_VIA
    assert e.angulo_aletas is None and e.tipo == M6.EMBOCADURA_CABEZAL_RECTO
    assert "Carta 11" in e.regla
    # los tubos siguen con el criterio y el muro normal al eje
    assert tubo.orientacion == M9.ORIENTACION_NORMAL_AL_EJE
    # con aleros en 'embocadura_cabezal' (archivo) el marco lo avisa
    assert any("SIN aleros" in a for a in e.avisos)


def test_sin_carta_11_el_marco_sigue_normal_al_eje():
    with declarados(DECLARACIONES_DEL_CAJON):
        e = M9.embocadura_del_punto(esviaje_grados=30.0, familia=Familia.C,
                                    id_punto="C-01")
    assert e.orientacion == M9.ORIENTACION_NORMAL_AL_EJE
    assert e.angulo_aletas is not None


@pytest.mark.parametrize("theta, esperadas", [
    (30.0, {"cajon_concreto_chaflan_esviaje_30",
            "cajon_concreto_bisel_45_esviaje_10_45"}),
    (20.0, {"cajon_concreto_bisel_45_esviaje_10_45"}),
    (45.0, {"cajon_concreto_chaflan_esviaje_45",
            "cajon_concreto_bisel_45_esviaje_10_45"}),
    (5.0, set()),
    (50.0, set()),
])
def test_las_filas_del_cabezal_paralelo_son_las_del_esviaje(theta, esperadas):
    with declarados({"embocadura_cajon":
                     "cajon_concreto_bisel_45_esviaje_10_45"}):
        e = M9.embocadura_del_punto(esviaje_grados=theta, familia=Familia.C)
    a1, c2 = M9.filas_hds5_del_cajon(e)
    assert set(a1) == esperadas
    assert c2 == CAJON_C2_SIN_ALETAS


def test_la_coherencia_pide_el_ke_del_cabezal_paralelo_al_terraplen():
    with declarados({"embocadura_cajon": CARTA_11_30,
                     "ke_entrada_cajon": "cajon_aletas_30_75_escuadra"}):
        e = M9.embocadura_del_punto(esviaje_grados=30.0, familia=Familia.C)
        with pytest.raises(DatoInvalidoError) as exc:
            M9.verificar_coherencia_embocadura_cajon(e, id_punto="C-01")
    assert "cajon_sin_aletas_escuadra_3" in str(exc.value)
    with declarados(PARALELO):
        e = M9.embocadura_del_punto(esviaje_grados=30.0, familia=Familia.C)
        assert "paralelo a la via" in \
            M9.verificar_coherencia_embocadura_cajon(e, id_punto="C-01")
    # con un esviaje que la fila no nombra, la coherencia se detiene
    with declarados(PARALELO):
        e = M9.embocadura_del_punto(esviaje_grados=20.0, familia=Familia.C)
        with pytest.raises(DatoInvalidoError):
            M9.verificar_coherencia_embocadura_cajon(e, id_punto="C-01")


def test_varias_celdas_con_cabezal_paralelo_se_avisa():
    with declarados(dict(PARALELO, n_celdas_cajon=2)):
        e = M9.embocadura_del_punto(esviaje_grados=30.0, familia=Familia.C)
    assert any("5.4.2" in a and "celdas" in a for a in e.avisos)


# ===========================================================================
# 2. La geometria del cabezal paralelo
# ===========================================================================

def test_el_muro_paralelo_contiene_la_boca_cortada_en_oblicuo():
    with declarados(PARALELO):
        e = M9.embocadura_del_punto(esviaje_grados=30.0, familia=Familia.C)
    extremo = ExtremoDelConducto(
        extremo="entrada", cota_solera=100.0, cota_pie=100.0,
        origen_cota_pie="caso", cota_clave_exterior=101.10, cota_agua=100.8,
        origen_cota_agua="caso", ancho_exterior=1.60, altura_interior=0.90)
    g = M9.predimensionar_cabezal(extremo=extremo, embocadura=e, talud=2.0)
    emp = M9._reglas()["empotramiento_lateral_m"]
    assert g.longitud == pytest.approx(
        1.60 / math.cos(math.radians(30.0)) + 2 * emp, rel=REL)
    assert g.aleros is None
    cb1 = next(v for v in M9.verificar_compatibilidad_cabezal(
        geometria=g, extremo=extremo, embocadura=e) if v.codigo == "CB1.e")
    assert cb1.cumple
    assert cb1.valor_admisible == pytest.approx(
        1.60 / math.cos(math.radians(30.0)), rel=REL)


# ===========================================================================
# 3. El pipeline: C-01 con la Carta 11
# ===========================================================================

def test_c01_con_cabezal_paralelo_calcula_con_la_carta_11(csv_c01):
    externos = _externos()
    with declarados(DECLARACIONES_DEL_CAJON):
        with declarados(PARALELO):
            informe = cli.correr(csv_c01, externos,
                                 alcance=cli.ALCANCE_PERFIL)
            c01 = informe.puntos[3]
            assert c01.dimensionado, [b.mensaje for b in c01.bloqueos]
            assert c01.embocadura.orientacion == \
                M9.ORIENTACION_PARALELO_A_LA_VIA
            r = c01.resultado
            h = r.resultado_hidraulico
            # la Forma 2 no sumergida, escrita: K y M del rotulo
            fila = _fila_ta1(CARTA_11_30).valores
            assert fila["equation_form"] == 2
            B, D = r.seccion.B, r.seccion.H
            q = KU_SI * h.Q_celda_m3s / (B * D * D ** 0.5)
            assert q < Q_LIM_NO_SUMERGIDO
            assert h.HW_entrada == pytest.approx(
                D * fila["K"] * q ** fila["M"], rel=1e-6)
            # la Fase 9: muro paralelo, sin aleros, sin el aviso de Δz
            servicio._fase_9(c01, externos)
            cab = c01.cabezal
            assert cab is not None, [b.mensaje for b in c01.bloqueos]
    assert cab.entrada.aleros is None and cab.salida.aleros is None
    emp = M9._reglas()["empotramiento_lateral_m"]
    # ancho exterior del marco 1.20 x 0.90 con pared de 0.20 m: 1.60 m
    for g in (cab.entrada, cab.salida):
        assert g.longitud == pytest.approx(
            1.60 / math.cos(math.radians(30.0)) + 2 * emp, rel=REL)
    assert not any("Δz" in a for a in cab.avisos)
    assert all(v.cumple for v in cab.verificaciones
               if v.codigo and v.codigo.startswith("CB1"))
