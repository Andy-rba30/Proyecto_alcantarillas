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
from pathlib import Path

import pytest

import criterios_adoptados as ca
from constantes_normativas import H_RELLENO_MIN
from dominios import ESVIAJE_MAX
from modelos import (CondicionRasante, ControlGobernante, CriterioPendienteError,
                     DatoInvalidoError, DisenoNoFactibleError, ErrorProyecto,
                     Familia, LimiteNumericoError, PuntoCritico,
                     ResultadoHidraulico, TipoMaterial)
from modulos.M0_carga import cargar_puntos
from modulos.M2_material import catalogo
from tolerancias import TOL_UMBRAL_NORMATIVO
from modulos.M5_verificaciones import v4_carga_entrada
from modulos.M7_geometria import (CRITERIO_COBERTURA_AASHTO,
                                  CRITERIO_CONDICION_PAVIMENTO,
                                  CRITERIO_TALUD, altura_recubrimiento,
                                  criterio_recubrimiento,
                                  altura_terraplen, cobertura_minima_aashto,
                                  compatibilidad_geometrica,
                                  cota_clave, cota_salida, espesor_paquete,
                                  factor_esviaje, g1_rasante_congelada,
                                  g2_cota_salida, longitud_conducto,
                                  proyeccion_taludes, tamizado_rasante)
from tests.fixtures.casos_patron import CP9_GEOMETRIA_7B
from tests.apoyo.aproximacion import REL_TRANSPORTE

# El HDPE es el unico material con minimo de relleno en EG-2013 (0.30 m,
# Subseccion 508.07, pag. 984). Ya NO es el h_rec del tamizado: desde C01,
# h_rec es el MAYOR entre ese minimo y la cobertura minima de la Tabla
# 12.6.6.3-1 de AASHTO LRFD, y en HDPE bajo pavimento la tabla pide ID/2 >=
# 24 in -- 0.75 m para D = 1.50 m --, muy por encima de los 0.30.
#
# Los tres materiales corren ahora el tamizado: no queda ninguno bloqueado por
# un vacio de recubrimiento. Los que bloquean 7.A son otros dos, y la corrida
# de pruebas los declara en conftest.py: 'espesor_pared_conducto' y
# 'condicion_pavimento' (esta ultima, "flexible").
H_REC_EG2013_HDPE = H_RELLENO_MIN["hdpe"]

# Valores de la corrida de pruebas, recalculados a mano para el HDPE de los
# tests (D = 1.50 m interior, t = 0.05 m, condicion "flexible"):
#
#   cobertura AASHTO = max(ID/2, 24 in) = max(0.75, 0.6096) = 0.75 m
#   h_rec            = max(0.30 de EG-2013, 0.75) = 0.75 m
#   cota clave       = cota_terreno + D + t = 42.10 + 1.50 + 0.05 = 43.65
H_REC_HDPE = 0.75
COTA_CLAVE_HDPE = 43.65


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


def _resultado(*, HW_entrada=0.50, S=0.006) -> ResultadoHidraulico:
    """
    `S` es la pendiente con que corrio el diseño y la que 7.B usa: por defecto
    la misma que `_punto()` trae en `S_cauce`, que es el caso normal (nadie
    declaro otra). Se puede pasar distinta para el punto que si la declara.
    """
    return ResultadoHidraulico(
        y_normal=0.60, y_critico=0.40,
        V_erosion=1.5, V_sedimentacion=1.2, Q=1.0, S=S,
        HW_entrada=HW_entrada, HW_salida=0.20,
        control_gobernante=ControlGobernante.ENTRADA,
    )



@pytest.fixture
def declarar_condicion_pavimento():
    """
    Declara 'condicion_pavimento' por la via de la GUI y repone al salir la
    que trae la corrida de pruebas (conftest.py). Se lee y se repone el valor
    VIGENTE, no uno escrito aqui: si conftest cambia de fila, estos tests la
    siguen sin editarse.
    """
    original = ca.valor(CRITERIO_CONDICION_PAVIMENTO)

    def _declarar(condicion):
        ca.establecer_valor_dinamico(CRITERIO_CONDICION_PAVIMENTO, condicion)

    yield _declarar
    ca.establecer_valor_dinamico(CRITERIO_CONDICION_PAVIMENTO, original)


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


def test_cota_clave_llega_a_la_superficie_exterior_del_tubo(hdpe):
    """
    MAT-D4: la clave es la FISICA -- la generatriz exterior superior --, que
    es desde donde EG-2013 508.07 mide el relleno. 42.10 + 1.50 + 0.05 =
    43.65, no 43.60.

    El espesor entra UNA vez, no dos: la cota de entrada es el invert
    INTERIOR, de modo que la generatriz exterior superior queda a D_int + t
    sobre ella. Sumar D_ext (42.10 + 1.60 = 43.70) seria contar el espesor
    del fondo, que esta por DEBAJO del invert.
    """
    punto = _punto(cota_terreno=42.10)
    assert (cota_clave(punto=punto, material=hdpe, D=1.50)
            == pytest.approx(COTA_CLAVE_HDPE))


def test_h_recubrimiento_del_hdpe_lo_gobierna_la_tabla_de_aashto(hdpe):
    """
    NOR-VAC-01: el 0.30 m de EG-2013 no es el minimo aplicable. Bajo pavimento
    la Tabla 12.6.6.3-1 pide ID/2 >= 24 in para el termoplastico, y con
    D = 1.50 m eso son 0.75 m: 2.5 veces el valor que el proyecto usaba.
    """
    assert altura_recubrimiento(material=hdpe, D=1.50) == pytest.approx(0.75)
    assert altura_recubrimiento(material=hdpe, D=1.50) > H_REC_EG2013_HDPE


def test_h_recubrimiento_de_concreto_sale_de_la_tabla_y_no_de_una_analogia(concreto):
    """
    EG-2013 no fija h_rec para concreto ni TMC, y el vacio se cubria por
    analogia con el 0.30 m del HDPE. No era un vacio: la Tabla 12.6.6.3-1 lo
    tabula, y su piso -- 12.0 in = 0.3048 m -- ya deja el 0.30 m adoptado 5 mm
    corto (NOR-VAC-01).

    Con D = 1.50 m y t = 0.10 m: Bc = 1.70 m, Bc/8 = 0.2125 m y sqrt(Bc)/8 en
    pies son 0.0900 m, de modo que gobierna el piso de 0.3048 m.
    """
    h_rec = altura_recubrimiento(material=concreto, D=1.50)
    assert h_rec == pytest.approx(0.3048)
    assert h_rec > 0.30


def test_el_recubrimiento_declara_su_procedencia_en_la_verificacion(concreto, hdpe):
    """
    La tabla de AASHTO entra en los TRES materiales, de modo que en los tres
    hay un criterio [C] que declarar. Antes el HDPE devolvia None -- su 0.30 m
    se leia como [N] puro -- y los otros dos citaban la analogia retirada.
    """
    assert criterio_recubrimiento(hdpe) == "cobertura_minima_aashto"
    assert criterio_recubrimiento(concreto) == "cobertura_minima_aashto"


# ---------------------------------------------------------------------------
# 7.A - el maximo de las dos condiciones
# ---------------------------------------------------------------------------

def test_tamizado_toma_el_maximo_y_reporta_las_dos_condiciones(hdpe):
    """
    cota clave      = 42.10 + 1.50 + 0.05 = 43.65   (clave FISICA, MAT-D4)
    h_rec           = max(0.30 EG-2013, 0.75 AASHTO) = 0.75
    e_paq           = 44.20 - 44.05 = 0.15
    resguardo(8.5)  = 0.80 (tramo 6-20 %)

    por recubrimiento: 43.65 + 0.75 + 0.15 = 44.55
    por resguardo    : 42.10 + 0.50 + 0.80 + 0.15 = 43.55
    """
    punto = _punto()
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=0.50)

    assert t.cota_por_recubrimiento == pytest.approx(44.55)
    assert t.cota_por_resguardo == pytest.approx(43.55)
    assert t.cota_rasante_min == pytest.approx(44.55)
    assert t.condicion_gobernante is CondicionRasante.RECUBRIMIENTO
    assert t.resguardo == pytest.approx(0.80)
    assert t.espesor_paquete == pytest.approx(0.15)


def test_un_HW_alto_hace_gobernar_el_resguardo(hdpe):
    """
    Con HW = 1.70: por resguardo = 42.10 + 1.70 + 0.80 + 0.15 = 44.75, que
    supera los 44.55 del recubrimiento. Cambia la condicion gobernante y con
    ella la variable que hay que mover.

    El HW de este test subio de 1.20 a 1.70 por la correccion de C01: con la
    clave fisica y la cobertura de AASHTO, la condicion de recubrimiento es
    0.50 m mas alta y 1.20 ya no la supera.
    """
    punto = _punto()
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=1.70)

    assert t.condicion_gobernante is CondicionRasante.RESGUARDO
    assert t.cota_rasante_min == pytest.approx(44.75)
    assert t.criterio_gobernante == "resguardo_HW_subrasante"


def test_en_empate_gobierna_el_recubrimiento(hdpe):
    """
    HW elegido para que las dos condiciones den 44.55 exactos:
    42.10 + HW + 0.80 + 0.15 = 44.55 -> HW = 1.50. Se declara gobernante el
    recubrimiento, que es el que no depende del calculo hidraulico.
    """
    punto = _punto()
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=1.50)

    assert t.cota_por_recubrimiento == pytest.approx(t.cota_por_resguardo)
    assert t.condicion_gobernante is CondicionRasante.RECUBRIMIENTO


def test_el_tamizado_declara_de_donde_sale_cada_umbral(hdpe):
    """
    El recubrimiento del HDPE ya no es [N] puro: lo gobierna la Tabla
    12.6.6.3-1, que es [C]. El tamizado tiene que citarla, tambien cuando la
    condicion que manda es esa.
    """
    t = tamizado_rasante(punto=_punto(), material=hdpe, D_supuesto=1.50, HW=0.50)
    assert t.criterio_recubrimiento == "cobertura_minima_aashto"
    assert t.criterio_gobernante == "cobertura_minima_aashto"
    assert t.criterio_resguardo == "resguardo_HW_subrasante"
    # La geometria fisica viaja con el resultado, para que la memoria pueda
    # mostrar sobre que diametro se calculo la cobertura.
    assert t.espesor_pared == pytest.approx(0.05)
    assert t.D_exterior == pytest.approx(1.60)


# ---------------------------------------------------------------------------
# El delta de rasante: en centimetros y sin excepcion generica
# ---------------------------------------------------------------------------

def test_rasante_suficiente_da_delta_cero_y_factible(hdpe):
    punto = _punto(cota_rasante=45.00, cota_subrasante=44.85)
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

    Con la rasante en 44.35 y minima 44.55 -> faltan 0.20 m = 20 cm.
    """
    punto = _punto(cota_rasante=44.35, cota_subrasante=44.20)
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=0.50)

    assert not t.factible
    assert t.delta_rasante_m == pytest.approx(0.20)
    assert t.delta_rasante_cm == pytest.approx(20.0)
    assert "no factible" in t.mensaje
    assert "20.0 cm" in t.mensaje


def test_la_excepcion_del_no_factible_es_de_la_taxonomia_y_lleva_el_delta(hdpe):
    """Nunca una excepcion generica: DisenoNoFactibleError con delta_rasante_m."""
    punto = _punto(cota_rasante=44.35, cota_subrasante=44.20)
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=0.50)

    with pytest.raises(DisenoNoFactibleError) as exc:
        t.exigir_factible()

    assert exc.value.delta_rasante_m == pytest.approx(0.20)
    assert exc.value.id_punto == "A-01"
    assert "subir rasante 20.0 cm" in str(exc.value)


def test_g1_reproduce_el_veredicto_del_tamizado(hdpe):
    punto = _punto(cota_rasante=44.35, cota_subrasante=44.20)
    t = tamizado_rasante(punto=punto, material=hdpe, D_supuesto=1.50, HW=0.50)
    v = g1_rasante_congelada(t)

    assert v.codigo == "G1"
    assert not v.cumple
    assert v.valor_obtenido == pytest.approx(44.35)
    assert v.valor_admisible == pytest.approx(44.55)


# ---------------------------------------------------------------------------
# El corte del acoplamiento circular: 7.A y V4 son la misma desigualdad
# ---------------------------------------------------------------------------

def test_la_rasante_minima_de_7A_hace_cumplir_V4_al_limite(hdpe):
    """
    Corazon del corte declarado en Sec. 7.B. La condicion de resguardo de 7.A
    es V4 despejada en la rasante:

        cota entrada + HW <= (cota rasante - e_paq) - resguardo
        cota rasante >= cota entrada + HW + resguardo + e_paq

    Se pone la rasante EXACTAMENTE en la minima que devuelve el tamizado (con
    el HW gobernando) y se comprueba que V4 cumple, al limite y sin holgura.
    """
    HW = 1.70                                   # gobierna el resguardo
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
    HW = 1.70
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
    assert factor_esviaje(_punto(esviaje_grados=0.0)) == pytest.approx(
        1.0, rel=REL_TRANSPORTE)


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
    punto = _punto(cota_rasante=45.00, cota_subrasante=44.85)
    geo = compatibilidad_geometrica(punto=punto, material=hdpe, D=1.50,
                                    resultado=_resultado(), longitud=20.0)

    assert [v.codigo for v in geo.verificaciones] == ["G1", "G2"]
    assert geo.factible
    assert geo.S_conducto == pytest.approx(punto.S_cauce)
    assert geo.caida == pytest.approx(0.006 * 20.0)
    assert geo.cota_salida == pytest.approx(41.98)
    # None y no 0.0: la rasante alcanza, de modo que no hay delta que pedir
    # (ver `CompatibilidadGeometrica.delta_rasante_cm`).
    assert geo.delta_rasante_cm is None
    geo.exigir_factible()                       # no lanza


def test_7B_no_factible_por_rasante_devuelve_el_delta_y_lo_lleva_a_la_excepcion(hdpe):
    """
    El caso que motiva toda la Fase 7: el diametro adoptado no cabe bajo la
    rasante congelada. Devuelve resultado con el delta; la excepcion, si se
    pide, es DisenoNoFactibleError con ese delta -- nunca generica.
    """
    punto = _punto(cota_rasante=44.35, cota_subrasante=44.20)
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
    punto = _punto(cota_rasante=45.00, cota_subrasante=44.85,
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


# ===========================================================================
# C09 / SIS-F-10 y SIS-B-23 - la guarda de la fila de AASHTO, y la del esviaje
# ===========================================================================
#
# `cobertura_minima_aashto` elige fila de la Tabla 12.6.6.3-1 con
# 'condicion_pavimento' [A]. Que la condicion declarada no exista en la tabla
# no lo probaba nadie, y es el caso que la GUI produce sola: la pestaña de
# criterios acepta texto, y "asfaltico" o "adoquinado" son lo primero que
# alguien escribe.
#
# La segunda mitad del bloque es la contraria: la guarda del esviaje NEGATIVO
# de `factor_esviaje` no la alcanza ningun punto, porque M0 rechaza el valor
# al cargar el CSV. No se cubre por inyeccion: se demuestra que el rango que
# M0 admite cae entero dentro del que M7 admite (SIS-B-23).


@pytest.mark.parametrize("condicion", [
    "asfaltico",        # el nombre corriente de la fila 'flexible'
    "Flexible",         # la misma fila, con mayuscula
    "afirmado",         # el nombre peruano de 'no_pavimentado'
    "",
])
def test_una_condicion_de_pavimento_fuera_de_la_tabla_se_detiene(
        hdpe, declarar_condicion_pavimento, condicion):
    """
    Falla si `cobertura_minima_aashto` deja de validar la condicion contra la
    tabla y revienta mas adentro con un KeyError -- fallo de PROGRAMA para la
    GUI -- por un criterio que el proyectista escribio mal. Y falla tambien
    si el motivo deja de enumerar las filas: sin la lista, quien declaro
    "asfaltico" no tiene como saber que la fila se llama "flexible".

    Las filas NO se escriben aqui: se leen de la tabla transcrita, de modo
    que si mañana se transcribe una cuarta, el test la exige en el mensaje
    sin que nadie lo edite.
    """
    filas = sorted(ca.valor(CRITERIO_COBERTURA_AASHTO)[hdpe.tipo.value])
    assert condicion not in filas, "el caso dejo de ser una condicion invalida"

    declarar_condicion_pavimento(condicion)
    with pytest.raises(DatoInvalidoError) as exc:
        cobertura_minima_aashto(material=hdpe, D=1.50)

    assert exc.value.campo == CRITERIO_CONDICION_PAVIMENTO
    assert exc.value.valor == condicion
    assert "12.6.6.3-1" in exc.value.motivo
    for fila in filas:
        assert fila in exc.value.motivo


@pytest.mark.parametrize("tipo", list(TipoMaterial))
def test_las_tres_filas_transcritas_si_dan_cobertura(
        declarar_condicion_pavimento, tipo):
    """
    El contraste del test anterior: la guarda rechaza lo que no esta en la
    tabla y no estorba a lo que si. Falla si al transcribir una fila nueva
    alguien la deja sin entrada para alguno de los tres materiales.
    """
    material = catalogo(tipo)
    filas = ca.valor(CRITERIO_COBERTURA_AASHTO)[tipo.value]

    for condicion in sorted(filas):
        declarar_condicion_pavimento(condicion)
        assert cobertura_minima_aashto(material=material, D=1.50) > 0, condicion


# --- guarda defensiva: se demuestra inalcanzable, no se alcanza ------------

def test_M0_rechaza_el_esviaje_negativo_antes_de_que_M7_lo_vea(tmp_path):
    """
    SIS-B-23. `factor_esviaje` admite (-ESVIAJE_MAX, ESVIAJE_MAX) y M0 exige
    [0, ESVIAJE_MAX) al cargar el CSV: el rango de M7 es un SUPERCONJUNTO del
    que M0 deja entrar, de modo que la mitad negativa de su guarda no la
    alcanza ningun PuntoCritico que venga del expediente. Ese es el motivo de
    que no tenga test que la ejecute, y este es el motivo escrito.

    Se demuestra por las dos vias: el hecho (M0 rechaza el valor, con el
    campo, antes de construir el punto) y la contencion de los dos rangos.
    Falla el dia que alguien relaje M0 y deje pasar un esviaje negativo:
    entonces la guarda de M7 deja de ser defensiva y necesita su propio test.
    """
    origen = Path(__file__).resolve().parent / "ejemplo_puntos.csv"
    lineas = origen.read_text(encoding="utf-8-sig").splitlines()
    cabecera = lineas[0].split(",")
    columna = cabecera.index("esviaje_grados")

    celdas = lineas[1].split(",")
    celdas[columna] = "-15"
    csv_negativo = tmp_path / "esviaje_negativo.csv"
    csv_negativo.write_text("\n".join([lineas[0], ",".join(celdas)]),
                            encoding="utf-8")

    with pytest.raises(DatoInvalidoError) as exc:
        cargar_puntos(csv_negativo)

    assert exc.value.campo == "esviaje_grados"
    assert "0 (cruce perpendicular)" in exc.value.motivo

    # Y la contencion de los rangos, que es lo que hace defensiva a la guarda
    # de M7: los dos extremos que M0 admite caen dentro de lo que M7 admite.
    assert -ESVIAJE_MAX < 0 < ESVIAJE_MAX
    assert -ESVIAJE_MAX < ESVIAJE_MAX - 0.1 < ESVIAJE_MAX


def test_el_esviaje_perpendicular_y_el_casi_paralelo_si_los_admite_M7():
    """
    Los dos extremos del intervalo que M0 deja pasar los resuelve M7 sin
    tocar su guarda: el perpendicular no alarga nada y el casi paralelo
    alarga muchisimo, pero los dos tienen longitud definida.
    """
    assert factor_esviaje(_punto(esviaje_grados=0.0)) == pytest.approx(1.0)
    assert factor_esviaje(_punto(esviaje_grados=ESVIAJE_MAX - 0.1)) > 1.0


# ---------------------------------------------------------------------------
# 7.B con el talud DECLARADO: la rama viva de longitud y proyeccion (CP-9)
# ---------------------------------------------------------------------------
#
# 'talud_terraplen' sigue VACIO en criterios_adoptados.py y estos tests NO lo
# rellenan: lo declaran solo mientras dura el test, por el MISMO camino que
# usan la GUI y la CLI -- `establecer_valor_dinamico`, que pasa por la guardia
# `_verificar_criterio` -- y lo retiran en el `finally`. El archivo de
# criterios no se toca, `criterios_sin_valor()` vuelve a listarlo al salir y
# `test_el_criterio_del_talud_sigue_declarado_sin_valor` sigue siendo el
# canario del vacio.
#
# Los numeros no se escriben aqui: salen de CP9_GEOMETRIA_7B, que explica de
# donde viene cada uno y se autoverifica con `python3
# tests/fixtures/casos_patron.py`. Duplicarlos como literales en este archivo
# es exactamente el defecto SIS-F-14.

CP9 = CP9_GEOMETRIA_7B
TOL_L = CP9["tolerancia_longitud"]
TOL_COTA = CP9["tolerancia_cota"]


def _punto_7b(**cambios) -> PuntoCritico:
    """El punto de CP-9: la geometria de 7.B, sin tocar el resto de columnas."""
    base = dict(ancho_plataforma=CP9["ancho_plataforma"],
                cota_terreno=CP9["cota_terreno"],
                cota_rasante=CP9["cota_rasante"],
                cota_subrasante=CP9["cota_subrasante"],
                cota_fondo_receptor=CP9["cota_fondo_receptor"],
                esviaje_grados=CP9["esviaje_perpendicular_grados"])
    base.update(cambios)
    return _punto(**base)


@pytest.fixture
def talud_declarado():
    """
    Declara 'talud_terraplen' SOLO para este test y lo retira al salir.

    Las dos comprobaciones de los extremos no son adorno: fijan que el
    criterio entra vacio y sale vacio, de modo que ninguna prueba de este
    archivo pueda dejar el vacio tapado para las que corran despues.
    """
    assert CRITERIO_TALUD in ca.criterios_sin_valor()
    ca.establecer_valor_dinamico(CRITERIO_TALUD, CP9["talud_de_prueba"])
    try:
        yield CP9["talud_de_prueba"]
    finally:
        ca.quitar_valor_dinamico(CRITERIO_TALUD)
    assert CRITERIO_TALUD in ca.criterios_sin_valor()


def test_la_proyeccion_son_dos_taludes_por_la_altura_de_terraplen(talud_declarado):
    """
    proyeccion = 2 * talud * altura de terraplen (Sec. 7.B).

        altura     = 45.00 - 42.10   = 2.90 m
        proyeccion = 2 * 2.5 * 2.90  = 14.50 m

    Lo que este numero separa (CP-9): 2/talud daria 2.32, talud al cuadrado
    18.125, un solo talud 7.25 y dividir por la altura 1.724.
    """
    punto = _punto_7b()
    assert altura_terraplen(punto) == pytest.approx(
        CP9["altura_terraplen_esperada"], abs=TOL_COTA)
    assert proyeccion_taludes(punto) == pytest.approx(
        CP9["proyeccion_esperada"], abs=TOL_L)


def test_la_longitud_suma_la_proyeccion_al_ancho_de_plataforma(talud_declarado):
    """
    longitud = (ancho de plataforma + proyeccion) / cos(esviaje). En el cruce
    perpendicular el factor vale 1 y la longitud es la suma pura:

        9.60 + 14.50 = 24.10 m

    Restar en vez de sumar da -4.90 m: un conducto de longitud negativa, que
    hoy no detecta nadie.
    """
    punto = _punto_7b(esviaje_grados=CP9["esviaje_perpendicular_grados"])
    assert factor_esviaje(punto) == pytest.approx(
        CP9["factor_esviaje_perpendicular_esperado"], abs=TOL_L)
    assert longitud_conducto(punto) == pytest.approx(
        CP9["longitud_perpendicular_esperada"], abs=TOL_L)


def test_el_esviaje_alarga_la_longitud_dividiendo_por_el_coseno(talud_declarado):
    """
    La MISMA seccion transversal, cruzada a 30 grados, da un conducto mas
    largo -- no mas corto:

        (9.60 + 14.50) / cos(30 grados) = 24.10 * 1.15470054 = 27.828283 m

    Multiplicar por el coseno en vez de dividir daria 20.8712122 m, menos que
    el cruce perpendicular (24.10 m), que es geometricamente imposible. El
    ultimo assert es el que lo dice sin depender del numero.
    """
    oblicuo = _punto_7b(esviaje_grados=CP9["esviaje_oblicuo_grados"])
    perpendicular = _punto_7b(
        esviaje_grados=CP9["esviaje_perpendicular_grados"])
    L = longitud_conducto(oblicuo)
    assert L == pytest.approx(CP9["longitud_oblicua_esperada"], abs=TOL_L)
    assert L != pytest.approx(
        CP9["longitud_oblicua_si_multiplica_por_el_coseno"], abs=TOL_L)
    assert L > longitud_conducto(perpendicular)


def test_7B_sin_longitud_dada_la_calcula_y_de_ahi_salen_caida_y_cota_de_salida(
        hdpe, talud_declarado):
    """
    La rama VIVA de `compatibilidad_geometrica`: sin `longitud` la calcula con
    'talud_terraplen', y de esa longitud cuelgan la caida y la cota de salida
    que G2 verifica (CP-9).

        proyeccion  = 2 * 2.5 * 2.90               = 14.50 m
        longitud    = (9.60 + 14.50) / cos(30 gr)  = 27.828283 m
        caida       = 0.006 * 27.828283            =  0.1669697 m
        cota salida = 42.10 - 0.1669697            = 41.9330303 msnm
    """
    punto = _punto_7b(esviaje_grados=CP9["esviaje_oblicuo_grados"])
    geo = compatibilidad_geometrica(punto=punto, material=hdpe, D=1.50,
                                    resultado=_resultado(S=CP9["S"]))

    assert geo.altura_terraplen == pytest.approx(
        CP9["altura_terraplen_esperada"], abs=TOL_COTA)
    assert geo.proyeccion_taludes == pytest.approx(
        CP9["proyeccion_esperada"], abs=TOL_L)
    assert geo.longitud == pytest.approx(
        CP9["longitud_oblicua_esperada"], abs=TOL_L)
    assert geo.longitud == pytest.approx(longitud_conducto(punto), abs=TOL_L)
    assert geo.cota_entrada == pytest.approx(
        CP9["cota_entrada_esperada"], abs=TOL_COTA)
    assert geo.caida == pytest.approx(
        CP9["caida_oblicua_esperada"], abs=TOL_COTA)
    assert geo.cota_salida == pytest.approx(
        CP9["cota_salida_oblicua_esperada"], abs=TOL_COTA)
    assert geo.factible


def test_las_dos_ramas_de_7B_componen_y_despejan_la_misma_proyeccion(
        hdpe, talud_declarado):
    """
    Pasarle a 7.B la longitud que ella misma habria calculado tiene que
    devolver la MISMA proyeccion: la rama con longitud dada despeja lo que la
    rama viva compone. Ata las dos ramas, que hoy no se contrastan entre si.
    """
    punto = _punto_7b(esviaje_grados=CP9["esviaje_oblicuo_grados"])
    viva = compatibilidad_geometrica(punto=punto, material=hdpe, D=1.50,
                                     resultado=_resultado(S=CP9["S"]))
    dada = compatibilidad_geometrica(punto=punto, material=hdpe, D=1.50,
                                     resultado=_resultado(S=CP9["S"]),
                                     longitud=viva.longitud)
    assert dada.proyeccion_taludes == pytest.approx(
        CP9["proyeccion_esperada"], abs=TOL_L)
    assert dada.proyeccion_taludes == pytest.approx(viva.proyeccion_taludes,
                                                    abs=TOL_L)


def test_g2_es_inclusiva_en_el_fondo_del_receptor_y_absorbe_el_ruido_de_float():
    """
    G2 compara dos cotas y el umbral es INCLUSIVO: una salida que cae
    exactamente sobre el fondo del receptor cumple, y el ruido de punto
    flotante -- TOL_UMBRAL_NORMATIVO, sumado al lado admisible -- no la
    convierte en incumplimiento.

    Sin este test sobreviven dos mutantes de `g2_cota_salida`: cambiar `>=`
    por `>` (que reprueba la igualdad exacta) y sumar la tolerancia en vez de
    restarla (que la exige 1e-9 m por encima del fondo).
    """
    receptor = CP9_GEOMETRIA_7B["cota_fondo_receptor"]
    punto = _punto(cota_fondo_receptor=receptor)

    # exactamente sobre el fondo: cumple
    assert g2_cota_salida(punto=punto, cota_salida_m=receptor).cumple
    # justo en el borde inclusivo que la tolerancia abre: cumple
    assert g2_cota_salida(punto=punto,
                          cota_salida_m=receptor - TOL_UMBRAL_NORMATIVO).cumple
    # un milimetro por debajo: no cumple, y la tolerancia no lo tapa
    assert not g2_cota_salida(punto=punto,
                              cota_salida_m=receptor - 1e-3).cumple


def test_el_esviaje_casi_paralelo_pasa_M0_y_da_una_longitud_absurda():
    """
    MAT-O18, la parte que su ficha da por inalcanzable y NO lo es. M0 valida
    `0 <= esviaje < 90`, de modo que 89.999999999 grados entra: el factor de
    esviaje vale 5.7e10 y la longitud del conducto sale del orden de 1e11 m.

    No se acota, y el docstring de `factor_esviaje` dice por que: no hay
    esviaje maximo constructivo que citar -- ni Sec. 7.B ni EG-2013 lo fijan --
    y elegir uno seria inventar un valor normativo. Este test existe para que
    el numero este MEDIDO y a la vista, en vez de descrito como imposible.
    """
    casi_paralelo = _punto(esviaje_grados=ESVIAJE_MAX - 1e-9)
    factor = factor_esviaje(casi_paralelo)

    assert factor > 1e9, (
        "el factor tiene que ser astronomico: si dejara de serlo, alguien "
        "puso una cota y hay que declararla como criterio")
    assert math.isfinite(factor), (
        "y aun asi finito: el dominio es abierto en 90, no cerrado")

    # El extremo cerrado si esta cubierto por la guarda.
    with pytest.raises(DatoInvalidoError):
        factor_esviaje(_punto(esviaje_grados=ESVIAJE_MAX))


# ---------------------------------------------------------------------------
# SIS-G-01 - el desborde aritmetico de 7.B
# ---------------------------------------------------------------------------

def test_una_cota_finita_pero_enorme_no_sale_como_inf_a_la_memoria():
    """
    SIS-G-01. La guarda de ENTRADA no puede cerrar esto y por eso hace falta
    la de SALIDA.

    `cota_rasante = 1e308` es finita: pasa `M0._a_float` (que solo rechaza
    'inf' y 'nan', MAT-D14) y pasa `_valida_rangos`, porque NINGUNA cota tiene
    techo en dominios.py. Con ella `altura_terraplen` sigue siendo finita
    (1e308) y es la MULTIPLICACION de `proyeccion_taludes` -- 2 * talud *
    altura -- la que desborda.

    Antes de esta guarda el `inf` no paraba en ningun sitio: `longitud_conducto`
    lo propagaba y el informe salia con `"longitud_m": {"valor": "inf"}`, un
    diagnostico entero construido sobre un numero que no lo es. Que es peor
    que un fallo, porque se lee como un resultado.

    NO se cierra poniendole techo a la cota: eso seria inventar un valor de
    proyecto, que CLAUDE.md prohibe. Ver `M7._exigir_finito`.
    """
    ca.establecer_valor_dinamico(CRITERIO_TALUD, 1.5)
    try:
        desmesurado = _punto(cota_rasante=1e308)

        # La entrada es finita: el problema no esta en el dato.
        assert math.isfinite(altura_terraplen(desmesurado))

        with pytest.raises(LimiteNumericoError) as exc:
            proyeccion_taludes(desmesurado)
        assert exc.value.campo == "proyeccion_taludes"
        assert exc.value.id_punto == "A-01"

        # Y la guarda INTERNA gana a la externa: quien llama a
        # `longitud_conducto` recibe el nombre de la magnitud que desbordo de
        # verdad, no el de la que la contiene.
        with pytest.raises(LimiteNumericoError) as exc_larga:
            longitud_conducto(desmesurado)
        assert exc_larga.value.campo == "proyeccion_taludes"
    finally:
        ca.quitar_valor_dinamico(CRITERIO_TALUD)


def test_el_desborde_de_7b_es_un_error_de_proyecto_y_no_un_crash():
    """
    La razon de que `LimiteNumericoError` descienda de `ErrorProyecto`: la GUI
    atrapa la raiz con un solo `except` (gui/app.py importa `ErrorProyecto` y
    nada mas) y tiene que mostrar esto como aviso, no como traza.

    El diagnostico es aritmetico, pero el remedio esta en el expediente: la
    cota absurda se corrige en el CSV.
    """
    ca.establecer_valor_dinamico(CRITERIO_TALUD, 1.5)
    try:
        with pytest.raises(ErrorProyecto):
            proyeccion_taludes(_punto(cota_rasante=1e308))
    finally:
        ca.quitar_valor_dinamico(CRITERIO_TALUD)


def test_la_guarda_de_finitud_no_estorba_al_camino_feliz():
    """
    El trinquete de la guarda: con datos de proyecto tiene que ser invisible.
    Si este test se rompe, alguien la escribio demasiado estrecha.
    """
    ca.establecer_valor_dinamico(CRITERIO_TALUD, 1.5)
    try:
        punto = _punto()
        assert math.isfinite(altura_terraplen(punto))
        assert math.isfinite(proyeccion_taludes(punto))
        assert math.isfinite(longitud_conducto(punto))
    finally:
        ca.quitar_valor_dinamico(CRITERIO_TALUD)
