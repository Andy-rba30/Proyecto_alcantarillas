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
                            columna (banderas de `cli.py`, ANOTADOS con las
                            familias que los usan) + ALCANCE de la corrida +
                            boton de ejecucion. Los dos campos de archivo
                            llevan su icono «i», que abre la AYUDA DERIVADA
                            (ver mas abajo).
    2. Criterios           Los criterios adoptados y su estado, con FILTRO
                            (por estado, por AMBITO y por texto) y RECUENTO de
                            pendientes; la ventana normativa de cada variable
                            (Sec. 4.2/4.3 del plan); y el unico sitio de la
                            interfaz que REESCRIBE `criterios_adoptados.py`
                            --- accion permanente, aparte y con confirmacion
                            propia, que es justo la pestana que esta lista
                            omitia.
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

Lo que se pone entre el proyectista y los 69 criterios
------------------------------------------------------
La pestana 2 lista los 69 criterios del archivo, 33 de ellos PENDIENTES. Tres
cosas la hacian dificil de usar, y las tres tienen la misma forma: informacion
que el programa TIENE y que no llegaba a la pantalla.

- **La fuente no cabia y no habia donde leerla.** Es el campo que dice de donde
  sale un valor --- la pregunta que la taxonomia de CLAUDE.md pone en el centro
  ---, tiene 280 caracteres de mediana y 4900 en el peor caso, y vivia en una
  columna de 300 px. Ninguna anchura arregla eso. El panel de detalle si podia,
  y tampoco: era un `Text` de `height=6` SIN barra de scroll, de modo que del
  criterio mas largo se veian 6 de sus 83 lineas y las otras 77 no eran
  alcanzables. Ahora la fuente encabeza el detalle, el detalle tiene scroll, y
  el reparto entre tabla y detalle es un `PanedWindow` que mueve el usuario.
- **No habia con que buscar.** 69 filas y ningun filtro: encontrar los
  pendientes era recorrerlas a ojo. Hay filtro por estado --- por el MISMO tag
  que devuelve `_estado_criterio`, no por un nombre paralelo --- y busqueda por
  clave o concepto, y arriba el recuento, que se calcula en el mismo recorrido
  que pinta las filas.
- **El programa pedia declarar lo que ya sabia que esta corrida no iba a
  invocar.** De los 33 pendientes, 22 son de Fase 8 y Fase 9 --- cabezal,
  licuefaccion, capacidad portante, aletas ---, que `--alcance perfil` ni
  ejecuta. El filtro de AMBITO los aparta, y sus dos ejes son DERIVADOS:
  «este alcance» es el que la pestana 1 ya declaro (`Criterio.nivel`, via
  `ca.criterios_del_alcance`), y «esta corrida» es el bloque «Criterios
  pendientes que bloquearon una etapa» del informe
  (`M11.criterios_bloqueantes`). Ninguno se elige a mano aqui, y ninguno
  calcula su propia respuesta. A perfil, la tabla pasa de 69 filas a 36 y los
  pendientes visibles de 33 a 11.
  FILTRAR NO ES OCULTAR: el recuento sigue contando los pendientes sobre los
  69 del archivo y dice ademas cuantas filas esconde el filtro. Un criterio
  que no se ve es un criterio que el proyectista no sabe que existe.
- **Un boton apagado no decia por que.** Ver `gui/componentes.BotonAccion`.

Que tiene que traer cada archivo: la ayuda DERIVADA (pestana 1)
---------------------------------------------------------------
El icono «i» de cada campo de archivo abre `gui/ayuda_entrada.py`: las 19
columnas del CSV con su concepto, su unidad, si pueden ir vacias y de donde
sale el dato; y las 8 claves que el JSON admite.

NINGUNA LINEA DE ESA AYUDA ESTA ESCRITA. Sale de `src/ayuda_entrada.py`, que
la deriva de `M0_carga.COLUMNAS` (que sale de los campos de `PuntoCritico`),
de `variables_entrada.VARIABLES`, de `M0_carga.VACIOS_ADMITIDOS` y de
`cli.CLAVES_EXTERNAS`. Una tabla de columnas escrita a mano no falla el dia
que se escribe: falla seis meses despues, cuando alguien anade una columna y
el proyectista llena su archivo siguiendo una ayuda que el propio programa ya
no cumple. `tests/test_ayuda_entrada.py` lo comprueba ANADIENDO una columna al
censo y viendo que la ayuda la recoge sola.

La ayuda del JSON esta a medias Y LO DICE: seis de las ocho claves no son
columna, ni dato de sitio, ni criterio --- no estan en ninguna de las tres
poblaciones del censo --- y su descripcion vive en prosa, en el docstring de
`cli.py`. Esa prosa no se parsea: un docstring no es una interfaz y se
reformatea sin que nada avise. De las seis se da lo que si es dato (el nombre
exacto y las familias que las usan) y se declara el hueco.

Los campos que este expediente no va a usar (pestana 1)
-------------------------------------------------------
La ventana pedia los cinco datos declarados a la vez, sin decir que dos de
ellos solo sirven para una familia --- eso estaba escrito, pero como PROSA en
un tooltip, que es la forma en que el programa no lo puede leer ---. Al cargar
el CSV, `cli.familias_del_csv` dice que familias trae el expediente y
`cli.familias_que_usan` que familias necesitan cada dato; los que no aplican
quedan ANOTADOS al lado.

Anotados, no deshabilitados, y no es un matiz de widget: el proyectista puede
estar preparando el dato de un punto que todavia no metio en el CSV, y un
campo apagado se lo impide mientras le dice que se equivoco. «No aplica»
tampoco quiere decir «es inerte»: en la Familia B, declarar `categoria_tr`
cambia el fundamento que la memoria imprime aunque el TR no se mueva, y por
eso esa familia SI figura entre las que lo usan --- lo dijo la medida, no la
lectura del codigo (`tests/test_familias_del_csv.py`).

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

import ast
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
# Solo para PREGUNTARLE si weasyprint cargo (`_ayuda_del_pdf`). No se le pide
# ningun calculo: la exportacion sigue pasando por `cli.exportar_pdf`, que es
# la misma puerta que usa la linea de comandos.
from modulos import M11_reporte as M11  # noqa: E402

# `ayuda_ent` y no `ayuda`: `ayuda` es el nombre de la variable de bucle de
# CAMPOS_EXTERNOS, en `_construir_tab_datos`, que es la MISMA funcion donde
# se crean los dos iconos. Con el alias corto, Python trata `ayuda` como
# local de esa funcion y la lambda del icono acabaria pidiendole
# `.PESTANA_CSV` a la ultima cadena de tooltip del bucle --- un
# AttributeError al pulsar, no al arrancar. Lo encontro `pyflakes`.
from gui import ayuda_entrada as ayuda_ent  # noqa: E402
from gui import ventana_normativa as ventana_norma  # noqa: E402
from gui.componentes import (COLOR_AVISO, COLOR_ERROR,  # noqa: E402
                             COLOR_OK, BotonAccion, BotonAyuda, MarcoScroll,
                             Tooltip)

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

# Los motivos por los que un boton esta apagado. Son DATO y no cadenas sueltas
# en el sitio donde se apaga cada uno: un motivo escrito junto a su condicion
# se copia mal la segunda vez que hace falta, y el usuario acaba leyendo dos
# explicaciones distintas del mismo bloqueo. `BotonAccion` los exige --- el
# motivo no es opcional --- por la misma razon por la que un criterio [A] sin
# valor lanza excepcion en vez de tomar un defecto: un bloqueo se declara.
MOTIVO_SIN_CRITERIO = "no hay ningun criterio seleccionado en la tabla"
MOTIVO_NO_DECLARADO = "el criterio no esta declarado para esta corrida"
MOTIVO_SIN_CORRIDA = "todavia no se ejecuto el pipeline: no hay informe que exportar"
MOTIVO_EJECUTANDO = "la corrida esta en marcha"

# Los filtros de estado de la tabla de criterios (pestana 2). Cada entrada es
# (rotulo, tag), y el `tag` es el MISMO que devuelve `_estado_criterio`: filtrar
# por un nombre propio seria una segunda regla de estado, y dos reglas de estado
# son dos tablas que pueden decir cosas distintas de la misma fila.
FILTROS_DE_ESTADO = (
    ("Todos", None),
    ("Solo PENDIENTES", "pendiente"),
    ("Declarados en esta corrida", "declarado_corrida"),
    ("PISADOS en esta corrida", "pisado_corrida"),
    ("Resueltos en el archivo", "resuelto"),
)

# Los filtros de AMBITO de la tabla de criterios (pestana 2). Responden a una
# pregunta distinta de la del estado --- aquel dice como esta un criterio,
# este dice si ESTA CORRIDA lo puede necesitar --- y por eso son dos combos y
# no uno solo con las siete opciones mezcladas.
#
# NINGUNO DE LOS TRES SE ELIGE A MANO EN ESTA PESTANA, y ese es todo el
# diseño: el segundo lee el alcance que la pestana 1 ya declaro, y el tercero
# lee el informe de la ultima corrida. Un desplegable donde el proyectista
# eligiera "perfil" aqui mientras la pestana 1 dice "expediente" seria una
# segunda declaracion de alcance, y dos declaraciones de alcance son dos
# corridas distintas descritas como una.
#
# LOS DOS PRIMEROS ESTIMAN Y EL TERCERO MIDE, y la diferencia importa al
# leerlos: "este alcance puede invocarlo" sale de `Criterio.nivel`, que dos
# corridas comprueban en `tests/test_nivel_medido.py` pero que sigue siendo
# una clasificacion previa; "bloqueo esta corrida" sale de
# `M11.criterios_bloqueantes`, que es el registro de lo que de verdad paso.
AMBITO_TODOS = "todos"
AMBITO_ALCANCE = "alcance"
AMBITO_BLOQUEANTES = "bloqueantes"

FILTROS_DE_AMBITO = (
    ("Todos", AMBITO_TODOS),
    ("Solo los que este alcance puede invocar", AMBITO_ALCANCE),
    ("Solo los que bloquearon esta corrida", AMBITO_BLOQUEANTES),
)

MOTIVO_SIN_CORRIDA_FILTRO = (
    "todavia no se ejecuto el pipeline: no hay corrida cuyos bloqueos filtrar")

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
        # Las familias que el CSV cargado trae. `None` --- y no una tupla
        # vacia --- mientras no se haya podido leer: "no se sabe" y "no hay
        # ninguna" son dos cosas distintas, y anotar "no aplica" sobre la
        # segunda cuando en realidad es la primera seria decirle al
        # proyectista que un campo le sobra sin haber leido su archivo.
        self.familias_csv: Optional[tuple] = None

        self._crear_interfaz()

        # El filtro de alcance de la pestana 2 no es una copia del selector de
        # la pestana 1: es el MISMO dato. Sin este `trace` la tabla se quedaba
        # filtrando por el alcance anterior hasta el proximo repintado, que es
        # justo la clase de desfase que hace desconfiar de un filtro.
        self.alcance_var.trace_add("write", lambda *_a: self._refiltrar())
        # Y la anotacion de la pestana 1 se rehace al cambiar el CSV, que es
        # cuando cambian las familias del expediente.
        self.csv_var.trace_add("write", lambda *_a: self._releer_familias())

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

        self.btn_ejecutar = BotonAccion(
            barra, "EJECUTAR PIPELINE (M0 -> M10)", letra=BotonAccion.GRANDE,
            fondo="#2e86c1", activebackground="#21618c", activeforeground="white",
            command=self.ejecutar_pipeline,
            ayuda="Corre M0 -> M10 con el CSV, los datos externos y el\n"
                  "alcance elegidos arriba.",
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
        f_csv = ttk.Frame(f_proj)
        f_csv.grid(row=1, column=2, sticky="w", padx=5)
        ttk.Button(f_csv, text="Examinar...", command=self._elegir_csv).pack(side="left")
        # EL ICONO VA AL LADO DEL CAMPO QUE EXPLICA, no en un menu de ayuda:
        # la pregunta «que columnas lleva esto» se hace mirando el campo, y una
        # ayuda que hay que ir a buscar es una ayuda que no se lee.
        BotonAyuda(
            f_csv, lambda: self._abrir_ayuda(ayuda_ent.PESTANA_CSV),
            "Que columnas tiene que traer el CSV, con su concepto, su unidad,\n"
            "si puede ir vacia y de donde sale el dato. La lista NO esta escrita:\n"
            "se deriva de M0_carga.COLUMNAS y de variables_entrada.py, de modo\n"
            "que no puede quedarse vieja. Incluye la cabecera exacta, copiable."
        ).pack(side="left", padx=(6, 0))

        ttk.Label(f_proj, text="JSON de datos externos (opcional):").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        ent_ext = ttk.Entry(f_proj, textvariable=self.datos_externos_var)
        ent_ext.grid(row=2, column=1, sticky="we", padx=5, pady=4)
        f_ext_botones = ttk.Frame(f_proj)
        f_ext_botones.grid(row=2, column=2, sticky="w", padx=5)
        ttk.Button(f_ext_botones, text="Examinar...",
                   command=self._elegir_datos_externos).pack(side="left")
        BotonAyuda(
            f_ext_botones, lambda: self._abrir_ayuda(ayuda_ent.PESTANA_JSON),
            "Las claves que el JSON admite y la forma del archivo.\n"
            "AYUDA A MEDIAS Y LO DICE: seis de las ocho claves no estan en el\n"
            "censo de variables_entrada.py --- no son columna, ni dato de sitio,\n"
            "ni criterio --- y de ellas solo se puede derivar el nombre y las\n"
            "familias que las usan. Su descripcion sigue en el docstring de\n"
            "cli.py, y esta ventana no lo copia a proposito."
        ).pack(side="left", padx=(6, 0))
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
        # La anotacion «no aplica» de cada campo. Es una etiqueta al lado y NO
        # un `state="disabled"`, y la diferencia es del oficio y no del
        # widget: el proyectista puede estar preparando el dato de un punto
        # que todavia no ha metido en el CSV, y un campo apagado le impide
        # hacerlo mientras le dice que se equivoco. Anotar informa; deshabilitar
        # decide por el.
        self.lbl_no_aplica = {}
        for fila, (clave, etiqueta, ayuda, unidad) in enumerate(CAMPOS_EXTERNOS):
            ttk.Label(f_ext, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=5, pady=6)
            ent = ttk.Entry(f_ext, textvariable=self.externos_vars[clave], width=20, justify="right")
            ent.grid(row=fila, column=1, sticky="w", padx=5, pady=6)
            ttk.Label(f_ext, text=unidad, style="Ayuda.TLabel").grid(row=fila, column=2, sticky="w")
            Tooltip(ent, ayuda)
            self.lbl_no_aplica[clave] = ttk.Label(f_ext, text="",
                                                   style="Ayuda.TLabel")
            self.lbl_no_aplica[clave].grid(row=fila, column=3, sticky="w",
                                            padx=(12, 0))

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

    # LA CLAVE DE `cli` QUE LLEVA CADA CAMPO DE LA VENTANA. Los rotulos de
    # `CAMPOS_EXTERNOS` son los de la GUI (`l_hidraulico`) y las claves con las
    # que `cli` razona son las del expediente (`L_hidraulico_m`): la traduccion
    # ya existia dentro de `_leer_banderas`, enterrada en el armado del dict, y
    # aqui hace falta la MISMA para preguntar por las familias. Se escribe una
    # vez y las dos la leen.
    CLAVE_EXTERNA_DE_CAMPO = {
        "luz_m": "luz_m",
        "TW_m": "TW_m",
        "longitud_m": "longitud_m",
        "l_hidraulico": "L_hidraulico_m",
        "categoria_tr": "categoria_tr",
    }

    def _releer_familias(self):
        """
        Relee del CSV que familias trae el expediente, y reanota la pestana 1.

        NO INTERRUMPE NI AVISA SI EL CSV NO SE PUEDE LEER, y es deliberado: se
        dispara al teclear la ruta, de modo que la mitad de las veces el
        archivo aun no existe. Un error de carga aqui es ruido; el que importa
        lo da EJECUTAR, con el mensaje entero. Lo unico que cambia es que la
        anotacion se calla: `None` es "no se sabe", no "no hay ninguna".
        """
        if not hasattr(self, "lbl_no_aplica"):
            return
        ruta = self.csv_var.get().strip()
        if not ruta:
            self.familias_csv = None
        else:
            try:
                self.familias_csv = cli.familias_del_csv(Path(ruta))
            except (OSError, UnicodeDecodeError, ErrorProyecto):
                self.familias_csv = None
        self._pintar_no_aplica()

    def _pintar_no_aplica(self):
        """
        La anotacion de cada campo declarado, con la familia que falta.

        El conjunto de familias que usa cada dato sale de
        `cli.familias_que_usan`, que es el MISMO que consulta `cli._fase_10`
        para decidir si esa fase corre. Una regla propia de la ventana seria
        una segunda respuesta a "¿este dato sirve para algo en este
        expediente?", y podria contradecir a la del pipeline.
        """
        for campo, lbl in self.lbl_no_aplica.items():
            if self.familias_csv is None:
                lbl.config(text="")
                continue
            usan = cli.familias_que_usan(self.CLAVE_EXTERNA_DE_CAMPO[campo])
            if any(familia in usan for familia in self.familias_csv):
                lbl.config(text="")
                continue
            faltan = ", ".join(f"Familia {f.value}" for f in usan)
            lbl.config(text=f"no aplica: este CSV no trae puntos de {faltan}",
                       foreground=COLOR_AVISO)

    def _abrir_ayuda(self, pestana):
        """
        Abre la ayuda de entrada en la pestana pedida.

        UNA SOLA VENTANA VIVA, y se reutiliza. Sin esto, cada clic en un icono
        abriria una copia mas: el usuario acabaria con cuatro ayudas apiladas y
        cerraria la de arriba creyendo que las cerro todas. Si ya esta abierta
        se le cambia la pestana y se le da el foco, que es lo que se espera al
        pulsar el icono del otro campo.
        """
        viva = getattr(self, "_ventana_ayuda", None)
        if viva is not None and viva.winfo_exists():
            viva.nb.select(viva.tab_json if pestana == ayuda_ent.PESTANA_JSON
                           else viva.tab_csv)
            viva.lift()
            viva.focus_set()
            return viva
        self._ventana_ayuda = ayuda_ent.abrir(self.root, pestana)
        return self._ventana_ayuda

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
        # La fila 2 es el `PanedWindow` (tabla + detalle): es la unica que
        # crece. La 0 es el encabezado, la 1 el filtro, la 3 el bloque de
        # declaracion y la 4 la linea de estado.
        p.rowconfigure(2, weight=1)

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
                 "cualquier calculo que los invoque hasta que se declare un valor. "
                 "Las filas en ambar son declaradas SOLO para esta corrida, y son de "
                 "dos clases que no se confunden: «declarado (corrida)» rellena un "
                 "vacio, y «pisado (corrida)» sustituye un valor que el archivo SI "
                 "tiene y que sigue diciendo otra cosa. La memoria imprime los "
                 "pisados en su propio bloque, con el valor del archivo al lado: "
                 "sirven para TANTEAR, no para entregar.",
            style="Ayuda.TLabel", wraplength=980, justify="left",
        ).pack(anchor="w", pady=(2, 8))

        # --- El filtro y el recuento -------------------------------------
        # Con 69 criterios --- 33 de ellos pendientes --- encontrar los que
        # hay que declarar era scroll a ojo. Y el RECUENTO va aqui, arriba de
        # la tabla, porque «cuantos me faltan» es la pregunta con que se abre
        # esta pestana y contar filas a mano es la peor forma de contestarla.
        # Los dos numeros se calculan en `_llenar_tabla_criterios`, sobre las
        # mismas filas que se pintan: un contador que se calculara aparte
        # podria decir un numero y la tabla mostrar otro.
        f_filtro = ttk.Frame(p, padding=(10, 0, 10, 6))
        f_filtro.grid(row=1, column=0, sticky="ew")
        f_filtro.columnconfigure(4, weight=1)

        ttk.Label(f_filtro, text="Estado:").grid(row=0, column=0, sticky="w")
        self.filtro_estado_var = tk.StringVar(value=FILTROS_DE_ESTADO[0][0])
        cmb_estado = ttk.Combobox(
            f_filtro, textvariable=self.filtro_estado_var, state="readonly",
            width=26, values=[rotulo for rotulo, _tag in FILTROS_DE_ESTADO])
        cmb_estado.grid(row=0, column=1, sticky="w", padx=(6, 16))
        Tooltip(cmb_estado,
                "PENDIENTE  = valor=None: bloquea el calculo que lo invoque.\n"
                "Declarado en esta corrida = valor puesto desde la ventana o\n"
                "  desde aqui; criterios_adoptados.py NO se modifico.\n"
                "Resuelto en el archivo = el valor viene de "
                "criterios_adoptados.py.")

        ttk.Label(f_filtro, text="Ambito:").grid(row=1, column=0, sticky="w",
                                                 pady=(6, 0))
        self.filtro_ambito_var = tk.StringVar(value=FILTROS_DE_AMBITO[0][0])
        cmb_ambito = ttk.Combobox(
            f_filtro, textvariable=self.filtro_ambito_var, state="readonly",
            width=38, values=[rotulo for rotulo, _t in FILTROS_DE_AMBITO])
        cmb_ambito.grid(row=1, column=1, columnspan=2, sticky="w",
                        padx=(6, 16), pady=(6, 0))
        Tooltip(cmb_ambito,
                "Ninguna de las dos opciones se elige a mano aqui:\n"
                "  - «este alcance» es el que declaraste en la pestana 1;\n"
                "  - «esta corrida» sale del informe de la ultima ejecucion.\n"
                "Las dos primeras ESTIMAN --- leen la clasificacion previa de\n"
                "cada criterio ---; la tercera MIDE: es el bloque «Criterios\n"
                "pendientes que bloquearon una etapa» del informe.\n"
                "Filtrar no es ocultar: el recuento sigue diciendo cuantos hay\n"
                "en total y cuantos esconde el filtro.")

        self.lbl_ambito = ttk.Label(f_filtro, text="", style="Ayuda.TLabel")
        self.lbl_ambito.grid(row=1, column=3, columnspan=2, sticky="w",
                             pady=(6, 0))

        ttk.Label(f_filtro, text="Buscar:").grid(row=0, column=2, sticky="w")
        self.filtro_texto_var = tk.StringVar()
        ent_buscar = ttk.Entry(f_filtro, textvariable=self.filtro_texto_var, width=28)
        ent_buscar.grid(row=0, column=3, sticky="w", padx=(6, 16))
        Tooltip(ent_buscar,
                "Busca en la CLAVE y en el CONCEPTO, sin distinguir mayusculas.\n"
                "Se aplica junto con el filtro de estado, no en su lugar.")

        self.lbl_recuento_criterios = ttk.Label(f_filtro, text="",
                                                 style="Header.TLabel")
        self.lbl_recuento_criterios.grid(row=0, column=4, sticky="e")

        # --- La tabla y el detalle, con el reparto en manos del usuario ----
        # `PanedWindow` y no dos filas fijas: el panel de detalle tenia
        # `height=6` y el criterio de fuente mas larga de este archivo ocupa
        # 83 lineas, de modo que 77 no se podian alcanzar de ninguna manera.
        # Con el divisor movible y su barra de scroll, el reparto lo decide
        # quien esta mirando, que es lo unico que sabe si en ese momento le
        # importa mas la lista o el texto de una fila.
        panel = ttk.PanedWindow(p, orient="vertical")
        panel.grid(row=2, column=0, sticky="nsew", padx=10)

        f_tabla = ttk.Frame(panel)
        panel.add(f_tabla, weight=2)
        f_tabla.columnconfigure(0, weight=1)
        f_tabla.rowconfigure(0, weight=1)

        cols = ("clave", "etiqueta", "concepto", "valor", "estado", "fuente")
        self.tree_criterios_todos = ttk.Treeview(
            f_tabla, columns=cols, show="headings", height=12)
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
        # El pisado se pinta como AVISO y con fondo propio: no es un vacio
        # (rojo) ni un valor del archivo (verde) ni un hueco rellenado
        # (ambar claro). Es el unico estado en que la tabla y el archivo
        # discrepan, y tiene que verse de un vistazo.
        self.tree_criterios_todos.tag_configure("pisado_corrida",
                                                 background="#fdebd0",
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

        # Barra HORIZONTAL, que no habia. Las seis columnas suman mas ancho
        # que la ventana, de modo que «Fuente» --- la ultima, y la que dice de
        # donde sale el valor --- se cortaba a media palabra sin ninguna forma
        # de llegar al resto. El texto COMPLETO vive abajo, en el detalle; esta
        # barra es para leer la tabla, no para sustituirlo.
        scroll_ch = ttk.Scrollbar(f_tabla, orient="horizontal",
                                   command=self.tree_criterios_todos.xview)
        self.tree_criterios_todos.configure(xscroll=scroll_ch.set)
        scroll_ch.grid(row=1, column=0, sticky="ew")

        f_detalle = ttk.LabelFrame(panel, text="Detalle del criterio seleccionado",
                                    padding=10)
        panel.add(f_detalle, weight=1)
        f_detalle.columnconfigure(0, weight=1)
        f_detalle.rowconfigure(0, weight=1)

        # `height=12` y no 6: un `PanedWindow` reparte por peso solo el espacio
        # SOBRANTE, de modo que el tamano de arranque de cada panel es el que
        # su contenido pide. Con 6 el detalle nacia en 95 px --- lo mismo que
        # tenia antes de todo esto --- y el divisor no arreglaba nada hasta
        # que alguien lo arrastrara. Doce lineas visibles de arranque, el resto
        # por la barra, y el reparto en manos del usuario a partir de ahi.
        self.txt_detalle_criterio = tk.Text(f_detalle, height=12, wrap="word",
                                             font=("Consolas", 9))
        self.txt_detalle_criterio.grid(row=0, column=0, sticky="nsew")
        scroll_det = ttk.Scrollbar(f_detalle, orient="vertical",
                                    command=self.txt_detalle_criterio.yview)
        self.txt_detalle_criterio.configure(yscrollcommand=scroll_det.set)
        scroll_det.grid(row=0, column=1, sticky="ns")
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

        # DOS FILAS DE BOTONES, y la segunda no es estetica: las cuatro en
        # una sola sumaban mas ancho que la ventana en su tamano por defecto
        # (1100 px) y la que se salia por el borde derecho era justamente
        # «Guardar en archivo fuente», la unica que modifica el archivo del
        # proyecto. Ahora las tres reversibles van juntas y la permanente va
        # sola, separada por una linea: la accion que no se deshace no
        # comparte fila con las que si.
        f_botones = ttk.Frame(f_declarar)
        f_botones.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

        self.btn_aplicar_corrida = BotonAccion(
            f_botones, "Aplicar solo a esta corrida", fondo="#2e86c1", command=self._aplicar_valor_corrida,
            motivo=MOTIVO_SIN_CRITERIO,
            ayuda="El valor se usa en el proximo EJECUTAR PIPELINE, pero\n"
                  "criterios_adoptados.py NO se modifica.")
        self.btn_aplicar_corrida.pack(side="left", padx=(0, 8), ipadx=6, ipady=3)

        self.btn_quitar_declarado = BotonAccion(
            f_botones, "Quitar declaracion de la corrida",
            letra=BotonAccion.DISCRETA, command=self._quitar_valor_corrida, motivo=MOTIVO_SIN_CRITERIO,
            ayuda="Retira el valor declarado para esta corrida Y su\n"
                  "procedencia. Lo que queda debajo depende de lo que habia:\n"
                  "si el criterio estaba vacio vuelve a bloquear el calculo;\n"
                  "si estaba PISADO vuelve a gobernar el valor del archivo.")
        self.btn_quitar_declarado.pack(side="left", padx=8, ipadx=6, ipady=3)

        self.btn_ventana_norma = BotonAccion(
            f_botones, "Ver la norma y declarar desde la tabla...",
            fondo="#5d6d7e",
            command=self._abrir_ventana_normativa, motivo=MOTIVO_SIN_CRITERIO,
            ayuda="Abre la ventana emergente de la variable: la tabla COMPLETA\n"
                  "con su numeral, su pagina impresa, sus notas al pie y sus\n"
                  "modificadores; o el rango con su semantica; o el catalogo con\n"
                  "la advertencia de que ninguna norma lo sostiene.\n"
                  "Al declarar desde alli queda registrada la procedencia: fila,\n"
                  "valor, alternativas descartadas, cita y fecha.")
        self.btn_ventana_norma.pack(side="left", padx=8, ipadx=6, ipady=3)

        ttk.Separator(f_declarar, orient="horizontal").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=8)

        f_permanente = ttk.Frame(f_declarar)
        f_permanente.grid(row=4, column=0, columnspan=2, sticky="w")

        self.btn_guardar_archivo = BotonAccion(
            f_permanente, "Guardar en archivo fuente (permanente)",
            fondo="#c0392b",
            command=self._guardar_valor_en_archivo, motivo=MOTIVO_SIN_CRITERIO,
            ayuda=
                  # SIS-A-14: decia 'Reescribe \'valor=None\'', y reescribe
                  # CUALQUIER valor -- tambien el de un criterio ya declarado --.
                  # El texto que lee el usuario tiene que decir lo mismo que el
                  # docstring de `escribir_valor_en_archivo`, o la correccion
                  # solo llega a quien lee el codigo.
                  "Reescribe el 'valor=' del criterio -- este declarado o no --\n"
                  "DIRECTAMENTE en criterios_adoptados.py. Pide confirmacion.\n"
                  "Etiqueta, justificacion y fuente no se tocan: revisalas a\n"
                  "mano si la razon del valor cambio.\n"
                  "No alcanza a los valores que son tabla, dict o tupla: esos\n"
                  "se rechazan y se editan a mano.")
        self.btn_guardar_archivo.pack(side="left", ipadx=6, ipady=3)

        self.lbl_estado_criterio = ttk.Label(p, text="", style="Ayuda.TLabel",
                                              wraplength=980, justify="left")
        self.lbl_estado_criterio.grid(row=4, column=0, sticky="w", padx=10, pady=(0, 10))

        self._clave_criterio_seleccionado = None
        self._seleccion_fuera_del_filtro = False
        self._claves_ambito = None
        # Refiltrar al escribir, no al pulsar: es la misma regla que la
        # Sec. 4.3 le pide al campo validable, y la que hace util un buscador.
        # La traza se engancha AQUI, al final: `_llenar_tabla_criterios` usa la
        # tabla, la etiqueta de recuento y la clave seleccionada, y engancharla
        # antes de que existan las tres deja la ventana a merced del orden en
        # que se escriban las variables.
        for var in (self.filtro_estado_var, self.filtro_texto_var,
                    self.filtro_ambito_var):
            var.trace_add("write", lambda *_a: self._llenar_tabla_criterios())
        self._llenar_tabla_criterios()

    def _estado_criterio(self, clave):
        """
        (texto, tag) del estado de un criterio para la tabla y el detalle.

        CUATRO ESTADOS Y NO TRES desde que se puede PISAR un valor de archivo.
        «declarado (corrida)» y «pisado (corrida)» son los dos declarados en
        caliente y NO comparten rotulo a proposito: el primero rellena un vacio
        y deja el expediente donde estaba; el segundo sustituye una decision ya
        transcrita, que sigue en el archivo diciendo otra cosa. Reutilizar el
        mismo tag para los dos habria hecho invisible en la tabla la unica
        diferencia que importa --- la que separa tantear de falsear ---, que es
        la forma exacta que tuvo SIS-A-01.
        """
        if ca.declarado_en_caliente(clave):
            if ca.criterio(clave).valor is None:
                return "declarado (corrida)", "declarado_corrida"
            return "pisado (corrida)", "pisado_corrida"
        if ca.criterio(clave).valor is None:
            return "PENDIENTE", "pendiente"
        return "resuelto", "resuelto"

    def _refiltrar(self):
        """
        Repinta la tabla de criterios si ya existe.

        La guardia no es defensiva de mas: `alcance_var` se traza en
        `__init__`, y `set()` sobre el defecto o una sesion cargada puede
        dispararla antes de que la pestana 2 este construida.
        """
        if hasattr(self, "tree_criterios_todos"):
            self._llenar_tabla_criterios()

    def _ambito_del_filtro(self):
        """El tag de `FILTROS_DE_AMBITO` que pide el filtro."""
        rotulo = self.filtro_ambito_var.get()
        for texto, tag in FILTROS_DE_AMBITO:
            if texto == rotulo:
                return tag
        return AMBITO_TODOS

    def _claves_del_ambito(self):
        """
        Las claves que el filtro de ambito deja pasar, o None si no filtra.

        NO CALCULA NINGUNA DE LAS DOS RESPUESTAS, y eso es a proposito: la de
        alcance la da `ca.criterios_del_alcance`, que lee `Criterio.nivel`; la
        de la corrida la da `M11.criterios_bloqueantes`, que es el mismo
        bloque que la memoria imprime. Una tercera regla escrita aqui seria
        una tercera respuesta a la misma pregunta, y la pestana acabaria
        diciendo algo distinto de lo que dice el informe.

        `None` cuando el filtro de bloqueantes se pide sin corrida: sin
        informe no hay conjunto medido, y devolver el vacio dejaria la tabla a
        cero, que se lee como "no queda nada por declarar" --- la lectura mas
        peligrosa que esta pestana puede dar. Se avisa en la linea de al lado.
        """
        ambito = self._ambito_del_filtro()
        if ambito == AMBITO_ALCANCE:
            return set(ca.criterios_del_alcance(self.alcance_var.get()))
        if ambito == AMBITO_BLOQUEANTES:
            if self.informe is None:
                return None
            return {c.clave for c in M11.criterios_bloqueantes(self.informe)}
        return None

    def _pintar_aviso_de_ambito(self, escondidos):
        """La linea que dice DE DONDE sale el conjunto que el filtro aplica."""
        ambito = self._ambito_del_filtro()
        if ambito == AMBITO_ALCANCE:
            texto = (f"segun el alcance «{self.alcance_var.get()}» de la "
                     f"pestana 1 ({escondidos} fuera de alcance)")
        elif ambito == AMBITO_BLOQUEANTES:
            texto = (MOTIVO_SIN_CORRIDA_FILTRO if self.informe is None
                     else f"medido sobre la corrida de {self.informe.generado}")
        else:
            texto = ""
        self.lbl_ambito.config(
            text=texto,
            foreground=(COLOR_AVISO if ambito == AMBITO_BLOQUEANTES
                        and self.informe is None else "#666666"))

    def _tag_del_filtro(self):
        """El tag de `_estado_criterio` que pide el filtro, o None si «Todos»."""
        rotulo = self.filtro_estado_var.get()
        for texto, tag in FILTROS_DE_ESTADO:
            if texto == rotulo:
                return tag
        return None

    def _pasa_el_filtro(self, clave, tag):
        """
        Si esta fila se pinta con el filtro puesto.

        EL CRITERIO SELECCIONADO PASA SIEMPRE, y no es una excepcion comoda:
        declarar un valor CAMBIA el estado de su fila --- de «PENDIENTE» a
        «declarado (corrida)» ---, de modo que con «Solo PENDIENTES» puesto la
        fila desapareceria en el mismo instante en que se declara. El usuario
        perderia de vista lo que acaba de hacer justo cuando quiere
        comprobarlo, y `selection_set` quedaria apuntando a una fila que ya no
        existe.
        """
        if clave == self._clave_criterio_seleccionado:
            self._seleccion_fuera_del_filtro = not self._encaja_en_el_filtro(clave, tag)
            return True
        return self._encaja_en_el_filtro(clave, tag)

    def _encaja_en_el_filtro(self, clave, tag):
        """
        Si la fila cumple los TRES filtros, sin la excepcion de la seleccionada.

        Los tres se aplican JUNTOS y no en lugar unos de otros: «solo
        PENDIENTES» dentro del alcance de perfil es la pregunta con la que se
        abre esta pestana, y contestarla con dos pasadas obligaria a recordar
        cual estaba puesto.
        """
        if (self._claves_ambito is not None
                and clave not in self._claves_ambito):
            return False
        pedido = self._tag_del_filtro()
        if pedido is not None and tag != pedido:
            return False
        texto = self.filtro_texto_var.get().strip().lower()
        if not texto:
            return True
        return texto in clave.lower() or texto in ca.criterio(clave).concepto.lower()

    def _llenar_tabla_criterios(self):
        for item in self.tree_criterios_todos.get_children():
            self.tree_criterios_todos.delete(item)
        pendientes = mostrados = 0
        self._seleccion_fuera_del_filtro = False
        # UNA sola vez por repintado y no una por fila: `criterios_del_alcance`
        # recorre y ordena los 69, y `criterios_bloqueantes` recorre el informe
        # entero. Se guarda en el objeto porque `_encaja_en_el_filtro` lo lee
        # fila a fila.
        self._claves_ambito = self._claves_del_ambito()
        # El valor efectivo NO se recalcula aqui: lo da `criterio_efectivo`,
        # la misma funcion que leen M11 y el JSON. Tres copias de la regla
        # "override si lo hay, archivo si no" son tres sitios donde puede
        # divergir, y esa divergencia fue el hallazgo bloqueante SIS-A-01.
        for clave in sorted(ca.CRITERIOS):
            c = ca.criterio(clave)
            valor_efectivo = ca.criterio_efectivo(clave).valor
            estado_txt, tag = self._estado_criterio(clave)
            if tag == "pendiente":
                pendientes += 1
            if not self._pasa_el_filtro(clave, tag):
                continue
            mostrados += 1
            self.tree_criterios_todos.insert("", "end", iid=clave, values=(
                clave, c.etiqueta, c.concepto,
                "(sin declarar)" if valor_efectivo is None else repr(valor_efectivo),
                estado_txt, c.fuente,
            ), tags=(tag,))
        self._reponer_seleccion()
        self._pintar_recuento(pendientes, mostrados)
        self._pintar_aviso_de_ambito(len(ca.CRITERIOS) - len(self._claves_ambito)
                                     if self._claves_ambito is not None else 0)

    def _reponer_seleccion(self):
        """
        Vuelve a seleccionar la fila que estaba seleccionada antes del repintado.

        ES LA RAIZ DE TRES DEFECTOS Y NO UNA COMODIDAD. `<<TreeviewSelect>>` no
        es sincrono: Tk lo ENCOLA. El `delete` de todas las filas deja la tabla
        sin seleccion, y si nadie la repone, en el siguiente giro del bucle de
        eventos `_al_seleccionar_criterio` entra con seleccion vacia y pone
        `_clave_criterio_seleccionado = None`. A partir de ahi, medido:

        - teclear en «Buscar» DESELECCIONABA el criterio --- detalle en blanco,
          botones apagados, y el mensaje de confirmacion borrado ---;
        - la promesa de `_pasa_el_filtro` («la seleccionada pasa siempre»)
          valia para UN refiltrado: al segundo, `_clave` ya era None y la fila
          desaparecia;
        - y `_tras_declarar_en_ventana` --- que declara desde la emergente, que
          NO es modal y deja tocar el filtro por debajo --- hacia
          `selection_set` sobre una fila inexistente y reventaba con
          `_tkinter.TclError`, que no desciende de `ErrorProyecto`: sale como
          traza de Tk y la GUI no la distingue de un fallo del programa, con el
          valor ya declarado y la fila fuera de la tabla.

        Reponerla aqui, en el UNICO sitio que borra e inserta filas, cierra los
        tres: la clave sobrevive al repintado, de modo que `_pasa_el_filtro`
        sigue protegiendo su fila y ningun `selection_set` posterior apunta al
        vacio. La condicion `in get_children()` no es defensiva de mas: la
        seleccion puede ser None al construir la ventana.
        """
        clave = self._clave_criterio_seleccionado
        if clave and clave in self.tree_criterios_todos.get_children():
            self.tree_criterios_todos.selection_set(clave)

    def _pintar_recuento(self, pendientes, mostrados):
        """
        «33 de 69 pendientes», y cuantas filas enseña y esconde el filtro.

        Los numeros salen del MISMO recorrido que pinta la tabla, no de un
        conteo aparte: un recuento calculado por su cuenta puede decir un
        numero mientras la tabla muestra otro, y entonces el que sobra es el
        recuento.

        LOS PENDIENTES SE CUENTAN SOBRE LOS 69, NO SOBRE LO FILTRADO, y es la
        mitad de lo que hace util este filtro. Un filtro que ademas moviera el
        recuento contestaria "te quedan 11" cuando lo cierto es "te quedan 33,
        de los que 11 los puede invocar esta corrida": la primera frase es la
        que hace que un criterio del expediente se olvide.
        """
        total = len(ca.CRITERIOS)
        texto = f"{pendientes} de {total} pendientes"
        if mostrados != total:
            # DOS NUMEROS Y NO UNO. "el filtro muestra 36" deja al lector
            # restando para saber cuantas filas dejo de ver, y esa resta es
            # justo la que hace falta para confiar en un filtro: lo que
            # esconde tiene que ser tan visible como lo que enseña. Los dos
            # salen del mismo recorrido que pinta la tabla.
            texto += (f"  |  el filtro muestra {mostrados} y esconde "
                      f"{total - mostrados}")
        # Y SE DICE CUANDO UNA DE ESAS FILAS NO ENCAJA. La seleccionada se
        # muestra siempre --- si no, se esfumaria justo al declararla ---, y
        # sin decirlo el recuento parecia equivocado: "33 pendientes, el filtro
        # muestra 34" no se entiende hasta que alguien explica cual es la de
        # mas. La frase no dice «la seleccionada» a proposito: la fila forzada
        # se queda a la vista hasta el proximo refiltrado, de modo que despues
        # de pinchar en otra sigue siendo cierto que hay una que no encaja, y
        # deja de ser cierto que sea la seleccionada.
        if self._seleccion_fuera_del_filtro:
            texto += " (incluida 1 que no encaja, para no perderla de vista)"
        self.lbl_recuento_criterios.config(
            text=texto, foreground=COLOR_ERROR if pendientes else COLOR_OK)

    def _al_seleccionar_criterio(self, _evt=None):
        seleccion = self.tree_criterios_todos.selection()
        self.txt_detalle_criterio.configure(state="normal")
        self.txt_detalle_criterio.delete("1.0", "end")
        # La linea de estado se limpia AL CAMBIAR DE FILA, y solo entonces.
        # Sin limpiarla, el "Error: ..." de un criterio se quedaba escrito
        # debajo del siguiente, que es atribuirle a una fila el problema de
        # otra. Limpiandola SIEMPRE se rompia lo contrario: declarar reselecciona
        # la misma fila --- `_aplicar_valor_corrida` hace `selection_set` para
        # que no se pierda de vista ---, ese `selection_set` vuelve a entrar
        # aqui, y el mensaje de confirmacion que se acababa de escribir se
        # borraba antes de que nadie lo leyera. La condicion es el cambio de
        # clave, no el evento.
        nueva = seleccion[0] if seleccion else None
        if nueva != self._clave_criterio_seleccionado:
            self.lbl_estado_criterio.config(text="")
        if not seleccion:
            self._clave_criterio_seleccionado = None
            self.lbl_criterio_seleccionado.config(text="(ninguno seleccionado)")
            for boton in (self.btn_aplicar_corrida, self.btn_quitar_declarado,
                          self.btn_guardar_archivo, self.btn_ventana_norma):
                boton.deshabilitar(MOTIVO_SIN_CRITERIO)
            self.txt_detalle_criterio.configure(state="disabled")
            return

        clave = seleccion[0]
        c = ca.criterio(clave)
        self._clave_criterio_seleccionado = clave
        self.lbl_criterio_seleccionado.config(text=clave)

        # LA FUENTE VA PRIMERA. Es la que dice DE DONDE sale el valor --- lo
        # que la taxonomia de CLAUDE.md convierte en la pregunta central de
        # cada fila --- y en la tabla no cabe: la mediana de este campo son 280
        # caracteres y el mas largo tiene 4900, contra los ~45 que entran en la
        # columna. Ninguna anchura de columna arregla eso; el sitio donde el
        # texto entero cabe es este panel, y por eso encabeza.
        lineas = [
            f"Fuente        : {c.fuente}",
            f"Justificacion : {c.justificacion}",
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
        # DECLARAR EN CALIENTE YA NO DEPENDE DE QUE EL CRITERIO ESTE VACIO.
        # La condicion era `c.valor is None or en_caliente`, y con ella un
        # criterio resuelto no se podia pisar para una corrida... mientras que
        # el boton rojo de al lado SI lo reescribia permanentemente. La puerta
        # ancha abierta y la estrecha cerrada: quien queria TANTEAR un espesor
        # tenia que modificar el expediente para hacer el ensayo.
        # Lo que sostiene que ahora se pueda no es este boton: es que un pisado
        # se rotula distinto (`_estado_criterio`), se filtra aparte y sale en
        # la memoria en su propio bloque con el valor del archivo al lado.
        self.btn_aplicar_corrida.habilitar()
        self.btn_quitar_declarado.estado(en_caliente, MOTIVO_NO_DECLARADO)
        self.btn_guardar_archivo.habilitar()
        self.btn_ventana_norma.habilitar()

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
        # LA CLAVE SE ADOPTA ANTES DE REPINTAR. Es el unico de los cuatro
        # llamadores que recibe la clave por argumento en vez de leer la
        # seleccionada, y la emergente no es modal (`transient` sin
        # `grab_set`): entre abrirla y declarar, el usuario pudo tocar el
        # filtro por debajo y dejar `_clave_criterio_seleccionado` en otra cosa
        # --- o en None ---. Adoptarla aqui es lo que hace que
        # `_pasa_el_filtro` proteja ESTA fila y que reponer la seleccion
        # encuentre algo.
        self._clave_criterio_seleccionado = clave
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
        la CLI resuelve el texto ENTERO con `ast.literal_eval` -- y asi leeria
        '1,5' como la TUPLA (1, 5) -- mientras aqui se admite la coma decimal,
        que para quien teclea en la ventana es lo natural. Unificar las dos
        por el lado de la CLI convertiria '1,5' en una tupla valida en
        silencio, que es una regresion peor que la duplicacion. La divergencia
        esta fijada por un test de contrato en tests/test_gui_contrato.py.

        POR QUE ADMITE ADEMAS UN LITERAL ESTRUCTURADO (C8, punto 6). Con solo
        las dos ramas de arriba, la GUI NO PODIA DECLARAR
        'secciones_cajon_normalizadas' --- la serie de pares (B, H) del
        catalogo del cajon ---: lo tecleado volvia como CADENA, la guardia de
        `criterios_adoptados` la aceptaba, y el bucle de MD se detenia despues
        con un `DatoInvalidoError` correcto pero sin salida, porque no habia
        forma de teclear una lista. O sea que uno de los siete criterios de la
        Familia C quedaba fuera de la declaracion en caliente sin que nada lo
        dijera: la ventana ofrecia el campo y el campo no servia.

        Y NO REABRE EL AGUJERO DEL '1,5'. La rama estructurada solo se toma
        cuando el texto ABRE con un delimitador de coleccion --- '[', '(' o
        '{' ---, que es algo que ningun decimal escrito con coma puede hacer.
        La ambiguedad de la CLI vive en el caso SIN delimitadores, y ese caso
        sigue yendo por la rama del float. Un literal mal cerrado sale como el
        `ValueError` de esta funcion, o sea como el rotulo rojo del panel, y
        no como traza de Tk.
        """
        texto = texto.strip()
        if texto == "":
            raise ValueError("El valor no puede quedar vacio.")
        if texto[0] in "[({":
            try:
                return ast.literal_eval(texto)
            except (ValueError, SyntaxError) as exc:
                raise ValueError(
                    f"«{texto}» empieza como una lista, tupla o dict y no se "
                    f"puede leer como tal ({exc}). Los pares del catalogo del "
                    "cajon se escriben asi: [[1.20, 0.90], [1.50, 1.20]]"
                ) from None
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
        # Sin `selection_set` detras: lo hace `_llenar_tabla_criterios`, que es
        # quien borra las filas y por tanto quien tiene que reponerla.
        self._llenar_tabla_criterios()

    def _quitar_valor_corrida(self):
        clave = self._clave_criterio_seleccionado
        if not clave:
            return
        # `dec.olvidar` retira el valor Y su procedencia. Retirar solo el
        # valor dejaria una procedencia hablando de un numero que ya no
        # gobierna nada, que es peor que no tener procedencia.
        # QUE PASA AL QUITAR DEPENDE DE QUE HABIA DEBAJO, y hasta aqui el
        # mensaje afirmaba una sola de las dos cosas. `quitar_valor_dinamico`
        # solo saca el override, de modo que `criterio_efectivo` cae al valor
        # del ARCHIVO: si el criterio estaba vacio, vuelve a bloquear; si
        # estaba pisado, vuelve al valor transcrito y no bloquea nada. Decir
        # «vuelve a bloquear el calculo» de un pisado es exactamente el defecto
        # que este cambio tenia que no cometer: un mensaje que describe un
        # estado distinto del que el programa acaba de dejar.
        valor_archivo = ca.criterio(clave).valor
        dec.olvidar(clave)
        if valor_archivo is None:
            texto = (f"Se quito la declaracion de '{clave}': el criterio "
                     "vuelve a estar PENDIENTE y bloquea el calculo que lo "
                     "invoque.")
        else:
            texto = (f"Se quito el valor pisado de '{clave}': vuelve a "
                     f"gobernar el del archivo, {valor_archivo!r}. No bloquea "
                     "nada.")
        self.lbl_estado_criterio.config(text=texto, foreground=COLOR_AVISO)
        self._llenar_tabla_criterios()

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

    # -------------------------- Pestana 3 -----------------------------
    def _construir_tab_puntos(self, p):
        p.columnconfigure(0, weight=1)
        p.rowconfigure(0, weight=1)

        f_tabla = ttk.Frame(p, padding=10)
        f_tabla.grid(row=0, column=0, sticky="nsew")
        f_tabla.columnconfigure(0, weight=1)
        f_tabla.rowconfigure(0, weight=1)

        cols = ("id", "progresiva", "familia", "dimensionado", "material",
                "seccion", "control", "HW", "V_erosion", "V_sedimentacion",
                "incumplidas", "bloqueos")
        self.tree_puntos = ttk.Treeview(f_tabla, columns=cols, show="headings", height=14)
        encabezados = [
            ("id", "Punto", 70, "w"),  # literal-ok: ancho de columna, px
            ("progresiva", "Progresiva", 90, "center"),  # literal-ok: ancho de columna, px
            ("familia", "Familia", 60, "center"),  # literal-ok: ancho de columna, px
            ("dimensionado", "Dimensionado", 90, "center"),  # literal-ok: ancho de columna, px
            ("material", "Material", 140, "w"),  # literal-ok: ancho de columna, px
            # LA COLUMNA DICE LA SECCION Y NO UN DIAMETRO (C8). Con «D (m)»,
            # un marco de 1.20 x 0.90 y otro de 2.00 x 0.90 salian los dos
            # «0.90» en el tablero, que es la mitad que no gobierna la
            # capacidad. Va mas ancha porque «marco 1.20 x 0.90 m» no cabe en
            # el ancho de un diametro.
            ("seccion", "Seccion", 130, "center"),  # literal-ok: ancho de columna, px
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

        # LOS CUATRO NACEN APAGADOS Y DICIENDO POR QUE. El motivo es siempre
        # el mismo --- no hay informe hasta que se ejecuta el pipeline --- y
        # hasta aqui no estaba escrito en ningun sitio: los botones salian
        # grises y el usuario tenia que deducirlo. Es el bloqueo mas frecuente
        # de esta ventana y era el unico mudo.
        self.btn_json = BotonAccion(
            f_exp, "Exportar JSON", fondo="#16a085",
            command=self.exportar_json, motivo=MOTIVO_SIN_CORRIDA,
            ayuda="El informe completo de la corrida en JSON.")
        self.btn_json.pack(side="left", padx=(0, 8), ipadx=8, ipady=4)

        self.btn_html = BotonAccion(
            f_exp, "Exportar memoria (HTML)", fondo="#2e86c1", command=self.exportar_html, motivo=MOTIVO_SIN_CORRIDA,
            ayuda="La memoria de calculo (M11) con la plantilla que\n"
                  "corresponde al alcance de la corrida.")
        self.btn_html.pack(side="left", padx=8, ipadx=8, ipady=4)

        self.btn_pdf = BotonAccion(
            f_exp, "Exportar memoria (PDF)", fondo="#8e44ad", command=self.exportar_pdf, motivo=MOTIVO_SIN_CORRIDA,
            ayuda=self._ayuda_del_pdf())
        self.btn_pdf.pack(side="left", padx=8, ipadx=8, ipady=4)

        self.btn_csv = BotonAccion(
            f_exp, "Exportar cuadro resumen (CSV)", fondo="#16a085", command=self.exportar_csv, motivo=MOTIVO_SIN_CORRIDA,
            ayuda="El cuadro resumen (entregable 3 de M11), una fila\n"
                  "por punto, en una hoja de calculo.")
        self.btn_csv.pack(side="left", padx=8, ipadx=8, ipady=4)

    def _ayuda_del_pdf(self):
        """
        Por que via saldra el PDF, DICHO ANTES DE PULSAR y no despues.

        `M11_reporte` intenta `from weasyprint import HTML` dentro de un
        `except Exception` --- que atrapa tanto el `ImportError` de «no esta
        instalado» como el `OSError` de «esta instalado y sus librerias
        nativas no cargan», que es el caso de Windows sin GTK ---. Si no
        cargo, la exportacion NO falla: escribe el HTML y lo abre en el
        navegador para imprimirlo con Ctrl+P. Eso funciona, y aun asi conviene
        decirlo de antemano: quien pulsa «Exportar memoria (PDF)» y ve
        aparecer un navegador cree que algo se rompio.

        Se lee `WeasyHTML` --- el MISMO simbolo que decide la via --- y no una
        comprobacion propia: dos formas de preguntar «¿hay weasyprint?» son
        dos respuestas que pueden discrepar, y la que veria el usuario seria
        la equivocada.
        """
        if M11.WeasyHTML is not None:
            return ("Escribe el PDF directamente con weasyprint.\n"
                    "La hoja ya esta configurada en A4.")
        return ("weasyprint no esta operativo en esta maquina: o no esta\n"
                "instalado, o esta instalado y sus librerias nativas (GTK,\n"
                "cairo, pango) no cargan --- lo corriente en Windows ---.\n"
                "NO es un bloqueo: al pulsar se escribe la memoria en HTML\n"
                "junto al destino que elijas y se abre en el navegador para\n"
                "guardarla como PDF con Ctrl+P (la hoja ya esta en A4).")

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
            # La traduccion rotulo-de-ventana -> clave-de-expediente sale de
            # `CLAVE_EXTERNA_DE_CAMPO` y ya no de un `if` escrito aqui: la
            # anotacion de familias necesita la MISMA correspondencia, y dos
            # copias de ella se separan el dia que aparezca un sexto campo.
            clave_bandera = self.CLAVE_EXTERNA_DE_CAMPO[clave]
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

        self.btn_ejecutar.deshabilitar(MOTIVO_EJECUTANDO)
        self.btn_ejecutar.config(text="Ejecutando...")
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
            self.btn_ejecutar.habilitar()
            self.btn_ejecutar.config(text="EJECUTAR PIPELINE (M0 -> M10)")

        self._llenar_tabla_puntos()
        self._llenar_resumen()
        # La pestana 2 se repinta porque acaba de aparecer el tercer filtro:
        # sin corrida, «solo los que bloquearon esta corrida» no tiene conjunto
        # que aplicar; con ella, ya lo tiene. Repintar aqui es lo que hace que
        # el filtro exacto este disponible en el momento en que se vuelve
        # exacto.
        self._llenar_tabla_criterios()
        for btn in (self.btn_json, self.btn_html, self.btn_pdf, self.btn_csv):
            btn.habilitar()
        # La via del PDF se relee AQUI y no solo al construir la ventana: es
        # barato y evita que la ayuda hable de una maquina distinta de la que
        # acaba de correr.
        self.btn_pdf.ayuda = self._ayuda_del_pdf()
        self.btn_pdf.tooltip.texto = self.btn_pdf.ayuda
        self.lbl_estado.config(
            text=f"Ejecutado ({self.informe.generado}). "
                 f"{self.informe.dimensionados}/{len(self.informe.puntos)} puntos dimensionados. "
                 f"Expediente {'cerrado' if self.informe.cerrado else 'NO cerrado'}.")
        self.nb.select(self.tab_puntos)

    def _mostrar_error_entrada(self, mensaje):
        self.lbl_error_datos.config(text=mensaje)
        self.nb.select(self.tab_datos)
        self.btn_ejecutar.habilitar()
        self.btn_ejecutar.config(text="EJECUTAR PIPELINE (M0 -> M10)")

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
                material = r.material.nombre
                seccion = r.seccion.etiqueta()
                control, HW = h.control_gobernante.value, f"{h.HW:.3f}"
                V_ero = f"{h.V_erosion:.2f}"
                V_sed = f"{h.V_sedimentacion:.2f}"
            else:
                material = seccion = control = HW = V_ero = V_sed = "-"

            tags = []
            if not informe_punto.dimensionado:
                tags.append("no_dimensionado")
            if n_bloqueos:
                tags.append("con_bloqueos")

            self.tree_puntos.insert("", "end", iid=punto.id, values=(
                punto.id, punto.progresiva_display, punto.familia.value,
                "si" if informe_punto.dimensionado else "no",
                material, seccion, control, HW, V_ero, V_sed, incumplidas,
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
