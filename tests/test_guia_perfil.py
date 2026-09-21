"""
tests/test_guia_perfil.py
=========================
La guardia de `docs/guia_perfil.md` (PF-5): la guia de corrida de perfil para
un tesista que no ha leido el codigo, que NO se escribe a mano dos veces.

Dos cosas se comprueban, y las dos contra la guia tal como esta en disco:

  1. LOS BLOQUES DE COMANDOS CORREN. Cada cerca `sh id=...` de la guia se
     ejecuta en subproceso, en el orden en que la guia la presenta, con los
     archivos que la propia guia muestra (las cercas `archivo=...` se
     escriben a disco tal cual) y con el CSV de trabajo derivado de
     `tests/ejemplo_puntos.csv` como la guia dice (una celda). Lo unico que
     se sustituye es `python`, `cli.py` y las rutas `tests/...`. Se afirma lo
     que la guia promete: el RESUMEN que imprime (las cercas
     `text id=resumen_*`, linea a linea, contra la salida real), los cuatro
     puntos dimensionados al final, la advertencia de corredor cuando no se
     declara sitio, el codigo de salida de cada comando.

  2. LAS LISTAS SALEN DE SUS SIMBOLOS. Las tablas entre `<!-- generado: X -->`
     y `<!-- fin: X -->` se comparan con lo que `tests/apoyo/guia_perfil.py`
     deriva de `M0_carga.COLUMNAS`, `VACIOS_ADMITIDOS`, `servicio.CLAVES_EXTERNAS`,
     `datos_sitio.DATOS_SITIO`, `ca.criterios_de_perfil_sin_valor()`,
     `M11.COLUMNAS_RESUMEN_CSV` y `sesion.sesion_vacia`, como los cuatro
     documentos generados de `docs/`: si un criterio cambia de forma, este
     archivo lo dice. Se regeneran con `python -m tests.apoyo.guia_perfil`.

Y los ejemplos de `--declarar` de la guia pasan la puerta real
(`cli.declarar_criterios`) y cubren cada uno de los criterios de perfil sin
valor, con todas sus formas. La guia dice COMO se declara y no QUE: aqui no
se afirma ningun valor de proyecto, solo que la sintaxis entra.
"""
from __future__ import annotations

import csv
import json
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import sesion
from src.modulos import M11_reporte as M11
from tests.apoyo import guia_perfil as gp

RAIZ = Path(__file__).resolve().parents[1]
GUIA = RAIZ / "docs" / "guia_perfil.md"
README = RAIZ / "README.md"
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"

TEXTO = GUIA.read_text(encoding="utf-8")
BLOQUES = gp.bloques_de_la_guia(TEXTO)
POR_ID = {b.id: b for b in BLOQUES if b.id}
ARCHIVOS = {b.archivo: b for b in BLOQUES if b.archivo}

# El orden en que la guia presenta sus comandos, que es tambien el orden de
# dependencias: `comparar` lee los JSON de `sin_cajon` y `perfil`, `sesion` y
# `pdf` leen la sesion que reproduce a `perfil`. `pdf` corre aparte (lento).
ORDEN_EN_LA_GUIA = ("prevuelo_vacio", "prevuelo_completo", "sin_cajon", "perfil",
                    "sesion", "pdf", "comparar", "barrido")
CORRIDAS = tuple(i for i in ORDEN_EN_LA_GUIA if i != "pdf")
ARCHIVOS_DE_LA_GUIA = ("guia/externos.json", "guia/sitio.json", "guia/sesion.json")
CSV_DE_TRABAJO = "guia/puntos.csv"
ID_PUNTO_QUE_LA_GUIA_RELLENA = "C-01"
COLUMNA_QUE_LA_GUIA_RELLENA = "cota_coronacion_canal"
PUNTOS_DEL_EJEMPLO = 4
# La clave del barrido de la guia y el resto de los siete del cajon, que el
# comando del barrido declara aparte.
CLAVE_DEL_BARRIDO = "n_celdas_cajon"
TEXTO_DEL_BARRIDO = "Barrido de"
TEXTO_ADVERTENCIA = "Advertencia de corredor"
TEXTO_SITIO_DECLARADO = "datos_sitio.py no se modifico"
TEXTO_SESION_RESTAURADA = "Criterios restaurados de la sesion"
TEXTO_COMPARAR = "DIFIEREN"
PRIMER_CRITERIO_DEL_CAJON = "embocadura_cajon"


def _comando(bloque: gp.BloqueDeLaGuia) -> list:
    """El comando de la guia con las tres sustituciones que el test se permite."""
    tokens = bloque.comando()
    salida = []
    for i, t in enumerate(tokens):
        if i == 0 and t == "python":
            salida.append(sys.executable)
        elif t == "cli.py":
            salida.append(str(RAIZ / "cli.py"))
        elif t.startswith("tests/"):
            salida.append(str(RAIZ / t))
        else:
            salida.append(t)
    return salida


def _declarados_en(bloque: gp.BloqueDeLaGuia) -> dict:
    """{clave: texto} de cada `--declarar CLAVE=VALOR` de un bloque `sh`."""
    tokens = bloque.comando()
    return {t.partition("=")[0]: t.partition("=")[2]
            for anterior, t in zip(tokens, tokens[1:]) if anterior == "--declarar"}


def _fila_c01_del_ejemplo() -> str:
    for linea in CSV_EJEMPLO.read_text(encoding="utf-8").splitlines():
        if linea.startswith(ID_PUNTO_QUE_LA_GUIA_RELLENA + ","):
            return linea
    raise AssertionError(f"{CSV_EJEMPLO.name} ya no trae la fila {ID_PUNTO_QUE_LA_GUIA_RELLENA}")


def _csv_de_trabajo(destino: Path) -> None:
    """`tests/ejemplo_puntos.csv` con la fila C-01 de la guia en vez de la suya."""
    original = _fila_c01_del_ejemplo()
    texto = CSV_EJEMPLO.read_text(encoding="utf-8")
    destino.write_text(texto.replace(original + "\n", POR_ID["fila_c01"].cuerpo + "\n"),
                       encoding="utf-8")


class Taller:
    """La carpeta de trabajo de la guia y el resultado de cada comando."""

    def __init__(self, raiz: Path) -> None:
        self.raiz = raiz
        self.resultados: dict = {}

    def preparar(self) -> None:
        (self.raiz / "guia" / "salida").mkdir(parents=True)
        for ruta, bloque in ARCHIVOS.items():
            (self.raiz / ruta).write_text(bloque.cuerpo + "\n", encoding="utf-8")
        _csv_de_trabajo(self.raiz / CSV_DE_TRABAJO)

    def correr(self, id_bloque: str) -> subprocess.CompletedProcess:
        hecho = subprocess.run(_comando(POR_ID[id_bloque]), cwd=self.raiz,
                               capture_output=True, text=True, timeout=600)
        self.resultados[id_bloque] = hecho
        return hecho

    def json(self, relativa: str) -> dict:
        return json.loads((self.raiz / relativa).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def taller(tmp_path_factory) -> Taller:
    t = Taller(tmp_path_factory.mktemp("guia_perfil"))
    t.preparar()
    for id_bloque in CORRIDAS:
        t.correr(id_bloque)
    return t


def _punto(informe: dict, id_punto: str) -> dict:
    return next(p for p in informe["puntos"] if p["id"] == id_punto)


def _diagnostico(hecho: subprocess.CompletedProcess) -> str:
    return f"rc={hecho.returncode}\n--- stdout ---\n{hecho.stdout[-3000:]}\n--- stderr ---\n{hecho.stderr[-3000:]}"


# ===========================================================================
# 1 - La guia tiene exactamente los bloques que este test conoce
# ===========================================================================

def test_la_guia_presenta_sus_comandos_en_el_orden_de_dependencias():
    ids_sh = tuple(b.id for b in BLOQUES if b.lenguaje == "sh")
    assert ids_sh == ORDEN_EN_LA_GUIA, ids_sh
    assert all(b.id for b in BLOQUES if b.lenguaje == "sh"), "todo bloque sh lleva id="
    assert tuple(ARCHIVOS) == ARCHIVOS_DE_LA_GUIA, tuple(ARCHIVOS)
    for id_texto in ("fila_c01", "resumen_sin_cajon", "resumen_perfil", "ejemplos_declarar"):
        assert id_texto in POR_ID, f"la guia perdio el bloque {id_texto}"


def test_el_readme_enlaza_la_guia():
    assert "docs/guia_perfil.md" in README.read_text(encoding="utf-8")


# ===========================================================================
# 2 - Sincronia: las listas de la guia salen de sus simbolos
# ===========================================================================

def test_la_guia_tiene_los_mismos_bloques_generados_que_el_generador():
    assert set(gp.bloques_generados_en(TEXTO)) == set(gp.GENERADORES)


@pytest.mark.parametrize("nombre", sorted(gp.GENERADORES))
def test_el_bloque_generado_esta_sincronizado(nombre):
    en_disco = gp.bloques_generados_en(TEXTO)[nombre]
    assert en_disco == gp.GENERADORES[nombre](), (
        f"el bloque «{nombre}» de docs/guia_perfil.md esta desincronizado con "
        "los simbolos de los que sale. NO se edita a mano: se regenera con "
        "`python -m tests.apoyo.guia_perfil` y se pega entre sus marcas")


def test_los_criterios_de_la_guia_son_los_de_perfil_sin_valor_con_su_forma():
    """La tabla nombra cada clave con SU forma: si una cambia, la fila cambia."""
    tabla = gp.bloques_generados_en(TEXTO)["criterios"]
    for clave in ca.criterios_de_perfil_sin_valor():
        c = ca.CRITERIOS[clave]
        assert f"| `{clave}` | [{c.etiqueta}] | `{c.forma}` |" in tabla, clave


# ===========================================================================
# 3 - El CSV de trabajo: una celda rellenada sobre el ejemplo del repositorio
# ===========================================================================

def test_la_fila_c01_de_la_guia_es_la_del_ejemplo_con_la_coronacion_rellenada():
    original = _fila_c01_del_ejemplo().split(",")
    de_la_guia = POR_ID["fila_c01"].cuerpo.split(",")
    columnas = CSV_EJEMPLO.read_text(encoding="utf-8").splitlines()[0].split(",")
    indice = columnas.index(COLUMNA_QUE_LA_GUIA_RELLENA)
    assert len(de_la_guia) == len(original) == len(columnas)
    assert original[indice] == "", "el ejemplo del repositorio ya trae la coronacion"
    assert de_la_guia[indice] != "", "la guia no rellena la coronacion"
    resto = [i for i in range(len(columnas)) if i != indice]
    assert [de_la_guia[i] for i in resto] == [original[i] for i in resto]


# ===========================================================================
# 4 - Las corridas, una a una, en el orden de la guia
# ===========================================================================

def test_el_prevuelo_del_csv_de_ejemplo_sale_con_1_y_nombra_la_luz_y_la_coronacion(taller):
    hecho = taller.resultados["prevuelo_vacio"]
    assert hecho.returncode == 1, _diagnostico(hecho)
    assert "luz_m" in hecho.stdout and COLUMNA_QUE_LA_GUIA_RELLENA in hecho.stdout


def test_el_prevuelo_con_el_csv_de_trabajo_y_el_json_sale_con_0(taller):
    hecho = taller.resultados["prevuelo_completo"]
    assert hecho.returncode == 0, _diagnostico(hecho)


def test_sin_sitio_ni_cajon_la_corrida_advierte_del_corredor_y_dice_su_resumen(taller):
    hecho = taller.resultados["sin_cajon"]
    assert hecho.returncode == 1, _diagnostico(hecho)
    assert TEXTO_ADVERTENCIA in hecho.stdout
    for linea in POR_ID["resumen_sin_cajon"].cuerpo.splitlines():
        assert linea in hecho.stdout, f"la guia promete «{linea}»\n{_diagnostico(hecho)}"
    informe = taller.json("guia/salida/sin_cajon.informe.json")
    assert informe["expediente"]["dimensionados"] == PUNTOS_DEL_EJEMPLO - 1
    assert not _punto(informe, ID_PUNTO_QUE_LA_GUIA_RELLENA)["dimensionado"]
    assert not informe["expediente"]["cerrado"]
    # La cebolla: la corrida nombra el PRIMER criterio del cajon que encontro,
    # que es el que la guia dice; los diez los listo el pre-vuelo.
    assert PRIMER_CRITERIO_DEL_CAJON in hecho.stdout


def test_la_corrida_de_perfil_dimensiona_los_cuatro_y_dice_su_resumen(taller):
    hecho = taller.resultados["perfil"]
    assert hecho.returncode == 0, _diagnostico(hecho)
    assert TEXTO_ADVERTENCIA not in hecho.stdout
    assert TEXTO_SITIO_DECLARADO in hecho.stdout
    for linea in POR_ID["resumen_perfil"].cuerpo.splitlines():
        assert linea in hecho.stdout, f"la guia promete «{linea}»\n{_diagnostico(hecho)}"
    informe = taller.json("guia/salida/perfil.informe.json")
    assert informe["expediente"]["dimensionados"] == PUNTOS_DEL_EJEMPLO
    assert informe["expediente"]["cerrado"] is True
    assert all(p["dimensionado"] for p in informe["puntos"])
    assert len(informe["puntos"]) == PUNTOS_DEL_EJEMPLO
    # Los [S] de esta corrida salieron del sitio.json de la guia, no del archivo.
    assert informe["expediente"]["corredor_del_proyecto"]["origen"].endswith("sitio.json")
    # La regla que C-01 necesita: S_conducto >= S_cauce, leida del volcado.
    c01 = _punto(informe, ID_PUNTO_QUE_LA_GUIA_RELLENA)
    assert c01["geometria"]["S_conducto"] >= c01["datos_declarados"]["S_cauce"]["valor"]


def test_la_corrida_de_perfil_deja_la_memoria_y_el_cuadro_resumen(taller):
    assert (taller.raiz / "guia" / "salida" / "memoria.html").stat().st_size > 0
    with (taller.raiz / "guia" / "salida" / "resumen.csv").open(encoding="utf-8", newline="") as f:
        filas = list(csv.reader(f))
    assert tuple(filas[0]) == tuple(M11.COLUMNAS_RESUMEN_CSV)
    assert len(filas) - 1 == PUNTOS_DEL_EJEMPLO


def test_la_sesion_de_la_guia_es_valida_y_reproduce_la_corrida_de_perfil(taller):
    datos = json.loads(ARCHIVOS["guia/sesion.json"].cuerpo)
    assert sesion.errores_de_sesion(datos) == []
    assert datos["formato_version"] == sesion.FORMATO_SESION
    # Los criterios de la sesion son EXACTAMENTE los siete que el comando de
    # perfil declara: la guia no puede decir una cosa en cada bloque.
    declarados = _declarados_en(POR_ID["perfil"])
    assert set(datos["criterios"]["valores"]) == set(declarados)
    hecho = taller.resultados["sesion"]
    assert hecho.returncode == 0, _diagnostico(hecho)
    assert TEXTO_SESION_RESTAURADA in hecho.stdout
    informe = taller.json("guia/salida/desde_sesion.informe.json")
    assert informe["expediente"]["dimensionados"] == PUNTOS_DEL_EJEMPLO
    assert informe["expediente"]["cerrado"] is True


def test_comparar_las_dos_corridas_dice_que_difieren(taller):
    hecho = taller.resultados["comparar"]
    assert hecho.returncode == 1, _diagnostico(hecho)
    assert TEXTO_COMPARAR in hecho.stdout


def test_el_barrido_corre_una_vez_por_valor_y_declara_los_otros_seis(taller):
    hecho = taller.resultados["barrido"]
    assert hecho.returncode == 0, _diagnostico(hecho)
    assert TEXTO_DEL_BARRIDO in hecho.stdout
    volcado = taller.json("guia/salida/barrido.json")
    assert [b["clave"] for b in volcado["barridos"]] == [CLAVE_DEL_BARRIDO]
    assert len(volcado["barridos"][0]["corridas"]) == 2
    # Los seis declarados del barrido son los siete de perfil menos la clave barrida.
    del_perfil = _declarados_en(POR_ID["perfil"])
    del_barrido = _declarados_en(POR_ID["barrido"])
    assert set(del_barrido) == set(del_perfil) - {CLAVE_DEL_BARRIDO}
    assert all(del_barrido[k] == del_perfil[k] for k in del_barrido)


@pytest.mark.lento
def test_el_pdf_por_la_sesion_se_escribe_o_deja_el_html_con_su_mensaje(taller):
    """
    Como `test_cli.test_bandera_pdf_escribe_o_deja_el_html_con_su_mensaje`:
    --pdf tiene dos finales declarados, y la guia los dice los dos.
    """
    hecho = taller.correr("pdf")
    assert hecho.returncode == 0, _diagnostico(hecho)
    destino = taller.raiz / "guia" / "salida" / "memoria.pdf"
    if destino.is_file():
        assert destino.stat().st_size > 0
    else:
        assert destino.with_suffix(".html").is_file(), _diagnostico(hecho)
        assert "html" in hecho.stdout.lower()


# ===========================================================================
# 5 - Los ejemplos de --declarar: sintaxis valida, uno por criterio, todas las formas
# ===========================================================================

def _ejemplos() -> list:
    lineas = POR_ID["ejemplos_declarar"].cuerpo.splitlines()
    ejemplos = []
    for linea in lineas:
        tokens = shlex.split(linea)
        assert tokens[0] == "--declarar" and len(tokens) == 2, linea
        ejemplos.append(tokens[1])
    return ejemplos


def test_hay_un_ejemplo_por_criterio_de_perfil_sin_valor_y_cubren_todas_las_formas():
    claves = [e.partition("=")[0] for e in _ejemplos()]
    assert claves == ca.criterios_de_perfil_sin_valor(), (
        "la guia ejemplifica exactamente los criterios de perfil sin valor, en su orden")
    formas = {ca.CRITERIOS[k].forma for k in claves}
    assert formas == {ca.CRITERIOS[k].forma for k in ca.criterios_de_perfil_sin_valor()}


@pytest.mark.parametrize("ejemplo", _ejemplos(), ids=lambda e: e.partition("=")[0])
def test_cada_ejemplo_de_declarar_pasa_la_puerta_real(ejemplo):
    clave = ejemplo.partition("=")[0]
    try:
        assert cli.declarar_criterios([ejemplo]) == [clave]
        assert ca.criterio_efectivo(clave).valor is not None
    finally:
        if ca.declarado_en_caliente(clave):
            ca.quitar_valor_dinamico(clave)
