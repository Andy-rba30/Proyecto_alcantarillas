"""
tests/test_t7a_correcciones.py
==============================
Aceptacion de las CORRECCIONES de la auditoria adversarial de T-7a
(2026-11-13): H1 a H10, los tres «dudosos» que el orquestador resolvio
(E.050 como [N→], la lectura de AASHTO 12.6.5 sobre la zapata del cabezal y
el piso de la zapata armada de E.060 15.7) y la decision 3 del dueño (la caja
receptora que el programa no modela, avisada en la Familia B). La decision 4
del dueño -- abrir la puerta de `ancho_derecho_via_m` -- NO se aplico: su
premisa quedo refutada (H2), y este archivo fija la refutacion.

Los oraculos son ARITMETICA ESCRITA en cada test, con los numeros del caso:
la longitud de los dos aleros con esviaje (el dorado del encargo: A-01, theta
15, alfa 45, talud 2.0, h0 - H_f = 1.05 m -> 2.1/cos 30 y 2.1/cos 60), el
desnivel del talud a lo largo del muro, el dentellon desde el terreno del
pie, la longitud entre cabezales al relleno retenido (13.486 m en A-01), el
piso de la zapata armada (0.30 + 0.07 m), el desplante bajo una hoya real de
la Fase 6.

NO SE ESCRIBIO EN ROJO CON `xfail(strict=True)`: el codigo de las
correcciones y este archivo se escribieron en la misma sesion. El rojo se
MIDIO copiando este archivo a un checkout de la FASE A (`1b83d39`) y se
declara en el informe de correcciones de T-7a.
"""

import ast
import inspect
import json
import math
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from src import constantes_normativas as cn
from src import criterios_adoptados as ca
from src import servicio
from src import variables_entrada as ve
from src.modelos import (ORIGEN_DIMENSION_DERIVADA, ORIGEN_DIMENSION_REGLA,
                         Bloqueo, SocavacionSalida, CriterioPendienteError, DatoFaltanteError,
                         DatoInvalidoError, EmbocaduraDelPunto,
                         ExtremoDelConducto, FormaSeccion,
                         LimiteNumericoError, MetodoLongitud, TipoDeBloqueo,
                         Verificacion)
from src.modulos import M2_material as M2
from src.modulos import M5_verificaciones as M5
from src.modulos import M6_proteccion as M6
from src.modulos import M9_cabezal as M9
from src.normativa.registro import construir
from tests.apoyo.aproximacion import ABS_CERO
from tests.apoyo.criterios import con_valor, declarados
from tests.test_canal_discrepancias import DECLARACIONES_DEL_CAJON

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_AMPLIADOS = RAIZ / "tests" / "linea_base_familia_c" / \
    "entradas_ampliadas.json"
DECISIONES = RAIZ / "docs" / "decisiones_diferidas.md"
HOJA_DE_RUTA = RAIZ / "docs" / "hoja_de_ruta_alcantarillas_v8.md"
LUZ = 2.75
REL = 1e-9          # aritmetica escrita contra el calculo: solo redondeo
ABS_MM = 1e-3       # lo que el encargo da con tres decimales (2.425, 4.200)
FILA_C01 = "C-01,3+100,C,,,,36.90,39.10,38.95,6.5,30,9.60,36.20,,,ML,,,"
CORONACION_CANAL_C01 = 38.30
BORDILLO = 0.15
MARGEN = 0.6096      # 2.0 ft
DESPLANTE_MIN = 0.80
# REESCRITO DECLARANDOLO (verificacion de las formulas de T-7c, punto 7). Era
# 0.30 + 0.070 = 0.37 m: la altura de E.060 15.7 mas los 70 mm de 7.7.1 a).
# Con ese piso la fila A8 del armado --hasta el EJE de la barra-- no cumplia
# en ningun cabezal de regla. Ahora el piso es, a mano:
#     0.30                 E.060 15.7, sobre el refuerzo inferior
#   + 0.0700               recubrimiento con que se ARMA la cara contra el
#                          suelo (con las declaraciones de prueba del conftest
#                          --acero «A», analisis quimico-- la regla del mayor
#                          da los 70 mm de E.060; sin ellas, la cota 91.44 mm)
#   + 0.0254 / 2 = 0.0127  medio diametro de la mayor barra del catalogo
#   = 0.3827 m
PISO_ARMADA = 0.30 + 0.070 + 0.0254 / 2


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


def _embocadura(angulo=45.0, esviaje=15.0) -> EmbocaduraDelPunto:
    return EmbocaduraDelPunto(
        tipo=M6.EMBOCADURA_CABEZAL_CON_ALEROS, angulo_aletas=angulo,
        regla="caso de prueba", esviaje_grados=esviaje,
        criterio_tipo="embocadura_cabezal", criterio_angulo="angulo_aletas")


def _dim(geometria, nombre):
    return next(d for d in geometria.dimensiones if d.nombre == nombre)


def _punto(informe, id_punto):
    return next(p for p in informe.puntos if p.punto.id == id_punto)


def _externos_json(tmp_path, datos):
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return cli.cargar_datos_externos(ruta, {"luz_m": LUZ})


@pytest.fixture(scope="module")
def corrida_perfil():
    externos = cli.cargar_datos_externos(None, {"luz_m": LUZ, "TW_m": 0.3})
    return cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL), \
        externos


@pytest.fixture(scope="module")
def a01(corrida_perfil):
    """A-01 dimensionado a perfil, con la Fase 9 corrida por su etapa."""
    informe, externos = corrida_perfil
    p = _punto(informe, "A-01")
    servicio._fase_9(p, externos)
    assert p.cabezal is not None, [b.mensaje for b in p.bloqueos]
    return p


@pytest.fixture(scope="module")
def csv_c01(tmp_path_factory):
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    ruta = tmp_path_factory.mktemp("c01") / "puntos_c01.csv"
    ruta.write_text(texto.replace(FILA_C01 + "\n",
                                  f"{FILA_C01}{CORONACION_CANAL_C01}\n"),
                    encoding="utf-8")
    return ruta


@pytest.fixture(scope="module")
def c01(csv_c01):
    externos = cli.cargar_datos_externos(EXTERNOS_AMPLIADOS, {"luz_m": LUZ})
    with declarados(DECLARACIONES_DEL_CAJON):
        informe = cli.correr(csv_c01, externos, alcance=cli.ALCANCE_PERFIL)
        p = _punto(informe, "C-01")
        assert p.dimensionado
        servicio._fase_9(p, externos)
    assert p.cabezal is not None, [b.mensaje for b in p.bloqueos]
    return p


# ===========================================================================
# H1 - los dos aleros con esviaje
# ===========================================================================

def test_h1_la_convencion_del_angulo_es_la_del_hds5_y_esta_citada():
    """ΘW: «Flare angle of wingwalls with respect to extension of culvert
    side wall», List of Symbols, pag. impresa xix, PDF 23."""
    c = construir().cita("HDS5_3ED.SIMBOLOS#THETA_W")
    assert c.texto_literal.texto == ("Flare angle of wingwalls with respect "
                                     "to extension of culvert side wall")
    assert (c.pagina_impresa, c.pagina_pdf) == ("xix", 23)
    assert c.verificado is not None
    # la regla de paginacion del HDS-5 traduce el folio romano (i = PDF 5)
    f = construir().fuente("HDS5_3ED")
    assert f.paginacion.pagina_pdf("xix") == 23
    assert f.paginacion.pagina_pdf("i") == 5
    assert f.paginacion.pagina_pdf("iix") is None
    assert f.paginacion.pagina_pdf("3.24") == 82 + 24


def test_h1_dorado_de_la_entrada_de_a01(a01):
    """
    theta = 15, alfa = 45, talud 2.0, h0 - H_f = 1.45 - 0.40 = 1.05 m:
        corto = 2.1 / cos 30 = 2.4249 m
        largo = 2.1 / cos 60 = 4.2000 m
    (el codigo de la FASE A daba 2.970 m a los dos lados).
    """
    a = a01.cabezal.entrada.aleros
    assert a.esviaje_grados == pytest.approx(15.0, rel=REL)
    assert a.altura_inicial - a.altura_final == pytest.approx(1.05, rel=REL)
    assert a.longitud_corto == pytest.approx(2.425, abs=ABS_MM)
    assert a.longitud_largo == pytest.approx(4.200, abs=ABS_MM)
    assert a.longitud_corto == pytest.approx(2.1 / (math.sqrt(3) / 2), rel=REL)
    assert a.longitud_largo == pytest.approx(2.1 / 0.5, rel=REL)


def test_h1_la_salida_de_a01_con_la_aritmetica_escrita(a01):
    """h0 = coronacion - pie = 43.4368 - 41.30; (h0 - 0.40)·2 / cos 30 y
    / cos 60 (el auditor midio 4.011 y 6.947 m)."""
    s = a01.cabezal.salida
    h0 = s.cota_coronacion - 41.30
    assert s.aleros.altura_inicial == pytest.approx(h0, rel=REL)
    assert s.aleros.longitud_corto == pytest.approx(
        (h0 - 0.40) * 2.0 / math.cos(math.radians(30.0)), rel=REL)
    assert s.aleros.longitud_largo == pytest.approx(
        (h0 - 0.40) * 2.0 / math.cos(math.radians(60.0)), rel=REL)
    assert s.aleros.longitud_corto == pytest.approx(4.011, abs=ABS_MM)
    assert s.aleros.longitud_largo == pytest.approx(6.947, abs=ABS_MM)


def test_h1_el_marco_c01_con_esviaje_de_30(c01):
    """
    C-01: theta = 30 (no SUPERA el umbral de 30: alfa = 45), de modo que
    corto / cos 15 y largo / cos 75: el largo es cos 15 / cos 75 = 3.732
    veces el corto, y 2.73 veces lo que la FASE A imprimia a los dos lados.
    """
    a = c01.cabezal.entrada.aleros
    assert a.angulo_grados == pytest.approx(45.0, rel=REL)
    assert a.esviaje_grados == pytest.approx(30.0, rel=REL)
    avance = (a.altura_inicial - a.altura_final) * 2.0
    assert a.longitud_corto == pytest.approx(
        avance / math.cos(math.radians(15.0)), rel=REL)
    assert a.longitud_largo == pytest.approx(
        avance / math.cos(math.radians(75.0)), rel=REL)
    assert a.longitud_largo / (avance / math.cos(math.radians(45.0))) == \
        pytest.approx(2.732, abs=ABS_MM)


def test_h1_sin_esviaje_los_dos_aleros_miden_lo_mismo():
    g = M9.predimensionar_cabezal(extremo=_extremo(),
                                  embocadura=_embocadura(45.0, esviaje=0.0),
                                  talud=2.0)
    assert g.aleros.longitud_corto == pytest.approx(g.aleros.longitud_largo,
                                                    rel=REL)
    assert g.aleros.longitud_largo == pytest.approx(
        1.05 * 2.0 / math.cos(math.radians(45.0)), rel=REL)


@pytest.mark.parametrize("alfa, theta", [(30.0, 60.0), (45.0, 45.0),
                                         (60.0, 45.0)])
def test_h1_un_alero_que_no_alcanza_la_altura_final_es_limite_numerico(
        alfa, theta):
    """alfa + theta >= 90: cos(alfa + theta) se anula (forma MAT-D13)."""
    with pytest.raises(LimiteNumericoError) as exc:
        M9.predimensionar_cabezal(extremo=_extremo(),
                                  embocadura=_embocadura(alfa, esviaje=theta),
                                  talud=2.0, id_punto="X-01")
    texto = str(exc.value)
    assert exc.value.valor == (alfa, theta)
    assert "cabezal_declarado" in texto and "alfa menor" in texto
    assert exc.value.campo == "angulo_aletas" and "X-01" in texto


def test_h1_con_los_aleros_declarados_no_hay_guardia():
    g = M9.predimensionar_cabezal(
        extremo=_extremo(), embocadura=_embocadura(45.0, esviaje=50.0),
        talud=2.0, declaradas={"longitud_aleros_m": 5.0})
    assert g.aleros.longitudes == pytest.approx((5.0, 5.0), rel=REL)


def test_h1_el_aviso_del_desnivel_del_talud_a_lo_largo_del_muro(a01):
    """Δz = L_c·sen(theta)/talud = 1.70·sen 15/2 = 0.220 m."""
    avisos = [x for x in a01.avisos() if "Δz" in x]
    assert len(avisos) == 1
    assert "0.220 m" in avisos[0]
    dz = 1.70 * math.sin(math.radians(15.0)) / 2.0
    assert dz == pytest.approx(0.220, abs=ABS_MM)
    assert f"= {dz:.3f} m" in avisos[0]
    assert "T7A-03" in avisos[0]


def test_h1_sin_esviaje_no_hay_aviso_de_desnivel(corrida_perfil):
    informe, externos = corrida_perfil
    original = _punto(informe, "A-02")
    a02 = replace(original, cabezal=None, bloqueos=list(original.bloqueos),
                  embocadura=replace(original.embocadura, esviaje_grados=0.0))
    servicio._fase_9(a02, externos)
    assert a02.cabezal is not None
    assert not any("Δz" in x for x in a02.avisos())
    a = a02.cabezal.entrada.aleros
    assert a.longitud_corto == pytest.approx(a.longitud_largo, rel=REL)


def test_h1_el_paso_9_0_3_lleva_theta_y_las_dos_longitudes(a01):
    p = next(x for x in a01.cabezal.pasos if x.codigo == "9.0.3e")
    nombres = [m.simbolo for m in p.sustitucion]
    assert "theta" in nombres and "alfa" in nombres
    assert "cos(alfa - theta)" in p.formula
    assert "cos(alfa_largo + theta)" in p.formula
    assert "alfa_largo" in nombres
    assert "HDS5_3ED.SIMBOLOS#THETA_W" in p.citas_textuales


def test_h1_el_fundamento_y_el_docstring_ya_no_dicen_lo_que_es_falso():
    f = construir().fundamento("F9.ALEROS")
    assert "direccion del eje" not in f.por_que
    assert "perpendicular a la via" in f.por_que
    assert "HDS5_3ED.SIMBOLOS#THETA_W" in f.citas
    doc = inspect.getdoc(M9.predimensionar_cabezal)
    assert "absorben el giro" not in doc
    assert "L_c·sen(theta)/talud" in doc


def test_h1_la_ficha_T7A_03_difiere_el_cabezal_paralelo_a_la_via():
    texto = DECISIONES.read_text(encoding="utf-8")
    ficha = texto[texto.index("## T7A-03"):texto.index("## T7A-04")]
    assert "paralelo a la vía" in ficha.lower()
    assert "orientacion_muro_respecto_al_trafico" in ficha
    assert "Carta 11" in ficha


# ===========================================================================
# H2 - la decision 4 del dueño no se aplica: la premisa estaba refutada
# ===========================================================================

# LOS TRES TESTS QUE SIGUEN SE REESCRIBIERON EN T-7b, y se declara. Fijaban
# lo que T-7a dejo: la puerta de `ancho_derecho_via_m` cerrada porque V5 no
# tenia metodo que leyera el dato, y V5 terminando siempre en el `raise`.
# El PUNTO 0 de T-7b (decision del dueño del 2026-11-13) le dio a V5 un
# metodo DECLARABLE -- el embalse a nivel -- y abrio la puerta del dato; las
# tres capas siguen existiendo, y la segunda y la tercera ya no se simulan:
# se atraviesan declarando.
def test_h2_la_puerta_de_ancho_derecho_via_m_se_abrio_en_T7b():
    """El dato tiene lector: `M5.v5_remanso`, con su metodo declarado."""
    assert "ancho_derecho_via_m" in servicio.CLAVES_EXTERNAS
    assert "ancho_derecho_via_m" not in servicio.CLAVES_DE_CABEZAL
    assert ca.CRITERIOS["remanso_derecho_via"].valor is None


def test_h2_las_tres_capas_que_detienen_la_fase_9_a_expediente(monkeypatch):
    """
    Lo que la ficha T7A-01 dice, medido: (1) el criterio vacio
    'remanso_derecho_via'; (2) declarado el metodo, `M5.v5_remanso` se
    detiene en `ancho_derecho_via_m`, que no vino; (3) con el dato, V5 se
    evalua y V8 se detiene en 'TR_evento_extremo'. SIN DECLARAR NADA, ningun
    punto del fixture llega al cabezal a expediente: T-7b no cambio eso.
    """
    externos = cli.cargar_datos_externos(None, {"luz_m": LUZ, "TW_m": 0.3})

    def bloqueo_de(informe):
        a = _punto(informe, "A-01")
        assert not a.dimensionado and a.cabezal is None
        return next(b for b in a.bloqueos if b.etapa.startswith("material"))

    b1 = bloqueo_de(cli.correr(CSV_EJEMPLO, externos,
                               alcance=cli.ALCANCE_EXPEDIENTE))
    assert b1.tipo is TipoDeBloqueo.CRITERIO_PENDIENTE
    assert "remanso_derecho_via" in b1.mensaje
    with declarados({"remanso_derecho_via": "embalse_a_nivel"}):
        b2 = bloqueo_de(cli.correr(CSV_EJEMPLO, externos,
                                   alcance=cli.ALCANCE_EXPEDIENTE))
        assert b2.tipo is TipoDeBloqueo.DATO_FALTANTE
        assert "ancho_derecho_via_m" in b2.mensaje
        # Con el dato (400 m de faja, DE PRUEBA) V5 se evalua de verdad y
        # la que detiene es V8, en su periodo de retorno.
        con_ancho = cli.cargar_datos_externos(
            None, {"luz_m": LUZ, "TW_m": 0.3, "ancho_derecho_via_m": 400.0})
        b3 = bloqueo_de(cli.correr(CSV_EJEMPLO, con_ancho,
                                   alcance=cli.ALCANCE_EXPEDIENTE))
    assert b3.tipo is TipoDeBloqueo.CRITERIO_PENDIENTE
    assert "TR_evento_extremo" in b3.mensaje


def test_h2_v5_recibe_el_dato_por_argumento_y_no_lo_lee_de_los_externos():
    """
    `M5.v5_remanso` ya lee el ancho (T-7b), y lo recibe del servicio en
    `derecho_de_via`: M5 sigue sin conocer los datos externos.
    """
    assert "derecho_de_via" in inspect.signature(M5.v5_remanso).parameters
    fuente = inspect.getsource(M5.v5_remanso)
    arbol = ast.parse(fuente.lstrip())
    llamadas = [n for n in ast.walk(arbol) if isinstance(n, ast.Call)
                and getattr(n.func, "attr", getattr(n.func, "id", "")) in
                ("valor", "dato")]
    lee_externos = [n for n in llamadas
                    if any(isinstance(a, ast.Constant)
                           and a.value == "ancho_derecho_via_m"
                           for a in n.args)]
    assert not lee_externos


def test_h2_la_ficha_T7A_01_dice_las_tres_capas():
    texto = DECISIONES.read_text(encoding="utf-8")
    ficha = texto[texto.index("## T7A-01"):texto.index("## T7A-02")]
    for pieza in ("remanso_derecho_via", "v5_remanso", "ancho_derecho_via_m",
                  "TR_evento_extremo", "decisión 4", "ningún test"):
        assert pieza in ficha, pieza


# ===========================================================================
# H3 - el dentellon se mide desde el terreno del pie
# ===========================================================================

def test_h3_el_dentellon_de_salida_de_a01_baja_desde_el_receptor(a01):
    """
    Pie de salida = min(solera 41.987, receptor 41.30) = 41.30: la base del
    dentellon queda en 41.30 - 0.80 = 40.50 (la FASE A la ponia en
    41.987 - 0.80 = 41.187, 0.11 m bajo el lecho).
    """
    lo = a01.cabezal.salida.losa
    assert lo.cota_terreno == pytest.approx(41.30, rel=REL)
    assert lo.cota_base_dentellon == pytest.approx(40.50, rel=REL)
    assert lo.profundidad_dentellon == pytest.approx(0.80, rel=REL)
    # la misma referencia que el desplante
    assert a01.cabezal.salida.cota_desplante == pytest.approx(40.50, rel=REL)


def test_h3_la_nota_de_la_lamina_04_dice_desde_donde_se_mide():
    nota = construir().cita("MC_HHD.LAMINA_04#DENTELLON").nota
    assert "TERRENO NATURAL" in nota
    assert "No se mide desde la cara superior de la losa" in nota
    doc = inspect.getdoc(M9.LosaDeEntrega)
    assert "DESDE EL TERRENO" in doc
    assert "desde la cara superior de la losa, que" not in doc


# ===========================================================================
# H4 - CB6 y CB7: los minimos con numero que una dimension declarada viola
# ===========================================================================

def _cb(geometria, extremo, codigo):
    return next(v for v in M9.verificar_compatibilidad_cabezal(
        geometria=geometria, extremo=extremo) if v.codigo.startswith(codigo))


def test_h4_cb6_una_zapata_de_gravedad_declarada_de_0_20_no_cumple():
    """E.060 22.7.4: «no debe ser menor que 300 mm» (el caso 1 del auditor,
    que pasaba CB1-CB4 en verde)."""
    ext = _extremo()
    g = M9.predimensionar_cabezal(
        extremo=ext, embocadura=_embocadura(), talud=2.0,
        declaradas={"espesor_zapata_m": 0.20},
        tipo_declarado=M9.TIPO_GRAVEDAD)
    cb6 = _cb(g, ext, "CB6")
    assert not cb6.cumple
    assert cb6.valor_admisible == pytest.approx(0.30, rel=REL)
    assert cb6.paso.umbral.cita_id == "E060.22.7.4#ZAPATA"


def test_h4_cb6_una_zapata_armada_declarada_bajo_el_piso_no_cumple():
    """
    Voladizo armado: 0.30 sobre el refuerzo + 0.070 + 0.0127 = 0.3827 m
    (`PISO_ARMADA`, reescrito y declarado arriba): 0.35 m sigue bajo el.
    """
    ext = _extremo()
    g = M9.predimensionar_cabezal(
        extremo=ext, embocadura=_embocadura(), talud=2.0,
        declaradas={"espesor_zapata_m": 0.35})
    cb6 = _cb(g, ext, "CB6")
    assert g.tipo == M9.TIPO_VOLADIZO and not cb6.cumple
    assert cb6.valor_admisible == pytest.approx(PISO_ARMADA, rel=REL)
    assert cb6.criterio_aplicado == "peralte_min_zapata_armada_m"


def test_h4_cb7_un_dentellon_declarado_de_0_10_no_cumple():
    ext = _extremo(extremo="salida", cota_solera=99.0, cota_pie=99.0,
                   cota_clave_exterior=100.0, cota_agua=99.4)
    g = M9.predimensionar_cabezal(
        extremo=ext, embocadura=_embocadura(), talud=2.0,
        declaradas={"profundidad_dentellon_m": 0.10})
    cb7 = _cb(g, ext, "CB7")
    assert not cb7.cumple
    assert cb7.valor_obtenido == pytest.approx(98.90, rel=REL)
    assert cb7.valor_admisible == pytest.approx(98.20, rel=REL)


def test_h4_cb7_un_dentellon_que_no_baja_bajo_la_hoya_no_cumple():
    """
    El caso 2 del auditor: hoya 2.0 m bajo el pie (fondo a 97.00) y un
    dentellon declarado de 1.0 m: base 98.00 > 97.00 - 0.6096 = 96.3904.
    """
    ext = _extremo(extremo="salida", cota_solera=99.0, cota_pie=99.0,
                   cota_clave_exterior=100.0, cota_agua=99.4,
                   cota_fondo_hoya=97.00, origen_socavacion="declarada")
    g = M9.predimensionar_cabezal(
        extremo=ext, embocadura=_embocadura(), talud=2.0,
        declaradas={"profundidad_dentellon_m": 1.0})
    cb7 = _cb(g, ext, "CB7")
    assert not cb7.cumple
    assert cb7.valor_admisible == pytest.approx(97.00 - MARGEN, rel=REL)
    assert cb7.paso.umbral.cita_id == "AASHTO_LRFD_9.12.6.5#DENTELLON"
    # y la regla, sin declarar, lo deja bajo la hoya con el margen
    g2 = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                   talud=2.0)
    assert g2.losa.cota_base_dentellon == pytest.approx(97.00 - MARGEN, rel=REL)
    assert _cb(g2, ext, "CB7").cumple


# ===========================================================================
# H5 - los tests que faltaban, y los mutantes que importan
# ===========================================================================

def test_h5_la_hoya_real_de_la_fase_6_baja_el_desplante_por_la_etapa(tmp_path):
    """
    A-01 con el lecho declarado: `M6.socavacion_salida` estima la hoya y
    `servicio._fase_9` la toma. A mano, desde la cota de la hoya que M6
    entrega:
        D_f = max(0.80, 41.30 - (hoya - 0.6096))
        desplante = 41.30 - D_f
        base del dentellon = min(41.30 - 0.80, hoya - 0.6096)
    """
    externos = _externos_json(tmp_path, {"globales": {"TW_m": 0.3}, "puntos": {
        "A-01": {"material_lecho_salida": {"tipo": "no_cohesivo",
                                           "D84_m": 0.03, "D16_m": 0.002},
                 "duracion_caudal_pico_min": 60}}})
    informe = cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)
    p = _punto(informe, "A-01")
    hoya = p.socavacion.cota_fondo_de_la_hoya
    assert hoya is not None and hoya < 41.30
    servicio._fase_9(p, externos)
    s = p.cabezal.salida
    D_f = max(DESPLANTE_MIN, 41.30 - (hoya - MARGEN))
    assert s.D_f == pytest.approx(D_f, rel=REL)
    assert s.cota_desplante == pytest.approx(41.30 - D_f, rel=REL)
    assert s.losa.cota_base_dentellon == pytest.approx(
        min(41.30 - DESPLANTE_MIN, hoya - MARGEN), rel=REL)
    cb5 = next(v for v in p.cabezal.verificaciones if v.codigo == "CB5.s")
    assert cb5.cumple
    assert cb5.valor_admisible == pytest.approx(hoya - MARGEN, rel=REL)
    assert not any("sin socavacion" in x for x in p.avisos())


def test_h5_cb5_falla_con_un_desplante_entre_la_hoya_y_la_hoya_menos_margen():
    """Fondo de la hoya a 98.00: un desplante a 97.80 queda bajo la hoya
    pero dentro del margen (97.3904): CB5 no cumple."""
    ext = _extremo(extremo="salida", cota_solera=99.0, cota_pie=99.0,
                   cota_clave_exterior=100.0, cota_agua=99.4,
                   cota_fondo_hoya=98.00, origen_socavacion="declarada")
    g = M9.predimensionar_cabezal(
        extremo=ext, embocadura=_embocadura(), talud=2.0,
        declaradas={"profundidad_desplante_m": 1.20})
    cb5 = _cb(g, ext, "CB5")
    assert g.cota_desplante == pytest.approx(97.80, rel=REL)
    assert not cb5.cumple
    assert cb5.valor_admisible == pytest.approx(98.00 - MARGEN, rel=REL)
    assert _cb(g, ext, "CB4").cumple          # 1.20 >= 0.80


def test_h5_una_altura_total_declarada_fija_la_coronacion():
    """desplante = 100.00 - 0.80 = 99.20; corona = 99.20 + 2.60 = 101.80;
    los aleros salen de ella: h0 = 1.80 -> derivados."""
    g = M9.predimensionar_cabezal(extremo=_extremo(),
                                  embocadura=_embocadura(45.0, esviaje=0.0),
                                  talud=2.0,
                                  declaradas={"altura_total_m": 2.60})
    assert g.cota_coronacion == pytest.approx(101.80, rel=REL)
    assert g.aleros.altura_inicial == pytest.approx(1.80, rel=REL)
    assert g.aleros.longitud_largo == pytest.approx(
        1.40 * 2.0 / math.cos(math.radians(45.0)), rel=REL)
    for nombre in ("longitud del alero corto (alfa - theta)",
                   "longitud del alero largo (alfa + theta)",
                   "ancho de la zapata (B)", "ancho del talon"):
        assert _dim(g, nombre).origen == ORIGEN_DIMENSION_DERIVADA, nombre


@pytest.mark.parametrize("delta, cumple", [(0.0, True), (-1e-3, False)])
def test_h5_la_frontera_de_cb2(delta, cumple):
    """Coronacion declarada justo en clave + recubrimiento (101.30)."""
    ext = _extremo(cota_agua=100.50)
    altura = (101.00 + 0.30 + delta) - (100.00 - DESPLANTE_MIN)
    g = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                  talud=2.0,
                                  declaradas={"altura_total_m": altura})
    assert g.cota_coronacion == pytest.approx(101.30 + delta, rel=REL)
    assert _cb(g, ext, "CB2").cumple is cumple


def test_h5_el_ancho_exterior_de_un_marco_de_dos_celdas(c01):
    """N = 2 celdas de 1.20 m con pared de 0.20: 2·1.20 + 3·0.20 = 3.00 m."""
    r = c01.resultado
    dos = replace(r, resultado_hidraulico=replace(r.resultado_hidraulico,
                                                  numero_celdas=2))
    with declarados(DECLARACIONES_DEL_CAJON):
        e, _s = M9.extremos_del_conducto(
            punto=c01.punto_de_calculo, resultado=dos,
            geometria=c01.geometria, socavacion=c01.socavacion)
        uno, _ = M9.extremos_del_conducto(punto=c01.punto_de_calculo,
                                          resultado=r, geometria=c01.geometria)
    assert e.ancho_exterior == pytest.approx(2 * 1.20 + 3 * 0.20, rel=REL)
    assert uno.ancho_exterior == pytest.approx(1.20 + 2 * 0.20, rel=REL)


def test_h5_sin_tw_ni_tirante_de_salida_es_un_fallo_del_programa(a01):
    r = a01.resultado
    sin = replace(r, resultado_hidraulico=replace(
        r.resultado_hidraulico, TW_m=None, y_salida_m=None))
    with pytest.raises(ValueError, match="nivel de agua"):
        M9.extremos_del_conducto(punto=a01.punto_de_calculo, resultado=sin,
                                 geometria=a01.geometria)


def test_h5_con_otro_metodo_de_longitud_no_hay_longitud_entre_cabezales():
    class _Simetrico:
        metodo = MetodoLongitud.TERRAPLEN_SIMETRICO

    L, motivo = M9.longitud_entre_cabezales(
        longitud=_Simetrico(), ancho_plataforma=9.6,
        cota_relleno_entrada=43.4, cota_relleno_salida=43.3)
    assert L is None
    assert "terraplen_simetrico" in motivo and "terreno" in motivo


@pytest.mark.parametrize("alfa", [90.0, -5.0, float("nan"), float("inf")])
def test_h5_las_guardias_del_angulo_de_los_aleros(alfa):
    with pytest.raises(DatoInvalidoError):
        M9.predimensionar_aleros(
            embocadura=_embocadura(alfa), altura_inicial=1.45, espesor=0.3,
            ancho_zapata=1.5, espesor_zapata=0.3, talud=2.0,
            reglas=ca.valor("predimensionamiento_cabezal"))


@pytest.mark.parametrize("theta", [-1.0, float("nan")])
def test_h5_la_guardia_del_esviaje_de_los_aleros(theta):
    with pytest.raises(DatoInvalidoError):
        M9.predimensionar_aleros(
            embocadura=_embocadura(45.0, esviaje=theta), altura_inicial=1.45,
            espesor=0.3, ancho_zapata=1.5, espesor_zapata=0.3, talud=2.0,
            reglas=ca.valor("predimensionamiento_cabezal"))


# ---------------------------------------------------------------------------
# H5, segunda tanda: los supervivientes de la mutacion de las correcciones
# que no eran equivalentes (arnes de EXT-11 sobre las funciones de la Fase 9
# del punto; los equivalentes de frontera y de texto se dicen en el informe)
# ---------------------------------------------------------------------------

def test_h5_sin_tw_pero_con_tirante_de_salida_no_es_un_fallo(a01):
    """La guardia exige que falten LOS DOS: con el tirante de M4 basta."""
    r = a01.resultado
    sin_tw = replace(r, resultado_hidraulico=replace(
        r.resultado_hidraulico, TW_m=None))
    _e, s = M9.extremos_del_conducto(punto=a01.punto_de_calculo,
                                     resultado=sin_tw, geometria=a01.geometria)
    assert s.cota_agua - s.cota_solera == pytest.approx(
        r.resultado_hidraulico.y_salida_m, rel=REL)


def test_h5_aleros_paralelos_al_barril_son_validos():
    """alfa = 0 es la Tabla C.2 «parallel (extension of sides)»: sin esviaje,
    L = (1.45 - 0.40)·2.0 / cos 0 = 2.10 m."""
    g = M9.predimensionar_cabezal(extremo=_extremo(),
                                  embocadura=_embocadura(0.0, esviaje=0.0),
                                  talud=2.0)
    assert g.aleros.longitudes == pytest.approx((2.10, 2.10), rel=REL)


def test_h5_el_mensaje_del_limite_nombra_alfa_mas_theta():
    with pytest.raises(LimiteNumericoError) as exc:
        M9.predimensionar_cabezal(extremo=_extremo(),
                                  embocadura=_embocadura(50.0, esviaje=45.0),
                                  talud=2.0)
    assert "alfa + theta = 95 grados" in str(exc.value)


def test_h5_un_resguardo_declarado_sube_la_coronacion_gobernada_por_el_agua():
    """Agua a 101.60 + resguardo 0.10 = 101.70 > 101.45 de la clave: rige el
    agua y CB3 la contrasta con el mismo resguardo."""
    reglas = dict(ca.valor("predimensionamiento_cabezal"))
    reglas["resguardo_agua_m"] = 0.10
    ext = _extremo(cota_agua=101.60)
    with declarados({"predimensionamiento_cabezal": reglas}):
        g = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                      talud=2.0)
        cb3 = _cb(g, ext, "CB3")
    assert g.cota_coronacion == pytest.approx(101.70, rel=REL)
    assert cb3.valor_admisible == pytest.approx(101.70, rel=REL)


def test_h5_la_regla_del_desplante_dice_de_donde_salio():
    ext = _extremo(extremo="salida", cota_solera=99.0, cota_pie=99.0,
                   cota_clave_exterior=100.0, cota_agua=99.4,
                   cota_fondo_hoya=98.20, origen_socavacion="declarada")
    g = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                  talud=2.0)
    assert "AASHTO 12.6.5" in _dim(g, "profundidad de desplante (D_f)").regla
    g0 = M9.predimensionar_cabezal(extremo=_extremo(),
                                   embocadura=_embocadura(), talud=2.0)
    assert "sin socavacion" in _dim(g0, "profundidad de desplante (D_f)").regla


def test_h5_el_criterio_de_cada_minimo_va_con_su_tipo():
    """El piso de la zapata armada lo gobierna su criterio [N→]; el de la de
    gravedad, E.060 22.7.4 (y CB6 cita el limite del ciclopeo)."""
    ext = _extremo()
    g = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                  talud=2.0)
    assert _dim(g, "espesor de la zapata").criterio == \
        "peralte_min_zapata_armada_m"
    gg = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                   talud=2.0, tipo_declarado=M9.TIPO_GRAVEDAD)
    cb6 = _cb(gg, ext, "CB6")
    assert cb6.criterio_aplicado == "predimensionamiento_cabezal"
    assert "E060.22.10.2#CICLOPEO" in cb6.paso.citas_textuales
    assert "concreto simple" in cb6.paso.umbral.aplicacion
    assert "ANALOGIA" in _cb(g, ext, "CB6").paso.umbral.aplicacion


def test_h5_el_margen_de_cada_cb_es_obtenido_menos_admisible():
    ext = _extremo()
    g = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                  talud=2.0)
    cb1 = _cb(g, ext, "CB1")                    # 1.70 >= 1.10
    assert cb1.paso.veredicto.margen == pytest.approx(0.60, rel=REL)
    cb7 = _cb(g, ext, "CB7")                    # 99.20 <= 99.20
    assert cb7.paso.veredicto.margen == pytest.approx(0.0, abs=ABS_CERO)
    g2 = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                   talud=2.0,
                                   declaradas={"profundidad_dentellon_m": 1.0})
    assert _cb(g2, ext, "CB7").paso.veredicto.margen == \
        pytest.approx(0.20, rel=REL)            # 99.20 - 99.00


def test_h5_cb7_dice_que_criterio_gobierna_la_base():
    ext = _extremo(extremo="salida", cota_solera=99.0, cota_pie=99.0,
                   cota_clave_exterior=100.0, cota_agua=99.4)
    g = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                  talud=2.0)
    cb7 = _cb(g, ext, "CB7")
    assert cb7.criterio_aplicado == "dentellon_losa_entrega"
    assert "Lamina" in cb7.paso.umbral.aplicacion
    ext_h = replace(ext, cota_fondo_hoya=97.0, origen_socavacion="declarada")
    gh = M9.predimensionar_cabezal(extremo=ext_h, embocadura=_embocadura(),
                                   talud=2.0)
    cb7h = _cb(gh, ext_h, "CB7")
    assert cb7h.criterio_aplicado == "margen_zapata_bajo_socavacion_m"
    assert "12.6.5" in cb7h.paso.umbral.aplicacion


def test_h5_una_altura_total_de_2_0_exactos_es_de_gravedad():
    """El umbral es inclusivo: H_c = 2.0 m -> gravedad ciclopeo."""
    g = M9.predimensionar_cabezal(extremo=_extremo(), embocadura=_embocadura(),
                                  talud=2.0,
                                  declaradas={"altura_total_m": 2.0})
    assert g.tipo == M9.TIPO_GRAVEDAD


def test_h5_una_longitud_entre_cabezales_corta_pero_positiva_existe():
    """Relleno a 46.50 sobre bordes a 44.20: 9.60 + 4·(-2.30) = 0.40 m en
    planta, 0.414 m sobre el eje: corta, pero existe."""
    L, motivo = M9.longitud_entre_cabezales(
        longitud=_LongitudPorExtremo(), ancho_plataforma=9.60,
        cota_relleno_entrada=46.50, cota_relleno_salida=46.50)
    assert motivo == ""
    assert L == pytest.approx(0.40 / math.cos(math.radians(15.0)), rel=REL)


class _LongitudPorExtremo:
    metodo = MetodoLongitud.POR_EXTREMO
    cota_borde_entrada = 44.20
    cota_borde_salida = 44.20
    talud = 2.0
    factor_esviaje = 1.0 / math.cos(math.radians(15.0))
    longitud = 18.869


def test_h5_el_motivo_cuando_hay_profundidad_pero_no_cota_de_hoya():
    s = SocavacionSalida(profundidad_para_desplante=0.8, origen="declarada")
    motivo = M9._motivo_sin_socavacion(s, "")
    assert "no la cota del fondo de la hoya" in motivo
    sin = SocavacionSalida(profundidad_para_desplante=None, origen="sin dato",
                           motivo_no_estimada="falta el lecho")
    assert M9._motivo_sin_socavacion(sin, "") == "falta el lecho"
    assert "no entrego" in M9._motivo_sin_socavacion(None, "")


def test_h5_sin_longitud_calculada_el_talud_es_el_del_criterio(a01):
    """Con la longitud DECLARADA (`longitud_calculada` None) los aleros
    siguen al talud del criterio; con una calculada, al de 7.B."""
    g_decl = replace(a01.geometria, longitud_calculada=None)
    c = M9.cabezal_del_punto(punto=a01.punto_de_calculo,
                             resultado=a01.resultado, geometria=g_decl,
                             embocadura=a01.embocadura)
    assert c.longitud_entre_cabezales is None
    assert c.entrada.aleros.longitud_corto == pytest.approx(
        a01.cabezal.entrada.aleros.longitud_corto, rel=REL)
    otra = replace(a01.geometria, longitud_calculada=replace(
        a01.geometria.longitud_calculada, talud=1.5))
    c15 = M9.cabezal_del_punto(punto=a01.punto_de_calculo,
                               resultado=a01.resultado, geometria=otra,
                               embocadura=a01.embocadura)
    assert c15.entrada.aleros.longitud_corto == pytest.approx(
        1.05 * 1.5 / math.cos(math.radians(30.0)), rel=REL)


def test_h5_el_paso_9_0_5_sustituye_el_relleno_y_los_espesores(a01, tmp_path):
    c = a01.cabezal
    p = next(x for x in c.pasos if x.codigo == "9.0.5")
    valores = {m.simbolo: m.valor for m in p.sustitucion}
    assert valores["rel_e"] == pytest.approx(c.entrada.cota_coronacion - BORDILLO,
                                             rel=REL)
    assert valores["rel_s"] == pytest.approx(c.salida.cota_coronacion - BORDILLO,
                                             rel=REL)
    assert valores["e_e + e_s"] == pytest.approx(0.60, rel=REL)
    dif = a01.geometria.longitud_calculada.longitud - c.longitud_entre_cabezales
    assert f"L_cab es {dif:.3f} m menor" in p.nota_del_proyecto
    # con espesores distintos en los dos extremos, el metrado suma los dos
    externos = _externos_json(tmp_path, {"puntos": {"A-01": {
        "cabezal_declarado": {"entrada": {"espesor_base_muro_m": 0.40}}}}})
    a = replace(a01, cabezal=None, bloqueos=list(a01.bloqueos))
    servicio._fase_9(a, externos)
    assert a.cabezal.longitud_metrado == pytest.approx(
        a.cabezal.longitud_entre_cabezales + 0.40 + 0.30, rel=REL)
    p2 = next(x for x in a.cabezal.pasos if x.codigo == "9.0.5")
    assert {m.simbolo: m.valor for m in p2.sustitucion}["e_e + e_s"] == \
        pytest.approx(0.70, rel=REL)


def test_h5_las_guardias_de_las_reglas_y_del_margen():
    reglas = dict(ca.valor("predimensionamiento_cabezal"))
    reglas["resguardo_agua_m"] = -0.10
    with con_valor("predimensionamiento_cabezal", reglas,
                   motivo="un resguardo negativo: la guardia de segunda linea"):
        with pytest.raises(DatoInvalidoError):
            M9.predimensionar_cabezal(extremo=_extremo(),
                                      embocadura=_embocadura(), talud=2.0)
    ext = _extremo(extremo="salida", cota_solera=99.0, cota_pie=99.0,
                   cota_clave_exterior=100.0, cota_agua=99.4,
                   cota_fondo_hoya=98.20, origen_socavacion="declarada")
    with con_valor("margen_zapata_bajo_socavacion_m", -0.10,
                   motivo="un margen negativo: la guardia de segunda linea"):
        with pytest.raises(DatoInvalidoError):
            M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                      talud=2.0)
    # el extremo bajo de la ventana (0, HEC-14 5.1.3) es valido: la zapata
    # baja HASTA la hoya, sin margen
    with declarados({"margen_zapata_bajo_socavacion_m": 0.0}):
        g = M9.predimensionar_cabezal(extremo=ext, embocadura=_embocadura(),
                                      talud=2.0)
    assert g.cota_desplante == pytest.approx(98.20, rel=REL)


def test_h5_los_mensajes_de_las_puertas_se_construyen():
    with pytest.raises(DatoInvalidoError, match="no es una dimension"):
        M9.predimensionar_cabezal(extremo=_extremo(), embocadura=_embocadura(),
                                  talud=2.0, declaradas={"altura": 2.0})
    with pytest.raises(DatoInvalidoError, match="se espera"):
        M9.predimensionar_cabezal(extremo=_extremo(), embocadura=_embocadura(),
                                  talud=2.0, tipo_declarado="mamposteria")
    with pytest.raises(DatoInvalidoError, match="tipo de cabezal"):
        M9.peralte_minimo_zapata("mamposteria")
    with con_valor("embocadura_cabezal", "caja_receptora",
                   motivo="una embocadura fuera del catalogo: la puerta"):
        with pytest.raises(DatoInvalidoError, match="se espera una de"):
            M9.embocadura_del_punto(esviaje_grados=0.0)
    # y la puerta del dato externo admite una dimension menor de 1 m
    assert M9.validar_cabezal_declarado({"espesor_losa_m": 0.25})[
        "entrada"]["espesor_losa_m"] == pytest.approx(0.25, rel=REL)


# ===========================================================================
# H6 - la longitud entre cabezales llega al relleno, y la de metrado
# ===========================================================================

def test_h6_a01_longitud_entre_cabezales_y_de_metrado(a01):
    """
    Relleno retenido: entrada 43.55 - 0.15 = 43.40; salida 43.4368 - 0.15 =
    43.2868. Bordes 44.20.
        L_cab = [9.60 + 2·(0.80 + 0.9132)] / cos 15 = 13.0264 · 1.035276
              = 13.486 m        (la FASE A daba 12.865, a la corona)
        L_metrado = 13.486 + 0.30 + 0.30 = 14.086 m
    """
    c = a01.cabezal
    s = c.salida
    esperado = (9.60 + 2.0 * ((44.20 - 43.40)
                              + (44.20 - (s.cota_coronacion - BORDILLO)))) \
        / math.cos(math.radians(15.0))
    assert c.longitud_entre_cabezales == pytest.approx(esperado, rel=REL)
    assert c.longitud_entre_cabezales == pytest.approx(13.486, abs=ABS_MM)
    assert c.longitud_metrado == pytest.approx(esperado + 0.60, rel=REL)
    p = next(x for x in c.pasos if x.codigo == "9.0.5")
    assert "trasdos" in p.resultado.procedencia
    assert "metrado" in p.que.lower()


def test_h6_el_docstring_dice_centimetros_y_el_relleno():
    doc = inspect.getdoc(M9.longitud_entre_cabezales)
    assert "milimetros" not in doc and "CENTIMETROS" in doc
    assert "MENOS EL BORDILLO" in doc
    doc_a = inspect.getdoc(M9.predimensionar_aleros)
    assert "MAS longitud" in doc_a


# ===========================================================================
# H7 - el umbral del tipo se mide sobre la altura total, y se dice
# ===========================================================================

def test_h7_el_aviso_del_tipo_por_altura_total(a01):
    avisos = [x for x in a01.avisos() if "altura TOTAL" in x]
    assert len(avisos) == 1 and "T7A-04" in avisos[0]
    assert a01.cabezal.entrada.tipo == a01.cabezal.salida.tipo == \
        M9.TIPO_VOLADIZO


def test_h7_con_altura_interior_de_0_90_ningun_cabezal_es_de_gravedad(c01, a01):
    """La menor altura total: 0.90 + pared + 0.30 + 0.15 + 0.80 > 2.0 m."""
    assert 0.90 + 0.30 + 0.15 + DESPLANTE_MIN > 2.0
    for p in (a01, c01):
        for g in p.cabezal.geometrias:
            assert g.altura_total > 2.0 and g.tipo == M9.TIPO_VOLADIZO


def test_h7_si_sale_de_gravedad_se_avisa_el_limite_del_ciclopeo(corrida_perfil):
    informe, externos = corrida_perfil
    # una copia del punto: el fixture de modulo no se toca
    a01 = replace(_punto(informe, "A-01"), cabezal=None,
                  bloqueos=list(_punto(informe, "A-01").bloqueos))
    reglas = dict(ca.valor("predimensionamiento_cabezal"))
    reglas["altura_max_gravedad_m"] = 2.5
    with declarados({"predimensionamiento_cabezal": reglas}):
        servicio._fase_9(a01, externos)
        c = a01.cabezal
    assert c.entrada.tipo == M9.TIPO_GRAVEDAD        # H_c = 2.25 <= 2.5
    assert c.salida.tipo == M9.TIPO_VOLADIZO         # H_c = 2.94 > 2.5
    aviso = next(x for x in c.avisos if "22.10.2.1" in x)
    assert "el de entrada" in aviso and "22.10.2.2" in aviso
    assert not any("altura TOTAL" in x for x in c.avisos)
    cita = construir().cita("E060.22.10.2#CICLOPEO")
    assert "muros de contención de gravedad" in cita.texto_literal.texto
    assert (cita.pagina_impresa, cita.pagina_pdf) == ("195", 195)


# ===========================================================================
# H8 y dudosos - E.050 por analogia, AASHTO 12.6.5, el piso de la zapata
# ===========================================================================

def test_h8_e050_26_2_es_N_flecha_para_un_cabezal_vial():
    assert not hasattr(cn, "PROFUNDIDAD_CIMENTACION_MIN_M")
    c = ca.CRITERIOS["profundidad_cimentacion_min_cabezal_m"]
    assert c.etiqueta == "N->" and c.nivel == ca.NIVEL_EXPEDIENTE
    assert "39.13.7" in c.justificacion and "Art. 1" in c.justificacion
    interp = construir().cita("E050.26.2#PROFUNDIDAD").interpretacion
    assert interp is not None
    assert any("edificaciones" in x for x in interp.en_contra)
    assert any("39.13.7" in x for x in interp.a_favor)


def test_h8_cb4_dice_por_analogia(a01):
    cb4 = next(v for v in a01.cabezal.verificaciones if v.codigo == "CB4.e")
    assert cb4.criterio_aplicado == "profundidad_cimentacion_min_cabezal_m"
    assert "ANALOGIA" in cb4.paso.umbral.aplicacion
    assert "EXIGENCIA de E.050" not in cb4.paso.umbral.aplicacion


def test_h8_la_hoja_de_ruta_declara_el_defecto_del_rotulo():
    texto = HOJA_DE_RUTA.read_text(encoding="utf-8")
    seccion = texto[texto.index("### 0.1 Jerarquía"):
                    texto.index("### 0.2")]
    assert "Defecto declarado (T-7a" in seccion
    assert "[N→]" in seccion


def test_dudoso_3_la_lectura_de_aashto_12_6_5_es_una_interpretacion():
    c = construir().cita("AASHTO_LRFD_9.12.6.5#ZAPATAS")
    assert c.interpretacion is not None
    assert "LEE incluida la zapata del cabezal" in c.interpretacion.texto
    assert ca.CRITERIOS["margen_zapata_bajo_socavacion_m"].etiqueta == "C"


def test_dudoso_4_el_piso_de_la_zapata_armada(a01):
    """
    E.060 15.7, pag. 138: «La altura de las zapatas, medida sobre el refuerzo
    inferior no debe ser menor de 300 mm para zapatas apoyadas sobre el
    suelo»; mas lo que queda debajo del eje de ese refuerzo: el
    recubrimiento con que se arma (70 mm aqui) y medio diametro de la mayor
    barra del catalogo (12.7 mm): 0.3827 m (`PISO_ARMADA`; era 0.37 m, y se
    declara donde se define). En la entrada de A-01 la regla H/10 daba
    2.25/10 = 0.225 m.
    """
    c = construir().cita("E060.15.7#PERALTE")
    assert "300 mm" in c.texto_literal.texto
    assert (c.pagina_impresa, c.pagina_pdf) == ("138", 138)
    k = ca.CRITERIOS["peralte_min_zapata_armada_m"]
    assert k.etiqueta == "N->" and k.valor == pytest.approx(0.30, rel=REL)
    piso, texto, cita = M9.peralte_minimo_zapata(M9.TIPO_VOLADIZO)
    assert piso == pytest.approx(PISO_ARMADA, rel=REL)
    assert cita == "E060.15.7#PERALTE"
    assert "recubrimiento con que se arma" in texto and "70.00 mm" in texto
    assert "12.70 mm" in texto and "eje de la capa inferior" in texto
    piso_g, _t, cita_g = M9.peralte_minimo_zapata(M9.TIPO_GRAVEDAD)
    assert piso_g == pytest.approx(0.30, rel=REL)
    assert cita_g == "E060.22.7.4#ZAPATA"
    e = a01.cabezal.entrada
    assert 2.25 / 10.0 < PISO_ARMADA
    assert e.espesor_zapata == pytest.approx(PISO_ARMADA, rel=REL)
    assert e.H == pytest.approx(2.25 - PISO_ARMADA, rel=REL)
    assert "15.7" in _dim(e, "espesor de la zapata").regla
    # a la salida H_c = 2.937 m: H/10 = 0.2937 sigue bajo el piso
    assert a01.cabezal.salida.espesor_zapata == pytest.approx(PISO_ARMADA,
                                                              rel=REL)


def test_dudoso_5_el_origen_de_h8_h6_no_se_verifico():
    j = ca.CRITERIOS["predimensionamiento_cabezal"].justificacion
    assert "no se pudo verificar" in j and "H/8 a H/6" in j


# ===========================================================================
# H9 - los detalles
# ===========================================================================

def test_h9_el_talon_con_b_declarado_es_derivado():
    g = M9.predimensionar_cabezal(extremo=_extremo(), embocadura=_embocadura(),
                                  talud=2.0,
                                  declaradas={"ancho_zapata_m": 2.0})
    t = _dim(g, "ancho del talon")
    assert t.origen == ORIGEN_DIMENSION_DERIVADA
    assert "ancho_zapata_m" in t.regla
    assert _dim(g, "ancho de la punta").origen == ORIGEN_DIMENSION_DERIVADA
    # sin nada declarado, ninguna es derivada
    g0 = M9.predimensionar_cabezal(extremo=_extremo(),
                                   embocadura=_embocadura(), talud=2.0)
    assert {d.origen for d in g0.dimensiones} == {ORIGEN_DIMENSION_REGLA}


def test_h9_el_json_no_lleva_un_criterio_vacio_con_cabezal_recto(
        corrida_perfil):
    informe, externos = corrida_perfil
    with declarados({"embocadura_cabezal": M6.EMBOCADURA_CABEZAL_RECTO}):
        recto = cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)
    j = cli._cabezal_del_punto_json(_punto(recto, "A-01"))
    assert j["embocadura"]["criterios"] == ["embocadura_cabezal"]


def test_h9_el_docstring_de_correr_cabezal_ya_no_habla_de_geometria_declarada():
    assert "la geometria declarada" not in inspect.getdoc(servicio.correr_cabezal)


def test_h9_el_aviso_dice_por_que_falta_la_socavacion(a01):
    """Con la etapa de la Fase 6 bloqueada, el motivo es el bloqueo y no un
    lecho que falta."""
    p = replace(a01, socavacion=None, cabezal=None,
                bloqueos=list(a01.bloqueos) + [Bloqueo(
                    fase=servicio.FASE_PROTECCION,
                    etapa=servicio.ETAPA_SOCAVACION_SALIDA,
                    tipo=TipoDeBloqueo.DATO_INVALIDO,
                    mensaje="dato invalido de prueba")])
    servicio._fase_9(p)
    aviso = next(x for x in p.cabezal.avisos if "sin socavacion" in x)
    assert "se detuvo" in aviso and "dato invalido de prueba" in aviso
    assert "material_lecho_salida" not in aviso
    # y sin bloqueo, el motivo es el que M6 dejo en la socavacion
    aviso_a01 = next(x for x in a01.avisos() if "sin socavacion" in x)
    assert a01.socavacion.motivo_no_estimada[:40] in aviso_a01


def test_h9_las_formulas_del_proyecto_no_llevan_una_cita_que_no_las_contiene(
        a01):
    for p in a01.cabezal.pasos:
        if p.fundamento_id in ("F9.CORONACION", "F9.ALEROS", "F9.LOSA",
                               "F9.LONGITUD"):
            assert p.formula_cita_id == "", p.codigo
            assert M9.NOTA_FORMULA_DEL_PROYECTO in p.nota_del_proyecto


def test_h9_la_escala_3_de_la_carta_12_no_tiene_banda():
    assert cn.BANDAS_ALETAS_CAJON_A1[
        "cajon_concreto_chaflan_aletas_184_esviaje_30"] == ()
    a1, _ = M9.filas_hds5_del_cajon(_embocadura(18.4))
    assert "cajon_concreto_chaflan_aletas_184_esviaje_30" not in a1
    assert "cajon_concreto_chaflan_aletas_184" in a1


def test_h9_el_recubrimiento_sobre_la_clave_no_se_apoya_en_aashto():
    j = ca.CRITERIOS["predimensionamiento_cabezal"].justificacion
    assert "12.6.6.3" not in j and "12 in" not in j
    assert "no un minimo de cobertura" in j


def test_h9_la_nota_del_angulo_dice_que_se_lee_antes_de_la_fase_4():
    v = ve.variable("angulo_aletas")
    assert v.consumido_por == ("M9_cabezal",)
    assert "ANTES de la Fase 4" in v.nota


def test_h9_la_coherencia_por_familia_equivale_a_la_forma(c01, corrida_perfil):
    """M2 da el marco solo a la Familia C: decidir por familia es decidir
    por forma, mientras eso se sostenga."""
    informe, _ = corrida_perfil
    for p in informe.puntos[:3]:
        assert all(m.forma is FormaSeccion.CIRCULAR
                   for m in M2.materiales_candidatos(p.punto_de_calculo))
    with declarados(DECLARACIONES_DEL_CAJON):
        assert all(m.forma is FormaSeccion.RECTANGULAR
                   for m in M2.materiales_candidatos(c01.punto_de_calculo))


# ===========================================================================
# H10 - «mas material» no es el lado seguro
# ===========================================================================

def test_h10_ninguna_frase_dice_que_mas_material_es_el_lado_seguro():
    j = ca.CRITERIOS["predimensionamiento_cabezal"].justificacion
    assert "no esconde ninguna falla" not in j
    assert "EMPEORA el deslizamiento" in j
    texto = DECISIONES.read_text(encoding="utf-8")
    ficha = texto[texto.index("## T7A-04"):texto.index("## T7A-05")]
    assert "empeora" in ficha and "T-7b" in ficha


# ===========================================================================
# Decisiones del dueño: la caja receptora (3) y la coherencia sin ruido
# ===========================================================================

def test_decision_3_la_familia_b_avisa_la_caja_receptora(corrida_perfil):
    informe, _ = corrida_perfil
    b01 = _punto(informe, "B-01")
    assert b01.embocadura is not None
    avisos = [x for x in b01.avisos() if "CAJA RECEPTORA" in x]
    assert len(avisos) == 1 and "T7A-02" in avisos[0]
    for id_punto in ("A-01", "A-02"):
        assert not any("CAJA RECEPTORA" in x
                       for x in _punto(informe, id_punto).avisos())


def test_la_coherencia_del_marco_no_es_un_aviso(c01):
    assert c01.coherencia_embocadura and "coherente" in \
        c01.coherencia_embocadura
    assert not any("coherente" in x for x in c01.avisos())
    lineas = cli._lineas_cabezal_del_punto(c01)
    assert sum("coherente" in x for x in lineas) == 1
    assert lineas[0].strip().startswith("Embocadura:")
    paso = next(x for x in c01.cabezal.pasos if x.codigo == "9.0.0")
    assert "coherente" in paso.nota_del_proyecto


# ===========================================================================
# Integracion (decision del dueño del 2026-11-13): el cabezal normal al eje
# es el de archivo en las tres familias, y el alero largo de un cruce esviado
# se acorta declarando un alfa menor de ese lado (aleros asimetricos)
# ===========================================================================

def test_integracion_el_alero_largo_de_c01_con_un_alfa_menor_declarado(
        c01, tmp_path):
    """
    C-01, theta = 30: con alfa = 45 el largo forma 75 grados con la bajada
    del talud (avance/cos 75). Declarado un alfa de 15 grados de ese lado,
    forma 45: avance/cos 45, y el corto no cambia (avance/cos 15).
    """
    externos = _externos_json(tmp_path, {"globales": {"TW_m": 0.3}, "puntos": {
        "C-01": {"Q_m3s": 0.85, "S_conducto": 0.004, "S_cauce": 0.006,
                 "cabezal_declarado": {"angulo_alero_largo_grados": 15.0}}}})
    p = replace(c01, cabezal=None, bloqueos=list(c01.bloqueos))
    with declarados(DECLARACIONES_DEL_CAJON):
        servicio._fase_9(p, externos)
    a = p.cabezal.entrada.aleros
    avance = (a.altura_inicial - a.altura_final) * 2.0
    assert a.angulo_largo_grados == pytest.approx(15.0, rel=REL)
    assert a.longitud_largo == pytest.approx(
        avance / math.cos(math.radians(45.0)), rel=REL)
    assert a.longitud_corto == pytest.approx(
        avance / math.cos(math.radians(15.0)), rel=REL)
    assert a.longitud_largo < c01.cabezal.entrada.aleros.longitud_largo
    d = _dim(p.cabezal.entrada, "angulo del alero largo")
    assert d.origen == "declarada" and d.unidad == "grados"
    assert _dim(p.cabezal.entrada, "longitud del alero largo (alfa + theta)"
                ).origen == ORIGEN_DIMENSION_DERIVADA
    # en un marco, el ke y la carta siguen siendo los del alfa de la regla
    aviso = next(x for x in p.cabezal.avisos if "asimetricos declarados" in x)
    assert "45 grados" in aviso and "Tablas A.1 y C.2" in aviso


def test_integracion_el_aviso_del_desnivel_nombra_el_remedio(a01):
    aviso = next(x for x in a01.avisos() if "Δz" in x)
    assert "angulo_alero_largo_grados" in aviso
    assert "normal al eje es el de archivo en las tres familias" in aviso
    p = next(x for x in a01.cabezal.pasos if x.codigo == "9.0.3e")
    assert "angulo_alero_largo_grados" in p.nota_del_proyecto


@pytest.mark.parametrize("malo", [90.0, -1.0, float("nan"), "15", True])
def test_integracion_el_angulo_declarado_pasa_por_la_puerta(malo):
    with pytest.raises(DatoInvalidoError):
        M9.validar_cabezal_declarado({"angulo_alero_largo_grados": malo})
    n = M9.validar_cabezal_declarado({"salida": {
        "angulo_alero_largo_grados": 0.0}})
    assert n["salida"]["angulo_alero_largo_grados"] == pytest.approx(
        0.0, abs=ABS_CERO)


def test_integracion_un_alfa_largo_declarado_que_no_alcanza_es_limite():
    with pytest.raises(LimiteNumericoError) as exc:
        M9.predimensionar_cabezal(
            extremo=_extremo(), embocadura=_embocadura(30.0, esviaje=30.0),
            talud=2.0, declaradas={"angulo_alero_largo_grados": 60.0})
    assert exc.value.campo == "cabezal_declarado.angulo_alero_largo_grados"
    assert "angulo_alero_largo_grados" in str(exc.value)
