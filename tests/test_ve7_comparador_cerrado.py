"""
tests/test_ve7_comparador_cerrado.py
====================================
VE-7, lote C (dictamen Fable del 2026-11-20, abierto (ii)): el comparador
de volcados compara TODA clave del punto y de la raiz. Hasta VE-7 enumeraba
a mano los campos del punto y dejaba fuera nueve (`avisos`, `caudal`,
`durabilidad`, `cabezal`, `licuefaccion`...) y la raiz `metrados`: dos
corridas que diferian en ellas salian IGUALES.

Se mide sobre el volcado de la cuarta corrida de referencia
(`materiales_y_ramas`), que lleva todas las claves con contenido: mutar
cualquiera da DIFIEREN y la diferencia la nombra.
"""

import copy
import json

import pytest

import cli
from src import comparador as cmp
from src import indice_formulas as ind


@pytest.fixture(scope="module")
def volcado():
    corrida = next(c for c in ind.CORRIDAS_DE_REFERENCIA
                   if c.nombre == "materiales_y_ramas")
    informe = ind.correr_referencia(corrida)
    return json.loads(json.dumps(cli.informe_json(informe), ensure_ascii=False,
                                 default=str))


def _mutar(valor):
    """Un valor distinto de la misma clave (la marca no es un numero)."""
    if isinstance(valor, dict):
        if not valor:
            return {"mutado": True}
        k = sorted(valor)[0]
        return {**valor, k: _mutar(valor[k])}
    if isinstance(valor, list):
        return valor + ["mutado"]
    if isinstance(valor, bool):
        return not valor
    if isinstance(valor, (int, float)):
        return valor * 3 + 1
    if valor is None:
        return "mutado"
    return f"{valor} mutado"


CLAVES_DEL_PUNTO = sorted({
    "progresiva", "familia", "pendientes_externos", "dimensionado",
    "datos_declarados", "tw_seccion_receptor", "avisos", "clasificacion",
    "caudal", "licuefaccion", "durabilidad", "diseno", "proteccion_salida",
    "proteccion_entrada", "socavacion_salida", "geometria", "cabezal",
    "estructural", "espaciamiento_alivio", "tramo_alivio", "aporte_alivio",
    "iteraciones", "verificaciones", "verificaciones_no_evaluadas",
    "bloqueos", "compatibilidad_rasante"})


def test_las_claves_del_punto_son_las_del_volcado(volcado):
    claves = set().union(*(set(p) for p in volcado["puntos"])) - {"id"}
    # `gobierno_por_receptor` y `metrado` solo salen en el punto que los tiene
    assert set(CLAVES_DEL_PUNTO) <= claves
    assert claves - set(CLAVES_DEL_PUNTO) <= {"gobierno_por_receptor", "metrado"}


@pytest.mark.parametrize("clave", CLAVES_DEL_PUNTO + ["metrado"])
def test_mutar_una_clave_del_punto_da_difieren_y_la_nombra(volcado, clave):
    a = volcado
    b = copy.deepcopy(volcado)
    punto = next((p for p in b["puntos"] if p.get(clave) not in (None, [], {})),
                 None)
    if punto is None:
        punto = next(p for p in b["puntos"] if clave in p)
    if clave == "licuefaccion":
        punto[clave] = dict(punto[clave], estado="mutado")
    elif clave == "verificaciones":
        punto[clave] = [dict(punto[clave][0], cumple=not punto[clave][0]["cumple"])] \
            + punto[clave][1:]
    elif clave == "bloqueos":
        punto[clave] = punto[clave] + [dict(punto[clave][0], mensaje="mutado")] \
            if punto[clave] else [{"etapa": "mutada", "tipo": "X"}]
    else:
        punto[clave] = _mutar(punto[clave])
    resultado = cmp.comparar(a, b)
    assert not resultado.iguales, clave
    texto = "\n".join(resultado.lineas())
    rotulo = {"verificaciones": cmp.ROTULO_VERIFICACION.strip(),
              "bloqueos": "bloqueo"}.get(clave, clave)
    assert rotulo in texto, (clave, texto[:400])


def test_la_raiz_metrados_se_compara(volcado):
    assert volcado.get("metrados")
    b = copy.deepcopy(volcado)
    b["metrados"] = _mutar(b["metrados"])
    resultado = cmp.comparar(volcado, b)
    assert not resultado.iguales
    assert "metrados" in "\n".join(resultado.lineas())


def test_una_clave_raiz_nueva_se_compara(volcado):
    b = copy.deepcopy(volcado)
    b["clave_que_no_existia"] = 1
    assert not cmp.comparar(volcado, b).iguales


def test_lo_omitido_no_cambia_y_el_volcado_es_igual_a_si_mismo(volcado):
    assert cmp.CAMPOS_OMITIDOS == (
        "generado", "expediente.generado_utc", "expediente.csv",
        "expediente.corredor_del_proyecto.origen",
        "datos_sitio.usados[].origen", "expediente.hidrologia.cuencas",
        "expediente.hidrologia.estacion")
    assert cmp.comparar(volcado, copy.deepcopy(volcado)).iguales
