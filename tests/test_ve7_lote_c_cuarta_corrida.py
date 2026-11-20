"""
tests/test_ve7_lote_c_cuarta_corrida.py
=======================================
VE-7, lote C, item C6 (VE5GUI-47, «Abierto: los 32 fundamentos que ninguna
corrida de referencia ejercita»; decision del consultor Fable, triaje VE-7,
2026-11-20): una CUARTA corrida de referencia, `materiales_y_ramas`, con
entradas de PRUEBA rotuladas, que recorre el TMC y el HDPE hasta la Fase 8,
el cabezal ciclopeo, el filtro y la socavacion de HEC-14 y el metodo racional
modificado (`FH.RM_*`), entre otras ramas.

Medido al cerrar el item: con las tres corridas de VE-6 quedaban 39 de 154
fundamentos sin paso; con la cuarta quedan 17. El censo de abajo los nombra
con la razon por la que esta corrida no los alcanza. `docs/indice_formulas.md`
NO se regenera aqui: lo sella el integrador.
"""

from pathlib import Path

import pytest

from src import indice_formulas as ind
from src.normativa import registro as _registro

RAIZ = Path(__file__).resolve().parents[1]
NOMBRE = "materiales_y_ramas"

# Lo que la cuarta corrida ejercita y ninguna de las otras tres alcanzaba.
EJERCITA_LA_CUARTA = frozenset({
    "F8.TMC_AREA", "F8.TMC_COSTURA", "F8.TMC_FF", "F8.TMC_ASD",
    "F8.HDPE_EMPUJE", "F8.HDPE_PANDEO", "F8.HDPE_DEFLEXION", "F8.HDPE_FF",
    "F9.CICLOPEO", "F6.FILTRO", "F6.SOCAVACION",
    "FH.RM_INTENSIDAD", "FH.RM_C", "FH.RM_CAUDAL",
    "F0.LICUEFACCION", "F11.ACERO", "F3.DUR.SUELO_FUNDACION",
    "F4.HORIZONTAL", "F4.N_CAJON_IN_SITU", "F9.ARM_DURABILIDAD",
    "F9.DIMENSIONADO_PANTALLA", "F9.GLOBAL_DECLARADA",
})

# Los que ninguna de las cuatro emite como PASO, con la razon.
# (a) Entran como `EleccionDeProyecto.fundamento_id` y no como paso: las
#     corridas los EMITEN, pero el indice solo cuenta pasos.
COMO_ELECCION = frozenset({"F3.D_EXTERIOR", "F5.V2b.REGIMEN", "F5.V7_FILA",
                           "F5.V7_NIVEL", "FH.FACTOR_P24"})
# (b) Entra por el BLOQUE FIJO de umbrales que M11 imprime siempre
#     (`constantes_normativas.UMBRALES_DE_VERIFICACION`, codigo `D_min`):
#     dictamen Fable (i-b), no se retira.
POR_BLOQUE_FIJO = frozenset({"F3.D_MIN"})
# (c) LA QUINTA (`regimenes_alternos`, dictamen Fable (i-c)): lo que ejercita
#     y ninguna de las cuatro primeras alcanzaba.
QUINTA = "regimenes_alternos"
EJERCITA_LA_QUINTA = frozenset({
    "F3.SELVA_ALTA_TMC", "F4.N_CAJON", "F4.PISO_HW", "F5.V1.RECEPTOR",
    "F5.V5_PERFIL", "F5.V8.DESBORDE", "F6.CAIDA", "F6.CAIDA_ESTANQUE",
    "F8.COBERTURA",
})
# (d) Sin ninguna puerta en las cinco: (razon MEDIDA, test que mide la
#     formula como archivo::test). Nada se forzo con datos invalidos.
SIN_EJERCITAR = {
    "F6.TW_ALTO": (
        "TW sobre la clave a la salida (Figura 10.3 de HEC-14): con "
        "'borde_libre_bajo_tw_ahogante' = no_cumple (archivo, y el regimen "
        "que F5.V1.RECEPTOR necesita) V1 descarta todo escalon con TW > "
        "(y/D)max*D; medido en A-03 de la quinta: TW = 1.0 m adopta Ø 1.35 m",
        "tests/test_ve5_m6_figura_10_3.py::"
        "test_la_fase_6_con_el_tw_alto_forma_la_envolvente"),
    "F9.DIMENSIONADO_PERALTE": (
        "peralte de la zapata por armado: por `correr_referencia` (y por "
        "`validacion_integral.correr_juego` fuera de pytest) la zapata de "
        "A-01 del juego de T-11 conserva el peralte de la regla "
        "(`intentos_de_peralte` vacio, medido); el test de abajo lo ve "
        "crecer bajo la suite: divergencia abierta, ficha VE7C-06",
        "tests/test_ve3_peralte_cabezal.py::"
        "test_el_peralte_crece_solo_donde_hace_falta"),
}
# Trinquete: SOLO DECRECE. El dictamen fijo 5 como tope; medido, 2.
MAX_SIN_EJERCITAR = 2


@pytest.fixture(scope="module")
def emitidos():
    por_corrida = {}
    for c in ind.CORRIDAS_DE_REFERENCIA:
        informe = ind.correr_referencia(c)
        pasos = ind.pasos_de_la_corrida(informe)
        por_corrida[c.nombre] = (
            {p.fundamento_id for p in pasos},
            {e.fundamento_id for p in pasos for e in p.elecciones},
            informe)
    return por_corrida


def test_C6_hay_cinco_corridas_y_la_cuarta_es_de_prueba_rotulada():
    nombres = [c.nombre for c in ind.CORRIDAS_DE_REFERENCIA]
    assert nombres == ["perfil_guia", "expediente_cabezal",
                       "hidrologia_calculada", NOMBRE, QUINTA]
    cuarta = ind.CORRIDAS_DE_REFERENCIA[3]
    assert cuarta.alcance == "expediente"
    assert cuarta.rotulo.startswith("DATOS DE PRUEBA, NO DEL PROYECTO")
    leeme = cuarta.carpeta.joinpath("LEEME.md").read_text(encoding="utf-8")
    assert leeme.startswith("# DATOS DE PRUEBA, NO DEL PROYECTO")
    for f in EJERCITA_LA_CUARTA:
        if f.startswith("F8."):
            continue   # los ocho de la Fase 8 se nombran por familia
        assert f in leeme, f
    assert cuarta.cuencas is not None and cuarta.estacion is not None


def test_C6_la_cuarta_ejercita_lo_que_las_tres_primeras_no(emitidos):
    otras = set().union(*(e for n, (e, _el, _i) in emitidos.items()
                          if n not in (NOMBRE, QUINTA)))
    propios, _el, _i = emitidos[NOMBRE]
    assert EJERCITA_LA_CUARTA <= propios
    assert not (EJERCITA_LA_CUARTA & otras)


def test_ic_la_quinta_es_de_prueba_y_ejercita_lo_que_las_cuatro_no(emitidos):
    quinta = ind.CORRIDAS_DE_REFERENCIA[4]
    assert quinta.alcance == "expediente"
    assert quinta.rotulo.startswith(
        "DATOS DE PRUEBA, NO DEL PROYECTO, NO ES UN DISEÑO VÁLIDO")
    leeme = quinta.carpeta.joinpath("LEEME.md").read_text(encoding="utf-8")
    assert leeme.startswith("# DATOS DE PRUEBA, NO DEL PROYECTO")
    for f in EJERCITA_LA_QUINTA:
        assert f in leeme, f
    def _puertas(nombres):
        pasos = tuple(p for n in nombres
                      for p in ind.pasos_de_la_corrida(emitidos[n][2]))
        return set().union(*ind.puertas_de_los_fundamentos(pasos).values())
    cuatro = _puertas([c.nombre for c in ind.CORRIDAS_DE_REFERENCIA[:4]])
    propia = _puertas([QUINTA])
    assert EJERCITA_LA_QUINTA <= propia
    assert not (EJERCITA_LA_QUINTA & cuatro)


def test_ic_la_quinta_no_cumple_solo_lo_medido(emitidos):
    *_, informe = emitidos[QUINTA]
    assert {pid: set(r) for pid, r in
            ind.raices_que_no_cumplen(informe).items()} == {"C-01": {"A2"}}
    por_id = {p.punto.id: p for p in informe.puntos}
    assert por_id["A-03"].resultado.seccion.etiqueta() == "Ø 1.35 m"
    assert not por_id["A-06"].dimensionado


def test_C6_la_cuarta_dimensiona_en_TMC_y_HDPE_con_cabezal_ciclopeo(emitidos):
    *_ , informe = emitidos[NOMBRE]
    por_id = {p.punto.id: p for p in informe.puntos}
    assert por_id["A-01"].resultado.material.tipo.value == "tmc"
    assert por_id["A-02"].resultado.material.tipo.value == "hdpe"
    assert por_id["A-02"].cabezal.entrada.tipo == "gravedad_ciclopeo"
    assert por_id["A-03"].caudal is not None and por_id["A-03"].caudal.calculado
    assert por_id["C-01"].dimensionado


def test_C6_los_que_quedan_sin_ejercitar_son_los_censados(emitidos):
    """
    La medida que pide el item: cuantos fundamentos ninguna corrida emite.
    Eran 39 de 154 sin paso con las tres de VE-6; 17 con la cuarta. Desde el
    dictamen Fable el indice cuenta las tres puertas (i-a) y hay una quinta
    corrida (i-c): cinco entran como eleccion, uno por el bloque fijo, y
    quedan DOS sin ninguna puerta, censados con su razon medida.
    """
    reg = _registro.construir()
    pasos = set().union(*(e for e, _el, _i in emitidos.values()))
    elecciones = set().union(*(el for _e, el, _i in emitidos.values()))
    sin_paso = {f.id for f in reg.fundamentos} - pasos
    assert sin_paso == COMO_ELECCION | POR_BLOQUE_FIJO | set(SIN_EJERCITAR) \
        | {"F4.PISO_HW"}           # entra como eleccion, desde la quinta
    assert COMO_ELECCION | {"F4.PISO_HW"} <= elecciones
    puertas = ind.puertas_de_los_fundamentos(
        tuple(p for c in ind.CORRIDAS_DE_REFERENCIA
              for p in ind.pasos_de_la_corrida(emitidos[c.nombre][2])))
    assert POR_BLOQUE_FIJO <= puertas[ind.PUERTA_BLOQUE_FIJO]
    sin_puerta = ({f.id for f in reg.fundamentos}
                  - set().union(*puertas.values()))
    assert sin_puerta == set(SIN_EJERCITAR)
    assert len(sin_puerta) <= MAX_SIN_EJERCITAR


def test_ic_cada_razon_del_censo_nombra_un_test_que_existe():
    import ast
    for f, (razon, prueba) in SIN_EJERCITAR.items():
        assert razon.strip(), f
        archivo, funcion = prueba.split("::")
        arbol = ast.parse((RAIZ / archivo).read_text(encoding="utf-8"))
        assert funcion in {n.name for n in ast.walk(arbol)
                           if isinstance(n, ast.FunctionDef)}, (f, prueba)


# --- dictamen Fable, C6.b --- lo que NO cumple en la cuarta, por la raiz del
# codigo, medido: la corrida ejercita formulas y no es un diseño.
NO_CUMPLE_EN_LA_CUARTA = {
    "A-01": {"A7", "E1-LRFD", "E3-LRFD"},
    "A-02": {"C2", "C3", "C7", "C8", "E1-LRFD", "E3-LRFD"},
    "C-01": {"A2", "A7", "E1-LRFD", "E3-LRFD"},
}


def test_C6_lo_que_no_cumple_es_exactamente_lo_censado(emitidos):
    *_, informe = emitidos[NOMBRE]
    medido = {pid: set(r) for pid, r in ind.raices_que_no_cumplen(informe).items()}
    assert medido == NO_CUMPLE_EN_LA_CUARTA
    a03 = next(p for p in informe.puntos if p.punto.id == "A-03")
    assert not a03.dimensionado
    assert any(b.tipo.value == "DisenoNoFactibleError" for b in a03.bloqueos)
    linea = ind.verificaciones_que_no_cumplen(informe)
    assert linea.startswith(ind.ROTULO_NO_CUMPLEN)
    assert "NO ES UN DISEÑO VÁLIDO" in ind.CORRIDAS_DE_REFERENCIA[3].rotulo
