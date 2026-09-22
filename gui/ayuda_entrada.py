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

Las tres pestanas
-----------------
Las dos primeras son dos archivos distintos del expediente, y estan en la
MISMA ventana porque se leen juntas: `Q_m3s` y `S_cauce` son columna del CSV y
ademas clave del JSON --- van vacias en la fila de un cruce de canal y entran
por el JSON cuando el Tablero 3.1 las entrega ---, y esa vuelta es imposible
de contar en dos ventanas que no se ven a la vez. El icono de cada campo abre
la ventana en SU pestana; una vez abierta, el usuario cruza.

La tercera (G5) no es un archivo: son los CONCEPTOS con que las otras
pantallas hablan --- familias, etiquetas, estados de un criterio y el glosario
del censo ---, para el lector que llega sin conocer el proyecto. Sus listas
son derivadas como las otras dos; sus parrafos son texto estable de
`src/ayuda_entrada.py`, declarado alli como escrito a mano y guardado contra
las listas.

Reutiliza `gui/componentes.py`: el `Tooltip`, y el `BotonAyuda` con que la
ventana principal la llama. NO usa `MarcoScroll`: sus dos pestanas reparten el
alto con un `PanedWindow` y un `Treeview`, que traen su propio scroll.
"""

from __future__ import annotations


import tkinter as tk
from tkinter import ttk

from src import ayuda_entrada as ay
from src.modelos import Familia

from gui import componentes as comp
from gui.componentes import COLOR_AVISO, COLOR_OK, Tooltip

# Los nombres de las tres pestanas, que ademas son los modos con que se
# puede abrir la ventana. Son rotulos de pantalla: lo que la ventana AFIRMA
# sale siempre de `src/ayuda_entrada.py`.
PESTANA_CSV = "csv"
PESTANA_JSON = "json"
PESTANA_CONCEPTOS = "conceptos"

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
_ANCHOS_GLOSARIO = (
    ("clave", "Simbolo (clave del censo)", 210, "w"),     # literal-ok: ancho en px
    ("unidad", "Unidad", 90, "center"),                   # literal-ok: ancho en px
    ("poblacion", "Que es", 130, "w"),                    # literal-ok: ancho en px
    ("fase", "Fase que lo consume", 220, "w"),            # literal-ok: ancho en px
    ("concepto", "Concepto", 330, "w"),                   # literal-ok: ancho en px
)


def _texto_solo_lectura(master, contenido, alto):
    """
    Un `Text` que se puede SELECCIONAR Y COPIAR pero no editar.

    `state="disabled"` a secas impediria seleccionar, y entonces la cabecera
    «copiable» no se podria copiar --- que es su unica razon de existir ---.
    Se deja habilitado y se bloquean las teclas que escriben: copiar (Ctrl-C,
    Ctrl-A) sigue funcionando porque no modifican el buffer.
    """
    # La caja copiable con la cara del tema (superficie y linea fina), en
    # monoespaciada porque es una cabecera que se pega tal cual.
    txt = comp.texto_plano(master, height=alto, wrap="none")
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
        self.configure(background=comp.FONDO)
        self.title(TITULO)
        self.geometry("1040x780")
        self.minsize(760, 520)
        self.transient(master)
        # Escape cierra la ayuda (EXT-8, PC-17), como el boton «Cerrar».
        self.bind("<Escape>", lambda _evt: self.destroy())

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_csv = ttk.Frame(self.nb)
        self.tab_json = ttk.Frame(self.nb)
        self.tab_conceptos = ttk.Frame(self.nb)
        self.nb.add(self.tab_csv, text="  CSV de puntos criticos (Sec. 1.2)  ")
        self.nb.add(self.tab_json, text="  JSON de datos externos  ")
        self.nb.add(self.tab_conceptos, text="  Conceptos  ")

        self._construir_csv(self.tab_csv)
        self._construir_json(self.tab_json)
        self._construir_conceptos(self.tab_conceptos)

        destinos = {PESTANA_JSON: self.tab_json,
                    PESTANA_CONCEPTOS: self.tab_conceptos}
        self.nb.select(destinos.get(pestana, self.tab_csv))

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
                  font=comp.tipografia().ui(comp.CUERPO_PT, "bold")).pack(anchor="w")
        ttk.Label(
            cab,
            text="Pegalo en una hoja vacia para empezar. Se lee de "
                 "M0_carga.COLUMNAS, que sale de los campos de PuntoCritico: "
                 "si manana el proyecto gana una columna, aparece aqui sola.",
            font=comp.tipografia().ui(comp.PEQUENA_PT), foreground=comp.TEXTO_SUAVE,
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
                  font=comp.tipografia().mono(comp.PEQUENA_PT), foreground=comp.TEXTO_SUAVE).grid(
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
        self.txt_csv = comp.texto_prosa(f_det, height=10, wrap="word")
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
                      font=comp.tipografia().mono(comp.CUERPO_PT)).grid(row=fila * 2, column=0,
                                                  sticky="w")
            ttk.Label(marco, text=f"    lo debe: {quien}",
                      font=comp.tipografia().ui(comp.PEQUENA_PT), foreground=comp.TEXTO_SUAVE,
                      wraplength=960, justify="left").grid(
                row=fila * 2 + 1, column=0, sticky="w", pady=(0, 4))

    def _al_elegir_columna(self, _evt=None):
        seleccion = self.tree_csv.selection()
        if not seleccion:
            comp.escribir_campos(self.txt_csv, ())
            return
        f = self._fichas_csv[seleccion[0]]
        # EL ORDEN LO DECIDIO LA VENTANA REAL, no el gusto. Con «SE LEE DE»
        # en segundo lugar, la ficha de `sucs_fundacion` --- 1236 caracteres
        # de trazabilidad --- empujaba la NOTA fuera del panel, y la nota es
        # justo lo que el proyectista necesita: QUE ESCRIBIR en la celda.
        # Se ordena por accionabilidad y la prosa larga queda al final, que
        # es donde el scroll molesta menos. Cada campo es un bloque con su
        # rotulo (bloque 4 del rediseño): el contenido es el de la ficha.
        campos = [("Concepto", f.concepto), ("Nota", f.nota),
                  ("Rango", f.dominio_declarado)]
        if f.limite_fisico is not None:
            campos.append(("Limite", f"{f.limite_fisico.rotulo}: "
                                     f"{f.limite_fisico.frase}\n"
                                     f"{f.limite_fisico.que_pasa_fuera}"))
        for vacio in f.vacios:
            campos.append(("Vacia", vacio.quien_lo_debe))
        campos.append(("Se lee de", f.de_donde_sale))
        comp.escribir_campos(self.txt_csv, campos,
                             titulo=f"{f.clave}   [{f.unidad}]")

    # ------------------------------------------------------------------
    # Pestana 2: el JSON
    # ------------------------------------------------------------------
    def _construir_json(self, p):
        p.columnconfigure(0, weight=1)
        p.rowconfigure(2, weight=1)

        fichas = ay.fichas_de_datos_externos()

        cab = ttk.Frame(p, padding=(8, 8, 8, 0))
        cab.grid(row=0, column=0, sticky="ew")
        ttk.Label(cab, text=f"El JSON admite {len(fichas)} claves, y solo esas.",
                  font=comp.tipografia().ui(comp.CUERPO_PT, "bold")).pack(anchor="w")
        ttk.Label(
            cab,
            text="Las dos secciones son opcionales. Una clave mal escrita NO "
                 "se ignora: es DatoInvalidoError, para que un 'luz_m2' no "
                 "deje el punto sin luz por un error de tipeo. Los valores son "
                 "numeros en SI, salvo 'categoria_tr', que es la fila de la "
                 "Tabla N 02.",
            font=comp.tipografia().ui(comp.PEQUENA_PT), foreground=comp.TEXTO_SUAVE,
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
        self.tree_json.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(f_tabla, orient="vertical",
                                command=self.tree_json.yview)
        self.tree_json.configure(yscroll=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        for f in fichas:
            self.tree_json.insert(
                "", "end", iid=f.clave,
                values=(f.clave, f.resumen_de_familias,
                        f"{f.concepto} [{f.unidad}] · se lee de: "
                        f"{f.de_donde_sale}"))

        # LAS OCHO TIENEN FICHA, y las ocho salen del censo de
        # `variables_entrada` (EXT-G-03): las dos que son columna del CSV
        # dicen lo mismo que en la pestaña 1, y las seis restantes son la
        # poblacion `dato_externo`. Esta ventana no transcribe prosa de
        # ningun docstring: lo que muestra es lo que el censo declara.
        ttk.Label(
            p,
            text="Concepto, unidad y origen salen del censo de "
                 "variables_entrada.py, el mismo del que sale la ayuda del "
                 "CSV: las dos claves que ademas son columna dicen aqui lo "
                 "mismo que alli.",
            font=comp.tipografia().ui(comp.PEQUENA_PT), foreground=comp.TEXTO_SUAVE,
            wraplength=980, justify="left").grid(
            row=3, column=0, sticky="w", padx=8, pady=8)


    # ------------------------------------------------------------------
    # Pestana 3: los conceptos
    # ------------------------------------------------------------------
    def _construir_conceptos(self, p):
        """
        Familias, etiquetas y estados en un texto con scroll; el glosario en
        su tabla. El reparto del alto es un `PanedWindow`, como en la pestana
        del CSV, porque las dos mitades se consultan con frecuencias
        distintas: la prosa se lee una vez, el glosario se vuelve a abrir
        cada vez que un simbolo aparece en otra pantalla.
        """
        p.columnconfigure(0, weight=1)
        p.rowconfigure(1, weight=1)

        cab = ttk.Frame(p, padding=(8, 8, 8, 0))
        cab.grid(row=0, column=0, sticky="ew")
        ttk.Label(cab, text="Las palabras con que este programa describe el "
                            "expediente.",
                  font=comp.tipografia().ui(comp.CUERPO_PT, "bold")).pack(anchor="w")
        ttk.Label(
            cab,
            text="Donde se usan: la pestana 1 agrupa los datos por FAMILIA y "
                 "anticipa los bloqueos antes de correr; la pestana 2 lista "
                 "los criterios con su ETIQUETA y su ESTADO, con filtros por "
                 "estado, ambito y fase; la pestana 3 traza cada numero hasta "
                 "su procedencia («¿de donde sale este numero?»). Las listas "
                 "de abajo son derivadas; los parrafos son texto estable de "
                 "src/ayuda_entrada.py.",
            font=comp.tipografia().ui(comp.PEQUENA_PT), foreground=comp.TEXTO_SUAVE,
            wraplength=980, justify="left").pack(anchor="w", pady=(2, 6))

        panel = ttk.PanedWindow(p, orient="vertical")
        panel.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        panel_prosa = comp.Panel(panel, "Familias, etiquetas y estados")
        panel.add(panel_prosa, weight=3)  # literal-ok: reparto del PanedWindow
        f_prosa = panel_prosa.interior
        f_prosa.columnconfigure(0, weight=1)
        f_prosa.rowconfigure(0, weight=1)
        self.txt_conceptos = comp.texto_prosa(f_prosa, height=16, wrap="word")
        self.txt_conceptos.grid(row=0, column=0, sticky="nsew")
        scroll_prosa = ttk.Scrollbar(f_prosa, orient="vertical",
                                     command=self.txt_conceptos.yview)
        self.txt_conceptos.configure(yscrollcommand=scroll_prosa.set)
        scroll_prosa.grid(row=0, column=1, sticky="ns")
        self._pintar_conceptos(self.txt_conceptos)

        panel_glosario = comp.Panel(
            panel, "Glosario de simbolos y unidades (el censo de "
                   "variables_entrada.py, entero)")
        panel.add(panel_glosario, weight=2)  # literal-ok: reparto del PanedWindow
        f_glosario = panel_glosario.interior
        f_glosario.columnconfigure(0, weight=1)
        f_glosario.rowconfigure(0, weight=1)

        self.tree_glosario = ttk.Treeview(
            f_glosario, columns=[c for c, *_r in _ANCHOS_GLOSARIO],
            show="headings", height=8)
        for col, titulo, ancho, anchor in _ANCHOS_GLOSARIO:
            self.tree_glosario.heading(col, text=titulo)
            self.tree_glosario.column(col, width=ancho, anchor=anchor)
        self.tree_glosario.grid(row=0, column=0, sticky="nsew")
        scroll_glo = ttk.Scrollbar(f_glosario, orient="vertical",
                                   command=self.tree_glosario.yview)
        self.tree_glosario.configure(yscroll=scroll_glo.set)
        scroll_glo.grid(row=0, column=1, sticky="ns")

        for f in ay.fichas_de_glosario():
            self.tree_glosario.insert(
                "", "end", iid=f.clave,
                values=(f.clave, f.unidad, f.poblacion, f.fase, f.concepto))

    def _pintar_conceptos(self, texto):
        """
        La mitad de prosa, ARMADA de las fichas y de nada mas: este metodo
        elige etiquetas de prosa (seccion, rotulo, cuerpo, mono), no
        contenido. Si una frase de aqui esta mal, se corrige en
        `src/ayuda_entrada.py` (los parrafos) o en la declaracion de la que
        su ficha deriva (las listas). Hasta el bloque 4 del rediseño esto
        era un texto monoespaciado con subrayados de «=».
        """
        texto.configure(state="normal")
        texto.delete("1.0", "end")

        def seccion(titulo):
            texto.insert("end", titulo + "\n", "seccion")

        def parrafo(contenido, etiqueta="cuerpo"):
            texto.insert("end", contenido + "\n", (etiqueta, "sangria"))

        familias = ay.fichas_de_familias()
        seccion(f"Las {len(familias)} familias ({familias[0].numeral})")
        for f in familias:
            texto.insert("end", f.rotulo + "\n", "rotulo")
            parrafo(f"De donde sale su Q: {f.origen_del_caudal}")
            for nota in f.notas:
                parrafo(f"Nota: {nota}", "suave")

        etiquetas = ay.fichas_de_etiquetas()
        seccion(f"Las {len(etiquetas)} etiquetas de un valor")
        texto.insert("end", "Todo valor del proyecto lleva una, de mas "
                            "determinado a mas elegido:\n", "cuerpo")
        for f in etiquetas:
            texto.insert("end", f"{f.rotulo}  {f.nombre}\n", "rotulo")
            parrafo(f.explicacion)
            parrafo(f"Vive en: {f.archivo}", "mono")

        estados = ay.fichas_de_estados()
        seccion("Estados de un criterio")
        for f in estados:
            texto.insert("end", f.rotulo + "\n", "rotulo")
            parrafo(f.explicacion)
            parrafo(f"(sale de: {f.origen})", "mono")
        texto.configure(state="disabled")


def abrir(master, pestana=PESTANA_CSV):
    """Abre la ayuda en la pestana pedida y devuelve la ventana."""
    return VentanaAyudaEntrada(master, pestana=pestana)
