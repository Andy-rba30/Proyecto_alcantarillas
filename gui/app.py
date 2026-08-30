# -*- coding: utf-8 -*-
"""
gui/app.py
==========
Interfaz grafica del expediente de alcantarillas. Reutiliza el patron de
`legacy/Tc.py`: Tkinter + ttkbootstrap, Notebook por pestanas, MarcoScroll y
Tooltip, los dos por `gui/componentes.py`.

Que NO reutiliza este archivo, dicho porque el encabezado lo afirmaba (SIS-A-12)
---------------------------------------------------------------------------
El **campo validable** de `legacy/Tc.py` (`_campo_validable` + `_marcar`)
existe en el proyecto, pero no aqui: vive en `gui/componentes.CampoValidable`
y lo usa la ventana emergente, `gui/ventana_normativa.py`, que es donde la
Sec. 4.3 pide validar AL ESCRIBIR. Esta ventana valida al pulsar EJECUTAR y
sus campos son `ttk.Entry` desnudos. De aquel componente quedaba ademas un
resto muerto --- `self.color_borde_ok`, el color de fondo neutro que
`_campo_validable` pintaba ---: se calculaba en `_crear_interfaz` y no lo
leia nadie. Retirado; el color neutro que el componente necesita se lo pide
hoy `CampoValidable` a su llamador.

No reimplementa el pipeline: llama a las mismas funciones que usa `cli.py`
(`cargar_datos_externos`, `correr`, `informe_json`, `exportar_html`,
`exportar_pdf`) para que la GUI y la linea de comandos vean siempre el mismo
expediente.

Pestanas -- son CUATRO, y esta lista decia tres (SIS-A-10)
-----------------------------------------------------------
    1. Datos de entrada    CSV de Sec. 1.2 (M0) + datos declarados que no son
                            columna (banderas de `cli.py`) + ALCANCE de la
                            corrida + boton de ejecucion.
    2. Criterios           Los criterios adoptados y su estado; la ventana
                            normativa de cada variable (Sec. 4.2/4.3 del
                            plan); y el unico sitio de la interfaz que
                            REESCRIBE `criterios_adoptados.py` --- accion
                            permanente, aparte y con confirmacion propia, que
                            es justo la pestana que esta lista omitia.
    3. Resultados por punto  Un Treeview con el resumen de cada punto y, al
                            seleccionar una fila, el detalle de verificaciones
                            y bloqueos de ese punto.
    4. Resumen             Estado del expediente, criterios pendientes que
                            bloquearon una etapa, lo diferido por alcance, y
                            exportacion (JSON/HTML/PDF/CSV).

El alcance de la corrida (SIS-A-17)
-----------------------------------
`cli.py` acepta `--alcance perfil|expediente` desde hace tiempo y la ventana
no lo exponia: corria SIEMPRE «expediente», de modo que `memoria_perfil.html`
--- una de las dos plantillas del proyecto --- era inalcanzable desde la
interfaz y el nivel de perfil solo existia para quien usara la linea de
comandos. El selector de la pestana 1 lo expone, y la exportacion elige la
plantilla con `cli.plantilla_por_alcance`, que es la MISMA funcion que usa
`cli.main`: dos reglas para elegir plantilla serian dos memorias distintas
para la misma corrida.

Los criterios en la sesion (SIS-A-18)
-------------------------------------
La sesion JSON guardaba el proyecto, el CSV y las cinco banderas, y NO las
declaraciones de la corrida. Quien declaraba cinco criterios y volvia al dia
siguiente recuperaba el nombre del archivo y perdia las cinco decisiones sin
un aviso. Ahora se guardan y se restauran los valores Y SU PROCEDENCIA, por
`declaracion.restaurar_sesion`, que repone por el mismo camino con guardia que
usan la ventana y la CLI. Lo que la guardia rechace se muestra: una sesion es
un archivo que alguien pudo editar a mano.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
for _ruta in (RAIZ, SRC):
    if str(_ruta) not in sys.path:
        sys.path.insert(0, str(_ruta))

import json  # noqa: E402

import cli  # noqa: E402
import criterios_adoptados as ca  # noqa: E402
import declaracion as dec  # noqa: E402
import variables_entrada as ve  # noqa: E402
from modelos import ErrorProyecto  # noqa: E402

from gui import ventana_normativa as ventana_norma  # noqa: E402
from gui.componentes import (COLOR_AVISO, COLOR_ERROR,  # noqa: E402
                             COLOR_OK, MarcoScroll, Tooltip)

try:
    import ttkbootstrap as tb
except ImportError:
    tb = None

APP_VERSION = "1.0"
# v2: la sesion guarda tambien el alcance de la corrida y los criterios
# declarados con su procedencia (SIS-A-17, SIS-A-18). Una sesion v1 se sigue
# leyendo: lo que no trae se queda en su valor por defecto y la ventana lo
# dice, que es el patron de migracion de `legacy/Tc.py`.
FORMATO_SESION = 2

# Banderas globales que acepta `cli.py` fuera del CSV (ver docstring de
# `cli.py`, seccion "Datos que NO estan en el CSV"). Cada tupla es
# (clave, etiqueta, ayuda, unidad).
CAMPOS_EXTERNOS = (
    ("luz_m", "Luz del cruce:",
     "Luz del cruce, en METROS (Sec. 2.1).\n"
     "Sin ella no se puede separar alcantarilla de puente\n"
     "y el punto no se dimensiona.", "[m]"),
    ("TW_m", "Tirante en el receptor (TW):",
     "Tirante en el receptor sobre el fondo de la salida, en METROS.\n"
     "Si no se declara se pide al criterio 'TW_receptor'.", "[m]"),
    ("longitud_m", "Longitud del conducto:",
     "Longitud del conducto, en METROS.\n"
     "Si no se declara la calcula M7 (Sec. 7.B).", "[m]"),
    ("l_hidraulico", "L hidraulico (cuneta, Familia B):",
     "Longitud a la que la cuneta agota su capacidad, en METROS.\n"
     "Solo aplica a Familia B (Fase 10).", "[m]"),
    ("categoria_tr", "Categoria TR (Familia A):",
     "Fila de la Tabla N 02: 'quebrada_importante' o 'quebrada_menor'\n"
     "(Sec. 2.2). Sin ella la Familia A se detiene en el umbral de area.", ""),
)


class ExpedienteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expediente de Alcantarillas - M0 a M10")
        self.root.geometry("1100x800")
        self.root.minsize(900, 620)

        self.proyecto_var = tk.StringVar()
        self.csv_var = tk.StringVar()
        self.datos_externos_var = tk.StringVar()
        self.externos_vars = {clave: tk.StringVar() for clave, *_r in CAMPOS_EXTERNOS}
        # El defecto es el MISMO que el de `cli.py` (`--alcance`, choices con
        # default `expediente`), y se lee de alli en vez de escribirse otra
        # vez: dos defectos que puedan divergir son dos programas.
        self.alcance_var = tk.StringVar(value=cli.ALCANCE_EXPEDIENTE)

        self.informe: Optional[cli.Informe] = None

        self._crear_interfaz()

    # ------------------------------------------------------------------
    # Construccion de la interfaz
    # ------------------------------------------------------------------
    def _crear_interfaz(self):
        if tb is not None:
            try:
                self.style = tb.Style(theme="litera")
            except Exception:
                self.style = ttk.Style()
        else:
            self.style = ttk.Style()
            if "clam" in self.style.theme_names():
                self.style.theme_use("clam")

        self.style.configure("TLabel", font=("Segoe UI", 9))
        self.style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"), foreground="#2c3e50")
        self.style.configure("Ayuda.TLabel", font=("Segoe UI", 8, "italic"), foreground="#666666")
        self.style.configure("Error.TLabel", font=("Segoe UI", 8, "bold"), foreground=COLOR_ERROR)
        self.style.configure("Res.TLabel", font=("Consolas", 11, "bold"), foreground="#1b4f72")

        contenedor = ttk.Frame(self.root, padding=10)
        contenedor.pack(fill="both", expand=True)

        self.nb = ttk.Notebook(contenedor)
        self.nb.pack(fill="both", expand=True)

        self.tab_datos = MarcoScroll(self.nb)
        self.tab_criterios = ttk.Frame(self.nb)
        self.tab_puntos = ttk.Frame(self.nb)
        self.tab_resumen = MarcoScroll(self.nb)
        self.nb.add(self.tab_datos, text="  1. Datos de entrada  ")
        self.nb.add(self.tab_criterios, text="  2. Criterios  ")
        self.nb.add(self.tab_puntos, text="  3. Resultados por punto  ")
        self.nb.add(self.tab_resumen, text="  4. Resumen  ")

        self._construir_tab_datos(self.tab_datos.interior)
        self._construir_tab_criterios(self.tab_criterios)
        self._construir_tab_puntos(self.tab_puntos)
        self._construir_tab_resumen(self.tab_resumen.interior)

        barra = ttk.Frame(contenedor, padding=(0, 10, 0, 0))
        barra.pack(fill="x")
        ttk.Button(barra, text="Guardar sesion", command=self.guardar_sesion).pack(side="left", padx=4)
        ttk.Button(barra, text="Cargar sesion", command=self.cargar_sesion).pack(side="left", padx=4)
        self.lbl_estado = ttk.Label(barra, text="Sin ejecutar.", style="Ayuda.TLabel")
        self.lbl_estado.pack(side="left", padx=(12, 0))

        self.btn_ejecutar = tk.Button(
            barra, text="EJECUTAR PIPELINE (M0 -> M10)", font=("Segoe UI", 10, "bold"),
            bg="#2e86c1", fg="white", activebackground="#21618c", activeforeground="white",
            relief="flat", cursor="hand2", command=self.ejecutar_pipeline,
        )
        self.btn_ejecutar.pack(side="right", padx=4, ipadx=14, ipady=6)

    # -------------------------- Pestana 1 -----------------------------
    def _construir_tab_datos(self, p):
        ttk.Label(p, text="1. Proyecto y CSV", style="Header.TLabel").pack(anchor="w")
        f_proj = ttk.Frame(p)
        f_proj.pack(fill="x", pady=(6, 14))
        f_proj.columnconfigure(1, weight=1)

        ttk.Label(f_proj, text="Nombre del proyecto:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        ent_proy = ttk.Entry(f_proj, textvariable=self.proyecto_var)
        ent_proy.grid(row=0, column=1, sticky="we", padx=5, pady=4, columnspan=2)
        Tooltip(ent_proy, "Encabeza la memoria de calculo (M11).")

        ttk.Label(f_proj, text="CSV de puntos criticos (Sec. 1.2):").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        ent_csv = ttk.Entry(f_proj, textvariable=self.csv_var)
        ent_csv.grid(row=1, column=1, sticky="we", padx=5, pady=4)
        ttk.Button(f_proj, text="Examinar...", command=self._elegir_csv).grid(row=1, column=2, sticky="w", padx=5)

        ttk.Label(f_proj, text="JSON de datos externos (opcional):").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        ent_ext = ttk.Entry(f_proj, textvariable=self.datos_externos_var)
        ent_ext.grid(row=2, column=1, sticky="we", padx=5, pady=4)
        ttk.Button(f_proj, text="Examinar...", command=self._elegir_datos_externos).grid(row=2, column=2, sticky="w", padx=5)
        Tooltip(ent_ext, "JSON con secciones 'globales' y/o 'puntos', igual que\n"
                         "el '--datos-externos' de cli.py. Una bandera de abajo\n"
                         "pisa al valor global de este archivo.")

        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=6)

        ttk.Label(p, text="2. Datos declarados (no son columna del CSV)",
                  style="Header.TLabel").pack(anchor="w", pady=(8, 0))
        ttk.Label(p, text="Se aplican como banderas globales, igual que --luz, --tw, "
                          "--longitud, --l-hidraulico y --categoria-tr de cli.py. "
                          "Un valor por punto solo puede declararse en el JSON de "
                          "datos externos.",
                  style="Ayuda.TLabel", wraplength=820, justify="left").pack(anchor="w", pady=(0, 8))

        f_ext = ttk.Frame(p)
        f_ext.pack(fill="x", pady=6)
        for fila, (clave, etiqueta, ayuda, unidad) in enumerate(CAMPOS_EXTERNOS):
            ttk.Label(f_ext, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=5, pady=6)
            ent = ttk.Entry(f_ext, textvariable=self.externos_vars[clave], width=20, justify="right")
            ent.grid(row=fila, column=1, sticky="w", padx=5, pady=6)
            ttk.Label(f_ext, text=unidad, style="Ayuda.TLabel").grid(row=fila, column=2, sticky="w")
            Tooltip(ent, ayuda)

        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=6)

        ttk.Label(p, text="3. Alcance de la corrida (--alcance)",
                  style="Header.TLabel").pack(anchor="w", pady=(8, 0))
        ttk.Label(
            p,
            text="Es una bifurcacion DECLARADA, no una poda. Con 'expediente' "
                 "todo corre como siempre. Con 'perfil', V5 y V8 se intentan "
                 "pero su fallo se difiere al expediente en vez de frenar el "
                 "dimensionamiento, y las Fases 8 y 9 no se ejecutan: nada de "
                 "lo diferido se pierde -- queda registrado con su fundamento "
                 "en el bloque de alcance del informe y de la memoria. El "
                 "alcance elige ademas la plantilla por defecto de la memoria.",
            style="Ayuda.TLabel", wraplength=820, justify="left",
        ).pack(anchor="w", pady=(0, 6))

        f_alc = ttk.Frame(p)
        f_alc.pack(fill="x", pady=4)
        for columna, (valor, etiqueta, ayuda) in enumerate((
                (cli.ALCANCE_EXPEDIENTE, "Expediente (defecto)",
                 "El pipeline completo: M0 a M10 mas la Fase 9.\n"
                 "Plantilla por defecto de la memoria: memoria_alcantarillas.html."),
                (cli.ALCANCE_PERFIL, "Perfil",
                 "V5 y V8 diferidas al expediente y Fases 8 y 9 no ejecutadas,\n"
                 "cada una con su constancia. Plantilla por defecto:\n"
                 "memoria_perfil.html, que sin este selector era INALCANZABLE\n"
                 "desde la ventana (SIS-A-17)."))):
            rb = ttk.Radiobutton(f_alc, text=etiqueta, value=valor,
                                 variable=self.alcance_var)
            rb.grid(row=0, column=columna, sticky="w", padx=12, pady=4)
            Tooltip(rb, ayuda)

        self.lbl_error_datos = ttk.Label(p, text="", style="Error.TLabel", wraplength=820, justify="left")
        self.lbl_error_datos.pack(anchor="w", padx=5, pady=(10, 0))

        ttk.Label(
            p,
            text="Ningun dato de esta seccion tiene valor por defecto: sin declararlo, "
                 "la etapa que lo necesita queda registrada como bloqueo en el informe "
                 "(no se sustituye por un numero plausible).",
            style="Ayuda.TLabel", wraplength=820, justify="left",
        ).pack(anchor="w", padx=5, pady=(6, 0))

    def _elegir_csv(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar CSV de puntos criticos",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            self.csv_var.set(ruta)

    def _elegir_datos_externos(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar JSON de datos externos",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            self.datos_externos_var.set(ruta)

    # -------------------------- Pestana 2 -----------------------------
    def _construir_tab_criterios(self, p):
        p.columnconfigure(0, weight=1)
        p.rowconfigure(1, weight=1)

        f_cab = ttk.Frame(p, padding=(10, 10, 10, 0))
        f_cab.grid(row=0, column=0, sticky="ew")
        ttk.Label(f_cab, text="Criterios adoptados (criterios_adoptados.py)",
                  style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            f_cab,
            # Las CUATRO que este archivo tiene, y solo esas (SIS-A-11).
            # [N] no aparece, y conviene decir con precision por que: NO es
            # que el codigo lo impida --- `ETIQUETAS_VALIDAS` admite 'N' y
            # `_verificar_criterio` la aceptaria ---, es que un valor
            # normativo vive en constantes_normativas.py, y lo que sostiene
            # esa separacion es el guardian
            # `test_ningun_criterio_adoptado_lleva_ya_la_etiqueta_N`.
            # Anunciar [N] aqui invitaba a leer como norma lo que es
            # adopcion. [S] SI esta -- hoy tres entradas, los datos de sitio
            # pendientes de ensayo que comparten tablero con los criterios --
            # y faltaba.
            text="Etiquetas: [N->] normativo por analogia  "
                 "[S] dato de sitio (procedimiento normativo sobre ESTE sitio: "
                 "se defiende con trazabilidad, no con sensibilidad)  "
                 "[C] fuente tecnica reconocida  [A] adopcion sin norma unica. "
                 "Ninguna fila de esta tabla es normativa: lo normativo vive "
                 "en constantes_normativas.py y no se declara desde aqui. "
                 "Las filas en rojo son criterios PENDIENTES (valor=None): bloquean "
                 "cualquier calculo que los invoque hasta que se declare un valor.",
            style="Ayuda.TLabel", wraplength=980, justify="left",
        ).pack(anchor="w", pady=(2, 8))

        f_tabla = ttk.Frame(p, padding=(10, 0))
        f_tabla.grid(row=1, column=0, sticky="nsew")
        f_tabla.columnconfigure(0, weight=1)
        f_tabla.rowconfigure(0, weight=1)

        cols = ("clave", "etiqueta", "concepto", "valor", "estado", "fuente")
        self.tree_criterios_todos = ttk.Treeview(
            f_tabla, columns=cols, show="headings", height=14)
        encabezados = [
            ("clave", "Clave", 190, "w"),  # literal-ok: ancho de columna, px
            ("etiqueta", "Etq.", 45, "center"),  # literal-ok: ancho de columna, px
            ("concepto", "Concepto", 260, "w"),  # literal-ok: ancho de columna, px
            ("valor", "Valor actual", 160, "w"),  # literal-ok: ancho de columna, px
            ("estado", "Estado", 110, "center"),  # literal-ok: ancho de columna, px
            ("fuente", "Fuente", 300, "w"),  # literal-ok: ancho de columna, px
        ]
        for col, txt, ancho, anchor in encabezados:
            self.tree_criterios_todos.heading(col, text=txt)
            self.tree_criterios_todos.column(col, width=ancho, anchor=anchor)
        self.tree_criterios_todos.grid(row=0, column=0, sticky="nsew")
        self.tree_criterios_todos.tag_configure("pendiente", background="#fdecea",
                                                 foreground=COLOR_ERROR)
        self.tree_criterios_todos.tag_configure("declarado_corrida",
                                                 background="#fef9e7",
                                                 foreground=COLOR_AVISO)
        self.tree_criterios_todos.tag_configure("resuelto", foreground=COLOR_OK)
        self.tree_criterios_todos.bind("<<TreeviewSelect>>", self._al_seleccionar_criterio)
        # Doble clic = abrir la ventana normativa de ese criterio. Es el gesto
        # que el usuario ya hace sobre una tabla, y el boton de abajo repite
        # la accion para quien no lo descubra.
        self.tree_criterios_todos.bind("<Double-1>", self._abrir_ventana_normativa)

        scroll_ct = ttk.Scrollbar(f_tabla, orient="vertical",
                                   command=self.tree_criterios_todos.yview)
        self.tree_criterios_todos.configure(yscroll=scroll_ct.set)
        scroll_ct.grid(row=0, column=1, sticky="ns")

        f_detalle = ttk.LabelFrame(p, text="Detalle del criterio seleccionado", padding=10)
        f_detalle.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 0))
        f_detalle.columnconfigure(0, weight=1)

        self.txt_detalle_criterio = tk.Text(f_detalle, height=6, wrap="word",
                                             font=("Consolas", 9))
        self.txt_detalle_criterio.grid(row=0, column=0, sticky="ew")
        self.txt_detalle_criterio.configure(state="disabled")

        f_declarar = ttk.LabelFrame(p, text="Declarar valor para el criterio pendiente",
                                     padding=10)
        f_declarar.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        f_declarar.columnconfigure(1, weight=1)

        ttk.Label(f_declarar, text="Criterio:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.lbl_criterio_seleccionado = ttk.Label(f_declarar, text="(ninguno seleccionado)",
                                                     style="Header.TLabel")
        self.lbl_criterio_seleccionado.grid(row=0, column=1, sticky="w")

        ttk.Label(f_declarar, text="Valor nuevo:").grid(row=1, column=0, sticky="w",
                                                          padx=(0, 6), pady=6)
        self.valor_declarado_var = tk.StringVar()
        ent_val = ttk.Entry(f_declarar, textvariable=self.valor_declarado_var)
        ent_val.grid(row=1, column=1, sticky="we", pady=6)
        Tooltip(ent_val, "Numero (con punto decimal) o texto, segun lo que pida el\n"
                         "criterio. Se intenta interpretar como numero; si no es\n"
                         "posible, se guarda como texto tal cual se escribe.")

        f_botones = ttk.Frame(f_declarar)
        f_botones.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

        self.btn_aplicar_corrida = tk.Button(
            f_botones, text="Aplicar solo a esta corrida", font=("Segoe UI", 9, "bold"),
            bg="#2e86c1", fg="white", relief="flat", cursor="hand2",
            state="disabled", command=self._aplicar_valor_corrida)
        self.btn_aplicar_corrida.pack(side="left", padx=(0, 8), ipadx=6, ipady=3)
        Tooltip(self.btn_aplicar_corrida,
                "El valor se usa en el proximo EJECUTAR PIPELINE, pero\n"
                "criterios_adoptados.py NO se modifica.")

        self.btn_quitar_declarado = tk.Button(
            f_botones, text="Quitar declaracion de la corrida", font=("Segoe UI", 9),
            relief="flat", cursor="hand2", state="disabled",
            command=self._quitar_valor_corrida)
        self.btn_quitar_declarado.pack(side="left", padx=8, ipadx=6, ipady=3)

        self.btn_ventana_norma = tk.Button(
            f_botones, text="Ver la norma y declarar desde la tabla...",
            font=("Segoe UI", 9, "bold"), bg="#5d6d7e", fg="white",
            relief="flat", cursor="hand2", state="disabled",
            command=self._abrir_ventana_normativa)
        self.btn_ventana_norma.pack(side="left", padx=8, ipadx=6, ipady=3)
        Tooltip(self.btn_ventana_norma,
                "Abre la ventana emergente de la variable: la tabla COMPLETA\n"
                "con su numeral, su pagina impresa, sus notas al pie y sus\n"
                "modificadores; o el rango con su semantica; o el catalogo con\n"
                "la advertencia de que ninguna norma lo sostiene.\n"
                "Al declarar desde alli queda registrada la procedencia: fila,\n"
                "valor, alternativas descartadas, cita y fecha.")

        self.btn_guardar_archivo = tk.Button(
            f_botones, text="Guardar en archivo fuente (permanente)", font=("Segoe UI", 9, "bold"),
            bg="#c0392b", fg="white", relief="flat", cursor="hand2",
            state="disabled", command=self._guardar_valor_en_archivo)
        self.btn_guardar_archivo.pack(side="left", padx=8, ipadx=6, ipady=3)
        Tooltip(self.btn_guardar_archivo,
                "Reescribe 'valor=None' por este valor DIRECTAMENTE en\n"
                "criterios_adoptados.py. Pide confirmacion. Etiqueta,\n"
                "justificacion y fuente no se tocan: revisalas a mano si\n"
                "el criterio deja de ser [A]/pendiente.")

        self.lbl_estado_criterio = ttk.Label(p, text="", style="Ayuda.TLabel",
                                              wraplength=980, justify="left")
        self.lbl_estado_criterio.grid(row=4, column=0, sticky="w", padx=10, pady=(0, 10))

        self._clave_criterio_seleccionado = None
        self._llenar_tabla_criterios()

    def _estado_criterio(self, clave):
        """(texto, tag) del estado de un criterio para la tabla y el detalle."""
        if ca.declarado_en_caliente(clave):
            return "declarado (corrida)", "declarado_corrida"
        if ca.criterio(clave).valor is None:
            return "PENDIENTE", "pendiente"
        return "resuelto", "resuelto"

    def _llenar_tabla_criterios(self):
        for item in self.tree_criterios_todos.get_children():
            self.tree_criterios_todos.delete(item)
        # El valor efectivo NO se recalcula aqui: lo da `criterio_efectivo`,
        # la misma funcion que leen M11 y el JSON. Tres copias de la regla
        # "override si lo hay, archivo si no" son tres sitios donde puede
        # divergir, y esa divergencia fue el hallazgo bloqueante SIS-A-01.
        for clave in sorted(ca.CRITERIOS):
            c = ca.criterio(clave)
            valor_efectivo = ca.criterio_efectivo(clave).valor
            estado_txt, tag = self._estado_criterio(clave)
            self.tree_criterios_todos.insert("", "end", iid=clave, values=(
                clave, c.etiqueta, c.concepto,
                "(sin declarar)" if valor_efectivo is None else repr(valor_efectivo),
                estado_txt, c.fuente,
            ), tags=(tag,))

    def _al_seleccionar_criterio(self, _evt=None):
        seleccion = self.tree_criterios_todos.selection()
        self.txt_detalle_criterio.configure(state="normal")
        self.txt_detalle_criterio.delete("1.0", "end")
        if not seleccion:
            self._clave_criterio_seleccionado = None
            self.lbl_criterio_seleccionado.config(text="(ninguno seleccionado)")
            self.btn_aplicar_corrida.config(state="disabled")
            self.btn_quitar_declarado.config(state="disabled")
            self.btn_guardar_archivo.config(state="disabled")
            self.btn_ventana_norma.config(state="disabled")
            self.txt_detalle_criterio.configure(state="disabled")
            return

        clave = seleccion[0]
        c = ca.criterio(clave)
        self._clave_criterio_seleccionado = clave
        self.lbl_criterio_seleccionado.config(text=clave)

        lineas = [
            f"Justificacion : {c.justificacion}",
            f"Fuente        : {c.fuente}",
            f"Se resuelve   : {ve.variable(clave).modo.value} "
            "(doble clic abre su ventana normativa)",
        ]
        procedencia = dec.procedencia_de(clave)
        if procedencia is not None:
            lineas.append(f"Procedencia   : {procedencia.como_texto()}")
        if c.reemplazado_por:
            lineas.append(f"Se sustituye por: {c.reemplazado_por}")
        if c.sensibilidad:
            lineas.append(f"Sensibilidad  : {c.sensibilidad}")
        if c.trazabilidad:
            lineas.append(f"Trazabilidad  : {c.trazabilidad}")
        if c.verificacion_pendiente:
            lineas.append(f">> VERIFICAR  : {c.verificacion_pendiente}")
        self.txt_detalle_criterio.insert("1.0", "\n".join(lineas))
        self.txt_detalle_criterio.configure(state="disabled")

        valor_actual = ca.criterio_efectivo(clave).valor
        self.valor_declarado_var.set("" if valor_actual is None else str(valor_actual))

        en_caliente = ca.declarado_en_caliente(clave)
        puede_declarar = c.valor is None or en_caliente
        self.btn_aplicar_corrida.config(state="normal" if puede_declarar or c.valor is None else "disabled")
        self.btn_quitar_declarado.config(state="normal" if en_caliente else "disabled")
        self.btn_guardar_archivo.config(state="normal")
        self.btn_ventana_norma.config(state="normal")

    def _abrir_ventana_normativa(self, _evt=None):
        """
        Abre la ventana emergente del criterio seleccionado.

        `al_declarar` refresca la tabla de esta pestana: la ventana declara
        por `declaracion`, que declara por `establecer_valor_dinamico`, y sin
        el refresco la fila seguiria diciendo PENDIENTE con el valor ya
        gobernando el calculo --- que es la forma que tenia SIS-A-01.
        """
        clave = self._clave_criterio_seleccionado
        if not clave:
            return
        ventana_norma.abrir(self.root, clave,
                            al_declarar=self._tras_declarar_en_ventana)

    def _tras_declarar_en_ventana(self, clave):
        self.lbl_estado_criterio.config(
            text=f"'{clave}' declarado desde su ventana normativa, SOLO para "
                 "la proxima corrida, con su procedencia registrada. "
                 "criterios_adoptados.py no se modifico.",
            foreground=COLOR_AVISO)
        self._llenar_tabla_criterios()
        self.tree_criterios_todos.selection_set(clave)

    def _interpretar_valor_declarado(self, texto):
        """
        Interpreta lo que el proyectista teclea en el campo de declaracion en
        caliente: un numero si lo parece (admitiendo la coma decimal, que es
        como se escribe aqui), y el texto tal cual si no.

        SIS-E-04. El `ValueError` de abajo NO es de la taxonomia de
        `ErrorProyecto`, y es deliberado: un widget vacio todavia no es un
        dato del expediente -- no hay columna que añadir ni celda que
        corregir --, y la excepcion NUNCA sale de esta clase: los dos
        llamadores (`_aplicar_valor_corrida` y `_guardar_valor_en_archivo`) la
        atrapan tres lineas mas abajo y la convierten en el rotulo rojo del
        panel. Es control de flujo de un widget, no un problema que la GUI
        tenga que distinguir de un fallo del programa, que es para lo que
        CLAUDE.md pide la taxonomia.

        DIVERGE de `cli.declarar_criterios`, y esta escrito para que se vea:
        la CLI resuelve el texto con `ast.literal_eval` -- admite listas y
        dicts, y leeria '1,5' como la TUPLA (1, 5) -- y aqui se admite la coma
        decimal, que para quien teclea en la ventana es lo natural. Unificar
        las dos por el lado de la CLI convertiria '1,5' en una tupla valida en
        silencio, que es una regresion peor que la duplicacion. La divergencia
        esta fijada por un test de contrato en tests/test_gui_contrato.py.
        """
        texto = texto.strip()
        if texto == "":
            raise ValueError("El valor no puede quedar vacio.")
        try:
            return float(texto.replace(",", "."))
        except ValueError:
            return texto

    def _aplicar_valor_corrida(self):
        clave = self._clave_criterio_seleccionado
        if not clave:
            return
        # `establecer_valor_dinamico` entra en el try: desde que somete la
        # declaracion a la guardia de criterios_adoptados, rechaza un valor
        # fuera del rango de sensibilidad con ValueError. Fuera del try, ese
        # rechazo salia como traceback de Tk en vez de como mensaje leible.
        try:
            valor_nuevo = self._interpretar_valor_declarado(self.valor_declarado_var.get())
            ca.establecer_valor_dinamico(clave, valor_nuevo)
        except (ValueError, KeyError) as exc:
            self.lbl_estado_criterio.config(text=f"Error: {exc}", foreground=COLOR_ERROR)
            return
        self.lbl_estado_criterio.config(
            text=f"'{clave}' declarado a {valor_nuevo!r} SOLO para la proxima corrida. "
                 "criterios_adoptados.py no se modifico.",
            foreground=COLOR_AVISO)
        self._llenar_tabla_criterios()
        self.tree_criterios_todos.selection_set(clave)

    def _quitar_valor_corrida(self):
        clave = self._clave_criterio_seleccionado
        if not clave:
            return
        # `dec.olvidar` retira el valor Y su procedencia. Retirar solo el
        # valor dejaria una procedencia hablando de un numero que ya no
        # gobierna nada, que es peor que no tener procedencia.
        dec.olvidar(clave)
        self.lbl_estado_criterio.config(
            text=f"Se quito la declaracion de '{clave}': vuelve a bloquear el calculo.",
            foreground=COLOR_AVISO)
        self._llenar_tabla_criterios()
        self.tree_criterios_todos.selection_set(clave)

    def _guardar_valor_en_archivo(self):
        clave = self._clave_criterio_seleccionado
        if not clave:
            return
        try:
            valor_nuevo = self._interpretar_valor_declarado(self.valor_declarado_var.get())
        except ValueError as exc:
            self.lbl_estado_criterio.config(text=f"Error: {exc}", foreground=COLOR_ERROR)
            return

        confirmado = messagebox.askyesno(
            "Confirmar escritura permanente",
            f"Esto reescribe 'valor=' de '{clave}' en criterios_adoptados.py "
            f"con el valor {valor_nuevo!r}.\n\n"
            "Es un cambio PERMANENTE al archivo fuente del proyecto, no solo "
            "a esta corrida. Etiqueta, justificacion y fuente del criterio "
            "no se actualizan solos: revisalas a mano si corresponde.\n\n"
            "¿Confirma que quiere escribir el archivo?",
            icon="warning",
        )
        if not confirmado:
            return
        try:
            ca.escribir_valor_en_archivo(clave, valor_nuevo)
        except (KeyError, ValueError, OSError) as exc:
            messagebox.showerror("No se pudo escribir el archivo", str(exc))
            return
        self.lbl_estado_criterio.config(
            text=f"'{clave}' = {valor_nuevo!r} escrito en criterios_adoptados.py.",
            foreground=COLOR_OK)
        self._llenar_tabla_criterios()
        self.tree_criterios_todos.selection_set(clave)

    # -------------------------- Pestana 3 -----------------------------
    def _construir_tab_puntos(self, p):
        p.columnconfigure(0, weight=1)
        p.rowconfigure(0, weight=1)

        f_tabla = ttk.Frame(p, padding=10)
        f_tabla.grid(row=0, column=0, sticky="nsew")
        f_tabla.columnconfigure(0, weight=1)
        f_tabla.rowconfigure(0, weight=1)

        cols = ("id", "progresiva", "familia", "dimensionado", "material", "D",
                "control", "HW", "V_erosion", "V_sedimentacion",
                "incumplidas", "bloqueos")
        self.tree_puntos = ttk.Treeview(f_tabla, columns=cols, show="headings", height=14)
        encabezados = [
            ("id", "Punto", 70, "w"),  # literal-ok: ancho de columna, px
            ("progresiva", "Progresiva", 90, "center"),  # literal-ok: ancho de columna, px
            ("familia", "Familia", 60, "center"),  # literal-ok: ancho de columna, px
            ("dimensionado", "Dimensionado", 90, "center"),  # literal-ok: ancho de columna, px
            ("material", "Material", 140, "w"),  # literal-ok: ancho de columna, px
            ("D", "D (m)", 65, "center"),  # literal-ok: ancho de columna, px
            ("control", "Control", 75, "center"),  # literal-ok: ancho de columna, px
            ("HW", "HW (m)", 70, "center"),  # literal-ok: ancho de columna, px
            # Dos columnas, no una: la velocidad contra los techos (V3, d50)
            # y la del piso (V2) se calculan con n distinto y no son el mismo
            # numero (MAT-D1).
            ("V_erosion", "V n min (m/s)", 90, "center"),  # literal-ok: ancho de columna, px
            ("V_sedimentacion", "V n max (m/s)", 90, "center"),  # literal-ok: ancho de columna, px
            ("incumplidas", "Verif. NO", 75, "center"),  # literal-ok: ancho de columna, px
            ("bloqueos", "Bloqueos", 75, "center"),  # literal-ok: ancho de columna, px
        ]
        for col, txt, ancho, anchor in encabezados:
            self.tree_puntos.heading(col, text=txt)
            self.tree_puntos.column(col, width=ancho, anchor=anchor)
        self.tree_puntos.grid(row=0, column=0, sticky="nsew")
        self.tree_puntos.tag_configure("no_dimensionado", background="#fdecea")
        self.tree_puntos.tag_configure("con_bloqueos", foreground=COLOR_AVISO)
        self.tree_puntos.bind("<<TreeviewSelect>>", self._al_seleccionar_punto)

        scroll = ttk.Scrollbar(f_tabla, orient="vertical", command=self.tree_puntos.yview)
        self.tree_puntos.configure(yscroll=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        ttk.Label(p, text="Detalle del punto seleccionado", style="Header.TLabel",
                  padding=(10, 0)).grid(row=1, column=0, sticky="w")

        f_detalle = ttk.Frame(p, padding=10)
        f_detalle.grid(row=2, column=0, sticky="nsew")
        p.rowconfigure(2, weight=1)
        f_detalle.columnconfigure(0, weight=1)
        f_detalle.rowconfigure(0, weight=1)

        self.txt_detalle = tk.Text(f_detalle, height=12, wrap="word", font=("Consolas", 9))
        self.txt_detalle.grid(row=0, column=0, sticky="nsew")
        self.txt_detalle.configure(state="disabled")
        scroll_det = ttk.Scrollbar(f_detalle, orient="vertical", command=self.txt_detalle.yview)
        self.txt_detalle.configure(yscroll=scroll_det.set)
        scroll_det.grid(row=0, column=1, sticky="ns")

    def _al_seleccionar_punto(self, _evt=None):
        seleccion = self.tree_puntos.selection()
        self.txt_detalle.configure(state="normal")
        self.txt_detalle.delete("1.0", "end")
        if seleccion and self.informe is not None:
            id_punto = seleccion[0]
            informe_punto = next((i for i in self.informe.puntos if i.punto.id == id_punto), None)
            if informe_punto is not None:
                self.txt_detalle.insert("1.0", "\n".join(cli._lineas_punto(informe_punto)))
        self.txt_detalle.configure(state="disabled")

    # -------------------------- Pestana 4 -----------------------------
    def _construir_tab_resumen(self, p):
        ttk.Label(p, text="Estado del expediente", style="Header.TLabel").pack(anchor="w")

        f_res = ttk.LabelFrame(p, text="Resumen", padding=12)
        f_res.pack(fill="x", pady=(8, 12))
        f_res.columnconfigure(1, weight=1)

        etiquetas = ["CSV", "Alcance de la corrida", "Puntos del expediente",
                     "Puntos dimensionados", "Verificaciones incumplidas",
                     "Etapas bloqueadas", "Diferidas por alcance",
                     "Expediente cerrado"]
        self.lbl_resumen = {}
        for fila, txt in enumerate(etiquetas):
            ttk.Label(f_res, text=f"{txt}:").grid(row=fila, column=0, sticky="w", pady=3)
            lbl = ttk.Label(f_res, text="-", style="Res.TLabel")
            lbl.grid(row=fila, column=1, sticky="w", padx=12, pady=3)
            self.lbl_resumen[txt] = lbl

        ttk.Label(p, text="Criterios pendientes que bloquearon una etapa (Sec. 0.7)",
                  style="Header.TLabel").pack(anchor="w", pady=(4, 2))
        ttk.Label(p, text="Un criterio con valor=None cuya etapa se invoco en esta corrida. "
                          "No es un defecto silencioso: el calculo se detuvo hasta declararlo.",
                  style="Ayuda.TLabel", wraplength=820, justify="left").pack(anchor="w", pady=(0, 8))

        f_crit = ttk.Frame(p)
        f_crit.pack(fill="both", expand=False, pady=4)
        cols = ("clave", "etiqueta", "concepto", "fuente", "fases", "puntos")
        self.tree_criterios = ttk.Treeview(f_crit, columns=cols, show="headings", height=8)
        encabezados = [
            ("clave", "Clave", 130, "w"),  # literal-ok: ancho de columna, px
            ("etiqueta", "Etiqueta", 60, "center"),  # literal-ok: ancho de columna, px
            ("concepto", "Concepto", 220, "w"),  # literal-ok: ancho de columna, px
            ("fuente", "Fuente que lo resolveria", 220, "w"),  # literal-ok: ancho de columna, px
            ("fases", "Fases", 140, "w"),  # literal-ok: ancho de columna, px
            ("puntos", "Puntos", 140, "w"),  # literal-ok: ancho de columna, px
        ]
        for col, txt, ancho, anchor in encabezados:
            self.tree_criterios.heading(col, text=txt)
            self.tree_criterios.column(col, width=ancho, anchor=anchor)
        self.tree_criterios.pack(side="left", fill="both", expand=True)
        scroll_c = ttk.Scrollbar(f_crit, orient="vertical", command=self.tree_criterios.yview)
        self.tree_criterios.configure(yscroll=scroll_c.set)
        scroll_c.pack(side="left", fill="y")

        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=12)

        ttk.Label(p, text="Exportacion", style="Header.TLabel").pack(anchor="w", pady=(0, 6))
        f_exp = ttk.Frame(p)
        f_exp.pack(fill="x")

        self.btn_json = tk.Button(f_exp, text="Exportar JSON", font=("Segoe UI", 9, "bold"),
                                  bg="#16a085", fg="white", relief="flat", cursor="hand2",
                                  state="disabled", command=self.exportar_json)
        self.btn_json.pack(side="left", padx=(0, 8), ipadx=8, ipady=4)

        self.btn_html = tk.Button(f_exp, text="Exportar memoria (HTML)", font=("Segoe UI", 9, "bold"),
                                  bg="#2e86c1", fg="white", relief="flat", cursor="hand2",
                                  state="disabled", command=self.exportar_html)
        self.btn_html.pack(side="left", padx=8, ipadx=8, ipady=4)

        self.btn_pdf = tk.Button(f_exp, text="Exportar memoria (PDF)", font=("Segoe UI", 9, "bold"),
                                 bg="#8e44ad", fg="white", relief="flat", cursor="hand2",
                                 state="disabled", command=self.exportar_pdf)
        self.btn_pdf.pack(side="left", padx=8, ipadx=8, ipady=4)
        Tooltip(self.btn_pdf, "Usa weasyprint si esta instalado.\n"
                              "Si no lo esta, abre la memoria en el navegador\n"
                              "para imprimirla como PDF (Ctrl+P).")

        self.btn_csv = tk.Button(f_exp, text="Exportar cuadro resumen (CSV)", font=("Segoe UI", 9, "bold"),
                                 bg="#16a085", fg="white", relief="flat", cursor="hand2",
                                 state="disabled", command=self.exportar_csv)
        self.btn_csv.pack(side="left", padx=8, ipadx=8, ipady=4)
        Tooltip(self.btn_csv, "El cuadro resumen (entregable 3 de M11), una fila\n"
                              "por punto, en una hoja de calculo.")

    # ------------------------------------------------------------------
    # Lectura de banderas
    # ------------------------------------------------------------------
    def _leer_banderas(self):
        """
        Los valores de texto de CAMPOS_EXTERNOS, tal como los espera
        `cargar_datos_externos`: None si el campo quedo vacio.
        """
        banderas = {}
        for clave, *_resto in CAMPOS_EXTERNOS:
            texto = self.externos_vars[clave].get().strip()
            if clave == "l_hidraulico":
                clave_bandera = "L_hidraulico_m"
            else:
                clave_bandera = clave
            banderas[clave_bandera] = None
            if texto:
                if clave == "categoria_tr":
                    banderas[clave_bandera] = texto
                else:
                    banderas[clave_bandera] = texto.replace(",", ".")
        return banderas

    # ------------------------------------------------------------------
    # Ejecucion del pipeline
    # ------------------------------------------------------------------
    def ejecutar_pipeline(self):
        self.lbl_error_datos.config(text="")
        ruta_csv_texto = self.csv_var.get().strip()
        if not ruta_csv_texto:
            self.lbl_error_datos.config(text="Debe seleccionar el CSV de puntos criticos.")
            self.nb.select(self.tab_datos)
            return
        ruta_csv = Path(ruta_csv_texto)

        ruta_externos = None
        texto_externos = self.datos_externos_var.get().strip()
        if texto_externos:
            ruta_externos = Path(texto_externos)

        self.btn_ejecutar.config(state="disabled", text="Ejecutando...")
        self.root.update_idletasks()
        try:
            externos = cli.cargar_datos_externos(ruta_externos, self._leer_banderas())
            self.informe = cli.correr(ruta_csv, externos,
                                      alcance=self.alcance_var.get())
        # SIS-E-01. Este brazo capturaba (OSError, ValueError), y ValueError
        # es la excepcion mas comun de un fallo de PROGRAMA nacido dentro del
        # pipeline: cualquiera de ellos se mostraba al proyectista como "No se
        # pudo leer la entrada", que le hace revisar el CSV en vez de reportar
        # el defecto, y ademas se comia el brazo de abajo, que es el que
        # imprime la traza. La CLI ya usaba el brazo estrecho correcto
        # (cli.py::main). Las TRES formas en que la ENTRADA puede fallar al
        # LEERSE: la de E/S (OSError), la del texto que no es UTF-8
        # (UnicodeDecodeError, que es subclase de ValueError y por lo tanto no
        # entra sola) y la del JSON mal formado. La segunda no es teorica en
        # este expediente: un CSV o un JSON guardado en ANSI por Excel en
        # Windows -- con las eñes del castellano -- estrellaria la ventana con
        # una traza en vez de decir que el archivo no esta en UTF-8.
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._mostrar_error_entrada(f"No se pudo leer la entrada:\n{exc}")
            return
        except ErrorProyecto as exc:
            self._mostrar_error_entrada(f"El expediente no se puede cargar:\n{exc}")
            return
        except Exception as exc:  # fallo de programa: se muestra con traza
            traceback.print_exc()
            messagebox.showerror("Error inesperado", f"{type(exc).__name__}: {exc}")
            return
        finally:
            self.btn_ejecutar.config(state="normal", text="EJECUTAR PIPELINE (M0 -> M10)")

        self._llenar_tabla_puntos()
        self._llenar_resumen()
        for btn in (self.btn_json, self.btn_html, self.btn_pdf, self.btn_csv):
            btn.config(state="normal")
        self.lbl_estado.config(
            text=f"Ejecutado ({self.informe.generado}). "
                 f"{self.informe.dimensionados}/{len(self.informe.puntos)} puntos dimensionados. "
                 f"Expediente {'cerrado' if self.informe.cerrado else 'NO cerrado'}.")
        self.nb.select(self.tab_puntos)

    def _mostrar_error_entrada(self, mensaje):
        self.lbl_error_datos.config(text=mensaje)
        self.nb.select(self.tab_datos)
        self.btn_ejecutar.config(state="normal", text="EJECUTAR PIPELINE (M0 -> M10)")

    # ------------------------------------------------------------------
    # Volcado a las tablas
    # ------------------------------------------------------------------
    def _llenar_tabla_puntos(self):
        for item in self.tree_puntos.get_children():
            self.tree_puntos.delete(item)
        for informe_punto in self.informe.puntos:
            punto = informe_punto.punto
            incumplidas = len(informe_punto.incumplidas())
            n_bloqueos = len(informe_punto.bloqueos)
            if informe_punto.dimensionado:
                r = informe_punto.resultado
                h = r.resultado_hidraulico
                material, D = r.material.nombre, f"{r.D:.2f}"
                control, HW = h.control_gobernante.value, f"{h.HW:.3f}"
                V_ero = f"{h.V_erosion:.2f}"
                V_sed = f"{h.V_sedimentacion:.2f}"
            else:
                material = D = control = HW = V_ero = V_sed = "-"

            tags = []
            if not informe_punto.dimensionado:
                tags.append("no_dimensionado")
            if n_bloqueos:
                tags.append("con_bloqueos")

            self.tree_puntos.insert("", "end", iid=punto.id, values=(
                punto.id, punto.progresiva_display, punto.familia.value,
                "si" if informe_punto.dimensionado else "no",
                material, D, control, HW, V_ero, V_sed, incumplidas,
                n_bloqueos,
            ), tags=tuple(tags))

        self.txt_detalle.configure(state="normal")
        self.txt_detalle.delete("1.0", "end")
        self.txt_detalle.configure(state="disabled")

    def _llenar_resumen(self):
        informe = self.informe
        incumplidas = sum(len(i.incumplidas()) for i in informe.puntos)
        n_bloqueos = len(informe.bloqueos())
        diferidas = len(informe.diferidos())
        self.lbl_resumen["CSV"].config(text=str(informe.csv))
        self.lbl_resumen["Alcance de la corrida"].config(text=informe.alcance)
        # Lo diferido por alcance NO es un bloqueo y no cuenta para `cerrado`:
        # es una etapa que ESTA corrida declaro fuera de su alcance. Se
        # imprime aparte, con su fundamento, porque «cerrado a nivel de
        # perfil» no significa que el expediente este completo.
        self.lbl_resumen["Diferidas por alcance"].config(
            text=str(diferidas),
            foreground=COLOR_AVISO if diferidas else COLOR_OK)
        self.lbl_resumen["Puntos del expediente"].config(text=str(len(informe.puntos)))
        self.lbl_resumen["Puntos dimensionados"].config(text=str(informe.dimensionados))
        self.lbl_resumen["Verificaciones incumplidas"].config(
            text=str(incumplidas), foreground=COLOR_ERROR if incumplidas else COLOR_OK)
        self.lbl_resumen["Etapas bloqueadas"].config(
            text=str(n_bloqueos), foreground=COLOR_AVISO if n_bloqueos else COLOR_OK)
        self.lbl_resumen["Expediente cerrado"].config(
            text="si" if informe.cerrado else "no",
            foreground=COLOR_OK if informe.cerrado else COLOR_ERROR)

        for item in self.tree_criterios.get_children():
            self.tree_criterios.delete(item)
        for c in cli.criterios_bloqueantes(informe):
            puntos = ", ".join(c.puntos) if c.puntos else "proyecto (Fase 9)"
            self.tree_criterios.insert("", "end", values=(
                c.clave, c.etiqueta, c.concepto, c.fuente,
                ", ".join(c.fases), puntos))

    # ------------------------------------------------------------------
    # Exportacion
    # ------------------------------------------------------------------
    def _plantilla(self):
        """
        La plantilla de la memoria, por la MISMA via que `cli.main`.

        Se lee del alcance del INFORME y no del selector: entre ejecutar y
        exportar el usuario puede haber movido el radio, y la memoria tiene
        que describir la corrida que se hizo, no la que se hara. Sin informe
        --- los botones estan deshabilitados, pero el metodo es publico ---
        manda el selector.
        """
        alcance = (self.informe.alcance if self.informe is not None
                   else self.alcance_var.get())
        return cli.plantilla_por_alcance(alcance)

    def exportar_json(self):
        if self.informe is None:
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar JSON del expediente", defaultextension=".json",
            filetypes=[("Archivo JSON", "*.json")],
            initialfile=self.informe.csv.with_suffix(".informe.json").name,
        )
        if not ruta:
            return
        try:
            Path(ruta).write_text(
                json.dumps(cli.informe_json(self.informe), ensure_ascii=False,
                           indent=2, allow_nan=False),
                encoding="utf-8")
            messagebox.showinfo("JSON exportado", f"Archivo: {ruta}")
        except (OSError, ErrorProyecto) as exc:
            messagebox.showerror("Error al exportar", f"{exc}")
        except Exception as exc:  # fallo de programa: se muestra con traza
            # Son CUATRO exportadores, no tres. Este quedaba con `except
            # OSError` a secas, y su cuerpo llama a `cli.informe_json` y a
            # `json.dumps(..., allow_nan=False)`: un ErrorProyecto al armar el
            # informe, o un ValueError de json por un NaN, escapaban del
            # manejador entero y el usuario no veia NADA -- ni mensaje ni
            # traza en la ventana.
            traceback.print_exc()
            messagebox.showerror("Error inesperado", f"{type(exc).__name__}: {exc}")

    def exportar_html(self):
        if self.informe is None:
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar memoria de calculo (HTML)", defaultextension=".html",
            filetypes=[("Archivo HTML", "*.html")],
        )
        if not ruta:
            return
        try:
            cli.exportar_html(self.informe, Path(ruta),
                              proyecto=self.proyecto_var.get(),
                              ruta_plantilla=self._plantilla())
            messagebox.showinfo("Memoria exportada", f"Archivo: {ruta}")
        except (OSError, ErrorProyecto) as exc:
            messagebox.showerror("Error al exportar", f"{exc}")
        except Exception as exc:  # fallo de programa: se muestra con traza
            traceback.print_exc()
            messagebox.showerror("Error inesperado", f"{type(exc).__name__}: {exc}")

    def exportar_pdf(self):
        if self.informe is None:
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar memoria de calculo (PDF)", defaultextension=".pdf",
            filetypes=[("Archivo PDF", "*.pdf")],
        )
        if not ruta:
            return
        try:
            resultado = cli.exportar_pdf(self.informe, Path(ruta),
                                         proyecto=self.proyecto_var.get(),
                                         ruta_plantilla=self._plantilla())
            messagebox.showinfo("Memoria exportada", resultado.mensaje)
        except (OSError, ErrorProyecto) as exc:
            messagebox.showerror("Error al exportar", f"{exc}")
        except Exception as exc:  # fallo de programa: se muestra con traza
            traceback.print_exc()
            messagebox.showerror("Error inesperado", f"{type(exc).__name__}: {exc}")

    def exportar_csv(self):
        if self.informe is None:
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar cuadro resumen (CSV)", defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")],
            initialfile=self.informe.csv.with_suffix(".resumen.csv").name,
        )
        if not ruta:
            return
        try:
            cli.exportar_csv(self.informe, Path(ruta))
            messagebox.showinfo("CSV exportado", f"Archivo: {ruta}")
        except (OSError, ErrorProyecto) as exc:
            messagebox.showerror("Error al exportar", f"{exc}")
        except Exception as exc:  # fallo de programa: se muestra con traza
            traceback.print_exc()
            messagebox.showerror("Error inesperado", f"{type(exc).__name__}: {exc}")

    # ------------------------------------------------------------------
    # Sesion (JSON) - patron de legacy/Tc.py
    # ------------------------------------------------------------------
    def guardar_sesion(self):
        # SIS-A-18. `criterios` y `alcance` son lo que faltaba: sin ellos, una
        # sesion guardada describia DONDE estaba el expediente y no QUE se
        # habia decidido sobre el, que es la parte que cuesta rehacer.
        data = {
            "formato_version": FORMATO_SESION,
            "app_version": APP_VERSION,
            "proyecto": self.proyecto_var.get(),
            "csv": self.csv_var.get(),
            "datos_externos": self.datos_externos_var.get(),
            "externos": {clave: var.get() for clave, var in self.externos_vars.items()},
            "alcance": self.alcance_var.get(),
            "criterios": dec.estado_de_sesion(),
        }
        ruta = filedialog.asksaveasfilename(
            title="Guardar sesion", defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json")],
            initialfile=f"sesion_{self.proyecto_var.get() or 'expediente'}.json",
        )
        if not ruta:
            return
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Exito", "Sesion guardada correctamente.")
        except OSError as exc:
            messagebox.showerror("Error al guardar", f"No se pudo escribir el archivo:\n{exc}")

    def cargar_sesion(self):
        ruta = filedialog.askopenfilename(
            title="Cargar sesion", filetypes=[("Archivos JSON", "*.json")])
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            # `UnicodeDecodeError` va aqui por la MISMA razon que en
            # `ejecutar_pipeline`, y faltaba: un JSON de sesion guardado en
            # ANSI por un editor de Windows --- con las eñes del castellano ---
            # estrellaba la ventana con una traza en vez de decir que el
            # archivo no esta en UTF-8. Es subclase de ValueError, no de
            # OSError ni de JSONDecodeError, de modo que este brazo no lo veia.
            messagebox.showerror("Error al cargar", f"No se pudo leer la sesion:\n{exc}")
            return
        if not isinstance(data, dict):
            # Un JSON VALIDO que no sea objeto --- `[1, 2]`, `"texto"`, `3` ---
            # pasa `json.load` sin error y revienta tres lineas mas abajo en
            # `data.get(...)` con un `AttributeError` que nadie captura. Es un
            # archivo mal formado, no un fallo del programa, y sale por el
            # mismo sitio que los demas archivos mal formados.
            messagebox.showerror(
                "Error al cargar",
                "El archivo es JSON valido pero no es una sesion: una sesion "
                f"es un objeto con claves, y este trae {type(data).__name__}.")
            return

        version = data.get("formato_version", 1)

        self.proyecto_var.set(data.get("proyecto", ""))
        self.csv_var.set(data.get("csv", ""))
        self.datos_externos_var.set(data.get("datos_externos", ""))
        for clave, valor in data.get("externos", {}).items():
            if clave in self.externos_vars:
                self.externos_vars[clave].set(valor)
        # Un alcance que la sesion no traiga (o que traiga escrito mal) NO se
        # adopta en silencio: se queda el defecto de `cli.py`, que es el mismo
        # que la ventana muestra al abrirse.
        alcance = data.get("alcance", cli.ALCANCE_EXPEDIENTE)
        if alcance not in (cli.ALCANCE_PERFIL, cli.ALCANCE_EXPEDIENTE):
            alcance = cli.ALCANCE_EXPEDIENTE
        self.alcance_var.set(alcance)

        aviso = self._restaurar_criterios(data.get("criterios"))

        self.lbl_error_datos.config(text="")
        self._llenar_tabla_criterios()
        self.nb.select(self.tab_datos)
        if version < FORMATO_SESION:
            aviso = (f"La sesion se guardo con el formato v{version} y se "
                     f"leyo como v{FORMATO_SESION}. Las sesiones v1 no "
                     "guardaban ni el alcance de la corrida ni los criterios "
                     "declarados: revise las dos cosas antes de ejecutar. "
                     + aviso)
        if aviso:
            messagebox.showinfo("Sesion cargada", aviso)

    def _restaurar_criterios(self, bloque):
        """
        Repone los criterios declarados que la sesion traiga (SIS-A-18).

        Todo pasa por `declaracion.restaurar_sesion`, que declara por
        `establecer_valor_dinamico` -- la misma guardia que el archivo -- y
        devuelve lo restaurado Y lo rechazado. Un JSON de sesion es un archivo
        que alguien pudo editar a mano: aceptar sus valores sin guardia
        convertiria el formato de sesion en la puerta de atras que este
        proyecto no tiene, y descartarlos en silencio esconderia justo el caso
        que importa -- el criterio que la sesion traia y que hoy la guardia
        rechaza.
        """
        if bloque is None:
            return ""
        try:
            resultado = dec.restaurar_sesion(bloque)
        except (ValueError, KeyError) as exc:
            return f"No se pudieron restaurar los criterios de la sesion: {exc}"
        partes = []
        if resultado.restaurados:
            partes.append(
                f"Criterios restaurados SOLO para esta corrida: "
                f"{', '.join(resultado.restaurados)}. "
                "criterios_adoptados.py no se modifico.")
        if resultado.hubo_rechazos:
            detalle = "; ".join(f"{clave}: {motivo}"
                                for clave, motivo in resultado.rechazados)
            partes.append(f"NO se restauraron: {detalle}")
        return " ".join(partes)


def main():
    root = tb.Window(themename="litera") if tb is not None else tk.Tk()
    ExpedienteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
