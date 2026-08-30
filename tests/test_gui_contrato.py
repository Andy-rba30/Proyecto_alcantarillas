"""
tests/test_gui_contrato.py
==========================
Contrato de `gui/app.py`, que hasta la sesion S16 no tenia NI UN test.

Por que estos tests leen el arbol en vez de importar el modulo
--------------------------------------------------------------
`gui/app.py` importa `tkinter` en su cabecera, y `tkinter` no esta disponible
en todo entorno donde corre la suite (no viene con la biblioteca estandar
compilada de muchas imagenes de servidor, y `ttkbootstrap` depende de el). Un
test que importara el modulo se SALTARIA justo donde mas falta hace: en la
integracion continua sin escritorio.

Lo que estos tests comprueban NO necesita ejecutar la GUI. Son propiedades del
CODIGO -- que orden tienen los brazos de un `except`, que la traduccion de
banderas no este escrita dos veces --, y esas se leen del AST con la misma
tecnica que ya usa `tests/test_sin_literales.py`. Es la unica forma de que
esta guardia corra SIEMPRE.

Los hallazgos que cierra
------------------------
    SIS-F-01  (PARCIAL, y conviene decir hasta donde). Los tests de este
              bloque NO ejecutan ninguna de las ~590 sentencias de gui/app.py:
              leen el arbol. Lo que cierran es que los brazos de except no
              vuelvan a la forma de SIS-E-01 / SIS-E-03. La parte EJECUTABLE
              -- las tres reimplementaciones que la ficha nombra -- se cubre
              en el bloque de mas abajo, que SI importa el modulo con un doble
              de tkinter y llama a la logica pura. El codigo que construye
              widgets sigue sin ejecutarse, y probarlo con un doble seria un
              espejismo: lo que se veria correr no es lo que corre en pantalla.
    SIS-E-01  el manejador de EJECUTAR capturaba (OSError, ValueError) ANTES
              del brazo con traza: un ValueError nacido en el pipeline -- la
              forma mas comun de un fallo de programa -- se mostraba como
              "No se pudo leer la entrada", que manda al proyectista a revisar
              su CSV. La CLI usaba el brazo estrecho correcto.
    SIS-E-03  los tres exportadores capturaban `Exception` sin traza, mientras
              el patron hermano de `ejecutar_pipeline` si la imprime.
"""

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
GUI = RAIZ / "gui" / "app.py"
CLI = RAIZ / "cli.py"

ARBOL_GUI = ast.parse(GUI.read_text(encoding="utf-8-sig"), filename="app.py")
ARBOL_CLI = ast.parse(CLI.read_text(encoding="utf-8-sig"), filename="cli.py")


# ---------------------------------------------------------------------------
# Lectura del arbol
# ---------------------------------------------------------------------------

def _funcion(arbol, nombre):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and nodo.name == nombre:
            return nodo
    raise AssertionError(f"'{nombre}' ya no existe: el test quedo obsoleto")


def _nombre_de_tipo(nodo):
    if isinstance(nodo, ast.Name):
        return nodo.id
    if isinstance(nodo, ast.Attribute):
        return nodo.attr
    return None


def _brazos(funcion):
    """[(tuple de tipos capturados, nodo del handler), ...] en orden."""
    brazos = []
    for nodo in ast.walk(funcion):
        if not isinstance(nodo, ast.Try):
            continue
        for manejador in nodo.handlers:
            tipo = manejador.type
            if tipo is None:
                capturados = ("<desnudo>",)
            elif isinstance(tipo, ast.Tuple):
                capturados = tuple(_nombre_de_tipo(e) for e in tipo.elts)
            else:
                capturados = (_nombre_de_tipo(tipo),)
            brazos.append((capturados, manejador))
    return brazos


def _llama_a(nodo, nombre):
    """
    La llamada tiene que ser una SENTENCIA DEL CUERPO del brazo, no un
    descendiente cualquiera: una `traceback.print_exc()` metida bajo un
    `if False:` no imprime ninguna traza y dejaba el test en verde.
    """
    for sentencia in getattr(nodo, "body", []):
        if (isinstance(sentencia, ast.Expr)
                and isinstance(sentencia.value, ast.Call)
                and _nombre_de_tipo(sentencia.value.func) == nombre):
            return True
    return False


# ---------------------------------------------------------------------------
# SIS-E-01 - el orden de los brazos de EJECUTAR
# ---------------------------------------------------------------------------

def test_el_brazo_de_entrada_de_la_gui_no_captura_ValueError():
    """
    Un ValueError nacido dentro del pipeline es un fallo de PROGRAMA. Si el
    primer brazo lo captura, el proyectista lee "No se pudo leer la entrada"
    -- y el brazo que imprime la traza no llega a ejecutarse nunca.
    """
    brazos = _brazos(_funcion(ARBOL_GUI, "ejecutar_pipeline"))
    culpables = [capturados for capturados, _ in brazos
                 if "ValueError" in capturados]
    assert not culpables, (
        f"ejecutar_pipeline vuelve a capturar ValueError en {culpables}: un "
        "fallo de programa se presentaria como problema del expediente. Da "
        "igual si el brazo es el primero o esta en un try ANIDADO -- mirar "
        "solo brazos[0] protegia una posicion del recorrido, no la propiedad")


def test_los_brazos_de_la_gui_y_de_la_cli_leen_la_entrada_igual():
    """
    Las dos puertas del mismo pipeline tienen que fallar igual: la asimetria
    entre ellas es lo que delato SIS-E-01, igual que la de `isfinite` delato
    MAT-D14.
    """
    de_la_gui = _brazos(_funcion(ARBOL_GUI, "ejecutar_pipeline"))[0][0]
    de_la_cli = [caps for caps, _ in _brazos(_funcion(ARBOL_CLI, "main"))
                 if "OSError" in caps]
    assert de_la_cli, "la CLI dejo de tener su brazo de lectura de entrada"
    assert set(de_la_gui) == set(de_la_cli[0]), (
        f"la GUI captura {de_la_gui} y la CLI {de_la_cli[0]}: la misma "
        "entrada tiene que fallar igual por las dos puertas")


# El brazo de lectura de entrada, en TODAS las funciones que abren un archivo
# que el proyectista elige. Comparar solo `brazos[0]` de `ejecutar_pipeline`
# --- como hacia la primera version de este archivo --- dejaba fuera la otra
# puerta que abre un archivo del usuario, `cargar_sesion`, que capturaba
# `(OSError, JSONDecodeError)` SIN `UnicodeDecodeError`: el mismo JSON en ANSI
# que `ejecutar_pipeline` explica por escrito estrellaba la ventana dos
# funciones mas abajo.
PUERTAS_QUE_LEEN_UN_ARCHIVO = ("ejecutar_pipeline", "cargar_sesion")


@pytest.mark.parametrize("nombre", PUERTAS_QUE_LEEN_UN_ARCHIVO)
def test_toda_puerta_que_lee_un_archivo_atrapa_el_error_de_codificacion(nombre):
    """
    `UnicodeDecodeError` es subclase de `ValueError`, no de `OSError` ni de
    `JSONDecodeError`: un brazo escrito como `(OSError, JSONDecodeError)` no
    lo ve, y un archivo guardado en ANSI sale como traza en vez de como
    "el archivo no esta en UTF-8".
    """
    brazos = _brazos(_funcion(ARBOL_GUI, nombre))
    lectura = [caps for caps, _ in brazos if "OSError" in caps]
    assert lectura, f"'{nombre}' dejo de tener brazo de lectura de entrada"
    assert "UnicodeDecodeError" in lectura[0], (
        f"'{nombre}' captura {lectura[0]} y le falta UnicodeDecodeError")


def test_la_divergencia_de_la_gui_con_la_cli_es_solo_el_brazo_de_programa():
    """
    La GUI tiene un brazo que la CLI no tiene, y es DELIBERADO: una ventana no
    se puede caer con una traza en la consola que nadie mira, de modo que
    `ejecutar_pipeline` termina en `except Exception` + `traceback.print_exc()`.
    La CLI no lo necesita porque ahi la traza SI es la salida.

    El test fija esa divergencia para que no crezca: cualquier OTRA diferencia
    entre las dos puertas es la asimetria que SIS-E-01 denuncia. La primera
    version comparaba solo el primer brazo y por eso no habria visto una
    segunda divergencia aparecer.
    """
    gui = [set(caps) for caps, _ in _brazos(_funcion(ARBOL_GUI, "ejecutar_pipeline"))]
    cli_ = [set(caps) for caps, _ in _brazos(_funcion(ARBOL_CLI, "main"))]
    solo_en_la_gui = [b for b in gui if b not in cli_]
    assert solo_en_la_gui == [{"Exception"}], (
        f"la GUI tiene brazos que la CLI no: {solo_en_la_gui}. El unico "
        "admitido es {'Exception'}, el que imprime la traza en vez de dejar "
        "caer la ventana; cualquier otro es la asimetria de SIS-E-01.")


def test_el_brazo_de_expediente_va_antes_del_de_programa():
    """
    `ErrorProyecto` tiene que capturarse ANTES que `Exception`: al reves, un
    problema del expediente saldria con traza como si fuera un defecto del
    programa, que es la distincion entera que CLAUDE.md pide a la taxonomia.
    """
    brazos = [caps for caps, _ in _brazos(_funcion(ARBOL_GUI, "ejecutar_pipeline"))]
    posicion = {}
    for indice, capturados in enumerate(brazos):
        for tipo in capturados:
            posicion.setdefault(tipo, indice)
    assert "ErrorProyecto" in posicion, "el brazo del expediente desaparecio"
    assert "Exception" in posicion, "el brazo con traza desaparecio"
    assert posicion["ErrorProyecto"] < posicion["Exception"]


def test_el_brazo_ancho_de_ejecutar_imprime_la_traza():
    for capturados, manejador in _brazos(_funcion(ARBOL_GUI, "ejecutar_pipeline")):
        if "Exception" in capturados:
            assert _llama_a(manejador, "print_exc"), (
                "el brazo de Exception dejo de imprimir la traza")
            return
    raise AssertionError("no hay brazo de Exception en ejecutar_pipeline")


# ---------------------------------------------------------------------------
# SIS-E-03 - los tres exportadores
# ---------------------------------------------------------------------------

# Son CUATRO botones de exportacion, no tres. `exportar_json` comparte
# pestana con los otros y su cuerpo llama a `cli.informe_json` y a
# `json.dumps(..., allow_nan=False)`: dejarlo fuera de la tupla congelaba la
# omision, y con un ErrorProyecto o un NaN el usuario no veia NADA.
EXPORTADORES = ("exportar_html", "exportar_pdf", "exportar_csv",
                "exportar_json")


@pytest.mark.parametrize("nombre", EXPORTADORES)
def test_cada_exportador_imprime_la_traza_del_fallo_inesperado(nombre):
    """
    SIS-E-03: los tres capturaban `Exception` a secas y mostraban el tipo y el
    mensaje, sin traza. Un fallo dentro de weasyprint o de la plantilla salia
    como una linea sin ninguna pista de donde ocurrio, mientras el patron
    hermano de `ejecutar_pipeline`, tres pantallas mas arriba, si la imprime.
    """
    anchos = [(caps, man) for caps, man in _brazos(_funcion(ARBOL_GUI, nombre))
              if "Exception" in caps or "<desnudo>" in caps]
    assert anchos, f"'{nombre}' ya no tiene brazo ancho: revisa este test"
    for _, manejador in anchos:
        assert _llama_a(manejador, "print_exc"), (
            f"'{nombre}' captura Exception sin imprimir la traza")


@pytest.mark.parametrize("nombre", EXPORTADORES)
def test_cada_exportador_separa_el_fallo_del_expediente(nombre):
    """
    Un `ErrorProyecto` al exportar -- un criterio que faltaba y que la memoria
    necesita -- lo corrige el proyectista y no lleva traza. El brazo estrecho
    tiene que existir y venir primero.
    """
    brazos = [caps for caps, _ in _brazos(_funcion(ARBOL_GUI, nombre))]
    estrechos = [i for i, caps in enumerate(brazos) if "ErrorProyecto" in caps]
    anchos = [i for i, caps in enumerate(brazos) if "Exception" in caps]
    assert estrechos, f"'{nombre}' no distingue el fallo del expediente"
    assert anchos, f"'{nombre}' no tiene brazo con traza"
    assert min(estrechos) < min(anchos)


# ---------------------------------------------------------------------------
# La GUI no puede volver a quedarse sin ninguna guardia
# ---------------------------------------------------------------------------

def test_ningun_manejador_de_la_gui_captura_sin_nombrar_la_excepcion():
    """
    Un `except:` desnudo -- y un `except BaseException`, que hace lo mismo con
    otro nombre -- se tragan hasta un KeyboardInterrupt: el usuario pulsa
    Ctrl-C y la ventana se lo come.
    """
    culpables = [(nodo.lineno, _nombre_de_tipo(nodo.type) or "<desnudo>")
                 for nodo in ast.walk(ARBOL_GUI)
                 if isinstance(nodo, ast.ExceptHandler)
                 and (nodo.type is None
                      or _nombre_de_tipo(nodo.type) == "BaseException")]
    assert not culpables, f"manejador que se traga todo en gui/app.py: {culpables}"


# ---------------------------------------------------------------------------
# La parte EJECUTABLE de SIS-F-01: la logica pura, con un doble de tkinter
# ---------------------------------------------------------------------------
# Los tests de arriba leen el arbol. Estos IMPORTAN el modulo y llaman a sus
# funciones, con un doble de `tkinter` en `sys.modules`. La distincion importa
# y se declara: probar con un doble la logica PURA -- interpretar un texto,
# traducir un nombre de bandera -- es honesto, porque esa logica no toca la
# pantalla; probar con un doble el codigo que CONSTRUYE widgets seria un
# espejismo, porque lo que se veria correr no es lo que corre. Por eso aqui
# solo entran las tres reimplementaciones que la ficha SIS-F-01 nombra.


def _con_doble_de_tkinter():
    """Importa gui.app con tkinter sustituido, y devuelve el modulo."""
    import sys
    import types

    if "gui.app" in sys.modules:
        return sys.modules["gui.app"]

    class _Cualquiera:
        def __init__(self, *a, **k):
            pass

        def __getattr__(self, nombre):
            return _Cualquiera()

        def __call__(self, *a, **k):
            return _Cualquiera()

    def _doble(nombre):
        modulo = types.ModuleType(nombre)
        modulo.__getattr__ = lambda n: _Cualquiera
        return modulo

    for nombre in ("tkinter", "tkinter.filedialog", "tkinter.messagebox",
                   "tkinter.ttk", "ttkbootstrap", "ttkbootstrap.constants"):
        sys.modules.setdefault(nombre, _doble(nombre))
    sys.modules["tkinter"].filedialog = sys.modules["tkinter.filedialog"]
    sys.modules["tkinter"].messagebox = sys.modules["tkinter.messagebox"]
    sys.modules["tkinter"].ttk = sys.modules["tkinter.ttk"]

    import gui.app as app
    return app


@pytest.fixture(scope="module")
def app():
    return _con_doble_de_tkinter()


@pytest.fixture
def ventana(app):
    """Una instancia SIN construir widgets: solo para llamar a su logica."""
    return object.__new__(app.ExpedienteApp)


def test_el_campo_de_declaracion_admite_la_coma_decimal(ventana):
    """Quien teclea en la ventana escribe 1,5 y espera un numero."""
    from tests.apoyo.aproximacion import REL_TRANSPORTE

    assert ventana._interpretar_valor_declarado("1,5") == pytest.approx(
        1.5, rel=REL_TRANSPORTE)
    assert ventana._interpretar_valor_declarado(" 2.5 ") == pytest.approx(
        2.5, rel=REL_TRANSPORTE)


def test_el_campo_de_declaracion_devuelve_el_texto_si_no_es_un_numero(ventana):
    """Los criterios CATEGORICOS entran por aqui: 'flexible', 'A'..."""
    assert ventana._interpretar_valor_declarado("flexible") == "flexible"
    assert ventana._interpretar_valor_declarado(" cota_terreno ") == "cota_terreno"


def test_el_campo_vacio_no_declara_nada(ventana):
    """
    SIS-E-04: el ValueError es deliberado y no sale de la clase. El test fija
    que sigue siendo ValueError -- si alguien lo cambia a un ErrorProyecto sin
    tocar los dos llamadores, el mensaje dejaria de mostrarse en el panel.
    """
    with pytest.raises(ValueError, match="no puede quedar vacio"):
        ventana._interpretar_valor_declarado("   ")


def test_la_gui_y_la_cli_divergen_al_interpretar_la_coma_y_esta_declarado(ventana):
    """
    LA DIVERGENCIA, FIJADA A PROPOSITO. `cli.declarar_criterios` resuelve el
    texto con `ast.literal_eval` y leeria '1,5' como la TUPLA (1, 5); la
    ventana lo lee como 1.5. Unificar por el lado de la CLI convertiria en
    silencio el numero que el usuario quiso escribir en una tupla valida, que
    es peor que la duplicacion. El test existe para que la divergencia se vea
    y se decida, en vez de descubrirse.
    """
    import ast as _ast

    assert _ast.literal_eval("1,5") == (1, 5)
    assert ventana._interpretar_valor_declarado("1,5") != (1, 5)
    assert "DIVERGE" in ventana._interpretar_valor_declarado.__doc__, (
        "la divergencia tiene que estar escrita donde vive el codigo")


def test_la_gui_traduce_las_mismas_banderas_que_la_cli(app, ventana):
    """
    SIS-F-01: "la GUI reimplementa la traduccion de banderas". Sigue
    reimplementandola, y este test impide que las dos listas se separen: las
    claves que `_leer_banderas` produce tienen que ser EXACTAMENTE las que
    `cli.main` arma para `cargar_datos_externos`.
    """
    class _Var:
        def __init__(self, texto=""):
            self._texto = texto

        def get(self):
            return self._texto

    ventana.externos_vars = {clave: _Var() for clave, *_ in app.CAMPOS_EXTERNOS}
    banderas = ventana._leer_banderas()

    de_la_cli = _banderas_de_la_cli()
    assert set(banderas) == de_la_cli, (
        f"la ventana produce {sorted(banderas)} y la CLI espera "
        f"{sorted(de_la_cli)}: las dos traducciones se separaron")
    assert all(valor is None for valor in banderas.values()), (
        "un campo vacio tiene que traducirse a None, no a cadena vacia")


def test_la_gui_pasa_la_coma_decimal_a_punto_salvo_en_la_categoria(app, ventana):
    """
    La otra mitad de la traduccion: los campos numericos admiten coma y la
    categoria de TR es una FILA de la Tabla N 02, no un numero.
    """
    class _Var:
        def __init__(self, texto=""):
            self._texto = texto

        def get(self):
            return self._texto

    ventana.externos_vars = {clave: _Var("1,5") for clave, *_ in app.CAMPOS_EXTERNOS}
    ventana.externos_vars["categoria_tr"] = _Var("quebrada_menor")
    banderas = ventana._leer_banderas()

    assert banderas["luz_m"] == "1.5"
    assert banderas["L_hidraulico_m"] == "1.5", (
        "la clave l_hidraulico se traduce a L_hidraulico_m: es el mapeo a mano "
        "que SIS-F-01 denuncia y el que se separaria en silencio")
    assert banderas["categoria_tr"] == "quebrada_menor"


def _banderas_de_la_cli():
    """Las claves del dict que `cli.main` arma, leidas del arbol."""
    principal = _funcion(ARBOL_CLI, "main")
    for nodo in ast.walk(principal):
        if (isinstance(nodo, ast.Assign) and len(nodo.targets) == 1
                and isinstance(nodo.targets[0], ast.Name)
                and nodo.targets[0].id == "banderas"
                and isinstance(nodo.value, ast.Dict)):
            return {clave.value for clave in nodo.value.keys
                    if isinstance(clave, ast.Constant)}
    raise AssertionError("cli.main dejo de armar el dict `banderas`")
