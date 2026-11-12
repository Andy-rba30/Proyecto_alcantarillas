"""
Aceptacion de T-4 de la cadena T: material, durabilidad y topes.

Cierra, en el orden del prompt:

  (1) INF-5.1.17  el TMC y el HDPE se descartaban por no tener espesor de
      INF-3.3.4   pared; ahora llegan a 7.A (recubrimiento minimo) y a V7;
  (2) INF-3.3.1   el tope de diametro sale de la serie de la norma de
                  producto, y la disponibilidad de mercado solo puede bajarlo;
  (3) INF-3.2.4   'v_max_tmc' es [A] con ventana y 'v_max_hdpe' sigue [C],
                  con la prohibicion citada de donde la fuente la escribe;
  (4) INF-3.3.1   la matriz de durabilidad es un filtro real de
                  `M2.materiales_candidatos`, con entradas opcionales;
      INF-5.1.9   `sucs_fundacion` tiene consumidor: el aviso de marco;
  (5) INF-3.2.1   el n del HDPE deja de ser una analogia con el concreto;
      INF-5.1.16  la constante del diametro de selva alta se conserva sin
                  consumidor, y se dice.

COMO SE ESCRIBIO, que la regla 4 de la cadena pide decirlo: el registro
normativo y las fichas de los criterios se escribieron ANTES que este archivo
--las citas habia que leerlas en el PDF para saber que se podia afirmar--, y
los tests despues, contra lo que las fuentes dicen. No hay por tanto una
medida de «rojo antes de tocar codigo» por test; lo que si se midio es que
este archivo no se puede ni recolectar sobre `87d1ce7` (sus imports no
existen) y que cada dorado de aqui se calcula a mano en el propio test, sin
leer el numero del codigo que mide.

LOS ESPESORES DEL EXPEDIENTE SE MIDEN SIN LA DECLARACION DE `conftest`. La
suite declara para toda corrida un espesor sintetico de TMC y de HDPE (ver
`conftest.py`), y una entrada declarada gana a la derivada: los tests de aqui
que miden lo que el ARCHIVO dice la retiran con la fixture `del_expediente`.
"""

import ast
import json
import math
from dataclasses import replace
from pathlib import Path

import pytest

import cli
from conftest import CLAVE_ESPESOR_PARED
from src import anticipo
from src import constantes_normativas as CN
from src import criterios_adoptados as ca
from src import servicio
from src.constantes_fisicas import PULGADA_EN_MM
from src.dominios import MILIMETROS_POR_METRO
from src.modelos import (DURABILIDAD_SIN_ENSAYOS, CriterioPendienteError,
                         DatoFaltanteError, DatoInvalidoError,
                         DictamenDurabilidad, DisenoNoFactibleError,
                         EfectoDeDurabilidad, EnsayosDurabilidad, Familia,
                         ReglaDeDurabilidad, SeccionCircular, TipoDeVeredicto,
                         TipoMaterial,
                         Verificacion)
from src.modulos import M11_reporte as M11
from src.modulos import M2_material as M2
from src.modulos import M5_verificaciones as M5
from src.modulos import M7_geometria as M7
from src.modulos import M9_cabezal as M9
from src.modulos import MD
from src.modulos.M0_carga import cargar_puntos
from src.normativa import fuentes, registro
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import con_valor, declarados, sin_valor
from tests.test_M5_verificaciones import _punto, _resultado

RAIZ = Path(__file__).resolve().parent.parent
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
ENTRADAS_ANCHAS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"
LUZ = 2.75

TMC, HDPE, CONCRETO = (TipoMaterial.TMC, TipoMaterial.HDPE,
                       TipoMaterial.CONCRETO_REFORZADO)

# Dorados A MANO, cada uno con la cuenta al lado.
T_TMC = (13 + 2.01) / 1000                   # profundidad 13 mm + plancha 2.01 mm
T_HDPE = {900: (42.5 * 25.4 - 900) / 2000,   # Max OD 42.5 in -> 0.08975 m
          1050: (48.0 * 25.4 - 1050) / 2000,  # Max OD 48.0 in -> 0.0846 m
          1200: (55.0 * 25.4 - 1200) / 2000}  # Max OD 55.0 in -> 0.0985 m
V_15_FT_S = 15 * 0.3048                      # 4.572 m/s
V_10_FT_S = 10 * 0.3048                      # 3.048 m/s

# El espesor del HDPE se guarda redondeado a 5 decimales de metro (centesimas
# de milimetro): la cuenta desde la tabla coincide dentro de ese redondeo.
ABS_REDONDEO_DEL_ESPESOR = 1e-5
# U de V7 se recalcula aqui con la misma formula y otro orden de operaciones.
REL_RECALCULO = 1e-9
# El diametro limite del factor de flexibilidad se compara al milimetro.
ABS_UN_MILIMETRO = 1.0


@pytest.fixture
def del_expediente():
    """Retira el espesor sintetico de `conftest`: queda el del archivo."""
    ca.quitar_valor_dinamico(CLAVE_ESPESOR_PARED)
    yield


@pytest.fixture(scope="module")
def reg():
    return registro.construir()


@pytest.fixture(scope="module")
def puntos():
    return {p.id: p for p in cargar_puntos(CSV_EJEMPLO)}


def _externos(tmp_path, extra=None, **banderas):
    """Los datos anchos de la linea base, mas lo que el test añada."""
    datos = json.loads(ENTRADAS_ANCHAS.read_text(encoding="utf-8"))
    for seccion, campos in (extra or {}).items():
        if seccion == "globales":
            datos.setdefault("globales", {}).update(campos)
        else:
            for id_punto, valores in campos.items():
                datos.setdefault("puntos", {}).setdefault(id_punto, {}).update(valores)
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    base = {"luz_m": LUZ, "TW_m": None, "longitud_m": None,
            "L_hidraulico_m": None, "categoria_tr": None}
    base.update(banderas)
    return cli.cargar_datos_externos(ruta, base)


def _corrida(tmp_path, extra=None):
    return cli.correr(CSV_EJEMPLO, _externos(tmp_path, extra),
                      alcance=cli.ALCANCE_PERFIL)


def _por_id(informe):
    return {p.punto.id: p for p in informe.puntos}


# ===========================================================================
# (1) INF-5.1.17 - el espesor de pared del TMC y del HDPE
# ===========================================================================

def test_el_espesor_del_tmc_es_la_profundidad_de_la_corrugacion_mas_la_plancha(
        del_expediente, reg):
    """
    El diametro nominal del tubo corrugado se mide en la cresta INTERIOR (M 36
    num. 8.1.1): lo que separa el diametro hidraulico del exterior es la
    profundidad de la corrugacion mas el espesor de la plancha. Con la
    adopcion del archivo --68 por 13 mm, 2.01 mm-- son 15.01 mm, y los dos
    sumandos se leen de las tablas del registro, no del codigo que se mide.
    """
    assert ca.valor(M2.CRITERIO_CALIBRE_TMC) == "68x13/2.01"
    profundidad = reg.tabla("AASHTO_M36.T1").fila("c68x13").valores[
        "profundidad_nominal_mm"]
    plancha = next(f.valores["t_mm"] for f in reg.tabla("ASTM_A796.T5").filas
                   if f.etiqueta_literal == "2.01")
    assert (profundidad, plancha) == (13, pytest.approx(2.01, rel=REL_TRANSPORTE))
    t = M2.espesor_pared(M2.catalogo(TMC), 0.90)
    assert t == pytest.approx(T_TMC, rel=REL_TRANSPORTE)
    assert t == pytest.approx((profundidad + plancha) / MILIMETROS_POR_METRO,
                              rel=REL_TRANSPORTE)
    # La tabla derivada cubre los diametros en que la corrugacion es estandar
    # y ninguno mas: 900 a 2100 mm con la de 68 por 13.
    por_diametro = M2.espesor_pared_de_tmc()
    assert set(por_diametro) == set(CN.DIAMETROS_ESTANDAR_TMC["68x13"])
    assert min(por_diametro) == 300 and max(por_diametro) == 2100


def test_el_espesor_del_hdpe_sale_del_diametro_exterior_maximo_de_LRFD(
        del_expediente, reg):
    """
    M 294 no tabula la altura del perfil corrugado (su 7.2.2 da el espesor
    minimo de la pared interior). AASHTO LRFD si tabula el diametro exterior
    MAXIMO del producto en la Table A12-11, y de ahi sale t = (OD - D)/2:
    es el lado seguro para la clave fisica y para el volumen de V7.
    """
    tabla = reg.tabla("AASHTO_LRFD_9.TA12-11")
    hdpe = M2.catalogo(HDPE)
    for d_mm, esperado in T_HDPE.items():
        nominal_in = round(d_mm / PULGADA_EN_MM / 6) * 6      # 36, 42, 48
        fila = next(f for f in tabla.filas
                    if f.valores["nominal_in"] == nominal_in)
        de_la_tabla = (fila.valores["od_max_in"] * PULGADA_EN_MM - d_mm) \
            / (2 * MILIMETROS_POR_METRO)
        t = M2.espesor_pared(hdpe, d_mm / MILIMETROS_POR_METRO)
        assert t == pytest.approx(esperado, rel=REL_TRANSPORTE), d_mm
        assert t == pytest.approx(de_la_tabla, abs=ABS_REDONDEO_DEL_ESPESOR), d_mm


@pytest.mark.parametrize("D", [1.35, 1.50])
def test_el_hdpe_de_1350_y_1500_no_tiene_fila_y_no_se_interpola(
        del_expediente, D):
    """
    La Table A12-11 termina en 48 in. Los dos ultimos tamaños de la serie del
    HDPE quedan sin fuente para su diametro exterior: `DatoFaltanteError` que
    nombra la fila, nunca la fila vecina ni una extrapolacion.
    """
    with pytest.raises(DatoFaltanteError) as exc:
        M2.espesor_pared(M2.catalogo(HDPE), D)
    assert str(round(D * MILIMETROS_POR_METRO)) in exc.value.campo
    assert "A12-11" in str(exc.value)
    assert "no se interpola" in str(exc.value)


def test_una_entrada_tmc_declarada_gana_a_la_derivada():
    """
    El proyectista que tiene la ficha del fabricante la declara, y esa
    entrada gana: es lo que hace `conftest` para la suite (0.013 m).
    """
    assert M2.espesor_pared(M2.catalogo(TMC), 0.90) == pytest.approx(
        0.013, rel=REL_TRANSPORTE)


def test_otra_corrugacion_mueve_el_espesor_y_el_tope_del_tmc(del_expediente):
    """
    'corrugacion_y_espesor_tmc' es [A] y se barre dentro de su conjunto
    cerrado. Con 75 por 25 mm y 2.77 mm el espesor es 27.77 mm y el tope
    sube a 3.60 m, que es el ultimo diametro en que esa corrugacion es
    estandar y el ultimo de la serie de M 36.
    """
    ficha = ca.criterio(M2.CRITERIO_CALIBRE_TMC)
    assert ficha.etiqueta == "A" and "75x25/2.77" in ficha.sensibilidad
    assert tuple(ficha.sensibilidad) == tuple(CN.TMC_PLANCHA_CORRUGADA)
    with declarados({M2.CRITERIO_CALIBRE_TMC: "75x25/2.77"}):
        tmc = M2.catalogo(TMC)
        assert M2.espesor_pared(tmc, 0.90) == pytest.approx(
            (25 + 2.77) / 1000, rel=REL_TRANSPORTE)
        assert tmc.D_max == pytest.approx(3.60, rel=REL_TRANSPORTE)
        assert tmc.D_max_criterio == M2.CRITERIO_D_MAX_NORMA
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(M2.CRITERIO_CALIBRE_TMC, "68x13/9.99")


@pytest.mark.parametrize("id_punto", ["A-01", "B-01"])
@pytest.mark.parametrize("tipo", [TMC, HDPE])
def test_tmc_y_hdpe_llegan_a_7A_y_a_V7_con_los_valores_del_archivo(
        del_expediente, puntos, id_punto, tipo):
    """
    Lo que INF-5.1.17 dice que no pasaba: hasta T-4 los dos materiales se
    detenian en `DatoFaltanteError` de 'espesor_pared_conducto' antes de la
    clave fisica (7.A) y del volumen desplazado (V7). Aqui se les llama con
    los valores del archivo, sobre los dos puntos de tubo del fixture, y los
    dos numeros que dependen del espesor se recalculan a mano.
    """
    punto, material = puntos[id_punto], M2.catalogo(tipo)
    seccion = SeccionCircular(D=0.90)
    t = T_TMC if tipo is TMC else T_HDPE[900]

    tamizado = M7.tamizado_rasante(punto=punto, material=material,
                                   seccion=seccion, HW=0.80)
    assert tamizado.espesor_pared == pytest.approx(t, rel=REL_TRANSPORTE)
    assert tamizado.cota_clave == pytest.approx(
        punto.cota_terreno + 0.90 + t, rel=REL_TRANSPORTE)

    v7 = M5.v7_flotacion(punto=punto, material=material, seccion=seccion,
                         resultado=_resultado())
    U = 9.81 * math.pi / 4 * (0.90 + 2 * t) ** 2
    assert v7.codigo == "V7"
    assert v7.valor_admisible == pytest.approx(U, rel=REL_RECALCULO)
    # Y el paso dice de donde salio t.
    eleccion = next(e for e in v7.paso.elecciones
                    if e.fundamento_id == "F3.D_EXTERIOR")
    assert eleccion.clave_criterio == (M2.CRITERIO_CALIBRE_TMC if tipo is TMC
                                       else M2.CRITERIO_ESPESOR_PARED)
    assert eleccion.cita_id in ("AASHTO_M36.T1", "AASHTO_LRFD_9.TA12-11")


def test_la_corrugacion_del_tmc_se_puede_barrer_por_la_puerta_de_siempre(tmp_path):
    """
    El prompt pide que el calibre sea un [A] BARRIBLE. Entra por la misma
    puerta que cualquier barrido (`barrido.barrer`), un valor fuera del
    conjunto no corre nada, y con las dos planchas el fixture adopta lo
    mismo: el concreto cierra antes de que el TMC entre en juego.
    """
    from src import barrido
    externos = _externos(tmp_path)
    r = barrido.barrer(CSV_EJEMPLO, externos, cli.ALCANCE_PERFIL,
                       M2.CRITERIO_CALIBRE_TMC, ("68x13/2.01", "75x25/2.77"),
                       nota="barrido del calibre del TMC", volcar=cli.informe_json)
    assert len(r.corridas) == 2
    for fila in r.filas:
        if fila.id_punto in ("A-01", "A-02"):
            assert fila.dimensionado and fila.seccion == "Ø 0.90 m"
            assert "oncreto" in fila.material
    with pytest.raises(ValueError):
        barrido.verificar_valores(M2.CRITERIO_CALIBRE_TMC, ("68x13/9.99",),
                                  nota="fuera del conjunto")


def test_el_minimo_de_eg2013_del_hdpe_participa_y_lo_que_gobierna_es_aashto(
        del_expediente):
    """
    El prompt pide comprobar que H_RELLENO_MIN del HDPE (0.30 m, EG-2013
    508.07) «se aplica de verdad». SE APLICA Y NO GOBIERNA, y hay que
    decirlo tal cual: 7.A toma el MAYOR entre ese minimo y la cobertura de
    AASHTO, que para el termoplastico es 0.61 m bajo pavimento (0.3048 m
    sin pavimento: lo mide el bucle de abajo). El 0.30 m entra en la
    comparacion --la memoria imprime los dos-- y pierde en todo diametro.
    Para el TMC el EG-2013 no fija minimo y solo queda AASHTO.
    """
    hdpe = M2.catalogo(HDPE)
    assert hdpe.h_relleno_min_eg2013 == pytest.approx(
        CN.H_RELLENO_MIN["hdpe"], rel=REL_TRANSPORTE)
    assert hdpe.h_relleno_min_eg2013 == pytest.approx(0.30, rel=REL_TRANSPORTE)
    for D in (0.90, 1.05, 1.20):
        h_rec, cual = M7.altura_recubrimiento(material=hdpe,
                                              seccion=SeccionCircular(D=D))
        assert h_rec > hdpe.h_relleno_min_eg2013
        assert cual.startswith(M7.MINIMO_AASHTO)
        assert M7.MINIMO_EG2013 in cual and "0.300" in cual
    assert h_rec == pytest.approx(0.6096, rel=REL_TRANSPORTE)     # con pavimento
    with declarados({"condicion_pavimento": "no_pavimentado"}):
        sin_pavimento, cual = M7.altura_recubrimiento(
            material=hdpe, seccion=SeccionCircular(D=0.90))
    assert sin_pavimento == pytest.approx(0.3048, rel=REL_TRANSPORTE)
    assert sin_pavimento > hdpe.h_relleno_min_eg2013 and cual.startswith(M7.MINIMO_AASHTO)
    _h, cual_tmc = M7.altura_recubrimiento(material=M2.catalogo(TMC),
                                           seccion=SeccionCircular(D=0.90))
    assert "no fija minimo" in cual_tmc


def test_procedencia_del_espesor_nombra_el_origen_de_cada_material(del_expediente):
    """El texto, la cita y el criterio que V7 imprime junto a t."""
    assert M2.procedencia_del_espesor(M2.catalogo(TMC))[1:] == (
        "AASHTO_M36.T1", M2.CRITERIO_CALIBRE_TMC)
    assert M2.procedencia_del_espesor(M2.catalogo(HDPE))[1:] == (
        "AASHTO_LRFD_9.TA12-11", M2.CRITERIO_ESPESOR_PARED)
    texto, cita, clave = M2.procedencia_del_espesor(M2.catalogo(CONCRETO))
    assert "M 170M" in texto and cita == "" and clave == M2.CRITERIO_ESPESOR_PARED


# ===========================================================================
# (2) INF-3.3.1 - el tope de diametro
# ===========================================================================

def test_el_tope_de_la_serie_se_deriva_de_la_ultima_fila_de_cada_norma(reg):
    """
    'D_max_norma_producto' [C] no se escribe: en TMC y HDPE es el mayor
    diametro designado de su tabla del registro. EN CONCRETO NO (auditoria
    de T-4, H2): la serie de M 170M llega a 3600 mm, pero por encima de 2700
    mm sus tablas llevan rayas y remiten a la Seccion 7.2 --diseño especial,
    con la pared que de el fabricante--. El tope es el ultimo diametro con
    diseño estandar, y coincide con la ultima fila de pared B declarada.
    """
    ficha = ca.criterio(M2.CRITERIO_D_MAX_NORMA)
    assert ficha.etiqueta == "C"
    esperado = {
        material: max(f.valores["dn_mm"] for f in reg.tabla(tabla).filas)
        / MILIMETROS_POR_METRO
        for material, tabla in (("tmc", "AASHTO_M36.T6"),
                                ("hdpe", "AASHTO_M294_TRAD.T7.2.2"))}
    esperado["concreto_reforzado"] = \
        CN.DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM / MILIMETROS_POR_METRO
    assert ficha.valor == pytest.approx(esperado, rel=REL_TRANSPORTE)
    assert esperado == pytest.approx(
        {"concreto_reforzado": 2.70, "tmc": 3.60, "hdpe": 1.50}, rel=REL_TRANSPORTE)
    # La serie sigue por encima, y la pared declarada termina donde el tope.
    serie = [f.valores["dn_mm"] for f in reg.tabla("AASHTO_M170M.T5").filas]
    assert max(serie) == 3600 and 2700 in serie
    pared_b = ca.CRITERIOS[CLAVE_ESPESOR_PARED].valor["concreto_reforzado"]
    assert max(pared_b) == CN.DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM
    assert "7.2.1" in CN.NUMERAL_DIAMETRO_MAX_ESTANDAR_M170M
    assert reg.cita("AASHTO_M170M.7.2.2").pagina_pdf == 13
    assert "wall thickness" in reg.cita("AASHTO_M170M.7.2.2").texto_literal.texto


def test_el_tope_efectivo_y_el_criterio_que_lo_fija():
    """
    2.70 m concreto (ultimo con diseño estandar), 2.10 m TMC (corrugacion
    adoptada), 1.50 m HDPE (serie). NINGUNO de los tres se movio respecto de
    antes de T-4; lo que cambio es que ahora tienen de donde salir.
    """
    assert M2.tope_de_diametro(CONCRETO)[:2] == (
        pytest.approx(2.70, rel=REL_TRANSPORTE), M2.CRITERIO_D_MAX_NORMA)
    assert M2.tope_de_diametro(TMC)[:2] == (
        pytest.approx(2.10, rel=REL_TRANSPORTE), M2.CRITERIO_CALIBRE_TMC)
    assert M2.tope_de_diametro(HDPE)[:2] == (
        pytest.approx(1.50, rel=REL_TRANSPORTE), M2.CRITERIO_D_MAX_NORMA)
    assert M2.tope_de_diametro(TMC)[2] == M2.ROTULO_TOPE_DE_CORRUGACION
    assert M2.tope_de_diametro(HDPE)[2] == M2.ROTULO_TOPE_DE_SERIE


def test_la_disponibilidad_local_es_opcional_y_solo_puede_bajar_el_tope():
    """
    'D_max_catalogo' queda como lo que su nombre dice: [A], opcional, sin
    valor. Declarado por debajo de la serie, gobierna y V9 lo cita; por
    encima, se rechaza --un diametro que la norma no tabula no es un
    producto de catalogo bajo esa norma--; y un material que la declaracion
    no nombra conserva su tope.
    """
    ficha = ca.criterio(M2.CRITERIO_D_MAX_CATALOGO)
    assert ficha.valor is None and ficha.opcional and ficha.etiqueta == "A"
    assert ca.valor_si_declarado(M2.CRITERIO_D_MAX_CATALOGO) is None
    with declarados({M2.CRITERIO_D_MAX_CATALOGO: {"concreto_reforzado": 2.40}}):
        tope, criterio, _rotulo = M2.tope_de_diametro(CONCRETO)
        assert (tope, criterio) == (pytest.approx(2.40, rel=REL_TRANSPORTE),
                                    M2.CRITERIO_D_MAX_CATALOGO)
        assert M2.tope_de_diametro(HDPE)[0] == pytest.approx(1.50, rel=REL_TRANSPORTE)
        v9 = M5.v9_disponibilidad_diametro(D=2.55, material=M2.catalogo(CONCRETO))
        assert not v9.cumple
        assert v9.criterio_aplicado == M2.CRITERIO_D_MAX_CATALOGO
    with declarados({M2.CRITERIO_D_MAX_CATALOGO: {"hdpe": 1.80}}):
        with pytest.raises(DatoInvalidoError) as exc:
            M2.tope_de_diametro(HDPE)
        assert exc.value.campo == M2.CRITERIO_D_MAX_CATALOGO
        assert "solo puede BAJAR" in exc.value.motivo
    # La del TMC se compara contra el tope de la CORRUGACION, no el de la serie.
    with declarados({M2.CRITERIO_D_MAX_CATALOGO: {"tmc": 2.40}}):
        with pytest.raises(DatoInvalidoError):
            M2.tope_de_diametro(TMC)


def test_la_progresion_del_concreto_termina_en_el_ultimo_diseño_estandar():
    """
    El catalogo del concreto NO recorre los diseños especiales de 2850 a
    3600 mm, y cada escalon que recorre tiene su pared declarada: ningun
    escalon del concreto puede detenerse por falta de espesor.
    """
    D, recorrido = M2.siguiente_diametro(CONCRETO), []
    while D is not None:
        recorrido.append(round(D * MILIMETROS_POR_METRO))
        D = M2.siguiente_diametro(CONCRETO, D)
    assert recorrido[0] == 900 and recorrido[-1] == 2700
    pared_b = ca.CRITERIOS[CLAVE_ESPESOR_PARED].valor["concreto_reforzado"]
    assert recorrido == sorted(pared_b)


# ===========================================================================
# (3) INF-3.2.4 - v_max de TMC y de HDPE
# ===========================================================================

def test_v_max_tmc_es_A_con_ventana_y_v_max_hdpe_sigue_C():
    """
    La asimetria es deliberada: la fuente PROHIBE el termoplastico en
    abrasion severa y al metal no le fija limite. Los dos numeros coinciden
    (15 ft/s) y no son la misma cosa. La ventana del TMC va de 10 ft/s
    (WSDOT §3-3.5) al valor adoptado; el techo NO es 4.6.
    """
    tmc, hdpe = ca.criterio("v_max_tmc"), ca.criterio("v_max_hdpe")
    assert tmc.etiqueta == "A" and hdpe.etiqueta == "C"
    assert tmc.valor == pytest.approx(V_15_FT_S, rel=REL_TRANSPORTE)
    assert hdpe.valor == pytest.approx(V_15_FT_S, rel=REL_TRANSPORTE)
    assert tmc.sensibilidad == pytest.approx((V_10_FT_S, V_15_FT_S), rel=REL_TRANSPORTE)
    assert tmc.nivel == ca.NIVEL_PERFIL and tmc.resolucion is not None
    # Lo que el dictamen mando retirar de la ficha del TMC.
    for campo in (tmc.justificacion, tmc.fuente, tmc.concepto):
        assert "conservador" not in campo.lower()
        assert "exige mayor calibre" not in campo.lower()
    assert "NINGUNA NORMA NI FUENTE TECNICA FIJA EL VALOR COMO LIMITE" in tmc.fuente
    # La prohibicion del HDPE se cita del §8-3.3; de la tabla, solo el umbral.
    assert "WSDOT_HM.8-3.3#SEVERA" in hdpe.fuente
    assert "LA TABLA NO PROHIBE NADA AL TERMOPLASTICO" in hdpe.fuente
    # Los dos cortes de la tabla, declarados en SI.
    assert "1.829" in tmc.justificacion and "4.572" in tmc.justificacion


def test_la_puerta_de_v_max_tmc_aplica_la_ventana():
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico("v_max_tmc", 4.6)
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico("v_max_tmc", 3.0)
    with declarados({"v_max_tmc": 3.5}):
        assert ca.valor("v_max_tmc") == pytest.approx(3.5, rel=REL_TRANSPORTE)


@pytest.mark.parametrize("tipo, etiqueta, debe_decir, no_debe_decir", [
    (TMC, "[A]", "ninguna fuente fija este valor como limite", "[C]"),
    (HDPE, "[C]", "§8-3.3", "[A]"),
])
def test_el_paso_de_v3_no_presenta_la_adopcion_del_tmc_como_limite_de_la_fuente(
        tipo, etiqueta, debe_decir, no_debe_decir):
    v3 = M5.v3_velocidad_maxima(material=M2.catalogo(tipo),
                                resultado=_resultado(V_erosion=2.0))
    (eleccion,) = v3.paso.elecciones
    assert etiqueta in eleccion.de_donde and no_debe_decir not in eleccion.de_donde
    assert debe_decir in eleccion.de_donde + " " + eleccion.por_que
    if tipo is TMC:
        assert eleccion.entre == (f"{V_10_FT_S} m/s", f"{V_15_FT_S} m/s")
        assert "no sustituye la proteccion" in eleccion.por_que


# ===========================================================================
# (5) INF-3.2.1 - el n de Manning del HDPE
# ===========================================================================

def test_el_n_del_hdpe_sale_de_HDS5_y_no_de_la_analogia_con_el_concreto(reg):
    ficha = ca.criterio("n_manning_hdpe")
    fila = reg.tabla("HDS5_3ED.TB.1").fila("polietileno_corrugado_liso")
    assert ficha.etiqueta == "C"
    assert ficha.valor == pytest.approx(
        (fila.valores["n_min"], fila.valores["n_max"]), rel=REL_TRANSPORTE)
    assert ficha.valor == pytest.approx((0.009, 0.015), rel=REL_TRANSPORTE)
    assert ficha.resolucion.tablas == ("HDS5_3ED.TB.1",)
    assert ficha.resolucion.fila_id == "polietileno_corrugado_liso"
    hdpe, concreto = M2.catalogo(HDPE), M2.catalogo(CONCRETO)
    assert (hdpe.n_min, hdpe.n_max) == pytest.approx((0.009, 0.015), rel=REL_TRANSPORTE)
    assert hdpe.n_min < concreto.n_min and hdpe.n_max > concreto.n_max


# ===========================================================================
# (4) INF-3.3.1 - la matriz de durabilidad
# ===========================================================================

def _excluidos(punto, **ensayos):
    return M2.matriz_durabilidad(punto, EnsayosDurabilidad(**ensayos)).excluidos


def test_sin_ensayos_la_matriz_no_actua_y_lo_dice():
    punto = _punto()
    for ensayos in (None, EnsayosDurabilidad()):
        d = M2.matriz_durabilidad(punto, ensayos)
        assert not d.aplicada and d.excluidos == () and d.pasos == ()
        assert d.resumen == DURABILIDAD_SIN_ENSAYOS
        assert DURABILIDAD_SIN_ENSAYOS == \
            "durabilidad: sin ensayos, matriz no aplicada"
        assert [m.tipo for m in M2.materiales_candidatos(punto, d)] == \
            [m.tipo for m in M2.materiales_candidatos(punto)] == \
            list(M2.tipos_candidatos(punto))


@pytest.mark.parametrize("pH, excluye, exige", [
    (4.9, True, False),      # fuera del intervalo: WSDOT §8-5.1
    (5.0, False, True),      # el borde es admisible, y pide proteccion
    (5.7, False, True),      # menor de 5.8: EG-2013 507.10
    (5.8, False, False),     # el borde de la proteccion no la exige
    (7.0, False, False),
    (8.5, False, False),
    (8.6, True, False),
])
def test_el_pH_excluye_el_tmc_fuera_del_intervalo_y_pide_proteccion_bajo_5_8(
        pH, excluye, exige):
    d = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(pH=pH))
    assert (TMC in d.excluidos) is excluye
    assert d.excluidos in ((), (TMC,))            # nunca concreto ni HDPE
    exigencias = [r for r in d.reglas
                  if r.efecto is EfectoDeDurabilidad.EXIGE and r.ensayo == "pH"]
    assert bool(exigencias) is exige
    if exige:
        assert exigencias[0].material is TMC
        assert exigencias[0].cita_ids == ("EG2013.507.10",)
    paso = d.pasos[0]
    assert paso.fundamento_id == "F3.DUR.PH"
    assert paso.umbral.cita_id == "WSDOT_HM.8-5.1#PH"
    assert paso.umbral.criterio_aplicado == M2.CRITERIO_DURABILIDAD_TMC


@pytest.mark.parametrize("rho, excluye", [(999.0, True), (1000.0, False),
                                         (5000.0, False)])
def test_la_resistividad_baja_excluye_el_tmc(rho, excluye):
    d = M2.matriz_durabilidad(_punto(),
                              EnsayosDurabilidad(resistividad_ohm_cm=rho))
    assert (d.excluidos == (TMC,)) is excluye
    paso = d.pasos[0]
    assert paso.fundamento_id == "F3.DUR.RESISTIVIDAD"
    assert paso.veredicto.margen == pytest.approx(rho - 1000.0, rel=REL_TRANSPORTE)


def test_los_umbrales_del_tmc_son_C_y_se_pueden_endurecer():
    """
    Los tres numeros son de WSDOT (§8-5.1 y §8-5.2) y viven en un criterio
    [C] con ventana por campo: el proyectista puede subir el pH minimo hasta
    el 5.8 de EG-2013 y entonces un pH de 5.5 excluye.
    """
    ficha = ca.criterio(M2.CRITERIO_DURABILIDAD_TMC)
    assert ficha.etiqueta == "C"
    assert ficha.valor == pytest.approx(
        {"pH_min": 5.0, "pH_max": 8.5, "resistividad_min_ohm_cm": 1000.0},
        rel=REL_TRANSPORTE)
    assert CN.PH_MIN_AGUA_TMC_SIN_PROTECCION == pytest.approx(5.8, rel=REL_TRANSPORTE)
    assert _excluidos(_punto(), pH=5.5) == ()
    endurecido = {**ficha.valor, "pH_min": 5.8}
    with declarados({M2.CRITERIO_DURABILIDAD_TMC: endurecido}):
        assert _excluidos(_punto(), pH=5.5) == (TMC,)
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(M2.CRITERIO_DURABILIDAD_TMC,
                                     {**ficha.valor, "pH_min": 4.0})


@pytest.mark.parametrize("campo, valor", [
    ("resistividad_min_ohm_cm", 0.0), ("resistividad_min_ohm_cm", 500.0),
    ("pH_max", 14.0), ("pH_max", 9.0), ("pH_min", 4.9),
])
def test_los_umbrales_del_tmc_no_se_pueden_relajar_por_la_puerta(campo, valor):
    """
    H4 de la auditoria: la ficha decia «solo se puede endurecer» y la puerta
    aceptaba resistividad minima 0 o 500 y pH maximo 14, que APAGAN el
    filtro. Cada ventana va ahora del valor de la fuente hacia el lado
    exigente, y endurecer sigue entrando.
    """
    ficha = ca.criterio(M2.CRITERIO_DURABILIDAD_TMC)
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(M2.CRITERIO_DURABILIDAD_TMC,
                                     {**ficha.valor, campo: valor})
    assert ficha.sensibilidad["resistividad_min_ohm_cm"][0] == pytest.approx(
        ficha.valor["resistividad_min_ohm_cm"], rel=REL_TRANSPORTE)
    assert ficha.sensibilidad["pH_max"][1] == pytest.approx(
        ficha.valor["pH_max"], rel=REL_TRANSPORTE)
    duro = {**ficha.valor, "resistividad_min_ohm_cm": 2000.0, "pH_max": 8.0}
    with declarados({M2.CRITERIO_DURABILIDAD_TMC: duro}):
        assert _excluidos(_punto(), resistividad_ohm_cm=1500.0) == (TMC,)
        assert _excluidos(_punto(), pH=8.2) == (TMC,)


def test_la_abrasion_severa_excluye_el_hdpe_y_avisa_al_metal_y_al_concreto():
    """
    La prohibicion es del §8-3.3 y solo alcanza al termoplastico. Al metal y
    al concreto la Table 8-4 les pide proteccion: aviso, no exclusion. El
    nivel es un dato de campo: no se deduce de la velocidad.
    """
    niveles = CN.NIVELES_DE_ABRASION
    assert niveles == ("no_abrasivo", "poco_abrasivo",
                       "moderadamente_abrasivo", "severamente_abrasivo")
    severa = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(abrasion=niveles[3]))
    assert severa.excluidos == (HDPE,)
    assert "WSDOT_HM.8-3.3#SEVERA" in severa.reglas_de(HDPE)[0].cita_ids
    assert {r.material for r in severa.reglas
            if r.efecto is EfectoDeDurabilidad.AVISA} == {TMC, CONCRETO}
    assert severa.motivo_de_exclusion(HDPE) and not severa.motivo_de_exclusion(TMC)
    moderada = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(abrasion=niveles[2]))
    assert moderada.excluidos == ()
    assert {r.material for r in moderada.reglas} == {TMC, CONCRETO}
    for nivel in niveles[:2]:
        d = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(abrasion=nivel))
        assert d.aplicada and len(d.pasos) == 1
        assert not [r for r in d.reglas if r.ensayo == "abrasion"]
    with pytest.raises(DatoInvalidoError) as exc:
        M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(abrasion="mucha"))
    assert exc.value.campo == "abrasion"


@pytest.mark.parametrize("ensayo, exposicion, a_c", [
    (dict(sulfatos_suelo_ppm=500.0), "insignificante", None),    # 0.05 %
    (dict(sulfatos_suelo_ppm=1500.0), "moderada", 0.50),         # 0.15 %
    (dict(sulfatos_agua_ppm=2000.0), "severa", 0.45),
    (dict(sulfatos_agua_ppm=12000.0), "muy_severa", 0.45),
    # Con las dos escalas gana la mas exigente.
    (dict(sulfatos_suelo_ppm=500.0, sulfatos_agua_ppm=2000.0), "severa", 0.45),
])
def test_los_sulfatos_exigen_al_concreto_y_nunca_lo_excluyen(ensayo, exposicion, a_c):
    """
    E.060 Tabla 4.4, por sus DOS escalas: sulfato en el suelo (% en peso; el
    ensayo entra en ppm y 1 % son 10 000 ppm) y sulfato en el agua (ppm).
    Por eso hay dos claves y no una `sulfatos_ppm`, que seria ambigua.
    """
    d = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(**ensayo))
    assert d.excluidos == ()
    paso = next(p for p in d.pasos if p.fundamento_id == "F3.DUR.SULFATOS")
    assert paso.resultado.valor == exposicion
    reglas = d.reglas_de(CONCRETO)
    if a_c is None:
        assert reglas == ()
    else:
        (regla,) = reglas
        assert regla.efecto is EfectoDeDurabilidad.EXIGE
        assert regla.cita_ids == ("E060.T4.4",)
        assert f"maxima {a_c}" in regla.texto


def test_la_fila_de_sulfatos_es_la_misma_regla_que_la_de_M9():
    """Dos lecturas de la misma tabla, contrastadas para que no diverjan."""
    for suelo_pct in (None, 0.0, 0.09, 0.10, 0.19, 0.20, 1.0, 2.0, 2.01):
        for agua in (None, 0.0, 149.0, 150.0, 1499.0, 1500.0, 10000.0, 10001.0):
            if suelo_pct is None and agua is None:
                continue
            m2 = M2._fila_de_sulfatos(suelo_pct, agua)["exposicion"]
            m9 = M9.clase_exposicion_sulfatos(so4_suelo_pct=suelo_pct,
                                              so4_agua_ppm=agua)
            assert m2 == getattr(m9, "exposicion", m9) or m2 in str(m9), (
                suelo_pct, agua, m2, m9)


def test_los_cloruros_no_tienen_umbral_para_el_concreto_y_si_para_el_acero():
    """
    E.060 4.4.2 define la exposicion del CONCRETO por el origen del cloruro,
    sin ppm: ahi el ensayo avisa y no decide. Para el ACERO galvanizado
    AASHTO LRFD si da umbral (100 ppm, por analogia): lo aplica la regla de
    suelo agresivo (H3 de la auditoria), que por defecto no excluye.
    """
    d = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(cloruros_ppm=900.0))
    assert d.aplicada and d.excluidos == ()
    (del_concreto,) = d.reglas_de(CONCRETO)
    assert del_concreto.efecto is EfectoDeDurabilidad.AVISA
    assert "no por un umbral en ppm" in del_concreto.texto
    assert not [r for r in d.reglas_de(TMC) if r.ensayo == "cloruros_ppm"]
    assert [p.fundamento_id for p in d.pasos] == ["F3.DUR.CLORUROS",
                                                 "F3.DUR.SUELO_AGRESIVO"]
    assert d.pasos[0].umbral is None
    bajo = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(cloruros_ppm=80.0))
    assert not [r for r in bajo.reglas if r.ensayo == "suelo_agresivo"]


# ===========================================================================
# Auditoria adversarial de T-4: H3, H5, H6, H8
# ===========================================================================

CASO_DEL_AUDITOR = dict(resistividad_ohm_cm=1500.0, cloruros_ppm=2000.0, pH=7.5)


def test_h3_el_suelo_agresivo_por_analogia_avisa_y_exige_proteccion_sin_excluir():
    """
    El caso del auditor: resistividad 1500 ohm-cm, cloruros 2000 ppm, pH 7.5.
    El filtro de la fuente de alcantarillas no lo toca (pH dentro de 5.0-8.5,
    resistividad sobre 1000) y hasta la auditoria la TMC salia candidata sin
    una linea. Ahora: aviso con el umbral y el valor, exigencia de proteccion
    de EG-2013 507.10, y la TMC sigue candidata, porque los criterios son de
    refuerzos enterrados y se aplican por analogia.
    """
    d = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(**CASO_DEL_AUDITOR))
    assert d.excluidos == ()
    aviso, exige = [r for r in d.reglas if r.ensayo == "suelo_agresivo"]
    assert aviso.material is TMC and aviso.efecto is EfectoDeDurabilidad.AVISA
    for trozo in ("AASHTO LRFD 11.10.6.4.2a", "por analogia",
                  "resistividad = 1500 ohm-cm menor de 3000 ohm-cm",
                  "cloruros = 2000 ppm mayor de 100 ppm"):
        assert trozo in aviso.texto
    assert "pH" not in aviso.texto.split("):", 1)[1].split(". La TMC")[0]
    assert aviso.criterio == M2.CRITERIO_SUELO_AGRESIVO
    assert "AASHTO_LRFD_9.11.10.6.4.2a#NO_AGRESIVO" in aviso.cita_ids
    assert exige.efecto is EfectoDeDurabilidad.EXIGE
    assert exige.cita_ids == ("EG2013.507.10",)
    assert "LECTURA DEL PROYECTO" in exige.texto
    paso = d.pasos[-1]
    assert paso.fundamento_id == "F3.DUR.SUELO_AGRESIVO"
    assert paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
    assert "3000" in str(paso.umbral.valor) and "100" in str(paso.umbral.valor)
    assert len(M2.materiales_candidatos(_punto(), d)) == len(TipoMaterial)


def test_h3_el_efecto_es_un_A_de_perfil_y_excluye_es_la_lectura_estricta():
    """
    'suelo_agresivo_lrfd_sobre_tmc' [A]: «aviso» en el archivo --la exclusion
    se reserva a las fuentes de alcantarillas-- y «excluye» declarable para
    la sensibilidad. Las dos lecturas sobre el mismo caso, y ninguna sin
    ensayos.
    """
    efecto = ca.criterio(M2.CRITERIO_EFECTO_SUELO_AGRESIVO)
    assert efecto.etiqueta == "A" and efecto.nivel == ca.NIVEL_PERFIL
    assert efecto.valor == M2.EFECTO_AVISO
    assert efecto.sensibilidad == (M2.EFECTO_AVISO, M2.EFECTO_EXCLUYE)
    assert "analogia" in efecto.justificacion
    umbrales = ca.criterio(M2.CRITERIO_SUELO_AGRESIVO)
    assert umbrales.etiqueta == "C"
    assert umbrales.valor == pytest.approx(
        {"pH_min": 5.0, "pH_max": 10.0, "resistividad_min_ohm_cm": 3000.0,
         "cloruros_max_ppm": 100.0, "sulfatos_max_ppm": 200.0},
        rel=REL_TRANSPORTE)
    ensayos = EnsayosDurabilidad(**CASO_DEL_AUDITOR)
    assert M2.matriz_durabilidad(_punto(), ensayos).excluidos == ()
    with declarados({M2.CRITERIO_EFECTO_SUELO_AGRESIVO: M2.EFECTO_EXCLUYE}):
        estricta = M2.matriz_durabilidad(_punto(), ensayos)
        assert estricta.excluidos == (TMC,)
        assert "suelo agresivo segun AASHTO LRFD" in estricta.motivo_de_exclusion(TMC)
        assert [m.tipo for m in M2.materiales_candidatos(_punto(), estricta)] \
            == [CONCRETO, HDPE]
        # Sin ensayos no actua ninguna de las dos lecturas.
        assert M2.matriz_durabilidad(_punto()).excluidos == ()
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(M2.CRITERIO_EFECTO_SUELO_AGRESIVO, "ignora")
    # Un suelo que cumple los cuatro criterios no dispara nada.
    limpio = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(
        pH=7.0, resistividad_ohm_cm=5000.0, cloruros_ppm=50.0,
        sulfatos_suelo_ppm=100.0))
    assert not [r for r in limpio.reglas if r.ensayo == "suelo_agresivo"]
    assert limpio.pasos[-1].veredicto.tipo.value == "cumple"


def test_h5_los_sulfatos_sobre_insignificante_exigen_proteger_la_tmc():
    """
    EG-2013 507.10 tiene dos disparadores y se aplicaba uno: «o que los
    suelos circundantes presenten sustancias agresivas». Con sulfatos por
    encima de la exposicion insignificante de E.060 T4.4 la TMC sigue
    candidata con la exigencia de proteccion; por debajo, no.
    """
    con = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(sulfatos_agua_ppm=2000.0))
    (exige,) = [r for r in con.reglas_de(TMC)
                if r.efecto is EfectoDeDurabilidad.EXIGE]
    assert exige.cita_ids == ("EG2013.507.10",)
    assert "exposicion a sulfatos 'severa'" in exige.texto
    assert con.excluidos == ()
    sin = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(sulfatos_agua_ppm=100.0))
    assert not [r for r in sin.reglas_de(TMC)
                if r.efecto is EfectoDeDurabilidad.EXIGE]


def test_h6_la_tmc_candidata_lleva_el_aviso_fijo_del_manual_sin_ensayos():
    """
    El texto del Manual de Hidrologia (4.1.1.3.7 f y g) es cualitativo y no
    depende de un ensayo: se imprime siempre que la TMC es candidata, sin
    excluirla. Con turba en el suelo de fundacion avisa ademas contra el
    metal. En la Familia C, donde la TMC no es candidata, no aparece.
    """
    d = M2.matriz_durabilidad(_punto())
    assert not d.aplicada and d.resumen == DURABILIDAD_SIN_ENSAYOS
    (fijo,) = [r for r in d.reglas if r.ensayo == "condicion_del_sitio"]
    assert fijo.material is TMC and fijo.efecto is EfectoDeDurabilidad.AVISA
    assert "no recomienda alcantarillas metalicas" in fijo.texto
    assert fijo.cita_ids == ("MC_HHD.4.1.1.3.7f#COSTA",
                             "MC_HHD.4.1.1.3.7g#AGRESIVAS")
    assert d.excluidos == ()
    con_ensayos = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(pH=7.0))
    assert [r for r in con_ensayos.reglas if r.ensayo == "condicion_del_sitio"]
    turba = M2.matriz_durabilidad(_punto(sucs_fundacion="PT"))
    (contra_metal,) = [r for r in turba.reglas
                       if r.ensayo == "sucs_fundacion" and r.material is TMC]
    assert "turba" in contra_metal.texto
    canal = M2.matriz_durabilidad(_punto(id="C-01", familia=Familia.C))
    assert canal.reglas == ()


def test_h8_dos_entradas_del_mismo_ensayo_que_se_contradicen_avisan():
    """
    Los sulfatos del EMS entran por la matriz (`sulfatos_*_ppm`) y por el
    dato de sitio 'exposicion_quimica_ems', que M9 lee para el recubrimiento
    del cabezal. Si dan exposiciones distintas se avisa; si coinciden, no. El
    contraste no registra el [S] como usado.
    """
    ems = ca.valores_dinamicos()[M2.CRITERIO_EXPOSICION_EMS]
    del_ems = M2._fila_de_sulfatos(ems.get("so4_suelo_pct"),
                                   ems.get("so4_agua_ppm"))["exposicion"]
    otra = 12000.0 if del_ems != "muy_severa" else 10.0
    ca.reiniciar_usos()
    d = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(sulfatos_agua_ppm=otra))
    (aviso,) = [r for r in d.reglas if r.criterio == M2.CRITERIO_EXPOSICION_EMS]
    assert aviso.material is None and "INCOHERENCIA" in aviso.texto
    assert del_ems in aviso.texto
    assert M2.CRITERIO_EXPOSICION_EMS not in ca.criterios_usados()
    if ems.get("so4_agua_ppm") is not None:
        igual = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(
            sulfatos_agua_ppm=ems["so4_agua_ppm"],
            sulfatos_suelo_ppm=(None if ems.get("so4_suelo_pct") is None
                                else ems["so4_suelo_pct"] * 10000)))
        assert not [r for r in igual.reglas
                    if r.criterio == M2.CRITERIO_EXPOSICION_EMS]


def test_en_la_familia_C_no_se_emiten_reglas_de_materiales_que_no_son_candidatos():
    canal = _punto(id="C-01", familia=Familia.C)
    assert M2.tipos_candidatos(canal) == (CONCRETO,)
    d = M2.matriz_durabilidad(canal, EnsayosDurabilidad(
        pH=4.0, resistividad_ohm_cm=100.0, abrasion="severamente_abrasivo"))
    assert d.aplicada and d.excluidos == ()
    assert {r.material for r in d.reglas} == {CONCRETO}


def test_el_filtro_conserva_el_orden_y_MD_lo_recibe():
    """
    `materiales_candidatos` filtra sin reordenar, y `MD.disenar_punto` pasa
    el dictamen: con el concreto y el HDPE fuera, lo que el bucle evalua es
    solo el TMC (medido con un verificador que anota el material).
    """
    punto = _punto()
    d = M2.matriz_durabilidad(punto, EnsayosDurabilidad(
        pH=4.0, abrasion="severamente_abrasivo"))
    assert [m.tipo for m in M2.materiales_candidatos(punto, d)] == [CONCRETO]
    sintetico = DictamenDurabilidad(aplicada=True, reglas=tuple(
        ReglaDeDurabilidad(ensayo="pH", material=m,
                           efecto=EfectoDeDurabilidad.EXCLUYE,
                           texto=f"excluido {m.value}", cita_ids=())
        for m in (CONCRETO, HDPE)))
    vistos = []

    def anota(*, punto, material, seccion, resultado):
        vistos.append(material.tipo)
        return (Verificacion(cumple=True, numeral="prueba", valor_obtenido=0.0,
                             valor_admisible=1.0, criterio_aplicado=None,
                             codigo="V1"),)

    resultado = MD.disenar_punto(punto, L=24.0, TW=0.0, verificar=anota,
                                 durabilidad=sintetico)
    assert set(vistos) == {TMC} and resultado.material.tipo is TMC


def test_si_la_matriz_excluye_a_todos_el_motivo_cita_cada_exclusion():
    todos = DictamenDurabilidad(aplicada=True, reglas=tuple(
        ReglaDeDurabilidad(ensayo="pH", material=m,
                           efecto=EfectoDeDurabilidad.EXCLUYE,
                           texto=f"motivo de {m.value}", cita_ids=())
        for m in TipoMaterial))
    with pytest.raises(DisenoNoFactibleError) as exc:
        MD.disenar_punto(_punto(), L=24.0, TW=0.0, durabilidad=todos,
                         verificar=lambda **kw: ())
    for m in TipoMaterial:
        assert f"{m.value}: motivo de {m.value}" in str(exc.value)
    assert "matriz de durabilidad" in str(exc.value)


def test_el_caracter_de_cada_umbral_de_durabilidad_sale_de_su_cita(reg):
    d = M2.matriz_durabilidad(_punto(), EnsayosDurabilidad(
        pH=6.0, resistividad_ohm_cm=4000.0, abrasion="poco_abrasivo"))
    assert len(d.pasos) == 4
    for paso in d.pasos:
        assert paso.por_que and paso.umbral is not None
        cita = reg.cita(paso.umbral.cita_id)
        assert paso.umbral.caracter == cita.caracter.value.upper()
        assert paso.veredicto.tipo.value == "cumple"


# ===========================================================================
# (4b) INF-5.1.9 - `sucs_fundacion` tiene consumidor
# ===========================================================================

def test_el_conjunto_de_suelos_deficientes_es_A_y_se_elige_entre_los_de_E050():
    """
    El Manual recomienda el marco «cuando el suelo de fundacion es de mala
    calidad» y no dice que suelos son esos. El conjunto es una adopcion
    declarada, elegida dentro de los quince simbolos de la Figura 3 de la
    E.050, y por defecto son los tres organicos de su Art. 24.
    """
    ficha = ca.criterio(M2.CRITERIO_SUCS_DEFICIENTE)
    assert ficha.etiqueta == "A" and ficha.nivel == ca.NIVEL_PERFIL
    assert ficha.valor == ("OL", "OH", "PT")
    assert tuple(ficha.sensibilidad) == CN.SIMBOLOS_SUCS
    assert len(CN.SIMBOLOS_SUCS) == 15 and set(ficha.valor) < set(CN.SIMBOLOS_SUCS)
    # Un simbolo que no es de la Figura 3 lo rechaza el consumidor: la
    # puerta de una serie de claves comprueba la forma, no el conjunto.
    with con_valor(M2.CRITERIO_SUCS_DEFICIENTE, ("XX",),
                   motivo="simbolo inexistente, para medir la guardia de M2"):
        with pytest.raises(DatoInvalidoError) as exc:
            M2.matriz_durabilidad(_punto())
    assert exc.value.campo == M2.CRITERIO_SUCS_DEFICIENTE


def test_componentes_sucs_parte_los_suelos_de_frontera():
    assert M2.componentes_sucs("SM") == ("SM",)
    assert M2.componentes_sucs("sp-sm") == ("SP", "SM")
    assert M2.componentes_sucs(" CL - ML ") == ("CL", "ML")
    assert M2.componentes_sucs("") == ()


def test_los_cuatro_puntos_del_fixture_no_ganan_aviso(puntos):
    """SM, SP-SM, SM y ML: ninguno esta en el conjunto. Solo la linea."""
    assert [p.sucs_fundacion for p in puntos.values()] == ["SM", "SP-SM", "SM", "ML"]
    for punto in puntos.values():
        d = M2.matriz_durabilidad(punto)
        assert not [r for r in d.reglas if r.ensayo == "sucs_fundacion"]
        assert d.pasos == ()
        assert punto.sucs_fundacion in d.suelo_fundacion
        assert "no esta entre los grupos SUCS declarados deficientes" in d.suelo_fundacion
        # H9: la linea no puede leerse como «apto», y remite a la licuacion.
        assert "no lo califica como apto" in d.suelo_fundacion
        assert "Art. 38" in d.suelo_fundacion and "licuacion" in d.suelo_fundacion


@pytest.mark.parametrize("sucs", ["OH", "CL-OL", "pt"])
def test_un_suelo_deficiente_avisa_del_marco_y_no_cambia_los_candidatos(sucs):
    punto = _punto(sucs_fundacion=sucs)
    d = M2.matriz_durabilidad(punto)
    assert not d.aplicada and d.excluidos == ()
    (regla,) = [r for r in d.reglas
                if r.ensayo == "sucs_fundacion" and r.material is None]
    # H9: la E.050 no solo prohibe cimentar: manda remover y reemplazar.
    assert "removerlos" in regla.texto and "reemplazarlos" in regla.texto
    assert "E050.24#REMOVER" in regla.cita_ids
    assert regla.efecto is EfectoDeDurabilidad.AVISA
    assert regla.criterio == M2.CRITERIO_SUCS_DEFICIENTE
    assert "MC_HHD.4.1.1.3.4a#MARCO" in regla.cita_ids
    (paso,) = d.pasos
    assert paso.fundamento_id == "F3.DUR.SUELO_FUNDACION"
    assert len(M2.materiales_candidatos(punto, d)) == len(TipoMaterial)
    # Sin ensayos la linea de «matriz no aplicada» se imprime igual.
    assert d.resumen == DURABILIDAD_SIN_ENSAYOS


def test_un_simbolo_que_no_es_sucs_se_dice_y_no_detiene():
    d = M2.matriz_durabilidad(_punto(sucs_fundacion="arcilla"))
    assert not [r for r in d.reglas if r.ensayo == "sucs_fundacion"]
    assert "no es una clasificacion SUCS" in d.suelo_fundacion


def test_en_un_marco_el_suelo_deficiente_no_avisa_porque_ya_es_marco():
    d = M2.matriz_durabilidad(_punto(id="C-01", familia=Familia.C,
                                     sucs_fundacion="OH"))
    assert d.reglas == () and "ya es un marco" in d.suelo_fundacion


def test_el_conjunto_declarado_cambia_el_aviso():
    punto = _punto(sucs_fundacion="ML")

    def del_suelo():
        return [r for r in M2.matriz_durabilidad(punto).reglas
                if r.ensayo == "sucs_fundacion"]

    assert del_suelo() == []
    with declarados({M2.CRITERIO_SUCS_DEFICIENTE: ("OL", "OH", "PT", "ML")}):
        assert len(del_suelo()) == 1


# ===========================================================================
# El pipeline: servicio, CLI y memoria
# ===========================================================================

def test_sin_ensayos_cada_punto_imprime_la_linea_y_no_se_mueve_ningun_diametro(
        tmp_path):
    """
    La corrida ancha de la linea base, en proceso. Los cuatro puntos llegan a
    la Fase 3 y los cuatro dicen «sin ensayos, matriz no aplicada» en el
    volcado, en el JSON y en la memoria. Y el resultado es el de antes de
    T-4: A-01 y A-02 en concreto de 0.90 m, B-01 y C-01 sin dimensionar.
    """
    informe = _corrida(tmp_path)
    por_id = _por_id(informe)
    assert list(por_id) == ["A-01", "A-02", "B-01", "C-01"]
    for punto in informe.puntos:
        assert punto.durabilidad is not None and not punto.durabilidad.aplicada
    volcado = cli.volcar(informe)
    assert volcado.count(f"Sec. 3.3 {DURABILIDAD_SIN_ENSAYOS}") == 4
    datos = cli.informe_json(informe)
    assert [p["durabilidad"]["resumen"] for p in datos["puntos"]] == \
        [DURABILIDAD_SIN_ENSAYOS] * 4
    assert all(p["durabilidad"]["materiales_excluidos"] == []
               for p in datos["puntos"])
    memoria = M11.memoria_html(informe, proyecto="T-4")
    assert memoria.count(f"<b>{DURABILIDAD_SIN_ENSAYOS}</b>") == 4
    assert memoria.count(M11.TITULO_DURABILIDAD) >= 4
    assert M11.traza_durabilidad(por_id["A-01"]) == ()

    adoptado = {i: (p.resultado.material.tipo, p.resultado.seccion.etiqueta())
                for i, p in por_id.items() if p.dimensionado}
    assert adoptado == {"A-01": (CONCRETO, "Ø 0.90 m"),
                        "A-02": (CONCRETO, "Ø 0.90 m")}
    diseno = {p["id"]: p["diseno"] for p in datos["puntos"]}
    assert diseno["A-01"]["dimension_max_criterio"] == M2.CRITERIO_D_MAX_NORMA
    assert diseno["A-01"]["dimension_max_catalogo_m"] == pytest.approx(2.70, rel=REL_TRANSPORTE)
    assert diseno["B-01"] is None and diseno["C-01"] is None
    usados = {c["clave"] for c in datos["criterios"]["usados"]}
    assert {M2.CRITERIO_SUCS_DEFICIENTE, M2.CRITERIO_D_MAX_NORMA} <= usados
    assert M2.CRITERIO_D_MAX_CATALOGO not in usados


def test_con_ensayos_el_del_punto_pisa_al_del_sitio_y_la_memoria_lo_imprime(
        tmp_path):
    """
    pH del sitio 7.0 (nada que excluir) y pH de A-02 4.6: el TMC sale de los
    candidatos SOLO en A-02. Ningun diametro se mueve --el concreto sigue
    siendo el primer candidato--; lo que cambia es la lista de materiales
    evaluables, y la memoria lo deja escrito con su paso y sus citas.
    """
    informe = _corrida(tmp_path, {"globales": {"pH": 7.0},
                                  "puntos": {"A-02": {"pH": 4.6}}})
    por_id = _por_id(informe)
    assert por_id["A-01"].durabilidad.excluidos == ()
    assert por_id["A-02"].durabilidad.excluidos == (TMC,)
    assert por_id["A-02"].durabilidad.ensayos.origen_de("pH") == \
        "datos externos (punto A-02)"
    assert por_id["A-01"].durabilidad.ensayos.origen_de("pH") == \
        "datos externos (globales)"
    assert por_id["A-02"].resultado.material.tipo is CONCRETO
    assert por_id["A-02"].resultado.seccion.etiqueta() == "Ø 0.90 m"

    volcado = cli.volcar(informe)
    assert DURABILIDAD_SIN_ENSAYOS not in volcado
    assert "[excluye] tmc: pH = 4.6" in volcado
    datos = {p["id"]: p["durabilidad"] for p in cli.informe_json(informe)["puntos"]}
    assert datos["A-02"]["materiales_excluidos"] == ["tmc"]
    assert datos["A-02"]["ensayos"]["pH"]["valor"] == pytest.approx(4.6, rel=REL_TRANSPORTE)
    assert datos["A-01"]["materiales_excluidos"] == []
    memoria = M11.memoria_html(informe, proyecto="T-4")
    assert M11.TITULO_TRAZA_DURABILIDAD in memoria
    assert "WSDOT_HM.8-5.1#PH" in memoria
    pasos = M11.traza_durabilidad(por_id["A-02"])
    assert [p.fundamento_id for p in pasos] == ["F3.DUR.PH",
                                                "F3.DUR.SUELO_AGRESIVO"]
    assert set(pasos) <= set(M11.pasos_del_informe(informe))
    assert set(pasos) <= set(M11.pasos_impresos(informe))


def test_un_punto_que_se_detiene_en_la_fase_2_no_llega_a_la_matriz():
    """Sin luz no hay Fase 3: ni dictamen, ni linea, ni criterio invocado."""
    externos = cli.cargar_datos_externos(None, {
        "luz_m": None, "TW_m": None, "longitud_m": None,
        "L_hidraulico_m": None, "categoria_tr": None})
    informe = cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)
    assert all(p.durabilidad is None for p in informe.puntos)
    assert "Sec. 3.3" not in cli.volcar(informe)
    assert cli.informe_json(informe)["criterios"]["usados"] == []
    assert M11.TITULO_DURABILIDAD not in M11.memoria_html(informe, proyecto="x")


def test_si_la_matriz_se_bloquea_el_bucle_de_materiales_no_corre(tmp_path):
    """
    Vaciado el criterio del conjunto de suelos, la etapa se bloquea como un
    pendiente declarable y MD NO dimensiona con los tres candidatos sin
    filtrar: eso seria rellenar el vacio en silencio.
    """
    with sin_valor(M2.CRITERIO_SUCS_DEFICIENTE):
        informe = _corrida(tmp_path)
    a01 = _por_id(informe)["A-01"]
    assert a01.durabilidad is None and not a01.dimensionado and a01.traza == []
    (bloqueo,) = [b for b in a01.bloqueos
                  if b.etapa == servicio.ETAPA_DURABILIDAD]
    assert M2.CRITERIO_SUCS_DEFICIENTE in bloqueo.mensaje
    assert "no evaluada (ver bloqueos)" in cli.volcar(informe)
    assert M11.ETAPA_DURABILIDAD == servicio.ETAPA_DURABILIDAD
    assert "no se pudo evaluar" in M11.memoria_html(informe, proyecto="x")


@pytest.mark.parametrize("clave, valor", [
    ("pH", True), ("pH", 0), ("pH", -1.0), ("pH", 14.5), ("pH", "acido"),
    ("resistividad_ohm_cm", 0), ("resistividad_ohm_cm", float("inf")),
    ("sulfatos_suelo_ppm", -5), ("sulfatos_agua_ppm", float("nan")),
    ("cloruros_ppm", False), ("abrasion", "severa"), ("abrasion", 3),
    # H11: una concentracion no puede pasar del 100 % de la muestra.
    ("sulfatos_suelo_ppm", 1e9), ("cloruros_ppm", 1000001),
])
def test_la_puerta_rechaza_un_ensayo_mal_escrito(clave, valor):
    with pytest.raises(DatoInvalidoError) as exc:
        servicio._dato_externo(clave, valor, "prueba")
    assert exc.value.campo == clave


def test_la_puerta_admite_el_cero_de_una_concentracion_y_los_cuatro_niveles():
    for clave in servicio.CLAVES_DE_DURABILIDAD_CON_CERO:
        assert servicio._dato_externo(clave, 0, "prueba").valor == pytest.approx(0.0, abs=ABS_CERO)
    for nivel in CN.NIVELES_DE_ABRASION:
        assert servicio._dato_externo("abrasion", nivel, "prueba").valor == nivel
    assert servicio._dato_externo("pH", 14, "prueba").valor == pytest.approx(14.0, rel=REL_TRANSPORTE)


def test_los_ensayos_son_opcionales_y_no_son_claves_que_una_etapa_exija(tmp_path):
    """
    Las seis claves entran por el mismo JSON y NO estan en `CLAVES_EXTERNAS`,
    cuyas claves son datos que alguna etapa exige: el pre-vuelo no las
    anuncia como faltas, y una clave mal tecleada las nombra entre las
    admitidas.
    """
    assert servicio.CLAVES_DE_DURABILIDAD == (
        "sulfatos_suelo_ppm", "sulfatos_agua_ppm", "cloruros_ppm", "pH",
        "resistividad_ohm_cm", "abrasion")
    assert cli.CLAVES_DE_DURABILIDAD is servicio.CLAVES_DE_DURABILIDAD
    assert not set(servicio.CLAVES_DE_DURABILIDAD) & set(servicio.CLAVES_EXTERNAS)
    externos = _externos(tmp_path)
    faltas = anticipo.datos_faltantes_por_punto(CSV_EJEMPLO, externos,
                                                cli.ALCANCE_PERFIL)
    assert not [f for f in faltas if f.dato in servicio.CLAVES_DE_DURABILIDAD]
    assert servicio.ensayos_de_durabilidad(externos, "A-01") == EnsayosDurabilidad()
    ruta = tmp_path / "malo.json"
    ruta.write_text(json.dumps({"globales": {"ph": 7.0}}), encoding="utf-8")
    with pytest.raises(DatoInvalidoError) as exc:
        cli.cargar_datos_externos(ruta, {})
    for clave in servicio.CLAVES_DE_DURABILIDAD:
        assert clave in exc.value.motivo


# ===========================================================================
# INF-5.1.16 - la constante de selva alta se conserva sin consumidor
# ===========================================================================

def test_el_diametro_minimo_de_selva_alta_sigue_sin_consumidor_y_esta_censado():
    """
    La hoja de ruta §3.1 manda «programar la rama y declararla inactiva». La
    rama NO existe: ningun modulo de calculo nombra la constante. No se le
    inventa consumidor --el corredor no es de selva alta y ningun dato de
    entrada dice en que region natural esta la obra--; se conserva como
    constante de referencia y la decision esta en la ficha T4-06 de
    `docs/decisiones_diferidas.md`.
    """
    nombre = "DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO"
    assert hasattr(CN, nombre)
    assert nombre in CN.CONSTANTES_DE_REFERENCIA
    consumidores = []
    for ruta in sorted((RAIZ / "src" / "modulos").glob("*.py")) + [
            RAIZ / "src" / "servicio.py", RAIZ / "cli.py"]:
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        if any(isinstance(n, (ast.Name, ast.Attribute))
               and (getattr(n, "id", None) == nombre
                    or getattr(n, "attr", None) == nombre)
               for n in ast.walk(arbol)):
            consumidores.append(ruta.name)
    assert consumidores == []
    fichas = (RAIZ / "docs" / "decisiones_diferidas.md").read_text(encoding="utf-8")
    assert nombre in fichas and "INF-5.1.16" in fichas


# ===========================================================================
# Lo que T-5 va a consumir, y el registro
# ===========================================================================

def test_la_vista_de_planchas_del_tmc_trae_A_I_y_r_de_las_tablas_de_A796(reg):
    """
    `TMC_PLANCHA_CORRUGADA` es lo que T-5 necesita para el calibre: por
    corrugacion y espesor, el area, el momento de inercia y el radio de giro
    de ASTM A796 (Tablas 5, 7 y 9), sin las filas de la nota A.
    """
    vista = CN.TMC_PLANCHA_CORRUGADA
    assert len(vista) == 17 and "68x13/2.01" in vista
    assert not [k for k in vista if k.endswith("/1.02")]
    for clave, fila in vista.items():
        corrugacion, espesor = clave.split("/")
        assert fila["corrugacion"] == corrugacion
        assert fila["espesor_m"] == pytest.approx(float(espesor) / 1000, rel=REL_TRANSPORTE)
        de_la_tabla = next(f.valores for f in reg.tabla(fila["tabla"]).filas
                           if f.etiqueta_literal == espesor)
        assert (fila["A_mm2_mm"], fila["I_mm4_mm"], fila["r_mm"]) == \
            pytest.approx((de_la_tabla["A"], de_la_tabla["I"], de_la_tabla["r"]), rel=REL_TRANSPORTE)
    assert sorted({f["profundidad_m"] for f in vista.values()}) == \
        pytest.approx([0.013, 0.025], rel=REL_TRANSPORTE)


def test_los_diametros_estandar_del_tmc_son_las_X_de_la_table_6(reg):
    filas = reg.tabla("AASHTO_M36.T6").filas
    for corrugacion, diametros in CN.DIAMETROS_ESTANDAR_TMC.items():
        assert diametros == tuple(f.valores["dn_mm"] for f in filas
                                  if f.valores[f"c{corrugacion}"] == "X")
    assert max(CN.DIAMETROS_ESTANDAR_TMC["68x13"]) == 2100
    assert max(CN.DIAMETROS_ESTANDAR_TMC["75x25"]) == 3600
    assert min(CN.DIAMETROS_ESTANDAR_TMC["125x25"]) == 825


@pytest.mark.parametrize("tabla, filas", [
    ("AASHTO_LRFD_9.TA12-11", 8), ("AASHTO_M36.T1", 4), ("AASHTO_M36.T7", 7),
    ("WSDOT_HM.T8-4", 4), ("HDS5_3ED.TB.1", 13), ("E050.FIG3", 15),
])
def test_las_tablas_que_T4_transcribio_estan_en_el_registro(reg, tabla, filas):
    t = reg.tabla(tabla)
    assert len(t.filas) == filas
    assert reg.cita(t.cita_id).fuente_id == tabla.split(".")[0]


def test_la_tabla_de_abrasion_declara_que_es_de_niveles_y_no_de_velocidades(reg):
    tabla = reg.tabla("WSDOT_HM.T8-4")
    assert tabla.interpretacion is not None and tabla.interpretacion.en_contra
    assert tuple(tabla.clave_corta(f) for f in tabla.filas) == CN.NIVELES_DE_ABRASION
    assert CN.NIVEL_DE_ABRASION_SEVERO == "severamente_abrasivo"


@pytest.mark.pdf
@pytest.mark.parametrize("fuente_id, pagina_pdf, fragmentos", [
    # La prohibicion del termoplastico, donde la fuente la escribe.
    ("WSDOT_HM", 228, ("shall not be used for severely abrasive",)),
    # Los cortes de la tabla de niveles de abrasion.
    ("WSDOT_HM", 243, ("15 ft/s",)),
    # El piso de la ventana de 'v_max_tmc'.
    ("WSDOT_HM", 76, ("10 ft/s",)),
    # pH y resistividad de la tuberia de acero.
    ("WSDOT_HM", 240, ("5.0", "8.5")),
    ("WSDOT_HM", 241, ("1,000 ohm-cm",)),
    # El n del polietileno corrugado de interior liso.
    ("HDS5_3ED", 208, ("Corrugated Polyethylene", "0.009-0.015")),
    # El diametro exterior maximo del tubo de PE corrugado.
    ("AASHTO_LRFD_9", 1746, ("42.5", "48.0", "55.0")),
    # El umbral de proteccion de la tuberia metalica.
    ("EG2013", 982, ("pH menor de 5.8", "suelos circundantes")),
    # Auditoria: suelo no agresivo para acero galvanizado (H3).
    ("AASHTO_LRFD_9", 1558, ("pH = 5 to 10", "3000 ohm-cm", "100 ppm", "200 ppm")),
    ("AASHTO_LRFD_9", 1603, ("3,000 ohm-cm", "100 ppm", "200 ppm")),
    ("AASHTO_LRFD_9", 1414, ("2,000 ohm-cm", "pH less than 5.5", "1,000 ppm",
                             "500 ppm")),
    # El factor de flexibilidad de la plancha de 13 mm (H7).
    ("ASTM_A796", 4, ("0.245",)),
    # El HDPE de interior liso de la norma peruana (H11).
    ("EG2013", 989, ("superficie interior lisa",)),
    # Licuacion y suelos no permitidos de la E.050 (H9).
    ("E050", 51, ("Licuación",)),
    ("E050", 37, ("removidos",)),
])
def test_los_numeros_de_T4_estan_en_la_pagina_que_se_cita(
        fuente_id, pagina_pdf, fragmentos):
    """
    Los Verbatim ya los verifica `test_normativa_pdf` uno a uno; esto fija
    ademas los NUMEROS que el calculo toma de cada pagina, para que un cambio
    de ejemplar se note aqui con el nombre del valor.
    """
    from src.normativa.extraccion import texto_de_pagina
    ruta = fuentes.ruta_pdf(fuentes.FUENTES[fuente_id])
    if not ruta.exists():
        pytest.skip(f"el PDF de {fuente_id} no esta enlazado (NORMAS_DIR)")
    texto = " ".join(texto_de_pagina(ruta, pagina_pdf).split())
    for fragmento in fragmentos:
        assert fragmento in texto, (fuente_id, pagina_pdf, fragmento)


# ===========================================================================
# Auditoria adversarial de T-4: H1 (verificador real), H7 y H11
# ===========================================================================

CASO_G2 = ("X-6,0+380,A,6,850,0.012,42.10,52.20,52.05,8.5,15,9.60,41.30,,,"
           "SM,,,")


# --- T-5 --- EL CASO G2 PASA POR LA FASE 8 REAL desde T-5, y con la
# fabricacion del TMC por defecto (anular remachada SIMPLE, la mas
# desfavorable con costura tabulada) ninguna plancha de 68 x 13 desarrolla
# el empuje de ~8.5 m de relleno sobre 1.95 m: el TMC se descartaria por
# F8.COSTURA y el caso dejaria de medir lo que mide (la evaluacion entera del
# concreto). Los dos tests H1 declaran por eso la remachada DOBLE, que la
# ventana del criterio admite; que la simple NO alcanza lo fija
# `tests/test_t5_estructural_conducto.py`.
FABRICACION_DEL_CASO_G2 = {"fabricacion_tmc": "anular_remachada_doble"}


def _correr_csv(tmp_path, fila):
    cabecera = CSV_EJEMPLO.read_text(encoding="utf-8").splitlines()[0]
    ruta = tmp_path / "caso.csv"
    ruta.write_text(cabecera + "\n" + fila + "\n", encoding="utf-8")
    externos = cli.cargar_datos_externos(None, {
        "luz_m": LUZ, "TW_m": 0.3, "longitud_m": None,
        "L_hidraulico_m": None, "categoria_tr": None})
    (punto,) = cli.correr(ruta, externos, alcance=cli.ALCANCE_PERFIL).puntos
    return punto


def test_h1_el_caso_del_auditor_adopta_tmc_porque_el_concreto_se_evaluo_entero(
        del_expediente, tmp_path):
    """
    Rasante alta, Q = 6 m3/s, S = 0.012, TW = 0.3: el concreto incumple V3 en
    TODA su progresion. Con el tope en el ultimo diseño estandar (2.70 m,
    H2) el concreto se EVALUA ENTERO y se descarta por catalogo; adoptar el
    TMC es entonces legitimo. Antes el concreto se detenia en 2.85 m por
    falta de pared y el TMC se adoptaba igual, sin bloqueo.
    """
    with declarados(FABRICACION_DEL_CASO_G2):
        punto = _correr_csv(tmp_path, CASO_G2)
    assert punto.dimensionado and punto.resultado.material.tipo is TMC
    del_concreto = [e for e in punto.traza if "oncreto" in e.material]
    assert del_concreto[-1].seccion.etiqueta() == "Ø 2.70 m"
    assert not [e for e in del_concreto
                if MD.MARCA_ESCALON_SIN_EVALUAR in e.motivo], (
        "algun escalon del concreto quedo sin evaluar")


def test_h1_un_candidato_anterior_sin_evaluar_por_dato_bloquea_al_posterior(
        del_expediente, tmp_path):
    """
    La rama que H1 destapo, con el verificador REAL del pipeline: si al
    concreto le falta la pared de un escalon que tendria que evaluar, el
    punto NO sale dimensionado en TMC; sale bloqueado por el dato que falta,
    con su campo.
    """
    del_archivo = ca.CRITERIOS[CLAVE_ESPESOR_PARED].valor
    recortado = {**del_archivo, "concreto_reforzado": {
        d: t for d, t in del_archivo["concreto_reforzado"].items() if d <= 1950}}
    with declarados({CLAVE_ESPESOR_PARED: recortado, **FABRICACION_DEL_CASO_G2}):
        punto = _correr_csv(tmp_path, CASO_G2)
    assert not punto.dimensionado
    (bloqueo,) = [b for b in punto.bloqueos if "MD" in b.etapa]
    assert bloqueo.tipo.value == "DatoFaltanteError"
    assert "espesor_pared_conducto[concreto_reforzado][2100]" in bloqueo.mensaje


def test_h1_si_ninguno_cierra_el_motivo_dice_que_escalones_no_se_evaluaron(
        del_expediente, tmp_path):
    """
    B-01 del fixture, con los valores del archivo: sigue siendo NO FACTIBLE
    --los escalones evaluados incumplen-- y no cambia de tipo de bloqueo;
    pero el motivo dice que el HDPE no se evaluo desde 1.35 m y por que dato,
    en vez de llamar «no evaluable» a un material con tres escalones medidos.
    """
    b01 = _por_id(_corrida(tmp_path))["B-01"]
    assert not b01.dimensionado
    (bloqueo,) = [b for b in b01.bloqueos if "MD" in b.etapa]
    assert bloqueo.tipo.value == "DisenoNoFactibleError"
    for trozo in ("HDPE: 3 escalon(es) evaluado(s), de Ø 0.90 m a Ø 1.20 m",
                  "NO SE EVALUO desde Ø 1.35 m hasta el tope del material "
                  "(1.50 m)",
                  "espesor_pared_conducto[hdpe][1350]"):
        assert trozo in bloqueo.mensaje, trozo


def test_h7_la_plancha_adoptada_no_cumple_el_factor_de_flexibilidad_hasta_su_tope():
    """
    El tope de 2.10 m del TMC es el de la CORRUGACION. Con la plancha
    adoptada, FF = s2/(E I) pasa de 0.245 mm/N (ASTM A796 num. 10.3, 13 mm
    de profundidad, terraplen) desde ~1.39 m. M2 no duplica la Fase 8: lo
    dice en la ficha, en el rotulo del tope y en la ficha T4-08.
    """
    plancha = CN.TMC_PLANCHA_CORRUGADA[ca.valor(M2.CRITERIO_CALIBRE_TMC)]
    s_limite_mm = math.sqrt(0.245 * 200000 * plancha["I_mm4_mm"])
    assert s_limite_mm == pytest.approx(1386, abs=ABS_UN_MILIMETRO)
    assert s_limite_mm < M2.tope_de_diametro(TMC)[0] * MILIMETROS_POR_METRO
    ficha = ca.criterio(M2.CRITERIO_CALIBRE_TMC)
    assert "0.245 mm/N" in ficha.justificacion and "1.39 m" in ficha.justificacion
    assert "num. 10.3" in ficha.verificacion_pendiente
    assert "NO EL DE LA PLANCHA" in M2.ROTULO_TOPE_DE_CORRUGACION
    assert "ENVOLVENTE" in (RAIZ / "docs" / "decisiones_diferidas.md").read_text(
        encoding="utf-8")


def test_h11_la_fila_de_n_del_hdpe_se_apoya_en_la_norma_peruana(reg):
    cita = reg.cita("EG2013.508.02a")
    assert "superficie interior lisa" in cita.texto_literal.texto
    assert "EG2013.508.02a" in ca.criterio("n_manning_hdpe").fuente
