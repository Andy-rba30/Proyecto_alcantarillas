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
from modulos.M1_clasificacion import (CRITERIO_CATEGORIA_A, PERFILES,
                                      clasificar, clasificar_puntos,
                                      datos_pendientes, denominacion_por_luz,
                                      exigir_alcance, perfil_de,
                                      periodo_retorno_de, tr_de_categoria,
                                      tr_desde_riesgo, verificar_luz)
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
