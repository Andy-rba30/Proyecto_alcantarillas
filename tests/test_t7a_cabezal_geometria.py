"""
tests/test_t7a_cabezal_geometria.py
===================================
Aceptacion de T-7a de la cadena T: el cabezal POR PUNTO y sus aleros
(INF-4.1, INF-4.2, INF-4.3 e INF-5.1.15 --el «INF-5.1.12» del prompt--).

Los oraculos son la ARITMETICA ESCRITA, calculada a mano en cada test con
los numeros del caso y no con la formula cerrada del codigo: la coronacion,
el desplante, la zapata, la longitud de los aleros (con el COSENO del angulo
con el eje, la discrepancia declarada contra el «sen» del encargo) y la
longitud entre cabezales.

NO SE ESCRIBIO EN ROJO PRIMERO, y se dice en vez de reconstruirlo: el codigo
se escribio antes que este archivo. El rojo se MIDIO contra `df1b23c` (la
base de la rama) copiando este archivo a un checkout de esa base: ver el
informe de FASE A de T-7a.

LAS CORRECCIONES DE LA AUDITORIA ADVERSARIAL (2026-11-13) REESCRIBIERON
ONCE TESTS DE ESTE ARCHIVO, y se dice cuales y por que en cada uno (busque
«correcciones de T-7a»): el piso de la zapata armada (0.225 -> 0.37 m), los
dos aleros con esviaje, el dentellon desde el terreno y bajo la hoya con
margen, CB6 y CB7, el origen «derivada», la longitud entre cabezales al
relleno retenido y E.050 como [N→]. Lo nuevo de las correcciones esta en
`tests/test_t7a_correcciones.py`.

Lo que el archivo fija, por bloques:

  1. Las fichas: 'angulo_aletas' y 'predimensionamiento_cabezal' tienen
     valor (regla [A] con ventana por campo); 'embocadura_cabezal' [A] de
     perfil; el margen bajo la socavacion [C] es 2.0 ft exactos; el
     dentellon [N->] es el de la Lamina Nº 04; el 0.80 m de E.050 y el 0.30
     m de E.060 son criterios [N->] con su cita (el segundo desde el cierre
     de T-7c; antes, constante [N]).
  2. La embocadura del punto y la COHERENCIA con el marco: cambiar el angulo
     o el tipo de embocadura no deja intactos ke ni la carta donde la fuente
     distingue (el marco); donde no distingue (el tubo), nada se mueve.
  3. El predimensionamiento de UN cabezal, con su aritmetica escrita.
  4. Las verificaciones CB1-CB5 y las dimensiones declaradas.
  5. La longitud entre cabezales (ficha T6-01).
  6. El pipeline: perfil (embocadura, Fase 9 diferida, ningun diametro
     movido), la Fase 9 del punto sobre el fixture, la memoria, el JSON y la
     CLI; y la puerta del dato externo `cabezal_declarado`.
"""

import math
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import servicio
from src import constantes_normativas as cn_t7a
from src.constantes_fisicas import PIE_EN_METROS
from src.constantes_normativas import (BANDAS_ALETAS_CAJON_A1,
                                       BANDAS_ALETAS_CAJON_C2,
                                       CAJON_A1_SIN_ALETAS,
                                       CAJON_C2_SIN_ALETAS,
                                       CARTAS_CAJON_TA1,
                                       KE_CAJON_C2, KE_HDS5_C2,
                                       NUMERAL_ZAPATA_CONCRETO_SIMPLE)
from src.modelos import (ORIGEN_DIMENSION_DECLARADA, ORIGEN_DIMENSION_REGLA,
                         ORIGEN_DIMENSION_DERIVADA,
                         CabezalDelPunto, DatoFaltanteError,
                         DatoInvalidoError, EmbocaduraDelPunto,
                         ExtremoDelConducto, GeometriaCabezal,
                         LimiteNumericoError, MetodoLongitud)
from src.modulos import M6_proteccion as M6
from src.modulos import M9_cabezal as M9
from src.modulos import M11_reporte as M11
from src.normativa.registro import construir
from tests.apoyo.aproximacion import ABS_CERO
from tests.apoyo.criterios import declarados, sin_valor
from tests.test_canal_discrepancias import DECLARACIONES_DEL_CAJON

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_AMPLIADOS = RAIZ / "tests" / "linea_base_familia_c" / \
    "entradas_ampliadas.json"
LUZ = 2.75
REL = 1e-9          # aritmetica escrita contra el calculo: solo redondeo
# Un cambio de carga que tiene que VERSE (ke 0.4 -> 0.5 mueve el HW en cm),
# y la diferencia entre el coseno y el seno a 30 grados (73 %): dos
# tolerancias de "distinto", no de "igual".
REL_CAMBIO_APRECIABLE = 1e-6
REL_OTRA_FORMULA = 1e-3
FILA_C01 = "C-01,3+100,C,,,,36.90,39.10,38.95,6.5,30,9.60,36.20,,,ML,,,"
CORONACION_CANAL_C01 = 38.30


# ===========================================================================
# Apoyos
# ===========================================================================

def _extremo(**cambios) -> ExtremoDelConducto:
    """Un extremo de ENTRADA de un tubo de 0.90 m con pared de 0.10 m."""
    base = dict(extremo="entrada", cota_solera=100.00, cota_pie=100.00,
                origen_cota_pie="caso de prueba",
                cota_clave_exterior=101.00, cota_agua=101.10,
                origen_cota_agua="caso de prueba", ancho_exterior=1.10,
                altura_interior=0.90)
    base.update(cambios)
    return ExtremoDelConducto(**base)


def _embocadura(angulo=45.0, tipo=M6.EMBOCADURA_CABEZAL_CON_ALEROS,
                esviaje=15.0) -> EmbocaduraDelPunto:
    return EmbocaduraDelPunto(
        tipo=tipo, angulo_aletas=angulo, regla="caso de prueba",
        esviaje_grados=esviaje, criterio_tipo="embocadura_cabezal",
        criterio_angulo="angulo_aletas" if angulo is not None else "")


def _dim(geometria, nombre):
    return next(d for d in geometria.dimensiones if d.nombre == nombre)


@pytest.fixture
def csv_c01(tmp_path):
    """El CSV de ejemplo con la coronacion del canal en C-01 (como PF-4)."""
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    assert FILA_C01 + "\n" in texto
    ruta = tmp_path / "puntos_c01.csv"
    ruta.write_text(texto.replace(FILA_C01 + "\n",
                                  f"{FILA_C01}{CORONACION_CANAL_C01}\n"),
                    encoding="utf-8")
    return ruta


def _externos():
    return cli.cargar_datos_externos(EXTERNOS_AMPLIADOS, {"luz_m": LUZ})


@pytest.fixture(scope="module")
def corrida_perfil():
    """La corrida de perfil del fixture con TW = 0.30 m: A-01, A-02 y B-01
    dimensionan en tubo de 0.90 m."""
    externos = cli.cargar_datos_externos(None, {"luz_m": LUZ, "TW_m": 0.3})
    return cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL), \
        externos


@pytest.fixture(scope="module")
def a01_con_cabezal(corrida_perfil):
    """
    A-01 de la corrida de perfil con su Fase 9 corrida por la MISMA etapa del
    servicio que la corrida de expediente usa (`servicio._fase_9`). A
    expediente ningun punto del fixture dimensiona, y no por una sola
    razon: V5 se detiene en el criterio vacio 'remanso_derecho_via', con el
    criterio declarado se detiene en `ancho_derecho_via_m` SIN leerlo
    (`M5.v5_remanso` no tiene metodo), y aunque V5 cumpliera, V8 se
    detiene en 'TR_evento_extremo' (ficha T7A-01, reescrita en las
    correcciones de T-7a). Esta es la via honesta de ejercitarla sobre un
    punto real.
    """
    informe, externos = corrida_perfil
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    assert a01.dimensionado
    servicio._fase_9(a01, externos)
    assert a01.cabezal is not None, [b.mensaje for b in a01.bloqueos]
    return a01


# ===========================================================================
# 1 - Las fichas y las constantes
# ===========================================================================

def test_angulo_aletas_es_una_regla_de_perfil_con_ventana_por_campo():
    c = ca.CRITERIOS["angulo_aletas"]
    assert c.valor == pytest.approx({"por_defecto_grados": 45.0,
                                     "umbral_esviaje_grados": 30.0,
                                     "con_esviaje_mayor_grados": 30.0}, rel=REL)
    assert c.nivel == ca.NIVEL_PERFIL and c.etiqueta == "A"
    for campo in ("por_defecto_grados", "con_esviaje_mayor_grados"):
        lo, hi = c.sensibilidad[campo]
        # la «ventana completa» {30, 45, 60} del encargo cabe entera, y
        # dentro de la banda de 30-75 grados de la Tabla C.2
        assert (lo, hi) == pytest.approx((30.0, 60.0), rel=REL)
    assert not c.sin_consumidor
    # la rama «60 grados en caja receptora» del encargo NO se adopta, y la
    # ficha dice por que (la Lamina 02-A dibuja la caja receptora sin aleros)
    assert "caja receptora" in c.justificacion.lower()


def test_embocadura_cabezal_es_una_categoria_de_perfil_con_aleros():
    c = ca.CRITERIOS["embocadura_cabezal"]
    assert c.valor == M6.EMBOCADURA_CABEZAL_CON_ALEROS
    assert c.sensibilidad == (M6.EMBOCADURA_CABEZAL_CON_ALEROS,
                              M6.EMBOCADURA_CABEZAL_RECTO)
    assert c.nivel == ca.NIVEL_PERFIL and c.forma == ca.FORMA_CATEGORIA
    assert set(c.sensibilidad) <= set(M6.EMBOCADURAS)


def test_predimensionamiento_cabezal_deja_de_ser_un_vacio():
    c = ca.CRITERIOS["predimensionamiento_cabezal"]
    assert c.valor is not None
    assert c.nivel == ca.NIVEL_EXPEDIENTE and c.etiqueta == "A"
    s = c.sensibilidad
    # las ventanas del encargo, una por una
    assert s["espesor_pantalla_voladizo_m"] == pytest.approx((0.20, 0.30), rel=REL)
    assert s["divisor_espesor_gravedad"] == pytest.approx((6.0, 8.0), rel=REL)        # H/8 - H/6
    assert s["fraccion_ancho_zapata"] == pytest.approx((0.40, 0.70), rel=REL)         # 0.4 - 0.7 H
    assert s["divisor_peralte_zapata"] == pytest.approx((10.0, 12.0), rel=REL)        # H/12 - H/10
    assert s["altura_final_aleros_m"] == pytest.approx((0.30, 0.50), rel=REL)
    assert s["fraccion_longitud_losa"] == pytest.approx((1.0, 1.5), rel=REL)
    assert s["espesor_losa_m"] == pytest.approx((0.20, 0.30), rel=REL)
    for campo, (lo, hi) in s.items():
        assert lo <= c.valor[campo] <= hi, campo
    assert "predimensionamiento_cabezal" not in ca.criterios_sin_valor()
    assert "angulo_aletas" not in ca.criterios_sin_valor()


def test_el_margen_bajo_la_socavacion_son_dos_pies_exactos():
    c = ca.CRITERIOS["margen_zapata_bajo_socavacion_m"]
    assert c.etiqueta == "C" and c.nivel == ca.NIVEL_EXPEDIENTE
    assert c.valor == pytest.approx(2.0 * PIE_EN_METROS, rel=REL)
    assert "12.6.5" in c.fuente


def test_el_dentellon_es_el_de_la_lamina_04_por_analogia():
    c = ca.CRITERIOS["dentellon_losa_entrega"]
    assert c.etiqueta == "N->"
    assert c.valor == pytest.approx({"profundidad_min_m": 0.80,
                                     "ancho_m": 0.40}, rel=REL)
    assert "analogia" in c.justificacion.lower()


def test_los_minimos_con_numero_llevan_su_cita_y_su_etiqueta():
    """
    Correcciones de T-7a (H8): el 0.80 m de E.050 26.2 DEJA de ser [N] en
    `constantes_normativas` y pasa a criterio [N→] con la analogia declarada
    (el ambito de E.050 son las edificaciones).

    REESCRITO DECLARANDOLO (cierre de T-7c, pregunta 1 de su FASE A): el
    0.30 m de E.060 22.7.4 seguia como constante [N]
    (`ESPESOR_MIN_ZAPATA_CONCRETO_SIMPLE_M`), y este test lo fijaba asi.
    Pasa al criterio [N→] 'espesor_min_zapata_concreto_simple_m', por la
    misma razon que E.050 26.2 y E.060 15.7: la excepcion de la §0.2 que
    hace regir E.060 en el cabezal cubre solo la durabilidad.
    """
    c = ca.CRITERIOS["profundidad_cimentacion_min_cabezal_m"]
    assert c.etiqueta == "N->" and c.valor == pytest.approx(0.80, rel=REL)
    assert "analogia" in c.justificacion.lower()
    z = ca.CRITERIOS["espesor_min_zapata_concreto_simple_m"]
    assert z.etiqueta == "N->" and z.valor == pytest.approx(0.30, rel=REL)
    assert "22.7.4" in z.fuente and "analogia" in z.fuente.lower()
    assert not hasattr(cn_t7a, "ESPESOR_MIN_ZAPATA_CONCRETO_SIMPLE_M")
    assert "22.7.4" in NUMERAL_ZAPATA_CONCRETO_SIMPLE


@pytest.mark.parametrize("cita_id, frase", [
    ("E050.26.2#PROFUNDIDAD", "0,80 metros"),
    ("AASHTO_LRFD_9.12.6.5#ZAPATAS", "not less than 2.0 ft below"),
    ("AASHTO_LRFD_9.12.6.5#DENTELLON", "cut-off wall"),
    ("AASHTO_LRFD_9.12.6.5#ALEROS", "wingwalls shall be extended"),
    ("AASHTO_LRFD_9.10.6.1.2#DESPLANTE", "bear below the maximum"),
    ("E060.22.7.4#ZAPATA", "300 mm"),
    ("MC_HHD.LAMINA_02A", "SIN  ALEROS"),
    ("MC_HHD.LAMINA_04#DENTELLON", "0.80 min."),
])
def test_las_citas_nuevas_estan_en_el_registro_con_su_frase(cita_id, frase):
    c = construir().cita(cita_id)
    assert frase in c.texto_literal.texto
    assert c.verificado is not None


def test_las_bandas_de_aletas_cubren_exactamente_las_filas_de_cajon():
    """Ni una fila de cajon sin banda, ni una banda sin fila."""
    assert set(BANDAS_ALETAS_CAJON_A1) == set(CARTAS_CAJON_TA1)
    assert set(BANDAS_ALETAS_CAJON_C2) == set(KE_CAJON_C2)
    assert CAJON_A1_SIN_ALETAS <= set(CARTAS_CAJON_TA1)
    assert CAJON_C2_SIN_ALETAS <= set(KE_CAJON_C2)
    # la banda de cada fila de la Tabla C.2 es la de su ROTULO
    for clave, bandas in BANDAS_ALETAS_CAJON_C2.items():
        agrupacion = KE_HDS5_C2[clave]["agrupacion"]
        if "no wingwalls" in agrupacion:
            assert bandas == ()
        elif "30" in agrupacion and "75" in agrupacion:
            assert bandas[0] == pytest.approx((30.0, 75.0), rel=REL)
        elif "10" in agrupacion and "25" in agrupacion:
            assert bandas[0] == pytest.approx((10.0, 25.0), rel=REL)
        else:
            assert "parallel" in agrupacion
            assert bandas[0] == pytest.approx((0.0, 0.0), abs=ABS_CERO)


# ===========================================================================
# 2 - La embocadura del punto y la coherencia con el marco
# ===========================================================================

@pytest.mark.parametrize("esviaje, esperado", [
    (0.0, 45.0), (15.0, 45.0), (30.0, 45.0),      # 30 no SUPERA el umbral
    (30.5, 30.0), (45.0, 30.0)])
def test_la_regla_del_angulo_de_los_aleros(esviaje, esperado):
    e = M9.embocadura_del_punto(esviaje_grados=esviaje)
    assert e.tipo == M6.EMBOCADURA_CABEZAL_CON_ALEROS
    assert e.angulo_aletas == pytest.approx(esperado, rel=REL)


def test_con_cabezal_recto_no_hay_angulo():
    with declarados({"embocadura_cabezal": M6.EMBOCADURA_CABEZAL_RECTO}):
        e = M9.embocadura_del_punto(esviaje_grados=15.0)
    assert e.angulo_aletas is None and e.criterio_angulo == ""


@pytest.mark.parametrize("malo", [float("nan"), -1.0, float("inf"), "15", True])
def test_un_esviaje_que_no_es_un_angulo_se_rechaza(malo):
    with pytest.raises(DatoInvalidoError):
        M9.embocadura_del_punto(esviaje_grados=malo)


def test_las_filas_del_marco_dependen_del_angulo_donde_la_fuente_distingue():
    """
    La Tabla C.2 del HDS-5 agrupa el cajon por bandas del angulo con el
    barril: a 45 grados, la fila «Square-edged at crown» de 30-75 (ke 0.4);
    a 20 grados, la de 10-25 (ke 0.5); sin aleros, la de «no wingwalls»
    (ke 0.5). El mapeo es de la fuente: se prueba tambien fuera de la
    ventana del criterio.
    """
    a1_45, c2_45 = M9.filas_hds5_del_cajon(_embocadura(45.0))
    assert c2_45 == {"cajon_aletas_30_75_escuadra",
                     "cajon_aletas_30_75_redondeado"}
    assert {"cajon_concreto_aletas_30_75", "cajon_concreto_aleta_45_d043",
            "cajon_concreto_chaflan_aletas_45",
            "cajon_concreto_bisel_superior_aletas_45_desplazadas"} == a1_45
    _, c2_20 = M9.filas_hds5_del_cajon(_embocadura(20.0))
    assert c2_20 == {"cajon_aletas_10_25_escuadra"}
    a1_30, _ = M9.filas_hds5_del_cajon(_embocadura(30.0))
    assert "cajon_concreto_aleta_18_337_d083" in a1_30
    assert "cajon_concreto_aleta_45_d043" not in a1_30
    a1_r, c2_r = M9.filas_hds5_del_cajon(_embocadura(None))
    assert a1_r == CAJON_A1_SIN_ALETAS and c2_r == CAJON_C2_SIN_ALETAS
    # y el ke de cada banda, el de la tabla: 0.4 / 0.5 / 0.5
    assert KE_HDS5_C2["cajon_aletas_30_75_escuadra"]["ke"] == pytest.approx(0.4, rel=REL)
    assert KE_HDS5_C2["cajon_aletas_10_25_escuadra"]["ke"] == pytest.approx(0.5, rel=REL)
    assert KE_HDS5_C2["cajon_sin_aletas_escuadra_3"]["ke"] == pytest.approx(0.5, rel=REL)


def test_la_coherencia_del_marco_solo_mira_lo_declarado():
    """
    Sin los criterios del cajon declarados no rellena ni deduce nada.
    REESCRITO al integrar detras de T-3: desde T-3 'embocadura_cajon' y
    'ke_entrada_cajon' TIENEN valor de archivo (la escala 1 de la Carta 8 y la
    fila de 30 a 75 grados a escuadra, ke 0.4), de modo que el vacio se
    prueba con `sin_valor`; y con los valores de archivo la coherencia se
    cumple para todo alfa de la ventana de 'angulo_aletas' (30 a 60 grados).
    """
    with sin_valor("embocadura_cajon"), sin_valor("ke_entrada_cajon"):
        assert M9.verificar_coherencia_embocadura_cajon(_embocadura(45.0)) is None
    for alfa in (30.0, 45.0, 60.0):
        nota = M9.verificar_coherencia_embocadura_cajon(_embocadura(alfa))
        assert "cajon_concreto_aletas_30_75" in nota
        assert "cajon_aletas_30_75_escuadra" in nota


def test_cambiar_el_tipo_de_embocadura_no_deja_el_ke_del_marco_intacto():
    with declarados({"embocadura_cajon": "cajon_concreto_aletas_30_75",
                     "ke_entrada_cajon": "cajon_aletas_30_75_escuadra"}):
        nota = M9.verificar_coherencia_embocadura_cajon(_embocadura(45.0))
        assert "cajon_aletas_30_75_escuadra" in nota
        with pytest.raises(DatoInvalidoError) as exc:
            M9.verificar_coherencia_embocadura_cajon(_embocadura(None))
    assert exc.value.campo == "embocadura_cajon"
    assert "cajon_concreto_aletas_90_15" in str(exc.value)


def test_cambiar_el_angulo_no_deja_la_carta_del_marco_intacta():
    """
    La Carta 9 nombra «45° wingwall flare»: con aleros a 30 grados la carta
    que corresponde es la de 18-33.7 grados, y la declarada no pasa.
    """
    with declarados({"embocadura_cajon": "cajon_concreto_aleta_45_d043",
                     "ke_entrada_cajon": "cajon_aletas_30_75_escuadra"}):
        assert M9.verificar_coherencia_embocadura_cajon(_embocadura(45.0))
        with pytest.raises(DatoInvalidoError) as exc:
            M9.verificar_coherencia_embocadura_cajon(_embocadura(30.0))
    assert "cajon_concreto_aleta_18_337_d083" in str(exc.value)


def test_en_un_marco_m4_recalcula_con_la_fila_de_la_embocadura(csv_c01):
    """
    C-01 con los siete del cajon: con aleros a 45 grados dimensiona el marco
    de 1.20 x 0.90 m (PARADA (c): la seccion de la linea base no se mueve).
    Con el cabezal RECTO y las filas de 30-75 grados, el punto se detiene en
    la coherencia y el bucle de MD no corre. Con el cabezal recto y SUS
    filas, M4 recalcula: la carga cambia porque cambian ke (0.4 -> 0.5) y la
    carta (escala 1 -> escala 2 de la Carta 8).
    """
    externos = _externos()
    with declarados(DECLARACIONES_DEL_CAJON):
        con_aleros = cli.correr(csv_c01, externos, alcance=cli.ALCANCE_PERFIL)
        with declarados({"embocadura_cabezal": M6.EMBOCADURA_CABEZAL_RECTO}):
            incoherente = cli.correr(csv_c01, externos,
                                     alcance=cli.ALCANCE_PERFIL)
            with declarados({
                    "embocadura_cajon": "cajon_concreto_aletas_90_15",
                    "ke_entrada_cajon": "cajon_sin_aletas_escuadra_3"}):
                recto = cli.correr(csv_c01, externos,
                                   alcance=cli.ALCANCE_PERFIL)
    c01 = con_aleros.puntos[3]
    assert c01.dimensionado
    assert c01.resultado.seccion.etiqueta() == "marco 1.20 × 0.90 m"
    assert "coherente" in c01.coherencia_embocadura
    bloqueado = incoherente.puntos[3]
    assert not bloqueado.dimensionado and not bloqueado.traza
    assert any("coherencia de la embocadura" in b.etapa
               for b in bloqueado.bloqueos)
    r = recto.puntos[3]
    assert r.dimensionado
    assert r.resultado.resultado_hidraulico.HW != pytest.approx(
        c01.resultado.resultado_hidraulico.HW, rel=REL_CAMBIO_APRECIABLE)


def test_en_un_tubo_el_angulo_y_el_tipo_no_mueven_nada(corrida_perfil):
    """
    La fuente no distingue: la Tabla C.2 pone el tubo bajo «Headwall or
    headwall and wingwalls» y las Cartas 1-3 no separan aleros. Ni el angulo
    ni el tipo mueven el HW de A-01, A-02 o B-01 (PARADA (c): diametros
    movidos, ninguno).
    """
    base, externos = corrida_perfil
    with declarados({"embocadura_cabezal": M6.EMBOCADURA_CABEZAL_RECTO}):
        recto = cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)
    with declarados({"angulo_aletas": {"por_defecto_grados": 60.0,
                                       "umbral_esviaje_grados": 30.0,
                                       "con_esviaje_mayor_grados": 60.0}}):
        a60 = cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)
    for otra in (recto, a60):
        for p, q in zip(base.puntos[:3], otra.puntos[:3]):
            assert p.dimensionado and q.dimensionado
            assert p.resultado.seccion.etiqueta() == "Ø 0.90 m"
            assert q.resultado.seccion.etiqueta() == "Ø 0.90 m"
            assert q.resultado.resultado_hidraulico.HW == pytest.approx(
                p.resultado.resultado_hidraulico.HW, rel=REL)


# ===========================================================================
# 3 - El predimensionamiento de UN cabezal, con la aritmetica escrita
# ===========================================================================

def test_predimensionamiento_de_un_cabezal_de_voladizo():
    """
    Tubo 0.90 m, pared 0.10 m: clave exterior a 1.00 m sobre la solera.
        coronacion = max(101.00 + 0.30 + 0.15, 101.10 + 0.00) = 101.45
        D_f = 0.80 (E.050)  ->  desplante 99.20  ->  H_c = 2.25 > 2.0: voladizo
        pantalla 0.30; B = 0.7*2.25 = 1.575
        e_z = max(2.25/10 = 0.225, 0.30 + 0.070 de E.060 15.7 + 7.7.1) = 0.37
        punta = 0.33*1.575 = 0.51975; talon = 1.575 - 0.51975 - 0.30 = 0.75525
        L_c = 1.10 + 2*0.30 = 1.70
        aleros, esviaje 15 y alfa 45: h0 = 1.45;
            corto = (1.45 - 0.40)*2.0/cos 30 = 2.42487...
            largo = (1.45 - 0.40)*2.0/cos 60 = 4.2
        losa 1.5*0.90 = 1.35 x 0.30; dentellon 0.80 x 0.40 bajo el terreno
        del pie (100.00): base a 99.20

    REESCRITO en las correcciones de T-7a: el espesor de la zapata era 0.225
    (H/10 sin piso) y pasa a 0.37 por el piso [N→] de E.060 15.7 (dudoso 4);
    los aleros eran 2.9698 m los dos (sin esviaje en la formula, H1).
    """
    g = M9.predimensionar_cabezal(extremo=_extremo(), embocadura=_embocadura(),
                                  talud=2.0)
    assert g.cota_coronacion == pytest.approx(101.45, rel=REL)
    assert g.D_f == pytest.approx(0.80, rel=REL)
    assert g.cota_desplante == pytest.approx(99.20, rel=REL)
    assert g.altura_total == pytest.approx(2.25, rel=REL)
    assert g.H == pytest.approx(2.25 - 0.37, rel=REL)
    assert g.tipo == M9.TIPO_VOLADIZO
    assert g.espesor_corona == pytest.approx(0.30, rel=REL)
    assert g.espesor_base_muro == pytest.approx(0.30, rel=REL)
    assert g.B == pytest.approx(1.575, rel=REL)
    assert g.espesor_zapata == pytest.approx(0.37, rel=REL)
    assert g.ancho_punta == pytest.approx(0.51975, rel=REL)
    assert g.ancho_talon == pytest.approx(0.75525, rel=REL)
    assert g.exigir_ancho_talon() == pytest.approx(0.75525, rel=REL)
    assert g.longitud == pytest.approx(1.70, rel=REL)
    assert g.beta_grados == pytest.approx(0.0, abs=ABS_CERO)
    a = g.aleros
    assert a.angulo_grados == pytest.approx(45.0, rel=REL)
    assert a.altura_inicial == pytest.approx(1.45, rel=REL)
    assert a.longitud_corto == pytest.approx(2.1 / (math.sqrt(3) / 2), rel=REL)
    assert a.longitud_largo == pytest.approx(2.1 / 0.5, rel=REL)
    assert a.espesor == pytest.approx(0.30, rel=REL) and a.ancho_zapata == pytest.approx(1.575, rel=REL)
    lo = g.losa
    assert (lo.longitud, lo.espesor) == pytest.approx((1.35, 0.30), rel=REL)
    assert lo.profundidad_dentellon == pytest.approx(0.80, rel=REL)
    assert lo.cota_base_dentellon == pytest.approx(99.20, rel=REL)
    assert lo.ancho_dentellon == pytest.approx(0.40, rel=REL)
    assert all(d.origen == ORIGEN_DIMENSION_REGLA for d in g.dimensiones)
    assert g.extremo == "entrada"


def test_el_agua_puede_gobernar_la_coronacion():
    g = M9.predimensionar_cabezal(extremo=_extremo(cota_agua=101.60),
                                  embocadura=_embocadura(), talud=2.0)
    assert g.cota_coronacion == pytest.approx(101.60, rel=REL)


def test_predimensionamiento_de_un_cabezal_de_gravedad_con_el_minimo_de_e060():
    """
    Clave exterior a 0.60 m: coronacion 100.00 + 0.60 + 0.45 = 101.05;
    H_c = 1.05 + 0.80 = 1.85 <= 2.0: gravedad ciclopeo.
        pantalla H_c/6 = 0.308333...; B = 0.7*1.85 = 1.295
        e_z = max(1.85/10 = 0.185, 0.30 de E.060 22.7.4) = 0.30
        punta = 0.33*1.295 = 0.42735; talon = 1.295 - 0.42735 - 1.85/6
    """
    g = M9.predimensionar_cabezal(
        extremo=_extremo(cota_clave_exterior=100.60, cota_agua=100.50,
                         ancho_exterior=0.70, altura_interior=0.50),
        embocadura=_embocadura(), talud=2.0)
    assert g.altura_total == pytest.approx(1.85, rel=REL)
    assert g.tipo == M9.TIPO_GRAVEDAD
    assert g.espesor_corona == pytest.approx(1.85 / 6, rel=REL)
    assert g.B == pytest.approx(1.295, rel=REL)
    assert g.espesor_zapata == pytest.approx(0.30, rel=REL)
    assert "22.7.4" in _dim(g, "espesor de la zapata").regla
    assert g.ancho_talon == pytest.approx(1.295 - 0.42735 - 1.85 / 6, rel=REL)


def test_a_la_salida_la_socavacion_baja_el_desplante_y_el_dentellon():
    """
    Hoya con fondo a 98.20, pie a 99.00, margen 2.0 ft = 0.6096:
        D_f = max(0.80, 99.00 - (98.20 - 0.6096)) = 1.4096
        base del dentellon = min(99.00 - 0.80, 98.20 - 0.6096) = 97.5904
        -> profundidad desde el terreno 1.4096
    Con el fondo a 97.90: D_f = 1.7096 y dentellon 1.7096 (base 97.2904).

    REESCRITO en las correcciones de T-7a (H3/H9): el dentellon llegaba AL
    fondo de la hoya (0.80 y 1.10 m, margen 0) medido desde la solera; ahora
    baja bajo la hoya con el margen de AASHTO 12.6.5 y se mide desde el
    terreno del pie, la misma referencia del desplante.
    """
    base = dict(extremo="salida", cota_solera=99.00, cota_pie=99.00,
                cota_clave_exterior=100.00, cota_agua=99.40)
    g = M9.predimensionar_cabezal(
        extremo=_extremo(**base, cota_fondo_hoya=98.20,
                         origen_socavacion="estimada"),
        embocadura=_embocadura(), talud=2.0)
    assert g.D_f == pytest.approx(99.00 - (98.20 - 0.6096), rel=REL)
    assert g.cota_desplante == pytest.approx(98.20 - 0.6096, rel=REL)
    assert g.losa.cota_base_dentellon == pytest.approx(97.5904, rel=REL)
    assert g.losa.profundidad_dentellon == pytest.approx(1.4096, rel=REL)
    g2 = M9.predimensionar_cabezal(
        extremo=_extremo(**base, cota_fondo_hoya=97.90,
                         origen_socavacion="estimada"),
        embocadura=_embocadura(), talud=2.0)
    assert g2.D_f == pytest.approx(1.7096, rel=REL)
    assert g2.losa.profundidad_dentellon == pytest.approx(1.7096, rel=REL)
    assert g2.losa.cota_base_dentellon == pytest.approx(97.2904, rel=REL)


def test_los_aleros_usan_el_coseno_del_angulo_con_el_eje():
    """
    DISCREPANCIA DECLARADA con el encargo, que escribe «/ sen alfa» con alfa
    «con el eje del conducto». Sin esviaje, a 30 grados: (1.45 - 0.40)*2.0/
    cos 30 = 2.42487... los dos; con el seno daria 4.2, un 73 % mas.
    REESCRITO en las correcciones de T-7a: el caso es SIN esviaje (con
    esviaje los dos aleros difieren, H1: `test_t7a_correcciones.py`).
    """
    g = M9.predimensionar_cabezal(extremo=_extremo(),
                                  embocadura=_embocadura(30.0, esviaje=0.0),
                                  talud=2.0)
    for L in g.aleros.longitudes:
        assert L == pytest.approx(1.05 * 2.0 / (math.sqrt(3) / 2), rel=REL)
        assert L != pytest.approx(1.05 * 2.0 / 0.5, rel=REL_OTRA_FORMULA)


def test_sin_aleros_no_se_predimensionan_aleros():
    g = M9.predimensionar_cabezal(extremo=_extremo(),
                                  embocadura=_embocadura(None), talud=2.0)
    assert g.aleros is None


def test_un_alero_que_ya_arranca_a_la_altura_final_no_se_alarga():
    aleros, _dims, nota = M9.predimensionar_aleros(
        embocadura=_embocadura(), altura_inicial=0.35, espesor=0.3,
        ancho_zapata=1.0, espesor_zapata=0.3, talud=2.0,
        reglas=ca.valor("predimensionamiento_cabezal"))
    assert aleros.longitud_corto == pytest.approx(0.0, abs=ABS_CERO)
    assert aleros.longitud_largo == pytest.approx(0.0, abs=ABS_CERO)
    assert "no se alarga" in nota


# ===========================================================================
# 4 - CB1-CB5 y las dimensiones declaradas
# ===========================================================================

def test_con_la_regla_las_siete_verificaciones_cumplen():
    """
    REESCRITO en las correcciones de T-7a (H4): eran cinco; CB6 (espesor de
    la zapata frente al minimo de su tipo) y CB7 (base del dentellon frente
    al terreno y a la hoya) se suman. CB4 cita E.050 POR ANALOGIA y gobierna
    el criterio [N→] (H8).
    """
    ext = _extremo(extremo="salida", cota_fondo_hoya=99.20,
                   origen_socavacion="estimada")
    g = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                  talud=2.0)
    vs = M9.verificar_compatibilidad_cabezal(geometria=g, extremo=ext)
    assert [v.codigo for v in vs] == ["CB1.s", "CB2.s", "CB3.s", "CB4.s",
                                      "CB5.s", "CB6.s", "CB7.s"]
    assert all(v.cumple for v in vs)
    assert all(v.paso is not None and v.paso.umbral is not None for v in vs)
    cb4 = vs[3]
    assert cb4.valor_admisible == pytest.approx(0.80, rel=REL)
    assert "26.2" in cb4.numeral and "analogia" in cb4.numeral
    assert cb4.criterio_aplicado == "profundidad_cimentacion_min_cabezal_m"
    cb5 = vs[4]
    assert cb5.criterio_aplicado == "margen_zapata_bajo_socavacion_m"


def test_sin_socavacion_no_hay_cb5():
    ext = _extremo()
    g = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                  talud=2.0)
    codigos = [v.codigo for v in
               M9.verificar_compatibilidad_cabezal(geometria=g, extremo=ext)]
    assert codigos == ["CB1.e", "CB2.e", "CB3.e", "CB4.e", "CB6.e", "CB7.e"]


def test_una_dimension_declarada_gana_y_se_verifica():
    ext = _extremo()
    g = M9.predimensionar_cabezal(
        extremo=ext, embocadura=_embocadura(), talud=2.0,
        declaradas={"profundidad_desplante_m": 0.50, "longitud_m": 1.00},
        tipo_declarado=M9.TIPO_GRAVEDAD)
    assert g.D_f == pytest.approx(0.50, rel=REL) and g.longitud == pytest.approx(1.00, rel=REL)
    assert g.tipo == M9.TIPO_GRAVEDAD
    assert _dim(g, "profundidad de desplante (D_f)").origen == \
        ORIGEN_DIMENSION_DECLARADA
    # REESCRITO en las correcciones de T-7a (H9): B = 0.7·H_c, y H_c sale
    # del desplante DECLARADO: B no es «propuesta por regla» sino derivada.
    # La longitud del muro no depende de ninguna declarada: sigue de regla.
    assert _dim(g, "ancho de la zapata (B)").origen == ORIGEN_DIMENSION_DERIVADA
    assert _dim(g, "longitud de la losa de entrega").origen == \
        ORIGEN_DIMENSION_REGLA
    vs = {v.codigo: v for v in
          M9.verificar_compatibilidad_cabezal(geometria=g, extremo=ext)}
    assert not vs["CB4.e"].cumple            # 0.50 < 0.80 de E.050
    assert not vs["CB1.e"].cumple            # 1.00 < 1.10 de ancho exterior
    assert vs["CB2.e"].cumple and vs["CB3.e"].cumple


def test_una_geometria_declarada_imposible_se_rechaza_nombrandola():
    with pytest.raises(DatoInvalidoError) as exc:
        M9.predimensionar_cabezal(
            extremo=_extremo(), embocadura=_embocadura(), talud=2.0,
            declaradas={"ancho_zapata_m": 0.40})
    assert "talon" in str(exc.value)
    with pytest.raises(DatoInvalidoError):
        M9.predimensionar_cabezal(
            extremo=_extremo(), embocadura=_embocadura(), talud=2.0,
            declaradas={"altura_total_m": 0.20, "espesor_zapata_m": 0.30})


def test_una_geometria_de_tanteo_sin_talon_pide_el_dato():
    g = GeometriaCabezal(H=2.0, B=1.5, D_f=0.8, espesor_corona=0.3,
                         espesor_base_muro=0.3, espesor_zapata=0.3)
    with pytest.raises(DatoFaltanteError) as exc:
        g.exigir_ancho_talon()
    assert exc.value.campo == "ancho_talon"


@pytest.mark.parametrize("malo", [
    "0.30", True, -1.0, 0.0, float("nan"), float("inf"), 31.0, [1.0]])
def test_la_puerta_del_dato_externo_rechaza_lo_que_no_es_una_dimension(malo):
    with pytest.raises(DatoInvalidoError):
        M9.validar_cabezal_declarado({"altura_total_m": malo})


def test_la_puerta_rechaza_claves_desconocidas_y_tipos_fuera_del_conjunto():
    for malo in ({"altura": 2.0}, {"tipo": "mamposteria"},
                 {"entrada": {"lonjitud_m": 2.0}}, {}, "2.0",
                 {"entrada": 2.0}):
        with pytest.raises(DatoInvalidoError):
            M9.validar_cabezal_declarado(malo)


def test_la_puerta_normaliza_comun_mas_extremo():
    n = M9.validar_cabezal_declarado(
        {"profundidad_desplante_m": 1.2, "tipo": "gravedad_ciclopeo",
         "salida": {"profundidad_desplante_m": 1.8}})
    assert n["entrada"]["tipo"] == n["salida"]["tipo"] == "gravedad_ciclopeo"
    assert n["entrada"]["profundidad_desplante_m"] == pytest.approx(1.2, rel=REL)
    assert n["salida"]["profundidad_desplante_m"] == pytest.approx(1.8, rel=REL)
    assert set(n["entrada"]) == set(n["salida"]) == {
        "profundidad_desplante_m", "tipo"}


def test_el_dato_externo_entra_por_el_json_y_fuera_de_las_claves_exigidas(
        tmp_path):
    ruta = tmp_path / "externos.json"
    ruta.write_text('{"puntos": {"A-01": {"cabezal_declarado": '
                    '{"salida": {"profundidad_desplante_m": 1.5}}}}}',
                    encoding="utf-8")
    externos = cli.cargar_datos_externos(ruta, {"luz_m": LUZ})
    salida = externos.valor("A-01", "cabezal_declarado")["salida"]
    assert set(salida) == {"profundidad_desplante_m"}
    assert salida["profundidad_desplante_m"] == pytest.approx(1.5, rel=REL)
    assert "cabezal_declarado" not in servicio.CLAVES_EXTERNAS
    malo = tmp_path / "malo.json"
    malo.write_text('{"globales": {"cabezal_declarado": {"altura_total_m": '
                    '"2.4"}}}', encoding="utf-8")
    with pytest.raises(DatoInvalidoError):
        cli.cargar_datos_externos(malo, {})


# ===========================================================================
# 5 - La longitud entre cabezales (ficha T6-01)
# ===========================================================================

class _LongitudPorExtremo:
    metodo = MetodoLongitud.POR_EXTREMO
    cota_borde_entrada = 44.20
    cota_borde_salida = 44.20
    talud = 2.0
    factor_esviaje = 1.0 / math.cos(math.radians(15.0))
    longitud = 18.869


def test_la_longitud_entre_cabezales_con_la_aritmetica_escrita():
    """
    Relleno retenido = coronacion - bordillo: 43.55 - 0.15 = 43.40 y
    43.437 - 0.15 = 43.287.
    [9.60 + 2.0*((44.20 - 43.40) + (44.20 - 43.287))] / cos 15
    = (9.60 + 2.0*1.713) / 0.965926 = 13.026 / 0.965926 = 13.4855...
    REESCRITO en las correcciones de T-7a (H6): el talud moria en la corona
    del bordillo (12.426 / cos 15 = 12.864 m).
    """
    L, motivo = M9.longitud_entre_cabezales(
        longitud=_LongitudPorExtremo(), ancho_plataforma=9.60,
        cota_relleno_entrada=43.40, cota_relleno_salida=43.287)
    assert motivo == ""
    assert L == pytest.approx(13.026 / math.cos(math.radians(15.0)), rel=REL)


def test_sin_metodo_por_extremo_no_hay_longitud_entre_cabezales():
    L, motivo = M9.longitud_entre_cabezales(
        longitud=None, ancho_plataforma=9.6, cota_relleno_entrada=1.0,
        cota_relleno_salida=1.0)
    assert L is None and "declaro" in motivo


def test_una_coronacion_sobre_la_plataforma_no_da_longitud():
    with pytest.raises(LimiteNumericoError):
        M9.longitud_entre_cabezales(
            longitud=_LongitudPorExtremo(), ancho_plataforma=9.60,
            cota_relleno_entrada=60.0, cota_relleno_salida=60.0)


# ===========================================================================
# 6 - El pipeline
# ===========================================================================

def test_a_perfil_cada_punto_lleva_su_embocadura_y_la_fase_9_se_difiere(
        corrida_perfil):
    informe, _ = corrida_perfil
    for p in informe.puntos:
        assert p.cabezal is None
        if p.dimensionado:
            assert p.embocadura is not None
            assert p.proteccion_entrada.tipo_embocadura == p.embocadura.tipo
            assert p.proteccion_entrada.elementos == \
                M6.EMBOCADURAS[M6.EMBOCADURA_CABEZAL_CON_ALEROS]
    assert any(b.diferido_por_alcance for b in informe.cabezal.bloqueos)
    usados = set(informe.contexto.criterios_usados)
    assert {"embocadura_cabezal", "angulo_aletas"} <= usados
    assert not {"predimensionamiento_cabezal",
                "margen_zapata_bajo_socavacion_m",
                "dentellon_losa_entrega"} & usados


def test_a_expediente_el_proyecto_ya_no_se_detiene_en_una_geometria_unica():
    informe = cli.correr(CSV_EJEMPLO, _externos(),
                         alcance=cli.ALCANCE_EXPEDIENTE)
    claves = {b.criterio for b in informe.cabezal.bloqueos if b.criterio}
    assert "predimensionamiento_cabezal" not in claves
    assert not hasattr(informe.cabezal, "geometria")
    # ningun punto del fixture dimensiona a expediente (V5 en el criterio
    # 'remanso_derecho_via', y detras V8: ficha T7A-01), y por eso ninguno
    # lleva cabezal: la Fase 9 solo propone sobre una seccion
    assert all(p.cabezal is None for p in informe.puntos)
    assert informe.cabezal.por_punto == []


def test_la_fase_9_del_punto_sobre_a01(a01_con_cabezal):
    c = a01_con_cabezal.cabezal
    assert isinstance(c, CabezalDelPunto)
    g = a01_con_cabezal.geometria
    e, s = c.entrada, c.salida
    # coronacion = solera + (0.90 + 0.10) + 0.30 + 0.15 en los dos extremos
    assert e.cota_coronacion == pytest.approx(g.cota_entrada.valor + 1.45,
                                              rel=REL)
    assert s.cota_coronacion == pytest.approx(g.cota_salida + 1.45, rel=REL)
    assert e.altura_total == pytest.approx(2.25, rel=REL)
    # a la salida el pie es el MAS BAJO entre la solera y el fondo del
    # receptor (41.30 en A-01, bajo la solera): el desplante baja con el
    pie_s = min(g.cota_salida, a01_con_cabezal.punto.cota_fondo_receptor)
    assert pie_s == pytest.approx(41.30, rel=REL)
    assert s.cota_desplante == pytest.approx(pie_s - 0.80, rel=REL)
    assert s.altura_total == pytest.approx(
        g.cota_salida + 1.45 - (pie_s - 0.80), rel=REL)
    assert s.aleros.altura_inicial == pytest.approx(
        s.cota_coronacion - pie_s, rel=REL)
    assert all(v.cumple for v in c.verificaciones)
    assert {v.codigo for v in c.verificaciones} == {
        "CB1.e", "CB2.e", "CB3.e", "CB4.e", "CB6.e", "CB7.e",
        "CB1.s", "CB2.s", "CB3.s", "CB4.s", "CB6.s", "CB7.s"}
    # la longitud entre cabezales, con la aritmetica de la ficha T6-01 y el
    # talud muriendo en el relleno retenido (corona - 0.15 de bordillo; H6)
    L = c.longitud_entre_cabezales
    lc = g.longitud_calculada
    esperado = (9.60 + 2.0 * ((lc.cota_borde_entrada - (e.cota_coronacion - 0.15))
                              + (lc.cota_borde_salida - (s.cota_coronacion - 0.15)))) \
        / math.cos(math.radians(15.0))
    assert L == pytest.approx(esperado, rel=REL)
    assert L < g.longitud
    # y el aviso del desplante sin socavacion, por `avisos()`
    assert any("sin socavacion" in a for a in a01_con_cabezal.avisos())
    # las CB entran a las verificaciones del punto, con su fase
    fases = {f for f, v in a01_con_cabezal.verificaciones()
             if v.codigo and v.codigo.startswith("CB")}
    assert fases == {servicio.FASE_CABEZAL}


def test_la_memoria_imprime_la_tabla_de_geometria_por_punto(a01_con_cabezal):
    html = M11.memoria_de_punto(a01_con_cabezal)
    assert "Fase 9 &mdash; Cabezal y aleros del punto" in html
    assert "Cabezal de entrada" in html and "Cabezal de salida" in html
    assert ORIGEN_DIMENSION_REGLA in html
    for codigo in ("9.0.0", "9.0.1e", "9.0.2s", "9.0.3e", "9.0.4s", "9.0.5"):
        assert codigo in html, codigo
    pasos = M11.traza_cabezal(a01_con_cabezal)
    assert {p.fundamento_id for p in pasos} >= {
        "F9.EMBOCADURA", "F9.CORONACION", "F9.DESPLANTE", "F9.ALEROS",
        "F9.LOSA", "F9.LONGITUD"}


def test_el_json_y_la_cli_llevan_el_cabezal_del_punto(a01_con_cabezal):
    j = cli._cabezal_del_punto_json(a01_con_cabezal)
    assert j["embocadura"]["tipo"] == M6.EMBOCADURA_CABEZAL_CON_ALEROS
    assert [c["extremo"] for c in j["cabezales"]] == ["entrada", "salida"]
    dims = j["cabezales"][0]["dimensiones"]
    assert all(d["origen"] == ORIGEN_DIMENSION_REGLA for d in dims)
    assert j["longitud_entre_cabezales_m"] is not None
    lineas = "\n".join(cli._lineas_cabezal_del_punto(a01_con_cabezal))
    assert "Fase 9  cabezal de entrada" in lineas
    assert "todas propuestas por regla" in lineas


def test_una_dimension_declarada_por_punto_llega_a_la_memoria(
        corrida_perfil, tmp_path):
    informe, _ = corrida_perfil
    a02 = next(p for p in informe.puntos if p.punto.id == "A-02")
    ruta = tmp_path / "externos.json"
    ruta.write_text('{"puntos": {"A-02": {"cabezal_declarado": '
                    '{"salida": {"profundidad_desplante_m": 1.5}}}}}',
                    encoding="utf-8")
    externos = cli.cargar_datos_externos(ruta, {"luz_m": LUZ})
    servicio._fase_9(a02, externos)
    s = a02.cabezal.salida
    assert s.D_f == pytest.approx(1.5, rel=REL)
    assert _dim(s, "profundidad de desplante (D_f)").origen == \
        ORIGEN_DIMENSION_DECLARADA
    assert _dim(a02.cabezal.entrada,
                "profundidad de desplante (D_f)").origen == \
        ORIGEN_DIMENSION_REGLA
    html = M11.memoria_de_punto(a02)
    assert ORIGEN_DIMENSION_DECLARADA in html


def test_la_fase_9_del_marco_c01(csv_c01):
    externos = _externos()
    with declarados(DECLARACIONES_DEL_CAJON):
        informe = cli.correr(csv_c01, externos, alcance=cli.ALCANCE_PERFIL)
        c01 = informe.puntos[3]
        assert c01.dimensionado
        servicio._fase_9(c01, externos)
    c = c01.cabezal
    # ancho exterior del marco 1.20 + 2*0.20 = 1.60; L_c = 1.60 + 0.60
    assert c.entrada.longitud == pytest.approx(2.20, rel=REL)
    # clave exterior 0.90 + 0.20 = 1.10 sobre la solera; corona +0.45
    assert c.entrada.cota_coronacion == pytest.approx(
        c01.geometria.cota_entrada.valor + 1.55, rel=REL)
    assert all(v.cumple for v in c.verificaciones)


def test_las_funciones_sin_consumidor_ya_no_culpan_a_un_criterio_vacio():
    for razon in M9.FUNCIONES_SIN_CONSUMIDOR.values():
        assert "esta vacio" not in razon or "predimensionamiento" not in razon


def test_los_extremos_salen_de_lo_que_las_fases_anteriores_resolvieron(
        a01_con_cabezal):
    """
    `extremos_del_conducto` no decide nada: lee la solera de 7.B, la clave
    FISICA (0.90 + 0.10 de pared), el HW de M4 y el ancho exterior.
    """
    p = a01_con_cabezal
    e, s = M9.extremos_del_conducto(
        punto=p.punto_de_calculo, resultado=p.resultado,
        geometria=p.geometria, socavacion=p.socavacion)
    h = p.resultado.resultado_hidraulico
    assert e.cota_solera == pytest.approx(p.geometria.cota_entrada.valor, rel=REL)
    assert s.cota_solera == pytest.approx(p.geometria.cota_salida, rel=REL)
    assert e.cota_clave_exterior - e.cota_solera == pytest.approx(1.00, rel=REL)
    assert e.cota_agua - e.cota_solera == pytest.approx(h.HW, rel=REL)
    assert s.cota_agua - s.cota_solera == pytest.approx(
        max(h.TW_m, h.y_salida_m), rel=REL)
    assert e.ancho_exterior == pytest.approx(1.10, rel=REL)
    assert s.cota_fondo_hoya is None          # el fixture no trae el lecho
    # y `cabezal_del_punto` llamado a mano da lo mismo que la etapa
    c = M9.cabezal_del_punto(punto=p.punto_de_calculo, resultado=p.resultado,
                             geometria=p.geometria, embocadura=p.embocadura,
                             socavacion=p.socavacion)
    assert c.longitud_entre_cabezales == pytest.approx(
        p.cabezal.longitud_entre_cabezales, rel=REL)
    assert [g.cota_coronacion for g in c.geometrias] == pytest.approx(
        [g.cota_coronacion for g in p.cabezal.geometrias], rel=REL)
