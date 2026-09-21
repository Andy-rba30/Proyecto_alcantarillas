"""
tests/test_ext8_rendimiento_gui.py
==================================
Aceptacion del cluster «rendimiento y GUI no bloqueante» del dictamen de la
auditoria externa del 2026-09-19 (PC-10, PC-11, PC-12, PC-17), ejecutada por
EXT-8 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md.

Escritos PRIMERO, en rojo, con `xfail(strict=True)` y la expectativa del
invariante como oraculo --- nunca la salida actual ---, y liberados al
corregir. Cuatro bloques, uno por punto ciego:

  PC-10  `import cli` costaba 0.8--1.0 s (medido aqui: 870--930 ms) porque
         weasyprint se importaba SIEMPRE (383 ms) aunque no hubiera `--pdf`,
         `scipy.optimize` en el import de M3/M4 (232 ms) y
         `variables_entrada` parseaba el AST de trece modulos al importar
         (~140 ms). Presupuesto: `import cli` < 0.3 s sin weasyprint, medido
         con `-X importtime`, y ninguno de los tres cargado tras el import.
  PC-11  el PDF corria en el HILO DE TK (11 s / 287 MB para 4 puntos; 360 s y
         5.7 GB para 200). Sale a un SUBPROCESO (`cli.py --sesion ... --pdf`),
         con progreso por lineas de stdout, cancelacion terminando el
         proceso, boton apagado con motivo visible y estado terminal claro.
         El contrato `M11.WeasyHTML` que la GUI sondea y los tests parchean
         se conserva.
  PC-12  la memoria HTML pesaba 54 KB marginales por punto (medido en este
         arbol a alcance expediente; el dictamen midio 67 KB sobre 40 puntos)
         con el 44 % de texto repetido: el paso 2.1 (F2.LUZ) se renderizaba
         DOS veces por punto, los punteros («el detalle esta en el bloque de
         discrepancias») se repetian x90 y las citas, fundamentos y umbrales
         iban enteros en cada paso. Sale un anexo unico con ancla por
         `cita_id` al que cada punto enlaza, construido por streaming.
  PC-17  accesibilidad minima: rueda en X11/macOS (<Button-4>/<Button-5>,
         delta normalizado), motivo del boton apagado en un ROTULO visible
         ademas del tooltip, Escape en las emergentes y Control-Return para
         ejecutar.

Lo que NO se prueba aqui: la cifra de «< 15 KB por punto» del dictamen se
MIDE despues de corregir y el test de tamano se fija con la medida (ver
`KB_POR_PUNTO_MAX` y `PAGINAS_POR_PUNTO_MAX`, con su medicion al lado).
"""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

import cli
from src import criterios_adoptados as ca
from src import declaracion as dec
from src import sesion as ses
from src.modulos import M11_reporte as M11
from src.normativa import registro as _registro
from tests.apoyo.aproximacion import REL_TRANSPORTE
from tests.apoyo.criterios import con_valor

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
EXTERNOS_AMPLIADOS = RAIZ / "tests" / "linea_base_familia_c" / "entradas_ampliadas.json"
GUI = RAIZ / "gui" / "app.py"
COMPONENTES = RAIZ / "gui" / "componentes.py"
VENTANA = RAIZ / "gui" / "ventana_normativa.py"
AYUDA = RAIZ / "gui" / "ayuda_entrada.py"
EXPORTACION = RAIZ / "gui" / "exportacion_pdf.py"
PLANTILLAS = (RAIZ / "src" / "plantillas" / "memoria_alcantarillas.html",
              RAIZ / "src" / "plantillas" / "memoria_perfil.html")

# Nacio con `pytestmark = pytest.mark.xfail(strict=True)` a nivel de modulo:
# medido en rojo ANTES de tocar codigo, 28 xfailed y 0 XPASS (con `sesion`
# y `gui/exportacion_pdf` todavia inexistentes, importados con guardia), y
# liberado al corregir.

# El presupuesto del prompt: `import cli` < 0.3 s sin weasyprint. Se mide con
# `-X importtime` en un subproceso limpio y se toma el MINIMO de tres
# corridas, porque lo que se acota es el coste del import y no el ruido de
# la maquina.
PRESUPUESTO_IMPORT_CLI_S = 0.3
CORRIDAS_IMPORTTIME = 3

# Tamano de la memoria por punto, MEDIDO despues de corregir (ficha EXT-8-01
# de decisiones_diferidas.md): coste marginal por punto de la corrida a
# alcance expediente con las entradas ampliadas de la linea base, cuatro
# puntos contra uno. Medido en EXT-8: 54.0 KB y ~20 paginas por punto antes
# de deduplicar; 44.6 KB y 14.0 paginas despues. El objetivo del dictamen
# (< 15 KB y < 10 paginas) NO se alcanzo: lo que queda es contenido DEL
# PUNTO (la sustitucion con procedencias, 8 KB; las tablas de datos,
# iteraciones y verificaciones, 15 KB; resultados y veredictos), no texto
# repetido --- la repeticion medida cayo del 44 % al 7 % de los bytes ---.
# El techo se fija con holgura sobre la MEDIDA, no sobre el objetivo, para
# que un cambio de formato que suba el coste se vea aqui y no en el
# siguiente PDF de 200 puntos.
KB_POR_PUNTO_MAX = 50.0
PAGINAS_POR_PUNTO_MAX = 16


def _arbol(ruta: Path) -> ast.Module:
    return ast.parse(ruta.read_text(encoding="utf-8-sig"), filename=ruta.name)


def _funcion(arbol: ast.Module, nombre: str):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and nodo.name == nombre:
            return nodo
    raise AssertionError(f"no existe la funcion {nombre!r}")


def _clase(arbol: ast.Module, nombre: str):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ClassDef) and nodo.name == nombre:
            return nodo
    raise AssertionError(f"no existe la clase {nombre!r}")


def _cadenas(nodo) -> set:
    return {n.value for n in ast.walk(nodo)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def _llamadas_a(nodo, nombre: str) -> list:
    return [n for n in ast.walk(nodo) if isinstance(n, ast.Call)
            and ast.unparse(n.func).endswith(nombre)]


def _csv_de_un_punto(tmp_path: Path) -> Path:
    lineas = CSV_EJEMPLO.read_text(encoding="utf-8").splitlines()
    destino = tmp_path / "uno.csv"
    destino.write_text("\n".join(lineas[:2]) + "\n", encoding="utf-8")
    return destino


@pytest.fixture(scope="module")
def informe_expediente():
    externos = cli.cargar_datos_externos(
        EXTERNOS_AMPLIADOS,
        {"luz_m": 2.75, "TW_m": None, "longitud_m": None,
         "L_hidraulico_m": None, "categoria_tr": None})
    return cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_EXPEDIENTE)


@pytest.fixture(scope="module")
def memoria_expediente(informe_expediente):
    return M11.memoria_html(informe_expediente, proyecto="EXT-8")


# ===========================================================================
# PC-10 - imports perezosos y presupuesto de `import cli`
# ===========================================================================

def _importtime_de_cli() -> float:
    """El coste acumulado de `import cli`, en segundos, sin weasyprint."""
    programa = ("import sys; sys.modules['weasyprint'] = None; import cli")
    mejor = None
    for _ in range(CORRIDAS_IMPORTTIME):
        hecho = subprocess.run(
            [sys.executable, "-X", "importtime", "-c", programa],
            cwd=RAIZ, capture_output=True, text=True, timeout=120)
        assert hecho.returncode == 0, hecho.stderr[-2000:]
        for linea in hecho.stderr.splitlines():
            partes = [p.strip() for p in linea.split("|")]
            if len(partes) == 3 and partes[2] == "cli":
                acumulado = int(partes[1]) / 1e6
                mejor = acumulado if mejor is None else min(mejor, acumulado)
    assert mejor is not None, "no aparecio la linea de `cli` en -X importtime"
    return mejor


def test_pc10_import_cli_cabe_en_el_presupuesto_sin_weasyprint():
    """Medido con -X importtime, minimo de tres corridas, en subproceso."""
    medido = _importtime_de_cli()
    assert medido < PRESUPUESTO_IMPORT_CLI_S, (
        f"`import cli` cuesta {medido:.3f} s (minimo de "
        f"{CORRIDAS_IMPORTTIME}); el presupuesto es "
        f"{PRESUPUESTO_IMPORT_CLI_S} s")


def test_pc10_import_cli_no_carga_weasyprint_ni_scipy_ni_el_censo():
    """
    Los tres perezosos, comprobados en un proceso limpio: `import cli` no
    trae weasyprint ni scipy.optimize a `sys.modules`, y el censo de
    `variables_entrada` no se construye hasta que alguien lo pide.
    """
    programa = (
        "import sys, json; import cli; from src import variables_entrada as ve\n"
        "print(json.dumps({'weasyprint': 'weasyprint' in sys.modules,\n"
        "  'scipy': 'scipy.optimize' in sys.modules,\n"
        "  'censo': 'VARIABLES' in vars(ve)}))\n"
        "ve.VARIABLES; print(json.dumps({'censo_despues': 'VARIABLES' in vars(ve),\n"
        "  'n': len(ve.VARIABLES)}))")
    hecho = subprocess.run([sys.executable, "-c", programa], cwd=RAIZ,
                           capture_output=True, text=True, timeout=120)
    assert hecho.returncode == 0, hecho.stderr[-2000:]
    antes, despues = (json.loads(l) for l in hecho.stdout.strip().splitlines())
    assert antes == {"weasyprint": False, "scipy": False, "censo": False}, antes
    assert despues["censo_despues"] is True
    from src import variables_entrada as ve
    assert despues["n"] == len(ve.VARIABLES) == len(ca.CRITERIOS) + len(ve._EXTERNOS) \
        + len(__import__("src.datos_sitio", fromlist=["DATOS_SITIO"]).DATOS_SITIO) \
        + len(__import__("src.modulos.M0_carga", fromlist=["COLUMNAS"]).COLUMNAS)


def test_pc10_el_censo_perezoso_sigue_pasando_su_guardia_al_construirse():
    """
    La coherencia del censo (`_coherencia_del_censo`) corria al importar;
    perezoso, tiene que correr al construir, y una variable sin modo tiene
    que seguir cayendo. Se comprueba leyendo el AST: `_construir` (o quien
    arme el diccionario) llama a la guardia antes de devolverlo.
    """
    from src import variables_entrada as ve
    arbol = _arbol(RAIZ / "src" / "variables_entrada.py")
    assert _funcion(arbol, "__getattr__"), "sin __getattr__ de modulo no hay pereza"
    llamadas = {ast.unparse(n.func) for n in ast.walk(arbol)
                if isinstance(n, ast.Call)}
    assert "_coherencia_del_censo" in llamadas
    # Y ninguna llamada a nivel de modulo: eso es lo que costaba 140 ms.
    nivel_modulo = {ast.unparse(n.value.func) for n in arbol.body
                    if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)}
    assert "_coherencia_del_censo" not in nivel_modulo
    assert "_construir" not in nivel_modulo
    assert ve.variable("Q_m3s").clave == "Q_m3s"


def test_pc10_scipy_se_importa_en_el_punto_de_uso():
    for modulo in ("M3_hidraulica", "M4_control"):
        arbol = _arbol(RAIZ / "src" / "modulos" / f"{modulo}.py")
        de_nivel_modulo = [n for n in arbol.body if isinstance(n, ast.ImportFrom)
                           and (n.module or "").startswith("scipy")]
        assert not de_nivel_modulo, f"{modulo}: scipy sigue en el import de modulo"
        dentro = [n for n in ast.walk(arbol) if isinstance(n, ast.ImportFrom)
                  and (n.module or "").startswith("scipy")]
        assert dentro, f"{modulo}: brentq ya no se importa de scipy"


def test_pc10_weasyprint_es_perezoso_y_la_sonda_conserva_el_diagnostico(monkeypatch):
    """
    `weasyprint_disponible()` es la sonda: carga UNA vez, y deja el mismo
    diagnostico que antes --- `WEASYPRINT_AUSENTE` distingue «no esta»
    (ImportError) de «esta y no carga» (cualquier otra excepcion) y
    `FALLO_WEASYPRINT` conserva el texto ---. `WeasyHTML` sigue siendo el
    simbolo que decide la via.
    """
    arbol = _arbol(RAIZ / "src" / "modulos" / "M11_reporte.py")
    # El unico import de weasyprint del modulo vive DENTRO de
    # `_importar_weasyprint`: ni al nivel del modulo ni dentro de un `try`
    # de nivel de modulo (que es como estaba, y que un filtro sobre
    # `arbol.body` no veria).
    dentro_de_funciones = {id(x) for f in ast.walk(arbol)
                           if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))
                           for x in ast.walk(f)}
    fuera = [n for n in ast.walk(arbol) if isinstance(n, (ast.ImportFrom, ast.Import))
             and "weasyprint" in ast.unparse(n) and id(n) not in dentro_de_funciones]
    assert not fuera, "weasyprint sigue importandose al cargar M11"
    sonda = _funcion(arbol, "weasyprint_disponible")
    intentos = [n for n in ast.walk(sonda) if isinstance(n, ast.Try)
                and any(isinstance(h.type, ast.Name) and h.type.id == "Exception"
                        for h in n.handlers)
                and _llamadas_a(n, "_importar_weasyprint")]
    assert intentos, "la sonda perdio el `except Exception` que separa ImportError de OSError"
    assert any(isinstance(x, ast.ImportFrom) and x.module == "weasyprint"
               for x in ast.walk(_funcion(arbol, "_importar_weasyprint")))

    # Comportamiento: los dos diagnosticos, inyectando el importador.
    def _no_esta():
        raise ImportError("No module named 'weasyprint'")

    def _no_carga():
        raise OSError("cannot load library 'gobject-2.0-0'")

    # Los CUATRO nombres que la sonda escribe se parchean, para que el
    # teardown deje el diagnostico del proceso como estaba.
    monkeypatch.setattr(M11, "WeasyHTML", None)
    monkeypatch.setattr(M11, "FALLO_WEASYPRINT", M11.FALLO_WEASYPRINT)
    monkeypatch.setattr(M11, "WEASYPRINT_AUSENTE", M11.WEASYPRINT_AUSENTE)
    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", False)
    monkeypatch.setattr(M11, "_importar_weasyprint", _no_esta)
    assert M11.weasyprint_disponible() is False
    assert M11.WEASYPRINT_AUSENTE is True
    assert "no esta instalado" in M11._por_que_no_hay_weasyprint()

    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", False)
    monkeypatch.setattr(M11, "_importar_weasyprint", _no_carga)
    assert M11.weasyprint_disponible() is False
    assert M11.WEASYPRINT_AUSENTE is False
    assert "gobject" in M11.FALLO_WEASYPRINT
    assert "SI esta instalado" in M11._por_que_no_hay_weasyprint()

    class _Falso:
        pass

    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", False)
    monkeypatch.setattr(M11, "_importar_weasyprint", lambda: _Falso)
    assert M11.weasyprint_disponible() is True
    assert M11.WeasyHTML is _Falso
    # Una segunda sonda no vuelve a importar: es UNA vez por proceso.
    monkeypatch.setattr(M11, "_importar_weasyprint", _no_esta)
    assert M11.weasyprint_disponible() is True


# ===========================================================================
# PC-11 - el PDF fuera del hilo de Tk, por subproceso
# ===========================================================================

CLAVE_DECLARADA = "phi_relleno_trasdos"      # un [A] de Fase 9 con ventana


def _sesion_de_prueba(csv: Path, alcance: str, proyecto: str = "obra EXT-8"):
    """Una sesion como la que `gui/app.py` guarda, con un criterio declarado."""
    return {
        "formato_version": ses.FORMATO_SESION,
        "app_version": "1.0",
        "proyecto": proyecto,
        "csv": str(csv),
        "datos_externos": str(EXTERNOS_AMPLIADOS),
        "externos": {"luz_m": "2,75", "TW_m": "", "longitud_m": "",
                     "l_hidraulico": "", "categoria_tr": ""},
        "alcance": alcance,
        "criterios": dec.estado_de_sesion(),
    }


def test_pc11_el_esquema_de_sesion_vive_fuera_de_la_gui_y_la_gui_lo_reexporta():
    """
    La CLI tiene que poder leer la sesion serializada sin importar Tk, y la
    GUI no puede tener un segundo esquema: `src/sesion.py` es el unico y
    `gui.app.errores_de_sesion` es el mismo objeto.
    """
    from tests.apoyo import doble_tkinter
    app = doble_tkinter.gui_app()
    assert app.errores_de_sesion is ses.errores_de_sesion
    assert app.FORMATO_SESION == ses.FORMATO_SESION
    assert app.ExpedienteApp.CLAVE_EXTERNA_DE_CAMPO is ses.CLAVE_EXTERNA_DE_CAMPO
    assert ses.errores_de_sesion({"externos": None})
    assert ses.errores_de_sesion({}) == []
    assert ses.banderas_de_externos({"luz_m": "1,5", "l_hidraulico": "",
                                     "categoria_tr": "quebrada_menor"}) == {
        "luz_m": "1.5", "TW_m": None, "longitud_m": None,
        "L_hidraulico_m": None, "categoria_tr": "quebrada_menor"}


def test_pc11_la_cli_restaura_la_sesion_serializada_con_sus_procedencias(tmp_path):
    """
    `--sesion` repone proyecto, CSV, datos externos, banderas, alcance y los
    criterios CON su procedencia, por `declaracion.restaurar_sesion` (el
    mismo camino con guardia que la GUI). Y `--declarar` sigue componiendo
    encima.
    """
    with con_valor(CLAVE_DECLARADA, 33.0, motivo="valor de prueba dentro de ventana"):
        dec.declarar_valor(CLAVE_DECLARADA, 33.0, nota="declarado para la prueba EXT-8")
        sesion = _sesion_de_prueba(CSV_EJEMPLO, cli.ALCANCE_PERFIL)
    ruta = tmp_path / "sesion.json"
    ruta.write_text(json.dumps(sesion), encoding="utf-8")

    cargada = cli.cargar_sesion_serializada(ruta)
    assert cargada.proyecto == "obra EXT-8"
    assert cargada.csv == CSV_EJEMPLO
    assert cargada.datos_externos == EXTERNOS_AMPLIADOS
    assert cargada.alcance == cli.ALCANCE_PERFIL
    assert cargada.banderas["luz_m"] == "2.75"
    assert cargada.banderas["TW_m"] is None

    ca.limpiar_valores_dinamicos()
    dec.limpiar()
    try:
        resultado = cli.aplicar_sesion_serializada(cargada)
        assert CLAVE_DECLARADA in resultado.restaurados
        assert ca.valores_dinamicos()[CLAVE_DECLARADA] == pytest.approx(33.0, rel=REL_TRANSPORTE)
        assert dec.procedencia_de(CLAVE_DECLARADA) is not None
        assert "EXT-8" in dec.procedencia_de(CLAVE_DECLARADA).nota
    finally:
        ca.limpiar_valores_dinamicos()
        dec.limpiar()


def test_pc11_la_cli_rechaza_una_sesion_deformada_sin_traza(tmp_path, capsys):
    ruta = tmp_path / "sesion.json"
    ruta.write_text(json.dumps({"externos": None, "csv": "x.csv"}), encoding="utf-8")
    codigo = cli.main(["--sesion", str(ruta), "--json", str(tmp_path / "a.json")])
    assert codigo == 2
    err = capsys.readouterr().err
    assert "sesion" in err.lower()
    assert "Traceback" not in err
    # Y sin CSV ni sesion, el parser lo dice.
    with pytest.raises(SystemExit):
        cli.main(["--json", str(tmp_path / "b.json")])


def test_pc11_la_cli_informa_progreso_por_lineas_de_stdout(tmp_path, capsys, monkeypatch):
    """
    Con `--progreso`, cada punto de la memoria y cada etapa de la
    exportacion dejan una linea `progreso: hecho/total etapa` en stdout, que
    es lo que la GUI lee del proceso hijo. Sin la bandera no aparecen: la
    linea base de la CLI no cambia.
    """
    monkeypatch.setattr(M11, "WeasyHTML", None)
    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", True)
    destino = tmp_path / "memoria.pdf"
    cli.main([str(CSV_EJEMPLO), "--luz", "2.0", "--json", str(tmp_path / "a.json"),
              "--pdf", str(destino), "--progreso"])
    salida = capsys.readouterr().out
    lineas = [l for l in salida.splitlines() if l.startswith(cli.PREFIJO_PROGRESO)]
    assert lineas, "no hubo ninguna linea de progreso"
    n_puntos = len(CSV_EJEMPLO.read_text(encoding="utf-8").splitlines()) - 1
    por_punto = [l for l in lineas if M11.ETAPA_PUNTO in l]
    assert len(por_punto) == n_puntos
    assert por_punto[-1].split()[1] == f"{n_puntos}/{n_puntos}"
    # Forzada la via del navegador arriba: la etapa terminal es la del HTML
    # para imprimir; con weasyprint seria `ETAPA_PDF` (lo fija el test del
    # subproceso).
    assert any(M11.ETAPA_NAVEGADOR in l for l in lineas)
    assert not any(M11.ETAPA_PDF in l for l in lineas)

    cli.main([str(CSV_EJEMPLO), "--luz", "2.0", "--json", str(tmp_path / "b.json"),
              "--html", str(tmp_path / "m.html")])
    assert cli.PREFIJO_PROGRESO not in capsys.readouterr().out


def _esperar(proceso, limite_s: float = 300.0):
    inicio = time.monotonic()
    while True:
        estado = proceso.sondear()
        if estado.terminal:
            return estado
        assert time.monotonic() - inicio < limite_s, "el subproceso no termino a tiempo"
        time.sleep(0.05)


@pytest.fixture
def exportacion():
    import gui.exportacion_pdf as ex
    return ex


def test_pc11_el_proceso_pdf_produce_el_pdf_y_reporta_progreso(tmp_path, exportacion):
    """
    `ProcesoPdf` corre `cli.py --sesion ... --pdf ... --progreso` en un
    subproceso, lee su progreso de las lineas de stdout y termina en un
    estado terminal claro. Sin Tk: el bucle `after` de la ventana solo
    llama a `sondear()`.
    """
    if not M11.weasyprint_disponible():
        pytest.skip("weasyprint no esta operativo en este interprete")
    csv = _csv_de_un_punto(tmp_path)
    sesion = _sesion_de_prueba(csv, cli.ALCANCE_EXPEDIENTE)
    destino = tmp_path / "salida" / "memoria.pdf"
    proceso = exportacion.ProcesoPdf(
        sesion=sesion, destino=destino, plantilla=cli.plantilla_por_alcance(
            cli.ALCANCE_EXPEDIENTE), directorio_trabajo=tmp_path / "trabajo",
        interprete=sys.executable, raiz=RAIZ)
    assert proceso.estado.terminal is False
    proceso.iniciar()
    estado = _esperar(proceso)
    assert estado is exportacion.EstadoPdf.TERMINADO, proceso.detalle
    assert destino.is_file() and destino.stat().st_size > 0
    assert destino.read_bytes().startswith(b"%PDF")
    assert proceso.progreso_visto, "no llego ninguna linea de progreso"
    assert any(M11.ETAPA_PDF in p for p in proceso.progreso_visto)
    assert str(destino) in proceso.detalle
    # El JSON de la corrida hija no pisa el `<csv>.informe.json` del usuario.
    assert not csv.with_suffix(".informe.json").exists()
    # El comando que lanzo es el contrato: plantilla explicita, JSON aparte.
    assert "--plantilla" in proceso.comando and "--json" in proceso.comando
    assert "--progreso" in proceso.comando and "--sesion" in proceso.comando


def test_pc11_el_pdf_del_subproceso_describe_la_misma_corrida(tmp_path, exportacion):
    """
    Equivalencia medida: el JSON que el hijo escribe es el de la corrida de
    la ventana --- mismas entradas, mismos resultados, mismo contexto ---
    salvo la marca de tiempo. Es lo que hace que «exportar en otro proceso»
    no sea «exportar otra cosa».
    """
    if not M11.weasyprint_disponible():
        pytest.skip("weasyprint no esta operativo en este interprete")
    csv = _csv_de_un_punto(tmp_path)
    sesion = _sesion_de_prueba(csv, cli.ALCANCE_PERFIL)
    externos = cli.cargar_datos_externos(EXTERNOS_AMPLIADOS,
                                         ses.banderas_de_externos(sesion["externos"]))
    # LAS MISMAS ENTRADAS POR LAS DOS PUERTAS: la corrida propia se hace con
    # la sesion repuesta desde su forma serializada (JSON ida y vuelta), que
    # es exactamente lo que el hijo recibe. No es un tecnicismo: un
    # criterio declarado como dict con claves ENTERAS (el espesor de pared
    # por diametro que `conftest` declara) vuelve del JSON con claves de
    # texto, y una sesion guardada y cargada ya lo hacia antes de EXT-8
    # (ficha EXT-8-03 de decisiones_diferidas.md). La equivalencia que se
    # afirma es «misma sesion serializada -> misma corrida», que es la que
    # el PDF necesita.
    estado_original = dec.estado_de_sesion()
    ida_y_vuelta = json.loads(json.dumps(sesion, ensure_ascii=False))
    try:
        dec.restaurar_sesion(ida_y_vuelta["criterios"], sustituir=True)
        propio = cli.informe_json(cli.correr(csv, externos, alcance=cli.ALCANCE_PERFIL))
    finally:
        dec.restaurar_sesion(estado_original, sustituir=True)
    proceso = exportacion.ProcesoPdf(
        sesion=sesion, destino=tmp_path / "m.pdf",
        plantilla=cli.plantilla_por_alcance(cli.ALCANCE_PERFIL),
        directorio_trabajo=tmp_path / "trabajo", interprete=sys.executable,
        raiz=RAIZ)
    proceso.iniciar()
    assert _esperar(proceso) is exportacion.EstadoPdf.TERMINADO, proceso.detalle
    ajeno = json.loads(proceso.ruta_json.read_text(encoding="utf-8"))
    # Los dos como JSON (el propio pasa por `json.dumps` como lo haria al
    # escribirse): las claves enteras de los dicts se vuelven texto al
    # serializar, y comparar el objeto vivo con el leido seria comparar dos
    # representaciones y no dos corridas.
    propio_json = json.loads(json.dumps(propio, ensure_ascii=False, allow_nan=False))
    assert exportacion.sin_marca_de_tiempo(propio_json) == exportacion.sin_marca_de_tiempo(ajeno)
    assert exportacion.sin_marca_de_tiempo(propio_json) != propio_json


def test_pc11_cancelar_termina_el_proceso_y_no_deja_pdf(tmp_path, exportacion):
    csv = _csv_de_un_punto(tmp_path)
    proceso = exportacion.ProcesoPdf(
        sesion=_sesion_de_prueba(csv, cli.ALCANCE_PERFIL),
        destino=tmp_path / "m.pdf",
        plantilla=cli.plantilla_por_alcance(cli.ALCANCE_PERFIL),
        directorio_trabajo=tmp_path / "trabajo", interprete=sys.executable,
        raiz=RAIZ)
    proceso.iniciar()
    proceso.cancelar()
    estado = _esperar(proceso, limite_s=60)
    assert estado is exportacion.EstadoPdf.CANCELADO
    assert not (tmp_path / "m.pdf").exists()
    assert "cancel" in proceso.detalle.lower()


def test_pc11_un_fallo_del_hijo_es_un_estado_terminal_con_su_motivo(tmp_path, exportacion):
    proceso = exportacion.ProcesoPdf(
        sesion=_sesion_de_prueba(tmp_path / "no_existe.csv", cli.ALCANCE_PERFIL),
        destino=tmp_path / "m.pdf",
        plantilla=cli.plantilla_por_alcance(cli.ALCANCE_PERFIL),
        directorio_trabajo=tmp_path / "trabajo", interprete=sys.executable,
        raiz=RAIZ)
    proceso.iniciar()
    estado = _esperar(proceso, limite_s=120)
    assert estado is exportacion.EstadoPdf.FALLIDO
    assert "no_existe.csv" in proceso.detalle or "No se pudo leer" in proceso.detalle
    assert not (tmp_path / "m.pdf").exists()


def test_pc11_la_sesion_del_hijo_es_la_de_la_corrida_y_no_los_campos_vivos(
        informe_expediente, exportacion):
    """
    Auditoria adversarial de EXT-8: la sesion se armaba con los campos vivos
    de la ventana, y cambiar el radio o la luz despues de correr no invalida
    el informe. La sesion del hijo sale del `ContextoCorrida` congelado y de
    las entradas fotografiadas al correr: cambiar los campos despues no la
    mueve.
    """
    with con_valor(CLAVE_DECLARADA, 33.0, motivo="valor de prueba dentro de ventana"):
        dec.declarar_valor(CLAVE_DECLARADA, 33.0, nota="declarado para EXT-8")
        externos = cli.cargar_datos_externos(
            EXTERNOS_AMPLIADOS, {"luz_m": 2.75, "TW_m": None, "longitud_m": None,
                                 "L_hidraulico_m": None, "categoria_tr": None})
        informe = cli.correr(CSV_EJEMPLO, externos, alcance=cli.ALCANCE_PERFIL)
        entradas = {"csv": str(CSV_EJEMPLO), "datos_externos": str(EXTERNOS_AMPLIADOS),
                    "externos": {"luz_m": "2,75", "TW_m": "", "longitud_m": "",
                                 "l_hidraulico": "", "categoria_tr": ""},
                    "alcance": cli.ALCANCE_PERFIL}
        sesion = exportacion.sesion_de_la_corrida(
            informe, proyecto="obra", formato_version=ses.FORMATO_SESION,
            app_version="1.0", **entradas)
    # Ya fuera del `con_valor`: el estado vivo cambio y la sesion no.
    assert sesion["alcance"] == cli.ALCANCE_PERFIL
    assert sesion["externos"]["luz_m"] == "2,75"
    assert sesion["criterios"]["valores"][CLAVE_DECLARADA] == pytest.approx(
        33.0, rel=REL_TRANSPORTE)
    assert "EXT-8" in sesion["criterios"]["procedencias"][CLAVE_DECLARADA]["nota"]
    assert set(sesion["criterios"]["valores"]) == set(
        informe.contexto.declarados_en_caliente) | set(informe.contexto.pisados_en_caliente)
    assert not ses.errores_de_sesion(json.loads(json.dumps(sesion)))
    # Y la ventana la arma asi: desde la corrida, no desde los StringVar.
    lanzar = ast.unparse(_funcion(_arbol(GUI), "_lanzar_pdf"))
    assert "sesion_de_la_corrida" in lanzar and "entradas_de_la_corrida" in lanzar
    assert "_datos_de_sesion" not in lanzar
    ejecutar = ast.unparse(_funcion(_arbol(GUI), "ejecutar_pipeline"))
    assert "entradas_de_la_corrida" in ejecutar


def test_pc11_un_hijo_que_no_arranca_es_terminal_y_no_deja_la_ventana_atascada(
        tmp_path, exportacion):
    """Auditoria adversarial de EXT-8: `iniciar()` fallido dejaba SIN_INICIAR."""
    proceso = exportacion.ProcesoPdf(
        sesion=_sesion_de_prueba(CSV_EJEMPLO, cli.ALCANCE_PERFIL),
        destino=tmp_path / "m.pdf", plantilla=cli.plantilla_por_alcance(cli.ALCANCE_PERFIL),
        directorio_trabajo=tmp_path / "trabajo",
        interprete=str(tmp_path / "interprete_que_no_existe"), raiz=RAIZ)
    proceso.iniciar()
    assert proceso.estado is exportacion.EstadoPdf.FALLIDO
    assert proceso.estado.terminal and "No se pudo lanzar" in proceso.detalle
    proceso.limpiar()
    assert not (tmp_path / "trabajo").exists()
    lanzar = ast.unparse(_funcion(_arbol(GUI), "_lanzar_pdf"))
    assert "estado.terminal" in lanzar, "la ventana no comprueba que el hijo arranco"


def test_pc11_la_bandera_escrita_gana_a_la_sesion_tambien_en_proyecto(tmp_path):
    ruta = tmp_path / "s.json"
    ruta.write_text(json.dumps(_sesion_de_prueba(CSV_EJEMPLO, cli.ALCANCE_PERFIL)),
                    encoding="utf-8")
    assert cli._parser().allow_abbrev is False
    with pytest.raises(SystemExit):
        cli._parser().parse_args(["--alc", "perfil", "x.csv"])
    assert cli._bandera_explicita(["--proyecto", ""], "--proyecto")
    assert cli._bandera_explicita(["--alcance=perfil"], "--alcance")
    assert not cli._bandera_explicita(["--sesion", "s"], "--alcance")


def test_pc12_exportar_html_no_deja_un_archivo_truncado(informe_expediente, tmp_path,
                                                         monkeypatch):
    """Auditoria adversarial de EXT-8: un fallo a mitad dejaba el HTML a medias."""
    def _revienta(_punto):
        raise ValueError("fallo simulado a mitad de la memoria")
    monkeypatch.setattr(M11, "memoria_de_punto", _revienta)
    destino = tmp_path / "m.html"
    with pytest.raises(ValueError, match="simulado"):
        M11.exportar_html(informe_expediente, destino, proyecto="P")
    assert not destino.exists()
    assert not list(tmp_path.iterdir())


def test_pc11_la_gui_exporta_el_pdf_sin_bloquear_el_hilo_de_tk():
    """
    Leido del arbol de `gui/app.py`: el boton llama a `ProcesoPdf`, sondea
    con `after` (nunca `wait()` ni `communicate()` ni un hilo), apaga el
    boton con motivo, ofrece cancelar, y termina en un estado que se lee en
    un rotulo. La via del navegador sigue pasando por `cli.exportar_pdf`
    con `ruta_plantilla` (el contrato que `test_gui_contrato` fija).
    """
    arbol = _arbol(GUI)
    exportar = _funcion(arbol, "exportar_pdf")
    texto = ast.unparse(exportar)
    assert "ProcesoPdf" in texto or "_lanzar_pdf" in texto
    fuente = GUI.read_text(encoding="utf-8-sig")
    assert "threading" not in fuente, "el PDF no sale por hilo: sale por subproceso"
    sondeo = _funcion(arbol, "_sondear_pdf")
    assert _llamadas_a(sondeo, "after"), "el sondeo no se reprograma con `after`"
    for prohibido in (".wait(", ".communicate("):
        assert prohibido not in fuente
    lanzar = ast.unparse(_funcion(arbol, "_lanzar_pdf"))
    assert "MOTIVO_EXPORTANDO_PDF" in lanzar and "deshabilitar" in lanzar
    # Por AST y no por texto (PC-21): los dos widgets son ATRIBUTOS que la
    # ventana asigna, no menciones.
    atributos = {n.attr for n in ast.walk(arbol) if isinstance(n, ast.Attribute)}
    assert {"btn_cancelar_pdf", "lbl_estado_pdf"} <= atributos
    # El contrato viejo sigue: la via del navegador con su plantilla.
    llamadas = _llamadas_a(exportar, "cli.exportar_pdf") + \
        _llamadas_a(_funcion(arbol, "_exportar_pdf_por_navegador"), "cli.exportar_pdf")
    assert llamadas
    assert all("ruta_plantilla" in {kw.arg for kw in l.keywords} for l in llamadas)


def test_pc11_la_ayuda_del_boton_dice_el_limite_medido_y_ofrece_el_navegador():
    """
    El limite medido (PC-11) esta en la ayuda del boton ANTES de pulsar, y por
    encima de `UMBRAL_PUNTOS_PDF` la ventana ofrece la via del navegador. El
    umbral se declara con su medida al lado.
    """
    from tests.apoyo import doble_tkinter
    app = doble_tkinter.gui_app()
    import gui.exportacion_pdf as ex
    ayuda = app.ExpedienteApp._ayuda_del_pdf(_AppMinima())
    assert str(ex.UMBRAL_PUNTOS_PDF) in ayuda
    assert "navegador" in ayuda.lower()
    assert ex.LIMITE_MEDIDO_PDF in ayuda
    assert re.search(r"\d+ s", ex.LIMITE_MEDIDO_PDF) and "GB" in ex.LIMITE_MEDIDO_PDF
    arbol = _arbol(GUI)
    exportar = ast.unparse(_funcion(arbol, "exportar_pdf"))
    assert "UMBRAL_PUNTOS_PDF" in exportar
    assert "askyesno" in exportar or "_preguntar_via" in exportar


class _AppMinima:
    """Lo minimo que `_ayuda_del_pdf` lee de la ventana."""
    informe = None


def test_pc11_el_contrato_weasyhtml_sigue_decidiendo_la_via(tmp_path, monkeypatch,
                                                            informe_expediente):
    """Los dos tests de `test_M11_reporte` parchean `WeasyHTML`: se conserva."""
    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", True)
    monkeypatch.setattr(M11, "WeasyHTML", None)
    salida = M11.exportar_pdf(informe_expediente, tmp_path / "m.pdf",
                              abrir_navegador=False, proyecto="P")
    assert salida.via == M11.VIA_NAVEGADOR

    class _Falso:
        def __init__(self, *, string, base_url):
            self.string = string

        def write_pdf(self, ruta):
            Path(ruta).write_bytes(b"%PDF-1.7")

    monkeypatch.setattr(M11, "WeasyHTML", _Falso)
    salida = M11.exportar_pdf(informe_expediente, tmp_path / "m.pdf", proyecto="P")
    assert salida.via == M11.VIA_WEASYPRINT
    # Y la via del navegador se puede FORZAR con weasyprint operativo: es la
    # que la ventana ofrece por encima del umbral.
    salida = M11.exportar_pdf(informe_expediente, tmp_path / "n.pdf", proyecto="P",
                              abrir_navegador=False, forzar_navegador=True)
    assert salida.via == M11.VIA_NAVEGADOR
    assert (tmp_path / "n.html").is_file()


# ===========================================================================
# PC-12 - la memoria deduplicada: F2.LUZ, punteros, anexo, streaming
# ===========================================================================

_H5 = re.compile(r'<div class="paso(?: nota)?"><h5>(?:<code>(.*?)</code> &mdash; )?(.*?)</h5>')


def test_pc12_el_paso_2_1_se_imprime_una_vez_por_punto(informe_expediente):
    """
    F2.LUZ se renderizaba en la traza de clasificacion Y en el desarrollo de
    verificaciones: x2 por punto. Una vez, y la traza de la GUI cuenta lo
    mismo (el test de `test_traza_punto` sigue fijando esa igualdad).
    """
    for punto in informe_expediente.puntos:
        html = M11.memoria_de_punto(punto)
        # Un paso es (codigo, titulo): dos pasos distintos pueden compartir
        # codigo (4.1 es el area mojada y tambien el tirante normal).
        titulares = _H5.findall(html)
        assert len(titulares) == len(set(titulares)), (
            f"{punto.punto.id}: pasos repetidos "
            f"{sorted(t for t in titulares if titulares.count(t) > 1)}")
        if punto.clasificacion is not None and \
                getattr(punto.clasificacion.verificacion_luz, "paso", None) is not None:
            luz = punto.clasificacion.verificacion_luz.paso
            assert [c for c, _ in titulares].count(luz.codigo) == 1


def test_pc12_desarrollo_de_verificaciones_es_una_sola_seleccion_compartida():
    """La GUI (traza_punto) y M11 leen la MISMA seleccion, sin el paso repetido."""
    from src import traza_punto
    fuente = ast.unparse(_arbol(RAIZ / "src" / "traza_punto.py"))
    assert "desarrollo_de_verificaciones" in fuente
    assert callable(M11.desarrollo_de_verificaciones)
    assert callable(getattr(traza_punto, "traza_del_punto"))


def test_pc12_hay_un_anexo_con_ancla_por_cita_id_y_los_pasos_enlazan(memoria_expediente,
                                                                    informe_expediente):
    """
    El anexo unico: cada cita que algun paso entrecomilla aparece UNA vez con
    `id="cita-<slug>"`, y los pasos la enlazan con `href="#cita-<slug>"` en
    vez de transcribirla. Lo mismo para fundamentos, umbrales y
    discrepancias. Los textos siguen saliendo del registro.
    """
    memoria = memoria_expediente
    assert M11.MARCADOR_ANEXO in M11.MARCADORES
    for plantilla in PLANTILLAS:
        assert f"%%{M11.MARCADOR_ANEXO}" in plantilla.read_text(encoding="utf-8")
    pasos = M11.pasos_impresos(informe_expediente)
    assert set(pasos) <= set(M11.pasos_del_informe(informe_expediente))
    citas = {c for p in pasos for c in p.citas_textuales}
    assert citas
    for cita_id in citas:
        ancla = M11.ancla_de_cita(cita_id)
        assert memoria.count(f'id="{ancla}"') == 1, cita_id
        assert f'href="#{ancla}"' in memoria, cita_id
    fundamentos = {p.fundamento_id for p in pasos if p.fundamento_id}
    for fid in fundamentos:
        ancla = M11.ancla_de_fundamento(fid)
        assert memoria.count(f'id="{ancla}"') == 1, fid
        assert f'href="#{ancla}"' in memoria, fid
    # Los textos literales del anexo son del registro, verificados.
    reg = _registro.construir()
    literales = {" ".join(t.split()) for t in reg.textos_literales()}
    anexo = M11.anexo_referencias(informe_expediente)
    import html as _html
    for bruto in re.findall(r"&laquo;(.*?)&raquo;", anexo, re.S):
        texto = " ".join(_html.unescape(bruto).split())
        assert any(texto == t or texto in t for t in literales), texto[:100]


def test_pc12_todo_enlace_interno_de_la_memoria_tiene_destino(memoria_expediente):
    """
    Cada `href="#..."` de la memoria entera apunta a un `id` que existe UNA
    vez. Lo encontro weasyprint al paginar (`No anchor #cita-... for internal
    URI reference`): el anexo enlazaba las citas de cada fundamento y solo
    transcribia las de los pasos.
    """
    memoria = memoria_expediente
    ids = re.findall(r'\bid="([^"]+)"', memoria)
    repetidos = sorted({i for i in ids if ids.count(i) > 1})
    assert not repetidos, f"ids repetidos: {repetidos}"
    destinos = set(ids)
    rotos = sorted({h for h in re.findall(r'href="#([^"]+)"', memoria) if h not in destinos})
    assert not rotos, f"enlaces internos sin destino: {rotos}"


def test_pc12_los_punteros_se_deduplican(memoria_expediente):
    """
    «El detalle esta en el bloque de discrepancias de esta memoria» x90 y
    «cuya ficha esta en el bloque 3 de esta memoria» x9 eran punteros en
    prosa repetidos en cada paso: pasan a ser UN enlace por paso, y la frase
    no se repite.
    """
    memoria = memoria_expediente
    assert "esta en el bloque de discrepancias de esta memoria" not in memoria
    assert "cuya ficha esta en el bloque 3 de esta memoria" not in memoria
    for dis in re.findall(r'href="#(disc-[^"]+)"', memoria):
        assert memoria.count(f'id="{dis}"') == 1, dis
    # Y un umbral en un paso ya no lleva su caracter y su aplicacion
    # transcritos: los enlaza.
    assert 'href="#umbral-' in memoria


def test_pc12_la_memoria_se_construye_por_partes_y_el_html_se_escribe_en_streaming(
        informe_expediente, tmp_path):
    partes = list(M11.memoria_html_por_partes(informe_expediente, proyecto="EXT-8"))
    assert len(partes) > len(informe_expediente.puntos)
    assert "".join(partes) == M11.memoria_html(informe_expediente, proyecto="EXT-8")
    arbol = _arbol(RAIZ / "src" / "modulos" / "M11_reporte.py")
    exportar = ast.unparse(_funcion(arbol, "exportar_html"))
    assert "memoria_html_por_partes" in exportar
    assert "memoria_html(" not in exportar.replace("memoria_html_por_partes", "")
    destino = tmp_path / "m.html"
    M11.exportar_html(informe_expediente, destino, proyecto="EXT-8")
    assert destino.read_text(encoding="utf-8") == "".join(partes)


def test_pc12_el_progreso_por_punto_se_emite_durante_la_construccion(informe_expediente):
    vistos = []
    M11.memoria_html(informe_expediente, proyecto="P",
                     progreso=lambda etapa, hecho, total: vistos.append((etapa, hecho, total)))
    por_punto = [v for v in vistos if v[0] == M11.ETAPA_PUNTO]
    n = len(informe_expediente.puntos)
    assert [h for _, h, _ in por_punto] == list(range(1, n + 1))
    assert all(t == n for _, _, t in por_punto)


def _memoria_de(csv: Path, n_lineas: int, tmp_path: Path, alcance: str) -> str:
    lineas = CSV_EJEMPLO.read_text(encoding="utf-8").splitlines()
    csv.write_text("\n".join(lineas[:n_lineas + 1]) + "\n", encoding="utf-8")
    externos = cli.cargar_datos_externos(
        EXTERNOS_AMPLIADOS, {"luz_m": 2.75, "TW_m": None, "longitud_m": None,
                             "L_hidraulico_m": None, "categoria_tr": None})
    informe = cli.correr(csv, externos, alcance=alcance)
    return M11.memoria_html(informe, proyecto="medida",
                            ruta_plantilla=cli.plantilla_por_alcance(alcance))


def test_pc12_el_coste_marginal_por_punto_cabe_en_el_techo_medido(tmp_path):
    """
    El coste MARGINAL por punto (memoria de 4 puntos menos memoria de 1,
    entre 3), medido a alcance expediente con las entradas ampliadas. Se fija
    aqui despues de medir (ver `KB_POR_PUNTO_MAX`).
    """
    uno = _memoria_de(tmp_path / "uno.csv", 1, tmp_path, cli.ALCANCE_EXPEDIENTE)
    cuatro = _memoria_de(tmp_path / "cuatro.csv", 4, tmp_path, cli.ALCANCE_EXPEDIENTE)
    marginal_kb = (len(cuatro.encode("utf-8")) - len(uno.encode("utf-8"))) / 3 / 1024
    assert marginal_kb < KB_POR_PUNTO_MAX, f"{marginal_kb:.1f} KB por punto"


@pytest.mark.pdf
def test_pc12_las_paginas_por_punto_caben_en_el_techo_medido(tmp_path):
    """
    Paginas marginales por punto del PDF real (weasyprint), contadas con
    PyMuPDF. Se salta sin cualquiera de los dos.
    """
    fitz = pytest.importorskip("fitz")
    if not M11.weasyprint_disponible():
        pytest.skip("weasyprint no esta operativo en este interprete")
    paginas = {}
    for n in (1, 4):
        html = _memoria_de(tmp_path / f"{n}.csv", n, tmp_path, cli.ALCANCE_EXPEDIENTE)
        destino = tmp_path / f"{n}.pdf"
        M11.WeasyHTML(string=html, base_url=str(M11.DIR_PLANTILLAS)).write_pdf(str(destino))
        with fitz.open(str(destino)) as doc:
            paginas[n] = doc.page_count
    marginal = (paginas[4] - paginas[1]) / 3
    assert marginal < PAGINAS_POR_PUNTO_MAX, f"{marginal:.1f} paginas por punto"


# ===========================================================================
# PC-17 - accesibilidad minima
# ===========================================================================

def test_pc17_la_rueda_normaliza_windows_x11_y_macos():
    from tests.apoyo import doble_tkinter
    comp = doble_tkinter.gui_componentes()
    # Windows: delta en multiplos de 120, hacia arriba positivo.
    assert comp.unidades_de_rueda(num=0, delta=120) == -1
    assert comp.unidades_de_rueda(num=0, delta=-240) == 2
    # macOS: deltas pequenos (1, 3...), nunca cero unidades.
    assert comp.unidades_de_rueda(num=0, delta=1) == -1
    assert comp.unidades_de_rueda(num=0, delta=-3) == 1
    # X11: botones 4 y 5, sin delta.
    assert comp.unidades_de_rueda(num=4, delta=0) == -1
    assert comp.unidades_de_rueda(num=5, delta=0) == 1
    arbol = _arbol(COMPONENTES)
    marco = _clase(arbol, "MarcoScroll")
    cadenas = _cadenas(marco)
    assert {"<Button-4>", "<Button-5>", "<MouseWheel>"} <= cadenas


def test_pc17_el_boton_apagado_tiene_un_rotulo_visible_ademas_del_tooltip():
    arbol = _arbol(COMPONENTES)
    boton = _clase(arbol, "BotonAccion")
    assert _funcion(boton, "con_rotulo"), "BotonAccion no ofrece un rotulo visible"
    pintar = ast.unparse(_funcion(boton, "_pintar"))
    assert "rotulo" in pintar, "el rotulo no se repinta con el estado"
    assert _llamadas_a(_arbol(GUI), "con_rotulo"), (
        "la ventana principal no usa el rotulo")


def _bind_de(nodo, evento: str):
    """Las llamadas `.bind(evento, ...)` del nodo, como texto del manejador."""
    return [ast.unparse(n.args[1]) for n in ast.walk(nodo)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "bind" and n.args
            and isinstance(n.args[0], ast.Constant) and n.args[0].value == evento
            and len(n.args) > 1]


def test_pc17_escape_cierra_las_emergentes_y_control_return_ejecuta():
    """El manejador de cada atajo hace lo que el atajo promete (no solo existe)."""
    for ruta, clase in ((VENTANA, "VentanaNormativa"), (AYUDA, "VentanaAyudaEntrada")):
        manejadores = _bind_de(_clase(_arbol(ruta), clase), "<Escape>")
        assert manejadores and all("destroy" in m for m in manejadores), \
            f"{clase} no cierra con Escape"
    arbol = _arbol(GUI)
    traza = _bind_de(_funcion(arbol, "_pintar_traza"), "<Escape>")
    assert traza and all("destroy" in m for m in traza)
    ejecutar = _bind_de(_funcion(arbol, "_crear_interfaz"), "<Control-Return>")
    assert ejecutar and all("ejecutar_pipeline" in m for m in ejecutar)


# ===========================================================================
# Higiene: el modulo nuevo entra en las guardias de la suite
# ===========================================================================

def test_ext8_el_modulo_de_exportacion_esta_vigilado():
    assert EXPORTACION.is_file()
    literales = (RAIZ / "tests" / "test_sin_literales.py").read_text(encoding="utf-8")
    assert "gui/exportacion_pdf.py" in literales
    # Por el DATO que test_gui_contrato publica, no por su texto (PC-21): un
    # comentario que nombrara el modulo pondria verde la version textual.
    from tests.test_gui_contrato import ARBOLES_DE_LA_GUI
    assert "gui/exportacion_pdf.py" in ARBOLES_DE_LA_GUI
