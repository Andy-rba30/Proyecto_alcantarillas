"""
tests/test_ui1_hidrologia_ventana.py
====================================
La aceptacion de UI-1 (cadena de interfaz): LA HIDROLOGIA EN LA VENTANA Y EN
LA SESION, que es la parte de interfaz de la ficha T1-04.

Hasta UI-1 `--cuencas` y `--estacion` solo entraban por la linea de comandos:
la ventana calculaba siempre con el caudal declarado, la sesion no guardaba
las dos rutas, y el PDF que la ventana escribe en un proceso hijo
(`cli.py --sesion`) habria recalculado SIN la hidrologia que la corrida de
la ventana uso. Que se vigila, en el orden del prompt:

(a) La ayuda de los dos CSV sale de `src/ayuda_entrada.py`, derivada de
    `MH_hidrologia` (la cabecera y las claves que cada columna admite), y no
    de gui/: la lista de claves admitidas se comprueba contra el CARGADOR,
    escribiendo un CSV con cada clave y con una que no existe.
(b) La pestaña 1: dos campos de archivo con «Examinar…» y su «i»; al
    ejecutar, `servicio.cargar_hidrologia` y `hidrologia=` a `correr`; con un
    solo campo, el mensaje DEL SERVICIO; un error de carga sale como el del
    JSON de datos externos; cambiar un campo invalida el informe; «Nuevo
    proyecto» los vacia.
(c) El anticipo recibe el MISMO conjunto de obras con caudal calculable que
    la CLI en `_prevuelo` y que M0 en `correr`
    (`servicio.ids_con_caudal_calculable`).
(d) La sesion de formato 4: dos claves con las rutas, con la convencion de
    rutas del CSV; una sesion de formato 3 DE VERDAD (guardada con el codigo
    de partida, `tests/fixtures/sesion_v3/`) se abre igual y se reescribe en
    4 al guardar.
(e) El hijo del PDF y la CLI: `sesion_de_la_corrida` lleva las dos rutas
    CON QUE CORRIO el informe y `cli.py --sesion` las usa si la linea de
    comandos no trae las banderas (que ganan); el JSON por las dos puertas
    es el mismo.
(f) Las huellas: `ContextoCorrida.cuencas_sha1` y `estacion_sha1` de los
    MISMOS bytes que se leyeron, impresas en el encabezado de trazabilidad y
    en el JSON solo cuando hay hidrologia.
(g) La ventana de verdad bajo xvfb (`tests/apoyo/gui_ui1_hidrologia_real.py`).
(h) Lo que la revision independiente de UI-1 encontro: el comparador mira el
    bloque de la hidrologia (sus huellas) y no sus rutas; una sola
    convencion de rutas para las dos puertas (`sesion.ruta_de_campo`); el
    anticipo dice lo MISMO que `--prevuelo` (mensaje y aviso de un solo
    sitio); la ayuda sale entera de src/; el orden de carga de la partida
    (cuencas, despues estacion).

Escrita PRIMERO, en rojo (`xfail(strict=True)` a nivel de modulo, medida
antes de tocar codigo: 34 xfailed y 2 XPASS) y liberada al implementar, como
manda el §1 de la cadena. Los dos XPASS son guardias que valen antes y
despues --- el fixture v3 es una sesion real de la version anterior, y la CLI
ya la abria ---, el mismo caso que EXT-10 dejo escrito. Los datos son DATOS
DE PRUEBA: las cuencas y la serie SINTETICAS de T-1 y el CSV de ejemplo.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

import cli
from src import declaracion as dec
from src import servicio
from src import sesion as ses
from src.modelos import DatoFaltanteError, DatoInvalidoError, ErrorProyecto
from src.modulos import M11_reporte as M11
from src.modulos import MH_hidrologia as MH
from tests.apoyo import doble_tkinter
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.doble_tkinter import VariableDeTexto


RAIZ = Path(__file__).resolve().parents[1]
GUI = RAIZ / "gui" / "app.py"
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"
HIDRO = RAIZ / "tests" / "fixtures" / "hidrologia"
CUENCAS = HIDRO / "cuencas_prueba.csv"
ESTACION = HIDRO / "estacion_prueba.csv"
SESION_V3 = RAIZ / "tests" / "fixtures" / "sesion_v3" / "sesion_v3_partida.json"
OBRAS_CON_CUENCA = ("A-01", "A-02", "B-01")
CLAVE_FEN = "homogeneidad_serie_fen"
ARBOL_GUI = ast.parse(GUI.read_text(encoding="utf-8-sig"), filename="app.py")
ARBOL_CLI = ast.parse((RAIZ / "cli.py").read_text(encoding="utf-8-sig"), filename="cli.py")
ARBOL_SERVICIO = ast.parse((RAIZ / "src" / "servicio.py").read_text(encoding="utf-8-sig"),
                           filename="servicio.py")


# ---------------------------------------------------------------------------
# Apoyos
# ---------------------------------------------------------------------------

def _funcion(arbol, nombre):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and nodo.name == nombre:
            return nodo
    raise AssertionError(f"no se encontro la funcion {nombre}")


def _llamadas(nodo):
    return [n for n in ast.walk(nodo) if isinstance(n, ast.Call)]


def _nombres_llamados(nodo):
    return {ast.unparse(n.func) for n in _llamadas(nodo)}


def _sha1(ruta: Path) -> str:
    return hashlib.sha1(Path(ruta).read_bytes()).hexdigest()


def _csv_sin_caudal(tmp_path: Path, nombre: str = "puntos_sin_q.csv") -> Path:
    """El CSV de ejemplo con el `Q_m3s` de las obras con cuenca vaciado."""
    with CSV_EJEMPLO.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    for fila in filas:
        if fila["id"] in OBRAS_CON_CUENCA:
            fila["Q_m3s"] = ""
    destino = tmp_path / nombre
    with destino.open("w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    return destino


def _externos():
    return cli.cargar_datos_externos(EXTERNOS, {"luz_m": "2.75", "TW_m": None,
                                                "longitud_m": None,
                                                "L_hidraulico_m": None,
                                                "categoria_tr": None})


def _cli(*args: str, timeout: float = 900.0) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(RAIZ / "cli.py"), *args],
                          cwd=RAIZ, capture_output=True, text=True, timeout=timeout)


def _escribir(ruta: Path, datos) -> Path:
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    return ruta


def _sin_marca(datos):
    return ses.sin_marca_de_tiempo(json.loads(json.dumps(datos, ensure_ascii=False,
                                                         allow_nan=False)))


@pytest.fixture
def con_fen():
    """El criterio FEN declarado: sin el, el caudal calculado se detiene."""
    dec.declarar_valor(CLAVE_FEN, "serie_completa",
                       nota="DATOS DE PRUEBA: declarado para UI-1")
    yield


@pytest.fixture(scope="module")
def app():
    return doble_tkinter.gui_app()


class _Widget:
    """El doble minimo de un widget: recuerda el texto, el estado y el motivo."""

    def __init__(self):
        self.texto = ""
        self.encendido = True
        self.motivo = None
        self.seleccion = None

    def config(self, **kw):
        if "text" in kw:
            self.texto = kw["text"]

    configure = config

    def habilitar(self):
        self.encendido, self.motivo = True, None

    def deshabilitar(self, motivo):
        self.encendido, self.motivo = False, motivo

    def estado(self, encendido, motivo):
        self.habilitar() if encendido else self.deshabilitar(motivo)

    def select(self, cual=None):
        self.seleccion = cual

    def update_idletasks(self):
        pass


class _Arbol:
    """El doble minimo de un `Treeview`: filas con sus valores, en orden."""

    def __init__(self):
        self.filas = {}

    def get_children(self):
        return tuple(self.filas)

    def delete(self, iid):
        self.filas.pop(iid)

    def insert(self, _padre, _donde, iid=None, values=()):
        iid = iid if iid is not None else f"I{len(self.filas)}"
        self.filas[iid] = tuple(values)
        return iid


# El grupo de exportacion se lee de la ventana (`app.BOTONES_DE_EXPORTACION`):
# desde UI-2 son siete, y una lista escrita aqui se quedaba corta.


def _ventana(app, *, csv_=None, cuencas="", estacion="", externos=EXTERNOS):
    """Una ventana SIN widgets de verdad: los campos y los dobles que la logica usa."""
    v = object.__new__(app.ExpedienteApp)
    v.proyecto_var = VariableDeTexto("obra UI-1")
    v.csv_var = VariableDeTexto("" if csv_ is None else str(csv_))
    v.datos_externos_var = VariableDeTexto(str(externos) if externos else "")
    v.datos_sitio_var = VariableDeTexto("")
    v.cuencas_var = VariableDeTexto(str(cuencas))
    v.estacion_var = VariableDeTexto(str(estacion))
    v.externos_vars = {clave: VariableDeTexto("") for clave, *_r in app.CAMPOS_EXTERNOS}
    v.externos_vars["luz_m"].set("2,75")
    v.alcance_var = VariableDeTexto(cli.ALCANCE_PERFIL)
    v.informe = None
    v.entradas_de_la_corrida = {}
    v.proyecto_de_la_corrida = ""
    v.sitio_de_la_sesion = {"valores": {}}
    v.sesion_id = "id-ui1"
    v.corridas = []
    for nombre in ("lbl_error_datos", "btn_ejecutar", "nb", "root", "lbl_estado",
                   "lbl_anticipo_criterios", "lbl_anticipo_csv",
                   "lbl_anticipo_diferido", "lbl_anticipo_prevuelo",
                   # VE-5 (ficha C8-02): la lista de corridas para comparar.
                   "cmb_corridas", "btn_comparar_corrida",
                   *app.BOTONES_DE_EXPORTACION):
        setattr(v, nombre, _Widget())
    v.corrida_a_comparar_var = VariableDeTexto("")
    v.tab_datos = object()
    v.tree_anticipo = _Arbol()
    v.tree_prevuelo = _Arbol()
    v._vaciar_tablas_del_informe = lambda motivo: None
    v._llenar_tabla_criterios = lambda: None
    return v


# ===========================================================================
# (a) La ayuda de los dos CSV sale de src/
# ===========================================================================

def test_a_la_ayuda_de_la_hidrologia_deriva_las_dos_cabeceras_del_cargador():
    from src import ayuda_entrada as ay
    assert ay.cabecera_cuencas() == ",".join(MH.COLUMNAS_CUENCAS
                                             + MH.COLUMNAS_CUENCAS_OPCIONALES)
    assert ay.cabecera_estacion() == ",".join(MH.COLUMNAS_ESTACION)
    fichas = ay.fichas_de_hidrologia()
    por_archivo = {}
    for f in fichas:
        por_archivo.setdefault(f.archivo, []).append(f)
    assert [f.clave for f in por_archivo[ay.ARCHIVO_CUENCAS]] == list(
        MH.COLUMNAS_CUENCAS + MH.COLUMNAS_CUENCAS_OPCIONALES)
    assert [f.clave for f in por_archivo[ay.ARCHIVO_ESTACION]] == list(MH.COLUMNAS_ESTACION)
    for f in fichas:
        assert f.obligatoria == (f.clave in MH.COLUMNAS_CUENCAS
                                 or f.archivo == ay.ARCHIVO_ESTACION), f.clave
    assert MH.MARCA_COMENTARIO in ay.PARRAFO_HIDROLOGIA
    assert "§2-bis" in ay.PARRAFO_HIDROLOGIA


def _fila_valida():
    return {"id": "A-02", "area_km2": "2.1", "L_cauce_m": "2400",
            "S_cauce_cuenca": "0.045", "S_terreno": "0.045",
            "cobertura": "cultivos", "suelo": "semipermeable",
            "estacion": "PRUEBA", "metodo_tc": MH.TC_METODO_KIRPICH,
            "H_desnivel_m": "", "ajuste_kirpich": "ninguno", "CN": ""}


def _cuencas_con(tmp_path, fila, nombre="c.csv"):
    columnas = list(MH.COLUMNAS_CUENCAS + MH.COLUMNAS_CUENCAS_OPCIONALES)
    ruta = tmp_path / nombre
    with ruta.open("w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=columnas, restval="")
        escritor.writeheader()
        escritor.writerow(fila)
    return ruta


def _fila_para(columna, clave):
    """Una fila valida con `columna = clave`, y lo que esa clave arrastra."""
    fila = _fila_valida()
    fila[columna] = clave
    if columna == "cobertura" and clave in MH.SUPERFICIES_VIALES:
        fila["suelo"] = ""
    if columna == "metodo_tc" and clave != MH.TC_METODO_KIRPICH:
        fila["ajuste_kirpich"] = ""
    return fila


def ay_titulos():
    from src import ayuda_entrada as ay
    return tuple(ay.TITULOS_DE_LA_HIDROLOGIA.values())


def test_a_lo_que_admite_cada_columna_no_afirma_que_sea_libre(tmp_path, con_fen):
    """
    Revision de UI-1: `cuencas.estacion` y `cuencas.id` remiten a OTRO archivo
    y la ayuda lo dice (`REMISIONES_DE_LA_HIDROLOGIA`); la guardia es de
    comportamiento: una estacion que el CSV de la estacion no trae detiene la
    carga, y una cuenca sin obra queda como bloqueo de la corrida.
    """
    from src import ayuda_entrada as ay
    por_clave = {(f.archivo, f.clave): f for f in ay.fichas_de_hidrologia()}
    for (archivo, clave), texto in ay.REMISIONES_DE_LA_HIDROLOGIA.items():
        assert por_clave[(archivo, clave)].que_admite == texto
    assert por_clave[(ay.ARCHIVO_CUENCAS, "area_km2")].que_admite == ay.SIN_LISTA_CERRADA
    fila = _fila_valida()
    fila["estacion"] = "NO-ESTA-EN-LA-SERIE"
    with pytest.raises(DatoFaltanteError) as exc:
        servicio.cargar_hidrologia(_cuencas_con(tmp_path, fila), ESTACION)
    assert exc.value.campo == "estacion"
    fila = _fila_valida()
    fila.update({"id": "Z-99", "estacion": "PRUEBA-SINTETICA"})
    informe = cli.correr(CSV_EJEMPLO, _externos(), alcance=cli.ALCANCE_PERFIL,
                         hidrologia=servicio.cargar_hidrologia(
                             _cuencas_con(tmp_path, fila), ESTACION))
    # Es un BLOQUEO que cuenta para el cierre, no un aviso: esta en
    # `bloqueos_reales` (la unica definicion de «etapa bloqueada», EXT-G-02)
    # y el expediente no cierra. La ayuda dice eso y no otra cosa.
    reales = [b for _punto, b in informe.bloqueos_reales()
              if b.etapa == "cuencas declaradas"]
    assert len(reales) == 1 and "Z-99" in reales[0].mensaje
    assert not informe.cerrado
    remision = ay.REMISIONES_DE_LA_HIDROLOGIA[(ay.ARCHIVO_CUENCAS, "id")]
    assert "bloqueo" in remision and "no cierra" in remision
    assert "avis" not in remision


def test_a_las_claves_que_la_ayuda_admite_son_las_que_el_cargador_acepta(tmp_path):
    """
    La lista de claves de cada columna esta escrita en `src/ayuda_entrada.py`
    como la correspondencia columna -> tabla del cargador, y esta guardia la
    ata al CARGADOR: cada clave listada pasa, y una que no existe se rechaza
    nombrando la columna. Si manana `cargar_cuencas` valida otra tabla, este
    test falla antes que la ayuda mienta.
    """
    from src import ayuda_entrada as ay
    con_claves = [f for f in ay.fichas_de_hidrologia() if f.claves_admitidas]
    assert {f.clave for f in con_claves} == {"cobertura", "suelo", "metodo_tc",
                                             "ajuste_kirpich", "fen"}
    for f in con_claves:
        if f.archivo != ay.ARCHIVO_CUENCAS:
            continue
        for clave in f.claves_admitidas:
            MH.cargar_cuencas(_cuencas_con(tmp_path, _fila_para(f.clave, clave)))
        with pytest.raises(DatoInvalidoError) as exc:
            MH.cargar_cuencas(_cuencas_con(tmp_path, _fila_para(f.clave, "no_existe")))
        # La Tabla N 08 se pide por el PAR: su campo es «cobertura / suelo».
        assert f.clave in exc.value.campo.split(" / ")
    fen = next(f for f in con_claves if f.clave == "fen")
    for marca in fen.claves_admitidas:
        ruta = tmp_path / "e.csv"
        ruta.write_text(f"estacion,anio,p24_mm,fen\nE,1990,10,{marca}\n", encoding="utf-8")
        MH.cargar_estacion(ruta)
    ruta.write_text("estacion,anio,p24_mm,fen\nE,1990,10,quiza\n", encoding="utf-8")
    with pytest.raises(DatoInvalidoError) as exc:
        MH.cargar_estacion(ruta)
    assert exc.value.campo == "fen"


def test_a_la_ventana_de_ayuda_pinta_la_hidrologia_y_no_la_sabe():
    arbol = ast.parse((RAIZ / "gui" / "ayuda_entrada.py").read_text(encoding="utf-8"))
    llamados = {ast.unparse(n.func) for n in ast.walk(arbol) if isinstance(n, ast.Call)}
    for nombre in ("ay.fichas_de_hidrologia", "ay.secciones_de_hidrologia"):
        assert nombre in llamados, nombre
    leidos = {ast.unparse(n) for n in ast.walk(arbol) if isinstance(n, ast.Attribute)}
    assert "ay.PARRAFO_HIDROLOGIA" in leidos
    # Revision de UI-1: ni los titulos ni lo que admite cada columna se
    # escriben en gui/ (decia «un numero o un texto libre» tambien de
    # `cuencas.estacion`, que no es libre).
    textos_de_gui = {n.value for n in ast.walk(arbol)
                     if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    for titulo in ay_titulos():
        assert titulo not in textos_de_gui, titulo
    assert not any("texto libre" in texto for texto in textos_de_gui)
    # Y la pestaña 1 pide sus dos tooltips a src/ en vez de escribirlos.
    construir = _funcion(ARBOL_GUI, "_construir_tab_datos")
    llamados_gui = _nombres_llamados(construir)
    assert "ay_contenido.ayuda_del_campo_de_hidrologia" in llamados_gui
    textos_tab = {n.value for n in ast.walk(construir)
                  if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert not any("--cuencas" in texto or "--estacion" in texto for texto in textos_tab)
    import gui.ayuda_entrada as gay
    assert gay.PESTANA_HIDROLOGIA not in (gay.PESTANA_CSV, gay.PESTANA_JSON,
                                          gay.PESTANA_CONCEPTOS)
    abrir = ast.unparse(_funcion(ARBOL_GUI, "_abrir_ayuda"))
    assert "PESTANA_HIDROLOGIA" in abrir and "tab_hidrologia" in abrir


# ===========================================================================
# (b) La pestaña 1
# ===========================================================================

def test_b_la_pestana_1_tiene_los_dos_campos_con_examinar_y_ayuda():
    construir = _funcion(ARBOL_GUI, "_construir_tab_datos")
    fuente = ast.unparse(construir)
    textos = {kw.value.value for n in _llamadas(construir) for kw in n.keywords
              if kw.arg == "text" and isinstance(kw.value, ast.Constant)}
    assert "CSV de cuencas (opcional):" in textos
    assert "CSV de la estación (opcional):" in textos
    assert "textvariable=self.cuencas_var" in fuente
    assert "textvariable=self.estacion_var" in fuente
    assert "command=self._elegir_cuencas" in fuente
    assert "command=self._elegir_estacion" in fuente
    assert fuente.count("ayuda_ent.PESTANA_HIDROLOGIA") == 2
    for nombre in ("_elegir_cuencas", "_elegir_estacion"):
        elegir = ast.unparse(_funcion(ARBOL_GUI, nombre))
        assert "filedialog.askopenfilename" in elegir


def test_b_ejecutar_carga_la_hidrologia_con_el_servicio_y_la_pasa_a_correr():
    assert cli.cargar_hidrologia is servicio.cargar_hidrologia
    ejecutar = _funcion(ARBOL_GUI, "ejecutar_pipeline")
    llamadas = {ast.unparse(n.func): n for n in _llamadas(ejecutar)}
    assert "cli.cargar_hidrologia" in llamadas
    correr = llamadas["cli.correr"]
    assert any(kw.arg == "hidrologia" for kw in correr.keywords)
    # En el MISMO try que la carga de los datos externos y que la corrida:
    # un error de carga sale por los mismos brazos.
    for nodo in ast.walk(ejecutar):
        if isinstance(nodo, ast.Try):
            dentro = {ast.unparse(n.func) for b in nodo.body for n in ast.walk(b)
                      if isinstance(n, ast.Call)}
            if "cli.correr" in dentro:
                assert "cli.cargar_hidrologia" in dentro
                assert "cli.cargar_datos_externos" in dentro
                break
    else:
        raise AssertionError("ejecutar_pipeline ya no corre dentro de un try")


def test_b_con_un_solo_campo_la_ventana_dice_el_mensaje_del_servicio(app, tmp_path):
    for cuencas, estacion in ((CUENCAS, ""), ("", ESTACION)):
        v = _ventana(app, csv_=_csv_sin_caudal(tmp_path), cuencas=cuencas,
                     estacion=estacion)
        v.ejecutar_pipeline()
        with pytest.raises(DatoFaltanteError) as esperado:
            servicio.cargar_hidrologia(Path(cuencas) if cuencas else None,
                                       Path(estacion) if estacion else None)
        assert v.informe is None
        assert str(esperado.value) in v.lbl_error_datos.texto
        assert v.lbl_error_datos.texto.startswith("El expediente no se puede cargar")
        for nombre in app.BOTONES_DE_EXPORTACION:
            assert getattr(v, nombre).motivo == app.MOTIVO_CORRIDA_FALLIDA


def test_b_un_archivo_que_no_existe_sale_como_el_del_json(app, tmp_path):
    v = _ventana(app, csv_=_csv_sin_caudal(tmp_path), cuencas=tmp_path / "no.csv",
                 estacion=ESTACION)
    v.ejecutar_pipeline()
    assert v.informe is None
    assert v.lbl_error_datos.texto.startswith("No se pudo leer la entrada")
    assert "no.csv" in v.lbl_error_datos.texto


def test_b_la_corrida_recibe_la_hidrologia_cargada_y_fotografia_las_rutas(
        app, tmp_path, monkeypatch):
    recibido = {}

    def _correr_que_para(ruta_csv, externos, **kw):
        recibido.update(kw)
        raise DatoInvalidoError("prueba", motivo="se detiene a proposito (UI-1)")

    monkeypatch.setattr(cli, "correr", _correr_que_para)
    v = _ventana(app, csv_=_csv_sin_caudal(tmp_path), cuencas=f"  {CUENCAS}  ",
                 estacion=ESTACION)
    v.ejecutar_pipeline()
    hidrologia = recibido["hidrologia"]
    assert hidrologia is not None
    assert sorted(hidrologia.cuencas) == sorted(OBRAS_CON_CUENCA)
    assert hidrologia.origen_cuencas == str(CUENCAS)
    assert v.entradas_de_la_corrida["cuencas"] == str(CUENCAS)
    assert v.entradas_de_la_corrida["estacion"] == str(ESTACION)
    # Sin los dos campos, None: el caudal entra declarado como siempre.
    recibido.clear()
    v = _ventana(app, csv_=CSV_EJEMPLO)
    v.ejecutar_pipeline()
    assert recibido["hidrologia"] is None
    assert v.entradas_de_la_corrida["cuencas"] == ""
    assert v.entradas_de_la_corrida["estacion"] == ""


def test_b_cambiar_un_campo_invalida_el_informe(app):
    v = _ventana(app)
    pintados = []
    v._pintar_anticipo = lambda: pintados.append(True)
    v.informe = object()
    v._al_cambiar_la_hidrologia()
    assert v.informe is None and pintados
    for nombre in app.BOTONES_DE_EXPORTACION:
        boton = getattr(v, nombre)
        assert not boton.encendido
        assert boton.motivo == app.MOTIVO_HIDROLOGIA_CAMBIADA
    assert "vuelva a ejecutar" in app.MOTIVO_HIDROLOGIA_CAMBIADA.lower()
    # Las dos trazas, en __init__: es el gesto de escribir en cualquiera.
    init = ast.unparse(_funcion(ARBOL_GUI, "__init__"))
    for var in ("self.cuencas_var.trace_add", "self.estacion_var.trace_add"):
        tramo = init[init.index(var):init.index(var) + 160]
        assert "_al_cambiar_la_hidrologia" in tramo, var


def _sin_dialogos(app, monkeypatch):
    """Los dialogos modales, contestados sin pantalla: «si» y nada que mostrar."""
    monkeypatch.setattr(app.messagebox, "askyesno", lambda *a, **k: True)
    monkeypatch.setattr(app.messagebox, "showinfo", lambda *a, **k: None)
    monkeypatch.setattr(app.messagebox, "showerror", lambda *a, **k: None)


def test_b_nuevo_proyecto_vacia_los_dos_campos(app, monkeypatch):
    _sin_dialogos(app, monkeypatch)
    v = _ventana(app, cuencas=CUENCAS, estacion=ESTACION)
    v.nuevo_proyecto()
    assert v.cuencas_var.get() == "" and v.estacion_var.get() == ""


def test_b_la_sesion_de_la_ventana_guarda_las_dos_rutas_como_el_csv(app):
    v = _ventana(app, csv_="tests/ejemplo_puntos.csv",
                 cuencas="tests/fixtures/hidrologia/cuencas_prueba.csv",
                 estacion="tests/fixtures/hidrologia/estacion_prueba.csv")
    data = v._datos_de_sesion()
    assert data["formato_version"] == ses.FORMATO_SESION
    # Tal como se teclearon, igual que el CSV: la convencion de rutas es UNA.
    assert data["csv"] == v.csv_var.get()
    assert data["cuencas"] == v.cuencas_var.get()
    assert data["estacion"] == v.estacion_var.get()
    assert set(data) == set(ses.ESQUEMA_SESION)
    assert ses.errores_de_sesion(data) == []


def test_b_cargar_sesion_repone_los_dos_campos(app, tmp_path, monkeypatch):
    sesion = ses.sesion_vacia("1.0")
    sesion.update({"csv": "tests/ejemplo_puntos.csv",
                   "cuencas": "tests/fixtures/hidrologia/cuencas_prueba.csv",
                   "estacion": "tests/fixtures/hidrologia/estacion_prueba.csv"})
    ruta = _escribir(tmp_path / "s4.json", sesion)
    _sin_dialogos(app, monkeypatch)
    monkeypatch.setattr(app.filedialog, "askopenfilename", lambda **kw: str(ruta))
    v = _ventana(app, cuencas="viejo.csv", estacion="viejo.csv")
    v.cargar_sesion()
    assert v.cuencas_var.get() == sesion["cuencas"]
    assert v.estacion_var.get() == sesion["estacion"]
    # Y una sesion de formato 3 de verdad deja los dos campos vacios.
    monkeypatch.setattr(app.filedialog, "askopenfilename", lambda **kw: str(SESION_V3))
    v.cargar_sesion()
    assert v.cuencas_var.get() == "" and v.estacion_var.get() == ""
    assert v.csv_var.get() == "tests/ejemplo_puntos.csv"


# ===========================================================================
# (c) El anticipo con el mismo conjunto que la CLI
# ===========================================================================

def test_c_el_conjunto_de_obras_calculables_es_uno_en_las_tres_puertas():
    assert servicio.ids_con_caudal_calculable(None) == frozenset()
    h = servicio.cargar_hidrologia(CUENCAS, ESTACION)
    assert servicio.ids_con_caudal_calculable(h) == h.ids_calculables()
    assert cli.ids_con_caudal_calculable is servicio.ids_con_caudal_calculable
    assert "ids_con_caudal_calculable" in _nombres_llamados(
        _funcion(ARBOL_SERVICIO, "correr"))
    assert "ids_con_caudal_calculable" in _nombres_llamados(
        _funcion(ARBOL_CLI, "_prevuelo"))
    pintar = _funcion(ARBOL_GUI, "_pintar_anticipo")
    assert {"cli.ids_con_caudal_calculable", "cli.cargar_hidrologia"} <= \
        _nombres_llamados(pintar)
    prevuelo = next(n for n in _llamadas(pintar)
                    if ast.unparse(n.func) == "antc.datos_faltantes_por_punto")
    assert any(kw.arg == "ids_con_caudal_calculable" for kw in prevuelo.keywords)


def _caudal_del_prevuelo(v):
    salida = {}
    for valores in v.tree_prevuelo.filas.values():
        identificador = valores[0].split(" ")[0]
        if valores[1] == "Q_m3s" and identificador in OBRAS_CON_CUENCA:
            salida[identificador] = (valores[2], valores[3])
    return salida


def test_c_el_anticipo_no_pinta_DETIENE_lo_que_la_corrida_va_a_calcular(app, tmp_path):
    from src import anticipo as antc
    puntos = _csv_sin_caudal(tmp_path)
    v = _ventana(app, csv_=puntos)
    v._pintar_anticipo()
    sin = _caudal_del_prevuelo(v)
    assert set(sin) == set(OBRAS_CON_CUENCA)
    assert all(estado == "DETIENE" for estado, _etapa in sin.values())

    v.cuencas_var.set(str(CUENCAS))
    v.estacion_var.set(str(ESTACION))
    v._pintar_anticipo()
    con = _caudal_del_prevuelo(v)
    assert set(con) == set(OBRAS_CON_CUENCA)
    assert all(c == ("espera", antc.ETAPA_DEPENDE_DE_LA_HIDROLOGIA)
               for c in con.values()), con

    # Con los dos, el aviso que la CLI imprime al pie del pre-vuelo.
    assert antc.AVISO_HIDROLOGIA_NO_CALCULADA in v.lbl_anticipo_prevuelo.texto

    # Con un solo campo el anticipo lo dice con el mensaje del servicio, y
    # no se cae.
    v.estacion_var.set("")
    v._pintar_anticipo()
    with pytest.raises(DatoFaltanteError) as esperado:
        servicio.cargar_hidrologia(CUENCAS, None)
    assert str(esperado.value) in v.lbl_anticipo_prevuelo.texto


def test_c_el_anticipo_dice_lo_mismo_que_el_prevuelo_de_la_cli(app, tmp_path, capsys):
    """
    Revision de UI-1 (regla 2 del §1 de la cadena): para la misma falta, la
    ventana y `cli.py --prevuelo` dicen EL MISMO texto, sacado de un solo
    sitio: el mensaje de carga (`servicio.mensaje_de_carga_fallida`) y el
    aviso de que el pre-vuelo no calcula la hidrologia
    (`anticipo.AVISO_HIDROLOGIA_NO_CALCULADA`).
    """
    from src import anticipo as antc
    puntos = _csv_sin_caudal(tmp_path)
    base = [str(puntos), "--datos-externos", str(EXTERNOS), "--luz", "2.75",
            "--alcance", cli.ALCANCE_PERFIL, "--prevuelo"]
    # Un solo campo: la linea de la CLI es, letra por letra, la de la ventana.
    v = _ventana(app, csv_=puntos, cuencas=CUENCAS)
    v._pintar_anticipo()
    assert cli.main(base + ["--cuencas", str(CUENCAS)]) == 2
    error = capsys.readouterr().err.strip()
    assert error == v.lbl_anticipo_prevuelo.texto
    # Los dos: el aviso, el mismo objeto en las dos puertas.
    v = _ventana(app, csv_=puntos, cuencas=CUENCAS, estacion=ESTACION)
    v._pintar_anticipo()
    cli.main(base + ["--cuencas", str(CUENCAS), "--estacion", str(ESTACION)])
    assert antc.AVISO_HIDROLOGIA_NO_CALCULADA in capsys.readouterr().out
    assert antc.AVISO_HIDROLOGIA_NO_CALCULADA in v.lbl_anticipo_prevuelo.texto
    # Ninguna de las dos puertas los escribe por su cuenta.
    for ruta in (RAIZ / "cli.py", RAIZ / "gui" / "app.py"):
        texto = ruta.read_text(encoding="utf-8")
        assert "pre-vuelo NO calcula la hidrologia" not in texto, ruta.name
        assert f'"{servicio.ROTULO_ENTRADA_ILEGIBLE}' not in texto, ruta.name
        assert f'"{servicio.ROTULO_EXPEDIENTE_NO_CARGABLE}' not in texto, ruta.name


def test_c_el_anticipo_se_refresca_al_cambiar_los_dos_campos():
    cambiar = ast.unparse(_funcion(ARBOL_GUI, "_al_cambiar_la_hidrologia"))
    assert "self._pintar_anticipo()" in cambiar


# ===========================================================================
# (d) La sesion de formato 4
# ===========================================================================

def test_d_el_formato_4_tiene_las_dos_rutas_y_la_sesion_vacia_las_trae_vacias():
    assert ses.FORMATO_SESION == 4
    assert ses.ESQUEMA_SESION["cuencas"] is str
    assert ses.ESQUEMA_SESION["estacion"] is str
    vacia = ses.sesion_vacia("1.0")
    assert vacia["cuencas"] == "" and vacia["estacion"] == ""
    assert ses.migrar_a_actual(vacia) == (vacia, [])
    assert ses.errores_de_sesion({"cuencas": 3})
    assert ses.errores_de_sesion({"estacion": None})


def test_d_el_fixture_v3_es_una_sesion_real_de_la_version_anterior():
    leeme = (SESION_V3.parent / "LEEME.md").read_text(encoding="utf-8")
    assert leeme.startswith("# DATOS DE PRUEBA, NO DEL PROYECTO")
    v3 = json.loads(SESION_V3.read_text(encoding="utf-8"))
    assert v3["formato_version"] == 3
    assert "DATOS DE PRUEBA" in v3["proyecto"]
    assert "cuencas" not in v3 and "estacion" not in v3
    # Lo que el prompt pide que traiga: declaraciones con procedencia, datos
    # de sitio declarados con su origen y una corrida embebida.
    assert v3["criterios"]["valores"] and v3["criterios"]["procedencias"]
    assert all("origen" in d for d in v3["sitio"]["valores"].values())
    assert v3["sitio"]["valores"]
    assert len(v3["corridas"]) == 1
    assert "informe_json" in v3["corridas"][0]
    assert v3["csv_sha1"] == v3["corridas"][0]["csv_sha1"]
    assert ses.errores_de_sesion(v3) == []
    # Y es la sesion de VERDAD de esas entradas (revision de UI-1): las claves
    # del formato 3 que la ventana escribia, su `app_version`, la huella de
    # su corrida es la del CSV que nombra, la corrida embebida es de ese CSV,
    # y el origen de cada [S] es la ruta del campo `datos_sitio`.
    assert set(v3) == set(ses.ESQUEMA_SESION) - {"cuencas", "estacion"}
    assert v3["app_version"] == app_version_de_la_ventana()
    assert v3["csv_sha1"] == _sha1(RAIZ / v3["csv"])
    corrida = v3["corridas"][0]["informe_json"]
    assert corrida["expediente"]["csv"] == v3["csv"]
    assert corrida["expediente"]["csv_sha1"] == v3["csv_sha1"]
    assert corrida["alcance"]["nivel"] == v3["alcance"]
    assert {d["origen"] for d in v3["sitio"]["valores"].values()} == {v3["datos_sitio"]}
    for clave, procedencia in v3["criterios"]["procedencias"].items():
        assert procedencia["clave"] == clave
        assert procedencia["valor"] == v3["criterios"]["valores"][clave]


def app_version_de_la_ventana():
    return doble_tkinter.gui_app().APP_VERSION


def test_d_una_sesion_v3_se_abre_igual_y_se_completa_sin_hidrologia():
    v3 = json.loads(SESION_V3.read_text(encoding="utf-8"))
    migrada, avisos = ses.migrar_a_actual(v3)
    assert avisos == []          # se abre igual que hoy: no hay nada que avisar
    assert migrada["formato_version"] == ses.FORMATO_SESION
    assert migrada["cuencas"] == "" and migrada["estacion"] == ""
    resto = {k: v for k, v in migrada.items()
             if k not in ("cuencas", "estacion", "formato_version")}
    assert resto == {k: v for k, v in v3.items() if k != "formato_version"}
    assert ses.errores_de_sesion(migrada) == []
    # Por la CLI: la misma lectura, sin avisos y sin hidrologia.
    cargada = cli.cargar_sesion_serializada(SESION_V3)
    assert cargada.formato_version == ses.FORMATO_SESION
    assert cargada.cuencas is None and cargada.estacion is None
    assert cargada.avisos == ()
    assert cargada.id == v3["id"]


@pytest.mark.parametrize("vieja", [
    {"proyecto": "obra v1", "csv": "x.csv"},
    {"formato_version": 2, "proyecto": "obra v2", "csv": "x.csv",
     "criterios": {"valores": {}, "procedencias": {}}},
    {"formato_version": 3, "proyecto": "v3 incompleta"},
])
def test_d_las_versiones_anteriores_llegan_a_4_por_escalones(vieja):
    migrada, _avisos = ses.migrar_a_actual(vieja)
    assert migrada["formato_version"] == 4
    assert migrada["cuencas"] == "" and migrada["estacion"] == ""
    assert ses.errores_de_sesion(migrada) == []


def test_d_una_v4_sin_las_dos_claves_se_completa_y_una_v5_no_se_lee():
    migrada, _avisos = ses.migrar_a_actual({"formato_version": 4, "proyecto": "x"})
    assert migrada["cuencas"] == "" and migrada["estacion"] == ""
    with pytest.raises(ValueError):
        ses.migrar_a_actual({"formato_version": 5})


def test_d_la_cli_resuelve_las_dos_rutas_como_resuelve_el_csv(tmp_path):
    sesion = ses.sesion_vacia("1.0")
    sesion.update({"csv": "tests/ejemplo_puntos.csv",
                   "cuencas": "tests/fixtures/hidrologia/cuencas_prueba.csv",
                   "estacion": "tests/fixtures/hidrologia/estacion_prueba.csv"})
    cargada = cli.cargar_sesion_serializada(_escribir(tmp_path / "s.json", sesion))
    assert cargada.csv == Path(sesion["csv"])
    assert cargada.cuencas == Path(sesion["cuencas"])
    assert cargada.estacion == Path(sesion["estacion"])
    vacia = cli.cargar_sesion_serializada(_escribir(tmp_path / "v.json",
                                                    ses.sesion_vacia("1.0")))
    assert vacia.cuencas is None and vacia.estacion is None


def test_d_una_ruta_con_espacios_en_los_extremos_vale_igual_en_las_dos_puertas(
        app, tmp_path):
    """
    Revision de UI-1: la ventana lee el campo sin los espacios de los
    extremos y la CLI, al abrir la sesion, hacia `Path` del texto crudo; una
    ruta con un espacio al final corria en la ventana y no existia para
    `cli.py --sesion`. Una sola convencion: `sesion.ruta_de_campo`.
    """
    assert ses.ruta_de_campo(f"  {CUENCAS}  ") == CUENCAS
    assert ses.ruta_de_campo("   ") is None and ses.ruta_de_campo(None) is None
    v = _ventana(app, cuencas=f"{CUENCAS} ", estacion=f" {ESTACION}")
    assert v._rutas_de_hidrologia() == (CUENCAS, ESTACION)
    puntos = _csv_sin_caudal(tmp_path)
    sesion = _sesion_con_hidrologia(tmp_path, puntos, csv=f"{puntos} ",
                                    cuencas=f"{CUENCAS} ", estacion=f"{ESTACION} ")
    ruta = _escribir(tmp_path / "s.json", sesion)
    cargada = cli.cargar_sesion_serializada(ruta)
    assert (cargada.csv, cargada.cuencas, cargada.estacion) == (puntos, CUENCAS, ESTACION)
    hecho = _cli("--sesion", str(ruta), "--prevuelo")
    assert hecho.returncode in (0, 1), hecho.stderr[-2000:]
    assert "cargaron y se validaron" in hecho.stdout


def test_d_la_cli_abre_la_sesion_v3_y_corre_sin_hidrologia(tmp_path):
    salida = tmp_path / "v3.informe.json"
    hecho = _cli("--sesion", str(SESION_V3), "--json", str(salida))
    assert hecho.returncode in (0, 1), hecho.stderr[-3000:]
    assert "Sesion migrada" not in hecho.stdout
    datos = json.loads(salida.read_text(encoding="utf-8"))
    assert "hidrologia" not in datos["expediente"]
    assert datos["expediente"]["csv"] == "tests/ejemplo_puntos.csv"
    # La corrida que la sesion embebe se compara con la de hoy (E04), y con
    # el archivo de criterios con que se guardo la REPRODUCE: abrir la v3 no
    # perdio nada de lo que su corrida uso. Si el archivo de criterios cambia,
    # DIFIERE es la respuesta correcta, y entonces se pide solo que compare.
    v3 = json.loads(SESION_V3.read_text(encoding="utf-8"))
    from src.modulos.M11_reporte import ARCHIVO_CRITERIOS
    if v3["corridas"][0]["criterios_sha1"] == _sha1(ARCHIVO_CRITERIOS):
        assert "Esta corrida REPRODUCE la guardada en la sesion" in hecho.stdout
    else:
        assert "Esta corrida DIFIERE de la guardada" in hecho.stdout


# ===========================================================================
# (e) El hijo del PDF y la CLI
# ===========================================================================

def _sesion_con_hidrologia(tmp_path, puntos, **campos):
    sesion = ses.sesion_vacia("1.0")
    sesion.update({"proyecto": "obra UI-1", "csv": str(puntos),
                   "datos_externos": str(EXTERNOS), "externos": {"luz_m": "2,75"},
                   "alcance": cli.ALCANCE_PERFIL,
                   "cuencas": str(CUENCAS), "estacion": str(ESTACION),
                   "criterios": dec.estado_de_sesion()})
    sesion.update(campos)
    return sesion


def test_e_la_sesion_del_hijo_lleva_las_rutas_con_que_corrio(tmp_path, con_fen):
    import gui.exportacion_pdf as expdf
    puntos = _csv_sin_caudal(tmp_path)
    informe = cli.correr(puntos, _externos(), alcance=cli.ALCANCE_PERFIL,
                         hidrologia=cli.cargar_hidrologia(CUENCAS, ESTACION))
    entradas = {"csv": str(puntos), "datos_externos": str(EXTERNOS),
                "datos_sitio": "", "externos": {"luz_m": "2,75"},
                "alcance": cli.ALCANCE_PERFIL,
                "cuencas": str(CUENCAS), "estacion": str(ESTACION)}
    sesion = expdf.sesion_de_la_corrida(
        informe, proyecto="obra", formato_version=ses.FORMATO_SESION,
        app_version="1.0", **entradas)
    assert sesion["cuencas"] == str(CUENCAS)
    assert sesion["estacion"] == str(ESTACION)
    assert set(sesion) == set(ses.ESQUEMA_SESION)
    assert ses.errores_de_sesion(json.loads(json.dumps(sesion))) == []
    # Sin hidrologia, las dos vacias.
    sin = expdf.sesion_de_la_corrida(
        informe, proyecto="obra", formato_version=ses.FORMATO_SESION,
        app_version="1.0", **dict(entradas, cuencas="", estacion=""))
    assert sin["cuencas"] == "" and sin["estacion"] == ""
    # La ventana la arma desde la corrida: `entradas_de_la_corrida` las trae.
    ejecutar = ast.unparse(_funcion(ARBOL_GUI, "ejecutar_pipeline"))
    tramo = ejecutar[ejecutar.index("self.entradas_de_la_corrida = "):]
    tramo = tramo[:tramo.index("}") + 1]
    assert "'cuencas'" in tramo and "'estacion'" in tramo


def test_e_la_cli_usa_las_rutas_de_la_sesion_y_la_bandera_escrita_gana(tmp_path, con_fen):
    puntos = _csv_sin_caudal(tmp_path)
    ruta = _escribir(tmp_path / "s.json", _sesion_con_hidrologia(tmp_path, puntos))
    salida = tmp_path / "a.json"
    hecho = _cli("--sesion", str(ruta), "--json", str(salida))
    assert hecho.returncode in (0, 1), hecho.stderr[-3000:]
    datos = json.loads(salida.read_text(encoding="utf-8"))
    hidro = datos["expediente"]["hidrologia"]
    assert hidro["cuencas"] == str(CUENCAS) and hidro["estacion"] == str(ESTACION)
    calculados = [p for p in datos["puntos"]
                  if (p.get("caudal") or {}).get("origen") == "calculado"]
    assert {p["id"] for p in calculados} == set(OBRAS_CON_CUENCA)
    # La bandera escrita gana, campo a campo.
    copia = tmp_path / "otra_cuencas.csv"
    copia.write_bytes(CUENCAS.read_bytes())
    hecho = _cli("--sesion", str(ruta), "--cuencas", str(copia),
                 "--json", str(salida))
    assert hecho.returncode in (0, 1), hecho.stderr[-3000:]
    hidro = json.loads(salida.read_text(encoding="utf-8"))["expediente"]["hidrologia"]
    assert hidro["cuencas"] == str(copia) and hidro["estacion"] == str(ESTACION)
    # El pre-vuelo tambien las toma de la sesion.
    hecho = _cli("--sesion", str(ruta), "--prevuelo")
    assert "--cuencas y --estacion se cargaron y se validaron" in hecho.stdout


def test_e_el_json_del_hijo_es_el_de_la_ventana_con_hidrologia(tmp_path, con_fen):
    """
    Equivalencia por las dos puertas (patron de EXT-8 y EXT-9): la corrida
    de este proceso con la sesion repuesta desde su forma serializada, y la
    del hijo `cli.py --sesion` con esa misma sesion, escriben el MISMO JSON
    salvo la marca de tiempo; y los dos traen la hidrologia.
    """
    puntos = _csv_sin_caudal(tmp_path)
    sesion = _sesion_con_hidrologia(tmp_path, puntos)
    ida_y_vuelta = json.loads(json.dumps(sesion, ensure_ascii=False))
    estado = dec.estado_de_sesion()
    try:
        dec.restaurar_sesion(ida_y_vuelta["criterios"], sustituir=True)
        propio = cli.informe_json(cli.correr(
            puntos, _externos(), alcance=cli.ALCANCE_PERFIL,
            hidrologia=cli.cargar_hidrologia(Path(sesion["cuencas"]),
                                             Path(sesion["estacion"]))))
    finally:
        dec.restaurar_sesion(estado, sustituir=True)
    ruta = _escribir(tmp_path / "s.json", sesion)
    salida = tmp_path / "hijo.json"
    hecho = _cli("--sesion", str(ruta), "--json", str(salida))
    assert hecho.returncode in (0, 1), hecho.stderr[-3000:]
    ajeno = json.loads(salida.read_text(encoding="utf-8"))
    assert "hidrologia" in propio["expediente"] and "hidrologia" in ajeno["expediente"]
    assert _sin_marca(propio) == _sin_marca(ajeno)


def test_e_el_proceso_del_pdf_reproduce_la_corrida_con_hidrologia(tmp_path, con_fen):
    if not M11.weasyprint_disponible():
        pytest.skip("weasyprint no esta operativo en este interprete")
    import time
    import gui.exportacion_pdf as expdf
    puntos = _csv_sin_caudal(tmp_path)
    sesion = _sesion_con_hidrologia(tmp_path, puntos)
    estado = dec.estado_de_sesion()
    try:
        dec.restaurar_sesion(json.loads(json.dumps(sesion["criterios"])), sustituir=True)
        propio = cli.informe_json(cli.correr(
            puntos, _externos(), alcance=cli.ALCANCE_PERFIL,
            hidrologia=cli.cargar_hidrologia(CUENCAS, ESTACION)))
    finally:
        dec.restaurar_sesion(estado, sustituir=True)
    proceso = expdf.ProcesoPdf(sesion=sesion, destino=tmp_path / "m.pdf",
                               plantilla=cli.plantilla_por_alcance(cli.ALCANCE_PERFIL),
                               directorio_trabajo=tmp_path / "trabajo",
                               interprete=sys.executable, raiz=RAIZ)
    proceso.iniciar()
    inicio = time.monotonic()
    while not proceso.sondear().terminal:
        assert time.monotonic() - inicio < 600, "el hijo no termino a tiempo"
        time.sleep(0.05)
    assert proceso.estado is expdf.EstadoPdf.TERMINADO, proceso.detalle
    ajeno = json.loads(proceso.ruta_json.read_text(encoding="utf-8"))
    assert _sin_marca(propio) == _sin_marca(ajeno)
    assert ajeno["expediente"]["hidrologia"]["cuencas"] == str(CUENCAS)


# ===========================================================================
# (f) Las huellas
# ===========================================================================

def test_f_el_contexto_lleva_las_dos_huellas_solo_con_hidrologia(tmp_path, con_fen):
    puntos = _csv_sin_caudal(tmp_path)
    con = cli.correr(puntos, _externos(), alcance=cli.ALCANCE_PERFIL,
                     hidrologia=cli.cargar_hidrologia(CUENCAS, ESTACION))
    assert con.contexto.cuencas_sha1 == _sha1(CUENCAS)
    assert con.contexto.estacion_sha1 == _sha1(ESTACION)
    sin = cli.correr(CSV_EJEMPLO, _externos(), alcance=cli.ALCANCE_PERFIL)
    assert sin.contexto.cuencas_sha1 is None and sin.contexto.estacion_sha1 is None


def test_f_las_huellas_son_de_los_mismos_bytes_que_se_leyeron(tmp_path, monkeypatch):
    """
    Como `csv_sha1` (PC-09): la huella es de los bytes que el cargador
    PARSEO, no del archivo que hay en disco despues. Se prueba sustituyendo
    la lectura: lo que se parsea y lo que se huella cambian JUNTOS.
    """
    original = CUENCAS.read_bytes()
    alterado = original.replace(b"A-02,2.1,2400,", b"A-02,2.1,2500,")
    assert alterado != original
    leer_bytes = servicio.leer_bytes

    def _leer(ruta):
        if Path(ruta) == CUENCAS:
            return alterado
        return leer_bytes(ruta)

    monkeypatch.setattr(servicio, "leer_bytes", _leer)
    h = servicio.cargar_hidrologia(CUENCAS, ESTACION)
    assert h.cuencas["A-02"].L_cauce_m == pytest.approx(2500.0, rel=REL_TRANSPORTE)
    assert h.cuencas_sha1 == hashlib.sha1(alterado).hexdigest()
    assert h.estacion_sha1 == _sha1(ESTACION)
    # Y editar el archivo despues de cargar no mueve la huella cargada.
    monkeypatch.setattr(servicio, "leer_bytes", leer_bytes)
    copia = tmp_path / "c.csv"
    copia.write_bytes(original)
    h = servicio.cargar_hidrologia(copia, ESTACION)
    copia.write_bytes(alterado)
    assert h.cuencas_sha1 == hashlib.sha1(original).hexdigest()


def test_f_el_orden_de_carga_es_el_de_la_partida(tmp_path):
    """
    Revision de UI-1: se lee y se parsea el CSV de cuencas y DESPUES el de la
    estacion, como antes de UI-1. Con un CSV de cuencas mal formado y la
    estacion inexistente, el primer error es el del expediente
    (`DatoFaltanteError`, «El expediente no se puede cargar») y no el de
    archivo; al reves, el archivo de cuencas que no existe sale primero.
    """
    malo = tmp_path / "mal.csv"
    malo.write_text("id,area_km2\nA-02,2.1\n", encoding="utf-8")
    with pytest.raises(DatoFaltanteError):
        servicio.cargar_hidrologia(malo, tmp_path / "no_existe.csv")
    with pytest.raises(FileNotFoundError):
        servicio.cargar_hidrologia(tmp_path / "no_existe.csv", ESTACION)
    # Y el cruce va al final, aparte (`MH.cruzar_entradas`).
    entrada = MH.cruzar_entradas(MH.cargar_cuencas(CUENCAS), MH.cargar_estacion(ESTACION),
                                 CUENCAS, ESTACION)
    assert entrada.ids_calculables() == servicio.cargar_hidrologia(
        CUENCAS, ESTACION).ids_calculables()


def test_f_el_cargador_decodifica_los_bytes_como_leia_el_archivo(tmp_path):
    """Los mismos datos por la ruta y por los bytes: la lectura no cambio."""
    texto = CUENCAS.read_bytes().replace(b"\n", b"\r\n")
    ruta = tmp_path / "crlf.csv"
    ruta.write_bytes(b"\xef\xbb\xbf" + texto)
    por_ruta = MH.cargar_cuencas(ruta)
    por_bytes = MH.cargar_cuencas(ruta, datos=ruta.read_bytes())
    assert {k: (c.area_km2, c.metodo_tc, c.origen) for k, c in por_ruta.items()} == \
        {k: (c.area_km2, c.metodo_tc, c.origen) for k, c in por_bytes.items()}


def test_f_las_huellas_van_al_encabezado_y_al_json_solo_con_hidrologia(tmp_path, con_fen):
    puntos = _csv_sin_caudal(tmp_path)
    con = cli.correr(puntos, _externos(), alcance=cli.ALCANCE_PERFIL,
                     hidrologia=cli.cargar_hidrologia(CUENCAS, ESTACION))
    sin = cli.correr(CSV_EJEMPLO, _externos(), alcance=cli.ALCANCE_PERFIL)
    for vista in (lambda i: M11.memoria_html(
                      i, ruta_plantilla=cli.plantilla_por_alcance(i.alcance)),
                  lambda i: M11.memoria_html(
                      i, ruta_plantilla=cli.plantilla_por_alcance(cli.ALCANCE_EXPEDIENTE)),
                  lambda i: M11.memoria_resumida_html(i)):
        html_con = vista(con)
        encabezado = html_con[:html_con.index("Version de criterios_adoptados")]
        for rotulo in (M11.ROTULO_CSV_CUENCAS, M11.ROTULO_SHA1_CUENCAS,
                       M11.ROTULO_CSV_ESTACION, M11.ROTULO_SHA1_ESTACION):
            assert rotulo in encabezado
        assert con.contexto.cuencas_sha1 in encabezado
        assert con.contexto.estacion_sha1 in encabezado
        html_sin = vista(sin)
        for rotulo in (M11.ROTULO_CSV_CUENCAS, M11.ROTULO_SHA1_CUENCAS):
            assert rotulo not in html_sin
    hidro = cli.informe_json(con)["expediente"]["hidrologia"]
    assert hidro["cuencas_sha1"] == con.contexto.cuencas_sha1
    assert hidro["estacion_sha1"] == con.contexto.estacion_sha1
    assert "hidrologia" not in cli.informe_json(sin)["expediente"]


def test_f_las_filas_del_encabezado_son_vacias_sin_hidrologia(tmp_path, con_fen):
    """
    `M11.filas_hidrologia` sobre la `Trazabilidad` de la corrida: la cadena
    vacia sin hidrologia (el contrato de la linea base) y, con ella, las
    cuatro filas con la ruta que la corrida registro y la huella del
    contexto.
    """
    sin = cli.correr(CSV_EJEMPLO, _externos(), alcance=cli.ALCANCE_PERFIL)
    traza = M11.trazabilidad(Path(sin.csv), sin.contexto, hidrologia=sin.hidrologia)
    assert traza.cuencas is None and traza.cuencas_sha1 is None
    assert M11.filas_hidrologia(traza) == ""
    con = cli.correr(_csv_sin_caudal(tmp_path), _externos(), alcance=cli.ALCANCE_PERFIL,
                     hidrologia=cli.cargar_hidrologia(CUENCAS, ESTACION))
    traza = M11.trazabilidad(Path(con.csv), con.contexto, hidrologia=con.hidrologia)
    filas = M11.filas_hidrologia(traza)
    assert filas.count("<tr>") == 4
    assert str(CUENCAS) in filas and str(ESTACION) in filas
    assert con.contexto.cuencas_sha1 in filas and con.contexto.estacion_sha1 in filas


def test_h_el_comparador_mira_las_huellas_de_la_hidrologia_y_no_sus_rutas(
        tmp_path, con_fen):
    """
    Revision de UI-1 (MEDIA): el comparador no miraba `expediente.hidrologia`,
    y una corrida con la serie de cuencas cambiada decia «REPRODUCE».
    Mismo contenido en otra ruta: iguales. Una linea de comentario mas en el
    CSV de cuencas (el calculo no cambia, la huella si): DIFIEREN, en
    `hidrologia.cuencas_sha1`. Con hidrologia y sin ella: DIFIEREN.
    """
    from src import comparador as compa
    puntos = _csv_sin_caudal(tmp_path)

    def _volcado(cuencas):
        return _sin_marca(cli.informe_json(cli.correr(
            puntos, _externos(), alcance=cli.ALCANCE_PERFIL,
            hidrologia=cli.cargar_hidrologia(cuencas, ESTACION))))

    base = _volcado(CUENCAS)
    # El MISMO nombre de archivo: el origen de cada cuenca lo nombra.
    otra_ruta = tmp_path / "otra" / CUENCAS.name
    otra_ruta.parent.mkdir()
    otra_ruta.write_bytes(CUENCAS.read_bytes())
    assert compa.comparar(base, _volcado(otra_ruta)).iguales
    comentada = tmp_path / "comentada" / CUENCAS.name
    comentada.parent.mkdir()
    comentada.write_bytes(CUENCAS.read_bytes() + b"# una linea de comentario\n")
    distinta = compa.comparar(base, _volcado(comentada))
    assert not distinta.iguales
    assert [d.campo for d in distinta.diferencias] == ["hidrologia.cuencas_sha1"]
    sin = _sin_marca(cli.informe_json(cli.correr(CSV_EJEMPLO, _externos(),
                                                 alcance=cli.ALCANCE_PERFIL)))
    con = _sin_marca(cli.informe_json(cli.correr(
        CSV_EJEMPLO, _externos(), alcance=cli.ALCANCE_PERFIL,
        hidrologia=cli.cargar_hidrologia(CUENCAS, ESTACION))))
    assert not compa.comparar(sin, con).iguales


def test_h_la_cli_dice_DIFIERE_si_la_serie_de_cuencas_cambio_tras_guardar(tmp_path, con_fen):
    """
    El escenario del revisor, por la puerta de la sesion: una sesion v4 con
    hidrologia y su corrida embebida; se añade una linea de comentario al
    CSV de cuencas; `cli.py --sesion` ya no dice «REPRODUCE».
    """
    puntos = _csv_sin_caudal(tmp_path)
    cuencas = tmp_path / "cuencas.csv"
    cuencas.write_bytes(CUENCAS.read_bytes())
    sesion = _sesion_con_hidrologia(tmp_path, puntos, cuencas=str(cuencas))
    estado = dec.estado_de_sesion()
    try:
        dec.restaurar_sesion(json.loads(json.dumps(sesion["criterios"])), sustituir=True)
        informe = cli.correr(puntos, _externos(), alcance=cli.ALCANCE_PERFIL,
                             hidrologia=cli.cargar_hidrologia(cuencas, ESTACION))
    finally:
        dec.restaurar_sesion(estado, sustituir=True)
    volcado = json.loads(json.dumps(cli.informe_json(informe), allow_nan=False))
    sesion["corridas"] = [ses.corrida_para_sesion(informe, volcado)]
    sesion["csv_sha1"] = informe.contexto.csv_sha1
    ruta = _escribir(tmp_path / "s.json", sesion)
    hecho = _cli("--sesion", str(ruta), "--json", str(tmp_path / "a.json"))
    assert hecho.returncode in (0, 1), hecho.stderr[-3000:]
    assert "Esta corrida REPRODUCE" in hecho.stdout
    cuencas.write_bytes(CUENCAS.read_bytes() + b"# una linea de comentario\n")
    hecho = _cli("--sesion", str(ruta), "--json", str(tmp_path / "b.json"))
    assert hecho.returncode in (0, 1), hecho.stderr[-3000:]
    assert "Esta corrida DIFIERE" in hecho.stdout
    assert "Esta corrida REPRODUCE" not in hecho.stdout


@pytest.mark.parametrize("plantilla", ["memoria_alcantarillas.html", "memoria_perfil.html",
                                       "memoria_resumida.html"])
def test_f_sin_hidrologia_el_encabezado_no_gana_ni_un_byte(plantilla):
    """
    El marcador va en la MISMA linea que la huella del CSV y su valor sin
    hidrologia es la cadena vacia: el HTML sin hidrologia es, byte a byte,
    el de antes (la linea base de la Familia C lo mide entero).
    """
    texto = (M11.DIR_PLANTILLAS / plantilla).read_text(encoding="utf-8")
    assert '<td class="mono">%%csv_sha1</td></tr>%%filas_hidrologia\n' in texto
    assert texto.count("%%filas_hidrologia") == 1
    assert "filas_hidrologia" in M11.MARCADORES
    assert "filas_hidrologia" in M11.MARCADORES_RESUMIDA


# ===========================================================================
# (g) La ventana de verdad
# ===========================================================================

def _interprete_con_ventana():
    from tests.test_gui_contrato import _ENVOLTORIO, _INTERPRETE
    return _INTERPRETE, _ENVOLTORIO


def test_g_la_ventana_real_calcula_el_caudal_guarda_la_sesion_4_y_abre_la_3(tmp_path):
    interprete, envoltorio = _interprete_con_ventana()
    if interprete is None:
        pytest.skip("ningun interprete disponible puede levantar una ventana "
                    "(falta tkinter, ttkbootstrap o el entorno grafico)")
    from src import anticipo as antc
    hecho = subprocess.run(
        envoltorio + [interprete, "-m", "tests.apoyo.gui_ui1_hidrologia_real",
                      str(tmp_path)],
        cwd=RAIZ, capture_output=True, text=True, timeout=1500)
    assert hecho.returncode == 0, (
        f"la corrida de la GUI fallo:\n{hecho.stdout[-4000:]}\n{hecho.stderr[-4000:]}")
    r = json.loads((tmp_path / "resumen_ui1.json").read_text(encoding="utf-8"))

    # 1. El anticipo: DETIENE sin hidrologia, espera con ella.
    assert set(r["prevuelo_sin_hidrologia"]) == set(OBRAS_CON_CUENCA)
    assert all(c["estado"] == "DETIENE" for c in r["prevuelo_sin_hidrologia"].values())
    assert all(c == {"estado": "espera", "etapa": antc.ETAPA_DEPENDE_DE_LA_HIDROLOGIA}
               for c in r["prevuelo_con_hidrologia"].values())
    assert r["mensaje_del_servicio"] in r["prevuelo_un_campo"]

    # 2. Un solo campo: no corre y dice el mensaje del servicio.
    assert r["un_campo"]["informe_es_None"]
    assert r["mensaje_del_servicio"] in r["un_campo"]["error_visible"]
    assert not any(e["encendido"] for e in r["un_campo"]["exportadores"].values())

    # 3. El caudal calculado, en el detalle de la pestaña 3, con las huellas.
    assert r["caudal"]["calculado"]
    assert r["caudal"]["leyenda"] and r["caudal"]["leyenda"] in r["detalle"]
    linea_del_caudal = next(l for l in r["lineas_de_la_cli"] if "Fase 1b" in l)
    assert linea_del_caudal.strip() in r["detalle"]
    assert "calculado" in linea_del_caudal
    c = r["contexto"]
    assert c["cuencas_sha1"] == c["cuencas_sha1_del_archivo"]
    assert c["estacion_sha1"] == c["estacion_sha1_del_archivo"]
    assert r["json_ventana_hidrologia"]["cuencas_sha1"] == c["cuencas_sha1"]
    assert all(e["encendido"] for e in r["exportadores_tras_correr"].values())
    assert r["entradas_de_la_corrida"]["cuencas"] == str(CUENCAS)

    # 4. Cambiar cualquiera de los dos campos invalida.
    t = r["tras_cambiar_cuencas"]
    assert t["informe_es_None"]
    assert not any(e["encendido"] for e in t["exportadores"].values())
    assert "cuencas" in t["exportadores"]["json"]["motivo"].lower()
    assert r["tras_cambiar_estacion"]["informe_es_None"]

    # 5. El hijo del PDF reproduce la corrida de la ventana, con hidrologia.
    h = r["hijo"]
    assert h["codigo"] in (0, 1), h["stderr"]
    assert h["sesion_cuencas"] == str(CUENCAS) and h["sesion_estacion"] == str(ESTACION)
    assert h["mismo_json"], "el JSON del hijo no es el de la ventana"
    assert h["hidrologia"]["cuencas_sha1"] == c["cuencas_sha1"]

    # 6. La sesion guardada es formato 4 con las dos rutas.
    g = r["sesion_guardada"]
    assert g["formato_version"] == 4 and g["errores"] == []
    assert g["cuencas"] == str(CUENCAS) and g["estacion"] == str(ESTACION)

    # 7. Nuevo proyecto vacia; cargar sesion repone.
    assert r["tras_nuevo"] == {"cuencas": "", "estacion": "", "informe_es_None": True}
    assert r["tras_cargar"]["cuencas"] == str(CUENCAS)
    assert r["tras_cargar"]["estacion"] == str(ESTACION)
    assert r["tras_cargar"]["informe_es_None"]

    # 8. La sesion v3 de verdad: se abre igual, corre sin hidrologia y se
    #    reescribe en 4.
    v3 = r["tras_cargar_v3"]
    assert v3["cuencas"] == "" and v3["estacion"] == ""
    assert all(v3[k] for k in ("proyecto_igual", "csv_igual", "externos_igual",
                               "sitio_igual", "id_igual"))
    assert v3["alcance"] == cli.ALCANCE_EXPEDIENTE and v3["corridas"] == 1
    assert v3["errores_en_dialogos"] == []
    # Lo que la v3 decidio, repuesto: sus criterios (y SOLO los suyos: el FEN
    # de la obra anterior se retira), sus datos de sitio y sus banderas.
    fixture = json.loads(SESION_V3.read_text(encoding="utf-8"))
    assert v3["criterios_declarados"] == sorted(fixture["criterios"]["valores"])
    assert v3["procedencias"] == sorted(fixture["criterios"]["procedencias"])
    assert v3["sitio_declarado"] == sorted(fixture["sitio"]["valores"])
    assert v3["externos"] == {**{c: "" for c in v3["externos"]}, **fixture["externos"]}
    assert r["corrida_v3"]["informe"] and r["corrida_v3"]["hidrologia_es_None"], \
        r["corrida_v3"]["error_visible"]
    w = r["v3_reescrita"]
    assert w["formato_version"] == 4 and w["errores"] == []
    assert w["cuencas"] == "" and w["estacion"] == "" and w["id_igual"]
    assert w["corridas"] == 2
