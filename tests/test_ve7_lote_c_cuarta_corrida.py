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
# (c) Sin ninguna puerta: una rama que datos de prueba validos no alcanzan
#     sin romper lo que la cuarta ejercita (el criterio es de toda la
#     corrida, o la rama es de otro regimen).
SIN_EJERCITAR = {
    "F4.PISO_HW": "eleccion del piso de HW, solo cuando Ks*S anula la carga de "
                  "entrada; ningun punto de prueba valido llega ahi",
    "F3.SELVA_ALTA_TMC": "'region_natural' es [S] de corredor: en selva alta el "
                         "TMC arranca en 1.35 m y A-01 deja de caber (se midio)",
    "F4.N_CAJON": "'n_manning_cajon' es de toda la corrida: la cuarta declara "
                  "el par in situ y las otras el de archivo (Tabla B.1)",
    "F5.V1.RECEPTOR": "gobierno por el nivel del receptor bajo «no_cumple» "
                      "(VE-3.13): otro regimen de V1 para toda la corrida",
    "F5.V5_PERFIL": "remanso por perfil: otra eleccion de 'remanso_derecho_via' "
                    "para toda la corrida (la de referencia es la cota)",
    "F5.V8.DESBORDE": "reparto con desborde: otra eleccion del umbral de no "
                      "colapso para toda la corrida",
    "F6.CAIDA": "salida colgada (HEC-14 Cap. 11): ningun punto dimensionado "
                "de prueba la produce",
    "F6.CAIDA_ESTANQUE": "la misma rama que F6.CAIDA",
    "F6.TW_ALTO": "TW sobre la clave a la salida (Figura 10.3): ningun punto "
                  "dimensionado de prueba lo tiene",
    "F8.COBERTURA": "relleno por debajo del dominio de la rueda distribuida: "
                    "ningun punto dimensionado de prueba lo tiene",
    "F9.DIMENSIONADO_PERALTE": "peralte de la zapata por armado: ninguna zapata "
                               "de prueba lo necesita con la regla de archivo",
}


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


def test_C6_hay_cuatro_corridas_y_la_cuarta_es_de_prueba_rotulada():
    nombres = [c.nombre for c in ind.CORRIDAS_DE_REFERENCIA]
    assert nombres == ["perfil_guia", "expediente_cabezal",
                       "hidrologia_calculada", NOMBRE]
    cuarta = ind.CORRIDAS_DE_REFERENCIA[-1]
    assert cuarta.alcance == "expediente"
    assert cuarta.rotulo.startswith("DATOS DE PRUEBA, NO DEL PROYECTO")
    leeme = cuarta.carpeta.joinpath("LEEME.md").read_text(encoding="utf-8")
    assert leeme.startswith("# DATOS DE PRUEBA, NO DEL PROYECTO")
    for f in EJERCITA_LA_CUARTA:
        if f.startswith("F8."):
            continue   # los ocho de la Fase 8 se nombran por familia
        assert f in leeme, f
    assert cuarta.cuencas is not None and cuarta.estacion is not None


def test_C6_la_cuarta_ejercita_lo_que_las_otras_tres_no(emitidos):
    otras = set().union(*(e for n, (e, _el, _i) in emitidos.items()
                          if n != NOMBRE))
    propios, _el, _i = emitidos[NOMBRE]
    assert EJERCITA_LA_CUARTA <= propios
    assert not (EJERCITA_LA_CUARTA & otras)


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
    La medida que pide el item: cuantos fundamentos ninguna corrida emite
    como paso. Eran 39 de 154 con las tres de VE-6; con la cuarta, 17. Y
    desde el dictamen Fable (i-a) el indice cuenta las tres puertas: de esos
    17, cinco entran como eleccion y uno por el bloque fijo; 11 sin puerta.
    """
    reg = _registro.construir()
    pasos = set().union(*(e for e, _el, _i in emitidos.values()))
    elecciones = set().union(*(el for _e, el, _i in emitidos.values()))
    sin_paso = {f.id for f in reg.fundamentos} - pasos
    assert sin_paso == COMO_ELECCION | POR_BLOQUE_FIJO | set(SIN_EJERCITAR)
    assert len(sin_paso) == 17
    assert COMO_ELECCION <= elecciones
    puertas = ind.puertas_de_los_fundamentos(
        tuple(p for c in ind.CORRIDAS_DE_REFERENCIA
              for p in ind.pasos_de_la_corrida(emitidos[c.nombre][2])))
    assert POR_BLOQUE_FIJO <= puertas[ind.PUERTA_BLOQUE_FIJO]
    sin_puerta = ({f.id for f in reg.fundamentos}
                  - set().union(*puertas.values()))
    assert sin_puerta == set(SIN_EJERCITAR)
    assert len(sin_puerta) == 11
    for f, razon in SIN_EJERCITAR.items():
        assert razon.strip(), f


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
