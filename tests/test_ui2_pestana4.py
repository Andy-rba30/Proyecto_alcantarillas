"""
tests/test_ui2_pestana4.py
==========================
La aceptacion de UI-2 (cadena de interfaz): LA PESTAÑA 4 CON LA MEMORIA
RESUMIDA Y EL CABEZAL DEL PROYECTO. Cierra la ficha T12-04 («la ventana
exporta solo la completa») y el hueco 3 del §0 de la cadena (el bloque del
cabezal del proyecto no se pintaba en ninguna pestaña).

Que se vigila, en el orden del prompt:

(a) El GRUPO de exportacion es uno (`gui/app.py::BOTONES_DE_EXPORTACION`) y
    trae los dos botones nuevos, «Memoria resumida (HTML)» y «Memoria
    resumida (PDF)»: nacen con `MOTIVO_SIN_CORRIDA`, se apagan con el motivo
    del gesto que invalida el informe y se encienden al correr, en TODOS los
    sitios que tratan a los exportadores como grupo; y leen del `Informe`
    (EXT-4), nunca del estado vivo.
(b) El PDF resumido sale por el proceso hijo de EXT-8: `cli.py --sesion ...
    --pdf-resumida ...`, armado por la MISMA funcion que el de la completa
    (`exportacion_pdf.comando_exportar_pdf`, con la vista como parametro), con
    la sesion de la corrida de UI-1 (hidrologia incluida), el rotulo «en
    marcha», la cancelacion y el estado terminal de la completa.
(c) El panel «Cabezal del proyecto» pinta `cli._lineas_cabezal` sin una
    palabra distinta, vacio con su motivo sin corrida, con lo que la CLI
    imprime cuando la Fase 9 se difiere, y se vacia y se llena con el resto
    de la pestaña.
(d) La ventana de verdad bajo xvfb (`tests/apoyo/gui_ui2_pestana4_real.py`)
    sobre la corrida de referencia `expediente_cabezal`: los siete botones,
    el panel igual al bloque que la CLI imprime para las mismas entradas, el
    HTML resumido con el mismo encabezado de trazabilidad que el completo, y
    el PDF resumido por el hijo (saltado SOLO si falta weasyprint, y
    diciendolo).

(e) Lo que la revision independiente de UI-2 encontro sobre `6392c34`: la
    ayuda del PDF resumido prometia el encabezado de la completa y el hijo
    recalcula (`expdf.AVISO_EL_HIJO_RECALCULA`); el exito del hijo se leia de
    «el destino existe», y un hijo que fallaba daba por bueno un PDF anterior
    y cancelar lo borraba (`expdf.CODIGOS_DE_SALIDA_CON_MEMORIA`, el PDF de
    trabajo y su entrega); correr con un PDF en marcha encendia los dos de PDF
    (`_encender_exportadores`); nada fijaba que la resumida lanzada desde la
    ventana llevara la hidrologia; y el hijo de la resumida no informaba
    avance (`progreso` en `M11.exportar_pdf_resumida`). Y en su verificacion:
    un PDF cortado a mitad (empieza por `%PDF`, sin `%%EOF`, codigo 1) se
    entregaba, y un PDF de un hijo anterior en el directorio de trabajo
    tambien. Cada test de (e) mata su mutante (medido: ficha UI2-03).

Escrita PRIMERO, en rojo (`xfail(strict=True)` a nivel de modulo, medida
antes de tocar codigo: 26 xfailed y 1 XPASS) y liberada al implementar, como
manda el §1 de la cadena. El XPASS es una guardia que vale antes y despues
(`test_b_un_solo_armador_del_comando`: la variante no puede duplicar el
armador). El de la linea de progreso de la resumida por `cli.py --progreso`
salio de esa primera redaccion al decidir no tocar `src/modulos/` y volvio
con la revision, que lo autorizo (ficha UI2-03). Los datos son DATOS DE
PRUEBA: las corridas de referencia de
`src/indice_formulas.CORRIDAS_DE_REFERENCIA` y las cuencas sinteticas de T-1.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

import cli
from src import declaracion as dec
from src import indice_formulas as ind
from src import sesion as ses
from src.modulos import M11_reporte as M11
from tests.apoyo import doble_tkinter

RAIZ = Path(__file__).resolve().parents[1]
GUI = RAIZ / "gui" / "app.py"
EXPORTACION_PDF = RAIZ / "gui" / "exportacion_pdf.py"
ARBOL_GUI = ast.parse(GUI.read_text(encoding="utf-8-sig"), filename="app.py")

LOS_DOS_NUEVOS = ("btn_html_resumida", "btn_pdf_resumida")
LOS_CINCO_DE_ANTES = ("btn_json", "btn_html", "btn_pdf", "btn_csv", "btn_comparar")


# ---------------------------------------------------------------------------
# Apoyos
# ---------------------------------------------------------------------------

def _funcion(arbol, nombre):
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and nodo.name == nombre:
            return nodo
    raise AssertionError(f"no se encontro la funcion {nombre}")


def _llamadas(nodo, nombre):
    return [n for n in ast.walk(nodo)
            if isinstance(n, ast.Call) and ast.unparse(n.func) == nombre]


def _referencia(nombre):
    return next(c for c in ind.CORRIDAS_DE_REFERENCIA if c.nombre == nombre)


def _es_separador(linea):
    limpia = linea.strip()
    return bool(limpia) and set(limpia) <= {"-", "="}


def _palabras(lineas):
    """
    Las lineas que se leen, con el espacio colapsado: lo que «ni una palabra
    distinta» compara. Los separadores de guiones y las lineas vacias no se
    pintan (`comp.escribir_lineas_de_cli`), y el hueco con que la CLI alinea
    columnas tampoco: ninguno de los tres es una palabra.
    """
    return [" ".join(l.split()) for l in lineas
            if l.strip() and not _es_separador(l)]


@pytest.fixture(scope="module")
def app():
    return doble_tkinter.gui_app()


@pytest.fixture(scope="module")
def informe_cabezal():
    return ind.correr_referencia(_referencia("expediente_cabezal"))


@pytest.fixture(scope="module")
def informe_perfil():
    return ind.correr_referencia(_referencia("perfil_guia"))


class _Boton:
    """El doble minimo de `BotonAccion`: recuerda si esta encendido y por que no."""

    def __init__(self):
        self.encendido = True
        self.motivo = None
        self.ayuda = ""

    def habilitar(self):
        self.encendido, self.motivo = True, None

    def deshabilitar(self, motivo):
        self.encendido, self.motivo = False, motivo


class _Rotulo:
    def __init__(self):
        self.texto = ""

    def config(self, **kw):
        if "text" in kw:
            self.texto = kw["text"]

    configure = config


class _Texto:
    """El doble de un `tk.Text`: lo que `escribir_lineas_de_cli` le escribe."""

    def __init__(self):
        self.partes = []
        self.estado = "normal"

    def configure(self, **kw):
        self.estado = kw.get("state", self.estado)

    config = configure

    def delete(self, *_a):
        self.partes = []

    def insert(self, _donde, texto, *_etiquetas):
        self.partes.append(texto)

    @property
    def contenido(self):
        return "".join(self.partes)


def _ventana(app, informe=None):
    """Una ventana SIN widgets de verdad: el grupo, el panel y lo que la logica lee."""
    v = object.__new__(app.ExpedienteApp)
    v.informe = informe
    for nombre in app.BOTONES_DE_EXPORTACION:
        setattr(v, nombre, _Boton())
    v.txt_cabezal = _Texto()
    v.txt_metrados = _Texto()          # VE-5 met: la Fase 11 bajo el cabezal
    v.lbl_cabezal = _Rotulo()
    v.lbl_estado = _Rotulo()
    v.lbl_error_datos = _Rotulo()
    v._vaciar_tablas_del_informe = lambda motivo: v._pintar_cabezal_del_proyecto(
        f"Sin informe vigente: {motivo}.")
    return v


# ===========================================================================
# (a) El grupo de exportacion
# ===========================================================================

def test_a_el_grupo_de_exportacion_es_uno_y_trae_los_dos_botones_nuevos(app):
    grupo = app.BOTONES_DE_EXPORTACION
    assert set(LOS_CINCO_DE_ANTES) <= set(grupo)
    assert set(LOS_DOS_NUEVOS) <= set(grupo)
    assert len(grupo) == len(set(grupo)) == 7


def _botones_creados(funcion):
    """{atributo: motivo} de cada `self.X = BotonAccion(..., motivo=...)`."""
    salida = {}
    for nodo in ast.walk(funcion):
        if (isinstance(nodo, ast.Assign) and len(nodo.targets) == 1
                and isinstance(nodo.targets[0], ast.Attribute)
                and isinstance(nodo.value, ast.Call)
                and ast.unparse(nodo.value.func) == "BotonAccion"):
            motivo = next((ast.unparse(kw.value) for kw in nodo.value.keywords
                           if kw.arg == "motivo"), None)
            salida[nodo.targets[0].attr] = motivo
    return salida


def test_a_cada_boton_que_nace_sin_corrida_en_la_pestana_4_esta_en_el_grupo(app):
    """
    En las DOS direcciones: un boton de la pestaña 4 que nace apagado por
    `MOTIVO_SIN_CORRIDA` es un exportador del informe y tiene que estar en el
    grupo (si no, invalidar el informe lo dejaria encendido), y todo miembro
    del grupo nace asi.
    """
    creados = _botones_creados(_funcion(ARBOL_GUI, "_construir_tab_resumen"))
    sin_corrida = {b for b, m in creados.items() if m == "MOTIVO_SIN_CORRIDA"}
    assert sin_corrida == set(app.BOTONES_DE_EXPORTACION)
    assert "btn_cancelar_pdf" in creados and "btn_cancelar_pdf" not in sin_corrida


def test_a_ningun_sitio_enumera_el_grupo_a_mano():
    """
    Los sitios que tratan a los exportadores como grupo (apagarlos al
    invalidar, encenderlos tras correr) leen la tupla: una enumeracion a mano
    es la que se queda corta cuando llega un boton nuevo.
    """
    for nodo in ast.walk(ARBOL_GUI):
        if isinstance(nodo, (ast.Tuple, ast.List)):
            atributos = {ast.unparse(e) for e in nodo.elts}
            assert not ({"self.btn_json", "self.btn_csv"} <= atributos), (
                f"enumeracion a mano del grupo: {ast.unparse(nodo)}")
    for funcion in ("_apagar_exportadores", "_encender_exportadores"):
        texto = ast.unparse(_funcion(ARBOL_GUI, funcion))
        assert "_botones_de_exportacion" in texto, funcion
    assert "self._encender_exportadores()" in ast.unparse(
        _funcion(ARBOL_GUI, "ejecutar_pipeline"))


@pytest.mark.parametrize("gesto, motivo", [
    ("_invalidar_informe", "MOTIVO_INFORME_DESACTUALIZADO"),
    ("_al_cambiar_la_hidrologia", "MOTIVO_HIDROLOGIA_CAMBIADA"),
    ("_mostrar_error_entrada", "MOTIVO_CORRIDA_FALLIDA"),
])
def test_a_los_siete_se_apagan_con_el_motivo_del_gesto(app, informe_cabezal, gesto, motivo):
    v = _ventana(app, informe_cabezal)
    for nombre in ("btn_ejecutar", "nb", "root"):
        setattr(v, nombre, doble_tkinter._Cualquiera())
    v._pintar_anticipo = lambda: None
    v.tab_datos = object()
    if gesto == "_invalidar_informe":
        v._invalidar_informe(app.MOTIVO_INFORME_DESACTUALIZADO)
    elif gesto == "_al_cambiar_la_hidrologia":
        v._al_cambiar_la_hidrologia()
    else:
        # Como en `ejecutar_pipeline`: el informe ya se retiro al empezar.
        v.informe = None
        v._mostrar_error_entrada("el CSV no se pudo leer")
    esperado = getattr(app, motivo)
    for nombre in app.BOTONES_DE_EXPORTACION:
        boton = getattr(v, nombre)
        assert not boton.encendido and boton.motivo == esperado, (gesto, nombre)
    # Y el panel del cabezal dice lo mismo que la barra.
    assert v.txt_cabezal.contenido == ""
    assert esperado in v.lbl_cabezal.texto


class _ProcesoEnMarcha:
    """Un hijo del PDF que sigue escribiendo (o que ya termino)."""

    def __init__(self, terminal=False):
        import gui.exportacion_pdf as ex
        self.estado = ex.EstadoPdf.TERMINADO if terminal else ex.EstadoPdf.EN_MARCHA


def test_a_tras_correr_se_encienden_los_siete_y_se_relee_la_ayuda_de_los_dos_pdf(app):
    v = _ventana(app)
    v.proceso_pdf = None
    v._apagar_exportadores(app.MOTIVO_EJECUTANDO)
    v._encender_exportadores()
    assert all(getattr(v, n).encendido for n in app.BOTONES_DE_EXPORTACION)
    v.proceso_pdf = _ProcesoEnMarcha(terminal=True)
    v._encender_exportadores()
    assert all(getattr(v, n).encendido for n in app.BOTONES_DE_EXPORTACION)
    ejecutar = ast.unparse(_funcion(ARBOL_GUI, "ejecutar_pipeline"))
    assert "self._encender_exportadores()" in ejecutar
    assert "self.btn_pdf.ayuda" in ejecutar
    assert "self.btn_pdf_resumida.ayuda" in ejecutar


def test_a_correr_con_un_pdf_en_marcha_no_enciende_los_dos_de_pdf(app):
    """
    Revision de UI-2: correr mientras el hijo escribe un PDF encendia los
    siete, y los dos de PDF quedaban encendidos y sin motivo con el hijo en
    marcha. Se quedan apagados con `MOTIVO_EXPORTANDO_PDF` y los enciende
    `_terminar_pdf`.
    """
    v = _ventana(app)
    v.proceso_pdf = _ProcesoEnMarcha()
    v._apagar_exportadores(app.MOTIVO_EJECUTANDO)
    v._encender_exportadores()
    for nombre in app.BOTONES_DE_EXPORTACION:
        boton = getattr(v, nombre)
        if nombre in app.BOTONES_PDF:
            assert not boton.encendido and boton.motivo == app.MOTIVO_EXPORTANDO_PDF
        else:
            assert boton.encendido, nombre
    assert set(app.BOTONES_PDF) == {"btn_pdf", "btn_pdf_resumida"}


def test_a_la_resumida_en_html_lee_del_informe_y_por_la_puerta_de_la_cli():
    """
    EXT-4: el HTML resumido se escribe en ESTE proceso con
    `M11.exportar_html_resumida` (la MISMA funcion que la CLI llama para
    `--html-resumida`), sobre `self.informe` y con el nombre del proyecto
    fotografiado al correr; nunca con el estado vivo de los catalogos.
    """
    assert cli.exportar_html_resumida is M11.exportar_html_resumida
    funcion = _funcion(ARBOL_GUI, "exportar_html_resumida")
    llamadas = _llamadas(funcion, "cli.exportar_html_resumida")
    assert len(llamadas) == 1
    assert ast.unparse(llamadas[0].args[0]) == "self.informe"
    proyecto = {kw.arg: ast.unparse(kw.value) for kw in llamadas[0].keywords}
    assert proyecto.get("proyecto") == "self.proyecto_de_la_corrida"
    texto = ast.unparse(funcion)
    for vivo in ("dec.", "ca.", "_datos_de_sesion", "proyecto_var", "alcance_var"):
        assert vivo not in texto, vivo


def test_a_la_resumida_en_pdf_sale_por_el_hijo_o_por_el_navegador_del_informe():
    funcion = _funcion(ARBOL_GUI, "exportar_pdf_resumida")
    texto = ast.unparse(funcion)
    assert "self._lanzar_pdf(" in texto and "expdf.VISTA_RESUMIDA" in texto
    assert "M11.weasyprint_disponible()" in texto
    navegador = _llamadas(funcion, "cli.exportar_pdf_resumida")
    assert navegador and all(ast.unparse(l.args[0]) == "self.informe" for l in navegador)
    for vivo in ("dec.", "ca.", "_datos_de_sesion", "proyecto_var", "alcance_var"):
        assert vivo not in texto, vivo
    # Un solo PDF en marcha a la vez: la resumida y la completa comparten el
    # proceso hijo, su cancelacion y su sondeo.
    assert "_hay_un_pdf_en_marcha" in texto
    assert "_hay_un_pdf_en_marcha" in ast.unparse(_funcion(ARBOL_GUI, "exportar_pdf"))
    lanzar = ast.unparse(_funcion(ARBOL_GUI, "_lanzar_pdf"))
    assert "vista=vista" in lanzar and "_botones_pdf" in lanzar


@pytest.mark.parametrize("nombre", ["exportar_html_resumida", "exportar_pdf_resumida"])
def test_a_los_dos_exportadores_nuevos_separan_el_fallo_del_expediente(nombre):
    """El patron de SIS-E-03: ErrorProyecto primero, y el brazo ancho con traza."""
    from tests.test_gui_contrato import _brazos, _llama_a
    brazos = _brazos(_funcion(ARBOL_GUI, nombre))
    tipos = [caps for caps, _ in brazos]
    estrechos = [i for i, caps in enumerate(tipos) if "ErrorProyecto" in caps]
    anchos = [i for i, caps in enumerate(tipos) if "Exception" in caps]
    assert estrechos and anchos and min(estrechos) < min(anchos)
    for caps, manejador in brazos:
        if "Exception" in caps:
            assert _llama_a(manejador, "print_exc")


def test_a_la_ayuda_del_pdf_resumido_dice_la_via_antes_de_pulsar(app):
    ayuda = app.ExpedienteApp._ayuda_del_pdf(object(), vista=app.expdf.VISTA_RESUMIDA)
    assert "resumida" in ayuda.lower()
    assert ("proceso aparte" in ayuda.lower()) or ("navegador" in ayuda.lower())
    completa = app.ExpedienteApp._ayuda_del_pdf(object())
    assert str(app.expdf.UMBRAL_PUNTOS_PDF) in completa


def test_a_la_ayuda_no_promete_el_encabezado_de_la_completa_al_pdf_del_hijo(
        app, monkeypatch):
    """
    Revision de UI-2: la ayuda del PDF resumido decia «Sale del mismo informe
    que la completa (mismo encabezado de trazabilidad)», y el hijo VOLVIA A
    CORRER la obra: su hora de corrida era otra. Desde VE-5 (fichas
    EXT-10-04 y UI5-01 b) el hijo formatea la corrida de la ventana sin
    recalcular, y las dos ayudas de PDF lo dicen con UN texto
    (`expdf.AVISO_EL_HIJO_NO_RECALCULA`); la del HTML resumido, que se
    escribe aqui del mismo informe, promete el encabezado entre los dos HTML.
    """
    monkeypatch.setattr(app.M11, "_WEASYPRINT_SONDEADO", True)
    monkeypatch.setattr(app.M11, "WeasyHTML", object())
    for vista in (app.expdf.VISTA_RESUMIDA, app.expdf.VISTA_COMPLETA):
        ayuda = app.ExpedienteApp._ayuda_del_pdf(object(), vista=vista)
        assert app.expdf.AVISO_EL_HIJO_NO_RECALCULA in ayuda, vista
        assert "proceso aparte" in ayuda.lower(), vista
    assert "NO vuelve a correr" in app.expdf.AVISO_EL_HIJO_NO_RECALCULA
    assert "HTML" in app.AYUDA_HTML_RESUMIDA and "mismo encabezado" in app.AYUDA_HTML_RESUMIDA
    creados = ast.unparse(_funcion(ARBOL_GUI, "_construir_tab_resumen"))
    assert "ayuda=AYUDA_HTML_RESUMIDA" in creados


def test_a_la_resumida_en_pdf_de_la_ventana_lleva_la_hidrologia_de_la_corrida(
        app, monkeypatch, tmp_path):
    """
    Revision de UI-2 (mutante vivo): nada fijaba que la resumida lanzada
    DESDE LA VENTANA llevara al hijo las dos rutas de la hidrologia con que
    corrio el informe. Se pulsa «Memoria resumida (PDF)» sobre la corrida de
    referencia `hidrologia_calculada` y se mira la sesion que recibe el hijo.
    """
    referencia = _referencia("hidrologia_calculada")
    informe = ind.correr_referencia(referencia)
    assert informe.hidrologia is not None
    recibidos = []

    class _HijoQueRecuerda:
        def __init__(self, **kw):
            recibidos.append(kw)
            self.vista = kw["vista"]
            self.estado = app.expdf.EstadoPdf.SIN_INICIAR
            self.progreso = app.expdf.PROGRESO_INICIAL

        def iniciar(self):
            self.estado = app.expdf.EstadoPdf.EN_MARCHA

    monkeypatch.setattr(app.expdf, "ProcesoPdf", _HijoQueRecuerda)
    monkeypatch.setattr(app.M11, "weasyprint_disponible", lambda: True)
    monkeypatch.setattr(app.filedialog, "asksaveasfilename",
                        lambda **kw: str(tmp_path / "resumida.pdf"))
    monkeypatch.setattr(app.tempfile, "mkdtemp", lambda **kw: str(tmp_path / "trabajo"))
    v = _ventana(app, informe)
    v.proceso_pdf = None
    v.proyecto_de_la_corrida = "DATOS DE PRUEBA - UI-2"
    v.sesion_id = "id-ui2"
    v.entradas_de_la_corrida = {
        "csv": str(referencia.csv), "datos_externos": str(referencia.externos),
        "datos_sitio": str(referencia.sitio), "cuencas": str(referencia.cuencas),
        "estacion": str(referencia.estacion), "externos": {},
        "alcance": referencia.alcance}
    for nombre in ("btn_cancelar_pdf", "lbl_estado_pdf", "root"):
        setattr(v, nombre, doble_tkinter._Cualquiera())
    v.exportar_pdf_resumida()
    assert len(recibidos) == 1, "la ventana no lanzo el hijo"
    kw = recibidos[0]
    assert kw["vista"] == app.expdf.VISTA_RESUMIDA and kw["plantilla"] is None
    assert kw["sesion"]["cuencas"] == str(referencia.cuencas)
    assert kw["sesion"]["estacion"] == str(referencia.estacion)
    # Es la sesion de la corrida, la MISMA que la completa enviaria.
    assert kw["sesion"] == app.expdf.sesion_de_la_corrida(
        informe, proyecto="DATOS DE PRUEBA - UI-2", formato_version=app.FORMATO_SESION,
        app_version=app.APP_VERSION, id_sesion="id-ui2", **v.entradas_de_la_corrida)
    for nombre in app.BOTONES_PDF:
        assert getattr(v, nombre).motivo == app.MOTIVO_EXPORTANDO_PDF


# ===========================================================================
# (b) El PDF resumido por el proceso hijo de EXT-8
# ===========================================================================

@pytest.fixture(scope="module")
def expdf():
    import gui.exportacion_pdf as ex
    return ex


def test_b_el_comando_de_la_resumida_es_el_de_la_completa_con_su_bandera(expdf, tmp_path):
    comunes = dict(interprete="py", cli=Path("cli.py"), sesion=Path("s.json"),
                   destino=Path("m.pdf"), json_aparte=Path("i.json"))
    completa = expdf.comando_exportar_pdf(plantilla=Path("p.html"), **comunes)
    # La completa, IGUAL que antes de UI-2 (el contrato con `cli.main`).
    assert completa == ["py", "cli.py", "--sesion", "s.json", "--pdf", "m.pdf",
                        "--json", "i.json", "--plantilla", "p.html", "--progreso"]
    resumida = expdf.comando_exportar_pdf(vista=expdf.VISTA_RESUMIDA, **comunes)
    assert resumida == ["py", "cli.py", "--sesion", "s.json", "--pdf-resumida",
                        "m.pdf", "--json", "i.json", "--progreso"]
    # La CLI lo entiende como lo que es.
    args = cli._parser().parse_args(resumida[2:])
    assert args.pdf_resumida_salida == Path("m.pdf") and args.pdf_salida is None
    assert args.progreso and args.html_salida is None
    with pytest.raises(ValueError):
        expdf.comando_exportar_pdf(vista="otra", **comunes)
    with pytest.raises(ValueError):
        expdf.comando_exportar_pdf(vista=expdf.VISTA_COMPLETA, **comunes)
    assert set(expdf.BANDERA_DE_LA_VISTA) == {expdf.VISTA_COMPLETA, expdf.VISTA_RESUMIDA}


def test_b_un_solo_armador_del_comando():
    """La variante no duplica la logica: una funcion arma los dos comandos."""
    arbol = ast.parse(EXPORTACION_PDF.read_text(encoding="utf-8-sig"))
    armadores = [n.name for n in ast.walk(arbol)
                 if isinstance(n, ast.FunctionDef) and "comando" in n.name]
    assert armadores == ["comando_exportar_pdf"]
    llamadas = [n for n in ast.walk(arbol) if isinstance(n, ast.Call)
                and ast.unparse(n.func) == "comando_exportar_pdf"]
    assert len(llamadas) == 1


def test_b_la_cli_con_la_linea_del_hijo_escribe_la_resumida_por_el_navegador(
        tmp_path, capsys, monkeypatch, expdf):
    """
    La linea que la ventana manda al hijo, corrida en este proceso con la
    via del navegador forzada: escribe la resumida (no la completa), deja el
    JSON aparte y no pisa el `<csv>.informe.json` del usuario.
    """
    monkeypatch.setattr(M11, "WeasyHTML", None)
    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", True)
    monkeypatch.setattr(M11.webbrowser, "open", lambda *a, **k: True)
    from tests.test_ext8_rendimiento_gui import _sesion_de_prueba
    referencia = _referencia("perfil_guia")
    sesion = tmp_path / "s.json"
    ses.escribir_json_atomico(sesion, _sesion_de_prueba(referencia.csv,
                                                        cli.ALCANCE_PERFIL))
    comando = expdf.comando_exportar_pdf(
        interprete="py", cli=Path("cli.py"), sesion=sesion,
        destino=tmp_path / "r.pdf", json_aparte=tmp_path / "aparte.json",
        vista=expdf.VISTA_RESUMIDA)
    assert cli.main(comando[2:]) in (0, 1)
    escrito = (tmp_path / "r.html").read_text(encoding="utf-8")
    assert M11.TITULO_RESUMEN_VERIFICACIONES in escrito
    assert "memoria RESUMIDA" in escrito
    assert (tmp_path / "aparte.json").is_file()
    assert not referencia.csv.with_suffix(".informe.json").exists()
    # La via del navegador lo dice, con el archivo que de verdad escribio.
    assert str(tmp_path / "r.html") in capsys.readouterr().out


def test_b_la_cli_informa_el_progreso_de_la_resumida(tmp_path, capsys, monkeypatch):
    """
    Con `--progreso`, el PDF resumido deja su linea de etapa en stdout, que
    es lo que el rotulo de la ventana lee del hijo; sin la bandera, ninguna
    (revision de UI-2: `progreso` en `M11.exportar_pdf_resumida`).
    """
    monkeypatch.setattr(M11, "WeasyHTML", None)
    monkeypatch.setattr(M11, "_WEASYPRINT_SONDEADO", True)
    monkeypatch.setattr(M11.webbrowser, "open", lambda *a, **k: True)
    csv_ = _referencia("perfil_guia").csv
    externos = str(_referencia("perfil_guia").externos)
    cli.main([str(csv_), "--datos-externos", externos, "--alcance", "perfil",
              "--json", str(tmp_path / "a.json"),
              "--pdf-resumida", str(tmp_path / "r.pdf"), "--progreso"])
    lineas = [l for l in capsys.readouterr().out.splitlines()
              if l.startswith(cli.PREFIJO_PROGRESO)]
    assert any(M11.ETAPA_NAVEGADOR in l for l in lineas), lineas
    cli.main([str(csv_), "--datos-externos", externos, "--alcance", "perfil",
              "--json", str(tmp_path / "b.json"),
              "--pdf-resumida", str(tmp_path / "s.pdf")])
    assert cli.PREFIJO_PROGRESO not in capsys.readouterr().out


# Un `cli.py` de mentira para el hijo: escribe (o no) un PDF en la ruta que
# recibe y sale con el codigo que se le dice. Es lo que deja probar, sin
# weasyprint y sin carreras, la regla de exito del hijo.
CLI_DE_MENTIRA = """
import json, sys
from pathlib import Path
orden = json.loads((Path(__file__).parent / "orden.json").read_text())
args = sys.argv[1:]
bandera = "--pdf-resumida" if "--pdf-resumida" in args else "--pdf"
contenido = {"entero": b"%PDF-del-hijo\\n%%EOF\\n",
             "truncado": b"%PDF-del-hijo, cortado a mitad sin trailer"}
if orden["escribe"]:
    Path(args[args.index(bandera) + 1]).write_bytes(contenido[orden["escribe"]])
sys.exit(orden["codigo"])
"""
PDF_ANTERIOR = b"%PDF-VIEJO, de otra exportacion\n%%EOF\n"
PDF_DEL_HIJO = b"%PDF-del-hijo\n%%EOF\n"


def _proceso_de_mentira(expdf, tmp_path, vista, codigo, escribe, trabajo=None):
    """Un `ProcesoPdf` con el `cli.py` de mentira y un destino con un PDF anterior."""
    raiz = tmp_path / "raiz"
    raiz.mkdir(exist_ok=True)
    (raiz / "cli.py").write_text(CLI_DE_MENTIRA, encoding="utf-8")
    (raiz / "orden.json").write_text(json.dumps({"codigo": codigo, "escribe": escribe}),
                                     encoding="utf-8")
    destino = tmp_path / "salida" / "memoria.pdf"
    destino.parent.mkdir(exist_ok=True)
    destino.write_bytes(PDF_ANTERIOR)
    proceso = expdf.ProcesoPdf(
        sesion={"csv": "x.csv"}, destino=destino, vista=vista,
        plantilla=Path("p.html") if vista == expdf.VISTA_COMPLETA else None,
        directorio_trabajo=trabajo or (tmp_path / "trabajo"),
        interprete=sys.executable, raiz=raiz)
    return proceso, destino


@pytest.mark.parametrize("vista", ["completa", "resumida"])
@pytest.mark.parametrize("codigo, escribe, terminado", [
    (0, "entero", True),     # cierra y escribe
    (1, "entero", True),     # no cierra (contrato de cli.main) y escribe
    (2, "entero", False),    # no pudo correr: lo que haya escrito no vale
    (0, None, False),        # dice que bien y no dejo PDF
    (1, "truncado", False),  # excepcion a mitad de la escritura (verificacion)
    (0, "truncado", False),  # y un cero no salva un PDF sin trailer
])
def test_b_el_exito_del_hijo_exige_su_codigo_y_su_pdf(tmp_path, expdf, vista,
                                                      codigo, escribe, terminado):
    """
    Revision de UI-2: el exito se leia de «el destino existe y no esta
    vacio», sin mirar el codigo de salida ni quien lo escribio. Ahora el hijo
    escribe en su directorio de trabajo y el PDF se entrega al destino solo
    con un codigo de `CODIGOS_DE_SALIDA_CON_MEMORIA` y un PDF suyo; si no, el
    destino --- aqui con un PDF anterior --- no se toca.
    """
    proceso, destino = _proceso_de_mentira(expdf, tmp_path, vista, codigo, escribe)
    proceso.iniciar()
    estado = _esperar(proceso, limite_s=60)
    assert expdf.CODIGOS_DE_SALIDA_CON_MEMORIA == (0, 1)
    if terminado:
        assert estado is expdf.EstadoPdf.TERMINADO, proceso.detalle
        assert destino.read_bytes() == PDF_DEL_HIJO
    else:
        assert estado is expdf.EstadoPdf.FALLIDO, proceso.detalle
        assert destino.read_bytes() == PDF_ANTERIOR
        assert "no se toco" in proceso.detalle
    assert str(destino) not in proceso.comando, "el hijo no escribe en el destino"
    assert not list(destino.parent.glob("*.parcial"))


def test_b_un_pdf_de_un_hijo_anterior_en_el_directorio_de_trabajo_no_se_entrega(
        tmp_path, expdf):
    """
    Verificacion de la revision de UI-2: con un `directorio_trabajo` fijo,
    reutilizado, un hijo que sale con 1 sin escribir habria entregado el PDF
    ENTERO que dejo el anterior. `iniciar` retira lo de antes.
    """
    trabajo = tmp_path / "trabajo_fijo"
    trabajo.mkdir()
    (trabajo / "memoria_del_hijo.pdf").write_bytes(b"%PDF-de-un-hijo-anterior\n%%EOF\n")
    proceso, destino = _proceso_de_mentira(expdf, tmp_path, expdf.VISTA_RESUMIDA,
                                           1, None, trabajo=trabajo)
    assert proceso.ruta_pdf_de_trabajo == trabajo / "memoria_del_hijo.pdf"
    proceso.iniciar()
    assert _esperar(proceso, limite_s=60) is expdf.EstadoPdf.FALLIDO, proceso.detalle
    assert destino.read_bytes() == PDF_ANTERIOR


@pytest.mark.lento
@pytest.mark.skipif(os.name != "posix" or shutil.which("bash") is None,
                    reason="el limite de tamaño de archivo se pone con `ulimit -f` de bash")
def test_b_un_pdf_cortado_a_mitad_por_el_hijo_real_no_se_entrega(tmp_path, expdf,
                                                                 informe_cabezal):
    """
    La reproduccion de la verificacion, con el hijo DE VERDAD: un interprete
    con `ulimit -f 1000` (Python ignora SIGXFSZ, y la escritura falla con
    `OSError` [Errno 27]) escribe la memoria completa de `expediente_cabezal`
    (1.8 MB) y la corta en 1 000 KB: el hijo sale con 1. Antes se daba por
    terminado y reemplazaba el PDF del usuario.

    CAMBIADO EN UI-5 (decision del dueño, ficha UI2-03), declarando la causa:
    hasta UI-5 el hijo dejaba en su directorio de trabajo un PDF CORTADO
    (empieza por `%PDF` y no lleva `%%EOF`), que este test exigia para no
    perder su objeto, y lo que lo detenia era la comprobacion del trailer de
    `ProcesoPdf`. Desde UI-5 `M11._escribir_pdf` escribe a un temporal del
    mismo directorio y lo retira al fallar: el hijo no deja PDF de trabajo
    ninguno, ni cortado ni entero, y el destino sigue sin tocarse. El
    trailer se queda como segunda linea (su test, el del hijo de mentira que
    sale con 0 o 1 y un PDF «truncado», sigue arriba).
    """
    if not M11.weasyprint_disponible():
        pytest.skip("weasyprint no esta operativo en este interprete: el hijo no "
                    "llega a escribir el PDF que se corta")
    limitado = tmp_path / "python_limitado.sh"
    limitado.write_text(f'#!/bin/bash\nulimit -f 1000\nexec "{sys.executable}" "$@"\n',
                        encoding="utf-8")
    limitado.chmod(0o755)
    referencia = _referencia("expediente_cabezal")
    sesion = expdf.sesion_de_la_corrida(
        informe_cabezal, proyecto="DATOS DE PRUEBA - UI-2", csv=str(referencia.csv),
        datos_externos=str(referencia.externos), externos={},
        alcance=referencia.alcance, formato_version=ses.FORMATO_SESION,
        app_version="1.0")
    destino = tmp_path / "completa.pdf"
    destino.write_bytes(PDF_ANTERIOR)
    proceso = expdf.ProcesoPdf(
        sesion=sesion, destino=destino, vista=expdf.VISTA_COMPLETA,
        plantilla=cli.plantilla_por_alcance(referencia.alcance),
        directorio_trabajo=tmp_path / "trabajo", interprete=str(limitado), raiz=RAIZ)
    proceso.iniciar()
    estado = _esperar(proceso)
    salida_del_hijo = proceso.ruta_salida.read_text(encoding="utf-8", errors="replace")
    assert "File too large" in salida_del_hijo or "Errno 27" in salida_del_hijo, (
        "la escritura no se corto: el test perderia su objeto")
    assert not proceso.ruta_pdf_de_trabajo.exists(), "M11 dejo un PDF de trabajo cortado"
    assert not list(proceso.directorio_trabajo.glob("*.parcial"))
    assert estado is expdf.EstadoPdf.FALLIDO, proceso.detalle
    # Desde VE-5 (ficha UI5-01 c) la CLI atrapa el `OSError` de la escritura
    # y sale con su codigo propio y su mensaje, no con la traza y el 1.
    assert f"codigo {cli.CODIGO_ESCRITURA_FALLIDA}" in proceso.detalle
    assert "Traceback" not in salida_del_hijo
    assert destino.read_bytes() == PDF_ANTERIOR


def test_b_un_hijo_que_no_puede_correr_no_da_por_bueno_el_pdf_anterior(tmp_path, expdf):
    """
    Lo reproducido por la revision, con la CLI DE VERDAD: destino con un PDF
    anterior y la sesion con el CSV retirado; el hijo sale con 2 («No se pudo
    leer la entrada»). Antes la ventana decia «terminado | PDF resumido
    escrito» con el archivo viejo.
    """
    from tests.test_ext8_rendimiento_gui import _sesion_de_prueba
    destino = tmp_path / "r.pdf"
    destino.write_bytes(PDF_ANTERIOR)
    proceso = expdf.ProcesoPdf(
        sesion=_sesion_de_prueba(tmp_path / "csv_retirado.csv", cli.ALCANCE_PERFIL),
        destino=destino, vista=expdf.VISTA_RESUMIDA,
        directorio_trabajo=tmp_path / "trabajo", interprete=sys.executable, raiz=RAIZ)
    proceso.iniciar()
    assert _esperar(proceso, limite_s=120) is expdf.EstadoPdf.FALLIDO
    assert "codigo 2" in proceso.detalle
    assert destino.read_bytes() == PDF_ANTERIOR


def test_b_cancelar_no_borra_un_pdf_anterior(tmp_path, expdf):
    """Revision de UI-2: cancelar borraba un PDF bueno que ya estuviera en el destino."""
    from tests.test_ext8_rendimiento_gui import _sesion_de_prueba
    destino = tmp_path / "r.pdf"
    destino.write_bytes(PDF_ANTERIOR)
    proceso = expdf.ProcesoPdf(
        sesion=_sesion_de_prueba(_referencia("perfil_guia").csv, cli.ALCANCE_PERFIL),
        destino=destino, vista=expdf.VISTA_RESUMIDA,
        directorio_trabajo=tmp_path / "trabajo", interprete=sys.executable, raiz=RAIZ)
    proceso.iniciar()
    proceso.cancelar()
    assert _esperar(proceso, limite_s=60) is expdf.EstadoPdf.CANCELADO
    assert destino.read_bytes() == PDF_ANTERIOR
    assert "no se toco" in proceso.detalle


def _esperar(proceso, limite_s=600.0):
    inicio = time.monotonic()
    while not proceso.sondear().terminal:
        assert time.monotonic() - inicio < limite_s, "el hijo no termino a tiempo"
        time.sleep(0.05)
    return proceso.estado


def test_b_el_hijo_escribe_la_resumida_con_la_hidrologia_de_la_corrida(tmp_path, expdf):
    """
    La sesion que viaja al hijo es la de UI-1, con las dos rutas de la
    hidrologia: el JSON del hijo es el de la corrida propia salvo la marca
    de tiempo, y el PDF que deja es la RESUMIDA.
    """
    if not M11.weasyprint_disponible():
        pytest.skip("weasyprint no esta operativo en este interprete: el PDF "
                    "resumido por el hijo no se puede escribir aqui")
    from tests.test_ui1_hidrologia_ventana import (CLAVE_FEN, CUENCAS, ESTACION,
                                                   _csv_sin_caudal, _externos,
                                                   _sesion_con_hidrologia,
                                                   _sin_marca)
    estado = dec.estado_de_sesion()
    try:
        dec.declarar_valor(CLAVE_FEN, "serie_completa",
                           nota="DATOS DE PRUEBA: declarado para UI-2")
        puntos = _csv_sin_caudal(tmp_path)
        sesion = _sesion_con_hidrologia(tmp_path, puntos, proyecto="obra UI-2")
        dec.restaurar_sesion(json.loads(json.dumps(sesion["criterios"])), sustituir=True)
        informe = cli.correr(puntos, _externos(), alcance=cli.ALCANCE_PERFIL,
                             hidrologia=cli.cargar_hidrologia(CUENCAS, ESTACION))
        propio = cli.informe_json(informe)
    finally:
        dec.restaurar_sesion(estado, sustituir=True)
    destino = tmp_path / "resumida.pdf"
    proceso = expdf.ProcesoPdf(sesion=sesion, destino=destino,
                               vista=expdf.VISTA_RESUMIDA,
                               directorio_trabajo=tmp_path / "trabajo",
                               interprete=sys.executable, raiz=RAIZ)
    proceso.iniciar()
    assert _esperar(proceso) is expdf.EstadoPdf.TERMINADO, proceso.detalle
    assert "--pdf-resumida" in proceso.comando and "--pdf" not in proceso.comando
    assert destino.read_bytes().startswith(b"%PDF")
    assert any(M11.ETAPA_PDF in p for p in proceso.progreso_visto), proceso.progreso_visto
    assert proceso.detalle.startswith(expdf.ROTULO_DE_LA_VISTA[expdf.VISTA_RESUMIDA])
    ajeno = json.loads(proceso.ruta_json.read_text(encoding="utf-8"))
    assert _sin_marca(propio) == _sin_marca(ajeno)
    assert ajeno["expediente"]["hidrologia"]["cuencas"] == str(CUENCAS)
    # Es la RESUMIDA y no la completa: su titulo de verificaciones y su
    # remision a la completa estan en el texto del PDF.
    fitz = pytest.importorskip("fitz", reason="sin PyMuPDF no se lee el texto del PDF")
    with fitz.open(destino) as documento:
        texto = " ".join(" ".join(p.get_text().split()) for p in documento)
    assert M11.TITULO_RESUMEN_VERIFICACIONES in texto
    assert "memoria RESUMIDA" in texto


def test_b_cancelar_la_resumida_no_deja_pdf(tmp_path, expdf):
    from tests.test_ext8_rendimiento_gui import _sesion_de_prueba
    proceso = expdf.ProcesoPdf(
        sesion=_sesion_de_prueba(_referencia("perfil_guia").csv, cli.ALCANCE_PERFIL),
        destino=tmp_path / "r.pdf", vista=expdf.VISTA_RESUMIDA,
        directorio_trabajo=tmp_path / "trabajo", interprete=sys.executable, raiz=RAIZ)
    proceso.iniciar()
    proceso.cancelar()
    assert _esperar(proceso, limite_s=60) is expdf.EstadoPdf.CANCELADO
    assert not (tmp_path / "r.pdf").exists()


# ===========================================================================
# (c) El panel «Cabezal del proyecto»
# ===========================================================================

def test_c_el_panel_pinta_el_cabezal_con_las_palabras_de_la_cli(app, informe_cabezal):
    v = _ventana(app, informe_cabezal)
    v._pintar_cabezal_del_proyecto()
    lineas = cli._lineas_cabezal(informe_cabezal.cabezal)
    assert _palabras(v.txt_cabezal.contenido.splitlines()) == _palabras(lineas)
    assert v.lbl_cabezal.texto == ""
    # Es el cabezal de un expediente que llego a la Fase 9.
    assert "Cadena sismica" in v.txt_cabezal.contenido
    assert v.txt_cabezal.estado == "disabled"


def test_c_a_perfil_el_panel_dice_lo_que_la_cli_imprime(app, informe_perfil):
    v = _ventana(app, informe_perfil)
    v._pintar_cabezal_del_proyecto()
    lineas = cli._lineas_cabezal(informe_perfil.cabezal)
    assert _palabras(v.txt_cabezal.contenido.splitlines()) == _palabras(lineas)
    diferidos = [b for b in informe_perfil.cabezal.bloqueos if b.diferido_por_alcance]
    assert diferidos, "a perfil la Fase 9 se difiere: el test perderia su objeto"
    assert diferidos[0].etapa in v.txt_cabezal.contenido


def test_c_sin_informe_el_panel_queda_vacio_con_su_motivo(app):
    v = _ventana(app, None)
    v.txt_cabezal.partes = ["algo de la corrida anterior\n"]
    v._pintar_cabezal_del_proyecto()
    assert v.txt_cabezal.contenido == ""
    assert v.lbl_cabezal.texto == app.MOTIVO_SIN_CORRIDA_CABEZAL
    v._pintar_cabezal_del_proyecto("Sin informe vigente: otro motivo.")
    assert v.lbl_cabezal.texto == "Sin informe vigente: otro motivo."


def test_c_el_panel_no_escribe_texto_propio():
    """La ventana solo pinta: el texto sale de `cli._lineas_cabezal`."""
    funcion = _funcion(ARBOL_GUI, "_pintar_cabezal_del_proyecto")
    llamada = _llamadas(funcion, "comp.escribir_lineas_de_cli")
    assert any("cli._lineas_cabezal(self.informe.cabezal)" in ast.unparse(l)
               for l in llamada)
    textos = [n.value for n in ast.walk(funcion)
              if isinstance(n, ast.Constant) and isinstance(n.value, str)
              and n is not funcion.body[0].value]
    assert all(len(t) < 20 for t in textos), textos   # solo opciones de widget


def test_c_el_panel_se_vacia_y_se_llena_con_el_resto_de_la_pestana():
    vaciar = ast.unparse(_funcion(ARBOL_GUI, "_vaciar_tablas_del_informe"))
    assert "self._pintar_cabezal_del_proyecto(" in vaciar
    llenar = ast.unparse(_funcion(ARBOL_GUI, "_llenar_resumen"))
    assert "self._pintar_cabezal_del_proyecto()" in llenar
    # La corrida que no produce informe deja el panel diciendolo, por la
    # misma via que la barra: los dos brazos de `ejecutar_pipeline`.
    for funcion in ("_mostrar_error_entrada", "ejecutar_pipeline"):
        texto = ast.unparse(_funcion(ARBOL_GUI, funcion))
        assert "self._vaciar_tablas_del_informe(MOTIVO_CORRIDA_FALLIDA)" in texto, funcion


# ===========================================================================
# (d) La ventana de verdad
# ===========================================================================

def _interprete_con_ventana():
    from tests.test_gui_contrato import _ENVOLTORIO, _INTERPRETE
    return _INTERPRETE, _ENVOLTORIO


@pytest.fixture(scope="module")
def ventana_real(tmp_path_factory):
    interprete, envoltorio = _interprete_con_ventana()
    if interprete is None:
        pytest.skip("ningun interprete disponible puede levantar una ventana "
                    "(falta tkinter, ttkbootstrap o el entorno grafico)")
    salida = tmp_path_factory.mktemp("ui2_ventana")
    hecho = subprocess.run(
        envoltorio + [interprete, "-m", "tests.apoyo.gui_ui2_pestana4_real", str(salida)],
        cwd=RAIZ, capture_output=True, text=True, timeout=1500)
    assert hecho.returncode == 0, (
        f"la corrida de la GUI fallo:\n{hecho.stdout[-4000:]}\n{hecho.stderr[-4000:]}")
    r = json.loads((salida / "resumen_ui2.json").read_text(encoding="utf-8"))
    return salida, r


def _bloque_del_cabezal_en_la_salida_de_la_cli(salida):
    """Las lineas que `volcar` imprime del cabezal del proyecto, de su titulo al siguiente."""
    lineas = salida.splitlines()
    titulo = f"{cli.FASE_CABEZAL} - del proyecto, no del punto"
    inicio = lineas.index(titulo)
    fin = lineas.index("ALCANCE DE LA CORRIDA", inicio)
    return lineas[inicio - 1:fin - 1]


def _cli_de_la_referencia(referencia, tmp_path):
    args = [sys.executable, str(RAIZ / "cli.py"), str(referencia.csv),
            "--datos-externos", str(referencia.externos),
            "--alcance", referencia.alcance, "--json", str(tmp_path / "cli.json")]
    if referencia.sitio is not None:
        args += ["--datos-sitio", str(referencia.sitio)]
    for clave, valor in referencia.declaraciones.items():
        args += ["--declarar", f"{clave}={valor!r}"]
    hecho = subprocess.run(args, cwd=RAIZ, capture_output=True, text=True, timeout=900)
    assert hecho.returncode in (0, 1), hecho.stderr[-3000:]
    return hecho.stdout


def test_d_la_ventana_real_nace_apagada_y_enciende_los_siete_al_correr(ventana_real):
    _salida, r = ventana_real
    antes = r["antes"]
    assert set(antes["exportadores"]) >= {"html_resumida", "pdf_resumida"}
    assert len(antes["exportadores"]) == 7
    for nombre, estado in antes["exportadores"].items():
        assert not estado["encendido"], nombre
        assert estado["motivo"] == r["motivo_sin_corrida"], nombre
    assert antes["rotulo"] == f"No disponible: {r['motivo_sin_corrida']}"
    assert antes["panel"] == {"texto": "", "motivo": r["motivo_sin_corrida_cabezal"]}

    t = r["tras_correr"]
    assert t["informe"], t["error_visible"]
    assert all(e["encendido"] for e in t["exportadores"].values())
    assert t["panel"]["motivo"] == ""
    assert _palabras(t["panel"]["texto"].splitlines()) == _palabras(t["lineas_de_la_cli"])

    i = r["tras_invalidar"]
    assert i["informe_es_None"]
    for nombre, estado in i["exportadores"].items():
        assert not estado["encendido"] and estado["motivo"] == r["motivo_hidrologia_cambiada"]
    assert i["panel"]["texto"] == "" and r["motivo_hidrologia_cambiada"] in i["panel"]["motivo"]

    f = r["tras_fallo"]
    assert f["informe_es_None"]
    for estado in f["exportadores"].values():
        assert not estado["encendido"] and estado["motivo"] == r["motivo_corrida_fallida"]
    assert f["panel"]["texto"] == "" and r["motivo_corrida_fallida"] in f["panel"]["motivo"]


def test_d_el_panel_de_la_ventana_es_el_bloque_que_la_cli_imprime(ventana_real, tmp_path,
                                                                  informe_cabezal):
    """
    «Ni una palabra distinta de la CLI», medido contra la CLI DE VERDAD: el
    bloque del cabezal del proyecto que `cli.py` imprime para las mismas
    entradas de la corrida de referencia, y el de `correr_referencia` en este
    proceso.
    """
    _salida, r = ventana_real
    panel = _palabras(r["tras_correr"]["panel"]["texto"].splitlines())
    stdout = _cli_de_la_referencia(_referencia("expediente_cabezal"), tmp_path)
    assert panel == _palabras(_bloque_del_cabezal_en_la_salida_de_la_cli(stdout))
    assert panel == _palabras(cli._lineas_cabezal(informe_cabezal.cabezal))
    assert any(l.startswith("Cadena sismica") for l in panel)


def test_d_a_perfil_el_panel_de_la_ventana_dice_lo_de_la_cli(ventana_real, informe_perfil):
    _salida, r = ventana_real
    p = r["perfil"]
    assert p["informe"] and p["alcance"] == cli.ALCANCE_PERFIL, p["error_visible"]
    panel = _palabras(p["panel"]["texto"].splitlines())
    assert panel == _palabras(p["lineas_de_la_cli"])
    assert panel == _palabras(cli._lineas_cabezal(informe_perfil.cabezal))


def _filas_de_trazabilidad(html):
    bloque = re.search(r'<div class="trazabilidad">(.*?)</div>', html, re.S).group(1)
    return {th.strip(): " ".join(td.split())
            for th, td in re.findall(r"<th>(.*?)</th>\s*<td[^>]*>(.*?)</td>", bloque, re.S)}


def test_d_el_html_resumido_de_la_ventana_lleva_el_encabezado_de_la_completa(ventana_real):
    salida, _r = ventana_real
    completa = (salida / "completa.html").read_text(encoding="utf-8")
    resumida = (salida / "resumida.html").read_text(encoding="utf-8")
    assert M11.TITULO_RESUMEN_VERIFICACIONES in resumida
    assert len(resumida) < len(completa)
    filas_c, filas_r = _filas_de_trazabilidad(completa), _filas_de_trazabilidad(resumida)
    assert set(filas_c) == set(filas_r) and len(filas_c) >= 9
    estado = "Estado del expediente"
    for fila in filas_c:
        if fila != estado:
            assert filas_c[fila] == filas_r[fila], fila
    # El estado: la misma marca, y cada vista dice donde esta su detalle.
    assert filas_c[estado].split("&mdash;")[0] == filas_r[estado].split("&mdash;")[0]
    # Y es la corrida de la ventana: su volcado lleva las mismas huellas.
    volcado = json.loads((salida / "ventana.json").read_text(encoding="utf-8"))
    assert volcado["expediente"]["csv_sha1"] in filas_r["SHA-1 del CSV de entrada"]


def test_d_el_pdf_resumido_de_la_ventana_sale_por_el_hijo(ventana_real):
    salida, r = ventana_real
    pdf = r["pdf_resumida"]
    if not r["weasyprint_disponible"]:
        assert pdf["html_navegador_existe"] and "weasyprint" in pdf["rotulo_final"]
        pytest.skip("weasyprint no esta operativo en el interprete de la ventana: "
                    "se midio la via del navegador y NO el proceso hijo")
    assert "--pdf-resumida" in pdf["comando"] and "--sesion" in pdf["comando"]
    assert "--pdf" not in pdf["comando"]
    durante = pdf["durante"]
    for nombre in ("pdf_resumida", "pdf"):
        assert not durante[nombre]["encendido"], nombre
        assert durante[nombre]["motivo"] == r["motivo_exportando_pdf"], nombre
    assert durante["cancelar"]
    assert durante["rotulo"].startswith("PDF resumido en marcha")
    assert pdf["termino_a_tiempo"] and pdf["estado_final"] == "terminado", pdf["rotulo_final"]
    assert pdf["existe"] and pdf["cabecera"] == "%PDF"
    assert pdf["despues"] == {"pdf_resumida": True, "pdf": True, "cancelar": False}
    assert pdf["rotulo_final"].startswith("Terminado")
    assert any(M11.ETAPA_PDF in p for p in pdf["progreso_visto"]), pdf["progreso_visto"]
    assert pdf["cancelacion_termino"] and pdf["estado_cancelado"] == "cancelado"
    assert pdf["cancelada_no_existe"] and pdf["rotulo_cancelado"].startswith("Cancelado")
    # El hijo formateo LA MISMA corrida que la ventana: desde VE-5 su JSON es
    # el de la ventana, con la hora incluida (no recalcula).
    hijo = json.loads((salida / "hijo_resumida.json").read_text(encoding="utf-8"))
    ventana = json.loads((salida / "ventana.json").read_text(encoding="utf-8"))
    assert ses.sin_marca_de_tiempo(hijo) == ses.sin_marca_de_tiempo(ventana)
    assert hijo == ventana
    # Y la ayuda del boton dice que el hijo no recalcula.
    import gui.exportacion_pdf as expdf
    assert expdf.AVISO_EL_HIJO_NO_RECALCULA in r["tras_correr"]["ayuda_pdf_resumida"]


def test_d_la_resumida_en_pdf_de_la_ventana_lleva_la_hidrologia(ventana_real):
    """
    Revision de UI-2, de punta a punta: la corrida de referencia CON
    hidrologia (`hidrologia_calculada`, los dos CSV en sus campos), su
    resumida en PDF por el hijo, y la sesion que el hijo recibio lleva las
    dos rutas; su JSON es el de la ventana salvo la hora, hidrologia incluida.
    """
    salida, r = ventana_real
    h = r["hidrologia"]
    assert h["informe"] and h["con_hidrologia"], h["error_visible"]
    if not r["weasyprint_disponible"]:
        pytest.skip("weasyprint no esta operativo en el interprete de la ventana: "
                    "no hubo hijo que mirar")
    assert h["termino_a_tiempo"] and h["estado_final"] == "terminado", h["rotulo_final"]
    assert h["existe"]
    referencia = _referencia("hidrologia_calculada")
    sesion = json.loads((salida / "hijo_hidrologia.sesion.json").read_text(encoding="utf-8"))
    assert sesion["cuencas"] == str(referencia.cuencas)
    assert sesion["estacion"] == str(referencia.estacion)
    hijo = json.loads((salida / "hijo_hidrologia.json").read_text(encoding="utf-8"))
    ventana = json.loads((salida / "ventana_hidrologia.json").read_text(encoding="utf-8"))
    assert "hidrologia" in hijo["expediente"]
    assert ses.sin_marca_de_tiempo(hijo) == ses.sin_marca_de_tiempo(ventana)
