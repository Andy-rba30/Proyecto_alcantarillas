"""
tests/test_ext11_cruce_temarios.py
==================================
PC-29, segunda mitad: el cruce de los temarios de refutacion
(`docs/auditorias/temario_refutar_95.json` y `_48.json`) contra la hoja
`Hallazgos` del tracker, COMO TEST. EXT-0 hizo el cruce a mano sobre los 71
items ALTA/CRITICA --- siete recibieron fila propia y ocho grupos quedaron
anotados en «Vinculos cruzados» de la fila NOR-* que los cubre --- y dejo
para EXT-11 que el cruce fuera repetible: un item que suba de severidad, o
un temario nuevo, no puede quedarse sin fila de estado sin que nada avise.

La regla, la misma de EXT-0: se cruzan los items cuya severidad es ALTA o
CRITICA, tomando la severidad FINAL si el item lleva veredicto y la
PROPUESTA si no lo lleva (los 39 cerrados en la corrida original no tienen
veredicto en el JSON; auditoria_normativa.md §12). Un item esta CUBIERTO si

    (a) tiene fila propia en `Hallazgos` (su `R95-nnn` / `R48-nnn` es el ID),
    (b) alguna fila lo NOMBRA en «Vinculos cruzados», en «Hallazgo» o en
        «Commit / PR» (los grupos PARCIAL de EXT-0), o
    (c) esta en `CUBIERTOS_POR_FILA_NOR`, el censo de este archivo, que dice
        QUE fila NOR-* del informe normativo trata el mismo hallazgo. Es el
        resto del cruce manual de EXT-0, que en el tracker no dejo huella
        porque el auditor numero sus hallazgos (`H-13`, `E-03`, `G-06`) con
        una numeracion distinta de la del informe consolidado (`NOR-E060-03`)
        y ningun documento del repositorio las enlaza.

El censo se comprueba en las dos direcciones: un item ALTA/CRITICA sin (a),
(b) ni (c) falla; una entrada de (c) cuyo item ya tiene (a) o (b) tambien,
para que el censo se achique si el tracker lo absorbe; y cada fila NOR que
el censo nombra tiene que existir y no estar «Abierta», porque un item
ALTA cubierto por una fila abierta no esta cubierto. Una fila «Cerrado
parcial» SI cubre (NOR-E060-02 cubre R95-030, NOR-HDS-05 cubre R48-036):
el parcial tiene fila de estado, que es lo que PC-29 exige, y su resto ya
esta planificado en el tracker.

Fuera del cruce, por diseño y por la regla de EXT-0: los 31 items cuya
severidad PROPUESTA era ALTA/CRITICA y cuya severidad FINAL bajo tras la
refutacion. El cruce mira lo que el refutador dejo en pie, no lo que el
auditor alego.

El tracker se lee con `tests/apoyo/tracker.py` (biblioteca estandar), no
con openpyxl: ver alli por que.
"""

import json
import re
from pathlib import Path

import pytest

from tests.apoyo import tracker

RAIZ = Path(__file__).resolve().parents[1]
TEMARIOS = (RAIZ / "docs" / "auditorias" / "temario_refutar_95.json",
            RAIZ / "docs" / "auditorias" / "temario_refutar_48.json")
SEVERIDADES_QUE_SE_CRUZAN = ("ALTA", "CRITICA", "CRÍTICA")
PATRON_ID_TEMARIO = re.compile(r"R(?:95|48)-\d{3}")
# El tamaño del tracker que `verificar_sesion.py` fija (303 desde EXT-0).
FILAS_ESPERADAS = 303

# (c): item del temario -> fila NOR-* que trata el mismo hallazgo. Cada
# entrada se leyo contra el enunciado del item y el titulo de la fila.
CUBIERTOS_POR_FILA_NOR = {
    # Manual de Suelos: compactacion, calicatas, espaciamiento
    "R95-001": "NOR-SUE-03",   # H-08 numerales de COMPACTACION_CORONA/CUERPO
    "R95-003": "NOR-SUE-01",   # H-12 el Cuadro 4.1 si dice cuando son 4 o 6
    "R95-004": "NOR-SUE-01",   # H-13 la cita «4 (o 6)» no existe
    "R95-005": "NOR-SUE-02",   # H-14 ESPACIAMIENTO_PERFIL_KM = 4.0
    # Manual de Hidrologia
    "R95-008": "NOR-HID-05",   # H-02 NUMERAL_LUZ, pags. 70 y 88
    "R48-003": "NOR-HID-05",   # E-06 la misma paginacion en la v8 y el manifiesto
    "R95-010": "NOR-HID-01",   # H-10 G_LAUSHEY = 9.8 como [N]
    "R95-012": "NOR-HID-02",   # H-19 LONG_MAX_CUNETA en la pag. 178
    # Manual de Puentes
    "R95-017": "NOR-PUE-01",   # H-01 SOBRECARGA_TRASDOS_H_EQ, num. 2.1.4.3.9
    "R48-004": "NOR-PUE-02",   # F-01 el 0.60 m como [N] sin condicion
    "R95-018": "NOR-PUE-04",   # H-03 el vacio de factores de carga
    "R95-019": "NOR-PUE-06",   # H-04 «el indice salta de 2.11 a 2.12»
    "R95-087": "NOR-PUE-06",   # H-04 la misma frase, segunda ronda
    "R48-016": "NOR-PUE-06",   # G-04 la frase impresa en la memoria
    "R95-020": "NOR-PUE-05",   # H-05 «vacio absoluto sobre conductos enterrados»
    "R95-089": "NOR-PUE-05",   # H-05 la misma frase en el manifiesto
    "R48-017": "NOR-PUE-05",   # G-05 la misma frase impresa en la memoria
    # E.060
    "R95-030": "NOR-E060-02",  # H-15 acero por temperatura en dos caras
    # EG-2013
    "R95-036": "NOR-EG-01",    # H-02 508.07 esta en la pag. 984, no en la 982
    "R95-086": "NOR-EG-01",    # H-02 idem, segunda ronda
    "R48-014": "NOR-EG-01",    # G-02 «pag. 982» impreso tres veces
    "R48-038": "NOR-EG-01",    # C-08 el mismo «pag. 982» en constante y criterio
    "R48-013": "NOR-EG-02",    # H-MC-29 donde vive la cita literal del 508.07
    "R95-043": "NOR-EG-03",    # H-16 CAMA_RELLENO_LATERAL['tmc'], pag. 970
    # HDS-5
    "R95-053": "NOR-HDS-02",   # H-17 HW_D_max = 1.5 «cita cerrada»
    "R48-034": "NOR-HDS-02",   # C-04 la pag. 2.14 y el rango 1.0-1.5
    "R95-054": "NOR-HDS-01",   # H-15 ke = 0.5, Tabla C.2 «pag. C.2»
    "R48-037": "NOR-HDS-01",   # C-07 idem
    "R48-036": "NOR-HDS-05",   # C-06 seccion llena / h_o sin condicion de uso
    # AASHTO LRFD
    "R95-057": "NOR-VAC-01",   # H-02 §14.a «el vacio esta cerrado» con tres fuentes
    "R95-061": "NOR-AAS-04",   # H-06 EH en reposo «sin minimo declarado»
    "R48-032": "NOR-ANA-01",   # C-02 la analogia HDPE «conservadora»
    "R48-018": "NOR-MEM-03",   # G-06 F_pga y la convergencia de las tres clases
    # Normas de producto
    "R95-072": "NOR-PRO-01",   # H-01 D_MAX['tmc'] = 2.10 m
    "R95-074": "NOR-PRO-02",   # H-02 D_MAX['concreto_reforzado'] = 2.70 m
    "R95-075": "NOR-PRO-03",   # H-03 «su Nota 1 las excluye»
    "R95-088": "NOR-PRO-03",   # H-03 idem, segunda ronda
    # Manifiesto de citas
    "R95-063": "NOR-MAN-01",   # H-08 «ninguna cita a AASHTO lleva valor»
    "R48-012": "NOR-MAN-01",   # H-MC-27 cuatro criterios con valor inventariados vacios
    "R95-064": "NOR-MAN-03",   # H-09 la fila FS_flotacion
    "R48-008": "NOR-MAN-03",   # H-MC-19 idem
    "R48-048": "NOR-MAN-03",   # C-19 el criterio retirado sigue inventariado
    "R48-009": "NOR-MAN-03",   # H-MC-20 la advertencia inexistente
    "R48-010": "NOR-MAN-02",   # H-MC-25 la distribucion de los 46 criterios
    "R48-011": "NOR-MAN-02",   # H-MC-26 «los 33 criterios [A]»
}


def _severidad(item: dict) -> str:
    campo = "severidad_final" if item.get("veredicto") else "severidad_propuesta"
    return (item.get(campo) or "").upper()


def _items_que_se_cruzan():
    salida = []
    for ruta in TEMARIOS:
        for item in json.loads(ruta.read_text(encoding="utf-8"))["items"]:
            if _severidad(item).startswith(SEVERIDADES_QUE_SE_CRUZAN):
                salida.append(item)
    return salida


@pytest.fixture(scope="module")
def filas():
    return tracker.hallazgos()


@pytest.fixture(scope="module")
def cobertura(filas):
    """(ids con fila propia, ids nombrados en alguna fila)."""
    propios = {f["ID"] for f in filas}
    nombrados = set()
    for f in filas:
        for campo in ("Vínculos cruzados", "Hallazgo", "Commit / PR"):
            nombrados |= set(PATRON_ID_TEMARIO.findall(f.get(campo, "")))
    return propios, nombrados


def test_el_lector_lee_el_tracker_entero(filas):
    assert len(filas) == FILAS_ESPERADAS
    assert {"ID", "Estado", "Vínculos cruzados", "Hallazgo"} <= set(filas[0])
    assert filas[0]["ID"] == "SIS-A-01"


def test_los_temarios_estan_completos_y_la_severidad_se_lee_como_en_EXT0():
    for ruta in TEMARIOS:
        d = json.loads(ruta.read_text(encoding="utf-8"))
        assert d["pendientes"] == 0 and d["cerrados"] == d["total"] == len(d["items"])
    items = _items_que_se_cruzan()
    # EXT-0 cruzo 71: es lo que la regla de severidad devuelve hoy, y si los
    # JSON cambian este numero cambia con ellos y hay que releerlo.
    assert len(items) == 71
    # Los que la refutacion BAJO de severidad quedan fuera (31), y los que
    # SUBIO entran (2, entre ellos R95-031 / H-13, de MEDIA a ALTA).
    bajaron = subieron = 0
    for ruta in TEMARIOS:
        for item in json.loads(ruta.read_text(encoding="utf-8"))["items"]:
            propuesta = (item.get("severidad_propuesta") or "").upper().startswith(
                SEVERIDADES_QUE_SE_CRUZAN)
            final = _severidad(item).startswith(SEVERIDADES_QUE_SE_CRUZAN)
            bajaron += propuesta and not final
            subieron += final and not propuesta
    assert (bajaron, subieron) == (31, 2)
    assert all(PATRON_ID_TEMARIO.fullmatch(i["id"]) for i in items)


@pytest.mark.parametrize("item", _items_que_se_cruzan(), ids=lambda i: i["id"])
def test_todo_item_ALTA_o_CRITICA_tiene_fila_de_estado_o_fila_que_lo_cubre(
        item, cobertura):
    propios, nombrados = cobertura
    id_item = item["id"]
    cubierto = (id_item in propios or id_item in nombrados
                or id_item in CUBIERTOS_POR_FILA_NOR)
    assert cubierto, (
        f"{id_item} [{item['hallazgo_id']}] {_severidad(item)} no tiene fila "
        f"propia, ninguna fila lo nombra y no esta en CUBIERTOS_POR_FILA_NOR: "
        f"{item['enunciado'][:160]}")


def test_el_censo_no_conserva_items_que_el_tracker_ya_absorbio(cobertura):
    propios, nombrados = cobertura
    absorbidos = sorted(i for i in CUBIERTOS_POR_FILA_NOR
                        if i in propios or i in nombrados)
    assert not absorbidos, (
        f"items del censo que ya tienen fila o mencion en el tracker: "
        f"{absorbidos}. Retiralos: el censo es el resto del cruce, no una copia.")
    ids_cruzados = {i["id"] for i in _items_que_se_cruzan()}
    fuera = sorted(set(CUBIERTOS_POR_FILA_NOR) - ids_cruzados)
    assert not fuera, f"items del censo que ya no son ALTA/CRITICA: {fuera}"


@pytest.mark.parametrize("id_item,fila_nor", sorted(CUBIERTOS_POR_FILA_NOR.items()))
def test_cada_fila_NOR_del_censo_existe_y_no_esta_abierta(id_item, fila_nor, filas):
    fila = next((f for f in filas if f["ID"] == fila_nor), None)
    assert fila is not None, f"{id_item} remite a {fila_nor}, que no esta en el tracker"
    assert fila_nor.startswith("NOR-"), "el censo remite a filas del informe normativo"
    assert not fila["Estado"].startswith("Abierto"), (
        f"{id_item} esta cubierto por {fila_nor}, que sigue «{fila['Estado']}»: "
        "un item ALTA cubierto por una fila abierta no esta cubierto")
