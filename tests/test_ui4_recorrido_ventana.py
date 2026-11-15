"""
tests/test_ui4_recorrido_ventana.py
===================================
La aceptacion de UI-4 (cadena de interfaz): LA VENTANA VERIFICADA DE
EXTREMO A EXTREMO, con lo que UI-1 a UI-3 le llevaron, sobre las tres
corridas de referencia (`src/indice_formulas.CORRIDAS_DE_REFERENCIA`) y el
CSV de ejemplo. UI-4 no añade funciones; lo que vigila, en el orden del
prompt:

(a) Lo que el recorrido encontro, y lo que UI-2 y UI-3 dejaron escrito para
    UI-4 (ficha UI4-01), cada uno con su test sin ventana:
    (a1) la tabla de la ventana del barrido nacia con alto CERO: el divisor
         del `PanedWindow` VERTICAL se colocaba con el ANCHO del evento
         (`componentes.repartir_al_mostrar`), y la tabla que el barrido
         escribe no se veia sin arrastrar el divisor (las capturas lo
         mostraron; los tests de UI-3 leian el texto del widget);
    (a2) cerrar la ventana PRINCIPAL con un PDF en marcha dejaba el hijo
         huerfano y su carpeta en el temporal (ficha UI3-02, abierto (3));
    (a3) a 1100 px la primera fila de exportacion no cabia: «Exportar
         cuadro resumen (CSV)» salia cortado y «Comparar con otro JSON...»
         fuera de la vista (ficha UI2-01, abierto (c)).
(b) El README de usuario dice donde esta en la ventana la hidrologia, la
    memoria resumida, el cabezal del proyecto y el barrido, con las
    capturas de `docs/capturas_interfaz/`, y no manda a la CLI lo que la
    ventana ya hace.
(c) El recorrido sobre la ventana de verdad bajo xvfb
    (`tests/apoyo/gui_ui4_recorrido_real.py`, un proceso aparte): cargar
    las entradas por «Examinar...», declarar por la pestaña 2, ejecutar a
    perfil y a expediente (el JSON de la ventana es el de la CLI con las
    mismas entradas, y el del CSV de ejemplo es la linea base), el detalle
    de la pestaña 3 y el panel del cabezal de la pestaña 4 con el texto de
    la CLI, los seis exportadores (los dos PDF por el hijo, con la
    hidrologia), «Guardar sesion» / «Nuevo proyecto» / «Cargar sesion» y
    otra vez EJECUTAR (el mismo JSON), la sesion v3 de prueba, un barrido,
    las capturas, y el cierre con un PDF en marcha.

Los tests de (a) y (b), y los de (c) que miden (a1)-(a3), se escribieron
PRIMERO, en rojo (`xfail(strict=True)`), y se liberaron al corregir. Los
demas de (c) verifican lo que UI-1 a UI-3 ya hacian: no tenian rojo que
medir, y se dice (ficha UI4-01). Todo son DATOS DE PRUEBA.

Y lo que la revision independiente de UI-4 encontro (ficha UI4-03): el hijo
del PDF que YA salio cuando se cierra la ventana se cierra como el sondeo
que no llego a hacerse (su PDF se entrega; un fallo no toca el destino), y
el ciclo guardar / «Nuevo proyecto» / cargar se hace a PERFIL y con una
bandera tecleada, que no es lo que «Nuevo proyecto» deja, para que reponer
el alcance y las banderas se compruebe de verdad (los dos, medidos por
mutacion).
"""

from __future__ import annotations

import ast
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import cli
from src import indice_formulas as ind
from src import sesion as ses
from src.modulos import M11_reporte as M11
from tests.apoyo import doble_tkinter
from tests.apoyo import gui_ui4_recorrido_real as recorrido

RAIZ = Path(__file__).resolve().parents[1]
GUI = RAIZ / "gui" / "app.py"
README = RAIZ / "README.md"
CAPTURAS = RAIZ / "docs" / "capturas_interfaz"
LINEA_BASE = RAIZ / "tests" / "linea_base_familia_c"
ARBOL_GUI = ast.parse(GUI.read_text(encoding="utf-8-sig"), filename="app.py")

# El segundo en que se declaro cada valor de un barrido: lo UNICO en que la
# tabla de la ventana y la de la CLI pueden diferir (ficha UI3-01).
SEGUNDO_DE_LA_DECLARACION = re.compile(r"declarado el \d{4}-\d\d-\d\dT\d\d:\d\d:\d\d")
# Lineas de la tabla del barrido que tienen que verse sin desplazar nada: el
# titulo, la cabecera y la primera fila.
LINEAS_DEL_BARRIDO_A_LA_VISTA = 3
FIRMA_PNG = b"\x89PNG\r\n\x1a\n"
TOPE_S = 900


# ---------------------------------------------------------------------------
# Apoyos
# ---------------------------------------------------------------------------

def _es_separador(linea):
    limpia = linea.strip()
    return bool(limpia) and set(limpia) <= {"-", "="}


def _palabras(lineas):
    """Lo que «ni una palabra distinta» compara (el criterio de UI-2)."""
    return [" ".join(l.split()) for l in lineas if l.strip() and not _es_separador(l)]


def _funcion(arbol, nombre):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and nodo.name == nombre:
            return nodo
    raise AssertionError(f"no se encontro la funcion {nombre}")


def _dimensiones_png(ruta):
    datos = ruta.read_bytes()
    assert datos[:8] == FIRMA_PNG, ruta
    ancho, alto = struct.unpack(">II", datos[16:24])
    return ancho, alto


# ===========================================================================
# (a1) El divisor de un PanedWindow vertical, por el alto
# ===========================================================================

class _PanedDoble:
    """Lo que `repartir_al_mostrar` usa de un `ttk.PanedWindow`, nada mas."""

    def __init__(self, orientacion, pesos=(3, 2)):
        self.orientacion = orientacion
        self.pesos = dict(zip(("arriba", "abajo"), pesos))
        self.al_configurar = None
        self.divisor = None

    def bind(self, evento, funcion, add=None):
        self.al_configurar = funcion
        return "id"

    def unbind(self, evento, identificador):
        pass

    def panes(self):
        return tuple(self.pesos)

    def pane(self, panel, opcion):
        return self.pesos[panel]

    def sashpos(self, indice, posicion):
        self.divisor = posicion

    def cget(self, opcion):
        assert opcion == "orient"
        return self.orientacion


def test_a1_el_divisor_vertical_se_reparte_por_el_alto():
    """
    La ventana del barrido mide 1016 x 526 px en su `PanedWindow`: con el
    ancho, 1016 * 3/5 = 609 px quedaba fuera de los 526 y Tk lo pegaba al
    fondo (medido: divisor en 520, la tabla sin mapear).
    """
    comp = doble_tkinter.gui_componentes()
    paned = _PanedDoble("vertical")
    comp.repartir_al_mostrar(paned)
    paned.al_configurar(SimpleNamespace(width=1016, height=526))
    assert paned.divisor == 526 * 3 // 5


def test_a1_el_divisor_horizontal_se_sigue_repartiendo_por_el_ancho():
    comp = doble_tkinter.gui_componentes()
    paned = _PanedDoble("horizontal")
    comp.repartir_al_mostrar(paned)
    paned.al_configurar(SimpleNamespace(width=1016, height=526))
    assert paned.divisor == 1016 * 3 // 5


# ===========================================================================
# (a2) Cerrar la ventana principal con un PDF en marcha
# ===========================================================================

def test_a2_el_hijo_del_pdf_se_termina_y_su_carpeta_se_retira(tmp_path):
    """
    `ProcesoPdf.terminar_y_limpiar`, con un hijo DE VERDAD que no termina
    solo: un `cli.py` de mentira en otra raiz que duerme. Termina, la
    carpeta de trabajo no queda y el destino del usuario no se toca. El hijo
    que ya termino, en el test siguiente.
    """
    import gui.exportacion_pdf as expdf

    raiz_falsa = tmp_path / "raiz"
    raiz_falsa.mkdir()
    (raiz_falsa / "cli.py").write_text("import time\ntime.sleep(600)\n", encoding="utf-8")
    destino = tmp_path / "destino.pdf"
    trabajo = tmp_path / "trabajo"
    proceso = expdf.ProcesoPdf(sesion={}, destino=destino, directorio_trabajo=trabajo,
                               vista=expdf.VISTA_RESUMIDA, raiz=raiz_falsa)
    proceso.iniciar()
    try:
        assert proceso.estado is expdf.EstadoPdf.EN_MARCHA
        proceso.terminar_y_limpiar(tope_s=TOPE_S)
    finally:
        if proceso._proceso is not None and proceso._proceso.poll() is None:
            proceso._proceso.kill()                 # el test no deja huerfanos
            proceso._proceso.wait()
    assert proceso._proceso.poll() is not None
    assert proceso.estado is expdf.EstadoPdf.CANCELADO
    assert not trabajo.exists()
    assert not destino.exists()
    # Sin arrancar tambien es un estado terminal y no deja nada.
    nunca = expdf.ProcesoPdf(sesion={}, destino=destino, directorio_trabajo=trabajo)
    nunca.terminar_y_limpiar(tope_s=TOPE_S)
    assert nunca.estado.terminal and not trabajo.exists()


# Dos `cli.py` de mentira que YA TERMINARON cuando la ventana se cierra: uno
# deja su PDF entero y sale con 0; el otro sale con 2 sin dejar nada.
_HIJO_QUE_ESCRIBE = (
    "import sys\n"
    "destino = sys.argv[sys.argv.index('--pdf-resumida') + 1]\n"
    "with open(destino, 'wb') as f:\n"
    "    f.write(b'%PDF-1.4\\n% hijo de prueba\\n%%EOF\\n')\n")
_HIJO_QUE_FALLA = "import sys\nsys.exit(2)\n"


@pytest.mark.parametrize("hijo, estado, entregado", [
    (_HIJO_QUE_ESCRIBE, "TERMINADO", True),
    (_HIJO_QUE_FALLA, "FALLIDO", False),
], ids=["con_su_pdf", "fallido"])
def test_a2_el_hijo_que_ya_termino_al_cerrar_se_cierra_como_el_sondeo(
        tmp_path, hijo, estado, entregado):
    """
    Revision de UI-4 (H1): el hijo puede haber SALIDO sin que la ventana lo
    haya sondeado todavia (el sondeo es cada `CADENCIA_SONDEO_PDF_MS`). Al
    cerrar se cierra como lo habria cerrado ese sondeo: el PDF entero que el
    usuario pidio se entrega (no se tira un trabajo terminado), y un hijo que
    fallo no toca el destino. En los dos, la carpeta de trabajo no queda.
    """
    import gui.exportacion_pdf as expdf

    raiz_falsa = tmp_path / "raiz"
    raiz_falsa.mkdir()
    (raiz_falsa / "cli.py").write_text(hijo, encoding="utf-8")
    destino = tmp_path / "destino.pdf"
    destino.write_bytes(b"el PDF anterior del usuario")
    trabajo = tmp_path / "trabajo"
    proceso = expdf.ProcesoPdf(sesion={}, destino=destino, directorio_trabajo=trabajo,
                               vista=expdf.VISTA_RESUMIDA, raiz=raiz_falsa)
    proceso.iniciar()
    proceso._proceso.wait(timeout=TOPE_S)
    assert proceso.estado is expdf.EstadoPdf.EN_MARCHA      # nadie lo sondeo aun
    proceso.terminar_y_limpiar(tope_s=TOPE_S)
    assert proceso.estado is getattr(expdf.EstadoPdf, estado), proceso.detalle
    if entregado:
        assert destino.read_bytes().startswith(b"%PDF")
    else:
        assert destino.read_bytes() == b"el PDF anterior del usuario"
    assert not trabajo.exists()


class _ProcesoDoble:
    def __init__(self):
        self.terminado_con = None

    def terminar_y_limpiar(self, tope_s):
        self.terminado_con = tope_s


def test_a2_la_ventana_termina_el_hijo_del_pdf_al_destruirse():
    """
    El `<Destroy>` de la ventana principal llega tambien por cada widget
    suyo: solo el de la RAIZ termina el hijo, con la espera acotada de la
    ventana del barrido (`proceso_barrido.TOPE_AL_TERMINAR_S`).
    """
    app = doble_tkinter.gui_app()
    v = app.ExpedienteApp.__new__(app.ExpedienteApp)
    v.root = object()
    v.proceso_pdf = _ProcesoDoble()
    v._al_destruirse(SimpleNamespace(widget=object()))
    assert v.proceso_pdf.terminado_con is None
    v._al_destruirse(SimpleNamespace(widget=v.root))
    assert v.proceso_pdf.terminado_con == app.pbarr.TOPE_AL_TERMINAR_S
    v.proceso_pdf = None
    v._al_destruirse(SimpleNamespace(widget=v.root))        # sin hijo: nada


def test_a2_la_ventana_engancha_su_destruccion():
    init = _funcion(ARBOL_GUI, "__init__")
    enganches = [n for n in ast.walk(init) if isinstance(n, ast.Call)
                 and ast.unparse(n.func) == "self.root.bind"
                 and n.args and isinstance(n.args[0], ast.Constant)
                 and n.args[0].value == "<Destroy>"]
    assert enganches, "la ventana no se entera de que la cierran"
    assert ast.unparse(enganches[0].args[1]) == "self._al_destruirse"
    assert any(k.arg == "add" for k in enganches[0].keywords)


# ===========================================================================
# (b) El README y las capturas
# ===========================================================================

def _seccion_de_la_ventana():
    """«La ventana», dentro de «4. Corrida»: hasta el siguiente titulo de sección."""
    texto = README.read_text(encoding="utf-8")
    inicio = texto.index("### La ventana")
    fin = texto.index("\n## ", inicio + 1)
    return texto[inicio:fin]


def _textos_de_la_gui():
    """Las cadenas de `gui/app.py`: los rotulos que la ventana pone."""
    return {n.value for n in ast.walk(ARBOL_GUI)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def test_b_el_readme_tiene_la_seccion_de_la_ventana_con_sus_capturas():
    seccion = _seccion_de_la_ventana()
    referidas = re.findall(r"\(docs/capturas_interfaz/([^)]+\.png)\)", seccion)
    assert sorted(referidas) == sorted(recorrido.CAPTURAS)
    for nombre in referidas:
        assert (CAPTURAS / nombre).is_file(), nombre


def test_b_las_capturas_son_png_de_la_ventana():
    """Las de la ventana principal miden la geometria de las capturas; la del barrido, la suya."""
    ancho, alto = (int(x) for x in
                   recorrido.GEOMETRIA_DE_LAS_CAPTURAS.split("+")[0].split("x"))
    for nombre in recorrido.CAPTURAS:
        dimensiones = _dimensiones_png(CAPTURAS / nombre)
        if nombre.startswith("pestana_"):
            assert dimensiones == (ancho, alto), nombre
        else:
            assert dimensiones[0] > ancho // 2 and dimensiones[1] > alto // 2, nombre
    assert sorted(p.name for p in CAPTURAS.iterdir()) == sorted(recorrido.CAPTURAS)


@pytest.mark.parametrize("cosa, pestana, palabras", [
    ("hidrologia", "1", ("CSV de cuencas", "CSV de la estación")),
    ("memoria resumida", "4", ("Memoria resumida (HTML)", "Memoria resumida (PDF)")),
    ("cabezal del proyecto", "4", ("Cabezal del proyecto",)),
    ("barrido", "2", ("Barrido…",)),
])
def test_b_el_readme_dice_donde_esta_cada_cosa_en_la_ventana(cosa, pestana, palabras):
    """
    Cada una en el parrafo de SU pestaña, con el rotulo que la ventana le
    pone: el del README tiene que ser un texto de `gui/app.py` (el de un
    boton o un panel, o el de un campo sin su «(opcional):»).
    """
    seccion = _seccion_de_la_ventana()
    parrafo = next(" ".join(p.split()) for p in seccion.split("\n\n")
                   if f"**Pestaña {pestana}" in p)
    textos = _textos_de_la_gui()
    for palabra in palabras:
        assert palabra in parrafo, (cosa, palabra)
        assert palabra in textos or f"{palabra} (opcional):" in textos, (cosa, palabra)


def test_b_el_readme_no_manda_a_la_cli_lo_que_la_ventana_hace():
    """
    Las frases que mandaban a la CLI lo que la ventana ya hace (la resumida,
    la hidrologia, el barrido) no vuelven, y lo que solo hace la CLI se dice
    como tal en la seccion de la ventana: las dos memorias en una invocacion
    (la resumida que nombra su completa) y `--plantilla`.
    """
    texto = " ".join(README.read_text(encoding="utf-8").split())
    for frase in ("la resumida se obtiene con la CLI",
                  "la resumida sale de la sesión guardada",
                  "Desde la ventana se exporta la completa;",
                  "El botón «memoria resumida» en la ventana",
                  "la hidrología entra sólo por la CLI",
                  "el barrido sólo por la CLI"):
        assert frase not in texto, frase
    seccion = " ".join(_seccion_de_la_ventana().split())
    assert "Lo que sólo hace la CLI" in seccion and "`--plantilla`" in seccion


# ===========================================================================
# (c) El recorrido sobre la ventana de verdad
# ===========================================================================

def _interprete_con_ventana():
    from tests.test_gui_contrato import _ENVOLTORIO, _INTERPRETE
    return _INTERPRETE, _ENVOLTORIO


@pytest.fixture(scope="module")
def r(tmp_path_factory):
    interprete, envoltorio = _interprete_con_ventana()
    if interprete is None:
        pytest.skip("ningun interprete disponible puede levantar una ventana "
                    "(falta tkinter, ttkbootstrap o el entorno grafico)")
    salida = tmp_path_factory.mktemp("ui4_recorrido")
    argumentos = [str(salida)]
    if shutil.which("import") is not None:
        argumentos += ["--capturas", str(salida / "capturas")]
    hecho = subprocess.run(
        envoltorio + [interprete, "-m", "tests.apoyo.gui_ui4_recorrido_real", *argumentos],
        cwd=RAIZ, capture_output=True, text=True, timeout=TOPE_S * 2)
    assert hecho.returncode == 0, (
        f"el recorrido fallo:\n{hecho.stdout[-6000:]}\n{hecho.stderr[-4000:]}")
    datos = json.loads((salida / "recorrido_ui4.json").read_text(encoding="utf-8"))
    return SimpleNamespace(salida=salida, datos=datos)


def _json(salida, nombre):
    return json.loads((salida / nombre).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def json_de_la_cli(tmp_path_factory):
    """El JSON que `cli.py` escribe con las MISMAS entradas que la ventana tecleo."""
    salida = tmp_path_factory.mktemp("ui4_cli")
    hechos = {}
    for referencia in ind.CORRIDAS_DE_REFERENCIA:
        destino = salida / f"{referencia.nombre}.json"
        hecho = subprocess.run(
            [sys.executable, str(RAIZ / "cli.py"), *recorrido.argumentos_de_la_cli(referencia),
             "--json", str(destino)],
            cwd=RAIZ, capture_output=True, text=True, timeout=TOPE_S)
        assert hecho.returncode in (0, 1), hecho.stderr[-3000:]
        hechos[referencia.nombre] = json.loads(destino.read_text(encoding="utf-8"))
    return hechos


def test_c0_recien_abierta_todo_apagado_y_diciendo_por_que(r):
    abierta = r.datos["recien_abierta"]
    # Los siete, nombrados AQUI y no leidos de la tupla de la que el recorrido
    # los lee (revision de UI-4): uno que saliera del grupo se veria.
    assert set(abierta["exportadores"]) == {
        "btn_json", "btn_html", "btn_pdf", "btn_csv", "btn_comparar",
        "btn_html_resumida", "btn_pdf_resumida"}
    for nombre, estado in abierta["exportadores"].items():
        assert not estado["encendido"] and estado["motivo"] == r.datos["motivo_sin_corrida"], nombre
    assert abierta["panel_del_cabezal"] == {
        "texto": "", "motivo": r.datos["motivo_sin_corrida_cabezal"]}


def test_c0_las_filas_de_exportacion_caben_en_la_geometria_por_defecto(r):
    """(a3) Los siete, mapeados, enteros y dentro de la pestaña 4, a 1100 x 800."""
    assert r.datos["geometria_por_defecto"] == "1100x800"
    for nombre, cabe in r.datos["recien_abierta"]["caben"].items():
        assert cabe == {"mapeado": True, "entero": True, "dentro": True}, nombre


@pytest.mark.parametrize("alcance, archivo", recorrido.CORRIDAS_DEL_EJEMPLO)
def test_c1_el_ejemplo_por_la_ventana_es_la_linea_base(r, alcance, archivo):
    """
    El CSV de ejemplo con las entradas de `regenerar.sh`, tecleado en la
    ventana: el MISMO JSON que la linea base fija (sin la marca de tiempo).
    """
    assert r.datos["ejemplo"][alcance]["informe"], r.datos["ejemplo"][alcance]
    ventana = _json(r.salida, f"ejemplo_{alcance}.json")
    base = json.loads((LINEA_BASE / archivo).read_text(encoding="utf-8"))
    assert ses.sin_marca_de_tiempo(ventana) == ses.sin_marca_de_tiempo(base)


def test_c1_el_cuadro_resumen_de_la_ventana_es_el_de_la_linea_base(r):
    assert r.datos["ejemplo"]["resumen_escrito"]
    ventana = (r.salida / "ejemplo_expediente.resumen.csv").read_bytes()
    assert ventana == (LINEA_BASE / recorrido.RESUMEN_DE_LA_LINEA_BASE).read_bytes()


@pytest.mark.parametrize("nombre", [c.nombre for c in ind.CORRIDAS_DE_REFERENCIA])
def test_c2_la_corrida_de_la_ventana_es_la_de_la_cli(r, json_de_la_cli, nombre):
    medido = r.datos[nombre]
    assert all(medido["examinar"].values()), medido["examinar"]
    assert medido["informe"], medido["error_visible"]
    referencia = recorrido.corrida(nombre)
    assert medido["alcance"] == referencia.alcance
    assert medido["con_hidrologia"] == (referencia.cuencas is not None)
    ventana = _json(r.salida, f"{nombre}.json")
    assert ses.sin_marca_de_tiempo(ventana) == ses.sin_marca_de_tiempo(json_de_la_cli[nombre])
    assert all(e["encendido"] for e in medido["exportadores"].values())


@pytest.mark.parametrize("nombre", ["expediente_cabezal", "hidrologia_calculada"])
def test_c2_las_declaraciones_entraron_por_la_pestana_2(r, nombre):
    """
    Cada valor tecleado en «Valor nuevo» y aplicado con el boton; la nota,
    solo donde la puerta la pidio (un dato de ensayo, una adopcion en un
    criterio de tabla), y lo dijo antes de pedirla.
    """
    declaraciones = r.datos[nombre]["declaraciones"]
    assert set(declaraciones) == set(recorrido.corrida(nombre).declaraciones)
    for clave, d in declaraciones.items():
        assert d["declarado"] and d["mismo_valor"], (clave, d["rotulo"])
        if d["con_nota"]:
            assert d["primer_rotulo"].startswith("Error:"), clave
            assert recorrido.NOTA in d["rotulo"], clave
    assert any(d["con_nota"] for d in declaraciones.values())
    assert not all(d["con_nota"] for d in declaraciones.values())


def _detalles():
    return [(nombre, punto) for nombre, puntos in recorrido.DETALLES.items()
            for punto in puntos]


@pytest.mark.parametrize("nombre, punto", _detalles())
def test_c3_el_detalle_de_la_pestana_3_es_el_de_la_cli(r, nombre, punto):
    d = r.datos[nombre]["detalles"][punto]
    assert _palabras(d["texto"].splitlines()) == _palabras(d["lineas_de_la_cli"])


def test_c3_el_detalle_dice_el_caudal_calculado_la_proteccion_la_fase_8_y_el_cabezal(r):
    detalles = r.datos["hidrologia_calculada"]["detalles"]
    calculado = detalles["A-01"]
    assert calculado["calculado"]
    assert any(l.startswith("Fase 1b Q calculado") for l in _palabras(
        calculado["texto"].splitlines()))
    dimensionado = detalles["C-01"]
    assert dimensionado["dimensionado"]
    lineas = _palabras(dimensionado["texto"].splitlines())
    for marca in ("Fase 6 ", "Fase 8 ", "Fase 9 cabezal de entrada",
                  "Fase 9 cabezal de salida", "Fase 9 armado del cabezal"):
        assert any(l.startswith(marca) for l in lineas), marca
    # Y en la corrida con cabezal de T-7b/T-7c, la Fase 8 de un tubo.
    cabezal = _palabras(r.datos["expediente_cabezal"]["detalles"]["A-01"]["texto"].splitlines())
    assert any(l.startswith("Fase 8 Clase") for l in cabezal)
    assert any(l.startswith("Fase 9 estabilidad del cabezal") for l in cabezal)


@pytest.mark.parametrize("nombre", [c.nombre for c in ind.CORRIDAS_DE_REFERENCIA])
def test_c4_el_panel_del_cabezal_del_proyecto_es_el_de_la_cli(r, nombre):
    medido = r.datos[nombre]
    panel = medido["panel_del_cabezal"]
    assert panel["motivo"] == ""
    assert _palabras(panel["texto"].splitlines()) == _palabras(
        medido["lineas_del_cabezal_de_la_cli"])
    lineas = _palabras(panel["texto"].splitlines())
    if recorrido.corrida(nombre).alcance == cli.ALCANCE_PERFIL:
        assert any("DiferidoPorAlcance" in l for l in lineas)
    else:
        assert any(l.startswith("Cadena sismica") for l in lineas)
        assert any(l.startswith("Cabezales por punto") for l in lineas)


def test_c5_los_exportadores_que_escribe_la_ventana(r):
    exportados = r.datos["exportados"]
    assert {n for n, e in exportados.items() if e["escrito"]} == {
        "json", "html", "csv", "html_resumida", "pdf", "pdf_resumida"}
    volcado = _json(r.salida, "hidrologia_calculada.json")
    assert _json(r.salida, "exportado.json") == volcado      # el de la corrida, entero
    contexto = volcado["expediente"]["hidrologia"]
    for html in ("completa.html", "resumida.html"):
        texto = (r.salida / html).read_text(encoding="utf-8")
        for huella in (volcado["expediente"]["csv_sha1"], contexto["cuencas_sha1"],
                       contexto["estacion_sha1"]):
            assert huella in texto, (html, huella)
    assert M11.TITULO_RESUMEN_VERIFICACIONES in (r.salida / "resumida.html").read_text(
        encoding="utf-8")
    cabecera = (r.salida / "resumen.csv").read_text(encoding="utf-8").splitlines()[0]
    assert cabecera.split(",") == list(M11.COLUMNAS_RESUMEN_CSV)


@pytest.mark.parametrize("vista, bandera", [("pdf", "--pdf"), ("pdf_resumida", "--pdf-resumida")])
def test_c5_los_dos_pdf_salen_por_el_hijo_con_la_hidrologia(r, vista, bandera):
    medido = r.datos["exportados"][vista]
    if not r.datos["weasyprint_disponible"]:
        assert medido["html_del_navegador"]
        pytest.skip("weasyprint no esta operativo en el interprete de la ventana: "
                    "se midio la via del navegador y NO el proceso hijo")
    assert bandera in medido["comando"] and "--sesion" in medido["comando"]
    assert medido["termino_a_tiempo"] and medido["estado"] == "terminado", medido["rotulo"]
    assert medido["cabecera"] == "%PDF" and medido["con_trailer"]
    # El hijo corrio LA MISMA obra que la ventana: su sesion lleva las dos
    # rutas de la hidrologia y su JSON es el de la ventana, salvo la hora.
    referencia = recorrido.corrida("hidrologia_calculada")
    sesion = _json(r.salida, f"hijo_{vista}.sesion.json")
    assert sesion["cuencas"] == recorrido.relativa(referencia.cuencas)
    assert sesion["estacion"] == recorrido.relativa(referencia.estacion)
    hijo = _json(r.salida, f"hijo_{vista}.json")
    assert ses.sin_marca_de_tiempo(hijo) == ses.sin_marca_de_tiempo(
        _json(r.salida, "hidrologia_calculada.json"))


def test_c6_guardar_nuevo_cargar_y_ejecutar_da_el_mismo_json(r):
    """
    El ciclo se hace a PERFIL y con la luz tecleada en la pestaña 1, que no es
    lo que «Nuevo proyecto» deja (revision de UI-4, H2): asi «Cargar sesion»
    tiene que REPONER el alcance y las banderas, y no basta con que se queden
    por defecto. Medido con el mutante: sin `self.alcance_var.set(alcance)`
    en `cargar_sesion`, este test cae.
    """
    ciclo = r.datos["ciclo_de_sesion"]
    assert ciclo["antes"]["informe"], ciclo["antes"]["error_visible"]
    guardados = ciclo["campos_guardados"]
    assert guardados["alcance_var"] == recorrido.ALCANCE_DEL_CICLO != cli.ALCANCE_EXPEDIENTE
    for campo, texto in recorrido.BANDERAS_DEL_CICLO.items():
        assert guardados["externos"][campo] == texto != ""
    assert ciclo["formato_version"] == ses.FORMATO_SESION and ciclo["errores"] == []
    referencia = recorrido.corrida("hidrologia_calculada")
    assert ciclo["cuencas"] == recorrido.relativa(referencia.cuencas)
    nuevo = ciclo["tras_nuevo"]
    assert nuevo["campos"]["alcance_var"] == cli.ALCANCE_EXPEDIENTE
    assert all(v == "" for c, v in nuevo["campos"].items() if c not in ("alcance_var", "externos"))
    assert all(v == "" for v in nuevo["campos"]["externos"].values())
    assert nuevo["declarados"] == [] and nuevo["sitio_declarado"] == []
    assert nuevo["informe_es_None"]
    assert not any(e["encendido"] for e in nuevo["exportadores"].values())
    cargada = ciclo["tras_cargar"]
    assert cargada["campos"] == guardados
    assert cargada["estado_de_sesion_igual"] and cargada["sitio_igual"]
    assert cargada["informe_es_None"]
    assert ciclo["corrida"]["informe"], ciclo["corrida"]["error_visible"]
    despues = _json(r.salida, "ciclo_despues.json")
    assert despues["alcance"]["nivel"] == recorrido.ALCANCE_DEL_CICLO
    assert ses.sin_marca_de_tiempo(despues) == ses.sin_marca_de_tiempo(
        _json(r.salida, "ciclo_antes.json"))


def test_c7_la_sesion_v3_se_abre_reproduce_y_se_reescribe(r):
    v3 = r.datos["sesion_v3"]
    assert v3["cuencas"] == "" and v3["estacion"] == ""
    assert v3["csv_igual"] and v3["id_igual"]
    assert v3["declarados"] == ["phi_relleno_trasdos"]
    assert all(tipo != "error" for tipo, _t, _x in v3["dialogos"])
    assert v3["informe"], v3["error_visible"]
    # CAMBIADO EN UI-5, declarando la causa: el fixture v3 es una sesion de la
    # version anterior, NO se regenera (su LEEME), y su corrida embebida lleva
    # la huella del archivo de criterios con que se guardo. UI-5 cambio la
    # guardia de `criterios_adoptados.py` (ficha UI3-03) y con ella su huella,
    # que el comparador compara: con otro archivo de criterios la respuesta
    # correcta es DIFIERE, y SOLO por esa huella --- ningun punto, ningun
    # numero, nada sin comparar ---. Es la misma regla que UI-1 escribio para
    # la CLI (`test_d_la_cli_abre_la_sesion_v3_y_corre_sin_hidrologia`).
    import hashlib
    fixture = json.loads((RAIZ / recorrido.SESION_V3).read_text(encoding="utf-8"))
    huella = hashlib.sha1(M11.ARCHIVO_CRITERIOS.read_bytes()).hexdigest()
    if fixture["corridas"][-1]["criterios_sha1"] == huella:
        assert v3["reproduce"], v3["comparacion"]
    else:
        assert v3["diferencias"] == [["expediente", "criterios_sha1"]], v3["comparacion"]
        assert v3["no_comparables"] == 0 and v3["puntos_solo_en_uno"] == 0
    reescrita = v3["reescrita"]
    assert reescrita["formato_version"] == ses.FORMATO_SESION
    assert reescrita["id_igual"] and reescrita["errores"] == []
    assert reescrita["corridas"] == 2          # la embebida y la de esta corrida


def test_c8_el_barrido_de_la_ventana_es_el_de_la_cli(r, tmp_path):
    barrido = r.datos["barrido"]
    assert barrido["boton_encendido"] and barrido["abierta"]
    assert barrido["termino_a_tiempo"] and barrido["estado"] == "terminado", barrido["detalle"]
    referencia = recorrido.corrida("perfil_guia")
    texto = ",".join(str(v) for v in recorrido.VALORES_DEL_BARRIDO)
    args = [a for a in recorrido.argumentos_de_la_cli(referencia)]
    hecho = subprocess.run(
        [sys.executable, str(RAIZ / "cli.py"), *args, "--barrido",
         f"{recorrido.CLAVE_DEL_BARRIDO}={texto}", "--json", str(tmp_path / "b.json")],
        cwd=RAIZ, capture_output=True, text=True, timeout=TOPE_S)
    assert hecho.returncode == 0, hecho.stderr[-3000:]
    lineas = hecho.stdout.splitlines()
    inicio = next(i for i, l in enumerate(lineas) if l.startswith("Barrido de '"))
    fin = next(i for i in range(inicio, len(lineas)) if not lineas[i].strip())

    def normalizadas(tabla):
        return [SEGUNDO_DE_LA_DECLARACION.sub("declarado el <segundo>", l) for l in tabla]

    assert normalizadas(barrido["lineas"]) == normalizadas(lineas[inicio:fin])
    assert barrido["json_guardado"]


def test_c8_el_barrido_no_cambia_la_ventana(r):
    assert r.datos["barrido"]["despues"] == {
        "ventana_barrido_es_None": True, "estado_de_sesion_igual": True,
        "sitio_igual": True, "informe_es_el_mismo": True, "volcado_igual": True,
        "exportadores_iguales": True, "filas_de_la_pestana_2_iguales": True}


def test_c8_la_tabla_del_barrido_se_ve_sin_mover_el_divisor(r):
    """(a1) en la ventana de verdad: el titulo, la cabecera y la primera fila, a la vista."""
    assert r.datos["barrido"]["lineas_a_la_vista"] >= LINEAS_DEL_BARRIDO_A_LA_VISTA


def test_c9_cerrar_la_ventana_con_un_pdf_en_marcha_no_deja_hijo_ni_carpeta(r):
    """(a2) en la ventana de verdad."""
    cierre = r.datos["cierre_con_pdf_en_marcha"]
    if not r.datos["weasyprint_disponible"]:
        pytest.skip("weasyprint no esta operativo: no hay hijo del PDF que cerrar")
    assert cierre == {"en_marcha_al_cerrar": True, "hijo_terminado": True,
                      "carpeta_retirada": True, "destino_intacto": True}


def test_c10_las_capturas_se_regeneran_con_el_recorrido(r):
    if shutil.which("import") is None:
        pytest.skip("sin ImageMagick (`import`) el recorrido no hace capturas")
    assert sorted(r.datos["capturas"]) == sorted(recorrido.CAPTURAS)
    for nombre in recorrido.CAPTURAS:
        assert _dimensiones_png(r.salida / "capturas" / nombre)


def test_c_ningun_dialogo_de_error_en_el_recorrido(r):
    assert r.datos["dialogos_de_error"] == []
    assert "error" not in r.datos
