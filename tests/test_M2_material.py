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
from modelos import (CriterioPendienteError, DatoFaltanteError,
                     DatoInvalidoError, Familia, FormaSeccion, Material,
                     TipoMaterial)
from modulos.M0_carga import cargar_puntos
from modulos.M2_material import (CRITERIO_ESPESOR_PARED, catalogo,
                                 espesor_pared, materiales_candidatos,
                                 siguiente_diametro, siguiente_seccion)
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import declarados

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


def test_familia_c_ofrece_el_marco_y_se_detiene_en_sus_criterios(punto_c):
    """
    C5 ABRIO LA FAMILIA C, y este test cambio de contrato con ella. Decia
    `materiales_candidatos(punto_c) == ()` -- Sec. 2.3 le asigna marco o
    multicelda y el catalogo era de conductos circulares --, y esa premisa ya
    no vale: el catalogo tiene forma y ofrece el marco.

    LO QUE SE COMPRUEBA AHORA ES LA DETENCION, que es lo que de verdad
    importa: el candidato existe y NO se puede construir todavia, porque sus
    criterios estan sin declarar por mandato del num. 4.1.1.3.4 a). La
    diferencia con antes no es de forma: "no hay material" no se podia
    resolver declarando nada, y "falta declarar la embocadura del marco" es
    una linea de la lista de trabajo del tesista.
    """
    assert punto_c.familia is Familia.C
    with pytest.raises(CriterioPendienteError) as exc:
        materiales_candidatos(punto_c)
    assert exc.value.clave == "embocadura_cajon"


def test_con_los_criterios_del_cajon_declarados_la_familia_c_da_un_candidato(
        punto_c):
    """
    La otra mitad, y hace falta: sin ella el test de arriba pasaria igual si
    `materiales_candidatos` levantara la excepcion y no ofreciera nada.

    Los valores se declaran EN CALIENTE y solo para este test, por el mismo
    camino que usan la GUI y la CLI. No son adopciones del expediente: lo que
    se ejercita es que el candidato se arma, que es de MARCO y que arrastra la
    fila de la Tabla N 09 con su analogia escrita.
    """
    with declarados({"embocadura_cajon": "cajon_concreto_aletas_30_75",
                     "n_manning_cajon": "concreto_afinado",
                     "n_celdas_cajon": 1,
                     "secciones_cajon_normalizadas": ((1.50, 1.20),
                                                      (2.00, 1.50))}):
        candidatos = materiales_candidatos(punto_c)

        assert len(candidatos) == 1, (
            "la Familia C tiene UN candidato: el marco de concreto. El TMC y "
            "el HDPE son productos de seccion circular")
        marco = candidatos[0]
        assert marco.forma is FormaSeccion.RECTANGULAR
        assert marco.tipo is TipoMaterial.CONCRETO_REFORZADO
        assert "afinado" in marco.fila_manning
        assert "analogia declarada" in marco.fila_manning
        # La carta es de CAJON, no la circular con otras constantes (regla #5).
        assert marco.hds5.forma in (1, 2)


# ---------------------------------------------------------------------------
# Los CINCO pasos de Fase 3 del marco, y el tope de catalogo que trae con ellos
# ---------------------------------------------------------------------------
# Este bloque es el que `tests/test_memoria_sustentada.py` nombra por su
# nombre al declarar los cinco fundamentos del cajon como «inalcanzables en
# esta corrida»: alli se declara que los pasos EXISTEN aunque la corrida por
# defecto no llegue a emitirlos, y aqui se mide.

DECLARACIONES_CAJON = {
    "embocadura_cajon": "cajon_concreto_aletas_30_75",
    "n_manning_cajon": "concreto_afinado",
    "n_celdas_cajon": 1,
    "ke_entrada_cajon": "cajon_aletas_30_75_escuadra",
    "secciones_cajon_normalizadas": ((1.50, 1.20), (2.00, 1.50), (2.50, 2.00)),
}


def _marco():
    return catalogo(TipoMaterial.CONCRETO_REFORZADO,
                    forma=FormaSeccion.RECTANGULAR)


def test_un_espesor_de_pared_de_cajon_nulo_o_negativo_se_detiene():
    """
    LA GUARDIA QUE NADIE MEDIA: cambiar `not t > 0` por `not t >= 0` en la
    rama del cajon de `M2.espesor_pared` sobrevivia a la suite entera, y lo
    midio la auditoria adversarial de C7. El umbral es MEDIDO y no generico
    -- forma MAT-D13 --: un espesor de cero no es «un dato raro», es una pared
    que no existe, y con el la subpresion se evaluaria sobre la seccion
    INTERIOR, que es la direccion insegura de MAT-D3.

    LA MITAD DEL NaN NO SE MIDE AQUI, Y SE DICE POR QUE: la capa de
    declaracion lo rechaza ANTES -- `criterios_adoptados` no admite declarar
    un criterio con NaN ni con infinito --, de modo que por la via del
    expediente ese valor no llega nunca a `espesor_pared`. La forma `not t > 0`
    se conserva igual, como guarda defensiva y por coherencia con MAT-D13; lo
    que este test mide son los dos casos ALCANZABLES.
    """
    for valor in (0.0, -0.05):
        declaraciones = dict(DECLARACIONES_CAJON,
                             **{"espesor_pared_cajon": valor})
        with declarados(declaraciones):
            with pytest.raises(DatoInvalidoError) as exc:
                espesor_pared(_marco(), 1.50)
        assert exc.value.campo == "espesor_pared_cajon", valor


def test_el_marco_no_hereda_la_seccion_de_tuberia_del_eg2013():
    """
    PUNTO 6 DEL BRIEF DE C7, y es la forma exacta de NOR-PUE-01: numeral que
    existe, titulo que suena a lo buscado, contenido que es otro.

    `SECCION_EG2013` indexa por MATERIAL y sus cuatro entradas son de TUBERIA
    -- los cuatro titulos impresos empiezan por esa palabra --, de modo que un
    marco de concreto reforzado heredaba la 506. La 506 se titula «Tuberia de
    concreto reforzado», su num. 506.01 alcanza «la instalacion de tubos», su
    506.02 pide el «diametro interno» y su partida 506.A se mide en METRO
    LINEAL: ninguna de las tres cosas le corresponde a un marco vaciado in
    situ.

    Donde SI cae es en la Seccion 503, y es hallazgo positivo y no un vacio:
    el num. 503.10 h) (impresa 926) le fija plazo de desencofrado a la «Placa
    superior en alcantarillas de cajon», o sea que el EG-2013 regula el
    vaciado in situ del cajon bajo la Seccion de concreto estructural. El
    «+ 504» del acero es ensamblaje del proyecto, autorizado por la ausencia
    verificada de partida propia (`SIN_PARTIDA_DE_CAJON_EG2013`), y esta dicho
    como tal en `NUMERAL_SECCION_CAJON_EG2013`.

    EL TUBO NO SE MUEVE, que es la otra mitad: la 506 sigue siendo suya.
    """
    from constantes_normativas import (SECCION_ACERO_REFUERZO,
                                       SECCION_CONCRETO_ESTRUCTURAL,
                                       SECCION_EG2013_CAJON)

    with declarados(DECLARACIONES_CAJON):
        marco = _marco()
    tubo = catalogo(TipoMaterial.CONCRETO_REFORZADO)

    assert marco.seccion_eg2013 == SECCION_EG2013_CAJON
    assert marco.seccion_eg2013 != tubo.seccion_eg2013
    assert tubo.seccion_eg2013 == "506"
    # Y las dos Secciones que la componen, nombradas: la del concreto y la del
    # acero, no una tercera inventada.
    assert SECCION_CONCRETO_ESTRUCTURAL in marco.seccion_eg2013
    assert SECCION_ACERO_REFUERZO in marco.seccion_eg2013


def test_los_cinco_pasos_de_fase_3_del_marco_salen_con_su_fundamento():
    """
    Los cinco pasos que `M2._pasos_del_marco` emite, con su fundamento.

    NO ES UN TEST DE ADORNO. `test_memoria_sustentada` deja los cinco
    fundamentos del cajon en `sin_alcanzar` -- la lista de los que ninguna
    corrida por defecto imprime -- y la unica razon por la que eso no es un
    hueco es que los pasos existen y se pueden ejercitar declarando los
    criterios. Si este test desaparece, aquella lista pasa a tapar cinco
    fundamentos huerfanos sin que nada avise.
    """
    with declarados(DECLARACIONES_CAJON):
        ids = [p.fundamento_id for p in _marco().pasos]
    assert ids == ["F3.TIPO_MARCO", "F3.SECCION_CANAL", "F3.MANTENIMIENTO",
                   "F3.CELDAS", "F4.N_CAJON"]


def test_el_tubo_no_emite_ningun_paso_de_fase_3():
    """
    La contraparte, y es la que fija que los cinco no son decoracion: el tubo
    NO elige nada en Fase 3 -- su fila de la Tabla N 09 y su carta de la Tabla
    A.1 son lectura directa -- y por eso su tupla viene vacia.
    """
    assert catalogo(TipoMaterial.CONCRETO_REFORZADO).pasos == ()


def test_el_tope_de_catalogo_del_marco_sale_de_su_propia_progresion():
    """
    `D_max` del marco es la MAYOR altura declarada, no el tope del tubo.

    Es lo que impide que V9 rechace o acepte un marco citando
    'D_max_catalogo', cuyo valor es un diametro de TUBERIA por material: el
    numero habria sido verdadero (2.70 m existe) y la procedencia falsa, que
    es el defecto que NOR-PRO-01 cerro para el circular.
    """
    with declarados(DECLARACIONES_CAJON):
        marco = _marco()
        tubo = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    assert marco.D_max == pytest.approx(2.00, rel=REL_TRANSPORTE)   # max H
    assert tubo.D_max == pytest.approx(2.70, rel=REL_TRANSPORTE)    # tubo
    assert "secciones_cajon_normalizadas" in marco.D_max_de_catalogo
    assert "NO DE NORMA" in marco.D_max_de_catalogo


# ---------------------------------------------------------------------------
# siguiente_seccion: la puerta que impide diseñar un tubo con datos de cajon
# ---------------------------------------------------------------------------

def test_siguiente_seccion_del_marco_recorre_la_progresion_declarada():
    with declarados(DECLARACIONES_CAJON):
        marco = _marco()
        s0 = siguiente_seccion(marco)
        s1 = siguiente_seccion(marco, s0)
        s2 = siguiente_seccion(marco, s1)
        assert (s0.B, s0.altura) == pytest.approx((1.50, 1.20),
                                                  rel=REL_TRANSPORTE)
        assert (s1.B, s1.altura) == pytest.approx((2.00, 1.50),
                                                  rel=REL_TRANSPORTE)
        assert (s2.B, s2.altura) == pytest.approx((2.50, 2.00),
                                                  rel=REL_TRANSPORTE)
        assert siguiente_seccion(marco, s2) is None


def test_el_marco_no_hereda_el_piso_de_090_m():
    """
    REGLA VINCULANTE #1, medida en vez de citada. El num. 4.1.1.3.4 a) fija el
    piso de 0.90 m y lo EXCEPTUA en la misma oracion para los cruces de canal
    de riego, que es lo que la Familia C es. El catalogo del marco tiene que
    admitir una serie entera por debajo de ese piso sin rechazar nada.

    Se mide con una progresion de 0.60 a 0.80 m: si alguien le colara al marco
    el filtro del circular -- o el `DIAMETRO_MIN` por cualquier via --, las
    tres desaparecen y este test cae. C6 lo añade porque la regla se citaba en
    cinco sesiones y ningun test la nombraba: lo unico que la rozaba era otro
    test cuya progresion empieza en 1.20 m, o sea POR ENCIMA del piso, que no
    distingue heredarlo de no heredarlo.
    """
    serie = ((0.80, 0.60), (1.00, 0.70), (1.10, 0.80))
    with declarados({**DECLARACIONES_CAJON,
                     "secciones_cajon_normalizadas": serie}):
        marco = _marco()
        recorridas = []
        seccion = siguiente_seccion(marco)
        while seccion is not None:
            recorridas.append((seccion.B, seccion.altura))
            seccion = siguiente_seccion(marco, seccion)
        tope = marco.D_max
    assert len(recorridas) == len(serie)
    for obtenida, esperada in zip(recorridas, serie):
        assert obtenida == pytest.approx(esperada, rel=REL_TRANSPORTE)
    assert tope == pytest.approx(0.80, rel=REL_TRANSPORTE)


def test_una_seccion_fuera_de_la_progresion_declarada_es_dato_invalido():
    """
    El catalogo no reconoce secciones "de proveedor", igual que no reconoce
    diametros fuera de la progresion (Sec. 3.2).
    """
    from modelos import SeccionRectangular
    with declarados(DECLARACIONES_CAJON):
        with pytest.raises(DatoInvalidoError) as exc:
            siguiente_seccion(_marco(), SeccionRectangular(1.75, 1.35))
    assert "secciones_cajon_normalizadas" in exc.value.motivo


def test_siguiente_seccion_del_tubo_no_lee_ningun_criterio_del_cajon():
    """
    LA PUERTA, dicha al reves: un tubo recorre su progresion sin tocar ningun
    criterio del marco. Sin esto, abrir la forma habria bastado para que una
    corrida circular se bloqueara pidiendo la seccion de un cajon que no
    tiene.
    """
    tubo = catalogo(TipoMaterial.CONCRETO_REFORZADO)
    s0 = siguiente_seccion(tubo)                 # no lanza CriterioPendiente
    assert s0.altura == pytest.approx(0.90, rel=REL_TRANSPORTE)
    assert siguiente_seccion(tubo, s0).altura == pytest.approx(
        1.05, rel=REL_TRANSPORTE)


# ---------------------------------------------------------------------------
# Las guardias que la auditoria adversarial de C5 exigio
# ---------------------------------------------------------------------------
# Las cuatro cierran el mismo modo de fallo con dos caras: una clave de OTRA
# FAMILIA que produce un numero plausible con la cita equivocada, y una ERRATA
# que salia como excepcion de PROGRAMA en vez de del expediente.

@pytest.mark.parametrize("clave,valor,en_el_mensaje", [
    # La carta CIRCULAR: le daba a un marco las constantes de la Carta 1 y la
    # Forma 1 con su Ks*S, mientras el paso de memoria imprimia que la carta
    # era «del bloque de CAJON» invocando el num. A.3 -- la regla que estaba
    # violando --. Es el unico punto donde la regla vinculante #5 se puede
    # hacer cumplir.
    ("embocadura_cajon", "circular_concreto_square_edge_headwall", "num. A.3"),
    # La ERRATA: salia como `KeyError` desnudo, que no desciende de
    # `ErrorProyecto`, y tumbaba la corrida entera.
    ("embocadura_cajon", "cajon_concreto_aleta_45_d04", "Claves admitidas"),
    # Un metal corrugado no es la analogia de un marco de CONCRETO.
    ("n_manning_cajon", "metal_corrugado_subdren", "a. Concreto"),
    ("n_manning_cajon", "concreto_afinad", "Claves admitidas"),
    # El escalar que la GUI sabe ofrecer: reventaba con `TypeError`. La misma
    # guardia que este modulo ya tenia escrita para 'espesor_pared_conducto'.
    ("secciones_cajon_normalizadas", 1.50, "serie de pares"),
    ("secciones_cajon_normalizadas", ((2.00, -1.50),), "POSITIVOS"),
])
def test_una_declaracion_de_otra_familia_o_con_errata_es_dato_invalido(
        clave, valor, en_el_mensaje):
    with declarados({**DECLARACIONES_CAJON, clave: valor}):
        with pytest.raises(DatoInvalidoError) as exc:
            _marco()
    assert exc.value.campo == clave
    assert en_el_mensaje in exc.value.motivo


def test_el_marco_no_toma_prestada_la_pared_del_tubo_de_su_misma_altura():
    """
    EL HALLAZGO MAS GRAVE DE LA AUDITORIA DE C5, y no era de texto: era un
    numero INSEGURO. `espesor_pared_conducto` tabula por diametro designado en
    mm de una norma de TUBERIA, y las alturas de marco plausibles caen sobre
    esa misma serie de 900 + 150k mm. Un marco de 2.00 x 1.50 m NO se detenia:
    recibia t = 0.150 m -- la pared del tubo de 1500 mm -- y con ella V7 se
    calculaba sobre un CILINDRO de 1.80 m, sobreestimando la seguridad
    alrededor de un 27 % (la subpresion real de un prisma es un 63 % mayor y
    el peso de relleno solo un 28 %).

    LA EXCEPCION CAMBIO EN C7 Y EL COMPORTAMIENTO NO. C5 la detuvo con
    `DatoFaltanteError` -- el revisor tenia que AÑADIR el dato, porque el
    proyecto no tenia donde ponerlo --. C7 abre `espesor_pared_cajon`, [A] de
    nivel perfil, y entonces el revisor ya no tiene que conseguir nada: tiene
    que DECIDIR. Esa es la frontera exacta que CLAUDE.md fija entre las dos
    excepciones, y por eso ahora es `CriterioPendienteError` -- la que la GUI
    muestra como pendiente declarable, con su ventana y su procedencia --.

    LO QUE NO CAMBIA es que se detiene, ni por que se detiene.
    """
    with declarados(DECLARACIONES_CAJON):
        marco = _marco()
        with pytest.raises(CriterioPendienteError) as exc:
            espesor_pared(marco, 1.50)
        assert exc.value.clave == "espesor_pared_cajon"
        # Y el tubo de la misma altura SI tiene fila: es lo que hace peligrosa
        # la coincidencia de series, y por eso se fija aqui al lado.
        assert espesor_pared(catalogo(TipoMaterial.CONCRETO_REFORZADO),
                             1.50) == pytest.approx(0.150, rel=REL_TRANSPORTE)
        # Y declarado, el marco NO lo lee de esa serie: lee lo adoptado.
        with declarados({"espesor_pared_cajon": 0.22}):
            assert espesor_pared(marco, 1.50) == pytest.approx(
                0.22, rel=REL_TRANSPORTE)


def test_la_progresion_del_marco_se_reconoce_con_tolerancia_y_no_con_igualdad():
    """
    CLAUDE.md prohibe comparar floats con `==` sin excepcion, y
    `_siguiente_seccion_cajon` los comparaba. Hoy acertaba siempre porque las
    dos secciones se reconstruyen del mismo criterio; deja de acertar en
    cuanto una llegue de otro sitio -- un JSON de tablero, la GUI, un
    round-trip por texto --, y entonces el bucle levantaria un
    `DatoInvalidoError` sobre una seccion que SI esta en la serie.
    """
    from modelos import SeccionRectangular
    with declarados(DECLARACIONES_CAJON):
        marco = _marco()
        # La misma seccion, con el ultimo bit movido.
        casi = SeccionRectangular(1.50 + 1e-13, 1.20 - 1e-13)
        siguiente = siguiente_seccion(marco, casi)
    assert (siguiente.B, siguiente.altura) == pytest.approx(
        (2.00, 1.50), rel=REL_TRANSPORTE)


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
