"""
tests/test_M1_clasificacion.py
==============================
M1 contra la Fase 2: umbral binario de luz (Sec. 2.1), TR calculado con la
formula de la Tabla N 02 (Sec. 2.2) y perfil de familia (Sec. 2.3).

Los tests que mas importan son tres:

    - el umbral de luz es BINARIO y no tiene casilla 'ponton';
    - el TR sale de la FORMULA, no de una lista de valores de costumbre, y
      reproduce los 71 y 35 anios de CP-1;
    - la Familia A sin categoria declarada NO elige fila por su cuenta:
      detiene el calculo con CriterioPendienteError.

Valores de referencia: tests/fixtures/casos_patron.py (CP-1).
"""

import dataclasses
from pathlib import Path

import pytest

import criterios_adoptados as ca
from constantes_normativas import LUZ_MAX_ALCANTARILLA, RIESGO_ADMISIBLE
from modelos import (CategoriaTR, Clasificacion, CriterioPendienteError,
                     DatoFaltanteError, DatoInvalidoError, Denominacion,
                     DisenoNoFactibleError, ErrorProyecto, Familia,
                     Verificacion)
from modulos.M0_carga import cargar_puntos
from modulos.M1_clasificacion import (CRITERIO_CATEGORIA_A,
                                      CRITERIO_RIESGO_PROPIETARIO, PERFILES,
                                      clasificar, clasificar_puntos,
                                      datos_pendientes, denominacion_por_luz,
                                      exigir_alcance, perfil_de,
                                      periodo_retorno_de, tr_de_categoria,
                                      tr_desde_riesgo, verificar_luz)
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.fixtures.casos_patron import CP1_PERIODO_RETORNO

CSV_VALIDO = Path(__file__).resolve().parent / "ejemplo_puntos.csv"

# Luz del cruce por punto: no es columna de Sec. 1.2 y por eso la pone el test,
# como la pondria la GUI desde la topografia. 2.75 m es el canal del ejemplo de
# Sec. 2.1 que si es alcantarilla.
LUCES = {"A-01": 2.75, "A-02": 1.80, "B-01": 1.20, "C-01": 2.75}


@pytest.fixture
def puntos():
    return cargar_puntos(CSV_VALIDO)


@pytest.fixture
def punto_a(puntos):
    return puntos[0]                      # A-01, Familia A, area 850 ha


@pytest.fixture
def punto_b(puntos):
    return puntos[2]                      # B-01, Familia B


@pytest.fixture
def punto_c(puntos):
    return puntos[3]                      # C-01, Familia C


@pytest.fixture
def umbral_declarado():
    """
    Rellena temporalmente el criterio pendiente para probar la rama automatica.
    No se toca el archivo: el vacio sigue vacio fuera de este fixture.
    """
    original = ca.CRITERIOS[CRITERIO_CATEGORIA_A]
    ca.CRITERIOS[CRITERIO_CATEGORIA_A] = dataclasses.replace(original, valor=500.0)
    yield 500.0
    ca.CRITERIOS[CRITERIO_CATEGORIA_A] = original


# ---------------------------------------------------------------------------
# Sec. 2.1 - Umbral binario de luz
# ---------------------------------------------------------------------------

def test_el_umbral_de_luz_es_binario_y_no_existe_el_ponton():
    """Sec. 2.1: la normativa MTC solo tipifica alcantarilla y puente."""
    assert set(Denominacion) == {Denominacion.ALCANTARILLA, Denominacion.PUENTE}
    assert "ponton" not in {d.value for d in Denominacion}


@pytest.mark.parametrize("luz, esperada", [
    (2.75, Denominacion.ALCANTARILLA),    # canal del ejemplo de Sec. 2.1
    (0.90, Denominacion.ALCANTARILLA),
    (5.99, Denominacion.ALCANTARILLA),
    (6.00, Denominacion.PUENTE),          # el umbral pertenece al puente
    (12.0, Denominacion.PUENTE),          # canal de 12 m del ejemplo de Sec. 2.1
])
def test_la_denominacion_sale_del_umbral_de_6_metros(luz, esperada):
    assert denominacion_por_luz(luz) is esperada


def test_el_umbral_pertenece_al_lado_exigente():
    """
    Justo en 6.0 m es PUENTE (la tabla dice '>= 6.0'), y una luz que el punto
    flotante deja apenas por debajo tampoco se convierte en alcantarilla.
    """
    assert denominacion_por_luz(LUZ_MAX_ALCANTARILLA) is Denominacion.PUENTE
    casi = LUZ_MAX_ALCANTARILLA - 1e-12
    assert denominacion_por_luz(casi) is Denominacion.PUENTE


def test_la_luz_se_devuelve_como_verificacion_con_numeral():
    v = verificar_luz(2.75, "A-01")
    assert isinstance(v, Verificacion)
    assert v.cumple is True
    assert v.valor_admisible == pytest.approx(LUZ_MAX_ALCANTARILLA)
    assert v.numeral == "4.1.1.3.1 / 4.1.1.5.1"
    assert v.criterio_aplicado is None     # umbral [N] puro
    assert verificar_luz(12.0, "X-01").cumple is False


def test_sin_luz_no_se_supone_que_el_cruce_es_estrecho():
    """No es columna de Sec. 1.2: si no llega, falta el dato."""
    with pytest.raises(DatoFaltanteError) as exc:
        denominacion_por_luz(None, "A-01")
    assert exc.value.campo == "luz_m"
    assert exc.value.id_punto == "A-01"


@pytest.mark.parametrize("luz", [0.0, -3.0])
def test_una_luz_imposible_es_dato_invalido_y_no_faltante(luz):
    with pytest.raises(DatoInvalidoError) as exc:
        denominacion_por_luz(luz, "A-01")
    assert exc.value.campo == "luz_m"


def test_un_puente_detiene_el_pipeline_con_el_manual_al_que_se_remite(punto_a):
    clasificacion = clasificar(punto_a, 12.0)
    assert clasificacion.en_alcance is False
    with pytest.raises(DisenoNoFactibleError) as exc:
        exigir_alcance(clasificacion)
    assert exc.value.id_punto == "A-01"
    assert "PUENTE" in str(exc.value)
    assert "ponton" in str(exc.value)      # se declara que la categoria no existe


def test_una_alcantarilla_pasa_el_control_de_alcance(punto_a):
    clasificacion = clasificar(punto_a, 2.75, CategoriaTR.QUEBRADA_IMPORTANTE)
    assert exigir_alcance(clasificacion) is clasificacion


# ---------------------------------------------------------------------------
# Sec. 2.2 - Periodo de retorno
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("caso", CP1_PERIODO_RETORNO,
                         ids=[c["descripcion"] for c in CP1_PERIODO_RETORNO])
def test_la_formula_del_TR_reproduce_CP1(caso):
    """TR = 1 / (1 - (1-R)^(1/n)), Sec. 2.2."""
    obtenido = tr_desde_riesgo(caso["R"], caso["n"])
    assert obtenido == pytest.approx(caso["TR_esperado"], abs=caso["tolerancia"])


@pytest.mark.parametrize("categoria, anios", [
    (CategoriaTR.QUEBRADA_IMPORTANTE, 71),   # quebradas importantes / badenes
    (CategoriaTR.QUEBRADA_MENOR, 35),        # quebradas menores / cunetas
])
def test_el_TR_de_diseno_es_el_de_la_tabla_N02(categoria, anios):
    """La columna 'TR de diseno' publica el valor exacto redondeado al anio."""
    tr = tr_de_categoria(categoria)
    assert tr.anios == anios
    assert tr.exacto == pytest.approx(anios, abs=0.5)
    # El redondeo queda visible, no perdido: el exacto no es el publicado.
    assert tr.exacto != pytest.approx(float(tr.anios))
    # El numeral ya no viaja pelado: lleva el titulo literal de la tabla y su
    # caracter -- maximos RECOMENDADOS, con la decision del Propietario en la
    # nota al pie (NOR-HID-08).
    assert "3.6" in tr.numeral and "Tabla N 02" in tr.numeral
    assert "MAXIMOS RECOMENDADOS" in tr.numeral
    assert "Propietario" in tr.numeral


def test_el_TR_no_se_copia_sino_que_se_calcula_desde_R_y_n():
    """Si alguien 'arregla' el modulo devolviendo 71 fijo, este test lo delata."""
    for categoria in CategoriaTR:
        fila = RIESGO_ADMISIBLE[categoria.value]
        tr = tr_de_categoria(categoria)
        assert tr.R == pytest.approx(fila["R"])
        assert tr.n == fila["n"]
        assert tr.exacto == pytest.approx(tr_desde_riesgo(fila["R"], fila["n"]))


def test_las_categorias_son_las_filas_del_anexo_B():
    """CategoriaTR y RIESGO_ADMISIBLE no pueden divergir."""
    assert {c.value for c in CategoriaTR} == set(RIESGO_ADMISIBLE)


def test_no_se_adopta_ningun_TR_minimo_de_costumbre():
    """Sec. 2.2: 'no existe TR minimo obligatorio independiente'."""
    assert {tr_de_categoria(c).anios for c in CategoriaTR} == {71, 35}


@pytest.mark.parametrize("R, n", [(0.0, 25), (1.0, 25), (1.5, 25), (0.30, 0)])
def test_un_riesgo_imposible_no_devuelve_un_TR_plausible(R, n):
    with pytest.raises(DatoInvalidoError):
        tr_desde_riesgo(R, n)


@pytest.mark.parametrize("R, n", [
    (1e-16, 25),        # el caso de la ficha
    (1e-16, 15),        # la otra fila de la Tabla N 02
    (5e-18, 100),
    (1e-17, 1),
])
def test_un_riesgo_que_degenera_la_formula_es_dato_invalido_y_no_un_fallo(R, n):
    """
    MAT-D13, borde R -> 0. Con un riesgo suficientemente pequeño
    (1-R)^(1/n) redondea a 1.0 en doble precision y el denominador se anula.
    Antes salia como ZeroDivisionError: un fallo de PROGRAMA, fuera de la
    taxonomia ErrorProyecto que CLAUDE.md exige para todo problema del
    expediente, y que la GUI muestra con traza en vez de como "corrige esta
    celda".

    El limite depende de n (esta en R ~ n*eps/2), y por eso la guarda mira el
    DENOMINADOR y no un umbral escrito sobre R: un umbral seria un literal de
    precision disfrazado de valor normativo, y ademas seria distinto para
    cada vida util.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        tr_desde_riesgo(R, n)
    assert exc.value.campo == "R"
    assert "doble precision" in str(exc.value)


def test_una_vida_util_no_finita_no_devuelve_un_TR_que_no_es_numero():
    """
    La guarda del denominador se escribe EN POSITIVO y negada. Con
    `denominador <= 0` un NaN la atravesaba -- es falso frente a `<=` igual
    que frente a `>` -- y `tr_desde_riesgo(0.2, nan)` DEVOLVIA nan: el mismo
    agujero que la guarda existe para cerrar, dentro de la funcion que se
    acababa de endurecer.
    """
    with pytest.raises(DatoInvalidoError):
        tr_desde_riesgo(0.2, float("nan"))
    with pytest.raises(DatoInvalidoError):
        tr_desde_riesgo(0.2, float("inf"))


def test_el_riesgo_pequeno_pero_representable_sigue_dando_un_TR():
    """
    La guarda no puede llevarse por delante un riesgo pequeño LEGITIMO: con
    R = 1e-9 y n = 25 la formula sigue teniendo solucion y el TR es enorme,
    que es la respuesta correcta -- un riesgo casi nulo exige un periodo de
    retorno casi infinito.
    """
    TR = tr_desde_riesgo(1e-9, 25)
    assert TR > 0
    assert TR == pytest.approx(25 / 1e-9, rel=1e-6), (
        "para R muy pequeño el TR tiende a n/R")


def test_una_categoria_que_no_es_fila_de_la_tabla_se_rechaza():
    with pytest.raises(DatoInvalidoError) as exc:
        tr_de_categoria("ponton")
    assert exc.value.campo == "categoria_tr"


# ---------------------------------------------------------------------------
# El vacio de la Familia A: 71 o 35, y la hoja de ruta no dice cual
# ---------------------------------------------------------------------------

def test_familia_A_sin_categoria_detiene_el_calculo(punto_a):
    """
    Sec. 2.3 dice 'TR 71 o 35 anios' sin regla de asignacion. M1 no elige por
    su cuenta: lee el criterio, que sigue vacio, y se detiene.
    """
    with pytest.raises(CriterioPendienteError) as exc:
        periodo_retorno_de(punto_a)
    assert exc.value.clave == CRITERIO_CATEGORIA_A
    assert exc.value.mensaje_gui == f"falta declarar: {CRITERIO_CATEGORIA_A}"
    assert isinstance(exc.value, ErrorProyecto)
    # Nadie relleno el vacio al pasar por aqui.
    assert ca.CRITERIOS[CRITERIO_CATEGORIA_A].valor is None


def test_familia_A_con_categoria_declarada_no_necesita_el_criterio(punto_a):
    """La salida documentada: se clasifica el cauce y se pasa la categoria."""
    tr = periodo_retorno_de(punto_a, CategoriaTR.QUEBRADA_IMPORTANTE)
    assert tr.anios == 71
    assert tr.categoria is CategoriaTR.QUEBRADA_IMPORTANTE
    assert tr.id_punto == "A-01"
    assert "declarada" in tr.fundamento

    menor = periodo_retorno_de(punto_a, "quebrada_menor")
    assert menor.anios == 35


def test_con_umbral_declarado_el_area_de_cuenca_decide(puntos, umbral_declarado):
    """
    El area es el dato que Sec. 1.1 llama 'solo clasificador'. Con umbral de
    500 ha: A-01 (850 ha) es importante y A-02 (210 ha) es menor.
    """
    a01, a02 = puntos[0], puntos[1]
    assert periodo_retorno_de(a01).categoria is CategoriaTR.QUEBRADA_IMPORTANTE
    assert periodo_retorno_de(a01).anios == 71
    assert periodo_retorno_de(a02).categoria is CategoriaTR.QUEBRADA_MENOR
    assert periodo_retorno_de(a02).anios == 35


def test_el_criterio_del_umbral_queda_registrado_como_usado(punto_a):
    """M11 debe poder decir que el calculo intento usarlo."""
    ca._USADOS.discard(CRITERIO_CATEGORIA_A)
    with pytest.raises(CriterioPendienteError):
        periodo_retorno_de(punto_a)
    assert CRITERIO_CATEGORIA_A in ca._USADOS


def test_un_puente_no_dispara_el_criterio_pendiente(punto_a):
    """
    Un punto fuera de alcance no debe mostrarse en la GUI como 'falta declarar
    el umbral': el problema es que el cruce es un puente.
    """
    clasificacion = clasificar(punto_a, 12.0)       # sin categoria: no lanza
    assert clasificacion.periodo_retorno.procede is False
    assert clasificacion.periodo_retorno.anios is None
    assert "puente" in clasificacion.periodo_retorno.fundamento


# ---------------------------------------------------------------------------
# Sec. 2.3 - Familias
# ---------------------------------------------------------------------------

def test_hay_perfil_para_las_tres_familias():
    assert set(PERFILES) == set(Familia)
    for familia in Familia:
        assert perfil_de(familia).familia is familia
        assert perfil_de(familia.value) is perfil_de(familia)


def test_la_familia_A_lleva_la_aceptacion_V1_V2_V4_V5():
    """Sec. 2.3, literal."""
    assert perfil_de(Familia.A).verificaciones_aceptacion == ("V1", "V2", "V4", "V5")


def test_las_familias_sin_conjunto_declarado_no_lo_inventan():
    """
    Sec. 2.3 solo declara el conjunto de aceptacion de la Familia A. None
    significa 'no declarado', y no debe confundirse con una tupla vacia, que
    se leeria como 'ninguna verificacion'.
    """
    for familia in (Familia.B, Familia.C):
        assert perfil_de(familia).verificaciones_aceptacion is None


def test_la_familia_B_tiene_fila_fija_y_no_pregunta_nada(punto_b):
    """Sec. 2.3: alcantarilla de alivio -> descarga de cunetas -> TR 35."""
    assert perfil_de(Familia.B).categoria_tr is CategoriaTR.QUEBRADA_MENOR
    tr = periodo_retorno_de(punto_b)
    assert tr.anios == 35
    assert tr.procede is True


def test_la_familia_B_no_admite_la_otra_fila(punto_b):
    with pytest.raises(DatoInvalidoError) as exc:
        periodo_retorno_de(punto_b, CategoriaTR.QUEBRADA_IMPORTANTE)
    assert exc.value.id_punto == "B-01"


def test_la_familia_C_no_tiene_periodo_de_retorno(punto_c):
    """Sec. 2.3: su Q es el de diseno del canal (ANA / Junta), no un TR."""
    tr = periodo_retorno_de(punto_c)
    assert tr.procede is False
    assert tr.anios is None and tr.categoria is None
    assert "ANA" in tr.fundamento


def test_pedir_el_TR_de_la_familia_C_lanza_en_vez_de_devolver_None(punto_c):
    tr = periodo_retorno_de(punto_c)
    with pytest.raises(DatoFaltanteError) as exc:
        tr.exigir_anios()
    assert exc.value.id_punto == "C-01"


def test_el_TR_que_procede_se_puede_exigir_sin_sobresaltos(punto_b):
    assert periodo_retorno_de(punto_b).exigir_anios() == 35


def test_la_familia_C_del_ejemplo_llega_con_su_caudal_pendiente(punto_c):
    """C-01 trae Q_m3s vacio por el Tablero 3.1: se marca, no se rechaza."""
    assert datos_pendientes(punto_c) == ("Q_m3s",)
    assert datos_pendientes(punto_c) == tuple(
        c for c in perfil_de(Familia.C).campos_requeridos if c in
        punto_c.pendientes_externos)


def test_una_familia_A_completa_no_tiene_pendientes(punto_a):
    assert datos_pendientes(punto_a) == ()


def test_el_umbral_de_terraplen_de_la_familia_B_se_declara_y_se_remite_a_M10():
    """
    Sec. 2.3 menciona bordillo y bajantes segun la altura del terraplen. M1 no
    lo resuelve ni se inventa un valor: lo deja declarado como nota y remite a
    la Fase 10, que es donde estan el espaciamiento y el drenaje longitudinal.
    """
    notas = " ".join(perfil_de(Familia.B).notas)
    assert "M10" in notas and "bordillo" in notas
    assert "curva peraltada" in notas          # el dato que Sec. 1.2 no trae


# ---------------------------------------------------------------------------
# Clasificacion completa
# ---------------------------------------------------------------------------

def test_clasificar_el_ejemplo_completo(puntos):
    categorias = {"A-01": CategoriaTR.QUEBRADA_IMPORTANTE,
                  "A-02": CategoriaTR.QUEBRADA_MENOR}
    clasificaciones = clasificar_puntos(puntos, LUCES, categorias)

    assert [c.punto.id for c in clasificaciones] == ["A-01", "A-02", "B-01", "C-01"]
    assert all(isinstance(c, Clasificacion) for c in clasificaciones)
    assert all(c.en_alcance for c in clasificaciones)
    assert [c.periodo_retorno.anios for c in clasificaciones] == [71, 35, 35, None]
    assert [c.perfil.familia for c in clasificaciones] == [
        Familia.A, Familia.A, Familia.B, Familia.C]


def test_clasificar_un_punto_sin_luz_en_el_mapa(puntos):
    """Si la GUI no trae la luz de un id, falta el dato de ese punto."""
    with pytest.raises(DatoFaltanteError) as exc:
        clasificar_puntos(puntos, {"B-01": 1.20})
    assert exc.value.campo == "luz_m"
    assert exc.value.id_punto == "A-01"


def test_la_clasificacion_es_inmutable(punto_b):
    clasificacion = clasificar(punto_b, 1.20)
    with pytest.raises(dataclasses.FrozenInstanceError):
        clasificacion.denominacion = Denominacion.PUENTE


# ===========================================================================
# C09 / SIS-F-10 - las guardas de expediente de M1, alcanzadas de verdad
# ===========================================================================
#
# La auditoria de sistema conto trece `raise` de ErrorProyecto sin ninguna
# corrida que los ejecutara, y M1 ponia tres de ellos. Un `raise` sin test no
# garantiza nada de lo que la GUI necesita: ni la CLASE de excepcion (que es
# lo que separa "problema del expediente" de "fallo del programa"), ni el
# CAMPO (que es lo que la GUI subraya), ni un motivo que diga POR QUE.
#
# Los tests de este bloque alcanzan cada guarda con una llamada normal y
# afirman las tres cosas. La cuarta guarda de M1 -- la fila sin entrada en
# RIESGO_ADMISIBLE -- no se alcanza: se demuestra inalcanzable, que es el
# cierre correcto de una guarda defensiva (SIS-B-23).


@pytest.mark.parametrize("luz, motivo_esperado", [
    ("dos metros", "no es un numero"),      # texto que no convierte
    ("", "no es un numero"),                # celda de la GUI en blanco
    (object(), "no es un numero"),          # ni siquiera es convertible
    ([2.75], "no es un numero"),            # la lista de luces, sin desempacar
])
def test_una_luz_que_no_es_un_numero_se_detiene_con_el_campo(
        punto_a, luz, motivo_esperado):
    """
    Falla si `_luz_valida` deja pasar un valor no convertible -- por ejemplo
    si alguien sustituye el `float(luz_m)` por un `try/except` que devuelve
    un default --, o si la excepcion pierde el campo o el motivo: la GUI
    subraya la casilla por `campo` y el revisor corrige por el motivo.

    Es DatoInvalidoError y no DatoFaltanteError porque la luz SI llego: hay
    que corregirla, no añadirla (CLAUDE.md, taxonomia de excepciones).
    """
    with pytest.raises(DatoInvalidoError) as exc:
        clasificar(punto_a, luz)

    assert exc.value.campo == "luz_m"
    assert exc.value.id_punto == punto_a.id
    assert motivo_esperado in exc.value.motivo


@pytest.mark.parametrize("declaracion, valor_rechazado, motivo_esperado", [
    ({"R": 0.50}, 0.50, "COMO MAXIMO"),      # mas riesgo del recomendado
    ({"n": 10}, 10, "vida util menor"),      # menos vida util que la tabla
])
def test_el_propietario_no_puede_ablandar_la_tabla_N_02(
        declaracion, valor_rechazado, motivo_esperado):
    """
    NOR-HID-08: la Tabla N 02 publica VALORES MAXIMOS RECOMENDADOS y su nota
    al pie deja la decision al Propietario. `_riesgo_del_propietario` solo
    admite ENDURECER: R menor o n mayor suben el TR y el caudal de diseño.

    Falla si la declaracion del Propietario deja de compararse contra la fila
    de la tabla -- que es lo que convierte esta via en un refinamiento y no
    en un portillo para bajar el caudal de diseño sin decirlo.

    Los maximos NO se escriben aqui: salen de RIESGO_ADMISIBLE, que es donde
    viven como [N].
    """
    fila = "quebrada_importante"
    ca.establecer_valor_dinamico(CRITERIO_RIESGO_PROPIETARIO,
                                 {fila: declaracion})
    try:
        with pytest.raises(DatoInvalidoError) as exc:
            tr_de_categoria(fila)
    finally:
        ca.quitar_valor_dinamico(CRITERIO_RIESGO_PROPIETARIO)

    assert exc.value.campo == CRITERIO_RIESGO_PROPIETARIO
    assert exc.value.valor == pytest.approx(valor_rechazado,
                                            rel=REL_TRANSPORTE)
    assert motivo_esperado in exc.value.motivo
    # El motivo tiene que decir contra QUE techo se rechazo, con el numero de
    # la tabla dentro: sin el, el revisor no sabe hasta donde puede declarar.
    assert str(RIESGO_ADMISIBLE[fila]["R" if "R" in declaracion else "n"]) \
        in exc.value.motivo


def test_una_declaracion_que_endurece_la_tabla_N_02_si_se_admite():
    """
    La cara opuesta del test anterior, y la que demuestra que la guarda no es
    un "no se puede declarar nada": bajar R y subir n sube el TR, que es la
    direccion segura, y el fundamento tiene que dejar dicho que los valores
    los declaro el Propietario.
    """
    fila = "quebrada_importante"
    maximos = RIESGO_ADMISIBLE[fila]
    ca.establecer_valor_dinamico(
        CRITERIO_RIESGO_PROPIETARIO,
        {fila: {"R": maximos["R"] / 2, "n": maximos["n"] * 2}})
    try:
        con_declaracion = tr_de_categoria(fila)
    finally:
        ca.quitar_valor_dinamico(CRITERIO_RIESGO_PROPIETARIO)

    por_defecto = tr_de_categoria(fila)
    assert con_declaracion.anios > por_defecto.anios
    assert CRITERIO_RIESGO_PROPIETARIO in con_declaracion.fundamento


@pytest.mark.parametrize("familia", ["D", "a", "", "Familia A", 1])
def test_una_familia_que_no_es_de_la_Sec_2_3_se_detiene_con_el_campo(familia):
    """
    Falla si `perfil_de` deja de validar la familia y revienta mas adentro con
    un KeyError sobre PERFILES: eso seria un fallo de PROGRAMA para la GUI, y
    lo que hay es un dato del expediente mal escrito.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        perfil_de(familia)

    assert exc.value.campo == "familia"
    # El motivo enumera las familias reales, leidas del enum: si mañana se
    # añade una cuarta, el mensaje la lista sin que nadie lo edite.
    for valida in Familia:
        assert valida.value in exc.value.motivo


# --- guarda defensiva: se demuestra inalcanzable, no se alcanza ------------

def test_ninguna_fila_de_la_Tabla_N_02_se_queda_sin_riesgo_admisible():
    """
    SIS-B-23, aplicado a la segunda guarda de `_categoria`: el `raise` para
    una CategoriaTR sin entrada en RIESGO_ADMISIBLE no lo alcanza ninguna
    llamada, porque el enum y la tabla cubren exactamente las mismas filas.
    Esa es la razon por la que no tiene test que lo ejecute, y este test es
    la razon escrita: mientras pase, la guarda es inalcanzable por
    construccion; el dia que alguien añada una fila al enum sin añadirla a la
    tabla, falla AQUI -- con el nombre de la fila huerfana -- en vez de
    esperar a que un punto de una obra caiga en el `raise`.
    """
    filas_del_enum = {c.value for c in CategoriaTR}
    filas_de_la_tabla = set(RIESGO_ADMISIBLE)

    assert filas_del_enum == filas_de_la_tabla, (
        "CategoriaTR y RIESGO_ADMISIBLE dejaron de cubrir las mismas filas: "
        f"sin tabla {sorted(filas_del_enum - filas_de_la_tabla)}, "
        f"sin enum {sorted(filas_de_la_tabla - filas_del_enum)}")

    # Y la consecuencia observable: toda fila del enum resuelve su TR.
    for fila in CategoriaTR:
        assert tr_de_categoria(fila).anios > 0


# ---------------------------------------------------------------------------
# MAT-D13, segunda vuelta: el mensaje nombra el PAR, y n en forma positiva
# ---------------------------------------------------------------------------

def test_el_mensaje_del_borde_de_tr_nombra_los_dos_datos():
    """
    La degeneracion es del par (R, n) y no de uno solo: con n grande, una R
    perfectamente sana la provoca. La primera version acusaba siempre a 'R' y
    mandaba a corregir el dato equivocado la mitad de las veces; escribir un
    discriminante seria falsa precision, porque no hay umbral que separe "culpa
    de R" de "culpa de n". Se dicen los dos.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        tr_desde_riesgo(1e-16, 25)
    mensaje = str(exc.value)
    assert "R = 1e-16" in mensaje and "n = 25" in mensaje
    assert "cualquiera de los dos lados" in mensaje


def test_una_vida_util_nan_no_atraviesa_la_guarda():
    """
    `n <= 0` es FALSO para un NaN y lo dejaba pasar hasta la formula. La
    condicion escrita en positivo y negada si lo atrapa, y lo atrapa acusando
    a 'n', que es el dato que hay que corregir.
    """
    with pytest.raises(DatoInvalidoError) as exc:
        tr_desde_riesgo(0.35, float("nan"))
    assert exc.value.campo == "n"


def test_una_vida_util_enorme_tambien_degenera_y_se_dice():
    with pytest.raises(DatoInvalidoError) as exc:
        tr_desde_riesgo(0.35, 10 ** 300)
    assert "degenera" in str(exc.value)


# ---------------------------------------------------------------------------
# SIS-C-12: el ejemplo del docstring, EJECUTADO
# ---------------------------------------------------------------------------

def _bloque_uso(ruta: Path) -> str:
    """El bloque `Uso` del docstring de modulo, tal cual esta escrito."""
    import ast as _ast
    import re as _re
    import textwrap as _textwrap
    doc = _ast.get_docstring(_ast.parse(ruta.read_text(encoding="utf-8")))
    m = _re.search(r"^Uso\n-+\n(.*?)(?=\n\S|\Z)", doc, _re.S | _re.M)
    assert m, f"{ruta.name} perdio su bloque Uso"
    return _textwrap.dedent(m.group(1))


def test_el_ejemplo_del_docstring_de_M1_ejecuta_y_da_los_TR_del_fixture():
    """
    SIS-C-12, y el hallazgo se quedaba corto: no era solo que el ejemplo diera
    las luces sin la salvedad que si lleva `LUCES` aqui arriba --- es que
    llamaba a `clasificar_puntos` con dos de sus tres argumentos y abortaba en
    el primer punto con `CriterioPendienteError`. Un ejemplo que no corre es
    peor que no tener ejemplo: el lector culpa a su entorno.

    Este test EJECUTA el bloque tal como esta escrito en el docstring --- lo
    extrae del archivo, no lo copia --- para que no puedan volver a divergir.
    Los TR que asegura son los mismos de `test_clasificar_el_ejemplo_completo`.

    Solo se ejercita el de M1. Los bloques `Uso` de los otros doce modulos son
    FRAGMENTOS a proposito (parten de un `resultado` que el llamante ya tiene)
    y ejecutarlos exigiria inventarles un contexto, que es justo lo que este
    test evita. Queda anotado en `docs/decisiones_diferidas.md`.
    """
    ruta = Path(__file__).resolve().parents[1] / "src" / "modulos" / "M1_clasificacion.py"
    ambito = {"__name__": "__uso_de_M1__"}
    exec(compile(_bloque_uso(ruta), str(ruta), "exec"), ambito)   # noqa: S102

    clasificaciones = ambito["clasificar_puntos"](
        ambito["puntos"], ambito["luces"], ambito["categorias"])
    assert [c.punto.id for c in clasificaciones] == ["A-01", "A-02", "B-01", "C-01"]
    assert [c.periodo_retorno.anios for c in clasificaciones] == [71, 35, 35, None]


def test_el_ejemplo_del_docstring_de_M1_declara_que_los_ids_son_del_fixture():
    """
    La otra mitad de SIS-C-12: los ids A-01..C-01 salen de
    `tests/ejemplo_puntos.csv` y no son puntos del expediente. El ejemplo
    tiene que decirlo, porque quien lo lea creera que son cuatro cruces
    reales de La Union.
    """
    ruta = Path(__file__).resolve().parents[1] / "src" / "modulos" / "M1_clasificacion.py"
    uso = " ".join(_bloque_uso(ruta).replace("#", " ").split()).lower()
    assert "fixture" in uso, (
        "el ejemplo volvio a dar los ids como si fueran del expediente")
    assert "no es columna de sec. 1.2" in uso, (
        "el ejemplo volvio a dar la luz sin decir que no sale del CSV")
