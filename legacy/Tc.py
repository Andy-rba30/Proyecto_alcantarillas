# -*- coding: utf-8 -*-
"""
Diseño Hidrológico - Estándar MTC
=================================
Memoria de cálculo hidrológico: tiempo de concentración (Kirpich y Témez),
curvas IDF por Dick y Peschke e intensidades de diseño.

Proyecto: Vía de Evitamiento - La Unión, Piura
          (Fases 3 y 4 de la hoja de ruta de delimitación de cuencas)

Dependencias obligatorias : numpy, matplotlib
Dependencias opcionales   : ttkbootstrap (tema visual), weasyprint (export PDF)
                            Si no están instaladas la aplicación funciona igual.

La plantilla de la memoria vive en "plantilla_memoria.html", junto a este
archivo, y se procesa con string.Template (delimitador "%%").


ESTATUS EN ESTE REPOSITORIO — LÉASE ANTES QUE NADA (SIS-B-10)
=============================================================
Esto NO es un módulo del calculador de alcantarillas. Es OTRO PROGRAMA, el
que está aguas arriba: calcula el tiempo de concentración y las curvas IDF,
y de ahí sale el caudal de diseño Q. La §1.2 de
`docs/hoja_de_ruta_alcantarillas_v8.md` lo dice por su nombre en la fila del
caudal — «Caudal de diseño Q | m³/s | Tc.py + IDF con TR de Fase 2» —, de
modo que Q entra al calculador como COLUMNA DEL CSV y este archivo es la
herramienta que la produce, fuera de la corrida.

Por eso se CONSERVA, y no por nostalgia. Lo que sí es cierto, y hay que
decirlo entero porque quien lo lea sin esta nota lo deducirá mal:

  * **Nadie lo importa, nadie lo prueba y el barrido de literales no lo
    recorre.** Sus 185 literales numéricos prohibidos no son
    una infracción pendiente: son código de otro programa, exento POR
    DIRECTORIO en `tests/test_sin_literales.DIRECTORIOS_FUERA_DEL_BARRIDO`,
    con la razón escrita ahí y comprobada por
    `test_la_razon_por_la_que_legacy_esta_exento_sigue_siendo_cierta`, que
    barre el AST del repositorio buscando importadores. Si alguien lo
    importara, ese test se pone en rojo y la exención cae.

  * **TAL COMO ESTÁ COMMITEADO NO CORRE AQUÍ**, y son dos cosas distintas:
    `matplotlib` es import de nivel superior y NO está en `requirements.txt`
    (ni debe estarlo: la §Estilo de CLAUDE.md fija las dependencias del
    software calculado y matplotlib no es una de ellas); y
    `plantilla_memoria.html`, que el encabezado de arriba anuncia «junto a
    este archivo», no existe en ningún punto del repositorio — `exportar_html`
    levanta `FileNotFoundError` con ese texto. Para volver a ejecutarlo hacen
    falta las dos cosas: instalar matplotlib fuera de `requirements.txt` y
    recuperar la plantilla del entorno donde este archivo se usó. Ninguna de
    las dos es trabajo del calculador de alcantarillas y por eso no se hacen
    aquí.

  * **Ya se le sacó lo que había que sacarle.** Los componentes de interfaz
    que `CLAUDE.md` manda reutilizar viven hoy en `gui/componentes.py`
    (`Tooltip` y `MarcoScroll`, el MISMO código movido; `CampoValidable`, que
    es su `_campo_validable` con la validación al escribir que pide la
    Sec. 4.3) y el patrón de plantilla `%%` en
    `M11_reporte.PlantillaHTML`. Leer este archivo para «no reinventar los
    componentes» ya no hace falta: están extraídos.

Qué haría falta para BORRARLO: que la §1.2 de la hoja de ruta dejara de
nombrarlo como origen de Q, o que su procedimiento entrara al calculador. Lo
primero es del autor de la hoja; lo segundo es una fase que no existe. Hasta
entonces, borrarlo dejaría al expediente sin la herramienta que produce una
de las columnas obligatorias de su CSV.
"""

import base64
import csv
import html
import io
import json
import os
import re
import tempfile
import webbrowser
from datetime import datetime
from string import Template

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib
matplotlib.use("Agg")  # sin backend interactivo: el gráfico solo se guarda a buffer
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------------------------------
# Dependencias opcionales
# --------------------------------------------------------------------------
try:
    import ttkbootstrap as tb
except ImportError:
    tb = None

try:
    from weasyprint import HTML as WeasyHTML
except Exception:  # ImportError o fallo de librerías nativas (GTK/cairo)
    WeasyHTML = None

# --------------------------------------------------------------------------
# Constantes
# --------------------------------------------------------------------------
APP_VERSION = "2.0"
FORMATO_SESION = 2                      # versión del JSON de sesión
NOMBRE_PLANTILLA = "plantilla_memoria.html"

EPSG_DEFECTO = "EPSG:32717 (WGS 84 / UTM zona 17S)"
FASE_DEFECTO = "Hoja de ruta - Fases 3 y 4 (delimitación de cuencas y modelamiento hidrológico)"

# Rango de pendientes para el que Kirpich fue calibrada (Tabla N.º 05, Manual MTC)
KIRPICH_S_MIN = 0.03
KIRPICH_S_MAX = 0.10

DURACIONES_MIN = [5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 360]
ENCODINGS_CSV = ("utf-8-sig", "utf-8", "cp1252", "latin-1")
MTC_KEYWORDS = ("normal", "gumbel", "log pearson", "log-pearson")

# Formatos unificados en toda la aplicación y en la memoria
DEC_L = 2      # longitud del cauce [m]
DEC_S = 4      # pendiente [m/m]
DEC_TC_H = 4   # tiempo de concentración [h]
DEC_TC_M = 2   # tiempo de concentración [min]
DEC_I = 2      # intensidades [mm/h]

COLOR_ERROR = "#e74c3c"
COLOR_OK = "#27ae60"


# ==========================================================================
# Funciones de cálculo (puras, sin dependencia de la interfaz)
# ==========================================================================
def tc_kirpich(L_m, S):
    """Tiempo de concentración de Kirpich, en horas. L en METROS, S en m/m."""
    return 0.000325 * (L_m ** 0.77) / (S ** 0.385)


def tc_temez(L_m, S):
    """Tiempo de concentración de Témez, en horas. L se convierte a KILÓMETROS."""
    L_km = L_m / 1000.0
    return 0.3 * (L_km / (S ** 0.25)) ** 0.76


def intensidad_dick_peschke(p24, t_horas):
    """Intensidad (mm/h) por desagregación de Dick y Peschke."""
    return (p24 * (t_horas / 24.0) ** 0.25) / t_horas


def nombre_archivo_seguro(texto, defecto="Memoria"):
    """Limpia un texto para usarlo como nombre de archivo en Windows/Linux."""
    limpio = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", texto or "")
    limpio = re.sub(r"\s+", "_", limpio).strip("._")
    reservados = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if not limpio or limpio.upper() in reservados:
        return defecto
    return limpio[:80]


class PlantillaHTML(Template):
    """string.Template con delimitador '%%' (el '$' se reserva para notación)."""
    delimiter = "%%"


# ==========================================================================
# Utilidades de interfaz
# ==========================================================================
class Tooltip:
    """Globo de ayuda simple para cualquier widget."""

    def __init__(self, widget, texto, retardo=400):
        self.widget = widget
        self.texto = texto
        self.retardo = retardo
        self._after_id = None
        self._tip = None
        widget.bind("<Enter>", self._programar, add="+")
        widget.bind("<Leave>", self._ocultar, add="+")
        widget.bind("<ButtonPress>", self._ocultar, add="+")

    def _programar(self, _evt=None):
        self._cancelar()
        self._after_id = self.widget.after(self.retardo, self._mostrar)

    def _cancelar(self):
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

    def _mostrar(self):
        if self._tip or not self.texto:
            return
        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self._tip = tk.Toplevel(self.widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self._tip, text=self.texto, justify="left", background="#ffffe0",
            relief="solid", borderwidth=1, font=("Segoe UI", 8), padx=6, pady=3,
        ).pack()

    def _ocultar(self, _evt=None):
        self._cancelar()
        if self._tip:
            self._tip.destroy()
            self._tip = None


class MarcoScroll(ttk.Frame):
    """Contenedor con scroll vertical: el contenido se agrega en `.interior`."""

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vbar.pack(side="right", fill="y")

        self.interior = ttk.Frame(self.canvas, padding=14)
        self._id_win = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")

        self.interior.bind("<Configure>", self._ajustar_region)
        self.canvas.bind("<Configure>", self._ajustar_ancho)
        self.canvas.bind("<Enter>", self._activar_rueda)
        self.canvas.bind("<Leave>", self._desactivar_rueda)

    def _ajustar_region(self, _evt=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_ancho(self, evt):
        self.canvas.itemconfigure(self._id_win, width=evt.width)

    def _activar_rueda(self, _evt=None):
        self.canvas.bind_all("<MouseWheel>", self._rueda)

    def _desactivar_rueda(self, _evt=None):
        self.canvas.unbind_all("<MouseWheel>")

    def _rueda(self, evt):
        # Los widgets con scroll propio (tabla K-S) manejan su propia rueda
        if isinstance(evt.widget, (ttk.Treeview, tk.Listbox, tk.Text)):
            return
        self.canvas.yview_scroll(int(-evt.delta / 120), "units")


# ==========================================================================
# Aplicación
# ==========================================================================
class HidroMTCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Diseño Hidrológico - Estándar MTC")
        self.root.geometry("960x780")
        self.root.minsize(820, 600)
        self.root.resizable(True, True)

        # ---- Variables principales -------------------------------------
        self.proyecto_var = tk.StringVar(value="Vía de Evitamiento La Unión - Región Piura")
        self.cuenca_var = tk.StringVar(value="Cuenca s/n - cauce principal")
        self.epsg_var = tk.StringVar(value=EPSG_DEFECTO)
        self.fase_var = tk.StringVar(value=FASE_DEFECTO)
        self.L_var = tk.StringVar()
        self.S_var = tk.StringVar()
        self.distribucion_var = tk.StringVar()
        self.metodo_tc_var = tk.StringVar(value="Kirpich")   # Tc adoptado para diseño
        self.dpi_var = tk.StringVar(value="150")
        self.png_aparte_var = tk.BooleanVar(value=False)

        # ---- Datos en memoria ------------------------------------------
        self.datos_precipitacion_dist = {}
        self.periodos = [10, 25, 50, 100, 500]
        self.p24_vars = {t: tk.StringVar() for t in self.periodos}
        self.cont_p24 = {}          # contenedores para marcar errores
        self.resultados = None      # último cálculo realizado

        self.distribucion_var.trace_add("write", self.actualizar_campos_p24)
        self.metodo_tc_var.trace_add("write", self._al_cambiar_metodo)
        for var in (self.L_var, self.S_var):
            var.trace_add("write", self._al_editar_geometria)

        self.crear_interfaz()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def crear_interfaz(self):
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
        self.style.configure("TButton", font=("Segoe UI", 9))
        self.style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"), foreground="#2c3e50")
        self.style.configure("Ayuda.TLabel", font=("Segoe UI", 8, "italic"), foreground="#666666")
        self.style.configure("Error.TLabel", font=("Segoe UI", 8, "bold"), foreground=COLOR_ERROR)
        self.style.configure("Res.TLabel", font=("Consolas", 11, "bold"), foreground="#1b4f72")

        try:
            self.color_borde_ok = self.style.lookup("TFrame", "background") or "SystemButtonFace"
        except tk.TclError:
            self.color_borde_ok = "SystemButtonFace"

        contenedor = ttk.Frame(self.root, padding=10)
        contenedor.pack(fill="both", expand=True)

        self.nb = ttk.Notebook(contenedor)
        self.nb.pack(fill="both", expand=True)

        self.tab_datos = MarcoScroll(self.nb)
        self.tab_dist = MarcoScroll(self.nb)
        self.tab_res = MarcoScroll(self.nb)
        self.nb.add(self.tab_datos, text="  1. Datos y geometría  ")
        self.nb.add(self.tab_dist, text="  2. Distribuciones (K-S)  ")
        self.nb.add(self.tab_res, text="  3. Resultados y memoria  ")

        self._construir_tab_datos(self.tab_datos.interior)
        self._construir_tab_distribuciones(self.tab_dist.interior)
        self._construir_tab_resultados(self.tab_res.interior)

        # ---- Barra inferior siempre visible ----------------------------
        barra = ttk.Frame(contenedor, padding=(0, 10, 0, 0))
        barra.pack(fill="x")
        ttk.Button(barra, text="Guardar sesión", command=self.guardar_sesion).pack(side="left", padx=4)
        ttk.Button(barra, text="Cargar sesión", command=self.cargar_sesion).pack(side="left", padx=4)

        btn_calc = tk.Button(
            barra, text="CALCULAR Tc Y CURVAS IDF", font=("Segoe UI", 10, "bold"),
            bg="#2e86c1", fg="white", activebackground="#21618c", activeforeground="white",
            relief="flat", cursor="hand2", command=self.procesar_calculo,
        )
        btn_calc.pack(side="right", padx=4, ipadx=14, ipady=6)

    # -------------------------- Pestaña 1 -----------------------------
    def _construir_tab_datos(self, p):
        btn_import = tk.Button(
            p, text="Cargar CSVs de Hydrognomon (Test K-S y Periodos)",
            font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white",
            activebackground="#1e8449", activeforeground="white",
            relief="flat", cursor="hand2", command=self.importar_datos,
        )
        btn_import.pack(fill="x", pady=(0, 14), ipady=6)

        ttk.Label(p, text="1. Datos del Proyecto", style="Header.TLabel").pack(anchor="w")
        f_proj = ttk.Frame(p)
        f_proj.pack(fill="x", pady=(6, 14))
        f_proj.columnconfigure(1, weight=1)

        campos = [
            ("Nombre del Proyecto:", self.proyecto_var, "Aparece en el encabezado de la memoria."),
            ("Cuenca / cauce principal:", self.cuenca_var, "Nombre o código de la cuenca delimitada (hoja de ruta 3.2)."),
            ("Sistema de coordenadas:", self.epsg_var, "Sistema en el que se delimitó la cuenca. Por defecto EPSG:32717 (UTM 17S)."),
            ("Origen de los datos:", self.fase_var, "Fase de la hoja de ruta de la que provienen los datos."),
        ]
        for i, (txt, var, ayuda) in enumerate(campos):
            ttk.Label(f_proj, text=txt).grid(row=i, column=0, sticky="w", padx=5, pady=4)
            ent = ttk.Entry(f_proj, textvariable=var)
            ent.grid(row=i, column=1, sticky="we", padx=5, pady=4)
            Tooltip(ent, ayuda)

        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=6)

        ttk.Label(p, text="2. Geometría de la Cuenca", style="Header.TLabel").pack(anchor="w", pady=(8, 0))
        f_geo = ttk.Frame(p)
        f_geo.pack(fill="x", pady=6)

        self.cont_L, self.ent_L = self._campo_validable(
            f_geo, "Longitud del cauce (L):", self.L_var, 0,
            "Longitud del cauce principal en METROS (m).\n"
            "Ej.: 5230.45\n"
            "Kirpich usa L en metros; para Témez el programa\n"
            "la convierte automáticamente a kilómetros.",
            "[m]",
        )
        self.cont_S, self.ent_S = self._campo_validable(
            f_geo, "Pendiente del cauce (S):", self.S_var, 1,
            "Pendiente media del cauce en m/m (adimensional).\n"
            "Ej.: 0.0085  →  0.85 %\n"
            "NO ingresar el valor en porcentaje.",
            "[m/m]",
        )

        self.lbl_error_geom = ttk.Label(p, text="", style="Error.TLabel")
        self.lbl_error_geom.pack(anchor="w", padx=5)

        ttk.Label(
            p,
            text="Nota: Kirpich fue calibrada para pendientes de 3 % a 10 % "
                 "(Tabla N.º 05 del Manual MTC). Fuera de ese rango conviene contrastar con Témez.",
            style="Ayuda.TLabel", wraplength=760, justify="left",
        ).pack(anchor="w", padx=5, pady=(10, 0))

    def _campo_validable(self, parent, etiqueta, var, fila, ayuda, unidad):
        """Etiqueta + Entry con borde que se pinta de rojo al validar."""
        ttk.Label(parent, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=5, pady=7)
        cont = tk.Frame(parent, background=self.color_borde_ok, padx=2, pady=2)
        cont.grid(row=fila, column=1, sticky="w", padx=5, pady=7)
        ent = ttk.Entry(cont, textvariable=var, width=18, justify="right")
        ent.pack()
        ttk.Label(parent, text=unidad, style="Ayuda.TLabel").grid(row=fila, column=2, sticky="w")
        Tooltip(ent, ayuda)
        return cont, ent

    # -------------------------- Pestaña 2 -----------------------------
    def _construir_tab_distribuciones(self, p):
        ttk.Label(p, text="Evaluación de Distribuciones (Test Kolmogorov-Smirnov)",
                  style="Header.TLabel").pack(anchor="w")
        ttk.Label(p, text="Importado desde el CSV de Hydrognomon. Haga clic en un encabezado para ordenar.",
                  style="Ayuda.TLabel").pack(anchor="w", pady=(0, 8))

        f_ks_container = ttk.Frame(p)
        f_ks_container.pack(fill="both", expand=True, pady=4)

        f_ks = ttk.Frame(f_ks_container)
        f_ks.pack(side="left", fill="both", expand=True)

        cols = ("dist", "a1", "a5", "a10", "attained", "dmax")
        self.tree_ks = ttk.Treeview(f_ks, columns=cols, show="headings", height=10)
        encabezados = [
            ("dist", "Distribución", 190, "w"),
            ("a1", "a=1%", 70, "center"),
            ("a5", "a=5%", 70, "center"),
            ("a10", "a=10%", 70, "center"),
            ("attained", "Attained a", 85, "center"),
            ("dmax", "DMax", 80, "center"),
        ]
        for col, txt, ancho, anchor in encabezados:
            self.tree_ks.heading(col, text=txt,
                                 command=lambda c=col: self.ordenar_arbol(self.tree_ks, c, False))
            self.tree_ks.column(col, width=ancho, anchor=anchor)

        self.tree_ks.grid(row=0, column=0, sticky="nsew")
        f_ks.rowconfigure(0, weight=1)
        f_ks.columnconfigure(0, weight=1)
        self.tree_ks.tag_configure("alta_aceptacion", background="#d4edda", foreground="#000000")

        scrollbar = ttk.Scrollbar(f_ks, orient=tk.VERTICAL, command=self.tree_ks.yview)
        self.tree_ks.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        f_recom = ttk.LabelFrame(f_ks_container, text="Recomendación", padding=8)
        f_recom.pack(side="left", fill="y", padx=(12, 0))
        self.lbl_recomendacion = ttk.Label(
            f_recom, text="Importe un CSV para\nver sugerencias.", justify="left",
            font=("Segoe UI", 9, "bold"), foreground="#2980b9",
        )
        self.lbl_recomendacion.pack(padx=5, pady=5)

        f_combo = ttk.Frame(p)
        f_combo.pack(fill="x", pady=12)
        ttk.Label(f_combo, text="Distribución elegida:").pack(side="left", padx=5)
        self.cb_dist = ttk.Combobox(f_combo, textvariable=self.distribucion_var,
                                    state="readonly", width=30)
        self.cb_dist.pack(side="left", padx=5)
        ttk.Label(f_combo, text="(* MTC recomienda: Normal, Gumbel, Log-Pearson III)",
                  style="Ayuda.TLabel").pack(side="left", padx=10)

        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=10)

        ttk.Label(p, text="Precipitaciones Máximas 24 h (P24) por Periodo de Retorno",
                  style="Header.TLabel").pack(anchor="w", pady=(0, 2))
        ttk.Label(p, text="Se rellenan solas al elegir una distribución; también pueden editarse a mano.",
                  style="Ayuda.TLabel").pack(anchor="w", pady=(0, 8))

        self.f_p24 = ttk.Frame(p)
        self.f_p24.pack(fill="x", pady=4)
        self.construir_interfaz_periodos()

        self.lbl_error_p24 = ttk.Label(p, text="", style="Error.TLabel")
        self.lbl_error_p24.pack(anchor="w", padx=5, pady=(6, 0))

    def construir_interfaz_periodos(self):
        for widget in self.f_p24.winfo_children():
            widget.destroy()
        self.cont_p24 = {}
        for i, t in enumerate(self.periodos):
            if t not in self.p24_vars:
                self.p24_vars[t] = tk.StringVar()
            fila, col = i // 3, (i % 3) * 2
            ttk.Label(self.f_p24, text=f"T = {t} años (mm):").grid(
                row=fila, column=col, sticky="w", padx=5, pady=6)
            cont = tk.Frame(self.f_p24, background=self.color_borde_ok, padx=2, pady=2)
            cont.grid(row=fila, column=col + 1, sticky="w", padx=10, pady=6)
            ttk.Entry(cont, textvariable=self.p24_vars[t], width=12, justify="right").pack()
            self.cont_p24[t] = cont

    # -------------------------- Pestaña 3 -----------------------------
    def _construir_tab_resultados(self, p):
        ttk.Label(p, text="Tiempo de Concentración - Comparación de métodos",
                  style="Header.TLabel").pack(anchor="w")

        f_tc = ttk.LabelFrame(p, text="Resultados", padding=12)
        f_tc.pack(fill="x", pady=(8, 12))
        f_tc.columnconfigure(1, weight=1)

        ttk.Label(f_tc, text="Kirpich  (L en m):").grid(row=0, column=0, sticky="w", pady=3)
        self.lbl_tc_kirpich = ttk.Label(f_tc, text="-", style="Res.TLabel")
        self.lbl_tc_kirpich.grid(row=0, column=1, sticky="w", padx=12, pady=3)

        ttk.Label(f_tc, text="Témez  (L en km):").grid(row=1, column=0, sticky="w", pady=3)
        self.lbl_tc_temez = ttk.Label(f_tc, text="-", style="Res.TLabel")
        self.lbl_tc_temez.grid(row=1, column=1, sticky="w", padx=12, pady=3)

        ttk.Label(f_tc, text="Diferencia relativa:").grid(row=2, column=0, sticky="w", pady=3)
        self.lbl_tc_dif = ttk.Label(f_tc, text="-", style="Res.TLabel")
        self.lbl_tc_dif.grid(row=2, column=1, sticky="w", padx=12, pady=3)

        self.lbl_aviso_pendiente = ttk.Label(f_tc, text="", wraplength=740, justify="left",
                                             font=("Segoe UI", 8), foreground="#b9770e")
        self.lbl_aviso_pendiente.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))

        f_sel = ttk.LabelFrame(p, text="Tc adoptado para el diseño (sección 4 de la memoria)", padding=12)
        f_sel.pack(fill="x", pady=(0, 12))
        ttk.Radiobutton(f_sel, text="Kirpich", value="Kirpich",
                        variable=self.metodo_tc_var).pack(side="left", padx=8)
        ttk.Radiobutton(f_sel, text="Témez", value="Témez",
                        variable=self.metodo_tc_var).pack(side="left", padx=8)
        self.lbl_tc_diseno = ttk.Label(f_sel, text="Tc de diseño: -", style="Res.TLabel")
        self.lbl_tc_diseno.pack(side="left", padx=24)

        ttk.Label(p, text="Intensidades de diseño (t = Tc)", style="Header.TLabel").pack(anchor="w")
        f_tabla = ttk.Frame(p)
        f_tabla.pack(fill="x", pady=(6, 12))
        cols = ("t", "p24", "i")
        self.tree_diseno = ttk.Treeview(f_tabla, columns=cols, show="headings", height=6)
        self.tree_diseno.heading("t", text="T (años)")
        self.tree_diseno.heading("p24", text="P24 (mm)")
        self.tree_diseno.heading("i", text="Intensidad de diseño (mm/h)")
        self.tree_diseno.column("t", width=100, anchor="center")
        self.tree_diseno.column("p24", width=120, anchor="center")
        self.tree_diseno.column("i", width=220, anchor="center")
        self.tree_diseno.pack(fill="x")

        ttk.Separator(p, orient="horizontal").pack(fill="x", pady=10)

        f_opts = ttk.Frame(p)
        f_opts.pack(fill="x", pady=(0, 10))
        ttk.Label(f_opts, text="Resolución del gráfico (dpi):").pack(side="left", padx=(0, 6))
        cb_dpi = ttk.Combobox(f_opts, textvariable=self.dpi_var, state="readonly",
                              width=6, values=("100", "150", "200", "300"))
        cb_dpi.pack(side="left")
        Tooltip(cb_dpi, "El gráfico se incrusta en el HTML como PNG en base64.\n"
                        "150 dpi da buena calidad con un archivo liviano;\n"
                        "300 dpi puede superar los 2-3 MB.")
        ttk.Checkbutton(f_opts, text="Guardar también el gráfico como PNG aparte",
                        variable=self.png_aparte_var).pack(side="left", padx=16)

        ttk.Label(p, text="Exportación", style="Header.TLabel").pack(anchor="w", pady=(4, 6))
        f_exp = ttk.Frame(p)
        f_exp.pack(fill="x")

        self.btn_html = tk.Button(f_exp, text="Exportar memoria (HTML)", font=("Segoe UI", 9, "bold"),
                                  bg="#2e86c1", fg="white", relief="flat", cursor="hand2",
                                  state="disabled", command=self.exportar_html)
        self.btn_html.pack(side="left", padx=(0, 8), ipadx=8, ipady=4)

        self.btn_pdf = tk.Button(f_exp, text="Exportar memoria (PDF)", font=("Segoe UI", 9, "bold"),
                                 bg="#8e44ad", fg="white", relief="flat", cursor="hand2",
                                 state="disabled", command=self.exportar_pdf)
        self.btn_pdf.pack(side="left", padx=8, ipadx=8, ipady=4)
        Tooltip(self.btn_pdf,
                "Usa weasyprint si está instalado.\n"
                "Si no lo está, abre la memoria en el navegador\n"
                "para imprimirla como PDF (Ctrl+P).")

        self.btn_csv = tk.Button(f_exp, text="Exportar tabla IDF (CSV)", font=("Segoe UI", 9, "bold"),
                                 bg="#16a085", fg="white", relief="flat", cursor="hand2",
                                 state="disabled", command=self.exportar_csv_idf)
        self.btn_csv.pack(side="left", padx=8, ipadx=8, ipady=4)

        self.lbl_estado = ttk.Label(p, text="Aún no se ha calculado. Complete L, S y las P24, "
                                            "y pulse «CALCULAR Tc Y CURVAS IDF».",
                                    style="Ayuda.TLabel", wraplength=760, justify="left")
        self.lbl_estado.pack(anchor="w", pady=(12, 0))

    # ------------------------------------------------------------------
    # Utilidades varias
    # ------------------------------------------------------------------
    def parse_float(self, val_str):
        try:
            limpio = (val_str or "").replace("%", "").strip()
            return float(limpio) if limpio else -1.0
        except ValueError:
            return -1.0

    def ordenar_arbol(self, tv, col, reverso):
        filas = [(tv.set(k, col), k) for k in tv.get_children("")]
        if col in ("attained", "dmax"):
            filas.sort(key=lambda t: self.parse_float(t[0]), reverse=reverso)
        else:
            filas.sort(reverse=reverso)
        for index, (_val, k) in enumerate(filas):
            tv.move(k, "", index)
        tv.heading(col, command=lambda: self.ordenar_arbol(tv, col, not reverso))

    def _marcar(self, contenedor, hay_error):
        if contenedor is not None and contenedor.winfo_exists():
            contenedor.configure(background=COLOR_ERROR if hay_error else self.color_borde_ok)

    def _limpiar_marcas(self):
        self._marcar(self.cont_L, False)
        self._marcar(self.cont_S, False)
        for cont in self.cont_p24.values():
            self._marcar(cont, False)
        self.lbl_error_geom.config(text="")
        self.lbl_error_p24.config(text="")

    def _al_editar_geometria(self, *_args):
        if not hasattr(self, "cont_L"):
            return
        # Al corregir el dato se apaga el resaltado en rojo
        if self.L_var.get().strip():
            self._marcar(self.cont_L, False)
        if self.S_var.get().strip():
            self._marcar(self.cont_S, False)
        if self.L_var.get().strip() and self.S_var.get().strip():
            self.lbl_error_geom.config(text="")
        if self.resultados is not None:
            self.lbl_estado.config(
                text="⚠ Cambió la geometría: los resultados y la memoria siguen "
                     "correspondiendo al último cálculo. Vuelva a calcular para actualizarlos.")

    # ------------------------------------------------------------------
    # Importación de CSVs de Hydrognomon
    # ------------------------------------------------------------------
    def _leer_csv(self, ruta):
        """Lee un CSV probando varias codificaciones y detectando el separador.

        Devuelve (filas, encoding_usado). Lanza ValueError si no se puede leer.
        """
        texto = None
        enc_usado = None
        ultimo_error = None
        for enc in ENCODINGS_CSV:
            try:
                with open(ruta, "r", encoding=enc, newline="") as f:
                    texto = f.read()
                enc_usado = enc
                break
            except UnicodeDecodeError as e:
                ultimo_error = e
                continue
        if texto is None:
            raise ValueError(
                f"No se pudo decodificar el archivo con ninguna codificación conocida "
                f"({', '.join(ENCODINGS_CSV)}). Detalle: {ultimo_error}"
            )

        filas = [f for f in csv.reader(io.StringIO(texto)) if f]
        # Si con coma no se separó nada pero hay ';' (exports en español), reintentar
        if filas and max(len(f) for f in filas[:10]) < 2 and ";" in texto:
            filas = [f for f in csv.reader(io.StringIO(texto), delimiter=";") if f]
        if not filas:
            raise ValueError("El archivo está vacío o no contiene filas legibles.")
        return filas, enc_usado

    def importar_datos(self):
        rutas = filedialog.askopenfilenames(
            title="Seleccionar archivos CSV de Hydrognomon",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        )
        if not rutas:
            return

        ks_cargado = False
        t_cargados = []
        fallidos = []       # (archivo, motivo)
        no_reconocidos = []

        for ruta in rutas:
            nombre = os.path.basename(ruta)
            try:
                lineas, enc = self._leer_csv(ruta)
                encabezado = lineas[0][0] if lineas[0] else ""

                # 1) Archivo del test Kolmogorov-Smirnov
                if "Kolmogorov-Smirnov" in encabezado:
                    self._cargar_ks(lineas)
                    ks_cargado = True

                # 2) Archivo de un periodo de retorno
                elif "T(Max)=" in encabezado:
                    t_val = self._cargar_periodo(lineas, encabezado)
                    if t_val is None:
                        fallidos.append((nombre, "No se pudo leer el periodo de retorno del encabezado."))
                    else:
                        t_cargados.append(t_val)
                else:
                    no_reconocidos.append(nombre)

            except Exception as e:
                fallidos.append((nombre, f"{type(e).__name__}: {e}"))

        if t_cargados:
            periodos_encontrados = set()
            for dist_dic in self.datos_precipitacion_dist.values():
                periodos_encontrados.update(dist_dic.keys())
            if periodos_encontrados:
                self.periodos = sorted(periodos_encontrados)
                self.construir_interfaz_periodos()

        self.actualizar_campos_p24()

        # ---- Resumen detallado -----------------------------------------
        partes = [
            f"Archivos seleccionados: {len(rutas)}",
            f"  • Test K-S cargado: {'Sí' if ks_cargado else 'No'}",
            f"  • Periodos (T) cargados: {len(t_cargados)}"
            + (f"  →  T = {', '.join(str(t) for t in sorted(t_cargados))} años" if t_cargados else ""),
        ]
        if no_reconocidos:
            partes.append("\nFormato no reconocido (sin 'Kolmogorov-Smirnov' ni 'T(Max)=' "
                          "en la primera línea):")
            partes += [f"  • {n}" for n in no_reconocidos]
        if fallidos:
            partes.append("\nArchivos con error:")
            partes += [f"  • {n}: {motivo}" for n, motivo in fallidos]

        resumen = "\n".join(partes)
        if fallidos or no_reconocidos:
            messagebox.showwarning("Importación con incidencias", resumen)
        else:
            messagebox.showinfo("Importación exitosa", resumen)

    def _cargar_ks(self, lineas):
        for item in self.tree_ks.get_children():
            self.tree_ks.delete(item)

        nombres_dist = []
        max_general, mejor_dist_general = -1.0, None
        max_mtc, mejor_dist_mtc = -1.0, None

        for partes in lineas[1:]:
            if len(partes) < 6:
                continue
            dist_nombre = partes[0].strip()
            a1, a5, a10 = partes[1].strip(), partes[2].strip(), partes[3].strip()
            attained, dmax = partes[4].strip(), partes[5].strip()

            val_float = self.parse_float(attained)
            nombres_dist.append(dist_nombre)

            tags = ("alta_aceptacion",) if val_float > 90.0 else ()
            self.tree_ks.insert("", "end", values=(dist_nombre, a1, a5, a10, attained, dmax), tags=tags)

            if val_float > max_general:
                max_general, mejor_dist_general = val_float, dist_nombre
            if any(kw in dist_nombre.lower() for kw in MTC_KEYWORDS) and val_float > max_mtc:
                max_mtc, mejor_dist_mtc = val_float, dist_nombre

        if not nombres_dist:
            return
        self.cb_dist["values"] = nombres_dist
        if not mejor_dist_general:
            return

        if any(kw in mejor_dist_general.lower() for kw in MTC_KEYWORDS):
            texto_recom = f"★ Recomendado (MTC):\n{mejor_dist_general}\n({max_general:.2f}%)"
            self.distribucion_var.set(mejor_dist_general)
        else:
            texto_recom = f"★ Máximo General:\n{mejor_dist_general}\n({max_general:.2f}%)\n\n"
            if mejor_dist_mtc and max_mtc >= 0:
                texto_recom += f"★ Máximo del MTC:\n{mejor_dist_mtc}\n({max_mtc:.2f}%)"
                self.distribucion_var.set(mejor_dist_mtc)
            else:
                texto_recom += "★ MTC: No hay datos válidos."
                self.distribucion_var.set(mejor_dist_general)
        self.lbl_recomendacion.config(text=texto_recom)

    def _cargar_periodo(self, lineas, encabezado):
        match = re.search(r"T\(Max\)=\s*([0-9.]+)", encabezado)
        if not match:
            return None
        t_val = int(float(match.group(1)))
        for partes in lineas[1:]:
            if len(partes) < 2:
                continue
            dist_nombre = partes[0].strip()
            try:
                valor = float(partes[1].strip())
            except ValueError:
                continue
            self.datos_precipitacion_dist.setdefault(dist_nombre, {})[t_val] = valor
        return t_val

    def actualizar_campos_p24(self, *_args):
        dist_actual = self.distribucion_var.get()
        for var in self.p24_vars.values():
            var.set("")
        if dist_actual in self.datos_precipitacion_dist:
            for t, val in self.datos_precipitacion_dist[dist_actual].items():
                if t in self.p24_vars:
                    self.p24_vars[t].set(f"{val:.2f}")

    # ------------------------------------------------------------------
    # Sesión (JSON) - compatible hacia atrás
    # ------------------------------------------------------------------
    def guardar_sesion(self):
        data = {
            "formato_version": FORMATO_SESION,
            "app_version": APP_VERSION,
            "proyecto": self.proyecto_var.get(),
            "cuenca": self.cuenca_var.get(),
            "epsg": self.epsg_var.get(),
            "fase": self.fase_var.get(),
            "L": self.L_var.get(),
            "S": self.S_var.get(),
            "distribucion": self.distribucion_var.get(),
            "metodo_tc": self.metodo_tc_var.get(),
            "dpi_grafico": self.dpi_var.get(),
            "periodos": self.periodos,
            "p24": {str(t): v.get() for t, v in self.p24_vars.items()},
            "datos_precipitacion_dist": {
                dist: {str(t): v for t, v in periodos.items()}
                for dist, periodos in self.datos_precipitacion_dist.items()
            },
        }
        ruta = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json")],
            initialfile=f"Sesion_{nombre_archivo_seguro(self.proyecto_var.get(), 'proyecto')}.json",
        )
        if not ruta:
            return
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Éxito", "Sesión guardada correctamente.")
        except OSError as e:
            messagebox.showerror("Error al guardar", f"No se pudo escribir el archivo:\n{e}")

    def cargar_sesion(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if not ruta:
            return
        try:
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except UnicodeDecodeError:
                with open(ruta, "r", encoding="cp1252") as f:
                    data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            messagebox.showerror("Error al cargar", f"No se pudo leer la sesión:\n{e}")
            return

        version = data.get("formato_version", 1)

        # Campos presentes desde la v1
        self.proyecto_var.set(data.get("proyecto", ""))
        self.L_var.set(data.get("L", ""))
        self.S_var.set(data.get("S", ""))

        if "periodos" in data:
            try:
                self.periodos = sorted(int(t) for t in data["periodos"])
            except (TypeError, ValueError):
                pass
            self.construir_interfaz_periodos()

        # Campos nuevos (v2): valores por defecto si la sesión es antigua
        self.cuenca_var.set(data.get("cuenca", "Cuenca s/n - cauce principal"))
        self.epsg_var.set(data.get("epsg", EPSG_DEFECTO))
        self.fase_var.set(data.get("fase", FASE_DEFECTO))
        self.metodo_tc_var.set(data.get("metodo_tc", "Kirpich"))
        self.dpi_var.set(str(data.get("dpi_grafico", "150")))

        self.datos_precipitacion_dist = {
            dist: {int(t): float(v) for t, v in periodos.items()}
            for dist, periodos in data.get("datos_precipitacion_dist", {}).items()
        }
        if self.datos_precipitacion_dist:
            self.cb_dist["values"] = list(self.datos_precipitacion_dist.keys())

        self.distribucion_var.set(data.get("distribucion", ""))

        # Los P24 se escriben después de la distribución para no ser sobrescritos
        for t_str, v in data.get("p24", {}).items():
            try:
                t_int = int(t_str)
            except (TypeError, ValueError):
                continue
            if t_int not in self.p24_vars:
                self.p24_vars[t_int] = tk.StringVar()
            self.p24_vars[t_int].set(v)

        self._limpiar_marcas()
        self._invalidar_resultados()
        if version < FORMATO_SESION:
            messagebox.showinfo(
                "Sesión antigua",
                f"La sesión se guardó con el formato v{version} y se migró al formato "
                f"v{FORMATO_SESION}.\nLos campos nuevos (cuenca, EPSG, método de Tc) "
                f"se cargaron con valores por defecto: revíselos antes de exportar.",
            )

    # ------------------------------------------------------------------
    # Cálculo
    # ------------------------------------------------------------------
    def _validar_entradas(self):
        """Valida L, S y las P24 marcando los campos en rojo.

        Devuelve (L, S, datos_t_p24) o None si hay errores.
        """
        self._limpiar_marcas()
        errores_geom = []

        L = S = None
        texto_L = self.L_var.get().strip().replace(",", ".")
        texto_S = self.S_var.get().strip().replace(",", ".")

        try:
            L = float(texto_L)
            if L <= 0:
                raise ValueError
        except ValueError:
            self._marcar(self.cont_L, True)
            errores_geom.append("La longitud L debe ser un número mayor a 0 (en metros).")

        try:
            S = float(texto_S)
            if S <= 0:
                raise ValueError
        except ValueError:
            self._marcar(self.cont_S, True)
            errores_geom.append("La pendiente S debe ser un número mayor a 0 (en m/m).")

        if errores_geom:
            self.lbl_error_geom.config(text="  ".join(errores_geom))
            self.nb.select(self.tab_datos)
            return None

        datos_t_p24 = {}
        errores_p24 = []
        for t in sorted(self.periodos):
            var = self.p24_vars.get(t)
            if var is None:
                continue
            val = var.get().strip().replace(",", ".")
            if not val:
                continue
            try:
                p24 = float(val)
                if p24 <= 0:
                    raise ValueError
                datos_t_p24[t] = p24
            except ValueError:
                self._marcar(self.cont_p24.get(t), True)
                errores_p24.append(str(t))

        if errores_p24:
            self.lbl_error_p24.config(
                text=f"Valores de P24 inválidos para T = {', '.join(errores_p24)} años "
                     f"(deben ser números mayores a 0)."
            )
            self.nb.select(self.tab_dist)
            return None

        if not datos_t_p24:
            self.lbl_error_p24.config(text="Debe ingresar al menos una precipitación P24.")
            self.nb.select(self.tab_dist)
            return None

        return L, S, datos_t_p24

    def procesar_calculo(self):
        validado = self._validar_entradas()
        if validado is None:
            return
        L, S, datos_t_p24 = validado

        try:
            tc_k = tc_kirpich(L, S)
            tc_t = tc_temez(L, S)

            duraciones_min = np.array(DURACIONES_MIN, dtype=float)
            duraciones_hr = duraciones_min / 60.0

            # Matriz de intensidades: una fila por duración, una columna por T
            periodos_orden = sorted(datos_t_p24.keys())
            matriz_idf = []
            for i, dur_min in enumerate(duraciones_min):
                fila = [int(dur_min)]
                for t in periodos_orden:
                    fila.append(intensidad_dick_peschke(datos_t_p24[t], duraciones_hr[i]))
                matriz_idf.append(fila)

            img_base64, png_bytes = self._construir_grafico(
                duraciones_min, duraciones_hr, datos_t_p24, periodos_orden)

            self.resultados = {
                "L": L, "S": S,
                "tc": {"Kirpich": tc_k, "Témez": tc_t},
                "datos_t_p24": datos_t_p24,
                "periodos_orden": periodos_orden,
                "matriz_idf": matriz_idf,
                "img_base64": img_base64,
                "png_bytes": png_bytes,
                "fecha": datetime.now(),
            }

            self._mostrar_resultados()
            self.nb.select(self.tab_res)

        except Exception as e:
            messagebox.showerror("Error inesperado", f"{type(e).__name__}: {e}")

    def _construir_grafico(self, duraciones_min, duraciones_hr, datos_t_p24, periodos_orden):
        try:
            dpi = int(self.dpi_var.get())
        except ValueError:
            dpi = 150

        fig, ax = plt.subplots(figsize=(9, 5))
        for t in periodos_orden:
            intensidades = intensidad_dick_peschke(datos_t_p24[t], duraciones_hr)
            ax.plot(duraciones_min, intensidades, marker="o", label=f"T = {t} años")

        ax.set_title("Curvas Intensidad-Duración-Frecuencia (IDF)", fontsize=14)
        ax.set_xlabel("Duración de la tormenta, t (minutos)", fontsize=11)
        ax.set_ylabel("Intensidad, I (mm/h)", fontsize=11)
        ax.grid(True, which="both", ls="--", alpha=0.7)
        ax.legend()
        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi)
        plt.close(fig)
        png_bytes = buf.getvalue()
        return base64.b64encode(png_bytes).decode("utf-8"), png_bytes

    def _tc_diseno(self):
        """(nombre_metodo, tc_horas) según el selector de la interfaz."""
        metodo = self.metodo_tc_var.get() or "Kirpich"
        if self.resultados is None:
            return metodo, None
        return metodo, self.resultados["tc"].get(metodo, self.resultados["tc"]["Kirpich"])

    def _intensidades_diseno(self):
        _metodo, tc_h = self._tc_diseno()
        return {
            t: intensidad_dick_peschke(p24, tc_h)
            for t, p24 in self.resultados["datos_t_p24"].items()
        }

    def _al_cambiar_metodo(self, *_args):
        if self.resultados is not None:
            self._mostrar_resultados()

    def _invalidar_resultados(self):
        self.resultados = None
        for lbl in (self.lbl_tc_kirpich, self.lbl_tc_temez, self.lbl_tc_dif):
            lbl.config(text="-")
        self.lbl_tc_diseno.config(text="Tc de diseño: -")
        self.lbl_aviso_pendiente.config(text="")
        for item in self.tree_diseno.get_children():
            self.tree_diseno.delete(item)
        for btn in (self.btn_html, self.btn_pdf, self.btn_csv):
            btn.config(state="disabled")
        self.lbl_estado.config(text="Aún no se ha calculado. Complete L, S y las P24, "
                                    "y pulse «CALCULAR Tc Y CURVAS IDF».")

    def _mostrar_resultados(self):
        r = self.resultados
        tc_k, tc_t = r["tc"]["Kirpich"], r["tc"]["Témez"]
        dif_pct = (tc_t - tc_k) / tc_k * 100.0

        self.lbl_tc_kirpich.config(
            text=f"{tc_k:.{DEC_TC_H}f} h   ({tc_k * 60:.{DEC_TC_M}f} min)")
        self.lbl_tc_temez.config(
            text=f"{tc_t:.{DEC_TC_H}f} h   ({tc_t * 60:.{DEC_TC_M}f} min)")
        signo = "+" if dif_pct >= 0 else ""
        self.lbl_tc_dif.config(
            text=f"{signo}{dif_pct:.{DEC_I}f} %   (Témez respecto a Kirpich)")

        S = r["S"]
        if KIRPICH_S_MIN <= S <= KIRPICH_S_MAX:
            self.lbl_aviso_pendiente.config(
                text=f"✓ La pendiente S = {S:.{DEC_S}f} m/m ({S * 100:.2f} %) está dentro del rango "
                     f"3 %-10 % para el que Kirpich fue calibrada (Tabla N.º 05 del Manual MTC).",
                foreground=COLOR_OK,
            )
        else:
            self.lbl_aviso_pendiente.config(
                text=f"⚠ La pendiente S = {S:.{DEC_S}f} m/m ({S * 100:.2f} %) queda FUERA del rango "
                     f"3 %-10 % para el que Kirpich fue calibrada (Tabla N.º 05 del Manual MTC). "
                     f"Se reporta Témez como contraste; la elección del Tc de diseño es criterio del proyectista.",
                foreground="#b9770e",
            )

        metodo, tc_d = self._tc_diseno()
        self.lbl_tc_diseno.config(
            text=f"Tc de diseño: {tc_d:.{DEC_TC_H}f} h ({tc_d * 60:.{DEC_TC_M}f} min)")

        for item in self.tree_diseno.get_children():
            self.tree_diseno.delete(item)
        int_diseno = self._intensidades_diseno()
        for t in r["periodos_orden"]:
            self.tree_diseno.insert("", "end", values=(
                t, f"{r['datos_t_p24'][t]:.2f}", f"{int_diseno[t]:.{DEC_I}f}"))

        for btn in (self.btn_html, self.btn_pdf, self.btn_csv):
            btn.config(state="normal")
        kb = len(r["png_bytes"]) * 4 / 3 / 1024
        self.lbl_estado.config(
            text=f"Cálculo actualizado ({r['fecha'].strftime('%d/%m/%Y %H:%M')}). "
                 f"Gráfico incrustado ≈ {kb:,.0f} KB en el HTML. "
                 f"Ya puede exportar la memoria.")

    # ------------------------------------------------------------------
    # Generación de la memoria
    # ------------------------------------------------------------------
    def _cargar_plantilla(self):
        base = os.path.dirname(os.path.abspath(__file__))
        ruta = os.path.join(base, NOMBRE_PLANTILLA)
        if not os.path.isfile(ruta):
            raise FileNotFoundError(
                f"No se encontró la plantilla «{NOMBRE_PLANTILLA}».\n\n"
                f"Debe estar en la misma carpeta que Tc.py:\n{base}"
            )
        with open(ruta, "r", encoding="utf-8") as f:
            return PlantillaHTML(f.read())

    def _texto_sustento(self, S, dif_pct, metodo):
        """Párrafo de sustento del método de Tc (HTML ya construido)."""
        s_pct = S * 100
        dentro = KIRPICH_S_MIN <= S <= KIRPICH_S_MAX
        if dentro:
            cuerpo = (
                f"La pendiente media del cauce, S = {S:.{DEC_S}f} m/m ({s_pct:.2f}&nbsp;%), se "
                f"encuentra <b>dentro</b> del rango de 3&nbsp;% a 10&nbsp;% para el cual la "
                f"fórmula de Kirpich fue calibrada, según la Tabla N.º 05 del Manual de "
                f"Hidrología, Hidráulica y Drenaje del MTC, por lo que su aplicación es directa. "
                f"Aun así se reporta el resultado del método de Témez como contraste, dado que "
                f"ambos métodos difieren en {abs(dif_pct):.2f}&nbsp;%."
            )
        else:
            relacion = "inferior" if S < KIRPICH_S_MIN else "superior"
            cuerpo = (
                f"La pendiente media del cauce, S = {S:.{DEC_S}f} m/m ({s_pct:.2f}&nbsp;%), es "
                f"<b>{relacion}</b> al rango de 3&nbsp;% a 10&nbsp;% para el cual la fórmula de "
                f"Kirpich fue calibrada, según la Tabla N.º 05 del Manual de Hidrología, "
                f"Hidráulica y Drenaje del MTC. Al tratarse de un terreno semiárido y de "
                f"topografía llana, la aplicación de Kirpich fuera de su rango de calibración "
                f"tiende a subestimar el tiempo de concentración y, por consiguiente, a "
                f"sobrestimar la intensidad de diseño. Por ello se calcula también el método de "
                f"Témez, cuyo resultado difiere en {abs(dif_pct):.2f}&nbsp;% respecto de Kirpich."
            )
        cierre = (
            f" La elección del valor de diseño queda a criterio del proyectista; en la presente "
            f"memoria se adoptó el método <b>{html.escape(metodo)}</b>, cuyo valor se emplea en "
            f"la sección 4."
        )
        return f'<div class="nota"><p>{cuerpo}{cierre}</p></div>'

    def _tabla_idf_html(self):
        r = self.resultados
        filas = ["<tr><th>Duración (min)</th>"]
        for t in r["periodos_orden"]:
            filas.append(f"<th>I (T={t}) mm/h</th>")
        filas.append("</tr>")
        for fila in r["matriz_idf"]:
            filas.append(f"<tr><td>{fila[0]}</td>")
            for valor in fila[1:]:
                filas.append(f"<td>{valor:.{DEC_I}f}</td>")
            filas.append("</tr>")
        return "".join(filas)

    def generar_html_texto(self, incrustar_grafico=True):
        """Devuelve el HTML completo de la memoria."""
        r = self.resultados
        plantilla = self._cargar_plantilla()

        L, S = r["L"], r["S"]
        tc_k, tc_t = r["tc"]["Kirpich"], r["tc"]["Témez"]
        dif_pct = (tc_t - tc_k) / tc_k * 100.0
        metodo, tc_d = self._tc_diseno()
        int_diseno = self._intensidades_diseno()

        filas_diseno = "".join(
            f"<tr><td>{t}</td><td>{r['datos_t_p24'][t]:.2f}</td>"
            f"<td><b>{int_diseno[t]:.{DEC_I}f}</b></td></tr>"
            for t in r["periodos_orden"]
        )

        nota_grafico = ""
        if self.png_aparte_var.get():
            nota_grafico = ('<p style="font-size:0.85em;color:#7b7b7b;text-align:center;">'
                            "El gráfico también se guardó como archivo PNG independiente "
                            "junto a esta memoria.</p>")

        valores = {
            # Texto proveniente del usuario: siempre escapado
            "proyecto": html.escape(self.proyecto_var.get()),
            "cuenca": html.escape(self.cuenca_var.get()) or "-",
            "epsg": html.escape(self.epsg_var.get()) or "-",
            "fase": html.escape(self.fase_var.get()) or "-",
            "distribucion": html.escape(self.distribucion_var.get()) or "(no especificada)",
            "fecha": r["fecha"].strftime("%d/%m/%Y"),
            # Geometría (decimales unificados con la interfaz)
            "L_m": f"{L:.{DEC_L}f}",
            "L_km": f"{L / 1000.0:.3f}",
            "S": f"{S:.{DEC_S}f}",
            "S_pct": f"{S * 100:.2f}",
            # Tiempos de concentración
            "tc_kirpich_h": f"{tc_k:.{DEC_TC_H}f}",
            "tc_kirpich_min": f"{tc_k * 60:.{DEC_TC_M}f}",
            "tc_temez_h": f"{tc_t:.{DEC_TC_H}f}",
            "tc_temez_min": f"{tc_t * 60:.{DEC_TC_M}f}",
            "dif_pct": f"{dif_pct:+.2f}",
            "metodo_diseno": html.escape(metodo),
            "tc_diseno_h": f"{tc_d:.{DEC_TC_H}f}",
            "tc_diseno_min": f"{tc_d * 60:.{DEC_TC_M}f}",
            "sustento_tc": self._texto_sustento(S, dif_pct, metodo),
            # Tablas y gráfico
            "tabla_idf": self._tabla_idf_html(),
            "filas_diseno": filas_diseno,
            "img_idf": r["img_base64"] if incrustar_grafico else "",
            "nota_grafico": nota_grafico,
            "app_version": APP_VERSION,
            "generado": r["fecha"].strftime("%d/%m/%Y %H:%M"),
        }
        return plantilla.safe_substitute(valores)

    def _ruta_sugerida(self, extension):
        base = nombre_archivo_seguro(self.proyecto_var.get(), "Proyecto")
        return f"Memoria_{base}.{extension}"

    def exportar_html(self):
        if self.resultados is None:
            messagebox.showwarning("Sin datos", "Primero ejecute el cálculo.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar memoria de cálculo",
            defaultextension=".html",
            filetypes=[("Archivo HTML", "*.html")],
            initialfile=self._ruta_sugerida("html"),
        )
        if not ruta:
            return
        try:
            contenido = self.generar_html_texto()
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(contenido)

            extra = ""
            if self.png_aparte_var.get():
                ruta_png = os.path.splitext(ruta)[0] + "_IDF.png"
                with open(ruta_png, "wb") as f:
                    f.write(self.resultados["png_bytes"])
                extra = f"\nGráfico PNG: {os.path.basename(ruta_png)}"

            mb = os.path.getsize(ruta) / (1024 * 1024)
            aviso = ""
            if mb > 4:
                aviso = ("\n\nEl archivo es grande porque el gráfico va incrustado en base64. "
                         "Puede reducir los dpi del gráfico y volver a calcular.")
            messagebox.showinfo(
                "Memoria exportada",
                f"Memoria exportada correctamente.\n\nArchivo: {os.path.basename(ruta)}\n"
                f"Tamaño: {mb:.2f} MB{extra}{aviso}",
            )
        except Exception as e:
            messagebox.showerror("Error al exportar", f"{type(e).__name__}: {e}")

    def exportar_pdf(self):
        if self.resultados is None:
            messagebox.showwarning("Sin datos", "Primero ejecute el cálculo.")
            return
        try:
            contenido = self.generar_html_texto()
        except Exception as e:
            messagebox.showerror("Error al generar la memoria", f"{type(e).__name__}: {e}")
            return

        if WeasyHTML is not None:
            ruta = filedialog.asksaveasfilename(
                title="Guardar memoria en PDF",
                defaultextension=".pdf",
                filetypes=[("Archivo PDF", "*.pdf")],
                initialfile=self._ruta_sugerida("pdf"),
            )
            if not ruta:
                return
            try:
                WeasyHTML(string=contenido, base_url=os.path.dirname(os.path.abspath(__file__))).write_pdf(ruta)
                messagebox.showinfo("PDF exportado",
                                    f"Memoria exportada a PDF.\n\nArchivo: {os.path.basename(ruta)}")
            except Exception as e:
                messagebox.showerror("Error al exportar PDF", f"{type(e).__name__}: {e}")
            return

        # Sin weasyprint: se abre en el navegador para «Imprimir → Guardar como PDF»
        seguir = messagebox.askokcancel(
            "Exportar a PDF",
            "La librería «weasyprint» no está instalada.\n\n"
            "Se abrirá la memoria en el navegador para que la guarde como PDF\n"
            "con Ctrl+P → «Guardar como PDF» (la hoja ya está configurada en A4).\n\n"
            "Para exportar directamente, instale:  pip install weasyprint",
        )
        if not seguir:
            return
        try:
            tmp = os.path.join(tempfile.gettempdir(), self._ruta_sugerida("html"))
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(contenido)
            webbrowser.open(f"file:///{tmp.replace(os.sep, '/')}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el navegador:\n{e}")

    def exportar_csv_idf(self):
        if self.resultados is None:
            messagebox.showwarning("Sin datos", "Primero ejecute el cálculo.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar tabla de intensidades IDF",
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")],
            initialfile=f"IDF_{nombre_archivo_seguro(self.proyecto_var.get(), 'Proyecto')}.csv",
        )
        if not ruta:
            return
        r = self.resultados
        metodo, tc_d = self._tc_diseno()
        int_diseno = self._intensidades_diseno()
        try:
            # utf-8-sig para que Excel en Windows respete las tildes
            with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.writer(f)
                w.writerow(["Proyecto", self.proyecto_var.get()])
                w.writerow(["Cuenca", self.cuenca_var.get()])
                w.writerow(["Distribución", self.distribucion_var.get()])
                w.writerow(["L (m)", f"{r['L']:.{DEC_L}f}", "S (m/m)", f"{r['S']:.{DEC_S}f}"])
                w.writerow(["Tc Kirpich (h)", f"{r['tc']['Kirpich']:.{DEC_TC_H}f}",
                            "Tc Témez (h)", f"{r['tc']['Témez']:.{DEC_TC_H}f}"])
                w.writerow([f"Tc de diseño ({metodo}) (h)", f"{tc_d:.{DEC_TC_H}f}"])
                w.writerow([])
                w.writerow(["Duración (min)"] + [f"I (T={t}) mm/h" for t in r["periodos_orden"]])
                for fila in r["matriz_idf"]:
                    w.writerow([fila[0]] + [f"{v:.{DEC_I}f}" for v in fila[1:]])
                w.writerow([])
                w.writerow(["Intensidades de diseño (t = Tc)"])
                w.writerow(["T (años)", "P24 (mm)", "I diseño (mm/h)"])
                for t in r["periodos_orden"]:
                    w.writerow([t, f"{r['datos_t_p24'][t]:.2f}", f"{int_diseno[t]:.{DEC_I}f}"])
            messagebox.showinfo("CSV exportado",
                                f"Tabla IDF exportada.\n\nArchivo: {os.path.basename(ruta)}")
        except Exception as e:
            messagebox.showerror("Error al exportar", f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    root = tb.Window(themename="litera") if tb is not None else tk.Tk()
    app = HidroMTCApp(root)
    root.mainloop()
