"""
tests/test_t7b_cabezal_estabilidad.py
=====================================
Aceptacion de T-7b: el ENSAMBLE DE ESTABILIDAD del cabezal en dos marcos que
no se cruzan (INF-4.4, INF-4.5, INF-5.1.5; fichas EXT-7-02 y EXT-7-04) y el
PUNTO 0 que lo hace alcanzable a nivel de expediente (residual de INF-4.2 e
INF-4.3, ficha T7A-01): V5 con metodo declarable, V8 con metodo y umbral
declarables, y las tres puertas de datos externos por punto.

Los oraculos son ARITMETICA ESCRITA, y estan en
`tests/fixtures/casos_patron.py` (`CP_T7B_ESTABILIDAD`, `CP_T7B_V5`): un muro
de tanteo calculado a mano con la forma de la ecuacion 3.11.5.3-1 de AASHTO
para K_A -- que no es la funcion del modulo, que deduce Coulomb de
Mononobe-Okabe --, las cargas con sus brazos, las combinaciones de cada marco
y las seis filas E1 a E3. Las cifras que el encargo cita del «PDF de VARIOS»
van aparte, en `CP_T7B_ENCARGO`, como CONTRASTE rotulado: la fuente no esta
en la sesion y no son un dorado.

NO SE ESCRIBIO EN ROJO CON `xfail(strict=True)`: el codigo y este archivo se
escribieron en la misma sesion. El rojo se MIDIO copiando este archivo y el
fixture a un checkout de `250c972`, y se declara en el informe de la FASE A
(ficha T7B-10 de `docs/decisiones_diferidas.md`).
"""

import ast
import inspect
import json
import math
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

import cli
from src import anticipo
from src import constantes_normativas as cn
from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src import modelos
from src import servicio
from src.modelos import (CARGA_DC, CARGA_EH, CARGA_EQ, CARGA_EV, CARGA_LS,
                         CARGA_WA, ELEMENTO_ALEROS, ELEMENTO_PANTALLA,
                         ELEMENTO_ZAPATA, MARCO_ASD, MARCO_ENVOLVENTE,
                         MARCO_LRFD, MARCO_RIGE_ASD, MARCO_RIGE_LRFD,
                         CondicionAnalisis, ControlGobernante,
                         CriterioPendienteError, DatoFaltanteError,
                         DatoInvalidoError, DerechoDeViaDelPunto,
                         DisenoNoFactibleError, EntornoDelCabezal,
                         ErrorProyecto, EstadoDeVerificacion,
                         EventoExtremoDelPunto, GeometriaCabezal,
                         MetodoNoEvaluableError, TipoDeBloqueo,
                         TipoDeVeredicto)
from src.modulos import M0_carga as M0
from src.modulos import M5_verificaciones as M5
from src.modulos import M9_cabezal as M9
from src.normativa import fuentes
from src.normativa.registro import construir
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import con_valor, sin_valor
from tests.fixtures.casos_patron import (CP_T7B_COHESIVO, CP_T7B_CUNA,
                                         CP_T7B_ENCARGO,
                                         CP_T7B_ESTABILIDAD, CP_T7B_MURO_2,
                                         CP_T7B_PEOR_COMBINACION,
                                         CP_T7B_SOLICITACIONES, CP_T7B_V5)

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
DECISIONES = RAIZ / "docs" / "decisiones_diferidas.md"
HOJA_DE_RUTA = RAIZ / "docs" / "hoja_de_ruta_alcantarillas_v8.md"
CONTRATO = RAIZ / "docs" / "contrato_entradas.md"

EST = CondicionAnalisis.ESTATICO
SIS = CondicionAnalisis.SISMICO
CP = CP_T7B_ESTABILIDAD
# Las tolerancias las DECLARA el caso patron (los dorados estan escritos a
# cuatro decimales: la tolerancia es la de esa escritura, no la de la
# maquina). ABS_CERO y REL_TRANSPORTE, para lo que solo se transporta.
TOL = CP["tolerancia"]              # kN/m, kN·m/m, m: cuatro decimales
REL = CP["tolerancia_rel"]          # presiones: relativa
TOL_K = CP["tolerancia_K"]          # coeficientes de empuje: seis decimales
TOL_FINA = CP["tolerancia_fina"]    # brazos y factores a cinco decimales
TOL_MM = CP["tolerancia_mm"]        # cifras escritas a tres decimales
TOL_CM = CP["tolerancia_cm"]        # cifras escritas a dos decimales

NUEVOS_T7B = (
    "umbral_no_colapso_evento_extremo", "marco_estabilidad_cabezal",
    "fila_phi_estabilidad_cabezal", "drenaje_trasdos",
    "peso_especifico_saturado_relleno_kn_m3",
    "fraccion_delta_sobre_phi_trasdos", "regla_pendiente_relleno_trasdos",
    "factores_inclinacion_carga_portante", "terreno_delante_del_cabezal")


# ---------------------------------------------------------------------------
# Apoyo: el muro de tanteo del dorado
# ---------------------------------------------------------------------------

def _geometria(**cambios) -> GeometriaCabezal:
    base = dict(CP["geometria"], cota_desplante=100.0, cota_coronacion=102.55,
                id_punto="T-00", extremo="entrada")
    base.update(cambios)
    return GeometriaCabezal(**base)


def _entorno(**cambios) -> EntornoDelCabezal:
    g = cambios.pop("geometria", None) or _geometria()
    base = dict(id_punto="T-00", extremo=g.extremo, geometria=g,
                cota_relleno=100.0 + CP["h"],
                cota_borde_plataforma=100.0 + CP["h"],
                origen_cota_borde="de prueba", talud=1.5, esviaje_grados=0.0,
                cota_freatico=100.0 + g.D_f - CP["NF"],
                cota_pie=100.0 + g.D_f, suelo=dict(CP["suelo"]))
    base.update(cambios)
    return EntornoDelCabezal(**base)


def _con_freatico(entorno, profundidad):
    """
    REESCRITO DECLARANDOLO (correcciones de T-7b, H1): el entorno ya no lleva
    la PROFUNDIDAD del freatico sino su COTA (`cota_freatico`), que
    `datos_del_cabezal_del_punto` deduce del terreno del CRUCE. En el muro
    de tanteo el terreno del cruce es el del pie, de modo que estos casos
    dicen lo mismo que antes: «a `profundidad` bajo el terreno del pie».
    """
    return replace(entorno, cota_freatico=(
        None if profundidad is None else entorno.cota_pie - profundidad))


def _declarar_sitio():
    """Los dos [S] de la sobrecarga viva: muro paralelo, borde a 1.60 m."""
    ds.establecer_dato_dinamico(
        "orientacion_muro_respecto_al_trafico", "paralelo_al_trafico",
        "de prueba (T-7b)", "2026-11-13", origen="prueba")
    ds.establecer_dato_dinamico(
        "distancia_borde_calzada_al_trasdos_m", 1.6,
        "de prueba (T-7b)", "2026-11-13", origen="prueba")


@pytest.fixture
def tanteo(monkeypatch):
    """
    Las declaraciones DE PRUEBA del muro de tanteo, por la puerta real
    (`establecer_valor_dinamico`: los tres valores caen en su ventana). El
    conftest repone el estado al salir. El coeficiente sismico se IMPONE
    (k_h = 0.25, k_v = 0): la cadena sismica del expediente es de T-anteriores
    y aqui se prueba lo que el ensamble hace con el.
    """
    ca.establecer_valor_dinamico("phi_relleno_trasdos", CP["phi_relleno"])
    ca.establecer_valor_dinamico("peso_especifico_relleno_kn_m3",
                                 CP["gamma_relleno"])
    ca.establecer_valor_dinamico("drenaje_trasdos", "drenado")
    _declarar_sitio()
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h=CP["sismico"]["k_h"], k_v=0.0))
    return _entorno()


def _carga(e, codigo):
    return next(c for c in e.cargas if c.codigo == codigo)


def _combo(e, fragmento, marco, para):
    hallados = [c for c in e.combinaciones
                if fragmento in c.nombre and c.marco == marco
                and c.para == para]
    assert len(hallados) == 1, [c.nombre for c in e.combinaciones]
    return hallados[0]


def _v(e, codigo):
    return next(v for v in e.verificaciones if v.codigo == codigo)


# ===========================================================================
# 1. LAS TABLAS DE AASHTO, CONTRA SU PAGINA
# ===========================================================================

@pytest.mark.pdf
@pytest.mark.parametrize("fuente_id, pagina_pdf, fragmentos", [
    # Tabla 10.6.3.1.2a-1: tres filas enteras (phi, Nc, Nq, Ngamma).
    ("AASHTO_LRFD_9", 1361, ("30 30.1 18.4 22.4", "32 35.5 23.2 30.2",
                             "34 42.2 29.4 41.1")),
    # Tabla 11.5.7-1: el portante y el deslizamiento de muros de gravedad.
    ("AASHTO_LRFD_9", 1486, ("Gravity and semigravity walls • MSE walls 0.55 "
                             "0.65", "Sliding 1.0")),
    # Tabla 10.5.5.2.2-1: el portante de las zapatas.
    ("AASHTO_LRFD_9", 1331, ("in clay 0.50", "in sand, using SPT 0.45")),
    # Art. 11.5.8: el portante del evento extremo NO es 1.0.
    ("AASHTO_LRFD_9", 1487, ("a resistance factor of 0.8 shall be used for "
                             "gravity and semigravity walls",)),
])
def test_los_numeros_de_T7b_estan_en_la_pagina_que_se_cita(
        fuente_id, pagina_pdf, fragmentos):
    from src.normativa.extraccion import texto_de_pagina
    ruta = fuentes.ruta_pdf(fuentes.FUENTES[fuente_id])
    if not ruta.exists():
        pytest.skip(f"el PDF de {fuente_id} no esta enlazado")
    texto = " ".join(texto_de_pagina(ruta, pagina_pdf).split())
    for fragmento in fragmentos:
        assert fragmento in texto, (fuente_id, pagina_pdf, fragmento)


def test_la_tabla_de_factores_de_capacidad_esta_entera_y_es_monotona():
    """46 filas, de phi = 0 a 45; las tres columnas crecen con phi."""
    t = cn.FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1
    assert sorted(t) == list(range(46))
    assert t[0] == (5.14, 1.0, 0.0)  # float-exacto: transcrito o declarado, no calculado
    assert t[32] == (35.5, 23.2, 30.2)  # float-exacto: transcrito o declarado, no calculado
    assert t[45] == (133.9, 134.9, 271.8)  # float-exacto: transcrito o declarado, no calculado
    # La tabla se imprime a un decimal: N_gamma repite 0.2 en phi = 2 y 3.
    for phi in range(45):
        assert all(a <= b for a, b in zip(t[phi], t[phi + 1])), phi
        assert t[phi][0] < t[phi + 1][0], phi


def test_los_factores_de_capacidad_interpolan_entre_filas_y_no_extrapolan():
    """
    A mano, entre phi = 32 (35.5, 23.2, 30.2) y 33 (38.6, 26.1, 35.2), a
    32.5: (37.05, 24.65, 32.70).
    """
    Nc, Nq, Ng = M9.factores_de_capacidad_de_carga(32.5)
    assert (Nc, Nq, Ng) == pytest.approx((37.05, 24.65, 32.70), abs=ABS_CERO)
    assert M9.factores_de_capacidad_de_carga(32.0) == (35.5, 23.2, 30.2)  # float-exacto: transcrito o declarado, no calculado
    with pytest.raises(DatoInvalidoError):
        M9.factores_de_capacidad_de_carga(45.5)
    with pytest.raises(DatoInvalidoError):
        M9.factores_de_capacidad_de_carga(float("nan"))


@pytest.mark.parametrize("D_w, esperado", [
    # D_f = 0.80, B = 2.00: a D_f + 1.5·B = 3.80 m o mas el agua no cuenta.
    (0.0, (0.5, 0.5)),            # agua en la superficie
    (0.80, (1.0, 0.5)),           # agua en el nivel de la zapata
    (3.80, (1.0, 1.0)),           # agua a 1.5·B bajo la zapata
    (9.0, (1.0, 1.0)),
    (0.40, (0.75, 0.5)),          # a media profundidad de desplante
    (2.30, (1.0, 0.75)),          # a media altura de la zona de 1.5·B
])
def test_los_coeficientes_del_freatico_son_los_de_la_tabla_e_interpolan(
        D_w, esperado):
    """Tabla 10.6.3.1.2a-2 de AASHTO; entre posiciones, lineal (a mano)."""
    assert M9.coeficientes_de_nivel_freatico(D_w=D_w, D_f=0.80, B=2.0) \
        == pytest.approx(esperado, abs=ABS_CERO)


def test_los_factores_de_resistencia_salen_de_la_fila_declarada():
    """
    Estatica: Tabla 10.5.5.2.2-1 (0.45 / 0.80 en friccionante; 0.50 / 0.85
    en cohesivo) o Tabla 11.5.7-1 (0.55 / 1.0), segun el criterio. Sismica:
    11.5.8, 0.8 en el portante -- NO «phi = 1.0» a secas -- y 1.0 en el
    deslizamiento, sin eleccion.
    """
    f = M9.factores_de_resistencia(EST, cohesivo=False)
    assert (f["portante"], f["deslizamiento"]) == (0.45, 0.80)  # float-exacto: transcrito o declarado, no calculado
    f = M9.factores_de_resistencia(EST, cohesivo=True)
    assert (f["portante"], f["deslizamiento"]) == (0.50, 0.85)  # float-exacto: transcrito o declarado, no calculado
    ca.establecer_valor_dinamico("fila_phi_estabilidad_cabezal",
                                 "muros_tabla_11_5_7")
    f = M9.factores_de_resistencia(EST, cohesivo=False)
    assert (f["portante"], f["deslizamiento"]) == (0.55, 1.0)  # float-exacto: transcrito o declarado, no calculado
    f = M9.factores_de_resistencia(SIS, cohesivo=False)
    assert (f["portante"], f["deslizamiento"]) == (0.8, 1.0)  # float-exacto: transcrito o declarado, no calculado
    assert f["criterio"] is None


# ===========================================================================
# 2. LOS CRITERIOS: nada inventado, y nada con valor donde el dueño dijo que no
# ===========================================================================

def test_los_nueve_criterios_nuevos_estan_al_final_y_son_de_expediente():
    claves = list(ca.CRITERIOS)
    for clave in NUEVOS_T7B:
        c = ca.CRITERIOS[clave]
        assert c.nivel == ca.NIVEL_EXPEDIENTE, clave
        assert c.justificacion.strip(), clave
    # Al final de su seccion: los nueve van seguidos, en este orden.
    indices = [claves.index(k) for k in NUEVOS_T7B]
    assert indices == list(range(indices[0], indices[0] + len(NUEVOS_T7B)))


@pytest.mark.parametrize("clave", ["remanso_derecho_via",
                                   "umbral_no_colapso_evento_extremo",
                                   "TR_evento_extremo", "c_phi_fundacion",
                                   "phi_relleno_trasdos",
                                   "peso_especifico_saturado_relleno_kn_m3"])
def test_lo_que_el_programa_no_puede_elegir_sigue_sin_valor_de_archivo(clave):
    """
    Decision del dueño (PUNTO 0): el metodo de V5 y lo de V8 son DECLARABLES
    y no tienen valor de archivo; los parametros del suelo y del relleno son
    del ensayo. Sin declarar nada, ningun resultado del fixture cambia.
    """
    assert ca.CRITERIOS[clave].valor is None
    with pytest.raises(CriterioPendienteError):
        ca.valor(clave)


@pytest.mark.parametrize("clave, valor, ventana", [
    ("marco_estabilidad_cabezal", MARCO_RIGE_LRFD,
     (MARCO_RIGE_LRFD, MARCO_RIGE_ASD, MARCO_ENVOLVENTE)),
    ("fila_phi_estabilidad_cabezal", "zapatas_seccion_10",
     ("zapatas_seccion_10", "muros_tabla_11_5_7")),
    ("drenaje_trasdos", "sin_drenaje", ("sin_drenaje", "drenado")),
    # CORRECCIONES DE T-7b (H4), declarado: la regla de archivo paso de
    # «talud_quebrado_2h» a la cuña de tanteo, que entra en la ventana.
    ("regla_pendiente_relleno_trasdos", "cuna_de_tanteo",
     ("cuna_de_tanteo", "talud_quebrado_2h", "talud_del_terraplen")),
    # CORRECCIONES DE T-7b (H7): el regimen del cabezal.
    ("regimen_cabezal", "cedente", ("cedente", "no_cedente")),
    ("factores_inclinacion_carga_portante", "aplicar", ("aplicar", "omitir")),
    ("terreno_delante_del_cabezal", "horizontal",
     ("horizontal", "talud_descendente")),
    # CORRECCIONES DE T-7b (H2), declarado: el metodo de COTA que la fuente
    # sostiene entra en la ventana, sin valor de archivo.
    ("remanso_derecho_via", None,
     ("embalse_a_nivel", "cota_de_afectacion",
      "perfil_de_remanso_paso_a_paso")),
    ("umbral_no_colapso_evento_extremo", None,
     ("sin_desborde_de_la_plataforma",
      "desborde_admitido_con_terraplen_protegido")),
])
def test_las_categorias_tienen_su_conjunto_cerrado_y_la_puerta_lo_exige(
        clave, valor, ventana):
    c = ca.CRITERIOS[clave]
    assert c.forma == ca.FORMA_CATEGORIA
    assert c.valor == valor
    assert tuple(c.sensibilidad) == ventana
    assert c.etiqueta == "A"
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(clave, "otra_cosa")
    for opcion in ventana:
        ca.establecer_valor_dinamico(clave, opcion)


def test_el_marco_que_rige_es_el_LRFD_por_decision_del_dueno():
    """Opcion (b) del dictamen: rige LRFD (AASHTO 11.6), ASD informa."""
    c = ca.CRITERIOS["marco_estabilidad_cabezal"]
    assert c.valor == MARCO_RIGE_LRFD == "lrfd_rige_asd_informa"
    assert "dueño" in c.justificacion or "dueno" in c.justificacion.lower()


def test_delta_sale_de_phi_por_una_fraccion_con_fuente():
    c = ca.CRITERIOS["fraccion_delta_sobre_phi_trasdos"]
    assert (c.valor, c.etiqueta) == (0.67, "C")  # float-exacto: transcrito o declarado, no calculado
    assert tuple(c.sensibilidad) == (0.33, 0.67)  # float-exacto: transcrito o declarado, no calculado
    assert "C3.11.5.3" in c.fuente


def test_los_cuatro_angulos_ya_no_detienen_el_caso_estatico():
    """
    Punto 5 del encargo: de los cuatro angulos solo phi (dato del ensayo del
    relleno) puede detener. delta, i y beta tienen origen.
    """
    assert ca.CRITERIOS["phi_relleno_trasdos"].valor is None
    assert ca.CRITERIOS["inclinacion_muro_beta"].valor == 0.0  # float-exacto: transcrito o declarado, no calculado
    for clave in ("friccion_muro_suelo_delta", "pendiente_relleno_trasdos_i"):
        c = ca.CRITERIOS[clave]
        assert c.opcional and c.valor is None and c.sensibilidad, clave
    assert ca.CRITERIOS["gamma_EQ"].valor == 0.5  # float-exacto: transcrito o declarado, no calculado
    assert ca.CRITERIOS["punto_aplicacion_incremento_sismico"].valor == 0.6  # float-exacto: transcrito o declarado, no calculado


# ===========================================================================
# 3. V5: EL EMBALSE A NIVEL
# ===========================================================================

def _punto_v5(S=CP_T7B_V5["S_cauce"], esviaje=CP_T7B_V5["esviaje"]):
    return SimpleNamespace(id="A-01", esviaje_grados=esviaje,
                           exigir=lambda nombre: S)


def _resultado_v5(HW=1.042):
    return SimpleNamespace(HW=HW, control_gobernante=ControlGobernante.ENTRADA)


def _derecho(ancho, semilongitud=9.317):
    return DerechoDeViaDelPunto(
        ancho_m=ancho, origen_ancho="dato externo de prueba",
        semilongitud_entrada_m=semilongitud,
        origen_semilongitud="semilongitud de entrada de 7.B (de prueba)")


def test_v5_sin_metodo_declarado_se_detiene_en_el_criterio():
    """Como antes de T-7b: nada declarado, nada cambia."""
    with pytest.raises(CriterioPendienteError) as e:
        M5.v5_remanso(punto=_punto_v5(), resultado=_resultado_v5(),
                      derecho_de_via=_derecho(400.0))
    assert e.value.clave == "remanso_derecho_via"


def test_v5_con_metodo_y_sin_ancho_se_detiene_en_el_dato_y_dice_cual():
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")
    for derecho in (None, _derecho(None)):
        with pytest.raises(DatoFaltanteError) as e:
            M5.v5_remanso(punto=_punto_v5(), resultado=_resultado_v5(),
                          derecho_de_via=derecho)
        assert e.value.campo == "ancho_derecho_via_m"
        assert "--datos-externos" in str(e.value)


def test_v5_embalse_a_nivel_el_dorado_a_mano():
    """
    x = 1.042 / 0.006 = 173.6667 m; d = (9.317 + 173.6667)·cos 15
    = 182.9837·0.965926 = 176.749 m <= 400/2 = 200 m. Margen 23.251 m.
    """
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")
    v = M5.v5_remanso(punto=_punto_v5(), resultado=_resultado_v5(),
                      derecho_de_via=_derecho(CP_T7B_V5["ancho_que_cumple"]))
    d = (9.317 + 1.042 / 0.006) * CP_T7B_V5["cos_15"]
    assert v.valor_obtenido == pytest.approx(d, abs=TOL_MM)
    assert v.valor_obtenido == pytest.approx(176.749, abs=TOL_MM)
    assert v.valor_admisible == pytest.approx(200.0, abs=ABS_CERO)
    assert v.cumple and v.codigo == "V5"
    assert v.criterio_aplicado == "remanso_derecho_via"
    assert v.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE
    assert v.paso.veredicto.margen == pytest.approx(200.0 - d, abs=TOL_MM)


def test_v5_puede_fallar_con_un_derecho_de_via_estrecho():
    """PRECISIONES: V5 no es un tramite. 176.75 > 300/2 = 150 -> no cumple."""
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")
    v = M5.v5_remanso(punto=_punto_v5(), resultado=_resultado_v5(),
                      derecho_de_via=_derecho(CP_T7B_V5["ancho_que_no"]))
    assert not v.cumple
    assert v.estado is EstadoDeVerificacion.NO_CUMPLE
    assert v.valor_admisible == pytest.approx(150.0, abs=ABS_CERO)
    assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
    assert v.paso.veredicto.margen < 0


def test_v5_el_paso_dice_los_supuestos_y_no_presume_el_lado():
    """Los supuestos del metodo viajan en la memoria, no en un docstring."""
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")
    v = M5.v5_remanso(punto=_punto_v5(), resultado=_resultado_v5(),
                      derecho_de_via=_derecho(400.0))
    nota = v.paso.nota_del_proyecto
    for frase in ("plano horizontal", "NO es la curva de remanso",
                  "simetrica", "topografia"):
        assert frase.lower() in nota.lower(), frase
    assert v.paso.umbral.cita_id
    simbolos = [m.simbolo for m in v.paso.sustitucion]
    assert simbolos == ["HW", "S_cauce", "x_embalse", "L_boca", "esviaje",
                        "ancho_derecho_via"]


def test_la_faja_simetrica_es_una_lectura_declarada_y_el_paso_la_cita():
    """
    La fuente da un ANCHO; V5 compara con su MITAD. Que la faja sea simetrica
    respecto del eje es lectura del proyecto, declarada como `Interpretacion`
    en la cita que el paso imprime, con lo que juega en contra.
    """
    cita = construir().cita("DG2018.304.07.02")
    assert cita.interpretacion is not None
    assert "simetrica" in cita.interpretacion.texto
    assert cita.interpretacion.en_contra and cita.interpretacion.a_favor
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")
    v = M5.v5_remanso(punto=_punto_v5(), resultado=_resultado_v5(),
                      derecho_de_via=_derecho(400.0))
    assert "DG2018.304.07.02" in v.paso.citas_textuales
    assert "HDS5_3ED.2.2.5#EMBALSE" in v.paso.citas_textuales


def test_v5_el_metodo_nombrado_y_no_implementado_no_da_cifra():
    ca.establecer_valor_dinamico("remanso_derecho_via",
                                 "perfil_de_remanso_paso_a_paso")
    with pytest.raises(MetodoNoEvaluableError) as e:
        M5.v5_remanso(punto=_punto_v5(), resultado=_resultado_v5(),
                      derecho_de_via=_derecho(400.0))
    assert str(e.value).startswith(modelos.MOTIVO_METODO_NO_EVALUABLE_REMANSO)
    assert not str(e.value).startswith(modelos.MOTIVO_METODO_NO_EVALUABLE)


@pytest.mark.parametrize("S", [0.0, -0.01, float("nan")])
def test_v5_sin_pendiente_de_cauce_no_hay_extension_finita(S):
    """
    Forma MAT-D13: `not S > 0`. Con S = 0 el plano no corta el fondo; un NaN
    es un dato que no es numero. Ninguno de los tres entrega una distancia.
    """
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")
    with pytest.raises((MetodoNoEvaluableError, DatoInvalidoError)):
        M5.v5_remanso(punto=_punto_v5(S=S), resultado=_resultado_v5(),
                      derecho_de_via=_derecho(400.0))


@pytest.mark.parametrize("ancho", [0.0, -10.0, float("inf"), True, "400"])
def test_v5_un_ancho_que_no_puede_ser_es_dato_invalido(ancho):
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")
    with pytest.raises(DatoInvalidoError):
        M5.v5_remanso(punto=_punto_v5(), resultado=_resultado_v5(),
                      derecho_de_via=_derecho(ancho))


def test_v5_el_esviaje_proyecta_y_la_extension_crece_con_la_carga():
    """d(esviaje = 0) = L + HW/S; a 60 grados, la mitad. Y d crece con HW."""
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")

    def d(HW, esviaje):
        return M5.v5_remanso(
            punto=_punto_v5(esviaje=esviaje), resultado=_resultado_v5(HW),
            derecho_de_via=_derecho(4000.0)).valor_obtenido

    assert d(1.2, 0.0) == pytest.approx(9.317 + 1.2 / 0.006, abs=ABS_CERO)
    assert d(1.2, 60.0) == pytest.approx(d(1.2, 0.0) / 2, abs=ABS_CERO)
    assert d(0.6, 0.0) < d(1.2, 0.0) < d(1.8, 0.0)


# --- lo que la mutacion enseño de V5 (arnes de EXT-11) ---------------------

def test_v5_el_umbral_es_inclusivo():
    """
    d = 9.317 + 1.2/0.006 = 209.317 m con esviaje 0; con una faja de
    418.634 m la mitad es exactamente esa distancia: cumple, con margen 0.
    """
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")
    v = M5.v5_remanso(punto=_punto_v5(esviaje=0.0),
                      resultado=_resultado_v5(1.2),
                      derecho_de_via=_derecho(418.634))
    assert v.cumple
    assert v.paso.veredicto.margen == pytest.approx(0.0, abs=TOL_K)


def test_v5_admite_carga_nula_y_boca_en_el_eje_y_rechaza_las_negativas():
    """
    HW = 0 y semilongitud = 0 son valores posibles (cada uno por separado
    deja una distancia finita); una carga o una semilongitud NEGATIVA no,
    aunque la otra sea buena. Y un ancho menor que un metro es un ancho.
    """
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")

    def v5(HW, semilongitud, ancho=400.0):
        return M5.v5_remanso(
            punto=_punto_v5(esviaje=0.0), resultado=_resultado_v5(HW),
            derecho_de_via=_derecho(ancho, semilongitud))

    assert v5(0.0, 9.317).valor_obtenido == pytest.approx(9.317, abs=ABS_CERO)
    assert v5(0.3, 0.0).valor_obtenido == pytest.approx(0.3 / 0.006,
                                                        rel=REL_TRANSPORTE)
    assert v5(0.3, 0.5).cumple
    assert not v5(0.3, 0.5, ancho=0.8).cumple
    for HW, semilongitud in ((-0.5, 9.317), (0.5, -9.317)):
        with pytest.raises(DatoInvalidoError):
            v5(HW, semilongitud)


@pytest.mark.parametrize("clave, llamar", [
    ("remanso_derecho_via",
     lambda: M5.v5_remanso(punto=_punto_v5(), resultado=_resultado_v5(),
                           derecho_de_via=_derecho(400.0))),
])
def test_un_metodo_de_V5_que_burla_la_puerta_lo_rechaza_el_consumidor(
        clave, llamar):
    with con_valor(clave, "a_ojo",
                   motivo="segunda linea: el consumidor no confia en la "
                          "puerta"):
        with pytest.raises(DatoInvalidoError) as e:
            llamar()
    assert "embalse_a_nivel" in str(e.value)


# ===========================================================================
# 4. V8: EL EVENTO EXTREMO
# ===========================================================================

def _punto_real(id_punto="A-01"):
    return next(p for p in M0.cargar_puntos(CSV_EJEMPLO) if p.id == id_punto)


def _evento(Q=1.3, TW=0.5, HW_ext=1.147, cota=44.2, resolver="si"):
    if resolver == "si":
        def resolver(seccion, material):
            return SimpleNamespace(
                HW=HW_ext, control_gobernante=ControlGobernante.ENTRADA)
    return EventoExtremoDelPunto(
        Q_m3s=Q, TW_m=TW, origen="dato externo de prueba",
        cota_desborde=cota, origen_cota_desborde="rasante (de prueba)",
        resolver=resolver)


def _llamar_v8(evento, Q_diseno=1.167):
    return M5.v8_evento_extremo(
        punto=_punto_real(),
        resultado=SimpleNamespace(
            Q=Q_diseno, control_gobernante=ControlGobernante.ENTRADA),
        material=SimpleNamespace(nombre="concreto"),
        seccion=SimpleNamespace(etiqueta=lambda: "Ø 0.90 m"), evento=evento)


def test_v8_se_detiene_en_orden_y_nunca_con_un_fallo_de_programa():
    """
    TR sin valor -> criterio; sin caudal -> dato; sin tirante del receptor ->
    dato; sin umbral -> criterio. Cada parada nombra lo que la destraba.
    """
    with pytest.raises(CriterioPendienteError) as e:
        _llamar_v8(_evento())
    assert e.value.clave == "TR_evento_extremo"
    ca.establecer_valor_dinamico("TR_evento_extremo", 500.0)
    with pytest.raises(DatoFaltanteError) as e:
        _llamar_v8(_evento(Q=None))
    assert e.value.campo == "Q_evento_extremo_m3s"
    with pytest.raises(DatoFaltanteError) as e:
        _llamar_v8(_evento(TW=None))
    assert e.value.campo == "TW_evento_extremo_m"
    with pytest.raises(CriterioPendienteError) as e:
        _llamar_v8(_evento())
    assert e.value.clave == "umbral_no_colapso_evento_extremo"


def _declarar_v8():
    ca.establecer_valor_dinamico("TR_evento_extremo", 500.0)
    ca.establecer_valor_dinamico("umbral_no_colapso_evento_extremo",
                                 "sin_desborde_de_la_plataforma")


def test_v8_compara_la_cota_del_embalse_con_la_de_desborde():
    """
    A-01: fondo de entrada adoptado en el terreno, 42.10 m. Con HW(Q_ext) =
    1.147 m el embalse llega a 43.247 m <= 44.20 m de la rasante: cumple, con
    0.953 m de margen. Con HW = 2.20 m llega a 44.30 m: desborda.
    """
    _declarar_v8()
    v = _llamar_v8(_evento())
    assert v.codigo == "V8" and v.cumple
    assert v.valor_obtenido == pytest.approx(42.10 + 1.147, abs=ABS_CERO)
    assert v.valor_admisible == pytest.approx(44.2, abs=ABS_CERO)
    assert v.criterio_aplicado == "umbral_no_colapso_evento_extremo"
    assert v.paso.veredicto.margen == pytest.approx(0.953, abs=ABS_CERO)
    v = _llamar_v8(_evento(HW_ext=2.20))
    assert not v.cumple
    assert v.valor_obtenido == pytest.approx(44.30, abs=ABS_CERO)


def test_v8_no_escala_ni_acepta_un_caudal_menor_que_el_de_diseno():
    _declarar_v8()
    with pytest.raises(DatoInvalidoError) as e:
        _llamar_v8(_evento(Q=1.0))
    assert e.value.campo == "Q_evento_extremo_m3s"
    for malo in (0.0, -1.0, float("nan"), True):
        with pytest.raises(DatoInvalidoError):
            _llamar_v8(_evento(Q=malo))


def test_v8_el_umbral_es_inclusivo_y_el_caudal_puede_ser_el_de_diseno():
    """
    Con HW(Q_ext) = 2.10 m el embalse llega justo a la rasante (42.10 + 2.10
    = 44.20 m): no desborda. Y un evento extremo con el MISMO caudal del
    diseño es admisible; tambien uno menor de 1 m3/s si el de diseño lo es.
    """
    _declarar_v8()
    v = _llamar_v8(_evento(HW_ext=2.10))
    assert v.cumple
    assert v.paso.veredicto.margen == pytest.approx(0.0, abs=TOL_K)
    assert _llamar_v8(_evento(Q=1.167)).cumple
    assert _llamar_v8(_evento(Q=0.5), Q_diseno=0.4).cumple


@pytest.mark.parametrize("malo", [float("inf"), "1.3", None.__class__])
def test_v8_un_caudal_que_no_es_un_numero_finito_es_dato_invalido(malo):
    _declarar_v8()
    with pytest.raises(DatoInvalidoError) as e:
        _llamar_v8(_evento(Q=malo))
    assert e.value.campo == "Q_evento_extremo_m3s"


def test_v8_sin_lo_que_el_servicio_le_entrega_se_detiene_en_un_dato():
    """
    Una llamada suelta sin la funcion que resuelve la hidraulica, o sin la
    cota de desborde: `DatoFaltanteError`, cada falta por separado. Y una
    cota de desborde que no es finita no da un «cumple».
    """
    _declarar_v8()
    for evento in (_evento(resolver=None), _evento(cota=None)):
        with pytest.raises(DatoFaltanteError) as e:
            _llamar_v8(evento)
        assert e.value.campo == "cota_desborde"
    with pytest.raises(ErrorProyecto) as e:
        _llamar_v8(_evento(cota=float("inf")))
    assert type(e.value).__name__ == "LimiteNumericoError"
    with con_valor("umbral_no_colapso_evento_extremo", "a_ojo",
                   motivo="segunda linea: el consumidor no confia en la "
                          "puerta"):
        with pytest.raises(DatoInvalidoError) as e:
            _llamar_v8(_evento())
    assert "sin_desborde_de_la_plataforma" in str(e.value)


def test_v8_lo_que_no_sabe_calcular_lo_dice_con_su_rotulo():
    """
    La seccion no conduce el caudal en lamina libre, o el umbral declarado
    admite el desborde: `MetodoNoEvaluableError` con el rotulo del evento
    extremo, no con el de HDS-5.
    """
    _declarar_v8()
    with pytest.raises(MetodoNoEvaluableError) as e:
        _llamar_v8(_evento(resolver=lambda seccion, material: None))
    assert str(e.value).startswith(
        modelos.MOTIVO_METODO_NO_EVALUABLE_EVENTO_EXTREMO)
    ca.establecer_valor_dinamico("umbral_no_colapso_evento_extremo",
                                 "desborde_admitido_con_terraplen_protegido")
    with pytest.raises(MetodoNoEvaluableError):
        _llamar_v8(_evento())


# ===========================================================================
# 5. LAS PUERTAS DE DATOS EXTERNOS Y EL PRE-VUELO
# ===========================================================================

def _externos(tmp_path, puntos=None, globales=None):
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps({"globales": globales or {},
                                "puntos": puntos or {}}), encoding="utf-8")
    return servicio.cargar_datos_externos(ruta, {})


def test_las_tres_claves_de_V5_y_V8_son_datos_externos_por_punto():
    """
    REESCRITO DECLARANDOLO (correcciones de T-7b, H2): son CUATRO desde que
    V5 tiene el metodo de cota, cuyo dato es la cota de afectacion aguas
    arriba; `CLAVES_EXTERNAS` pasa de 24 a 25. La cota admite cero y signo.
    """
    assert servicio.CLAVES_DE_V5_Y_V8 == (
        "ancho_derecho_via_m", "Q_evento_extremo_m3s", "TW_evento_extremo_m",
        "cota_afectacion_aguas_arriba_msnm")
    for clave in servicio.CLAVES_DE_V5_Y_V8:
        assert clave in servicio.CLAVES_EXTERNAS
    assert len(servicio.CLAVES_EXTERNAS) == 25
    cota = "cota_afectacion_aguas_arriba_msnm"
    assert {f.value for f in servicio.FAMILIAS_QUE_USAN[cota]} == {"A", "B"}
    assert cota in servicio.CLAVES_QUE_ADMITEN_CERO
    assert cota in servicio.CLAVES_CON_SIGNO
    assert servicio.METODO_QUE_EXIGE_LA_CLAVE == {
        "ancho_derecho_via_m": "embalse_a_nivel",
        cota: "cota_de_afectacion"}
    # El ancho del derecho de via es de las Familias A y B: en la C la
    # sustituye VC1 y el dato no se pide.
    familias = servicio.FAMILIAS_QUE_USAN["ancho_derecho_via_m"]
    assert {f.value for f in familias} == {"A", "B"}
    assert "TW_evento_extremo_m" in servicio.CLAVES_QUE_ADMITEN_CERO
    assert "ancho_derecho_via_m" not in servicio.CLAVES_QUE_ADMITEN_CERO


@pytest.mark.parametrize("clave, malo", [
    ("ancho_derecho_via_m", 0.0), ("ancho_derecho_via_m", -20.0),
    ("ancho_derecho_via_m", 1.0e6), ("ancho_derecho_via_m", "veinte"),
    ("Q_evento_extremo_m3s", 0.0), ("Q_evento_extremo_m3s", -1.0),
    ("TW_evento_extremo_m", -0.1),
])
def test_un_dato_de_V5_o_V8_que_no_puede_ser_no_entra(tmp_path, clave, malo):
    with pytest.raises(DatoInvalidoError):
        _externos(tmp_path, puntos={"A-01": {clave: malo}})


def test_el_tirante_del_evento_extremo_admite_cero(tmp_path):
    ext = _externos(tmp_path, puntos={"A-01": {"TW_evento_extremo_m": 0.0}})
    assert ext.valor("A-01", "TW_evento_extremo_m") == pytest.approx(
        0.0, abs=ABS_CERO)


def test_el_suelo_de_fundacion_por_punto_se_valida_en_la_puerta(tmp_path):
    bueno = {"cohesivo": False, "c_kpa": 0.0, "phi_grados": 32.0,
             "gamma_kn_m3": 18.0}
    ext = _externos(tmp_path, puntos={"A-01": {"suelo_fundacion": bueno}})
    assert ext.valor("A-01", "suelo_fundacion") == bueno
    for malo in ({"cohesivo": False, "c_kpa": 0.0, "phi_grados": 32.0},
                 dict(bueno, phi_grados=-5.0), dict(bueno, phi_grados=60.0),
                 dict(bueno, cohesivo="no"), dict(bueno, gamma_kn_m3=0.0),
                 dict(bueno, otro=1.0), dict(bueno, q_n_kpa=-10.0),
                 "arena", [1, 2]):
        with pytest.raises(DatoInvalidoError):
            _externos(tmp_path, puntos={"A-01": {"suelo_fundacion": malo}})


def test_el_prevuelo_no_anuncia_los_datos_de_V5_y_V8_sin_su_criterio():
    """
    Mientras 'remanso_derecho_via' y 'TR_evento_extremo' sigan vacios, V5 y
    V8 se detienen en el criterio y el dato todavia no falta: el pre-vuelo
    del fixture no gana ninguna falta.
    """
    externos = servicio.cargar_datos_externos(None, {})
    faltas = anticipo.datos_faltantes_por_punto(
        CSV_EJEMPLO, externos, servicio.ALCANCE_EXPEDIENTE)
    assert not [f for f in faltas if f.dato in servicio.CLAVES_DE_V5_Y_V8]


def test_el_prevuelo_si_los_anuncia_al_declarar_el_criterio_y_solo_a_expediente():
    externos = servicio.cargar_datos_externos(None, {})
    ca.establecer_valor_dinamico("remanso_derecho_via", "embalse_a_nivel")
    ca.establecer_valor_dinamico("TR_evento_extremo", 500.0)
    faltas = anticipo.datos_faltantes_por_punto(
        CSV_EJEMPLO, externos, servicio.ALCANCE_EXPEDIENTE)
    por_dato = {}
    for f in faltas:
        if f.dato in servicio.CLAVES_DE_V5_Y_V8:
            por_dato.setdefault(f.dato, set()).add(f.id_punto)
            assert f.detiene and f.etapa == servicio.ETAPA_BUCLE_DE_MD
    # V5 es de las Familias A y B (tres puntos); V8, de los cuatro.
    assert por_dato["ancho_derecho_via_m"] == {"A-01", "A-02", "B-01"}
    assert por_dato["Q_evento_extremo_m3s"] == {"A-01", "A-02", "B-01", "C-01"}
    assert por_dato["TW_evento_extremo_m"] == {"A-01", "A-02", "B-01", "C-01"}
    # (H2) Cada metodo de V5 pide SU dato: con «embalse_a_nivel» no se
    # anuncia la cota de afectacion, y con «cota_de_afectacion», al reves.
    assert "cota_afectacion_aguas_arriba_msnm" not in por_dato
    ca.establecer_valor_dinamico("remanso_derecho_via", "cota_de_afectacion")
    otra = {f.dato for f in anticipo.datos_faltantes_por_punto(
        CSV_EJEMPLO, externos, servicio.ALCANCE_EXPEDIENTE)
        if f.id_punto == "A-01"}
    assert "cota_afectacion_aguas_arriba_msnm" in otra
    assert "ancho_derecho_via_m" not in otra
    a_perfil = anticipo.datos_faltantes_por_punto(
        CSV_EJEMPLO, externos, servicio.ALCANCE_PERFIL)
    assert not [f for f in a_perfil if f.dato in servicio.CLAVES_DE_V5_Y_V8]


# ===========================================================================
# 6. EL ENSAMBLE: CARGAS, COMBINACIONES Y LAS SEIS FILAS, CONTRA EL DORADO
# ===========================================================================

def test_K_A_de_la_ecuacion_de_AASHTO_y_la_del_modulo_coinciden(tanteo):
    """
    El dorado esta calculado con la ec. 3.11.5.3-1 (Gamma); el modulo deduce
    Coulomb de Mononobe-Okabe con k_h = 0. Son dos escrituras de lo mismo.
    """
    phi, delta = math.radians(30.0), math.radians(20.1)
    gamma_mayus = (1 + math.sqrt(math.sin(phi + delta) * math.sin(phi)
                                 / math.sin(math.pi / 2 - delta))) ** 2
    a_mano = math.sin(math.pi / 2 + phi) ** 2 / (
        gamma_mayus * math.sin(math.pi / 2 - delta))
    assert a_mano == pytest.approx(CP["K_A"], abs=TOL_K)
    e = M9.ensamble_estabilidad(tanteo, EST)
    assert e.K_A == pytest.approx(CP["K_A"], abs=TOL_K)
    assert e.delta_grados == pytest.approx(CP["delta"], abs=ABS_CERO)
    assert e.i_grados == pytest.approx(0.0, abs=ABS_CERO)
    assert e.altura_empuje == pytest.approx(CP["h"], abs=ABS_CERO)
    assert e.h_eq == pytest.approx(CP["h_eq"], abs=ABS_CERO)


def test_las_cargas_sin_factorar_y_sus_brazos_son_las_del_dorado(tanteo):
    e = M9.ensamble_estabilidad(tanteo, EST)
    assert [c.codigo for c in e.cargas] == list(CP["cargas"])
    for codigo, (V, H, x, z) in CP["cargas"].items():
        c = _carga(e, codigo)
        assert c.V == pytest.approx(V, abs=TOL), codigo
        assert c.H == pytest.approx(H, abs=TOL), codigo
        if x is not None:
            assert c.x == pytest.approx(x, abs=TOL), codigo
        if z is not None:
            assert c.z == pytest.approx(z, abs=TOL), codigo
    tipos = {c.codigo: c.tipo for c in e.cargas}
    assert tipos == {"DC.pantalla": CARGA_DC, "DC.zapata": CARGA_DC,
                     "EV.talon": CARGA_EV, "EH.h": CARGA_EH, "EH.v": CARGA_EH,
                     "LS.h": CARGA_LS, "LS.v": CARGA_LS}


def test_el_empuje_se_descompone_y_la_vertical_carga_la_base(tanteo):
    """
    EXT-7-04: la resultante inclinada delta + beta ya no se toma entera como
    horizontal. P_A = 15.4100; .h = P·cos 20.1 y .v = P·sen 20.1, que
    estabiliza en el plano del talon (x = B).
    """
    e = M9.ensamble_estabilidad(tanteo, EST)
    h, v = _carga(e, "EH.h"), _carga(e, "EH.v")
    assert math.hypot(h.H, v.V) == pytest.approx(15.4100, abs=TOL)
    assert v.V / h.H == pytest.approx(math.tan(math.radians(20.1)), abs=ABS_CERO)
    assert v.x == CP["geometria"]["B"]
    assert v.V > 0 and v.momento > 0 > h.momento


def test_resistencia_I_minimos_y_maximos_son_las_del_dorado(tanteo):
    e = M9.ensamble_estabilidad(tanteo, EST)
    c = _combo(e, "Resistencia I (minimos)", MARCO_LRFD,
               "excentricidad y deslizamiento")
    d = CP["resistencia_min"]
    assert c.N == pytest.approx(d["N"], abs=TOL)
    assert c.H == pytest.approx(d["H"], abs=TOL)
    assert c.M_estabilizante == pytest.approx(d["M_e"], abs=TOL)
    assert c.M_volcante == pytest.approx(d["M_v"], abs=TOL)
    assert c.excentricidad == pytest.approx(d["e"], abs=TOL)
    c = _combo(e, "Resistencia I (maximos)", MARCO_LRFD, "portante")
    d = CP["resistencia_max"]
    assert c.N == pytest.approx(d["N"], abs=TOL)
    assert c.M_estabilizante == pytest.approx(d["M_e"], abs=TOL)
    assert c.excentricidad == pytest.approx(d["e"], abs=TOL)


def test_los_factores_de_cada_combinacion_LRFD_son_los_de_la_tabla(tanteo):
    """
    Minimos: 0.90 DC, 1.00 EV, 1.50 EH (dos componentes), 1.75 LS solo como
    empuje. Maximos: 1.25 DC, 1.35 EV, 1.50 EH, 1.75 LS con su peso.
    """
    e = M9.ensamble_estabilidad(tanteo, EST)
    minimos = dict(_combo(e, "(minimos)", MARCO_LRFD,
                          "excentricidad y deslizamiento").factores)
    assert minimos == {"DC.pantalla": 0.90, "DC.zapata": 0.90,  # float-exacto: transcrito o declarado, no calculado
                       "EV.talon": 1.00, "EH.h": 1.50, "EH.v": 1.50,
                       "LS.h": 1.75, "LS.v": 0.0}
    maximos = dict(_combo(e, "(maximos)", MARCO_LRFD, "portante").factores)
    assert maximos == {"DC.pantalla": 1.25, "DC.zapata": 1.25,  # float-exacto: transcrito o declarado, no calculado
                       "EV.talon": 1.35, "EH.h": 1.50, "EH.v": 1.50,
                       "LS.h": 1.75, "LS.v": 1.75}


@pytest.mark.parametrize("condicion", [EST, SIS])
def test_los_marcos_no_se_cruzan(tanteo, condicion):
    """
    REGLA DURA del encargo. En el marco ASD ninguna carga permanente lleva
    factor distinto de 1 (los unicos factores menores son los porcentajes del
    caso sismico, 0.5, y el 0 que excluye el peso de la sobrecarga); y ninguna
    fila ASD compara con una resistencia minorada por phi ni ninguna fila
    LRFD con un factor de seguridad.
    """
    e = M9.ensamble_estabilidad(tanteo, condicion)
    permanentes = {c.codigo for c in e.cargas
                   if c.tipo in (CARGA_DC, CARGA_EV, CARGA_WA)}
    for c in e.combinaciones:
        f = dict(c.factores)
        if c.marco == MARCO_ASD:
            assert all(f[k] == 1.0 for k in permanentes), c.nombre  # float-exacto: transcrito o declarado, no calculado
            assert set(f.values()) <= {0.0, 0.5, 1.0}, c.nombre
            assert c.nombre.startswith("Servicio")
        else:
            assert not c.nombre.startswith("Servicio")
    for v in e.del_marco(MARCO_ASD):
        simbolos = {m.simbolo for m in v.paso.sustitucion}
        assert not {"phi_b", "phi_tau"} & simbolos, v.codigo
        assert v.paso.fundamento_id == "F9.E_ASD"
        assert "E.050" in v.numeral or "E050" in v.paso.umbral.cita_id
    for v in e.del_marco(MARCO_LRFD):
        assert v.paso.fundamento_id.endswith("_LRFD")
        assert "FS" not in v.paso.formula
        assert v.paso.umbral.cita_id.startswith("AASHTO_LRFD_9")
    assert len(e.del_marco(MARCO_ASD)) == len(e.del_marco(MARCO_LRFD)) == 3


def test_las_seis_filas_estaticas_son_las_del_dorado(tanteo):
    e = M9.ensamble_estabilidad(tanteo, EST)
    assert [v.codigo for v in e.verificaciones] == [
        "E1-ASD.est.e", "E1-LRFD.est.e", "E2-ASD.est.e", "E2-LRFD.est.e",
        "E3-ASD.est.e", "E3-LRFD.est.e"]
    v = _v(e, "E1-LRFD.est.e")
    assert v.valor_obtenido == pytest.approx(CP["E1_LRFD"]["sigma_v"], rel=REL)
    assert v.valor_admisible == pytest.approx(CP["E1_LRFD"]["q_R"], rel=REL)
    q_n = next(m.valor for m in v.paso.sustitucion if m.simbolo == "q_n")
    assert q_n == pytest.approx(CP["E1_LRFD"]["q_n"], rel=REL)
    v = _v(e, "E2-LRFD.est.e")
    assert v.valor_obtenido == pytest.approx(CP["E2_LRFD"]["e"], abs=TOL)
    assert v.valor_admisible == pytest.approx(CP["E2_LRFD"]["e_max"], abs=ABS_CERO)
    v = _v(e, "E3-LRFD.est.e")
    assert v.valor_obtenido == pytest.approx(CP["E3_LRFD"]["H"], abs=TOL)
    assert v.valor_admisible == pytest.approx(CP["E3_LRFD"]["R_R"], abs=TOL)
    R_tau = next(m.valor for m in v.paso.sustitucion if m.simbolo == "R_tau")
    assert R_tau == pytest.approx(CP["E3_LRFD"]["R_tau"], abs=TOL)
    asd = CP["ASD"]
    v = _v(e, "E2-ASD.est.e")
    assert v.valor_obtenido == pytest.approx(asd["FS_volteo"], abs=TOL)
    assert v.valor_admisible == pytest.approx(1.5, abs=ABS_CERO)
    v = _v(e, "E3-ASD.est.e")
    assert v.valor_obtenido == pytest.approx(asd["FS_deslizamiento"], abs=TOL)
    assert v.valor_admisible == pytest.approx(1.5, abs=ABS_CERO)
    v = _v(e, "E1-ASD.est.e")
    assert v.valor_obtenido == pytest.approx(asd["q_servicio"], rel=REL)
    assert v.valor_admisible == pytest.approx(asd["q_adm"], rel=REL)
    assert all(v.cumple for v in e.verificaciones) and e.cumple


def test_en_el_marco_LRFD_no_hay_volteo_sino_excentricidad(tanteo):
    """AASHTO C11.6.3.3: la excentricidad REEMPLAZA al factor de seguridad."""
    e = M9.ensamble_estabilidad(tanteo, EST)
    v = _v(e, "E2-LRFD.est.e")
    assert "excentricidad" in v.paso.que
    assert "AASHTO_LRFD_9.C11.6.3.3#REEMPLAZA" in v.paso.citas_textuales
    assert "NO hay factor de seguridad al volteo" in v.paso.nota_del_proyecto
    assert "volteo" in _v(e, "E2-ASD.est.e").paso.que


def test_la_condicion_sismica_reproduce_el_dorado(tanteo):
    """
    k_h = 0.25: K_AE = 0.5083, P_AE = 26.3503, incremento 10.9403 a 0.6·h,
    inercia del muro 8.246 y del relleno 9.900, en su centro de gravedad.
    """
    e = M9.ensamble_estabilidad(tanteo, SIS)
    s = CP["sismico"]
    assert e.K_AE == pytest.approx(CP["K_AE_kh_025"], abs=TOL_K)
    assert e.k_h == s["k_h"]
    assert _carga(e, "EQ.dPAE.h").H == pytest.approx(s["dP_h"], abs=TOL)
    assert _carga(e, "EQ.dPAE.h").z == pytest.approx(s["z_dP"], abs=ABS_CERO)
    assert _carga(e, "EQ.dPAE.v").V == pytest.approx(s["dP_v"], abs=TOL)
    assert _carga(e, "EQ.PIR.muro").H == pytest.approx(s["PIR_muro"], abs=TOL)
    assert _carga(e, "EQ.PIR.muro").z == pytest.approx(s["z_muro"], abs=TOL_FINA)
    assert _carga(e, "EQ.PIR.suelo").H == pytest.approx(s["PIR_suelo"], abs=TOL)
    assert _carga(e, "EQ.PIR.suelo").z == pytest.approx(s["z_suelo"], abs=ABS_CERO)
    assert all(c.tipo == CARGA_EQ for c in e.cargas if c.codigo.startswith("EQ"))
    c1 = _combo(e, "100% P_AE + 50% P_IR", MARCO_LRFD,
                "excentricidad y deslizamiento")
    assert c1.N == pytest.approx(s["caso_1"]["N"], abs=TOL)
    assert c1.H == pytest.approx(s["caso_1"]["H"], abs=TOL)
    assert c1.excentricidad == pytest.approx(s["caso_1"]["e"], abs=TOL)
    v = _v(e, "E2-LRFD.sis.e")
    assert v.valor_obtenido == pytest.approx(s["caso_1"]["e"], abs=TOL)
    assert v.valor_admisible == pytest.approx(s["e_max"], abs=TOL_FINA)
    assert v.criterio_aplicado == "gamma_EQ"


def test_en_el_segundo_caso_sismico_rige_el_piso_del_empuje_estatico(tanteo):
    """
    0.5·P_AE = 13.175 < P_A = 15.410: el empuje no baja del estatico (AASHTO
    11.6.5.1). EH entero, incremento 0, inercia entera.
    """
    e = M9.ensamble_estabilidad(tanteo, SIS)
    c2 = _combo(e, "50% P_AE + 100% P_IR", MARCO_LRFD,
                "excentricidad y deslizamiento")
    assert "piso" in c2.nombre
    f = dict(c2.factores)
    assert (f["EH.h"], f["EQ.dPAE.h"], f["EQ.PIR.muro"]) == (1.0, 0.0, 1.0)  # float-exacto: transcrito o declarado, no calculado
    assert c2.H == pytest.approx(CP["sismico"]["caso_2"]["H"], abs=TOL)
    # Y el primer caso lleva la mitad de la inercia y gamma_EQ en la viva.
    f1 = dict(_combo(e, "100% P_AE + 50% P_IR", MARCO_LRFD,
                     "excentricidad y deslizamiento").factores)
    f1 = (f1["EQ.dPAE.h"], f1["EQ.PIR.muro"], f1["LS.h"], f1["LS.v"])
    assert f1 == (1.0, 0.5, 0.5, 0.0)  # float-exacto: transcrito o declarado, no calculado


def test_sin_el_piso_el_segundo_caso_lleva_la_mitad_del_empuje(tanteo,
                                                               monkeypatch):
    """Con k_h = 0.40 el 50 % de P_AE supera a P_A y el piso no rige."""
    monkeypatch.setattr(M9, "cadena_sismica",
                        lambda: SimpleNamespace(k_h=0.40, k_v=0.0))
    e = M9.ensamble_estabilidad(tanteo, SIS)
    P_A = math.hypot(_carga(e, "EH.h").H, _carga(e, "EH.v").V)
    dP = math.hypot(_carga(e, "EQ.dPAE.h").H, _carga(e, "EQ.dPAE.v").V)
    assert 0.5 * (P_A + dP) > P_A
    c2 = _combo(e, "50% P_AE + 100% P_IR", MARCO_LRFD,
                "excentricidad y deslizamiento")
    assert "piso" not in c2.nombre
    f = dict(c2.factores)
    assert (f["EH.h"], f["EQ.dPAE.h"], f["EQ.PIR.suelo"]) == (0.5, 0.5, 1.0)  # float-exacto: transcrito o declarado, no calculado


# ===========================================================================
# 7. CUAL MARCO DECIDE
# ===========================================================================

def test_lo_que_falla_en_el_marco_que_no_rige_informa_y_no_detiene(tanteo):
    """
    E3-ASD sismico del tanteo: FS = 51.014 / 41.647 = 1.2249... con la carga
    viva entera; el modulo da 1.2032 con el caso que rige, bajo 1.25. Con la
    regla de archivo (rige LRFD) sale como INDICADOR y `cumple` sigue en True.
    """
    e = M9.ensamble_estabilidad(tanteo, SIS)
    v = _v(e, "E3-ASD.sis.e")
    assert v.valor_admisible == pytest.approx(1.25, abs=ABS_CERO)
    assert v.valor_obtenido < v.valor_admisible
    assert v.paso.veredicto.tipo is TipoDeVeredicto.INDICADOR
    assert v.cumple and e.cumple
    assert "NO rige" in v.paso.veredicto.explicacion
    assert e.regla_de_marco == MARCO_RIGE_LRFD


@pytest.mark.parametrize("regla", [MARCO_RIGE_ASD, MARCO_ENVOLVENTE])
def test_con_otra_regla_esa_misma_fila_decide(tanteo, regla):
    ca.establecer_valor_dinamico("marco_estabilidad_cabezal", regla)
    e = M9.ensamble_estabilidad(tanteo, SIS)
    v = _v(e, "E3-ASD.sis.e")
    assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
    assert not v.cumple and not e.cumple
    assert e.regla_de_marco == regla


def test_cuando_rige_ASD_lo_que_falla_en_LRFD_solo_informa(tanteo):
    """Un talon corto hace fallar el deslizamiento LRFD estatico."""
    g = _geometria(B=1.20, ancho_talon=0.30)
    entorno = _entorno(geometria=g)
    e = M9.ensamble_estabilidad(entorno, EST)
    v = _v(e, "E3-LRFD.est.e")
    assert v.valor_obtenido > v.valor_admisible
    assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE and not e.cumple
    ca.establecer_valor_dinamico("marco_estabilidad_cabezal", MARCO_RIGE_ASD)
    e = M9.ensamble_estabilidad(entorno, EST)
    assert _v(e, "E3-LRFD.est.e").paso.veredicto.tipo \
        is TipoDeVeredicto.INDICADOR


def test_una_regla_de_marco_que_burla_la_puerta_se_rechaza(tanteo):
    with con_valor("marco_estabilidad_cabezal", "los_dos_mezclados",
                   motivo="segunda linea: el consumidor no confia en la "
                          "puerta"):
        with pytest.raises(DatoInvalidoError):
            M9.ensamble_estabilidad(tanteo, EST)


# ===========================================================================
# 8. EL AGUA: una vez, y hasta donde lo declara el drenaje
# ===========================================================================

def test_con_el_freatico_bajo_la_zapata_y_drenaje_no_hay_carga_de_agua(tanteo):
    e = M9.ensamble_estabilidad(tanteo, EST)
    assert not [c for c in e.cargas if c.tipo == CARGA_WA]


def test_sin_drenaje_el_agua_llega_a_la_superficie_y_pide_el_peso_saturado(
        tanteo):
    """
    Valor de archivo: 'sin_drenaje' (AASHTO 11.6.6). El relleno se llena de
    agua, y el peso saturado es dato del ensayo: sin el, criterio pendiente.
    """
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    with pytest.raises(CriterioPendienteError) as exc:
        M9.ensamble_estabilidad(tanteo, EST)
    assert exc.value.clave == "peso_especifico_saturado_relleno_kn_m3"


def test_el_agua_no_se_cuenta_dos_veces(tanteo):
    """
    La desviacion que `HIPOTESIS_EMPUJE_BAJO_NF` declaraba, cerrada. Sin
    drenaje, h_w = h = 2.40 m y gamma_sat = 20 kN/m3: el suelo
    empuja con su peso SUMERGIDO, 20 - 9.81 = 10.19, y el agua aparte.

      P_suelo = 0.5·0.297260·10.19·2.40^2 = 8.7238 kN/m   (a h/3 = 0.80)
      P_agua  = 0.5·9.81·2.40^2          = 28.2528 kN/m   (a 0.80)
      U       = 9.81·(0 + 2.40)/2·2.00   = 23.544 kN/m, a 2B/3 = 1.3333 m
                (triangular: cero delante, 2.40 m detras)
    El doble conteo -- el suelo con su peso total MAS el agua -- daria
    P_suelo = 15.41 kN/m, que es lo que NO tiene que salir.
    """
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    with con_valor("peso_especifico_saturado_relleno_kn_m3", 20.0,
                   motivo="dato de ensayo de prueba para el dorado del agua"):
        e = M9.ensamble_estabilidad(tanteo, EST)
    P_suelo = math.hypot(_carga(e, "EH.h").H, _carga(e, "EH.v").V)
    assert P_suelo == pytest.approx(8.7238, abs=TOL_MM)
    assert P_suelo < 15.0
    assert _carga(e, "EH.h").z == pytest.approx(0.80, abs=ABS_CERO)
    assert _carga(e, "WA.h").H == pytest.approx(28.2528, abs=TOL_MM)
    assert _carga(e, "WA.h").z == pytest.approx(0.80, abs=ABS_CERO)
    u = _carga(e, "WA.u")
    assert u.V == pytest.approx(-23.544, abs=TOL_MM)
    assert u.x == pytest.approx(4.0 / 3.0, abs=ABS_CERO)
    # El relleno sobre el talon pesa saturado: 20·1.10·2.00 = 44.0 kN/m.
    assert _carga(e, "EV.talon").V == pytest.approx(44.0, abs=ABS_CERO)
    # WA va con factor 1.00 en los dos marcos.
    for c in e.combinaciones:
        f = dict(c.factores)
        assert f["WA.h"] == f["WA.u"] == 1.0, c.nombre  # float-exacto: transcrito o declarado, no calculado
    assert any("sin drenaje" in a.lower() for a in e.avisos)


def test_drenado_con_freatico_alto_solo_moja_hasta_el_nivel_natural(tanteo):
    """
    NF a 0.30 m bajo el terreno del pie, D_f = 0.80: el agua queda 0.50 m
    sobre la base, delante y detras. Subpresion uniforme 9.81·0.50·2.00 =
    9.81 kN/m en el centro; empuje del agua 0.5·9.81·0.25 = 1.2263 kN/m.
    """
    entorno = _con_freatico(tanteo, 0.30)
    with con_valor("peso_especifico_saturado_relleno_kn_m3", 20.0,
                   motivo="dato de ensayo de prueba"):
        e = M9.ensamble_estabilidad(entorno, EST)
    assert _carga(e, "WA.u").V == pytest.approx(-9.81, abs=TOL_K)
    assert _carga(e, "WA.u").x == pytest.approx(1.0, abs=ABS_CERO)
    assert _carga(e, "WA.h").H == pytest.approx(1.22625, abs=TOL_K)
    # El portante lo siente por los coeficientes del freatico: D_w = 0.30.
    v = _v(e, "E1-LRFD.est.e")
    cw = {m.simbolo: m.valor for m in v.paso.sustitucion
          if m.simbolo in ("C_wq", "C_wgamma")}
    assert cw["C_wgamma"] == 0.5  # float-exacto: transcrito o declarado, no calculado
    assert cw["C_wq"] == pytest.approx(0.5 + 0.5 * 0.30 / 0.80, abs=ABS_CERO)


def test_con_agua_en_el_plano_de_empuje_el_sismo_no_se_evalua(tanteo):
    """AASHTO 11.6.5.3: Mononobe-Okabe solo con el relleno no saturado."""
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    with con_valor("peso_especifico_saturado_relleno_kn_m3", 20.0,
                   motivo="dato de ensayo de prueba"):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            M9.ensamble_estabilidad(tanteo, SIS)
    assert str(exc.value).startswith(modelos.MOTIVO_METODO_NO_EVALUABLE_CABEZAL)
    assert "11.6.5.3" in str(exc.value)


# ===========================================================================
# 9. LO QUE DETIENE, Y COMO
# ===========================================================================

def test_Mononobe_Okabe_fuera_de_su_dominio_no_da_cifra(tanteo, monkeypatch):
    """
    phi = 30 < i + arctan(k_h) con k_h = 0.60 (30.96 grados): la fuente pide
    otro metodo. Nunca un K_AE forzado ni un ZeroDivisionError.

    CON LA CUÑA DE TANTEO (correcciones de T-7b, H4; la regla de archivo):
    el relleno del muro de tanteo es horizontal e indefinido, y con
    phi < psi la cuña crece sin cota al tender el plano de falla a la
    horizontal: tampoco tiene maximo, y se detiene igual, con el mismo
    remedio. La rama de la formula cerrada se prueba en
    `test_la_formula_cerrada_fuera_de_su_dominio_tampoco_da_cifra`.
    """
    monkeypatch.setattr(M9, "cadena_sismica",
                        lambda: SimpleNamespace(k_h=0.60, k_v=0.0))
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M9.ensamble_estabilidad(tanteo, SIS)
    texto = str(exc.value)
    assert texto.startswith(modelos.MOTIVO_METODO_NO_EVALUABLE_CABEZAL)
    assert "factor_muro_eleccion" in texto
    # Y el caso estatico del mismo cabezal SI se evalua.
    assert M9.ensamble_estabilidad(tanteo, EST).cumple


def test_la_formula_cerrada_fuera_de_su_dominio_tampoco_da_cifra(
        tanteo, monkeypatch):
    """
    La rama de la formula cerrada (regla «talud_quebrado_2h»): phi = 30 <
    i + arctan(0.60) y se detiene en la condicion de 11.6.5.3, con el
    remedio que nombra la cuña de archivo.
    """
    monkeypatch.setattr(M9, "cadena_sismica",
                        lambda: SimpleNamespace(k_h=0.60, k_v=0.0))
    with con_valor("regla_pendiente_relleno_trasdos", "talud_quebrado_2h",
                   motivo="la rama de la formula cerrada"):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            M9.ensamble_estabilidad(tanteo, SIS)
    assert "11.6.5.3" in str(exc.value) and "cuna_de_tanteo" in str(exc.value)


def test_sin_el_freatico_del_punto_se_detiene_en_el_dato(tanteo):
    with pytest.raises(DatoFaltanteError) as exc:
        M9.ensamble_estabilidad(_con_freatico(tanteo, None), EST)
    assert exc.value.campo == "NF_profundidad_m"
    assert "No tiene valor por defecto" in str(exc.value)


def test_sin_el_angulo_del_relleno_se_detiene_en_el_criterio(tanteo):
    ca.quitar_valor_dinamico("phi_relleno_trasdos")
    with pytest.raises(CriterioPendienteError) as exc:
        M9.ensamble_estabilidad(tanteo, EST)
    assert exc.value.clave == "phi_relleno_trasdos"


def test_sin_suelo_de_fundacion_se_detiene_en_el_criterio_de_corredor(tanteo):
    with pytest.raises(CriterioPendienteError) as exc:
        M9.ensamble_estabilidad(replace(tanteo, suelo=None), EST)
    assert exc.value.clave == "c_phi_fundacion"


def test_el_suelo_del_punto_gana_sobre_el_de_corredor(tanteo):
    """La calicata del cruce gana; el criterio es el respaldo del corredor."""
    corredor = dict(CP["suelo"], phi_grados=25.0)
    with con_valor("c_phi_fundacion", corredor,
                   motivo="dato de ensayo de prueba, de corredor"):
        del_punto = M9.ensamble_estabilidad(tanteo, EST)
        del_corredor = M9.ensamble_estabilidad(replace(tanteo, suelo=None),
                                               EST)
    R_punto = _v(del_punto, "E3-LRFD.est.e").valor_admisible
    R_corredor = _v(del_corredor, "E3-LRFD.est.e").valor_admisible
    assert R_punto == pytest.approx(CP["E3_LRFD"]["R_R"], abs=TOL)
    # 0.80·77.2293·tan(25) = 28.810
    assert R_corredor == pytest.approx(0.80 * 77.2293 * math.tan(
        math.radians(25.0)), abs=TOL)


def test_la_resistencia_del_EMS_gana_sobre_la_calculada(tanteo):
    """`q_n_kpa` y `q_adm_kpa` del estudio de suelos, cada uno en SU marco."""
    suelo = dict(CP["suelo"], q_n_kpa=300.0, q_adm_kpa=90.0)
    e = M9.ensamble_estabilidad(replace(tanteo, suelo=suelo), EST)
    assert _v(e, "E1-LRFD.est.e").valor_admisible == pytest.approx(
        0.45 * 300.0, abs=ABS_CERO)
    assert _v(e, "E1-ASD.est.e").valor_admisible == pytest.approx(
        90.0, abs=ABS_CERO)


def test_la_subpresion_que_levanta_el_muro_no_es_un_fallo_de_programa(tanteo):
    """
    Con un muro casi sin peso y el relleno lleno de agua la suma vertical
    deja de ser de compresion: `DisenoNoFactibleError`, que el servicio
    registra como bloqueo, y no una division por cero.
    """
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    g = _geometria(H=2.0, B=2.0, espesor_corona=0.05, espesor_base_muro=0.05,
                   espesor_zapata=0.05, ancho_talon=0.01, ancho_punta=1.94)
    entorno = _entorno(geometria=g, cota_relleno=102.05,
                       cota_borde_plataforma=102.05)
    with con_valor("peso_especifico_saturado_relleno_kn_m3", 20.0,
                   motivo="dato de ensayo de prueba"):
        with pytest.raises(ErrorProyecto):
            M9.ensamble_estabilidad(entorno, EST)


def test_E4_y_E5_se_imprimen_diferidas_y_no_terminan_en_AssertionError(tanteo):
    """
    INF-4.5 / punto 4 del encargo: la estabilidad global y la del talud
    viajan como pendientes con su motivo, y las dos funciones sueltas
    levantan una excepcion del expediente.
    """
    e = M9.ensamble_estabilidad(tanteo, EST)
    assert [p[0] for p in e.pendientes] == ["E4", "E5"]
    assert any("E4 y E5" in a and "NO se evaluan" in a for a in e.avisos)
    assert "9.3.g.e" in [p.codigo for p in e.pasos]
    ca.establecer_valor_dinamico  # (la puerta existe; aqui no se declara)
    for funcion in (M9.verificar_estabilidad_global, M9.verificar_talud):
        fuente = inspect.getsource(funcion)
        arbol = ast.parse(fuente)
        assert not [n for n in ast.walk(arbol) if isinstance(n, ast.Assert)]
        assert not any(isinstance(n, ast.Raise) and "AssertionError"
                       in ast.unparse(n) for n in ast.walk(arbol))


def test_toda_parada_del_ensamble_desciende_de_ErrorProyecto():
    """
    Por AST: en el bloque de T-7b de M9 no hay `assert` ni excepcion desnuda.
    El bloque se localiza por SIMBOLO -- empieza en `CRITERIO_MARCO` --, no
    por el comentario que lo encabeza: la primera version de este test lo
    buscaba por texto, y el arnes de mutacion (que reescribe el modulo sin
    comentarios) lo mataba todo por esa razon y no por la que media.
    """
    modulo = ast.parse(Path(M9.__file__).read_text(encoding="utf-8"))
    inicio = next(n.lineno for n in modulo.body
                  if isinstance(n, ast.Assign)
                  and getattr(n.targets[0], "id", "") == "CRITERIO_MARCO")
    cuerpo = [n for n in modulo.body if n.lineno >= inicio]
    assert {"ensamble_estabilidad", "cargas_del_cabezal"} <= {
        n.name for n in cuerpo if isinstance(n, ast.FunctionDef)}
    arbol = ast.Module(body=cuerpo, type_ignores=[])
    assert not [n for n in ast.walk(arbol) if isinstance(n, ast.Assert)]
    permitidas = {"DatoInvalidoError", "DatoFaltanteError",
                  "CriterioPendienteError", "MetodoNoEvaluableError",
                  "LimiteNumericoError", "DisenoNoFactibleError",
                  "_no_evaluable"}
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Raise) and nodo.exc is not None:
            llamada = nodo.exc.func if isinstance(nodo.exc, ast.Call) \
                else nodo.exc
            assert ast.unparse(llamada) in permitidas, ast.unparse(nodo)


# ===========================================================================
# 10. LA GEOMETRIA DEL RELLENO Y LA PENDIENTE EQUIVALENTE
# ===========================================================================

def test_la_pendiente_sale_de_la_geometria_por_el_talud_quebrado(tanteo):
    """
    z_rel = 2.40 m; el terreno sube 0.90 m detras con talud 1.5. Regla de
    archivo: recta de la corona del relleno al terreno a 2·z_rel = 4.80 m.
    A 4.80 m el talud habria subido 3.20 m, pero se quiebra a 0.90:
        i = arctan(0.90 / 4.80) = 10.620 grados
    El plano de empuje (talon 1.10 m) sube min(1.10/1.5, 0.90) = 0.7333 m:
        h = 2.40 + 0.7333 = 3.1333 m
    """
    entorno = replace(tanteo, cota_borde_plataforma=103.30)
    r = M9.geometria_del_relleno(entorno)
    assert r["i_grados"] == pytest.approx(
        math.degrees(math.atan(0.90 / 4.80)), abs=ABS_CERO)
    assert r["i_grados"] == pytest.approx(10.620, abs=TOL_MM)
    assert r["h"] == pytest.approx(2.40 + 1.10 / 1.5, abs=ABS_CERO)
    # La cuña sobre el talon: triangulo 1.10 × 0.7333 / 2 = 0.40333 m2.
    assert r["area_tri"] == pytest.approx(1.10 * (1.10 / 1.5) / 2, abs=ABS_CERO)
    assert r["area_rec"] == pytest.approx(0.0, abs=ABS_CERO)
    e = M9.ensamble_estabilidad(entorno, EST)
    assert e.i_grados == pytest.approx(r["i_grados"], rel=REL_TRANSPORTE)
    # EV: 18·(1.10·2.00 + 0.40333) = 46.86 kN/m
    assert _carga(e, "EV.talon").V == pytest.approx(
        18.0 * (2.20 + 0.403333), abs=TOL_MM)


def test_con_la_otra_regla_la_pendiente_es_el_talud_entero(tanteo):
    """'talud_del_terraplen': i = arctan(1/1.5) = 33.69 grados, sin quiebre."""
    ca.establecer_valor_dinamico("regla_pendiente_relleno_trasdos",
                                 "talud_del_terraplen")
    r = M9.geometria_del_relleno(replace(tanteo, cota_borde_plataforma=103.30))
    assert r["i_grados"] == pytest.approx(33.690, abs=TOL_MM)
    # Y con el relleno horizontal sigue siendo cero.
    assert M9.geometria_del_relleno(tanteo)["i_grados"] == pytest.approx(
        0.0, abs=ABS_CERO)


def test_una_pendiente_declarada_gana_sobre_la_geometria(tanteo):
    ca.establecer_valor_dinamico("pendiente_relleno_trasdos_i", 5.0)
    r = M9.geometria_del_relleno(replace(tanteo, cota_borde_plataforma=103.30))
    assert r["i_grados"] == pytest.approx(5.0, abs=ABS_CERO)
    assert "declarado" in r["origen_i"]


def test_delta_declarado_gana_y_no_puede_pasar_de_phi(tanteo):
    ca.establecer_valor_dinamico("friccion_muro_suelo_delta", 15.0)
    assert M9.ensamble_estabilidad(tanteo, EST).delta_grados \
        == pytest.approx(15.0, abs=ABS_CERO)
    with con_valor("friccion_muro_suelo_delta", 31.0,
                   motivo="fuera de la ventana: delta > phi = 30"):
        with pytest.raises(DatoInvalidoError):
            M9.ensamble_estabilidad(tanteo, EST)


def test_un_talon_que_no_cabe_en_la_zapata_es_dato_invalido(tanteo):
    g = _geometria(ancho_talon=1.90)       # 1.90 + 0.30 > B = 2.00
    with pytest.raises(DatoInvalidoError):
        M9.ensamble_estabilidad(_entorno(geometria=g), EST)


# ===========================================================================
# 11. LA CAPACIDAD PORTANTE
# ===========================================================================

def test_la_capacidad_portante_nominal_a_mano_con_y_sin_inclinacion():
    """
    phi_f = 32 (Nq 23.2, Ngamma 30.2), c = 0, gamma = 18, D_f = 0.80, B' =
    1.94694, freatico profundo.
      sin inclinacion: 18·0.80·23.2 + 0.5·18·1.94694·30.2 = 334.08 + 529.18
                       = 863.26 kPa
      con H/V = 22.2997/89.9499: i_q = 0.565636, i_gamma = 0.425408
                       -> 188.966 + 225.118 = 414.084 kPa
    """
    suelo = dict(CP["suelo"])
    q, det = M9.resistencia_portante_nominal(
        suelo=suelo, B_efectivo=1.94694, D_f=0.80, D_w=5.0,
        H_servicio=22.2997, V_servicio=89.9499, aplicar_inclinacion=False)
    assert q == pytest.approx(334.08 + 0.5 * 18 * 1.94694 * 30.2, rel=REL_TRANSPORTE)
    assert q == pytest.approx(863.26, abs=TOL_CM)
    q, det = M9.resistencia_portante_nominal(
        suelo=suelo, B_efectivo=1.94694, D_f=0.80, D_w=5.0,
        H_servicio=22.2997, V_servicio=89.9499, aplicar_inclinacion=True)
    assert det["i_q"] == pytest.approx(0.565636, abs=TOL_FINA)
    assert det["i_gamma"] == pytest.approx(0.425408, abs=TOL_FINA)
    assert q == pytest.approx(CP["E1_LRFD"]["q_n"], rel=REL)


def test_el_termino_de_cohesion_entra_en_un_suelo_cohesivo():
    """
    Arcilla, phi = 0, c = 60 kPa: N_c = 5.14, N_q = 1, N_gamma = 0.
    q_n = 60·5.14 + 18·0.80·1.0 = 308.4 + 14.4 = 322.8 kPa (sin inclinacion).
    """
    suelo = {"cohesivo": True, "c_kpa": 60.0, "phi_grados": 0.0,
             "gamma_kn_m3": 18.0}
    q, _ = M9.resistencia_portante_nominal(
        suelo=suelo, B_efectivo=1.8, D_f=0.80, D_w=5.0, H_servicio=0.0,
        V_servicio=100.0, aplicar_inclinacion=False)
    assert q == pytest.approx(322.8, abs=ABS_CERO)


def test_omitir_los_factores_de_inclinacion_sube_la_resistencia(tanteo):
    """El criterio [A] existe para que la eleccion se vea: aplicar no relaja."""
    con = _v(M9.ensamble_estabilidad(tanteo, EST), "E1-LRFD.est.e")
    ca.establecer_valor_dinamico("factores_inclinacion_carga_portante",
                                 "omitir")
    sin = _v(M9.ensamble_estabilidad(tanteo, EST), "E1-LRFD.est.e")
    assert sin.valor_admisible > con.valor_admisible
    assert sin.valor_obtenido == pytest.approx(con.valor_obtenido,
                                               rel=REL_TRANSPORTE)


def test_con_hoya_de_socavacion_solo_cuenta_el_empotramiento_bajo_su_fondo(
        tanteo):
    """
    Salida con hoya cuyo fondo queda 0.50 m bajo el terreno del pie: D_f
    efectivo 0.30 m en vez de 0.80. El termino de sobrecarga baja en esa
    proporcion y con el la resistencia.
    """
    g = _geometria(extremo="salida")
    sin_hoya = _entorno(geometria=g)
    con_hoya = replace(sin_hoya, cota_fondo_hoya=100.30)
    a = _v(M9.ensamble_estabilidad(sin_hoya, EST), "E1-LRFD.est.s")
    b = _v(M9.ensamble_estabilidad(con_hoya, EST), "E1-LRFD.est.s")
    assert b.valor_admisible < a.valor_admisible
    # La diferencia es el termino de sobrecarga de 0.50 m:
    # 0.45·18·0.50·23.2·i_q = 0.45·118.104 = 53.147 kPa (i_q = 0.565636)
    assert a.valor_admisible - b.valor_admisible == pytest.approx(
        0.45 * 18 * 0.50 * 23.2 * 0.565636, abs=TOL_CM)


def test_la_zapata_en_talud_usa_los_factores_declarados_y_no_los_inventa(
        tanteo):
    """
    'terreno_delante_del_cabezal' = talud: la ecuacion del Manual de Puentes
    necesita N_cq y N_gamma_q, que salen de figuras y son un criterio SIN
    valor. Se detiene ahi; no sustituye por la del terreno horizontal.
    """
    ca.establecer_valor_dinamico("terreno_delante_del_cabezal",
                                 "talud_descendente")
    with pytest.raises(CriterioPendienteError):
        M9.ensamble_estabilidad(tanteo, EST)


# ===========================================================================
# 12. LA INTERFAZ PARA T-7c: SOLICITACIONES POR ELEMENTO
# ===========================================================================

def test_las_solicitaciones_son_por_elemento_y_del_marco_LRFD(tanteo):
    e = M9.ensamble_estabilidad(tanteo, EST)
    assert {s.elemento for s in e.solicitaciones} == {
        ELEMENTO_PANTALLA, ELEMENTO_ZAPATA, ELEMENTO_ALEROS}
    lrfd = {c.nombre for c in e.combinaciones if c.marco == MARCO_LRFD}
    assert {s.combinacion for s in e.solicitaciones} == lrfd
    secciones = {(s.elemento, s.seccion) for s in e.solicitaciones}
    assert len(secciones) == 4          # pantalla, aleros, punta y talon
    for s in e.solicitaciones:
        assert math.isfinite(s.V_u) and math.isfinite(s.M_u)
        assert s.nota.strip()


def test_la_solicitacion_del_arranque_de_la_pantalla_a_mano(tanteo):
    """
    Resistencia I: los empujes factorados son 1.50·14.4714 + 1.75·7.8283 =
    35.4066 kN/m. Su momento respecto de la base es 33.8051; respecto del
    arranque de la pantalla (0.40 m mas arriba):
        M_u = 33.8051 - 35.4066·0.40 = 19.6425 kN·m/m
    """
    e = M9.ensamble_estabilidad(tanteo, EST)
    s = next(x for x in e.solicitaciones if x.elemento == ELEMENTO_PANTALLA
             and "maximos" in x.combinacion)
    assert s.V_u == pytest.approx(35.4066, abs=TOL)
    assert s.M_u == pytest.approx(33.8051 - 35.4066 * 0.40, abs=TOL)


def test_la_punta_de_la_zapata_a_mano(tanteo):
    """
    Resistencia I (maximos): N = 123.7564, B' = 1.94694, presion uniforme
    sobre el ancho efectivo (suelo) sigma = 63.5646 kPa. La resultante cae
    hacia el talon (e < 0): el ancho efectivo arranca a 2·0.02653 = 0.05306
    de la punta... el modulo lo declara en `nota`. Menos el peso propio de la
    punta con su factor: 1.25·23.56·0.40 = 11.78 kPa.
    Aqui se fija lo que no depende de esa lectura: el cortante en la cara de
    la pantalla no supera sigma·punta y es positivo.
    """
    e = M9.ensamble_estabilidad(tanteo, EST)
    s = next(x for x in e.solicitaciones if x.elemento == ELEMENTO_ZAPATA
             and "punta" in x.seccion and "maximos" in x.combinacion)
    assert 0 < s.V_u <= 63.5646 * 0.60 + TOL
    assert 0 < s.M_u <= 63.5646 * 0.60 ** 2 / 2 + TOL


def test_las_piezas_del_ensamble_se_llaman_sueltas_y_dan_lo_mismo(tanteo):
    """
    La interfaz que T-7c va a usar: las cuatro piezas, una tras otra, dan lo
    mismo que el ensamble entero.
    """
    relleno = M9.geometria_del_relleno(tanteo)
    angulos = M9.angulos_del_empuje(tanteo, relleno)
    assert angulos["phi"] == pytest.approx(CP["phi_relleno"], abs=ABS_CERO)
    assert angulos["delta"] == pytest.approx(CP["delta"], abs=ABS_CERO)
    assert angulos["i"] == pytest.approx(0.0, abs=ABS_CERO)
    assert angulos["beta"] == pytest.approx(0.0, abs=ABS_CERO)
    assert "talon" in angulos["plano"]
    cargas, datos = M9.cargas_del_cabezal(tanteo, EST)
    combos = M9.combinaciones_de_estabilidad(cargas, datos, EST,
                                             tanteo.geometria.B)
    solicitaciones = M9.solicitaciones_por_elemento(tanteo, cargas, combos,
                                                    datos)
    entero = M9.ensamble_estabilidad(tanteo, EST)
    assert cargas == entero.cargas
    assert combos == entero.combinaciones
    assert solicitaciones == entero.solicitaciones
    assert len(combos) == 4 and len(solicitaciones) == 8


def test_sin_talon_el_plano_de_empuje_es_el_trasdos_y_beta_el_del_muro(
        tanteo):
    """
    Con talon, beta = 0 sobre el plano vertical de su extremo (AASHTO
    C3.11.5.3); sin talon el empuje actua sobre el trasdos, con su
    inclinacion, y no hay relleno sobre la zapata.

    REESCRITO DECLARANDOLO (correcciones de T-7b, H4): la cuña de tanteo de
    archivo es la del plano VERTICAL del talon; sobre un trasdos inclinado
    se detiene con «metodo no evaluable» y dice que regla declarar. Lo que
    este test fijaba -- el plano y la inclinacion del empuje -- se fija con
    la formula cerrada, declarando la regla.
    """
    g = _geometria(ancho_talon=0.0, ancho_punta=1.70, beta_grados=5.0)
    entorno = _entorno(geometria=g)
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M9.cargas_del_cabezal(entorno, EST)
    assert "talud_quebrado_2h" in str(exc.value)
    ca.establecer_valor_dinamico("regla_pendiente_relleno_trasdos",
                                 "talud_quebrado_2h")
    angulos = M9.angulos_del_empuje(entorno, M9.geometria_del_relleno(entorno))
    assert angulos["beta"] == pytest.approx(5.0, abs=ABS_CERO)
    assert "trasdos" in angulos["plano"]
    cargas, _ = M9.cargas_del_cabezal(entorno, EST)
    codigos = [c.codigo for c in cargas]
    assert "EV.talon" not in codigos and "LS.v" not in codigos
    # La resultante actua a delta + beta = 20.1 + 5.0 = 25.1 grados.
    falso = SimpleNamespace(cargas=cargas)
    assert _carga(falso, "EH.v").V / _carga(falso, "EH.h").H \
        == pytest.approx(math.tan(math.radians(25.1)), rel=REL_TRANSPORTE)
    # El empuje vertical cae en el trasdos: x = punta + pantalla = 2.00 m.
    assert _carga(SimpleNamespace(cargas=cargas), "EH.v").x == pytest.approx(
        2.00, abs=ABS_CERO)


def test_el_suelo_de_fundacion_se_valida_donde_se_lee():
    """
    `suelo_de_fundacion` devuelve el suelo y DE DONDE salio; el del punto
    gana y el de corredor pasa por `validar_suelo_fundacion`, la misma
    guardia que la puerta de datos externos.
    """
    del_punto = dict(CP["suelo"])
    suelo, origen = M9.suelo_de_fundacion(del_punto, id_punto="T-00")
    assert suelo == del_punto and "dato externo del punto" in origen
    with pytest.raises(CriterioPendienteError):
        M9.suelo_de_fundacion(None, id_punto="T-00")
    with con_valor("c_phi_fundacion", del_punto,
                   motivo="dato de ensayo de prueba, de corredor"):
        suelo, origen = M9.suelo_de_fundacion(None, id_punto="T-00")
    assert suelo == del_punto and "criterio de corredor" in origen
    assert M9.validar_suelo_fundacion(del_punto, id_punto="T-00") == del_punto
    for malo in (dict(del_punto, phi_grados=46.0), dict(del_punto, c_kpa=-1.0),
                 {k: v for k, v in del_punto.items() if k != "cohesivo"},
                 dict(del_punto, gamma_saturado_kn_m3=5.0), None, 32.0):
        with pytest.raises(DatoInvalidoError):
            M9.validar_suelo_fundacion(malo, id_punto="T-00")


def test_cada_carga_dice_a_que_elemento_llega(tanteo):
    e = M9.ensamble_estabilidad(tanteo, SIS)
    sobre = {c.codigo: c.sobre for c in e.cargas}
    assert sobre["DC.pantalla"] == sobre["EH.h"] == sobre["LS.h"] \
        == sobre["EQ.dPAE.h"] == sobre["EQ.PIR.muro"] == ELEMENTO_PANTALLA
    assert sobre["DC.zapata"] == sobre["EV.talon"] == sobre["EH.v"] \
        == sobre["LS.v"] == sobre["EQ.PIR.suelo"] == ELEMENTO_ZAPATA
    for c in e.cargas:
        assert c.procedencia.strip() and c.descripcion.strip()


# ===========================================================================
# 13. LA MEMORIA: PASOS, FUNDAMENTOS Y CITAS
# ===========================================================================

def test_los_pasos_del_ensamble_llevan_fundamento_y_cita(tanteo):
    registro = construir()
    for condicion in (EST, SIS):
        e = M9.ensamble_estabilidad(tanteo, condicion)
        for p in tuple(e.pasos) + tuple(v.paso for v in e.verificaciones):
            assert p.fundamento_id.startswith("F9."), p.codigo
            assert p.por_que.strip(), p.codigo
            for cita_id in p.citas_textuales:
                assert registro.cita(cita_id).id == cita_id, p.codigo
    est = M9.ensamble_estabilidad(tanteo, EST)
    assert [p.codigo for p in est.pasos] == [
        "9.2.1.est.e", "9.2.2.est.e", "9.2.3.est.e", "9.2.5.est.e", "9.3.g.e"]
    sis = M9.ensamble_estabilidad(tanteo, SIS)
    assert [p.codigo for p in sis.pasos] == ["9.2.4.sis.e", "9.2.5.sis.e"]


@pytest.mark.parametrize("cita_id, caracter", [
    ("AASHTO_LRFD_9.C11.6.3.3#REEMPLAZA", None),
    ("AASHTO_LRFD_9.11.6.3.2#PORTANTE", None),
    ("AASHTO_LRFD_9.10.6.3.4#RESISTENCIA", None),
    ("AASHTO_LRFD_9.11.5.8#PORTANTE", None),
    ("AASHTO_LRFD_9.11.6.5.3#VALIDEZ", None),
    ("AASHTO_LRFD_9.11.6.6#DRENAJE", None),
    ("AASHTO_LRFD_9.C3.11.5.3#PLANO_DEL_TALON", None),
    ("AASHTO_LRFD_9.C3.11.5.8.1#TALUD_QUEBRADO", None),
    ("AASHTO_LRFD_9.10.6.3.1.2a#QN", None),
    ("E050.17.1#SERVICIO", None),
    ("E050.39.13.8#DRENAJE", None),
    ("HDS5_3ED.2.2.5#EMBALSE", None),
    ("HDS5_3ED.5.4.2#PARALELO", None),
])
def test_las_citas_del_ensamble_estan_en_el_registro_con_su_literal(
        cita_id, caracter):
    cita = construir().cita(cita_id)
    assert cita.texto_literal is not None and cita.texto_literal.texto.strip()
    assert cita.pagina_pdf and cita.numeral


def test_los_fundamentos_de_V5_V8_y_del_cabezal_dejaron_de_ser_huecos():
    from src.normativa import fundamentos as fu
    for fid in ("F5.V5", "F5.V8", "F9.CABEZAL"):
        assert fid not in fu.SIN_FUNDAMENTO
    for fid in ("F5.V5", "F5.V8", "F9.EMPUJES", "F9.SOBRECARGA", "F9.AGUA",
                "F9.SISMO", "F9.COMBINACIONES", "F9.E1_LRFD", "F9.E2_LRFD",
                "F9.E3_LRFD", "F9.E_ASD", "F9.GLOBAL"):
        assert fid in fu.FUNDAMENTOS, fid
        assert fu.FUNDAMENTOS[fid].citas, fid


def test_E050_no_se_presenta_como_exigencia_del_cabezal(tanteo):
    """
    La E.050 es norma de edificaciones: su aplicacion al cabezal es por
    analogia ([N→]) y la nota de cada fila ASD lo dice.
    """
    e = M9.ensamble_estabilidad(tanteo, EST)
    for v in e.del_marco(MARCO_ASD):
        assert "ANALOGIA" in v.paso.nota_del_proyecto
        assert "[N→]" in v.paso.nota_del_proyecto
    for v in e.del_marco(MARCO_LRFD):
        assert "hipotesis" in v.paso.nota_del_proyecto.lower()


# ===========================================================================
# 14. EL CONTRASTE CON LAS CIFRAS DEL ENCARGO (FUENTE NO DISPONIBLE)
# ===========================================================================

def test_contraste_con_las_cifras_del_encargo_fuente_no_disponible():
    """
    «Cifras del encargo; fuente no disponible»: el PDF de VARIOS no esta en
    la sesion. NO es un dorado: es un contraste con tolerancia declarada, que
    dice hasta donde las formulas del modulo reproducen ese ejemplo con los
    parametros que se pudieron reconstruir (phi = 26.17, gamma = 1600 kg/m3,
    H = 3.00 m, k_h = 0.15, Rankine: delta = i = beta = 0).
    """
    e = CP_T7B_ENCARGO
    assert "fuente no disponible" in e["rotulo"]
    r = e["reconstruido"]
    phi = r["phi_grados"]
    Ka = M9.k_a_coulomb(phi_grados=phi, i_grados=0.0, beta_grados=0.0,
                        delta_grados=0.0)
    assert Ka == pytest.approx(e["Ka"], abs=e["tolerancia_Ka"])
    assert Ka == pytest.approx(math.tan(math.radians(45 - phi / 2)) ** 2,
                               abs=ABS_CERO)
    assert 1 / Ka == pytest.approx(e["Kp"], abs=e["tolerancia_Kp"])
    K_AE = M9.k_ae_mononobe_okabe(phi_grados=phi, i_grados=0.0,
                                  beta_grados=0.0, delta_grados=0.0,
                                  k_h=r["k_h"], k_v=0.0)
    assert K_AE == pytest.approx(e["K_AE"], abs=e["tolerancia_K_AE"])
    gamma, H = r["gamma_kg_m3"], r["H_m"]
    P_A = 0.5 * Ka * gamma * H ** 2
    assert P_A == pytest.approx(e["P_A_kg_m"], rel=e["tolerancia_P_A"])
    dP = 0.5 * gamma * H ** 2 * (K_AE - Ka)
    assert dP == pytest.approx(e["dP_AE_kg_m"], rel=e["tolerancia_dP_AE"])
    # El brazo del incremento: 0.6·H, lo que el criterio adopta.
    assert ca.CRITERIOS["punto_aplicacion_incremento_sismico"].valor \
        == r["fraccion_brazo"]
    M = P_A * H / 3 + dP * r["fraccion_brazo"] * H
    assert M == pytest.approx(e["M_sismico_kgm_m"], rel=e["tolerancia_M_sismico"])
    # REESCRITO DECLARANDOLO (correcciones de T-7b, H10). La ultima asercion
    # comprobaba k_h·(DC + EV) = EQ, y era TAUTOLOGICA: k_h = 0.15 se
    # reconstruyo justamente de EQ/(DC + EV) = 1.58/10.54. Lo que el ejemplo
    # permite contrastar de verdad es lo de arriba: con ese k_h y la phi
    # reconstruida de Kp, Mononobe-Okabe da el K_AE del ejemplo (0.498),
    # que no se uso para reconstruir ninguno de los dos. Aqui solo se deja
    # escrita la reconstruccion, como lo que es.
    k_h_reconstruido = e["EQ_t"] / (e["DC_t"] + e["EV_t"])
    assert k_h_reconstruido == pytest.approx(r["k_h"],
                                             rel=e["tolerancia_EQ"])


# ===========================================================================
# 14-bis. LO QUE LA MUTACION ENSEÑO DEL ENSAMBLE (arnes de EXT-11)
# ===========================================================================
# La primera medida mato 525 de 833 mutantes de M9: el primer muro de tanteo
# deja en cero la pantalla trapecial, la cuña sobre el talon, el agua parcial,
# el suelo cohesivo y la roca, y no fijaba ningun margen. Estos tests cierran
# esos huecos, cada uno con su oraculo a mano (`CP_T7B_MURO_2`,
# `CP_T7B_COHESIVO`, `CP_T7B_SOLICITACIONES`).

M2 = CP_T7B_MURO_2


@pytest.fixture
def muro_2(tanteo):
    """
    El segundo muro: trapecial, con cuña, pendiente y agua parcial.

    DECLARA LA REGLA «talud_quebrado_2h» (correcciones de T-7b, H4): el
    dorado `CP_T7B_MURO_2` se calculo a mano con la pendiente equivalente de
    la Figura C3.11.5.8.1-1, que dejo de ser la regla de archivo -- ahora lo
    es la cuña de tanteo con la superficie real, que tiene su propio dorado
    (`CP_T7B_CUNA`) --. Lo que este muro prueba (pantalla trapecial, cuña
    sobre el talon, agua parcial) no depende de la regla.
    """
    ca.establecer_valor_dinamico("regla_pendiente_relleno_trasdos",
                                 "talud_quebrado_2h")
    g = GeometriaCabezal(**dict(M2["geometria"], cota_desplante=100.0,
                                cota_coronacion=102.55, id_punto="T-02",
                                extremo="entrada"))
    return EntornoDelCabezal(
        id_punto="T-02", extremo="entrada", geometria=g,
        cota_relleno=100.0 + M2["z_rel"],
        cota_borde_plataforma=100.0 + M2["z_rel"] + M2["subida"],
        origen_cota_borde="de prueba", talud=M2["talud"], esviaje_grados=0.0,
        cota_freatico=100.0 + g.D_f - M2["NF"], cota_pie=100.0 + g.D_f,
        suelo=dict(CP["suelo"]))


def _ensamble_muro_2(entorno, condicion=EST):
    with con_valor("peso_especifico_saturado_relleno_kn_m3",
                   M2["gamma_saturado"],
                   motivo="dato de ensayo de prueba del segundo muro"):
        return M9.ensamble_estabilidad(entorno, condicion)


def test_el_segundo_muro_la_geometria_del_relleno_es_la_del_dorado(muro_2):
    r = M9.geometria_del_relleno(muro_2)
    assert r["h"] == pytest.approx(M2["h"], abs=ABS_CERO)
    assert r["i_grados"] == pytest.approx(M2["i_grados"],
                                          abs=M2["tolerancia_fina"])
    assert r["area_tri"] == pytest.approx(M2["area_tri"], abs=ABS_CERO)
    assert r["area_rec"] == pytest.approx(M2["area_rec"], abs=ABS_CERO)
    assert r["x_quiebre"] == pytest.approx(0.60, abs=ABS_CERO)


def test_el_segundo_muro_las_cargas_y_sus_brazos_son_las_del_dorado(muro_2):
    """
    Pantalla trapecial (dos centroides), cuña de relleno sobre el talon,
    relleno mojado bajo el agua, diagrama de empuje en tres partes, y agua.
    """
    e = _ensamble_muro_2(muro_2)
    assert e.K_A == pytest.approx(M2["K_A"], abs=M2["tolerancia_K"])
    assert [c.codigo for c in e.cargas] == list(M2["cargas"])
    for codigo, (V, H, x, z) in M2["cargas"].items():
        c = _carga(e, codigo)
        assert c.V == pytest.approx(V, abs=M2["tolerancia"]), codigo
        assert c.H == pytest.approx(H, abs=M2["tolerancia"]), codigo
        if x is not None:
            assert c.x == pytest.approx(x, abs=M2["tolerancia_fina"]), codigo
        if z is not None:
            assert c.z == pytest.approx(z, abs=M2["tolerancia_fina"]), codigo
    P = math.hypot(_carga(e, "EH.h").H, _carga(e, "EH.v").V)
    assert P == pytest.approx(M2["P_A"], abs=M2["tolerancia"])


def test_el_segundo_muro_la_combinacion_de_minimos_es_la_del_dorado(muro_2):
    """La subpresion resta de N y SUMA al momento volcante; WA con 1.00."""
    e = _ensamble_muro_2(muro_2)
    c = _combo(e, "Resistencia I (minimos)", MARCO_LRFD,
               "excentricidad y deslizamiento")
    d = M2["resistencia_min"]
    assert c.N == pytest.approx(d["N"], abs=M2["tolerancia"])
    assert c.H == pytest.approx(d["H"], abs=M2["tolerancia"])
    assert c.M_estabilizante == pytest.approx(d["M_e"], abs=M2["tolerancia"])
    assert c.M_volcante == pytest.approx(d["M_v"], abs=M2["tolerancia"])
    assert c.excentricidad == pytest.approx(d["e"], abs=M2["tolerancia_e"])
    f = dict(c.factores)
    assert f["WA.h"] == pytest.approx(1.0, abs=ABS_CERO)
    assert f["WA.u"] == pytest.approx(1.0, abs=ABS_CERO)


def test_sin_drenaje_el_agua_llena_el_relleno_retenido_y_no_pasa_del_muro(
        muro_2):
    """
    REESCRITO DECLARANDOLO (correcciones de T-7b, H6). Se llamaba «sin
    drenaje la cuña sobre el talon tambien pesa saturada» y fijaba el agua
    hasta el terreno sobre el extremo del talon, h_w = h = 2.70 m: 0.30 m
    por encima del relleno retenido contra el trasdos, es decir, agua por
    encima de la coronacion del muro, que el muro no puede retener. Ahora,
    sin drenaje, el agua llena el relleno RETENIDO, h_w = z_rel = 2.40 m:
      EV = 20·1.20·2.00 (saturado) + 18·0.27 (la cuña, seca) = 48.0 + 4.86
         = 52.86 kN/m
      E_w = 9.81·2.40²/2 = 28.2528 kN/m, a 2.40/3 = 0.80 m
    """
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    e = _ensamble_muro_2(muro_2)
    assert _carga(e, "EV.talon").V == pytest.approx(52.86, abs=TOL_K)
    assert _carga(e, "WA.h").H == pytest.approx(28.2528, abs=TOL_K)
    assert _carga(e, "WA.h").z == pytest.approx(0.80, abs=TOL_K)


def test_con_agua_natural_en_el_plano_el_sismo_tampoco_se_evalua(muro_2):
    """Drenado, pero con el freatico sobre la base: 11.6.5.3 no lo admite."""
    with pytest.raises(MetodoNoEvaluableError):
        _ensamble_muro_2(muro_2, SIS)


def test_los_margenes_de_las_seis_filas_son_los_del_dorado(tanteo):
    """
    Margen = admisible - obtenido en las filas LRFD (y en E1-ASD), y
    obtenido - exigido en los dos factores de seguridad:
      E1-LRFD 186.3379 - 63.5646 = 122.7733 kPa
      E2-LRFD 0.66667 - 0.14530 = 0.52137 m
      E3-LRFD 38.6066 - 35.4066 = 3.2000 kN/m
      E1-ASD  136.6091 - 47.0912 = 89.5179 kPa
      E2-ASD  4.6474 - 1.5 = 3.1474 ; E3-ASD 2.1823 - 1.5 = 0.6823
    """
    e = M9.ensamble_estabilidad(tanteo, EST)
    esperado = {"E1-LRFD.est.e": 122.7733, "E2-LRFD.est.e": 0.52137,
                "E3-LRFD.est.e": 3.2000, "E1-ASD.est.e": 89.5179,
                "E2-ASD.est.e": 3.1474, "E3-ASD.est.e": 0.6823}
    for codigo, margen in esperado.items():
        v = _v(e, codigo)
        assert v.paso.veredicto.margen == pytest.approx(
            margen, rel=CP_T7B_SOLICITACIONES["tolerancia"]), codigo
        assert v.paso.veredicto.tipo is TipoDeVeredicto.CUMPLE


def test_las_solicitaciones_de_la_zapata_son_las_del_dorado(tanteo):
    e = M9.ensamble_estabilidad(tanteo, EST)
    tol = CP_T7B_SOLICITACIONES["tolerancia"]

    def de(elemento, fragmento):
        return next(s for s in e.solicitaciones if s.elemento == elemento
                    and fragmento in s.seccion and "maximos" in s.combinacion)

    for clave, s in (("punta", de(ELEMENTO_ZAPATA, "punta")),
                     ("talon", de(ELEMENTO_ZAPATA, "talon")),
                     ("pantalla", de(ELEMENTO_PANTALLA, "arranque"))):
        d = CP_T7B_SOLICITACIONES[clave]
        assert s.V_u == pytest.approx(d["V_u"], abs=tol), clave
        assert s.M_u == pytest.approx(d["M_u"], abs=tol), clave
    alero = de(ELEMENTO_ALEROS, "arranque")
    pantalla = de(ELEMENTO_PANTALLA, "arranque")
    assert (alero.V_u, alero.M_u) == (pantalla.V_u, pantalla.M_u)


@pytest.mark.parametrize("c_kpa", [60.0, 15.0])
def test_el_suelo_cohesivo_desliza_por_el_menor_de_c_y_media_sigma(tanteo,
                                                                   c_kpa):
    """
    AASHTO 10.6.3.4 sobre material granular compactado: q_s = min(c,
    sigma_v/2) sobre el ancho efectivo. Con c = 60 rige sigma_v/2 y con
    c = 15 rige c. E.050 Art. 20: en cohesivos phi = 0, aunque se declare.
    """
    d = CP_T7B_COHESIVO[f"c_{c_kpa:g}"]
    tol = CP_T7B_COHESIVO["tolerancia"]
    suelo = {"cohesivo": True, "c_kpa": c_kpa, "phi_grados": 28.0,
             "gamma_kn_m3": 18.0}
    e = M9.ensamble_estabilidad(replace(tanteo, suelo=suelo), EST)
    v = _v(e, "E3-LRFD.est.e")
    R_tau = next(m.valor for m in v.paso.sustitucion if m.simbolo == "R_tau")
    assert R_tau == pytest.approx(d["R_tau"], abs=tol)
    assert v.valor_admisible == pytest.approx(d["R_R"], abs=tol)
    assert not v.cumple                    # 35.4066 > 32.82 y > 21.79
    assert _v(e, "E3-ASD.est.e").valor_obtenido == pytest.approx(
        d["FS_desliz_ASD"], abs=tol)
    assert any("material granular" in a for a in e.avisos)


def test_el_portante_de_un_suelo_cohesivo_lleva_el_factor_i_c(tanteo):
    """phi = 0: N_c = 5.14, N_q = 1, N_gamma = 0; i_c de la ec. -5."""
    d = CP_T7B_COHESIVO["c_60"]
    tol = CP_T7B_COHESIVO["tolerancia"]
    suelo = {"cohesivo": True, "c_kpa": 60.0, "phi_grados": 0.0,
             "gamma_kn_m3": 18.0}
    e = M9.ensamble_estabilidad(replace(tanteo, suelo=suelo), EST)
    v = _v(e, "E1-LRFD.est.e")
    m = {x.simbolo: x.valor for x in v.paso.sustitucion}
    assert m["q_n"] == pytest.approx(d["q_n"], abs=tol)
    assert m["phi_b"] == pytest.approx(0.50, abs=ABS_CERO)
    assert v.valor_admisible == pytest.approx(d["q_R"], abs=tol)
    q, det = M9.resistencia_portante_nominal(
        suelo=suelo, B_efectivo=1.94694, D_f=0.80, D_w=5.0,
        H_servicio=-22.2997, V_servicio=89.9499, aplicar_inclinacion=True)
    assert det["i_c"] == pytest.approx(d["i_c"], abs=TOL_FINA)
    assert q == pytest.approx(d["q_n"], abs=tol)   # el signo de H no cuenta
    # Y con phi > 0 el termino de cohesion lleva i_c = i_q - (1-i_q)/(N_q-1):
    # i_q = 0.565636, N_q = 23.2 -> i_c = 0.565636 - 0.434364/22.2 = 0.546070
    mixto = {"cohesivo": False, "c_kpa": 10.0, "phi_grados": 32.0,
             "gamma_kn_m3": 18.0}
    _, det = M9.resistencia_portante_nominal(
        suelo=dict(mixto, cohesivo=True, phi_grados=0.0), B_efectivo=1.0,
        D_f=0.0, D_w=9.0, H_servicio=0.0, V_servicio=50.0,
        aplicar_inclinacion=True)
    assert det["i_c"] == pytest.approx(1.0, abs=ABS_CERO)


@pytest.mark.parametrize("malo", [
    dict(B_efectivo=0.0), dict(V_servicio=0.0), dict(D_f=-0.1),
    dict(B_efectivo=float("nan")), dict(H_servicio=float("inf"))])
def test_la_capacidad_portante_rechaza_lo_que_no_puede_ser(malo):
    base = dict(suelo=dict(CP["suelo"]), B_efectivo=1.8, D_f=0.8, D_w=5.0,
                H_servicio=10.0, V_servicio=80.0, aplicar_inclinacion=True)
    base.update(malo)
    with pytest.raises(DatoInvalidoError):
        M9.resistencia_portante_nominal(**base)
    # D_f = 0 es posible (zapata superficial): no hay termino de sobrecarga.
    q, _ = M9.resistencia_portante_nominal(
        suelo=dict(CP["suelo"]), B_efectivo=2.0, D_f=0.0, D_w=9.0,
        H_servicio=0.0, V_servicio=80.0, aplicar_inclinacion=True)
    assert q == pytest.approx(0.5 * 18.0 * 2.0 * 30.2, rel=REL_TRANSPORTE)


def test_en_roca_el_limite_de_excentricidad_es_otro_y_el_portante_es_del_EMS(
        tanteo, monkeypatch):
    """
    Fundacion en roca: e <= 0.45·B (nueve decimos centrales), presion
    LINEAL sobre B, y la ecuacion de capacidad de carga de suelo no aplica:
    sin la resistencia nominal del EMS, «metodo no evaluable».
      maximos: N = 123.7564, e = 0.02653 -> q_max = N/B·(1 + 6e/B)
               = 61.8782·1.07959 = 66.803 kPa
    """
    monkeypatch.setattr(M9, "cimentacion_en_roca", lambda: True)
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M9.ensamble_estabilidad(tanteo, EST)
    assert "q_n_kpa" in str(exc.value)
    suelo = dict(CP["suelo"], q_n_kpa=800.0)
    e = M9.ensamble_estabilidad(replace(tanteo, suelo=suelo), EST)
    v = _v(e, "E2-LRFD.est.e")
    assert v.valor_admisible == pytest.approx(0.45 * 2.0, abs=ABS_CERO)
    assert "nueve decimos" in v.paso.umbral.descripcion
    v = _v(e, "E1-LRFD.est.e")
    assert v.valor_obtenido == pytest.approx(66.803, abs=TOL_MM)
    assert v.valor_admisible == pytest.approx(0.45 * 800.0, abs=ABS_CERO)


def test_si_la_resultante_cae_fuera_de_la_zapata_no_hay_presion_que_dar(
        tanteo):
    """
    Una zapata de 0.50 m bajo 2.40 m de empuje: la resultante factorada cae
    fuera de la base. E1 no da una presion: no cumple, sin cifra, en los dos
    marcos; y E2 lo dice con su numero.
    """
    g = _geometria(B=0.50, ancho_talon=0.10, ancho_punta=0.10)
    e = M9.ensamble_estabilidad(_entorno(geometria=g), EST)
    v = _v(e, "E1-LRFD.est.e")
    assert v.valor_obtenido is None and v.valor_admisible is None
    assert v.paso.veredicto.tipo is TipoDeVeredicto.NO_CUMPLE
    assert "fuera de la zapata" in v.paso.veredicto.explicacion
    v2 = _v(e, "E2-LRFD.est.e")
    assert v2.valor_obtenido > 0.25 > v2.valor_admisible
    assert not v2.cumple
    asd = _v(e, "E1-ASD.est.e")
    assert asd.valor_obtenido is None
    assert asd.paso.veredicto.tipo is TipoDeVeredicto.INDICADOR
    assert len(e.verificaciones) == 6


def test_la_zapata_en_talud_usa_los_factores_que_se_declaren(tanteo):
    """
    Manual de Puentes 2.8.1.3.1.2c: q = c·N_cq + 0.5·gamma·B·N_gamma_q, con
    N_q = 0. Con N_cq = 4.0 y N_gamma_q = 20.0 DE PRUEBA:
      c = 10, gamma = 18, B = 1.50  ->  40 + 270 = 310 kPa
    Y en el ensamble (friccionante: c = 0), combinacion de maximos:
      0.5·18·1.94694·20 = 350.449 kPa; phi_b = 0.45 -> 157.702 kPa
    """
    factores = {"N_cq": 4.0, "N_gamma_q": 20.0}
    with con_valor("N_cq_N_gammaq_meyerhof", factores,
                   motivo="factores de prueba: los reales se leen de las "
                          "figuras del Manual de Puentes"):
        q = M9.capacidad_portante_zapata_en_talud(
            B=1.5, H_s=0.0, gamma=18.0, c=10.0, phi_grados=0.0)
        assert q == pytest.approx(310.0, abs=ABS_CERO)
        for malo in (dict(B=0.0), dict(gamma=0.0), dict(c=-1.0)):
            with pytest.raises(DatoInvalidoError):
                M9.capacidad_portante_zapata_en_talud(
                    **dict(dict(B=1.5, H_s=0.0, gamma=18.0, c=10.0,
                                phi_grados=0.0), **malo))
        ca.establecer_valor_dinamico("terreno_delante_del_cabezal",
                                     "talud_descendente")
        e = M9.ensamble_estabilidad(tanteo, EST)
    assert _v(e, "E1-LRFD.est.e").valor_admisible == pytest.approx(
        0.45 * 0.5 * 18.0 * 1.94694 * 20.0, abs=TOL_MM)
    for malos in ({"N_cq": 4.0}, {"N_cq": 4.0, "N_gamma_q": float("nan")},
                  "4 y 20"):
        with con_valor("N_cq_N_gammaq_meyerhof", malos,
                       motivo="segunda linea: factores mal declarados"):
            with pytest.raises(DatoInvalidoError):
                M9.capacidad_portante_zapata_en_talud(
                    B=1.5, H_s=0.0, gamma=18.0, c=10.0, phi_grados=0.0)


def test_el_portante_sismico_inclina_con_las_cargas_de_servicio_de_su_caso(
        tanteo):
    """
    AASHTO pide los factores de inclinacion con cargas SIN factorar. Bajo
    sismo hay dos casos, y cada combinacion LRFD toma las de servicio DE SU
    MISMO CASO: el q_n de la fila se reproduce llamando a la ecuacion con la
    H y la V de esa combinacion hermana, y no con las de la otra.
    """
    e = M9.ensamble_estabilidad(tanteo, SIS)
    v = _v(e, "E1-LRFD.sis.e")
    m = {x.simbolo: x for x in v.paso.sustitucion}
    nombre = m["N"].procedencia.split("«")[1].split("»")[0]
    caso = nombre.replace("Evento Extremo I, ", "").replace(" (portante)", "")
    hermana = next(c for c in e.combinaciones if c.marco == MARCO_ASD
                   and c.para == "portante" and caso in c.nombre)
    otra = next(c for c in e.combinaciones if c.marco == MARCO_ASD
                and c.para == "portante" and caso not in c.nombre)
    assert hermana.H != pytest.approx(otra.H, rel=TOL_K)

    def q_n(servicio):
        return M9.resistencia_portante_nominal(
            suelo=dict(CP["suelo"]), B_efectivo=m["B'"].valor, D_f=0.80,
            D_w=5.0, H_servicio=servicio.H, V_servicio=servicio.N,
            aplicar_inclinacion=True)[0]

    assert m["q_n"].valor == pytest.approx(q_n(hermana), rel=REL_TRANSPORTE)
    assert m["q_n"].valor != pytest.approx(q_n(otra), rel=TOL_K)
    assert v.valor_admisible == pytest.approx(0.8 * m["q_n"].valor,
                                              rel=REL_TRANSPORTE)


def test_el_talud_quebrado_no_pasa_de_la_pendiente_del_terraplen(tanteo):
    """
    Con un terraplen alto detras (sube 5.00 m), a 2·z_rel = 4.80 m el talud
    1.5 H:V todavia no se ha quebrado: ha subido 4.80/1.5 = 3.20 m, y la
    pendiente equivalente es la del propio talud, arctan(1/1.5) = 33.69.
    """
    r = M9.geometria_del_relleno(replace(tanteo, cota_borde_plataforma=107.4))
    assert r["i_grados"] == pytest.approx(math.degrees(math.atan(1 / 1.5)),
                                          abs=ABS_CERO)
    # El relleno retenido tiene que quedar SOBRE la zapata.
    with pytest.raises(DatoInvalidoError):
        M9.geometria_del_relleno(replace(tanteo, cota_relleno=100.30))


def test_con_hoya_el_freatico_se_mide_desde_su_fondo(tanteo):
    """
    Salida con hoya de 0.50 m y freatico a 1.00 m bajo el pie: queda 0.50 m
    bajo el fondo de la hoya, 0.20 m bajo la zapata (D_f efectivo 0.30 m).
    C_wq = 1.0 y C_wgamma interpola entre 0.5 y 1.0 en 1.5·B':
      0.5 + 0.5·0.20/(1.5·B')
    """
    g = _geometria(extremo="salida")
    entorno = _con_freatico(replace(_entorno(geometria=g),
                                    cota_fondo_hoya=100.30), 1.00)
    e = M9.ensamble_estabilidad(entorno, EST)
    m = {x.simbolo: x.valor for x in
         _v(e, "E1-LRFD.est.s").paso.sustitucion}
    assert m["C_wq"] == pytest.approx(1.0, abs=ABS_CERO)
    assert m["C_wgamma"] == pytest.approx(
        0.5 + 0.5 * 0.20 / (1.5 * m["B'"]), rel=REL_TRANSPORTE)


@pytest.mark.parametrize("kwargs", [
    dict(D_w=1.0, D_f=0.8, B=0.0), dict(D_w=1.0, D_f=-0.1, B=2.0),
    dict(D_w=float("nan"), D_f=0.8, B=2.0)])
def test_los_coeficientes_del_freatico_rechazan_lo_que_no_puede_ser(kwargs):
    with pytest.raises(DatoInvalidoError):
        M9.coeficientes_de_nivel_freatico(**kwargs)


def test_los_coeficientes_del_freatico_en_sus_fronteras():
    """
    Zapata superficial (D_f = 0): el agua en la superficie ESTA en el nivel
    de la zapata -> (1.0, 0.5); y justo en el desplante y justo a 1.5·B.
    """
    f = M9.coeficientes_de_nivel_freatico
    assert f(D_w=0.0, D_f=0.0, B=2.0) == pytest.approx((1.0, 0.5),
                                                       abs=ABS_CERO)
    assert f(D_w=1.5, D_f=0.0, B=2.0) == pytest.approx((1.0, 0.75),
                                                       abs=ABS_CERO)
    assert f(D_w=-0.3, D_f=0.8, B=2.0) == pytest.approx((0.5, 0.5),
                                                        abs=ABS_CERO)
    assert f(D_w=0.8, D_f=0.8, B=2.0) == pytest.approx((1.0, 0.5),
                                                       abs=ABS_CERO)
    assert f(D_w=3.8, D_f=0.8, B=2.0) == pytest.approx((1.0, 1.0),
                                                       abs=ABS_CERO)


def test_el_suelo_de_fundacion_admite_sus_valores_de_frontera():
    """
    Lo que SI es valido en el borde: cohesion nula en un friccionante, phi
    nulo en un cohesivo, phi = 45 (ultima fila de la tabla), un q_n pequeño.
    Y lo que no: cohesivo sin cohesion, friccionante sin friccion.
    """
    v = M9.validar_suelo_fundacion
    assert v({"cohesivo": False, "c_kpa": 0.0, "phi_grados": 45.0,
              "gamma_kn_m3": 0.5, "q_n_kpa": 0.5, "q_adm_kpa": 0.5},
             id_punto="T")["phi_grados"] == pytest.approx(45.0, abs=ABS_CERO)
    assert v({"cohesivo": True, "c_kpa": 0.5, "phi_grados": 0.0,
              "gamma_kn_m3": 18.0}, id_punto="T")["cohesivo"] is True
    assert v({"cohesivo": False, "c_kpa": 0.5, "phi_grados": 0.5,
              "gamma_kn_m3": 18.0}, id_punto="T")["cohesivo"] is False
    for malo in ({"cohesivo": True, "c_kpa": 0.0, "phi_grados": 20.0,
                  "gamma_kn_m3": 18.0},
                 {"cohesivo": False, "c_kpa": 5.0, "phi_grados": 0.0,
                  "gamma_kn_m3": 18.0},
                 {"cohesivo": False, "c_kpa": 0.0, "phi_grados": 30.0,
                  "gamma_kn_m3": 18.0, "gamma_saturado_kn_m3": 9.81}):
        with pytest.raises(DatoInvalidoError):
            v(malo, id_punto="T")


@pytest.mark.parametrize("clave, valor", [
    ("gamma_EQ", 1.5), ("gamma_EQ", float("nan")),
    ("punto_aplicacion_incremento_sismico", 0.0),
    ("punto_aplicacion_incremento_sismico", 1.5),
    ("fraccion_delta_sobre_phi_trasdos", 1.5),
    ("drenaje_trasdos", "a_medias"),
    ("regla_pendiente_relleno_trasdos", "a_ojo"),
    ("fila_phi_estabilidad_cabezal", "la_mejor"),
    ("factores_inclinacion_carga_portante", "quizas"),
    ("terreno_delante_del_cabezal", "ondulado"),
    ("peso_especifico_saturado_relleno_kn_m3", 9.81),
])
def test_un_criterio_del_ensamble_que_burla_la_puerta_lo_rechaza_el_consumidor(
        tanteo, clave, valor):
    """Segunda linea: ningun valor imposible llega a una cifra."""
    entorno = (_con_freatico(tanteo, 0.30)
               if clave.startswith("peso_especifico") else tanteo)
    with con_valor(clave, valor,
                   motivo="segunda linea: el consumidor no confia en la "
                          "puerta"):
        with pytest.raises(DatoInvalidoError):
            for condicion in (EST, SIS):
                M9.ensamble_estabilidad(entorno, condicion)


def test_los_valores_de_frontera_del_ensamble_si_entran(tanteo, monkeypatch):
    """
    gamma_EQ = 0 y 1, el brazo a la altura entera, delta nulo y un freatico
    en la superficie son valores posibles. Y Mononobe-Okabe vale JUSTO en su
    limite: phi = i + arctan(k_h) con k_h = tan(30) = 0.57735.
    """
    for clave, valor in (("gamma_EQ", 0.0), ("gamma_EQ", 1.0),
                         ("punto_aplicacion_incremento_sismico", 1.0),
                         ("friccion_muro_suelo_delta", 0.0)):
        with con_valor(clave, valor, motivo="valor de frontera, de prueba"):
            assert len(M9.ensamble_estabilidad(tanteo, SIS).verificaciones) \
                == 6
    with con_valor("gamma_EQ", 1.0, motivo="valor de frontera, de prueba"):
        v = _v(M9.ensamble_estabilidad(tanteo, SIS), "E2-LRFD.sis.e")
    assert v.valor_admisible == pytest.approx(0.4 * 2.0, abs=ABS_CERO)
    with con_valor("peso_especifico_saturado_relleno_kn_m3", 20.0,
                   motivo="dato de ensayo de prueba"):
        e = M9.ensamble_estabilidad(_con_freatico(tanteo, 0.0), EST)
    assert _carga(e, "WA.u").V == pytest.approx(-9.81 * 0.80 * 2.0,
                                                abs=TOL_K)
    # REESCRITO DECLARANDOLO (H1): el entorno lleva la COTA del agua, y una
    # cota por encima del terreno ya no es un dato imposible del ensamble
    # (la profundidad negativa la rechaza M0 al cargar el CSV, y
    # `datos_del_cabezal_del_punto` exige la columna finita). La segunda
    # linea del ensamble es ahora la cota no finita.
    with pytest.raises(DatoInvalidoError):
        M9.ensamble_estabilidad(replace(tanteo, cota_freatico=math.nan), EST)
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h=math.tan(math.radians(30.0)), k_v=0.0))
    # REESCRITO DECLARANDOLO (correcciones de T-7b, H4): el limite exacto de
    # Mononobe-Okabe es de la FORMULA cerrada, y se prueba con ella. Con la
    # cuña de archivo y el relleno horizontal indefinido del muro de tanteo,
    # en phi = psi el empuje tiene su supremo en el BORDE del intervalo (el
    # plano de falla horizontal): no hay maximo interior, y se detiene.
    with pytest.raises(MetodoNoEvaluableError):
        M9.ensamble_estabilidad(tanteo, SIS)
    with con_valor("regla_pendiente_relleno_trasdos", "talud_quebrado_2h",
                   motivo="la formula cerrada en su limite"):
        assert M9.ensamble_estabilidad(tanteo, SIS).K_AE > 0.9


def test_bajo_sismo_cada_fila_imprime_su_peor_combinacion(tanteo):
    """
    Con dos casos sismicos (y dos variantes de cada uno), cada fila imprime
    la combinacion de MENOR holgura o de mayor aprovechamiento, que no es la
    misma para todas: el deslizamiento lo rige el caso 2 y el portante el
    caso 1 sin el peso de la sobrecarga. A mano en `CP_T7B_PEOR_COMBINACION`.
    """
    d = CP_T7B_PEOR_COMBINACION
    tol = d["tolerancia"]
    e = M9.ensamble_estabilidad(tanteo, SIS)
    v = _v(e, "E3-LRFD.sis.e")
    assert v.valor_obtenido == pytest.approx(d["E3_LRFD_sis"]["H"], abs=tol)
    assert v.valor_admisible == pytest.approx(d["E3_LRFD_sis"]["R_R"],
                                              abs=tol)
    v = _v(e, "E1-LRFD.sis.e")
    assert v.valor_obtenido == pytest.approx(d["E1_LRFD_sis"]["sigma_v"],
                                             abs=tol)
    assert v.valor_admisible == pytest.approx(d["E1_LRFD_sis"]["q_R"],
                                              abs=tol)
    assert _v(e, "E2-ASD.sis.e").valor_obtenido == pytest.approx(
        d["E2_ASD_sis"], abs=tol)
    assert _v(e, "E3-ASD.sis.e").valor_obtenido == pytest.approx(
        d["E3_ASD_sis"], abs=tol)


def test_el_talon_del_segundo_muro_descuenta_la_subpresion(muro_2):
    """La subpresion alivia el talon: V_u y M_u a mano, con su reparto."""
    d = CP_T7B_PEOR_COMBINACION["muro_2_talon_max"]
    e = _ensamble_muro_2(muro_2)
    s = next(x for x in e.solicitaciones if x.elemento == ELEMENTO_ZAPATA
             and "talon" in x.seccion and "maximos" in x.combinacion)
    assert s.V_u == pytest.approx(d["V_u"], abs=d["tolerancia"])
    assert s.M_u == pytest.approx(d["M_u"], abs=d["tolerancia"])


def test_el_agua_bajo_la_zapata_reduce_los_dos_terminos_del_portante():
    """
    Freatico a 0.30 m con D_f = 0.80 y B' = 2.00: C_wq = 0.5 + 0.5·0.30/0.80
    = 0.6875 y C_wgamma = 0.5. Sin inclinacion:
      q_n = 18·0.80·23.2·0.6875 + 0.5·18·2.00·30.2·0.5 = 229.68 + 271.80
          = 501.48 kPa
    """
    q, det = M9.resistencia_portante_nominal(
        suelo=dict(CP["suelo"]), B_efectivo=2.0, D_f=0.80, D_w=0.30,
        H_servicio=0.0, V_servicio=80.0, aplicar_inclinacion=False)
    assert (det["C_wq"], det["C_wgamma"]) == pytest.approx((0.6875, 0.5),
                                                           abs=ABS_CERO)
    assert q == pytest.approx(501.48, abs=TOL_K)


def test_el_entorno_sin_la_longitud_calculada_cae_en_lo_declarado():
    """
    Cuando 7.B no calculo la longitud (se declaro): el borde de la
    plataforma es la rasante en el eje, y lo dice; el talud, el criterio. Y
    un cabezal de tanteo sin losa toma como pie el desplante mas D_f. La
    hoya de socavacion solo llega al cabezal de SALIDA.
    """
    entrada = _geometria(extremo="entrada")
    salida = _geometria(extremo="salida", cota_desplante=99.0,
                        cota_coronacion=101.55)
    punto = SimpleNamespace(id="T-00", cota_rasante=104.5, esviaje_grados=7.0,
                            NF_profundidad_m=2.2, cota_terreno=101.0)
    cabezal = SimpleNamespace(geometrias=(entrada, salida))
    sin_calcular = SimpleNamespace(longitud_calculada=None)
    hoya = SimpleNamespace(cota_fondo_de_la_hoya=99.4)
    e, s = M9.datos_del_cabezal_del_punto(
        punto=punto, cabezal=cabezal, geometria=sin_calcular,
        socavacion=hoya, suelo_del_punto=dict(CP["suelo"]))
    bordillo = ca.valor("predimensionamiento_cabezal")["bordillo_m"]
    talud = ca.valor("talud_terraplen")
    for entorno, g in ((e, entrada), (s, salida)):
        assert entorno.cota_borde_plataforma == pytest.approx(
            104.5, abs=ABS_CERO)
        assert "rasante en el eje" in entorno.origen_cota_borde
        assert entorno.talud == pytest.approx(talud, rel=REL_TRANSPORTE)
        assert entorno.cota_pie == pytest.approx(g.cota_desplante + 0.80,
                                                 abs=ABS_CERO)
        assert entorno.cota_relleno == pytest.approx(
            g.cota_coronacion - bordillo, abs=ABS_CERO)
        assert entorno.esviaje_grados == pytest.approx(7.0, abs=ABS_CERO)
        assert entorno.suelo == CP["suelo"]
        # H1: la cota del agua sale del terreno del CRUCE y es la misma para
        # los dos cabezales, aunque sus pies esten a cotas distintas.
        assert entorno.cota_freatico == pytest.approx(101.0 - 2.2,
                                                      abs=ABS_CERO)
        assert "terreno natural del cruce" in entorno.origen_freatico
    assert e.cota_fondo_hoya is None
    assert s.cota_fondo_hoya == pytest.approx(99.4, abs=ABS_CERO)
    # Con la longitud calculada, el borde y el talud son los de 7.B.
    calculada = SimpleNamespace(longitud_calculada=SimpleNamespace(
        talud=1.75, cota_borde_entrada=104.1, cota_borde_salida=103.9))
    e, s = M9.datos_del_cabezal_del_punto(
        punto=punto, cabezal=cabezal, geometria=calculada)
    assert (e.cota_borde_plataforma, s.cota_borde_plataforma) \
        == pytest.approx((104.1, 103.9), abs=ABS_CERO)
    assert e.talud == pytest.approx(1.75, abs=ABS_CERO)
    assert "de 7.B" in e.origen_cota_borde
    assert s.cota_fondo_hoya is None and e.suelo is None


def test_el_brazo_del_empuje_sismico_total_es_el_promedio_ponderado(tanteo):
    """
    z_AE = (P_A·z_A + dP·z_dP) / P_AE = (15.4100·0.80 + 10.9403·1.44) /
    26.3503 = (12.3280 + 15.7540)/26.3503 = 1.06572 m = 0.444·h, dentro de
    la franja 0.4·h a 0.5·h de AASHTO C11.6.5.3.
    """
    _, datos = M9.cargas_del_cabezal(tanteo, SIS)
    assert datos["z_AE"] == pytest.approx(1.06572, abs=TOL_FINA)
    assert 0.4 * 2.4 <= datos["z_AE"] <= 0.5 * 2.4
    assert datos["P_AE"] == pytest.approx(CP["sismico"]["P_AE"], abs=TOL)
    assert datos["W_w"] == pytest.approx(14.136 + 18.848, abs=ABS_CERO)


# ===========================================================================
# 14-bis. LAS CORRECCIONES DE LA AUDITORIA ADVERSARIAL (H1 a H10)
# ===========================================================================
# El rojo de estos tests se MIDIO contra la FASE A (`fc792d9`): los simbolos
# nuevos no existian (`cuna_de_tanteo`, `regimen_cabezal`,
# `hidraulica_a_presion`, `cota_freatico`...) y cada uno fallaba por
# separado; ver la ficha T7B-13 de `docs/decisiones_diferidas.md`.

CU = CP_T7B_CUNA


@pytest.mark.parametrize("rho", sorted(CU["quebrado"]["P_por_rho"]))
def test_H4_cada_cuna_escrita_a_mano_da_su_empuje(rho):
    """
    El dorado de la superficie QUEBRADA, cuña a cuña (`CP_T7B_CUNA`): tres
    cortan la plataforma y una el talud, que son las dos ramas del area.
    """
    q = CU["quebrado"]
    P = M9.empuje_de_una_cuna(rho_grados=rho, h=q["h"], subida=q["subida"],
                              talud=q["talud"], phi_grados=q["phi"],
                              delta_grados=q["delta"], gamma=q["gamma"])
    assert P == pytest.approx(q["P_por_rho"][rho], abs=CU["tolerancia"])


def test_H4_la_cuna_critica_es_el_maximo_de_las_escritas_y_no_menos():
    q = CU["quebrado"]
    P, rho = M9.cuna_de_tanteo(h=q["h"], subida=q["subida"], talud=q["talud"],
                               phi_grados=q["phi"], delta_grados=q["delta"],
                               gamma=q["gamma"])
    assert P >= max(q["P_por_rho"].values()) - CU["tolerancia"]
    assert 50.0 < rho < 60.0
    sismica = M9.empuje_de_una_cuna(
        rho_grados=50.0, h=q["h"], subida=q["subida"], talud=q["talud"],
        phi_grados=q["phi"], delta_grados=q["delta"], gamma=q["gamma"],
        k_h=q["k_h"])
    assert sismica == pytest.approx(q["P_sismico_rho_50"],
                                    abs=CU["tolerancia"])
    P_E, _ = M9.cuna_de_tanteo(h=q["h"], subida=q["subida"],
                               talud=q["talud"], phi_grados=q["phi"],
                               delta_grados=q["delta"], gamma=q["gamma"],
                               k_h=q["k_h"])
    assert P_E >= sismica


def test_H4_con_talud_sin_quiebre_la_cuna_es_coulomb():
    """Primer limite analitico: la ec. 3.11.5.3-1 de AASHTO, a mano."""
    c = CU["coulomb"]
    P, _ = M9.cuna_de_tanteo(h=c["h"], subida=math.inf, talud=c["talud"],
                             phi_grados=c["phi"], delta_grados=c["delta"],
                             gamma=c["gamma"])
    assert P == pytest.approx(c["P_A"], abs=CU["tolerancia"])
    assert 2 * P / (c["gamma"] * c["h"] ** 2) == pytest.approx(
        c["K_A"], abs=CU["tolerancia"])


def test_H4_con_relleno_horizontal_y_sismo_la_cuna_es_mononobe_okabe():
    """Segundo limite analitico: A11.3.1-1 con beta = i = 0, a mano."""
    m = CU["mononobe_okabe"]
    P, _ = M9.cuna_de_tanteo(h=m["h"], subida=0.0, talud=2.0,
                             phi_grados=m["phi"], delta_grados=m["delta"],
                             gamma=m["gamma"], k_h=m["k_h"])
    assert P == pytest.approx(m["P_AE"], abs=CU["tolerancia"])


@pytest.mark.parametrize("extremo", ["entrada", "salida"])
def test_H4_los_oraculos_del_auditor_sobre_A01_se_reproducen(extremo):
    """
    CONTRASTE con la cuña independiente del auditor adversarial (la de su
    script `cuna.py`), sobre la geometria de A-01 de la FASE A: estatica,
    k_h = 0.25 y k_h = 0.50 (la de archivo, que la cuña SI evalua).
    """
    o = CU["auditor"][extremo]
    for k_h, esperado in o["P"].items():
        P, _ = M9.cuna_de_tanteo(h=o["h"], subida=o["subida"], talud=2.0,
                                 phi_grados=34.0, delta_grados=22.78,
                                 gamma=17.0, k_h=k_h)
        assert P == pytest.approx(esperado, abs=TOL_CM)


@pytest.mark.parametrize("kwargs", [
    dict(h=0.0), dict(h=-1.0), dict(h=math.nan), dict(talud=0.0),
    dict(phi_grados=0.0), dict(delta_grados=40.0), dict(k_v=1.0),
    dict(k_h=-0.1), dict(subida=-0.5), dict(subida=math.nan),
])
def test_H4_la_cuna_rechaza_lo_que_no_puede_ser(kwargs):
    base = dict(h=2.0, subida=0.5, talud=2.0, phi_grados=30.0,
                delta_grados=20.0, gamma=18.0)
    base.update(kwargs)
    with pytest.raises(DatoInvalidoError):
        M9.cuna_de_tanteo(**base)


def test_H4_la_cuna_sin_maximo_no_da_cifra():
    """
    MAT-D13: un talud sin quiebre mas empinado que phi - psi -- el empuje
    crece sin cota hacia el talud -- no tiene cuña critica: «metodo no
    evaluable» con el rotulo del cabezal, nunca una cifra.
    """
    with pytest.raises(MetodoNoEvaluableError) as exc:
        M9.cuna_de_tanteo(h=2.0, subida=math.inf, talud=2.0, phi_grados=34.0,
                          delta_grados=22.78, gamma=17.0, k_h=0.5)
    assert str(exc.value).startswith(modelos.MOTIVO_METODO_NO_EVALUABLE_CABEZAL)


def test_H4_el_ensamble_usa_la_cuna_y_la_formula_queda_de_contraste(tanteo):
    """
    El muro de tanteo con relleno QUEBRADO (sube 0.40 m con talud 1.5 hasta
    la plataforma): K_A es el equivalente de la cuña, 2·P/(gamma·h²), el
    empuje se reparte como el de Coulomb (resultante a h/3 en seco) y la
    formula cerrada con la pendiente 2H queda impresa como contraste. Con
    relleno horizontal (el muro de tanteo) la cuña ES Coulomb: los dorados
    del primer muro no se mueven.
    """
    e0 = M9.ensamble_estabilidad(tanteo, EST)
    assert e0.metodo_empuje == M9.METODO_EMPUJE_CUNA
    assert e0.K_A == pytest.approx(e0.K_A_contraste, abs=TOL_K)
    quebrado = replace(tanteo, cota_borde_plataforma=100.0 + CP["h"] + 0.40)
    e = M9.ensamble_estabilidad(quebrado, EST)
    rel = M9.geometria_del_relleno(quebrado)
    P, _ = M9.cuna_de_tanteo(h=rel["h"], subida=rel["subida_sobre_plano"],
                             talud=1.5, phi_grados=CP["phi_relleno"],
                             delta_grados=0.67 * CP["phi_relleno"],
                             gamma=CP["gamma_relleno"])
    assert e.K_A == pytest.approx(2 * P / (CP["gamma_relleno"] * rel["h"] ** 2),
                                  rel=REL_TRANSPORTE)
    # El sesgo de la pendiente equivalente depende de la geometria: en este
    # muro (talud 1.5, quiebre cerca) la formula da MAS que la cuña; en los
    # cabezales de A-01 da del 7 al 11 % MENOS (el oraculo del auditor). El
    # paso dice cuanto y hacia donde.
    assert e.K_A_contraste is not None
    assert abs(e.K_A_contraste - e.K_A) > TOL_K
    eh = _carga(e, "EH.h")
    assert eh.z == pytest.approx(rel["h"] / 3, abs=TOL_K)
    paso = next(p for p in e.pasos if p.codigo.startswith("9.2.1"))
    assert "AASHTO_LRFD_9.3.11.5.8.1#CUNA" in paso.citas_textuales
    procedencias = str([m.procedencia for m in paso.sustitucion])
    assert "CONTRASTE" in procedencias
    assert ("% MAS que la cuña" in procedencias
            or "% MENOS que la cuña" in procedencias)


def test_H4_con_la_regla_2H_rige_la_formula_y_su_sesgo_se_dice():
    c = ca.CRITERIOS["regla_pendiente_relleno_trasdos"]
    assert c.valor == "cuna_de_tanteo"
    assert "7 a 11 %" in c.justificacion and "MENOR" in c.justificacion
    for cita in ("AASHTO_LRFD_9.3.11.5.3#CULMANN",
                 "AASHTO_LRFD_9.3.11.5.8.1#CUNA",
                 "AASHTO_LRFD_9.C11.6.5.3#CUNA"):
        assert cita in c.justificacion or cita in c.fuente


@pytest.mark.parametrize("cita_id, caracter, pagina_pdf", [
    ("AASHTO_LRFD_9.3.11.5.3#CULMANN", "PERMISO", 175),
    ("AASHTO_LRFD_9.3.11.5.8.1#CUNA", "RECOMENDACION", 191),
    ("AASHTO_LRFD_9.C11.6.5.3#CUNA", "PERMISO", 1499),
    ("AASHTO_LRFD_9.C11.6.5.4#CEDENTE", "DEFINICION", 1501),
    ("AASHTO_LRFD_9.C11.6.5.4#K0", "RECOMENDACION", 1501),
    ("AASHTO_LRFD_9.3.11.5.2#K0", "PERMISO", 174),
    ("HDS5_3ED.2.2.5#NO_EXCEDER", "RECOMENDACION", 71),
    ("HDS5_3ED.2.2.5a#COTA_DE_DANO", "PERMISO", 72),
])
def test_las_citas_de_las_correcciones_estan_en_el_registro(
        cita_id, caracter, pagina_pdf):
    c = construir().cita(cita_id)
    assert c.caracter.name == caracter
    assert c.pagina_pdf == pagina_pdf


@pytest.mark.pdf
@pytest.mark.parametrize("cita_id", [
    "AASHTO_LRFD_9.3.11.5.3#CULMANN", "AASHTO_LRFD_9.3.11.5.8.1#CUNA",
    "AASHTO_LRFD_9.C11.6.5.3#CUNA", "AASHTO_LRFD_9.C11.6.5.4#CEDENTE",
    "AASHTO_LRFD_9.C11.6.5.4#K0", "AASHTO_LRFD_9.3.11.5.2#K0",
    "HDS5_3ED.2.2.5#NO_EXCEDER", "HDS5_3ED.2.2.5a#COTA_DE_DANO",
])
def test_el_literal_de_las_citas_nuevas_esta_en_su_pagina(cita_id):
    """Cada literal, leido otra vez en su pagina del PDF (sin espacios)."""
    import fitz
    c = construir().cita(cita_id)
    ruta = fuentes.ruta_pdf(fuentes.FUENTES[c.fuente_id])
    if not ruta.exists():
        pytest.skip(f"no esta el PDF de {c.fuente_id}")
    texto = fitz.open(str(ruta))[c.pagina_pdf - 1].get_text()
    plano = lambda t: "".join(t.split()).replace("–", "-")
    assert plano(c.texto_literal.texto) in plano(texto)


# --- H5: lo que cambia de veredicto dentro de la ventana se avisa ---------

def test_H5_una_fila_que_cambia_de_veredicto_con_la_fila_de_phi_se_avisa(
        tanteo):
    """
    Con el suelo de fundacion del muro de tanteo a phi_f = 26 grados (de
    prueba), el empuje factorado queda ENTRE la resistencia con la fila de
    las zapatas (0.80·R_tau) y la de muros (1.0·R_tau): E3-LRFD no cumple
    con la de archivo y cumpliria con la otra. El aviso lo dice con las dos
    cifras y el veredicto de archivo no cambia. Con el suelo del dorado (32
    grados) cumple con las dos y no hay aviso.
    """
    e = M9.ensamble_estabilidad(tanteo, EST)
    assert not [a for a in e.avisos if "E3-LRFD" in a
                and "CAMBIA DE VEREDICTO" in a]
    suelo = dict(CP["suelo"], phi_grados=26.0)
    e2 = M9.ensamble_estabilidad(replace(tanteo, suelo=suelo), EST)
    v2 = _v(e2, "E3-LRFD.est.e")
    R_tau = v2.valor_admisible / 0.80
    assert 0.80 * R_tau < v2.valor_obtenido <= 1.0 * R_tau
    assert v2.estado is EstadoDeVerificacion.NO_CUMPLE
    aviso = [a for a in e2.avisos if "E3-LRFD.est.e" in a
             and "CAMBIA DE VEREDICTO" in a]
    assert len(aviso) == 1
    assert "'zapatas_seccion_10'" in aviso[0]
    assert "'muros_tabla_11_5_7'" in aviso[0]
    assert f"{v2.valor_obtenido:.2f} contra {v2.valor_admisible:.2f} " \
           "(no cumple)" in aviso[0]
    assert f"contra {R_tau:.2f} (cumple)" in aviso[0]


def test_H5_los_factores_de_inclinacion_tambien_se_contrastan(tanteo):
    e = M9.ensamble_estabilidad(tanteo, SIS)
    for a in e.avisos:
        if "CAMBIA DE VEREDICTO" in a:
            assert "factores_inclinacion_carga_portante" in a \
                or "fila_phi_estabilidad_cabezal" in a
    # El contraste no detiene ni cambia el veredicto de archivo.
    assert e.verificaciones == M9.ensamble_estabilidad(tanteo, SIS).verificaciones


def test_H5_la_fila_de_phi_se_justifica_como_la_mas_exigente_y_no_por_remision():
    c = ca.CRITERIOS["fila_phi_estabilidad_cabezal"]
    assert "la mas exigente" in c.justificacion
    assert "AASHTO_LRFD_9.11.5.7#MUROS" in c.justificacion
    assert "no porque la tabla de muros remita" in c.justificacion
    assert "sensible" in c.justificacion


# --- H6: el agua sin drenaje no pasa del relleno retenido; con drenaje, el
#     aviso del desembalse rapido ----------------------------------------

def test_H6_sin_drenaje_el_agua_no_sube_por_encima_del_relleno_retenido(
        tanteo):
    """
    Muro de tanteo con el terreno SUBIENDO sobre el talon (h > z_rel): sin
    drenaje el agua llega a z_rel (el relleno retenido contra el trasdos) y
    no a h.
    """
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    quebrado = replace(tanteo, cota_borde_plataforma=100.0 + CP["h"] + 0.40)
    rel = M9.geometria_del_relleno(quebrado)
    assert rel["h"] > rel["z_rel"]
    with con_valor("peso_especifico_saturado_relleno_kn_m3", 20.0,
                   motivo="dato de ensayo de prueba"):
        cargas, datos = M9.cargas_del_cabezal(quebrado, EST)
    assert datos["h_w"] == pytest.approx(rel["z_rel"], abs=ABS_CERO)
    assert _carga(SimpleNamespace(cargas=cargas), "WA.h").H == pytest.approx(
        9.81 * rel["z_rel"] ** 2 / 2, rel=REL_TRANSPORTE)


def test_H6_con_drenaje_se_avisa_el_desembalse_rapido_con_su_orden(tanteo):
    """
    Con el agua de diseño a 1.50 m sobre la base (de prueba) el aviso da
    9.81·1.50²/2 = 11.0 kN/m frente a la componente horizontal del empuje.
    """
    entorno = replace(tanteo, cota_agua_diseno=100.0 + 1.50)
    e = M9.ensamble_estabilidad(entorno, EST)
    aviso = next(a for a in e.avisos if "desembalse rapido" in a)
    assert "C11.6.6" in aviso and "11.0 kN/m" in aviso
    sin_nivel = M9.ensamble_estabilidad(tanteo, EST)
    assert any("desembalse rapido" in a and "Orden de magnitud" not in a
               for a in sin_nivel.avisos)


def test_H6_drenaje_de_archivo_sigue_sin_drenaje_y_la_ficha_lo_dice():
    c = ca.CRITERIOS["drenaje_trasdos"]
    assert c.valor == "sin_drenaje"
    assert "desembalse rapido" in c.justificacion
    assert "nunca sube por encima del muro" in c.justificacion
    assert "nunca por encima del muro" in cn.HIPOTESIS_EMPUJE_BAJO_NF


# --- H8: lo que decia lo contrario que el codigo -------------------------

def test_H8_el_peso_saturado_del_suelo_de_fundacion_ya_no_se_admite():
    """
    `gamma_saturado_kn_m3` del suelo de fundacion se validaba y NADIE lo
    leia (el portante bajo el freatico va con los C_w de la Tabla
    10.6.3.1.2a-2): se retiro, y ahora es un campo no reconocido.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        M9.validar_suelo_fundacion(dict(CP["suelo"],
                                        gamma_saturado_kn_m3=20.0))
    assert "no reconocidos" in str(exc.value)
    assert "gamma_saturado_kn_m3" not in M9.CAMPOS_SUELO_OPCIONALES


def test_H8_la_nota_del_deslizamiento_en_arcilla_dice_lo_que_el_codigo_hace():
    nota = construir().cita("AASHTO_LRFD_9.10.6.3.4#RESISTENCIA").nota
    assert "ESTA implementado" in nota and "NO esta" not in nota
    assert "la estabilidad y el armado NO estan aqui" not in (
        servicio._fase_9.__doc__)


def test_H8_un_cabezal_con_una_sola_condicion_evaluada_se_avisa(tanteo):
    est = M9.ensamble_estabilidad(tanteo, EST)
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class _Cab:
        id_punto: str
        geometrias: tuple
        avisos: tuple = ()
        verificaciones: tuple = ()
        pasos: tuple = ()
        estabilidad: tuple = ()
    integrado = M9.integrar_estabilidad(
        _Cab(id_punto="T-00", geometrias=(tanteo.geometria,)), (est,))
    assert any("SOLO en la condicion estatico" in a
               and "sismico quedo sin evaluar" in a
               for a in integrado.avisos)


# --- H9: el alero que crece sin cota se avisa ----------------------------

@pytest.mark.lento
def test_H9_un_alero_mas_largo_que_el_conducto_se_avisa(tmp_path):
    """
    A-01 con un esviaje que lleva alfa + theta cerca de 90 grados (alfa = 30
    de la regla, theta declarado a 58 en el CSV de prueba): el alero largo
    supera la longitud entre cabezales y se AVISA, comparado con esa
    magnitud y sin umbral nuevo. Con el esviaje del fixture (15) no.
    """
    _, a01 = _correr_de_prueba(tmp_path)
    assert not [a for a in a01.avisos() if "MAS que la longitud entre" in a]
    texto = _csv_con_freatico(tmp_path, NF_DE_PRUEBA).read_text(
        encoding="utf-8")
    fila = FILA_A01.replace(",SM,,,", f",SM,{NF_DE_PRUEBA},,")
    assert fila in texto
    ruta = tmp_path / "esviado.csv"
    ruta.write_text(texto.replace(fila, fila.replace(",8.5,15,", ",8.5,58,")),
                    encoding="utf-8")
    externos = _externos(tmp_path, puntos={"A-01": {
        "cota_afectacion_aguas_arriba_msnm": COTA_AFECTACION_DE_PRUEBA,
        "Q_evento_extremo_m3s": 1.3, "TW_evento_extremo_m": 0.5}},
        globales={"luz_m": 3.0, "TW_m": 0.3})
    for clave, valor in DECLARACIONES_DE_PRUEBA.items():
        ca.establecer_valor_dinamico(clave, valor)
    ca.establecer_valor_dinamico("remanso_derecho_via", "cota_de_afectacion")
    _declarar_sitio()
    informe = servicio.correr(ruta, externos,
                              alcance=servicio.ALCANCE_EXPEDIENTE)
    a01 = next(p for p in informe.puntos if p.punto.id == "A-01")
    assert a01.cabezal is not None
    aviso = [a for a in a01.avisos() if "MAS que la longitud entre" in a]
    assert len(aviso) == 1
    largo = max(g.aleros.longitud_largo for g in a01.cabezal.geometrias)
    assert largo > a01.cabezal.longitud_entre_cabezales


# --- H7: el regimen del cabezal y la marca de la interfaz de T-7c ---------

def test_H7_el_regimen_es_un_criterio_y_cedente_es_la_hipotesis_de_archivo():
    c = ca.CRITERIOS["regimen_cabezal"]
    assert c.valor == "cedente" and c.etiqueta == "A"
    assert tuple(c.sensibilidad) == ("cedente", "no_cedente")
    assert c.nivel == ca.NIVEL_EXPEDIENTE
    for cita in ("AASHTO_LRFD_9.C11.6.5.4#CEDENTE",
                 "AASHTO_LRFD_9.C11.6.5.4#K0",
                 "AASHTO_LRFD_9.11.6.5.4#NO_CEDENTE"):
        assert cita in c.justificacion or cita in c.fuente


def test_H7_declarar_no_cedente_detiene_la_estabilidad_sin_cifra(tanteo):
    with con_valor("regimen_cabezal", "no_cedente",
                   motivo="el regimen que no esta implementado"):
        with pytest.raises(MetodoNoEvaluableError) as exc:
            M9.ensamble_estabilidad(tanteo, EST)
    assert "11.6.5.4" in str(exc.value)


def test_H7_las_solicitaciones_dicen_con_que_coeficiente_salen(tanteo):
    """
    Cada solicitacion lleva el regimen, el coeficiente con que se calcularon
    sus empujes y el K0 de 3.11.5.2 con su cociente: K0 = 1 - sen 30 = 0.5
    en el muro de tanteo (phi = 30), y K0/K_A el factor por el que crecerian
    los empujes de una pantalla que no cede.
    """
    est = M9.ensamble_estabilidad(tanteo, EST)
    sis = M9.ensamble_estabilidad(tanteo, SIS)
    assert est.regimen == "cedente" and est.K0 == pytest.approx(
        1 - math.sin(math.radians(CP["phi_relleno"])), abs=ABS_CERO)
    for s in est.solicitaciones:
        assert s.regimen == "cedente" and s.coeficiente_de_empuje == "K_A"
        assert s.K_empuje == pytest.approx(est.K_A, abs=ABS_CERO)
        assert s.K0_sobre_K_A == pytest.approx(est.K0 / est.K_A, abs=ABS_CERO)
        assert s.K0_sobre_K_A > 1
    for s in sis.solicitaciones:
        assert s.coeficiente_de_empuje == "K_AE"
        assert s.K_empuje == pytest.approx(sis.K_AE, abs=ABS_CERO)


# ===========================================================================
# 15. DE PUNTA A PUNTA POR `servicio.correr`
# ===========================================================================

# REESCRITO DECLARANDOLO (correcciones de T-7b): el metodo de V5 de las
# corridas de prueba es el de COTA (H2: el que la fuente sostiene), con una
# cota de afectacion DE PRUEBA, y no un derecho de via de 400 m que no existe;
# los tests del embalse a nivel lo declaran aparte. Y el freatico de prueba
# baja de 1.40 a 2.00 m bajo el terreno del cruce (H1: medido desde el
# cruce, 1.40 m deja 0.20 m de agua sobre la base del cabezal de salida y su
# sismica no es evaluable): el caso de 1.40 m tiene su propio test.
COTA_AFECTACION_DE_PRUEBA = 44.00   # msnm, DE PRUEBA: 1.90 m sobre el terreno
NF_DE_PRUEBA = "2.0"                # m bajo el terreno del cruce, DE PRUEBA
DECLARACIONES_DE_PRUEBA = {
    "TR_evento_extremo": 500.0,
    "umbral_no_colapso_evento_extremo": "sin_desborde_de_la_plataforma",
    "phi_relleno_trasdos": 34.0,
    "c_phi_fundacion": {"cohesivo": False, "c_kpa": 0.0, "phi_grados": 32.0,
                        "gamma_kn_m3": 18.0},
    "drenaje_trasdos": "drenado",
    "factor_muro_eleccion": "reduccion_por_desplazamiento",
}
FILA_A01 = ("A-01,0+380,A,1.167,850,0.006,42.10,44.20,44.05,8.5,15,9.60,"
            "41.30,,,SM,,,")


def _csv_con_freatico(tmp_path, NF="1.4"):
    """El CSV de ejemplo con el freatico de A-01 lleno (DE PRUEBA)."""
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    assert FILA_A01 in texto
    ruta = tmp_path / "puntos.csv"
    ruta.write_text(texto.replace(
        FILA_A01, FILA_A01.replace(",SM,,,", f",SM,{NF},,")),
        encoding="utf-8")
    return ruta


def _correr_de_prueba(tmp_path, *, metodo_v5="cota_de_afectacion",
                      cota_afectacion=COTA_AFECTACION_DE_PRUEBA, ancho=None,
                      extra_a01=None, declaraciones=None, NF=NF_DE_PRUEBA,
                      alcance=servicio.ALCANCE_EXPEDIENTE):
    """
    Corrida de expediente con TODO declarado, de prueba: ningun valor de
    estos es del proyecto. Entran por las puertas reales (el JSON de datos
    externos, `establecer_valor_dinamico` y el [S] por sesion).
    """
    a01 = {"Q_evento_extremo_m3s": 1.3, "TW_evento_extremo_m": 0.5}
    if cota_afectacion is not None:
        a01["cota_afectacion_aguas_arriba_msnm"] = cota_afectacion
    if ancho is not None:
        a01["ancho_derecho_via_m"] = ancho
    ca.establecer_valor_dinamico("remanso_derecho_via", metodo_v5)
    a01.update(extra_a01 or {})
    externos = _externos(tmp_path, puntos={"A-01": a01},
                         globales={"luz_m": 3.0, "TW_m": 0.3})
    for clave, valor in dict(DECLARACIONES_DE_PRUEBA,
                             **(declaraciones or {})).items():
        ca.establecer_valor_dinamico(clave, valor)
    _declarar_sitio()
    informe = servicio.correr(_csv_con_freatico(tmp_path, NF), externos,
                              alcance=alcance)
    return informe, next(p for p in informe.puntos if p.punto.id == "A-01")


@pytest.mark.lento
def test_A01_llega_a_la_Fase_9_con_E1_a_E3_evaluadas(tmp_path):
    """
    EL TEST DE PUNTA A PUNTA DEL ENCARGO (residual de INF-4.2 / INF-4.3,
    ficha T7A-01): a `--alcance expediente`, con V5 y V8 declarados, A-01
    dimensiona, alcanza la Fase 9 y sus dos cabezales salen con E1 a E3
    evaluadas en los dos marcos y las dos condiciones.
    """
    informe, a01 = _correr_de_prueba(tmp_path)
    assert a01.dimensionado
    assert a01.resultado.seccion.etiqueta() == "Ø 0.90 m"
    codigos = {v.codigo: v for v in a01.resultado.verificaciones}
    assert codigos["V5"].estado is EstadoDeVerificacion.CUMPLE
    assert codigos["V8"].estado is EstadoDeVerificacion.CUMPLE
    # V5 por el metodo de cota (H2): la cota de afectacion de prueba.
    assert codigos["V5"].valor_admisible == pytest.approx(
        COTA_AFECTACION_DE_PRUEBA, abs=ABS_CERO)
    assert a01.cabezal is not None
    est = a01.cabezal.estabilidad
    assert [(e.extremo, e.condicion) for e in est] == [
        ("entrada", EST), ("entrada", SIS), ("salida", EST), ("salida", SIS)]
    for e in est:
        codigos_e = [v.codigo for v in e.verificaciones]
        assert len(codigos_e) == 6
        assert {c.split(".")[0] for c in codigos_e} == {
            "E1-LRFD", "E2-LRFD", "E3-LRFD", "E1-ASD", "E2-ASD", "E3-ASD"}
        for v in e.verificaciones:
            assert v.valor_obtenido is not None and v.valor_admisible is not None
            assert math.isfinite(v.valor_obtenido)
        assert [p[0] for p in e.pendientes] == ["E4", "E5"]
    # Los avisos de los cuatro ensambles llegan al punto, sin repetirse.
    assert len(a01.cabezal.avisos) == len(set(a01.cabezal.avisos))
    assert sum("E4 y E5" in a for a in a01.cabezal.avisos) == 2
    assert all(a in a01.avisos() for a in a01.cabezal.avisos)
    # Las filas E viajan con las CB del cabezal: el informe las cuenta.
    todas = {v.codigo for v in a01.cabezal.verificaciones}
    assert {"E1-LRFD.est.e", "E3-ASD.sis.s"} <= todas
    assert not [b for b in a01.bloqueos if "estabilidad" in b.etapa]


@pytest.mark.lento
def test_con_la_regla_de_T7a_el_cabezal_de_A01_no_pasa_y_el_informe_lo_cuenta(
        tmp_path):
    """
    HALLAZGO que la corrida de punta a punta deja medido, y que se reporta
    en vez de taparlo: con la zapata que propone la regla de T-7a (0.70 de la
    altura total: 1.575 m en la entrada de A-01) y el suelo DE PRUEBA, el
    deslizamiento del marco que rige NO cumple en ninguno de los dos
    cabezales (33.95 > 28.86 kN/m a la entrada), ni la capacidad portante
    bajo sismo. El punto sigue dimensionado -- el conducto es el de la linea
    base -- y las filas salen como INCUMPLIDAS del punto; las del marco ASD
    que fallan, como avisos. T-7b no toca la regla: la progresion de
    dimensiones es una decision que el encargo no trae (ficha T7B-09).
    """
    _, a01 = _correr_de_prueba(tmp_path)
    assert a01.dimensionado
    incumplidas = {v.codigo for v in a01.incumplidas()}
    assert {"E3-LRFD.est.e", "E3-LRFD.est.s",
            "E1-LRFD.sis.e", "E1-LRFD.sis.s"} <= incumplidas
    assert not [c for c in incumplidas if "-ASD." in c]
    con_aviso = {v.codigo for v in a01.con_aviso()}
    assert {"E3-ASD.sis.e", "E3-ASD.sis.s"} <= con_aviso
    v = next(x for x in a01.incumplidas() if x.codigo == "E3-LRFD.est.e")
    assert v.valor_obtenido > v.valor_admisible
    assert "ampliar la zapata" in v.paso.veredicto.explicacion


@pytest.mark.lento
def test_con_una_zapata_declarada_mas_ancha_el_marco_que_rige_cumple(tmp_path):
    """
    La puerta que T-7a dejo para eso: `cabezal_declarado.ancho_zapata_m` =
    3.00 m en los dos cabezales de A-01 (DE PRUEBA; con 2.40 m el de salida,
    de 3.3 m de altura de empuje, todavia no pasa el deslizamiento). Las
    doce filas del marco LRFD cumplen, estaticas y sismicas; lo que queda
    sin cumplir es del marco ASD bajo sismo, que informa y no detiene.
    """
    _, a01 = _correr_de_prueba(
        tmp_path, extra_a01={"cabezal_declarado": {"ancho_zapata_m": 3.00}})
    assert a01.cabezal.entrada.B == pytest.approx(3.00, abs=ABS_CERO)
    filas = [v for e in a01.cabezal.estabilidad for v in e.verificaciones]
    assert len(filas) == 24
    lrfd = [v for v in filas if "-LRFD." in v.codigo]
    assert len(lrfd) == 12
    assert all(v.estado is EstadoDeVerificacion.CUMPLE for v in lrfd)
    assert not [v for v in a01.incumplidas() if v.codigo.startswith("E")]
    que_informan = [v for v in filas
                    if v.estado is EstadoDeVerificacion.INDICADOR]
    assert que_informan and all("-ASD.sis." in v.codigo for v in que_informan)
    assert all(e.cumple for e in a01.cabezal.estabilidad)


@pytest.mark.lento
def test_el_entorno_de_cada_cabezal_sale_de_lo_que_las_fases_ya_resolvieron(
        tmp_path):
    """
    `datos_del_cabezal_del_punto` no decide nada otra vez: el relleno
    retenido llega a la coronacion menos el bordillo de las reglas de T-7a,
    el talud y el borde de la plataforma son los de 7.B, el freatico el de la
    columna y la hoya solo a la salida. E `integrar_estabilidad` suma las
    filas E a las CB del cabezal sin tocar la geometria.
    """
    _, a01 = _correr_de_prueba(tmp_path)
    entrada, salida = M9.datos_del_cabezal_del_punto(
        punto=a01.punto_de_calculo, cabezal=a01.cabezal,
        geometria=a01.geometria, socavacion=a01.socavacion)
    bordillo = ca.valor("predimensionamiento_cabezal")["bordillo_m"]
    for entorno, g in ((entrada, a01.cabezal.entrada),
                       (salida, a01.cabezal.salida)):
        assert entorno.geometria is g and entorno.extremo == g.extremo
        assert entorno.cota_relleno == pytest.approx(
            g.cota_coronacion - bordillo, abs=ABS_CERO)
        # H1: la COTA del freatico, desde el terreno del CRUCE (42.10 msnm).
        assert entorno.cota_freatico == pytest.approx(42.10 - 2.0,
                                                      abs=ABS_CERO)
        assert entorno.talud == pytest.approx(
            a01.geometria.longitud_calculada.talud, rel=REL_TRANSPORTE)
        assert entorno.cota_borde_plataforma > entorno.cota_relleno
        assert entorno.suelo is None
    assert entrada.cota_fondo_hoya is None
    sin_filas = [v for v in a01.cabezal.verificaciones
                 if not v.codigo.startswith("E")]
    desnudo = replace(a01.cabezal, verificaciones=tuple(sin_filas),
                      estabilidad=())
    integrado = M9.integrar_estabilidad(desnudo, a01.cabezal.estabilidad)
    assert integrado.estabilidad == a01.cabezal.estabilidad
    assert integrado.geometrias == a01.cabezal.geometrias
    assert len(integrado.verificaciones) == len(sin_filas) + 24


@pytest.mark.lento
def test_el_freatico_se_mide_bajo_el_terreno_del_cruce_y_moja_la_salida(
        tmp_path):
    """
    DORADO A MANO DE H1 (correcciones de T-7b), con el pie del cabezal
    DISTINTO del terreno del cruce. A-01: terreno del cruce 42.10 msnm,
    NF_profundidad_m = 1.40 (de prueba) -> agua a 42.10 - 1.40 = 40.70 msnm.
      entrada: pie 42.10, base 42.10 - 0.80 = 41.30 > 40.70  -> seca
      salida:  pie 41.30 (fondo del receptor), base 41.30 - 0.80 = 40.50
               -> 40.70 - 40.50 = 0.20 m de agua sobre la base.
    La FASE A medía 1.40 bajo el pie de cada cabezal y dejaba el agua de la
    salida a 41.30 - 1.40 = 39.90, bajo la zapata (el test que lo fijaba
    exigia `NF_profundidad_m == 1.4` en los dos entornos y se reescribio).
    Con el agua en el plano: la estatica de la salida pide el peso saturado
    del relleno, y la sismica no es evaluable (11.6.5.3, relleno saturado).
    Subpresion de la salida, con el agua igual delante y detras (drenado):
      U = 9.81·0.20·B = 1.962·B kN/m
    """
    _, a01 = _correr_de_prueba(tmp_path, NF="1.4")
    entrada, salida = M9.datos_del_cabezal_del_punto(
        punto=a01.punto_de_calculo, cabezal=a01.cabezal,
        geometria=a01.geometria, socavacion=a01.socavacion)
    assert entrada.cota_freatico == pytest.approx(40.70, abs=TOL_MM)
    assert salida.cota_freatico == pytest.approx(40.70, abs=TOL_MM)
    assert a01.cabezal.entrada.cota_desplante == pytest.approx(41.30,
                                                               abs=TOL_MM)
    assert a01.cabezal.salida.cota_desplante == pytest.approx(40.50,
                                                              abs=TOL_MM)
    # Sin el peso saturado, las dos condiciones de la salida se detienen en
    # el criterio de ensayo; la entrada, seca, se evalua en las dos.
    salida_bloqueada = [b for b in a01.bloqueos
                        if "estabilidad E1-E3" in b.etapa
                        and "salida" in b.etapa]
    assert len(salida_bloqueada) == 2
    assert {b.criterio for b in salida_bloqueada} == {
        "peso_especifico_saturado_relleno_kn_m3"}
    assert [e.condicion for e in a01.cabezal.estabilidad
            if e.extremo == "entrada"] == [EST, SIS]
    # Con el peso saturado declarado (de prueba): la estatica de la salida se
    # evalua con la subpresion del dorado, y la sismica no es evaluable.
    _, a01 = _correr_de_prueba(
        tmp_path, NF="1.4",
        declaraciones={"peso_especifico_saturado_relleno_kn_m3": 20.0})
    sis_s = next(b for b in a01.bloqueos if "estabilidad E1-E3" in b.etapa
                 and "salida" in b.etapa and "sismico" in b.etapa)
    assert sis_s.tipo is TipoDeBloqueo.METODO_NO_EVALUABLE
    assert "h_w = 0.200 m" in sis_s.mensaje
    e = next(x for x in a01.cabezal.estabilidad
             if x.extremo == "salida" and x.condicion is EST)
    B = a01.cabezal.salida.B
    assert _carga(e, "WA.u").V == pytest.approx(-1.962 * B, abs=TOL_MM)
    assert _carga(e, "WA.h").H == pytest.approx(9.81 * 0.2 ** 2 / 2,
                                                abs=TOL_MM)


@pytest.mark.lento
def test_V5_por_cota_de_afectacion_a_mano_y_puede_fallar(tmp_path):
    """
    H2: el metodo de COTA. A-01, Ø 0.90 m: cota del embalse = cota de
    entrada (42.10, el terreno: fondo de entrada adoptado) + HW de M4. Con
    la cota de afectacion de prueba (44.00) cumple; con 43.00 msnm -- por
    debajo de 42.10 + HW -- el Ø 0.90 m NO cumple V5 y el punto no sale con
    esa seccion.
    """
    _, a01 = _correr_de_prueba(tmp_path)
    v5 = next(v for v in a01.resultado.verificaciones if v.codigo == "V5")
    HW = a01.resultado.resultado_hidraulico.HW
    assert v5.valor_obtenido == pytest.approx(42.10 + HW, abs=TOL_MM)
    assert v5.valor_admisible == pytest.approx(44.00, abs=ABS_CERO)
    assert v5.estado is EstadoDeVerificacion.CUMPLE
    assert v5.paso.umbral.cita_id == "HDS5_3ED.2.2.5a#COTA_DE_DANO"
    assert "HDS5_3ED.2.2.5#NO_EXCEDER" in v5.paso.citas_textuales
    _, a01 = _correr_de_prueba(tmp_path, cota_afectacion=43.00)
    primera = a01.traza[0]
    v5 = next(v for v in primera.verificaciones if v.codigo == "V5")
    assert v5.estado is EstadoDeVerificacion.NO_CUMPLE
    assert v5.valor_obtenido > 43.00
    assert not (a01.dimensionado
                and a01.resultado.seccion.etiqueta() == "Ø 0.90 m")


# --- H3: V8 con el barril a presion, y solo sobre el candidato que cumple -

@pytest.mark.lento
@pytest.mark.parametrize("Q_ext, regimen, adoptada", [
    (1.30, "lamina libre", "Ø 0.90 m"),       # x1.11
    (1.40, "lamina libre", "Ø 0.90 m"),       # x1.20
    (1.50, "barril a presion", "Ø 0.90 m"),   # x1.29: antes «no evaluable»
    (1.75, "barril a presion", "Ø 0.90 m"),   # x1.50
    (2.30, "barril a presion", "Ø 1.05 m"),   # x1.97: Ø 0.90 desborda
])
def test_H3_el_barrido_del_auditor_sobre_A01(tmp_path, Q_ext, regimen,
                                             adoptada):
    """
    EL BARRIDO DEL AUDITOR (correcciones de T-7b, H3), Q_ext de 1.11 a 1.97
    veces el de diseño (1.167 m3/s) en A-01, con la plataforma desbordando a
    44.20 msnm (el borde de la entrada de 7.B). En la FASE A, desde 1.29·Q el
    punto quedaba «no evaluable» porque el caudal no cabe en lamina libre.
    Ahora:
      * hasta 1.20·Q el barril va en lamina libre y V8 cumple con Ø 0.90 m;
      * con 1.29·Q y 1.50·Q va A PRESION (control de entrada sumergido,
        q* = 4.50 y 5.25, contra el de salida a barril lleno: gobierna la
        entrada) y V8 cumple con Ø 0.90 m (cota del embalse 43.43 y 43.69);
      * con 1.97·Q el Ø 0.90 m DESBORDA (44.41 > 44.20 msnm): V8 no cumple,
        es un incumplimiento y no un bloqueo, y MD sube a Ø 1.05 m, que
        cumple (43.72). El diametro se mueve por un dato DECLARADO del
        evento extremo, no por el fixture.
    """
    _, a01 = _correr_de_prueba(
        tmp_path, extra_a01={"Q_evento_extremo_m3s": Q_ext})
    assert a01.dimensionado
    assert a01.resultado.seccion.etiqueta() == adoptada
    v8 = next(v for v in a01.resultado.verificaciones if v.codigo == "V8")
    assert v8.estado is EstadoDeVerificacion.CUMPLE
    hw = next(m for m in v8.paso.sustitucion if m.simbolo == "HW_ext")
    assert regimen in hw.procedencia
    assert "control que gobierna: entrada" in hw.procedencia
    assert not [b for b in a01.bloqueos
                if b.tipo is TipoDeBloqueo.METODO_NO_EVALUABLE]
    if adoptada != "Ø 0.90 m":
        primera = a01.traza[0]
        v8_090 = next(v for v in primera.verificaciones if v.codigo == "V8")
        assert v8_090.estado is EstadoDeVerificacion.NO_CUMPLE
        assert v8_090.valor_obtenido > v8_090.valor_admisible
        assert "seccion candidata" in v8_090.paso.veredicto.explicacion


@pytest.mark.lento
def test_H3_V8_no_se_evalua_sobre_un_candidato_que_ya_incumple(tmp_path):
    """
    El Ø 0.90 m que incumple V5 (cota de afectacion de prueba a 43.00 msnm)
    se rechaza SIN V8: un V8 que no pudiera evaluarse ya no enmascara el V5
    que de verdad lo descarta.
    """
    _, a01 = _correr_de_prueba(tmp_path, cota_afectacion=43.00)
    incumplen_v5 = 0
    for paso in a01.traza:
        codigos = [v.codigo for v in paso.verificaciones]
        v5 = next((v for v in paso.verificaciones if v.codigo == "V5"), None)
        if v5 is not None and v5.estado is EstadoDeVerificacion.NO_CUMPLE:
            incumplen_v5 += 1
            assert "V8" not in codigos
            assert "V9" in codigos      # lo de despues se sigue evaluando
    assert incumplen_v5 >= 1


def test_H3_la_carga_a_presion_reutiliza_las_piezas_de_M4():
    """
    `M4.hidraulica_a_presion` no escribe ninguna ecuacion: su HW es el mayor
    de `control_entrada` y `control_salida` (a barril lleno) con el mismo
    caudal por celda, y dice cual gobierno.
    """
    from src.modulos import M2_material as M2, M4_control as M4
    punto = _punto_real()
    material = M2.materiales_candidatos(punto)[0]
    seccion = modelos.SeccionCircular(0.90)
    r = M4.hidraulica_a_presion(seccion=seccion, Q=1.75, S=0.006, L=18.9,
                                TW=0.5, material=material)
    critico = M4.tirante_critico(1.75, seccion)
    entrada = M4.control_entrada(Q=1.75, seccion=seccion, S=0.006,
                                 hds5=material.hds5, critico=critico)
    salida = M4.control_salida(Q=1.75, seccion=seccion, S=0.006, L=18.9,
                               TW=0.5, n=material.n_para_capacidad,
                               critico=critico,
                               criterio_ke=M4.criterio_ke_de(material))
    assert r.HW == pytest.approx(max(entrada.HW, salida.HW), abs=ABS_CERO)
    assert r.regimen == modelos.REGIMEN_EVENTO_A_PRESION
    assert r.control_gobernante.value in r.nota


@pytest.mark.lento
def test_V5_por_cota_sin_el_dato_se_detiene_en_el_dato(tmp_path):
    _, a01 = _correr_de_prueba(tmp_path, cota_afectacion=None)
    assert not a01.dimensionado
    campos = {b.campo for b in a01.bloqueos}
    assert "cota_afectacion_aguas_arriba_msnm" in campos


@pytest.mark.lento
def test_el_V5_de_la_corrida_es_el_del_dorado(tmp_path):
    """
    HW de A-01 con Ø 0.90 m y la semilongitud de entrada de 7.B: los numeros
    del paso se recomputan a mano con lo que el paso imprime.
    """
    _, a01 = _correr_de_prueba(tmp_path, metodo_v5="embalse_a_nivel",
                               cota_afectacion=None, ancho=400.0)
    v5 = next(v for v in a01.resultado.verificaciones if v.codigo == "V5")
    m = {x.simbolo: x.valor for x in v5.paso.sustitucion}
    assert m["S_cauce"] == CP_T7B_V5["S_cauce"]
    assert m["HW"] == pytest.approx(
        a01.resultado.resultado_hidraulico.HW, rel=REL_TRANSPORTE)
    d = (m["L_boca"] + m["HW"] / 0.006) * CP_T7B_V5["cos_15"]
    assert v5.valor_obtenido == pytest.approx(d, abs=TOL_MM)
    assert 170.0 < v5.valor_obtenido < 185.0


@pytest.mark.lento
def test_con_un_derecho_de_via_estrecho_V5_no_cumple_y_el_punto_no_pasa_en_silencio(
        tmp_path):
    """
    PRECISIONES: V5 puede fallar. Con 300 m de faja (150 m al lado de aguas
    arriba) el Ø 0.90 m que la linea base adopta NO cumple V5: la traza lo
    dice, y el punto no sale dimensionado con esa seccion.
    """
    _, a01 = _correr_de_prueba(tmp_path, metodo_v5="embalse_a_nivel",
                               cota_afectacion=None, ancho=300.0)
    primera = a01.traza[0]
    v5 = next(v for v in primera.verificaciones if v.codigo == "V5")
    assert v5.estado is EstadoDeVerificacion.NO_CUMPLE
    assert v5.valor_admisible == pytest.approx(150.0, abs=ABS_CERO)
    assert v5.valor_obtenido > v5.valor_admisible
    assert not primera.aceptado
    assert not (a01.dimensionado
                and a01.resultado.seccion.etiqueta() == "Ø 0.90 m")


@pytest.mark.lento
def test_el_piso_del_DG2018_contrasta_el_ancho_declarado_y_no_lo_sustituye(
        tmp_path):
    """
    Un ancho declarado bajo el minimo de la Tabla 304.09 se usa tal cual y
    se AVISA; el calculo no lo cambia por el de la tabla.
    """
    ds.establecer_dato_dinamico(
        "clase_de_via", "carretera_primera_clase", "de prueba (T-7b)",
        "2026-11-13", origen="prueba")
    _, a01 = _correr_de_prueba(tmp_path, metodo_v5="embalse_a_nivel",
                               cota_afectacion=None, ancho=20.0)
    v5 = next(v for v in a01.traza[0].verificaciones if v.codigo == "V5")
    # Se usa el declarado (20/2 = 10 m), no el de la tabla (25/2).
    assert v5.valor_admisible == pytest.approx(10.0, abs=ABS_CERO)
    assert v5.estado is EstadoDeVerificacion.NO_CUMPLE
    avisos = [a for a in a01.avisos() if a.startswith("Derecho de via")]
    assert any("por debajo del minimo" in a and "25.00 m" in a
               and "no se sustituye" in a for a in avisos)
    # Y el caso del num. 304.07.02: 5.00 m del borde de la obra de drenaje.
    assert any("5.00 m" in a and "304.07.02" in a for a in avisos)


@pytest.mark.lento
def test_sin_el_freatico_la_estabilidad_bloquea_el_cabezal_y_no_la_corrida(
        tmp_path):
    """
    La columna NF_profundidad_m vacia (el fixture tal cual): la geometria del
    cabezal sale, la estabilidad queda como `Bloqueo` de dato faltante en
    cada extremo y condicion, y la corrida termina.
    """
    informe, a01 = _correr_de_prueba(tmp_path, NF="")
    assert a01.dimensionado and a01.cabezal is not None
    assert a01.cabezal.estabilidad == ()
    bloqueos = [b for b in a01.bloqueos if "estabilidad E1-E3" in b.etapa]
    assert len(bloqueos) == 4
    assert all(b.tipo is TipoDeBloqueo.DATO_FALTANTE for b in bloqueos)
    assert all("NF_profundidad_m" in b.mensaje for b in bloqueos)


@pytest.mark.lento
def test_sin_reduccion_del_coeficiente_sismico_la_cuna_da_cifra(tmp_path):
    """
    REESCRITO DECLARANDOLO (correcciones de T-7b, H4). Se llamaba «sin
    reduccion del coeficiente sismico el sismo no es evaluable»: con k_h =
    0.50 de archivo, Mononobe-Okabe con la pendiente equivalente queda fuera
    de su dominio (phi = 34 < i + 26.6), y la sismica de cada cabezal era un
    bloqueo. Con la cuña de tanteo de archivo -- lo que C11.6.5.3 admite
    cuando Mononobe-Okabe no es adecuado -- el relleno que se quiebra en la
    plataforma tiene cuña critica, y la sismica DA CIFRA (el oraculo del
    auditor sobre la geometria de la FASE A: 59.7 y 98.2 kN/m). Con la zapata
    de la regla de T-7a esa cifra no cumple: lo dice la fila, no un bloqueo.
    Mononobe-Okabe queda como contraste «no evaluable».
    """
    _, a01 = _correr_de_prueba(
        tmp_path, declaraciones={"factor_muro_eleccion": "sin_reduccion"})
    condiciones = [(e.extremo, e.condicion) for e in a01.cabezal.estabilidad]
    assert condiciones == [("entrada", EST), ("entrada", SIS),
                           ("salida", EST), ("salida", SIS)]
    assert not [b for b in a01.bloqueos if "estabilidad E1-E3" in b.etapa]
    for e in a01.cabezal.estabilidad:
        if e.condicion is SIS:
            assert e.k_h == pytest.approx(0.50, abs=TOL_FINA)
            assert math.isfinite(e.K_AE) and e.K_AE > 1.0
            assert e.metodo_empuje == M9.METODO_EMPUJE_CUNA
            assert e.K_AE_contraste is None        # M-O fuera de su dominio
    incumplidas = {v.codigo for v in a01.incumplidas()}
    assert {"E2-LRFD.sis.e", "E3-LRFD.sis.e"} <= incumplidas


@pytest.mark.lento
def test_la_salida_de_la_CLI_y_el_JSON_llevan_la_estabilidad(tmp_path):
    informe, a01 = _correr_de_prueba(tmp_path)
    volcado = cli.informe_json(informe)
    punto = next(p for p in volcado["puntos"] if p["id"] == "A-01")
    est = punto["cabezal"]["estabilidad"]
    assert len(est) == 4
    primero = est[0]
    assert {"cargas", "combinaciones", "verificaciones", "pendientes",
            "solicitaciones"} <= set(primero)
    assert {c["codigo"] for c in primero["cargas"]} >= {
        "DC.pantalla", "EV.talon", "EH.h", "EH.v", "LS.h"}
    json.dumps(volcado)                       # serializable, sin inf ni NaN
    texto = cli.volcar(informe)
    assert "E1-LRFD.est.e" in texto and "E3-ASD.sis.s" in texto


@pytest.mark.lento
def test_la_memoria_del_punto_imprime_la_estabilidad_de_cada_cabezal(tmp_path):
    """
    INF-4.5: la memoria HTML del punto lleva, por cabezal y por condicion,
    la tabla de cargas con sus brazos, las combinaciones de los dos marcos y
    las filas E1 a E3 con su paso (formula, sustitucion, umbral, veredicto),
    mas E4 y E5 como diferidas. Y exporta entera, con su contexto de corrida.
    """
    from src.modulos import M11_reporte as M11
    informe, a01 = _correr_de_prueba(tmp_path)
    html = M11.memoria_de_punto(a01)
    for pieza in ("Estabilidad del cabezal de entrada",
                  "Estabilidad del cabezal de salida",
                  "DC.pantalla", "EH.v", "EQ.PIR.suelo",
                  "Resistencia I (minimos)", "Evento Extremo I",
                  "Servicio (volteo y deslizamiento)",
                  "E1 (LRFD), capacidad portante", "E2 (LRFD), excentricidad",
                  "E3 (LRFD), deslizamiento", "E4 y E5",
                  "diferidas al expediente"):
        assert pieza in html, pieza
    # Las filas del marco que no rige y fallan van como aviso, no como fallo.
    assert "Este marco NO rige" in html
    destino = tmp_path / "memoria.html"
    M11.exportar_html(informe, destino)
    assert "E3-LRFD.est.e" in destino.read_text(encoding="utf-8") \
        or "E3 (LRFD), deslizamiento" in destino.read_text(encoding="utf-8")


@pytest.mark.lento
def test_a_nivel_de_perfil_la_Fase_9_sigue_diferida(tmp_path):
    """
    El alcance de perfil sigue difiriendo la Fase 9: ni geometria ni
    estabilidad del cabezal. V5 y V8, en cambio, hacen lo que
    `_verificador_perfil` decia desde antes de T-7b que harian «si algun dia
    su logica existe»: declarados el metodo y los datos, devuelven su fila y
    entran a la tabla; sin declarar, se difieren como siempre (el otro test).
    """
    _, a01 = _correr_de_prueba(tmp_path, alcance=servicio.ALCANCE_PERFIL)
    assert a01.dimensionado
    assert a01.resultado.seccion.etiqueta() == "Ø 0.90 m"
    assert a01.cabezal is None
    codigos = {v.codigo: v.estado for v in a01.resultado.verificaciones}
    assert codigos["V5"] is EstadoDeVerificacion.CUMPLE
    assert codigos["V8"] is EstadoDeVerificacion.CUMPLE


@pytest.mark.lento
def test_sin_declarar_nada_el_fixture_se_detiene_donde_se_detenia():
    """
    REGLA DURA: sin declarar nada, ningun resultado cambia. A expediente los
    puntos de las Familias A y B siguen detenidos en el criterio de V5
    ('remanso_derecho_via'), como en `250c972`, y ninguno llega a la Fase 9.
    """
    externos = servicio.cargar_datos_externos(
        RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json",
        {"luz_m": 3.0})
    informe = servicio.correr(CSV_EJEMPLO, externos,
                              alcance=servicio.ALCANCE_EXPEDIENTE)
    for p in informe.puntos:
        assert not p.dimensionado, p.punto.id
        if p.punto.familia.value in ("A", "B"):
            criterios = {b.criterio for b in p.bloqueos}
            assert "remanso_derecho_via" in criterios, p.punto.id
        assert p.cabezal is None


# ===========================================================================
# 16. LOS DOCUMENTOS
# ===========================================================================

def test_la_hoja_de_ruta_escribe_la_decision_de_marco():
    """
    Punto 1 del encargo: la decision queda escrita en la hoja de ruta, y la
    E.050 deja de figurar como [N] del cabezal (defecto que T7A-08 dejo
    anotado para T-7b).
    """
    texto = HOJA_DE_RUTA.read_text(encoding="utf-8")
    assert "marco_estabilidad_cabezal" in texto
    assert "T-7b" in texto
    assert "lrfd_rige_asd_informa" in texto


def test_el_contrato_de_entradas_nombra_lo_que_T7b_pide():
    texto = CONTRATO.read_text(encoding="utf-8")
    for clave in ("ancho_derecho_via_m", "Q_evento_extremo_m3s",
                  "TW_evento_extremo_m", "cota_afectacion_aguas_arriba_msnm",
                  "regimen_cabezal", "suelo_fundacion",
                  "NF_profundidad_m", "phi_relleno_trasdos",
                  "c_phi_fundacion", "remanso_derecho_via",
                  "umbral_no_colapso_evento_extremo"):
        assert clave in texto, clave


# Correcciones de T-7b: dos fichas mas, T7B-13 (la medida del cierre) y
# T7B-14 (el regimen del cabezal para T-7c).
@pytest.mark.parametrize("ficha", [f"T7B-{n:02d}" for n in range(1, 15)])
def test_las_fichas_de_T7b_existen(ficha):
    assert f"\n## {ficha} · " in DECISIONES.read_text(encoding="utf-8")


def test_ningun_literal_de_T7b_quedo_sin_declarar():
    """Las constantes del bloque T-7b viven en constantes_normativas.py."""
    fuente = Path(cn.__file__).read_text(encoding="utf-8")
    assert "# --- T-7b ---" in fuente
    for nombre in ("PHI_ZAPATAS_T10_5_5_2_2_1", "PHI_MUROS_T11_5_7_1",
                   "PHI_EVENTO_EXTREMO_11_5_8",
                   "NUMERAL_EXCENTRICIDAD_ESTATICA_AASHTO",
                   "FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1",
                   "CW_NIVEL_FREATICO_T10_6_3_1_2A_2",
                   "TALUD_QUEBRADO_DISTANCIA_VECES_H"):
        assert fuente.index(nombre) > fuente.index("# --- T-7b ---"), nombre
