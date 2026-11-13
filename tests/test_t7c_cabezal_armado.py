"""
tests/test_t7c_cabezal_armado.py
================================
Aceptacion de T-7c: el ARMADO de cada cabezal (o la verificacion de su
alternativa en concreto ciclopeo), que cierra INF-4.6, la ficha EXT-7-01 y el
`NotImplementedError` de `M9.diseno_flexion_corte`.

Que fija, en el orden del archivo:

  1. los numeros de las dos fuentes, contra su pagina (marca `pdf`);
  2. las conversiones a SI de las constantes de AASHTO, contra la aritmetica
     y contra los tres ejemplos que el comentario C5.10.6 publica;
  3. las formulas de seccion, con los dorados A MANO de
     `tests/fixtures/casos_patron.py` (`CP_T7C_ARMADO`): flexion y cortante
     por AASHTO LRFD Seccion 5, y el contraste de E.060;
  4. el empuje en reposo: que se escala y que no;
  5. las solicitaciones de resistencia de cada seccion (pantalla, punta con
     presion de contacto lineal, talon con el peso entero, Evento Extremo);
  6. `diseno_flexion_corte`: que ya no lanza `NotImplementedError`, que
     puede fallar, y donde se detiene con «metodo no evaluable»;
  7. los minimos, el recubrimiento sin dato y el regimen de cortante de
     E.060 (los tres criterios que estaban vacios);
  8. el armado del cabezal entero, su tabla y sus avisos;
  9. la alternativa ciclopea;
 10. de punta a punta por `servicio.correr`, con los datos DE PRUEBA
     rotulados de T-7b, y la CLI.

Los dorados estan calculados a mano, con la aritmetica escrita, y son
independientes de las formulas cerradas del modulo: la flexion se despeja por
la ecuacion de segundo grado y el dorado la escribe paso a paso; el cortante
se calcula en las unidades de la fuente (kip, ksi, pulgada) y se convierte al
final, mientras el modulo lo hace con la constante en SI.

NO SE ESCRIBIO EN ROJO CON `xfail(strict=True)`: el codigo y este archivo se
escribieron en la misma sesion. El rojo se MIDIO copiando este archivo y el
fixture a un arbol exportado de `451a10a`, y se declara en el informe de la
FASE A (ficha T7C-08 de `docs/decisiones_diferidas.md`).
"""

import ast
import json
import math
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

import cli
from src import constantes_fisicas as cf
from src import constantes_normativas as cn
from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src import modelos
from src import servicio
from src.modelos import (ELEMENTO_ALEROS, ELEMENTO_PANTALLA, ELEMENTO_ZAPATA,
                         MARCO_E060, MARCO_LRFD, REGIMEN_RESISTENCIA_CEDENTE,
                         REGIMEN_RESISTENCIA_K0, SECCION_ALERO,
                         SECCION_PANTALLA, SECCION_PUNTA, SECCION_TALON,
                         Aleros, ArmadoDelCabezal, CondicionAnalisis,
                         CriterioPendienteError, DatoFaltanteError,
                         DatoInvalidoError, EntornoDelCabezal, ErrorProyecto,
                         EstadoDeVerificacion, GeometriaCabezal,
                         LimiteNumericoError, MetodoNoEvaluableError,
                         SolicitacionDeArmado, TipoDeBloqueo)
from src.modulos import M9_cabezal as M9
from src.normativa import fuentes
from src.normativa.registro import construir
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tests.apoyo.criterios import con_valor, sin_valor
from tests.fixtures.casos_patron import (CP_T7B_ESTABILIDAD, CP_T7C_ARMADO,
                                         CP_T7C_BASE_SERVICIO,
                                         CP_T7C_CICLOPEO, CP_T7C_EC_11_32,
                                         CP_T7C_TEMPERATURA_PUBLICADA)

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
DECISIONES = RAIZ / "docs" / "decisiones_diferidas.md"

EST = CondicionAnalisis.ESTATICO
SIS = CondicionAnalisis.SISMICO
CPB = CP_T7B_ESTABILIDAD
CP = CP_T7C_ARMADO
# Las tolerancias las DECLARA el caso patron: son las de la escritura del
# dorado. ABS_CERO y REL_TRANSPORTE, para lo que solo se transporta.
TOL = CP["tolerancia"]              # cifras escritas a 3-4 decimales
TOL_AS = CP["tolerancia_As"]        # areas escritas a un decimal, mm2/m
REL = CP["tolerancia_rel"]
TOL_CM = CP["tolerancia_cm"]        # cifras escritas a dos decimales
TOL_MM = CP["tolerancia_mm"]        # cifras escritas a tres decimales
TOL_FINA = CP["tolerancia_fina"]    # deformaciones y cocientes
TOL_K = CP["tolerancia_K"]          # coeficientes y constantes convertidas
TOL_EXACTA = CP["tolerancia_exacta"]        # una o dos operaciones exactas
REL_CALCULO = CP["tolerancia_calculo_rel"]  # la misma cuenta por otra via
REL_UNIDADES = CP["tolerancia_unidades_rel"]

NUEVOS_T7C = (
    "regimen_resistencia_elementos_cabezal", "fc_cabezal_mpa",
    "acero_refuerzo_cabezal", "catalogo_barras_refuerzo_cabezal",
    "regla_minimos_constructivos_cabezal",
    "criterio_traccion_cabezal_ciclopeo", "concreto_ciclopeo_cabezal")
ANTES_VACIOS = (
    "cortante_alto_muro_e060_art_11_10_10_2",
    "regimen_cortante_muro_e060_art_11_10_2",
    "cuantia_vertical_cortante_alto_e060_art_11_10_10_3")


# ---------------------------------------------------------------------------
# Apoyo: el muro de tanteo de T-7b, ahora con tipo y longitud
# ---------------------------------------------------------------------------

def _geometria(**cambios) -> GeometriaCabezal:
    base = dict(CPB["geometria"], cota_desplante=100.0, cota_coronacion=102.55,
                id_punto="T-00", extremo="entrada", tipo=M9.TIPO_VOLADIZO,
                longitud=3.0)
    base.update(cambios)
    return GeometriaCabezal(**base)


def _entorno(**cambios) -> EntornoDelCabezal:
    g = cambios.pop("geometria", None) or _geometria()
    h = cambios.pop("h", CPB["h"])
    base = dict(id_punto="T-00", extremo=g.extremo, geometria=g,
                cota_relleno=100.0 + h, cota_borde_plataforma=100.0 + h,
                origen_cota_borde="de prueba", talud=1.5, esviaje_grados=0.0,
                cota_freatico=100.0 + g.D_f - CPB["NF"],
                cota_pie=100.0 + g.D_f, suelo=dict(CPB["suelo"]))
    base.update(cambios)
    return EntornoDelCabezal(**base)


def _declarar_sitio():
    """Los dos [S] de la sobrecarga viva: muro paralelo, borde a 1.60 m."""
    ds.establecer_dato_dinamico(
        "orientacion_muro_respecto_al_trafico", "paralelo_al_trafico",
        "de prueba (T-7c)", "2026-11-13", origen="prueba")
    ds.establecer_dato_dinamico(
        "distancia_borde_calzada_al_trasdos_m", 1.6,
        "de prueba (T-7c)", "2026-11-13", origen="prueba")


@pytest.fixture
def tanteo(monkeypatch):
    """
    Las declaraciones DE PRUEBA del muro de tanteo de T-7b, por la puerta
    real, y el coeficiente sismico IMPUESTO (k_h = 0.25 sin reduccion: k_h0
    = k_h). El conftest repone el estado al salir.
    """
    ca.establecer_valor_dinamico("phi_relleno_trasdos", CPB["phi_relleno"])
    ca.establecer_valor_dinamico("peso_especifico_relleno_kn_m3",
                                 CPB["gamma_relleno"])
    ca.establecer_valor_dinamico("drenaje_trasdos", "drenado")
    _sin_datos_de_exposicion()
    _declarar_sitio()
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h=CPB["sismico"]["k_h"], k_v=0.0, k_h0=CPB["sismico"]["k_h"]))
    return _entorno()


def _sin_datos_de_exposicion():
    """
    Retira las dos declaraciones DE PRUEBA que el `conftest` de la raiz pone
    para toda la suite (categoria del acero «A» y un analisis quimico con
    cloruros): el expediente NO las tiene, y el dorado se calcula como el
    programa corre hoy, con la cota de recubrimiento por falta de dato. El
    conftest repone el estado al salir de cada test.
    """
    ca.quitar_valor_dinamico("categoria_refuerzo_aashto")
    ca.quitar_valor_dinamico("exposicion_quimica_ems")


def _v(armado, codigo):
    return next(v for v in armado.verificaciones if v.codigo == codigo)


def _sol(M=30.0, V=40.0, phi=0.9, condicion=EST, nombre="de prueba"):
    return SolicitacionDeArmado(
        combinacion=nombre, condicion=condicion, M_u=M, V_u=V,
        phi_flexion=phi, phi_corte=phi, M_u_cedente=M, V_u_cedente=V)


# ===========================================================================
# 1. LOS NUMEROS DE LAS DOS FUENTES, CONTRA SU PAGINA
# ===========================================================================

@pytest.mark.pdf
@pytest.mark.parametrize("fuente_id, pagina_pdf, fragmentos", [
    # 5.5.4.2: factores de resistencia de flexion y de cortante.
    ("AASHTO_LRFD_9", 388, ("Resistance factor φ shall be taken as:",
                            "For tension-controlled reinforced concrete "
                            "sections as specified in Article 5.6.2.1: "
                            "normal weight concrete",)),
    ("AASHTO_LRFD_9", 389, ("For shear and torsion in reinforced concrete "
                            "sections: normal weight concrete",)),
    # 1.3.2.1: el factor de resistencia del evento extremo.
    ("AASHTO_LRFD_9", 18, ("For service and extreme event limit states, "
                           "resistance factors shall be taken as 1.0",)),
    # 5.6.2.1 y 5.6.2.2: limite de traccion y bloque rectangular.
    ("AASHTO_LRFD_9", 394, ("shall be taken as 0.005 for nonprestressed "
                            "reinforcement",)),
    ("AASHTO_LRFD_9", 395, ("shall be taken as 0.85 for design compressive "
                            "strengths of concrete not exceeding 10.0 ksi",
                            "shall be reduced at a rate of 0.05 for each 1.0 "
                            "ksi of strength in excess of 4.0 ksi",
                            "shall not be taken to be less than 0.65")),
    # 5.6.3.3: el acero minimo de flexion y sus factores.
    ("AASHTO_LRFD_9", 401, ("1.33 times the factored moment required by the "
                            "applicable strength load combination",
                            "1.6 for all other concrete structures")),
    ("AASHTO_LRFD_9", 402, ("0.67 for AASHTO M 31 (ASTM A615), Grade 60 "
                            "reinforcement",
                            "0.75 for ASTM A706, Grade 60 reinforcement")),
    # 5.7.3.4.1: el procedimiento simplificado y sus condiciones.
    ("AASHTO_LRFD_9", 429, ("is less than 3dv with or without transverse "
                            "reinforcement",
                            "having an overall depth of less than 16.0 in., "
                            "the following values may be used:",
                            "β = 2.0", "θ = 45 degrees")),
    # 5.7.2.8: el peralte efectivo de cortante.
    ("AASHTO_LRFD_9", 424, ("need not be taken to be less than the greater "
                            "of 0.9de or 0.72h",)),
    # 5.10.6: retraccion y temperatura, y su espaciamiento.
    ("AASHTO_LRFD_9", 533, ("the product of 0.0018, 60.0 ksi, and 12.0 "
                            "in./ft",
                            "a 30.0 ft high × 1.0 ft thick wall section "
                            "requires 0.126 in.2/ft")),
    ("AASHTO_LRFD_9", 534, ("12.0 in. for walls and footings greater than "
                            "18.0 in. thick",
                            "3.0 times the component thickness but not less "
                            "than 18.0 in.")),
    # 5.10.3.2: espaciamiento maximo en muros y losas.
    ("AASHTO_LRFD_9", 531, ("1.5 times the thickness of the member; or",
                            "18.0 in.")),
    # 10.6.5 y 11.6.1.2: la presion lineal y el talon con el peso entero.
    ("AASHTO_LRFD_9", 1375, ("a triangular or trapezoidal contact stress "
                             "distribution based on factored loads shall be "
                             "used",)),
    ("AASHTO_LRFD_9", 1489, ("loaded with the full weight of the "
                             "superimposed material, unless a more exact "
                             "method is used",)),
    # E.060: combinaciones, factores de reduccion, cortante y ciclopeo.
    ("E060", 65, ("U = 1,4 CM + 1,7 CV + 1,7 CE", "U = 0,9 CM + 1,7 CE")),
    ("E060", 66, ("Flexión sin carga axial", "Cortante y torsión")),
    ("E060", 73, ("0,0018",)),
    ("E060", 78, ("no sea menor de 0,0012",)),
    ("E060", 104, ("no debe ser menor que 0,0025",)),
    ("E060", 195, ("no mayor a 10 MPa",)),
    ("E060", 191, ("deberá tomarse 50 mm menor que la dimensión real",)),
])
def test_los_numeros_de_T7c_estan_en_la_pagina_que_se_cita(
        fuente_id, pagina_pdf, fragmentos):
    from src.normativa.extraccion import texto_de_pagina
    ruta = fuentes.ruta_pdf(fuentes.FUENTES[fuente_id])
    if not ruta.exists():
        pytest.skip(f"el PDF de {fuente_id} no esta enlazado")
    texto = " ".join(texto_de_pagina(ruta, pagina_pdf).split())
    for fragmento in fragmentos:
        assert fragmento in texto, (fuente_id, pagina_pdf, fragmento)


def test_las_citas_de_T7c_existen_y_llevan_su_caracter():
    """
    Lo que el armado atribuye a cada fuente, por su caracter: el reposo es
    una RECOMENDACION del comentario, el simplificado un PERMISO, y la
    presion lineal y el talon con el peso entero, EXIGENCIAS.
    """
    reg = construir()
    esperado = {
        "AASHTO_LRFD_9.C3.11.1#REPOSO": "recomendacion",
        "AASHTO_LRFD_9.C11.6.5.4#H_MEDIOS": "recomendacion",
        "AASHTO_LRFD_9.C3.11.5.2#ACTIVO": "definicion",
        "AASHTO_LRFD_9.5.7.3.4.1#SIMPLIFICADO": "permiso",
        "AASHTO_LRFD_9.10.6.5#LINEAL": "exigencia",
        "AASHTO_LRFD_9.11.6.1.2#TALON": "exigencia",
        "AASHTO_LRFD_9.5.6.3.3#MINIMO": "exigencia",
        "AASHTO_LRFD_9.1.3.2.1#EXTREMO": "exigencia",
        "E060.22.6.3#TERCIO": "exigencia",
    }
    for cita_id, caracter in esperado.items():
        assert reg.cita(cita_id).caracter.value == caracter, cita_id


def test_las_lecturas_del_proyecto_van_como_interpretacion_y_no_como_cita():
    """
    Tres cosas que NINGUNA fuente dice y el proyecto hace: que la pantalla
    del cabezal no cede, que se le aplica la excepcion de las losas en el
    cortante, y que E.060 se usa por analogia. Cada una lleva lo que juega
    en contra.
    """
    reg = construir()
    for cita_id in ("AASHTO_LRFD_9.C3.11.1#REPOSO",
                    "AASHTO_LRFD_9.5.7.2.3#TRANSVERSAL",
                    "E060.9.2.5#EMPUJE"):
        lectura = reg.cita(cita_id).interpretacion
        assert lectura is not None and lectura.en_contra, cita_id


# ===========================================================================
# 2. LAS CONSTANTES: CONVERSION A SI EN LA CONSTANTE, NO EN LA LLAMADA
# ===========================================================================

def test_las_constantes_de_AASHTO_se_convierten_a_SI_una_sola_vez():
    """
    Las ecuaciones de la fuente estan en ksi y pulgadas; las constantes
    dimensionales llevan sufijo `_SI` o la unidad en el nombre, y valen lo
    que la conversion a mano da.
    """
    ksi = 6.894757293168361         # MPa por ksi
    assert cf.KSI_EN_MPA == pytest.approx(ksi, rel=REL_TRANSPORTE)
    # 0.0316·sqrt(ksi) = 0.0316·2.625787 = 0.082975
    assert cn.VC_COEFICIENTE_AASHTO_SI == pytest.approx(0.082975, abs=TOL_K)
    # 0.24·sqrt(ksi) = 0.630189
    assert cn.MODULO_ROTURA_AASHTO_SI == pytest.approx(0.630189, abs=TOL_K)
    # 16.0 in = 0.4064 m; 18.0 in = 0.4572 m; 12.0 in = 0.3048 m
    assert cn.PERALTE_MAX_SIMPLIFICADO_AASHTO_SI == pytest.approx(0.4064, abs=TOL_EXACTA)
    assert cn.ESPACIAMIENTO_MAX_ABSOLUTO_AASHTO_M == pytest.approx(
        0.4572, abs=TOL_EXACTA)
    assert cn.TEMPERATURA_S_MAX_GRUESO_M == pytest.approx(0.3048, abs=TOL_EXACTA)
    # 1.30 kip/(in·ft) = 1.30·4448.2216/(25.4·304.8) = 0.746932 N/mm2
    assert cn.TEMPERATURA_COEFICIENTE_AASHTO_SI == pytest.approx(
        1.30 * 4448.2216152605 / (25.4 * 304.8), rel=REL_TRANSPORTE)
    assert cn.TEMPERATURA_COEFICIENTE_AASHTO_SI == pytest.approx(0.746932,
                                                                 abs=TOL_K)
    # 0.11 y 0.60 in2/ft = 232.83 y 1270.0 mm2/m
    assert cn.TEMPERATURA_AS_MIN_AASHTO_SI == pytest.approx(232.83, abs=TOL_CM)
    assert cn.TEMPERATURA_AS_MAX_AASHTO_SI == pytest.approx(1270.0, abs=TOL_CM)
    # 4.0 ksi = 27.58 MPa; 10.0 ksi = 68.95 MPa; 75.0 ksi = 517.1 MPa
    assert cn.FC_MAX_BETA_1_MPA == pytest.approx(27.579, abs=TOL_MM)
    assert cn.FC_MAX_ALFA_1_MPA == pytest.approx(68.948, abs=TOL_MM)
    assert cn.FY_MAX_EPSILON_TL_MPA == pytest.approx(517.107, abs=TOL_MM)


def test_los_factores_de_resistencia_son_los_de_cada_marco_y_no_se_mezclan():
    assert cn.PHI_FLEXION_AASHTO == pytest.approx(0.90, abs=ABS_CERO)
    assert cn.PHI_CORTE_AASHTO == pytest.approx(0.90, abs=ABS_CERO)
    assert cn.PHI_EVENTO_EXTREMO_AASHTO == pytest.approx(1.0, abs=ABS_CERO)
    assert cn.PHI_FLEXION_E060 == pytest.approx(0.90, abs=ABS_CERO)
    assert cn.PHI_CORTE_E060 == pytest.approx(0.85, abs=ABS_CERO)
    assert cn.PHI_CICLOPEO_E060 == pytest.approx(0.5, abs=ABS_CERO)
    for constante, impreso in ((cn.E060_FACTOR_CM, 1.4),
                               (cn.E060_FACTOR_CV, 1.7),
                               (cn.E060_FACTOR_CE, 1.7),
                               (cn.E060_FACTOR_CM_MINIMO, 0.9)):
        assert constante == pytest.approx(impreso, rel=REL_TRANSPORTE)
    # El criterio del procedimiento entrega los de AASHTO, no los de E.060.
    proc = ca.valor("procedimiento_flexion_corte_aashto_sec5")
    assert proc["phi_corte"] == pytest.approx(0.90, abs=ABS_CERO)
    assert proc["phi_evento_extremo"] == pytest.approx(1.0, abs=ABS_CERO)
    assert proc["beta_simplificado"] == pytest.approx(2.0, abs=ABS_CERO)


@pytest.mark.parametrize("ancho, espesor, publicado",
                         CP_T7C_TEMPERATURA_PUBLICADA["casos"])
def test_el_acero_de_temperatura_reproduce_los_ejemplos_del_comentario(
        ancho, espesor, publicado):
    """
    ORACULO PUBLICADO: los tres ejemplos de C5.10.6 (pag. impresa 5-174), en
    in2/ft con fy = 60 ksi. El modulo trabaja en m, MPa y mm2/m.
    """
    por_pulg2_pie = 645.16 / 0.3048           # mm2/m por in2/ft
    As = M9.acero_de_temperatura_aashto(
        ancho=ancho, espesor=espesor,
        fy=CP_T7C_TEMPERATURA_PUBLICADA["fy_mpa"])
    assert As / por_pulg2_pie == pytest.approx(
        publicado, abs=CP_T7C_TEMPERATURA_PUBLICADA["tolerancia_in2_ft"])


def test_el_acero_de_temperatura_tiene_piso_y_techo():
    """0.11 <= A_s <= 0.60 in2/ft (ec. 5.10.6-2)."""
    delgado = M9.acero_de_temperatura_aashto(ancho=1.0, espesor=0.10, fy=420.0)
    macizo = M9.acero_de_temperatura_aashto(ancho=8.0, espesor=4.0, fy=420.0)
    assert delgado == pytest.approx(cn.TEMPERATURA_AS_MIN_AASHTO_SI, rel=REL_TRANSPORTE)
    assert macizo == pytest.approx(cn.TEMPERATURA_AS_MAX_AASHTO_SI, rel=REL_TRANSPORTE)


# ===========================================================================
# 3. LAS FORMULAS DE SECCION, CON SUS DORADOS A MANO
# ===========================================================================

def test_dorado_de_flexion_el_acero_que_pide_el_momento():
    """Punto 3 del dorado: R = 0.0987429 -> A_s = 435.3 mm2/m."""
    p = CP["pantalla"]
    As = M9.acero_por_flexion(M_u=p["reposo"]["M_u"], d=p["d_m"], fc=21.0,
                              fy=420.0, phi=0.9)
    assert As == pytest.approx(p["As_resistencia"], abs=TOL_AS)


def test_dorado_de_flexion_la_resistencia_con_la_barra_propuesta():
    """a = 15.1765 mm, M_n = 52.7230 kN·m/m, epsilon_t = 0.030976."""
    p = CP["pantalla"]
    r = M9.resistencia_a_flexion(As=p["barra"][2], d=p["d_m"], fc=21.0,
                                 fy=420.0)
    assert r["a"] * 1000 == pytest.approx(p["a_mm"], abs=TOL_MM)
    assert r["M_n"] == pytest.approx(p["M_n"], abs=TOL)
    M_r = cn.PHI_FLEXION_AASHTO * r["M_n"]
    assert M_r == pytest.approx(p["M_r"], abs=TOL)
    assert r["epsilon_t"] == pytest.approx(p["epsilon_t"], abs=TOL_FINA)


def test_la_flexion_ida_y_vuelta_cierra():
    """El acero que pide M_u, puesto en la seccion, resiste exactamente M_u."""
    for M_u in (5.0, 32.431104, 80.0):
        As = M9.acero_por_flexion(M_u=M_u, d=0.25, fc=21.0, fy=420.0, phi=0.9)
        r = M9.resistencia_a_flexion(As=As, d=0.25, fc=21.0, fy=420.0)
        M_r = cn.PHI_FLEXION_AASHTO * r["M_n"]
        assert M_r == pytest.approx(M_u, rel=REL_CALCULO)


def test_el_acero_crece_con_el_momento_y_baja_con_el_peralte():
    a1 = M9.acero_por_flexion(M_u=20.0, d=0.20, fc=21.0, fy=420.0, phi=0.9)
    a2 = M9.acero_por_flexion(M_u=40.0, d=0.20, fc=21.0, fy=420.0, phi=0.9)
    a3 = M9.acero_por_flexion(M_u=40.0, d=0.30, fc=21.0, fy=420.0, phi=0.9)
    assert a2 > 2 * a1 > 0           # mas que proporcional: el brazo baja
    assert a3 < a2
    # y con phi = 1.0 (Evento Extremo) pide menos que con 0.90
    assert M9.acero_por_flexion(M_u=40.0, d=0.20, fc=21.0, fy=420.0,
                                phi=1.0) < a2


def test_una_seccion_que_no_alcanza_no_devuelve_un_acero_inventado():
    """
    Con R >= 1 el bloque de compresiones no equilibra el momento con ningun
    acero: la funcion devuelve None y no un numero.
    """
    # R = 1  <=>  M_u = phi·0.85·f'c·b·d²/2 = 0.9·0.85·21000·0.04/2 = 321.3
    assert M9.acero_por_flexion(M_u=321.3 * 1.001, d=0.20, fc=21.0, fy=420.0,
                                phi=0.9) is None
    assert M9.acero_por_flexion(M_u=321.3 * 0.999, d=0.20, fc=21.0, fy=420.0,
                                phi=0.9) is not None
    assert M9.acero_por_flexion(M_u=0.0, d=0.20, fc=21.0, fy=420.0,
                                phi=0.9) == pytest.approx(0.0, abs=ABS_CERO)


@pytest.mark.parametrize("campo, valor", [
    ("d", 0.0), ("d", -0.1), ("d", float("nan")), ("fc", 0.0),
    ("fy", float("inf")), ("phi", 0.0), ("phi", float("nan"))])
def test_las_formulas_de_flexion_rechazan_lo_que_no_puede_ser(campo, valor):
    kw = dict(M_u=10.0, d=0.2, fc=21.0, fy=420.0, phi=0.9)
    kw[campo] = valor
    with pytest.raises(DatoInvalidoError):
        M9.acero_por_flexion(**kw)


def test_un_momento_no_finito_es_limite_numerico_y_no_un_acero():
    for malo in (float("nan"), float("inf")):
        with pytest.raises(LimiteNumericoError):
            M9.acero_por_flexion(M_u=malo, d=0.2, fc=21.0, fy=420.0, phi=0.9)


def test_dorado_del_momento_de_agrietamiento():
    """M_cr = 0.67·1.6·2.887888·15.0e6 N·mm = 46.437 kN·m/m."""
    M_cr = M9.momento_de_agrietamiento(espesor=0.30, fc=21.0, gamma_3=0.67)
    assert M_cr == pytest.approx(CP["pantalla"]["M_cr"], abs=TOL)
    # con el A706 (gamma_3 = 0.75) sube en 0.75/0.67
    assert M9.momento_de_agrietamiento(
        espesor=0.30, fc=21.0, gamma_3=0.75) == pytest.approx(
        M_cr * 0.75 / 0.67, rel=REL_TRANSPORTE)


def test_dorado_de_cortante_en_las_unidades_de_la_fuente():
    """
    Punto 4 del dorado: V_c calculado en kip, ksi y pulgadas (34.5702 kip) y
    convertido al final, contra el del modulo, que usa la constante en SI.

    REESCRITO DECLARANDOLO (correcciones de T-7c, H8). Fijaba d_v = 0.216 m
    (el piso 0.72·h de la letra de 5.7.2.8) y V_c = 164.264 kN/m; fija d_v =
    0.20221 m, el de la letra ACOTADO al peralte efectivo, y V_c = 153.776
    kN/m, con el de la letra a la vista en `d_v_letra`. Por que: con el
    recubrimiento de cota, 0.72·h supera a d_e y el piso daba un brazo de
    cortante mayor que la distancia del acero a la cara comprimida.
    """
    p = CP["pantalla"]
    r = M9.cortante_del_concreto(d=p["d_m"], a=p["a_mm"] / 1000, espesor=0.30,
                                 fc=21.0, beta=2.0)
    assert r["d_v_letra"] == pytest.approx(p["d_v_letra_m"], abs=TOL_EXACTA)
    assert r["d_v"] == pytest.approx(p["d_v_m"], abs=TOL_EXACTA)   # acotado a d
    assert r["V_c"] == pytest.approx(p["V_c"], abs=TOL_CM)
    assert r["V_n"] == pytest.approx(r["V_c"], rel=REL_TRANSPORTE)    # el tope no rige
    V_r = cn.PHI_CORTE_AASHTO * r["V_n"]
    assert V_r == pytest.approx(p["V_r"], abs=TOL_CM)
    # independiente: la aritmetica en unidades inglesas, aqui mismo
    kip = 0.0316 * 2.0 * math.sqrt(21.0 / 6.894757) * (1000 / 25.4) * (
        202.21 / 25.4)
    assert r["V_c"] == pytest.approx(kip * 4.4482216, rel=REL_UNIDADES)


def test_el_peralte_de_cortante_toma_el_mayor_de_los_tres():
    # d - a/2 gobierna cuando el recubrimiento es chico
    r = M9.cortante_del_concreto(d=0.27, a=0.01, espesor=0.30, fc=21.0,
                                 beta=2.0)
    assert r["d_v"] == pytest.approx(0.265, abs=ABS_CERO)
    # 0.9·d gobierna con un bloque profundo
    r = M9.cortante_del_concreto(d=0.27, a=0.08, espesor=0.30, fc=21.0,
                                 beta=2.0)
    assert r["d_v"] == pytest.approx(0.243, abs=ABS_CERO)


def test_el_tope_de_la_resistencia_nominal_a_cortante_existe():
    """V_n <= 0.25·f'c·b_v·d_v: con un beta absurdo, manda el tope."""
    r = M9.cortante_del_concreto(d=0.27, a=0.01, espesor=0.30, fc=21.0,
                                 beta=40.0)
    assert r["V_n"] == pytest.approx(0.25 * 21.0 * 1000 * 0.265, rel=REL_TRANSPORTE)
    assert r["V_n"] < r["V_c"]


@pytest.mark.parametrize("es_zapata, espesor, vuelo, d_v, permitido", [
    (False, 0.30, None, 0.216, True),       # pantalla de menos de 16.0 in
    (False, 0.4063, None, 0.30, True),      # justo por debajo
    (False, 0.4064, None, 0.30, False),     # 16.0 in exactos: «less than»
    (False, 0.50, None, 0.40, False),       # pantalla gruesa sin estribos
    (True, 0.50, 0.60, 0.40, True),         # zapata: vuelo < 3·d_v = 1.20
    (True, 0.50, 1.20, 0.40, False),        # vuelo = 3·d_v: «less than»
    (True, 0.50, 1.50, 0.40, False),        # zapata larga y gruesa
    (True, 0.37, 1.50, 0.27, True),         # zapata larga pero delgada
])
def test_las_condiciones_del_simplificado_son_las_de_la_fuente(
        es_zapata, espesor, vuelo, d_v, permitido):
    ok, motivo = M9.simplificado_permitido(es_zapata=es_zapata,
                                           espesor=espesor, vuelo=vuelo,
                                           d_v=d_v)
    assert ok is permitido, motivo
    assert motivo


@pytest.mark.parametrize("fc, aashto, e060", [
    (21.0, 0.85, 0.85),
    (28.0, 0.85 - 0.05 * (28.0 - 27.579029) / 6.894757, 0.85),
    # 35 MPa: AASHTO 0.85 - 0.05·(35 - 27.579)/6.8948 = 0.79618;
    #         E.060  0.85 - 0.20·(35 - 28)/28 = 0.80
    (35.0, 0.79618, 0.80),
    (60.0, 0.65, 0.65),
])
def test_beta_1_de_cada_norma(fc, aashto, e060):
    assert M9.beta_1_aashto(fc) == pytest.approx(aashto, abs=TOL_FINA)
    assert M9.beta_1_e060(fc) == pytest.approx(e060, abs=TOL_FINA)


@pytest.mark.parametrize("espesor, regla, s_max, quien", [
    # 0.30 m: 1.5h = 0.45; 18 in = 0.4572; temperatura max(0.9, 0.4572);
    # E.060 min(0.9, 0.40) -> 0.40 con el mas exigente, 0.45 sin E.060
    (0.30, "mas_exigente_aashto_e060", 0.40, "E.060"),
    (0.30, "solo_aashto", 0.45, "1.5 veces"),
    # 0.20 m: 1.5h = 0.30 gobierna en los dos
    (0.20, "mas_exigente_aashto_e060", 0.30, "1.5 veces"),
    # 0.50 m (> 18 in): el 12.0 in del acero de temperatura
    (0.50, "mas_exigente_aashto_e060", 0.3048, "temperatura"),
    (0.50, "solo_aashto", 0.3048, "temperatura"),
])
def test_el_espaciamiento_maximo_es_el_menor_de_los_topes(espesor, regla,
                                                         s_max, quien):
    s, origen = M9.espaciamiento_maximo_del_armado(espesor=espesor,
                                                   regla=regla)
    assert s == pytest.approx(s_max, abs=TOL_EXACTA)
    assert quien in origen


@pytest.mark.parametrize("hm, lm, rho_h, rho_v", CP_T7C_EC_11_32)
def test_la_ecuacion_11_32_de_E060_con_sus_dos_topes(hm, lm, rho_h, rho_v):
    """
    EXT-7-01: la ecuacion completa, que hasta T-7c «se declaraba evaluada
    fuera». Piso 0,0025 y techo en la rho_h requerida.
    """
    assert M9.cuantia_vertical_ec_11_32(hm=hm, lm=lm, rho_h=rho_h) == \
        pytest.approx(rho_v, abs=TOL_EXACTA)


@pytest.mark.parametrize("campo", ["hm", "lm", "rho_h"])
@pytest.mark.parametrize("malo", [0.0, -1.0, float("nan"), float("inf")])
def test_la_ecuacion_11_32_rechaza_lo_que_no_puede_ser(campo, malo):
    kw = dict(hm=2.4, lm=3.0, rho_h=0.003)
    kw[campo] = malo
    with pytest.raises(DatoInvalidoError):
        M9.cuantia_vertical_ec_11_32(**kw)


def test_la_propuesta_de_barra_toma_el_mayor_espaciamiento_que_cumple():
    cat = M9.catalogo_de_barras()
    # 584.2 mm2/m con s <= 0.40: 1/2" a 0.20 m (645); a 0.25 no alcanza (516)
    b = M9.proponer_barra(As=584.2, s_max=0.40, catalogo=cat, desde="1/2")
    assert (b.designacion, b.espaciamiento) == ("1/2", 0.20)  # float-exacto: transcrito o declarado, no calculado
    assert b.As_provisto == pytest.approx(645.0, abs=TOL_EXACTA)
    # con el espaciamiento maximo en 0.15 m, no ofrece 0.20
    b = M9.proponer_barra(As=300.0, s_max=0.15, catalogo=cat, desde="1/2")
    assert b.espaciamiento == pytest.approx(0.15, abs=ABS_CERO)
    # si la barra minima no alcanza ni a 0.10 m, sube de diametro
    b = M9.proponer_barra(As=1500.0, s_max=0.40, catalogo=cat, desde="1/2")
    assert b.designacion == "5/8" and b.As_provisto >= 1500.0
    # y si ninguna alcanza, no inventa una
    assert M9.proponer_barra(As=6000.0, s_max=0.40, catalogo=cat,
                             desde="1/2") is None


def test_el_catalogo_de_barras_se_valida_en_el_consumidor():
    malos = [
        {"barras": {}, "espaciamientos_m": (0.2,),
         "barra_minima_principal": "1/2", "barra_reparto": "3/8"},
        {"barras": {"1/2": (12.7, -1.0)}, "espaciamientos_m": (0.2,),
         "barra_minima_principal": "1/2", "barra_reparto": "1/2"},
        {"barras": {"1/2": (12.7, 129.0)}, "espaciamientos_m": (0.2, 0.0),
         "barra_minima_principal": "1/2", "barra_reparto": "1/2"},
        {"barras": {"1/2": (12.7, 129.0)}, "espaciamientos_m": (0.2,),
         "barra_minima_principal": "7/8", "barra_reparto": "1/2"},
    ]
    for malo in malos:
        with con_valor("catalogo_barras_refuerzo_cabezal", malo,
                       motivo="catalogo imposible: la guardia del consumidor"):
            with pytest.raises(DatoInvalidoError):
                M9.catalogo_de_barras()


# ===========================================================================
# 4. LOS CRITERIOS: LOS SIETE NUEVOS Y LOS TRES QUE ESTABAN VACIOS
# ===========================================================================

def test_los_siete_criterios_nuevos_son_de_expediente_y_tienen_ventana():
    for clave in NUEVOS_T7C:
        c = ca.CRITERIOS[clave]
        assert c.nivel == modelos.NIVEL_EXPEDIENTE, clave
        assert c.etiqueta == "A", clave
        assert c.valor is not None and c.sensibilidad, clave
    # al final de la seccion del cabezal, detras del de T-7b
    claves = list(ca.CRITERIOS)
    assert claves.index(NUEVOS_T7C[0]) == claves.index("regimen_cabezal") + 1
    assert [claves[claves.index(NUEVOS_T7C[0]) + i]
            for i in range(len(NUEVOS_T7C))] == list(NUEVOS_T7C)


def test_el_regimen_de_archivo_es_el_reposo_y_la_estabilidad_sigue_cediendo():
    """
    Decision del dueño (2026-11-13): los elementos se arman con K0; la
    estabilidad externa de T-7b NO cambia.
    """
    assert ca.valor("regimen_resistencia_elementos_cabezal") == \
        REGIMEN_RESISTENCIA_K0
    assert ca.CRITERIOS["regimen_resistencia_elementos_cabezal"].sensibilidad \
        == (REGIMEN_RESISTENCIA_K0, REGIMEN_RESISTENCIA_CEDENTE)
    assert ca.valor("regimen_cabezal") == "cedente"


@pytest.mark.parametrize("clave, malo", [
    ("regimen_resistencia_elementos_cabezal", "activo"),
    ("regla_minimos_constructivos_cabezal", "solo_e060"),
    ("criterio_traccion_cabezal_ciclopeo", "sin_criterio"),
    ("acero_refuerzo_cabezal", "A615_grado_75"),
    ("fc_cabezal_mpa", 10.0),
    ("fc_cabezal_mpa", 40.0),
])
def test_las_puertas_de_los_criterios_nuevos_rechazan_lo_que_no_esta(clave,
                                                                    malo):
    with pytest.raises(ValueError):
        ca.establecer_valor_dinamico(clave, malo)


def test_los_tres_criterios_de_cortante_alto_dejaron_de_estar_vacios():
    """
    T-7c punto 2. El 0,0025 horizontal y el piso de la ec. (11-32) son los
    del articulo, [N→] por analogia (E.060 es norma de edificaciones); el
    regimen es [A] y vale «perpendicular»: el cortante del ensamble es el
    del empuje.
    """
    sin = set(ca.criterios_sin_valor())
    for clave in ANTES_VACIOS:
        assert clave not in sin, clave
    assert ca.valor(ANTES_VACIOS[0]) == pytest.approx(0.0025, abs=ABS_CERO)
    assert ca.valor(ANTES_VACIOS[2]) == pytest.approx(0.0025, abs=ABS_CERO)
    assert ca.CRITERIOS[ANTES_VACIOS[0]].etiqueta == "N->"
    assert ca.CRITERIOS[ANTES_VACIOS[2]].etiqueta == "N->"
    assert ca.valor(ANTES_VACIOS[1]) == cn.REGIMEN_CORTANTE_PERPENDICULAR
    assert ca.CRITERIOS[ANTES_VACIOS[1]].etiqueta == "A"
    assert set(ca.CRITERIOS[ANTES_VACIOS[1]].sensibilidad) == {
        cn.REGIMEN_CORTANTE_EN_EL_PLANO, cn.REGIMEN_CORTANTE_PERPENDICULAR}


def test_el_MCFT_en_ksi_y_pulgadas_queda_como_referencia_no_ejecutable():
    """
    T-7c punto 1: el procedimiento general transcrito en unidades inglesas
    se conserva bajo UNA clave rotulada y ningun modulo lo lee.
    """
    proc = ca.valor("procedimiento_flexion_corte_aashto_sec5")
    assert proc["modelo_corte"] == "simplificado_5_7_3_4_1"
    referencia = proc["referencia_no_ejecutable_5_7_3_4_2"]
    assert "NO EJECUTABLE" in referencia["nota"]
    for vieja in ("Vc_kip", "Vs_kip", "dv_in", "espaciamiento_s_in",
                  "beta_con_refuerzo_transversal_minimo"):
        assert vieja not in proc, vieja
    fuente = (RAIZ / "src" / "modulos" / "M9_cabezal.py").read_text(
        encoding="utf-8")
    arbol = ast.parse(fuente)
    cadenas = {n.value for n in ast.walk(arbol)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert "referencia_no_ejecutable_5_7_3_4_2" not in cadenas
    assert not any("epsilon_s" in c and len(c) < 40 for c in cadenas)


def test_M9_ya_no_tiene_ningun_NotImplementedError():
    """El cierre que el prompt pide, por AST y no por texto."""
    arbol = ast.parse((RAIZ / "src" / "modulos" / "M9_cabezal.py").read_text(
        encoding="utf-8"))
    lanzados = [n for n in ast.walk(arbol) if isinstance(n, ast.Raise)
                and n.exc is not None
                and "NotImplementedError" in ast.unparse(n.exc)]
    assert not lanzados
    definidas = [n.name for n in ast.walk(arbol)
                 if isinstance(n, ast.FunctionDef)]
    assert definidas.count("diseno_flexion_corte") == 1


def test_las_funciones_del_armado_dejaron_de_estar_sin_consumidor():
    """El servicio las llama: salen de la lista de M9 en el mismo commit."""
    texto = " ".join(M9.FUNCIONES_SIN_CONSUMIDOR)
    assert "armado del num. 9.4" not in texto
    assert "NotImplementedError" not in " ".join(
        M9.FUNCIONES_SIN_CONSUMIDOR.values())
    for nombre in ("armar_elemento", "ensamblar_armado", "integrar_armado",
                   "verificar_cabezal_ciclopeo",
                   "solicitaciones_de_resistencia"):
        assert hasattr(servicio, nombre), nombre


def test_los_materiales_del_armado_salen_de_sus_dos_criterios():
    """f'c del criterio; fy y gamma_3, de la designacion del acero."""
    m = M9.materiales_del_armado()
    assert m["fc"] == pytest.approx(21.0, rel=REL_TRANSPORTE)
    assert m["fy"] == pytest.approx(420.0, rel=REL_TRANSPORTE)
    assert (m["acero"], m["gamma_3"]) == ("A615_grado_60",
                                          cn.GAMMA_3_AASHTO["A615_grado_60"])
    ca.establecer_valor_dinamico("acero_refuerzo_cabezal", "A706_grado_60")
    assert M9.materiales_del_armado()["gamma_3"] == pytest.approx(
        0.75, rel=REL_TRANSPORTE)
    # segunda linea: lo que burla la puerta lo rechaza el consumidor
    for clave, malo in (("fc_cabezal_mpa", 80.0), ("fc_cabezal_mpa", -1.0),
                        ("acero_refuerzo_cabezal", "A615_grado_75")):
        with con_valor(clave, malo, motivo="guardia del consumidor"):
            with pytest.raises(DatoInvalidoError):
                M9.materiales_del_armado()


def test_un_regimen_que_burla_la_puerta_lo_rechaza_el_consumidor():
    assert M9.regimen_de_resistencia() == REGIMEN_RESISTENCIA_K0
    with con_valor("regimen_resistencia_elementos_cabezal", "activo",
                   motivo="categoria imposible: guardia del consumidor"):
        with pytest.raises(DatoInvalidoError):
            M9.regimen_de_resistencia()


# ===========================================================================
# 5. EL EMPUJE EN REPOSO: QUE SE ESCALA Y QUE NO
# ===========================================================================

def test_solo_el_empuje_del_suelo_y_el_de_la_sobrecarga_cambian(tanteo):
    """
    Punto 1 del dorado. EH.h pasa a (K0/K_A)·P_A = 25.92, horizontal; EH.v a
    0; LS.h a K0·gamma·h_eq·h = 13.16736. El peso del concreto, el del
    relleno y el de la sobrecarga NO cambian, ni ningun brazo.
    """
    cargas, datos = M9.cargas_del_cabezal(tanteo, EST)
    assert datos["K0"] == pytest.approx(CP["K0"], abs=ABS_CERO)
    reposo = {c.codigo: c for c in M9.cargas_en_reposo(cargas, datos)}
    activo = {c.codigo: c for c in cargas}
    assert reposo["EH.h"].H == pytest.approx(CP["reposo"]["EH_h"], abs=TOL)
    assert reposo["EH.v"].V == pytest.approx(CP["reposo"]["EH_v"],
                                             abs=ABS_CERO)
    assert reposo["LS.h"].H == pytest.approx(CP["reposo"]["LS_h"], abs=TOL)
    for codigo in ("DC.pantalla", "DC.zapata", "EV.talon", "LS.v"):
        assert reposo[codigo] == activo[codigo], codigo
    for codigo in activo:
        assert (reposo[codigo].x, reposo[codigo].z) == (
            activo[codigo].x, activo[codigo].z), codigo
    assert set(reposo) == set(activo)


def test_el_agua_no_se_escala_con_el_cociente(tanteo):
    """
    Con el freatico alto (drenado, 1.0 m sobre la base) hay empuje
    hidrostatico y subpresion: en reposo son LOS MISMOS, y el suelo bajo el
    agua se escala con su peso sumergido (P_A entero por K0/K_A).
    """
    ca.establecer_valor_dinamico("peso_especifico_saturado_relleno_kn_m3",
                                 20.0)
    entorno = replace(tanteo, cota_freatico=101.0)
    cargas, datos = M9.cargas_del_cabezal(entorno, EST)
    reposo = {c.codigo: c for c in M9.cargas_en_reposo(cargas, datos)}
    activo = {c.codigo: c for c in cargas}
    assert "WA.h" in activo and "WA.u" in activo
    assert reposo["WA.h"] == activo["WA.h"]
    assert reposo["WA.u"] == activo["WA.u"]
    assert reposo["EH.h"].H == pytest.approx(
        datos["P_A"] * datos["K0"] / datos["K_A"], rel=REL_TRANSPORTE)


def test_el_factor_de_carga_del_reposo_es_el_de_su_fila_y_no_el_de_la_activa(
        tanteo):
    """
    Fila «En reposo» de la Tabla 2.4.5.3.1-2: 1.35, no 1.50. Con 1.50 sobre
    K0 el armado iria con un factor que la fuente da a otro empuje.
    """
    cargas, datos = M9.cargas_del_cabezal(tanteo, EST)
    cargas0 = M9.cargas_en_reposo(cargas, datos)
    maximos, minimos = M9._combinaciones_en_reposo(cargas0, 2.0)
    for combo in (maximos, minimos):
        assert combo.marco == MARCO_LRFD
        assert combo.factor_de("EH.h") == pytest.approx(1.35, abs=ABS_CERO)
        assert combo.factor_de("LS.h") == pytest.approx(1.75, abs=ABS_CERO)
    assert maximos.factor_de("DC.zapata") == pytest.approx(1.25, abs=ABS_CERO)
    assert minimos.factor_de("DC.zapata") == pytest.approx(0.90, abs=ABS_CERO)
    assert maximos.factor_de("EV.talon") == pytest.approx(1.35, abs=ABS_CERO)
    assert minimos.factor_de("EV.talon") == pytest.approx(1.00, abs=ABS_CERO)
    assert minimos.factor_de("LS.v") == pytest.approx(0.0, abs=ABS_CERO)


def test_un_cociente_que_no_existe_no_se_inventa(tanteo):
    cargas, datos = M9.cargas_del_cabezal(tanteo, EST)
    for K_A in (0.0, float("nan")):
        with pytest.raises(LimiteNumericoError):
            M9.cargas_en_reposo(cargas, dict(datos, K_A=K_A))


# ===========================================================================
# 6. LAS SOLICITACIONES DE RESISTENCIA
# ===========================================================================

def _de(sol, clave, fragmento):
    hallados = [s for s in sol["secciones"][clave]
                if fragmento in s.combinacion]
    assert hallados, [s.combinacion for s in sol["secciones"][clave]]
    return hallados[0]


def test_dorado_de_la_pantalla_activo_reposo_y_cual_rige(tanteo):
    """
    Punto 2 del dorado: 21.4658 / 26.4906 frente a 35.4024 / 43.5024.

    REESCRITO DECLARANDOLO (correcciones de T-7c, H1). Fijaba las cifras
    del diagrama ENTERO de cada empuje con su brazo desde el arranque
    (activo 19.6424 / 35.4066, reposo 32.4311 / 58.0349), que es la formula
    del codigo y no un calculo independiente: el momento quedaba un 8.4 %
    por debajo. Fija las del diagrama integrado por encima del arranque,
    calculadas a mano en `CP_T7C_ARMADO` (control del auditor de T-7c).
    """
    sol = M9.solicitaciones_de_resistencia(tanteo)
    assert sol["regimen"] == REGIMEN_RESISTENCIA_K0
    for fragmento in ("(maximos)", "(minimos)"):
        s = _de(sol, SECCION_PANTALLA, "Resistencia I " + fragmento)
        assert s.M_u_cedente == pytest.approx(
            CP["pantalla"]["activo"]["M_u"], abs=TOL)
        assert s.V_u_cedente == pytest.approx(
            CP["pantalla"]["activo"]["V_u"], abs=TOL)
        assert s.M_u_reposo == pytest.approx(
            CP["pantalla"]["reposo"]["M_u"], abs=TOL)
        assert s.V_u_reposo == pytest.approx(
            CP["pantalla"]["reposo"]["V_u"], abs=TOL)
        assert s.M_u == pytest.approx(s.M_u_reposo, abs=ABS_CERO)
        assert s.V_u == pytest.approx(s.V_u_reposo, abs=ABS_CERO)
        assert s.phi_flexion == pytest.approx(0.9, abs=ABS_CERO)


def test_con_el_regimen_cedente_rige_el_activo_y_el_reposo_se_conserva(tanteo):
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 REGIMEN_RESISTENCIA_CEDENTE)
    sol = M9.solicitaciones_de_resistencia(tanteo)
    s = _de(sol, SECCION_PANTALLA, "Resistencia I (maximos)")
    assert s.M_u == pytest.approx(CP["pantalla"]["activo"]["M_u"], abs=TOL)
    assert s.V_u == pytest.approx(CP["pantalla"]["activo"]["V_u"], abs=TOL)
    # el otro sigue a la vista: es el contraste que se imprime al lado
    assert s.M_u_reposo == pytest.approx(CP["pantalla"]["reposo"]["M_u"],
                                         abs=TOL)


def test_en_reposo_rige_la_mayor_y_no_el_reposo_a_secas(tanteo):
    """
    Con un relleno de phi alto K0 baja (1 - sen 38° = 0.384) y el activo de
    un relleno que sube puede superarlo: la envolvente no deja que el armado
    caiga por debajo del muro que cede.
    """
    ca.establecer_valor_dinamico("phi_relleno_trasdos", 38.0)
    entorno = replace(tanteo, cota_borde_plataforma=tanteo.cota_relleno + 3.0)
    sol = M9.solicitaciones_de_resistencia(entorno)
    for clave in (SECCION_PANTALLA, SECCION_PUNTA, SECCION_TALON):
        for s in sol["secciones"][clave]:
            assert s.M_u >= s.M_u_cedente - ABS_CERO or s.M_u_cedente < 0
            assert s.V_u >= s.V_u_cedente - ABS_CERO
            if s.M_u_reposo is not None:
                assert s.M_u >= s.M_u_reposo - ABS_CERO


def test_dorado_de_la_punta_con_la_presion_de_contacto_lineal(tanteo):
    """
    Punto 6 del dorado. Resistencia I (minimos) con el empuje en reposo: la
    resultante sale del tercio central (e = 0.5918 > B/6) y la presion es
    un TRIANGULO desde la punta, de 113.17 kPa.
    """
    sol = M9.solicitaciones_de_resistencia(tanteo)
    s = _de(sol, SECCION_PUNTA, "Resistencia I (minimos)")
    assert s.M_u_reposo == pytest.approx(CP["punta"]["M_u"], abs=TOL)
    assert s.V_u_reposo == pytest.approx(CP["punta"]["V_u"], abs=TOL)
    assert s.M_u == pytest.approx(CP["punta"]["M_u"], abs=TOL)
    # y la combinacion misma, con su presion
    cargas, datos = M9.cargas_del_cabezal(tanteo, EST)
    cargas0 = M9.cargas_en_reposo(cargas, datos)
    _, minimos = M9._combinaciones_en_reposo(cargas0, 2.0)
    assert minimos.N == pytest.approx(CP["punta"]["N"], abs=TOL)
    assert minimos.excentricidad == pytest.approx(CP["punta"]["e"], abs=TOL_FINA)
    presion = M9.presion_de_contacto_lineal(minimos)
    assert presion["forma"] == "triangulo desde la punta"
    assert presion["s0"] == pytest.approx(CP["punta"]["sigma"], abs=TOL_MM)
    assert presion["s1"] == pytest.approx(0.0, abs=ABS_CERO)


def test_la_presion_lineal_equilibra_la_resultante_en_los_tres_casos():
    """
    Trapecio, triangulo desde la punta y triangulo desde el talon: en los
    tres la integral de la presion es N y su centro de gravedad cae donde
    cae la resultante. Es la condicion que define la distribucion.
    """
    def combo(N, x_res, B=2.0):
        return modelos.CombinacionDeEstabilidad(
            nombre="de prueba", marco=MARCO_LRFD, condicion=EST, factores=(),
            N=N, H=0.0, M_estabilizante=N * x_res, M_volcante=0.0, B=B)

    for x_res, forma in ((0.90, "trapecio"), (0.40, "triangulo desde la punta"),
                         (1.75, "triangulo desde el talon")):
        c = combo(100.0, x_res)
        p = M9.presion_de_contacto_lineal(c)
        assert p["forma"] == forma
        F, M = M9._carga_lineal_sobre_un_tramo(p["x0"], p["x1"], p["s0"],
                                               p["s1"], 0.0, 2.0, 0.0)
        assert F == pytest.approx(100.0, rel=REL_TRANSPORTE)
        assert M / F == pytest.approx(x_res, rel=REL_TRANSPORTE)
        assert min(p["s0"], p["s1"]) >= -ABS_CERO


@pytest.mark.parametrize("N, x_res", [(0.0, 1.0), (-5.0, 1.0), (50.0, 0.0),
                                      (50.0, -0.2), (50.0, 2.0),
                                      (float("nan"), 1.0)])
def test_sin_resultante_dentro_de_la_base_no_hay_presion_lineal(N, x_res):
    c = modelos.CombinacionDeEstabilidad(
        nombre="de prueba", marco=MARCO_LRFD, condicion=EST, factores=(),
        N=N, H=0.0, M_estabilizante=N * x_res if N == N else 0.0,
        M_volcante=0.0, B=2.0)
    assert M9.presion_de_contacto_lineal(c) is None


def test_la_presion_del_armado_no_es_la_uniforme_de_la_capacidad_portante(
        tanteo):
    """
    AASHTO 10.6.5: para ARMAR la zapata, presion triangular o trapezoidal;
    la uniforme sobre B - 2e es la de E1. Con la resultante hacia la punta la
    lineal da mas momento en la punta que la uniforme del ensamble de T-7b.
    """
    e = M9.ensamble_estabilidad(tanteo, EST)
    uniforme = next(s for s in e.solicitaciones
                    if s.elemento == ELEMENTO_ZAPATA
                    and s.seccion.startswith("punta")
                    and s.combinacion == "Resistencia I (minimos)")
    sol = M9.solicitaciones_de_resistencia(tanteo)
    lineal = _de(sol, SECCION_PUNTA, "Resistencia I (minimos)")
    assert uniforme.M_u == pytest.approx(6.6065, abs=TOL)     # T-7b
    assert lineal.M_u_cedente == pytest.approx(7.848, abs=TOL)
    assert lineal.M_u_cedente > uniforme.M_u
    assert "lineal" in lineal.nota and "AASHTO 10.6.5" in lineal.nota


def test_las_solicitaciones_de_la_zapata_con_y_sin_agua(tanteo):
    """
    `solicitaciones_de_la_zapata` por si sola: sin presion evaluable no da
    nada; y con el freatico alto la subpresion entra a la PUNTA -- empuja
    la zapata hacia arriba junto con el terreno --, que es lo que la
    solicitacion de la interfaz de T-7b no contaba.
    """
    g = tanteo.geometria
    cargas, datos = M9.cargas_del_cabezal(tanteo, EST)
    combos = M9.combinaciones_de_estabilidad(cargas, datos, EST, g.B)
    maximos = next(c for c in combos if c.nombre == "Resistencia I (maximos)")
    z = M9.solicitaciones_de_la_zapata(g, cargas, maximos, datos)
    assert z["forma"] == "trapecio"
    assert z["punta"][1] == pytest.approx(8.308, abs=TOL)
    fuera = replace(maximos, M_estabilizante=0.0, M_volcante=10.0)
    assert M9.solicitaciones_de_la_zapata(g, cargas, fuera, datos) is None
    # con 1.0 m de agua sobre la base: u = 9.81 kPa uniforme bajo la zapata
    ca.establecer_valor_dinamico("peso_especifico_saturado_relleno_kn_m3",
                                 20.0)
    mojado = replace(tanteo, cota_freatico=101.0)
    cargas_w, datos_w = M9.cargas_del_cabezal(mojado, EST)
    combos_w = M9.combinaciones_de_estabilidad(cargas_w, datos_w, EST, g.B)
    max_w = next(c for c in combos_w if c.nombre == "Resistencia I (maximos)")
    con = M9.solicitaciones_de_la_zapata(g, cargas_w, max_w, datos_w)
    presion = M9.presion_de_contacto_lineal(max_w)
    F, M = M9._carga_lineal_sobre_un_tramo(
        presion["x0"], presion["x1"], presion["s0"], presion["s1"], 0.0, 0.6,
        0.6)
    peso = max_w.factor_de("DC.zapata") * 23.56 * 0.4
    subpresion = 9.81 * 0.6                  # kN/m sobre la punta, factor 1
    assert con["punta"][0] == pytest.approx(F + subpresion - peso * 0.6,
                                            rel=REL_CALCULO)
    assert con["punta"][1] == pytest.approx(
        M + subpresion * 0.3 - peso * 0.18, rel=REL_CALCULO)


def test_dorado_del_talon_con_el_peso_entero(tanteo):
    """
    AASHTO 11.6.1.2: el talon cargado con el peso entero de lo que tiene
    encima. 95.4844 kN/m y 56.8854 kN·m/m; el «mas exacto» (descontando la
    reaccion) se imprime en la nota y no rige.
    """
    sol = M9.solicitaciones_de_resistencia(tanteo)
    s = _de(sol, SECCION_TALON, "Resistencia I (maximos)")
    assert s.V_u_cedente == pytest.approx(CP["talon"]["V_u"], abs=TOL)
    assert s.M_u_cedente == pytest.approx(CP["talon"]["M_u"], abs=TOL)
    assert s.M_u == pytest.approx(CP["talon"]["M_u"], abs=TOL)
    assert "peso entero" in s.nota and "descontando" in s.nota
    # en reposo el empuje no tiene componente vertical: carga menos el talon
    assert s.M_u_reposo < s.M_u_cedente


def test_el_evento_extremo_va_con_phi_1_y_con_la_resultante_a_media_altura(
        tanteo):
    """
    Punto 7 del dorado. La fuente no da un K0 sismico: se arma con el empuje
    del metodo del ensamble y, en la pantalla, con la mayor de su posicion
    (22.5733) y la resultante total a h/2 (25.6499).

    REESCRITO DECLARANDOLO (correcciones de T-7c, H1). Fijaba 20.9007 y
    24.2235, con la resultante entera de cada empuje y la inercia del muro
    y de la zapata sobre la pantalla, y que el cortante NO cambiaba con la
    resultante a h/2. Fija las cifras con cada diagrama integrado sobre el
    arranque, la inercia de la pantalla sola y la resultante a h/2 como un
    diagrama uniforme, que mueve TAMBIEN el cortante (24.4962 en su posicion
    frente a 25.6499 a h/2): con el diagrama integrado, subir la resultante
    pone mas empuje sobre el arranque.
    """
    sol = M9.solicitaciones_de_resistencia(tanteo)
    assert sol["sismico"]
    s = next(x for x in sol["secciones"][SECCION_PANTALLA]
             if x.combinacion == "Evento Extremo I, 100% P_AE + 50% P_IR")
    p = CP["pantalla"]["sismico"]
    assert s.condicion is SIS
    assert s.phi_flexion == pytest.approx(1.0, abs=ABS_CERO)
    assert s.phi_corte == pytest.approx(1.0, abs=ABS_CERO)
    assert s.M_u_cedente == pytest.approx(p["en_su_posicion"], abs=TOL)
    assert s.M_u_reposo == pytest.approx(p["a_media_altura"], abs=TOL)
    assert s.M_u == pytest.approx(p["a_media_altura"], abs=TOL)
    assert "h/2" in s.nota
    assert s.V_u_cedente == pytest.approx(p["V_en_su_posicion"], abs=TOL)
    assert s.V_u == pytest.approx(p["a_media_altura"], abs=TOL)
    s2 = next(x for x in sol["secciones"][SECCION_PANTALLA]
              if x.combinacion.startswith("Evento Extremo I, 50% P_AE")
              and "portante" not in x.combinacion)
    assert s2.M_u_cedente == pytest.approx(p["caso_2"]["en_su_posicion"],
                                           abs=TOL)
    assert s2.M_u == pytest.approx(p["caso_2"]["a_media_altura"], abs=TOL)
    # y la zapata bajo sismo no se toca
    z = next(x for x in sol["secciones"][SECCION_PUNTA]
             if x.condicion is SIS)
    assert z.M_u_reposo is None


def test_con_regimen_cedente_el_sismo_es_el_de_la_interfaz_tal_cual(tanteo):
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 REGIMEN_RESISTENCIA_CEDENTE)
    sol = M9.solicitaciones_de_resistencia(tanteo)
    s = next(x for x in sol["secciones"][SECCION_PANTALLA]
             if x.combinacion == "Evento Extremo I, 100% P_AE + 50% P_IR")
    assert s.M_u == pytest.approx(
        CP["pantalla"]["sismico"]["en_su_posicion"], abs=TOL)


def test_si_la_cadena_reduce_kh_el_muro_que_no_cede_lo_avisa(tanteo,
                                                           monkeypatch):
    """
    AASHTO 11.6.5.4: para el muro que no cede, k_h = 1.0·k_h0. Si la cadena
    sismica reduce por desplazamiento, el armado del evento extremo queda
    por debajo y se dice; con el regimen cedente no hay nada que avisar.
    """
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h=0.25, k_v=0.0, k_h0=0.50))
    sol = M9.solicitaciones_de_resistencia(tanteo)
    assert any("11.6.5.4" in a and "k_h0" in a for a in sol["avisos"])
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 REGIMEN_RESISTENCIA_CEDENTE)
    sol = M9.solicitaciones_de_resistencia(tanteo)
    assert not any("11.6.5.4" in a for a in sol["avisos"])


def test_si_el_sismo_no_es_evaluable_el_armado_sale_de_resistencia_I_y_avisa(
        tanteo):
    """
    Sin drenaje el relleno se llena de agua y la condicion sismica no es
    evaluable (T-7b): el armado NO se detiene, sale de Resistencia I y lo
    dice; el bloqueo de esa causa es el de la estabilidad sismica.
    """
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    ca.establecer_valor_dinamico("peso_especifico_saturado_relleno_kn_m3",
                                 20.0)
    sol = M9.solicitaciones_de_resistencia(tanteo)
    assert not sol["sismico"]
    assert all(s.condicion is EST for v in sol["secciones"].values()
               for s in v)
    assert any("SOLO de Resistencia I" in a for a in sol["avisos"])


def test_el_contraste_E060_usa_sus_combinaciones_y_no_las_de_AASHTO(tanteo):
    """
    Punto 5 del dorado: (9-6) con 1,7 sobre el empuje y la sobrecarga, sobre
    las mismas cargas sin factorar: 39.0538 kN·m/m y 49.2538 kN/m.

    REESCRITO DECLARANDOLO (correcciones de T-7c, H1): fijaba 35.5332 y
    66.4485, con la resultante entera de cada empuje; el contraste usa la
    misma integracion sobre el arranque que el marco que rige.
    """
    sol = M9.solicitaciones_de_resistencia(tanteo)
    M, V = sol["e060"][SECCION_PANTALLA]
    assert M == pytest.approx(CP["e060_pantalla"]["M_u"], abs=TOL)
    assert V == pytest.approx(CP["e060_pantalla"]["V_u"], abs=TOL)
    cargas, _ = M9.cargas_del_cabezal(tanteo, EST)
    c96, c97 = M9._combinaciones_e060(cargas, 2.0)
    assert c96.marco == c97.marco == MARCO_E060
    assert c96.factor_de("DC.zapata") == pytest.approx(1.4, abs=ABS_CERO)
    assert c96.factor_de("EH.h") == pytest.approx(1.7, abs=ABS_CERO)
    assert c96.factor_de("EV.talon") == pytest.approx(1.7, abs=ABS_CERO)
    assert c96.factor_de("LS.h") == pytest.approx(1.7, abs=ABS_CERO)
    assert c97.factor_de("DC.zapata") == pytest.approx(0.9, abs=ABS_CERO)
    assert c97.factor_de("LS.h") == pytest.approx(0.0, abs=ABS_CERO)


def test_las_solicitaciones_del_ensamble_no_recorren_el_marco_del_contraste(
        tanteo):
    """
    `solicitaciones_por_elemento` gano el parametro `marco`: por defecto
    sigue entregando SOLO el LRFD, que es lo que la estabilidad guarda.
    """
    e = M9.ensamble_estabilidad(tanteo, EST)
    assert e.solicitaciones
    nombres = {c.nombre for c in e.combinaciones}
    assert not any("E.060" in n for n in nombres)
    assert all("Resistencia I" in s.combinacion for s in e.solicitaciones)


# ===========================================================================
# 7. EL DISEÑO DE UNA SECCION: `diseno_flexion_corte`
# ===========================================================================

def test_diseno_flexion_corte_ya_no_lanza_NotImplementedError():
    """El test que el prompt pide, sobre una seccion declarada."""
    seccion = M9.diseno_flexion_corte(momento=30.0, cortante=40.0,
                                      espesor=0.30)
    assert seccion.barra is not None
    assert [v.codigo for v in seccion.verificaciones] == [
        "A1.pantalla", "A2.pantalla", "A3.pantalla", "A4.pantalla"]
    assert all(v.estado is EstadoDeVerificacion.CUMPLE
               for v in seccion.verificaciones)
    assert all(v.paso is not None for v in seccion.verificaciones)


def test_diseno_flexion_corte_sin_sus_datos_se_detiene_en_el_dato():
    with pytest.raises(DatoFaltanteError) as e:
        M9.diseno_flexion_corte(momento=30.0, cortante=40.0)
    assert e.value.campo == "espesor"
    with pytest.raises(DatoFaltanteError) as e:
        M9.diseno_flexion_corte(espesor=0.30)
    assert e.value.campo == "momento"
    with pytest.raises(DatoFaltanteError) as e:
        M9.diseno_flexion_corte(momento=10.0, espesor=0.30)
    assert e.value.campo == "cortante"


@pytest.mark.parametrize("kw", [
    dict(momento=-1.0, cortante=10.0, espesor=0.3),
    dict(momento=10.0, cortante=float("nan"), espesor=0.3),
    dict(momento=float("inf"), cortante=10.0, espesor=0.3),
    dict(momento=10.0, cortante=10.0, espesor=0.0),
    dict(momento=10.0, cortante=10.0, espesor=float("nan")),
])
def test_diseno_flexion_corte_rechaza_lo_que_no_puede_ser(kw):
    with pytest.raises(DatoInvalidoError):
        M9.diseno_flexion_corte(**kw)


def test_dorado_de_la_seccion_de_la_pantalla_entera(tanteo):
    """
    Puntos 3 y 4 del dorado, por la funcion que arma: recubrimiento 91.44
    mm, d = 0.20221 m, 476.4 / 630.7 / 232.8 mm2/m, Ø 1/2" @ 0.20 m, M_r =
    47.4507, V_r = 138.40.

    REESCRITO DECLARANDOLO (correcciones de T-7c, H1 y H8): fijaba 435.3 /
    584.2 mm2/m y V_r = 147.84 (resultante entera de cada empuje y d_v de
    la letra); las cifras nuevas salen del momento con el diagrama
    integrado sobre el arranque y de d_v acotado al peralte efectivo. La
    barra propuesta no cambia.
    """
    sol = M9.solicitaciones_de_resistencia(tanteo)
    (p,) = M9.armar_elemento(tanteo, ELEMENTO_PANTALLA, sol)
    d = CP["pantalla"]
    assert p.recubrimiento_mm == pytest.approx(d["recubrimiento_mm"], abs=TOL_EXACTA)
    assert p.d == pytest.approx(d["d_m"], abs=TOL_EXACTA)
    assert p.As_resistencia == pytest.approx(d["As_resistencia"], abs=TOL_AS)
    assert p.As_minimo_flexion == pytest.approx(d["As_minimo_flexion"],
                                                abs=TOL_AS)
    assert p.As_minimo_constructivo == pytest.approx(d["As_temperatura"],
                                                     abs=TOL_AS)
    assert "5.10.6" in p.origen_minimo          # gana a los 225 de E.060
    assert p.As_adoptado == pytest.approx(d["As_minimo_flexion"], abs=TOL_AS)
    assert "minimo de flexion" in p.gobierna
    assert p.s_max == pytest.approx(d["s_max"], abs=TOL_EXACTA)
    assert (p.barra.designacion, p.barra.espaciamiento) == d["barra"][:2]
    assert p.barra.As_provisto == pytest.approx(d["barra"][2], abs=TOL_EXACTA)
    assert p.M_r == pytest.approx(d["M_r"], abs=TOL)
    assert p.epsilon_t == pytest.approx(d["epsilon_t"], abs=TOL_FINA)
    assert p.d_v == pytest.approx(d["d_v_m"], abs=TOL_EXACTA)
    assert p.V_c == pytest.approx(d["V_c"], abs=TOL_CM)
    assert p.V_r == pytest.approx(d["V_r"], abs=TOL_CM)
    # las verificaciones, con demanda y capacidad en su sitio
    a1 = next(v for v in p.verificaciones if v.codigo == "A1.pantalla.e")
    assert a1.valor_obtenido == pytest.approx(d["reposo"]["M_u"], abs=TOL)
    assert a1.valor_admisible == pytest.approx(d["M_r"], abs=TOL)
    a2 = next(v for v in p.verificaciones if v.codigo == "A2.pantalla.e")
    assert a2.valor_obtenido == pytest.approx(d["reposo"]["V_u"], abs=TOL)


def test_dorado_del_contraste_E060_de_la_pantalla(tanteo):
    """
    El dorado «calculado a mano con E.060» del prompt: A_s = 527.1 mm2/m,
    phi·V_c = 133.90 kN/m, aprovechamiento 0.8172. Informa: no decide.
    REESCRITO DECLARANDOLO (H1): fijaba 478.2 mm2/m y 0.7414, con la
    resultante entera de cada empuje.
    """
    sol = M9.solicitaciones_de_resistencia(tanteo)
    (p,) = M9.armar_elemento(tanteo, ELEMENTO_PANTALLA, sol)
    e = CP["e060_pantalla"]
    assert p.M_u_e060 == pytest.approx(e["M_u"], abs=TOL)
    assert p.V_u_e060 == pytest.approx(e["V_u"], abs=TOL)
    assert p.As_e060 == pytest.approx(e["As"], abs=TOL_AS)
    assert p.V_r_e060 == pytest.approx(e["phi_Vc"], abs=e["tolerancia_V"])
    a5 = next(v for v in p.verificaciones if v.codigo == "A5.pantalla.e")
    assert a5.valor_obtenido == pytest.approx(e["aprovechamiento"],
                                              abs=e["tolerancia_uso"])
    assert a5.estado is EstadoDeVerificacion.CUMPLE
    assert "analogia" in a5.paso.umbral.aplicacion


def test_las_resistencias_de_E060_solo_se_comparan_con_cargas_de_E060(tanteo):
    """
    NO SE CRUZAN LOS MARCOS. La fila A5 lleva el momento de (9-6) y su
    resistencia lleva 0,85 de cortante; las filas A1 y A2 llevan el momento
    de Resistencia I y phi = 0.90. Ninguna mezcla las dos cosas.
    """
    sol = M9.solicitaciones_de_resistencia(tanteo)
    (p,) = M9.armar_elemento(tanteo, ELEMENTO_PANTALLA, sol)
    por = {v.codigo.split(".")[0]: v for v in p.verificaciones}
    simbolos = lambda v: {m.simbolo: m for m in v.paso.sustitucion}  # noqa: E731
    assert simbolos(por["A1"])["M_u"].valor == pytest.approx(
        CP["pantalla"]["reposo"]["M_u"], abs=TOL)
    assert simbolos(por["A1"])["phi"].valor == pytest.approx(0.9,
                                                             abs=ABS_CERO)
    assert "M_u (E.060)" not in simbolos(por["A1"])
    assert simbolos(por["A5"])["M_u (E.060)"].valor == pytest.approx(
        CP["e060_pantalla"]["M_u"], abs=TOL)
    assert "M_u" not in simbolos(por["A5"])
    # la resistencia de E.060 es 0,85·0,17·sqrt(f'c)·d, no 0.90·V_c de AASHTO
    assert p.V_r_e060 == pytest.approx(
        0.85 * 0.17 * math.sqrt(21.0) * 1000 * p.d, rel=REL_CALCULO)
    assert p.V_r != pytest.approx(p.V_r_e060, rel=REL)


def test_A1_puede_fallar_cuando_la_seccion_no_alcanza():
    """
    Una verificacion que no puede fallar no es una verificacion (INF-5.1.12
    lo dijo de M10). 500 kN·m/m sobre 0.30 m: el bloque no lo equilibra.
    """
    s = M9.diseno_flexion_corte(momento=500.0, cortante=10.0, espesor=0.30)
    a1 = next(v for v in s.verificaciones if v.codigo == "A1.pantalla")
    assert a1.estado is EstadoDeVerificacion.NO_CUMPLE
    assert s.barra is None
    assert "aumentar el espesor" in a1.paso.veredicto.explicacion
    assert s.gobierna == "la seccion no alcanza"


def test_A1_falla_tambien_cuando_el_catalogo_no_tiene_barra_que_alcance():
    """160 kN·m/m sobre 0.30 m pide mas que 1" a 0.10 m (5100 mm2/m)? No:
    lo que se agota antes es el limite de traccion. Se fija por el veredicto."""
    momento = 140.0
    s = M9.diseno_flexion_corte(momento=momento, cortante=10.0, espesor=0.30)
    a1 = next(v for v in s.verificaciones if v.codigo == "A1.pantalla")
    if s.barra is None:
        assert a1.estado is EstadoDeVerificacion.NO_CUMPLE
    else:
        # con barra: cumple solo si la seccion sigue controlada por traccion
        controlada = s.epsilon_t >= cn.EPSILON_TL_AASHTO
        resiste = s.M_r >= momento
        assert a1.cumple is (controlada and resiste)


def test_A1_no_da_por_buena_una_seccion_que_no_esta_controlada_por_traccion():
    """
    El factor 0.90 solo vale con epsilon_t >= 0.005 (AASHTO 5.6.2.1). Con un
    catalogo de una sola barra enorme muy junta, la seccion queda
    sobrearmada: A1 no cumple aunque phi·M_n supere a M_u.
    """
    catalogo = {"barras": {"1": (25.4, 510.0)}, "espaciamientos_m": (0.05,),
                "barra_minima_principal": "1", "barra_reparto": "1"}
    with con_valor("catalogo_barras_refuerzo_cabezal", catalogo,
                   motivo="seccion sobrearmada: fija el limite de traccion"):
        s = M9.diseno_flexion_corte(momento=20.0, cortante=10.0, espesor=0.25)
    assert s.barra is not None and s.barra.As_provisto == pytest.approx(
        10200.0, abs=TOL_K)
    assert s.epsilon_t < cn.EPSILON_TL_AASHTO
    a1 = next(v for v in s.verificaciones if v.codigo == "A1.pantalla")
    assert a1.estado is EstadoDeVerificacion.NO_CUMPLE
    assert "controlada por traccion" in a1.paso.veredicto.explicacion


def test_A2_puede_fallar_y_no_propone_estribos():
    s = M9.diseno_flexion_corte(momento=10.0, cortante=400.0, espesor=0.30)
    a2 = next(v for v in s.verificaciones if v.codigo == "A2.pantalla")
    assert a2.estado is EstadoDeVerificacion.NO_CUMPLE
    assert a2.valor_obtenido > a2.valor_admisible
    assert "aumentar el espesor" in a2.paso.veredicto.explicacion


def test_los_umbrales_de_A1_y_A2_son_inclusivos():
    """Justo en la resistencia cumple; un pelo por encima, no."""
    base = M9.diseno_flexion_corte(momento=30.0, cortante=40.0, espesor=0.30)
    for momento, cortante, codigo, cumple in (
            (base.M_r, 40.0, "A1.pantalla", True),
            (base.M_r * 1.0001, 40.0, "A1.pantalla", None),
            (30.0, base.V_r, "A2.pantalla", True),
            (30.0, base.V_r * 1.0001, "A2.pantalla", False)):
        s = M9.diseno_flexion_corte(momento=momento, cortante=cortante,
                                    espesor=0.30)
        v = next(x for x in s.verificaciones if x.codigo == codigo)
        if cumple is None:
            # el momento mayor cambia el acero adoptado: lo que se fija es
            # que la resistencia provista nunca queda por debajo
            assert s.barra is None or s.M_r >= momento - 1e-9
        else:
            assert v.cumple is cumple, (momento, cortante, codigo)


def test_cada_combinacion_se_comprueba_con_SU_factor_de_resistencia():
    """
    Resistencia I con 0.90 y Evento Extremo con 1.0: el acero que rige es el
    de la combinacion que mas pide una vez dividida por su phi, no la de
    mayor momento.
    """
    # 36 con phi 1.0 pide menos acero que 34 con phi 0.9 (34/0.9 = 37.8)
    s = M9.diseno_flexion_corte(
        solicitaciones=(_sol(M=34.0, V=10.0, phi=0.9, nombre="Resistencia"),
                        _sol(M=36.0, V=10.0, phi=1.0, condicion=SIS,
                             nombre="Extremo")),
        espesor=0.30)
    assert s.rige_flexion.combinacion == "Resistencia"
    s2 = M9.diseno_flexion_corte(
        solicitaciones=(_sol(M=34.0, V=10.0, phi=0.9, nombre="Resistencia"),
                        _sol(M=40.0, V=10.0, phi=1.0, condicion=SIS,
                             nombre="Extremo")),
        espesor=0.30)
    assert s2.rige_flexion.combinacion == "Extremo"
    assert s2.As_resistencia == pytest.approx(M9.acero_por_flexion(
        M_u=40.0, d=s2.d, fc=21.0, fy=420.0, phi=1.0), rel=REL_TRANSPORTE)


def test_el_minimo_de_flexion_sale_del_momento_de_resistencia_y_no_del_sismico():
    """
    5.6.3.3: «1.33 times the factored moment required by the applicable
    STRENGTH load combination». Un momento sismico mayor no lo mueve.
    """
    solo = M9.diseno_flexion_corte(
        solicitaciones=(_sol(M=10.0, V=5.0),), espesor=0.30)
    con_sismo = M9.diseno_flexion_corte(
        solicitaciones=(_sol(M=10.0, V=5.0),
                        _sol(M=30.0, V=5.0, phi=1.0, condicion=SIS)),
        espesor=0.30)
    assert con_sismo.As_minimo_flexion == pytest.approx(
        solo.As_minimo_flexion, rel=REL_TRANSPORTE)
    # y es el menor de 1.33·M_u y M_cr: con M_u chico manda 1.33·M_u
    assert solo.As_minimo_flexion == pytest.approx(M9.acero_por_flexion(
        M_u=13.3, d=solo.d, fc=21.0, fy=420.0, phi=0.9), rel=REL_CALCULO)
    grande = M9.diseno_flexion_corte(
        solicitaciones=(_sol(M=45.0, V=5.0),), espesor=0.30)
    assert grande.As_minimo_flexion == pytest.approx(M9.acero_por_flexion(
        M_u=CP["pantalla"]["M_cr"], d=grande.d, fc=21.0, fy=420.0, phi=0.9),
        abs=TOL_AS)


def test_fuera_del_simplificado_el_cortante_se_detiene_con_su_rotulo():
    """
    Una pantalla de 0.45 m sin estribos queda fuera de 5.7.3.4.1 (16.0 in):
    «metodo no evaluable», con el rotulo del ARMADO y no el de HDS-5.
    """
    with pytest.raises(MetodoNoEvaluableError) as e:
        M9.diseno_flexion_corte(momento=30.0, cortante=40.0, espesor=0.45,
                                id_punto="T-00")
    assert e.value.rotulo == modelos.MOTIVO_METODO_NO_EVALUABLE_ARMADO
    assert str(e.value).startswith("método no evaluable (AASHTO LRFD 5.7.3.4")
    assert "HDS-5" not in str(e.value)
    assert "5.7.3.4.2" in e.value.procedimiento
    assert isinstance(e.value, ErrorProyecto)


def test_una_zapata_gruesa_y_corta_si_entra_en_el_simplificado():
    """La otra condicion de 5.7.3.4.1: vuelo < 3·d_v."""
    kw = dict(momento=30.0, cortante=40.0, espesor=0.60, es_zapata=True,
              elemento=ELEMENTO_ZAPATA, clave=SECCION_PUNTA,
              seccion="punta de prueba", cara="inferior", ancho_seccion=2.0)
    s = M9.diseno_flexion_corte(vuelo=0.80, **kw)
    assert s.V_r > 0
    with pytest.raises(MetodoNoEvaluableError):
        M9.diseno_flexion_corte(vuelo=2.50, **kw)


def test_la_pantalla_avisa_cuando_el_cortante_pasa_de_la_mitad_de_la_resistencia():
    """
    AASHTO 5.7.2.3 exceptua losas, zapatas y alcantarillas; que la pantalla
    sea una losa es lectura del proyecto. Por encima de 0.5·phi·V_c se dice.
    """
    poco = M9.diseno_flexion_corte(momento=10.0, cortante=20.0, espesor=0.30)
    mucho = M9.diseno_flexion_corte(momento=10.0, cortante=100.0,
                                    espesor=0.30)
    assert not any("5.7.2.3" in a for a in poco.avisos)
    assert any("5.7.2.3" in a for a in mucho.avisos)
    zapata = M9.diseno_flexion_corte(
        momento=10.0, cortante=100.0, espesor=0.30, es_zapata=True,
        vuelo=0.5, clave=SECCION_PUNTA, elemento=ELEMENTO_ZAPATA)
    assert not any("5.7.2.3" in a for a in zapata.avisos)


# ===========================================================================
# 8. RECUBRIMIENTO SIN DATO, MINIMOS Y REGIMEN DE CORTANTE DE E.060
# ===========================================================================

def test_sin_el_dato_de_exposicion_el_recubrimiento_es_la_cota_y_no_un_relleno():
    """
    El prompt pedia «sin dato, 70 mm»; eso seria suponer la categoria del
    acero y la agresividad del sitio. Se arma con la cota mas exigente
    (3.0 in x 1.2 = 91.44 mm) y se AVISA que el dato sigue faltando.
    """
    _sin_datos_de_exposicion()
    for condicion in ("contra_suelo", "suelo_intemperie_le_5_8",
                      "suelo_intemperie_ge_3_4"):
        mm, origen, aviso = M9.recubrimiento_para_armar(condicion=condicion)
        assert mm == pytest.approx(91.44, abs=TOL_EXACTA)
        assert mm >= cn.RECUBRIMIENTO[condicion]
        assert "cota mas exigente" in origen
        assert aviso and "categoria_refuerzo_aashto" in aviso
        assert "exposicion_quimica_ems" in aviso
    # los dos criterios siguen SIN valor: no se rellenaron
    assert "categoria_refuerzo_aashto" in ca.criterios_sin_valor()
    assert "exposicion_quimica_ems" in ca.criterios_sin_valor()


def test_con_los_dos_datos_declarados_el_recubrimiento_es_el_de_la_regla():
    """Categoria A y a/c <= 0.40 (cloruros): 70.0 / 61.0 / 61.0 mm."""
    exposicion = {"so4_suelo_pct": 0.05, "so4_agua_ppm": None,
                  "tabla_4_2": {"baja_permeabilidad": False,
                                "congelamiento_deshielo": False,
                                "cloruros": True}}
    with con_valor("categoria_refuerzo_aashto", "A",
                   motivo="acero sin recubrir, de prueba"), \
            con_valor("exposicion_quimica_ems", exposicion,
                      motivo="analisis quimico de prueba"):
        contra, origen, aviso = M9.recubrimiento_para_armar(
            condicion="contra_suelo")
        fina, _, _ = M9.recubrimiento_para_armar(
            condicion="suelo_intemperie_le_5_8")
    assert aviso is None and "regla del mayor" in origen
    assert contra == pytest.approx(70.0, abs=TOL_EXACTA)
    assert fina == pytest.approx(76.2 * 0.8, abs=TOL_EXACTA)
    assert contra < 91.44 and fina < 91.44


def test_un_criterio_pendiente_que_no_es_de_recubrimiento_no_se_traga():
    """Solo los dos de exposicion abren la cota; cualquier otro detiene."""
    with sin_valor("situacion_recubrimiento_aashto"):
        with pytest.raises(CriterioPendienteError) as e:
            M9.recubrimiento_para_armar(condicion="contra_suelo")
    assert e.value.clave == "situacion_recubrimiento_aashto"


def test_el_minimo_de_E060_por_cara_muro_y_zapata():
    # muro de 0.30 m (dos capas): 0.0015·300 000/2 = 225; 0.0020 -> 300
    v, origen = M9.minimo_e060_por_cara(es_zapata=False, direccion="vertical",
                                        espesor=0.30)
    assert v == pytest.approx(225.0, abs=TOL_EXACTA) and "2 capa" in origen
    h, _ = M9.minimo_e060_por_cara(es_zapata=False, direccion="horizontal",
                                   espesor=0.30)
    assert h == pytest.approx(300.0, abs=TOL_EXACTA)
    # muro de 0.20 m (una capa: 14.3.2 es estricto): 0.0015·200 000 = 300
    v, origen = M9.minimo_e060_por_cara(es_zapata=False, direccion="vertical",
                                        espesor=0.20)
    assert v == pytest.approx(300.0, abs=TOL_EXACTA) and "1 capa" in origen
    # zapata de 0.40 m: 0.0012·400 000 = 480 en traccion; 0.0018/2 -> 360
    p, _ = M9.minimo_e060_por_cara(es_zapata=True, direccion="principal",
                                   espesor=0.40)
    r, _ = M9.minimo_e060_por_cara(es_zapata=True, direccion="reparto",
                                   espesor=0.40)
    assert p == pytest.approx(480.0, abs=TOL_EXACTA)
    assert r == pytest.approx(360.0, abs=TOL_EXACTA)


def test_con_solo_AASHTO_los_minimos_de_E060_no_entran():
    con = M9.diseno_flexion_corte(
        momento=5.0, cortante=5.0, espesor=0.40, es_zapata=True, vuelo=0.5,
        clave=SECCION_PUNTA, elemento=ELEMENTO_ZAPATA, ancho_seccion=2.0)
    assert con.As_minimo_constructivo == pytest.approx(480.0, abs=TOL_EXACTA)
    assert "E.060" in con.origen_minimo
    ca.establecer_valor_dinamico("regla_minimos_constructivos_cabezal",
                                 "solo_aashto")
    sin = M9.diseno_flexion_corte(
        momento=5.0, cortante=5.0, espesor=0.40, es_zapata=True, vuelo=0.5,
        clave=SECCION_PUNTA, elemento=ELEMENTO_ZAPATA, ancho_seccion=2.0)
    assert sin.As_minimo_constructivo < 480.0
    assert "5.10.6" in sin.origen_minimo
    assert sin.s_max > con.s_max            # sin el tope de 400 mm de E.060


def test_con_el_cortante_en_el_plano_declarado_rigen_los_pisos_de_11_10_10():
    """
    T-7c punto 2. Perpendicular (archivo): 14.3.1. En el plano: 0,0025
    horizontal y la ec. (11-32) vertical, que con rho_h en su piso da 0,0025.
    """
    v0, _ = M9.minimo_e060_por_cara(es_zapata=False, direccion="vertical",
                                    espesor=0.30, hm=2.4, lm=3.0)
    h0, _ = M9.minimo_e060_por_cara(es_zapata=False, direccion="horizontal",
                                    espesor=0.30, hm=2.4, lm=3.0)
    ca.establecer_valor_dinamico("regimen_cortante_muro_e060_art_11_10_2",
                                 cn.REGIMEN_CORTANTE_EN_EL_PLANO)
    v1, origen = M9.minimo_e060_por_cara(es_zapata=False, direccion="vertical",
                                         espesor=0.30, hm=2.4, lm=3.0)
    h1, _ = M9.minimo_e060_por_cara(es_zapata=False, direccion="horizontal",
                                    espesor=0.30, hm=2.4, lm=3.0)
    assert v0 == pytest.approx(225.0, abs=TOL_EXACTA)
    assert h0 == pytest.approx(300.0, abs=TOL_EXACTA)
    assert v1 == pytest.approx(0.0025 * 300000 / 2, abs=TOL_EXACTA)
    assert h1 == pytest.approx(0.0025 * 300000 / 2, abs=TOL_EXACTA)
    assert "11-32" in origen


# ===========================================================================
# 9. EL ARMADO DEL CABEZAL ENTERO, SU TABLA Y SUS AVISOS
# ===========================================================================

def test_el_armado_del_muro_de_tanteo_y_su_tabla(tanteo):
    a = M9.armado_del_cabezal(tanteo)
    assert isinstance(a, ArmadoDelCabezal)
    assert (a.tipo, a.regimen, a.sismico) == (M9.TIPO_VOLADIZO,
                                              REGIMEN_RESISTENCIA_K0, True)
    assert (a.fc_mpa, a.fy_mpa) == (21.0, 420.0)  # float-exacto: transcrito o declarado, no calculado
    assert [s.clave for s in a.secciones] == [SECCION_PANTALLA, SECCION_PUNTA,
                                              SECCION_TALON]
    assert a.cumple
    # la tabla: tres filas principales y tres de reparto
    posiciones = [f.posicion.split(":")[0] for f in a.tabla]
    assert posiciones == ["pantalla", "punta", "talon", "pantalla",
                          "pantalla", "zapata"]
    principal = a.tabla[0]
    assert principal.As_requerido == pytest.approx(
        CP["pantalla"]["As_resistencia"], abs=TOL_AS)
    assert principal.As_adoptado == pytest.approx(
        CP["pantalla"]["As_minimo_flexion"], abs=TOL_AS)
    assert principal.barra.texto == 'Ø 1/2" @ 0.200 m'
    for fila in a.tabla:
        assert fila.cumple
        assert fila.barra.As_provisto >= fila.As_adoptado - 1e-9
        assert fila.barra.espaciamiento <= fila.s_max + 1e-9
        assert fila.As_adoptado >= max(fila.As_requerido, fila.As_minimo) \
            - 1e-9
    reparto = a.tabla[3:]
    assert all(f.As_requerido == pytest.approx(0.0, abs=ABS_CERO)
               for f in reparto)
    # horizontal de la pantalla: 0.0020·300 000/2 = 300 (E.060) > 232.8
    horizontal = next(f for f in a.tabla if "horizontal" in f.posicion)
    assert horizontal.As_minimo == pytest.approx(300.0, abs=TOL_EXACTA)
    # longitudinal de la zapata: 0.0018·400 000/2 = 360
    longitudinal = next(f for f in a.tabla if "longitudinal" in f.posicion)
    assert longitudinal.As_minimo == pytest.approx(360.0, abs=TOL_EXACTA)


def test_el_armado_emite_un_paso_por_cada_cosa_que_un_revisor_pregunta(tanteo):
    a = M9.armado_del_cabezal(tanteo)
    fundamentos = [p.fundamento_id for p in a.pasos]
    assert fundamentos[0] == "F9.ARM_REGIMEN"
    # REESCRITO DECLARANDOLO (correcciones de T-7c, H4): el ultimo paso era
    # el del regimen de cortante de E.060; ahora le sigue la fila A8 de la
    # zapata (E.060 15.7), que es por cabezal y no por seccion.
    assert fundamentos[-2:] == ["F9.ARM_CORTANTE_PLANO",
                                "F9.ARM_PERALTE_ZAPATA"]
    for f in ("F9.ARM_ZAPATA", "F9.ARM_FLEXION", "F9.ARM_CORTANTE",
              "F9.ARM_MINIMO", "F9.ARM_ESPACIAMIENTO", "F9.ARM_E060",
              "F9.ARM_TABLA", "F9.ARM_FISURACION"):
        assert f in fundamentos, f
    assert fundamentos.count("F9.ARM_FLEXION") == 3
    # el paso del regimen dice los dos momentos y cual rige
    regimen = a.pasos[0]
    valores = {m.simbolo: m.valor for m in regimen.sustitucion}
    assert valores["K0"] == pytest.approx(0.5, abs=ABS_CERO)
    assert valores["M_u activo, pantalla"] == pytest.approx(
        CP["pantalla"]["activo"]["M_u"], abs=TOL)
    assert valores["M_u reposo, pantalla"] == pytest.approx(
        CP["pantalla"]["reposo"]["M_u"], abs=TOL)
    assert regimen.resultado.valor == pytest.approx(
        CP["pantalla"]["reposo"]["M_u"], abs=TOL)
    assert "QUE SE ESCALA Y QUE NO" in regimen.nota_del_proyecto
    # toda cita de todo paso existe en el registro
    reg = construir()
    for p in a.pasos:
        for cita_id in p.citas_textuales:
            reg.cita(cita_id)


def test_los_avisos_del_armado_dicen_lo_que_no_cubre_y_lo_que_supone(tanteo):
    a = M9.armado_del_cabezal(tanteo)
    texto = " | ".join(a.avisos)
    assert all(x.startswith("Cabezal de entrada de T-00") for x in a.avisos)
    assert len(a.avisos) == len(set(a.avisos))
    for fragmento in ("COTA MAS EXIGENTE", "5.6.7", "sin iterarla",
                      "h/2", "NO se contrasto con el minimo por durabilidad",
                      "zapata y las secciones intermedias de los aleros"):
        assert fragmento in texto, fragmento


def test_el_armado_avisa_cuando_cambia_entre_el_reposo_y_el_activo(tanteo):
    """
    PRECISIONES: «imprime al lado la solicitacion con K0, con aviso por
    `avisos()` cuando cambie el armado». En el muro de tanteo la pantalla
    queda en el minimo de flexion con los dos (1.33·M_u cambia): el aviso
    aparece si y solo si la barra propuesta es otra.
    """
    reposo = M9.armado_del_cabezal(tanteo)
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 REGIMEN_RESISTENCIA_CEDENTE)
    activo = M9.armado_del_cabezal(tanteo)
    for clave in (SECCION_PANTALLA, SECCION_PUNTA, SECCION_TALON):
        r, c = reposo.seccion(clave), activo.seccion(clave)
        assert r.As_adoptado >= c.As_adoptado - 1e-9
        cambia = r.barra.texto != c.barra.texto
        avisa = any(f"el armado de {clave} CAMBIA" in a
                    for a in reposo.avisos)
        assert cambia == avisa, (clave, r.barra.texto, c.barra.texto)
    # la pantalla del muro de tanteo SI cambia: 1/2" @ 0.20 frente a @ 0.30
    assert reposo.seccion(SECCION_PANTALLA).barra.texto == 'Ø 1/2" @ 0.200 m'
    assert activo.seccion(SECCION_PANTALLA).barra.espaciamiento > 0.20
    assert any("el armado de pantalla CAMBIA" in a for a in reposo.avisos)


def test_ensamblar_armado_arma_la_tabla_con_las_piezas_que_recibe(tanteo):
    """
    El servicio llama a `armar_elemento` por elemento y despues a
    `ensamblar_armado`: si un elemento no se pudo armar, la tabla sale con
    los demas y no inventa sus filas.
    """
    sol = M9.solicitaciones_de_resistencia(tanteo)
    zapata = M9.armar_elemento(tanteo, ELEMENTO_ZAPATA, sol)
    a = M9.ensamblar_armado(tanteo, zapata, sol)
    assert [s.clave for s in a.secciones] == [SECCION_PUNTA, SECCION_TALON]
    assert all(f.elemento == ELEMENTO_ZAPATA for f in a.tabla)
    assert len(a.tabla) == 3
    assert "F9.ARM_CORTANTE_PLANO" not in [p.fundamento_id for p in a.pasos]
    # y es la misma que arma `armado_del_cabezal` de una sola llamada
    entero = M9.armado_del_cabezal(tanteo)
    assert entero.seccion(SECCION_PUNTA).barra == a.seccion(
        SECCION_PUNTA).barra


def test_los_aleros_se_arman_en_su_arranque_con_su_espesor(tanteo):
    """
    PRECISIONES: los aleros no quedan en silencio. Seccion critica en el
    arranque, con el espesor del alero y la solicitacion de la pantalla; su
    zapata y sus secciones intermedias van diferidas con ficha y aviso.
    """
    aleros = Aleros(angulo_grados=45.0, angulo_largo_grados=45.0,
                    esviaje_grados=0.0, longitud_corto=2.5, longitud_largo=2.5,
                    altura_inicial=1.6, altura_final=0.4, espesor=0.25,
                    ancho_zapata=1.2, espesor_zapata=0.37)
    entorno = replace(tanteo, geometria=_geometria(aleros=aleros))
    a = M9.armado_del_cabezal(entorno)
    alero = a.seccion(SECCION_ALERO)
    pantalla = a.seccion(SECCION_PANTALLA)
    assert alero.elemento == ELEMENTO_ALEROS
    assert alero.espesor == pytest.approx(0.25, abs=ABS_CERO)
    assert alero.rige_flexion.M_u == pytest.approx(
        pantalla.rige_flexion.M_u, abs=ABS_CERO)
    assert alero.d < pantalla.d
    assert alero.As_resistencia > pantalla.As_resistencia
    assert any(f.elemento == ELEMENTO_ALEROS and "horizontal" in f.posicion
               for f in a.tabla)
    assert "T7C-04" in DECISIONES.read_text(encoding="utf-8")
    # sin aleros (cabezal recto) no hay seccion ni fila, y no es un error
    assert M9.armar_elemento(tanteo, ELEMENTO_ALEROS) == ()


def test_una_zapata_sin_punta_no_arma_la_punta(tanteo):
    g = _geometria(ancho_punta=0.0, ancho_talon=1.70)
    a = M9.armado_del_cabezal(replace(tanteo, geometria=g))
    assert [s.clave for s in a.secciones] == [SECCION_PANTALLA, SECCION_TALON]


def test_con_la_resultante_fuera_de_la_base_la_punta_no_se_inventa(tanteo):
    """
    El armado arma la geometria que recibe, pase o no su estabilidad; pero
    si en TODAS las combinaciones la resultante cae fuera de la base no hay
    presion de contacto que integrar: «metodo no evaluable», con el rotulo
    del cabezal.
    """
    g = _geometria(B=0.95, ancho_punta=0.60, ancho_talon=0.05)
    with pytest.raises(MetodoNoEvaluableError) as e:
        M9.solicitaciones_de_resistencia(replace(tanteo, geometria=g))
    assert e.value.rotulo == modelos.MOTIVO_METODO_NO_EVALUABLE_CABEZAL
    assert "fuera de la base" in e.value.motivo


def test_el_cabezal_de_gravedad_no_pasa_por_el_armado(tanteo):
    g = _geometria(tipo=M9.TIPO_GRAVEDAD)
    with pytest.raises(DatoInvalidoError):
        M9.armar_elemento(replace(tanteo, geometria=g), ELEMENTO_PANTALLA)
    with pytest.raises(DatoInvalidoError):
        M9.armar_elemento(tanteo, "dentellon")


def test_integrar_armado_suma_verificaciones_pasos_y_avisos_sin_tocar_lo_demas(
        tanteo):
    a = M9.armado_del_cabezal(tanteo)
    cabezal = modelos.CabezalDelPunto(
        id_punto="T-00", embocadura=SimpleNamespace(), entrada=tanteo.geometria,
        salida=tanteo.geometria, verificaciones=(), avisos=("previo",))
    nuevo = M9.integrar_armado(cabezal, [a])
    assert nuevo.armado == (a,)
    assert nuevo.verificaciones == a.verificaciones
    assert nuevo.pasos == a.pasos
    assert nuevo.avisos[0] == "previo"
    assert set(a.avisos) <= set(nuevo.avisos)
    assert nuevo.entrada is cabezal.entrada
    # sin armados no cambia nada salvo el campo vacio
    assert M9.integrar_armado(cabezal, []).verificaciones == ()


# ===========================================================================
# 10. LA ALTERNATIVA CICLOPEA
# ===========================================================================

CPC = CP_T7C_CICLOPEO


def _gravedad(**cambios):
    base = dict(CPC["geometria"], cota_desplante=100.0,
                cota_coronacion=101.75, id_punto="T-00", extremo="entrada",
                tipo=M9.TIPO_GRAVEDAD, longitud=3.0)
    base.update(cambios)
    return _entorno(geometria=GeometriaCabezal(**base), h=CPC["h"])


def test_dorado_de_las_acciones_sobre_una_seccion_del_cuerpo(tanteo):
    """Arranque y media altura del cuerpo, en reposo y en activo, a mano."""
    entorno = _gravedad()
    _, datos = M9.cargas_del_cabezal(entorno, EST)
    tol = CPC["tolerancia"]
    for rotulo in ("arranque", "media"):
        d = CPC[rotulo]
        a = M9.acciones_sobre_una_seccion(entorno, datos, z_seccion=d["z"],
                                          en_reposo=True)
        assert a["t"] == pytest.approx(d["t"], abs=ABS_CERO)
        assert a["W"] == pytest.approx(d["W"], abs=tol)
        assert a["x_W"] == pytest.approx(d["x_W"], abs=TOL_K)
        M_H = a["M_suelo"] + a["M_ls"] + a["M_agua"]
        assert M_H == pytest.approx(d["M_H_reposo"], abs=tol)
        e = (M_H - a["W"] * (a["t"] / 2 - a["x_W"])) / a["W"]
        assert e == pytest.approx(d["e_reposo"], abs=TOL_FINA)
    a = M9.acciones_sobre_una_seccion(entorno, datos, z_seccion=0.30,
                                      en_reposo=False)
    M_H = a["M_suelo"] + a["M_ls"]
    assert M_H == pytest.approx(CPC["arranque"]["M_H_activo"], abs=tol)
    assert (M_H - a["W"] * (a["t"] / 2 - a["x_W"])) / a["W"] == pytest.approx(
        CPC["arranque"]["e_activo"], abs=TOL_FINA)


@pytest.mark.parametrize("z", [-0.1, 0.29, 1.60, 2.0, float("nan")])
def test_una_seccion_fuera_del_cuerpo_del_muro_se_rechaza(tanteo, z):
    entorno = _gravedad()
    _, datos = M9.cargas_del_cabezal(entorno, EST)
    with pytest.raises(DatoInvalidoError):
        M9.acciones_sobre_una_seccion(entorno, datos, z_seccion=z,
                                      en_reposo=True)


def test_el_agua_del_relleno_entra_a_las_secciones_del_cuerpo(tanteo):
    """
    Sin drenaje (el valor de archivo) el relleno se llena de agua: la
    seccion la recibe como empuje hidrostatico y con el suelo sumergido por
    debajo del nivel.
    """
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    ca.establecer_valor_dinamico("peso_especifico_saturado_relleno_kn_m3",
                                 20.0)
    entorno = _gravedad()
    _, datos = M9.cargas_del_cabezal(entorno, EST)
    a = M9.acciones_sobre_una_seccion(entorno, datos, z_seccion=0.30,
                                      en_reposo=True)
    # 1.30 m de agua sobre la seccion: 9.81·1.69/2 = 8.28945 a 1.30/3 m
    assert a["H_agua"] == pytest.approx(9.81 * 1.3 ** 2 / 2, rel=REL_CALCULO)
    assert a["M_agua"] == pytest.approx(9.81 * 1.3 ** 3 / 6, rel=REL_CALCULO)
    # suelo sumergido: 0.5·(20 - 9.81)·1.69/2
    assert a["H_suelo"] == pytest.approx(0.5 * (20 - 9.81) * 1.69 / 2,
                                         rel=REL_CALCULO)


def test_el_cabezal_ciclopeo_del_dorado(tanteo):
    """
    C2 y C3 no cumplen (1.1770 > 0.0833; 0.2693 > 0.0667): con sobrecarga
    de trafico un muro esbelto de gravedad trabaja a traccion. C6, la
    traccion admisible de E.060, cumple (0.5422). Decide «tracciones_nulas».

    REESCRITO DECLARANDOLO (correcciones de T-7c, H5). C2 valia la
    excentricidad de servicio (0.6016 m); ahora el arranque es una junta de
    construccion (E.060 22.4.7, 'junta_arranque_cabezal_ciclopeo' de
    archivo) y C2 toma la mayor de la de servicio y la amplificada de
    E.060, 1.1770 m, calculada a mano en `CP_T7C_CICLOPEO`.
    """
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    assert a.tipo == M9.TIPO_GRAVEDAD and a.secciones == () and a.tabla == ()
    assert a.fy_mpa is None and not a.sismico
    codigos = [v.codigo for v in a.verificaciones]
    assert codigos == ["C1.base.e", "C2.cuerpo.e", "C3.cuerpo.e",
                       "C4.material.e", "C5.material.e", "C6.cuerpo.e"]
    c2, c3, c6 = _v(a, "C2.cuerpo.e"), _v(a, "C3.cuerpo.e"), _v(a,
                                                                "C6.cuerpo.e")
    assert c2.valor_obtenido == pytest.approx(CPC["junta"]["e_u_reposo"],
                                              abs=TOL_FINA)
    servicio = {m.simbolo: m.valor for m in c2.paso.sustitucion}
    assert servicio["e (servicio)"] == pytest.approx(
        CPC["arranque"]["e_reposo"], abs=TOL_FINA)
    assert c2.paso.umbral.cita_id == "E060.22.4.7#JUNTAS"
    assert c2.valor_admisible == pytest.approx(0.5 / 6, abs=ABS_CERO)
    assert c3.valor_obtenido == pytest.approx(CPC["media"]["e_reposo"],
                                              abs=TOL_FINA)
    assert c3.valor_admisible == pytest.approx(0.4 / 6, abs=ABS_CERO)
    assert c2.estado is EstadoDeVerificacion.NO_CUMPLE
    assert c3.estado is EstadoDeVerificacion.NO_CUMPLE
    assert c6.valor_obtenido == pytest.approx(
        CPC["e060"]["aprovechamiento"], abs=CPC["e060"]["tolerancia"])
    assert c6.estado is EstadoDeVerificacion.CUMPLE
    assert not a.cumple
    assert all(p.fundamento_id == "F9.CICLOPEO" for p in a.pasos)


def test_con_la_traccion_admisible_de_E060_decide_C6_y_las_nulas_informan(
        tanteo):
    """
    REESCRITO DECLARANDOLO (correcciones de T-7c, H5). Fijaba que con
    «traccion_admisible_e060» C2 pasaba a INDICADOR y el cabezal cumplia.
    Ya no: el arranque es una junta de construccion y E.060 22.4.7 prohibe
    la traccion a traves de ella, de modo que C2 DECIDE con cualquier
    criterio; solo con el vaciado monolitico declarado vuelve a informar.
    """
    ca.establecer_valor_dinamico("criterio_traccion_cabezal_ciclopeo",
                                 "traccion_admisible_e060")
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    assert _v(a, "C2.cuerpo.e").estado is EstadoDeVerificacion.NO_CUMPLE
    assert _v(a, "C3.cuerpo.e").estado is EstadoDeVerificacion.INDICADOR
    assert _v(a, "C6.cuerpo.e").estado is EstadoDeVerificacion.CUMPLE
    assert not a.cumple
    assert any("traccion_admisible_e060" in x for x in a.avisos)
    assert any("22.4.7" in x for x in a.avisos)
    ca.establecer_valor_dinamico("junta_arranque_cabezal_ciclopeo",
                                 "vaciado_monolitico")
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    c2 = _v(a, "C2.cuerpo.e")
    assert c2.estado is EstadoDeVerificacion.INDICADOR
    assert c2.valor_obtenido == pytest.approx(CPC["arranque"]["e_reposo"],
                                              abs=TOL_FINA)
    assert c2.paso.umbral.cita_id == "E060.22.6.3#TERCIO"
    assert a.cumple


def test_C1_la_base_en_el_tercio_central_con_cargas_de_servicio(tanteo):
    """
    El muro de tanteo de T-7b tomado como de gravedad: la mayor
    excentricidad de servicio es la del reposo sin el peso de la sobrecarga,
    0.306553 m <= B/6 = 0.33333 m.
    """
    g = _geometria(tipo=M9.TIPO_GRAVEDAD)
    a = M9.verificar_cabezal_ciclopeo(replace(tanteo, geometria=g))
    c1 = _v(a, "C1.base.e")
    assert c1.valor_obtenido == pytest.approx(
        CP_T7C_BASE_SERVICIO["e"], abs=CP_T7C_BASE_SERVICIO["tolerancia"])
    assert c1.valor_admisible == pytest.approx(
        CP_T7C_BASE_SERVICIO["limite"], abs=ABS_CERO)
    assert c1.estado is EstadoDeVerificacion.CUMPLE
    # con el regimen cedente la excentricidad es la del activo, mucho menor
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 REGIMEN_RESISTENCIA_CEDENTE)
    b = M9.verificar_cabezal_ciclopeo(replace(tanteo, geometria=g))
    assert _v(b, "C1.base.e").valor_obtenido == pytest.approx(
        CP_T7C_BASE_SERVICIO["e_activo"],
        abs=CP_T7C_BASE_SERVICIO["tolerancia"])


def test_un_cuerpo_mas_grueso_reduce_la_excentricidad(tanteo):
    """Coherencia ingenieril: mas masa en el cuerpo, menos traccion."""
    esbelto = M9.verificar_cabezal_ciclopeo(_gravedad())
    grueso = M9.verificar_cabezal_ciclopeo(_gravedad(
        espesor_base_muro=0.90, B=1.60, ancho_punta=0.40, ancho_talon=0.30))
    e1 = _v(esbelto, "C2.cuerpo.e")
    e2 = _v(grueso, "C2.cuerpo.e")
    assert e2.valor_obtenido / e2.valor_admisible < \
        e1.valor_obtenido / e1.valor_admisible


def test_C4_y_C5_los_limites_del_material_pueden_fallar(tanteo):
    """
    f'c de la matriz >= max(10 de E.060, 14 del EG-2013) y piedra <= 30 %.
    Fuera de la ventana del criterio: se impone con `con_valor`.
    """
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    assert _v(a, "C4.material.e").estado is EstadoDeVerificacion.CUMPLE
    assert _v(a, "C4.material.e").valor_admisible == pytest.approx(
        14.0, abs=ABS_CERO)
    assert _v(a, "C5.material.e").estado is EstadoDeVerificacion.CUMPLE
    with con_valor("concreto_ciclopeo_cabezal",
                   {"fc_matriz_mpa": 12.0, "fraccion_piedra": 0.35},
                   motivo="material fuera de los dos limites"):
        b = M9.verificar_cabezal_ciclopeo(_gravedad())
    assert _v(b, "C4.material.e").estado is EstadoDeVerificacion.NO_CUMPLE
    assert _v(b, "C5.material.e").estado is EstadoDeVerificacion.NO_CUMPLE
    # la resistencia de diseño del contraste no pasa de 10 MPa (22.10.2.3):
    # con 12 o con 14 MPa de matriz C6 da lo mismo
    assert _v(b, "C6.cuerpo.e").valor_obtenido == pytest.approx(
        _v(a, "C6.cuerpo.e").valor_obtenido, rel=REL_TRANSPORTE)


def test_el_ciclopeo_dice_lo_que_no_verifica(tanteo):
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    texto = " | ".join(a.avisos)
    assert "solo en la condicion ESTATICA" in texto
    assert "22.10.2.2" in texto
    # punta 0.30 y talon 0.20 con zapata de 0.30: vuela mas que 0.15
    assert "vuela" in texto


def test_armado_del_cabezal_despacha_por_el_tipo_de_T7a(tanteo):
    assert M9.armado_del_cabezal(_gravedad()).tipo == M9.TIPO_GRAVEDAD
    assert M9.armado_del_cabezal(tanteo).tipo == M9.TIPO_VOLADIZO


# ===========================================================================
# 11. DE PUNTA A PUNTA POR `servicio.correr`, Y LA CLI
# ===========================================================================
# Los MISMOS datos de prueba rotulados de T-7b (ningun valor es del
# proyecto): metodo de V5 por cota, evento extremo, angulo del relleno,
# suelo de fundacion friccionante, trasdos drenado, k_h reducido y freatico
# a 2.0 m bajo el terreno del cruce.

COTA_AFECTACION_DE_PRUEBA = 44.00
NF_DE_PRUEBA = "2.0"
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


def _externos(tmp_path, puntos=None, globales=None):
    ruta = tmp_path / "externos.json"
    ruta.write_text(json.dumps({"globales": globales or {},
                                "puntos": puntos or {}}), encoding="utf-8")
    return servicio.cargar_datos_externos(ruta, {})


def _csv_con_freatico(tmp_path, NF=NF_DE_PRUEBA):
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    assert FILA_A01 in texto
    ruta = tmp_path / "puntos.csv"
    ruta.write_text(texto.replace(
        FILA_A01, FILA_A01.replace(",SM,,,", f",SM,{NF},,")),
        encoding="utf-8")
    return ruta


def _correr_de_prueba(tmp_path, *, extra_a01=None, declaraciones=None,
                      alcance=servicio.ALCANCE_EXPEDIENTE):
    a01 = {"Q_evento_extremo_m3s": 1.3, "TW_evento_extremo_m": 0.5,
           "cota_afectacion_aguas_arriba_msnm": COTA_AFECTACION_DE_PRUEBA}
    a01.update(extra_a01 or {})
    ca.establecer_valor_dinamico("remanso_derecho_via", "cota_de_afectacion")
    externos = _externos(tmp_path, puntos={"A-01": a01},
                         globales={"luz_m": 3.0, "TW_m": 0.3})
    for clave, valor in dict(DECLARACIONES_DE_PRUEBA,
                             **(declaraciones or {})).items():
        ca.establecer_valor_dinamico(clave, valor)
    _declarar_sitio()
    informe = servicio.correr(_csv_con_freatico(tmp_path), externos,
                              alcance=alcance)
    return informe, next(p for p in informe.puntos if p.punto.id == "A-01")


@pytest.mark.lento
def test_A01_sale_de_la_Fase_9_con_sus_dos_cabezales_armados(tmp_path):
    """
    EL TEST DE PUNTA A PUNTA: a `--alcance expediente` A-01 dimensiona (Ø
    0.90 m, el de la linea base), y sus dos cabezales salen con el armado
    de sus tres elementos: ningun `NotImplementedError`, ningun bloqueo de
    armado, las filas A1 a A5 entre las verificaciones del cabezal y los
    avisos en `InformePunto.avisos()`.
    """
    _, a01 = _correr_de_prueba(tmp_path)
    assert a01.dimensionado
    assert a01.resultado.seccion.etiqueta() == "Ø 0.90 m"
    armados = a01.cabezal.armado
    assert [a.extremo for a in armados] == ["entrada", "salida"]
    for a in armados:
        assert a.tipo == M9.TIPO_VOLADIZO
        assert a.regimen == REGIMEN_RESISTENCIA_K0
        assert {s.clave for s in a.secciones} == {
            SECCION_PANTALLA, SECCION_PUNTA, SECCION_TALON, SECCION_ALERO}
        assert a.sismico
        for s in a.secciones:
            assert s.barra is not None, (a.extremo, s.clave)
            assert s.M_r >= s.rige_flexion.M_u - 1e-9
            assert s.V_r >= s.rige_cortante.V_u - 1e-9
            assert math.isfinite(s.As_adoptado) and s.As_adoptado > 0
        assert len(a.tabla) == 8
    assert not [b for b in a01.bloqueos if "armado" in b.etapa]
    codigos = {v.codigo for v in a01.cabezal.verificaciones}
    for ext in ("e", "s"):
        for clave in ("pantalla", "punta", "talon", "alero"):
            for n in ("A1", "A2", "A3", "A4", "A5", "A6"):
                assert f"{n}.{clave}.{ext}" in codigos
        assert f"A8.zapata.{ext}" in codigos
    # los avisos del armado llegan al punto, sin repetirse
    assert all(x in a01.avisos() for a in armados for x in a.avisos)
    assert len(a01.cabezal.avisos) == len(set(a01.cabezal.avisos))
    # y la estabilidad de T-7b sigue donde estaba, con el muro que cede
    assert len(a01.cabezal.estabilidad) == 4
    assert {e.regimen for e in a01.cabezal.estabilidad} == {"cedente"}


@pytest.mark.lento
def test_el_armado_no_itera_la_geometria_aunque_el_cabezal_no_pase(tmp_path):
    """
    Con la regla de T-7a el cabezal de A-01 NO pasa el deslizamiento del
    marco que rige (ficha T7B-09). T-7c arma esa geometria tal como llega
    -- la misma zapata -- y lo dice.
    """
    _, a01 = _correr_de_prueba(tmp_path)
    incumplidas = {v.codigo for v in a01.incumplidas()}
    assert "E3-LRFD.est.e" in incumplidas
    for a, g in zip(a01.cabezal.armado, a01.cabezal.geometrias):
        assert a.seccion(SECCION_PUNTA).espesor == pytest.approx(
            g.espesor_zapata, abs=ABS_CERO)
        assert a.seccion(SECCION_PANTALLA).espesor == pytest.approx(
            g.espesor_base_muro, abs=ABS_CERO)
        assert any("sin iterarla" in x for x in a.avisos)
    # REESCRITO DECLARANDOLO (correcciones de T-7c, H4 y H7). Fijaba que
    # NINGUNA fila del armado estaba entre las incumplidas. Ahora hay dos
    # por cabezal, y las dos son hallazgos, no defectos del armado: A8 (la
    # zapata de 0.37 m de T-7a no da 300 mm sobre su refuerzo inferior con
    # el recubrimiento con que se arma: E.060 15.7, que T-7a dejo a T-7c) y
    # A7 (con el analisis quimico DE PRUEBA del conftest -- cloruros -- el
    # f'c de 21 MPa queda bajo el minimo por durabilidad). Ninguna fila de
    # resistencia (A1 a A6) incumple.
    assert sorted(c for c in incumplidas if c.startswith("A")) == [
        "A7.concreto.e", "A7.concreto.s", "A8.zapata.e", "A8.zapata.s"]


@pytest.mark.lento
def test_a_perfil_el_armado_no_corre_y_ningun_diametro_se_mueve(tmp_path):
    _, a01 = _correr_de_prueba(tmp_path, alcance=servicio.ALCANCE_PERFIL)
    assert a01.dimensionado
    assert a01.resultado.seccion.etiqueta() == "Ø 0.90 m"
    assert a01.cabezal is None


@pytest.mark.lento
def test_el_tipo_gravedad_declarado_lleva_a_la_alternativa_ciclopea(tmp_path):
    """
    PRECISIONES: con D >= 0.90 m todo cabezal sale voladizo; la rama de
    gravedad se alcanza declarando el tipo en `cabezal_declarado`. Por esa
    puerta el cabezal NO se arma: lleva C1 a C6.
    """
    _, a01 = _correr_de_prueba(
        tmp_path, extra_a01={"cabezal_declarado": {
            "tipo": "gravedad_ciclopeo"}})
    assert a01.dimensionado
    armados = a01.cabezal.armado
    assert armados and all(a.tipo == M9.TIPO_GRAVEDAD for a in armados)
    for a in armados:
        assert a.secciones == () and a.tabla == ()
        assert [v.codigo.split(".")[0] for v in a.verificaciones] == [
            "C1", "C2", "C3", "C4", "C5", "C6"]
    codigos = {v.codigo for v in a01.cabezal.verificaciones}
    assert "C2.cuerpo.e" in codigos and "A1.pantalla.e" not in codigos


@pytest.mark.lento
def test_un_elemento_que_no_se_puede_evaluar_es_un_bloqueo_y_los_demas_siguen(
        tmp_path):
    """
    Una pantalla declarada de 0.45 m queda fuera del simplificado de
    cortante: su etapa deja un `Bloqueo` «metodo no evaluable» con el
    rotulo del armado, y la zapata y los aleros se arman igual.
    """
    _, a01 = _correr_de_prueba(
        tmp_path, extra_a01={"cabezal_declarado": {
            "espesor_base_muro_m": 0.45, "espesor_corona_m": 0.45}})
    bloqueos = [b for b in a01.bloqueos if "armado" in b.etapa]
    # un bloqueo por cabezal para la pantalla; y otro para los aleros, cuyo
    # espesor la regla de T-7a deriva del de la pantalla declarada
    assert sorted(b.etapa for b in bloqueos) == sorted(
        servicio.etapa_de_armado(ext, que)
        for ext in ("entrada", "salida") for que in ("pantalla", "aleros"))
    for b in bloqueos:
        assert b.tipo is TipoDeBloqueo.METODO_NO_EVALUABLE
        assert "5.7.3.4" in b.mensaje
    for a in a01.cabezal.armado:
        assert {s.clave for s in a.secciones} == {SECCION_PUNTA,
                                                  SECCION_TALON}
        assert a.tabla and all(f.elemento == ELEMENTO_ZAPATA
                               for f in a.tabla)


@pytest.mark.lento
def test_la_CLI_y_el_JSON_llevan_la_tabla_de_armado(tmp_path):
    informe, a01 = _correr_de_prueba(tmp_path)
    volcado = cli.informe_json(informe)
    punto = next(p for p in volcado["puntos"] if p["id"] == "A-01")
    armado = punto["cabezal"]["armado"]
    assert [a["extremo"] for a in armado] == ["entrada", "salida"]
    fila = armado[0]["tabla"][0]
    assert set(fila) >= {"elemento", "posicion", "As_requerido_mm2_m",
                         "As_minimo_mm2_m", "As_adoptado_mm2_m", "barra",
                         "espaciamiento_m", "gobierna"}
    assert armado[0]["regimen"] == REGIMEN_RESISTENCIA_K0
    assert armado[0]["secciones"][0]["M_u_cedente_kn_m_m"] <= \
        armado[0]["secciones"][0]["M_u_kn_m_m"]
    json.dumps(volcado)                         # serializable
    texto = "\n".join(cli._lineas_cabezal_del_punto(a01))
    assert "armado del cabezal de entrada (AASHTO LRFD Seccion 5" in texto
    assert "armado del cabezal de salida" in texto
    assert "pantalla: trasdos (contra el relleno), armadura vertical: " \
           "requerido" in texto
    assert "armado: no evaluado" not in texto


# ===========================================================================
# 12. LO QUE QUEDA ESCRITO
# ===========================================================================

@pytest.mark.parametrize("ficha", ["T7C-01", "T7C-02", "T7C-03", "T7C-04",
                                   "T7C-05", "T7C-06", "T7C-07", "T7C-08",
                                   "T7C-09", "T7C-10", "T7C-11", "T7C-12",
                                   "T7C-13"])
def test_las_fichas_de_T7c_estan_en_el_registro_de_decisiones(ficha):
    assert f"## {ficha} " in DECISIONES.read_text(encoding="utf-8")


def test_la_ficha_EXT_7_01_dice_que_la_ecuacion_ya_se_evalua():
    texto = DECISIONES.read_text(encoding="utf-8")
    inicio = texto.index("## EXT-7-01 ")
    ficha = texto[inicio:texto.index("\n## ", inicio + 5)]
    assert "T-7c" in ficha and "cuantia_vertical_ec_11_32" in ficha


# ===========================================================================
# 13. LO QUE LA MUTACION ENSEÑO
# ===========================================================================
# La primera vuelta del arnes de EXT-11 sobre lo nuevo de M9 dejo vivos 259
# de 1007 mutantes. Los que eran huecos reales se cierran aqui: los margenes
# de las cinco filas, la rama del contraste de E.060 que NO cumple, las
# fronteras de las reglas (16.0 in, 3·d_v, 18.0 in, la serie del catalogo),
# las entradas que no pueden ser, el talon «mas exacto» con y sin agua, la
# fila de recubrimiento de cada cara y el agua en el cuerpo del ciclopeo.

def test_los_margenes_de_las_cinco_filas_de_la_pantalla_del_dorado(tanteo):
    """
    El margen es admisible menos demanda, con el signo de «cuanto sobra»:
    47.4507 - 32.4311 = 15.0196 kN·m/m; 147.84 - 58.0349 = 89.8051 kN/m;
    645.0 - 584.2 = 60.8 mm2/m; 0.40 - 0.20 = 0.20 m; 1 - 0.7414 = 0.2586.
    """
    sol = M9.solicitaciones_de_resistencia(tanteo)
    (p,) = M9.armar_elemento(tanteo, ELEMENTO_PANTALLA, sol)
    d, e = CP["pantalla"], CP["e060_pantalla"]

    def margen(codigo):
        return _v(p, codigo).paso.veredicto.margen

    assert margen("A1.pantalla.e") == pytest.approx(
        d["M_r"] - d["reposo"]["M_u"], abs=TOL)
    assert margen("A2.pantalla.e") == pytest.approx(
        d["V_r"] - d["reposo"]["V_u"], abs=TOL_CM)
    assert margen("A3.pantalla.e") == pytest.approx(
        d["barra"][2] - d["As_minimo_flexion"], abs=TOL_AS)
    assert _v(p, "A3.pantalla.e").valor_admisible == pytest.approx(
        d["As_minimo_flexion"], abs=TOL_AS)
    assert margen("A4.pantalla.e") == pytest.approx(
        d["s_max"] - d["barra"][1], abs=TOL_EXACTA)
    assert margen("A5.pantalla.e") == pytest.approx(
        1 - e["aprovechamiento"], abs=e["tolerancia_uso"])
    assert _v(p, "A5.pantalla.e").valor_admisible == pytest.approx(
        1, abs=ABS_CERO)
    assert all(margen(c) > 0 for c in ("A1.pantalla.e", "A2.pantalla.e",
                                       "A3.pantalla.e", "A4.pantalla.e",
                                       "A5.pantalla.e"))
    # y la memoria imprime los operandos, no ceros de relleno
    a3 = {m.simbolo: m.valor for m in _v(p, "A3.pantalla.e").paso.sustitucion}
    assert a3["A_s,min flexion"] == pytest.approx(d["As_minimo_flexion"],
                                                  abs=TOL_AS)
    assert a3["A_s,resistencia"] == pytest.approx(d["As_resistencia"],
                                                  abs=TOL_AS)
    assert a3["A_s,min E.060"] == pytest.approx(d["As_e060"], abs=TOL_AS)
    assert a3["1.33·M_u"] == pytest.approx(1.33 * d["reposo"]["M_u"], abs=TOL)
    a1 = {m.simbolo: m.valor for m in _v(p, "A1.pantalla.e").paso.sustitucion}
    assert a1["epsilon_t"] == pytest.approx(d["epsilon_t"], abs=TOL_FINA)
    a5 = {m.simbolo: m.valor for m in _v(p, "A5.pantalla.e").paso.sustitucion}
    assert a5["A_s (E.060)"] == pytest.approx(e["As"], abs=TOL_AS)
    assert a5["epsilon_t (E.060)"] > cn.EPSILON_T_MIN_E060


def _contraste(M_e, V_e):
    return M9.diseno_flexion_corte(momento=30.0, cortante=40.0, espesor=0.30,
                                   contraste_e060=(M_e, V_e))


def test_el_contraste_de_E060_que_no_cumple_informa_y_no_decide():
    """
    La fila A5 tiene tres maneras de quedar por encima de 1 -- el acero, el
    cortante y la seccion que no alcanza -- y en las tres sale como
    INDICADOR con su aviso; las cuatro filas que deciden no se mueven.
    """
    bien = _contraste(20.0, 30.0)
    a5 = _v(bien, "A5.pantalla")
    assert a5.estado is EstadoDeVerificacion.CUMPLE
    assert not any("CONTRASTE" in x for x in bien.avisos)
    assert 0 < a5.valor_obtenido < 1
    assert a5.paso.veredicto.margen == pytest.approx(1 - a5.valor_obtenido,
                                                     abs=ABS_CERO)
    for M_e, V_e, que in ((80.0, 30.0, "acero"), (20.0, 400.0, "cortante"),
                          (5000.0, 30.0, "no alcanza")):
        mal = _contraste(M_e, V_e)
        a5 = _v(mal, "A5.pantalla")
        assert a5.estado is EstadoDeVerificacion.INDICADOR, que
        assert a5.cumple, que                    # un indicador no incumple
        assert any("CONTRASTE con E.060 no cumple" in x
                   for x in mal.avisos), que
        assert [_v(mal, c).estado for c in ("A1.pantalla", "A2.pantalla",
                                            "A3.pantalla", "A4.pantalla")] \
            == [EstadoDeVerificacion.CUMPLE] * 4, que
        assert mal.barra.texto == bien.barra.texto, que
    # el aprovechamiento es el MAYOR de los dos cocientes
    por_acero = _v(_contraste(80.0, 30.0), "A5.pantalla")
    assert por_acero.valor_obtenido == pytest.approx(
        _contraste(80.0, 30.0).As_e060 / bien.barra.As_provisto,
        rel=REL_CALCULO)
    assert por_acero.paso.veredicto.margen < 0
    por_corte = _contraste(20.0, 400.0)
    assert _v(por_corte, "A5.pantalla").valor_obtenido == pytest.approx(
        400.0 / por_corte.V_r_e060, rel=REL_CALCULO)
    # la seccion que no alcanza en el marco de E.060 no tiene acero que dar
    assert _contraste(5000.0, 30.0).As_e060 is None


def test_las_formulas_de_seccion_rechazan_lo_que_no_puede_ser():
    """Cero, negativo e infinito: las tres maneras de no ser una medida."""
    for malo in (0.0, -0.3, float("inf")):
        with pytest.raises(DatoInvalidoError):
            M9.momento_de_agrietamiento(espesor=malo, fc=21.0, gamma_3=0.67)
        with pytest.raises(DatoInvalidoError):
            M9.momento_de_agrietamiento(espesor=0.3, fc=malo, gamma_3=0.67)
        with pytest.raises(DatoInvalidoError):
            M9.acero_de_temperatura_aashto(ancho=malo, espesor=0.3, fy=420.0)
        with pytest.raises(DatoInvalidoError):
            M9.espaciamiento_maximo_del_armado(espesor=malo)
        with pytest.raises(DatoInvalidoError):
            M9.minimo_e060_por_cara(es_zapata=True, direccion="principal",
                                    espesor=malo)
        with pytest.raises(DatoInvalidoError):
            M9.diseno_flexion_corte(momento=10.0, cortante=10.0, espesor=malo)
    for malo in (-1.0, float("inf")):
        with pytest.raises(DatoInvalidoError):
            M9.resistencia_a_flexion(As=malo, d=0.2, fc=21.0, fy=420.0)
        with pytest.raises(DatoInvalidoError):
            M9.proponer_barra(As=malo, s_max=0.3,
                              catalogo=M9.catalogo_de_barras(), desde="1/2")
    for malo in (0.0, -0.1, float("inf")):
        with pytest.raises(DatoInvalidoError):
            M9.proponer_barra(As=100.0, s_max=malo,
                              catalogo=M9.catalogo_de_barras(), desde="1/2")
    # una solicitacion por combinacion que no es un numero es de la
    # aritmetica, no del dato
    for malo in (-1.0, float("inf")):
        with pytest.raises(LimiteNumericoError):
            M9.diseno_flexion_corte(espesor=0.3,
                                    solicitaciones=(_sol(M=malo),))
        with pytest.raises(LimiteNumericoError):
            M9.diseno_flexion_corte(espesor=0.3,
                                    solicitaciones=(_sol(V=malo),))


def test_sin_acero_y_sin_momento_las_formulas_dan_cero_y_no_se_detienen():
    """El cero es un valor legitimo: una cara sin traccion que armar."""
    sin_acero = M9.resistencia_a_flexion(As=0.0, d=0.2, fc=21.0, fy=420.0)
    assert sin_acero["epsilon_t"] is None
    assert sin_acero["M_n"] == pytest.approx(0.0, abs=ABS_CERO)
    # medio kN·m ya pide acero: el umbral de «sin traccion» es el cero
    assert M9.acero_por_flexion(M_u=0.5, d=0.2, fc=21.0, fy=420.0,
                                phi=0.9) > 0
    minima = M9.proponer_barra(As=0.0, s_max=0.3,
                               catalogo=M9.catalogo_de_barras(), desde="1/2")
    assert minima.designacion == "1/2"
    assert minima.espaciamiento == pytest.approx(0.3, abs=ABS_CERO)
    nula = M9.diseno_flexion_corte(momento=0.0, cortante=0.0, espesor=0.30)
    assert nula.As_resistencia == pytest.approx(0.0, abs=ABS_CERO)
    assert nula.As_minimo_flexion == pytest.approx(0.0, abs=ABS_CERO)
    assert "minimo constructivo" in nula.gobierna
    assert nula.barra is not None


def test_las_fronteras_del_procedimiento_simplificado_de_cortante():
    """
    AASHTO 5.7.3.4.1 dice «less than»: 16.0 in justas y un vuelo de 3·d_v
    justo quedan FUERA. Y el vuelo se compara con 3·d_v, que el motivo dice.
    """
    limite = cn.PERALTE_MAX_SIMPLIFICADO_AASHTO_SI
    assert M9.simplificado_permitido(es_zapata=False, espesor=limite,
                                     vuelo=None, d_v=0.3)[0] is False
    assert M9.simplificado_permitido(es_zapata=False, espesor=0.40,
                                     vuelo=None, d_v=0.3)[0] is True
    justo = M9.simplificado_permitido(es_zapata=True, espesor=0.50,
                                      vuelo=1.2, d_v=0.4)
    assert justo[0] is False and "3·d_v = 1.200 m" in justo[1]
    corto = M9.simplificado_permitido(es_zapata=True, espesor=0.50,
                                      vuelo=1.19, d_v=0.4)
    assert corto[0] is True and "3·d_v = 1.200 m" in corto[1]
    largo = M9.simplificado_permitido(es_zapata=True, espesor=0.50,
                                      vuelo=2.0, d_v=0.4)
    assert largo[0] is False


def test_las_fronteras_del_espaciamiento_maximo_y_de_la_serie_del_catalogo():
    """
    5.10.6: 12.0 in rige en muros y zapatas de MAS de 18.0 in. Con 18.0 in
    justas el tope sigue siendo 18.0 in (solo AASHTO). Y la serie del
    catalogo se recorre con «menor o igual»: el espaciamiento igual al
    maximo y el acero igual al pedido valen.
    """
    con_18, _ = M9.espaciamiento_maximo_del_armado(
        espesor=cn.TEMPERATURA_ESPESOR_GRUESO_M,
        regla=modelos.MINIMOS_SOLO_AASHTO)
    assert con_18 == pytest.approx(cn.ESPACIAMIENTO_MAX_ABSOLUTO_AASHTO_M,
                                   abs=ABS_CERO)
    grueso, origen = M9.espaciamiento_maximo_del_armado(
        espesor=0.50, regla=modelos.MINIMOS_SOLO_AASHTO)
    assert grueso == pytest.approx(cn.TEMPERATURA_S_MAX_GRUESO_M,
                                   abs=ABS_CERO)
    assert "5.10.6" in origen
    catalogo = M9.catalogo_de_barras()
    en_el_tope = M9.proponer_barra(As=100.0, s_max=0.25, catalogo=catalogo,
                                   desde="1/2")
    assert en_el_tope.espaciamiento == pytest.approx(0.25, abs=ABS_CERO)
    justo = M9.proponer_barra(As=129.0 / 0.2, s_max=0.30, catalogo=catalogo,
                              desde="1/2")
    assert justo.designacion == "1/2"
    assert justo.espaciamiento == pytest.approx(0.2, abs=ABS_CERO)


def test_la_fila_de_recubrimiento_de_cada_cara():
    """
    E.060 7.7.1: la cara inferior de la zapata se vacia contra el suelo; las
    demas van en contacto con el relleno y su fila la parte la barra de 3/4".
    """
    catalogo = M9.catalogo_de_barras()
    assert catalogo["diametro_grueso"] == pytest.approx(19.1, abs=ABS_CERO)
    assert M9._condicion_de_recubrimiento(SECCION_PUNTA, 12.7, catalogo) \
        == M9.CONDICION_RECUBRIMIENTO_ZAPATA
    for clave in (SECCION_PANTALLA, SECCION_TALON, SECCION_ALERO):
        assert M9._condicion_de_recubrimiento(clave, 15.9, catalogo) \
            == M9.CONDICION_RECUBRIMIENTO_BARRA_FINA
        assert M9._condicion_de_recubrimiento(clave, 19.1, catalogo) \
            == M9.CONDICION_RECUBRIMIENTO_BARRA_GRUESA
        assert M9._condicion_de_recubrimiento(clave, 25.4, catalogo) \
            == M9.CONDICION_RECUBRIMIENTO_BARRA_GRUESA


def test_la_ec_11_32_solo_se_anuncia_en_la_cuantia_vertical():
    ca.establecer_valor_dinamico("regimen_cortante_muro_e060_art_11_10_2",
                                 cn.REGIMEN_CORTANTE_EN_EL_PLANO)
    _, vertical = M9.minimo_e060_por_cara(
        es_zapata=False, direccion="vertical", espesor=0.30, hm=2.4, lm=3.0)
    _, horizontal = M9.minimo_e060_por_cara(
        es_zapata=False, direccion="horizontal", espesor=0.30, hm=2.4, lm=3.0)
    assert "ec. 11-32 evaluada" in vertical
    assert "ec. 11-32 evaluada" not in horizontal


def test_la_carga_lineal_sobre_un_tramo_interior_a_mano():
    """
    Presion de 10 kPa en x = 0 a 30 kPa en x = 2 m, sobre el tramo [1, 2]
    y respecto de x = 1: extremos 20 y 30 kPa, F = 25 kN/m; centro de
    gravedad a (20 + 2·30)/(3·50) = 0.53333 m del origen del tramo, M =
    13.3333 kN·m/m. Y fuera del tramo cargado no hay nada.
    """
    F, M = M9._carga_lineal_sobre_un_tramo(0.0, 2.0, 10.0, 30.0, 1.0, 2.0,
                                           1.0)
    assert F == pytest.approx(25.0, abs=ABS_CERO)
    assert M == pytest.approx(25.0 * 80.0 / 150.0, abs=ABS_CERO)
    for a, b in ((2.0, 3.0), (-1.0, 0.0), (1.5, 1.5)):
        fuera = M9._carga_lineal_sobre_un_tramo(0.0, 2.0, 10.0, 30.0, a, b,
                                                1.0)
        assert fuera[0] == pytest.approx(0.0, abs=ABS_CERO)
        assert fuera[1] == pytest.approx(0.0, abs=ABS_CERO)
    sin_tramo = M9._carga_lineal_sobre_un_tramo(1.0, 1.0, 10.0, 30.0, 0.0,
                                                2.0, 0.0)
    assert sin_tramo[0] == pytest.approx(0.0, abs=ABS_CERO)
    assert sin_tramo[1] == pytest.approx(0.0, abs=ABS_CERO)


def test_el_talon_mas_exacto_descuenta_la_reaccion_y_la_subpresion(tanteo):
    """
    El «metodo mas exacto» de AASHTO 11.6.1.2 -- el que alimenta el
    contraste de E.060 15.4.1 y la nota del talon -- es el peso entero MENOS
    la reaccion del terreno y MENOS la subpresion que alcanzan al talon. Y
    la presion en la punta es la del borde cargado, o cero si el triangulo
    arranca del talon.
    """
    g = tanteo.geometria
    cargas, datos = M9.cargas_del_cabezal(tanteo, EST)
    combos = M9.combinaciones_de_estabilidad(cargas, datos, EST, g.B)
    maximos = next(c for c in combos if c.nombre == "Resistencia I (maximos)")
    z = M9.solicitaciones_de_la_zapata(g, cargas, maximos, datos)
    presion = M9.presion_de_contacto_lineal(maximos)
    x_t, talon = datos["x_trasdos"], datos["talon"]
    V_peso, M_peso = M9._talon_con_el_peso_entero(g, cargas, maximos, datos)
    F_t, M_t = M9._carga_lineal_sobre_un_tramo(
        presion["x0"], presion["x1"], presion["s0"], presion["s1"], x_t, g.B,
        x_t)
    assert F_t > 0 and M_t > 0
    assert z["talon"][0] == pytest.approx(V_peso - F_t, rel=REL_CALCULO)
    assert z["talon"][1] == pytest.approx(M_peso - M_t, rel=REL_CALCULO)
    assert z["talon"][1] < M_peso                  # el exacto pide menos
    assert z["sigma_punta"] == pytest.approx(presion["s0"], rel=REL_CALCULO)
    assert z["sigma_punta"] > 0
    hacia_el_talon = replace(maximos, M_estabilizante=maximos.N * 1.75,
                             M_volcante=0.0)
    assert M9.presion_de_contacto_lineal(hacia_el_talon)["forma"] \
        == "triangulo desde el talon"
    assert M9.solicitaciones_de_la_zapata(
        g, cargas, hacia_el_talon, datos)["sigma_punta"] == pytest.approx(
            0.0, abs=ABS_CERO)
    # con 1.0 m de agua sobre la base: 9.81 kPa uniformes tambien bajo el
    # talon, hacia arriba
    ca.establecer_valor_dinamico("peso_especifico_saturado_relleno_kn_m3",
                                 20.0)
    mojado = replace(tanteo, cota_freatico=101.0)
    cargas_w, datos_w = M9.cargas_del_cabezal(mojado, EST)
    combos_w = M9.combinaciones_de_estabilidad(cargas_w, datos_w, EST, g.B)
    max_w = next(c for c in combos_w if c.nombre == "Resistencia I (maximos)")
    con = M9.solicitaciones_de_la_zapata(g, cargas_w, max_w, datos_w)
    presion_w = M9.presion_de_contacto_lineal(max_w)
    Vw, Mw = M9._talon_con_el_peso_entero(g, cargas_w, max_w, datos_w)
    Fw, MFw = M9._carga_lineal_sobre_un_tramo(
        presion_w["x0"], presion_w["x1"], presion_w["s0"], presion_w["s1"],
        x_t, g.B, x_t)
    f_u = max_w.factor_de(M9.C_WA_U)
    assert f_u > 0
    assert con["talon"][0] == pytest.approx(Vw - Fw - f_u * 9.81 * talon,
                                            rel=REL_CALCULO)
    assert con["talon"][1] == pytest.approx(
        Mw - MFw - f_u * 9.81 * talon ** 2 / 2, rel=REL_CALCULO)


def test_el_contraste_E060_del_talon_va_con_la_reaccion_del_terreno(tanteo):
    """
    E.060 15.4.1: el momento de la zapata es el de las fuerzas a un lado del
    plano, con la reaccion. El contraste del talon no puede ser mayor que el
    del peso entero con las mismas cargas, y es positivo.
    """
    sol = M9.solicitaciones_de_resistencia(tanteo)
    M_e, V_e = sol["e060"][SECCION_TALON]
    g = tanteo.geometria
    cargas, datos = M9.cargas_del_cabezal(tanteo, EST)
    mayor_M, mayor_V = 0.0, 0.0
    for juego in (cargas, M9.cargas_en_reposo(cargas, datos)):
        for combo in M9._combinaciones_e060(juego, g.B):
            z = M9.solicitaciones_de_la_zapata(g, juego, combo, datos)
            if z is not None:
                mayor_M = max(mayor_M, z["talon"][1])
                mayor_V = max(mayor_V, abs(z["talon"][0]))
    assert M_e == pytest.approx(mayor_M, rel=REL_CALCULO)
    assert V_e == pytest.approx(mayor_V, rel=REL_CALCULO)
    assert M_e > 0 and V_e > 0
    entero = max(M9._talon_con_el_peso_entero(g, juego, combo, datos)[1]
                 for juego in (cargas, M9.cargas_en_reposo(cargas, datos))
                 for combo in M9._combinaciones_e060(juego, g.B))
    assert M_e < entero


def test_el_paso_del_regimen_imprime_el_cociente_con_que_escala(tanteo):
    """El cociente K0 / K_A del paso es el de los dos coeficientes del armado."""
    a = M9.armado_del_cabezal(tanteo)
    regimen = next(p for p in a.pasos if p.codigo == "9.4.r.e")
    por = {m.simbolo: m for m in regimen.sustitucion}
    assert por["K0 / K_A"].valor == pytest.approx(a.K0 / a.K_A,
                                                  rel=REL_CALCULO)
    assert por["K0 / K_A"].valor > 1
    assert por["M_u reposo, pantalla"].valor == pytest.approx(
        CP["pantalla"]["reposo"]["M_u"], abs=TOL)
    assert por["M_u activo, pantalla"].valor == pytest.approx(
        CP["pantalla"]["activo"]["M_u"], abs=TOL)
    assert por["K0"].valor == pytest.approx(CP["K0"], abs=ABS_CERO)
    assert regimen.resultado.procedencia == "el mayor de los dos"
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 REGIMEN_RESISTENCIA_CEDENTE)
    b = M9.armado_del_cabezal(tanteo)
    cedente = next(p for p in b.pasos if p.codigo == "9.4.r.e")
    assert cedente.resultado.procedencia == "el del muro que cede"


def test_el_aviso_del_cortante_en_el_plano_dice_la_esbeltez_del_muro(tanteo):
    """hm / lm = altura total / longitud del cabezal, no su producto."""
    ca.establecer_valor_dinamico("regimen_cortante_muro_e060_art_11_10_2",
                                 cn.REGIMEN_CORTANTE_EN_EL_PLANO)
    a = M9.armado_del_cabezal(tanteo)
    hm, lm = M9._altura_y_longitud(tanteo)
    aviso = next(x for x in a.avisos if "en el plano" in x)
    assert f"hm/lm = {hm / lm:.2f}" in aviso
    assert f"{hm / lm:.2f}" != f"{hm * lm:.2f}"
    plano = next(p for p in a.pasos if p.codigo == "9.4.p.e")
    assert plano.resultado.procedencia == "ec. (11-32) evaluada"
    ca.quitar_valor_dinamico("regimen_cortante_muro_e060_art_11_10_2")
    b = M9.armado_del_cabezal(tanteo)
    assert not any("en el plano»" in x for x in b.avisos)
    perpendicular = next(p for p in b.pasos if p.codigo == "9.4.p.e")
    assert "14.3.1" in perpendicular.resultado.procedencia


def test_el_fc_de_calculo_se_contrasta_con_el_minimo_por_durabilidad(tanteo):
    """
    Con el analisis quimico declarado (aqui, el de prueba del conftest de la
    suite: cloruros) el f'c de calculo de 21 MPa queda por debajo del minimo
    por durabilidad y el armado lo dice; con un f'c que lo alcanza, no.

    REESCRITO DECLARANDOLO (correcciones de T-7c, H7). Fijaba un AVISO «es
    MENOR que el minimo» y nada mas: la justificacion de 'fc_cabezal_mpa'
    hablaba de una verificacion A6 que no existia. Ahora es la fila A7, que
    DECIDE cuando el dato existe (NO CUMPLE) y sale tambien por los avisos;
    con un f'c que alcanza el minimo, cumple.
    """
    import conftest
    ca.establecer_valor_dinamico(conftest.CLAVE_EXPOSICION_QUIMICA,
                                 conftest.EXPOSICION_QUIMICA_DE_PRUEBA)
    ca.establecer_valor_dinamico(conftest.CLAVE_CATEGORIA_REFUERZO,
                                 conftest.CATEGORIA_REFUERZO_DE_PRUEBA)
    requisitos = M9.requisitos_durabilidad_concreto()
    assert requisitos.fc_min_MPa > ca.valor("fc_cabezal_mpa")
    a = M9.armado_del_cabezal(tanteo)
    a7 = _v(a, "A7.concreto.e")
    assert a7.estado is EstadoDeVerificacion.NO_CUMPLE
    assert a7.valor_obtenido == pytest.approx(21.0, abs=ABS_CERO)
    assert a7.valor_admisible == pytest.approx(requisitos.fc_min_MPa,
                                               abs=ABS_CERO)
    assert a7.paso.fundamento_id == "F9.ARM_DURABILIDAD"
    assert any(x.startswith("Cabezal de entrada de T-00: A7") for x in
               a.avisos)
    assert not any("NO se contrasto" in x for x in a.avisos)
    assert not a.cumple
    ca.establecer_valor_dinamico("fc_cabezal_mpa", 35.0)
    b = M9.armado_del_cabezal(tanteo)
    assert _v(b, "A7.concreto.e").estado is EstadoDeVerificacion.CUMPLE
    assert not any(": A7" in x for x in b.avisos)
    # sin el dato no hay fila, y el aviso lo dice
    _sin_datos_de_exposicion()
    c = M9.armado_del_cabezal(tanteo)
    assert not any(v.codigo.startswith("A7") for v in c.verificaciones)
    assert any("NO se contrasto" in x and "A7" in x for x in c.avisos)


def test_el_agua_entra_con_su_signo_a_las_filas_del_ciclopeo(tanteo):
    """
    Con el relleno lleno de agua (sin drenaje) el empuje hidrostatico SUMA
    al momento que vuelca la seccion: la excentricidad de C2 es la de las
    acciones de la seccion con el agua sumando, y el contraste de E.060 lleva
    el agua con el factor del empuje (1,7) en el momento y en el cortante.

    REESCRITO DECLARANDOLO (correcciones de T-7c, H5): C2 es la junta de
    construccion del arranque y toma la MAYOR de la excentricidad de
    servicio y la amplificada de E.060 (M_u / P_u, el agua con 1,7); C3,
    solo la de servicio, como antes.
    """
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    ca.establecer_valor_dinamico("peso_especifico_saturado_relleno_kn_m3",
                                 20.0)
    entorno = _gravedad()
    _, datos = M9.cargas_del_cabezal(entorno, EST)
    armado = M9.verificar_cabezal_ciclopeo(entorno)
    f_t = 0.5 * 0.42 * math.sqrt(10.0) * 1000.0         # kPa (22-7, phi 0,5)
    usos, excentricidades, cortantes = [], {}, []
    for z, codigo in ((0.30, "C2.cuerpo.e"), (0.30 + 1.30 / 2,
                                              "C3.cuerpo.e")):
        peor, peor_u = 0.0, 0.0
        for reposo in (False, True):
            a = M9.acciones_sobre_una_seccion(entorno, datos, z_seccion=z,
                                              en_reposo=reposo)
            assert a["M_agua"] > 0 and a["H_agua"] > 0
            brazo = a["t"] / 2 - a["x_W"]
            e = (a["M_suelo"] + a["M_ls"] + a["M_agua"]
                 - a["W"] * brazo) / a["W"]
            peor = max(peor, abs(e))
            t_r = a["t"] - 0.05
            P_u = 0.9 * a["W"]
            M_u = (1.7 * (a["M_suelo"] + a["M_agua"]) + 1.7 * a["M_ls"]
                   - P_u * brazo)
            V_u = 1.7 * (a["H_suelo"] + a["H_agua"]) + 1.7 * a["H_ls"]
            peor_u = max(peor_u, abs(M_u / P_u))
            sigma = abs(M_u) / (t_r ** 2 / 6) - P_u / t_r
            V_r = 0.5 * 0.11 * math.sqrt(10.0) * 1000.0 * t_r
            usos.append(max(sigma / f_t, V_u / V_r))
            cortantes.append(f"cortante {V_u:.1f} frente a {V_r:.1f} kN/m")
        excentricidades[codigo] = (max(peor, peor_u)
                                   if codigo.startswith("C2") else peor)
    for codigo, e in excentricidades.items():
        assert _v(armado, codigo).valor_obtenido == pytest.approx(
            e, rel=REL_CALCULO), codigo
        assert _v(armado, codigo).paso.veredicto.margen == pytest.approx(
            _v(armado, codigo).valor_admisible - e, rel=REL_CALCULO), codigo
    c6 = _v(armado, "C6.cuerpo.e")
    assert c6.valor_obtenido == pytest.approx(max(usos), rel=REL_CALCULO)
    assert c6.paso.veredicto.margen == pytest.approx(1 - max(usos),
                                                     rel=REL_CALCULO)
    assert c6.valor_admisible == pytest.approx(1, abs=ABS_CERO)
    # el cortante de cada seccion y de cada empuje, con su resistencia: la
    # traccion gobierna el cociente, y el cortante se lee de la memoria
    assert len(c6.paso.sustitucion) == len(cortantes)
    for magnitud, texto in zip(c6.paso.sustitucion, cortantes, strict=True):
        assert texto in magnitud.procedencia, magnitud.simbolo


def test_el_freatico_a_media_altura_parte_el_diagrama_en_tres(tanteo):
    """
    Agua hasta 0.90 m sobre la base y seccion a 0.30 m: sobre la seccion
    quedan 0.60 m sumergidos y 0.70 m secos (altura del diagrama 1.30 m). El
    empuje del suelo es el triangulo seco, el rectangulo que ese triangulo
    deja sobre la parte mojada, y el triangulo sumergido, cada uno con su
    brazo: 0.60 + 0.70/3, 0.60/2 y 0.60/3.
    """
    ca.establecer_valor_dinamico("peso_especifico_saturado_relleno_kn_m3",
                                 20.0)
    entorno = replace(_gravedad(), cota_freatico=100.9)
    _, datos = M9.cargas_del_cabezal(entorno, EST)
    a = M9.acciones_sobre_una_seccion(entorno, datos, z_seccion=0.30,
                                      en_reposo=True)
    K, gamma = datos["K0"], datos["gamma"]
    seco = K * gamma * 0.7 ** 2 / 2
    sobre_lo_mojado = K * gamma * 0.7 * 0.6
    sumergido = K * (20.0 - 9.81) * 0.6 ** 2 / 2
    assert a["altura"] == pytest.approx(1.3, abs=ABS_CERO)
    assert a["H_suelo"] == pytest.approx(seco + sobre_lo_mojado + sumergido,
                                         rel=REL_CALCULO)
    assert a["M_suelo"] == pytest.approx(
        seco * (0.6 + 0.7 / 3) + sobre_lo_mojado * 0.3 + sumergido * 0.2,
        rel=REL_CALCULO)
    assert a["H_agua"] == pytest.approx(9.81 * 0.6 ** 2 / 2, rel=REL_CALCULO)
    assert a["M_agua"] == pytest.approx(9.81 * 0.6 ** 3 / 6, rel=REL_CALCULO)


def test_el_peso_de_un_cuerpo_de_espesor_constante_cae_en_su_centro(tanteo):
    """Con corona y base iguales el trapecio es un rectangulo: x_W = t/2."""
    recto = _gravedad(espesor_base_muro=0.30, B=0.80)
    _, datos = M9.cargas_del_cabezal(recto, EST)
    a = M9.acciones_sobre_una_seccion(recto, datos, z_seccion=0.30,
                                      en_reposo=True)
    assert a["t"] == pytest.approx(0.30, abs=ABS_CERO)
    assert a["x_W"] == pytest.approx(0.15, abs=ABS_CERO)
    assert a["W"] == pytest.approx(datos["gamma_c"] * 0.30 * 1.30,
                                   rel=REL_CALCULO)


def test_cada_combinacion_de_la_pantalla_lleva_su_propia_solicitacion(tanteo):
    """
    La solicitacion del muro que cede de cada combinacion es la que el
    ensamble de T-7b entrega para esa combinacion y ese elemento. En la
    pantalla las dos Resistencia I coinciden: «minimos» y «maximos» difieren
    en las cargas verticales, y la pantalla solo recibe las horizontales,
    que llevan el mismo factor en las dos. (Por eso la mutacion no distingue
    la busqueda por combinacion en la pantalla: es equivalente.)
    """
    ensamble = M9.ensamble_estabilidad(tanteo, EST)
    sol = M9.solicitaciones_de_resistencia(tanteo)
    vistos = {}
    for nombre in ("Resistencia I (maximos)", "Resistencia I (minimos)"):
        de_t7b = next(s for s in ensamble.solicitaciones
                      if s.elemento == ELEMENTO_PANTALLA
                      and s.combinacion == nombre)
        mia = _de(sol, SECCION_PANTALLA, nombre)
        assert mia.M_u_cedente == pytest.approx(de_t7b.M_u,
                                                rel=REL_TRANSPORTE)
        assert mia.V_u_cedente == pytest.approx(abs(de_t7b.V_u),
                                                rel=REL_TRANSPORTE)
        vistos[nombre] = mia
    assert vistos["Resistencia I (minimos)"].M_u_cedente == pytest.approx(
        vistos["Resistencia I (maximos)"].M_u_cedente, rel=REL_TRANSPORTE)
    assert vistos["Resistencia I (minimos)"].M_u_reposo == pytest.approx(
        vistos["Resistencia I (maximos)"].M_u_reposo, rel=REL_TRANSPORTE)


def test_rige_el_cortante_que_mas_resistencia_nominal_pide():
    """
    Con factores de resistencia distintos no rige el mayor V_u sino el mayor
    V_u / phi: 90 / 0.90 = 100 pide mas que 95 / 1.00 = 95. Y en flexion lo
    mismo: 45 / 0.90 = 50 frente a 48 / 1.00 = 48.
    """
    estatica = _sol(M=45.0, V=90.0, phi=0.9, nombre="estatica")
    sismica = _sol(M=48.0, V=95.0, phi=1.0, condicion=SIS, nombre="sismica")
    seccion = M9.diseno_flexion_corte(espesor=0.30,
                                      solicitaciones=(sismica, estatica))
    assert seccion.rige_cortante.combinacion == "estatica"
    assert seccion.rige_flexion.combinacion == "estatica"
    assert _v(seccion, "A2.pantalla").valor_obtenido == pytest.approx(
        90.0, abs=ABS_CERO)
    assert seccion.V_r == pytest.approx(0.9 * seccion.V_c, rel=REL_CALCULO)


def test_los_margenes_de_las_filas_del_ciclopeo_del_dorado(tanteo):
    """
    C1: B/6 - e; C4: f'c de la matriz menos su minimo (14 - 14 = 0, cumple
    justo); C5: 0.30 - 0.30 = 0, cumple justo. Y con el material justo por
    debajo del limite, no cumplen.
    """
    g = _geometria(tipo=M9.TIPO_GRAVEDAD)
    a = M9.verificar_cabezal_ciclopeo(replace(tanteo, geometria=g))
    c1 = _v(a, "C1.base.e")
    assert c1.paso.veredicto.margen == pytest.approx(
        CP_T7C_BASE_SERVICIO["limite"] - CP_T7C_BASE_SERVICIO["e"],
        abs=CP_T7C_BASE_SERVICIO["tolerancia"])
    assert c1.paso.veredicto.margen > 0
    c4, c5 = _v(a, "C4.material.e"), _v(a, "C5.material.e")
    assert c4.estado is EstadoDeVerificacion.CUMPLE
    assert c5.estado is EstadoDeVerificacion.CUMPLE
    assert c4.paso.veredicto.margen == pytest.approx(0.0, abs=ABS_CERO)
    assert c5.paso.veredicto.margen == pytest.approx(0.0, abs=ABS_CERO)
    with con_valor("concreto_ciclopeo_cabezal",
                   {"fc_matriz_mpa": 20.0, "fraccion_piedra": 0.10},
                   motivo="material holgado en los dos limites"):
        b = M9.verificar_cabezal_ciclopeo(replace(tanteo, geometria=g))
    assert _v(b, "C4.material.e").paso.veredicto.margen == pytest.approx(
        6.0, abs=ABS_CERO)
    assert _v(b, "C5.material.e").paso.veredicto.margen == pytest.approx(
        0.20, abs=ABS_CERO)


# ===========================================================================
# 14. LAS CORRECCIONES DE LA AUDITORIA ADVERSARIAL DE T-7c (H1 a H12 y las
#     preguntas del informe de la FASE A que el orquestador resolvio)
# ===========================================================================
# NO SE ESCRIBIERON EN ROJO CON `xfail(strict=True)` ANTES DEL CODIGO: el
# rojo se MIDIO con este archivo final contra el arbol de la FASE A
# (`f50edbe`), y se declara en el informe del cierre y en la ficha T7C-08.

def test_H1_el_diagrama_bajo_el_arranque_no_resta_momento_a_la_pantalla(
        tanteo):
    """
    El caso que la formula anterior anulaba: con h <= 3·e_z la resultante
    del triangulo de suelo cae bajo el arranque y el momento salia CERO. Con
    el diagrama integrado sobre el arranque, la pantalla de un muro bajo
    (h = 1.00 m, e_z = 0.40 m) lleva K·gamma·0.60²/2 a 0.20 m. A mano, con
    el activo de la cuña (K_A = 0.297260, delta = 20.1 grados):
        P = 0.297260·18·0.60²/2·cos 20.1° = 0.963122·0.939094 = 0.904463
        M = 0.904463·0.60/3 = 0.180893 kN·m/m (sin factorar)
    """
    ca.establecer_valor_dinamico("h_eq_bajo_altura_tabulada", "primera_fila")
    g = _geometria(H=0.60, cota_coronacion=101.00)
    entorno = replace(tanteo, geometria=g, cota_relleno=101.00,
                      cota_borde_plataforma=101.00)
    cargas, datos = M9.cargas_del_cabezal(entorno, EST)
    assert datos["h"] == pytest.approx(1.00, abs=ABS_CERO)
    arranque = M9.empujes_sobre_el_arranque(cargas, datos, 0.40)
    H, M = arranque["EH.h"]
    assert H == pytest.approx(0.297260 * 18 * 0.60 ** 2 / 2
                              * math.cos(math.radians(20.1)), abs=TOL_MM)
    assert M == pytest.approx(H * 0.60 / 3, rel=REL_CALCULO)
    assert M > 0
    # la resultante entera con su brazo desde el arranque daba 0: su altura
    # (h/3 = 0.333 m) queda bajo el arranque (0.40 m)
    eh = next(c for c in cargas if c.codigo == "EH.h")
    assert eh.z < 0.40
    # y el diagrama del suelo, por unidad de coeficiente, sobre el arranque
    P, M_u = M9.diagrama_del_suelo_sobre(datos, 0.40)
    assert P == pytest.approx(18 * 0.60 ** 2 / 2, rel=REL_CALCULO)
    assert M_u == pytest.approx(P * 0.60 / 3, rel=REL_CALCULO)


def test_H1_el_agua_y_la_inercia_sobre_el_arranque(tanteo):
    """
    El agua del relleno (sin drenaje, hasta la superficie: h_w = 2.40 m)
    empuja la pantalla con su triangulo por encima del arranque, 9.81·2.00²/2
    = 19.62 kN/m a 2.00/3; y la inercia que carga la pantalla es la de la
    PANTALLA sola, k_h·W_p = 0.25·14.136 = 3.534 kN/m a 1.00 m (la de la
    zapata no la carga).
    """
    ca.establecer_valor_dinamico("drenaje_trasdos", "sin_drenaje")
    ca.establecer_valor_dinamico("peso_especifico_saturado_relleno_kn_m3",
                                 20.0)
    cargas, datos = M9.cargas_del_cabezal(tanteo, EST)
    H, M = M9.empujes_sobre_el_arranque(cargas, datos, 0.40)["WA.h"]
    assert H == pytest.approx(9.81 * 2.00 ** 2 / 2, abs=TOL_MM)
    assert M == pytest.approx(H * 2.00 / 3, rel=REL_CALCULO)
    ca.establecer_valor_dinamico("drenaje_trasdos", "drenado")
    cargas, datos = M9.cargas_del_cabezal(tanteo, SIS)
    H, M = M9.empujes_sobre_el_arranque(cargas, datos, 0.40)["EQ.PIR.muro"]
    assert H == pytest.approx(0.25 * 14.136, abs=TOL_MM)
    assert M == pytest.approx(H * 1.00, abs=TOL_MM)
    inc = next(c for c in cargas if c.codigo == "EQ.PIR.muro")
    assert inc.H > H                    # la del ensamble lleva la zapata


def test_H1_el_incremento_sismico_con_su_diagrama_lineal(tanteo):
    """
    Punto 7 del dorado: el incremento de 10.2740 kN/m a 0.6·h se reparte con
    el diagrama lineal que tiene esa resultante (1.712333 kPa en la base,
    6.849333 en la corona); sobre el arranque quedan 9.417833 kN/m a
    1.151515 m. Con 1/3 es el triangulo del estatico; por debajo de 1/3 se
    toma el de 1/3; por encima de 2/3 -- fuera de la ventana -- la
    resultante entera a su altura.
    """
    datos = {"h": 2.40, "fraccion_brazo": 0.6}
    p = CP["pantalla"]["sismico"]
    H, M = M9._incremento_sobre_el_arranque(10.2740, datos, 0.40, None)
    assert H == pytest.approx(p["incremento_sobre_el_arranque"], abs=TOL_MM)
    assert M / H == pytest.approx(p["brazo_del_incremento"], abs=TOL_MM)
    tercio = dict(datos, fraccion_brazo=1 / 3)
    H, M = M9._incremento_sobre_el_arranque(1.0, tercio, 0.40, None)
    assert H == pytest.approx((2.00 / 2.40) ** 2, rel=REL_CALCULO)
    assert M == pytest.approx(H * 2.00 / 3, rel=REL_CALCULO)
    bajo = M9._incremento_sobre_el_arranque(
        1.0, dict(datos, fraccion_brazo=0.333), 0.40, None)
    assert bajo == pytest.approx((H, M), rel=REL_CALCULO)
    alto = M9._incremento_sobre_el_arranque(
        1.0, dict(datos, fraccion_brazo=1.0), 0.40, None)
    assert alto == pytest.approx((1.0, 2.40 - 0.40), rel=REL_CALCULO)
    with pytest.raises(DatoInvalidoError):
        M9._incremento_sobre_el_arranque(1.0, dict(datos,
                                                   fraccion_brazo=math.nan),
                                         0.40, None)


def test_H1_la_estabilidad_externa_no_cambia(tanteo):
    """
    La correccion toca SOLO la solicitacion de la pantalla y del alero: las
    seis filas de la estabilidad del muro de tanteo siguen siendo las del
    dorado de T-7b (holguras a mano de `CP_T7B_SOLICITACIONES`).
    """
    e = M9.ensamble_estabilidad(tanteo, EST)
    holguras = {"E1-LRFD.est.e": 122.7733, "E2-LRFD.est.e": 0.52137,
                "E3-LRFD.est.e": 3.2000}
    for codigo, margen in holguras.items():
        v = next(x for x in e.verificaciones if x.codigo == codigo)
        assert v.paso.veredicto.margen == pytest.approx(margen,
                                                        rel=CPB["tolerancia_rel"])


def test_H2_el_muro_que_no_cede_arma_el_sismo_con_kh0(tanteo, monkeypatch):
    """
    AASHTO 11.6.5.4: «the value of kh used to calculate seismic earth
    pressure shall be increased to 1.0kh0». Con la cadena reducida (k_h =
    0.25, k_h0 = 0.50) el armado del muro que no cede va con 0.50 y la
    estabilidad sigue con 0.25. A mano (Mononobe-Okabe con relleno
    horizontal, que la cuña reproduce):
        psi = arctan 0.5 = 26.5651°; K_AE = cos²(3.4349°) / [cos 26.5651°
        · cos 46.6651° · (1 + sqrt(sen 50.1°·sen 3.4349° / cos 46.6651°))²]
            = 0.996411 / (0.894427·0.686313·1.584790) = 1.024444
        P_AE = 0.5·18·2.40²·1.024444 = 53.1072; incremento horizontal
        (53.1072 - 15.4100)·cos 20.1° = 35.4012 kN/m a 0.6·h
        sobre el arranque: 35.4012·0.916667 = 32.4511 a 1.151515
        V = 10.0496 + 32.4511 + 0.5·6.5236 + 0.5·0.5·14.136 = 49.2965
        M = 6.6997 + 37.3680 + 3.2618 + 3.5340 = 50.8635
    (a h/2: 49.8726·2.00/2.40 + 3.2618 + 3.5340 = 48.3563: rige su
    posicion).
    """
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h=0.25, k_v=0.0, k_h0=0.50))
    sol = M9.solicitaciones_de_resistencia(tanteo)
    assert sol["k_h_armado"] == pytest.approx(0.50, abs=ABS_CERO)
    assert sol["k_h_estabilidad"] == pytest.approx(0.25, abs=ABS_CERO)
    assert sol["datos_sismicos"]["K_AE"] == pytest.approx(1.024444, abs=TOL_K)
    s = _de(sol, SECCION_PANTALLA, "Evento Extremo I, 100% P_AE + 50% P_IR")
    assert s.M_u == pytest.approx(50.8635, abs=TOL)
    assert s.V_u == pytest.approx(49.2965, abs=TOL)
    assert s.M_u_reposo == pytest.approx(48.3563, abs=TOL)
    # la estabilidad externa no hereda el k_h0
    assert M9.ensamble_estabilidad(tanteo, SIS).K_AE == pytest.approx(
        CPB["K_AE_kh_025"], abs=TOL_K)
    assert any("1.0·k_h0 = 0.500" in a for a in sol["avisos"])
    # con el regimen que cede, el k_h de la cadena
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 REGIMEN_RESISTENCIA_CEDENTE)
    sol = M9.solicitaciones_de_resistencia(tanteo)
    assert sol["k_h_armado"] == pytest.approx(0.25, abs=ABS_CERO)
    s = _de(sol, SECCION_PANTALLA, "Evento Extremo I, 100% P_AE + 50% P_IR")
    assert s.M_u == pytest.approx(CP["pantalla"]["sismico"]["en_su_posicion"],
                                  abs=TOL)


def test_H2_si_solo_el_kh0_del_armado_no_es_evaluable_se_dice_asi(
        tanteo, monkeypatch):
    """
    Con k_h0 = 0.70 la cuña del relleno horizontal no tiene maximo (phi -
    psi < 0) y con k_h = 0.25 si: el armado sale de Resistencia I y el aviso
    dice que es el k_h0 del muro que no cede el que no se evalua, no la
    estabilidad, y que reducir k_h no es el remedio.
    """
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h=0.25, k_v=0.0, k_h0=0.70))
    sol = M9.solicitaciones_de_resistencia(tanteo)
    assert not sol["sismico"]
    (aviso,) = [a for a in sol["avisos"] if "SOLO de Resistencia I" in a]
    assert "k_h0 = 0.700" in aviso and "no es remedio" in aviso
    assert M9.ensamble_estabilidad(tanteo, SIS).verificaciones


def test_H2_la_puerta_de_kh_rechaza_lo_que_no_puede_ser(tanteo):
    for malo in (-0.1, math.nan, math.inf):
        with pytest.raises(DatoInvalidoError):
            M9.cargas_del_cabezal(tanteo, SIS, k_h=malo)


# --- H3: la fisuracion de AASHTO 5.6.7 --------------------------------------
# EL CONTROL DEL AUDITOR, a mano (pantalla de salida de A-01, Servicio I con
# reposo): M_s = 50.2 kN·m/m, A_s = 1290 mm2/m (Ø 1/2" @ 0.10), h = 0.30 m,
# d = 0.20221 m, d_c = 91.44 + 6.35 = 97.79 mm.
#   f_r = 2.887888 MPa; 0.8·f_r = 2.310311; M_s/S = 50.2/0.015 = 3346.7 kPa
#     = 3.3467 MPa > 2.3103: aplica
#   E_c = 2500·(21/6.894757)^0.33 ksi = 2500·3.045793^0.33 = 2500·1.444177
#     = 3610.44 ksi; n = 29000/3610.44 = 8.03227
#   rho·n = 1290e-6/0.20221·8.03227 = 0.0512420
#   k = sqrt(0.0512420² + 2·0.0512420) - 0.0512420 = 0.3242063 - 0.0512420
#     = 0.2729643; j = 1 - k/3 = 0.9090119
#   f_ss = 50.2 / (1290e-6·0.9090119·0.20221) = 211 710 kPa = 211.71 MPa
#   beta_s = 1 + 0.09779 / [0.7·(0.30 - 0.09779)] = 1.690866
#   en la fuente: s <= 700·gamma_e / (1.690866·30.706 ksi) - 2·3.8500 in
#     Clase 1: 13.482 - 7.700 = 5.782 in = 0.14687 m
#     Clase 2: 0.75·13.482 - 7.700 = 2.412 in = 0.06126 m
CP_FISURACION = {"M_s": 50.2, "As": 1290.0, "d": 0.20221, "h": 0.30,
                 "d_c": 0.09779, "f_t": 3.34667, "n": 8.03227,
                 "f_ss": 211.71, "beta_s": 1.690866, "s1": 0.14687,
                 "s2": 0.06126}


def test_H3_dorado_de_la_fisuracion_contra_el_control_del_auditor():
    c = CP_FISURACION
    r = M9.fisuracion_aashto(M_s=c["M_s"], As=c["As"], d=c["d"],
                             espesor=c["h"], d_c=c["d_c"], fc=21.0, fy=420.0)
    assert r["aplica"]
    assert r["f_t"] == pytest.approx(c["f_t"], abs=TOL_MM)
    assert r["umbral"] == pytest.approx(0.8 * 2.887888, abs=TOL_MM)
    assert r["n"] == pytest.approx(c["n"], abs=TOL_MM)
    assert r["f_ss"] == pytest.approx(c["f_ss"], abs=TOL_CM)
    assert r["beta_s"] == pytest.approx(c["beta_s"], abs=TOL_FINA)
    assert r["s_max"]["clase_1"] == pytest.approx(c["s1"], abs=TOL_MM)
    assert r["s_max"]["clase_2"] == pytest.approx(c["s2"], abs=TOL_MM)
    assert r["f_ss_max"] == pytest.approx(0.60 * 420.0, abs=ABS_CERO)
    # las constantes, contra la aritmetica: 700 kip/in y 29 000 ksi
    assert cn.FISURACION_COEFICIENTE_AASHTO_SI == pytest.approx(
        700 * 6.894757 * 0.0254, rel=REL_UNIDADES)
    assert cn.ES_REFUERZO_AASHTO_MPA == pytest.approx(29000 * 6.894757,
                                                      rel=REL_UNIDADES)
    assert cn.FISURACION_GAMMA_E["clase_1"] == pytest.approx(1.00,
                                                             abs=ABS_CERO)
    assert cn.FISURACION_GAMMA_E["clase_2"] == pytest.approx(0.75,
                                                             abs=ABS_CERO)
    assert set(cn.FISURACION_GAMMA_E) == {"clase_1", "clase_2"}
    # sin traccion no aplica
    assert not M9.fisuracion_aashto(M_s=0.0, As=1290.0, d=0.2, espesor=0.3,
                                    d_c=0.1, fc=21.0, fy=420.0)["aplica"]


@pytest.mark.parametrize("campo, malo", [
    ("As", 0.0), ("d", -0.1), ("espesor", math.nan), ("d_c", 0.0),
    ("d_c", 0.31), ("fc", math.inf), ("fy", -1.0)])
def test_H3_la_fisuracion_rechaza_lo_que_no_puede_ser(campo, malo):
    kw = dict(M_s=10.0, As=1000.0, d=0.2, espesor=0.3, d_c=0.1, fc=21.0,
              fy=420.0)
    kw[campo] = malo
    with pytest.raises(DatoInvalidoError):
        M9.fisuracion_aashto(**kw)
    with pytest.raises(LimiteNumericoError):
        M9.fisuracion_aashto(**dict(kw, **{campo: 0.2 if campo == "d_c"
                                           else 1000.0 if campo == "As"
                                           else 0.2 if campo == "d"
                                           else 0.3 if campo == "espesor"
                                           else 21.0 if campo == "fc"
                                           else 420.0}, M_s=math.nan))


def _seccion_con_servicio(M_s, *, M=60.0, V=40.0):
    return M9.diseno_flexion_corte(espesor=0.30,
                                   solicitaciones=(_sol(M=M, V=V),),
                                   momento_servicio=M_s)


def test_H3_sin_clase_la_propuesta_respeta_la_clase_1_y_la_fila_lo_dice():
    """
    Con el recubrimiento de cota (91.44 mm), M_u = 60 kN·m/m pide 824.5
    mm2/m y, sin fisuracion, Ø 1/2" @ 0.15 m (860). Con M_s = 50.2 la
    tension del acero en servicio a 0.15 y a 0.125 pasa de 0.60·f_y = 252
    MPa (312.6 y 262.3 MPa, a mano con n = 8.03227): la propuesta baja a Ø
    1/2" @ 0.10 m (1290; f_ss = 211.7, Clase 1 0.1469 m, Clase 2 0.0613 m,
    el control del auditor) y la fila sale INDICADOR «no decidida».
    Declarada la Clase 2 ninguna separacion de la barra de 1/2" llega a
    0.0613 m y la propuesta sube a Ø 5/8" @ 0.10 m (1990; f_ss = 141.2 MPa,
    beta_s = 1.707756, Clase 2: 0.75·122.589/(1.707756·141.15) - 2·0.09939
    = 0.1826 m): A6 decide y cumple.
    """
    _sin_datos_de_exposicion()
    sin = _seccion_con_servicio(50.2)
    a6 = _v(sin, "A6.pantalla")
    assert sin.fisuracion_aplica and sin.clase_exposicion is None
    assert sin.barra.designacion == "1/2"
    assert sin.barra.espaciamiento == pytest.approx(0.10, abs=ABS_CERO)
    assert sin.f_ss == pytest.approx(CP_FISURACION["f_ss"], abs=TOL_CM)
    assert sin.s_fisuracion["clase_1"] == pytest.approx(
        CP_FISURACION["s1"], abs=TOL_MM)
    assert sin.s_fisuracion["clase_2"] == pytest.approx(
        CP_FISURACION["s2"], abs=TOL_MM)
    assert a6.estado is EstadoDeVerificacion.INDICADOR
    assert "no decidida" in a6.paso.veredicto.explicacion
    assert "Clase 1" in a6.paso.nota_del_proyecto
    assert "A6" in _v(sin, "A4.pantalla").paso.nota_del_proyecto
    ca.establecer_valor_dinamico("clase_exposicion_fisuracion_cabezal",
                                 "clase_2")
    con = _seccion_con_servicio(50.2)
    assert con.clase_exposicion == "clase_2"
    assert con.barra.designacion == "5/8"
    assert con.barra.espaciamiento == pytest.approx(0.10, abs=ABS_CERO)
    assert con.f_ss == pytest.approx(141.15, abs=TOL_CM)
    assert con.s_fisuracion["clase_2"] == pytest.approx(0.1826, abs=TOL_MM)
    assert _v(con, "A6.pantalla").estado is EstadoDeVerificacion.CUMPLE
    # con la barra mayor el peralte baja (200.61 mm) y el acero pedido sube
    assert con.d == pytest.approx(0.20061, abs=TOL_EXACTA)
    assert con.As_adoptado > sin.As_adoptado
    ca.establecer_valor_dinamico("clase_exposicion_fisuracion_cabezal",
                                 "clase_1")
    uno = _seccion_con_servicio(50.2)
    assert _v(uno, "A6.pantalla").estado is EstadoDeVerificacion.CUMPLE
    assert uno.barra.espaciamiento == sin.barra.espaciamiento
    # sin la fisuracion la misma seccion proponia 0.15
    plana = M9.diseno_flexion_corte(espesor=0.30,
                                    solicitaciones=(_sol(M=60.0, V=40.0),))
    assert plana.barra.espaciamiento == pytest.approx(0.15, abs=ABS_CERO)


def test_H3_cuando_5_6_7_no_aplica_la_fila_lo_dice_y_cumple():
    seccion = _seccion_con_servicio(10.0)
    a6 = _v(seccion, "A6.pantalla")
    assert not seccion.fisuracion_aplica
    assert a6.estado is EstadoDeVerificacion.CUMPLE
    assert "no aplica" in a6.paso.veredicto.explicacion
    assert a6.valor_admisible == pytest.approx(0.8 * 2.887888, abs=TOL_MM)


def test_H3_sin_ninguna_barra_que_cumpla_la_clase_1_la_fila_no_cumple(
        monkeypatch):
    """
    Si ninguna barra del catalogo da el espaciamiento de 5.6.7 (aqui, una
    clase con un gamma_e minusculo), la propuesta se hace sin la fisuracion
    y A6 decide: no cumple ni con la clase que se declare.
    """
    monkeypatch.setitem(M9.FISURACION_GAMMA_E, "clase_1", 0.05)
    monkeypatch.setitem(M9.FISURACION_GAMMA_E, "clase_2", 0.04)
    seccion = _seccion_con_servicio(50.2)
    assert seccion.barra is not None
    assert _v(seccion, "A6.pantalla").estado is EstadoDeVerificacion.NO_CUMPLE
    ca.establecer_valor_dinamico("clase_exposicion_fisuracion_cabezal",
                                 "clase_1")
    seccion = _seccion_con_servicio(50.2)
    assert _v(seccion, "A6.pantalla").estado is EstadoDeVerificacion.NO_CUMPLE


def test_H3_sin_momento_de_servicio_A6_no_se_evalua_y_A4_lo_dice():
    seccion = M9.diseno_flexion_corte(momento=30.0, cortante=40.0,
                                      espesor=0.30)
    assert not any(v.codigo.startswith("A6") for v in seccion.verificaciones)
    assert seccion.M_servicio is None and seccion.fisuracion_aplica is None
    assert "NO se evalua" in _v(seccion, "A4.pantalla").paso.nota_del_proyecto


def test_H3_la_clase_de_exposicion_es_un_vacio_del_propietario():
    c = ca.CRITERIOS["clase_exposicion_fisuracion_cabezal"]
    assert c.valor is None and c.etiqueta == "A"
    assert c.sensibilidad == ("clase_1", "clase_2")
    assert c.nivel == ca.NIVEL_EXPEDIENTE
    with pytest.raises(DatoInvalidoError):
        with con_valor("clase_exposicion_fisuracion_cabezal", "clase_1",
                       motivo="de prueba"):
            ca.CRITERIOS  # noqa: B018
            object.__setattr__(ca.CRITERIOS[
                "clase_exposicion_fisuracion_cabezal"], "valor", "clase_3")
            try:
                M9.clase_de_exposicion()
            finally:
                object.__setattr__(ca.CRITERIOS[
                    "clase_exposicion_fisuracion_cabezal"], "valor", None)


def test_H3_el_servicio_de_cada_seccion_sale_con_el_regimen(tanteo):
    """Punto 5b del dorado: M_s de la pantalla = 22.9728 (reposo)."""
    sol = M9.solicitaciones_de_resistencia(tanteo)
    p = CP["pantalla"]["servicio"]
    assert sol["servicio"][SECCION_PANTALLA] == pytest.approx(p["reposo"],
                                                              abs=TOL)
    assert sol["servicio"][SECCION_ALERO] == pytest.approx(p["reposo"],
                                                           abs=TOL)
    (pantalla,) = M9.armar_elemento(tanteo, ELEMENTO_PANTALLA, sol)
    a6 = _v(pantalla, "A6.pantalla.e")
    assert a6.valor_obtenido == pytest.approx(p["f_t_MPa"], abs=TOL_MM)
    assert a6.valor_admisible == pytest.approx(p["umbral_MPa"], abs=TOL_MM)
    ca.establecer_valor_dinamico("regimen_resistencia_elementos_cabezal",
                                 REGIMEN_RESISTENCIA_CEDENTE)
    sol = M9.solicitaciones_de_resistencia(tanteo)
    assert sol["servicio"][SECCION_PANTALLA] == pytest.approx(p["activo"],
                                                              abs=TOL)


# --- H4, H6, H7, H8 ----------------------------------------------------------

def test_H4_la_altura_de_la_zapata_sobre_su_refuerzo(tanteo):
    """
    T-00: 400 - 91.44 - 12.7/2 = 302.21 mm >= 300: cumple. Con la zapata de
    0.37 m de A-01: 370 - 97.79 = 272.21 mm < 300: no cumple, y con
    «solo_aashto» informa.
    """
    a = M9.armado_del_cabezal(tanteo)
    a8 = _v(a, "A8.zapata.e")
    assert a8.estado is EstadoDeVerificacion.CUMPLE
    assert a8.valor_obtenido == pytest.approx(0.30221, abs=TOL_EXACTA)
    assert a8.valor_admisible == pytest.approx(0.30, abs=ABS_CERO)
    assert a8.paso.umbral.cita_id == "E060.15.7#PERALTE"
    delgada = replace(tanteo, geometria=_geometria(espesor_zapata=0.37,
                                                   D_f=0.77))
    b = M9.armado_del_cabezal(delgada)
    assert _v(b, "A8.zapata.e").valor_obtenido == pytest.approx(
        0.27221, abs=TOL_EXACTA)
    assert _v(b, "A8.zapata.e").estado is EstadoDeVerificacion.NO_CUMPLE
    assert any(": A8" in x for x in b.avisos)
    ca.establecer_valor_dinamico("regla_minimos_constructivos_cabezal",
                                 "solo_aashto")
    c = M9.armado_del_cabezal(delgada)
    assert _v(c, "A8.zapata.e").estado is EstadoDeVerificacion.INDICADOR


def test_H6_el_aviso_nombra_el_vano_la_losa_y_el_dentellon(tanteo):
    a = M9.armado_del_cabezal(tanteo)
    (aviso,) = [x for x in a.avisos if "NO cubre" in x]
    for palabra in ("VANO", "22.6.6.5", "losa de entrega", "dentellon",
                    "empalmes", "secciones intermedias de los aleros"):
        assert palabra in aviso, palabra
    assert "5.6.7" not in aviso            # la fisuracion ya es la fila A6
    b = M9.verificar_cabezal_ciclopeo(_gravedad())
    assert any("22.6.6.5" in x for x in b.avisos)


def test_H7_los_textos_dicen_lo_que_el_codigo_hace():
    fc = ca.CRITERIOS["fc_cabezal_mpa"].justificacion
    assert "verificacion A7" in fc and "A6" not in fc
    ciclo = ca.CRITERIOS["concreto_ciclopeo_cabezal"].justificacion
    assert "dos verificaciones del material" in ciclo and "R4" not in ciclo
    traccion = ca.CRITERIOS["criterio_traccion_cabezal_ciclopeo"].justificacion
    assert "22.4.7" in traccion and "NO la exige" not in traccion
    reg = construir()
    assert "A6" not in reg.cita("AASHTO_LRFD_9.5.6.7#FISURACION").nota.replace(
        "fila A6", "")
    assert "verificacion A5)" not in str(
        reg.cita("AASHTO_LRFD_9.5.5.4.2#FLEXION").nota)


def test_H8_el_peralte_de_cortante_no_pasa_del_efectivo():
    _sin_datos_de_exposicion()
    # con el recubrimiento de cota la letra da 0.72·h > d
    r = M9.cortante_del_concreto(d=0.20221, a=0.015, espesor=0.30, fc=21.0,
                                 beta=2.0)
    assert r["d_v_letra"] == pytest.approx(0.216, abs=TOL_EXACTA)
    assert r["d_v"] == pytest.approx(0.20221, abs=TOL_EXACTA)
    # con un recubrimiento chico no hay tope que aplicar
    r = M9.cortante_del_concreto(d=0.27, a=0.01, espesor=0.30, fc=21.0,
                                 beta=2.0)
    assert r["d_v"] == pytest.approx(r["d_v_letra"], abs=ABS_CERO)
    # la seccion lo avisa con las dos resistencias
    seccion = M9.diseno_flexion_corte(momento=30.0, cortante=40.0,
                                      espesor=0.30)
    assert seccion.d_v_letra == pytest.approx(0.216, abs=TOL_EXACTA)
    assert any("5.7.2.8" in x and "acota" in x for x in seccion.avisos)
    reg = construir()
    assert reg.cita("AASHTO_LRFD_9.5.7.2.8#DV").interpretacion is not None


def test_H8_la_aplicabilidad_del_simplificado_usa_el_d_v_de_la_letra():
    """
    Una zapata de 0.45 m (> 16.0 in) cuyo vuelo de 0.62 m queda por debajo
    de 3·d_v de la letra (3·0.324 = 0.972 m) entra al simplificado aunque
    el d_v acotado sea menor: la aplicabilidad es de la fuente.
    """
    seccion = M9.diseno_flexion_corte(momento=20.0, cortante=60.0,
                                      espesor=0.45, es_zapata=True,
                                      vuelo=0.62, clave=SECCION_PUNTA)
    assert seccion.d_v <= seccion.d + 1e-12
    paso = _v(seccion, "A2.punta").paso
    assert "zapata con vuelo" in next(m.procedencia for m in paso.sustitucion
                                      if m.simbolo == "beta")


# --- H5 y H11: el ciclopeo ---------------------------------------------------

def test_H5_H11_C6_incumple_y_decide_con_la_traccion_admisible(tanteo):
    """
    Un cuerpo de 0.30 m constante (H = 1.30 m, el resto del dorado), en el
    arranque y en reposo, a mano: W = 23.56·0.30·1.30 = 9.1884; P_u =
    0.9·9.1884 = 8.26956; M_u = 1.7·3.2955 + 1.7·4.636008 = 13.483564
    (brazo del peso nulo: cuerpo de espesor constante); t_r = 0.25;
    traccion = 13.483564/(0.25²/6) - 8.26956/0.25 = 1294.422 - 33.078 =
    1261.344 kPa frente a 0.5·0.42·sqrt(10)·1000 = 664.078: 1.8994. C6
    DECIDE con «traccion_admisible_e060» (NO CUMPLE) e informa con las
    tracciones nulas (INDICADOR). Es el mutante M10 de la auditoria.
    """
    g = _gravedad(espesor_base_muro=0.30)
    a = M9.verificar_cabezal_ciclopeo(g)
    c6 = _v(a, "C6.cuerpo.e")
    assert c6.valor_obtenido == pytest.approx(1261.344 / 664.078, abs=TOL)
    assert c6.estado is EstadoDeVerificacion.INDICADOR
    ca.establecer_valor_dinamico("criterio_traccion_cabezal_ciclopeo",
                                 "traccion_admisible_e060")
    b = M9.verificar_cabezal_ciclopeo(g)
    assert _v(b, "C6.cuerpo.e").estado is EstadoDeVerificacion.NO_CUMPLE
    assert _v(b, "C3.cuerpo.e").estado is EstadoDeVerificacion.INDICADOR


def test_H5_la_excentricidad_minima_de_22_6_3(tanteo, monkeypatch):
    """
    Sin empuje sobre la seccion, el momento de C6 no baja de P_u·0,10·t:
    cuerpo de 0.50 m en el arranque, W = 12.2512, P_u = 11.02608, M_u
    minimo = 0.551304; con el brazo del peso del cuerpo trapecial
    (0.25 - 0.2041667 = 0.0458333) el momento de la carga es 0.505362, que
    queda por debajo. Traccion = 0.551304/(0.45²/6) - 11.02608/0.45 =
    16.3349 - 24.5024 = -8.1675 kPa (la seccion sigue comprimida).
    """
    real = M9.acciones_sobre_una_seccion

    def sin_empuje(*args, **kw):
        a = dict(real(*args, **kw))
        for k in ("H_suelo", "M_suelo", "H_ls", "M_ls", "H_agua", "M_agua"):
            a[k] = 0.0
        return a

    monkeypatch.setattr(M9, "acciones_sobre_una_seccion", sin_empuje)
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    c6 = _v(a, "C6.cuerpo.e")
    arranque = c6.paso.sustitucion[0]
    assert "traccion -8.2 kPa" in arranque.procedencia


def test_H5_la_junta_se_declara_y_tiene_su_cita():
    c = ca.CRITERIOS["junta_arranque_cabezal_ciclopeo"]
    assert c.valor == "junta_de_construccion" and c.etiqueta == "A"
    assert c.sensibilidad == ("junta_de_construccion", "vaciado_monolitico")
    reg = construir()
    assert reg.cita("E060.22.4.7#JUNTAS").caracter.value == "exigencia"
    tercio = reg.cita("E060.22.6.3#TERCIO")
    assert tercio.interpretacion is not None
    assert "cargas de servicio" in tercio.interpretacion.en_contra[0]


def test_H5_C1_y_C3_no_llevan_el_caracter_de_una_exigencia(tanteo):
    a = M9.verificar_cabezal_ciclopeo(_gravedad())
    for codigo in ("C1.base.e", "C3.cuerpo.e"):
        assert _v(a, codigo).paso.umbral.caracter.startswith(
            "CRITERIO DEL PROYECTO"), codigo
    assert _v(a, "C2.cuerpo.e").paso.umbral.caracter == "EXIGENCIA"


# --- H9, H10, H11, H12 y las preguntas ----------------------------------------

def test_H9_el_reposo_de_minimos_que_vuelca_se_avisa(tanteo):
    """
    Con un relleno mas alto que el muro de tanteo (superficie 1.00 m sobre
    la coronacion, horizontal) el empuje en reposo factorado de minimos
    deja la resultante fuera de la base y el activo no: la punta se arma
    con el activo y se avisa.
    """
    alto = replace(tanteo, cota_relleno=tanteo.cota_relleno + 1.0,
                   cota_borde_plataforma=tanteo.cota_relleno + 1.0)
    sol = M9.solicitaciones_de_resistencia(alto)
    avisos = [a for a in sol["avisos"] if "se DESCARTA" in a]
    assert avisos and "Resistencia I (minimos), empuje en reposo" in avisos[0]
    s = _de(sol, SECCION_PUNTA, "Resistencia I (minimos)")
    assert s.M_u_reposo is None


def test_H10_la_sensibilidad_de_K0_con_talud_se_imprime_y_no_se_adopta(
        tanteo):
    i = 10.0
    entorno = replace(tanteo, cota_borde_plataforma=tanteo.cota_relleno + 0.5)
    a = M9.armado_del_cabezal(entorno)
    regimen = a.pasos[0]
    valores = {m.simbolo: m for m in regimen.sustitucion}
    k0t = valores["K0·(1 + sen i)"]
    assert "no adoptado" in k0t.procedencia
    assert k0t.valor > valores["K0"].valor
    assert a.K0 == pytest.approx(0.5, abs=ABS_CERO)
    del i


def test_H11_el_acero_de_temperatura_del_reparto_usa_el_mayor_ancho(tanteo):
    """
    El mutante M23 de la auditoria: el reparto de la zapata con «solo
    AASHTO» lleva A_s = 1.30·b·h/[2·(b + h)·f_y] con b = max(B, e_z) = 2.00
    m: 0.746932·2000·400/(2·2400·420) = 0.296402 mm2/mm = 296.4 mm2/m (con
    b = e_z = 0.40 m saldria el piso de 232.8).
    """
    ca.establecer_valor_dinamico("regla_minimos_constructivos_cabezal",
                                 "solo_aashto")
    a = M9.armado_del_cabezal(tanteo)
    fila = next(f for f in a.tabla if f.posicion.startswith("zapata"))
    assert fila.As_minimo == pytest.approx(296.40, abs=TOL_AS)


def test_H12_las_constantes_de_AASHTO_llevan_el_sufijo_y_la_barra_gruesa_no_vive_en_M9():
    for nombre in ("BETA_1_REDUCCION_AASHTO_SI",
                   "PERALTE_MAX_SIMPLIFICADO_AASHTO_SI",
                   "TEMPERATURA_AS_MIN_AASHTO_SI",
                   "TEMPERATURA_AS_MAX_AASHTO_SI",
                   "FISURACION_COEFICIENTE_AASHTO_SI",
                   "EC_COEFICIENTE_AASHTO_SI"):
        assert hasattr(cn, nombre), nombre
    for viejo in ("BETA_1_REDUCCION_POR_MPA", "PERALTE_MAX_SIMPLIFICADO_M",
                  "TEMPERATURA_AS_MIN_MM2_M", "TEMPERATURA_AS_MAX_MM2_M"):
        assert not hasattr(cn, viejo), viejo
    assert cn.RECUBRIMIENTO_BARRA_GRUESA_DESDE == "3/4"
    assert not hasattr(M9, "BARRA_GRUESA_DESDE")


def test_pregunta_2_el_aviso_del_recubrimiento_dice_donde_no_es_el_lado_seguro():
    _sin_datos_de_exposicion()
    _, _, aviso = M9.recubrimiento_para_armar(condicion="contra_suelo")
    for palabra in ("7.7.5.1", "corrosivo", "5.6.7", "15.7", "0.72·h"):
        assert palabra in aviso, palabra


def test_pregunta_4_la_pantalla_sobre_media_resistencia_es_un_indicador():
    """
    V_u = 80 kN/m en la pantalla de 0.30 m: phi·V_n = 138.40 >= 80 (cumple)
    y 0.5·phi·V_c = 69.20 < 80: A2 sale INDICADOR; en una zapata, CUMPLE.
    """
    pantalla = M9.diseno_flexion_corte(momento=30.0, cortante=80.0,
                                       espesor=0.30)
    a2 = _v(pantalla, "A2.pantalla")
    assert a2.estado is EstadoDeVerificacion.INDICADOR and a2.cumple
    assert "0.5·phi·V_c" in a2.paso.veredicto.explicacion
    zapata = M9.diseno_flexion_corte(momento=30.0, cortante=80.0,
                                     espesor=0.30, es_zapata=True,
                                     vuelo=0.50, clave=SECCION_PUNTA)
    assert _v(zapata, "A2.punta").estado is EstadoDeVerificacion.CUMPLE
    bajo = M9.diseno_flexion_corte(momento=30.0, cortante=60.0, espesor=0.30)
    assert _v(bajo, "A2.pantalla").estado is EstadoDeVerificacion.CUMPLE


def test_pregunta_1_el_espesor_minimo_de_concreto_simple_es_un_criterio(
        tanteo):
    espesor, texto, cita = M9.peralte_minimo_zapata(M9.TIPO_GRAVEDAD)
    assert espesor == pytest.approx(0.30, abs=ABS_CERO)
    assert "espesor_min_zapata_concreto_simple_m" in texto
    assert cita == "E060.22.7.4#ZAPATA"
    with con_valor("espesor_min_zapata_concreto_simple_m", 0.35,
                   motivo="de prueba"):
        assert M9.peralte_minimo_zapata(M9.TIPO_GRAVEDAD)[0] == \
            pytest.approx(0.35, abs=ABS_CERO)


def test_las_nueve_citas_del_cierre_estan_en_el_registro():
    reg = construir()
    for cita_id in ("AASHTO_LRFD_9.5.6.7#ESPACIAMIENTO",
                    "AASHTO_LRFD_9.5.6.7#GAMMA_E", "AASHTO_LRFD_9.5.6.7#FSS",
                    "AASHTO_LRFD_9.C5.6.7#CLASE_1",
                    "AASHTO_LRFD_9.5.4.3.2#ES", "AASHTO_LRFD_9.C5.4.2.4#EC",
                    "E060.22.4.7#JUNTAS", "E060.22.6.3#EXCENTRICIDAD",
                    "E060.22.6.6.5#ABERTURAS"):
        c = reg.cita(cita_id)
        assert c.verificado is not None, cita_id


@pytest.mark.lento
def test_el_armado_final_de_A01_con_los_datos_de_prueba(tmp_path):
    """
    El armado de A-01 con los datos DE PRUEBA de T-7b (no son del
    expediente) y SIN el analisis quimico ni la categoria del acero (el
    recubrimiento de cota, 91.44 mm), despues de las correcciones de T-7c.
    Es LECTURA DE LA CORRIDA, contrastada con los controles del auditor
    (que eran sin H1): la cadena declara la reduccion de k_h (0.25) y el
    muro que no cede arma el sismo con k_h0 = 0.50 (H2), y con el diagrama
    integrado sobre el arranque (H1) la pantalla de entrada pide 59.34 kN·m/m
    (57.27 en el control, sin H1: 730 frente a 703 mm2/m, la misma Ø 1/2" @
    0.175) y la de salida 138.08 (135.51: 1837 frente a 1798 mm2/m, la misma
    Ø 5/8" @ 0.10); la punta de salida, que H1 no toca, 755 mm2/m, Ø 1/2" @
    0.15, como el control. Ningun diametro del conducto se mueve.
    """
    _sin_datos_de_exposicion()
    _, a01 = _correr_de_prueba(tmp_path)
    assert a01.resultado.seccion.etiqueta() == "Ø 0.90 m"
    esperado = {
        ("entrada", SECCION_PANTALLA): (59.34, "1/2", 0.175),
        ("entrada", SECCION_PUNTA): (38.39, "1/2", 0.25),
        ("entrada", SECCION_TALON): (28.69, "1/2", 0.25),
        ("salida", SECCION_PANTALLA): (138.08, "5/8", 0.10),
        ("salida", SECCION_PUNTA): (83.51, "1/2", 0.15),
        ("salida", SECCION_TALON): (71.72, "1/2", 0.175),
    }
    for a in a01.cabezal.armado:
        for clave in (SECCION_PANTALLA, SECCION_PUNTA, SECCION_TALON):
            M_u, barra, s = esperado[(a.extremo, clave)]
            p = a.seccion(clave)
            assert p.rige_flexion.M_u == pytest.approx(M_u, abs=TOL_CM)
            assert p.barra.designacion == barra
            assert p.barra.espaciamiento == pytest.approx(s, abs=ABS_CERO)
    salida = next(a for a in a01.cabezal.armado if a.extremo == "salida")
    # 755 mm2/m, el control del auditor escrito sin decimales
    assert round(salida.seccion(SECCION_PUNTA).As_adoptado) == 755
    # la fisuracion aplica en la pantalla de salida y su barra la cumple
    # con las dos clases
    a6 = next(v for v in salida.verificaciones
              if v.codigo == "A6.pantalla.s")
    assert salida.seccion(SECCION_PANTALLA).fisuracion_aplica
    assert a6.estado is EstadoDeVerificacion.CUMPLE
    # la pantalla de salida pasa de 0.5·phi·V_c: A2 es un indicador (H8 y
    # pregunta 4), y el reposo de minimos que vuelca se avisa (H9)
    assert next(v for v in salida.verificaciones
                if v.codigo == "A2.pantalla.s").estado \
        is EstadoDeVerificacion.INDICADOR
    assert any("se DESCARTA" in x for x in salida.avisos)
    assert any("1.0·k_h0 = 0.500" in x for x in salida.avisos)



# ---------------------------------------------------------------------------
# Lo que la mutacion del cierre enseño (arnes de EXT-11 sobre las funciones
# que el cierre toco). Dos huecos reales: la fila A6 no se miraba por dentro
# (margen, rama con f_ss sobre el tope, nota con las dos clases), y la inercia
# de la pantalla se probaba en el muro de tanteo, donde el brazo desde el
# arranque es 1.00 m y multiplicar o dividir por el da lo mismo.
# ---------------------------------------------------------------------------

def test_mutacion_del_cierre_la_fila_A6_por_dentro():
    """
    Con el dorado de la fisuracion (s_max 0.14687 m en Clase 1 y 0.06126 m
    en Clase 2, f_ss = 211.71 MPa):
      sin clase, s = 0.10 m: INDICADOR, admisible el de la Clase 2 y margen
        0.06126 - 0.10 = -0.03874 m; la nota dice las dos clases.
      Clase 1 declarada: decide y cumple, margen 0.14687 - 0.10 = 0.04687 m.
      con f_y = 300 MPa el tope 0.60·f_y = 180 MPa queda bajo f_ss: NO
        CUMPLE aunque el espaciamiento cumpla, declarada o no la clase, y la
        explicacion nombra la tension y no el espaciamiento.
      sin traccion suficiente (M_s = 10): margen = 0.8·f_r - f_t.
    """
    c = CP_FISURACION
    base = dict(As=c["As"], d=c["d"], espesor=c["h"], d_c=c["d_c"], fc=21.0)
    fis = M9.fisuracion_aashto(M_s=c["M_s"], fy=420.0, **base)
    barra = SimpleNamespace(texto='Ø 1/2" @ 0.10 m')
    comun = dict(codigo="A6.prueba", donde="prueba", M_s=c["M_s"],
                 As=c["As"], rec=91.44, barra=barra)
    sin = M9._fila_de_fisuracion(fis=fis, s_prop=0.10, clase=None, **comun)
    assert sin.estado is EstadoDeVerificacion.INDICADOR
    assert sin.valor_admisible == pytest.approx(c["s2"], abs=TOL_MM)
    assert sin.paso.veredicto.margen == pytest.approx(c["s2"] - 0.10,
                                                      abs=TOL_MM)
    assert "Clase 1: s <= 0.147 m (cumple)" in sin.paso.nota_del_proyecto
    assert "Clase 2: s <= 0.061 m (NO cumple)" in sin.paso.nota_del_proyecto
    a_s = next(m for m in sin.paso.sustitucion if m.simbolo == "A_s")
    assert a_s.procedencia == barra.texto
    uno = M9._fila_de_fisuracion(fis=fis, s_prop=0.10, clase="clase_1",
                                 **comun)
    assert uno.estado is EstadoDeVerificacion.CUMPLE
    assert uno.paso.veredicto.margen == pytest.approx(c["s1"] - 0.10,
                                                      abs=TOL_MM)
    alto = M9.fisuracion_aashto(M_s=c["M_s"], fy=300.0, **base)
    assert alto["f_ss"] > alto["f_ss_max"]
    for clase in ("clase_1", None):
        v = M9._fila_de_fisuracion(fis=alto, s_prop=0.05, clase=clase,
                                   **comun)
        assert v.estado is EstadoDeVerificacion.NO_CUMPLE, clase
    v = M9._fila_de_fisuracion(fis=alto, s_prop=0.05, clase="clase_1",
                               **comun)
    assert "0.60·f_y" in v.paso.veredicto.explicacion
    leve = M9.fisuracion_aashto(M_s=10.0, fy=420.0, **base)
    assert not leve["aplica"]
    v = M9._fila_de_fisuracion(fis=leve, s_prop=0.10, clase=None,
                               **dict(comun, M_s=10.0))
    assert v.estado is EstadoDeVerificacion.CUMPLE
    assert v.paso.veredicto.margen == pytest.approx(
        leve["umbral"] - leve["f_t"], abs=TOL_MM)
    assert leve["umbral"] - leve["f_t"] > 0


def test_mutacion_del_cierre_la_inercia_de_la_pantalla_con_brazo_distinto_de_uno(
        tanteo):
    """
    En el muro bajo de H1 (h = 1.00 m, arranque a 0.40 m) la pantalla mide
    0.60 m y su centro de gravedad queda a 0.30 m del arranque: la inercia
    que la carga es k_h·W_p con ese brazo, 0.30 m y no 1.00 m.
    """
    ca.establecer_valor_dinamico("h_eq_bajo_altura_tabulada", "primera_fila")
    g = _geometria(H=0.60, cota_coronacion=101.00)
    entorno = replace(tanteo, geometria=g, cota_relleno=101.00,
                      cota_borde_plataforma=101.00)
    cargas, datos = M9.cargas_del_cabezal(entorno, SIS)
    pantalla = next(c for c in cargas if c.codigo == "DC.pantalla")
    assert pantalla.z == pytest.approx(0.70, abs=TOL_MM)   # 0.40 + 0.30
    H, M = M9.empujes_sobre_el_arranque(cargas, datos, 0.40)["EQ.PIR.muro"]
    assert H == pytest.approx(datos["k_h"] * pantalla.V, abs=TOL_MM)
    assert M == pytest.approx(H * 0.30, abs=TOL_MM)


def test_mutacion_del_cierre_el_aviso_del_d_v_acotado_con_sus_numeros():
    """
    El aviso de H8 se buscaba por dos palabras que tambien estan en el aviso
    del recubrimiento de cota, y la mutacion que lo apagaba vivia. En la
    pantalla de 0.30 m con Ø 1/2" (d = 0.20221 m): 0.72·h = 0.216 m, y la
    resistencia del concreto baja de 153.776·0.216/0.20221 = 164.3 kN/m a
    153.8 kN/m (el dorado de `CP_T7C_ARMADO`); la sustitucion de A2 dice el
    d_v de la letra.
    """
    _sin_datos_de_exposicion()
    seccion = M9.diseno_flexion_corte(momento=30.0, cortante=40.0,
                                      espesor=0.30)
    assert seccion.d == pytest.approx(0.20221, abs=TOL_EXACTA)
    aviso = [x for x in seccion.avisos if "0.72·h = 0.216 m" in x]
    assert len(aviso) == 1
    assert "de 164.3 a 153.8 kN/m" in aviso[0]
    d_v = next(m for m in _v(seccion, "A2.pantalla").paso.sustitucion
               if m.simbolo == "d_v")
    assert "la letra daria 0.2160 m" in d_v.procedencia


def test_mutacion_del_cierre_A8_y_el_paso_del_regimen_dicen_sus_numeros(
        tanteo, monkeypatch):
    """
    A8 en T-00: 0.40 - (91.44 + 12.7/2)/1000 = 0.30221 m, margen 0.00221 m
    sobre los 0.30 m; la otra lectura (hasta la cara) 0.40 - 0.09144 =
    0.30856 m. El paso del regimen, con la cadena de H2 (k_h = 0.25, k_h0 =
    0.50): k_h del armado 0.50 (1.0·k_h0) y de la estabilidad 0.25; y el
    contraste K0·(1 + sen i) dice «sen i» mas de empuje: con el talud
    de 0.5 m sobre el relleno del dorado de H10 se lee i del propio paso.
    """
    monkeypatch.setattr(M9, "cadena_sismica", lambda: SimpleNamespace(
        k_h=0.25, k_v=0.0, k_h0=0.50))
    a = M9.armado_del_cabezal(tanteo)
    a8 = _v(a, "A8.zapata.e")
    assert a8.paso.veredicto.margen == pytest.approx(0.00221, abs=TOL_EXACTA)
    cara = next(m for m in a8.paso.sustitucion
                if m.simbolo == "hasta la cara de la barra")
    assert cara.valor == pytest.approx(0.30856, abs=TOL_EXACTA)
    valores = {m.simbolo: m for m in a.pasos[0].sustitucion}
    assert valores["k_h del armado"].valor == pytest.approx(0.50,
                                                            abs=ABS_CERO)
    assert "1.0·k_h0" in valores["k_h del armado"].procedencia
    assert valores["k_h de la estabilidad"].valor == pytest.approx(
        0.25, abs=ABS_CERO)
    entorno = replace(tanteo, cota_borde_plataforma=tanteo.cota_relleno + 0.5)
    k0t = {m.simbolo: m for m in
           M9.armado_del_cabezal(entorno).pasos[0].sustitucion}[
               "K0·(1 + sen i)"]
    i = float(k0t.procedencia.split("i = ")[1].split(" grados")[0])
    assert k0t.valor == pytest.approx(0.5 * (1 + math.sin(math.radians(i))),
                                      abs=TOL_MM)
    assert f"Seria un {math.sin(math.radians(i)):.0%} mas" in k0t.procedencia
