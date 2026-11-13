"""
proceso/tests/test_t0_gobernanza_proceso.py
===========================================
La mitad de PROCESO de la aceptacion de T-0 de la cadena T, separada de
`tests/test_t0_gobernanza.py` por T-12 (INF-5.2.2): los tres bloques que
leen el material que T-12 movio a `proceso/` y que por eso salen de la suite
del entregable con el. Su texto es el de `tests/test_t0_gobernanza.py` en
`f77c5d4`, sin tocar mas que las rutas y las importaciones:

  1. El tracker (`proceso/auditorias/matriz_cruzada_auditorias.xlsx`) conoce
     los hallazgos del INFORME con prefijo `INF-`, con el numero de item del
     INFORME como ID canonico; cada alias con que la cadena cita un hallazgo
     lleva a UNA fila, y cada prompt escribe los estados que dice
     (`LO_QUE_ESCRIBIO_CADA_PROMPT`: la FASE B de cada prompt le añade su
     fila al integrar).
  5-bis. `proceso/verificar_sesion.py` busca los PDF por la misma puerta que
     la suite y cuenta las filas del tracker.
  6. La copia de la cadena en `proceso/planes_mejora/` no se edita sin que
     se note.

Se corre desde la raiz del repositorio:  python -m pytest proceso/tests
"""

import ast
import hashlib
import re
from pathlib import Path

import pytest

from proceso.apoyo import tracker

RAIZ = Path(__file__).resolve().parents[2]
CADENA = RAIZ / "proceso" / "planes_mejora" / "09_CADENA_PROMPTS_TESIS.md"
VERIFICAR_SESION = RAIZ / "proceso" / "verificar_sesion.py"


# ===========================================================================
# 1. El tracker: los hallazgos del INFORME, con ID canonico y alias
# ===========================================================================

# Cuantos items trae cada apartado del INFORME. No es un numero elegido: es
# el recuento de la lista numerada del §5.1, de las viñetas del §5.2, de las
# filas de las cuatro tablas del §3 y de los siete apartados del §4. Los dos
# de §0 son los puntos 4 y 5 de «lo que falta, en orden de gravedad», que no
# tienen fila propia en ninguna tabla y que la cadena cita (T-3: «Familia C
# no se dimensiona»).
ITEMS_DEL_INFORME = {
    "INF-5.1.": 18,
    "INF-5.2.": 7,
    "INF-3.1.": 6,
    "INF-3.2.": 9,
    "INF-3.3.": 8,
    "INF-3.4.": 7,
    "INF-4.": 7,
}
ITEMS_DE_LA_SECCION_0 = ("INF-0.4", "INF-0.5")

# (prompt que lo escribe, alias tal como lo escribe) -> ID canonico. Son las
# citas de la cadena cuyo numero NO es el del item del INFORME, mas las que
# citan una tabla entera con un rotulo entre comillas.
ALIAS_DE_LA_CADENA = {
    ("T-0", "INF-5.1.9"): "INF-5.1.10",
    ("T-10", "INF-5.1.9"): "INF-5.1.10",
    ("T-4", "INF-5.1.13"): "INF-5.1.17",
    ("T-5", "INF-5.1.5"): "INF-3.3.5",
    ("T-6", "INF-5.1.14"): "INF-5.1.18",
    ("T-7a", "INF-5.1.12"): "INF-5.1.15",
    ("T-8", "INF-5.1.11"): "INF-5.1.13",
    ("T-9", "INF-5.1.11"): "INF-5.1.12",
    ("T-1", "INF-5.2"): "INF-5.2.5",
    ("T-3", "INF-3.x"): "INF-0.4",
}

# Lo que T-0 cierra: los cuatro del punto 3 del prompt (con su numero
# canonico), el desacuerdo hoja de ruta / codigo del punto 2 y la gravedad
# con dos valores, que el punto 2 explica una vez en el Anexo B.
CERRADOS_EN_T0 = {"INF-5.1.1", "INF-5.1.2", "INF-5.1.4", "INF-5.1.10",
                  "INF-5.1.11", "INF-5.1.14"}

# LO QUE CADA PROMPT DE LA CADENA DEJA ESCRITO EN EL TRACKER, por estado. Esta
# tabla crece con cada prompt que integra: T-2 la abrio para que el test de
# abajo, que hasta entonces fijaba «cerrados == los de T-0», no hubiera que
# reescribirlo en cada integracion. Un hallazgo cerrado EN PARTE o verificado
# sin correccion no es «Cerrado»: lleva su propio estado, que el tracker ya
# usaba en las filas de las auditorias anteriores.
ESTADO_CERRADO = "Cerrado"
ESTADO_PARCIAL = "Cerrado parcial"
ESTADO_VERIFICADO = "Verificado (sin correccion)"
ESTADOS_DE_UNA_FILA_INF = ("Abierto", ESTADO_CERRADO, ESTADO_PARCIAL,
                           ESTADO_VERIFICADO, "N/A (sin trabajo)")
LO_QUE_ESCRIBIO_CADA_PROMPT = {
    "T-0": {ESTADO_CERRADO: CERRADOS_EN_T0},
    "T-2": {
        ESTADO_CERRADO: {"INF-5.1.6", "INF-5.1.7"},
        # T-2 hizo su parte y queda otra: la decision del dueño sobre
        # «aviso», el levantamiento del receptor y la corrida de HY-8 de
        # T-11. INF-3.2.7 (la pendiente) estuvo aqui hasta que T-6 hizo la
        # mitad de M7 y lo cerro: figura en la fila de T-6, porque un
        # hallazgo no se declara en dos prompts.
        ESTADO_PARCIAL: {"INF-3.2.2", "INF-3.2.6", "INF-3.2.8"},
        # La analogia de V4 se verifico contra el PDF y no se toco V4.
        ESTADO_VERIFICADO: {"INF-3.2.5"},
    },
    "T-4": {
        # Con los numeros del INFORME: el prompt cita INF-5.1.17 como
        # «INF-5.1.13». INF-5.1.9 e INF-5.1.16 no los nombraba ningun prompt
        # y el orquestador los asigno a T-4.
        ESTADO_CERRADO: {"INF-5.1.17", "INF-3.3.4", "INF-3.3.1", "INF-3.2.4",
                         "INF-5.1.9", "INF-5.1.16"},
        # INF-3.2.1 estuvo aqui como «Cerrado parcial» (solo la mitad del
        # HDPE) hasta que T-3 dio valor a `n_manning_cajon` y lo cerro: figura
        # en la fila de T-3, y su fila del tracker conserva el texto de T-4
        # detras de «Anterior:».
    },
    "T-1": {
        # La hidrologia dentro del programa (Fase 1-bis). INF-5.1.3 no lo
        # nombraba ningun prompt y el orquestador lo asigno a T-1.
        ESTADO_CERRADO: {"INF-3.1.2", "INF-3.1.3", "INF-3.1.5", "INF-3.1.6",
                         "INF-5.2.5", "INF-5.1.3"},
        # INF-3.1.1: la delimitacion de la cuenca sobre plano es una entrada
        # del estudio hidrologico; el programa la recibe y la contrasta.
        # INF-3.1.4: el tratamiento FEN tiene consumidor y regla; quien fija
        # R y n sigue siendo del Propietario, y el analisis de dos
        # poblaciones no se evalua.
        ESTADO_PARCIAL: {"INF-3.1.1", "INF-3.1.4"},
    },
    "T-6": {
        # La geometria de 7.B. Con los numeros del INFORME: el prompt cita
        # INF-5.1.18 como «INF-5.1.14». INF-3.2.7 lo abrio T-2 (la banda y
        # V10) y lo cierra T-6 con el origen de la pendiente en M7; su fila
        # del tracker conserva el texto de T-2 detras de «Anterior:».
        ESTADO_CERRADO: {"INF-5.1.18", "INF-3.3.3", "INF-3.2.7"},
    },
    "T-8": {
        # La proteccion de entrada y salida (Fase 6). Con los numeros del
        # INFORME: el prompt cita INF-5.1.13 como «INF-5.1.11». La pasada de
        # correcciones de la segunda auditoria (integrada detras de T-5) no
        # cambia ningun estado: escribe una NOTA en INF-3.3.7, INF-5.1.13 y
        # MAT-X6, delante del texto que ya tenian.
        ESTADO_CERRADO: {"INF-3.3.7", "INF-5.1.13"},
    },
    "T-5": {
        # La Fase 8 real del conducto. Con los numeros del INFORME: el prompt
        # la cita como «INF-5.1.5 "Fase 8 no verifica nada"» y como «INF-3.3
        # "carga viva / clase / relleno maximo"», y es INF-3.3.5 (el
        # INF-5.1.5 canonico es la mezcla de marcos del cabezal, de T-7b, y
        # sigue abierto). Cerrado con residuales declarados que dependen de
        # entradas: las clases de M 170M ilegibles, el perfil del fabricante
        # del HDPE y la costura empernada del TMC (fichas T5-02, T5-10, T5-03).
        ESTADO_CERRADO: {"INF-3.3.5"},
    },
    "T-3": {
        # La Familia C se dimensiona: el prompt la cita como «INF-3.x "Familia
        # C no se dimensiona"» y es INF-0.4 (§0 del INFORME, punto 4). Cierra
        # ademas la mitad del cajon de INF-3.2.1 (la del HDPE la hizo T-4).
        # INF-0.5 (criterios vacios) queda «Abierto» con una NOTA: los siete
        # del cajon salen de los vacios y quedan los de T-7a/b/c.
        ESTADO_CERRADO: {"INF-0.4", "INF-3.2.1"},
    },
    "T-9": {
        # El espaciamiento de alivios puede fallar (VB1 por tramo, VB2 la
        # condicion literal del Manual) y la longitud por capacidad se
        # calcula: el prompt cita «INF-5.1.11 (M10 no puede fallar)», que es
        # INF-5.1.12, e «INF-3.3 "espaciamiento"», que es INF-3.3.8.
        # INF-5.1.8 (`area_ha` en B) queda EN PARTE: tiene consumidores
        # reales pero nada comprueba que sea el area del tramo.
        ESTADO_CERRADO: {"INF-5.1.12", "INF-3.3.8"},
        ESTADO_PARCIAL: {"INF-5.1.8"},
    },
    "T-7a": {
        # El cabezal por punto y sus aleros: el prompt cita «INF-5.1.12
        # (cabezal "del proyecto")», que es INF-5.1.15. T-7a dejo INF-4.2,
        # INF-4.3 e INF-4.1 EN PARTE (ninguna corrida de expediente alcanzaba
        # la Fase 9, y los datos geotecnicos y sismicos eran de T-7b): las
        # tres filas las reescribio T-7b, y figuran abajo con su estado de
        # hoy (una fila no figura en dos prompts).
        ESTADO_CERRADO: {"INF-5.1.15", "INF-3.4.1", "INF-3.4.2"},
    },
    "T-7b": {
        # La estabilidad del cabezal en dos marcos (INF-4.4, INF-4.5,
        # INF-5.1.5), y el residual de T-7a: la Fase 9 alcanzable a
        # expediente por la ruta real (INF-4.2, CON LA SALVEDAD escrita en
        # su fila: exige declarar el metodo de V5 y sus datos, el TR y el Q
        # del evento extremo y el EMS) y los datos geotecnicos y sismicos por
        # punto (INF-4.1). INF-4.3 sigue EN PARTE: el cabezal paralelo a la
        # via para el marco (ficha T7A-03).
        ESTADO_CERRADO: {"INF-4.4", "INF-4.5", "INF-5.1.5", "INF-4.2",
                         "INF-4.1"},
        ESTADO_PARCIAL: {"INF-4.3"},
    },
    "T-7c": {
        # El armado del cabezal o su alternativa ciclopea (INF-4.6) y la fila
        # «Armado» del §3.4 que lo nombra (INF-3.4.5), cerrados con los
        # residuales nombrados en su fila (fichas T7C-03, -04, -06, -09 y
        # -11). INF-0.5, EXT-M-05, R95-031 e INF-4.3 ganan una NOTA y no
        # cambian de estado; la ficha EXT-7-01 se cierra en
        # docs/decisiones_diferidas.md.
        ESTADO_CERRADO: {"INF-4.6", "INF-3.4.5"},
    },
    "T-10": {
        # La memoria M11 completa: la Fase 9 en el HTML, del punto y del
        # proyecto (INF-3.4.7), y la seccion del cabezal por punto con sus
        # tablas, sus formulas sustituidas y sus FS (INF-4.7, con la salvedad
        # escrita en su fila: el programa no produce planos a los que
        # remitir). El prompt cita «INF-5.1.9» por INF-5.1.10, que cerro T-0
        # y figura arriba con su prompt: T-10 le deja una NOTA (el indice
        # regenerado con corridas que dimensionan) sin cambiarle el estado.
        ESTADO_CERRADO: {"INF-3.4.7", "INF-4.7"},
    },
    "T-11": {
        # La validacion integral de las tres familias. INF-0.5 se cierra CON
        # SALVEDAD escrita en la fila (precedente INF-4.2): a perfil el
        # fixture dimensiona sin declarar nada; a expediente, con todos los
        # datos puestos, siguen deteniendo por DECISION del dueño
        # 'remanso_derecho_via', 'TR_evento_extremo',
        # 'umbral_no_colapso_evento_extremo' y 'categoria_refuerzo_aashto'.
        # INF-3.4.3 e INF-3.4.6 los cerro T-7b y T-11 los verifico (la fila
        # lo dice); INF-3.4.4 queda en parte (E4/E5 sin evaluar, Meyerhof en
        # talud vacio, zapata sin iterar). INF-3.2.2 e INF-5.1.8 ganan una
        # NOTA sin cambiar de estado (siguen en las filas de T-2 y T-9).
        ESTADO_CERRADO: {"INF-0.5", "INF-3.4.3", "INF-3.4.6"},
        ESTADO_PARCIAL: {"INF-3.4.4"},
    },
    "T-12": {
        # El repositorio listo para la sustentacion, el ultimo de la cadena.
        # INF-5.2.2 (material de proceso) e INF-5.2.3 (PDF con copyright) se
        # cierran CON SALVEDAD escrita en su fila (precedente INF-0.5): cinco
        # documentos tecnicos de origen de proceso siguen en docs/, y los PDF
        # siguen en la historia de git (decision del dueño: no se reescribe).
        # INF-5.2.6 queda en parte (las 12 fuentes ausentes son entradas del
        # dueño). INF-5.2.1 gana una NOTA y sigue «Abierto»: el prompt no trae
        # accion para el.
        ESTADO_CERRADO: {"INF-5.2.2", "INF-5.2.3", "INF-5.2.4", "INF-5.2.7"},
        ESTADO_PARCIAL: {"INF-5.2.6"},
    },
}


@pytest.fixture(scope="module")
def filas():
    return tracker.hallazgos()


@pytest.fixture(scope="module")
def filas_inf(filas):
    return {f["ID"]: f for f in filas if f["ID"].startswith("INF-")}


def _ids_esperados():
    ids = set(ITEMS_DE_LA_SECCION_0)
    for prefijo, cuantos in ITEMS_DEL_INFORME.items():
        ids |= {f"{prefijo}{k}" for k in range(1, cuantos + 1)}
    return ids


def test_el_tracker_tiene_una_fila_por_hallazgo_del_INFORME(filas, filas_inf):
    assert set(filas_inf) == _ids_esperados()
    assert len({f["ID"] for f in filas}) == len(filas), "IDs repetidos en el tracker"


def test_cada_fila_INF_lleva_severidad_cluster_prompt_y_estado(filas_inf):
    assert filas_inf, "el tracker no tiene filas INF-"
    for id_, f in filas_inf.items():
        assert f["Severidad"].strip(), id_
        assert re.fullmatch(r"C\d\d", f["Cluster"]), (id_, f["Cluster"])
        assert f["Hallazgo"].strip() and f["Ubicación (archivo:línea del informe)"].strip(), id_
        # La columna «Fase» dice que prompt lo cierra, o que ninguno lo nombra.
        assert re.search(r"T-\d", f["Fase"]) or "ningún prompt" in f["Fase"], (id_, f["Fase"])
        assert f["Estado"] in ESTADOS_DE_UNA_FILA_INF, (id_, f["Estado"])


def test_cada_prompt_escribe_los_estados_que_dice_y_deja_abiertos_los_demas(filas_inf):
    """
    Hasta T-2 se llamaba `test_T0_cierra_los_que_dice_y_deja_abiertos_los_
    demas` y fijaba que los cerrados fueran exactamente los de T-0. Fija lo
    mismo para cada prompt que integra: las filas que dice, con el estado que
    dice, su responsable y su commit; y ninguna otra fila INF- fuera de
    «Abierto» o «N/A».
    """
    for estado in (ESTADO_CERRADO, ESTADO_PARCIAL, ESTADO_VERIFICADO):
        en_el_tracker = {i for i, f in filas_inf.items() if f["Estado"] == estado}
        declarados = set()
        for prompt, por_estado in LO_QUE_ESCRIBIO_CADA_PROMPT.items():
            for id_ in por_estado.get(estado, ()):
                declarados.add(id_)
                assert prompt in filas_inf[id_]["Commit / PR"], id_
                assert f"cadena T, {prompt}" in filas_inf[id_]["Responsable"], id_
        assert en_el_tracker == declarados, estado
    # Un mismo hallazgo no figura en dos estados ni en dos prompts.
    todos = [i for por_estado in LO_QUE_ESCRIBIO_CADA_PROMPT.values()
             for ids in por_estado.values() for i in ids]
    assert len(todos) == len(set(todos))
    # Lo que el INFORME reviso y dio por correcto no es trabajo pendiente.
    sin_trabajo = {i for i, f in filas_inf.items() if f["Estado"] == "N/A (sin trabajo)"}
    assert sin_trabajo == {"INF-3.2.3", "INF-3.3.2", "INF-3.3.6"}
    for id_ in sin_trabajo:
        assert filas_inf[id_]["Severidad"] == "OK"


@pytest.mark.parametrize("prompt,alias,canonico",
                         [(p, a, c) for (p, a), c in sorted(ALIAS_DE_LA_CADENA.items())])
def test_cada_alias_de_la_cadena_lleva_a_una_sola_fila(prompt, alias, canonico, filas_inf):
    """
    La cadena cita `INF-5.1.9` (T-0, T-10) para lo que el INFORME numera 10,
    `INF-5.1.11` para dos items distintos (T-8 y T-9), y asi. Cada alias
    queda escrito en «Vinculos cruzados» de SU fila, con el prompt que lo
    usa, y en ninguna otra con ese mismo prompt.
    """
    marca = f"{prompt} la cita como «{alias}"
    con_la_marca = [i for i, f in filas_inf.items() if marca in f["Vínculos cruzados"]]
    assert con_la_marca == [canonico], (marca, con_la_marca)


def test_la_tabla_de_equivalencias_esta_en_la_copia_de_la_cadena():
    texto = CADENA.read_text(encoding="utf-8")
    nota = texto.split(MARCA_DE_COPIA)[0]
    for (prompt, alias), canonico in ALIAS_DE_LA_CADENA.items():
        assert any(prompt in linea and alias in linea and canonico in linea
                   for linea in nota.split("\n")), (prompt, alias, canonico)


def test_verificar_sesion_busca_los_PDF_por_la_misma_puerta():
    arbol = ast.parse(VERIFICAR_SESION.read_text(encoding="utf-8"))
    atributos = {n.attr for n in ast.walk(arbol) if isinstance(n, ast.Attribute)}
    assert {"ruta_pdf", "directorios_de_normas"} <= atributos
    constantes = {n.targets[0].id: n.value for n in arbol.body
                  if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
    assert ast.literal_eval(constantes["HALLAZGOS_EN_LA_MATRIZ"]) == len(tracker.hallazgos())


# ===========================================================================
# 6. La copia de la cadena en proceso/planes_mejora
# ===========================================================================

MARCA_DE_COPIA = "<!-- COPIA FIEL: desde la linea siguiente, sin editar -->\n"


def test_la_copia_de_la_cadena_no_se_edita_sin_que_se_note():
    """
    El original vive en otro repositorio y la suite no puede leerlo: lo que
    se fija es que el cuerpo copiado conserve la huella que la nota declara.
    """
    texto = CADENA.read_text(encoding="utf-8")
    assert texto.count(MARCA_DE_COPIA) == 1
    nota, cuerpo = texto.split(MARCA_DE_COPIA)
    declarada = re.search(r"sha1 del original: `([0-9a-f]{40})`", nota)
    assert declarada, "la nota del orquestador perdio la huella del original"
    assert hashlib.sha1(cuerpo.encode("utf-8")).hexdigest() == declarada.group(1)
    assert cuerpo.startswith("# Cadena de prompts T")
    for n in ("T-0", "T-1", "T-7a", "T-7b", "T-7c", "T-12"):
        assert f"### {n} · " in cuerpo, n
