"""
tests/test_familias_del_csv.py
==============================
Que datos declarados sirven de algo en un expediente, segun las familias que
su CSV trae.

Para que existe
---------------
La pestana 1 de la ventana pide los cinco datos que no son columna de Sec. 1.2
--- `luz_m`, `TW_m`, `longitud_m`, `L_hidraulico_m` y `categoria_tr` --- sin
decir que dos de ellos solo sirven para UNA familia. Quien llena un expediente
de puras alcantarillas de paso ve un campo de cuneta que no le va a servir
para nada y no tiene como saberlo.

La distincion existia y estaba escrita como PROSA en el tooltip de la ventana
("Solo aplica a Familia B (Fase 10)"), que es la peor forma de tenerla: el
programa no la puede leer. `cli.FAMILIAS_QUE_USAN` la convierte en dato, y
este archivo es lo que impide que ese dato sea una lista que alguien mantiene
a mano.

Las dos defensas, que no son la misma
-------------------------------------
`L_hidraulico_m` la tiene ESTRUCTURAL: `cli._fase_10` lee esa misma fila para
decidir si la Fase 10 corre, de modo que la declaracion no puede quedarse
describiendo una condicion que el codigo ya no aplica. Se comprueba moviendo
la fila y viendo que la fase se mueve con ella.

`categoria_tr` no la tiene: quien decide vive en `M1.periodo_retorno_de`, que
esta CLI no gobierna. Su unica defensa es la MEDIDA --- correr el pipeline
familia por familia y comprobar que declarar el dato no mueve NADA del informe
en las familias que la fila no nombra ---, y es la que este archivo aplica a
las dos, porque una defensa estructural tampoco demuestra que la fila diga la
verdad sobre el resto de familias.
"""

import csv
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
for ruta in (str(RAIZ), str(SRC)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

import cli                                                        # noqa: E402
from modelos import Familia                                       # noqa: E402

CSV_PERFIL = RAIZ / "tests" / "ejemplo_puntos_perfil.csv"

# Datos externos con los que todas las familias del fixture llegan lo mas
# lejos que pueden. El caudal y la pendiente de C-01 son los del CANAL: su
# fila los trae vacios a proposito (Tablero 3.1).
EXTERNOS_BASE = dict(luz_m=3.0, TW_m=None, longitud_m=None)
EXTERNOS_POR_PUNTO = {"C-01": {"Q_m3s": 0.65, "S_conducto": 0.004}}

# El valor con el que se prueba cada dato declarado. No tiene que ser realista
# --- lo que se mide es si CAMBIA algo, no si es correcto ---, solo valido.
VALOR_DE_PRUEBA = {
    "L_hidraulico_m": 120.0,
    "categoria_tr": "quebrada_menor",
}


def _csv_de_familia(destino: Path, familia: Familia) -> Path:
    """El mismo corredor, con las filas de una sola familia."""
    filas = list(csv.reader(CSV_PERFIL.open(encoding="utf-8")))
    cabecera, cuerpo = filas[0], filas[1:]
    columna = cabecera.index("familia")
    propias = [f for f in cuerpo if f[columna] == familia.value]
    assert propias, f"el fixture no trae ningun punto de Familia {familia.value}"
    ruta = destino / f"puntos_{familia.value}.csv"
    with ruta.open("w", newline="", encoding="utf-8") as fh:
        escritor = csv.writer(fh)
        escritor.writerow(cabecera)
        escritor.writerows(propias)
    return ruta


def _sin_el_acuse(volcado: dict, clave: str) -> dict:
    """
    Quita del volcado el ACUSE de la declaracion, que no es un resultado.

    Cada punto lleva un bloque `datos_declarados` con lo que se le declaro y
    de donde vino, y ese bloque cambia --- tiene que cambiar --- por el solo
    hecho de declarar algo: la memoria esta obligada a decir que se declaro,
    lo haya usado o no. Compararlo aqui haria fallar al test por la unica
    diferencia que NO importa, y la anotacion de la ventana no promete que el
    dato no quede registrado: promete que no cambia ningun RESULTADO.
    """
    for punto in volcado.get("puntos", []):
        punto.get("datos_declarados", {}).pop(clave, None)
    return volcado


def _informe_comparable(ruta_csv: Path, extra: dict, sin_acuse_de: str = "") -> str:
    """
    El informe como TEXTO JSON, sin lo que cambia entre dos corridas iguales.

    Se comparan los VOLCADOS y no los objetos porque el volcado es lo que el
    proyectista ve --- el JSON, y por su misma via el HTML ---: si dos
    corridas producen el mismo volcado, declarar ese dato no le cambio nada a
    nadie. Fuera quedan la marca de tiempo y la ruta del CSV, que son
    distintas por construccion.

    Se serializa en vez de copiarse: el volcado lleva objetos que no son
    copiables sin mas --- `ReferenciaNormativa` es un `str` con `__new__`
    propio --- y ademas la comparacion de textos da un diff legible cuando
    falla, que es cuando hace falta leerlo.
    """
    banderas = dict(EXTERNOS_BASE)
    banderas.update({clave: None for clave in VALOR_DE_PRUEBA})
    banderas.update(extra)
    externos = cli.cargar_datos_externos(None, banderas)
    for id_punto, datos in EXTERNOS_POR_PUNTO.items():
        externos.por_punto.setdefault(id_punto, {}).update(
            {clave: cli.DatoDeclarado(clave, valor, "datos del expediente")
             for clave, valor in datos.items()})
    informe = cli.correr(ruta_csv, externos, alcance=cli.ALCANCE_EXPEDIENTE)
    volcado = cli.informe_json(informe)
    volcado["expediente"].pop("generado_utc", None)
    volcado["expediente"].pop("csv", None)
    if sin_acuse_de:
        volcado = _sin_el_acuse(volcado, sin_acuse_de)
    return json.dumps(volcado, default=str, sort_keys=True, ensure_ascii=False)


# ===========================================================================
# La medida: en las familias que la fila no nombra, declarar no mueve nada
# ===========================================================================

@pytest.mark.parametrize("clave", sorted(cli.FAMILIAS_QUE_USAN))
@pytest.mark.parametrize("familia", list(Familia))
def test_declarar_el_dato_no_mueve_nada_en_las_familias_que_no_lo_usan(
        tmp_path, clave, familia):
    """
    El contrato de `FAMILIAS_QUE_USAN`, medido corrida contra corrida.

    Si la fila dice que este dato NO sirve para esta familia, entonces un
    expediente de esa sola familia tiene que dar EL MISMO informe con el dato
    declarado y sin el, salvo el acuse de la propia declaracion. Si diera
    otro, la ventana estaria anotando «no aplica» sobre un campo que si cambia
    el resultado --- que es el unico fallo grave que esta anotacion puede
    tener.

    «NO APLICA» NO ES «ES INERTE», y el caso que lo separa se midio al
    escribir esto: en la Familia B, `categoria_tr` tiene fila FIJA por
    Sec. 2.3, de modo que declarar la fila que le toca no cambia nada ---
    esto ---, pero declarar OTRA es `DatoInvalidoError`. Lo que la anotacion
    promete es que declararlo no le va a servir de nada al proyectista, no que
    el campo este muerto; por eso se anota y no se deshabilita.

    Al reves no se comprueba aqui a proposito: que el dato SI mueva algo en la
    familia que lo usa es lo que prueban los tests de la Fase 10 y del TR, y
    repetirlo seria comprobar dos veces lo mismo.
    """
    if familia in cli.familias_que_usan(clave):
        pytest.skip(f"Familia {familia.value} SI usa '{clave}': "
                    "este test mide las que no")
    ruta = _csv_de_familia(tmp_path, familia)
    sin_declarar = _informe_comparable(ruta, {}, sin_acuse_de=clave)
    declarado = _informe_comparable(ruta, {clave: VALOR_DE_PRUEBA[clave]},
                                    sin_acuse_de=clave)
    assert sin_declarar == declarado, (
        f"declarar '{clave}' cambia el informe de un expediente de pura "
        f"Familia {familia.value}, y `FAMILIAS_QUE_USAN` dice que no lo usa: "
        "la ventana lo estaria anotando como «no aplica» mientras si aplica")


# ===========================================================================
# La defensa estructural de `L_hidraulico_m`
# ===========================================================================

def test_la_fase_10_lee_la_declaracion_y_no_una_condicion_propia(
        tmp_path, monkeypatch):
    """
    Que `FAMILIAS_QUE_USAN` sea el dato que DECIDE, y no un comentario al lado
    del `if`.

    Se comprueba moviendolo: si la fila de `L_hidraulico_m` deja de nombrar a
    la Familia B, la Fase 10 tiene que dejar de correr para un punto de esa
    familia. Un `if punto.familia is not Familia.B` escrito aparte se quedaria
    verde aqui, que es exactamente lo que hay que impedir.
    """
    ruta = _csv_de_familia(tmp_path, Familia.B)
    con_la_fila = _informe_comparable(ruta, {"L_hidraulico_m": 120.0})
    monkeypatch.setitem(cli.FAMILIAS_QUE_USAN, "L_hidraulico_m", ())
    sin_la_fila = _informe_comparable(ruta, {"L_hidraulico_m": 120.0})

    assert con_la_fila != sin_la_fila, (
        "vaciar la fila de 'L_hidraulico_m' en `FAMILIAS_QUE_USAN` no cambio "
        "nada: la Fase 10 no la esta leyendo, y la declaracion es entonces "
        "una tabla paralela")


# ===========================================================================
# Lo que la ventana pregunta
# ===========================================================================

def test_las_familias_del_csv_salen_de_la_misma_carga_que_corre_el_pipeline():
    """
    `familias_del_csv` usa `cargar_puntos`, no una lectura propia del archivo:
    dos lectores del mismo CSV son dos validaciones que pueden discrepar, y la
    ventana acabaria anotando sobre una familia que M0 rechaza.
    """
    assert cli.familias_del_csv(CSV_PERFIL) == (Familia.A, Familia.B, Familia.C)


def test_las_familias_del_csv_vienen_en_el_orden_de_la_seccion_2_3(tmp_path):
    """
    El orden es el de `Familia`, no el de aparicion en el archivo: la
    anotacion se lee mejor si «Familia B» significa lo mismo en dos
    expedientes distintos.
    """
    ruta = _csv_de_familia(tmp_path, Familia.C)
    assert cli.familias_del_csv(ruta) == (Familia.C,)


def test_un_dato_sin_fila_declarada_lo_usan_las_tres_familias():
    """
    Solo se declara la EXCEPCION. Un dato que gobierna el dimensionamiento de
    cualquier cruce no tiene que aparecer en `FAMILIAS_QUE_USAN` para que la
    ventana lo de por bueno --- y si el defecto fuera "ninguna", un campo
    nuevo nacería anotado como inutil hasta que alguien se acordara de
    declararlo.
    """
    for clave in ("luz_m", "TW_m", "longitud_m"):
        assert clave not in cli.FAMILIAS_QUE_USAN
        assert cli.familias_que_usan(clave) == tuple(Familia)


def test_toda_clave_declarada_es_una_clave_externa_de_verdad():
    """
    Una fila con la clave mal escrita no falla: no filtra nada y la anotacion
    calla para siempre. Aqui se ve.
    """
    for clave in cli.FAMILIAS_QUE_USAN:
        assert clave in cli.CLAVES_EXTERNAS, (
            f"'{clave}' no es una clave de `CLAVES_EXTERNAS`: la fila no "
            "gobierna ningun campo")
