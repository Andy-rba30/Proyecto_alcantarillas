"""
tests/test_M4_control.py
=========================
M4 contra las Fases 4.2 y 4.3, pieza por pieza:

    1. tirante_critico   contra CP-6: autoconsistencia (residuo de
       Q^2*T/(g*A^3) = 1 nulo y Froude = 1), y la independencia de n y S que
       lo distingue del tirante normal de M3.
    2. control_entrada   contra CP-5 / CP-5B / CP-5C: las tres ramas, el q*
       que las separa, la continuidad de la interpolacion en 3.5 y en 4.0, y
       la guardia de que Ks*S NO se omite.
    3. control_salida    contra CP-8: la constante de friccion es 19.63 (SI)
       y no 29 (imperial) -- test_constante_friccion_es_SI_no_imperial --, mas
       las dos ramas de h_o = max(TW, (y_c + D)/2).
    4. hw_gobernante     el mayor de los dos, CON la etiqueta de cual fue.

Cada pieza se prueba sola: las piezas 2 y 3 aceptan un TiranteCritico
inyectado, de modo que un fallo del solver critico no arrastra a los otros
dos tests a rojo por una causa que no es suya.
"""

import math

import pytest

import criterios_adoptados as ca
from constantes_fisicas import G
from constantes_normativas import (KU_SI, K_FRICCION_SI,
                                   Q_LIM_NO_SUMERGIDO, Q_LIM_SUMERGIDO)
from dominios import S_CAUCE_MAX
from modelos import (ConstantesHDS5, ControlGobernante, DatoInvalidoError,
                     DisenoNoFactibleError, RegimenEntrada, ResultadoHidraulico,
                     TiranteCritico)
from modulos.M2_material import catalogo
from modulos.M3_hidraulica import geometria
from modulos.M4_control import (CRITERIO_GEOMETRIA_SALIDA,
                                CRITERIO_TRANSICION, NUMERAL_CRITICO,
                                NUMERAL_ENTRADA, area_llena,
                                caudal_adimensional,
                                control_entrada, control_salida,
                                hw_gobernante, perdida_carga,
                                radio_hidraulico_lleno, resolver_control,
                                tirante_critico)
from modelos import (DatoInvalidoError, ErrorProyecto,
                     LimiteNumericoError, TipoMaterial)
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.fixtures.casos_patron import (CP2_GEOMETRIA_MANNING,
                                         CP5_TRANSICION_HDS5,
                                         CP5B_NO_SUMERGIDO, CP5C_SUMERGIDO,
                                         CP6_TIRANTE_CRITICO,
                                         CP8_CONTROL_SALIDA)
from tests.apoyo.aproximacion import REL_TRANSPORTE


@pytest.fixture
def concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


@pytest.fixture
def hds5(concreto):
    """Carta 'circular concreto, square edge w/headwall' de la Tabla A.1."""
    return concreto.hds5


# ===========================================================================
# Pieza 1 - Tirante critico (Sec. 4.2.1)
# ===========================================================================

@pytest.mark.parametrize("Q", CP6_TIRANTE_CRITICO["Q_casos"])
def test_el_residuo_de_la_ecuacion_critica_se_anula(Q):
    """CP-6: no hay valor cerrado con que contrastar, se exige
    autoconsistencia -- Q^2*T/(g*A^3) = 1 en la solucion."""
    c = CP6_TIRANTE_CRITICO
    critico = tirante_critico(Q=Q, D=c["D"])

    g = critico.geometria
    residuo = Q ** 2 * g.T / (G * g.A ** 3) - 1
    assert abs(residuo) < c["residuo_maximo_admisible"]


@pytest.mark.parametrize("Q", CP6_TIRANTE_CRITICO["Q_casos"])
def test_el_froude_vale_uno_en_el_tirante_critico(Q):
    """CP-6: F = V/sqrt(g*A/T) = 1 es la definicion misma de estado critico."""
    c = CP6_TIRANTE_CRITICO
    critico = tirante_critico(Q=Q, D=c["D"])

    g = critico.geometria
    froude = critico.V / math.sqrt(G * g.A / g.T)
    assert froude == pytest.approx(c["froude_esperado"], abs=c["froude_tolerancia"])


def test_la_velocidad_critica_es_Q_sobre_area():
    """
    Excepcion declarada a la guardia de M3 (V*A != Q): en el tirante critico
    la velocidad SI es Q/A, porque la ecuacion que lo define no contiene n y
    no hay dos ramas de rugosidad entre las que elegir.
    """
    c = CP6_TIRANTE_CRITICO
    Q = c["Q_casos"][0]
    critico = tirante_critico(Q=Q, D=c["D"])

    assert critico.V == pytest.approx(Q / critico.geometria.A, rel=1e-12)


def test_la_energia_critica_es_yc_mas_la_carga_de_velocidad():
    """H_c = y_c + V_c^2/(2g): lo que consume la Forma 1 de Sec. 4.2."""
    c = CP6_TIRANTE_CRITICO
    critico = tirante_critico(Q=c["Q_casos"][2], D=c["D"])

    assert critico.H_c == pytest.approx(
        critico.y_c + critico.V ** 2 / (2 * G), rel=1e-12)
    assert critico.H_c > critico.y_c


def test_el_tirante_critico_no_depende_de_n_ni_de_S():
    """
    La distincion con M3 que la hoja de ruta pide sostener: son DOS solvers,
    no dos llamadas al mismo. La firma de tirante_critico() ni siquiera
    admite n ni S, y el resultado crece solo con Q.
    """
    c = CP6_TIRANTE_CRITICO
    criticos = [tirante_critico(Q=Q, D=c["D"]) for Q in c["Q_casos"]]
    tirantes = [k.y_c for k in criticos]

    # Monotonia, no igualdad: `lista == sorted(lista)` compara floats con
    # `==` (aunque sea contra una permutacion de si misma) y ademas dice
    # menos de lo que se quiere afirmar.
    assert all(anterior <= siguiente
               for anterior, siguiente in zip(tirantes, tirantes[1:])), (
        "y_c debe crecer monotono con Q")
    assert all(0 < k.y_c < c["D"] for k in criticos)


def test_el_tirante_critico_de_cp2_queda_bajo_el_normal_en_pendiente_suave():
    """
    Con S = 0.005 el flujo de CP-2 es subcritico (regimen lento): y_c < y_n.
    Es la comprobacion cruzada entre los dos solvers -- si el critico saliera
    por encima del normal a esa pendiente, uno de los dos estaria mal.
    """
    c = CP2_GEOMETRIA_MANNING
    critico = tirante_critico(Q=c["Q_con_n_max_esperado"], D=c["D"])
    y_normal = c["y_sobre_D"] * c["D"]

    assert critico.y_c < y_normal


@pytest.mark.parametrize("kwargs, campo", [
    ({"Q": 0.0, "D": 0.90}, "Q"),
    ({"Q": -1.0, "D": 0.90}, "Q"),
    ({"Q": 1.0, "D": 0.0}, "D"),
])
def test_tirante_critico_valida_sus_parametros(kwargs, campo):
    with pytest.raises(DatoInvalidoError) as exc:
        tirante_critico(**kwargs)
    assert exc.value.campo == campo


# ===========================================================================
# Pieza 2 - Control de entrada, HDS-5 (Sec. 4.2)
# ===========================================================================

def test_area_llena_y_radio_hidraulico_lleno():
    c = CP5_TRANSICION_HDS5
    assert area_llena(c["D"]) == pytest.approx(c["A_llena_esperada"], abs=1e-5)
    assert radio_hidraulico_lleno(c["D"]) == pytest.approx(c["D"] / 4, rel=1e-12)


def test_ku_es_el_valor_metrico():
    """Ku = 1.811 (SI). El 1.0 imperial daria un q* 1.811 veces menor y
    cambiaria de rama sin avisar."""
    assert KU_SI == pytest.approx(CP5_TRANSICION_HDS5["Ku"], abs=1e-9)


@pytest.mark.parametrize("caso, esperado", [
    (CP5B_NO_SUMERGIDO, CP5B_NO_SUMERGIDO["q_estrella_aprox"]),
    (CP5C_SUMERGIDO, CP5C_SUMERGIDO["q_estrella_aprox"]),
])
def test_caudal_adimensional_reproduce_los_casos_patron(caso, esperado):
    assert caudal_adimensional(Q=caso["Q"], D=caso["D"]) == pytest.approx(
        esperado, abs=CP5_TRANSICION_HDS5["tolerancia"])


def test_caudal_adimensional_en_transicion_reproduce_cp5():
    c = CP5_TRANSICION_HDS5
    q = caudal_adimensional(Q=c["Q"], D=c["D"])
    assert q == pytest.approx(c["q_estrella_esperado"], abs=c["tolerancia"])
    assert Q_LIM_NO_SUMERGIDO < q < Q_LIM_SUMERGIDO


def test_el_area_de_q_estrella_es_la_llena_y_no_la_del_tirante():
    """
    q* se define sobre la seccion LLENA (CP-5: A = pi*D^2/4 = 0.63617 m2).
    Usar el area del tirante daria un q* mayor y podria saltar de rama.
    """
    c = CP5_TRANSICION_HDS5
    # El area va sin redondear: CP-5 la publica a cinco decimales (0.63617) y
    # contra ese valor la igualdad solo vale hasta la tolerancia del fixture.
    esperado = KU_SI * c["Q"] / (math.pi * c["D"] ** 2 / 4 * math.sqrt(c["D"]))
    assert caudal_adimensional(Q=c["Q"], D=c["D"]) == pytest.approx(esperado, rel=1e-12)

    con_area_del_tirante = KU_SI * c["Q"] / (
        CP2_GEOMETRIA_MANNING["A_esperado"] * math.sqrt(c["D"]))
    assert caudal_adimensional(Q=c["Q"], D=c["D"]) < con_area_del_tirante


@pytest.mark.parametrize("caso, regimen_esperado", [
    (CP5B_NO_SUMERGIDO, RegimenEntrada.NO_SUMERGIDO),
    (CP5_TRANSICION_HDS5, RegimenEntrada.TRANSICION),
    (CP5C_SUMERGIDO, RegimenEntrada.SUMERGIDO),
])
def test_cada_caso_patron_cae_en_su_rama(caso, regimen_esperado, hds5):
    resultado = control_entrada(Q=caso["Q"], D=caso["D"], S=0.005, hds5=hds5)
    assert resultado.regimen is regimen_esperado


def test_la_rama_no_sumergida_aplica_la_forma_1(hds5):
    """HWi/D = H_c/D + K*(q*)^M + Ks*S, con H_c del tirante critico."""
    c = CP5B_NO_SUMERGIDO
    S = 0.005
    critico = tirante_critico(Q=c["Q"], D=c["D"])
    resultado = control_entrada(Q=c["Q"], D=c["D"], S=S, hds5=hds5, critico=critico)

    esperado = (critico.H_c / c["D"]
                + hds5.K * resultado.q_estrella ** hds5.M
                + hds5.Ks * S)
    assert resultado.HW_sobre_D == pytest.approx(esperado, rel=1e-12)
    assert resultado.HW == pytest.approx(esperado * c["D"], rel=1e-12)


def test_la_rama_sumergida_aplica_la_forma_cuadratica(hds5):
    """HWi/D = c*(q*)^2 + Y + Ks*S: sin H_c, la geometria critica no entra."""
    c = CP5C_SUMERGIDO
    S = 0.005
    resultado = control_entrada(Q=c["Q"], D=c["D"], S=S, hds5=hds5)

    esperado = hds5.c * resultado.q_estrella ** 2 + hds5.Y + hds5.Ks * S
    assert resultado.HW_sobre_D == pytest.approx(esperado, rel=1e-12)


def test_la_transicion_interpola_y_no_devuelve_ninguna_rama_pura(hds5):
    """
    CP-5 lo dice expreso: "el test debe fallar si el modulo devuelve el valor
    puro de la forma no sumergida o de la sumergida en vez de interpolar".
    """
    c = CP5_TRANSICION_HDS5
    S = 0.005
    critico = tirante_critico(Q=c["Q"], D=c["D"])
    resultado = control_entrada(Q=c["Q"], D=c["D"], S=S, hds5=hds5, critico=critico)

    q = resultado.q_estrella
    puro_no_sumergido = critico.H_c / c["D"] + hds5.K * q ** hds5.M + hds5.Ks * S
    puro_sumergido = hds5.c * q ** 2 + hds5.Y + hds5.Ks * S

    assert resultado.regimen is RegimenEntrada.TRANSICION
    assert resultado.HW_sobre_D != pytest.approx(puro_no_sumergido, rel=1e-6)
    assert resultado.HW_sobre_D != pytest.approx(puro_sumergido, rel=1e-6)


def test_la_transicion_declara_que_la_recta_es_simplificacion_y_no_HDS5(hds5):
    """
    HDS-5 no interpola linealmente: empalma las dos ramas con una curva
    tangente empirica sin ecuacion publicada. La recta es una simplificacion
    ADOPTADA, y tiene que quedar registrada como criterio [C] cuando se usa,
    para que M11 la imprima. Fuera de la transicion no debe registrarse:
    entonces se aplican las ecuaciones literales de la Tabla A.1.
    """
    c = CP5_TRANSICION_HDS5
    assert ca.criterio(CRITERIO_TRANSICION).etiqueta == "C"

    # se limpia SOLO esta clave, para no borrar el registro de las demas
    ca._USADOS.discard(CRITERIO_TRANSICION)
    control_entrada(Q=CP5B_NO_SUMERGIDO["Q"], D=CP5B_NO_SUMERGIDO["D"],
                    S=0.005, hds5=hds5)
    assert CRITERIO_TRANSICION not in ca.criterios_usados()

    control_entrada(Q=c["Q"], D=c["D"], S=0.005, hds5=hds5)
    assert CRITERIO_TRANSICION in ca.criterios_usados()


def test_un_metodo_de_transicion_distinto_no_se_aplica_en_silencio(hds5):
    """
    Si alguien declara la curva tangente del HDS-5, M4 no la implementa: debe
    decirlo, no seguir devolviendo la recta bajo otra etiqueta.
    """
    c = CP5_TRANSICION_HDS5
    ca.establecer_valor_dinamico(CRITERIO_TRANSICION, "curva_tangente_hds5")
    try:
        with pytest.raises(DatoInvalidoError):
            control_entrada(Q=c["Q"], D=c["D"], S=0.005, hds5=hds5)
    finally:
        ca.quitar_valor_dinamico(CRITERIO_TRANSICION)


def test_la_interpolacion_reproduce_la_recta_entre_los_dos_extremos(hds5):
    """
    Se interpola entre la forma no sumergida evaluada en q* = 3.5 y la
    sumergida evaluada en q* = 4.0, no entre las dos evaluadas en el q* real.
    """
    c = CP5_TRANSICION_HDS5
    S = 0.005
    critico = tirante_critico(Q=c["Q"], D=c["D"])
    resultado = control_entrada(Q=c["Q"], D=c["D"], S=S, hds5=hds5, critico=critico)

    inferior = (critico.H_c / c["D"]
                + hds5.K * Q_LIM_NO_SUMERGIDO ** hds5.M + hds5.Ks * S)
    superior = hds5.c * Q_LIM_SUMERGIDO ** 2 + hds5.Y + hds5.Ks * S
    peso = ((resultado.q_estrella - Q_LIM_NO_SUMERGIDO)
            / (Q_LIM_SUMERGIDO - Q_LIM_NO_SUMERGIDO))

    assert resultado.HW_sobre_D == pytest.approx(
        inferior + peso * (superior - inferior), rel=1e-12)
    assert min(inferior, superior) <= resultado.HW_sobre_D <= max(inferior, superior)


def test_la_curva_empalma_continua_en_los_dos_limites(hds5):
    """
    En q* = 3.5 y en q* = 4.0 la interpolacion debe valer lo mismo que la
    rama pura de cada lado: un salto ahi seria un HW discontinuo frente a un
    cambio infinitesimal de caudal.
    """
    D, S = 0.90, 0.005
    A_llena = area_llena(D)

    def Q_para(q_estrella):
        return q_estrella * A_llena * math.sqrt(D) / KU_SI

    epsilon = 1e-7
    for limite in (Q_LIM_NO_SUMERGIDO, Q_LIM_SUMERGIDO):
        dentro = control_entrada(Q=Q_para(limite + epsilon) if limite == Q_LIM_NO_SUMERGIDO
                                 else Q_para(limite - epsilon),
                                 D=D, S=S, hds5=hds5)
        fuera = control_entrada(Q=Q_para(limite), D=D, S=S, hds5=hds5)
        assert dentro.regimen is RegimenEntrada.TRANSICION
        assert dentro.HW_sobre_D == pytest.approx(fuera.HW_sobre_D, abs=1e-6)


# --- Ks: no esta en la Tabla A.1 y no se omite -----------------------------

def test_ks_esta_en_todas_las_cartas_de_la_tabla_a1():
    """
    Ks NO figura en la Tabla A.1: viene de la formulacion. La guardia es que
    `ConstantesHDS5` lo declare obligatorio y que ninguna carta lo traiga en
    cero por descuido.
    """
    from constantes_normativas import HDS5_INLET

    for nombre, fila in HDS5_INLET.items():
        assert "Ks" in fila, f"la carta '{nombre}' perdio el Ks"
        assert any(fila["Ks"] == pytest.approx(k, rel=REL_TRANSPORTE)
               for k in (-0.5, 0.7)), (
            f"la carta '{nombre}' tiene Ks={fila['Ks']}: la formulacion solo "
            "admite -0.5 (sin inglete) y +0.7 (inglete)"
        )

    with pytest.raises(TypeError):
        ConstantesHDS5(K=0.0098, M=2.00, c=0.0398, Y=0.67)   # sin Ks


@pytest.mark.parametrize("caso", [CP5B_NO_SUMERGIDO, CP5C_SUMERGIDO,
                                  CP5_TRANSICION_HDS5])
def test_el_termino_ks_por_S_no_se_omite(caso, hds5):
    """
    Con Ks = -0.5, dos pendientes distintas tienen que dar HW distintos. Si
    alguien borra el termino, los dos resultados coinciden y este test cae.
    El efecto es chico a proposito -- unos milimetros -- porque ese es
    exactamente el error que no se ve en una revision a ojo.
    """
    suave = control_entrada(Q=caso["Q"], D=caso["D"], S=0.001, hds5=hds5)
    fuerte = control_entrada(Q=caso["Q"], D=caso["D"], S=0.050, hds5=hds5)

    delta_esperado = hds5.Ks * (0.050 - 0.001)
    assert suave.HW_sobre_D != pytest.approx(fuerte.HW_sobre_D, abs=1e-9)
    assert fuerte.HW_sobre_D - suave.HW_sobre_D == pytest.approx(delta_esperado, rel=1e-9)


def test_con_ks_negativo_mas_pendiente_significa_menos_carga(hds5):
    """Ks = -0.5 (embocadura no en inglete): el signo importa, no solo el
    modulo. Un tubo mas empinado entra mejor, no peor."""
    assert hds5.Ks < 0
    c = CP5B_NO_SUMERGIDO
    suave = control_entrada(Q=c["Q"], D=c["D"], S=0.001, hds5=hds5)
    fuerte = control_entrada(Q=c["Q"], D=c["D"], S=0.050, hds5=hds5)
    assert fuerte.HW < suave.HW


def test_una_carta_en_inglete_invierte_el_signo(hds5):
    """La carta 'circular_cmp_mitered' trae Ks = +0.7: mas pendiente, mas
    carga. Es la otra mitad de la formulacion, no un caso teorico."""
    from constantes_normativas import HDS5_INLET

    inglete = ConstantesHDS5.desde_dict(HDS5_INLET["circular_cmp_mitered"])
    assert inglete.Ks > 0

    c = CP5B_NO_SUMERGIDO
    suave = control_entrada(Q=c["Q"], D=c["D"], S=0.001, hds5=inglete)
    fuerte = control_entrada(Q=c["Q"], D=c["D"], S=0.050, hds5=inglete)
    assert fuerte.HW > suave.HW


def test_control_entrada_valida_la_pendiente(hds5):
    with pytest.raises(DatoInvalidoError) as exc:
        control_entrada(Q=1.0, D=0.90, S=0.0, hds5=hds5)
    assert exc.value.campo == "S"


# ===========================================================================
# Pieza 3 - Control de salida (Sec. 4.3)
# ===========================================================================

def test_constante_friccion_es_SI_no_imperial():
    """
    LA guardia obligatoria de Sec. 4.3. El 29 de la literatura FHWA es del
    sistema ingles y en metrico no falla ruidosamente: devuelve numeros
    plausibles y equivocados. Con los datos de CP-8, 0.5455 m en vez de
    0.4977 m -- un 9.6 % que nadie detecta a ojo.

    El test ataca por tres lados a la vez, porque cada uno solo cubre una
    forma de meter el error:
      1. la constante declarada vale 19.63 y no 29;
      2. la H que devuelve el modulo es la de CP-8 con 19.63;
      3. y NO es la que saldria con 29 -- si alguien sustituye la constante,
         el punto 2 falla; si ademas "corrige" el caso patron, falla el 3.
    """
    c = CP8_CONTROL_SALIDA

    assert K_FRICCION_SI == pytest.approx(c["K_friccion_SI_correcto"], abs=1e-9)
    assert K_FRICCION_SI != pytest.approx(c["K_friccion_imperial_incorrecto"], abs=1e-9)

    H = perdida_carga(V=c["V"], R=c["R"], n=c["n"], L=c["L"], ke=c["ke"])

    assert H == pytest.approx(c["H_esperado_con_K_SI"], abs=1e-4)
    assert H != pytest.approx(c["H_con_29_incorrecto"], abs=1e-3)

    H_imperial = ((1 + c["ke"] + c["K_friccion_imperial_incorrecto"]
                   * c["n"] ** 2 * c["L"] / c["R"] ** (4 / 3))
                  * c["V"] ** 2 / (2 * G))
    assert H_imperial == pytest.approx(c["H_con_29_incorrecto"], abs=1e-4)
    assert H < H_imperial


def test_la_perdida_de_carga_reproduce_la_formula_de_la_hoja_de_ruta():
    c = CP8_CONTROL_SALIDA
    esperado = ((1 + c["ke"] + K_FRICCION_SI * c["n"] ** 2 * c["L"] / c["R"] ** (4 / 3))
                * c["V"] ** 2 / (2 * G))
    assert perdida_carga(V=c["V"], R=c["R"], n=c["n"], L=c["L"],
                         ke=c["ke"]) == pytest.approx(esperado, rel=1e-12)


def test_el_ke_por_defecto_sale_del_criterio_adoptado():
    """CP-8 usaba ke=0.5 como dato suelto; hoy ese 0.5 esta declarado en
    'ke_entrada' [C] y el modulo lo lee de ahi si no se le pasa."""
    c = CP8_CONTROL_SALIDA
    assert ca.valor("ke_entrada") == pytest.approx(c["ke"], abs=1e-9)

    con_criterio = perdida_carga(V=c["V"], R=c["R"], n=c["n"], L=c["L"])
    explicito = perdida_carga(V=c["V"], R=c["R"], n=c["n"], L=c["L"], ke=c["ke"])
    assert con_criterio == pytest.approx(explicito, rel=1e-12)


def test_la_friccion_crece_con_la_longitud_y_con_n():
    c = CP8_CONTROL_SALIDA
    base = perdida_carga(V=c["V"], R=c["R"], n=c["n"], L=c["L"], ke=c["ke"])
    mas_largo = perdida_carga(V=c["V"], R=c["R"], n=c["n"], L=2 * c["L"], ke=c["ke"])
    mas_rugoso = perdida_carga(V=c["V"], R=c["R"], n=0.030, L=c["L"], ke=c["ke"])

    assert mas_largo > base
    assert mas_rugoso > base


def test_la_geometria_de_referencia_es_la_seccion_llena():
    """
    Sec. 4.3 no dice de que seccion salen V y R: la eleccion esta declarada
    en el criterio 'geometria_control_salida' [C]. El test la fija para que
    no pueda cambiar en silencio.
    """
    assert ca.valor("geometria_control_salida") == "seccion_llena"

    D, Q = 0.90, 1.0
    salida = control_salida(Q=Q, D=D, S=0.005, L=20.0, TW=0.0,
                            n=0.013, ke=0.5)

    assert salida.R == pytest.approx(radio_hidraulico_lleno(D), rel=1e-12)
    assert salida.V == pytest.approx(Q / area_llena(D), rel=1e-12)
    assert salida.R != pytest.approx(CP2_GEOMETRIA_MANNING["R_esperado"], rel=1e-3)


def test_ho_toma_la_rama_geometrica_con_TW_bajo():
    """h_o = max(TW, (y_c + D)/2): con salida libre gobierna la geometria."""
    D, Q = 0.90, 1.0
    critico = tirante_critico(Q=Q, D=D)
    salida = control_salida(Q=Q, D=D, S=0.005, L=20.0, TW=0.0, n=0.013, ke=0.5)

    assert salida.h_o == pytest.approx((critico.y_c + D) / 2, rel=1e-9)
    assert not salida.ahogado_por_TW


def test_ho_toma_el_TW_cuando_el_receptor_ahoga_la_salida():
    """La situacion que Sec. 4.3 advierte: el dren tiene nivel propio y es el
    que manda el remanso aguas arriba."""
    D, Q = 0.90, 1.0
    TW_alto = 1.60
    salida = control_salida(Q=Q, D=D, S=0.005, L=20.0, TW=TW_alto, n=0.013, ke=0.5)

    assert salida.h_o == pytest.approx(TW_alto, rel=1e-12)
    assert salida.ahogado_por_TW


def test_la_ecuacion_de_control_de_salida_es_H_mas_ho_menos_SL():
    D, Q, S, L = 0.90, 1.0, 0.005, 20.0
    salida = control_salida(Q=Q, D=D, S=S, L=L, TW=0.30, n=0.013, ke=0.5)

    assert salida.caida == pytest.approx(S * L, rel=1e-12)
    assert salida.HW == pytest.approx(salida.H + salida.h_o - S * L, rel=1e-12)


def test_un_TW_mas_alto_sube_el_HW_de_salida():
    comun = dict(Q=1.0, D=0.90, S=0.005, L=20.0, n=0.013, ke=0.5)
    bajo = control_salida(TW=0.0, **comun)
    alto = control_salida(TW=1.60, **comun)
    assert alto.HW > bajo.HW


@pytest.mark.parametrize("kwargs, campo", [
    ({"Q": 1.0, "D": 0.90, "S": 0.0, "L": 20.0, "TW": 0.0, "n": 0.013}, "S"),
    ({"Q": 1.0, "D": 0.90, "S": 0.005, "L": 0.0, "TW": 0.0, "n": 0.013}, "L"),
    ({"Q": 1.0, "D": 0.90, "S": 0.005, "L": 20.0, "TW": -0.1, "n": 0.013}, "TW"),
    ({"Q": 1.0, "D": 0.90, "S": 0.005, "L": 20.0, "TW": 0.0, "n": 0.0}, "n"),
])
def test_control_salida_valida_sus_parametros(kwargs, campo):
    with pytest.raises(DatoInvalidoError) as exc:
        control_salida(**kwargs)
    assert exc.value.campo == campo


# ===========================================================================
# Pieza 4 - Cual de los dos gobierna
# ===========================================================================

def test_gobierna_la_salida_cuando_el_receptor_ahoga(hds5):
    """Un TW alto empuja el HW de salida por encima del de entrada."""
    Q, D, S, L = 1.0, 0.90, 0.005, 20.0
    entrada = control_entrada(Q=Q, D=D, S=S, hds5=hds5)
    salida = control_salida(Q=Q, D=D, S=S, L=L, TW=2.50, n=0.013, ke=0.5)

    HW, control = hw_gobernante(entrada, salida)

    assert control is ControlGobernante.SALIDA
    assert HW == pytest.approx(salida.HW, rel=1e-12)
    assert HW > entrada.HW


def test_gobierna_la_entrada_con_salida_libre_y_conducto_corto(hds5):
    Q, D, S, L = 1.0, 0.90, 0.030, 8.0
    entrada = control_entrada(Q=Q, D=D, S=S, hds5=hds5)
    salida = control_salida(Q=Q, D=D, S=S, L=L, TW=0.0, n=0.013, ke=0.5)

    HW, control = hw_gobernante(entrada, salida)

    assert control is ControlGobernante.ENTRADA
    assert HW == pytest.approx(entrada.HW, rel=1e-12)


def test_el_gobernante_es_siempre_el_mayor_de_los_dos(hds5):
    """La regla, sin depender del escenario: max(HW_entrada, HW_salida)."""
    Q, D, S, L = 1.0, 0.90, 0.005, 20.0
    entrada = control_entrada(Q=Q, D=D, S=S, hds5=hds5)

    for TW in (0.0, 0.30, 0.80, 1.50, 2.50):
        salida = control_salida(Q=Q, D=D, S=S, L=L, TW=TW, n=0.013, ke=0.5)
        HW, control = hw_gobernante(entrada, salida)

        assert HW == pytest.approx(max(entrada.HW, salida.HW), rel=1e-12)
        esperado = (ControlGobernante.SALIDA if salida.HW > entrada.HW
                    else ControlGobernante.ENTRADA)
        assert control is esperado


def test_el_resultado_dice_cual_goberno_y_conserva_los_dos_HW(concreto):
    """
    `ResultadoHidraulico` no devuelve el maximo a secas: lleva los dos HW y
    la etiqueta. Su propiedad HW debe coincidir con el del control marcado.
    """
    c = CP2_GEOMETRIA_MANNING
    resultado = resolver_control(D=c["D"], Q=c["Q_con_n_max_esperado"], S=c["S"],
                                 L=20.0, TW=2.50, material=concreto)

    assert isinstance(resultado, ResultadoHidraulico)
    assert resultado.control_gobernante is ControlGobernante.SALIDA
    assert resultado.HW == pytest.approx(resultado.HW_salida, rel=1e-12)
    assert resultado.HW == pytest.approx(
        max(resultado.HW_entrada, resultado.HW_salida), rel=1e-12)


def test_resolver_control_conserva_el_reparto_de_rugosidades(concreto):
    """
    y_normal y la friccion del control de salida con n_max; las DOS
    velocidades tal como las deja M3 -- `V_erosion` con n_min (techos) y
    `V_sedimentacion` con n_max (piso de V2) --; el tirante critico sin n. La
    regla de doble n de Sec. 4.1 no se pierde al pasar por M4.
    """
    c = CP2_GEOMETRIA_MANNING
    Q = c["Q_con_n_max_esperado"]
    resultado = resolver_control(D=c["D"], Q=Q, S=c["S"], L=20.0, TW=0.30,
                                 material=concreto)

    assert resultado.y_normal == pytest.approx(c["y_sobre_D"] * c["D"], abs=1e-3)
    assert resultado.V_erosion == pytest.approx(c["V_con_n_min_esperado"],
                                                abs=c["tolerancia_hidraulica"])
    assert resultado.V_sedimentacion == pytest.approx(
        c["V_con_n_max_esperado"], abs=c["tolerancia_hidraulica"])
    assert resultado.y_critico == pytest.approx(tirante_critico(Q, c["D"]).y_c,
                                                rel=1e-9)
    assert resultado.Q == pytest.approx(Q, rel=1e-12)


def test_resolver_control_devuelve_none_si_el_tirante_normal_no_existe(concreto):
    """Mismo contrato que M3: 'este diametro no alcanza' es un resultado de
    diseno, no una excepcion."""
    assert resolver_control(D=0.90, Q=100.0, S=0.005, L=20.0, TW=0.0,
                            material=concreto) is None


def test_la_geometria_critica_es_la_misma_en_las_dos_piezas(hds5):
    """
    El critico se resuelve UNA vez y se inyecta en las dos piezas que lo
    necesitan. Si cada una lo recalculara por su cuenta, dos Brent distintos
    podrian devolver y_c distintos al ultimo bit y el h_o dejaria de casar
    con el H_c del control de entrada.
    """
    Q, D, S = 1.0, 0.90, 0.005
    critico = tirante_critico(Q, D)
    entrada = control_entrada(Q=Q, D=D, S=S, hds5=hds5, critico=critico)
    salida = control_salida(Q=Q, D=D, S=S, L=20.0, TW=0.0, n=0.013, ke=0.5,
                            critico=critico)

    assert entrada.critico is critico
    assert salida.critico is critico
    # Es identidad de OBJETO, no igualdad de float: las dos lineas de
    # arriba ya afirman que los dos son `critico`, y compararlos por valor
    # afirmaba menos con una igualdad de punto flotante de por medio.
    assert entrada.critico is salida.critico


def test_la_geometria_critica_inyectada_da_lo_mismo_que_la_resuelta_dentro(hds5):
    """Inyectar el critico es una optimizacion, no un cambio de resultado."""
    Q, D, S = 1.0, 0.90, 0.005
    con_inyeccion = control_entrada(Q=Q, D=D, S=S, hds5=hds5,
                                    critico=tirante_critico(Q, D))
    sin_inyeccion = control_entrada(Q=Q, D=D, S=S, hds5=hds5)

    assert con_inyeccion.HW == pytest.approx(sin_inyeccion.HW, rel=1e-12)


def test_las_tres_piezas_son_tipos_de_modelos(hds5):
    """Ningun dict ad-hoc: lo que sale de M4 son los tipos de modelos.py."""
    Q, D, S = 1.0, 0.90, 0.005
    critico = tirante_critico(Q, D)

    assert isinstance(critico, TiranteCritico)
    assert isinstance(critico.geometria, type(geometria(D, 1.0)))
    assert isinstance(control_entrada(Q=Q, D=D, S=S, hds5=hds5).regimen,
                      RegimenEntrada)


# ===========================================================================
# C09 / SIS-F-10 - las tres guardas de M4 que no ejecutaba nadie
# ===========================================================================
#
# Las tres salen por vias distintas de la taxonomia, y esa distincion es
# justamente lo que ningun test fijaba:
#
#   tirante_critico          DatoInvalidoError sobre 'Q'      -- el dato
#   _exigir_hw_no_negativo   DisenoNoFactibleError            -- la combinacion
#   _geometria_de_referencia DatoInvalidoError sobre el criterio
#
# Que la segunda sea DisenoNoFactibleError y no DatoInvalidoError esta
# razonado en el docstring de `_exigir_hw_no_negativo` (MAT-D10): con esa Q,
# esa D y esa S ningun dato esta mal -- lo que no se sostiene es la
# combinacion --, y una pendiente medida en campo no se "corrige".


def test_un_caudal_que_no_deja_residuo_critico_se_detiene_en_Q():
    """
    `tirante_critico` declara en su docstring que el residuo cambia de signo
    "para un Q y un D de proyecto", y deja la guarda explicita para que un
    caso degenerado salga como ErrorProyecto y no como el ValueError de
    `brentq`, que la GUI no sabria clasificar.

    El caso degenerado es un caudal tan pequeño que el area del extremo
    inferior del intervalo se cancela en doble precision y el residuo llega a
    cero exacto. Falla si alguien retira la guarda confiando en que brentq
    "siempre encuentra raiz": entonces esta llamada saldria como ValueError
    -- fallo de programa -- por un dato del expediente.
    """
    Q_degenerado = 1e-200        # m3/s; M0 solo exige Q > 0
    with pytest.raises(DatoInvalidoError) as exc:
        tirante_critico(Q=Q_degenerado, D=CP6_TIRANTE_CRITICO["D"])

    assert exc.value.campo == "Q"
    assert exc.value.valor == pytest.approx(Q_degenerado, rel=REL_TRANSPORTE)
    assert "no cambia de signo" in exc.value.motivo
    assert NUMERAL_CRITICO in exc.value.motivo


@pytest.mark.parametrize("Q", CP6_TIRANTE_CRITICO["Q_casos"])
def test_ningun_caudal_de_proyecto_llega_a_esa_guarda(Q):
    """
    La otra mitad del test anterior, y la que sostiene lo que el docstring de
    `tirante_critico` afirma: con los caudales de CP-6 la guarda no se
    dispara y el solver entrega tirante. Falla si la condicion del `if` se
    invierte o se endurece y empieza a rechazar caudales normales.
    """
    assert tirante_critico(Q=Q, D=CP6_TIRANTE_CRITICO["D"]).y_c > 0


@pytest.mark.parametrize("Q, D", [
    (0.05, 2.40),      # q* muy bajo: el termino de la carta casi no aporta
    (0.30, 2.40),
    (0.05, 1.20),
])
def test_la_correccion_por_pendiente_no_puede_dejar_la_carga_bajo_cero(
        hds5, Q, D):
    """
    MAT-D10. HWi/D = H_c/D + K*(q*)^M + Ks*S con Ks = -0.5 (sin inglete): con
    un q* chico y una pendiente fuerte, el termino Ks*S se come a los otros
    dos y la carta devuelve una carga a la entrada negativa, que no existe.

    Sec. 4.2 no acota ese termino y ni la hoja de ruta ni el HDS-5 fijan un
    piso, de modo que adoptar uno aqui seria rellenar un vacio en silencio.
    Falla si alguien "arregla" el numero con un max(0, ...) o con un piso
    inventado: entonces esta llamada devolveria un HW publicable que no lo es.

    La pendiente del caso esta DENTRO del dominio fisico del dato (se
    comprueba contra `dominios.S_CAUCE_MAX`, no contra un numero escrito
    aqui): el punto de la ficha es justamente que ningun dato esta mal.
    """
    S = 0.40                      # m/m
    assert 0 < S < S_CAUCE_MAX, "el caso dejo de ser una pendiente posible"

    with pytest.raises(DisenoNoFactibleError) as exc:
        control_entrada(Q=Q, D=D, S=S, hds5=hds5)

    motivo = str(exc.value)
    assert NUMERAL_ENTRADA in motivo
    # El motivo tiene que nombrar el termino culpable y su constante: sin eso
    # el revisor no sabe que lo que fallo fue la correccion por pendiente.
    assert "Ks" in motivo and str(hds5.Ks) in motivo
    assert "negativa" in motivo
    # Y los tres numeros con que se reproduce el caso.
    assert f"D={D}" in motivo and f"S={S}" in motivo


def test_con_la_misma_D_y_una_pendiente_corriente_la_carta_si_entrega_carga(hds5):
    """
    El contraste del test anterior: lo que no se sostiene es la COMBINACION,
    no la D ni el Q. Falla si la guarda se endurece y empieza a rechazar
    pendientes normales de alcantarilla.
    """
    entrada = control_entrada(Q=0.05, D=2.40, S=0.005, hds5=hds5)
    assert entrada.HW_sobre_D > 0
    assert entrada.HW > 0


@pytest.mark.parametrize("seleccion", [
    "barril_parcialmente_lleno",
    "seccion_llena_hasta_y_normal",
    "",
])
def test_una_seccion_de_referencia_distinta_de_la_llena_se_detiene(seleccion):
    """
    Sec. 4.3 se evalua sobre la seccion que elige 'geometria_control_salida'
    [C], y M4 solo implementa la seccion llena. Falla si alguien declara otra
    seleccion y M4 la ignora en silencio: el HW de control de salida saldria
    calculado con la seccion llena mientras la memoria declara otra cosa --
    el caso en que el numero y su justificacion dejan de corresponderse.

    Es DatoInvalidoError sobre el nombre del criterio, no CriterioPendiente:
    el criterio esta declarado, lo que no existe es el procedimiento.
    """
    ca.establecer_valor_dinamico(CRITERIO_GEOMETRIA_SALIDA, seleccion)
    try:
        with pytest.raises(DatoInvalidoError) as exc:
            control_salida(Q=1.0, D=0.90, S=0.005, L=20.0, TW=0.0, n=0.013)
    finally:
        ca.quitar_valor_dinamico(CRITERIO_GEOMETRIA_SALIDA)

    assert exc.value.campo == CRITERIO_GEOMETRIA_SALIDA
    assert exc.value.valor == seleccion
    assert "seccion llena" in exc.value.motivo
    # Y dice que haria falta para implementar la otra, que es lo que separa
    # "corregi el valor" de "hay que programar un procedimiento".
    assert "HDS-5" in exc.value.motivo


# ---------------------------------------------------------------------------
# SIS-G-02 y MAT-O18 - los dos extremos del caudal que la aritmetica no lleva
# ---------------------------------------------------------------------------

def test_un_caudal_diminuto_anula_el_area_despues_del_solver():
    """
    SIS-G-02. La guarda que ya existia protege el BRACKET de Brent; esta
    protege la division de DESPUES.

    Son dos cosas distintas y hasta S16.5 solo estaba la primera: con
    Q = 1e-33 y D = 0.90 m el residuo cruza el cero limpiamente, brentq
    converge sin quejarse, y el theta al que converge cae por debajo del
    umbral en que el area se cancela. `V_c = Q / geom.A` era entonces un
    `ZeroDivisionError` en crudo -- fuera de ErrorProyecto, de modo que la GUI
    no sabia si era problema del expediente o fallo del programa.

    EL UMBRAL ESTA MEDIDO, no supuesto: A = (D^2/8)(theta - sen theta) vale
    exactamente 0.0 desde theta <= 2.149e-08, porque theta - sen(theta) ~
    theta^3/6 cae bajo el ultimo bit de theta. Q = 1e-32 todavia da
    theta = 2.979e-08 y area positiva; Q = 1e-33 ya no.

    `Q_m3s` solo exige ser positivo y no se le puede poner un piso sin
    inventar un valor de proyecto, que es la misma razon por la que SIS-G-01
    no acota las cotas.
    """
    # El ultimo caudal que SI resuelve: la guarda no puede empezar antes.
    assert tirante_critico(1e-32, 0.90).geometria.A > 0

    with pytest.raises(LimiteNumericoError) as exc:
        tirante_critico(1e-33, 0.90)
    assert exc.value.campo == "Q"
    # El mensaje nombra el PAR, no solo Q: la degeneracion es de la
    # combinacion (Q, D), igual que en MAT-D13 lo es la de (R, n).
    assert "D = 0.9" in str(exc.value)


def test_un_caudal_enorme_no_revienta_con_overflow_crudo():
    """
    MAT-O18, la mitad que SI era alcanzable, remedida.

    Su ficha situaba el desborde en `q*^2` y lo clasificaba "solo alcanzable
    inyectando". LAS DOS COSAS SON FALSAS: esta en `Q ** 2` de
    `_residuo_critico`, y `Q_m3s` no tiene techo en dominios.py, de modo que
    un caudal de 1e155 llega entero desde un CSV que pasa las tres
    validaciones de M0. Es la tercera correccion a esa ficha; S16 ya habia
    encontrado dos.

    `float.__pow__` lanza OverflowError donde `Q * Q` daria `inf`, asi que el
    sintoma era una excepcion cruda y no un numero falso. Se traduce a la
    taxonomia en vez de reescribir la potencia: el numero no existe de las dos
    formas, y lo que hay que corregir es el dato.
    """
    material = catalogo(TipoMaterial.CONCRETO_REFORZADO)

    # Por debajo del umbral gobierna la guarda de bracket, que ya existia y
    # sigue siendo la respuesta correcta: no hay raiz que buscar.
    with pytest.raises(DatoInvalidoError):
        control_entrada(Q=1e154, D=0.90, S=0.006, hds5=material.hds5)

    with pytest.raises(LimiteNumericoError) as exc:
        control_entrada(Q=1e155, D=0.90, S=0.006, hds5=material.hds5)
    assert exc.value.campo == "Q"
    assert "Q^2" in str(exc.value)


def test_los_dos_extremos_son_errores_de_proyecto_no_crashes():
    """
    Lo que la clase nueva compra: la GUI atrapa los dos con el mismo `except
    ErrorProyecto` con que atrapa un CBR de 250 %. Antes uno era
    ZeroDivisionError y el otro OverflowError, y ninguno de los dos lo era.
    """
    material = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    with pytest.raises(ErrorProyecto):
        tirante_critico(1e-33, 0.90)
    with pytest.raises(ErrorProyecto):
        control_entrada(Q=1e155, D=0.90, S=0.006, hds5=material.hds5)


def test_el_caudal_de_proyecto_no_toca_ninguna_de_las_dos_guardas():
    """El trinquete: con datos reales las dos guardas son invisibles."""
    for Q in CP6_TIRANTE_CRITICO["Q_casos"]:
        critico = tirante_critico(Q, CP6_TIRANTE_CRITICO["D"])
        assert critico.geometria.A > 0
        assert math.isfinite(critico.V)
        assert math.isfinite(critico.H_c)


# ---------------------------------------------------------------------------
# SIS-B-18: la rama de h_o llega a la memoria, y no solo al booleano
# ---------------------------------------------------------------------------

def test_la_rama_de_ho_que_goberno_sale_escrita_en_la_memoria(concreto):
    """
    `ahogado_por_TW` era, segun SIS-B-18, el unico de cinco campos escritos y
    nunca leidos que ademas «no se emite ni al JSON ni al HTML»: una rama que
    el codigo distinguia y el revisor no veia. Dejo de serlo en S18, cuando
    `_pasos_hidraulicos` empezo a leerlo para redactar la procedencia de h_o.

    Los dos tests de arriba asertan el BOOLEANO; este aserta el TEXTO que sale
    impreso, que es lo que el revisor lee. Sin el, el campo asoma al
    entregable por una sola frase y nada la protege --- que es la forma exacta
    del precedente `FACTOR_MURO_TABLA` que CLAUDE.md registra: un test verde
    sobre el comentario en vez de sobre el hecho.
    """
    from modulos.M11_reporte import bloque_pasos

    c = CP2_GEOMETRIA_MANNING
    def _memoria(TW):
        r = resolver_control(D=c["D"], Q=c["Q_con_n_max_esperado"], S=c["S"],
                             L=20.0, TW=TW, material=concreto)
        return bloque_pasos(r.pasos, "Fases 3 y 4")

    ahogada = _memoria(2.50)
    libre = _memoria(0.0)

    assert "manda TW: la salida esta ahogada" in ahogada
    assert "manda la aproximacion geometrica" not in ahogada
    assert "manda la aproximacion geometrica" in libre
    assert "manda TW: la salida esta ahogada" not in libre
