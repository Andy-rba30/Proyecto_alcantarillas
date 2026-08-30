"""
tests/test_M2_material.py
==========================
M2 contra la Fase 3: catalogo de diametros normalizado (Sec. 3.2) y matriz de
decision de material (Sec. 3.4).

Los tests que mas importan son cuatro:

    - la progresion arranca en 0.90 m y sube de 0.15 m en 0.15 m;
    - cada material se detiene en SU tope de Sec. 3.2 (el de HDPE es el mas
      restrictivo: ~1.50 m) y siguiente_diametro() devuelve None ahi, nunca
      un numero que no existe como producto;
    - v_max_adoptado y h_relleno_min salen en None para TMC/HDPE sin lanzar
      CriterioPendienteError, porque el vacio esta documentado, no relleno;
    - la Familia C no tiene candidatos: su seccion es marco o multicelda.
"""

from pathlib import Path

import pytest

import criterios_adoptados as ca
from modelos import DatoFaltanteError, DatoInvalidoError, Familia, Material, TipoMaterial
from modulos.M0_carga import cargar_puntos
from modulos.M2_material import (CRITERIO_ESPESOR_PARED, catalogo,
                                 espesor_pared, materiales_candidatos,
                                 siguiente_diametro)
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.aproximacion import REL_TRANSPORTE

CSV_VALIDO = Path(__file__).resolve().parent / "ejemplo_puntos.csv"


@pytest.fixture
def puntos():
    return cargar_puntos(CSV_VALIDO)


@pytest.fixture
def punto_a(puntos):
    return puntos[0]        # A-01, Familia A


@pytest.fixture
def punto_c(puntos):
    return puntos[3]        # C-01, Familia C


# ---------------------------------------------------------------------------
# Sec. 3.2 - Progresion de diametros
# ---------------------------------------------------------------------------

def test_el_primer_diametro_es_el_minimo_normativo():
    assert siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO) == pytest.approx(0.90)


def test_el_paso_es_de_15_cm():
    D0 = siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO)
    D1 = siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO, D0)
    D2 = siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO, D1)
    assert D1 == pytest.approx(1.05)
    assert D2 == pytest.approx(1.20)


def test_admite_el_tipo_de_material_como_string():
    assert siguiente_diametro("concreto_reforzado") == pytest.approx(0.90)


@pytest.mark.parametrize("material, esperado", [
    (TipoMaterial.CONCRETO_REFORZADO, 2.70),
    (TipoMaterial.TMC, 2.10),
    (TipoMaterial.HDPE, 1.50),
])
def test_cada_material_se_detiene_en_su_tope(material, esperado):
    D = siguiente_diametro(material)
    ultimo = None
    while D is not None:
        assert D <= esperado + 1e-6
        ultimo = D
        D = siguiente_diametro(material, D)
    assert ultimo == pytest.approx(esperado)


def test_el_hdpe_es_el_mas_restrictivo():
    """Sec. 3.2: sin tope, el solver podria converger a un HDPE de 2.70 m,
    que no existe como producto AASHTO M294."""
    D = 1.50
    assert siguiente_diametro(TipoMaterial.HDPE, D) is None


def test_un_diametro_fuera_de_la_progresion_es_invalido():
    with pytest.raises(DatoInvalidoError) as exc:
        siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO, 1.00)
    assert exc.value.campo == "D"


def test_un_material_desconocido_es_invalido():
    with pytest.raises(DatoInvalidoError) as exc:
        siguiente_diametro("fierro_fundido")
    assert exc.value.campo == "material"


# ---------------------------------------------------------------------------
# Sec. 3.4 - Catalogo de material
# ---------------------------------------------------------------------------

def test_catalogo_devuelve_un_material_completo():
    concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    assert isinstance(concreto, Material)
    assert concreto.tipo is TipoMaterial.CONCRETO_REFORZADO
    assert concreto.D_max == pytest.approx(2.70)
    assert concreto.n_min == pytest.approx(0.010)
    assert concreto.n_max == pytest.approx(0.013)
    assert concreto.v_max_tabla10 == pytest.approx((3.0, 6.0))
    assert concreto.v_max_adoptado is None
    assert concreto.fila_manning.endswith("tubo recto y libre de basuras")
    assert concreto.seccion_eg2013 == "506"


def test_el_hdpe_usa_el_rango_de_manning_por_analogia():
    hdpe = catalogo(TipoMaterial.HDPE)
    assert hdpe.n_min == pytest.approx(0.010)
    assert hdpe.n_max == pytest.approx(0.013)
    assert hdpe.seccion_eg2013 == "508"
    assert hdpe.h_relleno_min_eg2013 == pytest.approx(0.30)   # [N] directo, sin vacio


def test_la_velocidad_maxima_declarada_llega_al_catalogo():
    """
    'v_max_tmc' y 'v_max_hdpe' ya estan declarados (WSDOT Hydraulics Manual,
    Tabla 8-4): el catalogo los trae y `v_max_definida` lo confirma.
    """
    tmc = catalogo(TipoMaterial.TMC)
    hdpe = catalogo(TipoMaterial.HDPE)
    assert tmc.v_max_adoptado == pytest.approx(ca.valor("v_max_tmc"),
                                               rel=REL_TRANSPORTE)
    assert hdpe.v_max_adoptado == pytest.approx(ca.valor("v_max_hdpe"),
                                                rel=REL_TRANSPORTE)
    assert tmc.v_max_tabla10 is None and hdpe.v_max_tabla10 is None
    assert tmc.v_max_definida
    assert hdpe.v_max_definida


def test_un_vacio_de_velocidad_maxima_no_detiene_el_catalogo(monkeypatch):
    """
    Lo que el test anterior protegia antes de que el criterio tuviera valor, y
    sigue siendo la conducta correcta si alguna vez vuelve a vaciarse: M2 lee
    esos criterios con tolerancia y refleja el vacio con None, en vez de
    lanzar CriterioPendienteError al construir el catalogo. Quien se detiene
    es V3, que es donde el numero hace falta.
    """
    original = ca.CRITERIOS["v_max_tmc"]
    monkeypatch.setitem(ca.CRITERIOS, "v_max_tmc",
                        original.__class__(**{**original.__dict__,
                                              "valor": None}))
    tmc = catalogo(TipoMaterial.TMC)
    assert tmc.v_max_adoptado is None
    assert not tmc.v_max_definida


# ---------------------------------------------------------------------------
# Declaracion en caliente: la via de la GUI
# ---------------------------------------------------------------------------
#
# `ca.establecer_valor_dinamico` es como la pestana "Criterios" de la GUI
# declara un criterio pendiente sin tocar criterios_adoptados.py. El catalogo
# tiene que verlo igual que si estuviera escrito en el archivo.
#
# El caso que fallaba era exactamente este: criterio VACIO en el archivo y
# declarado en caliente. `_valor_si_declarado` miraba `ca.criterio().valor` --
# el dict del archivo -- y devolvia None sin consultar los overrides, de modo
# que la declaracion del usuario se perdia. Con la clave YA declarada en el
# archivo el bug no se veia, porque la lectura caia en `ca.valor()`, que si
# resuelve overrides.

@pytest.fixture
def vaciar_criterio(monkeypatch):
    """Deja un criterio sin valor en el archivo, como estaba antes de cerrarse."""
    def _vaciar(clave):
        original = ca.CRITERIOS[clave]
        monkeypatch.setitem(ca.CRITERIOS, clave,
                            original.__class__(**{**original.__dict__,
                                                  "valor": None}))
    return _vaciar


def test_el_n_de_manning_del_hdpe_declarado_en_caliente_llega_al_catalogo(
        vaciar_criterio):
    """
    El peor de los tres: el None se desempaquetaba en (n_min, n_max) y
    reventaba con TypeError -- un fallo de PROGRAMA por un dato que el usuario
    si habia declarado.
    """
    vaciar_criterio("n_manning_hdpe")
    ca.establecer_valor_dinamico("n_manning_hdpe", (0.011, 0.012))
    try:
        hdpe = catalogo(TipoMaterial.HDPE)
        assert (hdpe.n_min, hdpe.n_max) == pytest.approx((0.011, 0.012),
                                                    rel=REL_TRANSPORTE)
    finally:
        ca.quitar_valor_dinamico("n_manning_hdpe")


def test_el_espesor_de_pared_declarado_en_caliente_llega_al_catalogo(
        vaciar_criterio):
    """
    Mismo mecanismo que probaba 'h_relleno_min_concreto_tmc' antes de
    retirarse (NOR-VAC-01): un criterio que el catalogo lee con
    `valor_si_declarado` tiene que ver la declaracion en caliente, no solo el
    valor del archivo.
    """
    vaciar_criterio("espesor_pared_conducto")
    ca.establecer_valor_dinamico(
        "espesor_pared_conducto",
        {"concreto_reforzado": 0.12, "tmc": 0.02, "hdpe": 0.06})
    try:
        concreto = catalogo(TipoMaterial.CONCRETO_REFORZADO)
        assert concreto.espesor_pared == pytest.approx(0.12)
    finally:
        ca.quitar_valor_dinamico("espesor_pared_conducto")


def test_la_velocidad_maxima_declarada_en_caliente_llega_al_catalogo(
        vaciar_criterio):
    vaciar_criterio("v_max_tmc")
    ca.establecer_valor_dinamico("v_max_tmc", 3.9)
    try:
        tmc = catalogo(TipoMaterial.TMC)
        assert tmc.v_max_adoptado == pytest.approx(3.9)
        assert tmc.v_max_definida
    finally:
        ca.quitar_valor_dinamico("v_max_tmc")


def test_la_declaracion_en_caliente_pisa_al_valor_del_archivo():
    """
    Sin vaciar nada: el override tiene que ganar sobre el valor escrito. Esta
    rama ya funcionaba antes del arreglo (caia en `ca.valor()`), y el test la
    fija para que siga funcionando.
    """
    assert ca.criterio("v_max_tmc").valor is not None
    ca.establecer_valor_dinamico("v_max_tmc", 3.9)
    try:
        assert catalogo(TipoMaterial.TMC).v_max_adoptado == pytest.approx(3.9)
    finally:
        ca.quitar_valor_dinamico("v_max_tmc")
    assert catalogo(TipoMaterial.TMC).v_max_adoptado == pytest.approx(
        ca.valor("v_max_tmc"), rel=REL_TRANSPORTE)


def test_solo_el_hdpe_tiene_minimo_de_relleno_en_eg2013():
    """
    EG-2013 fija la altura minima de relleno UNICAMENTE para HDPE (Subseccion
    508.07, pag. 984). El None de concreto y TMC significa eso y nada mas: su
    recubrimiento minimo lo pone la Tabla 12.6.6.3-1 de AASHTO LRFD, en
    `M7_geometria.altura_recubrimiento`.

    Este test comprobaba antes que los tres valian 0.30 m, que era la
    analogia de 'h_relleno_min_concreto_tmc'. Se retiro con el criterio
    (NOR-VAC-01): el 0.30 m quedaba 5 mm bajo el piso de 12 in de esa tabla.
    """
    assert catalogo(TipoMaterial.HDPE).h_relleno_min_eg2013 == pytest.approx(0.30)
    assert catalogo(TipoMaterial.CONCRETO_REFORZADO).h_relleno_min_eg2013 is None
    assert catalogo(TipoMaterial.TMC).h_relleno_min_eg2013 is None


def test_un_material_desconocido_en_catalogo_es_invalido():
    with pytest.raises(DatoInvalidoError):
        catalogo("pvc")


# ---------------------------------------------------------------------------
# Filtro de candidatos
# ---------------------------------------------------------------------------

def test_familia_a_tiene_los_tres_materiales_candidatos(punto_a):
    candidatos = materiales_candidatos(punto_a)
    assert {m.tipo for m in candidatos} == set(TipoMaterial)


def test_familia_c_no_tiene_candidatos(punto_c):
    """Sec. 2.3: la Familia C es marco o multicelda, no un conducto circular."""
    assert punto_c.familia is Familia.C
    assert materiales_candidatos(punto_c) == ()


# ===========================================================================
# C09 / SIS-F-10 - las dos guardas de 'espesor_pared_conducto'
# ===========================================================================
#
# El criterio es un dict {material: {diametro designado en mm: espesor en m}}
# -- desde S20, cuando dejo de ser un escalar por material: el espesor de
# pared depende del diametro y el bucle de MD recorre el catalogo entero -- y
# lo leen DOS sitios, con dos guardas distintas y motivos distintos:
#
#   `catalogo()`       rechaza la declaracion MAL FORMADA -- un escalar donde
#                      se espera el dict --, y la rechaza al construir el
#                      material, antes de que nadie use el numero.
#   `espesor_pared()`  rechaza el espesor que no es un numero y la fila de
#                      diametro que falta, ya con el material armado, en el
#                      punto donde el numero hace falta de verdad.
#
# Ninguna de las dos tenia corrida que la ejecutara. Las dos son
# DatoInvalidoError y no CriterioPendienteError a proposito: el criterio SI
# esta declarado -- hay que corregirlo, no declararlo (CLAUDE.md).


@pytest.mark.parametrize("declaracion", [
    0.10,               # el float que la GUI sabe ofrecer
    "0.10",             # el texto crudo de la casilla
    [0.10, 0.013, 0.05],  # los tres espesores sin la clave de cada material
])
def test_un_espesor_declarado_sin_separar_por_material_es_dato_invalido(
        declaracion):
    """
    Falla si `catalogo()` deja de comprobar la FORMA de la declaracion: sin
    esta guarda un escalar declarado desde la GUI reventaba mas adentro con
    un `TypeError` -- un fallo de programa para la GUI -- en vez de salir
    como problema del expediente con el nombre del criterio.
    """
    ca.establecer_valor_dinamico(CRITERIO_ESPESOR_PARED, declaracion)
    try:
        with pytest.raises(DatoInvalidoError) as exc:
            catalogo(TipoMaterial.CONCRETO_REFORZADO)
    finally:
        ca.quitar_valor_dinamico(CRITERIO_ESPESOR_PARED)

    assert exc.value.campo == CRITERIO_ESPESOR_PARED
    assert "una tabla de espesores por material" in exc.value.motivo
    # El motivo tiene que enseñar la forma esperada, con las tres claves:
    # es lo unico que le dice al revisor como se corrige.
    for tipo in TipoMaterial:
        assert tipo.value in exc.value.motivo


@pytest.mark.parametrize("espesor_declarado", [
    "0.10",             # el numero, pero como texto
    (0.10,),            # empaquetado, como si fuera un rango
    "diez centimetros",
])
def test_un_espesor_de_pared_que_no_es_un_numero_se_detiene_al_usarlo(
        espesor_declarado):
    """
    La declaracion tiene la forma correcta (dict por material) y el valor de
    dentro no es un numero. Falla si `espesor_pared()` deja pasar el valor:
    el espesor entra en la cota de clave (M5) y en la cobertura de AASHTO
    (M7), y un texto ahi revienta con TypeError a dos modulos de distancia
    del dato que lo causo.
    """
    ca.establecer_valor_dinamico(
        CRITERIO_ESPESOR_PARED,
        {"concreto_reforzado": {900: espesor_declarado},
         "tmc": {900: 0.013}, "hdpe": {900: 0.050}})
    try:
        material = catalogo(TipoMaterial.CONCRETO_REFORZADO)
        with pytest.raises(DatoInvalidoError) as exc:
            espesor_pared(material, 0.90)
    finally:
        ca.quitar_valor_dinamico(CRITERIO_ESPESOR_PARED)

    assert exc.value.campo == CRITERIO_ESPESOR_PARED
    assert "no es un numero" in exc.value.motivo
    # Y dice PARA QUE MATERIAL, que es lo que el revisor tiene que corregir:
    # los otros dos de la misma declaracion estaban bien.
    assert TipoMaterial.CONCRETO_REFORZADO.value in exc.value.motivo


def test_los_otros_materiales_de_la_misma_declaracion_siguen_valiendo():
    """
    La guarda es por material, no por declaracion entera: falla si alguien la
    sube a `catalogo()` y un espesor mal escrito en concreto deja sin
    catalogo al TMC y al HDPE, que estan bien.
    """
    ca.establecer_valor_dinamico(
        CRITERIO_ESPESOR_PARED,
        {"concreto_reforzado": {900: "0.10"},
         "tmc": {900: 0.013}, "hdpe": {900: 0.050}})
    try:
        assert espesor_pared(catalogo(TipoMaterial.TMC), 0.90) == pytest.approx(
            0.013, rel=REL_TRANSPORTE)
        assert espesor_pared(catalogo(TipoMaterial.HDPE), 0.90) == pytest.approx(
            0.050, rel=REL_TRANSPORTE)
    finally:
        ca.quitar_valor_dinamico(CRITERIO_ESPESOR_PARED)


def test_un_diametro_sin_fila_en_la_tabla_de_espesores_se_reclama_por_su_nombre():
    """
    La guarda que el modelo anterior no podia dar. Con un espesor ESCALAR por
    material, un punto que cerrara en 1.20 m se calculaba con el espesor del
    de 0.90 m y nada avisaba -- y el bucle de MD recorre el catalogo entero,
    de modo que no era un caso remoto. Ahora falta la fila y se dice cual.
    """
    ca.establecer_valor_dinamico(
        CRITERIO_ESPESOR_PARED, {"concreto_reforzado": {900: 0.100}})
    try:
        material = catalogo(TipoMaterial.CONCRETO_REFORZADO)
        assert espesor_pared(material, 0.90) == pytest.approx(
            0.100, rel=REL_TRANSPORTE)
        with pytest.raises(DatoFaltanteError) as exc:
            espesor_pared(material, 1.20)
    finally:
        ca.quitar_valor_dinamico(CRITERIO_ESPESOR_PARED)

    assert "1200" in exc.value.campo
    assert "no se interpola" in exc.value.detalle
