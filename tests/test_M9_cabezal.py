"""
tests/test_M9_cabezal.py
=========================
Fase 9 (M9_cabezal.py). Cuatro bloques, en el orden de la hoja de ruta:

    9.2 cadena sismica    los seis pasos horizontales por separado, k_v
                          aparte, y el ensamble `cadena_sismica()`.
    9.2 Mononobe-Okabe    el caso limite contra tan^2(45 - phi/2) -- el test
                          que garantiza que los signos estan bien puestos --,
                          la monotonia frente a k_h y el dominio de validez.
    9.2 cargas            sobrecarga de 0.60 m equivalente, empujes, agua,
                          subpresion y las tres combinaciones AASHTO.
    9.3 estabilidad       los FS de la tabla en sus dos condiciones.
    9.4 refuerzo          regla del recubrimiento MAYOR, cuantias minimas,
                          espaciamiento y alternativa ciclopea.

Y, transversalmente, que cada vacio declarado se detiene donde debe con
`CriterioPendienteError` en vez de rellenarse en silencio.
"""

import math
from pathlib import Path

import pytest

import criterios_adoptados as ca
import datos_sitio as ds
from constantes_fisicas import GAMMA_AGUA_KN_M3
from constantes_normativas import (CICLOPEO_FC_MATRIZ_MIN,
                                   CICLOPEO_FRACCION_PIEDRA_MAX,
                                   COMBINACIONES_AASHTO, CUANTIA_MIN_MURO,
                                   ESPACIAMIENTO_MAX_ABSOLUTO,
                                   FACTOR_MURO_TABLA, FS,
                                   NQ_ZAPATA_EN_TALUD,
                                   RECUBRIMIENTO, SOBRECARGA_TRASDOS_H_EQ)
from modelos import (CondicionAnalisis, CriterioPendienteError,
                     DatoFaltanteError, DatoInvalidoError,
                     DisenoNoFactibleError, GeometriaCabezal)
from modulos.M0_carga import cargar_puntos
from modulos.M9_cabezal import (CRITERIO_CORTANTE_ALTO,
                                NUMERAL_9_1,
                                aceleracion_ajustada_sitio,
                                cuantia_de_diseno,
                                altura_agua_sobre_base,
                                angulo_inercia_sismica,
                                aplica_sobrecarga_trasdos,
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
                                requiere_temperatura_dos_caras,
                                sobrecarga_trasdos_siempre_aplica, subpresion,
                                verificar_capacidad_portante, verificar_ciclopeo,
                                verificar_cuantia, verificar_deslizamiento,
                                verificar_espaciamiento, verificar_estabilidad,
                                verificar_estabilidad_global, verificar_talud,
                                verificar_volteo)
from tests.fixtures.casos_patron import CP7_CADENA_SISMICA

TOL = 1e-12

# Los dorados de la cadena sismica se LEEN del caso patron, no se reescriben
# como literales aqui (SIS-F-14): duplicarlos hacia que corregir el fixture no
# llegara nunca a estos tests.
CP7 = CP7_CADENA_SISMICA

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
    k_h0 = coeficiente_sismico_base(A_s=A_s)
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
        k_h0=coeficiente_sismico_base(A_s=A_s), factor_muro=cadena.factor_muro)

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
    assert factor_muro() == pytest.approx(FACTOR_MURO_TABLA["rigido"])
    assert cadena_sismica().k_h == pytest.approx(
        CP7["k_h_con_muro_rigido_esperado"])
    # La otra fila de la tabla existe y es [N]; lo que es [A] es no elegirla
    assert FACTOR_MURO_TABLA["desplazable"] == pytest.approx(
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
    EL test de esta formula. Con k_h = k_v = 0 e i = beta = delta = 0,
    Mononobe-Okabe tiene que devolver EXACTAMENTE tan^2(45 - phi/2), el Ka
    que cita Sec. 9.2. Si un signo esta cambiado, aqui se ve.
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
    assert previos == sorted(previos)
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

def test_la_sobrecarga_es_de_0_60_m_de_relleno_equivalente():
    assert SOBRECARGA_TRASDOS_H_EQ == pytest.approx(0.60)
    # p = gamma * 0.60 * ka   (num. 2.1.4.3.9)
    p = presion_sobrecarga_trasdos(gamma_relleno=19.0, k_a=0.30)
    assert p == pytest.approx(19.0 * 0.60 * 0.30)


def test_el_empuje_de_sobrecarga_es_rectangular_no_triangular():
    """
    Es la diferencia entre 0.60 m de relleno EQUIVALENTE y 0.60 m de relleno
    real encima: la presion es constante en toda la altura.
    """
    gamma, k_a, H = 19.0, 0.30, 2.4
    E = empuje_sobrecarga_trasdos(gamma_relleno=gamma, k_a=k_a, H=H)
    assert E == pytest.approx(presion_sobrecarga_trasdos(
        gamma_relleno=gamma, k_a=k_a) * H)
    # y por lo tanto NO es gamma*H^2*ka/2
    assert E != pytest.approx(empuje_activo_estatico(
        gamma_relleno=gamma, k_a=k_a, H=H))


def test_la_regla_de_H_medios_para_el_trafico():
    assert aplica_sobrecarga_trasdos(distancia_trafico=1.0, H=2.4)
    assert aplica_sobrecarga_trasdos(distancia_trafico=1.2, H=2.4)   # el borde
    assert not aplica_sobrecarga_trasdos(distancia_trafico=1.5, H=2.4)


def test_en_cabezal_bajo_terraplen_siempre_aplica():
    texto = sobrecarga_trasdos_siempre_aplica()
    assert "siempre" in texto and "0.60" in texto


def test_empuje_activo_estatico_es_triangular():
    gamma, k_a, H = 19.0, 0.30, 2.4
    assert empuje_activo_estatico(gamma_relleno=gamma, k_a=k_a, H=H) == (
        pytest.approx(gamma * H ** 2 * k_a / 2))


def test_empuje_sismico_total_y_su_incremento():
    gamma, H = 19.0, 2.4
    mo = empuje_mononobe_okabe(phi_grados=34.0, i_grados=0.0, beta_grados=0.0,
                               delta_grados=0.0, k_h=0.50, k_v=0.0)
    P_AE = empuje_activo_sismico_total(gamma_relleno=gamma, K_AE=mo.K_AE,
                                       H=H, k_v=mo.k_v)
    P_A = empuje_activo_estatico(gamma_relleno=gamma, k_a=mo.K_A, H=H)
    incremento = incremento_sismico(gamma_relleno=gamma, K_AE=mo.K_AE,
                                    K_A=mo.K_A, H=H, k_v=mo.k_v)
    assert incremento == pytest.approx(P_AE - P_A)
    assert incremento > 0


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
    """'factores_carga_aashto' es [C] (AASHTO LRFD 9a ed.): ya no se detiene."""
    assert len(combinaciones()) == 3          # describir: los nombres son [N]

    resistencia = factores_de_carga("Resistencia I")
    assert resistencia["DC"] == {"max": 1.25, "min": 0.90}
    assert resistencia["EV"] == {"max": 1.35, "min": 0.90}
    assert resistencia["EH"] == {"max": 1.50, "min": 0.90}
    assert resistencia["LS"] == pytest.approx(1.75)

    servicio = factores_de_carga("Servicio I")
    assert servicio["DC"] == {"max": 1.00, "min": 1.00}

    extremo = factores_de_carga("Evento Extremo I")
    assert extremo["EQ"] == {"max": 1.00, "min": 1.00}
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
    assert estatico.valor_admisible == 1.50
    assert sismico.valor_admisible == 1.25
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


# --- E.050 Art. 20: c y phi no se combinan --------------------------------

def test_en_cohesivo_phi_se_anula():
    c, phi = parametros_resistencia_art20(c=25.0, phi_grados=28.0, cohesivo=True)
    assert (c, phi) == (25.0, 0.0)


def test_en_friccionante_c_se_anula():
    c, phi = parametros_resistencia_art20(c=25.0, phi_grados=32.0, cohesivo=False)
    assert (c, phi) == (0.0, 32.0)


# --- Zapata proxima al talud ----------------------------------------------

def test_N_q_es_cero_en_zapata_proxima_al_talud():
    assert n_q_zapata_en_talud() == pytest.approx(0.0)
    assert NQ_ZAPATA_EN_TALUD == 0.0


def test_N_s_es_cero_si_B_menor_que_Hs():
    assert n_s_zapata_en_talud(B=1.6, H_s=3.0, gamma=19.0, c=20.0) == 0.0


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


def test_el_lado_aashto_de_la_regla_del_mayor_ya_no_esta_vacio():
    """
    'recubrimiento_aashto_mm' es [C]: AASHTO LRFD Tabla 5.10.1-1 organiza el
    recubrimiento por EXPOSICION, no por diametro; La Union es corredor
    costero, asi que las tres condiciones de E.060 leen 75 mm.
    """
    assert recubrimiento_aashto_mm(condicion="contra_suelo") == pytest.approx(75.0)
    assert recubrimiento_aashto_mm(condicion="suelo_intemperie_ge_3_4") == pytest.approx(75.0)
    assert recubrimiento_aashto_mm(condicion="suelo_intemperie_le_5_8") == pytest.approx(75.0)


def test_la_regla_del_recubrimiento_mayor_ya_se_evalua_con_los_dos_operandos():
    """
    Sec. 0.2: "rige el recubrimiento MAYOR entre AASHTO y E.060". Con AASHTO
    en 75 mm (exposicion costera) y E.060 en 70/50/40 mm, AASHTO gobierna
    en los tres casos.
    """
    for condicion in ("contra_suelo", "suelo_intemperie_ge_3_4",
                      "suelo_intemperie_le_5_8"):
        r = recubrimiento_de_diseno(condicion=condicion)
        assert r.aashto_mm == pytest.approx(75.0)
        assert r.adoptado_mm == pytest.approx(75.0)
        assert r.origen == "AASHTO"


def test_la_regla_del_mayor_toma_el_aashto_cuando_gobierna(monkeypatch):
    """
    Se inyecta un lado AASHTO ficticio para probar la REGLA, que es lo que
    este modulo aporta; el valor real sigue siendo un vacio del expediente.
    """
    monkeypatch.setitem(ca.CRITERIOS, "recubrimiento_aashto_mm",
                        ca.Criterio(valor={"contra_suelo": 75.0,
                                           "suelo_intemperie_ge_3_4": 25.0},
                                    etiqueta="A", concepto="prueba",
                                    justificacion="prueba", fuente="prueba"))

    manda_aashto = recubrimiento_de_diseno(condicion="contra_suelo")
    assert manda_aashto.adoptado_mm == pytest.approx(75.0)
    assert manda_aashto.origen == "AASHTO"

    manda_e060 = recubrimiento_de_diseno(condicion="suelo_intemperie_ge_3_4")
    assert manda_e060.adoptado_mm == pytest.approx(50.0)
    assert manda_e060.origen == "E.060"
    # los dos operandos viajan en el resultado, no solo el ganador
    assert manda_e060.e060_mm == 50.0 and manda_e060.aashto_mm == 25.0


def test_el_aumento_por_ambiente_corrosivo_se_declara_y_no_se_calcula():
    aviso = aviso_ambiente_corrosivo()
    assert "7.7.5.1" in aviso and "no lo calcula" in aviso


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
    ok = verificar_ciclopeo(fc_matriz=12.0, fraccion_piedra=0.25)
    assert all(v.cumple for v in ok)
    assert [v.codigo for v in ok] == ["R4", "R5"]

    flojo = verificar_ciclopeo(fc_matriz=8.0, fraccion_piedra=0.40)
    assert not any(v.cumple for v in flojo)
    assert flojo[0].valor_admisible == CICLOPEO_FC_MATRIZ_MIN
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
    "factores_carga_aashto", "peso_especifico_concreto_kn_m3",
    "recubrimiento_aashto_mm", "procedimiento_flexion_corte_aashto_sec5",
])
def test_los_cuatro_datos_de_C_2_estan_cerrados_como_C(clave):
    """
    Los cuatro criterios de la Fase 9 que dependian de una tabla AASHTO sin
    eleccion de ingenieria: transcripcion directa, etiqueta [C], fuente
    citada con edicion y pagina.
    """
    criterio = ca.criterio(clave)
    assert clave not in ca.criterios_sin_valor()
    assert criterio.valor is not None
    assert criterio.etiqueta == "C"
    assert not criterio.fuente.startswith("PENDIENTE")
    assert "AASHTO LRFD" in criterio.fuente
