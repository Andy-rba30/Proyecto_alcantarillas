"""
tests/test_M9_cabezal.py
=========================
Fase 9 (M9_cabezal.py). Cuatro bloques, en el orden de la hoja de ruta:

    9.2 cadena sismica    los seis pasos horizontales por separado, k_v
                          aparte, y el ensamble `cadena_sismica()`.
    9.2 Mononobe-Okabe    los tres juegos de CP9_MONONOBE_OKABE, con los seis
                          parametros distintos de cero -- son los que cubren
                          las convenciones de signo --, el caso limite contra
                          tan^2(45 - phi/2), que prueba la reduccion a Rankine
                          y NO los signos (SIS-F-04), la monotonia frente a
                          k_h y el dominio de validez.
    9.2 cargas            sobrecarga de 0.60 m equivalente, empujes, agua,
                          subpresion y las tres combinaciones AASHTO.
    9.3 estabilidad       los FS de la tabla en sus dos condiciones.
    9.4 refuerzo          regla del recubrimiento MAYOR, cuantias minimas,
                          espaciamiento y alternativa ciclopea.

Y, transversalmente, que cada vacio declarado se detiene donde debe con
`CriterioPendienteError` en vez de rellenarse en silencio.
"""

import math
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest
from dataclasses import replace

import criterios_adoptados as ca
import datos_sitio as ds
from constantes_fisicas import GAMMA_AGUA_KN_M3, PIE_EN_METROS
from constantes_normativas import (CICLOPEO_FC_MATRIZ_MIN_APLICABLE,
                                   RECUBRIMIENTO_MP_EQUIVALENCIA,
                                   RECUBRIMIENTO_MP_MM,
                                   CICLOPEO_FRACCION_PIEDRA_MAX,
                                   COMBINACIONES_AASHTO, CUANTIA_MIN_MURO,
                                   ESPACIAMIENTO_MAX_ABSOLUTO,
                                   EXPOSICION_ESPECIAL,
                                   F_PGA_CLASES_EN_ROCA,
                                   F_PGA_EXIGE_ESTUDIO_DE_SITIO,
                                   F_PGA_TABLA,
                                   F_PGA_TABLA_PGA_COLUMNAS,
                                   FS,
                                   K_V_DECLARACION_PRESCRITO,
                                   LECTURA_COLUMNA_EXTREMA_ESTRICTA,
                                   LECTURA_COLUMNA_EXTREMA_INCLUSIVE,
                                   LECTURAS_COLUMNA_EXTREMA,
                                   REDUCCION_KH_POR_DESPLAZAMIENTO,
                                   NQ_ZAPATA_EN_TALUD,
                                   ORIENTACION_PARALELO_AL_TRAFICO,
                                   ORIENTACION_PERPENDICULAR_AL_TRAFICO,
                                   RECUBRIMIENTO, SOBRECARGA_TRASDOS_H_EQ,
                                   SOBRECARGA_TRASDOS_PISO_MP_M,
                                   TABLA_GAMMA_P_FILAS)
from modelos import (CondicionAnalisis, CriterioPendienteError,
                     DatoFaltanteError, DatoInvalidoError,
                     DisenoNoFactibleError, GeometriaCabezal)
from modulos.M0_carga import cargar_puntos
from modulos import M9_cabezal as M9
from modulos.M9_cabezal import (CRITERIO_CORTANTE_ALTO,
                                cimentacion_en_roca,
                                clase_exposicion_sulfatos,
                                clases_de_sitio_plausibles,
                                demanda_sismica_cabezal,
                                factor_sitio_desde_tabla,
                                fuerza_inercia_muro,
                                lectura_columna_extrema,
                                NUMERAL_9_1,
                                excentricidad_admisible_sismica,
                                excentricidad_resultante,
                                presion_contacto_base,
                                verificar_excentricidad_sismica,
                                aceleracion_ajustada_sitio,
                                cuantia_de_diseno,
                                altura_agua_sobre_base,
                                angulo_inercia_sismica,
                                aplica_sobrecarga_trasdos,
                                h_eq_sobrecarga_trasdos,
                                aviso_ambiente_corrosivo, brazo_incremento_sismico,
                                cadena_sismica, capacidad_portante_zapata_en_talud,
                                coeficiente_sismico_base,
                                coeficiente_sismico_horizontal,
                                coeficiente_sismico_vertical, combinaciones,
                                condicion_normativa_cabezal, cuantia_minima,
                                diseno_flexion_corte, empuje_activo_estatico,
                                empuje_activo_sismico_total,
                                empuje_hidrostatico, empuje_mononobe_okabe,
                                empuje_sobrecarga_trasdos, empujes_trasdos,
                                espaciamiento_maximo, f_pga, factor_muro,
                                factores_de_carga, fs_requerido,
                                geometria_adoptada, incremento_sismico,
                                k_a_coulomb, k_ae_del_proyecto,
                                k_ae_mononobe_okabe, ka_rankine,
                                n_q_zapata_en_talud, n_s_zapata_en_talud,
                                nota_temperatura_dos_caras,
                                parametros_resistencia_art20, pga_roca_b,
                                peso_especifico_relleno, peso_propio_cabezal,
                                presion_sobrecarga_trasdos,
                                recubrimiento_aashto_mm, recubrimiento_de_diseno,
                                recubrimiento_e060_mm,
                                requisitos_durabilidad_concreto,
                                requiere_temperatura_dos_caras,
                                sobrecarga_trasdos_siempre_aplica, subpresion,
                                verificar_capacidad_portante, verificar_ciclopeo,
                                verificar_cuantia, verificar_deslizamiento,
                                verificar_espaciamiento, verificar_estabilidad,
                                verificar_estabilidad_global, verificar_talud,
                                verificar_volteo)
from tests.fixtures.casos_patron import (CP7_CADENA_SISMICA,
                                         CP9_EMPUJE_TRASDOS,
                                         CP9_ENSAMBLE_TRASDOS,
                                         CP9_MONONOBE_OKABE,
                                         CP9_RANKINE_LIMITE,
                                         CP9_TOLERANCIA_RELATIVA)
from tests.apoyo.aproximacion import ABS_CERO, REL_TRANSPORTE
from tolerancias import TOL_UMBRAL_NORMATIVO

TOL = 1e-12

# Mil veces el umbral normativo: un incumplimiento que la banda NO debe tapar.
TOL_MIL_VECES_EL_UMBRAL = 1000 * TOL_UMBRAL_NORMATIVO

# Los dorados de la cadena sismica se LEEN del caso patron, no se reescriben
# como literales aqui (SIS-F-14): duplicarlos hacia que corregir el fixture no
# llegara nunca a estos tests.
CP7 = CP7_CADENA_SISMICA
CP9 = CP9_EMPUJE_TRASDOS

# Tolerancia RELATIVA del contraste contra los dorados de CP-9 (SIS-F-05).
# No sale de src/tolerancias.py a proposito: aquellas tres miden la precision
# del CALCULO (convergencia de Brent, borde del intervalo, ruido en un umbral
# normativo) y esta mide el REDONDEO con que el dorado esta ESCRITO en el
# fixture. Se usa siempre como `rel=`, nunca `==` sobre floats (SIS-F-16).
REL_CP9 = CP9["tolerancia_relativa"]

CSV_EJEMPLO = Path(__file__).resolve().parent / "ejemplo_puntos.csv"

# NF de prueba, en m. No es un valor de proyecto: es el dato que en una corrida
# real trae la fila del CSV (`punto.exigir("NF_profundidad_m")`), y aqui se fija
# para que el ensamble de empujes tenga con que calcular la subpresion.
NF_DE_PRUEBA = 1.4


@pytest.fixture
def geometria():
    """
    Cabezal de tanteo. NO sale de 'predimensionamiento_cabezal' (vacio): es
    justamente el caso de uso que justifica que la geometria entre por
    argumento -- se propone, se verifica y se corrige sin tocar
    criterios_adoptados.py.
    """
    return GeometriaCabezal(H=2.00, B=1.60, D_f=1.00, espesor_corona=0.25,
                            espesor_base_muro=0.35, espesor_zapata=0.40)


# ===========================================================================
# 9.2 - Cadena sismica desagregada
# ===========================================================================

def test_los_seis_pasos_horizontales_dan_la_cadena_de_la_hoja_de_ruta():
    """PGA -> F_pga -> A_s -> k_h0 -> factor de muro -> k_h."""
    PGA = pga_roca_b()
    Fpga = f_pga()
    A_s = aceleracion_ajustada_sitio(PGA=PGA, F_pga=Fpga)
    k_h0 = coeficiente_sismico_base(A_s=A_s, F_pga=Fpga, PGA=PGA,
                                    cimentacion_en_roca=False)
    k_h = coeficiente_sismico_horizontal(k_h0=k_h0, factor_muro=factor_muro())

    assert PGA == pytest.approx(CP7["PGA"])
    assert Fpga == pytest.approx(CP7["F_pga"])
    assert A_s == pytest.approx(CP7["A_s_esperado"])
    assert k_h0 == pytest.approx(CP7["k_h0_esperado"])
    assert k_h == pytest.approx(CP7["k_h_con_muro_rigido_esperado"])


def test_k_v_va_aparte_y_es_cero():
    """No deriva de la cadena: es una adopcion [A] con su propia fila."""
    assert coeficiente_sismico_vertical() == pytest.approx(CP7["k_v_esperado"])
    assert ca.criterio("k_v").etiqueta == "A"


def test_cada_paso_lee_su_propio_criterio_y_no_un_0_50_escrito_a_mano():
    """
    La razon de ser de la desagregacion: si F_pga baja a 0.9 (clase de sitio E
    cuando llegue el SPT), TODA la cadena se mueve. Un k_h = 0.50 escrito a
    mano no se enteraria.
    """
    cadena = cadena_sismica()
    A_s = aceleracion_ajustada_sitio(PGA=cadena.PGA,
                                     F_pga=CP7["F_pga_clase_E"])
    k_h = coeficiente_sismico_horizontal(
        k_h0=coeficiente_sismico_base(A_s=A_s, F_pga=CP7["F_pga_clase_E"],
                                      PGA=cadena.PGA,
                                      cimentacion_en_roca=False),
        factor_muro=cadena.factor_muro)

    assert A_s == pytest.approx(CP7["A_s_con_F_pga_clase_E_esperado"])
    assert k_h == pytest.approx(CP7["k_h_con_F_pga_clase_E_esperado"])
    assert k_h != pytest.approx(cadena.k_h)


def test_la_cadena_no_se_detiene_por_ningun_vacio():
    """Sus cuatro insumos tienen valor declarado hoy."""
    cadena = cadena_sismica()
    assert cadena.k_h == pytest.approx(cadena.factor_muro * cadena.k_h0)
    assert cadena.k_h0 == pytest.approx(cadena.A_s)
    assert cadena.A_s == pytest.approx(cadena.F_pga * cadena.PGA)


def test_los_pasos_llevan_etiqueta_y_origen_para_M11():
    cadena = cadena_sismica()
    simbolos = [p.simbolo for p in cadena.pasos]
    assert simbolos == ["PGA", "F_pga", "A_s", "k_h0", "factor_muro",
                        "k_h", "k_v"]

    por_simbolo = {p.simbolo: p for p in cadena.pasos}
    # El PGA abre la cadena como dato de sitio [S]: la lectura de un mapa
    # normativo sobre las coordenadas de esta obra, no una constante universal
    assert por_simbolo["PGA"].etiqueta == "S"
    assert por_simbolo["PGA"].criterio == "PGA_roca_B"
    # F_pga es la unica pieza discutible de la cadena: [A] mientras no haya SPT
    assert por_simbolo["F_pga"].etiqueta == "A"
    assert por_simbolo["F_pga"].criterio == "F_pga"
    # k_h0 = A_s es [N] por 2.8.1.1.14.2, no una adopcion
    assert por_simbolo["k_h0"].etiqueta == "N"
    # los calculados no tienen criterio que citar
    assert por_simbolo["A_s"].criterio is None
    assert por_simbolo["k_h"].criterio is None


def test_el_factor_de_muro_reducido_no_se_asume():
    """
    Sec. 9.2: si el muro admitiera 25-50 mm de desplazamiento seria
    k_h = 0.5*k_h0 = 0.25. "No asumirlo en un cabezal empotrado".
    """
    assert factor_muro() == pytest.approx(CP7["factor_muro_rigido"])
    assert cadena_sismica().k_h == pytest.approx(
        CP7["k_h_con_muro_rigido_esperado"])
    # El unico valor [N] del numeral es el 0.5, y ademas es permisivo: lo que
    # es [A] es no acogerse a esa reduccion. El 1.0 no es una fila tabulada,
    # es la ausencia de reduccion (NOR-PUE-07).
    assert REDUCCION_KH_POR_DESPLAZAMIENTO == pytest.approx(
        CP7["factor_muro_desplazable"])
    assert ca.criterio("factor_muro_eleccion").etiqueta == "A"


def test_el_pga_sale_de_datos_de_sitio_y_no_de_un_criterio():
    """
    El docstring de `pga_roca_b` venia diciendo desde el principio que el
    valor "depende de la coordenada sobre la que se lea", que es la definicion
    de [S]. Hasta la quinta etiqueta figuraba como [N], la unica de las cuatro
    que no le corresponde.
    """
    assert pga_roca_b() == pytest.approx(ds.valor("PGA_roca_B"))
    assert ds.dato("PGA_roca_B").etiqueta == "S"
    assert ds.dato("PGA_roca_B").trazabilidad
    with pytest.raises(KeyError):
        ca.valor("PGA_roca_B")


def test_una_eleccion_de_factor_de_muro_fuera_de_la_tabla_es_dato_invalido(monkeypatch):
    """
    La eleccion es [A], pero solo entre las dos filas del numeral: un 0.7
    inventado no es una eleccion, es un valor sin fuente.
    """
    original = ca.CRITERIOS["factor_muro_eleccion"]
    monkeypatch.setitem(
        ca.CRITERIOS, "factor_muro_eleccion",
        original.__class__(**{**original.__dict__, "valor": 0.7}))
    with pytest.raises(DatoInvalidoError):
        factor_muro()


# ===========================================================================
# 9.2 - Mononobe-Okabe
# ===========================================================================

@pytest.mark.parametrize("phi", [25.0, 28.0, 30.0, 34.0, 38.0, 42.0])
def test_caso_limite_mononobe_okabe_es_el_ka_de_rankine(phi):
    """
    La reduccion a Rankine. Con k_h = k_v = 0 e i = beta = delta = 0,
    Mononobe-Okabe tiene que devolver EXACTAMENTE tan^2(45 - phi/2), el Ka
    que cita Sec. 9.2.

    NO ES "EL test de esta formula" NI "si un signo esta cambiado, aqui se
    ve", que es lo que decia este docstring y lo que SIS-F-04 cita como la
    documentacion que afirma lo que el codigo no da. Con los tres angulos en
    cero los cosenos son PARES: doce de los quince mutantes de signo dan aqui
    el mismo double que el original. Los signos los cubre
    `test_k_ae_contra_caso_patron_con_los_seis_parametros_no_nulos`, sobre
    CP9_MONONOBE_OKABE. Este test prueba la reduccion, que tambien hay que
    probar, y solo eso.
    """
    K_AE = k_ae_mononobe_okabe(phi_grados=phi, i_grados=0.0, beta_grados=0.0,
                               delta_grados=0.0, k_h=0.0, k_v=0.0)
    assert K_AE == pytest.approx(ka_rankine(phi_grados=phi), abs=TOL)


@pytest.mark.parametrize("phi", [30.0, 34.0])
def test_k_a_coulomb_coincide_con_rankine_cuando_los_tres_angulos_son_cero(phi):
    assert k_a_coulomb(phi_grados=phi, i_grados=0.0, beta_grados=0.0,
                       delta_grados=0.0) == pytest.approx(
        ka_rankine(phi_grados=phi), abs=TOL)


def test_k_ae_crece_con_k_h():
    """El coeficiente sismico solo puede aumentar el empuje activo."""
    previos = [k_ae_mononobe_okabe(phi_grados=34.0, i_grados=0.0,
                                   beta_grados=0.0, delta_grados=0.0,
                                   k_h=k_h, k_v=0.0)
               for k_h in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5)]
    assert all(anterior <= siguiente
               for anterior, siguiente in zip(previos, previos[1:])), (
        "K_AE tiene que crecer con k_h")
    assert previos[-1] > previos[0]


def test_k_ae_del_proyecto_es_mucho_mayor_que_el_estatico():
    """
    Con k_h = 0.50 el incremento no es un matiz: K_AE mas que duplica a K_A.
    Es la razon por la que la fila sismica de Sec. 9.3 suele gobernar.
    """
    mo = empuje_mononobe_okabe(phi_grados=34.0, i_grados=0.0, beta_grados=0.0,
                               delta_grados=0.0, k_h=0.50, k_v=0.0)
    assert mo.K_A == pytest.approx(ka_rankine(phi_grados=34.0), abs=TOL)
    assert mo.K_AE > 2 * mo.K_A
    assert mo.incremento == pytest.approx(mo.K_AE - mo.K_A)
    assert mo.psi_grados == pytest.approx(math.degrees(math.atan(0.5)))


def test_psi_es_arctan_de_kh_sobre_uno_menos_kv():
    assert angulo_inercia_sismica(k_h=0.0, k_v=0.0) == pytest.approx(0.0)
    assert angulo_inercia_sismica(k_h=0.5, k_v=0.0) == pytest.approx(26.565, abs=1e-3)
    # k_v reduce el denominador y por lo tanto agranda psi
    assert (angulo_inercia_sismica(k_h=0.5, k_v=0.25)
            > angulo_inercia_sismica(k_h=0.5, k_v=0.0))


def test_psi_con_k_v_uno_no_revienta_con_zerodivision():
    """atan2 y no una division: el caso absurdo sale por la puerta correcta."""
    assert angulo_inercia_sismica(k_h=0.5, k_v=1.0) == pytest.approx(90.0)
    with pytest.raises(DisenoNoFactibleError):
        k_ae_mononobe_okabe(phi_grados=34.0, i_grados=0.0, beta_grados=0.0,
                            delta_grados=0.0, k_h=0.5, k_v=1.0)


def test_fuera_del_dominio_sale_DisenoNoFactible_y_no_un_ValueError_de_sqrt():
    """
    phi - psi - i < 0: la cuna activa no encuentra equilibrio. Con k_h = 0.50
    (psi = 26.6 grados) bastan phi = 30 e i = 5 para cruzarlo -- exactamente
    la sensibilidad violenta que declara 'pendiente_relleno_trasdos_i'.
    """
    with pytest.raises(DisenoNoFactibleError) as excinfo:
        k_ae_mononobe_okabe(phi_grados=30.0, i_grados=5.0, beta_grados=0.0,
                            delta_grados=0.0, k_h=0.50, k_v=0.0)
    assert "phi - psi - i" in excinfo.value.motivo


def test_el_borde_exacto_del_dominio_si_tiene_solucion():
    """phi - psi - i = 0 es finito (el radical se anula), no un error."""
    psi = angulo_inercia_sismica(k_h=0.50, k_v=0.0)
    K_AE = k_ae_mononobe_okabe(phi_grados=psi, i_grados=0.0, beta_grados=0.0,
                               delta_grados=0.0, k_h=0.50, k_v=0.0)
    assert math.isfinite(K_AE) and K_AE > 0


def test_delta_mayor_reduce_k_ae():
    """La friccion muro-suelo alivia el empuje: por eso delta no es inocuo."""
    sin_delta = k_ae_mononobe_okabe(phi_grados=35.0, i_grados=0.0,
                                    beta_grados=0.0, delta_grados=0.0,
                                    k_h=0.2, k_v=0.0)
    con_delta = k_ae_mononobe_okabe(phi_grados=35.0, i_grados=0.0,
                                    beta_grados=0.0, delta_grados=17.5,
                                    k_h=0.2, k_v=0.0)
    assert con_delta < sin_delta


def test_k_ae_del_proyecto_se_detiene_en_los_angulos_pendientes():
    with pytest.raises(CriterioPendienteError) as excinfo:
        k_ae_del_proyecto()
    assert excinfo.value.clave in {"phi_relleno_trasdos",
                                   "pendiente_relleno_trasdos_i",
                                   "inclinacion_muro_beta",
                                   "friccion_muro_suelo_delta"}


@pytest.mark.parametrize("clave", ["phi_relleno_trasdos",
                                   "pendiente_relleno_trasdos_i",
                                   "inclinacion_muro_beta",
                                   "friccion_muro_suelo_delta"])
def test_los_cuatro_angulos_de_sec_9_2_estan_declarados_vacios(clave):
    """Sec. 9.2 los exige por su nombre y no los entrega."""
    assert clave in ca.criterios_sin_valor()


# ===========================================================================
# 9.2 - Sobrecarga de trasdos y empujes
# ===========================================================================
# Los dos datos de sitio que la sobrecarga necesita valen None en el
# expediente y por tanto DETIENEN el calculo. Estos ayudantes los declaran a
# valores DE PRUEBA para poder ejercitar el camino; no son una propuesta de
# proyecto y por eso viven aqui y no en datos_sitio.py, igual que los seis
# criterios de tanteo de la cadena sismica.

def _declarar_dato_de_sitio(monkeypatch, clave, valor):
    original = ds.dato(clave)
    monkeypatch.setitem(
        ds.DATOS_SITIO, clave,
        replace(original, valor=valor))


def _declarar_orientacion(monkeypatch, orientacion):
    _declarar_dato_de_sitio(monkeypatch,
                            "orientacion_muro_respecto_al_trafico", orientacion)


def _declarar_borde(monkeypatch, metros):
    _declarar_dato_de_sitio(monkeypatch,
                            "distancia_borde_calzada_al_trasdos_m", metros)



def test_el_0_60_es_el_PISO_del_manual_y_no_el_h_eq_de_diseno():
    """
    El numero no cambia y lo que significa, si. El Manual de Puentes escribe
    «una sobrecarga vertical NO MENOR QUE la equivalente a 0.60 m de altura de
    relleno» (num. 2.4.2.2, pag. impresa 102): es un PISO. El h_eq de diseño
    lo tabula AASHTO por altura y orientacion, y los dos rigen a la vez.
    """
    assert SOBRECARGA_TRASDOS_PISO_MP_M == pytest.approx(0.60)
    # El alias viejo sigue existiendo y sigue valiendo lo mismo: lo que ya no
    # es, es «el h_eq».
    assert SOBRECARGA_TRASDOS_H_EQ == SOBRECARGA_TRASDOS_PISO_MP_M


def test_el_h_eq_se_detiene_si_no_se_declara_la_orientacion_del_muro():
    """
    Conflicto vinculante #4: no hay contradiccion entre el 0.60 del Manual y
    el 1.12 de AASHTO, hay un DATO FALTANTE. Sin la orientacion, la fuente no
    dice cual de sus dos tablas aplica, y el calculo se detiene en vez de
    elegir por su cuenta.
    """
    with pytest.raises(CriterioPendienteError):
        h_eq_sobrecarga_trasdos(altura_muro_total=2.4)


def test_el_h_eq_perpendicular_reproduce_la_interpolacion_de_AASHTO(
        monkeypatch):
    """
    Tabla 3.11.6.4-1, filas 5.0 ft -> 4.0 ft y 10.0 ft -> 3.0 ft, con
    interpolacion lineal obligatoria. Un muro de 2.00 m son 6.5617 ft, y de
    ahi salen 3.6877 ft = 1.124 m: el 1.12 m que la auditoria calculo, contra
    el 0.60 m que el expediente aplicaba (factor 1.87).
    """
    _declarar_orientacion(monkeypatch, ORIENTACION_PERPENDICULAR_AL_TRAFICO)
    # 2.00 m = 6.5617 ft; 4.0 - (6.5617-5.0)/5.0 = 3.6877 ft = 1.1240 m
    esperado = (4.0 - (2.00 / PIE_EN_METROS - 5.0) / 5.0) * PIE_EN_METROS
    assert h_eq_sobrecarga_trasdos(altura_muro_total=2.00) == \
        pytest.approx(esperado)
    assert esperado == pytest.approx(1.1240, abs=1e-4)
    # Y la altura de la primera fila da su valor tabulado sin interpolar.
    assert h_eq_sobrecarga_trasdos(altura_muro_total=5.0 * PIE_EN_METROS) == \
        pytest.approx(4.0 * PIE_EN_METROS)


def test_el_h_eq_paralelo_depende_del_borde_de_calzada_y_el_umbral_es_exacto(
        monkeypatch):
    """
    El umbral de la Tabla 3.11.6.4-2 es «1.0 ft or Further» = 0.3048 m
    EXACTOS. Redondearlo a 0.30 relaja el criterio: un trasdos con el borde a
    0.30 m justos NO alcanza el umbral.

    LO QUE PASA POR DEBAJO DEL UMBRAL YA NO ES LEER LA OTRA COLUMNA: es la
    banda abierta 0 < d < 1.0 ft, que la fuente no cubre y que un criterio [A]
    VACIO detiene. La version anterior de este test afirmaba que 0.30 m daba
    1.3812 m -- la columna de 0.0 ft --, y esa lectura la elegia el codigo en
    duro. Con el criterio declarado, elegirla exige decirlo.
    """
    _declarar_orientacion(monkeypatch, ORIENTACION_PARALELO_AL_TRAFICO)
    _declarar_borde(monkeypatch, 0.35)
    assert h_eq_sobrecarga_trasdos(altura_muro_total=2.00) == \
        pytest.approx(2.0 * PIE_EN_METROS)      # 0.6096 m
    # El umbral EXACTO: 1.0 ft justo sigue siendo «or Further».
    _declarar_borde(monkeypatch, PIE_EN_METROS)
    assert h_eq_sobrecarga_trasdos(altura_muro_total=2.00) == \
        pytest.approx(2.0 * PIE_EN_METROS)
    # 0.30 m NO alcanza el umbral, y ahi la fuente calla: se detiene.
    _declarar_borde(monkeypatch, 0.30)
    with pytest.raises(CriterioPendienteError):
        h_eq_sobrecarga_trasdos(altura_muro_total=2.00)
    # Declarada la lectura, el numero es el de la columna de 0.0 ft.
    ca.establecer_valor_dinamico("h_eq_banda_intermedia_borde", "columna_cero")
    try:
        assert h_eq_sobrecarga_trasdos(altura_muro_total=2.00) == \
            pytest.approx(1.3812, abs=1e-4)
    finally:
        ca.limpiar_valores_dinamicos()
    # Y el borde 0.0 SI esta tabulado: no es banda, es columna.
    _declarar_borde(monkeypatch, 0.0)
    assert h_eq_sobrecarga_trasdos(altura_muro_total=2.00) == \
        pytest.approx(1.3812, abs=1e-4)


def test_el_h_eq_bajo_la_primera_fila_de_la_tabla_se_detiene(monkeypatch):
    """
    AASHTO manda interpolar «for intermediate wall heights» -- ENTRE filas --
    y sus dos tablas arrancan en 5.0 ft = 1.524 m. Por debajo no hay fila con
    que interpolar: es laguna de la fuente, no lectura de la tabla.

    LO ENCONTRO LA AUDITORIA ADVERSARIAL DE S12. El codigo tomaba la primera
    fila en duro con el argumento de que era el lado conservador, y no lo
    decide eso: extrapolar el primer tramo da un h_eq AUN MAYOR. Con muro
    paralelo, borde 0.20 m y altura total 1.20 m las dos lagunas se apilaban y
    la funcion devolvia 1.524 m -- 2.54 veces el piso del Manual -- sin decir
    de donde salia.
    """
    _declarar_orientacion(monkeypatch, ORIENTACION_PERPENDICULAR_AL_TRAFICO)
    with pytest.raises(CriterioPendienteError):
        h_eq_sobrecarga_trasdos(altura_muro_total=1.20)
    # La altura de la primera fila EXACTA no es laguna: la fila existe.
    assert h_eq_sobrecarga_trasdos(altura_muro_total=5.0 * PIE_EN_METROS) == \
        pytest.approx(4.0 * PIE_EN_METROS)
    # Y las dos lecturas declarables dan numeros DISTINTOS, que es por lo que
    # hay que elegir en vez de dejar que el codigo elija.
    ca.establecer_valor_dinamico("h_eq_bajo_altura_tabulada", "primera_fila")
    try:
        primera = h_eq_sobrecarga_trasdos(altura_muro_total=1.20)
    finally:
        ca.limpiar_valores_dinamicos()
    ca.establecer_valor_dinamico("h_eq_bajo_altura_tabulada", "extrapolar_lineal")
    try:
        extrapolada = h_eq_sobrecarga_trasdos(altura_muro_total=1.20)
    finally:
        ca.limpiar_valores_dinamicos()
    assert primera == pytest.approx(4.0 * PIE_EN_METROS)
    assert extrapolada > primera


def test_el_h_eq_nunca_baja_del_piso_peruano(monkeypatch):
    """La regla del mayor de Sec. 0.2, aplicada a la sobrecarga."""
    _declarar_orientacion(monkeypatch, ORIENTACION_PARALELO_AL_TRAFICO)
    _declarar_borde(monkeypatch, 1.0)
    # La columna «1.0 ft or Further» vale 2.0 ft = 0.6096 m en toda la tabla,
    # justo por encima del piso de 0.60 m; con un muro altisimo sigue ahi.
    assert h_eq_sobrecarga_trasdos(altura_muro_total=30.0) >= \
        SOBRECARGA_TRASDOS_PISO_MP_M


def test_la_orientacion_fuera_de_las_dos_tabuladas_es_dato_invalido(
        monkeypatch):
    """
    AASHTO no ofrece un eje libre de orientacion: ofrece dos binomios
    acoplados y no hay tabla para ningun otro caso.
    """
    _declarar_orientacion(monkeypatch, "en_esviaje")
    with pytest.raises(DatoInvalidoError):
        h_eq_sobrecarga_trasdos(altura_muro_total=2.4)


def test_la_presion_de_sobrecarga_usa_el_h_eq_resuelto(monkeypatch):
    _declarar_orientacion(monkeypatch, ORIENTACION_PERPENDICULAR_AL_TRAFICO)
    h_eq = h_eq_sobrecarga_trasdos(altura_muro_total=2.00)
    p = presion_sobrecarga_trasdos(gamma_relleno=19.0, k_a=0.30,
                                   altura_muro_total=2.00)
    assert p == pytest.approx(19.0 * h_eq * 0.30)


def test_el_empuje_de_sobrecarga_es_rectangular_no_triangular(monkeypatch):
    """
    Es la diferencia entre h_eq de relleno EQUIVALENTE y h_eq de relleno real
    encima: la presion es constante en toda la altura.
    """
    _declarar_orientacion(monkeypatch, ORIENTACION_PERPENDICULAR_AL_TRAFICO)
    gamma, k_a, H = 19.0, 0.30, 2.4
    E = empuje_sobrecarga_trasdos(gamma_relleno=gamma, k_a=k_a, H=H)
    assert E == pytest.approx(presion_sobrecarga_trasdos(
        gamma_relleno=gamma, k_a=k_a, altura_muro_total=H) * H)
    # y por lo tanto NO es gamma*H^2*ka/2
    assert E != pytest.approx(empuje_activo_estatico(
        gamma_relleno=gamma, k_a=k_a, H=H))


def test_la_regla_de_H_medios_para_el_trafico():
    assert aplica_sobrecarga_trasdos(distancia_trafico=1.0, H=2.4)
    assert aplica_sobrecarga_trasdos(distancia_trafico=1.2, H=2.4)   # el borde
    assert not aplica_sobrecarga_trasdos(distancia_trafico=1.5, H=2.4)


def test_en_cabezal_bajo_terraplen_siempre_aplica():
    texto = sobrecarga_trasdos_siempre_aplica()
    assert "siempre" in texto
    # El numeral que la declaracion imprime es el CORRECTO, no el retirado
    # (NOR-PUE-01): 2.4.2.2 «Cargas de Suelo: EH, ES, y DD», no 2.1.4.3.9
    # «Aparatos de Apoyo».
    assert "2.4.2.2" in texto and "2.1.4.3.9" not in texto
    # Y la declaracion nombra la exencion que el numeral concede y este
    # expediente no invoca.
    assert "losa de aproximacion" in texto


def test_empuje_activo_estatico_es_triangular():
    gamma, k_a, H = 19.0, 0.30, 2.4
    assert empuje_activo_estatico(gamma_relleno=gamma, k_a=k_a, H=H) == (
        pytest.approx(gamma * H ** 2 * k_a / 2))


# ---------------------------------------------------------------------------
# SIS-F-05 - Los tests de VALOR del empuje del trasdos, contra CP-9
# ---------------------------------------------------------------------------
# Lo que habia era `test_empuje_sismico_total_y_su_incremento` con un unico
# assert, `incremento == pytest.approx(P_AE - P_A)`, y una tautologia:
# `incremento_sismico` calcula justamente P_AE - P_A llamando a las mismas dos
# funciones que el test llama para armar el lado derecho. Cualquier mutante
# dentro de `empuje_activo_sismico_total` se propaga identico a los dos lados
# y la igualdad se sigue cumpliendo. Cuatro mutantes de esa unica linea
# sobrevivian a la suite entera.

def _declarar_criterio(monkeypatch, clave, valor):
    """Declara un criterio [A] vacio a un valor DE PRUEBA, no de proyecto."""
    original = ca.criterio(clave)
    monkeypatch.setitem(ca.CRITERIOS, clave,
                        ca.Criterio(valor=valor, etiqueta=original.etiqueta,
                                    concepto=original.concepto,
                                    justificacion=original.justificacion,
                                    fuente=original.fuente))


def test_empuje_sismico_total_es_gamma_H2_por_1_menos_kv_por_KAE_medios():
    """
    P_AE = gamma*H^2*(1-k_v)*K_AE/2, kN/m (Sec. 9.2), contra el dorado del
    bloque A de CP-9.

    El K_AE entra DADO y no desde Mononobe-Okabe: aqui se prueba la formula
    del empuje, no el coeficiente (eso es el bloque B). Las cuatro entradas
    son distintas entre si y ninguna vale 1 ni 2, que es lo que hace visible
    la diferencia entre multiplicar y dividir.
    """
    c = CP9
    P_AE = empuje_activo_sismico_total(gamma_relleno=c["A_gamma_relleno"],
                                       K_AE=c["A_K_AE"], H=c["A_H"],
                                       k_v=c["A_k_v"])
    assert P_AE == pytest.approx(c["A_P_AE_esperado"], rel=REL_CP9)
    # Y lejos de cada uno de los cuatro mutantes que sobrevivian: el assert de
    # arriba ya los mata, y estos dejan escrito CUALES eran y a que distancia.
    for clave in ("A_mutante_1_mas_kv", "A_mutante_por_dos",
                  "A_mutante_divide_kv", "A_mutante_divide_KAE"):
        assert P_AE != pytest.approx(c[clave], rel=REL_CP9)


def test_el_factor_vertical_es_uno_menos_kv_y_no_uno_mas():
    """
    Con k_v = 0 el factor vale 1 y el mutante (1 + k_v) es indetectable POR
    CONSTRUCCION -- y k_v = 0.0 era lo que usaba el test viejo. Con k_v > 0 la
    aceleracion vertical hacia arriba descarga el relleno: el empuje TIENE que
    bajar, y bajar exactamente en la proporcion (1 - k_v).
    """
    c = CP9
    sin_kv = empuje_activo_sismico_total(gamma_relleno=c["A_gamma_relleno"],
                                         K_AE=c["A_K_AE"], H=c["A_H"], k_v=0.0)
    con_kv = empuje_activo_sismico_total(gamma_relleno=c["A_gamma_relleno"],
                                         K_AE=c["A_K_AE"], H=c["A_H"],
                                         k_v=c["A_k_v"])
    assert con_kv < sin_kv
    assert con_kv == pytest.approx(sin_kv * (1 - c["A_k_v"]), rel=REL_CP9)


def test_empuje_sismico_total_y_su_incremento():
    """
    La cadena coherente del bloque B de CP-9: phi -> psi -> K_AE -> P_AE, y el
    incremento Delta P_AE = P_AE - P_A contrastado contra SU DORADO, no contra
    si mismo (SIS-F-05).
    """
    c = CP9
    mo = empuje_mononobe_okabe(phi_grados=c["B_phi_grados"],
                               i_grados=c["B_i_grados"],
                               beta_grados=c["B_beta_grados"],
                               delta_grados=c["B_delta_grados"],
                               k_h=c["B_k_h"], k_v=c["B_k_v"])
    assert mo.psi_grados == pytest.approx(c["B_psi_grados_esperado"],
                                          rel=REL_CP9)
    assert mo.K_AE == pytest.approx(c["B_K_AE_esperado"], rel=REL_CP9)
    assert mo.K_A == pytest.approx(c["B_K_A_esperado"], rel=REL_CP9)
    assert mo.incremento == pytest.approx(c["B_incremento_K_esperado"],
                                          rel=REL_CP9)

    P_AE = empuje_activo_sismico_total(gamma_relleno=c["B_gamma_relleno"],
                                       K_AE=mo.K_AE, H=c["B_H"], k_v=mo.k_v)
    P_A = empuje_activo_estatico(gamma_relleno=c["B_gamma_relleno"],
                                 k_a=mo.K_A, H=c["B_H"])
    incremento = incremento_sismico(gamma_relleno=c["B_gamma_relleno"],
                                    K_AE=mo.K_AE, K_A=mo.K_A, H=c["B_H"],
                                    k_v=mo.k_v)
    assert P_AE == pytest.approx(c["B_P_AE_esperado"], rel=REL_CP9)
    assert P_A == pytest.approx(c["B_P_A_esperado"], rel=REL_CP9)
    assert incremento == pytest.approx(c["B_incremento_P_esperado"],
                                       rel=REL_CP9)
    # El incremento es la PARTE sismica del total: positivo y menor que P_AE.
    assert 0 < incremento < P_AE


def test_empuje_activo_estatico_contra_su_dorado():
    """
    P_A = gamma*H^2*K_A/2, kN/m (Sec. 9.2), contra el dorado del bloque B.
    El test hermano (`..._es_triangular`) reescribe la formula en el propio
    assert: comprueba la transcripcion, no el valor. Este cierra el circulo
    con un numero recalculado fuera del repo.
    """
    c = CP9
    assert empuje_activo_estatico(gamma_relleno=c["B_gamma_relleno"],
                                  k_a=c["B_K_A_esperado"],
                                  H=c["B_H"]) == pytest.approx(
        c["B_P_A_esperado"], rel=REL_CP9)


def test_el_brazo_del_incremento_sismico_es_la_fraccion_por_H(monkeypatch):
    """
    Declarado el criterio, z = fraccion * H (Sec. 9.2). La fraccion (0.6) y H
    (2.4) son distintas y ninguna vale 1: multiplicar da 1.44 m y dividir
    daria 0.25 m. Complementa a `..._no_se_inventa`, que prueba el camino SIN
    declarar (`CriterioPendienteError`).
    """
    _declarar_criterio(monkeypatch, "punto_aplicacion_incremento_sismico",
                       CP9["B_brazo_fraccion"])
    assert brazo_incremento_sismico(H=CP9["B_H"]) == pytest.approx(
        CP9["B_z_incremento_esperado"], rel=REL_CP9)


def test_el_agua_no_lleva_coeficiente_de_empuje():
    """
    El error clasico del trasdos con freatico: multiplicar el empuje del agua
    por Ka. E_w = gamma_agua * h^2 / 2, sin coeficiente.
    """
    h = 1.2
    assert empuje_hidrostatico(h_agua=h) == pytest.approx(
        GAMMA_AGUA_KN_M3 * h ** 2 / 2)


def test_subpresion_uniforme_en_todo_el_ancho_de_zapata():
    assert subpresion(h_agua=1.2, B=1.6) == pytest.approx(
        GAMMA_AGUA_KN_M3 * 1.2 * 1.6)


def test_altura_de_agua_usa_el_NF_del_punto_y_no_baja_de_cero():
    """
    El NF entra por argumento: es la columna 'NF_profundidad_m' del CSV, dato
    de sitio [S] medido en cada cruce, no un criterio unico de proyecto.
    """
    NF = 1.4
    assert altura_agua_sobre_base(D_f=2.0, NF_profundidad_m=NF) == pytest.approx(0.6)
    # zapata sobre el freatico: no hay agua que empujar
    assert altura_agua_sobre_base(D_f=1.0, NF_profundidad_m=NF) == pytest.approx(0.0)


def test_dos_puntos_con_NF_distinto_dan_alturas_de_agua_distintas():
    """
    Lo que el criterio unico de tramo no podia expresar: el mismo desplante
    con el freatico a distinta profundidad da distinta subpresion, y cada
    cabezal se calcula con el NF de su cruce.
    """
    somero = altura_agua_sobre_base(D_f=2.0, NF_profundidad_m=0.8)
    profundo = altura_agua_sobre_base(D_f=2.0, NF_profundidad_m=1.4)
    assert somero > profundo
    assert somero == pytest.approx(1.2)


def test_sin_NF_medido_el_punto_se_detiene_en_vez_de_asumirlo():
    """
    Un punto cuyo estudio geotecnico todavia no dio el NF no se calcula con un
    valor plausible: `exigir` lanza DatoFaltanteError, que es lo que un
    criterio unico de tramo escondia detras de un 1.4 m para todos.
    """
    punto = cargar_puntos(CSV_EJEMPLO)[0]
    assert punto.NF_profundidad_m is None
    with pytest.raises(DatoFaltanteError) as excinfo:
        punto.exigir("NF_profundidad_m")
    assert excinfo.value.campo == "NF_profundidad_m"


def test_el_peso_propio_calcula_con_el_gamma_de_concreto_declarado(geometria):
    """
    'peso_especifico_concreto_kn_m3' es [C] (AASHTO LRFD Tabla 3.5.1-1,
    23.56 kN/m3): el peso propio ya no se detiene, calcula directo.
    """
    W = peso_propio_cabezal(geometria=geometria)
    gamma_c = ca.valor("peso_especifico_concreto_kn_m3")
    assert gamma_c == pytest.approx(23.56)
    assert W == pytest.approx(
        gamma_c * ((geometria.espesor_corona + geometria.espesor_base_muro)
                   / 2 * geometria.H + geometria.B * geometria.espesor_zapata))


def test_el_relleno_del_trasdos_es_el_mismo_criterio_que_usa_M8():
    """Un cabezal con un relleno y un conducto con otro es incoherente."""
    with pytest.raises(CriterioPendienteError) as excinfo:
        peso_especifico_relleno()
    assert excinfo.value.clave == "peso_especifico_relleno_kn_m3"


def test_el_ensamble_de_empujes_se_detiene_en_el_primer_vacio(geometria):
    with pytest.raises(CriterioPendienteError):
        empujes_trasdos(geometria=geometria,
                        condicion=CondicionAnalisis.ESTATICO,
                        altura_empuje=geometria.altura_total,
                        NF_profundidad_m=NF_DE_PRUEBA)


def test_la_altura_total_incluye_el_canto_de_la_zapata(geometria):
    assert geometria.altura_total == pytest.approx(
        geometria.H + geometria.espesor_zapata)
    assert geometria.altura_total > geometria.H


def test_el_brazo_del_incremento_sismico_no_se_inventa():
    """Mononobe-Okabe da el empuje, no su punto de aplicacion."""
    with pytest.raises(CriterioPendienteError) as excinfo:
        brazo_incremento_sismico(H=2.4)
    assert excinfo.value.clave == "punto_aplicacion_incremento_sismico"


# ===========================================================================
# 9.2 - Combinaciones AASHTO LRFD
# ===========================================================================

def test_las_tres_combinaciones_de_la_hoja_de_ruta():
    nombres = [c.nombre for c in combinaciones()]
    assert nombres == ["Resistencia I", "Servicio I", "Evento Extremo I"]
    assert list(COMBINACIONES_AASHTO) == nombres


def test_solo_evento_extremo_lleva_carga_sismica():
    por_nombre = {c.nombre: c for c in combinaciones()}
    assert "EQ" in por_nombre["Evento Extremo I"].componentes
    assert "EQ" not in por_nombre["Resistencia I"].componentes
    assert "EQ" not in por_nombre["Servicio I"].componentes


def test_la_sobrecarga_LS_esta_en_las_tres():
    """La de 0.60 m equivalente: en un cabezal bajo terraplen siempre aplica."""
    for combinacion in combinaciones():
        assert "LS" in combinacion.componentes


def test_describir_las_combinaciones_no_se_detiene_y_evaluarlas_tampoco():
    """
    Las tablas de factores de carga son [N] y la eleccion de fila esta
    declarada: ya no se detiene.

    EL gamma_EV MINIMO DEL CABEZAL ES 1.00 Y NO 0.90 (NOR-PUE-03). M9 modela
    el cabezal como muro de contencion, y la fila "Muros y estribos de
    retencion" de la Tabla 2.4.5.3.1-2 da 1.35 / 1.00. El 0.90 que este test
    exigia antes es de "Estructura rigida enterrada", la fila del CONDUCTO.

    El cambio RELAJA volteo y deslizamiento alrededor de un 8 %: el empuje
    vertical de tierra sobre el talon estabiliza, y minorar lo que estabiliza
    es la direccion conservadora. Se corrige igual porque el par anterior no
    era ninguna fila de la tabla y porque C3.4.1 de AASHTO prescribe ese 1.00
    para el deslizamiento de un muro en voladizo. Queda dicho aqui para que
    nadie lea este test como la prueba de que el expediente se endurecio.
    """
    assert len(combinaciones()) == 3          # describir: los nombres son [N]

    resistencia = factores_de_carga("Resistencia I")
    assert resistencia["DC"] == pytest.approx({"max": 1.25, "min": 0.90},
                                              rel=REL_TRANSPORTE)
    assert resistencia["EV"] == pytest.approx({"max": 1.35, "min": 1.00},
                                              rel=REL_TRANSPORTE)
    assert resistencia["EH"] == pytest.approx({"max": 1.50, "min": 0.90},
                                              rel=REL_TRANSPORTE)
    assert resistencia["LS"] == pytest.approx(1.75)

    servicio = factores_de_carga("Servicio I")
    assert servicio["DC"] == pytest.approx({"max": 1.00, "min": 1.00},
                                           rel=REL_TRANSPORTE)

    extremo = factores_de_carga("Evento Extremo I")
    assert extremo["EQ"] == pytest.approx({"max": 1.00, "min": 1.00},
                                          rel=REL_TRANSPORTE)
    assert extremo["LS"] == "gamma_EQ"       # a criterio del propietario


def test_una_combinacion_inventada_es_dato_invalido_no_criterio_pendiente():
    with pytest.raises(DatoInvalidoError):
        factores_de_carga("Resistencia III")


# ===========================================================================
# 9.3 - Estabilidad (E.050)
# ===========================================================================

@pytest.mark.parametrize("clave, estatico, sismico", [
    ("capacidad_portante", 3.00, 2.50),
    ("volteo", 1.50, 1.25),
    ("deslizamiento", 1.50, 1.25),
    ("estabilidad_global", 1.50, 1.25),
    ("talud", 1.50, 1.25),
])
def test_los_FS_son_los_de_la_tabla_de_sec_9_3(clave, estatico, sismico):
    assert fs_requerido(verificacion=clave,
                        condicion=CondicionAnalisis.ESTATICO) == estatico
    assert fs_requerido(verificacion=clave,
                        condicion=CondicionAnalisis.SISMICO) == sismico
    assert FS[clave] == {"estatico": estatico, "sismico": sismico}


def test_una_fila_inexistente_de_la_tabla_es_dato_invalido():
    with pytest.raises(DatoInvalidoError):
        fs_requerido(verificacion="pandeo", condicion=CondicionAnalisis.ESTATICO)


def test_volteo_cumple_en_estatico_y_no_en_sismico_con_el_mismo_FS():
    """
    Un FS de 1.30 pasa el umbral sismico (1.25) y no el estatico (1.50): el
    mismo numero, dos veredictos. Por eso la condicion viaja en la llamada.
    """
    estatico = verificar_volteo(momento_estabilizante=130.0,
                                momento_volcante=100.0,
                                condicion=CondicionAnalisis.ESTATICO)
    sismico = verificar_volteo(momento_estabilizante=130.0,
                               momento_volcante=100.0,
                               condicion=CondicionAnalisis.SISMICO)
    assert not estatico.cumple and sismico.cumple
    assert estatico.valor_obtenido == pytest.approx(1.30)
    assert estatico.valor_admisible == pytest.approx(1.50, rel=REL_TRANSPORTE)
    assert sismico.valor_admisible == pytest.approx(1.25, rel=REL_TRANSPORTE)
    assert estatico.codigo == "E2" and sismico.codigo == "E2"


def test_las_verificaciones_llevan_numeral_y_no_criterio_adoptado():
    """Los FS son [N] literales: `criterio_aplicado` tiene que ser None."""
    v = verificar_deslizamiento(fuerza_resistente=90.0, fuerza_actuante=50.0,
                                condicion=CondicionAnalisis.ESTATICO)
    assert v.criterio_aplicado is None
    assert "39.13.6 a" in v.numeral
    assert v.cumple and v.codigo == "E3"


def test_capacidad_portante_es_q_ultima_sobre_q_actuante():
    v = verificar_capacidad_portante(q_actuante=100.0, q_ultima=310.0,
                                     condicion=CondicionAnalisis.ESTATICO)
    assert v.valor_obtenido == pytest.approx(3.10)
    assert v.cumple and v.codigo == "E1"
    assert "Art. 21" in v.numeral


def test_una_presion_de_contacto_nula_es_dato_invalido():
    with pytest.raises(DatoInvalidoError):
        verificar_capacidad_portante(q_actuante=0.0, q_ultima=310.0,
                                     condicion=CondicionAnalisis.ESTATICO)


def test_sin_momento_volcante_el_FS_es_infinito_y_no_una_division_por_cero():
    v = verificar_volteo(momento_estabilizante=100.0, momento_volcante=0.0,
                         condicion=CondicionAnalisis.SISMICO)
    assert v.cumple and math.isinf(v.valor_obtenido)


def test_los_dos_unicos_inf_deliberados_del_repositorio_siguen_ahi():
    """
    EL CONTRAPESO DE SIS-G-01, y por eso vive aqui y no en M7.

    S16.5 puso guardas de finitud a la salida del calculo, y el riesgo obvio
    de esa clase de guarda es barrer de paso los `inf` que SI significan algo.
    En este repositorio son exactamente DOS, los dos en M9 y los dos por la
    misma razon: un FS infinito no es un numero grande, es la AUSENCIA de la
    solicitacion -- sin momento volcante no hay volteo posible, sin fuerza
    actuante no hay deslizamiento posible.

    Por eso `M7._exigir_finito` vive solo en M7 y no hay barrido global. Este
    test fija el censo: si alguna vez alguien generaliza la guarda a todo el
    calculo, cae aqui antes de llegar a la memoria.

    El docstring de `criterios_adoptados._verificar_finitud` nombraba solo a
    `verificar_volteo`; son los dos, y S16.5 lo corrigio ahi tambien.
    """
    volteo = verificar_volteo(momento_estabilizante=100.0, momento_volcante=0.0,
                              condicion=CondicionAnalisis.ESTATICO)
    deslizamiento = verificar_deslizamiento(fuerza_resistente=100.0,
                                            fuerza_actuante=0.0,
                                            condicion=CondicionAnalisis.ESTATICO)
    for v in (volteo, deslizamiento):
        assert math.isinf(v.valor_obtenido), (
            "un FS sin solicitacion es infinito a proposito: si esto deja de "
            "serlo, alguna guarda de finitud se paso de alcance")
        assert v.cumple


def test_el_agregado_devuelve_E1_a_E3_en_una_condicion(geometria):
    estabilidad = verificar_estabilidad(
        geometria=geometria, condicion=CondicionAnalisis.SISMICO,
        q_actuante=100.0, q_ultima=300.0,
        momento_estabilizante=200.0, momento_volcante=100.0,
        fuerza_resistente=80.0, fuerza_actuante=50.0)

    assert [v.codigo for v in estabilidad.verificaciones] == ["E1", "E2", "E3"]
    assert estabilidad.estable
    assert estabilidad.condicion is CondicionAnalisis.SISMICO


def test_el_agregado_marca_las_incumplidas(geometria):
    estabilidad = verificar_estabilidad(
        geometria=geometria, condicion=CondicionAnalisis.ESTATICO,
        q_actuante=100.0, q_ultima=200.0,       # FS = 2.0 < 3.0
        momento_estabilizante=200.0, momento_volcante=100.0,
        fuerza_resistente=80.0, fuerza_actuante=50.0)

    assert not estabilidad.estable
    assert [v.codigo for v in estabilidad.verificaciones_incumplidas] == ["E1"]


def test_incluir_las_globales_detiene_el_agregado(geometria):
    with pytest.raises(CriterioPendienteError) as excinfo:
        verificar_estabilidad(
            geometria=geometria, condicion=CondicionAnalisis.ESTATICO,
            q_actuante=100.0, q_ultima=400.0,
            momento_estabilizante=200.0, momento_volcante=100.0,
            fuerza_resistente=80.0, fuerza_actuante=50.0,
            incluir_globales=True)
    assert excinfo.value.clave == "metodo_estabilidad_global"


@pytest.mark.parametrize("funcion", [verificar_estabilidad_global, verificar_talud])
def test_E4_y_E5_tienen_umbral_pero_no_metodo(funcion):
    """El FS esta transcrito; con que producir el valor a comparar, no."""
    with pytest.raises(CriterioPendienteError) as excinfo:
        funcion(condicion=CondicionAnalisis.ESTATICO)
    assert excinfo.value.clave == "metodo_estabilidad_global"


# --- E3 deslizamiento: los asserts de VALOR que faltaban (SIS-F-06) --------

def test_deslizamiento_cumple_en_sismico_y_no_en_estatico_con_el_mismo_FS():
    """
    Gemelo de `test_volteo_cumple_en_estatico_y_no_en_sismico_con_el_mismo_FS`
    para E3, que era la unica de las tres filas vivas sin assert de valor
    (SIS-F-06): FS = F_resistente / F_actuante = 65/50 = 1.30 pasa el umbral
    sismico (1.25) y no el estatico (1.50).
    """
    estatico = verificar_deslizamiento(fuerza_resistente=65.0,
                                       fuerza_actuante=50.0,
                                       condicion=CondicionAnalisis.ESTATICO)
    sismico = verificar_deslizamiento(fuerza_resistente=65.0,
                                      fuerza_actuante=50.0,
                                      condicion=CondicionAnalisis.SISMICO)

    assert estatico.valor_obtenido == pytest.approx(1.30, abs=TOL)
    assert sismico.valor_obtenido == pytest.approx(1.30, abs=TOL)
    assert estatico.valor_admisible == pytest.approx(
        FS["deslizamiento"]["estatico"], abs=TOL)
    assert sismico.valor_admisible == pytest.approx(
        FS["deslizamiento"]["sismico"], abs=TOL)
    assert not estatico.cumple and sismico.cumple
    assert estatico.codigo == "E3" and sismico.codigo == "E3"
    assert estatico.criterio_aplicado is None
    assert "39.13.6 a" in estatico.numeral


def test_el_FS_de_deslizamiento_es_el_cociente_y_no_el_producto():
    """
    El mutante que SIS-F-06 documenta -- `fs = R * A` -- da 4500 donde la
    division da 1.80. Se fija el cociente con dos pares que comparten
    producto y no cociente.
    """
    uno = verificar_deslizamiento(fuerza_resistente=90.0, fuerza_actuante=50.0,
                                  condicion=CondicionAnalisis.ESTATICO)
    otro = verificar_deslizamiento(fuerza_resistente=50.0, fuerza_actuante=90.0,
                                   condicion=CondicionAnalisis.ESTATICO)
    assert uno.valor_obtenido == pytest.approx(1.8, abs=TOL)
    assert otro.valor_obtenido == pytest.approx(0.5555555555555556, abs=TOL)
    assert uno.cumple and not otro.cumple


def test_sin_fuerza_actuante_el_FS_de_deslizamiento_es_infinito():
    """
    Gemelo de `test_sin_momento_volcante_el_FS_es_infinito...` para E3: con
    F_actuante = 0 no hay deslizamiento posible y el FS es infinito. Mata las
    dos mutaciones de la guarda: `> 0` (que manda el 0.0 a la division) y
    `< 0` (idem).
    """
    v = verificar_deslizamiento(fuerza_resistente=90.0, fuerza_actuante=0.0,
                                condicion=CondicionAnalisis.SISMICO)
    assert math.isinf(v.valor_obtenido) and v.valor_obtenido > 0
    assert v.cumple and v.codigo == "E3"


def test_con_fuerza_actuante_negativa_el_FS_de_deslizamiento_sigue_infinito():
    """La guarda es `<= 0`, no `== 0`: un actuante negativo tampoco desliza."""
    v = verificar_deslizamiento(fuerza_resistente=90.0, fuerza_actuante=-10.0,
                                condicion=CondicionAnalisis.ESTATICO)
    assert math.isinf(v.valor_obtenido) and v.cumple


# --- E2 volteo: lo que faltaba del gemelo ----------------------------------

def test_el_volteo_lleva_numeral_de_E050_y_no_criterio_adoptado():
    """
    E2 tenia assert de valor pero no de numeral ni de `criterio_aplicado`:
    los FS de Sec. 9.3 son [N] puros.
    """
    v = verificar_volteo(momento_estabilizante=130.0, momento_volcante=100.0,
                         condicion=CondicionAnalisis.ESTATICO)
    assert v.criterio_aplicado is None
    assert "39.13.6 a" in v.numeral


def test_el_FS_de_volteo_es_el_cociente_y_no_el_producto():
    uno = verificar_volteo(momento_estabilizante=200.0, momento_volcante=100.0,
                           condicion=CondicionAnalisis.ESTATICO)
    otro = verificar_volteo(momento_estabilizante=100.0, momento_volcante=200.0,
                            condicion=CondicionAnalisis.ESTATICO)
    assert uno.valor_obtenido == pytest.approx(2.0, abs=TOL)
    assert otro.valor_obtenido == pytest.approx(0.5, abs=TOL)
    assert uno.cumple and not otro.cumple


# --- El borde de TOL_UMBRAL_NORMATIVO en _verificacion_por_fs (SIS-F-21) ---

def test_el_borde_de_la_tolerancia_del_umbral_cumple_y_mil_veces_mas_no():
    """
    SIS-F-21, la parte de M9. `_verificacion_por_fs` resta la tolerancia del
    lado ADMISIBLE, que aqui es una cota inferior. La banda
    [requerido - TOL, requerido) no la alcanza ningun FS de diseno -- 1e-9
    sobre un FS de orden 1 --, pero SI la alcanza una entrada de unidad, y es
    lo unico que fija de que lado se aplica la tolerancia.

    Mata tres mutantes de una vez: signo invertido (`requerido + TOL`),
    tolerancia borrada (`>= requerido`) y comparacion estricta
    (`> requerido - TOL`).
    """
    requerido = fs_requerido(verificacion="deslizamiento",
                             condicion=CondicionAnalisis.ESTATICO)

    borde = verificar_deslizamiento(
        fuerza_resistente=requerido - TOL_UMBRAL_NORMATIVO,
        fuerza_actuante=1.0, condicion=CondicionAnalisis.ESTATICO)
    assert borde.cumple and borde.codigo == "E3"

    fuera = verificar_deslizamiento(
        fuerza_resistente=requerido - TOL_MIL_VECES_EL_UMBRAL,
        fuerza_actuante=1.0, condicion=CondicionAnalisis.ESTATICO)
    assert not fuera.cumple


def test_el_borde_de_la_tolerancia_vale_igual_para_el_volteo():
    """La banda vive en `_verificacion_por_fs`: E2 y E3 la comparten."""
    requerido = fs_requerido(verificacion="volteo",
                             condicion=CondicionAnalisis.SISMICO)

    borde = verificar_volteo(
        momento_estabilizante=requerido - TOL_UMBRAL_NORMATIVO,
        momento_volcante=1.0, condicion=CondicionAnalisis.SISMICO)
    assert borde.cumple and borde.codigo == "E2"

    fuera = verificar_volteo(
        momento_estabilizante=requerido - TOL_MIL_VECES_EL_UMBRAL,
        momento_volcante=1.0, condicion=CondicionAnalisis.SISMICO)
    assert not fuera.cumple


# --- El agregado propaga la condicion a las tres filas ---------------------

def test_el_agregado_propaga_la_condicion_a_las_tres_filas(geometria):
    """
    Las tres verificaciones tienen que leer el umbral de la MISMA condicion
    que se le pidio al agregado: con FS entre los dos umbrales, el veredicto
    de las tres cambia de condicion a condicion.
    """
    demandas = dict(geometria=geometria,
                    q_actuante=100.0, q_ultima=260.0,      # E1 = 2.60
                    momento_estabilizante=130.0, momento_volcante=100.0,
                    fuerza_resistente=65.0, fuerza_actuante=50.0)

    sismico = verificar_estabilidad(condicion=CondicionAnalisis.SISMICO,
                                    **demandas)
    estatico = verificar_estabilidad(condicion=CondicionAnalisis.ESTATICO,
                                     **demandas)

    assert [v.valor_obtenido for v in sismico.verificaciones] == [
        pytest.approx(2.60, abs=TOL), pytest.approx(1.30, abs=TOL),
        pytest.approx(1.30, abs=TOL)]
    assert [v.valor_admisible for v in sismico.verificaciones] == [
        pytest.approx(2.50, abs=TOL), pytest.approx(1.25, abs=TOL),
        pytest.approx(1.25, abs=TOL)]
    assert [v.valor_admisible for v in estatico.verificaciones] == [
        pytest.approx(3.00, abs=TOL), pytest.approx(1.50, abs=TOL),
        pytest.approx(1.50, abs=TOL)]
    assert sismico.estable
    assert [v.codigo for v in estatico.verificaciones_incumplidas] == [
        "E1", "E2", "E3"]


# --- E.050 Art. 20: c y phi no se combinan --------------------------------

def test_en_cohesivo_phi_se_anula():
    c, phi = parametros_resistencia_art20(c=25.0, phi_grados=28.0, cohesivo=True)
    assert (c, phi) == pytest.approx((25.0, 0.0), abs=ABS_CERO)


def test_en_friccionante_c_se_anula():
    c, phi = parametros_resistencia_art20(c=25.0, phi_grados=32.0, cohesivo=False)
    assert (c, phi) == pytest.approx((0.0, 32.0), abs=ABS_CERO)


# --- Zapata proxima al talud ----------------------------------------------

def test_N_q_es_cero_en_zapata_proxima_al_talud():
    assert n_q_zapata_en_talud() == pytest.approx(0.0)
    assert NQ_ZAPATA_EN_TALUD == pytest.approx(0.0, abs=ABS_CERO)


def test_N_s_es_cero_si_B_menor_que_Hs():
    assert n_s_zapata_en_talud(B=1.6, H_s=3.0, gamma=19.0, c=20.0) == pytest.approx(0.0, abs=ABS_CERO)


def test_N_s_es_gamma_Hs_sobre_c_si_B_mayor_o_igual_que_Hs():
    assert n_s_zapata_en_talud(B=4.0, H_s=3.0, gamma=19.0,
                               c=20.0) == pytest.approx(19.0 * 3.0 / 20.0)


def test_N_s_con_c_cero_dice_que_hacer_en_vez_de_devolver_infinito():
    """Suelo friccionante (Art. 20): el caso es del abaco de N_gamma_q."""
    with pytest.raises(DatoInvalidoError) as excinfo:
        n_s_zapata_en_talud(B=4.0, H_s=3.0, gamma=19.0, c=0.0)
    assert "N_cq_N_gammaq_meyerhof" in str(excinfo.value)


def test_la_capacidad_portante_en_talud_se_detiene_en_los_abacos():
    """
    No hay via alternativa: usar N_c y N_gamma de terreno horizontal es
    exactamente la sobrestimacion que Sec. 9.3 advierte.
    """
    with pytest.raises(CriterioPendienteError) as excinfo:
        capacidad_portante_zapata_en_talud(B=1.6, H_s=3.0, gamma=19.0,
                                           c=0.0, phi_grados=32.0)
    assert excinfo.value.clave == "N_cq_N_gammaq_meyerhof"


def test_la_geometria_por_criterio_esta_vacia_pero_la_del_tanteo_no(geometria):
    """Tantear no exige editar criterios_adoptados.py; dimensionar solo, si."""
    assert geometria.B > 0
    with pytest.raises(CriterioPendienteError) as excinfo:
        geometria_adoptada()
    assert excinfo.value.clave == "predimensionamiento_cabezal"


# ===========================================================================
# 9.4 - Refuerzo, recubrimientos y durabilidad
# ===========================================================================

@pytest.mark.parametrize("condicion, mm", [
    ("contra_suelo", 70), ("suelo_intemperie_ge_3_4", 50),
    ("suelo_intemperie_le_5_8", 40),
])
def test_recubrimientos_de_E060_art_7_7_1(condicion, mm):
    assert recubrimiento_e060_mm(condicion=condicion) == pytest.approx(mm)
    assert RECUBRIMIENTO[condicion] == mm


def test_una_condicion_inexistente_es_dato_invalido():
    with pytest.raises(DatoInvalidoError):
        recubrimiento_e060_mm(condicion="sumergido")


def test_el_lado_aashto_de_la_regla_del_mayor_se_calcula_y_no_se_declara():
    """
    Cluster C07. El lado AASHTO ya no es un valor de tabla declarado: sale de
    tabla x factor por relacion a/c, con el piso de 1.0 in. Con la corrida de
    pruebas declarando categoria "A" y a/c = 0.40 (fila de cloruros de la
    Tabla 4.2), las tres condiciones de E.060 leen 76.2 x 0.8 = 60.96 mm -- no
    los 75 mm de antes, que eran los 3.0 in redondeados a la baja y sin el
    modificador del Art. 5.10.1.
    """
    esperado = 76.2 * 0.8
    for condicion in ("contra_suelo", "suelo_intemperie_ge_3_4",
                      "suelo_intemperie_le_5_8"):
        assert recubrimiento_aashto_mm(condicion=condicion) == pytest.approx(esperado)


def test_la_regla_del_recubrimiento_mayor_ya_se_evalua_con_los_dos_operandos():
    """
    Sec. 0.2: "rige el recubrimiento MAYOR entre AASHTO y E.060". LA
    CONCLUSION SE INVIERTE respecto de lo que este test comprobaba antes, y es
    el resultado del cluster C07: con el lado AASHTO en 60.96 mm, E.060
    gobierna el caso "contra el suelo" con sus 70 mm, y AASHTO sigue
    gobernando las dos condiciones de intemperie (50 y 40 mm).
    """
    contra_suelo = recubrimiento_de_diseno(condicion="contra_suelo")
    assert contra_suelo.aashto_mm == pytest.approx(60.96)
    assert contra_suelo.adoptado_mm == pytest.approx(70.0)
    assert contra_suelo.origen == "E.060"
    # la cadena que produjo el lado AASHTO viaja en el resultado: sin ella el
    # numero vuelve a ser un valor que hay que creer, que es como sobrevivio
    # el 75 mm con una columna y un modificador de menos
    assert contra_suelo.situacion == "vaciado_contra_suelo"
    assert contra_suelo.categoria == "A"
    assert contra_suelo.tabulado_mm == pytest.approx(76.2)
    assert contra_suelo.factor_ac == pytest.approx(0.8)

    for condicion in ("suelo_intemperie_ge_3_4", "suelo_intemperie_le_5_8"):
        r = recubrimiento_de_diseno(condicion=condicion)
        assert r.adoptado_mm == pytest.approx(60.96)
        assert r.origen == "AASHTO"
        assert r.e060_mm == RECUBRIMIENTO[condicion]


def test_la_regla_del_mayor_toma_el_aashto_cuando_gobierna():
    """
    Se cambia la categoria de acero para mover el lado AASHTO y comprobar la
    REGLA, que es lo que este modulo aporta. Con acero epoxico o galvanizado
    la tabla da 2.0 in = 50.8 mm y el factor los deja en 40.64: E.060 pasa a
    gobernar tambien la condicion de intemperie de barras >= 3/4" (50 mm) y
    sigue perdiendo en la de barras <= 5/8" (40 mm). Es exactamente la
    inversion que el conflicto #3 del plan anticipaba.
    """
    ca.establecer_valor_dinamico("categoria_refuerzo_aashto", "B")
    try:
        manda_e060 = recubrimiento_de_diseno(condicion="suelo_intemperie_ge_3_4")
        assert manda_e060.aashto_mm == pytest.approx(50.8 * 0.8)
        assert manda_e060.adoptado_mm == pytest.approx(50.0)
        assert manda_e060.origen == "E.060"

        manda_aashto = recubrimiento_de_diseno(condicion="suelo_intemperie_le_5_8")
        assert manda_aashto.adoptado_mm == pytest.approx(40.64)
        assert manda_aashto.origen == "AASHTO"
        # los dos operandos viajan en el resultado, no solo el ganador
        assert manda_aashto.e060_mm == pytest.approx(40.0, rel=REL_TRANSPORTE)
    finally:
        ca.establecer_valor_dinamico("categoria_refuerzo_aashto", "A")


@pytest.fixture
def vaciar_criterio(monkeypatch):
    """Deja un criterio sin valor en el archivo, como estaba antes de cerrarse."""
    def _vaciar(clave):
        original = ca.CRITERIOS[clave]
        monkeypatch.setitem(ca.CRITERIOS, clave,
                            original.__class__(**{**original.__dict__,
                                                  "valor": None}))
    return _vaciar


@pytest.mark.parametrize("clave", ["categoria_refuerzo_aashto",
                                   "exposicion_quimica_ems"])
def test_los_dos_vacios_del_recubrimiento_detienen_el_calculo(
        clave, vaciar_criterio):
    """
    LA AFIRMACION CENTRAL DE C07, comprobada y no solo escrita: sin la
    categoria de acero y sin el analisis quimico del EMS, el recubrimiento no
    se calcula. Hasta aqui esas dos detenciones vivian en la prosa de los
    docstrings; una corrida de pruebas las declara en el conftest y por eso
    el resto de la suite no las ve nunca.

    Se comprueban las dos claves porque bloquean por caminos distintos: la
    categoria decide la columna de la tabla, y la exposicion quimica entra
    por el factor de relacion a/c, dos eslabones separados de la misma
    cadena. Que una detenga no dice nada de la otra.
    """
    vaciar_criterio(clave)
    ca.quitar_valor_dinamico(clave)
    with pytest.raises(CriterioPendienteError) as exc:
        recubrimiento_de_diseno(condicion="contra_suelo")
    assert exc.value.clave == clave


def test_una_fila_no_declarada_de_la_tabla_4_2_no_se_lee_como_un_no(
        vaciar_criterio):
    """
    LA REGLA NUCLEAR, en el punto exacto donde se estaba incumpliendo. El dato
    se leia con `.get("cloruros_tabla_4_2")`: una clave ausente daba None,
    None es falso, y el calculo continuaba como si el EMS hubiera dicho que no
    hay cloruros. Con eso desaparecian sin ruido la a/c <= 0.40 y el
    f'c >= 35 MPa de esa fila.

    La ausencia de una lectura no es una lectura negativa: es
    DatoInvalidoError, y quien cierre el expediente tiene que anadir el
    ensayo que falta -- no corregir un numero, que es la frontera con
    DatoFaltanteError que este proyecto usa.
    """
    vaciar_criterio("exposicion_quimica_ems")
    ca.establecer_valor_dinamico(
        "exposicion_quimica_ems",
        {"so4_suelo_pct": 0.05, "so4_agua_ppm": None,
         "tabla_4_2": {"baja_permeabilidad": False,
                       "congelamiento_deshielo": False}})   # falta 'cloruros'
    try:
        with pytest.raises(DatoInvalidoError) as exc:
            recubrimiento_de_diseno(condicion="contra_suelo")
        assert "cloruros" in str(exc.value)
    finally:
        ca.quitar_valor_dinamico("exposicion_quimica_ems")


def test_las_tres_filas_de_la_tabla_4_2_entran_en_la_menor_a_c_aplicable(
        vaciar_criterio):
    """
    La nota al pie manda la MENOR relacion a/c APLICABLE, y aplicable no se
    puede evaluar sobre un conjunto al que le falta un candidato. Con la fila
    de baja permeabilidad activa y sin cloruros, la a/c que gobierna es la
    0.50 de esa fila -- no la ausencia de limite que salia cuando la unica
    fila mirada era la de cloruros.
    """
    vaciar_criterio("exposicion_quimica_ems")
    ca.establecer_valor_dinamico(
        "exposicion_quimica_ems",
        {"so4_suelo_pct": 0.0, "so4_agua_ppm": None,
         "tabla_4_2": {"baja_permeabilidad": True,
                       "congelamiento_deshielo": False,
                       "cloruros": False}})
    try:
        requisitos = requisitos_durabilidad_concreto()
        assert requisitos.a_c_max == pytest.approx(0.50)
        assert "Tabla 4.2" in requisitos.gobierna_a_c
    finally:
        ca.quitar_valor_dinamico("exposicion_quimica_ems")


def test_el_cruce_con_la_tabla_del_manual_cubre_las_filas_de_pilotes():
    """
    LA RED DE SEGURIDAD, COMPLETA. El cruce entre las dos transcripciones de
    la misma tabla se hacia con `situacion in RECUBRIMIENTO_MP_MM`, y en las
    filas de la familia de pilotes las claves no coinciden -- el Manual
    traduce "shafts" por "Pilares" y ademas parte en dos la fila de ambiente
    corrosivo --, de modo que el cruce se saltaba SIN AVISAR: cubria 14 filas
    de 21 mientras el comentario afirmaba que las cubria todas.

    Este test es el que impide que vuelva a pasar en silencio: toda fila de la
    tabla de AASHTO tiene equivalencia declarada, toda equivalencia apunta a
    filas que existen en la del Manual, y en la columna A -- la unica que el
    Manual tabula -- las dos fuentes coinciden.
    """
    tabla = ca.valor("tabla_recubrimiento_aashto_mm")
    assert set(tabla) == set(RECUBRIMIENTO_MP_EQUIVALENCIA), (
        "hay filas de la tabla de AASHTO sin equivalencia declarada con la "
        "del Manual de Puentes, o al reves")
    for situacion, filas_mp in RECUBRIMIENTO_MP_EQUIVALENCIA.items():
        assert filas_mp, f"'{situacion}' declara una equivalencia vacia"
        for fila in filas_mp:
            assert fila in RECUBRIMIENTO_MP_MM, (
                f"'{situacion}' apunta a '{fila}', que no esta en la tabla "
                f"del Manual")
        assert max(RECUBRIMIENTO_MP_MM[f] for f in filas_mp) == pytest.approx(
            tabla[situacion]["A"]), (
            f"'{situacion}': la columna A de AASHTO y la unica columna del "
            f"Manual dejaron de coincidir")


def test_el_aumento_por_ambiente_corrosivo_se_declara_y_no_se_calcula():
    aviso = aviso_ambiente_corrosivo()
    assert "7.7.5.1" in aviso and "no las calcula este modulo" in aviso
    # NOR-E060-04: la alternativa que el articulo ofrece, y que el aviso omitia
    assert "otro tipo de protección" in aviso


@pytest.mark.parametrize("direccion, minima", [
    ("horizontal", 0.0020), ("vertical", 0.0015),
])
def test_cuantias_minimas_de_referencia_art_14_3_1(direccion, minima):
    assert cuantia_minima(direccion=direccion) == pytest.approx(minima)
    assert CUANTIA_MIN_MURO[direccion] == minima


def test_verificar_cuantia_horizontal_y_vertical():
    ok = verificar_cuantia(cuantia_provista=0.0025, direccion="horizontal")
    no = verificar_cuantia(cuantia_provista=0.0010, direccion="vertical")
    assert ok.cumple and ok.codigo == "R1"
    assert not no.cumple and no.codigo == "R2"
    assert "14.3.1" in ok.numeral


# ---------------------------------------------------------------------------
# El minimo del Art. 14.3.1 es un PISO que se aplica, no una nota que se
# imprime. Antes de `cuantia_de_diseno` el modulo tenia el minimo transcrito y
# nada que lo levantara.
# ---------------------------------------------------------------------------

def test_la_cuantia_de_diseno_levanta_el_calculo_hasta_el_minimo():
    r = cuantia_de_diseno(cuantia_calculada=0.0012, direccion="horizontal",
                          cortante_alto=False)
    assert r.cuantia_adoptada == pytest.approx(CUANTIA_MIN_MURO["horizontal"])
    assert r.gobierna == "minimo_normativo"
    # los dos operandos viajan en el resultado, no solo el ganador
    assert r.cuantia_calculada == pytest.approx(0.0012)
    assert "14.3.1" in r.numeral


def test_la_cuantia_de_diseno_respeta_el_calculo_cuando_supera_el_minimo():
    r = cuantia_de_diseno(cuantia_calculada=0.0031, direccion="vertical",
                          cortante_alto=False)
    assert r.cuantia_adoptada == pytest.approx(0.0031)
    assert r.gobierna == "calculo"


def test_el_escalon_por_cortante_alto_detiene_el_calculo_y_no_se_rellena():
    """
    E.060 Art. 11.10.10.2 sube la cuantia horizontal minima bajo cortante
    alto, y M9 no calcula cortante. Declarar la condicion tiene que DETENER
    el calculo, no caer al 0.0020 del Art. 14.3.1, que es el menor de los dos
    minimos que tiene E.060.
    """
    with pytest.raises(CriterioPendienteError):
        cuantia_de_diseno(cuantia_calculada=0.0031, direccion="horizontal",
                          cortante_alto=True)
    assert ca.criterio(CRITERIO_CORTANTE_ALTO).valor is None


def test_cortante_alto_no_tiene_valor_por_defecto():
    """
    Si `cortante_alto` admitiera default, la respuesta comoda (False) daria
    siempre el minimo mas bajo sin que nadie la declare. El argumento es
    obligatorio a proposito.
    """
    with pytest.raises(TypeError):
        cuantia_de_diseno(cuantia_calculada=0.0031, direccion="horizontal")


def test_la_direccion_invalida_se_rechaza_antes_de_mirar_el_cortante():
    with pytest.raises(DatoInvalidoError):
        cuantia_de_diseno(cuantia_calculada=0.003, direccion="diagonal",
                          cortante_alto=False)


def test_el_numeral_9_1_separa_la_seccion_propia_del_numeral_del_eg2013():
    """
    'Sec. 9.1' es navegacion de la hoja de ruta y no existe en el EG-2013.
    Las dos mitades tienen que poder pedirse por separado.
    """
    assert NUMERAL_9_1.seccion_hoja_ruta == "Sec. 9.1"
    assert "503.01" in NUMERAL_9_1.numeral_norma
    assert "Sec. 9.1" not in NUMERAL_9_1.numeral_norma
    assert "Seccion 500" not in str(NUMERAL_9_1)


def test_acero_por_temperatura_en_ambas_caras_desde_250_mm():
    assert not requiere_temperatura_dos_caras(espesor=0.20)
    assert requiere_temperatura_dos_caras(espesor=0.25)     # el borde exacto
    assert requiere_temperatura_dos_caras(espesor=0.40)


def test_la_nota_de_temperatura_dice_una_o_ambas_caras_con_su_numeral():
    assert "AMBAS caras" in nota_temperatura_dos_caras(espesor=0.30)
    assert "UNA cara" in nota_temperatura_dos_caras(espesor=0.20)
    assert "14.8.3" in nota_temperatura_dos_caras(espesor=0.30)


def test_espaciamiento_maximo_es_el_menor_entre_3h_y_400_mm():
    # muro delgado: gobierna 3h
    assert espaciamiento_maximo(espesor=0.10) == pytest.approx(0.30)
    # muro grueso: gobierna el tope absoluto
    assert espaciamiento_maximo(espesor=0.40) == pytest.approx(
        ESPACIAMIENTO_MAX_ABSOLUTO)


def test_verificar_espaciamiento():
    v = verificar_espaciamiento(espaciamiento=0.25, espesor=0.30)
    assert v.cumple and v.codigo == "R3"
    assert not verificar_espaciamiento(espaciamiento=0.45, espesor=0.30).cumple


def test_alternativa_en_concreto_ciclopeo():
    # 12.0 MPa CUMPLIA antes y ya no: el minimo aplicable es el mayor de los
    # dos que rigen sobre el mismo material -- 10 MPa de E.060 Art. 22.10 y
    # 14 MPa de la Clase G de la Tabla 503-07 del EG-2013 (NOR-E060-07).
    ok = verificar_ciclopeo(fc_matriz=15.0, fraccion_piedra=0.25)
    assert all(v.cumple for v in ok)
    assert [v.codigo for v in ok] == ["R4", "R5"]

    flojo = verificar_ciclopeo(fc_matriz=8.0, fraccion_piedra=0.40)
    assert not any(v.cumple for v in flojo)
    assert flojo[0].valor_admisible == CICLOPEO_FC_MATRIZ_MIN_APLICABLE
    assert flojo[1].valor_admisible == CICLOPEO_FRACCION_PIEDRA_MAX


def test_el_diseno_por_flexion_y_corte_esta_citado_pero_no_ensamblado():
    """
    'procedimiento_flexion_corte_aashto_sec5' es [C] (phi, MCFT beta-theta,
    Vc, Vs, dv): ya no es CriterioPendienteError. Lo que sigue faltando es
    el ENSAMBLE (iterar epsilon_s), y por eso se detiene con
    NotImplementedError -- Sec. 0.2, Via 1: cuando se implemente, no se
    combinaran demandas mayoradas por AASHTO con resistencias reducidas por
    E.060.
    """
    assert "procedimiento_flexion_corte_aashto_sec5" not in ca.criterios_sin_valor()
    with pytest.raises(NotImplementedError):
        diseno_flexion_corte(momento=45.0, cortante=30.0)


# ===========================================================================
# 9.1 - Condicion normativa (declarativo)
# ===========================================================================

def test_la_declaracion_de_sec_9_1_recoge_sus_cuatro_avisos():
    texto = " ".join(condicion_normativa_cabezal())
    assert "503" in texto                       # concreto estructural
    assert "square edge" in texto               # embocadura a ras (Sec. 4.2)
    assert "subpresion" in texto or "Subpresion" in texto
    assert "borde del" in texto                 # zapata en talud
    assert "no gobierna el diseno estructural" in texto


# ===========================================================================
# Todos los vacios de la Fase 9, en un solo sitio
# ===========================================================================

def test_la_cadena_completa_corre_cuando_los_vacios_se_declaran(monkeypatch,
                                                               geometria):
    """
    Prueba de que lo que bloquea la Fase 9 son los DATOS y no el
    procedimiento: con los seis criterios rellenados a valores de tanteo, el
    camino Sec. 9.2 -> Sec. 9.3 corre entero y da numeros con sentido fisico.

    Los valores inyectados NO son una propuesta de proyecto -- son de prueba,
    y por eso viven en el test y no en criterios_adoptados.py.
    """
    valores = {
        "phi_relleno_trasdos": 34.0,
        "pendiente_relleno_trasdos_i": 0.0,
        "inclinacion_muro_beta": 0.0,
        "friccion_muro_suelo_delta": 0.0,
        "punto_aplicacion_incremento_sismico": 0.6,
        "peso_especifico_relleno_kn_m3": 19.0,
        "peso_especifico_concreto_kn_m3": 24.0,
    }
    for clave, valor in valores.items():
        original = ca.criterio(clave)
        monkeypatch.setitem(ca.CRITERIOS, clave,
                            ca.Criterio(valor=valor, etiqueta=original.etiqueta,
                                        concepto=original.concepto,
                                        justificacion=original.justificacion,
                                        fuente=original.fuente))
    # Y los dos datos de SITIO que la sobrecarga viva necesita (conflicto #4):
    # sin ellos la Sec. 9.2 se detiene antes de llegar a la Sec. 9.3.
    _declarar_orientacion(monkeypatch, ORIENTACION_PARALELO_AL_TRAFICO)
    _declarar_borde(monkeypatch, 1.0)

    H = geometria.altura_total
    estatico = empujes_trasdos(geometria=geometria,
                               condicion=CondicionAnalisis.ESTATICO,
                               altura_empuje=H,
                               NF_profundidad_m=NF_DE_PRUEBA)
    sismico = empujes_trasdos(geometria=geometria,
                              condicion=CondicionAnalisis.SISMICO,
                              altura_empuje=H,
                              NF_profundidad_m=NF_DE_PRUEBA)

    # El estatico no lleva componente EQ; el sismico si, y la suma crece
    assert estatico.incremento_sismico is None
    assert sismico.incremento_sismico > 0
    assert sismico.empuje_horizontal_total > estatico.empuje_horizontal_total
    assert sismico.momento_volcante > estatico.momento_volcante

    # Con i = beta = delta = 0 los dos coeficientes estaticos coinciden
    assert sismico.mononobe_okabe.K_A == pytest.approx(sismico.K_A, abs=TOL)

    # Brazos: triangulo en H/3, rectangulo en H/2, incremento en 0.6H
    assert estatico.z_activo == pytest.approx(H / 3)
    assert estatico.z_sobrecarga == pytest.approx(H / 2)
    assert sismico.z_incremento == pytest.approx(0.6 * H)

    # Zapata a 1.00 m con NF a 1.40 m: no hay agua sobre la base
    assert estatico.E_hidrostatico == pytest.approx(0.0)
    assert estatico.U_subpresion == pytest.approx(0.0)

    # Y el peso propio ya se puede calcular: pantalla trapecial + zapata
    W = peso_propio_cabezal(geometria=geometria)
    assert W == pytest.approx(24.0 * ((0.25 + 0.35) / 2 * 2.00 + 1.60 * 0.40))

    # Cierre: el mismo cabezal, dos condiciones, dos veredictos posibles
    estabilidad = verificar_estabilidad(
        geometria=geometria, condicion=CondicionAnalisis.SISMICO,
        q_actuante=100.0, q_ultima=300.0,
        momento_estabilizante=W * geometria.B / 2,
        momento_volcante=sismico.momento_volcante,
        fuerza_resistente=W / 2, fuerza_actuante=sismico.empuje_horizontal_total)
    assert len(estabilidad.verificaciones) == 3


@pytest.mark.parametrize("clave", [
    "pendiente_relleno_trasdos_i", "inclinacion_muro_beta",
    "friccion_muro_suelo_delta", "punto_aplicacion_incremento_sismico",
    "predimensionamiento_cabezal", "N_cq_N_gammaq_meyerhof",
    "metodo_estabilidad_global",
])
def test_cada_vacio_de_la_fase_9_esta_declarado_con_su_justificacion(clave):
    criterio = ca.criterio(clave)
    assert clave in ca.criterios_sin_valor()
    assert criterio.etiqueta == "A"
    assert criterio.fuente.startswith("PENDIENTE")
    assert len(criterio.justificacion) > 100      # no es un "falta el dato"


@pytest.mark.parametrize("clave", [
    "peso_especifico_concreto_kn_m3",
    "tabla_recubrimiento_aashto_mm",
    "procedimiento_flexion_corte_aashto_sec5",
])
def test_los_datos_de_C_2_estan_cerrados_como_C(clave):
    """
    Los criterios de la Fase 9 que dependian de una tabla AASHTO sin eleccion
    de ingenieria: transcripcion directa, etiqueta [C], fuente citada con
    edicion y pagina.

    'factores_carga_aashto' SALIO de esta lista (C03: NOR-PUE-04). Era el
    cuarto, y su [C] descansaba sobre una afirmacion falsa: que el corpus
    peruano no traia las tablas de factores de carga. El Manual de Puentes las
    trae completas en su pag. impresa 143, de modo que los numeros son [N] y
    viven en constantes_normativas; lo que queda en el criterio es la ELECCION
    de fila por estructura, que es [A]. Su contrato lo verifica el test
    siguiente.
    """
    criterio = ca.criterio(clave)
    assert clave not in ca.criterios_sin_valor()
    assert criterio.valor is not None
    assert criterio.etiqueta == "C"
    assert not criterio.fuente.startswith("PENDIENTE")
    assert "AASHTO LRFD" in criterio.fuente


def test_los_factores_de_carga_son_tabla_N_mas_eleccion_A():
    """
    La tabla es [N] y la eleccion de fila es [A] (Sec. 0.7). El criterio no
    puede volver a guardar numeros: si lo hiciera, volveria a poder escribir
    un par -- como el {max 1.35, min 0.90} de MAT-D8 -- que no es ninguna fila
    de la Tabla 2.4.5.3.1-2.
    """
    criterio = ca.criterio("factores_carga_aashto")
    assert criterio.etiqueta == "A"
    assert "factores_carga_aashto" not in ca.criterios_sin_valor()
    for elemento, filas in criterio.valor.items():
        for carga, fila in filas.items():
            assert isinstance(fila, str), (
                f"'{elemento}'/'{carga}' guarda {fila!r}: la eleccion nombra "
                "una fila, no un factor")
            assert fila in TABLA_GAMMA_P_FILAS, (
                f"'{elemento}'/'{carga}' nombra la fila '{fila}', que no "
                "esta en la Tabla 2.4.5.3.1-2")


# ===========================================================================
# 9.2 - Mononobe-Okabe: LOS SIGNOS (SIS-F-04)
# ===========================================================================
# El caso limite de Rankine no prueba los signos: con i = beta = delta = 0 y
# k_h = k_v = 0 los cuatro cosenos tienen argumento nulo y cos es par, de modo
# que doce de los quince mutantes de signo de la formula lo dejan intacto
# hasta el ultimo bit. Los tests de abajo contrastan contra CP-9, que tiene
# los seis parametros distintos entre si y distintos de cero.

@pytest.mark.parametrize("caso", CP9_MONONOBE_OKABE, ids=lambda c: c["nombre"])
def test_k_ae_contra_caso_patron_con_los_cuatro_angulos_no_nulos(caso):
    """
    EL test de valor de K_AE (Sec. 9.2), el que el caso limite de Rankine no
    podia ser (SIS-F-04). Dorados en CP-9, recomputados alli con la formula
    escrita otra vez y sin importar este modulo.
    """
    K_AE = k_ae_mononobe_okabe(
        phi_grados=caso["phi_grados"], i_grados=caso["i_grados"],
        beta_grados=caso["beta_grados"], delta_grados=caso["delta_grados"],
        k_h=caso["k_h"], k_v=caso["k_v"])
    assert K_AE == pytest.approx(caso["K_AE_esperado"],
                                 rel=CP9_TOLERANCIA_RELATIVA)


@pytest.mark.parametrize("caso", CP9_MONONOBE_OKABE, ids=lambda c: c["nombre"])
def test_k_a_coulomb_contra_caso_patron_con_angulos_no_nulos(caso):
    """
    El K_A estatico con i, beta y delta NO nulos: es Coulomb, no Rankine, y
    hasta hoy no tenia ningun contraste de valor fuera del caso de los tres
    angulos en cero. Fija las convenciones de angulo sin la cadena sismica de
    por medio (psi = 0), de modo que un signo que falle aqui es del bloque
    estatico y no del sismico.
    """
    K_A = k_a_coulomb(phi_grados=caso["phi_grados"], i_grados=caso["i_grados"],
                      beta_grados=caso["beta_grados"],
                      delta_grados=caso["delta_grados"])
    assert K_A == pytest.approx(caso["K_A_esperado"],
                                rel=CP9_TOLERANCIA_RELATIVA)


@pytest.mark.parametrize("caso", CP9_MONONOBE_OKABE, ids=lambda c: c["nombre"])
def test_psi_contra_caso_patron_con_k_v_no_nulo(caso):
    """
    psi = arctan[k_h / (1 - k_v)] en grados. Con k_v = 0 el signo del
    denominador es invisible: los tres casos de CP-9 lo tienen no nulo.
    """
    assert angulo_inercia_sismica(k_h=caso["k_h"], k_v=caso["k_v"]) == (
        pytest.approx(caso["psi_esperado"], rel=CP9_TOLERANCIA_RELATIVA))


@pytest.mark.parametrize("caso", CP9_MONONOBE_OKABE, ids=lambda c: c["nombre"])
def test_empuje_mononobe_okabe_empaqueta_los_dorados_de_cp9(caso):
    """
    El objeto que viaja a la memoria lleva los tres numeros contrastados y no
    solo K_AE: si `empuje_mononobe_okabe` cableara mal cualquiera de los tres,
    la memoria publicaria un coeficiente que nadie recalculo.
    """
    mo = empuje_mononobe_okabe(
        phi_grados=caso["phi_grados"], i_grados=caso["i_grados"],
        beta_grados=caso["beta_grados"], delta_grados=caso["delta_grados"],
        k_h=caso["k_h"], k_v=caso["k_v"])
    assert mo.K_AE == pytest.approx(caso["K_AE_esperado"], rel=CP9_TOLERANCIA_RELATIVA)
    assert mo.K_A == pytest.approx(caso["K_A_esperado"], rel=CP9_TOLERANCIA_RELATIVA)
    assert mo.psi_grados == pytest.approx(caso["psi_esperado"], rel=CP9_TOLERANCIA_RELATIVA)
    assert mo.incremento == pytest.approx(
        caso["K_AE_esperado"] - caso["K_A_esperado"], rel=CP9_TOLERANCIA_RELATIVA)


@pytest.mark.parametrize("caso", CP9_MONONOBE_OKABE, ids=lambda c: c["nombre"])
def test_el_corchete_es_1_mas_R_de_aashto_y_no_1_menos_R_del_manual(caso):
    """
    El denominador lleva [1 + R] (AASHTO, Art. A11.3.1, ec. A11.3.1-1) y NO
    el [1 - R] que el Manual de Puentes imprime por errata (Apendice A11,
    num. A.11.3.1, pag. impresa 586). La declaracion completa esta en
    `constantes_normativas.K_AE_ERRATA_MANUAL` y en el docstring de
    `k_ae_mononobe_okabe`.

    Este test existe para que "corregir" el mas a menos falle en rojo: el
    dorado de la errata esta en CP-9 y el modulo no puede producirlo. Con
    estos angulos el [1 - R] da entre 8 y 126 veces el valor correcto.
    """
    K_AE = k_ae_mononobe_okabe(
        phi_grados=caso["phi_grados"], i_grados=caso["i_grados"],
        beta_grados=caso["beta_grados"], delta_grados=caso["delta_grados"],
        k_h=caso["k_h"], k_v=caso["k_v"])
    assert K_AE == pytest.approx(caso["K_AE_esperado"], rel=CP9_TOLERANCIA_RELATIVA)
    assert K_AE != pytest.approx(caso["K_AE_errata_1_menos_R_esperado"], rel=1e-3)


def test_la_errata_1_menos_R_daria_el_reciproco_de_rankine():
    """
    Por que el [1 - R] del Manual es errata de imprenta y no una variante
    peruana: en el caso limite (i = beta = delta = 0, k_h = k_v = 0) la
    formula con [1 - R] no da un valor "parecido" al Ka de Rankine, da su
    RECIPROCO exacto -- (1+sen phi)/(1-sen phi) en vez de
    (1-sen phi)/(1+sen phi) --, es decir un empuje activo mayor que 1. El
    modulo tiene que dar Ka, no 1/Ka.
    """
    for phi, ka_dorado, errata in zip(
            CP9_RANKINE_LIMITE["phi_casos"],
            CP9_RANKINE_LIMITE["Ka_rankine_esperado"],
            CP9_RANKINE_LIMITE["K_AE_errata_1_menos_R_esperado"]):
        K_AE = k_ae_mononobe_okabe(phi_grados=phi, i_grados=0.0,
                                   beta_grados=0.0, delta_grados=0.0,
                                   k_h=0.0, k_v=0.0)
        # el Ka de Rankine tambien contra dorado, y no solo como patron movil:
        # hasta hoy `ka_rankine` no tenia ningun test de valor propio
        assert ka_rankine(phi_grados=phi) == pytest.approx(
            ka_dorado, rel=CP9_TOLERANCIA_RELATIVA)
        assert K_AE == pytest.approx(ka_dorado, rel=CP9_TOLERANCIA_RELATIVA)
        assert K_AE != pytest.approx(errata, rel=1e-3)
        assert errata * ka_dorado == pytest.approx(1.0, rel=1e-12)


def test_convenciones_de_i_beta_y_k_v_van_en_la_direccion_declarada():
    """
    Red secundaria y documentacion ejecutable de las convenciones que el
    docstring declara: i sobre la HORIZONTAL, beta sobre la VERTICAL positiva
    cuando el muro se aleja del relleno, k_v en el denominador de psi. Los
    tres aumentan K_AE. No se afirma nada sobre delta: K_AE NO es monotono en
    delta (con beta = 20 tiene un minimo cerca de delta = 5 grados y crece
    despues), y por eso `test_delta_mayor_reduce_k_ae` solo vale en su propia
    configuracion.

    LOS SEIS PARAMETROS SE LEEN DE CP9_MONONOBE_OKABE y no se escriben aqui.
    Estaban duplicados como literales --- los mismos seis numeros de CP9-A,
    digito a digito --- y eso es el defecto SIS-F-14: corregir el fixture no
    llegaba a este test. La resolucion de la fila 7 de la hoja `Conflictos`
    es vinculante y dice exactamente "hacer que los tests de M9 lean del
    fixture en vez de literales".
    """
    base = {clave: CP9_MONONOBE_OKABE[0][clave]
            for clave in ("phi_grados", "i_grados", "beta_grados",
                          "delta_grados", "k_h", "k_v")}
    referencia = k_ae_mononobe_okabe(**base)
    # Las perturbaciones SI son del test --- no son dorados, son "un poco mas
    # que el caso" --- y se derivan del propio caso para que no queden
    # colgando de un numero fijo si el fixture cambia de configuracion.
    mas = lambda clave, delta: {**base, clave: base[clave] + delta}   # noqa: E731
    assert k_ae_mononobe_okabe(**mas("i_grados", 7.0)) > referencia
    assert k_ae_mononobe_okabe(**mas("beta_grados", 8.0)) > referencia
    assert k_ae_mononobe_okabe(**mas("k_v", 0.15)) > referencia
    assert k_ae_mononobe_okabe(**mas("k_h", 0.10)) > referencia


# ---------------------------------------------------------------------------
# E6 y la presion de contacto: la fila que no tenia NI UNA llamada en la suite
# ---------------------------------------------------------------------------
# Hallazgo abierto en S16 al cerrar SIS-F-06, sin ID de auditoria propio: un
# sondeo de llamadas sobre la suite entera daba CERO para
# `presion_contacto_base`, `excentricidad_resultante`,
# `excentricidad_admisible_sismica`, `verificar_excentricidad_sismica` y
# `gamma_eq`. La fila E6 completa y el productor del `q_actuante` que consume
# E1 no se ejercitaban nunca.
#
# Que esten en `M9.FUNCIONES_SIN_CONSUMIDOR` no los exime: esa declaracion
# dice que la CLI no los ensambla todavia -- heredan el vacio de
# 'predimensionamiento_cabezal' y de 'gamma_EQ' --, no que no haya que
# probarlos. En ese mismo diccionario estan `verificar_estabilidad`,
# `empujes_trasdos` y `peso_propio_cabezal`, que si tienen tests.

def test_la_presion_de_contacto_en_suelo_es_uniforme_sobre_el_ancho_efectivo():
    """
    Suelo, resultante dentro del nucleo: Meyerhof reparte la normal sobre el
    ancho EFECTIVO B - 2e, no sobre B, y la presion es uniforme.
    """
    p = presion_contacto_base(N=200.0, momento_neto=40.0, B=1.60,
                              cimentacion_en_roca=False)
    assert p.e == pytest.approx(0.20, abs=TOL)
    assert p.ancho_efectivo == pytest.approx(1.20, abs=TOL)
    assert p.q_max == pytest.approx(166.66666666666666, abs=1e-9)
    assert p.q_min == pytest.approx(p.q_max, abs=TOL)
    assert "uniforme" in p.distribucion


def test_en_roca_las_dos_ramas_empalman_en_el_borde_del_nucleo():
    """
    El docstring lo afirma y nadie lo comprobaba: en e = B/6 la expresion
    trapecial y la triangular dan el mismo q_max = 2N/B, con q_min = 0.
    Es el unico punto donde las dos ramas tienen que coincidir, y por eso es
    el que fija que ninguna de las dos esta escrita al reves.
    """
    B, N = 1.60, 200.0
    p = presion_contacto_base(N=N, momento_neto=(B / 6) * N, B=B,
                              cimentacion_en_roca=True)
    assert p.q_max == pytest.approx(2 * N / B, abs=1e-9)
    assert p.q_min == pytest.approx(0.0, abs=1e-9)


def test_en_roca_fuera_del_nucleo_la_distribucion_es_triangular():
    p = presion_contacto_base(N=200.0, momento_neto=60.0, B=1.60,
                              cimentacion_en_roca=True)
    assert not p.dentro_del_nucleo
    assert p.q_max == pytest.approx(266.6666666666667, abs=1e-9)
    assert p.q_min == pytest.approx(0.0, abs=TOL)


def test_la_resultante_fuera_de_la_zapata_no_es_factible():
    """e > B/2: la resultante cae fuera de la base y no hay contacto que repartir."""
    with pytest.raises(DisenoNoFactibleError):
        presion_contacto_base(N=200.0, momento_neto=160.0, B=1.60,
                              cimentacion_en_roca=False)


def test_una_normal_no_comprimida_es_dato_invalido():
    with pytest.raises(DatoInvalidoError):
        excentricidad_resultante(N=-1.0, momento_neto=10.0, B=1.60)


def test_E6_interpola_el_limite_de_excentricidad_entre_B_tercios_y_04B():
    """
    El limite sismico de la excentricidad NO es "el tercio central" a secas
    -- esa es la tercera errata del Manual en esta cadena --: depende de
    gamma_EQ, y es la unica de las tres que MUEVE un numero.
    """
    B = 1.60
    assert excentricidad_admisible_sismica(B=B, gamma_EQ=0.0) == pytest.approx(
        B / 3, abs=TOL)
    assert excentricidad_admisible_sismica(B=B, gamma_EQ=1.0) == pytest.approx(
        0.4 * B, abs=TOL)
    assert excentricidad_admisible_sismica(B=B, gamma_EQ=0.5) == pytest.approx(
        0.5866666666666668, abs=TOL)


def test_E6_cumple_dentro_del_limite_y_no_fuera():
    v = verificar_excentricidad_sismica(N=200.0, momento_neto=40.0, B=1.60,
                                        gamma_EQ=0.0)
    assert v.cumple and v.codigo == "E6" and v.criterio_aplicado == "gamma_EQ"
    assert v.valor_obtenido == pytest.approx(0.20, abs=TOL)
    assert v.valor_admisible == pytest.approx(1.60 / 3, abs=TOL)

    fuera = verificar_excentricidad_sismica(N=200.0, momento_neto=120.0,
                                            B=1.60, gamma_EQ=0.0)
    assert not fuera.cumple
    assert fuera.valor_obtenido == pytest.approx(0.60, abs=TOL)


def test_un_gamma_EQ_fuera_de_la_tabla_es_dato_invalido():
    with pytest.raises(DatoInvalidoError):
        verificar_excentricidad_sismica(N=200.0, momento_neto=10.0, B=1.60,
                                        gamma_EQ=1.5)


# ===========================================================================
# SIS-F-10 (cluster C09) - LAS GUARDAS DE `ErrorProyecto` DE M9, EJERCITADAS
# ===========================================================================
# El hallazgo dice "trece raise de ErrorProyecto sin ninguna cobertura, dos de
# ellos alcanzables con una llamada normal". Medida de nuevo sobre el arbol de
# esta sesion la cuenta es mayor, y M9 es el modulo que mas aporta: treinta y
# tres `raise` que ninguna prueba ejecutaba.
#
# QUE PRUEBA CADA UNO DE ESTOS TESTS, y por que no basta con `pytest.raises`
# a secas: una guarda sin cobertura puede estar rota de tres formas que la
# suite verde no distingue -- no dispararse nunca (y dejar pasar el dato
# malo), disparar la excepcion EQUIVOCADA (y la GUI la muestra como fallo del
# programa en vez de como problema del expediente), o disparar la correcta con
# un motivo que no dice QUE hay que corregir. Por eso cada caso afirma las
# tres cosas: la CLASE, el `campo` cuando la excepcion lo lleva, y un trozo
# del motivo que explica POR QUE se detuvo.
#
# Los valores con que se provocan las detenciones son DE PRUEBA, no de
# proyecto: entran por `_declarar_criterio` (monkeypatch sobre `CRITERIOS`) o
# por `establecer_valor_dinamico` con su retirada en `finally`, nunca
# escribiendo nada en criterios_adoptados.py.

# Los dos criterios que el conftest declara EN CALIENTE para toda la corrida:
# sobre estos, parchear `CRITERIOS` no cambia nada, porque `ca.valor` mira
# primero `_OVERRIDES`. Se declaran y se retiran por el mismo camino que usan
# la GUI y la CLI.
_CRITERIOS_DECLARADOS_EN_LA_CORRIDA = (M9.CRITERIO_CATEGORIA_REFUERZO,
                                       M9.CRITERIO_EXPOSICION_QUIMICA)


@contextmanager
def _con_criterios(monkeypatch, declaraciones):
    """
    Declara varios criterios a la vez con valores DE PRUEBA y los devuelve a
    su estado anterior al salir, tome cada uno el camino que tome.
    """
    previos = {}
    for clave, valor in declaraciones.items():
        if clave in _CRITERIOS_DECLARADOS_EN_LA_CORRIDA:
            previos[clave] = ca.valores_dinamicos().get(clave)
            ca.establecer_valor_dinamico(clave, valor)
        else:
            _declarar_criterio(monkeypatch, clave, valor)
    try:
        yield
    finally:
        for clave, previo in previos.items():
            if previo is None:
                ca.quitar_valor_dinamico(clave)
            else:
                ca.establecer_valor_dinamico(clave, previo)


# ---------------------------------------------------------------------------
# 9.2 - La declaracion de filas de F_pga y la lectura de sus rotulos extremos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("declarado, motivo_esperado", [
    ("C", "tupla de filas"),                 # una cadena NO es una tupla de filas
    (1.0, "tupla de filas"),                 # el defecto viejo: el factor ya resuelto
    ((), "no declara ninguna fila"),
    (("Z",), "no es una fila de"),
    (("C", "Z"), "no es una fila de"),        # basta que UNA no exista
    (("F",), "no trae factor"),
    (("C", "F"), "no trae factor"),           # basta que UNA sea la fila del asterisco
], ids=["cadena", "factor_resuelto", "vacia", "fila_inexistente",
        "una_fila_inexistente", "fila_F", "una_fila_F"])
def test_la_declaracion_de_filas_de_F_pga_se_rechaza_entera(
        monkeypatch, declarado, motivo_esperado):
    """
    QUE DEFECTO LO HARIA FALLAR: que `clases_de_sitio_plausibles` aceptara una
    declaracion que no es "la tupla de filas de la tabla". Las cuatro formas
    de declararla mal no son intercambiables -- un factor ya resuelto (el
    defecto NOR-MEM-03 que el reparto R1 vino a cerrar), una tupla vacia, una
    fila que la tabla no tiene, y la fila F, que la fuente marca con asterisco
    y cuya Nota 2 exige estudio de respuesta dinamica de sitio en vez de dar
    un numero --, y cada una tiene que decir cual es.

    Si una sola de ellas dejara de detenerse, la cadena sismica entera saldria
    de un F_pga que nadie leyo de la tabla.
    """
    with _con_criterios(monkeypatch, {M9.CRITERIO_F_PGA: declarado}):
        with pytest.raises(DatoInvalidoError) as exc:
            clases_de_sitio_plausibles()
    assert exc.value.campo == M9.CRITERIO_F_PGA
    assert motivo_esperado in exc.value.motivo
    # y la fila del asterisco se rechaza por lo que ES, no por su nombre
    if motivo_esperado == "no trae factor":
        assert F_PGA_EXIGE_ESTUDIO_DE_SITIO in F_PGA_TABLA[exc.value.valor]


@pytest.mark.parametrize("clase, lectura, campo, motivo_esperado", [
    ("Z", LECTURA_COLUMNA_EXTREMA_INCLUSIVE, "clase", "no es una fila de"),
    ("C", "a_ojo", "lectura_extremos", "tiene que ser una de"),
    ("F", LECTURA_COLUMNA_EXTREMA_INCLUSIVE, "clase", "no tiene factor tabulado"),
], ids=["fila_inexistente", "lectura_inventada", "fila_F"])
def test_factor_sitio_desde_tabla_rechaza_la_fila_y_la_lectura_inexistentes(
        clase, lectura, campo, motivo_esperado):
    """
    QUE DEFECTO LO HARIA FALLAR: que la lectura de UNA fila de la tabla
    aceptara una fila que no existe, una lectura de rotulos que no es ninguna
    de las dos declarables, o la fila F -- que no tiene numero que leer --.
    La tercera sale con la MISMA excepcion que en `clases_de_sitio_plausibles`
    y es deliberado: el hecho es el mismo y dos excepciones distintas para un
    mismo hecho obligarian a quien atrapa a saber por cual de las dos puertas
    entro.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        factor_sitio_desde_tabla(clase=clase, PGA=F_PGA_TABLA_PGA_COLUMNAS[-1],
                                 lectura_extremos=lectura)
    assert exc.value.campo == campo
    assert motivo_esperado in exc.value.motivo


@pytest.mark.parametrize("extremo", [0, -1], ids=["rotulo_inferior",
                                                  "rotulo_superior"])
def test_la_lectura_estricta_detiene_en_los_dos_rotulos_extremos(extremo):
    """
    QUE DEFECTO LO HARIA FALLAR: que con la lectura 'limite_estricto' el
    modulo eligiera una columna igual. Los dos rotulos extremos de la tabla
    son desigualdades ESTRICTAS ("PGA < 0.10" y "PGA > 0.50") y el PGA de este
    proyecto cae justo sobre el superior (NOR-PUE-11): con esa lectura no hay
    columna que leer ni dos valores entre los que interpolar, y el calculo se
    detiene en vez de elegir por el proyectista.

    El contraste con la otra lectura va en el mismo test a proposito: es lo
    que demuestra que la declaracion NO es neutra.
    """
    PGA = F_PGA_TABLA_PGA_COLUMNAS[extremo]
    with pytest.raises(DisenoNoFactibleError) as exc:
        factor_sitio_desde_tabla(clase="D", PGA=PGA,
                                 lectura_extremos=LECTURA_COLUMNA_EXTREMA_ESTRICTA)
    assert "rotulo extremo" in exc.value.motivo
    assert "desigualdades" in exc.value.motivo
    # con la lectura que este proyecto declara, el mismo PGA SI lee columna
    assert factor_sitio_desde_tabla(
        clase="D", PGA=PGA,
        lectura_extremos=LECTURA_COLUMNA_EXTREMA_INCLUSIVE) == pytest.approx(
            F_PGA_TABLA["D"][extremo], rel=REL_TRANSPORTE)


def test_la_lectura_de_los_rotulos_extremos_no_admite_un_tercer_nombre(
        monkeypatch):
    """
    QUE DEFECTO LO HARIA FALLAR: que `lectura_columna_extrema` devolviera lo
    que el criterio diga, sin comprobar que es una de las dos lecturas
    declarables. Un nombre inventado llegaria a `factor_sitio_desde_tabla`, no
    coincidiria con 'limite_estricto' y se comportaria en silencio como
    'limite_inclusive': la declaracion dejaria de significar nada.
    """
    with _con_criterios(monkeypatch, {M9.CRITERIO_F_PGA_LECTURA: "a_ojo"}):
        with pytest.raises(DatoInvalidoError) as exc:
            lectura_columna_extrema()
    assert exc.value.campo == M9.CRITERIO_F_PGA_LECTURA
    assert "tiene que ser una de" in exc.value.motivo
    assert all(x in exc.value.motivo for x in LECTURAS_COLUMNA_EXTREMA)


@pytest.mark.parametrize("filas", [("B", "C"), ("A", "D", "E"), ("C", "A")],
                         ids=["roca_y_suelo", "roca_y_dos_suelos",
                              "suelo_y_roca"])
def test_una_declaracion_mixta_de_roca_y_suelo_no_elige_rama(monkeypatch, filas):
    """
    QUE DEFECTO LO HARIA FALLAR: que `cimentacion_en_roca` resolviera una
    declaracion mixta por mayoria o por el lado conservador. El
    num. 2.8.1.1.14.2.1 da a cada grupo una expresion distinta de k_h0
    (`K_H0_FACTOR_ROCA_A_B` multiplica en una y no en la otra), de modo que
    elegir una seria decidir por el proyectista en el eslabon del que cuelga
    la cadena sismica entera.
    """
    with _con_criterios(monkeypatch, {M9.CRITERIO_F_PGA: filas}):
        with pytest.raises(DatoInvalidoError) as exc:
            cimentacion_en_roca()
    assert exc.value.campo == M9.CRITERIO_F_PGA
    assert "mezcla filas de roca" in exc.value.motivo
    assert "expresion" in exc.value.motivo


@pytest.mark.parametrize("filas, en_roca", [
    (F_PGA_CLASES_EN_ROCA, True),
    (("C", "D", "E"), False),
], ids=["todas_roca", "todas_suelo"])
def test_una_declaracion_homogenea_si_resuelve_la_rama(monkeypatch, filas,
                                                       en_roca):
    """
    El reverso del test anterior: la detencion no puede ser el unico camino.
    Con las filas todas de roca la clausula del numeral se activa, y con las
    filas todas de suelo se descarta de forma trazable -- que es lo que
    pedian MAT-O4 y NOR-PUE-12 --.
    """
    with _con_criterios(monkeypatch, {M9.CRITERIO_F_PGA: filas}):
        assert cimentacion_en_roca() is en_roca


@pytest.mark.parametrize("declarado", ["0.15", True, [0.15], (0.15,)],
                         ids=["texto", "booleano", "lista", "tupla"])
def test_k_v_solo_admite_la_cadena_prescrita_o_un_numero(monkeypatch,
                                                         declarado):
    """
    QUE DEFECTO LO HARIA FALLAR: que 'k_v' aceptara cualquier cosa. El
    criterio declara UNA de dos cosas -- el regimen prescrito, y entonces rige
    el cero [N] del num. 2.8.1.1.14.2.1, o el numero que el proyectista aporta
    para el caso que ese numeral reserva y no cuantifica --, y el booleano
    entra en la lista porque en Python `True` es un entero: sin la
    comprobacion explicita de `bool`, un 'k_v' declarado a `True` se
    convertiria en k_v = 1.0 y con el psi = 90 grados.
    """
    with _con_criterios(monkeypatch, {M9.CRITERIO_K_V: declarado}):
        with pytest.raises(DatoInvalidoError) as exc:
            coeficiente_sismico_vertical()
    assert exc.value.campo == M9.CRITERIO_K_V
    assert K_V_DECLARACION_PRESCRITO in exc.value.motivo
    assert "reserva" in exc.value.motivo


def test_k_v_declarado_como_numero_para_el_caso_reservado_si_se_devuelve(
        monkeypatch):
    """
    El reverso: el numeral reserva dos casos y no los cuantifica, asi que un
    k_v numerico declarado por el proyectista es una declaracion VALIDA y
    tiene que llegar al calculo. Si esta rama se rompiera, el unico k_v
    posible seria el cero y el caso reservado no seria representable.
    """
    k_v_de_prueba = 0.25
    with _con_criterios(monkeypatch, {M9.CRITERIO_K_V: k_v_de_prueba}):
        assert coeficiente_sismico_vertical() == pytest.approx(
            k_v_de_prueba, rel=REL_TRANSPORTE)


# ---------------------------------------------------------------------------
# 9.2 - El dominio de Mononobe-Okabe: los cosenos del denominador
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("angulos, coseno_roto", [
    (dict(phi_grados=34.0, i_grados=0.0, beta_grados=45.0, delta_grados=60.0,
          k_h=0.50, k_v=0.0), "delta+beta+psi"),
    (dict(phi_grados=34.0, i_grados=100.0, beta_grados=0.0, delta_grados=0.0,
          k_h=0.0, k_v=0.0), "i-beta"),
    (dict(phi_grados=34.0, i_grados=0.0, beta_grados=0.0, delta_grados=-70.0,
          k_h=0.50, k_v=1.50), "psi"),
], ids=["delta_mas_beta_mas_psi", "i_menos_beta", "psi"])
def test_un_coseno_no_positivo_del_denominador_detiene_mononobe_okabe(
        angulos, coseno_roto):
    """
    QUE DEFECTO LO HARIA FALLAR: que la formula siguiera adelante con un
    coseno nulo o negativo en el denominador. Los tres cosenos --
    cos(psi), cos(delta+beta+psi) y cos(i-beta) -- multiplican abajo, y uno
    negativo no da un K_AE grande: da un K_AE con el SIGNO cambiado, que
    aguas abajo se convierte en un empuje que empuja al reves. Tiene que
    salir como `DisenoNoFactibleError` con los tres angulos impresos, nunca
    como un numero.

    LOS TRES CASOS SON DISTINTOS a proposito, porque la guarda es un `or` de
    tres condiciones y cualquiera de las tres podria estar rota sola:
      * delta+beta+psi > 90 grados, con un trasdos muy inclinado y friccion
        muro-suelo alta;
      * i-beta > 90 grados, con un relleno mas empinado que el trasdos;
      * psi > 90 grados, que exige k_v > 1 -- una aceleracion vertical mayor
        que g --, fisicamente absurdo pero declarable por error.

    POR QUE psi = 90 EXACTO NO SIRVE PARA CUBRIR ESTA GUARDA, y no se usa:
    con k_v = 1 el psi que devuelve `angulo_inercia_sismica` es 90 grados
    exactos, pero `cos(radians(90))` vale 6.12e-17 y no cero, de modo que
    `cos_psi <= 0` es falso y la ejecucion cae en la guarda siguiente. Eso es
    MAT-O18 y se corrige en produccion, no aqui: este test cubre la rama por
    la puerta que hoy existe y no toca el modulo.

    EL CASO [psi] LLEVA delta = -70 Y NO delta = 0, y la razon es que la
    primera version de este test estaba VERDE POR OTRA RAZON QUE LA QUE dice.
    Con delta = 0 y k_v = 1.50, psi = 135 grados: cos_psi = -0.707, pero
    tambien cos(delta+beta+psi) = cos(135) = -0.707, de modo que el `or`
    cortaba por el SEGUNDO termino y el primero --- `cos_psi <= 0` --- era
    codigo muerto para la suite. Medido: borrarlo entero dejaba la suite en
    verde. Con delta = -70, cos_psi sigue en -0.707 y cos_dbp sube a +0.423:
    el termino queda aislado.

    Y el assert cambia con el: `coseno_roto in motivo` era trivialmente
    cierto para "psi", porque el mensaje imprime `psi = ...` en los tres
    casos. Se comprueba ahora el VALOR del coseno que rompio, que es lo que
    distingue una guarda de otra.
    """
    with pytest.raises(DisenoNoFactibleError) as exc:
        k_ae_mononobe_okabe(**angulos)
    assert "algun coseno del denominador" in exc.value.motivo
    assert coseno_roto in exc.value.motivo


def test_cada_termino_de_la_guarda_de_cosenos_esta_aislado():
    """
    El complemento del test de arriba: cada uno de los tres terminos del `or`
    tiene un caso donde es el UNICO no positivo. Sin esta comprobacion, un
    caso donde dos cosenos son negativos a la vez deja el otro termino como
    codigo muerto sin que nada lo diga --- que es exactamente lo que pasaba.
    """
    casos = {
        "psi": dict(phi_grados=34.0, i_grados=0.0, beta_grados=0.0,
                    delta_grados=-70.0, k_h=0.50, k_v=1.50),
        "delta+beta+psi": dict(phi_grados=34.0, i_grados=0.0, beta_grados=45.0,
                               delta_grados=60.0, k_h=0.50, k_v=0.0),
        "i-beta": dict(phi_grados=34.0, i_grados=100.0, beta_grados=0.0,
                       delta_grados=0.0, k_h=0.0, k_v=0.0),
    }
    for esperado, a in casos.items():
        psi = angulo_inercia_sismica(k_h=a["k_h"], k_v=a["k_v"])
        cos = {
            "psi": math.cos(math.radians(psi)),
            "delta+beta+psi": math.cos(
                math.radians(a["delta_grados"] + a["beta_grados"] + psi)),
            "i-beta": math.cos(
                math.radians(a["i_grados"] - a["beta_grados"])),
        }
        no_positivos = [nombre for nombre, v in cos.items() if v <= 0]
        assert no_positivos == [esperado], (
            f"el caso de '{esperado}' tiene {no_positivos} no positivos: si "
            "hay mas de uno, el `or` corta por el primero y los demas "
            f"terminos quedan sin cubrir. Cosenos: {cos}")


# ---------------------------------------------------------------------------
# 9.2 - Las dos lagunas de las tablas de h_eq de AASHTO 3.11.6.4
# ---------------------------------------------------------------------------

def test_una_distancia_al_borde_de_calzada_negativa_es_dato_invalido(
        monkeypatch):
    """
    QUE DEFECTO LO HARIA FALLAR: que una distancia negativa del trasdos al
    borde de calzada se leyera como la columna "0.0 ft". Un negativo no es un
    cero medido con ruido: es un dato del expediente que hay que CORREGIR, y
    por eso sale como `DatoInvalidoError` con el nombre de la columna, y no
    como una lectura de tabla.
    """
    _declarar_orientacion(monkeypatch, ORIENTACION_PARALELO_AL_TRAFICO)
    _declarar_borde(monkeypatch, -0.50)
    with pytest.raises(DatoInvalidoError) as exc:
        h_eq_sobrecarga_trasdos(altura_muro_total=2.00)
    assert exc.value.campo == "distancia_borde_calzada_al_trasdos_m"
    assert "no puede ser negativa" in exc.value.motivo


@pytest.mark.parametrize("regla", [M9.H_EQ_BANDA_INTERPOLA, "a_ojo"],
                         ids=["interpolar_sin_regla_escrita", "regla_inventada"])
def test_la_banda_del_borde_solo_se_lee_con_la_columna_cero_declarada(
        monkeypatch, regla):
    """
    QUE DEFECTO LO HARIA FALLAR: que la banda abierta 0 < d < 1.0 ft de la
    Tabla 3.11.6.4-2 se resolviera con cualquier declaracion. La tabla tiene
    DOS columnas y nada en medio, y la unica interpolacion que AASHTO autoriza
    es la de ALTURAS. De las dos lecturas que el criterio nombra, solo
    'columna_cero' esta implementada: 'interpolar_entre_columnas' exige ademas
    ESCRIBIR la regla de interpolacion, que la fuente no da, y mientras no se
    escriba el calculo se detiene en vez de inventarla.
    """
    _declarar_orientacion(monkeypatch, ORIENTACION_PARALELO_AL_TRAFICO)
    _declarar_borde(monkeypatch, 0.15)
    with _con_criterios(monkeypatch, {M9.CRITERIO_H_EQ_BANDA_BORDE: regla}):
        with pytest.raises(DatoInvalidoError) as exc:
            h_eq_sobrecarga_trasdos(altura_muro_total=2.00)
    assert exc.value.campo == M9.CRITERIO_H_EQ_BANDA_BORDE
    assert "la fuente no da" in exc.value.motivo


def test_la_regla_bajo_la_primera_fila_solo_admite_las_dos_declaradas(
        monkeypatch):
    """
    QUE DEFECTO LO HARIA FALLAR: que `_interpolar_h_eq` aceptara cualquier
    rotulo en 'h_eq_bajo_altura_tabulada' y, al no coincidir con ninguna de
    las dos lecturas implementadas, siguiera adelante devolviendo lo que
    tocara. Por debajo de la primera fila (5.0 ft) no hay fila con que
    interpolar: la laguna la cierra una declaracion, y una declaracion que no
    se entiende no es una declaracion.
    """
    _declarar_orientacion(monkeypatch, ORIENTACION_PERPENDICULAR_AL_TRAFICO)
    with _con_criterios(monkeypatch, {M9.CRITERIO_H_EQ_BAJO_TABLA: "a_ojo"}):
        with pytest.raises(DatoInvalidoError) as exc:
            h_eq_sobrecarga_trasdos(altura_muro_total=1.20)
    assert exc.value.campo == M9.CRITERIO_H_EQ_BAJO_TABLA
    assert M9.H_EQ_BAJO_TABLA_PRIMERA_FILA in exc.value.motivo
    assert M9.H_EQ_BAJO_TABLA_EXTRAPOLAR in exc.value.motivo


# ---------------------------------------------------------------------------
# 9.2 - El piso estatico de P_seis se identifica por NOMBRE
# ---------------------------------------------------------------------------

def test_el_piso_estatico_tiene_que_nombrar_una_combinacion_que_existe(
        monkeypatch):
    """
    QUE DEFECTO LO HARIA FALLAR: que `demanda_sismica_cabezal` confiara en que
    `P_SEIS_PISO_ESTATICO` coincide con el nombre de una de las combinaciones
    de `P_SEIS_COMBINACIONES`. Si las dos constantes se desincronizaran -- al
    reescribir un nombre de combinacion, por ejemplo --, el piso del empuje
    activo estatico que exige el num. 2.8.1.1.14.1 no se aplicaria A NINGUNA
    combinacion, EN SILENCIO y en la direccion no conservadora.

    La desincronizacion se simula parcheando la constante en el modulo, que es
    exactamente el accidente contra el que la guarda existe.
    """
    nombres = [nombre for nombre, _, _ in M9.P_SEIS_COMBINACIONES]
    assert M9.P_SEIS_PISO_ESTATICO in nombres      # el invariante que protege
    monkeypatch.setattr(M9, "P_SEIS_PISO_ESTATICO",
                        "un nombre que la tabla no tiene")
    inercia = fuerza_inercia_muro(k_h=0.50, W_w=100.0, W_s=50.0)
    with pytest.raises(DatoInvalidoError) as exc:
        demanda_sismica_cabezal(P_AE=100.0, P_A=40.0, inercia=inercia)
    assert exc.value.campo == "P_SEIS_PISO_ESTATICO"
    assert "no se estaria aplicando a ninguna" in exc.value.motivo


# ---------------------------------------------------------------------------
# 9.3 - La excentricidad exige una base con ancho
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("B", [0.0, -1.60], ids=["ancho_nulo",
                                                 "ancho_negativo"])
def test_un_ancho_de_zapata_no_positivo_es_dato_invalido(B):
    """
    QUE DEFECTO LO HARIA FALLAR: que `excentricidad_resultante` devolviera
    igual `|momento/N|` con un B nulo o negativo. La excentricidad se compara
    despues contra un limite que es una fraccion de B (`B/3`, `0.4*B`), de
    modo que con B <= 0 la verificacion E6 pasaria a compararse contra un
    limite nulo o negativo y "cumpliria" o "no cumpliria" por una razon que no
    tiene nada que ver con la estabilidad. El gemelo con N <= 0 ya tiene su
    test; este cubre el otro operando.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        excentricidad_resultante(N=200.0, momento_neto=40.0, B=B)
    assert exc.value.campo == "B"
    assert "positivo" in exc.value.motivo


# ---------------------------------------------------------------------------
# 9.2 - Los factores de carga: la eleccion de fila de gamma_p
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("eleccion", [
    {"tmc": {"EV": "EV_flexibles_entre_otros"}},      # falta el cabezal
    "EV_muros_y_estribos_de_retencion",               # no es un mapa
    {M9.ELEMENTO_CABEZAL: "EV_muros_y_estribos_de_retencion"},   # el cabezal no es un mapa
], ids=["sin_cabezal", "no_es_mapa", "cabezal_no_es_mapa"])
def test_la_eleccion_de_filas_de_gamma_p_tiene_que_describir_al_cabezal(
        monkeypatch, eleccion):
    """
    QUE DEFECTO LO HARIA FALLAR: que `factores_de_carga` bajara a la Tabla
    2.4.5.3.1-2 sin saber que fila describe al cabezal. La declaracion [A]
    dice de que FILA cuelga cada estructura, y sin la entrada del cabezal el
    modulo no tiene con que elegir: con `.get()` a secas eso habria dado None
    y un AttributeError mas abajo -- un fallo del programa en vez de un
    problema del expediente, que es justo la frontera que la taxonomia de
    excepciones existe para mantener.
    """
    with _con_criterios(monkeypatch, {M9.CRITERIO_FACTORES_CARGA: eleccion}):
        with pytest.raises(DatoInvalidoError) as exc:
            factores_de_carga("Resistencia I")
    assert exc.value.campo == M9.CRITERIO_FACTORES_CARGA
    assert M9.ELEMENTO_CABEZAL in exc.value.motivo


@pytest.mark.parametrize("filas_del_cabezal, carga, fila_esperada", [
    ({"EV": "EV_inventada", "EH": "EH_activa"}, "EV", "EV_inventada"),
    ({"EV": "EV_muros_y_estribos_de_retencion", "EH": "EH_inventada"},
     "EH", "EH_inventada"),
    ({"EH": "EH_activa"}, "EV", None),                 # la carga sin declarar
], ids=["EV_fuera_de_la_tabla", "EH_fuera_de_la_tabla", "EV_sin_declarar"])
def test_una_fila_de_gamma_p_que_no_esta_en_la_tabla_detiene_la_combinacion(
        monkeypatch, filas_del_cabezal, carga, fila_esperada):
    """
    QUE DEFECTO LO HARIA FALLAR: que `_gamma_permanente` indexara
    `TABLA_GAMMA_P_FILAS` con lo que la declaracion diga. Una fila inventada
    daria KeyError -- fallo del programa -- y una carga sin declarar daria
    `None`, que tampoco es una fila: los dos casos son el mismo problema del
    expediente (la declaracion no dice de que fila cuelga esa carga del
    cabezal) y salen con el mismo `DatoInvalidoError`, nombrando la carga y
    la fila que se intento leer.

    Se prueba sobre 'Resistencia I' porque es la combinacion cuya columna de
    permanentes imprime el simbolo gamma_p; en Servicio I y Evento Extremo I
    la tabla imprime 1.00 y no se baja a la Tabla -2.
    """
    assert fila_esperada not in TABLA_GAMMA_P_FILAS
    with _con_criterios(monkeypatch, {
            M9.CRITERIO_FACTORES_CARGA: {M9.ELEMENTO_CABEZAL: filas_del_cabezal}}):
        with pytest.raises(DatoInvalidoError) as exc:
            factores_de_carga("Resistencia I")
    assert exc.value.campo == M9.CRITERIO_FACTORES_CARGA
    assert exc.value.valor == fila_esperada
    assert carga in exc.value.motivo
    assert "no es una fila de" in exc.value.motivo


# ---------------------------------------------------------------------------
# 9.4 - Durabilidad: las dos escalas de la Tabla 4.4 y la forma del dato
# ---------------------------------------------------------------------------

def test_la_tabla_4_4_exige_al_menos_una_de_sus_dos_escalas():
    """
    QUE DEFECTO LO HARIA FALLAR: que `clase_exposicion_sulfatos` clasificara
    sin ninguna medida. Las dos escalas -- sulfato en el SUELO (% en peso) y
    sulfato en el AGUA (ppm) -- son alternativas y el expediente puede traer
    una, la otra o las dos; lo que no puede es no traer ninguna, porque
    entonces el bucle no alcanza ninguna fila y devolveria la primera, que es
    la exposicion "insignificante": el requisito MAS BAJO de la tabla,
    adoptado por omision.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        clase_exposicion_sulfatos(so4_suelo_pct=None, so4_agua_ppm=None)
    assert exc.value.campo == M9.CRITERIO_EXPOSICION_QUIMICA
    assert "ninguna de las dos escalas" in exc.value.motivo
    # con UNA sola escala si clasifica: son alternativas, no acumulativas
    for medidas in ({"so4_suelo_pct": 0.05, "so4_agua_ppm": None},
                    {"so4_suelo_pct": None, "so4_agua_ppm": 200}):
        assert "exposicion" in clase_exposicion_sulfatos(**medidas)


_TABLA_4_2_DE_PRUEBA = {clave: False for clave in EXPOSICION_ESPECIAL}
_EXPOSICION_DE_PRUEBA = {"so4_suelo_pct": 0.0, "so4_agua_ppm": None,
                         "tabla_4_2": dict(_TABLA_4_2_DE_PRUEBA)}


def _sin(diccionario, clave):
    """El mismo diccionario sin una de sus claves."""
    return {k: v for k, v in diccionario.items() if k != clave}


def _con(diccionario, **cambios):
    """El mismo diccionario con algunas claves cambiadas o anadidas."""
    return {**diccionario, **cambios}


@pytest.mark.parametrize("declarado, motivo_esperado", [
    (0.45, "se declara como un diccionario"),
    ("cloruros", "se declara como un diccionario"),
    (_sin(_EXPOSICION_DE_PRUEBA, "so4_agua_ppm"), "falta la escala"),
    (_con(_EXPOSICION_DE_PRUEBA, so4_agua_ppm="muchos"), "magnitud medida"),
    (_con(_EXPOSICION_DE_PRUEBA, so4_suelo_pct=True), "magnitud medida"),
    (_sin(_EXPOSICION_DE_PRUEBA, "tabla_4_2"), "falta 'tabla_4_2'"),
    (_con(_EXPOSICION_DE_PRUEBA,
          tabla_4_2=_con(_TABLA_4_2_DE_PRUEBA, cloruros="si")),
     "aplica o no aplica"),
    (_con(_EXPOSICION_DE_PRUEBA,
          tabla_4_2=_con(_TABLA_4_2_DE_PRUEBA, carbonatacion=True)),
     "tres filas y no mas"),
], ids=["numero", "texto", "falta_una_escala", "escala_no_numerica",
        "escala_booleana", "falta_tabla_4_2", "fila_no_booleana",
        "fila_sobrante"])
def test_el_analisis_quimico_del_ems_se_valida_antes_de_usarlo(declarado,
                                                               motivo_esperado):
    """
    QUE DEFECTO LO HARIA FALLAR: que `_exposicion_quimica_validada` leyera el
    dato con `.get()` y siguiera. Es el unico dato del expediente que no es
    un numero ni un rotulo sino un diccionario, y la unica via por la que hoy
    se puede declarar desde la ventana produce float o str: sin comprobar la
    FORMA, declararlo mal no daba un problema del expediente sino un
    AttributeError.

    Las siete formas de declararlo mal tienen motivos distintos porque exigen
    correcciones distintas -- anadir un ensayo, corregir una unidad, quitar
    una fila que la Tabla 4.2 no tiene --. El booleano entra en la tabla
    porque `True` es un entero en Python y sin la comprobacion explicita se
    leeria como "1 % de sulfatos" o "1 ppm". La octava forma -- que falte una
    de las tres filas de la Tabla 4.2 -- tiene su propio test mas arriba,
    anclado al hallazgo que la descubrio.
    """
    previo = ca.valores_dinamicos().get(M9.CRITERIO_EXPOSICION_QUIMICA)
    ca.establecer_valor_dinamico(M9.CRITERIO_EXPOSICION_QUIMICA, declarado)
    try:
        with pytest.raises(DatoInvalidoError) as exc:
            requisitos_durabilidad_concreto()
    finally:
        if previo is None:
            ca.quitar_valor_dinamico(M9.CRITERIO_EXPOSICION_QUIMICA)
        else:
            ca.establecer_valor_dinamico(M9.CRITERIO_EXPOSICION_QUIMICA, previo)
    assert exc.value.campo == M9.CRITERIO_EXPOSICION_QUIMICA
    assert motivo_esperado in exc.value.motivo


# ---------------------------------------------------------------------------
# 9.4 - La cadena del lado AASHTO del recubrimiento, eslabon por eslabon
# ---------------------------------------------------------------------------

def test_una_condicion_inexistente_tambien_se_rechaza_en_el_lado_aashto():
    """
    QUE DEFECTO LO HARIA FALLAR: que el lado AASHTO de la regla del mayor
    aceptara una condicion que el Art. 7.7.1 de E.060 no tiene. Las dos
    tablas se indexan de forma distinta -- E.060 por diametro de barra,
    AASHTO por severidad de exposicion -- y el emparejamiento cuelga de la
    condicion de E.060: sin ella no hay nada que emparejar. El gemelo de
    `recubrimiento_e060_mm` ya tiene su test; este cubre el otro lado.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        recubrimiento_aashto_mm(condicion="sumergido")
    assert exc.value.campo == "condicion"
    assert "Art. 7.7.1" in exc.value.motivo
    assert all(fila in exc.value.motivo for fila in RECUBRIMIENTO)


# Una fila que existe en la tabla de AASHTO transcrita y NO en el mapa de
# equivalencias con la del Manual de Puentes: es la desincronizacion contra la
# que existe la ultima guarda de la cadena.
FILA_SIN_EQUIVALENCIA = "fila_que_solo_existe_en_una_de_las_dos_tablas"


def _tabla_recubrimiento_con_fila_huerfana():
    tabla = dict(ca.criterio(M9.CRITERIO_TABLA_RECUBRIMIENTO).valor)
    tabla[FILA_SIN_EQUIVALENCIA] = dict(next(iter(tabla.values())))
    return tabla


@pytest.mark.parametrize("declaraciones, campo, motivo_esperado", [
    ({M9.CRITERIO_SITUACION_RECUBRIMIENTO: {"suelo_intemperie_ge_3_4": "costera"}},
     "condicion", "no tiene fila emparejada"),
    ({M9.CRITERIO_SITUACION_RECUBRIMIENTO: {"contra_suelo": "fila_inventada"}},
     "situacion", "no es una fila de la Tabla 5.10.1-1"),
    ({M9.CRITERIO_CATEGORIA_REFUERZO: "Z"},
     M9.CRITERIO_CATEGORIA_REFUERZO, "las categorias de la Tabla 5.10.1-1"),
    ({M9.CRITERIO_TABLA_RECUBRIMIENTO: _tabla_recubrimiento_con_fila_huerfana(),
      M9.CRITERIO_SITUACION_RECUBRIMIENTO: {"contra_suelo": FILA_SIN_EQUIVALENCIA}},
     "situacion", "no tiene fila equivalente declarada"),
], ids=["condicion_sin_emparejar", "situacion_fuera_de_la_tabla",
        "categoria_fuera_de_la_tabla", "tablas_desincronizadas"])
def test_la_cadena_del_recubrimiento_aashto_se_detiene_en_cada_eslabon_roto(
        monkeypatch, declaraciones, campo, motivo_esperado):
    """
    QUE DEFECTO LO HARIA FALLAR: que el lado AASHTO se calculara igual con un
    eslabon roto. Son cuatro y cada uno rompe por su lado:

      * la condicion de E.060 sin fila emparejada en
        'situacion_recubrimiento_aashto' -- el emparejamiento no lo dice
        ninguna de las dos normas y por eso se declara;
      * la situacion emparejada que no existe en la transcripcion de la
        Tabla 5.10.1-1;
      * la categoria de acero fuera de las columnas A/B/C, que es el vacio
        NOR-AAS-01 y el que puede invertir quien gobierna la regla del mayor;
      * la fila sin correspondencia declarada en
        `RECUBRIMIENTO_MP_EQUIVALENCIA`, que significa que las dos
        transcripciones se han desincronizado. Ahi seguir seria calcular el
        recubrimiento con UNA sola de las dos fuentes creyendo que se
        compararon -- el defecto que ya vivio esta cadena cuando el cruce se
        hacia por nombre de clave y se saltaba en silencio las 8 filas de la
        familia de pilotes.
    """
    assert FILA_SIN_EQUIVALENCIA not in RECUBRIMIENTO_MP_EQUIVALENCIA
    with _con_criterios(monkeypatch, declaraciones):
        with pytest.raises(DatoInvalidoError) as exc:
            recubrimiento_aashto_mm(condicion="contra_suelo")
    assert exc.value.campo == campo
    assert motivo_esperado in exc.value.motivo


# ---------------------------------------------------------------------------
# 9.2 - El ENSAMBLADOR con agua: los once mutantes que sobrevivian
# ---------------------------------------------------------------------------
#
# Una revision adversarial barrio `empujes_trasdos` y encontro ONCE mutantes
# vivos que ninguna ficha nombra. La causa es una sola: el unico test que lo
# ejecutaba de punta a punta usaba `D_f = 1.00` con el NF a 1.40 m, de modo que
# `h_agua = 0` y toda la rama del agua corria en cero --- el propio test lo
# escribia ---, y los demas asserts eran de ORDEN y de BRAZO, ninguno de VALOR.
#
# Los once, con su efecto medido sobre este mismo tablero:
#   E_hidrostatico=0.0 / U_subpresion=0.0     la carga WA desaparece
#   h_agua/2 en el empuje hidrostatico        la parte el agua por cuatro
#   B=geometria.D_f en la subpresion          U baja 37.5 %: MAS normal en la
#                                             base, y FS de deslizamiento y de
#                                             capacidad portante MAS ALTOS
#   H=geometria.H en E_a / E_s / incremento   -30.6 %, -16.7 %, -30.6 %
#   k_v=mo.k_h en el incremento sismico       -80.6 %, NO CONSERVADOR
#   h_eq_sobrecarga=0.0 / gamma_relleno=0.0   los campos de trazabilidad de LS
#                                             que este mismo trabajo anadio
#   altura_para_h_eq con `-` en vez de `+`    hoy inocuo POR ACCIDENTE: con el
#                                             tablero paralelo al trafico la
#                                             tabla da 0.6096 para 1.60, 2.00 y
#                                             2.40; con la orientacion
#                                             perpendicular si dependeria
#
# Los dorados NO se escriben aqui: salen de CP9_ENSAMBLE_TRASDOS, que se
# recalcula solo en el bloque `__main__` del fixture. Duplicarlos como
# literales en este archivo es el defecto SIS-F-14 y la fila 7 de la hoja
# `Conflictos` lo prohibe expresamente.

CP9E = CP9_ENSAMBLE_TRASDOS


@pytest.fixture
def geometria_con_agua():
    """
    El mismo cabezal de tanteo con la zapata mas profunda: `D_f = 2.00` con el
    NF a 1.40 m deja 0.60 m de agua sobre la base. Es lo unico que cambia
    respecto de `geometria`, y es lo que hace visible la rama WA.
    """
    return GeometriaCabezal(H=CP9E["H"], B=CP9E["B"], D_f=CP9E["D_f"],
                            espesor_corona=0.25, espesor_base_muro=0.35,
                            espesor_zapata=CP9E["espesor_zapata"])


def _declarar_tablero_de_prueba(monkeypatch):
    """Los criterios de tanteo del ensamble, declarados en caliente."""
    valores = {
        "phi_relleno_trasdos": CP9E["phi_grados"],
        "pendiente_relleno_trasdos_i": 0.0,
        "inclinacion_muro_beta": 0.0,
        "friccion_muro_suelo_delta": 0.0,
        "punto_aplicacion_incremento_sismico": 0.6,
        "peso_especifico_relleno_kn_m3": CP9E["gamma_relleno"],
    }
    for clave, valor in valores.items():
        original = ca.criterio(clave)
        monkeypatch.setitem(ca.CRITERIOS, clave,
                            ca.Criterio(valor=valor, etiqueta=original.etiqueta,
                                        concepto=original.concepto,
                                        justificacion=original.justificacion,
                                        fuente=original.fuente))
    _declarar_orientacion(monkeypatch, ORIENTACION_PARALELO_AL_TRAFICO)
    _declarar_borde(monkeypatch, 1.0)


def test_el_ensamble_con_agua_da_los_cinco_valores_de_su_caso_patron(
        monkeypatch, geometria_con_agua):
    """
    QUE DEFECTO LO HARIA FALLAR: que el ensamblador anulara una carga, la
    partiera, o alimentara una funcion con la altura o el ancho equivocados.
    Ninguno de esos lo veia nadie mientras el tablero corriera sin agua y los
    asserts fueran de orden.
    """
    _declarar_tablero_de_prueba(monkeypatch)
    e = empujes_trasdos(geometria=geometria_con_agua,
                        condicion=CondicionAnalisis.ESTATICO,
                        altura_empuje=CP9E["altura_empuje"],
                        NF_profundidad_m=CP9E["NF_profundidad_m"])

    assert e.K_A == pytest.approx(CP9E["Ka_esperado"], rel=CP9_TOLERANCIA_RELATIVA)
    assert e.E_activo == pytest.approx(CP9E["E_activo_esperado"],
                                       rel=CP9_TOLERANCIA_RELATIVA)
    assert e.E_sobrecarga == pytest.approx(CP9E["E_sobrecarga_esperado"],
                                           rel=CP9_TOLERANCIA_RELATIVA)
    assert e.E_hidrostatico == pytest.approx(CP9E["E_hidrostatico_esperado"],
                                             rel=CP9_TOLERANCIA_RELATIVA)
    assert e.U_subpresion == pytest.approx(CP9E["U_subpresion_esperado"],
                                           rel=CP9_TOLERANCIA_RELATIVA)


def test_el_ensamble_lleva_a_la_memoria_la_trazabilidad_de_la_sobrecarga(
        monkeypatch, geometria_con_agua):
    """
    `h_eq_sobrecarga` y `gamma_relleno` son los campos que este trabajo anadio
    para que la memoria no imprima un empuje sin la altura equivalente que lo
    produjo. Sin este assert, los dos pueden viajar en 0.0 y nadie se entera.
    """
    _declarar_tablero_de_prueba(monkeypatch)
    e = empujes_trasdos(geometria=geometria_con_agua,
                        condicion=CondicionAnalisis.ESTATICO,
                        altura_empuje=CP9E["altura_empuje"],
                        NF_profundidad_m=CP9E["NF_profundidad_m"])
    assert e.h_eq_sobrecarga == pytest.approx(CP9E["h_eq"], rel=CP9_TOLERANCIA_RELATIVA)
    assert e.gamma_relleno == pytest.approx(CP9E["gamma_relleno"],
                                            rel=CP9_TOLERANCIA_RELATIVA)
    # Y la coherencia entre los dos: E_s = gamma * Ka * h_eq * He. Si el
    # ensamblador alimenta el empuje con una altura y declara otra, cae aqui.
    assert e.E_sobrecarga == pytest.approx(
        e.gamma_relleno * e.K_A * e.h_eq_sobrecarga * CP9E["altura_empuje"],
        rel=CP9_TOLERANCIA_RELATIVA)


def test_el_incremento_sismico_usa_la_altura_de_empuje_y_el_k_v(
        monkeypatch, geometria_con_agua):
    """
    Los dos mutantes no conservadores del ensamblador: `H=geometria.H` en vez
    de `altura_empuje` (-30.6 %) y `k_v=mo.k_h` en vez de `k_v=mo.k_v`
    (-80.6 %). El lado derecho se arma con la altura DEL TEST y con el k_v de
    la cadena, no con lo que el objeto devuelve, que es lo que hace que el
    assert no sea tautologico en la dimension que mide.
    """
    _declarar_tablero_de_prueba(monkeypatch)
    e = empujes_trasdos(geometria=geometria_con_agua,
                        condicion=CondicionAnalisis.SISMICO,
                        altura_empuje=CP9E["altura_empuje"],
                        NF_profundidad_m=CP9E["NF_profundidad_m"])
    He = CP9E["altura_empuje"]
    esperado = (0.5 * CP9E["gamma_relleno"]
                * (e.mononobe_okabe.K_AE - e.mononobe_okabe.K_A)
                * He ** 2 * (1 - cadena_sismica().k_v))
    assert e.incremento_sismico == pytest.approx(esperado,
                                                 rel=CP9_TOLERANCIA_RELATIVA)
    assert e.z_incremento == pytest.approx(0.6 * He,
                                           rel=CP9_TOLERANCIA_RELATIVA)


def test_la_subpresion_se_reparte_en_el_ancho_de_zapata_y_no_en_su_canto(
        monkeypatch, geometria_con_agua):
    """
    El mutante `B=geometria.D_f` baja U un 37.5 % en este tablero. Menos
    subpresion es MAS fuerza normal en la base, y por lo tanto FS de
    deslizamiento y de capacidad portante MAS ALTOS de lo que son: la
    direccion en la que un error no avisa.
    """
    _declarar_tablero_de_prueba(monkeypatch)
    e = empujes_trasdos(geometria=geometria_con_agua,
                        condicion=CondicionAnalisis.ESTATICO,
                        altura_empuje=CP9E["altura_empuje"],
                        NF_profundidad_m=CP9E["NF_profundidad_m"])
    assert e.U_subpresion == pytest.approx(
        CP9E["gamma_agua"] * CP9E["h_agua_esperada"] * geometria_con_agua.B,
        rel=CP9_TOLERANCIA_RELATIVA)
    assert e.z_hidrostatico == pytest.approx(CP9E["h_agua_esperada"] / 3,
                                             rel=CP9_TOLERANCIA_RELATIVA)


def test_la_altura_de_entrada_de_h_eq_se_mide_hasta_el_fondo_de_la_zapata(
        monkeypatch, geometria_con_agua):
    """
    AASHTO 3.11.6.4 mide la altura de entrada de h_eq desde la superficie del
    relleno hasta el FONDO DE LA ZAPATA, con un `shall`: es
    `geometria.H + geometria.espesor_zapata` y no `geometria.H`.

    EL TEST USA LA ORIENTACION PERPENDICULAR y no la paralela, y esa es toda
    su razon de ser. Con el tablero paralelo la tabla devuelve 0.6096 m para
    1.60, 2.00 y 2.40 m --- las tres alturas candidatas ---, de modo que
    equivocar la altura de entrada daba EL MISMO NUMERO y ningun assert podia
    verlo: la correccion quedaba viva por accidente del tablero elegido.
    Perpendicular, la tabla si depende de la altura (1.204 / 1.124 / 1.044) y
    el error se hace visible.
    """
    _declarar_tablero_de_prueba(monkeypatch)
    _declarar_orientacion(monkeypatch, ORIENTACION_PERPENDICULAR_AL_TRAFICO)
    e = empujes_trasdos(geometria=geometria_con_agua,
                        condicion=CondicionAnalisis.ESTATICO,
                        altura_empuje=CP9E["altura_empuje"],
                        NF_profundidad_m=CP9E["NF_profundidad_m"])
    assert e.h_eq_sobrecarga == pytest.approx(
        CP9E["h_eq_perpendicular_a_2_40"], rel=CP9_TOLERANCIA_RELATIVA), (
        "h_eq no corresponde a H + espesor_zapata = 2.40 m. Con "
        f"{CP9E['h_eq_perpendicular_a_1_60']} la altura de entrada seria "
        "1.60 m, que es H - espesor_zapata; con geometria.H sola seria 2.00.")


def test_la_autoverificacion_del_fixture_la_corre_pytest():
    """
    El bloque `__main__` de `tests/fixtures/casos_patron.py` recalcula los
    dorados desde la formula, y ES la defensa contra MAT-D7 / SIS-F-03 (los
    dorados de CP-1 estuvieron mal toda su vida porque nadie los recalculaba).
    Pero NINGUN test lo invocaba: la etiqueta "AUTOVERIFICADOS" solo era cierta
    si alguien lo ejecutaba a mano, y una edicion futura de un dorado no la
    habria detenido la suite.

    Se ejecuta el archivo como script, en un proceso aparte, y se exige codigo
    de salida 0. En proceso aparte a proposito: el bloque usa nombres con
    guion bajo al nivel del modulo y reimportarlo dentro del interprete de
    pytest ensuciaria el espacio de nombres del fixture que todos los demas
    tests comparten.
    """
    fixture = Path(__file__).resolve().parent / "fixtures" / "casos_patron.py"
    raiz = fixture.parents[2]
    entorno = dict(os.environ)
    entorno["PYTHONPATH"] = os.pathsep.join(
        [str(raiz), str(raiz / "src"), entorno.get("PYTHONPATH", "")])
    r = subprocess.run([sys.executable, str(fixture)], cwd=raiz,
                       capture_output=True, text=True, env=entorno, timeout=120)
    assert r.returncode == 0, (
        "la autoverificacion de los casos patron fallo. Un dorado dejo de "
        f"salir de su formula:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    assert "CP-9 ensamble verificado" in r.stdout, (
        "el bloque corrio pero no llego a verificar CP-9: revisa si una "
        "excepcion temprana lo dejo a medias")
