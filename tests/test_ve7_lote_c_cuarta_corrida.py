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

# VE-7 fix-suite: desde que el juego de T-11 declara la licuefaccion del EMS
# y los dos criterios de los metrados (datos de prueba: sin ellos la
# validacion integral no cerraba), la TERCERA corrida (`hidrologia_calculada`,
# que es ese juego materializado) tambien emite estos dos. La cuarta los
# sigue ejercitando; ya no es la unica.
TAMBIEN_LA_TERCERA = frozenset({"F0.LICUEFACCION", "F11.ACERO"})

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
    "FH.C_SUBAREAS": (
        "C ponderado por subareas (VE-7 lote B, B10, ficha VE7B-06): solo "
        "sale con la columna opcional `subareas` del CSV de cuencas, y "
        "ningun `cuencas.csv` de las corridas de referencia la trae "
        "(medido); entro al censo al integrar el lote B",
        "tests/test_ve7_lote_b_subareas.py::"
        "test_cada_C_es_la_celda_de_la_tabla_08"),
}
# `F9.DIMENSIONADO_PERALTE` SALIO DEL CENSO al integrar el lote A (ficha
# VE7C-06): lo emite la zapata de los ALEROS (`9.3.e.s.alero`, A-04 de la
# quinta y la cuarta). La de la zapata del cabezal (`9.3.p.*`) sigue sin
# puerta, y no por pytest ni por conftest: con 'momento_talon_cabezal' =
# «exacto» (archivo, decision 9 del dueño, VE-3.15; AASHTO 11.6.1.2 y
# 10.6.5) el talon de la salida de A-01 del juego de T-11 pide M_u = 76.8
# kN·m/m en vez de los 239.3 del peso entero, A1/A2 del talon cumplen con
# el peralte de la regla y el bucle no entra; `test_ve3_peralte_cabezal` lo
# ve crecer porque corre con los valores PREVIOS a VE-3.15
# (`valores_previos_ve3_15`, «peso_entero»). Lo fija
# `test_ic_el_peralte_sin_puerta_es_por_el_metodo_del_talon`.
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
    assert EJERCITA_LA_CUARTA & otras == TAMBIEN_LA_TERCERA


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


# --- dictamen Fable, C6.b, y VE-7 fix-suite (ficha VE7C-06) --- lo que NO
# cumple en la quinta, por la raiz del codigo, medido: la corrida ejercita
# formulas y no es un diseño. A-04 (receptor 3.8 m bajo la entrada) tiene un
# cabezal de salida de H_c = 6.03 m (B = 6.62 m dimensionado por
# estabilidad): la zapata de sus ALEROS crece por el talon hasta el tope
# 1.5·H_c (B = 9.02 m, `al_tope`) y la franja del extremo (1·L) sigue sin
# cumplir el deslizamiento sismico (E3-LRFD.sis.s.alero.100: 251.2 kN/m de
# demanda contra 224.1 de resistencia factorada). La app lo dice con su
# aviso («ZAPATA DE LOS ALEROS NO FACTIBLE con estos criterios»); el censo
# lo registra, no lo corrige.
NO_CUMPLE_EN_LA_QUINTA = {
    "C-01": {"A2"},
    "A-04": {"E3-LRFD"},
}
CODIGOS_QUE_NO_CUMPLEN_EN_A04_DE_LA_QUINTA = {"E3-LRFD.sis.s.alero.100"}


def test_ic_la_quinta_no_cumple_solo_lo_medido(emitidos):
    *_, informe = emitidos[QUINTA]
    assert {pid: set(r) for pid, r in
            ind.raices_que_no_cumplen(informe).items()} == NO_CUMPLE_EN_LA_QUINTA
    por_id = {p.punto.id: p for p in informe.puntos}
    a04 = por_id["A-04"].cabezal
    assert {v.codigo for v in a04.verificaciones_incumplidas} == \
        CODIGOS_QUE_NO_CUMPLEN_EN_A04_DE_LA_QUINTA
    assert a04.intentos_de_zapata_aleros[-1].al_tope
    assert any("ZAPATA DE LOS ALEROS NO FACTIBLE" in a for a in a04.avisos)
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


# --- VE-7, depuracion del peralte (ficha VE7C-06) --- La «divergencia» del
# censo NO era pytest contra fuera de pytest, ni conftest (cuyas
# declaraciones `correr_referencia` y `validacion_integral.correr` vacian al
# entrar: medido, la misma corrida con y sin `import conftest` da lo mismo).
# Era el criterio 'momento_talon_cabezal': `tests/test_ve3_peralte_cabezal.py`
# corre con los valores de archivo PREVIOS a VE-3.15 (fixture de modulo
# `valores_previos_ve3_15`), y de los cinco solo «peso_entero» hace crecer el
# peralte (medido clave a clave). Con el valor de archivo «exacto» el talon
# descuenta la reaccion del terreno y A1/A2 cumplen con el de la regla: el
# bucle de `M9.dimensionar_peralte_por_armado` no entra. Diferencia legitima
# de datos, no defecto. Este test la fija por las dos puertas: la de
# referencia (sin crecer) y el mismo juego con la otra opcion declarada por
# la guardia de `--declarar` (crece y emite el fundamento).
CLAVE_TALON = "momento_talon_cabezal"
PASO_DEL_PERALTE_M = 0.10             # 'dimensionamiento_zapata_cabezal'
ABS_MM = 5e-7


def _a01(informe):
    return next(p for p in informe.puntos if p.punto.id == "A-01")


def _veredictos(cab, codigos):
    return {v.codigo: v.cumple for a in cab.armado for v in a.verificaciones
            if v.codigo in codigos}


def test_ic_el_peralte_sin_puerta_es_por_el_metodo_del_talon(emitidos):
    """
    VE-7 (ficha VE7C-06): LA DIVERGENCIA DEL PERALTE, explicada (depuracion VE-7, 2026-11-20; medido).

    no era pytest contra fuera de pytest ni `conftest.py` (sus
    declaraciones las vacían `correr_referencia` y
    `validacion_integral.correr`: la misma corrida con y sin `import
    conftest` da lo mismo). Es el criterio `momento_talon_cabezal`:
    `tests/test_ve3_peralte_cabezal.py` corre con los valores de archivo
    PREVIOS a VE-3.15 (fixture de módulo `valores_previos_ve3_15`, ficha
    VE3-18), y de sus cinco sólo «peso_entero» hace crecer el peralte
    (medido clave a clave). Con el valor de archivo «exacto» (decisión 9
    del dueño; AASHTO 11.6.1.2 «more exact method» y la presión lineal de
    10.6.5) el talón de la salida de A-01 del juego pide M_u = 64.8 a 76.8
    kN·m/m según la combinación, frente a 143.0 a 239.3 del peso entero
    (envolventes 76.8 y 239.3: 3.1 veces; combinación a combinación, 2.0 a
    3.7), A1 y A2 del talón cumplen con el peralte de la regla (0.404 m) y
    el bucle de `M9.dimensionar_peralte_por_armado` no entra (`if not
    estado: return None`). Ni con φ = 30° ni con `drenaje_trasdos` =
    'sin_drenaje' crece. **Diferencia legítima de datos, no defecto**: la
    corrida real dimensiona lo que hace falta, y el test mide el MÉTODO
    con la otra opción de la ventana. Dos hallazgos más: (1) por
    `correr_referencia`, el A-01 de `hidrologia_calculada` ni siquiera
    llega al cabezal (su caudal calculado detiene el bucle de MD); el A-01
    del juego con cabezal es el de la quinta; (2) desde la integración del
    lote A, el fundamento SÍ tiene puerta: lo emite la zapata de los
    ALEROS (`9.3.e.s.alero`, A-04 de la quinta y de la cuarta), y salió
    del censo; la zapata del cabezal (`9.3.p.*`) sigue sin ella. El
    docstring de `M9.solicitaciones_de_resistencia` decía «rige el mayor»
    del peso entero y el que descuenta la reacción, anterior a la opción
    9; se corrigió (el código ya hacía lo de la ficha del criterio). Lo
    fija `tests/test_ve7_lote_c_cuarta_corrida.py::test_ic_el_peralte_sin_
    puerta_es_por_el_metodo_del_talon` (referencia sin crecer; el mismo
    juego con «peso_entero» declarado crece un paso y emite `9.3.p.s`).
    """
    from src import criterios_adoptados as ca
    from src.modelos import ORIGEN_DIMENSION_ARMADO, ORIGEN_DIMENSION_REGLA
    from src.modulos import M9_cabezal as M9
    from tests.apoyo import validacion_integral as V

    # 1. La referencia: «exacto» de archivo, y ninguna corrida lo declara.
    assert ca.CRITERIOS[CLAVE_TALON].valor == "exacto"
    for c in ind.CORRIDAS_DE_REFERENCIA:
        assert CLAVE_TALON not in c.declaraciones, c.nombre
    # Ningun cabezal de ninguna corrida itera el peralte.
    for nombre, (_e, _el, informe) in emitidos.items():
        for p in informe.puntos:
            if p.cabezal is not None:
                assert p.cabezal.intentos_de_peralte == (), (nombre,
                                                             p.punto.id)
    # El A-01 del juego de T-11 con cabezal es el de la quinta (en
    # `hidrologia_calculada` su caudal calculado no deja dimensionarlo):
    # la salida conserva el peralte de la regla porque A1/A2 del talon
    # CUMPLEN con el.
    assert _a01(emitidos["hidrologia_calculada"][2]).cabezal is None
    cab = _a01(emitidos[QUINTA][2]).cabezal
    assert next(d for d in cab.salida.dimensiones
                if d.nombre == "espesor de la zapata").origen \
        == ORIGEN_DIMENSION_REGLA
    talon_s = ("A1.talon.s", "A2.talon.s")
    assert _veredictos(cab, talon_s) == {c: True for c in talon_s}
    # La puerta que el fundamento SI tiene en las corridas de referencia es
    # la zapata de los ALEROS (VE-7 lote A, codigo `9.3.e.<x>.alero`): la de
    # la zapata del cabezal (`9.3.p.<x>`) no la abre ninguna.
    del_peralte = {p.codigo for _e, _el, informe in emitidos.values()
                   for p in ind.pasos_de_la_corrida(informe)
                   if p.fundamento_id == "F9.DIMENSIONADO_PERALTE"}
    assert del_peralte
    assert all(c.endswith(M9.SUFIJO_ALERO) for c in del_peralte), del_peralte

    # 2. El MISMO juego con «peso_entero» declarado (la otra opcion de la
    # ventana, la que `valores_previos_ve3_15` pone en el archivo): A1/A2 del
    # talon no cumplen con la regla, el peralte crece un paso y el fundamento
    # se emite. Si esto deja de crecer, la explicacion del censo cae.
    informe = V.correr_juego(V.aplicar(
        V.juego_completo(), [("declarar", CLAVE_TALON, "peso_entero")]))
    cab = _a01(informe).cabezal
    intentos = [i for i in cab.intentos_de_peralte if i.extremo == "salida"]
    assert intentos[0].espesor_zapata == pytest.approx(
        cab.entrada.espesor_zapata, abs=ABS_MM)   # el de la regla
    assert set(talon_s) <= set(intentos[0].incumplidas)
    assert intentos[-1].cumple
    assert cab.salida.espesor_zapata == pytest.approx(
        intentos[0].espesor_zapata + PASO_DEL_PERALTE_M, abs=ABS_MM)
    assert next(d for d in cab.salida.dimensiones
                if d.nombre == "espesor de la zapata").origen \
        == ORIGEN_DIMENSION_ARMADO
    assert "9.3.p.s" in {p.codigo for p in cab.pasos
                         if p.fundamento_id == "F9.DIMENSIONADO_PERALTE"}
