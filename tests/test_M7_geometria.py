"""
tests/test_M7_geometria.py
===========================
M7 contra las dos piezas de la Fase 7:

    7.A   la cota de rasante minima es el MAXIMO de las dos condiciones, y
          cada una gobierna donde debe. El delta sale en centimetros y el
          "no factible" no es una excepcion generica: es un resultado con
          numero, y la excepcion opcional es DisenoNoFactibleError con el
          delta dentro.
    7.B   longitud, esviaje, pendiente y cotas, con G1 (rasante congelada) y
          G2 (cota de salida sobre el fondo del receptor). Se detiene en
          'talud_terraplen' mientras ese criterio siga vacio.

Coherencia con V4 (M5): la segunda condicion de 7.A es la misma desigualdad
de V4 despejada en la rasante. El test que lo comprueba es el corazon del
corte del acoplamiento circular: con la rasante puesta EXACTAMENTE en la
minima de 7.A, V4 tiene que cumplir al limite.
"""

import math

import pytest

import criterios_adoptados as ca
from constantes_normativas import H_RELLENO_MIN
from modelos import (CondicionRasante, ControlGobernante, CriterioPendienteError,
                     DatoInvalidoError, DisenoNoFactibleError, Familia,
                     PuntoCritico, ResultadoHidraulico, TipoMaterial)
from modulos.M2_material import catalogo
from modulos.M5_verificaciones import v4_carga_entrada
from modulos.M7_geometria import (CRITERIO_TALUD, altura_recubrimiento,
                                  criterio_recubrimiento,
                                  altura_terraplen, compatibilidad_geometrica,
                                  cota_clave, cota_salida, espesor_paquete,
                                  factor_esviaje, g1_rasante_congelada,
                                  g2_cota_salida, longitud_conducto,
                                  proyeccion_taludes, tamizado_rasante)

# El HDPE es el unico material cuyo h_rec es [N] (0.30 m, EG-2013
# 508.07/508.08): con concreto o TMC, 7.A se detiene en el vacio
# 'h_relleno_min_concreto_tmc' y no hay tamizado que probar.
H_REC_HDPE = H_RELLENO_MIN["hdpe"]


def _punto(**cambios) -> PuntoCritico:
    base = dict(
        id="A-01",
        progresiva_km=0.380,
        progresiva_display="0+380",
        familia=Familia.A,
        Q_m3s=1.1673,
        area_ha=850.0,
        S_cauce=0.006,
        cota_terreno=42.10,
        cota_rasante=44.20,
        cota_subrasante=44.05,
        cbr_subrasante=8.5,           # tramo 6-20 % -> resguardo 0.80 m
        esviaje_grados=0.0,
        ancho_plataforma=9.60,
        cota_fondo_receptor=41.30,
        Q_receptor_m3s=None,
        cota_TW=None,
        sucs_fundacion="SM",
        NF_profundidad_m=None,     # lo da el estudio geotecnico, por punto
    )
    base.update(cambios)
    return PuntoCritico(**base)


def _resultado(*, HW_entrada=0.50) -> ResultadoHidraulico:
    return ResultadoHidraulico(
        y_normal=0.60, y_critico=0.40, V=1.5, Q=1.0,
        HW_entrada=HW_entrada, HW_salida=0.20,
        control_gobernante=ControlGobernante.ENTRADA,
    )


@pytest.fixture
def hdpe():
    return catalogo(TipoMaterial.HDPE)


@pytest.fixture
def concreto():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO)


# ---------------------------------------------------------------------------
# Piezas de 7.A
# ---------------------------------------------------------------------------

def test_espesor_paquete_es_la_diferencia_rasante_subrasante():
    punto = _punto(cota_rasante=44.20, cota_subrasante=44.05)
    assert espesor_paquete(punto) == pytest.approx(0.15)


def test_espesor_paquete_invertido_es_dato_invalido():
    """Sec. 1.5: la subrasante va BAJO la rasante. M0 lo exige; M7 tambien."""
    punto = _punto(cota_rasante=44.00, cota_subrasante=44.05)
    with pytest.raises(DatoInvalidoError) as exc:
        espesor_paquete(punto)
    assert exc.value.campo == "cota_subrasante"


def test_cota_clave_es_la_entrada_mas_el_diametro():
    punto = _punto(cota_terreno=42.10)
    assert cota_clave(punto=punto, D=1.50) == pytest.approx(43.60)


def test_h_recubrimiento_del_hdpe_es_el_valor_N_de_eg2013(hdpe):
    assert altura_recubrimiento(hdpe) == pytest.approx(H_REC_HDPE)


def test_h_recubrimiento_de_concreto_es_el_0_30_adoptado_por_analogia(concreto):
    """
    EG-2013 no fija h_rec para concreto ni TMC -- vacio VERIFICADO, Sec. 14.a
    del manifiesto. Se adopta el 0.30 m que 508.07 si fija para HDPE, por
    analogia [N->] y a nivel de perfil: el HDPE es el material con menor
    tolerancia a cobertura reducida, de modo que exigir su recubrimiento al
    concreto y al TMC no queda del lado inseguro.

    Antes esto lanzaba CriterioPendienteError y dejaba al HDPE como unico
    material capaz de completar diseno, que no era un resultado de ingenieria
    sino el efecto de un vacio documental.
    """
    assert altura_recubrimiento(concreto) == pytest.approx(0.30)
    assert altura_recubrimiento(concreto) == pytest.approx(H_REC_HDPE)


def test_el_recubrimiento_adoptado_declara_su_procedencia_en_la_verificacion(concreto, hdpe):
    """
    Los dos materiales usan el mismo numero pero NO por la misma razon, y la
    memoria tiene que poder distinguirlo: en HDPE es [N] leido de 508.07, en
    concreto es la analogia [N->]. `criterio_recubrimiento` es lo que lleva
    esa diferencia a la Verificacion de 7.B.
    """
    assert criterio_recubrimiento(hdpe) is None                 # [N] puro
    assert criterio_recubrimiento(concreto) == "h_relleno_min_concreto_tmc"


# ---------------------------------------------------------------------------
# 7.A - el maximo de las dos condiciones
# ---------------------------------------------------------------------------

def test_tamizado_toma_el_maximo_y_reporta_las_dos_condiciones(hdpe):
    """
    cota clave      = 42.10 + 1.50 = 43.60
    e_paq           = 44.20 - 44.05 = 0.15
    resguardo(8.5)  = 0.80 (tramo 6-20 %)

    por recubrimiento: 43.60 + 0.30 + 0.15 = 44.05
    por resguardo    : 42.10 + 0.50 + 0.80 + 0.15 = 43.55
    """
    punto = _punto()
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=0.50)

    assert t.cota_por_recubrimiento == pytest.approx(44.05)
    assert t.cota_por_resguardo == pytest.approx(43.55)
    assert t.cota_rasante_min == pytest.approx(44.05)
    assert t.condicion_gobernante is CondicionRasante.RECUBRIMIENTO
    assert t.resguardo == pytest.approx(0.80)
    assert t.espesor_paquete == pytest.approx(0.15)


def test_un_HW_alto_hace_gobernar_el_resguardo(hdpe):
    """
    Con HW = 1.20: por resguardo = 42.10 + 1.20 + 0.80 + 0.15 = 44.25, que
    supera los 44.05 del recubrimiento. Cambia la condicion gobernante y con
    ella la variable que hay que mover.
    """
    punto = _punto()
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=1.20)

    assert t.condicion_gobernante is CondicionRasante.RESGUARDO
    assert t.cota_rasante_min == pytest.approx(44.25)
    assert t.criterio_gobernante == "resguardo_HW_subrasante"


def test_en_empate_gobierna_el_recubrimiento(hdpe):
    """
    HW elegido para que las dos condiciones den 44.05 exactos:
    42.10 + HW + 0.80 + 0.15 = 44.05 -> HW = 1.00. Se declara gobernante el
    recubrimiento, que es el que no depende del calculo hidraulico.
    """
    punto = _punto()
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=1.00)

    assert t.cota_por_recubrimiento == pytest.approx(t.cota_por_resguardo)
    assert t.condicion_gobernante is CondicionRasante.RECUBRIMIENTO


def test_el_criterio_del_recubrimiento_es_None_en_hdpe_y_la_clave_en_concreto(hdpe):
    """El 0.30 m del HDPE es [N] puro: no hay criterio adoptado que citar."""
    t = tamizado_rasante(punto=_punto(), material=hdpe, D_supuesto=1.50, HW=0.50)
    assert t.criterio_recubrimiento is None
    assert t.criterio_gobernante is None          # gobierna el recubrimiento
    assert t.criterio_resguardo == "resguardo_HW_subrasante"


# ---------------------------------------------------------------------------
# El delta de rasante: en centimetros y sin excepcion generica
# ---------------------------------------------------------------------------

def test_rasante_suficiente_da_delta_cero_y_factible(hdpe):
    punto = _punto(cota_rasante=44.50, cota_subrasante=44.35)
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=0.50)

    assert t.factible
    assert t.delta_rasante_m == pytest.approx(0.0)
    assert t.delta_rasante_cm == pytest.approx(0.0)
    assert "factible" in t.mensaje
    t.exigir_factible()                            # no lanza


def test_rasante_insuficiente_devuelve_el_delta_en_cm_sin_lanzar(hdpe):
    """
    Sec. 7.B: "el chequeo devuelve 'no factible -> subir rasante X cm', nunca
    un resultado silencioso". Devuelve: no lanza.

    Con la rasante en 43.85 y minima 44.05 -> faltan 0.20 m = 20 cm.
    """
    punto = _punto(cota_rasante=43.85, cota_subrasante=43.70)
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=0.50)

    assert not t.factible
    assert t.delta_rasante_m == pytest.approx(0.20)
    assert t.delta_rasante_cm == pytest.approx(20.0)
    assert "no factible" in t.mensaje
    assert "20.0 cm" in t.mensaje


def test_la_excepcion_del_no_factible_es_de_la_taxonomia_y_lleva_el_delta(hdpe):
    """Nunca una excepcion generica: DisenoNoFactibleError con delta_rasante_m."""
    punto = _punto(cota_rasante=43.85, cota_subrasante=43.70)
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=0.50)

    with pytest.raises(DisenoNoFactibleError) as exc:
        t.exigir_factible()

    assert exc.value.delta_rasante_m == pytest.approx(0.20)
    assert exc.value.id_punto == "A-01"
    assert "subir rasante 20.0 cm" in str(exc.value)


def test_g1_reproduce_el_veredicto_del_tamizado(hdpe):
    punto = _punto(cota_rasante=43.85, cota_subrasante=43.70)
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=0.50)
    v = g1_rasante_congelada(t)

    assert v.codigo == "G1"
    assert not v.cumple
    assert v.valor_obtenido == pytest.approx(43.85)
    assert v.valor_admisible == pytest.approx(44.05)


# ---------------------------------------------------------------------------
# El corte del acoplamiento circular: 7.A y V4 son la misma desigualdad
# ---------------------------------------------------------------------------

def test_la_rasante_minima_de_7A_hace_cumplir_V4_al_limite(hdpe):
    """
    Corazon del corte declarado en Sec. 7.B. La condicion de resguardo de 7.A
    es V4 despejada en la rasante:

        HW <= (cota rasante - e_paq) - resguardo
        cota rasante >= HW + resguardo + e_paq

    Se pone la rasante EXACTAMENTE en la minima que devuelve el tamizado (con
    el HW gobernando) y se comprueba que V4 cumple, al limite y sin holgura.
    """
    HW = 1.20                                   # gobierna el resguardo
    e_paq = 0.15
    base = _punto()
    t = tamizado_rasante(punto=base, material=hdpe, D_supuesto=1.50, HW=HW)
    assert t.condicion_gobernante is CondicionRasante.RESGUARDO

    congelado = _punto(cota_rasante=t.cota_rasante_min,
                       cota_subrasante=t.cota_rasante_min - e_paq)
    v4 = v4_carga_entrada(punto=congelado, resultado=_resultado(HW_entrada=HW))

    assert v4.cumple
    # Al limite: el HW en cota coincide con el admisible de V4.
    assert v4.valor_obtenido == pytest.approx(v4.valor_admisible)


def test_un_centimetro_menos_de_rasante_rompe_V4(hdpe):
    """La otra mitad del mismo hecho: bajo la minima de 7.A, V4 no cumple."""
    HW = 1.20
    e_paq = 0.15
    t = tamizado_rasante(punto=_punto(), material=hdpe, D_supuesto=1.50, HW=HW)

    rasante = t.cota_rasante_min - 0.01
    punto = _punto(cota_rasante=rasante, cota_subrasante=rasante - e_paq)
    v4 = v4_carga_entrada(punto=punto, resultado=_resultado(HW_entrada=HW))

    assert not v4.cumple


def test_el_paquete_no_cambia_la_condicion_de_resguardo_solo_la_traslada(hdpe):
    """
    Por que el lazo se corta de una pasada: e_paq entra en la rasante minima
    con pendiente 1. Duplicarlo sube la rasante minima exactamente lo mismo,
    sin realimentar nada -- no hay que iterar.
    """
    delgado = _punto(cota_rasante=44.20, cota_subrasante=44.05)     # e_paq 0.15
    grueso = _punto(cota_rasante=44.50, cota_subrasante=44.20)      # e_paq 0.30

    t1 = tamizado_rasante(punto=delgado, material=hdpe, D_supuesto=1.50, HW=1.20)
    t2 = tamizado_rasante(punto=grueso, material=hdpe, D_supuesto=1.50, HW=1.20)

    assert t2.cota_por_resguardo - t1.cota_por_resguardo == pytest.approx(0.15)


def test_un_diametro_menor_sube_el_resguardo_relativo_al_recubrimiento(hdpe):
    """
    La ADVERTENCIA del docstring: el D maximo no es conservador para las dos
    condiciones. Bajar el diametro baja la clave (y con ella la condicion de
    recubrimiento) pero deja intacta la de resguardo, que solo depende del HW
    -- y en la realidad ese HW SUBE con el diametro menor. Por eso 7.B se
    corre otra vez con el diametro adoptado.
    """
    punto = _punto()
    grande = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=0.50)
    chico = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=0.90, HW=0.50)

    assert chico.cota_por_recubrimiento < grande.cota_por_recubrimiento
    assert chico.cota_por_resguardo == pytest.approx(grande.cota_por_resguardo)


# ---------------------------------------------------------------------------
# Piezas de 7.B
# ---------------------------------------------------------------------------

def test_esviaje_cero_no_alarga_el_conducto():
    assert factor_esviaje(_punto(esviaje_grados=0.0)) == pytest.approx(1.0)


def test_el_esviaje_alarga_por_el_inverso_del_coseno():
    punto = _punto(esviaje_grados=30.0)
    assert factor_esviaje(punto) == pytest.approx(1.0 / math.cos(math.radians(30.0)))


def test_esviaje_de_90_grados_no_define_longitud():
    punto = _punto(esviaje_grados=90.0)
    with pytest.raises(DatoInvalidoError) as exc:
        factor_esviaje(punto)
    assert exc.value.campo == "esviaje_grados"


def test_altura_de_terraplen_no_es_la_altura_de_relleno():
    """cota rasante - cota terreno, el brazo vertical del talud."""
    punto = _punto(cota_rasante=44.20, cota_terreno=42.10)
    assert altura_terraplen(punto) == pytest.approx(2.10)


def test_la_proyeccion_de_taludes_se_detiene_en_el_criterio_vacio():
    """
    Sec. 7.B pide sumarla pero no da la inclinacion del talud, y Sec. 1.2 no
    la trae como columna: el vacio se declara y detiene, no se rellena con un
    1.5:1 de practica corriente.
    """
    with pytest.raises(CriterioPendienteError) as exc:
        proyeccion_taludes(_punto())
    assert exc.value.clave == CRITERIO_TALUD

    with pytest.raises(CriterioPendienteError):
        longitud_conducto(_punto())


def test_el_criterio_del_talud_sigue_declarado_sin_valor():
    """Si algun dia recibe valor, este test cae y hay que revisar 7.B entera."""
    assert CRITERIO_TALUD in ca.criterios_sin_valor()
    assert ca.criterio(CRITERIO_TALUD).etiqueta == "A"


def test_cota_de_salida_es_la_entrada_menos_la_caida():
    punto = _punto(cota_terreno=42.10)
    assert cota_salida(punto=punto, longitud=20.0, S=0.006) == pytest.approx(41.98)


def test_g2_cumple_cuando_la_salida_queda_sobre_el_fondo_del_receptor():
    punto = _punto(cota_fondo_receptor=41.30)
    assert g2_cota_salida(punto=punto, cota_salida_m=41.98).cumple


def test_g2_incumple_cuando_la_salida_queda_bajo_el_receptor():
    punto = _punto(cota_fondo_receptor=41.30)
    v = g2_cota_salida(punto=punto, cota_salida_m=41.10)
    assert not v.cumple
    assert v.codigo == "G2"
    assert v.criterio_aplicado is None          # compara dos cotas, sin criterio


# ---------------------------------------------------------------------------
# 7.B completa
# ---------------------------------------------------------------------------

def test_7B_se_detiene_en_el_talud_si_no_se_le_pasa_la_longitud(hdpe):
    with pytest.raises(CriterioPendienteError) as exc:
        compatibilidad_geometrica(punto=_punto(), material=hdpe, D=1.50,
                                  resultado=_resultado())
    assert exc.value.clave == CRITERIO_TALUD


def test_7B_con_longitud_dada_arma_la_geometria_y_las_dos_verificaciones(hdpe):
    punto = _punto(cota_rasante=44.50, cota_subrasante=44.35)
    geo = compatibilidad_geometrica(punto=punto, material=hdpe, D=1.50,
                                    resultado=_resultado(), longitud=20.0)

    assert [v.codigo for v in geo.verificaciones] == ["G1", "G2"]
    assert geo.factible
    assert geo.S_conducto == pytest.approx(punto.S_cauce)
    assert geo.caida == pytest.approx(0.006 * 20.0)
    assert geo.cota_salida == pytest.approx(41.98)
    assert geo.delta_rasante_cm == pytest.approx(0.0)
    geo.exigir_factible()                       # no lanza


def test_7B_no_factible_por_rasante_devuelve_el_delta_y_lo_lleva_a_la_excepcion(hdpe):
    """
    El caso que motiva toda la Fase 7: el diametro adoptado no cabe bajo la
    rasante congelada. Devuelve resultado con el delta; la excepcion, si se
    pide, es DisenoNoFactibleError con ese delta -- nunca generica.
    """
    punto = _punto(cota_rasante=43.85, cota_subrasante=43.70)
    geo = compatibilidad_geometrica(punto=punto, material=hdpe, D=1.50,
                                    resultado=_resultado(), longitud=20.0)

    assert not geo.factible
    assert geo.delta_rasante_cm == pytest.approx(20.0)

    with pytest.raises(DisenoNoFactibleError) as exc:
        geo.exigir_factible()
    assert exc.value.delta_rasante_m == pytest.approx(0.20)


def test_7B_no_factible_por_cota_de_salida_no_lleva_delta_de_rasante(hdpe):
    """
    Subir la rasante no arregla una salida bajo el fondo del receptor: se
    corrige con la pendiente, la longitud o la cota del receptor. La
    excepcion sale sin delta, y eso es informacion, no una omision.
    """
    punto = _punto(cota_rasante=44.50, cota_subrasante=44.35,
                   cota_fondo_receptor=42.05)
    geo = compatibilidad_geometrica(punto=punto, material=hdpe, D=1.50,
                                    resultado=_resultado(), longitud=20.0)

    assert geo.tamizado.factible
    assert not geo.factible
    assert [v.codigo for v in geo.verificaciones_incumplidas] == ["G2"]

    with pytest.raises(DisenoNoFactibleError) as exc:
        geo.exigir_factible()
    assert exc.value.delta_rasante_m is None


def test_7B_deduce_la_proyeccion_de_la_longitud_que_se_le_pasa(hdpe):
    """
    Con longitud dada, la proyeccion es la que ESA longitud implica: no un
    calculo independiente. Con esviaje 0 y plataforma 9.60, una longitud de
    20.0 m implica 10.40 m de taludes.
    """
    geo = compatibilidad_geometrica(punto=_punto(), material=hdpe, D=1.50,
                                    resultado=_resultado(), longitud=20.0)
    assert geo.proyeccion_taludes == pytest.approx(10.40)
    assert geo.factor_esviaje == pytest.approx(1.0)
