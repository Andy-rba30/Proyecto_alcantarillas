"""
tests/apoyo/gui_ui4_recorrido_real.py
=====================================
UI-4, EL RECORRIDO DE EXTREMO A EXTREMO SOBRE LA VENTANA DE VERDAD: lo que la
cadena de interfaz llevo a la ventana (UI-1 a UI-3), probado junto y en el
orden en que lo usa el proyectista, sobre las tres corridas de referencia
(`src/indice_formulas.CORRIDAS_DE_REFERENCIA`) y el CSV de ejemplo.

    python -m tests.apoyo.gui_ui4_recorrido_real <salida> [--capturas <directorio>]

Se ejecuta desde la RAIZ del repositorio (las entradas se teclean RELATIVAS a
ella, como las nombran la linea base y la sesion v3 de prueba). Corre en un
proceso limpio por la razon de los demas apoyos de ventana real:
`test_gui_contrato.py` instala dobles de `tkinter`, y en un proceso limpio no
hay declaraciones de la suite (`conftest.py`). Todo son DATOS DE PRUEBA.

Que se recorre, en orden, y siempre por los botones de la ventana (los
dialogos de archivo devuelven la ruta que el recorrido elige, y los de aviso
se anotan):

  0. recien abierta: el grupo de exportacion apagado con su motivo, el panel
     del cabezal vacio con el suyo, y los siete botones de exportacion caben
     enteros en la geometria por defecto (ficha UI2-01, abierto (c));
  1. el CSV de ejemplo con los externos de la linea base y la luz de 2.75 m,
     a PERFIL y a EXPEDIENTE: los dos JSON y el cuadro resumen de la
     corrida de expediente, para compararlos con
     `tests/linea_base_familia_c/`;
  2. `perfil_guia` a perfil: CSV, externos y sitio por «Examinar...»; el
     detalle de la pestaña 3 y el panel del cabezal de la pestaña 4 (la
     Fase 9 diferida) con el texto de la CLI; y UN BARRIDO desde la pestaña
     2 (`n_celdas_cajon` = 1, 2), con su tabla --- y cuantas de sus lineas
     se ven sin mover el divisor --- y el estado de la ventana antes y
     despues;
  3. `expediente_cabezal` a expediente, con sus declaraciones tecleadas en
     la pestaña 2 y «Aplicar» (la nota, solo donde la puerta la exige): el
     detalle con la Fase 8 y el cabezal del punto, y el panel del cabezal
     del proyecto;
  4. `hidrologia_calculada` a expediente, con los dos CSV de la hidrologia:
     el detalle con el caudal CALCULADO y con la proteccion, la Fase 8 y el
     cabezal del punto; los SEIS exportadores por sus botones (los dos PDF
     por el proceso hijo, cuya sesion y JSON se guardan antes de que el
     directorio de trabajo se retire); y, a PERFIL y con la luz tecleada
     ---lo que «Nuevo proyecto» no deja---, EJECUTAR, «Guardar sesion»,
     «Nuevo proyecto», «Cargar sesion» y EJECUTAR otra vez;
  5. la sesion de formato 3 de prueba (`tests/fixtures/sesion_v3/`):
     abierta, ejecutada --- reproduce la corrida que trae embebida --- y
     guardada otra vez, ya en el formato actual;
  6. cerrar la ventana PRINCIPAL con un PDF en marcha: el hijo termina y su
     directorio de trabajo no queda en el temporal (ficha UI3-02, abierto
     (3)).

Con `--capturas`, ademas, las capturas de las cuatro pestañas y de la
ventana del barrido, en PNG, con ImageMagick (`import -window root` sobre la
region de la ventana), a `GEOMETRIA_DE_LAS_CAPTURAS`: son las de
`docs/capturas_interfaz/`, y se regeneran con este mismo comando bajo
`xvfb-run`. Lo que se ve en ellas lo produce el programa; este apoyo solo
elige que pestaña, que fila y que criterio estan a la vista.

Lo que el recorrido mide lo escribe en `<salida>/recorrido_ui4.json`, con los
volcados y los archivos exportados al lado; las comparaciones con la CLI y
con la linea base las hace `tests/test_ui4_recorrido_ventana.py`.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

import cli                                             # noqa: E402
from src import comparador as compa                    # noqa: E402
from src import criterios_adoptados as ca              # noqa: E402
from src import datos_sitio as ds                      # noqa: E402
from src import declaracion as dec                     # noqa: E402
from src import indice_formulas as ind                 # noqa: E402
from src import sesion as ses                          # noqa: E402

# --- Las entradas, RELATIVAS a la raiz -----------------------------------
CSV_EJEMPLO = "tests/ejemplo_puntos.csv"
EXTERNOS_LINEA_BASE = "tests/linea_base_familia_c/entradas_ampliadas.json"
LUZ_LINEA_BASE = "2.75"
# Las dos corridas del CSV de ejemplo y el archivo de la linea base que
# `tests/linea_base_familia_c/regenerar.sh` escribe con las MISMAS entradas.
CORRIDAS_DEL_EJEMPLO = (("perfil", "informe_perfil_ancho.json"),
                        ("expediente", "informe_expediente.json"))
RESUMEN_DE_LA_LINEA_BASE = "resumen_expediente.csv"
SESION_V3 = "tests/fixtures/sesion_v3/sesion_v3_partida.json"
NOTA = "DATOS DE PRUEBA: recorrido de UI-4 (la nota que la puerta exige)"
PROYECTO = "DATOS DE PRUEBA - recorrido de UI-4"
# El barrido de la guia de perfil (seccion 6 de docs/guia_perfil.md).
CLAVE_DEL_BARRIDO = "n_celdas_cajon"
VALORES_DEL_BARRIDO = (1, 2)
# El ciclo guardar / «Nuevo proyecto» / cargar se hace con un alcance y una
# bandera de la pestaña 1 que NO son los que deja «Nuevo proyecto» (perfil y la
# luz, con coma decimal; la luz es la misma que el JSON de la corrida trae).
ALCANCE_DEL_CICLO = cli.ALCANCE_PERFIL
BANDERAS_DEL_CICLO = {"luz_m": "3,0"}
# Los puntos cuyo detalle se lee en la pestaña 3, por corrida.
DETALLES = {"perfil_guia": ("C-01",),
            "expediente_cabezal": ("A-01",),
            "hidrologia_calculada": ("A-01", "C-01")}
# Las capturas: geometria (cabe en la pantalla de 1280x1024 que `xvfb-run`
# levanta por defecto) y nombres de archivo.
GEOMETRIA_DE_LAS_CAPTURAS = "1280x1000+0+0"
CAPTURAS = ("pestana_1_datos.png", "pestana_2_criterios.png",
            "pestana_3_resultados.png", "pestana_4_resumen.png",
            "ventana_barrido.png")
TOPE_S = 600


def corrida(nombre):
    return next(c for c in ind.CORRIDAS_DE_REFERENCIA if c.nombre == nombre)


def relativa(ruta):
    """La ruta de una entrada de referencia, relativa a la raiz; '' si no hay."""
    return "" if ruta is None else Path(ruta).resolve().relative_to(RAIZ).as_posix()


def argumentos_de_la_cli(referencia):
    """
    Las banderas de `cli.py` con las MISMAS entradas que el recorrido teclea en
    la ventana para `referencia` (las rutas relativas incluidas): con ellas la
    CLI y la ventana tienen que escribir el mismo JSON.
    """
    args = [relativa(referencia.csv), "--alcance", referencia.alcance,
            "--datos-externos", relativa(referencia.externos)]
    if referencia.sitio is not None:
        args += ["--datos-sitio", relativa(referencia.sitio)]
    if referencia.cuencas is not None:
        args += ["--cuencas", relativa(referencia.cuencas),
                 "--estacion", relativa(referencia.estacion)]
    for clave, valor in referencia.declaraciones.items():
        args += ["--declarar", f"{clave}={valor!r}"]
    return args


# --- Lectura de la ventana ------------------------------------------------
def _exportadores(ventana):
    import gui.app as gapp
    return {nombre: {"encendido": str(getattr(ventana, nombre).cget("state")) == "normal",
                     "motivo": getattr(ventana, nombre).motivo}
            for nombre in gapp.BOTONES_DE_EXPORTACION}


def _panel_del_cabezal(ventana):
    return {"texto": ventana.txt_cabezal.get("1.0", "end-1c"),
            "motivo": ventana.lbl_cabezal.cget("text")}


def _caben_los_exportadores(ventana, raiz):
    """
    Cada boton del grupo de exportacion, en la geometria de la ventana:
    mapeado, entero (con el ancho que pide) y dentro del area visible de la
    pestaña 4 (el lienzo de su `MarcoScroll`).
    """
    import gui.app as gapp
    ventana.nb.select(ventana.tab_resumen)
    raiz.update()
    lienzo = ventana.tab_resumen.canvas
    derecha = lienzo.winfo_rootx() + lienzo.winfo_width()
    salida = {}
    for nombre in gapp.BOTONES_DE_EXPORTACION:
        boton = getattr(ventana, nombre).boton
        salida[nombre] = {
            "mapeado": bool(boton.winfo_ismapped()),
            "entero": boton.winfo_width() >= boton.winfo_reqwidth(),
            "dentro": boton.winfo_rootx() + boton.winfo_width() <= derecha}
    return salida


def _botones_por_texto(raiz):
    """Los botones ttk de la ventana, por su texto (los de la barra superior)."""
    encontrados = {}
    pendientes = [raiz]
    while pendientes:
        widget = pendientes.pop()
        pendientes.extend(widget.winfo_children())
        if widget.winfo_class() == "TButton":
            encontrados.setdefault(str(widget.cget("text")), widget)
    return encontrados


def _pulsar_examinar(ventana, raiz, metodo, ruta):
    """
    Un «Examinar...» de la pestaña 1: el boton cuyo comando es `metodo`
    (Tkinter registra el comando con el nombre de la funcion al final), con
    el dialogo de archivo devolviendo `ruta`.
    """
    import gui.app as gapp
    pendientes = [ventana.tab_datos]
    while pendientes:
        widget = pendientes.pop()
        pendientes.extend(widget.winfo_children())
        if widget.winfo_class() == "TButton" and str(widget.cget("command")).endswith(metodo):
            gapp.filedialog.askopenfilename = lambda **kw: ruta
            widget.invoke()
            raiz.update()
            return True
    return False


def _campos_de_la_pestana_1(ventana):
    """Lo que una sesion guarda y repone de la pestaña 1: rutas, alcance y banderas."""
    campos = {nombre: getattr(ventana, nombre).get() for nombre in (
        "proyecto_var", "csv_var", "datos_externos_var", "datos_sitio_var",
        "cuencas_var", "estacion_var", "alcance_var")}
    campos["externos"] = {clave: var.get() for clave, var in ventana.externos_vars.items()}
    return campos


def _volcar(ventana, destino):
    destino.write_text(json.dumps(ventana.volcado_de_la_corrida, ensure_ascii=False,
                                  allow_nan=False, indent=1), encoding="utf-8")


def _ejecutar(ventana, raiz):
    ventana.btn_ejecutar.boton.invoke()
    raiz.update()
    return ventana.informe


def _seleccionar_criterio(ventana, raiz, clave):
    ventana.nb.select(ventana.tab_criterios)
    ventana.filtro_texto_var.set("")
    raiz.update()
    ventana.tree_criterios_todos.selection_set(clave)
    ventana.tree_criterios_todos.see(clave)
    raiz.update()


def _declarar_por_la_pestana_2(ventana, raiz, clave, valor):
    """
    Teclea `valor` en «Valor nuevo» y pulsa «Aplicar solo a esta corrida».
    Si la puerta lo rechaza pidiendo la nota (un dato de ensayo, una adopcion
    en un criterio de tabla), la escribe en el editor y pulsa otra vez: lo
    que haria el proyectista al leer el rechazo.
    """
    _seleccionar_criterio(ventana, raiz, clave)
    # Un texto se teclea tal cual (sin comillas); lo demas, como se escribe
    # en Python, que es lo que el campo lee (`interpretar_texto_declarado`).
    ventana.valor_declarado_var.set(valor if isinstance(valor, str) else repr(valor))
    raiz.update()
    ventana.btn_aplicar_corrida.boton.invoke()
    raiz.update()
    primer_rotulo = ventana.lbl_estado_criterio.cget("text")
    con_nota = False
    if clave not in ca.valores_dinamicos() and ventana.editor is not None:
        ventana.editor.nota_var.set(NOTA)
        raiz.update()
        ventana.btn_aplicar_corrida.boton.invoke()
        raiz.update()
        con_nota = True
    declarado = ca.valores_dinamicos().get(clave, None)
    return {"declarado": clave in ca.valores_dinamicos(),
            "mismo_valor": repr(declarado) == repr(valor),
            "con_nota": con_nota,
            "primer_rotulo": primer_rotulo if con_nota else "",
            "rotulo": ventana.lbl_estado_criterio.cget("text")}


def _poner_entradas(ventana, raiz, referencia):
    """Los campos de la pestaña 1 por sus «Examinar...», y el alcance."""
    ventana.nb.select(ventana.tab_datos)
    hechos = {"csv": _pulsar_examinar(ventana, raiz, "_elegir_csv", relativa(referencia.csv)),
              "externos": _pulsar_examinar(ventana, raiz, "_elegir_datos_externos",
                                           relativa(referencia.externos))}
    if referencia.sitio is not None:
        hechos["sitio"] = _pulsar_examinar(ventana, raiz, "_elegir_datos_sitio",
                                           relativa(referencia.sitio))
    if referencia.cuencas is not None:
        hechos["cuencas"] = _pulsar_examinar(ventana, raiz, "_elegir_cuencas",
                                             relativa(referencia.cuencas))
        hechos["estacion"] = _pulsar_examinar(ventana, raiz, "_elegir_estacion",
                                              relativa(referencia.estacion))
    ventana.alcance_var.set(referencia.alcance)
    raiz.update()
    return hechos


def _detalle(ventana, raiz, id_punto):
    ventana.nb.select(ventana.tab_puntos)
    ventana.tree_puntos.selection_set(id_punto)
    ventana.tree_puntos.see(id_punto)
    raiz.update()
    punto = next(p for p in ventana.informe.puntos if p.punto.id == id_punto)
    return {"texto": ventana.txt_detalle.get("1.0", "end-1c"),
            "lineas_de_la_cli": list(cli._lineas_punto(punto)),
            "calculado": bool(punto.caudal is not None and punto.caudal.calculado),
            "dimensionado": punto.dimensionado}


def _lo_de_la_corrida(ventana, raiz, nombre, salida):
    informe = ventana.informe
    medido = {"informe": informe is not None,
              "error_visible": ventana.lbl_error_datos.cget("text")}
    if informe is None:
        return medido
    _volcar(ventana, salida / f"{nombre}.json")
    medido["alcance"] = informe.alcance
    medido["con_hidrologia"] = informe.hidrologia is not None
    medido["exportadores"] = _exportadores(ventana)
    medido["detalles"] = {id_punto: _detalle(ventana, raiz, id_punto)
                          for id_punto in DETALLES.get(nombre, ())}
    ventana.nb.select(ventana.tab_resumen)
    raiz.update()
    medido["panel_del_cabezal"] = _panel_del_cabezal(ventana)
    medido["lineas_del_cabezal_de_la_cli"] = list(cli._lineas_cabezal(informe.cabezal))
    return medido


def _lineas_a_la_vista(texto, raiz):
    """
    Cuantas lineas de un `Text` se ven en la pantalla sin desplazar nada:
    las que Tk dibuja (`dlineinfo` no es None) con el widget mapeado. Un
    widget en un panel de alto cero no muestra ninguna.
    """
    raiz.update()
    if not texto.winfo_ismapped():
        return 0
    total = int(texto.index("end-1c").split(".")[0])
    return sum(1 for n in range(1, total + 1) if texto.dlineinfo(f"{n}.0") is not None)


# --- Los procesos hijos del PDF --------------------------------------------
def _esperar_pdf(ventana, raiz):
    inicio = time.monotonic()
    while ventana.proceso_pdf is not None and not ventana.proceso_pdf.estado.terminal:
        raiz.update()
        time.sleep(0.05)
        if time.monotonic() - inicio > TOPE_S:
            return False
    for _ in range(10):
        raiz.update()
        time.sleep(0.05)
    return True


def _esperar_barrido(vb, raiz):
    limite = time.monotonic() + TOPE_S
    while vb.proceso is not None and not vb.proceso.estado.terminal:
        if time.monotonic() > limite:
            return False
        raiz.update()
        time.sleep(0.05)
    raiz.update()
    return True


# --- Las capturas ------------------------------------------------------------
def _capturar(ventana_de_nivel, destino):
    """
    La region de una ventana de nivel superior, tal como esta en la pantalla
    (sin gestor de ventanas no hay marco que recortar), con ImageMagick.
    """
    ventana_de_nivel.update_idletasks()
    ventana_de_nivel.update()
    x, y = ventana_de_nivel.winfo_rootx(), ventana_de_nivel.winfo_rooty()
    ancho, alto = ventana_de_nivel.winfo_width(), ventana_de_nivel.winfo_height()
    subprocess.run(["import", "-window", "root", "-crop", f"{ancho}x{alto}+{x}+{y}",
                    "+repage", str(destino)], check=True, timeout=120,
                   capture_output=True)
    return destino.name


def _al_panel_del_cabezal(ventana, raiz):
    """La pestaña 4 desplazada hasta el panel «Cabezal del proyecto»."""
    interior = ventana.tab_resumen.interior
    raiz.update()
    arriba = ventana.lbl_cabezal.winfo_rooty() - interior.winfo_rooty()
    alto = max(interior.winfo_height(), 1)
    # El titulo del panel queda a la vista: se sube el alto de dos lineas.
    margen = 2 * ventana.lbl_cabezal.winfo_height()
    ventana.tab_resumen.canvas.yview_moveto(max(arriba - margen, 0) / alto)
    raiz.update()


# --- El recorrido ------------------------------------------------------------
def main(salida: Path, capturas=None) -> int:
    import ttkbootstrap as tb
    import webbrowser

    import gui.app as gapp
    import gui.ventana_barrido as gvb
    from src.modulos import M11_reporte as M11

    salida.mkdir(parents=True, exist_ok=True)
    if capturas is not None:
        capturas.mkdir(parents=True, exist_ok=True)
    dialogos = []
    gapp.messagebox.showinfo = lambda titulo, texto, *a, **k: dialogos.append(
        ["info", titulo, texto])
    gapp.messagebox.showerror = lambda titulo, texto, *a, **k: dialogos.append(
        ["error", titulo, texto])
    gapp.messagebox.askyesno = lambda *a, **k: True
    webbrowser.open = lambda *a, **k: True
    # El JSON y la sesion de cada hijo del PDF se guardan ANTES de que
    # `_terminar_pdf` retire su directorio de trabajo: son la prueba de que
    # el hijo corrio la misma obra que la ventana.
    limpiar = gapp.expdf.ProcesoPdf.limpiar
    prefijo = {"valor": "hijo"}

    def _limpiar_guardando(proceso):
        for origen, sufijo in ((proceso.ruta_json, ".json"),
                               (proceso.ruta_sesion, ".sesion.json")):
            if origen.is_file():
                shutil.copy(origen, salida / f"{prefijo['valor']}{sufijo}")
        limpiar(proceso)

    gapp.expdf.ProcesoPdf.limpiar = _limpiar_guardando

    r = {"motivo_sin_corrida": gapp.MOTIVO_SIN_CORRIDA,
         "motivo_sin_corrida_cabezal": gapp.MOTIVO_SIN_CORRIDA_CABEZAL,
         "weasyprint_disponible": M11.weasyprint_disponible(),
         "capturas": {}}
    raiz = tb.Window(themename="litera")
    destruida = False
    try:
        ventana = gapp.ExpedienteApp(raiz)
        ventana.proyecto_var.set(PROYECTO)
        raiz.update()
        # La que la ventana se da al abrirse (`ExpedienteApp.__init__`), leida
        # ya realizada: las capturas cambian de geometria y la reponen.
        geometria_por_defecto = raiz.geometry().split("+")[0]
        r["geometria_por_defecto"] = geometria_por_defecto
        barra = _botones_por_texto(raiz)

        # 0. Recien abierta.
        r["recien_abierta"] = {"exportadores": _exportadores(ventana),
                               "panel_del_cabezal": _panel_del_cabezal(ventana),
                               "caben": _caben_los_exportadores(ventana, raiz)}

        # 1. El CSV de ejemplo, a perfil y a expediente.
        ejemplo = {}
        _pulsar_examinar(ventana, raiz, "_elegir_csv", CSV_EJEMPLO)
        _pulsar_examinar(ventana, raiz, "_elegir_datos_externos", EXTERNOS_LINEA_BASE)
        ventana.externos_vars["luz_m"].set(LUZ_LINEA_BASE)
        for alcance, _archivo in CORRIDAS_DEL_EJEMPLO:
            ventana.alcance_var.set(alcance)
            raiz.update()
            informe = _ejecutar(ventana, raiz)
            ejemplo[alcance] = {"informe": informe is not None,
                                "error_visible": ventana.lbl_error_datos.cget("text")}
            if informe is not None:
                _volcar(ventana, salida / f"ejemplo_{alcance}.json")
        destino_csv = salida / "ejemplo_expediente.resumen.csv"
        gapp.filedialog.asksaveasfilename = lambda **kw: str(destino_csv)
        ventana.btn_csv.boton.invoke()
        raiz.update()
        ejemplo["resumen_escrito"] = destino_csv.is_file()
        r["ejemplo"] = ejemplo
        ventana.externos_vars["luz_m"].set("")

        # 2. perfil_guia, a perfil; el barrido desde la pestaña 2.
        referencia = corrida("perfil_guia")
        r["perfil_guia"] = {"examinar": _poner_entradas(ventana, raiz, referencia)}
        _ejecutar(ventana, raiz)
        r["perfil_guia"].update(_lo_de_la_corrida(ventana, raiz, "perfil_guia", salida))
        informe = ventana.informe
        volcado_antes = ses.sin_marca_de_tiempo(cli.informe_json(informe))
        estado_antes = dec.estado_de_sesion()
        sitio_antes = dec.estado_de_sitio_de_sesion()
        exportadores_antes = _exportadores(ventana)
        _seleccionar_criterio(ventana, raiz, CLAVE_DEL_BARRIDO)
        filas_antes = [list(ventana.tree_criterios_todos.item(i, "values"))
                       for i in ventana.tree_criterios_todos.get_children()]
        barrido = {"boton_encendido": str(ventana.btn_barrido.cget("state")) == "normal"}
        if capturas is not None:
            raiz.geometry(GEOMETRIA_DE_LAS_CAPTURAS)
            raiz.update()
            r["capturas"]["pestana_2_criterios.png"] = _capturar(
                raiz, capturas / "pestana_2_criterios.png")
        ventana.btn_barrido.boton.invoke()
        raiz.update()
        vb = ventana.ventana_barrido
        barrido["abierta"] = vb is not None
        if vb is not None:
            for valor in VALORES_DEL_BARRIDO:
                vb.editor.poner_valor(valor)
                raiz.update()
                vb.anadir_valor()
            vb.btn_correr.boton.invoke()
            raiz.update()
            barrido["termino_a_tiempo"] = _esperar_barrido(vb, raiz)
            barrido["estado"] = None if vb.proceso is None else vb.proceso.estado.value
            barrido["detalle"] = "" if vb.proceso is None else vb.proceso.detalle
            barrido["lineas"] = vb.txt_tabla.get("1.0", "end-1c").splitlines()
            barrido["lineas_a_la_vista"] = _lineas_a_la_vista(vb.txt_tabla, raiz)
            # La captura, con la tabla recien pintada y ANTES de guardar el
            # JSON: el rotulo diria entonces la ruta de trabajo del recorrido.
            if capturas is not None:
                r["capturas"]["ventana_barrido.png"] = _capturar(
                    vb.top, capturas / "ventana_barrido.png")
            destino_barrido = salida / "barrido_ventana.json"
            gvb.filedialog.asksaveasfilename = lambda **kw: str(destino_barrido)
            vb.btn_guardar.boton.invoke()
            raiz.update()
            barrido["json_guardado"] = destino_barrido.is_file()
            vb.cerrar()
            raiz.update()
        if capturas is not None:
            raiz.geometry(geometria_por_defecto)
            raiz.update()
        barrido["despues"] = {
            "ventana_barrido_es_None": ventana.ventana_barrido is None,
            "estado_de_sesion_igual": dec.estado_de_sesion() == estado_antes,
            "sitio_igual": dec.estado_de_sitio_de_sesion() == sitio_antes,
            "informe_es_el_mismo": ventana.informe is informe,
            "volcado_igual": ses.sin_marca_de_tiempo(cli.informe_json(ventana.informe))
            == volcado_antes,
            "exportadores_iguales": _exportadores(ventana) == exportadores_antes,
            "filas_de_la_pestana_2_iguales": [
                list(ventana.tree_criterios_todos.item(i, "values"))
                for i in ventana.tree_criterios_todos.get_children()] == filas_antes}
        r["barrido"] = barrido

        # 3. expediente_cabezal, con sus declaraciones por la pestaña 2.
        referencia = corrida("expediente_cabezal")
        r["expediente_cabezal"] = {"examinar": _poner_entradas(ventana, raiz, referencia)}
        r["expediente_cabezal"]["declaraciones"] = {
            clave: _declarar_por_la_pestana_2(ventana, raiz, clave, valor)
            for clave, valor in referencia.declaraciones.items()}
        _ejecutar(ventana, raiz)
        r["expediente_cabezal"].update(
            _lo_de_la_corrida(ventana, raiz, "expediente_cabezal", salida))

        # 4. hidrologia_calculada, con los dos CSV de la hidrologia. Primero
        #    se retira lo declarado para la corrida anterior, por «Quitar».
        for clave in list(ca.valores_dinamicos()):
            _seleccionar_criterio(ventana, raiz, clave)
            ventana.btn_quitar_declarado.boton.invoke()
            raiz.update()
        referencia = corrida("hidrologia_calculada")
        h = {"retirado_lo_anterior": not ca.valores_dinamicos(),
             "examinar": _poner_entradas(ventana, raiz, referencia)}
        h["declaraciones"] = {
            clave: _declarar_por_la_pestana_2(ventana, raiz, clave, valor)
            for clave, valor in referencia.declaraciones.items()}
        _ejecutar(ventana, raiz)
        h.update(_lo_de_la_corrida(ventana, raiz, "hidrologia_calculada", salida))
        r["hidrologia_calculada"] = h

        if capturas is not None and ventana.informe is not None:
            raiz.geometry(GEOMETRIA_DE_LAS_CAPTURAS)
            raiz.update()
            ventana.nb.select(ventana.tab_datos)
            ventana.tab_datos.canvas.yview_moveto(0)
            r["capturas"]["pestana_1_datos.png"] = _capturar(
                raiz, capturas / "pestana_1_datos.png")
            _detalle(ventana, raiz, "A-01")
            r["capturas"]["pestana_3_resultados.png"] = _capturar(
                raiz, capturas / "pestana_3_resultados.png")
            ventana.nb.select(ventana.tab_resumen)
            _al_panel_del_cabezal(ventana, raiz)
            r["capturas"]["pestana_4_resumen.png"] = _capturar(
                raiz, capturas / "pestana_4_resumen.png")
            ventana.tab_resumen.canvas.yview_moveto(0)
            raiz.geometry(geometria_por_defecto)
            raiz.update()

        # 4b. Los SEIS exportadores, por sus botones.
        exportados = {}
        for nombre, boton, archivo in (
                ("json", ventana.btn_json, "exportado.json"),
                ("html", ventana.btn_html, "completa.html"),
                ("csv", ventana.btn_csv, "resumen.csv"),
                ("html_resumida", ventana.btn_html_resumida, "resumida.html")):
            destino = salida / archivo
            gapp.filedialog.asksaveasfilename = lambda _d=destino, **kw: str(_d)
            boton.boton.invoke()
            raiz.update()
            exportados[nombre] = {"archivo": archivo, "escrito": destino.is_file()}
        for nombre, boton, archivo in (("pdf", ventana.btn_pdf, "completa.pdf"),
                                       ("pdf_resumida", ventana.btn_pdf_resumida,
                                        "resumida.pdf")):
            destino = salida / archivo
            gapp.filedialog.asksaveasfilename = lambda _d=destino, **kw: str(_d)
            prefijo["valor"] = f"hijo_{nombre}"
            boton.boton.invoke()
            raiz.update()
            medido = {"archivo": archivo}
            if r["weasyprint_disponible"]:
                medido["comando"] = list(ventana.proceso_pdf.comando)
                medido["termino_a_tiempo"] = _esperar_pdf(ventana, raiz)
                medido["estado"] = ventana.proceso_pdf.estado.value
                medido["rotulo"] = ventana.lbl_estado_pdf.cget("text")
            else:
                medido["html_del_navegador"] = destino.with_suffix(".html").is_file()
            medido["escrito"] = destino.is_file()
            medido["cabecera"] = (destino.read_bytes()[:4].decode("latin-1")
                                  if destino.is_file() else "")
            medido["con_trailer"] = (destino.is_file()
                                     and b"%%EOF" in destino.read_bytes()[-2048:])
            exportados[nombre] = medido
        r["exportados"] = exportados

        # 4c. Guardar sesion, Nuevo proyecto, Cargar sesion y EJECUTAR otra vez,
        #     con un alcance y una bandera DISTINTOS de lo que «Nuevo proyecto»
        #     deja (revision de UI-4, H2): con la sesion de expediente y sin
        #     banderas, «repuesto al cargar» y «quedo por defecto» eran lo
        #     mismo, y quitar de «Cargar sesion» la linea que repone el
        #     alcance sobrevivia al recorrido. La corrida que el ciclo tiene
        #     que reproducir es la de ese estado, hecha antes de guardar.
        ventana.alcance_var.set(ALCANCE_DEL_CICLO)
        for campo, texto in BANDERAS_DEL_CICLO.items():
            ventana.externos_vars[campo].set(texto)
        raiz.update()
        _ejecutar(ventana, raiz)
        ciclo = {"antes": {"informe": ventana.informe is not None,
                           "error_visible": ventana.lbl_error_datos.cget("text")}}
        if ventana.informe is not None:
            _volcar(ventana, salida / "ciclo_antes.json")
        estado_guardado = dec.estado_de_sesion()
        sitio_guardado = dec.estado_de_sitio_de_sesion()
        campos_guardados = _campos_de_la_pestana_1(ventana)
        ciclo["campos_guardados"] = campos_guardados
        guardada = salida / "sesion_guardada.json"
        gapp.filedialog.asksaveasfilename = lambda **kw: str(guardada)
        barra["Guardar sesion"].invoke()
        raiz.update()
        data = json.loads(guardada.read_text(encoding="utf-8"))
        ciclo.update({"formato_version": data["formato_version"],
                      "cuencas": data.get("cuencas"), "estacion": data.get("estacion"),
                      "errores": ses.errores_de_sesion(data)})
        barra["Nuevo proyecto"].invoke()
        raiz.update()
        ciclo["tras_nuevo"] = {
            "campos": _campos_de_la_pestana_1(ventana),
            "declarados": sorted(ca.valores_dinamicos()),
            "sitio_declarado": sorted(ds.datos_declarados_en_caliente()),
            "informe_es_None": ventana.informe is None,
            "exportadores": _exportadores(ventana)}
        gapp.filedialog.askopenfilename = lambda **kw: str(guardada)
        barra["Cargar sesion"].invoke()
        raiz.update()
        ciclo["tras_cargar"] = {
            "campos": _campos_de_la_pestana_1(ventana),
            "estado_de_sesion_igual": dec.estado_de_sesion() == estado_guardado,
            "sitio_igual": dec.estado_de_sitio_de_sesion() == sitio_guardado,
            "informe_es_None": ventana.informe is None}
        _ejecutar(ventana, raiz)
        ciclo["corrida"] = {"informe": ventana.informe is not None,
                            "error_visible": ventana.lbl_error_datos.cget("text")}
        if ventana.informe is not None:
            _volcar(ventana, salida / "ciclo_despues.json")
        r["ciclo_de_sesion"] = ciclo

        # 5. La sesion de formato 3 de prueba.
        dialogos_antes = len(dialogos)
        v3 = json.loads((RAIZ / SESION_V3).read_text(encoding="utf-8"))
        gapp.filedialog.askopenfilename = lambda **kw: SESION_V3
        barra["Cargar sesion"].invoke()
        raiz.update()
        sesion_v3 = {
            "dialogos": dialogos[dialogos_antes:],
            "cuencas": ventana.cuencas_var.get(), "estacion": ventana.estacion_var.get(),
            "csv_igual": ventana.csv_var.get() == v3["csv"],
            "id_igual": ventana.sesion_id == v3["id"],
            "declarados": sorted(ca.valores_dinamicos())}
        _ejecutar(ventana, raiz)
        sesion_v3["informe"] = ventana.informe is not None
        sesion_v3["error_visible"] = ventana.lbl_error_datos.cget("text")
        if ventana.informe is not None:
            comparacion = compa.comparar(ventana.volcado_de_la_corrida,
                                         v3["corridas"][-1]["informe_json"])
            sesion_v3["reproduce"] = comparacion.iguales
            sesion_v3["comparacion"] = comparacion.lineas()[:6]
        reescrita = salida / "sesion_v3_reescrita.json"
        gapp.filedialog.asksaveasfilename = lambda **kw: str(reescrita)
        barra["Guardar sesion"].invoke()
        raiz.update()
        data = json.loads(reescrita.read_text(encoding="utf-8"))
        sesion_v3["reescrita"] = {"formato_version": data["formato_version"],
                                  "id_igual": data["id"] == v3["id"],
                                  "corridas": len(data["corridas"]),
                                  "errores": ses.errores_de_sesion(data)}
        r["sesion_v3"] = sesion_v3

        # 6. Cerrar la ventana PRINCIPAL con un PDF en marcha.
        cierre = {}
        if r["weasyprint_disponible"] and ventana.informe is not None:
            destino = salida / "nunca.pdf"
            gapp.filedialog.asksaveasfilename = lambda **kw: str(destino)
            prefijo["valor"] = "hijo_al_cerrar"
            ventana.btn_pdf.boton.invoke()
            raiz.update()
            proceso = ventana.proceso_pdf
            cierre["en_marcha_al_cerrar"] = (proceso is not None
                                             and not proceso.estado.terminal)
            raiz.destroy()
            destruida = True
            if proceso is not None:
                cierre["hijo_terminado"] = proceso._proceso.poll() is not None
                cierre["carpeta_retirada"] = not proceso.directorio_trabajo.exists()
                cierre["destino_intacto"] = not destino.exists()
                if proceso._proceso.poll() is None:
                    proceso.cancelar()          # que la medida no deje huerfanos
                    proceso._proceso.wait(timeout=TOPE_S)
                shutil.rmtree(proceso.directorio_trabajo, ignore_errors=True)
        r["cierre_con_pdf_en_marcha"] = cierre
        codigo = 0
    except Exception:                                   # el recorrido no se calla
        r["error"] = traceback.format_exc()
        codigo = 1
    finally:
        if not destruida:
            raiz.destroy()
    # Los de TODO el recorrido, el cierre incluido (revision de UI-4).
    r["dialogos_de_error"] = [d for d in dialogos if d[0] == "error"]
    (salida / "recorrido_ui4.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    if "error" in r:
        print(r["error"])
    return codigo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="python -m tests.apoyo.gui_ui4_recorrido_real")
    parser.add_argument("salida", type=Path)
    parser.add_argument("--capturas", type=Path, default=None)
    argumentos = parser.parse_args()
    raise SystemExit(main(argumentos.salida, argumentos.capturas))
