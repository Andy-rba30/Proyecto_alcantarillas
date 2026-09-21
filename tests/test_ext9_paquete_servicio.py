"""
tests/test_ext9_paquete_servicio.py
===================================
La aceptacion de EXT-9 (PC-08 y las fases E01, E02, E03, E03a, E03b, E03c
del plan de evolucion): `src/` como paquete real con UN SOLO nombre, un solo
estilo de import en todo el repositorio, ningun `sys.path.insert`, y el
servicio de calculo separado de la CLI.

Escrita PRIMERO, en rojo, como manda la cadena EXT: `xfail(strict=True)` en
lo que describia el estado nuevo, medido antes de tocar codigo (4 passed,
10 xfailed, 0 XPASS) y liberado al convertir y mover. La guardia de
identidad --- la que PC-08 pide «antes de mover nada» --- nunca llevo
`xfail`: tiene que valer ANTES y DESPUES del movimiento, porque es el
invariante que el movimiento protege.

Que se vigila, y por que cada cosa
----------------------------------
1. IDENTIDAD (PC-08). `src/` no era paquete y cinco archivos lo insertaban
   en `sys.path`, de modo que `import src.criterios_adoptados` e
   `import criterios_adoptados` eran DOS modulos con dos `_OVERRIDES`, dos
   `_USADOS` y dos `CriterioPendienteError` que no se atrapan entre si. El
   dictamen lo demostro en vivo: `catalogo(CONCRETO, RECTANGULAR)` por una
   via exige los criterios del cajon y por la otra devuelve en silencio la
   norma del tubo. La guardia mide, en un proceso limpio, que ningun archivo
   de `src/` vive bajo dos claves de `sys.modules`.

2. UN SOLO ESTILO. El unico nombre importable es el del paquete: todo
   import de un modulo de `src/` es `from src... import ...`. Se rechaza por
   AST la forma plana (`import criterios_adoptados`, `from modulos import`)
   y la forma `import src.X` (el «import src.» que el prompt de EXT-9 nombra
   como la segunda identidad; con un solo estilo no hace falta una segunda
   escritura). `src/normativa/` conserva sus imports RELATIVOS, que ya eran
   los suyos y no salen del subpaquete: es la excepcion que el prompt
   declara («fuera de src/normativa»).

3. NINGUN `sys.path`. Ni los cinco de produccion ni el de `conftest.py` ni
   los de la suite: la raiz del repositorio es el unico anclaje, y la ponen
   el interprete (`python cli.py`, `python -m src.X`, `python -m gui.app`) o
   pytest (el `conftest.py` de la raiz).

4. SERVICIO. La orquestacion (las fases, `correr`, `correr_punto`, el
   contexto), los dataclasses del informe y la carga de datos externos
   viven en `src/servicio.py`; `cli.py` conserva JSON, texto y argparse.
   Importar y ejecutar el servicio no inicia la CLI ni la GUI, y las dos
   puertas --- el servicio y `cli.main` --- resuelven las mismas entradas y
   producen el mismo informe y el mismo contexto.

5. REEXPORTACIONES. `cli` sigue exponiendo lo que `gui/app.py` y la suite
   leen de el (los atributos se DERIVAN del AST de la GUI y del texto de la
   suite, no se listan a mano), y son el MISMO objeto que el del servicio,
   no una copia: patchear `servicio.X` es patchear lo que la CLI corre.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
PAQUETE = "src"
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.referencia.json"

# Lo que no se barre: `legacy/` es antecedente (no se importa en este
# repositorio, ver CLAUDE.md), y los cachés no son fuente.
FUERA_DEL_BARRIDO = {"legacy", ".git", "__pycache__", ".pytest_cache"}

# Los nombres PLANOS de los modulos y subpaquetes de `src/`: importarlos sin
# el paquete delante es la segunda identidad. Se derivan del arbol, no se
# escriben a mano, para que un modulo nuevo entre solo.
NOMBRES_PLANOS = sorted(
    {ruta.stem for ruta in SRC.glob("*.py") if ruta.stem != "__init__"}
    | {ruta.name for ruta in SRC.iterdir() if ruta.is_dir()
       and ruta.name != "__pycache__"})


def _archivos_python():
    return sorted(
        ruta for ruta in RAIZ.rglob("*.py")
        if not any(parte in FUERA_DEL_BARRIDO for parte in ruta.parts))


def _arbol(ruta: Path) -> ast.AST:
    return ast.parse(ruta.read_text(encoding="utf-8-sig"), filename=str(ruta))


def _relativa(ruta: Path) -> str:
    return ruta.relative_to(RAIZ).as_posix()


# ===========================================================================
# 1. Identidad: ningun archivo de src/ bajo dos claves de sys.modules
# ===========================================================================

PROGRAMA_IDENTIDAD = r"""
import json, sys
from pathlib import Path
import cli                                     # arrastra los once modulos
src = Path(sys.argv[1]).resolve()
# Los modulos que la CLI no arrastra, importados con la convencion que el
# arbol tenga HOY (plana mientras src/ no sea paquete; del paquete despues):
# el sondeo mide un proceso real, no fabrica la mezcla que denuncia.
paquete = (src / "__init__.py").exists()
for nombre in ("anticipo", "ayuda_entrada", "indice_formulas", "sesion",
               "traza_punto", "ventana_normativa", "variables_entrada",
               "normativa.manifiesto"):
    __import__(f"src.{nombre}" if paquete else nombre)
por_archivo = {}
for clave, modulo in list(sys.modules.items()):
    archivo = getattr(modulo, "__file__", None)
    if not archivo:
        continue
    ruta = Path(archivo).resolve()
    if src not in ruta.parents:
        continue
    por_archivo.setdefault(ruta.relative_to(src).as_posix(), []).append(clave)
print(json.dumps(por_archivo, sort_keys=True))
"""


def _claves_por_archivo_de_src() -> dict:
    hecho = subprocess.run(
        [sys.executable, "-c", PROGRAMA_IDENTIDAD, str(SRC)],
        cwd=RAIZ, capture_output=True, text=True, timeout=300)
    assert hecho.returncode == 0, hecho.stderr[-3000:]
    return json.loads(hecho.stdout.strip().splitlines()[-1])


def test_pc08_ningun_modulo_de_src_vive_bajo_dos_claves_de_sys_modules():
    """
    La guardia de identidad, en subproceso: `import cli` y los modulos de
    `src/` que la CLI no arrastra, y cada archivo bajo `src/` aparece en
    `sys.modules` bajo UNA clave. Dos claves son dos modulos con dos
    estados (PC-08). Vale antes y despues de convertir `src/` en paquete.
    """
    por_archivo = _claves_por_archivo_de_src()
    assert por_archivo, "el sondeo no encontro ningun modulo bajo src/"
    dobles = {archivo: claves for archivo, claves in por_archivo.items()
              if len(claves) != 1}
    assert not dobles, (
        "archivos de src/ importados bajo DOS claves (dos modulos, dos "
        f"estados; PC-08): {dobles}")
    # El sondeo no es vacuo: los tres archivos con estado estan.
    for nombre in ("criterios_adoptados.py", "datos_sitio.py", "declaracion.py"):
        assert nombre in por_archivo, f"{nombre} no llego a importarse"


# ===========================================================================
# 2 y 3. Un solo estilo de import, ningun sys.path
# ===========================================================================

def _imports_planos(ruta: Path):
    """Los imports que nombran un modulo de src/ SIN el paquete delante."""
    hallados = []
    for nodo in ast.walk(_arbol(ruta)):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                if alias.name.split(".")[0] in NOMBRES_PLANOS:
                    hallados.append((nodo.lineno, f"import {alias.name}"))
        elif isinstance(nodo, ast.ImportFrom) and nodo.level == 0 and nodo.module:
            if nodo.module.split(".")[0] in NOMBRES_PLANOS:
                hallados.append((nodo.lineno, f"from {nodo.module} import ..."))
    return hallados


def _imports_de_la_forma_import_src(ruta: Path):
    """`import src.X [as Y]`: la escritura que el prompt de EXT-9 rechaza."""
    return [(nodo.lineno, f"import {alias.name}")
            for nodo in ast.walk(_arbol(ruta)) if isinstance(nodo, ast.Import)
            for alias in nodo.names
            if alias.name == PAQUETE or alias.name.startswith(PAQUETE + ".")]


def _imports_relativos(ruta: Path):
    return [nodo.lineno for nodo in ast.walk(_arbol(ruta))
            if isinstance(nodo, ast.ImportFrom) and nodo.level > 0]


def _toca_sys_path(ruta: Path):
    """Toda llamada `sys.path.<algo>(...)` y toda asignacion a `sys.path`."""
    hallados = []
    for nodo in ast.walk(_arbol(ruta)):
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute):
            objeto = nodo.func.value
            if (isinstance(objeto, ast.Attribute) and objeto.attr == "path"
                    and isinstance(objeto.value, ast.Name)
                    and objeto.value.id == "sys"):
                hallados.append((nodo.lineno, f"sys.path.{nodo.func.attr}"))
        if isinstance(nodo, (ast.Assign, ast.AugAssign)):
            destinos = (nodo.targets if isinstance(nodo, ast.Assign)
                        else [nodo.target])
            for destino in destinos:
                if (isinstance(destino, ast.Attribute) and destino.attr == "path"
                        and isinstance(destino.value, ast.Name)
                        and destino.value.id == "sys"):
                    hallados.append((nodo.lineno, "sys.path ="))
    return hallados




def test_src_es_un_paquete_real_y_no_un_namespace():
    """
    `src/__init__.py` y `src/modulos/__init__.py` existen y `src` se resuelve
    como paquete REGULAR (con origen), no como namespace package: un
    namespace es lo que hoy permite `python -m src.normativa.manifiesto`
    sin que `src` sea un nombre, y esa ambiguedad es la que PC-08 explota.
    """
    import importlib.util
    assert (SRC / "__init__.py").exists()
    assert (SRC / "modulos" / "__init__.py").exists()
    assert (SRC / "normativa" / "__init__.py").exists()
    spec = importlib.util.find_spec(PAQUETE)
    assert spec is not None and spec.origin is not None, (
        "`src` se resuelve como namespace package, no como paquete real")
    assert Path(spec.origin).resolve() == (SRC / "__init__.py").resolve()


def test_ningun_archivo_del_repositorio_toca_sys_path():
    """
    Los cinco `sys.path.insert` de produccion (cli.py, gui/app.py,
    gui/ayuda_entrada.py, gui/ventana_normativa.py, src/indice_formulas.py),
    el de `conftest.py` y los de la suite: ninguno. La raiz la pone quien
    ejecuta, no quien importa.
    """
    hallados = {_relativa(ruta): toques
                for ruta in _archivos_python()
                if (toques := _toca_sys_path(ruta))}
    assert not hallados, f"archivos que manipulan sys.path: {hallados}"


def test_ningun_archivo_importa_un_modulo_de_src_por_su_nombre_plano():
    """
    Un solo estilo: `from src... import ...`. La forma plana es la segunda
    identidad de PC-08 y se rechaza en TODO el repositorio (produccion,
    GUI, suite, scripts de apoyo, `conftest.py`).
    """
    hallados = {_relativa(ruta): planos
                for ruta in _archivos_python()
                if (planos := _imports_planos(ruta))}
    assert not hallados, (
        "imports planos de modulos de src/ (segunda identidad, PC-08): "
        f"{hallados}")


def test_ningun_archivo_escribe_import_src_punto():
    """
    La escritura `import src.X` se rechaza en todo el repositorio: hoy porque
    crea la segunda identidad (0 usos en produccion, PC-08), y despues del
    paquete porque el estilo unico es `from src... import ...`. Vale antes y
    despues; el prompt de EXT-9 la pide «antes de mover nada».
    """
    hallados = {_relativa(ruta): usos
                for ruta in _archivos_python()
                if (usos := _imports_de_la_forma_import_src(ruta))}
    assert not hallados, f"`import src.` fuera de estilo: {hallados}"


def test_los_imports_relativos_solo_viven_en_src_normativa():
    """
    `src/normativa/` conserva sus imports relativos (son los suyos desde que
    es paquete y no salen del subpaquete). Fuera de el, ninguno: un relativo
    en `src/modulos/` seria un tercer estilo.
    """
    normativa = SRC / "normativa"
    hallados = {_relativa(ruta): lineas
                for ruta in _archivos_python()
                if normativa not in ruta.parents
                and (lineas := _imports_relativos(ruta))}
    assert not hallados, f"imports relativos fuera de src/normativa: {hallados}"


def test_el_detector_de_imports_ve_las_tres_formas(tmp_path):
    """Un mutante del detector que no viera una forma dejaria la guardia vacua."""
    archivo = tmp_path / "x.py"
    archivo.write_text(
        "import criterios_adoptados as ca\n"
        "from modulos import M4_control\n"
        "from modulos.M3_hidraulica import geometria\n"
        "import src.datos_sitio as ds\n"
        "from src import declaracion\n"
        "from . import esquema\n"
        "import sys\nsys.path.insert(0, 'x')\nsys.path.append('y')\n",
        encoding="utf-8")
    assert [f for _, f in _imports_planos(archivo)] == [
        "import criterios_adoptados", "from modulos import ...",
        "from modulos.M3_hidraulica import ..."]
    assert [f for _, f in _imports_de_la_forma_import_src(archivo)] == [
        "import src.datos_sitio"]
    assert _imports_relativos(archivo) == [6]
    assert [f for _, f in _toca_sys_path(archivo)] == [
        "sys.path.insert", "sys.path.append"]


# ===========================================================================
# 4. El servicio de calculo
# ===========================================================================

# Lo que E01 mueve de cli.py: la orquestacion, los dataclasses del informe y
# la carga de datos externos. La lista es de ACEPTACION (lo que el prompt
# nombra); la guardia de abajo comprueba ademas que cli.py no DEFINA nada de
# lo que el servicio define, sea cual sea el nombre.
ORQUESTACION = (
    "correr", "correr_punto", "correr_cabezal", "capturar_contexto",
    "_bloqueo", "_etapa", "_verificador_perfil", "_fase_2", "_fase_diseno",
    "_fase_6", "_fase_7", "_fase_8", "_fase_10", "_diferir_fase_8",
    "_compuerta_metodo_h_o", "_resolver_tw", "_resolver_longitud",
    "_completar_s_cauce", "_avisar_ids_desconocidos", "_cabezal_diferido",
)
DATACLASSES_DEL_INFORME = ("DatoDeclarado", "InformePunto", "InformeCabezal",
                           "ResumenDeCorrida", "Informe")
CARGA_DE_DATOS_EXTERNOS = ("DatosExternos", "cargar_datos_externos",
                           "_dato_externo", "_numero_externo", "_exige_clave",
                           "CLAVES_EXTERNAS", "CLAVES_TEXTO", "_DOMINIO_DE_CLAVE")
DATOS_DEL_ALCANCE = ("ALCANCE_PERFIL", "ALCANCE_EXPEDIENTE",
                     "MODULOS_DIFERIDOS_POR_ALCANCE",
                     "VERIFICACIONES_DIFERIDAS_POR_ALCANCE",
                     "FAMILIAS_QUE_USAN", "familias_que_usan",
                     "familias_del_csv", "puntos_por_familia")
ADAPTADORES_QUE_SE_QUEDAN = ("main", "_parser", "informe_json", "volcar",
                             "plantilla_por_alcance", "declarar_criterios",
                             "cargar_sesion_serializada",
                             "aplicar_sesion_serializada", "PREFIJO_PROGRESO")


def _definidos_en(ruta: Path) -> set:
    """Nombres definidos EN el archivo (def, class, asignacion de modulo)."""
    nombres = set()
    for nodo in _arbol(ruta).body:
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            nombres.add(nodo.name)
        elif isinstance(nodo, ast.Assign):
            nombres |= {d.id for d in nodo.targets if isinstance(d, ast.Name)}
        elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
            nombres.add(nodo.target.id)
    return nombres


def test_e01_la_orquestacion_vive_en_el_servicio_y_no_en_cli():
    """
    `src/servicio.py` DEFINE la orquestacion, los dataclasses y la carga de
    datos externos; `cli.py` ya no define nada de eso (los reexporta) y
    sigue definiendo los adaptadores.
    """
    servicio = SRC / "servicio.py"
    assert servicio.exists(), "falta src/servicio.py"
    en_servicio = _definidos_en(servicio)
    en_cli = _definidos_en(RAIZ / "cli.py")
    movidos = (ORQUESTACION + DATACLASSES_DEL_INFORME
               + CARGA_DE_DATOS_EXTERNOS + DATOS_DEL_ALCANCE)
    faltan = [n for n in movidos if n not in en_servicio]
    assert not faltan, f"el servicio no define: {faltan}"
    duplicados = sorted(en_servicio & en_cli)
    assert not duplicados, (
        "cli.py DEFINE lo que el servicio ya define (dos definiciones, dos "
        f"comportamientos): {duplicados}")
    quedan = [n for n in ADAPTADORES_QUE_SE_QUEDAN if n not in en_cli]
    assert not quedan, f"cli.py dejo de definir sus adaptadores: {quedan}"


def test_e01_el_servicio_no_importa_cli_ni_gui_ni_argparse():
    """Por AST: el servicio no conoce a sus adaptadores."""
    arbol = _arbol(SRC / "servicio.py")
    importados = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            importados |= {a.name.split(".")[0] for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            importados.add(nodo.module.split(".")[0])
    assert not importados & {"cli", "gui", "argparse", "tkinter", "ttkbootstrap"}, (
        f"el servicio importa a un adaptador: {importados}")


PROGRAMA_SERVICIO_SOLO = r"""
import json, sys
from pathlib import Path
from src import servicio
externos = servicio.cargar_datos_externos(Path(sys.argv[2]), {})
informe = servicio.correr(Path(sys.argv[1]), externos,
                          alcance=servicio.ALCANCE_EXPEDIENTE)
print(json.dumps({
    "cli": "cli" in sys.modules,
    "gui": any(k == "gui" or k.startswith("gui.") for k in sys.modules),
    "tkinter": "tkinter" in sys.modules,
    "ttkbootstrap": "ttkbootstrap" in sys.modules,
    "puntos": len(informe.puntos),
    "contexto": informe.contexto is not None,
}))
"""


def test_e02_importar_y_ejecutar_el_servicio_no_inicia_cli_ni_gui():
    """
    En un proceso limpio: `from src import servicio`, una corrida entera, y
    ni `cli` ni `gui` ni Tk llegaron a `sys.modules`. (`argparse` no se mide
    aqui porque lo importa scipy por su cuenta; que el servicio no lo importe
    lo fija la guardia por AST de arriba.)
    """
    hecho = subprocess.run(
        [sys.executable, "-c", PROGRAMA_SERVICIO_SOLO,
         str(CSV_EJEMPLO), str(EXTERNOS_EJEMPLO)],
        cwd=RAIZ, capture_output=True, text=True, timeout=300)
    assert hecho.returncode == 0, hecho.stderr[-3000:]
    medido = json.loads(hecho.stdout.strip().splitlines()[-1])
    assert medido["puntos"] > 0 and medido["contexto"] is True, medido
    assert not medido["cli"], "el servicio arrastro a cli"
    assert not medido["gui"] and not medido["tkinter"] \
        and not medido["ttkbootstrap"], f"el servicio arrastro a la GUI: {medido}"


def _sin_marca_de_tiempo(informe_json: dict) -> dict:
    copia = json.loads(json.dumps(informe_json))
    copia.pop("generado", None)
    return copia


def test_e02_equivalencia_por_las_dos_puertas(tmp_path):
    """
    Las MISMAS entradas por el servicio (`cargar_datos_externos` + `correr`)
    y por la CLI (`cli.main` con las banderas equivalentes) dan las mismas
    entradas resueltas, el mismo informe y el mismo contexto: se compara el
    JSON entero salvo la marca de tiempo. Los datos declarados viajan con
    su origen, de modo que la comparacion cubre tambien de donde salio cada
    uno.
    """
    import cli
    from src import servicio

    externos = servicio.cargar_datos_externos(
        EXTERNOS_EJEMPLO, {"luz_m": None, "TW_m": None, "longitud_m": None,
                           "L_hidraulico_m": None, "categoria_tr": None})
    por_servicio = servicio.correr(CSV_EJEMPLO, externos,
                                   alcance=servicio.ALCANCE_EXPEDIENTE)
    contexto_servicio = por_servicio.contexto

    destino = tmp_path / "por_cli.json"
    codigo = cli.main([str(CSV_EJEMPLO), "--datos-externos", str(EXTERNOS_EJEMPLO),
                       "--alcance", servicio.ALCANCE_EXPEDIENTE,
                       "--json", str(destino)])
    assert codigo in (0, 1), codigo
    por_cli = json.loads(destino.read_text(encoding="utf-8"))

    assert _sin_marca_de_tiempo(cli.informe_json(por_servicio)) \
        == _sin_marca_de_tiempo(por_cli)
    # El contexto: lo que la corrida uso y con que valores. La CLI vuelve a
    # correr, de modo que el registro de usos tiene que ser el mismo.
    assert contexto_servicio is not None
    assert [c["clave"] for c in por_cli["criterios"]["usados"]] \
        == list(contexto_servicio.criterios_usados)
    assert por_cli["expediente"]["csv_sha1"] == contexto_servicio.csv_sha1


# ===========================================================================
# 5. Reexportaciones: lo que la GUI y la suite leen de `cli`
# ===========================================================================

def _atributos_de_cli_en(ruta: Path) -> set:
    """Los `cli.X` que un archivo escribe (por AST: atributos sobre `cli`)."""
    return {nodo.attr for nodo in ast.walk(_arbol(ruta))
            if isinstance(nodo, ast.Attribute)
            and isinstance(nodo.value, ast.Name) and nodo.value.id == "cli"}


def _privados_de_cli_en_la_suite() -> set:
    """
    Los `cli._x` que la suite ESCRIBE COMO CODIGO, leidos del AST de cada
    archivo de tests (una mencion en prosa, como las de este docstring, no
    es un uso).
    """
    privados = set()
    for ruta in (RAIZ / "tests").rglob("*.py"):
        if "__pycache__" in ruta.parts:
            continue
        privados |= {n for n in _atributos_de_cli_en(ruta) if n.startswith("_")}
    return {p for p in privados if not p.startswith("__")}


def test_e03_cli_reexporta_el_mismo_objeto_que_el_servicio():
    """
    Cada atributo que `gui/app.py` lee de `cli`, y cada privado que la
    suite lee de `cli`, existe en `cli` y --- cuando el servicio lo define ---
    ES el mismo objeto. Sin identidad, un `monkeypatch.setattr(servicio, ...)`
    no alcanzaria a lo que la CLI corre, y al reves.
    """
    import cli
    from src import servicio

    de_la_gui = _atributos_de_cli_en(RAIZ / "gui" / "app.py")
    de_la_suite = _privados_de_cli_en_la_suite()
    assert de_la_gui and de_la_suite, "el censo salio vacio"
    en_servicio = _definidos_en(SRC / "servicio.py")
    for nombre in sorted(de_la_gui | de_la_suite):
        if nombre in ("py", "__doc__"):
            continue
        # `_fase_` es un prefijo que la suite escribe en prosa, no un nombre.
        if nombre.endswith("_") and not hasattr(cli, nombre):
            continue
        assert hasattr(cli, nombre), f"cli dejo de exponer {nombre}"
        if nombre in en_servicio:
            assert getattr(cli, nombre) is getattr(servicio, nombre), (
                f"cli.{nombre} no es el objeto del servicio: patchear uno no "
                "alcanza al otro")


def test_e03_anticipo_ayuda_e_indice_apuntan_al_servicio_y_no_a_cli():
    """
    Los tres consumidores de `src/` que leian de `cli` (2, 5 y 2 atributos)
    leen ahora del servicio: ningun `import cli` ni `cli.X` en ellos, y si
    un uso de `servicio`.
    """
    for nombre in ("anticipo.py", "ayuda_entrada.py", "indice_formulas.py"):
        ruta = SRC / nombre
        arbol = _arbol(ruta)
        importa_cli = [nodo.lineno for nodo in ast.walk(arbol)
                       if (isinstance(nodo, ast.Import)
                           and any(a.name == "cli" for a in nodo.names))
                       or (isinstance(nodo, ast.ImportFrom)
                           and nodo.module == "cli")]
        assert not importa_cli, f"{nombre} sigue importando cli: {importa_cli}"
        assert not _atributos_de_cli_en(ruta), f"{nombre} sigue leyendo cli.X"
        usa_servicio = any(
            isinstance(nodo, ast.ImportFrom) and nodo.module == PAQUETE
            and any(a.name == "servicio" for a in nodo.names)
            for nodo in ast.walk(arbol))
        assert usa_servicio, f"{nombre} no importa el servicio"


def test_las_dos_entradas_del_paquete_comparten_convencion():
    """
    `python -m src.indice_formulas` y `python -m src.normativa.manifiesto`
    arrancan por la misma via (`-m` desde la raiz, sin path a mano): sin
    `--escribir` cada uno solo comprueba su documento generado, y en un
    proceso limpio lo encuentra sincronizado.
    """
    for modulo, senal in (("src.indice_formulas", "sincronizado"),
                          ("src.normativa.manifiesto", "manifiesto_citas.md")):
        hecho = subprocess.run([sys.executable, "-m", modulo],
                               cwd=RAIZ, capture_output=True, text=True,
                               timeout=600)
        assert hecho.returncode == 0, (modulo, hecho.stdout[-1500:],
                                       hecho.stderr[-2000:])
        assert senal in hecho.stdout, (modulo, hecho.stdout[:500])
