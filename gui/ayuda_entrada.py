# -*- coding: utf-8 -*-
"""
gui/ayuda_entrada.py
====================
LA VENTANA de ayuda de la pestana 1: que tiene que traer el CSV de Sec. 1.2, y
que acepta el JSON de `--datos-externos`.

Este archivo PINTA. No sabe ni una columna, ni una unidad, ni que celda puede
ir vacia: todo se lo da `src/ayuda_entrada.py`, que lo deriva de
`M0_carga.COLUMNAS`, `variables_entrada.VARIABLES`, `M0_carga.VACIOS_ADMITIDOS`
y `cli.CLAVES_EXTERNAS`. El reparto es el mismo de `gui/ventana_normativa.py`
y por la misma razon: el contenido se compara campo a campo sin escritorio, en
`tests/test_ayuda_entrada.py`, y aqui queda el cableado de widgets.

SI ESTA AYUDA DICE ALGO QUE NO ES CIERTO, NO SE ARREGLA AQUI. Se arregla en el
sitio de donde el dato sale --- el `concepto` de la columna en
`variables_entrada`, el grupo de `VACIOS_ADMITIDOS` en `M0_carga` ---, y
entonces la ayuda cambia sola. Escribir la correccion en este archivo crearia
la segunda version del dato, que es exactamente lo que la ayuda derivada
existe para no tener.

Las dos pestanas
----------------
Son dos porque son dos archivos distintos del expediente, y estan en la MISMA
ventana porque se leen juntas: `Q_m3s` y `S_cauce` son columna del CSV y ademas
clave del JSON --- van vacias en la fila de un cruce de canal y entran por el
JSON cuando el Tablero 3.1 las entrega ---, y esa vuelta es imposible de contar
en dos ventanas que no se ven a la vez. El icono de cada campo abre la ventana
en SU pestana; una vez abierta, el usuario cruza.

Reutiliza `gui/componentes.py`: el `Tooltip`, y el `BotonAyuda` con que la
ventana principal la llama. NO usa `MarcoScroll`: sus dos pestanas reparten el
alto con un `PanedWindow` y un `Treeview`, que traen su propio scroll.
"""

from __future__ import annotations

import sys
from pathlib import Path

import tkinter as tk
from tkinter import ttk

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
for _ruta in (RAIZ, SRC):
    if str(_ruta) not in sys.path:
        sys.path.insert(0, str(_ruta))

import ayuda_entrada as ay  # noqa: E402
from modelos import Familia  # noqa: E402

from gui.componentes import COLOR_AVISO, COLOR_OK, Tooltip  # noqa: E402

# Los nombres de las dos pestanas, que ademas son los dos modos con que se
# puede abrir la ventana. Son rotulos de pantalla: lo que la ventana AFIRMA
# sale siempre de `src/ayuda_entrada.py`.
PESTANA_CSV = "csv"
PESTANA_JSON = "json"

TITULO = "Que tiene que traer el expediente"

# Anchos de columna del Treeview, en pixeles. Geometria de presentacion.
_ANCHOS_CSV = (
    ("clave", "Columna (encabezado exacto)", 210, "w"),   # literal-ok: ancho en px
    ("unidad", "Unidad", 70, "center"),                   # literal-ok: ancho en px
    # 240 y no 210: «puede ir vacia solo en Familia C» es la celda mas larga
    # de esta columna y con 210 se cortaba en la propia familia, que es el
    # dato. Medido sobre la ventana real.
    ("obligatoria", "Obligatoria", 240, "w"),             # literal-ok: ancho en px
    ("concepto", "Concepto", 420, "w"),                   # literal-ok: ancho en px
)
_ANCHOS_JSON = (
    ("clave", "Clave", 170, "w"),                         # literal-ok: ancho en px
    ("familias", "Familias que la usan", 190, "w"),       # literal-ok: ancho en px
    ("concepto", "Concepto", 520, "w"),                   # literal-ok: ancho en px
)


def _texto_solo_lectura(master, contenido, alto):
    """
    Un `Text` que se puede SELECCIONAR Y COPIAR pero no editar.

    `state="disabled"` a secas impediria seleccionar, y entonces la cabecera
    «copiable» no se podria copiar --- que es su unica razon de existir ---.
    Se deja habilitado y se bloquean las teclas que escriben: copiar (Ctrl-C,
    Ctrl-A) sigue funcionando porque no modifican el buffer.
    """
    txt = tk.Text(master, height=alto, wrap="none", font=("Consolas", 9),
                  borderwidth=1, relief="solid")
    txt.insert("1.0", contenido)
    # 0x4 es el bit de Control en el `state` de un evento de Tk: con el pulsado
    # la tecla es un atajo (Ctrl-C, Ctrl-A) y no una escritura, y por eso pasa.
    # Las de navegacion pasan tambien: mover el cursor no cambia el buffer.
    CONTROL = 0x4  # literal-ok: mascara del bit de Control en el `state` de Tk
    txt.bind("<Key>", lambda e: (
        None if e.state & CONTROL or e.keysym in ("Left", "Right", "Up", "Down",
                                                  "Home", "End", "Prior", "Next")
        else "break"))
    return txt


class VentanaAyudaEntrada(tk.Toplevel):
    """La ayuda de los dos archivos de entrada, abierta en la pestana pedida."""

    def __init__(self, master, pestana=PESTANA_CSV):
        super().__init__(master)
        self.title(TITULO)
        self.geometry("1040x780")
        self.minsize(760, 520)
        self.transient(master)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_csv = ttk.Frame(self.nb)
        self.tab_json = ttk.Frame(self.nb)
        self.nb.add(self.tab_csv, text="  CSV de puntos criticos (Sec. 1.2)  ")
        self.nb.add(self.tab_json, text="  JSON de datos externos  ")

        self._construir_csv(self.tab_csv)
        self._construir_json(self.tab_json)

        self.nb.select(self.tab_json if pestana == PESTANA_JSON else self.tab_csv)

        ttk.Button(self, text="Cerrar", command=self.destroy).pack(
            side="right", padx=10, pady=(0, 10))

    # ------------------------------------------------------------------
    # Pestana 1: el CSV
    # ------------------------------------------------------------------
    def _construir_csv(self, p):
        p.columnconfigure(0, weight=1)
        p.rowconfigure(3, weight=1)

        fichas = ay.fichas_de_columnas()

        cab = ttk.Frame(p, padding=(8, 8, 8, 0))
        cab.grid(row=0, column=0, sticky="ew")
        ttk.Label(cab, text=f"El encabezado tiene {len(fichas)} columnas, en "
                            "este orden exacto.",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(
            cab,
            text="Pegalo en una hoja vacia para empezar. Se lee de "
                 "M0_carga.COLUMNAS, que sale de los campos de PuntoCritico: "
                 "si manana el proyecto gana una columna, aparece aqui sola.",
            font=("Segoe UI", 8, "italic"), foreground="#666666",
            wraplength=980, justify="left").pack(anchor="w", pady=(2, 6))

        caja = ttk.Frame(p, padding=(8, 0))
        caja.grid(row=1, column=0, sticky="ew")
        caja.columnconfigure(0, weight=1)
        entrada = _texto_solo_lectura(caja, ay.cabecera_csv(), 2)  # literal-ok: alto en lineas
        entrada.grid(row=0, column=0, sticky="ew")
        scroll_cab = ttk.Scrollbar(caja, orient="horizontal",
                                    command=entrada.xview)
        entrada.configure(xscrollcommand=scroll_cab.set)
        scroll_cab.grid(row=1, column=0, sticky="ew")
        Tooltip(entrada, "Seleccionable: Ctrl-A y Ctrl-C copian la linea entera.")

        ttk.Label(p, text=f"La fila lleva {len(fichas)} celdas, ni una mas: "
                          f"{ay.fila_de_ejemplo()}",
                  font=("Consolas", 8), foreground="#666666").grid(
            row=2, column=0, sticky="w", padx=8, pady=(2, 8))

        panel = ttk.PanedWindow(p, orient="vertical")
        panel.grid(row=3, column=0, sticky="nsew", padx=8)

        f_tabla = ttk.Frame(panel)
        panel.add(f_tabla, weight=3)  # literal-ok: reparto del PanedWindow
        f_tabla.columnconfigure(0, weight=1)
        f_tabla.rowconfigure(0, weight=1)

        self.tree_csv = ttk.Treeview(
            f_tabla, columns=[c for c, *_r in _ANCHOS_CSV], show="headings",
            height=12)
        for col, titulo, ancho, anchor in _ANCHOS_CSV:
            self.tree_csv.heading(col, text=titulo)
            self.tree_csv.column(col, width=ancho, anchor=anchor)
        self.tree_csv.tag_configure("obligatoria", foreground=COLOR_OK)
        self.tree_csv.tag_configure("admite_vacio", foreground=COLOR_AVISO)
        self.tree_csv.grid(row=0, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(f_tabla, orient="vertical",
                                command=self.tree_csv.yview)
        self.tree_csv.configure(yscroll=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        self._fichas_csv = {f.clave: f for f in fichas}
        for f in fichas:
            self.tree_csv.insert(
                "", "end", iid=f.clave,
                values=(f.clave, f.unidad, f.resumen_de_obligatoriedad(),
                        f.concepto),
                tags=("obligatoria" if f.obligatoria else "admite_vacio",))
        self.tree_csv.bind("<<TreeviewSelect>>", self._al_elegir_columna)

        f_det = ttk.LabelFrame(panel, text="De donde sale el dato de esta columna",
                                padding=8)
        panel.add(f_det, weight=2)  # literal-ok: reparto del PanedWindow
        f_det.columnconfigure(0, weight=1)
        f_det.rowconfigure(0, weight=1)
        # CON SCROLL Y NO SIN EL. La `resolucion` de `sucs_fundacion` ocupa
        # 1300 caracteres --- explica por que la columna es obligatoria aunque
        # hoy no la lea ningun modulo --- y en un panel fijo se veria el primer
        # tercio. Es el mismo defecto que el detalle de la pestana 2 tuvo.
        # `height=10` y no 8: el panel arranca con el tamaño que su contenido
        # pide, y con 8 la ficha de una columna se cortaba justo antes de «SE
        # LEE DE», que es la linea por la que se abre esta ayuda. Medido sobre
        # la ventana real, no supuesto.
        self.txt_csv = tk.Text(f_det, height=10, wrap="word", font=("Consolas", 9))
        self.txt_csv.grid(row=0, column=0, sticky="nsew")
        scroll_det = ttk.Scrollbar(f_det, orient="vertical",
                                    command=self.txt_csv.yview)
        self.txt_csv.configure(yscrollcommand=scroll_det.set)
        scroll_det.grid(row=0, column=1, sticky="ns")
        self.txt_csv.configure(state="disabled")

        self._pintar_vacios(p)

    def _pintar_vacios(self, p):
        """
        Las celdas que pueden ir vacias, AGRUPADAS POR QUIEN DEBE EL DATO.

        Es la mitad que la lista de columnas no da. Leyendo fila por fila se ve
        que `Q_m3s` admite vacio; no se ve que en un cruce de canal las tres
        columnas del caudal, el area y la pendiente las debe el MISMO tablero y
        llegan juntas. Un proyectista que no lo sepa cree que le falta un dato
        suyo, y lo que falta es la respuesta de la Junta de Usuarios.
        """
        marco = ttk.LabelFrame(
            p, text="Celdas que pueden ir vacias: quien debe cada dato",
            padding=8)
        marco.grid(row=4, column=0, sticky="ew", padx=8, pady=(8, 8))
        marco.columnconfigure(0, weight=1)

        for fila, (quien, columnas, familias) in enumerate(
                ay.vacios_por_quien_lo_debe()):
            cuales = ", ".join(columnas)
            donde = ("en las tres familias"
                     if len(familias) == len(tuple(Familia))
                     else "solo en " + ", ".join(f"Familia {f.value}"
                                                 for f in familias))
            ttk.Label(marco, text=f"· {cuales}  ({donde})",
                      font=("Consolas", 9)).grid(row=fila * 2, column=0,
                                                  sticky="w")
            ttk.Label(marco, text=f"    lo debe: {quien}",
                      font=("Segoe UI", 8, "italic"), foreground="#666666",
                      wraplength=960, justify="left").grid(
                row=fila * 2 + 1, column=0, sticky="w", pady=(0, 4))

    def _al_elegir_columna(self, _evt=None):
        seleccion = self.tree_csv.selection()
        self.txt_csv.configure(state="normal")
        self.txt_csv.delete("1.0", "end")
        if seleccion:
            f = self._fichas_csv[seleccion[0]]
            lineas = [f"{f.clave}   [{f.unidad}]", "",
                      f"CONCEPTO   {f.concepto}", "",
                      f"SE LEE DE  {f.de_donde_sale}"]
            if f.dominio_declarado:
                lineas += ["", f"RANGO      {f.dominio_declarado}"]
            if f.limite_fisico is not None:
                lineas += ["",
                           f"LIMITE     {f.limite_fisico.rotulo}: "
                           f"{f.limite_fisico.frase}",
                           f"           {f.limite_fisico.que_pasa_fuera}"]
            for vacio in f.vacios:
                lineas += ["", f"VACIA      {vacio.quien_lo_debe}"]
            self.txt_csv.insert("1.0", "\n".join(lineas))
        self.txt_csv.configure(state="disabled")

    # ------------------------------------------------------------------
    # Pestana 2: el JSON
    # ------------------------------------------------------------------
    def _construir_json(self, p):
        p.columnconfigure(0, weight=1)
        p.rowconfigure(2, weight=1)

        fichas = ay.fichas_de_datos_externos()
        sin_censo = [f.clave for f in fichas if not f.en_el_censo]

        cab = ttk.Frame(p, padding=(8, 8, 8, 0))
        cab.grid(row=0, column=0, sticky="ew")
        ttk.Label(cab, text=f"El JSON admite {len(fichas)} claves, y solo esas.",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(
            cab,
            text="Las dos secciones son opcionales. Una clave mal escrita NO "
                 "se ignora: es DatoInvalidoError, para que un 'luz_m2' no "
                 "deje el punto sin luz por un error de tipeo. Los valores son "
                 "numeros en SI, salvo 'categoria_tr', que es la fila de la "
                 "Tabla N 02.",
            font=("Segoe UI", 8, "italic"), foreground="#666666",
            wraplength=980, justify="left").pack(anchor="w", pady=(2, 6))

        caja = ttk.Frame(p, padding=(8, 0))
        caja.grid(row=1, column=0, sticky="ew")
        caja.columnconfigure(0, weight=1)
        # 6 lineas: las que ocupa el esqueleto entero, para que se vea sin
        # scroll. Es alto de widget, no una magnitud del expediente.
        esqueleto = _texto_solo_lectura(caja, ay.esqueleto_json(), 6)  # literal-ok: alto en lineas
        esqueleto.grid(row=0, column=0, sticky="ew")
        Tooltip(esqueleto,
                "La forma del archivo, sin datos. Pegado tal cual es valido y\n"
                "no declara nada: se le anaden las claves de la tabla de abajo.")

        f_tabla = ttk.Frame(p, padding=(8, 8, 8, 0))
        f_tabla.grid(row=2, column=0, sticky="nsew")
        f_tabla.columnconfigure(0, weight=1)
        f_tabla.rowconfigure(0, weight=1)

        self.tree_json = ttk.Treeview(
            f_tabla, columns=[c for c, *_r in _ANCHOS_JSON], show="headings",
            height=8)
        for col, titulo, ancho, anchor in _ANCHOS_JSON:
            self.tree_json.heading(col, text=titulo)
            self.tree_json.column(col, width=ancho, anchor=anchor)
        self.tree_json.tag_configure("sin_censo", foreground=COLOR_AVISO)
        self.tree_json.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(f_tabla, orient="vertical",
                                command=self.tree_json.yview)
        self.tree_json.configure(yscroll=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        for f in fichas:
            concepto = f.concepto if f.en_el_censo else (
                "(sin ficha: no es columna del CSV, ni dato de sitio, ni "
                "criterio; su descripcion esta en el docstring de cli.py)")
            self.tree_json.insert(
                "", "end", iid=f.clave,
                values=(f.clave, f.resumen_de_familias, concepto),
                tags=() if f.en_el_censo else ("sin_censo",))

        # LO QUE ESTA AYUDA NO PUEDE DECIR, DICHO. Seis de las ocho claves no
        # estan en el censo de `variables_entrada`, de modo que de ellas no hay
        # concepto ni unidad que derivar. Su documentacion es prosa en un
        # docstring, y un docstring no es una interfaz: parsearlo daria una
        # ayuda que se rompe callada la proxima vez que alguien lo reformatee.
        # Se dice en vez de rellenarse con una frase inventada.
        ttk.Label(
            p,
            text="Las " + str(len(sin_censo)) + " claves en ambar (" +
                 ", ".join(sin_censo) + ") no tienen ficha: no son columna del "
                 "CSV, ni dato de sitio, ni criterio, de modo que no estan en "
                 "el censo de variables_entrada.py y esta ayuda no tiene de "
                 "donde derivar su concepto ni su unidad. Estan descritas en "
                 "el docstring de cli.py, seccion «Datos que NO estan en el "
                 "CSV». Esta ventana no lo transcribe a proposito: una ayuda "
                 "que copie prosa se separa de ella sin que nadie avise.",
            font=("Segoe UI", 8, "italic"), foreground=COLOR_AVISO,
            wraplength=980, justify="left").grid(
            row=3, column=0, sticky="w", padx=8, pady=8)


def abrir(master, pestana=PESTANA_CSV):
    """Abre la ayuda en la pestana pedida y devuelve la ventana."""
    return VentanaAyudaEntrada(master, pestana=pestana)
